import json
import requests
import pygame
import uuid
import os
import time
import threading
import pyttsx3
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

global is_playing
is_playing = False

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
    text_to_speech(answer)
    # engine = pyttsx3.init()
    # engine.setProperty('rate', 175)
    # engine.setProperty('voice', 'Hans RSI Harpo 22kHz')
    # engine.say(answer)
    # engine.runAndWait()

def play_mp3(file_path: str):
    global is_playing

    # Initialisiere Pygame (vor jedem Abspielen)
    pygame.init()
    pygame.mixer.init()

    # Setze is_playing auf True, um die Wiedergabe zu starten
    is_playing = True
    
    # Lade die MP3-Datei
    pygame.mixer.music.load(file_path)
    
    # Starte die Wiedergabe
    pygame.mixer.music.play()

    # Warte, bis die Wiedergabe beendet ist oder gestoppt werden soll
    while pygame.mixer.music.get_busy() and is_playing:
        pygame.time.Clock().tick(10)

    # Beende Pygame nach der Wiedergabe
    pygame.quit()

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

    # Remove the audio file
    os.remove(save_file_path)

def stop_music():
    global is_playing
    is_playing = False
    pygame.mixer.music.stop()

def handle_music():
    global is_playing
    file_path = "F:/Come non vorrei vorrei non amarti.mp3"
    threading.Thread(target=play_mp3, args=(file_path,)).start()