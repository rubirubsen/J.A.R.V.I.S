from datetime import datetime
from modules.input import * 
from modules.output import * 
import cv2 

def detect_objects(frame, model):
    results = model(frame)  # YOLO-Modelldurchlauf auf dem Bild
    objects = results.names  # Die erkannten Objekte
    detected_objects = []

    for idx, conf in enumerate(results.xywh[0][:, -2]):
        if conf > 0.5:  # Wir akzeptieren nur Objekte mit einer Konfidenz über 50%
            detected_objects.append(results.names[int(results.xywh[0][idx, -1])])

    return detected_objects

def handle_jarvisVision():
    cap = cv2.VideoCapture(1)  # Kamera 1 öffnen

    if not cap.isOpened():
        print("Fehler beim Öffnen der Kamera!")
        return False

    seenObjects = set()  # Set, um die erkannten Objekte zu speichern
    frame_count = 0  # Zähler für die Frames

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fehler beim Abrufen des Frames!")
            break

        # Erkennung von Objekten im aktuellen Frame mit YOLO
        detected_objects = object_detection_with_gpu(frame)

        # Wenn wir im Bereich der ersten 5 Frames sind, fügen wir die Objekte zur Menge hinzu
        if frame_count < 5:
            seenObjects.update(detected_objects)

        # Zeige den Webcam-Stream
        cv2.imshow("Jarvis Webcam", frame)

        # Erhöhe die Frame-Anzahl
        frame_count += 1

        # Beende bei "q"
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Wenn wir nach den ersten 5 Frames oder beim Beenden die Objekte sprechen wollen
    translated_objects = translate_objects(list(seenObjects))
    say_detected_objects(translated_objects)

    return True

def translate_objects(objects):
    # Wörterbuch von Englisch nach Deutsch
    object_translation = {
        "Cup": "Tasse",
        "Pen": "Stift",
        "Box": "Schachtel",
        "Plate": "Teller",
        # Füge hier mehr Objekte und deren Übersetzungen hinzu
    }

    # Übersetze die Objekte
    return [object_translation.get(obj, obj) for obj in objects]