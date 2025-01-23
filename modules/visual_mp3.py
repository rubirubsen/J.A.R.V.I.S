import pygame
import sys
import numpy as np
import math
import subprocess
import wave
import colorsys

# Funktion zum Konvertieren von MP3 nach WAV mit ffmpeg
def convert_mp3_to_wav(mp3_path, wav_path):
    subprocess.call(['C:\\ffmpeg\\bin\\ffmpeg.exe', '-i', mp3_path, '-y', wav_path])

# Funktion zur Erzeugung von Regenbogenfarben
def get_rainbow_color(index, total):
    hue = index / total
    return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0))

# Initialisieren von Pygame
pygame.init()

# Fenstergröße
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Audio Equalizer")

# Pfade zu den Audio-Dateien
mp3_file = "C:/dev/python/jetson/modules/DeepJarvis_ivc_s60_sb70_se13_b_m2.mp3"
wav_file = "C:/dev/python/jetson/modules/output.wav"

# Konvertiere MP3 nach WAV
convert_mp3_to_wav(mp3_file, wav_file)
print('CONVERT DONE', wav_file)

# Audio-Datei öffnen
wave_file = wave.open(wav_file, 'rb')

# Audioeigenschaften
sample_width = wave_file.getsampwidth()
channels = wave_file.getnchannels()
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
bar_width = 5  # Schmalere Balken
bar_spacing = 2  # Abstand zwischen den Balken


# Einfache Glättung der Amplitudenwerte
def smooth_amplitude(current, previous, alpha=0.1):
    return alpha * current + (1 - alpha) * previous

# Hauptloop
running = True
frame_index = 0
previous_heights = [0] * num_bands  # Speichern der vorherigen Höhen für Glättung
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
        total_bar_width = (bar_width + bar_spacing) * (num_bands * 2)  # Verdoppelt, da wir jetzt 128 Balken haben
        start_x = (width - total_bar_width) // 2  # Zentrum des Fensters

        # Band Order ist nun von 63 bis 0 und dann von 0 bis 63
        band_order = list(reversed(range(num_bands))) + list(range(num_bands))
        
        for i, band_index in enumerate(band_order):
            start = band_index * band_width
            end = (band_index + 1) * band_width if band_index < num_bands - 1 else len(freqs)
            band_amplitude = np.max(fft_out[start:end])
            
            # Skalierung der Amplitude für die Darstellung mit Dämpfung der tieferen Frequenzen
            max_amplitude = 2**(sample_width*8-1)
            if band_index < 4:  # Die ersten 4 Bänder (Bass) werden gedämpft
                bar_height = int((band_amplitude / max_amplitude) * (height / 2) * 0.25)  # Reduzierte Skalierung für Bass
            else:
                bar_height = int((band_amplitude / max_amplitude) * (height / 2))
            
            # Glättung der Ausschläge
            # Da wir jetzt 128 Balken haben, müssen wir `previous_heights` entsprechend anpassen
            if i < num_bands:
                bar_height = smooth_amplitude(bar_height, previous_heights[band_index])
                previous_heights[band_index] = bar_height
            else:
                bar_height = smooth_amplitude(bar_height, previous_heights[num_bands - 1 - band_index])
                previous_heights[num_bands - 1 - band_index] = bar_height
            
            x_pos = start_x + i * (bar_width + bar_spacing)
            
            # Regenbogenfarbe für jeden Balken
            # Die Farben werden basierend auf der ursprünglichen Position des Bandes vergeben
            color = get_rainbow_color(band_index, num_bands)
            
            # Zeichne die vertikalen Linien für jedes Frequenzband, zentriert und mit abgerundeten Ecken
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