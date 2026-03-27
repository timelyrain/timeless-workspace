# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A production algorithmic trading system for a $1M active portfolio targeting 15% annual returns with a maximum 10% drawdown. The system runs 29 institutional trading signal generators + a master risk dashboard, all automated via GitHub Actions with Telegram alerts.

## Running Scripts

All scripts live in `projects/` and expect a `.env` file in that same directory:

```bash
# Setup (one-time)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp projects/.env.example projects/.env  # then fill in secrets

# Run individual scripts
python projects/instituitional-risk-signal.py    # Master risk dashboard
python projects/portfolio-risk-var-cvar.py       # VaR/CVaR calculator
python projects/01-sector-rs-momentum-signals.py # Individual signal (1-30)
python projects/fetch-ibkr-positions.py          # Sync IBKR positions
```

Scripts load env from `Path(__file__).parent / '.env'` via `python-dotenv`.

## Required Secrets

The `.env` file (or GitHub Secrets for Actions) must contain:
- `FRED_API_KEY` — Federal Reserve data (fred.stlouisfed.org)
- `TELEGRAM_TOKEN_RISK` — Telegram bot token (from @BotFather)
- `CHAT_ID` — Telegram channel/chat ID
- `ANTHROPIC_API_KEY` — Claude AI analysis
- `GEMINI_API_KEY` — Google AI analysis
- `IBKR_FLEX_TOKEN_HK`, `IBKR_QUERY_ID_HK` — IBKR Flex Query (positions sync)

## Architecture

### Core Data Flow

1. **Risk assessment** (`instituitional-risk-signal.py`) runs daily post-market close (6:45 PM ET via GitHub Actions), calculates a composite risk score (0–100), appends to `risk_history.json`, and sends a Telegram alert.
2. **Portfolio risk** (`portfolio-risk-var-cvar.py`) calculates VaR/CVaR per category and alerts on drift from target allocations.
3. **Signal scripts** (01–30) run 2–4× daily during market hours; each sends a Telegram alert only when signals trigger.
4. **Positions sync** (`fetch-ibkr-positions.py`) pulls live IBKR positions after close and updates the Excel dashboard.

### Risk Regime System

The master risk score drives portfolio allocation via 5 regimes:

| Regime | Score | Action | Confirmation |
|---|---|---|---|
| ALL_CLEAR | >85 | Full deployment | Immediate |
| NORMAL | 70–85 | Hold, monitor only | No action |
| ELEVATED | 55–70 | Reduce growth + income, raise cash to 24% | 3-day confirmation |
| HIGH | 40–55 | Core only, exit income, raise cash to 33% | 3-day confirmation |
| EXTREME | <40 | Maximum defense, 39% cash, 25% gold | Immediate |

3-day confirmation rule: score must remain in the new band for 3 consecutive days before triggering a regime change. Prevents whipsawing on noise. Only the two extreme bands (>85, <40) act immediately.

### Portfolio Structure (7 sleeves — single source of truth)

Defined in `projects/portfolio_categories_mappings.py`. Target allocations: global_triads=0.28, four_horsemen=0.25, cash_cow=0.25, alpha=0.05, omega=0.02, vault=0.08, war_chest=0.07.

| Sleeve | Weight | Holdings | Role |
|---|---|---|---|
| Global Triads | 28% | VWRA 75% / 82846 5% / DHL 5% / ES3 5% / XMME 10% | Strategic core — passive global beta |
| Four Horsemen | 25% | EQCH 70% / CBUK 7.5% / 9807 7.5% / INRA 7.5% / GRDU 7.5% | Growth engine |
| Cash Cow | 25% | Wheel / CSPs / CC / call options (USD) | Income strategy |
| Alpha | 5% | Theme stocks (USD) | Speculative offensive |
| Omega | 2% | SPY + QQQ bear spreads (USD) | Portfolio insurance |
| Vault | 8% | GSD 90% / AEM 10% (SGD) | Tail hedge + leveraged gold |
| War Chest | 7% | Cash (USD) | Dry powder |

### Sleeve Rationale (do not change without explicit instruction)

- **VWRA**: passive global beta — market cap tech dominance accepted, not fought
- **EQCH**: active QQQ overweight + CHF hedge — US tech outperformance thesis
- **CBUK**: China internet/tech via CQQQ + CHF hedge — China recovery thesis (not a QQQ duplicate)
- **GSD**: pure tail hedge (90%). **AEM**: leveraged gold, ring-fenced (10%) — not a hedge instrument
- **82846 / 9807**: long-term China overweight (~5% total portfolio), CAPE-based fair value thesis
- **XMME**: long-term EM exposure (~5%), unhedged for indirect USD diversification
- **INRA / GRDU**: long-term holds, no exit thesis. Rate sensitivity is a known accepted risk.

### Key Constraints

