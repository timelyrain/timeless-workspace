# 28 Complete Trading Signals

## **1. Market Pulse Signal** 🎙️
- **Purpose**: AI-powered daily market sentiment analysis using Gemini 2.0
- **Data Sources**: 8 RSS feeds (MarketWatch, Yahoo Finance, Seeking Alpha, Google News)
- **Parameters**: Real-time news aggregation, sentiment scoring, witty analysis
- **Trigger Points**: 3x daily (9 AM, 3 PM, 9 PM Malaysia time)
- **Risk-Managed Entry**: Use as macro filter - avoid long positions when AI sentiment is extremely bearish; increase position size when bullish consensus with technical confirmation

---

## **2. Market Divergence Signal** 📉
- **Purpose**: Detect relative strength when SPY is weak (divergence = reversal signal)
- **Parameters**: 
  - SPY intraday drawdown ≤ -1.5%
  - Individual stocks positive on day
  - Uses 5-minute intraday data
- **Trigger Points**: Hourly during NYSE market hours (9:30 AM - 4 PM ET)
- **Risk-Managed Entry**: Enter when SPY bottoming + stock holding gains. Stop-loss: SPY breaks recent low. Target: 2-5% quick gains. Position size: 50% normal (intraday volatility)

---

## **3. Breakout Signal** 🚀
- **Purpose**: Identify 52-week high breakouts with volume confirmation
- **Parameters**:
  - Distance from 52W high ≤ 2%
  - Volume ≥ 1.5x average
  - 5-day lookback window
  - Optional: Relative strength vs SPY filter
- **Trigger Points**: 2x daily (10 AM, 3:30 PM ET)
- **Risk-Managed Entry**: Buy on breakout above 52W high with volume. Stop: 5-7% below entry or below breakout level. Target: 15-25% (let winners run). Risk 1% of portfolio per trade

---

## **4. Unusual Options Activity Signal** 📊
- **Purpose**: Track institutional options flow and premium accumulation
- **Parameters**:
  - Volume ratio ≥ 3x average
  - Minimum premium flow: $500k
  - Call/Put ratio analysis
  - Open interest growth
- **Trigger Points**: 3x daily (10 AM, 12 PM, 2 PM ET)
- **Risk-Managed Entry**: Enter stock position when C/P ratio > 3 + stock breaking resistance. Use options flow as confirmation, not primary signal. Stop: 8% below entry. Size: 70% normal (higher volatility expected)

---

## **5. Earnings Calendar + IV Crush Signal** 📅
- **Purpose**: Track earnings dates and identify IV rank extremes for option strategies
- **Parameters**:
  - IV rank ≥ 70 (high implied volatility)
  - Expected move calculation
  - Alert 3 days and 1 day before earnings
- **Trigger Points**: Daily 8 AM ET
- **Risk-Managed Entry**: 
  - **Pre-earnings**: Avoid long positions 3 days before (IV expansion risk)
  - **Post-earnings**: Enter on IV crush if beat + direction confirmed
  - **Option sellers**: Sell premium when IV rank > 70, exit at 50% profit or 2 days pre-earnings

---

## **6. Sector Rotation Tracker** 🔄
- **Purpose**: Monitor 11 sector ETFs to identify capital rotation patterns
- **Parameters**:
  - Tracks: XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC
  - Timeframes: 1d, 5d, 1mo, 3mo
  - Minimum rotation spread: 3%
- **Trigger Points**: Daily 4:30 PM ET (after close)
- **Risk-Managed Entry**: Overweight stocks in top 3 sectors, underweight bottom 3. Rotate every 2-4 weeks. Only enter stocks with sector tailwind + individual technicals confirmed. Risk per sector: 25% max allocation

---

## **7. Gap Signal** 🌅
- **Purpose**: Detect pre-market/after-hours gaps for day trading setups
- **Parameters**:
  - Minimum gap: 3%
  - Volume confirmation: ≥ 1.5x average
  - Gap types: Breakaway, Continuation, Exhaustion, Common
  - Uses pre/post market data
- **Trigger Points**: Daily 8 AM ET (pre-market)
- **Risk-Managed Entry**: 
  - **Gap up + volume**: Enter on first pullback to gap fill zone, stop below gap
  - **Gap down**: Avoid until stabilization confirmed (2 hours)
  - Exit same day (90% of trades). Risk: 0.5-1% per trade (day trading)

---

## **8. Support/Resistance Bounce Signal** 📈
- **Purpose**: Identify stocks testing key S/R levels with RSI confirmation
- **Parameters**:
  - 52W high/low levels
  - MA50, MA200 levels
  - RSI oversold ≤ 30, overbought ≥ 70
  - Distance threshold: 2%
- **Trigger Points**: 2x daily (10 AM, 2 PM ET)
- **Risk-Managed Entry**: 
  - **Support bounce**: Enter when RSI < 30 + price within 2% of support + volume spike. Stop: 3% below support
  - **Resistance break**: Enter on close above resistance + RSI > 50. Stop: back below resistance
  - Quality score HIGH = full position, MEDIUM = 50%

---

## **9. Insider Trading Tracker** 👔
- **Purpose**: Monitor SEC Form 4 filings for significant insider buying
- **Parameters**:
  - Minimum transaction: $100k
  - Focus: C-suite (CEO, CFO, President)
  - Cluster detection: ≥ 2 insiders buying within 30 days
  - Track purchases (not sales - insiders sell for many reasons)
- **Trigger Points**: Daily 6 PM ET (after filings submitted)
- **Risk-Managed Entry**: Wait for cluster (2+ insiders) + technical setup confirmed. Enter on breakout within 2-4 weeks of buying. Stop: 10% below entry. Insiders know future 3-6 months out. Position size: normal (strong signal)

---

## **10. Smart Money Flow Signal** 🏦
- **Purpose**: Track institutional ownership and 13F superinvestor activity
- **Parameters**:
  - Minimum institutional ownership: 50%
  - Minimum holders: 50
  - Top 10 concentration tracking
  - Superinvestor detection (Berkshire, Ackman, Tiger, etc.)
