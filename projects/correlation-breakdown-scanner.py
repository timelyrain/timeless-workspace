"""
Correlation Breakdown Scanner ⚠️
Detects when historically correlated pairs diverge (anomaly = opportunity).

Example: NVDA up 3%, AMD down 2% = unusual divergence
Either mean reversion play or new trend forming.

Schedule: Daily 3 PM ET
"""

import yfinance as yf
import requests
import os
import numpy as np
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Define correlated pairs
CORRELATED_PAIRS = [
    ('NVDA', 'AMD'),
    ('MSFT', 'GOOGL'),
    ('META', 'GOOGL'),
    ('JPM', 'GS'),
    ('COST', 'WMT'),
    ('NFLX', 'DIS'),
    ('TSLA', 'RIVN') if 'RIVN' in ['ABT', 'ADBE'] else ('TSLA', 'NIO'),  # Fallback
    ('CRWD', 'PANW'),
    ('SHOP', 'MELI'),
    ('SNOW', 'DDOG'),
]

# Settings
MIN_HISTORICAL_CORRELATION = 0.6  # Must be correlated >= 0.6
MIN_DIVERGENCE_PCT = 4.0  # Divergence >= 4% to flag
CORRELATION_PERIOD = 60  # 60-day historical correlation

def scan_correlation_breakdowns():
    signals = []
    
    for stock1_ticker, stock2_ticker in CORRELATED_PAIRS:
        try:
            print(f"Scanning {stock1_ticker}/{stock2_ticker}...")
            
            stock1 = yf.Ticker(stock1_ticker)
            stock2 = yf.Ticker(stock2_ticker)
            
            hist1 = stock1.history(period='6mo')
            hist2 = stock2.history(period='6mo')
            
            if hist1.empty or hist2.empty:
                continue
            
            # Align dates
            common_dates = hist1.index.intersection(hist2.index)
            if len(common_dates) < CORRELATION_PERIOD:
                continue
            
            hist1_aligned = hist1.loc[common_dates]
            hist2_aligned = hist2.loc[common_dates]
            
            # Calculate historical correlation
            returns1 = hist1_aligned['Close'].pct_change()
            returns2 = hist2_aligned['Close'].pct_change()
            
            historical_corr = returns1.tail(CORRELATION_PERIOD).corr(returns2.tail(CORRELATION_PERIOD))
            
            # Skip if not historically correlated
            if abs(historical_corr) < MIN_HISTORICAL_CORRELATION:
                continue
            
            # Calculate today's performance
            current_price1 = hist1_aligned['Close'].iloc[-1]
            current_price2 = hist2_aligned['Close'].iloc[-1]
            
            prev_price1 = hist1_aligned['Close'].iloc[-2] if len(hist1_aligned) >= 2 else hist1_aligned['Close'].iloc[0]
            prev_price2 = hist2_aligned['Close'].iloc[-2] if len(hist2_aligned) >= 2 else hist2_aligned['Close'].iloc[0]
            
            perf1 = ((current_price1 - prev_price1) / prev_price1) * 100
            perf2 = ((current_price2 - prev_price2) / prev_price2) * 100
            
            # Calculate divergence
            divergence = abs(perf1 - perf2)
            
            if divergence >= MIN_DIVERGENCE_PCT:
                # Determine leader/laggard
                if perf1 > perf2:
                    leader = stock1_ticker
                    laggard = stock2_ticker
                    leader_perf = perf1
                    laggard_perf = perf2
                else:
                    leader = stock2_ticker
                    laggard = stock1_ticker
                    leader_perf = perf2
                    laggard_perf = perf1
                
                # Score
                score = 0
                if divergence >= 8:
                    score += 5  # Extreme
                elif divergence >= 6:
                    score += 3
                else:
                    score += 2
                
                if historical_corr >= 0.8:
                    score += 2  # Very strong historical correlation
                
                quality = 'HIGH' if score >= 6 else 'MEDIUM'
                
                # Trade idea
                if historical_corr > 0:  # Positive correlation
                    if perf1 * perf2 < 0:  # Opposite directions
                        trade_idea = "MEAN REVERSION (opposite directions)"
                    else:
                        trade_idea = "RELATIVE STRENGTH (leader continues)"
                else:
                    trade_idea = "INVERSE CORRELATION BREAKDOWN"
                
                signals.append({
                    'pair': f"{stock1_ticker}/{stock2_ticker}",
                    'leader': leader,
                    'laggard': laggard,
                    'leader_perf': leader_perf,
                    'laggard_perf': laggard_perf,
                    'divergence': divergence,
                    'historical_corr': historical_corr,
                    'trade_idea': trade_idea,
                    'score': score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {stock1_ticker}/{stock2_ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "⚠️ Correlation Breakdown Scanner\n\nNo unusual divergences detected in correlated pairs."
    
    signals = sorted(signals, key=lambda x: x['divergence'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"⚠️ Correlation Breakdown Scanner\n⏰ {timestamp}\n"
    message += f"🔍 Found {len(signals)} correlation anomaly(ies)\n\n"
    
    for signal in signals:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        
        message += f"{quality_emoji} {signal['pair']}\n"
        message += f"  🏆 Leader: {signal['leader']} ({signal['leader_perf']:+.1f}%)\n"
        message += f"  🐢 Laggard: {signal['laggard']} ({signal['laggard_perf']:+.1f}%)\n"
        message += f"  ↔️ Divergence: {signal['divergence']:.1f}%\n"
        message += f"  📊 Historical Corr: {signal['historical_corr']:.2f}\n"
        message += f"  💡 Trade Idea: {signal['trade_idea']}\n"
        message += f"  ⭐ Score: {signal['score']}/7 ({signal['quality']})\n\n"
    
    message += "\n💡 Large divergences often mean-revert within days"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Correlation Breakdown Scanner...")
    signals = scan_correlation_breakdowns()
    print(f"Found {len(signals)} correlation breakdown(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Correlation Breakdown Scanner completed")

if __name__ == "__main__":
    main()
