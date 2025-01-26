#OLLAMA MAIN MODULE
import requests

from modules.output.speech.speaker import *

def get_model_from_ollama():
    try:
        # URL des Ollama-Servers, passe dies je nach Server und Endpunkt an
        ollama_url = "http://localhost:11434/api/ps"  # Verwende den richtigen Port und Endpunkt
        response = requests.get(ollama_url)
        
        # Überprüfe, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            model_data = response.json()  # Angenommen, die Antwort ist im JSON-Format
            
            # Das Modell aus der Antwort extrahieren
            models = model_data.get("models", [])  # Liste der Modelle extrahieren
            if models:
                model_name = models[0].get("model")  # Holen des Modellnamens des ersten Modells
                return model_name
            else:
                print("Kein Modell gefunden.")
                return None
        else:
            print(f"Fehler beim Abrufen des Modells: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None

    try:
        # URL des Ollama-Servers, passe dies je nach Server und Endpunkt an
        ollama_url = "http://localhost:11434/api/ps"  # Verwende den richtigen Port und Endpunkt
        response = requests.get(ollama_url)
        
        # Überprüfe, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            model_data = response.json()  # Angenommen, die Antwort ist im JSON-Format
            
            # Das Modell aus der Antwort extrahieren
            models = model_data.get("models", [])  # Liste der Modelle extrahieren
            if models:
                model_name = models[0].get("model")  # Holen des Modellnamens des ersten Modells
                return model_name
            else:
                print("Kein Modell gefunden.")
                return None
        else:
            print(f"Fehler beim Abrufen des Modells: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None
    
def handle_aktuelles_sprachmodell():
    
    model = get_model_from_ollama()
    print(model)
    if "codellama" in model:
        answer = use_talker("teile mir mit dass wir aktuell im Programmiermodus sind und das benutzte modell nennt sich codellama", model)
    else:
        answer = use_talker("teile mir mit dass wir aktuell im regulären unterhaltungsmodus sind und das modell nennt sich ollama3", model)
    print("Jarvis: " + answer)
    speak(answer)
    return True
