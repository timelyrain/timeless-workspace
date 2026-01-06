import yfinance as yf

vxx = yf.Ticker('VXX').history(period='1d')['Close'].iloc[-1]
vixy = yf.Ticker('VIXY').history(period='1d')['Close'].iloc[-1]
ratio = vixy / vxx

print(f"VXX: ${vxx:.2f}")
print(f"VIXY: ${vixy:.2f}")
print(f"Ratio: {ratio:.3f}")

if ratio > 1.03:
    print("Structure: CONTANGO (normal)")
elif ratio < 0.97:
    print(f"Structure: BACKWARDATION (magnitude: {1-ratio:.1%} inversion)")
else:
    print("Structure: FLAT")