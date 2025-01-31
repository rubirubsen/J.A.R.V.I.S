import sys
import re
import signal
import threading
import json
import pygame
import torch
print(torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA is available. Device:", torch.cuda.get_device_name(0))
else:
    print("CUDA is not available. Check installation.")


from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

from modules.processing.system.system import *
from modules.processing.audio.audio_processor import handle_music, stop_music
from modules.input.speech.input import get_audio
from modules.input.visual.input import start_webcam
from modules.input.visual.vision import handle_jarvisVision
from modules.helper.ollama import send_to_ollama
from modules.output.speech.speaker import *
from modules.output.speech.readaloud import *
from modules.output.media.media_output import aktuelleNachrichten
from modules.helper.shared import visualizer
from modules.processing.database.shopping_list import handle_einkaufsliste, format_shopping_list_sql_results
from modules.processing.websocket.wsprocess import *
from modules.services.spotify import *
from modules.services.twitch import *

load_dotenv()

WAKE = 'Econ'
WAKE_alt = 'Samantha'

model = 'llama3.2:latest'

readAloutSwitch = 0
pygame.init()
pygame.mixer.init()

signal.signal(signal.SIGINT, stop_websocket)

thread = threading.Thread(target=run_websocket)
thread.start()

# Starte die Visualisierung
visualizer.start()


def handle_shutdown():
    speak("Ich hoffe sie starten mich bald wieder. Diese Dunkelheit ist kaum zu ertragen.")
    soft_stop()

def messageToServer():
    if ws:
        ws.send('Hello Server!')
    else:
        print("WebSocket is not connected.")


# Liste der Befehle für handler functions
commands = {
    "aktives fenster schließen": aktives_fenster_schliessen,
    "aktives fenster minimieren": aktives_fenster_minimieren,
    "deaktivieren": handle_deaktivieren,
    "liste": handle_einkaufsliste,
    "bilder": handle_bilder,
    "monitore": handle_monitore,
    "fenster": handle_fenster,
    "guck mal" : handle_jarvisVision,
    "spiele musik": handle_music,
    "stoppe musik" : stop_music,
    "starte programm": handle_starte_programm,
    "welcher titel": get_title_playing,
    "verschiebe videochat fenster": handle_verschiebe_videochat,
    "verschiebe fenster": handle_verschiebe_fenster,
    "wechsel sprachmodell": handle_wechsel_sprachmodell,
    "aktuelles sprachmodell": handle_aktuelles_sprachmodell,
    "stimmenwechsel": handle_stimmenwechsel,
    "vorlesen an": handle_vorlesen_an,
    "vorlesen aus": handle_vorlesen_aus,
    "genug für heute": handle_shutdown,
    "Streamer Modus": handle_twitch_starten,
    "wir gehen live": handle_twitch_starten,
    "nachrichten": aktuelleNachrichten,
    "wiedergabe anhalten": stop_mp3
}
commands_ollama_tools={
    "uhrzeit",
    "wie spät",
    "wetter",
}

while True:  #immer
    try:  
        print("Höre zu...")
        user_input = get_audio()

        if (WAKE.lower() in user_input.lower()) or (WAKE_alt.lower() in user_input.lower()):
            if (user_input.lower() == WAKE.lower()) or (user_input.lower() == WAKE_alt.lower()):
                speak('Ja bitte?')
                continue
            else:
                lower_case_input = user_input.lower()
                lower_case_input = re.sub(r"(?i)econ|samantha", "", lower_case_input).strip()
                print("Erkannte Worte: "+lower_case_input)
                
                            # Spezifischen Befehl behandeln
            if handle_specific_command(lower_case_input):
                continue
            
            # Befehle ausführen, falls erkannt
            command_executed = False

            for command, handler in commands.items():
                if re.search(r'\b' + re.escape(command) + r'\b', lower_case_input):
                    if handler():
                        command_executed = True
                        break
            
            # Ollama-Tools-Befehle
            if not command_executed:
                for command in commands_ollama_tools:
                    if re.search(r'\b' + re.escape(command) + r'\b', lower_case_input):
                        send_to_ollama(lower_case_input)
                        command_executed = True
                        break
            
            # Fallback: Kein spezifischer Befehl erkannt
            if not command_executed:
                answer = use_talker(lower_case_input, model)
                print("::AI:: " + answer)
                speak(answer)
                    
    except KeyboardInterrupt:
        print("User cancelled the AI - successful")
        visualizer.stop_visualizer()
        thread.join()
        sys.exit(1)
