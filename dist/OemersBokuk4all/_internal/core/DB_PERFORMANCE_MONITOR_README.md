# Database Performance Monitoring System

Comprehensive database performance monitoring with query tracking, slow query detection, health checks, automated alerts, and optimization recommendations.

## Features

- **Query Performance Tracking**: Track all database queries with detailed metrics
- **Slow Query Detection**: Automatically detect and log slow queries
- **Connection Pool Monitoring**: Monitor connection pool usage and health
- **Automated Alerts**: Configurable alerts for performance issues
- **Optimization Recommendations**: AI-powered recommendations for performance improvements
- **Real-time Statistics**: Live performance metrics and dashboards
- **Thread-Safe**: Safe for concurrent use in multi-threaded applications

## Quick Start

### Basic Usage

```python
from core.db_performance_monitor import create_performance_monitor

# Create monitor with default settings
monitor = create_performance_monitor(
    slow_query_threshold=1.0,
    enable_recommendations=True
)

# Record query execution
monitor.record_query(
    query="SELECT * FROM users WHERE id = 1",
    duration=0.15,
    rows_affected=1,
    connection_id="conn_123",
    user_id="user_456"
)

# Get performance statistics
stats = monitor.get_stats()
print(f"Total Queries: {stats.total_queries}")
print(f"Slow Queries: {stats.slow_queries}")
print(f"Average Query Time: {stats.avg_query_time:.3f}s")
print(f"Error Rate: {stats.error_rate:.1%}")
```

### With Custom Thresholds

```python
from core.db_performance_monitor import (
    DatabasePerformanceMonitor,
    PerformanceThresholds
)

# Define custom thresholds
thresholds = PerformanceThresholds(
    slow_query_threshold=0.5,  # 500ms
    very_slow_query_threshold=2.0,  # 2 seconds
    error_rate_threshold=0.1,  # 10%
    connection_pool_usage_threshold=0.8,  # 80%
    avg_query_time_threshold=0.3  # 300ms
)

monitor = DatabasePerformanceMonitor(
    thresholds=thresholds,
    max_slow_queries=100,
    enable_recommendations=True
)
```

### With Alert Callbacks

```python
def alert_handler(alert):
    """Handle performance alerts"""
    print(f"ALERT [{alert.severity.value}]: {alert.message}")
    print(f"Metric: {alert.metric_name}")
    print(f"Current: {alert.current_value}, Threshold: {alert.threshold_value}")
    
    # Send to monitoring system
    send_to_slack(alert)
    send_to_pagerduty(alert)

monitor = create_performance_monitor()
monitor.register_alert_callback(alert_handler)
```

## Core Components

### DatabasePerformanceMonitor

Main monitoring class that tracks all database performance metrics.

```python
monitor = DatabasePerformanceMonitor(
    thresholds=PerformanceThresholds(),
    max_slow_queries=100,
    max_alerts=1000,
    enable_recommendations=True
)
```

### Query Tracking

```python
# Record successful query
monitor.record_query(
    query="SELECT * FROM users WHERE email = ?",
    duration=0.25,
    rows_affected=1,
    connection_id="conn_123",
    user_id="user_456"
)

# Record failed query
monitor.record_query(
    query="SELECT * FROM invalid_table",
    duration=0.1,
    error=Exception("Table does not exist")
)
```

### Connection Pool Monitoring

```python
# Record connection events
monitor.record_connection_event("create", "conn_1")
monitor.record_connection_event("checkout", "conn_1")
monitor.record_connection_event("checkin", "conn_1")
monitor.record_connection_event("error", "conn_2", error=Exception("Connection failed"))

# Update pool metrics
monitor.update_pool_metrics(
    pool_size=10,
    checked_out=7,
    checked_in=3,
    overflow=0
)
```

### Performance Statistics

```python
stats = monitor.get_stats()

# Query metrics
print(f"Total Queries: {stats.total_queries}")
print(f"Slow Queries: {stats.slow_queries}")
print(f"Failed Queries: {stats.failed_queries}")
print(f"Average Query Time: {stats.avg_query_time:.3f}s")
print(f"Error Rate: {stats.error_rate:.1%}")

# Connection metrics
print(f"Active Connections: {stats.active_connections}")
print(f"Pool Usage: {stats.connection_pool_usage:.1%}")

# Query type breakdown
print(f"SELECT: {stats.select_queries}")
print(f"INSERT: {stats.insert_queries}")
print(f"UPDATE: {stats.update_queries}")
print(f"DELETE: {stats.delete_queries}")
```

