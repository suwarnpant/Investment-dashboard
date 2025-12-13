import streamlit as st
from datetime import datetime, timezone
import time

from utils.portfolio_engine import read_google_sheet
from utils.news_engine import fetch_news_finnhub
from openai import OpenAI

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="News", layout="wide")
st.title("📰 Portfolio News — Key Headlines")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def _safe_ts(ts: int | float | None) -> str:
    try:
        if not ts:
            return ""
        # Finnhub returns unix seconds
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).astimezone().strftime("%d %b %H:%M")
    except Exception:
        return ""

def classify_headline(headline: str) -> str:
    """
    Simple keyword classifier for filtering.
    """
    h = (headline or "").lower()

    earnings_kw = ["earnings", "eps", "revenue", "guidance", "q1", "q2", "q3", "q4", "quarter", "results", "profit", "margin"]
    ma_kw = ["acquire", "acquisition", "merger", "buyout", "takeover", "deal", "stake", "invests in", "to buy", "sale"]
    reg_kw = ["regulator", "sec", "antitrust", "doj", "probe", "lawsuit", "ban", "sanction", "compliance", "fine", "policy", "tariff"]
    product_kw = ["launch", "unveil", "release", "product", "chip", "ai", "model", "vehicle", "ev", "software", "update", "partnership"]
    macro_kw = ["fed", "inflation", "rates", "yield", "oil", "gold", "dollar", "usd", "rupee", "macro", "economy", "recession", "cpi", "jobs"]
    legal_kw = ["court", "lawsuit", "settlement", "appeal", "injunction", "patent", "ip", "litigation"]

    def contains_any(words):
        return any(w in h for w in words)

    if contains_any(earnings_kw): return "Earnings"
    if contains_any(ma_kw):       return "M&A"
    if contains_any(reg_kw):      return "Regulation"
    if contains_any(product_kw):  return "Product"
    if contains_any(macro_kw):    return "Macro"
    if contains_any(legal_kw):    return "Legal"
    return "Other"


@st.cache_data(ttl=1800, show_spinner=False)
def load_portfolio(sheet_id: str):
    df = read_google_sheet(sheet_id)
    # Normalize columns we need
    if "ticker" not in df.columns:
        return None
    if "country" not in df.columns:
        df["country"] = ""
    if "asset_name" not in df.columns:
        df["asset_name"] = ""

    df["ticker"] = df["ticker"].fillna("").astype(str).str.strip()
    df["country"] = df["country"].fillna("").astype(str).str.strip().str.upper()
    df["asset_name"] = df["asset_name"].fillna("").astype(str).str.strip()

    df = df[df["ticker"] != ""].copy()
    return df


@st.cache_data(ttl=1200, show_spinner=False)
def fetch_portfolio_news(tickers: tuple[str, ...]):
    """
    Fetch per-ticker news, aggregate and dedupe.
    Returns list[dict] with keys: headline, source, datetime, url, ticker
    """
    all_news = []
    seen = set()

    for tkr in tickers:
        try:
            items = fetch_news_finnhub(tkr) or []
        except Exception:
            items = []

        for n in items:
            headline = (n.get("headline") or "").strip()
            url = (n.get("url") or "").strip()
            if not headline:
                continue

            # dedupe on headline (and url if present)
            key = (headline.lower(), url)
            if key in seen:
                continue
            seen.add(key)

            all_news.append({
                "headline": headline,
                "source": (n.get("source") or "").strip(),
                "datetime": n.get("datetime", 0),
                "url": url,
                "ticker": tkr
            })

    # sort most recent
    all_news.sort(key=lambda x: x.get("datetime", 0), reverse=True)
    return all_news


@st.cache_data(ttl=3600, show_spinner=False)
def ai_rank_and_summarize(headlines_block: str, api_key: str) -> dict:
    """
    LLM: pick most impactful + summary + what to watch
    Returns dict with keys: summary, impactful (list of strings), watch (list of strings)
    """
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a buy-side equity + macro analyst writing a tight morning news brief for a portfolio manager.

Given these portfolio-linked headlines (most recent first), do:

A) "Most impactful today" — pick the 5 headlines that matter most (market-moving / thesis-relevant).
B) "Daily summary" — 1 short paragraph synthesizing what today’s news implies (risk-on/off, sector themes).
C) "What to watch" — 5 bullets: concrete things to monitor today (earnings, guidance, regulatory steps, launches, macro prints).

Rules:
- Use ONLY what is implied by the headlines (no made-up facts).
- Be crisp, institutional tone.
- Output strictly as JSON with keys: summary (string), impactful (array of strings), watch (array of strings).

