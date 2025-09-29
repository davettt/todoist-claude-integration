# Quick Start Guide

Get up and running in 5 minutes.

---

## First Time Setup

### 1. Install
```bash
cd todoist-python
pip3 install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
```

Edit `.env` and add your Todoist API token:
```
TODOIST_API_TOKEN=your_token_here
```

Get token: [Todoist Settings → Integrations → API token](https://todoist.com/prefs/integrations)

### 3. Initialize
```bash
python3 get_todoist_config.py
```

### 4. Optional: Google Calendar
- Get credentials from [Google Cloud Console](https://console.cloud.google.com)
- Save as `local_data/calendar_credentials.json`
- Run: `python3 get_calendar_data.py`

---

## Daily Use - Simple CLI

**Just run one command:**
```bash
python3 daily_manager.py
```

This gives you a simple menu to do everything:

```
📋 DAILY WORKFLOW (Do these in order):
  1. 📤 Export data (Step 1)
  2. 💬 Instructions for Claude (Step 2)
  3. ✅ Apply changes (Step 3)

📊 VIEWS:
  4. 📋 View my current tasks
  5. 📅 View my calendar

⚙️ SETUP & HELP:
  6. 🔧 First-time setup
  7. 📖 Show full workflow guide
  8. 🚪 Exit
```

**That's it!** Everything you need is in this one interface.

---

## The 3-Step Daily Workflow

### Step 1: Export (Option 1)
Saves your current tasks and calendar to files Claude can read.

### Step 2: Talk to Claude (Option 2)
The menu shows you exactly what to say to Claude. Just copy/paste:

```
Please help me manage my tasks today. 

Read these files from my todoist-python folder:
- local_data/personal_data/current_tasks.json
- local_data/personal_data/calendar_full_analysis.json (if available)

Then follow the instructions in the "For Claude" section of README.md
```

Claude will:
- ✅ Review your tasks and calendar
- ✅ Help you plan your day
- ✅ Create task operation files as needed

### Step 3: Apply Changes (Option 3)
If Claude created any changes, this applies them to your Todoist.

---

## Alternative: Command Line

If you prefer running commands directly instead of the menu:

```bash
# Step 1: Export
python3 get_current_tasks.py
python3 get_calendar_data.py

# Step 2: Talk to Claude (copy instructions from Option 2)

# Step 3: Apply changes
python3 todoist_task_manager.py
```

But the menu (`daily_manager.py`) is easier! 😊

---

## For Claude: Task Operation Instructions

When the user asks for help with tasks, follow these guidelines:

### 1. Review Current State
Read files in `local_data/personal_data/`:
- `current_tasks.json` - Today's priorities
- `calendar_full_analysis.json` - Schedule (if available)

### 2. Create Operation Files

**Format:** `tasks_[description]_YYYY-MM-DD.json`

**Structure:**
```json
{
  "operation_type": "Brief description",
  "generated_at": "2025-09-29T17:00:00",
  "completions": [
    {"content": "Exact task name from Todoist"}
  ],
  "updates": [
    {
      "content": "Exact task name",
      "project_name": "Project",
      "section_name": "Section",
      "due_date": "YYYY-MM-DD",
      "priority": 2,
      "labels": ["Personal"]
    }
  ],
  "deletions": [
    {"content": "Exact task name"}
  ],
  "new_tasks": [
    {
      "content": "New task",
      "project_name": "This week",
      "section_name": "In Progress",
      "due_date": "tomorrow",
      "priority": 2,
      "labels": ["Personal"]
    }
  ]
}
```

### 3. Key Rules

**Use EXACT task names** from the JSON files

**Completions vs Deletions:**
- ✅ Use `completions` for: "done", "finished", "mark complete"
- 🗑️ Use `deletions` for: "delete", "remove permanently"
- **Important:** Completions preserve history and advance recurring tasks

**Priority levels:**
- 1 = Urgent/P1
- 2 = High/P2  
- 3 = Medium/P3
- 4 = Low/P4

**Due dates:**
- Natural language: "tomorrow", "next week"
- Specific: "YYYY-MM-DD"

### 4. After Creating File

Tell the user:
1. What operations are in the file
2. To choose option 3 in daily_manager.py (or run `python3 todoist_task_manager.py`)
3. What will happen when they apply it

---

## Quick Tips

**Check tasks anytime:**
- Run `daily_manager.py`
- Choose option 4 (View current tasks)
- Or option 5 (View calendar)

**No need to remember commands:**
- Everything is in the `daily_manager.py` menu
- It guides you through the 3 steps
- Shows you exactly what to say to Claude

**Start fresh each day:**
- Export new data (Option 1)
- New conversation with Claude
- Apply changes (Option 3)

---

## Troubleshooting

**"No task files found"**
- Claude hasn't created operation files yet
- Or files not named `tasks*.json`

**"Task not found"**
- Task name doesn't match exactly
- Check exact names in Option 4 (View current tasks)

**"Connection error"**
- Check `.env` has correct `TODOIST_API_TOKEN`

---

## Advanced Interface (Optional)

For power users who need more control:
```bash
python3 todoist_manager.py
```

This provides 13 menu options including:
- File management and history
- Detailed system information  
- Advanced configuration views

Most users won't need this - `daily_manager.py` has everything! 😊

---

## Important Notes

**Folder creation:**
- `local_data/` folders are created automatically on first run
- You don't need to create them manually
- They appear when you run any export script or menu

**Files location:**
- Your task data: `local_data/personal_data/`
- Processed operations: `local_data/processed/`
- Backups: `local_data/backups/`

---

## What's Next?

- Read [README.md](README.md) for complete details
- Run `python3 daily_manager.py` and explore
- Try the 3-step workflow with Claude

**You're all set!** 🚀

---

*Tip: Bookmark `daily_manager.py` - it's your one-stop interface for everything.*