### Slow Query Analysis

```python
# Get recent slow queries
slow_queries = monitor.get_slow_queries(limit=10)
for query in slow_queries:
    print(f"Query: {query.query[:100]}")
    print(f"Duration: {query.duration:.2f}s")
    print(f"Type: {query.query_type.value}")
    print(f"Timestamp: {query.timestamp}")

# Get very slow queries
very_slow = monitor.get_very_slow_queries(limit=5)
```

### Query Analysis

```python
# Statistics by query type
stats_by_type = monitor.get_query_stats_by_type()
for query_type, stats in stats_by_type.items():
    print(f"{query_type}:")
    print(f"  Count: {stats['count']}")
    print(f"  Avg Duration: {stats['avg_duration']:.3f}s")
    print(f"  Max Duration: {stats['max_duration']:.3f}s")

# Statistics by table
stats_by_table = monitor.get_query_stats_by_table(limit=10)
for table, count in stats_by_table.items():
    print(f"{table}: {count} queries")
```

### Performance Alerts

```python
# Get all alerts
alerts = monitor.get_alerts(limit=100)

# Filter by severity
warning_alerts = monitor.get_alerts(severity=AlertSeverity.WARNING)
error_alerts = monitor.get_alerts(severity=AlertSeverity.ERROR)

# Process alerts
for alert in alerts:
    print(f"[{alert.severity.value}] {alert.message}")
    print(f"Metric: {alert.metric_name}")
    print(f"Value: {alert.current_value} (threshold: {alert.threshold_value})")
```

### Optimization Recommendations

```python
# Get recommendations
recommendations = monitor.get_recommendations(force_refresh=True)

for rec in recommendations:
    print(f"[{rec.priority.upper()}] {rec.title}")
    print(f"Category: {rec.category}")
    print(f"Description: {rec.description}")
    print(f"Impact: {rec.impact} | Effort: {rec.effort}")
    
    if rec.details:
        print(f"Details: {rec.details}")
```

## Integration with Database Manager

```python
from core.database import DatabaseManager
from core.db_performance_monitor import create_performance_monitor

# Create monitor
monitor = create_performance_monitor()

# Create database manager
db_manager = DatabaseManager()

# Hook into database events
from sqlalchemy import event

@event.listens_for(db_manager.engine, "before_cursor_execute")
def before_query(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()
    context._query_statement = statement

@event.listens_for(db_manager.engine, "after_cursor_execute")
def after_query(conn, cursor, statement, parameters, context, executemany):
    if hasattr(context, '_query_start_time'):
        duration = time.time() - context._query_start_time
        monitor.record_query(
            query=statement,
            duration=duration,
            connection_id=str(id(conn))
        )

@event.listens_for(db_manager.engine, "connect")
def on_connect(dbapi_conn, connection_record):
    monitor.record_connection_event("create", str(id(dbapi_conn)))

@event.listens_for(db_manager.engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    monitor.record_connection_event("checkout", str(id(dbapi_conn)))

@event.listens_for(db_manager.engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    monitor.record_connection_event("checkin", str(id(dbapi_conn)))
```

## Alert Types

### Slow Query Alerts

- **WARNING**: Query exceeds slow_query_threshold
- **ERROR**: Query exceeds very_slow_query_threshold

### Error Rate Alerts

- **ERROR**: Error rate exceeds threshold (default 5%)

### Connection Pool Alerts

- **WARNING**: Pool usage exceeds threshold (default 80%)
- **ERROR**: High connection failure rate

### Performance Degradation Alerts

- **WARNING**: Average query time exceeds threshold

## Optimization Recommendations

The system automatically generates recommendations based on observed patterns:

### Index Recommendations

- Detects slow SELECT queries that may benefit from indexes
- Identifies frequently queried columns without indexes

### Query Optimization

- Identifies inefficient query patterns
- Suggests query rewrites for better performance

### Connection Pool Tuning

- Recommends pool size adjustments based on usage patterns
- Identifies connection leaks and bottlenecks

### Workload Analysis

- Detects write-heavy workloads that may benefit from read replicas
- Identifies hot tables that may need partitioning or caching

