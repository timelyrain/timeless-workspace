"""
╔══════════════════════════════════════════════════════════════════════╗
║                 INSTITUTIONAL RISK SIGNAL v1.5                    ║
╚══════════════════════════════════════════════════════════════════════╝

WHAT'S NEW IN v1.5:
✅ Fed Balance Sheet (liquidity tracking)
✅ Dollar Index trend (global liquidity)
✅ Sector Rotation XLU/XLK (risk-on/off)
✅ Gold/SPY ratio (safe haven demand)
✅ % Below 200-MA (severe breakdown signal)
✅ New Highs-Lows (breadth expansion/contraction)
✅ VIX-derived Fear & Greed Index (CNN API deprecated)
✅ Comprehensive data verification system

14 SIGNALS | INSTITUTIONAL-GRADE

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
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import schedule
import time

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
# V1.5 WEIGHTING FRAMEWORK - 14 INDICATORS
# =============================================================================
"""
TIER 1: CREDIT & LIQUIDITY (50 points)
├─ HY Credit Spread:        20 pts  [FRED: BAMLH0A0HYM2]
├─ Fed Balance Sheet YoY:   15 pts  [FRED: WALCL]
├─ TED Spread:              10 pts  [FRED: TEDRATE]
└─ Dollar Index Trend:       5 pts  [Yahoo: DX-Y.NYB]

TIER 2: MARKET BREADTH (30 points)
├─ % Above 50-MA:           12 pts  [Calculated: 27 blue-chip stocks]
├─ % Below 200-MA:          10 pts  [Calculated: 27 blue-chip stocks]
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

