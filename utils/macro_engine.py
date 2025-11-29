from .market_data import get_index_price

def fetch_macro():
    return {
        "US 10Y": get_index_price("^TNX"),
        "VIX": get_index_price("^VIX"),
        "Nasdaq 100": get_index_price("^NDX"),
        "Nifty 50": get_index_price("^NSEI"),
        "Hang Seng": get_index_price("^HSI"),
    }