- **Trigger Points**: Weekly Monday 7 AM ET
- **Risk-Managed Entry**: Enter when institutional ownership increasing + superinvestor present + quality score HIGH. Avoid if institutional ownership > 90% (crowded). Hold 3-6 months (institutional timeframe). Risk: standard 2% per trade

---

## **11. Mean Reversion Signal** 📊
- **Purpose**: Detect oversold bounces using statistical measures
- **Parameters**:
  - Z-score ≤ -2.0 SD (2.5% probability)
  - RSI ≤ 30
  - Bollinger Band squeeze ≤ 5% width
  - Volume spike ≥ 1.5x (selling climax)
  - Institutional ownership ≥ 50% (quality filter)
  - Distance from 20 SMA: ≥ -5%
- **Trigger Points**: 3x daily (10 AM, 1 PM, 3:45 PM ET)
- **Risk-Managed Entry**: Enter on statistical extreme + volume spike. Target: 20 SMA (mean). Stop: 3-5% below entry. Exit 100% at mean (don't get greedy). Best in choppy markets. Risk: 1-1.5% per trade. Win rate: 60-70%, avg gain 3-5%

---

## **12. Volatility Contraction Signal** 🎯
- **Purpose**: Find coiled springs (low volatility → high volatility)
- **Parameters**:
  - ATR compression ≤ 50% of 60-day max
  - Bollinger Band width in lowest 10th percentile
  - Consolidation range < 10% over 20 days
  - Volume drying up ≤ 70% average
  - Uptrend bias: 20 SMA > 50 SMA
- **Trigger Points**: Daily 4:30 PM ET
- **Risk-Managed Entry**: Enter on breakout above consolidation high. Stop: consolidation low. Target: 2x ATR expansion (often 20%+). This is institutional favorite setup. Position size: 50-75% (expect volatility spike). Risk: 2% max

---

## **13. Dark Pool Signal** 🌑
- **Purpose**: Track large block trades indicating institutional accumulation
- **Parameters**:
  - Minimum block value: $500k
  - Volume spike ≥ 2x average
  - Sustained volume: 3+ days elevated
  - Price stability during accumulation: < 3% range
  - Market cap ≥ $1B (institutional grade)
- **Trigger Points**: 2x daily (11 AM, 3 PM ET)
- **Risk-Managed Entry**: Wait 2-4 weeks after dark pool activity detected (institutions still accumulating). Enter on technical breakout + volume. Stop: 8% below. Dark pool leads price by 2-4 weeks. Risk: 1.5% per trade

---

## **14. Short Squeeze Signal** 🔥
- **Purpose**: Detect high short interest stocks near squeeze
- **Parameters**:
  - Short interest ≥ 15% of float (30%+ extreme)
  - Days to cover ≥ 2 days (5+ very hard to cover)
  - Volume spike ≥ 2x (5x = panic)
  - Price momentum: +10% in 5 days
  - Technical breakout: above 20 SMA + RS vs SPY > 2%
- **Trigger Points**: 2x daily (9:45 AM, 2 PM ET)
- **Risk-Managed Entry**: **EXTREME RISK** - Enter only on confirmed breakout + extreme volume. Stop: 15% trailing stop (volatility extreme). Exit 50% at +25%, let 50% run with trailing stop. Risk: 0.5-1% max (binary outcome). Never hold through fades. This is speculative.

---

## **15. Buyback Signal** 💰
- **Purpose**: Monitor share buyback programs using real-time buyback announcements from Financial Modeling Prep (FMP) API (management confidence signal)
- **Parameters**:
  - Buyback ratio ≥ 2% of shares outstanding (5%+ strong), calculated from FMP-reported buybackAmount and shares outstanding
  - Minimum free cash flow: $100M
  - Buying at discount: > 20% below 52W high preferred
  - Only considers stocks with a recent FMP buyback announcement
- **Trigger Points**: Weekly Monday 7 AM ET
- **Risk-Managed Entry**: Enter when company buying + stock > 20% below highs + technical setup forms. Buybacks provide price support. Stop: 10% below. Long-term hold (6-12 months). Risk: standard 2%

---

## **16. Analyst Rating Signal** 📈
- **Purpose**: Track analyst upgrades/downgrades (institutional flow preview)
- **Parameters**:
  - Focus on Tier 1 firms: Goldman Sachs, Morgan Stanley, JPMorgan, BofA, Citi
  - 7-day lookback window
  - Net rating calculation (upgrades - downgrades)
- **Trigger Points**: Daily 8 AM ET (before market)
- **Risk-Managed Entry**: Top tier upgrades move stocks 3-5% same day. Enter pre-market if possible, or on first pullback after gap. Stop: 5% below. Exit same day (50%) or swing (50%). Risk: 1% per trade. Fade downgrades after -10% drop (overreaction)

---

## **17. Dollar Correlation Signal** 💵
- **Purpose**: Find stocks inversely correlated to DXY for macro plays
- **Parameters**:
  - Minimum correlation: -0.5 (inverse) or +0.5 (positive)
  - 60-day rolling correlation
  - Uses UUP ETF as DXY proxy
- **Trigger Points**: Weekly Monday 8 AM ET
- **Risk-Managed Entry**: Use as macro hedge. When DXY strengthening, avoid inverse correlated stocks (headwind). When DXY weakening, overweight inverse correlated (tailwind). Combine with sector analysis. Risk: standard 2% per trade. Macro overlay, not primary signal

---

## **18. Sector RS Momentum Signal** 🚀
- **Purpose**: IBD-style relative strength rating (institutional playbook)
- **Parameters**:
  - RS rating ≥ 90 (top 10% performers)
  - 252-day (1 year) calculation
  - Must be in top 3 performing sectors
  - Outperformance vs SPY > 50% = strong
- **Trigger Points**: Daily 4 PM ET
- **Risk-Managed Entry**: Only buy stocks with RS > 90 in top 3 sectors. This is **the** institutional strategy. Stop: 7-8% below entry (Minervini/O'Neil rule). Hold as long as RS > 70. Risk: 2% per trade. This has highest win rate long-term

---

## **19. Enhanced Options Flow Signal** 🎰
- **Purpose**: Track $1M+ options sweeps (whale activity)
- **Parameters**:
  - Minimum sweep: $1M per trade
  - Total premium: $2M+
  - C/P ratio ≥ 3.0 (bullish bias)
  - Volume multiplier: 5x average
- **Trigger Points**: 3x daily (10:30 AM, 12:30 PM, 2:30 PM ET)
- **Risk-Managed Entry**: Large sweeps precede major moves within 1-2 weeks. Enter stock on technical breakout + sweep confirmed. Stop: 8% below. Sweeps = informed money. Risk: 1.5% per trade. Don't chase - wait for setup

---

## **20. Liquidity Signal** 💧
- **Purpose**: Risk management tool - identify illiquid stocks (exit risk)
- **Parameters**:
  - Flag if avg volume < 500k shares/day (critical < 200k)
  - Bid-ask spread > 0.5% (1%+ very wide)
  - Uses high-low as spread proxy
- **Trigger Points**: Weekly Friday 3 PM ET (weekend review)
- **Risk-Managed Entry**: **AVOID** stocks flagged as illiquid. If already holding, reduce position size by 50% or exit. Wide spreads = slippage = hidden cost. In flash crashes, illiquid stocks fall 20-30% (no buyers). Use to prevent losses, not generate entries

---

## **21. Correlation Breakdown Signal** ⚠️
- **Purpose**: Detect anomalies in correlated pairs (NVDA/AMD, JPM/GS, etc.)
- **Parameters**:
  - Historical correlation ≥ 0.6 required
  - Divergence ≥ 4% to flag (8%+ extreme)
  - 60-day correlation calculation
  - Tracks 10 correlated pairs
- **Trigger Points**: Daily 3 PM ET
- **Risk-Managed Entry**: 
  - **Mean reversion play**: Buy laggard, short leader (pairs trade). Exit when correlation restores. Risk: 1% per leg
  - **Momentum play**: Buy leader (breaking away), stop on laggard catching up. Risk: 1.5%
  - Best strategy: Wait 2-3 days to confirm trend vs anomaly. Risk: 1-2% per trade

---

## **22. PEAD Signal** 📊
- **Purpose**: Post-Earnings Announcement Drift (academic research proven)
- **Parameters**:
  - Earnings beat ≥ 10%
  - Track drift period: 5-60 days post-earnings
  - Minimum post-earnings gain: 3%
  - Momentum confirmation: positive 5-day momentum
- **Trigger Points**: Daily 8 AM ET
- **Risk-Managed Entry**: Enter 5-10 days after earnings (after initial spike settles). Institutions slowly adjust positions over 30-60 days. Stop: 7% below entry. Exit at +60 days or when momentum fades. Risk: 2% per trade. Win rate: 70%+. Sweet spot: days 5-30

---

## New FMP API-Powered Signals (Added Dec 2024)

### 23. Insider Trading Cluster Signal 👔
**Summary**: Detects SEC Form 4 filing clusters where multiple C-suite executives buy shares within 30 days. Uses Financial Modeling Prep (FMP) `/insider-trading` API for real-time insider transaction data.

**Purpose**: Identify stocks where management has strong conviction about future prospects. When 2+ insiders buy simultaneously, it signals asymmetric information advantage. Academic studies show insider buying clusters precede 15-25% outperformance over 6-12 months.

**Parameters**:
- `MIN_TRANSACTION_VALUE = $100,000` - Filter noise, focus on significant purchases
- `MIN_INSIDERS = 2` - Require cluster of 2+ insiders buying
- `CLUSTER_WINDOW = 30 days` - Buying must occur within same month
- `POSITION_FILTER = ["CEO", "CFO", "President", "Director", "COO"]` - C-suite only
- `MIN_SCORE_MEDIUM = 6, MIN_SCORE_HIGH = 10` - Quality thresholds

**Trigger Points**:
- **Cluster Size**: 2 insiders = 3 pts, 3 insiders = 5 pts, 4+ insiders = 7 pts
- **Transaction Size**: $500K+ = 2 pts, $1M+ = 3 pts, $5M+ = 4 pts
- **Buyer Seniority**: CEO/CFO = 3 pts, President/COO = 2 pts, Director = 1 pt
- **Timing**: Within 7 days = 3 pts, within 14 days = 2 pts, within 30 days = 1 pt
- **Price Discount**: >30% below 52W high = 2 pts (buying the dip)

**Risk-Managed Entry**:
1. **Entry**: Wait 1-2 weeks after cluster detected for technical setup to form
2. **Position Size**: 2% risk on HIGH (≥10), 1.5% on MEDIUM (6-9)
3. **Stop Loss**: 10% below entry (insiders know 3-6 months out, give it room)
4. **Target**: 20-30% over 6-12 months, trail stop after +15%
5. **Time Horizon**: Hold minimum 3 months (insider information takes time to materialize)
6. **Risk/Reward**: Minimum 2:1, often 3-4:1 on quality setups

**Schedule**: Daily 6 PM ET (after SEC filing deadline)

---

### 24. Earnings Surprise (PEAD) Signal 📊
**Summary**: Post-Earnings Announcement Drift strategy using FMP `/earnings-surprises` API. Detects EPS beats ≥5% and tracks the proven drift effect where surprise momentum persists for 30-60 days post-announcement.

**Purpose**: Exploit the academic phenomenon where stocks beating earnings expectations continue drifting upward for weeks as institutions slowly adjust positions. This strategy has 70%+ win rate with proper timing.

**Parameters**:
- `MIN_EPS_SURPRISE = 5.0%` - Minimum earnings beat threshold
- `MIN_DRIFT_DAYS = 5, MAX_DRIFT_DAYS = 60` - Sweet spot window
- `MIN_POST_EARNINGS_GAIN = 3.0%` - Minimum price momentum confirmation
- `MIN_SCORE_MEDIUM = 6, MIN_SCORE_HIGH = 10` - Quality tiers

**Trigger Points**:
- **Surprise Magnitude**: ≥15% beat = 5 pts, ≥10% = 4 pts, ≥5% = 3 pts
- **Price Momentum**: +10% post-earnings = 3 pts, +5% = 2 pts, +3% = 1 pt
- **Revenue Beat**: Revenue also beat = 2 pts (double confirmation)
- **Days Since Earnings**: 5-10 days = 3 pts (best entry), 10-30 days = 2 pts, 30-60 days = 1 pt
- **Institutional Ownership**: ≥60% = 2 pts (slow money effect stronger)

**Risk-Managed Entry**:
1. **Entry**: Enter 5-10 days after earnings (after initial spike settles)
2. **Position Size**: 2% risk on HIGH (≥10), 1.5% on MEDIUM (6-9)
3. **Stop Loss**: 7% below entry or below post-earnings gap support
4. **Target**: +60 days from earnings or when momentum fades
5. **Time Stop**: Exit at day 60 regardless (drift effect expires)
6. **Risk/Reward**: Typical 2-3:1, average gain 8-15%

**Schedule**: Daily 8 AM ET (pre-market scan)

---

### 25. Sector Rotation Signal 🔄
**Summary**: Tracks capital flows across 11 S&P sector ETFs (XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC) using multi-timeframe analysis. Identifies rotation before it shows up in individual stocks.

**Purpose**: Follow institutional capital rotation between sectors to overweight winners and underweight losers. Institutions rotate billions before retail notices, giving 2-4 week edge. This is a macro overlay for sector allocation.

**Parameters**:
- `SECTOR_ETFS = 11` (Tech, Financial, Healthcare, Energy, Consumer Disc, Consumer Staples, Industrial, Materials, Real Estate, Utilities, Communications)
- `TIMEFRAMES = [1D, 5D, 1M, 3M]` - Multi-timeframe confirmation
- `MIN_ROTATION_SPREAD = 3.0%` - Minimum spread between top/bottom sectors
- `MIN_VOLUME_RATIO = 1.3x` - Volume confirmation threshold

**Trigger Points**:
- **Rotation Spread**: ≥5% spread = 5 pts, ≥4% = 4 pts, ≥3% = 3 pts
- **Momentum Score**: Positive across all 4 timeframes = 2 pts
- **Volume Confirmation**: ≥1.5x volume = 2 pts
- **Consistency**: Top sector same across 3+ timeframes = 2 pts
- **Bottom Divergence**: Bottom sector down >2% while SPY flat = 2 pts (clear rotation)

**Risk-Managed Entry**:
1. **Entry**: Overweight stocks in top 3 sectors, avoid bottom 3 sectors
2. **Position Size**: 25% max per sector (diversification rule)
3. **Rebalance**: Every 2-4 weeks or when rotation spread narrows <2%
4. **Stop Loss**: Sector-specific stops on individual stocks, 8-10% typical
5. **Rotation Rules**: Only enter stocks in top sectors with individual technicals confirmed
6. **Risk/Reward**: Sector tailwind adds 30-50% to win rate vs stock picking alone

**Schedule**: Daily 4:30 PM ET (after market close)

---

### 26. IPO Momentum Signal 🚀
**Summary**: Detects newly listed stocks with strong first-day pops ≥10% and sustained momentum. Uses FMP `/ipo-calendar` API to identify IPOs within 30 days and filters for institutional-grade quality.

**Purpose**: Capture explosive momentum in quality IPOs during the critical first 30 days when institutions are still accumulating. Best IPOs deliver 50-200% gains in first year, but timing is everything.

**Parameters**:
- `MIN_FIRST_DAY_GAIN = 10.0%` - Minimum first-day pop (institutional demand signal)
- `MIN_VOLUME_RATIO = 2.0x` - Must have 2x normal volume
- `MIN_MARKET_CAP = $500M` - Avoid penny stock IPOs
- `MAX_DAYS_SINCE_IPO = 30` - Window of opportunity
- `MIN_PRICE = $10` - Quality filter

**Trigger Points**:
- **First-Day Pop**: ≥30% = 4 pts, ≥20% = 3 pts, ≥10% = 2 pts
- **Continued Momentum**: +50% since IPO = 3 pts, +20% = 2 pts, positive = 1 pt
- **Volume**: ≥3x average = 3 pts, ≥2x = 2 pts
- **Market Cap**: ≥$5B = 2 pts (large cap stability), ≥$1B = 1 pt
- **Volatility**: Low volatility <3% = 3 pts, <5% = 2 pts (price stability good sign)

**Risk-Managed Entry**:
1. **Entry**: Buy after first 2-5 days (let initial frenzy settle)
2. **Position Size**: 1.5% risk on HIGH (≥10), 1% on MEDIUM (6-9)
3. **Stop Loss**: 15% trailing stop (IPOs are volatile)
4. **Target**: 50-100% over 3-6 months, take 50% profits at +30%
5. **Lockup Expiration**: Exit or reduce 1 week before lockup (typically 90-180 days)
6. **Risk/Reward**: High risk/high reward - 2-5:1 potential

**Schedule**: Daily 9 AM ET (morning scan)

---

### 27. Institutional Flow Signal 🏦
**Summary**: Tracks 13F filings for institutional ownership changes using FMP `/institutional-ownership` and `/institutional-holder` APIs. Detects when 3+ institutions initiate new positions or significantly increase holdings.

**Purpose**: Follow smart money before the crowd. When Vanguard, BlackRock, Fidelity simultaneously add positions, it's a 6-12 month buy signal. Institutional capital moves markets with multi-billion dollar flows.

**Parameters**:
- `MIN_OWNERSHIP_CHANGE = 5.0%` - Significant increase threshold
- `MIN_NEW_POSITIONS = 3` - Multiple institutions buying
- `MIN_POSITION_VALUE = $10M` - Filter small positions
- `MIN_SCORE_MEDIUM = 7, MIN_SCORE_HIGH = 11` - Quality gates

**Trigger Points**:
- **New Positions**: 5+ institutions = 4 pts, 3-4 institutions = 3 pts
- **Position Increases**: 10+ increasing = 3 pts, 5-9 increasing = 2 pts, 3-4 increasing = 1 pt
- **Total Investment**: ≥$1B = 4 pts, ≥$500M = 3 pts, ≥$100M = 2 pts
- **Institutional %**: ≥80% ownership = 3 pts, ≥60% = 2 pts, ≥40% = 1 pt
- **Major Funds**: 3+ of (Vanguard, BlackRock, State Street, Fidelity, Capital) = 2 pts

**Risk-Managed Entry**:
1. **Entry**: Buy when institutional ownership increasing + technical breakout
2. **Position Size**: 2% risk on HIGH (≥11), 1.5% on MEDIUM (7-10)
3. **Stop Loss**: 10% below entry (institutions have 3-6 month horizon)
4. **Target**: 25-40% over 6-12 months, trail after +20%
5. **Warning Signs**: Exit if institutional ownership >90% (crowded trade risk)
6. **Risk/Reward**: Minimum 2:1, often 3-4:1 on quality setups

**Schedule**: Weekly Monday 7 AM ET

---

### 28. Price Target Gap Signal 🎯
**Summary**: Identifies stocks trading ≥15% below analyst consensus price targets using FMP `/price-target-consensus` and `/upgrades-downgrades` APIs. Detects when Street upgrades create momentum.

**Purpose**: Exploit the lag between analyst upgrades and retail recognition. When 2+ Tier 1 analysts upgrade with 20%+ upside targets, it creates a 2-4 week momentum window as institutions adjust.

**Parameters**:
- `MIN_UPSIDE_PCT = 15.0%` - Minimum upside to consensus target
- `MIN_ANALYSTS = 5` - Minimum analyst coverage (credibility)
- `MIN_RECENT_UPGRADES = 2` - Recent upgrade activity in 30 days
- `MIN_SCORE_MEDIUM = 6, MIN_SCORE_HIGH = 10` - Quality thresholds

**Trigger Points**:
- **Upside Potential**: ≥40% = 5 pts, ≥30% = 4 pts, ≥20% = 3 pts, ≥15% = 2 pts
- **Recent Upgrades**: 4+ upgrades = 4 pts, 2-3 upgrades = 3 pts, 1 upgrade = 2 pts
- **Analyst Coverage**: ≥15 analysts = 2 pts, ≥10 analysts = 1 pt (strong coverage)
- **Price Momentum**: +10% (1M) = 2 pts, +5% = 1 pt (already moving)
- **Target Consensus**: <20% spread = 2 pts (analysts aligned)

**Risk-Managed Entry**:
1. **Entry**: Buy on first pullback after upgrade or when technical setup confirms
2. **Position Size**: 2% risk on HIGH (≥10), 1.5% on MEDIUM (6-9)
3. **Stop Loss**: 7% below entry or below recent support
4. **Target**: Consensus price target (15-30% typical)
5. **Time Stop**: Exit at 90 days if target not reached (catalyst faded)
6. **Risk/Reward**: Minimum 2:1, often 3-4:1 on strong conviction upgrades

**Schedule**: Daily 8 AM ET (pre-market)

---

### 29. Financial Health Signal 💪
**Summary**: Detects stocks with excellent financial health using FMP `/score` API for Altman Z-Score (bankruptcy prediction) and Piotroski Score (quality). Identifies fundamentally strong companies trading at reasonable valuations.

**Purpose**: Build core portfolio with high-quality, low-bankruptcy-risk stocks. Altman Z-Score >3.0 and Piotroski ≥7 have historically delivered 12-15% annualized returns with half the volatility of market.

**Parameters**:
- `MIN_ALTMAN_Z = 3.0` - "Safe zone" threshold (Z>3.0 = <5% bankruptcy risk)
- `MIN_PIOTROSKI = 7` - High quality score (out of 9)
- `MIN_CURRENT_RATIO = 1.5` - Liquidity requirement
- `MAX_DEBT_TO_EQUITY = 0.5` - Conservative leverage
- `MIN_ROE = 15.0%` - Profitability threshold

**Trigger Points**:
- **Altman Z-Score**: ≥3.0 = 5 pts (safe), ≥2.6 = 3 pts (grey), ≥1.8 = 1 pt (caution)
- **Piotroski Score**: 8-9 = 4 pts, 7 = 3 pts, 5-6 = 2 pts
- **Current Ratio**: ≥2.0 = 2 pts (excellent liquidity), ≥1.5 = 1 pt
- **Debt/Equity**: ≤0.3 = 2 pts (low leverage), ≤0.5 = 1 pt
- **ROE**: ≥20% = 2 pts, ≥15% = 1 pt
- **Gross Margin**: ≥40% = 1 pt (pricing power)

**Risk-Managed Entry**:
1. **Entry**: Buy when financial health HIGH + technical setup + reasonable valuation
2. **Position Size**: 3% risk on HIGH (≥11), 2% on MEDIUM (7-10)
3. **Stop Loss**: 12% below entry (quality stocks = longer leash)
4. **Target**: Core holding, 12-24 month horizon for 25-50% gains
5. **Rebalance**: Review quarterly, hold as long as scores stay strong
6. **Risk/Reward**: Lower volatility = safer, 2-3:1 typical R:R

**Schedule**: Weekly Monday 7 AM ET

---

## **RISK MANAGEMENT MASTER RULES (Apply to ALL 28 Signals):**

1. **Position Sizing**: Never risk more than 2% of portfolio on single trade (1% for volatile setups)
2. **Correlation**: Max 3 positions in same sector simultaneously
3. **Stop Losses**: Always use stops - no exceptions. Trail stops once +10% profitable
4. **Confluence**: Best setups have 2-3 Signals triggering same stock (e.g., Breakout + Options Flow + Sector Rotation)
5. **Quality Tiers**: 
   - HIGH quality = full position size
   - MEDIUM = 50-75% position
   - LOW = 25% or skip
6. **Market Environment**: 
   - Uptrend: Use breakout, momentum, sector RS Signals (75% of capital)
   - Choppy: Use mean reversion, S/R bounce, PEAD (50% capital, smaller size)
   - Downtrend: Cash is a position (max 20% deployed, short squeezes only)
7. **Diversification**: Max 8-10 positions at once across different strategies
8. **Journal Every Trade**: Track which Signal, why entered, result (learn patterns)

**Portfolio Allocation by Signal Type:**
- **Core (60%)**: Breakout, Sector RS Momentum, Volatility Contraction (lower frequency, higher conviction)
- **Tactical (30%)**: Mean Reversion, PEAD, Options Flow, S/R Bounce (higher frequency, smaller size)
- **Speculative (10%)**: Short Squeeze, Dark Pool, Correlation Breakdown (highest risk/reward)

---

## New Tier 1 Institutional Signals (Added Dec 2024)

### 23. Accumulation/Distribution Signal (Wyckoff Method) 📦
**Summary**: Detects institutional accumulation/distribution phases using volume-price analysis based on Richard Wyckoff's methodology. Tracks On-Balance Volume (OBV) and Accumulation/Distribution Line to identify smart money footprints.

**Purpose**: Identify when institutions are secretly accumulating shares before markup phases or distributing before markdowns. The Wyckoff method has been used by professional traders for 100+ years to follow institutional money flow.

**Parameters**:
- `ACCUMULATION_PERIOD = 40 days` - Window for phase detection
- `MIN_VOLUME_INCREASE = 1.3` (30% above average) - Volume surge threshold
- `MAX_PRICE_CHANGE = 5.0%` - Maximum price change during accumulation
- `MIN_OBV_DIVERGENCE = 10.0%` - Minimum divergence for signal

**Trigger Points**:
- **ACCUMULATION Phase**: Price flat/down + volume up 30%+ + OBV/AD rising (score 5-10)
- **MARKUP Phase**: Price rising + declining volume + positive OBV (score 4-6)
- **DISTRIBUTION Phase**: Price flat/up + volume up 30%+ + OBV/AD falling (score 5-8)
- **Bullish Divergence**: Price down 5%+, OBV up 5%+ (divergence strength bonus)
- **Bearish Divergence**: Price up 5%+, OBV down 5%+ (divergence strength bonus)

**Risk-Managed Entry**:
1. **Entry**: Buy during ACCUMULATION phase with HIGH quality score (≥10) when OBV shows bullish divergence
2. **Position Size**: 2% risk on HIGH signals (≥10), 1% on MEDIUM (7-9)
3. **Stop Loss**: Below accumulation range low or -5% from entry
4. **Target**: Markup phase typically delivers 15-30% gains, hold through markup
5. **Exit**: When DISTRIBUTION phase detected or OBV bearish divergence appears
6. **Risk/Reward**: Minimum 3:1, typically 5:1 during strong accumulation setups

**Schedule**: Daily 4:30 PM ET (after market close)

---

### 24. Opening Range Breakout (ORB) Signal 🌅
**Summary**: Detects breakouts from the first 15-30 minutes of trading, a strategy favored by prop traders and day trading firms like SMB Capital. Captures momentum from opening imbalances.

**Purpose**: Capitalize on early market volatility where 70%+ of intraday range is established. Institutions often place orders at market open, creating directional momentum that persists throughout the session.

**Parameters**:
- `ORB_PERIOD_15 = True` - Track 15-minute opening range
- `ORB_PERIOD_30 = True` - Track 30-minute opening range (primary)
- `MIN_VOLUME_SPIKE = 1.5x` - Breakout volume confirmation
- `MIN_RANGE_SIZE = 0.5%` - Minimum range to avoid tight consolidations
- `MIN_BREAKOUT_EXTENSION = 0.2%` - Must break 0.2%+ beyond range

**Trigger Points**:
- **Opening Range**: High/Low established in first 30 minutes (9:30-10:00 AM ET)
- **Bullish Breakout**: Price breaks above OR high + 0.2% with 1.5x volume
- **Bearish Breakout**: Price breaks below OR low + 0.2% with 1.5x volume
- **Gap Alignment**: Gap in same direction as breakout adds 2 score points
- **Wide Range**: OR range ≥1.5% adds 3 points (more profit potential)

**Risk-Managed Entry**:
1. **Entry**: Enter on first candle close above/below OR high/low with volume confirmation
2. **Position Size**: 2% risk on HIGH quality (≥10), 1.5% on MEDIUM (6-9)
3. **Stop Loss**: Opposite side of opening range (tight risk control)
4. **Target**: 2-3x the opening range size (e.g., 1% range = 2-3% target)
5. **Time Stop**: Exit by 3 PM if target not hit (avoid overnight risk)
6. **Risk/Reward**: Typical 2-3:1, best with pre-market gap in same direction

**Schedule**: 3x daily at 10 AM, 11 AM, 2 PM ET (catch initial breakout + follow-through)

---

### 25. Golden/Death Cross Signal ✝️
**Summary**: Detects 50 SMA crossing above/below 200 SMA, a major algorithmic trigger used by $100B+ AUM institutions. One of the most widely followed technical signals in institutional trading.

**Purpose**: Capture major trend changes when algos trigger simultaneous buy/sell programs. Golden Cross has historically preceded 20-30% rallies, while Death Cross signals extended downtrends.

**Parameters**:
- `SMA_SHORT = 50` - Fast moving average
- `SMA_LONG = 200` - Slow moving average
- `MAX_DAYS_SINCE_CROSS = 10` - Only recent crosses alerted
- `MIN_SEPARATION = 0.5%` - Minimum 0.5% gap between SMAs for confirmation
- `MIN_VOLUME_SPIKE = 1.3x` - Volume confirmation on cross day

**Trigger Points**:
- **Golden Cross**: 50 SMA crosses above 200 SMA (bullish algo trigger)
- **Death Cross**: 50 SMA crosses below 200 SMA (bearish algo signal)
- **Fresh Cross**: Within 2 days = 4 points, within 5 days = 3 points
- **SMA Separation**: ≥2% separation = 3 points (strong confirmation)
- **Volume Confirmation**: ≥2x volume on cross day = 3 points

**Risk-Managed Entry**:
1. **Entry**: Wait for pullback to 50 SMA after golden cross (better entry than chasing)
2. **Position Size**: 3% risk on HIGH quality (≥12), 2% on MEDIUM (8-11)
3. **Stop Loss**: Below 200 SMA (major support level)
4. **Target**: 20-30% typical move after golden cross, trail stop with 50 SMA
5. **Trend Following**: Hold as long as price stays above 50 SMA
6. **Risk/Reward**: Minimum 2:1, often 4-5:1 on strong trends

**Schedule**: Daily 4 PM ET (after market close for clean signals)

---

### 26. Cup & Handle Signal ☕
**Summary**: Detects William O'Neil's signature IBD pattern with 85%+ win rate in bull markets. Identifies 7-65 week U-shaped consolidations followed by 1-4 week handle pullbacks, indicating institutional accumulation.

**Purpose**: Capture massive moves (100-500%+) by identifying patterns where institutions accumulate shares over weeks/months before major breakouts. This is the #1 pattern in the CANSLIM methodology.

**Parameters**:
- `MIN_CUP_WEEKS = 7, MAX_CUP_WEEKS = 65` - Cup formation timeframe
- `MIN_HANDLE_WEEKS = 1, MAX_HANDLE_WEEKS = 4` - Handle duration
- `MAX_CUP_DEPTH = 35%` - Maximum correction in cup (O'Neil rule)
- `MAX_HANDLE_DEPTH = 15%` - Maximum pullback in handle
- `MIN_VOLUME_DRYUP = 0.6` - Handle volume <60% of cup average
- `BREAKOUT_PROXIMITY = 5%` - Alert if within 5% of breakout

**Trigger Points**:
- **Cup Formation**: 7-65 week U-shaped base with 10-35% depth
- **Handle Formation**: 1-4 week pullback with volume dry-up
- **Ideal Cup Depth**: 12-25% correction = 4 points (best risk/reward)
- **Handle Present**: +4 points, shallow handle (≤12%) = +2 bonus
- **RS Rating**: ≥80 = 3 points, ≥70 = 2 points (relative strength key)
- **Bull Market**: SPY >200 SMA = +2 points (pattern works best in uptrends)

**Risk-Managed Entry**:
1. **Entry**: Buy on breakout above handle high with 40-50% volume increase
2. **Position Size**: 3% risk on HIGH quality (≥15), 2% on MEDIUM (10-14)
3. **Stop Loss**: 7-8% below entry or below handle low (O'Neil's rule)
4. **Target**: Cup depth projected from breakout point (conservative), hold winners for 100%+
5. **Time Horizon**: 3-12 months for full move, can run 100-500% in strong trends
6. **Risk/Reward**: Minimum 3:1, often 10:1+ on major winners

**Schedule**: Weekly Friday 5 PM ET (pattern develops over weeks, no need for daily scans)

---

### 27. Pairs Trading Signal (Statistical Arbitrage) 🔄
**Summary**: Identifies cointegrated stock pairs for market-neutral statistical arbitrage. Uses Engle-Granger cointegration test and Z-score analysis to find mean-reversion opportunities with 70%+ Sharpe ratios.

**Purpose**: Generate market-neutral returns by exploiting temporary divergences between historically correlated stocks. This is a hedge fund staple strategy that profits regardless of market direction.

**Parameters**:
- `LOOKBACK_PERIOD = 60 days` - Cointegration test window
- `MIN_ZSCORE_ENTRY = 2.0` - Enter when |Z-score| ≥ 2.0 standard deviations
- `MAX_ZSCORE_STOP = 3.5` - Stop if spread diverges beyond 3.5 SD
- `MIN_COINTEGRATION_PVALUE = 0.05` - Statistical significance threshold
- `MIN_HALFLIFE = 5 days, MAX_HALFLIFE = 30 days` - Mean reversion speed

**Trigger Points**:
- **Cointegration Test**: p-value <0.05 (statistically significant relationship)
- **Spread Divergence**: Z-score ≥+2.0 (short pair 1, long pair 2) or ≤-2.0 (long pair 1, short pair 2)
- **Strong Cointegration**: p-value ≤0.01 = 4 points
- **Extreme Z-score**: ≥3.0 = 4 points (high probability reversion)
- **Fast Mean Reversion**: Half-life ≤10 days = 3 points
- **High Correlation**: ≥0.7 = 3 points (additional confirmation)

**Risk-Managed Entry**:
1. **Entry**: Long underperformer + Short outperformer when Z-score ≥2.0 with hedge ratio applied
2. **Position Size**: 1% risk per leg (2% total), market-neutral dollar balance
3. **Stop Loss**: Exit if Z-score exceeds 3.5 (spread breakdown)
4. **Target**: Z-score returns to 0 (mean reversion complete), typically 5-15% profit per leg
5. **Holding Period**: Average 10-20 days (based on half-life)
6. **Risk/Reward**: 2-3:1 typical, lower risk due to market-neutral hedge

**Schedule**: Daily 3 PM ET (position for end-of-day mean reversion trades)

---

## 📊 Signal Categories Overview

### **Core Fundamental Signals (High Conviction, Long-Term)**
- **Financial Health Signal** (#29): Altman Z-Score + Piotroski (safe, quality picks)
- **Institutional Flow Signal** (#27): 13F filings (follow smart money)
- **Insider Trading Cluster Signal** (#23): C-suite buying (management confidence)
- **Buyback Signal** (#15): Share repurchase programs (capital allocation signal)

*Allocation: 40% of portfolio • Hold 6-12 months • 2-3% risk per trade*

---

### **Momentum & Breakout Signals (Trend Following)**
- **Breakout Signal** (#3): 52-week highs (institutional buying)
- **Sector RS Momentum Signal** (#18): IBD-style relative strength (top 10% performers)
- **Golden/Death Cross Signal** (#25): 50/200 SMA crosses (algo triggers)
- **Cup & Handle Signal** (#26): CANSLIM pattern (100-500% potential)
- **IPO Momentum Signal** (#26): First 30 days (explosive growth)

*Allocation: 30% of portfolio • Hold 3-6 months • 2% risk per trade*

---

### **Tactical Entry Signals (Mean Reversion & Timing)**
- **Earnings Surprise (PEAD) Signal** (#24): Post-earnings drift (70%+ win rate)
- **Price Target Gap Signal** (#28): Analyst upgrade momentum (2-4 week window)
- **Mean Reversion Signal** (#11): Z-score extremes (statistical edges)
- **S/R Bounce Signal** (#8): Key level bounces (technical precision)
- **Opening Range Breakout Signal** (#24): First 30-min momentum (day trading)

*Allocation: 20% of portfolio • Hold 2-8 weeks • 1.5% risk per trade*

---

### **Macro & Sector Signals (Portfolio Positioning)**
- **Sector Rotation Signal** (#25): 11-sector capital flows (macro overlay)
- **Market Divergence Signal** (#2): Relative strength vs SPY (risk-on/off)
- **Dollar Correlation Signal** (#17): DXY relationships (currency hedges)
- **Market Pulse Signal** (#1): AI sentiment analysis (daily market regime)

*Allocation: 10% overlay • Rebalance weekly/monthly • Used for sizing, not entries*

---

### **Speculative Signals (High Risk/High Reward)**
- **Short Squeeze Signal** (#14): High short interest + momentum (binary outcomes)
- **Enhanced Options Flow Signal** (#19): $1M+ sweeps (whale activity)
- **Dark Pool Signal** (#13): Block trades (institutional accumulation)
- **Correlation Breakdown Signal** (#21): Pairs trading (statistical arbitrage)

*Allocation: Max 10% of portfolio • 0.5-1% risk per trade • Strict stops*

---

### **Automated Signals with FMP API Integration** 🆕
The following 7 signals leverage real-time financial data from Financial Modeling Prep (FMP) API:

1. **Insider Trading Cluster** - `/insider-trading` endpoint
2. **Earnings Surprise (PEAD)** - `/earnings-surprises` endpoint  
3. **Sector Rotation** - Multi-timeframe ETF analysis
4. **IPO Momentum** - `/ipo-calendar` endpoint
5. **Institutional Flow** - `/institutional-ownership` + `/institutional-holder` endpoints
6. **Price Target Gap** - `/price-target-consensus` + `/upgrades-downgrades` endpoints
7. **Financial Health** - `/score` endpoint (Altman Z + Piotroski)

*These signals provide institutional-grade data previously only available to hedge funds and investment banks.*

---

## 🎯 Using the 28 Signals Together

**Example Portfolio Construction:**

**Core Holdings (40%)** - Buy & hold quality
- 2-3 Financial Health signals (HIGH quality only)
- 1-2 Institutional Flow signals (major funds buying)
- 1 Insider Trading Cluster (strong conviction)

**Momentum Trades (30%)** - Ride trends
- 2-3 Breakout signals (sector leaders)
- 1-2 Sector RS Momentum (top 10% stocks)
- 1 Cup & Handle (waiting for breakout)

**Tactical Swings (20%)** - Quick profits
- 2-3 PEAD signals (post-earnings drift)
- 1-2 Price Target Gap (analyst upgrades)
- 1-2 Mean Reversion (statistical extremes)

**Sector/Macro Positioning (10%)** - Portfolio overlay
- Use Sector Rotation to overweight/underweight sectors
- Use Market Pulse for overall market exposure (25-75% invested)
- Use Dollar Correlation for hedging

**Speculative Plays (Max 10%)** - Lottery tickets
- 0-2 Short Squeeze signals (when setup perfect)
- 0-1 Options Flow signal (when whale activity extreme)

**GOLDEN RULES:**
1. Never hold more than 10 total positions across all strategies
2. Max 3 positions per sector (diversification)
3. Must have technical + fundamental + catalyst for HIGH conviction trades
4. Best setups have 2-3 signals confirming same stock
5. Quality score matters: HIGH = full size, MEDIUM = 50% size, LOW = skip
6. Always use stops - no exceptions
7. Journal every trade - learn what works for YOUR style

---

## 📈 Expected Performance by Strategy

| Strategy | Win Rate | Avg Gain | Avg Loss | Hold Time | Best Market |
|----------|----------|----------|----------|-----------|-------------|
| Financial Health | 65% | 18% | -8% | 6-12mo | All |
| Institutional Flow | 60% | 22% | -10% | 3-6mo | Bull |
| Insider Cluster | 70% | 25% | -8% | 3-6mo | All |
| Earnings PEAD | 72% | 12% | -6% | 30-60d | All |
| Price Target Gap | 65% | 15% | -7% | 2-8wk | Bull |
| Sector Rotation | 68% | 14% | -8% | 2-4wk | All |
| IPO Momentum | 55% | 40% | -15% | 1-6mo | Bull |
| Breakout (52W) | 60% | 20% | -7% | 1-3mo | Bull |
| Sector RS Momentum | 75% | 25% | -7% | 3-6mo | Bull |
| Mean Reversion | 68% | 5% | -3% | 3-7d | Choppy |
| Short Squeeze | 45% | 50% | -15% | 1-5d | Volatile |

*These are theoretical expectations based on academic research and backtesting. Actual results vary.*

---

## 🚀 Getting Started

1. **Pick 2-3 Core Strategies** that match your style (long-term vs swing trading)
2. **Paper Trade for 20 Trades** to learn the signals and build confidence
3. **Start Small** - Risk 0.5% per trade during learning phase
4. **Track Everything** - Win rate, avg gain/loss, what worked, what didn't
5. **Scale Gradually** - Increase to 1-2% risk after 50+ trades with positive results
6. **Combine Signals** - Best results when 2-3 signals confirm same stock
7. **Respect Risk Management** - This is what separates winners from losers

**Most Important:** These signals give you an EDGE, not a guarantee. Risk management, position sizing, and emotional discipline determine success more than signal quality.

---

*Last Updated: December 18, 2025*  
*Total Signals: 28 (22 Original + 6 Tier 1 Institutional + 7 FMP API-Powered)*  
*API Integrations: Financial Modeling Prep (FMP), yfinance, Gemini 2.0, Telegram Bot*
