import streamlit as st
from openai import OpenAI
import time

# We DO NOT store OpenAI client globally (breaks Streamlit cache)

@st.cache_data(show_spinner=False)
def analyze_thesis(asset, ticker, price, high52, low52, api_key):
    """
    Streamlit-safe cached LLM function.
    All arguments must be serializable!!
    """
    prompt = f"""
    You are an investment analyst. Generate a concise thesis.

    Asset: {asset}
    Ticker: {ticker}
    Current Price: {price}
    52W High: {high52}
    52W Low: {low52}

    Provide:
    - Bull case (2 bullets)
    - Bear case (2 bullets)
    - Key risks (1–2 lines)
    - Suggested stance: BUY / HOLD / REDUCE
    """

    # Create OpenAI client inside function (safe)
    client = OpenAI(api_key=api_key)

    # retry logic
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",   # safer + higher rate limits
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message["content"]

        except Exception:
            time.sleep(2)

    # fallback result
    return "⚠️ Rate limit or API error. Try again in 30 sec."
