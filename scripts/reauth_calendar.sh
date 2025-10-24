#!/usr/bin/env bash
# Re-authorize Google Calendar API quickly by deleting the local OAuth token and launching a flow
# Usage:
#   bash scripts/reauth_calendar.sh
# Notes:
# - This removes only the local refresh/access token at local_data/calendar_token.json
# - Your credentials file (local_data/calendar_credentials.json) must exist
# - A browser window will open to complete OAuth consent

set -euo pipefail

TOKEN_PATH="local_data/calendar_token.json"
CREDENTIALS_PATH="local_data/calendar_credentials.json"

if [[ ! -f "$CREDENTIALS_PATH" ]]; then
  echo "❌ Missing Calendar credentials: $CREDENTIALS_PATH"
  echo "   Download OAuth client credentials (Desktop app) from Google Cloud Console"
  echo "   and save them as local_data/calendar_credentials.json"
  exit 1
fi

echo "🔐 Re-authorizing Google Calendar API access..."
echo "🗑️  Removing Calendar token: $TOKEN_PATH"
rm -f "$TOKEN_PATH"

echo "ℹ️  Note: Gmail token is kept separate (using gmail_token.json)"
echo "    If you need to reauth Gmail API, run: bash scripts/reauth_gmail.sh"

# Run calendar export to trigger re-auth
if [[ -f "get_calendar_data.py" ]]; then
  python3 get_calendar_data.py
else
  echo "❌ Could not find an entry script to trigger Calendar auth (get_calendar_data.py)."
  echo "   Run your preferred script manually after deleting: rm -f $TOKEN_PATH"
  exit 1
fi
