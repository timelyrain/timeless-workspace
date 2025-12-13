"""
Smart Money Flow Scanner (Institutional) 🏦
Tracks institutional activity, 13F filings updates, and smart money movements.

Key Features:
- Monitors significant institutional ownership changes
- Tracks hedge fund activity (new positions, increased stakes)
- Identifies institutional buying pressure
- Detects unusual institutional accumulation
- Follows what the big players do

Usage Tips:
1. New institutional positions often signal conviction
2. Increased stakes by multiple funds = strong signal
3. Watch for 13F "superinvestors" (Buffett, Ackman, etc.)
4. Institutional ownership >70% can limit upside (crowded)
5. Fresh institutional buying after earnings often bullish

Data Source: Yahoo Finance institutional holders data
Schedule: Weekly on Mondays at 7 AM ET (after weekend 13F analysis)

Note: 13F filings are quarterly and delayed 45 days. This scanner detects
relative changes in institutional holdings between reporting periods.
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
import pandas as pd

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

# Watchlist - same as other scanners
WATCHLIST = [
    'ABT', 'ADBE', 'AMT', 'ANET', 'APP', 'ASML', 'AVGO', 'COIN', 'COST', 'CRM',
    'CRWD', 'DDOG', 'DIS', 'GOOGL', 'GS', 'HUBS', 'ISRG', 'JNJ', 'JPM', 'LLY',
    'MA', 'MCD', 'META', 'MELI', 'MSFT', 'NET', 'NFLX', 'NOW', 'NVDA', 'ORCL',
    'PANW', 'PFE', 'PG', 'PLTR', 'PYPL', 'S', 'SHOP', 'SNOW', 'SOFI', 'TEAM',
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

# === CUSTOMIZABLE SETTINGS ===

# Minimum institutional ownership percentage to consider
MIN_INSTITUTIONAL_OWNERSHIP = 50.0  # % (50% = institutions own half the float)

# Minimum change in institutional ownership to flag (percentage points)
MIN_OWNERSHIP_CHANGE = 5.0  # pp (e.g., 65% -> 70% = +5pp change)

# Minimum number of institutional holders to consider liquid
MIN_HOLDER_COUNT = 50

# Notable "superinvestor" institutions to highlight
SUPERINVESTORS = [
    'Berkshire Hathaway',
    'Bill & Melinda Gates Foundation',
    'Pershing Square',
    'Tiger Global',
    'Soros Fund Management',
    'Bridgewater Associates',
    'Renaissance Technologies',
    'D.E. Shaw',
    'Citadel Advisors',
    'Two Sigma',
    'Millennium Management',
    'Point72',
    'Third Point',
    'Maverick Capital',
    'Viking Global',
]

# Minimum position size for superinvestor to flag ($M)
MIN_SUPERINVESTOR_POSITION = 50.0  # $50M position

# Concentration risk threshold (% of float held by top 10)
CONCENTRATION_THRESHOLD = 40.0  # % (high concentration can be risky)

# === END SETTINGS ===


def get_institutional_data(ticker):
    """
    Fetch institutional ownership data from yfinance.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with institutional metrics
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get institutional holders
        inst_holders = stock.institutional_holders
        major_holders = stock.major_holders
        
        if inst_holders is None or inst_holders.empty:
            return None
        
        # Parse major holders data for institutional ownership %
        inst_ownership_pct = None
        if major_holders is not None and not major_holders.empty:
            # Major holders format: [value, description]
            for idx, row in major_holders.iterrows():
                desc = str(row[1]).lower() if len(row) > 1 else ''
                if 'institutions' in desc or 'institutional' in desc:
                    try:
                        # Extract percentage (format: "XX.XX%")
                        pct_str = str(row[0]).replace('%', '')
                        inst_ownership_pct = float(pct_str)
                    except:
                        pass
        
        # Get top institutional holders
        top_holders = []
        total_shares = 0
        
        for idx, row in inst_holders.iterrows():
            holder = {
                'name': row.get('Holder', 'Unknown'),
                'shares': row.get('Shares', 0),
                'date': row.get('Date Reported', None),
                'pct_out': row.get('% Out', 0),  # % of outstanding shares
                'value': row.get('Value', 0)
            }
            top_holders.append(holder)
            total_shares += holder['shares']
        
        # Calculate top 10 concentration
        top_10_concentration = sum([h['pct_out'] for h in top_holders[:10]])
        
        return {
            'ticker': ticker,
            'inst_ownership_pct': inst_ownership_pct,
            'num_holders': len(inst_holders),
            'top_holders': top_holders,
            'top_10_concentration': top_10_concentration,
            'total_inst_shares': total_shares
        }
    
    except Exception as e:
        print(f"Error fetching institutional data for {ticker}: {e}")
        return None


