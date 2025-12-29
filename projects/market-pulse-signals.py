import os
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Comprehensive free RSS feeds - institutional grade sources
RSS_FEEDS = {
    # Major Financial News Outlets
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    
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
    
    # Return top 25 headlines to avoid overwhelming Gemini
    return "\n".join(all_headlines[:25])

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

def send_telegram_message(message):
    """Sends the analysis to Telegram"""
    print("📱 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Convert Markdown to plain text to avoid formatting issues
    # Remove ** for bold and _ for italics
    plain_message = message.replace('**', '').replace('_', '')
    
    # Telegram has a 4096 character limit
    if len(plain_message) > 4096:
        print(f"⚠️  Message too long ({len(plain_message)} chars), truncating to 4096...")
        plain_message = plain_message[:4090] + "\n\n[...]"
    
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
        # 1. Get News from multiple sources
        headlines_text = get_market_headlines()
        
        if not headlines_text:
            error_msg = "⚠️ No market news found from any source."
            print(error_msg)
            if TELEGRAM_TOKEN and CHAT_ID:
                send_telegram_message(error_msg)
            exit()

        # 2. Analyze with Gemini
        analysis = analyze_with_gemini(headlines_text)
        
        # 3. Format message
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        header = f"🚀 **Your Daily Market Tea** ☕\n_{timestamp}_\n\n"
        
        headline_count = len(headlines_text.split('\n'))
        footer = (
            f"\n\n━━━━━━━━━━━━━━━━━\n"
            f"📰 _Brewed from {headline_count} fresh headlines_\n"
            f"🔍 _Sources: MarketWatch, Investing.com, Yahoo Finance, Seeking Alpha & Google News_\n"
            f"🤖 _Analyzed by your friendly neighborhood KHK AI_"
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
        
    except Exception as e:
        error_msg = f"❌ Critical Error: {str(e)}"
        print(error_msg)
        if TELEGRAM_TOKEN and CHAT_ID:
            send_telegram_message(f"⚠️ Bot Error: {str(e)}")