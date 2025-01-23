import json
import requests
import pygame
import uuid
import os
import time
import threading
import pyttsx3
import threading
import queue
from bs4 import BeautifulSoup
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from modules.input import get_audio

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
pygame.init()
pygame.mixer.init()

voice_id = "WgV8ZPI6TnwXGf9zkN2O"
chatter_voice_id = ""
model = "llama3"
message_queue = queue.Queue()

# Global variable to track whether music is playing
is_playing = False
music_lock = threading.Lock()  # Create a lock to ensure thread safety

def process_messages():
    while True:
        text, voice_id = message_queue.get()  # Nachricht und Voice-ID aus der Queue entnehmen
        try:
            chat_to_speech(text, voice_id)  # Nachricht verarbeiten
        finally:
            message_queue.task_done()  # Markiere die Aufgabe als erledigt

def enqueue_message(data):
    message_queue.put(data)  # Füge die Nachricht in die Queue ein

def stop_processing():
    """Stoppt den Verarbeitungsthread."""
    message_queue.put((None, None))  # Stopp-Signal
    processing_thread.join()

processing_thread = threading.Thread(target=process_messages, daemon=True)
processing_thread.start()

def use_talker(prompt: str, model: str):
    api_url = "http://127.0.0.1:11434/api/generate"
    prompt = prompt + ". Maximal 30 Worte. In Deutsch."
    print("Sending: " + prompt)
    headers = {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'application/json'
    }
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    response_raw = requests.request("POST", api_url, headers=headers, data=payload)
    response_json = json.loads(response_raw.text)
    print(response_json)
    answer = response_json['response']
    return answer

def speak(answer: str):
    # text_to_speech(answer)
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('voice', 'Hans RSI Harpo 22kHz')
    engine.say(answer)
    engine.runAndWait()

def text_to_speech(text: str):
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id=voice_id,  
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.6,
            similarity_boost=0.7,
            style=0.13,
            use_speaker_boost=True,
        ),
    )

    # Generating a unique file name for the output MP3 file
    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Playing the audio file
    play_mp3(save_file_path)
    time.sleep(1)

def handle_stimmenwechsel():
    # Liste der verfügbaren Stimmen mit ihren IDs
    voices = {
        "Stefan": "aooilHhhdCuhtje0hCLx",
        "Tom": "nPczCjzI2devNBz1zQrb",
        "Aria": "9BWtsMINqrJLrRacOk9x",
        "Jens": "sEdFrFTCDGCgMzAJgN23",
        "Schweinebacke": "pyp0ouVwQtR8K0UAmeO0",
        "Onkel Monte": "tT5oqpuao9zAkCP1rldL",
        "tiefer Jarvis": "WgV8ZPI6TnwXGf9zkN2O",
        "Kevin": "RjXkcUtoePljvmTEjiYS",
        "Anton": "BGtECcWHNy9MizUX3BIR",
        "Original": "1suvBmcKlCTfzjRX7JAL"
    }

    # Die verfügbaren Stimmen dynamisch aus der Liste abrufen
    available_voices = ", ".join(voices.keys())
    speak(f"Welche Stimme soll es sein? Verfügbare Stimmen sind: {available_voices}")
    stimme_input = get_audio().strip()

    # Stimme ändern, wenn sie in der Liste verfügbar ist
    if stimme_input in voices:
        global voice_id
        voice_id = voices[stimme_input]
        speak(f"Die Stimme wurde auf {stimme_input} geändert.")
    else:
        speak(f"Entschuldigung, die Stimme {stimme_input} ist nicht verfügbar.")
    return True

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

def stop_music():
    global is_playing
    if is_playing:  # Check if music is playing
        print("Stopping music...")
        pygame.mixer.music.fadeout(300)  # Optional: Use fadeout for smooth transition
        
        # Warten, bis der Fadeout-Effekt abgeschlossen ist (maximal 300 ms)
        time.sleep(0.5)  # Eine kurze Pause, um den Übergang zu ermöglichen
        
        pygame.mixer.music.stop()  # Sicherstellen, dass die Musik gestoppt wird
        pygame.mixer.quit()  # Mixer beenden
        
        time.sleep(1)  # Gebe etwas Zeit, um sicherzustellen, dass die Musik vollständig gestoppt wurde
        is_playing = False  # Set status to False since music is stopped
        return True
    else:
        print("No music is playing.")
        return False

def handle_music():
    global is_playing  # Access the global variable

    with music_lock:  # Ensure no other thread is trying to change the state simultaneously
        if not is_playing:  # Check if music is not currently playing
            print("Music is not playing. Starting music...")
            file_path = "F:/Come non vorrei vorrei non amarti.mp3"
            threading.Thread(target=play_mp3, args=(file_path,)).start()  # Start music in a new thread
        else:
            print("Music is already playing.")

