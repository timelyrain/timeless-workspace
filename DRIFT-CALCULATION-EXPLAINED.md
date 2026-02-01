# Portfolio Drift Calculation Explained

## Your Current Situation (Feb 2, 2026)

### What is "38% Total Drift"?

**Total Drift = Sum of absolute differences between actual and target allocations**

```
Category              Actual   Target   Difference   Absolute
──────────────────────────────────────────────────────────────
Global Triads         29.2%    30.2%      -0.9%        0.9%
Four Horsemen         20.5%    21.1%      -0.6%        0.6%
Cash Cow              14.8%    12.6%      +2.2%        2.2%
Alpha                  1.4%     1.0%      +0.4%        0.4%
Omega (Insurance)      1.3%    10.1%      -8.8%        8.8%  ⚠️
Vault (Gold)           1.2%    10.1%      -8.9%        8.9%  ⚠️
War Chest (Cash)      31.7%    15.1%     +16.6%       16.6%  ⚠️
──────────────────────────────────────────────────────────────
TOTAL DRIFT                                          38.4%
```

**This means:**
- ✅ Your portfolio is NOT down 38%
- ✅ It means you're off target by a combined 38.4 percentage points across all categories
- ⚠️ Main issues:
  - **Omega**: Need 8.8% more insurance (SPY/QQQ options)
  - **Vault**: Need 8.9% more gold (GSD)
  - **War Chest**: Have 16.6% too much cash

---

## What is "27% from 4d ago"?

This is showing **drift trend** - how your drift has changed over time.

### Interpretation:
```
Drift 4 days ago: ~65%
Drift today:      38%
Change:           -27 percentage points
```

**This is GOOD NEWS! 📉**
- Your drift **decreased** by 27 percentage points
- You're getting closer to your target allocation
- The arrow shows improvement: 📉 (going down)

---

## Why These Target Allocations?

Your targets are **dynamically adjusted** based on risk score:

### Base Allocation (PORTFOLIO_2026):
```python
Global Triads:  30%
Four Horsemen:  30%
Cash Cow:       25%
Alpha:           2%
Omega:         2.5%
Vault:           5%
War Chest:       5%
```

### Current Risk Score: ~60-75 (ELEVATED)

When risk score is 60-75, the system automatically adjusts to:
```python
Global Triads:  30%      (unchanged - keep core)
Four Horsemen:  21%      (cut 30% from base, from 30% to 21%)
Cash Cow:       13%      (cut 50%, defensive options only)
Alpha:           1%      (cut 50%, reduce offensive)
Omega:          10%      (4x insurance! from 2.5% to 10%)
Vault:          10%      (2x gold from 5% to 10%)
War Chest:      15%      (3x cash from 5% to 15%)
```

**The system is telling you:**
- ⚠️ Risk is elevated, reduce growth exposure
- ⚠️ Increase insurance (Omega) to 10%
- ⚠️ Raise gold (Vault) to 10%
- ⚠️ You already have 31.7% cash but target is only 15%

---

## Action Items

### ❌ You're OVER-allocated:
1. **War Chest**: Have 31.7%, need 15.1% → **Sell $168k cash to deploy**

### ✅ You're UNDER-allocated:
1. **Omega**: Have 1.3%, need 10.1% → **Buy $88k SPY/QQQ puts/spreads**
2. **Vault**: Have 1.2%, need 10.1% → **Buy $89k GSD (gold)**

### 🎯 Result:
- Reduce drift from 38% to <5%
- Follow elevated risk regime guidelines
- Maintain defensive posture with proper hedges

---

## Summary

- ✅ **38% drift** = You need to rebalance 38 percentage points total
- ✅ **27% from 4d ago** = Drift improved (decreased) by 27 points
- ✅ **Not a loss** = Your portfolio value is fine, just misaligned with targets
- ⚠️ **Main fix**: Deploy excess cash into insurance (Omega) and gold (Vault)
