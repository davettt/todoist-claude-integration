# Productivity Hub - Strategic Roadmap
**Private Document - Not pushed to GitHub**

---

## 🎯 Vision

Transform todoist-python into a comprehensive productivity hub with integrated:
- Task management (Todoist)
- Calendar (Google Calendar)
- Email processing (Gmail assistant)
- Client relationship management (Custom local CRM)

**Timeline:** 6-month phased implementation  
**Current Status:** Foundation phase (task + calendar working)

---

## 📊 Current State (Sept 2025)

### ✅ Working Systems
- Todoist integration (full CRUD operations)
- Google Calendar integration (optional)
- Three CLI interfaces:
  - `daily_manager.py` - Simple 3-step workflow
  - `todoist_manager.py` - Advanced features
  - `calendar_manager.py` - Calendar operations
- Modular architecture (apis/, utils/)
- Security hardened (no user path exposure)

### 🔄 Current Business Context
- Business in holding pattern (not actively seeking new clients)
- Existing clients: Recurring services only (~2 invoices/month)
- CapsuleCRM: Handling recurring reminders (free plan)
- Target: Resume active client work in ~6 months

### ⚠️ Current Limitations
- No email integration
- No unified client management
- Manual CRM updates
- Limited client workflow automation

---

## 🗺️ Phased Implementation Plan

### PHASE 1: Email Integration Foundation (NOW - Week 1)
**Goal:** Email forwarding → Task/Calendar automation

#### Setup Requirements
1. **Create dedicated Gmail account**
   - Purpose: Assistant inbox for forwarded emails
   - Example: `david-todoist-assistant@gmail.com`
   - Separate from business email (david@tiongcreative.com.au)

2. **Google Cloud Console**
   - Enable Gmail API (same project as Calendar)
   - Create OAuth credentials
   - Download → save as `local_data/gmail_credentials.json`

#### Implementation Tasks
- [ ] Create `apis/gmail_client.py`
  - OAuth authentication (same pattern as calendar)
  - Read unread messages
  - Get message content
  - Delete messages after processing
  
- [ ] Create `email_processor.py`
  - Sanitize emails (CRITICAL: strip all URLs)
  - Extract client info (email, name, company)
  - Send to Claude for analysis
  - Identify: meeting requests, action items, client context
  
- [ ] Create `process_forwarded_emails.py`
  - Main email processing script
  - Check Gmail inbox
  - Process each forwarded email
  - Create task/calendar operation files
  - Delete from Gmail after processing
  - Log interactions locally

- [ ] Update `daily_manager.py`
  - Add option: "Process forwarded emails"
  - Show pending email operations for review
  - Preview before applying

#### Security Requirements
**CRITICAL: URL Stripping**
```python
def sanitize_email_content(email_text):
    """Remove all URLs and suspicious content"""
    # Remove URLs
    email_text = re.sub(r'http[s]?://\S+', '[URL REMOVED]', email_text)
    # Remove email addresses from body
    email_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                       '[EMAIL REMOVED]', email_text)
    return email_text
```

**No whitelisting needed initially** - Just strip URLs

#### Data Structure (Foundation for CRM)
```json
// Start capturing client context NOW
{
  "email_metadata": {
    "from_address": "client@example.com",
    "from_name": "John Client",
    "company": "ClientCorp",
    "date": "2025-09-29T18:00:00"
  },
  "operations": [...],
  "interaction_log": {
    "date": "2025-09-29",
    "type": "email_received",
    "summary": "Client asked about hosting performance",
    "action_taken": "task_created"
  }
}
```

#### File Structure
```
todoist-python/
├── apis/
│   └── gmail_client.py              ← NEW
├── email_processor.py                ← NEW
├── process_forwarded_emails.py       ← NEW
├── daily_manager.py                  ← UPDATE (add email option)
└── local_data/
    ├── gmail_credentials.json        ← NEW (OAuth)
    ├── gmail_token.json              ← NEW (auto-generated)
    └── personal_data/
        └── interaction_log.json      ← NEW (foundation for CRM)
```

