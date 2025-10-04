# Quick Start Guide

Get up and running with Todoist + Claude in 5-10 minutes.

---

## Prerequisites

- Python 3.7 or higher
- Todoist account (free or paid)
- Claude AI access (claude.ai)
- Optional: Google account (for calendar integration)
- Optional: Gmail account (for email integration)

---

## Installation

### 1. Clone & Install Dependencies

```bash
cd todoist-python
pip3 install -r requirements.txt
```

**Dependencies installed:**
- `todoist-api-python` - Todoist integration
- `python-dotenv` - Environment configuration
- `google-auth`, `google-api-python-client` - Calendar/Gmail (optional)
- `beautifulsoup4`, `lxml` - Email parsing (optional)

### 2. Configure Todoist API

```bash
cp .env.example .env
```

Edit `.env` and add your Todoist API token:
```
TODOIST_API_TOKEN=your_token_here_12345abcdef
```

**Get your token:**
1. Go to [Todoist Settings → Integrations](https://todoist.com/prefs/integrations)
2. Scroll to "Developer" section
3. Copy your API token
4. Paste into `.env` file

### 3. Initialize Todoist Connection

```bash
python3 get_todoist_config.py
```

This fetches your projects, sections, and labels to `local_data/personal_data/todoist_reference.json`.

**You're ready to use task management!** 🎉

---

## Optional: Google Calendar Setup

If you want calendar integration for availability analysis:

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (e.g., "Todoist Assistant")
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON

### 2. Install Credentials

```bash
# Save downloaded file as:
mv ~/Downloads/credentials.json local_data/calendar_credentials.json
```

### 3. First Run (Authorization)

```bash
python3 get_calendar_data.py
```

This will:
- Open your browser for Google authorization
- Save access token to `local_data/calendar_token.json`
- Export calendar data to `local_data/personal_data/calendar_full_analysis.json`

**Note:** You only authorize once. Future runs use the saved token.

### 4. Select Your Calendar

To see available calendars:
```bash
python3 list_calendars.py
```

Most users use their primary calendar (default).

**Calendar integration complete!** 📅

---

## Optional: Email Integration Setup

If you want to forward emails and create tasks automatically:

### 1. Create Gmail OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Use same project from Calendar setup (or create new)
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON

### 2. Install Gmail Credentials

```bash
# Save downloaded file as:
mv ~/Downloads/gmail-credentials.json local_data/gmail_credentials.json
```

### 3. First Run (Authorization)

```bash
python3 process_emails.py
```

This will:
- Open browser for Gmail authorization
- Save token to `local_data/gmail_token.json`
- Process any forwarded emails

### 4. Configure Trusted Senders

Edit `.env` to add trusted email forwarders and senders:

```bash
# Your email accounts that can forward to the assistant inbox
TRUSTED_FORWARDERS=your.email@gmail.com,work.email@company.com

# Content sources you trust (for prioritization)
TRUSTED_SENDERS=james@jamesclear.com,newsletter@example.com
```

**Security note:** The dual trust system checks:
- **Forwarder** - Must be one of your accounts (security)
- **Original sender** - From your trusted sources (priority)

### 5. Set Up Email Forwarding

**Option A: Gmail Filter (Recommended)**
1. Gmail Settings → Filters and Blocked Addresses
2. Create filter: `to:assistant@yourdomain.com` (your assistant inbox)
3. Forward to your main account
4. Skip inbox (stays organized)

**Option B: Manual Forward**
- Forward individual emails to your assistant inbox
- Subject: "Fw: Original Subject"
- Body includes original sender info

**Email integration complete!** 📧

---

## Daily Workflow

### The Easy Way: Daily Manager CLI

```bash
python3 daily_manager.py
```

**The menu guides you through everything:**

```
📋 DAILY WORKFLOW (Do these in order):
  1. 📤 Export data (Step 1)
  2. 💬 Instructions for Claude (Step 2)
  3. ✅ Apply changes (Step 3)
  4. 📧 Process forwarded emails
  5. 📊 Generate email digest
  6. 📝 Review digest interactively

📊 VIEWS:
  7. 📋 View my current tasks
  8. 📅 View my calendar

⚙️ SETUP & HELP:
  9. 🔧 First-time setup
  10. 📖 Show full workflow guide
  11. 🚪 Exit
```

### The 3-Step Process

#### Step 1: Export Data
Choose option 1 to export:
- Current tasks (overdue, today, tomorrow, upcoming week)
- Calendar availability (if configured)

Files created:
- `local_data/personal_data/current_tasks.json`
- `local_data/personal_data/calendar_full_analysis.json`

#### Step 2: Talk to Claude
Choose option 2 to see instructions. Then in Claude:

```
Please help me manage my tasks today.

Read these files from my todoist-python folder:
- local_data/personal_data/current_tasks.json
- local_data/personal_data/calendar_full_analysis.json (if available)

Then follow the instructions in the "For Claude" section of README.md
```

Claude will:
- Review your current situation
- Help you prioritize
- Create operation files for any changes

#### Step 3: Apply Changes
Choose option 3 to apply changes to Todoist.

**That's it!** Repeat daily. 🎯

---

## Email Workflow

### Processing Forwarded Emails

When you forward emails to your assistant inbox:

**Option 4: Process Forwarded Emails**
- Fetches forwarded emails from Gmail
- Strips URLs and email addresses (security)
- Creates pending operation files
- Waits for your review

Files created:
- `local_data/pending_operations/tasks_email_YYYY-MM-DD_HHMMSS.json`

**Then tell Claude:**
> "Review my pending emails"

Claude will:
- Read the sanitized email content
- Extract actionable tasks
- Suggest new tasks or calendar events

### AI Email Digest

**Option 5: Generate Email Digest**
- Analyzes last 2 weeks of emails
- Uses Claude API to predict interest levels
- Creates markdown digest with summaries

**Option 6: Review Digest Interactively**
- Read email summaries
- Rate predictions (correct/incorrect)
- Archive, trash, or keep emails
- System learns from your feedback

Files created:
- `local_data/email_digests/digest_YYYY-MM-DD.md`
- `local_data/personal_data/email_interest_profile.json` (learning data)
- `local_data/personal_data/email_feedback_log.json` (accuracy tracking)

---

## Command Reference

### Daily Manager (Recommended)
```bash
python3 daily_manager.py
```
Interactive menu with guided workflow.

### Individual Scripts

**Export data:**
```bash
python3 get_current_tasks.py        # Current/upcoming tasks
python3 get_all_tasks_enhanced.py   # All tasks (comprehensive)
python3 get_calendar_data.py        # Calendar availability
```

**Process operations:**
```bash
python3 todoist_task_manager.py     # Apply task changes
python3 process_emails.py           # Process forwarded emails
```

**Email digest:**
```bash
python3 biweekly_email_digest.py    # Generate digest
python3 review_digest_interactive.py # Review & rate
```

**Setup helpers:**
```bash
python3 get_todoist_config.py       # Fetch projects/labels
python3 list_calendars.py           # List Google calendars
```

**Maintenance:**
```bash
python3 cleanup.py                  # Remove temp files before git commit
```

---

## File Structure Explained

```
todoist-python/
├── .env                           # Your API tokens (NEVER commit)
├── daily_manager.py               # Main CLI interface
│
├── local_data/
│   ├── calendar_credentials.json  # Google Calendar OAuth (NEVER commit)
│   ├── calendar_token.json        # Calendar access token (NEVER commit)
│   ├── gmail_credentials.json     # Gmail OAuth (NEVER commit)
│   ├── gmail_token.json          # Gmail access token (NEVER commit)
│   │
│   ├── personal_data/            # Claude reads these files
│   │   ├── current_tasks.json         # Your current tasks
│   │   ├── calendar_full_analysis.json # Calendar availability
│   │   ├── todoist_reference.json     # Projects/labels
│   │   ├── email_interest_profile.json # AI learning data
│   │   └── email_feedback_log.json    # Rating accuracy
│   │
│   ├── pending_operations/       # Email operations awaiting review
│   │   └── tasks_email_*.json
│   │
│   ├── email_digests/           # Generated email digests
│   │   └── digest_YYYY-MM-DD.md
│   │
│   └── processed/               # Archived operations
│       └── tasks_*.json
│
└── tasks_*.json                 # Temporary - Claude creates these
```

**Protected by .gitignore:**
- All credentials and tokens
- Personal data files
- Temporary operation files

---

## Configuration Details

### Todoist (.env)

```bash
# Required
TODOIST_API_TOKEN=your_token_here

# Optional: Email integration
TRUSTED_FORWARDERS=your.email@gmail.com,work@company.com
TRUSTED_SENDERS=newsletter@trusted.com,james@jamesclear.com

# Optional: Claude API (for email digest)
ANTHROPIC_API_KEY=your_claude_api_key
```

**Get Claude API key:**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Settings → API Keys
3. Create new key
4. Add to `.env`

### Calendar Setup

**Default behavior:**
- Uses your primary Google Calendar
- Analyzes next 2 weeks
- Identifies free time and focus blocks

**To use specific calendar:**
1. Run `python3 list_calendars.py`
2. Find calendar ID
3. Edit script to use specific calendar

### Email Trust System

**Trusted Forwarders** - Your accounts that can forward emails:
- Primary security check
- Only processes emails from these addresses
- Format: `email1@domain.com,email2@domain.com`

**Trusted Senders** - Content sources you prioritize:
- Secondary check for original email sender
- Helps AI prioritize interesting content
- Format: `sender1@domain.com,sender2@domain.com`

**How it works:**
1. Email arrives at assistant inbox
2. System checks: Is forwarder in TRUSTED_FORWARDERS?
3. Extracts original sender from forwarded email body
4. Checks: Is original sender in TRUSTED_SENDERS?
5. Both displayed in digest for transparency

---

## Troubleshooting

### Todoist Issues

**"Connection error" or "Invalid token"**
- Check `.env` has correct `TODOIST_API_TOKEN`
- Verify token at: [Todoist Settings → Integrations](https://todoist.com/prefs/integrations)
- Make sure no extra spaces in `.env`

**"Task not found for completion/update"**
- Task name must match EXACTLY
- Run option 7 to see exact names
- Use `task_id` field for 100% accuracy

**"No task files found"**
- Claude hasn't created operation files yet
- Or files not named with `tasks_*.json` pattern

### Calendar Issues

**"Calendar credentials not found"**
- Make sure file is: `local_data/calendar_credentials.json`
- Check it's valid JSON (download again if needed)

**"Invalid credentials" or "Token expired"**
- Delete `local_data/calendar_token.json`
- Run `python3 get_calendar_data.py` again
- Re-authorize when browser opens

**"No events found" (but you have events)**
- Check timezone in `get_calendar_data.py`
- Verify calendar ID (run `python3 list_calendars.py`)

### Email Issues

**"Gmail credentials not found"**
- Make sure file is: `local_data/gmail_credentials.json`
- Enable Gmail API in Google Cloud Console

**"Insufficient permissions"**
- Delete `local_data/gmail_token.json`
- Run `python3 process_emails.py` again
- Accept all permissions when re-authorizing

**"No emails found"**
- Check emails are forwarded to correct inbox
- Verify TRUSTED_FORWARDERS in `.env`
- Email must have "Fwd:" or "Fw:" in subject

**"Security warning: Email not from trusted forwarder"**
- This is working correctly!
- Only emails from TRUSTED_FORWARDERS are processed
- Add forwarder to `.env` if legitimate

### General Issues

**"Module not found" errors**
- Run: `pip3 install -r requirements.txt`
- Make sure you're in the todoist-python directory

**"Permission denied"**
- Check file permissions: `chmod +x *.py`
- Or run with: `python3 script_name.py`

**Changes not appearing in Todoist**
- Check preview output before applying
- Verify internet connection
- Look for error messages in output

---

## Tips & Best Practices

### Daily Workflow Tips

**Start each day fresh:**
1. Run `daily_manager.py`
2. Export data (option 1)
3. New Claude conversation
4. Review and plan

**Be specific with Claude:**
- ❌ "I finished some stuff"
- ✅ "Mark 'Pay rent' and 'Call dentist' complete"

**Use the preview:**
- Option 3 shows what will change
- Review before confirming
- Ctrl+C to cancel if needed

### Task Management Tips

**Use completions, not deletions:**
- Completions preserve history
- Deletions are permanent
- Recurring tasks need completions

**Leverage task IDs:**
- Include `task_id` for exact matching
- Prevents issues with duplicate names
- Found in exported JSON files

**Natural due dates work:**
- "tomorrow" → Next day
- "next Friday" → Upcoming Friday
- "in 3 days" → 3 days from now

### Email Integration Tips

**Set up filters:**
- Auto-forward from specific senders
- Keep inbox organized
- Process in batches

**Rate digest predictions:**
- Helps AI learn your preferences
- Improves future predictions
- Track accuracy in feedback log

**Review pending operations:**
- Don't let them pile up
- Process within 24 hours
- Batch similar emails

---

## Advanced Features

### Batch Operations

You can handle multiple tasks in one operation file:

```json
{
  "operation_type": "End of day cleanup",
  "completions": [
    {"content": "Task 1"},
    {"content": "Task 2"},
    {"content": "Task 3"}
  ],
  "new_tasks": [
    {"content": "Follow-up for tomorrow", "due_date": "tomorrow"}
  ]
}
```

### Custom Workflows

**Weekly planning:**
1. Export all tasks: `python3 get_all_tasks_enhanced.py`
2. Review with Claude
3. Batch reschedule/update

**Email sprint:**
1. Generate digest (option 5)
2. Review interactively (option 6)
3. Process pending operations (option 4)
4. Apply changes (option 3)

**Calendar time blocking:**
```bash
python3 calendar_event_manager.py
```
Create calendar events for task focus time.

### Backup & Recovery

The system auto-creates backups in:
- `local_data/backups/` - Recent operation files
- `local_data/processed/` - Successfully applied operations

**Manual backup:**
```bash
# Copy entire local_data folder
cp -r local_data ~/Documents/todoist-backup-$(date +%Y%m%d)
```

---

## What's Next?

**You're all set!** Here's what to do now:

1. ✅ Run `python3 daily_manager.py`
2. ✅ Export data (option 1)
3. ✅ Talk to Claude (option 2)
4. ✅ Start managing tasks!

**Learn more:**
- [README.md](README.md) - Complete feature overview
- [CHANGELOG.md](CHANGELOG.md) - Version history
- Email integration specs in `local_data/specs/`

**Get help:**
- Check troubleshooting section above
- Review error messages (they're descriptive)
- Open GitHub issue for bugs

---

## Keyboard Shortcuts

While in `daily_manager.py` menu:
- **1-11** - Select option
- **Ctrl+C** - Cancel/Exit
- **Ctrl+D** - Exit (EOF)

While applying changes:
- **Ctrl+C** - Cancel operation
- **Y/N** - Confirm/Decline prompts

---

**Happy task managing!** 🚀

*Tip: Bookmark this guide - it has everything you need.*
