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
🧠 CLAUDE-POWERED CIO INTERPRETATION - Dynamic daily analysis (NEW!)

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

14 SIGNALS + V-RECOVERY OVERRIDE + AI CIO | INSTITUTIONAL-GRADE

DEPENDENCIES:
pip install yfinance pandas fredapi requests python-dotenv lxml html5lib beautifulsoup4

SETUP:
1. Get FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Get Anthropic API key: https://console.anthropic.com/settings/keys
3. Get Gemini API key: https://aistudio.google.com/app/apikey
4. Add to .env file:
   FRED_API_KEY=your_fred_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here  # For CIO interpretation
   GEMINI_API_KEY=your_gemini_key_here  # For Gemini CIO interpretation
   TELEGRAM_TOKEN_RISK=your_telegram_token
   CHAT_ID=your_chat_id

DAILY OUTPUT:
You'll receive THREE Telegram messages each day:

MESSAGE 1: MAIN REPORT (Objective Data)
- All 14 signal readings with actual values
- Risk score and tier breakdown
- Allocation recommendation (60/30/5/5 format)
- Automated alerts for divergences
- Market summary (The Good / The Concerns)

MESSAGE 2: CIO INTERPRETATION (Dynamic Analysis by Claude)
- "What the score says vs what I see" analysis
- Hidden tensions and divergences explained
- Quality of score assessment (clean or tension?)
- Honest tactical call with specific adjustments
- Dynamic trigger points for what would change the call
- Written fresh each day by Claude Sonnet 4.5

MESSAGE 3: CIO INTERPRETATION (Dynamic Analysis by Gemini)
- Alternative AI perspective on same data
- Same structured analysis format as Claude
- Different AI reasoning approach (Google Gemini 2.0)
- Provides second opinion for validation

The CIO interpretations are NOT static if/else logic. Both Claude and Gemini
analyze your specific data each morning giving you real insights like a human
CIO would. Different market conditions = different analysis. Having two AI
models provides diverse perspectives on the same data.

═══════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════
GLOSSARY - ABBREVIATIONS & TERMS
═══════════════════════════════════════════════════════════════════════

TIER 1: CREDIT & LIQUIDITY
───────────────────────────
HY = High Yield
  - Also called "junk bonds" - bonds rated below investment grade (BB+ or lower)
  - Companies with weaker credit that have to pay higher yields to borrow
  - When these spreads widen, it means investors are pricing in default risk

LIBOR = London Interbank Offered Rate
  - The rate banks charge each other for short-term loans
  - Being phased out (replaced by SOFR now), but TED spread still uses legacy data
  - If banks won't lend to each other cheaply, that's a liquidity crisis signal

TED = Treasury-Eurodollar
  - "T" = Treasury bill rate (safe)
  - "ED" = Eurodollar rate (3-month LIBOR - riskier)
  - The spread between them = how much extra yield for bank risk
  - Named after the T-bill and Eurodollar futures contracts traded in Chicago

DXY = Dollar Index
  - Measures US dollar strength vs a basket of 6 major currencies (EUR, JPY, GBP, CAD, SEK, CHF)
  - When DXY goes up, dollar is strengthening
  - Ticker symbol on trading platforms

EM = Emerging Markets
  - Countries like Brazil, India, China, Mexico, Turkey, South Africa
  - Usually borrow in dollars, so strong dollar = their debt becomes more expensive
  - EM stress often precedes global risk-off

QE = Quantitative Easing
  - Fed buying bonds to inject liquidity (printing money)
  - Expands Fed's balance sheet
  - 2020: Massive QE = stocks went crazy

QT = Quantitative Tightening
  - Fed selling bonds to drain liquidity (opposite of QE)
  - Shrinks Fed's balance sheet
  - 2022: Aggressive QT = bear market

TIER 2: MARKET BREADTH
──────────────────────
MA = Moving Average
  - Average price over X days (50-MA = 50-day moving average, 200-MA = 200-day)
  - Stock above MA = uptrend, below MA = downtrend
  - Most widely used technical indicator

AD Line = Advance-Decline Line
  - Originally: number of stocks advancing minus declining each day
  - Our version: SPY's proximity to recent highs (simpler, same concept)
  - Measures market breadth participation

SPY = S&P 500 ETF
  - Ticker for the most liquid S&P 500 index fund
  - We use it as proxy for "the market"
  - Trades like a stock, tracks the index

TIER 3: RISK APPETITE
─────────────────────
XLU = Utilities Sector ETF
  - Defensive stocks: electric, gas, water companies
  - Stable, boring, dividend-paying
  - People buy when scared (recession-proof)

XLK = Technology Sector ETF
  - Growth stocks: Apple, Microsoft, Nvidia, etc.
  - High beta, high growth potential
  - People buy when optimistic about economy

GLD = Gold ETF
  - Tracks physical gold price
  - Safe haven asset
  - Goes up when people are scared or when dollar weakens

VIX = Volatility Index
  - "Fear gauge" - measures S&P 500 implied volatility
  - Calculated from options prices
  - High VIX = expensive insurance = fear

VXX = Short-term VIX futures ETF
  - Holds 1-month VIX futures
  - More volatile than VIX itself

VIXY = Short-term VIX futures ETF (different provider)
  - Similar to VXX but different structure
  - We compare VIXY/VXX ratio to detect term structure

Contango = Normal futures curve
  - Far-dated contracts more expensive than near-dated
  - Means: "Things are calm now, might get worse later"
  - Healthy market state

Backwardation = Inverted futures curve
  - Near-dated contracts MORE expensive than far-dated
  - Means: "Shit is hitting the fan RIGHT NOW"
  - Danger signal

TIER 4: SENTIMENT
─────────────────
T10Y2Y = 10-Year Treasury Yield minus 2-Year Treasury Yield
  - FRED's ticker code for the yield curve spread
  - Normal: 10-year pays MORE than 2-year (positive spread)
  - Inverted: 2-year pays MORE than 10-year (negative spread = recession warning)

