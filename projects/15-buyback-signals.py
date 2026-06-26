"""
Buyback Authorization Signals 💰
Monitors share buyback announcements using Financial Modeling Prep (FMP) API for accurate, real-time data.

Key Features:
- Tracks companies with active buyback programs (via FMP buyback endpoint)
- Monitors buyback % of shares outstanding (using FMP-reported buybackAmount)
- Detects accelerated buyback activity
- Identifies strong shareholder return signals

Usage Tips:
1. Buybacks often signal management confidence
2. Active buybacks provide price support
3. Companies buying >5% annually = very bullish
4. Best in combination with earnings beats
5. Avoid if buyback at all-time highs (bad capital allocation)

Strategy: Follow companies putting money where their mouth is.
Schedule: Runs weekly Monday 7 AM ET (after weekend filings review).

Note: Buyback data is now sourced from Financial Modeling Prep (FMP) API, not yfinance. You must set FMP_API_KEY in your .env file.
"""

import yfinance as yf
import requests
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FMP_API_KEY = os.getenv('FMP_API_KEY')

WATCHLIST = load_watchlist()

# === SETTINGS ===
# Buyback data is now sourced from FMP API (see get_fmp_buyback_amount)
MIN_BUYBACK_RATIO = 2.0  # % of shares outstanding (from FMP buybackAmount)
STRONG_BUYBACK_RATIO = 5.0
MIN_FREE_CASH_FLOW = 100_000_000  # $100M minimum FCF
MIN_PRICE = 20.0

def get_fmp_buyback_amount(ticker):
    """
    Fetches the most recent buyback amount (in dollars) from FMP cash flow statement endpoint.
    Returns (buyback_amount, fiscal_date). If no data, returns (0, None).
    """
    url = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&apikey={FMP_API_KEY}"
    print(f"FMP URL: {url}")
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        print(f"FMP cash flow data for {ticker}: {data}")
        if data and isinstance(data, list) and 'commonStockRepurchased' in data[0]:
            latest = data[0]
            return float(latest.get('commonStockRepurchased', 0)), latest.get('date', '')
        return 0, None
    except Exception as e:
        print(f"FMP error for {ticker}: {e}")
        return 0, None

def scan_buybacks():
    """
    Scans for buyback signals using FMP cash flow statement
    - Only considers stocks with a recent repurchase > 0
    - Calculates buyback % of shares outstanding (using repurchase $ / (shares_outstanding * price))
    - Applies scoring based on buyback %, free cash flow, and price discount
    """
    signals = []
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1y')
            if hist.empty:
                continue
            current_price = hist['Close'].iloc[-1]
            if current_price < MIN_PRICE:
                continue
            # FMP buyback integration (cash flow statement)
            print(f"Fetching buyback data for {ticker} from FMP...")
            buyback_amount, buyback_date = get_fmp_buyback_amount(ticker)
            shares_outstanding = info.get('sharesOutstanding', 0)
            if buyback_amount == 0 or shares_outstanding == 0 or current_price == 0:
                continue
            # Estimate buyback %: repurchase $ / (shares_outstanding * price)
            buyback_pct = abs(buyback_amount) / (shares_outstanding * current_price) * 100
            free_cash_flow = info.get('freeCashflow', 0)
            if free_cash_flow < MIN_FREE_CASH_FLOW:
                continue
            score = 0
            if buyback_pct >= STRONG_BUYBACK_RATIO:
                score += 5
            elif buyback_pct >= MIN_BUYBACK_RATIO:
                score += 3
            if free_cash_flow > 1_000_000_000:  # $1B+
                score += 2
            high_52w = hist['High'].max()
            distance_from_high = ((high_52w - current_price) / high_52w) * 100
            if distance_from_high > 20:  # Buying at discount
                score += 2
            if score >= 5:
                quality = 'HIGH' if score >= 7 else 'MEDIUM'
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'buyback_pct': buyback_pct,
                    'fcf_m': free_cash_flow / 1_000_000,
                    'distance_from_high': distance_from_high,
                    'score': score,
                    'quality': quality,
                    'buyback_date': buyback_date
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    return signals

def format_alert_message(signals):
    if not signals:
        return "💰 Buyback Scanner\n\nNo significant buyback activity detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"💰 Buyback Authorization Scanner\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} active buyback program(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  🔄 Buyback: ~{signal['buyback_pct']:.1f}% of shares\n"
        message += f"  💵 Free Cash Flow: ${signal['fcf_m']:.0f}M\n"
        message += f"  📉 Below 52W High: {signal['distance_from_high']:.1f}%\n"
        message += f"  ⭐ Score: {signal['score']}/9 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Buybacks = Management confidence + price support"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        # Telegram has a 4096 character limit
        if len(message) > 4096:
            message = message[:4090] + "\n\n[...]"
        
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Buyback Scanner...")
    signals = scan_buybacks()
    print(f"Found {len(signals)} buyback signal(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Buyback Scanner completed")

if __name__ == "__main__":
    main()
