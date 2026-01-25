"""
Options Screener - Mini Project Starter
Similar to OptionsHawk / OptionsAlpha

Features:
1. Unusual options activity scanner
2. High IV rank opportunities
3. Cheap options finder
4. Earnings plays
5. Options flow tracker

Data Sources:
- yfinance (free, basic options data)
- CBOE (free, IV data)
- Tradier (sandbox free, $10/month live)
- Can upgrade to Polygon.io or IBKR later

Author: KHK Intelligence
Date: January 23, 2026
"""

import os
import json
import yfinance as yf
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_MARKET")
CHAT_ID = os.environ.get("CHAT_ID")

# Watchlist - start with liquid stocks
WATCHLIST = [
    'SPY', 'QQQ', 'IWM',  # ETFs
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META',  # Mega caps
    'AMD', 'INTC', 'NFLX', 'BABA', 'DIS', 'BA', 'GS', 'JPM',  # Others
]

# Alert thresholds
ALERT_THRESHOLDS = {
    'unusual_volume_ratio': 5.0,  # Increased from 3.0 to reduce noise
    'min_volume': 1000,  # Increased from 500 - only large flows
    'high_iv_threshold': 0.50,  # 50%+ IV = elevated volatility (similar to IBKR 58%)
    'high_iv_rank_proxy': 0.60,  # If near-term IV > 60%, likely high IV rank (good for premium selling)
    'call_put_ratio_extreme': 3.0,  # Ratio > 3.0 or < 0.33
    'min_delta': 0.20,  # Minimum delta for actionable trades
}

# Consolidation settings
CONSOLIDATION = {
    'enabled': True,  # Send consolidated digest instead of individual alerts
    'max_trades_per_symbol': 2,  # Top 2 trades per symbol
    'min_premium': 0.50,  # Minimum $0.50 to be actionable (filter out $0.01 lottery tickets)
}

