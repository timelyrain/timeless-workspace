import os
import json
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_MARKET")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Comprehensive free RSS feeds - institutional grade sources
RSS_FEEDS = {
    # Major Financial News Outlets
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    "ZeroHedge": "https://feeds.feedburner.com/zerohedge/feed",
    
    # Google News - Targeted Searches (24h filter)
    "Google: Market News": "https://news.google.com/rss/search?q=stock+market+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: S&P 500": "https://news.google.com/rss/search?q=S%26P+500+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Fed News": "https://news.google.com/rss/search?q=federal+reserve+when:24h&hl=en-US&gl=US&ceid=US:en",
    "Google: Earnings": "https://news.google.com/rss/search?q=earnings+report+when:24h&hl=en-US&gl=US&ceid=US:en",
}

def get_market_headlines():
    """Fetches top headlines from multiple institutional sources"""
    print(f"Fetching news from {len(RSS_FEEDS)} sources...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_headlines = []
    sources_fetched = 0
    
    for source, url in RSS_FEEDS.items():
        try:
            print(f"  ✓ Fetching from {source}...")
            feed = feedparser.parse(url)

            if not feed.entries:
                print(f"    ⚠ No entries found")
                continue
                
            # Get top 3-4 stories from each source
            count = 0
            for entry in feed.entries[:4]:
                # Clean up title (remove source attribution from Google News)
                title = entry.title
                if ' - ' in title and source.startswith('Google'):
                    title = title.split(' - ')[0]
                
                headline = f"**{source}**: {title}"
                all_headlines.append(headline)
                count += 1
            
            print(f"    → Got {count} headlines")
            sources_fetched += 1
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue
    
    print(f"\n📊 Total: {len(all_headlines)} headlines from {sources_fetched} sources\n")
    
    if not all_headlines:
        return ""
    
    # Deduplicate case-insensitively and cap to top 25 to avoid overwhelming Gemini
    deduped = []
    seen = set()
    for h in all_headlines:
        key = h.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(h)
        if len(deduped) >= 25:
            break

    return "\n".join(deduped)

def analyze_with_gemini(headlines):
    """Sends headlines to Gemini 2.0 for analysis"""
    print("🤖 Analyzing with Gemini AI...\n")
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = (
        f"You are a witty, engaging financial analyst who makes market news fun to read. "
        f"Analyze today's market headlines with personality:\n\n"
        f"{headlines}\n\n"
        f"Write a daily market briefing that's informative AND entertaining. Cover:\n\n"
        f"1. **Market Vibe Check** 🎯: What's the overall sentiment? (Bulls charging? 🐂 Bears hibernating? 🐻 Or everyone confused? 🤷)\n"
        f"2. **Hot Topics** 🔥: What's actually moving markets today? (3-4 key stories with some flair)\n"
        f"3. **The Big Boards** 📊: How are the indices likely to react? (S&P, Nasdaq, Dow)\n"
        f"4. **Sector Spotlight** 💡: Which sectors are getting all the attention?\n"
        f"5. **Name Drops** 🏢: Any companies stealing the show today?\n\n"
        f"Writing style:\n"
        f"- Use emojis strategically (but don't go crazy)\n"
        f"- Add witty one-liners and metaphors\n"
        f"- Keep it conversational and fun\n"
        f"- Stay factual - no BS, just facts with personality\n"
        f"- Under 500 words\n"
        f"- Use markdown for structure\n\n"
        f"Think: 'Professional trader at happy hour explaining the day' energy 🍻"
    )

    response = model.generate_content(prompt)
    return response.text


def analyze_structured_with_gemini(headlines):
    """Ask Gemini for structured sentiment, impact, and directional cues."""
    print("🤖 Getting structured summary from Gemini...\n")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    prompt = (
        "Summarize these headlines for trading decisions. Return ONLY JSON with this schema:\n"
        "{\n"
        "  \"overall_sentiment\": \"bullish|bearish|neutral\",\n"
        "  \"macro_driver\": \"string\",\n"
        "  \"high_impact_items\": [\n"
        "    {\"title\": \"string\", \"direction\": \"up|down|mixed\", \"impact\": \"high|medium|low\", \"why\": \"string\"}\n"
        "  ],\n"
        "  \"top_tickers\": [\n"
        "    {\"ticker\": \"string\", \"sentiment\": \"bullish|bearish|neutral\", \"why\": \"string\"}\n"
        "  ]\n"
        "}\n"
        "Rules: be concise; limit high_impact_items to 5; limit top_tickers to 6; omit markdown; no extra text.\n"
        f"Headlines:\n{headlines}"
    )

    response = model.generate_content(prompt)
    return response.text or ""


def _clean_structured_json(raw: str) -> str:
    """Strip fences/markdown and extract the first JSON object if present."""
    if not raw:
        return ""
    s = raw.strip()
    # Remove Markdown fences/backticks if present
    if s.startswith("```json"):
        s = s[len("```json"):]
    s = s.strip('`').strip()
    # Extract JSON object between first { and last }
    if '{' in s and '}' in s:
        start = s.find('{')
        end = s.rfind('}')
        if end > start:
            s = s[start:end+1]
    return s

def send_telegram_message(message):
    """Sends the analysis to Telegram"""
    print("📱 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram has a 4096 character limit - truncate BEFORE any processing
    if len(message) > 4096:
        print(f"⚠️  Message too long ({len(message)} chars), truncating to 4096...")
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


def build_structured_section(structured_json: str) -> str:
    """Format structured JSON (string) into a compact text block."""
    if not structured_json:
        return ""
    try:
        cleaned = _clean_structured_json(structured_json)
        if not cleaned:
            return ""
        data = json.loads(cleaned)
    except Exception as e:
        print(f"✗ Failed to parse structured summary: {e}")
        return ""

    overall = data.get("overall_sentiment", "neutral").upper()
    macro = data.get("macro_driver", "")
    items = data.get("high_impact_items", []) or []
    tickers = data.get("top_tickers", []) or []

    lines = []
    lines.append(f"📈 Structured read: {overall}")
    if macro:
        lines.append(f"🌐 Macro: {macro}")

    if items:
        lines.append("🔥 High-impact moves:")
        for itm in items[:5]:
            title = itm.get("title", "")
            direction = itm.get("direction", "")
            impact = itm.get("impact", "")
            why = itm.get("why", "")
            arrow = "🟢" if direction == "up" else "🔴" if direction == "down" else "↔️"
            lines.append(f"- {arrow} ({impact}) {title} — {why}")

    if tickers:
        lines.append("🎯 Top tickers:")
        for t in tickers[:6]:
            tk = t.get("ticker", "").upper()
            sent = t.get("sentiment", "")
            why = t.get("why", "")
            emoji = "🟢" if sent == "bullish" else "🔴" if sent == "bearish" else "⚪"
            lines.append(f"- {emoji} {tk}: {why}")

    return "\n".join(lines)

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
        # 1. Get News from multiple sources
        headlines_text = get_market_headlines()
        
        if not headlines_text:
            error_msg = "⚠️ No market news found from any source."
            print(error_msg)
            if TELEGRAM_TOKEN and CHAT_ID:
                send_telegram_message(error_msg)
            exit()

        # 2. Analyze with Gemini (narrative + structured)
        analysis = analyze_with_gemini(headlines_text)
        structured_json = analyze_structured_with_gemini(headlines_text)
        structured_block = build_structured_section(structured_json)
        
        # 3. Format message
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        header = f"🚀 **Your Daily Market Tea** ☕\n_{timestamp}_\n\n"
        
        headline_count = len(headlines_text.split('\n'))
        footer = (
            f"\n\n━━━━━━━━━━━━━━━━━\n"
            f"📰 _Brewed from {headline_count} fresh headlines_\n"
            f"🔍 _Sources: Reuters, WSJ, MarketWatch, Investing.com, Yahoo Finance, Seeking Alpha, ZeroHedge & Google News_\n"
            f"🤖 _Analyzed by your friendly neighborhood KHK AI_"
        )
        
        full_message = header
        if structured_block:
            full_message += structured_block + "\n\n"
        full_message += analysis + footer
        
        # 4. Send or print
        if TELEGRAM_TOKEN and CHAT_ID:
            send_telegram_message(full_message)
        else:
            print("\n" + "=" * 60)
            print("ANALYSIS RESULT (Telegram not configured)")
            print("=" * 60 + "\n")
            print(full_message)
        
        print("\n✅ Bot execution completed successfully!")
        
    except Exception as e:
        error_msg = f"❌ Critical Error: {str(e)}"
        print(error_msg)
        if TELEGRAM_TOKEN and CHAT_ID:
            send_telegram_message(f"⚠️ Bot Error: {str(e)}")