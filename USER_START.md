# Getting Started

*Quick setup guide for new users*

## Installation

1. **Clone and install:**
   ```bash
   git clone [repo-url]
   cd todoist-claude-integration
   pip install requests python-dotenv
   ```

2. **Get your Todoist API token:**
   - Go to [Todoist Integrations](https://todoist.com/prefs/integrations)
   - Copy your API token

3. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env and add: TODOIST_API_TOKEN=your_token_here
   ```

4. **Initialize:**
   ```bash
   python3 get_todoist_config.py
   python3 get_current_tasks.py
   ```

## First Use

1. **Start a Claude conversation with:**
   ```
   I have a Todoist + Claude integration system at [YOUR_FOLDER_PATH]. 
   Please examine local_data/personal_data/current_tasks.json to see my tasks, 
   then help me manage them.
   ```

2. **Tell Claude what you need to do:**
   - "I need to call the dentist tomorrow and update my website this week"

3. **Process the tasks:**
   ```bash
   python3 todoist_task_manager.py
   ```

4. **Check your Todoist** - tasks appear automatically!

## Daily Workflow

- `python3 get_current_tasks.py` → See current tasks
- Ask Claude to create/update tasks → JSON file created
- `python3 todoist_task_manager.py` → Apply changes
- Tasks sync to all devices

## Customization

Edit your project names, labels, and workflow patterns in the generated configuration files to match your Todoist setup.

---

*That's it! The system learns your Todoist structure and helps Claude create properly organized tasks.*