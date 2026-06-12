#!/usr/bin/env python3
"""
Financial Health Signal Scanner
Detects stocks with strong financial health scores (Altman Z-Score, Piotroski Score).
Uses FMP API for financial scoring data.
"""

import os
import sys
import json
from datetime import datetime
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
MIN_ALTMAN_Z = 3.0  # "Safe" zone for Altman Z-Score
MIN_PIOTROSKI = 7  # High quality (out of 9)
MIN_SCORE_MEDIUM = 7
MIN_SCORE_HIGH = 11

def send_telegram_message(message):
    """Send message via Telegram bot"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit
    if len(message) > 4096:
        message = message[:4090] + "\n\n[...]"
    
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

def get_financial_scores(ticker):
    """Fetch financial scores from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return None
    
    url = f"https://financialmodelingprep.com/api/v4/score"
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
        print(f"Error fetching financial scores for {ticker}: {e}")
        return None

def get_financial_ratios(ticker):
    """Fetch key financial ratios from FMP"""
    if not FMP_API_KEY:
        print("FMP API key not configured")
        return None
    
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}"
    params = {
        'limit': 1,
        'apikey': FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        else:
            return None
    except Exception as e:
        print(f"Error fetching ratios for {ticker}: {e}")
        return None

def analyze_financial_health(ticker):
    """Analyze financial health and generate score"""
    try:
        # Get financial scores
        scores = get_financial_scores(ticker)
        
        if not scores:
            return None
        
        # Get stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)
        
        if current_price <= 0:
            return None
        
        # Extract scores
        altman_z = scores.get('altmanZScore', 0)
        piotroski = scores.get('piotroskiScore', 0)
        
        # Get additional ratios
        ratios = get_financial_ratios(ticker)
        
        current_ratio = ratios.get('currentRatio', 0) if ratios else 0
        debt_to_equity = ratios.get('debtEquityRatio', 0) if ratios else 0
        roe = ratios.get('returnOnEquity', 0) if ratios else 0
        roa = ratios.get('returnOnAssets', 0) if ratios else 0
        gross_margin = ratios.get('grossProfitMargin', 0) if ratios else 0
        
        # Calculate score (0-16 points)
        score = 0
        score_details = []
        
        # Altman Z-Score (0-5 points)
        if altman_z >= 3.0:
            score += 5
            score_details.append(f"Altman Z-Score: {altman_z:.2f} - Safe zone (+5)")
        elif altman_z >= 2.6:
            score += 3
            score_details.append(f"Altman Z-Score: {altman_z:.2f} - Grey zone (+3)")
        elif altman_z >= 1.8:
            score += 1
            score_details.append(f"Altman Z-Score: {altman_z:.2f} - Caution zone (+1)")
        else:
            score_details.append(f"Altman Z-Score: {altman_z:.2f} - Distress zone")
        
        # Piotroski Score (0-4 points)
        if piotroski >= 8:
            score += 4
            score_details.append(f"Piotroski Score: {piotroski}/9 - Excellent (+4)")
        elif piotroski >= MIN_PIOTROSKI:
            score += 3
            score_details.append(f"Piotroski Score: {piotroski}/9 - Strong (+3)")
        elif piotroski >= 5:
            score += 2
            score_details.append(f"Piotroski Score: {piotroski}/9 - Average (+2)")
        else:
            score_details.append(f"Piotroski Score: {piotroski}/9 - Weak")
        
        # Current Ratio (0-2 points) - liquidity
        if current_ratio >= 2.0:
            score += 2
            score_details.append(f"Current Ratio: {current_ratio:.2f} - Excellent liquidity (+2)")
        elif current_ratio >= 1.5:
            score += 1
            score_details.append(f"Current Ratio: {current_ratio:.2f} - Good liquidity (+1)")
        
        # Debt to Equity (0-2 points) - leverage
        if debt_to_equity <= 0.3:
            score += 2
            score_details.append(f"D/E Ratio: {debt_to_equity:.2f} - Low leverage (+2)")
        elif debt_to_equity <= 0.5:
            score += 1
            score_details.append(f"D/E Ratio: {debt_to_equity:.2f} - Moderate leverage (+1)")
        
        # Return on Equity (0-2 points)
        if roe >= 0.20:  # 20%+
            score += 2
            score_details.append(f"ROE: {roe*100:.1f}% - Excellent (+2)")
        elif roe >= 0.15:  # 15%+
            score += 1
            score_details.append(f"ROE: {roe*100:.1f}% - Good (+1)")
        
        # Gross Margin (0-1 point)
        if gross_margin >= 0.40:  # 40%+
            score += 1
            score_details.append(f"Gross Margin: {gross_margin*100:.1f}% - Strong (+1)")
        
        # Determine quality based on minimum thresholds
        meets_altman = altman_z >= MIN_ALTMAN_Z
        meets_piotroski = piotroski >= MIN_PIOTROSKI
        
        # Must meet at least one key threshold
        if not (meets_altman or meets_piotroski):
            return None
        
        if score >= MIN_SCORE_HIGH:
            quality = "HIGH"
        elif score >= MIN_SCORE_MEDIUM:
            quality = "MEDIUM"
        else:
            quality = None
        
        if quality is None:
            return None
        
        # Get historical performance for context
        hist = stock.history(period='3mo')
        if not hist.empty:
            month_ago_price = hist['Close'].iloc[max(0, len(hist)-21)]
            momentum_pct = ((current_price - month_ago_price) / month_ago_price) * 100
        else:
            momentum_pct = 0
        
        return {
            'ticker': ticker,
            'current_price': current_price,
            'market_cap': market_cap,
            'altman_z': altman_z,
            'piotroski': piotroski,
            'current_ratio': current_ratio,
            'debt_to_equity': debt_to_equity,
            'roe': roe,
            'roa': roa,
            'gross_margin': gross_margin,
            'momentum_pct': momentum_pct,
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
    
    message = "💪 <b>Financial Health Signals</b>\n\n"
    
    for signal in signals:
        quality_emoji = "🔥" if signal['quality'] == "HIGH" else "⚡"
        
        message += f"{quality_emoji} <b>{signal['ticker']}</b>\n"
        message += f"Price: ${signal['current_price']:.2f}\n"
        message += f"Market Cap: ${signal['market_cap']/1e9:.2f}B\n"
        message += f"Altman Z-Score: {signal['altman_z']:.2f}\n"
        message += f"Piotroski Score: {signal['piotroski']}/9\n"
        message += f"Current Ratio: {signal['current_ratio']:.2f}\n"
        message += f"D/E Ratio: {signal['debt_to_equity']:.2f}\n"
        message += f"ROE: {signal['roe']*100:.1f}%\n"
        message += f"Gross Margin: {signal['gross_margin']*100:.1f}%\n"
        message += f"Momentum: {signal['momentum_pct']:+.1f}% (1M)\n"
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
    print("Financial Health Signal Scanner")
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
        
        signal = analyze_financial_health(ticker)
        
        if signal:
            signals.append(signal)
            print(f"  ✓ Signal generated: {signal['quality']} quality, score {signal['score']}/16")
        else:
            print(f"  Does not meet financial health criteria")
        
        time.sleep(0.3)  # Rate limiting
    
    # Sort by score
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"Found {len(signals)} financial health signals")
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
