# Institutional Risk Dashboard — 22 Indicators Glossary

A reference guide for every indicator used in the risk dashboard: what it is, why it matters, who uses it, how it works, and when it is most useful.

---

## TIER 1 — Credit + Macro (max 39.25 pts)

*Credit and macro indicators are the foundation of institutional risk management. They measure the cost and availability of capital, central bank policy, and currency stress — the forces that ultimately determine whether businesses can borrow, invest, and grow.*

---

### 1. HY Spread — High-Yield Credit Spread
**Source:** FRED `BAMLH0A0HYM2` (ICE BofA US High Yield Option-Adjusted Spread)
**Weight:** 30% of credit composite (~6% of total)

**What it is:**
The yield premium that below-investment-grade ("junk") corporate bonds pay over equivalent US Treasuries, measured in percentage points. It represents the extra return investors demand for lending to risky companies.

**How it works:**
When companies have to pay more to borrow (spread widens), it signals that lenders are nervous about defaults — a classic risk-off signal. When spreads are tight, lenders are confident, credit is flowing freely, and the economy is healthy. Measured daily by ICE BofA from hundreds of actual bond prices.

**Why it matters:**
HY spread is one of the most forward-looking indicators in finance. Corporate bond markets react to deteriorating business conditions *before* equity markets do, because bond investors have seniority in a bankruptcy and are incentivized to get out early. A sharp widening in HY spreads has preceded every major equity selloff.

**Who uses it:**
Macro hedge funds, credit portfolio managers, risk desks at investment banks, and Fed economists all watch HY spreads daily. It is a core input in the Chicago Fed NFCI and most systematic macro strategies.

**When it is most useful:**
- **During late economic cycles** — spreads widen before recessions
- **During market stress** — rapid widening (>20% in 30 days) signals a credit event may be developing
- **As a divergence signal** — equity markets at highs but spreads widening = hidden risk building

**Scoring in this dashboard:**
`<3% = 20/20 · <4% = 16/20 (healthy) · <4.5% = 12/20 · <5.5% = 6/20 · ≥5.5% = 0/20`
A 30-day rate-of-change penalty: if spreads have widened >20%, score drops by 5 pts.

---

### 2. IG Spread — Investment-Grade Credit Spread
**Source:** FRED `BAMLC0A0CM` (ICE BofA US Corporate Option-Adjusted Spread)
**Weight:** 30% of credit composite (~6% of total)

**What it is:**
The yield premium that investment-grade corporate bonds (BBB and above) pay over US Treasuries. IG bonds are issued by large, financially stable companies — think Apple, JPMorgan, or Microsoft.

**How it works:**
Same mechanism as HY spread but for higher-quality borrowers. IG spreads are tighter (lower) because the risk of default is smaller. When IG spreads widen, it means even the strongest corporate borrowers are feeling credit stress — a much more severe signal than HY widening alone.

**Why it matters:**
IG credit markets are the plumbing of the financial system. Pension funds, insurance companies, and sovereign wealth funds all hold IG bonds as "safe" assets. When IG spreads blow out (as they did in March 2020), it signals systemic stress — forced selling, liquidity crises, or loss of confidence in the financial system itself.

**Who uses it:**
Fixed income portfolio managers, central bankers, risk parity funds, and macro strategists. Warren Buffett famously watches credit spreads as a "fear gauge" more reliable than equity volatility.

**When it is most useful:**
- **As a confirmation of HY stress** — if HY spreads widen but IG holds tight, it is company-specific; if both widen, it is systemic
- **During rate hike cycles** — IG spreads can widen as refinancing costs rise
- **In liquidity crises** — IG spreads spike dramatically (2008: 600 bps, 2020: 380 bps)

**Scoring in this dashboard:**
`<1.2% = 20/20 · <1.5% = 16/20 · <2.0% = 12/20 · <2.5% = 6/20 · ≥2.5% = 0/20`

---

### 3. Credit Stress Ratio (HY/IG)
**Source:** Computed from FRED `BAMLH0A0HYM2` ÷ `BAMLC0A0CM`
**Weight:** 25% of credit composite (~5% of total)

**What it is:**
The ratio of the HY spread to the IG spread. It measures how much *more* risky borrowers are being charged relative to safe borrowers — a pure measure of risk discrimination in the credit market.

**How it works:**
In normal markets, the ratio sits in the 3.5–4.0 range: risky companies pay roughly 3.5–4x the premium that safe companies pay. When the ratio spikes (>4.5), lenders are discriminating sharply against risky borrowers — a sign of credit tightening and potential economic slowdown. When the ratio compresses below 3.0, lenders are not charging enough for risk — a sign of complacency.

**Why it matters:**
Looking at either HY or IG in isolation misses the relationship between them. A 5% HY spread in a world where IG spreads are also 2% (ratio = 2.5) is very different from a 5% HY spread when IG is 0.8% (ratio = 6.25). The ratio captures the *structure* of credit risk pricing, not just the absolute level.

**Who uses it:**
Credit strategists at investment banks, distressed debt hedge funds, and systematic macro funds use this ratio to identify regime shifts in credit conditions.

**When it is most useful:**
- **Identifying credit cycle turning points** — ratio rising = tightening conditions ahead
- **Separating idiosyncratic vs systemic risk** — rising HY/IG ratio = broad credit stress, not just one sector
- **Pre-recession signals** — the ratio typically starts rising 6–12 months before a recession

