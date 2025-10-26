## Enhanced Database Layer

Comprehensive database management system with audit logging, soft delete, bulk operations, caching, connection pooling, and performance monitoring.

### Features

- **Repository Pattern**: Generic repository with CRUD operations
- **Audit Logging**: Automatic tracking of all database changes
- **Soft Delete**: Reversible deletion with restoration capabilities
- **Bulk Operations**: High-performance bulk create, update, and delete
- **Repository Caching**: Optional caching for improved performance
- **Unit of Work**: Transaction management with nested transaction support
- **Connection Pooling**: Configurable connection pooling with health monitoring
- **Performance Monitoring**: Query tracking, slow query detection, and metrics
- **Database Agnostic**: Support for SQLite, DuckDB, and PostgreSQL
- **Zero-Downtime Migrations**: Alembic integration for schema changes

### Quick Start

```python
from core.database import (
    Base,
    Repository,
    UnitOfWork,
    get_db_manager,
    run_tx,
    init_database,
)
from sqlalchemy import Column, Integer, String, DateTime

# Define your model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # For soft delete

# Initialize database
init_database(auto_migrate=True)

# Create repository
db_manager = get_db_manager()
user_repo = Repository(User, db_manager, enable_audit=True)

# Set audit context
user_repo.set_context(user_id="admin", session_id="session123")

# CRUD operations
user = user_repo.create(name="John Doe", email="john@example.com")
user = user_repo.get_by_id(user.id)
user = user_repo.update(user.id, name="Jane Doe")
user_repo.delete(user.id, soft=True)  # Soft delete
user = user_repo.restore(user.id)  # Restore
```

### Core Components

#### DatabaseManager

Manages database connections, sessions, and performance monitoring.

```python
from core.database import get_db_manager

db_manager = get_db_manager()

# Health check
health = db_manager.health_check()
print(f"Healthy: {health['healthy']}")
print(f"Metrics: {health['metrics']}")

# Get metrics
metrics = db_manager.get_metrics()
print(f"Query count: {metrics['query_count']}")
print(f"Slow queries: {metrics['slow_query_count']}")
```

**Features:**
- Automatic connection pooling
- Connection health checks with pre-ping
- Query performance tracking
- Slow query detection
- Connection leak detection
- Automatic retry on connection failure

#### Repository Pattern

Generic repository for CRUD operations with audit logging and soft delete.

```python
from core.database import Repository, get_db_manager

db_manager = get_db_manager()
user_repo = Repository(
    User,
    db_manager,
    enable_audit=True,  # Enable audit logging
    enable_cache=True   # Enable caching
)

# Set audit context
user_repo.set_context(
    user_id="user123",
    session_id="session456",
    correlation_id="req789"
)

# Create
user = user_repo.create(name="John", email="john@example.com")

# Read
user = user_repo.get_by_id(user.id)
users = user_repo.get_all(limit=10, offset=0)
users = user_repo.find_by(email="john@example.com")

# Update
user = user_repo.update(user.id, name="Jane")

# Delete (soft by default)
user_repo.delete(user.id, soft=True)

# Restore soft-deleted
user = user_repo.restore(user.id)

# Hard delete
user_repo.delete(user.id, soft=False)

# Pagination
page = user_repo.paginate(page=1, page_size=20, email="john@example.com")
print(f"Total: {page['total']}, Pages: {page['total_pages']}")

# Count
count = user_repo.count()

# Exists
exists = user_repo.exists(user.id)
```

#### Bulk Operations

High-performance bulk operations for large datasets.

```python
# Bulk create
users_data = [
    {"name": f"User {i}", "email": f"user{i}@example.com"}
    for i in range(1000)
]
users = user_repo.bulk_create(users_data)

# Bulk update
updates = [
    {"id": user.id, "name": f"Updated {user.name}"}
    for user in users[:100]
]
count = user_repo.bulk_update(updates)

# Bulk delete
ids = [user.id for user in users[100:200]]
count = user_repo.bulk_delete(ids, soft=True)
```

#### Unit of Work

Transaction management with automatic commit/rollback.

