import streamlit as st
import requests
from datetime import datetime, timedelta

def fetch_news_finnhub(ticker):
    api_key = st.secrets["finnhub"]["api_key"]
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={ticker}&from={yesterday}&to={today}&token={api_key}"
    )

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        news = r.json()
        return news[:5]  # top 5
    except Exception as e:
        return []
