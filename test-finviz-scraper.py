import requests
from bs4 import BeautifulSoup
import re

def fetch_finviz_news():
    """Scrape Finviz news page since RSS feed is broken"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get('https://finviz.com/news.ashx', headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the news table
        news_table = soup.find('table', class_='styled-table-new')
        if not news_table:
            return []
        
        headlines = []
        
        # Look for all links in the table
        for link in news_table.find_all('a', href=True):
            text = link.get_text(strip=True)
            # Skip empty, very short, or navigation links
            if len(text) > 20 and not text.startswith(('Home', 'Screener', 'Maps')):
                # Clean up timestamp if present (e.g., "Jan-23-26 06:30PM")
                text = re.sub(r'^[A-Z][a-z]{2}-\d{2}-\d{2}\s+\d{2}:\d{2}[AP]M\s+', '', text)
                if text and len(text) > 15:
                    headlines.append(text)
        
        # Deduplicate and return top 10
        seen = set()
        unique = []
        for h in headlines:
            if h.lower() not in seen:
                seen.add(h.lower())
                unique.append(h)
                if len(unique) >= 10:
                    break
        
        return unique
        
    except Exception as e:
        print(f"Finviz scraping error: {e}")
        return []

# Test it
print("Testing Finviz scraper...")
print("=" * 80)
headlines = fetch_finviz_news()
print(f"\nFound {len(headlines)} headlines:\n")
for i, h in enumerate(headlines, 1):
    print(f"{i}. {h[:80]}")

print("\n" + "=" * 80)
if headlines:
    print("✅ SUCCESS - Finviz scraping works!")
else:
    print("❌ FAILED - No headlines extracted")
