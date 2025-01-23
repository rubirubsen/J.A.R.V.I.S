#SPEECH INPUT MODULE

import speech_recognition as sr


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Sprechen Sie jetzt...")
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio, language="de-DE")
            print("Gesagt:", said)
        except Exception as e:
            print("Exception: " + str(e))

    return said
