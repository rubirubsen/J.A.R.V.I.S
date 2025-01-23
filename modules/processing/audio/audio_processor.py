#AUDIO PROCESSING MODULE
import threading
import pygame
import threading
import time

# Global variable to track whether music is playing
is_playing = False
music_lock = threading.Lock()  # Create a lock to ensure thread safety

def handle_music():
    global is_playing  # Access the global variable

    with music_lock:  # Ensure no other thread is trying to change the state simultaneously
        if not is_playing:  # Check if music is not currently playing
            print("Music is not playing. Starting music...")
            file_path = "F:/Come non vorrei vorrei non amarti.mp3"
            threading.Thread(target=play_mp3, args=(file_path,)).start()  # Start music in a new thread
        else:
            print("Music is already playing.")

def stop_music():
    global is_playing
    if is_playing:  # Check if music is playing
        print("Stopping music...")
        pygame.mixer.music.fadeout(300)  # Optional: Use fadeout for smooth transition
        
        # Warten, bis der Fadeout-Effekt abgeschlossen ist (maximal 300 ms)
        time.sleep(0.5)  # Eine kurze Pause, um den Übergang zu ermöglichen
        
        pygame.mixer.music.stop()  # Sicherstellen, dass die Musik gestoppt wird
        pygame.mixer.quit()  # Mixer beenden
        
        time.sleep(1)  # Gebe etwas Zeit, um sicherzustellen, dass die Musik vollständig gestoppt wurde
        is_playing = False  # Set status to False since music is stopped
        return True
    else:
        print("No music is playing.")
        return False