def read_chat(text: str , username:str):
    
    chatters = {
        "bohnenkrautsaft":"sEdFrFTCDGCgMzAJgN23",
        "mjrey_":"cgSgspJ2msm6clMCkdW9",
        "derhamsta":"tT5oqpuao9zAkCP1rldL",
        "frauhamsta":"9BWtsMINqrJLrRacOk9x",
        "erik_zev":"pyp0ouVwQtR8K0UAmeO0",
        "completabledev":"BGtECcWHNy9MizUX3BIR",
        "schwatvogel":"TX3LPaxmHKxFdv7VOQHJ",
        "mr_n00bis":"pqHfZKP75CvOlQylNhV4",
        "radioante":"nPczCjzI2devNBz1zQrb",
        "demonic_medusa":"Xb7hH8MSUJpSbSDYk0k2",
        "xhorror":"N2lVS1w4EtoT3dr4eOWO",
        "l0wb0b88":"IKne3meq5aSn9XLyUdCD",
        "zeroacid89":"RjXkcUtoePljvmTEjiYS",
        "framesecond":"cjVigY5qzO86Huf0OWal",
    }

    if username in chatters:
        print(f"Found {username} in Chatters")
        voice_id = chatters[username]
        enqueue_message((text, voice_id))  # Füge Text und Voice-ID in die Queue ein
    else:
        print(f"User {username} not found in chatters list.")
        voice_id = 'bIHbv24MWmeRgasZH58o'
        enqueue_message((text, voice_id))   # Füge Text und Voice-ID in die Queue ein

def chat_to_speech(text: str,voice_id:str):
    
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id=voice_id,  
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.6,
            similarity_boost=0.7,
            style=0.13,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Playing the audio file
    play_mp3(save_file_path)
    time.sleep(1)

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
        
def bilderSuchePrompt():
    """
    Funktion zur Erstellung einer generativen Abfrage für die Bildersuche.
    Fragt den Benutzer nach einem Suchbegriff und verarbeitet diesen weiter.
    """
    url = "http://localhost:11434/api/generate"

    # Payload für die Anfrage
    payload = json.dumps({
        "model": "llama3",
        "prompt": "Du bist ein AI Assistent. Frage mich, welche Bilddateien bei Google ich suche. Wahlweise sarkastisch, ironisch oder roboterähnlich. Nur in Deutsch und maximal 30 Wörter.",
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Anfrage an den lokalen API-Endpunkt
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        # AI-Antwort ausgeben und Benutzerinput holen
        print("AI:", response_data["response"])
        speak(response_data["response"])  # Funktion spricht die Antwort
        searchterm = get_audio()  # Benutzer gibt Suchbegriff ein

        if not searchterm:
            raise ValueError("Kein Suchbegriff erkannt.")

        # Weiterverarbeitung des Suchbegriffs
        searchterm2 = bilderSucheExec(searchterm)
        return searchterm2

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage (Prompt): {e}")
        return None
    except KeyError as e:
        print(f"Fehler in der API-Antwort (Prompt): {e}")
        return None
    except ValueError as e:
        print(f"Benutzereingabe fehlgeschlagen: {e}")
        return None

def bilderSucheExec(searchterm):
    """
    Funktion zur Verarbeitung des Suchbegriffs.
    Ruft die API auf, um den Suchbegriff in ein sauberes JSON-Format zu bringen.
    """
    url = "http://localhost:11434/api/generate"

    # Payload für die Anfrage
    payload = json.dumps({
        "model": "gemma2:2b",
        "prompt": f"{searchterm}. Filtere diese Aussage nach einem Suchobjekt und gib mir dieses als Wert 'searchTerm' in einem JSON zurück. Keine weiteren Kommentare, nur das JSON.",
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Anfrage an den lokalen API-Endpunkt
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        # Ausgabe und Verarbeitung des Ergebnisses
        print("Antwort von API (Exec):", response_data)

        if "response" not in response_data:
            raise KeyError("Die API-Antwort enthält keinen 'response'-Schlüssel.")

        # Entferne Markdown-Backticks und parse das JSON
        raw_response = response_data["response"]
        clean_response = raw_response.strip("```json").strip("```").strip()
        print('+++CLEAN+++: ',clean_response)
        json_response = json.loads(clean_response)

        # Extrahiere den Suchbegriff
        searchterm_cleaned = json_response.get("searchTerm")

        if not searchterm_cleaned:
            raise ValueError("Kein Suchobjekt gefunden.")

        return searchterm_cleaned

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage (Exec): {e}")
        return None
    except KeyError as e:
        print(f"Fehler in der API-Antwort (Exec): {e}")
        return None
    except ValueError as e:
        print(f"Verarbeitung des Suchbegriffs fehlgeschlagen: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim JSON-Parsing: {e}")
        return None,
