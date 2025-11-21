# Migration Scripts Documentation

This directory contains migration scripts for migrating data from the Streamlit application to the new Electron-based application.

## Overview

The migration system handles:
- **Database Migration** (Requirement 5.1): SQLite database schema and data migration
- **Settings Migration** (Requirement 5.2): Application settings and configuration
- **Project Data Conversion** (Requirement 5.3): Project-specific data transformation
- **User Data Migration** (Requirement 5.4): User accounts, preferences, and authentication

## Components

### 1. Migration Manager (`migration_manager.py`)

The main orchestrator that coordinates all migration tasks.

**Features:**
- Automatic backup creation before migration
- Sequential execution of all migration steps
- Comprehensive validation
- Automatic rollback on failure
- Detailed migration reporting

**Usage:**
```python
from migration_manager import MigrationManager

manager = MigrationManager(
    source_path=Path("/path/to/streamlit/data"),
    target_path=Path("/path/to/electron/data")
)

report = manager.run_full_migration()
```

### 2. Database Migrator (`database_migrator.py`)

Handles SQLite database migration with schema transformation support.

**Features:**
- Automatic table schema detection
- Column mapping and renaming
- Data transformation functions
- Record count validation
- Transaction management

**Usage:**
```python
from database_migrator import DatabaseMigrator

migrator = DatabaseMigrator(
    source_db=Path("source.db"),
    target_db=Path("target.db")
)

# Add schema mapping
migrator.add_schema_mapping("users", {
    "old_column": "new_column"
})

# Add data transformer
def transform_user(row):
    row['created_at'] = datetime.now().isoformat()
    return row

migrator.add_data_transformer("users", transform_user)

# Run migration
result = migrator.migrate()

# Validate
validation = migrator.validate_migration()
```

### 3. Settings Migrator (`settings_migrator.py`)

Migrates application settings from various formats (JSON, YAML, INI, TOML).

**Features:**
- Multi-format support (JSON, YAML, INI, TOML)
- Streamlit config to Electron config transformation
- Settings consolidation
- Format standardization to JSON

**Usage:**
```python
from settings_migrator import SettingsMigrator

migrator = SettingsMigrator(
    source_path=Path("/path/to/source/settings"),
    target_path=Path("/path/to/target/settings")
)

result = migrator.migrate()
validation = migrator.validate_migration()
```

### 4. Project Data Converter (`project_data_converter.py`)

Converts project-specific data to the new format.

**Features:**
- Project metadata transformation
- Calculation data conversion
- 3D visualization data migration
- PDF configuration migration
- File attachment copying

**Usage:**
```python
from project_data_converter import ProjectDataConverter

converter = ProjectDataConverter(
    source_path=Path("/path/to/source/projects"),
    target_path=Path("/path/to/target/projects")
)

result = converter.convert()
validation = converter.validate_conversion()
```

### 5. User Data Migrator (`user_data_migrator.py`)

Migrates user accounts and preferences with security considerations.

**Features:**
- Password hashing with bcrypt
- Role mapping
- User preferences migration
- Default admin creation
- Email validation

**Usage:**
```python
from user_data_migrator import UserDataMigrator

migrator = UserDataMigrator(
    source_path=Path("/path/to/source/users"),
    target_path=Path("/path/to/target/users")
)

result = migrator.migrate()
validation = migrator.validate_migration()
```

## CLI Tool

The `migrate_cli.py` provides a command-line interface for running migrations.

### Full Migration

```bash
python migrate_cli.py full /path/to/streamlit/data /path/to/electron/data
```

### Individual Migrations

```bash
# Database only
python migrate_cli.py database /path/to/source.db /path/to/target.db

# Settings only
python migrate_cli.py settings /path/to/source/settings /path/to/target/settings

# Projects only
python migrate_cli.py projects /path/to/source/projects /path/to/target/projects

# Users only
python migrate_cli.py users /path/to/source/users /path/to/target/users
```

## Migration Process

### 1. Pre-Migration Checklist

- [ ] Backup all source data
- [ ] Verify source data integrity
- [ ] Ensure sufficient disk space
- [ ] Stop Streamlit application
- [ ] Review migration logs directory

### 2. Running Migration

```bash
# Full migration with all steps
python migrate_cli.py full /path/to/streamlit/data /path/to/electron/data
```

### 3. Post-Migration Validation

The migration automatically validates:
- Database record counts
- File counts
- Data integrity (checksums)
- User account structure
- Settings format

### 4. Migration Report

After migration, a detailed report is saved to `migration_report.json`:

```json
{
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:05:00",
  "success": true,
  "steps": [
    {
      "step": "backup",
      "success": true,
      "message": "Backup created successfully: 1234 files"
    },
    {
      "step": "database_migration",
      "success": true,
      "message": "Migrated 5 databases, 25 tables, 10000 records"
    }
  ],
  "errors": []
}
```

