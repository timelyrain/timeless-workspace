"""
Accumulation/Distribution Scanner (Wyckoff Method) 📦
Detects institutional accumulation/distribution through volume-price analysis.

Key Features:
- On-Balance Volume (OBV) analysis
- Accumulation/Distribution Line (A/D Line)
- Volume-weighted divergences
- Wyckoff phases: Accumulation, Markup, Distribution, Markdown
- Institutional footprint detection

Usage Tips:
1. Accumulation phase: Price flat/down + volume increasing = institutions buying
2. Distribution phase: Price flat/up + volume increasing = institutions selling
3. Best signal: Price making lower lows but OBV making higher lows (bullish divergence)
4. Confirm with 4-8 week period (institutions need time to build positions)
5. Enter on markup phase exit from accumulation range

Strategy: Follow institutional footprints - they position 4-8 weeks early.
Schedule: Daily 4:30 PM ET (after market close for clean data)
"""

import yfinance as yf
import requests
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_DIVERGENCE')
CHAT_ID = os.getenv('CHAT_ID')

WATCHLIST = load_watchlist()

# === SETTINGS ===
ACCUMULATION_PERIOD = 40  # 40 days (~8 weeks) for accumulation detection
MIN_VOLUME_INCREASE = 1.3  # 30% volume increase during accumulation
MAX_PRICE_CHANGE = 5.0  # Price stays within 5% during accumulation
MIN_OBV_DIVERGENCE = 10.0  # OBV divergence threshold (%)
MIN_PRICE = 20.0
MIN_AVG_VOLUME = 500000

