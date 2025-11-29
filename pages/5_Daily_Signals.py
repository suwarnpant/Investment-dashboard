import streamlit as st
from utils.portfolio_engine import read_google_sheet
from utils.llm_engine import analyze_thesis
import yfinance as yf

st.title("📊 Daily AI Signals")

# Load portfolio
df = read_google_sheet(st.secrets["google"]["sheet_id"])

for _, row in df.iterrows():

    asset = row.get("asset_name", "Unnamed Asset")
    ticker = row.get("ticker", None)

    st.subheader(f"📌 {asset}")

    if not ticker:
        st.warning("No ticker found, skipping.")
        continue

    # ---- Fetch live market data ----
    try:
        y = yf.Ticker(ticker)
        info = y.info

        current_price = info.get("currentPrice", 0)
        high52 = info.get("fiftyTwoWeekHigh", 0)
        low52 = info.get("fiftyTwoWeekLow", 0)
    except Exception as e:
        st.error(f"Price fetch failed: {e}")
        current_price = high52 = low52 = 0

    # ---- AI Signal ----
    with st.spinner("Generating AI signal..."):
        analysis = analyze_thesis(
            asset=asset,
            ticker=ticker,
            price=current_price,
            high52=high52,
            low52=low52,
            api_key=st.secrets["openai"]["api_key"]
        )

    st.write(analysis)
    st.divider()
