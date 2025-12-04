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
        COLLECTION_ID = "1454818"  # Dark minimal curated
        url = (
            f"https://api.unsplash.com/photos/random"
            f"?collections={COLLECTION_ID}"
            f"&orientation=landscape"
            f"&content_filter=high"
            f"&client_id={UNSPLASH_API_KEY}"
        )
        r = requests.get(url).json()
        img = r["urls"]["regular"]
        return img + f"&t={datetime.now().timestamp()}"
    except:
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1920&q=80"

bg_url = get_unsplash_image()

# ---------------------------------------------------------
# CSS (Neumorphic transparent cards)
# ---------------------------------------------------------
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("{bg_url}") no-repeat center center fixed;
    background-size: cover;
}}

.weather-card, .macro-card {{
    padding: 16px;
    border-radius: 22px;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow:
        8px 8px 16px rgba(0,0,0,0.45),
        -8px -8px 16px rgba(255,255,255,0.04);
    color: white;
    text-align: center;
    margin-bottom: 20px;
}}

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
    hour = datetime.now(ist).hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    return "Good Evening"

st.markdown(
    f"<h1 style='text-align:center; color:white; margin-top:-20px;'>{get_greeting()}, Suwarn 👋</h1>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# WEATHER
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
        return temp, desc, f"http://openweathermap.org/img/w/{icon}.png"
    except:
        return None, None, None

st.markdown("<h3 style='color:white;'>🌤 Weather</h3>", unsafe_allow_html=True)
w_cols = st.columns(4)

for i, (city, cid) in enumerate(cities.items()):
    temp, desc, icon = get_weather(cid)
    w_cols[i].markdown(
        f"""
        <div class="weather-card">
            <h4>{city}</h4>
            {'<img src="'+icon+'" width="50">' if icon else ''}
            <div>{f"{temp:.1f}" if temp else "N/A"}°C</div>
            <small>{desc or ''}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# MACRO INDICATORS
# ---------------------------------------------------------
MACROS = {
    "Nifty 50": ("^NSEI", "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Nifty_50_Logo.svg/1200px-Nifty_50_Logo.svg.png"),
    "Nasdaq 100": ("^NDX", "https://www.nasdaq.com/sites/acquia.prod/files/2020/09/24/nasdaq.jpg"),
    "Hang Seng": ("^HSI", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQondjn-eCA_xCRsB7Tw3D79fmSOoTW-WXmIg&s"),
    "BTC/USD": ("BTC-USD", "https://cryptologos.cc/logos/bitcoin-btc-logo.png"),
    "USD/INR": ("USDINR=X", "https://p7.hiclipart.com/preview/309/810/323/indian-rupee-sign-computer-icons-currency-symbol-icon-design-rupee.jpg"),
    "Gold": ("GOLD_INR", "https://png.pngtree.com/png-vector/20200615/ourmid/pngtree-physical-gold-bar-cartoon-golden-vector-png-image_2256034.jpg"),
    "Crude Oil": ("CRUDE", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7YJgVc8O5qY-yXfiWBJUtJo0i0Dsf0fARzg&s"),
}

def fetch_macro(ticker):
    try:
        # ----- GOLD (Yahoo + INR conversion) -----
        if ticker == "GOLD_INR":
            gold = yf.Ticker("GC=F").history(period="5d")
            if len(gold) < 2:
                return None, None
            usd_today = float(gold["Close"].iloc[-1])
            usd_prev = float(gold["Close"].iloc[-2])

            fx = yf.Ticker("USDINR=X").history(period="2d")
            usdinr = float(fx["Close"].iloc[-1]) if not fx.empty else 83.0

            inr_per_gram = (usd_today / 31.1035) * usdinr
            inr_10g = inr_per_gram * 10
            pct = (usd_today - usd_prev) / usd_prev * 100
            return inr_10g, pct

        # ----- CRUDE OIL -----
        if ticker == "CRUDE":
            crude = yf.Ticker("CL=F").history(period="5d")
            if len(crude) < 2:
                return None, None
            last = float(crude["Close"].iloc[-1])
            prev = float(crude["Close"].iloc[-2])
            pct = (last - prev) / prev * 100
            return last, pct

        # ----- EQUITY / FX -----
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) >= 2:
            last = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])
            return last, (last - prev) / prev * 100

        return None, None

    except Exception as e:
        print("MACRO ERROR:", ticker, e)
        return None, None

# --------------------------- DISPLAY MACROS ---------------------------
st.markdown("<h3 style='color:white; margin-top:25px;'>📈 Macro Indicators</h3>", unsafe_allow_html=True)
m_cols = st.columns(len(MACROS))

macro_snapshot = {}

for i, (label, (ticker, logo)) in enumerate(MACROS.items()):
    val, pct = fetch_macro(ticker)

    macro_snapshot[label] = {
        "latest": val,
        "pct_change": pct
    }

    val_fmt = "N/A" if val is None else f"{val:,.2f}"
    pct_fmt = "" if pct is None else f"{pct:+.2f}%"
    pct_color = "lightgreen" if pct and pct > 0 else "salmon"

    m_cols[i].markdown(
        f"""
        <div class="macro-card">
            <img src="{logo}" class="macro-logo">
            <br><b>{label}</b><br>
            {val_fmt}<br>
            <span style="color:{pct_color};">{pct_fmt}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# MACRO SUMMARY (NEW)
# ---------------------------------------------------------
def build_clean_macro_snapshot(raw):
    out = {}
    for name, d in raw.items():
        if d["latest"] is None:
            continue
        out[name] = {
            "latest": d["latest"],
            "pct_change": d["pct_change"] or 0.0
        }
    return out

clean_snapshot = build_clean_macro_snapshot(macro_snapshot)

st.markdown("<h3 style='color:white; margin-top:25px;'>📰 Macro Summary</h3>", unsafe_allow_html=True)

if not clean_snapshot:
    st.info("Macro summary unavailable today.")
else:
    lines = []
    for name, d in clean_snapshot.items():
        pct = d["pct_change"]
        direction = "▲" if pct > 0 else "▼" if pct < 0 else "•"
        lines.append(f"**{name}** {direction} {pct:+.2f}%")

    st.markdown(
        f"""
        <div class="macro-card" style="padding:20px; font-size:18px;">
            {'<br>'.join(lines)}
        </div>
        """,
        unsafe_allow_html=True
    )
