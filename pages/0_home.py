import streamlit as st
import requests
import yfinance as yf
import pytz
from datetime import datetime
import time
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
        url = (
            "https://api.unsplash.com/photos/random?"
            "query=dark,minimal&orientation=landscape&client_id="
            + UNSPLASH_API_KEY
        )

        r = requests.get(url).json()
        print("Unsplash Response:", r)   # <–– now 'r' exists

        if "urls" in r:
            img = r["urls"]["regular"]   # faster/lighter than full
            return img + f"&t={datetime.now().timestamp()}"
        else:
            print("Unsplash ERROR: No URLs returned")
            raise Exception("No image in response")

    except Exception as e:
        print("Unsplash ERROR:", e)
        return (
            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
            "?auto=format&fit=crop&w=1920&q=80"
        )

 



bg_url = get_unsplash_image()

page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("{bg_url}") no-repeat center center fixed;
    background-size: cover;
}}

/* -------------------------- */
/*   NEUMORPHIC CARD STYLE    */
/* -------------------------- */
.weather-card, .macro-card {{
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);

    box-shadow:
        8px 8px 16px rgba(0,0,0,0.45),
        -8px -8px 16px rgba(255,255,255,0.04);

    background-blend-mode: overlay;

    color: white;
    text-align: center;
    margin-bottom: 20px;
    transition: 0.25s ease;
}}

.weather-card:hover, .macro-card:hover {{
    transform: translateY(-3px);
    box-shadow:
        12px 12px 20px rgba(0,0,0,0.55),
        -12px -12px 20px rgba(255,255,255,0.05);
}}

/* Logo size */
.macro-logo {{
    width: 35px;
    height: 35px;
    margin-bottom: 8px;
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
        return "Good Evening"

greet = get_greeting()

st.markdown(
    f"<h1 style='text-align:center; color:white; margin-top:-20px;'>{greet}, Suwarn !!!</h1>",
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
    "Nifty 50": (
        "^NSEI",
        "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Nifty_50_Logo.svg/1200px-Nifty_50_Logo.svg.png"
    ),
    "Nasdaq 100": (
        "^NDX",
        "https://www.nasdaq.com/sites/acquia.prod/files/2020/09/24/nasdaq.jpg"
    ),
    "Hang Seng": (
        "^HSI",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQondjn-eCA_xCRsB7Tw3D79fmSOoTW-WXmIg&s"
    ),
    "BTC/USD": (
        "BTC-USD",
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=031"
    ),
    "USD/INR": (
        "USDINR=X",
        "https://p7.hiclipart.com/preview/309/810/323/indian-rupee-sign-computer-icons-currency-symbol-icon-design-rupee.jpg"
    ),
    "Gold": (
        "GC=F",
        "data:image/jpeg;base64,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"
    ),
    "Crude Oil": (
        "CL=F",
        "data:image/jpeg;base64,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"
    )
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
