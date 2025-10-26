# Database Migration System

Comprehensive database migration management with automatic execution, rollback capabilities, and environment-specific configuration.

## Overview

The migration system provides:

- **Automatic Migration Execution**: Migrations run automatically on application startup
- **Safe Rollback**: Rollback capabilities with safety checks
- **Migration Templates**: Pre-built templates for common operations
- **Environment-Specific Configuration**: Different settings for dev/staging/prod
- **Zero-Downtime Support**: Transaction-per-migration for safe deployments

## Quick Start

### Initialize Database with Migrations

```python
from core.database import init_database

# Initialize database and run pending migrations
init_database(auto_migrate=True)
```

### Check Migration Status

```python
from core.migration_manager import get_migration_status

status = get_migration_status()
print(f"Current: {status['current_revision']}")
print(f"Head: {status['head_revision']}")
print(f"Pending: {status['pending_migrations']}")
```

### Run Migrations Manually

```python
from core.migration_manager import migrate

# Run all pending migrations
migrate(auto_run=True)

# Run to specific revision
migrate(target_revision="abc123", auto_run=True)
```

### Rollback Migrations

```python
from core.migration_manager import rollback

# Rollback one migration
rollback(target_revision="-1")

# Rollback to specific revision
rollback(target_revision="abc123")

# Rollback all migrations
rollback(target_revision="base")
```

## Creating Migrations

### Auto-Generate from Model Changes

```python
from core.migration_manager import create_migration

# Create migration with auto-detection of model changes
revision = create_migration(
    message="Add user profile fields",
    autogenerate=True
)
```

### Create Empty Migration Template

```python
from core.migration_manager import create_migration

# Create empty migration for manual editing
revision = create_migration(
    message="Custom data migration",
    autogenerate=False
)
```

### Using Migration Templates

```python
from core.migration_templates import generate_migration_code

# Generate code for adding a column
code = generate_migration_code(
    "add_column",
    table_name="users",
    column_name="age",
    column_type="sa.Integer()",
    nullable=True,
    default=0,
    comment="User age"
)

print(code["upgrade"])
print(code["downgrade"])
```

## Migration Templates

### Add Column

```python
from core.migration_templates import MigrationTemplates

template = MigrationTemplates.add_column_template(
    table_name="users",
    column_name="phone",
    column_type="sa.String(20)",
    nullable=True,
    default=None,
    comment="User phone number"
)
```

### Add Index

```python
template = MigrationTemplates.add_index_template(
    table_name="users",
    column_names=["email"],
    unique=True,
    index_name="uix_users_email"
)
```

### Add Foreign Key

```python
template = MigrationTemplates.add_foreign_key_template(
    table_name="posts",
    column_name="user_id",
    ref_table="users",
    ref_column="id",
    ondelete="CASCADE"
)
```

### Create Table

```python
columns = [
    {"name": "username", "type": "sa.String(100)", "nullable": False},
    {"name": "email", "type": "sa.String(255)", "nullable": False},
    {"name": "age", "type": "sa.Integer()", "nullable": True, "default": 0}
]

template = MigrationTemplates.create_table_template(
    table_name="users",
    columns=columns,
    with_timestamps=True,
    with_soft_delete=True
)
```

### Rename Column

```python
template = MigrationTemplates.rename_column_template(
    table_name="users",
    old_name="name",
    new_name="full_name"
)
```

### Add Check Constraint

```python
template = MigrationTemplates.add_check_constraint_template(
    table_name="users",
    constraint_name="check_age_positive",
    condition="age >= 0"
)
```

### Data Migration

```python
template = MigrationTemplates.data_migration_template(
    description="Set default user status",
    upgrade_sql="UPDATE users SET status = 'active' WHERE status IS NULL",
    downgrade_sql="UPDATE users SET status = NULL WHERE status = 'active'"
)
```

## Migration Manager API

### MigrationManager Class

```python
from core.migration_manager import MigrationManager

manager = MigrationManager()

# Get current database revision
current = manager.get_current_revision()

# Get head revision from scripts
head = manager.get_head_revision()

# Get pending migrations
pending = manager.get_pending_migrations()

# Check if migrations are pending
has_pending = manager.has_pending_migrations()

# Run migrations
manager.run_migrations(target_revision="head")

# Rollback migrations
manager.rollback_migration(target_revision="-1", safety_check=True)

# Create new migration
manager.create_migration(message="Add user fields", autogenerate=True)

# Get migration history
history = manager.get_migration_history()

# Verify migrations
results = manager.verify_migrations()

# Stamp database with revision
manager.stamp_database(revision="head")
```

## Environment-Specific Configuration

### Development

```bash
# .env.dev
ENV=dev
DATABASE_URL=duckdb:///dev.db
DB_ECHO=true
```

### Staging

```bash
# .env.staging
ENV=staging
DATABASE_URL=postgresql://user:pass@staging-db/app
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### Production

```bash
# .env.prod
ENV=prod
DATABASE_URL=postgresql://user:pass@prod-db/app
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_ECHO=false
```

## Safety Features

### Rollback Safety Checks

The migration system performs safety checks before rollback:

1. **Database Accessibility**: Verifies database is accessible
2. **Production Protection**: Requires explicit confirmation in production
3. **Backup Verification**: Checks for recent backups (if enabled)

```python
# Rollback with safety checks (default)
rollback(target_revision="-1", safety_check=True)

