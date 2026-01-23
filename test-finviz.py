import feedparser
import requests
from bs4 import BeautifulSoup

print("=" * 80)
print("FINVIZ NEWS - DETAILED DIAGNOSTICS")
print("=" * 80 + "\n")

# Test 1: Direct RSS parse
print("Test 1: Direct RSS Feed Parse")
print("-" * 40)
url = "https://finviz.com/news.ashx?v=rss"
print(f"URL: {url}\n")

try:
    feed = feedparser.parse(url)
    print(f"Feed parsed: {feed.bozo}")
    print(f"Entries found: {len(feed.entries)}")
    if feed.bozo:
        print(f"Parse error: {feed.bozo_exception}")
    if feed.entries:
        print(f"Sample: {feed.entries[0].title}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try with custom headers (some sites block default user agents)
print("\n\nTest 2: With Custom Headers")
print("-" * 40)
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"HTTP Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content length: {len(response.content)} bytes")
    
    # Try parsing the response
    feed = feedparser.parse(response.content)
    print(f"\nFeed parsed: Success")
    print(f"Entries found: {len(feed.entries)}")
    if feed.entries:
        print(f"Sample: {feed.entries[0].title}")
        print(f"Link: {feed.entries[0].link if hasattr(feed.entries[0], 'link') else 'N/A'}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try alternative Finviz endpoints
print("\n\nTest 3: Alternative Finviz Endpoints")
print("-" * 40)

alternatives = [
    "https://finviz.com/news.ashx",  # Without RSS parameter
    "https://finviz.com/api/news.ashx?v=rss",  # API path
    "https://www.finviz.com/news.ashx?v=rss",  # With www
]

for alt_url in alternatives:
    print(f"\nTrying: {alt_url}")
    try:
        response = requests.get(alt_url, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            print(f"  Entries: {len(feed.entries)}")
            if feed.entries:
                print(f"  ✅ WORKS! Sample: {feed.entries[0].title[:60]}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")

# Test 4: Try scraping the main news page as fallback
print("\n\nTest 4: Scrape Main News Page (Fallback Method)")
print("-" * 40)

try:
    response = requests.get("https://finviz.com/news.ashx", headers=headers, timeout=10)
    print(f"HTTP Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Finviz news items are typically in a table with class 'news-table' or similar
        news_items = soup.find_all('a', class_='tab-link-news')[:10]
        
        print(f"News items found via scraping: {len(news_items)}")
        if news_items:
            print("\nSample headlines:")
            for i, item in enumerate(news_items[:3], 1):
                print(f"  {i}. {item.get_text(strip=True)[:70]}")
            print("\n✅ Scraping method works as fallback!")
        else:
            # Try alternative selectors
            print("Trying alternative selectors...")
            all_links = soup.find_all('a')
            news_links = [a for a in all_links if 'news' in a.get('href', '').lower()][:5]
            print(f"Found {len(news_links)} potential news links")
            for link in news_links[:3]:
                print(f"  - {link.get_text(strip=True)[:60]}")
                
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