```python
from core.database import UnitOfWork, get_db_manager

db_manager = get_db_manager()

# Simple transaction
with UnitOfWork(db_manager, user_id="user123") as uow:
    user_repo = uow.get_repository(User, enable_audit=True)
    order_repo = uow.get_repository(Order, enable_audit=True)
    
    user = user_repo.create(name="John", email="john@example.com")
    order = order_repo.create(user_id=user.id, total=100.0)
    
    # Commits automatically on exit

# Transaction with rollback
try:
    with UnitOfWork(db_manager) as uow:
        user_repo = uow.get_repository(User)
        user = user_repo.create(name="Will Rollback", email="rollback@example.com")
        raise Exception("Error!")
except Exception:
    pass  # Transaction rolled back automatically

# Nested transactions (savepoints)
with UnitOfWork(db_manager) as uow1:
    user_repo = uow1.get_repository(User)
    user1 = user_repo.create(name="Outer", email="outer@example.com")
    
    try:
        with UnitOfWork(db_manager) as uow2:
            user2 = user_repo.create(name="Inner", email="inner@example.com")
            raise Exception("Inner error")
    except Exception:
        pass  # Inner rolled back, outer continues
```

#### run_tx Helper

Simplified transaction execution with audit context.

```python
from core.database import run_tx

def create_user_and_order(uow):
    user_repo = uow.get_repository(User)
    order_repo = uow.get_repository(Order)
    
    user = user_repo.create(name="John", email="john@example.com")
    order = order_repo.create(user_id=user.id, total=100.0)
    
    return {"user": user, "order": order}

# Run in transaction with audit context
result = run_tx(
    create_user_and_order,
    user_id="admin",
    session_id="session123",
    correlation_id="req456"
)
```

### Audit Logging

Automatic tracking of all database changes.

```python
from core.database import get_audit_logs, cleanup_audit_logs

# Query audit logs
logs = get_audit_logs(
    resource_type="users",
    resource_id="123",
    user_id="admin",
    action="UPDATE",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    limit=100
)

for log in logs:
    print(f"{log.timestamp}: {log.action} by {log.user_id}")
    print(f"  Old: {log.old_values}")
    print(f"  New: {log.new_values}")

# Cleanup old audit logs
deleted = cleanup_audit_logs(retention_days=90)
print(f"Deleted {deleted} old audit logs")
```

**Audit Log Fields:**
- `user_id`: User who performed the action
- `action`: CREATE, UPDATE, DELETE, SOFT_DELETE, RESTORE, BULK_*
- `resource_type`: Table name
- `resource_id`: Entity ID
- `old_values`: JSON of old values (for updates/deletes)
- `new_values`: JSON of new values (for creates/updates)
- `timestamp`: When the action occurred
- `session_id`: Session identifier
- `correlation_id`: Request correlation ID
- `ip_address`: Client IP (if available)
- `user_agent`: Client user agent (if available)

### Soft Delete

Reversible deletion with restoration capabilities.

```python
# Soft delete (default)
user_repo.delete(user.id, soft=True)

# Entity is hidden from normal queries
user = user_repo.get_by_id(user.id)  # Returns None

# But can be found with include_deleted
users = user_repo.get_all(include_deleted=True)
deleted_user = next(u for u in users if u.id == user.id)
print(f"Deleted at: {deleted_user.deleted_at}")

# Restore
user = user_repo.restore(user.id)
print(f"Restored: {user.name}")

# Hard delete (permanent)
user_repo.delete(user.id, soft=False)
```

**Requirements for Soft Delete:**
- Model must have `deleted_at` column (DateTime, nullable=True)
- Repository automatically filters out soft-deleted entities
- Use `include_deleted=True` to include soft-deleted entities

### Repository Caching

Optional caching for improved performance.

```python
# Create repository with caching
user_repo = Repository(User, db_manager, enable_cache=True)

# First get - from database
user = user_repo.get_by_id(123)

# Second get - from cache (faster)
user = user_repo.get_by_id(123)

# Update invalidates cache
user_repo.update(123, name="Updated")

# Next get - from database again
user = user_repo.get_by_id(123)

# Manual cache invalidation
user_repo._invalidate_cache(123)  # Specific entity
user_repo._invalidate_cache()     # All entities
```

### Performance Monitoring

Track query performance and detect slow queries.

```python
from core.database import get_db_manager

db_manager = get_db_manager()

# Get metrics
metrics = db_manager.get_metrics()
print(f"Query count: {metrics['query_count']}")
print(f"Slow query count: {metrics['slow_query_count']}")
print(f"Error count: {metrics['error_count']}")
print(f"Avg query time: {metrics['avg_query_time']:.4f}s")

# Get slow queries
for query in metrics['slow_queries']:
    print(f"Duration: {query['duration']:.4f}s")
    print(f"Query: {query['query']}")

# Reset metrics
db_manager.reset_metrics()
```

**Metrics Tracked:**
- Total query count
- Slow query count (> 1 second by default)
- Error count
- Total query time
- Average query time
- Connection count
- Last 100 slow queries with details

