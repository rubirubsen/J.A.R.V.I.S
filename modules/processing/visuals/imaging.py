#IMAGE PROCESSOR MODULE

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
    """
    Funktion zur Verarbeitung des Suchbegriffs.
    Ruft die API auf, um den Suchbegriff in ein sauberes JSON-Format zu bringen.
    """
    url = "http://localhost:11434/api/generate"

    # Payload für die Anfrage
    payload = json.dumps({
        "model": "gemma2:2b",
        "prompt": f"{searchterm}. Filtere diese Aussage nach einem Suchobjekt und gib mir dieses als Wert 'searchTerm' in einem JSON zurück. Keine weiteren Kommentare, nur das JSON.",
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Anfrage an den lokalen API-Endpunkt
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        # Ausgabe und Verarbeitung des Ergebnisses
        print("Antwort von API (Exec):", response_data)

        if "response" not in response_data:
            raise KeyError("Die API-Antwort enthält keinen 'response'-Schlüssel.")

        # Entferne Markdown-Backticks und parse das JSON
        raw_response = response_data["response"]
        clean_response = raw_response.strip("```json").strip("```").strip()
        print('+++CLEAN+++: ',clean_response)
        json_response = json.loads(clean_response)

        # Extrahiere den Suchbegriff
        searchterm_cleaned = json_response.get("searchTerm")

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
        return None,