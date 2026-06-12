"""
📈 SUPPORT/RESISTANCE BOUNCE SCANNER
====================================

WHAT IT DOES:
-------------
Identifies stocks testing key support or resistance levels with potential for
bounce or breakdown. Uses price action, volume, and technical indicators to
find high-probability reversal or continuation setups.

Key levels are where institutions often place orders, creating natural zones
of buying or selling pressure that can lead to predictable price reactions.

FEATURES:
---------
✅ Identifies 52-week highs/lows as key levels
✅ Calculates support/resistance zones
✅ Detects when price tests these levels
✅ RSI confirmation (oversold/overbought)
✅ Volume analysis on test
✅ Multiple bounces strengthen level validity
✅ Telegram alerts on high-probability setups

KEY SETTINGS (Customize below):
-------------------------------
SUPPORT_LEVEL_THRESHOLD: How close to support to alert
  - 2.0% = Near support (default)
  - 1.0% = Very close (fewer signals)
  - 3.0% = Early warning (more signals)

RESISTANCE_LEVEL_THRESHOLD: How close to resistance to alert
  - 2.0% = Near resistance (default)
  - 1.0% = Very close (fewer signals)
  - 3.0% = Early warning (more signals)

RSI_OVERSOLD: RSI level for oversold condition
  - 30 = Classic oversold (default)
  - 25 = Deeply oversold
  - 35 = Earlier signals

RSI_OVERBOUGHT: RSI level for overbought condition
  - 70 = Classic overbought (default)
  - 75 = Very overbought
  - 65 = Earlier signals

VOLUME_CONFIRMATION: Require volume spike on test
  - True = Only alert with volume (default, higher quality)
  - False = All tests regardless of volume

MIN_VOLUME_RATIO: If volume confirmation enabled
  - 1.2x = Light confirmation (default)
  - 1.5x = Moderate
  - 2.0x = Strong

SUPPORT/RESISTANCE TYPES:
-------------------------
1. HORIZONTAL LEVELS:
   • 52-week high/low
   • Previous swing highs/lows
   • Round numbers ($50, $100, etc.)

2. MOVING AVERAGES:
   • 50-day MA (intermediate trend)
   • 200-day MA (long-term trend)

3. FIBONACCI LEVELS:
   • 38.2%, 50%, 61.8% retracements

TRADING STRATEGIES:
------------------
SUPPORT BOUNCE:
  • Watch for price to test support
  • Look for RSI oversold + volume spike
  • Enter on bullish candle confirmation
  • Stop below support
  • Target: Previous resistance

RESISTANCE REJECTION:
  • Watch for price to test resistance
  • Look for RSI overbought + volume spike
  • Enter short on bearish candle confirmation
  • Stop above resistance
  • Target: Previous support

BREAKOUT:
  • Strong close above resistance on volume
  • Previous resistance becomes new support
  • Enter on retest of breakout level

BREAKDOWN:
  • Strong close below support on volume
  • Previous support becomes new resistance
  • Enter short on retest of breakdown level

USAGE TIPS:
-----------
• Multiple tests of a level make it stronger
• The longer a level holds, the more significant the eventual break
• Best setups combine support/resistance + RSI + volume
• Use previous close as stop loss reference
• Scale in/out of positions at key levels
• Watch for false breakouts (trap moves)
• Combine with sector rotation for context
"""

import yfinance as yf
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
import numpy as np
import pandas as pd
from watchlist_loader import load_watchlist

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Watchlist
WATCHLIST = load_watchlist()

# Telegram Credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==========================================
# 🎯 SUPPORT/RESISTANCE SETTINGS - CUSTOMIZE HERE!
# ==========================================

# Distance thresholds (percentage from level)
SUPPORT_LEVEL_THRESHOLD = 2.0  # Alert when within 2% of support
RESISTANCE_LEVEL_THRESHOLD = 2.0  # Alert when within 2% of resistance

