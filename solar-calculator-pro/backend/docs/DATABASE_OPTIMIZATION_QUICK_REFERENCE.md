# Database Optimization Quick Reference

Quick reference for common database optimization tasks.

## Service Initialization

```python
from services.database_optimization_service import DatabaseOptimizationService

service = DatabaseOptimizationService(engine)
```

## Query Optimization

```python
# Analyze query
result = service.analyze_query("SELECT * FROM users WHERE email = 'user@example.com'")
print(f"Time: {result['execution_time_ms']}ms")
print(f"Issues: {result['issues']}")
print(f"Suggestions: {result['suggestions']}")
```

## Index Management

```python
# Get all indexes
indexes = service.get_indexes()

# Get indexes for table
user_indexes = service.get_indexes("users")

# Analyze index usage
analysis = service.analyze_index_usage("users")

# Create index
service.create_index("users", ["email"])

# Create unique index
service.create_index("users", ["email"], unique=True)

# Create composite index
service.create_index("orders", ["user_id", "order_date"])

# Drop index
service.drop_index("idx_users_email")
```

## Partitioning Analysis

```python
# Find partitioning candidates
candidates = service.analyze_partitioning_candidates()

for c in candidates:
    print(f"{c['table_name']}: {c['row_count']} rows")
```

## Data Archiving

```python
from datetime import datetime, timedelta

# Find archiving candidates
candidates = service.analyze_archiving_candidates(age_threshold_days=365)

# Archive old data
threshold = datetime.now() - timedelta(days=365)
result = service.archive_old_data(
    table_name="users",
    date_column="created_at",
    threshold_date=threshold
)
print(f"Archived: {result['archived_count']} records")
```

## Maintenance Operations

```python
# Run VACUUM
vacuum_result = service.vacuum_database()
print(f"Space freed: {vacuum_result['space_freed_mb']} MB")

# Run ANALYZE
analyze_result = service.analyze_tables()

# Analyze specific tables
analyze_result = service.analyze_tables(["users", "orders"])

# Configure maintenance schedule
schedule = service.schedule_maintenance(
    vacuum_enabled=True,
    analyze_enabled=True,
    vacuum_schedule="weekly",
    analyze_schedule="daily"
)
```

## Performance Monitoring

```python
# Get performance metrics
metrics = service.get_performance_metrics()
print(f"DB Size: {metrics['database_size_mb']} MB")
print(f"Tables: {metrics['table_count']}")
print(f"Rows: {metrics['total_rows']}")
print(f"Indexes: {metrics['total_indexes']}")

# Generate optimization report
report = service.get_optimization_report()
print(f"Recommendations: {report['recommendations']}")
```

## API Endpoints

### Query Optimization
```bash
# Analyze query
POST /api/v1/database-optimization/query/analyze
{
  "query": "SELECT * FROM users WHERE email = 'user@example.com'"
}

# Get slow queries
GET /api/v1/database-optimization/query/slow?threshold_ms=1000&limit=10
```

### Index Management
```bash
# Get indexes
GET /api/v1/database-optimization/indexes
GET /api/v1/database-optimization/indexes?table_name=users

# Analyze index usage
GET /api/v1/database-optimization/indexes/analyze/users

# Create index
POST /api/v1/database-optimization/indexes/create
{
  "table_name": "users",
  "columns": ["email"],
  "unique": true
}

# Drop index
DELETE /api/v1/database-optimization/indexes/idx_users_email
```

### Partitioning
```bash
# Get partitioning candidates
GET /api/v1/database-optimization/partitioning/candidates
```

### Archiving
```bash
# Get archiving candidates
GET /api/v1/database-optimization/archiving/candidates?age_threshold_days=365

# Archive old data
POST /api/v1/database-optimization/archiving/archive
{
  "table_name": "users",
  "date_column": "created_at",
  "threshold_date": "2023-01-01T00:00:00",
  "archive_table_suffix": "_archive"
}
```

### Maintenance
```bash
# Run VACUUM
POST /api/v1/database-optimization/maintenance/vacuum

# Run ANALYZE
POST /api/v1/database-optimization/maintenance/analyze
POST /api/v1/database-optimization/maintenance/analyze?table_names=users&table_names=orders

# Configure schedule
POST /api/v1/database-optimization/maintenance/schedule
{
  "vacuum_enabled": true,
  "analyze_enabled": true,
  "vacuum_schedule": "weekly",
  "analyze_schedule": "daily"
}
```

### Monitoring
```bash
# Get performance metrics
GET /api/v1/database-optimization/metrics

# Get optimization report
GET /api/v1/database-optimization/report
```

## Common Patterns

### Daily Maintenance
```python
# Run ANALYZE daily
service.analyze_tables()
```

### Weekly Maintenance
```python
# Run VACUUM weekly
service.vacuum_database()

# Review optimization report
report = service.get_optimization_report()
```

### Monthly Optimization
```python
# Analyze all indexes
for table in inspector.get_table_names():
    analysis = service.analyze_index_usage(table)
    if analysis['recommendations']:
        print(f"{table}: {analysis['recommendations']}")

# Check archiving candidates
candidates = service.analyze_archiving_candidates(365)
if candidates:
    # Archive old data
    for candidate in candidates:
        threshold = datetime.fromisoformat(candidate['threshold_date'])
        service.archive_old_data(
            candidate['table_name'],
            candidate['date_column'],
            threshold
        )
```

### Performance Troubleshooting
```python
# 1. Check metrics
metrics = service.get_performance_metrics()

# 2. Analyze slow queries
slow_queries = service.get_slow_queries(threshold_ms=1000)

# 3. Check index usage
for table in tables:
    analysis = service.analyze_index_usage(table)

# 4. Run maintenance
service.analyze_tables()
service.vacuum_database()
```

## Best Practices

### Index Creation
- Index columns used in WHERE clauses
- Index columns used in JOIN conditions
- Index columns used in ORDER BY
- Use composite indexes for multi-column queries
- Avoid over-indexing (slows INSERT/UPDATE)

### Maintenance Schedule
- **ANALYZE**: Daily or after bulk operations
- **VACUUM**: Weekly or monthly
- **Index Review**: Monthly
- **Archiving**: Quarterly

### Performance Monitoring
- Monitor database size weekly
- Track query performance
- Review optimization reports monthly
- Act on recommendations promptly

### Data Management
- Archive data older than 1-2 years
- Implement retention policies
- Regular backups before major operations
- Test optimizations in staging first

## Troubleshooting

### Slow Queries
1. Analyze query with `analyze_query()`
2. Check for missing indexes
3. Review query plan
4. Implement suggested optimizations

### Large Database Size
1. Run VACUUM to reclaim space
2. Check for archiving candidates
3. Archive old data
4. Review data retention policies

### Poor Performance
1. Get performance metrics
2. Generate optimization report
3. Review recommendations
4. Implement optimizations
5. Monitor impact

## Related Commands

```bash
# Run demo
python demo_database_optimization.py

# Run tests
pytest tests/test_database_optimization_service.py -v

# Check coverage
pytest tests/test_database_optimization_service.py --cov=services.database_optimization_service
```

## See Also

- [Database Optimization Guide](DATABASE_OPTIMIZATION_GUIDE.md) - Complete documentation
- [Database Backup Guide](DATABASE_BACKUP_GUIDE.md) - Backup and restore
- [Migration System Guide](MIGRATION_SYSTEM_GUIDE.md) - Data migration
