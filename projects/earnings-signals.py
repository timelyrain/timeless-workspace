"""
📅 EARNINGS CALENDAR + PRE-EARNINGS IV CRUSH SCANNER
=====================================================

WHAT IT DOES:
-------------
Tracks upcoming earnings for your watchlist and identifies high IV (Implied Volatility)
opportunities before earnings announcements. Helps you:
  1. Know when your stocks are reporting earnings
  2. Calculate expected move based on options pricing
  3. Identify IV crush opportunities (selling options before earnings)
  4. Spot high-risk/high-reward setups

IV Crush is when implied volatility drops dramatically after earnings, causing
options to lose value even if the stock moves. This scanner helps you profit from
or avoid this phenomenon.

FEATURES:
---------
✅ Earnings Calendar - Shows upcoming earnings dates for watchlist
✅ IV Rank Calculation - How high is current IV vs historical
✅ Expected Move - What the options market is pricing in
✅ Days to Earnings - Time remaining before announcement
✅ IV Crush Opportunities - Flag high IV stocks before earnings
✅ Strategy Suggestions - Trade ideas based on IV levels
✅ Telegram Alerts - Get notified days before earnings

KEY SETTINGS (Customize below):
-------------------------------
DAYS_AHEAD: How far ahead to look for earnings
  - 7 days = This week (default)
  - 14 days = Next two weeks
  - 30 days = Full month ahead

MIN_IV_RANK: Minimum IV rank to flag as opportunity
  - 70 = High IV only (default)
  - 80 = Very high IV (stricter)
  - 50 = Medium-high IV (more opportunities)

MIN_EXPECTED_MOVE: Minimum expected move percentage
  - 5.0% = Significant moves only (default)
  - 3.0% = More moderate movers
  - 8.0% = Only highly volatile stocks

ALERT_DAYS_BEFORE: Days before earnings to send reminder
  - [3, 1] = Alert 3 days and 1 day before (default)
  - [7, 3, 1] = More advance warnings
  - [1] = Day before only

TRADING STRATEGIES:
------------------
HIGH IV BEFORE EARNINGS:
  • SELL options (credit spreads, iron condors, naked puts/calls)
  • Collect premium before IV crush
  • Risk: Large unexpected moves

LOW IV BEFORE EARNINGS:
  • BUY options (straddles, strangles)
  • Bet on larger move than market expects
  • Risk: IV crush if move is small

EXPECTED MOVE:
  • Stock priced to move ±X%
  • Use to set strikes for spreads
  • Good for probability analysis

USAGE TIPS:
-----------
• Run daily during market hours leading up to earnings season
• Combine with breakout scanner to find momentum into earnings
• Sell premium 2-3 days before earnings (peak IV)
• Close positions right before earnings or hold through for directional bet
• Watch for earnings surprises in similar sector stocks
• Check analyst estimates and guidance before trading
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import pytz
import os
import pandas as pd
import numpy as np
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
# 🎯 EARNINGS SCANNER SETTINGS - CUSTOMIZE HERE!
# ==========================================

# How many days ahead to look for earnings
# 7 = this week | 14 = two weeks | 30 = full month
DAYS_AHEAD = 7

# Minimum IV Rank to flag as high IV opportunity (0-100)
# 70 = high IV | 80 = very high | 50 = moderate
MIN_IV_RANK = 70

# Minimum expected move percentage to report
# 5.0% = significant | 3.0% = moderate | 8.0% = very volatile
MIN_EXPECTED_MOVE = 5.0

# Days before earnings to send alerts (list)
# [3, 1] = 3 days before and 1 day before
ALERT_DAYS_BEFORE = [3, 1]

def send_telegram_message(message):
    """Sends alert to Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
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

def calculate_iv_rank(current_iv, iv_history):
    """
    Calculate IV Rank: where current IV sits in the range of historical IV
    IV Rank = (Current IV - Min IV) / (Max IV - Min IV) * 100
    Returns 0-100 where 100 = highest IV in the period
    """
    if len(iv_history) < 2:
        return None
    
    min_iv = iv_history.min()
    max_iv = iv_history.max()
    
    if max_iv == min_iv:
        return 50.0  # Neutral if no variance
    
    iv_rank = ((current_iv - min_iv) / (max_iv - min_iv)) * 100
    return iv_rank

