#TIME HANDLE MODULE
from datetime import datetime
from modules.output.speech.speaker import speak
def handle_uhrzeit():
    H = datetime.now().hour
    M = datetime.now().minute
    timenow = f"{H} Uhr und {M} Minuten"
    print(timenow)
    speak(f"Es ist nun genau {timenow}")
    return True
