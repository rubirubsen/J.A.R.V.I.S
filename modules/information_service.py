from modules.input import get_monitors_info, get_windows_info

def handle_monitore():
    monitore = get_monitors_info()
    print("Monitore: ")
    print(monitore)
    fenster = get_windows_info()
    print("Fenster: ")
    print(fenster)
    return True

def handle_aktuelles_sprachmodell():
    print(model)
    if "codellama" in model:
        answer = use_talker("teile mir mit dass wir aktuell im Programmiermodus sind und das benutzte modell nennt sich codellama", model)
    else:
        answer = use_talker("teile mir mit dass wir aktuell im regulären unterhaltungsmodus sind und das modell nennt sich ollama3", model)
    print("Jarvis: " + answer)
    speak(answer)
    return True

def handle_uhrzeit():
    H = datetime.now().hour
    M = datetime.now().minute
    timenow = f"{H} Uhr und {M} Minuten"
    print(timenow)
    speak(f"Es ist nun genau {timenow}")
    return True
   
