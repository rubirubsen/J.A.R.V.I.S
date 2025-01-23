import tkinter as tk
from tkinter import messagebox
import pygame
import time

def process_chat_and_code(algorithm_raw):
    """Dummy-Prozess, um Daten auszugeben."""
    # Extrahieren der Werte aus dem JSON-String
    import json
    data = json.loads(algorithm_raw)
    chat_text = f"{data['codingLanguage']} - {data['taskTitle']}"
    code_block = data['code_block']
    return chat_text, code_block

def generiere_algorithmus():
    algorithm_raw = '''{
        "codingLanguage": "Python",
        "taskTitle": "Starting Spotify with Python",
        "code_block": "import spotipy\\nfrom spotipy.oauth2 import SpotifyOAuth\\n... <Weitere Zeilen>"
    }'''
    chat_text, code_block = process_chat_and_code(algorithm_raw)
    return f"{chat_text}\n\n{code_block}"

def zeige_algorithmus():
    algorithmus = generiere_algorithmus()
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    messagebox.showinfo("Generierter Algorithmus", algorithmus)
    root.destroy()

def zeige_algorithmus_tkinter():
    algorithmus = generiere_algorithmus()
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    messagebox.showinfo("Generierter Algorithmus", algorithmus)
    root.destroy()

def zeige_algorithmus_pygame():
    algorithmus = generiere_algorithmus()

    pygame.init()
    
    # Fenstergröße und Titel
    screen_width, screen_height = 800, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Generierter Algorithmus")

    # Farben und Schriftart
    white = (255, 255, 255)
    black = (0, 0, 0)
    font = pygame.font.SysFont(None, 24)
    
    # Text rendern (Split, wenn zu lang)
    lines = algorithmus.split("\n")
    rendered_lines = [font.render(line, True, black) for line in lines]

    running = True
    while running:
        screen.fill(white)

        # Zeilen anzeigen
        y_offset = 20
        for line in rendered_lines:
            text_rect = line.get_rect(topleft=(20, y_offset))
            screen.blit(line, text_rect)
            y_offset += 30

        # Event-Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False

        pygame.display.flip()

    pygame.quit()

# Ablauf: tkinter -> pygame
zeige_algorithmus_tkinter()
time.sleep(1)  # Warten für einen reibungslosen Übergang
zeige_algorithmus_pygame()