- Non-US citizen, Malaysia-based. **UCITS-domiciled ETFs only** (Ireland/Luxembourg). US estate tax threshold is $60K — no US-domiciled funds. Verify via ISIN codes in IBKR.
- CHF exposure (EQCH/CBUK) is intentional USD devaluation hedge — not redundant.
- Separate bond portfolio and real estate exist outside this system.
- Dividends from DHL and ES3 sweep automatically to IBKR cash (War Chest). No active redeployment needed — daily rebalance handles drift.
- Daily manual rebalance keeps sleeve drift <10%.

### Key Files

| File | Purpose |
|---|---|
| `projects/portfolio_categories_mappings.py` | Single source of truth: SYMBOL_MAPPING, TARGET_ALLOCATIONS, EXCHANGE_SUFFIX_MAP |
| `projects/watchlist_loader.py` | Loads `watchlist.json`, splits stocks/ETFs, used by signal scripts |
| `risk_history.json` | Daily risk score history — auto-committed by GitHub Actions |
| `watchlist.json` | Trading universe (~40 tickers) — auto-updated weekly |
| `fetch-ibkr-positions-dashboard.xlsx` | Dual-account positions + category allocation dashboard |

### Multi-Exchange Ticker Handling

`EXCHANGE_SUFFIX_MAP` in `portfolio_categories_mappings.py` maps IBKR exchange codes to yfinance suffixes (e.g., `SGX` → `.SI`, `LSEETF` → `.L`, `SEHK` → `.HK`). US exchanges map to empty string.

### GitHub Actions

36 workflows in `.github/workflows/` — one per signal script plus utilities. All follow the same pattern: checkout → Python 3.11 → pip install → create `projects/.env` from secrets → run script. The `institutional-risk-signal.yml` workflow also commits `risk_history.json` back to `main` with retry logic.

## Wheel Strategy — 3 Deployment Gates

Gate 1: IV Rank ≥ 30 (Tastytrade)
Gate 2: Dashboard score ≥ 75 (full size) / 60–75 (half size) / <60 (stand down)
Gate 3: ≥ 7 days since last trade per underlying

**Watchlist (fixed core + rotating opportunistic):**
- Mega-cap tech: AAPL, MSFT
- Quality consumer: PEP, COST
- Financials: V, JPM
- Opportunistic: 1–2 picks (highest IV rank that week from Tastytrade scan)

**Alpha trigger:** IV Rank ≥ 50 AND dashboard score ≥ 85 → deploy Alpha capital into long calls (asymmetric opportunity).

**Halt rule:** Stop all new puts if portfolio drawdown exceeds 8%. Shift Cash Cow to cash, monetize hedges.

## Risk Signal System — Scoring

- 22-indicator Python dashboard (`instituitional-risk-signal.py`)
- Tier 1 — Credit + Macro (39.25 pts): HY/IG spreads, credit stress ratio, NFCI, Fed balance sheet, DXY
- Tier 2 — Positioning + Flows (61 pts): breadth, ETF flows, sector rotation
- Tier 3 — Options + Structure (46 pts): VIX term structure, SKEW, VVIX, VIX9D, VXN
- Normalized to /100 (146.25 pts raw max — not 154, that was a stale comment now corrected)
- Daily Telegram alerts: objective data report + dual CIO analysis (Claude + Gemini)

## Code Conventions

- **Do not modify scoring logic, indicator weights, or thresholds without explicit instruction**
- Base allocation weights: global_triads=0.28, four_horsemen=0.25, cash_cow=0.25, alpha=0.05, omega=0.02, vault=0.08, war_chest=0.07
- `vix_term_struct` is the correct data key (not `vix_struct` — was a silent bug, now fixed)
- `patch_backwardation_history()` runs once on startup via guard flag — do not remove
- Bear spreads = insurance. Never sell during market stress for small profit.
- Signals prioritize credit markets and breadth over VIX alone.
- `PORTFOLIO_2026` block was intentionally removed from the script — portfolio structure lives here and in memory only.

## Workflow

- Strategy decisions are finalized in Claude.ai project first, then translated into precise Claude Code / Copilot prompts for execution.
- Every code change prompt must specify exactly what to change AND what not to touch.
- Claude.ai = thinking and documentation. Claude Code / Copilot = execution only.

## Signal Tiers

Signals 01–30 are tiered by reliability:
- **Tier 1** (01–04): Sector RS momentum, breakouts, earnings drift, insider trading (65–75% win rate)
- **Tier 2** (05–10): Mean reversion, institutional flows, sector rotation, financial health, volatility, accumulation
- **Tier 3** (11–20): Price targets, cup/handle, dark pool, options flow, buybacks, support/resistance, golden cross, ORB, gap, smart money
- **Tier 4+** (21–30): Market pulse, SPY divergence, dollar correlation, analyst ratings, IV crush, IPO momentum, short squeeze, pairs trading, correlation breakdown, liquidity

## Validation

Run monthly to validate signal quality against realized outcomes:
```bash
python projects/instituitional-risk-signal-validation-report-monthly.py
```
Uses `risk_history.json` data already collected — no extra API calls.
