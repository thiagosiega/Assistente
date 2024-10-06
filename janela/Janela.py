import tkinter as tk
import re
from Gemini.gemini_ia import IA
import sys
import os
import keyboard
import pyttsx3  
import speech_recognition as sr

# Não sei porque, nem como, mas o GPT diz e funciona então PRONTO!!! não mexa!!!
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

        # Inicializa o mecanismo de texto para fala
        self.tts_engine = pyttsx3.init()

        # Definindo estilos de tags para o Text widget
        self.chat_log.tag_config('negrito', font=('Helvetica', 12, 'bold'))
        self.chat_log.tag_config('italico', font=('Helvetica', 12, 'italic'))

        # Atualiza a personalidade ao mudar o menu
        self.personalidade_atual.trace("w", self.atualizar_personalidade)

    # Método para criar uma nova janela (comando janela)
    def janela(self):
        janela_ia = tk.Toplevel(self.root)
        janela_ia.title("Janela criada pela IA")
        janela_ia.geometry("500x600")

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

        # Ajuste os widgets de chat e scrollbar
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.pack(fill=tk.X, padx=5, pady=5)  # Ajusta a largura da Entry

        self.send_button = tk.Button(self.root, text="Enviar", command=self.enviar_mensagem)
        self.send_button.pack(fill=tk.X, padx=5, pady=5)  # Ajusta a largura do botão de enviar

        self.exit_button = tk.Button(self.root, text="Sair", command=self.root.quit)
        self.exit_button.pack(fill=tk.X, padx=5, pady=5)  # Ajusta a largura do botão de sair

        # Cria um menu dropdown para seleção de personalidades
        personalidades = ["objetiva", "informativa", "conversacional"]
        self.personalidade_menu = tk.OptionMenu(self.root, self.personalidade_atual, *personalidades)
        self.personalidade_menu.pack(fill=tk.X, padx=5, pady=5)  # Ajusta a largura do menu de personalidades

        # Botão de voz
        self.voice_button = tk.Button(self.root, text="Voz", command=self.on_voice_button_pressed)
        self.voice_button.pack(fill=tk.X, padx=5, pady=5)  # Ajusta a largura do botão de voz

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

    def recognize_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Aguarde um momento... Fale agora.")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {text}")
                return text
            except sr.UnknownValueError:
                print("Não foi possível entender o áudio.")
                return None
            except sr.RequestError as e:
                print(f"Erro ao solicitar resultados do serviço de reconhecimento de fala; {e}")
                return None
    def aplicar_filtros_fala(self, texto):
        texto_processado = texto.replace("**", "").replace("*", "").replace("$&", "").replace("&$", "")
        # Aqui você pode adicionar mais regras de formatação se necessário
        return texto_processado

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

        if message:
            texto_com_personalidade = self.definir_personalidade(message)
            print(f"Texto com personalidade: {texto_com_personalidade}")
            resposta = self.gemini.gerar_texto(texto_com_personalidade)  # Gera a resposta da IA

            # Aplica filtros à resposta
            resposta_filtrada = self.aplicar_filtros_fala(resposta)

            self.append_to_chat_log("IA", resposta_filtrada)

            # Converte a resposta filtrada em fala
            self.tts_engine.say(resposta_filtrada)
            self.tts_engine.runAndWait()


    # Inicia a aplicação
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Janela()
    app.run()
