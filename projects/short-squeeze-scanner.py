"""
Short Interest Squeeze Scanner 🔥
Detects high short interest stocks with squeeze potential (GME/AMC-style setups).

Key Features:
- Monitors short interest % of float
- Tracks days to cover ratio
- Detects volume + price breakouts in heavily shorted stocks
- Identifies catalyst convergence (short squeeze triggers)
- Cost to borrow analysis (when available via yfinance)

Usage Tips:
1. Best setups: SI > 20% + days-to-cover > 3 + technical breakout
2. Extreme risk/reward - can move 50-200% in days
3. Enter on confirmed breakout, not early
4. Use trailing stops (volatility is extreme)
5. Watch for momentum fade (exit fast)

Strategy: Find over-shorted stocks near technical breakout levels.
Schedule: Runs 2x daily (9:45 AM, 2 PM ET) to catch squeeze momentum.

Note: Short interest data updated bi-weekly (FINRA). This scanner uses
yfinance data which may have delays.
"""

import yfinance as yf
import requests
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

# Watchlist
WATCHLIST = [
    'ABT', 'ADBE', 'AMT', 'ANET', 'APP', 'ASML', 'AVGO', 'COIN', 'COST', 'CRM',
    'CRWD', 'DDOG', 'DIS', 'GOOGL', 'GS', 'HUBS', 'ISRG', 'JNJ', 'JPM', 'LLY',
    'MA', 'MCD', 'META', 'MELI', 'MSFT', 'NET', 'NFLX', 'NOW', 'NVDA', 'ORCL',
    'PANW', 'PFE', 'PG', 'PLTR', 'PYPL', 'S', 'SHOP', 'SNOW', 'SOFI', 'TEAM',
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

# === CUSTOMIZABLE SETTINGS ===

# Short interest thresholds
MIN_SHORT_INTEREST_PCT = 15.0        # >= 15% of float shorted
HIGH_SHORT_INTEREST = 30.0           # >= 30% = extreme
EXTREME_SHORT_INTEREST = 50.0        # >= 50% = powder keg

# Days to cover (DTG) - time for shorts to exit
MIN_DAYS_TO_COVER = 2.0              # >= 2 days (harder to cover)
HIGH_DAYS_TO_COVER = 5.0             # >= 5 days (squeeze catalyst)

# Volume spike (shorts getting squeezed)
MIN_VOLUME_SPIKE = 2.0               # 2x average volume
EXTREME_VOLUME_SPIKE = 5.0           # 5x = panic covering

# Price action (breakout required)
MIN_PRICE_INCREASE_5D = 10.0         # >= 10% up in last 5 days
MIN_PRICE_INCREASE_1D = 5.0          # >= 5% up today (momentum)

# Technical breakout levels
BREAKOUT_ABOVE_MA = True             # Must be above 20 SMA
MIN_RS_VS_SPY = 2.0                  # Relative strength vs SPY >= 2%

# Quality filters
MIN_PRICE = 5.0                      # >= $5 (avoid penny stocks)
MIN_AVG_VOLUME = 500000              # >= 500k shares (liquid enough)

# Options activity (if available)
CALL_PUT_RATIO_BULLISH = 2.0         # Call/Put volume >= 2.0 = retail bullish

# === END SETTINGS ===


def get_short_interest_data(ticker_obj):
    """
    Get short interest data from yfinance.
    Returns: (short_pct_float, days_to_cover, short_ratio)
    """
    try:
        info = ticker_obj.info
        
        # Short % of float
        short_pct_float = info.get('shortPercentOfFloat', 0) * 100  # Convert to %
        
        # Short ratio (days to cover)
        short_ratio = info.get('shortRatio', 0)
        
        # Some tickers report 'sharesShort' and 'sharesOutstanding'
        shares_short = info.get('sharesShort', 0)
        float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
        
        # Recalculate if needed
        if short_pct_float == 0 and shares_short > 0 and float_shares > 0:
            short_pct_float = (shares_short / float_shares) * 100
        
        return short_pct_float, short_ratio, shares_short
    
    except Exception as e:
        return 0, 0, 0


def calculate_relative_strength(stock_hist, spy_hist):
    """Calculate relative strength vs SPY."""
    stock_return = ((stock_hist['Close'].iloc[-1] - stock_hist['Close'].iloc[0]) / 
                    stock_hist['Close'].iloc[0]) * 100
    spy_return = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[0]) / 
                  spy_hist['Close'].iloc[0]) * 100
    
    rs = stock_return - spy_return
    return rs


