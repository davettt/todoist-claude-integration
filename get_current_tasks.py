import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

if not TODOIST_API_TOKEN:
    print("❌ Error: TODOIST_API_TOKEN not found!")
    print("Please create a .env file with your API token.")
    exit(1)

def fetch_active_tasks():
    """Fetch all active tasks from Todoist"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch tasks: {response.text}")
        return []

def fetch_projects():
    """Fetch projects for name mapping"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/projects", headers=headers)
    
    if response.status_code == 200:
        projects = response.json()
        return {p['id']: p['name'] for p in projects}
    else:
        return {}

def fetch_sections():
    """Fetch sections for name mapping"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/sections", headers=headers)
    
    if response.status_code == 200:
        sections = response.json()
        return {s['id']: s['name'] for s in sections}
    else:
        return {}

def categorize_tasks_by_date(tasks):
    """Categorize tasks by their due dates"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    overdue = []
    due_today = []
    due_tomorrow = []
    upcoming = []  # Next 7 days
    no_due_date = []
    
    for task in tasks:
        if not task.get('due'):
            no_due_date.append(task)
            continue
            
        due_date_str = task['due']['date']
        try:
            # Handle both date and datetime formats
            if 'T' in due_date_str:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            else:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            if due_date < today:
                overdue.append(task)
            elif due_date == today:
                due_today.append(task)
            elif due_date == tomorrow:
                due_tomorrow.append(task)
            elif due_date <= today + timedelta(days=7):
                upcoming.append(task)
                
        except ValueError:
            no_due_date.append(task)
    
    return {
        'overdue': overdue,
        'due_today': due_today,
        'due_tomorrow': due_tomorrow,
        'upcoming': upcoming,
        'no_due_date': no_due_date
    }

def display_task_summary(tasks, project_names, section_names):
    """Display a summary of current tasks"""
    categorized = categorize_tasks_by_date(tasks)
    
    print("🚀 Current Task Overview")
    print("=" * 50)
    
    def format_task(task):
        project = project_names.get(task.get('project_id', ''), 'Unknown')
        section = section_names.get(task.get('section_id', ''), '')
        section_info = f" | {section}" if section else ""
        
        labels = task.get('labels', [])
        label_info = f" [{', '.join(labels)}]" if labels else ""
        
        priority_map = {4: " 🔴", 3: " 🟡", 2: " 🔵", 1: ""}
        priority = priority_map.get(task.get('priority', 1), "")
        
        return f"  • {task['content']}{priority} ({project}{section_info}){label_info}"
    
    # Overdue tasks
    if categorized['overdue']:
        print(f"\n❗ OVERDUE ({len(categorized['overdue'])} tasks):")
        print("-" * 20)
        for task in categorized['overdue']:
            due_date = task['due']['date'][:10] if task.get('due') else ''
            print(f"{format_task(task)} | Due: {due_date}")
    
    # Due today
    if categorized['due_today']:
        print(f"\n📅 DUE TODAY ({len(categorized['due_today'])} tasks):")
        print("-" * 20)
        for task in categorized['due_today']:
            print(format_task(task))
    
    # Due tomorrow
    if categorized['due_tomorrow']:
        print(f"\n🔜 DUE TOMORROW ({len(categorized['due_tomorrow'])} tasks):")
        print("-" * 20)
        for task in categorized['due_tomorrow']:
            print(format_task(task))
    
    # Upcoming this week
    if categorized['upcoming']:
        print(f"\n📆 UPCOMING THIS WEEK ({len(categorized['upcoming'])} tasks):")
        print("-" * 20)
        for task in categorized['upcoming']:
            due_date = task['due']['date'][:10] if task.get('due') else ''
            print(f"{format_task(task)} | Due: {due_date}")
    
    # Summary stats
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  • Overdue: {len(categorized['overdue'])}")
    print(f"  • Due today: {len(categorized['due_today'])}")
    print(f"  • Due tomorrow: {len(categorized['due_tomorrow'])}")
    print(f"  • Upcoming (7 days): {len(categorized['upcoming'])}")
    print(f"  • No due date: {len(categorized['no_due_date'])}")
    print(f"  • Total active: {len(tasks)}")
    
    return categorized

def save_current_tasks_json(tasks, project_names, section_names):
    """Save current tasks to JSON for Claude"""
    categorized = categorize_tasks_by_date(tasks)
    
    def simplify_task(task):
        project = project_names.get(task.get('project_id', ''), 'Unknown')
        section = section_names.get(task.get('section_id', ''), '')
        
        return {
            "content": task['content'],
            "project": project,
            "section": section,
            "labels": task.get('labels', []),
            "priority": task.get('priority', 1),
            "due_date": task['due']['date'][:10] if task.get('due') else None,
            "description": task.get('description', '')
        }
    
    claude_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "overdue_count": len(categorized['overdue']),
            "due_today_count": len(categorized['due_today']),
            "due_tomorrow_count": len(categorized['due_tomorrow']),
            "total_active": len(tasks)
        },
        "tasks": {
            "overdue": [simplify_task(task) for task in categorized['overdue']],
            "due_today": [simplify_task(task) for task in categorized['due_today']],
            "due_tomorrow": [simplify_task(task) for task in categorized['due_tomorrow']],
            "upcoming_week": [simplify_task(task) for task in categorized['upcoming']]
        }
    }
    
    with open("current_tasks.json", "w") as f:
        json.dump(claude_data, f, indent=2)
    
    print(f"\n💾 Current tasks saved to: current_tasks.json")
    print("Share this with Claude for context-aware task planning!")

if __name__ == "__main__":
    try:
        print("Fetching your current tasks...")
        
        # Fetch data
        tasks = fetch_active_tasks()
        project_names = fetch_projects()
        section_names = fetch_sections()
        
        if not tasks:
            print("No active tasks found!")
            exit(0)
        
        # Display summary
        categorized = display_task_summary(tasks, project_names, section_names)
        
        # Save JSON for Claude
        save_current_tasks_json(tasks, project_names, section_names)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
