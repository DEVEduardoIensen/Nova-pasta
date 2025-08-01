import websocket
import json
import threading
import time
from datetime import datetime, timezone
from queue import Queue
from collections import defaultdict

def formatar_preco(valor): return "{:.2f}".format(float(valor))
def formatar_volume(valor): return "{:.5f}".format(float(valor))

def iniciar_fluxo(queue):
    buffer = []
    lock = threading.Lock()

    def processar_buffer():
        while True:
            time.sleep(0.05)  # Aguarda 50ms
            with lock:
                if not buffer:
                    continue

                # Cria JSON agrupado
                dados_fluxo = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "preco_atual": None,
                    "fluxo_ordens": []
                }

                agrupadas = defaultdict(float)
                normais = []

                for trade in buffer:
                    preco = formatar_preco(trade["p"])
                    quantidade = float(trade["q"])
                    tipo = "buy" if not trade["m"] else "sell"
                    dados_fluxo["preco_atual"] = preco

                    if abs(quantidade - 0.00005) < 1e-8:
                        agrupadas[(tipo, preco)] += quantidade
                    else:
                        normais.append({
                            "tipo": tipo,
                            "preco": preco,
                            "quantidade": formatar_volume(quantidade)
                        })

                dados_fluxo["fluxo_ordens"].extend(normais)

                for (tipo, preco), soma in agrupadas.items():
                    dados_fluxo["fluxo_ordens"].append({
                        "tipo": tipo,
                        "preco": preco,
                        "quantidade": formatar_volume(soma),
                        "agrupada": True
                    })

                buffer.clear()
                queue.put({
                    "tipo": "fluxo",
                    "dados": dados_fluxo
                })

    def on_message(ws, msg):
        trade = json.loads(msg)
        with lock:
            buffer.append(trade)

    # Start da thread que processa o buffer
    threading.Thread(target=processar_buffer, daemon=True).start()

    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_message=on_message
    )
    ws.run_forever()
