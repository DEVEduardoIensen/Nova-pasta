import asyncio
import websockets
import json
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYMBOL = "btcusdt"
STREAM_URL = f"wss://stream.binance.com:9443/stream?streams={SYMBOL}@depth20@100ms/{SYMBOL}@aggTrade/{SYMBOL}@kline_1m"

async def enviar_ao_gpt(dados):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": "Voce recebe dados em tempo real do mercado de BTC/USDT pode me dizer o que voce esta recebendo."},
                {"role": "user", "content": json.dumps(dados)}
            ],
            temperature=0.1
        )
        print("Resposta GPT:", resposta.choices[0].message.content)
    except Exception as e:
        print("Erro ao enviar pro GPT:", e)

def limpar_book(book):
    # Remove ordens irrelevantes (ex: volumes muito pequenos)
    volume_minimo = 0.00001
    book_filtrado = [[preco, qtd] for preco, qtd in book if float(qtd) >= volume_minimo]
    return book_filtrado

async def receber_dados():
    fluxo_ordens = []
    async with websockets.connect(STREAM_URL) as ws:
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                tipo = data["stream"]
                conteudo = data["data"]

                if "@aggTrade" in tipo:
                    fluxo_ordens.append({
                        "tipo": "buy" if conteudo["m"] == False else "sell",
                        "preco": conteudo["p"],
                        "quantidade": conteudo["q"]
                    })
                    if len(fluxo_ordens) > 30:
                        fluxo_ordens = fluxo_ordens[-30:]

                elif "@depth20" in tipo:
                    order_book = {
                        "bids": limpar_book(conteudo["bids"]),
                        "asks": limpar_book(conteudo["asks"])
                    }

                elif "@kline_1m" in tipo and conteudo["k"]["x"]:  # Candle fechado
                    k = conteudo["k"]
                    kline_1m = {
                        "open": k["o"],
                        "high": k["h"],
                        "low": k["l"],
                        "close": k["c"],
                        "volume": k["v"],
                        "is_green": float(k["c"]) > float(k["o"])
                    }

                    json_enviar = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "preco_atual": k["c"],
                        "kline_1m": kline_1m,
                        "order_book": order_book,
                        "fluxo_ordens": fluxo_ordens
                    }

                    await enviar_ao_gpt(json_enviar)

            except Exception as e:
                print("Erro no WebSocket:", e)

asyncio.run(receber_dados())