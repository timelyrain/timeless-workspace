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
        'hedge': 0.05,            # QQQ puts (15% OTM)
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
    # Symbol to category mapping for IBKR positions
    SYMBOL_MAPPING = {
        'global_core': ['VWRA', 'VWCE', 'ES3', 'DHL', '82846', 'VT', 'VXUS'],
        'growth_engine': ['CSNDX', 'CTEC', 'HEAL', 'INRA', 'LOCK'],
        'income_strategy': ['GOOGL', 'PEP', 'V'],  # Only the underlying stocks for wheel
        'hedge': [],  # QQQ puts - will detect from AssetClass=OPT
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
            if not excel_path.exists():
                return None
            
            # Read both accounts
            df_hk = pd.read_excel(excel_path, sheet_name='PositionsHK')
            df_al = pd.read_excel(excel_path, sheet_name='PositionsAL')
            
            # Combine and calculate total portfolio value
            total_value = df_hk['PositionValueUSD'].sum() + df_al['PositionValueUSD'].sum()
            
            if total_value == 0:
                return None
            
            # Categorize positions
            positions = {
                'global_core': 0,
                'growth_engine': 0,
                'income_strategy': 0,
                'hedge': 0,
                'gold': 0,
                'cash': 0,
                'other': 0,
                'total': total_value
            }
            
            # Process both dataframes
            for df in [df_hk, df_al]:
                for _, row in df.iterrows():
                    symbol = str(row['Symbol']).strip()
                    value = row['PositionValueUSD']
                    asset_class = row.get('AssetClass', '')
                    
                    # Categorize
                    categorized = False
                    for category, symbols in self.SYMBOL_MAPPING.items():
                        if symbol in symbols:
                            positions[category] += value
                            categorized = True
                            break
                    
                    # Check for hedge (QQQ puts)
                    if not categorized and asset_class in ['OPT', 'FOP'] and 'QQQ' in symbol:
                        positions['hedge'] += value
                        categorized = True
                    
                    # Check for cash
                    if not categorized and asset_class == 'CASH':
                        positions['cash'] += value
                        categorized = True
                    
                    # Everything else goes to 'other'
                    if not categorized:
                        positions['other'] += value
            
            # Convert to percentages
            for key in positions:
                if key != 'total':
                    positions[key] = positions[key] / total_value
            
            # Combine gold + cash into reserves
            positions['reserves'] = positions['gold'] + positions['cash']
            
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
        for category in ['global_core', 'growth_engine', 'income_strategy', 'hedge', 'reserves']:
            target_pct = target_allocation.get(category, 0)
            actual_pct = actual.get(category, 0)
            diff = actual_pct - target_pct
            drift[category] = diff
            total_drift += abs(diff)
            
            # Flag significant drifts (>3%)
            if abs(diff) > 0.03:
                direction = 'overweight' if diff > 0 else 'underweight'
                alerts.append(f"{category.replace('_', ' ').title()}: {direction} by {abs(diff)*100:.0f}%")
        
        return {
            'drift': drift,
            'total_drift': total_drift,
            'alerts': alerts,
            'show': total_drift > 0.05  # Only show if total drift > 5%
        }
    
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
                'hedge': base['hedge'],
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
                'hedge': base['hedge'],
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
                'hedge': base['hedge'] * 2,  # Double hedge (10% in QQQ puts)
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
                'hedge': base['hedge'] * 3,  # 15% in QQQ puts
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
                'hedge': base['hedge'] * 5,  # 25% in QQQ puts
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
        
        # Portfolio allocation breakdown
        if drift_analysis and drift_analysis['show']:
            # Show target vs actual with drift
            lines.extend(["💼 PORTFOLIO ALLOCATION (Target → Actual)"])
            
            categories = [
                ('Global Core', 'global_core'),
                ('Growth Engine', 'growth_engine'),
                ('Income Strategy', 'income_strategy'),
                ('Hedge (QQQ Puts)', 'hedge'),
                ('Reserves', 'reserves')
            ]
            
            for label, key in categories:
                target = portfolio[key] * 100
                actual = self.actual_positions[key] * 100
                diff = drift_analysis['drift'][key] * 100
                
                if abs(diff) > 3:
                    indicator = "⚠️" if abs(diff) > 5 else "⚡"
                    lines.append(f"{label}: {target:.0f}% → {actual:.0f}% ({diff:+.0f}% {indicator})")
                else:
                    lines.append(f"{label}: {target:.0f}% → {actual:.0f}%")
            
            lines.extend([
                "",
                f"⚠️ DRIFT: {drift_analysis['total_drift']*100:.0f}% total",
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
                f"Hedge (QQQ Puts): {portfolio['hedge']*100:.0f}%",
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
        
        # Tier scores
        lines.extend([
            "📈 TIER SCORES",
            f"T1: {self.scores['tier1']:.0f}/50 ({self.scores['tier1']/50*100:.0f}%)",
            f"T2: {self.scores['tier2']:.0f}/30 ({self.scores['tier2']/30*100:.0f}%)",
            f"T3: {self.scores['tier3']:.0f}/15 ({self.scores['tier3']/15*100:.0f}%)",
            f"T4: {self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            "",
        ])
        
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
    # AI CIO INTERPRETATION
    # =============================================================================
    
    def generate_cio_interpretation(self):
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
- Hedge (QQQ Puts 15% OTM): {portfolio['hedge']*100:.0f}%
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
                return f"🧠 CIO INTERPRETATION\n📅 {self.timestamp.strftime('%b %d, %Y')}\n\n{resp.json()['content'][0]['text']}"
            return None
        except Exception as e:
            print(f"⚠️ CIO Error: {e}")
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
        
        # CIO interpretation
        cio = self.generate_cio_interpretation()
        if cio:
            print("\n" + cio + "\n")
            send_to_telegram(cio)
        
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
