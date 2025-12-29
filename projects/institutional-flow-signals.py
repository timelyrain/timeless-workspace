#!/usr/bin/env python3
"""
Institutional Flow Signal Scanner
Detects significant institutional ownership changes from 13F filings.
Uses FMP API for institutional ownership data.
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
MIN_OWNERSHIP_CHANGE = 5  # Minimum % change in institutional ownership
MIN_NEW_POSITIONS = 3  # Minimum number of new institutional positions
MIN_POSITION_VALUE = 10_000_000  # $10M minimum position value
MIN_SCORE_MEDIUM = 7
MIN_SCORE_HIGH = 11

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

def get_institutional_ownership(ticker):
    """Fetch institutional ownership data from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return None
    
    url = f"https://financialmodelingprep.com/api/v3/institutional-ownership/symbol-ownership"
    params = {
        'symbol': ticker,
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data if data else None
        else:
            print(f"FMP API error for {ticker}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching institutional data for {ticker}: {e}")
        return None

def get_institutional_holders_list(ticker):
    """Fetch list of institutional holders from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return []
    
    url = f"https://financialmodelingprep.com/api/v3/institutional-holder/{ticker}"
    params = {
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data if data else []
        else:
            print(f"FMP API error for {ticker}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching institutional holders for {ticker}: {e}")
        return []

def analyze_institutional_flow(ticker):
    """Analyze institutional ownership changes and generate score"""
    try:
        # Get institutional ownership data
        ownership_data = get_institutional_ownership(ticker)
        holders_data = get_institutional_holders_list(ticker)
        
        if not ownership_data or not holders_data:
            return None
        
        # Get stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)
        
        if current_price <= 0 or market_cap <= 0:
            return None
        
        # Analyze ownership changes
        total_invested = 0
        total_shares = 0
        new_positions = 0
        increased_positions = 0
        major_investors = []
        
        for holder in holders_data[:20]:  # Top 20 holders
            shares = holder.get('sharesNumber', 0)
            change = holder.get('change', 0)
            investor_name = holder.get('investorName', 'Unknown')
            report_date = holder.get('reportDate', '')
            
            if shares == 0:
                continue
            
            position_value = shares * current_price
            
            # Track significant positions
            if position_value >= MIN_POSITION_VALUE:
                total_shares += shares
                total_invested += position_value
                
                # New position (change equals current shares)
                if abs(change - shares) < 1000:  # Allow small rounding error
                    new_positions += 1
                    major_investors.append({
                        'name': investor_name,
                        'action': 'NEW',
                        'shares': shares,
                        'value': position_value
                    })
                # Increased position
                elif change > 0:
                    increased_positions += 1
                    change_pct = (change / (shares - change)) * 100 if shares > change else 0
                    if change_pct >= MIN_OWNERSHIP_CHANGE:
                        major_investors.append({
                            'name': investor_name,
                            'action': 'INCREASED',
                            'change_pct': change_pct,
                            'shares': shares,
                            'value': position_value
                        })
        
        # Get ownership percentage
        shares_outstanding = info.get('sharesOutstanding', 0)
        institutional_pct = (total_shares / shares_outstanding * 100) if shares_outstanding > 0 else 0
        
        # Calculate score (0-16 points)
        score = 0
        score_details = []
        
        # New positions (0-4 points)
        if new_positions >= 5:
            score += 4
            score_details.append(f"Many new positions: {new_positions} institutions (+4)")
        elif new_positions >= MIN_NEW_POSITIONS:
            score += 3
            score_details.append(f"New positions: {new_positions} institutions (+3)")
        elif new_positions >= 2:
            score += 2
            score_details.append(f"Some new positions: {new_positions} institutions (+2)")
        
        # Increased positions (0-3 points)
        if increased_positions >= 10:
            score += 3
            score_details.append(f"Many increases: {increased_positions} institutions (+3)")
        elif increased_positions >= 5:
            score += 2
            score_details.append(f"Several increases: {increased_positions} institutions (+2)")
        elif increased_positions >= 3:
            score += 1
            score_details.append(f"Some increases: {increased_positions} institutions (+1)")
        
        # Total institutional investment (0-4 points)
        if total_invested >= 1_000_000_000:  # $1B+
            score += 4
            score_details.append(f"Major investment: ${total_invested/1e9:.2f}B (+4)")
        elif total_invested >= 500_000_000:  # $500M+
            score += 3
            score_details.append(f"Significant investment: ${total_invested/1e6:.0f}M (+3)")
        elif total_invested >= 100_000_000:  # $100M+
            score += 2
            score_details.append(f"Substantial investment: ${total_invested/1e6:.0f}M (+2)")
        
        # Institutional ownership percentage (0-3 points)
        if institutional_pct >= 80:
            score += 3
            score_details.append(f"Very high ownership: {institutional_pct:.1f}% (+3)")
        elif institutional_pct >= 60:
            score += 2
            score_details.append(f"High ownership: {institutional_pct:.1f}% (+2)")
        elif institutional_pct >= 40:
            score += 1
            score_details.append(f"Moderate ownership: {institutional_pct:.1f}% (+1)")
        
        # Quality of investors (0-2 points) - presence of major funds
        major_fund_keywords = ['vanguard', 'blackrock', 'state street', 'fidelity', 'capital']
        major_funds_present = sum(1 for inv in major_investors 
                                 if any(keyword in inv['name'].lower() for keyword in major_fund_keywords))
        if major_funds_present >= 3:
            score += 2
            score_details.append(f"Major funds present: {major_funds_present} (+2)")
        elif major_funds_present >= 1:
            score += 1
            score_details.append(f"Major fund present: {major_funds_present} (+1)")
        
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
            'market_cap': market_cap,
            'new_positions': new_positions,
            'increased_positions': increased_positions,
            'total_invested': total_invested,
            'institutional_pct': institutional_pct,
            'major_investors': major_investors[:5],  # Top 5
            'score': score,
            'max_score': 16,
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
    
    message = "🏛️ <b>Institutional Flow Signals</b>\n\n"
    
    for signal in signals:
        quality_emoji = "🔥" if signal['quality'] == "HIGH" else "⚡"
        
        message += f"{quality_emoji} <b>{signal['ticker']}</b>\n"
        message += f"Price: ${signal['current_price']:.2f}\n"
        message += f"Market Cap: ${signal['market_cap']/1e9:.2f}B\n"
        message += f"New Positions: {signal['new_positions']} institutions\n"
        message += f"Increased: {signal['increased_positions']} institutions\n"
        message += f"Total Invested: ${signal['total_invested']/1e9:.2f}B\n"
        message += f"Inst. Ownership: {signal['institutional_pct']:.1f}%\n"
        message += f"Quality: <b>{signal['quality']}</b>\n"
        message += f"Score: {signal['score']}/{signal['max_score']}\n"
        
        if signal['score_details']:
            message += "\nScore Breakdown:\n"
            for detail in signal['score_details']:
                message += f"  • {detail}\n"
        
        if signal['major_investors']:
            message += "\nTop Investors:\n"
            for inv in signal['major_investors']:
                action = inv['action']
                name = inv['name'][:30]  # Truncate long names
                value_str = f"${inv['value']/1e6:.0f}M"
                
                if action == 'NEW':
                    message += f"  🆕 {name}: {value_str}\n"
                else:
                    change_pct = inv.get('change_pct', 0)
                    message += f"  📈 {name}: +{change_pct:.1f}% ({value_str})\n"
        
        message += "\n" + "="*40 + "\n\n"
    
    return message

def main():
    print("=" * 60)
    print("Institutional Flow Signal Scanner")
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
        
        signal = analyze_institutional_flow(ticker)
        
        if signal:
            signals.append(signal)
            print(f"  ✓ Signal generated: {signal['quality']} quality, score {signal['score']}/16")
        else:
            print(f"  No significant institutional flow")
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by score
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"Found {len(signals)} institutional flow signals")
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
