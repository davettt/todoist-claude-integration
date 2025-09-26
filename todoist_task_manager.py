"""
Enhanced Todoist Task Manager with modular architecture
Processes Claude-generated JSON files using the new API client structure
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.todoist_client import TodoistClient
from utils.file_manager import (
    find_operation_files, 
    handle_multiple_files, 
    archive_processed_file,
    get_file_preview
)

def process_single_file(task_file: str, todoist_client: TodoistClient) -> int:
    """
    Process a single task file with enhanced error handling
    
    Args:
        task_file: Path to JSON file containing task operations
        todoist_client: Initialized Todoist API client
        
    Returns:
        Number of successful operations
    """
    print(f"\n📄 Processing: {task_file}")
    print("-" * 50)
    
    try:
        # Read the JSON file
        with open(task_file, 'r') as f:
            data = json.load(f)
        
        # Extract operations
        updates = data.get("updates", [])
        deletions = data.get("deletions", [])
        new_tasks = data.get("new_tasks", [])
        
        total_operations = len(updates) + len(deletions) + len(new_tasks)
        
        if total_operations == 0:
            print("⚠️ No operations found in this file!")
            return 0
        
        print(f"📋 Found {len(updates)} updates, {len(deletions)} deletions, {len(new_tasks)} new tasks")
        
        # Show preview of operations
        if updates:
            print("\n🔄 UPDATES:")
            for task in updates:
                project = task.get('project_name', 'Unknown project')
                print(f"  • {task['content']} → {project}")
        
        if deletions:
            print("\n🗑️ DELETIONS:")
            for task in deletions:
                print(f"  • {task['content']}")
        
        if new_tasks:
            print("\n➕ NEW TASKS:")
            for task in new_tasks:
                project = task.get('project_name', 'Unknown project')
                print(f"  • {task['content']} → {project}")
        
        print("-" * 50)
        
        # Ask for confirmation
        confirm = input(f"Apply these changes from {task_file}? (y/n): ").lower().strip()
        
        if confirm != 'y':
            print("⚠️ Skipped this file.")
            return 0
        
        # Get current tasks and project mappings
        print("🔄 Fetching current Todoist data...")
        existing_tasks = todoist_client.get_all_tasks()
        if existing_tasks is None:
            print("❌ Failed to fetch existing tasks")
            return 0
        
        project_map, section_map = todoist_client.build_project_mappings()
        if not project_map:
            print("❌ Failed to fetch project mappings")
            return 0
        
        # Process operations
        success_count = 0
        
        # 1. Process deletions first
        print("\n🗑️ Processing deletions...")
        for task_info in deletions:
            if todoist_client.process_task_operation(
                task_info, "delete", existing_tasks, project_map, section_map
            ):
                success_count += 1
        
        # 2. Process updates
        if updates:
            print("\n🔄 Processing updates...")
            for task_info in updates:
                if todoist_client.process_task_operation(
                    task_info, "update", existing_tasks, project_map, section_map
                ):
                    success_count += 1
        
        # 3. Process new tasks
        if new_tasks:
            print("\n➕ Processing new tasks...")
            for task_info in new_tasks:
                if todoist_client.process_task_operation(
                    task_info, "create", existing_tasks, project_map, section_map
                ):
                    success_count += 1
        
        print(f"\n✨ Processed {success_count} out of {total_operations} operations from {task_file}")
        
        # Archive the processed file
        if success_count > 0:
            archive_processed_file(task_file)
        
        return success_count
        
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {task_file}")
        return 0
    except FileNotFoundError:
        print(f"❌ Error: Could not read {task_file}")
        return 0
    except Exception as e:
        print(f"❌ Error processing {task_file}: {str(e)}")
        return 0

def process_task_operations():
    """Main function to process task operations from Claude's JSON files"""
    print("🚀 Enhanced Todoist Task Manager")
    print("=" * 50)
    print("Supports: Creating, Updating, Moving, and Deleting tasks")
    print("Features: Modular architecture, enhanced error handling, smart file management")
    print()
    
    try:
        # Initialize Todoist client
        print("🔄 Initializing Todoist connection...")
        todoist_client = TodoistClient()
        print("✅ Connected to Todoist API")
        
    except ValueError as e:
        print(str(e))
        print("\nPlease check your .env file and try again.")
        return
    except Exception as e:
        print(f"❌ Failed to initialize Todoist client: {str(e)}")
        return
    
    # Find task files
    task_files = find_operation_files()
    
    if not task_files:
        print("❌ No task files found!")
        print("Expected files: tasks.json or tasks_YYYY-MM-DD.json")
        print("💡 Ask Claude to create a task file for you!")
        return
    
    # Handle multiple files intelligently
    if len(task_files) > 1:
        print(f"🔍 Found {len(task_files)} task files")
        task_files = handle_multiple_files(task_files)
        if task_files is None:  # User cancelled
            return
    
    # Process selected files
    total_success = 0
    for task_file in task_files:
        success_count = process_single_file(task_file, todoist_client)
        total_success += success_count
        
        # If processing multiple files, add some spacing
        if len(task_files) > 1 and task_file != task_files[-1]:
            print("\n" + "=" * 30)
    
    print("\n" + "=" * 50)
    files_text = "file" if len(task_files) == 1 else "files"
    print(f"🎉 COMPLETE: Successfully processed {total_success} operations across {len(task_files)} {files_text}!")

if __name__ == "__main__":
    process_task_operations()