HEADLINES:
{headlines_block}
""".strip()

    # retry to reduce rate-limit failures
    for _ in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            txt = resp.choices[0].message.content.strip()

            # very lightweight JSON extraction (avoid extra deps)
            # If model returns fenced JSON, strip fences.
            if txt.startswith("```"):
                txt = txt.replace("```json", "").replace("```", "").strip()

            import json
            return json.loads(txt)

        except Exception:
            time.sleep(1.5)

    return {
        "summary": "⚠️ AI summary unavailable right now (rate limit or network).",
        "impactful": [],
        "watch": []
    }


# ---------------------------------------------------------
# UI CONTROLS
# ---------------------------------------------------------
df = load_portfolio(st.secrets["google"]["sheet_id"])
if df is None or df.empty:
    st.warning("No portfolio tickers found. Ensure your sheet has a 'ticker' column filled.")
    st.stop()

# Country sets (expects US / IND)
us_df = df[df["country"].isin(["US", "USA"])].copy()
ind_df = df[df["country"].isin(["IND", "IN", "INDIA"])].copy()

tab_all, tab_us, tab_ind = st.tabs(["All", "US", "India"])

filters = ["Earnings", "M&A", "Regulation", "Product", "Macro", "Legal", "Other"]

with st.sidebar:
    st.subheader("Filters")
    selected_filters = st.multiselect(
        "Headline categories",
        options=filters,
        default=filters,
    )
    max_headlines = st.slider("Max headlines", 5, 50, 20, 5)

    st.divider()
    st.subheader("AI Brief")
    run_ai = st.checkbox("Generate AI brief (Most impactful + summary + what to watch)", value=True)
    st.caption("Uses your OpenAI API key from secrets. Cached for 1 hour.")

def render_news(feed_df, label: str):
    tickers = tuple(feed_df["ticker"].unique().tolist())
    if not tickers:
        st.info(f"No tickers found for {label}.")
        return

    with st.spinner("Fetching news…"):
        news = fetch_portfolio_news(tickers)

    if not news:
        st.info("No major portfolio-linked news found (last 24–48 hours).")
        return

    # attach category + map to portfolio asset name
    tkr_to_name = dict(zip(feed_df["ticker"], feed_df["asset_name"]))
    for n in news:
        n["category"] = classify_headline(n["headline"])
        n["asset_name"] = tkr_to_name.get(n["ticker"], n["ticker"])

    # filter
    news = [n for n in news if n["category"] in selected_filters]

    if not news:
        st.info("No headlines match your selected filters.")
        return

    # limit to max_headlines
    news = news[:max_headlines]

    # ---------------------------------------------------------
    # AI BRIEF (top area)
    # ---------------------------------------------------------
    if run_ai:
        # feed up to 40 lines to AI for ranking; still show only max_headlines
        ai_input = "\n".join([f"- {n['headline']}" for n in news[:40]])
        ai = ai_rank_and_summarize(ai_input, st.secrets["openai"]["api_key"])

        # Beautiful “brief” card
        st.markdown(
            """
            <style>
            .brief-card{
                padding: 18px;
                border-radius: 18px;
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🧠 AI Brief")
        st.markdown(f"<div class='brief-card'>{ai.get('summary','')}</div>", unsafe_allow_html=True)

        impactful = ai.get("impactful") or []
        watch = ai.get("watch") or []

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🔥 Most impactful today")
            if impactful:
                for h in impactful[:5]:
                    st.write(f"- {h}")
            else:
                st.caption("—")

        with c2:
            st.markdown("#### 👀 What to watch")
            if watch:
                for w in watch[:5]:
                    st.write(f"- {w}")
            else:
                st.caption("—")

        st.markdown("---")

    # ---------------------------------------------------------
    # HEADLINES LIST (clean, key-only)
    # ---------------------------------------------------------
    st.markdown(f"### 🗞️ Top {len(news)} headlines ({label})")
    st.caption("Headline · Source · Time · Tag · Linked holding")

    for i, n in enumerate(news, start=1):
        ts = _safe_ts(n.get("datetime"))
        src = n.get("source", "")
        cat = n.get("category", "Other")
        url = n.get("url", "")
        holding = n.get("asset_name", n.get("ticker", ""))

        st.markdown(
            f"""
**{i}. {n['headline']}**  
<small>{src} · {ts} · <b>{cat}</b> · <i>{holding} ({n['ticker']})</i></small>  
{f"[Read more]({url})" if url else ""}
""",
            unsafe_allow_html=True
        )
        st.markdown("---")


with tab_all:
    render_news(df, "All Portfolio")

with tab_us:
    render_news(us_df, "US Portfolio")

with tab_ind:
    render_news(ind_df, "India Portfolio")
