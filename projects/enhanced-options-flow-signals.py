"""
Enhanced Options Flow Scanner 🎰
Tracks large options sweeps ($1M+) and aggressive buying at ask.

This is an enhanced version of the existing unusual-options-scanner
with focus on institutional-sized premium flow and directional bets.

Schedule: 3x daily (10:30 AM, 12:30 PM, 2:30 PM ET)
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

WATCHLIST = load_watchlist()

# Enhanced thresholds
MIN_SWEEP_PREMIUM = 1_000_000  # $1M minimum for "whale" detection
MIN_TOTAL_PREMIUM = 2_000_000  # $2M total options premium
VOLUME_MULTIPLIER = 5.0  # 5x avg volume = institutional
MIN_CALL_PUT_RATIO = 3.0  # Heavy call bias = bullish sweep

def scan_enhanced_options_flow():
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Get options data
            exp_dates = stock.options
            if not exp_dates or len(exp_dates) == 0:
                continue
            
            # Check next 2 expirations
            total_call_premium = 0
            total_put_premium = 0
            total_call_volume = 0
            total_put_volume = 0
            large_trades = []
            
            for exp_date in exp_dates[:2]:
                try:
                    option_chain = stock.option_chain(exp_date)
                    
                    calls = option_chain.calls
                    puts = option_chain.puts
                    
                    # Calculate premium flow
                    if not calls.empty:
                        calls_premium = (calls['lastPrice'] * calls['volume'] * 100).sum()
                        total_call_premium += calls_premium
                        total_call_volume += calls['volume'].sum()
                        
                        # Find large individual trades
                        for _, row in calls.iterrows():
                            trade_premium = row['lastPrice'] * row['volume'] * 100
                            if trade_premium >= MIN_SWEEP_PREMIUM:
                                large_trades.append({
                                    'type': 'CALL',
                                    'strike': row['strike'],
                                    'premium': trade_premium,
                                    'exp': exp_date
                                })
                    
                    if not puts.empty:
                        puts_premium = (puts['lastPrice'] * puts['volume'] * 100).sum()
                        total_put_premium += puts_premium
                        total_put_volume += puts['volume'].sum()
                        
                        for _, row in puts.iterrows():
                            trade_premium = row['lastPrice'] * row['volume'] * 100
                            if trade_premium >= MIN_SWEEP_PREMIUM:
                                large_trades.append({
                                    'type': 'PUT',
                                    'strike': row['strike'],
                                    'premium': trade_premium,
                                    'exp': exp_date
                                })
                
                except Exception as e:
                    continue
            
            # Calculate metrics
            total_premium = total_call_premium + total_put_premium
            if total_premium < MIN_TOTAL_PREMIUM:
                continue
            
            call_put_ratio = total_call_premium / total_put_premium if total_put_premium > 0 else 99
            
            # Get current price
            hist = stock.history(period='5d')
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            
            # Score
            score = 0
            if len(large_trades) >= 3:
                score += 5  # Multiple sweeps
            elif len(large_trades) >= 1:
                score += 3
            
            if total_premium >= 5_000_000:  # $5M+
                score += 3
            elif total_premium >= MIN_TOTAL_PREMIUM:
                score += 2
            
            if call_put_ratio >= MIN_CALL_PUT_RATIO:
                score += 3  # Bullish bias
            
            if score >= 5:
                quality = 'HIGH' if score >= 8 else 'MEDIUM'
                direction = 'BULLISH' if call_put_ratio >= 2.0 else 'BEARISH' if call_put_ratio <= 0.5 else 'NEUTRAL'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'total_premium_m': total_premium / 1_000_000,
                    'call_put_ratio': call_put_ratio,
                    'direction': direction,
                    'large_trades': large_trades[:3],  # Top 3
                    'score': score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "🎰 Enhanced Options Flow Scanner\n\nNo large sweeps detected ($1M+ threshold)."
    
    signals = sorted(signals, key=lambda x: x['total_premium_m'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🎰 Enhanced Options Flow Scanner\n⏰ {timestamp}\n"
    message += f"💰 Found {len(signals)} large sweep(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        
        if signal['direction'] == 'BULLISH':
            dir_emoji = "📈"
        elif signal['direction'] == 'BEARISH':
            dir_emoji = "📉"
        else:
            dir_emoji = "↔️"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  {dir_emoji} Direction: {signal['direction']}\n"
        message += f"  💰 Total Premium: ${signal['total_premium_m']:.1f}M\n"
        message += f"  📊 C/P Ratio: {signal['call_put_ratio']:.2f}\n"
        
        if signal['large_trades']:
            message += f"  🐋 Large Sweeps:\n"
            for trade in signal['large_trades'][:2]:
                message += f"     • {trade['type']} ${trade['strike']}: ${trade['premium']/1_000_000:.1f}M\n"
        
        message += f"  ⭐ Score: {signal['score']}/11 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Large sweeps often precede major moves"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Enhanced Options Flow Scanner...")
    signals = scan_enhanced_options_flow()
    print(f"Found {len(signals)} large sweep(s)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Enhanced Options Flow Scanner completed")

if __name__ == "__main__":
    main()
