#!/usr/bin/env python3
"""
Enhanced Todoist Manager with modular architecture
Main interface for all Todoist + Claude integration operations
"""

import os
import subprocess
import sys
from datetime import datetime

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.file_manager import (
    PROCESSED_DIR,
    find_operation_files,
    get_personal_data_path,
)


def print_banner():
    """Display the main banner"""
    print("\n" + "=" * 60)
    print("🚀 TODOIST + CLAUDE PRODUCTIVITY HUB")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    print("🏗️ Modular Architecture v2.0")
    print()


def print_menu():
    """Display the enhanced menu options"""
    print("What would you like to do?")
    print()
    print("📋 TASK MANAGEMENT:")
    print("  1. View current tasks (overdue, today, tomorrow)")
    print("  2. 🆕 Comprehensive ALL tasks analysis (strategic insights)")
    print("  3. 📅 Calendar management interface")
    print("  4. Process task operations from Claude JSON files")
    print()
    print("📅 CALENDAR MANAGEMENT:")
    print("  5. Export calendar data for Claude analysis")
    print("  6. Process calendar operations from Claude JSON files")
    print()
    print("⚙️ CONFIGURATION:")
    print("  7. Fetch Todoist projects, labels & sections")
    print("  8. View saved configuration")
    print()
    print("📁 FILE MANAGEMENT:")
    print("  9. List task and calendar files")
    print("  10. View processed file history")
    print()
    print("❓ HELP:")
    print("  11. Show workflow instructions")
    print("  12. System information")
    print("  13. Exit")
    print()


def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🔄 {description}...")
    print("-" * 30)

    try:
        result = subprocess.run(
            [sys.executable, script_name], capture_output=False, text=True
        )

        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
        else:
            print(
                f"❌ {description} encountered an error (exit code: {result.returncode})"
            )

    except FileNotFoundError:
        print(f"❌ Error: {script_name} not found!")
        print("Make sure all scripts are in the same folder.")
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")


