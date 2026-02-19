#!/usr/bin/env python3
"""
Auto-Categorize Uncategorized Positions

Two independent sync operations run every time:

1. CASH COW SYNC (fetch-ibkr-positions-dashboard.xlsx → IncomeStrategy sheet)
   - Reads the canonical list of cash cow tickers from the IncomeStrategy sheet
   - Adds any missing tickers to 'cash_cow' in portfolio_categories_mappings.py
   - Removes tickers from 'cash_cow' that are no longer in the sheet
   - This is fully automatic — IncomeStrategy sheet is the single source of truth

2. ALPHA SYNC (fetch-ibkr-positions.xlsx vs dashboard sheets)
   - Reads all stock/ETF positions from fetch-ibkr-positions.xlsx
   - Loads all known tickers from dashboard sheets: GlobalETF, GrowthEngine, IncomeStrategy, Gold
   - Any IBKR position NOT found in any dashboard sheet → classified as 'alpha'
   - Adds new alpha positions and removes alpha positions no longer held
   - Sends Telegram confirmation so you can correct any wrong classifications

Usage:
    python auto-categorize-positions.py
"""

import os
import re
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
POSITIONS_FILE = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'
DASHBOARD_FILE = Path(__file__).parent / 'fetch-ibkr-positions-dashboard.xlsx'
MAPPINGS_FILE = Path(__file__).parent / 'portfolio_categories_mappings.py'


# =============================================================================
# DASHBOARD SHEET READERS
# =============================================================================

# Maps each dashboard sheet to its SYMBOL_MAPPING category
DASHBOARD_SHEET_MAP = {
    'GlobalETF':      'global_triads',
    'GrowthEngine':   'four_horsemen',
    'IncomeStrategy': 'cash_cow',
    'Gold':           'vault',
}


def load_dashboard_sheet_tickers(sheet_name):
    """Read ticker list (column 0, skip header row) from a dashboard sheet."""
    if not DASHBOARD_FILE.exists():
        print(f"❌ Dashboard file not found: {DASHBOARD_FILE}")
        return []
    try:
        df = pd.read_excel(DASHBOARD_FILE, sheet_name=sheet_name, header=None)
        tickers = df.iloc[1:, 0].dropna().astype(str).str.strip().tolist()
        return [t for t in tickers if t and t != 'nan']
    except Exception as e:
        print(f"❌ Error reading sheet '{sheet_name}': {e}")
        return []


def load_income_strategy_tickers():
    """Convenience wrapper — returns cash_cow canonical list."""
    return load_dashboard_sheet_tickers('IncomeStrategy')


def load_all_dashboard_tickers():
    """Return set of ALL tickers defined across all four dashboard sheets."""
    all_tickers = set()
    for sheet in DASHBOARD_SHEET_MAP:
        all_tickers.update(load_dashboard_sheet_tickers(sheet))
    return all_tickers


def sync_cash_cow(source):
    """
    Sync the cash_cow list in portfolio_categories_mappings.py with the
    IncomeStrategy sheet. Returns (source, added, removed) tuple.
    """
    income_tickers = load_income_strategy_tickers()
    if not income_tickers:
        print("  ⚠️  No tickers found in IncomeStrategy sheet — skipping cash_cow sync")
        return source, [], []

    # Parse current cash_cow list from source file
    pattern = r"(    'cash_cow': \[)(.*?)(    \])"
    match = re.search(pattern, source, re.DOTALL)
    if not match:
        print("  ⚠️  Could not find 'cash_cow' list in mappings file — skipping")
        return source, [], []

    current_block = match.group(2)
    # Extract currently listed symbols (ignore comment lines)
    current_symbols = set(re.findall(r"'([A-Z0-9]+)'", current_block))

    income_set = set(income_tickers)
    to_add = sorted(income_set - current_symbols)
    to_remove = sorted(current_symbols - income_set)

    if not to_add and not to_remove:
        print("  ✅ cash_cow already in sync with IncomeStrategy sheet")
        return source, [], []

    # Rebuild the cash_cow block from the canonical list
    comment_line = "        # Source of truth: fetch-ibkr-positions-dashboard.xlsx → IncomeStrategy sheet\n"
    # Group tickers in rows of 6 for readability
    ticker_lines = ""
    row = []
    for i, ticker in enumerate(income_tickers):
        row.append(f"'{ticker}'")
        if len(row) == 6 or i == len(income_tickers) - 1:
            ticker_lines += "        " + ", ".join(row) + ",\n"
            row = []

    new_block = f"    'cash_cow': [\n{comment_line}{ticker_lines}"
    source = source[:match.start()] + new_block + match.group(3) + source[match.end():]

    if to_add:
        print(f"  ➕ Added to cash_cow: {', '.join(to_add)}")
    if to_remove:
        print(f"  ➖ Removed from cash_cow: {', '.join(to_remove)}")

    return source, to_add, to_remove


