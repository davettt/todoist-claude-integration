# Todoist + Claude Integration

*A CLI tool that lets you manage Todoist tasks, process emails, and analyze your calendar through natural conversations with Claude AI.*

**Current Version:** v1.3.1 | [Changelog](CHANGELOG.md) | [Quick Start Guide](QUICKSTART.md)

---

## What This Does

1. **Export** your tasks and calendar to local files
2. **Process emails** - Forward emails to create tasks automatically  
3. **AI Email Digest** - Get smart email summaries with interest predictions
4. **Talk to Claude** about what you need to do
5. **Apply** changes automatically to Todoist

That's it. Simple, powerful, automated.

---

## Key Features

### 📋 Task Management
- Create, update, complete, and delete tasks through conversation
- Natural language due dates ("tomorrow", "next Friday")
- Project/section organization with labels and priorities
- Batch operations and intelligent task matching

### 📧 Email Integration
- **Forward emails** to auto-create tasks and extract action items
- **AI-powered digest** with HIGH/MEDIUM/LOW interest predictions
- **Dual trust system** - Verify both forwarder (security) and original sender (priority)
- **Interactive review** - Rate emails to improve AI predictions over time
- **Secure processing** - All URLs and email addresses stripped before analysis

### 📅 Calendar Analysis
- View availability and free time across 2 weeks
- Identify focus blocks for deep work (3+ hour uninterrupted slots)
- Schedule-aware task planning
- Avoid conflicts when adding new commitments

---

## Quick Start

**New user?** → Read [QUICKSTART.md](QUICKSTART.md) for 5-minute setup

**Daily workflow:**

```bash
python3 daily_manager.py
```

Then follow the simple menu:
1. **Export data** - Get latest tasks and calendar
2. **Talk to Claude** - Describe what you want to do
3. **Apply changes** - Update Todoist automatically

That's the whole workflow! 🎯

---

## The Daily Manager

```bash
python3 daily_manager.py
```

**Menu Options:**
```
1. Export data (Step 1)
2. Instructions for Claude (Step 2)  
3. Apply changes (Step 3)
4. Process forwarded emails
5. Generate AI email digest
6. Review digest interactively
7. View my current tasks
8. View my calendar
9. First-time setup
10. Show full workflow guide
11. Exit
```

If you have pending email operations, you'll see a banner:
> 📧 2 pending email operations ready for review

Mention these to Claude and it will help you process them.

---

## For Claude: How to Help Users

### 1. Read Current State

**Always check these files first:**
- `local_data/personal_data/current_tasks.json` - User's tasks (overdue, today, upcoming)
- `local_data/personal_data/calendar_full_analysis.json` - Calendar availability
- `local_data/pending_operations/tasks_email_*.json` - Pending email operations

### 2. Understand User Intent

**Common requests:**
- "What should I focus on today?" → Review `due_today` and calendar availability
- "I finished X and Y" → Create `completions` operation
- "Add task to X" → Create `new_tasks` operation  
- "Move X to Friday" → Create `updates` operation
- "Delete X" → Create `deletions` operation (use sparingly - completions preserve history)
- "Review my emails" → Check `pending_operations/` directory

### 3. Create Operation File

**Filename format:** `tasks_[brief-description]_YYYY-MM-DD.json`

**Template:**
```json
{
  "operation_type": "Brief description of what this does",
  "generated_at": "2025-10-04T19:00:00",
  "completions": [
    {
      "content": "Exact task name from current_tasks.json",
      "task_id": "9382265058",
      "reason": "Optional: Why completing"
    }
  ],
  "updates": [
    {
      "content": "Exact task name",
      "task_id": "9382265058",
      "due_date": "2025-10-07",
      "priority": 2,
      "labels": ["Personal"],
      "description": "Updated description"
    }
  ],
  "new_tasks": [
    {
      "content": "New task title",
      "project_name": "This week",
      "section_name": "In Progress",
      "due_date": "tomorrow",
      "priority": 2,
      "labels": ["Personal"],
      "description": "Task details"
    }
  ],
  "deletions": [
    {
      "content": "Exact task name",
      "task_id": "9382265058",
      "reason": "Optional: Why deleting"
    }
  ]
}
```

### 4. Critical Rules

**Task Matching:**
- Use EXACT task names from the JSON files
- Include `task_id` when available (most reliable)
- For duplicate names, include `project_name` and `section_name`
- When uncertain, show user the exact name and confirm

**Completions vs Deletions:**
- ✅ **completions**: Use for "done", "finished", "complete" - preserves history
- 🗑️ **deletions**: Use for "delete", "remove permanently" - use sparingly
- **ALWAYS use completions for recurring tasks** (deletion breaks the recurrence)

**Priority Levels:**
- 1 = P1 (Urgent/Red)
- 2 = P2 (High/Orange)  
- 3 = P3 (Medium/Blue)
- 4 = P4 (Low/None)