# RSI thresholds for confirmation
RSI_OVERSOLD = 30  # Below this = oversold (support bounce candidate)
RSI_OVERBOUGHT = 70  # Above this = overbought (resistance rejection candidate)
RSI_PERIOD = 14  # Period for RSI calculation

# Volume confirmation
VOLUME_CONFIRMATION = True  # Require volume spike for alerts
MIN_VOLUME_RATIO = 1.2  # Volume must be 1.2x average
VOLUME_LOOKBACK = 20  # Days for average volume calculation

# Lookback for support/resistance levels
LOOKBACK_DAYS = 252  # 52 weeks

def send_telegram_message(message):
    """Sends alert to Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials not found. Printing to console instead.")
        print(message)
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit - truncate BEFORE any processing
    if len(message) > 4096:
        message = message[:4090] + "\n\n[...]"
    
    plain_message = message.replace('**', '').replace('_', '')
    
    payload = {"chat_id": CHAT_ID, "text": plain_message}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✓ Telegram alert sent successfully!")
    except Exception as e:
        print(f"✗ Telegram error: {e}")

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    deltas = prices.diff()
    gain = deltas.where(deltas > 0, 0).rolling(window=period).mean()
    loss = -deltas.where(deltas < 0, 0).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_support_resistance_test(ticker):
    """Detect if stock is testing support or resistance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{LOOKBACK_DAYS}d")
        
        if hist.empty or len(hist) < RSI_PERIOD + 1:
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate key levels
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Calculate moving averages as additional levels
        ma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else None
        ma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        
        # Calculate RSI
        rsi = calculate_rsi(hist['Close'], RSI_PERIOD).iloc[-1]
        
        # Volume analysis
        current_volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].tail(VOLUME_LOOKBACK).mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Check volume requirement
        if VOLUME_CONFIRMATION and volume_ratio < MIN_VOLUME_RATIO:
            return None
        
        # Determine if testing support or resistance
        distance_to_low = ((current_price - low_52w) / low_52w) * 100
        distance_to_high = ((high_52w - current_price) / current_price) * 100
        
        setups = []
        
        # Support bounce setup
        if distance_to_low <= SUPPORT_LEVEL_THRESHOLD:
            if rsi <= RSI_OVERSOLD:
                setup_type = "🎯 STRONG Support Bounce"
                quality = "HIGH"
            else:
                setup_type = "📌 Support Test"
                quality = "MEDIUM"
            
            setups.append({
                'type': setup_type,
                'level': low_52w,
                'level_name': '52W Low',
                'distance': distance_to_low,
                'rsi': rsi,
                'quality': quality,
                'direction': 'BULLISH 🟢'
            })
        
        # Resistance rejection setup
        if distance_to_high <= RESISTANCE_LEVEL_THRESHOLD:
            if rsi >= RSI_OVERBOUGHT:
                setup_type = "🎯 STRONG Resistance Rejection"
                quality = "HIGH"
            else:
                setup_type = "📌 Resistance Test"
                quality = "MEDIUM"
            
            setups.append({
                'type': setup_type,
                'level': high_52w,
                'level_name': '52W High',
                'distance': distance_to_high,
                'rsi': rsi,
                'quality': quality,
                'direction': 'BEARISH 🔴'
            })
        
        # Check MA levels (if available)
        if ma_50 and abs((current_price - ma_50) / ma_50 * 100) <= 1.0:
            setups.append({
                'type': "📊 50-MA Test",
                'level': ma_50,
                'level_name': '50-Day MA',
                'distance': abs((current_price - ma_50) / ma_50 * 100),
                'rsi': rsi,
                'quality': "MEDIUM",
                'direction': 'SUPPORT 🟡' if current_price > ma_50 else 'RESISTANCE 🟡'
            })
        
        if ma_200 and abs((current_price - ma_200) / ma_200 * 100) <= 1.5:
            setups.append({
                'type': "📊 200-MA Test",
                'level': ma_200,
                'level_name': '200-Day MA',
                'distance': abs((current_price - ma_200) / ma_200 * 100),
                'rsi': rsi,
                'quality': "HIGH",
                'direction': 'SUPPORT 🟡' if current_price > ma_200 else 'RESISTANCE 🟡'
            })
        
        if not setups:
            return None
        
        return {
            'ticker': ticker,
            'price': current_price,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'setups': setups
        }
        
    except Exception as e:
        print(f"Error detecting S/R for {ticker}: {e}")
        return None

