# Complete Database Schema Extraction

**Task 98 - Database Schema Complete Extraction**  
**Date:** 2025-01-21  
**Status:** Complete  
**Requirements:** 5.1, 6.1

## Executive Summary

This document provides a complete extraction of the database schema from the legacy Streamlit application. The application uses **SQLite3** with raw SQL queries (not SQLAlchemy ORM). The database consists of **30+ tables** across multiple functional domains including CRM, product management, PDF generation, admin settings, and more.

## Database Technology Stack

- **Database Engine:** SQLite3
- **ORM:** None (Raw SQL with sqlite3.Connection)
- **Row Factory:** sqlite3.Row (for dict-like access)
- **Database File:** `data/app_data.db`
- **Schema Version:** 14 (tracked via `DB_SCHEMA_VERSION` constant)

## Database Location and Structure

```
project_root/
├── data/
│   ├── app_data.db              # Main SQLite database
│   └── customer_docs/           # File storage for customer documents
│       └── customer_{id}/       # Per-customer document folders
├── database.py                  # Main database module
├── product_db.py               # Product-specific database operations
├── brand_logo_db.py            # Brand logo management
└── crm/                        # CRM-specific database operations
```

## Core Database Tables

### 1. Admin Settings Table
**Table:** `admin_settings`  
**Purpose:** Key-value store for application-wide configuration


```sql
CREATE TABLE IF NOT EXISTS admin_settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

**Columns:**
- `key` (TEXT, PRIMARY KEY): Setting identifier
- `value` (TEXT): JSON-encoded or string value

**Key Settings Stored:**
- `pricing_calculation_mode`: "standard" | "matrix"
- `price_matrix_csv_data`: CSV data for price matrix
- `feed_in_tariffs`: Feed-in tariff configuration (JSON)
- `global_constants`: Application-wide constants (JSON)
- `visualization_settings`: Chart and visualization config (JSON)
- `pdf_design_settings`: PDF styling configuration (JSON)
- `brand_logos`: Map of brand names to base64 logos (JSON)
- `active_company_id`: Currently active company ID

**Indexes:** None (PRIMARY KEY on `key`)

**Foreign Keys:** None

### 2. Products Table
**Table:** `products`  
**Purpose:** Product catalog for solar modules, inverters, batteries, etc.

```sql
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    manufacturer TEXT,
    model_name TEXT NOT NULL UNIQUE,
    price_euro REAL,
    datasheet_link TEXT,
    image_url TEXT,
    specifications TEXT,
    created_at TEXT,
    updated_at TEXT
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Auto-incrementing product ID
- `category` (TEXT, NOT NULL): Product category (e.g., "PV Module", "Inverter")
- `manufacturer` (TEXT): Manufacturer name
- `model_name` (TEXT, NOT NULL, UNIQUE): Product model identifier
- `price_euro` (REAL): Product price in euros
- `datasheet_link` (TEXT): URL to product datasheet
- `image_url` (TEXT): URL to product image
- `specifications` (TEXT): JSON-encoded product specifications
- `created_at` (TEXT): Creation timestamp
- `updated_at` (TEXT): Last update timestamp

**Indexes:** 
- UNIQUE constraint on `model_name`

**Foreign Keys:** None


### 3. Companies Table
**Table:** `companies`  
**Purpose:** Multi-company support for different business entities

```sql
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    logo_base64 TEXT,
    street TEXT,
    zip_code TEXT,
    city TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Company ID
- `name` (TEXT, NOT NULL, UNIQUE): Company name
- `logo_base64` (TEXT): Base64-encoded company logo
- `street`, `zip_code`, `city` (TEXT): Address fields
- `phone`, `email`, `website` (TEXT): Contact information
- `is_default` (INTEGER): 1 if default company, 0 otherwise
- `created_at`, `updated_at` (TEXT): Timestamps

**Indexes:** 
- UNIQUE constraint on `name`

**Foreign Keys:** None

**Business Rules:**
- Only one company should have `is_default = 1`
- Used for multi-company PDF generation and branding

### 4. Company Documents Table
**Table:** `company_documents`  
**Purpose:** File attachments for companies (logos, templates, etc.)

```sql
CREATE TABLE IF NOT EXISTS company_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    doc_type TEXT,
    display_name TEXT,
    file_name TEXT,
    absolute_file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Document ID
