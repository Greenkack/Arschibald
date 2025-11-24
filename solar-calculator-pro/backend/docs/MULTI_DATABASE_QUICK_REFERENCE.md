# Multi-Database Support - Quick Reference

## Supported Databases

- ✅ SQLite (default)
- ✅ PostgreSQL
- ✅ MySQL

## Quick Start

### 1. Configure Database

```python
from backend.core.database_abstraction import DatabaseConfig, DatabaseType

# SQLite
config = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./database.db"
)

# PostgreSQL
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    database="mydb",
    username="user",
    password="pass"
)

# MySQL
config = DatabaseConfig(
    db_type=DatabaseType.MYSQL,
    host="localhost",
    database="mydb",
    username="user",
    password="pass"
)
```

### 2. Use Database

```python
from backend.core.database_abstraction import DatabaseManager

with DatabaseManager(config) as manager:
    session = manager.get_session()
    # ... your operations ...
    session.close()
```

### 3. Migrate Database

```python
from backend.services.database_migration_service import DatabaseMigrationService

service = DatabaseMigrationService(source_config, target_config)
progress = service.migrate_all()
```

## Common Operations

### Connect/Disconnect

```python
manager = DatabaseManager(config)
manager.connect()
# ... operations ...
manager.disconnect()
```

### Create Tables

```python
manager.create_tables()
```

### Get Session

```python
session = manager.get_session()
```

### Execute Raw SQL

```python
result = manager.execute_raw_sql("SELECT * FROM users")
```

### Backup

```python
manager.backup("./backup.db")
```

### Restore

```python
manager.restore("./backup.db")
```

## Migration Workflow

```python
# 1. Validate
validation = service.validate_migration()

# 2. Migrate
progress = service.migrate_all(batch_size=1000)

# 3. Verify
verification = service.verify_migration()

# 4. Rollback (if needed)
service.rollback_migration()
```

## API Endpoints

### Test Connection
```
POST /api/v1/database-type/test-connection
```

### Migrate
```
POST /api/v1/database-type/migrate
```

### Verify
```
POST /api/v1/database-type/verify-migration
```

### Rollback
```
POST /api/v1/database-type/rollback-migration
```

## Configuration Parameters

| Parameter | SQLite | PostgreSQL | MySQL | Description |
|-----------|--------|------------|-------|-------------|
| `db_type` | ✅ | ✅ | ✅ | Database type |
| `sqlite_path` | ✅ | ❌ | ❌ | Path to SQLite file |
| `host` | ❌ | ✅ | ✅ | Database host |
| `port` | ❌ | ✅ | ✅ | Database port |
| `database` | ❌ | ✅ | ✅ | Database name |
| `username` | ❌ | ✅ | ✅ | Username |
| `password` | ❌ | ✅ | ✅ | Password |
| `pool_size` | ❌ | ✅ | ✅ | Connection pool size |
| `max_overflow` | ❌ | ✅ | ✅ | Max overflow connections |
| `pool_timeout` | ❌ | ✅ | ✅ | Pool timeout (seconds) |
| `pool_recycle` | ❌ | ✅ | ✅ | Connection recycle time |
| `echo` | ✅ | ✅ | ✅ | Log SQL queries |

## Default Ports

- PostgreSQL: 5432
- MySQL: 3306

## Best Practices

✅ **DO:**
- Use context managers (`with` statement)
- Handle exceptions properly
- Test migrations on copies first
- Use environment variables for credentials
- Configure appropriate pool sizes
- Monitor migration progress

❌ **DON'T:**
- Hardcode credentials
- Skip validation before migration
- Migrate without backups
- Use same database for source and target
- Ignore error messages

## Troubleshooting

### Cannot connect
- Check database is running
- Verify credentials
- Check firewall settings

### Migration fails
- Check error messages
- Verify disk space
- Try smaller batch size
- Use rollback to clean up

### Slow performance
- Increase batch size
- Check network speed
- Optimize queries
- Add indexes

## Requirements

### Python Packages
```bash
pip install sqlalchemy
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL
```

### System Tools
- `pg_dump` and `psql` for PostgreSQL backup/restore
- `mysqldump` and `mysql` for MySQL backup/restore

## Examples

### Complete Migration Example

```python
from backend.core.database_abstraction import DatabaseConfig, DatabaseType
from backend.services.database_migration_service import DatabaseMigrationService

# Source: SQLite
source = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./old.db"
)

# Target: PostgreSQL
target = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    database="newdb",
    username="postgres",
    password="password"
)

# Migrate
service = DatabaseMigrationService(source, target)

# Validate
if not service.validate_migration()["valid"]:
    print("Validation failed!")
    exit(1)

# Migrate
progress = service.migrate_all(batch_size=1000)
print(f"Migrated {progress.migrated_rows} rows")

# Verify
verification = service.verify_migration()
if verification["success"]:
    print("Migration successful!")
else:
    print("Verification failed!")
    service.rollback_migration()
```

### Using Different Databases

```python
# Development: SQLite
dev_config = DatabaseConfig(
    db_type=DatabaseType.SQLITE,
    sqlite_path="./dev.db"
)

# Staging: PostgreSQL
staging_config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="staging.example.com",
    database="staging_db",
    username="staging_user",
    password="staging_pass"
)

# Production: PostgreSQL
prod_config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="prod.example.com",
    database="prod_db",
    username="prod_user",
    password="prod_pass",
    pool_size=20,
    max_overflow=40
)
```

## Support

For detailed documentation, see:
- [Multi-Database Support Guide](./MULTI_DATABASE_SUPPORT_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)

For issues or questions:
- Check error logs
- Review troubleshooting section
- Contact development team
