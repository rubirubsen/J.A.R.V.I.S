import os
import json
from modules.sql import connect_to_mssql
from modules.output import speak
from dotenv import load_dotenv

load_dotenv()

def handle_einkaufsliste():
    print("Lade Liste...")
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    
    print(server, database,username,password)

    # Verbindung zur MSSQL-Datenbank herstellen
    conn = connect_to_mssql(server, database, username, password)
    
    if conn:
        cursor = conn.cursor()  # Cursor erstellen
        cursor.execute("SELECT * FROM shopping_list")  # SQL-Abfrage ausführen
        results = cursor.fetchall()  # Ergebnisse der Abfrage holen
        antwort = construct_sentence(results)  # Antwort konstruieren
        speak(antwort)  # Antwort sprechen
        conn.close()  # Verbindung schließen
        return True
    else:
        print("Fehler bei der Verbindung zur Datenbank.")
        return False

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

