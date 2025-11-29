import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .market_data import get_stock_price, get_crypto_price

def read_google_sheet(sheet_id):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["google"]["service_account_json"],
        scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def calculate_portfolio(df):
    prices = []
    highs = []
    lows = []

    for i, row in df.iterrows():
        ticker = row['ticker']
        category = row['category']

        if category.lower() == "crypto":
            price = get_crypto_price(ticker)
            high, low = None, None
        else:
            price, high, low = get_stock_price(ticker)

        prices.append(price)
        highs.append(high)
        lows.append(low)

    df['current_price'] = prices
    df['52w_high'] = highs
    df['52w_low'] = lows
    df['current_value'] = df['current_price'] * df['units']
    df['pnl'] = (df['current_price'] - df['avg_price']) * df['units']

    return df
