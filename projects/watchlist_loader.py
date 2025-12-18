"""
Watchlist Loader Utility
Centralized watchlist management for all trading scanners.

Usage in your scanners:
    from watchlist_loader import load_watchlist
    
    WATCHLIST = load_watchlist()
    # or for stocks only:
    WATCHLIST = load_watchlist(include_etfs=False)
"""

import json
from pathlib import Path

def load_watchlist(include_etfs=True, watchlist_path=None):
    """
    Load watchlist from centralized JSON file.
    
    Args:
        include_etfs (bool): Include ETFs in watchlist (default: True)
        watchlist_path (str): Custom path to watchlist.json (default: ../watchlist.json)
    
    Returns:
        list: Combined list of stock tickers
    """
    if watchlist_path is None:
        # Default: look for watchlist.json in parent directory
        watchlist_path = Path(__file__).parent.parent / 'watchlist.json'
    else:
        watchlist_path = Path(watchlist_path)
    
    try:
        with open(watchlist_path, 'r') as f:
            data = json.load(f)
        
        stocks = data.get('stocks', [])
        etfs = data.get('etfs', [])
        
        if include_etfs:
            return stocks + etfs
        else:
            return stocks
    
    except FileNotFoundError:
        print(f"Warning: watchlist.json not found at {watchlist_path}")
        print("Using fallback watchlist...")
        # Fallback watchlist
        return [
            'SPY', 'QQQ'
        ]
    
    except json.JSONDecodeError as e:
        print(f"Error parsing watchlist.json: {e}")
        print("Using fallback watchlist...")
        return []


if __name__ == "__main__":
    # Test the loader
    print("Loading watchlist...")
    watchlist = load_watchlist()
    print(f"\nLoaded {len(watchlist)} tickers:")
    print(watchlist)
    
    print("\n\nStocks only:")
    stocks_only = load_watchlist(include_etfs=False)
    print(f"Loaded {len(stocks_only)} stocks")
