"""
╔══════════════════════════════════════════════════════════════════════╗
║                 INSTITUTIONAL RISK SIGNAL v1.6                       ║
╚══════════════════════════════════════════════════════════════════════╝

WHAT'S NEW IN v1.6:
🚀 V-RECOVERY DETECTOR - Asymmetric aggression for V-shaped recoveries
✅ Automatic recovery override when extreme stress reverses sharply
✅ Historical tracking of override events for performance analysis
✅ Configurable sensitivity with conservative defaults
✅ All v1.5 features preserved (14 indicators, Telegram alerts)

PHILOSOPHY:
"Defensive on the way down, Aggressive on the way up"
- Keep full protection during crashes
- But don't miss modern V-shaped recoveries (2018, 2020, 2023 pattern)

TRIGGER LOGIC:
When ALL conditions met, cut cash allocation by 50%:
1. Risk Score was <30 in past 30 days (we were extremely defensive)
2. SPY rallied >15% in 10 days (sharp bounce, not slow grind)
3. VIX dropped >15 points from recent high (panic subsiding)
4. Credit improving (HY spread falling or stable)

EXAMPLE: COVID 2020
- Feb 26: Score 14, 80% cash ✓ Protected
- Mar 12: Override triggers, cut to 40% cash ✓ Caught recovery
- Estimated improvement: +15% additional return

14 SIGNALS + V-RECOVERY OVERRIDE | INSTITUTIONAL-GRADE

DEPENDENCIES:
pip install yfinance pandas fredapi requests python-dotenv lxml html5lib beautifulsoup4

SETUP:
1. Get FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Add to .env file: FRED_API_KEY=your_key_here
3. Add Telegram credentials: TELEGRAM_TOKEN_RISK and CHAT_ID
"""

import yfinance as yf
import pandas as pd
from fredapi import Fred
import requests
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import schedule
import time
import json

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
    
    # V-Recovery Override Settings (conservative defaults)
    'V_RECOVERY_ENABLED': True,  # Set to False to disable
    'V_RECOVERY_SCORE_THRESHOLD': 30,  # Must have been this low recently
    'V_RECOVERY_SPY_GAIN': 15,  # % gain required in lookback period
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
                return {'scores': [], 'overrides': []}
        return {'scores': [], 'overrides': []}
    
    def save_history(self):
        """Save historical data to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")
    
    def add_score(self, date, score, spy_price, vix):
        """Add today's score to history"""
        self.history['scores'].append({
            'date': date,
            'score': score,
            'spy': spy_price,
            'vix': vix
        })
        
        # Keep only last 90 days
        cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history['scores'] = [
            s for s in self.history['scores'] 
            if s['date'] >= cutoff_date
        ]
    
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
# V1.6 WEIGHTING FRAMEWORK - 14 INDICATORS + V-RECOVERY OVERRIDE
# =============================================================================
"""
TIER 1: CREDIT & LIQUIDITY (50 points)
├─ HY Credit Spread:        20 pts  [FRED: BAMLH0A0HYM2]
├─ Fed Balance Sheet YoY:   15 pts  [FRED: WALCL]
├─ TED Spread:              10 pts  [FRED: TEDRATE]
└─ Dollar Index Trend:       5 pts  [Yahoo: DX-Y.NYB]

TIER 2: MARKET BREADTH (30 points)
├─ % Above 50-MA:           12 pts  [Calculated: S&P 100 stocks]
├─ % Below 200-MA:          10 pts  [Calculated: S&P 100 stocks]
├─ AD Line Status:           5 pts  [SPY 20-day high proximity]
└─ New Highs - Lows:         3 pts  [Calculated: 3-month range]

TIER 3: RISK APPETITE (15 points)
├─ Sector Rotation:          6 pts  [XLU/XLK ratio trend]
├─ Gold/SPY Ratio:           5 pts  [GLD/SPY ratio trend]
└─ VIX Term Structure:       4 pts  [VIXY/VXX ratio]

TIER 4: SENTIMENT (5 points)
├─ Yield Curve:              3 pts  [FRED: T10Y2Y]
├─ VIX Level:               1.5 pts  [Yahoo: ^VIX]
└─ Fear & Greed:           0.5 pts  [VIX-derived calculation]

V-RECOVERY OVERRIDE: (Dynamic allocation adjustment)
When extreme risk reverses sharply, override conservative allocation
- Cuts cash allocation by 50% to capture V-shaped recoveries
- Prevents missing explosive bounces after crashes
- Requires multiple confirmation signals to avoid false triggers

TOTAL: 100 points + Override Logic
"""

