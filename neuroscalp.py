import asyncio
import websockets
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LIMIAR_VOLUME = 0.01
SYMBOL = "btcusdt"

URL = f"wss://stream.binance.com:9443/stream?streams={SYMBOL}@depth@100ms/{SYMBOL}@aggTrade/{SYMBOL}@kline_1m"

PROMPT_BASE = """
Você é um sistema de trading autônomo.

Receberá dados em tempo real do mercado: book, candle e fluxo.

Decida se deve ENTRAR COMPRADO, ENTRAR VENDIDO ou AGUARDAR.

Lembre-se:

- Toda entrada precisa cobrir as taxas da Binance (0.3% + 0.3%)
- A decisão deve ser com foco em identificar o início de tendências
- Encerre posições antes de uma possível reversão

Responda apenas com:
COMPRAR
VENDER

senao fique em silencio espernando a decisao 
"""

# função para enviar os dados ao GPT
async def enviar_ao_gpt(dados):
    try:
        resposta = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",  # ou o que você tiver habilitado
            messages=[
                {"role": "system", "content": PROMPT_BASE},
                {"role": "user", "content": json.dumps(dados)}
            ],
            temperature=0
        )
        decisao = resposta.choices[0].message.content.strip()
        print("📤 Decisão do GPT:", decisao)
    except Exception as e:
        print("Erro com o GPT:", e)

# função principal
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
                    comprador = conteudo['m'] == False

                    if volume >= LIMIAR_VOLUME:
                        json_limpo = {
                            "tipo": "fluxo",
                            "preco": preco,
                            "volume": volume,
                            "comprador": comprador
                        }
                        await enviar_ao_gpt(json_limpo)

                elif "@depth" in stream:
                    bids = [[float(p), float(q)] for p, q in conteudo.get('bids', []) if float(q) >= LIMIAR_VOLUME]
                    asks = [[float(p), float(q)] for p, q in conteudo.get('asks', []) if float(q) >= LIMIAR_VOLUME]

                    json_limpo = {
                        "tipo": "book",
                        "bids": bids[:5],
                        "asks": asks[:5]
                    }
                    await enviar_ao_gpt(json_limpo)

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
                    await enviar_ao_gpt(candle)

            except Exception as e:
                print("Erro na leitura do WebSocket:", e)
                await asyncio.sleep(2)

# executa
if __name__ == "__main__":
    asyncio.run(conectar())
