"""
🌅 GAP SCANNER (PRE-MARKET & AFTER-HOURS)
=========================================

WHAT IT DOES:
-------------
Identifies stocks with significant price gaps from previous close, typically caused by:
  • Earnings announcements
  • Major news events
  • Analyst upgrades/downgrades
  • Sector-wide moves
  • M&A activity

Gaps are powerful signals for day traders and swing traders, often leading to
continuation or reversal patterns that offer high-probability setups.

FEATURES:
---------
✅ Detects gap ups and gap downs
✅ Calculates gap percentage and volume
✅ Identifies gap types (breakaway, continuation, exhaustion)
✅ Shows pre-market/after-hours price action
✅ Volume confirmation for gap validity
✅ Telegram alerts before market open
✅ Tracks gap fill potential

KEY SETTINGS (Customize below):
-------------------------------
MIN_GAP_PERCENTAGE: Minimum gap size to report
  - 3.0% = Significant gaps (default)
  - 2.0% = Moderate gaps (more signals)
  - 5.0% = Large gaps only (high conviction)

MIN_VOLUME_RATIO: Volume confirmation requirement
  - 1.5x = Moderate volume (default)
  - 2.0x = Strong volume confirmation
  - 1.0x = No volume filter (all gaps)

GAP_TYPES: Filter by gap direction
  - 'both' = Up and down gaps (default)
  - 'up' = Only gap ups
  - 'down' = Only gap downs

SCAN_TIME: When to run the scanner
  - 'premarket' = Before 9:30 AM ET (default)
  - 'afterhours' = After 4:00 PM ET
  - 'both' = Both sessions

GAP TYPES EXPLAINED:
--------------------
1. BREAKAWAY GAP:
   • Breaks above resistance or below support
   • Often doesn't fill
   • Strong volume
   • Trade: Follow the direction

2. CONTINUATION GAP (Runaway):
   • Mid-trend gap
   • Shows strong momentum
   • Partial fill possible
   • Trade: Pullback entry in trend direction

3. EXHAUSTION GAP:
   • Near end of trend
   • Often fills quickly
   • Climactic volume
   • Trade: Fade the gap (counter-trend)

4. COMMON GAP:
   • No major news
   • Usually fills same day
   • Low volume
   • Trade: Gap fill play

TRADING STRATEGIES:
------------------
GAP UP (Bullish):
  • Gap & Go: Buy if holds above gap, strong volume
  • Gap Fill: Short if weak volume, sell into pop
  • Breakout: Buy on consolidation above gap level

GAP DOWN (Bearish):
  • Gap & Crap: Short if breaks below gap level
  • Gap Fill: Buy if strong support, reversal signs
  • Breakdown: Short continuation after bounce fails

USAGE TIPS:
-----------
• Run at 8:00 AM ET to catch pre-market gaps
• Check news catalyst for gap direction validity
• Large gaps (>5%) often have follow-through
• Gaps on low volume tend to fill
• Wait for first 30 min to confirm direction
• Use previous day's high/low as key levels
• Combine with support/resistance scanner
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
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
# 🎯 GAP SCANNER SETTINGS - CUSTOMIZE HERE!
# ==========================================

# Minimum gap percentage to report
# 3.0% = significant | 2.0% = moderate | 5.0% = large only
MIN_GAP_PERCENTAGE = 3.0

# Minimum volume ratio vs average (for confirmation)
# 1.5x = moderate | 2.0x = strong | 1.0x = no filter
MIN_VOLUME_RATIO = 1.5

# Which gaps to scan for
# 'both' = up and down | 'up' = bullish only | 'down' = bearish only
GAP_TYPES = 'both'

# Number of days of volume history for average
VOLUME_LOOKBACK = 20

def send_telegram_message(message):
    """Sends alert to Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not found. Printing to console instead.")
        print(message)
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    plain_message = message.replace('**', '').replace('_', '')
    
    if len(plain_message) > 4096:
        plain_message = plain_message[:4090] + "\n\n[...]"
    
    payload = {"chat_id": CHAT_ID, "text": plain_message}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✓ Telegram alert sent successfully!")
    except Exception as e:
        print(f"✗ Telegram error: {e}")

