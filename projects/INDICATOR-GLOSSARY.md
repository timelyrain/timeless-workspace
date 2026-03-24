# 📊 Institutional Risk Dashboard — Indicator Glossary

> 22 indicators across 3 tiers, scored and normalized to a 0–100 risk scale.
> Data sources: FRED (Federal Reserve), Yahoo Finance, CBOE indices.

---

## TIER 1: Credit + Macro (max 39.25 pts)

Credit conditions and macro liquidity — the foundation of systemic risk. When credit breaks, everything breaks.

---

### #1 · HY Spread — High Yield Corporate Bond Spread
**Full Name:** ICE BofA US High Yield Option-Adjusted Spread (OAS)
**Source:** FRED `BAMLH0A0HYM2` · **Score Variable:** `s1` · **Max:** 20 (within credit composite)

**What it is:** The yield premium that investors demand to hold junk-rated (BB and below) corporate bonds over risk-free US Treasuries, measured in percentage points.

**How it works:** When investors are confident, they accept thin spreads (2.5–3.5%) for the extra risk. When fear rises, they dump junk bonds and spreads blow out (5%+ in stress, 10%+ in crisis like March 2020). The dashboard also applies a **30-day rate-of-change penalty** — if spreads widen 20%+ in a month, the score is penalized by 5 points to catch rapid deterioration early.

**Why it matters:** HY spreads are the single best real-time measure of credit stress. They reflect the collective judgment of thousands of institutional bond traders about corporate default risk. Credit leads equity — spreads typically widen 2–4 weeks before stock selloffs.

**Who uses it:** Every institutional credit desk, macro hedge fund, and risk management team. It's the first line on any CIO's morning risk dashboard.

**When it's useful:** Always, but especially at inflection points. Spreads tightening after a selloff = recovery signal. Spreads widening while equities rally = dangerous divergence (the "smart money" warning).

---

### #2 · IG Spread — Investment Grade Corporate Bond Spread
**Full Name:** ICE BofA US Corporate Master Option-Adjusted Spread
**Source:** FRED `BAMLC0A0CM` · **Score Variable:** `s_ig` · **Max:** 20 (within credit composite)

**What it is:** The yield premium for investment-grade (BBB and above) corporate bonds over Treasuries. Typically 0.8–1.5% in normal markets.

**How it works:** IG spreads move in the same direction as HY but with less volatility. Widening IG spreads signals that even high-quality borrowers face tighter conditions — this is more concerning than HY widening alone because it means the stress is systemic, not just limited to weak companies.

**Why it matters:** IG is the backbone of corporate America's funding. When IG spreads widen sharply, it signals that the plumbing of the financial system is under stress. In March 2020, IG spreads blew out to 4%+ and the Fed had to intervene with unprecedented corporate bond buying.

**Who uses it:** Investment-grade bond portfolio managers, corporate treasurers monitoring their borrowing costs, central banks watching financial conditions.

**When it's useful:** Most powerful as a confirmation signal. When both HY and IG are widening together, the credit market is sending a unified stress signal. IG widening without HY widening can signal rate/duration risk rather than credit risk.

---

### #3 · Credit Stress Ratio — HY/IG Spread Ratio
**Full Name:** High Yield to Investment Grade Spread Ratio
**Source:** Calculated: `HY Spread ÷ IG Spread` · **Score Variable:** `s_ratio` · **Max:** 20 (within credit composite)

**What it is:** The ratio of junk bond spreads to investment-grade spreads. Measures how much extra risk premium the market charges for credit quality deterioration.

**How it works:** In healthy markets, the ratio is 3.0–3.5× (junk pays about 3× more than IG). When it rises to 4.0–4.5×, the market is differentiating more aggressively between good and bad credits — a sign of growing selectivity and stress. Above 5× signals crisis-level discrimination.

**Why it matters:** The ratio strips out the general level of rates and isolates pure credit quality differentiation. It can rise even when absolute spreads look calm — an early warning that institutional investors are quietly rotating out of weaker names.

**Who uses it:** Credit strategists, distressed debt investors, risk managers at insurance companies and pension funds.

