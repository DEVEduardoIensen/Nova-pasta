import requests
import time
import winsound
import threading

def beep_infinito(parar_evento):
    while not parar_evento.is_set():
        winsound.Beep(1000, 500)  # beep 0.5s
        time.sleep(0.2)  # pausa pequena pra não travar a CPU

def get_ip():
    try:
        return requests.get("https://api.ipify.org").text.strip()
    except:
        return None

ip_atual = get_ip()
print(f"[INÍCIO] IP atual: {ip_atual}")

parar_beep = threading.Event()
thread_beep = None

while True:
    time.sleep(1)
    novo_ip = get_ip()
    if novo_ip is None:
        print("[ERRO] Não foi possível obter o IP")
        continue
    
    if novo_ip != ip_atual:
        print(f"[ALERTA] IP MUDOU: {ip_atual} → {novo_ip}")
        ip_atual = novo_ip
        
        # Se já estiver tocando beep, não inicia outro
        if thread_beep is None or not thread_beep.is_alive():
            parar_beep.clear()
            thread_beep = threading.Thread(target=beep_infinito, args=(parar_beep,))
            thread_beep.start()

        print("Pressione ENTER para parar o alarme e continuar...")
        input()
        parar_beep.set()
        thread_beep.join()
        print("Alarme parado. Monitorando IP...")
    
    else:
        print(f"[OK] IP ainda é: {ip_atual}")
