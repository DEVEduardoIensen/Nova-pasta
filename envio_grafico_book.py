import websocket
import threading
import json
import time
from datetime import datetime, timezone

# ========== CONFIG ==========
ms_envio = 1000  # Envio a cada 1 segundo (pode ajustar depois)
volume_minimo_btc = 0.00001  # Filtro mínimo de volume no book

# ========== DADOS ==========
dados_grafico_book = {
    "timestamp": None,
    "kline_1m": {},
    "order_book": {"bids": [], "asks": []}
}

# ========== COLETORES ==========
def coletor_kline():
    def on_message(ws, msg):
        global dados_grafico_book
        k = json.loads(msg)["k"]

        dados_grafico_book["kline_1m"] = {
            "open": k["o"],
            "high": k["h"],
            "low": k["l"],
            "close": k["c"],
            "volume": k["v"],
            "is_green": float(k["c"]) >= float(k["o"])
        }
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@kline_1m", on_message=on_message)
    ws.run_forever()

def coletor_book():
    def on_message(ws, msg):
        global dados_grafico_book
        b = json.loads(msg)
        bids_filtrados = [i for i in b["bids"] if float(i[1]) >= volume_minimo_btc]
        asks_filtrados = [i for i in b["asks"] if float(i[1]) >= volume_minimo_btc]

        dados_grafico_book["order_book"] = {
            "bids": bids_filtrados,
            "asks": asks_filtrados
        }
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@depth20", on_message=on_message)
    ws.run_forever()

# ========== LOOP DE LOG ==========
def salvar_em_log_envio_gpt():
    while True:
        try:
            with open("log_envio_gpt.json", "a") as f:
                f.write(json.dumps({
                    "tipo": "grafico_book",
                    "dados": dados_grafico_book,
                    "timestamp_envio": datetime.now(timezone.utc).isoformat()
                }, indent=2) + "\n\n")
        except Exception as e:
            print("❌ Erro ao salvar log:", e)

        time.sleep(ms_envio / 1000)

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    print("📡 Coletando gráfico (kline) + book e salvando no log_envio_gpt.json...")
    threading.Thread(target=coletor_kline, daemon=True).start()
    threading.Thread(target=coletor_book, daemon=True).start()
    threading.Thread(target=salvar_em_log_envio_gpt, daemon=True).start()

    while True:
        time.sleep(1)
