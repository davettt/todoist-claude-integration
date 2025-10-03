# Todoist + Claude Integration

*Manage your tasks by talking to Claude. Simple, powerful, automated.*

**Current Version:** v1.2.0 | [Changelog](CHANGELOG.md)

---

## What This Does

1. **Export** your tasks and calendar to local files
2. **Process emails** (optional) - Forward emails to create tasks automatically
3. **Talk to Claude** about what you need to do
4. **Apply** changes automatically to Todoist

That's it. Simple, powerful, automated.

---

## Quick Start

**First time?** → Read [QUICKSTART.md](QUICKSTART.md) (5 minute setup)

**Daily use - Simple CLI:**
```bash
python3 daily_manager.py
```

This gives you a guided menu for everything:
- Export your data (Step 1)
- Instructions for Claude (Step 2)  
- Apply changes (Step 3)
- Process forwarded emails (Step 4)
- View tasks and calendar
- Backups and setup

**Or run commands directly:**
```bash
# Step 1: Export
python3 get_current_tasks.py
python3 get_calendar_data.py

# Step 2: Talk to Claude (see instructions below)

# Step 3: Apply changes
python3 todoist_task_manager.py
```

💡 **Tip:** Use `daily_manager.py` - it's easier!

---

## Maintenance

**Before pushing to git:**
```bash
python3 cleanup.py  # Removes temp files
```

**Versioning:** See [CHANGELOG.md](CHANGELOG.md) for version history

**Protected data:** `.gitignore` prevents committing personal data, credentials, or tokens

---

## Instructions for Claude

When helping users manage tasks, follow this process:

### 1. Read Current State
Check `local_data/personal_data/`:
- `current_tasks.json` - User's current tasks
- `calendar_full_analysis.json` - Calendar (if available)

Check `local_data/pending_operations/`:
- `tasks_email_*.json` - Pending email operations to review
- These contain sanitized email content that needs task/event extraction

### 2. Understand User Intent

**Common requests:**
- "What should I focus on?" → Review due_today and calendar
- "Review pending emails" → Check pending_operations/ for email operations
- "I finished [task]" → Create `completions` operation
- "Move [task] to [date]" → Create `updates` operation  
- "Add task: [description]" → Create `new_tasks` operation
- "Delete [task]" → Create `deletions` operation

**Email operations:**
- Read sanitized content from `tasks_email_*.json` files
- Extract actionable tasks and meeting requests
- Update the same file by populating `new_tasks` and `calendar_events` arrays
- Content is already sanitized (URLs/emails removed for security)

### 3. Create Operation File

**Filename:** `tasks_[brief-description]_YYYY-MM-DD.json`

**Template:**
```json
{
  "operation_type": "One-line description",
  "generated_at": "2025-09-29T17:00:00",
  "completions": [
    {
      "content": "Exact task name from Todoist",
      "task_id": "Optional: Todoist task ID for exact match",
      "project_name": "Optional: for disambiguation if duplicate names exist",
      "section_name": "Optional: for disambiguation if duplicate names exist",
      "reason": "Optional: why completing"
    }
  ],
  "updates": [
    {
      "content": "Exact task name",
      "task_id": "Optional: Todoist task ID for exact match",
      "project_name": "Project name (also used for disambiguation)",
      "section_name": "Section name (also used for disambiguation)",
      "due_date": "YYYY-MM-DD or 'tomorrow'",
      "priority": 2,
      "labels": ["Label1"],
      "description": "Task description"
    }
  ],
  "deletions": [
    {
      "content": "Exact task name",
      "task_id": "Optional: Todoist task ID for exact match",
      "project_name": "Optional: for disambiguation if duplicate names exist",
      "section_name": "Optional: for disambiguation if duplicate names exist",
      "reason": "Optional: why deleting"
    }
  ],
  "new_tasks": [
    {
      "content": "New task title",
      "project_name": "This week",
      "section_name": "In Progress",
      "due_date": "2025-10-01",
      "priority": 2,
      "labels": ["Personal"],
      "description": "Detailed description"
    }
  ]
}
```

### 4. Critical Rules

**Task Matching:**
- Use EXACT names from `current_tasks.json` or `all_tasks_comprehensive.json`
- If uncertain, show user exact name and confirm
- **NEW**: For duplicate task names, use one of these strategies:
  1. Include `task_id` field (most reliable - get from exported JSON)
  2. Include both `project_name` and `section_name` for disambiguation
  3. Ensure task names are unique before creating tasks

