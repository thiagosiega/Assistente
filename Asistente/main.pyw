import sys
import os
import re
import subprocess
import keyboard
import speech_recognition as sr
import pyttsx3
import time
import threading

# Adiciona o diretório ao sys.path (não o arquivo)
sys.path.append("Gemini")

from gemini_ia import IA

# Configuração do mecanismo de fala
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidade da fala
engine.setProperty('volume', 0.9)  # Volume da fala

COMANDOS_VALIDOS = ["bloco_de_notas", "calculadora", "navegador", "VScode"]
Text_informativo = (
    "Comandos disponíveis: " + ", ".join(COMANDOS_VALIDOS) + ".\n"
    "Para executar um comando, diga por exemplo: 'Abra a calculadora'.\n"
    "Para encerrar o programa, diga: 'Pare o programa'."
)

# Mapeamento de comandos de voz para o formato esperado
COMANDOS_MAPA = {
    "abra a calculadora": "$&calculadora&$",
    "abra o bloco de notas": "$&bloco_de_notas&$",
    "abra o navegador": "$&navegador&$",
    "abra o vscode": "$&VScode&$",
    "pare o programa": "$&stop&$"
}

# Instância da IA
ia = IA()

# Flag para controlar o loop principal
running = True

def falar_texto(texto):
    """Função para converter texto em fala."""
    engine.say(texto)
    engine.runAndWait()

def parar_fala():
    """Interrompe imediatamente qualquer fala em andamento."""
    engine.stop()

def capturar_audio():
    """Captura o áudio do microfone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Fale agora.")
        audio = recognizer.listen(source, phrase_time_limit=5)
    return audio

def transcrever_audio(audio):
    """Transcreve o áudio capturado para texto."""
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
    """Converte comandos de voz comuns para o formato esperado."""
    comando_formatado = COMANDOS_MAPA.get(texto.lower())
    if comando_formatado:
        print(f"Comando reconhecido: {comando_formatado}")
        return comando_formatado
    return texto

def processa_comando(mensagem):
    """Processa e executa comandos específicos no formato $&comando&$."""
    global running
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
            elif comando == "stop":
                print("Comando de parada recebido. Encerrando o programa e interrompendo o áudio.")
                parar_fala()  # Interrompe imediatamente qualquer fala
                running = False
                return True
        else:
            print(f"Comando '{comando}' não é válido.")
    return False    

def remover_formatacao(texto):
    """Remove marcações como * e ** do texto."""
    return re.sub(r'[*_]', '', texto)

# Loop principal do programa
print("Programa rodando em segundo plano. Pressione Ctrl + Shift + X para iniciar o reconhecimento de voz.")

while running:
    # Verifica se a combinação Ctrl + Shift + X está pressionada
    if keyboard.is_pressed("ctrl+shift+x"):
        print("Comando de voz ativado. Solte as teclas e fale...")
        
        # Aguarda até que as teclas sejam liberadas
        while keyboard.is_pressed("ctrl+shift+x"):
            time.sleep(0.1)
        
        # Captura o áudio
        audio = capturar_audio()
        
        # Transcreve o áudio para texto
        texto = transcrever_audio(audio)
        
        # Converte comandos de voz comuns para o formato $&comando&$
        texto_convertido = converter_comando_para_formato(texto)
        
        # Adiciona o texto informativo antes de enviar para a IA
        texto_com_informativo = Text_informativo + "\n\n" + texto_convertido
        
        # Processa comandos no texto com informativo
        if not processa_comando(texto_convertido):
            # Envia o texto combinado para a IA
            resposta = ia.gerar_texto(texto_com_informativo)
            print(resposta)  # Exibe a resposta no console

            # Remove a formatação antes de falar
            resposta_sem_formatacao = remover_formatacao(resposta)

            # Inicia a fala em uma nova thread para permitir interrupção
            thread_fala = threading.Thread(target=falar_texto, args=(resposta_sem_formatacao,))
            thread_fala.start()

            # Monitora a tecla para interrupção da fala
            while thread_fala.is_alive():
                if keyboard.is_pressed("ctrl+shift+z"):
                    parar_fala()
                    print("Fala interrompida.")
                    break

        # Pequena pausa para evitar múltiplas ativações rápidas
        time.sleep(1)

print("Programa finalizado.")
