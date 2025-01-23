import requests
from ollama import ChatResponse, chat
from typing import Dict, Any

# Beispiel-Aufruf

def get_weather(city: str) -> Dict[str, Any]:
    """
    Fetches the weather data for a given city using the OpenWeather API.

    Args:
        city (str): The name of the city for which to fetch the weather.

    Returns:
        dict: A dictionary containing the weather data for the city.
    """
    api_key = '1afe3cf1fbefb54c8b35e1ecbf355b9c'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

messages = [{'role': 'user', 'content': 'Sonnenuntergang in Hannover, Deutschland?'}]
print('Prompt:', messages[0]['content'])

tools = [
    {
        "name": "get_weather",
        "description": "Fetches current weather data for a city.",
        "function": {
            "name": "get_weather",  # Name der Funktion
            "parameters": {
                "city": {
                    "type": "string",
                    "description": "The name of the city for which to fetch the weather."
                }
            },
            "call": get_weather  # Übergabe der Funktionsreferenz hier
        }
    }
]

response = chat(
  'llama3.2',
  messages=messages,
  tools=tools
)

output = None  # Initialisieren von output, um später darauf zugreifen zu können

if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
    # There may be multiple tool calls in the response
    for tool in response.message.tool_calls:
        # Ensure the function is available, and then call it
        if function_to_call := tools[0].get("function"):
            print('Calling function:', tool.function.name)
            print('Arguments:', tool.function.arguments)

            # Überprüfen und nur 'city' an die Funktion übergeben
            if 'city' in tool.function.arguments:
                output = function_to_call["call"](city=tool.function.arguments['city'])
                print('Function output:', output)
            else:
                print('City argument not found')

        else:
            print('Function', tool.function.name, 'not found')

    # Add the function response to messages for the model to use
    messages.append(response.message)
    messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
    print('Messages:', messages)
    # Get final response from model with function outputs
    final_response = chat('llama3.2', messages=messages)

    print('Final response:', final_response.message.content)

else:
    print('No tool calls returned from model')