# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.6] - 2025-10-25

### Added
- **Structured Email Digest Format** (decision-focused email summaries)
  - New digest format with 4 key sections: summary, relevance, key details, decision point
  - Claude API prompt redesigned (`utils/claude_api_client.py`) to request structured JSON output:
    - `summary`: Comprehensive 3-4 sentence overview enabling confident decisions without reading full email
    - `relevance`: Clear explanation of how email connects to user's interests/projects/trusted sources
    - `key_details[]`: Specific actionable items, data points, or insights (concrete, not vague)
    - `decision_point`: Describes what additional value reading the full email provides
  - Digest generator updated (`utils/email_digest_generator.py`) with emoji-coded markdown headers:
    - `📋 What's This About:` - Displays summary
    - `🎯 Why It's Relevant:` - Displays relevance
    - `💡 Key Details:` - Displays bullet-point key details
    - `📧 Decision Point:` - Displays decision point text
  - Interactive digest parser enhanced (`review_digest_interactive.py`) to extract all structured fields:
    - Detects new section headers and captures multi-line content
    - Parses key_details bullet points
    - Maintains backward compatibility with legacy bullet-point format

### Improved
- Email digest clarity and actionability - summaries are comprehensive enough to decide without reading full email
- User decision-making - decision_point field explicitly states what value remains if reading full email
- Format consistency - emoji headers provide visual structure to digest markdown
- AI prompt instructions - now emphasizes concrete details, specific connections, and clear value propositions

### Backward Compatibility
- New structured format coexists with legacy format
- Digest generator falls back to legacy bullet-point format if structured fields unavailable
- Parser gracefully handles both old and new digest formats
- No breaking changes to workflow or data structure

### Technical Details
- New JSON fields in Claude API response: `summary`, `relevance`, `key_details[]`, `decision_point`
- Maintained: `level`, `category`, `overall_reasoning`, `confidence`, `technologies_mentioned`, `topics_identified`
- Parser state management with dedicated flags for each section
- Multi-line content capture for summary and relevance fields
- Bullet point detection (•) for key_details extraction

## [1.5.5] - 2025-10-25

### Fixed
- **AI-Identified Themes Now Flow to Profile Suggestions**
  - Fixed Claude API prompt (`utils/claude_api_client.py`) to extract `technologies_mentioned` and `topics_identified`
  - Updated digest generator (`utils/email_digest_generator.py`) to include Technologies and Topics in markdown output
  - Enhanced digest parser (`review_digest_interactive.py`) to extract these fields from markdown
  - Modified feedback recording to pass `ai_analysis` dict with captured themes to learning engine
  - Result: Technologies and topics from email analysis now appear as selectable profile suggestions

- **Dynamic Thresholds for Small Datasets**
  - Learning engine now uses adaptive confidence thresholds:
    - Small datasets (< 15 high-value emails): threshold = 1 mention (shows emerging interests)
    - Large datasets (≥ 15 emails): threshold = 2 mentions (shows validated patterns)
  - Added fallback extraction:
    - Extracts technologies from email reasoning field when explicit data missing
    - Infers topics from email category when explicit data missing
  - Confidence labeling:
    - 2+ mentions: "High Confidence"
    - 1 mention: "Emerging interest" or "Emerging theme"
  - Result: Users with small feedback datasets now see actionable suggestions instead of empty list

### Impact
- Users can now apply AI-identified technologies (Docker, Kubernetes, GitHub, etc.) to their profile
- Users can apply AI-identified topics (DevOps, Developer Tools, etc.) to their profile
- Works with both new rich feedback data AND existing legacy entries
- Suggestions appear alongside trusted sender recommendations
- One-click batch application with confidence-based categorization

### Technical Details
- No breaking changes to existing code
- Backward compatible with existing feedback logs
- Fallback logic gracefully handles incomplete ai_analysis data
- Enhanced learning_engine.py with smarter extraction and thresholds

## [1.5.4] - 2025-10-24

