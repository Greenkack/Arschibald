# Database Schema Quick Reference

**Task 98 - Database Schema Complete Extraction**  
**Date:** 2025-01-21

## Quick Stats

- **Database Engine:** SQLite3
- **Total Tables:** 30+
- **Schema Version:** 14
- **Database File:** `data/app_data.db`
- **ORM:** None (Raw SQL)

## Table Summary

| # | Table Name | Purpose | Key Columns | Relationships |
|---|------------|---------|-------------|---------------|
| 1 | admin_settings | App configuration | key (PK), value | None |
| 2 | products | Product catalog | id (PK), model_name (UK) | None |
| 3 | companies | Multi-company support | id (PK), name (UK) | → company_documents, company_text_templates, company_image_templates |
| 4 | company_documents | Company files | id (PK), company_id (FK) | companies ← |
| 5 | company_text_templates | Company text templates | id (PK), company_id (FK) | companies ← |
| 6 | company_image_templates | Company image templates | id (PK), company_id (FK) | companies ← |
| 7 | pdf_templates | PDF templates | id (PK), template_type | None |
| 8 | customers | Customer management | id (PK), email | → projects, customer_documents, crm_* |
| 9 | projects | Customer projects | id (PK), customer_id (FK) | customers ←, → project_calculations |
| 10 | customer_documents | Customer files | id (PK), customer_id (FK) | customers ←, projects ← |
| 11 | project_calculations | Calculation versions | id (PK), project_id (FK) | projects ←, customers ← |
| 12 | crm_tasks | Task management | id (PK), customer_id (FK) | customers ←, projects ← |
| 13 | crm_activities | Activity log | id (PK), customer_id (FK) | customers ←, projects ← |
| 14 | crm_reminders | Automated reminders | id (PK), customer_id (FK) | customers ←, projects ← |
| 15 | crm_tags | Tag definitions | id (PK), name (UK) | → customer_tags |
| 16 | customer_tags | Customer-tag junction | id (PK), customer_id, tag_id | customers ←, crm_tags ← |
| 17 | crm_leads | Lead management | id (PK), converted_to_customer_id | → customers |
| 18 | crm_appointments | Calendar/appointments | id (PK), customer_id (FK) | customers ←, projects ← |
| 19 | user_dashboard_settings | Dashboard config | id (PK), user_id (UK) | None |
| 20 | sales_targets | Sales targets | id (PK), target_name | → sales_forecasts |
| 21 | sales_forecasts | Sales forecasting | id (PK), target_id (FK) | sales_targets ← |
| 22 | kb_categories | KB categories | id (PK), parent_id (FK) | → kb_categories (self), → kb_articles |
| 23 | kb_articles | KB articles | id (PK), category_id (FK) | kb_categories ←, → kb_ratings |
| 24 | kb_ratings | Article ratings | id (PK), article_id (FK) | kb_articles ← |
| 25 | heat_pumps | Heat pump catalog | id (PK), model_name (UK) | None |
| 26 | brand_logos | Brand logos | id (PK), brand_name (UK) | None |
| 27 | services | Services catalog | id (PK), name | None |

## Common Queries

### Get Customer with Projects
```sql
SELECT c.*, p.id as project_id, p.project_name
FROM customers c
LEFT JOIN projects p ON c.id = p.customer_id
WHERE c.id = ?;
```

### Get Project with Latest Calculation
```sql
SELECT p.*, pc.calculation_data
FROM projects p
LEFT JOIN project_calculations pc ON p.id = pc.project_id
WHERE p.id = ?
ORDER BY pc.version DESC
LIMIT 1;
```

### Get Customer Documents
```sql
SELECT * FROM customer_documents
WHERE customer_id = ?
ORDER BY uploaded_at DESC;
```

### Get Active Tasks for Customer
```sql
SELECT * FROM crm_tasks
WHERE customer_id = ?
AND status != 'completed'
ORDER BY due_date ASC;
```

### Get Customer Tags
```sql
SELECT t.name, t.color
FROM crm_tags t
JOIN customer_tags ct ON t.id = ct.tag_id
WHERE ct.customer_id = ?;
```

## Key Functions

### Database Connection
```python
conn = get_db_connection()  # Returns sqlite3.Connection with Row factory
```

### Admin Settings
```python
save_admin_setting(key, value)  # Save setting
load_admin_setting(key, default)  # Load setting
```

### Customer Documents
```python
add_customer_document(customer_id, file_bytes, display_name, doc_type, project_id)
list_customer_documents(customer_id, project_id)
delete_customer_document(document_id)
```

### Database Maintenance
```python
backup_database(backup_path)  # Backup database
restore_database(backup_path)  # Restore database
validate_database_integrity()  # Check integrity
get_database_statistics()  # Get stats
```

## Migration Checklist

- [ ] Extract all table schemas
- [ ] Document all relationships
- [ ] Map all indexes and constraints
- [ ] Extract migration history
- [ ] Document stored procedures (N/A for SQLite)
- [ ] Create ER diagrams
- [ ] Define SQLAlchemy models
- [ ] Create Alembic migrations
- [ ] Test data migration
- [ ] Validate referential integrity

## Next Steps for FastAPI Migration

1. **Create SQLAlchemy Models** - Define ORM models matching schema
2. **Setup Alembic** - Initialize migration system
3. **Create Initial Migration** - Generate from existing schema
4. **Add Indexes** - Optimize frequently queried columns
5. **Implement Connection Pooling** - Use SQLAlchemy engine
6. **Add Async Support** - Use aiosqlite for async operations
7. **Create Pydantic Schemas** - Define request/response models
8. **Implement CRUD Operations** - Create service layer
9. **Add Data Validation** - Use Pydantic validators
10. **Test Migration** - Verify data integrity