## Configuration

### Performance Thresholds

```python
thresholds = PerformanceThresholds(
    slow_query_threshold=1.0,  # Slow query threshold (seconds)
    very_slow_query_threshold=5.0,  # Very slow query threshold
    error_rate_threshold=0.05,  # Maximum acceptable error rate (5%)
    connection_pool_usage_threshold=0.8,  # Pool usage warning (80%)
    avg_query_time_threshold=0.5,  # Average query time warning
    queries_per_second_threshold=100.0,  # QPS warning threshold
    connection_leak_threshold=5,  # Number of leaked connections
    failed_connection_threshold=10  # Failed connection count
)
```

### Monitor Configuration

```python
monitor = DatabasePerformanceMonitor(
    thresholds=thresholds,
    max_slow_queries=100,  # Maximum slow queries to track
    max_alerts=1000,  # Maximum alerts to retain
    enable_recommendations=True  # Enable optimization recommendations
)
```

## Best Practices

### 1. Set Appropriate Thresholds

```python
# Development
thresholds = PerformanceThresholds(slow_query_threshold=2.0)

# Production
thresholds = PerformanceThresholds(slow_query_threshold=0.5)
```

### 2. Monitor Continuously

```python
# Start monitoring at application startup
monitor = create_performance_monitor()

# Register alert handlers
monitor.register_alert_callback(send_to_monitoring_system)

# Periodic health checks
def check_database_health():
    stats = monitor.get_stats()
    if stats.error_rate > 0.05:
        alert_ops_team()
```

### 3. Review Recommendations Regularly

```python
# Daily recommendation review
recommendations = monitor.get_recommendations(force_refresh=True)
for rec in recommendations:
    if rec.priority == "high":
        create_jira_ticket(rec)
```

### 4. Track Trends Over Time

```python
# Export metrics for trending
stats = monitor.get_stats()
metrics_db.store({
    'timestamp': datetime.utcnow(),
    'total_queries': stats.total_queries,
    'avg_query_time': stats.avg_query_time,
    'error_rate': stats.error_rate,
    'pool_usage': stats.connection_pool_usage
})
```

### 5. Reset Stats Periodically

```python
# Reset daily stats
if datetime.utcnow().hour == 0:
    monitor.reset_stats()
```

## Troubleshooting

### High Slow Query Count

1. Review slow queries: `monitor.get_slow_queries()`
2. Check recommendations: `monitor.get_recommendations()`
3. Add indexes on frequently queried columns
4. Optimize query patterns

### High Error Rate

1. Review failed queries in logs
2. Check database connectivity
3. Verify query syntax and permissions
4. Monitor for transient errors

### High Connection Pool Usage

1. Check for connection leaks
2. Increase pool size if needed
3. Review long-running transactions
4. Implement connection timeout

### Performance Degradation

1. Review query statistics by type
2. Identify hot tables
3. Check for missing indexes
4. Consider caching frequently accessed data

## API Reference

### DatabasePerformanceMonitor

- `record_query(query, duration, error, rows_affected, connection_id, user_id)`: Record query execution
- `record_connection_event(event_type, connection_id, error)`: Record connection event
- `update_pool_metrics(pool_size, checked_out, checked_in, overflow)`: Update pool metrics
- `get_stats()`: Get current performance statistics
- `get_slow_queries(limit)`: Get recent slow queries
- `get_very_slow_queries(limit)`: Get very slow queries
- `get_alerts(severity, limit)`: Get performance alerts
- `get_query_stats_by_type()`: Get statistics by query type
- `get_query_stats_by_table(limit)`: Get statistics by table
- `get_recommendations(force_refresh)`: Get optimization recommendations
- `register_alert_callback(callback)`: Register alert callback
- `reset_stats()`: Reset all statistics

### Factory Functions

- `create_performance_monitor(slow_query_threshold, enable_recommendations)`: Create monitor with defaults

## Examples

See `example_db_performance_monitor_usage.py` for comprehensive examples including:

- Basic performance monitoring
- Custom thresholds
- Connection pool monitoring
- Query analysis
- Optimization recommendations
- Real-time monitoring with alerts

## Testing

Run tests with pytest:

```bash
pytest core/test_db_performance_monitor.py -v
```

## License

Part of the Streamlit Robustness Enhancement project.
