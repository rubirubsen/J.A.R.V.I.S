#MONITOR PROCESSING MODULE

from modules.input.visual.input import get_monitors_info, get_windows_info

def handle_monitore():
    monitore = get_monitors_info()
    print("Monitore: ")
    print(monitore)
    fenster = get_windows_info()
    print("Fenster: ")
    print(fenster)
    return True
