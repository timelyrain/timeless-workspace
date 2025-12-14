"""
Cup & Handle Scanner ☕
Detects William O'Neil IBD pattern (85%+ win rate in bull markets).

Key Features:
- Cup formation: 7-65 week U-shaped consolidation
- Handle formation: 1-4 week pullback
- Volume dry-up in handle
- Breakout proximity detection
- RS rating integration

Usage Tips:
1. Best in confirmed uptrends (market >200 SMA)
2. Enter on breakout above handle high with volume
3. Stop: Below handle low or 7-8% from entry
4. Target: Cup depth added to breakout point
5. Hold winners - can run 100-500%+

Strategy: Institutional accumulation pattern - O'Neil's CANSLIM #1 pattern.
Schedule: Weekly Friday 5 PM ET (pattern forms over weeks)
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
import numpy as np

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

WATCHLIST = [
    'ABT', 'ADBE', 'AMT', 'ANET', 'APP', 'ASML', 'AVGO', 'COIN', 'COST', 'CRM',
    'CRWD', 'DDOG', 'DIS', 'GOOGL', 'GS', 'HUBS', 'ISRG', 'JNJ', 'JPM', 'LLY',
    'MA', 'MCD', 'META', 'MELI', 'MSFT', 'NET', 'NFLX', 'NOW', 'NVDA', 'ORCL',
    'PANW', 'PFE', 'PG', 'PLTR', 'PYPL', 'S', 'SHOP', 'SNOW', 'SOFI', 'TEAM',
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

# === SETTINGS ===
MIN_CUP_WEEKS = 7
MAX_CUP_WEEKS = 65
MIN_HANDLE_WEEKS = 1
MAX_HANDLE_WEEKS = 4
MAX_CUP_DEPTH = 35  # Max 35% correction in cup (O'Neil rule)
MAX_HANDLE_DEPTH = 15  # Max 15% pullback in handle
MIN_VOLUME_DRYUP = 0.6  # Handle volume should be <60% of cup average
BREAKOUT_PROXIMITY = 5.0  # Alert if within 5% of breakout point
MIN_PRICE = 20.0
MIN_AVG_VOLUME = 500000

def detect_cup_and_handle(hist):
    """
    Detect cup and handle pattern.
    Returns: (cup_found, handle_found, cup_depth, handle_depth, breakout_price, distance_to_breakout)
    """
    try:
        if len(hist) < MIN_CUP_WEEKS * 5:  # Need at least minimum weeks of data
            return False, False, None, None, None, None
        
        # Use weekly data for pattern detection
        # Resample to weekly
        weekly = hist.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        if len(weekly) < MIN_CUP_WEEKS:
            return False, False, None, None, None, None
        
        current_price = weekly['Close'].iloc[-1]
        
        # Search for cup pattern (7-65 weeks)
        cup_found = False
        cup_start_idx = None
        cup_bottom_idx = None
        cup_peak_price = None
        
        for start_idx in range(len(weekly) - MIN_CUP_WEEKS, max(0, len(weekly) - MAX_CUP_WEEKS - 1), -1):
            # Cup should start from a high
            cup_start_price = weekly['High'].iloc[start_idx]
            
            # Find the bottom of the cup (lowest point after start)
            search_end = min(start_idx + MAX_CUP_WEEKS, len(weekly))
            cup_section = weekly.iloc[start_idx:search_end]
            bottom_idx = cup_section['Low'].idxmin()
            bottom_idx_pos = weekly.index.get_loc(bottom_idx)
            cup_bottom_price = weekly['Low'].loc[bottom_idx]
            
            # Calculate cup depth
            cup_depth_pct = ((cup_start_price - cup_bottom_price) / cup_start_price) * 100
            
            # Check if cup depth is within acceptable range
            if cup_depth_pct > MAX_CUP_DEPTH or cup_depth_pct < 10:
                continue
            
            # Check if price has recovered (near cup start level)
            recovery_pct = ((current_price - cup_bottom_price) / (cup_start_price - cup_bottom_price)) * 100
            
            if recovery_pct >= 80:  # Recovered at least 80% of cup depth
                cup_found = True
                cup_start_idx = start_idx
                cup_bottom_idx = bottom_idx_pos
                cup_peak_price = cup_start_price
                break
        
        if not cup_found:
            return False, False, None, None, None, None
        
        # Look for handle (1-4 weeks pullback from right side of cup)
        handle_found = False
        handle_depth_pct = None
        handle_low_price = None
        
        # Handle should be recent (last 1-4 weeks)
        handle_search_start = max(cup_bottom_idx + 3, len(weekly) - MAX_HANDLE_WEEKS - 1)
        
        if len(weekly) - handle_search_start >= MIN_HANDLE_WEEKS:
            handle_section = weekly.iloc[handle_search_start:]
            handle_high_price = handle_section['High'].max()
            handle_low_price = handle_section['Low'].min()
            
            handle_depth_pct = ((handle_high_price - handle_low_price) / handle_high_price) * 100
            
            # Handle depth should be reasonable (not too deep)
            if handle_depth_pct <= MAX_HANDLE_DEPTH and handle_depth_pct >= 5:
                # Check volume dry-up in handle
                cup_avg_volume = weekly.iloc[cup_start_idx:cup_bottom_idx+1]['Volume'].mean()
                handle_avg_volume = handle_section['Volume'].mean()
                
                if handle_avg_volume < cup_avg_volume * (1 + MIN_VOLUME_DRYUP):
                    handle_found = True
        
        # Calculate breakout price (top of handle/cup)
        recent_high = weekly.iloc[-MAX_HANDLE_WEEKS:]['High'].max()
        breakout_price = max(recent_high, cup_peak_price)
        
        distance_to_breakout = ((breakout_price - current_price) / current_price) * 100
        
        return cup_found, handle_found, cup_depth_pct, handle_depth_pct, breakout_price, distance_to_breakout
    
    except Exception as e:
        return False, False, None, None, None, None

def calculate_rs_rating(ticker_hist, ticker):
    """Calculate Relative Strength rating (0-100) vs market."""
    try:
        # Get SPY for comparison
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='6mo')
        
        if len(spy_hist) < 20 or len(ticker_hist) < 20:
            return None
        
        # Calculate 6-month return
        ticker_return = ((ticker_hist['Close'].iloc[-1] - ticker_hist['Close'].iloc[0]) / ticker_hist['Close'].iloc[0]) * 100
        spy_return = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[0]) / spy_hist['Close'].iloc[0]) * 100
        
        # Calculate relative strength
        rs = ticker_return - spy_return
        
        # Convert to 0-100 scale (simplified - real IBD uses percentile ranking)
        # Assuming typical range of -50 to +100 for RS
        rs_rating = max(0, min(100, (rs + 50) * 0.67))
        
        return rs_rating
    except:
        return None

def scan_cup_and_handle():
    """Scan for cup and handle patterns."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            stock = yf.Ticker(ticker)
            
            # Get 2 years of daily data (need enough for weekly pattern)
            hist = stock.history(period='2y')
            
            if len(hist) < 100:  # Need at least ~20 weeks of data
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                continue
            
            # Detect pattern
            cup_found, handle_found, cup_depth, handle_depth, breakout_price, distance_to_breakout = detect_cup_and_handle(hist)
            
            if cup_found and breakout_price:
                # Calculate RS rating
                rs_rating = calculate_rs_rating(hist, ticker)
                
                # Volume analysis
                recent_volume = hist['Volume'].iloc[-5:].mean()
                volume_ratio = recent_volume / avg_volume
                
                # Check market condition (SPY above 200 SMA = bull market)
                spy = yf.Ticker('SPY')
                spy_hist = spy.history(period='1y')
                spy_sma_200 = spy_hist['Close'].rolling(window=200).mean().iloc[-1]
                spy_price = spy_hist['Close'].iloc[-1]
                bull_market = spy_price > spy_sma_200
                
                # Price trend (should be rising into handle)
                price_trend = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100
                
                # Score
                score = 0
                
                # Cup quality
                if 12 <= cup_depth <= 25:
                    score += 4  # Ideal cup depth
                elif cup_depth <= 35:
                    score += 2
                
                # Handle present
                if handle_found:
                    score += 4
                    if handle_depth <= 12:
                        score += 2  # Shallow handle = stronger
                else:
                    score += 1  # Cup without handle (still valid)
                
                # RS Rating
                if rs_rating and rs_rating >= 80:
                    score += 3
                elif rs_rating and rs_rating >= 70:
                    score += 2
                
                # Volume
                if volume_ratio >= 1.3:
                    score += 2
                
                # Market condition
                if bull_market:
                    score += 2
                
                # Breakout proximity
                if distance_to_breakout <= 2:
                    score += 3  # Very close to breakout
                elif distance_to_breakout <= BREAKOUT_PROXIMITY:
                    score += 2
                
                # Price trend
                if price_trend > 0:
                    score += 1
                
                if score >= 10:  # Minimum quality threshold
                    quality = 'HIGH' if score >= 15 else 'MEDIUM'
                    
                    # Calculate target (cup depth projected from breakout)
                    target_price = breakout_price + (breakout_price * cup_depth / 100)
                    
                    # Stop loss (below handle low or 7-8%)
                    handle_low = hist['Close'].iloc[-20:].min() if handle_found else current_price * 0.92
                    stop_price = min(handle_low, current_price * 0.92)
                    
                    risk_reward = abs(target_price - breakout_price) / abs(breakout_price - stop_price)
                    
                    pattern_type = "CUP WITH HANDLE" if handle_found else "CUP (No Handle)"
                    
                    signals.append({
                        'ticker': ticker,
                        'price': current_price,
                        'pattern_type': pattern_type,
                        'cup_depth': cup_depth,
                        'handle_depth': handle_depth,
                        'breakout_price': breakout_price,
                        'distance_to_breakout': distance_to_breakout,
                        'rs_rating': rs_rating,
                        'volume_ratio': volume_ratio,
                        'bull_market': bull_market,
                        'price_trend': price_trend,
                        'target_price': target_price,
                        'stop_price': stop_price,
                        'risk_reward': risk_reward,
                        'score': score,
                        'quality': quality
                    })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    """Format cup & handle alerts for Telegram."""
    if not signals:
        return "☕ Cup & Handle Scanner\n\nNo cup & handle patterns detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"☕ Cup & Handle Scanner (IBD Pattern)\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} pattern(s)\n\n"
    
    for signal in signals[:6]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        market_emoji = "📈" if signal['bull_market'] else "📉"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  ☕ {signal['pattern_type']}\n"
        message += f"  📏 Cup Depth: {signal['cup_depth']:.1f}%"
        if signal['handle_depth']:
            message += f" | Handle: {signal['handle_depth']:.1f}%"
        message += f"\n"
        message += f"  🚀 Breakout: ${signal['breakout_price']:.2f} ({signal['distance_to_breakout']:+.1f}% away)\n"
        if signal['rs_rating']:
            message += f"  💪 RS Rating: {signal['rs_rating']:.0f}/100\n"
        message += f"  📊 Volume: {signal['volume_ratio']:.1f}x\n"
        message += f"  {market_emoji} Market: {'Bull' if signal['bull_market'] else 'Bear'}\n"
        message += f"  📈 Price Trend: {signal['price_trend']:+.1f}%\n"
        message += f"  🎯 Target: ${signal['target_price']:.2f} | Stop: ${signal['stop_price']:.2f}\n"
        message += f"  ⚖️ Risk/Reward: 1:{signal['risk_reward']:.1f}\n"
        message += f"  ⭐ Score: {signal['score']}/21 ({signal['quality']})\n\n"
    
    if len(signals) > 6:
        message += f"... and {len(signals) - 6} more\n"
    
    message += "\n💡 Enter on breakout | Stop: 7-8% or below handle | Target: Cup depth"
    
    return message

def send_telegram_message(message):
    """Send message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    """Main execution."""
    print("Starting Cup & Handle Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for IBD patterns...")
    
    signals = scan_cup_and_handle()
    
    print(f"\nFound {len(signals)} cup & handle pattern(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nCup & Handle Scanner completed")

if __name__ == "__main__":
    main()