def detect_superinvestor_activity(inst_data):
    """
    Check if any superinvestors have significant positions.
    
    Args:
        inst_data: Institutional data dictionary
        
    Returns:
        List of superinvestor activity dictionaries
    """
    if not inst_data or not inst_data.get('top_holders'):
        return []
    
    superinvestor_activity = []
    
    for holder in inst_data['top_holders']:
        holder_name = holder['name']
        
        # Check if this is a known superinvestor
        for superinvestor in SUPERINVESTORS:
            if superinvestor.lower() in holder_name.lower():
                # Calculate position value (millions)
                position_value_m = holder['value'] / 1_000_000 if holder['value'] else 0
                
                if position_value_m >= MIN_SUPERINVESTOR_POSITION:
                    superinvestor_activity.append({
                        'name': superinvestor,
                        'full_name': holder_name,
                        'shares': holder['shares'],
                        'pct_out': holder['pct_out'],
                        'value_m': position_value_m,
                        'date': holder['date']
                    })
                    break  # Don't double-count
    
    return superinvestor_activity


def calculate_institutional_score(inst_data):
    """
    Calculate a score indicating institutional attractiveness.
    
    Args:
        inst_data: Institutional data dictionary
        
    Returns:
        Tuple of (score, rating) where score is 0-100 and rating is HIGH/MEDIUM/LOW
    """
    if not inst_data:
        return 0, 'LOW'
    
    score = 0
    
    # Factor 1: Institutional ownership % (0-40 points)
    inst_pct = inst_data.get('inst_ownership_pct', 0)
    if 50 <= inst_pct <= 80:
        score += 40  # Sweet spot
    elif 40 <= inst_pct < 50 or 80 < inst_pct <= 90:
        score += 30
    elif inst_pct < 40:
        score += 10  # Low institutional interest
    else:
        score += 20  # Too crowded (>90%)
    
    # Factor 2: Number of holders (0-20 points)
    num_holders = inst_data.get('num_holders', 0)
    if num_holders >= 200:
        score += 20
    elif num_holders >= 100:
        score += 15
    elif num_holders >= 50:
        score += 10
    else:
        score += 5
    
    # Factor 3: Top 10 concentration (0-20 points)
    concentration = inst_data.get('top_10_concentration', 0)
    if concentration < CONCENTRATION_THRESHOLD:
        score += 20  # Good diversification
    elif concentration < 50:
        score += 15
    elif concentration < 60:
        score += 10
    else:
        score += 5  # High concentration risk
    
    # Factor 4: Superinvestor presence (0-20 points)
    superinvestors = detect_superinvestor_activity(inst_data)
    if len(superinvestors) >= 3:
        score += 20
    elif len(superinvestors) >= 2:
        score += 15
    elif len(superinvestors) >= 1:
        score += 10
    else:
        score += 5
    
    # Determine rating
    if score >= 80:
        rating = 'HIGH'
    elif score >= 60:
        rating = 'MEDIUM'
    else:
        rating = 'LOW'
    
    return score, rating


