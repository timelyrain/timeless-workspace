# Options Screener Mini Project

## 🎯 Project Overview
Professional options screener similar to OptionsHawk/OptionsAlpha.

## 📊 Current Implementation (v2.0 - COMPLETE!)

### ✅ Phase 2 Features (ALL IMPLEMENTED):
1. ✅ **Unusual Activity Scanner with Greeks**
   - Detects volume > 2x open interest
   - Filters for significant volume (>100 contracts)
   - **NEW**: Full Black-Scholes Greeks (Delta, Gamma, Theta, Vega)
   - Tracks both calls and puts

2. ✅ **High IV Scanner**
   - Identifies stocks with IV > 50%
   - Finds ATM options for premium selling
   - Good for iron condors, credit spreads

3. ✅ **Cheap Options Finder**
   - Scans for options under $1.00
   - Filters for minimum liquidity
   - Shows OTM percentage

4. ✅ **Earnings Calendar Integration**
   - Auto-fetches earnings dates
   - Identifies plays within 7 days of earnings
   - Suggests strategies (IV Crush vs Straddle)
   - Alerts on high IV pre-earnings opportunities

5. ✅ **Telegram Alerts System**
   - 🚨 Unusual activity alerts (ratio > 3.0x)
   - ⚡ Extreme call/put ratio alerts
   - 📅 Earnings play alerts
   - Includes full Greeks in alerts
   - Smart deduplication (no spam)

6. ✅ **Call/Put Ratio Analysis**
   - Per-symbol sentiment analysis
   - BULLISH/BEARISH/NEUTRAL classification
   - Identifies extreme positioning
   - Market sentiment gauge

### 📈 Today's Results:
- **83 Telegram alerts sent** (unusual activity detected)
- **140 unusual options positions** identified
- **Market Sentiment**: AAPL & TSLA bullish, SPY/AMD/NVDA neutral
- **Top Alert**: AAPL $270 PUT with 1666x volume/OI ratio

### Data Source:
- **yfinance** (free): Options chain, volume, OI, IV, Greeks calculation
- Limitations: 15-min delay, adequate for EOD strategies

## 🚀 What's Next?

### ~~Phase 2 (COMPLETED ✅)~~:
- ✅ ~~Add Greeks calculator~~ - **DONE**
- ✅ ~~Earnings calendar integration~~ - **DONE**
- ✅ ~~Telegram alerts for unusual activity~~ - **DONE**
- ✅ ~~Call/Put ratio analysis~~ - **DONE**

### Phase 3 (Optional Upgrades):
- [ ] Integrate Tradier API ($10/month) for real-time data
- [ ] Or use Polygon.io ($200/month) for full flow tracking
- [ ] Or IBKR API if you have account

### Phase 4 (Advanced Features):
- [ ] Options flow tracker (track big money moves)
- [ ] Dark pool activity correlation
- [ ] Multi-leg strategy scanner (spreads, butterflies)
- [ ] Backtesting framework
- [ ] Web dashboard (Streamlit/Flask)
- [ ] Historical IV rank calculation

## 💡 Data Source Options

### Free:
- **yfinance**: ✅ Currently using, good for testing
- **CBOE**: IV data, free but need scraping

### Paid (Recommended):
- **Tradier**: $10/month sandbox, great for retail
  - Real-time options data
  - Greeks included
  - Easy API
  
- **Polygon.io**: $200/month
  - Full options flow
  - Tick-by-tick data
  - Best for serious trading

- **IBKR API**: Free with account
  - Professional-grade data
  - Need IBKR account
  - More complex to implement

### Premium:
- **Unusual Whales**: $50/month (retail data)
- **FlowAlgo**: $150/month (pro flow data)

## 🎯 Usage

### Run the scanner:
```bash
.venv/bin/python projects/31-options-screener.py
```

### Output:
- Console: Formatted tables of opportunities
- JSON: Full results saved to `options_scan_results.json`

### Customize watchlist:
Edit `WATCHLIST` in the script or pass custom symbols:
```python
scanner = OptionsScanner(symbols=['SPY', 'AAPL', 'TSLA'])
scanner.run_full_scan()
```

## 📈 Example Opportunities

**Unusual Activity Alert** (with Greeks):
```
🚨 UNUSUAL OPTIONS ACTIVITY

TSLA $450.00
CALL $500 exp 2026-02-21
Volume: 5,000 | OI: 1,200 | Ratio: 4.2x
Premium: $12.50 | IV: 65%

Greeks:
Δ 0.450 | Γ 0.00234
Θ -0.250 | ν 0.125

→ Bullish flow, potential earnings play
```

**Call/Put Ratio Alert**:
```
⚡ EXTREME CALL/PUT RATIO

AAPL - 🟢 BULLISH

C/P Ratio: 1.88
High call volume indicates bullish positioning
```

**Earnings Play**:
```
📅 EARNINGS PLAY DETECTED

NVDA
Earnings: 2026-01-28 (5 days)
IV: 72% (HIGH)

💡 Strategy: IV Crush play (sell premium)
```

**High IV Play**:
```
NVDA ATM CALL $520 exp 2026-02-07
IV: 72% (very high)
Premium: $18.50
→ Good for credit spreads or covered calls
```

**Cheap Option**:
```
AMD CALL $180 exp 2026-01-31
Premium: $0.85
OTM: +8.5%
Volume: 850
→ Lottery ticket, 10x potential
```

## 🔧 Technical Details

**Dependencies**:
- yfinance
- pandas
- python-dotenv

**Rate Limits**:
- yfinance: ~2000 requests/hour
- Be respectful, add delays for large scans

**Data Quality**:
- yfinance: 15-min delay, adequate for EOD scans
- For real-time: upgrade to Tradier or Polygon.io

## 📝 TODO

### Immediate:
- [ ] Test with current market data
- [ ] Add error handling for missing options chains
- [ ] Implement rate limiting
- [ ] Add configurable thresholds

### Soon:
- [ ] Greeks calculation (Black-Scholes)
- [ ] Earnings calendar check
- [ ] IV percentile (need historical data)
- [ ] Telegram alerts integration

### Future:
- [ ] Web dashboard (Flask/Streamlit)
- [ ] Real-time monitoring mode
- [ ] Alert system for specific criteria
- [ ] Integration with position tracker

---

**Status**: 🟢 Ready for testing
**Next Action**: Run the scanner and review results
**Upgrade Path**: Tradier API for real-time data ($10/month)
