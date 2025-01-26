import pygame
import numpy as np
import colorsys
import threading
import time
from scipy.signal.windows import hann
from pydub import AudioSegment

AudioSegment.converter = 'ffmpeg'
mp3_filepath = ''

class AudioVisualizer:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.visualizer_thread = None
        self.is_running = False
        self.max_amplitude = 1024
        pygame.mixer.init()

    def start(self):
        if not self.is_running:
            self.visualizer_thread = threading.Thread(target=self.run_visualizer)
            self.visualizer_thread.daemon = True
            self.visualizer_thread.start()
            self.is_running = True

    
    def stop_visualizer(self):
        self.is_running = False
        if self.visualizer_thread is not None and self.visualizer_thread != threading.current_thread():
            self.visualizer_thread.join()

    def playFile(self, mp3_file):
        
        global mp3_filepath
        mp3_filepath = mp3_file
        
        print('Wir gehen in die Wiedergabe ...', mp3_file)
        
        if self.is_running:
            pygame.mixer.music.load(mp3_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Prüfen, ob Musik noch abgespielt wird
                time.sleep(0.1)
            pygame.mixer.music.unload()
            print('Fertig mit Sprachausgabe')
        else:
            print('Visualizer läuft nicht.')
            

    def run_visualizer(self):
        self.screen, self.clock = self.create_visualizer_window()
        
        decay_rate = 0.8
        num_bands = 64
        bar_width = 5
        bar_spacing = 2
        previous_heights = [0] * num_bands
        frame_index = 0

        total_bar_width = (bar_width + bar_spacing) * (num_bands * 2)
        start_x = (self.screen.get_width() - total_bar_width) // 2

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_visualizer()

            self.screen.fill((0, 0, 0))

            if pygame.mixer.music.get_busy():
                
                raw_data = self.get_audio_data()
                raw_data = raw_data.astype(np.float32) / np.max(np.abs(raw_data)) if np.max(np.abs(raw_data)) != 0 else raw_data
                windowed_data = raw_data * hann(len(raw_data))
                fft_out = np.abs(np.fft.rfft(windowed_data)) * 10  # Hier 10 als Beispiel, anpassen nach Bedarf
                freqs = np.fft.rfftfreq(len(raw_data), 0.5 / 44100)

                band_width = len(freqs) // num_bands
                band_order = list(reversed(range(num_bands))) + list(range(num_bands))

                # Berechnen eines dynamischen Maximums für die Balkenhöhe basierend auf den aktuellen Daten
                self.max_amplitude = 0.9 * self.max_amplitude + 0.1 * np.max(fft_out) if np.max(fft_out) > 0 else self.max_amplitude
                dynamic_max = self.max_amplitude if self.max_amplitude > 0 else 1

                for i, band_index in enumerate(band_order):
                    start = band_index * band_width
                    end = (band_index + 1) * band_width if band_index < num_bands - 1 else len(freqs)
                    band_amplitude = np.mean(fft_out[start:end])

                    max_height = self.screen.get_height() * 0.8  # Platz für Reflektion
                    # Logarithmische Skalierung der Balkenhöhe
                    bar_height = int(np.log(1 + band_amplitude) * (max_height / np.log(1 + dynamic_max)))
                    bar_height = max(1, min(bar_height, int(max_height)))  # Sicherstellen, dass bar_height zwischen 1 und max_height liegt

                    # Glättung entfernen oder mit hohem Alpha-Wert
                    # bar_height = int(self.smooth_amplitude(bar_height, previous_heights[band_index], alpha=0.9))  # Sehr hoher Alpha-Wert für schnelle Anpassung
                    # Stattdessen Dekay einfügen
                    bar_height = max(1, int(bar_height - decay_rate * previous_heights[band_index]))  # Dekay der Balkenhöhe
                    previous_heights[band_index] = bar_height

                    #print(f"Band Amplitude for band {band_index}: {band_amplitude}")
                    #print(f"Bar Height for band {band_index}: {bar_height}")

                    x_pos = start_x + i * (bar_width + bar_spacing)
                    color = self.get_rainbow_color(band_index, num_bands)

                    # Zeichne Balken mit reflektierender Animation
                    for y in range(bar_height):
                        bar_height = self.smooth_amplitude(bar_height, previous_heights[i % num_bands], alpha=0.1)
                        previous_heights[i % num_bands] = bar_height

                        x_pos = start_x + i * (bar_width + bar_spacing)
                        color = self.get_rainbow_color(i % num_bands, num_bands)

                        pygame.draw.rect(self.screen, color, (x_pos, self.screen.get_height() // 2 - bar_height // 2, bar_width, bar_height), 0, 3)
                        
                        # intensity = (1 - y / bar_height)  # Gradienten-Intensität
                        # shade_color = tuple(int(c * intensity) for c in color)
                        # pygame.draw.rect(self.screen, shade_color, (x_pos, self.screen.get_height() // 2 - y, bar_width, 1))
                        #pygame.draw.rect(self.screen, shade_color, (x_pos, self.screen.get_height() // 2 + y, bar_width, 1))  # Reflektion
                    
                    
            else:
                self.animate_idle_bars(previous_heights, num_bands, bar_width, bar_spacing, start_x)

            pygame.display.flip()
            self.clock.tick(120)

    def create_visualizer_window(self):
        pygame.init()
        clock = pygame.time.Clock()
        width, height = 600, 400
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Visualizer")
        screen.fill((0, 0, 0))
        return screen, clock

    def get_rainbow_color(self, index, total):
        hue = index / total + 0.5
        saturation = 0.8
        intensity = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, intensity)
        return tuple(int(round(x * 255)) for x in rgb)

    def smooth_amplitude(self, current, previous, alpha=0.1):
        return alpha * current + (1 - alpha) * previous

    def get_audio_data(self):
        global mp3_filepath
        #print('get_audio_from: ', mp3_filepath)
        
        # Lade die MP3-Datei mit pydub
        sound = AudioSegment.from_mp3(mp3_filepath)
        sound = sound.set_channels(1)  # Mono

        # Hole die Abtastrate der Audiodatei
        sample_rate = sound.frame_rate
        raw_data = np.array(sound.get_array_of_samples())

        # Passe die Daten an, um sie zu normalisieren und korrekt zu verwenden
        raw_data = raw_data.astype(np.float32) / (2**15)  # Normalisieren der Rohdaten
        raw_data = raw_data[:4096]  # Nimm nur die ersten 4096 Werte

        #print(f"Abtastrate: {sample_rate}, Anzahl der Samples: {len(raw_data)}")
        return raw_data

    def animate_idle_bars(self, previous_heights, num_bands, bar_width, bar_spacing, start_x):
        for i in range(num_bands * 2):
            bar_height = 5  # Einfache Animation ohne Musik
            bar_height = self.smooth_amplitude(bar_height, previous_heights[i % num_bands], alpha=0.1)
            previous_heights[i % num_bands] = bar_height

            x_pos = start_x + i * (bar_width + bar_spacing)
            color = self.get_rainbow_color(i % num_bands, num_bands)

            pygame.draw.rect(self.screen, color, (x_pos, self.screen.get_height() // 2 - bar_height // 2, bar_width, bar_height), 0, 3)