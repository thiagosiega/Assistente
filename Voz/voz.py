import speech_recognition as sr

recognizer = sr.Recognizer()

def on_shift_c_pressed():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='pt-BR')
            return text
        except sr.UnknownValueError:
            return "Não entendi o que você disse."
        except sr.RequestError as e:
            return "Erro ao se comunicar com o Google Speech Recognition: {0}".format(e)
        