**When it's useful:** Especially valuable in late-cycle environments where absolute spreads may look benign (compressed by QE or yield-chasing) but the ratio reveals underlying quality stress.

---

### #4 · NFCI — Chicago Fed National Financial Conditions Index
**Full Name:** Chicago Fed National Financial Conditions Index
**Source:** FRED `NFCI` · **Score Variable:** `s_nfci` · **Max:** 15 (within credit composite)

**What it is:** A weekly composite index of 105 financial indicators spanning money markets, debt markets, equity markets, and the banking system. Constructed by the Federal Reserve Bank of Chicago. Negative values = loose/easy conditions; positive values = tight/stressed conditions.

**How it works:** The NFCI aggregates credit spreads, interbank lending rates, equity volatility, commercial paper rates, repo rates, bank lending surveys, and dozens more into a single number. It's mean-zero by construction — readings below -0.5 indicate very loose conditions, above +0.5 indicates significant tightening.

**Why it matters:** Replaced the deprecated TED Spread (LIBOR-Treasury spread) which became meaningless after LIBOR was discontinued in 2023. The NFCI is the institutional gold standard for real-time financial conditions. It captures funding stress that no single indicator can — including shadow banking, repo markets, and non-bank lending.

**Who uses it:** The Federal Reserve itself (cited in FOMC minutes), macro hedge funds, bank risk departments, sovereign wealth funds.

**When it's useful:** Most predictive during tightening cycles. A spike from negative to positive territory often precedes equity corrections by 2–6 weeks. Also useful for identifying when the Fed's tightening is "biting" the real economy.

---

### #5 · Fed BS YoY — Federal Reserve Balance Sheet Year-over-Year Change
**Full Name:** Federal Reserve Total Assets — Year-over-Year Percentage Change
**Source:** FRED `WALCL` (weekly) · **Score Variable:** `s2` · **Max:** 15

**What it is:** The annual rate of change in the Fed's total balance sheet. Positive = the Fed is expanding (QE/liquidity injection). Negative = the Fed is contracting (QT/liquidity drain).

**How it works:** The Fed's balance sheet is the most powerful liquidity driver in global markets. When the Fed buys bonds (QE), it creates bank reserves, suppresses yields, and pushes investors into risk assets. When it shrinks (QT), it reverses this process. The dashboard measures YoY% change: values above +2% indicate net expansion, below -2% indicates meaningful contraction.

**Why it matters:** "Don't fight the Fed" is the most important axiom in institutional investing. The correlation between Fed balance sheet changes and S&P 500 performance is among the strongest in finance. QT environments are headwinds; QE environments are tailwinds.

**Who uses it:** Every institutional investor. It's the macro variable that the biggest funds (Bridgewater, Citadel, Millennium) track most closely for their macro overlay.

**When it's useful:** Critical during regime transitions — when the Fed pivots from QT to QE (or vice versa), it signals a major inflection point for all risk assets. The rate of change matters more than the absolute level.

---

### #6 · DXY Trend — US Dollar Index Trend
**Full Name:** ICE US Dollar Index — 20-Day Moving Average Deviation
**Source:** Yahoo Finance `DX-Y.NYB` · **Score Variable:** `s4` · **Max:** 5

**What it is:** The percentage deviation of the US Dollar Index from its 20-day moving average. Positive = dollar strengthening above trend. Negative = dollar weakening below trend.

**How it works:** The DXY measures the dollar against a basket of 6 major currencies (EUR 57.6%, JPY 13.6%, GBP 11.9%, CAD 9.1%, SEK 4.2%, CHF 3.6%). A strengthening dollar tightens global financial conditions because most emerging market debt and commodities are dollar-denominated. The dashboard uses mean-reversion (deviation from 20dMA) rather than absolute level.

**Why it matters:** A surging dollar is a headwind for US multinationals (70%+ of S&P 500 revenue is international), emerging markets, and commodities. Dollar strength + Fed QT is the most toxic combination for risk assets.

**Who uses it:** FX traders, global macro funds, EM fund managers, commodity traders. A secondary but important signal in the risk framework.

**When it's useful:** Most impactful during dollar strength episodes (DXY > 105). Dollar weakness is generally permissive for risk assets. The combination of dollar strength + credit spread widening is an institutional red flag.

