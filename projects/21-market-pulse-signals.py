import os
import json
import re
import requests
import feedparser
import google.generativeai as genai
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from difflib import SequenceMatcher

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_MARKET")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Source quality tiers for prioritization
SOURCE_TIERS = {
    'tier1': ['Bloomberg Markets', 'WSJ Markets', 'Financial Times Markets', 'FT Global Economy'],
    'tier2': ['CNBC Breaking', 'CNBC Top News', 'SEC News', 'Finviz News', 'Benzinga'],
    'tier3': ['MarketWatch', 'Yahoo Finance', 'Investing.com', 'Seeking Alpha', 'TradingView Ideas', 'ZeroHedge', 'Nikkei Asia']
}

# Impact keywords for scoring (Phase 1)
IMPACT_KEYWORDS = {
    'CRITICAL': [
        'earnings beat', 'earnings miss', 'guidance raised', 'guidance cut', 
        'merger', 'acquisition', 'buyout', 'takeover',
        'FDA approval', 'FDA rejection', 'bankruptcy', 'delisting',
        'CEO resigns', 'CEO appointed', 'massive layoffs', 'restructuring plan'
    ],
    'HIGH': [
        'federal reserve', 'fed decision', 'interest rate', 'rate cut', 'rate hike',
        'jobs report', 'unemployment', 'inflation', 'CPI', 'PPI',
        'tariff', 'trade war', 'sanctions', 'geopolitical',
        'earnings report', 'revenue beat', 'revenue miss',
        'layoffs', 'job cuts'
    ],
    'MEDIUM': [
        'analyst upgrade', 'analyst downgrade', 'price target',
        'buyback', 'dividend', 'stock split',
        'partnership', 'contract', 'deal',
        'product launch', 'new product'
    ],
    'LOW': [
        'could', 'might', 'may', 'opinion', 'analysis',
        'how to invest', 'investment tips', 'market outlook'
    ]
}

# Fluff patterns to filter out
FLUFF_PATTERNS = [
    r'^how to\s+',
    r'^why you should\s+',
    r'^\d+ reasons\s+',
    r'^best\s+\w+\s+to\s+',
    r'investment tips',
    r'what investors need to know',
    r'^i\'?m inheriting',
    r'^should i\s+',
]

# Comprehensive RSS feeds - institutional grade sources (all tested & verified working)
RSS_FEEDS = {
    # Premium Financial News (Tier 1)
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "Financial Times Markets": "https://www.ft.com/markets?format=rss",
    "FT Global Economy": "https://www.ft.com/global-economy?format=rss",
    
    # Major Financial Media (Tier 2)
    "CNBC Breaking": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNBC Top News": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    
    # Trading & Analysis Platforms
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    "Benzinga": "https://www.benzinga.com/feed",
    "TradingView Ideas": "https://www.tradingview.com/feed/",
    "ZeroHedge": "https://feeds.feedburner.com/zerohedge/feed",
    
    # Institutional & Regulatory
    "SEC News": "https://www.sec.gov/news/pressreleases.rss",
    
    # International Markets
    "Nikkei Asia": "https://asia.nikkei.com/rss/feed/nar",
    
    # Google News - Targeted Searches (24h filter)
    "Google: Market News": "https://news.google.com/rss/search?q=stock+market+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: S&P 500": "https://news.google.com/rss/search?q=S%26P+500+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Fed News": "https://news.google.com/rss/search?q=federal+reserve+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Earnings": "https://news.google.com/rss/search?q=earnings+report+when:24h&hl=en-US&gl=US&ceid=US:en",
}

