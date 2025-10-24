# Add Interactive Interest Profile Management

## Problem Statement
Users cannot view or edit their email interest profile (`local_data/personal_data/email_interest_profile.json`) without manually editing JSON files. This makes the email digest system difficult to maintain as interests change over time, leading to poor AI predictions.

## Requirements

### Functional Requirements
1. **View Profile**: Display current profile in human-readable format
   - Show core interests, active projects, trusted senders/forwarders
   - Display counts for keyword lists
   - Show last modified date

2. **Manage Profile**: Interactive editing capabilities
   - Add/remove core interests
   - Add/remove active projects  
   - Add/remove trusted senders (with email validation)
   - Reset to defaults option

3. **Data Safety**
   - Create backup before any changes
   - Handle missing/corrupted profile files gracefully
   - Validate email addresses and domains

### Integration Requirements
- Add options 7 and 8 to daily manager EMAIL section
- Don't break existing menu numbering or functionality
- Use existing profile JSON structure

## User Experience

### View Profile (Option 7)
User sees organized display:
```
🎯 CORE INTERESTS:
  • Personal development
  • AI and automation
  
🚀 ACTIVE PROJECTS:
  • todoist-python integration
  
🔒 TRUSTED FORWARDERS: 5 configured
📧 TRUSTED SENDERS: 3 configured
📅 Last updated: 2025-10-24 2:30 PM
```

### Manage Profile (Option 8)
Interactive menu with options:
1. Add/remove core interests
2. Add/remove active projects
3. Add/remove trusted senders
4. View current profile
5. Reset to defaults
6. Exit

**Add Flow**: User types comma-separated items, system validates and saves
**Remove Flow**: User selects from numbered list, system confirms removal

## Technical Constraints
- Profile file location: `local_data/personal_data/email_interest_profile.json`
- Backup naming: `email_interest_profile_backup_YYYY-MM-DD.json`
- Email validation: Basic format checking for @ and domain structure
- No external dependencies required

## Files to Modify
- Create: `utils/profile_manager.py`
- Modify: `daily_manager.py` (add menu options and imports)
- Update: `version.py` (1.3.1 → 1.4.0)
- Update: `CHANGELOG.md`

## Success Criteria
- ✅ Users can view profile without editing JSON
- ✅ Users can add/remove interests and projects interactively
- ✅ Email validation prevents invalid trusted senders
- ✅ Backup created before any changes
- ✅ Missing/corrupted files handled gracefully
- ✅ All existing functionality remains unchanged

## Testing Requirements

### Manual Tests
1. View profile with existing data
2. Add new interest, verify saved correctly
3. Remove existing project, verify backup created
4. Test with missing profile file
5. Test with corrupted JSON file
6. Verify email validation for trusted senders

### Regression Tests
- All existing daily manager options still work
- Email digest generation uses updated profile
- Menu numbering unchanged for other options

## Version Information
**Version bump:** 1.3.1 → 1.4.0 (MINOR - new features, backward compatible)

**CHANGELOG entry:**
```markdown
## [1.4.0] - 2025-10-24

### Added
- View interest profile in daily manager (option 7)
- Interactive profile management in daily manager (option 8)
- Add/remove interests, projects, and trusted senders
- Email validation for trusted senders
- Automatic profile backup before changes
- Graceful handling of missing/corrupted profile files
```

## Cleanup Instructions
Delete after implementation:
- Any `SUMMARY.md` or `IMPLEMENTATION*.md` files created by Claude Code
- This `PROFILE_MANAGEMENT_SPEC.md` file
- Any other temporary `.md` files