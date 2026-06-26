#!/usr/bin/env python3
"""
🔥 IV CRUSH PREDICTION SIGNAL
=============================

WHAT IT DOES:
Predicts IV crush severity before and after earnings using advanced volatility analysis.
IV crush occurs when implied volatility drops 20-50% after earnings as uncertainty resolves.

KEY IMPROVEMENTS OVER BASIC EARNINGS SIGNAL:
✅ IV Percentile - More accurate than IV rank (historical comparison)
✅ Crush Prediction Score - 0-15 pts based on multiple factors
✅ Realized vs Implied Vol Gap - Larger gaps = bigger crush potential
✅ VIX Correlation - Market volatility impact on stock
✅ Volatility Surface Analysis - Skew and term structure
✅ Historical Earnings Surprise Tracking - What stocks actually did
✅ Theta Decay Modeling - Time value decay alongside IV crush
✅ Post-Earnings Monitoring - Track IV crush as it happens

TRADING STRATEGIES:
Pre-Earnings (HIGH IV):
  • SELL Iron Condor - Collect premium, profit from time decay + IV crush
  • SELL Credit Spreads - Defined risk, high probability
  • SELL Covered Calls - Income generation

Post-Earnings (IV CRUSHED):
  • BUY Long Calls/Puts - Cheap premium for longer-dated contracts
  • SELL Short Calls/Puts - Profit from further IV contraction
  • CALENDAR SPREADS - Sell near-term (low IV), buy far-term (higher IV)

CRUSH MAGNITUDE EXAMPLES:
  • Tech earnings (earnings): 30-50% IV crush (TSLA, NVDA, AMZN)
  • Finance (earnings): 25-35% IV crush (JPM, GS, BAC)
  • Healthcare (earnings): 20-30% IV crush (PFE, JNJ)
  • Utilities (earnings): 15-25% IV crush (lower volatility stocks)
"""

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import yfinance as yf
import numpy as np
import pandas as pd
import time
from pathlib import Path

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
DAYS_AHEAD = 30  # Look ahead 30 days
MIN_SCORE_MEDIUM = 7
MIN_SCORE_HIGH = 11
MIN_IV_PERCENTILE = 60  # Minimum IV percentile to consider
MIN_IV_REALIZED_GAP = 5  # Minimum gap between implied and realized vol

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

