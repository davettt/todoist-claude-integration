#!/usr/bin/env python3
"""
Biweekly Email Digest Generator
Processes emails from Gmail assistant inbox and generates AI-powered digest
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.gmail_client import GmailClient
from utils.email_digest_generator import EmailDigestGenerator
from utils.email_sanitizer import extract_sender_info
from utils.forwarded_email_parser import extract_original_sender


def has_task_marker(subject: str) -> bool:
    """
    Check if email subject has task marker

    Args:
        subject: Email subject line

    Returns:
        True if has [TASK] or #task marker
    """
    subject_lower = subject.lower()
    return "[task]" in subject_lower or "#task" in subject_lower


def fetch_digest_emails(days_back: int = 14) -> list:
    """
    Fetch emails from Gmail for digest generation

    Args:
        days_back: Number of days to look back for emails

    Returns:
        List of email dicts suitable for digest processing
    """
    try:
        print("🔄 Connecting to Gmail...")
        gmail_client = GmailClient()

        print(f"📧 Fetching emails from last {days_back} days...")
        # Try to get unread messages first
        messages = gmail_client.get_unread_messages(max_results=200)

        # If no unread messages, try recent messages (includes read emails)
        if not messages:
            print("   No unread emails found, fetching recent emails instead...")
            messages = gmail_client.get_recent_messages(max_results=200)

        if not messages:
            print("📭 No emails found")
            return []

        print(f"   Found {len(messages)} messages")
        print()

        # Process each message
        digest_emails = []
        task_email_count = 0

        for message in messages:
            details = gmail_client.get_message_details(message["id"])
            if not details:
                continue

            # Extract metadata
            headers = details["headers"]
            subject = headers.get("subject", "(No Subject)")
            from_header = headers.get("from", "Unknown")
            date = headers.get("date", "")

            # Skip task emails
            if has_task_marker(subject):
                task_email_count += 1
                continue

            # Parse forwarder (who sent to Gmail inbox)
            forwarder_info = extract_sender_info(from_header)
            forwarder = f"{forwarder_info['name']} <{forwarder_info['email']}>"

            # Try to extract original sender from forwarded email body
            original_sender = extract_original_sender(details["body"])

            # Add to digest list
            digest_emails.append(
                {
                    "id": details["id"],
                    "subject": subject,
                    "forwarder": forwarder,
                    "forwarder_email": forwarder_info["email"],
                    "original_sender": original_sender,
                    "date": date,
                    "body": details["body"],
                }
            )

        print(f"✅ Collected {len(digest_emails)} emails for digest")
        print(
            f"   Skipped {task_email_count} task emails (have [TASK] or #task marker)"
        )
        print()

        return digest_emails

    except ValueError as e:
        print(f"❌ Gmail connection failed: {str(e)}")
        print()
        print("📝 Setup Instructions:")
        print("   1. Ensure Gmail API is enabled")
        print("   2. Download OAuth credentials as gmail_credentials.json")
        print("   3. Re-run this script to authenticate")
        print()
        return []

    except Exception as e:
        print(f"❌ Error fetching emails: {str(e)}")
        return []


def main():
    """Main entry point for digest generation"""
    print("\n" + "=" * 70)
    print("📧 BIWEEKLY EMAIL DIGEST GENERATOR")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Fetch unread emails from Gmail assistant inbox")
    print("  2. Skip emails with [TASK] or #task markers")
    print("  3. Use Claude AI to analyze remaining emails")
    print("  4. Generate markdown digest with interest predictions")
    print()

    # Get date range
    days_back = 14
    print(f"📅 Processing emails from last {days_back} days")
    print()

    # Fetch emails
    emails = fetch_digest_emails(days_back)

    if not emails:
        print("=" * 70)
        print("📭 NO EMAILS TO PROCESS")
        print("=" * 70)
        print()
        print("Possible reasons:")
        print("  • No unread emails in Gmail assistant inbox")
        print("  • All emails have [TASK] or #task markers")
        print("  • Auto-forwarding not configured")
        print()
        print("💡 Next steps:")
        print("  1. Forward some newsletter emails to your Gmail assistant")
        print("  2. Ensure they DON'T have [TASK] or #task in subject")
        print("  3. Run this script again")
        print()
        return

    # Generate digest
    try:
        print("🤖 Initializing AI digest generator...")
        generator = EmailDigestGenerator()

        digest_path = generator.generate_digest(emails, date_range_days=days_back)

        if digest_path:
            print()
            print("=" * 70)
            print("✅ DIGEST GENERATED SUCCESSFULLY")
            print("=" * 70)
            print()
            print(f"📄 Digest saved: {os.path.basename(digest_path)}")
            print()

            # Automatically mark emails as read
            if emails:
                print("📧 Email Management:")
                print(f"   Marking {len(emails)} emails as read in Gmail...")

                gmail_client = GmailClient()
                marked_count = 0

                for email in emails:
                    try:
                        gmail_client.mark_as_read(email["id"])
                        marked_count += 1
                    except Exception:
                        print(f"   ⚠️  Failed to mark {email['subject'][:40]}...")

                print(f"   ✅ Marked {marked_count}/{len(emails)} emails as read")
                print()

            print("📝 Next steps:")
            print("  • Return to daily manager")
            print("  • Choose option 6 to review digest interactively")
            print("  • Rate each email to help AI learn your preferences")
            print()
            print("💡 Tip: Interactive review lets you read, rate, and")
            print("   archive/delete emails all in one seamless flow!")
            print()

        else:
            print()
            print("=" * 70)
            print("❌ DIGEST GENERATION FAILED")
            print("=" * 70)
            print()
            print("Please check the error messages above.")
            print()

    except ValueError as e:
        print()
        print("=" * 70)
        print("❌ SETUP ERROR")
        print("=" * 70)
        print()
        print(str(e))
        print()
        print("📝 Setup Instructions:")
        print("  1. Get Anthropic API key from: https://console.anthropic.com/")
        print("  2. Add to .env file: ANTHROPIC_API_KEY=your-key-here")
        print(
            "  3. Configure interests in: local_data/personal_data/email_interest_profile.json"
        )
        print("  4. Re-run this script")
        print()

    except Exception as e:
        print()
        print(f"❌ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
