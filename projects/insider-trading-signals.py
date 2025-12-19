"""
Insider Trading Cluster Signals 👔
Monitors SEC Form 4 filings for significant insider buying patterns using FMP API.

Key Features:
- Tracks C-suite insider purchases (CEO, CFO, President, Directors)
- Detects insider buying clusters (2+ insiders within 30 days)
- Minimum transaction size filtering ($100k+)
- Aggregate buying momentum scoring
- Distinguishes purchases vs. sales (only purchases signal confidence)

Usage Tips:
1. Insider clusters (2+ execs buying) = strong bullish signal
2. C-suite buys are more meaningful than board member buys
3. Ignore sales (insiders sell for many reasons - diversification, taxes, etc.)
4. Large purchases ($500k+) by CEO/CFO = highest conviction
5. Best signal: cluster buying + stock near 52W low

Strategy: Insiders know the business 3-6 months ahead. Follow the smart money.
Schedule: Daily 6 PM ET (after market close, after SEC filings submitted).

Note: Uses FMP /insider-trading API. Requires FMP_API_KEY in .env file.
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
FMP_API_KEY = os.getenv('FMP_API_KEY')

WATCHLIST = load_watchlist()

# === SETTINGS ===
MIN_TRANSACTION_VALUE = 100_000  # $100k minimum purchase
STRONG_TRANSACTION_VALUE = 500_000  # $500k+ = high conviction
CLUSTER_DAYS = 30  # Look for 2+ insiders buying within 30 days
MIN_INSIDERS_FOR_CLUSTER = 2  # Minimum insiders for cluster signal
C_SUITE_TITLES = ['CEO', 'CFO', 'President', 'Chief Executive Officer', 'Chief Financial Officer']
MIN_PRICE = 5.0  # Avoid penny stocks

def get_insider_trades(ticker, days=90):
    """Fetch insider trades from FMP API for the last N days."""
    url = f"https://financialmodelingprep.com/stable/insider-trading?symbol={ticker}&page=0&apikey={FMP_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data or not isinstance(data, list):
            return []
        
        # Filter to recent purchases only
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_purchases = []
        
        for trade in data:
            filing_date = datetime.strptime(trade.get('filingDate', ''), '%Y-%m-%d %H:%M:%S')
            if filing_date < cutoff_date:
                continue
            
            # Only purchases (acquisitionOrDisposition = 'A')
            if trade.get('acquistionOrDisposition') != 'A':
                continue
            
            securities_transacted = float(trade.get('securitiesTransacted', 0))
            price = float(trade.get('price', 0))
            transaction_value = securities_transacted * price
            
            if transaction_value >= MIN_TRANSACTION_VALUE:
                recent_purchases.append({
                    'insider_name': trade.get('reportingName', 'Unknown'),
                    'title': trade.get('typeOfOwner', 'Unknown'),
                    'transaction_date': trade.get('transactionDate', ''),
                    'filing_date': filing_date,
                    'shares': securities_transacted,
                    'price': price,
                    'value': transaction_value
                })
        
        return recent_purchases
    
    except Exception as e:
        print(f"FMP error for {ticker}: {e}")
        return []

def detect_insider_cluster(trades):
    """Detect if there's a cluster of insider buying (2+ insiders within 30 days)."""
    if len(trades) < MIN_INSIDERS_FOR_CLUSTER:
        return False, 0, []
    
    # Sort by filing date
    trades_sorted = sorted(trades, key=lambda x: x['filing_date'], reverse=True)
    
    # Check for cluster within CLUSTER_DAYS
    clusters = []
    for i in range(len(trades_sorted)):
        cluster = [trades_sorted[i]]
        for j in range(i + 1, len(trades_sorted)):
            days_diff = (trades_sorted[i]['filing_date'] - trades_sorted[j]['filing_date']).days
            if days_diff <= CLUSTER_DAYS:
                cluster.append(trades_sorted[j])
        
        if len(cluster) >= MIN_INSIDERS_FOR_CLUSTER:
            clusters.append(cluster)
    
    if not clusters:
        return False, 0, []
    
    # Get the most recent cluster
    best_cluster = clusters[0]
    total_value = sum(t['value'] for t in best_cluster)
    
    return True, total_value, best_cluster

