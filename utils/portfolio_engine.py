import json
import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from .market_data import get_stock_price, get_crypto_price


def _get_gsheet_client():
    """Authorize and return a gspread client using the service account JSON in st.secrets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # service_account_json is stored as a JSON string in secrets
    sa_json_str = st.secrets["google"]["service_account_json"]
    sa_info = json.loads(sa_json_str)

    creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scope)
    client = gspread.authorize(creds)
    return client


def read_google_sheet(sheet_id: str) -> pd.DataFrame:
    """Read the first worksheet from the given Google Sheet ID."""
    client = _get_gsheet_client()
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def calculate_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """Add live prices, 52w range, value and P&L to the portfolio DataFrame."""

    # make sure numeric
    df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0.0)
    df["avg_price"] = pd.to_numeric(df["avg_price"], errors="coerce").fillna(0.0)

    prices = []
    highs = []
    lows = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        category = str(row["category"]).lower()

        if category == "crypto":
            price = get_crypto_price(ticker)
            high, low = None, None
        else:
            price, high, low = get_stock_price(ticker)

        prices.append(price)
        highs.append(high)
        lows.append(low)

    df["current_price"] = prices
    df["52w_high"] = highs
    df["52w_low"] = lows

    df["current_value"] = df["current_price"] * df["units"]
    df["pnl"] = (df["current_price"] - df["avg_price"]) * df["units"]

    return df
