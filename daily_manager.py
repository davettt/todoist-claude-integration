#!/usr/bin/env python3
"""
Todoist + Claude Daily Manager
Simplified interface focused on the 3-step daily workflow
"""

import os
import subprocess
import sys
from datetime import datetime

# Import version info
try:
    from version import __version__
except ImportError:
    __version__ = "unknown"


def print_banner():
    """Display the main banner"""
    print("\n" + "=" * 60)
    print("🚀 TODOIST + CLAUDE DAILY MANAGER")
    print(f"   Version {__version__}")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")

    # Show pending email operations count
    pending_count = count_pending_email_operations()
    if pending_count > 0:
        print(
            f"📧 {pending_count} pending email operation{'s' if pending_count != 1 else ''} ready for review"
        )

    print()


def count_pending_email_operations():
    """Count pending email operation files"""
    import glob

    pending_dir = "local_data/pending_operations"
    if os.path.exists(pending_dir):
        pattern = os.path.join(pending_dir, "tasks_email_*.json")
        files = glob.glob(pattern)
        return len(files)
    return 0


def print_menu():
    """Display the simple daily menu"""
    print("📋 DAILY WORKFLOW (Do these in order):")
    print()
    print("  1. 📤 Export data (Step 1 - Run first each day)")
    print("  2. 💬 Instructions for Claude (Step 2 - Copy/paste to Claude)")
    print("  3. ✅ Apply changes (Step 3 - After Claude creates files)")
    print()
    print("📧 EMAIL:")
    print("  4. 📨 Process forwarded emails (create tasks from emails)")
    print("  5. 📰 Generate email digest (AI-powered newsletter summary)")
    print("  6. 📧 Review digest interactively (view + rate in one flow)")
    print("  7. 👁️ View my email profile (interests, projects, trusted senders)")
    print("  8. ⚙️ Manage my email profile (add/remove interests, projects)")
    print()
    print("📊 VIEWS:")
    print("  9. 📋 View my current tasks")
    print("  10. 📅 View my calendar")
    print()
    print("💾 BACKUP:")
    print("  11. 💾 Create backup (before making changes)")
    print("  12. 📂 Manage backups (list/restore)")
    print()
    print("⚙️ SETUP & HELP:")
    print("  13. 🔧 First-time setup")
    print("  14. 📖 Show full workflow guide")
    print("  15. 🚪 Exit")
    print()


