# Data Migration Service Guide

## Task 235: Data Migration Implementation

This guide covers the complete data migration system for migrating from Streamlit SQLite to the new Electron application database.

## Overview

The migration service provides:
- SQLite to new database migration
- Data validation during migration
- Migration progress tracking UI
- Rollback functionality
- Automatic backup before migration
- Migration of all data types

## Quick Start

### Starting a Migration

```python
from backend.services.migration_service import MigrationService

# Initialize service
service = MigrationService(
    source_db_path="/path/to/streamlit/database.db",
    target_db_path="/path/to/electron/database.db",
    backup_dir="backups/migrations"
)

# Run full migration
report = service.run_full_migration()

# Check results
print(f"Status: {report.overall_status}")
print(f"Migrated: {report.migrated_records}/{report.total_records}")
```

### Using the API

```bash
# Start migration
curl -X POST http://localhost:8000/api/v1/migration/start \
  -H "Content-Type: application/json" \
  -d '{
    "source_db_path": "/path/to/source.db",
    "target_db_path": "/path/to/target.db"
  }'

# Check progress
curl http://localhost:8000/api/v1/migration/progress/{migration_id}

# Get report
curl http://localhost:8000/api/v1/migration/report/{migration_id}
```

## Data Types Migrated

| Data Type | Source Tables | Description |
|-----------|---------------|-------------|
| User Settings | user_settings, user_preferences, app_settings | User preferences and app configuration |
| Projects | projects, solar_projects, heatpump_projects | All project data |
| Customers | customers, crm_customers, contacts | CRM customer data |
| Products | products, pv_modules, inverters, batteries, heatpumps, wallboxes, accessories | Product catalog |
| Price Matrices | price_matrices, price_matrix_data, pricing_rules | Pricing data |

## Migration Process

### 1. Backup Creation

Before any migration, a backup is automatically created:

```python
backup_path = service.create_backup()
# Returns: "backups/migrations/backup_20241128_143022.db"
```

### 2. Data Validation

Each record is validated before migration:

```python
from backend.services.migration_service import DataValidator

# Validate user settings
errors = DataValidator.validate_user_settings({"user_id": "user1", "theme": "dark"})
# Returns: [] (no errors)

# Invalid data
errors = DataValidator.validate_user_settings({"theme": "dark"})
# Returns: ["Missing user_id"]
```

### 3. Migration Execution

Migrate specific data types or all at once:

```python
# Migrate specific type
progress = service.migrate_user_settings()
progress = service.migrate_projects()
progress = service.migrate_customers()
progress = service.migrate_products()
progress = service.migrate_price_matrices()

# Or migrate everything
report = service.run_full_migration()
```

### 4. Progress Tracking

Track migration progress in real-time:

```python
def progress_callback(progress):
    print(f"{progress.data_type}: {progress.migrated_records}/{progress.total_records}")

service.add_progress_callback(progress_callback)
service.run_full_migration()
```

### 5. Rollback

If something goes wrong, rollback to the backup:

```python
success = service.rollback(backup_path)
if success:
    print("Rollback completed successfully")
```

## API Endpoints

### POST /api/v1/migration/start

Start a new migration.

**Request:**
```json
{
  "source_db_path": "/path/to/source.db",
  "target_db_path": "/path/to/target.db",
  "backup_dir": "backups/migrations",
  "data_types": ["user_settings", "projects"]
}
```

**Response:**
```json
{
  "migration_id": "migration_20241128_143022_abc12345",
  "status": "in_progress",
  "message": "Migration started successfully",
  "started_at": "2024-11-28T14:30:22.123456"
}
```

### GET /api/v1/migration/progress/{migration_id}

Get migration progress.

**Response:**
```json
{
  "migration_id": "migration_20241128_143022_abc12345",
  "overall_status": "in_progress",
  "total_records": 1000,
  "migrated_records": 750,
  "failed_records": 5,
  "progress_percent": 75.0,
  "data_type_progress": {
    "user_settings": {
      "status": "completed",
      "total": 100,
      "migrated": 100,
      "failed": 0
    },
    "projects": {
      "status": "in_progress",
      "total": 500,
      "migrated": 350,
      "failed": 5
    }
  }
}
```

### POST /api/v1/migration/rollback

Rollback a migration.

**Request:**
```json
{
  "migration_id": "migration_20241128_143022_abc12345",
  "backup_path": null
}
```

### GET /api/v1/migration/report/{migration_id}

Get complete migration report.

### GET /api/v1/migration/list

List all migrations.

### GET /api/v1/migration/validate/{migration_id}

Validate a completed migration.

### DELETE /api/v1/migration/cleanup/{migration_id}

Clean up migration resources.

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Source database not found | Invalid path | Verify source_db_path |
| Table has more than one primary key | Schema conflict | Check table structure |
| Validation failed | Invalid data | Review validation_errors in report |

### Handling Failures

```python
report = service.run_full_migration()

if report.overall_status == MigrationStatus.FAILED:
    print("Migration failed!")
    print(f"Errors: {report.validation_errors}")
    
    # Rollback
    service.rollback(report.backup_path)
```

## Best Practices

1. **Always backup first** - The service does this automatically, but verify the backup exists
2. **Validate before migration** - Use DataValidator to check data quality
3. **Monitor progress** - Use callbacks or API to track progress
4. **Test with sample data** - Run migration on a test database first
5. **Keep backups** - Don't delete backups until migration is verified

## Migration Report

After migration, generate a detailed report:

```python
report = service.generate_report()

# Save to file
service.save_report("migration_report.json")
```

Report includes:
- Migration ID and timestamps
- Source and target database paths
- Backup location
- Total/migrated/failed record counts
- Progress by data type
- Validation errors
- Recommendations

## Integration with Frontend

The migration service integrates with the React frontend through:

1. **REST API** - For starting and monitoring migrations
2. **WebSocket** - For real-time progress updates (optional)
3. **Progress UI** - Display migration progress in the app

Example React integration:

```typescript
// Start migration
const response = await fetch('/api/v1/migration/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    source_db_path: sourcePath,
    target_db_path: targetPath
  })
});

const { migration_id } = await response.json();

// Poll for progress
const interval = setInterval(async () => {
  const progress = await fetch(`/api/v1/migration/progress/${migration_id}`);
  const data = await progress.json();
  
  updateProgressUI(data);
  
  if (data.overall_status === 'completed' || data.overall_status === 'failed') {
    clearInterval(interval);
  }
}, 1000);
```

## Requirements Coverage

This implementation satisfies:
- **5.1**: SQLite to new database migration
- **5.2**: Data validation during migration
- **5.3**: Migration progress tracking
- **5.4**: Rollback functionality
- **5.5**: Backup before migration
- **5.6**: Migration of all data types
- **5.7**: Migration report generation