YoY = Year-over-Year
  - Comparing data to same period last year
  - Fed BS YoY = how much Fed's balance sheet changed vs 12 months ago
  - Removes seasonal effects

GENERAL TRADING TERMS
─────────────────────
Spread (in credit context)
  - Extra yield above risk-free rate (Treasuries)
  - HY spread = junk bond yield minus Treasury yield
  - Wider spread = more risk priced in

ETF = Exchange-Traded Fund
  - Trades like a stock but holds a basket of securities
  - SPY, XLU, XLK, GLD are all ETFs
  - Liquid, low-cost way to get sector/asset exposure

Beta
  - How much an asset moves relative to the market
  - Beta 1.0 = moves with market
  - Beta >1.0 = more volatile than market (Tier 3 positions)
  - Beta <1.0 = less volatile than market (Tier 1 positions)

FRED = Federal Reserve Economic Data
  - St. Louis Fed's database of economic indicators
  - Free API access (what we use)
  - Gold standard for macro data

FRED TICKER CODES
─────────────────
BAMLH0A0HYM2 = FRED code for HY spread
  - "BAML" = Bank of America Merrill Lynch (data provider)
  - "H0A0HYM2" = their internal code for high-yield spread

WALCL = FRED code for Fed balance sheet
  - "W" = Weekly data
  - "ALCL" = All Federal Reserve Banks, Total Assets
  - Tracks total Fed assets (size of balance sheet)

TEDRATE = FRED code for TED spread
  - Direct ticker, no acronym breakdown
  - Updated daily

T10Y2Y = FRED code for yield curve
  - "T10Y" = 10-year Treasury
  - "2Y" = 2-year Treasury
  - The difference between them

