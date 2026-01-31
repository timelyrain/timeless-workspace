#!/bin/bash
# Watchlist Auto-Update Scheduler with Sleep Prevention
# Runs every Sunday at 8 PM ET with caffeinate to prevent Mac sleep

# Navigate to project directory
cd /Users/hongkiatkoh/Developer/timeless-workspace

# Activate virtual environment
source .venv/bin/activate

# Run with caffeinate to keep Mac awake during execution
# -i: prevent idle sleep; -m: prevent system sleep; -u: user activity simulation
caffeinate -i -m -u -t 3600 python projects/watchlist-auto-updater.py

# Log completion with timestamp
echo "✅ Watchlist updated on $(date)" >> logs/watchlist-updates.log
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> logs/watchlist-updates.log
