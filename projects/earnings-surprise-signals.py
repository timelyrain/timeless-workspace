"""
Earnings Surprise Signals (PEAD Strategy) 📅
Post-Earnings-Announcement-Drift: Stocks with earnings beats tend to drift higher for weeks.

Key Features:
- Tracks earnings beats/misses using FMP earnings surprises API
- Calculates EPS surprise % and revenue surprise %
- Detects post-earnings momentum continuation
- Filters for quality earnings beats (both EPS and revenue)
- Identifies pre-earnings setup opportunities

Usage Tips:
1. EPS beat + Revenue beat = highest quality signal
2. PEAD effect strongest in small/mid caps
3. Typical drift: 3-5% over 30 days post-earnings
4. Enter 1-3 days after earnings (avoid IV crush)
5. Best with analyst upgrade post-earnings

Strategy: Academic strategy - earnings surprises underreact initially, then drift for weeks.
Schedule: Daily 8 AM ET (check previous day's earnings, setup for day trades).

Note: Uses FMP /earnings-surprises API. Requires FMP_API_KEY in .env file.
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
CHAT_ID = os.getenv('CHAT_ID')
FMP_API_KEY = os.getenv('FMP_API_KEY')

WATCHLIST = load_watchlist()

# === SETTINGS ===
MIN_EPS_SURPRISE = 5.0  # Minimum 5% EPS surprise
STRONG_EPS_SURPRISE = 15.0  # 15%+ = strong beat
MIN_REVENUE_SURPRISE = 2.0  # Minimum 2% revenue surprise
LOOKBACK_DAYS = 7  # Look for earnings in last 7 days
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500000

def get_recent_earnings_surprises():
    """Fetch recent earnings surprises from FMP API."""
    # Get current and previous quarter
    today = datetime.now()
    current_year = today.year
    current_quarter = (today.month - 1) // 3 + 1
    
    # Try current and previous quarter
    quarters_to_check = [
        (current_year, current_quarter),
        (current_year if current_quarter > 1 else current_year - 1, 
         current_quarter - 1 if current_quarter > 1 else 4)
    ]
    
    all_surprises = {}
    
    for year, quarter in quarters_to_check:
        url = f"https://financialmodelingprep.com/stable/earnings-surprises?year={year}&quarter=Q{quarter}&apikey={FMP_API_KEY}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data and isinstance(data, list):
                for surprise in data:
                    symbol = surprise.get('symbol')
                    if symbol in WATCHLIST:
                        all_surprises[symbol] = surprise
        except Exception as e:
            print(f"FMP error for Q{quarter} {year}: {e}")
            continue
    
    return all_surprises

def scan_earnings_surprises():
    """Scan for PEAD (Post-Earnings-Announcement-Drift) signals."""
    signals = []
    
    # Get recent earnings surprises
    surprises = get_recent_earnings_surprises()
    
    for ticker in WATCHLIST:
        try:
            if ticker not in surprises:
                continue
            
            print(f"Scanning {ticker}...")
            
            surprise_data = surprises[ticker]
            
            # Get earnings date
            earnings_date_str = surprise_data.get('date', '')
            if not earnings_date_str:
                continue
            
            earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
            days_since_earnings = (datetime.now() - earnings_date).days
            
            # Only consider earnings within lookback period
            if days_since_earnings > LOOKBACK_DAYS or days_since_earnings < 0:
                continue
            
            # Get surprise metrics
            actual_eps = float(surprise_data.get('actualEarningResult', 0))
            estimated_eps = float(surprise_data.get('estimatedEarning', 0))
            
            if estimated_eps == 0:
                continue
            
            eps_surprise_pct = ((actual_eps - estimated_eps) / abs(estimated_eps)) * 100
            
            # Only positive surprises (beats)
            if eps_surprise_pct < MIN_EPS_SURPRISE:
                continue
            
            # Get current price and volume
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                continue
            
            # Calculate post-earnings performance
            try:
                # Get price on earnings date and current
                earnings_price = hist.loc[hist.index >= pd.Timestamp(earnings_date)]['Close'].iloc[0]
                post_earnings_return = ((current_price - earnings_price) / earnings_price) * 100
            except:
                post_earnings_return = 0
            
            # Score
            score = 0
            
            # EPS surprise strength
            if eps_surprise_pct >= STRONG_EPS_SURPRISE * 2:  # 30%+
                score += 5
            elif eps_surprise_pct >= STRONG_EPS_SURPRISE:  # 15%+
                score += 4
            elif eps_surprise_pct >= MIN_EPS_SURPRISE * 2:  # 10%+
                score += 3
            elif eps_surprise_pct >= MIN_EPS_SURPRISE:  # 5%+
                score += 2
            
            # Post-earnings momentum (PEAD)
            if post_earnings_return > 5:
                score += 3
            elif post_earnings_return > 2:
                score += 2
            elif post_earnings_return > 0:
                score += 1
            
            # Recent earnings (fresher = better)
            if days_since_earnings <= 3:
                score += 2
            elif days_since_earnings <= 5:
                score += 1
            
            # Volume confirmation
            recent_volume = hist['Volume'].iloc[-5:].mean()
            if recent_volume > avg_volume * 1.5:
                score += 2
            
            if score >= 6:
                quality = 'HIGH' if score >= 10 else 'MEDIUM'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'eps_surprise_pct': eps_surprise_pct,
                    'actual_eps': actual_eps,
                    'estimated_eps': estimated_eps,
                    'days_since_earnings': days_since_earnings,
                    'post_earnings_return': post_earnings_return,
                    'earnings_date': earnings_date_str,
                    'score': score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return None
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"📅 Earnings Surprise Signals (PEAD)\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} earnings beat(s) with drift potential\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  📈 EPS Surprise: {signal['eps_surprise_pct']:+.1f}% (${signal['actual_eps']:.2f} vs ${signal['estimated_eps']:.2f})\n"
        message += f"  📅 Earnings Date: {signal['earnings_date']} ({signal['days_since_earnings']} days ago)\n"
        message += f"  🚀 Post-Earnings Drift: {signal['post_earnings_return']:+.1f}%\n"
        message += f"  ⭐ Score: {signal['score']}/12 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 PEAD: Earnings beats drift higher for 2-4 weeks. Enter 1-3 days after earnings."
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Earnings Surprise (PEAD) Scanner...")
    signals = scan_earnings_surprises()
    print(f"Found {len(signals)} PEAD signal(s)")
    
    message = format_alert_message(signals)
    
    if message:
        print(f"\n{message}")
        send_telegram_message(message)
    else:
        print("\nNo earnings surprises detected. Skipping Telegram alert.")
    
    print("Earnings Surprise Scanner completed")

if __name__ == "__main__":
    main()