# =============================================================================
# NEW POSITION SCAN — classify uncategorized positions from IBKR positions file
# =============================================================================

def get_all_categorized_symbols():
    """Get set of all symbols already in SYMBOL_MAPPING."""
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
        df_hk = pd.read_excel(POSITIONS_FILE, sheet_name='PositionsHK')
        df_al = pd.read_excel(POSITIONS_FILE, sheet_name='PositionsAL')
        df = pd.concat([df_hk, df_al], ignore_index=True)
        df = df[df['AssetClass'] == 'STK'].copy()
        # Deduplicate — keep first occurrence (same stock in both accounts)
        df = df.drop_duplicates(subset='Symbol', keep='first')
        return df
    except Exception as e:
        print(f"❌ Error loading positions: {e}")
        return None


def find_new_alpha_positions():
    """
    Alpha rule: any ticker held in fetch-ibkr-positions.xlsx that does NOT
    appear in any dashboard sheet (GlobalETF, GrowthEngine, IncomeStrategy, Gold)
    and is not already in SYMBOL_MAPPING → classify as 'alpha'.
    Also detects alpha positions no longer held (to remove from mapping).
    Returns (to_add, to_remove) lists of dicts.
    """
    dashboard_tickers = load_all_dashboard_tickers()
    categorized = get_all_categorized_symbols()  # Current state of mappings file

    positions = load_positions()
    if positions is None or positions.empty:
        return [], []

    held_symbols = set(positions['Symbol'].tolist())

    # Current alpha symbols in mappings
    current_alpha = set(SYMBOL_MAPPING.get('alpha', []))

    # New alpha = held + not in dashboard + not already mapped anywhere
    to_add = []
    for _, row in positions.iterrows():
        symbol = row['Symbol']
        if symbol not in dashboard_tickers and symbol not in categorized:
            to_add.append({
                'symbol': symbol,
                'description': str(row.get('Description', 'N/A')),
                'value': float(row.get('PositionValueUSD', 0) or 0),
                'suggested_category': 'alpha',
                'reason': '🎲 Not in any dashboard sheet → Alpha',
            })

    # Stale alpha = in alpha mapping but no longer held in IBKR positions
    # (only flag positions not in any dashboard sheet either — dashboard-defined
    #  symbols stay put even if not currently held)
    to_remove = [
        s for s in current_alpha
        if s not in held_symbols and s not in dashboard_tickers
    ]

    return to_add, to_remove


def add_symbols_to_mappings(source, to_add):
    """Insert new symbols into the correct category list in the source string."""
    added = []
    by_category = {}
    for item in to_add:
        by_category.setdefault(item['suggested_category'], []).append(item)

    for category, items in by_category.items():
        for item in items:
            symbol = item['symbol']
            description = item['description'][:50]
            new_line = f"        '{symbol}',    # Auto-added: {description}\n"
            pattern = rf"(    '{re.escape(category)}': \[.*?\n)(    \])"
            match = re.search(pattern, source, re.DOTALL)
            if match:
                source = source[:match.end(1)] + new_line + source[match.end(1):]
                added.append(item)
                print(f"  ✅ Added '{symbol}' → {category}")
            else:
                print(f"  ⚠️  Could not find '{category}' list — skipping '{symbol}'")
    return source, added


