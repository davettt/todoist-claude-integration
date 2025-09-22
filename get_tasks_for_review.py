import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

def get_tasks_for_review():
    """Get tasks that need housekeeping - focus on ones without due dates"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    
    # Get all tasks
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch tasks")
        return
    
    tasks = response.json()
    
    # Get projects and sections for context
    projects_response = requests.get("https://api.todoist.com/rest/v2/projects", headers=headers)
    projects = projects_response.json() if projects_response.status_code == 200 else []
    project_map = {p['id']: p['name'] for p in projects}
    
    sections_response = requests.get("https://api.todoist.com/rest/v2/sections", headers=headers)
    sections = sections_response.json() if sections_response.status_code == 200 else []
    section_map = {s['id']: s['name'] for s in sections}
    
    # Filter tasks for review - prioritize ones without due dates in Inbox
    tasks_for_review = []
    
    for task in tasks:
        # Skip tasks we already know about
        skip_tasks = [
            "Pay rent",
            "Update remaining address details and passport", 
            "Get back into paid studies",
            "domains check"
        ]
        
        if task['content'] in skip_tasks:
            continue
            
        # Prioritize tasks that need attention:
        # 1. No due date
        # 2. In Inbox project
        # 3. No labels
        # 4. No section
        
        needs_attention = False
        reasons = []
        
        if not task.get('due'):
            needs_attention = True
            reasons.append("no due date")
            
        project_name = project_map.get(task.get('project_id'), 'Unknown')
        if project_name == "Inbox":
            needs_attention = True
            reasons.append("in Inbox")
            
        if not task.get('labels'):
            needs_attention = True
            reasons.append("no labels")
            
        section_name = section_map.get(task.get('section_id'), '')
        if not section_name:
            needs_attention = True
            reasons.append("no section")
            
        if needs_attention:
            task_info = {
                "content": task['content'],
                "project": project_name,
                "section": section_name,
                "labels": task.get('labels', []),
                "priority": task.get('priority', 1),
                "due_date": task['due']['date'] if task.get('due') else None,
                "description": task.get('description', ''),
                "attention_reasons": reasons
            }
            tasks_for_review.append(task_info)
    
    # Sort by number of issues (most issues first)
    tasks_for_review.sort(key=lambda x: len(x['attention_reasons']), reverse=True)
    
    print("🔍 TASKS NEEDING HOUSEKEEPING:")
    print("=" * 50)
    
    for i, task in enumerate(tasks_for_review[:10], 1):  # Show top 10
        print(f"\n{i}. {task['content']}")
        print(f"   Project: {task['project']} | Section: {task['section'] or 'None'}")
        print(f"   Labels: {task['labels'] or 'None'} | Priority: {task['priority']}")
        print(f"   Due: {task['due_date'] or 'None'}")
        print(f"   Issues: {', '.join(task['attention_reasons'])}")
        if task['description']:
            print(f"   Description: {task['description'][:60]}...")
    
    # Save to file for Claude to read
    review_data = {
        "generated_at": "2025-09-22",
        "top_5_tasks_for_review": tasks_for_review[:5],
        "total_tasks_needing_attention": len(tasks_for_review)
    }
    
    with open("tasks_needing_review.json", "w") as f:
        json.dump(review_data, f, indent=2)
    
    print(f"\n💾 Saved {len(tasks_for_review[:5])} tasks to: tasks_needing_review.json")
    print("Claude can now read this file to help with housekeeping!")
    
    return tasks_for_review[:5]  # Return top 5 for review

if __name__ == "__main__":
    get_tasks_for_review()
