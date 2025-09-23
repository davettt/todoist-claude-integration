import requests
import json
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_API_URL = "https://api.todoist.com/rest/v2/tasks"
TODOIST_SYNC_URL = "https://api.todoist.com/sync/v9/sync"

# Check if token is loaded
if not TODOIST_API_TOKEN:
    print("❌ Error: TODOIST_API_TOKEN not found!")
    print("Please create a .env file with your API token.")
    print("See setup instructions for details.")
    exit(1)

def get_all_tasks():
    """Fetch all tasks from Todoist to get task IDs"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get(TODOIST_API_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch tasks: {response.text}")
        return []

def get_projects_and_sections():
    """Fetch projects and sections for ID mapping"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    
    # Get projects
    projects_response = requests.get("https://api.todoist.com/rest/v2/projects", headers=headers)
    projects = projects_response.json() if projects_response.status_code == 200 else []
    project_map = {p['name']: p['id'] for p in projects}
    
    # Get sections
    sections_response = requests.get("https://api.todoist.com/rest/v2/sections", headers=headers)
    sections = sections_response.json() if sections_response.status_code == 200 else []
    section_map = {}
    for section in sections:
        project_id = section['project_id']
        section_name = section['name']
        if project_id not in section_map:
            section_map[project_id] = {}
        section_map[project_id][section_name] = section['id']
    
    return project_map, section_map

def find_task_by_content(all_tasks, content):
    """Find a task by its content"""
    for task in all_tasks:
        if task['content'] == content:
            return task
    return None

def create_todoist_task(task_data):
    """Create a single task in Todoist"""
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(TODOIST_API_URL, headers=headers, json=task_data)
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Created: {task['content']}")
        return task
    else:
        print(f"❌ Failed to create task: {task_data['content']}")
        print(f"Error: {response.text}")
        return None

def update_task_fields(task_id, task_data):
    """Update task fields that work with REST API (not project/section)"""
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Only include fields that work with REST API
    update_data = {}
    
    for field in ['content', 'description', 'priority', 'labels', 'due_string']:
        if field in task_data:
            update_data[field] = task_data[field]
    
    if not update_data:
        return True  # Nothing to update
    
    response = requests.post(f"{TODOIST_API_URL}/{task_id}", headers=headers, json=update_data)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to update task fields: {response.text}")
        return False

def move_task_to_project_and_section(task_id, project_id, section_id=None):
    """Move task using Sync API (supports project/section moves)"""
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    commands = []
    
    # Step 1: Move to project if specified
    if project_id:
        move_project_uuid = str(uuid.uuid4())
        commands.append({
            "type": "item_move",
            "uuid": move_project_uuid,
            "args": {
                "id": task_id,
                "project_id": int(project_id)
            }
        })
    
    # Step 2: Move to section if specified (separate command)
    if section_id:
        move_section_uuid = str(uuid.uuid4())
        commands.append({
            "type": "item_move",
            "uuid": move_section_uuid,
            "args": {
                "id": task_id,
                "section_id": int(section_id)
            }
        })
    
    if not commands:
        return True  # Nothing to move
    
    # Execute all commands
    sync_data = {"commands": commands}
    
    response = requests.post(TODOIST_SYNC_URL, headers=headers, json=sync_data)
    
    if response.status_code == 200:
        result = response.json()
        
        # Check for errors in sync_status
        if 'sync_status' in result:
            for command_uuid, status in result['sync_status'].items():
                if 'error' in status:
                    print(f"❌ Move command failed: {status['error']}")
                    return False
        
        return True
    else:
        print(f"❌ Failed to move task: {response.text}")
        return False

