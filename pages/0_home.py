import streamlit as st
import requests
import datetime
import yfinance as yf

st.set_page_config(
    page_title="Dashboard Home",
    layout="wide",
)

# ---------------------------------------------------------
# FETCH BACKGROUND FROM UNSPLASH
# ---------------------------------------------------------
def get_unsplash_background():
    try:
        access_key = st.secrets["unsplash"]["access_key"]
        query = "calm minimal gradient abstract soft subtle background"
        url = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape&client_id={access_key}"
        data = requests.get(url).json()
        return data["urls"]["regular"]
    except:
        # fallback gradient
        return "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1600&q=80"

bg_image = get_unsplash_background()

st.markdown(
    f"""
    <style>
        .stApp {{
            background: url('{bg_image}') no-repeat center center fixed;
            background-size: cover;
        }}
        .city-card {{
            padding: 18px;
            border-radius: 14px;
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(8px);
            box-shadow: 0px 4px 8px rgba(0,0,0,0.10);
            text-align: center;
            font-size: 18px;
            margin: 5px;
        }}
        .macro-card {{
            padding: 12px;
            border-radius: 12px;
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(8px);
            text-align: center;
            min-width: 140px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.08);
            font-size: 17px;
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
# WEATHER SECTION
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
        pct = ((latest - prev) / prev) * 100
        return latest, pct
    except:
        return None, None

macro_cols = st.columns(len(MACROS))
for idx, (name, ticker) in enumerate(MACROS.items()):
    price, pct = fetch_macro(ticker)

    if price is None:
        card = f"<div class='macro-card'><b>{name}</b><br>N/A</div>"
    else:
        card = f"""
        <div class='macro-card'>
            <b>{name}</b><br>
            {price:,.2f}<br>
            <span style='color:{'green' if pct>0 else 'red'};'>{pct:+.2f}%</span>
        </div>
        """

    with macro_cols[idx]:
        st.markdown(card, unsafe_allow_html=True)
