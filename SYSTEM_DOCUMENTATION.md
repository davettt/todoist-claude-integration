# Todoist + Claude Integration System Documentation

## System Overview
This system enables seamless task management by allowing Claude to create structured task files that are processed by Python scripts to interact with Todoist's API.

## Architecture
- **Claude AI**: Task processing and JSON generation  
- **Python Scripts**: API integration and task management
- **Todoist API**: Task creation, updates, and deletion
- **Local Storage**: Configuration and task file management

## Core Components

### Scripts
1. **todoist_manager.py** - Main menu interface
2. **todoist_task_manager.py** - Enhanced task processor (REST + Sync API)
3. **get_current_tasks.py** - Current task analysis
4. **get_todoist_config.py** - Configuration fetcher

### Configuration Files
- **.env** - API credentials (TODOIST_API_TOKEN)
- **todoist_reference.json** - Projects, sections, labels mapping
- **current_tasks.json** - Latest task snapshot

### Data Flow
1. User dictates tasks to Claude
2. Claude generates structured JSON files
3. Python script processes JSON via Todoist APIs
4. Tasks appear in Todoist and sync across devices
5. Processed files archived to prevent re-execution

## API Integration Details

### Todoist API Usage
- **REST API v2**: Task field updates (content, priority, labels, due dates)
- **Sync API v9**: Project/section moves (required for location changes)
- **Two-step process**: Update fields first, then move locations

### Authentication
- Bearer token authentication via .env file
- Token stored securely, never in code files

## Task Organization Schema

### Projects (Time-based)
- **Inbox**: Quick capture, unsorted items
- **This week**: Current focus with workflow stages
- **This month**: Medium-term planning and consideration
- **This year**: Long-term goals and ideas  
- **Experiments**: Categorized by life area
- **Subscriptions**: Simple list management

### Workflow Sections
- **Incoming**: New tasks, not yet planned
- **Plan**: Ready to be scheduled/organized  
- **In Progress**: Currently working on
- **Completed**: Done tasks
- **Backlog**: Future tasks, not immediate priority
- **Considering**: Ideas being evaluated
- **Pending**: Waiting on something/someone
- **Disregarded**: Decided not to pursue

### Labels (Context-based)
- **Work**: Professional/business tasks
- **Company**: Primary employment tasks  
- **Personal**: Non-work life tasks

*Note: Users customize these labels for their specific needs*

## Security & Data Handling

### Security Measures
- API token stored in .env file (gitignored)
- No sensitive data in code or JSON files
- Task content is personal but not financial/credential data
- Local processing, minimal cloud exposure

### Data Backup
- All processed files archived with timestamps
- Git repository for code versioning
- Todoist serves as primary data store
- Local files are processing artifacts, not primary storage

## Common Operations

### Adding New Tasks
```json
{
  "new_tasks": [{
    "content": "Task description",
    "project_name": "This week",
    "section_name": "Incoming",
    "labels": ["Personal"],
    "priority": 2,
    "due_date": "2025-09-25",
    "description": "Detailed context"
  }]
}
```

### Updating Existing Tasks
```json
{
  "updates": [{
    "content": "Existing task name (exact match required)",
    "project_name": "This month",
    "section_name": "Considering", 
    "labels": ["Personal"],
    "priority": 1,
    "due_date": "2025-10-15",
    "description": "Updated description"
  }]
}
```

### Deleting Tasks
```json
{
  "deletions": [{
    "content": "Task to remove",
    "reason": "No longer relevant"
  }]
}
```

## Error Handling & Recovery

### Common Issues
1. **Task not found**: Exact content match required for updates/deletions
2. **Project/section not found**: Check spelling against todoist_reference.json
3. **API rate limits**: Built-in error handling and retries
4. **Authentication errors**: Check .env file and token validity

### Recovery Procedures
1. **Lost configuration**: Run `get_todoist_config.py` to refresh
2. **Failed operations**: Check processed/ folder for what completed
3. **Corrupted files**: Regenerate from Todoist using current task scripts

## Maintenance

### Regular Tasks
- **Weekly**: Review current tasks and adjust projects
- **Monthly**: Clean up completed tasks and archive old files
- **Quarterly**: Review and update project/section structure

### Monitoring
- **File sizes**: Large JSON files indicate potential issues
- **Processed folder**: Monitor for failed operations
- **API responses**: Error patterns indicate systematic issues

## Future Enhancements

### Planned Improvements
1. **Recurring task templates** - Standardized task creation patterns
2. **Batch operation validation** - Preview changes before applying
3. **Task dependency mapping** - Project relationship tracking
4. **Performance analytics** - Task completion tracking
5. **Calendar integration** - Due date optimization based on schedule

### Extension Points
- **Additional APIs**: Calendar, email, note-taking apps
- **AI enhancements**: Better task categorization and scheduling
- **Mobile interface**: Direct task creation from phone
- **Team collaboration**: Shared project management

## Troubleshooting Guide

### Setup Issues
- **Missing .env**: Create file with TODOIST_API_TOKEN=your_token
- **Permission errors**: Check file system permissions
- **Import errors**: Install required packages (requests, python-dotenv)

### Runtime Issues  
- **Empty task files**: Verify JSON structure and file permissions
- **API failures**: Check network connectivity and token validity
- **Sync issues**: Allow time for Todoist propagation across devices

### Data Issues
- **Duplicate tasks**: Review processed files for re-execution
- **Missing tasks**: Check deletion logs and Todoist trash
- **Incorrect assignments**: Verify project/section mappings

---

*Last updated: 2025-09-22*
*System version: 1.0*
*Compatible with: Todoist API v2/v9, Claude Sonnet 4*
