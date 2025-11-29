import streamlit as st
from utils.portfolio_engine import read_google_sheet
from utils.news_engine import fetch_news_finnhub

st.title("📰 News Summary")

df = read_google_sheet(st.secrets["google"]["sheet_id"])

for _, row in df.iterrows():
    st.subheader(row['asset_name'])
    news = fetch_news_finnhub(row['ticker'])

    if not news:
        st.write("No news in last 24 hours.")
        continue

    for n in news[:5]:
        st.write(f"**{n['headline']}**")
        st.write(n.get('summary', ''))
        st.write("---")

st.autorefresh(interval=900000)
