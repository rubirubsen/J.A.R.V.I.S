from modules.output import *

songTitle = ''
songArtist = ''

def set_title_playing(title, artist):
    global songTitle
    songTitle= title
    global songArtist
    songArtist= artist
    return

def get_title_playing():
    global songTitle
    global songArtist
    speak(f'Wir hören {songTitle} von {songArtist}. Gefällt es Dir?')
    return True

def get_playback_state():
    """Gibt den aktuellen Wiedergabestatus zurück."""
    try:
        playback = spotify.current_playback()
        if playback:
            return "PLAYING" if playback.get("is_playing") else "PAUSED"
        return "Keine Wiedergabe aktiv."
    except Exception as e:
        return f"Fehler: {e}"


def get_current_time():
    """Gibt die aktuelle Position des Songs (in Sekunden) zurück."""
    try:
        playback = spotify.current_playback()
        if playback:
            return playback.get("progress_ms", 0) / 1000
        return 0
    except Exception as e:
        return f"Fehler: {e}"


def get_duration():
    """Gibt die Gesamtdauer des aktuellen Songs (in Sekunden) zurück."""
    try:
        playback = spotify.current_playback()
        if playback and playback.get("item"):
            return playback["item"]["duration_ms"] / 1000
        return 0
    except Exception as e:
        return f"Fehler: {e}"


def add_song_to_playlist(playlist_id, song_uri):
    """Fügt einen Song zur angegebenen Playlist hinzu."""
    try:
        spotify.playlist_add_items(playlist_id, [song_uri])
        return True
    except Exception as e:
        return f"Fehler: {e}"


def search_song(song_name):
    """Sucht nach einem Song und gibt dessen URI zurück."""
    try:
        results = spotify.search(q=song_name, type="track", limit=1)
        if results["tracks"]["items"]:
            return results["tracks"]["items"][0]["uri"]
        return "Kein Song gefunden."
    except Exception as e:
        return f"Fehler: {e}"