def scan_short_squeeze_setups():
    """Scan for short squeeze opportunities."""
    signals = []
    
    # Get SPY data for RS calculation
    spy = yf.Ticker('SPY')
    spy_hist = spy.history(period='1mo')
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if hist.empty or len(hist) < 60:
                continue
            
            # Current metrics
            current_price = hist['Close'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            avg_volume_20 = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Quality filters
            if current_price < MIN_PRICE or avg_volume_20 < MIN_AVG_VOLUME:
                continue
            
            # Get short interest data
            short_pct, days_to_cover, shares_short = get_short_interest_data(stock)
            
            # Skip if no short interest
            if short_pct < MIN_SHORT_INTEREST_PCT:
                continue
            
            # Calculate price changes
            price_5d_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else hist['Close'].iloc[0]
            price_1d_ago = hist['Close'].iloc[-2] if len(hist) >= 2 else hist['Close'].iloc[0]
            
            price_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
            price_change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
            
            # Volume analysis
            volume_ratio = current_volume / avg_volume_20
            
            # Technical indicators
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            above_sma = current_price > sma_20
            
            # Relative strength vs SPY
            rs_vs_spy = calculate_relative_strength(hist.tail(20), spy_hist.tail(20))
            
            # Check squeeze criteria
            is_high_si = short_pct >= MIN_SHORT_INTEREST_PCT
            is_extreme_si = short_pct >= EXTREME_SHORT_INTEREST
            has_high_dtc = days_to_cover >= MIN_DAYS_TO_COVER
            has_volume_spike = volume_ratio >= MIN_VOLUME_SPIKE
            has_extreme_volume = volume_ratio >= EXTREME_VOLUME_SPIKE
            has_price_momentum_5d = price_change_5d >= MIN_PRICE_INCREASE_5D
            has_price_momentum_1d = price_change_1d >= MIN_PRICE_INCREASE_1D
            is_breaking_out = above_sma and rs_vs_spy >= MIN_RS_VS_SPY
            
            # Signal scoring
            score = 0
            
            if is_extreme_si:
                score += 5  # Extreme SI = huge potential
            elif short_pct >= HIGH_SHORT_INTEREST:
                score += 3
            elif is_high_si:
                score += 2
            
            if has_high_dtc:
                score += 2  # Hard to cover
            
            if days_to_cover >= HIGH_DAYS_TO_COVER:
                score += 2  # Very hard to cover
            
            if has_extreme_volume:
                score += 3  # Panic volume
            elif has_volume_spike:
                score += 2
            
            if has_price_momentum_5d:
                score += 2  # Squeeze starting
            
            if has_price_momentum_1d:
                score += 1  # Recent momentum
            
            if is_breaking_out:
                score += 2  # Technical breakout
            
            # Minimum score to alert
            if score >= 8:  # Strong squeeze potential
                # Calculate potential upside (rough estimate)
                # Assumes 20-50% of shorts forced to cover
                potential_covering_volume = (shares_short * 0.35) if shares_short > 0 else 0
                avg_daily_volume = avg_volume_20
                covering_pressure_days = (potential_covering_volume / avg_daily_volume) if avg_daily_volume > 0 else 0
                
                # Quality rating
                if score >= 13:
                    quality = 'EXTREME'
                elif score >= 11:
                    quality = 'HIGH'
                elif score >= 9:
                    quality = 'MEDIUM'
                else:
                    quality = 'LOW'
                
                # Squeeze stage
                if has_extreme_volume and has_price_momentum_1d:
                    stage = "ACTIVE SQUEEZE"
                elif has_volume_spike and has_price_momentum_5d:
                    stage = "SQUEEZE STARTING"
                elif is_breaking_out:
                    stage = "PRE-SQUEEZE BREAKOUT"
                else:
                    stage = "SETUP FORMING"
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'short_pct': short_pct,
                    'days_to_cover': days_to_cover,
                    'volume_ratio': volume_ratio,
                    'price_change_5d': price_change_5d,
                    'price_change_1d': price_change_1d,
                    'rs_vs_spy': rs_vs_spy,
                    'above_sma_20': above_sma,
                    'sma_20': sma_20,
                    'covering_pressure_days': covering_pressure_days,
                    'score': score,
                    'quality': quality,
                    'stage': stage
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals


def format_alert_message(signals):
    """Format short squeeze alerts for Telegram."""
    if not signals:
        return "🔥 Short Squeeze Scanner\n\nNo high short interest squeeze setups detected."
    
    # Sort by score descending
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    
    # Get timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🔥 Short Squeeze Scanner\n"
    message += f"⏰ {timestamp}\n"
    message += f"💥 Found {len(signals)} squeeze setup(s)\n\n"
    
    for signal in signals[:8]:  # Top 8
        if signal['quality'] == 'EXTREME':
            quality_emoji = "🔴"
        elif signal['quality'] == 'HIGH':
            quality_emoji = "🟢"
        elif signal['quality'] == 'MEDIUM':
            quality_emoji = "🟡"
        else:
            quality_emoji = "⚪"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  🎯 Stage: {signal['stage']}\n"
        message += f"  🩳 Short Interest: {signal['short_pct']:.1f}% of float\n"
        message += f"  ⏱️ Days to Cover: {signal['days_to_cover']:.1f} days\n"
        message += f"  📊 Volume: {signal['volume_ratio']:.1f}x average\n"
        message += f"  📈 Performance: {signal['price_change_1d']:+.1f}% (1d) | {signal['price_change_5d']:+.1f}% (5d)\n"
        message += f"  💪 RS vs SPY: {signal['rs_vs_spy']:+.1f}%\n"
        message += f"  🎯 20 SMA: ${signal['sma_20']:.2f} ({'ABOVE' if signal['above_sma_20'] else 'BELOW'})\n"
        message += f"  ⭐ Squeeze Score: {signal['score']}/18 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more setup(s)\n"
    
    message += "\n⚠️ EXTREME RISK: Short squeezes are violent and unpredictable\n"
    message += "💡 Enter on breakout confirmation, use trailing stops"
    
    return message


def send_telegram_message(message):
    """Send message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': None
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"Telegram error: {response.status_code} {response.text}")
            return False
        
        print("Alert sent successfully")
        return True
    
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def main():
    """Main execution."""
    print("Starting Short Squeeze Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for squeeze setups...")
    
    signals = scan_short_squeeze_setups()
    
    print(f"\nFound {len(signals)} short squeeze setup(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nShort Squeeze Scanner completed")


if __name__ == "__main__":
    main()