def scan_support_resistance():
    """Scan watchlist for support/resistance tests"""
    print("=" * 60)
    print("📈 SUPPORT/RESISTANCE BOUNCE SCANNER")
    print("=" * 60)
    
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Scanning {len(WATCHLIST)} stocks for S/R tests...")
    print(f"Criteria: Within {SUPPORT_LEVEL_THRESHOLD}% of support or {RESISTANCE_LEVEL_THRESHOLD}% of resistance\n")
    
    results = []
    
    for i, ticker in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] Checking {ticker}...", end='\r')
        test_info = detect_support_resistance_test(ticker)
        if test_info:
            results.append(test_info)
    
    print("\n" + "=" * 60 + "\n")
    
    # Separate by quality
    high_quality = [r for r in results if any(s['quality'] == 'HIGH' for s in r['setups'])]
    medium_quality = [r for r in results if r not in high_quality]
    
    if results:
        header = f"📈 SUPPORT/RESISTANCE ALERTS - {timestamp}\n"
        header += f"Found {len(results)} setup(s): {len(high_quality)} HIGH quality, {len(medium_quality)} MEDIUM\n"
        header += "=" * 50 + "\n\n"
        
        sections = []
        
        # High quality setups
        if high_quality:
            hq_section = "🎯 HIGH QUALITY SETUPS:\n"
            for r in high_quality:
                hq_section += f"\n  {r['ticker']} - ${r['price']:.2f}\n"
                hq_section += f"    • RSI: {r['rsi']:.1f} | Volume: {r['volume_ratio']:.1f}x\n"
                for setup in r['setups']:
                    if setup['quality'] == 'HIGH':
                        hq_section += (
                            f"    • {setup['type']} {setup['direction']}\n"
                            f"      Level: ${setup['level']:.2f} ({setup['level_name']}) - {setup['distance']:.2f}% away\n"
                        )
            sections.append(hq_section)
        
        # Medium quality setups
        if medium_quality:
            mq_section = "\n📌 MEDIUM QUALITY SETUPS:\n"
            for r in medium_quality:
                mq_section += f"\n  {r['ticker']} - ${r['price']:.2f}\n"
                mq_section += f"    • RSI: {r['rsi']:.1f} | Volume: {r['volume_ratio']:.1f}x\n"
                for setup in r['setups']:
                    mq_section += (
                        f"    • {setup['type']} {setup['direction']}\n"
                        f"      Level: ${setup['level']:.2f} ({setup['level_name']}) - {setup['distance']:.2f}% away\n"
                    )
            sections.append(mq_section)
        
        footer = (
            f"\n{'=' * 50}\n"
            f"⚙️ Criteria: {SUPPORT_LEVEL_THRESHOLD}% support, {RESISTANCE_LEVEL_THRESHOLD}% resistance\n"
            f"📊 RSI: <{RSI_OVERSOLD} oversold, >{RSI_OVERBOUGHT} overbought\n"
            f"💡 Wait for candle confirmation before entry\n"
            f"🛡️ Use stops just beyond key levels\n"
        )
        
        final_message = header + "\n".join(sections) + footer
        
        print(final_message)
        send_telegram_message(final_message)
        
    else:
        no_setups_msg = (
            f"📈 S/R Scanner - {timestamp}\n"
            f"No support/resistance tests detected.\n\n"
            f"Scanned {len(WATCHLIST)} stocks.\n"
        )
        print(no_setups_msg)

if __name__ == "__main__":
    scan_support_resistance()