**Due Dates:**
- Natural language: "tomorrow", "next week", "Oct 15"
- Specific format: "YYYY-MM-DD"

### 5. Response Format

After creating the operation file, tell the user:

1. **What you created:** "I've created an operation file with 2 completions and 1 new task"
2. **How to apply:** "Run: `python3 todoist_task_manager.py`"
3. **What will happen:** "This will mark 'Pay rent' and 'Call dentist' as complete, and create a new task 'Grocery shopping' for tomorrow"

**Be specific and clear!** Users need to know exactly what will change.

---

## Examples

### Morning Planning
**User:** "What should I focus on today?"

**Claude:**
1. Reads `current_tasks.json` for due tasks
2. Checks `calendar_full_analysis.json` for free time
3. Suggests: "You have 1 task due today and 13 hours of free time. I recommend tackling your address updates this morning."

### Completing Tasks
**User:** "I paid rent and called the dentist"

**Claude creates `tasks_completions_2025-10-04.json`:**
```json
{
  "operation_type": "Mark completed tasks",
  "generated_at": "2025-10-04T10:30:00",
  "completions": [
    {"content": "Pay rent", "task_id": "9431228119"},
    {"content": "Call dentist", "task_id": "9467234567"}
  ]
}
```

### Adding Tasks
**User:** "Add a task to grocery shop tomorrow, high priority"

**Claude creates `tasks_new-grocery_2025-10-04.json`:**
```json
{
  "operation_type": "Add grocery shopping task",
  "generated_at": "2025-10-04T14:00:00",
  "new_tasks": [
    {
      "content": "Grocery shopping",
      "project_name": "This week",
      "section_name": "Incoming",
      "due_date": "tomorrow",
      "priority": 2,
      "labels": ["Personal"]
    }
  ]
}
```

### Rescheduling
**User:** "Move my address update to Sunday"

**Claude creates `tasks_reschedule_2025-10-04.json`:**
```json
{
  "operation_type": "Reschedule address task to Sunday",
  "generated_at": "2025-10-04T16:00:00",
  "updates": [
    {
      "content": "Update remaining address details and passport",
      "task_id": "9382265058",
      "due_date": "2025-10-05"
    }
  ]
}
```

### Email Processing
**User:** "Review my pending emails"

**Claude:**
1. Checks `local_data/pending_operations/` directory
2. Finds `tasks_email_2025-10-04.json` with sanitized content
3. Extracts action items and suggests tasks to create
4. Updates the same file with `new_tasks` array populated

---

## File Structure

```
todoist-python/
├── README.md                      ← Overview & Claude instructions
├── QUICKSTART.md                  ← Setup & detailed usage
├── CHANGELOG.md                   ← Version history
│
├── daily_manager.py               ← Main CLI (start here!)
├── get_current_tasks.py           ← Export tasks
├── get_calendar_data.py           ← Export calendar
├── todoist_task_manager.py        ← Apply changes
├── process_emails.py              ← Process forwarded emails
├── biweekly_email_digest.py       ← Generate email digest
├── review_digest_interactive.py   ← Review & rate emails
│
└── local_data/
    ├── personal_data/             ← Claude reads these
    │   ├── current_tasks.json
    │   ├── calendar_full_analysis.json
    │   ├── email_interest_profile.json
    │   └── email_feedback_log.json
    ├── pending_operations/        ← Email operations to review
    └── email_digests/             ← Generated digests
```

---

## Privacy & Security

- 🔒 **Local-first**: All data stays on your machine + Todoist/Google servers
- 🔒 **No third-party storage**: Never uploads to unknown cloud services
- 🔒 **Dual trust system**: Verifies both email forwarder (security) and original sender (priority)
- 🔒 **Content sanitization**: Strips all URLs and email addresses before processing
- 🔒 **Credentials protected**: `.gitignore` prevents committing tokens/credentials
- ✅ **Open source**: Review all code - no hidden behavior

---

## Roadmap

**✅ Current (v1.3.1):**
- Complete Todoist integration
- Optional calendar analysis
- Email forwarding with dual trust system
- AI-powered email digest with learning
- Interactive review and feedback

**🚀 Next:**
- Email observation period (gather more feedback data)
- Local CRM foundation (client/sender database)
- Task templates for common patterns
- Analytics and productivity insights

Full version history: [CHANGELOG.md](CHANGELOG.md)

---

## Support & Contributing

**Getting Started:**
- 📚 [QUICKSTART.md](QUICKSTART.md) - Complete setup guide
- 📋 [CHANGELOG.md](CHANGELOG.md) - What's new
- ❓ Issues - Report bugs or request features

**Contributing:**
This is a personal productivity system, but:
- Bug reports welcome via GitHub issues
- Suggestions welcome via discussions  
- Forks encouraged (MIT license)

*Note: I keep contributions minimal to maintain system stability for personal use.*

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Ready to start?** → [QUICKSTART.md](QUICKSTART.md) ⚡

---

*Version 1.3.1 - Last updated: October 4, 2025*
