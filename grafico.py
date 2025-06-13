import websocket
import json
import datetime

def on_open(ws):
    print("Conexão aberta ao gráfico (kline)")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexão encerrada - Código: {close_status_code}, Mensagem: {close_msg}")

def on_message(ws, message):
    data = json.loads(message)
    k = data['k']
    print(f"\n[ NOVO CANDLE ]")
    print(f"Time: {datetime.datetime.fromtimestamp(k['t'] / 1000)}")
    print(f"Abertura: {k['o']}")
    print(f"Alta: {k['h']}")
    print(f"Baixa: {k['l']}")
    print(f"Fechamento: {k['c']}")
    print(f"Volume: {k['v']}")

socket = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
