"""
IBKR Flex Query to Excel Updater
=================================

Fetches open positions from Interactive Brokers via Flex Query API
and updates an Excel file with the latest data.

SETUP:
1. Create Flex Query in IBKR Account Management
   - Reports → Flex Queries → Create → Activity Flex Query
   - Add sections: Open Positions
   - Set format: CSV
   - Note your Query ID

2. Get Flex Web Service Token
   - Settings → General → FlexWeb Service
   - Generate token and note it

3. Add to .env file:
   IBKR_FLEX_TOKEN=your_token_here
   IBKR_QUERY_ID=your_query_id_here
   IBKR_CASH_QUERY_ID=your_cash_query_id_here

USAGE:
python fetch-ibkr-positions.py

OUTPUT:
- Creates/updates: fetch-ibkr-positions.xlsx
- Sheet name: "Positions"
- Includes timestamp of last update
"""

import os
import sys
import time
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from io import StringIO

# Load environment variables
load_dotenv()

# Configuration
IBKR_FLEX_TOKEN = os.getenv('IBKR_FLEX_TOKEN')
IBKR_QUERY_ID = os.getenv('IBKR_QUERY_ID')
IBKR_CASH_QUERY_ID = os.getenv('IBKR_CASH_QUERY_ID')

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
EXCEL_FILE = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'

# IBKR API Endpoints
REQUEST_URL = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest'
STATEMENT_URL = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement'


def validate_config(flex_token, query_id):
    """Validate that required configuration is present"""
    if not flex_token or flex_token == 'your_flex_token_here':
        print("❌ ERROR: IBKR_FLEX_TOKEN not configured in .env file")
        print("   Get token from: IBKR Account Management → Settings → FlexWeb Service")
        return False

    if not query_id or query_id == 'your_query_id_here':
        print("❌ ERROR: IBKR_QUERY_ID not configured in .env file")
        print("   Get Query ID from: IBKR Reports → Flex Queries")
        return False

    print("✅ Configuration validated")
    return True


def request_flex_report(label, flex_token, query_id):
    """
Step 1: Request flex report generation
    Returns: Reference code for retrieving the report
    """
    # Transient IBKR errors that resolve with a retry
    RETRYABLE_CODES = {'1001', '1003', '1004'}
    max_request_retries = 5
    request_retry_delay = 30  # seconds between retries

    for attempt in range(1, max_request_retries + 1):
        print(f"\n📊 Requesting Flex Query report from IBKR ({label})... (attempt {attempt}/{max_request_retries})")

        params = {
            't': flex_token,
            'q': query_id,
            'v': '3'  # API version
        }

        try:
            response = requests.get(REQUEST_URL, params=params, timeout=30)
            response.raise_for_status()

            content = response.text

            # Check for errors
            if '<Status>Fail</Status>' in content:
                error_code = content.split('<ErrorCode>')[1].split('</ErrorCode>')[0] if '<ErrorCode>' in content else 'Unknown'
                error_msg = content.split('<ErrorMessage>')[1].split('</ErrorMessage>')[0] if '<ErrorMessage>' in content else 'Unknown error'
                print(f"❌ IBKR API Error {error_code}: {error_msg}")
                if error_code == '1002':
                    print("🔑 TOKEN/AUTH ERROR — check IBKR_FLEX_TOKEN in GitHub Secrets (Settings → Secrets → Actions)")
                    print("   Token may have expired or been regenerated in IBKR Account Management → Settings → FlexWeb Service")
                    return None
                if error_code in RETRYABLE_CODES and attempt < max_request_retries:
                    print(f"⏳ Transient error — retrying in {request_retry_delay}s...")
                    time.sleep(request_retry_delay)
                    continue
                return None

            # Extract reference code
            if '<ReferenceCode>' in content:
                ref_code = content.split('<ReferenceCode>')[1].split('</ReferenceCode>')[0]
                print(f"✅ Report requested successfully (Reference: {ref_code})")
                return ref_code
            else:
                print("❌ Unexpected response format:")
                print(content)
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            if attempt < max_request_retries:
                print(f"⏳ Retrying in {request_retry_delay}s...")
                time.sleep(request_retry_delay)
            else:
                return None

    return None


