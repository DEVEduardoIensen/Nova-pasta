import websocket
import json

def on_message(ws, message):
    data = json.loads(message)

    bids = data.get("b", [])  
    asks = data.get("a", [])  

    print("\n[ NOVO PACOTE DO BOOK ]")
    print(f"Bids (compras): {len(bids)} níveis")
    print(f"Asks (vendas): {len(asks)} níveis")

    print("Exemplo de Bids:")
    for bid in bids:
        print(bid)

    print("Exemplo de Asks:")
    for ask in asks:
        print(ask)

def on_open(ws):
    print("Conexão aberta")

def on_error(ws, error):
    print("Erro:", error)

def on_close(ws, code, reason):
    print("Conexão encerrada")


SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@depth"

ws = websocket.WebSocketApp(SOCKET,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()
