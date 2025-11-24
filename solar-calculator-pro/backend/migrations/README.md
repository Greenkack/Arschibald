# Database Migration System

Comprehensive database migration system with validation, rollback, and progress tracking.

## Features

- ✅ **Schema Migrations**: Add/modify tables and columns
- ✅ **Data Migrations**: Transform and migrate data
- ✅ **Validation**: Pre and post-migration validation
- ✅ **Rollback**: Full rollback capabilities
- ✅ **Progress Tracking**: Real-time progress updates
- ✅ **Dependency Resolution**: Automatic dependency ordering
- ✅ **Incremental Migration**: Migrate to specific versions
- ✅ **Dry Run**: Test migrations without applying changes

## Quick Start

### 1. Create a Migration

```python
from migration_manager import MigrationStep, MigrationType

# Schema migration
migration = MigrationStep(
    id="001_add_user_email",
    name="Add Email Column",
    description="Add email column to users table",
    type=MigrationType.SCHEMA,
    up_sql="ALTER TABLE users ADD COLUMN email TEXT",
    down_sql="ALTER TABLE users DROP COLUMN email"
)
```

### 2. Register and Execute

```python
from migration_manager import MigrationManager

# Initialize manager
manager = MigrationManager("sqlite:///database.db")

# Register migration
manager.register_migration(migration)

# Execute migrations
result = manager.migrate()
print(f"Migrations executed: {result['migrations_executed']}")
```

### 3. Rollback if Needed

```python
# Rollback last migration
result = manager.rollback()

# Rollback to specific version
result = manager.rollback(target_version="001_add_user_email")
```

## Migration Types

### Schema Migrations

Modify database structure:

```python
MigrationStep(
    id="001_create_table",
    name="Create Products Table",
    type=MigrationType.SCHEMA,
    up_sql="""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """,
    down_sql="DROP TABLE products"
)
```

### Data Migrations

Transform existing data:

```python
def transform_data(session):
    transformer = DataTransformer(session)
    
    # Normalize text
    transformer.normalize_text('users', 'email', lowercase=True)
    
    # Convert types
    transformer.convert_type('products', 'price', float)
    
    return transformer.transformations_applied

MigrationStep(
    id="002_normalize_data",
    name="Normalize User Data",
    type=MigrationType.DATA,
    up_function=transform_data
)
```

### Transformation Migrations

Complex data transformations:

```python
def split_names(session):
    transformer = DataTransformer(session)
    
    # Split full_name into first_name and last_name
    transformer.split_column(
        table='users',
        source_column='full_name',
        target_columns=['first_name', 'last_name'],
        separator=' '
    )
    
    return transformer.transformations_applied

MigrationStep(
    id="003_split_names",
    name="Split User Names",
    type=MigrationType.TRANSFORMATION,
    up_function=split_names
)
```

## Data Transformation

### Available Transformations

```python
from data_transformer import DataTransformer

transformer = DataTransformer(session)

# 1. Transform column values
transformer.transform_column(
    table='users',
    column='email',
    transform_func=lambda x: x.lower()
)

# 2. Map values
transformer.map_values(
    table='users',
    column='status',
    value_map={'0': 'inactive', '1': 'active'}
)

# 3. Convert data types
transformer.convert_type('products', 'price', float)

# 4. Normalize text
transformer.normalize_text(
    table='users',
    column='name',
    lowercase=True,
    strip=True
)

# 5. Split columns
transformer.split_column(
    table='users',
    source_column='full_name',
    target_columns=['first_name', 'last_name']
)

# 6. Merge columns
transformer.merge_columns(
    table='users',
    source_columns=['first_name', 'last_name'],
    target_column='full_name'
)

# 7. Transform JSON data
transformer.migrate_json_data(
    table='settings',
    column='config',
    transform_func=lambda data: {**data, 'version': 2}
)

# 8. Remove duplicates
transformer.deduplicate_rows(
    table='users',
    unique_columns=['email'],
    keep='first'
)
```

## Data Validation

### Built-in Validation Rules

```python
from data_validator import DataValidator

validator = DataValidator(session)

# Table and column existence
validator.add_table_exists('users')
validator.add_column_exists('users', 'email')

# Data integrity
validator.add_not_null('users', 'email')
validator.add_unique('users', 'email')

# Data types
validator.add_data_type('products', 'price', float)

# Value ranges
validator.add_range('products', 'price', min_value=0, max_value=10000)

# Pattern matching
validator.add_pattern('users', 'email', r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Foreign keys
validator.add_foreign_key('orders', 'user_id', 'users', 'id')

# Custom validation
validator.add_custom(
    name='check_admin_exists',
    description='At least one admin user must exist',
    validation_func=lambda s: s.execute(
        text("SELECT COUNT(*) FROM users WHERE role='admin'")
    ).scalar() > 0
)

# Execute validation
result = validator.validate()
if not result['valid']:
    print(f"Validation failed: {result['failed']} rules")
    for failure in validator.get_failed_rules():
        print(f"  - {failure['message']}")
```

