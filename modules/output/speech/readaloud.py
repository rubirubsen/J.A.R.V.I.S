#READALOUDD MODULE FOR CHATREADER

from modules.output.speech.speaker import speak

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