**Scoring in this dashboard:**
`<3.0 = 20/20 · <3.5 = 16/20 (tight, healthy) · <4.0 = 12/20 (normal) · <4.5 = 6/20 (elevated) · <5.0 = 2/20 · ≥5.0 = 0/20 (stress)`

---

### 4. NFCI — National Financial Conditions Index
**Source:** FRED `NFCI` (Chicago Federal Reserve)
**Weight:** 15% of credit composite (~3% of total)

**What it is:**
A weekly composite index of 105 measures of US financial conditions, spanning money markets, debt and equity markets, and the traditional and shadow banking systems. Negative values = looser-than-average conditions; positive values = tighter-than-average conditions.

**How it works:**
The Chicago Fed combines over 100 variables — including interest rate spreads, equity volatility, leverage ratios, and bank lending standards — into a single z-score relative to historical averages. It is not a prediction; it is a real-time snapshot of how easy or difficult it is for businesses and consumers to access capital.

**Why it matters:**
The NFCI replaced the TED Spread (LIBOR-based, deprecated 2023) in this dashboard because it is far more comprehensive. The TED Spread measured only one dimension of funding stress; NFCI measures all of them simultaneously. The Federal Reserve uses this index to assess whether monetary policy is achieving its intended effect on the economy.

**Who uses it:**
The Chicago Federal Reserve publishes it. Used by Fed economists, macro hedge funds, academic researchers, and policy analysts. It is the institutional gold standard for financial conditions monitoring.

**When it is most useful:**
- **During rate hike cycles** — NFCI shows when policy is actually tightening conditions (lagged effect)
- **In early stress periods** — NFCI will often turn positive before a full market crisis
- **For confirming macro regime** — sustained negative NFCI = abundant liquidity = supports risk assets

**Scoring in this dashboard:**
`< -0.5 = 15/15 · < -0.25 = 12/15 · <0 = 8/15 · <0.25 = 4/15 · <0.5 = 2/15 · ≥0.5 = 0/15`

---

### 5. Fed Balance Sheet YoY — Federal Reserve Assets Year-Over-Year
**Source:** FRED `WALCL` (Federal Reserve Total Assets)
**Weight:** 15 pts (direct, ~10% of total)

**What it is:**
The year-over-year percentage change in the total size of the Federal Reserve's balance sheet — the sum of all assets the Fed holds, primarily US Treasuries and mortgage-backed securities.

**How it works:**
When the Fed buys assets (Quantitative Easing / QE), it injects money into the financial system, expanding liquidity, suppressing yields, and inflating asset prices. When it sells assets or lets them mature (Quantitative Tightening / QT), it withdraws liquidity — the reverse effect. This is monitored weekly via WALCL.

**Why it matters:**
The Fed balance sheet is the primary tool of modern monetary policy beyond interest rates. The 2020 expansion from $4T to $9T directly fuelled the equity rally that followed. The subsequent QT starting in 2022 contributed to the bear market. Tracking YoY growth tells you whether central bank liquidity is a headwind or tailwind.

**Who uses it:**
Every institutional macro investor watches Fed balance sheet trends. Global macro hedge funds, sovereign wealth funds, and multi-asset allocators all adjust exposures based on QE/QT cycles.

**When it is most useful:**
- **During monetary policy regime changes** — spotting the shift from QE to QT is critical for asset allocation
- **In low-growth environments** — QE matters more when organic economic growth is weak
- **For equity premium forecasting** — the "Fed put" is most powerful when the balance sheet is expanding

**Scoring in this dashboard:**
`< -10% = 4/15 (heavy QT) · < -2% = 9/15 · <2% = 12/15 · <10% = 15/15 · ≥10% = 15/15 (QE)`

---

### 6. DXY Trend — US Dollar Index 20-Day Trend
**Source:** Yahoo Finance `DX-Y.NYB` (ICE US Dollar Index)
**Weight:** 5 pts (direct, ~3% of total)

**What it is:**
The percentage deviation of the US Dollar Index from its 20-day moving average. The DXY measures the dollar against a basket of six major currencies (EUR 57.6%, JPY 13.6%, GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%).

**How it works:**
The 20-day MA deviation captures whether the dollar is in a short-term uptrend (strengthening) or downtrend (weakening) relative to recent history. A rising dollar is typically bearish for risk assets: it tightens financial conditions globally, pressures emerging markets, reduces US corporate earnings from overseas, and signals risk-off sentiment.

**Why it matters:**
The dollar is the world's reserve currency. When it strengthens, it effectively tightens global monetary conditions — even if the Fed hasn't raised rates. Dollar strength drains liquidity from emerging markets (they must repay dollar-denominated debt with more of their local currency), squeezes US multinationals' foreign earnings, and signals that global investors are seeking safety in USD assets.

**Who uses it:**
Global macro funds, FX traders, emerging market investors, and multinational corporate treasurers all track DXY trends closely. George Soros and Stanley Druckenmiller built careers partly on dollar trend trading.

**When it is most useful:**
- **During risk-off events** — a surging dollar amplifies global stress
- **For emerging market exposure** — dollar strength = EM headwind
- **As a contrarian signal** — extreme dollar strength (>3% above 20dMA) often reverses

**Scoring in this dashboard:**
`< -3% = 5/5 (weak dollar, bullish) · < -1% = 4/5 · <1% = 3/5 · <3% = 1/5 · ≥3% = 0/5 (strong dollar, bearish)`

---

## TIER 2 — Positioning + Institutional Flows (max 61 pts)