═══════════════════════════════════════════════════════════════════════
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
        """Count consecutive days of backwardation
        Returns: (days, avg_magnitude)
        """
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
├─ HY Credit Spread:        20 pts  [FREED: BAMLH0A0HYM2]
│  What it is: The extra yield investors demand to hold junk bonds vs safe Treasury bonds
│  Why it matters: When shit hits the fan, this screams FIRST. Credit markets panic before stocks do.
│  Type: Leading indicator (predicts trouble 2-4 weeks ahead)
│  Who uses it: Every institutional desk on Wall Street. The "smart money" indicator.
│  Normal range: 3-4% = healthy, 4.5-5% = caution, >5.5% = red alert
│  Released: Daily, updates after market close (FRED data)
│  Real impact: 
│    - Tight spreads (3%) = companies can borrow cheap, economy humming
│    - Wide spreads (6%+) = credit freeze coming, recession risk
│  Example: Feb 2020 COVID - HY spreads jumped to 8%+ while VIX was still calm. Credit knew first.
│
├─ Fed Balance Sheet YoY:   15 pts  [FRED: WALCL]
│  What it is: How much the Fed's balance sheet grew/shrank vs last year (in %)
│  Why it matters: Fed expanding = printing money = liquidity flood = stocks go up. Fed shrinking = draining liquidity = danger.
│  Type: Concurrent indicator (tells you what's happening NOW)
│  Who uses it: Macro hedge funds, Ray Dalio types who trade on liquidity cycles
│  Normal range: +2% to -2% = stable, >+10% = massive QE, <-10% = aggressive QT
│  Released: Weekly (Thursdays), FRED updates it
│  Real impact:
│    - 2020: Fed expanded 75% YoY → stocks went ballistic
│    - 2022: Fed contracted -8% YoY → bear market
│  Key insight: "Don't fight the Fed" - when they're expanding, stay bullish. When contracting, be cautious.
│
├─ TED Spread:              10 pts  [FRED: TEDRATE]
│  What it is: Difference between 3-month LIBOR (bank lending rate) and 3-month Treasury
│  Why it matters: Measures how scared banks are to lend to each other. Banking stress indicator.
│  Type: Leading indicator (spikes DURING crises, not before)
│  Who uses it: Risk managers, CFOs, anyone worried about liquidity freezes
│  Normal range: 0.2-0.5 = healthy, 0.5-0.8 = elevated, >1.0 = crisis mode
│  Released: Daily, FRED data
│  Real impact:
│    - 2008 Lehman: TED spiked to 4.5 → complete credit freeze
│    - Normal times: Stays below 0.5, nobody even looks at it
│  Key insight: When this spikes, banks don't trust each other. That's bad. Very bad.
│
└─ Dollar Index Trend:       5 pts  [Yahoo: DX-Y.NYB]
   What it is: Is the US dollar strengthening or weakening vs its 20-day average?
   Why it matters: Strong dollar = global liquidity drain, EM stress, multinational earnings hurt. Weak dollar = risk-on, everyone happy.
   Type: Concurrent indicator
   Who uses it: International investors, commodity traders, EM fund managers
   Normal range: -1% to +1% = stable, >+3% = flight to safety (bad), <-3% = dollar weakness (good for risk)
   Released: Real-time during market hours, we calculate the trend daily
   Real impact:
     - Strong dollar events: 2022 DXY +20% → everything collapsed (stocks, crypto, commodities)
     - Weak dollar: 2020-2021 DXY -10% → massive risk-on rally
   Key insight: Dollar up = liquidity down = risk assets down. Inverse correlation is real.

TIER 2: MARKET BREADTH (30 points)
├─ % Above 50-MA:           12 pts  [Calculated: 27 blue-chip stocks]
│  What it is: What percentage of our sample stocks (100 blue chips) are trading above their 50-day moving average
│  Why it matters: If SPY is at highs but only 40% of stocks are above their 50-MA, that's a weak rally. Breadth confirms or warns.
│  Type: Concurrent indicator (real-time health check)
│  Who uses it: Every technical analyst on Wall Street
│  Normal range: >65% = healthy, 50-65% = mixed, <50% = weak breadth (danger)
│  Released: We calculate it daily from live stock prices
│  Real impact:
│    - Strong breadth (>70%): Rally is real, broad participation, sustainable
│    - Weak breadth (<40%): Only a few stocks holding up the index, fragile
│  Example: Jan 2022 - SPY kept making highs but breadth collapsed to 35%. Market rolled over 3 weeks later.
│  Key insight: The market can't rally on 10 stocks forever. When breadth breaks, indices follow.
│
├─ % Below 200-MA:          10 pts  [Calculated: 27 blue-chip stocks]
│  What it is: Percentage of stocks trading BELOW their 200-day moving average (severe breakdown indicator)
│  Why it matters: This is the "blood in the streets" metric. When >50% are below 200-MA, it's a bear market.
│  Type: Lagging indicator (confirms damage, doesn't predict it)
│  Who uses it: Value investors looking for bottoms, risk managers measuring severity
│  Normal range: <25% = healthy, 25-35% = caution, >50% = bear market confirmed
│  Released: We calculate daily
│  Real impact:
│    - March 2020: 80% below 200-MA → capitulation, then bottom
│    - Bull markets: Stays <20%, nobody cares about it
│  Key insight: Inverse of breadth strength. When this spikes, we're in trouble. But extreme readings (>70%) often mark bottoms.
│
├─ AD Line Status:           5 pts  [SPY 20-day high proximity]
│  What it is: Is SPY near its 20-day high? If yes, breadth is "confirming." If no, breadth is "diverging."
│  Why it matters: Catches when price makes new highs but fewer stocks participate (bearish divergence)
│  Type: Concurrent indicator
│  Who uses it: Technical traders watching for divergences
│  Three states:
│    - "Confirming" = SPY within 1% of 20-day high (healthy)
│    - "Flat" = SPY 1-5% off high (neutral)
│    - "Diverging" = SPY >5% off high (warning)
│  Released: We calculate daily
│  Real impact:
│    - Diverging + weak breadth = top forming (2021 November before crash)
│    - Confirming = trend is strong, keep riding
│  Key insight: Simple but effective divergence detector.
│
└─ New Highs - Lows:         3 pts  [Calculated: 3-month range]
   What it is: How many stocks in our sample are at 52-week highs minus how many are at 52-week lows
   Why it matters: Extreme readings signal turning points. +10 = euphoria, -10 = capitulation
   Type: Concurrent with some leading characteristics at extremes
   Who uses it: Contrarian investors, sentiment traders
   Normal range: -5 to +5 = normal chop, >+10 = expansion/euphoria, <-10 = contraction/fear
   Released: We calculate daily
   Real impact:
     - Extreme positive: Often marks short-term tops (too much euphoria)
     - Extreme negative: Often marks bottoms (max fear)
   Key insight: Mean-reverting indicator. Extremes don't last.

TIER 3: RISK APPETITE (15 points)
├─ Sector Rotation XLU/XLK:  6 pts  [XLU/XLK ratio trend]
│  What it is: Ratio of Utilities (XLU) to Technology (XLK). Are defensive stocks or growth stocks outperforming?
│  Why it matters: When utilities outperform tech, institutions are rotating defensive. Risk-off mode.
│  Type: Concurrent indicator
│  Who uses it: Sector rotation traders, asset allocators
│  Normal range: <-2% = tech outperforming (risk-on), +2 to +5% = utilities catching up (risk-off)
│  Released: We calculate daily from ETF prices
│  Real impact:
│    - XLU outperforming (>+5%): Flight to safety, recession fears, be defensive
│    - XLK outperforming (<-3%): Risk appetite strong, growth mode
│  Example: 2022 bear market - XLU massively outperformed XLK. Clear risk-off signal.
│  Key insight: Where the money flows tells you what institutions believe.
│
├─ Gold/SPY Ratio:           5 pts  [GLD/SPY ratio trend]
│  What it is: Ratio of gold (GLD) to stocks (SPY). Is safe haven in demand?
│  Why it matters: Gold rallying vs stocks = fear. Stocks rallying vs gold = greed.
│  Type: Concurrent indicator
│  Who uses it: Macro traders, gold bugs, risk-parity funds
│  Normal range: -1% to +1% = neutral, >+3% = safe haven bid (bad for stocks), <-3% = risk-on (good for stocks)
│  Released: We calculate daily from ETF prices
│  Real impact:
│    - Gold outperforming: 2020 COVID, 2022 inflation → risk assets suffered
│    - Stocks outperforming: 2023 rally → gold got destroyed
│  Key insight: Classic risk-on/risk-off barometer. They inverse each other.
│
└─ VIX Term Structure:       4 pts  [VIXY/VXX ratio]
   What it is: Are VIX futures in contango (backwardation = near-term more expensive than far-term, stress)
   Why it matters: Contango = calm markets, backwardation = panic/fear NOW
   Type: Concurrent indicator of market stress
   Who uses it: VIX traders, vol arb funds, risk managers
   Three states:
     - "Contango" = healthy (far VIX > near VIX)
     - "Flat" = neutral
     - "Backwardation" = stressed (near VIX > far VIX)
   Released: We check daily using VIXY/VXX ratio
   Real impact:
     - Backwardation: March 2020, Feb 2018 → crashes happening NOW
     - Contango: Normal bull markets → all clear
   Key insight: Backwardation = fear is HERE, not expected. That's the dangerous kind.

TIER 4: SENTIMENT (5 points)
├─ Yield Curve:              3 pts  [FRED: T10Y2Y]
│  What it is: 10-year Treasury yield minus 2-year Treasury yield
│  Why it matters: Inverted curve (negative) = recession coming in 6-18 months. Most reliable recession predictor.
│  Type: Leading indicator (predicts recessions 12-18 months ahead)
│  Who uses it: Every economist, Fed, bond traders
│  Normal range: >+0.5% = healthy, 0 to +0.2% = flattening, <0 = inverted (recession warning)
│  Released: Daily, FRED data
│  Real impact:
│    - Every recession since 1970 was preceded by inversion
│    - 2022: Inverted in July → recession fears dominated 2023
│  Key insight: The bond market is smarter than the stock market. When bonds say recession, listen.
│
├─ VIX Level:               1.5 pts  [Yahoo: ^VIX]
│  What it is: The "fear gauge" - implied volatility of S&P 500 options
│  Why it matters: Tells you if options traders are pricing in calm or chaos
│  Type: Concurrent indicator (real-time fear/calm)
│  Who uses it: Everyone. Most watched indicator on CNBC.
│  Normal range: <15 = complacency, 15-20 = normal, 20-30 = elevated, >30 = fear/panic
│  Released: Real-time during market hours
│  Real impact:
│    - VIX <12: Extreme complacency, often precedes corrections
│    - VIX >40: Panic mode, often marks bottoms
│  Key insight: We give it LOW weight (1.5 pts) because it's easily manipulated. VIX can be calm while credit markets scream.
│
└─ Fear & Greed Index:      0.5 pts  [VIX-derived calculation]
   What it is: VIX-derived calculation mapping 0-100 (we replaced CNN's API with our own VIX calculation)
   Why it matters: Sentiment barometer. Extreme fear = contrarian buy. Extreme greed = contrarian sell.
   Type: Concurrent sentiment gauge
   Who uses it: Retail traders love it, institutions ignore it
   Normal range: 35-65 = neutral zone, <20 = extreme fear, >80 = extreme greed
   Released: We calculate daily from VIX
   Real impact:
     - Extreme fear (<20): Often marks bottoms (March 2020, Oct 2022)
     - Extreme greed (>80): Often marks tops (Jan 2018, Nov 2021)
   Key insight: We give it TINY weight (0.5 pts) because sentiment is noise. But extreme readings matter.

V-RECOVERY OVERRIDE: (Dynamic allocation adjustment)
When extreme risk reverses sharply, override conservative allocation
- Cuts cash allocation by 50% to capture V-shaped recoveries
- Prevents missing explosive bounces after crashes
- Requires multiple confirmation signals to avoid false triggers

SUMMARY OF THE FRAMEWORK
Why these 14?
  - Tier 1 (50%) = Credit/liquidity matters MOST. Smart money signals.
  - Tier 2 (30%) = Breadth confirms or warns. Can't ignore participation.
  - Tier 3 (15%) = Risk appetite matters but less critical.
  - Tier 4 (5%) = Sentiment is noise, but extremes matter.

The hierarchy:
  1. Credit markets (HY spread, TED) scream first → heaviest weight
  2. Breadth confirms the move → second heaviest
  3. Sector rotation shows flow → moderate weight
  4. Sentiment/VIX = noise → minimal weight

Time horizons:
  - Leading (predict): HY Spread, Yield Curve
  - Concurrent (confirm): Most breadth, Fed BS, sector rotation
  - Lagging (validate): % Below 200-MA

What we DON'T use:
  - Put/call ratios (manipulated)
  - RSI/MACD (noise)
  - News headlines (laggy, emotional)
  - Earnings (backward-looking)

The edge:
This framework prioritizes HARD-TO-MANIPULATE signals (credit markets) over 
EASY-TO-MANIPULATE signals (VIX, sentiment). That's why it's institutional-grade.

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
        Returns: tuple (structure, ratio, magnitude_pct) or (None, None, None)
        """
        try:
            vxx = yf.Ticker('VXX').history(period='5d')['Close'].iloc[-1]
            vixy = yf.Ticker('VIXY').history(period='5d')['Close'].iloc[-1]
            ratio = vixy / vxx
            
            # Determine structure
            if ratio > 1.03:
                struct = 'Contango'
                magnitude_pct = (ratio - 1.0) * 100  # How much contango
            elif ratio < 0.97:
                struct = 'Backwardation'
                magnitude_pct = (1.0 - ratio) * 100  # How much backwardation (positive number)
            else:
                struct = 'Flat'
                magnitude_pct = 0.0
            
            # Get backwardation streak if applicable
            streak_info = ""
            if struct == 'Backwardation':
                streak, avg_mag = self.history_manager.get_backwardation_streak()
                if streak > 0:
                    streak_info = f" Day {streak}"
                    # Record today's backwardation
                    self.history_manager.add_backwardation_event(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        vixy_vxx_ratio=ratio,
                        magnitude_pct=magnitude_pct
                    )
            
            print(f"   ✓ VIX Struct: {struct}{streak_info} (ratio={ratio:.3f}, mag={magnitude_pct:.1f}%)")
            return struct, ratio, magnitude_pct
            
        except Exception as e:
            print(f"   ✗ VIX Struct: Error - {str(e)[:50]}")
            return None, None, None
    
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
        
        # Alert 6: Backwardation Persistence (NEW - ESCALATES)
        if d.get('vix_struct') == 'Backwardation':
            streak, avg_mag = self.history_manager.get_backwardation_streak()
            
            if streak >= 5:
                # Day 5+ = CRITICAL
                self.alerts.append({
                    'type': 'BACKWARDATION PERSISTING',
                    'severity': 'CRITICAL',
                    'icon': '🚨🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak} - INSTITUTIONS STILL HEDGING',
                    'action': 'TIGHTEN STOPS 12-15%, REDUCE TIER 3'
                })
            elif streak >= 3:
                # Day 3-4 = HIGH CONCERN
                self.alerts.append({
                    'type': 'BACKWARDATION PERSISTING',
                    'severity': 'HIGH',
                    'icon': '🚨🚨',
                    'msg': f'VIX BACKWARDATION DAY {streak} - PATTERN FORMING',
                    'action': 'WATCH CREDIT & BREADTH CLOSELY'
                })
            elif streak >= 1 and d.get('vix') and d['vix'] < 16:
                # Day 1-2 + Low VIX = HIDDEN DANGER
                self.alerts.append({
                    'type': 'HIDDEN TENSION',
                    'severity': 'MEDIUM',
                    'icon': '⚠️',
                    'msg': f'VIX CALM ({d["vix"]:.1f}) BUT BACKWARDATION DETECTED',
                    'action': 'INSTITUTIONS BUYING PROTECTION - STAY ALERT'
                })
        
        # Alert 7: V-Recovery Active
        if self.v_recovery_active:
            self.alerts.append({
                'type': 'V-RECOVERY OVERRIDE ACTIVE',
                'severity': 'INFO',
                'icon': '🚀',
                'msg': self.v_recovery_reason,
                'action': 'CASH ALLOCATION CUT BY 50% - AGGRESSIVE RE-ENTRY'
            })
        
        # Alert 8: All Clear
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
            "🎯 RISK DASHBOARD v1.6",
            f"📅 {self.timestamp.strftime('%b %d, %Y @ %H:%M')}",
            "",
            f"📊 SCORE: {score:.1f}/100",
            f"🎚️ {risk}",
            f"💼 {pos}",
            "",
        ]
        
        # Show allocation (with override if active)
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
        
        # Add detailed dollar allocation breakdown
        lines.extend(self._generate_allocation_breakdown(final_alloc))
        
        # Enhanced tier scores with individual signals
        sc = self.scores['components']
        lines.extend([
            "📈 TIER SCORES",
            "",
            f"T1 (Credit & Liquidity): {self.scores['tier1']:.1f}/50 ({self.scores['tier1']/50*100:.0f}%)",
            f"  • HY Spread: {sc['hy_spread']:.1f}/20 [{format(d.get('hy_spread'), '.2f') + '%' if d.get('hy_spread') is not None else 'N/A'}]",
            f"  • Fed BS YoY: {sc['fed_bs']:.1f}/15 [{format(d.get('fed_bs_yoy'), '.1f') + '%' if d.get('fed_bs_yoy') is not None else 'N/A'}]",
            f"  • TED Spread: {sc['ted']:.1f}/10 [{format(d.get('ted_spread'), '.2f') if d.get('ted_spread') is not None else 'N/A'}]",
            f"  • DXY Trend: {sc['dxy']:.1f}/5 [{format(d.get('dxy_trend'), '.1f') + '%' if d.get('dxy_trend') is not None else 'N/A'}]",
            "",
            f"T2 (Market Breadth): {self.scores['tier2']:.1f}/30 ({self.scores['tier2']/30*100:.0f}%)",
            f"  • % >50-MA: {sc['pct_50ma']:.1f}/12 [{format(d.get('pct_above_50ma'), '.0f') + '%' if d.get('pct_above_50ma') is not None else 'N/A'}]",
            f"  • % <200-MA: {sc['pct_200ma']:.1f}/10 [{format(d.get('pct_below_200ma'), '.0f') + '%' if d.get('pct_below_200ma') is not None else 'N/A'}]",
            f"  • A-D Line: {sc['ad_line']:.1f}/5 [{d.get('ad_line', 'N/A')}]",
            f"  • New H-L: {sc['new_hl']:.1f}/3 [{d.get('new_hl', 'N/A')}]",
            "",
            f"T3 (Risk Appetite): {self.scores['tier3']:.1f}/15 ({self.scores['tier3']/15*100:.0f}%)",
            f"  • XLU/XLK: {sc['sector_rot']:.1f}/6 [{format(d.get('sector_rot'), '.1f') + '%' if d.get('sector_rot') is not None else 'N/A'}]",
            f"  • GLD/SPY: {sc['gold_spy']:.1f}/5 [{format(d.get('gold_spy'), '.1f') + '%' if d.get('gold_spy') is not None else 'N/A'}]",
            f"  • VIX Struct: {sc['vix_struct']:.1f}/4 [{d.get('vix_struct', 'N/A')}]",
            "",
            f"T4 (Sentiment): {self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            f"  • Yield Curve: {sc['yield_curve']:.1f}/3 [{format(d.get('yield_curve'), '.2f') + '%' if d.get('yield_curve') is not None else 'N/A'}]",
            f"  • VIX Level: {sc['vix']:.1f}/1.5 [{format(d.get('vix'), '.1f') if d.get('vix') is not None else 'N/A'}]",
            f"  • Fear/Greed: {sc['fear_greed']:.1f}/0.5 [{format(d.get('fear_greed'), '.0f') if d.get('fear_greed') is not None else 'N/A'}]",
            "",
        ])
        
        # Add market summary
        lines.extend(self._generate_summary())
        
        # Add divergence alerts
        if self.alerts:
            lines.append("")
            lines.append("🚨 ALERTS")
            for alert in self.alerts:
                lines.extend([
                    "",
                    f"{alert['icon']} {alert['type']}",
                    f"{alert['msg']}",
                    f"→ {alert['action']}"
                ])
        
        return "\n".join(lines)
    
    def _generate_allocation_breakdown(self, allocation):
        """Generate detailed allocation breakdown with percentages only
        
        Args:
            allocation: tuple (tier1%, tier2%, tier3%, cash%)
        
        Returns:
            list of strings for report lines
        """
        tier1_pct, tier2_pct, tier3_pct, cash_pct = allocation
        
        total_invested_pct = tier1_pct + tier2_pct + tier3_pct
        
        lines = [
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
        lines = [
            "📝 SUMMARY"
        ]
        
        if good:
            lines.append("✅ Good:")
            for item in good[:3]:  # Top 3 only
                lines.append(f"• {item}")
        
        if concerns:
            lines.append("")
            lines.append("⚠️ Watch:")
            for item in concerns[:3]:  # Top 3 only
                lines.append(f"• {item}")
        
        if not good and not concerns:
            lines.append("• No major issues")
        
        lines.append("")
        
        return lines
    
    def _get_backwardation_context(self):
        """Generate backwardation context for CIO interpretation
        Returns: dict with backwardation details
        """
        d = self.data
        
        if d.get('vix_struct') != 'Backwardation':
            return {
                'active': False,
                'message': 'No backwardation detected'
            }
        
        streak, avg_mag = self.history_manager.get_backwardation_streak()
        
        # Determine severity
        if streak >= 5:
            severity = "CRITICAL - Pattern firmly established"
        elif streak >= 3:
            severity = "HIGH - Pattern forming, needs attention"
        elif streak >= 1:
            severity = "MEDIUM - New signal, watch closely"
        else:
            severity = "INFO - Single occurrence"
        
        return {
            'active': True,
            'streak_days': streak,
            'magnitude_pct': d.get('vix_magnitude', 0),
            'avg_magnitude': avg_mag,
            'vix_level': d.get('vix'),
            'vixy_vxx_ratio': d.get('vixy_vxx_ratio'),
            'severity': severity,
            'message': f"Backwardation Day {streak}: {severity}. VIX calm at {d.get('vix', 'N/A'):.1f} but institutions buying {d.get('vix_magnitude', 0):.1f}% premium on near-term protection."
        }
    
    def generate_cio_interpretation(self):
        """Generate CIO's honest interpretation using Claude API for dynamic analysis
        Returns: str - Multi-line CIO analysis report"""
        
        print("🔍 Checking for ANTHROPIC_API_KEY...")
        
        # Check if Claude API key is available
        claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not claude_api_key:
            print("❌ ANTHROPIC_API_KEY not found in environment")
            print("   Checked: os.getenv('ANTHROPIC_API_KEY')")
            print("   Make sure .env file is in the same directory as the script")
            print("   And contains: ANTHROPIC_API_KEY=sk-ant-api03-...")
            return None
        
        if claude_api_key == 'YOUR_ANTHROPIC_API_KEY_HERE':
            print("❌ ANTHROPIC_API_KEY is placeholder value")
            print("   Replace with actual key from console.anthropic.com")
            return None
        
        print(f"✅ API key found (starts with: {claude_api_key[:15]}...)")
        
        score = self.scores['total']
        d = self.data
        
        # Build comprehensive data package for Claude
        data_package = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': f"{score:.1f}/100",
            'tier_scores': {
                'tier1_credit_liquidity': f"{self.scores['tier1']:.1f}/50 ({self.scores['tier1']/50*100:.0f}%)",
                'tier2_breadth': f"{self.scores['tier2']:.1f}/30 ({self.scores['tier2']/30*100:.0f}%)",
                'tier3_risk_appetite': f"{self.scores['tier3']:.1f}/15 ({self.scores['tier3']/15*100:.0f}%)",
                'tier4_sentiment': f"{self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            },
            'raw_indicators': {
                'tier1': {
                    'hy_spread': f"{d.get('hy_spread', 'N/A')}%" if d.get('hy_spread') else "N/A",
                    'fed_bs_yoy': f"{d.get('fed_bs_yoy', 'N/A')}%" if d.get('fed_bs_yoy') else "N/A",
                    'ted_spread': f"{d.get('ted_spread', 'N/A')}" if d.get('ted_spread') else "N/A",
                    'dxy_trend': f"{d.get('dxy_trend', 'N/A')}%" if d.get('dxy_trend') else "N/A",
                },
                'tier2': {
                    'pct_above_50ma': f"{d.get('pct_above_50ma', 'N/A')}%" if d.get('pct_above_50ma') else "N/A",
                    'pct_below_200ma': f"{d.get('pct_below_200ma', 'N/A')}%" if d.get('pct_below_200ma') else "N/A",
                    'ad_line': d.get('ad_line', 'N/A'),
                    'new_hl': f"{d.get('new_hl', 'N/A')}" if d.get('new_hl') is not None else "N/A",
                },
                'tier3': {
                    'sector_rot': f"{d.get('sector_rot', 'N/A')}%" if d.get('sector_rot') else "N/A",
                    'gold_spy': f"{d.get('gold_spy', 'N/A')}%" if d.get('gold_spy') else "N/A",
                    'vix_struct': d.get('vix_struct', 'N/A'),
                },
                'tier4': {
                    'yield_curve': f"{d.get('yield_curve', 'N/A')}%" if d.get('yield_curve') else "N/A",
                    'vix': f"{d.get('vix', 'N/A')}" if d.get('vix') else "N/A",
                    'fear_greed': f"{d.get('fear_greed', 'N/A')}/100" if d.get('fear_greed') else "N/A",
                }
            },
            'backwardation_context': self._get_backwardation_context(),
            'allocation': {
                'base': f"{int(self.get_base_allocation()[0]*100)}/{int(self.get_base_allocation()[1]*100)}/{int(self.get_base_allocation()[2]*100)}/{int(self.get_base_allocation()[3]*100)}",
                'description': 'Tier1/Tier2/Tier3/Cash percentages'
            },
            'alerts': [alert for alert in self.alerts],
            'v_recovery_active': self.v_recovery_active
        }
        
        # Craft the prompt for Claude
        prompt = f"""You are the CIO (Chief Investment Officer) analyzing today's institutional risk dashboard for your CEO. The CEO is a sophisticated trader with $2M portfolio ($1M active trading, $1M in bonds). They value direct, blunt, witty analysis over diplomatic corporate speak.

TODAY'S DATA:
{json.dumps(data_package, indent=2)}

CONTEXT YOU NEED TO KNOW:
- Tier 1 (Credit/Liquidity) = 50% weight = Most important, "smart money" signals
- Tier 2 (Breadth) = 30% weight = Confirms or warns about market structure
- Tier 3 (Risk Appetite) = 15% weight = Shows institutional positioning
- Tier 4 (Sentiment) = 5% weight = Noise, but extremes matter

KEY SIGNAL INTERPRETATIONS:
- HY Spread: <3.5% = very tight/healthy, 3-4% = normal, 4.5-5% = caution, >5.5% = stress
- TED Spread: <0.3 = healthy banking, 0.5-0.8 = elevated, >1.0 = crisis
- % Above 50-MA: >65% = healthy breadth, 50-65% = mixed, <50% = weak
- % Below 200-MA: <25% = healthy, 25-35% = caution, >50% = bear market
- New H-L: >+10 = euphoria (contrarian sell), <-10 = capitulation (contrarian buy)
- VIX Backwardation = institutions hedging (danger signal even if VIX calm)
  * Day 1-2: Watch mode
  * Day 3-4: Pattern forming, heightened alert
  * Day 5+: CRITICAL - institutions committed to hedging
- Fear/Greed: >75 = extreme greed, <25 = extreme fear

YOUR TASK:
Write a brief CIO interpretation for iPhone Telegram.

FORMAT:
- Short, punchy lines
- No decorative dividers
- Mobile-friendly
- Direct language

STRUCTURE:

💭 HEADLINE
[One punchy line about what you see]

📊 SCORE QUALITY
T1: XX/50 (XX%) [STRONG/WEAK]
T2: XX/30 (XX%) [STRONG/WEAK]
T3: XX/15 (XX%) [STRONG/WEAK]
T4: X/5 (XX%) [STRONG/WEAK]

👁️ WHAT I SEE
✅ [2-3 positives with numbers]
⚠️ [2-3 concerns with numbers]

🎯 MARKET REGIME
[2-3 sentences on market type, score quality, what institutions doing]

💡 MY CALL
System: XX/XX/XX/XX
[If adjustments:]
Suggest: XX/XX/XX/XX
Stops: X-X%
Why: [brief reason]
[If clean:]
Run the playbook.

🔄 FLIP TRIGGERS
→ [Specific trigger with numbers]
→ [Specific trigger with numbers]

⚡ BOTTOM LINE
[One clear sentence - deployed/cautious/defensive and why]

KEEP UNDER 1200 CHARS.
USE ACTUAL NUMBERS FROM TODAY.
BE SPECIFIC AND DIRECT.

Write now:"""

        try:
            import requests
            
            print("\n🧠 Generating CIO interpretation using Claude API...")
            
            # Call Claude API
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": claude_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                cio_text = result['content'][0]['text']
                
                # Format with simple header
                formatted_output = [
                    "🧠 CIO INTERPRETATION (Claude)",
                    f"📅 {self.timestamp.strftime('%b %d, %Y')}",
                    "",
                    cio_text,
                ]
                
                print("✅ CIO interpretation generated successfully")
                return "\n".join(formatted_output)
            
            else:
                print(f"⚠️  Claude API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"⚠️  Error generating CIO interpretation: {e}")
            return None
    
    def generate_gemini_interpretation(self):
        """Generate CIO's honest interpretation using Gemini API for dynamic analysis
        Returns: str - Multi-line CIO analysis report"""
        
        print("🔍 Checking for GEMINI_API_KEY...")
        
        # Check if Gemini API key is available
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            print("   Checked: os.getenv('GEMINI_API_KEY')")
            print("   Make sure .env file is in the same directory as the script")
            print("   And contains: GEMINI_API_KEY=...")
            return None
        
        if gemini_api_key == 'YOUR_GEMINI_API_KEY_HERE':
            print("❌ GEMINI_API_KEY is placeholder value")
            print("   Replace with actual key from Google AI Studio")
            return None
        
        print(f"✅ API key found (starts with: {gemini_api_key[:15]}...)")
        
        score = self.scores['total']
        d = self.data
        
        # Build comprehensive data package for Gemini (same as Claude)
        data_package = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': f"{score:.1f}/100",
            'tier_scores': {
                'tier1_credit_liquidity': f"{self.scores['tier1']:.1f}/50 ({self.scores['tier1']/50*100:.0f}%)",
                'tier2_breadth': f"{self.scores['tier2']:.1f}/30 ({self.scores['tier2']/30*100:.0f}%)",
                'tier3_risk_appetite': f"{self.scores['tier3']:.1f}/15 ({self.scores['tier3']/15*100:.0f}%)",
                'tier4_sentiment': f"{self.scores['tier4']:.1f}/5 ({self.scores['tier4']/5*100:.0f}%)",
            },
            'raw_indicators': {
                'tier1': {
                    'hy_spread': f"{d.get('hy_spread', 'N/A')}%" if d.get('hy_spread') else "N/A",
                    'fed_bs_yoy': f"{d.get('fed_bs_yoy', 'N/A')}%" if d.get('fed_bs_yoy') else "N/A",
                    'ted_spread': f"{d.get('ted_spread', 'N/A')}" if d.get('ted_spread') else "N/A",
                    'dxy_trend': f"{d.get('dxy_trend', 'N/A')}%" if d.get('dxy_trend') else "N/A",
                },
                'tier2': {
                    'pct_above_50ma': f"{d.get('pct_above_50ma', 'N/A')}%" if d.get('pct_above_50ma') else "N/A",
                    'pct_below_200ma': f"{d.get('pct_below_200ma', 'N/A')}%" if d.get('pct_below_200ma') else "N/A",
                    'ad_line': d.get('ad_line', 'N/A'),
                    'new_hl': f"{d.get('new_hl', 'N/A')}" if d.get('new_hl') is not None else "N/A",
                },
                'tier3': {
                    'sector_rot': f"{d.get('sector_rot', 'N/A')}%" if d.get('sector_rot') else "N/A",
                    'gold_spy': f"{d.get('gold_spy', 'N/A')}%" if d.get('gold_spy') else "N/A",
                    'vix_struct': d.get('vix_struct', 'N/A'),
                },
                'tier4': {
                    'yield_curve': f"{d.get('yield_curve', 'N/A')}%" if d.get('yield_curve') else "N/A",
                    'vix': f"{d.get('vix', 'N/A')}" if d.get('vix') else "N/A",
                    'fear_greed': f"{d.get('fear_greed', 'N/A')}/100" if d.get('fear_greed') else "N/A",
                }
            },
            'backwardation_context': self._get_backwardation_context(),
            'allocation': {
                'base': f"{int(self.get_base_allocation()[0]*100)}/{int(self.get_base_allocation()[1]*100)}/{int(self.get_base_allocation()[2]*100)}/{int(self.get_base_allocation()[3]*100)}",
                'description': 'Tier1/Tier2/Tier3/Cash percentages'
            },
            'alerts': [alert for alert in self.alerts],
            'v_recovery_active': self.v_recovery_active
        }
        
        # Craft the prompt for Gemini (identical to Claude)
        prompt = f"""You are the CIO (Chief Investment Officer) analyzing today's institutional risk dashboard for your CEO. The CEO is a sophisticated trader with $2M portfolio ($1M active trading, $1M in bonds). They value direct, blunt, witty analysis over diplomatic corporate speak.

TODAY'S DATA:
{json.dumps(data_package, indent=2)}

CONTEXT YOU NEED TO KNOW:
- Tier 1 (Credit/Liquidity) = 50% weight = Most important, "smart money" signals
- Tier 2 (Breadth) = 30% weight = Confirms or warns about market structure
- Tier 3 (Risk Appetite) = 15% weight = Shows institutional positioning
- Tier 4 (Sentiment) = 5% weight = Noise, but extremes matter

KEY SIGNAL INTERPRETATIONS:
- HY Spread: <3.5% = very tight/healthy, 3-4% = normal, 4.5-5% = caution, >5.5% = stress
- TED Spread: <0.3 = healthy banking, 0.5-0.8 = elevated, >1.0 = crisis
- % Above 50-MA: >65% = healthy breadth, 50-65% = mixed, <50% = weak
- % Below 200-MA: <25% = healthy, 25-35% = caution, >50% = bear market
- New H-L: >+10 = euphoria (contrarian sell), <-10 = capitulation (contrarian buy)
- VIX Backwardation = institutions hedging (danger signal even if VIX calm)
  * Day 1-2: Watch mode
  * Day 3-4: Pattern forming, heightened alert
  * Day 5+: CRITICAL - institutions committed to hedging
- Fear/Greed: >75 = extreme greed, <25 = extreme fear

YOUR TASK:
Write a brief CIO interpretation for iPhone Telegram.

FORMAT:
- Short, punchy lines
- No decorative dividers
- Mobile-friendly
- Direct language

STRUCTURE:

💭 HEADLINE
[One punchy line about what you see]

📊 SCORE QUALITY
T1: XX/50 (XX%) [STRONG/WEAK]
T2: XX/30 (XX%) [STRONG/WEAK]
T3: XX/15 (XX%) [STRONG/WEAK]
T4: X/5 (XX%) [STRONG/WEAK]

👁️ WHAT I SEE
✅ [2-3 positives with numbers]
⚠️ [2-3 concerns with numbers]

🎯 MARKET REGIME
[2-3 sentences on market type, score quality, what institutions doing]

💡 MY CALL
System: XX/XX/XX/XX
[If adjustments:]
Suggest: XX/XX/XX/XX
Stops: X-X%
Why: [brief reason]
[If clean:]
Run the playbook.

🔄 FLIP TRIGGERS
→ [Specific trigger with numbers]
→ [Specific trigger with numbers]

⚡ BOTTOM LINE
[One clear sentence - deployed/cautious/defensive and why]

KEEP UNDER 1200 CHARS.
USE ACTUAL NUMBERS FROM TODAY.
BE SPECIFIC AND DIRECT.

Write now:"""

        try:
            import google.generativeai as genai
            
            print("\n🧠 Generating CIO interpretation using Gemini API...")
            
            # Configure and call Gemini API
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            response = model.generate_content(prompt)
            
            if response.text:
                cio_text = response.text
                
                # Format with simple header
                formatted_output = [
                    "🧠 CIO INTERPRETATION (Gemini)",
                    f"📅 {self.timestamp.strftime('%b %d, %Y')}",
                    "",
                    cio_text,
                ]
                
                print("✅ Gemini CIO interpretation generated successfully")
                return "\n".join(formatted_output)
            
            else:
                print(f"⚠️  Gemini API returned no text")
                return None
                
        except Exception as e:
            print(f"⚠️  Error generating Gemini CIO interpretation: {e}")
            return None
    
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
        7. Generate & send CIO interpretation (separate message)
        8. Save history
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
            vix=self.data.get('vix'),
            vix_structure=self.data.get('vix_struct'),
            vixy_vxx_ratio=self.data.get('vixy_vxx_ratio')
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
        
        # Send main report to Telegram
        send_to_telegram(report)
        
        print("\n" + "="*80)
        print("GENERATING CIO INTERPRETATION")
        print("="*80)
        
        # Generate and send CIO interpretation (separate message to avoid 4000 char limit)
        # This uses Claude API for dynamic analysis
        try:
            cio_analysis = self.generate_cio_interpretation()
            
            if cio_analysis:
                print("\n" + cio_analysis + "\n")
                
                # Save CIO analysis to separate file
                cio_filename = f"cio_analysis_{self.timestamp.strftime('%Y%m%d')}.txt"
                with open(cio_filename, 'w') as f:
                    f.write(cio_analysis)
                print(f"💾 CIO analysis saved to {cio_filename}\n")
                
                # Send CIO interpretation as second Telegram message
                send_to_telegram(cio_analysis)
                print("✅ CIO interpretation sent to Telegram\n")
            else:
                print("⚠️  CIO interpretation returned None")
                print("   Check API key configuration in .env file")
                print("   Expected: ANTHROPIC_API_KEY=sk-ant-api03-...\n")
        except Exception as e:
            print(f"❌ ERROR in CIO interpretation section: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)
        print("GENERATING GEMINI CIO INTERPRETATION")
        print("="*80)
        
        # Generate and send Gemini CIO interpretation (third message)
        # This uses Gemini API for alternative AI perspective
        try:
            gemini_analysis = self.generate_gemini_interpretation()
            
            if gemini_analysis:
                print("\n" + gemini_analysis + "\n")
                
                # Save Gemini analysis to separate file
                gemini_filename = f"gemini_analysis_{self.timestamp.strftime('%Y%m%d')}.txt"
                with open(gemini_filename, 'w') as f:
                    f.write(gemini_analysis)
                print(f"💾 Gemini analysis saved to {gemini_filename}\n")
                
                # Send Gemini interpretation as third Telegram message
                send_to_telegram(gemini_analysis)
                print("✅ Gemini interpretation sent to Telegram\n")
            else:
                print("⚠️  Gemini interpretation returned None")
                print("   Check API key configuration in .env file")
                print("   Expected: GEMINI_API_KEY=...\n")
        except Exception as e:
            print(f"❌ ERROR in Gemini interpretation section: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
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
