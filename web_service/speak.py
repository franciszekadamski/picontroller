import pyttsx3


def speak_aloud(text):
    engine = pyttsx3.init()
    voice_rate = 120
    engine.setProperty('rate', voice_rate)
    engine.say(text)
    engine.runAndWait()