---

## TIER 2: Positioning + Institutional Flows (max 61 pts)

Market breadth, money flows, and positioning — where the rubber meets the road. Shows what investors are actually doing, not just what prices say.

---

### #7 · % Above 50MA — S&P 500 Breadth (50-Day Moving Average)
**Full Name:** Percentage of S&P 500 Stocks Trading Above Their 50-Day Moving Average
**Source:** Computed from batch `yf.download()` of 503 S&P 500 constituents · **Score Variable:** `s5` · **Max:** 12

**What it is:** The percentage of all S&P 500 stocks whose current price is above their individual 50-day (10-week) moving average. A measure of short-to-medium-term market breadth.

**How it works:** In a healthy bull market, 60–75%+ of stocks trade above their 50MA — the rally is broad-based. When it drops below 35%, most stocks are in intermediate-term downtrends even if the index is being held up by a few mega-caps. Below 20% is a breadth collapse — almost every stock is breaking down.

**Why it matters:** Breadth divergence is one of the most reliable warning signals in market history. The 2021–2022 topping process saw the S&P 500 make new highs while breadth steadily deteriorated (fewer stocks participating). When the mega-cap dam breaks, the damage is swift because there's no underlying breadth support.

**Who uses it:** Technical analysts, quantitative strategists, market timing models. Stan Weinstein's Stage Analysis and Lowry Research breadth models are institutional standards.

**When it's useful:** Extreme readings are most actionable. >75% = potentially overbought (but can persist in strong bulls). <25% = either capitulation (bottom signal) or accelerating bear (context-dependent). The dashboard correctly does NOT give an "oversold bonus" at extreme lows — 13% breadth is a market in freefall, not an opportunity.

---

### #8 · % Below 200MA — S&P 500 Breadth (200-Day Moving Average)
**Full Name:** Percentage of S&P 500 Stocks Trading Below Their 200-Day Moving Average
**Source:** Computed from batch `yf.download()` of 503 S&P 500 constituents · **Score Variable:** `s6` · **Max:** 10

**What it is:** The percentage of S&P 500 stocks in long-term downtrends (below their 200-day/40-week moving average). The inverse of the 50MA indicator — this measures structural damage.

**How it works:** The 200MA is the institutional dividing line between bull and bear for individual stocks. When >50% of the index is below their 200MA, the market is in a structural bear regardless of what the index price says. Below 25% = healthy bull market with broad long-term participation.

**Why it matters:** The 200MA captures structural trends that the 50MA misses. A stock below its 200MA has been declining for months — this isn't a dip, it's a trend change. When this indicator is elevated, recovery takes longer because so many stocks need to rebuild from damaged patterns.

**Who uses it:** Portfolio managers for regime classification (bull vs bear), trend-following CTAs, asset allocators deciding equity underweight/overweight.

**When it's useful:** Best as a regime filter. When >50% of stocks are below their 200MA, history shows that drawdown risk is 3–5× higher than normal. It's a "stay defensive" signal even if the headline index looks like it's recovering.

---

### #9 · A/D Breadth — Advance/Decline Ratio
**Full Name:** S&P 500 Advance/Decline Breadth Ratio (5-Day Average)
**Source:** Computed from batch S&P 500 daily returns · **Score Variable:** `s7` · **Max:** 5

**What it is:** The ratio of advancing (positive return) stocks to total stocks across the S&P 500, averaged over the last 5 trading days. Range: 0.0 (all declining) to 1.0 (all advancing).

**How it works:** Each day, every S&P 500 stock is classified as advancing (up) or declining (down). The 5-day average smooths daily noise. Above 0.55 = broad participation in the rally. Below 0.45 = most stocks declining even if the index is flat (mega-cap masking). Below 0.35 = capitulation-level breadth collapse.

**Why it matters:** The A/D ratio is the purest measure of market participation. Unlike moving average breadth which is lagging, A/D captures real-time buying and selling pressure across all 500 stocks. It's the first signal to detect when a rally is narrowing or a selloff is broadening.

**Who uses it:** Market internals analysts, intraday traders, institutional trading desks monitoring "under the hood" market health.

