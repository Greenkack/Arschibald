# Database Layer Quick Start

Get started with the enhanced database layer in 5 minutes.

## Installation

The database layer is already included in the core module. No additional installation required.

## Basic Setup

```python
from core.database import init_database, get_db_manager

# Initialize database (runs migrations automatically)
init_database(auto_migrate=True)

# Get database manager
db_manager = get_db_manager()
```

## Define Your Model

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from core.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # For soft delete
```

## Create Repository

```python
from core.database import Repository, get_db_manager

db_manager = get_db_manager()
user_repo = Repository(User, db_manager, enable_audit=True)

# Set audit context (optional but recommended)
user_repo.set_context(
    user_id="current_user_id",
    session_id="current_session_id"
)
```

## CRUD Operations

```python
# CREATE
user = user_repo.create(name="John Doe", email="john@example.com")
print(f"Created user: {user.id}")

# READ
user = user_repo.get_by_id(user.id)
users = user_repo.get_all(limit=10)
users = user_repo.find_by(email="john@example.com")

# UPDATE
user = user_repo.update(user.id, name="Jane Doe")

# DELETE (soft delete by default)
user_repo.delete(user.id, soft=True)

# RESTORE
user = user_repo.restore(user.id)
```

## Transactions

```python
from core.database import UnitOfWork

# Simple transaction
with UnitOfWork(db_manager, user_id="admin") as uow:
    user_repo = uow.get_repository(User)
    order_repo = uow.get_repository(Order)
    
    user = user_repo.create(name="John", email="john@example.com")
    order = order_repo.create(user_id=user.id, total=100.0)
    
    # Commits automatically on exit

# Or use helper function
from core.database import run_tx

def create_user_and_order(uow):
    user_repo = uow.get_repository(User)
    order_repo = uow.get_repository(Order)
    
    user = user_repo.create(name="John", email="john@example.com")
    order = order_repo.create(user_id=user.id, total=100.0)
    
    return {"user": user, "order": order}

result = run_tx(create_user_and_order, user_id="admin")
```

## Bulk Operations

```python
# Bulk create
users_data = [
    {"name": f"User {i}", "email": f"user{i}@example.com"}
    for i in range(100)
]
users = user_repo.bulk_create(users_data)

# Bulk update
updates = [
    {"id": user.id, "name": f"Updated {user.name}"}
    for user in users[:10]
]
count = user_repo.bulk_update(updates)

# Bulk delete
ids = [user.id for user in users[10:20]]
count = user_repo.bulk_delete(ids, soft=True)
```

## Pagination

```python
# Get first page
page = user_repo.paginate(page=1, page_size=20)

print(f"Total: {page['total']}")
print(f"Pages: {page['total_pages']}")
print(f"Items: {len(page['items'])}")

for user in page['items']:
    print(f"  {user.name} - {user.email}")
```

## Audit Logs

```python
from core.database import get_audit_logs

# Query audit logs
logs = get_audit_logs(
    resource_type="users",
    user_id="admin",
    action="CREATE",
    limit=10
)

for log in logs:
    print(f"{log.timestamp}: {log.action} by {log.user_id}")
```

## Health Check

```python
# Check database health
health = db_manager.health_check()

print(f"Healthy: {health['healthy']}")
print(f"Database: {health['database_type']}")
print(f"Tables: {health['table_count']}")

# Get metrics
metrics = health['metrics']
print(f"Queries: {metrics['query_count']}")
print(f"Slow queries: {metrics['slow_query_count']}")
```

## Configuration

Set environment variables:

```bash
# SQLite (development)
DATABASE_URL=sqlite:///./app.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Pool settings (PostgreSQL only)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

## Common Patterns

### Soft Delete Pattern

```python
# Delete (soft)
user_repo.delete(user.id, soft=True)

# User is hidden from normal queries
user = user_repo.get_by_id(user.id)  # Returns None

# But can be found with include_deleted
users = user_repo.get_all(include_deleted=True)

# Restore
user = user_repo.restore(user.id)
```

### Transaction Rollback

```python
try:
    with UnitOfWork(db_manager) as uow:
        user_repo = uow.get_repository(User)
        user = user_repo.create(name="Test", email="test@example.com")
        
        # Something goes wrong
        raise Exception("Error!")
        
except Exception:
    pass  # Transaction automatically rolled back
```

### Caching

```python
# Enable caching
user_repo = Repository(User, db_manager, enable_cache=True)

# First get - from database
user = user_repo.get_by_id(123)

# Second get - from cache (faster)
user = user_repo.get_by_id(123)

# Update invalidates cache
user_repo.update(123, name="Updated")
```

## Next Steps

- Read the [full documentation](DATABASE_README.md)
- Check out [example usage](example_database_usage.py)
- Run the [verification script](verify_database.py)
- Explore [test suite](test_database.py)

## Tips

1. Always use transactions for multiple operations
2. Enable audit logging in production
3. Use soft delete by default
4. Set audit context for tracking
5. Use bulk operations for large datasets
6. Monitor slow queries regularly
7. Clean up audit logs periodically

## Troubleshooting

**Connection errors?**
```python
# Check health
health = db_manager.health_check()
print(health)
```

**Slow queries?**
```python
# Check metrics
metrics = db_manager.get_metrics()
for query in metrics['slow_queries']:
    print(query['query'], query['duration'])
```

**Need to reset?**
```python
# Drop and recreate tables
db_manager.drop_tables()
db_manager.create_tables()
```

## Support

For more information, see:
- [DATABASE_README.md](DATABASE_README.md) - Full documentation
- [example_database_usage.py](example_database_usage.py) - Complete examples
- [test_database.py](test_database.py) - Test suite