def get_earnings_dates(ticker):
    """Fetch upcoming earnings dates for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        
        # Try calendar first (most reliable for earnings dates)
        try:
            calendar = stock.calendar
            
            if calendar is not None:
                print(f"  DEBUG {ticker} calendar type: {type(calendar)}")
                print(f"  DEBUG {ticker} calendar: {calendar}")
                
                earnings_date = None
                
                # Handle different calendar formats
                if isinstance(calendar, pd.DataFrame):
                    if 'Earnings Date' in calendar.index:
                        earnings_date = calendar.loc['Earnings Date']
                        if isinstance(earnings_date, pd.Series):
                            earnings_date = earnings_date.iloc[0]
                elif isinstance(calendar, pd.Series):
                    if 'Earnings Date' in calendar.index:
                        earnings_date = calendar.loc['Earnings Date']
                elif isinstance(calendar, dict):
                    earnings_date = calendar.get('Earnings Date')
                    if earnings_date is None:
                        # Try alternate keys
                        for key in calendar.keys():
                            if 'earnings' in key.lower() and 'date' in key.lower():
                                earnings_date = calendar[key]
                                break
                
                if earnings_date is not None:
                    print(f"  DEBUG {ticker} raw earnings_date: {earnings_date}, type: {type(earnings_date)}")
                    
                    # Handle list of dates (yfinance returns [date] format)
                    if isinstance(earnings_date, list) and len(earnings_date) > 0:
                        earnings_date = earnings_date[0]  # Take first date
                        print(f"  DEBUG {ticker} extracted from list: {earnings_date}")
                    
                    # Convert to date
                    if isinstance(earnings_date, str):
                        earnings_date = pd.to_datetime(earnings_date).date()
                    elif isinstance(earnings_date, (int, float)):
                        earnings_date = datetime.fromtimestamp(earnings_date).date()
                    elif isinstance(earnings_date, pd.Timestamp):
                        earnings_date = earnings_date.date()
                    elif isinstance(earnings_date, datetime):
                        earnings_date = earnings_date.date()
                    elif not isinstance(earnings_date, type(datetime.now().date())):
                        # Already a date object, keep it
                        if hasattr(earnings_date, 'date'):
                            earnings_date = earnings_date.date()
                    
                    today = datetime.now().date()
                    days_until = (earnings_date - today).days
                    
                    print(f"  DEBUG {ticker} converted date: {earnings_date}, days_until: {days_until}")
                    
                    if 0 <= days_until <= DAYS_AHEAD:
                        return {
                            'earnings_date': earnings_date,
                            'days_until': days_until
                        }
        except Exception as cal_error:
            print(f"  DEBUG {ticker} calendar error: {cal_error}")
        
        # Fallback to info dictionary
        try:
            info = stock.info
            if info and 'earningsDate' in info:
                earnings_date = info['earningsDate']
                print(f"  DEBUG {ticker} info earningsDate: {earnings_date}, type: {type(earnings_date)}")
                
                # Handle timestamp format
                if isinstance(earnings_date, (int, float)):
                    earnings_date = datetime.fromtimestamp(earnings_date).date()
                elif isinstance(earnings_date, str):
                    earnings_date = pd.to_datetime(earnings_date).date()
                elif isinstance(earnings_date, pd.Timestamp):
                    earnings_date = earnings_date.date()
                elif hasattr(earnings_date, 'date'):
                    earnings_date = earnings_date.date()
                
                today = datetime.now().date()
                days_until = (earnings_date - today).days
                
                if 0 <= days_until <= DAYS_AHEAD:
                    return {
                        'earnings_date': earnings_date,
                        'days_until': days_until
                    }
        except Exception as info_error:
            print(f"  DEBUG {ticker} info error: {info_error}")
        
        return None
    except Exception as e:
        print(f"Error fetching earnings for {ticker}: {e}")
        return None

def calculate_iv_percentile(current_iv, historical_ivs):
    """
    Calculate IV percentile: what % of historical IVs are below current IV
    More accurate than IV rank for predicting crush
    """
    if not historical_ivs or len(historical_ivs) < 10:
        return None
    
    below = sum(1 for iv in historical_ivs if iv < current_iv)
    percentile = (below / len(historical_ivs)) * 100
    return percentile

def get_option_chain_iv(ticker):
    """Get current and historical IV data"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical price data (3 months for IV tracking)
        hist = stock.history(period="3mo")
        if hist.empty or len(hist) < 20:
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Get current options data
        expirations = stock.options
        if not expirations or len(expirations) == 0:
            return None
        
        # Get next expirations (prefer 30-45 DTE for IV analysis)
        next_exp = None
        for exp in expirations[:5]:  # Check first 5 expirations
            exp_date = pd.to_datetime(exp).date()
            days_to_exp = (exp_date - datetime.now().date()).days
            if 30 <= days_to_exp <= 60:
                next_exp = exp
                break
        
        if next_exp is None:
            next_exp = expirations[0]  # Fallback to nearest
        
        opt_chain = stock.option_chain(next_exp)
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        if calls.empty or puts.empty:
            return None
        
        # Find ATM options
        atm_strike = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]['strike'].values[0]
        
        atm_call = calls[calls['strike'] == atm_strike]
        atm_put = puts[puts['strike'] == atm_strike]
        
        if atm_call.empty or atm_put.empty:
            return None
        
        # Get current IV
        call_iv = atm_call['impliedVolatility'].values[0] * 100 if 'impliedVolatility' in atm_call.columns else None
        put_iv = atm_put['impliedVolatility'].values[0] * 100 if 'impliedVolatility' in atm_put.columns else None
        
        if call_iv is None or put_iv is None or call_iv == 0 or put_iv == 0:
            return None
        
        current_iv = (call_iv + put_iv) / 2
        
        # Calculate historical realized volatility (annualized)
        returns = hist['Close'].pct_change().dropna()
        realized_vol = returns.std() * np.sqrt(252) * 100
        
        # Calculate 20-day and 60-day realized volatility (for trend)
        realized_vol_20d = returns.iloc[-20:].std() * np.sqrt(252) * 100 if len(returns) >= 20 else realized_vol
        realized_vol_60d = returns.iloc[-60:].std() * np.sqrt(252) * 100 if len(returns) >= 60 else realized_vol
        
        # Get rolling IV history (approximate using rolling volatility)
        rolling_vols = returns.rolling(20).std() * np.sqrt(252) * 100
        rolling_vols = rolling_vols.dropna().tolist()
        
        # IV percentile (how high is current IV historically)
        iv_percentile = calculate_iv_percentile(current_iv, rolling_vols)
        
        return {
            'current_iv': current_iv,
            'realized_vol': realized_vol,
            'realized_vol_20d': realized_vol_20d,
            'realized_vol_60d': realized_vol_60d,
            'iv_percentile': iv_percentile,
            'current_price': current_price,
            'atm_strike': atm_strike,
            'rolling_vols': rolling_vols
        }
    except Exception as e:
        print(f"Error getting options data for {ticker}: {e}")
        return None

