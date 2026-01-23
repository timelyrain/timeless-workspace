# Risk Signal Validation

## Overview
Lightweight walk-forward validation that analyzes your risk signal performance using data you're already collecting. **No additional API calls required.**

## What It Does
1. **Score Correlation Analysis** - Compares risk scores vs SPY forward returns (1-week, 1-month)
2. **Regime Accuracy** - Checks if regime changes (ELEVATED → HIGH RISK) preceded market drops
3. **Alert Timing** - Validates if critical alerts (HIDDEN DANGER, CREDIT WARNING) were accurate
4. **Signal Quality** - Detects whipsaws, false positives, score stability issues

## Usage

### Run Monthly Validation
```bash
cd /Users/hongkiatkoh/Desktop/timeless-workspace/timeless-workspace
.venv/bin/python projects/instituitional-risk-signal-validation-report-monthly.py
```

This generates `validation_report_YYYYMM.txt` with comprehensive analysis.

### Requirements
- Minimum **7 days** of risk_history.json data
- Internet connection (only for SPY price data on dates you already scored)

### What You Get
```
📊 SCORE vs FORWARD RETURNS CORRELATION
  • 1-week forward returns correlation: 0.650
  • High risk score (≥75): +2.3% avg return
  • Low risk score (<60): -1.8% avg return
  
🎚️ REGIME CHANGE ACCURACY
  • 2026-01-10: NORMAL → ELEVATED (Score: 64.1)
    SPY max drawdown next 21 days: -3.2%
    ✅ Correct signal

🚨 ALERT TIMING ANALYSIS
  • 2026-01-15: HIDDEN DANGER
    SPY 5-day return: -4.1%
    ✅ Good call

⚖️ SIGNAL QUALITY METRICS
  • Mean: 68.2/100
  • Std Dev: 8.3 (stable)
  • Regime changes: 2 (low whipsaw)
```

## Interpretation Guide

### Correlation Scores
- **> 0.3**: Strong predictive power ✅
- **0.0 - 0.3**: Weak but positive correlation ⚠️
- **< 0.0**: Inverse relationship (red flag!) ❌

### Regime Changes
- Look for **drawdowns following downgrades** (NORMAL → ELEVATED → HIGH RISK)
- **3%+ drop after warning = good call**
- **Market rally after warning = false positive**

### Alert Timing
- Critical alerts should precede **-2% or worse** moves within 5 days
- Too many false positives = adjust thresholds

### Signal Quality
- **Score std dev < 10**: Stable, reliable
- **Score std dev > 15**: Volatile, may need smoothing
- **Regime flips < 3**: Low whipsaw
- **Regime flips > 5**: Too sensitive, widen thresholds

## Schedule
Run this **monthly** after collecting 30+ days of data. More frequent runs won't add much value since you need forward returns to materialize.

## No Backtesting?
This is **better than traditional backtesting** because:
1. ✅ Uses real production data (no survivorship bias)
2. ✅ Walk-forward = truly out-of-sample validation
3. ✅ Catches bugs/drift in real-time
4. ✅ No overfitting risk (not optimizing thresholds)
5. ✅ Zero extra API costs

Traditional backtesting would require 500K+ API calls and still wouldn't prove future performance.

## Files
- `projects/instituitional-risk-signal-validation-report-monthly.py` - Validation script
- `risk_history.json` - Data source (auto-maintained by daily runs)
- `validation_report_YYYYMM.txt` - Monthly output
