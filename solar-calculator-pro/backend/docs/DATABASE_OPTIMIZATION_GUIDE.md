# Database Optimization Guide

Complete guide for database optimization and performance management in the Solar Calculator Pro application.

## Table of Contents

1. [Overview](#overview)
2. [Query Optimization](#query-optimization)
3. [Index Management](#index-management)
4. [Table Partitioning](#table-partitioning)
5. [Data Archiving](#data-archiving)
6. [Maintenance Operations](#maintenance-operations)
7. [Performance Monitoring](#performance-monitoring)
8. [Best Practices](#best-practices)
9. [API Reference](#api-reference)

## Overview

The Database Optimization Service provides comprehensive tools for maintaining and optimizing database performance:

- **Query Analysis**: Analyze query performance and get optimization suggestions
- **Index Management**: Create, analyze, and manage database indexes
- **Partitioning Analysis**: Identify tables that could benefit from partitioning
- **Data Archiving**: Archive old data to improve performance
- **Maintenance Operations**: Automated VACUUM and ANALYZE operations
- **Performance Monitoring**: Track database metrics and generate reports

### Key Benefits

- Improved query performance
- Reduced database size
- Better resource utilization
- Automated maintenance
- Comprehensive monitoring

## Query Optimization

### Analyzing Queries

Analyze query performance and get optimization suggestions:

```python
from services.database_optimization_service import DatabaseOptimizationService

service = DatabaseOptimizationService(engine)

# Analyze a query
query = "SELECT * FROM users WHERE email = 'user@example.com'"
result = service.analyze_query(query)

print(f"Execution time: {result['execution_time_ms']}ms")
print(f"Issues: {result['issues']}")
print(f"Suggestions: {result['suggestions']}")
```

### Query Plan Analysis

The service analyzes the query execution plan to identify:

- Full table scans
- Missing indexes
- Temporary table usage
- Inefficient sorting
- Suboptimal JOIN conditions

### Optimization Suggestions

Based on the analysis, the service provides actionable suggestions:

- Add indexes on frequently queried columns
- Optimize JOIN conditions
- Use covering indexes
- Add indexes for ORDER BY clauses

## Index Management

### Getting Indexes

List all indexes or indexes for a specific table:

```python
# Get all indexes
all_indexes = service.get_indexes()

# Get indexes for specific table
user_indexes = service.get_indexes("users")
```

### Analyzing Index Usage

Analyze index effectiveness and get recommendations:

```python
analysis = service.analyze_index_usage("users")

print(f"Row count: {analysis['row_count']}")
print(f"Indexes: {len(analysis['indexes'])}")
print(f"Recommendations: {analysis['recommendations']}")
```

### Creating Indexes

Create indexes to improve query performance:

```python
# Simple index
result = service.create_index(
    table_name="users",
    columns=["email"]
)

# Unique index
result = service.create_index(
    table_name="users",
    columns=["email"],
    unique=True
)

# Composite index
result = service.create_index(
    table_name="orders",
    columns=["user_id", "order_date"]
)

# Custom index name
result = service.create_index(
    table_name="users",
    columns=["email"],
    index_name="idx_users_email_unique"
)
```

### Dropping Indexes

Remove unused or redundant indexes:

```python
result = service.drop_index("idx_users_email")
```

### Index Best Practices

1. **Index Frequently Queried Columns**: Add indexes on columns used in WHERE, JOIN, and ORDER BY clauses
2. **Use Composite Indexes**: For queries with multiple conditions
3. **Avoid Over-Indexing**: Too many indexes slow down INSERT/UPDATE operations
4. **Monitor Index Usage**: Regularly analyze and remove unused indexes
5. **Consider Unique Indexes**: For columns with unique values

## Table Partitioning

### Analyzing Partitioning Candidates

Identify tables that could benefit from partitioning:

```python
candidates = service.analyze_partitioning_candidates()

for candidate in candidates:
    print(f"Table: {candidate['table_name']}")
    print(f"Row count: {candidate['row_count']}")
    print(f"Partition columns: {candidate['partition_columns']}")
    print(f"Strategy: {candidate['strategy']}")
```

### Partitioning Strategies

The service recommends partitioning for:

- Large tables (>100,000 rows)
- Tables with date/timestamp columns
- Tables with range-based queries
- Tables with historical data

### Partitioning Benefits

- Improved query performance
- Easier data management
- Better maintenance operations
- Simplified archiving

## Data Archiving

### Finding Archiving Candidates

Identify tables with old data suitable for archiving:

```python
# Find data older than 365 days
candidates = service.analyze_archiving_candidates(age_threshold_days=365)

for candidate in candidates:
    print(f"Table: {candidate['table_name']}")
    print(f"Old records: {candidate['old_records_count']}")
    print(f"Recommendation: {candidate['recommendation']}")
```

### Archiving Old Data

Move old data to archive tables:

```python
from datetime import datetime, timedelta

threshold_date = datetime.now() - timedelta(days=365)

result = service.archive_old_data(
    table_name="users",
    date_column="created_at",
    threshold_date=threshold_date,
    archive_table_suffix="_archive"
)

print(f"Archived {result['archived_count']} records")
print(f"Archive table: {result['archive_table']}")
```

### Archiving Process

1. Creates archive table (if it doesn't exist)
2. Copies old records to archive table
3. Deletes archived records from main table
4. Maintains data integrity

### Archiving Benefits

- Reduced main table size
- Improved query performance
- Better backup efficiency
- Preserved historical data

## Maintenance Operations

### VACUUM Operation

Reclaim space and defragment the database:

```python
result = service.vacuum_database()

print(f"Duration: {result['duration_seconds']}s")
print(f"Space freed: {result['space_freed_mb']} MB")
print(f"Size before: {result['size_before_bytes']} bytes")
print(f"Size after: {result['size_after_bytes']} bytes")
```

### ANALYZE Operation

Update statistics for the query optimizer:

```python
# Analyze all tables
result = service.analyze_tables()

# Analyze specific tables
result = service.analyze_tables(table_names=["users", "orders"])

print(f"Duration: {result['duration_seconds']}s")
```

### Maintenance Schedule

Configure automatic maintenance:

```python
schedule = service.schedule_maintenance(
    vacuum_enabled=True,
    analyze_enabled=True,
    vacuum_schedule="weekly",
    analyze_schedule="daily"
)
```

### Recommended Schedule

- **ANALYZE**: Daily or after significant data changes
- **VACUUM**: Weekly or monthly, depending on database activity
- **Index Analysis**: Monthly
- **Archiving**: Quarterly or as needed

## Performance Monitoring

### Getting Performance Metrics

Get comprehensive database metrics:

```python
metrics = service.get_performance_metrics()

print(f"Database size: {metrics['database_size_mb']} MB")
print(f"Total tables: {metrics['table_count']}")
print(f"Total rows: {metrics['total_rows']}")
print(f"Total indexes: {metrics['total_indexes']}")

# Table statistics
for stat in metrics['table_statistics']:
    print(f"{stat['table_name']}: {stat['row_count']} rows")
```

### Optimization Report

Generate comprehensive optimization analysis:

```python
report = service.get_optimization_report()

# Performance metrics
print(report['performance_metrics'])

# Index analysis for each table
print(report['index_analysis'])

# Partitioning candidates
print(report['partitioning_candidates'])

# Archiving candidates
print(report['archiving_candidates'])

# Overall recommendations
print(report['recommendations'])
```

### Monitoring Best Practices

1. **Regular Monitoring**: Check metrics weekly
2. **Track Trends**: Monitor growth over time
3. **Set Alerts**: Configure alerts for thresholds
4. **Review Reports**: Analyze optimization reports monthly
5. **Act on Recommendations**: Implement suggested optimizations

## Best Practices

### Query Optimization

- Use indexes on frequently queried columns
- Avoid SELECT * in production queries
- Use LIMIT for large result sets
- Optimize JOIN conditions
- Use prepared statements

### Index Management

- Create indexes based on query patterns
- Use composite indexes for multi-column queries
- Remove unused indexes
- Monitor index size
- Balance read vs. write performance

### Data Management

- Archive old data regularly
- Implement data retention policies
- Use appropriate data types
- Normalize database structure
- Avoid storing large BLOBs in database

### Maintenance

- Run VACUUM regularly
- Update statistics with ANALYZE
- Monitor database size
- Check for fragmentation
- Backup before major operations

### Performance

- Monitor query execution times
- Track database growth
- Optimize slow queries
- Use connection pooling
- Implement caching strategies

## API Reference

### DatabaseOptimizationService

Main service class for database optimization.

#### Methods

##### Query Optimization

- `analyze_query(query: str)` - Analyze query performance
- `get_slow_queries(threshold_ms: float, limit: int)` - Get slow queries

##### Index Management

- `get_indexes(table_name: Optional[str])` - Get indexes
- `analyze_index_usage(table_name: str)` - Analyze index usage
- `create_index(table_name, columns, index_name, unique)` - Create index
- `drop_index(index_name: str)` - Drop index

##### Partitioning

- `analyze_partitioning_candidates()` - Find partitioning candidates

##### Archiving

- `analyze_archiving_candidates(age_threshold_days)` - Find archiving candidates
- `archive_old_data(table_name, date_column, threshold_date)` - Archive old data

##### Maintenance

- `vacuum_database()` - Run VACUUM
- `analyze_tables(table_names)` - Run ANALYZE
- `schedule_maintenance(...)` - Configure maintenance schedule

##### Monitoring

- `get_performance_metrics()` - Get performance metrics
- `get_optimization_report()` - Generate optimization report

### API Endpoints

All endpoints are available under `/api/v1/database-optimization`:

#### Query Optimization
- `POST /query/analyze` - Analyze query
- `GET /query/slow` - Get slow queries

#### Index Management
- `GET /indexes` - Get indexes
- `GET /indexes/analyze/{table_name}` - Analyze index usage
- `POST /indexes/create` - Create index
- `DELETE /indexes/{index_name}` - Drop index

#### Partitioning
- `GET /partitioning/candidates` - Get partitioning candidates

#### Archiving
- `GET /archiving/candidates` - Get archiving candidates
- `POST /archiving/archive` - Archive old data

#### Maintenance
- `POST /maintenance/vacuum` - Run VACUUM
- `POST /maintenance/analyze` - Run ANALYZE
- `POST /maintenance/schedule` - Configure schedule

#### Monitoring
- `GET /metrics` - Get performance metrics
- `GET /report` - Get optimization report

## Troubleshooting

### Common Issues

**Issue**: Slow queries after adding indexes
- **Solution**: Run ANALYZE to update statistics

**Issue**: Database size not decreasing after deleting data
- **Solution**: Run VACUUM to reclaim space

**Issue**: Index creation fails
- **Solution**: Check for duplicate index names or invalid columns

**Issue**: Archive operation fails
- **Solution**: Verify date column exists and has correct data type

### Performance Tips

1. **Index Selectivity**: Create indexes on columns with high selectivity
2. **Query Patterns**: Analyze actual query patterns before creating indexes
3. **Maintenance Windows**: Schedule VACUUM during low-traffic periods
4. **Incremental Archiving**: Archive data in batches for large tables
5. **Monitor Impact**: Track performance before and after optimizations

## Examples

See `demo_database_optimization.py` for comprehensive examples of all features.

## Requirements

- SQLAlchemy 2.0+
- Python 3.10+
- SQLite 3.35+ (or other supported database)

## Related Documentation

- [Database Backup Guide](DATABASE_BACKUP_GUIDE.md)
- [Migration System Guide](MIGRATION_SYSTEM_GUIDE.md)
- [Performance Optimization Guide](../../../docs/BACKEND_PERFORMANCE_GUIDE.md)
