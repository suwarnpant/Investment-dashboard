import streamlit as st
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="Home", layout="wide")

# ==========================================================
# 1) BACKGROUND IMAGE FROM UNSPLASH (DARK, CALM, ABSTRACT)
# ==========================================================
UNSPLASH_API_KEY = st.secrets["unsplash"]["api_key"]

def get_unsplash_image():
    try:
        url = (
            "https://api.unsplash.com/photos/random"
            "?query=minimal dark abstract gradient texture"
            "&orientation=landscape"
        )
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json()["urls"]["full"]
        else:
            return "https://images.unsplash.com/photo-1522199670076-2852f80289c7"
    except:
        return "https://images.unsplash.com/photo-1522199670076-2852f80289c7"

bg_url = get_unsplash_image()

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url('{bg_url}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

.block-container {{
    background: rgba(0,0,0,0);
}}

.card {{
    background: rgba(0, 0, 0, 0.35);
    padding: 18px;
    border-radius: 14px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: white;
    text-align: center;
}}

.logo {{
    width: 36px;
    margin-bottom: 6px;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# ==========================================================
# 2) GREETING (IST BASED)
# ==========================================================
ist = pytz.timezone("Asia/Kolkata")
hour = datetime.now(ist).hour

if hour < 12:
    greet = "🌅 Good Morning"
elif hour < 17:
    greet = "🌤️ Good Afternoon"
else:
    greet = "🌙 Good Evening"

st.markdown(f"<h1 style='color:white;font-weight:300'>{greet}, Suwarn 👋</h1>", unsafe_allow_html=True)

# ==========================================================
# 3) WEATHER — OpenWeather API
# ==========================================================
WEATHER_KEY = st.secrets["weather"]["api_key"]

cities = {
    "Pune": "Pune,IN",
    "Mumbai": "Mumbai,IN",
    "Ahmedabad": "Ahmedabad,IN",
    "Haldwani": "Haldwani,IN"
}

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
        r = requests.get(url).json()
        return r["main"]["temp"], r["weather"][0]["main"]
    except:
        return None, None

st.markdown("<h3 style='color:white;'>🌦️ Weather</h3>", unsafe_allow_html=True)

cols = st.columns(4)
for (cname, query), col in zip(cities.items(), cols):
    temp, cond = get_weather(query)
    with col:
        st.markdown(
            f"""
            <div class="card">
                <b>{cname}</b><br>
                {temp if temp else 'N/A'}°C<br>
                {cond if cond else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================================
# 4) MACRO INDICATORS (Yahoo Finance)
# ==========================================================
import yfinance as yf

MACROS = {
    "Nifty 50": {"ticker": "^NSEI", "logo": "https://upload.wikimedia.org/wikipedia/commons/8/89/NSE_logo.svg"},
    "Nasdaq 100": {"ticker": "^NDX", "logo": "https://upload.wikimedia.org/wikipedia/commons/4/4a/NASDAQ_Logo.svg"},
    "Hang Seng": {"ticker": "^HSI", "logo": "https://upload.wikimedia.org/wikipedia/commons/6/6c/Hang_Seng_Bank_logo.svg"},
    "BTC/USD": {"ticker": "BTC-USD", "logo": "https://cryptologos.cc/logos/bitcoin-btc-logo.png"},
    "USD/INR": {"ticker": "INR=X", "logo": "https://upload.wikimedia.org/wikipedia/commons/4/41/Flag_of_India.svg"},
    "Gold": {"ticker": "GC=F", "logo": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Gold_ingots_icon.png"},
    "Crude Oil": {"ticker": "CL=F", "logo": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Oil_barrel_icon.png"},
}

def get_macro(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        price = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2] if len(data) > 1 else price
        pct = ((price - prev) / prev) * 100 if prev != 0 else 0
        return price, pct
    except:
        return None, None

st.markdown("<br><h3 style='color:white;'>📊 Macro Indicators</h3>", unsafe_allow_html=True)

macro_cols = st.columns(4)
macro_items = list(MACROS.items())

for i, col in enumerate(macro_cols):
    with col:
        for name, info in macro_items[i*2 : (i+1)*2]:  # 2 per column
            price, pct = get_macro(info["ticker"])
            change_color = "lightgreen" if pct and pct > 0 else "#ff6b6b"
            pct_disp = f"{pct:+.2f}%" if pct is not None else ""
            price_disp = f"{price:,.2f}" if price else "N/A"

            st.markdown(
                f"""
                <div class="card">
                    <img src="{info['logo']}" class="logo"><br>
                    <b>{name}</b><br>
                    {price_disp}<br>
                    <span style="color:{change_color}">{pct_disp}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