- `company_id` (INTEGER, NOT NULL): Reference to companies table
- `doc_type` (TEXT): Document type (e.g., "logo", "template")
- `display_name` (TEXT): User-friendly document name
- `file_name` (TEXT): Original filename
- `absolute_file_path` (TEXT): Path to file on disk
- `uploaded_at` (TIMESTAMP): Upload timestamp

**Indexes:** None

**Foreign Keys:**
- `company_id` → `companies(id)`


### 5. PDF Templates Table
**Table:** `pdf_templates`  
**Purpose:** Store PDF template configurations

```sql
CREATE TABLE IF NOT EXISTS pdf_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_type TEXT NOT NULL,
    name TEXT NOT NULL,
    content TEXT,
    image_data BLOB,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Template ID
- `template_type` (TEXT, NOT NULL): Type of template (e.g., "offer", "invoice")
- `name` (TEXT, NOT NULL): Template name
- `content` (TEXT): Template content (JSON or text)
- `image_data` (BLOB): Binary image data for template
- `created_at`, `updated_at` (TEXT): Timestamps

**Indexes:** None

**Foreign Keys:** None

### 6. Company Text Templates Table
**Table:** `company_text_templates`  
**Purpose:** Company-specific text templates for PDFs

```sql
CREATE TABLE IF NOT EXISTS company_text_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    template_key TEXT NOT NULL,
    template_text TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Template ID
- `company_id` (INTEGER, NOT NULL): Reference to companies table
- `template_key` (TEXT, NOT NULL): Template identifier key
- `template_text` (TEXT): Template text content
- `created_at`, `updated_at` (TEXT): Timestamps

**Indexes:** None

**Foreign Keys:**
- `company_id` → `companies(id)`

### 7. Company Image Templates Table
**Table:** `company_image_templates`  
**Purpose:** Company-specific image templates for PDFs

```sql
CREATE TABLE IF NOT EXISTS company_image_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    template_key TEXT NOT NULL,
    image_data BLOB,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Template ID
- `company_id` (INTEGER, NOT NULL): Reference to companies table
- `template_key` (TEXT, NOT NULL): Template identifier key
- `image_data` (BLOB): Binary image data
- `created_at`, `updated_at` (TEXT): Timestamps

**Indexes:** None

**Foreign Keys:**
- `company_id` → `companies(id)`


## CRM Tables

### 8. Customers Table
**Table:** `customers`  
**Purpose:** Core customer/contact management

```sql
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salutation TEXT,
    title TEXT,
    first_name TEXT,
    last_name TEXT,
    company_name TEXT,
    street TEXT,
    zip_code TEXT,
    city TEXT,
    phone TEXT,
    mobile TEXT,
    email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lead_source TEXT,
    lead_status TEXT,
    assigned_to TEXT,
    last_contact_date TEXT,
    next_follow_up_date TEXT,
    customer_value REAL,
    tags TEXT
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Customer ID
- `salutation`, `title`, `first_name`, `last_name` (TEXT): Personal information
- `company_name` (TEXT): Company name if business customer
- `street`, `zip_code`, `city` (TEXT): Address
- `phone`, `mobile`, `email` (TEXT): Contact information
- `notes` (TEXT): Free-form notes
- `created_at`, `updated_at` (TIMESTAMP): Timestamps
- `lead_source` (TEXT): Where lead came from
- `lead_status` (TEXT): Current lead status
- `assigned_to` (TEXT): Assigned sales person
- `last_contact_date`, `next_follow_up_date` (TEXT): Contact tracking
- `customer_value` (REAL): Estimated customer value
- `tags` (TEXT): JSON array of tags

**Indexes:** None

**Foreign Keys:** None

### 9. Projects Table
**Table:** `projects`  
**Purpose:** Track customer projects (solar installations, etc.)

```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    project_name TEXT,
    project_type TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_data TEXT,
    notes TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Project ID
- `customer_id` (INTEGER, NOT NULL): Reference to customers table
- `project_name` (TEXT): Project name
- `project_type` (TEXT): Type (e.g., "solar", "heatpump")
- `status` (TEXT): Project status
- `created_at`, `updated_at` (TIMESTAMP): Timestamps
- `project_data` (TEXT): JSON-encoded project data
- `notes` (TEXT): Project notes

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`


### 10. Customer Documents Table
**Table:** `customer_documents`  
**Purpose:** File attachments for customers (PDFs, images, etc.)

