"""
🚀 BREAKOUT SCANNER
====================

WHAT IT DOES:
-------------
Scans your watchlist for stocks breaking out to new highs with strong momentum.
Identifies potential explosive moves before they happen by combining three key signals:
  1. Price Action: Stock approaching or at 52-week high
  2. Volume Confirmation: Above-average buying pressure
  3. Relative Strength: Outperforming the market (SPY)

FEATURES:
---------
✅ 52-Week High Detection - Catches stocks at peak performance
✅ Volume Confirmation - Ensures institutional interest
✅ Relative Strength Filter - Only shows market leaders
✅ Telegram Alerts - Real-time notifications with full context
✅ Ranked Results - Strongest setups shown first
✅ Customizable Thresholds - Tune to your trading style

KEY SETTINGS (Customize below):
-------------------------------
LOOKBACK_DAYS: How far back to check for highs
  - 252 days = 52-week high (default)
  - 126 days = 6-month high (more frequent signals)
  - 63 days = quarterly high (very active)

BREAKOUT_THRESHOLD: How close to the high (%)
  - 0.5% = Very strict, only stocks AT highs
  - 1.0% = Moderate, within striking distance
  - 2.0% = Relaxed, early warning system

VOLUME_MULTIPLIER: Volume confirmation level
  - 1.5x = Moderate activity (default)
  - 2.0x = Strong conviction, fewer signals
  - 1.2x = More sensitive, more alerts

MIN_RS_VS_SPY: Relative strength requirement (%)
  - 5.0% = Strong outperformance (default)
  - 10.0% = Elite leaders only
  - 2.0% = More inclusive, catches early movers

RELATIVE STRENGTH FILTER USAGE:
--------------------------------
The RS filter is OPTIONAL. Change MIN_RS_VS_SPY to control filtering:

1. DISABLED (All Breakouts):
   MIN_RS_VS_SPY = None
   → Gets ALL breakouts regardless of how they compare to SPY
   → Use in choppy/weak markets to catch all opportunities
   → More alerts, lower quality

2. NO UNDERPERFORMERS:
   MIN_RS_VS_SPY = 0.0
   → Only stocks not losing to SPY
   → Filters out weak stocks but keeps everything else
   → Balanced approach

3. STRONG LEADERS (Default):
   MIN_RS_VS_SPY = 5.0
   → Only stocks beating SPY by 5%+
   → High quality signals, market leaders only
   → Use in bull markets to find the best

4. ELITE ONLY:
   MIN_RS_VS_SPY = 10.0
   → Top performers beating SPY by 10%+
   → Very strict, fewest alerts, highest conviction
   → Use when you only want the absolute strongest

USAGE TIPS:
-----------
• Morning Scan: Run at market open to catch overnight momentum
• End of Day: Run at 3:30 PM ET to catch closing breakouts
• Combine with divergence scanner for complete picture
• Adjust thresholds based on market volatility
• Start with MIN_RS_VS_SPY = None to see all breakouts, then tighten
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
from watchlist_loader import load_watchlist

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- CONFIGURATION ---
# Watchlist - same as divergence scanner for consistency
WATCHLIST = load_watchlist()

BENCHMARK = 'SPY'

# Telegram Credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("")

# ==========================================
# 🎯 BREAKOUT SCANNER SETTINGS - CUSTOMIZE HERE!
# ==========================================

# Lookback period for high calculation
# 252 = 52-week high | 126 = 6-month | 63 = quarterly
LOOKBACK_DAYS = 252

# How close to the high (percentage)
# Lower = stricter (0.5% = must be very close)
# Higher = earlier signals (2.0% = catches runups)
BREAKOUT_THRESHOLD = 0.5

# Volume requirement (multiple of 20-day average)
# 1.5x = moderate activity | 2.0x = strong conviction | 1.2x = more sensitive
VOLUME_MULTIPLIER = 1.5

# Relative strength filter (OPTIONAL - set to None to disable)
# How to use:
#   MIN_RS_VS_SPY = None     -> DISABLED: Get ALL breakouts regardless of SPY
#   MIN_RS_VS_SPY = 0.0      -> Get breakouts only if not underperforming SPY
#   MIN_RS_VS_SPY = 5.0      -> Only stocks outperforming SPY by 5%+ (strong leaders)
#   MIN_RS_VS_SPY = 10.0     -> Elite leaders only (very strict)
#
# Examples:
#   - Bull market: Use 5.0 to find the strongest leaders
#   - Choppy market: Use None to catch all breakouts
#   - Weak market: Use 0.0 to avoid underperformers
MIN_RS_VS_SPY = None  # Change to None to disable the filter

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

def scan_breakouts():
    """
    Scans watchlist for breakout setups over the past 5 days:
    1. Near 52-week high (within threshold) at any point in last 5 days
    2. High volume (above average) on breakout day
    3. Strong relative strength vs SPY
    """
    print("=" * 60)
    print("🚀 BREAKOUT SCANNER (5-Day Lookback)")
    print("=" * 60)
    
    # Get NY timezone for timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Fetching {LOOKBACK_DAYS}-day data for {len(WATCHLIST)} stocks + {BENCHMARK}...")
    print("Checking for breakouts in the past 5 trading days...\n")
    
    # Download historical data
    tickers = WATCHLIST + [BENCHMARK]
    try:
        data = yf.download(tickers, period=f"{LOOKBACK_DAYS}d", progress=False, auto_adjust=True)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    if data.empty:
        print("No data retrieved. Market might be closed or network issue.")
        return
    
    print("Data fetched. Analyzing...\n")
    
    # Get SPY performance for relative strength calculation
    spy_close = data['Close'][BENCHMARK]
    spy_current = spy_close.iloc[-1]
    spy_start = spy_close.iloc[0]
    spy_performance = ((spy_current - spy_start) / spy_start) * 100
    
    breakouts = []
    
    for ticker in WATCHLIST:
        try:
            # Get price data
            close_prices = data['Close'][ticker]
            volume_data = data['Volume'][ticker]
            
            if close_prices.isna().all() or volume_data.isna().all():
                continue
            
            current_price = close_prices.iloc[-1]
            high_52week = close_prices.max()
            
            # Check the past 5 trading days for breakouts
            breakout_detected = False
            breakout_day = None
            breakout_price = None
            breakout_volume_ratio = 0
            
            for i in range(1, 6):  # Check last 5 days
                if len(close_prices) < i:
                    break
                
                day_price = close_prices.iloc[-i]
                day_volume = volume_data.iloc[-i]
                
                # Calculate how close to 52-week high on this day
                distance_from_high = ((high_52week - day_price) / high_52week) * 100
                
                # Check if this day was near the high
                if distance_from_high <= BREAKOUT_THRESHOLD:
                    # Check volume for that day (20-day average)
                    avg_volume_20d = volume_data.iloc[-(20+i):(-i if i > 1 else None)].mean()
                    volume_ratio = day_volume / avg_volume_20d if avg_volume_20d > 0 else 0
                    
                    if volume_ratio >= VOLUME_MULTIPLIER:
                        breakout_detected = True
                        breakout_day = i
                        breakout_price = day_price
                        breakout_volume_ratio = volume_ratio
                        break  # Found the most recent breakout
            
            if not breakout_detected:
                continue
            
            # Calculate relative strength vs SPY
            stock_start = close_prices.iloc[0]
            stock_performance = ((current_price - stock_start) / stock_start) * 100
            relative_strength = stock_performance - spy_performance
            
            # Apply RS filter only if enabled (not None)
            if MIN_RS_VS_SPY is not None and relative_strength < MIN_RS_VS_SPY:
                continue
            
            # Calculate distance from current price to high
            current_distance = ((high_52week - current_price) / high_52week) * 100
            
            # This is a valid breakout!
            breakouts.append({
                'ticker': ticker,
                'price': current_price,
                'high_52w': high_52week,
                'distance': current_distance,
                'breakout_day': breakout_day,
                'breakout_price': breakout_price,
                'volume_ratio': breakout_volume_ratio,
                'rs_vs_spy': relative_strength,
                'performance': stock_performance
            })
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    # Sort by relative strength (strongest first)
    breakouts.sort(key=lambda x: x['rs_vs_spy'], reverse=True)
    
    # Build alert message
    if breakouts:
        header = f"🚀 BREAKOUT ALERT (5-Day Scan) - {timestamp}\n"
        header += f"Found {len(breakouts)} strong setup(s):\n"
        header += "=" * 50 + "\n\n"
        
        alerts = []
        for b in breakouts:
            # Determine when the breakout happened
            if b['breakout_day'] == 1:
                day_text = "Today"
            elif b['breakout_day'] == 2:
                day_text = "Yesterday"
            else:
                day_text = f"{b['breakout_day']} days ago"
            
            alert = (
                f"📊 {b['ticker']} - ${b['price']:.2f}\n"
                f"  • Breakout: {day_text} at ${b['breakout_price']:.2f}\n"
                f"  • 52W High: ${b['high_52w']:.2f} (now {b['distance']:.2f}% away)\n"
                f"  • Volume on breakout: {b['volume_ratio']:.1f}x average\n"
                f"  • RS vs SPY: +{b['rs_vs_spy']:.1f}%\n"
                f"  • Overall Performance: +{b['performance']:.1f}%\n"
            )
            alerts.append(alert)
        
        # Build footer with criteria
        rs_text = f"+{MIN_RS_VS_SPY}% RS" if MIN_RS_VS_SPY is not None else "No RS filter"
        footer = (
            f"\n{'=' * 50}\n"
            f"📈 SPY Performance: {spy_performance:+.1f}%\n"
            f"⚙️ Criteria: <{BREAKOUT_THRESHOLD}% from 52W high, "
            f"{VOLUME_MULTIPLIER}x volume, {rs_text}\n"
            f"🔍 Scanned past 5 trading days\n"
        )
        
        final_message = header + "\n".join(alerts) + footer
        
        print(final_message)
        send_telegram_message(final_message)
        
    else:
        rs_text = f"Relative Strength >{MIN_RS_VS_SPY}% vs SPY" if MIN_RS_VS_SPY is not None else "No RS filter (all breakouts)"
        no_alerts_msg = (
            f"🔍 Breakout Scanner (5-Day) - {timestamp}\n"
            f"No breakouts detected in the past 5 trading days.\n\n"
            f"Scanned {len(WATCHLIST)} stocks with criteria:\n"
            f"  • Within {BREAKOUT_THRESHOLD}% of 52-week high\n"
            f"  • Volume >{VOLUME_MULTIPLIER}x average\n"
            f"  • {rs_text}\n"
            f"  • Checked past 5 trading days\n"
        )
        print(no_alerts_msg)
        # Optional: comment out next line if you don't want "no alerts" messages
        # send_telegram_message(no_alerts_msg)

if __name__ == "__main__":
    scan_breakouts()
