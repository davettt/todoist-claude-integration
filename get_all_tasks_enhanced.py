"""
Enhanced ALL Tasks Analysis with comprehensive insights
Provides complete visibility into ALL Todoist tasks for strategic planning
"""

import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.todoist_client import TodoistClient
from utils.file_manager import save_personal_data


def build_lookup_maps(todoist_client):
    """Build project and section lookup maps"""
    projects = todoist_client.get_projects()
    sections = todoist_client.get_sections()

    if not projects:
        return {}, {}

    project_names = {p["id"]: p["name"] for p in projects}
    section_names = {}

    if sections:
        section_names = {s["id"]: s["name"] for s in sections}

    return project_names, section_names


def categorize_all_tasks(tasks):
    """Enhanced categorization including ALL tasks with comprehensive analysis"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)

    categories = {
        "overdue": [],
        "due_today": [],
        "due_tomorrow": [],
        "due_this_week": [],
        "due_next_week": [],
        "due_this_month": [],
        "due_future": [],
        "no_due_date": [],
    }

    for task in tasks:
        if not task.get("due"):
            categories["no_due_date"].append(task)
            continue

        due_date_str = task["due"]["date"]
        try:
            # Handle both date and datetime formats
            if "T" in due_date_str:
                due_date = datetime.fromisoformat(
                    due_date_str.replace("Z", "+00:00")
                ).date()
            else:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            if due_date < today:
                categories["overdue"].append(task)
            elif due_date == today:
                categories["due_today"].append(task)
            elif due_date == tomorrow:
                categories["due_tomorrow"].append(task)
            elif due_date <= next_week:
                categories["due_this_week"].append(task)
            elif due_date <= today + timedelta(days=14):
                categories["due_next_week"].append(task)
            elif due_date <= next_month:
                categories["due_this_month"].append(task)
            else:
                categories["due_future"].append(task)

        except ValueError:
            categories["no_due_date"].append(task)

    return categories


def analyze_by_project(tasks, project_names, section_names):
    """Analyze task distribution by project and section"""
    project_analysis = defaultdict(
        lambda: {
            "total": 0,
            "by_section": defaultdict(int),
            "by_priority": defaultdict(int),
            "with_due_dates": 0,
            "no_due_dates": 0,
            "overdue": 0,
            "tasks": [],
        }
    )

    today = datetime.now().date()

    for task in tasks:
        project_id = task.get("project_id", "")
        project_name = project_names.get(project_id, "Unknown Project")
        section_name = section_names.get(task.get("section_id", ""), "No Section")

        # Basic counts
        project_analysis[project_name]["total"] += 1
        project_analysis[project_name]["by_section"][section_name] += 1
        project_analysis[project_name]["by_priority"][task.get("priority", 1)] += 1
        project_analysis[project_name]["tasks"].append(task)

        # Due date analysis
        if task.get("due"):
            project_analysis[project_name]["with_due_dates"] += 1
            try:
                due_date_str = task["due"]["date"]
                if "T" in due_date_str:
                    due_date = datetime.fromisoformat(
                        due_date_str.replace("Z", "+00:00")
                    ).date()
                else:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

                if due_date < today:
                    project_analysis[project_name]["overdue"] += 1
            except ValueError:
                pass
        else:
            project_analysis[project_name]["no_due_dates"] += 1

    return dict(project_analysis)


def analyze_task_aging(tasks):
    """Analyze how long tasks have been sitting without updates"""
    from datetime import timezone

    now = datetime.now(timezone.utc)  # Make timezone-aware
    aging_analysis = {
        "recent": [],  # Created/updated within 7 days
        "aging": [],  # 7-30 days old
        "stale": [],  # 30+ days old
        "ancient": [],  # 90+ days old
    }

    for task in tasks:
        # Use created_at if available, otherwise estimate based on task ID
        created_str = task.get("created_at", "")
        if created_str:
            try:
                # Parse the datetime and make it timezone-aware if needed
                if "Z" in created_str:
                    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                elif "+" in created_str or created_str.endswith("Z"):
                    created = datetime.fromisoformat(created_str)
                else:
                    # Assume UTC if no timezone info
                    created = datetime.fromisoformat(created_str).replace(
                        tzinfo=timezone.utc
                    )

                # Ensure both datetimes are timezone-aware
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if now.tzinfo is None:
                    now = now.replace(tzinfo=timezone.utc)

                age_days = (now - created).days

                if age_days <= 7:
                    aging_analysis["recent"].append((task, age_days))
                elif age_days <= 30:
                    aging_analysis["aging"].append((task, age_days))
                elif age_days <= 90:
                    aging_analysis["stale"].append((task, age_days))
                else:
                    aging_analysis["ancient"].append((task, age_days))
            except (ValueError, TypeError):
                aging_analysis["aging"].append((task, "unknown"))
        else:
            aging_analysis["aging"].append((task, "unknown"))

    return aging_analysis


def identify_actionable_opportunities(categories, project_analysis):
    """Identify tasks that could be worked on now"""
    opportunities = {
        "quick_wins": [],  # No due date, low complexity
        "prep_work": [],  # Supporting tasks for upcoming deadlines
        "neglected_important": [],  # High priority, no due date
        "context_batching": {},  # Similar tasks that could be batched
        "project_momentum": [],  # Projects with only 1-2 tasks that could be completed
    }

    # Quick wins: Tasks without due dates that might be simple
    for task in categories["no_due_date"]:
        content = task["content"].lower()
        # Heuristics for quick tasks
        if any(
            word in content
            for word in [
                "call",
                "email",
                "book",
                "schedule",
                "check",
                "update",
                "cancel",
            ]
        ):
            opportunities["quick_wins"].append(task)
        elif task.get("priority", 1) >= 3:  # High priority without due date
            opportunities["neglected_important"].append(task)

    # Context batching: Group by labels or similar content
    label_groups = defaultdict(list)
    for task in categories["no_due_date"]:
        for label in task.get("labels", []):
            label_groups[label].append(task)

    # Only include groups with 2+ tasks
    opportunities["context_batching"] = {
        k: v for k, v in label_groups.items() if len(v) >= 2
    }

    # Project momentum: Projects with few remaining tasks
    for project, analysis in project_analysis.items():
        if 1 <= analysis["total"] <= 3 and analysis["overdue"] == 0:
            opportunities["project_momentum"].extend(analysis["tasks"])

    return opportunities


def display_comprehensive_analysis(tasks, project_names, section_names):
    """Display comprehensive task analysis"""
    print("🚀 COMPREHENSIVE TASK ANALYSIS")
    print("=" * 60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 Total Active Tasks: {len(tasks)}")
    print()

    # 1. Time-based categorization
    categories = categorize_all_tasks(tasks)

    print("⏰ TIME-BASED BREAKDOWN:")
    print("-" * 30)

    time_categories = [
        ("overdue", "❗ OVERDUE", "red"),
        ("due_today", "📅 DUE TODAY", "yellow"),
        ("due_tomorrow", "🔜 DUE TOMORROW", "blue"),
        ("due_this_week", "📆 THIS WEEK", "green"),
        ("due_next_week", "📋 NEXT WEEK", "cyan"),
        ("due_this_month", "📅 THIS MONTH", "white"),
        ("due_future", "🔮 FUTURE", "white"),
        ("no_due_date", "⏳ NO DUE DATE", "magenta"),
    ]

    def format_task_brief(task):
        project = project_names.get(task.get("project_id", ""), "Unknown")
        priority_map = {4: "🔴", 3: "🟡", 2: "🔵", 1: ""}
        priority = priority_map.get(task.get("priority", 1), "")
        return f"    • {task['content'][:50]}{'...' if len(task['content']) > 50 else ''}{priority} ({project})"

    for key, label, color in time_categories:
        count = len(categories[key])
        if count > 0:
            print(f"\n{label} ({count}):")
            # Show first 5 tasks, then summarize
            for task in categories[key][:5]:
                print(format_task_brief(task))
            if count > 5:
                print(f"    ... and {count - 5} more")

    # 2. Project analysis
    print("\n\n📂 PROJECT BREAKDOWN:")
    print("-" * 30)

    project_analysis = analyze_by_project(tasks, project_names, section_names)

    for project, analysis in sorted(
        project_analysis.items(), key=lambda x: x[1]["total"], reverse=True
    ):
        total = analysis["total"]
        overdue = analysis["overdue"]
        no_due = analysis["no_due_dates"]

        overdue_str = f" | {overdue} overdue" if overdue > 0 else ""
        no_due_str = f" | {no_due} no due date" if no_due > 0 else ""

        print(f"\n📁 {project} ({total} tasks{overdue_str}{no_due_str}):")

        # Show section breakdown
        for section, count in analysis["by_section"].items():
            if count > 0:
                print(f"  └── {section}: {count}")

        # Show priority breakdown if varied
        priority_counts = analysis["by_priority"]
        if len([p for p in priority_counts.values() if p > 0]) > 1:
            priority_str = ", ".join(
                [
                    f"P{p}:{c}"
                    for p, c in sorted(priority_counts.items(), reverse=True)
                    if c > 0
                ]
            )
            print(f"  └── Priorities: {priority_str}")

    # 3. Actionable opportunities
    print("\n\n🎯 ACTIONABLE OPPORTUNITIES:")
    print("-" * 30)

    opportunities = identify_actionable_opportunities(categories, project_analysis)

    if opportunities["quick_wins"]:
        print(f"\n⚡ QUICK WINS ({len(opportunities['quick_wins'])}):")
        print("  Tasks that could be completed quickly:")
        for task in opportunities["quick_wins"][:5]:
            print(format_task_brief(task))
        if len(opportunities["quick_wins"]) > 5:
            print(f"    ... and {len(opportunities['quick_wins']) - 5} more")

    if opportunities["neglected_important"]:
        print(
            f"\n🚨 HIGH PRIORITY, NO DUE DATE ({len(opportunities['neglected_important'])}):"
        )
        print("  Important tasks that might need scheduling:")
        for task in opportunities["neglected_important"]:
            print(format_task_brief(task))

    if opportunities["context_batching"]:
        print("\n🔄 CONTEXT BATCHING OPPORTUNITIES:")
        print("  Similar tasks that could be done together:")
        for label, tasks in opportunities["context_batching"].items():
            if len(tasks) >= 2:
                print(f"  📌 {label} ({len(tasks)} tasks)")

    if opportunities["project_momentum"]:
        print(
            f"\n🚀 PROJECT COMPLETION OPPORTUNITIES ({len(opportunities['project_momentum'])}):"
        )
        print("  Projects with few remaining tasks (could finish completely):")
        momentum_projects = defaultdict(list)
        for task in opportunities["project_momentum"]:
            project = project_names.get(task.get("project_id", ""), "Unknown")
            momentum_projects[project].append(task)

        for project, tasks in momentum_projects.items():
            print(f"  📁 {project} ({len(tasks)} remaining)")

    # 4. Task aging analysis
    print("\n\n📊 TASK AGING ANALYSIS:")
    print("-" * 30)

    aging = analyze_task_aging(tasks)
    print(f"🆕 Recent (≤7 days): {len(aging['recent'])}")
    print(f"📅 Aging (8-30 days): {len(aging['aging'])}")
    print(f"⚠️ Stale (31-90 days): {len(aging['stale'])}")
    print(f"🕸️ Ancient (90+ days): {len(aging['ancient'])}")

    if aging["stale"]:
        print("\n⚠️ STALE TASKS (consider reviewing):")
        for task, age in aging["stale"][:3]:
            age_str = f"{age} days" if isinstance(age, int) else "unknown age"
            print(f"  • {task['content'][:40]}... ({age_str})")

    if aging["ancient"]:
        print("\n🕸️ ANCIENT TASKS (consider archiving or re-prioritizing):")
        for task, age in aging["ancient"][:3]:
            age_str = f"{age} days" if isinstance(age, int) else "unknown age"
            print(f"  • {task['content'][:40]}... ({age_str})")

    return categories, project_analysis, opportunities


def save_comprehensive_tasks_json(
    tasks, project_names, section_names, categories, project_analysis, opportunities
):
    """Save comprehensive task data for Claude analysis"""

    def simplify_task(task):
        project = project_names.get(task.get("project_id", ""), "Unknown")
        section = section_names.get(task.get("section_id", ""), "")

        # Calculate task age if possible
        age_days = None
        if task.get("created_at"):
            try:
                from datetime import timezone

                created_str = task["created_at"]
                # Parse the datetime and make it timezone-aware if needed
                if "Z" in created_str:
                    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                elif "+" in created_str or created_str.endswith("Z"):
                    created = datetime.fromisoformat(created_str)
                else:
                    # Assume UTC if no timezone info
                    created = datetime.fromisoformat(created_str).replace(
                        tzinfo=timezone.utc
                    )

                now = datetime.now(timezone.utc)

                # Ensure both datetimes are timezone-aware
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if now.tzinfo is None:
                    now = now.replace(tzinfo=timezone.utc)

                age_days = (now - created).days
            except (ValueError, TypeError):
                pass

        return {
            "content": task["content"],
            "project": project,
            "section": section,
            "labels": task.get("labels", []),
            "priority": task.get("priority", 1),
            "due_date": task["due"]["date"][:10] if task.get("due") else None,
            "description": task.get("description", ""),
            "age_days": age_days,
            "task_id": task.get("id", ""),
            "url": task.get("url", ""),
        }

    # Build comprehensive Claude-friendly data structure
    claude_data = {
        "generated_at": datetime.now().isoformat(),
        "analysis_type": "comprehensive_all_tasks",
        "summary": {
            "total_active": len(tasks),
            "overdue_count": len(categories["overdue"]),
            "due_today_count": len(categories["due_today"]),
            "due_tomorrow_count": len(categories["due_tomorrow"]),
            "due_this_week_count": len(categories["due_this_week"]),
            "no_due_date_count": len(categories["no_due_date"]),
            "projects_count": len(project_analysis),
        },
        "time_categories": {
            "overdue": [simplify_task(task) for task in categories["overdue"]],
            "due_today": [simplify_task(task) for task in categories["due_today"]],
            "due_tomorrow": [
                simplify_task(task) for task in categories["due_tomorrow"]
            ],
            "due_this_week": [
                simplify_task(task) for task in categories["due_this_week"]
            ],
            "due_next_week": [
                simplify_task(task) for task in categories["due_next_week"]
            ],
            "due_this_month": [
                simplify_task(task) for task in categories["due_this_month"]
            ],
            "due_future": [simplify_task(task) for task in categories["due_future"]],
            "no_due_date": [simplify_task(task) for task in categories["no_due_date"]],
        },
        "project_analysis": {
            project: {
                "total_tasks": analysis["total"],
                "overdue_tasks": analysis["overdue"],
                "no_due_date_tasks": analysis["no_due_dates"],
                "section_breakdown": dict(analysis["by_section"]),
                "priority_breakdown": dict(analysis["by_priority"]),
                "tasks": [simplify_task(task) for task in analysis["tasks"]],
            }
            for project, analysis in project_analysis.items()
        },
        "opportunities": {
            "quick_wins": [simplify_task(task) for task in opportunities["quick_wins"]],
            "neglected_important": [
                simplify_task(task) for task in opportunities["neglected_important"]
            ],
            "context_batching": {
                label: [simplify_task(task) for task in tasks]
                for label, tasks in opportunities["context_batching"].items()
            },
            "project_momentum": [
                simplify_task(task) for task in opportunities["project_momentum"]
            ],
        },
    }

    # Save to personal data directory
    save_personal_data("all_tasks_comprehensive.json", claude_data)
    print("\n💾 Comprehensive task data saved!")
    print("📁 File: local_data/personal_data/all_tasks_comprehensive.json")
    print("🤖 Share this with Claude for strategic task management!")


def main():
    """Main function for comprehensive task analysis"""
    print("🔍 COMPREHENSIVE TASK ANALYSIS")
    print("=" * 35)
    print("Fetching and analyzing ALL your Todoist tasks for strategic insights...")
    print()

    try:
        # Initialize Todoist client
        todoist_client = TodoistClient()
        print("✅ Connected to Todoist API")

        # Fetch all data
        print("🔄 Fetching all tasks...")
        tasks = todoist_client.get_all_tasks()

        if not tasks:
            print("📭 No active tasks found!")
            return

        print("🔄 Fetching project and section information...")
        project_names, section_names = build_lookup_maps(todoist_client)

        # Perform comprehensive analysis
        categories, project_analysis, opportunities = display_comprehensive_analysis(
            tasks, project_names, section_names
        )

        # Save comprehensive data for Claude
        save_comprehensive_tasks_json(
            tasks,
            project_names,
            section_names,
            categories,
            project_analysis,
            opportunities,
        )

        print("\n🎉 Comprehensive analysis complete!")
        print(
            f"📊 Analyzed {len(tasks)} total tasks across {len(project_analysis)} projects"
        )
        print(
            f"🎯 Identified {len(opportunities['quick_wins'])} quick wins and {len(opportunities['neglected_important'])} high-priority items"
        )

        # Quick summary for immediate action
        print("\n" + "=" * 60)
        print("📋 IMMEDIATE ACTION SUMMARY:")
        print(f"  • Focus today: {len(categories['due_today'])} tasks due")
        print(f"  • Plan tomorrow: {len(categories['due_tomorrow'])} tasks due")
        print(f"  • Quick wins available: {len(opportunities['quick_wins'])}")
        print(
            f"  • High priority without dates: {len(opportunities['neglected_important'])}"
        )

        if categories["overdue"]:
            print(
                f"  • ⚠️ URGENT: {len(categories['overdue'])} overdue tasks need attention!"
            )

    except ValueError as e:
        print(str(e))
        print("\nPlease check your .env file and try again.")
    except Exception as e:
        print(f"❌ Error during comprehensive analysis: {str(e)}")
        print("Please check your API token and internet connection.")


if __name__ == "__main__":
    main()
