import pandas as pd
import requests
import ccxt
import ta
from datetime import datetime

# ==== Configuration ====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375263937335132190/smDvToD98xqTK8j9s-IjklZToNUByBZkVwgNfRrMVBKxBkfG78f9Rv7XUbERo0sp2V2i"
TIMEFRAME = '12h'
LIMIT = 1000

# ==== Discord Sender ====
def send_summary_to_discord(buys, sells):
    timestamp = datetime.utcnow().isoformat()

    embed = {
        "title": "📈 12/21 EMA Crossover Signals",
        "description": "Top 1000 Binance USDT Pairs • 12H Timeframe",
        "color": 0x1ABC9C,  # Teal color
        "fields": [
            {
                "name": "🟢 Buy Signals",
                "value": "\n".join([f"➕ `{symbol}`" for symbol in buys]) if buys else "_No signals_",
                "inline": False
            },
            {
                "name": "🔴 Sell Signals",
                "value": "\n".join([f"➖ `{symbol}`" for symbol in sells]) if sells else "_No signals_",
                "inline": False
            }
        ],
        "footer": {
            "text": "Signal Bot • 12/21 EMA Strategy"
        },
        "timestamp": timestamp
    }

    payload = {
        "username": "EMA Signal Bot",
        "avatar_url": "https://cryptologos.cc/logos/binance-coin-bnb-logo.png",  # optional
        "embeds": [embed]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload)


# ==== Data Fetcher ====
def fetch_data(exchange, symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# ==== Signal Checker ====
def check_ema_signal(df):
    ema12 = ta.trend.EMAIndicator(close=df['close'], window=12).ema_indicator()
    ema21 = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()

    if ema12.iloc[-1] > ema21.iloc[-1] and ema12.iloc[-2] <= ema21.iloc[-2]:
        return "BUY"
    elif ema12.iloc[-1] < ema21.iloc[-1] and ema12.iloc[-2] >= ema21.iloc[-2]:
        return "SELL"
    return None

# ==== Get Top 1000 USDT Pairs ====
def get_top_1000_usdt_pairs(exchange):
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if symbol.endswith('/USDT') and markets[symbol]['active']]
    return usdt_pairs[:1000]

# ==== Runner ====
def run_bot():
    exchange = ccxt.binance()
    pairs = get_top_1000_usdt_pairs(exchange)

    buys = []
    sells = []

    for symbol in pairs:
        try:
            df = fetch_data(exchange, symbol)
            signal = check_ema_signal(df)
            if signal == "BUY":
                buys.append(symbol)
            elif signal == "SELL":
                sells.append(symbol)
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    send_summary_to_discord(buys, sells)

if __name__ == "__main__":
    run_bot()
