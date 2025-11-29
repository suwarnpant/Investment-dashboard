import streamlit as st
from utils.portfolio_engine import read_google_sheet, calculate_portfolio
from utils.news_engine import fetch_news_finnhub
from utils.llm_engine import analyze_thesis

st.title("📗 Asset Details + AI Insights")

df = calculate_portfolio(read_google_sheet(st.secrets["google"]["sheet_id"]))

asset_list = df['asset_name'].tolist()
selected = st.selectbox("Select an asset", asset_list)

row = df[df['asset_name'] == selected].iloc[0]

st.subheader(f"{selected}")
st.write(row)

news = fetch_news_finnhub(row['ticker'])

analysis = analyze_thesis(
    asset=row['asset_name'],
    thesis=row['thesis'],
    news=news,
    price=row['current_price'],
    high52=row['52w_high'],
    low52=row['52w_low']
)

st.subheader("AI Thesis Analysis")
st.write(analysis)

st.autorefresh(interval=900000)