**When it's useful:** Most valuable during divergences — if SPY is up but the A/D ratio is below 0.45, the rally is fake (driven by a few names). During selloffs, A/D dropping below 0.35 consistently often marks the intense selling phase before a bottom.

---

### #10 · New H-L — New Highs Minus New Lows
**Full Name:** S&P 500 Net New 52-Week Highs Minus New 52-Week Lows
**Source:** Computed from batch S&P 500 3-month price data · **Score Variable:** `s8` · **Max:** 3

**What it is:** The count of S&P 500 stocks making new 3-month highs minus those making new 3-month lows. Positive = more stocks hitting highs. Negative = more stocks hitting lows.

**How it works:** Stocks within 0.5% of their 3-month high are counted as "new highs"; within 0.5% of their 3-month low as "new lows." In healthy markets, new highs outnumber new lows by 20+. In stressed markets, new lows dominate. Current reading of -107 (13 highs, 120 lows) signals extreme bearish breadth.

**Why it matters:** New highs/lows is a leading indicator of trend strength. A market making new index highs with shrinking new-high lists is topping. A market making new index lows with shrinking new-low lists is basing. The magnitude matters — extreme negative readings (-50+) indicate broad-based capitulation.

**Who uses it:** Market technicians, breadth analysis systems (Zweig, Lowry), trend-following models.

**When it's useful:** Best at extremes. When new lows exceed 100+ across the S&P 500, historical data shows the market is in a high-probability washout zone. As a recovery signal, when new lows start contracting from extremes (e.g., -107 → -50 → -20), it signals the selling is exhausting.

---

### #11 · Sector Rotation — Defensive vs Cyclical Basket
**Full Name:** Defensive/Cyclical Sector Rotation Trend (3v3 Basket)
**Source:** Yahoo Finance batch download · **Score Variable:** `s9` · **Max:** 6

**Basket Composition:**
- **Cyclicals:** XLY (Consumer Discretionary), XLF (Financials), XLI (Industrials)
- **Defensives:** XLU (Utilities), XLP (Consumer Staples), XLV (Healthcare)

**What it is:** The percentage deviation of the Defensive/Cyclical basket ratio from its 20-day moving average. Positive = defensives outperforming (risk-off rotation). Negative = cyclicals outperforming (risk-on rotation).

**How it works:** Equal-weight normalized baskets eliminate single-sector noise. Both baskets are indexed to day-0 = 1.0, then the defensive/cyclical ratio is tracked. When money flows from cyclicals to defensives, the ratio rises — a classic risk-off signal. The 20-day MA provides a trend baseline.

**Why it matters:** Sector rotation is the institutional language of risk appetite. When pension funds and endowments rotate from consumer discretionary/financials into utilities/staples/healthcare, they're positioning for a downturn. This is "what smart money does" before it shows up in headline indices.

**Who uses it:** Asset allocators, sector rotation strategies, institutional equity strategists (Goldman, JPM, Morgan Stanley sector models).

**When it's useful:** Most predictive during transitions. A persistent shift toward defensives (2–3 weeks) often precedes broader market weakness by 1–2 weeks. Also useful to confirm that a selloff is "real" (institutional rotation) vs "technical" (algorithmic/short-term).

---

### #12 · Gold/SPY — Gold-to-S&P 500 Ratio
**Full Name:** GLD/SPY Price Ratio Trend vs 20-Day Moving Average
**Source:** Yahoo Finance `GLD`, `SPY` · **Score Variable:** `s10` · **Max:** 4

**What it is:** The percentage deviation of the Gold/SPY price ratio from its 20-day moving average. Positive = gold outperforming (risk-off/uncertainty). Negative = SPY outperforming (risk-on).

**How it works:** Gold is the ultimate safe-haven asset. When the GLD/SPY ratio rises, investors are choosing the safety of gold over equities — a fear signal. The dashboard includes a **VIX regime check**: when VIX > 25 and gold is lagging SPY (ratio falling), the bullish read is capped at 2/4 because gold lagging during high volatility typically indicates forced liquidation (margin calls), not genuine risk-on appetite.

