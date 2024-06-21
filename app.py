import sys
import re
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

WAKE = 'Jarvis'

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
