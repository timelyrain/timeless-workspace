"""
Sector Relative Strength Momentum Scanner 🚀
IBD-style RS rating system (stock vs SPY over 52 weeks).

Filters for RS > 90 percentile + stock in top 3 performing sectors.
This is the institutional playbook - buy the strongest in the strongest sectors.

Schedule: Daily 4 PM ET (after market close)
"""

import yfinance as yf
import requests
import os
import numpy as np
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
    'TSLA', 'TSM', 'UNH', 'V', 'WMT', 'ZS',
    'SPY', 'QQQ', 'IWM', 'DIA', 'TLT'
]

SECTOR_ETFS = {
    'Technology': 'XLK',
    'Financials': 'XLF',
    'Healthcare': 'XLV',
    'Energy': 'XLE',
    'Consumer Disc': 'XLY',
    'Consumer Staples': 'XLP',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Utilities': 'XLU',
    'Communication': 'XLC'
}

MIN_RS_RATING = 90  # Top 10% RS
RS_PERIOD = 252  # 252 trading days (~1 year)

def calculate_rs_rating(stock_returns, spy_returns, watchlist_returns):
    """Calculate IBD-style RS rating (0-99)."""
    # Stock vs SPY performance
    stock_vs_spy = stock_returns[-RS_PERIOD:].sum() - spy_returns[-RS_PERIOD:].sum()
    
    # Rank against all watchlist stocks
    all_vs_spy = [r[-RS_PERIOD:].sum() - spy_returns[-RS_PERIOD:].sum() for r in watchlist_returns]
    all_vs_spy.sort()
    
    # Percentile rank
    rank_position = sum(1 for x in all_vs_spy if x < stock_vs_spy)
    rs_rating = (rank_position / len(all_vs_spy)) * 100
    
    return rs_rating, stock_vs_spy

def scan_sector_momentum():
    signals = []
    
    # Get SPY data
    spy = yf.Ticker('SPY')
    spy_hist = spy.history(period='1y')
    spy_returns = spy_hist['Close'].pct_change()
    
    # Get sector performance
    sector_performance = {}
    for sector_name, etf in SECTOR_ETFS.items():
        try:
            sector = yf.Ticker(etf)
            sector_hist = sector.history(period='3mo')
            if not sector_hist.empty:
                perf = ((sector_hist['Close'].iloc[-1] - sector_hist['Close'].iloc[0]) / 
                        sector_hist['Close'].iloc[0]) * 100
                sector_performance[sector_name] = perf
        except:
            continue
    
    # Top 3 sectors
    top_sectors = sorted(sector_performance.items(), key=lambda x: x[1], reverse=True)[:3]
    top_sector_names = [s[0] for s in top_sectors]
    
    # Calculate RS for all stocks first (for percentile ranking)
    all_returns = []
    for ticker in WATCHLIST:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            if not hist.empty and len(hist) >= RS_PERIOD:
                returns = hist['Close'].pct_change()
                all_returns.append(returns)
        except:
            continue
    
    # Now scan each stock
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            info = stock.info
            
            if hist.empty or len(hist) < RS_PERIOD:
                continue
            
            current_price = hist['Close'].iloc[-1]
            returns = hist['Close'].pct_change()
            
            # Calculate RS rating
            rs_rating, stock_vs_spy_pct = calculate_rs_rating(returns, spy_returns, all_returns)
            
            if rs_rating < MIN_RS_RATING:
                continue
            
            # Get sector
            sector = info.get('sector', 'Unknown')
            
            # Check if in top 3 sectors
            is_top_sector = any(top in sector for top in top_sector_names)
            
            # Score
            score = 0
            if rs_rating >= 95:
                score += 5
            elif rs_rating >= 90:
                score += 3
            
            if is_top_sector:
                score += 3
            
            if stock_vs_spy_pct > 50:  # Massively outperforming
                score += 2
            
            if score >= 5:
                quality = 'HIGH' if score >= 8 else 'MEDIUM'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'rs_rating': rs_rating,
                    'outperformance_pct': stock_vs_spy_pct,
                    'sector': sector,
                    'is_top_sector': is_top_sector,
                    'score': score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals, top_sectors

def format_alert_message(signals, top_sectors):
    if not signals:
        return "🚀 Sector RS Momentum Scanner\n\nNo RS > 90 setups in top sectors."
    
    signals = sorted(signals, key=lambda x: x['rs_rating'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🚀 Sector RS Momentum Scanner\n⏰ {timestamp}\n\n"
    message += f"🔥 Top 3 Sectors:\n"
    for i, (sector, perf) in enumerate(top_sectors, 1):
        message += f"  {i}. {sector}: {perf:+.1f}%\n"
    
    message += f"\n📊 Found {len(signals)} high RS stock(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        sector_flag = " [TOP SECTOR]" if signal['is_top_sector'] else ""
        
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}{sector_flag}\n"
        message += f"  📈 RS Rating: {signal['rs_rating']:.0f}/99 (Top {100-signal['rs_rating']:.0f}%)\n"
        message += f"  💪 Outperformance: {signal['outperformance_pct']:+.1f}% vs SPY\n"
        message += f"  🏢 Sector: {signal['sector']}\n"
        message += f"  ⭐ Score: {signal['score']}/10 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Buy the strongest stocks in the strongest sectors"
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Sector RS Momentum Scanner...")
    signals, top_sectors = scan_sector_momentum()
    print(f"Found {len(signals)} high RS stock(s)")
    message = format_alert_message(signals, top_sectors)
    print(f"\n{message}")
    send_telegram_message(message)
    print("Sector RS Momentum Scanner completed")

if __name__ == "__main__":
    main()
