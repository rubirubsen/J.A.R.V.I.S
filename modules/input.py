import speech_recognition as sr
from screeninfo import get_monitors
import pygetwindow as gw
import cv2 

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Sprechen Sie jetzt...")
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio, language="de-DE")
            print("Gesagt:", said)
        except Exception as e:
            print("Exception: " + str(e))

    return said

def get_monitors_info():
    monitors = get_monitors()
    num_monitors = len(monitors)
    arrangement = []
    for m in monitors:
        arrangement.append(f"Monitor {m.name}: {m.width}x{m.height} at ({m.x}, {m.y})")
    return num_monitors, arrangement

def get_windows_info():
    windows = gw.getAllWindows()
    windows_info = [f"{w.title} at ({w.left}, {w.top}, {w.width}, {w.height})" for w in windows]
    return windows_info

def switch_lights_on():
    print(f'lights are on')
    return True

def start_webcam():
    """
    Startet die Webcam und zeigt einen Live-Feed in einem Fenster an.
    Drücke 'q', um den Stream zu beenden.
    """
    # Zugriff auf die Standard-Webcam (Kamera 0)
    webcam = cv2.VideoCapture(1)

    # Überprüfen, ob die Webcam erfolgreich geöffnet wurde
    if not webcam.isOpened():
        print("Fehler: Webcam konnte nicht geöffnet werden.")
        return

    print("Webcam gestartet. Drücke 'q', um den Stream zu beenden.")

    while True:
        # Einzelnen Frame von der Webcam lesen
        ret, frame = webcam.read()

        # Überprüfen, ob der Frame erfolgreich gelesen wurde
        if not ret:
            print("Fehler beim Lesen des Frames.")
            break

        # Frame im Fenster anzeigen
        cv2.imshow('Jarvis Webcam View', frame)

        # Warte auf Tastendruck 'q', um den Stream zu beenden
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Webcam-Stream beendet.")
            break

    # Ressourcen freigeben
    webcam.release()
    cv2.destroyAllWindows()
    return True
