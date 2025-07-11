import threading
import time
import json
from datetime import datetime, timezone
from queue import Queue
import requests
import winsound
import os
import openai
from utils_memory import exportar_memoria_texto
from utils_memoria_curta import carregar_memoria_curta, salvar_memoria_curta, apagar_da_memoria_curta

# ======== GPT CONFIG - API OFICIAL OPENAI ========
openai.api_key = os.getenv("OPENAI_API_KEY")
modelo = "gpt-4.1-mini-2025-04-14"

# ======== CACHE DAS MEMÓRIAS (2 MINUTOS) ========
memoria_cache = ""
memoria_curta_cache = ""
ultima_atualizacao = 0

def atualizar_memorias():
    global memoria_cache, memoria_curta_cache, ultima_atualizacao
    agora = time.time()
    if agora - ultima_atualizacao >= 120:
        memoria_cache = exportar_memoria_texto()
        memoria_curta = carregar_memoria_curta()
        memoria_curta_cache = json.dumps(memoria_curta, indent=2, ensure_ascii=False)
        ultima_atualizacao = agora

# ======== LIMPEZA DE LOG GPT ========
def limpar_log_periodicamente(intervalo=50):
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
def enviar_para_gpt(tipo, dados, incluir_memorias=True):
    try:
        mensagens = []

        if incluir_memorias:
            atualizar_memorias()
            prompt = {
                "role": "system",
                "content": (
                    "Abaixo estão instruções e informações fixas do operador humano (memory_gpt.json):\n\n"
                    f"{memoria_cache}\n\n"
                    "Abaixo está a memória temporária atual (memoria_curta_gpt.json), enviada como JSON real:\n\n"
                    f"{memoria_curta_cache}\n\n"
                    "Use essas informações para decidir se deve salvar novos dados ou apagar dados antigos da memória curta. Responda sempre com {'salvar': {...}} ou {'apagar': [...]} quando salvar use: operaçao: quantidade de usdt: e status da operaçao:, nada alem disso."
                    "  atualize a memoria curta com sua propria vontade, e sempre lembre o que a memoria fixa te falou, por que ela só é enviada 1 vez a cada dois minutos."
                )
            }
            mensagens.append(prompt)

        mensagens.append({"role": "user", "content": json.dumps(dados)})

        response = openai.chat.completions.create(
            model=modelo,
            messages=mensagens,
            temperature=0.2
        )

        resposta_gpt = response.choices[0].message.content
        print(f"🧠 GPT ({tipo.upper()}): {resposta_gpt.encode('utf-8', errors='replace').decode('utf-8')}")

        try:
            resposta_json = json.loads(resposta_gpt)
            if "salvar" in resposta_json:
                salvar_memoria_curta(resposta_json["salvar"])
                print("💾 GPT salvou na memória curta:", resposta_json["salvar"])
            if "apagar" in resposta_json:
                apagar_da_memoria_curta(resposta_json["apagar"])
                print("🗑️ GPT apagou da memória curta:", resposta_json["apagar"])
        except:
            pass

        with open("log_envio_gpt.json", "a", encoding="utf-8") as f:
            json.dump({
                "tipo": tipo,
                "dados": dados,
                "timestamp_envio": datetime.now(timezone.utc).isoformat()
            }, f, indent=2, ensure_ascii=False)
            f.write("\n\n")

    except Exception as e:
        print("❌ Erro ao enviar para o GPT:", e)

# ✅ ENVIO EXCLUSIVO DA MEMÓRIA FIXA A CADA 2 MIN
def loop_envio_memorias():
    while True:
        atualizar_memorias()
        dados_memorias = {
            "tipo": "memorias",
            "memory_fixa": memoria_cache,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        enviar_para_gpt("memorias", dados_memorias, incluir_memorias=False)
        time.sleep(120)

# ======== MONITOR DE FILAS =========
def monitorar_filas():
    while True:
        if modo_pausa:
            time.sleep(1)
            continue

        if not queue_fluxo.empty():
            pacote = queue_fluxo.get()
            dados = pacote["dados"].copy()
            dados["memoria_curta"] = json.loads(memoria_curta_cache)
            enviar_para_gpt(pacote["tipo"], dados, incluir_memorias=False)

        if not queue_book.empty():
            pacote = queue_book.get()
            dados = pacote["dados"].copy()
            dados["memoria_curta"] = json.loads(memoria_curta_cache)
            enviar_para_gpt(pacote["tipo"], dados, incluir_memorias=False)

        time.sleep(0.01)

# ======== INÍCIO =========
if __name__ == "__main__":
    print("🧠 NeuroScalp MAIN rodando (API OpenAI, com memória ativa)...\n")

    threading.Thread(target=iniciar_fluxo, args=(queue_fluxo,), daemon=True).start()
    threading.Thread(target=iniciar_grafico_book, args=(queue_book,), daemon=True).start()
    threading.Thread(target=monitorar_ip, daemon=True).start()
    threading.Thread(target=monitorar_filas, daemon=True).start()
    threading.Thread(target=limpar_log_periodicamente, daemon=True).start()
    threading.Thread(target=loop_envio_memorias, daemon=True).start()

    while True:
        time.sleep(1)