**Why it matters:** The gold/equity ratio captures a different dimension of risk than credit or volatility. It reflects geopolitical risk, currency debasement fear, and structural uncertainty that other indicators may miss. Gold outperformance during equity rallies is a warning that "something is off."

**Who uses it:** Macro investors, gold bugs, multi-asset portfolio managers, sovereign wealth funds. Ray Dalio's All Weather portfolio uses gold as a core risk-parity component.

**When it's useful:** Most powerful during regime uncertainty — stagflation scares, geopolitical crises, or Fed policy confusion. The VIX regime check makes it especially useful during crash dynamics where naive gold/equity signals can be misleading.

---

### #13 · ETF Flows — Institutional Money Flow Divergence
**Full Name:** 9-ETF Institutional Flow Divergence (Volume Surge + Price Momentum)
**Source:** Yahoo Finance batch download · **Score Variable:** `s18` · **Max:** 8

**Tracked ETFs:** SPY, QQQ, IWM, DIA (equity), EEM (emerging), TLT (bonds), GLD (gold), HYG, LQD (credit)

**What it is:** Counts the number of major ETFs experiencing simultaneous volume surges (5-day avg > 20-day avg by 10%+) with directional price moves (positive = inflow, negative = outflow).

**How it works:** When institutional investors make large allocation shifts, it shows up as abnormal volume combined with directional price pressure. If 7+ ETFs show outflows simultaneously, it signals coordinated risk reduction across all asset classes — a rare and dangerous signal. 7+ inflows signal coordinated risk-on.

**Why it matters:** Individual ETF flows can be noisy, but when multiple ETFs across different asset classes (equity, bonds, gold, credit) all show the same directional flow, it's a powerful signal of institutional herding. This is the closest proxy for actual fund flow data without a Bloomberg terminal.

**Who uses it:** ETF market makers, institutional equity traders, macro fund managers monitoring cross-asset flows.

**When it's useful:** Strongest at extremes. 7+ coordinated outflows = panic selling across all asset classes (very rare, very bearish). During normal markets, mixed readings (some in, some out) reflect healthy rebalancing. The transition from mixed to one-sided is the key signal.

---

### #14 · Credit Flows — Credit Market Flow Stress
**Full Name:** Credit ETF Flow Stress Monitor (4 Credit ETFs)
**Source:** Yahoo Finance batch download · **Score Variable:** `s19` · **Max:** 7

**Tracked ETFs:** HYG (High Yield), LQD (Investment Grade), JNK (High Yield), EMB (Emerging Market Debt)

**What it is:** Monitors volume surges (8%+ above 20-day average) combined with directional price moves (0.5%+) across 4 major credit ETFs to detect credit-specific flow stress.

**How it works:** Credit ETFs have lower volatility than equity ETFs, so the detection thresholds are calibrated lower (8% vol / 0.5% price vs 10% / 0% for equity ETFs). When 2+ credit ETFs show simultaneous outflows, it signals institutional credit redemption — bond funds facing withdrawals, which forces them to sell holdings into a declining market (a feedback loop).

**Why it matters:** Credit flows lead equity flows by 1–2 weeks. When HYG/LQD/JNK are all seeing outflows, the credit market is pricing in deterioration that equity markets haven't fully recognized yet. The 2015, 2018, and 2020 equity selloffs were all preceded by credit ETF outflows.

**Who uses it:** Fixed income portfolio managers, credit hedge funds, cross-asset strategists. Jeff Gundlach (DoubleLine) famously watches credit flows as a leading indicator.

**When it's useful:** Most valuable as an early warning system. Credit flows turning negative while equities are still holding up = the "smart money" is leaving. All 4 ETFs in outflow simultaneously is a rare but powerful sell signal.

---

### #15 · Sector Rotation Strength — 11-Sector Momentum Dispersion
**Full Name:** S&P 500 Sector Momentum Dispersion (Top 3 vs Bottom 3 Spread)
**Source:** Yahoo Finance batch download of 11 SPDR sector ETFs · **Score Variable:** `s20` · **Max:** 6

**Tracked Sectors:** XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC

**What it is:** The 10-day price momentum spread between the best-performing 3 sectors and worst-performing 3 sectors. Measures how aggressively capital is rotating between sectors.

