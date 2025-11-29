import streamlit as st
import pandas as pd
from utils.portfolio_engine import read_google_sheet, calculate_portfolio
from utils.news_engine import fetch_news_finnhub
from utils.llm_engine import analyze_thesis

st.title("📊 Asset Breakdown")

df = calculate_portfolio(read_google_sheet(st.secrets["google"]["sheet_id"]))

asset_list = df['asset_name'].tolist()
selected = st.selectbox("Select an asset", asset_list)

row = df[df['asset_name'] == selected].iloc[0]

st.subheader(selected)
st.write(row)

news = fetch_news_finnhub(row['ticker'])

with st.spinner("Analyzing investment thesis..."):
    analysis = analyze_thesis(
        asset=row['asset_name'],
        ticker=row['ticker'],
        price=row['price'],
        high52=row['52w_high'],
        low52=row['52w_low'],
        api_key=st.secrets["openai"]["api_key"]   # REQUIRED FIX
    )

st.markdown("### 🧠 Investment Thesis")
st.write(analysis)
