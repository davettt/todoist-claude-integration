# Todoist + Claude Integration

*Manage your Todoist tasks through natural conversations with Claude AI - no clicking, just talking.*

**Current Version:** v1.3.1 | [Changelog](CHANGELOG.md)

---

## What It Does

- 🗣️ **Chat naturally with Claude** - "I finished the report" or "Add grocery shopping for tomorrow"
- 📋 **Automatic task management** - Claude creates/updates/completes tasks in Todoist
- 📧 **Smart email processing** - Forward emails to auto-create tasks with AI digest
- 📅 **Calendar integration** - Claude considers your schedule when planning tasks
- ✨ **Simple workflow** - Export → Chat with Claude → Apply changes

---

## Quick Start

**Want to try it right now?**

```bash
# 1. Clone and install
git clone <repo-url>
cd todoist-python
pip install -r requirements.txt

# 2. Set up credentials
cp .env.example .env
# Add your Todoist API token to .env

# 3. Run the daily manager
python3 daily_manager.py
```

**That's it!** See [Installation](#installation) for detailed setup.

---

## Installation

### Prerequisites

Before installing, make sure you have:
- **Python 3.9 or newer** ([Check version](https://www.python.org/downloads/): `python3 --version`)
- **pip** (usually comes with Python)
- **Todoist account** ([Sign up free](https://todoist.com/))
- **Todoist API token** ([Get it here](https://todoist.com/prefs/integrations))
- **Optional:** Google Calendar API credentials (for calendar features)

### Step 1: Clone the Repository

```bash
git clone <repo-url>
cd todoist-python
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs:** Python packages for Todoist API, Google Calendar, email processing, etc.

### Step 3: Set Up API Credentials

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Todoist API token:
# TODOIST_API_TOKEN=your-token-here
```

Get your Todoist API token from: [Todoist Integrations](https://todoist.com/prefs/integrations)

**Optional - Google Calendar:**
- See [Setting Up Calendar Integration](#setting-up-calendar-integration) if you want calendar features
- Not required for basic task management

### Step 4: First Run

```bash
python3 daily_manager.py
```

**Expected result:** You'll see a menu with options to export data, view tasks, etc.

### Troubleshooting Installation

**Python not found?**
- Install from [python.org](https://www.python.org/downloads/)
- Try `python3` instead of `python`

**"No module named 'todoist_api_python'" or similar?**
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the todoist-python directory

**"Invalid Todoist API token"?**
- Check `.env` file format: `TODOIST_API_TOKEN=your-token` (no quotes, no spaces)
- Get a new token from [Todoist Integrations](https://todoist.com/prefs/integrations)

---

## How to Use

### The Daily Workflow (3 Steps)

```bash
python3 daily_manager.py
```

You'll see a simple menu organized by workflow:

```
📋 DAILY WORKFLOW:
  1. Export data (Step 1)
  2. Instructions for Claude (Step 2)
  3. Apply changes (Step 3)

📧 EMAIL:
  4. Process forwarded emails
  5. Generate email digest
  6. Review digest interactively

📊 VIEWS:
  7. View my current tasks
  8. View my calendar

💾 BACKUP:
  9. Create backup
  10. Manage backups

⚙️ SETUP & HELP:
  11. First-time setup
  12. Show full workflow guide
  13. Exit
```

**The basic workflow:**

**Step 1 - Export data:**
- Choose option 1
- Exports your tasks to `local_data/personal_data/current_tasks.json`

**Step 2 - Chat with Claude:**
- Choose option 2 to see instructions
- Open Claude.ai in your browser
- Tell Claude: "Read my Todoist data at [folder path]"
- Have a natural conversation about your tasks

**Step 3 - Apply changes:**
- Claude creates a JSON file with your changes
- Choose option 3 in the menu
- Script automatically updates Todoist

**That's it!** Repeat daily.

### Example Conversations with Claude

**Morning planning:**
> You: "What should I focus on today?"
> 
> Claude: *Reads your tasks and calendar* "You have 3 tasks due today and a meeting at 2pm. I recommend tackling the report before lunch."

**Completing tasks:**
> You: "I finished the report and called the client"
>
> Claude: *Creates completion file* "I've marked those 2 tasks as complete. Run the apply script."

**Adding new tasks:**
> You: "Add grocery shopping for tomorrow, high priority"
>
> Claude: *Creates new task file* "Added 'Grocery shopping' for tomorrow with high priority."

---

## Common Tasks

### Daily Planning

```bash
python3 daily_manager.py
# Choose: 1 (Export data)
# Then chat with Claude about your day
# Choose: 3 (Apply changes)
```

### Viewing Your Current Tasks

```bash
python3 daily_manager.py
# Choose: 7 (View my current tasks)
```

Shows your overdue, today, and upcoming tasks.

### Processing Forwarded Emails

```bash
python3 daily_manager.py
# Choose: 4 (Process forwarded emails)
```

Forward emails to your special address, then process them to create tasks.

### Setting Up Email Integration

**Prerequisites:**
- Gmail account for assistant inbox
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (Desktop app)
- Anthropic API key (for AI digest)

**Setup steps:**
1. Use same Google Cloud project (or create new one)
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials → save as `local_data/gmail_credentials.json`
5. Configure `.env` with:
   ```bash
   TRUSTED_FORWARDERS=your.email@gmail.com,work@company.com
   TRUSTED_SENDERS=newsletter@trusted.com,sender@example.com
   ANTHROPIC_API_KEY=your-claude-api-key
   ```
6. Run `python3 process_emails.py` to authorize

**How it works:**
- Forward emails to your Gmail assistant account
- System checks dual trust: forwarder (security) + original sender (priority)
- Emails WITH `[TASK]` or `#task` → create task operations
- Emails WITHOUT markers → save for AI digest

### Getting an Email Digest

```bash
python3 daily_manager.py
# Choose: 5 (Generate AI email digest)
```

Get AI-powered summaries with interest predictions (HIGH/MEDIUM/LOW).

### Setting Up Calendar Integration

**Prerequisites:**
- Google account with Calendar
- Google Cloud project with Calendar API enabled
- OAuth 2.0 credentials (Desktop app)

**Quick setup:**
```bash
python3 daily_manager.py
# Choose: 11 (First-time setup)
```

**Manual setup:**
1. Create Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials → save as `local_data/calendar_credentials.json`
5. Run `python3 get_calendar_data.py` to authorize

Calendar data will be exported to `local_data/personal_data/calendar_full_analysis.json`.

---

## For Claude: How to Help Users

### 1. Read Current State

**Always check these files first:**
- `local_data/personal_data/current_tasks.json` - User's tasks (overdue, today, upcoming)
- `local_data/personal_data/calendar_full_analysis.json` - Calendar availability (if available)
- `local_data/pending_operations/tasks_email_*.json` - Pending email operations (if any)

### 2. Understand User Intent

**Common requests:**
- "What should I focus on today?" → Review `due_today` and calendar availability
- "I finished X and Y" → Create `completions` operation
- "Add task to X" → Create `new_tasks` operation  
- "Move X to Friday" → Create `updates` operation
- "Delete X" → Create `deletions` operation (use sparingly)
- "Review my emails" → Check `pending_operations/` directory

### 3. Create Operation File

**Filename format:** `tasks_[brief-description]_YYYY-MM-DD.json`

**Template:**
```json
{
  "operation_type": "Brief description",
  "generated_at": "2025-10-04T19:00:00",
  "completions": [
    {
      "content": "Exact task name from current_tasks.json",
      "task_id": "9382265058",
      "reason": "Optional: Why completing"
    }
  ],
  "new_tasks": [
    {
      "content": "New task title",
      "project_name": "This week",
      "due_date": "tomorrow",
      "priority": 2,
      "labels": ["Personal"]
    }
  ]
}
```

### 4. Critical Rules

- Use EXACT task names from JSON files
- Include `task_id` when available
- Use `completions` for done tasks (preserves history)
- Use natural language dates: "tomorrow", "next Friday", "Oct 15"
- Priority levels: 1=Urgent, 2=High, 3=Medium, 4=Low

**Full documentation:** See [For Claude](#for-claude-how-to-help-users) section above for complete details.

---

## Requirements

- Python 3.9 or newer
- Todoist account (free or paid)
- Todoist API token

**Optional:**
- Google Calendar API credentials (for calendar features)
- Gmail API credentials (for email features)

---

## Data Storage & Privacy

- 🏠 **Your data stays local** in `local_data/` folder
- 🔒 **API tokens** stored in `.env` file (never committed to git)
- ☁️ **Cloud sync** only to Todoist and Google (if enabled)
- 🔒 **Email security** - Dual trust verification, URLs/emails stripped before AI processing
- 🚫 **No tracking** or external analytics
- ✅ **Open source** - review all code yourself

**Your private files:**
- `local_data/personal_data/` - Your tasks, calendar, email data
- `.env` - Your API credentials
- Both are excluded from git automatically

---

## Usage & Forking

This project is open source under MIT license. You're welcome to:
- **Fork the repository** and customize for your own needs
- **Report bugs** via GitHub issues
- **Suggest improvements** in discussions

*Note: This is a personal productivity system. While the code is open source, I keep contributions minimal to maintain system stability for personal use.*

### For Developers (Forking/Customization)

If you've forked this project and want to modify it, see:
- **[.claude/README.md](.claude/README.md)** - Claude Code integration guide
- **[.claude/workflow/code_standards.md](.claude/workflow/code_standards.md)** - Code quality workflow

**Quick fork setup:**
```bash
git clone <your-fork-url>
cd todoist-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# See .claude/ folder for development docs
```

---

## Troubleshooting

### Installation Issues

**"No module named 'todoist_api_python'"**
- Run: `pip install -r requirements.txt`
- Make sure you're in the todoist-python directory

**"Invalid Todoist API token"**
- Check `.env` format: `TODOIST_API_TOKEN=your-token` (no quotes/spaces)
- Get new token: [Todoist Integrations](https://todoist.com/prefs/integrations)

### Calendar/Email Issues

**"Credentials not found"**
- Verify file location: `local_data/calendar_credentials.json` or `local_data/gmail_credentials.json`
- Re-download from Google Cloud Console

**"Token expired" or "Invalid credentials"**
- Delete token file: `local_data/calendar_token.json` or `local_data/gmail_token.json`
- Re-run the script to re-authorize

**"No emails found" (but you forwarded emails)**
- Check emails forwarded to correct inbox
- Verify `TRUSTED_FORWARDERS` in `.env`
- Email subject must have "Fwd:" or "Fw:"

### Task Management Issues

**"Task not found"**
- Task names must match EXACTLY (check option 7)
- Use `task_id` field for 100% accuracy

**Changes not appearing in Todoist**
- Check internet connection
- Review preview output before confirming
- Look for error messages in terminal

---

## Support

- 📖 **Questions?** Check [Troubleshooting](#troubleshooting) and [Common Tasks](#common-tasks)
- 🐛 **Found a bug?** Open an issue on GitHub
- 💡 **Have an idea?** Start a discussion

---

## Advanced

### Email Features

**Forward emails to create tasks:**
1. Set up email forwarding (see [Setting Up Email Integration](#setting-up-email-integration))
2. Forward emails to your Gmail assistant account
3. Process with option 4 in daily manager

**AI Email Digest:**
- Get HIGH/MEDIUM/LOW interest predictions
- Learn from your ratings over time
- Secure: URLs and email addresses stripped before AI processing

### Calendar Integration

**View your schedule:**
- See availability and free time blocks
- Identify 3+ hour focus blocks for deep work
- Schedule-aware task planning

**Setup:**
- Run option 11 (First-time setup) in daily manager
- Follow prompts to connect Google Calendar

### File Structure

```
todoist-python/
├── .env                           # API tokens (NEVER commit)
├── daily_manager.py               # Main CLI - start here!
├── get_current_tasks.py           # Export tasks
├── todoist_task_manager.py        # Apply changes
├── process_emails.py              # Email processing
├── biweekly_email_digest.py       # Generate digest
├── review_digest_interactive.py   # Review & rate
│
├── local_data/
│   ├── calendar_credentials.json  # Google Calendar OAuth (gitignored)
│   ├── calendar_token.json        # Calendar access token (gitignored)
│   ├── gmail_credentials.json     # Gmail OAuth (gitignored)
│   ├── gmail_token.json           # Gmail access token (gitignored)
│   │
│   ├── personal_data/             # Claude reads these
│   │   ├── current_tasks.json          # Your tasks
│   │   ├── calendar_full_analysis.json # Calendar availability
│   │   ├── todoist_reference.json      # Projects/labels
│   │   ├── email_interest_profile.json # AI learning data
│   │   └── email_feedback_log.json     # Rating accuracy
│   │
│   ├── pending_operations/        # Email ops awaiting review
│   │   └── tasks_email_*.json
│   │
│   ├── email_digests/             # Generated digests
│   │   └── digest_YYYY-MM-DD.md
│   │
│   └── processed/                 # Archived operations
│       └── tasks_*.json
│
└── tasks_*.json                   # Temporary - Claude creates

**All credentials and personal data are gitignored**
```

### Roadmap

**✅ Current (v1.3.1):**
- Complete Todoist integration
- Calendar analysis
- Email forwarding with AI digest
- Interactive review

**🚀 Next:**
- Local CRM (client/sender database)
- Task templates
- Analytics and productivity insights

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Version:** v1.3.1 | **Last updated:** 2025-10-12

**Ready to get started?** Run `python3 daily_manager.py` 🚀
