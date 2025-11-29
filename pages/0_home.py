import streamlit as st
import requests
from datetime import datetime
import pytz
import yfinance as yf

st.set_page_config(page_title="Home", layout="wide")


# ==========================================================
# 1) BACKGROUND — UNSPLASH MINIMAL DARK GRADIENT
# ==========================================================
UNSPLASH_API_KEY = st.secrets["unsplash"]["api_key"]

def get_unsplash_image():
    try:
        url = (
            "https://api.unsplash.com/photos/random"
            "?query=minimal dark gradient abstract texture"
            "&orientation=landscape"
        )
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()["urls"]["regular"]
    except:
        pass

    # fallback
    return "https://images.unsplash.com/photo-1522199670076-2852f80289c7"


bg_url = get_unsplash_image()


# ----------------------------------------------------------
# Inject background CSS
# ----------------------------------------------------------
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url('{bg_url}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0) !important;
}}

.block-container {{
    background: rgba(0,0,0,0) !important;
}}

.card {{
    background: rgba(0, 0, 0, 0.35);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: white;
    text-align: center;
    margin-bottom: 20px;
}}

.logo {{
    width: 40px;
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

st.markdown(
    f"<h1 style='color:white;font-weight:300'>{greet}, Suwarn 👋</h1>",
    unsafe_allow_html=True
)


# ==========================================================
# 3) WEATHER — OPENWEATHER API
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
        temp = r["main"]["temp"]
        cond = r["weather"][0]["main"]
        return round(temp, 1), cond  # single decimal
    except:
        return None, None


st.markdown("<h3 style='color:white;'>🌦️ Weather</h3>", unsafe_allow_html=True)
cols = st.columns(4)

for (name, query), col in zip(cities.items(), cols):
    temp, cond = get_weather(query)
    temp_disp = f"{temp:.1f}°C" if temp is not None else "N/A"

    col.markdown(
        f"""
        <div class="card">
            <b>{name}</b><br>
            {temp_disp}<br>
            {cond if cond else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# 4) MACRO INDICATORS — YFINANCE
# ==========================================================
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
        data = yf.Ticker(ticker).history(period="2d")
        price = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2]
        pct = (price - prev) / prev * 100
        return float(price), float(pct)
    except:
        return None, None


st.markdown("<br><h3 style='color:white;'>📊 Macro Indicators</h3>", unsafe_allow_html=True)

cols = st.columns(4)
macro_list = list(MACROS.items())

for i, col in enumerate(cols):
    items = macro_list[i*2 : (i+1)*2]  # 2 per column

    for name, info in items:
        price, pct = get_macro(info["ticker"])
        price_disp = f"{price:,.2f}" if price else "N/A"
        pct_disp = f"{pct:+.2f}%" if pct else "N/A"
        color = "lightgreen" if pct and pct > 0 else "#ff6b6b"

        col.markdown(
            f"""
            <div class="card">
                <img src="{info['logo']}" class="logo"><br>
                <b>{name}</b><br>
                {price_disp}<br>
                <span style="color:{color}">{pct_disp}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
