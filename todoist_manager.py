#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

def print_banner():
    """Display the main banner"""
    print("\n" + "=" * 50)
    print("🚀 TODOIST + CLAUDE TASK MANAGER")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    print()

def print_menu():
    """Display the main menu options"""
    print("What would you like to do?")
    print()
    print("📋 TASK MANAGEMENT:")
    print("  1. View current tasks (overdue, today, tomorrow)")
    print("  2. Create/Update/Delete tasks from Claude JSON file")
    print()
    print("⚙️  CONFIGURATION:")
    print("  3. Get Todoist projects, labels & sections")
    print("  4. View saved configuration")
    print()
    print("📁 FILE MANAGEMENT:")
    print("  5. List task files in folder")
    print("  6. View processed task history")
    print()
    print("❓ HELP:")
    print("  7. Show workflow instructions")
    print("  8. Exit")
    print()

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🔄 {description}...")
    print("-" * 30)

    try:
        result = subprocess.run([sys.executable, script_name],
                              capture_output=False,
                              text=True)

        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ {description} encountered an error (exit code: {result.returncode})")

    except FileNotFoundError:
        print(f"❌ Error: {script_name} not found!")
        print("Make sure all scripts are in the same folder.")
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")

def list_task_files():
    """List available task JSON files"""
    import glob

    print("\n📁 TASK FILES IN CURRENT FOLDER:")
    print("-" * 30)

    json_files = glob.glob("tasks*.json")

    if json_files:
        for i, file in enumerate(json_files, 1):
            file_size = os.path.getsize(file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"  {i}. {file}")
            print(f"     └── Modified: {mod_time.strftime('%Y-%m-%d %H:%M')} | Size: {file_size} bytes")
    else:
        print("  No task files found (tasks*.json)")
        print("  💡 Ask Claude to create a task file for you!")

    other_files = ['current_tasks.json', 'todoist_reference.json']
    existing_other = [f for f in other_files if os.path.exists(f)]

    if existing_other:
        print("\n📄 OTHER FILES:")
        for file in existing_other:
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"  • {file} (modified: {mod_time.strftime('%Y-%m-%d %H:%M')})")

def view_processed_history():
    """Show processed task history"""
    print("\n📚 PROCESSED TASK HISTORY:")
    print("-" * 30)

    if os.path.exists("processed"):
        import glob
        processed_files = glob.glob("processed/*.json")

        if processed_files:
            # Sort by modification time (newest first)
            processed_files.sort(key=os.path.getmtime, reverse=True)

            for file in processed_files[:10]:  # Show last 10
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
    config_files = ['todoist_reference.json', 'todoist_config.json']

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\n📋 CONFIGURATION FROM {config_file.upper()}:")
            print("-" * 40)

            try:
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)

                if 'projects' in config:
                    if isinstance(config['projects'], dict):
                        # New format (todoist_config.json)
                        for project, info in config['projects'].items():
                            sections = info.get('sections', [])
                            print(f"  📂 {project}")
                            if sections:
                                for section in sections:
                                    print(f"    └── {section}")
                            else:
                                print(f"    └── (no sections)")
                    else:
                        # Old format (todoist_reference.json)
                        for project in config['projects']:
                            print(f"  📂 {project['name']}")
                            sections = project.get('sections', [])
                            if sections:
                                for section in sections:
                                    print(f"    └── {section['name']}")

                if 'labels' in config:
                    labels = config['labels']
                    if labels:
                        if isinstance(labels[0], dict):
                            # Old format with label objects
                            label_names = [label['name'] for label in labels]
                        else:
                            # New format with just label names
                            label_names = labels
                        print(f"\n  🏷️  Labels: {', '.join(label_names)}")
                    else:
                        print(f"\n  🏷️  Labels: None")

                if 'last_updated' in config:
                    print(f"\n  📅 Last updated: {config['last_updated'][:19]}")

            except Exception as e:
                print(f"  ❌ Error reading {config_file}: {str(e)}")
            return

    print("\n❌ No configuration files found!")
    print("Run option 3 to fetch your current Todoist setup.")

def show_workflow_help():
    """Display workflow instructions"""
    print("\n📖 TODOIST + CLAUDE WORKFLOW:")
    print("=" * 40)

    print("\n🔄 TYPICAL WORKFLOW:")
    print("1. Run option 1 to see current task load")
    print("2. Dictate new tasks to Claude in chat")
    print("3. Claude creates tasks_YYYY-MM-DD.json file")
    print("4. Download and save JSON file to this folder")
    print("5. Run option 2 to create/update/delete tasks in Todoist")
    print("6. Tasks sync to iPhone automatically")

    print("\n⚙️  SETUP (ONE-TIME):")
    print("• Create .env file with TODOIST_API_TOKEN")
    print("• Run option 3 to fetch your projects/labels")
    print("• Share configuration with Claude")

    print("\n📁 FILE STRUCTURE:")
    print("your-folder/")
    print("├── .env (your API token)")
    print("├── todoist_manager.py (this script)")
    print("├── todoist_claude.py (task creator)")
    print("├── get_todoist_config.py (config fetcher)")
    print("├── get_current_tasks.py (current tasks)")
    print("├── tasks_*.json (from Claude)")
    print("└── processed/ (archived tasks)")

    print("\n💡 TIPS:")
    print("• Use option 1 regularly to see workload")
    print("• Keep task JSON files descriptive")
    print("• Review tasks before confirming creation")
    print("• Archive old files to keep folder clean")

def main():
    """Main menu loop"""
    while True:
        print_banner()
        print_menu()

        try:
            choice = input("Choose an option (1-8): ").strip()

            if choice == '1':
                run_script('get_current_tasks.py', 'Fetching current tasks')

            elif choice == '2':
                run_script('todoist_task_manager.py', 'Processing Claude task file')

            elif choice == '3':
                run_script('get_todoist_config.py', 'Fetching Todoist configuration')

            elif choice == '4':
                view_configuration()

            elif choice == '5':
                list_task_files()

            elif choice == '6':
                view_processed_history()

            elif choice == '7':
                show_workflow_help()

            elif choice == '8':
                print("\n👋 Goodbye! Happy task managing!")
                break

            else:
                print("\n❌ Invalid choice. Please choose 1-8.")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