### Database Health Check

Comprehensive health monitoring.

```python
from core.database import get_db_manager

db_manager = get_db_manager()

health = db_manager.health_check()

print(f"Healthy: {health['healthy']}")
print(f"Database type: {health['database_type']}")
print(f"Connection test: {health['connection_test']}")
print(f"Table count: {health['table_count']}")

# Pool status (PostgreSQL only)
if 'pool_status' in health:
    pool = health['pool_status']
    print(f"Pool size: {pool['size']}")
    print(f"Checked out: {pool['checked_out']}")
    print(f"Available: {pool['checked_in']}")

# Metrics
metrics = health['metrics']
print(f"Query count: {metrics['query_count']}")
print(f"Slow queries: {metrics['slow_query_count']}")
```

### Database Migrations

Alembic integration for schema changes.

```python
from core.database import migrate, init_database

# Initialize database with migrations
init_database(auto_migrate=True)

# Or run migrations manually
success = migrate(auto_run=True)

# Check for pending migrations
migrate(auto_run=False)
```

### Connection Pooling

Automatic connection pooling with health monitoring.

**SQLite/DuckDB:**
- Uses StaticPool (single connection)
- Suitable for development and small deployments

**PostgreSQL:**
- Uses QueuePool with configurable pool size
- Default: pool_size=5, max_overflow=10
- Connection pre-ping for health checks
- Automatic connection recycling (1 hour)
- Connection leak detection

**Configuration:**
```python
from core.config import AppConfig

config = AppConfig(
    database=DatabaseConfig(
        pool_size=10,
        max_overflow=20,
        echo=False  # Set to True for SQL logging
    )
)
```

### Error Handling

Automatic retry and error handling.

```python
from core.database import get_db_manager

db_manager = get_db_manager()

# Automatic retry on connection failure
# Retries up to 3 times with exponential backoff
session = db_manager.get_session()

# Transaction rollback on error
try:
    with UnitOfWork(db_manager) as uow:
        # Operations...
        raise Exception("Error!")
except Exception:
    pass  # Automatically rolled back
```

### Best Practices

1. **Always use Unit of Work for transactions**
   ```python
   with UnitOfWork(db_manager) as uow:
       repo = uow.get_repository(Model)
       # Operations...
   ```

2. **Set audit context for tracking**
   ```python
   repo.set_context(user_id="user123", session_id="session456")
   ```

3. **Use soft delete by default**
   ```python
   repo.delete(entity_id, soft=True)
   ```

4. **Use bulk operations for large datasets**
   ```python
   repo.bulk_create(data_list)
   repo.bulk_update(updates_list)
   ```

5. **Enable caching for read-heavy workloads**
   ```python
   repo = Repository(Model, db_manager, enable_cache=True)
   ```

6. **Monitor performance regularly**
   ```python
   metrics = db_manager.get_metrics()
   health = db_manager.health_check()
   ```

7. **Clean up audit logs periodically**
   ```python
   cleanup_audit_logs(retention_days=90)
   ```

### Database Support

#### SQLite (Development)
```python
DATABASE_URL=sqlite:///./app.db
```

#### DuckDB (Development)
```python
DATABASE_URL=duckdb:///./app.duckdb
```

#### PostgreSQL (Production)
```python
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Performance Tips

1. **Use bulk operations** for inserting/updating many records
2. **Enable caching** for frequently accessed data
3. **Use pagination** instead of loading all records
4. **Monitor slow queries** and add indexes as needed
5. **Use connection pooling** in production (PostgreSQL)
6. **Clean up audit logs** regularly to prevent table bloat
7. **Use soft delete** to avoid foreign key issues

### Troubleshooting

#### Connection Pool Exhausted
```python
# Increase pool size in config
config.database.pool_size = 20
config.database.max_overflow = 40
```

#### Slow Queries
```python
# Check slow queries
metrics = db_manager.get_metrics()
for query in metrics['slow_queries']:
    print(query['query'], query['duration'])

# Add indexes to your models
class User(Base):
    email = Column(String(255), index=True)
```

#### Memory Issues with Large Datasets
```python
# Use pagination
page = repo.paginate(page=1, page_size=100)

# Or use bulk operations
repo.bulk_create(data_list)
```

#### Audit Log Table Too Large
```python
# Clean up old logs
cleanup_audit_logs(retention_days=30)
```

### See Also

- [Configuration Guide](CONFIG_README.md)
- [Migration Guide](MIGRATION_README.md)
- [Example Usage](example_database_usage.py)
- [Test Suite](test_database.py)
