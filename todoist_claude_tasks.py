import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_API_URL = "https://api.todoist.com/rest/v2/tasks"

# Check if token is loaded
if not TODOIST_API_TOKEN:
    print("❌ Error: TODOIST_API_TOKEN not found!")
    print("Please create a .env file with your API token.")
    print("See setup instructions for details.")
    exit(1)

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

def process_claude_tasks():
    """
    Process tasks from Claude's JSON files
    """

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

        tasks = data.get("tasks", [])

        if not tasks:
            print("❌ No tasks found in file!")
            return

        print(f"📋 Processing {len(tasks)} tasks from {task_file}...")
        print("-" * 50)

        # Show preview of tasks
        for i, task in enumerate(tasks, 1):
            due_info = f" (due: {task.get('due_date', 'no date')})" if task.get('due_date') else ""
            priority_info = f" [P{task.get('priority', 1)}]" if task.get('priority', 1) > 1 else ""
            print(f"  {i}. {task['content']}{due_info}{priority_info}")

        print("-" * 50)

        # Ask for confirmation
        confirm = input("Create these tasks in Todoist? (y/n): ").lower().strip()

        if confirm != 'y':
            print("❌ Cancelled. No tasks created.")
            return

        created_count = 0

        for task in tasks:
            # Prepare task data for Todoist API
            todoist_task = {
                "content": task["content"],
                "description": task.get("description", ""),
                "priority": task.get("priority", 1)
            }

            # Add due date if provided
            if task.get("due_date"):
                todoist_task["due_string"] = task["due_date"]

            # Create the task
            if create_todoist_task(todoist_task):
                created_count += 1

        print("-" * 50)
        print(f"✨ Successfully created {created_count} out of {len(tasks)} tasks!")

        # Archive the processed file
        if created_count > 0:
            archive_processed_file(task_file)

    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {task_file}")
    except FileNotFoundError:
        print(f"❌ Error: Could not read {task_file}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def get_todoist_projects():
    """Helper function to see your existing Todoist projects"""
    headers = {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}"
    }

    response = requests.get("https://api.todoist.com/rest/v2/projects", headers=headers)

    if response.status_code == 200:
        projects = response.json()
        print("📁 Your Todoist Projects:")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")
    else:
        print("❌ Failed to fetch projects")

if __name__ == "__main__":
    print("🚀 Todoist Task Creator")
    print("=" * 30)

    # Uncomment the next line to see your existing projects
    # get_todoist_projects()

    # Process tasks from Claude
    process_claude_tasks()
