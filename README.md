# Todoist + Claude Integration

*Intelligent task management by dictating to Claude AI and automatically syncing with Todoist*

## Features

✅ **Voice-to-Tasks**: Dictate tasks to Claude, get organized JSON files  
✅ **Complete CRUD Operations**: Create, update, move, and delete tasks  
✅ **Smart Organization**: Automatic project and section assignment  
✅ **Batch Processing**: Handle multiple operations in one go  
✅ **Safe Operations**: Preview changes before applying  
✅ **Future-Proof**: Comprehensive documentation for easy setup  

## How It Works

1. **Talk to Claude**: Describe your tasks and goals naturally
2. **Get Structured Data**: Claude creates organized JSON files
3. **Process Automatically**: Python scripts sync everything to Todoist
4. **Access Everywhere**: Tasks appear on all your devices instantly

## Quick Start

### Prerequisites
- Python 3.7+
- Todoist account with API access
- Claude AI access (claude.ai)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/todoist-claude-integration.git
cd todoist-claude-integration
```

2. **Install dependencies**
```bash
pip install requests python-dotenv
```

3. **Configure your API token**
```bash
cp .env.example .env
# Edit .env and add your Todoist API token
```

4. **Set up your Todoist configuration**
```bash
python3 get_todoist_config.py
```

5. **Start managing tasks**
```bash
python3 todoist_manager.py
```

## Documentation

- 📚 **[System Documentation](SYSTEM_DOCUMENTATION.md)** - Complete technical guide
- 🚀 **[Quick Start for Claude](CLAUDE_QUICKSTART.md)** - Claude AI integration guide  
- 🔒 **[Security Guidelines](SECURITY_CHECKLIST.md)** - Best practices and security
- 🛠️ **[Roadmap](IMPROVEMENTS_ROADMAP.md)** - Planned features and improvements

## Core Scripts

- **`todoist_manager.py`** - Main menu interface
- **`todoist_task_manager.py`** - Enhanced task processor  
- **`get_current_tasks.py`** - Current task analysis
- **`get_todoist_config.py`** - Configuration setup

## Example Workflow

**You:** "I need to update my website, call the dentist, and plan next week's meetings"

**Claude:** Creates structured JSON file:
```json
{
  "new_tasks": [
    {
      "content": "Update website homepage",
      "project_name": "This week", 
      "section_name": "Incoming",
      "labels": ["Work"],
      "priority": 2,
      "due_date": "2025-09-25"
    }
  ]
}
```

**System:** Processes file and creates tasks in Todoist automatically.

## Project Structure

```
todoist-claude-integration/
├── todoist_manager.py          # Main interface
├── todoist_task_manager.py     # Task processor
├── get_current_tasks.py        # Status checker
├── get_todoist_config.py       # Configuration
├── .env.example               # Environment template
├── .gitignore                 # Git exclusions
├── processed/                 # Archived operations
└── docs/                      # Documentation
```

## Security & Privacy

- 🔒 **API tokens** stored in local `.env` file (never committed)
- 🏠 **Task data** stays on your machine and Todoist
- 🚫 **No cloud storage** of sensitive information
- ✅ **Open source** - review all code

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Task templates for common patterns
- [ ] Calendar integration for smart scheduling  
- [ ] Mobile quick-add interface
- [ ] Analytics and productivity insights
- [ ] Team collaboration features

## License & Disclaimer

MIT License - see [LICENSE](LICENSE) file for details

⚠️  **Important:** This software is provided "as is" without warranty. Users are responsible for:
- Securing their API tokens and personal data
- Testing the system with non-critical tasks first  
- Regular backups of important task data
- Understanding the code before running it

**Use at your own risk.** The authors are not responsible for any data loss, API quota exhaustion, or unintended task modifications.

## Support

- 📖 Read the [documentation](SYSTEM_DOCUMENTATION.md)
- 🐛 Report issues on GitHub
- 💡 Suggest features in discussions

---

*Supercharge your productivity with AI-powered task management!*
