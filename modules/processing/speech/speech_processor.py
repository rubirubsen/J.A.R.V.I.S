#SPEECH PROCESSOR MODULE
import queue
import os
import time
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

from modules.processing.llm.ollama import get_model_from_ollama
from modules.output.speech.speaker import use_talker
voice_id = "WgV8ZPI6TnwXGf9zkN2O"


message_queue = queue.Queue()

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

def handle_aktuelles_sprachmodell():
    
    model = get_model_from_ollama()
    print(model)
    if "codellama" in model:
        answer = use_talker("teile mir mit dass wir aktuell im Programmiermodus sind und das benutzte modell nennt sich codellama", model)
    else:
        answer = use_talker("teile mir mit dass wir aktuell im regulären unterhaltungsmodus sind und das modell nennt sich ollama3", model)
    print("Jarvis: " + answer)
    speak(answer)
    return True