#!/usr/bin/env python3
"""
Interactive Digest Review
Shows each email with AI analysis, then immediately asks for rating
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.email_feedback_tracker import EmailFeedbackTracker


def review_digest_interactive(digest_path: str = None):
    """
    Interactive digest review - show email, then rate it immediately

    Args:
        digest_path: Optional path to digest markdown file
    """
    print("\n" + "=" * 70)
    print("📧 INTERACTIVE DIGEST REVIEW")
    print("=" * 70)
    print()
    print("Read each email with AI analysis, then rate the prediction!")
    print()

    # Initialize feedback tracker
    tracker = EmailFeedbackTracker()

    # If no digest path provided, find the latest
    if not digest_path:
        import glob

        digest_dir = "local_data/email_digests"
        pattern = os.path.join(digest_dir, "digest_*.md")
        digests = glob.glob(pattern)

        if not digests:
            print("❌ No digests found!")
            print(f"   Expected location: {digest_dir}/")
            print()
            print("Generate a digest first using option 5 in daily_manager.py")
            return

        # Sort by modification time (newest first)
        digests.sort(key=os.path.getmtime, reverse=True)
        digest_path = digests[0]

    if not os.path.exists(digest_path):
        print(f"❌ Digest not found: {digest_path}")
        return

    print(f"📄 Reviewing: {os.path.basename(digest_path)}")
    print()

    # Parse the digest file to extract emails with full content
    emails = parse_digest_with_content(digest_path)

    if not emails:
        print("❌ No emails found in digest")
        return

    print(f"Found {len(emails)} emails to review")
    print()
    print("=" * 70)
    print()

    # Review each email interactively
    rated_count = 0

    for i, email in enumerate(emails, 1):
        # Show email with AI analysis
        show_email_with_analysis(email, i, len(emails))

        # Ask for rating
        rating = get_rating()

        if rating == "quit":
            print("\n💾 Saving ratings and exiting...")
            show_summary(tracker, rated_count)
            return

        if rating == "skip":
            print("⏭️  Skipped")
            print()
            continue

        # Record feedback
        feedback_type, actual_interest = rating
        notes = input("Optional notes (or press Enter to skip): ").strip()

        success = tracker.record_feedback(
            email_subject=email["subject"],
            email_from=email["from"],
            predicted_level=email["level"],
            actual_interest=actual_interest,
            feedback_type=feedback_type,
            notes=notes,
        )

        if success:
            rated_count += 1
            print("✅ Feedback recorded!")

            # Ask about email management
            gmail_id = email.get("gmail_id")
            action = get_email_action()
            if action != "skip":
                if gmail_id:
                    handle_email_action(gmail_id, action)
                else:
                    print(
                        "⚠️  Cannot perform action - Gmail ID not available in this digest"
                    )
                    print("   (Regenerate digest to enable email management)")
        else:
            print("❌ Failed to record feedback")

        print()

        # Add separator between emails
        if i < len(emails):
            print("-" * 70)
            print()

    # Show summary
    show_summary(tracker, rated_count)

    # Mark digest as reviewed (even if user skipped all - they still went through it)
    mark_digest_reviewed(digest_path)


def show_email_with_analysis(email: dict, current: int, total: int):
    """Display email with full AI analysis"""
    print(f"📧 Email {current}/{total}")
    print("=" * 70)
    print()

    # Subject (bold and prominent)
    print(f"Subject: {email['subject']}")
    print(f"From:    {email['from']}")

    # Show forwarder if available (for security visibility)
    if email.get("forwarder"):
        print(f"Fwd by:  {email['forwarder']}")

    if email.get("date"):
        # Simplify date display
        date = email["date"]
        # Try to extract just the date part if it's RFC format
        if "," in date:
            date = date.split(",", 1)[1].strip().split(" +")[0]
        print(f"Date:    {date}")

    print()
    print("-" * 70)
    print()

    # AI Prediction (prominent)
    level = email["level"].upper()
    level_emoji = {"URGENT": "🚨", "HIGH": "⭐", "MEDIUM": "📊", "LOW": "📉"}.get(
        level, "📧"
    )

    print(f"{level_emoji} AI PREDICTION: {level}")

    category = email.get("category", "unknown")
    confidence = email.get("confidence", "unknown").strip(
        "* "
    )  # Remove stray asterisks
    print(f"   Category: {category}")
    print(f"   Confidence: {confidence}")
    print()

    # Show key points
    if email.get("bullets"):
        print("KEY POINTS:")
        for i, bullet in enumerate(email["bullets"], 1):
            # Clean up bullet text (remove leading/trailing asterisks and spaces)
            bullet_clean = bullet.strip("* ").strip()
            # Indent wrapped lines
            print(f"  {i}. {bullet_clean}")
        print()

    # Show AI reasoning
    if email.get("reasoning"):
        reasoning = email["reasoning"].strip("* ").strip()  # Remove stray asterisks
        print("AI REASONING:")
        print(f"  {reasoning}")
        print()

    print("=" * 70)
    print()


def get_rating():
    """Get rating from user"""
    print("Was this prediction accurate?")
    print("  [1] 👍 Correct - AI got it right")
    print("  [2] 👎 Wrong - Completely missed my interest level")
    print("  [3] ⬆️  Too low - Should have been higher priority")
    print("  [4] ⬇️  Too high - Should have been lower priority")
    print("  [s] Skip this email")
    print("  [q] Quit and save")
    print()

    while True:
        choice = input("Your rating (1-4, s, q): ").strip().lower()

        if choice == "q":
            return "quit"

        if choice == "s":
            return "skip"

        if choice not in ["1", "2", "3", "4"]:
            print("❌ Invalid choice. Please enter 1-4, s, or q.")
            continue

        # Map choice to feedback type and actual interest
        feedback_map = {
            "1": ("thumbs_up", "useful"),
            "2": ("thumbs_down", "not_interesting"),
            "3": ("escalate", "more_important"),
            "4": ("downgrade", "less_important"),
        }

        return feedback_map[choice]


def get_email_action():
    """Ask what to do with the email in Gmail"""
    print()
    print("What do you want to do with this email in Gmail?")
    print("  [a] Archive (mark as read, remove from inbox)")
    print("  [k] Keep in inbox (leave as-is)")
    print("  [t] Trash (move to trash, auto-delete in 30 days)")
    print("  [Enter] Skip (don't change)")
    print()

    while True:
        choice = input("Action (a/k/t/Enter): ").strip().lower()

        if choice == "" or choice == "enter":
            return "skip"

        if choice in ["a", "k", "t"]:
            return choice

        print("❌ Invalid choice. Please enter a, k, t, or just press Enter.")


def handle_email_action(gmail_id: str, action: str):
    """Perform action on Gmail email"""
    try:
        from apis.gmail_client import GmailClient

        gmail = GmailClient()

        if action == "a":
            # Archive = mark as read + remove inbox label
            success = gmail.archive_message(gmail_id)
            if success:
                print("📬 Email archived (removed from inbox)")
            else:
                print("⚠️  Failed to archive email")

        elif action == "k":
            print("📧 Email kept in inbox")

        elif action == "t":
            print(f"🗑️  Moving email to trash (ID: {gmail_id})...")
            success = gmail.trash_message(gmail_id)
            if success:
                print("✅ Email moved to trash")
                print(
                    "   (Will auto-delete in 30 days, or restore from trash if needed)"
                )
            else:
                print("⚠️  Failed to trash email - check errors above")

    except Exception as e:
        print(f"⚠️  Could not perform action: {str(e)}")
        import traceback

        traceback.print_exc()


def parse_digest_with_content(digest_path: str) -> list:
    """
    Parse digest markdown file to extract emails with full content

    Args:
        digest_path: Path to digest markdown file

    Returns:
        List of email dicts with subject, from, level, bullets, reasoning
    """
    emails = []
    current_level = None
    current_email = {}
    in_key_points = False

    try:
        with open(digest_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            line_stripped = line.strip()

            # Detect section headers
            if line_stripped.startswith("## 🚨 URGENT"):
                current_level = "urgent"
            elif line_stripped.startswith("## ⭐ HIGH INTEREST"):
                current_level = "high"
            elif line_stripped.startswith("## 📊 MEDIUM INTEREST"):
                current_level = "medium"
            elif line_stripped.startswith("## 📉 LOW INTEREST"):
                current_level = "low"

            # Email subject (### header)
            elif line_stripped.startswith("### ") and current_level:
                # Save previous email if exists
                if current_email.get("subject"):
                    emails.append(current_email.copy())

                # Start new email
                current_email = {
                    "subject": line_stripped[4:],
                    "level": current_level,
                    "from": "",
                    "date": "",
                    "category": "",
                    "confidence": "",
                    "bullets": [],
                    "reasoning": "",
                    "gmail_id": "",
                }
                in_key_points = False

            # Gmail ID comment
            elif line_stripped.startswith("<!-- gmail_id:") and current_email:
                gmail_id = (
                    line_stripped.replace("<!-- gmail_id:", "")
                    .replace("-->", "")
                    .strip()
                )
                current_email["gmail_id"] = gmail_id

            # From line (original sender)
            elif line_stripped.startswith("**From:**") and current_email:
                from_text = line_stripped[10:].strip()
                if "|" in from_text:
                    from_text = from_text.split("|")[0].strip()
                current_email["from"] = from_text

            # Forwarded by line
            elif line_stripped.startswith("**Forwarded by:**") and current_email:
                forwarder = line_stripped[18:].strip()
                current_email["forwarder"] = forwarder

            # Date line
            elif line_stripped.startswith("**Date:**") and current_email:
                current_email["date"] = line_stripped[10:].strip()

            # Category line
            elif line_stripped.startswith("**Category:**") and current_email:
                parts = line_stripped[14:].split("|")
                if parts:
                    current_email["category"] = parts[0].strip()
                if len(parts) > 1 and "Confidence:" in parts[1]:
                    current_email["confidence"] = parts[1].split(":")[1].strip()

            # Key points section
            elif line_stripped.startswith("**Key Points:**"):
                in_key_points = True

            # Bullet point
            elif line_stripped.startswith("- ") and in_key_points and current_email:
                bullet_text = line_stripped[2:]
                current_email["bullets"].append(bullet_text)

            # Summary (for low interest)
            elif line_stripped.startswith("**Summary:**") and current_email:
                summary = line_stripped[13:].strip()
                current_email["bullets"].append(summary)

            # AI Analysis / Why low priority
            elif (
                line_stripped.startswith("**AI Analysis:**")
                or line_stripped.startswith("**Why low priority:**")
            ) and current_email:
                reasoning = (
                    line_stripped.split(":", 1)[1].strip()
                    if ":" in line_stripped
                    else ""
                )
                current_email["reasoning"] = reasoning

        # Add last email
        if current_email.get("subject"):
            emails.append(current_email)

    except Exception as e:
        print(f"❌ Error parsing digest: {str(e)}")
        import traceback

        traceback.print_exc()

    return emails


def mark_digest_reviewed(digest_path: str):
    """Move digest to reviewed folder after interactive review"""
    try:
        import shutil

        # Create reviewed directory
        reviewed_dir = "local_data/email_digests/reviewed"
        os.makedirs(reviewed_dir, exist_ok=True)

        # Move digest to reviewed folder
        filename = os.path.basename(digest_path)
        new_path = os.path.join(reviewed_dir, filename)

        shutil.move(digest_path, new_path)

        print("\n" + "=" * 70)
        print("✅ DIGEST MARKED AS REVIEWED")
        print("=" * 70)
        print()
        print(f"📂 Moved to: {reviewed_dir}/")
        print(f"📝 File: {filename}")
        print()
        print("💡 Next time you review (option 6), you'll get the latest unreviewed digest!")
        print()

    except Exception as e:
        print(f"\n⚠️  Could not move digest: {str(e)}")
        print("   (Digest remains in original location)")


def show_summary(tracker: EmailFeedbackTracker, rated_count: int):
    """Show rating summary and learning insights"""
    print("\n" + "=" * 70)
    print("📊 RATING SUMMARY")
    print("=" * 70)
    print()

    if rated_count == 0:
        print("No ratings provided this session.")
        return

    print(f"✅ You rated {rated_count} email(s) this session")
    print()

    # Get learning insights
    insights = tracker.get_learning_insights()
    stats = insights.get("stats", {})

    print("📈 OVERALL LEARNING PROGRESS:")
    print(
        f"  • Total feedback collected: {stats.get('total_feedback_count', 0)} emails"
    )
    print(f"  • Current accuracy: {stats.get('current_accuracy', 0)}%")
    print()

    # Show recommendations
    recommendations = insights.get("recommendations", [])
    if recommendations:
        print("💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  {rec}")
        print()

    print("🎯 The more feedback you provide, the better the AI becomes!")
    print()


def main():
    """CLI entry point"""
    import sys

    digest_path = None
    if len(sys.argv) > 1:
        digest_path = sys.argv[1]

    try:
        review_digest_interactive(digest_path)
    except KeyboardInterrupt:
        print("\n\n❌ Review cancelled")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
