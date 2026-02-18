#!/usr/bin/env python3
"""
Auto-Categorize Uncategorized Positions

Checks fetch-ibkr-positions.xlsx for uncategorized stocks/ETFs and suggests 
categories via Telegram. You can approve additions by updating the config file.

Logic:
- ETFs → Suggest Global Triads or Four Horsemen (based on description)
- Individual stocks → Suggest Alpha (speculation)
- Options → Already handled (Cash Cow or Omega)
- Cash → War Chest (already tracked)

Usage:
    python auto-categorize-positions.py

Output:
    Telegram alert listing uncategorized positions with suggested categories
"""

import os
import sys
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv
from portfolio_categories_mappings import SYMBOL_MAPPING

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_RISK')
CHAT_ID = os.getenv('CHAT_ID')
POSITIONS_FILE = Path(__file__).parent / "fetch-ibkr-positions.xlsx"


def get_all_categorized_symbols():
    """Get set of all symbols already in SYMBOL_MAPPING."""
    categorized = set()
    for category, symbols in SYMBOL_MAPPING.items():
        categorized.update(symbols)
    return categorized


def load_positions():
    """Load positions from Excel file."""
    if not POSITIONS_FILE.exists():
        print(f"❌ File not found: {POSITIONS_FILE}")
        return None
    
    try:
        # Read both sheets
        positions_hk = pd.read_excel(POSITIONS_FILE, sheet_name='PositionsHK')
        positions_al = pd.read_excel(POSITIONS_FILE, sheet_name='PositionsAL')
        
        # Combine
        all_positions = pd.concat([positions_hk, positions_al], ignore_index=True)
        
        # Filter to stocks and ETFs only (exclude options and cash)
        stocks_etfs = all_positions[all_positions['AssetClass'] == 'STK'].copy()
        
        return stocks_etfs
        
    except Exception as e:
        print(f"❌ Error loading positions: {e}")
        return None


def suggest_category(row):
    """Suggest category based on asset class and description."""
    symbol = row['Symbol']
    description = str(row.get('Description', '')).upper()
    
    # Check if it's an ETF (common keywords in description)
    etf_keywords = ['ETF', 'ISHARES', 'VANGUARD', 'SPDR', 'INVESCO', 'XTRACKERS', 'UBS']
    is_etf = any(keyword in description for keyword in etf_keywords)
    
    if is_etf:
        # ETF classification based on description
        if any(word in description for word in ['NASDAQ', 'TECH', 'GROWTH', 'INNOVATION']):
            return 'four_horsemen', '🚀 Growth/Tech ETF'
        elif any(word in description for word in ['WORLD', 'GLOBAL', 'ALL COUNTRY', 'MSCI', 'DIVIDEND']):
            return 'global_triads', '🌍 Strategic Core ETF'
        else:
            return 'global_triads', '🌍 ETF (default to core)'
    else:
        # Individual stock → Alpha (speculation/theme)
        return 'alpha', '🎲 Individual Stock'


def find_uncategorized():
    """Find positions not in SYMBOL_MAPPING."""
    categorized_symbols = get_all_categorized_symbols()
    positions = load_positions()
    
    if positions is None or len(positions) == 0:
        return []
    
    # Find uncategorized
    uncategorized = []
    for _, row in positions.iterrows():
        symbol = row['Symbol']
        if symbol not in categorized_symbols:
            suggested_cat, reason = suggest_category(row)
            uncategorized.append({
                'symbol': symbol,
                'description': row.get('Description', 'N/A'),
                'value': row.get('PositionValueUSD', 0),
                'suggested_category': suggested_cat,
                'reason': reason
            })
    
    return uncategorized


def send_telegram_alert(message):
    """Send alert via Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")
        return False


def format_message(uncategorized):
    """Format Telegram message with uncategorized positions."""
    if not uncategorized:
        return None
    
    msg = "🔍 *UNCATEGORIZED POSITIONS DETECTED*\n\n"
    msg += f"Found {len(uncategorized)} position(s) not in portfolio_categories_mappings.py:\n\n"
    
    # Group by suggested category
    by_category = {}
    for item in uncategorized:
        cat = item['suggested_category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    # Display by category
    for category, items in by_category.items():
        cat_name = category.replace('_', ' ').title()
        msg += f"*Suggested: {cat_name}*\n"
        for item in items:
            msg += f"• `{item['symbol']}` - {item['description'][:40]}\n"
            msg += f"  Value: ${item['value']:,.0f} | {item['reason']}\n"
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━\n\n"
    msg += "*📝 ACTION REQUIRED:*\n"
    msg += "Update `portfolio_categories_mappings.py` to categorize these positions.\n\n"
    msg += "*Example:*\n"
    msg += "```python\n"
    
    # Show example for first uncategorized
    first = uncategorized[0]
    cat = first['suggested_category']
    msg += f"'{cat}': [\n"
    msg += f"    # ... existing symbols ...\n"
    msg += f"    '{first['symbol']}',  # ← Add this\n"
    msg += f"],\n"
    msg += "```"
    
    return msg


def main():
    """Main execution."""
    print("=" * 60)
    print("AUTO-CATEGORIZE UNCATEGORIZED POSITIONS")
    print("=" * 60)
    print()
    
    print("📂 Loading positions...")
    uncategorized = find_uncategorized()
    
    if not uncategorized:
        print("✅ All positions are categorized!")
        return
    
    print(f"⚠️  Found {len(uncategorized)} uncategorized position(s):")
    for item in uncategorized:
        print(f"   • {item['symbol']} → Suggest: {item['suggested_category']}")
    print()
    
    print("📱 Sending Telegram alert...")
    message = format_message(uncategorized)
    
    if send_telegram_alert(message):
        print("✅ Alert sent successfully")
    else:
        print("❌ Failed to send alert")
        print("\nMessage preview:")
        print(message)
    
    print()
    print("=" * 60)
    print("✅ Analysis Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
