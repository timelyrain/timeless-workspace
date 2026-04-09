"""
╔══════════════════════════════════════════════════════════════════════╗
║                   MARKET CYCLE DETECTOR v1.0                         ║
╚══════════════════════════════════════════════════════════════════════╝

Identifies the current economic regime and market cycle phase daily.
Pure data output — no AI interpretation layer.

TWO-LAYER FRAMEWORK:
  Layer 1 — Economic Regime (2×2 Growth × Inflation matrix):
    GOLDILOCKS (Growth↑, Inflation↓)  — best equity environment
    REFLATION  (Growth↑, Inflation↑)  — commodities, cyclicals, TIPS
    STAGFLATION(Growth↓, Inflation↑)  — gold, cash, hard assets
    CONTRACTION(Growth↓, Inflation↓)  — bonds, defensives, gold

  Layer 2 — Market Cycle Phase (5 phases):
    EARLY (Recovery) → MID (Expansion) → LATE (Overheating)
    → DOWNTURN (Contraction) → RECESSION

SCORING:
  Growth Score   (0–50 pts): T10Y2Y + T10Y3M + IndPro + Claims + Sahm/UNRATE
  Inflation Score(0–50 pts): CPI YoY + 5Y Breakeven + PPI + Real Rates (DFII10)
  Cycle Score    (0–100 pts): HY spreads + IG spreads + SPY/200DMA + RSP/SPY breadth
                               + XLY/XLP rotation + XLF leadership + Copper/Gold + NFCI
                               + Yield curve trend

ALL FREE DATA:
  FRED (daily):   T10Y2Y, T10Y3M, T5YIE, DFII10, BAMLH0A0HYM2, BAMLC0A0CM, NFCI
  FRED (monthly): CPIAUCSL, PPIACO, INDPRO, UNRATE
  FRED (weekly):  ICSA
  yfinance:       SPY, RSP, XLY, XLP, XLF, HG=F, GLD

SYSTEM: $1M Portfolio Cycle Intelligence (Arthur Protocol)
"""

import yfinance as yf
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
    'FRED_API_KEY':      os.getenv('FRED_API_KEY', 'YOUR_FRED_API_KEY_HERE'),
    'TELEGRAM_TOKEN':    os.getenv('TELEGRAM_TOKEN_RISK'),
    'CHAT_ID':           os.getenv('CHAT_ID'),
    'CYCLE_HISTORY_FILE': 'cycle_history.json',
}

if CONFIG['FRED_API_KEY'] == 'YOUR_FRED_API_KEY_HERE':
    print("⚠️  WARNING: FRED_API_KEY not set.")

fred = Fred(api_key=CONFIG['FRED_API_KEY'])

# =============================================================================
# METADATA TABLES
# =============================================================================

PHASE_META = {
    'EARLY': {
        'icon': '🌱',
        'label': 'Early Cycle (Recovery)',
        'description': (
            'Post-trough recovery. Credit spreads tightening, breadth expanding, '
            'financials leading. Cyclicals and growth outperform.'
        ),
        'assets': 'Financials, Materials, Industrials, Small/Mid-cap, EM equities',
    },
    'MID': {
        'icon': '📈',
        'label': 'Mid Cycle (Expansion)',
        'description': (
            'Peak expansion. Broad breadth, PMI well above 50, credit stable, '
            'momentum strong across all sectors.'
        ),
        'assets': 'Broad equities, growth, quality, global diversification',
    },
    'LATE': {
        'icon': '⚡',
        'label': 'Late Cycle (Overheating)',
        'description': (
            'Growth decelerating. Breadth narrowing, inflation rising, '
            'yield curve flattening, credit spreads ticking wider.'
        ),
        'assets': 'Energy, Materials, TIPS, Defensives (XLU/XLP), Gold',
    },
    'DOWNTURN': {
        'icon': '📉',
        'label': 'Downturn (Contraction)',
        'description': (
            'Credit stress rising. SPY at/below 200DMA. Breadth collapsed. '
            'Risk-off regime — capital preservation priority.'
        ),
        'assets': 'Cash, Gold, Long bonds, Defensives (XLU, XLP), Hedges',
    },
    'RECESSION': {
        'icon': '❄️',
        'label': 'Recession',
        'description': (
            'Sahm Rule triggered. HY spreads blown out. Equity breadth collapsed. '
            'Maximum defense — align with EXTREME risk regime.'
        ),
        'assets': 'Cash, Treasuries, Gold only. Short equities via hedges.',
    },
}

REGIME_META = {
    'GOLDILOCKS': {
        'icon': '🟢',
        'label': 'Goldilocks (Growth↑  Inflation↓)',
        'description': 'Best equity environment. Real earnings growth without inflation headwinds.',
        'assets': 'Equities (growth + value), EM, investment-grade credit',
    },
    'REFLATION': {
        'icon': '🟡',
        'label': 'Reflation (Growth↑  Inflation↑)',
        'description': 'Early-to-mid cycle with rising prices. Commodities, cyclicals, TIPS outperform.',
        'assets': 'Commodities, energy, financials, EM equities, TIPS',
    },
    'STAGFLATION': {
        'icon': '🔴',
        'label': 'Stagflation (Growth↓  Inflation↑)',
        'description': 'Worst equity environment. Central banks constrained. Hard assets win.',
        'assets': 'Gold, commodities, cash, TIPS — avoid equities and long bonds',
    },
    'CONTRACTION': {
        'icon': '🟠',
        'label': 'Contraction (Growth↓  Inflation↓)',
        'description': 'Deflationary pressure. Duration assets outperform. Equities defensive only.',
        'assets': 'Long bonds (duration), cash, gold, defensive equities',
    },
}

