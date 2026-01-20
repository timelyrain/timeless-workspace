# PROJECT CONTEXT: 15% PORTFOLIO ALGORITHMIC SYSTEM

## 1. OBJECTIVE & CONSTRAINTS
- **User Persona:** 52-year-old Full-time Trader.
- **Goal:** Consistent 15% Annual Returns.
- **Hard Constraint:** Maximum Portfolio Drawdown of 10%.
- **Capital:** $1M Active Trading
- **Risk Tolerance:** Institutional-Grade. Manipulation-resistant signals only.

## 2. THE STRATEGY (The North Star)
- **Global Strategic Core (30%):** VWRA (World), ES3 (SG Banks), DHL (Value), 82846 (China A).
- **Growth Engine (30%):** CSNDX (Nasdaq), CTEC (China Tech), HEAL (Biotech), INRA (Clean Energy), LOCK (Cyber).
- **Income Strategy (25%):** The Wheel (Selling Puts) on GOOGL, PEP, V. High IV Rank, 0.20 Delta.
- **Hedge (5%):** Long Puts on QQQ (15% OTM) + Sniper entries which are individual theme stocks
- **Reserves (10%):** Cash 7% & Gold (GSD) 3%

## 3. TECHNICAL ARCHITECTURE (The Python System)
- **Framework:** Python script monitoring 14 Institutional Signals.
- **Weights:** Credit & Liquidity (50%), Market Breadth (30%), Risk Appetite (15%), Sentiment (5%).
- **Inputs:** FRED API (Economic Data), Yahoo Finance (Market Data), CNN Fear & Greed.
- **Outputs:** 1. Daily Risk Score (0-100).
  2. Automated Telegram Alerts (Mobile Optimized).
  3. AI Analysis Summary (Daily).

## 4. CODING RULES (For AI Assistant)
- **Style:** Pythonic, modular, heavily commented for maintainability.
- **Libraries:** pandas, yfinance, fredapi, python-telegram-bot.
- **Error Handling:** Robust. The system must run on a server; if an API fails, it must retry or degrade gracefully, not crash.
- **Output:** All alerts must be formatted for iPhone screens (short, emoji-coded, clear numbers).