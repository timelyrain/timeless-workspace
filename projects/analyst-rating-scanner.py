"""
Analyst Rating Scanner 📈
Tracks analyst upgrades/downgrades and price target changes.

Note: yfinance provides recommendations/upgrades data. For real-time
alerts, paid services (Benzinga, AlphaVantage) provide better coverage.

Schedule: Daily 8 AM ET (before market open)
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
import pandas as pd
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

WATCHLIST = load_watchlist()
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

# Tier 1 firms (weight higher)
TOP_TIER_FIRMS = ['Goldman Sachs', 'Morgan Stanley', 'JPMorgan', 'Bank of America', 'Citi']

def scan_analyst_ratings():
    signals = []
    cutoff_date = datetime.now() - timedelta(days=7)
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Get recommendations
            recommendations = stock.recommendations
            if recommendations is None or recommendations.empty:
                continue
            
            # Filter recent
            recommendations = recommendations[recommendations.index >= cutoff_date]
            if recommendations.empty:
                continue
            
            # Analyze recent ratings
            upgrades = []
            downgrades = []
            
            for idx, row in recommendations.iterrows():
                action = str(row.get('To Grade', '')).lower()
                firm = str(row.get('Firm', 'Unknown'))
                from_grade = str(row.get('From Grade', ''))
                
                is_top_tier = any(tier.lower() in firm.lower() for tier in TOP_TIER_FIRMS)
                
                if 'buy' in action or 'outperform' in action or 'overweight' in action:
                    upgrades.append({
                        'firm': firm,
                        'action': action,
                        'date': idx,
                        'is_top_tier': is_top_tier,
                        'from_grade': from_grade
                    })
                elif 'sell' in action or 'underperform' in action or 'underweight' in action:
                    downgrades.append({
                        'firm': firm,
                        'action': action,
                        'date': idx,
                        'is_top_tier': is_top_tier,
                        'from_grade': from_grade
                    })
            
            if len(upgrades) > 0 or len(downgrades) > 0:
                # Get current price
                hist = stock.history(period='5d')
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # Score
                score = len(upgrades) * 2 - len(downgrades) * 2
                for upg in upgrades:
                    if upg['is_top_tier']:
                        score += 2
                
                quality = 'HIGH' if score >= 5 else 'MEDIUM' if score >= 3 else 'LOW'
                
                if score >= 2:  # Net positive
                    signals.append({
                        'ticker': ticker,
                        'price': current_price,
                        'upgrades': upgrades,
                        'downgrades': downgrades,
                        'net_rating': score,
                        'quality': quality
                    })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "📈 Analyst Rating Scanner\n\nNo significant rating changes this week."
    
    signals = sorted(signals, key=lambda x: x['net_rating'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"📈 Analyst Rating Scanner\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} rating change(s) this week\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡" if signal['quality'] == 'MEDIUM' else "⚪"
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  ⬆️ Upgrades: {len(signal['upgrades'])} | ⬇️ Downgrades: {len(signal['downgrades'])}\n"
        
        # Show recent upgrades
        for upg in signal['upgrades'][:2]:
            tier_flag = " [TOP TIER]" if upg['is_top_tier'] else ""
            message += f"     • {upg['firm']}: {upg['action'].upper()}{tier_flag}\n"
        
        message += f"  ⭐ Net Rating: {signal['net_rating']:+d} ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Top tier upgrades often move stocks 3-5%"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Analyst Rating Scanner...")
    signals = scan_analyst_ratings()
    print(f"Found {len(signals)} rating change(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Analyst Rating Scanner completed")

if __name__ == "__main__":
    main()
