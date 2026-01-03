# Database Service Guide

## Overview

The `DatabaseService` is a comprehensive wrapper around the existing `database.py` functionality, providing:

- **CRUD Operations**: Generic create, read, update, delete operations for all entities
- **Query Optimization**: Index management and query analysis
- **Transaction Management**: ACID-compliant transactions with automatic rollback
- **Connection Pooling**: Efficient connection management for better performance
- **Backup & Restore**: Automated database backup and restore utilities
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Legacy Compatibility**: Seamless integration with existing database.py functions

## Installation

```python
from backend.services.database_service import DatabaseService, get_database_service

# Create service instance
db_service = DatabaseService()

# Or use singleton
db_service = get_database_service()
```

## Basic Usage

### CRUD Operations

#### Create

```python
# Create a new record
data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
}
record_id = db_service.create('users', data)
print(f"Created record with ID: {record_id}")
```

#### Read

```python
# Read single record
user = db_service.read('users', record_id)
print(f"User: {user['name']}")

# Read all records
all_users = db_service.read_all('users')

# Read with filters
active_users = db_service.read_all('users', filters={'status': 'active'})

# Read with ordering and limit
recent_users = db_service.read_all('users', order_by='created_at DESC', limit=10)
```

#### Update

```python
# Update record
update_data = {'email': 'newemail@example.com'}
success = db_service.update('users', record_id, update_data)
```

#### Delete

```python
# Delete record
success = db_service.delete('users', record_id)
```

### Transaction Management

```python
# Automatic transaction with commit/rollback
try:
    with db_service.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (?)", ('Alice',))
        cursor.execute("INSERT INTO orders (user_id, amount) VALUES (?, ?)", (1, 100.0))
        # Automatically commits if no exception
except TransactionError as e:
    print(f"Transaction failed: {e}")
    # Automatically rolled back
```

### Custom Queries

```python
# Execute custom query
results = db_service.execute_query(
    "SELECT * FROM users WHERE age > ? AND status = ?",
    (25, 'active')
)

# Batch operations
data_list = [
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com')
]
count = db_service.execute_many(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    data_list
)
```

## Query Optimization

### Create Indexes

```python
# Create single column index
db_service.create_index('users', ['email'])

# Create multi-column index
db_service.create_index('orders', ['user_id', 'created_at'])

# Create unique index
db_service.create_index('users', ['email'], unique=True)
```

### Analyze Tables

```python
# Get table analysis
analysis = db_service.analyze_table('users')
print(f"Table: {analysis['table']}")
print(f"Columns: {len(analysis['columns'])}")
print(f"Indexes: {len(analysis['indexes'])}")
print(f"Row count: {analysis['row_count']}")
```

### Optimize Database

```python
# Run VACUUM and ANALYZE
db_service.optimize_database()
```

## Backup and Restore

### Create Backup

```python
# Automatic backup with timestamp
backup_path = db_service.backup()
print(f"Backup created: {backup_path}")

# Custom backup path
backup_path = db_service.backup('/path/to/custom/backup.db')
```

### Restore from Backup

```python
# Restore database
success = db_service.restore('/path/to/backup.db')
```

### List Backups

```python
# Get all available backups
backups = db_service.list_backups()
for backup in backups:
    print(f"{backup['filename']}: {backup['size_mb']} MB, {backup['created_at']}")
```

## Legacy Database Functions

The service provides wrappers for all existing database.py functions:

```python
# Admin settings
value = db_service.get_admin_setting('key', default='default_value')
db_service.set_admin_setting('key', 'new_value')

# Pricing mode
mode = db_service.get_pricing_mode()  # 'standard' or 'matrix'
db_service.set_pricing_mode('matrix')

# Brand logos
logo_base64 = db_service.get_brand_logo('BrandName')

# Customer documents
doc_id = db_service.add_customer_document(
    customer_id=1,
    file_bytes=pdf_bytes,
    display_name='Invoice.pdf',
    doc_type='invoice'
)

docs = db_service.list_customer_documents(customer_id=1)
db_service.delete_customer_document(doc_id)

# Settings import/export
settings = db_service.export_settings()
db_service.import_settings(settings)

# Statistics and validation
stats = db_service.get_statistics()
integrity = db_service.validate_integrity()
```

## Health Monitoring

```python
# Check database health
health = db_service.health_check()
print(f"Status: {health['status']}")
print(f"Pool size: {health['connection_pool_size']}")
print(f"DB size: {health['database_size_mb']} MB")

# Get table list
tables = db_service.get_table_list()
print(f"Tables: {', '.join(tables)}")
```

## Connection Management

### Using Context Manager

```python
# Automatic connection management
with db_service.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
# Connection automatically returned to pool
```

### Service as Context Manager

```python
# Automatic cleanup
with DatabaseService() as service:
    # Use service
    users = service.read_all('users')
# Service automatically closed
```

## Error Handling

The service provides custom exceptions for different error types:

```python
from backend.services.database_service import (
    DatabaseError,
    ConnectionError,
    TransactionError,
    QueryError
)

try:
    db_service.create('users', {'invalid_column': 'value'})
except DatabaseError as e:
    print(f"Database error: {e}")

try:
    with db_service.transaction() as conn:
        # ... operations
        raise Exception("Something went wrong")
except TransactionError as e:
    print(f"Transaction failed and rolled back: {e}")
```

## Best Practices

1. **Use Transactions**: Always use transactions for multiple related operations
2. **Create Indexes**: Add indexes for frequently queried columns
3. **Regular Backups**: Schedule regular backups before major operations
4. **Connection Pooling**: Reuse the singleton instance for better performance
5. **Error Handling**: Always handle DatabaseError exceptions
6. **Optimize Regularly**: Run optimize_database() periodically
7. **Monitor Health**: Check health_check() in production environments

## Performance Tips

1. **Batch Operations**: Use `execute_many()` for bulk inserts
2. **Limit Results**: Use `limit` parameter when reading large datasets
3. **Index Strategy**: Create indexes on foreign keys and frequently filtered columns
4. **Connection Pool**: Adjust pool size based on concurrent usage
5. **WAL Mode**: Service automatically enables WAL mode for better concurrency

## Requirements Satisfied

- **Requirement 1.2**: Database logic integration from legacy system
- **Requirement 5.1**: Data migration and compatibility
- **Requirement 8.4**: Database query optimization with indexing

## API Reference

See inline documentation in `backend/services/database_service.py` for complete API reference.
