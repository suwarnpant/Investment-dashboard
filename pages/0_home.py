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
        # curated dark-minimal collections
        COLLECTION_ID = "1454818"   # Dark Minimal Collection

        url = (
            f"https://api.unsplash.com/photos/random"
            f"?collections={COLLECTION_ID}"
            f"&orientation=landscape"
            f"&content_filter=high"
            f"&client_id={UNSPLASH_API_KEY}"
        )

        r = requests.get(url).json()
        img = r["urls"]["regular"]

        # ensure refresh
        return img + f"&t={datetime.now().timestamp()}"

    except Exception as e:
        print("Unsplash ERROR:", e)
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1920&q=80"

 



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
        "https://s3-symbol-logo.tradingview.com/indices/usd-inr--600.png"
    ),
    "Gold": ("GOLD_INR", "https://img.freepik.com/premium-psd/design-mockup-with-gold-logo-leather_310696-18.jpg"
    ),
    
    "Crude Oil": (
        "CRUDE",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7YJgVc8O5qY-yXfiWBJUtJo0i0Dsf0fARzg&s"
    )
}


def fetch_macro(ticker):
    try:
        # ----------------------------------------------------
        # 1) GOLD (INR per 10g using MetalPriceAPI)
        # ----------------------------------------------------
        if ticker == "GOLD_INR":
            try:
                url = "https://api.metalpriceapi.com/v1/latest"
                params = {
                    "api_key": "6299316948900caacac7dc9f57d0466b",
                    "base": "USD",
                    "currencies": "XAU"
                }

                r = requests.get(url, params=params).json()

                # --- USD Gold Spot per Ounce ---
                if "rates" in r and "USDXAU" in r["rates"]:
                    usd_per_oz = float(r["rates"]["USDXAU"])
                else:
                    return None, None

                # --- USDINR rate ---
                try:
                    fx = yf.Ticker("USDINR=X").history(period="2d")
                    usdinr = float(fx["Close"].iloc[-1])
                except:
                    usdinr = 83.0  # fallback INR

                # --- Convert USD/oz → INR per 10g ---
                inr_per_gram = (usd_per_oz / 31.1035) * usdinr
                inr_10g = inr_per_gram * 10

                # No reliable % from API → use 0 or None
                return inr_10g, None

            except Exception as e:
                print("GOLD API ERROR:", e)
                return None, None

        # ----------------------------------------------------
        # 2) CRUDE OIL (API-Ninja)
        # ----------------------------------------------------
        if ticker == "CRUDE":
            try:
                headers = {"X-Api-Key": st.secrets["ninjas"]["api_key"]}
                url = "https://api.api-ninjas.com/v1/commodities?name=crude oil"

                crude_data = requests.get(url, headers=headers).json()

                if crude_data:
                    price = crude_data[0]["price"]
                    pct = crude_data[0].get("price_change_pct", 0.0)
                    return price, pct

                return None, None

            except Exception as e:
                print("CRUDE API ERROR:", e)
                return None, None

        # ----------------------------------------------------
        # 3) ALL OTHER MACROS (Yahoo Finance)
        # ----------------------------------------------------
        data = yf.Ticker(ticker).history(period="5d")

        if len(data) >= 2:
            last = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])
            pct = (last - prev) / prev * 100
            return last, pct

        return None, None

    except Exception as e:
        print("MACRO ERROR:", ticker, e)
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
