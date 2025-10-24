"""
Profile Manager for Email Interest Profile
Allows users to view and interactively manage their email preferences
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict


class ProfileManager:
    """Manage email interest profile interactively"""

    def __init__(
        self, profile_path: str = "local_data/personal_data/email_interest_profile.json"
    ):
        """Initialize profile manager with path to profile file"""
        self.profile_path = profile_path
        self.profile_dir = os.path.dirname(profile_path)
        self.profile = None
        self.load_profile()

    def load_profile(self) -> None:
        """Load profile from file, handle missing/corrupted files gracefully"""
        try:
            if not os.path.exists(self.profile_path):
                print(f"⚠️  Profile file not found: {self.profile_path}")
                print("Creating default profile...")
                self.profile = self._get_default_profile()
                self._save_profile()
                return

            with open(self.profile_path, "r") as f:
                self.profile = json.load(f)
                print("✅ Profile loaded successfully")

        except json.JSONDecodeError:
            print(f"⚠️  Profile file is corrupted: {self.profile_path}")
            print("Creating backup and default profile...")
            self._backup_profile()
            self.profile = self._get_default_profile()
            self._save_profile()

        except Exception as e:
            print(f"❌ Error loading profile: {str(e)}")
            self.profile = self._get_default_profile()

    def _get_default_profile(self) -> Dict[str, Any]:
        """Return default profile structure"""
        return {
            "core_interests": [],
            "active_projects": [],
            "trusted_forwarders": [],
            "trusted_senders": [],
            "urgency_keywords": [],
            "auto_skip_keywords": [],
            "digest_settings": {
                "max_emails_per_digest": 100,
                "schedule": "biweekly",
                "preferred_days": ["wednesday", "sunday"],
                "auto_archive_low_interest": False,
                "include_low_interest_summary": True,
            },
            "urgency_settings": {
                "notify_urgent_immediately": False,
                "trusted_senders_for_urgency": ["security@", "noreply@"],
            },
            "ai_settings": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens_per_email": 1500,
                "temperature": 0.3,
                "confidence_threshold": 0.7,
            },
        }

    def _save_profile(self) -> None:
        """Save profile to file"""
        try:
            os.makedirs(self.profile_dir, exist_ok=True)
            with open(self.profile_path, "w") as f:
                json.dump(self.profile, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving profile: {str(e)}")

    def _backup_profile(self) -> None:
        """Create backup of current profile"""
        try:
            if not os.path.exists(self.profile_path):
                return

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_path = self.profile_path.replace(
                ".json", f"_backup_{timestamp}.json"
            )

            with open(self.profile_path, "r") as src:
                with open(backup_path, "w") as dst:
                    dst.write(src.read())

            print(f"💾 Backup created: {backup_path}")

        except Exception as e:
            print(f"⚠️  Could not create backup: {str(e)}")

    def view_profile(self) -> None:
        """Display profile in human-readable format"""
        if not self.profile:
            print("❌ No profile loaded")
            return

        print("\n" + "=" * 60)
        print("📋 YOUR EMAIL INTEREST PROFILE")
        print("=" * 60)
        print()

        # Core interests
        interests = self.profile.get("core_interests", [])
        print("🎯 CORE INTERESTS:")
        if interests:
            for interest in interests:
                print(f"  • {interest}")
        else:
            print("  (none configured)")
        print()

        # Active projects
        projects = self.profile.get("active_projects", [])
        print("🚀 ACTIVE PROJECTS:")
        if projects:
            for project in projects:
                print(f"  • {project}")
        else:
            print("  (none configured)")
        print()

        # Trusted forwarders and senders counts
        forwarders = self.profile.get("trusted_forwarders", [])
        senders = self.profile.get("trusted_senders", [])

        print(f"🔒 TRUSTED FORWARDERS: {len(forwarders)} configured")
        if forwarders:
            for forwarder in forwarders:
                print(f"  • {forwarder}")
        print()

        print(f"📧 TRUSTED SENDERS: {len(senders)} configured")
        if senders:
            for sender in senders:
                print(f"  • {sender}")
        print()

        # Last modified
        try:
            mtime = os.path.getmtime(self.profile_path)
            mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %I:%M %p")
            print(f"📅 Last updated: {mod_time}")
        except Exception:
            print("📅 Last updated: Unknown")

        print()

    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        # Accept both email addresses and domain names
        if "@" in email:
            # Email format: something@domain.com
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        else:
            # Domain format: domain.com or subdomain@domain.com
            pattern = (
                r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$"
            )

        return re.match(pattern, email) is not None

    def add_core_interests(self) -> None:
        """Add new core interests"""
        print("\n" + "-" * 60)
        print("Add Core Interests")
        print("-" * 60)
        print("Enter interests (comma-separated). E.g: 'AI, productivity, coding'")
        print()

        user_input = input("Enter interests (or press Enter to skip): ").strip()
        if not user_input:
            return

        new_interests = [i.strip() for i in user_input.split(",") if i.strip()]

        if not new_interests:
            print("❌ No interests provided")
            return

        self._backup_profile()

        current = self.profile.get("core_interests", [])
        added = []

        for interest in new_interests:
            if interest not in current:
                current.append(interest)
                added.append(interest)

        self.profile["core_interests"] = current
        self._save_profile()

        if added:
            print(f"\n✅ Added {len(added)} interest(s):")
            for interest in added:
                print(f"  • {interest}")
        else:
            print("\nℹ️  All interests already exist")

    def remove_core_interests(self) -> None:
        """Remove core interests"""
        current = self.profile.get("core_interests", [])

        if not current:
            print("\n❌ No core interests to remove")
            return

        print("\n" + "-" * 60)
        print("Remove Core Interests")
        print("-" * 60)
        print("Select interests to remove:")
        print()

        for i, interest in enumerate(current, 1):
            print(f"  {i}. {interest}")

        print()
        selection = input(
            "Enter numbers to remove (comma-separated), or Enter to skip: "
        ).strip()

        if not selection:
            return

        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            indices.sort(reverse=True)

            removed = []
            for idx in indices:
                if 0 <= idx < len(current):
                    removed.append(current.pop(idx))

            if removed:
                self._backup_profile()
                self.profile["core_interests"] = current
                self._save_profile()

                print(f"\n✅ Removed {len(removed)} interest(s):")
                for interest in removed:
                    print(f"  • {interest}")
            else:
                print("\n❌ Invalid selection")

        except ValueError:
            print("\n❌ Invalid input. Please enter numbers separated by commas.")

    def add_active_projects(self) -> None:
        """Add new active projects"""
        print("\n" + "-" * 60)
        print("Add Active Projects")
        print("-" * 60)
        print("Enter projects (comma-separated). E.g: 'Project A, Project B'")
        print()

        user_input = input("Enter projects (or press Enter to skip): ").strip()
        if not user_input:
            return

        new_projects = [p.strip() for p in user_input.split(",") if p.strip()]

        if not new_projects:
            print("❌ No projects provided")
            return

        self._backup_profile()

        current = self.profile.get("active_projects", [])
        added = []

        for project in new_projects:
            if project not in current:
                current.append(project)
                added.append(project)

        self.profile["active_projects"] = current
        self._save_profile()

        if added:
            print(f"\n✅ Added {len(added)} project(s):")
            for project in added:
                print(f"  • {project}")
        else:
            print("\nℹ️  All projects already exist")

    def remove_active_projects(self) -> None:
        """Remove active projects"""
        current = self.profile.get("active_projects", [])

        if not current:
            print("\n❌ No active projects to remove")
            return

        print("\n" + "-" * 60)
        print("Remove Active Projects")
        print("-" * 60)
        print("Select projects to remove:")
        print()

        for i, project in enumerate(current, 1):
            print(f"  {i}. {project}")

        print()
        selection = input(
            "Enter numbers to remove (comma-separated), or Enter to skip: "
        ).strip()

        if not selection:
            return

        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            indices.sort(reverse=True)

            removed = []
            for idx in indices:
                if 0 <= idx < len(current):
                    removed.append(current.pop(idx))

            if removed:
                self._backup_profile()
                self.profile["active_projects"] = current
                self._save_profile()

                print(f"\n✅ Removed {len(removed)} project(s):")
                for project in removed:
                    print(f"  • {project}")
            else:
                print("\n❌ Invalid selection")

        except ValueError:
            print("\n❌ Invalid input. Please enter numbers separated by commas.")

    def add_trusted_senders(self) -> None:
        """Add new trusted senders with email validation"""
        print("\n" + "-" * 60)
        print("Add Trusted Senders")
        print("-" * 60)
        print("Enter senders (comma-separated). Examples:")
        print("  • Email: james@example.com")
        print("  • Domain: example.com")
        print()

        user_input = input("Enter senders (or press Enter to skip): ").strip()
        if not user_input:
            return

        new_senders = [s.strip() for s in user_input.split(",") if s.strip()]

        if not new_senders:
            print("❌ No senders provided")
            return

        self._backup_profile()

        current = self.profile.get("trusted_senders", [])
        added = []
        invalid = []

        for sender in new_senders:
            if not self._validate_email(sender):
                invalid.append(sender)
            elif sender not in current:
                current.append(sender)
                added.append(sender)

        self.profile["trusted_senders"] = current
        self._save_profile()

        if added:
            print(f"\n✅ Added {len(added)} sender(s):")
            for sender in added:
                print(f"  • {sender}")

        if invalid:
            print(f"\n⚠️  Skipped {len(invalid)} invalid email(s):")
            for sender in invalid:
                print(f"  • {sender}")

    def remove_trusted_senders(self) -> None:
        """Remove trusted senders"""
        current = self.profile.get("trusted_senders", [])

        if not current:
            print("\n❌ No trusted senders to remove")
            return

        print("\n" + "-" * 60)
        print("Remove Trusted Senders")
        print("-" * 60)
        print("Select senders to remove:")
        print()

        for i, sender in enumerate(current, 1):
            print(f"  {i}. {sender}")

        print()
        selection = input(
            "Enter numbers to remove (comma-separated), or Enter to skip: "
        ).strip()

        if not selection:
            return

        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            indices.sort(reverse=True)

            removed = []
            for idx in indices:
                if 0 <= idx < len(current):
                    removed.append(current.pop(idx))

            if removed:
                self._backup_profile()
                self.profile["trusted_senders"] = current
                self._save_profile()

                print(f"\n✅ Removed {len(removed)} sender(s):")
                for sender in removed:
                    print(f"  • {sender}")
            else:
                print("\n❌ Invalid selection")

        except ValueError:
            print("\n❌ Invalid input. Please enter numbers separated by commas.")

    def reset_to_defaults(self) -> None:
        """Reset profile to defaults with confirmation"""
        print("\n" + "-" * 60)
        print("Reset Profile to Defaults")
        print("-" * 60)
        print("⚠️  This will DELETE all your custom settings!")
        print()

        confirm = (
            input("Type 'reset' to confirm, or press Enter to cancel: ").strip().lower()
        )

        if confirm != "reset":
            print("❌ Cancelled")
            return

        self._backup_profile()
        self.profile = self._get_default_profile()
        self._save_profile()

        print("\n✅ Profile reset to defaults")
        print("💾 Your previous profile was backed up")

    def find_similar_interests(self, new_interest: str) -> list[str]:
        """Find interests similar to the one being added

        Checks for:
        - Exact matches (case-insensitive)
        - Substring matches
        - Format variations (e.g., "Machine Learning" vs "ML")
        """
        similar = []
        new_lower = new_interest.lower().strip()
        current_interests = self.profile.get("core_interests", [])

        # Common abbreviations and variations
        variations_map = {
            "machine learning": ["ml", "deep learning"],
            "ml": ["machine learning"],
            "artificial intelligence": ["ai"],
            "ai": ["artificial intelligence"],
            "javascript": ["js"],
            "js": ["javascript"],
            "typescript": ["ts"],
            "ts": ["typescript"],
            "python": ["py"],
            "react": ["reactjs"],
            "docker": ["containerization"],
            "kubernetes": ["k8s"],
            "k8s": ["kubernetes"],
        }

        for interest in current_interests:
            interest_lower = interest.lower().strip()

            # Exact match (case-insensitive)
            if new_lower == interest_lower:
                similar.append(interest)
                continue

            # Substring match
            if new_lower in interest_lower or interest_lower in new_lower:
                similar.append(interest)
                continue

            # Check variations
            for variant_key, variant_list in variations_map.items():
                if new_lower == variant_key and interest_lower in variant_list:
                    similar.append(interest)
                    break
                if new_lower in variant_list and interest_lower == variant_key:
                    similar.append(interest)
                    break

        return similar

    def batch_add_interests(
        self, interests_to_add: list[str], backup_before: bool = True
    ) -> dict[str, any]:
        """Add multiple interests at once with duplicate detection

        Args:
            interests_to_add: List of interests to add
            backup_before: Whether to backup profile before changes

        Returns:
            Dictionary with results: {
                'added': [list of successfully added],
                'duplicates': [list of duplicates skipped],
                'similar': {interest: [similar_interests]},
                'total_added': count,
                'backup_created': bool
            }
        """
        result = {
            "added": [],
            "duplicates": [],
            "similar": {},
            "total_added": 0,
            "backup_created": False,
        }

        if not interests_to_add:
            return result

        # Create backup if requested
        if backup_before:
            self._backup_profile()
            result["backup_created"] = True

        current = self.profile.get("core_interests", [])
        current_lower = [i.lower() for i in current]

        for interest in interests_to_add:
            interest = interest.strip()
            if not interest:
                continue

            # Check for exact duplicates
            if interest.lower() in current_lower:
                result["duplicates"].append(interest)
                continue

            # Check for similar interests
            similar = self.find_similar_interests(interest)
            if similar:
                result["similar"][interest] = similar
                # Don't add if there are similar interests - ask user to consolidate
                continue

            # Add the interest
            current.append(interest)
            result["added"].append(interest)
            current_lower.append(interest.lower())

        result["total_added"] = len(result["added"])

        # Save if anything was added
        if result["added"]:
            self.profile["core_interests"] = current
            self._save_profile()

        return result

    def consolidate_interests(
        self,
        interests_to_remove: list[str],
        consolidated_name: str,
        backup_before: bool = True,
    ) -> dict[str, any]:
        """Consolidate similar interests into one

        Args:
            interests_to_remove: List of similar interests to remove
            consolidated_name: Single consolidated interest name
            backup_before: Whether to backup before changes

        Returns:
            Dictionary with results
        """
        result = {
            "removed": [],
            "added": False,
            "backup_created": False,
        }

        if backup_before:
            self._backup_profile()
            result["backup_created"] = True

        current = self.profile.get("core_interests", [])

        # Remove the old interests
        for interest in interests_to_remove:
            if interest in current:
                current.remove(interest)
                result["removed"].append(interest)

        # Add consolidated interest if not already present
        if result["removed"] and consolidated_name not in current:
            current.append(consolidated_name)
            result["added"] = True

        if result["removed"]:
            self.profile["core_interests"] = current
            self._save_profile()

        return result

    def get_profile_comparison(
        self, before: dict[str, any], after: dict[str, any]
    ) -> dict[str, any]:
        """Get detailed comparison of profile changes

        Args:
            before: Profile state before changes
            after: Profile state after changes

        Returns:
            Dictionary with before/after comparison and summary
        """
        comparison = {
            "interests": {"added": [], "removed": []},
            "senders": {"added": [], "removed": []},
            "projects": {"added": [], "removed": []},
            "summary": "",
        }

        # Compare interests
        before_interests = set(before.get("core_interests", []))
        after_interests = set(after.get("core_interests", []))

        comparison["interests"]["added"] = list(after_interests - before_interests)
        comparison["interests"]["removed"] = list(before_interests - after_interests)

        # Compare trusted senders
        before_senders = set(before.get("trusted_senders", []))
        after_senders = set(after.get("trusted_senders", []))

        comparison["senders"]["added"] = list(after_senders - before_senders)
        comparison["senders"]["removed"] = list(before_senders - after_senders)

        # Compare projects
        before_projects = set(before.get("active_projects", []))
        after_projects = set(after.get("active_projects", []))

        comparison["projects"]["added"] = list(after_projects - before_projects)
        comparison["projects"]["removed"] = list(before_projects - after_projects)

        # Build summary
        changes = []
        if comparison["interests"]["added"]:
            changes.append(f"+{len(comparison['interests']['added'])} interest(s)")
        if comparison["interests"]["removed"]:
            changes.append(f"-{len(comparison['interests']['removed'])} interest(s)")
        if comparison["senders"]["added"]:
            changes.append(f"+{len(comparison['senders']['added'])} sender(s)")
        if comparison["senders"]["removed"]:
            changes.append(f"-{len(comparison['senders']['removed'])} sender(s)")
        if comparison["projects"]["added"]:
            changes.append(f"+{len(comparison['projects']['added'])} project(s)")
        if comparison["projects"]["removed"]:
            changes.append(f"-{len(comparison['projects']['removed'])} project(s)")

        comparison["summary"] = ", ".join(changes) if changes else "No changes"

        return comparison

    def interactive_menu(self) -> None:
        """Interactive profile management menu"""
        while True:
            print("\n" + "=" * 60)
            print("⚙️  MANAGE YOUR EMAIL PROFILE")
            print("=" * 60)
            print()
            print("What would you like to do?")
            print()
            print("  1. Add core interests")
            print("  2. Remove core interests")
            print("  3. Add active projects")
            print("  4. Remove active projects")
            print("  5. Add trusted senders")
            print("  6. Remove trusted senders")
            print("  7. View current profile")
            print("  8. Reset to defaults")
            print("  9. Exit to main menu")
            print()

            choice = input("Choose an option (1-9): ").strip()

            if choice == "1":
                self.add_core_interests()

            elif choice == "2":
                self.remove_core_interests()

            elif choice == "3":
                self.add_active_projects()

            elif choice == "4":
                self.remove_active_projects()

            elif choice == "5":
                self.add_trusted_senders()

            elif choice == "6":
                self.remove_trusted_senders()

            elif choice == "7":
                self.view_profile()

            elif choice == "8":
                self.reset_to_defaults()

            elif choice == "9":
                print("\n👋 Returning to main menu...")
                break

            else:
                print("\n❌ Invalid choice. Please choose 1-9.")

            input("\n⏎ Press Enter to continue...")