## Progress Tracking

### Real-time Progress Updates

```python
from progress_tracker import ProgressTracker, ProgressLogger

# Create tracker
tracker = ProgressTracker(total_steps=3)

# Add console logging
logger = ProgressLogger(tracker)

# Track progress
tracker.start_step("Creating tables")
# ... do work ...
tracker.complete_step()

tracker.start_step("Migrating data")
# ... do work ...
tracker.update_step_progress(0.5)  # 50% complete
# ... do more work ...
tracker.complete_step()

tracker.start_step("Creating indexes")
# ... do work ...
tracker.complete_step()

# Get summary
summary = tracker.get_summary()
print(f"Progress: {summary['progress']['percentage']:.1f}%")
```

### WebSocket Progress Updates

```python
from progress_tracker import ProgressWebSocket

# Send progress via WebSocket
ws_progress = ProgressWebSocket(tracker, websocket_manager)

# Progress updates will be automatically broadcast to connected clients
```

## Advanced Usage

### Dependency Management

```python
# Migrations with dependencies
migration_1 = MigrationStep(
    id="001_create_users",
    name="Create Users Table",
    type=MigrationType.SCHEMA,
    up_sql="CREATE TABLE users (...)",
    dependencies=[]
)

migration_2 = MigrationStep(
    id="002_create_orders",
    name="Create Orders Table",
    type=MigrationType.SCHEMA,
    up_sql="CREATE TABLE orders (...)",
    dependencies=["001_create_users"]  # Depends on users table
)

# Manager will execute in correct order
manager.register_migration(migration_1)
manager.register_migration(migration_2)
manager.migrate()  # Executes 001 first, then 002
```

### Incremental Migration

```python
# Migrate to specific version
manager.migrate(target_version="002_create_orders")

# Check current status
status = manager.get_migration_status()
print(f"Current version: {status['current_version']}")
print(f"Pending migrations: {status['pending_migrations']}")
```

### Dry Run

```python
# Test migration without applying changes
result = manager.migrate(dry_run=True)
print(f"Would execute {len(result['migrations_to_execute'])} migrations")
```

### Database Validation

```python
# Validate database integrity
validation = manager.validate_database()

if not validation['valid']:
    print(f"Found {validation['issues_found']} issues:")
    for issue in validation['issues']:
        print(f"  [{issue['severity']}] {issue['message']}")
```

### Export Migration History

```python
# Export history to JSON
manager.export_migration_history('migration_history.json')
```

## Best Practices

### 1. Always Include Rollback

```python
# Good: Includes rollback
MigrationStep(
    id="001_add_column",
    up_sql="ALTER TABLE users ADD COLUMN email TEXT",
    down_sql="ALTER TABLE users DROP COLUMN email"
)

# Bad: No rollback
MigrationStep(
    id="001_add_column",
    up_sql="ALTER TABLE users ADD COLUMN email TEXT"
    # Missing down_sql!
)
```

### 2. Add Validation

```python
def validate(session):
    validator = DataValidator(session)
    validator.add_column_exists('users', 'email')
    validator.add_not_null('users', 'email')
    return validator.validate()['valid']

MigrationStep(
    id="001_add_email",
    up_sql="ALTER TABLE users ADD COLUMN email TEXT NOT NULL",
    down_sql="ALTER TABLE users DROP COLUMN email",
    validation_function=validate
)
```

### 3. Use Batch Processing

```python
# Process large datasets in batches
transformer.transform_column(
    table='users',
    column='email',
    transform_func=lambda x: x.lower(),
    batch_size=1000  # Process 1000 rows at a time
)
```

### 4. Track Progress

```python
def migrate_with_progress(session):
    tracker = ProgressTracker(total_steps=3)
    transformer = DataTransformer(session)
    
    tracker.start_step("Step 1")
    # ... work ...
    tracker.complete_step()
    
    tracker.start_step("Step 2")
    # ... work ...
    tracker.complete_step()
    
    return transformer.transformations_applied
```

### 5. Handle Errors Gracefully

```python
def safe_migration(session):
    try:
        # Attempt migration
        result = perform_migration(session)
        return result
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        # Rollback is automatic
        raise
```

## Requirements

- Python 3.10+
- SQLAlchemy 2.0+
- Database: SQLite, PostgreSQL, MySQL

## Related Documentation

- [Migration Manager API](migration_manager.py)
- [Data Transformer API](data_transformer.py)
- [Data Validator API](data_validator.py)
- [Progress Tracker API](progress_tracker.py)
- [Example Migrations](examples/)
