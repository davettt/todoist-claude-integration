"""
File management utilities for Todoist + Claude integration
Standardized patterns for local_data/ structure and multi-file handling
"""

import os
import shutil
import glob
from datetime import datetime
from typing import List, Optional, Dict, Any

# Standardized directory structure
LOCAL_DATA_DIR = "local_data/personal_data"
PROCESSED_DIR = "local_data/processed"
BACKUPS_DIR = "local_data/backups"

def ensure_local_data_structure():
    """Create local_data directory structure if it doesn't exist"""
    directories = [LOCAL_DATA_DIR, PROCESSED_DIR, BACKUPS_DIR]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def get_personal_data_path(filename: str) -> str:
    """Get full path for personal data file"""
    ensure_local_data_structure()
    return os.path.join(LOCAL_DATA_DIR, filename)

def get_processed_path(filename: str) -> str:
    """Get full path for processed file"""
    ensure_local_data_structure()
    return os.path.join(PROCESSED_DIR, filename)

def save_personal_data(filename: str, data: Dict[Any, Any]) -> None:
    """Save data to personal_data directory"""
    import json
    
    filepath = get_personal_data_path(filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Saved: {filepath}")

def load_personal_data(filename: str) -> Optional[Dict[Any, Any]]:
    """Load data from personal_data directory"""
    import json
    
    filepath = get_personal_data_path(filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def find_operation_files(pattern: str = "tasks*.json") -> List[str]:
    """Find operation files in root directory and pending_operations directory"""
    # Check root directory (legacy location)
    json_files = glob.glob(pattern)
    
    # Check pending_operations directory (new location for email operations)
    pending_ops_dir = "local_data/pending_operations"
    if os.path.exists(pending_ops_dir):
        pending_pattern = os.path.join(pending_ops_dir, pattern)
        pending_files = glob.glob(pending_pattern)
        json_files.extend(pending_files)
    
    if json_files:
        # Sort by modification time (newest first)
        json_files.sort(key=os.path.getmtime, reverse=True)
    
    return json_files

def archive_processed_file(filename: str, operation_type: str = "operation") -> None:
    """Archive a processed file with timestamp"""
    ensure_local_data_structure()
    
    if not os.path.exists(filename):
        print(f"⚠️ File not found: {filename}")
        return
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(filename)[0]
    archived_name = f"{base_name}_{timestamp}.json"
    
    # Move to processed directory
    archived_path = os.path.join(PROCESSED_DIR, archived_name)
    shutil.move(filename, archived_path)
    
    print(f"📁 Archived {filename} → {archived_path}")

def get_file_preview(filename: str) -> Dict[str, Any]:
    """Get a preview of what's in a task operation file"""
    try:
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Todoist-specific operation file structure
        updates = len(data.get("updates", []))
        deletions = len(data.get("deletions", []))
        new_tasks = len(data.get("new_tasks", []))
        
        description = data.get("operation_type", data.get("description", ""))
        if len(description) > 60:
            description = description[:60] + "..."
        
        return {
            "updates": updates,
            "deletions": deletions,
            "new_tasks": new_tasks,
            "description": description,
            "total": updates + deletions + new_tasks,
            "timestamp": datetime.fromtimestamp(os.path.getmtime(filename))
        }
    except Exception as e:
        return {"error": f"Cannot read file: {str(e)}"}

def handle_multiple_files(files: List[str]) -> Optional[List[str]]:
    """
    Handle multiple task files with user guidance
    Returns list of files to process, or None if cancelled
    """
    if len(files) <= 1:
        return files
    
    print("🔍 MULTIPLE TASK FILES DETECTED")
    print("=" * 50)
    
    # Show file details with previews
    for i, filename in enumerate(files):
        preview = get_file_preview(filename)
        newest_indicator = " (newest)" if i == 0 else ""
        
        print(f"📄 {filename}{newest_indicator}")
        
        if "error" in preview:
            print(f"   └── ❌ {preview['error']}")
        else:
            age = datetime.now() - preview['timestamp']
            if age.days > 0:
                age_str = f"{age.days} day{'s' if age.days != 1 else ''} old"
            elif age.seconds > 3600:
                hours = age.seconds // 3600
                age_str = f"{hours} hour{'s' if hours != 1 else ''} old"
            else:
                minutes = age.seconds // 60
                age_str = f"{minutes} minute{'s' if minutes != 1 else ''} old"
            
            print(f"   ├── {age_str}")
            
            if preview['description']:
                print(f"   ├── {preview['description']}")
            
            operations = []
            if preview['updates'] > 0:
                operations.append(f"{preview['updates']} update{'s' if preview['updates'] != 1 else ''}")
            if preview['deletions'] > 0:
                operations.append(f"{preview['deletions']} deletion{'s' if preview['deletions'] != 1 else ''}")
            if preview['new_tasks'] > 0:
                operations.append(f"{preview['new_tasks']} new task{'s' if preview['new_tasks'] != 1 else ''}")
            
            if operations:
                print(f"   └── {', '.join(operations)}")
            else:
                print(f"   └── No operations found")
    
    print()
    print("=" * 50)
    print("Options:")
    print("[1] Process NEWEST file only (recommended)")
    print("[2] Archive old files and process newest")
    print("[3] Choose specific file to process")
    print("[4] Cancel")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            return [files[0]]  # Return only newest file
        elif choice == '2':
            # Archive old files, return newest
            for old_file in files[1:]:
                archive_processed_file(old_file, "auto_archived")
            return [files[0]]
        elif choice == '3':
            return choose_specific_file(files)
        elif choice == '4':
            print("❌ Cancelled.")
            return None
        else:
            print("❌ Invalid choice. Please select 1-4.")

def choose_specific_file(files: List[str]) -> List[str]:
    """Let user choose a specific file to process"""
    print("\nSelect file to process:")
    
    for i, filename in enumerate(files):
        preview = get_file_preview(filename)
        operations_count = preview.get('total', 0) if 'error' not in preview else 0
        print(f"[{i+1}] {filename} ({operations_count} operations)")
    
    while True:
        try:
            choice = input(f"\nSelect file (1-{len(files)}): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(files):
                return [files[index]]
            else:
                print(f"❌ Invalid choice. Please select 1-{len(files)}.")
        except ValueError:
            print("❌ Please enter a valid number.")