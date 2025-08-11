# envio_saldo_estado.py
import os
import time
import hmac
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")

BASE_URL = "https://api.binance.com"

def assinatura(query):
    return hmac.new(API_SECRET.encode(), query.encode(), "sha256").hexdigest()

def saldo_spot():
    """Busca saldo spot atual (BNB e USDT)"""
    ts = int(time.time() * 1000)
    query = f"timestamp={ts}"
    sign = assinatura(query)
    url = f"{BASE_URL}/api/v3/account?{query}&signature={sign}"
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.get(url, headers=headers, timeout=5)
    r.raise_for_status()
    dados = r.json()
    saldos = {}
    for asset in dados.get("balances", []):
        if asset["asset"] in ["BNB", "USDT"]:
            saldos[asset["asset"]] = float(asset["free"])
    return saldos

def estado_operacao():
    """Verifica se há ordens abertas no SPOT"""
    ts = int(time.time() * 1000)
    query = f"timestamp={ts}"
    sign = assinatura(query)
    url = f"{BASE_URL}/api/v3/openOrders?{query}&signature={sign}"
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.get(url, headers=headers, timeout=5)
    r.raise_for_status()
    ordens = r.json()
    return len(ordens) > 0  # True se tem ordem aberta

def iniciar_saldo_estado(queue_saldo_estado):
    def enviar():
        try:
            queue_saldo_estado.put({
                "tipo": "saldo_estado",
                "dados": {
                    "saldo": saldo_spot(),
                    "em_operacao": estado_operacao()
                }
            })
        except Exception as e:
            print(f"❌ Erro ao enviar saldo/estado: {e}")

    def loop_envio():
        enviar()  # Envio inicial
        while True:
            time.sleep(150)  # Atualiza a cada 150 segundos
            enviar()

    threading.Thread(target=loop_envio, daemon=True).start()
