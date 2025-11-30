import streamlit as st
import pandas as pd
import yfinance as yf
from utils.portfolio_engine import read_google_sheet
from utils.llm_engine import analyze_thesis

st.set_page_config(page_title="US Stocks", layout="wide")

st.title("🇺🇸 US Stocks Portfolio")

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
df = read_google_sheet(st.secrets["google"]["sheet_id"])

# Keep only US stocks
df = df[df["country"].str.lower() == "us"].copy()

# Ensure numeric
df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0)
df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce").fillna(0)

# ---------------------------------------------------------
# Fetch live prices + 52W High/Low
# ---------------------------------------------------------
def get_live_fields(ticker: str):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")

        if hist.empty:
            return None, None, None

        current = float(hist["Close"].iloc[-1])
        high52 = float(hist["High"].max())
        low52 = float(hist["Low"].min())

        return current, high52, low52
    except Exception:
        return None, None, None


df["current_price"], df["52w_high"], df["52w_low"] = zip(
    *df["ticker"].apply(get_live_fields)
)

df["pnl_%"] = (
    (df["current_price"] - df["avg_price"]) / df["avg_price"] * 100
).replace([float("inf"), -float("inf")], 0).fillna(0)

# ---------------------------------------------------------
# LLM Wrapper (cached)
# ---------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def get_llm_signal(row_dict):
    """
    Provide row as dict to avoid parameter mismatch.
    Calls analyze_thesis() from llm_engine.py.
    """
    return analyze_thesis(
        asset=row_dict["asset_name"],
        ticker=row_dict["ticker"],
        thesis=row_dict.get("thesis", ""),
        units=float(row_dict.get("units", 0)),
        avg_price=float(row_dict.get("avg_price", 0)),
        price=float(row_dict.get("current_price", 0)) if row_dict.get("current_price") else None,
        high52=float(row_dict.get("52w_high", 0)) if row_dict.get("52w_high") else None,
        low52=float(row_dict.get("52w_low", 0)) if row_dict.get("52w_low") else None,
    )

# ---------------------------------------------------------
# Display Portfolio Table
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# AI Thesis Signal Section
# ---------------------------------------------------------
st.subheader("🤖 AI Thesis Reviews")

for idx, row in df.iterrows():
    st.markdown(f"### **{row['asset_name']} ({row['ticker']})**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Price", f"{row['current_price']:.2f}" if row["current_price"] else "—")

    with col2:
        st.metric("52W High", f"{row['52w_high']:.2f}" if row["52w_high"] else "—")

    with col3:
        st.metric("52W Low", f"{row['52w_low']:.2f}" if row["52w_low"] else "—")

    with col4:
        st.metric("PnL %", f"{row['pnl_%']:.1f}%" if row["pnl_%"] else "—")

    # Run LLM
    with st.spinner("Generating AI insight…"):
        signal = get_llm_signal(row.to_dict())

    # The new analyze_thesis returns CLEAN MARKDOWN text
    st.markdown(signal)

    st.markdown("---")
