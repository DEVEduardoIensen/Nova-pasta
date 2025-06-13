import websocket
import json
import datetime

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@trade"

def on_open(ws):
    print("Conexão aberta")

def on_close(ws):
    print("Conexão fechada")

def on_message(ws, message):
    data = json.loads(message)
    event_time = datetime.datetime.fromtimestamp(data['E'] / 1000)
    receive_time = datetime.datetime.now()
    price = data['p']
    latency = max((receive_time - event_time).total_seconds() * 1000,0 )
    print(f"{receive_time} - BTCUSDT: {price} - Latência: {latency:.2f} ms")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()