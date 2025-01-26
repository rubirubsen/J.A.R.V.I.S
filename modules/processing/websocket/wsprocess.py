import websocket
import os
import json
import signal
import sys
from modules.output.speech.speaker import *
from modules.helper.shared import visualizer

ws = None
wsurl = 'wss://rubizockt.de:3000?uid='+os.getenv('WSSECRET')+'&client_type=jarvis'

artist_names = 'niemandem'
track_name = 'Keine Musik'
readAloutSwitch = 0
def run_websocket():
    global ws
    websocket.enableTrace(False)
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
        
def stop_websocket(signum, frame):
    print("Stopping WebSocket...")
    ws.close()
    visualizer.stop_visualizer()
    sys.exit(1)
def soft_stop():
    print("AI fährt herunter")
    ws.close()
    visualizer.stop_visualizer()
    sys.exit(1)

def on_message(ws, message):
    try:
        # Versuche, die Nachricht in ein Dictionary zu parsen
        message_data = json.loads(message)
        
        # Prüfe, ob das Feld 'cmd' in den empfangenen Daten existiert
        if 'cmd' in message_data:
            global artist_names, track_name  # Füge das hier hinzu, um globale Variablen zu verwenden
            if message_data['cmd'] == 'trackUpdate':
                old_track = track_name
                old_artist = artist_names
                track_data = json.loads(message_data['data'])
                track_name = track_data['track']['trackName']
                artist_names = track_data['track']['artistNames']
                
                if track_name == old_track:
                    return
                else:
                    print("+++ NOW PLAYING: "+ artist_names + " - " + track_name + ' +++')
                
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
    ws.send('{"cmd":"welcomeCall", "data":"Hello Server!"}') #TODO: ordentliche Anmeldungsroutine implementieren
    print("WebSocket connection opened")

def get_song_info():
    global track_name,artist_names
    return {
        "track_name":track_name, 
        "artist_names": artist_names
    }

def set_song_info(newArtist, newTrack):
    global track_name, artist_names
    track_name = newArtist
    artist_names = newTrack
