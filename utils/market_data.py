import yfinance as yf
import requests

def get_stock_price(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")
        price = hist["Close"].iloc[-1]
        high_52 = data.info.get("fiftyTwoWeekHigh", None)
        low_52 = data.info.get("fiftyTwoWeekLow", None)
        return price, high_52, low_52
    except:
        return None, None, None

def get_crypto_price(id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
    try:
        r = requests.get(url).json()
        return r[id]['usd']
    except:
        return None

def get_index_price(ticker):
    return get_stock_price(ticker)[0]