**How it works:** Each of the 11 S&P sectors' 10-day price return is calculated. The top 3 are averaged and the bottom 3 are averaged. A wide spread (>20%) = healthy rotation where capital is actively flowing between sectors (leadership emerging). A narrow spread (<10%) = correlated selling (panic) or correlated buying (complacent).

**Why it matters:** In healthy markets, sector rotation is the engine of price discovery — money leaving overvalued sectors and flowing into undervalued ones. When all sectors move together (narrow spread), it signals either panic (everything down) or bubble (everything up). Both are unhealthy.

**Who uses it:** Quantitative sector rotation strategies, tactical asset allocators, market regime classifiers.

**When it's useful:** Most useful as a regime confirmation tool. Rotation spread >20 during an uptrend = healthy bull continuation. Spread <5 during a downtrend = correlated panic selling (potential capitulation). Narrowing spread during a rally = late-cycle warning (breadth exhaustion).

---

## TIER 3: Options Intelligence + Structure (max 46 pts)

Volatility complex and structural indicators — what the options market and yield curve say about forward expectations.

---

### #16 · VIX Term Structure — Volatility Futures Curve Shape
**Full Name:** CBOE VIX vs VIX3M Term Structure Slope
**Source:** Yahoo Finance `^VIX`, `^VIX3M` · **Score Variable:** `s11` · **Max:** 15

**What it is:** The percentage difference between 3-month VIX (VIX3M) and spot VIX: `(VIX3M - VIX) / VIX × 100`. Positive = contango (normal/calm). Negative = backwardation (fear/stress).

**How it works:** In normal markets, VIX3M > VIX (contango) because uncertainty is higher further out. When spot VIX spikes above VIX3M (backwardation), it means near-term fear exceeds long-term uncertainty — the market is pricing an imminent crisis. The slope is the most predictive single vol signal: >15% contango = calm/complacent, 5–15% = healthy, -5% to +5% = uncertain, <-5% = stress/backwardation.

**Why it matters:** VIX term structure is the highest-weighted indicator in the vol complex (15/46 = 33%) because empirical research shows it's the most reliable predictor of forward equity returns. Backwardation episodes have preceded every major market drawdown since 2007. The signal typically fires 1–3 days before the worst selling.

**Who uses it:** Volatility arbitrage funds, options market makers, institutional hedging desks. It's the first thing vol traders check every morning.

**When it's useful:** Backwardation (<-5%) is the highest-conviction bearish signal in the entire dashboard. Extreme contango (>25%) can signal complacency — markets may be vulnerable to a vol shock. The transition from contango to flat is the early warning; flat to backwardation is confirmation.

---

### #17 · Yield Curve — 10-Year Minus 2-Year Treasury Spread
**Full Name:** US Treasury 10-Year Minus 2-Year Constant Maturity Spread
**Source:** FRED `T10Y2Y` · **Score Variable:** `s12` · **Max:** 3

**What it is:** The spread between the 10-year and 2-year US Treasury yields. Positive = normal upward-sloping curve. Negative = inverted (short rates exceed long rates).

**How it works:** A positive yield curve means the market expects higher rates in the future (economic growth). An inverted curve means the market expects the Fed to cut rates (recession coming). Deeply inverted (<-0.5%) has predicted every US recession since 1970 with only one false signal. The current reading of +0.51% indicates a normal, positive curve.

**Why it matters:** While yield curve inversion is a reliable recession predictor, it's a very long-lead indicator (12–18 months ahead). It's weighted modestly (3/46) because by the time it signals, faster-moving indicators (VIX, credit spreads) have already reacted. Its value is in confirming the macro backdrop.

**Who uses it:** Fixed income strategists, macro economists, recession probability models (NY Fed publishes a formal model based on this).

**When it's useful:** Inversion (going negative) is a "set your 12-month timer" signal. Steepening after inversion (going from negative back to positive) is actually the more dangerous moment — it often coincides with the recession beginning, as the Fed starts emergency cutting.

---

### #18 · VIX Level — CBOE Volatility Index
**Full Name:** CBOE Volatility Index (VIX) — "The Fear Gauge"
**Source:** Yahoo Finance `^VIX` · **Score Variable:** `s13` · **Max:** 10

