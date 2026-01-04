"""
Quick test script to verify yfinance data extraction for all watchlist stocks
"""
import yfinance as yf
from watchlist_loader import load_watchlist

WATCHLIST = load_watchlist()
LOOKBACK_DAYS = 252

print("=" * 80)
print("YFINANCE DATA VERIFICATION TEST")
print("=" * 80)
print(f"\nFetching {LOOKBACK_DAYS}-day data for {len(WATCHLIST)} stocks...\n")

# Download data
tickers = WATCHLIST + ['SPY']
data = yf.download(tickers, period=f"{LOOKBACK_DAYS}d", progress=False, auto_adjust=True)

print("DATA SUMMARY BY STOCK:")
print("=" * 80)

for ticker in WATCHLIST:
    try:
        close_prices = data['Close'][ticker]
        volume_data = data['Volume'][ticker]
        
        # Filter out NaN values
        valid_close = close_prices.dropna()
        valid_volume = volume_data.dropna()
        
        if len(valid_close) == 0:
            print(f"\n❌ {ticker}: NO DATA (may be delisted or invalid)")
            continue
        
        # Calculate key metrics
        current_price = valid_close.iloc[-1]
        high_52w = valid_close.max()
        low_52w = valid_close.min()
        distance_from_high = ((high_52w - current_price) / high_52w) * 100
        
        avg_volume = valid_volume.mean()
        recent_volume = valid_volume.iloc[-1] if len(valid_volume) > 0 else 0
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
        
        # Performance
        start_price = valid_close.iloc[0]
        performance = ((current_price - start_price) / start_price) * 100
        
        print(f"\n✅ {ticker}")
        print(f"   Data points: {len(valid_close)} days")
        print(f"   Current: ${current_price:.2f}")
        print(f"   52W High: ${high_52w:.2f} (distance: {distance_from_high:.2f}%)")
        print(f"   52W Low: ${low_52w:.2f}")
        print(f"   Performance: {performance:+.1f}%")
        print(f"   Avg Volume: {avg_volume:,.0f}")
        print(f"   Recent Volume: {recent_volume:,.0f} ({volume_ratio:.2f}x avg)")
        
        # Show last 5 days
        print(f"   Last 5 days:")
        for i in range(min(5, len(valid_close))):
            idx = -(i+1)
            date = valid_close.index[idx].strftime('%Y-%m-%d')
            price = valid_close.iloc[idx]
            vol = valid_volume.iloc[idx] if len(valid_volume) > abs(idx) else 0
            print(f"      {date}: ${price:.2f} | Vol: {vol:,.0f}")
        
    except Exception as e:
        print(f"\n❌ {ticker}: ERROR - {e}")

# SPY summary
print("\n" + "=" * 80)
print("BENCHMARK (SPY) DATA:")
print("=" * 80)
try:
    spy_close = data['Close']['SPY'].dropna()
    spy_current = spy_close.iloc[-1]
    spy_start = spy_close.iloc[0]
    spy_performance = ((spy_current - spy_start) / spy_start) * 100
    
    print(f"Data points: {len(spy_close)} days")
    print(f"Current: ${spy_current:.2f}")
    print(f"Performance: {spy_performance:+.1f}%")
    print(f"\nLast 5 days:")
    for i in range(min(5, len(spy_close))):
        idx = -(i+1)
        date = spy_close.index[idx].strftime('%Y-%m-%d')
        price = spy_close.iloc[idx]
        print(f"   {date}: ${price:.2f}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
