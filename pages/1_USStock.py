import streamlit as st
import pandas as pd
import yfinance as yf
from utils.portfolio_engine import read_google_sheet
from utils.llm_engine import analyze_thesis

st.set_page_config(page_title="US Stocks", layout="wide")

st.title("🇺🇸 US Stocks Portfolio")

# ------------------------------------------
# Load Data
# ------------------------------------------
df = read_google_sheet(st.secrets["google"]["sheet_id"])

# Filter only US stocks
df = df[df["country"].str.lower() == "us"]

# Ensure numeric columns
df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0)
df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce").fillna(0)

# ------------------------------------------
# Fetch Live Market Data
# ------------------------------------------
def get_live_fields(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.history(period="1y")

        current = info["Close"].iloc[-1]
        high_52 = info["High"].max()
        low_52 = info["Low"].min()

        return current, high_52, low_52
    except:
        return None, None, None


df["current_price"], df["52w_high"], df["52w_low"] = zip(
    *df["ticker"].apply(get_live_fields)
)

df["pnl_%"] = ((df["current_price"] - df["avg_price"]) / df["avg_price"]) * 100

# ------------------------------------------
# LLM Signal Generation
# ------------------------------------------
@st.cache_data(ttl=900)
def get_llm_signal(row):
    return analyze_thesis(
        asset=row["asset_name"],
        thesis=row["thesis"],
        price=row["current_price"],
        high52=row["52w_high"],
        low52=row["52w_low"]
    )

# ------------------------------------------
# Display Table
# ------------------------------------------
st.subheader("📊 Live Portfolio Overview")

display_df = df[[
    "asset_name",
    "ticker",
    "units",
    "avg_price",
    "current_price",
    "pnl_%",
    "52w_high",
    "52w_low",
    "thesis"
]].copy()

st.dataframe(display_df, use_container_width=True)

# ------------------------------------------
# Signals Section
# ------------------------------------------
st.subheader("🤖 AI Thesis Signals")

for idx, row in df.iterrows():
    st.markdown(f"### **{row['asset_name']} ({row['ticker']})**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Price", f"{row['current_price']:.2f}")

    with col2:
        st.metric("52W High", f"{row['52w_high']:.2f}")

    with col3:
        st.metric("52W Low", f"{row['52w_low']:.2f}")

    with st.spinner("Generating insights…"):
        signal = get_llm_signal(row)

    st.markdown(f"💡 **Signal:** {signal}")
    st.markdown("---")
