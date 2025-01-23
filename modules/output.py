import pygame
import os
import time
import threading
import pyttsx3
from dotenv import load_dotenv
from output.speech.speaker import chat_to_speech


load_dotenv()

pygame.init()
pygame.mixer.init()

print('git suckx ass')

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