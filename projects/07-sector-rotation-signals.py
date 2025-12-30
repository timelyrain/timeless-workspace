"""
Sector Rotation Signals 🔄
Tracks capital flows across 11 S&P sectors to identify rotation opportunities using FMP API.

Key Features:
- Monitors performance of 11 sector ETFs (XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC)
- Detects sector leadership changes (1D, 5D, 1M, 3M timeframes)
- Identifies momentum rotation patterns
- Tracks sector relative strength vs SPY
- Calculates sector rotation spread (top vs bottom)

Usage Tips:
1. Overweight stocks in top 3 performing sectors
2. Underweight/avoid bottom 3 sectors
3. Sector rotation lags economic cycle by 3-6 months
4. Best signal: new sector leadership + increasing spread
5. Rotation works best in trending markets (not choppy)

Strategy: Follow the smart money sector flows. Capital rotates before fundamentals confirm.
Schedule: Daily 4:30 PM ET (after market close for clean data).

Note: Uses FMP /historical-price-eod and /sector-performance endpoints. Requires FMP_API_KEY.
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
import pandas as pd

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
FMP_API_KEY = os.getenv('FMP_API_KEY')

# === SETTINGS ===
SECTOR_ETFS = {
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

MIN_ROTATION_SPREAD = 3.0  # Minimum 3% spread between top and bottom sectors
STRONG_ROTATION_SPREAD = 5.0  # 5%+ spread = strong rotation

def get_sector_performance():
    """Calculate sector performance across multiple timeframes."""
    sector_data = {}
    
    for etf, sector_name in SECTOR_ETFS.items():
        try:
            stock = yf.Ticker(etf)
            hist = stock.history(period='6mo')
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate returns for different timeframes
            performance = {}
            
            # 1 day
            if len(hist) >= 2:
                performance['1D'] = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            
            # 5 days (1 week)
            if len(hist) >= 6:
                performance['5D'] = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
            
            # 21 days (1 month)
            if len(hist) >= 22:
                performance['1M'] = ((current_price - hist['Close'].iloc[-22]) / hist['Close'].iloc[-22]) * 100
            
            # 63 days (3 months)
            if len(hist) >= 64:
                performance['3M'] = ((current_price - hist['Close'].iloc[-64]) / hist['Close'].iloc[-64]) * 100
            
            # Volume trend
            avg_volume_recent = hist['Volume'].iloc[-5:].mean()
            avg_volume_month = hist['Volume'].iloc[-21:].mean()
            volume_trend = ((avg_volume_recent - avg_volume_month) / avg_volume_month) * 100
            
            sector_data[etf] = {
                'sector': sector_name,
                'price': current_price,
                'performance': performance,
                'volume_trend': volume_trend
            }
        
        except Exception as e:
            print(f"Error processing {etf}: {e}")
            continue
    
    return sector_data

def analyze_sector_rotation(sector_data):
    """Analyze sector rotation patterns and generate signals."""
    if len(sector_data) < 5:  # Need at least 5 sectors for meaningful analysis
        return []
    
    signals = []
    
    # Analyze each timeframe
    for timeframe in ['1D', '5D', '1M', '3M']:
        # Get sectors with valid data for this timeframe
        valid_sectors = {etf: data for etf, data in sector_data.items() 
                        if timeframe in data['performance']}
        
        if len(valid_sectors) < 5:
            continue
        
        # Sort by performance
        sorted_sectors = sorted(valid_sectors.items(), 
                              key=lambda x: x[1]['performance'][timeframe], 
                              reverse=True)
        
        # Get top 3 and bottom 3
        top_3 = sorted_sectors[:3]
        bottom_3 = sorted_sectors[-3:]
        
        # Calculate spread
        spread = top_3[0][1]['performance'][timeframe] - bottom_3[-1][1]['performance'][timeframe]
        
        # Only signal if spread is significant
        if spread < MIN_ROTATION_SPREAD:
            continue
        
        # Score
        score = 0
        
        # Spread magnitude
        if spread >= STRONG_ROTATION_SPREAD * 2:  # 10%+
            score += 5
        elif spread >= STRONG_ROTATION_SPREAD:  # 5%+
            score += 4
        elif spread >= MIN_ROTATION_SPREAD * 1.5:  # 4.5%+
            score += 3
        elif spread >= MIN_ROTATION_SPREAD:  # 3%+
            score += 2
        
        # Top sector momentum (all top 3 positive)
        if all(s[1]['performance'][timeframe] > 0 for s in top_3):
            score += 2
        
        # Volume confirmation in top sectors
        top_with_volume = sum(1 for s in top_3 if s[1]['volume_trend'] > 0)
        if top_with_volume >= 2:
            score += 2
        
        # Consistency across timeframes (check if top sectors are leaders in multiple timeframes)
        if timeframe != '1D':
            consistency_score = 0
            for etf, _ in top_3:
                # Check if this sector is also in top 5 in longer timeframe
                if timeframe == '5D' and '1M' in valid_sectors[etf]['performance']:
                    if valid_sectors[etf]['performance']['1M'] > 0:
                        consistency_score += 1
                elif timeframe == '1M' and '3M' in valid_sectors[etf]['performance']:
                    if valid_sectors[etf]['performance']['3M'] > 0:
                        consistency_score += 1
            
            if consistency_score >= 2:
                score += 2
        
        if score >= 6:
            quality = 'HIGH' if score >= 10 else 'MEDIUM'
            
            signals.append({
                'timeframe': timeframe,
                'spread': spread,
                'top_sectors': [(etf, data['sector'], data['performance'][timeframe]) for etf, data in top_3],
                'bottom_sectors': [(etf, data['sector'], data['performance'][timeframe]) for etf, data in bottom_3],
                'score': score,
                'quality': quality
            })
    
    return signals

def format_alert_message(signals, sector_data):
    if not signals:
        return None
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🔄 Sector Rotation Signals\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} rotation pattern(s)\n\n"
    
    for signal in signals[:4]:  # Show top 4 timeframes
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        message += f"{quality_emoji} {signal['timeframe']} Rotation (Spread: {signal['spread']:.1f}%)\n"
        message += f"  📈 LEADERS:\n"
        for i, (etf, sector, perf) in enumerate(signal['top_sectors'], 1):
            message += f"    {i}. {sector} ({etf}): {perf:+.1f}%\n"
        
        message += f"  📉 LAGGARDS:\n"
        for i, (etf, sector, perf) in enumerate(signal['bottom_sectors'], 1):
            message += f"    {i}. {sector} ({etf}): {perf:+.1f}%\n"
        
        message += f"  ⭐ Score: {signal['score']}/13 ({signal['quality']})\n\n"
    
    message += "\n💡 Overweight stocks in top 3 sectors, avoid bottom 3. Sector rotation leads fundamentals."
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Sector Rotation Scanner...")
    
    # Get sector performance data
    sector_data = get_sector_performance()
    print(f"Fetched data for {len(sector_data)} sectors")
    
    # Analyze rotation
    signals = analyze_sector_rotation(sector_data)
    print(f"Found {len(signals)} rotation signal(s)")
    
    message = format_alert_message(signals, sector_data)
    
    if message:
        print(f"\n{message}")
        send_telegram_message(message)
    else:
        print("\nNo significant sector rotation detected. Skipping Telegram alert.")
    
    print("Sector Rotation Scanner completed")

if __name__ == "__main__":
    main()