```sql
CREATE TABLE IF NOT EXISTS customer_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    doc_type TEXT,
    display_name TEXT,
    file_name TEXT,
    absolute_file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Document ID
- `customer_id` (INTEGER, NOT NULL): Reference to customers table
- `project_id` (INTEGER): Optional reference to projects table
- `doc_type` (TEXT): Document type (e.g., "offer_pdf", "image", "note")
- `display_name` (TEXT): User-friendly name
- `file_name` (TEXT): Original filename
- `absolute_file_path` (TEXT): Relative path from data directory
- `uploaded_at` (TIMESTAMP): Upload timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `project_id` → `projects(id)` (implicit, not enforced)

### 11. Project Calculations Table
**Table:** `project_calculations`  
**Purpose:** Store calculation results and versions for projects

```sql
CREATE TABLE IF NOT EXISTS project_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    calculation_data TEXT NOT NULL,
    calculation_type TEXT,
    is_main_offer INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    notes TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Calculation ID
- `project_id` (INTEGER, NOT NULL): Reference to projects table
- `customer_id` (INTEGER, NOT NULL): Reference to customers table
- `version` (INTEGER): Calculation version number
- `calculation_data` (TEXT): JSON with all calculation results
- `calculation_type` (TEXT): Type ("pv", "heatpump", "combined")
- `is_main_offer` (INTEGER): 1 if main offer, 0 otherwise
- `created_at` (TIMESTAMP): Creation timestamp
- `created_by` (TEXT): User who created calculation
- `notes` (TEXT): Calculation notes

**Indexes:**
- `idx_project_calculations_project_id` on `project_id`
- `idx_project_calculations_customer_id` on `customer_id`

**Foreign Keys:**
- `project_id` → `projects(id)`
- `customer_id` → `customers(id)`


### 12. CRM Tasks Table
**Table:** `crm_tasks`  
**Purpose:** Task management for customer follow-ups

```sql
CREATE TABLE IF NOT EXISTS crm_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    customer_id INTEGER,
    project_id INTEGER,
    assigned_to TEXT,
    due_date TEXT,
    priority TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Task ID
- `title` (TEXT, NOT NULL): Task title
- `description` (TEXT): Task description
- `customer_id` (INTEGER): Reference to customers table
- `project_id` (INTEGER): Reference to projects table
- `assigned_to` (TEXT): Assigned user
- `due_date` (TEXT): Due date
- `priority` (TEXT): Priority level
- `status` (TEXT): Task status (default: "open")
- `created_at` (TIMESTAMP): Creation timestamp
- `completed_at` (TIMESTAMP): Completion timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `project_id` → `projects(id)`

### 13. CRM Activities Table
**Table:** `crm_activities`  
**Purpose:** Activity log and notes for customers

```sql
CREATE TABLE IF NOT EXISTS crm_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    activity_type TEXT,
    subject TEXT,
    description TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Activity ID
- `customer_id` (INTEGER, NOT NULL): Reference to customers table
- `project_id` (INTEGER): Reference to projects table
- `activity_type` (TEXT): Type (e.g., "call", "email", "meeting", "note")
- `subject` (TEXT): Activity subject
- `description` (TEXT): Activity description
- `created_by` (TEXT): User who created activity
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `project_id` → `projects(id)`


### 14. CRM Reminders Table
**Table:** `crm_reminders`  
**Purpose:** Automated reminders for follow-ups

```sql
CREATE TABLE IF NOT EXISTS crm_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_type TEXT NOT NULL,
    customer_id INTEGER,
    project_id INTEGER,
    reminder_date TEXT NOT NULL,
    message TEXT,
    is_sent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Reminder ID
- `reminder_type` (TEXT, NOT NULL): Type of reminder
- `customer_id` (INTEGER): Reference to customers table
- `project_id` (INTEGER): Reference to projects table
- `reminder_date` (TEXT, NOT NULL): When to send reminder
- `message` (TEXT): Reminder message
- `is_sent` (INTEGER): 1 if sent, 0 otherwise
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `project_id` → `projects(id)`

### 15. CRM Tags Table
**Table:** `crm_tags`  
**Purpose:** Tag definitions for customer segmentation

```sql
CREATE TABLE IF NOT EXISTS crm_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Tag ID
- `name` (TEXT, NOT NULL, UNIQUE): Tag name
- `color` (TEXT): Tag color (hex code)
- `description` (TEXT): Tag description
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:**
- UNIQUE constraint on `name`

