import streamlit as st
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

@st.cache_data(show_spinner=False)
def analyze_thesis(asset, ticker, price, high52, low52):
    prompt = f"""
    You are an investment analyst.
    Create a short thesis for the stock below:

    Asset: {asset}
    Ticker: {ticker}
    Current Price: {price}
    52W High: {high52}
    52W Low: {low52}

    Provide:
    - Bull case (2 bullets)
    - Bear case (2 bullets)
    - Key risks (1–2 lines)
    - Whether long-term investors should BUY / HOLD / AVOID
    """

    # retry logic
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.choices[0].message["content"]

        except Exception as e:
            time.sleep(2)
    
    return "Rate-limit hit. Please try again in a few seconds."
