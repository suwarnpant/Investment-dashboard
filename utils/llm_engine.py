import streamlit as st
from openai import OpenAI
import time

# We DO NOT store OpenAI client globally (breaks Streamlit cache)

@st.cache_data(show_spinner=False)
def analyze_thesis(asset, ticker, thesis, units, avg_price, price, high52, low52, api_key):
    """
    Streamlit-safe cached LLM function.
    All arguments must be serializable!!
    Returns: markdown string with commentary + stance + signals.
    """
    prompt = f"""
You are an investment analyst. Critically review my current stock thesis and position.

Asset: {asset}
Ticker: {ticker}
Units held: {units}
Average buy price: {avg_price}
Current price: {price}
52W High: {high52}
52W Low: {low52}
Current thesis: "{thesis}"

Please provide:

1. Commentary (3–4 lines) – Does the thesis still broadly hold at the current price? 
   Comment on valuation vs my buy level and the 52W range.
2. Suggested thesis changes (3–5 bullet points) – How should I update/refine my thesis 
   in light of recent developments, risks or competitive shifts?
3. Stance – One clear tag in ALL CAPS: BUY / HOLD / TRIM / EXIT, plus one short 
   sentence of justification.
4. Signals to monitor – 3–5 specific data points, KPIs or events that would either 
   confirm or break the thesis.

Respond in clean markdown, using sections:

- Commentary
- Suggested changes
- Stance
- Signals to monitor
""".strip()

    # Create OpenAI client inside function (safe for Streamlit)
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
