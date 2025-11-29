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
def get_live_fields(ticker: str):
    try:
        t = yf.Ticker(ticker)
        info = t.history(period="1y")

        if info.empty:
            return None, None, None

        current = float(info["Close"].iloc[-1])
        high_52 = float(info["High"].max())
        low_52 = float(info["Low"].min())

        return current, high_52, low_52
    except Exception:
        return None, None, None


df["current_price"], df["52w_high"], df["52w_low"] = zip(
    *df["ticker"].apply(get_live_fields)
)

df["pnl_%"] = (
    (df["current_price"] - df["avg_price"]) / df["avg_price"] * 100
).replace([float("inf"), -float("inf")], 0)

# ------------------------------------------
# LLM Signal Generation
# ------------------------------------------
@st.cache_data(ttl=900)
def get_llm_signal(row):
    return analyze_thesis(
        asset=row["asset_name"],
        ticker=row["ticker"],
        thesis=row["thesis"],
        units=float(row["units"]),
        avg_price=float(row["avg_price"]),
        price=float(row["current_price"]),
        high52=float(row["52w_high"]),
        low52=float(row["52w_low"]),
        api_key=st.secrets["openai"]["api_key"],
    ):
    """
    Wraps analyze_thesis so it can use all key inputs.
    Expected to return a dict:
    {
      "action": "Buy/Hold/Trim/Exit",
      "commentary": "...",
      "thesis_update": "...",
      "signals_to_monitor": [...]
    }
    """
    return analyze_thesis(
        asset=asset_name,
        ticker=ticker,
        thesis=thesis,
        units=float(units),
        avg_price=float(avg_price),
        price=float(current_price) if current_price is not None else None,
        high52=float(high_52) if high_52 is not None else None,
        low52=float(low_52) if low_52 is not None else None,
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if pd.notnull(row["current_price"]):
            st.metric("Current Price", f"{row['current_price']:.2f}")
        else:
            st.metric("Current Price", "—")

    with col2:
        if pd.notnull(row["52w_high"]):
            st.metric("52W High", f"{row['52w_high']:.2f}")
        else:
            st.metric("52W High", "—")

    with col3:
        if pd.notnull(row["52w_low"]):
            st.metric("52W Low", f"{row['52w_low']:.2f}")
        else:
            st.metric("52W Low", "—")

    with col4:
        if pd.notnull(row["pnl_%"]):
            st.metric("PnL %", f"{row['pnl_%']:.1f}%")
        else:
            st.metric("PnL %", "—")

    with st.spinner("Generating AI insight…"):
        signal = get_llm_signal(
            asset_name=row["asset_name"],
            ticker=row["ticker"],
            thesis=row.get("thesis", ""),
            units=row["units"],
            avg_price=row["avg_price"],
            current_price=row["current_price"],
            high_52=row["52w_high"],
            low_52=row["52w_low"],
        )

    # Handle both dict and plain-text fallback
    if isinstance(signal, dict):
        action = signal.get("action", "").strip()
        commentary = signal.get("commentary", "").strip()
        thesis_update = signal.get("thesis_update", "").strip()
        signals_to_monitor = signal.get("signals_to_monitor", []) or []

        # Action pill
        if action:
            st.markdown(f"**🧭 AI Action:** `{action}`")

        if commentary:
            st.markdown(f"💡 **Commentary:** {commentary}")

        if thesis_update:
            with st.expander("🔁 Suggested Thesis Update"):
                st.write(thesis_update)

        if signals_to_monitor:
            st.markdown("📌 **Signals to Monitor:**")
            for s in signals_to_monitor:
                st.markdown(f"- {s}")
    else:
        # Simple text signal from older analyze_thesis
        st.markdown(f"💡 **Signal:** {signal}")

    st.markdown("---")
