import tkinter as tk
import re
from Gemini.gemini_ia import IA
import sys
import os
import keyboard
import speech_recognition as sr
import threading
from tkinter import messagebox

# Nao sei porque, nem como, mas o GPT diz e funciona emtao PRONTO!!! nao mexa!!!
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personalidade import Personalidade
from Voz.voz import on_shift_c_pressed


# Definindo comandos disponíveis
COMANDOS_DISPONIVEIS = ["janela", "olamundo"]

class Janela:
    def __init__(self):
        # Configuração inicial da janela principal
        self.root = tk.Tk()
        self.root.title("Janela de Bate Papo")

        # Define a personalidade padrão
        personalidade_atual = "objetiva"  # ou qualquer valor padrão desejado

        # Inicializa a personalidade padrão
        self.personalidade = Personalidade(personalidade_atual)
        self.personalidade_atual = tk.StringVar(value=personalidade_atual)

        # Cria a interface
        self.create_widgets()

        # Inicializa a IA Gemini
        self.gemini = IA()

        # Definindo estilos de tags para o Text widget
        self.chat_log.tag_config('negrito', font=('Helvetica', 12, 'bold'))
        self.chat_log.tag_config('italico', font=('Helvetica', 12, 'italic'))

        # Atualiza a personalidade ao mudar o menu
        self.personalidade_atual.trace("w", self.atualizar_personalidade)

    # Método para criar uma nova janela (comando janela)
    def janela(self):
        janela_ia = tk.Toplevel(self.root)
        janela_ia.title("Janela criada pela IA")
        janela_ia.geometry("300x300")

    # Método olamundo (comando olamundo)
    def olamundo(self):
        print("Olá Mundo")

    # Define a resposta da IA baseada na personalidade selecionada
    def definir_personalidade(self, texto):
        return self.personalidade.definir_personalidade(texto)

    # Método que aplica filtros de formatação e executa comandos
    def aplicar_filtros(self, texto):
        # Expressões regulares para formatação e comandos
        topico_negrito_pat = re.compile(r'\* \*\*(.*?)\*\*')  # * **texto**
        negrito_pat = re.compile(r'\*\*(.*?)\*\*')  # **texto**
        italico_pat = re.compile(r'\*(.*?)\*')  # *texto*
        comando_pat = re.compile(r'\$&(\w+)&\$')  # $&comando&$
        topico_pat = re.compile(r'\*(\S.*?)')  # *texto

        # Função para aplicar estilos (negrito ou itálico) no Text widget
        def aplicar_estilo(match, tag):
            self.chat_log.insert(tk.END, match.group(1), tag)

        # Inicialmente insere o texto sem formatação
        index = 0

        # Aplica o filtro de tópico em negrito (* **texto**)
        for match in topico_negrito_pat.finditer(texto):
            self.chat_log.insert(tk.END, texto[index:match.start()])
            self.chat_log.insert(tk.END, '=> ', 'italico')  # Substitui o "*"
            aplicar_estilo(match, 'negrito')
            index = match.end()

        # Aplica o filtro de negrito (**texto**)
        for match in negrito_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_estilo(match, 'negrito')
            index = match.end()

        # Aplica o filtro de itálico (*texto*)
        for match in italico_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_estilo(match, 'italico')
            index = match.end()

        # Aplica o filtro de tópico (*texto)
        for match in topico_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            self.chat_log.insert(tk.END, '=> ', 'italico')  # Substitui o "*"

        # Verifica e executa comandos ($&comando&$)
        for match in comando_pat.finditer(texto[index:]):
            comando = match.group(1)
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            index = match.end()

            # Executa o comando associado
            if comando in COMANDOS_DISPONIVEIS:
                if comando == "janela":
                    self.janela()
                elif comando == "olamundo":
                    self.olamundo()

        # Insere o restante do texto, se houver
        if index < len(texto):
            self.chat_log.insert(tk.END, texto[index:])

    def create_widgets(self):
        self.chat_log = tk.Text(self.root, state='disabled', width=50, height=20)
        self.scrollbar = tk.Scrollbar(self.root, command=self.chat_log.yview)
        self.chat_log.config(yscrollcommand=self.scrollbar.set)

        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.pack()
        self.entry_box.bind("<Return>", self.enviar_mensagem)

        self.send_button = tk.Button(self.root, text="Enviar", command=self.enviar_mensagem)
        self.send_button.pack()

        self.exit_button = tk.Button(self.root, text="Sair", command=self.root.quit)
        self.exit_button.pack()

        # Cria um menu dropdown para seleção de personalidades
        personalidades = ["objetiva", "informativa", "conversacional"]
        self.personalidade_menu = tk.OptionMenu(self.root, self.personalidade_atual, *personalidades)
        self.personalidade_menu.pack()

        # Botão de voz
        self.voice_button = tk.Button(self.root, text="Voz", command=self.on_voice_button_pressed)
        self.voice_button.pack()

        # Adiciona hotkey para Shift+C
        keyboard.add_hotkey('shift+c', self.on_shift_c_pressed)

    def on_voice_button_pressed(self):
        text = self.recognize_voice()
        if text:
            self.entry_box.delete(0, tk.END)
            self.entry_box.insert(tk.END, text)
            self.enviar_mensagem()

    def on_shift_c_pressed(self):
        text = self.recognize_voice()
        if text:
            self.entry_box.delete(0, tk.END)
            self.entry_box.insert(tk.END, text)
            self.enviar_mensagem()

    def on_voice_button_pressed(self):
        threading.Thread(target=self.recognize_voice).start()
        #cria um label para mostrar o texto reconhecido
        label = tk.Label(self.root, text="Pode falar")
        label.pack()

    def on_shift_c_pressed(self):
        threading.Thread(target=self.recognize_voice).start()
        label = tk.Label(self.root, text="Pode falar")
        label.pack()

    def recognize_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language='pt-BR')
                self.entry_box.delete(0, tk.END)
                self.entry_box.insert(tk.END, text)
                self.enviar_mensagem()
            except sr.UnknownValueError:
                messagebox.showinfo("Erro", "Não entendi o que você disse.")
            except sr.RequestError as e:
                messagebox.showinfo("Erro", "Erro ao se comunicar com o Google Speech Recognition: {0}".format(e))

    # Método que atualiza a personalidade quando a seleção no menu muda
    def atualizar_personalidade(self, *args):
        nova_personalidade = self.personalidade_atual.get()
        self.personalidade.mudar_personalidade(nova_personalidade)

    # Adiciona mensagens ao chat_log com filtro aplicado
    def append_to_chat_log(self, speaker, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{speaker}: ")
        self.aplicar_filtros(message)
        self.chat_log.insert(tk.END, "\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    # Método para enviar uma mensagem e receber a resposta da IA
    def enviar_mensagem(self, event=None):
        message = self.entry_box.get().strip()
        self.entry_box.delete(0, tk.END)
        self.append_to_chat_log("Você", message)

        # Gera o texto ajustado pela personalidade e o envia para a IA
        texto_com_personalidade = self.definir_personalidade(message)
        print(f"Texto com personalidade: {texto_com_personalidade}")
        resposta = self.gemini.gerar_texto(texto_com_personalidade)

        # Aplica filtros à resposta e executa comandos se houver
        self.append_to_chat_log("Gemini", resposta)
        self.aplicar_filtros(resposta)  # Aqui aplica filtros e executa comandos na resposta

    # Método para executar a aplicação
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Janela()
    app.run()
