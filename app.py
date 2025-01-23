import sys
import re
import tkinter as tk
import signal
from tkinter import messagebox
from dotenv import load_dotenv
import threading
import websocket
import json  
from pydub import AudioSegment
from pydub.playback import play
from modules.processing.system.system import *
from modules.processing.audio.audio_processor import *
from modules.input.speech.input import *
from modules.output.speech.speaker import speak, use_talker
from modules.processing.database.shopping_list import *
from modules.services.spotify import *
from modules.services.twitch import *

from playsound import playsound
from pydub.playback import play

load_dotenv()
AudioSegment.converter = 'C:/ffmpeg'
WAKE = 'Jarvis'
model = 'Llama3'
ws = None
readAloutSwitch = 0

wsurl = 'wss://rubizockt.de:3000?uid='+os.getenv('WSSECRET')+'&client_type=jarvis'

def on_message(ws, message):
    try:
        # Versuche, die Nachricht in ein Dictionary zu parsen
        message_data = json.loads(message)
        
        # Prüfe, ob das Feld 'cmd' in den empfangenen Daten existiert
        if 'cmd' in message_data:
            if message_data['cmd'] == 'trackUpdate':
                print("track update")
            elif message_data['cmd'] == 'trigger':
                return
            elif message_data['cmd'] == 'chatMessage' and readAloutSwitch == 1:
                # Extrahiere die Nachricht und den Benutzernamen, wenn verfügbar
                message_text = message_data.get('message', '')  # Verwende .get(), um einen Fehler zu vermeiden
                
                # Überprüfe, ob die Nachricht mit "!" beginnt oder vom Benutzer "rubizockt" kommt
                if message_text.startswith('!') or message_data['tags'].get('username') == 'rubizockt':
                    return  # Nachricht wird ignoriert
                
                # Wenn die Nachricht keine der oben genannten Bedingungen erfüllt
                print('MESSAGE:', message_text)
                username = message_data['tags'].get('username', 'Unbekannter Benutzer')  # Verwendet .get() für Sicherheit
                print('USER: ', username)
                read_chat(message_text, username)  # Weitergabe der Nachricht an die Funktion zum Vorlesen

            elif message_data['cmd'] == 'notPlaying':
                track_info = message_data.get('trackInfo', 'Keine Track-Info verfügbar')
                print(track_info)
    
    except json.JSONDecodeError:
        print("Fehler beim Decodieren der Nachricht: ", message)

def on_error(ws, error):
    print(f"Error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    ws.send('{"cmd":"welcomeCall", "data":"Hello Server!"}')
    print("WebSocket connection opened")

def stop_websocket(signum, frame):
    print("Stopping WebSocket...")
    ws.close()
    sys.exit(1)


signal.signal(signal.SIGINT, stop_websocket)

def run_websocket():
    global ws
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(wsurl,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("WebSocket connection interrupted")
        ws.close()
        sys.exit(0)

def handle_vorlesen_an():
    global readAloutSwitch
    readAloutSwitch = 1
    speak('Mögen die Stimmen dich in deinen Träumen verfolgen.')
    return True

def handle_vorlesen_aus():
    global readAloutSwitch
    readAloutSwitch = 0
    speak('Und jetzt halten alle gepflegt die Schnauze!')
    return True

def handle_shutdown():
    speak('Alles klar, gute Nacht - du mörder!')
    print("User cancelled the AI - successful")
    thread.join()
    sys.exit(1)

thread = threading.Thread(target=run_websocket)
thread.start()

# Liste der Befehle für handler functions
commands = {
    "aktives fenster schließen": aktives_fenster_schliessen,
    "aktives fenster minimieren": aktives_fenster_minimieren,
    "deaktivieren": handle_deaktivieren,
    "liste": handle_einkaufsliste,
    "uhrzeit": handle_uhrzeit,
    "wie spät": handle_uhrzeit,
    "bilder": handle_bilder,
    "monitore": handle_monitore,
    "fenster": handle_fenster,
    "spiele musik": handle_music,
    "stoppe musik" : stop_music,
    "starte programm": handle_starte_programm,
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
    "nachrichten": aktuelleNachrichten
}

def messageToServer():
    if ws:
        ws.send('Hello Server!')
    else:
        print("WebSocket is not connected.")

while True:  #immer
    try:  
        print("Höre zu...")
        user_input = get_audio()

        if WAKE.lower() in user_input.lower():
            if user_input.lower() == "jarvis":
                speak('Ja bitte?')
                continue
            else:
                lower_case_input = user_input.lower()
                lower_case_input = re.sub(r"(?i)jarvis", "", lower_case_input).strip()
                print("Erkannte Worte: "+lower_case_input)
                
                if handle_specific_command(lower_case_input):
                    continue  # Springe zur nächsten Iteration der Schleife
                
                # Check if command exists in dictionary and execute it
                for command, handler in commands.items():
                    if re.search(r'\b' + re.escape(command) + r'\b', lower_case_input):
                        if handler():
                            break
                    
                else:
                    answer = use_talker(lower_case_input, model)
                    print("Jarvis: " + answer)
                    speak(answer)
                    
    except KeyboardInterrupt:
        print("User cancelled the AI - successful")
        thread.join()
        sys.exit(1)
