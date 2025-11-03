# Database Migration System - Quick Reference

## Overview

The database migration system uses Alembic to manage schema changes with automatic execution on startup, rollback capabilities, and safety checks.

## Quick Start

### 1. Initialize Migration Environment

```python
from core.migrations import get_migration_manager

manager = get_migration_manager()
manager.initialize_alembic()
```

Or via CLI:
```bash
python -m core.cli_migrations init
```

### 2. Create a Migration

```python
from core.migrations import create_migration

# Auto-generate from model changes
revision = create_migration("add_user_table", autogenerate=True)

# Manual migration
revision = create_migration("custom_changes", autogenerate=False)
```

Or via CLI:
```bash
python -m core.cli_migrations create "add_user_table" --auto
```

### 3. Run Migrations

```python
from core.migrations import migrate

# Upgrade to latest
migrate()

# Upgrade to specific revision
migrate("abc123")
```

Or via CLI:
```bash
python -m core.cli_migrations upgrade
python -m core.cli_migrations upgrade --revision abc123
```

### 4. Rollback Migrations

```python
from core.migrations import rollback

# Rollback one step
rollback("-1")

# Rollback to specific revision
rollback("abc123")
```

Or via CLI:
```bash
python -m core.cli_migrations downgrade
python -m core.cli_migrations downgrade --revision abc123 --force
```

## Common Operations

### Check Current State

```python
manager = get_migration_manager()

# Get current revision
current = manager.get_current_revision()
print(f"Current: {current}")

# Get pending migrations
pending = manager.get_pending_migrations()
print(f"Pending: {len(pending)}")
```

CLI:
```bash
python -m core.cli_migrations current
python -m core.cli_migrations pending
```

### View Migration History

```python
manager = get_migration_manager()
history = manager.get_migration_history()

for entry in history:
    print(f"{entry['revision']}: {entry['message']}")
```

CLI:
```bash
python -m core.cli_migrations history
```

### Validate Migrations

```python
manager = get_migration_manager()
results = manager.validate_migrations()

print(f"Status: {results['status']}")
print(f"Errors: {results['errors']}")
print(f"Warnings: {results['warnings']}")
```

CLI:
```bash
python -m core.cli_migrations validate
```

## Migration Templates

### Available Templates

1. **add_column** - Add a new column to a table
2. **add_index** - Add an index to a table
3. **add_table** - Create a new table
4. **add_foreign_key** - Add a foreign key constraint

### Create Template

```python
manager = get_migration_manager()
template_path = manager.create_migration_template("add_column")
```

CLI:
```bash
python -m core.cli_migrations template add_column
```

### Example: Add Column Migration

```python
"""Add email column to users

Revision ID: abc123
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'email')
```

### Example: Add Index Migration

```python
"""Add index on user email

Revision ID: def456
"""
from alembic import op

def upgrade() -> None:
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('idx_users_email', 'users')
```

## Automatic Migration on Startup

Migrations run automatically when the application starts:

```python
from core.database import init_database

# This will run pending migrations automatically
init_database()
```

## Environment-Specific Configuration

### Development
- Database: SQLite/DuckDB
- Auto-migration: Enabled
- Rollback: Allowed without confirmation

### Staging
- Database: PostgreSQL
- Auto-migration: Enabled
- Rollback: Requires confirmation

### Production
- Database: PostgreSQL
- Auto-migration: Enabled (safe migrations only)
- Rollback: Requires explicit confirmation
- Extra logging and validation

## Safety Features

### 1. Transaction Per Migration
Each migration runs in its own transaction for safety:
```python
# Configured in env.py
context.configure(
    transaction_per_migration=True
)
```

### 2. Rollback Capability
All migrations must implement both upgrade and downgrade:
```python
def upgrade() -> None:
    # Forward migration
    pass

def downgrade() -> None:
    # Rollback migration
    pass
```

### 3. Validation Before Apply
```python
manager = get_migration_manager()
results = manager.validate_migrations()

if results['status'] != 'success':
    print("Validation failed!")
    for error in results['errors']:
        print(f"  - {error}")
```

### 4. Production Warnings
Extra confirmation required for production operations:
```python
if config.is_production():
    logger.warning("Attempting rollback in production")
    # Requires explicit confirmation
```

## Integration with Application

### In Application Initialization

```python
from core.config import load_config
from core.database import init_database
from core.migrations import migrate

def init_app():
    """Initialize application"""
    # Load configuration
    config = load_config()

    # Initialize database and run migrations
    init_database()  # This calls migrate() automatically

    # Application is ready
    logger.info("Application initialized")
```

