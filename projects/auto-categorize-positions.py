#!/usr/bin/env python3
"""
Auto-Categorize Uncategorized Positions

Compares live IBKR positions against SYMBOL_MAPPING (portfolio_categories_mappings.py).
Any stock/ETF position not found in SYMBOL_MAPPING is flagged as uncategorized and
reported via Telegram for manual review.

Categories are now defined in Dashboard (fetch-ibkr-positions-dashboard.xlsx) and
mirrored in SYMBOL_MAPPING — no automatic file modifications are made.

Usage:
    python auto-categorize-positions.py
"""

import os
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
POSITIONS_FILE = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'
DASHBOARD_FILE = Path(__file__).parent / 'fetch-ibkr-positions-dashboard.xlsx'


# =============================================================================
# POSITION READERS
# =============================================================================

def get_all_categorized_symbols():
    """Return set of all tickers defined across SYMBOL_MAPPING (Dashboard categories)."""
    categorized = set()
    for symbols in SYMBOL_MAPPING.values():
        categorized.update(symbols)
    return categorized


def load_positions():
    """Load stock/ETF positions from Excel file (both accounts, deduplicated)."""
    if not POSITIONS_FILE.exists():
        print(f"❌ File not found: {POSITIONS_FILE}")
        return None
    try:
        df = pd.read_excel(POSITIONS_FILE, sheet_name='Positions')
        df = df[df['AssetClass'] == 'STK'].copy()
        df = df.drop_duplicates(subset='Symbol', keep='first')
        return df
    except Exception as e:
        print(f"❌ Error loading positions: {e}")
        return None


def find_uncategorized_positions():
    """
    Return list of IBKR stock positions not in any Dashboard category (SYMBOL_MAPPING).
    These need manual review and classification.
    Returns None if positions could not be loaded (load error), [] if all categorized.
    """
    categorized = get_all_categorized_symbols()
    positions = load_positions()
    if positions is None:
        return None  # Load error — caller should alert
    if positions.empty:
        return []

    uncategorized = []
    for _, row in positions.iterrows():
        symbol = row['Symbol']
        if symbol not in categorized:
            uncategorized.append({
                'symbol': symbol,
                'description': str(row.get('Description', 'N/A')),
                'value': float(row.get('PositionValueUSD', 0) or 0),
            })
    return uncategorized


# =============================================================================
# TELEGRAM
# =============================================================================

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  Telegram not configured (TELEGRAM_TOKEN_RISK or CHAT_ID missing)")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Telegram failed: {e}")
        return False


def format_summary(uncategorized):
    """Build Telegram message for uncategorized positions."""
    if not uncategorized:
        return None
    msg = "⚠️ *AUTO-CATEGORIZE: Uncategorized Positions Detected*\n\n"
    msg += "*Positions not in any Dashboard category (SYMBOL\\_MAPPING):*\n"
    for item in uncategorized:
        msg += f"  • `{item['symbol']}` — {item['description'][:40]}\n"
        msg += f"     ${item['value']:,.0f}\n"
    msg += "\n📋 Add these to `portfolio_categories_mappings.py` and `Dashboard` manually.\n"
    return msg


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("AUTO-CATEGORIZE POSITIONS")
    print("=" * 60)
    print()

    print("🔍 Scanning IBKR positions against Dashboard categories...")
    uncategorized = find_uncategorized_positions()

    if uncategorized is None:
        msg = "❌ AUTO-CATEGORIZE: Failed to load positions from fetch-ibkr-positions.xlsx — check file and Positions sheet."
        print(f"  {msg}")
        send_telegram(msg)
        return
    elif not uncategorized:
        print("  ✅ All positions are categorized — no action needed")
    else:
        print(f"  ⚠️  Found {len(uncategorized)} uncategorized position(s):")
        for item in uncategorized:
            print(f"     • {item['symbol']} ({item['description'][:40]}) — ${item['value']:,.0f}")
        print()
        print("📱 Sending Telegram alert...")
        message = format_summary(uncategorized)
        if message and send_telegram(message):
            print("  ✅ Telegram sent")
        else:
            print("  ❌ Telegram failed")
        print()
        print("📋 Next step: add these tickers to portfolio_categories_mappings.py")
        print("   and to Dashboard in fetch-ibkr-positions-dashboard.xlsx")

    print()
    print("=" * 60)
    print("✅ Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