#### Success Criteria
- ✅ Can forward email to assistant inbox
- ✅ Email processed automatically
- ✅ Task created with client context
- ✅ Calendar event created if meeting
- ✅ Interaction logged locally
- ✅ Original email deleted from Gmail
- ✅ All URLs stripped before processing

#### User Workflow
```
1. Receive client email in ProtonMail/VentraIP/Outlook
2. Forward to assistant@gmail.com
3. Run: python3 daily_manager.py
4. Option: "Process forwarded emails"
5. Review suggested tasks/events
6. Apply changes
```

---

### PHASE 2: Observation & Data Collection (Months 1-3)
**Goal:** Learn patterns, accumulate interaction data

#### Activities
- Use email forwarding daily
- Track in notes:
  - How many client emails/week?
  - How often need CRM logging?
  - What client info needed most?
  - Pain points with current workflow?

#### Data Accumulation
- Interaction logs building up in JSON
- Client email addresses identified
- Patterns emerging (types of requests, frequency)
- Foundation data for CRM design

#### Evaluation Questions
- Is manual CRM update becoming painful?
- Which emails need CRM logging vs don't?
- What client context would help most?
- Ready to build CRM features?

---

### PHASE 3: Local CRM Foundation (Months 3-4, ~2 weeks)
**Goal:** Lightweight client database with secure storage

#### Implementation Tasks
- [ ] Create `crm/client_database.py`
  - SQLite database with encryption
  - Client table (id, email, name, company, status)
  - Interactions table (date, type, summary, encrypted notes)
  - Services table (hosting, domains, rates, renewal dates)
  - Invoices table (date, amount, status, due date)

- [ ] Create `crm/interaction_logger.py`
  - Log all client contact automatically
  - Link to tasks/emails/calendar
  - Encrypted storage

- [ ] Create `crm/service_manager.py`
  - Track client services (hosting, domains, etc.)
  - Renewal date tracking
  - Rate management

- [ ] Create `client_manager.py`
  - CLI interface for client management
  - View clients
  - View interaction history
  - Add/update services
  - Generate invoice reminders

- [ ] Create `utils/secure_storage.py`
  - Encryption wrapper for sensitive data
  - Key management (.env)
  - Encrypt/decrypt helpers

#### Security Implementation
```python
# Generate encryption key (one-time)
from cryptography.fernet import Fernet
key = Fernet.generate_key()

# Add to .env
CLIENT_DB_KEY=your_generated_key_here

# Encrypt sensitive data before storing
class SecureClientDatabase:
    def store_note(self, note):
        encrypted = self.cipher.encrypt(note.encode())
        # Store encrypted in database
```

#### Database Schema
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    company TEXT,
    first_contact_date TEXT,
    last_contact_date TEXT,
    status TEXT,  -- prospect/active/inactive
    notes_encrypted BLOB
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    date TEXT NOT NULL,
    type TEXT,  -- email/meeting/call/work
    summary_encrypted BLOB,
    related_task_id TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    service_type TEXT,  -- hosting/domain/web/other
    start_date TEXT,
    renewal_date TEXT,
    rate REAL,
    status TEXT,  -- active/cancelled
    notes_encrypted BLOB,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    date TEXT NOT NULL,
    amount REAL,
    status TEXT,  -- pending/sent/paid
    due_date TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
```

#### File Structure Updates
```
todoist-python/
├── crm/                              ← NEW
│   ├── __init__.py
│   ├── client_database.py
│   ├── interaction_logger.py
│   ├── service_manager.py
│   └── invoice_scheduler.py
├── utils/
│   └── secure_storage.py             ← NEW
├── client_manager.py                 ← NEW
└── local_data/
    ├── clients.db                    ← NEW (encrypted SQLite)
    └── client_files/                 ← NEW (encrypted docs)
