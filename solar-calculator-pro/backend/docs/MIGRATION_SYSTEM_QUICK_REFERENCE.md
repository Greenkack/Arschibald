# Database Migration System - Quick Reference

## Installation

```bash
cd solar-calculator-pro/backend
pip install sqlalchemy
```

## Basic Usage

### 1. Create Migration Manager

```python
from migrations.migration_manager import MigrationManager

manager = MigrationManager("sqlite:///database.db")
```

### 2. Create Migration

```python
from migrations.migration_manager import MigrationStep, MigrationType

migration = MigrationStep(
    id="001_add_column",
    name="Add Email Column",
    description="Add email to users",
    type=MigrationType.SCHEMA,
    up_sql="ALTER TABLE users ADD COLUMN email TEXT",
    down_sql="ALTER TABLE users DROP COLUMN email"
)
```

### 3. Execute Migration

```python
manager.register_migration(migration)
result = manager.migrate()
```

### 4. Rollback

```python
result = manager.rollback()
```

## Common Operations

### Schema Migration

```python
MigrationStep(
    id="001_create_table",
    type=MigrationType.SCHEMA,
    up_sql="CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)",
    down_sql="DROP TABLE products"
)
```

### Data Transformation

```python
from migrations.data_transformer import DataTransformer

def transform(session):
    transformer = DataTransformer(session)
    transformer.normalize_text('users', 'email', lowercase=True)
    return transformer.transformations_applied

MigrationStep(
    id="002_normalize",
    type=MigrationType.DATA,
    up_function=transform
)
```

### Add Validation

```python
from migrations.data_validator import DataValidator

def validate(session):
    validator = DataValidator(session)
    validator.add_not_null('users', 'email')
    return validator.validate()['valid']

MigrationStep(
    id="003_add_email",
    up_sql="ALTER TABLE users ADD COLUMN email TEXT NOT NULL",
    validation_function=validate
)
```

## Data Transformer Methods

```python
transformer = DataTransformer(session)

# Transform values
transformer.transform_column('users', 'email', lambda x: x.lower())

# Map values
transformer.map_values('users', 'status', {'0': 'inactive', '1': 'active'})

# Convert types
transformer.convert_type('products', 'price', float)

# Normalize text
transformer.normalize_text('users', 'name', lowercase=True, strip=True)

# Split column
transformer.split_column('users', 'full_name', ['first_name', 'last_name'])

# Merge columns
transformer.merge_columns('users', ['first_name', 'last_name'], 'full_name')

# Remove duplicates
transformer.deduplicate_rows('users', ['email'], keep='first')
```

## Data Validator Methods

```python
validator = DataValidator(session)

# Structure validation
validator.add_table_exists('users')
validator.add_column_exists('users', 'email')

# Data integrity
validator.add_not_null('users', 'email')
validator.add_unique('users', 'email')

# Data types
validator.add_data_type('products', 'price', float)

# Value constraints
validator.add_range('products', 'price', 0, 10000)
validator.add_pattern('users', 'email', r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Relationships
validator.add_foreign_key('orders', 'user_id', 'users', 'id')

# Execute
result = validator.validate()
```

## Progress Tracking

```python
from migrations.progress_tracker import ProgressTracker, ProgressLogger

tracker = ProgressTracker(total_steps=3)
logger = ProgressLogger(tracker)

tracker.start_step("Step 1")
# ... work ...
tracker.complete_step()

tracker.start_step("Step 2")
tracker.update_step_progress(0.5)  # 50%
# ... work ...
tracker.complete_step()
```

## Advanced Features

### Dependency Management

```python
migration_1 = MigrationStep(id="001", ..., dependencies=[])
migration_2 = MigrationStep(id="002", ..., dependencies=["001"])
```

### Incremental Migration

```python
manager.migrate(target_version="002")
```

### Dry Run

```python
result = manager.migrate(dry_run=True)
```

### Check Status

```python
status = manager.get_migration_status()
print(f"Current: {status['current_version']}")
print(f"Pending: {status['pending_migrations']}")
```

### Validate Database

```python
validation = manager.validate_database()
if not validation['valid']:
    for issue in validation['issues']:
        print(f"{issue['severity']}: {issue['message']}")
```

### Export History

```python
manager.export_migration_history('history.json')
```

## Error Handling

```python
try:
    result = manager.migrate()
    if result['status'] == 'failed':
        print(f"Failed: {result['migrations_failed']}")
        for r in result['results']:
            if r['status'] == 'failed':
                print(f"  {r['step_id']}: {r['error_message']}")
except Exception as e:
    print(f"Migration error: {str(e)}")
```

## Best Practices

1. **Always include rollback**: Define `down_sql` or `down_function`
2. **Add validation**: Use `validation_function` to verify changes
3. **Use batch processing**: Set `batch_size` for large datasets
4. **Track progress**: Use `ProgressTracker` for long operations
5. **Test first**: Use `dry_run=True` before applying
6. **Handle errors**: Wrap in try/except and check results
7. **Document migrations**: Add clear `name` and `description`
8. **Version control**: Use sequential IDs (001, 002, 003...)

## Common Patterns

### Add Column with Default

```python
MigrationStep(
    id="001",
    up_sql="""
        ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active';
        UPDATE users SET status = 'active' WHERE status IS NULL;
    """,
    down_sql="ALTER TABLE users DROP COLUMN status"
)
```

### Rename Column

```python
MigrationStep(
    id="002",
    up_sql="""
        ALTER TABLE users RENAME COLUMN old_name TO new_name;
    """,
    down_sql="""
        ALTER TABLE users RENAME COLUMN new_name TO old_name;
    """
)
```

### Migrate JSON Data

```python
def migrate_json(session):
    transformer = DataTransformer(session)
    transformer.migrate_json_data(
        'settings',
        'config',
        lambda data: {**data, 'version': 2}
    )
    return transformer.transformations_applied

MigrationStep(id="003", up_function=migrate_json)
```

## Troubleshooting

### Migration Fails

```python
# Check validation
result = manager.validate_database()

# View failed migrations
for r in manager.results:
    if r.status == MigrationStatus.FAILED:
        print(f"{r.step_id}: {r.error_message}")

# Rollback
manager.rollback()
```

### Orphaned Migrations

```python
validation = manager.validate_database()
for issue in validation['issues']:
    if issue['type'] == 'orphaned_migrations':
        print(f"Orphaned: {issue['migrations']}")
```

### Checksum Mismatch

```python
# Migration was modified after execution
validation = manager.validate_database()
for issue in validation['issues']:
    if issue['type'] == 'checksum_mismatch':
        print(f"Modified: {issue['migration_id']}")
```

## Requirements

- Python 3.10+
- SQLAlchemy 2.0+
- Database: SQLite, PostgreSQL, MySQL

## See Also

- [Full Documentation](README.md)
- [Example Migrations](examples/)
- [API Reference](migration_manager.py)
- [Tests](../tests/test_migration_system.py)
