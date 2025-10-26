# Structured Logging System

Comprehensive structured logging implementation using `structlog` with correlation IDs, JSON output, and environment-specific configuration.

## Features

- **Structured JSON Logging**: All logs in JSON format for easy aggregation and analysis
- **Correlation IDs**: Automatic correlation ID generation and propagation across requests
- **Environment-Specific Configuration**: Different log levels for dev/staging/prod
- **Runtime Log Level Adjustment**: Change log levels without restarting
- **Sensitive Data Censoring**: Automatic redaction of passwords, API keys, tokens
- **Multiple Output Formats**: JSON for production, human-readable for development
- **Rotating Log Files**: Automatic log rotation with configurable size limits
- **Separate Error Logs**: Dedicated error log files for easier troubleshooting

## Requirements

Implements requirements:
- **7.6**: Structured logging with correlation IDs and trace context
- **9.5**: Log level configuration per environment with runtime adjustment
- **12.5**: Structured logs with Trace-IDs for monitoring and observability

## Quick Start

### Basic Setup

```python
from core.config import load_config
from core.logging_config import init_logging_from_config
from core.logging_system import get_logger

# Load configuration
config = load_config()

# Initialize logging
init_logging_from_config(config)

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("application_started", version=config.app_version)
logger.debug("debug_information", key="value")
logger.warning("warning_message", reason="something")
logger.error("error_occurred", error_type="ValueError")
```

### Using Correlation IDs

```python
from core.logging_system import CorrelationContext, get_logger

logger = get_logger(__name__)

# Automatic correlation ID generation
with CorrelationContext() as correlation_id:
    logger.info("request_started")
    # ... process request ...
    logger.info("request_completed")
    # All logs in this context will have the same correlation_id

# Manual correlation ID
with CorrelationContext("custom-correlation-id"):
    logger.info("processing_with_custom_id")
```

### Adding Context to Logs

```python
from core.logging_system import LogContext, get_logger

logger = get_logger(__name__)

# Add context variables
with LogContext(user_id="user123", request_id="req456"):
    logger.info("user_action", action="login")
    # Logs will include user_id and request_id
```

### Convenience Functions

```python
from core.logging_system import (
    get_logger,
    log_request,
    log_response,
    log_database_query,
    log_cache_operation,
    log_job_event,
    log_error,
    log_security_event,
    log_performance_metric,
)

logger = get_logger(__name__)

# HTTP request/response
log_request(logger, "GET", "/api/users", user_id="user123")
log_response(logger, "GET", "/api/users", 200, 45.5)

# Database operations
log_database_query(logger, "SELECT", "users", 12.3, rows_affected=5)

# Cache operations
log_cache_operation(logger, "get", "user:123", hit=True)

# Job events
log_job_event(logger, "started", "job-123", "calculation")

# Errors with context
try:
    raise ValueError("Something went wrong")
except ValueError as e:
    log_error(logger, e, context={"operation": "data_processing"})

# Security events
log_security_event(
    logger,
    "login_attempt",
    user_id="user123",
    ip_address="192.168.1.1",
    success=True,
)

# Performance metrics
log_performance_metric(logger, "response_time", 45.5, unit="ms")
```

## Configuration

### Environment-Specific Log Levels

Default log levels by environment:
- **dev**: DEBUG
- **staging**: INFO
- **prod**: WARNING

Override with environment variable:
```bash
export LOG_LEVEL=DEBUG
```

### JSON Format Configuration

JSON format is automatically enabled for production and staging environments.

Override with environment variable:
```bash
export LOG_JSON=true   # Force JSON format
export LOG_JSON=false  # Force human-readable format
```

### Runtime Log Level Adjustment

```python
from core.logging_config import adjust_log_level_runtime, get_current_log_level

# Get current level
current = get_current_log_level()
print(f"Current log level: {current}")

# Change level at runtime
adjust_log_level_runtime("DEBUG")
adjust_log_level_runtime("INFO")
adjust_log_level_runtime("WARNING")
```

### Using LoggingConfigManager

```python
from core.config import load_config
from core.logging_config import LoggingConfigManager

config = load_config()
manager = LoggingConfigManager(config)
manager.initialize()

# Set log level
manager.set_level("DEBUG")

# Get current level
level = manager.get_level()

# Reload configuration
manager.reload_from_config()
```

## Log Output Format

### JSON Format (Production)

```json
{
  "timestamp": "2025-01-19T10:30:45.123456Z",
  "level": "info",
  "event": "user_action",
  "logger": "app.users",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "environment": "prod",
  "app": "streamlit-robust",
  "version": "1.0.0",
  "user_id": "user123",
  "action": "login",
  "ip_address": "192.168.1.1"
}
```

