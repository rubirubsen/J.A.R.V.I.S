import re
import json 

import re
import json

def process_chat_and_code(text):
    # Variablen initialisieren
    chat_text = ""
    code_block = ""

    # Escape-Zeichen und Codeblöcke erkennen
    # Ersetze Escape-Zeichen (z.B. \n, \t) korrekt
    text = bytes(text, 'utf-8').decode('unicode_escape')

    # Suche nach Codeblöcken (alles zwischen ```...```)
    code_match = re.search(r'```(.*?)```', text, re.DOTALL)

    if code_match:
        # Text vor dem Codeblock als Chat-Text
        chat_text = text.split('```')[0].strip()

        # Extrahiere den Codeblock
        code_block = code_match.group(1).strip()

        # JSON-Validierung und saubere Ausgabe
        try:
            # Falls der Codeblock JSON-Daten enthält
            json_data = json.loads(code_block)
            print("Saubere JSON-Daten in der Konsole:")
            print(json.dumps(json_data, indent=4))
        except json.JSONDecodeError:
            print("Kein gültiges JSON im Codeblock gefunden.")

        # Text nach dem Codeblock als weiteren Chat-Text
        remaining_text = text.split('```', 2)[-1].strip()

        # Füge den verbleibenden Chat-Text zum ursprünglichen Chat-Text hinzu
        chat_text += "\n" + remaining_text
    else:
        # Wenn kein Codeblock vorhanden ist, wird der gesamte Text als Chat-Text behandelt
        chat_text = text

    return chat_text, code_block
