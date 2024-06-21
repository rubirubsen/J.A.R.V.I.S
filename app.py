import io
import pyautogui
import pyodbc
import re
import sys
from datetime import datetime
from dotenv import load_dotenv
import threading
from modules.information_service import *
from modules.input import *
from modules.output import *
from modules.shopping_list import *
from modules.system import *
from playsound import playsound
from pydub.playback import play

load_dotenv()

global model

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WAKE = "Jarvis" 
model = "llama3"
voice_id = "1suvBmcKlCTfzjRX7JAL"
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

# Liste der verfügbaren Stimmen mit ihren IDs
voices = {
    "Stefan": "aooilHhhdCuhtje0hCLx",
    "Angie": "mfzvLIyvgTXSjgTnaRwB",
    "Jens": "neD6Qt1SbhIelQYpHOVy",
    "Schweinebacke": "pyp0ouVwQtR8K0UAmeO0",
    "Onkel Monte": "tT5oqpuao9zAkCP1rldL",
    "tiefer Jarvis": "WgV8ZPI6TnwXGf9zkN2O",
    "Kevin": "RjXkcUtoePljvmTEjiYS",
    "Anton": "BGtECcWHNy9MizUX3BIR",
    "Original": "1suvBmcKlCTfzjRX7JAL"
}

# Liste der Befehle für handler functions
commands = {
    "deaktivieren": handle_deaktivieren,
    "liste": handle_einkaufsliste,
    "uhrzeit": handle_uhrzeit,
    "wie spät": handle_uhrzeit,
    "bilder": handle_bilder,
    "monitore": handle_monitore,
    "fenster": handle_fenster,
    "musik": handle_music,
    "stoppe musik" : stop_music,
    "starte programm": handle_starte_programm,
    "verschiebe videochat fenster": handle_verschiebe_videochat,
    "verschiebe fenster": handle_verschiebe_fenster,
    "wechsel sprachmodell": handle_wechsel_sprachmodell,
    "aktuelles sprachmodell": handle_aktuelles_sprachmodell,
    "stimmenwechsel": handle_stimmenwechsel,
    "genug für heute": handle_shutdown
}
        
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
                print(lower_case_input)
                
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
        sys.exit(1)
