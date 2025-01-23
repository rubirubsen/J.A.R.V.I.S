#MEDIA OUTPUT MODULE
import pygame
import threading
import os
import time
from bs4 import BeautifulSoup

def play_mp3(file_path: str):
    global is_playing

    with music_lock:
        # Setze is_playing auf True, um die Wiedergabe zu starten
        is_playing = True

        # Lade und spiele die MP3-Datei
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Warten, bis die Musik stoppt oder gestoppt werden soll
        while pygame.mixer.music.get_busy() and is_playing:
            pygame.time.Clock().tick(10)

        # Musikwiedergabe beendet
        is_playing = False
        time.sleep(0.5)  # Ein kleiner Sleep, um sicherzustellen, dass die Musik wirklich gestoppt ist
        try:
            pygame.mixer.music.unload()
            os.remove(file_path)  # Datei nach dem Abspielen löschen
            print(f"{file_path} wurde gelöscht.")
        except PermissionError:
            print(f"Fehler: {file_path} kann nicht gelöscht werden. Wird noch von einem Prozess verwendet.")

def aktuelleNachrichten():
    global is_playing

    with music_lock:
        if not is_playing:
            url = 'https://www.deutschlandfunk.de/nachrichten-100.html'

            # Holen des HTML-Inhalts der Seite
            response = requests.get(url)
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

                # Starte einen separaten Thread zum Abspielen der Musik
                threading.Thread(target=play_mp3, args=(audio_file_path,)).start()
                return True
            else:
                print("Button nicht gefunden auf der Seite!")
                return True
        else:
            print("Music is already playing.")
            return False
       