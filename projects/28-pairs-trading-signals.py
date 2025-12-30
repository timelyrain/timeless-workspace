"""
Pairs Trading Scanner 🔄
Statistical arbitrage using cointegration (market-neutral hedge fund strategy).

Key Features:
- Cointegration testing (Engle-Granger method)
- Spread Z-score calculation
- Mean reversion signals
- Half-life of mean reversion
- Entry/exit thresholds

Usage Tips:
1. Market-neutral strategy (hedge against market risk)
2. Enter when Z-score >= 2.0 (spread extreme)
3. Long underperformer, short outperformer
4. Exit at Z-score = 0 (mean reversion complete)
5. Stop if spread diverges further (Z-score > 3.5)

Strategy: Hedge fund staple - 70%+ Sharpe ratio, market-neutral returns.
Schedule: Daily 3 PM ET (end of day positioning)
"""

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pytz
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import coint

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Define pair groups (historically correlated stocks)
PAIR_GROUPS = [
    # Tech Giants
    ['GOOGL', 'META', 'MSFT'],
    # Cloud/SaaS
    ['CRM', 'NOW', 'SNOW', 'TEAM'],
    # Semiconductors
    ['NVDA', 'AVGO', 'ASML', 'TSM'],
    # Payment Processors
    ['MA', 'V', 'PYPL'],
    # E-commerce
    ['SHOP', 'MELI'],
    # Cybersecurity
    ['CRWD', 'PANW', 'ZS', 'NET'],
    # Healthcare
    ['JNJ', 'PFE', 'LLY', 'ABT', 'UNH'],
    # Consumer
    ['COST', 'WMT', 'PG', 'MCD'],
    # Finance
    ['JPM', 'GS'],
    # Media/Entertainment
    ['DIS', 'NFLX'],
    # ETFs
    ['SPY', 'QQQ', 'IWM', 'DIA']
]

# === SETTINGS ===
LOOKBACK_PERIOD = 60  # 60 days for cointegration test
MIN_ZSCORE_ENTRY = 2.0  # Enter when |Z-score| >= 2.0
MAX_ZSCORE_STOP = 3.5  # Stop if spread diverges beyond 3.5
MIN_COINTEGRATION_PVALUE = 0.05  # p-value < 0.05 for statistical significance
MIN_HALFLIFE = 5  # Minimum 5 days for mean reversion
MAX_HALFLIFE = 30  # Maximum 30 days (faster = better)
MIN_PRICE = 20.0

def calculate_spread(price1, price2):
    """Calculate spread between two price series using linear regression."""
    try:
        # Use linear regression to find hedge ratio
        # price1 = alpha + beta * price2 + error
        X = price2.values.reshape(-1, 1)
        y = price1.values
        
        # Calculate beta (hedge ratio)
        beta = np.polyfit(X.flatten(), y, 1)[0]
        
        # Calculate spread
        spread = price1 - (beta * price2)
        
        return spread, beta
    except:
        return None, None

def calculate_halflife(spread):
    """Calculate half-life of mean reversion (Ornstein-Uhlenbeck process)."""
    try:
        spread_lag = spread.shift(1).dropna()
        spread_ret = spread.diff().dropna()
        
        # Align indices
        spread_lag = spread_lag.iloc[1:]
        spread_ret = spread_ret.iloc[1:]
        
        if len(spread_lag) < 10:
            return None
        
        # Linear regression: spread_ret = lambda * spread_lag + c
        X = spread_lag.values.reshape(-1, 1)
        y = spread_ret.values
        
        lambda_param = np.polyfit(X.flatten(), y, 1)[0]
        
        if lambda_param >= 0:
            return None  # Not mean-reverting
        
        halflife = -np.log(2) / lambda_param
        
        return halflife
    except:
        return None

def test_cointegration(price1, price2):
    """
    Test for cointegration using Engle-Granger method.
    Returns: (cointegrated, p_value)
    """
    try:
        # Engle-Granger cointegration test
        score, p_value, _ = coint(price1, price2)
        
        cointegrated = p_value < MIN_COINTEGRATION_PVALUE
        
        return cointegrated, p_value
    except:
        return False, 1.0

