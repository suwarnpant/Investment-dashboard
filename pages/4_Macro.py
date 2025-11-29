import streamlit as st
from utils.macro_engine import fetch_macro

st.title("🌍 Macro Dashboard")

macro = fetch_macro()

for k, v in macro.items():
    st.metric(k, v)

st.autorefresh(interval=900000)
