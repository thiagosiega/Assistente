import tkinter as tk
from Gemini.gemini_ia import IA

class Janela:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Janela de Bate Papo")
        self.create_widgets()
        self.gemini = IA()

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

    def append_to_chat_log(self, speaker, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"{speaker}: {message}\n")
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
