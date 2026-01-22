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
   IBKR_FLEX_TOKEN_HK=your_token_here
   IBKR_QUERY_ID_HK=your_query_id_here
   IBKR_FLEX_TOKEN_AL=your_token_here
   IBKR_QUERY_ID_AL=your_query_id_here

USAGE:
python fetch-ibkr-positions.py

OUTPUT:
- Creates/updates: daily-open-positions.xlsx
- Sheet name: "Positions"
- Includes timestamp of last update
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from io import StringIO

# Load environment variables
load_dotenv()

# Configuration - HK Account
IBKR_FLEX_TOKEN_HK = os.getenv('IBKR_FLEX_TOKEN_HK')
IBKR_QUERY_ID_HK = os.getenv('IBKR_QUERY_ID_HK')
IBKR_CASH_QUERY_ID_HK = os.getenv('IBKR_CASH_QUERY_ID_HK')

# Configuration - AL Account
IBKR_FLEX_TOKEN_AL = os.getenv('IBKR_FLEX_TOKEN_AL')
IBKR_QUERY_ID_AL = os.getenv('IBKR_QUERY_ID_AL')
IBKR_CASH_QUERY_ID_AL = os.getenv('IBKR_CASH_QUERY_ID_AL')

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
EXCEL_FILE = Path(__file__).parent / 'fetch-ibkr-positions.xlsx'

# IBKR API Endpoints
REQUEST_URL = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest'
STATEMENT_URL = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement'


def validate_config(account_name, flex_token, query_id):
    """Validate that required configuration is present"""
    if not flex_token or flex_token == 'your_flex_token_here':
        print(f"❌ ERROR: IBKR_FLEX_TOKEN_{account_name} not configured in .env file")
        print("   Get token from: IBKR Account Management → Settings → FlexWeb Service")
        return False
    
    if not query_id or query_id == 'your_query_id_here':
        print(f"❌ ERROR: IBKR_QUERY_ID_{account_name} not configured in .env file")
        print("   Get Query ID from: IBKR Reports → Flex Queries")
        return False
    
    print(f"✅ Configuration validated for {account_name} account")
    return True


