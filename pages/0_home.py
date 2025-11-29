import streamlit as st
import requests
import yfinance as yf
import pytz
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Home", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE FROM UNSPLASH (daily refresh)
# ---------------------------------------------------------
UNSPLASH_API_KEY = st.secrets["unsplash"]["api_key"]

def get_unsplash_image():
    try:
        # UPDATED QUERY → calm minimal dark abstract
        url = (
            "https://api.unsplash.com/photos/random"
            "?query=minimal dark abstract gradient"
            "&orientation=landscape"
            f"&client_id={UNSPLASH_API_KEY}"
        )
        r = requests.get(url).json()
        return r["urls"]["full"]
    except:
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"

bg_url = get_unsplash_image()

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("{bg_url}") no-repeat center center fixed;
    background-size: cover;
}}

.macro-card {{
    padding: 12px;
    border-radius: 18px;
    background: rgba(255,255,255,0.10);
    text-align: center;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    color: white;
    margin-bottom: 10px;
}}

.macro-logo {{
    width: 35px;
    height: 35px;
    margin-bottom: 8px;
}}

.weather-card {{
    padding: 12px;
    border-radius: 18px;
    background: rgba(255,255,255,0.10);
    text-align: center;
    backdrop-filter: blur(10px);
    color: white;
    margin-bottom: 15px;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------------------------------------------
# GREETING BASED ON IST
# ---------------------------------------------------------
def get_greeting():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    hour = now.hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 22:
        return "Good Evening"
    else:
        return "Good Night"

greet = get_greeting()

st.markdown(
    f"<h1 style='text-align:center; color:white; margin-top:-20px;'>{greet}, Suwarn 👋</h1>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# WEATHER (OpenWeather API)
# ---------------------------------------------------------
OPENWEATHER_KEY = st.secrets["weather"]["api_key"]

cities = {
    "Pune": "1279228",
    "Mumbai": "1275339",
    "Ahmedabad": "1279233",
    "Haldwani": "1270079"
}

def get_weather(city_id):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={OPENWEATHER_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/w/{icon}.png"
        return temp, desc, icon_url
    except:
        return None, None, None

st.markdown("<h3 style='color:white;'>🌤 Weather</h3>", unsafe_allow_html=True)
w_cols = st.columns(4)

for i, (city, cid) in enumerate(cities.items()):
    temp, desc, icon = get_weather(cid)
    with w_cols[i]:
        st.markdown(
            f"""
            <div class="weather-card">
                <h4 style="margin-bottom:2px;">{city}</h4>
                {'<img src="'+icon+'" width="50">' if icon else ''}
                <div>{f"{temp:.1f}" if temp is not None else "N/A"}°C</div>
                <small>{desc if desc else ''}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
# ---------------------------------------------------------
# MACRO INDICATORS (FIXED: logos + BTC/Gold/Crude prices)
# ---------------------------------------------------------
MACROS = {
    "Nifty 50": ("^NSEI", "https://i.imgur.com/pQXjO7p.png"),
    "Nasdaq 100": ("^NDX", "https://i.imgur.com/6Z7L8tW.png"),
    "Hang Seng": ("^HSI", "https://i.imgur.com/Dm0H7mE.png"),
    "BTC/USD": ("BTC-USD", "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=029"),
    "USD/INR": ("USDINR=X", "https://i.imgur.com/Wx1yHOP.png"),
    "Gold": ("GC=F", "https://i.imgur.com/p7TCy3n.png"),
    "Crude Oil": ("CL=F", "https://i.imgur.com/KTc9KRV.png")
}

def fetch_macro(ticker):
    try:
        # First attempt - 2 day history
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            last = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            pct = (last - prev) / prev * 100
            return last, pct

        # Fallback 1 — use fast_info
        t = yf.Ticker(ticker)
        last = t.fast_info.get("last_price")
        prev = t.fast_info.get("previous_close")

        if last and prev:
            pct = (last - prev) / prev * 100
            return last, pct

        # Fallback 2 — as last resort
        return None, None

    except:
        return None, None

st.markdown("<h3 style='color:white; margin-top:25px;'>📈 Macro Indicators</h3>", unsafe_allow_html=True)
m_cols = st.columns(len(MACROS))

for i, (name, (ticker, logo)) in enumerate(MACROS.items()):
    val, pct = fetch_macro(ticker)

    val_fmt = "N/A" if val is None else f"{val:,.2f}"
    pct_fmt = "" if pct is None else f"{pct:+.2f}%"
    pct_color = "lightgreen" if pct and pct > 0 else "salmon"

    with m_cols[i]:
        st.markdown(
            f"""
            <div class="macro-card">
                <img src="{logo}" class="macro-logo">
                <br><b>{name}</b><br>
                {val_fmt}<br>
                <span style="color:{pct_color};">{pct_fmt}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
