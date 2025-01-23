import re
import json 

def process_chat_and_code(text):
    # Variablen initialisieren
    chat_text = ""
    code_block = ""

    # Escape-Zeichen und Codeblöcke erkennen
    # Ersetze Escape-Zeichen (z.B. \n, \t) korrekt
    text = bytes(text, 'utf-8').decode('unicode_escape')

    # Suche nach Codeblöcken (alles zwischen ```...```)
    code_match = re.search(r'```(.*?)```', text, re.DOTALL)

    if code_match:
        # Text vor dem Codeblock als Chat-Text
        chat_text = text.split('```')[0].strip()

        # Extrahiere den Codeblock
        code_block = code_match.group(1).strip()

        # JSON-Validierung und saubere Ausgabe
        try:
            # Falls der Codeblock JSON-Daten enthält
            json_data = json.loads(code_block)
            print("Saubere JSON-Daten in der Konsole:")
            print(json.dumps(json_data, indent=4))
        except json.JSONDecodeError:
            print("Kein gültiges JSON im Codeblock gefunden.")

        # Text nach dem Codeblock als weiteren Chat-Text
        remaining_text = text.split('```', 2)[-1].strip()

        # Füge den verbleibenden Chat-Text zum ursprünglichen Chat-Text hinzu
        chat_text += "\n" + remaining_text
    else:
        # Wenn kein Codeblock vorhanden ist, wird der gesamte Text als Chat-Text behandelt
        chat_text = text

    return chat_text, code_block


def generiere_algorithmus():
    algorithm_raw = '{\n\"codingLanguage\": \"Python\",\n\"taskTitle\": \"Starting Spotify with Python\",\n\"code_block\": \"<span class=\\\"hljs-keyword\\\">import</span> spotipy<br><span class=\\\"hljs-keyword\\\">from</span> spotipy.oauth2 <span class=\\\"hljs-keyword\\\">import</span> SpotifyOAuth<br><br><span class=\\\"hljs-comment\\\"># Replace with your client ID and secret from the Spotify Developer Dashboard</span><br><span class=\\\"hljs-variable\\\">client_id</span> = \\\"your_client_id_here\\\"<br><span class=\\\"hljs-variable\\\">client_secret</span> = \\\"your_client_secret_here\\\"<br><br><span class=\\\"hljs-keyword\\\">scope</span> = <span class=\\\"hljs-string\\\">\\\"user-read-private user-read-email\\\"</span><br><br>auth_manager = SpotifyOAuth(<span class=\\\"hljs-variable\\\">client_id</span>, <span class=\\\"hljs-variable\\\">client_secret</span>, <span class=\\\"hljs-string\\\">\\\"http://localhost:8080/callback\\\"</span>, <span class=\\\"hljs-keyword\\\">scope</span>)<br><br>spotify = spotipy.Spotify(auth_manager=auth_manager)<br><br><span class=\\\"hljs-comment\\\"># Replace with the URL of your local server</span><br><span class=\\\"hljs-keyword\\\">server</span> = <span class=\\\"hljs-string\\\">\\\"http://localhost:8080/callback\\\"</span><br><br><span class=\\\"hljs-keyword\\\">@app.route</span>(<span class=\\\"hljs-string\\\">\\\"/callback\\\"</span>)<br><span class=\\\"hljs-keyword\\\">def</span> <span class=\\\"hljs-title function\\\">callback</span>():<br>&nbsp;&nbsp;<span class=\\\"hljs-comment\\\"># Spotify redirects the user to this endpoint after authorization</span><br>&nbsp;&nbsp;<span class=\\\"hljs-keyword\\\">global</span> <span class=\\\"hljs-variable\\\">auth_manager</span><br>&nbsp;&nbsp;<span class=\\\"hljs-comment\\\"># Get the access token from Spotify</span><br>&nbsp;&nbsp;access_token = auth_manager.get_access_token(<span class=\\\"hljs-string\\\">\\\"http://localhost:8080/callback\\\"</span>)<br>&nbsp;&nbsp;<span class=\\\"hljs-keyword\\\">if</span> (access_token is <span class=\\\"hljs-literal\\\">None</span>):<br>&nbsp;&nbsp;&nbsp;&nbsp;return <span class=\\\"hljs-string\\\">\\\"Access denied\\\"</span><br><br>&nbsp;&nbsp;# Use the access token to make requests to Spotify API</br>&nbsp;&nbsp;spotify.trace = True<br>&nbsp;&nbsp;print(spotify.user_playlists())\"\n}'
    chat_text, code_block = process_chat_and_code(algorithm_raw)
    print('CHAT TEXT: ', chat_text)
    print('CODEBLOCK :', code_block)
    return chat_text, code_block; 
