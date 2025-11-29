import requests
from datetime import datetime, timedelta

def fetch_news_finnhub(ticker):
    api_key = st.secrets["finnhub"]["api_key"]
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={yesterday()}&to={today()}&token={api_key}"

    try:
        return requests.get(url).json()
    except:
        return []

def today():
    return datetime.now().strftime("%Y-%m-%d")

def yesterday():
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
