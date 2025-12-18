"""
🔄 SECTOR ROTATION TRACKER
==========================

WHAT IT DOES:
-------------
Monitors the performance of major market sectors to identify capital rotation patterns.
Helps you understand which sectors are gaining or losing institutional favor, allowing
you to position your portfolio in leading sectors and avoid lagging ones.

Sector rotation is a key indicator of market cycles:
  • Early Bull: Financials, Technology lead
  • Mid Bull: Industrials, Materials gain
  • Late Bull: Energy, Consumer Discretionary peak
  • Defensive: Healthcare, Utilities, Consumer Staples outperform

FEATURES:
---------
✅ Tracks 11 major S&P sectors via sector ETFs
✅ Ranks sectors by performance (1D, 1W, 1M, 3M)
✅ Identifies rotation trends (leaders becoming laggards)
✅ Compares to SPY benchmark
✅ Shows relative strength momentum
✅ Telegram alerts on major shifts
✅ Helps identify macro trends

KEY SETTINGS (Customize below):
-------------------------------
TIMEFRAMES: Which periods to analyze
  - ['1d', '5d', '1mo', '3mo'] = Complete picture (default)
  - ['1d', '5d'] = Short-term focus
  - ['1mo', '3mo'] = Long-term trends

MIN_ROTATION_THRESHOLD: Performance spread to flag rotation
  - 3.0% = Significant divergence (default)
  - 5.0% = Major rotation only
  - 2.0% = More sensitive to shifts

TOP_N_SECTORS: How many top/bottom sectors to highlight
  - 3 = Top 3 and Bottom 3 (default)
  - 5 = Top 5 and Bottom 5
  - 2 = Most extreme only

SECTOR ETFS TRACKED:
--------------------
XLK - Technology
XLF - Financials
XLV - Healthcare
XLE - Energy
XLY - Consumer Discretionary
XLP - Consumer Staples
XLI - Industrials
XLB - Materials
XLRE - Real Estate
XLU - Utilities
XLC - Communication Services

TRADING APPLICATIONS:
---------------------
1. SECTOR ROTATION STRATEGY:
   • Buy strongest sectors
   • Sell/Avoid weakest sectors
   • Rotate capital into leaders

2. MARKET CYCLE IDENTIFICATION:
   • Risk-On: Tech, Discretionary, Financials lead
   • Risk-Off: Utilities, Staples, Healthcare lead
   • Recovery: Industrials, Materials gain

3. DIVERSIFICATION:
   • Spread across multiple strong sectors
   • Avoid concentration in weak sectors

4. TIMING:
   • Enter when sector shows momentum
   • Exit when sector rotation signals weakness

USAGE TIPS:
-----------
• Run daily to track rotation trends
• Compare 1D vs 1M to spot reversals
• Strong 3M + Strong 1M = Sustained leadership
• Weak 3M but Strong 1W = Potential reversal
• Combine with individual stock scanners for best picks within strong sectors
• Watch for defensive sector strength as recession indicator
"""

import yfinance as yf
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
import pandas as pd

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Telegram Credentials
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==========================================
# 🎯 SECTOR ROTATION SETTINGS - CUSTOMIZE HERE!
# ==========================================

# Sector ETFs to track
SECTORS = {
    'XLK': 'Technology',
    'XLF': 'Financials',
    'XLV': 'Healthcare',
    'XLE': 'Energy',
    'XLY': 'Consumer Discretionary',
    'XLP': 'Consumer Staples',
    'XLI': 'Industrials',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLU': 'Utilities',
    'XLC': 'Communication Services'
}

BENCHMARK = 'SPY'

# Timeframes to analyze (yfinance format: 1d, 5d, 1mo, 3mo, 6mo, 1y)
TIMEFRAMES = {
    '1d': '1 Day',
    '5d': '1 Week',
    '1mo': '1 Month',
    '3mo': '3 Months'
}

# Minimum spread between top and bottom to flag major rotation
MIN_ROTATION_THRESHOLD = 3.0  # percentage points

# Number of top/bottom sectors to highlight
TOP_N_SECTORS = 3