# Sleeve guidance per phase — specific to this portfolio's 7-sleeve structure
PHASE_SLEEVE_GUIDANCE = {
    'EARLY': {
        'global_triads': 'HOLD — accumulate dips, recovery broadening globally',
        'four_horsemen': 'ADD — cyclicals and growth lead early cycle (EQCH, 9807)',
        'cash_cow':      'INCREASE CSPs — vol still elevated, sell puts on quality pullbacks',
        'alpha':         'ADD — asymmetric calls on beaten-down quality names',
        'omega':         'TRIM — tail risk falling, monetize residual hedges',
        'vault':         'TRIM SLOWLY — gold lags in early risk-on recovery',
        'war_chest':     'DEPLOY — put dry powder to work in cyclicals and growth',
    },
    'MID': {
        'global_triads': 'HOLD FULL — market breadth supports full core position',
        'four_horsemen': 'HOLD FULL — expansion favours all four engines',
        'cash_cow':      'FULL WHEEL — max deployment across entire watchlist',
        'alpha':         'HOLD — momentum supportive, no new size added',
        'omega':         'BASE ONLY — 2% insurance, no overhedging in expansion',
        'vault':         'BASE WEIGHT — 8%, no outperformance expected mid cycle',
        'war_chest':     'MINIMUM — 7% base cash, deploy excess capital',
    },
    'LATE': {
        'global_triads': 'HOLD — tilt toward XMME/ES3, reduce EQCH overweight',
        'four_horsemen': 'TRIM GROWTH — reduce EQCH/CBUK, hold INRA (energy) and GRDU',
        'cash_cow':      'TILT DEFENSIVE — CSPs on V, JPM, PEP; reduce tech-heavy positions',
        'alpha':         'EXIT — close speculative longs, lock profits',
        'omega':         'BUILD — begin adding bear spreads on any rally',
        'vault':         'ADD GSD — gold outperforms late cycle and stagflation',
        'war_chest':     'RAISE CASH — build toward 10-15% ahead of transition',
    },
    'DOWNTURN': {
        'global_triads': 'HOLD CORE — VWRA/ES3 only; trim 82846/XMME (EM risk elevated)',
        'four_horsemen': 'REDUCE — exit EQCH/CBUK, retain INRA defensively',
        'cash_cow':      'PAUSE — stand down if portfolio drawdown exceeds 8%',
        'alpha':         'FLAT — zero speculative exposure',
        'omega':         'ELEVATED — maximize bear spread allocation per risk regime',
        'vault':         'OVERWEIGHT GSD — gold is primary hedge instrument now',
        'war_chest':     'MAX CASH — raise toward 25-33% (align with risk regime)',
    },
    'RECESSION': {
        'global_triads': 'MINIMAL — VWRA only for long-term global beta',
        'four_horsemen': 'EXIT — liquidate all thematic/growth exposure',
        'cash_cow':      'HALT — no new puts; close existing positions before expiry',
        'alpha':         'FLAT — zero speculative exposure',
        'omega':         'MAX — monetize hedges only at deep capitulation drops',
        'vault':         'MAX OVERWEIGHT — gold + AEM at maximum allocation',
        'war_chest':     'MAX CASH — 39%+ cash; align with EXTREME risk regime',
    },
}

# =============================================================================
# TELEGRAM UTILITIES
# =============================================================================

