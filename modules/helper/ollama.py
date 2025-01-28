# OLLAMA HELPER MODUL
# Used to perform Ollama-Request regarding the tools added to this file e.g. weather

import requests
from ollama import ChatResponse, chat
from modules.input.speech.input import get_audio
from modules.output.speech.speaker import *

import os

api_key = '1afe3cf1fbefb54c8b35e1ecbf355b9c'


def get_weather(city: str):
    """
    Fetches the weather data for a given city using the OpenWeather API.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=de"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Fehler beim Abrufen der Wetterdaten: {response.status_code}"}

def get_current_time():
    """
    Gibt den aktuellen Wochentag die aktuelle Uhrzeit aus. 
    """
    H = datetime.now().hour
    M = datetime.now().minute
    D = datetime.now().day
    Day = ''
    match D:
        case 1:
            Day = "Montag"
        case 2:
            Day = "Dienstag"
        case 3:
            Day = "Mittwoch"
        case 4: 
            Day = "Donnerstag"
        case 5: 
            Day = "Freitag"
        case 6:
            Day = "Samstag"
        case 7:
            Day = "Sonntag"
    timenow = f"Es ist {Day}. {H} Uhr und {M} Minuten"
    return timenow

def ollama_request(user_input: str):
    """
    Verarbeitet die Benutzeranfrage mit dem Ollama-Tool und extrahiert den Städtenamen.
    Ruft dann Wetterdaten für die angegebene Stadt ab.
    """
    # Anfragen-Nachricht für das Modell vorbereiten
    messages = [
        {
            "role": "user", 
            "content": user_input
        }
    ],
    tools = [
        {
            "name": "get_weather",
            "description": "Holt aktuelle Wetterdaten für eine Stadt.",
            "function": {
                "name": "get_weather",
                "parameters": {
                    "city": {
                        "type": "string",
                        "description": "Der Name der Stadt für die Wetterabfrage."
                    }
                },
                "call": get_weather,  # Referenz auf die Funktion
            },
        },
        {
            "name":"get_current_time",
            "description":"Gibt den aktuellen Wochentag und die aktuelle Uhrzeit aus",
            "function": {
                "name": "get_current_time",
                "parameters":{
                    
                }
                ,
                "call": get_current_time
            },
        }
    ]

    try:
        # Anfrage an das Modell senden
        response = chat("llama3.2", messages=messages, tools=tools)

        # Überprüfen, ob ein Tool-Aufruf für 'get_weather' gemacht wurde
        if hasattr(response.message, "tool_calls") and response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                if tool_call.function.name == "get_weather":
                    city = tool_call.function.arguments.get("city")
                    return get_weather(city) if city else {"error": "Bitte gib eine Stadt an."}
        else:
            return {"error": "Keine Tools vom Modell aufgerufen."}
            return False
    
    except Exception as e:
        # Fehlerbehandlung für mögliche Ausnahmen während der API-Anfrage oder Verarbeitung
        return {"error": f"Ein Fehler ist aufgetreten: {str(e)}"}

def send_to_ollama(user_input):
    
    print(user_input)
    
    weather_data = ollama_request(user_input)
    
    if "error" in weather_data:
        print("error in weather_data: ", weather_data["error"])
        speak(f"Fehler: {weather_data['error']}")
    else:
        city = weather_data.get("name", "unbekannte Stadt")
        temp = weather_data["main"]["temp"]
        temp = round(temp)
        description = weather_data["weather"][0]["description"]
        speak(f"In {city} beträgt die Temperatur {temp} Grad Celsius und es ist {description}.")
        return True
