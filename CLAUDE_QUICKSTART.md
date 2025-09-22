# Claude + Todoist Integration System

## Quick Start for New Claude Conversations

**When starting a new Claude conversation, use this approach:**

1. Tell Claude about your Todoist integration system
2. Ask Claude to read the documentation files in your project folder
3. Claude will understand your setup and be ready to help

---

## System Overview for Claude

This is a Python-based system that integrates Claude AI with Todoist for intelligent task management.

### How It Works
1. User dictates tasks to Claude
2. Claude creates JSON files with structured task data
3. Python scripts process JSON files to create/update/delete Todoist tasks
4. Tasks sync across all devices automatically

### Key Components
- **Main interface:** `todoist_manager.py`
- **Task processor:** `todoist_task_manager.py` 
- **Status checker:** `get_current_tasks.py`
- **Configuration:** Generated dynamically from user's Todoist setup

### JSON Format for Tasks
```json
{
  "operation_type": "description",
  "updates": [
    {
      "content": "Task name",
      "project_name": "Project Name",
      "section_name": "Section Name", 
      "labels": ["label1", "label2"],
      "priority": 2,
      "due_date": "2025-09-25",
      "description": "Detailed description"
    }
  ],
  "deletions": [{"content": "Task to delete", "reason": "No longer needed"}],
  "new_tasks": []
}
```

### Getting Started
1. **Review current tasks:** User runs `get_current_tasks.py` 
2. **Check configuration:** Read `todoist_reference.json` for user's setup
3. **Create task files:** Generate JSON files using the format above
4. **Process tasks:** User runs `todoist_task_manager.py` to apply changes

### Workflow Tips
- Always check current task load before adding new tasks
- Use user's actual project and section names from their configuration
- Suggest realistic due dates based on workload
- Group related tasks in single operations for efficiency

---

## For Users Setting Up

Replace this quickstart guide with your personal version containing:
- Your specific project structure
- Your labels and workflow
- Your file paths and preferences  
- Your task assignment logic

This template provides the framework - customize it for your needs!