def calculate_obv(hist):
    """Calculate On-Balance Volume."""
    obv = [0]
    for i in range(1, len(hist)):
        if hist['Close'].iloc[i] > hist['Close'].iloc[i-1]:
            obv.append(obv[-1] + hist['Volume'].iloc[i])
        elif hist['Close'].iloc[i] < hist['Close'].iloc[i-1]:
            obv.append(obv[-1] - hist['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    
    return pd.Series(obv, index=hist.index)

def calculate_ad_line(hist):
    """Calculate Accumulation/Distribution Line."""
    clv = ((hist['Close'] - hist['Low']) - (hist['High'] - hist['Close'])) / (hist['High'] - hist['Low'])
    clv = clv.fillna(0)  # Handle division by zero
    ad_line = (clv * hist['Volume']).cumsum()
    return ad_line

def detect_phase(hist, period=ACCUMULATION_PERIOD):
    """
    Detect Wyckoff phase: Accumulation, Markup, Distribution, Markdown.
    Returns: (phase, confidence_score)
    """
    recent = hist.tail(period)
    
    # Price metrics
    price_change = ((recent['Close'].iloc[-1] - recent['Close'].iloc[0]) / recent['Close'].iloc[0]) * 100
    price_high = recent['High'].max()
    price_low = recent['Low'].min()
    price_range = ((price_high - price_low) / price_low) * 100
    
    # Volume metrics
    avg_volume_first_half = recent['Volume'].iloc[:period//2].mean()
    avg_volume_second_half = recent['Volume'].iloc[period//2:].mean()
    volume_increase = ((avg_volume_second_half - avg_volume_first_half) / avg_volume_first_half) * 100
    
    # OBV and A/D Line
    obv = calculate_obv(hist)
    ad_line = calculate_ad_line(hist)
    
    obv_recent = obv.tail(period)
    ad_recent = ad_line.tail(period)
    
    obv_change = ((obv_recent.iloc[-1] - obv_recent.iloc[0]) / abs(obv_recent.iloc[0])) * 100 if obv_recent.iloc[0] != 0 else 0
    ad_change = ((ad_recent.iloc[-1] - ad_recent.iloc[0]) / abs(ad_recent.iloc[0])) * 100 if ad_recent.iloc[0] != 0 else 0
    
    # Phase detection logic
    score = 0
    phase = "UNKNOWN"
    
    # ACCUMULATION: Price flat/down, volume up, OBV/AD rising
    if (price_range <= MAX_PRICE_CHANGE and 
        volume_increase >= (MIN_VOLUME_INCREASE - 1) * 100 and
        obv_change > 0 and ad_change > 0):
        phase = "ACCUMULATION"
        score = 5
        if price_change < 0:  # Price down while volume up = strong accumulation
            score += 3
        if volume_increase >= 50:
            score += 2
    
    # MARKUP: Price rising, volume declining, OBV/AD still positive
    elif (price_change > 10 and 
          volume_increase < 0 and
          obv_change > 0):
        phase = "MARKUP"
        score = 4
        if price_change > 20:
            score += 2
    
    # DISTRIBUTION: Price flat/up, volume up, OBV/AD falling
    elif (price_range <= MAX_PRICE_CHANGE * 1.5 and
          volume_increase >= (MIN_VOLUME_INCREASE - 1) * 100 and
          obv_change < 0 and ad_change < 0):
        phase = "DISTRIBUTION"
        score = 5
        if price_change > 0:  # Price up while OBV down = distribution
            score += 3
    
    # MARKDOWN: Price falling, volume declining
    elif price_change < -10:
        phase = "MARKDOWN"
        score = 3
    
    return phase, score, price_change, volume_increase, obv_change, ad_change

def detect_divergence(hist, period=ACCUMULATION_PERIOD):
    """Detect bullish/bearish divergences between price and OBV."""
    recent = hist.tail(period)
    obv = calculate_obv(hist).tail(period)
    
    # Price trend (linear regression)
    price_x = np.arange(len(recent))
    price_y = recent['Close'].values
    price_slope = np.polyfit(price_x, price_y, 1)[0]
    
    # OBV trend
    obv_y = obv.values
    obv_slope = np.polyfit(price_x, obv_y, 1)[0]
    
    # Normalize slopes for comparison
    price_slope_pct = (price_slope / price_y[0]) * 100 * len(price_x)
    obv_slope_pct = (obv_slope / abs(obv_y[0])) * 100 * len(price_x) if obv_y[0] != 0 else 0
    
    # Detect divergence
    divergence_type = None
    divergence_strength = 0
    
    if price_slope_pct < -5 and obv_slope_pct > 5:  # Price down, OBV up
        divergence_type = "BULLISH"
        divergence_strength = abs(obv_slope_pct - price_slope_pct)
    elif price_slope_pct > 5 and obv_slope_pct < -5:  # Price up, OBV down
        divergence_type = "BEARISH"
        divergence_strength = abs(price_slope_pct - obv_slope_pct)
    
    return divergence_type, divergence_strength

def scan_accumulation_distribution():
    """Scan for accumulation/distribution patterns."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            
            if hist.empty or len(hist) < ACCUMULATION_PERIOD * 2:
                continue
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            if current_price < MIN_PRICE or avg_volume < MIN_AVG_VOLUME:
                continue
            
            # Detect phase
            phase, phase_score, price_chg, vol_inc, obv_chg, ad_chg = detect_phase(hist, ACCUMULATION_PERIOD)
            
            # Detect divergence
            div_type, div_strength = detect_divergence(hist, ACCUMULATION_PERIOD)
            
            # Calculate overall score
            total_score = phase_score
            
            if div_type == "BULLISH":
                total_score += 4
            elif div_type == "BEARISH":
                total_score -= 2  # Flag bearish divergence as warning
            
            if div_strength >= MIN_OBV_DIVERGENCE:
                total_score += 2
            
            # Only alert on accumulation or strong divergence
            if phase == "ACCUMULATION" or (div_type == "BULLISH" and div_strength >= MIN_OBV_DIVERGENCE):
                quality = 'HIGH' if total_score >= 10 else 'MEDIUM' if total_score >= 7 else 'LOW'
                
                # Trade recommendation
                if phase == "ACCUMULATION":
                    recommendation = "BUY - Institutions accumulating"
                elif phase == "MARKUP":
                    recommendation = "HOLD - Markup phase continuing"
                elif phase == "DISTRIBUTION":
                    recommendation = "SELL - Institutions distributing"
                else:
                    recommendation = "WATCH - Divergence detected"
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'phase': phase,
                    'price_change': price_chg,
                    'volume_increase': vol_inc,
                    'obv_change': obv_chg,
                    'ad_change': ad_chg,
                    'divergence_type': div_type if div_type else "NONE",
                    'divergence_strength': div_strength,
                    'recommendation': recommendation,
                    'score': total_score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    """Format alerts for Telegram."""
    if not signals:
        return "📦 Accumulation/Distribution Scanner\n\nNo institutional accumulation/distribution detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"📦 Accumulation/Distribution Scanner (Wyckoff)\n⏰ {timestamp}\n"
    message += f"🔍 Found {len(signals)} institutional footprint(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡" if signal['quality'] == 'MEDIUM' else "⚪"
        
        phase_emoji = {
            'ACCUMULATION': '📦',
            'MARKUP': '📈',
            'DISTRIBUTION': '📤',
            'MARKDOWN': '📉'
        }.get(signal['phase'], '❓')
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  {phase_emoji} Phase: {signal['phase']}\n"
        message += f"  📊 Price Change: {signal['price_change']:+.1f}%\n"
        message += f"  📈 Volume Increase: {signal['volume_increase']:+.1f}%\n"
        message += f"  💹 OBV Change: {signal['obv_change']:+.1f}%\n"
        message += f"  💰 A/D Line: {signal['ad_change']:+.1f}%\n"
        
        if signal['divergence_type'] != "NONE":
            div_emoji = "🔺" if signal['divergence_type'] == "BULLISH" else "🔻"
            message += f"  {div_emoji} Divergence: {signal['divergence_type']} (strength: {signal['divergence_strength']:.1f})\n"
        
        message += f"  💡 {signal['recommendation']}\n"
        message += f"  ⭐ Score: {signal['score']}/15 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Accumulation = Buy zone | Distribution = Sell zone"
    
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
    print("Starting Accumulation/Distribution Scanner...")
    print(f"Scanning {len(WATCHLIST)} stocks for institutional footprints...")
    
    signals = scan_accumulation_distribution()
    
    print(f"\nFound {len(signals)} institutional pattern(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nAccumulation/Distribution Scanner completed")

if __name__ == "__main__":
    main()
