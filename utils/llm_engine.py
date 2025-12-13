import time
from openai import OpenAI


def analyze_thesis(
    asset: str,
    ticker: str,
    thesis: str,
    units: float,
    avg_price: float,
    price: float,
    high52: float,
    low52: float,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Calls OpenAI to evaluate your thesis.
    Returns markdown string.
    NOTE: Keep this function NON-cached; cache it at the page level.
    """

    thesis = (thesis or "").strip() or "No thesis provided."

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
1) **Commentary** (3–4 sentences)
   - Does the thesis broadly still hold?
   - Evaluate current price vs my buy level and vs the 52W range.

2) **Thesis Update Suggestions**
   Provide 3–5 bullets to refine the thesis (risks, catalysts, competition, macro).

3) **Action Signal**
   Output exactly ONE tag in ALL CAPS:
   **ACCUMULATE / HOLD / TRIM / EXIT**
   + one-sentence justification.

4) **Signals to Monitor**
   3–5 specific KPIs, events, red flags, or datapoints that confirm/break the thesis.

Return ONLY clean markdown with these headings:

### Commentary
### Suggested changes
### Stance
### Signals to monitor
""".strip()

    client = OpenAI(api_key=api_key)

    # Exponential backoff for rate limits / transient errors
    last_err = None
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content

        except Exception as e:
            last_err = e
            # backoff: 1.5s, 3s, 6s, 12s, 24s
            time.sleep(1.5 * (2 ** attempt))

    return f"⚠️ LLM temporarily unavailable. Last error: {last_err}"
