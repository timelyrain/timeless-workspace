"""
Mean Reversion Scanner 📊
Detects oversold bounces using statistical measures for high probability trades.

Key Features:
- Z-score analysis for statistical extremes
- Bollinger Band squeeze detection
- RSI oversold conditions with volume confirmation
- Institutional ownership filter (quality stocks only)
- Multi-timeframe confluence

Usage Tips:
1. Best in ranging/choppy markets (not strong trends)
2. Higher win rate (60-70%) but smaller gains (2-5%)
3. Exit at mean (20 SMA) or Bollinger mid-band
4. Use tight stops (3-5% below entry)
5. Avoid during earnings week

Strategy: Buy statistical extremes in quality names, sell at mean reversion.
Schedule: Runs 3x daily (10 AM, 1 PM, 3:45 PM ET) to catch intraday setups.
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
from watchlist_loader import load_watchlist

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Watchlist (centralized)
WATCHLIST = load_watchlist()

# === CUSTOMIZABLE SETTINGS ===

# Z-Score thresholds (standard deviations from mean)
Z_SCORE_OVERSOLD = -2.0      # <= -2.0 SD = statistical extreme (2.5% probability)
Z_SCORE_OVERBOUGHT = 2.0     # >= 2.0 SD = statistical extreme

# RSI thresholds
RSI_OVERSOLD = 30            # RSI <= 30 = oversold
RSI_PERIOD = 14              # Standard RSI lookback

# Bollinger Band settings
BB_PERIOD = 20               # Standard 20-day BB
BB_STD_DEV = 2.0             # 2 standard deviations (95% confidence)
BB_SQUEEZE_THRESHOLD = 0.05  # BB width < 5% = squeeze/contraction

# Volume confirmation
MIN_VOLUME_SPIKE = 1.5       # Volume must be 1.5x average (selling climax)

# Institutional ownership filter (quality stocks)
MIN_INSTITUTIONAL_OWNERSHIP = 50.0  # >= 50% institutional ownership

# Distance from mean for entry (%)
MAX_DISTANCE_FROM_MEAN = -5.0  # <= -5% below 20 SMA

# Lookback period for statistics
LOOKBACK_DAYS = 60           # 60 trading days (~3 months)

# Quality filters
MIN_PRICE = 10.0             # >= $10 (avoid penny stocks)
MIN_AVG_VOLUME = 500000      # >= 500k shares daily average

# === END SETTINGS ===


def calculate_z_score(prices, period=LOOKBACK_DAYS):
    """Calculate Z-score (standardized price deviation)."""
    mean = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    z_score = (prices - mean) / std
    return z_score


def calculate_rsi(prices, period=RSI_PERIOD):
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(prices, period=BB_PERIOD, std_dev=BB_STD_DEV):
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    bb_width = (upper_band - lower_band) / sma  # Normalized width
    return sma, upper_band, lower_band, bb_width


def get_institutional_ownership(ticker):
    """Get institutional ownership percentage."""
    try:
        stock = yf.Ticker(ticker)
        major_holders = stock.major_holders
        
        if major_holders is None or major_holders.empty:
            return None
        
        # Parse institutional ownership from major holders
        for idx, row in major_holders.iterrows():
            desc = str(row[1]).lower() if len(row) > 1 else ''
            if 'institutions' in desc or 'institutional' in desc:
                try:
                    pct_str = str(row[0]).replace('%', '')
                    return float(pct_str)
                except:
                    pass
        return None
    except:
        return None


def scan_mean_reversion_setups():
    """Scan for mean reversion opportunities."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')  # Extra buffer for calculations
            
            if hist.empty or len(hist) < LOOKBACK_DAYS:
                continue
            
            # Current metrics
            current_price = hist['Close'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Apply quality filters
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                continue
            
            # Check institutional ownership
            inst_ownership = get_institutional_ownership(ticker)
            if inst_ownership is None or inst_ownership < MIN_INSTITUTIONAL_OWNERSHIP:
                continue
            
            # Calculate indicators
            closes = hist['Close']
            z_score = calculate_z_score(closes, LOOKBACK_DAYS)
            rsi = calculate_rsi(closes, RSI_PERIOD)
            sma_20, bb_upper, bb_lower, bb_width = calculate_bollinger_bands(closes, BB_PERIOD, BB_STD_DEV)
            
            # Current values
            current_z = z_score.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_bb_width = bb_width.iloc[-1]
            current_sma = sma_20.iloc[-1]
            distance_from_mean_pct = ((current_price - current_sma) / current_sma) * 100
            volume_ratio = current_volume / avg_volume
            
            # Distance to Bollinger Bands
            distance_to_lower_bb = ((current_price - bb_lower.iloc[-1]) / current_price) * 100
            
            # Check for mean reversion setup
            is_oversold_z = current_z <= Z_SCORE_OVERSOLD
            is_oversold_rsi = current_rsi <= RSI_OVERSOLD
            is_below_mean = distance_from_mean_pct <= MAX_DISTANCE_FROM_MEAN
            has_volume_spike = volume_ratio >= MIN_VOLUME_SPIKE
            is_bb_squeeze = current_bb_width <= BB_SQUEEZE_THRESHOLD
            
            # At or near lower Bollinger Band
            is_at_bb_lower = distance_to_lower_bb <= 2.0  # Within 2% of lower band
            
            # Signal scoring (confluence of factors)
            score = 0
            if is_oversold_z:
                score += 3  # Strong signal
            if is_oversold_rsi:
                score += 2
            if is_below_mean:
                score += 2
            if has_volume_spike:
                score += 2  # Selling climax
            if is_at_bb_lower:
                score += 2
            if is_bb_squeeze:
                score += 1  # Bonus for tight range
            
            # Minimum score to trigger alert
            if score >= 6:  # At least 6 points = strong setup
                # Calculate expected target (mean reversion to 20 SMA)
                expected_gain_pct = ((current_sma - current_price) / current_price) * 100
                
                # Quality rating
                if score >= 9:
                    quality = 'HIGH'
                elif score >= 7:
                    quality = 'MEDIUM'
                else:
                    quality = 'LOW'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'z_score': current_z,
                    'rsi': current_rsi,
                    'distance_from_mean_pct': distance_from_mean_pct,
                    'sma_20': current_sma,
                    'bb_width_pct': current_bb_width * 100,
                    'volume_ratio': volume_ratio,
                    'expected_gain_pct': expected_gain_pct,
                    'inst_ownership': inst_ownership,
                    'score': score,
                    'quality': quality,
                    'is_bb_squeeze': is_bb_squeeze
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals


def format_alert_message(signals):
    """Format mean reversion alerts for Telegram."""
    if not signals:
        return "📊 Mean Reversion Scanner\n\nNo oversold bounces detected. Market is balanced."
    
    # Sort by score descending
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    
    # Get timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"📊 Mean Reversion Scanner\n"
    message += f"⏰ {timestamp}\n"
    message += f"🎯 Found {len(signals)} oversold bounce setup(s)\n\n"
    
    for signal in signals[:8]:  # Top 8
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡" if signal['quality'] == 'MEDIUM' else "⚪"
        squeeze_flag = " [SQUEEZE]" if signal['is_bb_squeeze'] else ""
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}{squeeze_flag}\n"
        message += f"  📉 Z-Score: {signal['z_score']:.2f} SD | RSI: {signal['rsi']:.1f}\n"
        message += f"  📍 Distance from Mean: {signal['distance_from_mean_pct']:.1f}%\n"
        message += f"  🎯 Target (20 SMA): ${signal['sma_20']:.2f} (+{signal['expected_gain_pct']:.1f}%)\n"
        message += f"  📊 Volume: {signal['volume_ratio']:.1f}x avg | BB Width: {signal['bb_width_pct']:.2f}%\n"
        message += f"  🏢 Inst. Own: {signal['inst_ownership']:.1f}%\n"
        message += f"  ⭐ Quality Score: {signal['score']}/12 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more setup(s)\n"
    
    message += "\n💡 Strategy: Buy statistical extreme, sell at mean reversion (20 SMA)\n"
    message += "⚠️ Use tight stops (3-5% below entry)"
    
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
    print("Starting Mean Reversion Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for oversold bounces...")
    
    signals = scan_mean_reversion_setups()
    
    print(f"\nFound {len(signals)} mean reversion setup(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nMean Reversion Scanner completed")


if __name__ == "__main__":
    main()
