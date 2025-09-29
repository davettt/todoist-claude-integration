#!/usr/bin/env python3
"""
Todoist + Claude Daily Manager
Simplified interface focused on the 3-step daily workflow
"""

import os
import subprocess
import sys
from datetime import datetime

def print_banner():
    """Display the main banner"""
    print("\n" + "=" * 60)
    print("🚀 TODOIST + CLAUDE DAILY MANAGER")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
    print()

def print_menu():
    """Display the simple daily menu"""
    print("📋 DAILY WORKFLOW (Do these in order):")
    print()
    print("  1. 📤 Export data (Step 1 - Run first each day)")
    print("  2. 💬 Instructions for Claude (Step 2 - Copy/paste to Claude)")
    print("  3. ✅ Apply changes (Step 3 - After Claude creates files)")
    print()
    print("📊 VIEWS:")
    print("  4. 📋 View my current tasks")
    print("  5. 📅 View my calendar")
    print()
    print("⚙️ SETUP & HELP:")
    print("  6. 🔧 First-time setup")
    print("  7. 📖 Show full workflow guide")
    print("  8. 🚪 Exit")
    print()

def run_script(script_name, description):
    """Run a Python script"""
    print(f"\n🔄 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
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
    run_script('get_current_tasks.py', 'Task export')
    
    # Run get_calendar_data.py if available
    if os.path.exists('get_calendar_data.py'):
        print("\n📅 Exporting calendar...")
        run_script('get_calendar_data.py', 'Calendar export')
    
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
    print("📋 COPY AND PASTE THIS TO CLAUDE:")
    print()
    print("-" * 60)
    message = """I need help managing my tasks.

Please check the todoist-python folder and read these files:
- local_data/personal_data/current_tasks.json
- local_data/personal_data/calendar_full_analysis.json (if available)

Then follow the instructions in the "For Claude" section of README.md"""
    print(message)
    print("-" * 60)
    print()
    print("Claude will then:")
    print("  ✅ Review your tasks and calendar")
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
    task_files = glob.glob('tasks*.json')
    
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
    
    run_script('todoist_task_manager.py', 'Applying changes to Todoist')
    
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
    data_file = 'local_data/personal_data/current_tasks.json'
    
    if not os.path.exists(data_file):
        print()
        print("⚠️  No task data found!")
        print()
        print("Run option 1 (Export data) first to generate this file.")
        return
    
    try:
        import json
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        tasks = data.get('tasks', {})
        
        print()
        print(f"📊 SUMMARY:")
        print(f"  • Overdue: {summary.get('overdue_count', 0)}")
        print(f"  • Due today: {summary.get('due_today_count', 0)}")
        print(f"  • Due tomorrow: {summary.get('due_tomorrow_count', 0)}")
        print(f"  • Total active: {summary.get('total_active', 0)}")
        
        # Show today's tasks
        due_today = tasks.get('due_today', [])
        if due_today:
            print()
            print("🎯 DUE TODAY:")
            for task in due_today:
                priority_emoji = "🔴" if task.get('priority') == 1 else "🟡"
                print(f"  {priority_emoji} {task['content']}")
                if task.get('description'):
                    print(f"     └─ {task['description'][:60]}...")
        
        # Show overdue tasks
        overdue = tasks.get('overdue', [])
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
    calendar_file = 'local_data/personal_data/calendar_full_analysis.json'
    
    if not os.path.exists(calendar_file):
        print()
        print("⚠️  No calendar data found!")
        print()
        print("Run option 1 (Export data) first to generate this file.")
        print("(Requires Google Calendar setup)")
        return
    
    try:
        import json
        with open(calendar_file, 'r') as f:
            data = json.load(f)
        
        # Show today's schedule
        today = datetime.now().strftime('%Y-%m-%d')
        daily_analysis = data.get('daily_analysis', {})
        
        today_data = daily_analysis.get(today, {})
        
        if today_data:
            print()
            print(f"📅 TODAY ({today_data.get('day_name', 'Unknown')}):")
            print(f"  • Events: {today_data.get('events_count', 0)}")
            print(f"  • Free hours: {today_data.get('total_free_hours', 0):.1f}")
            print(f"  • Focus blocks: {today_data.get('focus_blocks_count', 0)}")
            
            events = today_data.get('events', [])
            if events:
                print()
                print("  Today's events:")
                for event in events:
                    start_time = event['start'].split('T')[1][:5]
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
    
    run_script('get_todoist_config.py', 'Fetching Todoist configuration')
    
    print()
    print("Setup complete! You can now use the daily workflow.")

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
    print("   • Save any files Claude creates to this folder")
    print()
    print("3️⃣  APPLY CHANGES (if Claude made changes)")
    print("   • Choose option 3 from this menu")
    print("   • Your tasks update in Todoist automatically")
    print()
    print("-" * 60)
    print()
    print("💡 WHAT CLAUDE CAN DO:")
    print("  • Review your tasks and calendar")
    print("  • Help you prioritize your day")
    print("  • Create new tasks")
    print("  • Mark tasks as complete")
    print("  • Reschedule tasks")
    print("  • Delete tasks")
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
            choice = input("Choose an option (1-8): ").strip()
            
            if choice == '1':
                export_daily_data()
                
            elif choice == '2':
                show_claude_instructions()
                
            elif choice == '3':
                apply_changes()
                
            elif choice == '4':
                view_current_tasks()
                
            elif choice == '5':
                view_calendar()
                
            elif choice == '6':
                first_time_setup()
                
            elif choice == '7':
                show_full_workflow()
                
            elif choice == '8':
                print("\n👋 Have a productive day!")
                break
                
            else:
                print("\n❌ Invalid choice. Please choose 1-8.")
            
            input("\n⏎ Press Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\n⏎ Press Enter to continue...")

if __name__ == "__main__":
    main()
