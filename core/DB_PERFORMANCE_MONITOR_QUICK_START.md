# Database Performance Monitoring - Quick Start Guide

Get started with database performance monitoring in 5 minutes.

## Installation

The database performance monitoring system is part of the core module. No additional installation required.

## Basic Setup

### 1. Create a Monitor

```python
from core.db_performance_monitor import create_performance_monitor

# Create with default settings
monitor = create_performance_monitor(
    slow_query_threshold=1.0,  # Queries slower than 1s are "slow"
    enable_recommendations=True
)
```

### 2. Record Query Execution

```python
import time

# Time your query
start = time.time()
# ... execute your query ...
duration = time.time() - start

# Record it
monitor.record_query(
    query="SELECT * FROM users WHERE id = 1",
    duration=duration,
    rows_affected=1
)
```

### 3. Get Statistics

```python
stats = monitor.get_stats()

print(f"Total Queries: {stats.total_queries}")
print(f"Slow Queries: {stats.slow_queries}")
print(f"Average Time: {stats.avg_query_time:.3f}s")
print(f"Error Rate: {stats.error_rate:.1%}")
```

## Common Use Cases

### Monitor Slow Queries

```python
# Get recent slow queries
slow_queries = monitor.get_slow_queries(limit=10)

for query in slow_queries:
    print(f"Duration: {query.duration:.2f}s")
    print(f"Query: {query.query[:100]}")
    print(f"Type: {query.query_type.value}")
    print()
```

### Track Errors

```python
# Record failed query
try:
    # ... execute query ...
    pass
except Exception as e:
    monitor.record_query(
        query="SELECT * FROM invalid_table",
        duration=0.1,
        error=e
    )

# Check error rate
stats = monitor.get_stats()
if stats.error_rate > 0.05:  # More than 5% errors
    print("⚠️  High error rate detected!")
```

### Monitor Connection Pool

```python
# Update pool metrics (typically from SQLAlchemy events)
monitor.update_pool_metrics(
    pool_size=10,
    checked_out=7,
    checked_in=3,
    overflow=0
)

# Check pool usage
stats = monitor.get_stats()
if stats.connection_pool_usage > 0.8:
    print("⚠️  Connection pool usage high!")
```

### Get Optimization Recommendations

```python
# Get recommendations
recommendations = monitor.get_recommendations()

for rec in recommendations:
    if rec.priority == "high":
        print(f"🔴 {rec.title}")
        print(f"   {rec.description}")
        print(f"   Impact: {rec.impact} | Effort: {rec.effort}")
```

### Set Up Alerts

```python
def alert_handler(alert):
    """Handle performance alerts"""
    if alert.severity.value == "error":
        print(f"🚨 CRITICAL: {alert.message}")
        # Send to monitoring system
    elif alert.severity.value == "warning":
        print(f"⚠️  WARNING: {alert.message}")

monitor.register_alert_callback(alert_handler)

# Alerts will be triggered automatically when thresholds are exceeded
```

## Integration with SQLAlchemy

```python
from sqlalchemy import event, create_engine
from core.db_performance_monitor import create_performance_monitor
import time

# Create monitor
monitor = create_performance_monitor()

# Create engine
engine = create_engine("postgresql://user:pass@localhost/db")

# Hook into query events
@event.listens_for(engine, "before_cursor_execute")
def before_query(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_query(conn, cursor, statement, parameters, context, executemany):
    if hasattr(context, '_query_start_time'):
        duration = time.time() - context._query_start_time
        monitor.record_query(
            query=statement,
            duration=duration,
            connection_id=str(id(conn))
        )

# Hook into connection events
@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, connection_record):
    monitor.record_connection_event("create", str(id(dbapi_conn)))

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    monitor.record_connection_event("checkout", str(id(dbapi_conn)))

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    monitor.record_connection_event("checkin", str(id(dbapi_conn)))
```

## Dashboard Example

