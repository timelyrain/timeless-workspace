import yfinance as yf
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

# --- CONFIGURATION ---
# List of stocks to watch (instituition critera RoE 15%, Net Profit 25%, Nasdaq and SP500, 10bil market cap)
WATCHLIST = load_watchlist()
BENCHMARK = 'SPY'

# Telegram Credentials (loaded from environment or .env file)
import os
load_dotenv()  # pulls TELEGRAM_TOKEN and CHAT_ID from a local .env if present
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_DIVERGENCE")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials not found. Printing to console instead.")
        print(message)
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def scan_market():
    print("Fetching data...")
    # Download data for all tickers + SPY for the current day
    tickers = WATCHLIST + [BENCHMARK]
    data = yf.download(tickers, period="1d", interval="5m", progress=False, auto_adjust=True)['Close']
    
    if data.empty:
        print("No data found. Market might be closed.")
        return

    # Calculate % Change since Open
    # We take the first available price of the day (Open) and the last (Current)
    opens = data.iloc[0]
    currents = data.iloc[-1]
    
    pct_changes = ((currents - opens) / opens) * 100
    spy_change = pct_changes[BENCHMARK]
    # Track SPY intraday drawdown from open to the lowest 5m bar
    spy_intraday_drawdown_pct = ((data[BENCHMARK].min() - opens[BENCHMARK]) / opens[BENCHMARK]) * 100
    
    # --- THE ALGORITHM ---
    # We only care if SPY is WEAK (Red) and Stock is STRONG (Green)
    # OR if Stock is vastly outperforming SPY (e.g., SPY +0.1%, Stock +2.0%)
    
    alerts = []
    
    for ticker in WATCHLIST:
        stock_change = pct_changes[ticker]
        relative_strength = stock_change - spy_change
        
        # Condition 1: "The Divergence" (SPY dropped >1.5% intraday, stock green)
        if spy_intraday_drawdown_pct <= -1.5 and stock_change > 0:
            alerts.append(f"🚀 *DIVERGENCE ALERT: {ticker}*\nSPY fell {spy_intraday_drawdown_pct:.2f}% intraday, but {ticker} is Green ({stock_change:.2f}%).")
            
        # Condition 2: "The Rocket" (Stock is beating SPY by 2%+)
        elif relative_strength > 2.0:
            alerts.append(f"💪 *RS ALERT: {ticker}*\nMassive Relative Strength! {ticker} is leading SPY by {relative_strength:.2f}%.")

    if alerts:
        ny_tz = pytz.timezone('America/New_York')
        timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        final_msg = f"⏰ *Market Scan: {timestamp}*\n\n" + "\n\n".join(alerts)
        send_telegram_message(final_msg)
        print("Alerts sent!")
    else:
        print("No significant Relative Strength found right now.")

if __name__ == "__main__":
    scan_market()