**Foreign Keys:** None

### 16. Customer Tags Table (Junction Table)
**Table:** `customer_tags`  
**Purpose:** Many-to-many relationship between customers and tags

```sql
CREATE TABLE IF NOT EXISTS customer_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(tag_id) REFERENCES crm_tags(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Junction ID
- `customer_id` (INTEGER, NOT NULL): Reference to customers table
- `tag_id` (INTEGER, NOT NULL): Reference to crm_tags table
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `tag_id` → `crm_tags(id)`


### 17. CRM Leads Table
**Table:** `crm_leads`  
**Purpose:** Lead management and pipeline tracking

```sql
CREATE TABLE IF NOT EXISTS crm_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    lead_source TEXT,
    lead_status TEXT DEFAULT 'new',
    pipeline_stage TEXT,
    estimated_value REAL,
    probability INTEGER,
    expected_close_date TEXT,
    assigned_to TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    converted_to_customer_id INTEGER,
    FOREIGN KEY(converted_to_customer_id) REFERENCES customers(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Lead ID
- `company_name` (TEXT, NOT NULL): Company name
- `contact_person` (TEXT): Contact person name
- `email`, `phone` (TEXT): Contact information
- `lead_source` (TEXT): Lead source
- `lead_status` (TEXT): Status (default: "new")
- `pipeline_stage` (TEXT): Current pipeline stage
- `estimated_value` (REAL): Estimated deal value
- `probability` (INTEGER): Win probability percentage
- `expected_close_date` (TEXT): Expected close date
- `assigned_to` (TEXT): Assigned sales person
- `notes` (TEXT): Lead notes
- `created_at`, `updated_at` (TIMESTAMP): Timestamps
- `converted_to_customer_id` (INTEGER): Reference to customers table if converted

**Indexes:** None

**Foreign Keys:**
- `converted_to_customer_id` → `customers(id)`

### 18. CRM Appointments Table
**Table:** `crm_appointments`  
**Purpose:** Calendar and appointment management

```sql
CREATE TABLE IF NOT EXISTS crm_appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    start_datetime TEXT NOT NULL,
    end_datetime TEXT NOT NULL,
    location TEXT,
    customer_id INTEGER,
    project_id INTEGER,
    assigned_to TEXT,
    appointment_type TEXT,
    status TEXT DEFAULT 'scheduled',
    reminder_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Appointment ID
- `title` (TEXT, NOT NULL): Appointment title
- `description` (TEXT): Appointment description
- `start_datetime`, `end_datetime` (TEXT, NOT NULL): Start and end times
- `location` (TEXT): Appointment location
- `customer_id` (INTEGER): Reference to customers table
- `project_id` (INTEGER): Reference to projects table
- `assigned_to` (TEXT): Assigned user
- `appointment_type` (TEXT): Type of appointment
- `status` (TEXT): Status (default: "scheduled")
- `reminder_minutes` (INTEGER): Minutes before to send reminder
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `customer_id` → `customers(id)`
- `project_id` → `projects(id)`


### 19. User Dashboard Settings Table
**Table:** `user_dashboard_settings`  
**Purpose:** Per-user dashboard widget configuration

```sql
CREATE TABLE IF NOT EXISTS user_dashboard_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    widget_config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Settings ID
- `user_id` (TEXT, NOT NULL, UNIQUE): User identifier
- `widget_config` (TEXT): JSON configuration for dashboard widgets
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Indexes:**
- UNIQUE constraint on `user_id`

**Foreign Keys:** None

### 20. Sales Targets Table
**Table:** `sales_targets`  
**Purpose:** Sales targets for forecasting

```sql
CREATE TABLE IF NOT EXISTS sales_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_name TEXT NOT NULL,
    target_period TEXT,
    start_date TEXT,
    end_date TEXT,
    target_revenue REAL,
    target_units INTEGER,
    assigned_to TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Target ID
- `target_name` (TEXT, NOT NULL): Target name
- `target_period` (TEXT): Period (e.g., "Q1 2024", "2024")
- `start_date`, `end_date` (TEXT): Target period dates
- `target_revenue` (REAL): Revenue target
- `target_units` (INTEGER): Units target
- `assigned_to` (TEXT): Assigned sales person/team
- `notes` (TEXT): Target notes
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Indexes:** None

**Foreign Keys:** None

### 21. Sales Forecasts Table
**Table:** `sales_forecasts`  
**Purpose:** Sales forecasting data

```sql
CREATE TABLE IF NOT EXISTS sales_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER,
    forecast_date TEXT NOT NULL,
    forecasted_revenue REAL,
    forecasted_units INTEGER,
    confidence_level TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(target_id) REFERENCES sales_targets(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Forecast ID
- `target_id` (INTEGER): Reference to sales_targets table
- `forecast_date` (TEXT, NOT NULL): Date of forecast
- `forecasted_revenue` (REAL): Forecasted revenue
- `forecasted_units` (INTEGER): Forecasted units
- `confidence_level` (TEXT): Confidence level
- `notes` (TEXT): Forecast notes
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `target_id` → `sales_targets(id)`


## Knowledge Base Tables

### 22. KB Categories Table
**Table:** `kb_categories`  
**Purpose:** Hierarchical categories for knowledge base

```sql
CREATE TABLE IF NOT EXISTS kb_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_id) REFERENCES kb_categories(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Category ID
- `name` (TEXT, NOT NULL): Category name
- `parent_id` (INTEGER): Parent category ID (for hierarchy)
- `description` (TEXT): Category description
- `sort_order` (INTEGER): Display order
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `parent_id` → `kb_categories(id)` (self-referencing)

### 23. KB Articles Table
**Table:** `kb_articles`  
**Purpose:** Knowledge base articles

```sql
CREATE TABLE IF NOT EXISTS kb_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category_id INTEGER,
    author TEXT,
    status TEXT DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES kb_categories(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Article ID
- `title` (TEXT, NOT NULL): Article title
- `content` (TEXT, NOT NULL): Article content (markdown/HTML)
- `category_id` (INTEGER): Reference to kb_categories table
- `author` (TEXT): Article author
- `status` (TEXT): Status (default: "draft")
- `view_count` (INTEGER): Number of views
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Indexes:** None

**Foreign Keys:**
- `category_id` → `kb_categories(id)`

### 24. KB Ratings Table
**Table:** `kb_ratings`  
**Purpose:** Article ratings and feedback

```sql
CREATE TABLE IF NOT EXISTS kb_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    feedback TEXT,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(article_id) REFERENCES kb_articles(id)
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Rating ID
- `article_id` (INTEGER, NOT NULL): Reference to kb_articles table
- `rating` (INTEGER, NOT NULL): Rating value (e.g., 1-5)
- `feedback` (TEXT): User feedback
- `user_id` (TEXT): User who rated
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes:** None

**Foreign Keys:**
- `article_id` → `kb_articles(id)`


## Product-Specific Tables

### 25. Heat Pumps Table
**Table:** `heat_pumps`  
**Purpose:** Heat pump product catalog

```sql
CREATE TABLE IF NOT EXISTS heat_pumps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL UNIQUE,
    manufacturer TEXT,
    heating_capacity_kw REAL,
    cop_rating REAL,
    price_euro REAL,
    datasheet_link TEXT,
    specifications TEXT,
    created_at TEXT,
    updated_at TEXT
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Heat pump ID
- `model_name` (TEXT, NOT NULL, UNIQUE): Model identifier
- `manufacturer` (TEXT): Manufacturer name
- `heating_capacity_kw` (REAL): Heating capacity in kW
- `cop_rating` (REAL): Coefficient of Performance
- `price_euro` (REAL): Price in euros
- `datasheet_link` (TEXT): URL to datasheet
- `specifications` (TEXT): JSON-encoded specifications
- `created_at`, `updated_at` (TEXT): Timestamps

**Indexes:**
- UNIQUE constraint on `model_name`

**Foreign Keys:** None

### 26. Brand Logos Table
**Table:** `brand_logos`  
**Purpose:** Brand logo management

```sql
CREATE TABLE IF NOT EXISTS brand_logos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE,
    logo_base64 TEXT,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Logo ID
- `brand_name` (TEXT, NOT NULL, UNIQUE): Brand name
- `logo_base64` (TEXT): Base64-encoded logo image
- `logo_url` (TEXT): URL to logo image
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Indexes:**
- UNIQUE constraint on `brand_name`

**Foreign Keys:** None

### 27. Services Table
**Table:** `services`  
**Purpose:** Additional services catalog

```sql
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price_euro REAL,
    category TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Service ID
- `name` (TEXT, NOT NULL): Service name
- `description` (TEXT): Service description
- `price_euro` (REAL): Service price
- `category` (TEXT): Service category
- `is_active` (INTEGER): 1 if active, 0 if inactive
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

**Indexes:** None

**Foreign Keys:** None


### 28. Products Complete Table
**Table:** `products_complete`  
**Purpose:** Extended product catalog with additional attributes

```sql
CREATE TABLE IF NOT EXISTS products_complete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategorie TEXT NOT NULL,
    hersteller TEXT,
    modellname TEXT NOT NULL UNIQUE,
    preis_euro REAL,
    datenblatt_link TEXT,
    bild_url TEXT,
    spezifikationen TEXT,
    created_at TEXT,
    updated_at TEXT,
    additional_attributes TEXT
)
```

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Product ID
- `kategorie` (TEXT, NOT NULL): Product category (German)
- `hersteller` (TEXT): Manufacturer (German)
- `modellname` (TEXT, NOT NULL, UNIQUE): Model name (German)
- `preis_euro` (REAL): Price in euros
- `datenblatt_link` (TEXT): Datasheet link
- `bild_url` (TEXT): Image URL
- `spezifikationen` (TEXT): JSON specifications
- `created_at`, `updated_at` (TEXT): Timestamps
- `additional_attributes` (TEXT): JSON for extra attributes

**Indexes:**
- UNIQUE constraint on `modellname`

**Foreign Keys:** None

**Note:** This appears to be a German-language variant of the products table.

## Database Relationships

### Entity Relationship Diagram (Textual)

```
companies (1) ----< (N) company_documents
companies (1) ----< (N) company_text_templates
companies (1) ----< (N) company_image_templates

customers (1) ----< (N) projects
customers (1) ----< (N) customer_documents
customers (1) ----< (N) crm_tasks
customers (1) ----< (N) crm_activities
customers (1) ----< (N) crm_reminders
customers (1) ----< (N) customer_tags
customers (1) <---- (1) crm_leads (converted_to_customer_id)
customers (1) ----< (N) crm_appointments

projects (1) ----< (N) customer_documents
projects (1) ----< (N) project_calculations
projects (1) ----< (N) crm_tasks
projects (1) ----< (N) crm_activities
projects (1) ----< (N) crm_reminders
projects (1) ----< (N) crm_appointments

crm_tags (1) ----< (N) customer_tags

kb_categories (1) ----< (N) kb_categories (self-referencing)
kb_categories (1) ----< (N) kb_articles

kb_articles (1) ----< (N) kb_ratings

sales_targets (1) ----< (N) sales_forecasts
```

### Key Relationships

1. **Company → Documents**: One-to-many relationship for company files
2. **Customer → Projects**: One-to-many relationship for customer projects
3. **Customer → Documents**: One-to-many relationship for customer files
4. **Project → Calculations**: One-to-many for calculation versions
5. **Customer ↔ Tags**: Many-to-many through customer_tags junction table
6. **KB Categories**: Self-referencing hierarchy for nested categories


## Indexes and Constraints

### Primary Keys
All tables use auto-incrementing INTEGER primary keys (`id` column).

### Unique Constraints
- `admin_settings.key` - Ensures unique setting keys
- `products.model_name` - Prevents duplicate product models
- `companies.name` - Ensures unique company names
- `crm_tags.name` - Prevents duplicate tag names
- `user_dashboard_settings.user_id` - One dashboard config per user
- `heat_pumps.model_name` - Prevents duplicate heat pump models
- `brand_logos.brand_name` - Ensures unique brand names
- `products_complete.modellname` - Prevents duplicate product models

### Foreign Key Constraints
The database uses foreign key constraints for referential integrity:

1. **company_documents.company_id** → companies.id
2. **company_text_templates.company_id** → companies.id
3. **company_image_templates.company_id** → companies.id
4. **projects.customer_id** → customers.id
5. **customer_documents.customer_id** → customers.id
6. **project_calculations.project_id** → projects.id
7. **project_calculations.customer_id** → customers.id
8. **crm_tasks.customer_id** → customers.id
9. **crm_tasks.project_id** → projects.id
10. **crm_activities.customer_id** → customers.id
11. **crm_activities.project_id** → projects.id
12. **crm_reminders.customer_id** → customers.id
13. **crm_reminders.project_id** → projects.id
14. **customer_tags.customer_id** → customers.id
15. **customer_tags.tag_id** → crm_tags.id
16. **crm_leads.converted_to_customer_id** → customers.id
17. **crm_appointments.customer_id** → customers.id
18. **crm_appointments.project_id** → projects.id
19. **sales_forecasts.target_id** → sales_targets.id
20. **kb_categories.parent_id** → kb_categories.id (self-referencing)
21. **kb_articles.category_id** → kb_categories.id
22. **kb_ratings.article_id** → kb_articles.id

### Indexes
The following indexes are explicitly created:

1. **idx_project_calculations_project_id** on project_calculations(project_id)
2. **idx_project_calculations_customer_id** on project_calculations(customer_id)

**Note:** SQLite automatically creates indexes for PRIMARY KEY and UNIQUE constraints.

## Default Values

### Timestamp Defaults
Most tables use `CURRENT_TIMESTAMP` for `created_at` and `updated_at` columns.

### Status Defaults
- `crm_tasks.status` → "open"
- `crm_leads.lead_status` → "new"
- `crm_appointments.status` → "scheduled"
- `kb_articles.status` → "draft"

### Boolean Defaults (INTEGER 0/1)
- `companies.is_default` → 0
- `project_calculations.is_main_offer` → 0
- `crm_reminders.is_sent` → 0
- `services.is_active` → 1

### Numeric Defaults
- `project_calculations.version` → 1
- `kb_categories.sort_order` → 0
- `kb_articles.view_count` → 0


## Migration History

### Schema Version Tracking
The database uses a `DB_SCHEMA_VERSION` constant (currently 14) to track schema versions.

```python
DB_SCHEMA_VERSION = 14
```

### Version History (Inferred from Code)
Based on code comments and structure:

- **Version 1-13**: Historical versions (not documented in current code)
- **Version 14**: Current version with corrected column names and `last_modified` field

### Migration Approach
The application uses a **create-if-not-exists** approach rather than formal migrations:
- Tables are created with `CREATE TABLE IF NOT EXISTS`
- Schema changes are handled by:
  1. Checking if columns exist
  2. Using `ALTER TABLE ADD COLUMN` for new columns
  3. Manual data migration scripts when needed

### Known Migration Patterns

```python
# Example: Adding missing columns to existing tables
cursor.execute("PRAGMA table_info(customers)")
columns = [col[1] for col in cursor.fetchall()]
if 'lead_source' not in columns:
    cursor.execute("ALTER TABLE customers ADD COLUMN lead_source TEXT")
```

## Stored Procedures

**Note:** SQLite does not support stored procedures. All business logic is implemented in Python code.

## Triggers

**Note:** No triggers are explicitly defined in the current codebase. All data manipulation is handled through Python code.

## Views

**Note:** No views are explicitly defined in the current codebase. All queries are constructed dynamically in Python.

## Data Types Used

### SQLite Data Types
The database uses standard SQLite data types:

1. **INTEGER**: IDs, counts, boolean flags (0/1), percentages
2. **TEXT**: Strings, JSON data, timestamps (ISO 8601 format)
3. **REAL**: Floating-point numbers (prices, ratings, measurements)
4. **BLOB**: Binary data (images in pdf_templates and company_image_templates)

### JSON Storage
Many columns store JSON-encoded data as TEXT:
- `admin_settings.value` - Configuration objects
- `products.specifications` - Product specifications
- `project_data` - Project configuration
- `calculation_data` - Calculation results
- `widget_config` - Dashboard configuration
- `tags` - Array of tags

### Timestamp Format
Timestamps are stored as TEXT in ISO 8601 format:
```
YYYY-MM-DD HH:MM:SS
```


## Database Access Patterns

### Connection Management
```python
def get_db_connection() -> sqlite3.Connection | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn
```

### Row Factory
All connections use `sqlite3.Row` factory for dict-like column access:
```python
cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
row = cursor.fetchone()
customer_name = row['first_name']  # Dict-like access
```

### Transaction Handling
- Auto-commit is disabled by default
- Explicit `conn.commit()` required for changes
- No explicit transaction management (BEGIN/COMMIT/ROLLBACK)

### Error Handling
```python
try:
    conn = get_db_connection()
    # Database operations
    conn.commit()
except Exception as e:
    print(f"DB Error: {e}")
finally:
    if conn:
        conn.close()
```

## Performance Considerations

### Current Limitations
1. **No Query Optimization**: Most queries are simple SELECT/INSERT/UPDATE
2. **Limited Indexing**: Only 2 explicit indexes beyond primary keys
3. **No Connection Pooling**: New connection per operation
4. **No Prepared Statements**: Queries constructed dynamically
5. **JSON in TEXT**: No native JSON querying capabilities

### Recommended Optimizations for Migration

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_customers_email ON customers(email);
   CREATE INDEX idx_projects_status ON projects(status);
   CREATE INDEX idx_crm_tasks_status ON crm_tasks(status);
   CREATE INDEX idx_crm_tasks_due_date ON crm_tasks(due_date);
   CREATE INDEX idx_crm_activities_customer_id ON crm_activities(customer_id);
   CREATE INDEX idx_customer_documents_customer_id ON customer_documents(customer_id);
   ```

2. **Connection Pooling**: Implement connection pooling for FastAPI backend

3. **Prepared Statements**: Use parameterized queries consistently

4. **JSON Columns**: Consider PostgreSQL's JSONB for better JSON querying

5. **Full-Text Search**: Add FTS5 virtual tables for text search

## File Storage

### Document Storage Structure
```
data/
├── app_data.db
└── customer_docs/
    ├── customer_1/
    │   ├── document1.pdf
    │   └── image1.jpg
    ├── customer_2/
    │   └── offer.pdf
    └── ...
```

### File Path Storage
- **Absolute paths** stored in database (relative to `data/` directory)
- **File naming**: `{display_name}_{timestamp}.{ext}`
- **Security**: Filenames sanitized (no `/` or `\`)


## Database Initialization

### Initial Setup
```python
# Create data directory
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Create customer documents directory
CUSTOMER_DOCS_BASE_DIR = os.path.join(DATA_DIR, 'customer_docs')
os.makedirs(CUSTOMER_DOCS_BASE_DIR, exist_ok=True)
```

### Table Creation Order
Tables are created on-demand using `CREATE TABLE IF NOT EXISTS`. No specific order required due to deferred foreign key checking.

### Initial Data
Default admin settings are populated on first run:

```python
INITIAL_ADMIN_SETTINGS = {
    "pricing_calculation_mode": "standard",
    "feed_in_tariffs": {...},
    "global_constants": {...},
    "visualization_settings": {...},
    "pdf_design_settings": {...},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
    "title_options": ['Dr.', 'Prof.', 'Mag.', 'Ing.', ''],
    "active_company_id": None
}
```

## Database Backup and Restore

### Backup Function
```python
def backup_database(backup_path: str) -> bool:
    shutil.copy2(DB_PATH, backup_path)
```

### Restore Function
```python
def restore_database(backup_path: str) -> bool:
    shutil.copy2(backup_path, DB_PATH)
```

### Validation
```python
def validate_database_integrity() -> dict[str, Any]:
    # Runs PRAGMA integrity_check
    # Checks foreign key constraints
    # Identifies orphaned records
    # Detects duplicate data
```

## Database Statistics

### Available Metrics
```python
def get_database_statistics() -> dict[str, Any]:
    return {
        'admin_settings_count': int,
        'products_count': int,
        'companies_count': int,
        'company_documents_count': int,
        'pdf_templates_count': int,
        'database_size_mb': float,
        'schema_version': int
    }
```

## Migration Recommendations

### For FastAPI Backend

1. **Use SQLAlchemy ORM**:
   - Define models matching current schema
   - Use Alembic for migrations
   - Maintain backward compatibility

2. **Connection Pooling**:
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.pool import QueuePool
   
   engine = create_engine(
       f"sqlite:///{DB_PATH}",
       poolclass=QueuePool,
       pool_size=5,
       max_overflow=10
   )
   ```

3. **Async Support**:
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine
   
   engine = create_async_engine(
       f"sqlite+aiosqlite:///{DB_PATH}"
   )
   ```

4. **Type Safety**:
   - Use Pydantic models for validation
   - Define TypedDict for JSON columns
   - Add type hints to all database functions

5. **Query Optimization**:
   - Add indexes for frequently queried columns
   - Use eager loading for relationships
   - Implement pagination for large result sets