```python
def print_dashboard():
    """Print performance dashboard"""
    stats = monitor.get_stats()
    
    print("\n" + "=" * 60)
    print("DATABASE PERFORMANCE DASHBOARD")
    print("=" * 60)
    
    # Query metrics
    print("\n📊 Query Metrics:")
    print(f"   Total Queries: {stats.total_queries}")
    print(f"   Slow Queries: {stats.slow_queries} ({stats.slow_queries/max(stats.total_queries,1):.1%})")
    print(f"   Failed Queries: {stats.failed_queries}")
    print(f"   Average Time: {stats.avg_query_time:.3f}s")
    print(f"   Error Rate: {stats.error_rate:.1%}")
    
    # Connection metrics
    print("\n🔌 Connection Pool:")
    print(f"   Active: {stats.active_connections}")
    print(f"   Idle: {stats.idle_connections}")
    print(f"   Usage: {stats.connection_pool_usage:.1%}")
    
    # Query breakdown
    print("\n📈 Query Types:")
    print(f"   SELECT: {stats.select_queries}")
    print(f"   INSERT: {stats.insert_queries}")
    print(f"   UPDATE: {stats.update_queries}")
    print(f"   DELETE: {stats.delete_queries}")
    
    # Recent alerts
    alerts = monitor.get_alerts(limit=5)
    if alerts:
        print("\n🚨 Recent Alerts:")
        for alert in alerts[-5:]:
            print(f"   [{alert.severity.value}] {alert.message}")
    
    # Top recommendations
    recommendations = monitor.get_recommendations()
    if recommendations:
        print("\n💡 Top Recommendations:")
        for rec in recommendations[:3]:
            print(f"   [{rec.priority}] {rec.title}")
    
    print("=" * 60)

# Call periodically
import threading

def dashboard_loop():
    while True:
        print_dashboard()
        time.sleep(60)  # Update every minute

dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
dashboard_thread.start()
```

## Custom Thresholds

```python
from core.db_performance_monitor import (
    DatabasePerformanceMonitor,
    PerformanceThresholds
)

# Define custom thresholds for production
thresholds = PerformanceThresholds(
    slow_query_threshold=0.5,  # 500ms
    very_slow_query_threshold=2.0,  # 2 seconds
    error_rate_threshold=0.02,  # 2%
    connection_pool_usage_threshold=0.7,  # 70%
    avg_query_time_threshold=0.2  # 200ms
)

monitor = DatabasePerformanceMonitor(
    thresholds=thresholds,
    max_slow_queries=200,
    enable_recommendations=True
)
```

## Export Metrics

```python
def export_metrics():
    """Export metrics to monitoring system"""
    stats = monitor.get_stats()
    
    # Export to Prometheus
    metrics = {
        'db_queries_total': stats.total_queries,
        'db_queries_slow': stats.slow_queries,
        'db_queries_failed': stats.failed_queries,
        'db_query_duration_avg': stats.avg_query_time,
        'db_error_rate': stats.error_rate,
        'db_connections_active': stats.active_connections,
        'db_pool_usage': stats.connection_pool_usage,
    }
    
    return metrics

# Export periodically
def export_loop():
    while True:
        metrics = export_metrics()
        send_to_prometheus(metrics)
        time.sleep(15)  # Every 15 seconds
```

## Testing

```python
# Run verification
from core.verify_db_performance_monitor import run_all_verifications

if run_all_verifications():
    print("✅ All checks passed!")
else:
    print("❌ Some checks failed")

# Run examples
from core.example_db_performance_monitor_usage import main
main()
```

## Next Steps

1. **Read the full documentation**: `DB_PERFORMANCE_MONITOR_README.md`
2. **Run the examples**: `python core/example_db_performance_monitor_usage.py`
3. **Run the tests**: `pytest core/test_db_performance_monitor.py -v`
4. **Integrate with your database**: Add event listeners to your SQLAlchemy engine
5. **Set up alerts**: Configure alert callbacks for your monitoring system
6. **Review recommendations**: Check optimization recommendations regularly

## Troubleshooting

### No queries being recorded

- Verify monitor is created before queries execute
- Check that `record_query()` is being called
- Ensure SQLAlchemy event listeners are registered

### Alerts not firing

- Check threshold values are appropriate
- Verify alert callbacks are registered
- Ensure queries are actually slow/failing

### High memory usage

- Reduce `max_slow_queries` and `max_alerts` limits
- Call `reset_stats()` periodically
- Limit query history retention

## Support

For issues or questions:
- Check the full README: `DB_PERFORMANCE_MONITOR_README.md`
- Run verification: `python core/verify_db_performance_monitor.py`
- Review examples: `core/example_db_performance_monitor_usage.py`
