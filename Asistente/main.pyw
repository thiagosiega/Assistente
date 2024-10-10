import sys
import os
import re
import subprocess
import keyboard
import speech_recognition as sr
import pyttsx3
import time

# Adiciona o diretório ao sys.path (não o arquivo)
sys.path.append("Gemini")

from gemini_ia import IA

# Configuração do mecanismo de fala
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidade da fala
engine.setProperty('volume', 0.9)  # Volume da fala

COMANDOS_VALIDOS = ["bloco_de_notas", "calculadora", "navegador", "VScode"]
Text_informativo = "Comandos disponíveis: " + str(COMANDOS_VALIDOS) + ".\nPara executar um comando, diga por exemplo: 'Abra a calculadora'."

# Mapeamento de comandos de voz para o formato esperado
COMANDOS_MAPA = {
    "abra a calculadora": "$&calculadora&$",
    "abra o bloco de notas": "$&bloco_de_notas&$",
    "abra o navegador": "$&navegador&$",
    "abra o vscode": "$&VScode&$"
}

# Instância da IA
ia = IA()

def falar_texto(texto):
    #remove os "*" do texto
    texto = texto.replace("*", "")
    # Função para falar o texto
    engine.say(texto)
    engine.runAndWait()

def capturar_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Fale agora.")
        audio = recognizer.listen(source, phrase_time_limit=5)
    return audio

def transcrever_audio(audio):
    recognizer = sr.Recognizer()
    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        print("Texto transcrito:", texto)
        return texto
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio.")
    except sr.RequestError:
        print("Erro ao se comunicar com o serviço de reconhecimento.")
    return ""

def converter_comando_para_formato(texto):
    comando_formatado = COMANDOS_MAPA.get(texto.lower())
    if comando_formatado:
        print(f"Comando reconhecido: {comando_formatado}")
        return comando_formatado
    return texto

def processa_comando(mensagem):
    match = re.search(r'\$&(\w+)&\$', mensagem)
    if match:
        comando = match.group(1)
        if comando in COMANDOS_VALIDOS:
            caminho_script = os.path.join("comandos", f"{comando}.py")
            print(f"Tentando executar: {caminho_script}")
            if os.path.isfile(caminho_script):
                try:
                    subprocess.Popen(["python", caminho_script])
                    print(f"Abrindo {comando}...")
                except Exception as e:
                    print(f"Erro ao executar o comando '{comando}': {str(e)}")
                return True
            else:
                print(f"O script para '{comando}' não foi encontrado no caminho: {caminho_script}")
        else:
            print(f"Comando '{comando}' não é válido.")
    return False    

# Loop principal do programa
print("Programa rodando em segundo plano. Pressione Ctrl + Shift + C para iniciar o reconhecimento de voz.")
while True:
    keyboard.wait("ctrl+shift+c")
    print("Comando de voz ativado. Solte as teclas e fale...")
    keyboard.wait("ctrl+shift+c", suppress=True, trigger_on_release=True)
    
    audio = capturar_audio()
    texto = transcrever_audio(audio)
    
    texto_convertido = converter_comando_para_formato(texto)
    texto_com_informativo = Text_informativo + "\n\n" + texto_convertido
    
    # Se não for um comando, envie para IA e fale o texto sem aplicar filtros
    if not processa_comando(texto_convertido):
        resposta = ia.gerar_texto(texto_com_informativo)
        print(resposta)  # Exibe a resposta com formatação no console
        falar_texto(resposta)  # Fala a resposta sem aplicar filtros
    
    time.sleep(1)