def scan_pairs_trading():
    """Scan for pairs trading opportunities."""
    signals = []
    
    for group in PAIR_GROUPS:
        # Test all pair combinations within each group
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                ticker1 = group[i]
                ticker2 = group[j]
                
                try:
                    print(f"Testing pair: {ticker1} / {ticker2}...")
                    
                    # Get historical data
                    stock1 = yf.Ticker(ticker1)
                    stock2 = yf.Ticker(ticker2)
                    
                    hist1 = stock1.history(period='6mo')
                    hist2 = stock2.history(period='6mo')
                    
                    if len(hist1) < LOOKBACK_PERIOD or len(hist2) < LOOKBACK_PERIOD:
                        continue
                    
                    # Align dates
                    common_dates = hist1.index.intersection(hist2.index)
                    if len(common_dates) < LOOKBACK_PERIOD:
                        continue
                    
                    price1 = hist1.loc[common_dates, 'Close']
                    price2 = hist2.loc[common_dates, 'Close']
                    
                    current_price1 = price1.iloc[-1]
                    current_price2 = price2.iloc[-1]
                    
                    if current_price1 < MIN_PRICE or current_price2 < MIN_PRICE:
                        continue
                    
                    # Test cointegration
                    cointegrated, p_value = test_cointegration(price1, price2)
                    
                    if not cointegrated:
                        continue
                    
                    # Calculate spread
                    spread, hedge_ratio = calculate_spread(price1, price2)
                    
                    if spread is None:
                        continue
                    
                    # Calculate Z-score
                    spread_mean = spread.mean()
                    spread_std = spread.std()
                    
                    if spread_std == 0:
                        continue
                    
                    current_zscore = (spread.iloc[-1] - spread_mean) / spread_std
                    
                    # Check if Z-score is at entry threshold
                    if abs(current_zscore) < MIN_ZSCORE_ENTRY:
                        continue
                    
                    # Calculate half-life
                    halflife = calculate_halflife(spread)
                    
                    if halflife is None or halflife < MIN_HALFLIFE or halflife > MAX_HALFLIFE:
                        continue
                    
                    # Determine trade direction
                    if current_zscore > 0:
                        # Spread too high: Short ticker1, Long ticker2
                        long_ticker = ticker2
                        short_ticker = ticker1
                        long_price = current_price2
                        short_price = current_price1
                    else:
                        # Spread too low: Long ticker1, Short ticker2
                        long_ticker = ticker1
                        short_ticker = ticker2
                        long_price = current_price1
                        short_price = current_price2
                    
                    # Calculate correlation (additional validation)
                    correlation = price1.pct_change().corr(price2.pct_change())
                    
                    # Score
                    score = 0
                    
                    # Cointegration strength
                    if p_value <= 0.01:
                        score += 4  # Very strong cointegration
                    elif p_value <= 0.03:
                        score += 3
                    else:
                        score += 2
                    
                    # Z-score magnitude
                    abs_zscore = abs(current_zscore)
                    if abs_zscore >= 3.0:
                        score += 4  # Extreme divergence
                    elif abs_zscore >= 2.5:
                        score += 3
                    else:
                        score += 2
                    
                    # Half-life (faster mean reversion = better)
                    if halflife <= 10:
                        score += 3
                    elif halflife <= 20:
                        score += 2
                    else:
                        score += 1
                    
                    # Correlation
                    if correlation >= 0.7:
                        score += 3
                    elif correlation >= 0.5:
                        score += 2
                    
                    # Spread stability (low std = more predictable)
                    spread_cv = spread_std / abs(spread_mean) if spread_mean != 0 else 999
                    if spread_cv <= 0.3:
                        score += 2
                    
                    if score >= 10:  # Minimum quality threshold
                        quality = 'HIGH' if score >= 14 else 'MEDIUM'
                        
                        # Calculate position sizes (notional balance)
                        # For $10,000 capital per pair
                        capital_per_leg = 5000
                        long_shares = int(capital_per_leg / long_price)
                        short_shares = int(capital_per_leg / short_price)
                        
                        signals.append({
                            'ticker1': ticker1,
                            'ticker2': ticker2,
                            'price1': current_price1,
                            'price2': current_price2,
                            'long_ticker': long_ticker,
                            'short_ticker': short_ticker,
                            'long_price': long_price,
                            'short_price': short_price,
                            'long_shares': long_shares,
                            'short_shares': short_shares,
                            'hedge_ratio': hedge_ratio,
                            'current_zscore': current_zscore,
                            'p_value': p_value,
                            'halflife': halflife,
                            'correlation': correlation,
                            'spread_mean': spread_mean,
                            'spread_std': spread_std,
                            'score': score,
                            'quality': quality
                        })
                
                except Exception as e:
                    print(f"Error processing pair {ticker1}/{ticker2}: {e}")
                    continue
    
    return signals

def format_alert_message(signals):
    """Format pairs trading alerts for Telegram."""
    if not signals:
        return "🔄 Pairs Trading Scanner\n\nNo cointegrated pair opportunities detected."
    
    signals = sorted(signals, key=lambda x: x['score'], reverse=True)
    ny_tz = pytz.timezone('America/New_York')
    timestamp = datetime.now(ny_tz).strftime('%Y-%m-%d %I:%M %p ET')
    
    message = f"🔄 Pairs Trading Scanner (Statistical Arbitrage)\n⏰ {timestamp}\n"
    message += f"📊 Found {len(signals)} pair trade(s)\n\n"
    
    for signal in signals[:6]:
        quality_emoji = "🟢" if signal['quality'] == 'HIGH' else "🟡"
        
        message += f"{quality_emoji} {signal['ticker1']} / {signal['ticker2']}\n"
        message += f"  📈 LONG: {signal['long_ticker']} @ ${signal['long_price']:.2f} ({signal['long_shares']} shares)\n"
        message += f"  📉 SHORT: {signal['short_ticker']} @ ${signal['short_price']:.2f} ({signal['short_shares']} shares)\n"
        message += f"  📏 Hedge Ratio: {signal['hedge_ratio']:.2f}\n"
        message += f"  📊 Z-Score: {signal['current_zscore']:.2f} (Entry >= 2.0)\n"
        message += f"  🔗 Cointegration p-value: {signal['p_value']:.4f}\n"
        message += f"  ⏱️ Half-Life: {signal['halflife']:.0f} days\n"
        message += f"  🔄 Correlation: {signal['correlation']:.2f}\n"
        message += f"  💡 Exit Target: Z-score = 0 | Stop: Z-score > {MAX_ZSCORE_STOP}\n"
        message += f"  ⭐ Score: {signal['score']}/16 ({signal['quality']})\n\n"
    
    if len(signals) > 6:
        message += f"... and {len(signals) - 6} more\n"
    
    message += "\n💡 Market-neutral hedge | Exit at Z=0 | Stop if Z>3.5"
    
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
    print("Starting Pairs Trading Scanner...")
    print(f"Testing {sum(len(group) * (len(group) - 1) // 2 for group in PAIR_GROUPS)} potential pairs...")
    
    signals = scan_pairs_trading()
    
    print(f"\nFound {len(signals)} cointegrated pair(s)")
    
    message = format_alert_message(signals)
    print(f"\n{message}")
    
    send_telegram_message(message)
    
    print("\nPairs Trading Scanner completed")

if __name__ == "__main__":
    main()
