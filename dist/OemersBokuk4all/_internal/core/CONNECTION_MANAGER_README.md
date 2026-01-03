# Enhanced Connection Manager

Comprehensive database connection management with pooling, health monitoring, leak detection, and failover support.

## Overview

The Enhanced Connection Manager provides production-ready database connection management with:

- **Connection Pooling**: Configurable pool sizes with overflow support
- **Health Monitoring**: Automatic health checks with recovery
- **Leak Detection**: Identifies and reports connection leaks
- **Failover Support**: Automatic failover to backup databases
- **Performance Metrics**: Detailed connection pool metrics
- **Thread Safety**: Safe for concurrent access

## Quick Start

### Basic Usage

```python
from core.connection_manager import create_connection_manager

# Create connection manager
manager = create_connection_manager(
    database_url="postgresql://user:pass@localhost/db",
    pool_size=5,
    max_overflow=10
)

# Use session scope for operations
with manager.session_scope() as session:
    result = session.execute("SELECT * FROM users")
    users = result.fetchall()

# Clean up
manager.dispose()
```

### Integration with DatabaseManager

```python
from core.database import get_db_manager

# Get database manager (uses enhanced connection manager by default)
db_manager = get_db_manager()

# Use database manager methods
with db_manager.session_scope() as session:
    # Your database operations
    pass

# Get connection pool metrics
metrics = db_manager.get_connection_pool_metrics()
print(f"Pool utilization: {metrics['utilization']}")

# Check for connection leaks
leaks = db_manager.detect_connection_leaks()
if leaks:
    print(f"Warning: {len(leaks)} connection leaks detected")
```

## Features

### 1. Connection Pooling

Efficient connection pooling with configurable sizes:

```python
from core.connection_manager import ConnectionPoolConfig, EnhancedConnectionManager

config = ConnectionPoolConfig(
    pool_size=10,              # Base pool size
    max_overflow=20,           # Additional connections allowed
    pool_timeout=30,           # Timeout for getting connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True         # Test connections before use
)

manager = EnhancedConnectionManager(config, database_url)
```

**Benefits:**
- Reuses connections for better performance
- Limits concurrent connections to database
- Automatically recycles stale connections
- Pre-ping ensures connection validity

### 2. Health Monitoring

Automatic health checks with recovery:

```python
manager = create_connection_manager(
    database_url="postgresql://localhost/db",
    health_monitoring=True
)

# Get health status
status = manager.get_health_status()
print(f"Database healthy: {status['healthy']}")
print(f"Response time: {status['health_check']['response_time']}s")

# Get health statistics
if manager.health_monitor:
    stats = manager.health_monitor.get_health_stats()
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Total checks: {stats['total_checks']}")
```

**Features:**
- Background health monitoring
- Automatic recovery on failure
- Health check history
- Performance statistics

### 3. Connection Leak Detection

Identifies connections that aren't properly closed:

```python
config = ConnectionPoolConfig(
    leak_detection_enabled=True,
    leak_threshold_seconds=300.0  # 5 minutes
)

manager = EnhancedConnectionManager(config, database_url)

# Check for leaks
metrics = manager.get_pool_metrics()
if metrics.leaked_connections > 0:
    print(f"Warning: {metrics.leaked_connections} leaks detected")
    
    # Get leak details
    if manager.leak_detector:
        leaked = manager.leak_detector.detect_leaks()
        for leak in leaked:
            print(f"Connection {leak.connection_id}")
            print(f"  Duration: {leak.duration}s")
            print(f"  Thread: {leak.checked_out_by}")
```

**Benefits:**
- Prevents connection pool exhaustion
- Identifies problematic code paths
- Provides detailed leak information
- Configurable leak threshold

### 4. Database Failover

Automatic failover to backup databases:

```python
manager = create_connection_manager(
    database_url="postgresql://primary:5432/db",
    failover_urls=[
        "postgresql://backup1:5432/db",
        "postgresql://backup2:5432/db"
    ]
)

# Get failover status
if manager.failover_manager:
    stats = manager.failover_manager.get_failover_stats()
    print(f"Current database: {stats['current_url']}")
    print(f"Is primary: {stats['is_primary']}")
    print(f"Failover count: {stats['failover_count']}")
```

**Features:**
- Automatic failover on connection failure
- Multiple backup databases
- Automatic primary restoration
- Failover statistics

### 5. Performance Metrics

Detailed connection pool metrics:

```python
metrics = manager.get_pool_metrics()

print(f"Pool size: {metrics.size}")
print(f"Checked out: {metrics.checked_out}")
print(f"Checked in: {metrics.checked_in}")
print(f"Overflow: {metrics.overflow}")
print(f"Total checkouts: {metrics.total_checkouts}")
print(f"Total connections created: {metrics.total_connections_created}")
print(f"Failed checkouts: {metrics.failed_checkouts}")
print(f"Average checkout time: {metrics.avg_checkout_time}s")
print(f"Utilization: {metrics.to_dict()['utilization']}")
```

## Configuration

### ConnectionPoolConfig

Complete configuration options:

```python
config = ConnectionPoolConfig(
    # Pool settings
    pool_size=5,                    # Base pool size
    max_overflow=10,                # Max overflow connections
    pool_timeout=30,                # Timeout for getting connection (seconds)
    pool_recycle=3600,              # Recycle connections after (seconds)
    pool_pre_ping=True,             # Test connections before use
    echo_pool=False,                # Log pool events
    
    # Leak detection
    leak_detection_enabled=True,    # Enable leak detection
    leak_threshold_seconds=300.0,   # Leak threshold (seconds)
    
    # Health monitoring
    health_check_enabled=True,      # Enable health monitoring
    health_check_interval=60,       # Health check interval (seconds)
    
    # Failover
    failover_enabled=False,         # Enable failover
    failover_urls=[],               # List of failover URLs
    failover_retry_attempts=3,      # Retry attempts per failover
    failover_retry_delay=1.0        # Delay between retries (seconds)
)
```

