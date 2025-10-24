#!/usr/bin/env bash
# Re-authorize Gmail API quickly by deleting the local OAuth token and launching a flow
# Usage:
#   bash scripts/reauth_gmail.sh
# Notes:
# - This removes only the local refresh/access token at local_data/gmail_token.json
# - Your credentials file (local_data/gmail_credentials.json) must exist
# - A browser window will open to complete OAuth consent

set -euo pipefail

TOKEN_PATH="local_data/gmail_token.json"
CREDENTIALS_PATH="local_data/gmail_credentials.json"

if [[ ! -f "$CREDENTIALS_PATH" ]]; then
  echo "❌ Missing Gmail credentials: $CREDENTIALS_PATH"
  echo "   Download OAuth client credentials (Desktop app) from Google Cloud Console"
  echo "   and save them as local_data/gmail_credentials.json"
  exit 1
fi

echo "🔐 Re-authorizing Gmail API access..."
echo "🗑️  Removing Gmail token: $TOKEN_PATH"
rm -f "$TOKEN_PATH"

echo "ℹ️  Note: Calendar token is kept separate (using calendar_token.json)"
echo "    If you need to reauth Calendar API, run: bash scripts/reauth_calendar.sh"

# Prefer digest (triggers Gmail auth), fallback to email processor
if [[ -f "biweekly_email_digest.py" ]]; then
  python3 biweekly_email_digest.py
elif [[ -f "process_emails.py" ]]; then
  python3 process_emails.py
else
  echo "❌ Could not find an entry script to trigger Gmail auth (biweekly_email_digest.py or process_emails.py)."
  echo "   Run your preferred script manually after deleting: rm -f $TOKEN_PATH"
  exit 1
fi
