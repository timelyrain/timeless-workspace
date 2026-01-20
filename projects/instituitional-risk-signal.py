"""
╔══════════════════════════════════════════════════════════════════════╗
║                 INSTITUTIONAL RISK SIGNAL v1.7                       ║
╚══════════════════════════════════════════════════════════════════════╝

WHAT'S NEW IN v1.7:
🚀 CALIBRATED V-RECOVERY - Threshold lowered to 8% (from 15%) to catch realistic institutional flows
🛡️ KILL-SWITCH INSTALLED - Aborts override if Score < 60 after 5 days of rallying
✅ Automatic recovery override when extreme stress reverses sharply
✅ Historical tracking of override events for performance analysis
✅ All v1.6 features preserved (14 indicators, Telegram alerts, AI CIO)

PHILOSOPHY:
"Defensive on the way down, Aggressive on the way up, Cynical on the follow-through"
- Keep full protection during crashes
- Catch the 8% institutional thrust off the bottom
- ABORT if credit markets don't confirm the rally within 1 week

TRIGGER LOGIC:
When ALL conditions met, cut cash allocation by 50%:
1. Risk Score was <30 in past 30 days (we were extremely defensive)
2. SPY rallied >8% in 10 days (sharp bounce, standard V-shape magnitude)
3. VIX dropped >15 points from recent high (panic subsiding)
4. Credit improving (HY spread falling or stable)
5. KILL-SWITCH: If override active >5 days, Current Score MUST be >60. If not, abort.

14 SIGNALS + V-RECOVERY OVERRIDE + KILL-SWITCH | INSTITUTIONAL-GRADE
"""

import yfinance as yf
import pandas as pd
from fredapi import Fred
import requests
from io import StringIO
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import schedule
import time
import json
import concurrent.futures

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

CONFIG = {
    'FRED_API_KEY': os.getenv('FRED_API_KEY', 'YOUR_FRED_API_KEY_HERE'),
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN_RISK'),
    'CHAT_ID': os.getenv('CHAT_ID'),
    'RUN_TIME': '09:15',
    
    # V-Recovery Override Settings (Calibrated for realistic institutional flows)
    'V_RECOVERY_ENABLED': True,  # Set to False to disable
    'V_RECOVERY_SCORE_THRESHOLD': 30,  # Must have been this low recently
    # Context: In March 2020 (the fastest crash/recovery in history), SPY rallied about 17% in the 3 days following the bottom. This rule would have barely triggered.
    # Risk: In a standard V-shape correction (like December 2018), the market might "only" rally 8-10% in 10 days. Your current setting would keep you in cash while the train leaves the station.
    'V_RECOVERY_SPY_GAIN': 8,   # CHANGED v1.7: % gain required (8% catches realistic thrusts)
    'V_RECOVERY_SPY_DAYS': 10,  # Days to measure gain
    'V_RECOVERY_VIX_DROP': 15,  # Points VIX must drop from high
    'V_RECOVERY_LOOKBACK': 30,  # Days to look back for extreme scores
}