*Positioning indicators measure the actual state of the equity market — what proportion of stocks are in uptrends vs downtrends, whether market breadth is broad or narrow, and where institutional capital is flowing. These are the real-time pulse of market health.*

---

### 7. % Stocks Above 50-Day MA — S&P 500 Short-Term Breadth
**Source:** Computed from batch Yahoo Finance download (503 S&P 500 stocks)
**Weight:** 12 pts (direct, ~8% of total)

**What it is:**
The percentage of S&P 500 stocks whose current price is above their 50-day moving average. A pure breadth indicator showing how many stocks are in short-term uptrends.

**How it works:**
Each of the 503 S&P 500 stocks is compared to its own 50-day MA. The percentage above gives a market-wide breadth reading. Calculated via a single batch download of all 500+ stocks — no survivorship bias, complete picture of the index.

**Why it matters:**
A market can rise due to a handful of mega-cap stocks dragging the index higher while most stocks are falling — a phenomenon called "narrow leadership." This indicator exposes that. When <30% of stocks are above their 50dMA during an apparent market high, it is a major divergence warning. When >75% are above, it signals broad participation and a healthy bull market.

**Who uses it:**
Breadth analysis is used by technical analysts, quantitative portfolio managers, and market strategists. Ned Davis Research, Lowry's Reports, and Dorsey Wright are famous breadth research firms. The indicator is a core tool in Intermarket Analysis.

**When it is most useful:**
- **Detecting "stealth bear markets"** — index at highs but breadth collapsing = dangerous divergence
- **Identifying regime change** — dropping below 40% signals broad deterioration
- **Confirming rallies** — a rally on narrow breadth (<50%) is less reliable than one on broad breadth (>65%)

**Scoring in this dashboard:**
`<20% = 0/12 · <35% = 2/12 · <45% = 4/12 · <55% = 7/12 · <65% = 10/12 · <75% = 12/12`

---

### 8. % Stocks Below 200-Day MA — S&P 500 Long-Term Breadth
**Source:** Computed from batch Yahoo Finance download (503 S&P 500 stocks)
**Weight:** 10 pts (direct, ~7% of total)

**What it is:**
The percentage of S&P 500 stocks trading *below* their 200-day moving average — the traditional line between bull and bear territory for individual stocks.

**How it works:**
The 200-day MA is the most widely-watched long-term trend indicator. A stock above its 200dMA is in a structural uptrend; below it is in a structural downtrend. This indicator counts how many S&P 500 stocks are in structural downtrends, giving a precise bear market breadth reading.

**Why it matters:**
The 200dMA divides bull from bear at the individual stock level. When >50% of the S&P 500 is below its 200dMA, the market is in a statistical bear market even if the index hasn't officially declined 20% yet — because the average stock already has. This indicator is more honest than headline index performance.

**Who uses it:**
Systematic quant funds use this as a "risk-off" trigger for reducing equity exposure. Stan Druckenmiller and other macro investors use it to assess the "texture" of the market. It is a key input in many factor-based allocation models.

**When it is most useful:**
- **Confirming bear markets** — >60% below 200dMA = structural bear, not just a correction
- **Identifying recovery** — the % dropping from 60% back toward 30% signals a new bull market forming
- **Risk management** — rising from 25% to 40% rapidly = warning sign for portfolio protection

**Scoring in this dashboard:**
`>65% = 1/10 · >50% = 3/10 · >35% = 6/10 · >25% = 8/10 · ≤25% = 10/10`

---

### 9. A/D Breadth — S&P 500 Advance/Decline Ratio
**Source:** Computed from batch Yahoo Finance download (503 S&P 500 stocks)
**Weight:** 5 pts (direct, ~3% of total)

**What it is:**
The 5-day average ratio of advancing stocks (those that closed higher than the prior day) to total stocks traded, across all 503 S&P 500 constituents. Expressed as a percentage: e.g., 44% means 44% of stocks advanced on an average day.

**How it works:**
Each trading day, every S&P 500 stock is classified as advancing (up on the day) or declining (down on the day). The ratio is averaged over 5 days to smooth daily noise. This tells you whether on balance, more stocks are going up or down — independent of the magnitude of moves.

**Why it matters:**
The A/D ratio catches what price-level indicators miss: the *participation* of the market move. An index can rise because 10 mega-cap stocks surged 3% while 490 stocks fell. The A/D ratio would reveal that: e.g., 42% advancing even though the index was up. Real healthy markets see >55% advancing on up days.

**Who uses it:**
The A/D Line (cumulative version) is one of the oldest technical indicators, dating to the 1920s. Used by Richard Wyckoff, Gerald Loeb, and still central to the work of market breadth analysts today. Any serious technical analyst monitors it daily.

**When it is most useful:**
- **Detecting distribution phases** — market rising but A/D falling = smart money selling into strength
- **Confirming bottoms** — A/D improving before price = accumulation beginning
- **Intraday risk management** — a low A/D ratio on a flat index day = underlying weakness

**Scoring in this dashboard:**
`<35% = 0/5 · <40% = 1/5 · <45% = 2/5 · <50% = 3/5 · <55% = 4/5 · ≥60% = 5/5`

---

### 10. New Highs minus New Lows — 3-Month H-L Net
**Source:** Computed from batch Yahoo Finance download (503 S&P 500 stocks)
**Weight:** 3 pts (direct, ~2% of total)

