import websocket
import json
from datetime import datetime


socket = "wss://stream.binance.com:9443/ws/btcusdt@trade"

def on_message(ws, message):
    data = json.loads(message)
    trade_time = datetime.fromtimestamp(data['T'] / 1000)  # horário do trade
    price = float(data['p'])
    qty = float(data['q'])
    side = "Compra" if data['m'] == False else "Venda"
    
    print(f"[{trade_time}] {side}: {qty} BTC a {price} USD")

def on_error(ws, error):
    print("Erro:", error)

def on_close(ws, close_status_code, close_msg):
    print("Conexão encerrada")

def on_open(ws):
    print("Conexão aberta ao fluxo de ordens (trades)")

ws = websocket.WebSocketApp(socket,
                             on_open=on_open,
                             on_message=on_message,
                             on_error=on_error,
                             on_close=on_close)
ws.run_forever()