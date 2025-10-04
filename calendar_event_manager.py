#!/usr/bin/env python3
"""
Calendar Event Manager
Processes Claude-generated JSON files for calendar operations
Mirrors the todoist_task_manager.py architecture
"""

import json
import os
import sys

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.google_calendar_client import GoogleCalendarClient
from utils.file_manager import (
    archive_processed_file,
    find_operation_files,
    handle_multiple_files,
)


def find_calendar_operation_files():
    """Find calendar operation JSON files"""
    import glob

    calendar_files = []

    # Look for calendar-specific files
    patterns = [
        "calendar_*.json",
        "events_*.json",
        "schedule_*.json",
        "timeblock_*.json",
    ]

    for pattern in patterns:
        calendar_files.extend(glob.glob(pattern))

    return sorted(calendar_files)


def process_calendar_operations_file(
    calendar_file: str, calendar_client: GoogleCalendarClient
) -> int:
    """Process a single calendar operations file"""
    print(f"\n📅 Processing: {calendar_file}")
    print("-" * 50)

    try:
        # Read the JSON file
        with open(calendar_file, "r") as f:
            data = json.load(f)

        # Extract operations
        create_events = data.get("create_events", [])
        update_events = data.get("update_events", [])
        delete_events = data.get("delete_events", [])
        time_blocks = data.get("time_blocks", [])

        total_operations = (
            len(create_events)
            + len(update_events)
            + len(delete_events)
            + len(time_blocks)
        )

        if total_operations == 0:
            print("⚠️ No calendar operations found in this file!")
            return 0

        print(
            f"📋 Found {len(create_events)} creates, {len(update_events)} updates, {len(delete_events)} deletions, {len(time_blocks)} time blocks"
        )

        # Show preview of operations
        if create_events:
            print("\n➕ CREATE EVENTS:")
            for event in create_events:
                summary = event.get("summary", "Untitled Event")
                start_time = event.get("start", {}).get("dateTime", "No time")
                print(f"  • {summary} at {start_time}")

        if time_blocks:
            print("\n⏰ TIME BLOCKS:")
            for block in time_blocks:
                task_name = block.get("task_name", "Unknown Task")
                start_time = block.get("start_time", "No time")
                duration = block.get("duration_minutes", 60)
                print(f"  • {task_name} at {start_time} ({duration}min)")

        if update_events:
            print("\n✏️ UPDATE EVENTS:")
            for event in update_events:
                event_id = event.get("event_id", "Unknown ID")
                summary = event.get("summary", "Untitled Event")
                print(f"  • {summary} (ID: {event_id})")

        if delete_events:
            print("\n🗑️ DELETE EVENTS:")
            for event in delete_events:
                event_id = event.get("event_id", "Unknown ID")
                summary = event.get("summary", "Untitled Event")
                print(f"  • {summary} (ID: {event_id})")

        print("-" * 50)

        # Ask for confirmation
        confirm = (
            input(f"Apply these calendar changes from {calendar_file}? (y/n): ")
            .lower()
            .strip()
        )

        if confirm != "y":
            print("⚠️ Skipped this file.")
            return 0

        # Process operations
        success_count = 0
        calendar_id = data.get("calendar_id", "primary")

        # 1. Process deletions first
        if delete_events:
            print("\n🗑️ Processing deletions...")
            for event_info in delete_events:
                event_id = event_info.get("event_id")
                summary = event_info.get("summary", "")

                if event_id and calendar_client.delete_event(
                    calendar_id, event_id, summary
                ):
                    success_count += 1

        # 2. Process updates
        if update_events:
            print("\n✏️ Processing updates...")
            for event_info in update_events:
                event_id = event_info.get("event_id")
                if not event_id:
                    print(
                        f"⚠️ Missing event_id for update: {event_info.get('summary', 'Unknown')}"
                    )
                    continue

                # Remove event_id from data before sending to API
                update_data = {k: v for k, v in event_info.items() if k != "event_id"}

                if calendar_client.update_event(calendar_id, event_id, update_data):
                    success_count += 1

        # 3. Process new events
        if create_events:
            print("\n➕ Processing new events...")
            for event_info in create_events:
                if calendar_client.create_event(calendar_id, event_info):
                    success_count += 1

        # 4. Process time blocks (special case of create events)
        if time_blocks:
            print("\n⏰ Processing time blocks...")
            for block_info in time_blocks:
                task_data = {
                    "content": block_info.get("task_name", "Task"),
                    "description": block_info.get("task_description", ""),
                    "task_id": block_info.get("task_id", ""),
                    "priority": block_info.get("priority", 1),
                }

                start_time = block_info.get("start_time")
                duration = block_info.get("duration_minutes", 60)

                if start_time and calendar_client.create_task_time_block(
                    task_data, start_time, duration, calendar_id
                ):
                    success_count += 1

        print(
            f"\n✨ Processed {success_count} out of {total_operations} operations from {calendar_file}"
        )

        # Archive the processed file
        if success_count > 0:
            archive_processed_file(calendar_file)

        return success_count

    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {calendar_file}")
        return 0
    except FileNotFoundError:
        print(f"❌ Error: Could not read {calendar_file}")
        return 0
    except Exception as e:
        print(f"❌ Error processing {calendar_file}: {str(e)}")
        return 0