# Rollback without safety checks (use with caution)
rollback(target_revision="-1", safety_check=False)
```

### Transaction Per Migration

Each migration runs in its own transaction for safety:

- If a migration fails, it's automatically rolled back
- Other migrations are not affected
- Database remains in consistent state

## Zero-Downtime Migrations

### Best Practices

1. **Backward Compatible Changes**: Make schema changes backward compatible
2. **Multi-Step Migrations**: Break breaking changes into multiple steps
3. **Feature Flags**: Use feature flags to control new functionality
4. **Blue-Green Deployment**: Deploy to parallel environment first

### Example: Renaming a Column

**Step 1**: Add new column

```python
# Migration 1: Add new column
op.add_column('users', sa.Column('full_name', sa.String(255)))
```

**Step 2**: Copy data

```python
# Migration 2: Copy data
op.execute("UPDATE users SET full_name = name")
```

**Step 3**: Update application code to use new column

**Step 4**: Remove old column

```python
# Migration 3: Remove old column
op.drop_column('users', 'name')
```

## CLI Integration

### Run Migrations

```bash
# Run all pending migrations
python -m core.migration_manager migrate

# Run to specific revision
python -m core.migration_manager migrate --revision abc123
```

### Rollback Migrations

```bash
# Rollback one migration
python -m core.migration_manager rollback

# Rollback to specific revision
python -m core.migration_manager rollback --revision abc123
```

### Create Migration

```bash
# Create migration with auto-detection
python -m core.migration_manager create "Add user fields"

# Create empty migration
python -m core.migration_manager create "Custom migration" --no-autogenerate
```

### Check Status

```bash
# Show migration status
python -m core.migration_manager status

# Show migration history
python -m core.migration_manager history
```

## Testing

### Run Migration Tests

```bash
# Run all migration tests
pytest core/test_migration_manager.py -v

# Run specific test
pytest core/test_migration_manager.py::TestMigrationManager::test_run_migrations -v
```

### Test Migration in Isolation

```python
import pytest
from core.migration_manager import MigrationManager

@pytest.fixture
def migration_manager():
    # Create isolated migration manager for testing
    return MigrationManager()

def test_my_migration(migration_manager):
    # Test migration logic
    pass
```

## Troubleshooting

### Migration Fails

```python
from core.migration_manager import get_migration_manager

manager = get_migration_manager()

# Verify migration integrity
results = manager.verify_migrations()
print(results)

# Check database health
from core.database import get_db_manager
db_manager = get_db_manager()
print(db_manager.health_check())
```

### Stuck Migration

```python
# Manually stamp database to skip problematic migration
manager.stamp_database(revision="next_revision_id")
```

### Reset Migrations

```python
# Rollback all migrations
rollback(target_revision="base")

# Re-run all migrations
migrate(target_revision="head")
```

## Advanced Usage

### Custom Migration Logic

```python
# In migration file
def upgrade():
    # Custom logic before schema change
    connection = op.get_bind()
    result = connection.execute("SELECT COUNT(*) FROM users")
    count = result.scalar()
    
    if count > 1000:
        # Batch processing for large tables
        pass
    
    # Schema change
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Custom logic after schema change
    op.execute("UPDATE users SET status = 'active'")
```

### Conditional Migrations

```python
def upgrade():
    # Check if column exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'status' not in columns:
        op.add_column('users', sa.Column('status', sa.String(20)))
```

### Migration Dependencies

```python
# In migration file
depends_on = ['abc123', 'def456']  # Required migrations

def upgrade():
    # This migration requires abc123 and def456 to be applied first
    pass
```

## Best Practices

1. **Always Test Migrations**: Test migrations in development before production
2. **Use Descriptive Messages**: Write clear migration messages
3. **Keep Migrations Small**: One logical change per migration
4. **Review Generated Migrations**: Always review auto-generated migrations
5. **Backup Before Migration**: Always have a recent backup
6. **Monitor Migration Performance**: Track migration execution time
7. **Document Complex Migrations**: Add comments for complex logic
8. **Use Templates**: Use migration templates for consistency
9. **Test Rollback**: Always test rollback before deploying
10. **Version Control**: Commit migrations to version control

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 5.1**: Automatic migration execution on application startup
- **Requirement 5.2**: Atomic and rollback-capable migrations
- **Requirement 5.7**: Zero-downtime migration strategy with restore capability

## Architecture

```
core/
├── alembic/                    # Alembic migration directory
│   ├── versions/              # Migration scripts
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
├── alembic.ini                # Alembic configuration
├── migration_manager.py       # Migration management
├── migration_templates.py     # Migration templates
└── test_migration_manager.py  # Migration tests
```

## See Also

- [Configuration System](CONFIG_README.md)
- [Database Layer](database.py)
- [Logging System](LOGGING_README.md)