**What it is:** The market's expectation of 30-day forward volatility for the S&P 500, derived from options prices. Quoted in annualized percentage points.

**How it works:** VIX below 15 = calm/complacent. 15–20 = normal. 20–25 = elevated uncertainty. 25–30 = fear. 30–35 = high fear. 35+ = panic (March 2020 peak: 82.69). The dashboard weights VIX as a confirmatory signal (10/46 = 22% of T3) rather than primary because VIX is coincident (moves with the selloff) while term structure is leading.

**Why it matters:** VIX is the most widely watched fear gauge in the world. It's used for position sizing (higher VIX = smaller positions), options pricing (all options are priced relative to implied vol), and portfolio insurance (VIX derivatives are the primary institutional hedging tool). A VIX above 25 changes the entire market microstructure — market makers widen spreads, algorithms reduce risk, and retail stops get triggered.

**Who uses it:** Everyone — from retail traders to the Federal Reserve. It's the single most recognized market indicator in the world.

**When it's useful:** VIX is most useful as a regime classifier. Below 15 = "green light" for risk-taking. Above 30 = "red light" — focus on capital preservation. The transition zones (20–25) are where most institutional decision-making happens.

---

### #19 · SKEW — CBOE SKEW Index
**Full Name:** CBOE S&P 500 SKEW Index
**Source:** Yahoo Finance `^SKEW` · **Score Variable:** `s14` · **Max:** 5

**What it is:** Measures the perceived tail risk (probability of extreme moves) in S&P 500 options. Derived from the pricing of out-of-the-money puts relative to at-the-money options. Range: ~100 (no tail risk) to 170+ (extreme tail fear).

**How it works:** The SKEW captures what VIX misses — the shape of the volatility smile, not just its level. VIX can be low (calm) while SKEW is high (institutions are quietly buying crash protection). The dashboard uses a bell-curve scoring: 120–140 is the "healthy" range where normal hedging activity occurs. Below 110 = dangerous complacency (nobody is hedging). Above 150 = extreme fear (everyone is panic-hedging).

**Why it matters:** SKEW is the "stealth fear" indicator. Before Black Monday 1987, the October 2008 crash, and the February 2018 Volmageddon, SKEW was elevated while VIX was low — institutions were buying puts without telling anyone. It's the closest the market gets to a "smart money positioning" indicator.