**Completions vs Deletions:**
- ✅ **completions**: "done", "finished", "mark complete", "cross off"
- 🗑️ **deletions**: "delete", "remove permanently", "get rid of"
- **Important:** Completions preserve history, deletions don't
- **Important:** Always use completions for recurring tasks

**Priority Levels:**
- 1 = P1 (Urgent/Red)
- 2 = P2 (High/Orange)
- 3 = P3 (Medium/Blue)
- 4 = P4 (Low/None)

**Due Dates:**
- Natural: "tomorrow", "next week", "Oct 15"
- Specific: "YYYY-MM-DD"

### 5. Response Format

After creating operation file, tell user:
1. **What's in it:** "2 completions, 1 new task"
2. **How to apply:** "Run: `python3 todoist_task_manager.py`"
3. **What happens:** "This will mark [tasks] as complete and create [task]"

---

## Features

**Task Management:**
- ✅ Create, update, complete, delete tasks
- ✅ Natural language due dates
- ✅ Project/section organization
- ✅ Priority and label management
- ✅ Recurring task support

**Email Integration (NEW):**
- 📧 Forward emails to create tasks automatically
- 📧 Secure content sanitization (URLs/emails stripped)
- 📧 Extract action items and meeting requests
- 📧 Review pending operations before applying

**Calendar Integration (Optional):**
- 📅 View availability and free time
- 📅 Schedule time blocks for tasks
- 📅 Avoid scheduling conflicts

**Smart Features:**
- 🤖 Batch operations (handle multiple tasks at once)
- 🤖 Preview before applying
- 🤖 Automatic file archiving
- 🤖 Error handling and validation

---

## File Structure

```
todoist-python/
├── README.md                   ← You are here
├── QUICKSTART.md               ← 5-minute setup guide
├── CHANGELOG.md                ← Version history
├── .env                        ← Your API token (create from .env.example)
│
├── Core Scripts:
│   ├── daily_manager.py            ← **START HERE** - Main CLI interface
│   ├── get_current_tasks.py        ← Export tasks (or use CLI option 1)
│   ├── get_calendar_data.py        ← Export calendar (or use CLI option 1)
│   ├── todoist_task_manager.py     ← Apply changes (or use CLI option 3)
│   └── process_emails.py           ← Process forwarded emails (or use CLI option 4)
│
├── Setup Scripts (one-time):
│   ├── get_todoist_config.py       ← Fetch projects/labels
│   └── list_calendars.py           ← List available calendars
│
├── local_data/
│   ├── personal_data/              ← Claude reads these files
│   │   ├── current_tasks.json
│   │   ├── calendar_full_analysis.json
│   │   └── todoist_reference.json
│   ├── pending_operations/         ← Email operations awaiting review
│   │   └── tasks_email_*.json
│   └── processed/                  ← Archived operations
│
└── tasks_*.json                    ← Claude creates these (temporary)
```

---

## Examples

### Morning Planning
**User:** "What should I focus on today?"

**Claude:**
1. Reads `current_tasks.json`
2. Checks `calendar_full_analysis.json` for free time
3. Suggests priorities based on due dates and availability

### Completing Tasks
**User:** "I paid rent and called the dentist"

**Claude creates:**
```json
{
  "completions": [
    {"content": "Pay rent"},
    {"content": "Call dentist"}
  ]
}
```

### Adding Tasks
**User:** "Add task to grocery shop tomorrow"

**Claude creates:**
```json
{
  "new_tasks": [
    {
      "content": "Grocery shopping",
      "project_name": "Personal",
      "due_date": "tomorrow",
      "priority": 2
    }
  ]
}
```

### Rescheduling
**User:** "Move my address update to Friday"

**Claude creates:**
```json
{
  "updates": [
    {
      "content": "Update remaining address details",
      "due_date": "2025-10-03"
    }
  ]
}
```

### Email Integration
**User forwards email:** "Hi, can you update the website header by Friday? Thanks, John"

**System:**
1. Receives email in Gmail assistant inbox
2. Strips URLs and email addresses (security)
3. Creates operation file in `pending_operations/`

**User runs:** `python3 daily_manager.py` → Option 4

**Claude reviews and suggests:**
```json
{
  "new_tasks": [
    {
      "content": "Update website header for John",
      "project_name": "Client Work",
      "due_date": "2025-10-06",
      "priority": 2
    }
  ]
}
```

---

