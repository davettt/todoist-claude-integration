#!/usr/bin/env python3
"""
Calendar Data Export and Analysis - TIMEZONE FIXED VERSION
Fetches calendar data and creates insights for Claude analysis
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.google_calendar_client import GoogleCalendarClient
from utils.file_manager import save_personal_data


def get_local_timezone():
    """Get the local timezone offset"""
    import time

    # Get local timezone offset in seconds
    local_offset = -time.timezone if not time.daylight else -time.altzone
    return timezone(timedelta(seconds=local_offset))


def analyze_calendar_availability(calendar_client, days_ahead=14):
    """Analyze calendar availability for the next N days"""

    # Calculate time range with proper timezone
    local_tz = get_local_timezone()
    now = datetime.now(local_tz)
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=days_ahead)

    # Format for API (use ISO format with timezone, not 'Z')
    # Note: These are calculated but not used in the current implementation
    # time_min = start_time.isoformat()
    # time_max = end_time.isoformat()

    # Process events day by day for consistency with free time analysis
    processed_events = []
    for i in range(days_ahead):
        day_start = start_time + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_time_min = day_start.isoformat()
        day_time_max = day_end.isoformat()

        day_events = calendar_client.get_events("primary", day_time_min, day_time_max)
        if day_events:
            for event in day_events:
                start_info = event.get("start", {})
                end_info = event.get("end", {})

                # Handle different time formats
                start_dt_str = start_info.get("dateTime", start_info.get("date", ""))
                end_dt_str = end_info.get("dateTime", end_info.get("date", ""))

                if start_dt_str and end_dt_str:
                    try:
                        # Parse datetime
                        if "T" in start_dt_str:
                            start_dt = datetime.fromisoformat(
                                start_dt_str.replace("Z", "+00:00")
                            )
                            end_dt = datetime.fromisoformat(
                                end_dt_str.replace("Z", "+00:00")
                            )
                            is_all_day = False
                        else:
                            # All-day event
                            start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d")
                            end_dt = datetime.strptime(end_dt_str, "%Y-%m-%d")
                            is_all_day = True

                        processed_events.append(
                            {
                                "id": event.get("id", ""),
                                "summary": event.get("summary", "Untitled"),
                                "description": event.get("description", ""),
                                "start": start_dt.isoformat(),
                                "end": end_dt.isoformat(),
                                "duration_minutes": (end_dt - start_dt).total_seconds()
                                / 60,
                                "date": start_dt.strftime("%Y-%m-%d"),
                                "day_of_week": start_dt.strftime("%A"),
                                "is_all_day": is_all_day,
                                "calendar_id": "primary",
                            }
                        )

                    except ValueError as e:
                        print(f"⚠️ Error parsing event time: {e}")
                        continue

    # Find free time slots - analyze each day individually for better accuracy
    processed_free_slots = []
    for i in range(days_ahead):
        day_start = start_time + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_time_min = day_start.isoformat()
        day_time_max = day_end.isoformat()

        day_free_slots = calendar_client.find_free_time(
            "primary", day_time_min, day_time_max, 30
        )

        for slot in day_free_slots:
            try:
                start_dt = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(slot["end"].replace("Z", "+00:00"))
                duration = slot["duration_minutes"]

                # Only include slots that overlap with working hours, but trim to working hours
                if duration >= 30:
                    # Calculate working hours for this day
                    working_start_hour = 7
                    working_end_hour = 20

                    start_date = start_dt.date()
                    working_start = datetime.combine(
                        start_date, datetime.min.time().replace(hour=working_start_hour)
                    )
                    working_end = datetime.combine(
                        start_date, datetime.min.time().replace(hour=working_end_hour)
                    )

                    # Make timezone aware
                    if start_dt.tzinfo:
                        working_start = working_start.replace(tzinfo=start_dt.tzinfo)
                        working_end = working_end.replace(tzinfo=start_dt.tzinfo)

                    # Trim slot to working hours
                    trimmed_start = max(start_dt, working_start)
                    trimmed_end = min(end_dt, working_end)

                    # Only include if there's meaningful overlap
                    if trimmed_start < trimmed_end:
                        trimmed_duration = (
                            trimmed_end - trimmed_start
                        ).total_seconds() / 60

                        if (
                            trimmed_duration >= 30
                        ):  # At least 30 minutes in working hours
                            # Calculate how many 3-hour focus blocks fit in this slot
                            focus_blocks_in_slot = int(
                                trimmed_duration / 180
                            )  # 180 min = 3 hours

                            processed_free_slots.append(
                                {
                                    "start": trimmed_start.strftime("%Y-%m-%d %H:%M"),
                                    "end": trimmed_end.strftime("%Y-%m-%d %H:%M"),
                                    "duration_minutes": trimmed_duration,
                                    "duration_formatted": format_duration(
                                        trimmed_duration
                                    ),
                                    "date": trimmed_start.strftime("%Y-%m-%d"),
                                    "day_of_week": trimmed_start.strftime("%A"),
                                    "is_large_block": trimmed_duration
                                    >= 120,  # 2+ hours
                                    "is_focus_time": trimmed_duration
                                    >= 180,  # 3+ hours
                                    "focus_blocks_count": focus_blocks_in_slot,  # How many 3h blocks fit
                                }
                            )
            except ValueError:
                continue

    # Daily analysis
    daily_analysis = {}
    for i in range(days_ahead):
        date = (start_time + timedelta(days=i)).strftime("%Y-%m-%d")
        day_name = (start_time + timedelta(days=i)).strftime("%A")

        day_events = [
            e for e in processed_events if e["date"] == date and not e["is_all_day"]
        ]
        day_free_slots = [s for s in processed_free_slots if s["date"] == date]

        # Calculate metrics
        total_busy_minutes = sum(e["duration_minutes"] for e in day_events)
        total_free_minutes = sum(s["duration_minutes"] for s in day_free_slots)
        large_blocks = [s for s in day_free_slots if s["is_large_block"]]
        focus_slots = [s for s in day_free_slots if s["is_focus_time"]]
        # Count total focus blocks (sum of focus_blocks_count from each slot)
        total_focus_blocks = sum(s.get("focus_blocks_count", 0) for s in day_free_slots)

        # Availability rating (1-10)
        if total_free_minutes >= 480:  # 8+ hours
            rating = 10
        elif total_free_minutes >= 360:  # 6+ hours
            rating = 8
        elif total_free_minutes >= 240:  # 4+ hours
            rating = 6
        elif total_free_minutes >= 120:  # 2+ hours
            rating = 4
        elif total_free_minutes >= 60:  # 1+ hour
            rating = 2
        else:
            rating = 1

        daily_analysis[date] = {
            "day_name": day_name,
            "events_count": len(day_events),
            "events": day_events,
            "free_slots_count": len(day_free_slots),
            "free_slots": day_free_slots,
            "total_busy_hours": round(total_busy_minutes / 60, 1),
            "total_free_hours": round(total_free_minutes / 60, 1),
            "large_blocks_count": len(large_blocks),
            "focus_blocks_count": total_focus_blocks,  # Total number of 3h blocks
            "focus_slots_count": len(focus_slots),  # Number of slots with 3+ hours
            "availability_rating": rating,
            "best_for_meetings": len(day_free_slots) > 0
            and any(30 <= s["duration_minutes"] <= 90 for s in day_free_slots),
            "best_for_deep_work": total_focus_blocks > 0,
            "is_weekend": day_name in ["Saturday", "Sunday"],
        }

    return {
        "generated_at": datetime.now(local_tz).isoformat(),
        "analysis_period": f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
        "summary": {
            "total_events": len(processed_events),
            "total_free_slots": len(processed_free_slots),
            "best_days_for_work": [
                date
                for date, analysis in daily_analysis.items()
                if analysis["availability_rating"] >= 8
            ],
            "busy_days": [
                date
                for date, analysis in daily_analysis.items()
                if analysis["availability_rating"] <= 3
            ],
            "focus_time_available": sum(
                1
                for analysis in daily_analysis.values()
                if analysis["focus_blocks_count"] > 0
            ),
            "total_focus_blocks": sum(
                analysis["focus_blocks_count"] for analysis in daily_analysis.values()
            ),
        },
        "daily_analysis": daily_analysis,
        "all_events": processed_events,
        "free_time_slots": processed_free_slots,
    }


def format_duration(minutes):
    """Format duration in human-readable format"""
    hours = int(minutes // 60)
    mins = int(minutes % 60)

    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"


def display_calendar_summary(calendar_data):
    """Display calendar availability summary"""
    print("📅 CALENDAR AVAILABILITY ANALYSIS")
    print("=" * 45)

    summary = calendar_data["summary"]
    daily_analysis = calendar_data["daily_analysis"]

    print(f"📊 Analysis period: {calendar_data['analysis_period']}")
    print(f"📅 Total events: {summary['total_events']}")
    print(f"⏰ Free time slots: {summary['total_free_slots']}")
    print(f"🎯 Best work days: {len(summary['best_days_for_work'])}")
    print(f"🔴 Busy days: {len(summary['busy_days'])}")
    print(f"💪 Days with focus time: {summary['focus_time_available']}")
    print(f"🎯 Total focus blocks (3h each): {summary['total_focus_blocks']}")
    print(
        f"   → That's {summary['total_focus_blocks'] * 3} hours of deep work capacity!"
    )

    # Show next few days
    print("\n📅 UPCOMING DAYS OVERVIEW:")
    print("-" * 30)

    for date, analysis in list(daily_analysis.items())[:7]:  # Next 7 days
        rating_emoji = (
            "🟢"
            if analysis["availability_rating"] >= 8
            else "🟡"
            if analysis["availability_rating"] >= 6
            else "🔴"
        )

        print(f"{rating_emoji} {analysis['day_name']} ({date}):")
        print(
            f"   Events: {analysis['events_count']} | Free: {analysis['total_free_hours']}h | Rating: {analysis['availability_rating']}/10"
        )

        if analysis["events"]:
            for event in analysis["events"][:2]:  # Show first 2 events
                start_time = event["start"][11:16]  # Extract HH:MM
                print(f"   • {start_time} {event['summary']}")
            if len(analysis["events"]) > 2:
                print(f"   • ... and {len(analysis['events']) - 2} more")

        if analysis["focus_blocks_count"] > 0:
            print(
                f"   🎯 {analysis['focus_blocks_count']} focus time block(s) available"
            )

    # Highlight best opportunities
    if summary["best_days_for_work"]:
        print("\n🌟 BEST PRODUCTIVITY OPPORTUNITIES:")
        for date in summary["best_days_for_work"][:3]:
            analysis = daily_analysis[date]
            print(
                f"  • {analysis['day_name']} ({date}): {analysis['total_free_hours']}h free"
            )


def save_calendar_data_for_claude(calendar_data):
    """Save calendar data in format optimized for Claude analysis"""

    # Create Claude-optimized structure
    claude_data = {
        "generated_at": calendar_data["generated_at"],
        "data_type": "calendar_availability_analysis",
        "summary": calendar_data["summary"],
        "daily_availability": {},
        "upcoming_events": calendar_data["all_events"][:20],  # Next 20 events
        "optimal_time_slots": [],
    }

    # Process daily availability for Claude
    for date, analysis in calendar_data["daily_analysis"].items():
        claude_data["daily_availability"][date] = {
            "day_name": analysis["day_name"],
            "availability_rating": analysis["availability_rating"],
            "total_free_hours": analysis["total_free_hours"],
            "events_count": analysis["events_count"],
            "large_blocks_available": analysis["large_blocks_count"],
            "ideal_for_focus_work": analysis["best_for_deep_work"],
            "good_for_meetings": analysis["best_for_meetings"],
            "is_weekend": analysis["is_weekend"],
        }

    # Extract optimal time slots for task scheduling
    for slot in calendar_data["free_time_slots"]:
        if slot["duration_minutes"] >= 60:  # 1+ hour slots
            claude_data["optimal_time_slots"].append(
                {
                    "date": slot["date"],
                    "day_name": slot["day_of_week"],
                    "start_time": slot["start"],
                    "duration": slot["duration_formatted"],
                    "suitable_for": (
                        "focus_work"
                        if slot["is_focus_time"]
                        else "admin_work"
                        if slot["is_large_block"]
                        else "quick_tasks"
                    ),
                }
            )

    # Save for Claude
    save_personal_data("calendar_availability.json", claude_data)
    print("🤖 Calendar data saved for Claude analysis!")


def main():
    """Main function to export calendar data"""
    print("📅 CALENDAR DATA EXPORT & ANALYSIS")
    print("=" * 35)
    print("Fetching your calendar data and creating availability insights...")
    print()

    try:
        # Initialize calendar client
        print("🔄 Connecting to Google Calendar...")
        calendar_client = GoogleCalendarClient()
        print("✅ Connected to Google Calendar API")

        # Get calendar list
        print("🔄 Fetching calendar information...")
        calendars = calendar_client.get_calendars()
        if calendars:
            print(f"📋 Found {len(calendars)} calendars")
            for cal in calendars[:3]:  # Show first 3
                primary_text = " (PRIMARY)" if cal.get("primary") else ""
                print(f"  • {cal.get('summary', 'Untitled')}{primary_text}")

        # Analyze calendar availability
        print("🔄 Analyzing calendar availability...")
        calendar_data = analyze_calendar_availability(calendar_client)

        if calendar_data is None:
            print("❌ Failed to analyze calendar data")
            return

        # Display summary
        display_calendar_summary(calendar_data)

        # Save data for Claude
        save_calendar_data_for_claude(calendar_data)

        # Save complete data for internal use
        save_personal_data("calendar_full_analysis.json", calendar_data)

        print("\n💾 Calendar data exported successfully!")
        print("📁 Files saved:")
        print("  • calendar_availability.json (for Claude)")
        print("  • calendar_full_analysis.json (complete data)")
        print("🤖 Share calendar_availability.json with Claude for task scheduling!")

    except ValueError as e:
        error_str = str(e)
        print(f"❌ Setup Error: {error_str}")

        # Handle expired token specially
        if "EXPIRED_TOKEN" in error_str:
            print("\n🔐 Token Recovery Instructions:")
            print("Your Google Calendar token has expired or been revoked.")
            print("\nQuick fix - run this command:")
            print("  bash scripts/reauth_calendar.sh")
            print("\nOr manually recover:")
            print("  1. Delete: rm local_data/calendar_token.json")
            print("  2. Re-run this script to trigger OAuth re-authentication")
        else:
            print("\nSetup Instructions:")
            print(
                "1. Install Google Calendar API: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
            print("2. Download credentials from Google Cloud Console")
            print("3. Save as local_data/calendar_credentials.json")
    except Exception as e:
        print(f"❌ Error during calendar export: {str(e)}")
        print("Please check your Google Calendar access and try again.")


if __name__ == "__main__":
    main()
