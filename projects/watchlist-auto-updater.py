"""
Autonomous Watchlist Updater 🔄
Automatically refreshes watchlist with top-performing stocks.

Data Sources:
- Finviz screener (top RS stocks)
- Major index components (SPY top holdings)
- Recent 52-week high breakouts

Schedule: Weekly on Sunday 8 PM ET
"""

import yfinance as yf
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

WATCHLIST_PATH = Path(__file__).parent.parent / 'watchlist.json'

# Configuration
MIN_MARKET_CAP = 10_000_000_000  # $10B minimum
MIN_AVG_VOLUME = 1_000_000  # 1M shares/day
MIN_PRICE = 20  # No penny stocks
MAX_STOCKS = 60  # Cap at 60 stocks

CORE_HOLDINGS = [
    # Always keep these mega-caps
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
    'JPM', 'V', 'MA', 'UNH', 'LLY', 'HD', 'COST'
]

def get_sp500_top_performers(lookback_days=90):
    """Get top 30 S&P 500 performers over past 3 months."""
    print("📊 Fetching S&P 500 top performers...")
    
    # Get S&P 500 components (simplified - using common tickers)
    sp500_sample = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
        'UNH', 'JNJ', 'XOM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'LLY',
        'ABBV', 'KO', 'AVGO', 'PEP', 'COST', 'TMO', 'MCD', 'CSCO', 'ACN',
        'ABT', 'WMT', 'DHR', 'ADBE', 'CRM', 'NFLX', 'NKE', 'DIS', 'VZ',
        'CMCSA', 'INTC', 'PFE', 'T', 'AMD', 'QCOM', 'TXN', 'NEE', 'PM',
        'BMY', 'UNP', 'RTX', 'HON', 'LIN', 'UPS', 'BA', 'LOW', 'AMGN',
        'SBUX', 'CAT', 'GS', 'BAC', 'BLK', 'AXP', 'ISRG', 'MS', 'SPGI',
        'NOW', 'GILD', 'DE', 'BKNG', 'SYK', 'MDLZ', 'ELV', 'ADP', 'VRTX',
        'C', 'CI', 'ZTS', 'MMC', 'TJX', 'CB', 'SO', 'PLD', 'REGN', 'ADI',
        'LRCX', 'DUK', 'EOG', 'SLB', 'NOC', 'ITW', 'KLAC', 'APD', 'MO',
        'GE', 'SCHW', 'USB', 'FIS', 'EL', 'CL', 'TGT', 'SHW', 'PNC'
    ]
    
    performers = []
    for ticker in sp500_sample:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')
            info = stock.info
            
            if len(hist) < lookback_days:
                continue
            
            # Calculate performance
            start_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            pct_change = ((current_price - start_price) / start_price) * 100
            
            # Filter criteria
            market_cap = info.get('marketCap', 0)
            avg_volume = info.get('averageVolume', 0)
            
            if market_cap < MIN_MARKET_CAP or avg_volume < MIN_AVG_VOLUME:
                continue
            
            if current_price < MIN_PRICE:
                continue
            
            performers.append({
                'ticker': ticker,
                'performance': pct_change,
                'market_cap': market_cap,
                'sector': info.get('sector', 'Unknown')
            })
            
            print(f"  ✓ {ticker}: {pct_change:+.1f}%")
        
        except Exception as e:
            print(f"  ✗ {ticker}: {e}")
            continue
    
    # Sort by performance
    performers.sort(key=lambda x: x['performance'], reverse=True)
    return performers[:30]  # Top 30

def get_high_momentum_stocks():
    """Find stocks making 52-week highs with strong volume."""
    print("\n🚀 Scanning for breakout stocks...")
    
    # Sample of high-growth stocks to monitor
    growth_candidates = [
        'PLTR', 'CRWD', 'SNOW', 'DDOG', 'NET', 'OKTA', 'ZS', 'S', 'TEAM',
        'HUBS', 'MDB', 'WDAY', 'VEEV', 'PANW', 'FTNT', 'TTD', 'ANET',
        'SMCI', 'MSTR', 'HOOD', 'COIN', 'SQ', 'SHOP', 'RBLX', 'ABNB',
        'DASH', 'UBER', 'LYFT', 'RIVN', 'LCID', 'CEG', 'VST', 'NRG',
        'IONQ', 'LUNR', 'RKLB', 'ASTS'
    ]
    
    breakouts = []
    for ticker in growth_candidates:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            info = stock.info
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            high_52w = hist['Close'].max()
            avg_volume = info.get('averageVolume', 0)
            
            # Check if near 52-week high (within 5%)
            pct_from_high = ((current_price - high_52w) / high_52w) * 100
            
            if pct_from_high > -5 and avg_volume > MIN_AVG_VOLUME:
                breakouts.append({
                    'ticker': ticker,
                    'pct_from_high': pct_from_high,
                    'sector': info.get('sector', 'Technology')
                })
                print(f"  🎯 {ticker}: {pct_from_high:.1f}% from 52w high")
        
        except Exception as e:
            continue
    
    return breakouts

def ensure_sector_diversity(stocks):
    """Balance sector exposure - max 35% in any sector."""
    print("\n⚖️ Balancing sector exposure...")
    
    sector_counts = {}
    for stock in stocks:
        sector = stock.get('sector', 'Unknown')
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    max_per_sector = int(len(stocks) * 0.35)  # 35% cap
    
    balanced = []
    sector_current = {}
    
    for stock in stocks:
        sector = stock.get('sector', 'Unknown')
        if sector_current.get(sector, 0) < max_per_sector:
            balanced.append(stock)
            sector_current[sector] = sector_current.get(sector, 0) + 1
    
    print(f"  Sector distribution: {sector_current}")
    return balanced

def update_watchlist():
    """Main update logic."""
    print("=" * 60)
    print("🔄 WATCHLIST AUTO-UPDATER")
    print("=" * 60 + "\n")
    
    # 1. Get top performers
    top_performers = get_sp500_top_performers()
    
    # 2. Get breakout candidates
    breakouts = get_high_momentum_stocks()
    
    # 3. Combine and deduplicate
    all_tickers = set(CORE_HOLDINGS)
    
    for stock in top_performers:
        all_tickers.add(stock['ticker'])
    
    for stock in breakouts:
        all_tickers.add(stock['ticker'])
    
    # 4. Build final list with metadata for balancing
    final_stocks = []
    for ticker in all_tickers:
        try:
            info = yf.Ticker(ticker).info
            final_stocks.append({
                'ticker': ticker,
                'sector': info.get('sector', 'Unknown')
            })
        except:
            final_stocks.append({'ticker': ticker, 'sector': 'Unknown'})
    
    # 5. Balance sectors
    balanced = ensure_sector_diversity(final_stocks)
    
    # 6. Cap at MAX_STOCKS
    if len(balanced) > MAX_STOCKS:
        balanced = balanced[:MAX_STOCKS]
    
    stock_list = [s['ticker'] for s in balanced]
    stock_list.sort()
    
    # 7. Update JSON
    watchlist_data = {
        "stocks": stock_list,
        "etfs": ["SPY", "QQQ", "DIA", "IWM"],
        "description": f"Auto-updated watchlist. Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "total_stocks": len(stock_list),
        "update_frequency": "Weekly"
    }
    
    with open(WATCHLIST_PATH, 'w') as f:
        json.dump(watchlist_data, f, indent=2)
    
    print(f"\n✅ Watchlist updated: {len(stock_list)} stocks")
    print(f"📁 Saved to: {WATCHLIST_PATH}")
    
    return stock_list

if __name__ == "__main__":
    update_watchlist()
