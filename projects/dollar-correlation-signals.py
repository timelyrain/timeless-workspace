"""
Dollar Correlation Scanner 💵
Finds stocks with strong inverse correlation to DXY (US Dollar Index).

Key Features:
- Tracks 60-day rolling correlation to DXY
- Identifies inverse correlations (< -0.5)
- Useful for macro hedging and currency plays
- Finds multinationals hurt/helped by strong dollar

Usage: Strong dollar hurts exporters, helps importers.
Schedule: Weekly Monday 8 AM ET
"""

import yfinance as yf
import requests
import os
import numpy as np
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

# Settings
MIN_INVERSE_CORRELATION = -0.5  # Strong inverse
MIN_POSITIVE_CORRELATION = 0.5  # Strong positive
CORRELATION_PERIOD = 60  # 60 days

def scan_dollar_correlation():
    signals = []
    
    # Get DXY data (use UUP ETF as proxy for DXY)
    dxy = yf.Ticker('UUP')  # US Dollar ETF
    dxy_hist = dxy.history(period='6mo')
    
    if dxy_hist.empty:
        print("Error: Could not fetch DXY data")
        return []
    
    dxy_returns = dxy_hist['Close'].pct_change()
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            
            if hist.empty or len(hist) < CORRELATION_PERIOD:
                continue
            
            current_price = hist['Close'].iloc[-1]
            stock_returns = hist['Close'].pct_change()
            
            # Align dates
            common_dates = dxy_returns.index.intersection(stock_returns.index)
            if len(common_dates) < CORRELATION_PERIOD:
                continue
            
            dxy_aligned = dxy_returns.loc[common_dates]
            stock_aligned = stock_returns.loc[common_dates]
            
            # Calculate correlation
            correlation = stock_aligned.tail(CORRELATION_PERIOD).corr(dxy_aligned.tail(CORRELATION_PERIOD))
            
            # Check thresholds
            is_inverse = correlation <= MIN_INVERSE_CORRELATION
            is_positive = correlation >= MIN_POSITIVE_CORRELATION
            
            if is_inverse or is_positive:
                corr_type = "INVERSE" if is_inverse else "POSITIVE"
                strength = abs(correlation)
                
                quality = 'HIGH' if strength >= 0.7 else 'MEDIUM'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'correlation': correlation,
                    'corr_type': corr_type,
                    'strength': strength,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "💵 Dollar Correlation Scanner\n\nNo strong DXY correlations detected."
    
    signals = sorted(signals, key=lambda x: abs(x['correlation']), reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"💵 Dollar Correlation Scanner\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} DXY-correlated stock(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        corr_emoji = "📉" if signal['corr_type'] == 'INVERSE' else "📈"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  {corr_emoji} Correlation: {signal['correlation']:.2f} ({signal['corr_type']})\n"
        message += f"  💪 Strength: {signal['strength']:.2%} ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Inverse corr = benefits from weak dollar (exporters)"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Dollar Correlation Scanner...")
    signals = scan_dollar_correlation()
    print(f"Found {len(signals)} correlated stock(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Dollar Correlation Scanner completed")

if __name__ == "__main__":
    main()
