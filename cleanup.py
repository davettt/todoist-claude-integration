#!/usr/bin/env python3
"""
Cleanup script - Remove temporary, backup, and extra documentation files
Run this before committing to git to keep the repository clean
"""

import glob
import os


def cleanup_files():
    """Remove temporary and debug files"""

    print("🧹 CLEANUP SCRIPT")
    print("=" * 50)
    print()
    print("This will remove:")
    print("  • Backup files (*_BACKUP.py, *_FIXED.py)")
    print("  • Debug files (DEBUG_*.py)")
    print("  • Extra documentation files")
    print()

    confirm = input("Continue? (y/n): ").strip().lower()

    if confirm != "y":
        print("❌ Cleanup cancelled")
        return

    print()
    print("🔄 Cleaning up...")

    # Patterns to remove
    patterns = [
        # Root directory - backup/debug files
        "DEBUG_*.py",
        "BUG_FIXES_*.md",
        "FIXES_COMPLETE_*.md",
        "*_FIXED.py",
        # Root directory - extra docs (keep only README, QUICKSTART, CHANGELOG)
        "MAINTENANCE.md",
        "MAINTENANCE_SETUP.md",
        "VERSION.md",
        "VERSION_GUIDE.md",
        "SETUP_COMPLETE.md",
        # APIs directory
        "apis/*_BACKUP.py",
        "apis/*_FIXED.py",
        "apis/*_OLD.py",
    ]

    removed_count = 0

    for pattern in patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"  ✅ Removed: {file}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Error removing {file}: {e}")

    print()
    print(f"🎉 Cleanup complete! Removed {removed_count} file(s)")
    print()
    print("📁 Keeping only:")
    print("  • README.md")
    print("  • QUICKSTART.md")
    print("  • CHANGELOG.md")
    print("  • ROADMAP_personal.md (optional personal roadmap)")
    print()
    print("Safe to commit to git now!")


if __name__ == "__main__":
    cleanup_files()