```

#### Success Criteria
- ✅ Can store client info securely (encrypted)
- ✅ Can log interactions
- ✅ Can track services and renewals
- ✅ Can view client history
- ✅ Simple CLI for client management

---

### PHASE 4: Email-CRM Integration (Months 4-5, ~2 weeks)
**Goal:** Connect email processing to client database

#### Implementation Tasks
- [ ] Update `email_processor.py`
  - Check if email from known client
  - Show client context when processing
  - Auto-log interaction to CRM
  - Link tasks to client records

- [ ] Create `integrations/email_to_client.py`
  - Email → Client lookup/creation
  - Interaction logging
  - Context enrichment

- [ ] Create `integrations/task_client_linking.py`
  - Link Todoist tasks to clients
  - Show client context in tasks
  - Track client work

- [ ] Update `daily_manager.py`
  - Show client context when reviewing emails
  - Display client interaction history
  - Option to view client dashboard

#### Enhanced Email Workflow
```
Email arrives from client@example.com
↓
System checks: Known client?
↓
YES: Show context:
  - Last interaction: 3 weeks ago
  - Current services: Hosting, Domain
  - Outstanding tasks: None
  - Next invoice: Due in 2 months
  - Interaction history: Last 5 contacts
↓
Claude analyzes WITH context
↓
Creates:
  - Task (with client link)
  - Calendar event if needed
  - CRM interaction log
  - Updates client last_contact_date
↓
User reviews full context and approves
```

#### Success Criteria
- ✅ Email processing recognizes clients
- ✅ Shows full client context
- ✅ Auto-logs interactions
- ✅ Tasks linked to clients
- ✅ Complete client view available

---

### PHASE 5: Full CRM Features (Month 5-6, ~3 weeks)
**Goal:** Complete client management system for business relaunch

#### Implementation Tasks
- [ ] Create `crm/invoice_scheduler.py`
  - Monthly check for upcoming invoices
  - Auto-create invoice reminder tasks
  - Track invoice status

- [ ] Create `crm/renewal_tracker.py`
  - Monthly check for service renewals
  - Auto-create renewal tasks (14 days before)
  - Email client renewal notices

- [ ] Create `crm/client_health.py`
  - Analyze client engagement
  - Flag clients with no contact 90+ days
  - Identify upsell opportunities
  - Generate client health dashboard

- [ ] Create `migrate_from_capsule.py`
  - Export data from CapsuleCRM
  - Import to local database
  - Preserve interaction history
  - Migration verification

- [ ] Create `workflows/new_client_onboarding.py`
  - Standardized new client process
  - Checklist automation
  - Document templates
  - Welcome email sequence

- [ ] Update `daily_manager.py`
  - Client dashboard view
  - Today's client tasks
  - Upcoming renewals/invoices
  - Client health alerts

#### Automated Client Management
```python
# Run monthly
def automated_client_maintenance():
    # Invoice reminders
    for client in active_clients:
        if client.next_invoice_date in next_30_days:
            create_task(f"Invoice {client.name}", 
                       due=client.next_invoice_date,
                       priority=2)
    
    # Renewal reminders
    for service in active_services:
        if service.renewal_date in next_60_days:
            create_task(f"Renew {service.type} for {client.name}",
                       due=service.renewal_date - 14_days,
                       priority=2)
    
    # Client health checks
    for client in active_clients:
        days_since_contact = (now() - client.last_contact_date).days
        if days_since_contact > 90:
            create_task(f"Follow up with {client.name}",
                       due="this week",
                       labels=["Client Retention"])
```

#### Final File Structure
```
productivity-hub/  (renamed from todoist-python)
├── apis/
│   ├── todoist_client.py
│   ├── google_calendar_client.py
│   └── gmail_client.py
│
├── crm/
│   ├── client_database.py
│   ├── interaction_logger.py
│   ├── service_manager.py
│   ├── invoice_scheduler.py
│   ├── renewal_tracker.py
│   └── client_health.py
│
├── integrations/
│   ├── email_to_client.py
│   ├── task_client_linking.py
│   └── calendar_client_sync.py
│
├── workflows/
│   ├── new_client_onboarding.py
│   ├── project_workflow.py
│   └── invoice_workflow.py
│
├── utils/
│   ├── file_manager.py
│   └── secure_storage.py
│
├── daily_manager.py           ← Enhanced with client features
├── client_manager.py
├── migrate_from_capsule.py
│
└── local_data/
    ├── clients.db             ← Encrypted client data
    ├── client_files/          ← Encrypted documents
    └── backups/
        └── clients_backup_YYYY-MM-DD.db
