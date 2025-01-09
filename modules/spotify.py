import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API-Konfiguration (füge hier deine eigenen Daten ein)
SPOTIFY_CLIENT_ID = "dein_client_id"
SPOTIFY_CLIENT_SECRET = "dein_client_secret"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state playlist-modify-private"

# Authentifizierung
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))


def get_title_playing():
    """Gibt den Titel des aktuell gespielten Songs zurück."""
    try:
        playback = spotify.current_playback()
        if playback and playback.get("is_playing"):
            track = playback["item"]
            return f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}"
        return "Aktuell wird nichts abgespielt."
    except Exception as e:
        return f"Fehler: {e}"


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
