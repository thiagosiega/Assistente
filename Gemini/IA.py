import google.generativeai as genai

# Configure sua chave de API
genai.configure(api_key="SEU_CHAVE_API")

# Modelo a ser utilizado
model = "gemini-1.5-flash"

# Prompt para a geração de texto
prompt = "Escreva um poema sobre a beleza da natureza."

# Chamada à API para gerar o texto
response = genai.generate_text(model=model, prompt=prompt)

# Imprimir o resultado
print(response.text)