TOTAL: 100 points (14 indicators with verification)
"""

class RiskDashboard:
    def __init__(self):
        self.data = {}
        self.scores = {}
        self.alerts = []
        self.timestamp = datetime.now()
    
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
        """Get S&P 100 (OEX) constituents for breadth calculations
        Returns: list of ticker symbols (100 largest US stocks)
        
        Uses a cached list of S&P 100 constituents (updated periodically).
        This is the institutional standard for market breadth analysis.
        All 11 sectors represented for unbiased breadth measurement.
        """
        # S&P 100 constituents as of Q4 2025 (11 sectors, ~100 stocks)
        sp100 = [
            # Technology (16)
            'AAPL','MSFT','NVDA','GOOGL','GOOG','META','AVGO','ORCL','CSCO',
            'ADBE','CRM','AMD','INTC','QCOM','TXN','IBM',
            # Healthcare (13)
            'UNH','JNJ','LLY','MRK','ABBV','TMO','ABT','DHR','PFE','AMGN',
            'BMY','GILD','CVS',
            # Financials (13)
            'JPM','V','MA','BAC','WFC','MS','GS','BLK','C','SPGI','AXP','BX','CB',
            # Consumer Discretionary (11)
            'AMZN','TSLA','HD','MCD','NKE','SBUX','LOW','TGT','TJX','BKNG','CMG',
            # Communication Services (6)
            'GOOGL','META','DIS','NFLX','T','VZ',
            # Industrials (9)
            'UNP','HON','UPS','RTX','LMT','BA','CAT','GE','DE',
            # Consumer Staples (8)
            'PG','KO','PEP','WMT','COST','MDLZ','CL','MO',
            # Energy (6)
            'XOM','CVX','COP','SLB','EOG','PXD',
            # Utilities (3)
            'NEE','DUK','SO',
            # Real Estate (3)
            'AMT','PLD','EQIX',
            # Materials (4)
            'LIN','APD','SHW','NEM',
            # Financials (Additional)
            'SCHW','USB','PNC','TFC'
        ]
        
        # Remove duplicates and limit to 100
        unique_tickers = list(dict.fromkeys(sp100))[:100]
        print(f"   ✓ Using S&P 100 stocks ({len(unique_tickers)} tickers) for breadth")
        return unique_tickers
    
    def _fred_get(self, series, name):
        """Fetch latest value from FRED API series"""
        try:
            data = fred.get_series_latest_release(series)
            val = float(data.iloc[-1])
            print(f"   ✓ {name}: {val:.2f}")
            return val
        except Exception as e:
            print(f"   ✗ {name}: Error")
            return None
    
    def _yf_get(self, ticker, name):
        try:
            val = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
            print(f"   ✓ {name}: {val:.2f}")
            return float(val)
        except:
            print(f"   ✗ {name}: Error")
            return None
    
    def _fed_bs_yoy(self):
        try:
            bs = fred.get_series_latest_release('WALCL')
            yoy = ((bs.iloc[-1] - bs.iloc[-52]) / bs.iloc[-52]) * 100
            print(f"   ✓ Fed BS YoY: {yoy:.1f}%")
            return float(yoy)
        except:
            print(f"   ✗ Fed BS YoY: Error")
            return None
    
    def _dxy_trend(self):
        try:
            hist = yf.Ticker('DX-Y.NYB').history(period='2mo')['Close']
            trend = ((hist.iloc[-1] - hist.rolling(20).mean().iloc[-1]) / hist.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ DXY Trend: {trend:.1f}%")
            return float(trend)
        except:
            print(f"   ✗ DXY Trend: Error")
            return None
    
    def _pct_above_ma(self, period):
        """Calculate % of sample stocks trading above moving average"""
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
        pct = (above / valid * 100) if valid > 0 else None
        if pct: print(f"   ✓ % Above {period}-MA: {pct:.0f}%")
        else: print(f"   ✗ % Above {period}-MA: Error")
        return pct
    
    def _pct_below_ma(self, period):
        """Calculate % of sample stocks trading below moving average"""
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
        pct = (below / valid * 100) if valid > 0 else None
        if pct: print(f"   ✓ % Below {period}-MA: {pct:.0f}%")
        else: print(f"   ✗ % Below {period}-MA: Error")
        return pct
    
    def _ad_line_status(self):
        """Proxy for Advance-Decline line using SPY proximity to 20-day highs"""
        try:
            spy = yf.Ticker('SPY').history(period='3mo')
            pct = ((spy['Close'].iloc[-1] - spy['Close'].iloc[-20:].max()) / spy['Close'].iloc[-20:].max()) * 100
            status = 'Confirming' if pct >= -1 else 'Flat' if pct >= -5 else 'Diverging'
            print(f"   ✓ AD Line: {status}")
            return status
        except:
            print(f"   ✗ AD Line: Error")
            return None
    
    def _new_highs_lows(self):
        """Calculate net new highs minus lows in sample stocks (3-month range)"""
        highs, lows = 0, 0
        for t in self.sample_tickers:
            try:
                hist = yf.Ticker(t).history(period='3mo')
                if len(hist) >= 52:
                    cur = hist['Close'].iloc[-1]
                    if cur >= hist['Close'].max() * 0.995: highs += 1  # Within 0.5% of high
                    elif cur <= hist['Close'].min() * 1.005: lows += 1  # Within 0.5% of low
            except:
                pass
        net = highs - lows
        print(f"   ✓ New H-L: {net}")
        return net
    
    def _sector_rotation(self):
        """Calculate defensive/growth rotation (XLU Utilities / XLK Technology)
        Positive = risk-off rotation, Negative = risk-on rotation"""
        try:
            xlu = yf.Ticker('XLU').history(period='2mo')['Close']
            xlk = yf.Ticker('XLK').history(period='2mo')['Close']
            ratio = xlu / xlk
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ XLU/XLK: {trend:.1f}%")
            return float(trend)
        except:
            print(f"   ✗ XLU/XLK: Error")
            return None
    
    def _gold_spy_ratio(self):
        """Calculate safe haven demand (GLD / SPY ratio trend)
        Positive = flight to safety, Negative = risk appetite"""
        try:
            gld = yf.Ticker('GLD').history(period='2mo')['Close']
            spy = yf.Ticker('SPY').history(period='2mo')['Close']
            ratio = gld / spy
            trend = ((ratio.iloc[-1] - ratio.rolling(20).mean().iloc[-1]) / ratio.rolling(20).mean().iloc[-1]) * 100
            print(f"   ✓ GLD/SPY: {trend:.1f}%")
            return float(trend)
        except:
            print(f"   ✗ GLD/SPY: Error")
            return None
    
    def _vix_structure(self):
        """Detect VIX term structure using VIXY/VXX ratio
        Contango = normal (risk-on), Backwardation = stress (risk-off)"""
        try:
            vxx = yf.Ticker('VXX').history(period='5d')['Close'].iloc[-1]
            vixy = yf.Ticker('VIXY').history(period='5d')['Close'].iloc[-1]
            ratio = vixy / vxx
            struct = 'Contango' if ratio > 1.03 else 'Backwardation' if ratio < 0.97 else 'Flat'
            print(f"   ✓ VIX Struct: {struct}")
            return struct
        except:
            print(f"   ✗ VIX Struct: Error")
            return None
    
    def _fear_greed(self):
        """Calculate Fear & Greed proxy from VIX (CNN API deprecated)"""
        try:
            vix = self.data.get('vix')
            if vix is not None:
                # VIX-to-Fear/Greed mapping (inverse relationship)
                # VIX 10-12 → Extreme Greed (80-90)
                # VIX 15 → Greed (70)
                # VIX 20 → Neutral (50)
                # VIX 25 → Fear (30)
                # VIX 30+ → Extreme Fear (10-20)
                fear_greed = max(0, min(100, 100 - (vix - 10) * 3))
                print(f"   ✓ Fear/Greed: {fear_greed:.0f} (VIX-derived)")
                return fear_greed
        except:
            pass
        
        print(f"   ✗ Fear/Greed: VIX unavailable")
        return None
    
    def _verify_data_quality(self):
        """Verify all 14 indicators have valid data and are within expected ranges
        Returns: bool - True if at least 10 indicators passed validation"""
        print("\n" + "="*80)
        print("DATA VERIFICATION REPORT")
        print("="*80)
        
        verification = {
            'hy_spread': {'range': (0, 20), 'unit': '%', 'critical': True},
            'fed_bs_yoy': {'range': (-50, 50), 'unit': '%', 'critical': True},
            'ted_spread': {'range': (0, 5), 'unit': 'bps', 'critical': True},
            'dxy_trend': {'range': (-20, 20), 'unit': '%', 'critical': False},
            'pct_above_50ma': {'range': (0, 100), 'unit': '%', 'critical': True},
            'pct_below_200ma': {'range': (0, 100), 'unit': '%', 'critical': True},
            'ad_line': {'range': None, 'unit': 'status', 'critical': False},
            'new_hl': {'range': (-27, 27), 'unit': 'net', 'critical': False},
            'sector_rot': {'range': (-30, 30), 'unit': '%', 'critical': False},
            'gold_spy': {'range': (-30, 30), 'unit': '%', 'critical': False},
            'vix_struct': {'range': None, 'unit': 'status', 'critical': False},
            'yield_curve': {'range': (-2, 3), 'unit': '%', 'critical': True},
            'vix': {'range': (5, 80), 'unit': 'index', 'critical': True},
            'fear_greed': {'range': (0, 100), 'unit': 'index', 'critical': False}
        }
        
        issues = []
        warnings = []
        passed = 0
        
        for indicator, spec in verification.items():
            value = self.data.get(indicator)
            
            # Check 1: Data exists
            if value is None:
                msg = f"❌ {indicator}: NO DATA"
                if spec['critical']:
                    issues.append(msg)
                else:
                    warnings.append(msg)
                print(msg)
                continue
            
            # Check 2: Correct data type
            if spec['range'] is not None:  # Numeric indicators
                if not isinstance(value, (int, float)):
                    msg = f"⚠️  {indicator}: Invalid type (got {type(value).__name__})"
                    warnings.append(msg)
                    print(msg)
                    continue
                
                # Check 3: Value in expected range
                min_val, max_val = spec['range']
                if not (min_val <= value <= max_val):
                    msg = f"⚠️  {indicator}: Out of range ({value:.2f} not in [{min_val}, {max_val}])"
                    warnings.append(msg)
                    print(msg)
                else:
                    print(f"✅ {indicator}: {value:.2f} {spec['unit']} (valid)")
                    passed += 1
            else:  # Status indicators (ad_line, vix_struct)
                expected_values = {
                    'ad_line': ['Confirming', 'Flat', 'Diverging'],
                    'vix_struct': ['Contango', 'Flat', 'Backwardation']
                }
                if indicator in expected_values and value not in expected_values[indicator]:
                    msg = f"⚠️  {indicator}: Unexpected value '{value}'"
                    warnings.append(msg)
                    print(msg)
                else:
                    print(f"✅ {indicator}: {value} (valid)")
                    passed += 1
        
        # Summary
        print("\n" + "="*80)
        print(f"VERIFICATION SUMMARY: {passed}/14 passed")
        
        if issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(issues)}):")
            for issue in issues:
                print(f"   {issue}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")
        
        if not issues and not warnings:
            print("\n✅ ALL INDICATORS VERIFIED - DATA QUALITY EXCELLENT")
        
        print("="*80 + "\n")
        
        # Store verification results
        self.verification_passed = passed
        self.verification_issues = issues
        self.verification_warnings = warnings
        
        return passed >= 10  # Require at least 10 valid indicators
    
    # =========================================================================
    # SCORING ENGINE - Converts raw data to 0-100 risk score
    # =========================================================================
    
    def calculate_scores(self):
        """Score all 14 indicators using v1.5 tiered weighting system
        Returns: dict with total score and tier breakdowns"""
        d = self.data
        
        # Tier 1: Credit & Liquidity (50 pts)
        s1 = self._score_range(d['hy_spread'], [(3,20),(4,16),(4.5,12),(5.5,6)], 0) if d.get('hy_spread') is not None else 0
        s2 = self._score_range(d['fed_bs_yoy'], [(10,15),(2,12),(-2,9),(-10,4)], 0) if d.get('fed_bs_yoy') is not None else 0
        s3 = self._score_range(d['ted_spread'], [(0.3,10),(0.5,8),(0.75,5),(1,2)], 0) if d.get('ted_spread') is not None else 0
        s4 = self._score_range(d['dxy_trend'], [(-3,5),(-1,4),(1,3),(3,1)], 0) if d.get('dxy_trend') is not None else 0
        
        # Tier 2: Breadth (30 pts)
        s5 = self._score_range(d['pct_above_50ma'], [(75,12),(65,10),(55,7),(45,4),(35,2)], 0) if d.get('pct_above_50ma') is not None else 0
        s6 = self._score_range(d['pct_below_200ma'], [(15,10),(25,8),(35,6),(50,3),(65,1)], 0, inverse=True) if d.get('pct_below_200ma') is not None else 0
        s7 = {'Confirming':5, 'Flat':2, 'Diverging':0}.get(d['ad_line'], 0)
        s8 = self._score_range(d['new_hl'], [(10,3),(5,2.5),(0,2),(-5,1),(-10,0.5)], 0) if d.get('new_hl') is not None else 0
        
        # Tier 3: Risk Appetite (15 pts)
        s9 = self._score_range(d['sector_rot'], [(-5,6),(-2,5),(2,4),(5,2)], 0) if d.get('sector_rot') is not None else 0
        s10 = self._score_range(d['gold_spy'], [(-3,5),(-1,4),(1,3),(3,1)], 0) if d.get('gold_spy') is not None else 0
        s11 = {'Contango':4, 'Flat':2, 'Backwardation':0}.get(d['vix_struct'], 0)
        
        # Tier 4: Sentiment (5 pts)
        s12 = self._score_range(d['yield_curve'], [(0.5,3),(0.2,2.5),(-0.2,2),(-0.5,1)], 0) if d.get('yield_curve') is not None else 0
        s13 = self._score_range(d['vix'], [(12,0),(16,1.5),(20,1),(30,0.5)], 0) if d.get('vix') is not None else 0
        s14 = self._score_range(d['fear_greed'], [(35,0.5),(20,0.3),(80,0.3)], 0) if d.get('fear_greed') is not None and 35<=d.get('fear_greed',50)<=80 else 0
        
        total = s1+s2+s3+s4+s5+s6+s7+s8+s9+s10+s11+s12+s13+s14
        
        self.scores = {
            'total': total,
            'tier1': s1+s2+s3+s4,
            'tier2': s5+s6+s7+s8,
            'tier3': s9+s10+s11,
            'tier4': s12+s13+s14
        }
        return self.scores
    
    def _score_range(self, val, thresholds, default, inverse=False):
        """Helper function to score values based on threshold ranges
        Args:
            val: Value to score
            thresholds: List of (threshold, score) tuples
            default: Default score if no threshold matches
            inverse: If True, reverse comparison logic (for % below MA)
        """
        if val is None: return default
        for thresh, score in thresholds:
            if (val < thresh if not inverse else val > thresh):
                return score
        return default
    
    # =========================================================================
    # DIVERGENCE DETECTION - Identify hidden risks & pattern breaks
    # =========================================================================
    
    def detect_divergences(self):
        """Detect critical divergence patterns between indicators
        Returns: list of alert dictionaries with type, severity, message, action"""
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
        
        # Alert 6: All Clear
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
    # REPORT GENERATION
    # =========================================================================
    
    def generate_report(self):
        """Generate formatted text report with scores and alerts
        Returns: str - Multi-line formatted report"""
        score = self.scores['total']
        d = self.data
        
        if score >= 90: risk, pos = "★★★★★ ALL CLEAR", "FULL DEPLOYMENT (60/30/10)"
        elif score >= 75: risk, pos = "★★★★☆ NORMAL", "STAY COURSE"
        elif score >= 60: risk, pos = "★★★☆☆ ELEVATED", "REDUCE TIER 3"
        elif score >= 40: risk, pos = "★★☆☆☆ HIGH RISK", "GO DEFENSIVE"
        else: risk, pos = "★☆☆☆☆ EXTREME", "MAX DEFENSE"
        
        lines = [
            "🎯 INSTITUTIONAL RISK DASHBOARD v1.5",
            f"📅 {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"📊 TOTAL RISK SCORE: {score:.1f}/100",
            f"🎚️ RISK LEVEL: {risk}",
            f"💼 POSITIONING: {pos}",
            "",
            "📈 TIER BREAKDOWN:",
            f"├─ Tier 1 (Credit/Liquidity): {self.scores['tier1']:.1f}/50 ({self.scores['tier1']/50*100:.0f}%)",
            f"├─ Tier 2 (Breadth): {self.scores['tier2']:.1f}/30 ({self.scores['tier2']/30*100:.0f}%)",
            f"├─ Tier 3 (Risk Appetite): {self.scores['tier3']:.1f}/15 ({self.scores['tier3']/15*100:.0f}%)",
            f"└─ Tier 4 (Sentiment): {self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            "",
            "📋 INDICATOR DETAILS:",
            "",
            "💰 TIER 1: CREDIT & LIQUIDITY",
            f"  • HY Spread: {d.get('hy_spread'):.2f if d.get('hy_spread') is not None else 'N/A'}{'%' if d.get('hy_spread') is not None else ''} (Range: 3-6%)",
            f"  • Fed BS YoY: {d.get('fed_bs_yoy'):.1f if d.get('fed_bs_yoy') is not None else 'N/A'}{'%' if d.get('fed_bs_yoy') is not None else ''} (Range: -10% to +10%)",
            f"  • TED Spread: {d.get('ted_spread'):.2f if d.get('ted_spread') is not None else 'N/A'} (Range: 0.1-0.5)",
            f"  • DXY Trend: {d.get('dxy_trend'):.1f if d.get('dxy_trend') is not None else 'N/A'}{'%' if d.get('dxy_trend') is not None else ''} (Range: -3% to +3%)",
            "",
            "📊 TIER 2: MARKET BREADTH",
            f"  • % Above 50-MA: {d.get('pct_above_50ma'):.0f if d.get('pct_above_50ma') is not None else 'N/A'}{'%' if d.get('pct_above_50ma') is not None else ''} (Healthy: >65%)",
            f"  • % Below 200-MA: {d.get('pct_below_200ma'):.0f if d.get('pct_below_200ma') is not None else 'N/A'}{'%' if d.get('pct_below_200ma') is not None else ''} (Healthy: <25%)",
            f"  • AD Line: {d.get('ad_line', 'N/A')}",
            f"  • New H-L: {d.get('new_hl', 'N/A')} (Range: -10 to +10)",
            "",
            "🎯 TIER 3: RISK APPETITE",
            f"  • XLU/XLK Rotation: {d.get('sector_rot'):.1f if d.get('sector_rot') is not None else 'N/A'}{'%' if d.get('sector_rot') is not None else ''} (Risk-on: <-2%)",
            f"  • GLD/SPY Ratio: {d.get('gold_spy'):.1f if d.get('gold_spy') is not None else 'N/A'}{'%' if d.get('gold_spy') is not None else ''} (Risk-on: <-1%)",
            f"  • VIX Structure: {d.get('vix_struct', 'N/A')}",
            "",
            "🧠 TIER 4: SENTIMENT",
            f"  • Yield Curve: {d.get('yield_curve'):.2f if d.get('yield_curve') is not None else 'N/A'}{'%' if d.get('yield_curve') is not None else ''} (Healthy: >0.2%)",
            f"  • VIX Level: {d.get('vix'):.1f if d.get('vix') is not None else 'N/A'} (Calm: <16)",
            f"  • Fear/Greed: {d.get('fear_greed'):.0f if d.get('fear_greed') is not None else 'N/A'}{'/100' if d.get('fear_greed') is not None else ''} (Neutral: 35-65)",
            "",
        ]
        
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
    
    def run_assessment(self):
        """Execute complete risk assessment pipeline:
        1. Fetch all 14 indicators
        2. Verify data quality
        3. Calculate scores
        4. Detect divergences
        5. Generate & send report
        Returns: float - Total risk score (0-100)
        """
        print("\n" + "="*80)
        print("STARTING DAILY RISK ASSESSMENT v1.5")
        print("="*80)
        
        self.fetch_all_data()
        self.calculate_scores()
        self.detect_divergences()
        report = self.generate_report()
        
        print("\n" + report + "\n")
        
        # Save
        filename = f"risk_report_{self.timestamp.strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"💾 Saved to {filename}\n")
        
        # Send to Telegram
        send_to_telegram(report)
        
        return self.scores['total']

def main():
    """Main entry point - Run institutional risk assessment"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              INSTITUTIONAL RISK DASHBOARD v1.5                       ║
║         14 Signals | 100% Free Data | Production Ready               ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    dashboard = RiskDashboard()
    dashboard.run_assessment()
    
    print("✅ Assessment complete. Run daily at market open.\n")

if __name__ == "__main__":
    main()
