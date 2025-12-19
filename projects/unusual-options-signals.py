"""
📊 UNUSUAL OPTIONS ACTIVITY SCANNER
====================================

WHAT IT DOES:
-------------
Detects unusual options activity that may signal upcoming moves in stocks.
Tracks large institutional orders, abnormal volume, and aggressive positioning
that often precedes significant price movements.

This scanner identifies "smart money" moves by looking for:
  1. Unusually high options volume vs historical average
  2. Large premium spent (big money flowing in)
  3. Bullish vs Bearish positioning
  4. Call/Put ratio anomalies

FEATURES:
---------
✅ Unusual Volume Detection - Spots abnormal options activity
✅ Premium Flow Analysis - Tracks where the big money is going
✅ Call/Put Ratio - Identifies directional bias
✅ Historical Comparison - Compares to 20-day average volume
✅ Real-time Alerts - Get notified of institutional moves
✅ Telegram Integration - Instant notifications

KEY SETTINGS (Customize below):
-------------------------------
VOLUME_THRESHOLD: Unusual volume multiplier
  - 3.0x = Very unusual activity (default)
  - 2.0x = Moderately unusual (more signals)
  - 5.0x = Extremely unusual only (rare, high conviction)

MIN_PREMIUM_FLOW: Minimum dollar flow to consider
  - $500,000 = Medium size (default)
  - $1,000,000 = Large institutional only
  - $250,000 = Catch smaller flows

CALL_PUT_RATIO_THRESHOLD: What ratio indicates bias
  - 2.0 = Bullish if C/P > 2.0, Bearish if < 0.5 (default)
  - 3.0 = More strict bullish/bearish identification
  - 1.5 = More sensitive to directional bias

NOTE:
-----
This scanner requires options data which may need:
1. yfinance options data (basic, free)
2. OR paid data providers for real-time flow (Unusual Whales, Flow Algo, etc.)

Currently using yfinance for basic unusual activity detection.
For production use, consider integrating with:
  - Unusual Whales API
  - FlowAlgo API
  - CBOE Options Data Feed

USAGE TIPS:
-----------
• Best during market hours when options are actively traded
• Combine with breakout scanner for confirmation
• Large put flows can indicate hedging OR bearish bets
• Large call flows often precede rallies
• Watch for sweep orders (aggressive fills across exchanges)
• Check expiration dates - near-term = urgent, far-term = long conviction
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
import pandas as pd
from watchlist_loader import load_watchlist

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- CONFIGURATION ---
# Watchlist - same as other scanners for consistency
WATCHLIST = load_watchlist()

# Telegram Credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==========================================
# 🎯 OPTIONS SCANNER SETTINGS - CUSTOMIZE HERE!
# ==========================================

# Unusual volume threshold (multiplier of average)
# 3.0x = very unusual | 2.0x = more signals | 5.0x = extremely rare
VOLUME_THRESHOLD = 3.0

# Minimum premium flow to report (in dollars)
# $500K = medium institutional | $1M = large only | $250K = smaller flows
MIN_PREMIUM_FLOW = 500000

# Call/Put ratio thresholds for directional bias
# Bullish if ratio > threshold, Bearish if < (1/threshold)
# 2.0 = balanced | 3.0 = strict | 1.5 = sensitive
CALL_PUT_RATIO_THRESHOLD = 2.0

# Lookback period for average volume calculation (days)
LOOKBACK_DAYS = 20

def send_telegram_message(message):
    """Sends alert to Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not found. Printing to console instead.")
        print(message)
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Remove markdown formatting to avoid Telegram parsing errors
    plain_message = message.replace('**', '').replace('_', '')
    
    # Telegram has a 4096 character limit
    if len(plain_message) > 4096:
        plain_message = plain_message[:4090] + "\n\n[...]"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": plain_message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✓ Telegram alert sent successfully!")
    except Exception as e:
        print(f"✗ Telegram error: {e}")