### Human-Readable Format (Development)

```
10:30:45 - app.users - INFO - user_action user_id=user123 action=login
```

## Sensitive Data Protection

The logging system automatically censors sensitive data:

```python
logger.info(
    "api_call",
    api_key="sk-1234567890",  # Will be [REDACTED]
    password="secret123",      # Will be [REDACTED]
    token="bearer xyz",        # Will be [REDACTED]
    username="john",           # Will be visible
)
```

Censored fields:
- `password`, `pwd`
- `secret`
- `token`, `auth`, `authorization`
- `api_key`, `apikey`
- `credential`

## Log Files

### File Structure

```
logs/
├── app_20250119.log          # Main application log
├── app_20250119.log.1        # Rotated log (older)
├── app_20250119.log.2        # Rotated log (oldest)
├── errors_20250119.log       # Error-only log
└── errors_20250119.log.1     # Rotated error log
```

### Rotation Policy

- **Max file size**: 50MB
- **Backup count**: 10 files
- **Encoding**: UTF-8

## Integration with AppConfig

The logging system integrates seamlessly with `AppConfig`:

```python
from core.config import load_config
from core.logging_config import get_logging_manager

# Load configuration
config = load_config()

# Get logging manager (singleton)
manager = get_logging_manager(config)

# Logging is now configured based on AppConfig
# - Log level from environment
# - Log directory from config.log_dir
# - JSON format based on environment
```

## Best Practices

### 1. Use Structured Fields

```python
# Good: Structured fields
logger.info("user_login", user_id="user123", ip="192.168.1.1", success=True)

# Avoid: String interpolation
logger.info(f"User user123 logged in from 192.168.1.1")
```

### 2. Use Correlation IDs for Request Tracking

```python
with CorrelationContext() as correlation_id:
    logger.info("request_started")
    process_request()
    logger.info("request_completed")
```

### 3. Add Context for Related Operations

```python
with LogContext(user_id=user.id, session_id=session.id):
    logger.info("operation_started")
    perform_operation()
    logger.info("operation_completed")
```

### 4. Use Convenience Functions

```python
# Instead of manual logging
logger.info("database_query", type="SELECT", table="users", duration=12.3)

# Use convenience function
log_database_query(logger, "SELECT", "users", 12.3)
```

### 5. Log Errors with Context

```python
try:
    risky_operation()
except Exception as e:
    log_error(logger, e, context={
        "operation": "risky_operation",
        "user_id": user_id,
        "input_data": input_summary,
    })
    raise
```

## Testing

Run tests:

```bash
# Test structured logging
pytest core/test_logging_system.py -v

# Test configuration integration
pytest core/test_logging_config.py -v

# Run all logging tests
pytest core/test_logging*.py -v
```

## Log Aggregation

The JSON format is designed for easy integration with log aggregation systems:

### Elasticsearch/Kibana

```json
{
  "timestamp": "2025-01-19T10:30:45.123456Z",
  "level": "info",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "environment": "prod",
  "app": "streamlit-robust"
}
```

### Splunk

```json
{
  "time": "2025-01-19T10:30:45.123456Z",
  "severity": "INFO",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### CloudWatch Logs

```json
{
  "@timestamp": "2025-01-19T10:30:45.123456Z",
  "level": "INFO",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Troubleshooting

### Logs Not Appearing

1. Check log level: `get_current_log_level()`
2. Verify log directory exists and is writable
3. Check file permissions

### Correlation IDs Not Appearing

1. Ensure you're using `CorrelationContext`
2. Verify correlation ID is set: `get_correlation_id()`

### Sensitive Data Not Censored

1. Check field names match censored patterns
2. Add custom censoring if needed

## Migration from Standard Logging

### Before (Standard Logging)

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"User {user_id} performed action")
```

### After (Structured Logging)

```python
from core.logging_system import get_logger

logger = get_logger(__name__)
logger.info("user_action", user_id=user_id, action="performed")
```

## Performance Considerations

- **Minimal overhead**: structlog is designed for performance
- **Lazy evaluation**: Log messages only formatted if level is enabled
- **Efficient JSON serialization**: Uses optimized JSON renderer
- **Rotating files**: Prevents disk space issues

## Related Documentation

- [Configuration System](CONFIG_README.md)
- [Application Architecture](../docs/ARCHITECTURE.md)
- [Monitoring and Observability](../docs/MONITORING.md)