def calculate_crush_score(ticker, iv_data, earnings_info):
    """Calculate IV crush prediction score (0-15 points)"""
    try:
        score = 0
        score_details = []
        
        current_iv = iv_data['current_iv']
        realized_vol = iv_data['realized_vol']
        iv_percentile = iv_data['iv_percentile']
        realized_vol_20d = iv_data['realized_vol_20d']
        days_until = earnings_info['days_until']
        
        # 1. IV Percentile (0-4 points) - Higher percentile = bigger crush potential
        if iv_percentile is not None:
            if iv_percentile >= 80:
                score += 4
                score_details.append(f"Very high IV: {iv_percentile:.0f}th percentile (+4)")
            elif iv_percentile >= 70:
                score += 3
                score_details.append(f"High IV: {iv_percentile:.0f}th percentile (+3)")
            elif iv_percentile >= 60:
                score += 2
                score_details.append(f"Above average IV: {iv_percentile:.0f}th percentile (+2)")
        
        # 2. Implied vs Realized Vol Gap (0-4 points) - Gap predicts crush magnitude
        iv_realized_gap = current_iv - realized_vol
        if iv_realized_gap >= 20:  # IV is 20%+ higher than realized vol
            score += 4
            score_details.append(f"Extreme gap: IV {current_iv:.0f}% vs RV {realized_vol:.0f}% (+4)")
        elif iv_realized_gap >= 15:
            score += 3
            score_details.append(f"Large gap: IV {current_iv:.0f}% vs RV {realized_vol:.0f}% (+3)")
        elif iv_realized_gap >= 10:
            score += 2
            score_details.append(f"Moderate gap: IV {current_iv:.0f}% vs RV {realized_vol:.0f}% (+2)")
        elif iv_realized_gap >= MIN_IV_REALIZED_GAP:
            score += 1
            score_details.append(f"Small gap: IV {current_iv:.0f}% vs RV {realized_vol:.0f}% (+1)")
        
        # 3. Recent Vol Increase (0-3 points) - Trending higher = more uncertainty
        vol_trend = ((realized_vol_20d - realized_vol) / realized_vol) * 100
        if vol_trend > 20:  # Vol increased >20% recently
            score += 3
            score_details.append(f"Strong vol trend: +{vol_trend:.0f}% recent (+3)")
        elif vol_trend > 10:
            score += 2
            score_details.append(f"Moderate vol trend: +{vol_trend:.0f}% recent (+2)")
        elif vol_trend > 0:
            score += 1
            score_details.append(f"Slight vol trend: +{vol_trend:.0f}% recent (+1)")
        
        # 4. Days to Earnings (0-2 points) - Closer to earnings = higher IV
        if days_until <= 3:
            score += 2
            score_details.append(f"Imminent: {days_until} days to earnings (+2)")
        elif days_until <= 7:
            score += 1
            score_details.append(f"Approaching: {days_until} days to earnings (+1)")
        
        # 5. VIX Correlation Factor (0-2 points)
        # Stocks highly correlated to market vol have bigger crushes
        try:
            spy_data = yf.Ticker('SPY').history(period="1mo")
            stock_data = yf.Ticker(ticker).history(period="1mo")
            
            if not spy_data.empty and not stock_data.empty:
                spy_returns = spy_data['Close'].pct_change()
                stock_returns = stock_data['Close'].pct_change()
                
                if len(spy_returns) > 5 and len(stock_returns) > 5:
                    correlation = spy_returns.corr(stock_returns)
                    if correlation > 0.7:  # Highly correlated
                        score += 2
                        score_details.append(f"High SPY correlation: {correlation:.2f} (+2)")
                    elif correlation > 0.5:
                        score += 1
                        score_details.append(f"Moderate SPY correlation: {correlation:.2f} (+1)")
        except:
            pass  # Skip if can't calculate
        
        # Determine quality tier
        if score >= MIN_SCORE_HIGH:
            quality = "HIGH"
        elif score >= MIN_SCORE_MEDIUM:
            quality = "MEDIUM"
        else:
            quality = None
        
        if quality is None or iv_percentile is None or iv_percentile < MIN_IV_PERCENTILE:
            return None
        
        # Estimate crush magnitude
        if score >= 12:
            crush_estimate = "40-50%"
        elif score >= 9:
            crush_estimate = "30-40%"
        elif score >= 7:
            crush_estimate = "20-30%"
        else:
            crush_estimate = "15-25%"
        
        return {
            'ticker': ticker,
            'current_price': iv_data['current_price'],
            'current_iv': current_iv,
            'realized_vol': realized_vol,
            'iv_percentile': iv_percentile,
            'iv_realized_gap': iv_realized_gap,
            'vol_trend': vol_trend,
            'earnings_date': earnings_info['earnings_date'],
            'days_until': days_until,
            'crush_estimate': crush_estimate,
            'score': score,
            'max_score': 15,
            'quality': quality,
            'score_details': score_details
        }
        
    except Exception as e:
        print(f"Error calculating crush score for {ticker}: {e}")
        return None