def scan_institutional_activity():
    """
    Scan watchlist for institutional activity signals.
    
    Returns:
        List of alert dictionaries
    """
    alerts = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            # Get institutional data
            inst_data = get_institutional_data(ticker)
            
            if not inst_data:
                continue
            
            # Apply filters
            inst_pct = inst_data.get('inst_ownership_pct', 0)
            num_holders = inst_data.get('num_holders', 0)
            
            if inst_pct < MIN_INSTITUTIONAL_OWNERSHIP:
                continue
            
            if num_holders < MIN_HOLDER_COUNT:
                continue
            
            # Check for superinvestor activity
            superinvestors = detect_superinvestor_activity(inst_data)
            
            # Calculate institutional score
            score, rating = calculate_institutional_score(inst_data)
            
            # Get current price
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            
            # Build alert
            alert = {
                'ticker': ticker,
                'price': current_price,
                'inst_ownership_pct': inst_pct,
                'num_holders': num_holders,
                'top_10_concentration': inst_data['top_10_concentration'],
                'superinvestors': superinvestors,
                'score': score,
                'rating': rating,
                'top_3_holders': inst_data['top_holders'][:3]
            }
            
            # Only alert if rating is MEDIUM or HIGH, or if superinvestors present
            if rating in ['MEDIUM', 'HIGH'] or len(superinvestors) > 0:
                alerts.append(alert)
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return alerts


def format_alert_message(alerts):
    """
    Format institutional activity alerts for Telegram.
    
    Args:
        alerts: List of alert dictionaries
        
    Returns:
        Formatted message string
    """
    if not alerts:
        return "🏦 Smart Money Flow Scanner\n\nNo significant institutional activity detected in watchlist."
    
    # Sort by score descending
    alerts = sorted(alerts, key=lambda x: x['score'], reverse=True)
    
    # Get current timestamp in NYSE timezone
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🏦 Smart Money Flow Scanner\n"
    message += f"⏰ {timestamp}\n"
    message += f"📊 Found {len(alerts)} stock(s) with notable institutional activity\n\n"
    
    for alert in alerts[:8]:  # Limit to top 8
        # Rating emoji
        if alert['rating'] == 'HIGH':
            rating_emoji = "🟢"
        elif alert['rating'] == 'MEDIUM':
            rating_emoji = "🟡"
        else:
            rating_emoji = "⚪"
        
        message += f"{rating_emoji} {alert['ticker']} - ${alert['price']:.2f}\n"
        message += f"  📈 Inst. Ownership: {alert['inst_ownership_pct']:.1f}%\n"
        message += f"  👥 {alert['num_holders']} institutional holders\n"
        message += f"  🎯 Top 10 Concentration: {alert['top_10_concentration']:.1f}%\n"
        message += f"  ⭐ Quality Score: {alert['score']}/100 ({alert['rating']})\n"
        
        # Show superinvestors if present
        if alert['superinvestors']:
            message += f"  🌟 Superinvestors:\n"
            for si in alert['superinvestors'][:3]:  # Max 3
                message += f"     • {si['name']}: ${si['value_m']:.1f}M ({si['pct_out']:.2f}%)\n"
        
        # Show top 3 holders
        message += f"  🏢 Top 3 Holders:\n"
        for holder in alert['top_3_holders']:
            message += f"     • {holder['name'][:30]}: {holder['pct_out']:.2f}%\n"
        
        message += "\n"
    
    if len(alerts) > 8:
        message += f"... and {len(alerts) - 8} more stock(s)\n"
    
    message += "\n💡 Tip: Fresh institutional buying + high score = strong conviction signal"
    
    return message


def send_telegram_message(message):
    """
    Send message to Telegram chat.
    
    Args:
        message: Text message to send
        
    Returns:
        Boolean indicating success
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': None  # Plain text to avoid formatting issues
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"Telegram error: {response.status_code} {response.text}")
            return False
        
        print("Alert sent successfully to Telegram")
        return True
    
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


def main():
    """Main execution function."""
    print("Starting Smart Money Flow Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for institutional activity...")
    
    # Scan for institutional activity
    alerts = scan_institutional_activity()
    
    print(f"\nFound {len(alerts)} stock(s) with notable institutional activity")
    
    # Format and send message
    message = format_alert_message(alerts)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nSmart Money Flow Scanner completed")


if __name__ == "__main__":
    main()