## The CLI Interface (Recommended)

### Use the Menu Interface
```bash
python3 daily_manager.py
```

**What you get:**
- 📔 Guided 3-step workflow (Export → Claude → Apply)
- 📄 View tasks and calendar anytime
- 🔧 First-time setup helper
- 📚 Full workflow guide
- ✅ Everything in one place

**Why use this?**
- No need to remember commands
- See your tasks before talking to Claude
- Copy/paste instructions for Claude
- Preview changes before applying

**The menu:**
```
1. Export data (Step 1)
2. Instructions for Claude (Step 2)
3. Apply changes (Step 3)
4. Process forwarded emails
5. View my current tasks
6. View my calendar
7. First-time setup
8. Show full workflow guide
9. Exit
```

Just run it every day and follow the numbers! 🎯

**Note:** If you have pending email operations, the banner will show:
"📧 2 pending email operations ready for review"

Mention these to Claude in your conversation (option 2) and Claude will review them.

### Advanced Menu (Optional)

For power users who want more options:
```bash
python3 todoist_manager.py
```

This provides 13 menu options including:
- File management and history
- Detailed configuration views
- System information
- Advanced features

Most users won't need this - `daily_manager.py` has everything! 😊

### Export All Tasks
```bash
python3 get_all_tasks_enhanced.py
```

Gets complete task list (not just current/upcoming).

### Calendar Time Blocking
```bash
python3 calendar_event_manager.py
```

Create calendar events for tasks (requires calendar setup).

---

## Troubleshooting

**"No task files found"**
- Claude hasn't created operation files yet
- Or files not named `tasks*.json` pattern

**"Task not found for completion/update"**
- Task name doesn't match exactly
- Task may already be completed/deleted
- Check `current_tasks.json` for exact names

**"Connection error"**
- Check `.env` file has `TODOIST_API_TOKEN=your_token`
- Verify token at: Todoist Settings → Integrations

**Script errors**
- Run: `pip3 install -r requirements.txt`
- Check Python version: `python3 --version` (needs 3.7+)

---

## Privacy & Security

- 🔒 API tokens stored locally in `.env` (never committed)
- 🏠 All data stays on your machine + Todoist/Google servers
- 🚫 No third-party cloud storage
- ✅ Open source - review all code
- 📝 `.gitignore` protects sensitive files

---

## Architecture

**Simple view:**
```
Export → Claude reads files → Creates operations → Apply to Todoist
```

**Technical view:**
```
Python Scripts ←→ Local JSON Files ←→ Claude AI
       ↓
   Todoist API
   Google Calendar API (optional)
```

**Core modules:**
- `apis/todoist_client.py` - Todoist API wrapper
- `apis/google_calendar_client.py` - Calendar API wrapper
- `utils/file_manager.py` - File operations
- Task/Calendar managers - Main execution scripts

---

## Tips for Best Results

**For Users:**
- Start fresh conversation with Claude each day
- Be specific: "Mark 'Pay rent' complete" not "I paid stuff"
- Run export (Step 1) every morning for current data
- Review preview before applying changes

**For Claude:**
- Always match exact task names from JSON files
- Use completions (not deletions) for finished tasks
- Confirm ambiguous requests with user
- Explain what will happen when changes are applied

---

## Roadmap

**Current:** ✅ Complete Todoist integration, optional Calendar, Email integration (Phase 1)

**Phase 1 Complete:**
- ✅ Gmail API integration with OAuth2
- ✅ Email content sanitization (URL/email stripping)
- ✅ Pending operations workflow
- ✅ Daily manager UI integration

**Next:**
- [ ] Email observation period (Phase 2 - collect usage patterns)
- [ ] Local CRM foundation (Phase 3 - client database)
- [ ] Task templates for common patterns
- [ ] Analytics and productivity insights

---

## Contributing

This is a personal productivity system, but:
- **Bug reports:** Open GitHub issues
- **Suggestions:** Start a discussion
- **Forks:** MIT license - customize freely

*Note: I keep contributions minimal to maintain system stability for personal use.*

---

## License

MIT License - See LICENSE file for details

---

## Support

**Documentation:**
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [CHANGELOG.md](CHANGELOG.md) - Version history
- This README - Complete reference

**Getting Help:**
- Check troubleshooting section above
- Review error messages (they're usually clear)
- Verify `.env` configuration
- Ensure data export ran successfully

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md) ⚡

---

*Version 1.2.0 - Last updated: October 3, 2025*
