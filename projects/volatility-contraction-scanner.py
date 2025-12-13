"""
Volatility Contraction Scanner 🎯
Detects stocks in tight consolidation before explosive moves (institutional favorite).

Key Features:
- ATR (Average True Range) compression analysis
- Bollinger Band width at multi-week lows
- Low volatility consolidation patterns
- Volume drying up (coiling spring effect)
- Breakout proximity detection

Usage Tips:
1. Best setup: Low volatility → High volatility (statistical tendency)
2. Often precedes 20%+ moves within days/weeks
3. Enter on breakout above consolidation range
4. Use wider stops (consolidation range low)
5. Position size smaller (higher volatility expected)

Strategy: Find the calm before the storm - volatility clusters.
Schedule: Runs daily at 4:30 PM ET (after market close for clean data).
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

# ATR (Average True Range) settings
ATR_PERIOD = 14                      # Standard ATR lookback
ATR_COMPRESSION_THRESHOLD = 0.50     # ATR < 50% of 60-day max = extreme compression

# Bollinger Band width settings
BB_PERIOD = 20                       # Standard 20-day BB
BB_STD_DEV = 2.0                     # 2 standard deviations
BB_WIDTH_LOOKBACK = 60               # Compare to 60-day BB width
BB_WIDTH_PERCENTILE = 10             # Current width in lowest 10th percentile

# Consolidation range settings
CONSOLIDATION_PERIOD = 20            # Look at last 20 days
MAX_PRICE_RANGE_PCT = 10.0           # High-low range must be < 10% (tight)
MIN_CONSOLIDATION_DAYS = 10          # At least 10 days in range

# Volume analysis
VOLUME_DRYUP_THRESHOLD = 0.7         # Volume < 70% of average = drying up

# Trend requirement (want consolidation in uptrend)
MIN_20_50_SMA_SLOPE = 0.0            # 20 SMA above 50 SMA (uptrend bias)
ALLOW_DOWNTREND = False              # Set True to scan in downtrends too

# Quality filters
MIN_PRICE = 15.0                     # >= $15
MIN_AVG_VOLUME = 500000              # >= 500k shares

# Breakout proximity (how close to range high?)
BREAKOUT_PROXIMITY_PCT = 5.0         # Within 5% of consolidation high

# === END SETTINGS ===


def calculate_atr(high, low, close, period=ATR_PERIOD):
    """Calculate Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def calculate_bollinger_width(prices, period=BB_PERIOD, std_dev=BB_STD_DEV):
    """Calculate Bollinger Band width (normalized)."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    bb_width = (upper_band - lower_band) / sma
    return bb_width


def detect_consolidation(prices, period=CONSOLIDATION_PERIOD):
    """
    Detect tight consolidation pattern.
    Returns: (is_consolidating, range_pct, consolidation_high, consolidation_low)
    """
    recent_prices = prices[-period:]
    
    if len(recent_prices) < MIN_CONSOLIDATION_DAYS:
        return False, 0, 0, 0
    
    high = recent_prices.max()
    low = recent_prices.min()
    range_pct = ((high - low) / low) * 100
    
    # Check if range is tight enough
    is_consolidating = range_pct <= MAX_PRICE_RANGE_PCT
    
    return is_consolidating, range_pct, high, low


def calculate_sma_slope(prices, short_period=20, long_period=50):
    """Calculate SMA slope (trend direction)."""
    sma_short = prices.rolling(window=short_period).mean()
    sma_long = prices.rolling(window=long_period).mean()
    
    # Slope: difference between SMAs (positive = uptrend)
    slope = ((sma_short.iloc[-1] - sma_long.iloc[-1]) / sma_long.iloc[-1]) * 100
    
    return slope, sma_short.iloc[-1], sma_long.iloc[-1]


def scan_volatility_contraction():
    """Scan for volatility contraction patterns."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            
            if hist.empty or len(hist) < 100:
                continue
            
            # Current metrics
            current_price = hist['Close'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            avg_volume_20 = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Quality filters
            if current_price < MIN_PRICE or avg_volume_20 < MIN_AVG_VOLUME:
                continue
            
            # Calculate ATR
            atr = calculate_atr(hist['High'], hist['Low'], hist['Close'], ATR_PERIOD)
            current_atr = atr.iloc[-1]
            atr_60d_max = atr[-60:].max()
            atr_compression_ratio = current_atr / atr_60d_max if atr_60d_max > 0 else 1
            
            # Calculate Bollinger Band width
            bb_width = calculate_bollinger_width(hist['Close'], BB_PERIOD, BB_STD_DEV)
            current_bb_width = bb_width.iloc[-1]
            bb_width_60d = bb_width[-BB_WIDTH_LOOKBACK:]
            bb_width_percentile = (bb_width_60d < current_bb_width).sum() / len(bb_width_60d) * 100
            
            # Detect consolidation
            is_consolidating, range_pct, consol_high, consol_low = detect_consolidation(
                hist['Close'], CONSOLIDATION_PERIOD
            )
            
            # SMA slope (trend)
            sma_slope, sma_20, sma_50 = calculate_sma_slope(hist['Close'], 20, 50)
            
            # Volume analysis
            volume_ratio = current_volume / avg_volume_20
            is_volume_dryup = volume_ratio <= VOLUME_DRYUP_THRESHOLD
            
            # Breakout proximity
            distance_to_high_pct = ((consol_high - current_price) / current_price) * 100
            is_near_breakout = distance_to_high_pct <= BREAKOUT_PROXIMITY_PCT
            
            # Check criteria
            is_atr_compressed = atr_compression_ratio <= ATR_COMPRESSION_THRESHOLD
            is_bb_narrow = bb_width_percentile <= BB_WIDTH_PERCENTILE
            is_uptrend = sma_slope >= MIN_20_50_SMA_SLOPE
            
            # Trend requirement
            if not ALLOW_DOWNTREND and not is_uptrend:
                continue
            
            # Signal scoring
            score = 0
            if is_atr_compressed:
                score += 4  # Primary signal
            if is_bb_narrow:
                score += 3  # Strong confirmation
            if is_consolidating:
                score += 3  # Pattern present
            if is_volume_dryup:
                score += 2  # Volume confirms
            if is_near_breakout:
                score += 2  # Ready to pop
            if is_uptrend:
                score += 1  # Trend bias
            
            # Minimum score to alert
            if score >= 8:  # Strong contraction setup
                # Calculate expected move (historical ATR expansion)
                expected_move_pct = (atr_60d_max / current_price) * 100 * 2  # 2x ATR expansion
                
                # Quality rating
                if score >= 12:
                    quality = 'HIGH'
                elif score >= 10:
                    quality = 'MEDIUM'
                else:
                    quality = 'LOW'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'atr_compression_ratio': atr_compression_ratio,
                    'current_atr': current_atr,
                    'bb_width_percentile': bb_width_percentile,
                    'bb_width_pct': current_bb_width * 100,
                    'consolidation_range_pct': range_pct,
                    'consol_high': consol_high,
                    'consol_low': consol_low,
                    'volume_ratio': volume_ratio,
                    'sma_slope': sma_slope,
                    'distance_to_breakout_pct': distance_to_high_pct,
                    'expected_move_pct': expected_move_pct,
                    'score': score,
                    'quality': quality,
                    'is_near_breakout': is_near_breakout
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals


def format_alert_message(signals):
    """Format volatility contraction alerts for Telegram."""
    if not signals:
        return "🎯 Volatility Contraction Scanner\n\nNo tight consolidations detected. Volatility is normal."
    
    # Sort by score descending
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    
    # Get timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🎯 Volatility Contraction Scanner\n"
    message += f"⏰ {timestamp}\n"
    message += f"🔥 Found {len(signals)} coiled spring setup(s)\n\n"
    
    for signal in signals[:8]:  # Top 8
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡" if signal['quality'] == 'MEDIUM' else "⚪"
        breakout_flag = " [NEAR BREAKOUT]" if signal['is_near_breakout'] else ""
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}{breakout_flag}\n"
        message += f"  📉 ATR Compression: {signal['atr_compression_ratio']:.1%} (Current ATR: ${signal['current_atr']:.2f})\n"
        message += f"  📊 BB Width Percentile: {signal['bb_width_percentile']:.0f}th ({signal['bb_width_pct']:.2f}%)\n"
        message += f"  📍 Consolidation Range: {signal['consolidation_range_pct']:.1f}%\n"
        message += f"  🎯 Breakout Level: ${signal['consol_high']:.2f} (+{signal['distance_to_breakout_pct']:.1f}%)\n"
        message += f"  📊 Volume: {signal['volume_ratio']:.2f}x | Trend: {signal['sma_slope']:+.1f}%\n"
        message += f"  💥 Expected Move: {signal['expected_move_pct']:.1f}% on expansion\n"
        message += f"  ⭐ Quality Score: {signal['score']}/15 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more setup(s)\n"
    
    message += "\n💡 Strategy: Wait for breakout above consolidation high\n"
    message += "⚠️ Low volatility clusters into high volatility - expect 20%+ moves"
    
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
    print("Starting Volatility Contraction Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for coiled springs...")
    
    signals = scan_volatility_contraction()
    
    print(f"\nFound {len(signals)} volatility contraction setup(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nVolatility Contraction Scanner completed")


if __name__ == "__main__":
    main()
