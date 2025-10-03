# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-10-03

### Added
- **Email Integration (Phase 1)** - Forward emails to create tasks automatically
  - Gmail API client with OAuth2 authentication (`apis/gmail_client.py`)
  - Email content sanitization - strips all URLs and email addresses for security (`utils/email_sanitizer.py`)
  - Email processor for automated task/event extraction (`email_processor.py`)
  - CLI script for processing forwarded emails (`process_emails.py`)
  - Pending operations directory structure (`local_data/pending_operations/`)
  - Interaction logging for future CRM integration (`local_data/personal_data/email_interactions_log.json`)
- Daily manager UI enhancements
  - Banner shows pending email operation count
  - Option 4: Process forwarded emails
  - Updated "Instructions for Claude" to include pending operations
  - Email operations mentioned in workflow guide
- File manager now checks pending_operations directory
- Security: Comprehensive URL/email stripping with 22 test cases (all passing)
- Dependencies: beautifulsoup4, lxml for HTML email parsing

### Changed
- README updated with email integration documentation and examples
- File structure includes pending_operations and email processing scripts
- .gitignore updated for Gmail credentials and email interaction logs
- requirements.txt updated with email processing dependencies

### Security
- All URLs stripped from email content before processing (no whitelisting)
- All email addresses removed from email bodies
- OAuth credentials and tokens properly git-ignored
- Local-only email processing (no cloud storage)

## [1.1.0] - 2025-09-30

### Added
- Focus blocks now counted accurately (counts how many 3-hour blocks fit in each free slot)
- New metric: `total_focus_blocks` in summary showing total deep work capacity
- New metric: `focus_slots_count` to distinguish between number of slots vs number of blocks
- Display now shows total deep work hours available (`total_focus_blocks × 3`)
- Versioning system with semantic versioning (MAJOR.MINOR.PATCH)
- Cleanup script to remove temporary files before git commits
- Version number now displayed in CLI banner

### Fixed
- **BREAKING FIX**: Timezone handling - calendar queries now use local timezone instead of forcing UTC
  - Events are now correctly found regardless of system timezone
  - Fixes issue where events were missed due to timezone offset (e.g., 9am meeting wasn't found because query started at 10am local time)
- Free time calculation no longer spans across busy periods
  - Algorithm now properly excludes meetings from free time blocks
  - Example: Day with 9am meeting now shows 2 free slots (7-9am, 10am-8pm) instead of 1 slot (7am-8pm)
- Focus blocks count now reflects actual productivity capacity
  - 13-hour free day now correctly shows 4 focus blocks (was 1)

### Changed
- `get_calendar_data.py` - Complete rewrite with timezone fixes and improved metrics
- `apis/google_calendar_client.py` - Rewrote `find_free_time()` algorithm for accuracy
- Updated `.gitignore` to better protect personal data and credentials

## [1.0.2] - 2025-09-29

### Added
- Manual backup system for local data protection
  - Creates timestamped backups in ~/Documents/todoist-backups
  - Keeps last 10 days automatically
  - Backs up personal data, OAuth credentials, and configuration
  - Includes restore functionality with confirmation
  - Integrated into daily_manager.py (options 6 & 7)
  - Selective backup: only critical files, excludes archives

### Changed
- Daily manager workflow improvements for better user experience

## [1.0.1] - 2025-09-27

### Changed
- Refactored Todoist logic to modular APIs for multi-service expansion
- Improved code organization and maintainability

## [1.0.0] - 2025-09-23

### Added
- Initial release with complete Todoist + Claude integration
- Task management automation (create, update, complete, delete)
- Intelligent multi-file handling with age detection and previews
- Archive functionality for automatic cleanup of old task files
- Natural language due dates support
- Batch operations support
- Daily manager CLI interface with guided 3-step workflow
- Calendar integration (optional) for availability analysis
- Comprehensive documentation and setup guides
- Secure API integration with proper error handling
- MIT license with safety disclaimers

### Changed
- Contributing guidelines now encourage forking over PRs for personal use focus

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Incompatible API changes or breaking changes
- **MINOR** version (0.X.0): New functionality in a backward compatible manner
- **PATCH** version (0.0.X): Backward compatible bug fixes

### Breaking Changes
Changes that require users to modify their workflow or data structure are marked as **BREAKING** in the changelog.
