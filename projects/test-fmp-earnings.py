"""
Test FMP API connection and data retrieval for earnings surprises
"""
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from watchlist_loader import load_watchlist

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

FMP_API_KEY = os.getenv('FMP_API_KEY')
WATCHLIST = load_watchlist()

print("=" * 80)
print("FMP EARNINGS SURPRISES API TEST")
print("=" * 80)

if not FMP_API_KEY:
    print("\n❌ ERROR: FMP_API_KEY not found in .env file!")
    print("   Add FMP_API_KEY=your_key_here to projects/.env")
    exit(1)

print(f"\n✅ FMP API Key found: {FMP_API_KEY[:10]}...{FMP_API_KEY[-4:]}")
print(f"✅ Watchlist loaded: {len(WATCHLIST)} stocks")

# Get current quarter info
today = datetime.now()
current_year = today.year
current_quarter = (today.month - 1) // 3 + 1

print(f"\n📅 Current date: {today.strftime('%Y-%m-%d')}")
print(f"📅 Current quarter: Q{current_quarter} {current_year}")

# Test API calls
quarters_to_check = [
    (current_year, current_quarter),
    (current_year if current_quarter > 1 else current_year - 1, 
     current_quarter - 1 if current_quarter > 1 else 4)
]

print("\n" + "=" * 80)
print("TESTING FMP API CALLS")
print("=" * 80)

all_symbols = []
watchlist_matches = []

for year, quarter in quarters_to_check:
    url = f"https://financialmodelingprep.com/api/v3/earnings-surprises?year={year}&quarter=Q{quarter}&apikey={FMP_API_KEY}"
    print(f"\n🔍 Fetching Q{quarter} {year}...")
    print(f"   URL: {url[:80]}...")
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"   Status Code: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"   ❌ Error: {resp.text[:200]}")
            continue
        
        data = resp.json()
        
        if not data:
            print(f"   ⚠️  No data returned (empty response)")
            continue
        
        if not isinstance(data, list):
            print(f"   ⚠️  Unexpected format: {type(data)}")
            print(f"   Response: {str(data)[:200]}")
            continue
        
        print(f"   ✅ Received {len(data)} earnings records")
        
        # Check for watchlist matches
        quarter_matches = []
        for record in data:
            symbol = record.get('symbol')
            if symbol:
                all_symbols.append(symbol)
                if symbol in WATCHLIST:
                    quarter_matches.append(record)
        
        print(f"   📊 Watchlist matches: {len(quarter_matches)}")
        
        if quarter_matches:
            print(f"\n   Matched stocks in Q{quarter} {year}:")
            for rec in quarter_matches[:5]:  # Show first 5
                sym = rec.get('symbol')
                date = rec.get('date', 'N/A')
                actual = rec.get('actualEarningResult', 0)
                est = rec.get('estimatedEarning', 0)
                surprise = ((actual - est) / abs(est) * 100) if est != 0 else 0
                print(f"      • {sym}: {date} | Surprise: {surprise:+.1f}%")
        
        watchlist_matches.extend(quarter_matches)
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timeout after 10 seconds")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total earnings records retrieved: {len(all_symbols)}")
print(f"Unique symbols: {len(set(all_symbols))}")
print(f"Watchlist matches (all quarters): {len(watchlist_matches)}")

if watchlist_matches:
    print(f"\n✅ SUCCESS: Found {len(watchlist_matches)} watchlist stocks with earnings data")
    print("\nMatched stocks:")
    for rec in watchlist_matches:
        sym = rec.get('symbol')
        date = rec.get('date', 'N/A')
        actual = rec.get('actualEarningResult', 0)
        est = rec.get('estimatedEarning', 0)
        surprise = ((actual - est) / abs(est) * 100) if est != 0 else 0
        print(f"  {sym}: {date} | Actual: ${actual:.2f} vs Est: ${est:.2f} | Surprise: {surprise:+.1f}%")
else:
    print(f"\n⚠️  No watchlist stocks found with earnings in Q{quarters_to_check[0][1]} or Q{quarters_to_check[1][1]} {current_year}")
    print("\nPossible reasons:")
    print("  1. None of your watchlist stocks reported earnings in these quarters")
    print("  2. FMP data is delayed or incomplete for recent quarters")
    print("  3. Earnings dates fall outside the 7-day lookback window in the main script")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