def request_flex_report(account_name, flex_token, query_id):
    """
    Step 1: Request flex report generation
    Returns: Reference code for retrieving the report
    """
    print(f"\n📊 Requesting Flex Query report from IBKR ({account_name})...")
    
    params = {
        't': flex_token,
        'q': query_id,
        'v': '3'  # API version
    }
    
    try:
        response = requests.get(REQUEST_URL, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        content = response.text
        
        # Check for errors
        if '<Status>Fail</Status>' in content:
            error_code = content.split('<ErrorCode>')[1].split('</ErrorCode>')[0] if '<ErrorCode>' in content else 'Unknown'
            error_msg = content.split('<ErrorMessage>')[1].split('</ErrorMessage>')[0] if '<ErrorMessage>' in content else 'Unknown error'
            print(f"❌ IBKR API Error {error_code}: {error_msg}")
            sys.exit(1)
        
        # Extract reference code
        if '<ReferenceCode>' in content:
            ref_code = content.split('<ReferenceCode>')[1].split('</ReferenceCode>')[0]
            print(f"✅ Report requested successfully (Reference: {ref_code})")
            return ref_code
        else:
            print(f"❌ Unexpected response format:")
            print(content)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


def fetch_flex_report(account_name, flex_token, reference_code, max_retries=20, retry_delay=5):
    """
    Step 2: Fetch the generated flex report (with retries)
    IBKR takes a few seconds to generate the report
    
    Returns: CSV data as string
    """
    print(f"\n⏳ Waiting for report generation ({account_name}, max {max_retries * retry_delay}s)...")
    
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


def parse_csv_to_dataframe(csv_data, account_name):
    """
    Parse CSV data into pandas DataFrame
    """
    if not csv_data:
        print(f"⚠️  No data to parse for {account_name}")
        return None
    
    try:
        # Use StringIO to read CSV from string
        df = pd.read_csv(StringIO(csv_data))
        
        # Convert Symbol column to string to ensure consistent matching with Excel formulas
        if 'Symbol' in df.columns:
            df['Symbol'] = df['Symbol'].astype(str)
        
        # Add PositionValueUSD column
        if 'PositionValue' in df.columns and 'FXRateToBase' in df.columns:
            df['PositionValueUSD'] = df['PositionValue'] * df['FXRateToBase']
            print(f"✅ Parsed {len(df)} positions for {account_name} (added PositionValueUSD)")
        else:
            print(f"✅ Parsed {len(df)} positions for {account_name}")
            print(f"   ⚠️  Warning: PositionValue or FXRateToBase column not found")
        
        return df
    except Exception as e:
        print(f"❌ Error parsing CSV for {account_name}: {e}")
        print("CSV preview:")
        print(csv_data[:500])
        return None


def fetch_and_merge_cash_balances(df_positions, account_name, flex_token, cash_query_id):
    """
    Fetch cash balances and merge with positions data as 'CASH' AssetClass rows
    """
    if not cash_query_id:
        print(f"   ⚠️  No cash query ID configured for {account_name}, skipping cash fetch")
        return df_positions
    
    print(f"\n💵 Fetching cash balances for {account_name}...")
    
    # Request cash report
    reference_code = request_flex_report(f"{account_name}-CASH", flex_token, cash_query_id)
    if not reference_code:
        print(f"   ⚠️  Failed to request cash report for {account_name}")
        return df_positions
    
    # Fetch cash report
    csv_data = fetch_flex_report(f"{account_name}-CASH", flex_token, reference_code)
    if not csv_data:
        print(f"   ⚠️  No cash data received for {account_name}")
        return df_positions
    
    try:
        # Parse cash CSV
        df_cash = pd.read_csv(StringIO(csv_data))
        
        # Cash report has: EndingCash column with single USD total
        if len(df_cash) == 0:
            print(f"   ℹ️  No cash balances found for {account_name}")
            return df_positions
        
        # Get total cash in USD (single row with EndingCash column)
        if 'EndingCash' in df_cash.columns:
            total_cash_usd = float(df_cash['EndingCash'].iloc[0]) if len(df_cash) > 0 else 0
        elif 'endingcash' in df_cash.columns:
            total_cash_usd = float(df_cash['endingcash'].iloc[0]) if len(df_cash) > 0 else 0
        else:
            print(f"   ⚠️  EndingCash column not found in cash report for {account_name}")
            print(f"   Available columns: {df_cash.columns.tolist()}")
            return df_positions
        
        # Skip if balance is zero or very small
        if abs(total_cash_usd) < 0.01:
            print(f"   ℹ️  No significant cash balance for {account_name}")
            return df_positions
        
        # Create a single cash row matching positions DataFrame schema
        cash_row = {
            'ClientAccountID': df_positions['ClientAccountID'].iloc[0] if len(df_positions) > 0 else account_name,
            'CurrencyPrimary': 'USD',
            'FXRateToBase': 1.0,
            'AssetClass': 'CASH',
            'SubCategory': 'Cash',
            'Symbol': 'USD',
            'Description': 'Cash Balance (Total USD)',
            'Multiplier': 1,
            'Strike': None,
            'Expiry': None,
            'Put/Call': None,
            'ReportDate': df_positions['ReportDate'].iloc[0] if len(df_positions) > 0 else datetime.now().strftime('%Y-%m-%d'),
            'Quantity': total_cash_usd,
            'MarkPrice': 1.0,
            'PositionValue': total_cash_usd,
            'OpenPrice': None,
            'CostBasisPrice': None,
            'CostBasisMoney': None,
            'FifoPnlUnrealized': 0,
            'Side': 'Long',
            'PositionValueUSD': total_cash_usd
        }
        
        df_cash_formatted = pd.DataFrame([cash_row])
        # Merge with positions
        df_merged = pd.concat([df_positions, df_cash_formatted], ignore_index=True)
        print(f"   ✅ Added cash balance: ${total_cash_usd:,.2f} USD")
        return df_merged
            
    except Exception as e:
        print(f"   ⚠️  Error processing cash data for {account_name}: {e}")
        import traceback
        traceback.print_exc()
        return df_positions


def update_excel_file(df_hk, df_al):
    """
    Update Excel file with new position data for both accounts
    Creates file if it doesn't exist
    """
    print(f"\n📝 Updating Excel file: {EXCEL_FILE.name}")
    
    try:
        # Add metadata
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create a writer object
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
            # Write HK positions data
            if df_hk is not None and len(df_hk) > 0:
                df_hk.to_excel(writer, sheet_name='PositionsHK', index=False)
                print(f"   ✅ Wrote {len(df_hk)} HK positions")
            
            # Write AL positions data
            if df_al is not None and len(df_al) > 0:
                df_al.to_excel(writer, sheet_name='PositionsAL', index=False)
                print(f"   ✅ Wrote {len(df_al)} AL positions")
            
            # Write metadata
            metadata_data = {
                'Last Updated': [timestamp],
                'HK Positions': [len(df_hk) if df_hk is not None else 0],
                'AL Positions': [len(df_al) if df_al is not None else 0],
                'HK Query ID': [IBKR_QUERY_ID_HK],
                'AL Query ID': [IBKR_QUERY_ID_AL]
            }
            metadata = pd.DataFrame(metadata_data)
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        print(f"✅ Excel file updated successfully")
        print(f"   Location: {EXCEL_FILE.absolute()}")
        print(f"   Timestamp: {timestamp}")
        
        # Display summary
        print(f"\n📊 Position Summary:")
        if df_hk is not None and len(df_hk) > 0:
            print(f"   HK Account: {len(df_hk)} positions")
            if 'Symbol' in df_hk.columns:
                symbols_hk = df_hk['Symbol'].astype(str).unique()[:5]
                print(f"      Symbols: {', '.join(symbols_hk)}")
                if len(df_hk['Symbol'].unique()) > 5:
                    print(f"      ... and {len(df_hk['Symbol'].unique()) - 5} more")
        
        if df_al is not None and len(df_al) > 0:
            print(f"   AL Account: {len(df_al)} positions")
            if 'Symbol' in df_al.columns:
                symbols_al = df_al['Symbol'].astype(str).unique()[:5]
                print(f"      Symbols: {', '.join(symbols_al)}")
                if len(df_al['Symbol'].unique()) > 5:
                    print(f"      ... and {len(df_al['Symbol'].unique()) - 5} more")
        
        # Prepare return data for telegram
        total_positions = 0
        all_symbols = []
        if df_hk is not None:
            total_positions += len(df_hk)
            if 'Symbol' in df_hk.columns:
                all_symbols.extend(df_hk['Symbol'].astype(str).unique().tolist())
        if df_al is not None:
            total_positions += len(df_al)
            if 'Symbol' in df_al.columns:
                all_symbols.extend(df_al['Symbol'].astype(str).unique().tolist())
        
        return timestamp, total_positions, all_symbols
        
    except Exception as e:
        print(f"❌ Error updating Excel file: {e}")
        return None, 0, []


def send_telegram_notification(success=True, timestamp=None, position_count=0, symbols=None, hk_count=0, al_count=0):
    """
    Send Telegram notification about position update
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  Telegram credentials not configured, skipping notification")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        if success:
            # Build symbol list preview
            symbol_preview = ""
            if symbols and len(symbols) > 0:
                symbol_list = ', '.join(symbols[:8])
                if len(symbols) > 8:
                    symbol_list += f" +{len(symbols) - 8} more"
                symbol_preview = f"\n📈 Symbols: {symbol_list}\n"
            
            message = (
                f"✅ *IBKR Positions Updated*\n\n"
                f"📊 Total Positions: {position_count}\n"
                f"   • HK Account: {hk_count}\n"
                f"   • AL Account: {al_count}\n"
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


def main():
    """Main execution flow"""
    print("=" * 70)
    print("IBKR FLEX QUERY TO EXCEL UPDATER (HK + AL)")
    print("=" * 70)
    
    try:
        df_hk = None
        df_al = None
        
        # ===== STEP 1: Fetch all position reports first =====
        print("\n" + "=" * 70)
        print("FETCHING HK ACCOUNT POSITIONS")
        print("=" * 70)
        
        if validate_config("HK", IBKR_FLEX_TOKEN_HK, IBKR_QUERY_ID_HK):
            reference_code_hk = request_flex_report("HK", IBKR_FLEX_TOKEN_HK, IBKR_QUERY_ID_HK)
            
            if reference_code_hk:
                csv_data_hk = fetch_flex_report("HK", IBKR_FLEX_TOKEN_HK, reference_code_hk)
                
                if csv_data_hk:
                    df_hk = parse_csv_to_dataframe(csv_data_hk, "HK")
                else:
                    print("⚠️  No HK positions data received")
            else:
                print("⚠️  Failed to request HK report")
        else:
            print("⚠️  HK account not configured, skipping")
        
        # ===== Process AL Account =====
        print("\n" + "=" * 70)
        print("FETCHING AL ACCOUNT POSITIONS")
        print("=" * 70)
        
        if validate_config("AL", IBKR_FLEX_TOKEN_AL, IBKR_QUERY_ID_AL):
            reference_code_al = request_flex_report("AL", IBKR_FLEX_TOKEN_AL, IBKR_QUERY_ID_AL)
            
            if reference_code_al:
                csv_data_al = fetch_flex_report("AL", IBKR_FLEX_TOKEN_AL, reference_code_al)
                
                if csv_data_al:
                    df_al = parse_csv_to_dataframe(csv_data_al, "AL")
                else:
                    print("⚠️  No AL positions data received")
            else:
                print("⚠️  Failed to request AL report")
        else:
            print("⚠️  AL account not configured, skipping")
        
        # ===== STEP 2: Now fetch cash balances after all positions complete =====
        print("\n" + "=" * 70)
        print("FETCHING CASH BALANCES")
        print("=" * 70)
        
        # Fetch HK cash (positions already fully complete at this point)
        if df_hk is not None and IBKR_CASH_QUERY_ID_HK:
            print("\n💵 Fetching HK cash balance...")
            df_hk = fetch_and_merge_cash_balances(df_hk, "HK", IBKR_FLEX_TOKEN_HK, IBKR_CASH_QUERY_ID_HK)
        
        # Fetch AL cash
        if df_al is not None and IBKR_CASH_QUERY_ID_AL:
            print("\n💵 Fetching AL cash balance...")
            df_al = fetch_and_merge_cash_balances(df_al, "AL", IBKR_FLEX_TOKEN_AL, IBKR_CASH_QUERY_ID_AL)
        
        # ===== Update Excel File =====
        if df_hk is None and df_al is None:
            print("\n❌ No position data available from either account")
            send_telegram_notification(success=False)
            sys.exit(1)
        
        # Update Excel with both accounts
        timestamp, total_positions, all_symbols = update_excel_file(df_hk, df_al)
        
        # Send Telegram notification
        hk_count = len(df_hk) if df_hk is not None else 0
        al_count = len(df_al) if df_al is not None else 0
        
        send_telegram_notification(
            success=True, 
            timestamp=timestamp, 
            position_count=total_positions,
            symbols=all_symbols,
            hk_count=hk_count,
            al_count=al_count
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
