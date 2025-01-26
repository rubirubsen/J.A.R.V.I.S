import pygame
import sys
import numpy as np
import math
import subprocess
import wave
import colorsys

# Funktion
def create_visualizer_window():
    """Erstellt ein Pygame-Fenster für das visuelle Feedback."""
    pygame.init()

    # Fenstergröße
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("JARVIS Visualizer")

    # Hintergrundfarbe (optional)
    screen.fill((0, 0, 0))

    # Event-Loop (um das Fenster am Laufen zu halten)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hier könnte später das visuelle Feedback eingebaut werden.
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Funktion zum Konvertieren von MP3 nach WAV mit ffmpeg
def convert_mp3_to_wav(mp3_path, wav_path):
    subprocess.call(['C:\\ffmpeg\\bin\\ffmpeg.exe', '-i', mp3_path, '-y', wav_path])

# Funktion zur Erzeugung von Regenbogenfarben
def get_rainbow_color(index, total):
    """
    Rufe eine Farbe des Regenbogens ab, basierend auf dem angegebenen Index und der Gesamtzahl der Farben.
    
    Parameters:
    index (int): Der Index der gewünschten Farbe.
    total (int): Die Gesamtzahl der Farben.
    
    Returns:
    tuple: Ein RGB-Farbtupel, repräsentiert als eine Tupel aus drei Werten zwischen 0 und 255.
    """
    # Berechne den Hue-Wert
    hue = index / total + 0.5
    
    # Verwende die HSV-Formel mit einer konstanten Saturation (1.0) und Variablen für die Intensität
    saturation = 0.8
    intensity = 0.9
    
    # Konvertiere den HSV-Wert in ein RGB-Farbtupel
    rgb = colorsys.hsv_to_rgb(hue, saturation, intensity)
    
    # Runde die RGB-Werte auf zwei Dezimalstellen ab und wandele sie in ganze Zahlen um
    return tuple(int(round(x * 255)) for x in rgb)


# Einfache Glättung der Amplitudenwerte
def smooth_amplitude(current, previous, alpha=0.1):
    return alpha * current + (1 - alpha) * previous

# Funktion zum Starten des Pygame-Fensters und der Animation
def start_audio_visualizer(mp3_file, wav_file):
    pygame.init()

    # Fenstergröße
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Audio Equalizer")

    # Konvertiere MP3 nach WAV
    convert_mp3_to_wav(mp3_file, wav_file)

    # Audio-Datei öffnen
    wave_file = wave.open(wav_file, 'rb')

    # Audioeigenschaften
    sample_width = wave_file.getsampwidth()
    sample_rate = wave_file.getframerate()
    num_frames = wave_file.getnframes()

    # Audio-Daten lesen
    raw_data = wave_file.readframes(num_frames)
    wave_file.close()

    # Konvertieren der Rohdaten in ein Numpy-Array für Analyse
    if sample_width == 2:
        audio_data = np.frombuffer(raw_data, dtype=np.int16)
    elif sample_width == 1:
        audio_data = np.frombuffer(raw_data, dtype=np.uint8)
    else:
        raise ValueError("Unsupported sample width")

    # Pygame Audio initialisieren und MP3 abspielen
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_file)
    pygame.mixer.music.play()

    # Clock für Framerate
    clock = pygame.time.Clock()

    # Anzahl der Frequenzbänder
    num_bands = 64

    # Breite der Balken anpassen
    bar_width = 5
    bar_spacing = 2

    # Hauptloop
    running = True
    frame_index = 0
    previous_heights = [0] * num_bands
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Hintergrund schwarz

        # Berechne die Amplitude für den aktuellen Frame
        if frame_index + sample_rate // 30 < len(audio_data):
            chunk = audio_data[frame_index:frame_index + sample_rate // 30]

            # Frequenzanalyse (vereinfacht)
            fft_out = np.abs(np.fft.rfft(chunk))
            freqs = np.fft.rfftfreq(len(chunk), 1.0/sample_rate)

            # Teile die Frequenzen in Bänder auf
            band_width = len(freqs) // num_bands
            total_bar_width = (bar_width + bar_spacing) * (num_bands * 2)
            start_x = (width - total_bar_width) // 2

            band_order = list(reversed(range(num_bands))) + list(range(num_bands))

            for i, band_index in enumerate(band_order):
                start = band_index * band_width
                end = (band_index + 1) * band_width if band_index < num_bands - 1 else len(freqs)
                band_amplitude = np.max(fft_out[start:end])

                max_amplitude = 2**(sample_width*8-1)
                if band_index < 4:
                    bar_height = int((band_amplitude / max_amplitude) * (height / 2) * 0.25)
                else:
                    bar_height = int((band_amplitude / max_amplitude) * (height / 2))

                if i < num_bands:
                    bar_height = smooth_amplitude(bar_height, previous_heights[band_index])
                    previous_heights[band_index] = bar_height
                else:
                    bar_height = smooth_amplitude(bar_height, previous_heights[num_bands - 1 - band_index])
                    previous_heights[num_bands - 1 - band_index] = bar_height

                x_pos = start_x + i * (bar_width + bar_spacing)

                color = get_rainbow_color(band_index, num_bands)

                pygame.draw.rect(screen, color, (x_pos, height // 2 - bar_height // 2, bar_width, bar_height), 0, 3)

        pygame.display.flip()
        clock.tick(30)  # 30 FPS

        # Verschieben zum nächsten Frame der Audio-Daten
        frame_index = (frame_index + sample_rate // 30) % len(audio_data)

        # Beenden, sobald Musik zu Ende ist
        if not pygame.mixer.music.get_busy():
            running = False

    pygame.quit()
    sys.exit()