**What it is:**
The number of S&P 500 stocks making new 3-month highs minus those making new 3-month lows. A positive number means more stocks are breaking out than breaking down.

**How it works:**
Each stock's current price is compared to its highest and lowest price over the prior 63 trading days (3 months). A stock is counted as a "new high" if it is within 0.5% of its 3-month peak; a "new low" if within 0.5% of its 3-month trough. Net = Highs − Lows.

**Why it matters:**
New highs and lows are pure momentum — they tell you whether the market's leaders are accelerating (new highs expanding) or whether more stocks are breaking down than breaking out. A deeply negative H-L reading (as seen at -107 in March 2026) during a rally is a glaring warning that the rally is built on sand.

**Who uses it:**
Used by Investor's Business Daily (CANSLIM methodology), IBD-style growth investors, and systematic momentum strategies. Stan Weinstein's Stage Analysis also relies heavily on H-L data.

**When it is most useful:**
- **Bull market confirmation** — sustained positive H-L (>+20) = healthy trend
- **Bear market identification** — deeply negative H-L during a selloff = no floor in sight
- **Divergence signals** — index near highs but H-L negative = end of trend approaching

**Scoring in this dashboard:**
`< -10 = 0.5/3 · < -5 = 1/3 · <0 = 2/3 · <5 = 2.5/3 · ≥10 = 3/3`

---

### 11. Sector Rotation — Defensive vs Cyclical Basket
**Source:** Yahoo Finance ETFs: XLY, XLF, XLI (cyclical) vs XLU, XLP, XLV (defensive)
**Weight:** 6 pts (direct, ~4% of total)

**What it is:**
The trend of a defensive sector basket (Utilities + Consumer Staples + Healthcare) relative to a cyclical basket (Consumer Discretionary + Financials + Industrials), measured as the percentage deviation from the 20-day moving average of their ratio.

**How it works:**
Both baskets are equal-weight normalized to remove size bias, then divided to create a ratio. A rising ratio means defensives are outperforming cyclicals — investors are rotating into safety. A falling ratio means cyclicals are leading — investors are taking on risk. The 20-day MA deviation isolates the current trend from long-term valuation differences.

**Why it matters:**
Sector rotation is one of the oldest and most reliable signals in equity analysis. Martin Pring's "Intermarket Analysis" framework is built on the idea that capital rotates between sectors in a predictable sequence: from defensives to cyclicals in recoveries, and back to defensives before downturns. This indicator captures the current phase.

**Who uses it:**
Asset allocators, sector-rotation ETF strategies, and tactical portfolio managers. "Sector rotation" is a core discipline at institutions like Fidelity and Vanguard, and is the basis of many smart-beta factor strategies.

**When it is most useful:**
- **Late cycle warning** — defensives starting to outperform = investors positioning for slowdown
- **Recovery confirmation** — cyclicals leading defensives = economic expansion expected
- **Portfolio rotation guidance** — when to shift from growth to defensive sectors

**Scoring in this dashboard:**
`< -5% = 6/6 (cyclicals strongly leading = risk-on) · < -2% = 4/6 · <2% = 2/6 · ≥5% = 0/6 (defensives strongly leading = risk-off)`

---

### 12. Gold/SPY Ratio — Gold vs S&P 500 Relative Performance
**Source:** Yahoo Finance `GLD` and `SPY`
**Weight:** 4 pts (direct, ~3% of total)

**What it is:**
The percentage deviation of the GLD/SPY price ratio from its 20-day moving average. When gold outperforms SPY, investors are seeking safety; when SPY outperforms gold, risk appetite is dominant.

**How it works:**
GLD (SPDR Gold Shares) and SPY (SPDR S&P 500 ETF) are divided daily to create a ratio. The ratio's deviation from its 20-day MA captures the current trend in risk appetite. A rising ratio = gold outperforming = defensive positioning. A falling ratio = equities outperforming = risk-on.

**Why it matters:**
Gold and equities have an inverse relationship during stress: gold rises when investors fear inflation, deflation, currency debasement, or systemic collapse. The *relative* performance of gold vs equities is one of the cleanest real-money measures of risk appetite because both are highly liquid global assets.

**⚠️ Important caveat:** During acute selloffs with VIX >25, gold can *lag* SPY due to forced margin-call liquidation — investors selling gold to meet equity margin calls. This dashboard includes a regime check: if VIX >25 and gold is lagging by >1%, the bullish signal is capped at 2/4 to avoid false-positives.

**Who uses it:**
Global macro hedge funds, commodity trading advisors (CTAs), and risk-parity strategies like Ray Dalio's All Weather Portfolio monitor gold/equity ratios as a core allocation signal.

**When it is most useful:**
- **Inflation hedging** — gold outperforming = inflation expectations rising
- **Currency crisis** — sustained gold outperformance = dollar credibility declining
- **Safe-haven demand** — gold surging in a selloff = genuine fear; gold falling in a selloff = liquidation (different dynamic)

**Scoring in this dashboard:**
`< -5% = 4/4 (SPY crushing gold = risk-on, regime-capped to 2/4 if VIX>25) · < -1% = 3/4 · <1% = 2/4 · <5% = 1/4 · ≥+5% = 1/4 (gold surging = risk-off)`

---

### 13. ETF Flow Divergence — Institutional Money Flow (9 ETFs)
**Source:** Yahoo Finance: SPY, QQQ, IWM, DIA, EEM, TLT, GLD, HYG, LQD
**Weight:** 8 pts (direct, ~5% of total)