def send_telegram_message(message):
    """Sends alert to Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
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

def calculate_performance(ticker, period):
    """Calculate percentage performance over a period"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty or len(hist) < 2:
            return None
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        performance = ((end_price - start_price) / start_price) * 100
        
        return performance
    except Exception as e:
        print(f"Error calculating performance for {ticker}: {e}")
        return None

def scan_sector_rotation():
    """Scans sector ETFs and ranks by performance"""
    print("=" * 60)
    print("🔄 SECTOR ROTATION TRACKER")
    print("=" * 60)
    
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Analyzing {len(SECTORS)} sectors across {len(TIMEFRAMES)} timeframes...")
    print("Fetching data...\n")
    
    # Collect performance data
    results = {}
    
    for period_key, period_name in TIMEFRAMES.items():
        print(f"  Calculating {period_name} performance...", end='\r')
        
        sector_perf = {}
        
        # Get benchmark performance
        spy_perf = calculate_performance(BENCHMARK, period_key)
        
        # Get sector performances
        for ticker, name in SECTORS.items():
            perf = calculate_performance(ticker, period_key)
            if perf is not None:
                sector_perf[ticker] = {
                    'name': name,
                    'performance': perf,
                    'vs_spy': perf - spy_perf if spy_perf else None
                }
        
        results[period_key] = {
            'period_name': period_name,
            'spy_performance': spy_perf,
            'sectors': sector_perf
        }
    
    print("\n" + "=" * 60 + "\n")
    
    # Build report
    messages = []
    
    for period_key, data in results.items():
        period_name = data['period_name']
        spy_perf = data['spy_performance']
        sectors = data['sectors']
        
        if not sectors:
            continue
        
        # Sort sectors by performance
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['performance'], reverse=True)
        
        # Get top and bottom performers
        top_sectors = sorted_sectors[:TOP_N_SECTORS]
        bottom_sectors = sorted_sectors[-TOP_N_SECTORS:]
        
        # Calculate rotation magnitude
        if len(sorted_sectors) >= 2:
            spread = sorted_sectors[0][1]['performance'] - sorted_sectors[-1][1]['performance']
            is_major_rotation = spread >= MIN_ROTATION_THRESHOLD
        else:
            spread = 0
            is_major_rotation = False
        
        # Build message for this timeframe
        header = f"\n{'🔥' if is_major_rotation else '📊'} {period_name.upper()} ROTATION\n"
        header += "=" * 40 + "\n"
        header += f"SPY: {spy_perf:+.2f}% | Spread: {spread:.2f}%\n\n"
        
        # Top performers
        top_section = "🚀 LEADERS:\n"
        for ticker, info in top_sectors:
            vs_spy = info['vs_spy']
            vs_spy_str = f"(SPY {vs_spy:+.2f}%)" if vs_spy else ""
            top_section += f"  {ticker} {info['name']}: {info['performance']:+.2f}% {vs_spy_str}\n"
        
        # Bottom performers
        bottom_section = "\n🔻 LAGGARDS:\n"
        for ticker, info in bottom_sectors:
            vs_spy = info['vs_spy']
            vs_spy_str = f"(SPY {vs_spy:+.2f}%)" if vs_spy else ""
            bottom_section += f"  {ticker} {info['name']}: {info['performance']:+.2f}% {vs_spy_str}\n"
        
        messages.append(header + top_section + bottom_section)
    
    # Build final message
    if messages:
        title = f"🔄 SECTOR ROTATION REPORT - {timestamp}\n"
        title += "=" * 50 + "\n"
        
        final_message = title + "\n".join(messages)
        
        # Add trading insights
        insights = (
            f"\n{'=' * 50}\n"
            f"💡 INSIGHTS:\n"
            f"  • Favor stocks in leading sectors\n"
            f"  • Avoid lagging sectors unless contrarian\n"
            f"  • Watch for sector reversals (1D vs 1M divergence)\n"
            f"  • Defensive strength = Risk-off market\n"
            f"  • Tech/Discretionary strength = Risk-on market\n"
        )
        
        final_message += insights
        
        print(final_message)
        send_telegram_message(final_message)
    else:
        print("No sector data available.")

if __name__ == "__main__":
    scan_sector_rotation()
