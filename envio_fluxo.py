# envio_fluxo.py
import websocket
import json
from datetime import datetime, timezone

def formatar_preco(valor): return "{:.2f}".format(float(valor))
def formatar_volume(valor): return "{:.5f}".format(float(valor))

def iniciar_fluxo(queue):
    dados_fluxo = {
        "timestamp": None,
        "preco_atual": None,
        "fluxo_ordens": []
    }

    def on_message(ws, msg):
        trade = json.loads(msg)
        dados_fluxo["timestamp"] = datetime.now(timezone.utc).isoformat()
        dados_fluxo["preco_atual"] = formatar_preco(trade["p"])

        nova_ordem = {
            "tipo": "buy" if not trade["m"] else "sell",
            "preco": formatar_preco(trade["p"]),
            "quantidade": formatar_volume(trade["q"])
        }

        dados_fluxo["fluxo_ordens"].append(nova_ordem)

        # ENVIA PRA FILA:
        queue.put({
            "tipo": "fluxo",
            "dados": dados_fluxo.copy()
        })

    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@trade", on_message=on_message)
    ws.run_forever()