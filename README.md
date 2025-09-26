# Todoist + Claude Integration

*Intelligent task management by dictating to Claude AI and automatically syncing with Todoist*

## Features

✅ **Voice-to-Tasks**: Dictate tasks to Claude, get organized JSON files  
✅ **Complete CRUD Operations**: Create, update, move, and delete tasks  
✅ **Smart Organization**: Automatic project and section assignment  
✅ **Batch Processing**: Handle multiple operations in one go  
✅ **Safe Operations**: Preview changes before applying  
✅ **Multi-File Intelligence**: Smart handling of multiple task files with user guidance  

## Quick Start

### Prerequisites
- Python 3.7+
- Todoist account with API access
- Claude AI access (claude.ai)

### Installation
```bash
git clone [your-repo-url]
cd todoist-claude-integration
pip install requests python-dotenv
cp .env.example .env
# Add your Todoist API token to .env
python3 get_todoist_config.py
python3 get_current_tasks.py
```

## How It Works

1. **Talk to Claude**: Describe your tasks and goals naturally
2. **Get Structured Data**: Claude creates organized JSON files
3. **Process Automatically**: Python scripts sync everything to Todoist
4. **Access Everywhere**: Tasks appear on all your devices instantly

## Example Workflow

**You:** "I need to update my website, call the dentist, and plan next week's meetings"

**Claude:** Creates structured JSON file with proper projects, sections, and due dates

**System:** Processes file and creates tasks in Todoist automatically

## Using with Claude

**Start any Claude conversation with:**
```
I have a Todoist + Claude integration system. Please read the documentation files in this folder:

[YOUR_FOLDER_PATH]

Start with examining local_data/personal_data/current_tasks.json to see my current task state.
```

## Core Scripts

- `todoist_manager.py` - Main menu interface
- `todoist_task_manager.py` - Enhanced task processor
- `get_current_tasks.py` - Current task analysis
- `get_todoist_config.py` - Configuration setup

## Daily Commands

```bash
# Check current tasks
python3 get_current_tasks.py

# Process task files from Claude
python3 todoist_task_manager.py

# Update your Todoist configuration
python3 get_todoist_config.py
```

## Project Structure

```
todoist-claude-integration/
├── README.md                    # This file
├── USER_START.md               # Setup guide for new users
├── Core Python scripts         # Main functionality
├── .env.example               # Environment template
└── local_data/               # Personal files (not in git)
    ├── personal_data/        # Your tasks and config
    ├── processed/           # Task history
    └── backups/            # Archive files
```

## Security & Privacy

- 🔒 **API tokens** stored in local `.env` file (never committed)
- 🏠 **Task data** stays on your machine and Todoist
- 🚫 **No cloud storage** of sensitive information
- ✅ **Open source** - review all code

## Usage & Forking

This project is open source under MIT license. You're welcome to:
- **Fork the repository** and customize for your needs
- **Report bugs** via GitHub issues 
- **Suggest improvements** in discussions

*Note: This is a personal productivity system. While the code is open source, I keep contributions minimal to maintain system stability.*

## Roadmap

- [x] Multi-file intelligence and smart cleanup
- [ ] Calendar integration for smart scheduling  
- [ ] Task templates for common patterns
- [ ] Mobile quick-add interface
- [ ] Analytics and productivity insights

## Important Disclaimers

⚠️  **Use at your own risk:** This software is provided "as is" without warranty. Users are responsible for:
- Securing API tokens and personal data
- Testing with non-critical tasks first  
- Regular backups of important task data
- Understanding the code before running it

## Support

- 📖 Read USER_START.md for detailed setup
- 🐛 Report issues on GitHub
- 💡 Suggest features in discussions

---

*Supercharge your productivity with AI-powered task management!*