### Environment Variables

Configure via environment variables:

```bash
# Database URLs
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_FAILOVER_URLS=postgresql://backup1/db,postgresql://backup2/db

# Pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

## API Reference

### EnhancedConnectionManager

Main connection manager class.

#### Methods

**`__init__(config: ConnectionPoolConfig, database_url: str)`**
- Initialize connection manager with configuration

**`get_session() -> Session`**
- Get database session with automatic failover
- Returns: SQLAlchemy Session

**`session_scope()`**
- Context manager for transactional scope
- Automatically commits on success, rolls back on error

**`get_pool_metrics() -> PoolMetrics`**
- Get current connection pool metrics
- Returns: PoolMetrics object

**`get_health_status() -> Dict[str, Any]`**
- Get comprehensive health status
- Returns: Dictionary with health information

**`dispose()`**
- Dispose of all connections in pool
- Stops health monitoring

**`reset_metrics()`**
- Reset all metrics to zero

### DatabaseManager Integration

Enhanced DatabaseManager methods:

**`get_connection_pool_metrics() -> Dict[str, Any]`**
- Get connection pool metrics
- Returns: Dictionary with pool metrics

**`detect_connection_leaks() -> List[Dict[str, Any]]`**
- Detect potential connection leaks
- Returns: List of leak information

**`get_health_monitor_stats() -> Dict[str, Any]`**
- Get health monitoring statistics
- Returns: Dictionary with health stats

**`get_failover_status() -> Dict[str, Any]`**
- Get failover status
- Returns: Dictionary with failover information

**`dispose_connections()`**
- Dispose of all connections in pool

## Best Practices

### 1. Always Use Session Scope

```python
# Good: Automatic cleanup
with manager.session_scope() as session:
    result = session.query(User).all()

# Bad: Manual cleanup required
session = manager.get_session()
result = session.query(User).all()
session.close()  # Easy to forget!
```

### 2. Configure Appropriate Pool Sizes

```python
# Development: Small pool
config = ConnectionPoolConfig(pool_size=2, max_overflow=3)

# Production: Larger pool
config = ConnectionPoolConfig(pool_size=10, max_overflow=20)
```

### 3. Enable Health Monitoring in Production

```python
manager = create_connection_manager(
    database_url=prod_url,
    health_monitoring=True  # Always enable in production
)
```

### 4. Monitor for Connection Leaks

```python
# Regularly check for leaks
metrics = manager.get_pool_metrics()
if metrics.leaked_connections > 0:
    logger.warning(f"Connection leaks detected: {metrics.leaked_connections}")
    # Investigate and fix leaking code
```

### 5. Use Failover for High Availability

```python
manager = create_connection_manager(
    database_url=primary_url,
    failover_urls=[backup1_url, backup2_url]
)
```

### 6. Set Appropriate Leak Thresholds

```python
# Short-lived operations: Lower threshold
config = ConnectionPoolConfig(leak_threshold_seconds=60.0)

# Long-running operations: Higher threshold
config = ConnectionPoolConfig(leak_threshold_seconds=600.0)
```

## Troubleshooting

### Connection Pool Exhausted

**Symptom:** Timeout errors when getting connections

**Solutions:**
1. Increase pool size: `pool_size=20`
2. Increase max overflow: `max_overflow=30`
3. Check for connection leaks
4. Reduce connection hold time

### Connection Leaks Detected

**Symptom:** Leaked connections in metrics

**Solutions:**
1. Always use `session_scope()` context manager
2. Ensure sessions are closed in finally blocks
3. Review code for unclosed sessions
4. Check leak details for problematic code paths

### Health Checks Failing

**Symptom:** Health status shows unhealthy

**Solutions:**
1. Check database connectivity
2. Verify database credentials
3. Check network connectivity
4. Review database logs
5. Consider failover if available

### Slow Connection Checkout

**Symptom:** High average checkout time

**Solutions:**
1. Enable `pool_pre_ping` to detect stale connections
2. Reduce `pool_recycle` time
3. Check database performance
4. Review slow queries

## Performance Considerations

### Pool Sizing

- **Too small:** Connection contention, timeouts
- **Too large:** Resource waste, database overload
- **Rule of thumb:** `pool_size = (core_count * 2) + effective_spindle_count`

### Connection Recycling

- Recycle connections periodically to prevent stale connections
- Default: 3600 seconds (1 hour)
- Adjust based on database timeout settings

### Pre-ping

- Enables connection health checks before use
- Small overhead but prevents stale connection errors
- Recommended for production

### Leak Detection

- Minimal overhead when enabled
- Runs during connection checkout/checkin
- Threshold should match typical operation duration

## Examples

See `example_connection_manager_usage.py` for complete examples:

- Basic usage
- Health monitoring
- Connection pool metrics
- Leak detection
- Database failover
- Integration with DatabaseManager
- Advanced configuration
- Concurrent access

## Testing

Run tests:

```bash
pytest core/test_connection_manager.py -v
```

Test coverage:
- Connection pooling
- Health monitoring
- Leak detection
- Failover management
- Concurrent access
- Error recovery

## Requirements

- SQLAlchemy >= 1.4
- structlog (optional, for structured logging)
- Python >= 3.8

## Related Documentation

- [Database README](DATABASE_README.md) - Main database documentation
- [Migration README](MIGRATION_README.md) - Database migrations
- [Session README](SESSION_README.md) - Session management

## Support

For issues or questions:
1. Check troubleshooting section
2. Review example usage
3. Check test cases for patterns
4. Review source code documentation
