# Database Setup and Configuration Guide

Complete guide for the database setup with SQLAlchemy async support, connection pooling, session management, and Alembic migrations.

**Requirements:** 1.2, 1.5

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Configuration](#configuration)
4. [Database Engines](#database-engines)
5. [Session Management](#session-management)
6. [Async Support](#async-support)
7. [Connection Pooling](#connection-pooling)
8. [Transaction Management](#transaction-management)
9. [Dependencies](#dependencies)
10. [Alembic Migrations](#alembic-migrations)
11. [Best Practices](#best-practices)

## Overview

The database setup provides a robust foundation for data persistence with:

- **Dual Mode Support**: Both synchronous and asynchronous operations
- **Connection Pooling**: Efficient connection management
- **Transaction Management**: ACID-compliant transactions
- **Migration Support**: Alembic for schema versioning
- **Type Safety**: Full SQLAlchemy ORM support

## Features

### ✅ Synchronous Database Operations
- Traditional SQLAlchemy ORM
- Session management with context managers
- Transaction support
- Connection pooling

### ✅ Asynchronous Database Operations
- Async SQLAlchemy support
- AsyncSession for non-blocking I/O
- Async transaction management
- Async connection pooling

### ✅ Connection Pooling
- QueuePool for PostgreSQL/MySQL
- NullPool for SQLite
- Configurable pool size and overflow
- Connection health checks

### ✅ Migration Support
- Alembic integration
- Auto-generate migrations
- Version control for schema
- Rollback support

## Configuration

### Environment Variables

```env
# Database Configuration
DATABASE_URL=sqlite:///./solar_calculator.db
DATABASE_ECHO=False
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### Supported Databases

| Database | Sync URL | Async URL |
|----------|----------|-----------|
| SQLite | `sqlite:///./db.db` | `sqlite+aiosqlite:///./db.db` |
| PostgreSQL | `postgresql://user:pass@host/db` | `postgresql+asyncpg://user:pass@host/db` |
| MySQL | `mysql://user:pass@host/db` | `mysql+aiomysql://user:pass@host/db` |

## Database Engines

### Synchronous Engine

```python
from backend.core.database import engine, SessionLocal

# Use the engine directly
with engine.connect() as conn:
    result = conn.execute("SELECT 1")

# Or use sessions
db = SessionLocal()
try:
    users = db.query(User).all()
finally:
    db.close()
```

### Asynchronous Engine

```python
from backend.core.database import async_engine, AsyncSessionLocal

# Use async engine
async with async_engine.connect() as conn:
    result = await conn.execute("SELECT 1")

# Or use async sessions
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

## Session Management

### Basic Session Usage

```python
from backend.core.database import SessionLocal

db = SessionLocal()
try:
    # Your database operations
    user = db.query(User).first()
except Exception as e:
    db.rollback()
    raise
finally:
    db.close()
```

### Dependency Injection (FastAPI)

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Async Session Usage

```python
from backend.core.database import AsyncSessionLocal
from sqlalchemy import select

async with AsyncSessionLocal() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Async Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_async_db

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## Async Support

### Why Async?

- **Non-blocking I/O**: Handle multiple requests concurrently
- **Better Performance**: Especially for I/O-bound operations
- **Scalability**: Handle more concurrent connections

### Async Example

```python
from sqlalchemy import select
from backend.core.database import AsyncSessionLocal
from backend.models.database_models import User

async def get_user_by_email(email: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).filter(User.email == email)
        )
        return result.scalar_one_or_none()

async def create_user(username: str, email: str):
    async with AsyncSessionLocal() as session:
        user = User(username=username, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
```

## Connection Pooling

### Pool Configuration

```python
# In backend/core/config.py
DATABASE_POOL_SIZE = 5          # Number of connections to maintain
DATABASE_MAX_OVERFLOW = 10      # Additional connections when pool is full
DATABASE_POOL_TIMEOUT = 30      # Seconds to wait for connection
DATABASE_POOL_RECYCLE = 3600    # Recycle connections after 1 hour
```

### Pool Statistics

```python
from backend.core.database import get_db_stats

stats = get_db_stats()
print(f"Pool size: {stats['pool_size']}")
print(f"Checked in: {stats['checked_in']}")
print(f"Checked out: {stats['checked_out']}")
```

### SQLite Optimizations

For SQLite, the following pragmas are automatically set:

- `journal_mode=WAL`: Write-Ahead Logging for better concurrency
- `synchronous=NORMAL`: Balance between safety and speed
- `foreign_keys=ON`: Enable foreign key constraints
- `temp_store=MEMORY`: Store temp tables in memory
- `cache_size=-64000`: 64MB cache

## Transaction Management

### Sync Transactions

```python
from backend.core.database import SessionLocal, transaction

db = SessionLocal()
try:
    with transaction(db) as tx:
        user = User(username="john")
        tx.add(user)
        # Automatically commits on success
        # Automatically rolls back on error
finally:
    db.close()
```

### Async Transactions

```python
from backend.core.database import AsyncSessionLocal, async_transaction

async with AsyncSessionLocal() as session:
    async with async_transaction(session) as tx:
        user = User(username="jane")
        tx.add(user)
        # Automatically commits on success
```

### Manual Transaction Control

```python
db = SessionLocal()
try:
    user = User(username="bob")
    db.add(user)
    db.commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()
```

## Dependencies

### Available Dependencies

```python
from backend.core.dependencies import (
    get_database_session,           # Basic session
    get_async_database_session,     # Async session
    get_db_with_transaction,        # Session with auto-transaction
    get_async_db_with_transaction,  # Async session with auto-transaction
    get_readonly_db,                # Read-only session
    get_async_readonly_db,          # Async read-only session
    get_pagination_params,          # Pagination helper
    get_batch_operation_context,    # Batch operations
)
```

### Pagination Example

```python
from fastapi import Depends
from backend.core.dependencies import get_pagination_params, PaginationParams

@app.get("/users")
def get_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    query = db.query(User)
    return pagination.apply_to_query(query).all()
```

### Batch Operations Example

```python
from backend.core.dependencies import get_batch_operation_context

@app.post("/users/batch")
def create_users_batch(
    users: List[UserCreate],
    batch_ctx: BatchOperationContext = Depends(get_batch_operation_context)
):
    for user_data in users:
        user = User(**user_data.dict())
        batch_ctx.add(user)
    return {"created": len(users)}
```

## Alembic Migrations

### Initialize Alembic

Alembic is already configured. The structure is:

```
backend/
├── alembic/
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment
│   ├── script.py.mako    # Migration template
│   └── README            # Alembic documentation
└── alembic.ini           # Alembic configuration
```

### Create a Migration

```bash
# Auto-generate migration from model changes
cd backend
alembic revision --autogenerate -m "Add user table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Upgrade one step
alembic upgrade +1
```

### Rollback Migrations

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Downgrade to base (remove all)
alembic downgrade base
```

### View Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show verbose history
alembic history --verbose
```

### Migration Example

```python
# alembic/versions/001_add_user_table.py
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_user_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_user_email', 'users')
    op.drop_table('users')
```

## Best Practices

### 1. Always Use Context Managers

```python
# ✅ Good
async with AsyncSessionLocal() as session:
    # Your code here
    pass

# ❌ Bad
session = AsyncSessionLocal()
# Your code here
await session.close()  # Easy to forget!
```

### 2. Use Dependency Injection

```python
# ✅ Good
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# ❌ Bad
@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users
```

### 3. Handle Transactions Properly

```python
# ✅ Good
with transaction(db) as tx:
    user = User(username="john")
    tx.add(user)
    # Auto-commit or rollback

# ❌ Bad
user = User(username="john")
db.add(user)
db.commit()  # No error handling!
```

### 4. Use Async for I/O-Bound Operations

```python
# ✅ Good for multiple I/O operations
async def get_user_with_projects(user_id: int):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        projects = await session.execute(
            select(Project).filter(Project.user_id == user_id)
        )
        return user, projects.scalars().all()
```

### 5. Close Sessions Properly

```python
# ✅ Good
db = SessionLocal()
try:
    # Your operations
    pass
finally:
    db.close()

# ✅ Better
with SessionLocal() as db:
    # Your operations
    pass
```

### 6. Use Pagination for Large Datasets

```python
# ✅ Good
pagination = get_pagination_params(skip=0, limit=100)
query = db.query(User)
users = pagination.apply_to_query(query).all()

# ❌ Bad
users = db.query(User).all()  # Could be millions of records!
```

### 7. Use Batch Operations for Bulk Inserts

```python
# ✅ Good
with BatchOperationContext(db, batch_size=100) as batch:
    for data in large_dataset:
        batch.add(User(**data))

# ❌ Bad
for data in large_dataset:
    db.add(User(**data))
    db.commit()  # Commits for each record!
```

### 8. Monitor Connection Pool

```python
# Regularly check pool statistics
stats = get_db_stats()
if stats['checked_out'] > stats['pool_size'] * 0.8:
    logger.warning("Connection pool is nearly exhausted")
```

## Troubleshooting

### Connection Pool Exhausted

**Problem**: `QueuePool limit of size X overflow Y reached`

**Solution**:
```python
# Increase pool size in config
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
```

### SQLite Database Locked

**Problem**: `database is locked`

**Solution**:
- Use WAL mode (automatically enabled)
- Reduce transaction duration
- Consider PostgreSQL for high concurrency

### Migration Conflicts

**Problem**: Multiple migration heads

**Solution**:
```bash
# Merge migration heads
alembic merge heads -m "Merge migrations"
```

### Async Session Errors

**Problem**: `greenlet_spawn has not been called`

**Solution**:
```bash
# Install greenlet
pip install greenlet
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_database_setup.py -v
```

Run the demo:

```bash
cd backend
python demo_database_setup.py
```

## Summary

The database setup provides:

- ✅ Sync and async support
- ✅ Connection pooling
- ✅ Transaction management
- ✅ Migration support with Alembic
- ✅ Comprehensive dependencies
- ✅ Type-safe ORM
- ✅ Production-ready configuration

For more information, see:
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Database Documentation](https://fastapi.tiangolo.com/tutorial/sql-databases/)
