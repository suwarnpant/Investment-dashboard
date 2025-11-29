import streamlit as st
from utils.portfolio_engine import read_google_sheet, calculate_portfolio

st.set_page_config(layout="wide")

st.title("📘 Portfolio Overview")

df = read_google_sheet(st.secrets["google"]["sheet_id"])
df = calculate_portfolio(df)

st.dataframe(df)

total_value = df['current_value'].sum()
total_pnl = df['pnl'].sum()

st.metric("Total Portfolio Value", f"${total_value:,.2f}")
st.metric("Total P/L", f"${total_pnl:,.2f}")

st.autorefresh(interval=900000)  # 15 mins