### Manual Migration Control

```python
from core.migrations import get_migration_manager

def init_app_manual():
    """Initialize with manual migration control"""
    config = load_config()

    # Initialize database without migrations
    db_manager = get_db_manager()
    db_manager.create_tables()

    # Run migrations manually
    manager = get_migration_manager()

    # Validate first
    results = manager.validate_migrations()
    if results['status'] == 'success':
        manager.run_migrations()
    else:
        logger.error("Migration validation failed")
```

## Troubleshooting

### No Migrations Directory

```bash
python -m core.cli_migrations init
```

### Migrations Out of Sync

```bash
# Check current state
python -m core.cli_migrations current
python -m core.cli_migrations pending

# Validate
python -m core.cli_migrations validate

# If needed, rollback and reapply
python -m core.cli_migrations downgrade --revision base
python -m core.cli_migrations upgrade
```

### Migration Failed

```python
# Check error logs
manager = get_migration_manager()
results = manager.validate_migrations()
print(results['errors'])

# Rollback if needed
manager.rollback_migration("-1")
```

### Database Schema Mismatch

```bash
# Create new migration from current models
python -m core.cli_migrations create "sync_schema" --auto

# Review the generated migration
# Then apply it
python -m core.cli_migrations upgrade
```

## Best Practices

### 1. Always Test Migrations
```python
# Test in development first
ENV=dev python -m core.cli_migrations upgrade

# Then staging
ENV=staging python -m core.cli_migrations upgrade

# Finally production
ENV=prod python -m core.cli_migrations upgrade
```

### 2. Use Descriptive Messages
```bash
# Good
python -m core.cli_migrations create "add_user_email_column"

# Bad
python -m core.cli_migrations create "update"
```

### 3. Review Auto-Generated Migrations
Always review auto-generated migrations before applying:
```bash
# Generate migration
python -m core.cli_migrations create "add_column" --auto

# Review the file in core/alembic/versions/
# Edit if needed
# Then apply
python -m core.cli_migrations upgrade
```

### 4. Keep Migrations Small
Create focused migrations for single changes:
```bash
# Good - separate migrations
python -m core.cli_migrations create "add_user_email"
python -m core.cli_migrations create "add_user_phone"

# Bad - combined migration
python -m core.cli_migrations create "add_user_fields"
```

### 5. Test Rollback
Always test that rollback works:
```bash
# Apply migration
python -m core.cli_migrations upgrade

# Test rollback
python -m core.cli_migrations downgrade --revision -1

# Reapply
python -m core.cli_migrations upgrade
```

## CLI Reference

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize migration environment | `python -m core.cli_migrations init` |
| `create` | Create new migration | `python -m core.cli_migrations create "message"` |
| `upgrade` | Run pending migrations | `python -m core.cli_migrations upgrade` |
| `downgrade` | Rollback migrations | `python -m core.cli_migrations downgrade` |
| `current` | Show current revision | `python -m core.cli_migrations current` |
| `history` | Show migration history | `python -m core.cli_migrations history` |
| `pending` | Show pending migrations | `python -m core.cli_migrations pending` |
| `validate` | Validate migration state | `python -m core.cli_migrations validate` |
| `template` | Create migration template | `python -m core.cli_migrations template add_column` |

## API Reference

### MigrationManager

```python
from core.migrations import MigrationManager

manager = MigrationManager()

# Initialize
manager.initialize_alembic()

# Run migrations
manager.run_migrations("head")

# Create migration
manager.create_migration("message", autogenerate=True)

# Rollback
manager.rollback_migration("-1")

# Get state
current = manager.get_current_revision()
pending = manager.get_pending_migrations()
history = manager.get_migration_history()

# Validate
results = manager.validate_migrations()

# Templates
template_path = manager.create_migration_template("add_column")
```

### Helper Functions

```python
from core.migrations import migrate, rollback, create_migration

# Run migrations
migrate()
migrate("abc123")

# Rollback
rollback()
rollback("abc123")

# Create migration
revision = create_migration("message", autogenerate=True)
```

## Requirements

The migration system requires:
- `alembic>=1.12.0`
- `sqlalchemy>=2.0.0`
- `typer>=0.9.0` (for CLI)
- `rich>=13.0.0` (for CLI)

Install with:
```bash
pip install alembic sqlalchemy typer rich
```

## See Also

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Database System Guide](./database.py)
- [Configuration Guide](./CONFIG_SYSTEM_GUIDE.md)
