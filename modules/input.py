import speech_recognition as sr
from screeninfo import get_monitors
import pygetwindow as gw

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