def detect_gap(ticker):
    """Detect if stock has gapped and calculate gap details"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get recent data including pre-market
        hist = stock.history(period='5d', interval='1d', prepost=True)
        
        if hist.empty or len(hist) < 2:
            return None
        
        # Previous close
        prev_close = hist['Close'].iloc[-2]
        
        # Current price (could be pre-market or regular hours)
        current_price = hist['Close'].iloc[-1]
        
        # Calculate gap
        gap_pct = ((current_price - prev_close) / prev_close) * 100
        gap_dollars = current_price - prev_close
        
        # Check if meets minimum threshold
        if abs(gap_pct) < MIN_GAP_PERCENTAGE:
            return None
        
        # Check direction filter
        if GAP_TYPES == 'up' and gap_pct < 0:
            return None
        if GAP_TYPES == 'down' and gap_pct > 0:
            return None
        
        # Get volume data
        current_volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].iloc[:-1].tail(VOLUME_LOOKBACK).mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Check volume requirement
        if volume_ratio < MIN_VOLUME_RATIO:
            return None
        
        # Get previous day high/low for reference levels
        prev_high = hist['High'].iloc[-2]
        prev_low = hist['Low'].iloc[-2]
        
        # Determine gap type (simplified)
        if abs(gap_pct) >= 5.0 and volume_ratio >= 2.0:
            gap_type = "🚀 Breakaway" if gap_pct > 0 else "💥 Breakdown"
        elif volume_ratio >= 3.0:
            gap_type = "⚡ Exhaustion"
        elif 3.0 <= abs(gap_pct) < 5.0:
            gap_type = "📈 Continuation" if gap_pct > 0 else "📉 Continuation"
        else:
            gap_type = "📊 Common"
        
        return {
            'ticker': ticker,
            'prev_close': prev_close,
            'current_price': current_price,
            'gap_pct': gap_pct,
            'gap_dollars': gap_dollars,
            'volume_ratio': volume_ratio,
            'prev_high': prev_high,
            'prev_low': prev_low,
            'gap_type': gap_type,
            'direction': '🟢 UP' if gap_pct > 0 else '🔴 DOWN'
        }
        
    except Exception as e:
        print(f"Error detecting gap for {ticker}: {e}")
        return None

def scan_gaps():
    """Scan watchlist for gaps"""
    print("=" * 60)
    print("🌅 GAP SCANNER (PRE-MARKET & AFTER-HOURS)")
    print("=" * 60)
    
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Scanning {len(WATCHLIST)} stocks for gaps >{MIN_GAP_PERCENTAGE}%...")
    print(f"Volume filter: >{MIN_VOLUME_RATIO}x average\n")
    
    gaps = []
    
    for i, ticker in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] Checking {ticker}...", end='\r')
        gap_info = detect_gap(ticker)
        if gap_info:
            gaps.append(gap_info)
    
    print("\n" + "=" * 60 + "\n")
    
    # Sort by gap size (absolute)
    gaps.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
    
    # Separate gap ups and downs
    gap_ups = [g for g in gaps if g['gap_pct'] > 0]
    gap_downs = [g for g in gaps if g['gap_pct'] < 0]
    
    if gaps:
        header = f"🚨 GAP ALERT - {timestamp}\n"
        header += f"Found {len(gaps)} gap(s): {len(gap_ups)} UP, {len(gap_downs)} DOWN\n"
        header += "=" * 50 + "\n\n"
        
        sections = []
        
        # Gap Ups
        if gap_ups:
            gap_up_section = "🟢 GAP UPS:\n"
            for g in gap_ups:
                gap_up_section += (
                    f"\n  {g['gap_type']} {g['ticker']} {g['direction']}\n"
                    f"    • Gap: {g['gap_pct']:+.2f}% (${g['gap_dollars']:+.2f})\n"
                    f"    • Price: ${g['current_price']:.2f} (from ${g['prev_close']:.2f})\n"
                    f"    • Volume: {g['volume_ratio']:.1f}x average\n"
                    f"    • Prev High: ${g['prev_high']:.2f} (key resistance)\n"
                    f"    • Strategy: {'Gap & Go if holds' if g['volume_ratio'] >= 2.0 else 'Watch for gap fill'}\n"
                )
            sections.append(gap_up_section)
        
        # Gap Downs
        if gap_downs:
            gap_down_section = "🔴 GAP DOWNS:\n"
            for g in gap_downs:
                gap_down_section += (
                    f"\n  {g['gap_type']} {g['ticker']} {g['direction']}\n"
                    f"    • Gap: {g['gap_pct']:+.2f}% (${g['gap_dollars']:+.2f})\n"
                    f"    • Price: ${g['current_price']:.2f} (from ${g['prev_close']:.2f})\n"
                    f"    • Volume: {g['volume_ratio']:.1f}x average\n"
                    f"    • Prev Low: ${g['prev_low']:.2f} (key support)\n"
                    f"    • Strategy: {'Gap & Crap if breaks' if g['volume_ratio'] >= 2.0 else 'Potential gap fill'}\n"
                )
            sections.append(gap_down_section)
        
        footer = (
            f"\n{'=' * 50}\n"
            f"⚙️ Criteria: >{MIN_GAP_PERCENTAGE}% gap, >{MIN_VOLUME_RATIO}x volume\n"
            f"💡 Large gaps often continue | Low volume gaps usually fill\n"
            f"⏰ Wait for first 30 min to confirm direction\n"
        )
        
        final_message = header + "\n".join(sections) + footer
        
        print(final_message)
        send_telegram_message(final_message)
        
    else:
        no_gaps_msg = (
            f"🌅 Gap Scanner - {timestamp}\n"
            f"No significant gaps detected.\n\n"
            f"Scanned {len(WATCHLIST)} stocks with criteria:\n"
            f"  • Gap >{MIN_GAP_PERCENTAGE}%\n"
            f"  • Volume >{MIN_VOLUME_RATIO}x average\n"
        )
        print(no_gaps_msg)

if __name__ == "__main__":
    scan_gaps()
