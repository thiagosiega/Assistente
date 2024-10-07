import tkinter as tk
import re
import sys
import os
import pyttsx3  
import threading
import speech_recognition as sr
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from personalidade import Personalidade
from Gemini.gemini_ia import IA
from personalidade import COMANDOS_DISPONIVEIS

class Janela:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Janela de Bate Papo")

        # Inicializações
        self.personalidade_atual = tk.StringVar(value="objetiva")
        self.personalidade = Personalidade(self.personalidade_atual.get())
        self.gemini = IA()
        self.tts_engine = pyttsx3.init()
        self.voice_active = False

        # Criação dos componentes da interface
        self.create_widgets()
        
        # Configurações de estilo para o chat
        self.config_chat_styles()
        
        # Monitora mudanças na personalidade
        self.personalidade_atual.trace("w", self.atualizar_personalidade)
        
        # Bind para reconhecimento de voz
        self.root.bind('<Shift-C>', self.on_shift_c_pressed)
        self.root.bind('<KeyRelease-Shift_L>', self.on_shift_c_released)

    def create_widgets(self):
        # Área de chat
        self.chat_log = tk.Text(self.root, state='disabled', width=50, height=20)
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.root, command=self.chat_log.yview)
        self.chat_log.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Caixa de entrada e botões
        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.root, text="Enviar", command=self.enviar_mensagem).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.root, text="Sair", command=self.root.quit).pack(fill=tk.X, padx=5, pady=5)
        tk.OptionMenu(self.root, self.personalidade_atual, "objetiva", "informativa", "conversacional").pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.root, text="Voz", command=self.on_voice_button_pressed).pack(fill=tk.X, padx=5, pady=5)

    def config_chat_styles(self):
        # Estilos de fonte para o chat
        self.chat_log.tag_config('negrito', font=('Helvetica', 12, 'bold'))
        self.chat_log.tag_config('italico', font=('Helvetica', 12, 'italic'))

    def aplicar_filtros(self, texto):
        # Função para aplicar formatação ao texto do chat
        topico_negrito_pat = re.compile(r'\* \*\*(.*?)\*\*')
        negrito_pat = re.compile(r'\*\*(.*?)\*\*')
        italico_pat = re.compile(r'\*(.*?)\*')
        
        def inserir_com_tag(match, tag):
            self.chat_log.insert(tk.END, match.group(1), tag)

        # Aplica cada padrão ao texto
        index = 0
        for pat, tag in [(topico_negrito_pat, 'negrito'), (negrito_pat, 'negrito'), (italico_pat, 'italico')]:
            for match in pat.finditer(texto):
                self.chat_log.insert(tk.END, texto[index:match.start()])
                inserir_com_tag(match, tag)
                index = match.end()
        self.chat_log.insert(tk.END, texto[index:])

    def enviar_mensagem(self, event=None):
        # Processa a mensagem enviada pelo usuário
        mensagem = self.entry_box.get().strip()
        self.entry_box.delete(0, tk.END)
        self.append_to_chat_log("Você", mensagem)

        if mensagem:
            if self.processa_comando(mensagem):
                return
            
            # Gera a resposta da IA e verifica se é um comando
            resposta = self.gemini.gerar_texto(self.personalidade.definir_personalidade(mensagem))
            if self.processa_comando(resposta):
                return
            
            resposta_filtrada = self.aplicar_filtros_fala(resposta)
            print(f"Resposta filtrada: {resposta_filtrada}")
            self.append_to_chat_log("IA", resposta_filtrada)

            # Inicia uma nova thread para rodar o TTS
            threading.Thread(target=self.falar_texto, args=(resposta_filtrada,)).start()

    def processa_comando(self, mensagem):
        # Processa e executa comandos específicos no formato $&comando&$
        match = re.search(r'\$&(\w+)&\$', mensagem)
        if match:
            comando = match.group(1)
            if comando in COMANDOS_DISPONIVEIS:
                caminho_script = os.path.join("comandos", f"{comando}.py")
                if os.path.isfile(caminho_script):
                    try:
                        subprocess.Popen(["python", caminho_script])
                    except Exception as e:
                        self.append_to_chat_log("IA", f"Erro ao executar o comando '{comando}': {str(e)}")
                    return True
                else:
                    self.append_to_chat_log("IA", f"O script para '{comando}' não foi encontrado.")
            else:
                self.append_to_chat_log("IA", f"Comando '{comando}' não encontrado.")
        return False

    def on_voice_button_pressed(self):
        threading.Thread(target=self.start_voice_recognition).start()

    def on_shift_c_pressed(self, event=None):
        if not self.voice_active:
            self.voice_active = True
            threading.Thread(target=self.start_voice_recognition).start()

    def on_shift_c_released(self, event=None):
        self.voice_active = False

    def start_voice_recognition(self):
        # Inicia o reconhecimento de voz em um loop enquanto 'voice_active' for True
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Aguarde um momento... Fale agora.")
            while self.voice_active:
                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    texto = recognizer.recognize_google(audio, language='pt-BR')
                    print(f"Você disse: {texto}")
                    self.entry_box.delete(0, tk.END)
                    self.entry_box.insert(tk.END, texto)
                    self.enviar_mensagem()
                except (sr.UnknownValueError, sr.RequestError):
                    pass
    def falar_texto(self, texto):
        # Função isolada para rodar o TTS em uma thread separada
        self.tts_engine.say(texto)
        self.tts_engine.runAndWait()

    def atualizar_personalidade(self, *args):
        self.personalidade.mudar_personalidade(self.personalidade_atual.get())

    def append_to_chat_log(self, speaker, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{speaker}: ")
        self.aplicar_filtros(message)
        self.chat_log.insert(tk.END, "\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def aplicar_filtros_fala(self, texto):
        return texto.replace("**", "").replace("*", "").replace("$&", "").replace("&$", "")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Janela()
    app.run()