**What it is:**
A count of institutional ETF inflows vs outflows across 9 major ETFs spanning equities, bonds, gold, and credit. An "inflow" is detected when a 5-day average volume is >10% above its 20-day average AND price is positive; an "outflow" is the same volume surge with negative price.

**How it works:**
Volume surges on ETFs are a reliable proxy for institutional activity — retail traders don't move ETF volume materially. By requiring *both* elevated volume AND a price direction, this indicator filters out noise and identifies whether large capital is flowing into risk assets (inflow) or fleeing them (outflow). It covers risk-on ETFs (SPY, QQQ, IWM, DIA, EEM), safe havens (TLT, GLD), and credit (HYG, LQD).

**Why it matters:**
ETFs are the primary vehicle through which institutional and retail capital enters and exits the market. $6+ trillion is invested in US ETFs. When multiple major ETFs simultaneously show volume surges with price declines (outflows), it signals broad institutional de-risking — often a leading indicator of further declines.

**Who uses it:**
Institutional flow analysis is used by market makers, prime brokers, quantitative equity firms, and tactical asset allocators. Tools like Bloomberg's ETF flow tracker and State Street's "Sector Spiders" flow data serve a similar function for institutions.

**When it is most useful:**
- **Identifying capitulation** — extreme outflows across all 9 ETFs = potential selling climax
- **Confirming rallies** — inflows in equity ETFs + outflows in TLT = genuine risk-on rotation
- **Credit warning** — outflows in HYG/LQD before equity ETFs signal = credit leads equity

**Scoring in this dashboard:**
`≥7 outflows = 0/8 · ≥5 outflows = 2/8 · ≥7 inflows = 8/8 · ≥5 inflows = 6/8 · mixed = 4/8`

---

### 14. Credit Flow Stress — Credit ETF Money Flow (4 ETFs)
**Source:** Yahoo Finance: HYG, LQD, JNK, EMB
**Weight:** 7 pts (direct, ~5% of total)

**What it is:**
A count of inflows vs outflows specifically in credit market ETFs: HYG (high-yield), LQD (investment-grade), JNK (high-yield, alternative), and EMB (emerging market bonds).

**How it works:**
Credit ETFs have smaller daily price moves than equity ETFs (0.3–0.5% typical vs 1–2% for SPY). Thresholds are accordingly calibrated: 8% volume surge + 0.5% price move (versus 10% volume + positive price for equity ETFs). This makes the detector sensitive to the actual dynamics of bond markets. Credit flows *lead* equity flows by 1–2 weeks — bond investors move first.

**Why it matters:**
The bond market is 3x larger than the equity market and is dominated by sophisticated institutional investors — insurance companies, pension funds, and hedge funds. When credit ETFs show sustained outflows, it means the "smart money" in fixed income is de-risking, typically before equity markets react. The 2022 bear market was clearly telegraphed by HYG and LQD outflows months before equity indices peaked.

**Who uses it:**
Credit analysts, multi-asset portfolio managers, and macro hedge funds treat credit ETF flows as a leading indicator of equity risk. Fixed income desks at Goldman Sachs, JPMorgan, and BlackRock monitor these flows in real time.

**When it is most useful:**
- **Early warning system** — credit outflows preceding equity selloffs by 2–4 weeks
- **Confirming credit market stress** — alongside HY/IG spread widening, makes the case much stronger
- **Recovery signals** — credit inflows returning before equity ETF inflows = early sign of recovery

**Scoring in this dashboard:**
`≥2 outflows = 0/7 · 1 outflow = 2/7 · ≥3 inflows = 7/7 · ≥2 inflows = 5/7 · neutral = 3/7`

---

### 15. Sector Rotation Strength — 11-Sector Momentum Dispersion
**Source:** Yahoo Finance: XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC
**Weight:** 6 pts (direct, ~4% of total)

**What it is:**
The spread between the average 10-day momentum of the top 3 performing sectors and the bottom 3 performing sectors across all 11 GICS sectors. Measures how actively capital is rotating between sectors.

**How it works:**
Each of the 11 SPDR sector ETFs is ranked by its 10-day price return. The top 3 average minus the bottom 3 average gives the "rotation spread." A wide spread (>20 pts) means capital is moving aggressively from laggards to leaders — healthy rotation. A narrow spread means everything is moving together — either panic selling (broad decline) or complacent buying (all up together).

**Why it matters:**
Active sector rotation is a feature of healthy bull markets — capital continuously moves from overvalued sectors to undervalued ones. When rotation stops (narrow spread), it usually means the market is either in panic mode (everything down together) or in a late-cycle blow-off (everything up together, unsustainably). Rotation strength is particularly useful for identifying when a selloff is *selective* (sector-specific) vs *systemic* (everything falling equally).

**Who uses it:**
Sector rotation funds, tactical ETF managers, and quant strategists use dispersion metrics to calibrate how much active positioning is warranted vs passive indexing. It is a key input in momentum factor strategies.

**When it is most useful:**
- **Bull market health check** — wide spread = active allocation, market functioning normally
- **Crisis identification** — narrow spread in a down market = correlated selling, panic
- **Recovery confirmation** — spread widening from a narrow base = differentiation returning, recovery beginning

**Scoring in this dashboard:**
`>20 pts = 6/6 (strong rotation) · >10 pts = 4/6 · ≤10 pts = 0/6 (correlated moves)`

---

## TIER 3 — Options + Structure (max 46 pts)

