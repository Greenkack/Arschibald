# Multi-Database Support Guide

## Overview

The Solar Calculator Pro application supports multiple database backends:
- **SQLite** - Default, file-based database (ideal for single-user desktop applications)
- **PostgreSQL** - Enterprise-grade relational database (ideal for multi-user deployments)
- **MySQL** - Popular open-source relational database (ideal for web deployments)

This guide explains how to configure, use, and migrate between different database types.

## Architecture

### Database Abstraction Layer

The application uses a database abstraction layer that provides a unified interface for all supported database types:

```
┌─────────────────────────────────────────┐
│      Application Layer                  │
├─────────────────────────────────────────┤
│      DatabaseManager                    │
├─────────────────────────────────────────┤
│      Database Adapters                  │
│  ┌──────────┬──────────┬──────────┐    │
│  │ SQLite   │PostgreSQL│  MySQL   │    │
│  │ Adapter  │ Adapter  │ Adapter  │    │
│  └──────────┴──────────┴──────────┘    │
├─────────────────────────────────────────┤
│      SQLAlchemy ORM                     │
├─────────────────────────────────────────┤
│      Database Engines                   │
│  ┌──────────┬──────────┬──────────┐    │
│  │ SQLite   │PostgreSQL│  MySQL   │    │
│  └──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────┘
```

### Key Components

1. **DatabaseConfig** - Configuration for database connection
2. **DatabaseAdapter** - Abstract base class for database-specific operations
3. **DatabaseFactory** - Creates appropriate adapter based on configuration
4. **DatabaseManager** - Unified interface for database operations
5. **DatabaseMigrationService** - Handles migration between database types

## Configuration

### SQLite Configuration

```python
from backend.core.database_abstraction import DatabaseConfig, DatabaseType

config = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./database.db",
    echo=False  # Set to True for SQL query logging
)
```

### PostgreSQL Configuration

```python
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="solar_calculator",
    username="postgres",
    password="your_password",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False
)
```

### MySQL Configuration

```python
config = DatabaseConfig(
    db_type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    database="solar_calculator",
    username="root",
    password="your_password",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False
)
```

## Usage

### Basic Database Operations

```python
from backend.core.database_abstraction import DatabaseManager, DatabaseConfig, DatabaseType

# Create configuration
config = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./database.db"
)

# Create manager
manager = DatabaseManager(config)

# Connect to database
manager.connect()

# Get session
session = manager.get_session()

# Perform operations
# ... your database operations ...

# Close session
session.close()

# Disconnect
manager.disconnect()
```

### Using Context Manager

```python
with DatabaseManager(config) as manager:
    session = manager.get_session()
    # Perform operations
    session.close()
# Automatically disconnects
```

### Creating Tables

```python
manager.connect()
manager.create_tables()
manager.disconnect()
```

### Executing Raw SQL

```python
manager.connect()
result = manager.execute_raw_sql(
    "SELECT * FROM users WHERE id = :id",
    {"id": 1}
)
manager.disconnect()
```

## Database Migration

### Migration Process

The migration service allows you to migrate data from one database type to another:

```python
from backend.services.database_migration_service import DatabaseMigrationService

# Source configuration (e.g., SQLite)
source_config = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./old_database.db"
)

# Target configuration (e.g., PostgreSQL)
target_config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    database="solar_calculator",
    username="postgres",
    password="password"
)

# Create migration service
migration_service = DatabaseMigrationService(source_config, target_config)

# Validate migration
validation = migration_service.validate_migration()
if not validation["valid"]:
    print("Migration validation failed:", validation["errors"])
    exit(1)

# Perform migration
progress = migration_service.migrate_all(batch_size=1000)

print(f"Migration completed: {progress.completed_tables}/{progress.total_tables} tables")
print(f"Migrated {progress.migrated_rows} rows")

# Verify migration
verification = migration_service.verify_migration()
if verification["success"]:
    print("Migration verified successfully!")
else:
    print("Migration verification failed:", verification["row_count_mismatches"])
```

### Migration Steps

1. **Validate** - Check that both databases are accessible
2. **Migrate Schema** - Create tables in target database
3. **Migrate Data** - Copy data in batches
4. **Verify** - Compare row counts between source and target
5. **Rollback** (if needed) - Drop all tables in target database

### Monitoring Migration Progress

```python
progress = migration_service.migrate_all()

print(f"Total tables: {progress.total_tables}")
print(f"Completed tables: {progress.completed_tables}")
print(f"Total rows: {progress.total_rows}")
print(f"Migrated rows: {progress.migrated_rows}")
print(f"Progress: {progress.get_progress_percentage():.2f}%")
print(f"Current table: {progress.current_table}")
print(f"Errors: {progress.errors}")
```

## API Endpoints

### Test Database Connection

```http
POST /api/v1/database-type/test-connection
Content-Type: application/json

{
  "config": {
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "solar_calculator",
    "username": "postgres",
    "password": "password"
  }
}
```

### Validate Migration

```http
POST /api/v1/database-type/validate-migration
Content-Type: application/json

{
  "source_config": {
    "db_type": "sqlite",
    "sqlite_path": "./database.db"
  },
  "target_config": {
    "db_type": "postgresql",
    "host": "localhost",
    "database": "solar_calculator",
    "username": "postgres",
    "password": "password"
  }
}
```

