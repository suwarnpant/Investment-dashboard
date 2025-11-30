import streamlit as st
from openai import OpenAI
import time

# ---------------------------------------------------------
# LLM ANALYSIS ENGINE (Streamlit-cache safe)
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def analyze_thesis(asset, ticker, thesis, units, avg_price, price, high52, low52):
    """
    AI-based thesis review for your portfolio.
    Cached for performance. All arguments must be serializable.
    """

    # Safety for empty thesis
    if thesis is None or str(thesis).strip() == "":
        thesis = "No thesis provided."

    # Strong improved prompt (based on your latest instructions)
    prompt = f"""
You are my personal investment analyst. Evaluate this position logically and concisely.

ASSET: {asset}
TICKER: {ticker}
UNITS HELD: {units}
AVERAGE BUY PRICE: {avg_price}
CURRENT PRICE: {price}
52W HIGH: {high52}
52W LOW: {low52}

CURRENT THESIS:
{thesis}

TASK:
1. **Commentary** (3–4 sentences)  
   - Does the thesis broadly still hold?  
   - Evaluate valuation vs my buy level and vs the 52W range.

2. **Thesis Update Suggestions**  
   Give 3–5 bullet points on how the thesis should evolve  
   (risks, catalysts, competitive changes, macro effects).

3. **Action Signal (VERY IMPORTANT)**  
   Output a single tag in ALL CAPS:  
   **ACCUMULATE / HOLD / TRIM / EXIT**  
   + A one-sentence justification.

4. **Signals to Monitor (3–5 bullets)**  
   Specific KPIs, catalysts, red flags or data points  
   that could strengthen or break the thesis.

Be concise. Respond only in clean markdown using sections:

### Commentary
### Suggested changes
### Stance
### Signals to monitor
    """

    # Initialize OpenAI client — do NOT store globally
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])

    # Retry logic (stable for Streamlit Cloud)
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-5",   # You asked to use “current model”
                messages=[{"role": "user", "content": prompt}]
            )
            # Clean extraction
            return response.choices[0].message["content"]

        except Exception as e:
            print("LLM ERROR:", e)
            time.sleep(2)

    # Final fallback
    return "⚠️ LLM temporarily unavailable. Please retry in 30 seconds."