### Added
- **Automated Profile Application Workflow** (enables intelligent profile updates from AI learning)
  - New `batch_add_interests()` method in `utils/profile_manager.py` - Add multiple interests at once with duplicate detection
  - New `find_similar_interests()` method - Detects duplicate/similar interests (exact match, substring, format variations)
  - New `consolidate_interests()` method - Merge similar interests into single consolidated name
  - New `get_profile_comparison()` method - Show detailed before/after profile changes
  - Common abbreviation mapping for variation detection (e.g., "ML" vs "Machine Learning", "AI" vs "Artificial Intelligence")
- **Enhanced Profile Application UI** (`apply_profile_suggestions()` in `learning_analyzer.py`)
  - Categorizes suggestions by confidence level (high, medium, low)
  - Visual indicators: 🎯 for high confidence, ⚠️ for medium, 💭 for low
  - Three application modes:
    - [a] Apply all high-confidence suggestions (one-click batch application)
    - [r] Review and select individually (selective application, not all-or-nothing)
    - [s] Skip for now
  - Interactive review mode for user control over each suggestion
  - Detailed feedback on each action: added, duplicates skipped, similar items identified
  - Before/after profile comparison with summary of all changes
  - Automatic backup creation before applying changes

### Improved
- **Batch application efficiency**: Users can now apply multiple learned suggestions in one action instead of manually adding each
- **Duplicate prevention**: System prevents adding interests already present or similar to existing ones
- **User control**: Suggestions are categorized by confidence so users can choose their comfort level for automation
- **Transparency**: Clear display of what changed, why items were skipped, and what went wrong

### Backward Compatibility
- All new methods in ProfileManager are optional enhancements
- Existing workflows and apply_profile_suggestions() behavior preserved
- No changes to profile data structure or storage format

### Expected User Workflow
1. **Run learning analyzer** - Generate profile suggestions from feedback patterns (option 9 in daily manager)
2. **Choose application mode** - Apply high-confidence only, review individually, or skip
3. **See results immediately** - Profile updated with backup, before/after comparison shown
4. **Continue improving** - Enhanced profile provides better email predictions going forward

## [1.5.3] - 2025-10-24

### Added
- **Rich AI Analysis Data Collection** (`utils/email_feedback_tracker.py`)
  - Extended feedback logging to capture AI-identified content metadata
  - New `ai_analysis` parameter stores: category, confidence, key_points, reasoning, technologies, topics
  - Backward compatible - gracefully handles existing entries without AI data
- **Intelligent Interest Suggestions** (enhanced `_suggest_interests_to_add()`)
  - Now analyzes AI-identified technologies and topics from high-value content
  - Suggests specific, meaningful interests (e.g., "Machine Learning", "Developer Tools")
  - Falls back to keyword extraction for entries without AI data
- **Content Pattern Analysis** (new methods in `utils/learning_engine.py`)
  - `analyze_content_patterns()` - Analyzes AI-identified themes in high-value content
  - `_analyze_category_preferences()` - Identifies user's preferred content categories
  - `_analyze_technology_mentions()` - Tracks technologies user cares about
  - `_analyze_topic_patterns()` - Finds common topics in escalated content
- **Enhanced Learning Dashboard** (`learning_analyzer.py`)
  - New option 4: Content pattern analysis display
  - Shows preferred categories, technologies, and topic themes
  - Provides insights about content preferences based on AI analysis

### Improved
- Interest suggestions now based on actual AI analysis instead of primitive keyword matching
- Learning system can identify specific technologies and topics user prefers
- More actionable recommendations: suggest "Docker" instead of random keywords
- Rich feedback data enables future improvements to learning algorithms

### Backward Compatibility
- Existing feedback entries work without `ai_analysis` field
- New entries with AI data provide enhanced learning capabilities
- System gracefully degrades to keyword matching for entries without AI analysis

## [1.5.2] - 2025-10-24

