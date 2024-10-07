import tkinter as tk
import re
import sys
import os
import pyttsx3  
import threading
import speech_recognition as sr

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from personalidade import Personalidade
from Gemini.gemini_ia import IA

COMANDOS_DISPONIVEIS = ["janela", "olamundo"]

class Janela:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Janela de Bate Papo")

        personalidade_atual = "objetiva"  
        self.personalidade = Personalidade(personalidade_atual)
        self.personalidade_atual = tk.StringVar(value=personalidade_atual)

        self.create_widgets()

        self.gemini = IA()
        self.tts_engine = pyttsx3.init()
        
        self.chat_log.tag_config('negrito', font=('Helvetica', 12, 'bold'))
        self.chat_log.tag_config('italico', font=('Helvetica', 12, 'italic'))

        self.personalidade_atual.trace("w", self.atualizar_personalidade)

        # Bind para detectar Shift+C pressionado e liberado
        self.root.bind('<Shift-C>', self.on_shift_c_pressed)
        self.root.bind('<KeyRelease-Shift_L>', self.on_shift_c_released)

        self.voice_active = False

    def janela(self):
        janela_ia = tk.Toplevel(self.root)
        janela_ia.title("Janela criada pela IA")
        janela_ia.geometry("500x600")

    def olamundo(self):
        print("Olá Mundo")

    def definir_personalidade(self, texto):
        return self.personalidade.definir_personalidade(texto)

    def aplicar_filtros(self, texto):
        topico_negrito_pat = re.compile(r'\* \*\*(.*?)\*\*')  
        negrito_pat = re.compile(r'\*\*(.*?)\*\*')  
        italico_pat = re.compile(r'\*(.*?)\*')  
        comando_pat = re.compile(r'\$&(\w+)&\$')  
        topico_pat = re.compile(r'\*(\S.*?)')  

        def aplicar_estilo(match, tag):
            self.chat_log.insert(tk.END, match.group(1), tag)

        index = 0

        for match in topico_negrito_pat.finditer(texto):
            self.chat_log.insert(tk.END, texto[index:match.start()])
            self.chat_log.insert(tk.END, '=> ', 'italico')  
            aplicar_estilo(match, 'negrito')
            index = match.end()

        for match in negrito_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_estilo(match, 'negrito')
            index = match.end()

        for match in italico_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_estilo(match, 'italico')
            index = match.end()

        for match in topico_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            self.chat_log.insert(tk.END, '=> ', 'italico')  

        for match in comando_pat.finditer(texto[index:]):
            comando = match.group(1)
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            index = match.end()

            if comando in COMANDOS_DISPONIVEIS:
                if comando == "janela":
                    self.janela()
                elif comando == "olamundo":
                    self.olamundo()

        if index < len(texto):
            self.chat_log.insert(tk.END, texto[index:])

    def create_widgets(self):
        self.chat_log = tk.Text(self.root, state='disabled', width=50, height=20)
        self.scrollbar = tk.Scrollbar(self.root, command=self.chat_log.yview)
        self.chat_log.config(yscrollcommand=self.scrollbar.set)

        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.pack(fill=tk.X, padx=5, pady=5)

        self.send_button = tk.Button(self.root, text="Enviar", command=self.enviar_mensagem)
        self.send_button.pack(fill=tk.X, padx=5, pady=5)

        self.exit_button = tk.Button(self.root, text="Sair", command=self.root.quit)
        self.exit_button.pack(fill=tk.X, padx=5, pady=5)

        personalidades = ["objetiva", "informativa", "conversacional"]
        self.personalidade_menu = tk.OptionMenu(self.root, self.personalidade_atual, *personalidades)
        self.personalidade_menu.pack(fill=tk.X, padx=5, pady=5)

        self.voice_button = tk.Button(self.root, text="Voz", command=self.on_voice_button_pressed)
        self.voice_button.pack(fill=tk.X, padx=5, pady=5)

    def on_voice_button_pressed(self):
        threading.Thread(target=self.start_voice_recognition).start()

    def on_shift_c_pressed(self, event=None):
        if not self.voice_active:
            self.voice_active = True
            threading.Thread(target=self.start_voice_recognition).start()

    def on_shift_c_released(self, event=None):
        self.voice_active = False

    def start_voice_recognition(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Aguarde um momento... Fale agora.")
            while self.voice_active:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                try:
                    text = recognizer.recognize_google(audio, language='pt-BR')
                    print(f"Você disse: {text}")
                    self.entry_box.delete(0, tk.END)
                    self.entry_box.insert(tk.END, text)
                    self.enviar_mensagem()
                except (sr.UnknownValueError, sr.RequestError):
                    pass

    def atualizar_personalidade(self, *args):
        nova_personalidade = self.personalidade_atual.get()
        self.personalidade.mudar_personalidade(nova_personalidade)

    def append_to_chat_log(self, speaker, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{speaker}: ")
        self.aplicar_filtros(message)
        self.chat_log.insert(tk.END, "\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def aplicar_filtros_fala(self, texto):
        texto_filtrado = texto.replace("**", "").replace("*", "").replace("$&", "").replace("&$", "")
        return texto_filtrado
    def enviar_mensagem(self, event=None):
        message = self.entry_box.get().strip()
        self.entry_box.delete(0, tk.END)
        self.append_to_chat_log("Você", message)

        if message:
            texto_com_personalidade = self.definir_personalidade(message)
            print(f"Texto com personalidade: {texto_com_personalidade}")
            resposta = self.gemini.gerar_texto(texto_com_personalidade)

            resposta_filtrada = self.aplicar_filtros_fala(resposta)

            self.append_to_chat_log("IA", resposta_filtrada)

            self.tts_engine.say(resposta_filtrada)
            self.tts_engine.runAndWait()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Janela()
    app.run()
