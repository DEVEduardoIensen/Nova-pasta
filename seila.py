import websocket
import json
import datetime

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"

def on_open(ws):
    print("Conexão aberta.")

def on_close(ws):
    print("Conexão fechada.")

def on_message(ws, message):
    data = json.loads(message)
    bid_price = data.get('b')
    ask_price = data.get('a')
    now = datetime.datetime.now()

    linha = f"Dados gravados: {now} | Bid: {bid_price} | Ask: {ask_price}\n"

    with open("book_data.log", "a") as f:
        f.write(linha)

    print(linha.strip())

ws = websocket.WebSocketApp(SOCKET,
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message)

ws.run_forever()