def remove_symbols_from_alpha(source, to_remove):
    """Remove stale symbols from the alpha list in the source string."""
    removed = []
    for symbol in to_remove:
        # Match the symbol line in the alpha list (handles both inline and own-line formats)
        pattern = rf"\s*'{re.escape(symbol)}'[^\n]*\n"
        # Only remove if it's inside the alpha block
        alpha_block_match = re.search(r"(    'alpha': \[)(.*?)(    \])", source, re.DOTALL)
        if alpha_block_match and f"'{symbol}'" in alpha_block_match.group(2):
            alpha_start = alpha_block_match.start(2)
            alpha_end = alpha_block_match.end(2)
            alpha_block = source[alpha_start:alpha_end]
            new_block = re.sub(rf"\s*'{re.escape(symbol)}'[^\n]*\n", '\n', alpha_block, count=1)
            source = source[:alpha_start] + new_block + source[alpha_end:]
            removed.append(symbol)
            print(f"  ➖ Removed '{symbol}' from alpha (no longer held)")
    return source, removed


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


def format_summary(cash_cow_added, cash_cow_removed, alpha_added, alpha_removed):
    """Build Telegram summary message for all changes made."""
    if not any([cash_cow_added, cash_cow_removed, alpha_added, alpha_removed]):
        return None

    msg = "🔄 *AUTO-CATEGORIZE: Mappings Updated*\n\n"

    if cash_cow_added or cash_cow_removed:
        msg += "*💰 Cash Cow (synced from IncomeStrategy sheet):*\n"
        if cash_cow_added:
            msg += f"  ➕ Added: {', '.join(f'`{s}`' for s in cash_cow_added)}\n"
        if cash_cow_removed:
            msg += f"  ➖ Removed: {', '.join(f'`{s}`' for s in cash_cow_removed)}\n"
        msg += "\n"

    if alpha_added or alpha_removed:
        msg += "*🎲 Alpha (positions not in any dashboard sheet):*\n"
        if alpha_added:
            for item in alpha_added:
                msg += f"  ➕ `{item['symbol']}` — {item['description'][:35]}\n"
                msg += f"     ${item['value']:,.0f}\n"
        if alpha_removed:
            msg += f"  ➖ Removed (no longer held): {', '.join(f'`{s}`' for s in alpha_removed)}\n"
        msg += "\n"
        if alpha_added:
            msg += "⚠️ *Review alpha additions — move to correct category if wrong*\n"

    return msg


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("AUTO-CATEGORIZE POSITIONS")
    print("=" * 60)
    print()

    source = MAPPINGS_FILE.read_text()
    any_changes = False

    # --- Step 1: Sync cash_cow from IncomeStrategy sheet ---
    print("💰 Step 1: Syncing cash_cow from IncomeStrategy sheet...")
    source, cc_added, cc_removed = sync_cash_cow(source)
    if cc_added or cc_removed:
        any_changes = True
    print()

    # --- Step 2: Sync alpha from IBKR positions vs dashboard sheets ---
    print("🎲 Step 2: Syncing alpha positions (IBKR positions vs dashboard sheets)...")
    alpha_to_add, alpha_to_remove = find_new_alpha_positions()
    alpha_added, alpha_removed = [], []

    if not alpha_to_add and not alpha_to_remove:
        print("  ✅ alpha already in sync")
    else:
        if alpha_to_add:
            print(f"  ⚠️  Found {len(alpha_to_add)} new alpha position(s):")
            for item in alpha_to_add:
                print(f"     • {item['symbol']} ({item['description'][:40]})")
            source, alpha_added = add_symbols_to_mappings(source, alpha_to_add)
            if alpha_added:
                any_changes = True
        if alpha_to_remove:
            print(f"  ⚠️  Found {len(alpha_to_remove)} stale alpha position(s) to remove:")
            for s in alpha_to_remove:
                print(f"     • {s}")
            source, alpha_removed = remove_symbols_from_alpha(source, alpha_to_remove)
            if alpha_removed:
                any_changes = True
    print()

    # --- Save if anything changed ---
    if any_changes:
        MAPPINGS_FILE.write_text(source)
        print(f"💾 Saved changes to portfolio_categories_mappings.py")
        print()
        print("📱 Sending Telegram confirmation...")
        message = format_summary(cc_added, cc_removed, alpha_added, alpha_removed)
        if message and send_telegram(message):
            print("  ✅ Telegram sent")
        else:
            print("  ❌ Telegram failed — file changes were still saved")
    else:
        print("✅ No changes needed — portfolio_categories_mappings.py is up to date")

    print()
    print("=" * 60)
    print("✅ Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
