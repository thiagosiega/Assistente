import psutil

def encerrar_processos_python():
    for processo in psutil.process_iter(['pid', 'name']):
        if 'python' in processo.info['name']:
            try:
                processo_terminado = psutil.Process(processo.info['pid'])
                processo_terminado.terminate()  # Encerra o processo
                processo_terminado.wait(timeout=3)  # Aguarda até que o processo seja encerrado
                print(f"Processo Python com PID {processo.info['pid']} encerrado.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                print(f"Não foi possível encerrar o processo com PID {processo.info['pid']}.")

encerrar_processos_python()
