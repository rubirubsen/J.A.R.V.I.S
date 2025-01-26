#SPEECH OUTPUT MODULE

import pyttsx3
import threading
import json
import requests
import uuid
import queue
import dotenv
import os
import pygame
import time
import sys

from pydub import AudioSegment
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from modules.helper.shared import visualizer

dotenv.load_dotenv('../.env')
voice_id = "WgV8ZPI6TnwXGf9zkN2O"
chatter_voice_id = ""
model = "llama3.2:latest"
message_queue = queue.Queue()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def is_file_in_use(file_path):
    try:
        with open(file_path, 'r+'):
            print('File is open')
            return False
    except IOError:
        print('File is closed')
        return True

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

def speak(text):
    print('Speaking: ', text)
    file_path = 'C:/dev/python/jetson/antwort.wav'

    # Sicherstellen, dass die Datei existiert
    if os.path.exists(file_path):
        os.remove(file_path)

    # Initialisiere die pyttsx3-Engine
    engine = pyttsx3.init()

    try:
        # Setze die Sprache und Stimme (optional)
        engine.setProperty('rate', 175)
        engine.setProperty('voice', 'Hans RSI Harpo 22kHz')

        # Speichern der Sprachausgabe als WAV-Datei
        engine.save_to_file(text, file_path)
        engine.runAndWait()  # Warten bis die Sprachausgabe abgeschlossen ist
    finally:
        # Stelle sicher, dass die Engine gestoppt wird
        engine.stop()

    # Datei abspielen
    visualizer.playFile(file_path)
    
def old_speak(answer: str):
    print(answer)
    mp3_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mp3')
    wav_file = 'answer.wav'
    file_path = os.path.join(mp3_folder, wav_file)
    

    # Initialisiere pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.setProperty('voice', 'Hans RSI Harpo 22kHz')
    engine.save_to_file(answer, file_path)
    engine.runAndWait()
    engine.stop()
    
    print(f"WAV-Datei gespeichert unter {file_path}")

    # Visualizer abspielen
    try:
        visualizer.playFile(file_path)
    except pygame.error as e:
        print(f"Fehler beim Abspielen der WAV-Datei: {e}")
        
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
