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
URL = f"wss://stream.binance.com:9443/stream?streams={SYMBOL}@depth@100ms/{SYMBOL}@aggTrade/{SYMBOL}@kline_1m"

PROMPT_BASE = """


Está recebendo dados em tempo real do BTC/USDT:

- Fluxo de ordens (agregadas)
- Livro de ofertas (book)
- Candle de 1 minuto (kline)

Apenas diga se está recebendo todos corretamente. nao esqueca de responder do grafico de falar se esta recebendo ele tambem
eu tenho que lapidar o codigo 



"""

# Função para enviar ao GPT
async def enviar_ao_gpt(dados):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=[
                {"role": "system", "content": PROMPT_BASE},
                {"role": "user", "content": json.dumps(dados)}
            ],
            temperature=0
        )
        decisao = resposta.choices[0].message.content.strip()
        print("📤 GPT:", decisao)
    except Exception as e:
        print("Erro com o GPT:", e)

# Função principal
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

                    print(f"🟡 Fluxo detectado: {preco} | {volume} | {'compra' if comprador else 'venda'}")

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

                    bids = [[float(p), float(q)] for p, q in bids_raw if float(q) >= LIMIAR_VOLUME]
                    asks = [[float(p), float(q)] for p, q in asks_raw if float(q) >= LIMIAR_VOLUME]

                    print(f"🟢 Book atualizado: {len(bids)} bids | {len(asks)} asks")

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

                    print(f"🔵 Candle fechado: {candle['volume']} | Abertura: {candle['abertura']} | Fechamento: {candle['fechamento']}")

                    await enviar_ao_gpt(candle)

            except Exception as e:
                print("Erro no WebSocket:", e)
                await asyncio.sleep(1)


# Executa
if __name__ == "__main__":
    asyncio.run(conectar())
