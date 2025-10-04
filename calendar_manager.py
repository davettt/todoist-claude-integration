#!/usr/bin/env python3
"""
Calendar Management Interface - Updated with Calendar Selection
Dedicated interface for Google Calendar integration operations
"""

import os
import subprocess
import sys
from datetime import datetime

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.file_manager import get_personal_data_path


def print_banner():
    """Display the calendar banner"""
    print("\\n" + "=" * 60)
    print("📅 GOOGLE CALENDAR INTEGRATION MANAGER")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    print("🔗 Calendar + Todoist Integration")
    print()


def print_menu():
    """Display calendar management options"""
    print("What would you like to do?")
    print()
    print("📅 CALENDAR OPERATIONS:")
    print("  1. Export calendar data for Claude analysis")
    print("  2. Process calendar operations from Claude JSON files")
    print("  3. View calendar availability summary")
    print()
    print("⏰ TIME BLOCKING:")
    print("  4. Create time blocks for today's tasks")
    print("  5. Schedule tasks for tomorrow")
    print("  6. Plan weekly task schedule")
    print()
    print("📊 ANALYSIS:")
    print("  7. View calendar integration data")
    print("  8. Show upcoming events and free time")
    print("  9. List all available calendars")
    print()
    print("❓ HELP:")
    print("  10. Calendar setup instructions")
    print("  11. Back to main menu")
    print("  12. Exit")
    print()


def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\\n🔄 {description}...")
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


def view_calendar_data():
    """Display saved calendar data"""
    print("\\n📊 CALENDAR INTEGRATION DATA:")
    print("-" * 35)

    # Check for calendar files
    calendar_files = [
        ("calendar_availability.json", "Calendar availability for Claude"),
        ("calendar_full_analysis.json", "Complete calendar analysis"),
        ("calendar_integrated_insights.json", "Task scheduling insights"),
    ]

    found_files = 0
    for filename, description in calendar_files:
        filepath = get_personal_data_path(filename)
        if os.path.exists(filepath):
            found_files += 1
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"\\n📄 {filename}")
            print(f"   Description: {description}")
            print(f"   Last updated: {mod_time.strftime('%Y-%m-%d %H:%M')}")

            # Show summary if available
            try:
                import json

                with open(filepath, "r") as f:
                    data = json.load(f)

                if "summary" in data:
                    summary = data["summary"]
                    print(f"   Events: {summary.get('total_events', 'N/A')}")
                    print(
                        f"   Best work days: {len(summary.get('best_days_for_work', []))}"
                    )
                    print(
                        f"   Focus time available: {summary.get('focus_time_available', 'N/A')} days"
                    )

            except Exception:
                print("   Status: File exists but couldn't read summary")

    if found_files == 0:
        print("❌ No calendar data files found!")
        print("Run option 1 to export calendar data first.")


def show_calendar_setup():
    """Display calendar setup instructions"""
    print("\\n📅 CALENDAR INTEGRATION SETUP:")
    print("=" * 40)

    print("\\n🔧 PREREQUISITES:")
    print("1. Google Cloud Project with Calendar API enabled")
    print("2. OAuth 2.0 credentials (Desktop application)")
    print("3. Python packages installed")

    print("\\n📦 REQUIRED PACKAGES:")
    print(
        "pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )

    print("\\n⚙️ SETUP STEPS:")
    print("1. Go to Google Cloud Console (console.cloud.google.com)")
    print("2. Create/select project")
    print("3. Enable Google Calendar API")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download credentials JSON file")
    print("6. Save as: local_data/calendar_credentials.json")
    print("7. Run option 1 to authenticate and export data")

    print("\\n🔐 AUTHENTICATION:")
    print("• First run will open browser for Google authentication")
    print("• Credentials saved locally for future use")
    print("• No API keys needed in .env file")

    print("\\n📁 FILE STRUCTURE:")
    print("local_data/")
    print("├── calendar_credentials.json (OAuth credentials)")
    print("├── calendar_token.json (saved auth token)")
    print("├── calendar_availability.json (for Claude)")
    print("└── calendar_full_analysis.json (complete data)")


def main():
    """Main menu loop for calendar management"""
    while True:
        print_banner()
        print_menu()

        try:
            choice = input("Choose an option (1-12): ").strip()

            if choice == "1":
                run_script("get_calendar_data.py", "Exporting calendar data")

            elif choice == "2":
                run_script(
                    "calendar_event_manager.py", "Processing calendar operations"
                )

            elif choice == "3":
                view_calendar_data()

            elif choice == "4":
                print("\\n⏰ TIME BLOCKING FOR TODAY:")
                print("This feature will be implemented to:")
                print("• Analyze today's free time slots")
                print("• Suggest time blocks for due tasks")
                print("• Create calendar events automatically")
                print("\\n💡 For now, use option 2 with a timeblock JSON file!")

            elif choice == "5":
                print("\\n📅 TOMORROW'S SCHEDULE:")
                print("This feature will be implemented to:")
                print("• Plan tomorrow's task schedule")
                print("• Optimize time allocation")
                print("• Create advance time blocks")
                print("\\n💡 For now, use option 2 with a schedule JSON file!")

            elif choice == "6":
                print("\\n📊 WEEKLY PLANNING:")
                print("This feature will be implemented to:")
                print("• Analyze entire week availability")
                print("• Distribute tasks across optimal days")
                print("• Create comprehensive weekly schedule")
                print("\\n💡 For now, use comprehensive task analysis!")

            elif choice == "7":
                view_calendar_data()

            elif choice == "8":
                print("\\n📊 UPCOMING EVENTS SUMMARY:")
                print("This will show a quick overview of:")
                print("• Next 7 days of calendar events")
                print("• Available free time slots")
                print("• Best opportunities for task scheduling")
                print("\\n💡 Run option 1 to get detailed calendar analysis!")

            elif choice == "9":
                run_script("list_calendars.py", "Listing available calendars")

            elif choice == "10":
                show_calendar_setup()

            elif choice == "11":
                # Return to main menu
                run_script("todoist_manager.py", "Opening main menu")
                break

            elif choice == "12":
                print("\\n👋 Goodbye! Happy calendar managing!")
                break

            else:
                print("\\n❌ Invalid choice. Please choose 1-12.")

            input("\\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\\n\\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\\n❌ Error: {str(e)}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
