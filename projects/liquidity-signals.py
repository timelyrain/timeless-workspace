"""
Liquidity Scanner 💧
Tracks bid-ask spread and volume to identify illiquid stocks (exit risk).

This is a risk management tool - avoid getting stuck in illiquid names.
Schedule: Weekly Friday 3 PM ET (weekend review)
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
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

WATCHLIST = load_watchlist()

# Liquidity thresholds
MAX_AVG_VOLUME = 500000  # Flag if < 500k shares/day
MAX_SPREAD_PCT = 0.5  # Flag if spread > 0.5%
WARNING_VOLUME = 200000  # Critical if < 200k

def scan_liquidity_risk():
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Estimate spread (using high-low as proxy since real bid-ask needs live data)
            recent_5d = hist.tail(5)
            avg_spread = ((recent_5d['High'] - recent_5d['Low']) / recent_5d['Close']).mean() * 100
            
            # Check liquidity concerns
            is_low_volume = avg_volume < MAX_AVG_VOLUME
            is_critical_volume = avg_volume < WARNING_VOLUME
            is_wide_spread = avg_spread > MAX_SPREAD_PCT
            
            if is_low_volume or is_wide_spread:
                # Risk score
                risk_score = 0
                if is_critical_volume:
                    risk_score += 5
                elif is_low_volume:
                    risk_score += 3
                
                if avg_spread > 1.0:  # Very wide
                    risk_score += 3
                elif is_wide_spread:
                    risk_score += 2
                
                risk_level = 'CRITICAL' if risk_score >= 6 else 'HIGH' if risk_score >= 4 else 'MEDIUM'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'avg_volume': avg_volume,
                    'avg_spread_pct': avg_spread,
                    'risk_score': risk_score,
                    'risk_level': risk_level
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "💧 Liquidity Scanner\n\nAll watchlist stocks have adequate liquidity."
    
    signals = sorted(signals, key=lambda x: x['risk_score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"💧 Liquidity Scanner (Risk Management)\n⏰ {timestamp}\n"
    message += f"⚠️ Found {len(signals)} stock(s) with liquidity concerns\n\n"
    
    for signal in signals:
        if signal['risk_level'] == 'CRITICAL':
            risk_emoji = "🔴"
        elif signal['risk_level'] == 'HIGH':
            risk_emoji = "🟠"
        else:
            risk_emoji = "🟡"
        
        message += f"{risk_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  📊 Avg Volume: {signal['avg_volume']:,.0f} shares/day\n"
        message += f"  📏 Avg Spread: {signal['avg_spread_pct']:.2f}%\n"
        message += f"  ⚠️ Risk Level: {signal['risk_level']} ({signal['risk_score']}/8)\n\n"
    
    message += "\n💡 Low liquidity = harder to exit positions quickly"
    message += "\n⚠️ Consider reducing position size or avoiding these stocks"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Liquidity Scanner...")
    signals = scan_liquidity_risk()
    print(f"Found {len(signals)} liquidity concern(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Liquidity Scanner completed")

if __name__ == "__main__":
    main()
