import websocket
import threading
import json
import time
from datetime import datetime, timezone

# ========== CONFIG ==========
ms_fluxo = 5  # frequência de envio (ms)

# ========== FORMATADORES ==========
def formatar_preco(valor):
    return "{:.2f}".format(float(valor))

def formatar_volume(valor):
    return "{:.5f}".format(float(valor))

# ========== DADOS ==========
dados_fluxo = {
    "timestamp": None,
    "preco_atual": None,
    "fluxo_ordens": []
}

# ========== COLETOR DE FLUXO ==========
def coletor_fluxo():
    def on_message(ws, msg):
        global dados_fluxo
        trade = json.loads(msg)

        dados_fluxo["timestamp"] = datetime.now(timezone.utc).isoformat()
        dados_fluxo["preco_atual"] = formatar_preco(trade["p"])

        nova_ordem = {
            "tipo": "buy" if not trade["m"] else "sell",
            "preco": formatar_preco(trade["p"]),
            "quantidade": formatar_volume(trade["q"])
        }

        dados_fluxo["fluxo_ordens"].append(nova_ordem)

        # ❌ REMOVIDO: limite_ordens = X (agora é produção total)

    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@trade", on_message=on_message)
    ws.run_forever()

# ========== LOOP DE ENVIO ==========
def salvar_em_log_envio_gpt():
    while True:
        try:
            with open("log_envio_gpt.json", "a") as f:
                f.write(json.dumps({
                    "tipo": "fluxo",
                    "dados": dados_fluxo,
                    "timestamp_envio": datetime.now(timezone.utc).isoformat()
                }, indent=2) + "\n\n")
        except Exception as e:
            print("❌ Erro ao salvar no log:", e)

        time.sleep(ms_fluxo / 1000)

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    print("📡 Coletando fluxo (modo produção) e salvando no log_envio_gpt.json...")
    threading.Thread(target=coletor_fluxo, daemon=True).start()
    threading.Thread(target=salvar_em_log_envio_gpt, daemon=True).start()

    while True:
        time.sleep(1)
