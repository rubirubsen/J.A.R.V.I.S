@echo off
tasklist /fi "imagename eq spotify.exe" | find /i "spotify.exe" > nul
if not errorlevel 1 (
    echo Beende laufende Spotify-Prozesse...
    taskkill /im spotify.exe /f
)
echo Starte Spotify...
start spotify:user:anything:playlist:22nGVo4QFZcfTAXcsl67kD