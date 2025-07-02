# main.py
import threading
import time
import json
from datetime import datetime, timezone
from queue import Queue
import requests
import winsound
import os
from openai import OpenAI

# ======== GPT CONFIG ========
token = os.environ["GITHUB_TOKEN"]
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=token,
)


# ======== LIMPEZA DE LOG GPT ========
def limpar_log_periodicamente(intervalo=5):
    while True:
        try:
            with open("log_envio_gpt.json", "w") as f:
                f.write("")
        except Exception as e:
            print(f"❌ Erro ao limpar o log: {e}")
        time.sleep(intervalo)






# ======== IMPORTANDO OS MÓDULOS =========
from envio_fluxo import iniciar_fluxo
from envio_grafico_book import iniciar_grafico_book

# ======== FILAS =========
queue_fluxo = Queue()
queue_book = Queue()

modo_pausa = False
ip_atual = None

# ======== IP =========
def get_ip():
    try:
        return requests.get("https://api.ipify.org").text.strip()
    except:
        return None

def beep_infinito(parar_evento):
    while not parar_evento.is_set():
        winsound.Beep(1000, 500)
        time.sleep(0.2)

def monitorar_ip():
    global ip_atual, modo_pausa
    parar_beep = threading.Event()
    thread_beep = None

    while True:
        time.sleep(1)
        novo_ip = get_ip()
        if novo_ip is None:
            continue
        if ip_atual is None:
            ip_atual = novo_ip
            print(f"[IP] Inicial: {ip_atual}")
            continue
        if novo_ip != ip_atual:
            print(f"\n[⚠️ IP ALTERADO] {ip_atual} → {novo_ip}")
            ip_atual = novo_ip
            modo_pausa = True
            if thread_beep is None or not thread_beep.is_alive():
                parar_beep.clear()
                thread_beep = threading.Thread(target=beep_infinito, args=(parar_beep,))
                thread_beep.start()
            print("Pressione ENTER para retomar...")
            input()
            parar_beep.set()
            thread_beep.join()
            modo_pausa = False
            print("✔️ Retomando operação...\n")

# ======== GPT ENVIO =========
def enviar_para_gpt(tipo, dados):
    try:
        prompt = {
            "role": "system",
            "content": "Você está recebendo dados do BTC/USDT em tempo real. Confirme o  recebimento está correto do fluxo de ordens."
        }

        response = client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[prompt, {"role": "user", "content": json.dumps(dados)}],
            temperature=0.2
        )

        print(f"🧠 GPT ({tipo.upper()}):", response.choices[0].message.content)

        with open("log_envio_gpt.json", "a") as f:
            f.write(json.dumps({
                "tipo": tipo,
                "dados": dados,
                "timestamp_envio": datetime.now(timezone.utc).isoformat()
            }, indent=2) + "\n\n")

    except Exception as e:
        print("❌ Erro ao enviar para o GPT:", e)

# ======== MONITOR DE FILAS =========
def monitorar_filas():
    while True:
        if modo_pausa:
            time.sleep(1)
            continue

        if not queue_fluxo.empty():
            pacote = queue_fluxo.get()
            print("📦 FLUXO ENTREGUE AO MAIN:", pacote["dados"]["fluxo_ordens"][-1])  # DEBUG 👈
            enviar_para_gpt(pacote["tipo"], pacote["dados"])

        if not queue_book.empty():
            pacote = queue_book.get()
            print("📘 BOOK ENTREGUE AO MAIN")  # DEBUG 👈
            enviar_para_gpt(pacote["tipo"], pacote["dados"])

        time.sleep(0.01)

# ======== INÍCIO =========
if __name__ == "__main__":
    print("🧠 NeuroScalp MAIN rodando (modular, com debug)...\n")

    threading.Thread(target=iniciar_fluxo, args=(queue_fluxo,), daemon=True).start()
    threading.Thread(target=iniciar_grafico_book, args=(queue_book,), daemon=True).start()
    threading.Thread(target=monitorar_ip, daemon=True).start()
    threading.Thread(target=monitorar_filas, daemon=True).start()
    threading.Thread(target=limpar_log_periodicamente, daemon=True).start()


    while True:
        time.sleep(1)
