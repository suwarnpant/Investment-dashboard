import time
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from utils.portfolio_engine import read_google_sheet
from utils.llm_engine import analyze_thesis


st.set_page_config(page_title="US Stocks", layout="wide")
st.title("🇺🇸 US Stock Equities")


# ---------------------------------------------------------
# 1) LOAD & VALIDATE DATA
# ---------------------------------------------------------
df = read_google_sheet(st.secrets["google"]["sheet_id"])

required = ["asset_name", "ticker", "category", "units", "avg_price", "thesis", "sector", "country"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing required column(s) in sheet: {', '.join(missing)}")
    st.stop()

df = df.copy()
df["country"] = df["country"].fillna("").astype(str)
df["ticker"] = df["ticker"].fillna("").astype(str).str.strip()
df["asset_name"] = df["asset_name"].fillna("").astype(str)
df["thesis"] = df["thesis"].fillna("").astype(str)
df["sector"] = df["sector"].fillna("").astype(str)
df["category"] = df["category"].fillna("").astype(str)

df = df[df["country"].str.strip().str.lower() == "us"].copy()
df = df[df["ticker"] != ""].copy()

if df.empty:
    st.warning("No US stocks found. Check 'country' == 'US' and tickers are filled.")
    st.stop()

df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0.0)
df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce").fillna(0.0)


# ---------------------------------------------------------
# 2) LIVE DATA (YFINANCE) — cached
# ---------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def get_live_fields(ticker: str):
    """
    Returns (current_price, 52w_high, 52w_low) using last 1y of data.
    """
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if hist is None or hist.empty:
            return None, None, None
        current = float(hist["Close"].iloc[-1])
        high_52 = float(hist["High"].max())
        low_52 = float(hist["Low"].min())
        return current, high_52, low_52
    except Exception:
        return None, None, None


@st.cache_data(ttl=900, show_spinner=False)
def get_day_change_pct(ticker: str):
    """
    Returns (day_change_pct, last_close, prev_close) based on last 2 daily closes.
    """
    try:
        h = yf.Ticker(ticker).history(period="5d", interval="1d")
        if h is None or h.empty or len(h) < 2:
            return None, None, None
        last = float(h["Close"].iloc[-1])
        prev = float(h["Close"].iloc[-2])
        if prev == 0:
            return None, last, prev
        pct = (last - prev) / prev * 100
        return pct, last, prev
    except Exception:
        return None, None, None


df["current_price"], df["52w_high"], df["52w_low"] = zip(*df["ticker"].apply(get_live_fields))
df["day_change_pct"], df["last_close"], df["prev_close"] = zip(*df["ticker"].apply(get_day_change_pct))


# ---------------------------------------------------------
# 3) PORTFOLIO METRICS
# ---------------------------------------------------------
df["position_invested"] = df["units"] * df["avg_price"]
df["position_value"] = df["units"] * df["current_price"].fillna(0.0)

df["pnl_absolute"] = df["position_value"] - df["position_invested"]
df["pnl_pct"] = np.where(
    df["position_invested"] > 0,
    (df["pnl_absolute"] / df["position_invested"]) * 100,
    np.nan,
)

total_value = float(df["position_value"].sum())
df["weight_pct"] = np.where(total_value > 0, df["position_value"] / total_value * 100, np.nan)

df.sort_values("position_value", ascending=False, inplace=True)


# ---------------------------------------------------------
# 4) TOP MOVERS
# ---------------------------------------------------------
st.subheader("⚡ Top Movers (last close vs previous close)")

movers = df[["asset_name", "ticker", "day_change_pct"]].copy()
movers = movers[pd.notnull(movers["day_change_pct"])].copy()

if movers.empty:
    st.caption("No mover data available right now (Yahoo may have returned empty).")
else:
    top_gainers = movers.sort_values("day_change_pct", ascending=False).head(3)
    top_losers = movers.sort_values("day_change_pct", ascending=True).head(3)

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Top Gainers**")
        for _, r in top_gainers.iterrows():
            st.write(f"▲ **{r['asset_name']} ({r['ticker']})** — {r['day_change_pct']:+.2f}%")

    with g2:
        st.markdown("**Top Losers**")
        for _, r in top_losers.iterrows():
            st.write(f"▼ **{r['asset_name']} ({r['ticker']})** — {r['day_change_pct']:+.2f}%")


st.markdown("---")


# ---------------------------------------------------------
# 5) PORTFOLIO TABLE
# ---------------------------------------------------------
st.subheader("📊 Current US Equity Portfolio")

portfolio_view = df[[
    "asset_name", "ticker", "units", "avg_price", "current_price",
    "position_invested", "position_value", "weight_pct",
    "pnl_absolute", "pnl_pct", "day_change_pct",
    "52w_high", "52w_low",
    "thesis", "sector", "category"
]].copy()

portfolio_view.rename(columns={
    "asset_name": "Stock",
    "ticker": "Ticker",
    "units": "Units",
    "avg_price": "Avg Buy Price",
    "current_price": "Current Price",
    "position_invested": "Invested ($)",
    "position_value": "Current Value ($)",
    "weight_pct": "Weight (%)",
    "pnl_absolute": "PnL ($)",
    "pnl_pct": "PnL (%)",
    "day_change_pct": "Day Chg (%)",
    "52w_high": "52W High",
    "52w_low": "52W Low",
    "thesis": "Thesis",
    "sector": "Sector",
    "category": "Category",
}, inplace=True)