def delete_todoist_task(task_id, content):
    """Delete a task from Todoist"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    
    response = requests.delete(f"{TODOIST_API_URL}/{task_id}", headers=headers)
    
    if response.status_code == 204:
        print(f"🗑️  Deleted: {content}")
        return True
    else:
        print(f"❌ Failed to delete task: {content}")
        print(f"Error: {response.text}")
        return False

def prepare_task_data(task, project_map, section_map):
    """Prepare task data for Todoist API"""
    todoist_task = {
        "content": task["content"],
        "description": task.get("description", ""),
        "priority": task.get("priority", 1)
    }
    
    # Add due date if provided
    if task.get("due_date"):
        todoist_task["due_string"] = task["due_date"]
    
    # Add labels if specified
    if task.get("labels"):
        todoist_task["labels"] = task["labels"]
    
    # Store project/section info separately for move operations
    project_id = None
    section_id = None
    
    if task.get("project_name"):
        project_id = project_map.get(task["project_name"])
    
    if task.get("section_name") and task.get("project_name"):
        project_id_for_section = project_map.get(task["project_name"])
        if project_id_for_section and project_id_for_section in section_map:
            section_id = section_map[project_id_for_section].get(task["section_name"])
    
    return todoist_task, project_id, section_id

def find_task_files():
    """Find all task JSON files in the current directory"""
    import glob
    import os
    
    # Look for tasks.json or tasks_*.json files
    json_files = glob.glob("tasks*.json")
    
    if not json_files:
        return None
    
    # Sort by modification time (newest first)
    json_files.sort(key=os.path.getmtime, reverse=True)
    return json_files

def archive_processed_file(filename):
    """Move processed file to archive folder"""
    import os
    import shutil
    from datetime import datetime
    
    # Create processed folder if it doesn't exist
    archive_dir = "processed"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(filename)[0]
    archived_name = f"{base_name}_{timestamp}.json"
    
    # Move file
    shutil.move(filename, os.path.join(archive_dir, archived_name))
    print(f"📁 Archived {filename} → processed/{archived_name}")

def process_task_operations():
    """Process task operations from Claude's JSON files"""
    
    # Find task files
    task_files = find_task_files()
    
    if not task_files:
        print("❌ No task files found!")
        print("Expected files: tasks.json or tasks_YYYY-MM-DD.json")
        print("💡 Ask Claude to create a task file for you!")
        return
    
    # Use the newest file
    task_file = task_files[0]
    print(f"📄 Found task file: {task_file}")
    
    if len(task_files) > 1:
        print(f"ℹ️  Note: {len(task_files)} task files found, using newest: {task_file}")
    
    try:
        # Read the JSON file
        with open(task_file, 'r') as f:
            data = json.load(f)
        
        # Get current tasks and project mappings
        print("🔄 Fetching current Todoist data...")
        all_tasks = get_all_tasks()
        project_map, section_map = get_projects_and_sections()
        
        # Process different types of operations
        updates = data.get("updates", [])
        deletions = data.get("deletions", [])
        new_tasks = data.get("new_tasks", [])
        
        total_operations = len(updates) + len(deletions) + len(new_tasks)
        
        if total_operations == 0:
            print("❌ No operations found in file!")
            return
        
        print(f"📋 Found {len(updates)} updates, {len(deletions)} deletions, {len(new_tasks)} new tasks")
        print("-" * 50)
        
        # Show preview of operations
        if updates:
            print("🔄 UPDATES:")
            for task in updates:
                print(f"  • {task['content']} → {task.get('project_name', 'Unknown project')}")
        
        if deletions:
            print("🗑️  DELETIONS:")
            for task in deletions:
                print(f"  • {task['content']}")
        
        if new_tasks:
            print("➕ NEW TASKS:")
            for task in new_tasks:
                print(f"  • {task['content']} → {task.get('project_name', 'Unknown project')}")
        
        print("-" * 50)
        
        # Ask for confirmation
        confirm = input("Apply these changes to Todoist? (y/n): ").lower().strip()
        
        if confirm != 'y':
            print("❌ Cancelled. No changes made.")
            return
        
        # Process operations
        success_count = 0
        
        # 1. Process deletions first
        for task_info in deletions:
            existing_task = find_task_by_content(all_tasks, task_info['content'])
            if existing_task:
                if delete_todoist_task(existing_task['id'], task_info['content']):
                    success_count += 1
            else:
                print(f"⚠️  Task not found for deletion: {task_info['content']}")
        
        # 2. Process updates
        for task_info in updates:
            existing_task = find_task_by_content(all_tasks, task_info['content'])
            if existing_task:
                task_data, project_id, section_id = prepare_task_data(task_info, project_map, section_map)
                
                # Update fields first
                field_success = update_task_fields(existing_task['id'], task_data)
                
                # Then move if needed
                move_success = True
                if project_id or section_id:
                    move_success = move_task_to_project_and_section(
                        existing_task['id'], project_id, section_id
                    )
                
                if field_success and move_success:
                    print(f"✅ Updated: {task_info['content']}")
                    success_count += 1
                else:
                    print(f"⚠️  Partial update for: {task_info['content']}")
            else:
                print(f"⚠️  Task not found for update: {task_info['content']}")
        
        # 3. Process new tasks
        for task_info in new_tasks:
            task_data, project_id, section_id = prepare_task_data(task_info, project_map, section_map)
            
            # Create task first
            created_task = create_todoist_task(task_data)
            if created_task:
                # Then move if needed
                if project_id or section_id:
                    move_task_to_project_and_section(created_task['id'], project_id, section_id)
                success_count += 1
        
        print("-" * 50)
        print(f"✨ Successfully processed {success_count} out of {total_operations} operations!")
        
        # Archive the processed file
        if success_count > 0:
            archive_processed_file(task_file)
        
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {task_file}")
    except FileNotFoundError:
        print(f"❌ Error: Could not read {task_file}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Todoist Task Manager (Enhanced with Sync API)")
    print("=" * 50)
    print("Supports: Creating, Updating, Moving, and Deleting tasks")
    print()
    
    # Process task operations from Claude
    process_task_operations()