*Options market indicators reveal what sophisticated, risk-aware market participants are paying to hedge their portfolios. The options market is where institutional traders express their true convictions about risk — in real money. These indicators are leading, not lagging.*

---

### 16. VIX Term Structure — VIX vs VIX3M Slope
**Source:** Yahoo Finance `^VIX` and `^VIX3M`
**Weight:** 15 pts (direct, ~10% of total) — highest weight in the dashboard

**What it is:**
The percentage difference between the 3-month VIX (VIX3M, measuring expected volatility over the next 3 months) and the spot VIX (measuring the next 30 days). When VIX3M > VIX (contango), the curve slopes up normally. When VIX > VIX3M (backwardation), near-term fear exceeds medium-term — a stress signal.

**How it works:**
`Slope = (VIX3M − VIX) / VIX × 100`
- **Strong contango (>+15%)**: VIX futures price in much more calm over 3 months than now — market expects the stress to resolve. Bullish.
- **Flat (+/- 5%)**: Uncertainty at all horizons.
- **Backwardation (< -5%)**: Near-term fear is *more severe* than 3-month fear — market is in acute stress, buyers are paying a premium for immediate protection.

**Why it matters:**
The term structure of volatility is the most predictive single indicator of market regime. Options market makers are professional risk-takers with billions of dollars at stake — when they price backwardation, they are telling you the risk is real and immediate. Studies show VIX backwardation predicts equity drawdowns with higher accuracy than VIX level alone.

**Who uses it:**
Volatility arbitrage hedge funds, options market makers, and volatility overlay managers (who systematically sell options when the curve is in steep contango). The VIX term structure is a core signal for vol-targeting strategies used by quantitative funds managing trillions in assets.

**When it is most useful:**
- **Crisis early warning** — VIX curve flipping to backwardation is one of the most reliable early crisis signals
- **Options selling timing** — steep contango = high VIX futures premium = favorable environment for options sellers
- **Regime identification** — sustained contango = risk-on regime; backwardation = risk-off regime

**Scoring in this dashboard:**
`< -5% = 0/15 (backwardation) · <5% = 5/15 (flat) · <15% = 10/15 (mild contango) · ≥15% = 15/15 (strong contango)`

---

### 17. Yield Curve (10Y−2Y) — Treasury Term Spread
**Source:** FRED `T10Y2Y` (10-Year minus 2-Year Treasury Yield)
**Weight:** 3 pts (direct, ~2% of total)

**What it is:**
The difference in yield between the 10-year US Treasury bond and the 2-year US Treasury note, in percentage points. Positive = normal upward-sloping curve. Negative = inverted curve.

**How it works:**
In a healthy economy, longer-term bonds yield more than short-term ones (investors demand a premium for tying up money longer). When short rates rise above long rates — typically because the Fed is aggressively hiking short rates — the curve "inverts." An inverted yield curve means banks earn less on loans (long-term) than they pay on deposits (short-term), which crushes bank lending and slows the economy.

**Why it matters:**
The inverted yield curve has preceded every US recession since 1955, with only one false positive. It is the most reliable recession predictor in economics, with a typical lead time of 12–24 months. The Federal Reserve itself closely monitors 10Y−2Y as a policy input. It is a long-lead indicator, not a timing tool.

**Who uses it:**
Every major bank research department, central bank, and institutional investor tracks the yield curve. It is the backbone of the Estrella-Mishkin recession probability model used by the New York Fed.

**When it is most useful:**
- **Recession forecasting** — inversion lasting >3 months has predicted every post-WWII recession
- **Bank profitability** — steep curve = banks profit, lend more, economy grows; flat/inverted = banks tighten
- **Long-term asset allocation** — yield curve signals where we are in the economic cycle

**Scoring in this dashboard:**
`< -0.5 = 0/3 · < -0.2 = 1/3 · <0.2 = 2/3 · <0.5 = 2.5/3 · ≥0.5 = 3/3 (normal curve, bullish)`

---

### 18. VIX Level — CBOE Volatility Index
**Source:** Yahoo Finance `^VIX`
**Weight:** 10 pts (direct, ~7% of total)

**What it is:**
The CBOE VIX is the market's real-time estimate of expected S&P 500 volatility over the next 30 days, expressed as an annualized percentage. Colloquially known as the "fear gauge" or "fear index."

**How it works:**
VIX is computed from the implied volatilities of S&P 500 options across multiple strikes and two near-term expiration dates. A VIX of 20 means the market expects the S&P 500 to move roughly ±1.26% per day (20/√252 × some factor). It is a real-money measure: traders paying higher premiums for options bids the VIX up.

**Why it matters:**
VIX is the most widely-watched risk indicator in the world. It is the benchmark for the entire volatility derivatives market (VIX futures, VXX, UVXY, etc.). While it is a coincident indicator rather than a leading one, it quantifies the exact price of fear in the market at this moment. VIX above 30 signals a genuine crisis; above 40 is extreme.

**Who uses it:**
Every professional investor monitors VIX. It is used by options traders for pricing, by portfolio managers for risk management, and by the Federal Reserve as one input in financial stability assessments. VIX readings above 25 often trigger institutional de-risking protocols.

**When it is most useful:**
- **Timing options selling** — high VIX = expensive options = premium sellers have edge
- **Portfolio protection calibration** — VIX tells you what insurance costs right now
- **Mean reversion trading** — VIX above 40 has historically been a strong contrarian buy signal for equities
- **Risk-on/risk-off confirmation** — VIX below 15 = complacency/risk-on; above 25 = fear/risk-off

