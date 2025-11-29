import streamlit as st
import requests
import datetime
import yfinance as yf

st.set_page_config(page_title="Home", layout="wide")

# ---------------------------------------------------------
# FETCH BACKGROUND FROM UNSPLASH
# ---------------------------------------------------------
def get_unsplash_background():
    try:
        access_key = st.secrets["unsplash"]["access_key"]
        query = "calm minimal gradient abstract soft background"
        url = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape&client_id={access_key}"
        data = requests.get(url).json()
        return data["urls"]["full"]
    except:
        return "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1600&q=80"

bg_image = get_unsplash_background()

# Background style
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url('{bg_image}') no-repeat center center fixed !important;
            background-size: cover !important;
        }}

        .glass-card {{
            padding: 20px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.3);
            text-align: center;
            color: #ffffff;
            font-size: 18px;
        }}

        .macro-card {{
            padding: 15px;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.25);
            text-align: center;
            color: #ffffff;
            font-size: 17px;
        }}

        .macro-logo {{
            width: 32px;
            height: 32px;
            margin-bottom: 6px;
        }}

        .weather-logo {{
            width: 36px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# GREETING
# ---------------------------------------------------------
hour = datetime.datetime.now().hour
if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

st.markdown(f"<h2 style='color:white;'>👋 {greeting}, Suwarn</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------
# WEATHER SECTION
# ---------------------------------------------------------
API_KEY = st.secrets["weather"]["api_key"]
CITIES = ["Pune", "Mumbai", "Ahmedabad", "Haldwani"]

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
        return temp, desc, icon_url
    except:
        return None, None, None

st.markdown("<h3 style='color:white;'>🌦 Weather</h3>", unsafe_allow_html=True)
weather_cols = st.columns(len(CITIES))

for i, city in enumerate(CITIES):
    temp, desc, icon = get_weather(city)
    with weather_cols[i]:
        st.markdown(
            f"""
            <div class="glass-card">
                <img src="{icon}" class="weather-logo">
                <br><b>{city}</b><br>
                {temp}°C<br>
                {desc}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
MACROS = {
    "Nifty 50": ("^NSEI", "https://upload.wikimedia.org/wikipedia/commons/3/3a/NSE_Logo.svg"),
    "NASDAQ 100": ("^NDX", "https://upload.wikimedia.org/wikipedia/commons/7/77/NASDAQ_Logo.svg"),
    "US 10Y Bond": ("^TNX", "https://cdn-icons-png.flaticon.com/512/711/711284.png"),
    "India VIX": ("^INDIAVIX", "https://cdn-icons-png.flaticon.com/512/476/476700.png"),
    "US VIX": ("^VIX", "https://cdn-icons-png.flaticon.com/512/476/476700.png"),
}

def fetch_macro(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        last = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2]
        pct = (last - prev) / prev * 100
        return last, pct
    except:
        return None, None

st.markdown("<h3 style='color:white; margin-top:20px;'>🌍 Macro Indicators</h3>", unsafe_allow_html=True)
macro_cols = st.columns(len(MACROS))

for i, (name, (ticker, logo)) in enumerate(MACROS.items()):
    value, pct = fetch_macro(ticker)
    with macro_cols[i]:
        st.markdown(
            f"""
            <div class="macro-card">
                <img src="{logo}" class="macro-logo">
                <br><b>{name}</b><br>
                {value:,.2f if value else "N/A"}<br>
                <span style="color:{'lightgreen' if pct and pct>0 else 'salmon'};">
                    {pct:+.2f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )
