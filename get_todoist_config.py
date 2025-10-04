"""
Enhanced Todoist Configuration Setup with modular architecture
Fetches projects, sections, and labels using the new API client structure
"""

import os
import sys
from datetime import datetime

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.todoist_client import TodoistClient
from utils.file_manager import save_personal_data


def display_configuration(projects, labels, sections):
    """Display current Todoist configuration in a user-friendly format"""
    print("🚀 Your Current Todoist Configuration")
    print("=" * 50)

    # Create sections mapping by project
    sections_by_project = {}
    for section in sections:
        project_id = section["project_id"]
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section)

    # Display projects with their sections
    print("\n📁 YOUR TODOIST PROJECTS & SECTIONS:")
    print("-" * 40)
    if projects:
        for project in projects:
            project_info = f"  📂 {project['name']}"
            if project.get("is_favorite"):
                project_info += " ⭐"
            print(project_info)

            # Show sections for this project
            project_sections = sections_by_project.get(project["id"], [])
            if project_sections:
                for section in project_sections:
                    print(f"    └── {section['name']}")
            else:
                print("    └── (no sections)")
            print()  # Empty line between projects
    else:
        print("  No projects found")

    # Display labels
    print("🏷️ YOUR TODOIST LABELS:")
    print("-" * 30)
    if labels:
        label_names = [label["name"] for label in labels]
        # Group labels in lines of 4 for readability
        for i in range(0, len(label_names), 4):
            line_labels = label_names[i : i + 4]
            print(f"  • {', '.join(line_labels)}")
    else:
        print("  No labels found")


def save_configuration_data(projects, labels, sections):
    """Save configuration to personal data directory"""
    # Create sections mapping by project for easy lookup
    sections_by_project = {}
    for section in sections:
        project_id = section["project_id"]
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(
            {"name": section["name"], "id": section["id"]}
        )

    # Build configuration structure
    config = {
        "last_updated": datetime.now().isoformat(),
        "projects": [
            {
                "name": p["name"],
                "id": p["id"],
                "is_favorite": p.get("is_favorite", False),
                "sections": sections_by_project.get(p["id"], []),
            }
            for p in projects
        ],
        "labels": [{"name": label["name"], "id": label["id"]} for label in labels],
    }

    # Save to personal data directory
    save_personal_data("todoist_reference.json", config)
    print(
        "You can share this configuration with Claude for properly organized task files!"
    )


def generate_claude_summary(projects, labels, sections):
    """Generate a summary perfect for sharing with Claude"""
    print("\n" + "=" * 50)
    print("📋 COPY THIS TO SHARE WITH CLAUDE:")
    print("=" * 50)

    # Create sections mapping by project
    sections_by_project = {}
    for section in sections:
        project_id = section["project_id"]
        if project_id not in sections_by_project:
            sections_by_project[project_id] = []
        sections_by_project[project_id].append(section["name"])

    print("My Todoist Projects & Sections:")
    for project in projects:
        print(f"  📂 {project['name']}")
        project_sections = sections_by_project.get(project["id"], [])
        if project_sections:
            for section in project_sections:
                print(f"    └── {section}")
        else:
            print("    └── (no sections)")

    print("\nMy Todoist Labels:")
    label_names = [label["name"] for label in labels]
    for name in label_names:
        print(f"  - {name}")

    print(
        "\nPlease use these projects, sections, and labels when creating task JSON files for me."
    )
    print("=" * 50)


def main():
    """Main configuration setup function"""
    print("🔧 Todoist Configuration Setup")
    print("=" * 30)
    print("Fetching your current Todoist setup...")
    print()

    try:
        # Initialize Todoist client
        todoist_client = TodoistClient()
        print("✅ Connected to Todoist API")

        # Fetch all configuration data
        print("🔄 Fetching projects...")
        projects = todoist_client.get_projects()

        print("🔄 Fetching labels...")
        labels = todoist_client.get_labels()

        print("🔄 Fetching sections...")
        sections = todoist_client.get_sections()

        # Validate we got data
        if not projects:
            print("❌ No projects retrieved. Please check your API token.")
            return

        if labels is None:
            labels = []  # Labels are optional

        if sections is None:
            sections = []  # Sections are optional

        # Display configuration
        display_configuration(projects, labels, sections)

        # Save to file
        save_configuration_data(projects, labels, sections)

        # Generate Claude summary
        generate_claude_summary(projects, labels, sections)

        print("\n🎉 Configuration setup complete!")
        print(
            f"📊 Summary: {len(projects)} projects, {len(labels)} labels, {len(sections)} sections"
        )

    except ValueError as e:
        print(str(e))
        print("\nPlease check your .env file and try again.")
    except Exception as e:
        print(f"❌ Error during configuration setup: {str(e)}")
        print("Please check your API token and internet connection.")


if __name__ == "__main__":
    main()