**Scoring in this dashboard:**
`<15 = 10/10 · <20 = 7/10 · <25 = 4/10 · <30 = 2/10 · <35 = 1/10 · ≥35 = 0/10`

---

### 19. SKEW Index — CBOE S&P 500 Tail Risk Index
**Source:** Yahoo Finance `^SKEW`
**Weight:** 5 pts (direct, ~3% of total)

**What it is:**
The CBOE SKEW Index measures the implied volatility skew — the difference in implied volatility between out-of-the-money put options (crash protection) and at-the-money options. It quantifies how much extra premium investors are paying for tail-risk protection.

**How it works:**
A SKEW of 100 means put options are priced "fairly" with no tail-risk premium. Higher readings (120–150) indicate investors are paying a premium for out-of-the-money puts — hedging against a crash. Very high SKEW (>150) signals extreme tail-risk fear. Very low SKEW (<110) signals complacency — nobody is buying protection.

**Why it matters:**
SKEW captures a different dimension than VIX. VIX measures the overall *level* of fear; SKEW measures the *shape* of fear — specifically whether traders are worried about a fat-tail event (a sudden crash) rather than just elevated day-to-day volatility. Historically, SKEW spikes have preceded significant drawdowns by days to weeks.

**Who uses it:**
Options traders use SKEW to assess whether the put skew is cheap or expensive for hedging. Volatility hedge funds trade the spread between SKEW and VIX as a vol-of-vol arb. Risk managers use it to calibrate tail-risk hedging budgets.

**When it is most useful:**
- **Pre-event hedging** — SKEW rising ahead of FOMC, earnings season, or geopolitical events signals smart money is buying insurance
- **Identifying complacency** — extremely low SKEW during a quiet market = nobody is hedged = dangerous
- **Crash probability** — SKEW above 145 has historically had higher association with subsequent 5%+ S&P 500 drawdowns

**Scoring in this dashboard:**
Bell-curve scoring: `<110 = 1/5 (complacency) · <120 = 3/5 · <140 = 5/5 (healthy hedging) · <150 = 3/5 (fear) · ≥150 = 1/5 (panic)`

---

### 20. VVIX — Volatility of Volatility Index
**Source:** Yahoo Finance `^VVIX`
**Weight:** 8 pts (direct, ~5% of total)

**What it is:**
The VVIX measures the implied volatility of VIX *options* — i.e., the expected volatility of the VIX itself. While VIX measures expected S&P 500 volatility, VVIX measures expected volatility *of that volatility*.

**How it works:**
Computed the same way as VIX but applied to VIX options instead of SPX options. A VVIX of 90 means VIX itself is expected to move ±~6% per day. When VVIX spikes, it means options on VIX are being bid up aggressively — institutions are buying protection on *volatility jumping*. This is a higher-order fear signal that often *leads* VIX spikes by hours to days.

**Why it matters:**
VVIX is the leading indicator for VIX. When VVIX surges before VIX does, it signals that sophisticated volatility traders (who have better information flow than equity traders) are positioning for a volatility event. In August 2015, VVIX spiked to 180 hours before the "Flash Crash." In Q4 2018, VVIX consistently led VIX higher.

**Who uses it:**
Exclusively used by volatility professionals — VIX options traders, vol-of-vol hedge funds, and risk desks at derivatives-heavy institutions. It is one of the most technical and sophisticated indicators in this dashboard.

**When it is most useful:**
- **Pre-crisis early warning** — VVIX spiking while VIX is still calm = storm approaching
- **Vol regime identification** — sustained high VVIX (>115) = vol regime is unstable
- **Calibrating options positions** — high VVIX means VIX options themselves are expensive, making VIX calls costly to own

**Scoring in this dashboard:**
`<75 = 2/8 (dangerous complacency) · <90 = 8/8 (calm, bullish) · <100 = 6/8 (normal) · <115 = 3/8 (elevated) · ≥115 = 0/8 (extreme uncertainty)`

---

### 21. VIX9D/VIX Ratio — Near-Term Event Risk Premium
**Source:** Yahoo Finance `^VIX9D` and `^VIX`
**Weight:** 3 pts (direct, ~2% of total)

**What it is:**
The percentage premium or discount of the 9-day VIX (VIX9D, measuring expected S&P 500 volatility over the next 9 days) relative to the standard 30-day VIX. Measures near-term event risk specifically.

**How it works:**
`VIX9D/VIX Ratio = (VIX9D / VIX − 1) × 100`
When VIX9D > VIX (positive ratio), traders are paying more for very near-term options than medium-term ones — this indicates a specific near-term event is feared (an FOMC meeting, CPI report, earnings season, or geopolitical catalyst). When VIX9D < VIX (negative ratio), the near term is expected to be calmer than the medium term.

**Why it matters:**
The VIX9D was introduced by CBOE specifically because 30-day VIX misses very near-term event risk. If the Fed announces a surprise rate decision in 7 days, VIX9D will reflect that cost immediately while VIX30 dilutes it across 30 days. This makes VIX9D/VIX a specific detector for "known unknowns" — scheduled risk events.

**Who uses it:**
Event-driven options traders, earnings volatility traders, and macro event risk desks use VIX9D to price the specific event premium. It is also used by systematic volatility sellers who want to know whether near-term options are unusually expensive before selling them.

