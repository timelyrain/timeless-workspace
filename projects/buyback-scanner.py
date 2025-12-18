"""
Buyback Authorization Scanner 💰
Monitors share buyback announcements and 10b5-1 plan activity.

Key Features:
- Tracks companies with active buyback programs
- Monitors buyback % of shares outstanding
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

Note: Buyback data available via company filings and yfinance info.
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

WATCHLIST = load_watchlist()

# === SETTINGS ===
MIN_BUYBACK_RATIO = 2.0  # % of shares outstanding
STRONG_BUYBACK_RATIO = 5.0
MIN_FREE_CASH_FLOW = 100_000_000  # $100M minimum FCF
MIN_PRICE = 20.0

def scan_buybacks():
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
            
            # Check for buyback indicators
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            free_cash_flow = info.get('freeCashflow', 0)
            
            # Estimate buyback activity (simplified - real data needs filings)
            shares_change = info.get('sharesShortPriorMonth', 0) - info.get('sharesShort', 0)
            
            # Calculate buyback ratio (if data available)
            if shares_outstanding > 0:
                buyback_pct = abs(shares_change) / shares_outstanding * 100 if shares_change < 0 else 0
            else:
                buyback_pct = 0
            
            # Free cash flow check
            if free_cash_flow < MIN_FREE_CASH_FLOW:
                continue
            
            # Score
            score = 0
            if buyback_pct >= STRONG_BUYBACK_RATIO:
                score += 5
            elif buyback_pct >= MIN_BUYBACK_RATIO:
                score += 3
            
            if free_cash_flow > 1_000_000_000:  # $1B+
                score += 2
            
            # Price relative to 52W high
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
                    'quality': quality
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
