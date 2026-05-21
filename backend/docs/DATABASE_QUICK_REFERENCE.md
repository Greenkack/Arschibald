# Database Setup Quick Reference

Quick reference for common database operations.

## Import Statements

```python
# Sync operations
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, get_db, transaction
from backend.models.database_models import User, Customer, Project

# Async operations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import AsyncSessionLocal, get_async_db, async_transaction

# Dependencies
from fastapi import Depends
from backend.core.dependencies import (
    get_database_session,
    get_pagination_params,
    PaginationParams,
)
```

## Basic CRUD Operations

### Create

```python
# Sync
db = SessionLocal()
user = User(username="john", email="john@example.com")
db.add(user)
db.commit()
db.refresh(user)
db.close()

# Async
async with AsyncSessionLocal() as session:
    user = User(username="jane", email="jane@example.com")
    session.add(user)
    await session.commit()
    await session.refresh(user)
```

### Read

```python
# Sync
db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
users = db.query(User).all()
db.close()

# Async
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User).filter(User.id == 1))
    user = result.scalar_one_or_none()
    
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Update

```python
# Sync
db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
user.email = "newemail@example.com"
db.commit()
db.close()

# Async
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User).filter(User.id == 1))
    user = result.scalar_one()
    user.email = "newemail@example.com"
    await session.commit()
```

### Delete

```python
# Sync
db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()
db.close()

# Async
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User).filter(User.id == 1))
    user = result.scalar_one()
    await session.delete(user)
    await session.commit()
```

## FastAPI Endpoints

### Sync Endpoint

```python
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### Async Endpoint

```python
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@app.post("/users")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

## Transactions

### Sync Transaction

```python
from backend.core.database import transaction

db = SessionLocal()
try:
    with transaction(db) as tx:
        user = User(username="john")
        tx.add(user)
        # Auto-commits on success
finally:
    db.close()
```

### Async Transaction

```python
from backend.core.database import async_transaction

async with AsyncSessionLocal() as session:
    async with async_transaction(session) as tx:
        user = User(username="jane")
        tx.add(user)
        # Auto-commits on success
```

## Pagination

```python
@app.get("/users")
def get_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    query = db.query(User)
    return pagination.apply_to_query(query).all()

# Usage: GET /users?skip=0&limit=10
```

## Batch Operations

```python
from backend.core.dependencies import BatchOperationContext

db = SessionLocal()
try:
    with BatchOperationContext(db, batch_size=100) as batch:
        for i in range(1000):
            user = User(username=f"user{i}")
            batch.add(user)
finally:
    db.close()
```

## Alembic Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

## Database Initialization

```python
from backend.core.database import init_db, init_async_db

# Sync
init_db()

# Async
await init_async_db()
```

## Health Checks

```python
from backend.core.database import check_db_connection, check_async_db_connection

# Sync
if check_db_connection():
    print("Database is healthy")

# Async
if await check_async_db_connection():
    print("Database is healthy")
```

## Connection Pool Stats

```python
from backend.core.database import get_db_stats

stats = get_db_stats()
print(f"Pool size: {stats['pool_size']}")
print(f"Checked out: {stats['checked_out']}")
```

## Common Queries

### Filter

```python
# Sync
users = db.query(User).filter(User.role == "admin").all()

# Async
result = await session.execute(select(User).filter(User.role == "admin"))
users = result.scalars().all()
```

### Order By

```python
# Sync
users = db.query(User).order_by(User.created_at.desc()).all()

# Async
result = await session.execute(select(User).order_by(User.created_at.desc()))
users = result.scalars().all()
```

### Limit and Offset

```python
# Sync
users = db.query(User).offset(10).limit(5).all()

# Async
result = await session.execute(select(User).offset(10).limit(5))
users = result.scalars().all()
```

### Count

```python
# Sync
count = db.query(User).count()

# Async
from sqlalchemy import func
result = await session.execute(select(func.count(User.id)))
count = result.scalar()
```

### Join

```python
# Sync
results = db.query(User, Project).join(Project, User.id == Project.customer_id).all()

# Async
result = await session.execute(
    select(User, Project).join(Project, User.id == Project.customer_id)
)
results = result.all()
```

## Error Handling

```python
from sqlalchemy.exc import IntegrityError

try:
    db.add(user)
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=400, detail="User already exists")
finally:
    db.close()
```

## Configuration

```env
DATABASE_URL=sqlite:///./solar_calculator.db
DATABASE_ECHO=False
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

## Testing

```python
import pytest
from backend.core.database import init_db, SessionLocal

@pytest.fixture
def db():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_create_user(db):
    user = User(username="test")
    db.add(user)
    db.commit()
    assert user.id is not None
```
