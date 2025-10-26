# Database Connection Manager - Quick Reference Card

## Quick Start

```python
from core.connection_manager import create_connection_manager

# Basic usage
manager = create_connection_manager(
    database_url="postgresql://user:pass@localhost/db"
)

# Get session
with manager.session_scope() as session:
    result = session.execute("SELECT * FROM users")
```

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_FAILOVER_URLS=postgresql://backup1/db,postgresql://backup2/db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### Programmatic
```python
manager = create_connection_manager(
    database_url="postgresql://...",
    pool_size=10,              # Base pool size
    max_overflow=20,           # Additional connections
    leak_detection=True,       # Enable leak detection
    health_monitoring=True,    # Enable health monitoring
    failover_urls=[...]        # Failover databases
)
```

## Common Operations

### Get Session
```python
# Method 1: Context manager (recommended)
with manager.session_scope() as session:
    result = session.execute("SELECT * FROM users")
    # Auto-commit on success, rollback on error

# Method 2: Manual
session = manager.get_session()
try:
    result = session.execute("SELECT * FROM users")
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()
```

### Check Health
```python
status = manager.get_health_status()
print(f"Healthy: {status['healthy']}")
print(f"Response time: {status['health_check']['response_time']:.3f}s")
```

### Get Metrics
```python
metrics = manager.get_pool_metrics()
print(f"Pool size: {metrics.size}")
print(f"Checked out: {metrics.checked_out}")
print(f"Utilization: {metrics.to_dict()['utilization']}")
```

### Check for Leaks
```python
status = manager.get_health_status()
leak_info = status['leak_detection']
print(f"Active: {leak_info['active_connections']}")
print(f"Leaked: {leak_info['total_leaked']}")
```

### Check Failover Status
```python
status = manager.get_health_status()
failover = status['failover_stats']
print(f"Current: {failover['current_url']}")
print(f"Is Primary: {failover['is_primary']}")
print(f"Failover count: {failover['failover_count']}")
```

## Integration with DatabaseManager

```python
from core.database import DatabaseManager

# Create with enhanced connection manager
db = DatabaseManager(use_enhanced_connection_manager=True)

# Use all features
session = db.get_session()
health = db.health_check()
metrics = db.get_connection_pool_metrics()
leaks = db.detect_connection_leaks()
```

## Monitoring

### Pool Metrics
```python
metrics = manager.get_pool_metrics()
# Returns: size, checked_in, checked_out, overflow,
#          total_checkouts, leaked_connections, etc.
```

### Health Statistics
```python
status = manager.get_health_status()
stats = status['health_stats']
# Returns: total_checks, healthy_checks, failed_checks,
#          success_rate, avg_response_time
```

### Comprehensive Status
```python
status = manager.get_health_status()
# Returns: healthy, pool_metrics, health_check,
#          health_stats, failover_stats, leak_detection
```

## Configuration Options

### ConnectionPoolConfig
```python
from core.connection_manager import ConnectionPoolConfig

config = ConnectionPoolConfig(
    pool_size=10,                      # Base pool size
    max_overflow=20,                   # Additional connections
    pool_timeout=30,                   # Timeout in seconds
    pool_recycle=3600,                 # Recycle after 1 hour
    pool_pre_ping=True,                # Test before use
    leak_detection_enabled=True,       # Enable leak detection
    leak_threshold_seconds=300.0,      # 5 minutes
    health_check_enabled=True,         # Enable monitoring
    health_check_interval=60,          # Check every 60s
    failover_enabled=True,             # Enable failover
    failover_urls=[...],               # Backup databases
    failover_retry_attempts=3,         # Retry attempts
    failover_retry_delay=1.0           # Delay between retries
)
```

## Best Practices

1. **Always close sessions**: Use context managers
2. **Monitor pool utilization**: Keep below 80%
3. **Set appropriate timeouts**: Match your needs
4. **Enable health monitoring**: Catch issues early
5. **Configure failover**: For production HA
6. **Review leak warnings**: Fix connection leaks
7. **Monitor metrics**: Track performance

## Troubleshooting

### High Pool Utilization
```python
metrics = manager.get_pool_metrics()
utilization = metrics.checked_out / metrics.size
if utilization > 0.8:
    # Increase pool_size or max_overflow
```

### Connection Leaks
```python
status = manager.get_health_status()
if status['leak_detection']['total_leaked'] > 0:
    # Review code for unclosed sessions
```

### Health Check Failures
```python
status = manager.get_health_status()
if not status['healthy']:
    error = status['health_check']['error']
    # Check database connectivity
```

## Performance Tips

- Use connection pooling (enabled by default)
- Enable pre-ping for stale detection
- Set appropriate pool_recycle time
- Monitor and tune pool_size
- Use session_scope() for cleanup
- Enable health monitoring

## Key Classes

- `ConnectionPoolConfig` - Pool configuration
- `EnhancedConnectionManager` - Main manager
- `ConnectionHealthMonitor` - Health monitoring
- `ConnectionLeakDetector` - Leak detection
- `DatabaseFailoverManager` - Failover management
- `PoolMetrics` - Pool metrics
- `HealthCheckResult` - Health check results
- `ConnectionInfo` - Connection tracking

## Event Listeners

- `on_connect` - New connection created
- `on_checkout` - Connection checked out
- `on_checkin` - Connection returned
- `on_pool_connect` - Pool-level events

## Thread Safety

All components are thread-safe:
- Uses `threading.Lock()` for synchronization
- Safe for concurrent access
- Background monitoring thread
- Lock contention <0.1ms

## Documentation

- `CONNECTION_MANAGER_README.md` - Full documentation
- `CONNECTION_MANAGER_QUICK_START.md` - Quick start
- `example_connection_manager_usage.py` - Examples
- `TASK_8_3_COMPLETE.md` - Implementation details

## Testing

```bash
# Run tests
pytest core/test_connection_manager.py -v

# Run verification
python core/verify_connection_manager.py
python core/verify_task_8_3.py
```

## Support

For issues:
1. Check logs for errors
2. Review health status
3. Verify database connectivity
4. Check pool configuration
5. Review documentation