total_invested = float(portfolio_view["Invested ($)"].sum())
total_value = float(portfolio_view["Current Value ($)"].sum())
total_pnl = total_value - total_invested
total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Invested", f"${total_invested:,.2f}")
c2.metric("Current Value", f"${total_value:,.2f}")
c3.metric("Total PnL ($)", f"${total_pnl:,.2f}")
c4.metric("Total PnL (%)", f"{total_pnl_pct:,.2f}%")
c5.metric("Positions", f"{len(portfolio_view)}")

st.dataframe(
    portfolio_view.style.format({
        "Avg Buy Price": "{:.2f}",
        "Current Price": "{:.2f}",
        "Invested ($)": "{:.2f}",
        "Current Value ($)": "{:.2f}",
        "Weight (%)": "{:.2f}",
        "PnL ($)": "{:.2f}",
        "PnL (%)": "{:.2f}",
        "Day Chg (%)": "{:.2f}",
        "52W High": "{:.2f}",
        "52W Low": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")


# ---------------------------------------------------------
# 6) AI — SINGLE BUTTON ONLY (SESSION STORAGE)
# ---------------------------------------------------------
st.subheader("🤖 AI Thesis Validation")

if "ai_results" not in st.session_state:
    st.session_state["ai_results"] = {}  # ticker -> markdown

OPENAI_KEY = st.secrets["openai"]["api_key"]

@st.cache_data(ttl=3600, show_spinner=False)
def get_llm_signal_cached(
    asset_name: str,
    ticker: str,
    thesis: str,
    units: float,
    avg_price: float,
    current_price: float,
    high_52: float,
    low_52: float,
    api_key: str,
):
    return analyze_thesis(
        asset=asset_name,
        ticker=ticker,
        thesis=thesis or "",
        units=float(units),
        avg_price=float(avg_price),
        price=float(current_price),
        high52=float(high_52),
        low52=float(low_52),
        api_key=api_key,
        model="gpt-4o-mini",   # same as Home (more stable than gpt-5 for rate limits)
    )

run_all = st.button("🚀 Generate AI for ALL (throttled)")

st.caption("Runs sequentially with delays. Results are stored for this session (and cached for 1 hour).")

if run_all:
    progress = st.progress(0)
    status = st.empty()

    rows = df.reset_index(drop=True)
    n = len(rows)

    for i, row in rows.iterrows():
        ticker = str(row["ticker"])
        asset = str(row["asset_name"])

        status.write(f"Generating AI: **{asset} ({ticker})**  ({i+1}/{n})")

        cur = row["current_price"]
        h52 = row["52w_high"]
        l52 = row["52w_low"]

        if pd.isnull(cur) or pd.isnull(h52) or pd.isnull(l52):
            st.session_state["ai_results"][ticker] = "⚠️ Live price/52W data missing (yfinance empty)."
        else:
            try:
                md = get_llm_signal_cached(
                    asset_name=asset,
                    ticker=ticker,
                    thesis=str(row.get("thesis", "")),
                    units=float(row["units"]),
                    avg_price=float(row["avg_price"]),
                    current_price=float(cur),
                    high_52=float(h52),
                    low_52=float(l52),
                    api_key=OPENAI_KEY,
                )
                st.session_state["ai_results"][ticker] = md
            except Exception as e:
                st.session_state["ai_results"][ticker] = f"⚠️ AI call failed (rate limit / network). {e}"

        progress.progress(int((i + 1) / n * 100))
        time.sleep(1.4)  # throttle (slightly higher to reduce rate-limit bursts)

    status.success("Done. Expand each stock below to view the AI output.")

st.markdown("---")


# ---------------------------------------------------------
# 7) DEEP DIVE PER STOCK (NO PER-STOCK BUTTON)
# ---------------------------------------------------------
st.subheader("🔍 Deep Dive: Per Stock")

for _, row in df.reset_index(drop=True).iterrows():
    asset = row["asset_name"]
    ticker = row["ticker"]
    title = f"{asset} ({ticker})"

    with st.expander(title, expanded=False):
        top1, top2, top3, top4, top5 = st.columns(5)

        cur = row["current_price"]
        h52 = row["52w_high"]
        l52 = row["52w_low"]
        pnlp = row["pnl_pct"]
        wgt = row["weight_pct"]

        top1.metric("Current Price", f"{cur:.2f}" if pd.notnull(cur) else "—")
        top2.metric("52W High", f"{h52:.2f}" if pd.notnull(h52) else "—")
        top3.metric("52W Low", f"{l52:.2f}" if pd.notnull(l52) else "—")
        top4.metric("PnL (%)", f"{pnlp:.2f}%" if pd.notnull(pnlp) else "—")
        top5.metric("Weight (%)", f"{wgt:.2f}%" if pd.notnull(wgt) else "—")

        st.markdown("**Your Current Thesis**")
        st.write(row.get("thesis", "") or "_No thesis text captured yet._")

        if ticker in st.session_state["ai_results"]:
            st.markdown("### 🤖 AI View on This Position")
            st.markdown(st.session_state["ai_results"][ticker])
        else:
            st.caption("No AI output yet. Click **Generate AI for ALL** above.")

st.markdown("---")
st.caption("LLM outputs are for decision support only, not investment advice.")