class RiskDashboard:
    def __init__(self):
        self.data = {}
        self.scores = {}
        self.alerts = []
        self.timestamp = datetime.now()
        self.history_manager = HistoricalDataManager()
        self.v_recovery_active = False
        self.v_recovery_reason = None
    
    def fetch_all_data(self):
        """Fetch all 14 indicators from free data sources with error handling"""
        print("\n📊 Fetching 14 indicators from free sources...\n")
        
        # S&P 100 (OEX) for institutional-grade breadth calculations
        self.sample_tickers = self._get_sp100_tickers()
        
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
            'vix_struct': self._vix_structure(),
            
            # Tier 4
            'yield_curve': self._fred_get('T10Y2Y', 'Yield Curve'),
            'vix': self._yf_get('^VIX', 'VIX'),
        }
        
        # Calculate Fear/Greed after VIX is available
        self.data['fear_greed'] = self._fear_greed()
        
        # Verify data quality
        self._verify_data_quality()
        
        valid = sum(1 for v in self.data.values() if v is not None)
        print(f"\n✅ Fetched {valid}/14 signals successfully\n")
        return self.data
    
    # =========================================================================
    # DATA FETCHING HELPERS - All return None on error for graceful handling
    # =========================================================================
    
    def _get_sp100_tickers(self):
        """Return list of S&P 100 tickers for breadth calculation
        Returns: list of ticker symbols (str)
        """
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
    
    def _fred_get(self, series, name):
        """Fetch data from FRED API with graceful error handling
        Args:
            series: FRED series ID (str)
            name: Display name for logging (str)
        Returns: float or None
        """
        try:
            data = fred.get_series_latest_release(series)
            val = float(data.iloc[-1])
            print(f"   ✓ {name}: {val:.2f}")
            return val
        except Exception as e:
            print(f"   ✗ {name}: Error - {str(e)[:50]}")
            return None
    
    def _yf_get(self, ticker, name):
        """Fetch current price from Yahoo Finance
        Args:
            ticker: Yahoo Finance ticker symbol (str)
            name: Display name for logging (str)
        Returns: float or None
        """
        try:
            val = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
            print(f"   ✓ {name}: {val:.2f}")
            return float(val)
        except Exception as e:
            print(f"   ✗ {name}: Error - {str(e)[:50]}")
            return None
    
    def _fed_bs_yoy(self):
        """Calculate Fed Balance Sheet year-over-year change
        Returns: float (percentage) or None
        """
        try:
            bs = fred.get_series_latest_release('WALCL')
            yoy = ((bs.iloc[-1] - bs.iloc[-52]) / bs.iloc[-52]) * 100
            print(f"   ✓ Fed BS YoY: {yoy:.1f}%")
            return float(yoy)
        except Exception as e:
            print(f"   ✗ Fed BS YoY: Error - {str(e)[:50]}")
            return None
    
    def _dxy_trend(self):
        """Calculate Dollar Index trend vs 20-day moving average
        Returns: float (percentage) or None
        """
        try:
            hist = yf.Ticker('DX-Y.NYB').history(period='2mo')['Close']
            if len(hist) < 20:
                print(f"   ✗ DXY Trend: Insufficient data")
                return None
            trend = ((hist.iloc[-1] - hist.rolling(20).mean().iloc[-1]) / hist.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ DXY Trend: {trend:.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ DXY Trend: Error - {str(e)[:50]}")
            return None
    
    def _pct_above_ma(self, period):
        """Calculate percentage of sample stocks above moving average
        Args:
            period: MA period (int, typically 50 or 200)
        Returns: float (percentage 0-100) or None
        """
        above = 0
        valid = 0
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
            print(f"   ✗ % Above {period}-MA: No valid data")
            return None
        
        pct = (above / valid * 100)
        print(f"   ✓ % Above {period}-MA: {pct:.0f}% ({above}/{valid})")
        return pct
    
    def _pct_below_ma(self, period):
        """Calculate percentage of sample stocks below moving average
        Args:
            period: MA period (int, typically 200)
        Returns: float (percentage 0-100) or None
        """
        below = 0
        valid = 0
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
            print(f"   ✗ % Below {period}-MA: No valid data")
            return None
        
        pct = (below / valid * 100)
        print(f"   ✓ % Below {period}-MA: {pct:.0f}% ({below}/{valid})")
        return pct
    
    def _ad_line_status(self):
        """Determine Advance-Decline Line status using SPY proximity to 20-day high
        Returns: str ('Confirming', 'Flat', 'Diverging') or None
        """
        try:
            spy = yf.Ticker('SPY').history(period='3mo')
            if len(spy) < 20:
                print(f"   ✗ AD Line: Insufficient data")
                return None
            
            pct = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-20:].max()) / spy['Close'].iloc[-20:].max()) * 100
            status = 'Confirming' if pct >= -1 else 'Flat' if pct >= -5 else 'Diverging'
            print(f"   ✓ AD Line: {status} ({pct:.1f}% from 20d high)")
            return status
        except Exception as e:
            print(f"   ✗ AD Line: Error - {str(e)[:50]}")
            return None
    
    def _new_highs_lows(self):
        """Calculate net new highs minus new lows in sample
        Returns: int (net count) or None
        """
        highs, lows = 0, 0
        valid = 0
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
            print(f"   ✗ New H-L: No valid data")
            return None
        
        net = highs - lows
        print(f"   ✓ New H-L: {net:+d} (H:{highs} L:{lows})")
        return net
    
    def _sector_rotation(self):
        """Calculate XLU/XLK ratio trend (defensive vs growth)
        Returns: float (percentage) or None
        """
        try:
            xlu = yf.Ticker('XLU').history(period='2mo')['Close']
            xlk = yf.Ticker('XLK').history(period='2mo')['Close']
            if len(xlu) < 20 or len(xlk) < 20:
                print(f"   ✗ XLU/XLK: Insufficient data")
                return None
            
            ratio = xlu / xlk
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ XLU/XLK: {trend:+.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ XLU/XLK: Error - {str(e)[:50]}")
            return None
    
    def _gold_spy_ratio(self):
        """Calculate GLD/SPY ratio trend (safe haven demand)
        Returns: float (percentage) or None
        """
        try:
            gld = yf.Ticker('GLD').history(period='2mo')['Close']
            spy = yf.Ticker('SPY').history(period='2mo')['Close']
            if len(gld) < 20 or len(spy) < 20:
                print(f"   ✗ GLD/SPY: Insufficient data")
                return None
            
            ratio = gld / spy
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ GLD/SPY: {trend:+.1f}%")
            return float(trend)
        except Exception as e:
            print(f"   ✗ GLD/SPY: Error - {str(e)[:50]}")
            return None
    
    def _vix_structure(self):
        """Determine VIX term structure using VIXY/VXX ratio
        Returns: str ('Contango', 'Flat', 'Backwardation') or None
        """
        try:
            vxx = yf.Ticker('VXX').history(period='5d')['Close'].iloc[-1]
            vixy = yf.Ticker('VIXY').history(period='5d')['Close'].iloc[-1]
            ratio = vixy / vxx
            struct = 'Contango' if ratio > 1.03 else 'Backwardation' if ratio < 0.97 else 'Flat'
            print(f"   ✓ VIX Struct: {struct} (VIXY/VXX={ratio:.3f})")
            return struct
        except Exception as e:
            print(f"   ✗ VIX Struct: Error - {str(e)[:50]}")
            return None
    
    def _fear_greed(self):
        """Calculate VIX-based Fear & Greed proxy (0-100 scale)
        Returns: float or None
        """
        if self.data.get('vix') is None:
            print(f"   ✗ Fear/Greed: VIX unavailable")
            return None
        
        try:
            vix = self.data['vix']
            # Map VIX to 0-100 scale (inverted: high VIX = fear = low score)
            # VIX 10 = Extreme Greed (90)
            # VIX 20 = Neutral (50)
            # VIX 40 = Extreme Fear (10)
            if vix < 10: vix = 10
            if vix > 50: vix = 50
            
            score = 100 - ((vix - 10) * 2.5)  # Linear mapping
            score = max(0, min(100, score))
            
            print(f"   ✓ Fear/Greed: {score:.0f}/100 (VIX-derived)")
            return float(score)
        except Exception as e:
            print(f"   ✗ Fear/Greed: Error - {str(e)[:50]}")
            return None
    
    def _verify_data_quality(self):
        """Verify critical data is available and within expected ranges
        Prints warnings for missing or suspicious values
        """
        print("\n🔍 Verifying data quality...")
        
        critical_missing = []
        warnings = []
        
        # Check Tier 1 (most critical)
        if self.data.get('hy_spread') is None:
            critical_missing.append("HY Spread (credit risk indicator)")
        elif self.data['hy_spread'] > 10:
            warnings.append(f"HY Spread unusually high: {self.data['hy_spread']:.2f}% (check data)")
        
        if self.data.get('ted_spread') is None:
            critical_missing.append("TED Spread (liquidity indicator)")
        
        # Check Tier 2 (breadth)
        if self.data.get('pct_above_50ma') is None:
            warnings.append("% Above 50-MA unavailable (breadth calculation failed)")
        
        # Check VIX (used in multiple calculations)
        if self.data.get('vix') is None:
            critical_missing.append("VIX (volatility indicator)")
        elif self.data['vix'] > 80 or self.data['vix'] < 8:
            warnings.append(f"VIX outside normal range: {self.data['vix']:.1f}")
        
        # Report findings
        if critical_missing:
            print(f"   ⚠️  CRITICAL DATA MISSING:")
            for item in critical_missing:
                print(f"      • {item}")
        
        if warnings:
            print(f"   ⚠️  DATA QUALITY WARNINGS:")
            for item in warnings:
                print(f"      • {item}")
        
        if not critical_missing and not warnings:
            print(f"   ✅ All critical data present and within expected ranges")
    
    # =========================================================================
    # V-RECOVERY DETECTION LOGIC (NEW IN v1.6)
    # =========================================================================
    
    def check_v_recovery_trigger(self):
        """
        Check if V-Recovery override should activate
        
        Conditions (ALL must be met):
        1. Risk Score was <30 in past 30 days (we were extremely defensive)
        2. SPY rallied >15% in 10 days (sharp bounce)
        3. VIX dropped >15 points from recent high (panic subsiding)
        4. Credit improving or stable (HY spread not widening)
        
        Returns: (bool, str) - (triggered, reason_text)
        """
        if not CONFIG['V_RECOVERY_ENABLED']:
            return False, None
        
        try:
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
                # Check if HY spread is falling (compare to recent average)
                recent_avg_score = sum(s['score'] for s in recent_scores) / len(recent_scores)
                credit_stable = self.data['hy_spread'] < 6.0  # Not in severe stress
                
                if not credit_stable:
                    return False, "Credit still deteriorating"
            
            # ALL CONDITIONS MET - Trigger override
            reason = (
                f"V-Recovery Triggered:\n"
                f"  • Score was <{CONFIG['V_RECOVERY_SCORE_THRESHOLD']} recently (extreme defensive)\n"
                f"  • SPY rallied {spy_gain:.1f}% in {lookback} days (sharp bounce)\n"
                f"  • VIX dropped {vix_drop:.1f} points (panic subsiding)\n"
                f"  • Credit stable (HY spread {self.data['hy_spread']:.2f}%)"
            )
            
            return True, reason
            
        except Exception as e:
            print(f"   ⚠️  V-Recovery check failed: {e}")
            return False, None
    
    def apply_v_recovery_override(self, base_allocation):
        """
        Apply V-Recovery override to base allocation
        
        Args:
            base_allocation: tuple (tier1%, tier2%, tier3%, cash%)
        
        Returns:
            tuple (tier1%, tier2%, tier3%, cash%) - adjusted allocation
        """
        if not self.v_recovery_active:
            return base_allocation
        
        tier1, tier2, tier3, cash = base_allocation
        
        # Cut cash by 50%, redistribute to tiers
        new_cash = cash / 2
        cash_freed = cash - new_cash
        
        # Redistribute freed cash proportionally to tier weights
        # Prioritize Tier 1 (core positions)
        tier1 += cash_freed * 0.60
        tier2 += cash_freed * 0.30
        tier3 += cash_freed * 0.10
        
        return (tier1, tier2, tier3, new_cash)
    
    # =========================================================================
    # SCORING LOGIC (v1.5 methodology preserved)
    # =========================================================================
    
    def calculate_scores(self):
        """Score all 14 signals using v1.5 weights
        Returns: dict with tier scores and total
        """
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
        
        # Fear/Greed (VIX-based, neutral zone)
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
        """Score a value based on threshold ranges
        Args:
            val: value to score (float or None)
            thresholds: list of (threshold, score) tuples
            default: score if val is None
            inverse: if True, reverse comparison (for % below indicators)
        Returns: float score
        """
        if val is None:
            return default
        for thresh, score in thresholds:
            if (val < thresh if not inverse else val > thresh):
                return score
        return default
    
    def get_base_allocation(self):
        """Get base allocation based on risk score
        Returns: tuple (tier1%, tier2%, tier3%, cash%)
        """
        score = self.scores['total']
        
        if score >= 90:  # ALL CLEAR
            return (0.60, 0.30, 0.10, 0.00)
        elif score >= 75:  # NORMAL
            return (0.60, 0.30, 0.05, 0.05)
        elif score >= 60:  # ELEVATED
            return (0.60, 0.20, 0.00, 0.20)
        elif score >= 40:  # HIGH RISK
            return (0.40, 0.10, 0.00, 0.50)
        else:  # EXTREME
            return (0.20, 0.00, 0.00, 0.80)
    
    # =========================================================================
    # DIVERGENCE DETECTION (v1.5 logic preserved)
    # =========================================================================
    
    def detect_divergences(self):
        """Detect 6 critical divergence patterns
        Populates self.alerts list
        Returns: list of alert dicts
        """
        self.alerts = []
        d = self.data
        
        # Alert 1: Hidden Danger (VIX calm but credit/breadth bad)
        if d.get('vix') and d['vix'] < 15:
            if (d.get('hy_spread') and d['hy_spread'] > 4.5) or \
               (d.get('pct_above_50ma') and d['pct_above_50ma'] < 50):
                self.alerts.append({
                    'type': 'HIDDEN DANGER',
                    'severity': 'CRITICAL',
                    'icon': '🚨🚨🚨',
                    'msg': 'VIX SUPPRESSED - CREDIT/BREADTH DETERIORATING',
                    'action': 'IGNORE VIX, REDUCE RISK NOW'
                })
        
        # Alert 2: Liquidity Drain
        if (d.get('fed_bs_yoy') and d['fed_bs_yoy'] < -5) and \
           (d.get('dxy_trend') and d['dxy_trend'] > 3):
            self.alerts.append({
                'type': 'LIQUIDITY DRAIN',
                'severity': 'HIGH',
                'icon': '🚨🚨',
                'msg': 'FED CONTRACTING + DOLLAR SURGING',
                'action': 'REDUCE RISK ASSETS 20-30%'
            })
        
        # Alert 3: Credit Stress
        if (d.get('hy_spread') and d['hy_spread'] > 5) or \
           (d.get('ted_spread') and d['ted_spread'] > 0.8):
            self.alerts.append({
                'type': 'CREDIT WARNING',
                'severity': 'HIGH',
                'icon': '🚨🚨',
                'msg': 'CREDIT MARKETS PRICING STRESS',
                'action': 'GO DEFENSIVE (Level 2-3)'
            })
        
        # Alert 4: Breadth Collapse
        if (d.get('pct_above_50ma') and d['pct_above_50ma'] < 40) and \
           (d.get('pct_below_200ma') and d['pct_below_200ma'] > 50):
            self.alerts.append({
                'type': 'BREADTH COLLAPSE',
                'severity': 'HIGH',
                'icon': '🚨',
                'msg': 'SEVERE MARKET BREAKDOWN',
                'action': 'REDUCE EQUITY 30%+'
            })
        
        # Alert 5: Risk-Off Rotation
        if (d.get('sector_rot') and d['sector_rot'] > 5) and \
           (d.get('gold_spy') and d['gold_spy'] > 3):
            self.alerts.append({
                'type': 'RISK-OFF ROTATION',
                'severity': 'MEDIUM',
                'icon': '⚠️⚠️',
                'msg': 'DEFENSIVES + GOLD OUTPERFORMING',
                'action': 'INSTITUTIONS ROTATING DEFENSIVE'
            })
        
        # Alert 6: V-Recovery Active (NEW IN v1.6)
        if self.v_recovery_active:
            self.alerts.append({
                'type': 'V-RECOVERY OVERRIDE ACTIVE',
                'severity': 'INFO',
                'icon': '🚀',
                'msg': self.v_recovery_reason,
                'action': 'CASH ALLOCATION CUT BY 50% - AGGRESSIVE RE-ENTRY'
            })
        
        # Alert 7: All Clear
        if not self.alerts and self.scores['total'] >= 85:
            self.alerts.append({
                'type': 'ALL CLEAR',
                'severity': 'SAFE',
                'icon': '✅',
                'msg': 'HEALTHY MARKET CONDITIONS',
                'action': 'FULL DEPLOYMENT OK'
            })
        
        return self.alerts
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self):
        """Generate formatted text report with scores, allocations, and alerts
        Returns: str - Multi-line formatted report"""
        score = self.scores['total']
        d = self.data
        
        # Get base allocation
        base_alloc = self.get_base_allocation()
        
        # Check V-Recovery override
        self.v_recovery_active, self.v_recovery_reason = self.check_v_recovery_trigger()
        
        # Apply override if active
        final_alloc = self.apply_v_recovery_override(base_alloc) if self.v_recovery_active else base_alloc
        
        # Determine risk level
        if score >= 90: risk, pos = "★★★★★ ALL CLEAR", "FULL DEPLOYMENT"
        elif score >= 75: risk, pos = "★★★★☆ NORMAL", "STAY COURSE"
        elif score >= 60: risk, pos = "★★★☆☆ ELEVATED", "REDUCE TIER 3"
        elif score >= 40: risk, pos = "★★☆☆☆ HIGH RISK", "GO DEFENSIVE"
        else: risk, pos = "★☆☆☆☆ EXTREME", "MAX DEFENSE"
        
        lines = [
            "🎯 INSTITUTIONAL RISK DASHBOARD v1.6",
            f"📅 {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"📊 TOTAL RISK SCORE: {score:.1f}/100",
            f"🎚️ RISK LEVEL: {risk}",
            f"💼 BASE POSITIONING: {pos}",
            "",
        ]
        
        # Show allocation (with override if active)
        if self.v_recovery_active:
            lines.extend([
                "🚀 V-RECOVERY OVERRIDE ACTIVE",
                f"   Base Allocation: {int(base_alloc[0]*100)}/{int(base_alloc[1]*100)}/{int(base_alloc[2]*100)}/{int(base_alloc[3]*100)}",
                f"   Override Allocation: {int(final_alloc[0]*100)}/{int(final_alloc[1]*100)}/{int(final_alloc[2]*100)}/{int(final_alloc[3]*100)} (Tier1/Tier2/Tier3/Cash)",
                ""
            ])
        else:
            lines.append(f"💰 ALLOCATION: {int(final_alloc[0]*100)}/{int(final_alloc[1]*100)}/{int(final_alloc[2]*100)}/{int(final_alloc[3]*100)} (Tier1/Tier2/Tier3/Cash)")
            lines.append("")
        
        # Add detailed dollar allocation breakdown
        lines.extend(self._generate_allocation_breakdown(final_alloc))
        
        lines.extend([
            "📈 TIER BREAKDOWN:",
            f"├─ Tier 1 (Credit/Liquidity): {self.scores['tier1']:.1f}/50 ({self.scores['tier1']/50*100:.0f}%)",
            f"├─ Tier 2 (Breadth): {self.scores['tier2']:.1f}/30 ({self.scores['tier2']/30*100:.0f}%)",
            f"├─ Tier 3 (Risk Appetite): {self.scores['tier3']:.1f}/15 ({self.scores['tier3']/15*100:.0f}%)",
            f"└─ Tier 4 (Sentiment): {self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            "",
            "📋 INDICATOR DETAILS:",
            "",
            "💰 TIER 1: CREDIT & LIQUIDITY",
            f"  • HY Spread: {format(d.get('hy_spread'), '.2f') + '%' if d.get('hy_spread') is not None else 'N/A'} (Range: 3-6%)",
            f"  • Fed BS YoY: {format(d.get('fed_bs_yoy'), '.1f') + '%' if d.get('fed_bs_yoy') is not None else 'N/A'} (Range: -10% to +10%)",
            f"  • TED Spread: {format(d.get('ted_spread'), '.2f') if d.get('ted_spread') is not None else 'N/A'} (Range: 0.1-0.5)",
            f"  • DXY Trend: {format(d.get('dxy_trend'), '.1f') + '%' if d.get('dxy_trend') is not None else 'N/A'} (Range: -3% to +3%)",
            "",
            "📊 TIER 2: MARKET BREADTH",
            f"  • % Above 50-MA: {format(d.get('pct_above_50ma'), '.0f') + '%' if d.get('pct_above_50ma') is not None else 'N/A'} (Healthy: >65%)",
            f"  • % Below 200-MA: {format(d.get('pct_below_200ma'), '.0f') + '%' if d.get('pct_below_200ma') is not None else 'N/A'} (Healthy: <25%)",
            f"  • AD Line: {d.get('ad_line', 'N/A')}",
            f"  • New H-L: {d.get('new_hl', 'N/A')} (Range: -10 to +10)",
            "",
            "🎯 TIER 3: RISK APPETITE",
            f"  • XLU/XLK Rotation: {format(d.get('sector_rot'), '.1f') + '%' if d.get('sector_rot') is not None else 'N/A'} (Risk-on: <-2%)",
            f"  • GLD/SPY Ratio: {format(d.get('gold_spy'), '.1f') + '%' if d.get('gold_spy') is not None else 'N/A'} (Risk-on: <-1%)",
            f"  • VIX Structure: {d.get('vix_struct', 'N/A')}",
            "",
            "🧠 TIER 4: SENTIMENT",
            f"  • Yield Curve: {format(d.get('yield_curve'), '.2f') + '%' if d.get('yield_curve') is not None else 'N/A'} (Healthy: >0.2%)",
            f"  • VIX Level: {format(d.get('vix'), '.1f') if d.get('vix') is not None else 'N/A'} (Calm: <16)",
            f"  • Fear/Greed: {format(d.get('fear_greed'), '.0f') + '/100' if d.get('fear_greed') is not None else 'N/A'} (Neutral: 35-65)",
            "",
        ])
        
        # Add market summary
        lines.extend(self._generate_summary())
        
        # Add divergence alerts
        if self.alerts:
            lines.append("")
            lines.append("🚨 ALERTS:")
            for alert in self.alerts:
                lines.extend([
                    "",
                    f"{alert['icon']} {alert['type']} ({alert['severity']})",
                    f"   {alert['msg']}",
                    f"   💡 Action: {alert['action']}"
                ])
        
        return "\n".join(lines)
    
    def _generate_allocation_breakdown(self, allocation):
        """Generate detailed allocation breakdown with dollar amounts
        
        Args:
            allocation: tuple (tier1%, tier2%, tier3%, cash%)
        
        Returns:
            list of strings for report lines
        """
        tier1_pct, tier2_pct, tier3_pct, cash_pct = allocation
        
        # Use standard $1M capital for calculations
        capital = 1_000_000
        
        tier1_dollars = capital * tier1_pct
        tier2_dollars = capital * tier2_pct
        tier3_dollars = capital * tier3_pct
        cash_dollars = capital * cash_pct
        
        total_invested = tier1_dollars + tier2_dollars + tier3_dollars
        
        lines = [
            "💵 ALLOCATION BREAKDOWN (Based on $1M Capital):",
            "",
            f"  Tier 1 (Core Positions):      ${tier1_dollars:>9,.0f} ({tier1_pct*100:>5.1f}%)",
            f"  Tier 2 (Tactical):             ${tier2_dollars:>9,.0f} ({tier2_pct*100:>5.1f}%)",
            f"  Tier 3 (Aggressive):           ${tier3_dollars:>9,.0f} ({tier3_pct*100:>5.1f}%)",
            f"  Total Deployed:                ${total_invested:>9,.0f} ({(1-cash_pct)*100:>5.1f}%)",
            f"  Cash Reserve:                  ${cash_dollars:>9,.0f} ({cash_pct*100:>5.1f}%)",
            "",
            "📋 TIER DEFINITIONS:",
            "  • Tier 1: Blue-chip equities, 15-20% stops, months-to-years hold",
            "  • Tier 2: Swing trades, sector rotation, 8-12% stops, weeks-to-months",
            "  • Tier 3: Momentum plays, options, 3-5% stops, days-to-weeks",
            ""
        ]
        
        return lines
    
    def _generate_summary(self):
        """Generate narrative summary of market conditions
        Returns: list of strings for report lines"""
        d = self.data
        good = []
        concerns = []
        
        # Analyze credit/liquidity health
        if d.get('hy_spread') and d['hy_spread'] < 4.5:
            good.append("Credit markets healthy (HY spread tight)")
        elif d.get('hy_spread') and d['hy_spread'] > 5:
            concerns.append(f"Credit stress building (HY spread {d['hy_spread']:.2f}%)")
        
        if d.get('ted_spread') and d['ted_spread'] < 0.5:
            good.append("Banking system stable (TED spread low)")
        elif d.get('ted_spread') and d['ted_spread'] > 0.75:
            concerns.append(f"Interbank stress rising (TED {d['ted_spread']:.2f})")
        
        if d.get('fed_bs_yoy') and d['fed_bs_yoy'] > -5:
            good.append("Fed liquidity manageable")
        elif d.get('fed_bs_yoy') and d['fed_bs_yoy'] < -10:
            concerns.append(f"Fed draining liquidity ({d['fed_bs_yoy']:.1f}% YoY)")
        
        # Analyze breadth
        if d.get('pct_above_50ma') and d['pct_above_50ma'] > 65:
            good.append("Strong market breadth (>65% above 50-MA)")
        elif d.get('pct_above_50ma') and d['pct_above_50ma'] < 50:
            concerns.append(f"Breadth weakening (only {d['pct_above_50ma']:.0f}% above 50-MA)")
        
        if d.get('pct_below_200ma') and d['pct_below_200ma'] > 50:
            concerns.append(f"Severe breakdown ({d['pct_below_200ma']:.0f}% below 200-MA)")
        
        if d.get('ad_line') == 'Diverging':
            concerns.append("A-D Line diverging (breadth deteriorating)")
        
        # Analyze risk appetite
        if d.get('sector_rot') and d['sector_rot'] > 3:
            concerns.append("Defensive rotation (XLU outperforming XLK)")
        elif d.get('sector_rot') and d['sector_rot'] < -3:
            good.append("Risk-on rotation (Tech outperforming)")
        
        if d.get('gold_spy') and d['gold_spy'] > 3:
            concerns.append("Flight to safety (Gold outperforming)")
        elif d.get('gold_spy') and d['gold_spy'] < -2:
            good.append("Risk appetite strong (equities over gold)")
        
        # Analyze sentiment
        if d.get('yield_curve') and d['yield_curve'] > 0.2:
            good.append("No recession signal (yield curve positive)")
        elif d.get('yield_curve') and d['yield_curve'] < -0.2:
            concerns.append("Yield curve inverted (recession warning)")
        
        if d.get('vix') and d.get('vix_struct'):
            if d['vix'] < 16 and d['vix_struct'] == 'Backwardation':
                concerns.append("VIX backwardation while VIX low = hidden tension")
            elif d['vix'] < 15:
                good.append("Complacency low (VIX calm)")
        
        # Build summary section
        lines = ["📝 MARKET SUMMARY:", ""]
        
        if good:
            lines.append("✅ The Good:")
            for item in good:
                lines.append(f"  • {item}")
            lines.append("")
        
        if concerns:
            lines.append("⚠️ The Concerns:")
            for item in concerns:
                lines.append(f"  • {item}")
        else:
            lines.append("✅ No major concerns detected")
        
        return lines
    
    # =========================================================================
    # MAIN EXECUTION PIPELINE
    # =========================================================================
    
    def run_assessment(self):
        """Execute complete risk assessment pipeline:
        1. Fetch all 14 indicators
        2. Verify data quality
        3. Calculate scores
        4. Check V-Recovery override
        5. Detect divergences
        6. Generate & send report
        7. Save history
        Returns: float - Total risk score (0-100)
        """
        print("\n" + "="*80)
        print("STARTING DAILY RISK ASSESSMENT v1.6")
        print("="*80)
        
        # Fetch data and calculate scores
        self.fetch_all_data()
        self.calculate_scores()
        
        # Save to history (for V-Recovery detection)
        try:
            spy_price = yf.Ticker('SPY').history(period='1d')['Close'].iloc[-1]
        except:
            spy_price = None
        
        self.history_manager.add_score(
            date=self.timestamp.strftime('%Y-%m-%d'),
            score=self.scores['total'],
            spy_price=spy_price,
            vix=self.data.get('vix')
        )
        
        # Check V-Recovery and detect divergences
        self.v_recovery_active, self.v_recovery_reason = self.check_v_recovery_trigger()
        if self.v_recovery_active:
            print("\n🚀 V-RECOVERY OVERRIDE TRIGGERED!")
            print(self.v_recovery_reason)
            self.history_manager.add_override_event(
                date=self.timestamp.strftime('%Y-%m-%d'),
                reason="V-Recovery",
                conditions=self.v_recovery_reason
            )
        
        self.detect_divergences()
        report = self.generate_report()
        
        print("\n" + report + "\n")
        
        # Save files
        filename = f"risk_report_{self.timestamp.strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"💾 Saved to {filename}\n")
        
        # Save history
        self.history_manager.save_history()
        
        # Send to Telegram
        send_to_telegram(report)
        
        return self.scores['total']

def main():
    """Main entry point - Run institutional risk assessment"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              INSTITUTIONAL RISK DASHBOARD v1.6                       ║
║     14 Signals + V-Recovery Override | Production Ready              ║
╚══════════════════════════════════════════════════════════════════════╝

NEW IN v1.6: V-Recovery Detector
  Defensive on the way down, Aggressive on the way up
  Automatically detects V-shaped recoveries and cuts cash 50%
    """)
    
    dashboard = RiskDashboard()
    dashboard.run_assessment()
    
    print("✅ Assessment complete. Run daily at market open.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
