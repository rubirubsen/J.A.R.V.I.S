import os
import json
import pyodbc
from dotenv import load_dotenv
load_dotenv()

def handle_einkaufsliste():
    print("Lade Liste...")
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    conn = connect_to_mssql(server, database, username, password)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_list")
    results = cursor.fetchall()
    antwort = construct_sentence(results)
    speak(antwort)
    return True

def construct_sentence(results):
    sentence = "Auf der Einkaufsliste stehen: "
    for row in results:
        id, item, count, note = row
        if count == 1:
            item_string = f"ein mal {item}"
        else:
            item_string = f"{count} mal {item}"
            
        if note:
            item_string += f", Notiz: {note}"
        sentence += item_string + ", "
    sentence = sentence.rstrip(", ") + ". Und das ist alles."
    return sentence

def format_shopping_list_sql_results(results):
    formatted_results = []
    for row in results:
        id, item, count, note = row
        formatted_row = {
            "count": count,
            "item": item,
            "note": note
        }
        formatted_results.append(formatted_row)
    return json.dumps(formatted_results)