### Migrate Database

```http
POST /api/v1/database-type/migrate
Content-Type: application/json

{
  "source_config": { ... },
  "target_config": { ... },
  "batch_size": 1000
}
```

### Verify Migration

```http
POST /api/v1/database-type/verify-migration
Content-Type: application/json

{
  "source_config": { ... },
  "target_config": { ... }
}
```

## Backup and Restore

### SQLite Backup

```python
manager = DatabaseManager(sqlite_config)
success = manager.backup("./backup.db")
```

### PostgreSQL Backup

Requires `pg_dump` to be installed:

```python
manager = DatabaseManager(postgresql_config)
success = manager.backup("./backup.sql")
```

### MySQL Backup

Requires `mysqldump` to be installed:

```python
manager = DatabaseManager(mysql_config)
success = manager.backup("./backup.sql")
```

### Restore

```python
manager = DatabaseManager(config)
success = manager.restore("./backup.db")
```

## Best Practices

### 1. Connection Pooling

For PostgreSQL and MySQL, configure appropriate pool sizes:

```python
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    # ... other settings ...
    pool_size=5,        # Number of connections to maintain
    max_overflow=10,    # Maximum additional connections
    pool_timeout=30,    # Timeout for getting connection
    pool_recycle=3600   # Recycle connections after 1 hour
)
```

### 2. Error Handling

Always use try-except blocks:

```python
try:
    manager.connect()
    session = manager.get_session()
    # ... operations ...
    session.close()
except Exception as e:
    logger.error(f"Database error: {e}")
    # Handle error
finally:
    manager.disconnect()
```

### 3. Migration Testing

Always test migration on a copy of your data first:

```bash
# Create backup
cp database.db database_backup.db

# Test migration
python test_migration.py

# If successful, proceed with actual migration
```

### 4. Batch Size Tuning

Adjust batch size based on available memory:

- Small datasets (< 10,000 rows): batch_size=1000
- Medium datasets (10,000 - 100,000 rows): batch_size=5000
- Large datasets (> 100,000 rows): batch_size=10000

### 5. Database Selection

Choose database based on deployment:

- **SQLite**: Single-user desktop application, development
- **PostgreSQL**: Multi-user production, complex queries, ACID compliance
- **MySQL**: Web applications, high read performance

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to PostgreSQL/MySQL

**Solution**:
1. Check database server is running
2. Verify credentials
3. Check firewall settings
4. Ensure database exists

### Migration Failures

**Problem**: Migration fails partway through

**Solution**:
1. Check error messages in progress.errors
2. Verify both databases are accessible
3. Check disk space
4. Use rollback to clean up target database
5. Retry with smaller batch size

### Performance Issues

**Problem**: Migration is slow

**Solution**:
1. Increase batch size
2. Disable foreign key constraints during migration
3. Create indexes after migration
4. Use faster network connection

### Data Type Mismatches

**Problem**: Data types don't match between databases

**Solution**:
1. SQLAlchemy handles most conversions automatically
2. For custom types, create migration transformations
3. Test with small dataset first

## Security Considerations

### 1. Credential Management

Never hardcode credentials:

```python
import os

config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
```

### 2. Connection Encryption

For PostgreSQL, use SSL:

```python
connection_string = (
    f"postgresql://{username}:{password}@{host}:{port}/{database}"
    f"?sslmode=require"
)
```

### 3. Backup Encryption

Encrypt backups before storing:

```python
import gzip
import shutil

# Backup
manager.backup("./backup.sql")

# Compress and encrypt
with open("./backup.sql", "rb") as f_in:
    with gzip.open("./backup.sql.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
```

## Performance Optimization

### 1. Indexing

Create indexes for frequently queried columns:

```python
from sqlalchemy import Index

Index("idx_user_email", User.email)
Index("idx_project_created", Project.created_at)
```

### 2. Query Optimization

Use query optimization techniques:

```python
# Use select_related for foreign keys
session.query(Project).options(
    selectinload(Project.user)
).all()

# Limit results
session.query(Project).limit(100).all()

# Use pagination
session.query(Project).offset(100).limit(100).all()
```

### 3. Connection Pooling

Configure appropriate pool sizes for your workload:

```python
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    pool_size=10,      # Increase for high concurrency
    max_overflow=20,   # Allow burst traffic
    pool_recycle=1800  # Recycle connections more frequently
)
```

## Monitoring

### 1. Connection Pool Monitoring

```python
engine = manager.adapter.engine
pool = engine.pool

print(f"Pool size: {pool.size()}")
print(f"Checked out connections: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

### 2. Query Performance

Enable SQL logging:

```python
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    echo=True  # Log all SQL queries
)
```

### 3. Migration Progress

Monitor migration in real-time:

```python
import time

progress = migration_service.progress
while progress.completed_tables < progress.total_tables:
    print(f"Progress: {progress.get_progress_percentage():.2f}%")
    print(f"Current table: {progress.current_table}")
    time.sleep(1)
```

## Conclusion

The multi-database support system provides a flexible and robust way to work with different database backends. By following this guide, you can:

- Configure any supported database type
- Migrate between database types seamlessly
- Monitor and optimize database performance
- Handle errors and troubleshoot issues
- Implement security best practices

For additional support, refer to the API documentation or contact the development team.
