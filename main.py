import asyncio
import websockets
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LIMIAR_VOLUME = 0.000000001
SYMBOL = "btcusdt"
URL = f"wss://stream.binance.com:9443/stream?streams=btcusdt@depth20@100ms/{SYMBOL}@aggTrade/{SYMBOL}@kline_1m"


PROMPT_BASE = """
Está recebendo dados em tempo real do BTC/USDT:
pode me dizer o que está recebendo e como esta recebendo
"""

# Flags para evitar repetir respostas
recebeu_fluxo = False
recebeu_book = False
recebeu_candle = False

async def enviar_ao_gpt(dados):
    global recebeu_fluxo, recebeu_book, recebeu_candle
    tipo = dados.get("tipo")

    try:
        resposta = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": PROMPT_BASE},
                {"role": "user", "content": json.dumps(dados)}
            ],
            temperature=0
        )
        texto = resposta.choices[0].message.content.strip()

        # Evita repetir confirmações
        if tipo == "fluxo" and not recebeu_fluxo:
            print("📤 GPT (fluxo):", texto)
            recebeu_fluxo = "fluxo" in texto.lower() or "ordens" in texto.lower()

        elif tipo == "book" and not recebeu_book:
            print("📤 GPT (book):", texto)
            recebeu_book = "book" in texto.lower() or "ofertas" in texto.lower()

        elif tipo == "candle" and not recebeu_candle:
            print("📤 GPT (candle):", texto)
            recebeu_candle = "candle" in texto.lower() or "gráfico" in texto.lower()

    except Exception as e:
        print("❌ Erro com o GPT:", e)

async def conectar():
    print(f"Conectando ao WebSocket da Binance para {SYMBOL.upper()}...")
    async with websockets.connect(URL) as ws:
        while True:
            try:
                resposta = await ws.recv()
                dados = json.loads(resposta)
                stream = dados['stream']
                conteudo = dados['data']

                if "@aggTrade" in stream:
                    preco = float(conteudo['p'])
                    volume = float(conteudo['q'])
                    comprador = not conteudo['m']
                    print(f"🟡 Fluxo: {preco} | {volume} | {'compra' if comprador else 'venda'}")

                    if volume >= LIMIAR_VOLUME:
                        fluxo = {
                            "tipo": "fluxo",
                            "preco": preco,
                            "volume": volume,
                            "comprador": comprador
                        }
                        await enviar_ao_gpt(fluxo)

                elif "@depth" in stream:
                    bids_raw = conteudo.get('bids', [])
                    asks_raw = conteudo.get('asks', [])

                    # DEPOIS (CERTO — envia o book completo, sem filtrar)
                    bids = [[float(p), float(q)] for p, q in bids_raw]
                    asks = [[float(p), float(q)] for p, q in asks_raw]


                    print(f"🟢 Book: {len(bids)} bids | {len(asks)} asks")

                    book = {
                        "tipo": "book",
                        "bids": bids,
                        "asks": asks
                    }
                    await enviar_ao_gpt(book)

                elif "@kline" in stream:
                    k = conteudo['k']
                    candle = {
                        "tipo": "candle",
                        "abertura": float(k['o']),
                        "fechamento": float(k['c']),
                        "maxima": float(k['h']),
                        "minima": float(k['l']),
                        "volume": float(k['v'])
                    }

                    print(f"🔵 Candle: Abertura: {candle['abertura']} | Fechamento: {candle['fechamento']}")

                    await enviar_ao_gpt(candle)

            except Exception as e:
                print("❌ Erro no WebSocket:", e)
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(conectar())