def run_script(script_name, description):
    """Run a Python script"""
    print(f"\n🔄 {description}...")
    print("-" * 50)

    try:
        result = subprocess.run(
            [sys.executable, script_name], capture_output=False, text=True
        )

        if result.returncode == 0:
            print(f"\n✅ {description} completed!")
        else:
            print(f"\n❌ Error occurred (exit code: {result.returncode})")

    except FileNotFoundError:
        print(f"❌ Error: {script_name} not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def export_daily_data():
    """Step 1: Export tasks and calendar"""
    print("\n" + "=" * 60)
    print("STEP 1: EXPORTING YOUR DATA")
    print("=" * 60)
    print()
    print("This will save your current tasks and calendar to files")
    print("that Claude can read.")
    print()

    # Run get_current_tasks.py
    print("📋 Exporting tasks...")
    run_script("get_current_tasks.py", "Task export")

    # Run get_calendar_data.py if available
    if os.path.exists("get_calendar_data.py"):
        print("\n📅 Exporting calendar...")
        run_script("get_calendar_data.py", "Calendar export")

    print("\n" + "=" * 60)
    print("✅ STEP 1 COMPLETE!")
    print("=" * 60)
    print()
    print("Next: Choose option 2 to see what to tell Claude")


def show_claude_instructions():
    """Step 2: Show what to tell Claude"""
    print("\n" + "=" * 60)
    print("STEP 2: TALK TO CLAUDE")
    print("=" * 60)
    print()

    # Check for pending email operations
    pending_count = count_pending_email_operations()

    print("📋 COPY AND PASTE THIS TO CLAUDE:")
    print()
    print("-" * 60)

    # Build the message
    lines = [
        "I need help managing my tasks.",
        "",
        "Please check the todoist-python folder and read these files:",
        "- local_data/personal_data/current_tasks.json",
        "- local_data/personal_data/calendar_full_analysis.json (if available)",
    ]

    if pending_count > 0:
        email_text = (
            f"- local_data/pending_operations/ ({pending_count} email operation"
        )
        if pending_count != 1:
            email_text += "s"
        email_text += " to review)"
        lines.append(email_text)

    lines.append("")
    lines.append(
        'Then follow the instructions in the "For Claude" section of README.md'
    )

    message = "\n".join(lines)
    print(message)
    print("-" * 60)
    print()
    print("Claude will then:")
    print("  ✅ Review your tasks and calendar")
    if pending_count > 0:
        email_text = f"  ✅ Review {pending_count} pending email operation"
        if pending_count != 1:
            email_text += "s"
        print(email_text)
    print("  ✅ Help you plan your day")
    print("  ✅ Create task operation files if needed")
    print()
    print("If Claude creates any task files, save them to this folder,")
    print("then come back here and choose option 3.")
    print()


def apply_changes():
    """Step 3: Apply task changes"""
    print("\n" + "=" * 60)
    print("STEP 3: APPLYING CHANGES")
    print("=" * 60)
    print()

    # Check if there are any task files
    import glob

    task_files = glob.glob("tasks*.json")

    if not task_files:
        print("ℹ️  No task files found (tasks*.json)")
        print()
        print("This means either:")
        print("  • You haven't talked to Claude yet (go to option 2)")
        print("  • Claude didn't need to make any changes")
        print("  • You already applied the changes")
        print()
        return

    print(f"Found {len(task_files)} task file(s) to process:")
    for f in task_files:
        print(f"  • {f}")
    print()

    run_script("todoist_task_manager.py", "Applying changes to Todoist")

    print("\n" + "=" * 60)
    print("✅ STEP 3 COMPLETE!")
    print("=" * 60)
    print()
    print("Your tasks are now updated in Todoist!")


def view_current_tasks():
    """Quick view of current tasks"""
    print("\n📋 YOUR CURRENT TASKS:")
    print("-" * 50)

    # Check if data file exists
    data_file = "local_data/personal_data/current_tasks.json"

    if not os.path.exists(data_file):
        print()
        print("⚠️  No task data found!")
        print()
        print("Run option 1 (Export data) first to generate this file.")
        return

    try:
        import json

        with open(data_file, "r") as f:
            data = json.load(f)

        summary = data.get("summary", {})
        tasks = data.get("tasks", {})

        print()
        print("📊 SUMMARY:")
        print(f"  • Overdue: {summary.get('overdue_count', 0)}")
        print(f"  • Due today: {summary.get('due_today_count', 0)}")
        print(f"  • Due tomorrow: {summary.get('due_tomorrow_count', 0)}")
        print(f"  • Total active: {summary.get('total_active', 0)}")

        # Show today's tasks
        due_today = tasks.get("due_today", [])
        if due_today:
            print()
            print("🎯 DUE TODAY:")
            for task in due_today:
                priority_emoji = "🔴" if task.get("priority") == 1 else "🟡"
                print(f"  {priority_emoji} {task['content']}")
                if task.get("description"):
                    print(f"     └─ {task['description'][:60]}...")

        # Show overdue tasks
        overdue = tasks.get("overdue", [])
        if overdue:
            print()
            print("⚠️  OVERDUE:")
            for task in overdue:
                print(f"  • {task['content']}")

        print()
        print(f"Generated: {data.get('generated_at', 'Unknown')[:16]}")

    except Exception as e:
        print(f"❌ Error reading task data: {str(e)}")


def view_calendar():
    """Quick view of calendar"""
    print("\n📅 YOUR CALENDAR:")
    print("-" * 50)

    # Check if calendar file exists
    calendar_file = "local_data/personal_data/calendar_full_analysis.json"

    if not os.path.exists(calendar_file):
        print()
        print("⚠️  No calendar data found!")
        print()
        print("Run option 1 (Export data) first to generate this file.")
        print("(Requires Google Calendar setup)")
        return

    try:
        import json

        with open(calendar_file, "r") as f:
            data = json.load(f)

        # Show today's schedule
        today = datetime.now().strftime("%Y-%m-%d")
        daily_analysis = data.get("daily_analysis", {})

        today_data = daily_analysis.get(today, {})

        if today_data:
            print()
            print(f"📅 TODAY ({today_data.get('day_name', 'Unknown')}):")
            print(f"  • Events: {today_data.get('events_count', 0)}")
            print(f"  • Free hours: {today_data.get('total_free_hours', 0):.1f}")
            print(f"  • Focus blocks: {today_data.get('focus_blocks_count', 0)}")

            events = today_data.get("events", [])
            if events:
                print()
                print("  Today's events:")
                for event in events:
                    start_time = event["start"].split("T")[1][:5]
                    print(f"    • {start_time} - {event['summary']}")

        print()
        print(f"Analysis period: {data.get('analysis_period', 'Unknown')}")

    except Exception as e:
        print(f"❌ Error reading calendar data: {str(e)}")


def first_time_setup():
    """Run first-time setup scripts"""
    print("\n" + "=" * 60)
    print("FIRST-TIME SETUP")
    print("=" * 60)
    print()
    print("This will fetch your Todoist configuration (projects, labels, etc.)")
    print()

    run_script("get_todoist_config.py", "Fetching Todoist configuration")

    print()
    print("Setup complete! You can now use the daily workflow.")


def create_backup():
    """Create a backup of local data"""
    print("\n" + "=" * 60)
    print("💾 CREATE BACKUP")
    print("=" * 60)
    print()
    print("This will create a timestamped backup of:")
    print("  • All personal data files")
    print("  • Client database (when exists)")
    print("  • Environment configuration")
    print("  • Personal roadmap")
    print()
    print("Backups are stored in: ~/Documents/todoist-backups")
    print("Last 10 days of backups are kept automatically.")
    print()

    description = input("Backup description (or press Enter to skip): ").strip()
    if not description:
        description = "Manual backup"

    try:
        from utils.backup_manager import BackupManager

        backup = BackupManager()
        backup.create_backup(description)
    except Exception as e:
        print(f"❌ Error creating backup: {str(e)}")


def manage_backups():
    """Manage existing backups"""
    try:
        from utils.backup_manager import BackupManager

        backup = BackupManager()

        while True:
            print("\n" + "=" * 60)
            print("📂 MANAGE BACKUPS")
            print("=" * 60)
            print()
            print("Options:")
            print("  1. List all backups")
            print("  2. Restore from backup")
            print("  3. Return to main menu")
            print()

            choice = input("Choose an option (1-3): ").strip()

            if choice == "1":
                backup.list_backups()

            elif choice == "2":
                backups = backup.list_backups()
                if backups:
                    backup_num = input(
                        "\nEnter backup number to restore (or 'c' to cancel): "
                    ).strip()
                    if backup_num.lower() != "c":
                        try:
                            idx = int(backup_num) - 1
                            if 0 <= idx < len(backups):
                                backup.restore_backup(backups[idx]["name"])
                            else:
                                print("❌ Invalid backup number")
                        except ValueError:
                            print("❌ Invalid input")

            elif choice == "3":
                break

            else:
                print("❌ Invalid choice. Please choose 1-3.")

            if choice in ["1", "2"]:
                input("\n⏎ Press Enter to continue...")

    except Exception as e:
        print(f"❌ Error managing backups: {str(e)}")


def process_forwarded_emails():
    """Process forwarded emails to create tasks"""
    print("\n" + "=" * 60)
    print("📧 PROCESS FORWARDED EMAILS")
    print("=" * 60)
    print()
    print("This will process unread emails from your Gmail assistant inbox")
    print("and create operation files for task/event creation.")
    print()
    print("NOTE: Emails WITH [TASK] or #task markers → create task operations")
    print("      Emails WITHOUT markers → save for digest (option 5)")
    print()

    try:
        from email_processor import EmailProcessor

        processor = EmailProcessor()

        # Show stats
        stats = processor.get_interaction_stats()
        if stats["total_emails"] > 0:
            print(f"📊 Previous activity: {stats['total_emails']} emails processed")
            print()

        print("🔄 Processing emails...")
        results = processor.process_new_emails(max_emails=10)

        if results:
            print()
            print(f"✅ Processed {len(results)} email(s)")
            print()
            print("📝 Next steps:")
            print(
                "  • For task emails: Talk to Claude (option 2), then apply (option 3)"
            )
            print("  • For newsletters: Run digest generator (option 5)")
        else:
            print()
            print("📭 No new emails to process")

    except ValueError as e:
        print()
        print("❌ Setup Error:")
        print(f"   {str(e)}")
        print()
        print("📝 Setup Instructions:")
        print("   1. Enable Gmail API in Google Cloud Console")
        print("   2. Download OAuth credentials")
        print("   3. Save as: local_data/gmail_credentials.json")
        print("   4. Return to this menu and try again")

    except ImportError:
        print()
        print("❌ Email processor not found")
        print("   Missing: email_processor.py")
        print("   Please ensure all email integration files are installed")

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")


def generate_email_digest():
    """Generate AI-powered email digest"""
    print("\n" + "=" * 60)
    print("📰 GENERATE EMAIL DIGEST")
    print("=" * 60)
    print()
    print("This will:")
    print("  • Fetch unread emails WITHOUT [TASK]/#task markers")
    print("  • Use Claude AI to analyze interest level")
    print("  • Generate a prioritized markdown digest")
    print("  • Group by: Urgent → High → Medium → Low")
    print()

    try:
        run_script("biweekly_email_digest.py", "Generating AI-powered email digest")

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")


def review_digest_interactive():
    """Review digest interactively - view and rate in one flow"""
    print("\n" + "=" * 60)
    print("📧 INTERACTIVE DIGEST REVIEW")
    print("=" * 60)
    print()
    print("This will show each email with AI analysis,")
    print("then immediately ask you to rate the prediction.")
    print()
    print("Perfect flow: Read → Rate → Next email!")
    print()

    try:
        run_script("review_digest_interactive.py", "Starting interactive review")

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")


def view_profile():
    """View email interest profile"""
    try:
        from utils.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.view_profile()

    except Exception as e:
        print(f"❌ Error viewing profile: {str(e)}")


def manage_profile():
    """Manage email interest profile interactively"""
    print("\n" + "=" * 60)
    print("⚙️ MANAGE YOUR EMAIL PROFILE")
    print("=" * 60)
    print()
    print("Update your interests, active projects, and trusted senders")
    print("to improve email digest personalization.")
    print()

    try:
        from utils.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.interactive_menu()

    except Exception as e:
        print(f"❌ Error managing profile: {str(e)}")


def show_full_workflow():
    """Display the full workflow guide"""
    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW GUIDE")
    print("=" * 60)
    print()
    print("📅 DAILY ROUTINE (3 simple steps):")
    print()
    print("1️⃣  EXPORT DATA (30 seconds)")
    print("   • Choose option 1 from this menu")
    print("   • This saves your tasks & calendar to files")
    print()
    print("2️⃣  TALK TO CLAUDE (as long as you need)")
    print("   • Start a new conversation with Claude")
    print("   • Choose option 2 to see what to say")
    print("   • Claude will help you plan and manage tasks")
    print("   • Claude can review pending email operations")
    print("   • Save any files Claude creates to this folder")
    print()
    print("3️⃣  APPLY CHANGES (if Claude made changes)")
    print("   • Choose option 3 from this menu")
    print("   • Your tasks update in Todoist automatically")
    print()
    print("-" * 60)
    print()
    print("📧 EMAIL WORKFLOW (Optional):")
    print()
    print("  TASK EMAILS (with [TASK] or #task in subject):")
    print("    • Forward emails to your Gmail assistant account")
    print("    • Select option 4 to process forwarded emails")
    print("    • System extracts tasks and creates operation files")
    print("    • Talk to Claude about the pending operations (option 2)")
    print("    • Review and apply changes (option 3)")
    print()
    print("  NEWSLETTER EMAILS (without task markers):")
    print("    • Forward newsletters to your Gmail assistant account")
    print("    • DON'T add [TASK] or #task to the subject")
    print("    • Select option 5 to generate AI-powered digest")
    print("    • Select option 6 for interactive review:")
    print("      - Shows each email with AI analysis")
    print("      - Rate the prediction immediately")
    print("      - Perfect flow: Read → Rate → Next!")
    print("    • The more you rate, the better the AI gets!")
    print()
    print("-" * 60)
    print()
    print("💡 WHAT CLAUDE CAN DO:")
    print("  • Review your tasks and calendar")
    print("  • Review pending email operations")
    print("  • Help you prioritize your day")
    print("  • Create new tasks")
    print("  • Mark tasks as complete")
    print("  • Reschedule tasks")
    print("  • Delete tasks")
    print("  • Extract tasks from forwarded emails")
    print()
    print("-" * 60)
    print()
    print("📖 FOR MORE DETAILS:")
    print("  • Read README.md for complete instructions")
    print("  • Read QUICKSTART.md for setup guide")
    print()


def main():
    """Main menu loop"""
    while True:
        print_banner()
        print_menu()

        try:
            choice = input("Choose an option (1-15): ").strip()

            if choice == "1":
                export_daily_data()

            elif choice == "2":
                show_claude_instructions()

            elif choice == "3":
                apply_changes()

            elif choice == "4":
                process_forwarded_emails()

            elif choice == "5":
                generate_email_digest()

            elif choice == "6":
                review_digest_interactive()

            elif choice == "7":
                view_profile()

            elif choice == "8":
                manage_profile()

            elif choice == "9":
                view_current_tasks()

            elif choice == "10":
                view_calendar()

            elif choice == "11":
                create_backup()

            elif choice == "12":
                manage_backups()

            elif choice == "13":
                first_time_setup()

            elif choice == "14":
                show_full_workflow()

            elif choice == "15":
                print("\n👋 Have a productive day!")
                break

            else:
                print("\n❌ Invalid choice. Please choose 1-15.")

            input("\n⏎ Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\n⏎ Press Enter to continue...")


if __name__ == "__main__":
    main()
