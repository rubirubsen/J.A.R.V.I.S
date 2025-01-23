import os
import sys
import pyodbc
import subprocess
import time
import pyautogui
import webbrowser
import random
import ctypes
import speech_recognition as sr
from screeninfo import get_monitors
import pygetwindow as gw
from modules.output import handle_music, stop_music,speak,bilderSuchePrompt, bilderSucheExec
from modules.input import get_audio
from modules.sql import connect_to_mssql

global model
model = "gemma2:2b"

def check_command(input_text, *keywords):
    return all(keyword.lower() in input_text.lower() for keyword in keywords)
    
def handle_deaktivieren():
    speak("Okay, ich warte auf das nächste Aktivierungswort.")
    return True  # Continue loop

def aktives_fenster_minimieren():
    aktives_fenster = gw.getActiveWindow()
    if aktives_fenster:
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.GetForegroundWindow(), 6)  # 6 = Minimieren
        speak(f"Fenster '{aktives_fenster.title}' wurde minimiert.")
        return True
    else:
        speak("Kein aktives Fenster gefunden.")
        return False

def aktives_fenster_schliessen():
    aktives_fenster = gw.getActiveWindow()
    if aktives_fenster:
        ctypes.windll.user32.PostMessageW(ctypes.windll.user32.GetForegroundWindow(), 0x0010, 0, 0)  # 0x0010 = WM_CLOSE
        speak(f"Fenster '{aktives_fenster.title}' wurde geschlossen.")
        return True
    else:
        speak("Kein aktives Fenster gefunden.")
        return False

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
    return True

def start_process(process:str):
    script_dir = os.path.dirname(__file__)  # Verzeichnis des aktuellen Skripts
    
    batch_files = {
        "camfrog": "camfrog.bat",
        "spotify": "spotify.bat",
        "firefox": "firefox.bat",
        "notepad": "notepad.bat",
        "vscode":  "vscode.bat"
    }

    batch_file = os.path.join(script_dir, "..", "batch-folder", batch_files.get(process))
    
    if batch_file:
        try:
            # Starten der Batch-Datei
            subprocess.run([batch_file], shell=True)
            time.sleep(5)
            pyautogui.press('space')
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen der Batch-Datei: {e}")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    else:
        print(f"Keine Batch-Datei für den Prozess '{process}' gefunden.")

def handle_verschiebe_videochat():
    move_window_to_monitor("Videochat")
    return True

def handle_starte_programm():
    speak("Welches Programm soll ich starten?")
    programm_name = get_audio()
    print("verstanden:", programm_name)

    programm_name_lower = programm_name.lower()

    program_names = {
        "camfrog": ["Videochat", "camfrog", "video chat", "kamera chat", "frosch"],
        "spotify": ["spotify", "musik"],
        "firefox": ["firefox", "browser", "webbrowser"],
        "notepad": ["notepad", "editor", "texteditor"],
        "vscode": ["vscode", "code", "visual studio code", "cursor", "vscodium"],
    }

    # Finden des korrekten Schlüssels für den gegebenen Programmnamen
    found_program = None
    
    for key, names in program_names.items():
        if programm_name_lower in [name.lower() for name in names]:
            found_program = key
            break

    if found_program:
        start_process(found_program)
    else:
        speak("Ich habe dich nicht verstanden, bitte wiederhole das nochmal.")
    
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
        elif any(word in model_choice for word in ["Gangster", "Zauberer", "Magie", "Zauberei"]):
            model = "wizardlm2"
            speak("Ok, ab jetzt übernehme ich keine Gewährleistung mehr. Das Nutzen dieser Fähigkeiten birgt ein gewisses Risiko. Wizard LM aktiviert. Viel Spaß.")
            loop = False
        else:
            speak("Das habe ich nicht verstanden!")
    return True

def handle_specific_command(command: str):
    """
    Funktion zur Verarbeitung spezifischer Befehle wie "starte Spotify".
    """
    command = command.lower()

    if "spotify" in command:
        start_process("Spotify")
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
    
    searchterm = bilderSuchePrompt()
    searchterm2 = bilderSucheExec(searchterm)
    search_url = "https://www.google.com/search?q=" + searchterm2 + "&tbm=isch"
    webbrowser.open(search_url)
    for window in gw.getWindowsWithTitle(''):
        if "Google Chrome" in window.title or "Mozilla Firefox" in window.title or "Microsoft Edge" in window.title:
            window.activate()
            break
    speak('Sollten sie noch etwas brauchen sagen sie bescheid.')
    return True

def handle_fenster():
    # Code für Fensterinformationen abrufen
    pass

def handle_monitore():
    monitore = get_monitors_info()
    print("Monitore: ")
    print(monitore)
    fenster = get_windows_info()
    print("Fenster: ")
    print(fenster)
    return True
