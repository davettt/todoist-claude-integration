import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

# Check if token is loaded
if not TODOIST_API_TOKEN:
    print("❌ Error: TODOIST_API_TOKEN not found!")
    print("Please create a .env file with your API token.")
    print("See setup instructions for details.")
    exit(1)

def fetch_projects():
    """Fetch all projects from Todoist"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/projects", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch projects: {response.text}")
        return []

def fetch_labels():
    """Fetch all labels from Todoist"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/labels", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch labels: {response.text}")
        return []

def fetch_sections():
    """Fetch all sections from Todoist"""
    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    response = requests.get("https://api.todoist.com/rest/v2/sections", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch sections: {response.text}")
        return []

def display_config():
    """Display current Todoist configuration"""
    print("🚀 Fetching your current Todoist configuration...")
    print("=" * 50)

    # Fetch projects, labels, and sections
    projects = fetch_projects()
    labels = fetch_labels()
    sections = fetch_sections()

    # Create a mapping of sections by project
    sections_by_project = {}
    for section in sections:
        project_id = section['project_id']
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section)

    # Display projects with their sections
    print("\n📁 YOUR TODOIST PROJECTS & SECTIONS:")
    print("-" * 40)
    if projects:
        for project in projects:
            project_info = f"  📂 {project['name']}"
            if project.get('is_favorite'):
                project_info += " ⭐"
            print(project_info)

            # Show sections for this project
            project_sections = sections_by_project.get(project['id'], [])
            if project_sections:
                for section in project_sections:
                    print(f"    └── {section['name']}")
            else:
                print("    └── (no sections)")
            print()  # Empty line between projects
    else:
        print("  No projects found")

    # Display labels
    print("🏷️  YOUR TODOIST LABELS:")
    print("-" * 30)
    if labels:
        label_names = [label['name'] for label in labels]
        # Group labels in lines of 4 for readability
        for i in range(0, len(label_names), 4):
            line_labels = label_names[i:i+4]
            print(f"  • {', '.join(line_labels)}")
    else:
        print("  No labels found")

    return projects, labels, sections

def save_reference_file(projects, labels, sections):
    """Save configuration to reference file"""
    # Create sections mapping by project
    sections_by_project = {}
    for section in sections:
        project_id = section['project_id']
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append({
            "name": section["name"],
            "id": section["id"]
        })

    config = {
        "last_updated": datetime.now().isoformat(),
        "projects": [{
            "name": p["name"],
            "id": p["id"],
            "is_favorite": p.get("is_favorite", False),
            "sections": sections_by_project.get(p["id"], [])
        } for p in projects],
        "labels": [{"name": l["name"], "id": l["id"]} for l in labels]
    }

    with open("todoist_reference.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n💾 Configuration saved to: todoist_reference.json")
    print("You can share this with Claude to get properly organized task files!")

def generate_claude_summary(projects, labels, sections):
    """Generate a summary perfect for sharing with Claude"""
    print("\n" + "=" * 50)
    print("📋 COPY THIS TO SHARE WITH CLAUDE:")
    print("=" * 50)

    # Create sections mapping by project
    sections_by_project = {}
    for section in sections:
        project_id = section['project_id']
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section['name'])

    print("My Todoist Projects & Sections:")
    for project in projects:
        print(f"  📂 {project['name']}")
        project_sections = sections_by_project.get(project['id'], [])
        if project_sections:
            for section in project_sections:
                print(f"    └── {section}")
        else:
            print("    └── (no sections)")

    print("\nMy Todoist Labels:")
    label_names = [l["name"] for l in labels]
    for name in label_names:
        print(f"  - {name}")

    print("\nPlease use these projects, sections, and labels when creating task JSON files for me.")
    print("=" * 50)

if __name__ == "__main__":
    try:
        projects, labels, sections = display_config()

        if projects or labels:
            save_reference_file(projects, labels, sections)
            generate_claude_summary(projects, labels, sections)
        else:
            print("\n❌ No configuration retrieved. Please check your API token.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
