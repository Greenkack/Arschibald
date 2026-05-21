# CRM System Deep Analysis
## Comprehensive Documentation for Streamlit-to-Electron Migration

**Task:** 97. CRM System Deep Analysis  
**Date:** 2025-01-21  
**Status:** Complete  
**Requirements:** 1.3, 6.1

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Core Modules Analysis](#core-modules-analysis)
4. [Customer Management Workflows](#customer-management-workflows)
5. [Offer Tracking System](#offer-tracking-system)
6. [Task & Note Management](#task--note-management)
7. [Email Integration](#email-integration)
8. [Reporting & Forecasting](#reporting--forecasting)
9. [Database Schema](#database-schema)
10. [Integration Points](#integration-points)
11. [Migration Recommendations](#migration-recommendations)

---

## Executive Summary

The CRM system is a comprehensive customer relationship management solution integrated into the solar calculator application. It provides:

- **Customer Management**: Full CRUD operations with advanced filtering and search
- **Project Tracking**: Solar project lifecycle management linked to customers
- **Offer Management**: Complete offer workflow from draft to acceptance/rejection
- **Task System**: Priority-based task management with due dates and assignments
- **Communication History**: Notes, emails, calls, and appointments tracking
- **Lead Scoring**: Automated lead qualification and prioritization
- **Pipeline Management**: Visual sales pipeline with Kanban-style interface
- **Reporting Engine**: Customizable reports with visualizations
- **Forecasting**: Sales targets and pipeline-based forecasting
- **Email Integration**: SMTP-based email sending with templates

**Total Lines of Code Analyzed:** ~15,000+ lines across 50+ files

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CRM System                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Core UI    │  │   Features   │  │  Integration │     │
│  │              │  │              │  │              │     │
│  │ • crm.py     │  │ • Offers     │  │ • PDF Bridge │     │
│  │ • Dashboard  │  │ • Tasks      │  │ • Calc Bridge│     │
│  │ • Pipeline   │  │ • Notes      │  │ • Data Input │     │
│  │ • Calendar   │  │ • Email      │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Advanced    │  │   Reporting  │  │   Utilities  │     │
│  │              │  │              │  │              │     │
│  │ • Lead Score │  │ • Reports    │  │ • Backup     │     │
│  │ • Forecasting│  │ • Analytics  │  │ • Import/Exp │     │
│  │ • Contracts  │  │ • Dashboards │  │ • Notif.     │     │
│  │ • Geo Mapping│  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  SQLite Database │
                  │                  │
                  │ • customers      │
                  │ • projects       │
                  │ • crm_leads      │
                  │ • crm_tasks      │
                  │ • crm_activities │
                  │ • email_*        │
                  │ • sales_*        │
                  └──────────────────┘
```


### Module Structure

```
crm/
├── __init__.py
├── features/                    # Feature modules (18 files)
│   ├── offer_tracker.py        # Offer lifecycle management
│   ├── task_manager.py         # Task CRUD & workflow
│   ├── note_manager.py         # Communication history
│   ├── email_manager.py        # Email sending & templates
│   ├── reporting_engine.py     # Report generation
│   ├── forecasting_engine.py   # Sales forecasting
│   ├── lead_scoring.py         # Lead qualification
│   ├── contract_manager.py     # Contract management
│   ├── geo_mapper.py           # Geographic mapping
│   ├── feedback_manager.py     # Customer feedback
│   ├── knowledge_base.py       # Knowledge management
│   ├── call_manager.py         # Call logging
│   ├── tag_manager.py          # Tagging system
│   ├── template_manager.py     # Template management
│   ├── dashboard_widgets.py    # Dashboard components
│   └── *_ui.py                 # UI components for each feature
├── integration/                 # Integration bridges (3 files)
│   ├── pdf_bridge.py           # PDF generation integration
│   ├── calculation_bridge.py   # Solar calculator integration
│   └── data_input_bridge.py    # Data input integration
└── utils/                       # Utility modules (3 files)
    ├── backup_scheduler.py     # Automated backups
    ├── import_export_manager.py # Data import/export
    └── notification_manager.py  # Notification system

Main UI Files:
├── crm.py                      # Main CRM module (2335 lines)
├── crm_dashboard_ui.py         # Dashboard interface
├── crm_pipeline_ui.py          # Sales pipeline UI
└── crm_calendar_ui.py          # Calendar & appointments
```

---

## Core Modules Analysis

### 1. crm.py - Main CRM Module

**File:** `crm.py` (2335 lines)  
**Purpose:** Core customer and project management

#### Key Functions:

**Customer Management:**
- `create_tables_crm()` - Database schema initialization
- `save_customer()` - Create/update customer records
- `load_customer()` - Retrieve single customer
- `load_all_customers()` - Retrieve all customers
- `delete_customer()` - Remove customer and related data
- `render_crm()` - Main UI rendering function

**Project Management:**
- `save_project()` - Create/update project records
- `load_project()` - Retrieve single project
- `load_projects_for_customer()` - Get customer's projects
- `delete_project()` - Remove project

**UI Rendering:**
- `render_customer_management()` - Customer list and forms
- `render_lead_scoring_tab()` - Lead scoring interface
- `render_backup_tab()` - Backup management

#### Database Schema (customers table):

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salutation TEXT,
    title TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    company_name TEXT,
    address TEXT,
    house_number TEXT,
    zip_code TEXT,
    city TEXT,
    state TEXT,
    region TEXT,
    email TEXT,
    phone_landline TEXT,
    phone_mobile TEXT,
    income_tax_rate_percent REAL DEFAULT 0.0,
    creation_date TEXT,
    last_updated TEXT
)
```

#### Database Schema (projects table):

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    project_name TEXT NOT NULL,
    project_status TEXT,
    roof_type TEXT,
    roof_covering_type TEXT,
    free_roof_area_sqm REAL,
    roof_orientation TEXT,
    roof_inclination_deg INTEGER,
    building_height_gt_7m INTEGER,
    annual_consumption_kwh REAL,
    costs_household_euro_mo REAL,
    annual_heating_kwh REAL,
    costs_heating_euro_mo REAL,
    anlage_type TEXT,
    feed_in_type TEXT,
    module_quantity INTEGER,
    selected_module_id INTEGER,
    selected_inverter_id INTEGER,
    include_storage INTEGER,
    selected_storage_id INTEGER,
    selected_storage_storage_power_kw REAL,
    include_additional_components INTEGER,
    selected_wallbox_id INTEGER,
    selected_ems_id INTEGER,
    selected_optimizer_id INTEGER,
    selected_carport_id INTEGER,
    selected_notstrom_id INTEGER,
    selected_tierabwehr_id INTEGER,
    visualize_roof_in_pdf INTEGER,
    latitude REAL,
    longitude REAL,
    creation_date TEXT,
    last_updated TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

#### Key Features:

1. **Advanced Search & Filtering:**
   - Full-text search across name, city, email, phone
   - Multi-select city filter
   - Tag-based filtering
   - Sort by name, city, date

2. **View Modes:**
   - Card view (4-column grid)
   - Table view with actions
   - Detail view with full information

3. **Tag System Integration:**
   - Customer tagging for categorization
   - Tag-based filtering and search
   - Visual tag badges with colors

4. **Document Management:**
   - File upload to customer records
   - Document type classification
   - Version tracking
   - Download and delete capabilities

5. **Email Integration:**
   - Direct email sending from customer view
   - Email template support
   - Email history tracking


### 2. crm_dashboard_ui.py - Dashboard Interface

**File:** `crm_dashboard_ui.py`  
**Purpose:** Central CRM dashboard with KPIs and widgets

#### Key Components:

**Dashboard Tabs:**
1. **Overview** - Business metrics and activity timeline
2. **Widgets** - Configurable dashboard widgets
3. **Customers** - Customer overview with search
4. **Projects** - Project pipeline visualization
5. **Revenue** - Revenue analysis and trends
6. **Statistics** - Business statistics and charts
7. **Tasks** - Task management interface

#### KPI Cards:

```python
KPIs = {
    'active_customers': "Number of active customers",
    'running_projects': "Projects in progress",
    'open_offers': "Pending offers",
    'total_revenue': "Total revenue (EUR)"
}
```

#### Features:

- **Real-time Statistics:** Live KPI updates
- **Activity Timeline:** Recent customer interactions
- **Customer Search:** Advanced filtering and search
- **Project Pipeline:** Visual funnel representation
- **Revenue Charts:** Monthly/yearly comparisons
- **Performance Metrics:** Conversion rates, cycle times

---

### 3. crm_pipeline_ui.py - Sales Pipeline

**File:** `crm_pipeline_ui.py` (1055 lines)  
**Purpose:** Visual sales pipeline management

#### Pipeline Stages:

```python
pipeline_stages = {
    'lead': {'name': 'Lead', 'icon': '📋', 'order': 1},
    'qualified': {'name': 'Qualifiziert', 'icon': '✅', 'order': 2},
    'proposal': {'name': 'Angebot', 'icon': '📄', 'order': 3},
    'negotiation': {'name': 'Verhandlung', 'icon': '🤝', 'order': 4},
    'won': {'name': 'Gewonnen', 'icon': '🎉', 'order': 5},
    'lost': {'name': 'Verloren', 'icon': '❌', 'order': 6}
}
```

#### Lead Sources:

- Website
- Empfehlung (Referral)
- Social Media
- Kaltakquise (Cold calling)
- Messe (Trade show)
- Online-Werbung (Online advertising)
- Printmedien (Print media)
- Sonstiges (Other)

#### Key Features:

1. **Kanban Board:** Drag-and-drop pipeline visualization
2. **Lead Scoring Integration:** Automatic lead prioritization
3. **Pipeline Analytics:** Conversion rates, deal values
4. **Lead Management:** Create, edit, move leads
5. **Follow-up Tracking:** Automated reminders
6. **Source Performance:** Lead source analytics

#### Database Schema (crm_leads):

```sql
CREATE TABLE crm_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    lead_source TEXT,
    estimated_value REAL DEFAULT 0,
    probability INTEGER DEFAULT 50,
    expected_close_date DATE,
    stage TEXT DEFAULT 'lead',
    stage_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER DEFAULT 0
)
```

---

### 4. crm_calendar_ui.py - Calendar & Appointments

**File:** `crm_calendar_ui.py`  
**Purpose:** Appointment scheduling and calendar management

#### Appointment Types:

```python
appointment_types = {
    'consultation': {'name': 'Beratungstermin', 'icon': '💼'},
    'site_visit': {'name': 'Vor-Ort-Termin', 'icon': '🏠'},
    'installation': {'name': 'Installation', 'icon': '🔧'},
    'follow_up': {'name': 'Nachfassung', 'icon': '📞'},
    'reminder': {'name': 'Erinnerung', 'icon': '⏰'},
    'maintenance': {'name': 'Wartung', 'icon': '🛠️'}
}
```

#### Features:

1. **Month View:** Calendar grid with appointments
2. **Appointment Creation:** Form with customer linking
3. **Reminder System:** Configurable reminders (15min - 1 day)
4. **Filtering:** By type, period, status
5. **Customer Integration:** Link appointments to customers
6. **Status Tracking:** Scheduled, completed, cancelled

#### Database Schema (crm_appointments):

```sql
CREATE TABLE crm_appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    customer_id INTEGER,
    location TEXT,
    notes TEXT,
    reminder_minutes INTEGER DEFAULT 60,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

---

## Customer Management Workflows

### Workflow 1: New Customer Creation

```
1. User clicks "Neuen Kunden anlegen"
2. Form displays with fields:
   - Salutation, Title, Name (required)
   - Company name (optional)
   - Address details
   - Contact information
   - Tax rate
3. User fills form and submits
4. Validation:
   - First name and last name required
   - Email format validation
   - Phone format validation
5. save_customer() creates record
6. Success message displayed
7. View switches to customer list
8. New customer appears in list
```

### Workflow 2: Customer Search & Filter

```
1. User enters search term in search box
2. System searches across:
   - First name + Last name
   - City
   - Email
   - Phone
3. User selects filters:
   - City (multi-select)
   - Tags (multi-select)
   - Sort order
4. Results update in real-time
5. User can switch between:
   - Card view (4 columns)
   - Table view (with actions)
```

### Workflow 3: Customer Detail View

```
1. User clicks "View" on customer
2. System loads customer data
3. Display sections:
   - Basic information
   - Contact details
   - Tax information
   - Tags
   - Email integration
   - Projects list
   - Document vault
4. User can:
   - Edit customer
   - Add project
   - Send email
   - Upload documents
   - Add tags
```

### Workflow 4: Project Management

```
1. From customer view, click "Neues Projekt anlegen"
2. Option to load data from input tab
3. Form displays with sections:
   - Project name and status
   - Roof details
   - Consumption data
   - System configuration
4. User fills or loads data
5. save_project() creates record
6. Project linked to customer
7. Project appears in customer's project list
```

---

## Offer Tracking System

### Module: crm/features/offer_tracker.py

**Purpose:** Complete offer lifecycle management from draft to acceptance/rejection

#### Offer Status Flow:

```
draft → sent → [accepted | rejected]
         ↓
    follow_up
```

#### Key Functions:

**1. create_offer_tracking_tables()**
- Extends projects table with offer fields
- Adds columns: offer_status, offer_sent_date, offer_accepted_date, etc.

**2. update_offer_status()**
```python
def update_offer_status(
    conn: sqlite3.Connection,
    project_id: int,
    new_status: str,
    **kwargs: Any
) -> bool
```
- Updates offer status
- Sets status-specific dates
- Creates automatic follow-up reminders (7 days after sending)
- Tracks rejection reasons

**3. get_offer_status()**
- Retrieves complete offer information
- Returns status, dates, version, value, rejection details

**4. get_all_offers()**
- Lists all offers with optional filtering
- Includes customer information
- Supports status filtering

**5. get_pending_follow_ups()**
- Finds offers needing follow-up
- Filters by due date
- Returns customer contact information

**6. update_lead_status_from_offer()**
- Syncs offer status with lead pipeline
- Maps: accepted → won, rejected → lost

**7. get_offer_statistics()**
- Calculates offer metrics
- Returns: total offers, status breakdown, conversion rate, avg value

#### Database Extensions:

```sql
ALTER TABLE projects ADD COLUMN offer_status TEXT DEFAULT "draft";
ALTER TABLE projects ADD COLUMN offer_sent_date TEXT;
ALTER TABLE projects ADD COLUMN offer_accepted_date TEXT;
ALTER TABLE projects ADD COLUMN offer_rejected_date TEXT;
ALTER TABLE projects ADD COLUMN offer_version INTEGER DEFAULT 1;
ALTER TABLE projects ADD COLUMN offer_value REAL;
ALTER TABLE projects ADD COLUMN rejection_reason TEXT;
ALTER TABLE projects ADD COLUMN rejection_notes TEXT;
ALTER TABLE projects ADD COLUMN follow_up_date TEXT;
ALTER TABLE projects ADD COLUMN follow_up_completed INTEGER DEFAULT 0;
```

#### Offer Workflow:

```
1. Create Project → Status: draft
2. Generate PDF Offer
3. Send to Customer → Status: sent
   - Sets offer_sent_date
   - Creates follow_up_date (+7 days)
4. Customer Response:
   a) Accepted → Status: accepted
      - Sets offer_accepted_date
      - Updates lead to "won"
      - Triggers contract creation
   b) Rejected → Status: rejected
      - Sets offer_rejected_date
      - Records rejection_reason
      - Updates lead to "lost"
5. Follow-up Reminder
   - Notification when follow_up_date reached
   - Mark as completed after contact
```


---

## Task & Note Management

### Module: crm/features/task_manager.py

**Purpose:** Complete task management with CRUD operations, status workflow, and notifications

#### Task Status Flow:

```
open → in_progress → completed
  ↑                      ↓
  └──────── reopen ──────┘
```

#### Task Priorities:

- **Low** (🔵): Non-urgent tasks
- **Medium** (🟡): Standard priority
- **High** (🔴): Urgent tasks

#### Key Functions:

**CRUD Operations:**

1. **create_task()** - Create new task
   - Required: title, description, status, priority
   - Optional: due_date, customer_id, project_id, lead_id, assigned_to
   - Returns: task_id

2. **get_task()** - Retrieve single task
3. **update_task()** - Update task fields
4. **delete_task()** - Remove task

**Query Functions:**

5. **get_all_tasks()** - List with filters
   - Filter by: status, priority, customer, project, lead, assigned_to
   - Special filters: overdue_only, due_soon_days

6. **get_tasks_by_customer()** - Customer-specific tasks
7. **get_tasks_by_project()** - Project-specific tasks
8. **get_tasks_by_lead()** - Lead-specific tasks
9. **get_overdue_tasks()** - Past due date tasks
10. **get_tasks_due_soon()** - Tasks due in X days

**Workflow Functions:**

11. **mark_task_in_progress()** - Set status to 'in_progress'
12. **mark_task_completed()** - Set status to 'completed', set completed_at
13. **reopen_task()** - Reset to 'open', clear completed_at

**Statistics & Notifications:**

14. **get_task_statistics()** - Aggregate metrics
    - Total, by status, by priority
    - Overdue count, due today, due this week

15. **get_tasks_needing_notification()** - Notification queue
    - Overdue tasks (high priority)
    - Due today (medium priority)
    - Due tomorrow (low priority)

**Helper Functions:**

16. **is_task_overdue()** - Check if task is past due
17. **get_task_display_color()** - Color coding for UI
18. **format_task_for_display()** - Add display metadata

#### Database Schema (crm_tasks):

```sql
CREATE TABLE crm_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open', -- 'open', 'in_progress', 'completed'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high'
    due_date DATE,
    customer_id INTEGER,
    project_id INTEGER,
    lead_id INTEGER,
    assigned_to TEXT,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (lead_id) REFERENCES crm_leads(id)
)
```

#### Task Workflow Example:

```
1. Create Task:
   - Title: "Follow up with customer"
   - Priority: High
   - Due: Tomorrow
   - Assigned to: "John Doe"
   - Linked to: Customer #123

2. Task appears in:
   - Customer detail view
   - Dashboard task list
   - "Due Soon" notifications

3. User starts work:
   - mark_task_in_progress()
   - Status: in_progress

4. User completes:
   - mark_task_completed()
   - Status: completed
   - completed_at: timestamp

5. If needed, reopen:
   - reopen_task()
   - Status: open
   - completed_at: NULL
```

---

### Module: crm/features/note_manager.py

**Purpose:** Communication history and activity tracking

#### Activity Types:

```python
ACTIVITY_TYPES = {
    "note": "Notiz",
    "email": "E-Mail",
    "call": "Anruf",
    "appointment": "Termin",
    "meeting": "Besprechung",
    "task": "Aufgabe",
    "other": "Sonstiges"
}
```

#### Key Functions:

**CRUD Operations:**

1. **create_activity()** - Add new activity
   - Parameters: customer_id, activity_type, title, content, created_by, is_important
   - Returns: activity_id

2. **get_activity()** - Retrieve single activity
3. **get_customer_activities()** - List customer activities
   - Filter by: activity_type, include_archived
   - Limit results
   - Sorted by date (newest first)

4. **update_activity()** - Modify activity
5. **delete_activity()** - Remove activity
6. **toggle_important()** - Mark/unmark as important

**Search & Management:**

7. **search_activities()** - Full-text search
   - Search in: title, content
   - Filter by: customer_id, activity_type
   - Returns: matching activities

8. **auto_archive_old_activities()** - Cleanup
   - Archives activities older than X days
   - Excludes important activities
   - Returns: count archived

9. **get_activity_statistics()** - Metrics
   - Total activities
   - By type breakdown
   - Important count
   - Last activity date

**Helper Functions:**

10. **add_note()** - Shortcut for note creation
11. **add_email_activity()** - Shortcut for email logging
12. **add_call_activity()** - Shortcut for call logging
13. **add_appointment_activity()** - Shortcut for appointment logging

#### Database Schema (crm_activities):

```sql
CREATE TABLE crm_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_important BOOLEAN DEFAULT 0,
    archived BOOLEAN DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

#### Activity Timeline Workflow:

```
1. Customer Interaction Occurs
   ↓
2. Create Activity:
   - Type: call/email/meeting/note
   - Title: Brief description
   - Content: Detailed notes
   - Mark important if needed
   ↓
3. Activity Appears in:
   - Customer detail view
   - Activity timeline
   - Search results
   ↓
4. Auto-Archive After 30 Days:
   - Non-important activities archived
   - Important activities retained
   ↓
5. Search & Retrieval:
   - Full-text search
   - Filter by type
   - View archived
```

---

## Email Integration

### Module: crm/features/email_manager.py

**Purpose:** SMTP email sending with templates and history tracking

#### Key Components:

**1. SMTP Configuration Management**

```python
smtp_config = {
    'smtp_host': 'smtp.example.com',
    'smtp_port': 587,
    'smtp_username': 'user@example.com',
    'smtp_password': '***',
    'smtp_use_tls': True,
    'smtp_from_email': 'noreply@example.com',
    'smtp_from_name': 'Company Name'
}
```

Functions:
- `get_smtp_config()` - Load configuration
- `save_smtp_config()` - Save configuration
- `test_smtp_connection()` - Validate settings

**2. Email Template System**

Template Structure:
```python
{
    'name': 'Angebot versendet',
    'subject': 'Ihr Solar-Angebot von {{company_name}}',
    'body': 'Sehr geehrte/r {{customer_name}}, ...',
    'category': 'Angebot',
    'placeholders': ['customer_name', 'company_name', 'current_date']
}
```

Functions:
- `create_email_template()` - Create template
- `get_email_template()` - Retrieve by ID
- `get_email_template_by_name()` - Retrieve by name
- `list_email_templates()` - List all templates
- `update_email_template()` - Modify template
- `delete_email_template()` - Soft delete (set inactive)

**3. Placeholder System**

Supported Placeholders:
- `{{customer_name}}` - Full name
- `{{first_name}}` - First name
- `{{last_name}}` - Last name
- `{{company_name}}` - Company
- `{{email}}` - Email address
- `{{phone}}` - Phone number
- `{{address}}` - Full address
- `{{city}}` - City
- `{{zip_code}}` - ZIP code
- `{{project_value}}` - Project value
- `{{current_date}}` - Current date

Functions:
- `replace_placeholders()` - Replace in text
- `extract_placeholders()` - Find placeholders in text

**4. Email Sending**

Functions:
- `send_email()` - Direct SMTP send
  - Supports HTML/plain text
  - Attachment support
  - Error handling

- `send_email_with_template()` - Template-based send
  - Loads template
  - Replaces placeholders
  - Sends email
  - Logs to history

**5. Email History**

Functions:
- `save_email_to_history()` - Log sent email
- `get_email_history_for_customer()` - Customer email log
- `get_all_email_history()` - All emails with filters

#### Database Schema:

**email_templates:**
```sql
CREATE TABLE email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT,
    placeholders TEXT, -- JSON array
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**email_history:**
```sql
CREATE TABLE email_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    template_id INTEGER,
    attachments TEXT, -- JSON array
    status TEXT DEFAULT 'sent', -- 'sent', 'failed'
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_by TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (template_id) REFERENCES email_templates(id)
)
```

#### Default Templates:

1. **Angebot versendet** - Offer sent notification
2. **Follow-up nach Angebot** - Offer follow-up
3. **Terminbestätigung** - Appointment confirmation
4. **Auftragsbestätigung** - Order confirmation

#### Email Workflow:

```
1. User selects customer
2. Clicks "Send Email"
3. Selects template or writes custom
4. System replaces placeholders:
   {{customer_name}} → "Max Mustermann"
   {{current_date}} → "21.01.2025"
5. Optional: Attach PDF offer
6. Send via SMTP
7. Log to email_history:
   - Status: sent/failed
   - Timestamp
   - Template used
8. Activity created in crm_activities
9. Email appears in customer history
```


---

## Reporting & Forecasting

### Module: crm/features/reporting_engine.py

**Purpose:** Comprehensive reporting system with visualizations and exports

#### Report Types:

**1. Predefined Reports:**

- **Sales Overview** - Revenue and offer analysis
- **Conversion Funnel** - Pipeline conversion rates
- **Lead Sources** - Lead source performance

**2. Custom Reports:**

- **Report Builder** - Flexible query builder
- **Custom Filters** - Dynamic filtering
- **Aggregations** - SUM, AVG, COUNT, etc.

#### Key Functions:

**Predefined Reports:**

1. **get_sales_overview()**
```python
def get_sales_overview(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "monthly"  # daily, weekly, monthly
) -> Dict[str, Any]
```
Returns:
- DataFrame with sales data
- Summary statistics
- Plotly chart
- Period: daily/weekly/monthly

2. **get_conversion_funnel()**
- Analyzes lead progression through pipeline
- Calculates conversion rates per stage
- Returns funnel visualization

3. **get_lead_sources_report()**
- Analyzes lead sources
- Calculates conversion rate per source
- Shows average deal value per source

**Custom Report Builder:**

4. **build_custom_report()**
```python
def build_custom_report(
    table: str,
    columns: List[str],
    filters: Optional[Dict[str, Any]] = None,
    group_by: Optional[List[str]] = None,
    aggregations: Optional[Dict[str, str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]
```

Example:
```python
report = build_custom_report(
    table='projects',
    columns=['project_name', 'offer_value', 'offer_status'],
    filters={'offer_status': ['sent', 'accepted']},
    group_by=['offer_status'],
    aggregations={'offer_value': 'SUM'},
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

**Visualization Functions:**

5. **_create_sales_overview_chart()** - Bar chart with status colors
6. **_create_funnel_chart()** - Funnel visualization
7. **_create_lead_sources_chart()** - Pie + bar chart combo

**Export Functions:**

8. **export_to_excel()** - Excel file with formatting
9. **export_to_csv()** - CSV export
10. **export_chart_to_html()** - Interactive HTML chart

**Template Management:**

11. **save_report_template()** - Save report configuration
12. **load_report_template()** - Load saved report
13. **list_report_templates()** - List all templates
14. **delete_report_template()** - Remove template

#### Database Schema (saved_reports):

```sql
CREATE TABLE saved_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    report_type TEXT NOT NULL,
    config TEXT NOT NULL, -- JSON configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    last_used TIMESTAMP
)
```

#### Report Workflow:

```
1. User selects report type:
   - Predefined (Sales, Funnel, Sources)
   - Custom (Report Builder)

2. Configure parameters:
   - Date range
   - Filters
   - Grouping
   - Aggregations

3. Generate report:
   - Query database
   - Process data
   - Create visualizations

4. View results:
   - Data table
   - Charts
   - Summary statistics

5. Export options:
   - Excel (.xlsx)
   - CSV (.csv)
   - HTML (interactive chart)

6. Save as template:
   - Name and description
   - Store configuration
   - Reuse later
```

---

### Module: crm/features/forecasting_engine.py

**Purpose:** Sales targets and pipeline-based forecasting

#### Key Components:

**1. Sales Targets**

Target Types:
- **Individual** - Personal sales goals
- **Team** - Team-wide targets
- **Company** - Organization-wide goals

Period Types:
- **Monthly** - 1 month targets
- **Quarterly** - 3 month targets
- **Yearly** - Annual targets

Target Units:
- **EUR** - Revenue targets
- **deals** - Number of closed deals
- **leads** - Number of new leads

Functions:
- `create_sales_target()` - Create new target
- `get_sales_targets()` - List with filters
- `update_target_progress()` - Update current value
- `update_target_status()` - Change status (active/completed/failed/cancelled)

**2. Forecasting**

Forecast Methods:
- **pipeline_based** - Based on current pipeline
- **historical** - Based on past performance
- **manual** - Manual entry

Functions:
- `calculate_pipeline_forecast()` - Calculate from pipeline
  - Weights leads by stage probability
  - Calculates confidence level
  - Returns forecast value

- `create_forecast()` - Save forecast
- `get_forecasts()` - List forecasts

**3. Analysis & Tracking**

Functions:
- `get_target_achievement_status()` - Calculate progress
  - Achievement percentage
  - Time percentage
  - Health status (excellent/good/warning/critical)

- `check_at_risk_targets()` - Find endangered targets
- `auto_update_target_progress_from_pipeline()` - Auto-sync

#### Database Schema:

**sales_targets:**
```sql
CREATE TABLE sales_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_name TEXT NOT NULL,
    target_type TEXT NOT NULL, -- 'individual', 'team', 'company'
    assigned_to TEXT,
    period_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'yearly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    target_value REAL NOT NULL,
    target_unit TEXT DEFAULT 'EUR',
    current_value REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT
)
```

**sales_forecasts:**
```sql
CREATE TABLE sales_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER,
    forecast_period TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    forecast_value REAL NOT NULL,
    confidence_level REAL, -- 0.0 - 1.0
    forecast_method TEXT,
    pipeline_data TEXT, -- JSON
    calculation_details TEXT, -- JSON
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY(target_id) REFERENCES sales_targets(id)
)
```

#### Pipeline Forecast Algorithm:

```python
# Stage probability weights
stage_probabilities = {
    'lead': 0.10,        # 10% chance
    'qualified': 0.25,   # 25% chance
    'proposal': 0.50,    # 50% chance
    'negotiation': 0.75, # 75% chance
    'won': 1.0,          # 100% (already won)
    'lost': 0.0          # 0% (already lost)
}

# Calculate weighted value
for lead in pipeline:
    probability = stage_probabilities[lead.stage]
    weighted_value = lead.estimated_value * probability
    total_forecast += weighted_value

# Confidence based on lead count
if leads < 5: confidence = 0.3
elif leads < 10: confidence = 0.5
elif leads < 20: confidence = 0.7
else: confidence = 0.85
```

#### Forecasting Workflow:

```
1. Create Sales Target:
   - Name: "Q1 2025 Revenue"
   - Type: Team
   - Period: 2025-01-01 to 2025-03-31
   - Target: €500,000
   - Unit: EUR

2. Generate Forecast:
   - Method: pipeline_based
   - Analyze current pipeline
   - Weight by stage probability
   - Calculate confidence

3. Monitor Progress:
   - Current: €320,000 (64%)
   - Time elapsed: 60%
   - Status: on_track
   - Health: good

4. Alerts:
   - If achievement < time_elapsed * 0.8:
     Status: at_risk
   - If achievement < time_elapsed * 0.6:
     Status: off_track

5. Auto-Update:
   - When lead moves to "won"
   - Add deal value to current_value
   - Recalculate forecast
```

---

## Database Schema

### Complete Schema Overview

**Core Tables:**

1. **customers** - Customer master data
2. **projects** - Solar projects linked to customers
3. **crm_leads** - Sales pipeline leads
4. **crm_tasks** - Task management
5. **crm_activities** - Communication history
6. **crm_appointments** - Calendar appointments

**Email System:**

7. **email_templates** - Email templates
8. **email_history** - Sent email log

**Forecasting:**

9. **sales_targets** - Sales goals
10. **sales_forecasts** - Revenue forecasts

**Reporting:**

11. **saved_reports** - Report templates

**Additional Features:**

12. **crm_tags** - Tag definitions
13. **customer_tags** - Customer-tag relationships
14. **lead_scoring_rules** - Scoring configuration
15. **customer_documents** - Document storage

### Relationships:

```
customers (1) ──< (N) projects
customers (1) ──< (N) crm_activities
customers (1) ──< (N) crm_appointments
customers (1) ──< (N) crm_tasks
customers (1) ──< (N) email_history
customers (1) ──< (N) customer_documents
customers (N) ──< (N) crm_tags (via customer_tags)

projects (1) ──< (N) crm_tasks

crm_leads (1) ──< (N) crm_tasks

email_templates (1) ──< (N) email_history

sales_targets (1) ──< (N) sales_forecasts
```

---

## Integration Points

### 1. PDF Bridge (crm/integration/pdf_bridge.py)

**Purpose:** Integrate CRM with PDF generation system

Functions:
- `generate_offer_pdf()` - Create offer PDF from project
- `attach_pdf_to_customer()` - Save PDF to customer documents
- `get_pdf_type_badge_color()` - UI badge colors
- `get_pdf_type_label()` - PDF type labels

Integration Flow:
```
Project → generate_offer_pdf() → PDF File → attach_to_customer() → Document Vault
```

### 2. Calculation Bridge (crm/integration/calculation_bridge.py)

**Purpose:** Link CRM with solar calculator

Functions:
- `import_calculation_to_project()` - Import calc results
- `sync_project_with_calculation()` - Keep in sync
- `get_calculation_summary()` - Display in CRM

Integration Flow:
```
Solar Calculator → Calculation Results → import_to_project() → CRM Project
```

### 3. Data Input Bridge (crm/integration/data_input_bridge.py)

**Purpose:** Import data from input forms

Functions:
- `load_from_session_state()` - Import from Streamlit session
- `map_input_to_project()` - Field mapping
- `validate_imported_data()` - Data validation

Integration Flow:
```
Input Form → Session State → load_from_session() → Project Data
```

---

## Migration Recommendations

### For FastAPI Backend:

**1. Service Layer Structure:**

```python
# backend/services/crm_service.py
class CRMService:
    def __init__(self, db: Session):
        self.db = db
    
    # Customer operations
    async def create_customer(self, customer_data: CustomerCreate) -> Customer
    async def get_customer(self, customer_id: int) -> Customer
    async def list_customers(self, filters: CustomerFilters) -> List[Customer]
    async def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer
    async def delete_customer(self, customer_id: int) -> bool
    
    # Project operations
    async def create_project(self, project_data: ProjectCreate) -> Project
    async def get_project(self, project_id: int) -> Project
    async def list_projects(self, customer_id: int) -> List[Project]
    
    # Offer operations
    async def update_offer_status(self, project_id: int, status: str) -> Offer
    async def get_pending_follow_ups(self) -> List[Offer]
    
    # Task operations
    async def create_task(self, task_data: TaskCreate) -> Task
    async def get_tasks(self, filters: TaskFilters) -> List[Task]
    async def update_task_status(self, task_id: int, status: str) -> Task
```

**2. API Endpoints:**

```python
# backend/api/v1/crm.py
@router.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, service: CRMService = Depends())

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(filters: CustomerFilters, service: CRMService = Depends())

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, service: CRMService = Depends())

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, data: CustomerUpdate, service: CRMService = Depends())

@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, service: CRMService = Depends())

# Similar endpoints for projects, tasks, offers, etc.
```

**3. Pydantic Models:**

```python
# backend/models/crm_schemas.py
class CustomerBase(BaseModel):
    salutation: Optional[str]
    title: Optional[str]
    first_name: str
    last_name: str
    company_name: Optional[str]
    email: Optional[EmailStr]
    phone_mobile: Optional[str]
    address: Optional[str]
    city: Optional[str]
    zip_code: Optional[str]

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    first_name: Optional[str]
    last_name: Optional[str]

class CustomerResponse(CustomerBase):
    id: int
    creation_date: datetime
    last_updated: datetime
    
    class Config:
        orm_mode = True
```

### For React Frontend:

**1. Component Structure:**

```typescript
// frontend/src/pages/CRM/
├── CustomerList.tsx          // Customer list with search/filter
├── CustomerDetail.tsx        // Customer detail view
├── CustomerForm.tsx          // Create/edit customer
├── ProjectList.tsx           // Project list
├── ProjectDetail.tsx         // Project detail
├── OfferTracker.tsx          // Offer management
├── TaskManager.tsx           // Task list and management
├── ActivityTimeline.tsx      // Communication history
├── EmailComposer.tsx         // Email sending interface
├── Dashboard.tsx             // CRM dashboard
└── Pipeline.tsx              // Sales pipeline
```

**2. API Service:**

```typescript
// frontend/src/services/crmService.ts
export const crmService = {
  // Customers
  getCustomers: (filters?: CustomerFilters) => api.get('/crm/customers', { params: filters }),
  getCustomer: (id: number) => api.get(`/crm/customers/${id}`),
  createCustomer: (data: CustomerCreate) => api.post('/crm/customers', data),
  updateCustomer: (id: number, data: CustomerUpdate) => api.put(`/crm/customers/${id}`, data),
  deleteCustomer: (id: number) => api.delete(`/crm/customers/${id}`),
  
  // Projects
  getProjects: (customerId: number) => api.get(`/crm/customers/${customerId}/projects`),
  createProject: (data: ProjectCreate) => api.post('/crm/projects', data),
  
  // Tasks
  getTasks: (filters?: TaskFilters) => api.get('/crm/tasks', { params: filters }),
  createTask: (data: TaskCreate) => api.post('/crm/tasks', data),
  updateTaskStatus: (id: number, status: string) => api.patch(`/crm/tasks/${id}/status`, { status }),
  
  // Offers
  updateOfferStatus: (projectId: number, status: string) => 
    api.patch(`/crm/projects/${projectId}/offer-status`, { status }),
  getPendingFollowUps: () => api.get('/crm/offers/pending-follow-ups'),
  
  // Email
  sendEmail: (data: EmailSend) => api.post('/crm/email/send', data),
  getEmailTemplates: () => api.get('/crm/email/templates'),
  
  // Reports
  getSalesOverview: (params: ReportParams) => api.get('/crm/reports/sales-overview', { params }),
  getConversionFunnel: (params: ReportParams) => api.get('/crm/reports/conversion-funnel', { params }),
};
```

**3. State Management (Zustand):**

```typescript
// frontend/src/store/crmStore.ts
interface CRMState {
  customers: Customer[];
  selectedCustomer: Customer | null;
  tasks: Task[];
  offers: Offer[];
  
  // Actions
  fetchCustomers: (filters?: CustomerFilters) => Promise<void>;
  selectCustomer: (id: number) => Promise<void>;
  createCustomer: (data: CustomerCreate) => Promise<Customer>;
  updateCustomer: (id: number, data: CustomerUpdate) => Promise<Customer>;
  deleteCustomer: (id: number) => Promise<void>;
  
  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  updateTaskStatus: (id: number, status: string) => Promise<void>;
}

export const useCRMStore = create<CRMState>((set, get) => ({
  customers: [],
  selectedCustomer: null,
  tasks: [],
  offers: [],
  
  fetchCustomers: async (filters) => {
    const customers = await crmService.getCustomers(filters);
    set({ customers });
  },
  
  // ... other actions
}));
```

### Key Migration Considerations:

1. **Database Migration:**
   - Keep SQLite for development
   - Consider PostgreSQL for production
   - Use Alembic for schema migrations

2. **Authentication:**
   - Implement JWT-based auth
   - Role-based access control (RBAC)
   - Secure customer data access

3. **File Storage:**
   - Move from filesystem to cloud storage (S3, Azure Blob)
   - Implement secure file upload/download
   - Maintain document versioning

4. **Email System:**
   - Keep SMTP configuration
   - Add email queue for reliability
   - Implement retry logic

5. **Real-time Updates:**
   - Use WebSockets for live updates
   - Notify on task assignments
   - Alert on offer status changes

6. **Search & Filtering:**
   - Implement full-text search (PostgreSQL FTS or Elasticsearch)
   - Add advanced filtering UI
   - Support saved searches

7. **Reporting:**
   - Keep Plotly for visualizations
   - Add scheduled reports
   - Implement report caching

8. **Performance:**
   - Implement pagination (limit/offset or cursor-based)
   - Add caching layer (Redis)
   - Optimize database queries with indexes

---

## Summary

The CRM system is a mature, feature-rich application with:

- **15,000+ lines** of well-structured code
- **50+ modules** covering all CRM aspects
- **15+ database tables** with proper relationships
- **Complete workflows** for customer lifecycle management
- **Advanced features** like lead scoring, forecasting, reporting
- **Integration points** with solar calculator, PDF generation, email

**Migration Complexity:** Medium-High
- Well-organized code structure
- Clear separation of concerns
- Comprehensive feature set requires careful planning
- Database schema is well-designed and can be migrated incrementally

**Recommended Approach:**
1. Start with core customer/project management
2. Add offer tracking and task management
3. Implement email integration
4. Add advanced features (reporting, forecasting)
5. Integrate with other systems (PDF, calculator)

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-21  
**Author:** Kiro AI Assistant  
**Task Status:** ✅ Complete

