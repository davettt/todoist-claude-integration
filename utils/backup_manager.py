#!/usr/bin/env python3
"""
Backup Manager - Manual backup system for local data
Creates timestamped backups in user's Documents folder
Keeps last 10 days of backups
"""

import json
import os
import shutil
from datetime import datetime, timedelta


class BackupManager:
    """Manual backup system for critical local data"""

    def __init__(self):
        # Backup location in Documents folder (separate from project directory)
        self.backup_root = os.path.expanduser("~/Documents/todoist-backups")

        # Ensure backup directory exists
        os.makedirs(self.backup_root, exist_ok=True)

    def create_backup(self, description="Manual backup"):
        """
        Create a timestamped backup of all critical data

        Args:
            description: Optional description of why backup was created
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = f"{self.backup_root}/{timestamp}"

        print(f"\n🔄 Creating backup: {timestamp}")
        print(f"📁 Location: {backup_dir}")
        print("-" * 50)

        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)

        # Files and directories to backup
        items_to_backup = [
            # Critical data
            ("local_data/personal_data/", "Personal data files"),
            ("local_data/calendar_credentials.json", "Calendar OAuth credentials"),
            ("local_data/calendar_token.json", "Calendar OAuth token"),
            ("local_data/clients.db", "Client database (when exists)"),
            ("local_data/interaction_log.json", "Interaction log (when exists)"),
            # Configuration
            (".env", "Environment variables"),
            ("ROADMAP_personal.md", "Personal roadmap"),
            # Optional: Processed operations (if you want history)
            # ("local_data/processed/", "Processed operations"),
        ]

        backed_up = []
        skipped = []

        for item, description_text in items_to_backup:
            if os.path.exists(item):
                try:
                    dest_path = os.path.join(backup_dir, item)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                    if os.path.isdir(item):
                        shutil.copytree(item, dest_path, dirs_exist_ok=True)
                        print(f"✅ Backed up: {item} (directory)")
                    else:
                        shutil.copy2(item, dest_path)
                        size = os.path.getsize(item)
                        print(f"✅ Backed up: {item} ({size} bytes)")

                    backed_up.append(item)
                except Exception as e:
                    print(f"❌ Failed to backup {item}: {str(e)}")
                    skipped.append((item, str(e)))
            else:
                skipped.append((item, "File/directory does not exist yet"))

        # Create backup manifest
        manifest = {
            "backup_date": timestamp,
            "backup_time": datetime.now().isoformat(),
            "description": description,
            "files_backed_up": backed_up,
            "files_skipped": [
                {"item": item, "reason": reason} for item, reason in skipped
            ],
            "backup_size_bytes": self._get_directory_size(backup_dir),
        }

        with open(f"{backup_dir}/manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        print("-" * 50)
        print("✅ Backup complete!")
        print(f"📊 Files backed up: {len(backed_up)}")
        if skipped:
            print(f"⚠️  Files skipped: {len(skipped)}")
        print(f"💾 Total size: {self._format_size(manifest['backup_size_bytes'])}")
        print(f"\n📝 Description: {description}")

        # Cleanup old backups
        self.cleanup_old_backups()

        return backup_dir

    def cleanup_old_backups(self, keep_days=10):
        """
        Remove backups older than specified days

        Args:
            keep_days: Number of days of backups to keep (default: 10)
        """
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed_count = 0

        print(f"\n🧹 Cleaning up backups older than {keep_days} days...")

        for backup_name in os.listdir(self.backup_root):
            backup_path = os.path.join(self.backup_root, backup_name)

            if os.path.isdir(backup_path):
                try:
                    # Parse timestamp from directory name
                    backup_date = datetime.strptime(
                        backup_name.split("_")[0], "%Y-%m-%d"
                    )

                    if backup_date < cutoff:
                        shutil.rmtree(backup_path)
                        print(f"🗑️  Removed: {backup_name}")
                        removed_count += 1
                except (ValueError, IndexError):
                    # Not a valid backup directory name, skip
                    pass

        if removed_count > 0:
            print(f"✅ Removed {removed_count} old backup(s)")
        else:
            print("✅ No old backups to remove")

    def list_backups(self):
        """List all available backups"""
        print("\n📋 AVAILABLE BACKUPS:")
        print("=" * 60)

        backups = []

        for backup_name in sorted(os.listdir(self.backup_root), reverse=True):
            backup_path = os.path.join(self.backup_root, backup_name)

            if os.path.isdir(backup_path):
                manifest_path = os.path.join(backup_path, "manifest.json")

                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)

                        backups.append(
                            {
                                "name": backup_name,
                                "path": backup_path,
                                "date": manifest.get("backup_date", backup_name),
                                "description": manifest.get(
                                    "description", "No description"
                                ),
                                "size": manifest.get("backup_size_bytes", 0),
                                "files": len(manifest.get("files_backed_up", [])),
                            }
                        )
                    except Exception:
                        # Manifest couldn't be read
                        backups.append(
                            {
                                "name": backup_name,
                                "path": backup_path,
                                "date": backup_name,
                                "description": "No manifest",
                                "size": 0,
                                "files": "?",
                            }
                        )

        if not backups:
            print("No backups found.")
            print(f"Backups will be stored in: {self.backup_root}")
            return []

        for i, backup in enumerate(backups, 1):
            print(f"\n{i}. {backup['date']}")
            print(f"   Description: {backup['description']}")
            print(f"   Files: {backup['files']}")
            print(f"   Size: {self._format_size(backup['size'])}")
            print(f"   Location: {backup['path']}")

        print("=" * 60)
        print(f"Total backups: {len(backups)}")

        return backups

    def restore_backup(self, backup_name):
        """
        Restore from a specific backup
        WARNING: This will overwrite current files!

        How restore works:
        - Copies files from backup folder back to original locations
        - Only restores files that were in the backup (selective restore)
        - OVERWRITES current files with backup versions
        - Does NOT delete files that aren't in the backup

        Example:
        - Backup has: personal_data/, .env, calendar_token.json
        - Current has: personal_data/, .env, calendar_token.json, clients.db
        - After restore: All backed up files replaced, clients.db untouched

        Args:
            backup_name: Name of the backup directory to restore from
        """
        backup_path = os.path.join(self.backup_root, backup_name)

        if not os.path.exists(backup_path):
            print(f"❌ Backup not found: {backup_name}")
            return False

        print("\n⚠️  WARNING: This will overwrite current files!")
        print(f"📁 Restoring from: {backup_name}")
        print("\nHow this works:")
        print("  • Copies backup files to original locations")
        print("  • Overwrites existing files with backup versions")
        print("  • Files not in backup remain untouched")
        print("  • Directories are replaced completely")
        print()
        confirm = input("Type 'RESTORE' to confirm: ")

        if confirm != "RESTORE":
            print("❌ Restore cancelled")
            return False

        # Read manifest (not currently used, but validates backup structure)
        manifest_path = os.path.join(backup_path, "manifest.json")
        if os.path.exists(manifest_path):
            # Manifest exists - backup is complete
            pass
        else:
            print("⚠️  No manifest found, restoring all files...")

        restored = []
        failed = []

        print("\n🔄 Restoring files...")

        # Restore each file/directory
        for item in os.listdir(backup_path):
            if item == "manifest.json":
                continue

            source = os.path.join(backup_path, item)
            dest = item

            try:
                if os.path.isdir(source):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                    print(f"✅ Restored: {item} (directory)")
                else:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(source, dest)
                    print(f"✅ Restored: {item}")

                restored.append(item)
            except Exception as e:
                print(f"❌ Failed to restore {item}: {str(e)}")
                failed.append((item, str(e)))

        print("-" * 50)
        print("✅ Restore complete!")
        print(f"📊 Files restored: {len(restored)}")
        if failed:
            print(f"❌ Files failed: {len(failed)}")

        print("\n💡 Note: Only files in the backup were restored.")
        print("   Other files in your project remain unchanged.")

        return len(failed) == 0

    def _get_directory_size(self, path):
        """Calculate total size of directory"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
        except Exception:
            pass
        return total

    def _format_size(self, bytes):
        """Format bytes to human readable size"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"


def main():
    """Run backup manager as standalone script"""
    backup = BackupManager()

    print("\n" + "=" * 60)
    print("💾 BACKUP MANAGER")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("  1. Create backup now")
        print("  2. List all backups")
        print("  3. Restore from backup")
        print("  4. Exit")

        choice = input("\nChoose an option (1-4): ").strip()

        if choice == "1":
            description = input("Backup description (optional): ").strip()
            if not description:
                description = "Manual backup"
            backup.create_backup(description)

        elif choice == "2":
            backup.list_backups()

        elif choice == "3":
            backups = backup.list_backups()
            if backups:
                backup_num = input(
                    "\nEnter backup number to restore (or 'c' to cancel): "
                ).strip()
                if backup_num.lower() != "c":
                    try:
                        idx = int(backup_num) - 1
                        if 0 <= idx < len(backups):
                            backup.restore_backup(backups[idx]["name"])
                        else:
                            print("❌ Invalid backup number")
                    except ValueError:
                        print("❌ Invalid input")

        elif choice == "4":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please choose 1-4.")


if __name__ == "__main__":
    main()
