#!/usr/bin/env python3
"""
Email Processing Pipeline
Coordinates Gmail API, sanitization, and operation file creation
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.gmail_client import GmailClient
from utils.email_sanitizer import (
    sanitize_email_content,
    html_to_text,
    extract_sender_info,
    is_content_safe,
    get_sanitization_summary
)
from utils.file_manager import archive_processed_file


class EmailProcessor:
    """Main email processing coordinator"""

    def __init__(self):
        self.gmail_client = None
        self.interactions_log_path = 'local_data/personal_data/email_interactions_log.json'
        self.pending_operations_dir = 'local_data/pending_operations'
        self.interactions = []
        self._ensure_data_directory()
        self._load_interactions_log()

    def _ensure_data_directory(self):
        """Create necessary directories if they don't exist"""
        os.makedirs('local_data/personal_data', exist_ok=True)
        os.makedirs(self.pending_operations_dir, exist_ok=True)

    def _load_interactions_log(self):
        """Load existing email interactions log"""
        if os.path.exists(self.interactions_log_path):
            try:
                with open(self.interactions_log_path, 'r') as f:
                    self.interactions = json.load(f)
                print(f"📋 Loaded {len(self.interactions)} previous interactions")
            except json.JSONDecodeError:
                print("⚠️ Interactions log corrupted, starting fresh")
                self.interactions = []
        else:
            self.interactions = []

    def _save_interactions_log(self):
        """Save email interactions log"""
        try:
            with open(self.interactions_log_path, 'w') as f:
                json.dump(self.interactions, f, indent=2)
            print(f"💾 Saved interactions log ({len(self.interactions)} total)")
        except Exception as e:
            print(f"❌ Error saving interactions log: {str(e)}")

    def _initialize_gmail(self):
        """Initialize Gmail client (lazy loading)"""
        if not self.gmail_client:
            try:
                self.gmail_client = GmailClient()
                print("✅ Gmail client initialized")
            except ValueError as e:
                print(f"❌ Gmail initialization failed: {str(e)}")
                raise

    def process_new_emails(self, max_emails: int = 10, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """
        Main entry point: Process unread emails from Gmail

        Args:
            max_emails: Maximum number of emails to process
            mark_as_read: If True, mark emails as read after processing (default: True)

        Returns:
            List of processing results
        """
        print("\n" + "=" * 60)
        print("📧 EMAIL PROCESSING PIPELINE")
        print("=" * 60)
        print()

        # Initialize Gmail client
        self._initialize_gmail()

        # Fetch unread messages
        print("🔍 Fetching unread messages...")
        messages = self.gmail_client.get_unread_messages(max_results=max_emails)

        if not messages:
            print("📭 No unread messages found")
            return []

        print(f"📨 Found {len(messages)} unread message(s)")
        print()

        results = []

        for i, message in enumerate(messages, 1):
            print(f"Processing {i}/{len(messages)}: {message['id'][:10]}...")
            print("-" * 40)

            result = self._process_single_email(message, mark_as_read)

            if result:
                results.append(result)

            print()

        print("=" * 60)
        print(f"✅ Processing complete: {len(results)} email(s) processed")
        print("=" * 60)

        return results

    def _process_single_email(self, message: Dict[str, Any], mark_as_read: bool = True) -> Optional[Dict[str, Any]]:
        """
        Process a single email through the pipeline

        Args:
            message: Message metadata from Gmail
            mark_as_read: Whether to mark as read after processing

        Returns:
            Processing result dict or None if failed
        """
        try:
            # 1. Get full message details
            details = self.gmail_client.get_message_details(message['id'])
            if not details:
                print("❌ Failed to fetch message details")
                return None

            # 2. Extract metadata
            headers = details['headers']
            from_header = headers.get('from', 'Unknown <unknown@unknown.com>')
            subject = headers.get('subject', '(No Subject)')
            date_str = headers.get('date', datetime.now().isoformat())

            sender_info = extract_sender_info(from_header)

            print(f"📬 From: {sender_info['name']} <{sender_info['email']}>")
            print(f"📋 Subject: {subject}")

            # 3. Get email body
            body = details['body']

            # If body looks like HTML, convert to text
            if body and ('<html' in body.lower() or '<div' in body.lower()):
                print("🔄 Converting HTML to text...")
                body = html_to_text(body)

            if not body or len(body.strip()) < 10:
                print("⚠️ Email body too short or empty, skipping")
                return None

            # 4. CRITICAL: Sanitize content
            print("🔒 Sanitizing content (removing URLs and emails)...")
            sanitized_body = sanitize_email_content(body)

            # Get sanitization summary
            sanitization_summary = get_sanitization_summary(body, sanitized_body)
            print(f"   • URLs removed: {sanitization_summary['urls_removed']}")
            print(f"   • Emails removed: {sanitization_summary['emails_removed']}")
            print(f"   • Safe: {'✅' if sanitization_summary['is_safe'] else '❌'}")

            # Verify safety
            if not is_content_safe(sanitized_body):
                print("❌ Content sanitization failed - unsafe content detected!")
                return None

            # 5. Create operation file (would normally send to Claude, but for now just create template)
            print("📝 Creating operation file...")
            operation_file = self._create_operation_file(
                sender_info=sender_info,
                subject=subject,
                date=date_str,
                sanitized_body=sanitized_body
            )

            # 6. Log interaction
            interaction = {
                "email_id": message['id'],
                "date_received": date_str,
                "from_address": sender_info['email'],
                "from_name": sender_info['name'],
                "subject": subject,
                "processed_date": datetime.now().isoformat(),
                "operation_file": operation_file,
                "sanitization_summary": sanitization_summary,
                "status": "processed"
            }

            self.interactions.append(interaction)
            self._save_interactions_log()

            # 7. Mark as read (or delete based on configuration)
            if mark_as_read:
                self.gmail_client.mark_as_read(message['id'])
                print("✅ Marked as read")

            print(f"✅ Created: {operation_file}")

            return {
                'message_id': message['id'],
                'from': sender_info,
                'subject': subject,
                'operation_file': operation_file
            }

        except Exception as e:
            print(f"❌ Error processing email: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _create_operation_file(self, sender_info: Dict[str, str], subject: str,
                               date: str, sanitized_body: str) -> str:
        """
        Create operation file with sanitized email content

        This file will be processed by Claude or manually reviewed

        Args:
            sender_info: Dict with 'name' and 'email'
            subject: Email subject
            date: Email date
            sanitized_body: Sanitized email body (URLs/emails removed)

        Returns:
            Filename of created operation file
        """
        # Create operation data structure
        operation = {
            "operation_type": f"Email from {sender_info['name']}",
            "generated_at": datetime.now().isoformat(),
            "source": "email_processor",
            "email_metadata": {
                "from_name": sender_info['name'],
                "from_email": sender_info['email'],
                "subject": subject,
                "date": date
            },
            "sanitized_content": sanitized_body,
            "instructions": {
                "for_claude": "Extract action items as tasks and meeting requests as calendar events",
                "security_note": "Content has been sanitized - all URLs and email addresses removed"
            },
            "new_tasks": [],
            "calendar_events": [],
            "notes": "This file requires manual review or Claude processing to extract tasks/events"
        }

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_'))[:30]
        safe_subject = safe_subject.replace(' ', '_')

        filename = f"tasks_email_{safe_subject}_{timestamp}.json"
        filepath = os.path.join(self.pending_operations_dir, filename)

        # Save file to pending_operations directory
        with open(filepath, 'w') as f:
            json.dump(operation, f, indent=2)

        return filename

    def get_interaction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about processed emails

        Returns:
            Dict with interaction statistics
        """
        if not self.interactions:
            return {
                'total_emails': 0,
                'unique_senders': 0,
                'date_range': None
            }

        # Get unique senders
        unique_senders = set(interaction['from_address'] for interaction in self.interactions)

        # Get date range
        dates = [interaction['processed_date'] for interaction in self.interactions]
        dates.sort()

        return {
            'total_emails': len(self.interactions),
            'unique_senders': len(unique_senders),
            'senders': list(unique_senders),
            'first_processed': dates[0] if dates else None,
            'last_processed': dates[-1] if dates else None
        }


def main():
    """CLI entry point for testing"""
    print("📧 Email Processor Test")
    print("=" * 40)

    processor = EmailProcessor()

    # Show stats
    stats = processor.get_interaction_stats()
    print(f"\n📊 Email Statistics:")
    print(f"   • Total processed: {stats['total_emails']}")
    print(f"   • Unique senders: {stats['unique_senders']}")

    if stats['total_emails'] > 0:
        print(f"   • First: {stats['first_processed']}")
        print(f"   • Last: {stats['last_processed']}")

    print()

    # Process new emails
    try:
        results = processor.process_new_emails(max_emails=5)

        if results:
            print(f"\n✅ Processed {len(results)} new email(s)")
        else:
            print("\n📭 No new emails to process")

    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
