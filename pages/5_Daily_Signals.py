import streamlit as st
from utils.portfolio_engine import read_google_sheet, calculate_portfolio
from utils.news_engine import fetch_news_finnhub
from utils.llm_engine import analyze_thesis

st.title("🚦 Daily Signals")

df = calculate_portfolio(read_google_sheet(st.secrets["google"]["sheet_id"]))

signals = []

for _, row in df.iterrows():
    news = fetch_news_finnhub(row['ticker'])
    analysis = analyze_thesis(
        asset=row['asset_name'],
        thesis=row['thesis'],
        news=news,
        price=row['current_price'],
        high52=row['52w_high'],
        low52=row['52w_low']
    )
    signals.append((row['asset_name'], analysis))

for name, signal in signals:
    st.subheader(name)
    st.write(signal)
    st.write("---")

st.autorefresh(interval=900000)
