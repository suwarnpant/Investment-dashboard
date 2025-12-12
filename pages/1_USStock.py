import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from utils.portfolio_engine import read_google_sheet
from utils.llm_engine import analyze_thesis

# Optional – if you already set this in main app, you can remove this line
st.set_page_config(page_title="US Stocks", layout="wide")

st.title("🇺🇸 US Stock Equities")

# ---------------------------------------------------------
# 1. LOAD & PREPARE DATA
# ---------------------------------------------------------
df = read_google_sheet(st.secrets["google"]["sheet_id"])

# Filter only US stocks (assuming 'country' column holds 'US')
df = df[df["country"].str.lower() == "us"].copy()

if df.empty:
    st.warning("No US stocks found in your sheet. Check the 'country' column.")
    st.stop()

# Ensure numeric
df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0.0)
df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce").fillna(0.0)

# ---------------------------------------------------------
# 2. LIVE DATA: CURRENT PRICE + 52W HIGH/LOW (YFinance)
# ---------------------------------------------------------
def get_live_fields(ticker: str):
    """
    Returns (current_price, 52w_high, 52w_low) using last 1y of data.
    """
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if hist.empty:
            return None, None, None

        current = float(hist["Close"].iloc[-1])
        high_52 = float(hist["High"].max())
        low_52 = float(hist["Low"].min())
        return current, high_52, low_52
    except Exception:
        return None, None, None

df["current_price"], df["52w_high"], df["52w_low"] = zip(
    *df["ticker"].apply(get_live_fields)
)

# Compute PnL
df["position_invested"] = df["units"] * df["avg_price"]
df["position_value"] = df["units"] * df["current_price"].fillna(0.0)

# % PnL (handle divide-by-zero and None)
df["pnl_absolute"] = df["position_value"] - df["position_invested"]
df["pnl_pct"] = np.where(
    df["position_invested"] > 0,
    df["pnl_absolute"] / df["position_invested"] * 100,
    np.nan,
)

# Sort by portfolio weight (largest positions first)
df.sort_values("position_value", ascending=False, inplace=True)

# ---------------------------------------------------------
# 3. PORTFOLIO TABLE (TOP SECTION)
# ---------------------------------------------------------
st.subheader("📊 Current US Equity Portfolio")

portfolio_view = df[[
    "asset_name",
    "ticker",
    "units",
    "avg_price",
    "current_price",
    "position_invested",
    "position_value",
    "pnl_absolute",
    "pnl_pct",
    "52w_high",
    "52w_low",
    "thesis",
    "sector",
    "category"
]].copy()

portfolio_view.rename(columns={
    "asset_name": "Stock",
    "ticker": "Ticker",
    "units": "Units",
    "avg_price": "Avg Buy Price",
    "current_price": "Current Price",
    "position_invested": "Invested ($)",
    "position_value": "Current Value ($)",
    "pnl_absolute": "PnL ($)",
    "pnl_pct": "PnL (%)",
    "52w_high": "52W High",
    "52w_low": "52W Low",
    "thesis": "Thesis",
    "sector": "Sector",
    "category": "Category",
}, inplace=True)

# Summary metrics on top
total_invested = portfolio_view["Invested ($)"].sum()
total_value = portfolio_view["Current Value ($)"].sum()
total_pnl = total_value - total_invested
total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Invested", f"${total_invested:,.2f}")
c2.metric("Current Value", f"${total_value:,.2f}")
c3.metric("Total PnL ($)", f"${total_pnl:,.2f}")
c4.metric("Total PnL (%)", f"{total_pnl_pct:,.2f}%")

st.dataframe(
    portfolio_view.style.format({
        "Avg Buy Price": "{:.2f}",
        "Current Price": "{:.2f}",
        "Invested ($)": "{:.2f}",
        "Current Value ($)": "{:.2f}",
        "PnL ($)": "{:.2f}",
        "PnL (%)": "{:.2f}",
        "52W High": "{:.2f}",
        "52W Low": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ---------------------------------------------------------
# 4. LLM WRAPPER (CACHED) FOR THESIS VALIDATION
# ---------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def get_llm_signal(
    asset_name: str,
    ticker: str,
    thesis: str,
    units: float,
    avg_price: float,
    current_price: float | None,
    high_52: float | None,
    low_52: float | None,
):
    """
    Cached wrapper around analyze_thesis.
    Returns a markdown string with commentary + stance + signals.
    """
    return analyze_thesis(
        asset=asset_name,
        ticker=ticker,
        thesis=thesis or "",
        units=units,
        avg_price=avg_price,
        price=current_price if current_price is not None else 0.0,
        high52=high_52 if high_52 is not None else 0.0,
        low52=low_52 if low_52 is not None else 0.0,
        api_key=st.secrets["openai"]["api_key"],
    )

# ---------------------------------------------------------
# 5. DEEP-DIVE SECTION PER STOCK
# ---------------------------------------------------------
st.subheader("🔍 Deep Dive: Thesis Validation & Actions")

for _, row in df.iterrows():
    stock_title = f"{row['asset_name']} ({row['ticker']})"
    with st.expander(stock_title, expanded=False):
        top1, top2, top3, top4 = st.columns(4)

        with top1:
            st.metric(
                "Current Price",
                f"{row['current_price']:.2f}" if pd.notnull(row["current_price"]) else "—"
            )
        with top2:
            st.metric(
                "52W High",
                f"{row['52w_high']:.2f}" if pd.notnull(row["52w_high"]) else "—"
            )
        with top3:
            st.metric(
                "52W Low",
                f"{row['52w_low']:.2f}" if pd.notnull(row["52w_low"]) else "—"
            )
        with top4:
            st.metric(
                "Position PnL (%)",
                f"{row['pnl_pct']:.2f}%" if pd.notnull(row["pnl_pct"]) else "—"
            )

        # Show your existing thesis
        st.markdown("**Your Current Thesis**")
        st.write(row.get("thesis", "") or "_No thesis text captured yet._")

        # LLM analysis
        with st.spinner("Running AI thesis validation…"):
            llm_markdown = get_llm_signal(
                asset_name=row["asset_name"],
                ticker=row["ticker"],
                thesis=row.get("thesis", ""),
                units=float(row["units"]),
                avg_price=float(row["avg_price"]),
                current_price=float(row["current_price"]) if pd.notnull(row["current_price"]) else None,
                high_52=float(row["52w_high"]) if pd.notnull(row["52w_high"]) else None,
                low_52=float(row["52w_low"]) if pd.notnull(row["52w_low"]) else None,
            )

        st.markdown("---")
        st.markdown("### 🤖 AI View on This Position")
        st.markdown(llm_markdown)

st.markdown("---")
st.caption("LLM outputs are for decision support only, not investment advice.")
