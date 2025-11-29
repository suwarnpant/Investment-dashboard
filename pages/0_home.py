import streamlit as st
import requests
import datetime
import random

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Home",
    layout="wide",
)

# ---------------------------------------------------------
# DAILY BACKGROUND (calm minimal gradients)
# ---------------------------------------------------------
BACKGROUNDS = [
    "linear-gradient(135deg, #DEE4EA, #F7F9FA)",
    "linear-gradient(135deg, #DCE7F3, #F8FBFF)",
    "linear-gradient(135deg, #E8EAF6, #F5F7FA)",
    "linear-gradient(135deg, #E4F1F7, #F8FCFF)",
]
selected_bg = BACKGROUNDS[datetime.datetime.now().day % len(BACKGROUNDS)]

st.markdown(
    f"""
    <style>
        .stApp {{
            background: {selected_bg};
        }}
        .city-card {{
            padding: 18px;
            border-radius: 14px;
            background: white;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.06);
            text-align: center;
            font-size: 18px;
            margin: 5px;
        }}
        .macro-card {{
            padding: 12px;
            border-radius: 12px;
            background: white;
            text-align: center;
            min-width: 140px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# GREETING
# ---------------------------------------------------------
now = datetime.datetime.now().hour
if now < 12:
    greeting = "Good Morning"
elif now < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

st.markdown(f"## 👋 {greeting}, **Suwarn**")

# ---------------------------------------------------------
# WEATHER FETCH
# ---------------------------------------------------------
WEATHER_CITIES = ["Pune", "Mumbai", "Ahmedabad", "Haldwani"]
API_KEY = st.secrets["weather"]["api_key"]

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        return f"{temp:.1f}°C | {desc}"
    except:
        return "N/A"

# ---------------------------------------------------------
# WEATHER ROW
# ---------------------------------------------------------
st.markdown("### 🌦 Weather Overview")

cols = st.columns(len(WEATHER_CITIES))
for idx, city in enumerate(WEATHER_CITIES):
    with cols[idx]:
        st.markdown(
            f"<div class='city-card'><b>{city}</b><br>{get_weather(city)}</div>",
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 🌍 Macro Indicators")

import yfinance as yf

MACROS = {
    "Nifty 50": "^NSEI",
    "NASDAQ 100": "^NDX",
    "US 10Y Bond": "^TNX",
    "India VIX": "^INDIAVIX",
    "US VIX": "^VIX",
}

def fetch_macro(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        latest = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2]
        change = latest - prev
        pct = (change / prev) * 100
        return latest, pct
    except:
        return None, None

macro_cols = st.columns(len(MACROS))
for idx, (name, ticker) in enumerate(MACROS.items()):
    price, pct = fetch_macro(ticker)

    if price is None:
        card = f"<div class='macro-card'><b>{name}</b><br>N/A</div>"
    else:
        sign = "🟢" if pct > 0 else "🔻"
        card = f"""
        <div class='macro-card'>
            <b>{name}</b><br>
            {price:,.2f}<br>
            <span style='color:{"green" if pct>0 else "red"};'>{sign} {pct:.2f}%</span>
        </div>
        """

    with macro_cols[idx]:
        st.markdown(card, unsafe_allow_html=True)
