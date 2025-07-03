# envio_grafico_book.py
import websocket
import json
from datetime import datetime, timezone
import threading

def formatar_preco(valor): return "{:.2f}".format(float(valor))
def formatar_volume(valor): return "{:.5f}".format(float(valor))

def iniciar_grafico_book(queue):
    dados = {
        "timestamp": None,
        "kline_1m": {},
        "order_book": {"bids": [], "asks": []}
    }

    def on_kline(ws, msg):
        k = json.loads(msg)["k"]
        dados["kline_1m"] = {
            "open": formatar_preco(k["o"]),
            "high": formatar_preco(k["h"]),
            "low": formatar_preco(k["l"]),
            "close": formatar_preco(k["c"]),
            "volume": formatar_volume(k["v"]),
            "is_green": float(k["c"]) >= float(k["o"])
        }

    def on_book(ws, msg):
        b = json.loads(msg)
        bids = [[formatar_preco(i[0]), formatar_volume(i[1])] for i in b["bids"] if float(i[1]) >= 0.00001]
        asks = [[formatar_preco(i[0]), formatar_volume(i[1])] for i in b["asks"] if float(i[1]) >= 0.00001]
        dados["order_book"] = {"bids": bids, "asks": asks}
        dados["timestamp"] = datetime.now(timezone.utc).isoformat()
        queue.put({
            "tipo": "grafico_book",
            "dados": dados.copy()
        })

    threading.Thread(target=lambda: websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@kline_1m", on_message=on_kline
    ).run_forever(), daemon=True).start()

    websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@depth20", on_message=on_book).run_forever()
