import streamlit as st
import requests
import base64
from datetime import datetime
import pytz

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# UNSPLASH BACKGROUND (BASE64 EMBED, ALWAYS WORKS)
# ---------------------------------------------------------
UNSPLASH_API_KEY = st.secrets["unsplash"]["api_key"]

def get_bg_base64():
    try:
        url = (
            "https://api.unsplash.com/photos/random"
            "?query=minimal dark gradient abstract"
            "&orientation=landscape"
        )
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            img_url = r.json()["urls"]["full"]
        else:
            img_url = "https://images.unsplash.com/photo-1522199670076-2852f80289c7"
    except:
        img_url = "https://images.unsplash.com/photo-1522199670076-2852f80289c7"

    img_data = requests.get(img_url).content
    encoded = base64.b64encode(img_data).decode()
    return encoded


bg_base64 = get_bg_base64()

background_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("data:image/jpeg;base64,{bg_base64}") !important;
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
    background: rgba(0,0,0,0.4);
    padding: 18px;
    border-radius: 14px;
    color: white;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    text-align: center;
}}

.macro-card {{
    background: rgba(0,0,0,0.45);
    padding: 18px;
    border-radius: 12px;
    color: white;
    width: 160px;
    display: inline-block;
    margin: 8px;
}}

.macro-logo {{
    width: 32px;
    height: 32px;
    margin-bottom: 6px;
}}
</style>
"""
st.markdown(background_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# GREETING (IST BASED)
# ---------------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
hour = now.hour

if hour < 12:
    greet = "Good Morning Suwarn"
elif hour < 17:
    greet = "Good Afternoon Suwarn"
else:
    greet = "Good Evening Suwarn"

st.markdown(f"<h1 style='color:white'>{greet}</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# WEATHER (4 cities)
# ---------------------------------------------------------
WEATHER_KEY = st.secrets["weather"]["api_key"]
cities = ["Pune", "Mumbai", "Ahmedabad", "Haldwani"]

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
    r = requests.get(url).json()
    temp = r["main"]["temp"]
    cond = r["weather"][0]["description"].title()
    return temp, cond

st.markdown("<h2 style='color:white'>Weather</h2>", unsafe_allow_html=True)

wcols = st.columns(len(cities))

for i, city in enumerate(cities):
    temp, cond = get_weather(city)
    wcols[i].markdown(
        f"""
        <div class="card">
            <h3>{city}</h3>
            <b>{temp:.1f}°C</b><br>
            {cond}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
def get_price_yf(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
        r = requests.get(url).json()
        result = r["chart"]["result"][0]
        price = result["meta"]["regularMarketPrice"]
        prev = result["meta"]["chartPreviousClose"]
        pct = ((price - prev) / prev) * 100
        return price, pct
    except:
        return None, None

indicators = [
    ("Nifty 50", "^NSEI", "https://icons.iconarchive.com/icons/iconsmind/outline/512/Line-Chart-icon.png"),
    ("Nasdaq 100", "^NDX", "https://cdn-icons-png.flaticon.com/512/833/833524.png"),
    ("Hang Seng", "^HSI", "https://cdn-icons-png.flaticon.com/512/32/32213.png"),
    ("BTC/USD", "BTC-USD", "https://cryptologos.cc/logos/bitcoin-btc-logo.png"),
    ("Gold", "GC=F", "https://cdn-icons-png.flaticon.com/512/179/179249.png"),
    ("Crude Oil", "CL=F", "https://cdn-icons-png.flaticon.com/512/727/727240.png"),
    ("USD/INR", "INR=X", "https://cdn-icons-png.flaticon.com/512/2894/2894978.png"),
]

st.markdown("<h2 style='color:white'>Macro Indicators</h2>", unsafe_allow_html=True)

mcols = st.columns(4)

for i, (name, ticker, logo) in enumerate(indicators):
    price, pct = get_price_yf(ticker)
    color = "lightgreen" if pct and pct > 0 else "red"
    mcols[i % 4].markdown(
        f"""
        <div class="macro-card">
            <img src="{logo}" class="macro-logo"><br>
            <b>{name}</b><br>
            {price:.2f if price else "N/A"}<br>
            <span style="color:{color}">{pct:+.2f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )

