import os
from dotenv import load_dotenv

load_dotenv()

binance_key = os.getenv("BINANCE_API_KEY")
binance_secret = os.getenv("BINANCE_SECRET_KEY")

print("API Key da Binance :", binance_key)
print("API Secret da Binance :", binance_secret)
