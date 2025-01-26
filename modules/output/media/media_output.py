#MEDIA OUTPUT MODULE
import pygame
import threading
from threading import Event
import os
import time
import requests
from bs4 import BeautifulSoup
from modules.helper.shared import visualizer

is_playing = False

pygame.init()
pygame.mixer.init()
stop_event = Event()
current_thread = None  # Global definieren, um aktiven Thread zu verfolgen

def stop_mp3():
    global stop_event, is_playing, current_thread
    print('Willkommen in der STOP-MP3-FUNKTION')

    if not is_playing:
        print("Es wird keine Musik abgespielt.")
        return

    print("Musik wird gestoppt...")

    stop_event.set()
    pygame.mixer.music.fadeout(500)  # Fadeout für 500 ms
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    is_playing = False

    if current_thread and current_thread.is_alive():
        print("Beende aktuellen Musik-Thread.")
        current_thread.join()  # Warten bis der Thread sauber beendet wird
    print("Musik erfolgreich gestoppt.")
    return True

def play_mp3(file_path: str):
    global stop_event, current_thread, is_playing
    print('Lade mp3 für wiedergabe...')

    if is_playing:
        print("Ein anderer Song wird bereits abgespielt.")
        return

    stop_event.clear()
    current_thread = threading.current_thread()
    print(current_thread)
    
    is_playing = True
    pygame.init()
    pygame.mixer.init(buffer=2048)
    print(f"Spiele Datei: {file_path}")
    visualizer.playFile(file_path)
    

    # Überprüfe kontinuierlich das stop_event während der Wiedergabe
    while pygame.mixer.music.get_busy():
        if stop_event.is_set():
            print("Stop-Event erkannt, Abbruch der Wiedergabe.")
            break
        pygame.time.Clock().tick(10)  # Kleine Pause, um CPU zu schonen

    # Stoppen der Musik und Freigabe
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    is_playing = False
    print("Wiedergabe beendet.")

def aktuelleNachrichten():
    global is_playing

    if not is_playing:
        url = 'https://www.deutschlandfunk.de/nachrichten-100.html'
        
        # Holen des HTML-Inhalts der Seite
        try:
            response = requests.get(url)
            response.raise_for_status()  # Überprüft, ob der HTTP-Status OK ist
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der Audiodatei: {e}")
            return False
        html = response.text

        # Parsing des HTML-Inhalts mit BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Suche nach dem Button, der die Audio-URL enthält
        audio_button = soup.find(class_='b-button-play')
        
        if audio_button:
            audio_url = audio_button.get('data-audio')
            # Die Audiodatei lokal speichern
            audio_file_path = "nachrichten_dlf.mp3"
            
            response = requests.get(audio_url)
            
            with open(audio_file_path, 'wb') as file:
                file.write(response.content)

            audio_file_path = 'C:\dev\python\jetson\\nachrichten_dlf.mp3'
            # Starte einen separaten Thread zum Abspielen der Musik
            threading.Thread(target=play_mp3, args=(audio_file_path,)).start()
            return True
        else:
            print("Button nicht gefunden auf der Seite!")
            return True
    else:
        print("Music is already playing.")
        return False
