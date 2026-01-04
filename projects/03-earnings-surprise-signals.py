"""
Earnings Surprise Signals (PEAD Strategy) 📅
Post-Earnings-Announcement-Drift: Stocks with earnings beats tend to drift higher for weeks.

Key Features:
- Tracks earnings beats/misses using Alpha Vantage earnings API
- Calculates EPS surprise % from actual vs estimated
- Detects post-earnings momentum continuation
- Filters for quality earnings beats
- Identifies pre-earnings setup opportunities

Usage Tips:
1. EPS beat = quality signal for PEAD
2. PEAD effect strongest in small/mid caps
3. Typical drift: 3-5% over 30 days post-earnings
4. Enter 1-3 days after earnings (avoid IV crush)
5. Best with analyst upgrade post-earnings

Strategy: Academic strategy - earnings surprises underreact initially, then drift for weeks.
Schedule: Daily 8 AM ET (check previous day's earnings, setup for day trades).

Note: Uses Alpha Vantage EARNINGS_CALENDAR endpoint for bulk fetching. Requires ALPHA_VANTAGE_API_KEY in .env file.
Free tier: 25 API calls/day. This script uses 1-2 calls per run (fetches recent earnings calendar, then filters for watchlist matches).
"""

import yfinance as yf
import requests
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

WATCHLIST = load_watchlist()

# === SETTINGS ===
MIN_EPS_SURPRISE = 5.0  # Minimum 5% EPS surprise
STRONG_EPS_SURPRISE = 15.0  # 15%+ = strong beat
MIN_REVENUE_SURPRISE = 2.0  # Minimum 2% revenue surprise
LOOKBACK_DAYS = 7  # Look for earnings in last 7 days
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500000

def get_recent_earnings_from_calendar():
    """Fetch recent earnings reports from Alpha Vantage EARNINGS_CALENDAR.
    Returns dict of {symbol: earnings_data} for watchlist stocks that reported recently.
    """
    # Alpha Vantage EARNINGS_CALENDAR returns 3-month horizon by default
    # We'll fetch the calendar and filter for past earnings within our lookback window
    url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey={ALPHA_VANTAGE_API_KEY}"
    
    print("Fetching recent earnings calendar from Alpha Vantage...")
    
    try:
        resp = requests.get(url, timeout=15)
        
        # Check for rate limiting
        if 'Note' in resp.text or 'API call frequency' in resp.text:
            print("⚠️  API rate limit reached. Try again later.")
            return {}
        
        # EARNINGS_CALENDAR returns CSV format
        lines = resp.text.strip().split('\n')
        if len(lines) < 2:
            print("✗ No earnings data returned")
            return {}
        
        # Parse CSV header and data
        header = lines[0].split(',')
        
        earnings_dict = {}
        today = datetime.now()
        
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) < 6:
                continue
            
            try:
                symbol = parts[0].strip()
                report_date_str = parts[2].strip()  # reportDate column
                estimate_str = parts[4].strip()  # estimate
                
                # Only process watchlist stocks
                if symbol not in WATCHLIST:
                    continue
                
                # Parse report date
                report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
                days_since = (today - report_date).days
                
                # Only include earnings that already happened within lookback window
                if days_since < 0 or days_since > LOOKBACK_DAYS:
                    continue
                
                # For past earnings, we need to fetch actual results separately
                # Alpha Vantage calendar only shows estimates, not actuals
                # We'll need to call EARNINGS endpoint for actual EPS
                if symbol not in earnings_dict:  # Take most recent only
                    earnings_dict[symbol] = {
                        'reportDate': report_date_str,
                        'estimate': estimate_str,
                        'days_since': days_since
                    }
            
            except (ValueError, IndexError) as e:
                continue
        
        print(f"✓ Found {len(earnings_dict)} watchlist stocks with recent earnings\n")
        return earnings_dict
    
    except Exception as e:
        print(f"✗ Alpha Vantage calendar error: {e}")
        return {}


def get_actual_earnings_for_symbol(ticker):
    """Fetch actual earnings results for a specific ticker.
    Returns dict with actual EPS and estimated EPS, or None.
    """
    url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if 'Error Message' in data or 'Note' in data:
            return None
        
        quarterly = data.get('quarterlyEarnings', [])
        if not quarterly or len(quarterly) == 0:
            return None
        
        # Get most recent quarter
        latest = quarterly[0]
        reported_eps = latest.get('reportedEPS')
        estimated_eps = latest.get('estimatedEPS')
        fiscal_date = latest.get('fiscalDateEnding')
        
        if reported_eps and estimated_eps:
            try:
                return {
                    'reportedEPS': float(reported_eps),
                    'estimatedEPS': float(estimated_eps),
                    'fiscalDateEnding': fiscal_date
                }
            except (ValueError, TypeError):
                return None
        
        return None
    
    except Exception as e:
        print(f"  ✗ Error fetching earnings for {ticker}: {e}")
        return None