```

#### Success Criteria
- ✅ Complete client lifecycle management
- ✅ Automated reminders (invoices, renewals)
- ✅ Client health monitoring
- ✅ Migrated from CapsuleCRM
- ✅ Ready for active client work
- ✅ Maximum efficiency workflow

---

## 🔐 Security Requirements

### PII Storage Strategy
**What stays in CapsuleCRM (during transition):**
- Contact details (until migrated)
- Financial data (until migrated)

**What goes in local encrypted database:**
- Interaction logs
- Internal notes
- Task history
- Service details
- Project status

**Encryption approach:**
```python
# All sensitive data encrypted at rest
# Key stored in .env (like API tokens)
# Use cryptography.fernet for encryption
# Only decrypted when needed for display
```

### Data Protection
- ✅ Encryption key in .env (git-ignored)
- ✅ Database encrypted at rest
- ✅ No URLs stored from emails
- ✅ Regular backups (encrypted)
- ✅ No cloud storage of PII
- ✅ Local-only processing

---

## 📋 Current Action Items

### Immediate (This Week)
1. [ ] Create dedicated Gmail account
2. [ ] Set up Gmail API in Google Cloud Console
3. [ ] Download OAuth credentials
4. [ ] Begin Phase 1 implementation

### Documentation Updates Needed
- [ ] Update README with email integration
- [ ] Create EMAIL_SETUP.md guide
- [ ] Update QUICKSTART.md with email workflow
- [ ] Create CRM_GUIDE.md (when Phase 3 starts)

### Environment Variables to Add
```bash
# .env additions

# Gmail (uses OAuth, no token needed)
# CLIENT_DB_KEY will be added in Phase 3
CLIENT_DB_KEY=generate_when_ready
```

---

## 💡 Design Principles

### Keep These In Mind
1. **Modular architecture** - Each feature is independent
2. **Security first** - All PII encrypted at rest
3. **Local-first** - No cloud dependencies for sensitive data
4. **Progressive enhancement** - Each phase adds value
5. **User control** - Always review before applying changes
6. **Data ownership** - You own all data, no vendor lock-in

### Don't Do These
- ❌ Store URLs from emails
- ❌ Auto-apply changes without review
- ❌ Store unencrypted PII
- ❌ Rush to integrate before observing patterns
- ❌ Over-engineer before understanding needs

---

## 📊 Success Metrics

### Phase 1 Success (Week 1)
- Processing 5+ emails per week
- Tasks created successfully
- Calendar events from emails working
- No security issues

### Phase 2 Success (Month 3)
- Clear usage patterns identified
- Interaction log has 3 months data
- Know exactly what CRM needs
- Ready to build Phase 3

### Phase 3 Success (Month 4)
- Client database operational
- Can track all clients
- Interaction history complete
- Services and renewals tracked

### Phase 4 Success (Month 5)
- Email → Client integration seamless
- Full context shown automatically
- No duplicate data entry
- Workflow efficient

### Phase 5 Success (Month 6)
- Ready for active client work
- Automated reminders working
- CapsuleCRM migrated/phased out
- Maximum efficiency achieved

---

## 🎯 End Goal

**By Month 6, you'll have:**
- Unified productivity hub
- Email → Tasks → Calendar → CRM (all integrated)
- Automated client management
- Secure local PII storage
- Maximum efficiency for client work
- Zero ongoing costs
- Complete data ownership

**When clients return:**
- Forward email → System handles everything
- Full client context automatically
- Tasks created with links to client
- Interactions logged automatically
- Renewals/invoices never forgotten
- Professional, efficient service delivery

---

## 📝 Notes

### Remember
- This is YOUR system - customize as needed
- Build incrementally - don't rush
- Observe patterns before building features
- Security is non-negotiable
- Keep it simple until complexity is justified

### When to Deviate
If you find during Phase 2 that:
- Email integration isn't being used → Don't build CRM
- CRM needs are different → Adjust Phase 3 design
- Timeline changes → Adapt accordingly

**The plan is a guide, not a mandate. Adjust based on real usage.**

---

**Last Updated:** September 29, 2025  
**Status:** Phase 1 Ready to Begin  
**Next Review:** After Phase 1 completion (~1 week)