# Validate FRED API key
if CONFIG['FRED_API_KEY'] == 'YOUR_FRED_API_KEY_HERE':
    print("⚠️  WARNING: FRED_API_KEY not set. Economic indicators (HY Spread, Fed BS, TED, Yield Curve) will fail.")
    print("   Get your free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    print("   Add to GitHub Secrets: FRED_API_KEY")

fred = Fred(api_key=CONFIG['FRED_API_KEY'])

# =============================================================================
# TELEGRAM UTILITIES
# =============================================================================

def send_to_telegram(message):
    """Send message to Telegram channel"""
    if not CONFIG['TELEGRAM_TOKEN'] or not CONFIG['CHAT_ID']:
        print("⚠️  Telegram credentials not found in .env. Skipping alert.")
        return False
    
    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendMessage"
    
    # Telegram has 4096 char limit, split if needed
    max_length = 4000  # Leave buffer for safety
    messages = []
    
    if len(message) <= max_length:
        messages = [message]
    else:
        # Split by sections
        parts = message.split('\n\n')
        current = ""
        for part in parts:
            if len(current) + len(part) + 2 <= max_length:
                current += part + "\n\n"
            else:
                if current:
                    messages.append(current.strip())
                current = part + "\n\n"
        if current:
            messages.append(current.strip())
    
    success = True
    for i, msg in enumerate(messages):
        payload = {
            'chat_id': CONFIG['CHAT_ID'],
            'text': msg,
            'disable_web_page_preview': True
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                if len(messages) == 1:
                    print("✅ Sent to Telegram")
                else:
                    print(f"✅ Sent to Telegram (part {i+1}/{len(messages)})")
            else:
                print(f"⚠️  Telegram error: {resp.status_code} - {resp.text}")
                success = False
        except Exception as e:
            print(f"⚠️  Telegram send failed: {e}")
            success = False
    
    return success

# =============================================================================
# HISTORICAL DATA MANAGER - For V-Recovery Detection
# =============================================================================

class HistoricalDataManager:
    """Manages historical risk scores and market data for V-Recovery detection"""
    
    def __init__(self, history_file='risk_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        """Load historical data from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {'scores': [], 'overrides': [], 'backwardation': []}
        return {'scores': [], 'overrides': [], 'backwardation': []}
    
    def save_history(self):
        """Save historical data to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")
    
    def add_score(self, date, score, spy_price, vix, vix_structure=None, vixy_vxx_ratio=None):
        """Add today's score to history"""
        entry = {
            'date': date,
            'score': score,
            'spy': spy_price,
            'vix': vix
        }
        
        # Add VIX structure data if available
        if vix_structure:
            entry['vix_structure'] = vix_structure
        if vixy_vxx_ratio:
            entry['vixy_vxx_ratio'] = vixy_vxx_ratio
        
        self.history['scores'].append(entry)
        
        # Keep only last 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['scores'] = [
            s for s in self.history['scores'] 
            if s['date'] >= cutoff_date
        ]
    
    def add_backwardation_event(self, date, vixy_vxx_ratio, magnitude_pct):
        """Record backwardation occurrence"""
        if 'backwardation' not in self.history:
            self.history['backwardation'] = []
        
        self.history['backwardation'].append({
            'date': date,
            'ratio': vixy_vxx_ratio,
            'magnitude': magnitude_pct
        })
        
        # Keep only last 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['backwardation'] = [
            b for b in self.history['backwardation'] 
            if b['date'] >= cutoff_date
        ]
    
    def get_backwardation_streak(self):
        """Count consecutive days of backwardation"""
        if 'backwardation' not in self.history or not self.history['backwardation']:
            return 0, 0.0
        
        # Sort by date
        events = sorted(self.history['backwardation'], key=lambda x: x['date'], reverse=True)
        
        # Count consecutive days from today backwards
        today = datetime.now().strftime('%Y-%m-%d')
        streak = 0
        magnitudes = []
        
        # Check if today has backwardation
        if events and events[0]['date'] == today:
            streak = 1
            magnitudes.append(events[0]['magnitude'])
            
            # Count backwards
            for i in range(1, len(events)):
                prev_date = (datetime.strptime(events[i-1]['date'], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                if events[i]['date'] == prev_date:
                    streak += 1
                    magnitudes.append(events[i]['magnitude'])
                else:
                    break
        
        avg_magnitude = sum(magnitudes) / len(magnitudes) if magnitudes else 0.0
        return streak, avg_magnitude
    
    def add_override_event(self, date, reason, conditions):
        """Record when V-Recovery override triggered"""
        self.history['overrides'].append({
            'date': date,
            'reason': reason,
            'conditions': conditions
        })
        
        # Keep only last 50 override events
        if len(self.history['overrides']) > 50:
            self.history['overrides'] = self.history['overrides'][-50:]

    def get_override_streak(self):
        """Count consecutive days of override triggers ending yesterday
        Used for the Kill-Switch logic
        """
        if 'overrides' not in self.history or not self.history['overrides']:
            return 0
            
        # Sort by date descending
        events = sorted(self.history['overrides'], key=lambda x: x['date'], reverse=True)
        streak = 0
        
        # Check from yesterday backwards (to see how long we've been in override mode)
        check_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        for event in events:
            if event['date'] == check_date:
                streak += 1
                # Move check_date back one day
                check_date = (datetime.strptime(check_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            elif event['date'] > check_date:
                continue # Skip if duplicate or future (unlikely)
            else:
                break # Gap found
                
        return streak
    
    def get_recent_scores(self, days=30):
        """Get scores from last N days"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return [s for s in self.history['scores'] if s['date'] >= cutoff]
    
    def had_extreme_score_recently(self, threshold=30, days=30):
        """Check if we had score below threshold in last N days"""
        recent = self.get_recent_scores(days)
        if not recent:
            return False
        return min(s['score'] for s in recent) < threshold

# =============================================================================
# WEIGHTING FRAMEWORK - 14 INDICATORS + V-RECOVERY OVERRIDE
# =============================================================================
# (Full indicator documentation preserved from v1.6)

class RiskDashboard:
    def __init__(self):
        self.data = {}
        self.scores = {}
        self.alerts = []
        self.timestamp = datetime.now()
        self.history_manager = HistoricalDataManager()
        self.v_recovery_active = False
        self.v_recovery_reason = None
        self.market_data = None  # For holding batch downloaded data
        self.missing_signals = [] # Track failed indicators
    
    def fetch_all_data(self):
        """Fetch all 14 indicators from free data sources with error handling"""
        print("\n📊 Fetching 14 indicators from free sources...\n")
        
        # S&P 100 (OEX) for institutional-grade breadth calculations
        self.sample_tickers = self._get_sp100_tickers()
        
        # Prefetch batch data for efficient breadth calculations
        self._fetch_market_breadcrumbs()
        
        self.data = {
            # Tier 1
            'hy_spread': self._fred_get('BAMLH0A0HYM2', 'HY Spread'),
            'fed_bs_yoy': self._fed_bs_yoy(),
            'ted_spread': self._fred_get('TEDRATE', 'TED Spread'),
            'dxy_trend': self._dxy_trend(),
            
            # Tier 2
            'pct_above_50ma': self._pct_above_ma(50),
            'pct_below_200ma': self._pct_below_ma(200),
            'ad_line': self._ad_line_status(),
            'new_hl': self._new_highs_lows(),
            
            # Tier 3
            'sector_rot': self._sector_rotation(),
            'gold_spy': self._gold_spy_ratio(),
            
            # Tier 4
            'yield_curve': self._fred_get('T10Y2Y', 'Yield Curve'),
            'vix': self._yf_get('^VIX', 'VIX'),
        }
        
        # Get VIX structure (returns tuple)
        vix_struct, vixy_vxx_ratio, vix_magnitude = self._vix_structure()
        self.data['vix_struct'] = vix_struct
        self.data['vixy_vxx_ratio'] = vixy_vxx_ratio
        self.data['vix_magnitude'] = vix_magnitude
        
        # Calculate Fear/Greed after VIX is available
        self.data['fear_greed'] = self._fear_greed()
        
        # Verify data quality
        self._verify_data_quality()
        
        # Capture missing signals for strict error handling
        main_signals = ['hy_spread', 'fed_bs_yoy', 'ted_spread', 'dxy_trend',
                       'pct_above_50ma', 'pct_below_200ma', 'ad_line', 'new_hl',
                       'sector_rot', 'gold_spy', 'yield_curve', 'vix', 'vix_struct', 'fear_greed']
        
        self.missing_signals = [k for k in main_signals if self.data.get(k) is None]
        
        valid = sum(1 for k in main_signals if self.data.get(k) is not None)
        print(f"\n✅ Fetched {valid}/14 signals successfully\n")
        return self.data
    
    # =========================================================================
    # DATA FETCHING HELPERS - All return None on error for graceful handling
    # =========================================================================
    
    def _fetch_market_breadcrumbs(self):
        """Fetch batch data using ThreadPool (Faster & more robust than yf.download)"""
        print("   📊 Fetching breadth data (Parallel execution)...")
        
        def fetch_ticker_data(ticker):
            try:
                # Fetch only Close price to save bandwidth
                data = yf.Ticker(ticker).history(period="1y", auto_adjust=True)
                if not data.empty:
                    return data['Close'].rename(ticker)
            except:
                pass
            return None

        try:
            # Use ThreadPool to fetch 100 tickers in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(fetch_ticker_data, self.sample_tickers))
            
            # Filter valid results and combine into one DataFrame
            valid_results = [r for r in results if r is not None]
            
            if valid_results:
                self.market_data = pd.concat(valid_results, axis=1).sort_index()
                print(f"   ✓ Parallel fetch complete for {len(self.market_data.columns)} tickers")
            else:
                print("   ⚠️ Parallel fetch returned empty data")
                self.market_data = None
                
        except Exception as e:
            print(f"   ⚠️ Parallel fetch failed: {e}. Will fallback to individual fetching.")
            self.market_data = None

    def _get_sp100_tickers(self):
        """Return list of S&P 100 tickers, dynamically fetched with fallback"""
        dynamic_list = self._fetch_sp100_dynamic()
        if dynamic_list:
            return dynamic_list
            
        print("   ⚠️  Using hardcoded fallback list for breadth")
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
            'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'CSCO', 'ABT', 'ACN',
            'DHR', 'VZ', 'ADBE', 'NKE', 'TXN', 'NEE', 'PM', 'LIN', 'CRM',
            'ORCL', 'UNP', 'DIS', 'BMY', 'CMCSA', 'NFLX', 'WFC', 'UNH', 'AMD',
            'INTC', 'QCOM', 'RTX', 'HON', 'INTU', 'LOW', 'T', 'AMGN', 'BA',
            'SBUX', 'CAT', 'DE', 'GS', 'SPGI', 'AXP', 'BLK', 'MS', 'MDT',
            'ELV', 'GILD', 'PLD', 'SYK', 'MDLZ', 'MMC', 'C', 'ADI', 'CB',
            'ISRG', 'NOW', 'ZTS', 'TJX', 'VRTX', 'BKNG', 'MO', 'AMT', 'SO',
            'DUK', 'ADP', 'CI', 'PGR', 'SCHW', 'REGN', 'CL', 'MMM', 'BDX',
            'GE', 'SLB', 'USB', 'TMUS', 'CVS', 'FI', 'ETN', 'BSX', 'PNC'
        ]

    def _fetch_sp100_dynamic(self):
        """Fetch S&P 100 components from Wikipedia with caching"""
        cache_file = Path(__file__).parent / "sp100_cache.json"
        stale_tickers = None
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    stale_tickers = data.get('tickers')
                    last_updated = datetime.strptime(data['timestamp'], '%Y-%m-%d')
                    if (datetime.now() - last_updated).days < 30:
                        print(f"   ✓ Loaded {len(data['tickers'])} tickers from cache ({data['timestamp']})")
                        return data['tickers']
            except Exception:
                pass
        
        print("   🌐 Fetching fresh S&P 100 list from Wikipedia...")
        try:
            url = 'https://en.wikipedia.org/wiki/S%26P_100'
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            
            tables = pd.read_html(StringIO(r.text))
            df = None
            for t in tables:
                if 'Symbol' in t.columns:
                    df = t
                    break
            
            if df is not None:
                tickers = df['Symbol'].astype(str).str.replace('.', '-', regex=False).tolist()
                if 90 <= len(tickers) <= 110:
                    try:
                        with open(cache_file, 'w') as f:
                            json.dump({
                                'timestamp': datetime.now().strftime('%Y-%m-%d'),
                                'tickers': tickers
                            }, f)
                        print(f"   ✓ Fetched {len(tickers)} tickers from Wikipedia (Cached)")
                        return tickers
                    except:
                        return tickers
        except Exception as e:
            print(f"   ⚠️  Wikipedia fetch failed: {e}")
        
        if stale_tickers:
            print("   ⚠️  Web fetch failed. Using stale cache as fallback.")
            return stale_tickers
        return None
    
    def _fred_get(self, series, name):
        try:
            data = fred.get_series_latest_release(series)
            val = float(data.iloc[-1])
            print(f"   ✓ {name}: {val:.2f}")
            return val
        except Exception as e:
            print(f"   ✗ {name}: Error - {str(e)[:50]}")
            return None
    
    def _yf_get(self, ticker, name):
        try:
            val = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
            print(f"   ✓ {name}: {val:.2f}")
            return float(val)
        except Exception as e:
            print(f"   ✗ {name}: Error - {str(e)[:50]}")
            return None
    
    def _fed_bs_yoy(self):
        try:
            bs = fred.get_series_latest_release('WALCL')
            yoy = ((bs.iloc[-1] - bs.iloc[-52]) / bs.iloc[-52]) * 100
            print(f"   ✓ Fed BS YoY: {yoy:.1f}%")
            return float(yoy)
        except Exception as e:
            print(f"   ✗ Fed BS YoY: Error - {str(e)[:50]}")
            return None
    
    def _dxy_trend(self):
        try:
            hist = yf.Ticker('DX-Y.NYB').history(period='2mo')['Close']
            if len(hist) < 20: return None
            trend = ((hist.iloc[-1] - hist.rolling(20).mean().iloc[-1]) / hist.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ DXY Trend: {trend:.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ DXY Trend: Error - {str(e)[:50]}")
            return None
    
    def _pct_above_ma(self, period):
        if self.market_data is not None and not self.market_data.empty:
            try:
                ma = self.market_data.rolling(window=period).mean()
                last_prices = self.market_data.iloc[-1]
                last_ma = ma.iloc[-1]
                above = (last_prices > last_ma).sum()
                valid = last_prices.count()
                if valid > 0:
                    pct = (above / valid * 100)
                    print(f"   ✓ % Above {period}-MA: {pct:.0f}% ({above}/{valid}) [Batch]")
                    return pct
            except Exception: pass
        
        above, valid = 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='1y')
                if len(hist) >= period:
                    valid += 1
                    if hist['Close'].iloc[-1] > hist['Close'].rolling(period).mean().iloc[-1]:
                        above += 1
            except: pass
        
        if valid == 0: return None
        pct = (above / valid * 100)
        print(f"   ✓ % Above {period}-MA: {pct:.0f}% ({above}/{valid}) [Slow]")
        return pct
    
    def _pct_below_ma(self, period):
        if self.market_data is not None and not self.market_data.empty:
            try:
                ma = self.market_data.rolling(window=period).mean()
                last_prices = self.market_data.iloc[-1]
                last_ma = ma.iloc[-1]
                below = (last_prices < last_ma).sum()
                valid = last_prices.count()
                if valid > 0:
                    pct = (below / valid * 100)
                    print(f"   ✓ % Below {period}-MA: {pct:.0f}% ({below}/{valid}) [Batch]")
                    return pct
            except Exception: pass

        below, valid = 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='1y')
                if len(hist) >= period:
                    valid += 1
                    if hist['Close'].iloc[-1] < hist['Close'].rolling(period).mean().iloc[-1]:
                        below += 1
            except: pass
        
        if valid == 0: return None
        pct = (below / valid * 100)
        print(f"   ✓ % Below {period}-MA: {pct:.0f}% ({below}/{valid}) [Slow]")
        return pct
    
    def _ad_line_status(self):
        try:
            spy = yf.Ticker('SPY').history(period='3mo')
            if len(spy) < 20: return None
            pct = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-20:].max()) / spy['Close'].iloc[-20:].max()) * 100
            status = 'Confirming' if pct >= -1 else 'Flat' if pct >= -5 else 'Diverging'
            print(f"   ✓ AD Line: {status} ({pct:.1f}% from 20d high)")
            return status
        except Exception as e:
            print(f"   ✗ AD Line: Error - {str(e)[:50]}")
            return None
    
    def _new_highs_lows(self):
        if self.market_data is not None and not self.market_data.empty:
            try:
                recent_data = self.market_data.tail(63)
                if not recent_data.empty:
                    current = recent_data.iloc[-1]
                    highs = (current >= recent_data.max() * 0.995).sum()
                    lows = (current <= recent_data.min() * 1.005).sum()
                    net = highs - lows
                    print(f"   ✓ New H-L: {net:+d} (H:{highs} L:{lows}) [Batch]")
                    return int(net)
            except Exception: pass
                
        highs, lows, valid = 0, 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='3mo')
                if len(hist) >= 52:
                    valid += 1
                    cur = hist['Close'].iloc[-1]
                    if cur >= hist['Close'].max() * 0.995: highs += 1
                    elif cur <= hist['Close'].min() * 1.005: lows += 1
            except: pass
        
        if valid == 0: return None
        net = highs - lows
        print(f"   ✓ New H-L: {net:+d} (H:{highs} L:{lows}) [Slow]")
        return net
    
    def _sector_rotation(self):
        try:
            xlu = yf.Ticker('XLU').history(period='2mo')['Close']
            xlk = yf.Ticker('XLK').history(period='2mo')['Close']
            if len(xlu) < 20 or len(xlk) < 20: return None
            ratio = xlu / xlk
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ XLU/XLK: {trend:+.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ XLU/XLK: Error - {str(e)[:50]}")
            return None
    
    def _gold_spy_ratio(self):
        try:
            gld = yf.Ticker('GLD').history(period='2mo')['Close']
            spy = yf.Ticker('SPY').history(period='2mo')['Close']
            if len(gld) < 20 or len(spy) < 20: return None
            ratio = gld / spy
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ GLD/SPY: {trend:+.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ GLD/SPY: Error - {str(e)[:50]}")
            return None
    
    def _vix_structure(self):
        try:
            vxx = yf.Ticker('VXX').history(period='5d')['Close'].iloc[-1]
            vixy = yf.Ticker('VIXY').history(period='5d')['Close'].iloc[-1]
            ratio = vixy / vxx
            
            if ratio > 1.03:
                struct, mag = 'Contango', (ratio - 1.0) * 100
            elif ratio < 0.97:
                struct, mag = 'Backwardation', (1.0 - ratio) * 100
            else:
                struct, mag = 'Flat', 0.0
            
            streak_info = ""
            if struct == 'Backwardation':
                streak, avg_mag = self.history_manager.get_backwardation_streak()
                if streak > 0:
                    streak_info = f" Day {streak}"
                    self.history_manager.add_backwardation_event(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        vixy_vxx_ratio=ratio,
                        magnitude_pct=mag
                    )
            
            print(f"   ✓ VIX Struct: {struct}{streak_info} (ratio={ratio:.3f}, mag={mag:.1f}%)")
            return struct, ratio, mag
            
        except Exception as e:
            print(f"   ✗ VIX Struct: Error - {str(e)[:50]}")
            return None, None, None
    
    def _fear_greed(self):
        if self.data.get('vix') is None: return None
        try:
            vix = self.data['vix']
            if vix < 10: vix = 10
            if vix > 50: vix = 50
            score = max(0, min(100, 100 - ((vix - 10) * 2.5)))
            print(f"   ✓ Fear/Greed: {score:.0f}/100 (VIX-derived)")
            return float(score)
        except Exception: return None
    
    def _verify_data_quality(self):
        print("\n🔍 Verifying data quality...")
        critical_missing = []
        warnings = []
        if self.data.get('hy_spread') is None: critical_missing.append("HY Spread")
        elif self.data['hy_spread'] > 10: warnings.append(f"HY Spread high: {self.data['hy_spread']:.2f}%")
        if self.data.get('ted_spread') is None: critical_missing.append("TED Spread")
        if self.data.get('pct_above_50ma') is None: warnings.append("% Above 50-MA missing")
        if self.data.get('vix') is None: critical_missing.append("VIX")
        
        if critical_missing:
            print(f"   ⚠️  CRITICAL DATA MISSING: {', '.join(critical_missing)}")
        if warnings:
            print(f"   ⚠️  DATA QUALITY WARNINGS: {', '.join(warnings)}")
        if not critical_missing and not warnings:
            print(f"   ✅ All critical data present")
    
    # =========================================================================
    # V-RECOVERY DETECTION + KILL SWITCH (UPDATED v1.7)
    # =========================================================================
    
    def check_v_recovery_trigger(self):
        """
        Check if V-Recovery override should activate
        INCLUDES KILL-SWITCH: If override active > 5 days but score < 60, abort.
        """
        if not CONFIG['V_RECOVERY_ENABLED']:
            return False, None
        
        try:
            # --- EXISTING TRIGGER LOGIC ---
            # Get SPY historical data
            spy = yf.Ticker('SPY').history(period='2mo')
            if len(spy) < CONFIG['V_RECOVERY_SPY_DAYS']:
                return False, "Insufficient SPY data"
            
            # Condition 1: Had extreme score recently
            had_extreme = self.history_manager.had_extreme_score_recently(
                threshold=CONFIG['V_RECOVERY_SCORE_THRESHOLD'],
                days=CONFIG['V_RECOVERY_LOOKBACK']
            )
            
            if not had_extreme:
                return False, None
            
            # Condition 2: SPY rallied sharply
            lookback = CONFIG['V_RECOVERY_SPY_DAYS']
            spy_gain = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-lookback]) / 
                       spy['Close'].iloc[-lookback] * 100)
            
            if spy_gain < CONFIG['V_RECOVERY_SPY_GAIN']:
                return False, None
            
            # Condition 3: VIX dropped significantly
            recent_scores = self.history_manager.get_recent_scores(CONFIG['V_RECOVERY_LOOKBACK'])
            if not recent_scores or self.data.get('vix') is None:
                return False, "Insufficient VIX history"
            
            vix_high = max(s['vix'] for s in recent_scores if s.get('vix'))
            vix_drop = vix_high - self.data['vix']
            
            if vix_drop < CONFIG['V_RECOVERY_VIX_DROP']:
                return False, None
            
            # Condition 4: Credit improving or stable
            if self.data.get('hy_spread') is not None:
                recent_avg_score = sum(s['score'] for s in recent_scores) / len(recent_scores)
                credit_stable = self.data['hy_spread'] < 6.0
                if not credit_stable:
                    return False, "Credit still deteriorating"
            
            # --- NEW KILL-SWITCH LOGIC ---
            current_score = self.scores['total']
            override_streak = self.history_manager.get_override_streak()
            
            # If we've been overriding for 5+ days, the score MUST have recovered to at least 60 (Elevated)
            # If it's still < 60 (High/Extreme Risk), the fundamentals aren't confirming the rally.
            if override_streak >= 5 and current_score < 60:
                return False, f"KILL-SWITCH ACTIVE: Rally unconfirmed. Day {override_streak+1} of override but Score is {current_score:.1f} (<60)."
            
            # --- ALL CONDITIONS MET ---
            streak_msg = f" (Day {override_streak + 1})" if override_streak > 0 else " (New Trigger)"
            reason = (
                f"V-Recovery Triggered{streak_msg}:\n"
                f"  • Score was <{CONFIG['V_RECOVERY_SCORE_THRESHOLD']} recently\n"
                f"  • SPY rallied {spy_gain:.1f}% in {lookback} days\n"
                f"  • VIX dropped {vix_drop:.1f} points\n"
                f"  • Validation: Score {current_score:.1f} (Kill-switch at <60 after Day 5)"
            )
            
            return True, reason
            
        except Exception as e:
            print(f"   ⚠️  V-Recovery check failed: {e}")
            return False, None
    
    def apply_v_recovery_override(self, base_allocation):
        """Apply V-Recovery override to base allocation"""
        if not self.v_recovery_active:
            return base_allocation
        
        tier1, tier2, tier3, cash = base_allocation
        
        # Cut cash by 50%, redistribute to tiers
        new_cash = cash / 2
        cash_freed = cash - new_cash
        
        # Redistribute freed cash proportionally to tier weights
        tier1 += cash_freed * 0.60
        tier2 += cash_freed * 0.30
        tier3 += cash_freed * 0.10
        
        return (tier1, tier2, tier3, new_cash)
    
    # =========================================================================
    # SCORING LOGIC
    # =========================================================================
    
    def calculate_scores(self):
        d = self.data
        
        # Tier 1: Credit & Liquidity (50 pts)
        s1 = self._score_range(d.get('hy_spread'), [(3,20),(4,16),(4.5,12),(5.5,6)], 0)
        s2 = self._score_range(d.get('fed_bs_yoy'), [(10,15),(2,12),(-2,9),(-10,4)], 0)
        s3 = self._score_range(d.get('ted_spread'), [(0.3,10),(0.5,8),(0.75,5),(1,2)], 0)
        s4 = self._score_range(d.get('dxy_trend'), [(-3,5),(-1,4),(1,3),(3,1)], 0)
        
        # Tier 2: Breadth (30 pts)
        s5 = self._score_range(d.get('pct_above_50ma'), [(75,12),(65,10),(55,7),(45,4),(35,2)], 0)
        s6 = self._score_range(d.get('pct_below_200ma'), [(15,10),(25,8),(35,6),(50,3),(65,1)], 0, inverse=True)
        s7 = {'Confirming':5, 'Flat':2, 'Diverging':0}.get(d.get('ad_line'), 0)
        s8 = self._score_range(d.get('new_hl'), [(10,3),(5,2.5),(0,2),(-5,1),(-10,0.5)], 0)
        
        # Tier 3: Risk Appetite (15 pts)
        s9 = self._score_range(d.get('sector_rot'), [(-5,6),(-2,5),(2,4),(5,2)], 0)
        s10 = self._score_range(d.get('gold_spy'), [(-3,5),(-1,4),(1,3),(3,1)], 0)
        s11 = {'Contango':4, 'Flat':2, 'Backwardation':0}.get(d.get('vix_struct'), 0)
        
        # Tier 4: Sentiment (5 pts)
        s12 = self._score_range(d.get('yield_curve'), [(0.5,3),(0.2,2.5),(-0.2,2),(-0.5,1)], 0)
        s13 = self._score_range(d.get('vix'), [(12,0),(16,1.5),(20,1),(30,0.5)], 0)
        fg = d.get('fear_greed')
        s14 = 0.5 if (fg and 35 <= fg <= 65) else 0.3 if fg else 0
        
        total = s1+s2+s3+s4+s5+s6+s7+s8+s9+s10+s11+s12+s13+s14
        
        self.scores = {
            'total': total,
            'tier1': s1+s2+s3+s4,
            'tier2': s5+s6+s7+s8,
            'tier3': s9+s10+s11,
            'tier4': s12+s13+s14,
            'components': {
                'hy_spread': s1, 'fed_bs': s2, 'ted': s3, 'dxy': s4,
                'pct_50ma': s5, 'pct_200ma': s6, 'ad_line': s7, 'new_hl': s8,
                'sector_rot': s9, 'gold_spy': s10, 'vix_struct': s11,
                'yield_curve': s12, 'vix': s13, 'fear_greed': s14
            }
        }
        return self.scores
    
    def _score_range(self, val, thresholds, default, inverse=False):
        if val is None: return default
        for thresh, score in thresholds:
            if (val < thresh if not inverse else val > thresh): return score
        return default
    
    def get_base_allocation(self):
        score = self.scores['total']
        if score >= 90: return (0.60, 0.30, 0.10, 0.00)
        elif score >= 75: return (0.60, 0.30, 0.05, 0.05)
        elif score >= 60: return (0.60, 0.20, 0.00, 0.20)
        elif score >= 40: return (0.40, 0.10, 0.00, 0.50)
        else: return (0.20, 0.00, 0.00, 0.80)
    
    # =========================================================================
    # DIVERGENCE DETECTION
    # =========================================================================
    
    def detect_divergences(self):
        self.alerts = []
        d = self.data
        
        # Alert 1: Hidden Danger
        if d.get('vix') and d['vix'] < 15:
            if (d.get('hy_spread') and d['hy_spread'] > 4.5) or \
               (d.get('pct_above_50ma') and d['pct_above_50ma'] < 50):
                self.alerts.append({'type': 'HIDDEN DANGER', 'severity': 'CRITICAL', 'icon': '🚨🚨🚨',
                    'msg': 'VIX SUPPRESSED - CREDIT/BREADTH DETERIORATING', 'action': 'IGNORE VIX, REDUCE RISK NOW'})
        
        # Alert 2: Liquidity Drain
        if (d.get('fed_bs_yoy') and d['fed_bs_yoy'] < -5) and (d.get('dxy_trend') and d['dxy_trend'] > 3):
            self.alerts.append({'type': 'LIQUIDITY DRAIN', 'severity': 'HIGH', 'icon': '🚨🚨',
                'msg': 'FED CONTRACTING + DOLLAR SURGING', 'action': 'REDUCE RISK ASSETS 20-30%'})
        
        # Alert 3: Credit Stress
        if (d.get('hy_spread') and d['hy_spread'] > 5) or (d.get('ted_spread') and d['ted_spread'] > 0.8):
            self.alerts.append({'type': 'CREDIT WARNING', 'severity': 'HIGH', 'icon': '🚨🚨',
                'msg': 'CREDIT MARKETS PRICING STRESS', 'action': 'GO DEFENSIVE (Level 2-3)'})
        
        # Alert 4: Breadth Collapse
        if (d.get('pct_above_50ma') and d['pct_above_50ma'] < 40) and (d.get('pct_below_200ma') and d['pct_below_200ma'] > 50):
            self.alerts.append({'type': 'BREADTH COLLAPSE', 'severity': 'HIGH', 'icon': '🚨',
                'msg': 'SEVERE MARKET BREAKDOWN', 'action': 'REDUCE EQUITY 30%+'})
        
        # Alert 5: Backwardation Persistence
        if d.get('vix_struct') == 'Backwardation':
            streak, avg_mag = self.history_manager.get_backwardation_streak()
            if streak >= 5:
                self.alerts.append({'type': 'BACKWARDATION PERSISTING', 'severity': 'CRITICAL', 'icon': '🚨🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak} - INSTITUTIONS STILL HEDGING', 'action': 'TIGHTEN STOPS 12-15%, REDUCE TIER 3'})
            elif streak >= 3:
                self.alerts.append({'type': 'BACKWARDATION PERSISTING', 'severity': 'HIGH', 'icon': '🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak} - PATTERN FORMING', 'action': 'WATCH CREDIT & BREADTH CLOSELY'})
        
        # Alert 6: V-Recovery Active
        if self.v_recovery_active:
            self.alerts.append({'type': 'V-RECOVERY OVERRIDE ACTIVE', 'severity': 'INFO', 'icon': '🚀',
                'msg': self.v_recovery_reason, 'action': 'CASH ALLOCATION CUT BY 50% - AGGRESSIVE RE-ENTRY'})
        
        # Alert 7: All Clear
        if not self.alerts and self.scores['total'] >= 85:
            self.alerts.append({'type': 'ALL CLEAR', 'severity': 'SAFE', 'icon': '✅',
                'msg': 'HEALTHY MARKET CONDITIONS', 'action': 'FULL DEPLOYMENT OK'})
        
        return self.alerts
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def _send_error_notification(self):
        msg = [f"⚠️ SYSTEM ALERT: DATA FETCH FAILED\n📅 {self.timestamp.strftime('%Y-%m-%d %H:%M')}"]
        for s in self.missing_signals: msg.append(f"❌ {s}")
        msg.append("\n🚫 Score calculation aborted to prevent inaccurate results.")
        send_to_telegram("\n".join(msg))

    def generate_report(self):
        score = self.scores['total']
        d = self.data
        base_alloc = self.get_base_allocation()
        self.v_recovery_active, self.v_recovery_reason = self.check_v_recovery_trigger()
        final_alloc = self.apply_v_recovery_override(base_alloc) if self.v_recovery_active else base_alloc
        
        if score >= 90: risk, pos = "★★★★★ ALL CLEAR", "FULL DEPLOYMENT"
        elif score >= 75: risk, pos = "★★★★☆ NORMAL", "STAY COURSE"
        elif score >= 60: risk, pos = "★★★☆☆ ELEVATED", "REDUCE TIER 3"
        elif score >= 40: risk, pos = "★★☆☆☆ HIGH RISK", "GO DEFENSIVE"
        else: risk, pos = "★☆☆☆☆ EXTREME", "MAX DEFENSE"
        
        lines = [
            "🎯 RISK DASHBOARD v1.7",
            f"📅 {self.timestamp.strftime('%b %d, %Y @ %H:%M')}",
            "",
            f"📊 SCORE: {score:.1f}/100",
            f"🎚️ {risk}",
            f"💼 {pos}",
            "",
        ]
        
        if self.v_recovery_active:
            lines.extend([
                "🚀 V-RECOVERY ACTIVE",
                f"Base: {int(base_alloc[0]*100)}/{int(base_alloc[1]*100)}/{int(base_alloc[2]*100)}/{int(base_alloc[3]*100)}",
                f"Override: {int(final_alloc[0]*100)}/{int(final_alloc[1]*100)}/{int(final_alloc[2]*100)}/{int(final_alloc[3]*100)}",
                "(T1/T2/T3/Cash)",
                ""
            ])
        else:
            lines.extend([
                "💰 ALLOCATION",
                f"{int(final_alloc[0]*100)}/{int(final_alloc[1]*100)}/{int(final_alloc[2]*100)}/{int(final_alloc[3]*100)}",
                "(T1/T2/T3/Cash)",
                ""
            ])
        
        lines.extend(self._generate_allocation_breakdown(final_alloc))
        sc = self.scores['components']
        lines.extend([
            "📈 TIER SCORES",
            f"T1 (Credit & Liquidity): {self.scores['tier1']:.1f}/50",
            f"  • HY Spread: {sc['hy_spread']:.1f}/20 [{d.get('hy_spread', 'N/A')}%]",
            f"  • Fed BS YoY: {sc['fed_bs']:.1f}/15 [{d.get('fed_bs_yoy', 'N/A')}%]",
            f"  • TED Spread: {sc['ted']:.1f}/10 [{d.get('ted_spread', 'N/A')}]",
            f"  • DXY Trend: {sc['dxy']:.1f}/5 [{d.get('dxy_trend', 'N/A')}%]",
            "",
            f"T2 (Market Breadth): {self.scores['tier2']:.1f}/30",
            f"  • % >50-MA: {sc['pct_50ma']:.1f}/12 [{d.get('pct_above_50ma', 'N/A')}%]",
            f"  • % <200-MA: {sc['pct_200ma']:.1f}/10 [{d.get('pct_below_200ma', 'N/A')}%]",
            f"  • A-D Line: {sc['ad_line']:.1f}/5 [{d.get('ad_line', 'N/A')}]",
            f"  • New H-L: {sc['new_hl']:.1f}/3 [{d.get('new_hl', 'N/A')}]",
            "",
            f"T3 (Risk Appetite): {self.scores['tier3']:.1f}/15",
            f"  • XLU/XLK: {sc['sector_rot']:.1f}/6 [{d.get('sector_rot', 'N/A')}%]",
            f"  • GLD/SPY: {sc['gold_spy']:.1f}/5 [{d.get('gold_spy', 'N/A')}%]",
            f"  • VIX Struct: {sc['vix_struct']:.1f}/4 [{d.get('vix_struct', 'N/A')}]",
            "",
            f"T4 (Sentiment): {self.scores['tier4']:.1f}/5",
            f"  • Yield Curve: {sc['yield_curve']:.1f}/3 [{d.get('yield_curve', 'N/A')}%]",
            f"  • VIX Level: {sc['vix']:.1f}/1.5 [{d.get('vix', 'N/A')}]",
            f"  • Fear/Greed: {sc['fear_greed']:.1f}/0.5 [{d.get('fear_greed', 'N/A')}]",
            "",
        ])
        
        lines.extend(self._generate_summary())
        
        if self.alerts:
            lines.append("")
            lines.append("🚨 ALERTS")
            for alert in self.alerts:
                lines.extend(["", f"{alert['icon']} {alert['type']}", f"{alert['msg']}", f"→ {alert['action']}"])
        
        return "\n".join(lines)
    
    def _generate_allocation_breakdown(self, allocation):
        tier1_pct, tier2_pct, tier3_pct, cash_pct = allocation
        total_invested_pct = tier1_pct + tier2_pct + tier3_pct
        return [
            "💵 BREAKDOWN",
            f"T1 Core: {tier1_pct*100:.0f}%",
            f"T2 Tactical: {tier2_pct*100:.0f}%",
            f"T3 Aggr: {tier3_pct*100:.0f}%",
            f"Cash: {cash_pct*100:.0f}%",
            "",
            f"Deployed: {total_invested_pct*100:.0f}%",
            f"Risk: {(1-cash_pct)*100:.0f}%",
            ""
        ]
    
    def _generate_summary(self):
        d = self.data
        good, concerns = [], []
        
        if d.get('hy_spread') and d['hy_spread'] < 4.5: good.append("Credit markets healthy")
        elif d.get('hy_spread') and d['hy_spread'] > 5: concerns.append(f"Credit stress ({d['hy_spread']:.2f}%)")
        
        if d.get('pct_above_50ma') and d['pct_above_50ma'] > 65: good.append("Strong breadth")
        elif d.get('pct_above_50ma') and d['pct_above_50ma'] < 50: concerns.append("Breadth weakening")
        
        if d.get('sector_rot') and d['sector_rot'] > 3: concerns.append("Defensive rotation")
        elif d.get('sector_rot') and d['sector_rot'] < -3: good.append("Risk-on rotation")
        
        lines = ["📝 SUMMARY"]
        if good: lines.append("✅ Good:"); lines.extend([f"• {x}" for x in good[:3]])
        if concerns: lines.append(""); lines.append("⚠️ Watch:"); lines.extend([f"• {x}" for x in concerns[:3]])
        if not good and not concerns: lines.append("• No major issues")
        return lines

    def _get_backwardation_context(self):
        d = self.data
        if d.get('vix_struct') != 'Backwardation': return {'active': False, 'message': 'No backwardation'}
        streak, avg_mag = self.history_manager.get_backwardation_streak()
        severity = "CRITICAL" if streak >= 5 else "HIGH" if streak >= 3 else "MEDIUM"
        return {
            'active': True, 'streak_days': streak, 'severity': severity,
            'message': f"Backwardation Day {streak}: {severity}."
        }

    def _construct_cio_prompt(self):
        score = self.scores['total']
        d = self.data
        data_package = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': f"{score:.1f}/100",
            'tier_scores': {
                'tier1': f"{self.scores['tier1']:.1f}/50",
                'tier2': f"{self.scores['tier2']:.1f}/30",
                'tier3': f"{self.scores['tier3']:.1f}/15",
                'tier4': f"{self.scores['tier4']:.1f}/5",
            },
            'raw_indicators': d,
            'backwardation_context': self._get_backwardation_context(),
            'allocation': str(self.get_base_allocation()),
            'alerts': self.alerts,
            'v_recovery': {
                'active': self.v_recovery_active,
                'reason': self.v_recovery_reason
            }
        }
        
        prompt = f"""You are the CIO analyzing today's institutional risk dashboard. The CEO values blunt, witty analysis.
TODAY'S DATA: {json.dumps(data_package, default=str, indent=2)}

CONTEXT:
- Tier 1 (Credit/Liquidity) = 50% weight (Most important)
- Tier 2 (Breadth) = 30% weight
- V-Recovery Logic: If active, we override conservatism. KILL SWITCH activates if score < 60 after 5 days.

YOUR TASK:
Write a brief CIO interpretation for iPhone Telegram.
FORMAT:
💭 HEADLINE
📊 SCORE QUALITY
👁️ WHAT I SEE
🎯 MARKET REGIME
💡 MY CALL (Allocation & Why)
🔄 FLIP TRIGGERS
⚡ BOTTOM LINE

KEEP UNDER 1200 CHARS. USE ACTUAL NUMBERS. BE DIRECT.
Write now:"""
        return prompt

    def generate_cio_interpretation(self):
        print("🔍 Checking for ANTHROPIC_API_KEY...")
        key = os.getenv('ANTHROPIC_API_KEY')
        if not key or 'YOUR_' in key: return None
        
        try:
            print("\n🧠 Generating CIO interpretation (Claude)...")
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": self._construct_cio_prompt()}]},
                timeout=30
            )
            if resp.status_code == 200:
                return f"🧠 CIO INTERPRETATION (Claude)\n📅 {self.timestamp.strftime('%b %d, %Y')}\n\n{resp.json()['content'][0]['text']}"
            return None
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None

    def generate_gemini_interpretation(self):
        print("🔍 Checking for GEMINI_API_KEY...")
        key = os.getenv('GEMINI_API_KEY')
        if not key or 'YOUR_' in key: return None
        
        try:
            import google.generativeai as genai
            print("\n🧠 Generating CIO interpretation (Gemini)...")
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            resp = model.generate_content(self._construct_cio_prompt())
            if resp.text:
                return f"🧠 CIO INTERPRETATION (Gemini)\n📅 {self.timestamp.strftime('%b %d, %Y')}\n\n{resp.text}"
            return None
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None

    def run_assessment(self):
        print("\n" + "="*80 + "\nSTARTING DAILY RISK ASSESSMENT v1.7\n" + "="*80)
        self.fetch_all_data()
        
        if self.missing_signals:
            print(f"\n❌ CRITICAL: Found {len(self.missing_signals)} missing indicators. Aborting.")
            self._send_error_notification()
            return None

        self.calculate_scores()
        
        # Save history
        try: spy_price = yf.Ticker('SPY').history(period='1d')['Close'].iloc[-1]
        except: spy_price = None
        self.history_manager.add_score(
            date=self.timestamp.strftime('%Y-%m-%d'),
            score=self.scores['total'],
            spy_price=spy_price,
            vix=self.data.get('vix'),
            vix_structure=self.data.get('vix_struct'),
            vixy_vxx_ratio=self.data.get('vixy_vxx_ratio')
        )
        
        # Check triggers
        self.v_recovery_active, self.v_recovery_reason = self.check_v_recovery_trigger()
        if self.v_recovery_active:
            print(f"\n🚀 {self.v_recovery_reason}")
            self.history_manager.add_override_event(
                date=self.timestamp.strftime('%Y-%m-%d'),
                reason="V-Recovery",
                conditions=self.v_recovery_reason
            )
        
        self.detect_divergences()
        report = self.generate_report()
        print("\n" + report + "\n")
        
        with open(f"risk_report_{self.timestamp.strftime('%Y%m%d')}.txt", 'w') as f: f.write(report)
        self.history_manager.save_history()
        send_to_telegram(report)
        
        # CIO Interpretations
        cio = self.generate_cio_interpretation()
        if cio: send_to_telegram(cio)
        
        gem = self.generate_gemini_interpretation()
        if gem: send_to_telegram(gem)
        
        return self.scores['total']

def main():
    print("INSTITUTIONAL RISK DASHBOARD v1.7 | 14 Signals + V-Recovery (8%) + Kill-Switch")
    dashboard = RiskDashboard()
    dashboard.run_assessment()

if __name__ == "__main__":
    try: main()
    except Exception as e:
        import traceback
        traceback.print_exc()