## Rollback

If migration fails, automatic rollback is attempted:

1. Target directory is removed
2. Data is restored from backup
3. Rollback status is included in migration report

## Data Transformations

### Database Transformations

Example user table transformation:

```python
def user_transformer(row):
    # Add created_at if missing
    if 'created_at' not in row:
        row['created_at'] = datetime.now().isoformat()
    
    # Hash password if plain text
    if 'password' in row and not row['password'].startswith('$2b$'):
        import bcrypt
        row['password'] = bcrypt.hashpw(
            row['password'].encode(), 
            bcrypt.gensalt()
        ).decode()
    
    return row
```

### Settings Transformations

Streamlit theme to Electron theme:

```python
# Streamlit config
{
  "theme": {
    "base": "light",
    "primaryColor": "#1976d2"
  }
}

# Electron config
{
  "theme": {
    "mode": "light",
    "colors": {
      "primary": "#1976d2"
    }
  }
}
```

### Project Data Transformations

Old format:
```json
{
  "project_name": "Solar Project 1",
  "status": "active",
  "system_size": 10.5
}
```

New format:
```json
{
  "id": 1,
  "name": "Solar Project 1",
  "type": "solar",
  "status": "in_progress",
  "data": {
    "solar": {
      "system_size": 10.5
    }
  },
  "_migrated_at": "2024-01-01T10:00:00"
}
```

## Error Handling

All migration components include comprehensive error handling:

- **Try-catch blocks** around all critical operations
- **Detailed error logging** with stack traces
- **Error collection** in migration reports
- **Graceful degradation** - partial success is possible
- **Automatic rollback** on critical failures

## Logging

Migration logs are saved to:
- `migration_YYYYMMDD_HHMMSS.log` - Detailed log file
- Console output - Real-time progress
- `migration_report.json` - Structured report

Log levels:
- **INFO**: Normal progress messages
- **WARNING**: Non-critical issues
- **ERROR**: Failures that don't stop migration
- **CRITICAL**: Failures that stop migration

## Security Considerations

### Password Handling

- All passwords are hashed with bcrypt
- Plain text passwords are automatically hashed during migration
- Salt is generated for each password
- Minimum password strength is not enforced during migration (should be enforced in application)

### Default Admin User

If no users exist after migration, a default admin is created:
- **Username**: admin
- **Password**: admin123 (MUST BE CHANGED)
- **Role**: admin

**⚠️ IMPORTANT**: Change the default admin password immediately after migration!

### Data Encryption

- Database files are not encrypted during migration
- Sensitive data should be encrypted at application level
- Consider encrypting backup files

## Performance

### Optimization Tips

1. **Large Databases**: Use batch processing for tables with millions of records
2. **Network Storage**: Copy data locally before migration
3. **Parallel Processing**: Run independent migrations in parallel
4. **Incremental Migration**: Migrate in stages for very large datasets

### Expected Performance

- **Small dataset** (< 1GB): 1-5 minutes
- **Medium dataset** (1-10GB): 5-30 minutes
- **Large dataset** (> 10GB): 30+ minutes

## Troubleshooting

### Common Issues

**Issue**: Database migration fails with "database is locked"
**Solution**: Ensure source database is not in use

**Issue**: Settings migration fails with "invalid JSON"
**Solution**: Validate source JSON files manually

**Issue**: User migration creates default admin
**Solution**: Check if source user files exist and are readable

**Issue**: Validation fails with record count mismatch
**Solution**: Check migration logs for specific table issues

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

### Unit Tests

```bash
pytest tests/test_migration_manager.py
pytest tests/test_database_migrator.py
pytest tests/test_settings_migrator.py
pytest tests/test_project_data_converter.py
pytest tests/test_user_data_migrator.py
```

### Integration Tests

```bash
pytest tests/test_migration_integration.py
```

### Test Data

Test data is available in `tests/fixtures/`:
- `test_database.db` - Sample database
- `test_settings/` - Sample settings files
- `test_projects/` - Sample project data
- `test_users/` - Sample user data

## Requirements

### Python Dependencies

```
sqlite3 (built-in)
json (built-in)
pathlib (built-in)
bcrypt>=4.0.0
pyyaml>=6.0
toml>=0.10.2
```

### System Requirements

- Python 3.10+
- Sufficient disk space (2x source data size)
- Read/write permissions on source and target directories

## Support

For issues or questions:
1. Check migration logs
2. Review this documentation
3. Check migration report JSON
4. Enable debug logging
5. Contact development team

## Version History

- **1.0.0** (2024-01-01): Initial release
  - Database migration
  - Settings migration
  - Project data conversion
  - User data migration
  - CLI tool
  - Validation system
  - Rollback functionality
