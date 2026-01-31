# 🎯 Trading Signals Guide

Last verified vs code: December 30, 2025

**Table of Contents**
- [Tiers 1-6 Overview](#-tier-1-core-institutional-strategies-start-here)
- [Journey Roadmap](#-your-complete-trading-journey-roadmap)
- [Portfolio Construction](#-portfolio-construction-by-phase)
- [Performance Tables](#-signal-win-rates--expected-performance)
- [Risk Rules](#-risk-management-master-rules)
- [Run & Setup](#-additional-resources)

**Signal Index:** [Tier 1](#-tier-1-core-institutional-strategies-start-here) | [Tier 2](#-tier-2-strong-institutional-following-month-3-4) | [Tier 3](#-tier-3-catalyst-based-signals-month-5-6) | [Tier 4](#-tier-4-technical-precision-signals-month-7) | [Tier 5](#-tier-5-macro--positioning-overlays-month-9) | [Tier 6](#-tier-6-speculative--advanced-year-2)

Timezones: All times ET unless noted; Market Pulse uses Malaysia time (UTC+8) explicitly.

**Purpose:** Start your trading journey with the highest-edge signals first. This guide ranks all 29 signals (plus 1 liquidity risk filter) by institutional usage, proven win rates, and beginner-friendliness.

**How to Use:** Master each tier before moving to the next. Focus on 2-3 signals at a time, paper trade 20+ times, then scale up.

---

## 🏆 TIER 1: Core Institutional Strategies (START HERE)

### **Master These First - Your Foundation (Month 1-2)**

**#1. Sector RS Momentum Signal** 🚀
- **Why #1:** IBD/O'Neil institutional playbook, 75% win rate, highest long-term edge
- **Win Rate:** 75% | **Avg Gain:** 25% | **Hold:** 3-6 months
- **Edge:** Only buy top 10% performers (RS ≥90) in top 3 sectors
- **File:** `01-sector-rs-momentum-signals.py`
- **Purpose:** IBD-style relative strength (institutional playbook)
- **Parameters:** RS ≥90 (top 10%), 252-day calc, top 3 sectors only, outperform SPY >50%
- **Schedule:** Daily 4 PM ET
- **Entry:** Only RS>90 in top 3 sectors. Stop: 7-8%. Hold RS>70. Risk: 2%. Highest win rate long-term

**#2. Breakout Signal** 🚀
- **Why #2:** Simple algorithmic trigger, 65% win rate, clear rules
- **Win Rate:** 65% | **Avg Gain:** 20% | **Hold:** 1-3 months
- **Edge:** 52-week high breakouts = institutional FOMO cascade
- **File:** `02-breakout-signals.py`
- **Purpose:** 52-week high breakouts with volume
- **Parameters:** Distance from 52W high ≤2%, Volume ≥1.5x avg, 5-day lookback
- **Schedule:** 2x daily (10 AM, 3:30 PM ET)
- **Entry:** Buy on breakout above 52W high. Stop: 5-7% below. Target: 15-25%. Risk: 1%

**#3. Earnings Surprise (PEAD) Signal** 📊
- **Why #3:** Academic proven, 70%+ win rate, institutions lag 30-60 days
- **Win Rate:** 72% | **Avg Gain:** 12% | **Hold:** 30-60 days
- **Edge:** Post-earnings drift as institutions slowly adjust positions
- **File:** `03-earnings-surprise-signals.py`
- **Purpose:** EPS beats ≥5%, drift 30-60d (institutions lag)
- **Parameters:** Min beat 5%, drift 5-60d, min gain 3%
- **Scoring:** ≥15% beat=5pts, +10% post=3pts, revenue beat=2pts, d5-10=3pts, inst≥60%=2pts
- **Schedule:** Daily 8 AM ET
- **Entry:** Enter 5-10d after. Size: 2% HIGH, 1.5% MED. Stop: 7%. Exit d60. R:R 2-3:1. Avg 8-15%

**#4. Insider Trading Cluster Signal** 👔
- **Why #4:** Information asymmetry, 70% win rate, management knows 3-6 months ahead
- **Win Rate:** 70% | **Avg Gain:** 25% | **Hold:** 3-6 months
- **Edge:** When 2+ C-suite execs buy = strong conviction
- **File:** `04-insider-trading-signals.py`
- **Purpose:** SEC Form 4 clusters of insider buying (C-suite focus)
- **Parameters:** Min $100k buys; ≥2 insiders within 30 days; CEO/CFO/President/Director titles preferred; $500k+ = high conviction; avoid prices < $5
- **Schedule:** Daily 6 PM ET (post-close after filings)
- **Entry:** Wait for cluster + technical setup; enter on breakout/pullback; stop ~10%; target 20-30%; size 2% HIGH (strong cluster), 1.5% MED

**#5. Mean Reversion Signal** 📊
- **Why #5:** Statistical edge, 68% win rate, quick 3-5% gains
- **Win Rate:** 68% | **Avg Gain:** 5% | **Hold:** 3-7 days
- **Edge:** Z-score ≤-2.0 (2.5% probability) + quality stocks = bounce
- **File:** `05-mean-reversion-signals.py`
- **Purpose:** Oversold bounces via statistics
- **Parameters:** Z-score ≤-2.0 SD, RSI ≤30, BB squeeze ≤5%, volume ≥1.5x, dist from 20 SMA ≥-5%
- **Schedule:** 3x daily (10 AM, 1 PM, 3:45 PM ET)
- **Entry:** Extreme + volume spike. Target: 20 SMA. Stop: 3-5%. Exit at mean. Risk: 1-1.5%. Win: 60-70%

**🎓 Month 1-2 Action Plan:**
1. Paper trade signals #1-5 for 20 trades each (100 total trades)
2. Risk 0.5% per trade during learning phase
3. Track: Win rate, avg gain/loss, what worked, what didn't
4. Goal: 60%+ win rate on paper before risking real money

---

## 🥈 TIER 2: Strong Institutional Following (Month 3-4)

### **Build Institutional Perspective**

**#6. Institutional Flow Signal** 🏦
- **Why #6:** Follow 13F filings, 60% win rate, smart money tracker
- **Win Rate:** 60% | **Avg Gain:** 22% | **Hold:** 3-6 months
- **File:** `06-institutional-flow-signals.py`
- **Purpose:** 13F filings ownership changes
- **Parameters:** Min 5% change, ≥3 new positions, min $10M position
- **Scoring:** 5+ new=4pts, 10+ increasing=3pts, ≥$1B=4pts, ≥80% ownership=3pts, major funds=2pts
- **Schedule:** Weekly Monday 7 AM ET
- **Entry:** Increasing + breakout. Size: 2% HIGH (≥11), 1.5% MED. Stop: 10%. Target: 25-40%. Hold 6-12mo

**#7. Sector Rotation Signal** 🔄
- **Why #7:** Macro overlay, adds 30-50% to win rate, capital flow tracker
- **Win Rate:** 68% | **Avg Gain:** 14% | **Hold:** 2-4 weeks
- **File:** `07-sector-rotation-signals.py`
- **Purpose:** Track capital rotation across 11 S&P sector ETFs
- **Parameters:** XLK/XLF/XLV/XLE/XLY/XLP/XLI/XLB/XLRE/XLU/XLC; timeframes 1D/5D/1M/3M; min spread 3% (5%+ strong); volume trend confirmation
- **Schedule:** Daily 4:30 PM ET (post-close for clean data)
- **Entry:** Overweight top 3, avoid bottom 3; rebalance every 2-4 weeks; cap 25% per sector; best in trending markets

**#8. Financial Health Signal** 💪
- **Why #8:** Altman Z + Piotroski, 65% win rate, low-risk quality picks
- **Win Rate:** 65% | **Avg Gain:** 18% | **Hold:** 6-12 months
- **File:** `08-financial-health-signals.py`
- **Purpose:** Altman Z-Score + Piotroski (quality fundamentals)
- **Parameters:** Min Z≥3.0, Piotroski≥7, current ratio≥1.5, debt/equity≤0.5, ROE≥15%
- **Scoring:** Z≥3.0=5pts, Piotroski 8-9=4pts, current≥2.0=2pts, D/E≤0.3=2pts, ROE≥20%=2pts
- **Schedule:** Weekly Monday 7 AM ET
- **Entry:** HIGH + setup + valuation. Size: 3% HIGH (≥11), 2% MED. Stop: 12%. Hold 12-24mo. Core holdings

**#9. Volatility Contraction Signal** 🎯
- **Why #9:** Institutional favorite, coiled springs, 20%+ explosive moves
- **Win Rate:** 65% | **Avg Gain:** 20%+ | **Hold:** 1-3 months
- **File:** `09-volatility-contraction-signals.py`
- **Purpose:** Coiled springs (low vol → high vol)
- **Parameters:** ATR ≤50% of 60d max, BB width lowest 10%, consolidation <10% over 20d, vol ≤70%
- **Schedule:** Daily 4:30 PM ET
- **Entry:** Breakout above consolidation high. Stop: consolidation low. Target: 2x ATR (20%+). Risk: 2%

**#10. Accumulation/Distribution (Wyckoff)** 📦
- **Why #10:** 100-year proven method, 65% win rate, volume-price analysis
- **Win Rate:** 65% | **Avg Gain:** 20% | **Hold:** 2-4 months
- **File:** `10-accumulation-distribution-signals.py`
- **Purpose:** Detect institutional accumulation/distribution via OBV + A/D divergences
- **Parameters:** 40d window, price range ≤5%, volume +30%, OBV/A-D rising, min price $20, avg vol ≥500k
- **Schedule:** Daily 4:30 PM ET (post-close for clean volume)
- **Entry:** Buy when phase=ACCUMULATION and bullish OBV divergence; avoid/exit when phase=DISTRIBUTION

**🎓 Month 3-4 Action Plan:**
1. Continue mastering Tier 1 signals (1-5) with real small positions
2. Add 2-3 Tier 2 signals to paper trading
3. Risk 1% per trade on Tier 1, 0.5% on Tier 2 (still learning)
4. Goal: Build 6-month track record with 60%+ overall win rate

---

## 🥉 TIER 3: Catalyst-Based Signals (Month 5-6)

### **Higher Hit Rate with Timing**

**#11. Price Target Gap Signal** 🎯
- **Why #11:** Analyst upgrades, 65% win rate, 2-4 week momentum window
- **Win Rate:** 65% | **Avg Gain:** 15% | **Hold:** 2-8 weeks
- **File:** `11-price-target-signals.py`
- **Purpose:** Trading ≥15% below analyst consensus
- **Parameters:** Min upside 15%, min 5 analysts, ≥2 recent upgrades
- **Scoring:** ≥40% upside=5pts, 4+ upgrades=4pts, ≥15 analysts=2pts, +10% 1M=2pts, <20% spread=2pts
- **Schedule:** Daily 8 AM ET
- **Entry:** Buy pullback after upgrade. Size: 2% HIGH, 1.5% MED. Stop: 7%. Target: consensus. Exit d90

**#12. Cup & Handle Signal** ☕
- **Why #12:** CANSLIM #1 pattern, 85% win rate in bull markets, 100-500% potential
- **Win Rate:** 85% (bulls) | **Avg Gain:** 100%+ | **Hold:** 3-12 months
- **File:** `12-cup-handle-signals.py`
- **Purpose:** Detect O'Neil cup & handle bases with volume dry-up and RS strength
- **Parameters:** Cup depth 12-35%, handle depth 5-15%, cup 7-65w, handle 1-4w, handle vol <60% of cup, breakout within 5%, min price $20, avg vol ≥500k, RS ≥70-80, SPY >200SMA
- **Schedule:** Weekly Friday 5 PM ET (pattern evolves over weeks)
- **Entry:** Breakout above handle high with volume surge; stop below handle low or 7-8%; target = cup depth added to breakout

**#13. Dark Pool Signal** 🌑
- **Why #13:** Block trades, leads price 2-4 weeks, institutional accumulation
- **Win Rate:** 60% | **Avg Gain:** 15% | **Hold:** 2-8 weeks
- **File:** `13-dark-pool-signals.py`
- **Purpose:** Large block trades (institutional accumulation)
- **Parameters:** Min block $500k, volume ≥2x, sustained 3+ days, price stable <3%, mcap ≥$1B
- **Schedule:** 2x daily (11 AM, 3 PM ET)
- **Entry:** Wait 2-4wks after detection. Enter technical breakout. Stop: 8%. Leads 2-4wks. Risk: 1.5%

**#14. Enhanced Options Flow Signal** 🎰
- **Why #14:** $1M+ sweeps, whale activity, 1-2 week lead time
- **Win Rate:** 65% | **Avg Gain:** 15% | **Hold:** 1-2 weeks
- **File:** `14-enhanced-options-flow-signals.py`
- **Purpose:** $1M+ options sweeps (whale activity)
- **Parameters:** Min sweep $1M, total premium $2M+, C/P ≥3.0, volume 5x avg
- **Schedule:** 3x daily (10:30 AM, 12:30 PM, 2:30 PM ET)
- **Entry:** Sweeps precede moves 1-2wks. Enter breakout + sweep. Stop: 8%. Risk: 1.5%. Don't chase

**#15. Buyback Signal** 💰
- **Why #15:** Management confidence, price support, 60% win rate
- **Win Rate:** 60% | **Avg Gain:** 18% | **Hold:** 6-12 months
- **File:** `15-buyback-signals.py`
- **Purpose:** Share buyback programs (management confidence)
- **Parameters:** Buyback ratio ≥2% (5%+ strong), min FCF $100M, >20% below 52W high preferred
- **Schedule:** Weekly Monday 7 AM ET
- **Entry:** Company buying + >20% below highs + setup. Stop: 10%. Hold 6-12mo. Risk: 2%

**🎓 Month 5-6 Action Plan:**
1. Tier 1 signals (1-5) should be your core portfolio (50% allocation)
2. Tier 2 signals (6-10) for diversification (30% allocation)
3. Add 2-3 Tier 3 signals for catalyst-based timing (20% allocation)
4. Goal: Consistent profitability with 8-10 total positions max

---

## 📊 TIER 4: Technical Precision Signals (Month 7+)

### **Refine Entry Timing**

**#16. Support/Resistance Bounce Signal** 📈
- **Win Rate:** 60% | **File:** `16-support-resistance-signals.py`
- **Purpose:** Key S/R levels with RSI confirmation
- **Parameters:** 52W high/low, MA50/MA200 levels, RSI ≤30 or ≥70, distance 2%
- **Schedule:** 2x daily (10 AM, 2 PM ET)
- **Entry:** Support: RSI<30 + within 2% + volume spike. Stop: 3% below. Resistance: Close above + RSI>50

**#17. Golden/Death Cross Signal** ✝️
- **Win Rate:** 65% | **File:** `17-golden-cross-signals.py`
- **Purpose:** Track 50/200 SMA crosses (golden = bullish, death = bearish) used by institutional algos
- **Parameters:** 50/200 SMA, fresh cross ≤10 days, separation ≥0.5-2%, cross volume ≥1.3x avg, price ≥$20, avg vol ≥500k
- **Schedule:** Daily 4 PM ET (post-close for clean MA signals)
- **Entry:** Golden: buy pullback to 50 SMA after cross; stop below 200 SMA; target ~20% or prior high. Death: short/avoid while below 200 SMA

**#18. Opening Range Breakout (ORB)** 🌅
- **Win Rate:** 65% (day trading) | **File:** `18-orb-signals.py`
- **Purpose:** Catch momentum breaks of the 15/30-min opening range with volume and gap confluence
- **Parameters:** 15/30-min ORB, min range 0.5% (1-1.5% better), breakout ≥0.2% past OR high/low, volume ≥1.5x avg, gap in same direction boosts score, min price $20, avg vol ≥500k
- **Schedule:** 10 AM, 11 AM, 2 PM ET (covers initial ORB plus midday follow-through)
- **Entry:** Enter on close above OR high (long) or below OR low (short) with volume; stop opposite side of range; target 2-3x range size; skip very tight ranges

**#19. Gap Signal** 🌅
- **Win Rate:** 60% (day trading) | **File:** `19-gap-signals.py`
- **Purpose:** Pre-market/after-hours gaps for day trading
- **Parameters:** Min gap 3%, volume ≥1.5x, types: Breakaway/Continuation/Exhaustion
- **Schedule:** Daily 8 AM ET
- **Entry:** Gap up+volume: Enter pullback to fill zone. Gap down: Wait 2hrs. Exit same day. Risk: 0.5-1%

**#20. Smart Money Flow Signal** 🏦
- **Win Rate:** 60% | **File:** `20-smart-money-flow-signals.py`
- **Purpose:** Institutional ownership & 13F superinvestors
- **Parameters:** Min 50% institutional ownership, min 50 holders, top 10 concentration
- **Schedule:** Weekly Monday 7 AM ET
- **Entry:** Increasing ownership + superinvestor + HIGH score. Avoid >90%. Hold 3-6mo. Risk: 2%

---

## 🌍 TIER 5: Macro & Positioning Overlays (Month 9+)

### **Portfolio-Level Decisions**

**#21. Market Pulse Signal** 🎙️ *(macro filter)*
- **Why:** Portfolio-level risk dial using AI macro sentiment
- **File:** `21-market-pulse-signals.py`
- **Purpose:** AI-powered daily sentiment using Gemini 2.0 to gate sizing
- **Data:** 8 RSS feeds (MarketWatch, Investing.com, Yahoo, Seeking Alpha, multiple Google News queries)
- **Schedule:** 3x daily (9 AM, 3 PM, 9 PM Malaysia time / UTC+8) or on-demand run
- **Usage:** Macro filter; avoid longs when extreme bearish, size up when bullish

**#22. Market Divergence Signal** 📉
- **Why:** Catch stocks showing relative strength while SPY is weak
- **Win Rate:** 55% (intraday) | **File:** `22-spy-divergence.py`
- **Purpose:** Detect relative strength when SPY weak
- **Parameters:** SPY intraday drawdown ≤-1.0% and stock green; or stock outperforming SPY by >2%; 5-min intraday data
- **Schedule:** Run intraday as needed during US session
- **Entry:** Enter when SPY stabilizes and stock remains green/RS >2%. Stop: SPY breaks low. Target: 2-5%. Size: ~50%

**#23. Dollar Correlation Signal** 💵 *(hedge/filter)*
- **Why:** Hedge or lean into USD trends that drive equity moves
- **File:** `23-dollar-correlation-signals.py`
- **Purpose:** Stocks inversely correlated to DXY
- **Parameters:** Min correlation -0.5 (inverse) or +0.5 (positive), 60-day rolling, uses UUP ETF
- **Schedule:** Weekly Monday 8 AM ET
- **Entry:** Macro hedge. DXY strengthening = avoid inverse. DXY weakening = overweight inverse. Risk: 2%

**#24. Analyst Rating Signal** 📈
- **Why:** Tier 1 broker upgrades/downgrades often move price same day
- **Win Rate:** 60% (same-day) | **File:** `24-analyst-rating-signals.py`
- **Purpose:** Track upgrades/downgrades (institutional preview)
- **Parameters:** Tier 1: GS, MS, JPM, BofA, Citi. 7-day lookback. Net rating calculation
- **Schedule:** Daily 8 AM ET
- **Entry:** Top tier upgrades move 3-5% same day. Enter pre-market or pullback. Stop: 5%. Risk: 1%

**#25. Earnings Calendar + IV Crush** 📅
- **Why:** Monetize implied volatility collapse around earnings
- **File:** `25-iv-crush-signals.py`
- **Purpose:** Advanced IV crush prediction with volatility analysis
- **Parameters:** IV percentile ≥60, IV-realized gap ≥5%, crush score 0-15pts, VIX correlation; 30-day lookahead
- **Schedule:** Daily 8 AM ET
- **Entry:** Pre-earnings: Sell premium when score HIGH. Post: Buy cheap options after crush. Iron condors best

---

## ⚠️ TIER 6: Speculative / Advanced (Year 2+)

### **High Risk/High Reward - Use Carefully**

**#26. IPO Momentum Signal** 🚀
- **Win Rate:** 55% | **Risk:** High volatility
- **File:** `26-ipo-momentum-signals.py`
- **Purpose:** Newly listed with ≥10% first-day pop
- **Parameters:** Min 10% first-day, volume 2x, mcap ≥$500M, max 30d since IPO, min price $10
- **Scoring:** ≥30% pop=4pts, +50% since=3pts, ≥3x vol=3pts, ≥$5B mcap=2pts, low vol<3%=3pts
- **Schedule:** Daily 9 AM ET
- **Entry:** Buy d2-5 after (frenzy settles). Size: 1.5% HIGH, 1% MED. Stop: 15% trail. Exit 1wk before lockup

**#27. Short Squeeze Signal** 🔥
- **Win Rate:** 45% | **Risk:** EXTREME (binary outcomes)
- **File:** `27-short-squeeze-signals.py`
- **Purpose:** High short interest near squeeze
- **Parameters:** SI ≥15% (30%+ extreme), days to cover ≥2, volume ≥2x, +10% in 5d, break 20 SMA
- **Schedule:** 2x daily (9:45 AM, 2 PM ET)
- **Entry:** EXTREME RISK. Confirmed breakout + volume. Stop: 15% trailing. Exit 50% at +25%. Risk: 0.5-1%

**#28. Pairs Trading Signal** 🔄
- **Win Rate:** 70% Sharpe | **Risk:** Requires sophistication
- **File:** `28-pairs-trading-signals.py`
- **Purpose:** Market-neutral stat arb using cointegrated pairs (hedge market beta)
- **Parameters:** Engle-Granger p<0.05, Z-score ≥2.0 entry (stop >3.5), half-life 5-30d, correlation ≥0.5 (≥0.7 best), min price $20, 60d lookback
- **Schedule:** Daily 3 PM ET (end-of-day positioning)
- **Entry:** Long laggard / short leader when Z≥2; exit at Z=0; stop if Z>3.5; size legs dollar-neutral (e.g., ~$5k each)

**#29. Correlation Breakdown Signal** ⚠️
- **Win Rate:** 60% | **Risk:** Statistical arbitrage, advanced
- **File:** `29-correlation-breakdown-signals.py`
- **Purpose:** Detect anomalies in correlated pairs
- **Parameters:** Historical corr ≥0.6, divergence ≥4% (8%+ extreme), 60-day calc, 10 pairs
- **Schedule:** Daily 3 PM ET
- **Entry:** Mean reversion: Buy laggard, short leader. Momentum: Buy leader. Wait 2-3d confirm. Risk: 1-2%

---

## 📅 Your Complete Trading Journey Roadmap

### **Phase 1: Foundation (Months 1-2)**
**Focus:** Signals #1-5 (Tier 1)
- **Action:** Paper trade 100 total trades (20 per signal)
- **Risk:** 0% (paper only)
- **Goal:** Learn the signals, build confidence, 60%+ win rate on paper
- **Time Commitment:** 1-2 hours/day studying + tracking signals

### **Phase 2: Real Money Small (Months 3-4)**
**Focus:** Signals #1-5 real money + #6-10 paper
- **Action:** Risk 0.5-1% per trade on Tier 1 signals
- **Capital:** Start with $5K-10K max (even if you have more)
- **Goal:** First 50 real trades with positive P&L
- **Time Commitment:** 2-3 hours/day (market watch + journaling)

### **Phase 3: Scale & Diversify (Months 5-6)**
**Focus:** Signals #1-10 real money + #11-15 paper
- **Action:** Risk 1-2% per trade, 8-10 positions max
- **Portfolio Split:** 50% Tier 1, 30% Tier 2, 20% Tier 3
- **Goal:** Consistent monthly profitability (6 months track record)
- **Time Commitment:** 3-4 hours/day (full routine established)

### **Phase 4: Mature Trader (Months 7-12)**
**Focus:** All signals 1-25, selective use of 26-29
- **Action:** Full portfolio allocation across strategies
- **Risk Management:** 2% per trade max, strict stops
- **Goal:** 15-25% annual returns, Sharpe ratio >1.5
- **Time Commitment:** 2-3 hours/day (efficient routine)

---

## 🎯 Portfolio Construction by Phase

### **Beginner Portfolio (Months 1-4)**
```
Total Positions: 3-5 max
- 2-3 Sector RS Momentum (#1)
- 1-2 Breakouts (#2)
- 0-1 PEAD (#3)
Cash Reserve: 50%+ (stay cautious)
```

### **Intermediate Portfolio (Months 5-8)**
```
Total Positions: 6-8 max
Core (50%):
- 2-3 Sector RS Momentum (#1)
- 1-2 Insider Clusters (#4)
- 1 Financial Health (#8)

Tactical (30%):
- 1-2 Breakouts (#2)
- 1 PEAD (#3)

Quick Gains (20%):
- 1 Mean Reversion (#5)
- 1 Price Target Gap (#11)

Cash Reserve: 20-30%
```

### **Advanced Portfolio (Months 9+)**
```
Total Positions: 8-10 max
Core Holdings (40%):
- 2 Financial Health (#8)
- 1-2 Institutional Flow (#6)
- 1 Insider Cluster (#4)

Momentum Trades (30%):
- 2-3 Sector RS / Breakouts (#1, #2)
- 1 Cup & Handle (#12)

Tactical Swings (20%):
- 2 PEAD / Price Target (#3, #11)
- 1 Dark Pool (#13)

Speculative (10%):
- 0-1 Short Squeeze (#27) when perfect setup
- 0-1 Options Flow (#14)

Cash Reserve: 10-20%
```

---

## 🏆 Signal Win Rates & Expected Performance

| Priority | Signal Name | Win Rate | Avg Gain | Avg Loss | Best Market |
|----------|-------------|----------|----------|----------|-------------|
| #1 | Sector RS Momentum | 75% | 25% | -7% | Bull |
| #2 | Breakout (52W) | 65% | 20% | -7% | Bull |
| #3 | PEAD | 72% | 12% | -6% | All |
| #4 | Insider Cluster | 70% | 25% | -8% | All |
| #5 | Mean Reversion | 68% | 5% | -3% | Choppy |
| #6 | Institutional Flow | 60% | 22% | -10% | Bull |
| #7 | Sector Rotation | 68% | 14% | -8% | All |
| #8 | Financial Health | 65% | 18% | -8% | All |
| #9 | Vol Contraction | 65% | 20%+ | -10% | Bull |
| #10 | Wyckoff A/D | 65% | 20% | -8% | All |

*Note: These are theoretical expectations. Your actual results will vary based on execution, discipline, and market conditions.*

*Provenance: Indicative, based on historical logic/backtests in the scripts; not forward-looking performance.*

---

## ✅ Golden Rules (Apply to ALL Signals)

- Master first: 20+ paper trades per signal, 60%+ win rate before live
- Position sizing caps: Tier 1: 1-2%; Tier 2-3: 1-1.5%; Tier 4-6: 0.5-1%; never >2%
- Stops always: hard stops only; trail once +10%
- Max exposure: 10 positions total; max 3 per sector; start with 5 live max until 3 profitable months
- Confluence sizing: 1 signal = 50% size; 2 signals = 75%; 3 signals = 100%
- Market regime: Bull → momentum (1,2,6,9,12); Choppy → mean reversion (5,16); Bear → mostly cash (≤20%), squeeze-only
- Journal and review weekly; adjust monthly by win rate per signal

**Typical stop/target conventions:**
- Intraday (ORB/Gap): stop = other side of range (~1R); target = 2-3R
- Swing (Breakout/RS/PEAD): stop 5-8%; target 15-25% (or 2x ATR for vol contraction)
- Position/multi-week (Sector RS/Financial/Buyback): stop 7-12%; target 20-40%; trail after +10%
- IV premium sells: defined-risk spreads; size small; manage to 50-70% max profit

**Glossary (quick):** RS = relative strength vs peers/benchmark; IV percentile = current IV vs its own history; Z-score = standard deviations from mean; DTC = days to cover (short interest); Confluence = multiple signals aligning on the same ticker.

---

## 🚀 Quick Start Checklist

- [ ] Read this README (focus Tier 1 first)
- [ ] Configure `.env` (Telegram, FMP, Gemini as needed) + `watchlist.txt`
- [ ] Paper trade signals #1-5: 20 trades each (track win rate, R:R)
- [ ] Hit 60%+ win rate on 3 signals before going live; keep risk 0.5% when you start
- [ ] Add Tier 2 after 6-8 weeks: start with 2 signals, paper first
- [ ] Max 5 live positions until 3 straight profitable months; journal every trade
- [ ] Reassess monthly: sizing, stops, and which signals fit your style

---

## 📚 Additional Resources

**Full Signal Details:** See README.md for complete documentation of all 29 signals

**Python Scripts:** All signals are in `/projects/` directory:
- Run locally: `python projects/[signal-name].py`
- Example: `python projects/07-sector-rotation-signals.py`
- Automated: GitHub Actions workflows run daily/weekly

**Environment Setup:**
- Core: `.env` with `TELEGRAM_TOKEN`, `CHAT_ID` (required for Telegram alerts; without them, scripts print to console)
- Data keys: `FMP_API_KEY` (IPO momentum, IV crush), `GEMINI_API_KEY` (Market Pulse), yfinance (most scans)
- Watchlist: Edit `watchlist.txt`; many scanners load from it
- Failure modes: Missing keys degrade gracefully—alerts print locally instead of sending; IPO/IV crush skip if FMP key absent; Market Pulse exits if Gemini key missing

**Common failures & fixes:**
- Missing `GEMINI_API_KEY`: Market Pulse will exit early. Add key or skip running that script.
- Missing `FMP_API_KEY`: IPO Momentum and IV Crush will skip/return empty. Add key to `.env`.
- Missing `TELEGRAM_TOKEN`/`CHAT_ID`: Scripts still run but only print; add both to send alerts.
- Empty `watchlist.txt`: Many scans will return nothing; seed with 10–20 liquid tickers.

**Outputs:**
- With Telegram keys: alerts send to your chat; otherwise they print to console
- Sample alert:
```
⏰ Market Scan: 2025-12-30 10:00 ET
🚀 DIVERGENCE ALERT: AAPL
SPY fell -1.2% intraday, AAPL +0.8%
```

**Maintenance:**
- Update "Last verified vs code" when scripts change
- Keep README file names/numbers in sync with `/projects/` and workflows

## 📖 Glossary

- RS (Relative Strength): A stock’s performance vs peers/benchmarks over a lookback (higher = stronger leader)
- IV Percentile: Current implied volatility relative to its own 1y history (higher = richer premium)
- Z-score: Standard deviations from mean; used for mean reversion and spread extremes
- DTC (Days to Cover): Short interest divided by average daily volume; higher = harder for shorts to exit
- ATR (Average True Range): Recent average range; often used for stops/targets
- R / Risk Unit: The initial risk on a trade (distance from entry to stop); targets often quoted in R multiples
- BB Width: Bollinger Band width; compression signals low volatility before expansion
- Sweep / Block Trade: Large options flow (sweep = fast, multi-exchange buy); block = single large print (often institutional)
- 52W High/Low: Highest/lowest price in the past 52 weeks; common breakout/reversal reference
- SMA/EMA: Simple/Exponential Moving Average; trend and crossovers (e.g., 50/200) guide bias
- UUP / DXY: UUP ETF proxies the US Dollar Index (DXY) for correlation/hedge signals
- SPY: S&P 500 ETF; used as market benchmark in RS/divergence logic

**Support:**
- README.md: Complete signal documentation
- Python files: Each has detailed docstring at top
- Workflows: `.github/workflows/` for automation schedules

---

## 🛡️ RISK MANAGEMENT TOOLS (Not Ranked)

### **Liquidity Scanner** 💧
- **File:** `30-liquidity-signals.py`
- **Purpose:** Risk management tool to flag illiquid stocks (exit risk)
- **Parameters:** Avg vol <500k (critical <200k), spread >0.5% (1%+ wide) using high-low proxy
- **Schedule:** Weekly Friday 3 PM ET (weekend review)
- **Action:** AVOID CRITICAL/HIGH flags; if already holding, cut ~50% or exit to reduce slippage risk

**🎯 Usage Tip:** Run before new entries; this is a "what NOT to trade" filter, not a buy signal.

---

## 🛡️ RISK MANAGEMENT MASTER RULES

**Position Sizing:**
- Never risk >2% of portfolio per trade (1% for volatile)
- HIGH quality = full size, MEDIUM = 50-75%, LOW = skip
- Max 3 positions in same sector
- Max 8-10 total positions across all strategies

**Stop Losses:**
- Always use stops - no exceptions
- Trail stops once +10% profitable
- Adjust stops based on signal timeframe (day trade 3-5%, swing 7-10%, long-term 12-15%)

**Confluence:**
- Best setups have 2-3 signals confirming same stock
- Example: Breakout + Options Flow + Sector Rotation = HIGH conviction

**Market Environment:**
- **Uptrend** (SPY > 200 SMA): Breakout, momentum, sector RS signals. 75% capital deployed
- **Choppy** (SPY near 200 SMA): Mean reversion, S/R bounce, PEAD. 50% capital, smaller size
- **Downtrend** (SPY < 200 SMA): Cash is position. Max 20% deployed, short squeezes only

**Portfolio Allocation:**
- Core (60%): Breakout, Sector RS, Volatility Contraction (lower frequency, higher conviction)
- Tactical (30%): Mean Reversion, PEAD, Options Flow (higher frequency, smaller size)
- Speculative (10%): Short Squeeze, Dark Pool, Correlation Breakdown (highest risk/reward)

**Journal Every Trade:**
- Track: Signal used, entry reason, exit reason, P/L, lessons learned
- Review monthly: Which signals work best for YOUR style
- Adapt strategy based on data, not emotions

---

## 📊 EXPECTED PERFORMANCE BY STRATEGY

| Strategy | Win Rate | Avg Gain | Avg Loss | Hold Time | Best Market |
|----------|----------|----------|----------|-----------|-------------|
| Sector RS Momentum | 75% | 25% | -7% | 3-6mo | Bull |
| Breakout (52W) | 65% | 20% | -7% | 1-3mo | Bull |
| Earnings PEAD | 72% | 12% | -6% | 30-60d | All |
| Insider Cluster | 70% | 25% | -8% | 3-6mo | All |
| Mean Reversion | 68% | 5% | -3% | 3-7d | Choppy |
| Institutional Flow | 60% | 22% | -10% | 3-6mo | Bull |
| Sector Rotation | 68% | 14% | -8% | 2-4wk | All |
| Financial Health | 65% | 18% | -8% | 6-12mo | All |
| Volatility Contraction | 65% | 20% | -8% | 1-3mo | Bull |
| Accumulation/Dist | 65% | 20% | -8% | 2-4mo | All |
| Price Target Gap | 65% | 15% | -7% | 2-8wk | Bull |
| Cup & Handle | 85% (bull) | 100%+ | -8% | 3-12mo | Bull |
| Dark Pool | 60% | 15% | -8% | 2-8wk | All |
| Enhanced Options Flow | 65% | 15% | -8% | 1-2wk | All |
| Buyback | 60% | 18% | -10% | 6-12mo | All |
| Support/Resistance | 60% | 5% | -3% | days | Choppy |
| Golden/Death Cross | 65% | 20% | -10% | 1-3mo | All |
| Opening Range Breakout | 65% | 2-3R | -1R | intraday | Volatile |
| Gap | 60% | 3-5% | -3% | intraday | Volatile |
| Smart Money Flow | 60% | 22% | -10% | 3-6mo | Bull |
| Market Pulse (macro filter) | N/A (filter) | N/A | N/A | daily | All |
| SPY Divergence | 55% | 2-5% | -2% to -3% | intraday | Choppy |
| Dollar Correlation | Hedge tool | 5-10% | -3% to -5% | weekly | All |
| Analyst Rating | 60% | 3-5% | -5% | 0-1d | All |
| IV Crush (Earnings) | Premium strategy | 5-15% | Defined spread risk | 1-10d | Earnings |
| IPO Momentum | 55% | 40% | -15% | 1-6mo | Bull |
| Short Squeeze | 45% | 50% | -15% | 1-5d | Volatile |
| Pairs Trading | Market-neutral | 2-5% spread reversion | -2% stop | 5-30d | All |
| Correlation Breakdown | 60% | 3-6% | -3% | 1-5d | All |

*Theoretical expectations based on academic research and backtesting. Actual results vary.*

---

**Remember:** 
- The best trader isn't the one who knows the most signals
- It's the one who masters 3-5 signals perfectly
- Start with Tier 1, build competence, then expand
- Discipline beats intelligence in trading

**Good luck on your trading journey! 🚀**

*Last Updated: December 30, 2025*

---

## 🛠️ SETUP & CONFIGURATION GUIDE

### **Overview**
This workspace contains automated trading signal systems that run on schedule and require minimal manual intervention. Below is the complete setup documentation for all systems.

---

### **1. Environment Setup**

#### **Prerequisites**
- macOS with Python 3.9+
- Virtual environment configured
- API keys for Gemini AI and Telegram

#### **Environment Variables (.env file)**
```bash
# Create .env in workspace root or projects/ directory
TELEGRAM_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### **Installation**
```bash
# Navigate to workspace
cd ~/Developer/timeless-workspace

# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# (Includes: yfinance, feedparser, google-generativeai, requests, python-dotenv, pytz)
```

---

### **2. Watchlist System (Autonomous Updates)**

#### **What It Does**
- Automatically scans S&P 500 top performers every Sunday 8 PM
- Finds breakout stocks near 52-week highs
- Updates `watchlist.json` with strongest 40-60 stocks
- Balances sector exposure to avoid concentration
- Maintains core mega-cap holdings

#### **Files Involved**
- **`watchlist.json`** - Master watchlist (edited by updater)
- **`projects/watchlist-auto-updater.py`** - Scans and updates watchlist
- **`projects/watchlist_loader.py`** - Loader utility for other scripts
- **`scripts/update-watchlist.sh`** - Bash wrapper with sleep prevention

#### **Schedule: Sunday 8:00 PM (Automated via Launchd)**

**Status Check:**
```bash
# View if job is loaded
launchctl list | grep timeless

# View logs
tail -f ~/Developer/timeless-workspace/logs/watchlist-updates.log
tail -f ~/Developer/timeless-workspace/logs/watchlist-errors.log
```

**Manual Run:**
```bash
cd ~/Developer/timeless-workspace
source .venv/bin/activate
python projects/watchlist-auto-updater.py
```

**Management Commands:**
```bash
# Unload (stop) the job
launchctl unload ~/Library/LaunchAgents/com.timeless.watchlist-updater.plist

# Reload (restart) the job
launchctl unload ~/Library/LaunchAgents/com.timeless.watchlist-updater.plist
launchctl load ~/Library/LaunchAgents/com.timeless.watchlist-updater.plist

# Test run immediately
launchctl start com.timeless.watchlist-updater

# Remove completely
launchctl unload ~/Library/LaunchAgents/com.timeless.watchlist-updater.plist
rm ~/Library/LaunchAgents/com.timeless.watchlist-updater.plist
```

**What Gets Updated:**
- Min Market Cap: $10B
- Min Avg Volume: 1M shares/day
- Min Price: $20
- Max Stocks: 60
- Core Holdings: Always kept (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, JPM, V, MA, UNH, LLY, HD, COST)
- Sector Balance: Max 35% per sector

**Technical Details:**
- Uses `caffeinate` to prevent Mac sleep during execution
- Logs to separate stdout/stderr files
- Automatically activates virtual environment
- Sleep prevention: 1-hour timeout buffer
- Runs via macOS Launchd (not cron) for better reliability

---

### **3. Sector RS Momentum Signal**

#### **Purpose**
IBD-style relative strength scanner identifying the strongest stocks in the strongest sectors.

**File:** `projects/01-sector-rs-momentum-signals.py`  
**Schedule:** Daily 4 PM ET  
**Watchlist:** Uses `watchlist.json`

#### **Setup**
```bash
# Run manually
python projects/01-sector-rs-momentum-signals.py

# Output: Telegram alert + console display
```

**What It Scans:**
- RS Rating: Compares each stock vs SPY over 252 trading days
- Top 3 Sectors: Measures 3-month performance of 11 sector ETFs
- Filters: RS ≥90 (top 10%), must be in top 3 sector
- Quality Score: Based on RS ≥95, top sector status, outperformance >50%

**Output Format:**
```
🚀 Sector RS Momentum Scanner
⏰ 2025-12-30 04:00 PM ET

🔥 Top 3 Sectors:
  1. Technology: +15.2%
  2. Communication: +12.8%
  3. Consumer Disc: +9.4%

📊 Found 3 high RS stock(s)

🟢 NVDA - $875.50 [TOP SECTOR]
  📈 RS Rating: 98/99 (Top 2%)
  💪 Outperformance: +85.3% vs SPY
  🏢 Sector: Technology
  ⭐ Score: 10/10 (HIGH)
```

---

### **4. Market Pulse Signal (Daily News Bot)**

#### **Purpose**
Analyzes daily financial news from 11 sources using Gemini AI to provide:
- Narrative market briefing (witty, conversational)
- Structured sentiment/impact analysis (JSON)
- Top tickers and macro drivers

**File:** `projects/21-market-pulse-signals.py`  
**Schedule:** Daily (configurable time, currently no schedule)  
**RSS Feeds:** 11 sources (Reuters, WSJ, MarketWatch, Yahoo Finance, Seeking Alpha, ZeroHedge, + 5 Google News targets)

#### **Setup**
```bash
# Requires: GEMINI_API_KEY, TELEGRAM_TOKEN, CHAT_ID in .env

# Run manually
python projects/21-market-pulse-signals.py
```

**RSS Feed Sources:**
1. Reuters Business - Institutional breaking news
2. WSJ Markets - Wall Street Journal (paywalled)
3. MarketWatch - Dow Jones financial news
4. Investing.com - Broker/analyst perspective
5. Yahoo Finance - Market data + news
6. Seeking Alpha - Retail + professional commentary
7. ZeroHedge - Contrarian/bearish viewpoint
8-11. Google News - Targeted searches (Market, S&P 500, Fed, Earnings)

#### **Features**
- **Deduplication:** Removes duplicate headlines (case-insensitive)
- **Headline Cap:** Limits to 25 headlines to avoid overwhelming Gemini
- **Structured Output:**
  - Overall sentiment (bullish/bearish/neutral)
  - Macro driver (main story of the day)
  - High-impact items (5 max) with direction (up/down/mixed)
  - Top tickers (6 max) with sentiment
- **JSON Cleaning:** Strips markdown fences and backticks from Gemini responses
- **Error Handling:** Gracefully handles missing feeds and JSON parse errors

#### **Output Example**
```
🚀 Your Daily Market Tea ☕
_December 30, 2025 at 04:00 PM_

📈 Structured read: BULLISH
🌐 Macro: Fed rate cuts expected in 2026; tech earnings in focus

🔥 High-impact moves:
- 🟢⬆️ (high) Fed Policy Shift - Expects rate cuts next year
- 🟢⬆️ (high) AI Sector Momentum - NVDA rallies on data center demand
- 🟡↔️ (medium) Earnings Season - Mixed results from Q4 reports

🎯 Top tickers:
- 🟢 NVDA: Strong AI fundamentals, data center boom
- 🟢 TSLA: EV demand recovery, margin expansion
- 🟡 MSFT: Copilot adoption slower than expected

[Narrative analysis from Gemini follows...]
```

#### **Configuration Options**
```python
# In projects/21-market-pulse-signals.py:
RSS_FEEDS = {
    # Add/remove feeds as needed
    "Your Source": "https://feed.url.here"
}
MIN_HEADLINES = 5  # Minimum before Gemini analysis
MAX_HEADLINES = 25  # Cap to avoid token limits
```

---

### **5. Logging & Monitoring**

#### **Log Locations**
```bash
# Watchlist updater logs
~/Developer/timeless-workspace/logs/watchlist-updates.log
~/Developer/timeless-workspace/logs/watchlist-errors.log

# Market Pulse Signal (if enabled with launchd)
~/Developer/timeless-workspace/logs/market-pulse.log
```

#### **View Real-time Logs**
```bash
# Watchlist updates
tail -f ~/Developer/timeless-workspace/logs/watchlist-updates.log

# Errors
tail -f ~/Developer/timeless-workspace/logs/watchlist-errors.log

# Count recent updates
grep "✅" ~/Developer/timeless-workspace/logs/watchlist-updates.log | wc -l
```

#### **Troubleshooting**
| Issue | Solution |
|-------|----------|
| Launchd job not running | Check `launchctl list \| grep timeless` |
| Mac sleeping at 8 PM | Job is queued; will run when Mac wakes. Disable sleep in System Prefs for reliability |
| "No headlines found" | Check RSS feed URLs; firewall may block feedparser requests |
| Gemini API errors | Verify API key in `.env`; check token balance |
| Telegram not receiving | Verify TELEGRAM_TOKEN and CHAT_ID in `.env` |
| JSON parse errors | Gemini response format changed; check `_clean_structured_json()` function |

---

### **6. Watchlist Maintenance Guide**

#### **Current Watchlist (40 stocks)**
**Updated:** December 30, 2025 via auto-updater

**Composition:**
- 9 Technology stocks (AAPL, MSFT, GOOGL, NVDA, META, ADBE, CRM, AVGO, KLAC)
- 9 Healthcare stocks (UNH, LLY, ABBV, TMO, ISRG, VRTX, JNJ, ABT, MRK)
- 9 Financial Services (JPM, BAC, GS, V, MA, BLK, COIN, C, MS)
- 4 Consumer stocks (HD, COST, NKE, SYK)
- 3 Industrials (CAT, BA, GE)
- 2 Communication (DIS, NFLX)
- 1 Utility (NEE)
- 1 Real Estate (PLD)
- 4 ETFs for benchmarking (SPY, QQQ, DIA, IWM)

#### **Manual Updates**
Edit `watchlist.json` directly:
```json
{
  "stocks": ["AAPL", "MSFT", "GOOGL", ...],
  "etfs": ["SPY", "QQQ", ...],
  "description": "Your custom description"
}
```

#### **Quality Filters**
Updater automatically filters:
- Market Cap ≥ $10B
- Avg Volume ≥ 1M shares/day
- Price ≥ $20
- Sector balance (max 35% per sector)

#### **Add Sector-Specific Watches**
Example: Add emerging AI stocks monthly
```python
# In watchlist-auto-updater.py, add to growth_candidates:
growth_candidates = [
    # ... existing ...
    'UPST',  # AI lending
    'MNDY',  # AI project management
    'RBLX',  # Metaverse/AI
]
```

---

### **7. Running Signals on Schedule**

#### **Current Scheduled Tasks**
| Signal | Schedule | Execution | Status |
|--------|----------|-----------|--------|
| Watchlist Auto-Updater | Sun 8 PM | Launchd | ✅ Active |
| Sector RS Scanner | Daily 4 PM | Manual | ⏳ Needs launchd setup |
| Market Pulse News Bot | Daily (var) | Manual | ⏳ Needs launchd setup |

#### **Setting Up Launchd for Sector RS Signals**
```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.timeless.sector-rs-scanner.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.timeless.sector-rs-scanner</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/hongkiatkoh/Developer/timeless-workspace/projects/01-sector-rs-momentum-signals.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>16</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/hongkiatkoh/Developer/timeless-workspace/logs/sector-rs.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/hongkiatkoh/Developer/timeless-workspace/logs/sector-rs-errors.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.timeless.sector-rs-scanner.plist

# Verify
launchctl list | grep sector
```

---

### **8. Quick Reference**

#### **Essential Commands**
```bash
# Test all systems
python projects/01-sector-rs-momentum-signals.py
python projects/21-market-pulse-signals.py
python projects/watchlist-auto-updater.py

# Check scheduled jobs
launchctl list | grep timeless

# View recent watchlist updates
tail -20 ~/Developer/timeless-workspace/logs/watchlist-updates.log

# Manually trigger watchlist update
launchctl start com.timeless.watchlist-updater

# Edit .env
nano ~/Developer/timeless-workspace/projects/.env

# Check Python environment
source .venv/bin/activate
python --version
pip list | grep -E "(yfinance|feedparser|google|requests)"
```

#### **Directory Structure**
```
timeless-workspace/
├── README.md                          # This file
├── watchlist.json                     # Master watchlist (auto-updated)
├── requirements.txt                   # Python dependencies
├── .env                               # API keys (not in git)
├── .venv/                             # Python virtual environment
│
├── projects/                          # All trading signal scripts
│   ├── 01-sector-rs-momentum-signals.py
│   ├── 21-market-pulse-signals.py
│   ├── watchlist-auto-updater.py
│   ├── watchlist_loader.py
│   └── .env                           # Copy of main .env
│
├── scripts/                           # Bash wrappers & config
│   ├── update-watchlist.sh            # Called by launchd
│   ├── launchd-commands.txt           # Management reference
│   └── crontab-example.txt            # Legacy (use launchd instead)
│
└── logs/                              # Execution logs
    ├── watchlist-updates.log
    ├── watchlist-errors.log
    ├── sector-rs.log
    └── sector-rs-errors.log
```

---

### **9. Troubleshooting Checklist**

- [ ] Virtual environment activated? `source .venv/bin/activate`
- [ ] `.env` file exists with API keys?
- [ ] Watchlist.json is valid JSON? Test: `python -m json.tool watchlist.json`
- [ ] Launchd job loaded? `launchctl list | grep timeless`
- [ ] Check logs for errors? `tail -50 logs/watchlist-updates.log`
- [ ] Test script manually first before scheduling
- [ ] Network firewall blocking feedparser? Test with `curl`
- [ ] Telegram token valid? Test with `curl` to Telegram API
- [ ] Gemini API quota exceeded? Check gemini.google.com console

---

### **10. Future Enhancements**

- [ ] Add email notifications as backup to Telegram
- [ ] Integrate with live brokerage API for actual trading
- [ ] Add historical backtesting for RS signals
- [ ] Create dashboard for signal performance tracking
- [ ] Add SMS alerts for high-impact signals
- [ ] Implement position sizing based on Kelly Criterion
- [ ] Add portfolio rebalancing alerts
- [ ] Create weekly summary report

---

**Last Updated:** December 30, 2025  
**Maintained By:** Your Name  
**Questions?** See troubleshooting section or check logs
