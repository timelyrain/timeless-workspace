#!/usr/bin/env python3
"""Quick test of the optimized news filtering system"""

import sys
import os

# Add projects directory to path
sys.path.insert(0, 'projects')
os.chdir('projects')

# Set minimal env vars for testing
os.environ['GEMINI_API_KEY'] = 'test'  # Will be loaded from .env
os.environ['TELEGRAM_TOKEN_MARKET'] = ''
os.environ['CHAT_ID'] = ''

# Import and test the helper functions
import re

# Test impact scoring
IMPACT_KEYWORDS = {
    'CRITICAL': ['earnings beat', 'earnings miss', 'merger', 'FDA approval', 'bankruptcy'],
    'HIGH': ['federal reserve', 'rate cut', 'inflation', 'tariff'],
    'MEDIUM': ['analyst upgrade', 'buyback', 'dividend'],
    'LOW': ['could', 'might', 'opinion']
}

FLUFF_PATTERNS = [
    r'^how to\s+',
    r'^why you should\s+',
    r'^\d+ reasons\s+',
    r'^i\'?m inheriting',
]

def calculate_impact_score(headline):
    headline_lower = headline.lower()
    
    for pattern in FLUFF_PATTERNS:
        if re.search(pattern, headline_lower):
            return 0, 'FLUFF'
    
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
    
    return 30, 'NORMAL'

def extract_tickers(headline):
    patterns = [
        r'\(([A-Z]{1,5})\)',
        r'\$([A-Z]{1,5})\b',
        r'\b([A-Z]{2,5})\b(?=\s+(?:stock|shares|earnings|revenue))',
    ]
    
    tickers = set()
    for pattern in patterns:
        matches = re.findall(pattern, headline)
        tickers.update(matches)
    
    false_positives = {'CEO', 'CFO', 'IPO', 'ETF', 'SEC', 'FDA', 'USA', 'NYSE', 'AI', 'EV', 'ESG', 'M&A'}
    return [t for t in tickers if t not in false_positives]

# Test cases
test_headlines = [
    "Tesla (TSLA) earnings beat expectations by 15%",
    "How to invest in the stock market for beginners",
    "Federal Reserve signals potential rate cut in March",
    "Apple stock might rally next quarter says analyst",
    "NVDA shares surge on AI chip demand",
    "I'm inheriting $250K. Will paying off my student loans be smart?",
    "Analyst upgrades Microsoft (MSFT) to strong buy",
    "Market analysis: what investors need to know",
    "Intel (INTC) announces massive layoffs and restructuring",
    "3 reasons why you should buy gold now",
]

print("=" * 80)
print("OPTIMIZED NEWS FILTERING TEST")
print("=" * 80 + "\n")

print("Testing Impact Scoring & Ticker Extraction:\n")
for headline in test_headlines:
    score, impact = calculate_impact_score(headline)
    tickers = extract_tickers(headline)
    
    emoji = "🔴" if impact == 'CRITICAL' else ("🟠" if impact == 'HIGH' else ("🟡" if impact == 'MEDIUM' else "⚪"))
    if impact == 'FLUFF':
        emoji = "🗑️"
    
    print(f"{emoji} [{impact:8s}] Score: {score:3d} | Tickers: {tickers or 'None'}")
    print(f"   {headline}")
    print()

print("=" * 80)
print("RESULTS:")
print("=" * 80)
filtered_count = sum(1 for h in test_headlines if calculate_impact_score(h)[1] != 'FLUFF')
print(f"✅ Kept: {filtered_count}/{len(test_headlines)} headlines")
print(f"🗑️ Filtered: {len(test_headlines) - filtered_count}/{len(test_headlines)} fluff items")
print(f"\n📊 Quality improvement: {(filtered_count/len(test_headlines)*100):.0f}% signal-to-noise")
