#!/usr/bin/env python3
"""
IPO Momentum Signal Scanner
Detects newly listed stocks with strong first-week momentum and institutional interest.
Uses FMP API for IPO calendar data.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import yfinance as yf
import time

# Load environment variables
load_dotenv()

# Configuration
FMP_API_KEY = os.getenv('FMP_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Signal thresholds
MIN_FIRST_DAY_GAIN = 10  # Minimum first-day pop %
MIN_VOLUME_RATIO = 2.0   # Minimum volume vs 5-day average
MIN_MARKET_CAP = 500_000_000  # $500M minimum market cap
MAX_DAYS_SINCE_IPO = 30  # Look at IPOs within last 30 days
MIN_PRICE = 10  # Minimum price to avoid penny stocks
MIN_SCORE_MEDIUM = 6
MIN_SCORE_HIGH = 10

def send_telegram_message(message):
    """Send message via Telegram bot"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def get_recent_ipos():
    """Fetch recent IPO calendar from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return []
    
    # Get IPOs from the past 60 days to ensure we catch the 30-day window
    from_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://financialmodelingprep.com/api/v3/ipo-calendar"
    params = {
        'from': from_date,
        'to': to_date,
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"FMP IPO calendar returned {len(data)} IPOs")
            return data
        else:
            print(f"FMP API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching IPO data from FMP: {e}")
        return []

def get_ipo_first_day_performance(ticker, ipo_date_str):
    """Calculate first-day performance for an IPO"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data starting from IPO date
        ipo_date = datetime.strptime(ipo_date_str, '%Y-%m-%d')
        start_date = ipo_date - timedelta(days=1)
        end_date = ipo_date + timedelta(days=5)
        
        hist = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                            end=end_date.strftime('%Y-%m-%d'))
        
        if hist.empty or len(hist) < 2:
            return None
        
        # First day's open and close
        first_day = hist.iloc[0]
        open_price = first_day['Open']
        close_price = first_day['Close']
        volume = first_day['Volume']
        
        if open_price <= 0 or close_price <= 0:
            return None
        
        first_day_gain = ((close_price - open_price) / open_price) * 100
        
        return {
            'open': open_price,
            'close': close_price,
            'first_day_gain': first_day_gain,
            'volume': volume
        }
    except Exception as e:
        print(f"Error getting first-day performance for {ticker}: {e}")
        return None

