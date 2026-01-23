import feedparser
import requests
from datetime import datetime

# Test all potential RSS feeds
TEST_FEEDS = {
    # Current feeds
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    "ZeroHedge": "https://feeds.feedburner.com/zerohedge/feed",
    
    # New premium sources to test
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    "Bloomberg Politics": "https://www.bloomberg.com/politics/feeds/site.xml",
    "Financial Times Markets": "https://www.ft.com/markets?format=rss",
    "CNBC Breaking": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNBC Top News": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "Barron's": "https://feeds.barrons.com/barrons/topstories",
    
    # Specialized trading sources
    "Benzinga": "https://www.benzinga.com/feed",
    "The Fly": "https://thefly.com/news.php?rss",
    "Finviz News": "https://finviz.com/news.ashx?v=rss",
    
    # Institutional/Government
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "SEC News": "https://www.sec.gov/news/pressreleases.rss",
    "Treasury": "https://home.treasury.gov/rss/press-releases",
    
    # Options focused
    "CBOE News": "https://www.cboe.com/rss/news_feed/",
    
    # International
    "FT Global Economy": "https://www.ft.com/global-economy?format=rss",
    "Reuters World": "https://feeds.reuters.com/reuters/worldNews",
    "Nikkei Asia": "https://asia.nikkei.com/rss/feed/nar",
    
    # Alternative/Technical
    "TradingView Ideas": "https://www.tradingview.com/feed/",
    "Stocktwits Trending": "https://stocktwits.com/trending.rss",
    
    # Google News searches (current)
    "Google: Market News": "https://news.google.com/rss/search?q=stock+market+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: S&P 500": "https://news.google.com/rss/search?q=S%26P+500+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Fed News": "https://news.google.com/rss/search?q=federal+reserve+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Earnings": "https://news.google.com/rss/search?q=earnings+report+when:24h&hl=en-US&gl=US&ceid=US:en",
}

def test_feed(name, url):
    """Test if a feed is accessible and has content"""
    try:
        # Try to fetch with timeout
        feed = feedparser.parse(url)
        
        # Check for errors
        if hasattr(feed, 'bozo') and feed.bozo:
            if hasattr(feed, 'bozo_exception'):
                return False, f"Parse error: {type(feed.bozo_exception).__name__}"
        
        # Check for entries
        if not feed.entries:
            return False, "No entries found"
        
        # Get sample headline
        sample = feed.entries[0].title if feed.entries else "N/A"
        return True, f"OK - {len(feed.entries)} entries (e.g., '{sample[:60]}...')"
        
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

print("=" * 80)
print(f"RSS FEED ACCESSIBILITY TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80 + "\n")

working_feeds = {}
broken_feeds = {}

for name, url in TEST_FEEDS.items():
    print(f"Testing: {name:30s} ", end="", flush=True)
    success, message = test_feed(name, url)
    
    if success:
        print(f"✅ {message}")
        working_feeds[name] = url
    else:
        print(f"❌ {message}")
        broken_feeds[name] = url

print("\n" + "=" * 80)
print(f"RESULTS: {len(working_feeds)} working, {len(broken_feeds)} broken")
print("=" * 80 + "\n")

print("✅ WORKING FEEDS:")
for name in sorted(working_feeds.keys()):
    print(f"  - {name}")

if broken_feeds:
    print("\n❌ BROKEN FEEDS:")
    for name in sorted(broken_feeds.keys()):
        print(f"  - {name}")

print("\n" + "=" * 80)
print("RECOMMENDED RSS_FEEDS DICTIONARY:")
print("=" * 80 + "\n")
print("RSS_FEEDS = {")
for name, url in sorted(working_feeds.items()):
    print(f'    "{name}": "{url}",')
print("}")