def scan_insider_trading():
    """Scan for insider trading cluster signals."""
    signals = []
    
    for ticker in WATCHLIST:
        try:
            print(f"Scanning {ticker}...")
            
            # Get current price and history
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            
            if hist.empty:
                continue
            
            current_price = hist['Close'].iloc[-1]
            if current_price < MIN_PRICE:
                continue
            
            # Get insider trades
            trades = get_insider_trades(ticker, days=90)
            
            if not trades:
                continue
            
            # Detect cluster
            is_cluster, total_value, cluster_trades = detect_insider_cluster(trades)
            
            if not is_cluster:
                continue
            
            # Calculate score
            score = 0
            
            # Cluster size
            if len(cluster_trades) >= 4:
                score += 5
            elif len(cluster_trades) >= 3:
                score += 4
            elif len(cluster_trades) >= 2:
                score += 3
            
            # Total value
            if total_value >= 5_000_000:  # $5M+
                score += 4
            elif total_value >= 1_000_000:  # $1M+
                score += 3
            elif total_value >= 500_000:  # $500k+
                score += 2
            
            # C-suite involvement
            c_suite_count = sum(1 for t in cluster_trades if any(title in t['title'] for title in C_SUITE_TITLES))
            if c_suite_count >= 2:
                score += 3
            elif c_suite_count >= 1:
                score += 2
            
            # Price relative to 52W high (buying at discount = stronger signal)
            high_52w = hist['High'].max()
            distance_from_high = ((high_52w - current_price) / high_52w) * 100
            if distance_from_high > 30:
                score += 3
            elif distance_from_high > 20:
                score += 2
            elif distance_from_high > 10:
                score += 1
            
            if score >= 6:
                quality = 'HIGH' if score >= 10 else 'MEDIUM'
                
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'insider_count': len(cluster_trades),
                    'c_suite_count': c_suite_count,
                    'total_value': total_value,
                    'distance_from_high': distance_from_high,
                    'recent_trades': cluster_trades[:3],  # Top 3 for display
                    'score': score,
                    'quality': quality
                })
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return signals

def format_alert_message(signals):
    if not signals:
        return None
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"👔 Insider Trading Cluster Signals\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} insider cluster(s)\n\n"
    
    for signal in signals[:8]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        message += f"{quality_emoji} {signal['ticker']} - ${signal['price']:.2f}\n"
        message += f"  👥 Insiders Buying: {signal['insider_count']} ({signal['c_suite_count']} C-suite)\n"
        message += f"  💰 Total Cluster Value: ${signal['total_value']/1_000_000:.2f}M\n"
        message += f"  📉 Below 52W High: {signal['distance_from_high']:.1f}%\n"
        
        # Show top 3 trades
        for i, trade in enumerate(signal['recent_trades'][:2], 1):
            message += f"  #{i}: {trade['title']} bought ${trade['value']/1_000:.0f}k on {trade['transaction_date']}\n"
        
        message += f"  ⭐ Score: {signal['score']}/15 ({signal['quality']})\n\n"
    
    if len(signals) > 8:
        message += f"... and {len(signals) - 8} more\n"
    
    message += "\n💡 Insider clusters = Management confidence. They know 3-6 months ahead."
    
    return message

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Insider Trading Cluster Scanner...")
    signals = scan_insider_trading()
    print(f"Found {len(signals)} insider cluster signal(s)")
    
    message = format_alert_message(signals)
    
    if message:
        print(f"\n{message}")
        send_telegram_message(message)
    else:
        print("\nNo insider clusters detected. Skipping Telegram alert.")
    
    print("Insider Trading Scanner completed")

if __name__ == "__main__":
    main()