def scan_earnings_surprises():
    """Scan for PEAD (Post-Earnings-Announcement-Drift) signals."""
    signals = []
    
    # Step 1: Get bulk earnings calendar (1 API call)
    recent_earnings = get_recent_earnings_from_calendar()
    
    if not recent_earnings:
        print("No recent earnings found in watchlist.")
        return signals
    
    print(f"Processing {len(recent_earnings)} stocks with recent earnings...\n")
    
    # Step 2: For each stock with recent earnings, fetch actual results
    for idx, ticker in enumerate(recent_earnings.keys(), 1):
        try:
            print(f"[{idx}/{len(recent_earnings)}] Scanning {ticker}...")
            
            calendar_data = recent_earnings[ticker]
            days_since_earnings = calendar_data['days_since']
            
            # Get actual earnings results (1 API call per stock)
            actual_data = get_actual_earnings_for_symbol(ticker)
            
            if not actual_data:
                print(f"  ✗ Could not retrieve actual earnings data\n")
                continue
            
            actual_eps = actual_data['reportedEPS']
            estimated_eps = actual_data['estimatedEPS']
            
            if estimated_eps == 0:
                print(f"  ✗ Estimated EPS is zero, cannot calculate surprise\n")
                continue
            
            # Calculate surprise percentage
            eps_surprise_pct = ((actual_eps - estimated_eps) / abs(estimated_eps)) * 100
            
            print(f"  📊 EPS: ${actual_eps:.2f} vs ${estimated_eps:.2f} = {eps_surprise_pct:+.1f}%")
            
            # Only positive surprises (beats)
            if eps_surprise_pct < MIN_EPS_SURPRISE:
                print(f"  ✗ Surprise {eps_surprise_pct:.1f}% below threshold {MIN_EPS_SURPRISE}%\n")
                continue
            
            earnings_date_str = calendar_data['reportDate']
            earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
            
            # Get current price and volume from yfinance
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if hist.empty:
                print(f"  ✗ No price data available")
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                print(f"  ✗ Price ${current_price:.2f} or volume {avg_volume:,.0f} below threshold")
                continue
            
            # Calculate post-earnings performance
            try:
                # Get price on earnings date and current
                earnings_price = hist.loc[hist.index >= earnings_date]['Close'].iloc[0]
                post_earnings_return = ((current_price - earnings_price) / earnings_price) * 100
                print(f"  📈 Post-earnings drift: {post_earnings_return:+.1f}%")
            except:
                post_earnings_return = 0
                print(f"  ⚠️  Could not calculate post-earnings return")
            
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
                
                print(f"  🟢 SIGNAL: Score {score}/12 ({quality})\n")
                
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
            else:
                print(f"  ✗ Score {score}/12 below threshold (need 6+)\n")
            
            # Rate limiting: Alpha Vantage free tier = 5 calls/min
            time.sleep(12)  # 12 sec between calls
        
        except Exception as e:
            print(f"  ✗ Error processing {ticker}: {e}\n")
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
    print(f"Using Alpha Vantage EARNINGS_CALENDAR (bulk fetch) + EARNINGS (per-stock actuals)")
    print(f"Free tier: 25 calls/day. This run uses: 1 calendar call + N stock calls\n")
    
    if not ALPHA_VANTAGE_API_KEY:
        print("❌ ERROR: ALPHA_VANTAGE_API_KEY not found in .env file!")
        print("   Get your free key at: https://www.alphavantage.co/support/#api-key")
        print("   Add to .env: ALPHA_VANTAGE_API_KEY=your_key_here")
        return
    
    signals = scan_earnings_surprises()
    print(f"\nFound {len(signals)} PEAD signal(s)")
    
    message = format_alert_message(signals)
    
    if message:
        print(f"\n{message}")
        send_telegram_message(message)
    else:
        print("\nNo earnings surprises detected. Skipping Telegram alert.")
    
    print("Earnings Surprise Scanner completed")

if __name__ == "__main__":
    main()
