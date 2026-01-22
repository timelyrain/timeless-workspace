"""
╔══════════════════════════════════════════════════════════════════════╗
║                 INSTITUTIONAL RISK SIGNAL v1.8                       ║
╚══════════════════════════════════════════════════════════════════════╝

WHAT'S NEW IN v1.8:
🎯 2026 PORTFOLIO MAPPING - Real allocation guidance for your actual positions
📊 ACTIONABLE ADJUSTMENTS - Specific guidance per position type
✅ All v1.7 features preserved (V-Recovery 8%, Kill-Switch, AI CIO)

YOUR 2026 PORTFOLIO STRUCTURE (Aligned with ARTHUR_CONTEXT.md):
- 30% Global Core (VWRA, ES3, DHL, 82846 - diversified value)
- 30% Growth Engine (CSNDX, CTEC, HEAL, INRA, LOCK - high growth)
- 25% Income Strategy (Wheel on GOOGL, PEP, V - premium collection)
- 5% Hedge (QQQ puts 15% OTM - downside protection)
- 10% Reserves (Cash + Gold split dynamically by risk score)

ALLOCATION PHILOSOPHY:
Score 90+: FULL DEPLOYMENT - Run your base allocation
Score 75-90: NORMAL - Base allocation, tighter stops
Score 60-75: ELEVATED - Reduce speculative, defensive options
Score 40-60: HIGH RISK - Cut QQQ/spec, raise cash via options
Score <40: EXTREME - Max defense, protect capital

14 SIGNALS + V-RECOVERY + PORTFOLIO MAPPING | INSTITUTIONAL-GRADE

SYSTEM: 15% Portfolio Risk Monitor (Arthur Protocol)
CONTEXT: See ARTHUR_CONTEXT.md for full strategy and logic constraints.
"""

import yfinance as yf
import pandas as pd
from fredapi import Fred
import requests
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

CONFIG = {
    'FRED_API_KEY': os.getenv('FRED_API_KEY', 'YOUR_FRED_API_KEY_HERE'),
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN_RISK'),
    'CHAT_ID': os.getenv('CHAT_ID'),
    'RUN_TIME': '09:15',
    
    # V-Recovery Override Settings
    'V_RECOVERY_ENABLED': True,
    'V_RECOVERY_SCORE_THRESHOLD': 30,
    'V_RECOVERY_SPY_GAIN': 8,
    'V_RECOVERY_SPY_DAYS': 10,
    'V_RECOVERY_VIX_DROP': 15,
    'V_RECOVERY_LOOKBACK': 30,
}

# Portfolio Configuration (2026 Structure - Aligned with ARTHUR_CONTEXT.md)
PORTFOLIO_2026 = {
    'TOTAL_CAPITAL': 1_000_000,  # $1M active trading capital
    'BASE_ALLOCATION': {
        'global_core': 0.30,      # VWRA, ES3, DHL, 82846
        'growth_engine': 0.30,    # CSNDX, CTEC, HEAL, INRA, LOCK
        'income_strategy': 0.25,  # Wheel on GOOGL, PEP, V
        'alpha_insurance': 0.05,  # Theme stocks (Sniper) + QQQ puts (Hedge)
        'reserves': 0.10          # Cash + Gold (split dynamically by risk score)
    }
}

if CONFIG['FRED_API_KEY'] == 'YOUR_FRED_API_KEY_HERE':
    print("⚠️  WARNING: FRED_API_KEY not set.")
    print("   Get your free key at: https://fred.stlouisfed.org/docs/api/api_key.html")

fred = Fred(api_key=CONFIG['FRED_API_KEY'])

# =============================================================================
# TELEGRAM UTILITIES
# =============================================================================

def send_to_telegram(message):
    """Send message to Telegram channel"""
    if not CONFIG['TELEGRAM_TOKEN'] or not CONFIG['CHAT_ID']:
        print("⚠️  Telegram credentials not found. Skipping alert.")
        return False
    
    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendMessage"
    max_length = 4000
    messages = []
    
    if len(message) <= max_length:
        messages = [message]
    else:
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
        payload = {'chat_id': CONFIG['CHAT_ID'], 'text': msg, 'disable_web_page_preview': True}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"✅ Sent to Telegram" + (f" (part {i+1}/{len(messages)})" if len(messages) > 1 else ""))
            else:
                print(f"⚠️  Telegram error: {resp.status_code}")
                success = False
        except Exception as e:
            print(f"⚠️  Telegram send failed: {e}")
            success = False
    
    return success

# =============================================================================
# HISTORICAL DATA MANAGER
# =============================================================================