**When it is most useful:**
- **Pre-event positioning** — high ratio before FOMC/CPI = market pricing in a surprise
- **Post-event relief** — ratio collapses after the event = "vol crush" opportunity
- **Identifying event-driven selloffs** — if VIX9D is high but VIX3M is not, the fear is time-limited

**Scoring in this dashboard:**
`>15% = 0/3 (extreme near-term fear) · >5% = 1/3 · >-5% = 3/3 (normal) · ≤-5% = 2/3 (calm near term)`

---

### 22. VXN−VIX Spread — NASDAQ vs S&P 500 Volatility Premium
**Source:** Yahoo Finance `^VXN` and `^VIX`
**Weight:** 2 pts (direct, ~1% of total)

**What it is:**
The absolute difference between VXN (CBOE NASDAQ-100 Volatility Index, measuring expected QQQ volatility) and VIX (S&P 500 volatility). Measures whether tech-heavy NASDAQ is experiencing more fear than the broader market.

**How it works:**
`Spread = VXN − VIX`
VXN is almost always higher than VIX because NASDAQ-100 is more concentrated in high-beta tech stocks, which are inherently more volatile. A "normal" spread is around +3 to +5 points. A very high spread (>6) means tech-specific fear is elevated far beyond market-wide fear — often indicating a tech-specific risk (regulatory, valuation correction, rate sensitivity). A negative spread (rare) means broad market fear exceeds tech fear — unusual and worth noting.

**Why it matters:**
Because tech stocks (NVDA, MSFT, AAPL, META, GOOGL, AMZN) now represent >30% of the S&P 500, tech-specific volatility has an outsized impact on index performance. Monitoring VXN vs VIX separates tech-driven risk from broader market risk, which helps in making sector allocation decisions — particularly whether to hedge tech holdings specifically.

**Who uses it:**
Technology sector investors, QQQ/NASDAQ traders, and sector-specific options traders use the VXN-VIX spread as a signal for tech sector hedging. It is particularly relevant for growth-oriented portfolios with heavy tech exposure.

**When it is most useful:**
- **Tech rotation signals** — widening VXN-VIX spread = specific tech selling pressure, not broad market
- **NASDAQ hedging calibration** — high spread = QQQ puts expensive, but may be warranted
- **Identifying tech-led selloffs** — spread widening *before* VIX rising = tech is leading the decline

**Scoring in this dashboard:**
`>6 = 0/2 (extreme tech fear) · >3 = 0.5/2 (elevated) · >-2 = 2/2 (balanced, healthy) · ≤-2 = 1/2 (tech complacency)`

---

## Quick Reference: All 22 Indicators

| # | Short Name | Full Name | Source | Tier | Max Pts |
|---|---|---|---|---|---|
| 1 | HY Spread | High-Yield Credit Spread | FRED BAMLH0A0HYM2 | T1 | 20 (×30%) |
| 2 | IG Spread | Investment-Grade Credit Spread | FRED BAMLC0A0CM | T1 | 20 (×30%) |
| 3 | Credit Ratio | HY/IG Credit Stress Ratio | Computed | T1 | 20 (×25%) |
| 4 | NFCI | National Financial Conditions Index | FRED NFCI | T1 | 15 (×15%) |
| 5 | Fed BS | Fed Balance Sheet YoY | FRED WALCL | T1 | 15 |
| 6 | DXY | US Dollar Index Trend | YF DX-Y.NYB | T1 | 5 |
| 7 | >50MA | % Stocks Above 50-Day MA | YF batch 503 stocks | T2 | 12 |
| 8 | <200MA | % Stocks Below 200-Day MA | YF batch 503 stocks | T2 | 10 |
| 9 | A/D | Advance/Decline Breadth Ratio | YF batch 503 stocks | T2 | 5 |
| 10 | H-L | New Highs minus New Lows | YF batch 503 stocks | T2 | 3 |
| 11 | Sect Rot | Defensive vs Cyclical Basket | YF 6 ETFs | T2 | 6 |
| 12 | Au/SPY | Gold vs S&P 500 Ratio | YF GLD + SPY | T2 | 4 |
| 13 | ETF Flows | ETF Flow Divergence (9 ETFs) | YF 9 ETFs | T2 | 8 |
| 14 | Credit Flows | Credit ETF Flow Stress (4 ETFs) | YF 4 ETFs | T2 | 7 |
| 15 | Sect Strength | Sector Rotation Strength (11 sectors) | YF 11 ETFs | T2 | 6 |
| 16 | VIX Term | VIX Term Structure Slope | YF ^VIX + ^VIX3M | T3 | 15 |
| 17 | Yield Curve | 10Y−2Y Treasury Spread | FRED T10Y2Y | T3 | 3 |
| 18 | VIX | CBOE Volatility Index Level | YF ^VIX | T3 | 10 |
| 19 | SKEW | CBOE S&P 500 Tail Risk Index | YF ^SKEW | T3 | 5 |
| 20 | VVIX | Volatility of VIX | YF ^VVIX | T3 | 8 |
| 21 | VIX9D | VIX9D/VIX Near-Term Risk Ratio | YF ^VIX9D + ^VIX | T3 | 3 |
| 22 | VXN−VIX | NASDAQ vs S&P 500 Vol Spread | YF ^VXN + ^VIX | T3 | 2 |

**Total raw max: 146.25 pts → normalised to /100**

---

*Data sources: FRED (Federal Reserve Economic Data), Yahoo Finance. All indicators are free public data. Last updated: March 2026.*
