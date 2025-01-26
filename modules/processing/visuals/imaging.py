#IMAGE PROCESSOR MODULE
import json
import requests
from modules.output.speech.speaker import *
from modules.input.speech.input import get_audio
import re

def extract_json_from_response(response_text):
    """
    Extrahiert JSON-Inhalt aus einem möglichen Markdown-Format.
    """
    try:
        # Suche nach JSON-ähnlichem Inhalt
        json_match = re.search(r"{.*?}", response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("Kein gültiger JSON-Inhalt gefunden.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Fehler beim Parsen des JSON: {e}")

def parse_clean_response(raw_response):
    try:
        # Entferne mögliche Backticks und überprüfe auf JSON-ähnliches Format
        json_match = re.search(r"{.*}", raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("Kein JSON-Inhalt in der Antwort gefunden.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültiges JSON: {e}")
    
def bilderSuchePrompt():
    """
    Funktion zur Erstellung einer generativen Abfrage für die Bildersuche.
    Fragt den Benutzer nach einem Suchbegriff und verarbeitet diesen weiter.
    """
    url = "http://localhost:11434/api/generate"

    # Payload für die Anfrage
    payload = json.dumps({
        "model": "llama3",
        "prompt": "Du bist ein AI Assistent. Frage mich, welche Bilddateien bei Google ich suche. Wahlweise sarkastisch, ironisch oder roboterähnlich. Nur in Deutsch und maximal 30 Wörter.",
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Anfrage an den lokalen API-Endpunkt
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        # AI-Antwort ausgeben und Benutzerinput holen
        print("AI:", response_data["response"])
        speak(response_data["response"])  # Funktion spricht die Antwort
        searchterm = get_audio()  # Benutzer gibt Suchbegriff ein

        if not searchterm:
            raise ValueError("Kein Suchbegriff erkannt.")

        # Weiterverarbeitung des Suchbegriffs
        searchterm2 = bilderSucheExec(searchterm)
        return searchterm2

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage (Prompt): {e}")
        return None
    except KeyError as e:
        print(f"Fehler in der API-Antwort (Prompt): {e}")
        return None
    except ValueError as e:
        print(f"Benutzereingabe fehlgeschlagen: {e}")
        return None

def bilderSucheExec(searchterm):
    url = "http://localhost:11434/api/generate"

    payload = json.dumps({
        "model": "gemma2:2b",
        "prompt": f"Filtere den folgenden Suchbegriff: '{searchterm}'. Gib mir den gesamten Suchbegriff als Wert 'searchTerm' im JSON zurück. Keine weiteren Kommentare, nur das JSON.",
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        print("Antwort von Ollama:", response_data)  # Debug

        if "response" not in response_data:
            raise KeyError("Die API-Antwort enthält keinen 'response'-Schlüssel.")

        # Bereinige und parse die Antwort
        raw_response = response_data["response"]
        cleaned_data = extract_json_from_response(raw_response)

        # Extrahiere den Suchbegriff
        searchterm_cleaned = cleaned_data.get("searchTerm")

        if not searchterm_cleaned:
            raise ValueError("Kein Suchobjekt gefunden.")

        return searchterm_cleaned

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage (Exec): {e}")
        return None
    except KeyError as e:
        print(f"Fehler in der API-Antwort (Exec): {e}")
        return None
    except ValueError as e:
        print(f"Verarbeitung des Suchbegriffs fehlgeschlagen: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim JSON-Parsing: {e}")
        return None