class HistoricalDataManager:
    """Manages historical risk scores and market data"""
    
    def __init__(self, history_file='risk_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {'scores': [], 'overrides': [], 'backwardation': []}
        return {'scores': [], 'overrides': [], 'backwardation': []}
    
    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")
    
    def add_score(self, date, score, spy_price, vix, vix_structure=None, vixy_vxx_ratio=None):
        entry = {'date': date, 'score': score, 'spy': spy_price, 'vix': vix}
        if vix_structure:
            entry['vix_structure'] = vix_structure
        if vixy_vxx_ratio:
            entry['vixy_vxx_ratio'] = vixy_vxx_ratio
        
        self.history['scores'].append(entry)
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['scores'] = [s for s in self.history['scores'] if s['date'] >= cutoff_date]
    
    def add_backwardation_event(self, date, vixy_vxx_ratio, magnitude_pct):
        if 'backwardation' not in self.history:
            self.history['backwardation'] = []
        self.history['backwardation'].append({'date': date, 'ratio': vixy_vxx_ratio, 'magnitude': magnitude_pct})
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['backwardation'] = [b for b in self.history['backwardation'] if b['date'] >= cutoff_date]
    
    def get_backwardation_streak(self):
        if 'backwardation' not in self.history or not self.history['backwardation']:
            return 0, 0.0
        events = sorted(self.history['backwardation'], key=lambda x: x['date'], reverse=True)
        today = datetime.now().strftime('%Y-%m-%d')
        streak = 0
        magnitudes = []
        if events and events[0]['date'] == today:
            streak = 1
            magnitudes.append(events[0]['magnitude'])
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
        self.history['overrides'].append({'date': date, 'reason': reason, 'conditions': conditions})
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
                continue  # Skip if duplicate or future (unlikely)
            else:
                break  # Gap found
                
        return streak
    
    def get_recent_scores(self, days=30):
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return [s for s in self.history['scores'] if s['date'] >= cutoff]
    
    def had_extreme_score_recently(self, threshold=30, days=30):
        recent = self.get_recent_scores(days)
        if not recent:
            return False
        return min(s['score'] for s in recent) < threshold
    
    def get_override_start_date(self):
        """Get the date when current override started"""
        if not self.history.get('overrides'):
            return None
        # Get most recent override
        recent_overrides = sorted(self.history['overrides'], key=lambda x: x['date'], reverse=True)
        if recent_overrides:
            return recent_overrides[0]['date']
        return None
    
    def add_drift_snapshot(self, date, total_drift, category_drifts):
        """Store daily portfolio drift snapshot"""
        if 'drift_history' not in self.history:
            self.history['drift_history'] = []
        
        entry = {
            'date': date,
            'total_drift': total_drift,
            'categories': category_drifts
        }
        
        # Remove existing entry for same date (in case of re-run)
        self.history['drift_history'] = [d for d in self.history['drift_history'] if d['date'] != date]
        self.history['drift_history'].append(entry)
        
        # Keep last 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['drift_history'] = [d for d in self.history['drift_history'] if d['date'] >= cutoff_date]
    
    def get_drift_trend(self, days=7):
        """Get drift trend over last N days"""
        if 'drift_history' not in self.history or not self.history['drift_history']:
            return None
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent = sorted(
            [d for d in self.history['drift_history'] if d['date'] >= cutoff],
            key=lambda x: x['date']
        )
        
        if len(recent) < 2:
            return None
        
        # Calculate trend (improving = drift decreasing)
        first_drift = recent[0]['total_drift']
        last_drift = recent[-1]['total_drift']
        change = last_drift - first_drift
        change_pct = (change / first_drift * 100) if first_drift > 0 else 0
        
        return {
            'history': recent,
            'first_drift': first_drift,
            'last_drift': last_drift,
            'change': change,
            'change_pct': change_pct,
            'improving': change < 0,  # Drift decreasing = improving
            'days': len(recent)
        }
    
    def get_score_trend(self, days=7):
        """Get risk score trend with regime changes"""
        if not self.history.get('scores'):
            return None
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent = sorted(
            [s for s in self.history['scores'] if s['date'] >= cutoff],
            key=lambda x: x['date']
        )
        
        if len(recent) < 2:
            return None
        
        # Calculate score change
        first_score = recent[0]['score']
        last_score = recent[-1]['score']
        change = last_score - first_score
        
        # Map scores to regimes
        def get_regime(score):
            if score >= 90: return 'ALL CLEAR'
            elif score >= 75: return 'NORMAL'
            elif score >= 60: return 'ELEVATED'
            elif score >= 40: return 'HIGH RISK'
            else: return 'EXTREME RISK'
        
        first_regime = get_regime(first_score)
        last_regime = get_regime(last_score)
        regime_changed = first_regime != last_regime
        
        # Track key signal changes
        signal_changes = {}
        if 'vix' in recent[0] and 'vix' in recent[-1]:
            vix_change = recent[-1]['vix'] - recent[0]['vix']
            vix_pct = (vix_change / recent[0]['vix'] * 100) if recent[0]['vix'] > 0 else 0
            signal_changes['vix'] = {'change': vix_change, 'pct': vix_pct, 'first': recent[0]['vix'], 'last': recent[-1]['vix']}
        
        return {
            'history': recent,
            'first_score': first_score,
            'last_score': last_score,
            'change': change,
            'improving': change > 0,  # Score increasing = improving
            'first_regime': first_regime,
            'last_regime': last_regime,
            'regime_changed': regime_changed,
            'signal_changes': signal_changes,
            'days': len(recent)
        }
    
    def days_since_override_start(self):
        """Calculate days since override activated"""
        start_date = self.get_override_start_date()
        if not start_date:
            return 0
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            return (datetime.now() - start).days
        except:
            return 0

# =============================================================================
# RISK DASHBOARD - v1.8 with 2026 Portfolio Mapping
# =============================================================================

class RiskDashboard:
    # Symbol to category mapping for IBKR positions (from fetch-ibkr-positions-dashboard.xlsx)
    SYMBOL_MAPPING = {
        'global_core': ['82846', 'DHL', 'ES3', 'VWRA', 'VWCE', 'VT', 'VXUS'],
        'growth_engine': ['CSNDX', 'CTEC', 'HEAL', 'INRA', 'LOCK'],
        'income_strategy': [
            'SPY', 'QQQ', 'ADBE', 'AMD', 'CRM', 'CSCO', 'ORCL', 'COST', 'PEP', 'WMT', 
            'XOM', 'JPM', 'V', 'LLY', 'UNH', 'AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 
            'NVDA', 'TSLA'
        ],
        'alpha_sniper': [],  # Theme stocks - anything not in above categories
        'alpha_hedge': [],  # QQQ puts - detected from options
        'gold': ['GSD', 'GLD', 'IAU'],
    }
    
    def __init__(self):
        self.data = {}
        self.scores = {}
        self.alerts = []
        self.timestamp = datetime.now()
        self.history_manager = HistoricalDataManager()
        self.v_recovery_active = False
        self.v_recovery_reason = None
        self.missing_signals = []
        self.actual_positions = None
    
    # [DATA FETCHING METHODS - Keep all from v1.7]
    def _get_sp100_tickers(self):
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
            'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'CSCO', 'ABT', 'ACN',
            'DHR', 'VZ', 'ADBE', 'NKE', 'TXN', 'NEE', 'PM', 'LIN', 'CRM',
            'ORCL', 'UNP', 'DIS', 'BMY', 'CMCSA', 'NFLX', 'WFC', 'UNH', 'AMD',
        ]
    
    def _fred_get(self, series, name):
        try:
            data = fred.get_series_latest_release(series)
            val = float(data.iloc[-1])
            print(f"   ✓ {name}: {val:.2f}")
            return val
        except Exception as e:
            print(f"   ✗ {name}: Error")
            self.missing_signals.append(name)
            return None
    
    def _yf_get(self, ticker, name):
        try:
            val = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
            print(f"   ✓ {name}: {val:.2f}")
            return float(val)
        except:
            print(f"   ✗ {name}: Error")
            self.missing_signals.append(name)
            return None
    
    def _fed_bs_yoy(self):
        try:
            bs = fred.get_series_latest_release('WALCL')
            yoy = ((bs.iloc[-1] - bs.iloc[-52]) / bs.iloc[-52]) * 100
            print(f"   ✓ Fed BS YoY: {yoy:.1f}%")
            return float(yoy)
        except:
            print(f"   ✗ Fed BS YoY: Error")
            self.missing_signals.append("Fed BS YoY")
            return None
    
    def _dxy_trend(self):
        try:
            hist = yf.Ticker('DX-Y.NYB').history(period='2mo')['Close']
            if len(hist) < 20:
                return None
            trend = ((hist.iloc[-1] - hist.rolling(20).mean().iloc[-1]) / hist.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ DXY Trend: {trend:.1f}%")
            return float(trend)
        except:
            print(f"   ✗ DXY Trend: Error")
            return None
    
    def _pct_above_ma(self, period):
        above, valid = 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='1y')
                if len(hist) >= period:
                    valid += 1
                    if hist['Close'].iloc[-1] > hist['Close'].rolling(period).mean().iloc[-1]:
                        above += 1
            except:
                pass
        if valid == 0:
            return None
        pct = (above / valid * 100)
        print(f"   ✓ % Above {period}-MA: {pct:.0f}% ({above}/{valid})")
        return pct
    
    def _pct_below_ma(self, period):
        below, valid = 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='1y')
                if len(hist) >= period:
                    valid += 1
                    if hist['Close'].iloc[-1] < hist['Close'].rolling(period).mean().iloc[-1]:
                        below += 1
            except:
                pass
        if valid == 0:
            return None
        pct = (below / valid * 100)
        print(f"   ✓ % Below {period}-MA: {pct:.0f}% ({below}/{valid})")
        return pct
    
    def _ad_line_status(self):
        try:
            spy = yf.Ticker('SPY').history(period='3mo')
            if len(spy) < 20:
                return None
            pct = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-20:].max()) / spy['Close'].iloc[-20:].max()) * 100
            status = 'Confirming' if pct >= -1 else 'Flat' if pct >= -5 else 'Diverging'
            print(f"   ✓ AD Line: {status} ({pct:.1f}% from 20d high)")
            return status
        except:
            print(f"   ✗ AD Line: Error")
            return None
    
    def _new_highs_lows(self):
        highs, lows, valid = 0, 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='3mo')
                if len(hist) >= 52:
                    valid += 1
                    cur = hist['Close'].iloc[-1]
                    if cur >= hist['Close'].max() * 0.995:
                        highs += 1
                    elif cur <= hist['Close'].min() * 1.005:
                        lows += 1
            except:
                pass
        if valid == 0:
            return None
        net = highs - lows
        print(f"   ✓ New H-L: {net:+d} (H:{highs} L:{lows})")
        return net
    
    def _sector_rotation(self):
        try:
            xlu = yf.Ticker('XLU').history(period='2mo')['Close']
            xlk = yf.Ticker('XLK').history(period='2mo')['Close']
            if len(xlu) < 20 or len(xlk) < 20:
                return None
            ratio = xlu / xlk
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ XLU/XLK: {trend:+.1f}%")
            return float(trend)
        except:
            print(f"   ✗ XLU/XLK: Error")
            return None
    
    def _gold_spy_ratio(self):
        try:
            gld = yf.Ticker('GLD').history(period='2mo')['Close']
            spy = yf.Ticker('SPY').history(period='2mo')['Close']
            if len(gld) < 20 or len(spy) < 20:
                return None
            ratio = gld / spy
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ GLD/SPY: {trend:+.1f}%")
            return float(trend)
        except:
            print(f"   ✗ GLD/SPY: Error")
            return None
    
    def _vix_structure(self):
        try:
            vxx = yf.Ticker('VXX').history(period='5d')['Close'].iloc[-1]
            vixy = yf.Ticker('VIXY').history(period='5d')['Close'].iloc[-1]
            ratio = vixy / vxx
            if ratio > 1.03:
                struct = 'Contango'
                magnitude_pct = (ratio - 1.0) * 100
            elif ratio < 0.97:
                struct = 'Backwardation'
                magnitude_pct = (1.0 - ratio) * 100
            else:
                struct = 'Flat'
                magnitude_pct = 0.0
            streak_info = ""
            if struct == 'Backwardation':
                streak, avg_mag = self.history_manager.get_backwardation_streak()
                if streak > 0:
                    streak_info = f" Day {streak}"
                    self.history_manager.add_backwardation_event(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        vixy_vxx_ratio=ratio,
                        magnitude_pct=magnitude_pct
                    )
            print(f"   ✓ VIX Struct: {struct}{streak_info} (ratio={ratio:.3f})")
            return struct, ratio, magnitude_pct
        except:
            print(f"   ✗ VIX Struct: Error")
            return None, None, None
    
    def _fear_greed(self):
        if self.data.get('vix') is None:
            return None
        try:
            vix = self.data['vix']
            if vix < 10: vix = 10
            if vix > 50: vix = 50
            score = 100 - ((vix - 10) * 2.5)
            score = max(0, min(100, score))
            print(f"   ✓ Fear/Greed: {score:.0f}/100")
            return float(score)
        except:
            return None
    
    def fetch_all_data(self):
        print("\n📊 Fetching 14 indicators...\n")
        self.sample_tickers = self._get_sp100_tickers()
        self.missing_signals = []
        
        self.data = {
            'hy_spread': self._fred_get('BAMLH0A0HYM2', 'HY Spread'),
            'fed_bs_yoy': self._fed_bs_yoy(),
            'ted_spread': self._fred_get('TEDRATE', 'TED Spread'),
            'dxy_trend': self._dxy_trend(),
            'pct_above_50ma': self._pct_above_ma(50),
            'pct_below_200ma': self._pct_below_ma(200),
            'ad_line': self._ad_line_status(),
            'new_hl': self._new_highs_lows(),
            'sector_rot': self._sector_rotation(),
            'gold_spy': self._gold_spy_ratio(),
            'yield_curve': self._fred_get('T10Y2Y', 'Yield Curve'),
            'vix': self._yf_get('^VIX', 'VIX'),
        }
        
        vix_struct, vixy_vxx_ratio, vix_magnitude = self._vix_structure()
        self.data['vix_struct'] = vix_struct
        self.data['vixy_vxx_ratio'] = vixy_vxx_ratio
        self.data['vix_magnitude'] = vix_magnitude
        self.data['fear_greed'] = self._fear_greed()
        
        valid = sum(1 for v in self.data.values() if v is not None)
        print(f"\n✅ Fetched {valid}/14 signals successfully\n")
        return self.data
    
    def calculate_scores(self):
        d = self.data
        s1 = self._score_range(d.get('hy_spread'), [(3,20),(4,16),(4.5,12),(5.5,6)], 0)
        s2 = self._score_range(d.get('fed_bs_yoy'), [(10,15),(2,12),(-2,9),(-10,4)], 0)
        s3 = self._score_range(d.get('ted_spread'), [(0.3,10),(0.5,8),(0.75,5),(1,2)], 0)
        s4 = self._score_range(d.get('dxy_trend'), [(-3,5),(-1,4),(1,3),(3,1)], 0)
        s5 = self._score_range(d.get('pct_above_50ma'), [(75,12),(65,10),(55,7),(45,4),(35,2)], 0)
        s6 = self._score_range(d.get('pct_below_200ma'), [(15,10),(25,8),(35,6),(50,3),(65,1)], 0, inverse=True)
        s7 = {'Confirming':5, 'Flat':2, 'Diverging':0}.get(d.get('ad_line'), 0)
        s8 = self._score_range(d.get('new_hl'), [(10,3),(5,2.5),(0,2),(-5,1),(-10,0.5)], 0)
        s9 = self._score_range(d.get('sector_rot'), [(-5,6),(-2,5),(2,4),(5,2)], 0)
        s10 = self._score_range(d.get('gold_spy'), [(-3,5),(-1,4),(1,3),(3,1)], 0)
        s11 = {'Contango':4, 'Flat':2, 'Backwardation':0}.get(d.get('vix_struct'), 0)
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
        }
        return self.scores
    
    def _score_range(self, val, thresholds, default, inverse=False):
        if val is None:
            return default
        for thresh, score in thresholds:
            if (val < thresh if not inverse else val > thresh):
                return score
        return default
    
    # =============================================================================
    # IBKR POSITION INTEGRATION
    # =============================================================================
    
    def load_actual_positions(self):
        """Load actual positions from IBKR fetch-ibkr-positions.xlsx"""
        try:
            import pandas as pd
            from pathlib import Path
            
            excel_path = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'
            dashboard_path = Path(__file__).parent / 'fetch-ibkr-positions-dashboard.xlsx'
            
            if not excel_path.exists():
                return None
            
            # Read both accounts
            df_hk = pd.read_excel(excel_path, sheet_name='PositionsHK')
            df_al = pd.read_excel(excel_path, sheet_name='PositionsAL')
            
            # Extract cash from IBKR positions (auto-detected from fetch-ibkr-positions.py)
            cash_hk = df_hk[df_hk['AssetClass'] == 'CASH']['PositionValueUSD'].sum() if 'CASH' in df_hk['AssetClass'].values else 0
            cash_al = df_al[df_al['AssetClass'] == 'CASH']['PositionValueUSD'].sum() if 'CASH' in df_al['AssetClass'].values else 0
            
            if cash_hk > 0 or cash_al > 0:
                print(f"   📊 Cash auto-detected from IBKR: HK ${cash_hk:,.0f}, AL ${cash_al:,.0f}")
            
            # Combine and calculate total portfolio value (including cash)
            total_value = df_hk['PositionValueUSD'].sum() + df_al['PositionValueUSD'].sum()
            
            if total_value == 0:
                return None
            
            # Categorize positions
            positions = {
                'global_core': 0,
                'growth_engine': 0,
                'income_strategy': 0,
                'alpha_sniper': 0,
                'alpha_hedge': 0,
                'gold': 0,
                'cash': 0,
                'other': 0,
                'total': total_value
            }
            
            # First pass: Identify multi-leg option strategies (spreads/iron condors)
            # Group options by underlying + expiry to detect spreads
            multi_leg_strategies = {}
            for df in [df_hk, df_al]:
                for _, row in df.iterrows():
                    symbol = str(row['Symbol']).strip()
                    asset_class = row.get('AssetClass', '')
                    
                    if asset_class in ['OPT', 'FOP']:
                        # Extract underlying (e.g., EW2G6 from "EW2G6 P6525")
                        underlying = symbol.split()[0] if ' ' in symbol else symbol[:6]
                        expiry = row.get('Expiry', '')
                        key = f"{underlying}_{expiry}"
                        
                        if key not in multi_leg_strategies:
                            multi_leg_strategies[key] = {'legs': [], 'has_short': False}
                        
                        multi_leg_strategies[key]['legs'].append(symbol)
                        if row.get('Side', '') == 'Short':
                            multi_leg_strategies[key]['has_short'] = True
            
            # Identify spread strategies (2+ legs on same underlying)
            spread_underlyings = {k.split('_')[0] for k, v in multi_leg_strategies.items() if len(v['legs']) >= 2 and v['has_short']}
            
            # Second pass: Categorize positions
            for df in [df_hk, df_al]:
                for _, row in df.iterrows():
                    symbol = str(row['Symbol']).strip()
                    value = row['PositionValueUSD']
                    asset_class = row.get('AssetClass', '')
                    
                    # Get option metadata
                    side = row.get('Side', '')
                    put_call = row.get('Put/Call', '')
                    
                    # Categorize stocks by symbol mapping first
                    categorized = False
                    for category, symbols in self.SYMBOL_MAPPING.items():
                        if symbol in symbols:
                            positions[category] += value
                            categorized = True
                            break
                    
                    # Options categorization logic
                    if not categorized and asset_class in ['OPT', 'FOP']:
                        underlying = symbol.split()[0] if ' ' in symbol else symbol[:6]
                        
                        # Rule 1: Multi-leg spreads with shorts = Income Strategy (all legs)
                        if underlying in spread_underlyings:
                            positions['income_strategy'] += value
                            categorized = True
                        
                        # Rule 2: Single-leg short options (CSPs/covered calls) = Income Strategy
                        elif side == 'Short':
                            positions['income_strategy'] += value
                            categorized = True
                        
                        # Rule 3: Single-leg long puts (not part of spread) = Alpha Hedge
                        elif side == 'Long' and put_call == 'P':
                            positions['alpha_hedge'] += value
                            categorized = True
                        
                        # Rule 4: Long calls on income tickers = Income Strategy (e.g., LEAPS)
                        elif side == 'Long' and put_call == 'C':
                            for income_ticker in self.SYMBOL_MAPPING['income_strategy']:
                                if income_ticker in symbol:
                                    positions['income_strategy'] += value
                                    categorized = True
                                    break
                            
                            # If not income ticker, treat as Alpha Sniper (speculative)
                            if not categorized:
                                positions['alpha_sniper'] += value
                                categorized = True
                    
                    # Check for cash
                    if not categorized and asset_class == 'CASH':
                        positions['cash'] += value
                        categorized = True
                    if not categorized and asset_class == 'STK':
                        positions['alpha_sniper'] += value
                        categorized = True
                    
                    # Everything else goes to 'other'
                    if not categorized:
                        positions['other'] += value
                        print(f"   ⚠️  UNCATEGORIZED: {symbol} (${value:,.0f}) - {asset_class}")
            
            # Add cash from dashboard
            positions['cash'] += cash_hk + cash_al
            
            # Store raw position details for rebalancing recommendations
            positions['position_details'] = {
                'total_value': total_value,
                'by_category': {},
                'by_symbol': {}
            }
            
            # Recalculate to capture position details by symbol
            for df in [df_hk, df_al]:
                for _, row in df.iterrows():
                    symbol = str(row['Symbol']).strip()
                    value = row['PositionValueUSD']
                    asset_class = row.get('AssetClass', '')
                    
                    if asset_class == 'STK' and abs(value) > 1:
                        positions['position_details']['by_symbol'][symbol] = {
                            'value': value,
                            'asset_class': asset_class
                        }
            
            # Convert to percentages
            for key in positions:
                if key != 'total' and key != 'position_details':
                    positions[key] = positions[key] / total_value
            
            # Combine alpha categories (should be ~5% total per dashboard)
            positions['alpha_insurance'] = positions['alpha_sniper'] + positions['alpha_hedge']
            
            # Combine gold + cash into reserves
            positions['reserves'] = positions['gold'] + positions['cash']
            
            # Debug output
            print(f"\n📊 IBKR POSITIONS LOADED:")
            print(f"   Total Portfolio Value: ${total_value:,.0f}")
            print(f"   Global Core: {positions['global_core']*100:.1f}%")
            print(f"   Growth Engine: {positions['growth_engine']*100:.1f}%")
            print(f"   Income Strategy: {positions['income_strategy']*100:.1f}%")
            print(f"   Alpha & Insurance: {positions['alpha_insurance']*100:.1f}%")
            print(f"     ├─ Sniper (themes): {positions['alpha_sniper']*100:.1f}%")
            print(f"     └─ Hedge (QQQ puts): {positions['alpha_hedge']*100:.1f}%")
            print(f"   Reserves: {positions['reserves']*100:.1f}%")
            print(f"     ├─ Gold: {positions['gold']*100:.1f}%")
            print(f"     └─ Cash: {positions['cash']*100:.1f}%")
            print(f"   Other (uncategorized): {positions['other']*100:.1f}%\n")
            
            return positions
            
        except Exception as e:
            print(f"   ⚠️  Could not load IBKR positions: {e}")
            return None
    
    def compare_to_target(self, target_allocation):
        """Compare actual positions to target allocation"""
        if not self.actual_positions:
            return None
        
        actual = self.actual_positions
        drift = {}
        total_drift = 0
        alerts = []
        
        # Calculate drift for each category
        print(f"🎯 DRIFT CALCULATION:")
        for category in ['global_core', 'growth_engine', 'income_strategy', 'alpha_insurance', 'reserves']:
            target_pct = target_allocation.get(category, 0)
            actual_pct = actual.get(category, 0)
            diff = actual_pct - target_pct
            drift[category] = diff
            total_drift += abs(diff)
            
            print(f"   {category}: Actual {actual_pct*100:.1f}% - Target {target_pct*100:.1f}% = {diff*100:+.1f}% (abs: {abs(diff)*100:.1f}%)")
            
            # Flag significant drifts (>3%)
            if abs(diff) > 0.03:
                direction = 'overweight' if diff > 0 else 'underweight'
                alerts.append(f"{category.replace('_', ' ').title()}: {direction} by {abs(diff)*100:.0f}%")
        
        print(f"   ───────────────────────────────────")
        print(f"   TOTAL DRIFT: {total_drift*100:.1f}%\n")
        
        # Save drift snapshot to history
        today = datetime.now().strftime('%Y-%m-%d')
        self.history_manager.add_drift_snapshot(today, total_drift, drift)
        self.history_manager.save_history()
        
        return {
            'drift': drift,
            'total_drift': total_drift,
            'alerts': alerts,
            'show': total_drift > 0.05  # Only show if total drift > 5%
        }
    
    def generate_rebalancing_recommendations(self, target_allocation, drift_analysis):
        """Generate specific buy/sell recommendations to reach target allocation"""
        if not self.actual_positions or not drift_analysis['show']:
            return None
        
        actual = self.actual_positions
        total_value = actual.get('position_details', {}).get('total_value', 0)
        
        if total_value == 0:
            return None
        
        recommendations = {
            'sells': [],
            'buys': [],
            'total_to_sell': 0,
            'total_to_buy': 0
        }
        
        # Identify what to sell (overweight categories)
        for category in ['global_core', 'growth_engine', 'income_strategy', 'alpha_insurance', 'reserves']:
            drift = drift_analysis['drift'].get(category, 0)
            
            if drift > 0.03:  # Overweight by >3%
                amount = drift * total_value
                recommendations['sells'].append({
                    'category': category,
                    'current_pct': actual[category] * 100,
                    'target_pct': target_allocation[category] * 100,
                    'drift_pct': drift * 100,
                    'amount': amount
                })
                recommendations['total_to_sell'] += amount
        
        # Identify what to buy (underweight categories)
        for category in ['global_core', 'growth_engine', 'income_strategy', 'alpha_insurance', 'reserves']:
            drift = drift_analysis['drift'].get(category, 0)
            
            if drift < -0.03:  # Underweight by >3%
                amount = abs(drift) * total_value
                recommendations['buys'].append({
                    'category': category,
                    'current_pct': actual[category] * 100,
                    'target_pct': target_allocation[category] * 100,
                    'drift_pct': drift * 100,
                    'amount': amount
                })
                recommendations['total_to_buy'] += amount
        
        return recommendations if recommendations['sells'] or recommendations['buys'] else None
    
    def analyze_options_positions(self):
        """Analyze income strategy options for expiry and urgency"""
        try:
            import pandas as pd
            from pathlib import Path
            from datetime import datetime, timedelta
            
            excel_path = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'
            if not excel_path.exists():
                return None
            
            df_hk = pd.read_excel(excel_path, sheet_name='PositionsHK')
            df_al = pd.read_excel(excel_path, sheet_name='PositionsAL')
            
            analysis = {
                'csps': [],
                'covered_calls': [],
                'spreads': [],
                'stocks': [],
                'total_premium': 0,
                'days_to_nearest_expiry': None
            }
            
            today = datetime.now()
            nearest_expiry = None
            
            # Analyze all options
            for df in [df_hk, df_al]:
                opts = df[df['AssetClass'].isin(['OPT', 'FOP'])]
                for _, row in opts.iterrows():
                    symbol = row['Symbol']
                    side = row.get('Side', '')
                    put_call = row.get('Put/Call', '')
                    value = row['PositionValueUSD']
                    expiry = row.get('Expiry', '')
                    
                    # Calculate days to expiry
                    days_to_expiry = None
                    if pd.notna(expiry):
                        try:
                            expiry_date = pd.to_datetime(expiry)
                            days_to_expiry = (expiry_date - today).days
                            
                            if nearest_expiry is None or days_to_expiry < nearest_expiry:
                                nearest_expiry = days_to_expiry
                        except:
                            pass
                    
                    # Categorize
                    if side == 'Short':
                        if put_call == 'P':
                            analysis['csps'].append({
                                'symbol': symbol,
                                'value': value,
                                'days_to_expiry': days_to_expiry
                            })
                        elif put_call == 'C':
                            analysis['covered_calls'].append({
                                'symbol': symbol,
                                'value': value,
                                'days_to_expiry': days_to_expiry
                            })
                        analysis['total_premium'] += abs(value)
                
                # Get stocks in income strategy
                income_tickers = self.SYMBOL_MAPPING['income_strategy']
                stocks = df[(df['AssetClass'] == 'STK') & (df['Symbol'].isin(income_tickers))]
                for _, row in stocks.iterrows():
                    analysis['stocks'].append({
                        'symbol': row['Symbol'],
                        'value': row['PositionValueUSD']
                    })
            
            analysis['days_to_nearest_expiry'] = nearest_expiry
            return analysis
            
        except Exception as e:
            print(f"   ⚠️  Could not analyze options: {e}")
            return None
    
    # =============================================================================
    # NEW v1.8: 2026 PORTFOLIO ALLOCATION LOGIC
    # =============================================================================
    
    def get_portfolio_allocation(self):
        """
        Map risk score to specific portfolio adjustments
        Returns: dict with position-specific guidance
        """
        score = self.scores['total']
        base = PORTFOLIO_2026['BASE_ALLOCATION']
        
        # Score-based allocation
        if score >= 90:  # ALL CLEAR
            base_allocation = {
                'regime': '★★★★★ ALL CLEAR',
                'global_core': base['global_core'],
                'growth_engine': base['growth_engine'],
                'income_strategy': base['income_strategy'],
                'alpha_insurance': base['alpha_insurance'],
                'reserves': base['reserves'],
                'gold_pct': 0.03,  # 3% of reserves in gold
                'cash_pct': 0.07,  # 7% in cash
                'stops': '15-20%',
                'options_guidance': 'Sell CSPs at 30-45 DTE, 15-20 delta on GOOGL, PEP, V',
                'action': 'FULL DEPLOYMENT - Run base allocation'
            }
        
        elif score >= 75:  # NORMAL
            base_allocation = {
                'regime': '★★★★☆ NORMAL',
                'global_core': base['global_core'],
                'growth_engine': base['growth_engine'] * 0.9,  # Slightly reduce growth
                'income_strategy': base['income_strategy'] * 0.9,  # More conservative
                'alpha_insurance': base['alpha_insurance'],
                'reserves': base['reserves'] + 0.06,  # Raise reserves to 16%
                'gold_pct': 0.04,  # 4% in gold
                'cash_pct': 0.12,  # 12% in cash
                'stops': '12-15%',
                'options_guidance': 'Tighter strikes: 10-15 delta CSPs, 30 DTE',
                'action': 'STAY COURSE - Tighten stops, be selective on new CSPs'
            }
        
        elif score >= 60:  # ELEVATED
            base_allocation = {
                'regime': '★★★☆☆ ELEVATED',
                'global_core': base['global_core'],
                'growth_engine': base['growth_engine'] * 0.7,  # Cut growth significantly
                'income_strategy': base['income_strategy'] * 0.5,  # Very defensive options
                'alpha_insurance': base['alpha_insurance'] * 2,  # Double alpha/hedge (10%)
                'reserves': 0.25,  # Raise reserves to 25%
                'gold_pct': 0.10,  # 10% in gold
                'cash_pct': 0.15,  # 15% in cash
                'stops': '10-12%',
                'options_guidance': 'DEFENSIVE: Far OTM CSPs (5-10 delta), close losing positions',
                'action': 'REDUCE RISK - Cut growth/income, raise reserves and hedge'
            }
        
        elif score >= 40:  # HIGH RISK
            base_allocation = {
                'regime': '★★☆☆☆ HIGH RISK',
                'global_core': base['global_core'] * 0.8,  # Trim core slightly
                'growth_engine': base['growth_engine'] * 0.3,  # Skeleton growth
                'income_strategy': 0,  # Exit all income strategies
                'alpha_insurance': base['alpha_insurance'] * 3,  # 15% alpha/hedge
                'reserves': 0.40,  # 40% reserves
                'gold_pct': 0.15,  # 15% in gold
                'cash_pct': 0.25,  # 25% in cash
                'stops': '8-10%',
                'options_guidance': 'CLOSE POSITIONS: Roll losing CSPs, collect premium and exit',
                'action': 'GO DEFENSIVE - Major risk reduction, protect capital'
            }
        
        else:  # EXTREME (<40)
            base_allocation = {
                'regime': '★☆☆☆☆ EXTREME RISK',
                'global_core': base['global_core'] * 0.5,  # Cut core in half
                'growth_engine': 0,  # Exit all growth
                'income_strategy': 0,  # No options
                'alpha_insurance': base['alpha_insurance'] * 5,  # 25% alpha/hedge
                'reserves': 0.55,  # 55% reserves
                'gold_pct': 0.20,  # 20% in gold
                'cash_pct': 0.35,  # 35% in cash
                'stops': '5-8%',
                'options_guidance': 'CLOSE ALL: Exit CSPs at any reasonable price, stop selling premium',
                'action': 'MAX DEFENSE - Capital preservation mode'
            }
        
        # Apply V-Recovery override if active
        if self.v_recovery_active and base_allocation:
            return self._apply_v_recovery_to_portfolio(base_allocation)
        return base_allocation if base_allocation else self.get_portfolio_allocation()  # Fallback
    
    def _apply_v_recovery_to_portfolio(self, base_alloc):
        """Apply V-Recovery override - cut reserves by 50% and redeploy"""
        old_reserves = base_alloc['reserves']
        new_reserves = old_reserves * 0.5
        freed_capital = old_reserves - new_reserves
        
        # Redistribute freed capital proportionally to core/growth/income
        total_active = base_alloc['global_core'] + base_alloc['growth_engine'] + base_alloc['income_strategy']
        
        if total_active > 0:
            boost_factor = 1 + (freed_capital / total_active)
            return {
                **base_alloc,
                'regime': base_alloc['regime'] + ' + V-RECOVERY',
                'global_core': base_alloc['global_core'] * boost_factor,
                'growth_engine': base_alloc['growth_engine'] * boost_factor,
                'income_strategy': base_alloc['income_strategy'] * boost_factor,
                'reserves': new_reserves,
                'gold_pct': base_alloc['gold_pct'],  # Keep gold proportion
                'cash_pct': base_alloc['cash_pct'] * 0.5,  # Cut cash proportion
                'action': base_alloc['action'] + ' | V-RECOVERY: Reserves cut 50%, redeployed to core/growth/income'
            }
        else:
            return base_alloc
    
    # =============================================================================
    # V-RECOVERY DETECTION with KILL-SWITCH
    # =============================================================================
    
    def check_v_recovery_trigger(self):
        if not CONFIG['V_RECOVERY_ENABLED']:
            return False, None
        
        try:
            spy = yf.Ticker('SPY').history(period='2mo')
            if len(spy) < CONFIG['V_RECOVERY_SPY_DAYS']:
                return False, None
            
            # Check if override already active and apply kill-switch
            # Use consecutive streak logic (not calendar days) to match v1.7 behavior
            override_streak = self.history_manager.get_override_streak()
            if override_streak >= 5:
                current_score = self.scores['total']
                if current_score < 60:
                    print(f"⚠️ KILL-SWITCH: Override active {override_streak} consecutive days but score={current_score:.1f} < 60. ABORTING.")
                    return False, f"KILL-SWITCH activated: {override_streak} days active, score={current_score:.1f}"
            
            had_extreme = self.history_manager.had_extreme_score_recently(
                threshold=CONFIG['V_RECOVERY_SCORE_THRESHOLD'],
                days=CONFIG['V_RECOVERY_LOOKBACK']
            )
            
            if not had_extreme:
                return False, None
            
            lookback = CONFIG['V_RECOVERY_SPY_DAYS']
            spy_gain = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-lookback]) / 
                       spy['Close'].iloc[-lookback] * 100)
            
            if spy_gain < CONFIG['V_RECOVERY_SPY_GAIN']:
                return False, None
            
            recent_scores = self.history_manager.get_recent_scores(CONFIG['V_RECOVERY_LOOKBACK'])
            if not recent_scores or self.data.get('vix') is None:
                return False, None
            
            vix_high = max(s['vix'] for s in recent_scores if s.get('vix'))
            vix_drop = vix_high - self.data['vix']
            
            if vix_drop < CONFIG['V_RECOVERY_VIX_DROP']:
                return False, None
            
            if self.data.get('hy_spread') is not None:
                credit_stable = self.data['hy_spread'] < 6.0
                if not credit_stable:
                    return False, None
            
            reason = (
                f"V-Recovery Triggered:\n"
                f"  • Score <{CONFIG['V_RECOVERY_SCORE_THRESHOLD']} recently\n"
                f"  • SPY +{spy_gain:.1f}% in {lookback} days\n"
                f"  • VIX dropped {vix_drop:.1f} pts\n"
                f"  • Credit stable ({self.data['hy_spread']:.2f}%)"
            )
            
            return True, reason
            
        except Exception as e:
            print(f"   ⚠️  V-Recovery check failed: {e}")
            return False, None
    
    # =============================================================================
    # DIVERGENCE DETECTION
    # =============================================================================
    
    def detect_divergences(self):
        self.alerts = []
        d = self.data
        
        if d.get('vix') and d['vix'] < 15:
            if (d.get('hy_spread') and d['hy_spread'] > 4.5) or \
               (d.get('pct_above_50ma') and d['pct_above_50ma'] < 50):
                self.alerts.append({
                    'type': 'HIDDEN DANGER',
                    'severity': 'CRITICAL',
                    'icon': '🚨🚨🚨',
                    'msg': 'VIX CALM BUT CREDIT/BREADTH DETERIORATING',
                    'action': 'REDUCE RISK NOW'
                })
        
        if (d.get('fed_bs_yoy') and d['fed_bs_yoy'] < -5) and \
           (d.get('dxy_trend') and d['dxy_trend'] > 3):
            self.alerts.append({
                'type': 'LIQUIDITY DRAIN',
                'severity': 'HIGH',
                'icon': '🚨🚨',
                'msg': 'FED CONTRACTING + DOLLAR SURGING',
                'action': 'REDUCE RISK ASSETS 20-30%'
            })
        
        if (d.get('hy_spread') and d['hy_spread'] > 5) or \
           (d.get('ted_spread') and d['ted_spread'] > 0.8):
            self.alerts.append({
                'type': 'CREDIT WARNING',
                'severity': 'HIGH',
                'icon': '🚨🚨',
                'msg': 'CREDIT MARKETS PRICING STRESS',
                'action': 'GO DEFENSIVE'
            })
        
        if d.get('vix_struct') == 'Backwardation':
            streak, avg_mag = self.history_manager.get_backwardation_streak()
            if streak >= 5:
                self.alerts.append({
                    'type': 'BACKWARDATION PERSISTING',
                    'severity': 'CRITICAL',
                    'icon': '🚨🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak}',
                    'action': 'TIGHTEN STOPS, REDUCE TIER 3'
                })
            elif streak >= 3:
                self.alerts.append({
                    'type': 'BACKWARDATION PATTERN',
                    'severity': 'HIGH',
                    'icon': '🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak}',
                    'action': 'WATCH CREDIT & BREADTH'
                })
            elif streak >= 1 and d.get('vix') and d['vix'] < 16:
                self.alerts.append({
                    'type': 'HIDDEN TENSION',
                    'severity': 'MEDIUM',
                    'icon': '⚠️',
                    'msg': f'VIX CALM BUT BACKWARDATION DETECTED',
                    'action': 'INSTITUTIONS BUYING PROTECTION'
                })
        
        if self.v_recovery_active:
            self.alerts.append({
                'type': 'V-RECOVERY ACTIVE',
                'severity': 'INFO',
                'icon': '🚀',
                'msg': self.v_recovery_reason,
                'action': 'AGGRESSIVE RE-ENTRY'
            })
        
        if not self.alerts and self.scores['total'] >= 85:
            self.alerts.append({
                'type': 'ALL CLEAR',
                'severity': 'SAFE',
                'icon': '✅',
                'msg': 'HEALTHY MARKET CONDITIONS',
                'action': 'FULL DEPLOYMENT OK'
            })
        
        return self.alerts
    
    # =============================================================================
    # REPORTING with 2026 PORTFOLIO BREAKDOWN
    # =============================================================================
    
    def generate_report(self):
        score = self.scores['total']
        d = self.data
        
        # Get portfolio allocation
        portfolio = self.get_portfolio_allocation()
        
        # Check V-Recovery
        self.v_recovery_active, self.v_recovery_reason = self.check_v_recovery_trigger()
        if self.v_recovery_active:
            portfolio = self.get_portfolio_allocation()  # Recalc with override
        
        lines = [
            "🎯 RISK DASHBOARD v1.8",
            f"📅 {self.timestamp.strftime('%b %d, %Y @ %H:%M')}",
            "",
            f"📊 SCORE: {score:.1f}/100",
            f"🎚️ {portfolio['regime']}",
            "",
        ]
        
        # Load actual positions and compare to target
        self.actual_positions = self.load_actual_positions()
        drift_analysis = self.compare_to_target(portfolio) if self.actual_positions else None
        
        # Get rebalancing recommendations and options analysis
        rebalance_recs = self.generate_rebalancing_recommendations(portfolio, drift_analysis) if drift_analysis else None
        options_analysis = self.analyze_options_positions() if self.actual_positions else None
        
        # Get drift trend and score trend
        drift_trend = self.history_manager.get_drift_trend(days=7) if drift_analysis else None
        score_trend = self.history_manager.get_score_trend(days=7)
        
        # Portfolio allocation breakdown
        if drift_analysis and drift_analysis['show']:
            # Show actual vs target with action needed
            lines.extend(["💼 PORTFOLIO ALLOCATION (Actual → Target)"])
            
            categories = [
                ('Global Core', 'global_core'),
                ('Growth Engine', 'growth_engine'),
                ('Income Strategy', 'income_strategy'),
                ('Alpha & Insurance', 'alpha_insurance'),
                ('Reserves', 'reserves')
            ]
            
            for label, key in categories:
                target = portfolio[key] * 100
                actual = self.actual_positions[key] * 100
                diff = drift_analysis['drift'][key] * 100
                
                if abs(diff) > 3:
                    indicator = "⚠️" if abs(diff) > 5 else "⚡"
                    # Show action needed: negative diff means underweight (need to add +), positive means overweight (need to reduce -)
                    action = f"{-diff:+.0f}%"
                    lines.append(f"{label}: {actual:.0f}% → {target:.0f}% ({action} {indicator})")
                else:
                    lines.append(f"{label}: {actual:.0f}% → {target:.0f}%")
            
            # Show drift with trend if available
            drift_line = f"⚠️ DRIFT: {drift_analysis['total_drift']*100:.0f}% total"
            if drift_trend:
                if drift_trend['improving']:
                    trend_icon = "📉" if abs(drift_trend['change']) > 0.02 else "↘️"
                    drift_line += f" {trend_icon} ({abs(drift_trend['change']*100):.0f}% from {drift_trend['days']}d ago)"
                else:
                    trend_icon = "📈" if drift_trend['change'] > 0.02 else "↗️"
                    drift_line += f" {trend_icon} (+{drift_trend['change']*100:.0f}% from {drift_trend['days']}d ago)"
            
            lines.extend([
                "",
                drift_line,
                f"📋 {', '.join(drift_analysis['alerts'][:2])}",  # Show top 2 alerts
                ""
            ])
        else:
            # Show target allocation only
            lines.extend([
                "💼 PORTFOLIO ALLOCATION (Target)",
                f"Global Core: {portfolio['global_core']*100:.0f}%",
                f"Growth Engine: {portfolio['growth_engine']*100:.0f}%",
                f"Income Strategy: {portfolio['income_strategy']*100:.0f}%",
                f"Alpha & Insurance: {portfolio['alpha_insurance']*100:.0f}%",
                f"Reserves: {portfolio['reserves']*100:.0f}% (Gold: {portfolio['gold_pct']*100:.0f}%, Cash: {portfolio['cash_pct']*100:.0f}%)",
                ""
            ])
        
        lines.extend([
            f"🛡️ Stops: {portfolio['stops']}",
            f"📈 Options: {portfolio['options_guidance']}",
            "",
            f"💡 ACTION: {portfolio['action']}",
            "",
        ])
        
        # Add rebalancing recommendations if significant drift
        if rebalance_recs and (rebalance_recs['sells'] or rebalance_recs['buys']):
            lines.extend(["🔄 REBALANCING RECOMMENDATIONS"])
            
            if rebalance_recs['sells']:
                lines.append("SELL (Overweight):")
                for rec in rebalance_recs['sells'][:3]:  # Top 3
                    cat_name = rec['category'].replace('_', ' ').title()
                    lines.append(f"  • {cat_name}: ${rec['amount']/1000:.0f}k ({rec['drift_pct']:.0f}% over)")
            
            if rebalance_recs['buys']:
                lines.append("BUY (Underweight):")
                for rec in rebalance_recs['buys'][:3]:  # Top 3
                    cat_name = rec['category'].replace('_', ' ').title()
                    lines.append(f"  • {cat_name}: ${rec['amount']/1000:.0f}k ({abs(rec['drift_pct']):.0f}% under)")
            
            lines.append("")
        
        # Add options analysis if available
        if options_analysis:
            total_csps = len(options_analysis['csps'])
            total_ccs = len(options_analysis['covered_calls'])
            total_stocks = len(options_analysis['stocks'])
            days_to_expiry = options_analysis['days_to_nearest_expiry']
            
            if total_csps > 0 or total_ccs > 0 or total_stocks > 0:
                lines.extend(["📊 INCOME STRATEGY POSITIONS"])
                
                if total_csps > 0:
                    lines.append(f"  • CSPs: {total_csps} active")
                if total_ccs > 0:
                    lines.append(f"  • Covered Calls: {total_ccs} active")
                if total_stocks > 0:
                    stock_value = sum(s['value'] for s in options_analysis['stocks'])
                    lines.append(f"  • Stock Holdings: {total_stocks} positions (${stock_value/1000:.0f}k)")
                
                if days_to_expiry is not None:
                    urgency = "🔴 URGENT" if days_to_expiry <= 3 else "🟡 Soon" if days_to_expiry <= 7 else "🟢 OK"
                    lines.append(f"  • Nearest Expiry: {days_to_expiry} days {urgency}")
                
                lines.append("")
        
        # Tier scores
        lines.extend([
            "📈 TIER SCORES",
            f"T1: {self.scores['tier1']:.0f}/50 ({self.scores['tier1']/50*100:.0f}%)",
            f"T2: {self.scores['tier2']:.0f}/30 ({self.scores['tier2']/30*100:.0f}%)",
            f"T3: {self.scores['tier3']:.0f}/15 ({self.scores['tier3']/15*100:.0f}%)",
            f"T4: {self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            "",
        ])
        
        # Score trend (historical comparison)
        if score_trend and score_trend['days'] >= 2:
            lines.extend(["📊 RISK TREND ({} days)".format(score_trend['days'])])
            
            # Show score movement
            if score_trend['improving']:
                trend_icon = "📈" if score_trend['change'] > 5 else "↗️"
                lines.append(f"{trend_icon} Score: {score_trend['first_score']:.0f} → {score_trend['last_score']:.0f} (+{score_trend['change']:.0f} pts)")
            else:
                trend_icon = "📉" if score_trend['change'] < -5 else "↘️"
                lines.append(f"{trend_icon} Score: {score_trend['first_score']:.0f} → {score_trend['last_score']:.0f} ({score_trend['change']:.0f} pts)")
            
            # Show regime change if occurred
            if score_trend['regime_changed']:
                lines.append(f"⚠️ Regime: {score_trend['first_regime']} → {score_trend['last_regime']}")
            
            # Show key signal changes
            if 'vix' in score_trend['signal_changes']:
                vix = score_trend['signal_changes']['vix']
                if abs(vix['pct']) > 10:  # Only show if >10% change
                    direction = "↑" if vix['change'] > 0 else "↓"
                    lines.append(f"  • VIX: {vix['first']:.1f} → {vix['last']:.1f} ({direction}{abs(vix['pct']):.0f}%)")
            
            lines.append("")
        
        # Key signals
        lines.extend([
            "📊 KEY SIGNALS",
            f"HY Spread: {d.get('hy_spread', 'N/A'):.2f}%" if d.get('hy_spread') else "HY Spread: N/A",
            f"VIX: {d.get('vix', 'N/A'):.1f}" if d.get('vix') else "VIX: N/A",
        ])
        
        if d.get('vix_struct'):
            vix_line = f"VIX: {d['vix_struct']}"
            if d['vix_struct'] == 'Backwardation':
                streak, _ = self.history_manager.get_backwardation_streak()
                if streak > 0:
                    vix_line = f"⚠️ VIX: Back Day {streak}"
            lines.append(vix_line)
        
        lines.extend([
            f"% >50MA: {d.get('pct_above_50ma', 'N/A'):.0f}%" if d.get('pct_above_50ma') else "% >50MA: N/A",
            f"F&G: {d.get('fear_greed', 'N/A'):.0f}" if d.get('fear_greed') else "F&G: N/A",
            "",
        ])
        
        # Alerts
        if self.alerts:
            lines.append("🚨 ALERTS")
            for alert in self.alerts:
                lines.extend(["", f"{alert['icon']} {alert['type']}", f"{alert['msg']}", f"→ {alert['action']}"])
        
        return "\n".join(lines)
    
    # =============================================================================
    # AI CIO INTERPRETATIONS - Dual Analysis (Claude + Gemini)
    # =============================================================================
    
    def generate_claude_interpretation(self):
        """Claude CIO Analysis"""
        key = os.getenv('ANTHROPIC_API_KEY')
        if not key or 'YOUR_' in key:
            return None
        
        try:
            portfolio = self.get_portfolio_allocation()
            prompt = f"""You are the CIO analyzing today's risk dashboard for a $1M portfolio trader targeting 15% annual returns.

TODAY'S DATA:
Score: {self.scores['total']:.1f}/100
Regime: {portfolio['regime']}
Portfolio Allocation:
- Global Core (VWRA/ES3/DHL/82846): {portfolio['global_core']*100:.0f}%
- Growth Engine (CSNDX/CTEC/HEAL/INRA/LOCK): {portfolio['growth_engine']*100:.0f}%
- Income Strategy (Wheel on GOOGL/PEP/V): {portfolio['income_strategy']*100:.0f}%
- Alpha & Insurance (Sniper + QQQ Puts): {portfolio['alpha_insurance']*100:.0f}%
- Reserves: {portfolio['reserves']*100:.0f}% (Gold: {portfolio['gold_pct']*100:.0f}%, Cash: {portfolio['cash_pct']*100:.0f}%)
Action: {portfolio['action']}

Key Indicators:
- HY Spread: {self.data.get('hy_spread', 'N/A')}%
- VIX: {self.data.get('vix', 'N/A')}
- % Above 50MA: {self.data.get('pct_above_50ma', 'N/A')}%
- Breadth: {self.data.get('ad_line', 'N/A')}

Write brief CIO interpretation for mobile:
💭 HEADLINE (one line)
📊 SCORE QUALITY (tiers assessment)
👁️ WHAT I SEE (2-3 bullets)
🎯 REGIME (2 sentences)
💡 MY CALL (specific to positions)
🔄 FLIP TRIGGERS (specific)
⚡ BOTTOM LINE (one sentence)

<1200 chars, use numbers, be direct."""

            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]},
                timeout=30
            )
            if resp.status_code == 200:
                return f"🧠 CLAUDE CIO ANALYSIS\n📅 {self.timestamp.strftime('%b %d, %Y')}\n\n{resp.json()['content'][0]['text']}"
            return None
        except Exception as e:
            print(f"⚠️ Claude CIO Error: {e}")
            return None
    
    def generate_gemini_interpretation(self):
        """Gemini CIO Analysis - Second Opinion"""
        key = os.getenv('GEMINI_API_KEY')
        if not key or 'YOUR_' in key:
            return None
        
        try:
            portfolio = self.get_portfolio_allocation()
            prompt = f"""You are the Chief Investment Officer providing a second opinion on today's risk dashboard for a $1M portfolio targeting 15% annual returns.

TODAY'S MARKET SNAPSHOT:
Risk Score: {self.scores['total']:.1f}/100
Market Regime: {portfolio['regime']}

Current Portfolio:
- Global Core ETFs: {portfolio['global_core']*100:.0f}%
- Growth Engine: {portfolio['growth_engine']*100:.0f}%
- Income Strategy (Options): {portfolio['income_strategy']*100:.0f}%
- Alpha & Insurance: {portfolio['alpha_insurance']*100:.0f}%
- Reserves: {portfolio['reserves']*100:.0f}% (Gold {portfolio['gold_pct']*100:.0f}% | Cash {portfolio['cash_pct']*100:.0f}%)

Recommended Action: {portfolio['action']}

Key Market Indicators:
- High Yield Spread: {self.data.get('hy_spread', 'N/A')}% (credit stress)
- VIX: {self.data.get('vix', 'N/A')} (fear gauge)
- Stocks Above 50MA: {self.data.get('pct_above_50ma', 'N/A')}% (breadth)
- Market Breadth: {self.data.get('ad_line', 'N/A')}

Provide your CIO perspective (max 1000 chars) covering:
💭 HEADLINE: One-line market view
📊 SCORE INSIGHT: Quality assessment
👁️ KEY OBSERVATIONS: 2-3 critical points
🎯 REGIME CONTEXT: Market environment assessment
💡 PORTFOLIO STANCE: Specific position guidance
🔄 WATCH TRIGGERS: Conditions that would change your view
⚡ EXECUTIVE SUMMARY: Bottom line call

Be direct, use specific numbers, focus on actionable insights."""

            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if resp.status_code == 200:
                text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                return f"💎 GEMINI CIO ANALYSIS\n📅 {self.timestamp.strftime('%b %d, %Y')}\n\n{text}"
            return None
        except Exception as e:
            print(f"⚠️ Gemini CIO Error: {e}")
            return None
    
    # =============================================================================
    # MAIN EXECUTION
    # =============================================================================
    
    def run_assessment(self):
        print("\n" + "="*80)
        print("STARTING DAILY RISK ASSESSMENT v1.8 - 2026 PORTFOLIO")
        print("="*80)
        
        self.fetch_all_data()
        
        if self.missing_signals:
            print(f"\n❌ CRITICAL: {len(self.missing_signals)} missing signals")
            return None
        
        self.calculate_scores()
        
        # Save history
        try:
            spy_price = yf.Ticker('SPY').history(period='1d')['Close'].iloc[-1]
        except:
            spy_price = None
        
        self.history_manager.add_score(
            date=self.timestamp.strftime('%Y-%m-%d'),
            score=self.scores['total'],
            spy_price=spy_price,
            vix=self.data.get('vix'),
            vix_structure=self.data.get('vix_struct'),
            vixy_vxx_ratio=self.data.get('vixy_vxx_ratio')
        )
        
        # V-Recovery check
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
        
        # Save and send
        with open(f"risk_report_{self.timestamp.strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(report)
        self.history_manager.save_history()
        send_to_telegram(report)
        
        # Dual CIO interpretations (4-eye principle)
        claude_cio = self.generate_claude_interpretation()
        if claude_cio:
            print("\n" + claude_cio + "\n")
            send_to_telegram(claude_cio)
        
        gemini_cio = self.generate_gemini_interpretation()
        if gemini_cio:
            print("\n" + gemini_cio + "\n")
            send_to_telegram(gemini_cio)
        
        return self.scores['total']

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              INSTITUTIONAL RISK DASHBOARD v1.8                       ║
║         14 Signals + V-Recovery + 2026 Portfolio Mapping             ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    dashboard = RiskDashboard()
    dashboard.run_assessment()
    print("\n✅ Assessment complete.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
