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
    "Nasdaq ": (
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
    "Gold": ("GOLD_INR", "https://static.vecteezy.com/system/resources/thumbnails/050/138/921/small/three-gold-bars-stacked-over-black-background-neon-sign-vector.jpg"
    ),
    
    "Crude Oil": (
        "CRUDE_INR",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpXtOOhMFHRVBhLgUi5nliSWrD-CNrOcmtTA&s"
    )
}

def fetch_macro(ticker):
    try:

        # ----------------------------------------------------
        # 1) GOLD (GC=F → Convert USD/oz → INR per 10g)
        # ----------------------------------------------------
        if ticker == "GOLD_INR":
            try:
                gold = yf.Ticker("GC=F").history(period="1mo", interval="1d")

                if gold is None or gold.empty:
                    print("Gold history empty")
                    return None, None

                # always works even if only 1 row exists
                usd_today = float(gold["Close"].iloc[-1])

                if len(gold) > 1:
                    usd_prev = float(gold["Close"].iloc[-2])
                else:
                    usd_prev = usd_today  # → avoids out-of-bounds, gives 0% change

                pct_change = (usd_today - usd_prev) / usd_prev * 100

                # USD → INR conversion
                fx = yf.Ticker("USDINR=X").history(period="5d")
                if fx is not None and not fx.empty:
                    usdinr = float(fx["Close"].iloc[-1])
                else:
                    usdinr = 83.0  # fallback

                # Convert USD/oz → INR per 10g
                inr_per_gram = (usd_today / 31.1035) * usdinr
                inr_10g = inr_per_gram * 10

                return inr_10g, pct_change

            except Exception as e:
                print("GOLD ERROR:", e)
                return None, None

        # ----------------------------------------------------
        # 2) CRUDE OIL (api-ninjas → cleaner + more reliable)
        # ----------------------------------------------------
        if ticker == "CRUDE_INR":
            try:
                crude = yf.Ticker("CL=F").history(period="1mo", interval="1d")

                if crude is None or crude.empty:
                    print("Crude history empty")
                    return None, None

                usd_today = float(crude["Close"].iloc[-1])

                if len(crude) > 1:
                    usd_prev = float(crude["Close"].iloc[-2])
                else:
                    usd_prev = usd_today

                pct_change = (usd_today - usd_prev) / usd_prev * 100

                # USDINR
                fx = yf.Ticker("USDINR=X").history(period="5d")
                if fx is None or fx.empty:
                    usdinr = 83.0
                else:
                    usdinr = float(fx["Close"].iloc[-1])

                # Convert crude USD/barrel → INR/barrel
                inr_price = usd_today * usdinr

                return inr_price, pct_change

            except Exception as e:
                print("CRUDE ERROR:", e)
                return None, None

        # ----------------------------------------------------
        # 3) ALL OTHER MACROS → Yahoo Finance
        # ----------------------------------------------------
        data = yf.Ticker(ticker).history(period="5d")

        if data is None or data.empty:
            return None, None

        last = float(data["Close"].iloc[-1])

        if len(data) > 1:
            prev = float(data["Close"].iloc[-2])
        else:
            prev = last  # → avoid crash

        pct = (last - prev) / prev * 100

        return last, pct

    except Exception as e:
        print("MACRO ERROR:", ticker, e)
        return None, None


# ---------------------------------------------------------
# MACRO SUMMARY HELPERS
# ---------------------------------------------------------
def get_last_change(ticker):
    """
    Fetch last 2 closes and compute % change.
    """
    try:
        data = yf.Ticker(ticker).history(period="3d")
        if len(data) < 2:
            return None, None, None

        last = float(data["Close"].iloc[-1])
        prev = float(data["Close"].iloc[-2])
        pct = (last - prev) / prev * 100
        return last, prev, pct
    except:
        return None, None, None


def build_clean_macro_snapshot(macro_dict):
    """
    Remove indicators where latest/previous are None.
    This prevents summary generation failure.
    """
    clean = {}
    for name, values in macro_dict.items():
        if not values:
            continue

        latest = values.get("latest")
        previous = values.get("previous")
        pct = values.get("pct_change")

        # Skip unusable entries
        if latest is None or previous is None:
            continue

        clean[name] = {
            "latest": latest,
            "previous": previous,
            "pct_change": pct
        }

    return clean



def generate_macro_summary(snapshot):
    """
    Uses LLM to generate a clean English summary.
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])

        prompt = f"""
You are a global macro strategist. Write a concise, high-quality daily macro summary.
Use ONLY the data below:

{snapshot}

Format the output as:
- Key movement
- Direction
- Impact on sentiment
- Risk-on/off tone
    
Keep the summary to 5–7 bullet points.
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message["content"]

    except Exception as e:
        print("Macro Summary Error:", e)
        return "Macro summary unavailable today."


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
# ---------------------------------------------------------
# DAILY MACRO SUMMARY SECTION
# ---------------------------------------------------------
st.markdown("<h3 style='color:white; margin-top:35px;'>📰 Daily Macro Summary</h3>", unsafe_allow_html=True)

# Select high-impact macros for summary
MACRO_SET = {
    "US 10Y Yield": "^TNX",
    "VIX": "^VIX",
    "Dollar Index (DXY)": "DX-Y.NYB",
    "Crude Oil": "CL=F",
    "Gold": "GC=F",
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX"
}

# Fetch last movements
snapshot = {}

for name, ticker in MACRO_SET.items():
    last, prev, pct = get_last_change(ticker)
    snapshot[name] = {
        "latest": last,
        "previous": prev,
        "pct_change": pct
    }
st.write("DEBUG SNAPSHOT:", snapshot)

# Generate AI summary
clean_snapshot = build_clean_macro_snapshot(macro_snapshot)

if not clean_snapshot:
    st.warning("Macro summary unavailable today.")
else:
    with st.spinner("Generating macro summary…"):
        summary = analyze_macro(clean_snapshot, api_key=st.secrets["openai"]["api_key"])
        st.markdown(summary)


# Display in neumorphic card (using your existing style)
st.markdown(
    f"""
    <div class="weather-card">
        <div style="text-align:left; color:white; font-size:16px;">
            {summary}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
