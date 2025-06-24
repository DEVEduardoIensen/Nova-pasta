import websocket
import threading
import json
import time
from datetime import datetime, timezone
from openai import OpenAI
import os
from dotenv import load_dotenv

# Setup OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Dados em tempo real
dados = {
    "timestamp": None,
    "preco_atual": None,
    "kline_1m": {},
    "order_book": {"bids": [], "asks": []},
    "fluxo_ordens": []
}

# Prompt do GPT
prompt_sistema = {
    "role": "system",
    "content": """Está recebendo dados em tempo real do BTC/USDT:

- Fluxo de ordens (agregadas)
- Livro de ofertas (book)
- Candle de 1 minuto (kline)

Apenas diga se está recebendo todos corretamente. nao esqueca de responder do grafico de falar se esta recebendo ele tambem
eu tenho que lapidar o codigo 
 voce pode me dizer o que voce esta recebendo e como esta recebendo"""
}

# WebSocket - fluxo de ordens
def on_trade(ws, message):
    try:
        trade = json.loads(message)
        dados["timestamp"] = datetime.now(timezone.utc).isoformat()
        dados["preco_atual"] = trade["p"]
        novo_trade = {
            "tipo": "buy" if not trade["m"] else "sell",
            "preco": trade["p"],
            "quantidade": trade["q"]
        }
        dados["fluxo_ordens"].append(novo_trade)
        if len(dados["fluxo_ordens"]) > 10:
            dados["fluxo_ordens"] = dados["fluxo_ordens"][-10:]
    except Exception as e:
        print("Erro trade:", e)

# WebSocket - candle 1 minuto
def on_kline(ws, message):
    try:
        k = json.loads(message)["k"]
        dados["kline_1m"] = {
            "open": k["o"],
            "high": k["h"],
            "low": k["l"],
            "close": k["c"],
            "volume": k["v"],
            "is_green": float(k["c"]) >= float(k["o"])
        }
    except Exception as e:
        print("Erro kline:", e)

# WebSocket - order book
def on_book(ws, message):
    try:
        b = json.loads(message)
        dados["order_book"] = {
            "bids": b["bids"][:3],
            "asks": b["asks"][:3]
        }
    except Exception as e:
        print("Erro book:", e)

# Envia dados para o GPT
def loop_envio_gpt():
    while True:
        try:
            time.sleep(3)
            mensagens = [
                prompt_sistema,
                {"role": "user", "content": json.dumps(dados)}
            ]
            resposta = client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=mensagens,
                temperature=0.2
            )
            print("\n🧠 [GPT]:", resposta.choices[0].message.content)
        except Exception as e:
            print("Erro GPT:", e)

# Inicializa WebSockets
def iniciar_websockets():
    threading.Thread(target=websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_message=on_trade
    ).run_forever, daemon=True).start()

    threading.Thread(target=websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@kline_1m",
        on_message=on_kline
    ).run_forever, daemon=True).start()

    threading.Thread(target=websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@depth20@100ms",
        on_message=on_book
    ).run_forever, daemon=True).start()

    threading.Thread(target=loop_envio_gpt, daemon=True).start()

# Roda o bot
if __name__ == "__main__":
    print("🚀 NeuroScalp iniciado com OpenAI nova - Enviando dados em tempo real...")
    iniciar_websockets()
    while True:
        time.sleep(1)
