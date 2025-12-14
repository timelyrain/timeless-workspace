"""
Golden/Death Cross Scanner ✝️
Detects 50 SMA crossing 200 SMA (major algo trigger).

Key Features:
- Golden Cross: 50 SMA crosses above 200 SMA (bullish)
- Death Cross: 50 SMA crosses below 200 SMA (bearish)
- Recent crosses (within 5 days) prioritized
- Distance from cross tracked
- Volume confirmation
- Trend strength measurement

Usage Tips:
1. Wait for cross confirmation (50 SMA clearly above/below 200 SMA)
2. Best with volume spike on cross day
3. Enter on pullback to 50 SMA after golden cross
4. Stop: Below 200 SMA
5. Target: Previous high + 20-30%

Strategy: Capture institutional algo entries - $100B+ AUM use this signal.
Schedule: Daily 4 PM ET (after market close for clean signals)
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
SMA_SHORT = 50
SMA_LONG = 200
MAX_DAYS_SINCE_CROSS = 10  # Only alert if cross within 10 days
MIN_SEPARATION = 0.5  # Minimum 0.5% separation between SMAs for confirmation
MIN_VOLUME_SPIKE = 1.3  # 1.3x average volume on cross day
MIN_PRICE = 20.0
MIN_AVG_VOLUME = 500000

def calculate_sma(data, period):
    """Calculate Simple Moving Average."""
    return data['Close'].rolling(window=period).mean()

def detect_sma_cross(hist):
    """
    Detect 50/200 SMA crosses.
    Returns: (cross_type, days_since_cross, cross_price, separation_pct)
    """
    try:
        sma_50 = calculate_sma(hist, SMA_SHORT)
        sma_200 = calculate_sma(hist, SMA_LONG)
        
        # Remove NaN values
        valid_idx = ~(sma_50.isna() | sma_200.isna())
        sma_50 = sma_50[valid_idx]
        sma_200 = sma_200[valid_idx]
        hist_valid = hist[valid_idx]
        
        if len(sma_50) < 2:
            return None, None, None, None
        
        # Check for recent crosses
        cross_found = False
        cross_type = None
        days_since_cross = None
        cross_price = None
        
        for i in range(len(sma_50) - 1, max(0, len(sma_50) - MAX_DAYS_SINCE_CROSS - 1), -1):
            if i == 0:
                break
            
            # Golden Cross: 50 crosses above 200
            if sma_50.iloc[i-1] <= sma_200.iloc[i-1] and sma_50.iloc[i] > sma_200.iloc[i]:
                cross_type = "GOLDEN"
                days_since_cross = len(sma_50) - 1 - i
                cross_price = hist_valid['Close'].iloc[i]
                cross_found = True
                break
            
            # Death Cross: 50 crosses below 200
            if sma_50.iloc[i-1] >= sma_200.iloc[i-1] and sma_50.iloc[i] < sma_200.iloc[i]:
                cross_type = "DEATH"
                days_since_cross = len(sma_50) - 1 - i
                cross_price = hist_valid['Close'].iloc[i]
                cross_found = True
                break
        
        if not cross_found:
            return None, None, None, None
        
        # Calculate current separation
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]
        separation_pct = ((current_sma_50 - current_sma_200) / current_sma_200) * 100
        
        return cross_type, days_since_cross, cross_price, separation_pct
    
    except Exception as e:
        return None, None, None, None

def calculate_trend_strength(hist, sma_50, sma_200):
    """Calculate trend strength based on price position relative to SMAs."""
    try:
        current_price = hist['Close'].iloc[-1]
        
        # Above both = strong uptrend
        # Below both = strong downtrend
        if current_price > sma_50 and sma_50 > sma_200:
            strength = 10
        elif current_price > sma_50 and current_price > sma_200:
            strength = 7
        elif current_price < sma_50 and sma_50 < sma_200:
            strength = 10  # Strong downtrend
        elif current_price < sma_50 and current_price < sma_200:
            strength = 7
        else:
            strength = 5
        
        return strength
    except:
        return 5

def scan_golden_death_crosses():
    """Scan for golden/death crosses."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            stock = yf.Ticker(ticker)
            
            # Get 1 year of data (need 200+ days for 200 SMA)
            hist = stock.history(period='1y')
            
            if len(hist) < 210:  # Need at least 210 days for reliable 200 SMA
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                continue
            
            # Calculate SMAs
            sma_50 = calculate_sma(hist, SMA_SHORT)
            sma_200 = calculate_sma(hist, SMA_LONG)
            
            if sma_50.isna().iloc[-1] or sma_200.isna().iloc[-1]:
                continue
            
            # Detect crosses
            cross_type, days_since_cross, cross_price, separation_pct = detect_sma_cross(hist)
            
            if cross_type and days_since_cross is not None:
                # Volume analysis on cross day
                cross_idx = len(hist) - 1 - days_since_cross
                cross_volume = hist['Volume'].iloc[cross_idx]
                volume_ratio = cross_volume / avg_volume
                
                # Current volume
                recent_volume = hist['Volume'].iloc[-5:].mean()
                current_volume_ratio = recent_volume / avg_volume
                
                # Trend strength
                trend_strength = calculate_trend_strength(hist, sma_50.iloc[-1], sma_200.iloc[-1])
                
                # Price change since cross
                price_change_pct = ((current_price - cross_price) / cross_price) * 100
                
                # Score
                score = 0
                
                # Freshness (recent cross = higher score)
                if days_since_cross <= 2:
                    score += 4
                elif days_since_cross <= 5:
                    score += 3
                else:
                    score += 2
                
                # SMA separation (confirmation)
                if abs(separation_pct) >= 2.0:
                    score += 3
                elif abs(separation_pct) >= MIN_SEPARATION:
                    score += 2
                else:
                    score += 1
                
                # Volume confirmation
                if volume_ratio >= 2.0:
                    score += 3
                elif volume_ratio >= MIN_VOLUME_SPIKE:
                    score += 2
                
                # Sustained volume
                if current_volume_ratio >= 1.3:
                    score += 2
                
                # Trend strength
                if trend_strength >= 10:
                    score += 3
                elif trend_strength >= 7:
                    score += 2
                
                # Price follow-through
                if cross_type == "GOLDEN" and price_change_pct > 5:
                    score += 2
                elif cross_type == "DEATH" and price_change_pct < -5:
                    score += 2
                
                if score >= 8:  # Minimum quality threshold
                    quality = 'HIGH' if score >= 12 else 'MEDIUM'
                    
                    # Calculate targets
                    if cross_type == "GOLDEN":
                        target_price = current_price * 1.20  # 20% target typical
                        stop_price = sma_200.iloc[-1]
                        recommendation = "BUY - Major bullish algo signal"
                    else:  # DEATH
                        target_price = current_price * 0.80  # 20% downside
                        stop_price = sma_200.iloc[-1]
                        recommendation = "SELL/SHORT - Major bearish algo signal"
                    
                    risk_reward = abs(target_price - current_price) / abs(current_price - stop_price)
                    
                    signals.append({
                        'ticker': ticker,
                        'price': current_price,
                        'cross_type': cross_type,
                        'days_since_cross': days_since_cross,
                        'cross_price': cross_price,
                        'price_change_pct': price_change_pct,
                        'sma_50': sma_50.iloc[-1],
                        'sma_200': sma_200.iloc[-1],
                        'separation_pct': separation_pct,
                        'volume_ratio': volume_ratio,
                        'current_volume_ratio': current_volume_ratio,
                        'trend_strength': trend_strength,
                        'target_price': target_price,
                        'stop_price': stop_price,
                        'risk_reward': risk_reward,
                        'recommendation': recommendation,
                        'score': score,
                        'quality': quality
                    })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    """Format golden/death cross alerts for Telegram."""
    if not signals:
        return "✝️ Golden/Death Cross Scanner\n\nNo recent SMA crosses detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"✝️ Golden/Death Cross Scanner\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} SMA cross(es)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        cross_emoji = "🟢✝️" if signal['cross_type'] == "GOLDEN" else "🔴☠️"
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  {cross_emoji} {signal['cross_type']} CROSS ({signal['days_since_cross']} days ago)\n"
        message += f"  📈 Cross Price: ${signal['cross_price']:.2f} | Change: {signal['price_change_pct']:+.1f}%\n"
        message += f"  📊 50 SMA: ${signal['sma_50']:.2f} | 200 SMA: ${signal['sma_200']:.2f}\n"
        message += f"  📏 Separation: {signal['separation_pct']:+.1f}%\n"
        message += f"  📊 Cross Volume: {signal['volume_ratio']:.1f}x | Current: {signal['current_volume_ratio']:.1f}x\n"
        message += f"  💪 Trend Strength: {signal['trend_strength']}/10\n"
        message += f"  🎯 Target: ${signal['target_price']:.2f} | Stop: ${signal['stop_price']:.2f}\n"
        message += f"  ⚖️ Risk/Reward: 1:{signal['risk_reward']:.1f}\n"
        message += f"  💡 {signal['recommendation']}\n"
        message += f"  ⭐ Score: {signal['score']}/17 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Golden Cross = BUY | Death Cross = SELL | Stop: 200 SMA"
    
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
    print("Starting Golden/Death Cross Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for 50/200 SMA crosses...")
    
    signals = scan_golden_death_crosses()
    
    print(f"\nFound {len(signals)} SMA cross(es)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nGolden/Death Cross Scanner completed")

if __name__ == "__main__":
    main()
