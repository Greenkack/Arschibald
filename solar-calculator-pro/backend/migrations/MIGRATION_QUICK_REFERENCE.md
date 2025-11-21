# Migration Quick Reference

## Quick Start

### Full Migration (Recommended)

```bash
python migrate_cli.py full /path/to/streamlit/data /path/to/electron/data
```

This runs all migration steps in sequence:
1. ✓ Create backup
2. ✓ Migrate databases
3. ✓ Migrate settings
4. ✓ Convert project data
5. ✓ Migrate user data
6. ✓ Validate migration

## Individual Migrations

### Database Only
```bash
python migrate_cli.py database source.db target.db
```

### Settings Only
```bash
python migrate_cli.py settings /source/settings /target/settings
```

### Projects Only
```bash
python migrate_cli.py projects /source/projects /target/projects
```

### Users Only
```bash
python migrate_cli.py users /source/users /target/users
```

## Python API

### Full Migration
```python
from migration_manager import MigrationManager
from pathlib import Path

manager = MigrationManager(
    source_path=Path("/path/to/source"),
    target_path=Path("/path/to/target")
)

report = manager.run_full_migration()
print(f"Success: {report['success']}")
```

### Database Migration
```python
from database_migrator import DatabaseMigrator

migrator = DatabaseMigrator(
    source_db=Path("source.db"),
    target_db=Path("target.db")
)

result = migrator.migrate()
validation = migrator.validate_migration()
```

### Settings Migration
```python
from settings_migrator import SettingsMigrator

migrator = SettingsMigrator(
    source_path=Path("/source/settings"),
    target_path=Path("/target/settings")
)

result = migrator.migrate()
```

### Project Conversion
```python
from project_data_converter import ProjectDataConverter

converter = ProjectDataConverter(
    source_path=Path("/source/projects"),
    target_path=Path("/target/projects")
)

result = converter.convert()
```

### User Migration
```python
from user_data_migrator import UserDataMigrator

migrator = UserDataMigrator(
    source_path=Path("/source/users"),
    target_path=Path("/target/users")
)

result = migrator.migrate()
```

## Common Patterns

### Custom Database Transformation

```python
from database_migrator import DatabaseMigrator

migrator = DatabaseMigrator(source_db, target_db)

# Add column mapping
migrator.add_schema_mapping("users", {
    "old_name": "new_name"
})

# Add data transformer
def transform_user(row):
    row['updated_at'] = datetime.now().isoformat()
    return row

migrator.add_data_transformer("users", transform_user)

result = migrator.migrate()
```

### Custom Project Conversion

```python
from project_data_converter import ProjectDataConverter

converter = ProjectDataConverter(source_path, target_path)

# Add custom conversion rule
def convert_solar_data(data):
    # Custom transformation
    return transformed_data

converter.add_conversion_rule("solar", convert_solar_data)

result = converter.convert()
```

## Validation

### Check Migration Success

```python
report = manager.run_full_migration()

if report['success']:
    print("✓ Migration successful")
else:
    print("✗ Migration failed")
    for error in report['errors']:
        print(f"  - {error}")
```

### Validate Individual Components

```python
# Database validation
db_validation = migrator.validate_migration()
print(f"Database: {'PASS' if db_validation['success'] else 'FAIL'}")

# Settings validation
settings_validation = settings_migrator.validate_migration()
print(f"Settings: {'PASS' if settings_validation['success'] else 'FAIL'}")

# Project validation
project_validation = converter.validate_conversion()
print(f"Projects: {'PASS' if project_validation['success'] else 'FAIL'}")

# User validation
user_validation = user_migrator.validate_migration()
print(f"Users: {'PASS' if user_validation['success'] else 'FAIL'}")
```

## Rollback

Automatic rollback on failure:

```python
report = manager.run_full_migration()

if not report['success']:
    if 'rollback' in report:
        print(f"Rollback: {report['rollback']['message']}")
```

Manual rollback:

```python
# Restore from backup
import shutil
shutil.copytree(backup_path, target_path)
```

## Logging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log to File

```python
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
```

## Error Handling

### Try-Catch Pattern

```python
try:
    report = manager.run_full_migration()
    if report['success']:
        print("Migration completed successfully")
    else:
        print("Migration completed with errors")
        for error in report['errors']:
            print(f"  - {error}")
except Exception as e:
    print(f"Migration failed: {str(e)}")
```

## Migration Report

### Access Report Data

```python
report = manager.run_full_migration()

# Overall status
print(f"Success: {report['success']}")
print(f"Started: {report['started_at']}")
print(f"Completed: {report['completed_at']}")

# Step details
for step in report['steps']:
    print(f"{step['step']}: {step['message']}")

# Errors
for error in report['errors']:
    print(f"Error: {error}")
```

### Save Report

```python
import json

with open('migration_report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

## Pre-Migration Checklist

- [ ] Backup source data
- [ ] Stop Streamlit application
- [ ] Verify disk space (2x source size)
- [ ] Check file permissions
- [ ] Review source data integrity

## Post-Migration Checklist

- [ ] Review migration report
- [ ] Validate all data
- [ ] Test application with migrated data
- [ ] Change default admin password
- [ ] Archive source data
- [ ] Delete backup (after verification)

## Default Admin User

After migration, if no users exist:

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

**⚠️ CHANGE PASSWORD IMMEDIATELY!**

## File Locations

### Source Files (Streamlit)
```
/path/to/streamlit/
├── *.db                    # Databases
├── .streamlit/config.toml  # Streamlit config
├── settings.json           # Settings
├── projects/               # Project data
└── users/                  # User data
```

### Target Files (Electron)
```
/path/to/electron/
├── *.db                    # Migrated databases
├── app_config.json         # App configuration
├── settings.json           # Consolidated settings
├── projects/               # Converted projects
├── users/                  # Migrated users
└── backups/                # Backup directory
```

## Performance Tips

1. **Run locally**: Copy data to local disk before migration
2. **Close applications**: Stop Streamlit and close database connections
3. **Sufficient space**: Ensure 2x source data size available
4. **Batch processing**: For very large datasets, migrate in batches

## Troubleshooting

### Database Locked
```bash
# Check for open connections
lsof /path/to/database.db

# Kill processes if needed
kill -9 <PID>
```

### Permission Denied
```bash
# Check permissions
ls -la /path/to/data

# Fix permissions
chmod -R 755 /path/to/data
```

### Out of Space
```bash
# Check disk space
df -h

# Clean up if needed
rm -rf /path/to/old/backups
```

## Support Commands

### Check Python Version
```bash
python --version  # Should be 3.10+
```

### Install Dependencies
```bash
pip install bcrypt pyyaml toml
```

### Run Tests
```bash
pytest tests/
```

### View Logs
```bash
tail -f migration_*.log
```

## Quick Validation

```bash
# Count records in database
sqlite3 target.db "SELECT COUNT(*) FROM users;"

# Check settings file
cat target/settings.json | python -m json.tool

# List projects
ls -la target/projects/

# Verify users
cat target/users/users.json | python -m json.tool
```

## Emergency Rollback

```bash
# Stop migration (Ctrl+C)
# Restore from backup
cp -r backups/YYYYMMDD_HHMMSS/source/* /path/to/target/
```

## Contact

For issues:
1. Check logs: `migration_*.log`
2. Check report: `migration_report.json`
3. Enable debug logging
4. Contact development team