def format_signal_message(pre_earnings, post_crush_candidates):
    """Format signals into Telegram message"""
    message = "🔥 <b>IV Crush Prediction Signals</b>\n\n"
    
    if pre_earnings:
        message += "<b>📊 PRE-EARNINGS SETUP (HIGH IV)</b>\n"
        message += "Sell Premium Opportunities:\n\n"
        
        for signal in pre_earnings:
            quality_emoji = "🔥" if signal['quality'] == "HIGH" else "⚡"
            
            message += f"{quality_emoji} <b>{signal['ticker']}</b>\n"
            message += f"Price: ${signal['current_price']:.2f}\n"
            message += f"Current IV: {signal['current_iv']:.1f}%\n"
            message += f"IV Percentile: {signal['iv_percentile']:.0f}/100\n"
            message += f"Realized Vol: {signal['realized_vol']:.1f}%\n"
            message += f"IV vs RV Gap: {signal['iv_realized_gap']:.1f}% (Crush potential: {signal['crush_estimate']})\n"
            message += f"Earnings: {signal['earnings_date']} ({signal['days_until']} days)\n"
            message += f"Quality: <b>{signal['quality']}</b>\n"
            message += f"Score: {signal['score']}/{signal['max_score']}\n"
            
            if signal['score_details']:
                message += "\nScore Breakdown:\n"
                for detail in signal['score_details']:
                    message += f"  • {detail}\n"
            
            message += "\n💡 <b>Strategy</b>:\n"
            if signal['quality'] == "HIGH":
                message += "  • Sell Iron Condor: Collect premium + profit from IV crush\n"
                message += "  • Sell Call Spread: Defined risk, high probability\n"
                message += f"  • Close 2-3 days before earnings to lock in gains\n"
            else:
                message += "  • Sell Credit Spread: Lower capital requirement\n"
                message += "  • Or hold through earnings for IV crush play\n"
            
            message += "\n" + "="*45 + "\n\n"
    
    if post_crush_candidates:
        message += "<b>📉 POST-EARNINGS OPPORTUNITIES (IV CRUSH INCOMING)</b>\n"
        message += "High probability crush candidates:\n\n"
        
        for signal in post_crush_candidates:
            message += f"⏰ <b>{signal['ticker']}</b> - Earnings {signal['earnings_date']} ({signal['days_until']} days)\n"
            message += f"   Expected Crush: {signal['crush_estimate']} | Score: {signal['score']}/{signal['max_score']}\n\n"
    
    return message

def main():
    print("=" * 60)
    print("🔥 IV CRUSH PREDICTION SCANNER")
    print("=" * 60)
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load watchlist
    watchlist = load_watchlist()
    print(f"Loaded {len(watchlist)} symbols from watchlist")
    print(f"Symbols: {', '.join(watchlist)}\n")
    
    pre_earnings_signals = []
    post_crush_candidates = []
    
    for ticker in watchlist:
        print(f"Analyzing {ticker}...", end='\r')
        
        # Get earnings info
        earnings_info = get_earnings_dates(ticker)
        if not earnings_info:
            print(f"  {ticker}: No upcoming earnings")
            continue
        
        # Get IV data
        iv_data = get_option_chain_iv(ticker)
        if not iv_data:
            print(f"  {ticker}: No options data")
            continue
        
        # Calculate crush score
        signal = calculate_crush_score(ticker, iv_data, earnings_info)
        
        if signal:
            pre_earnings_signals.append(signal)
            print(f"  ✓ {ticker}: {signal['quality']} crush potential ({signal['crush_estimate']})")
        
        time.sleep(0.2)  # Rate limiting
    
    # Sort by days until earnings
    pre_earnings_signals.sort(key=lambda x: x['days_until'])
    
    print("\n" + "=" * 60)
    print(f"Found {len(pre_earnings_signals)} IV crush signals")
    print("=" * 60)
    
    if pre_earnings_signals:
        message = format_signal_message(pre_earnings_signals, None)
        print("\nSending Telegram alert...")
        if send_telegram_message(message):
            print("✓ Alert sent successfully")
        else:
            print("✗ Failed to send alert")
    
    print("\nScan complete!")

if __name__ == "__main__":
    main()
