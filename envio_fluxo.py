# envio_fluxo.py
import websocket
import json
import threading
import time
from datetime import datetime, timezone
from queue import Queue

def formatar_preco(valor):
    return "{:.2f}".format(float(valor))

def formatar_volume(valor):
    return "{:.5f}".format(float(valor))

def iniciar_fluxo(queue):
    buffer_ordens = []
    lock = threading.Lock()

    def enviar_fluxo_periodicamente():
        while True:
            time.sleep(1)  # envia a cada 1 segundo
            with lock:
                if buffer_ordens:
                    preco_atual = buffer_ordens[-1]["preco"]
                    dados_fluxo = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "preco_atual": preco_atual,
                        "fluxo_ordens": buffer_ordens.copy()
                    }

                    queue.put({
                        "tipo": "fluxo",
                        "dados": dados_fluxo
                    })

                    buffer_ordens.clear()

    def on_message(ws, msg):
        trade = json.loads(msg)
        nova_ordem = {
            "tipo": "buy" if not trade["m"] else "sell",
            "preco": formatar_preco(trade["p"]),
            "quantidade": formatar_volume(trade["q"])
        }

        with lock:
            buffer_ordens.append(nova_ordem)

    # Inicia thread de envio periódico
    threading.Thread(target=enviar_fluxo_periodicamente, daemon=True).start()

    # Conecta ao WebSocket da Binance
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_message=on_message
    )
    ws.run_forever()