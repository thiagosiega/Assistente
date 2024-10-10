import os
import google.generativeai as genai


class IA:
    def __init__(self):
        self.model = "gemini-1.5-flash"

    def chave_key(self):
        FILE = 'Key.txt'
        if os.path.exists(FILE):
            with open(FILE, 'r') as file:
                return file.read().strip()
        else:
            raise FileNotFoundError('Arquivo Key.txt não encontrado')

    def gerar_texto(self, prompt):
        genai.configure(api_key=self.chave_key())
        model = genai.GenerativeModel(self.model)
        
        try:
            response = model.generate_content(prompt)

            if response and hasattr(response, 'candidates'):
                candidates = response.candidates
                if candidates and hasattr(candidates[0], 'content'):
                    parts = candidates[0].content.parts
                    if parts:
                        return parts[0].text
        except Exception as e:
            print(f"Erro ao gerar texto: {e}")
            return "Ocorreu um erro ao gerar a resposta."
        
        return "Não foi possível gerar uma resposta."

