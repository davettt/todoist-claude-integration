#!/usr/bin/env python3
"""
Learning Analyzer - Interactive dashboard for AI learning insights
Shows user their evolving preferences and provides actionable recommendations
"""

import os
import sys
from datetime import datetime

from utils.learning_engine import LearningEngine
from utils.profile_manager import ProfileManager


def print_header(title: str):
    """Print section header"""
    print()
    print("=" * 60)
    print(f"🧠 {title}")
    print("=" * 60)
    print()


def display_accuracy_analysis():
    """Display accuracy trends and analysis"""
    print_header("ACCURACY ANALYSIS")

    engine = LearningEngine()
    analysis = engine.analyze_feedback_patterns()

    if analysis.get("status") == "insufficient_data":
        print("⚠️  Not enough feedback data yet")
        print(f"   Current: {analysis.get('feedback_count', 0)} entries")
        print("   Need: At least 5 feedback entries")
        print()
        return

    # Overall stats
    total = analysis.get("feedback_count", 0)
    print(f"📊 Total Feedback Entries: {total}")
    print()

    # Accuracy by level
    if analysis.get("accuracy_by_level"):
        print("📈 Accuracy by Prediction Level:")
        print()
        for level, stats in analysis["accuracy_by_level"].items():
            bar_length = int(stats["accuracy"] / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {level.upper():8} [{bar}] {stats['accuracy']}%")
            print(f"            {stats['accurate']}/{stats['total']} correct")
        print()

    # Time trends
    trends = analysis.get("time_trends", {})
    if trends.get("status") != "insufficient_data":
        print("📉 Accuracy Trends Over Time:")
        print()
        print(f"   Early accuracy:   {trends.get('early_accuracy', 0)}%")
        print(f"   Recent accuracy:  {trends.get('recent_accuracy', 0)}%")
        print(f"   Trend:            {trends.get('trend', 'unknown').title()}")
        improvement = trends.get("improvement", 0)
        if improvement > 0:
            print(f"   Change:           ↑ {improvement:.1f}% improvement")
        elif improvement < 0:
            print(f"   Change:           ↓ {abs(improvement):.1f}% decline")
        else:
            print("   Change:           → Stable")
        print()

    # Strongest and weakest
    if analysis.get("strongest_areas"):
        print("✅ Strongest Areas (80%+ accurate):")
        for area in analysis["strongest_areas"]:
            print(f"   • {area.title()}")
        print()

    if analysis.get("weakest_areas"):
        print("⚠️  Areas for Improvement (<60% accurate):")
        for area in analysis["weakest_areas"]:
            print(f"   • {area.title()}")
        print()


def display_profile_suggestions():
    """Display profile optimization suggestions"""
    print_header("PROFILE OPTIMIZATION SUGGESTIONS")

    engine = LearningEngine()
    suggestions = engine.generate_profile_suggestions()

    if suggestions.get("status") == "insufficient_data":
        print("⚠️  Not enough feedback data yet")
        print(f"   Current: {suggestions.get('current_feedback_count', 0)} entries")
        print("   Need: At least 10 feedback entries for suggestions")
        print()
        return

    any_suggestions = False

    # Add interests
    if suggestions.get("add_interests"):
        any_suggestions = True
        print("🔼 Interests to Add:")
        print()
        for interest in suggestions["add_interests"]:
            print(f"   + {interest['interest']}")
            print(f"     → {interest['reason']}")
            print(f"     Confidence: {interest['confidence']}")
            print()

    # Remove interests
    if suggestions.get("remove_interests"):
        any_suggestions = True
        print("🔽 Interests to Review:")
        print()
        for interest in suggestions["remove_interests"]:
            print(f"   - {interest['interest']}")
            print(f"     → {interest['reason']}")
            print()

    # Add senders
    if suggestions.get("add_senders"):
        any_suggestions = True
        print("✉️  Trusted Senders to Add:")
        print()
        for sender in suggestions["add_senders"]:
            print(f"   + {sender['sender']}")
            print(f"     → {sender['reason']}")
            print(f"     Confidence: {sender['confidence']}")
            print()

    if not any_suggestions:
        print("💭 No strong suggestions at this time")
        print("    Continue providing feedback for better recommendations")
        print()

    # Confidence notes
    if suggestions.get("confidence_notes"):
        print("ℹ️  Confidence Assessment:")
        print(f"   {suggestions['confidence_notes']}")
        print()


def display_sender_analysis():
    """Display sender-specific patterns"""
    print_header("TOP SENDERS ANALYSIS")

    engine = LearningEngine()
    analysis = engine.analyze_feedback_patterns()

    if analysis.get("status") == "insufficient_data":
        print("⚠️  Not enough feedback data yet")
        print()
        return

    senders = analysis.get("sender_patterns", {})

    if not senders:
        print("No sender patterns identified yet")
        print()
        return

    print("📧 Your Top Senders:")
    print()

    for i, (sender, stats) in enumerate(list(senders.items())[:5], 1):
        print(f"{i}. {sender}")
        print(f"   • Total emails: {stats['total_emails']}")
        print(f"   • Prediction accuracy: {stats['accuracy']}%")

        # Show high-value metrics
        high_value_rate = stats.get("high_value_rate", 0)
        escalation_rate = stats.get("escalation_rate", 0)

        if high_value_rate > 0:
            print(
                f"   • High-value content: {stats['high_value_emails']}/{stats['total_emails']} ({high_value_rate}%)"
            )

        if escalation_rate > 0:
            print(
                f"   • Escalated (marked more important): {stats['escalated_emails']}/{stats['total_emails']} ({escalation_rate}%)"
            )

        # Add visual feedback based on meaningful metrics
        if escalation_rate >= 20:
            print("   ⬆️ Frequently escalated - consider adding to trusted senders")
        elif high_value_rate >= 30:
            print("   ✅ Often contains high-priority content")
        else:
            print("   📊 Mostly low-priority content user agrees with")
        print()


def display_content_patterns():
    """Display AI-identified content patterns and preferences"""
    print_header("CONTENT PATTERN ANALYSIS")

    engine = LearningEngine()
    patterns = engine.analyze_content_patterns()

    if patterns.get("status") == "insufficient_data":
        print("⚠️  Not enough high-value content data yet")
        print(f"   {patterns.get('message')}")
        print()
        return

    print(f"📊 Analysis based on {patterns.get('high_value_count')} high-value emails")
    print()

    # Preferred categories
    categories = patterns.get("preferred_categories", {})
    if categories:
        print("🎯 Your Preferred Content Categories:")
        for i, (category, count) in enumerate(list(categories.items())[:5], 1):
            bar_length = (
                int((count / max(categories.values())) * 20)
                if categories.values()
                else 0
            )
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {i}. {category:20} [{bar}] {count} emails")
        print()

    # Technology interests
    technologies = patterns.get("technology_interests", {})
    if technologies:
        print("💻 Technology & Tools You Care About:")
        for i, (tech, count) in enumerate(list(technologies.items())[:8], 1):
            print(f"   {i:2}. {tech:25} ({count} mentions)")
        print()

    # Topic themes
    topics = patterns.get("topic_themes", {})
    if topics:
        print("🏷️  Common Topic Themes:")
        for i, (topic, count) in enumerate(list(topics.items())[:8], 1):
            print(f"   {i:2}. {topic:25} ({count} mentions)")
        print()

    # Insights
    if categories and technologies:
        print("💡 Insights:")
        top_category = list(categories.keys())[0]
        top_tech = list(technologies.keys())[0]
        print(f"   • You consistently prioritize {top_category} content")
        print(f"   • {top_tech} is your most frequently encountered topic")
        print()


def display_learning_weights():
    """Display learning weights being applied"""
    print_header("LEARNING WEIGHTS (AI ADJUSTMENTS)")

    engine = LearningEngine()
    weights = engine.calculate_learning_weights()

    if weights.get("status") == "no_data":
        print("No feedback data to calculate weights")
        print()
        return

    print("📊 Current Learning Weights:")
    print()

    base_conf = weights.get("base_confidence", 0)
    print(f"Base Confidence: {base_conf*100:.0f}%")
    print()

    print("Active Adjustments:")
    min_threshold = weights.get("minimum_confidence_threshold", 0.3)
    print(f"  • Minimum confidence threshold: {min_threshold*100:.0f}%")

    trusted_boost = weights.get("trusted_sender_boost", 1.0)
    print(f"  • Trusted sender boost: {trusted_boost:.1f}x")

    anti_patterns = weights.get("anti_patterns_weight", 1.0)
    print(f"  • Anti-pattern weight: {anti_patterns:.1f}x")

    print()
    print("📈 Per-Level Confidence:")
    for level in ["urgent", "high", "medium", "low"]:
        key = f"level_{level}_confidence"
        if key in weights:
            conf = weights[key]
            bar_length = int(conf * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   {level.upper():8} [{bar}] {conf*100:.0f}%")
    print()


def display_full_report():
    """Display comprehensive learning report"""
    print_header("COMPREHENSIVE LEARNING REPORT")

    engine = LearningEngine()

    # Generate report
    report_path = "local_data/email_digests/learning_report_latest.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    report = engine.export_learning_report(output_path=report_path)

    # Display to console
    print(report)
    print()
    print(f"✅ Full report saved to: {report_path}")
    print()


def apply_profile_suggestions():
    """Guide user through applying suggestions to their profile with confidence categorization"""
    print_header("APPLY PROFILE SUGGESTIONS")

    engine = LearningEngine()
    suggestions = engine.generate_profile_suggestions()

    if suggestions.get("status") == "insufficient_data":
        print("⚠️  Not enough feedback data for suggestions")
        print()
        return

    # Categorize suggestions by confidence
    categorized = {"high_confidence": [], "medium_confidence": [], "low_confidence": []}

    if suggestions.get("add_interests"):
        for interest in suggestions["add_interests"]:
            conf = interest.get("confidence", "Medium")
            if "high" in conf.lower():
                categorized["high_confidence"].append(("interest", interest))
            elif "medium" in conf.lower():
                categorized["medium_confidence"].append(("interest", interest))
            else:
                categorized["low_confidence"].append(("interest", interest))

    if suggestions.get("add_senders"):
        for sender in suggestions["add_senders"]:
            conf = sender.get("confidence", "Medium")
            if "high" in conf.lower():
                categorized["high_confidence"].append(("sender", sender))
            elif "medium" in conf.lower():
                categorized["medium_confidence"].append(("sender", sender))
            else:
                categorized["low_confidence"].append(("sender", sender))

    # Display high-confidence suggestions
    if categorized["high_confidence"]:
        print("🎯 HIGH CONFIDENCE (Ready to apply):")
        print()
        for idx, (stype, item) in enumerate(categorized["high_confidence"], 1):
            if stype == "interest":
                print(f"   [✓] {item['interest']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'High')}")
            else:
                print(f"   [✓] {item['sender']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'High')}")
        print()

    # Display medium-confidence suggestions
    if categorized["medium_confidence"]:
        print("⚠️  MEDIUM CONFIDENCE (Review recommended):")
        print()
        for idx, (stype, item) in enumerate(categorized["medium_confidence"], 1):
            if stype == "interest":
                print(f"   [ ] {item['interest']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'Medium')}")
            else:
                print(f"   [ ] {item['sender']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'Medium')}")
        print()

    # Display low-confidence suggestions
    if categorized["low_confidence"]:
        print("💭 LOW CONFIDENCE (Consider carefully):")
        print()
        for idx, (stype, item) in enumerate(categorized["low_confidence"], 1):
            if stype == "interest":
                print(f"   [ ] {item['interest']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'Low')}")
            else:
                print(f"   [ ] {item['sender']} - {item['reason']}")
                print(f"       Confidence: {item.get('confidence', 'Low')}")
        print()

    # Prompt user for action
    print("Actions:")
    print("  [a] Apply all high confidence suggestions")
    print("  [r] Review and select individually")
    print("  [s] Skip for now")
    print()

    choice = input("Choose an action (a/r/s): ").strip().lower()

    if choice == "s":
        print("❌ Changes cancelled")
        print()
        return

    # Prepare interests and senders to apply
    interests_to_apply = []
    senders_to_apply = []

    manager = ProfileManager()
    profile_before = {
        "core_interests": manager.profile.get("core_interests", []).copy(),
        "trusted_senders": manager.profile.get("trusted_senders", []).copy(),
        "active_projects": manager.profile.get("active_projects", []).copy(),
    }

    if choice == "a":
        # Apply only high-confidence
        for stype, item in categorized["high_confidence"]:
            if stype == "interest":
                interests_to_apply.append(item["interest"])
            else:
                senders_to_apply.append(item["sender"])
    elif choice == "r":
        # Interactive review mode
        print()
        print("Review suggestions individually:")
        print()

        all_to_review = (
            categorized["high_confidence"]
            + categorized["medium_confidence"]
            + categorized["low_confidence"]
        )

        for idx, (stype, item) in enumerate(all_to_review, 1):
            if stype == "interest":
                name = item["interest"]
                reason = item["reason"]
                conf = item.get("confidence", "Unknown")
            else:
                name = item["sender"]
                reason = item["reason"]
                conf = item.get("confidence", "Unknown")

            print(f"{idx}. {name}")
            print(f"   Reason: {reason}")
            print(f"   Confidence: {conf}")
            response = input("   Add this? (y/n): ").strip().lower()

            if response == "y":
                if stype == "interest":
                    interests_to_apply.append(name)
                else:
                    senders_to_apply.append(name)
            print()

    if not interests_to_apply and not senders_to_apply:
        print("❌ No suggestions selected")
        print()
        return

    # Apply using batch methods
    print("Applying suggestions to profile...")
    print()

    results = {}
    if interests_to_apply:
        result = manager.batch_add_interests(interests_to_apply, backup_before=True)
        results["interests"] = result

        print("✅ Interests:")
        for interest in result["added"]:
            print(f"   + {interest}")
        if result["duplicates"]:
            print("   ⊘ Already present:", ", ".join(result["duplicates"]))
        if result["similar"]:
            for interest, similar_list in result["similar"].items():
                print(
                    f"   ⚠️  Skipped '{interest}' (similar to: {', '.join(similar_list)})"
                )
        print()

    if senders_to_apply:
        # Add trusted senders
        current_senders = manager.profile.get("trusted_senders", [])
        added_senders = []
        for sender in senders_to_apply:
            if sender not in current_senders:
                current_senders.append(sender)
                added_senders.append(sender)

        if added_senders:
            manager.profile["trusted_senders"] = current_senders
            manager._save_profile()

        print("✅ Trusted Senders:")
        for sender in added_senders:
            print(f"   + {sender}")
        duplicates = set(senders_to_apply) - set(added_senders)
        if duplicates:
            print("   ⊘ Already present:", ", ".join(duplicates))
        print()

    # Show profile comparison
    profile_after = {
        "core_interests": manager.profile.get("core_interests", []).copy(),
        "trusted_senders": manager.profile.get("trusted_senders", []).copy(),
        "active_projects": manager.profile.get("active_projects", []).copy(),
    }

    comparison = manager.get_profile_comparison(profile_before, profile_after)
    print(f"📊 Profile Summary: {comparison['summary']}")
    print()

    # Backup confirmation
    backup_path = (
        manager.profile_path.replace(
            ".json", f"_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )
        if "interests" in results and results["interests"].get("backup_created")
        else "Profile not backed up"
    )

    if backup_path != "Profile not backed up":
        print("💾 Backup created before changes")
    print()
    print(
        "✅ Profile successfully updated! Changes will improve AI analysis going forward."
    )
    print()


def interactive_menu():
    """Main interactive menu"""
    while True:
        print()
        print("=" * 60)
        print("🧠 EMAIL DIGEST AI LEARNING ANALYZER")
        print("=" * 60)
        print()
        print("What would you like to do?")
        print()
        print("  1. View accuracy analysis & trends")
        print("  2. View profile optimization suggestions")
        print("  3. View sender analysis & patterns")
        print("  4. View content pattern analysis (AI-identified themes)")
        print("  5. View learning weights & AI adjustments")
        print("  6. Generate comprehensive learning report")
        print("  7. Apply suggestions to profile")
        print("  8. Back to main menu")
        print()

        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            display_accuracy_analysis()
            input("Press Enter to continue...")

        elif choice == "2":
            display_profile_suggestions()
            input("Press Enter to continue...")

        elif choice == "3":
            display_sender_analysis()
            input("Press Enter to continue...")

        elif choice == "4":
            display_content_patterns()
            input("Press Enter to continue...")

        elif choice == "5":
            display_learning_weights()
            input("Press Enter to continue...")

        elif choice == "6":
            display_full_report()
            input("Press Enter to continue...")

        elif choice == "7":
            apply_profile_suggestions()
            input("Press Enter to continue...")

        elif choice == "8":
            print("\n👋 Returning to main menu...")
            break

        else:
            print("\n❌ Invalid choice. Please choose 1-8.")
            input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    print()
    print("🧠 AI LEARNING ANALYZER")
    print()

    # Check if there's feedback data
    feedback_path = "local_data/personal_data/email_feedback_log.json"
    if not os.path.exists(feedback_path):
        print("⚠️  No feedback data found yet")
        print()
        print("To use the learning analyzer:")
        print("  1. Generate email digests (option 5 in daily manager)")
        print("  2. Review digests interactively (option 6 in daily manager)")
        print("  3. Rate emails with 👍 👎 ⬆️ ⬇️")
        print()
        print("Once you've rated 5+ emails, return here to see learning insights!")
        print()
        return

    # Show summary stats
    engine = LearningEngine()
    analysis = engine.analyze_feedback_patterns()

    if analysis.get("status") == "insufficient_data":
        print(f"📊 You have {analysis.get('feedback_count', 0)} feedback entries")
        print("   Minimum needed: 5 entries for analysis")
        print()
        return

    feedback_count = analysis.get("feedback_count", 0)
    print(f"✅ Learning data available ({feedback_count} feedback entries)")
    print()

    # Show quick summary
    trends = analysis.get("time_trends", {})
    if trends.get("status") != "insufficient_data":
        accuracy = trends.get("recent_accuracy", 0)
        trend_emoji = (
            "📈"
            if trends.get("trend") == "improving"
            else "📉"
            if trends.get("trend") == "declining"
            else "→"
        )
        print(f"📊 Recent Accuracy: {accuracy}% {trend_emoji}")

    strongest = analysis.get("strongest_areas", [])
    if strongest:
        print(f"✅ Best at: {', '.join(strongest[:2])}")

    weakest = analysis.get("weakest_areas", [])
    if weakest:
        print(f"⚠️  Challenge: {', '.join(weakest[:2])}")

    print()

    # Start interactive menu
    interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
