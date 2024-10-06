import tkinter as tk
import re
from Gemini.gemini_ia import IA

comandos_disponiveis = ["janela", "olamundo"]

class Janela:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Janela de Bate Papo")
        # Inicializa personalidade padrão
        self.personalidade_atual = tk.StringVar(self.root)
        self.personalidade_atual.set("objetiva")  # Valor padrão inicial
        self.create_widgets()
        self.gemini = IA()
        # Definindo as tags de estilo para o widget Text
        self.chat_log.tag_config('negrito', font=('Helvetica', 12, 'bold'))
        self.chat_log.tag_config('italico', font=('Helvetica', 12, 'italic'))
        
        # Inicializa personalidade padrão
        self.personalidade_atual = tk.StringVar(self.root)
        self.personalidade_atual.set("objetiva")  # Valor padrão inicial

    def janela(self):
        janela_ia = tk.Tk()
        janela_ia.title("Janela criada pela IA")
        janela_ia.geometry("300x300")
        janela_ia.mainloop()

    def olamundo(self):
        print("Olá Mundo")

    def definir_personalidade(self, texto):
        personalidades = {
            "objetiva": [
                "Seja direto e objetivo.",
                "Respostas curtas e diretas.",
                "Voce tem comandos disponíveis, todos seguem o padrão antes e depois posuem '$&'\nExemplo:'$&janela$&'.",
                "Todos os comando sao executados na maquina do user.",
                f"Comandos disponíveis: {comandos_disponiveis}",
                f"Com isso responda: {texto}"
            ],
            "informativa": [
                "Busque o maximo de informaçoes disponiveis independente da fonte.",
                "O obijetivo é sempre buscar mais informaçoes.",
                "Qual quer resultado vago nao e aceitavel.",
                f"Com isso responda: {texto}"
            ],
            "conversacional": [
                "Você é a Yuno Gasai.",
                "Aja como se estivesse conversando com o seu amado.",
                "Sempre mantenha a conversa ativa.",
                f"Com isso responda: {texto}"
            ]
        }
        return personalidades[self.personalidade_atual.get()]

    def filtros(self, texto):
        # Expressão regular para identificar o padrão "* **" que vira "=> **negrito**"
        topico_negrito_pat = re.compile(r'\* \*\*(.*?)\*\*')  # Identifica * **texto**
        # Expressão regular para identificar negrito **texto**
        negrito_pat = re.compile(r'\*\*(.*?)\*\*')
        # Expressão regular para identificar itálico *texto*
        italico_pat = re.compile(r'\*(.*?)\*')
        # Comandos a serem executados
        comando_pat = re.compile(r'\$&(\w+)&\$')  

        # Função para aplicar o estilo negrito ou itálico no widget Text
        def aplicar_filtro(match, tag):
            self.chat_log.insert(tk.END, match.group(1), tag)

        # Inicialmente, insere o texto sem formatação
        index = 0

        # Verifica o padrão "* **" (tópico com negrito)
        for match in topico_negrito_pat.finditer(texto):
            self.chat_log.insert(tk.END, texto[index:match.start()])  # Insere texto antes do padrão
            self.chat_log.insert(tk.END, '=> ', 'italico')  # Seta no lugar do primeiro "*"
            aplicar_filtro(match, 'negrito')  # Aplica o negrito no texto entre "**"
            index = match.end()

        # Aplica o padrão de negrito **texto**
        for match in negrito_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_filtro(match, 'negrito')
            index = match.end()

        # Aplica o padrão de itálico *texto*
        for match in italico_pat.finditer(texto[index:]):
            self.chat_log.insert(tk.END, texto[index:match.start() + index])
            aplicar_filtro(match, 'italico')
            index = match.end()

        # Verifica se há comandos a serem executados
        for match in comando_pat.finditer(texto[index:]):
            comando = match.group(1)
            if comando in comandos_disponiveis:
                self.chat_log.insert(tk.END, texto[index:match.start() + index])
                index = match.end()
                # Executa o comando associado
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
        self.entry_box.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack()

        # Cria um menu dropdown para seleção de personalidades
        personalidades = ["objetiva", "informativa", "conversacional"]
        self.personalidade_menu = tk.OptionMenu(self.root, self.personalidade_atual, *personalidades)
        self.personalidade_menu.pack()

    def append_to_chat_log(self, speaker, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{speaker}: ")
        self.filtros(message)  # Aplica os filtros de formatação
        self.chat_log.insert(tk.END, "\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def send_message(self, event=None):
        message = self.entry_box.get().strip()
        self.entry_box.delete(0, tk.END)
        self.append_to_chat_log("Você", message)
        response = self.gemini.gerar_texto(message)
        self.append_to_chat_log("Gemini", response)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Janela()
    app.run()
