from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def analyze_thesis(asset, thesis, news, price, high52, low52):
    
    news_text = "\n".join([
        f"- {n.get('headline', '')}: {n.get('summary', '')}"
        for n in news
    ])[:4000]  # keep below token limit
    
    prompt = f"""
    You are an expert investment analyst.
    
    Asset: {asset}
    Current Price: {price}
    52W High: {high52}
    52W Low: {low52}

    Thesis:
    {thesis}

    News last 24 hours:
    {news_text}

    TASKS:
    1. Tell me if anything in the news weakens or strengthens the thesis.
    2. State if the thesis is intact, weakening, or broken.
    3. Give a BUY / HOLD / AVOID decision.
    4. Provide a traffic light flag (GREEN/AMBER/RED).
    5. Provide a 2-line summary insight.
    """

    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.choices[0].message.content