def fetch_finviz_news():
    """Scrape Finviz news page (RSS feed is broken, so we scrape directly)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get('https://finviz.com/news.ashx', headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news_table = soup.find('table', class_='styled-table-new')
        if not news_table:
            return []
        
        headlines = []
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
        print(f"    ✗ Finviz scraping error: {e}")
        return []

def calculate_impact_score(headline):
    """Phase 1: Calculate impact score based on keywords"""
    headline_lower = headline.lower()
    
    # Check for fluff patterns first (auto-disqualify)
    for pattern in FLUFF_PATTERNS:
        if re.search(pattern, headline_lower):
            return 0, 'FLUFF'
    
    # Score based on keywords
    for keyword in IMPACT_KEYWORDS['CRITICAL']:
        if keyword in headline_lower:
            return 100, 'CRITICAL'
    
    for keyword in IMPACT_KEYWORDS['HIGH']:
        if keyword in headline_lower:
            return 75, 'HIGH'
    
    for keyword in IMPACT_KEYWORDS['MEDIUM']:
        if keyword in headline_lower:
            return 50, 'MEDIUM'
    
    for keyword in IMPACT_KEYWORDS['LOW']:
        if keyword in headline_lower:
            return 10, 'LOW'
    
    return 30, 'NORMAL'  # Default for news without specific keywords

def extract_tickers(headline):
    """Extract stock tickers from headline"""
    # Common patterns: (TICKER), $TICKER, or standalone 3-5 letter caps
    patterns = [
        r'\(([A-Z]{1,5})\)',  # (AAPL)
        r'\$([A-Z]{1,5})\b',  # $AAPL
        r'\b([A-Z]{2,5})\b(?=\s+(?:stock|shares|earnings|revenue))',  # AAPL stock
    ]
    
    tickers = set()
    for pattern in patterns:
        matches = re.findall(pattern, headline)
        tickers.update(matches)
    
    # Filter out common false positives
    false_positives = {'CEO', 'CFO', 'IPO', 'ETF', 'SEC', 'FDA', 'USA', 'NYSE', 'AI', 'EV', 'ESG', 'M&A'}
    return [t for t in tickers if t not in false_positives]

def get_source_tier(source):
    """Get tier number for a source"""
    for tier, sources in SOURCE_TIERS.items():
        if source in sources:
            return int(tier[-1])  # Extract number from 'tier1', 'tier2', etc.
    return 3  # Default to tier 3

def get_market_headlines():
    """Fetches top headlines from multiple institutional sources with intelligent filtering"""
    print(f"Fetching news from {len(RSS_FEEDS) + 1} sources...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_headlines = []  # List of dicts with metadata
    sources_fetched = 0
    
    # First, fetch Finviz via scraping (special case)
    print(f"  ✓ Fetching from Finviz News (scraped)...")
    finviz_headlines = fetch_finviz_news()
    if finviz_headlines:
        for headline in finviz_headlines:
            score, impact = calculate_impact_score(headline)
            tickers = extract_tickers(headline)
            all_headlines.append({
                'source': 'Finviz News',
                'title': headline,
                'tier': 2,
                'impact_score': score,
                'impact_level': impact,
                'tickers': tickers,
                'timestamp': datetime.now()
            })
        print(f"    → Got {len(finviz_headlines)} headlines")
        sources_fetched += 1
    else:
        print(f"    ⚠ No entries found")
    
    # Then fetch RSS feeds with tier-based limits
    for source, url in RSS_FEEDS.items():
        try:
            print(f"  ✓ Fetching from {source}...")
            feed = feedparser.parse(url)

            if not feed.entries:
                print(f"    ⚠ No entries found")
                continue
            
            tier = get_source_tier(source)
            max_items = 4 if tier == 1 else (3 if tier == 2 else 2)
            
            count = 0
            for entry in feed.entries[:max_items]:
                # Clean up title (remove source attribution from Google News)
                title = entry.title
                if ' - ' in title and source.startswith('Google'):
                    title = title.split(' - ')[0]
                
                # Calculate impact and extract tickers
                score, impact = calculate_impact_score(title)
                tickers = extract_tickers(title)
                
                # Skip fluff content
                if impact == 'FLUFF':
                    continue
                
                all_headlines.append({
                    'source': source,
                    'title': title,
                    'tier': tier,
                    'impact_score': score,
                    'impact_level': impact,
                    'tickers': tickers,
                    'timestamp': datetime.now()
                })
                count += 1
            
            print(f"    → Got {count} headlines")
            sources_fetched += 1
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue
    
    print(f"\n📊 Raw total: {len(all_headlines)} headlines from {sources_fetched} sources")
    
    if not all_headlines:
        return "", []
    
    # Phase 1: Filter and sort by impact
    print(f"🔍 Phase 1: Impact scoring & filtering...")
    filtered = [h for h in all_headlines if h['impact_score'] > 0]
    print(f"   → Filtered out {len(all_headlines) - len(filtered)} low-quality items")
    
    # Phase 2: Smart deduplication (fuzzy matching for similar headlines)
    print(f"🔍 Phase 2: Fuzzy deduplication...")
    
    SIMILARITY_THRESHOLD = 0.70  # 70% similarity = considered duplicate
    deduplicated = []
    
    for h in filtered:
        title = h['title'].lower()
        is_duplicate = False
        
        # Compare with all existing deduplicated headlines
        for existing in deduplicated:
            existing_title = existing['title'].lower()
            
            # Calculate similarity ratio (0.0 to 1.0)
            similarity = SequenceMatcher(None, title, existing_title).ratio()
            
            if similarity >= SIMILARITY_THRESHOLD:
                # Found duplicate - keep the better one
                is_duplicate = True
                
                # Replace if current headline is from better source or higher impact
                if (h['tier'] < existing['tier'] or 
                    (h['tier'] == existing['tier'] and h['impact_score'] > existing['impact_score'])):
                    deduplicated.remove(existing)
                    deduplicated.append(h)
                    print(f"   🔄 Replaced: '{existing_title[:60]}...'")
                    print(f"      With: '{title[:60]}...' (similarity: {similarity:.0%})")
                break
        
        if not is_duplicate:
            deduplicated.append(h)
    
    print(f"   → Removed {len(filtered) - len(deduplicated)} similar headlines")
    
    # Sort by impact score (descending) and tier (ascending - tier 1 is best)
    deduplicated.sort(key=lambda x: (x['impact_score'], -x['tier']), reverse=True)
    
    # Take top 30 for further processing
    top_headlines = deduplicated[:30]
    
    print(f"📊 Phase 1+2 complete: {len(top_headlines)} high-quality headlines selected\n")
    
    # Format for Gemini (Phase 3 will do semantic clustering)
    formatted = []
    for h in top_headlines:
        ticker_str = f" [{', '.join(h['tickers'])}]" if h['tickers'] else ""
        impact_emoji = "🔴" if h['impact_level'] == 'CRITICAL' else ("🟠" if h['impact_level'] == 'HIGH' else "🟡")
        formatted.append(f"{impact_emoji} **{h['source']}**: {h['title']}{ticker_str}")
    
    return "\n".join(formatted), top_headlines

def analyze_with_gemini(headlines):
    """Sends headlines to Gemini 2.0 for analysis with Phase 3: Semantic clustering"""
    print("🤖 Phase 3: AI-powered semantic analysis & consolidation...\n")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-001')
    
    prompt = (
        f"You are an elite financial analyst creating an actionable market briefing. "
        f"The headlines below are PRE-FILTERED and SCORED by impact (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM).\n\n"
        f"YOUR TASK:\n"
        f"1. **Consolidate duplicate/similar stories** into single topics (e.g., 5 headlines about Tesla → 1 Tesla summary)\n"
        f"2. **Prioritize by trading impact** - what will actually move markets?\n"
        f"3. **Extract key tickers** mentioned and their directional bias\n\n"
        f"HEADLINES:\n{headlines}\n\n"
        f"Write a streamlined daily briefing:\n\n"
        f"**START WITH ONE-LINE HEADER:**\n"
        f"Format: [📈/📉/➡️] Sentiment: [BULLISH/BEARISH/NEUTRAL] | 🌐 Driver: [key macro theme]\n"
        f"Example: 📈 Sentiment: BULLISH | 🌐 Driver: Fed dovish pivot\n\n"
        f"**THEN PROVIDE FULL BRIEFING:**\n\n"
        f"1. **🎯 Market Vibe Check**: Overall sentiment in ONE sentence (Bulls/Bears/Confused?)\n\n"
        f"2. **🔥 Top Market Movers** (3-5 consolidated topics, not 20 separate headlines):\n"
        f"   - Focus on what's ACTIONABLE for traders\n"
        f"   - Merge similar stories (e.g., 'Fed rate expectations' not 3 separate Fed headlines)\n"
        f"   - Include specific tickers where relevant\n"
        f"   - Use 🟢 for bullish, 🔴 for bearish, ⚪ for neutral\n\n"
        f"3. **📊 Index Outlook**: S&P 500, Nasdaq, Dow - ONE line each\n\n"
        f"4. **🎯 Tickers in Focus**: List 3-5 most mentioned/impactful stocks with brief context\n\n"
        f"5. **💡 Sector Rotation**: Which sectors are moving and why (1-2 sentences)\n\n"
        f"STYLE RULES:\n"
        f"- Under 400 words total\n"
        f"- Consolidate aggressively - quality over quantity\n"
        f"- No fluff or filler\n"
        f"- Professional but engaging\n"
        f"- Focus on TRADEABLE information\n\n"
        f"Think: 'Bloomberg Terminal morning brief' meets 'trader's actionable intel' 📈"
    )

    response = model.generate_content(prompt)
    return response.text


def send_telegram_message(message):
    """Sends the analysis to Telegram"""
    print("📱 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit - truncate BEFORE any processing
    if len(message) > 4096:
        print(f"⚠️  Message too long ({len(message)} chars), truncating to 4090...")
        message = message[:4090] + "\n\n[...]"
    
    # Convert Markdown to plain text to avoid formatting issues
    # Remove ** for bold and _ for italics
    plain_message = message.replace('**', '').replace('_', '')
    
    payload = {
        "chat_id": CHAT_ID,
        "text": plain_message
    }
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"✗ Telegram API error: {response.status_code}")
            print(f"   Response: {response.text}\n")
        response.raise_for_status()
        print("✓ Message sent successfully!\n")
    except Exception as e:
        print(f"✗ Telegram error: {e}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 MARKET SENTIMENT BOT")
    print("=" * 60 + "\n")
    
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY environment variable is missing.")
        exit(1)
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  Warning: Telegram credentials missing. Analysis will print to console only.")

    try:
        # 1. Get News from multiple sources (with optimization phases 1+2)
        headlines_text, headline_metadata = get_market_headlines()
        
        if not headlines_text:
            error_msg = "⚠️ No market news found from any source."
            print(error_msg)
            if TELEGRAM_TOKEN and CHAT_ID:
                send_telegram_message(error_msg)
            exit()

        # 2. Analyze with Gemini (single optimized call)
        analysis = analyze_with_gemini(headlines_text)
        
        # 3. Format message with optimization stats
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        header = f"🚀 Market Intel 📊\n{timestamp}\n\n"
        
        # Count impact levels
        critical_count = sum(1 for h in headline_metadata if h['impact_level'] == 'CRITICAL')
        high_count = sum(1 for h in headline_metadata if h['impact_level'] == 'HIGH')
        
        footer = (
            f"\n\n━━━━━━━━━━━━━━━━━\n"
            f"📊 Intelligence: {len(headline_metadata)} curated headlines ({critical_count} critical, {high_count} high-impact)\n"
            f"🔍 Sources: Bloomberg, WSJ, FT, CNBC, Finviz, SEC & 13 premium feeds\n"
            f"🤖 AI-optimized by KHK Intelligence"
        )
        
        full_message = header + analysis + footer
        
        # 4. Send or print
        if TELEGRAM_TOKEN and CHAT_ID:
            send_telegram_message(full_message)
        else:
            print("\n" + "=" * 60)
            print("ANALYSIS RESULT (Telegram not configured)")
            print("=" * 60 + "\n")
            print(full_message)
        
        print("\n✅ Bot execution completed successfully!")
        print(f"📈 Processed {len(headline_metadata)} optimized headlines")
        
    except Exception as e:
        error_msg = f"❌ Critical Error: {str(e)}"
        print(error_msg)
        if TELEGRAM_TOKEN and CHAT_ID:
            send_telegram_message(f"⚠️ Bot Error: {str(e)}")
        import sys
        sys.exit(1)  # Exit with error code to fail the GitHub Actions workflow