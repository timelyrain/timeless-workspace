"""
Dark Pool Activity Scanner 🌑
Tracks large block trades and off-exchange activity (institutional accumulation).

Key Features:
- Detects unusually large block trades (>$500k)
- Monitors off-exchange volume percentage
- Tracks institutional accumulation patterns
- Identifies smart money positioning before public breakouts
- Volume-weighted analysis

Usage Tips:
1. Dark pool activity often precedes major moves (2-4 weeks lead time)
2. Rising dark pool % + price strength = accumulation
3. Large blocks at stable prices = controlled buying
4. Combine with other scanners for confirmation
5. Most reliable in liquid large caps

Strategy: Follow institutional money - they know something you don't (yet).
Schedule: Runs 2x daily (11 AM, 3 PM ET) to catch morning and afternoon activity.

Note: True dark pool data requires paid feeds (IEX, FINRA ATS). This scanner
uses volume anomalies and block trade detection as a proxy.
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
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Watchlist (centralized)
WATCHLIST = load_watchlist()

# === CUSTOMIZABLE SETTINGS ===

# Block trade definition (minimum value)
MIN_BLOCK_VALUE = 500000             # $500k minimum block size

# Volume anomaly thresholds
MIN_VOLUME_SPIKE = 2.0               # 2x average volume
SUSTAINED_VOLUME_DAYS = 3            # Volume elevated for N days = accumulation

# Price stability during accumulation (controlled buying)
MAX_PRICE_VOLATILITY = 3.0           # Price range < 3% during volume spike = controlled

# Intraday volume analysis (block detection proxy)
BLOCK_TRADE_THRESHOLD = 5.0          # Single candle volume > 5% of daily avg

# Accumulation pattern detection
MIN_ACCUMULATION_DAYS = 5            # At least 5 days of elevated volume
ACCUMULATION_LOOKBACK = 20           # Check last 20 days

# Quality filters
MIN_PRICE = 20.0                     # >= $20 (institutional grade)
MIN_AVG_VOLUME = 1000000             # >= 1M shares (liquid)
MIN_MARKET_CAP = 1_000_000_000       # >= $1B market cap

# Price action during accumulation
PRICE_TRENDING_UP = 2.0              # Price up >= 2% during accumulation = bullish
PRICE_FLAT_RANGE = 5.0               # Price within 5% range = controlled

# === END SETTINGS ===


def detect_block_trades(hist, lookback_days=5):
    """
    Detect potential block trades (large volume candles).
    Returns number of block trade days detected.
    """
    recent_data = hist.tail(lookback_days)
    avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
    
    block_days = 0
    block_details = []
    
    for idx, row in recent_data.iterrows():
        volume = row['Volume']
        price = row['Close']
        
        # Check if this candle had unusually high volume
        if volume > (avg_volume * BLOCK_TRADE_THRESHOLD):
            trade_value = volume * price
            
            if trade_value >= MIN_BLOCK_VALUE:
                block_days += 1
                block_details.append({
                    'date': idx,
                    'volume': volume,
                    'price': price,
                    'value': trade_value
                })
    
    return block_days, block_details


def detect_accumulation_pattern(hist, lookback=ACCUMULATION_LOOKBACK):
    """
    Detect sustained volume accumulation pattern.
    Returns: (is_accumulating, accumulation_days, price_change_pct)
    """
    recent_data = hist.tail(lookback)
    avg_volume = hist['Volume'].rolling(window=50).mean().tail(lookback)
    
    # Count days with elevated volume
    elevated_volume_days = (recent_data['Volume'] > avg_volume * MIN_VOLUME_SPIKE).sum()
    
    # Check if sustained
    is_accumulating = elevated_volume_days >= MIN_ACCUMULATION_DAYS
    
    # Price change during period
    start_price = recent_data['Close'].iloc[0]
    end_price = recent_data['Close'].iloc[-1]
    price_change_pct = ((end_price - start_price) / start_price) * 100
    
    # Check price stability/trend
    price_high = recent_data['High'].max()
    price_low = recent_data['Low'].min()
    price_range_pct = ((price_high - price_low) / price_low) * 100
    
    return is_accumulating, elevated_volume_days, price_change_pct, price_range_pct


def get_market_cap(ticker_obj):
    """Get market capitalization."""
    try:
        info = ticker_obj.info
        return info.get('marketCap', 0)
    except:
        return 0


def scan_dark_pool_activity():
    """Scan for dark pool / block trade activity."""
    signals = []
    
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
            avg_volume_50 = hist['Volume'].rolling(window=50).mean().iloc[-1]
            
            # Quality filters
            if current_price < MIN_PRICE or avg_volume_20 < MIN_AVG_VOLUME:
                continue
            
            market_cap = get_market_cap(stock)
            if market_cap < MIN_MARKET_CAP:
                continue
            
            # Detect recent block trades
            block_days, block_details = detect_block_trades(hist, lookback_days=5)
            
            # Detect accumulation pattern
            is_accumulating, accum_days, price_change, price_range = detect_accumulation_pattern(
                hist, ACCUMULATION_LOOKBACK
            )
            
            # Current volume analysis
            volume_ratio_20d = current_volume / avg_volume_20
            volume_ratio_50d = current_volume / avg_volume_50
            
            # Check for sustained elevated volume
            recent_5d = hist.tail(SUSTAINED_VOLUME_DAYS)
            avg_vol_recent = recent_5d['Volume'].mean()
            sustained_volume = avg_vol_recent > (avg_volume_50 * MIN_VOLUME_SPIKE)
            
            # Price stability check (controlled buying)
            recent_5d_range = ((recent_5d['High'].max() - recent_5d['Low'].min()) / recent_5d['Low'].min()) * 100
            is_controlled_buying = recent_5d_range <= MAX_PRICE_VOLATILITY
            
            # Accumulation with price strength
            is_price_trending_up = price_change >= PRICE_TRENDING_UP
            is_price_flat = price_range <= PRICE_FLAT_RANGE
            
            # Signal scoring
            score = 0
            
            if block_days >= 2:
                score += 4  # Multiple block trades
            elif block_days >= 1:
                score += 2
            
            if is_accumulating:
                score += 3  # Sustained pattern
            
            if sustained_volume:
                score += 2  # Recent volume spike
            
            if is_controlled_buying:
                score += 2  # Stable prices = controlled
            
            if is_price_trending_up:
                score += 2  # Bullish accumulation
            elif is_price_flat:
                score += 1  # Neutral accumulation
            
            if volume_ratio_20d >= MIN_VOLUME_SPIKE:
                score += 1
            
            # Minimum score to alert
            if score >= 7:  # Strong dark pool signal
                # Calculate total block value
                total_block_value = sum([b['value'] for b in block_details]) if block_details else 0
                
                # Quality rating
                if score >= 11:
                    quality = 'HIGH'
                elif score >= 9:
                    quality = 'MEDIUM'
                else:
                    quality = 'LOW'
                
                # Determine pattern type
                if is_controlled_buying and is_price_trending_up:
                    pattern = "BULLISH ACCUMULATION"
                elif is_controlled_buying:
                    pattern = "CONTROLLED BUYING"
                elif is_price_trending_up:
                    pattern = "VOLUME + MOMENTUM"
                else:
                    pattern = "UNUSUAL ACTIVITY"
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'volume_ratio_20d': volume_ratio_20d,
                    'block_days': block_days,
                    'total_block_value': total_block_value,
                    'accumulation_days': accum_days,
                    'price_change_pct': price_change,
                    'price_range_pct': price_range,
                    'recent_5d_range_pct': recent_5d_range,
                    'market_cap_b': market_cap / 1_000_000_000,
                    'score': score,
                    'quality': quality,
                    'pattern': pattern,
                    'block_details': block_details[:3]  # Top 3
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals


def format_alert_message(signals):
    """Format dark pool activity alerts for Telegram."""
    if not signals:
        return "🌑 Dark Pool Activity Scanner\n\nNo unusual block trade activity detected."
    
    # Sort by score descending
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    
    # Get timestamp
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🌑 Dark Pool Activity Scanner\n"
    message += f"⏰ {timestamp}\n"
    message += f"🔍 Found {len(signals)} unusual block trade signal(s)\n\n"
    
    for signal in signals[:8]:  # Top 8
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡" if signal['quality'] == 'MEDIUM' else "⚪"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  🏷️ Pattern: {signal['pattern']}\n"
        message += f"  📊 Volume: {signal['volume_ratio_20d']:.1f}x (20d avg)\n"
        message += f"  💰 Block Trades: {signal['block_days']} day(s)"
        
        if signal['total_block_value'] > 0:
            message += f" (${signal['total_block_value']/1_000_000:.1f}M total)\n"
        else:
            message += "\n"
        
        message += f"  📈 Accumulation: {signal['accumulation_days']} days ({signal['price_change_pct']:+.1f}%)\n"
        message += f"  📍 Price Range: {signal['recent_5d_range_pct']:.1f}% (5d)\n"
        message += f"  🏢 Market Cap: ${signal['market_cap_b']:.1f}B\n"
        message += f"  ⭐ Score: {signal['score']}/14 ({signal['quality']})\n"
        
        # Show top block trades
        if signal['block_details']:
            message += f"  🔸 Recent Blocks:\n"
            for block in signal['block_details'][:2]:
                block_date = block['date'].strftime('%m/%d')
                block_value_m = block['value'] / 1_000_000
                message += f"     • {block_date}: ${block_value_m:.1f}M @ ${block['price']:.2f}\n"
        
        message += "\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more signal(s)\n"
    
    message += "\n💡 Dark pool activity often leads price by 2-4 weeks"
    
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
    print("Starting Dark Pool Activity Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for block trades...")
    
    signals = scan_dark_pool_activity()
    
    print(f"\nFound {len(signals)} dark pool signal(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nDark Pool Activity Scanner completed")


if __name__ == "__main__":
    main()
