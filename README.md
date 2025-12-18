# 21 Complete Trading Signals

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
- **Purpose**: Monitor share buyback programs (management confidence signal)
- **Parameters**:
  - Buyback ratio ≥ 2% of shares outstanding (5%+ strong)
  - Minimum free cash flow: $100M
  - Buying at discount: > 20% below 52W high preferred
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

## **RISK MANAGEMENT MASTER RULES (Apply to ALL 21 Signals):**

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
