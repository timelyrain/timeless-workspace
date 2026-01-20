# IBKR Position Fetcher Setup Guide

Automatically fetch your Interactive Brokers open positions and receive Telegram notifications.

## Setup Steps

### 1. Create IBKR Flex Query

1. Log into [IBKR Account Management](https://www.interactivebrokers.com/sso/Login)
2. Navigate to **Reports → Flex Queries → Custom Flex Queries**
3. Click **Create** → **Activity Flex Query**
4. Configure query:
   - **Name**: "Daily Open Positions"
   - **Sections**: Select **Open Positions**
   - **Format**: CSV
   - **Model**: Leave default
   - **Period**: Today
5. Click **Save**
6. **Note your Query ID** (e.g., `123456`)

### 2. Get FlexWeb Service Token

1. In IBKR Account Management, go to **Settings → General**
2. Find **FlexWeb Service** section
3. Click **Generate Token**
4. **Copy and save the token** (36 characters)

### 3. Configure GitHub Secrets

Add these secrets in your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `IBKR_FLEX_TOKEN_HK` | FlexWeb Service token (HK) | `123456789012345678901234567890123456` |
| `IBKR_QUERY_ID_HK` | Flex Query ID (HK) | `123456` |
| `IBKR_FLEX_TOKEN_AL` | FlexWeb Service token (AL) | `123456789012345678901234567890123456` |
| `IBKR_QUERY_ID_AL` | Flex Query ID (AL) | `789012` |
| `TELEGRAM_TOKEN` | Your Telegram bot token | `8470489967:AAFBeqaGf...` |
| `CHAT_ID` | Your Telegram chat ID | `6482242525` |

### 4. Test Locally (Optional)

Update `projects/.env`:
```bash
IBKR_FLEX_TOKEN_HK=your_token_here
IBKR_QUERY_ID_HK=your_query_id_here
IBKR_FLEX_TOKEN_AL=your_token_here
IBKR_QUERY_ID_AL=your_query_id_here
TELEGRAM_TOKEN=8470489967:AAFBeqaGfoRa2pKyZlNFFJ1O2fX0RepGKRI
CHAT_ID=6482242525
```

Run the script:
```bash
cd projects
python fetch-ibkr-positions.py
```

### 5. Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. Find **"Fetch IBKR Positions"** workflow
3. Click **"Enable workflow"** if needed
4. Workflow runs automatically at **9:00 AM Malaysia Time** daily
5. Or click **"Run workflow"** to test manually

## Features

✅ **Dual Account Support** - Fetches HK and AL accounts simultaneously  
✅ **Automated Daily Sync** - Runs at 9:00 AM MYT (1:00 AM UTC)  
✅ **Telegram Notifications** - Success/failure alerts with position breakdown  
✅ **Excel Output** - `fetch-ibkr-positions.xlsx` with 3 sheets:
   - **PositionsHK**: HK account holdings
   - **PositionsAL**: AL account holdings
   - **Metadata**: Update timestamp and query info  
✅ **GitHub Artifacts** - 30-day retention of Excel files  
✅ **Error Handling** - Robust retry logic and notifications  

## Telegram Message Format

**Success:**
```
✅ IBKR Positions Updated

📊 Total Positions: 45
   • HK Account: 30
   • AL Account: 15
📈 Symbols: AAPL, MSFT, GOOGL, AMZN, NVDA +10 more
🕐 Updated: 2026-01-14 09:00:15
📁 File: fetch-ibkr-positions.xlsx

Run from: GitHub Actions
```

**Failure:**
```
❌ IBKR Position Update Failed

⚠️ Error occurred while fetching positions
🕐 Time: 2026-01-14 09:00:15

Please check GitHub Actions logs for details.
```

## Troubleshooting

### "IBKR_FLEX_TOKEN not configured"
- Verify GitHub Secrets are set correctly
- Token must be exactly 36 characters

### "Report not ready after X seconds"
- IBKR servers may be slow during peak hours
- Try manual trigger outside market hours

### "No positions found"
- Check if you have open positions in your account
- Verify Flex Query includes "Open Positions" section

### Telegram not working
- Verify bot token and chat ID
- Test by sending: `curl -X POST "https://api.telegram.org/bot<TOKEN>/getMe"`

## Manual Trigger

Run workflow manually:
1. Go to **Actions** → **Fetch IBKR Positions**
2. Click **Run workflow** → **Run workflow**
3. Wait 30-60 seconds for completion
4. Check Telegram for notification

## Schedule

- **Default**: Daily at 9:00 AM Malaysia Time (MYT, UTC+8)
- **Cron**: `0 1 * * *` (1:00 AM UTC)
- **Change schedule**: Edit `.github/workflows/fetch-ibkr-positions.yml`

## Files Created

```
projects/
├── fetch-ibkr-positions.py      # Main script
├── fetch-ibkr-positions.xlsx    # Output file (local only)
└── .env                          # Local config (gitignored)

.github/workflows/
└── fetch-ibkr-positions.yml     # GitHub Actions workflow
```

## Support

Questions? Check:
- [IBKR Flex Web Service Guide](https://www.interactivebrokers.com/en/software/am/am/reports/flex_web_service_version_3.htm)
- GitHub Actions logs for detailed error messages
