# Database Connection Manager - Quick Start Guide

## Overview

The Enhanced Connection Manager provides production-ready database connection management with:
- ✅ Connection pooling with configurable sizes
- ✅ Automatic health monitoring and recovery
- ✅ Connection leak detection and prevention
- ✅ Database failover for high availability

## Quick Start

### Basic Usage

```python
from core.connection_manager import create_connection_manager

# Create connection manager
manager = create_connection_manager(
    database_url="postgresql://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20
)

# Get a session
session = manager.get_session()
try:
    # Use session
    result = session.execute("SELECT * FROM users")
finally:
    session.close()

# Or use context manager
with manager.session_scope() as session:
    result = session.execute("SELECT * FROM users")
    # Automatically commits on success, rolls back on error
```

### With Health Monitoring

```python
# Health monitoring is enabled by default
manager = create_connection_manager(
    database_url="postgresql://...",
    health_monitoring=True  # Default
)

# Check health status
status = manager.get_health_status()
print(f"Database healthy: {status['healthy']}")
print(f"Response time: {status['health_check']['response_time']:.3f}s")
```

### With Leak Detection

```python
# Leak detection is enabled by default
manager = create_connection_manager(
    database_url="postgresql://...",
    leak_detection=True  # Default
)

# Check for leaks
status = manager.get_health_status()
leak_info = status['leak_detection']
print(f"Active connections: {leak_info['active_connections']}")
print(f"Total leaked: {leak_info['total_leaked']}")
```

### With Failover Support

```python
# Configure failover URLs
manager = create_connection_manager(
    database_url="postgresql://primary/db",
    failover_urls=[
        "postgresql://backup1/db",
        "postgresql://backup2/db"
    ]
)

# Failover happens automatically on connection failure
session = manager.get_session()  # Will use backup if primary fails

# Check failover status
status = manager.get_health_status()
print(f"Current URL: {status['failover_stats']['current_url']}")
print(f"Is Primary: {status['failover_stats']['is_primary']}")
```

## Integration with DatabaseManager

```python
from core.database import DatabaseManager

# DatabaseManager uses enhanced connection manager by default
db_manager = DatabaseManager(use_enhanced_connection_manager=True)

# All features available through DatabaseManager
session = db_manager.get_session()
health = db_manager.health_check()
metrics = db_manager.get_connection_pool_metrics()
leaks = db_manager.detect_connection_leaks()
```

## Environment Configuration

```bash
# Database URL
DATABASE_URL=postgresql://user:pass@localhost/db

# Failover URLs (comma-separated)
DATABASE_FAILOVER_URLS=postgresql://backup1/db,postgresql://backup2/db

# Pool configuration
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Leak detection threshold (seconds)
CONNECTION_LEAK_THRESHOLD=300

# Health check interval (seconds)
CONNECTION_HEALTH_CHECK_INTERVAL=60
```

## Monitoring

### Get Pool Metrics

```python
metrics = manager.get_pool_metrics()
print(f"Pool size: {metrics.size}")
print(f"Checked out: {metrics.checked_out}")
print(f"Utilization: {metrics.to_dict()['utilization']}")
print(f"Average checkout time: {metrics.avg_checkout_time:.3f}s")
```

### Get Health Statistics

```python
status = manager.get_health_status()

# Pool metrics
print(status['pool_metrics'])

# Health check results
print(status['health_check'])

# Health statistics
print(status['health_stats'])

# Failover status
print(status['failover_stats'])

# Leak detection
print(status['leak_detection'])
```

## Advanced Configuration

```python
from core.connection_manager import ConnectionPoolConfig, EnhancedConnectionManager

config = ConnectionPoolConfig(
    # Pool settings
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    
    # Leak detection
    leak_detection_enabled=True,
    leak_threshold_seconds=300.0,
    
    # Health monitoring
    health_check_enabled=True,
    health_check_interval=60,
    
    # Failover
    failover_enabled=True,
    failover_urls=["postgresql://backup/db"],
    failover_retry_attempts=3,
    failover_retry_delay=1.0
)

manager = EnhancedConnectionManager(config, "postgresql://primary/db")
```

## Best Practices

1. **Always close sessions**: Use context managers or explicit close()
2. **Monitor pool utilization**: Keep below 80% for optimal performance
3. **Set appropriate timeouts**: Match your application's needs
4. **Enable health monitoring**: Catch issues before they impact users
5. **Configure failover**: For production high availability
6. **Review leak warnings**: Investigate and fix connection leaks
7. **Monitor metrics**: Track performance over time

## Troubleshooting

### High Pool Utilization

```python
metrics = manager.get_pool_metrics()
if metrics.checked_out / metrics.size > 0.8:
    print("Warning: High pool utilization!")
    # Consider increasing pool_size or max_overflow
```

### Connection Leaks

```python
status = manager.get_health_status()
if status['leak_detection']['total_leaked'] > 0:
    print("Warning: Connection leaks detected!")
    # Review code for unclosed sessions
```

### Health Check Failures

```python
status = manager.get_health_status()
if not status['healthy']:
    print(f"Database unhealthy: {status['health_check']['error']}")
    # Check database connectivity and logs
```

## Performance Tips

- Use connection pooling (enabled by default)
- Enable pre-ping for stale connection detection
- Set appropriate pool_recycle time
- Monitor and tune pool_size based on load
- Use session_scope() for automatic cleanup
- Enable health monitoring for proactive detection

## Next Steps

- Review `CONNECTION_MANAGER_README.md` for detailed documentation
- Check `example_connection_manager_usage.py` for more examples
- Run `verify_connection_manager.py` to test your setup
- See `test_connection_manager.py` for comprehensive tests

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review health status and metrics
3. Verify database connectivity
4. Check pool configuration
5. Review the comprehensive documentation