def process_calendar_operations():
    """Main function to process calendar operations from Claude's JSON files"""
    print("📅 CALENDAR EVENT MANAGER")
    print("=" * 40)
    print("Supports: Creating, Updating, and Deleting calendar events")
    print("Features: Time blocking, task scheduling, event management")
    print()

    try:
        # Initialize calendar client
        print("🔄 Initializing Google Calendar connection...")
        calendar_client = GoogleCalendarClient()
        print("✅ Connected to Google Calendar API")

    except ValueError as e:
        print(str(e))
        print("\nPlease check your calendar setup and try again.")
        return
    except Exception as e:
        print(f"❌ Failed to initialize calendar client: {str(e)}")
        return

    # Find calendar operation files
    calendar_files = find_calendar_operation_files()

    # Also check for general operation files that might contain calendar ops
    general_files = find_operation_files()

    # Filter general files for calendar content
    calendar_related_files = []
    for file in general_files:
        try:
            with open(file, "r") as f:
                content = f.read().lower()
                if any(
                    keyword in content
                    for keyword in ["calendar", "event", "time_block", "schedule"]
                ):
                    calendar_related_files.append(file)
        except Exception:
            continue

    all_calendar_files = list(set(calendar_files + calendar_related_files))

    if not all_calendar_files:
        print("❌ No calendar operation files found!")
        print(
            "Expected files: calendar_*.json, events_*.json, schedule_*.json, timeblock_*.json"
        )
        print("💡 Ask Claude to create a calendar operation file for you!")
        return

    # Handle multiple files intelligently
    if len(all_calendar_files) > 1:
        print(f"🔍 Found {len(all_calendar_files)} calendar operation files")
        selected_files = handle_multiple_files(all_calendar_files)
        if selected_files is None:  # User cancelled
            return
        all_calendar_files = selected_files

    # Process selected files
    total_success = 0
    for calendar_file in all_calendar_files:
        success_count = process_calendar_operations_file(calendar_file, calendar_client)
        total_success += success_count

        # If processing multiple files, add spacing
        if len(all_calendar_files) > 1 and calendar_file != all_calendar_files[-1]:
            print("\n" + "=" * 30)

    print("\n" + "=" * 50)
    files_text = "file" if len(all_calendar_files) == 1 else "files"
    print(
        f"🎉 COMPLETE: Successfully processed {total_success} calendar operations across {len(all_calendar_files)} {files_text}!"
    )


if __name__ == "__main__":
    process_calendar_operations()
