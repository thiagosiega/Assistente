import subprocess

def requisitos():
    # Caminho do arquivo com a lista de bibliotecas e versões
    arquivo_requisitos = "bibliotecas.txt"

    # Executa o comando para instalar todas as bibliotecas e versões do arquivo
    subprocess.run(["pip", "install", "-r", arquivo_requisitos])


if __name__ == "__main__":
    requisitos()
    from janela.Janela import Janela
    app = Janela()
    app.run()