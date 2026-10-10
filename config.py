import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise SystemExit("Missing TELEGRAM_TOKEN or CHAT_ID in environment variables")

CHAT_ID = int(CHAT_ID)

MIN_VOLUME_24H_USDT = 500000
GROWTH_15M_THRESHOLD = 0.05
STRONG_GROWTH_THRESHOLD = 0.12
ORDERBOOK_LIMIT = 50
SELL_PRESSURE_THRESHOLD = -0.25
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
COOLDOWN_SECONDS = 1800
SCAN_INTERVAL = 60
GATE_BASE = "https://api.gateio.ws/api/v4"