### Fixed
- **CRITICAL: Learning engine fundamentally misinterpreted feedback semantics**
  - Was treating all "useful" feedback as "high-value sender" (WRONG)
  - Now correctly distinguishes: 👍 to LOW priority ≠ valuable sender
  - Fixed `_suggest_senders_to_add()` to only recommend senders with actual escalations (⬆️) or high-priority agreements
  - Fixed `_suggest_interests_to_add()` to only extract keywords from genuinely high-value content (not low-priority agreements)
  - Fixed `_analyze_sender_patterns()` to show meaningful metrics instead of misleading "useful_rate"
- Replaced misleading "useful_rate" metric with:
  - `high_value_rate`: % of emails user wanted higher priority OR agreed with high/urgent predictions
  - `escalation_rate`: % of emails user explicitly escalated (⬆️)
- Updated learning analyzer display and reports to show correct metrics

### Impact
- Senders like Strava/Prime Video no longer wrongly suggested as "trusted" (user agrees they're LOW priority)
- Only suggests senders where user genuinely escalates or wants higher priority content
- Interest suggestions now based on actual high-value content, not low-priority agreements
- Learning insights are now accurate and actionable

## [1.5.1] - 2025-10-24

### Fixed
- **CRITICAL: Email feedback accuracy calculation was completely inverted**
  - Previously: LOW predictions showed 0% accuracy (inverted logic)
  - Fixed: LOW predictions now correctly show 100% accuracy (matches user behavior)
  - Overall accuracy corrected from 38.9% to 80.4% (realistic range)
  - All 470 feedback entries recalculated with correct logic
- Corrected feedback interpretation:
  - 👍 (useful) = User agrees with prediction = ACCURATE
  - 👎 (not_interesting) = Only accurate if LOW (can't go lower)
  - ⬆️ (more_important) = Prediction was too low = INACCURATE
  - ⬇️ (less_important) = Prediction was too high = INACCURATE
- Learning analysis now provides meaningful, actionable insights based on correct accuracy data

### Impact
- Learning engine suggestions are now valid and reliable
- Accuracy trends now reflect actual user preferences
- System can now improve email digest predictions based on real feedback patterns

## [1.5.0] - 2025-10-24

### Added
- **AI Learning Engine** (`utils/learning_engine.py`)
  - Analyzes user feedback patterns to identify trends and biases
  - Generates profile optimization suggestions based on rating history
  - Calculates learning weights for adaptive AI adjustments
  - Provides adaptive context for dynamic AI prompting
- **Adaptive AI Context** (`utils/adaptive_ai_context.py`)
  - Generates dynamic analysis prompts based on learned preferences
  - Incorporates strongest/weakest areas into recommendations
  - Adjusts confidence thresholds based on historical accuracy
  - Highlights learned sender preferences during analysis
- **Learning Insights Dashboard** (`learning_analyzer.py`)
  - Interactive CLI for viewing learning insights and trends
  - Displays accuracy analysis by prediction level and over time
  - Shows sender-specific patterns and usefulness rates
  - Provides actionable profile optimization suggestions
  - Shows learning weights being applied to AI analysis
  - Generates comprehensive learning reports (markdown export)
  - Guides users through applying suggestions to their profile
- **Enhanced Email Digest Generator**
  - Shows when learning adjustments are being applied during analysis
  - Displays active learning preferences before digest generation
  - Integrates learning context into analysis workflow
- **Daily Manager Enhancement**
  - Option 9: Analyze AI learning & suggestions (new)
  - View evolving preferences and accuracy improvements
  - Get personalized recommendations for profile optimization

### Changed
- Daily manager menu reorganized (options shifted to accommodate learning feature)
  - Email options now include learning analysis (option 9)
  - View options shifted to 10-11, Backup/Setup/Exit shifted to 12-16
- Menu prompt updated to accept choices 1-16
- Email digest generator now initializes learning engine at startup

### Improved
- Email digest analysis with learning-based adjustments
- Profile recommendations based on substantial feedback analysis
- User experience with personalized learning insights

## [1.4.0] - 2025-10-24

### Added
- Interactive profile management system (`utils/profile_manager.py`)
  - View email interest profile in human-readable format
  - Manage interests, active projects, and trusted senders interactively
  - Email validation for trusted senders (supports both email addresses and domains)
  - Automatic backup creation before any profile changes
  - Graceful handling of missing or corrupted profile files
- Daily manager enhancements
  - Option 7: View email interest profile (display current interests, projects, trusted senders)
  - Option 8: Manage email interest profile (add/remove items interactively)
  - Menu reorganized to include profile management in EMAIL section

### Changed
- Daily manager menu reorganized (options shifted to accommodate new features)
  - Former options 7-8 (VIEWS) now options 9-10
  - Former options 9-13 (BACKUP/SETUP/EXIT) now options 11-15
- Menu prompt updated to accept choices 1-15

## [1.3.1] - 2025-10-04

### Added
- Original sender extraction from forwarded email bodies (`utils/forwarded_email_parser.py`)
- Dual trust system with separate `trusted_forwarders` and `trusted_senders` lists
- `archive_message()` method to properly remove emails from inbox
- Security warnings when emails not from user's forwarding accounts
- Forwarder display in digest LOW interest section

### Changed
- Enhanced Claude API prompts for more specific, actionable email summaries
- MEDIUM interest emails now show AI reasoning to help decision-making
- LOW interest emails show all bullet points instead of just first one
- Archive action now properly removes from inbox (not just mark as read)

### Fixed
- Archive functionality now removes INBOX label in addition to UNREAD
- Email display formatting improvements (no stray asterisks)

### Security
- **Dual trust verification**: Checks both forwarder (security) and original sender (priority)
- Forwarder validation prevents processing non-forwarded emails
- Original sender prioritization for trusted content sources
- Both forwarder and sender displayed in digests for transparency

## [1.3.0] - 2025-10-04

### Added
- **Email Digest System (Phase 2.5)** - AI-powered email intelligence with learning system
  - Claude API integration for smart email analysis (`utils/email_digest_generator.py`)
  - Biweekly email digest generator with interest level predictions (`biweekly_email_digest.py`)
  - Interactive digest review tool with inline rating system (`review_digest_interactive.py`)
  - Email feedback tracker for continuous learning (`utils/email_feedback_tracker.py`)
  - Interest profile system for personalized email prioritization (`local_data/personal_data/email_interest_profile.json`)
  - Feedback logging with accuracy tracking (`local_data/personal_data/email_feedback_log.json`)
- Daily manager enhancements
  - Option 5: Generate biweekly email digest
  - Option 6: Review digest interactively (read, rate, manage emails)
  - Auto-mark emails as read after digest generation
- Email management actions during review
  - Archive emails (mark as read)
  - Trash emails (30-day auto-delete failsafe)
  - Keep in inbox or skip
- Gmail API enhancements
  - Full Gmail scope for read, modify, and trash operations
  - `trash_message()` method for safe email cleanup
  - Embedded Gmail IDs in digest markdown for email management

### Changed
- Gmail API scopes upgraded to `https://mail.google.com/` for full email management
- Improved email display formatting (cleaner layout, no stray asterisks, emoji indicators)
- Date display simplification in interactive review
- Better error handling and user messaging throughout digest workflow
- Enhanced Claude API prompts for more specific, actionable email summaries
- MEDIUM interest emails now show AI reasoning to help decision-making
- LOW interest emails show all bullet points instead of just first one

### Fixed
- Gmail API authentication scopes for delete/trash operations
- Stray asterisks in email display formatting
- Email archiving now properly removes from inbox (not just mark as read)
- Archive action now uses `archive_message()` method (removes UNREAD + INBOX labels)

### Security
- **Dual trust system**: Separate checks for forwarders (your accounts) vs senders (content sources)
- Original sender extraction from forwarded email bodies (`utils/forwarded_email_parser.py`)
- Trusted forwarders list prevents processing emails sent directly to inbox
- Trusted senders list prioritizes content from known sources (e.g., James Clear)
- Security warnings when emails not forwarded from user's accounts
- Both forwarder and original sender displayed in digests for transparency

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
