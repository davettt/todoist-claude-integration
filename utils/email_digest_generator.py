"""
Email Digest Generator
Creates markdown digests from analyzed emails with AI-powered interest predictions
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from utils.adaptive_ai_context import AdaptiveAIContext
from utils.claude_api_client import ClaudeAPIClient
from utils.email_sanitizer import sanitize_email_content
from utils.learning_engine import LearningEngine


class EmailDigestGenerator:
    """Generates AI-powered email digests"""

    def __init__(self):
        """Initialize digest generator"""
        self.claude_client = None
        self.digest_dir = "local_data/email_digests"
        self.profile_path = "local_data/personal_data/email_interest_profile.json"
        self.user_profile = self._load_user_profile()

        # Initialize learning components
        self.learning_engine = None
        self.adaptive_context = None
        self.learning_context = None
        self._init_learning()

        # Store analyzed emails for post-processing
        self.analyzed_emails = []

        # Ensure directory exists
        os.makedirs(self.digest_dir, exist_ok=True)

    def _init_learning(self):
        """Initialize learning engine and adaptive context"""
        try:
            self.learning_engine = LearningEngine()
            self.adaptive_context = AdaptiveAIContext()
            self.learning_context = self.learning_engine.get_adaptive_context()
        except Exception:
            # Learning initialization failed, continue without it
            self.learning_context = {"status": "unavailable"}

    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user's interest profile"""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load interest profile: {str(e)}")
                return self._get_default_profile()
        else:
            print("⚠️  Interest profile not found, using defaults")
            return self._get_default_profile()

    def _get_default_profile(self) -> Dict[str, Any]:
        """Get default interest profile"""
        return {
            "core_interests": [],
            "active_projects": [],
            "trusted_senders": [],
            "urgency_keywords": [
                "security alert",
                "suspicious activity",
                "unauthorized",
                "payment failed",
                "subscription ending",
                "account suspended",
            ],
            "auto_skip_keywords": ["sale", "discount", "limited time", "offer expires"],
            "digest_settings": {
                "max_emails_per_digest": 100,
                "auto_archive_low_interest": False,
                "auto_label_low_interest": True,
            },
        }

    def _is_trusted_sender(self, email_address: str) -> bool:
        """
        Check if email address is from a trusted original sender

        Args:
            email_address: Email address to check

        Returns:
            True if trusted, False otherwise
        """
        trusted_senders = self.user_profile.get("trusted_senders", [])

        if not trusted_senders:
            return False

        email_lower = email_address.lower()

        for trusted in trusted_senders:
            trusted_lower = trusted.lower()

            # Exact match
            if email_lower == trusted_lower:
                return True

            # Domain match (e.g., "jamesclear.com" matches "james@jamesclear.com")
            if "@" not in trusted_lower and trusted_lower in email_lower:
                return True

        return False

    def _is_trusted_forwarder(self, email_address: str) -> bool:
        """
        Check if forwarder is one of user's own email addresses (security check)

        Args:
            email_address: Forwarder email address to check

        Returns:
            True if from user's own accounts, False otherwise
        """
        trusted_forwarders = self.user_profile.get("trusted_forwarders", [])

        if not trusted_forwarders:
            # If not configured, show warning but allow (for backwards compatibility)
            return True

        email_lower = email_address.lower()

        for trusted in trusted_forwarders:
            if email_lower == trusted.lower():
                return True

        return False

    def _initialize_claude(self):
        """Lazy load Claude API client"""
        if not self.claude_client:
            try:
                self.claude_client = ClaudeAPIClient()
            except ValueError as e:
                raise ValueError(f"Claude API initialization failed: {str(e)}")

    def generate_digest(
        self, emails: List[Dict[str, Any]], date_range_days: int = 14
    ) -> Optional[str]:
        """
        Generate markdown digest from emails

        Args:
            emails: List of email dicts with 'subject', 'from', 'body', 'date' keys
            date_range_days: Number of days covered by this digest

        Returns:
            Path to generated markdown file, or None if failed
        """
        if not emails:
            print("📭 No emails to process for digest")
            return None

        print(f"\n{'='*60}")
        print("📧 EMAIL DIGEST GENERATION")
        print(f"{'='*60}")
        print(f"Emails to analyze: {len(emails)}")
        print()

        # Initialize Claude API
        try:
            self._initialize_claude()
        except ValueError as e:
            print(str(e))
            return None

        # Show cost estimate
        cost_estimate = self.claude_client.estimate_cost(len(emails))
        print("💰 Cost Estimate:")
        print(f"   Emails: {cost_estimate['email_count']}")
        print(f"   Estimated cost: ${cost_estimate['estimated_total_cost']:.2f}")
        print()

        # Warn if expensive
        if cost_estimate["estimated_total_cost"] > 1.00:
            print(
                f"⚠️  This digest will cost approximately ${cost_estimate['estimated_total_cost']:.2f}"
            )
            confirm = input("   Continue? (y/n): ").strip().lower()
            if confirm != "y":
                print("❌ Digest generation cancelled")
                return None
            print()

        # Show learning info if available
        if self.learning_context and self.learning_context.get("status") == "ready":
            print("🤖 Analyzing emails with your learning profile...")
            print()

            # Show what learning adjustments are being applied
            adjustments = self.learning_context.get("learning_adjustments", {})
            if adjustments:
                print("   📈 Learning adjustments being applied:")
                if adjustments.get("use_learned_sender_preferences"):
                    print("     • Using learned sender preferences")
                if adjustments.get("emphasize_strongest_areas"):
                    print("     • Emphasizing your strongest areas")
                if adjustments.get("apply_confidence_adjustments"):
                    print("     • Applying confidence-based adjustments")

                # Show strongest areas
                strongest = self.learning_context.get("learned_preferences", {}).get(
                    "strongest_areas", []
                )
                if strongest:
                    print(f"     • Strong match for: {', '.join(strongest[:2])}")

                print()
        else:
            print("🔍 Analyzing emails with Claude AI...")
            print()

        analyzed_emails = []
        for i, email in enumerate(emails, 1):
            print(
                f"   [{i}/{len(emails)}] {email.get('subject', 'No subject')[:50]}..."
            )

            analysis = self._analyze_email(email)
            if analysis:
                analyzed_emails.append({"email": email, "analysis": analysis})

        print()
        print(f"✅ Analyzed {len(analyzed_emails)}/{len(emails)} emails")
        print()

        # Store analyzed emails for post-processing
        self.analyzed_emails = analyzed_emails

        # Generate markdown
        print("📝 Generating markdown digest...")
        markdown_path = self._create_markdown_digest(analyzed_emails, date_range_days)

        if markdown_path:
            print(f"✅ Digest created: {markdown_path}")
            return markdown_path
        else:
            print("❌ Failed to create digest")
            return None

    def auto_handle_low_interest_emails(self) -> Dict[str, int]:
        """
        Automatically mark LOW-rated emails as read and add 'low_interest' label
        Based on profile setting: digest_settings.auto_label_low_interest

        Returns:
            Dict with counts of processed and failed emails
        """
        from apis.gmail_client import GmailClient

        # Check if feature is enabled
        auto_label_enabled = self.user_profile.get("digest_settings", {}).get(
            "auto_label_low_interest", False
        )

        if not auto_label_enabled:
            return {"processed": 0, "failed": 0, "skipped_disabled": True}

        # Get LOW-rated emails
        low_interest_emails = [
            item
            for item in self.analyzed_emails
            if item["analysis"].get("level") == "low"
        ]

        if not low_interest_emails:
            return {"processed": 0, "failed": 0, "skipped_no_low": True}

        print()
        print("📋 Auto-handling LOW-interest emails:")
        print(f"   Found {len(low_interest_emails)} LOW-rated emails")
        print("   Marking as read + adding 'low_interest' label...")

        # Initialize Gmail client
        gmail_client = GmailClient()

        processed_count = 0
        failed_count = 0

        for item in low_interest_emails:
            email = item["email"]
            email_id = email.get("id")
            subject = email.get("subject", "No subject")[:40]

            if not email_id:
                print(f"   ⚠️  No ID for email: {subject}")
                failed_count += 1
                continue

            try:
                success = gmail_client.mark_as_read_and_label_low_interest(email_id)
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                    print(f"   ⚠️  Failed to process: {subject}")
            except Exception as e:
                print(f"   ⚠️  Error processing {subject}: {str(e)}")
                failed_count += 1

        print(
            f"   ✅ Processed {processed_count}/{len(low_interest_emails)} LOW-rated emails"
        )
        if failed_count > 0:
            print(f"   ⚠️  Failed: {failed_count}")
        print()

        return {
            "processed": processed_count,
            "failed": failed_count,
            "total_low": len(low_interest_emails),
        }

    def _analyze_email(self, email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze single email with Claude API"""
        try:
            # Sanitize content before sending to API
            body = email.get("body", "")
            sanitized_body = sanitize_email_content(body)

            # Determine display sender (original if available, otherwise forwarder)
            original_sender = email.get("original_sender")
            forwarder = email.get("forwarder", "Unknown")
            forwarder_email = email.get("forwarder_email", "")

            # Security check: Verify forwarder is from user's accounts
            is_from_user = self._is_trusted_forwarder(forwarder_email)

            if not is_from_user:
                print(
                    f"      ⚠️  WARNING: Email not from your accounts! Forwarder: {forwarder_email}"
                )
                # Could skip analysis or mark as suspicious
                # For now, we'll continue but flag it

            if original_sender:
                email_from = f"{original_sender['name']} <{original_sender['email']}>"
                sender_email = original_sender["email"]
            else:
                email_from = forwarder
                sender_email = forwarder_email

            # Check if original sender is trusted (for priority ranking)
            is_trusted_sender = self._is_trusted_sender(sender_email)

            # Add both trust statuses to profile for this analysis
            analysis_profile = self.user_profile.copy()
            analysis_profile["current_sender_is_trusted"] = is_trusted_sender
            analysis_profile["forwarded_by_user"] = is_from_user

            # Analyze with Claude
            analysis = self.claude_client.analyze_email_interest(
                email_content=sanitized_body,
                email_subject=email.get("subject", ""),
                email_from=email_from,
                user_profile=analysis_profile,
            )

            return analysis

        except Exception as e:
            print(f"      ⚠️  Analysis failed: {str(e)}")
            return None

    def _create_markdown_digest(
        self, analyzed_emails: List[Dict[str, Any]], date_range_days: int
    ) -> Optional[str]:
        """Create markdown digest file"""
        try:
            # Group by interest level
            grouped = self._group_by_interest_level(analyzed_emails)

            # Generate markdown content
            markdown = self._generate_markdown_content(grouped, date_range_days)

            # Save to file
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"digest_{timestamp}.md"
            filepath = os.path.join(self.digest_dir, filename)

            with open(filepath, "w") as f:
                f.write(markdown)

            return filepath

        except Exception as e:
            print(f"❌ Error creating markdown: {str(e)}")
            return None

    def _group_by_interest_level(
        self, analyzed_emails: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group analyzed emails by interest level"""
        grouped = {"urgent": [], "high": [], "medium": [], "low": []}

        for item in analyzed_emails:
            level = item["analysis"].get("level", "medium")
            if level in grouped:
                grouped[level].append(item)
            else:
                grouped["medium"].append(item)  # Default to medium if invalid

        return grouped

    def _generate_markdown_content(
        self, grouped: Dict[str, List[Dict[str, Any]]], date_range_days: int
    ) -> str:
        """Generate markdown content for digest"""
        lines = []

        # Header
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range_days)

        lines.append("# Email Digest")
        lines.append(
            f"**Period:** {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        )
        lines.append(f"**Generated:** {end_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
        lines.append("")

        # Summary
        total_emails = sum(len(emails) for emails in grouped.values())
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- 📧 Total emails: {total_emails}")
        lines.append(f"- 🚨 Urgent: {len(grouped['urgent'])}")
        lines.append(f"- ⭐ High interest: {len(grouped['high'])}")
        lines.append(f"- 📊 Medium interest: {len(grouped['medium'])}")
        lines.append(f"- 📉 Low interest: {len(grouped['low'])}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Urgent section
        if grouped["urgent"]:
            lines.extend(
                self._generate_section(
                    "🚨 URGENT - Requires Immediate Attention",
                    grouped["urgent"],
                    show_reasoning=True,
                )
            )

        # High interest section
        if grouped["high"]:
            lines.extend(
                self._generate_section(
                    "⭐ HIGH INTEREST - Worth Reading",
                    grouped["high"],
                    show_reasoning=True,
                )
            )

        # Medium interest section
        if grouped["medium"]:
            lines.extend(
                self._generate_section(
                    "📊 MEDIUM INTEREST - May Be Useful",
                    grouped["medium"],
                    show_reasoning=True,  # Show reasoning to help user decide
                )
            )

        # Low interest section (condensed)
        if grouped["low"]:
            lines.extend(self._generate_low_interest_section(grouped["low"]))

        # Footer
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## How to Provide Feedback")
        lines.append("")
        lines.append("Help improve future digests by marking emails:")
        lines.append("- 👍 **Useful** - Good prediction, read and enjoyed")
        lines.append("- 👎 **Not Interesting** - Wrong prediction, not interesting")
        lines.append("- ⚠️ **More Important** - Should have been higher priority")
        lines.append("- ✅ **Less Important** - Should have been lower priority")
        lines.append("")
        lines.append("The AI learns from your feedback and improves over time!")
        lines.append("")

        return "\n".join(lines)

    def _generate_section(
        self, title: str, emails: List[Dict[str, Any]], show_reasoning: bool = True
    ) -> List[str]:
        """Generate markdown section for interest level"""
        lines = []

        lines.append(f"## {title}")
        lines.append("")

        for item in emails:
            email = item["email"]
            analysis = item["analysis"]

            # Email header
            subject = email.get("subject", "No subject")
            date = email.get("date", "")

            # Handle sender display (original sender if available, otherwise forwarder)
            original_sender = email.get("original_sender")
            forwarder = email.get("forwarder", "Unknown sender")

            lines.append(f"### {subject}")

            if original_sender:
                # Show original sender prominently, forwarder as secondary info
                original = f"{original_sender['name']} <{original_sender['email']}>"
                lines.append(f"**From:** {original}")
                lines.append(f"**Forwarded by:** {forwarder}")
            else:
                # Just show forwarder
                lines.append(f"**From:** {forwarder}")

            if date:
                lines.append(f"**Date:** {date}")

            # Add Gmail ID as HTML comment (invisible in rendering, parseable for actions)
            gmail_id = email.get("id", "")
            if gmail_id:
                lines.append(f"<!-- gmail_id: {gmail_id} -->")

            category = analysis.get("category", "other")
            confidence = analysis.get("confidence", "medium")
            lines.append(f"**Category:** {category} | **Confidence:** {confidence}")

            # Add technologies and topics if present
            technologies = analysis.get("technologies_mentioned", [])
            topics = analysis.get("topics_identified", [])
            if technologies:
                lines.append(f"**Technologies:** {', '.join(technologies)}")
            if topics:
                lines.append(f"**Topics:** {', '.join(topics)}")
            lines.append("")

            # Use new structured format if available, fall back to old format
            summary = analysis.get("summary")
            relevance = analysis.get("relevance")
            key_details = analysis.get("key_details", [])
            decision_point = analysis.get("decision_point")

            if summary:
                # New structured format
                lines.append("**📋 What's This About:**")
                lines.append(summary)
                lines.append("")

                if relevance:
                    lines.append("**🎯 Why It's Relevant:**")
                    lines.append(relevance)
                    lines.append("")

                if key_details:
                    lines.append("**💡 Key Details:**")
                    for detail in key_details:
                        lines.append(f"• {detail}")
                    lines.append("")

                if decision_point:
                    lines.append("**📧 Decision Point:**")
                    lines.append(
                        f"Worth reading if you want {decision_point.lower() if not decision_point[0].isupper() else decision_point}"
                    )
                    lines.append("")

            else:
                # Fallback to old bullet format for backward compatibility
                bullets = analysis.get("bullets", [])
                if bullets:
                    lines.append("**Key Points:**")
                    for bullet in bullets:
                        content = bullet.get("content", "")
                        reasoning = bullet.get("reasoning", "")

                        lines.append(f"- {content}")
                        if show_reasoning and reasoning:
                            lines.append(f"  - *Why: {reasoning}*")

                    lines.append("")

                # Overall reasoning
                if show_reasoning:
                    overall = analysis.get("overall_reasoning", "")
                    if overall:
                        lines.append(f"**AI Analysis:** {overall}")
                        lines.append("")

            lines.append("---")
            lines.append("")

        return lines

    def _generate_low_interest_section(self, emails: List[Dict[str, Any]]) -> List[str]:
        """Generate condensed section for low interest emails"""
        lines = []

        lines.append("## 📉 LOW INTEREST - Probably Skip")
        lines.append("")
        lines.append(
            "These emails likely don't match your interests. Brief summaries below:"
        )
        lines.append("")

        for item in emails:
            email = item["email"]
            analysis = item["analysis"]

            subject = email.get("subject", "No subject")
            category = analysis.get("category", "other")
            confidence = analysis.get("confidence", "medium")

            # Handle sender display
            original_sender = email.get("original_sender")
            forwarder = email.get("forwarder", "Unknown")

            # Show subject and from
            lines.append(f"### {subject}")

            if original_sender:
                from_display = f"{original_sender['name']} <{original_sender['email']}>"
            else:
                from_display = forwarder

            lines.append(
                f"**From:** {from_display} | **Category:** {category} | **Confidence:** {confidence}"
            )

            # Show forwarder if we have original sender (for security visibility)
            if original_sender and forwarder != "Unknown":
                lines.append(f"**Forwarded by:** {forwarder}")

            # Add technologies and topics if present
            technologies = analysis.get("technologies_mentioned", [])
            topics = analysis.get("topics_identified", [])
            if technologies:
                lines.append(f"**Technologies:** {', '.join(technologies)}")
            if topics:
                lines.append(f"**Topics:** {', '.join(topics)}")

            # Add Gmail ID as HTML comment
            gmail_id = email.get("id", "")
            if gmail_id:
                lines.append(f"<!-- gmail_id: {gmail_id} -->")

            lines.append("")

            # Use new structured format if available, fall back to old format
            summary = analysis.get("summary")
            relevance = analysis.get("relevance")

            if summary:
                # New structured format for LOW interest
                lines.append("**📋 Summary:**")
                lines.append(summary)
                lines.append("")

                if relevance:
                    lines.append("**🎯 Why Flagged Low:**")
                    lines.append(relevance)
                    lines.append("")
            else:
                # Fallback to old format
                bullets = analysis.get("bullets", [])
                if bullets:
                    if len(bullets) == 1:
                        # Single bullet: show as summary
                        lines.append(f"**Summary:** {bullets[0].get('content', '')}")
                    else:
                        # Multiple bullets: show as list
                        lines.append("**What's in it:**")
                        for bullet in bullets:
                            content = bullet.get("content", "")
                            if content:
                                lines.append(f"- {content}")
                    lines.append("")

                # Show overall reasoning (why it's low priority)
                overall = analysis.get("overall_reasoning", "")
                if overall:
                    lines.append(f"**Why low priority:** {overall}")
                    lines.append("")

            lines.append("---")
            lines.append("")

        return lines
