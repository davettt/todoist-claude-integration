#!/usr/bin/env python3
"""
Email Processing CLI Script
Simple interface to process forwarded emails from Gmail
"""

from email_processor import EmailProcessor


def main():
    """Main CLI entry point"""
    print("\n" + "=" * 60)
    print("📧 EMAIL PROCESSING SYSTEM")
    print("=" * 60)
    print()
    print("This will process unread emails from your Gmail assistant inbox")
    print("and create operation files for Todoist task creation.")
    print()

    try:
        # Initialize processor
        processor = EmailProcessor()

        # Show current stats
        stats = processor.get_interaction_stats()
        if stats['total_emails'] > 0:
            print(f"📊 Previous Activity:")
            print(f"   • {stats['total_emails']} emails processed total")
            print(f"   • {stats['unique_senders']} unique senders")
            print()

        # Process emails
        print("🔄 Processing unread emails...")
        print()

        results = processor.process_new_emails(max_emails=10, mark_as_read=True)

        if results:
            print()
            print("=" * 60)
            print(f"✅ SUCCESS: Processed {len(results)} email(s)")
            print("=" * 60)
            print()
            print("📋 Created operation files:")
            for result in results:
                print(f"   • {result['operation_file']}")
                print(f"     From: {result['from']['name']}")
                print(f"     Subject: {result['subject']}")
                print()

            print("📝 Next Steps:")
            print("   1. Review the operation files above")
            print("   2. Run: python3 daily_manager.py")
            print("   3. Select option 3 to apply changes to Todoist")
            print()

        else:
            print()
            print("=" * 60)
            print("📭 No new emails to process")
            print("=" * 60)
            print()

    except ValueError as e:
        print()
        print("❌ Setup Error:")
        print(f"   {str(e)}")
        print()
        print("📝 Setup Instructions:")
        print("   1. Ensure Gmail API is enabled in Google Cloud Console")
        print("   2. Download OAuth credentials")
        print("   3. Save as: local_data/gmail_credentials.json")
        print("   4. Re-run this script to authenticate")
        print()

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
