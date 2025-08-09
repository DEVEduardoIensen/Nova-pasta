import os
import time
import hmac
import json
import threading
import requests
import websocket
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")

BASE_URL = "https://api.binance.com"
WS_BASE = "wss://stream.binance.com:9443/ws"

from queue import Queue

queue_saldo = Queue()

def criar_listen_key():
    url = f"{BASE_URL}/api/v3/userDataStream"
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.post(url, headers=headers)
    return r.json().get("listenKey")

def renovar_listen_key(listen_key):
    url = f"{BASE_URL}/api/v3/userDataStream"
    headers = {"X-MBX-APIKEY": API_KEY}
    requests.put(url, headers=headers, params={"listenKey": listen_key})

def saldo_spot():
    ts = int(time.time() * 1000)
    query = f"timestamp={ts}"
    assinatura = hmac.new(API_SECRET.encode(), query.encode(), "sha256").hexdigest()
    url = f"{BASE_URL}/api/v3/account?{query}&signature={assinatura}"
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.get(url, headers=headers)
    dados = r.json()
    saldos = {}
    for asset in dados.get("balances", []):
        if asset["asset"] in ["BNB", "USDT"]:
            saldos[asset["asset"]] = float(asset["free"])
    return saldos

def iniciar_envio_saldo():
    def on_message(ws, message):
        try:
            msg = json.loads(message)
            if msg.get("e") in ["outboundAccountPosition", "balanceUpdate"]:
                novos_saldos = saldo_spot()
                nonlocal saldo_anterior
                if novos_saldos != saldo_anterior:
                    saldo_anterior = novos_saldos
                    queue_saldo.put({
                        "tipo": "saldo",
                        "dados": novos_saldos
                    })
        except Exception as e:
            print(f"❌ Erro ao processar saldo: {e}")

    def on_error(ws, error):
        print(f"⚠️ Erro WS saldo: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("🔌 WebSocket saldo fechado, tentando reconectar...")
        conectar_ws()

    def conectar_ws():
        nonlocal listen_key
        try:
            listen_key = criar_listen_key()
            threading.Thread(target=renovar_listen_key_periodicamente, daemon=True).start()

            # REST inicial só 1 vez
            iniciais = saldo_spot()
            nonlocal saldo_anterior
            saldo_anterior = iniciais
            queue_saldo.put({
                "tipo": "saldo",
                "dados": iniciais
            })

            ws_url = f"{WS_BASE}/{listen_key}"
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print(f"❌ Erro ao conectar saldo: {e}")
            time.sleep(5)
            conectar_ws()

    def renovar_listen_key_periodicamente():
        while True:
            time.sleep(1800)
            try:
                renovar_listen_key(listen_key)
                print("♻️ listenKey renovado (saldo).")
            except:
                pass

    listen_key = None
    saldo_anterior = {}
    conectar_ws()