def get_options_activity(ticker):
    """
    Fetches options data for a ticker and analyzes for unusual activity
    Returns dict with activity details or None if no unusual activity
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get current price
        hist = stock.history(period="1d")
        if hist.empty:
            return None
        current_price = hist['Close'].iloc[-1]
        
        # Get options expiration dates
        expirations = stock.options
        if not expirations or len(expirations) == 0:
            return None
        
        # Check nearest expiration (most active)
        nearest_exp = expirations[0]
        opt_chain = stock.option_chain(nearest_exp)
        
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        if calls.empty or puts.empty:
            return None
        
        # Calculate total volume and open interest
        call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
        put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
        total_volume = call_volume + put_volume
        
        call_oi = calls['openInterest'].sum() if 'openInterest' in calls.columns else 0
        put_oi = puts['openInterest'].sum() if 'openInterest' in puts.columns else 0
        
        # Estimate premium flow (volume * average premium)
        if 'lastPrice' in calls.columns and 'volume' in calls.columns:
            call_premium = (calls['lastPrice'] * calls['volume'] * 100).sum()  # *100 for contract multiplier
        else:
            call_premium = 0
            
        if 'lastPrice' in puts.columns and 'volume' in puts.columns:
            put_premium = (puts['lastPrice'] * puts['volume'] * 100).sum()
        else:
            put_premium = 0
            
        total_premium = call_premium + put_premium
        
        # Calculate Call/Put ratio
        cp_ratio = call_volume / put_volume if put_volume > 0 else float('inf')
        
        # Get historical average volume (using open interest as proxy since we can't get historical options volume easily)
        avg_volume = (call_oi + put_oi) / LOOKBACK_DAYS if (call_oi + put_oi) > 0 else 1
        
        # Check for unusual activity
        volume_ratio = total_volume / avg_volume if avg_volume > 0 else 0
        
        # Determine if this is unusual
        is_unusual = (volume_ratio >= VOLUME_THRESHOLD and total_premium >= MIN_PREMIUM_FLOW)
        
        if not is_unusual:
            return None
        
        # Determine bias
        if cp_ratio >= CALL_PUT_RATIO_THRESHOLD:
            bias = "BULLISH 🐂"
        elif cp_ratio <= (1 / CALL_PUT_RATIO_THRESHOLD):
            bias = "BEARISH 🐻"
        else:
            bias = "NEUTRAL ⚖️"
        
        return {
            'ticker': ticker,
            'price': current_price,
            'expiration': nearest_exp,
            'call_volume': int(call_volume),
            'put_volume': int(put_volume),
            'total_volume': int(total_volume),
            'call_premium': call_premium,
            'put_premium': put_premium,
            'total_premium': total_premium,
            'cp_ratio': cp_ratio,
            'volume_ratio': volume_ratio,
            'bias': bias
        }
        
    except Exception as e:
        print(f"Error fetching options for {ticker}: {e}")
        return None

def scan_unusual_options():
    """
    Scans watchlist for unusual options activity
    """
    print("=" * 60)
    print("📊 UNUSUAL OPTIONS ACTIVITY SCANNER")
    print("=" * 60)
    
    # Get NY timezone for timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Scanning {len(WATCHLIST)} stocks for unusual options activity...")
    print(f"Criteria: >{VOLUME_THRESHOLD}x volume, >${MIN_PREMIUM_FLOW:,.0f} premium flow\n")
    
    unusual_activity = []
    
    for i, ticker in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] Checking {ticker}...", end='\r')
        activity = get_options_activity(ticker)
        if activity:
            unusual_activity.append(activity)
    
    print("\n" + "=" * 60 + "\n")
    
    # Sort by premium flow (largest first)
    unusual_activity.sort(key=lambda x: x['total_premium'], reverse=True)
    
    # Build alert message
    if unusual_activity:
        header = f"🚨 UNUSUAL OPTIONS ACTIVITY - {timestamp}\n"
        header += f"Found {len(unusual_activity)} unusual flow(s):\n"
        header += "=" * 50 + "\n\n"
        
        alerts = []
        for activity in unusual_activity:
            alert = (
                f"📊 {activity['ticker']} - ${activity['price']:.2f} {activity['bias']}\n"
                f"  • Exp: {activity['expiration']}\n"
                f"  • Volume: {activity['total_volume']:,} ({activity['volume_ratio']:.1f}x avg)\n"
                f"  • Calls: {activity['call_volume']:,} | Puts: {activity['put_volume']:,}\n"
                f"  • C/P Ratio: {activity['cp_ratio']:.2f}\n"
                f"  • Premium Flow: ${activity['total_premium']:,.0f}\n"
                f"    (Calls: ${activity['call_premium']:,.0f} | Puts: ${activity['put_premium']:,.0f})\n"
            )
            alerts.append(alert)
        
        footer = (
            f"\n{'=' * 50}\n"
            f"⚙️ Criteria: >{VOLUME_THRESHOLD}x volume, >${MIN_PREMIUM_FLOW:,.0f} flow\n"
            f"🎯 C/P Threshold: {CALL_PUT_RATIO_THRESHOLD}\n"
        )
        
        final_message = header + "\n".join(alerts) + footer
        
        print(final_message)
        send_telegram_message(final_message)
        
    else:
        no_activity_msg = (
            f"📊 Unusual Options Scanner - {timestamp}\n"
            f"No unusual activity detected.\n\n"
            f"Scanned {len(WATCHLIST)} stocks with criteria:\n"
            f"  • Volume >{VOLUME_THRESHOLD}x average\n"
            f"  • Premium flow >${MIN_PREMIUM_FLOW:,.0f}\n"
            f"  • C/P Ratio threshold: {CALL_PUT_RATIO_THRESHOLD}\n"
        )
        print(no_activity_msg)
        # Optional: comment out next line if you don't want "no activity" messages
        # send_telegram_message(no_activity_msg)

if __name__ == "__main__":
    scan_unusual_options()