def list_files_and_data():
    """List available task files and personal data"""
    print("\n📁 TASK FILES & PERSONAL DATA:")
    print("=" * 40)

    # Task files in main directory
    json_files = find_operation_files()

    if json_files:
        print("\n🔄 PENDING TASK FILES (Main Directory):")
        for i, file in enumerate(json_files, 1):
            if os.path.exists(file):
                file_size = os.path.getsize(file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                print(f"  {i}. {file}")
                print(
                    f"     └── Modified: {mod_time.strftime('%Y-%m-%d %H:%M')} | Size: {file_size} bytes"
                )
    else:
        print("\n🔄 PENDING TASK FILES:")
        print("  No task files found (tasks*.json)")
        print("  💡 Ask Claude to create a task file for you!")

    # Personal data files
    personal_data_files = [
        "current_tasks.json",
        "all_tasks_comprehensive.json",
        "calendar_availability.json",
        "calendar_full_analysis.json",
        "calendar_integrated_insights.json",
        "todoist_reference.json",
    ]

    existing_files = []
    for filename in personal_data_files:
        filepath = get_personal_data_path(filename)
        if os.path.exists(filepath):
            existing_files.append(filepath)

    if existing_files:
        print("\n📄 PERSONAL DATA FILES:")
        for filepath in existing_files:
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"  • {os.path.basename(filepath)}")
            print(f"    └── {filepath}")
            print(f"    └── Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("\n📄 PERSONAL DATA FILES:")
        print("  No personal data files found")
        print("  Run option 4 to create configuration files")


def view_processed_history():
    """Show processed task history"""
    print("\n📚 PROCESSED TASK HISTORY:")
    print("-" * 30)

    if os.path.exists(PROCESSED_DIR):
        import glob

        processed_files = glob.glob(f"{PROCESSED_DIR}/*.json")

        if processed_files:
            # Sort by modification time (newest first)
            processed_files.sort(key=os.path.getmtime, reverse=True)

            print(
                f"\n📁 Found {len(processed_files)} processed files (showing last 10):"
            )
            for file in processed_files[:10]:
                mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                filename = os.path.basename(file)
                print(f"  • {filename}")
                print(f"    └── Processed: {mod_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("  No processed files found")
    else:
        print("  No processed folder found")
        print("  Files will be archived here after processing")


def view_configuration():
    """Display saved configuration"""
    print("\n📋 TODOIST CONFIGURATION:")
    print("-" * 30)

    config_path = get_personal_data_path("todoist_reference.json")

    if os.path.exists(config_path):
        try:
            import json

            with open(config_path, "r") as f:
                config = json.load(f)

            print(f"\n📂 Configuration from: {config_path}")

            if "projects" in config:
                print(f"\n📁 PROJECTS ({len(config['projects'])}):")
                for project in config["projects"]:
                    print(f"  📂 {project['name']}")
                    sections = project.get("sections", [])
                    if sections:
                        for section in sections:
                            print(f"    └── {section['name']}")
                    else:
                        print("    └── (no sections)")

            if "labels" in config:
                labels = config["labels"]
                if labels:
                    label_names = [label["name"] for label in labels]
                    print(f"\n🏷️ LABELS ({len(labels)}):")
                    # Group labels in lines of 4 for readability
                    for i in range(0, len(label_names), 4):
                        line_labels = label_names[i : i + 4]
                        print(f"  • {', '.join(line_labels)}")

            if "last_updated" in config:
                print(f"\n📅 Last updated: {config['last_updated'][:19]}")

        except Exception as e:
            print(f"❌ Error reading configuration: {str(e)}")
    else:
        print("❌ No configuration file found!")
        print(f"Expected location: {config_path}")
        print("Run option 4 to fetch your current Todoist setup.")


def show_workflow_help():
    """Display workflow instructions"""
    print("\n📖 TODOIST + CLAUDE WORKFLOW:")
    print("=" * 40)

    print("\n🔄 ENHANCED WORKFLOW:")
    print("1. Run option 1 to see current task load")
    print("2. Run option 2 for comprehensive strategic analysis")
    print("3. Run option 3 for calendar-integrated planning")
    print("4. Tell Claude your tasks in chat")
    print("5. Claude creates tasks_YYYY-MM-DD.json file")
    print("6. Save JSON file to this main folder")
    print("7. Run option 4 to process tasks in Todoist")
    print("8. Tasks sync to all devices automatically")

    print("\n⚙️ SETUP (ONE-TIME):")
    print("• Create .env file with TODOIST_API_TOKEN")
    print("• Run option 5 to fetch your projects/labels")
    print("• Share local_data/personal_data/ files with Claude")

    print("\n📁 FILE STRUCTURE:")
    print("todoist-claude-integration/")
    print("├── .env (your API token)")
    print("├── Core Python scripts (modular architecture)")
    print("├── tasks_*.json (temporary, from Claude)")
    print("├── apis/ (API client modules)")
    print("├── utils/ (shared utilities)")
    print("└── local_data/")
    print("    ├── personal_data/ (current_tasks.json, config)")
    print("    └── processed/ (archived completed tasks)")

    print("\n💡 TIPS:")
    print("• Check current tasks before adding new ones")
    print("• Claude reads from local_data/personal_data/")
    print("• Task files are archived after processing")
    print("• Personal data stays local (not in git)")
    print("• Modular architecture supports future expansion")


def show_system_info():
    """Display system information and architecture details"""
    print("\n🏗️ SYSTEM ARCHITECTURE:")
    print("=" * 30)

    print("\n📊 PROJECT STATUS:")
    print("• Architecture: Modular v2.0")
    print("• APIs Supported: Todoist (Calendar & Email planned)")
    print("• Data Storage: local_data/ structure")
    print("• Documentation: Streamlined (2 files)")

    print("\n📁 DIRECTORY STRUCTURE:")
    directories = [
        ("apis/", "API client modules"),
        ("utils/", "Shared utilities"),
        ("local_data/personal_data/", "Your task data"),
        ("local_data/processed/", "Archived operations"),
        ("local_data/backups/", "System backups"),
    ]

    for directory, description in directories:
        exists = "✅" if os.path.exists(directory) else "❌"
        print(f"  {exists} {directory} - {description}")

    print("\n🔧 CORE MODULES:")
    modules = [
        ("apis/todoist_client.py", "Todoist API operations"),
        ("utils/file_manager.py", "File & data management"),
        ("todoist_task_manager.py", "Task processing engine"),
        ("get_current_tasks.py", "Task analysis"),
        ("get_todoist_config.py", "Configuration setup"),
    ]

    for module, description in modules:
        exists = "✅" if os.path.exists(module) else "❌"
        print(f"  {exists} {module} - {description}")

    print("\n🚀 READY FOR:")
    print("• ✅ Current Todoist operations")
    print("• 🔄 Calendar integration (next phase)")
    print("• 📧 Email automation (future)")
    print("• 🤖 Cross-platform workflows")


def main():
    """Main menu loop"""
    while True:
        print_banner()
        print_menu()

        try:
            choice = input("Choose an option (1-13): ").strip()

            if choice == "1":
                run_script("get_current_tasks.py", "Analyzing current tasks")

            elif choice == "2":
                run_script(
                    "get_all_tasks_enhanced.py", "Comprehensive ALL tasks analysis"
                )

            elif choice == "3":
                run_script(
                    "calendar_manager.py", "Opening Calendar Management Interface"
                )

            elif choice == "4":
                run_script(
                    "todoist_task_manager.py", "Processing Claude task operations"
                )

            elif choice == "5":
                run_script("get_calendar_data.py", "Exporting calendar data for Claude")

            elif choice == "6":
                run_script(
                    "calendar_event_manager.py",
                    "Processing calendar operations from Claude",
                )

            elif choice == "7":
                run_script("get_todoist_config.py", "Fetching Todoist configuration")

            elif choice == "8":
                view_configuration()

            elif choice == "9":
                list_files_and_data()

            elif choice == "10":
                view_processed_history()

            elif choice == "11":
                show_workflow_help()

            elif choice == "12":
                show_system_info()

            elif choice == "13":
                print("\n👋 Goodbye! Happy task managing!")
                break

            else:
                print("\n❌ Invalid choice. Please choose 1-13.")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
