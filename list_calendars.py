#!/usr/bin/env python3
"""
Quick script to list your available calendars and their IDs
"""

import os
import sys

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.google_calendar_client import GoogleCalendarClient


def list_calendars():
    """List all available calendars with their IDs"""
    print("📅 YOUR GOOGLE CALENDARS")
    print("=" * 40)

    try:
        # Initialize calendar client
        calendar_client = GoogleCalendarClient()

        # Get all calendars
        calendars = calendar_client.get_calendars()

        if not calendars:
            print("❌ No calendars found!")
            return

        print(f"Found {len(calendars)} calendars:\\n")

        for i, calendar in enumerate(calendars, 1):
            calendar_id = calendar.get("id", "Unknown ID")
            summary = calendar.get("summary", "Untitled Calendar")
            is_primary = calendar.get("primary", False)
            access_role = calendar.get("accessRole", "Unknown")

            primary_text = " (PRIMARY)" if is_primary else ""

            print(f"{i}. {summary}{primary_text}")
            print(f"   📧 ID: {calendar_id}")
            print(f"   🔐 Access: {access_role}")
            print()

        print("💡 USAGE TIPS:")
        print("• Use 'primary' for your main calendar")
        print("• Use the full email ID for specific calendars")
        print("• Copy the calendar ID to use in JSON files")

    except Exception as e:
        print(f"❌ Error listing calendars: {str(e)}")


if __name__ == "__main__":
    list_calendars()
