import os
import sys
import pyodbc
import subprocess
import time
import pyautogui
import speech_recognition as sr
from screeninfo import get_monitors
import pygetwindow as gw
from modules.output import handle_music, stop_music

def check_command(input_text, *keywords):
    return all(keyword.lower() in input_text.lower() for keyword in keywords)

def connect_to_mssql(server, database, username, password):
    """
    Connect to a Microsoft SQL Server database using pyodbc.

    Args:
        server (str): The server name or IP address.
        database (str): The database name.
        username (str): The username to use for the connection.
        password (str): The password to use for the connection.

    Returns:
        A pyodbc connection object if the connection is successful, None otherwise.
    """
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def handle_shutdown():
    speak('Alles klar, gute Nacht - du mörder!')
    print("User cancelled the AI - successful")
    sys.exit(1)
    
def handle_deaktivieren():
    speak("Okay, ich warte auf das nächste Aktivierungswort.")
    return True  # Continue loop

def move_window_to_monitor(window_title: str):
    window_title = window_title
    if any(word in window_title.lower() for word in ["videochat","camfrog","video chat","kamera chat","frosch"]):
        window_title = ": Video Chat Room"
    elif window_title.lower() == "voicemeeter":
        window_title = "VoiceMeeter"
        
    # Fenster anhand des Teils des Titels finden
    windows = [window for window in gw.getAllWindows() if window.title.endswith(window_title)]

    # Sicherstellen, dass mindestens ein Fenster gefunden wurde
    if windows:
        window = windows[0]  # Das erste Fenster in der Liste auswählen

        # Zielmonitor bestimmen
        monitors = get_monitors()

        # Berechnen, ob der Monitor links, rechts oder in der Mitte ist
        left_monitor = None
        right_monitor = None
        center_monitor = None
        for monitor in monitors:
            if monitor.x < 0:
                left_monitor = monitor
            elif monitor.x > 0:
                right_monitor = monitor
            elif monitor.is_primary:
                center_monitor = monitor

        # Benutzer nach dem Zielmonitor fragen
        speak("Auf welchen Monitor möchten Sie das Fenster verschieben? Links, Mitte oder Rechts?")
        user_input = get_audio().lower()

        # Monitorindex basierend auf Benutzereingabe auswählen
        if "links" in user_input:
            target_monitor = left_monitor
        elif "mitte" in user_input:
            target_monitor = center_monitor
        elif "rechts" in user_input:
            target_monitor = right_monitor
        else:
            speak("Entschuldigung, ich habe die Anweisung nicht verstanden.")
            return

        # Neue Position berechnen
        new_position = (target_monitor.x + 10, target_monitor.y + 10)  # Beispiel: 10 Pixel Abstand zum oberen linken Rand des Zielmonitors

        # Fenster verschieben
        window.moveTo(*new_position)
    else:
        print("Fenster mit dem Titel, der auf " + window_title + " endet, nicht gefunden.")
        
def start_exe(programm_name: str):
    programm_name = programm_name.lower()
    # exe_path = None
    
    if any(word in programm_name for word in ["spotify", "musik", "lieblingssongs"]):
       start_spotify()
    
    # if exe_path is None:
    #     print(f"Programm passend zu '{programm_name}' nicht gefunden.")
    #     return
    
    # if not os.path.isfile(exe_path):
    #     raise FileNotFoundError(f"Die Datei {exe_path} wurde nicht gefunden.")
    
    # try:
    #     # Starten der Verknüpfung
    #     os.startfile(exe_path)
    # except Exception as e:
    #     print(f"Ein Fehler ist beim Ausführen des Programms aufgetreten: {e}")
    # return True

def start_spotify():
    batch_file = "C:\\Users\\rubir\\Desktop\\start_spotify.bat"

    if not os.path.isfile(batch_file):
        raise FileNotFoundError(f"Die Datei {batch_file} wurde nicht gefunden.")

    try:
        # Starten der Batch-Datei
        subprocess.run([batch_file], shell=True)
        time.sleep(5)
        pyautogui.press('space')
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen der Batch-Datei: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

def handle_verschiebe_videochat():
    move_window_to_monitor("Videochat")
    return True

def handle_starte_programm():
    speak("Welches Programm soll ich starten?")
    programm_name = get_audio()
    start_exe(programm_name)
    return True

def handle_verschiebe_fenster():
    speak("Welches Fenster genau?")
    window_input = get_audio()
    move_window_to_monitor(window_input)
    return True

def handle_wechsel_sprachmodell():
    global model
    loop = True
    while(loop):
        speak("Welchen Modus soll ich aktivieren?")
        model_choice = get_audio()
        if any(word in model_choice for word in ["programmieren", "Programmierung", "Coding", "Software"]):
            model = "codellama"
            speak("Modell wurde angepasst")
            loop = False
        elif any(word in model_choice for word in ["casual", "unterhaltung", "smalltalk", "Small talk"]):
            model = "llama3"
            speak("Ok, ab jetzt also gemütlich.")
            loop = False
        else:
            speak("Das habe ich nicht verstanden!")
    return True

def handle_stimmenwechsel():
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
    
def handle_specific_command(command: str):
    """
    Funktion zur Verarbeitung spezifischer Befehle wie "starte Spotify".
    """
    command = command.lower()

    if "spotify" in command:
        start_exe("Spotify")
        return True
    elif "musik anhalten" in command:
        stop_music()
        return True
    elif "musik" in command:
        handle_music()  # Hier entsprechenden Programmnamen einfügen
        return True
    # Weitere spezifische Befehle hier ergänzen...

    return False  # Befehl nicht erkannt

def handle_bilder():
    # Code für Bilder anzeigen
    pass

def handle_fenster():
    # Code für Fensterinformationen abrufen
    pass
