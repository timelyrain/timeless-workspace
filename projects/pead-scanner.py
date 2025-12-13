"""
Post-Earnings Announcement Drift (PEAD) Scanner 📊
Tracks stocks that beat earnings by >10% and monitors 30-60 day drift.

Academic research shows stocks that significantly beat continue to
drift higher for weeks as institutions slowly adjust positions.

Schedule: Daily 8 AM ET (track ongoing drift positions)
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

WATCHLIST = [
    'ABT', 'ADBE', 'AMT', 'ANET', 'APP', 'ASML', 'AVGO', 'COIN', 'COST', 'CRM',
    'CRWD', 'DDOG', 'DIS', 'GOOGL', 'GS', 'HUBS', 'ISRG', 'JNJ', 'JPM', 'LLY',
    'MA', 'MCD', 'META', 'MELI', 'MSFT', 'NET', 'NFLX', 'NOW', 'NVDA', 'ORCL',
    'PANW', 'PFE', 'PG', 'PLTR', 'PYPL', 'S', 'SHOP', 'SNOW', 'SOFI', 'TEAM',
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

# Settings
MIN_EARNINGS_BEAT = 10.0  # >= 10% beat
DRIFT_PERIOD_MIN = 5  # At least 5 days post-earnings
DRIFT_PERIOD_MAX = 60  # Within 60 days
MIN_POST_EARNINGS_GAIN = 3.0  # >= 3% gain post-earnings

def scan_pead_opportunities():
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Get earnings dates
            try:
                earnings_dates = stock.earnings_dates
                if earnings_dates is None or earnings_dates.empty:
                    continue
            except:
                continue
            
            # Get most recent earnings
            recent_earnings = earnings_dates.head(1)
            if recent_earnings.empty:
                continue
            
            earnings_date = recent_earnings.index[0]
            days_since_earnings = (datetime.now() - earnings_date).days
            
            # Check if within drift period
            if days_since_earnings < DRIFT_PERIOD_MIN or days_since_earnings > DRIFT_PERIOD_MAX:
                continue
            
            # Get earnings surprise data
            eps_estimate = recent_earnings['EPS Estimate'].iloc[0] if 'EPS Estimate' in recent_earnings.columns else None
            eps_actual = recent_earnings['Reported EPS'].iloc[0] if 'Reported EPS' in recent_earnings.columns else None
            
            if eps_estimate is None or eps_actual is None or eps_estimate == 0:
                continue
            
            # Calculate beat percentage
            beat_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100
            
            if beat_pct < MIN_EARNINGS_BEAT:
                continue
            
            # Get price data
            hist = stock.history(period='3mo')
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            
            # Find price at earnings date
            earnings_date_pd = earnings_date.tz_localize(None) if earnings_date.tzinfo else earnings_date
            nearest_date = hist.index[hist.index.get_indexer([earnings_date_pd], method='nearest')[0]]
            earnings_price = hist.loc[nearest_date]['Close']
            
            # Calculate drift
            drift_pct = ((current_price - earnings_price) / earnings_price) * 100
            
            if drift_pct < MIN_POST_EARNINGS_GAIN:
                continue
            
            # Calculate momentum (last 5 days)
            price_5d_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
            momentum_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
            
            # Score
            score = 0
            if beat_pct >= 20:
                score += 5  # Massive beat
            elif beat_pct >= 15:
                score += 3
            else:
                score += 2
            
            if drift_pct >= 10:
                score += 3  # Strong drift
            elif drift_pct >= 5:
                score += 2
            else:
                score += 1
            
            if momentum_5d > 0:
                score += 2  # Continued momentum
            
            if days_since_earnings <= 30:
                score += 1  # Still in sweet spot
            
            quality = 'HIGH' if score >= 8 else 'MEDIUM'
            
            # Estimate remaining drift potential (statistical)
            expected_total_drift = beat_pct * 0.5  # Historical: ~50% of beat translates to drift
            remaining_potential = expected_total_drift - drift_pct
            
            signals.append({
                'ticker': ticker,
                'price': current_price,
                'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                'days_since': days_since_earnings,
                'beat_pct': beat_pct,
                'drift_pct': drift_pct,
                'momentum_5d': momentum_5d,
                'remaining_potential': max(0, remaining_potential),
                'score': score,
                'quality': quality
            })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return "📊 PEAD Scanner\n\nNo post-earnings drift opportunities detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"📊 Post-Earnings Announcement Drift Scanner\n⏰ {timestamp}\n"
    message += f"📈 Found {len(signals)} active drift position(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  📅 Earnings: {signal['earnings_date']} ({signal['days_since']} days ago)\n"
        message += f"  🎯 Beat: {signal['beat_pct']:+.1f}%\n"
        message += f"  📈 Drift: {signal['drift_pct']:+.1f}% post-earnings\n"
        message += f"  🚀 Momentum (5d): {signal['momentum_5d']:+.1f}%\n"
        message += f"  💡 Est. Remaining: {signal['remaining_potential']:.1f}%\n"
        message += f"  ⭐ Score: {signal['score']}/11 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 PEAD effect strongest in days 5-30 post-earnings"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting PEAD Scanner...")
    signals = scan_pead_opportunities()
    print(f"Found {len(signals)} PEAD opportunity(ies)")
    message = format_alert_message(signals)
    print(f"\n{message}")
    send_telegram_message(message)
    print("PEAD Scanner completed")

if __name__ == "__main__":
    main()