def send_to_telegram(message):
    """Send message to Telegram with chunking for long messages"""
    if not CONFIG['TELEGRAM_TOKEN'] or not CONFIG['CHAT_ID']:
        print("⚠️  Telegram credentials not found. Skipping.")
        return False

    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendMessage"
    max_length = 4000
    chunks = []

    if len(message) <= max_length:
        chunks = [message]
    else:
        parts = message.split('\n\n')
        current = ""
        for part in parts:
            if len(current) + len(part) + 2 <= max_length:
                current += part + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = part + "\n\n"
        if current:
            chunks.append(current.strip())

    success = True
    for i, chunk in enumerate(chunks):
        payload = {
            'chat_id': CONFIG['CHAT_ID'],
            'text': chunk,
            'disable_web_page_preview': True,
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                suffix = f" (part {i+1}/{len(chunks)})" if len(chunks) > 1 else ""
                print(f"✅ Telegram sent{suffix}")
            else:
                print(f"⚠️  Telegram error: {resp.status_code}")
                success = False
        except Exception as e:
            print(f"⚠️  Telegram send failed: {e}")
            success = False

    return success


# =============================================================================
# CYCLE HISTORY MANAGER
# =============================================================================

class CycleHistoryManager:
    """
    Persists daily cycle readings to cycle_history.json (180-day rolling window).
    Used for trend display only — no confirmation gating.
    """

    def __init__(self, history_file=None):
        self.history_file = history_file or CONFIG['CYCLE_HISTORY_FILE']
        self.history = self._load()

    def _load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'cycles': []}

    def save(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            print(f"💾 Cycle history saved → {self.history_file}")
        except Exception as e:
            print(f"⚠️  Could not save cycle history: {e}")

    def add_entry(self, date, phase, regime, cycle_score,
                  growth_score, inflation_score, data_snapshot):
        """Append today's reading, dedup by date, keep 180-day window."""
        entry = {
            'date': date,
            'phase': phase,
            'regime': regime,
            'cycle_score': round(cycle_score, 1),
            'growth_score': round(growth_score, 1),
            'inflation_score': round(inflation_score, 1),
            'snapshot': data_snapshot,
        }
        self.history['cycles'] = [
            c for c in self.history['cycles'] if c['date'] != date
        ]
        self.history['cycles'].append(entry)
        cutoff = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        self.history['cycles'] = [
            c for c in self.history['cycles'] if c['date'] >= cutoff
        ]



# =============================================================================
# MARKET CYCLE DETECTOR
# =============================================================================

class CycleDetector:
    """
    Daily market cycle and economic regime detector.

    Scoring:
      growth_score   (0–50): yield curve + IndPro + claims + unemployment (Sahm)
      inflation_score(0–50): CPI + breakevens + PPI + real rates
      cycle_score    (0–100): credit + breadth + momentum + rotation + copper/gold

    Classification:
      Economic Regime: GOLDILOCKS / REFLATION / STAGFLATION / CONTRACTION
      Cycle Phase:     EARLY / MID / LATE / DOWNTURN / RECESSION
    """

    def __init__(self):
        self.timestamp = datetime.now()
        self.data = {}
        self.scores = {}
        self.growth_score = 0.0
        self.inflation_score = 0.0
        self.cycle_score = 0.0
        self.phase = None
        self.regime = None
        self.history = CycleHistoryManager()

    # =========================================================================
    # DATA FETCHING HELPERS
    # =========================================================================

    def _fred_daily(self, series_id, lookback_days=90):
        """Fetch a FRED daily series. Returns (latest_value, full_series)."""
        try:
            start = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            series = fred.get_series(series_id, observation_start=start).dropna()
            if len(series) < 2:
                return None, None
            return float(series.iloc[-1]), series
        except Exception as e:
            print(f"⚠️  FRED {series_id}: {e}")
            return None, None

    def _fred_monthly(self, series_id, months=18):
        """Fetch a FRED monthly series. Returns list of (date_str, value)."""
        try:
            start = (datetime.now() - timedelta(days=months * 31)).strftime('%Y-%m-%d')
            series = fred.get_series(series_id, observation_start=start).dropna()
            return [(str(d.date()), float(v)) for d, v in series.items()]
        except Exception as e:
            print(f"⚠️  FRED {series_id}: {e}")
            return []

    def _fred_weekly(self, series_id, weeks=52):
        """Fetch a FRED weekly series. Returns list of (date_str, value)."""
        try:
            start = (datetime.now() - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
            series = fred.get_series(series_id, observation_start=start).dropna()
            return [(str(d.date()), float(v)) for d, v in series.items()]
        except Exception as e:
            print(f"⚠️  FRED {series_id}: {e}")
            return []

    def _yf_close(self, ticker, days=250):
        """Fetch yfinance Close price series."""
        try:
            df = yf.Ticker(ticker).history(period=f"{days}d")
            if df.empty:
                return None
            return df['Close']
        except Exception as e:
            print(f"⚠️  yfinance {ticker}: {e}")
            return None

    def _3m_change_pct(self, values_list):
        """% change: last entry vs entry 3 steps earlier (monthly cadence)."""
        if len(values_list) < 4:
            return None
        old = values_list[-4][1]
        new = values_list[-1][1]
        return (new - old) / old * 100 if old else None

    # =========================================================================
    # FETCH ALL DATA
    # =========================================================================

    def fetch_all_data(self):
        """Pull all FRED and yfinance data needed for scoring."""
        print("\n📡 Fetching market cycle data...")

        # ── Yield Curve (daily) ───────────────────────────────────────────────
        t10y2y, t10y2y_s = self._fred_daily('T10Y2Y', 90)
        t10y3m, _        = self._fred_daily('T10Y3M', 90)
        self.data['t10y2y'] = t10y2y
        self.data['t10y3m'] = t10y3m

        # 3-month change in T10Y2Y (curve steepening/flattening signal)
        if t10y2y_s is not None and len(t10y2y_s) >= 63:
            self.data['t10y2y_change_3m'] = float(t10y2y_s.iloc[-1] - t10y2y_s.iloc[-63])
        elif t10y2y_s is not None and len(t10y2y_s) > 1:
            self.data['t10y2y_change_3m'] = float(t10y2y_s.iloc[-1] - t10y2y_s.iloc[0])
        else:
            self.data['t10y2y_change_3m'] = None

        # ── Inflation Market Indicators (daily) ────────────────────────────────
        t5yie, t5yie_s = self._fred_daily('T5YIE', 90)
        dfii10, _      = self._fred_daily('DFII10', 90)
        self.data['t5yie']  = t5yie
        self.data['dfii10'] = dfii10

        # 3-month trend in 5Y breakeven
        if t5yie_s is not None and len(t5yie_s) >= 63:
            self.data['t5yie_change_3m'] = float(t5yie_s.iloc[-1] - t5yie_s.iloc[-63])
        elif t5yie_s is not None and len(t5yie_s) > 1:
            self.data['t5yie_change_3m'] = float(t5yie_s.iloc[-1] - t5yie_s.iloc[0])
        else:
            self.data['t5yie_change_3m'] = None

        # ── Credit Spreads (daily) ─────────────────────────────────────────────
        hy, hy_s = self._fred_daily('BAMLH0A0HYM2', 60)
        ig, _    = self._fred_daily('BAMLC0A0CM', 60)
        self.data['hy_spread'] = hy
        self.data['ig_spread'] = ig

        # 30-day trend in HY spread (positive = widening = deteriorating)
        if hy_s is not None and len(hy_s) >= 20:
            self.data['hy_spread_trend'] = float(hy_s.iloc[-1] - hy_s.iloc[-20])
        else:
            self.data['hy_spread_trend'] = 0.0

        # ── Financial Conditions (weekly) ─────────────────────────────────────
        nfci, _ = self._fred_daily('NFCI', 30)
        self.data['nfci'] = nfci

        # ── Monthly Macro Series ───────────────────────────────────────────────
        cpi_series    = self._fred_monthly('CPIAUCSL', 18)
        ppi_series    = self._fred_monthly('PPIACO', 18)
        indpro_series = self._fred_monthly('INDPRO', 18)
        unrate_series = self._fred_monthly('UNRATE', 18)

        # CPI YoY + 6M directional trend
        if len(cpi_series) >= 13:
            cpi_now     = cpi_series[-1][1]
            cpi_12m_ago = cpi_series[-13][1]
            cpi_6m_ago  = cpi_series[-7][1]
            self.data['cpi_yoy']   = (cpi_now - cpi_12m_ago) / cpi_12m_ago * 100 if cpi_12m_ago else None
            self.data['cpi_trend'] = cpi_now - cpi_6m_ago   # positive = rising
        else:
            self.data['cpi_yoy']   = None
            self.data['cpi_trend'] = None

        # PPI 3-month % change
        self.data['ppi_trend'] = self._3m_change_pct(ppi_series)

        # Industrial Production — 3M annualised growth rate
        if len(indpro_series) >= 4:
            ip_now    = indpro_series[-1][1]
            ip_3m_ago = indpro_series[-4][1]
            ip_3m_pct = (ip_now - ip_3m_ago) / ip_3m_ago * 100 if ip_3m_ago else None
            self.data['indpro_annualized'] = ip_3m_pct * 4 if ip_3m_pct is not None else None
        else:
            self.data['indpro_annualized'] = None

        # Sahm Rule + Unemployment trend
        if len(unrate_series) >= 15:
            u_vals = [v for _, v in unrate_series]
            curr_3m_avg = sum(u_vals[-3:]) / 3
            # Min of all rolling 3M averages in prior 12 months
            rolling_3m = [
                sum(u_vals[i:i+3]) / 3
                for i in range(len(u_vals) - 15, len(u_vals) - 2)
            ]
            self.data['sahm_value']     = curr_3m_avg - min(rolling_3m) if rolling_3m else 0.0
            self.data['unrate_current'] = u_vals[-1]
            self.data['unrate_3m_trend']= u_vals[-1] - u_vals[-4]
        else:
            self.data['sahm_value']      = None
            self.data['unrate_current']  = None
            self.data['unrate_3m_trend'] = None

        # ── Initial Jobless Claims (weekly) ───────────────────────────────────
        icsa_series = self._fred_weekly('ICSA', 26)
        if len(icsa_series) >= 16:
            icsa_vals = [v for _, v in icsa_series]
            curr_4wk  = sum(icsa_vals[-4:]) / 4
            prior_4wk = sum(icsa_vals[-16:-12]) / 4  # 12 weeks prior
            self.data['icsa_trend'] = (curr_4wk - prior_4wk) / prior_4wk * 100 if prior_4wk else None
        else:
            self.data['icsa_trend'] = None

        # ── yfinance: Market Structure ─────────────────────────────────────────
        print("📊 Fetching market structure data...")

        spy = self._yf_close('SPY', 250)
        rsp = self._yf_close('RSP', 250)
        xly = self._yf_close('XLY', 100)
        xlp = self._yf_close('XLP', 100)
        xlf = self._yf_close('XLF', 100)

        # SPY vs 200-day MA
        if spy is not None and len(spy) >= 200:
            spy_now    = float(spy.iloc[-1])
            spy_200dma = float(spy.iloc[-200:].mean())
            self.data['spy_vs_200dma_pct'] = (spy_now - spy_200dma) / spy_200dma * 100
        else:
            self.data['spy_vs_200dma_pct'] = None

        # RSP/SPY ratio 3M trend — breadth proxy (positive = broad participation)
        if spy is not None and rsp is not None:
            try:
                ratio = (rsp / spy).dropna()
                if len(ratio) >= 63:
                    self.data['rsp_spy_ratio_trend'] = (
                        float(ratio.iloc[-1]) - float(ratio.iloc[-63])
                    ) / float(ratio.iloc[-63]) * 100
                elif len(ratio) > 1:
                    self.data['rsp_spy_ratio_trend'] = (
                        float(ratio.iloc[-1]) - float(ratio.iloc[0])
                    ) / float(ratio.iloc[0]) * 100
                else:
                    self.data['rsp_spy_ratio_trend'] = None
            except Exception:
                self.data['rsp_spy_ratio_trend'] = None
        else:
            self.data['rsp_spy_ratio_trend'] = None

        # XLY/XLP ratio — risk appetite (discretionary vs staples)
        if xly is not None and xlp is not None:
            try:
                ratio = (xly / xlp).dropna()
                if len(ratio) >= 2:
                    self.data['xly_xlp_ratio'] = float(ratio.iloc[-1])
                    n = min(63, len(ratio) - 1)
                    self.data['xly_xlp_trend'] = (
                        float(ratio.iloc[-1]) - float(ratio.iloc[-n-1])
                    ) / float(ratio.iloc[-n-1]) * 100
                else:
                    self.data['xly_xlp_ratio'] = None
                    self.data['xly_xlp_trend'] = None
            except Exception:
                self.data['xly_xlp_ratio'] = None
                self.data['xly_xlp_trend'] = None
        else:
            self.data['xly_xlp_ratio'] = None
            self.data['xly_xlp_trend'] = None

        # XLF vs SPY relative 3M performance — financials leadership (early cycle)
        if xlf is not None and spy is not None:
            try:
                n = min(63, len(xlf) - 1, len(spy) - 1)
                xlf_ret = (float(xlf.iloc[-1]) - float(xlf.iloc[-n-1])) / float(xlf.iloc[-n-1]) * 100
                spy_ret = (float(spy.iloc[-1]) - float(spy.iloc[-n-1])) / float(spy.iloc[-n-1]) * 100
                self.data['xlf_relative'] = xlf_ret - spy_ret
            except Exception:
                self.data['xlf_relative'] = None
        else:
            self.data['xlf_relative'] = None

        # Copper/Gold ratio 3M trend — growth vs fear barometer
        try:
            copper = self._yf_close('HG=F', 100)
            gold   = self._yf_close('GLD', 100)
            if copper is not None and gold is not None:
                ratio = (copper / gold).dropna()
                n = min(63, len(ratio) - 1)
                if len(ratio) >= 2:
                    self.data['copper_gold_ratio'] = float(ratio.iloc[-1])
                    self.data['copper_gold_trend'] = (
                        float(ratio.iloc[-1]) - float(ratio.iloc[-n-1])
                    ) / float(ratio.iloc[-n-1]) * 100
                else:
                    self.data['copper_gold_ratio'] = None
                    self.data['copper_gold_trend'] = None
            else:
                self.data['copper_gold_ratio'] = None
                self.data['copper_gold_trend'] = None
        except Exception as e:
            print(f"⚠️  Copper/Gold: {e}")
            self.data['copper_gold_ratio'] = None
            self.data['copper_gold_trend'] = None

        print("✅ Data fetch complete.\n")

    # =========================================================================
    # SCORING
    # =========================================================================

    def score_growth(self):
        """
        Growth Score — 0 to 50 pts across 5 indicators.
        ≥25 = growth accelerating / positive; <25 = decelerating / negative.
        """
        s = {}

        # 1. T10Y2Y — yield curve level (0–10 pts)
        v = self.data.get('t10y2y')
        if v is not None:
            if v >= 1.50:    pts = 10
            elif v >= 0.75:  pts = 8
            elif v >= 0.25:  pts = 6
            elif v >= 0.00:  pts = 4
            elif v >= -0.25: pts = 2
            elif v >= -0.75: pts = 1
            else:             pts = 0
        else:
            pts = 5  # neutral on missing data
        s['t10y2y'] = pts

        # 2. T10Y3M — yield curve level, more predictive for recession (0–10 pts)
        v = self.data.get('t10y3m')
        if v is not None:
            if v >= 2.00:    pts = 10
            elif v >= 1.00:  pts = 8
            elif v >= 0.00:  pts = 5
            elif v >= -0.50: pts = 2
            else:             pts = 0
        else:
            pts = 5
        s['t10y3m'] = pts

        # 3. Industrial Production — 3M annualised growth rate (0–10 pts)
        v = self.data.get('indpro_annualized')
        if v is not None:
            if v >= 4.0:    pts = 10
            elif v >= 2.0:  pts = 8
            elif v >= 0.5:  pts = 6
            elif v >= -0.5: pts = 4
            elif v >= -2.0: pts = 2
            else:            pts = 0
        else:
            pts = 5
        s['indpro'] = pts

        # 4. Initial Jobless Claims 4W MA trend vs 12W ago (0–10 pts)
        #    Negative trend = claims falling = good
        v = self.data.get('icsa_trend')
        if v is not None:
            if v <= -10:  pts = 10
            elif v <= -5: pts = 8
            elif v <= -2: pts = 6
            elif v <= 2:  pts = 5   # stable
            elif v <= 6:  pts = 3
            elif v <= 10: pts = 1
            else:          pts = 0
        else:
            pts = 5
        s['icsa'] = pts

        # 5. Sahm Rule + Unemployment trend (0–10 pts)
        sahm         = self.data.get('sahm_value')
        unrate_trend = self.data.get('unrate_3m_trend')
        if sahm is not None:
            if sahm >= 0.50:   pts = 0   # recession threshold breached
            elif sahm >= 0.30: pts = 2
            elif sahm >= 0.20: pts = 4
            elif unrate_trend is not None and unrate_trend > 0.2:
                                pts = 5   # rising, not yet alarming
            elif unrate_trend is not None and unrate_trend <= 0:
                                pts = 9   # unemployment falling
            else:               pts = 7
        else:
            pts = 5
        s['sahm'] = pts

        self.growth_score = sum(s.values())
        self.scores['growth'] = s
        print(f"  Growth:    {self.growth_score:.0f}/50  {s}")
        return self.growth_score

    def score_inflation(self):
        """
        Inflation Score — 0 to 50 pts across 4 indicators.
        ≥25 = inflation rising/hot; <25 = falling/contained.
        """
        s = {}

        # 1. CPI YoY level + 6M directional trend (0–15 pts)
        cpi_yoy   = self.data.get('cpi_yoy')
        cpi_trend = self.data.get('cpi_trend')
        if cpi_yoy is not None:
            if cpi_yoy >= 5.0:   lv = 10
            elif cpi_yoy >= 4.0: lv = 8
            elif cpi_yoy >= 3.0: lv = 6
            elif cpi_yoy >= 2.5: lv = 5
            elif cpi_yoy >= 2.0: lv = 3
            elif cpi_yoy >= 1.0: lv = 2
            else:                 lv = 0
            if cpi_trend is not None:
                tv = 4 if cpi_trend > 0.5 else (2 if cpi_trend > 0 else (1 if cpi_trend > -0.5 else 0))
            else:
                tv = 2
            s['cpi'] = lv + tv
        else:
            s['cpi'] = 7

        # 2. 5Y Breakeven Inflation — level + 3M trend (0–15 pts)
        t5yie       = self.data.get('t5yie')
        t5yie_trend = self.data.get('t5yie_change_3m')
        if t5yie is not None:
            if t5yie >= 3.0:   lv = 10
            elif t5yie >= 2.5: lv = 8
            elif t5yie >= 2.2: lv = 6
            elif t5yie >= 2.0: lv = 4
            elif t5yie >= 1.8: lv = 2
            else:               lv = 0
            if t5yie_trend is not None:
                tv = 4 if t5yie_trend > 0.2 else (2 if t5yie_trend > 0 else (1 if t5yie_trend > -0.2 else 0))
            else:
                tv = 2
            s['breakeven'] = lv + tv
        else:
            s['breakeven'] = 7

        # 3. PPI — 3M % change (0–10 pts)
        v = self.data.get('ppi_trend')
        if v is not None:
            if v >= 3.0:   pts = 10
            elif v >= 1.5: pts = 8
            elif v >= 0.5: pts = 6
            elif v >= -0.5:pts = 4
            elif v >= -2.0:pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['ppi'] = pts

        # 4. Real 10Y Rate (DFII10) — deeply negative = inflationary (0–10 pts)
        v = self.data.get('dfii10')
        if v is not None:
            if v <= -1.5:  pts = 10
            elif v <= -0.5:pts = 8
            elif v <= 0.0: pts = 6
            elif v <= 0.5: pts = 4
            elif v <= 1.5: pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['real_rate'] = pts

        self.inflation_score = sum(s.values())
        self.scores['inflation'] = s
        print(f"  Inflation: {self.inflation_score:.0f}/50  {s}")
        return self.inflation_score

    def score_cycle(self):
        """
        Cycle Score — 0 to 100 pts across 9 market structure indicators.
        High = healthy expansion; Low = contraction/recession stress.
        """
        s = {}

        # 1. HY Credit Spread — level + 30d trend modifier (0–20 pts)
        hy       = self.data.get('hy_spread')
        hy_trend = self.data.get('hy_spread_trend', 0.0)
        if hy is not None:
            if hy < 300:   base = 20
            elif hy < 350: base = 16
            elif hy < 400: base = 12
            elif hy < 500: base = 8
            elif hy < 650: base = 4
            elif hy < 800: base = 1
            else:           base = 0
            # Trend modifier: tightening = +2, widening = -2
            mod = -2 if (hy_trend or 0) > 30 else (2 if (hy_trend or 0) < -20 else 0)
            s['hy_spread'] = max(0, min(20, base + mod))
        else:
            s['hy_spread'] = 10

        # 2. IG Credit Spread — level (0–10 pts)
        ig = self.data.get('ig_spread')
        if ig is not None:
            if ig < 70:    pts = 10
            elif ig < 90:  pts = 8
            elif ig < 110: pts = 6
            elif ig < 140: pts = 4
            elif ig < 180: pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['ig_spread'] = pts

        # 3. SPY vs 200DMA % deviation (0–15 pts)
        v = self.data.get('spy_vs_200dma_pct')
        if v is not None:
            if v >= 10:   pts = 15
            elif v >= 5:  pts = 12
            elif v >= 2:  pts = 9
            elif v >= 0:  pts = 6
            elif v >= -3: pts = 3
            elif v >= -8: pts = 1
            else:          pts = 0
        else:
            pts = 7
        s['spy_200dma'] = pts

        # 4. RSP/SPY ratio 3M trend — breadth proxy (0–10 pts)
        #    Positive = equal-weight outperforming = broad participation
        v = self.data.get('rsp_spy_ratio_trend')
        if v is not None:
            if v >= 3.0:   pts = 10
            elif v >= 1.0: pts = 8
            elif v >= 0.0: pts = 6
            elif v >= -2.0:pts = 4
            elif v >= -4.0:pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['breadth'] = pts

        # 5. XLY/XLP ratio 3M trend — risk appetite (0–10 pts)
        v = self.data.get('xly_xlp_trend')
        if v is not None:
            if v >= 5.0:   pts = 10
            elif v >= 2.0: pts = 8
            elif v >= 0.0: pts = 6
            elif v >= -3.0:pts = 4
            elif v >= -6.0:pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['xly_xlp'] = pts

        # 6. XLF relative vs SPY 3M — financials leadership (0–10 pts)
        v = self.data.get('xlf_relative')
        if v is not None:
            if v >= 5.0:   pts = 10
            elif v >= 2.0: pts = 8
            elif v >= 0.0: pts = 6
            elif v >= -3.0:pts = 4
            elif v >= -6.0:pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['xlf_lead'] = pts

        # 7. Copper/Gold ratio 3M trend — growth vs fear (0–10 pts)
        v = self.data.get('copper_gold_trend')
        if v is not None:
            if v >= 8.0:   pts = 10
            elif v >= 3.0: pts = 8
            elif v >= 0.0: pts = 6
            elif v >= -4.0:pts = 4
            elif v >= -8.0:pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['copper_gold'] = pts

        # 8. NFCI — Chicago Fed Financial Conditions (0–10 pts)
        #    Negative NFCI = accommodative (good); Positive = tightening (bad)
        v = self.data.get('nfci')
        if v is not None:
            if v <= -0.50: pts = 10
            elif v <= -0.2:pts = 8
            elif v <= 0.0: pts = 6
            elif v <= 0.3: pts = 4
            elif v <= 0.6: pts = 2
            else:           pts = 0
        else:
            pts = 5
        s['nfci'] = pts

        # 9. Yield curve 3M trend — steepening vs flattening (0–5 pts)
        v = self.data.get('t10y2y_change_3m')
        if v is not None:
            if v >= 0.5:   pts = 5
            elif v >= 0.2: pts = 4
            elif v >= 0.0: pts = 3
            elif v >= -0.2:pts = 2
            else:           pts = 0
        else:
            pts = 2
        s['curve_trend'] = pts

        self.cycle_score = sum(s.values())
        self.scores['cycle'] = s
        print(f"  Cycle:     {self.cycle_score:.0f}/100  {s}")
        return self.cycle_score

    # =========================================================================
    # CLASSIFICATION
    # =========================================================================

    def classify_regime(self):
        """
        Economic Regime from 2×2 growth × inflation matrix.
        Threshold = 25 pts (50% of max 50 pts).
        """
        growth_rising    = self.growth_score >= 25
        inflation_rising = self.inflation_score >= 25

        if growth_rising and not inflation_rising:
            self.regime = 'GOLDILOCKS'
        elif growth_rising and inflation_rising:
            self.regime = 'REFLATION'
        elif not growth_rising and inflation_rising:
            self.regime = 'STAGFLATION'
        else:
            self.regime = 'CONTRACTION'

        return self.regime

    def classify_phase(self):
        """
        Market Cycle Phase from cycle_score + growth direction + key signals.

        Decision logic:
          < 20:          RECESSION (systemic stress)
          < 40:          DOWNTURN  (contraction)
          Sahm ≥ 0.5     + cs < 40: RECESSION override
          ≥ 78:          MID       (broad expansion)
          58-78:         EARLY if growth↑ + spreads tightening, else MID or LATE
          40-58:         EARLY if growth↑, else LATE
        """
        cs           = self.cycle_score
        growth_rising = self.growth_score >= 25
        hy_tightening = (self.data.get('hy_spread_trend') or 0) < 0
        sahm          = self.data.get('sahm_value') if self.data.get('sahm_value') is not None else 0.0

        # Hard recession override
        if sahm >= 0.5 and cs < 40:
            self.phase = 'RECESSION'
            return 'RECESSION'

        if cs < 20:
            self.phase = 'RECESSION'
            return 'RECESSION'

        if cs < 40:
            self.phase = 'DOWNTURN'
            return 'DOWNTURN'

        if cs >= 78:
            self.phase = 'MID'
            return 'MID'

        if cs >= 58:
            if growth_rising and hy_tightening:
                self.phase = 'EARLY'
            elif not growth_rising:
                self.phase = 'LATE'
            else:
                self.phase = 'MID' if cs >= 68 else 'EARLY'
            return self.phase

        # 40–58 range
        self.phase = 'EARLY' if growth_rising else 'LATE'
        return self.phase

    # =========================================================================
    # REPORT
    # =========================================================================

    def _fmt(self, v, decimals=2, suffix=''):
        """Format a numeric value with optional suffix, or return N/A."""
        if v is None:
            return 'N/A'
        return f"{v:.{decimals}f}{suffix}"

    def _fmt_chg(self, v, decimals=1, suffix=''):
        """Format a change/trend value with explicit +/- sign, or return N/A."""
        if v is None:
            return 'N/A'
        return f"{v:+.{decimals}f}{suffix}"

    def generate_report(self):
        """Build the full Telegram report."""
        date_str   = self.timestamp.strftime('%Y-%m-%d %H:%M ET')
        pm = PHASE_META[self.phase]
        rm = REGIME_META[self.regime]
        gs = self.scores.get('growth', {})
        ins = self.scores.get('inflation', {})
        cs  = self.scores.get('cycle', {})

        L = []

        title = "MARKET CYCLE DETECTOR v1.0"
        width = max(len(title), len(date_str)) + 4
        L.append("╔" + "═" * width + "╗")
        L.append(f"║  {title.center(width - 4)}  ║")
        L.append(f"║  {date_str.center(width - 4)}  ║")
        L.append("╚" + "═" * width + "╝\n")

        L.append(f"PHASE:   {pm['icon']} {pm['label']}")
        L.append(f"REGIME:  {rm['icon']} {rm['label']}\n")

        # ── Layer 1: Economic Regime ──────────────────────────────────────────
        L.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append("LAYER 1 — ECONOMIC REGIME\n")

        g_dir = "Accelerating ↑" if self.growth_score >= 25 else "Decelerating ↓"
        L.append(f"Growth Score: {self.growth_score:.1f}/50  ({g_dir})")
        L.append(f"  • T10Y2Y yield curve:   {self._fmt(self.data.get('t10y2y'), 2, '%')} → {gs.get('t10y2y','N/A')}/10")
        L.append(f"  • T10Y3M yield curve:   {self._fmt(self.data.get('t10y3m'), 2, '%')} → {gs.get('t10y3m','N/A')}/10")
        L.append(f"  • IndPro (3M ann.):     {self._fmt_chg(self.data.get('indpro_annualized'), 1, '%')} → {gs.get('indpro','N/A')}/10")
        L.append(f"  • Claims 4W trend:      {self._fmt_chg(self.data.get('icsa_trend'), 1, '%')} → {gs.get('icsa','N/A')}/10")
        L.append(f"  • Sahm Rule:            {self._fmt(self.data.get('sahm_value'), 2)} (UNRATE {self._fmt(self.data.get('unrate_current'), 1, '%')}) → {gs.get('sahm','N/A')}/10")

        i_dir = "Rising ↑" if self.inflation_score >= 25 else "Falling ↓"
        L.append(f"\nInflation Score: {self.inflation_score:.1f}/50  ({i_dir})")
        L.append(f"  • CPI YoY:             {self._fmt(self.data.get('cpi_yoy'), 1, '%')} → {ins.get('cpi','N/A')}/15")
        L.append(f"  • 5Y Breakeven:        {self._fmt(self.data.get('t5yie'), 2, '%')} (3M chg {self._fmt_chg(self.data.get('t5yie_change_3m'), 2, 'pp')}) → {ins.get('breakeven','N/A')}/15")
        L.append(f"  • PPI 3M trend:        {self._fmt_chg(self.data.get('ppi_trend'), 1, '%')} → {ins.get('ppi','N/A')}/10")
        L.append(f"  • Real Rate (DFII10):  {self._fmt(self.data.get('dfii10'), 2, '%')} → {ins.get('real_rate','N/A')}/10")

        L.append(f"\nREGIME: {rm['icon']} {rm['label']}")
        L.append(f"→ {rm['description']}")
        L.append(f"→ Favoured: {rm['assets']}")

        # ── Layer 2: Market Cycle Phase ───────────────────────────────────────
        L.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append("LAYER 2 — MARKET CYCLE PHASE\n")
        L.append(f"Cycle Score: {self.cycle_score:.1f}/100 → {pm['icon']} {pm['label']}\n")

        L.append("Credit (0–30 pts):")
        L.append(f"  • HY Spread:  {self._fmt(self.data.get('hy_spread'), 0, 'bps')} ({self._fmt_chg(self.data.get('hy_spread_trend'), 0, 'bps 30d')}) → {cs.get('hy_spread','N/A')}/20")
        L.append(f"  • IG Spread:  {self._fmt(self.data.get('ig_spread'), 0, 'bps')} → {cs.get('ig_spread','N/A')}/10")

        L.append("\nMarket Structure (0–45 pts):")
        L.append(f"  • SPY vs 200DMA:       {self._fmt_chg(self.data.get('spy_vs_200dma_pct'), 1, '%')} → {cs.get('spy_200dma','N/A')}/15")
        L.append(f"  • RSP/SPY breadth 3M:  {self._fmt_chg(self.data.get('rsp_spy_ratio_trend'), 1, '%')} → {cs.get('breadth','N/A')}/10")
        L.append(f"  • XLY/XLP risk apt. 3M:{self._fmt_chg(self.data.get('xly_xlp_trend'), 1, '%')} → {cs.get('xly_xlp','N/A')}/10")
        L.append(f"  • XLF vs SPY 3M:       {self._fmt_chg(self.data.get('xlf_relative'), 1, 'pp')} → {cs.get('xlf_lead','N/A')}/10")

        L.append("\nMacro Pulse (0–25 pts):")
        L.append(f"  • Copper/Gold 3M:      {self._fmt_chg(self.data.get('copper_gold_trend'), 1, '%')} → {cs.get('copper_gold','N/A')}/10")
        L.append(f"  • NFCI:                {self._fmt(self.data.get('nfci'), 3)} → {cs.get('nfci','N/A')}/10")
        L.append(f"  • Curve trend (3M):    {self._fmt_chg(self.data.get('t10y2y_change_3m'), 2, 'pp')} → {cs.get('curve_trend','N/A')}/5")

        L.append(f"\nPHASE: {pm['icon']} {pm['label']}")
        L.append(f"→ {pm['description']}")
        L.append(f"→ Favoured: {pm['assets']}")

        # ── Sleeve Guidance ───────────────────────────────────────────────────
        L.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append(f"SLEEVE GUIDANCE — {pm['icon']} {self.phase} CYCLE\n")
        guidance = PHASE_SLEEVE_GUIDANCE[self.phase]
        sleeves = {
            'global_triads': 'Global Triads  (VWRA/82846/DHL/ES3/XMME)',
            'four_horsemen': 'Four Horsemen  (EQCH/CBUK/9807/INRA/GRDU)',
            'cash_cow':      'Cash Cow       (Wheel Strategy)',
            'alpha':         'Alpha          (Speculation)',
            'omega':         'Omega          (Insurance)',
            'vault':         'Vault          (GSD/AEM — Gold)',
            'war_chest':     'War Chest      (Cash)',
        }
        for key, name in sleeves.items():
            L.append(f"  {name}")
            L.append(f"  → {guidance[key]}\n")

        # ── Glossary ──────────────────────────────────────────────────────────
        L.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        L.append("GLOSSARY\n")
        L.append("Economic Regime (Growth × Inflation direction):")
        L.append("  🟢 GOLDILOCKS  — Growth↑, Inflation↓. Best equity environment.")
        L.append("  🟡 REFLATION   — Growth↑, Inflation↑. Commodities & cyclicals win.")
        L.append("  🔴 STAGFLATION — Growth↓, Inflation↑. Gold & cash. Avoid equities.")
        L.append("  🟠 CONTRACTION — Growth↓, Inflation↓. Bonds & defensives win.\n")
        L.append("Cycle Phase (market structure + credit + breadth):")
        L.append("  🌱 EARLY    — Credit tightening, breadth expanding, financials lead.")
        L.append("  📈 MID      — Broad expansion, credit stable, momentum strong.")
        L.append("  ⚡ LATE     — Breadth narrowing, inflation rising, spreads ticking wider.")
        L.append("  📉 DOWNTURN — Credit stress, SPY below 200DMA, breadth collapsed.")
        L.append("  ❄️ RECESSION — Sahm triggered, HY spreads blown out, max defense.")

        return "\n".join(L)

    # =========================================================================
    # MAIN RUN
    # =========================================================================

    def run(self):
        """Execute full daily cycle detection workflow."""
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    MARKET CYCLE DETECTOR v1.0                        ║
╚══════════════════════════════════════════════════════════════════════╝
        """)

        # 1. Fetch data
        self.fetch_all_data()

        # 2. Score all components
        print("📊 Scoring components...")
        self.score_growth()
        self.score_inflation()
        self.score_cycle()

        # 3. Classify
        self.classify_regime()
        self.classify_phase()

        print(f"\n🌐 Regime: {self.regime} — {REGIME_META[self.regime]['label']}")
        print(f"📈 Phase:  {self.phase}  — {PHASE_META[self.phase]['label']}")

        # 4. Persist to history (180-day rolling log)
        today = self.timestamp.strftime('%Y-%m-%d')
        snapshot = {
            'hy_spread':         self.data.get('hy_spread'),
            'ig_spread':         self.data.get('ig_spread'),
            'spy_vs_200dma_pct': self.data.get('spy_vs_200dma_pct'),
            't10y2y':            self.data.get('t10y2y'),
            'cpi_yoy':           self.data.get('cpi_yoy'),
            't5yie':             self.data.get('t5yie'),
            'sahm_value':        self.data.get('sahm_value'),
            'nfci':              self.data.get('nfci'),
        }
        self.history.add_entry(
            today, self.phase, self.regime,
            self.cycle_score, self.growth_score, self.inflation_score, snapshot
        )

        # 5. Generate + send report
        report = self.generate_report()
        print("\n" + report)

        self.history.save()
        send_to_telegram(report)

        print("\n✅ Cycle detection complete.\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    detector = CycleDetector()
    detector.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise
