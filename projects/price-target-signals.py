#!/usr/bin/env python3
"""
Price Target Gap Signal Scanner
Detects stocks with significant upside to analyst price targets.
Uses FMP API for analyst price target consensus data.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import yfinance as yf
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from projects.watchlist_loader import load_watchlist

# Load environment variables
load_dotenv()

# Configuration
FMP_API_KEY = os.getenv('FMP_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Signal thresholds
MIN_UPSIDE_PCT = 15  # Minimum upside to target price
MIN_ANALYSTS = 5  # Minimum number of analysts covering
MIN_RECENT_UPGRADES = 2  # Minimum recent upgrades in last 30 days
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

def get_price_target_consensus(ticker):
    """Fetch analyst price target consensus from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return None
    
    url = f"https://financialmodelingprep.com/api/v4/price-target-consensus"
    params = {
        'symbol': ticker,
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        else:
            print(f"FMP API error for {ticker}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching price target for {ticker}: {e}")
        return None

def get_recent_upgrades_downgrades(ticker):
    """Fetch recent analyst upgrades/downgrades from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return []
    
    url = f"https://financialmodelingprep.com/api/v3/upgrades-downgrades"
    params = {
        'symbol': ticker,
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data if data else []
        else:
            return []
    except Exception as e:
        print(f"Error fetching upgrades/downgrades for {ticker}: {e}")
        return []

def analyze_price_target_gap(ticker):
    """Analyze price target gap and generate score"""
    try:
        # Get price target consensus
        consensus = get_price_target_consensus(ticker)
        
        if not consensus:
            return None
        
        # Get stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        if current_price <= 0:
            return None
        
        # Extract consensus data
        target_high = consensus.get('targetHigh', 0)
        target_low = consensus.get('targetLow', 0)
        target_consensus = consensus.get('targetConsensus', 0)
        target_median = consensus.get('targetMedian', 0)
        num_analysts = consensus.get('analystCount', 0)
        
        if target_consensus <= 0 or num_analysts < MIN_ANALYSTS:
            return None
        
        # Calculate upside
        upside_pct = ((target_consensus - current_price) / current_price) * 100
        upside_high_pct = ((target_high - current_price) / current_price) * 100
        
        if upside_pct < MIN_UPSIDE_PCT:
            return None
        
        # Get recent upgrades/downgrades
        upgrades_downgrades = get_recent_upgrades_downgrades(ticker)
        
        # Filter recent actions (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_upgrades = 0
        recent_downgrades = 0
        recent_actions = []
        
        for action in upgrades_downgrades[:20]:  # Check last 20 actions
            try:
                action_date = datetime.strptime(action.get('publishedDate', '')[:10], '%Y-%m-%d')
                if action_date >= cutoff_date:
                    grade_current = action.get('gradingCompany', 'Unknown')
                    action_type = action.get('action', '').lower()
                    
                    if 'upgrade' in action_type or 'up' in action_type:
                        recent_upgrades += 1
                        recent_actions.append(f"↗️ {grade_current}")
                    elif 'downgrade' in action_type or 'down' in action_type:
                        recent_downgrades += 1
                        recent_actions.append(f"↘️ {grade_current}")
            except:
                continue
        
        # Get historical data for momentum
        hist = stock.history(period='3mo')
        if hist.empty:
            return None
        
        # Calculate momentum
        month_ago_price = hist['Close'].iloc[max(0, len(hist)-21)]
        price_momentum_pct = ((current_price - month_ago_price) / month_ago_price) * 100
        
        # Calculate score (0-15 points)
        score = 0
        score_details = []
        
        # Upside potential (0-5 points)
        if upside_pct >= 40:
            score += 5
            score_details.append(f"Huge upside: {upside_pct:.1f}% to target (+5)")
        elif upside_pct >= 30:
            score += 4
            score_details.append(f"Very strong upside: {upside_pct:.1f}% (+4)")
        elif upside_pct >= 20:
            score += 3
            score_details.append(f"Strong upside: {upside_pct:.1f}% (+3)")
        elif upside_pct >= MIN_UPSIDE_PCT:
            score += 2
            score_details.append(f"Good upside: {upside_pct:.1f}% (+2)")
        
        # Recent upgrades (0-4 points)
        if recent_upgrades >= 4:
            score += 4
            score_details.append(f"Multiple upgrades: {recent_upgrades} in 30 days (+4)")
        elif recent_upgrades >= MIN_RECENT_UPGRADES:
            score += 3
            score_details.append(f"Recent upgrades: {recent_upgrades} in 30 days (+3)")
        elif recent_upgrades >= 1:
            score += 2
            score_details.append(f"Recent upgrade: {recent_upgrades} in 30 days (+2)")
        
        # Analyst coverage (0-2 points)
        if num_analysts >= 15:
            score += 2
            score_details.append(f"Strong coverage: {num_analysts} analysts (+2)")
        elif num_analysts >= 10:
            score += 1
            score_details.append(f"Good coverage: {num_analysts} analysts (+1)")
        
        # Price momentum (0-2 points) - is it already moving?
        if price_momentum_pct > 10:
            score += 2
            score_details.append(f"Strong momentum: +{price_momentum_pct:.1f}% (1M) (+2)")
        elif price_momentum_pct > 5:
            score += 1
            score_details.append(f"Positive momentum: +{price_momentum_pct:.1f}% (1M) (+1)")
        
        # Target range consistency (0-2 points) - are analysts aligned?
        if target_high > 0 and target_low > 0:
            range_spread = ((target_high - target_low) / target_consensus) * 100
            if range_spread < 20:  # Tight range = consensus
                score += 2
                score_details.append(f"High consensus: {range_spread:.0f}% spread (+2)")
            elif range_spread < 40:
                score += 1
                score_details.append(f"Moderate consensus: {range_spread:.0f}% spread (+1)")
        
        # Penalty for recent downgrades
        if recent_downgrades > recent_upgrades:
            score = max(0, score - 2)
            score_details.append(f"Recent downgrades: {recent_downgrades} (-2)")
        
        # Determine quality
        if score >= MIN_SCORE_HIGH:
            quality = "HIGH"
        elif score >= MIN_SCORE_MEDIUM:
            quality = "MEDIUM"
        else:
            quality = None
        
        if quality is None:
            return None
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'target_low': target_low,
            'target_consensus': target_consensus,
            'target_high': target_high,
            'upside_pct': upside_pct,
            'upside_high_pct': upside_high_pct,
            'num_analysts': num_analysts,
            'recent_upgrades': recent_upgrades,
            'recent_downgrades': recent_downgrades,
            'recent_actions': recent_actions[:5],  # Top 5
            'momentum_pct': price_momentum_pct,
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
    
    message = "🎯 <b>Price Target Gap Signals</b>\n\n"
    
    for signal in signals:
        quality_emoji = "🔥" if signal['quality'] == "HIGH" else "⚡"
        
        message += f"{quality_emoji} <b>{signal['ticker']}</b>\n"
        message += f"Current: ${signal['current_price']:.2f}\n"
        message += f"Target: ${signal['target_consensus']:.2f} (↗️ {signal['upside_pct']:.1f}%)\n"
        message += f"Range: ${signal['target_low']:.2f} - ${signal['target_high']:.2f}\n"
        message += f"High Target: ${signal['target_high']:.2f} (↗️ {signal['upside_high_pct']:.1f}%)\n"
        message += f"Analysts: {signal['num_analysts']}\n"
        message += f"Recent: {signal['recent_upgrades']} ↗️ / {signal['recent_downgrades']} ↘️\n"
        message += f"Momentum: {signal['momentum_pct']:+.1f}% (1M)\n"
        message += f"Quality: <b>{signal['quality']}</b>\n"
        message += f"Score: {signal['score']}/{signal['max_score']}\n"
        
        if signal['score_details']:
            message += "\nScore Breakdown:\n"
            for detail in signal['score_details']:
                message += f"  • {detail}\n"
        
        if signal['recent_actions']:
            message += "\nRecent Actions:\n"
            for action in signal['recent_actions']:
                message += f"  {action}\n"
        
        message += "\n" + "="*40 + "\n\n"
    
    return message

def main():
    print("=" * 60)
    print("Price Target Gap Signal Scanner")
    print("=" * 60)
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load watchlist
    watchlist = load_watchlist()
    print(f"Loaded {len(watchlist)} symbols from watchlist")
    print(f"Symbols: {', '.join(watchlist)}\n")
    
    # Analyze each symbol
    signals = []
    
    for ticker in watchlist:
        print(f"Analyzing {ticker}...")
        
        signal = analyze_price_target_gap(ticker)
        
        if signal:
            signals.append(signal)
            print(f"  ✓ Signal generated: {signal['quality']} quality, score {signal['score']}/15")
        else:
            print(f"  No significant price target gap")
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by score
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"Found {len(signals)} price target gap signals")
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
