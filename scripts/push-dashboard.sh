#!/bin/zsh
# Push updated dashboard xlsx to GitHub
# Usage: ./scripts/push-dashboard.sh

set -e
cd "$(dirname "$0")/.."

echo "📊 Pushing dashboard xlsx to GitHub..."

# Temporarily re-enable tracking
git update-index --no-assume-unchanged projects/fetch-ibkr-positions-dashboard.xlsx

# Stash the dashboard file, pull latest, then unstash
git stash push -m "dashboard-update" projects/fetch-ibkr-positions-dashboard.xlsx
git pull --rebase origin main
git stash pop

# Commit if changed
if git diff --quiet projects/fetch-ibkr-positions-dashboard.xlsx; then
  echo "✅ No changes — dashboard already up to date"
else
  git add projects/fetch-ibkr-positions-dashboard.xlsx
  git commit -m "Update IBKR positions dashboard spreadsheet"
  git push origin main
  echo "✅ Dashboard pushed"
fi

# Re-ignore local changes
git update-index --assume-unchanged projects/fetch-ibkr-positions-dashboard.xlsx