**Who uses it:** Options market makers, volatility surface traders, tail risk hedge funds (Universa, Nassim Taleb's fund).

**When it's useful:** Most valuable for detecting hidden risk. SKEW > 150 with VIX < 20 = institutions are buying crash insurance while the market looks calm. This divergence has preceded 5 of the last 7 >10% drawdowns. SKEW < 110 is also dangerous — it means nobody is hedging at all.

---

### #20 · VVIX — Volatility of Volatility
**Full Name:** CBOE VVIX Index (VIX of VIX)
**Source:** Yahoo Finance `^VVIX` · **Score Variable:** `s15` · **Max:** 8

**What it is:** The expected volatility of the VIX index itself — essentially, how uncertain the market is about its own fear level. Normal range: 80–100.

**How it works:** VVIX measures the uncertainty about VIX options pricing. When VVIX is below 90, vol traders are confident about the current vol regime (calm and predictable). When VVIX spikes above 115, it means nobody agrees on where vol is going — this "uncertainty about uncertainty" precedes the most violent market moves in either direction.

**Why it matters:** VVIX is a leading indicator for VIX itself. VVIX typically spikes 1–2 days before major VIX moves, giving a slight edge on timing. It's also critical for VIX options traders — high VVIX makes VIX hedges expensive, creating a "hedging trap" where protection costs spike right when you need it most.

**Who uses it:** Volatility arbitrage desks, VIX options market makers, institutional hedging strategists. It's a niche but powerful signal.

**When it's useful:** VVIX > 120 combined with VIX > 25 = the market is in crisis mode and doesn't know where the bottom is. VVIX > 120 with VIX < 20 = a vol explosion is imminent (the market senses something even though VIX hasn't moved yet). Current reading of 126.3 with VIX at 26.8 = elevated uncertainty consistent with the stressed market.

---

### #21 · VIX9D/VIX — Short-Term Fear Premium
**Full Name:** CBOE 9-Day VIX to 30-Day VIX Ratio
**Source:** Yahoo Finance `^VIX9D`, `^VIX` · **Score Variable:** `s16` · **Max:** 3

**What it is:** The percentage difference between the ultra-short-term VIX (9-day) and the standard 30-day VIX: `(VIX9D / VIX - 1) × 100`. Positive = elevated near-term event premium. Negative = near-term calm.

**How it works:** VIX9D captures the next ~2 weeks of expected volatility. When VIX9D > VIX by 5%+, options traders are pricing a specific near-term event (earnings tsunami, Fed meeting, geopolitical deadline, options expiration). When VIX9D < VIX by 5%+, near-term calm despite medium-term concern (often post-event relief).

**Why it matters:** The 9D/30D ratio isolates event-driven fear from structural fear. VIX can be elevated due to general uncertainty, but VIX9D spiking above VIX means there's a specific catalyst the market is pricing — which often means the worst of the move is concentrated in the next 1–2 weeks.

**Who uses it:** Event-driven options traders, weekly expiration specialists, earnings season strategists.

**When it's useful:** Most actionable around known catalysts — FOMC meetings, monthly options expiration (OPEX), earnings blackout periods. A VIX9D/VIX ratio > 15% has historically been associated with sharp 2–3% market moves within the following 5 trading days.

---

### #22 · VXN-VIX — Tech Volatility Spread
**Full Name:** CBOE NASDAQ-100 Volatility Index Minus CBOE S&P 500 Volatility Index
**Source:** Yahoo Finance `^VXN`, `^VIX` · **Score Variable:** `s17` · **Max:** 2

**What it is:** The absolute spread between NASDAQ-100 implied volatility (VXN) and S&P 500 implied volatility (VIX). Positive = tech is more fearful than the broad market. Negative = tech is calmer.

**How it works:** In normal markets, VXN runs 2–4 points above VIX because tech stocks are inherently more volatile. When the spread widens to 6+, it means tech is selling off harder than the broad market — often a sign of growth-stock rotation, rate-driven multiple compression, or sector-specific stress. When the spread narrows or goes negative, tech is outperforming (momentum/growth leadership).

**Why it matters:** Tech (NASDAQ-100) represents ~35% of S&P 500 market cap. When tech fear diverges significantly from broad market fear, it signals sector-specific dynamics that may or may not spread to the broader market. Tech leading the selloff is more concerning than tech lagging it.

**Who uses it:** Tech-focused portfolio managers, growth vs value rotation traders, QQQ options market makers.

**When it's useful:** Supplementary signal weighted at only 2/46 (4%) because it's sector-specific. Most useful for tech-heavy portfolios. A VXN-VIX spread > 6 combined with NASDAQ correction = tech rotation is underway. Spread compression during a selloff = tech is "catching a bid" relative to the market (potential growth bottom).

---

## Scoring Summary

| Tier | Indicators | Max Points | Purpose |
|------|-----------|-----------|---------|
| T1 | HY, IG, Ratio, NFCI, Fed BS, DXY | 39.25 | Credit health + macro liquidity |
| T2 | >50MA, <200MA, A/D, H-L, Rotation, Gold/SPY, ETF Flows, Credit Flows, Sector Strength | 61 | Market breadth + institutional positioning |
| T3 | VIX Term, Yield Curve, VIX, SKEW, VVIX, VIX9D, VXN-VIX | 46 | Options intelligence + structural |
| **Total** | **22 indicators** | **146.25 raw → normalized to /100** | |

**Regime Classification:**
| Score | Regime | Stars | Action |
|-------|--------|-------|--------|
| 90+ | ALL CLEAR | ★★★★★ | Full deployment |
| 75–90 | NORMAL | ★★★★☆ | Base allocation, tighter stops |
| 60–75 | ELEVATED | ★★★☆☆ | Cut growth, raise cash to 24% |
| 40–60 | HIGH RISK | ★★☆☆☆ | Sell aggressively, 33% cash |
| <40 | EXTREME | ★☆☆☆☆ | Liquidate to 39% cash, 25% gold |
