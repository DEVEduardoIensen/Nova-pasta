import time

# Caminho do arquivo de log
arquivo_log = "log_envio_gpt.json"

def limpar_log():
    while True:
        try:
            with open(arquivo_log, "w") as f:
                f.write("")  # apaga tudo
            
        except Exception as e:
            print("❌ Erro ao limpar o log:", e)
        
        time.sleep(5)  # espera 5 segundos e limpa de novo

if __name__ == "__main__":

    limpar_log()