def calculate_black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Calculate Black-Scholes Greeks
    S: Stock price
    K: Strike price
    T: Time to expiration (years)
    r: Risk-free rate
    sigma: Implied volatility
    """
    if T <= 0 or sigma <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:  # put
        delta = -norm.cdf(-d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change in IV
    
    return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 6),
        'theta': round(theta, 4),
        'vega': round(vega, 4)
    }

def get_earnings_date(symbol):
    """Fetch next earnings date for a symbol"""
    try:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar
        if calendar is not None and 'Earnings Date' in calendar:
            earnings_dates = calendar['Earnings Date']
            if isinstance(earnings_dates, pd.Series):
                next_date = earnings_dates.iloc[0] if len(earnings_dates) > 0 else None
            else:
                next_date = earnings_dates
            
            if next_date:
                if isinstance(next_date, pd.Timestamp):
                    return next_date.strftime('%Y-%m-%d')
                return str(next_date)
        return None
    except:
        return None

def send_telegram_alert(message, token, chat_id):
    """Send alert to Telegram"""
    if not token or not chat_id:
        print("  ⚠️  Telegram credentials missing")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if not response.ok:
            print(f"  ⚠️  Telegram API error: {response.status_code} - {response.text[:200]}")
        return response.ok
    except Exception as e:
        print(f"  ⚠️  Telegram request failed: {str(e)}")
        return False

class OptionsScanner:
    """Main options scanner class"""
    
    def __init__(self, symbols=None, enable_alerts=True, send_consolidated=True):
        self.symbols = symbols or WATCHLIST
        self.enable_alerts = enable_alerts
        self.send_consolidated = send_consolidated  # Send one digest instead of many alerts
        self.telegram_token = TELEGRAM_TOKEN
        self.chat_id = CHAT_ID
        self.results = {
            'unusual_activity': [],
            'high_iv': [],
            'cheap_options': [],
            'earnings_plays': [],
            'flow_alerts': [],
            'call_put_ratios': []
        }
        self.earnings_calendar = {}
        self.alerts_sent = []
        self.actionable_trades = []  # For consolidated digest
    
    def scan_unusual_activity(self, symbol):
        """
        Detect unusual options activity with Greeks
        - Volume >> Open Interest
        - Large single trades
        - Calculate Greeks for each opportunity
        """
        print(f"  Scanning unusual activity for {symbol}...")
        
        try:
            ticker = yf.Ticker(symbol)
            stock_price = ticker.history(period='1d')['Close'].iloc[-1]
            
            # Get all expiration dates
            expirations = ticker.options
            if not expirations:
                return None
            
            # Get earnings date
            earnings_date = get_earnings_date(symbol)
            if earnings_date:
                self.earnings_calendar[symbol] = earnings_date
            
            total_call_volume = 0
            total_put_volume = 0
            
            # Scan near-term options (next 2 expirations)
            for exp_date in expirations[:2]:
                opt_chain = ticker.option_chain(exp_date)
                
                calls = opt_chain.calls
                puts = opt_chain.puts
                
                # Calculate total volume for call/put ratio
                total_call_volume += calls['volume'].sum()
                total_put_volume += puts['volume'].sum()
                
                # Time to expiration in years
                exp_datetime = pd.to_datetime(exp_date)
                days_to_exp = (exp_datetime - pd.Timestamp.now()).days
                T = max(days_to_exp / 365.0, 0.001)
                
                # Find unusual volume (volume > 2x open interest)
                unusual_calls = calls[calls['volume'] > (calls['openInterest'] * 2)]
                unusual_puts = puts[puts['volume'] > (puts['openInterest'] * 2)]
                
                # Filter for significant volume (>100 contracts)
                unusual_calls = unusual_calls[unusual_calls['volume'] > 100]
                unusual_puts = unusual_puts[unusual_puts['volume'] > 100]
                
                # Process unusual calls
                for _, row in unusual_calls.iterrows():
                    iv = row.get('impliedVolatility', 0)
                    # Skip if IV is invalid (too low or missing)
                    if iv < 0.01:  # Less than 1% IV is likely bad data
                        continue
                    
                    greeks = calculate_black_scholes_greeks(
                        S=stock_price,
                        K=row['strike'],
                        T=T,
                        r=0.05,
                        sigma=iv,
                        option_type='call'
                    )
                    
                    volume_ratio = row['volume'] / max(row['openInterest'], 1)
                    
                    result = {
                        'symbol': symbol,
                        'type': 'CALL',
                        'strike': row['strike'],
                        'expiration': exp_date,
                        'days_to_exp': days_to_exp,
                        'volume': row['volume'],
                        'open_interest': row['openInterest'],
                        'ratio': volume_ratio,
                        'premium': row['lastPrice'],
                        'iv': iv,
                        'delta': greeks['delta'],
                        'gamma': greeks['gamma'],
                        'theta': greeks['theta'],
                        'vega': greeks['vega'],
                        'stock_price': stock_price,
                        'earnings_date': earnings_date
                    }
                    
                    self.results['unusual_activity'].append(result)
                    
                    # Collect for consolidated digest instead of immediate alert
                    if self.send_consolidated:
                        if (volume_ratio > ALERT_THRESHOLDS['unusual_volume_ratio'] and
                            row['lastPrice'] >= CONSOLIDATION['min_premium'] and
                            abs(greeks['delta']) >= ALERT_THRESHOLDS['min_delta'] and
                            abs(greeks['delta']) < 0.99 and  # Filter out likely bad Greeks (delta too close to ±1)
                            iv >= 0.03):  # Require at least 3% IV (valid data, not necessarily high IV)
                            self._add_actionable_trade(result, 'UNUSUAL_CALL')
                    elif self.enable_alerts and volume_ratio > ALERT_THRESHOLDS['unusual_volume_ratio']:
                        self._send_unusual_activity_alert(result)
                
                # Process unusual puts
                for _, row in unusual_puts.iterrows():
                    iv = row.get('impliedVolatility', 0)
                    # Skip if IV is invalid (too low or missing)
                    if iv < 0.01:  # Less than 1% IV is likely bad data
                        continue
                    
                    greeks = calculate_black_scholes_greeks(
                        S=stock_price,
                        K=row['strike'],
                        T=T,
                        r=0.05,
                        sigma=iv,
                        option_type='put'
                    )
                    
                    volume_ratio = row['volume'] / max(row['openInterest'], 1)
                    
                    result = {
                        'symbol': symbol,
                        'type': 'PUT',
                        'strike': row['strike'],
                        'expiration': exp_date,
                        'days_to_exp': days_to_exp,
                        'volume': row['volume'],
                        'open_interest': row['openInterest'],
                        'ratio': volume_ratio,
                        'premium': row['lastPrice'],
                        'iv': iv,
                        'delta': greeks['delta'],
                        'gamma': greeks['gamma'],
                        'theta': greeks['theta'],
                        'vega': greeks['vega'],
                        'stock_price': stock_price,
                        'earnings_date': earnings_date
                    }
                    
                    self.results['unusual_activity'].append(result)
                    
                    # Collect for consolidated digest instead of immediate alert
                    if self.send_consolidated:
                        if (volume_ratio > ALERT_THRESHOLDS['unusual_volume_ratio'] and
                            row['lastPrice'] >= CONSOLIDATION['min_premium'] and
                            abs(greeks['delta']) >= ALERT_THRESHOLDS['min_delta'] and
                            abs(greeks['delta']) < 0.99 and  # Filter out likely bad Greeks (delta too close to ±1)
                            iv >= 0.03):  # Require at least 3% IV (valid data, not necessarily high IV)
                            self._add_actionable_trade(result, 'UNUSUAL_PUT')
                    elif self.enable_alerts and volume_ratio > ALERT_THRESHOLDS['unusual_volume_ratio']:
                        self._send_unusual_activity_alert(result)
            
            # Calculate and store call/put ratio
            if total_put_volume > 0:
                cp_ratio = total_call_volume / total_put_volume
                self.results['call_put_ratios'].append({
                    'symbol': symbol,
                    'call_volume': total_call_volume,
                    'put_volume': total_put_volume,
                    'cp_ratio': cp_ratio,
                    'sentiment': 'BULLISH' if cp_ratio > 1.5 else ('BEARISH' if cp_ratio < 0.67 else 'NEUTRAL')
                })
                
                # Alert on extreme ratios
                if self.enable_alerts and (cp_ratio > ALERT_THRESHOLDS['call_put_ratio_extreme'] or 
                                          cp_ratio < (1 / ALERT_THRESHOLDS['call_put_ratio_extreme'])):
                    self._send_cp_ratio_alert(symbol, cp_ratio)
            
            return True
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None
    
    def scan_high_iv(self, symbol):
        """
        Find high IV rank opportunities (premium selling)
        - IV > 50% (elevated volatility)
        - Check term structure to estimate IV rank
        - Premium selling: sell calls, puts, spreads, iron condors
        """
        print(f"  Scanning high IV for {symbol}...")
        
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations or len(expirations) < 2:
                return None
            
            # Get stock price
            stock_price = ticker.history(period='1d')['Close'].iloc[-1]
            
            # Check first 3 expirations to build IV term structure
            iv_term_structure = []
            for exp_date in expirations[:3]:
                opt_chain = ticker.option_chain(exp_date)
                calls = opt_chain.calls
                atm_call = calls.iloc[(calls['strike'] - stock_price).abs().argsort()[:1]]
                
                if not atm_call.empty:
                    iv = atm_call.iloc[0].get('impliedVolatility', 0)
                    if iv > 0.01:  # Valid IV
                        iv_term_structure.append({'exp': exp_date, 'iv': iv})
            
            if not iv_term_structure:
                return None
            
            # Use nearest expiration IV
            nearest_iv = iv_term_structure[0]['iv']
            
            # Calculate average IV across term structure (proxy for IV level)
            avg_iv = sum([x['iv'] for x in iv_term_structure]) / len(iv_term_structure)
            max_iv = max([x['iv'] for x in iv_term_structure])
            
            # If any expiration has IV > 50%, it's a premium selling opportunity
            # Prefer checking max IV across term structure (catches elevated IV in any expiration)
            if max_iv > ALERT_THRESHOLDS['high_iv_threshold']:  # IV > 50%
                # Estimate IV rank: if max IV > 60%, likely high IV rank (70%+ percentile)
                estimated_iv_rank = 'HIGH' if max_iv > ALERT_THRESHOLDS['high_iv_rank_proxy'] else 'MEDIUM'
                
                self.results['high_iv'].append({
                    'symbol': symbol,
                    'stock_price': stock_price,
                    'atm_strike': iv_term_structure[0]['exp'],
                    'expiration': iv_term_structure[0]['exp'],
                    'iv': nearest_iv,
                    'max_iv': max_iv,
                    'avg_iv': avg_iv,
                    'iv_rank_estimate': estimated_iv_rank,
                    'call_premium': None,
                    'term_structure': iv_term_structure
                })
            
            return True
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None
    
    def scan_cheap_options(self, symbol, max_price=1.0):
        """
        Find cheap options (lottery tickets)
        - Premium < $1.00
        - OTM options with high delta
        """
        print(f"  Scanning cheap options for {symbol}...")
        
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            
            if not expirations:
                return None
            
            stock_price = ticker.history(period='1d')['Close'].iloc[-1]
            
            # Scan first 3 expirations
            for exp_date in expirations[:3]:
                opt_chain = ticker.option_chain(exp_date)
                
                # Find cheap calls
                cheap_calls = opt_chain.calls[opt_chain.calls['lastPrice'] < max_price]
                cheap_calls = cheap_calls[cheap_calls['volume'] > 50]  # Some liquidity
                
                # Find cheap puts
                cheap_puts = opt_chain.puts[opt_chain.puts['lastPrice'] < max_price]
                cheap_puts = cheap_puts[cheap_puts['volume'] > 50]
                
                # Store top 2 of each
                for _, row in cheap_calls.head(2).iterrows():
                    self.results['cheap_options'].append({
                        'symbol': symbol,
                        'type': 'CALL',
                        'strike': row['strike'],
                        'expiration': exp_date,
                        'premium': row['lastPrice'],
                        'volume': row['volume'],
                        'otm_percent': ((row['strike'] - stock_price) / stock_price) * 100
                    })
                
                for _, row in cheap_puts.head(2).iterrows():
                    self.results['cheap_options'].append({
                        'symbol': symbol,
                        'type': 'PUT',
                        'strike': row['strike'],
                        'expiration': exp_date,
                        'premium': row['lastPrice'],
                        'volume': row['volume'],
                        'otm_percent': ((stock_price - row['strike']) / stock_price) * 100
                    })
            
            return True
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None
    
    def scan_earnings_plays(self):
        """Identify stocks with earnings in next 7 days with high IV"""
        print("\n📅 Scanning for earnings plays...")
        
        for symbol, earnings_date in self.earnings_calendar.items():
            if not earnings_date:
                continue
            
            try:
                earnings_dt = pd.to_datetime(earnings_date)
                days_to_earnings = (earnings_dt - pd.Timestamp.now()).days
                
                if 0 <= days_to_earnings <= 7:
                    # Find high IV options near earnings
                    high_iv_plays = [r for r in self.results['high_iv'] if r['symbol'] == symbol]
                    
                    if high_iv_plays:
                        for play in high_iv_plays:
                            self.results['earnings_plays'].append({
                                'symbol': symbol,
                                'earnings_date': earnings_date,
                                'days_to_earnings': days_to_earnings,
                                'iv': play['iv'],
                                'atm_strike': play['atm_strike'],
                                'stock_price': play['stock_price'],
                                'strategy': 'IV_CRUSH' if play['iv'] > 0.7 else 'STRADDLE'
                            })
                            
                            # Alert on earnings plays
                            if self.enable_alerts and play['iv'] > ALERT_THRESHOLDS['high_iv_threshold']:
                                self._send_earnings_alert(symbol, earnings_date, days_to_earnings, play['iv'])
            except:
                continue
    
    def _add_actionable_trade(self, result, trade_type):
        """Add trade to actionable list for consolidated digest"""
        self.actionable_trades.append({
            'type': trade_type,
            'data': result
        })
        print(f"    ✅ Added {trade_type}: {result['symbol']} ${result['strike']:.0f} (ratio {result['ratio']:.1f}x)")
    
    def _generate_consolidated_digest(self):
        """Generate a single consolidated message with top actionable trades"""
        if not self.actionable_trades:
            return None
        
        # Group by symbol and strategy
        by_symbol = {}
        for trade in self.actionable_trades:
            symbol = trade['data']['symbol']
            if symbol not in by_symbol:
                by_symbol[symbol] = {'calls': [], 'puts': []}
            
            if trade['data']['type'] == 'CALL':
                by_symbol[symbol]['calls'].append(trade['data'])
            else:
                by_symbol[symbol]['puts'].append(trade['data'])
        
        # Build consolidated message
        message = "🎯 *DAILY OPTIONS DIGEST*\n"
        message += f"_{datetime.now().strftime('%B %d, %Y')}_\n\n"
        
        # Market Sentiment Overview
        if self.results['call_put_ratios']:
            message += "*📊 MARKET SENTIMENT*\n"
            for cp in sorted(self.results['call_put_ratios'], key=lambda x: x['cp_ratio'], reverse=True)[:5]:
                emoji = "🟢" if cp['sentiment'] == 'BULLISH' else ("🔴" if cp['sentiment'] == 'BEARISH' else "⚪")
                message += f"{emoji} {cp['symbol']}: {cp['cp_ratio']:.2f} ({cp['sentiment']})\n"
            message += "\n"
        
        # Top Actionable Trades by Symbol
        message += "*🚨 TOP ACTIONABLE TRADES*\n\n"
        
        trade_count = 0
        for symbol in sorted(by_symbol.keys()):
            trades = by_symbol[symbol]
            
            # Get top 2 calls and top 2 puts per symbol
            top_calls = sorted(trades['calls'], key=lambda x: x['ratio'], reverse=True)[:CONSOLIDATION['max_trades_per_symbol']]
            top_puts = sorted(trades['puts'], key=lambda x: x['ratio'], reverse=True)[:CONSOLIDATION['max_trades_per_symbol']]
            
            if not top_calls and not top_puts:
                continue
            
            # Get stock price from first available trade
            stock_price = (top_calls[0]['stock_price'] if top_calls else top_puts[0]['stock_price'])
            message += f"*{symbol}* ${stock_price:.2f}\n"
            
            # Add calls
            for t in top_calls:
                sentiment = "🟢 BULLISH" if t['delta'] > 0.5 else "⚪ MODERATE"
                message += f"  {sentiment} CALL ${t['strike']:.0f} exp {t['expiration']}\n"
                message += f"    Vol: {t['volume']:,.0f} | Ratio: {t['ratio']:.1f}x | ${t['premium']:.2f}\n"
                message += f"    Δ {t['delta']:.2f} | IV {t['iv']:.0%}\n"
                trade_count += 1
            
            # Add puts  
            for t in top_puts:
                sentiment = "🔴 BEARISH" if t['delta'] < -0.5 else "⚪ MODERATE"
                message += f"  {sentiment} PUT ${t['strike']:.0f} exp {t['expiration']}\n"
                message += f"    Vol: {t['volume']:,.0f} | Ratio: {t['ratio']:.1f}x | ${t['premium']:.2f}\n"
                message += f"    Δ {t['delta']:.2f} | IV {t['iv']:.0%}\n"
                trade_count += 1
            
            message += "\n"
            
            if trade_count >= 15:  # Cap at 15 total trades
                break
        
        # Earnings Plays
        if self.results['earnings_plays']:
            message += "*📅 EARNINGS PLAYS*\n"
            for ep in self.results['earnings_plays'][:3]:
                message += f"  {ep['symbol']}: {ep['earnings_date']} ({ep['days_to_earnings']}d)\n"
                message += f"    IV {ep['iv']:.0%} - {ep['strategy']}\n"
            message += "\n"
        
        # Summary
        message += f"━━━━━━━━━━━━━━━\n"
        message += f"📊 {trade_count} actionable trades\n"
        message += f"🔍 {len(self.symbols)} symbols scanned\n"
        message += f"⚡ Filters: Vol/OI>{ALERT_THRESHOLDS['unusual_volume_ratio']}x, Premium>${CONSOLIDATION['min_premium']}, |Δ|>{ALERT_THRESHOLDS['min_delta']}"
        
        return message
    
    def _send_consolidated_digest(self):
        """Send consolidated daily digest"""
        message = self._generate_consolidated_digest()
        
        if not message:
            print("  ℹ️  No actionable trades met thresholds")
            return
        
        print(f"🔍 DEBUG: Telegram Token = {self.telegram_token[:20]}... (length: {len(self.telegram_token) if self.telegram_token else 0})")
        print(f"🔍 DEBUG: Chat ID = {self.chat_id}")
        print(f"🔍 DEBUG: Message length = {len(message)} chars")
        
        # Save message to file for debugging
        with open('last_telegram_message.txt', 'w') as f:
            f.write(message)
        print("  📝 Message saved to last_telegram_message.txt")
        
        if send_telegram_alert(message, self.telegram_token, self.chat_id):
            print(f"  ✉️  Consolidated digest sent ({len(self.actionable_trades)} trades filtered)")
        else:
            print("  ⚠️  Failed to send digest - check Telegram credentials")
    
    def _send_unusual_activity_alert(self, result):
        """Send Telegram alert for unusual activity"""
        if result['volume'] < ALERT_THRESHOLDS['min_volume']:
            return
        
        alert_key = f"{result['symbol']}_{result['type']}_{result['strike']}_{result['expiration']}"
        if alert_key in self.alerts_sent:
            return
        
        message = (
            f"🚨 *UNUSUAL OPTIONS ACTIVITY*\n\n"
            f"*{result['symbol']}* ${result['stock_price']:.2f}\n"
            f"{result['type']} ${result['strike']:.2f} exp {result['expiration']}\n\n"
            f"📊 Volume: {result['volume']:,.0f} | OI: {result['open_interest']:,.0f}\n"
            f"📈 Ratio: {result['ratio']:.1f}x\n"
            f"💰 Premium: ${result['premium']:.2f}\n"
            f"📉 IV: {result['iv']:.1%}\n\n"
            f"*Greeks:*\n"
            f"Δ {result['delta']:.3f} | Γ {result['gamma']:.5f}\n"
            f"Θ {result['theta']:.3f} | ν {result['vega']:.3f}\n"
        )
        
        if result.get('earnings_date'):
            message += f"\n📅 Earnings: {result['earnings_date']}"
        
        if send_telegram_alert(message, self.telegram_token, self.chat_id):
            self.alerts_sent.append(alert_key)
            print(f"    ✉️ Alert sent for {result['symbol']} {result['type']}")
    
    def _send_cp_ratio_alert(self, symbol, cp_ratio):
        """Send alert for extreme call/put ratios"""
        alert_key = f"CP_{symbol}_{datetime.now().strftime('%Y%m%d')}"
        if alert_key in self.alerts_sent:
            return
        
        sentiment = "🟢 BULLISH" if cp_ratio > 2 else "🔴 BEARISH"
        
        message = (
            f"⚡ *EXTREME CALL/PUT RATIO*\n\n"
            f"*{symbol}* - {sentiment}\n\n"
            f"📊 C/P Ratio: {cp_ratio:.2f}\n"
            f"{'High call volume indicates bullish positioning' if cp_ratio > 2 else 'High put volume indicates bearish positioning'}\n"
        )
        
        if send_telegram_alert(message, self.telegram_token, self.chat_id):
            self.alerts_sent.append(alert_key)
            print(f"    ✉️ C/P ratio alert sent for {symbol}")
    
    def _send_earnings_alert(self, symbol, earnings_date, days_to_earnings, iv):
        """Send alert for earnings plays"""
        alert_key = f"EARNINGS_{symbol}_{earnings_date}"
        if alert_key in self.alerts_sent:
            return
        
        message = (
            f"📅 *EARNINGS PLAY DETECTED*\n\n"
            f"*{symbol}*\n\n"
            f"📆 Earnings: {earnings_date} ({days_to_earnings} days)\n"
            f"📈 IV: {iv:.1%} (HIGH)\n\n"
            f"💡 Strategy: {'IV Crush play (sell premium)' if iv > 0.7 else 'Straddle/Strangle opportunity'}\n"
        )
        
        if send_telegram_alert(message, self.telegram_token, self.chat_id):
            self.alerts_sent.append(alert_key)
            print(f"    ✉️ Earnings alert sent for {symbol}")
    
    def run_full_scan(self):
        """Run all scanners on watchlist"""
        print("=" * 80)
        print("🔍 OPTIONS SCREENER - Starting Full Scan")
        print("=" * 80 + "\n")
        
        for symbol in self.symbols:
            print(f"\n📊 Scanning {symbol}...")
            self.scan_unusual_activity(symbol)
            self.scan_high_iv(symbol)
            self.scan_cheap_options(symbol)
        
        # Run earnings scanner after individual scans
        self.scan_earnings_plays()
        
        # Send consolidated digest if enabled
        if self.send_consolidated:
            self._send_consolidated_digest()
        
        print("\n" + "=" * 80)
        print("✅ Scan Complete!")
        print("=" * 80 + "\n")
        
        self._print_results()
        return self.results
    
    def _print_results(self):
        """Print formatted results"""
        
        # Call/Put Ratios
        print("\n⚖️ CALL/PUT RATIOS (Market Sentiment)")
        print("─" * 80)
        if self.results['call_put_ratios']:
            df = pd.DataFrame(self.results['call_put_ratios'])
            df = df.sort_values('cp_ratio', ascending=False)
            print(df[['symbol', 'call_volume', 'put_volume', 'cp_ratio', 'sentiment']].to_string(index=False))
        else:
            print("No call/put ratio data")
        
        # Unusual Activity with Greeks
        print("\n\n🚨 UNUSUAL OPTIONS ACTIVITY (Top 10)")
        print("─" * 80)
        if self.results['unusual_activity']:
            df = pd.DataFrame(self.results['unusual_activity'])
            df = df.sort_values('ratio', ascending=False).head(10)
            print(df[['symbol', 'type', 'strike', 'volume', 'ratio', 'premium', 'delta', 'iv']].to_string(index=False))
        else:
            print("No unusual activity detected")
        
        # Earnings Plays
        print("\n\n📅 EARNINGS PLAYS (Next 7 Days)")
        print("─" * 80)
        if self.results['earnings_plays']:
            df = pd.DataFrame(self.results['earnings_plays'])
            df = df.sort_values('days_to_earnings')
            print(df[['symbol', 'earnings_date', 'days_to_earnings', 'iv', 'strategy']].to_string(index=False))
        else:
            print("No earnings plays in next 7 days")
        
        # High IV
        print("\n\n📈 HIGH IV OPPORTUNITIES (Premium Selling)")
        print("─" * 80)
        if self.results['high_iv']:
            df = pd.DataFrame(self.results['high_iv'])
            df = df.sort_values('max_iv', ascending=False).head(10)
            print(df[['symbol', 'stock_price', 'iv', 'max_iv', 'avg_iv', 'iv_rank_estimate']].to_string(index=False))
            print("\n💡 Strategy: Sell premium (iron condors, credit spreads, covered calls)")
            print("   HIGH rank = IV > 60% (ideal), MEDIUM = IV 50-60% (good)")
        else:
            print("No high IV opportunities found")
        
        # Cheap Options
        print("\n\n💰 CHEAP OPTIONS (Lottery Tickets)")
        print("─" * 80)
        if self.results['cheap_options']:
            df = pd.DataFrame(self.results['cheap_options'])
            df = df.sort_values('premium').head(15)
            print(df[['symbol', 'type', 'strike', 'premium', 'volume', 'otm_percent']].to_string(index=False))
        else:
            print("No cheap options found")
        
        # Summary stats
        print("\n\n📊 SCAN SUMMARY")
        print("─" * 80)
        print(f"Symbols scanned: {len(self.symbols)}")
        print(f"Unusual activity alerts: {len(self.results['unusual_activity'])}")
        print(f"Earnings plays: {len(self.results['earnings_plays'])}")
        print(f"High IV opportunities: {len(self.results['high_iv'])}")
        print(f"Telegram alerts sent: {len(self.alerts_sent)}")
    
    def save_results(self, filename='options_scan_results.json'):
        """Save results to JSON"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = {
            'timestamp': timestamp,
            'results': self.results,
            'symbols_scanned': self.symbols
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    print("=" * 80)
    print("🎯 OPTIONS SCREENER v1.0")
    print("   Mini Project - Options Flow & Unusual Activity")
    print("=" * 80 + "\n")
    
    # Start with a smaller watchlist for testing
    test_symbols = ['SPY', 'AAPL', 'TSLA', 'NVDA', 'AMD']
    
    scanner = OptionsScanner(symbols=test_symbols)
    results = scanner.run_full_scan()
    scanner.save_results('options_scan_results.json')
    
    print("\n" + "=" * 80)
    print("🎉 Scan complete! Check options_scan_results.json for full data")
    print("=" * 80)
