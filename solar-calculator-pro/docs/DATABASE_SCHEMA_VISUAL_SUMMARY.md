# Database Schema Visual Summary

**Task 98 - Database Schema Complete Extraction**  
**Date:** 2025-01-21

## 📊 Database at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                          │
│                   data/app_data.db                          │
│                   Schema Version: 14                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐         ┌────▼────┐        ┌────▼────┐
    │ Admin  │         │   CRM   │        │Products │
    │8 tables│         │16 tables│        │4 tables │
    └────────┘         └─────────┘        └─────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────▼─────┐   ┌────▼────┐
              │Knowledge  │   │  Sales  │
              │Base       │   │Forecast │
              │3 tables   │   │2 tables │
              └───────────┘   └─────────┘
```

## 🗂️ Table Distribution

| Domain | Tables | Percentage |
|--------|--------|------------|
| CRM System | 16 | 53% |
| Admin & Config | 8 | 27% |
| Products | 4 | 13% |
| Knowledge Base | 3 | 10% |
| Sales Forecasting | 2 | 7% |
| **Total** | **30+** | **100%** |

## 🔗 Relationship Density

```
High Connectivity (5+ relationships):
  ├─ customers (10 relationships)
  ├─ projects (7 relationships)
  └─ companies (3 relationships)

Medium Connectivity (2-4 relationships):
  ├─ crm_tags (2 relationships)
  ├─ kb_categories (2 relationships)
  └─ kb_articles (2 relationships)

Low Connectivity (0-1 relationships):
  ├─ products (0 relationships)
  ├─ heat_pumps (0 relationships)
  ├─ services (0 relationships)
  └─ admin_settings (0 relationships)
```

## 📈 Data Flow Visualization

### Customer Journey Flow
```
┌──────────────┐
│  crm_leads   │ Lead captured
└──────┬───────┘
       │ Convert
       ▼
┌──────────────┐
│  customers   │ Customer created
└──────┬───────┘
       │ Create project
       ▼
┌──────────────┐
│   projects   │ Project initiated
└──────┬───────┘
       │ Calculate
       ▼
┌──────────────────────┐
│project_calculations  │ Calculations stored
└──────┬───────────────┘
       │ Generate
       ▼
┌──────────────────────┐
│customer_documents    │ PDF/Documents saved
└──────────────────────┘
```

### Activity Tracking Flow
```
┌──────────────┐
│  customers   │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐   ┌──────────────┐
│  crm_tasks   │   │crm_activities│
└──────────────┘   └──────────────┘
       │                 │
       ▼                 ▼
┌──────────────┐   ┌──────────────┐
│crm_reminders │   │crm_appointments│
└──────────────┘   └──────────────┘
```

## 🔑 Key Metrics

### Primary Keys
- **All tables:** Auto-incrementing INTEGER
- **Total:** 30+ primary keys

### Unique Constraints
- **Total:** 8 unique constraints
- **Most common:** model_name, name, brand_name

### Foreign Keys
- **Total:** 22 foreign key relationships
- **Most referenced:** customers (10x), projects (7x)

### Indexes
- **Explicit indexes:** 2
- **Auto-indexed (PK/UK):** 38+
- **Recommended additions:** 10+

## 📦 Storage Patterns

### JSON Storage (TEXT columns)
```
admin_settings.value          → Configuration objects
products.specifications       → Product specs
project_data                  → Project configuration
calculation_data              → Calculation results
widget_config                 → Dashboard config
tags                          → Tag arrays
```

### BLOB Storage
```
pdf_templates.image_data      → Template images
company_image_templates.image_data → Company images
```

### File System Storage
```
data/customer_docs/
  └─ customer_{id}/
      ├─ document1.pdf
      ├─ image1.jpg
      └─ offer.pdf
```

## 🎯 Critical Tables

### Top 5 Most Important Tables

1. **customers** (10 relationships)
   - Core CRM entity
   - Links to all CRM features

2. **projects** (7 relationships)
   - Central project management
   - Links calculations and documents

3. **project_calculations** (2 relationships)
   - Stores all calculation results
   - Versioned calculation history

4. **admin_settings** (0 relationships)
   - Application configuration
   - Critical for app behavior

5. **products** (0 relationships)
   - Product catalog
   - Essential for calculations

## 🚀 Migration Priority

### Phase 1: Core Tables (High Priority)
```
✓ admin_settings
✓ customers
✓ projects
✓ project_calculations
✓ products
```

### Phase 2: CRM Tables (Medium Priority)
```
✓ crm_tasks
✓ crm_activities
✓ crm_reminders
✓ crm_tags
✓ customer_tags
```

### Phase 3: Extended Features (Low Priority)
```
✓ crm_leads
✓ crm_appointments
✓ sales_targets
✓ sales_forecasts
✓ kb_* tables
```

## 📋 Checklist Status

- [x] Extract all SQLAlchemy models (N/A - uses raw SQL)
- [x] Document all table relationships
- [x] Map all indexes and constraints
- [x] Extract migration history
- [x] Document stored procedures (N/A - SQLite)
- [x] Create complete ER diagrams

## 🎉 Task Complete!

All database schema extraction tasks completed successfully. Ready for FastAPI migration!