def get_earnings_data(ticker):
    """
    Fetches earnings date and options data for IV analysis
    Returns dict with earnings info or None
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get earnings date
        calendar = stock.calendar
        if calendar is None or calendar.empty:
            return None
        
        # Extract earnings date (different formats possible)
        earnings_date = None
        if 'Earnings Date' in calendar.index:
            earnings_date = calendar.loc['Earnings Date']
            if isinstance(earnings_date, pd.Series):
                earnings_date = earnings_date.iloc[0]
        
        if earnings_date is None or pd.isna(earnings_date):
            return None
        
        # Convert to datetime if string
        if isinstance(earnings_date, str):
            earnings_date = pd.to_datetime(earnings_date)
        
        # Calculate days until earnings
        today = datetime.now().date()
        if hasattr(earnings_date, 'date'):
            earnings_date = earnings_date.date()
        
        days_until = (earnings_date - today).days
        
        # Only report if within our lookback period
        if days_until < 0 or days_until > DAYS_AHEAD:
            return None
        
        # Get current price and historical data for IV calculation
        hist = stock.history(period="3mo")  # 3 months for IV rank
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Get options data for IV and expected move calculation
        try:
            expirations = stock.options
            if not expirations or len(expirations) == 0:
                return None
            
            # Find expiration closest to earnings date
            exp_dates = [pd.to_datetime(exp).date() for exp in expirations]
            earnings_exp = min([exp for exp in exp_dates if exp >= earnings_date], 
                             default=exp_dates[0] if exp_dates else None)
            
            if earnings_exp is None:
                return None
            
            # Get options chain for that expiration
            exp_str = earnings_exp.strftime('%Y-%m-%d')
            if exp_str not in expirations:
                exp_str = expirations[0]
            
            opt_chain = stock.option_chain(exp_str)
            calls = opt_chain.calls
            puts = opt_chain.puts
            
            if calls.empty or puts.empty:
                return None
            
            # Find ATM options for IV
            atm_strike = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]['strike'].values[0]
            
            atm_call = calls[calls['strike'] == atm_strike]
            atm_put = puts[puts['strike'] == atm_strike]
            
            if atm_call.empty or atm_put.empty:
                return None
            
            # Get IV from ATM options
            call_iv = atm_call['impliedVolatility'].values[0] * 100 if 'impliedVolatility' in atm_call.columns else None
            put_iv = atm_put['impliedVolatility'].values[0] * 100 if 'impliedVolatility' in atm_put.columns else None
            
            if call_iv is None or put_iv is None or call_iv == 0 or put_iv == 0:
                return None
            
            current_iv = (call_iv + put_iv) / 2
            
            # Calculate IV rank using historical volatility as proxy
            # (True IV history requires historical options data which is complex)
            # Using realized volatility (std of returns) as approximation
            returns = hist['Close'].pct_change().dropna()
            hist_vol = returns.rolling(20).std() * np.sqrt(252) * 100  # Annualized
            iv_rank = calculate_iv_rank(current_iv, hist_vol)
            
            # Calculate expected move
            # Expected Move = Stock Price * IV * sqrt(Days to Expiration / 365)
            days_to_exp = (earnings_exp - today).days
            expected_move_pct = current_iv * np.sqrt(days_to_exp / 365.0)
            expected_move_dollars = current_price * (expected_move_pct / 100)
            
            # Determine if this is a high IV opportunity
            is_opportunity = (iv_rank and iv_rank >= MIN_IV_RANK) and (expected_move_pct >= MIN_EXPECTED_MOVE)
            
            # Check if we should alert (within alert window)
            should_alert = days_until in ALERT_DAYS_BEFORE
            
            return {
                'ticker': ticker,
                'price': current_price,
                'earnings_date': earnings_date,
                'days_until': days_until,
                'current_iv': current_iv,
                'iv_rank': iv_rank,
                'expected_move_pct': expected_move_pct,
                'expected_move_dollars': expected_move_dollars,
                'atm_strike': atm_strike,
                'is_opportunity': is_opportunity,
                'should_alert': should_alert
            }
            
        except Exception as e:
            print(f"Error getting options data for {ticker}: {e}")
            return None
        
    except Exception as e:
        print(f"Error fetching earnings for {ticker}: {e}")
        return None

def scan_earnings():
    """
    Scans watchlist for upcoming earnings and IV opportunities
    """
    print("=" * 60)
    print("📅 EARNINGS CALENDAR + IV CRUSH SCANNER")
    print("=" * 60)
    
    # Get NY timezone for timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan Time: {timestamp}\n")
    
    print(f"Scanning {len(WATCHLIST)} stocks for earnings in next {DAYS_AHEAD} days...")
    print(f"IV Criteria: Rank >{MIN_IV_RANK}, Expected Move >{MIN_EXPECTED_MOVE}%\n")
    
    upcoming_earnings = []
    iv_opportunities = []
    
    for i, ticker in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] Checking {ticker}...", end='\r')
        earnings_info = get_earnings_data(ticker)
        if earnings_info:
            upcoming_earnings.append(earnings_info)
            if earnings_info['is_opportunity']:
                iv_opportunities.append(earnings_info)
    
    print("\n" + "=" * 60 + "\n")
    
    # Sort by days until earnings (soonest first)
    upcoming_earnings.sort(key=lambda x: x['days_until'])
    iv_opportunities.sort(key=lambda x: x['days_until'])
    
    # Build messages
    messages = []
    
    # 1. High IV Opportunities
    if iv_opportunities:
        header = f"🔥 HIGH IV EARNINGS OPPORTUNITIES - {timestamp}\n"
        header += f"Found {len(iv_opportunities)} high IV setup(s):\n"
        header += "=" * 50 + "\n\n"
        
        alerts = []
        for info in iv_opportunities:
            # Determine urgency
            if info['days_until'] <= 1:
                urgency = "⚠️ URGENT"
            elif info['days_until'] <= 3:
                urgency = "🔔 SOON"
            else:
                urgency = "📌 UPCOMING"
            
            # Strategy suggestion
            if info['iv_rank'] and info['iv_rank'] >= 80:
                strategy = "Strategy: SELL premium (credit spreads, iron condor)"
            elif info['iv_rank'] and info['iv_rank'] >= 70:
                strategy = "Strategy: Consider selling premium or neutral plays"
            else:
                strategy = "Strategy: Moderate IV, watch for further increase"
            
            alert = (
                f"{urgency} {info['ticker']} - ${info['price']:.2f}\n"
                f"  • Earnings: {info['earnings_date']} ({info['days_until']} days)\n"
                f"  • Current IV: {info['current_iv']:.1f}%\n"
                f"  • IV Rank: {info['iv_rank']:.0f}/100 {'🔥' if info['iv_rank'] >= 80 else '⚡'}\n"
                f"  • Expected Move: ±{info['expected_move_pct']:.2f}% (${info['expected_move_dollars']:.2f})\n"
                f"  • ATM Strike: ${info['atm_strike']:.2f}\n"
                f"  • {strategy}\n"
            )
            alerts.append(alert)
        
        footer = (
            f"\n{'=' * 50}\n"
            f"⚙️ Criteria: IV Rank >{MIN_IV_RANK}, Move >{MIN_EXPECTED_MOVE}%\n"
            f"💡 High IV = Sell premium | Low IV = Buy options\n"
        )
        
        messages.append(header + "\n".join(alerts) + footer)
    
    # 2. Full Earnings Calendar
    if upcoming_earnings:
        cal_header = f"\n📅 EARNINGS CALENDAR ({DAYS_AHEAD} Days) - {timestamp}\n"
        cal_header += f"{len(upcoming_earnings)} stock(s) reporting:\n"
        cal_header += "=" * 50 + "\n\n"
        
        cal_items = []
        for info in upcoming_earnings:
            cal_item = (
                f"📊 {info['ticker']} - {info['earnings_date']} "
                f"({info['days_until']}d) - Expected: ±{info['expected_move_pct']:.1f}%"
            )
            cal_items.append(cal_item)
        
        messages.append(cal_header + "\n".join(cal_items))
    
    # Send messages
    if messages:
        final_message = "\n\n".join(messages)
        print(final_message)
        send_telegram_message(final_message)
    else:
        no_earnings_msg = (
            f"📅 Earnings Scanner - {timestamp}\n"
            f"No earnings in the next {DAYS_AHEAD} days.\n\n"
            f"Scanned {len(WATCHLIST)} stocks.\n"
        )
        print(no_earnings_msg)
        # Optional: comment out if you don't want "no earnings" messages
        # send_telegram_message(no_earnings_msg)

if __name__ == "__main__":
    scan_earnings()
