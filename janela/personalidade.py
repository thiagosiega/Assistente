import json

# Classe que define a personalidade do chatbot
COMANDOS_DISPONIVEIS = ["janela", "olamundo"]

class Personalidade:
    def __init__(self, personalidade_atual):
        self.personalidade_atual = personalidade_atual
        self.file_persona = "Personalidades/"

    def carregar_personalidade(self):
        # Acessa o arquivo de personalidade e retorna o json referente à personalidade
        try:
            with open(self.file_persona + self.personalidade_atual + ".json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Arquivo de personalidade '{self.personalidade_atual}.json' não encontrado.")
            return None

    def mudar_personalidade(self, nova_personalidade):
        self.personalidade_atual = nova_personalidade

    def definir_personalidade(self, texto):
        # Carregar a personalidade
        personalidade = self.carregar_personalidade()

        # Se não conseguir carregar, retorna um texto padrão
        if personalidade is None:
            return "Desculpe, não consegui carregar a personalidade."

        # Extrair informações do JSON
        informacoes = "\n".join(personalidade.get("infor", []))

        # Mapear personalidades
        personalidades = {
            "objetiva": (
                f"{informacoes}\n"
                f"Comandos disponíveis: {COMANDOS_DISPONIVEIS}.\n"
                f"Com isso, responda: {texto}"
            ),
            "informativa": (
                f"{informacoes}\n"
                f"Com isso, responda: {texto}"
            ),
            "conversacional": (
                f"{informacoes}\n"
                "Você é a Yuno Gasai.\n"
                "Mantenha um tom pessoal e envolvente.\n"
                f"Com isso, responda: {texto}"
            )
        }

        # Retorna o texto ajustado com base na personalidade
        return personalidades.get(self.personalidade_atual, "Personalidade desconhecida.")