def fetch_flex_report(label, flex_token, reference_code, max_retries=20, retry_delay=5):
    """
    Step 2: Fetch the generated flex report (with retries)
    IBKR takes a few seconds to generate the report

    Returns: CSV data as string
    """
    print(f"\n⏳ Waiting for report generation ({label}, max {max_retries * retry_delay}s)...")

    params = {
        't': flex_token,
        'q': reference_code,
        'v': '3'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(STATEMENT_URL, params=params, timeout=30)
            response.raise_for_status()
            content = response.text

            # Check if this is CSV data (starts with quotes or field names)
            if content.startswith('"') or content.startswith('ClientAccountID'):
                print(f"✅ Report generated successfully (attempt {attempt + 1})")
                return content

            # Check if report is ready (XML response)
            if '<Status>Success</Status>' in content:
                print(f"✅ Report generated successfully (attempt {attempt + 1})")

                # Extract CSV data (everything after the XML header)
                if '</FlexStatementResponse>' in content:
                    csv_data = content.split('</FlexStatementResponse>')[1].strip()
                    if csv_data:
                        return csv_data
                    else:
                        print("⚠️  Report is empty - no open positions?")
                        return None
                else:
                    return content  # Entire response is CSV

            # Check if still processing
            if '<Status>Warn</Status>' in content or 'Statement generation in progress' in content:
                print(f"   Attempt {attempt + 1}/{max_retries} - Still generating...")
                time.sleep(retry_delay)
                continue

            # Check for errors
            if '<Status>Fail</Status>' in content:
                error_msg = content.split('<ErrorMessage>')[1].split('</ErrorMessage>')[0] if '<ErrorMessage>' in content else 'Unknown error'
                print(f"❌ Error retrieving report: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None

    print(f"❌ Timeout: Report not ready after {max_retries * retry_delay} seconds")
    return None


def parse_csv_to_dataframe(csv_data):
    """
    Parse CSV data into pandas DataFrame
    """
    if not csv_data:
        print("⚠️  No data to parse")
        return None

    try:
        df = pd.read_csv(StringIO(csv_data))

        # Convert Symbol column to string for consistent Excel formula matching
        if 'Symbol' in df.columns:
            df['Symbol'] = df['Symbol'].astype(str)

        # Add PositionValueUSD column if possible
        if 'PositionValue' in df.columns and 'FXRateToBase' in df.columns:
            df['PositionValueUSD'] = df['PositionValue'] * df['FXRateToBase']
            print(f"✅ Parsed {len(df)} positions (added PositionValueUSD)")
        else:
            print(f"✅ Parsed {len(df)} positions")
            print("   ⚠️  Warning: PositionValue or FXRateToBase column not found")

        return df
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        print(f"CSV preview: {csv_data[:500]}")
        return None


def fetch_cash_balance(flex_token, cash_query_id):
    """
    Fetch cash balance and return as a simple dollar amount
    """
    if not cash_query_id:
        print("   ⚠️  No cash query ID configured, skipping cash fetch")
        return 0.0

    print("\n💵 Fetching cash balance...")

    reference_code = request_flex_report("CASH", flex_token, cash_query_id)
    if not reference_code:
        print("   ⚠️  Failed to request cash report")
        return 0.0

    csv_data = fetch_flex_report("CASH", flex_token, reference_code)
    if not csv_data:
        print("   ⚠️  No cash data received")
        return 0.0

    try:
        df_cash = pd.read_csv(StringIO(csv_data))

        if len(df_cash) == 0:
            print("   ℹ️  No cash balances found")
            return 0.0

        # Get total cash in USD (case-insensitive column lookup)
        for col in ['EndingCash', 'endingcash']:
            if col in df_cash.columns:
                total_cash_usd = float(df_cash[col].iloc[0])
                print(f"   ✅ Cash balance: ${total_cash_usd:,.2f} USD")
                return total_cash_usd

        print("   ⚠️  EndingCash column not found in cash report")
        print(f"   Available columns: {df_cash.columns.tolist()}")
        return 0.0

    except Exception as e:
        print(f"   ⚠️  Error processing cash data: {e}")
        return 0.0


def update_excel_file(df, cash):
    """
    Update Excel file with new position data.
    Creates file if it doesn't exist.
    """
    print(f"\n📝 Updating Excel file: {EXCEL_FILE.name}")

    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
            stocks_total = df['PositionValueUSD'].sum() if df is not None else 0.0
            grand_total = stocks_total + cash

            # Write positions data
            if df is not None:
                df.to_excel(writer, sheet_name='Positions', index=False)
                print(f"   ✅ Wrote {len(df)} positions")

            # Summary sheet
            summary_data = {
                'Category': ['Positions Value', 'Cash Balance', 'Total'],
                'Amount': [f'${stocks_total:,.2f}', f'${cash:,.2f}', f'${grand_total:,.2f}']
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            print("   ✅ Wrote Summary sheet")

            # Metadata sheet
            metadata_data = {
                'Last Updated': [timestamp],
                'Positions': [len(df) if df is not None else 0],
                'Query ID': [IBKR_QUERY_ID]
            }
            pd.DataFrame(metadata_data).to_excel(writer, sheet_name='Metadata', index=False)

        print("✅ Excel file updated successfully")
        print(f"   Location: {EXCEL_FILE.absolute()}")
        print(f"   Timestamp: {timestamp}")

        position_count = len(df) if df is not None else 0
        all_symbols = []
        if df is not None and 'Symbol' in df.columns:
            all_symbols = df['Symbol'].astype(str).unique().tolist()

        print(f"\n📊 Position Summary: {position_count} positions")
        if all_symbols:
            preview = ', '.join(all_symbols[:5])
            if len(all_symbols) > 5:
                preview += f" ... and {len(all_symbols) - 5} more"
            print(f"   Symbols: {preview}")

        return timestamp, position_count, all_symbols

    except Exception as e:
        print(f"❌ Error updating Excel file: {e}")
        return None, 0, []


def send_telegram_notification(success=True, timestamp=None, position_count=0, symbols=None):
    """
    Send Telegram notification about position update
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  Telegram credentials not configured, skipping notification")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        if success:
            symbol_preview = ""
            if symbols and len(symbols) > 0:
                symbol_list = ', '.join(symbols[:8])
                if len(symbols) > 8:
                    symbol_list += f" +{len(symbols) - 8} more"
                symbol_preview = f"\n📈 Symbols: {symbol_list}\n"

            message = (
                f"✅ *IBKR Positions Updated*\n\n"
                f"📊 Total Positions: {position_count}\n"
                f"{symbol_preview}"
                f"🕐 Updated: {timestamp}\n"
                f"📁 File: fetch-ibkr-positions.xlsx\n\n"
                f"_Run from: {os.environ.get('GITHUB_ACTIONS', 'Local')}_"
            )
        else:
            message = (
                f"❌ *IBKR Position Update Failed*\n\n"
                f"⚠️ Error occurred while fetching positions\n"
                f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Please check logs for details."
            )

        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Telegram notification sent")
        else:
            print(f"⚠️  Telegram notification failed: {response.status_code}")

    except Exception as e:
        print(f"⚠️  Error sending Telegram notification: {e}")


def write_sleeve_totals_json(df, cash):
    """
    Calculate category totals from positions data and write to sleeve_totals.json.
    This sidecar file is read by instituitional-risk-signal.py instead of relying
    on stale cached formula values in fetch-ibkr-positions-dashboard.xlsx.
    Categories match Dashboard column B (see portfolio_categories_mappings.py).
    """
    try:
        from portfolio_categories_mappings import SYMBOL_MAPPING

        category_totals = {cat: 0.0 for cat in SYMBOL_MAPPING}
        category_totals['cash'] = cash

        if df is not None:
            for _, row in df.iterrows():
                symbol = str(row.get('Symbol', '')).strip()
                value = float(row.get('PositionValueUSD', 0) or 0)
                asset_class = str(row.get('AssetClass', '')).strip()

                # Skip options — not tracked in Dashboard categories
                if asset_class in ('OPT', 'FOP'):
                    continue

                # Match against category symbol lists (first match wins)
                for cat, symbols in SYMBOL_MAPPING.items():
                    if cat == 'cash':
                        continue
                    if symbol in symbols:
                        category_totals[cat] += value
                        break

        grand_total = sum(category_totals.values())

        output = {
            'timestamp': datetime.now().isoformat(),
            'sleeve_totals_usd': category_totals,
            'grand_total_usd': grand_total,
        }

        json_path = Path(__file__).parent / 'sleeve_totals.json'
        with open(json_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n📋 Category totals written to sleeve_totals.json")
        for cat, val in category_totals.items():
            pct = (val / grand_total * 100) if grand_total > 0 else 0
            print(f"   {cat}: ${val:,.0f} ({pct:.1f}%)")
        print(f"   TOTAL: ${grand_total:,.0f}")

    except Exception as e:
        print(f"⚠️  Could not write sleeve_totals.json: {e}")


def main():
    """Main execution flow"""
    print("=" * 70)
    print("IBKR FLEX QUERY TO EXCEL UPDATER")
    print("=" * 70)

    try:
        df = None

        # ===== STEP 1: Fetch positions =====
        print("\n" + "=" * 70)
        print("FETCHING POSITIONS")
        print("=" * 70)

        if validate_config(IBKR_FLEX_TOKEN, IBKR_QUERY_ID):
            reference_code = request_flex_report("POSITIONS", IBKR_FLEX_TOKEN, IBKR_QUERY_ID)
            if reference_code:
                csv_data = fetch_flex_report("POSITIONS", IBKR_FLEX_TOKEN, reference_code)
                if csv_data:
                    df = parse_csv_to_dataframe(csv_data)

        # ===== STEP 2: Fetch cash balance =====
        if df is not None:
            print("\n⏳ Waiting 5 seconds before cash query to avoid rate limiting...")
            time.sleep(5)

        print("\n" + "=" * 70)
        print("FETCHING CASH BALANCE")
        print("=" * 70)

        cash = fetch_cash_balance(IBKR_FLEX_TOKEN, IBKR_CASH_QUERY_ID) if df is not None else 0.0

        # ===== Update Excel File =====
        if df is None:
            print("\n❌ No position data available")
            print("⚠️  IBKR statements not available — skipping update (will retry tomorrow)")
            send_telegram_notification(success=False)
            sys.exit(0)  # Exit 0 so GitHub Action doesn't fail red on transient IBKR errors

        timestamp, total_positions, all_symbols = update_excel_file(df, cash)

        # Write sleeve totals sidecar JSON for instituitional-risk-signal.py
        write_sleeve_totals_json(df, cash)

        send_telegram_notification(
            success=True,
            timestamp=timestamp,
            position_count=total_positions,
            symbols=all_symbols
        )

        print("\n" + "=" * 70)
        print("✅ COMPLETE - Excel file updated with latest IBKR positions")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        send_telegram_notification(success=False)
        sys.exit(1)


if __name__ == '__main__':
    main()