def analyze_ipo_momentum(ticker, ipo_data, first_day_perf):
    """Analyze IPO momentum and generate score"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get current data
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)
        
        if current_price < MIN_PRICE:
            return None
        
        if market_cap < MIN_MARKET_CAP:
            return None
        
        # Get recent historical data for momentum analysis
        hist = stock.history(period='1mo')
        if hist.empty or len(hist) < 5:
            return None
        
        # Calculate metrics
        recent_data = hist.tail(5)
        avg_volume = recent_data['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Price momentum since IPO
        ipo_price = first_day_perf['close']
        price_change_pct = ((current_price - ipo_price) / ipo_price) * 100
        
        # Calculate score (0-15 points)
        score = 0
        score_details = []
        
        # First-day pop (0-4 points)
        first_day_gain = first_day_perf['first_day_gain']
        if first_day_gain >= 30:
            score += 4
            score_details.append(f"Strong first-day pop: {first_day_gain:.1f}% (+4)")
        elif first_day_gain >= 20:
            score += 3
            score_details.append(f"Good first-day pop: {first_day_gain:.1f}% (+3)")
        elif first_day_gain >= MIN_FIRST_DAY_GAIN:
            score += 2
            score_details.append(f"Moderate first-day pop: {first_day_gain:.1f}% (+2)")
        
        # Continued momentum (0-3 points)
        if price_change_pct > 50:
            score += 3
            score_details.append(f"Exceptional momentum: +{price_change_pct:.1f}% since IPO (+3)")
        elif price_change_pct > 20:
            score += 2
            score_details.append(f"Strong momentum: +{price_change_pct:.1f}% since IPO (+2)")
        elif price_change_pct > 0:
            score += 1
            score_details.append(f"Positive momentum: +{price_change_pct:.1f}% since IPO (+1)")
        
        # Volume confirmation (0-3 points)
        if volume_ratio >= 3.0:
            score += 3
            score_details.append(f"Very high volume: {volume_ratio:.1f}x average (+3)")
        elif volume_ratio >= MIN_VOLUME_RATIO:
            score += 2
            score_details.append(f"High volume: {volume_ratio:.1f}x average (+2)")
        
        # Market cap size (0-2 points) - larger IPOs tend to be more stable
        if market_cap >= 5_000_000_000:  # $5B+
            score += 2
            score_details.append(f"Large cap: ${market_cap/1e9:.1f}B (+2)")
        elif market_cap >= 1_000_000_000:  # $1B+
            score += 1
            score_details.append(f"Mid cap: ${market_cap/1e9:.1f}B (+1)")
        
        # Price stability (0-3 points) - not too volatile
        recent_returns = recent_data['Close'].pct_change().dropna()
        volatility = recent_returns.std() * 100
        if volatility < 3:
            score += 3
            score_details.append(f"Low volatility: {volatility:.1f}% (+3)")
        elif volatility < 5:
            score += 2
            score_details.append(f"Moderate volatility: {volatility:.1f}% (+2)")
        elif volatility < 8:
            score += 1
            score_details.append(f"Acceptable volatility: {volatility:.1f}% (+1)")
        
        # Determine quality
        if score >= MIN_SCORE_HIGH:
            quality = "HIGH"
        elif score >= MIN_SCORE_MEDIUM:
            quality = "MEDIUM"
        else:
            quality = None  # Below threshold
        
        if quality is None:
            return None
        
        return {
            'ticker': ticker,
            'company_name': ipo_data.get('companyName', ticker),
            'ipo_date': ipo_data.get('ipoDate', 'N/A'),
            'ipo_price': ipo_price,
            'current_price': current_price,
            'first_day_gain': first_day_gain,
            'total_gain': price_change_pct,
            'market_cap': market_cap,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'score': score,
            'max_score': 15,
            'quality': quality,
            'score_details': score_details
        }
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def format_signal_message(signals):
    """Format signals into Telegram message"""
    if not signals:
        return None
    
    message = "🚀 <b>IPO Momentum Signals</b>\n\n"
    
    for signal in signals:
        quality_emoji = "🔥" if signal['quality'] == "HIGH" else "⚡"
        
        message += f"{quality_emoji} <b>{signal['ticker']}</b> - {signal['company_name']}\n"
        message += f"IPO Date: {signal['ipo_date']}\n"
        message += f"First Day: +{signal['first_day_gain']:.1f}%\n"
        message += f"Total Gain: {signal['total_gain']:+.1f}%\n"
        message += f"Price: ${signal['ipo_price']:.2f} → ${signal['current_price']:.2f}\n"
        message += f"Market Cap: ${signal['market_cap']/1e9:.2f}B\n"
        message += f"Volume: {signal['volume_ratio']:.1f}x average\n"
        message += f"Quality: <b>{signal['quality']}</b>\n"
        message += f"Score: {signal['score']}/{signal['max_score']}\n"
        
        if signal['score_details']:
            message += "\nScore Breakdown:\n"
            for detail in signal['score_details']:
                message += f"  • {detail}\n"
        
        message += "\n" + "="*40 + "\n\n"
    
    return message

def main():
    print("=" * 60)
    print("IPO Momentum Signal Scanner")
    print("=" * 60)
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fetch recent IPOs
    print("Fetching recent IPO calendar from FMP...")
    ipos = get_recent_ipos()
    
    if not ipos:
        print("No IPO data available")
        return
    
    # Filter IPOs within our time window
    cutoff_date = datetime.now() - timedelta(days=MAX_DAYS_SINCE_IPO)
    recent_ipos = []
    
    for ipo in ipos:
        try:
            ipo_date = datetime.strptime(ipo.get('ipoDate', ''), '%Y-%m-%d')
            if ipo_date >= cutoff_date:
                recent_ipos.append(ipo)
        except:
            continue
    
    print(f"Found {len(recent_ipos)} IPOs in the past {MAX_DAYS_SINCE_IPO} days")
    
    if not recent_ipos:
        print("No recent IPOs to analyze")
        return
    
    # Analyze each IPO
    signals = []
    
    for ipo in recent_ipos:
        ticker = ipo.get('symbol', '').strip()
        if not ticker:
            continue
        
        print(f"\nAnalyzing {ticker}...")
        
        # Get first-day performance
        first_day_perf = get_ipo_first_day_performance(ticker, ipo.get('ipoDate', ''))
        
        if not first_day_perf:
            print(f"  Could not get first-day data")
            continue
        
        print(f"  First day: {first_day_perf['first_day_gain']:.1f}%")
        
        if first_day_perf['first_day_gain'] < MIN_FIRST_DAY_GAIN:
            print(f"  Below minimum first-day gain threshold")
            continue
        
        # Analyze momentum
        signal = analyze_ipo_momentum(ticker, ipo, first_day_perf)
        
        if signal:
            signals.append(signal)
            print(f"  ✓ Signal generated: {signal['quality']} quality, score {signal['score']}/15")
        else:
            print(f"  Below scoring threshold")
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by score
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"Found {len(signals)} IPO momentum signals")
    print("=" * 60)
    
    if signals:
        # Send Telegram alert
        message = format_signal_message(signals)
        if message:
            print("\nSending Telegram alert...")
            if send_telegram_message(message):
                print("✓ Alert sent successfully")
            else:
                print("✗ Failed to send alert")
    
    print("\nScan complete!")

if __name__ == "__main__":
    main()
