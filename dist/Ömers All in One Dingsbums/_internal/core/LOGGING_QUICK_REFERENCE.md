# Structured Logging Quick Reference

## Overview

The application uses **structlog** for structured logging with:
- ✅ Consistent JSON output for production
- ✅ Human-readable console output for development
- ✅ Automatic correlation ID generation and propagation
- ✅ Environment-specific log levels
- ✅ PII masking for security
- ✅ Runtime log level adjustment

## Quick Start

### Basic Setup

```python
from core.config import load_config
from core.logging_config import setup_logging, get_logger

# Initialize logging
config = load_config()
setup_logging(config)

# Get a logger
logger = get_logger(__name__)

# Log messages
logger.info("application_started", version="1.0.0")
logger.warning("cache_miss", key="user_123")
logger.error("database_error", error="Connection timeout")
```

### Correlation ID for Request Tracing

```python
from core.logging_config import CorrelationIdContext, get_logger

logger = get_logger(__name__)

# Automatic correlation ID generation
with CorrelationIdContext() as correlation_id:
    logger.info("request_started", method="POST", path="/api/users")
    process_request()
    logger.info("request_completed", duration_ms=123)
    # All logs within this block share the same correlation_id

# Custom correlation ID (e.g., from HTTP header)
with CorrelationIdContext("req-abc-123"):
    logger.info("processing_request")
```

### Adding Context to Logs

```python
from core.logging_config import LogContext, get_logger

logger = get_logger(__name__)

# Add context for a scope
with LogContext(user_id="123", session="abc-def"):
    logger.info("user_action", action="login")
    logger.info("profile_updated")
    # All logs include user_id and session

# One-off context
logger.info("payment_processed", 
    user_id="123",
    amount=99.99,
    currency="USD",
    payment_method="credit_card"
)
```

### Error Logging

```python
from core.logging_config import log_error, get_logger

logger = get_logger(__name__)

try:
    risky_operation()
except Exception as e:
    # Log with full context and traceback
    log_error(e, {
        "user_id": "123",
        "operation": "checkout",
        "cart_items": 5
    })
```

### Event Tracking

```python
from core.logging_config import track

# Track user events
track("user_login", {
    "user_id": "123",
    "method": "oauth",
    "provider": "google"
})

track("form_submitted", {
    "form_id": "contact",
    "duration_ms": 1234,
    "fields_filled": 5
})

track("feature_used", {
    "feature": "export_pdf",
    "user_tier": "premium"
})
```

### Runtime Log Level Adjustment

```python
from core.logging_config import set_log_level
import logging

# Change log level at runtime
set_log_level("DEBUG")      # String
set_log_level(logging.INFO)  # Constant

# Useful for debugging production issues
```

## Log Levels by Environment

| Environment | Default Level | Description |
|------------|---------------|-------------|
| Development | DEBUG | All logs including debug messages |
| Staging | INFO | Informational and above |
| Production | WARNING | Warnings, errors, and critical only |

## PII Masking

Sensitive data is automatically masked in logs:

```python
logger.info("user_login",
    username="john",
    password="secret123",  # Automatically masked
    api_key="sk-abc123"    # Automatically masked
)

# Output: password="***REDACTED***", api_key="***REDACTED***"
```

Masked fields:
- `password`, `secret`, `token`
- `api_key`, `apikey`, `authorization`
- `credit_card`, `ssn`, `social_security`

## Log Output Formats

### Development (Console)
```
2025-01-19T10:30:45Z [info     ] user_login                     user_id=123 method=oauth
2025-01-19T10:30:46Z [warning  ] cache_miss                     key=user_123
2025-01-19T10:30:47Z [error    ] database_error                 error=Connection timeout
```

### Production (JSON)
```json
{
  "timestamp": "2025-01-19T10:30:45Z",
  "level": "info",
  "event": "user_login",
  "user_id": "123",
  "method": "oauth",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "logger": "app.auth"
}
```

## Best Practices

### ✅ DO

```python
# Use structured logging with key-value pairs
logger.info("user_created", user_id="123", email="user@example.com")

# Use correlation IDs for request tracing
with CorrelationIdContext():
    process_request()

# Log errors with context
log_error(exception, {"user_id": "123", "operation": "save"})

# Use descriptive event names
track("checkout_completed", {"order_id": "456", "total": 99.99})
```

### ❌ DON'T

```python
# Don't use string formatting
logger.info(f"User {user_id} logged in")  # ❌

# Don't log sensitive data without masking
logger.info("auth", password=user_password)  # ❌ (auto-masked anyway)

# Don't use generic event names
logger.info("event", data=some_data)  # ❌

# Don't log in tight loops without throttling
for item in million_items:
    logger.debug("processing", item=item)  # ❌
```

## Integration with Existing Code

### Replace Standard Logging

```python
# Old way
import logging
logger = logging.getLogger(__name__)
logger.info("User logged in: %s", user_id)

# New way
from core.logging_config import get_logger
logger = get_logger(__name__)
logger.info("user_login", user_id=user_id)
```

### Streamlit Integration

```python
import streamlit as st
from core.logging_config import get_logger, CorrelationIdContext

logger = get_logger(__name__)

# Generate correlation ID per session
if "correlation_id" not in st.session_state:
    with CorrelationIdContext() as correlation_id:
        st.session_state.correlation_id = correlation_id

# Use correlation ID for all logs in this session
with CorrelationIdContext(st.session_state.correlation_id):
    logger.info("page_rendered", page="dashboard")
```

## Centralized Logging Preparation

The logging system is ready for centralized logging:

### Elasticsearch/Logstash
- JSON output format ✅
- Structured fields ✅
- Correlation IDs ✅
- Timestamps in ISO 8601 ✅

### CloudWatch/Datadog
- Structured logging ✅
- Custom fields ✅
- Error tracking ✅
- Performance metrics ✅

### Configuration
```python
# In production, pipe JSON logs to your aggregation system
# Example: Docker logs → Fluentd → Elasticsearch
```

## Troubleshooting

### Logs not appearing?
```python
# Check log level
import logging
print(logging.root.level)  # Should be DEBUG in dev

# Manually set level
from core.logging_config import set_log_level
set_log_level("DEBUG")
```

### Correlation ID not propagating?
```python
# Ensure you're using the context manager
with CorrelationIdContext() as correlation_id:
    # All code here will have correlation_id
    your_function()
```

### PII still visible in logs?
```python
# Check field names - must contain sensitive keywords
# password, secret, token, api_key, etc.
logger.info("data", user_password="secret")  # Will be masked
```

## Examples

### Complete Request Handling
```python
from core.logging_config import (
    get_logger, 
    CorrelationIdContext, 
    LogContext,
    log_error
)

logger = get_logger(__name__)

def handle_request(request):
    with CorrelationIdContext(request.headers.get("X-Correlation-ID")):
        logger.info("request_received", 
            method=request.method,
            path=request.path
        )
        
        try:
            with LogContext(user_id=request.user_id):
                result = process_request(request)
                logger.info("request_completed", 
                    status=200,
                    duration_ms=123
                )
                return result
        except Exception as e:
            log_error(e, {
                "method": request.method,
                "path": request.path
            })
            raise
```

### Background Job Logging
```python
from core.logging_config import get_logger, CorrelationIdContext

logger = get_logger(__name__)

def process_job(job_id, correlation_id=None):
    with CorrelationIdContext(correlation_id):
        logger.info("job_started", job_id=job_id)
        
        try:
            result = expensive_operation()
            logger.info("job_completed", 
                job_id=job_id,
                duration_ms=5000,
                records_processed=1000
            )
            return result
        except Exception as e:
            log_error(e, {"job_id": job_id})
            raise
```

## API Reference

### Functions

- `setup_logging(config)` - Initialize logging system
- `get_logger(name)` - Get structured logger
- `set_log_level(level)` - Change log level at runtime
- `log_error(err, ctx, logger_name)` - Log error with context
- `track(event, props)` - Track user event
- `generate_correlation_id()` - Generate new correlation ID
- `get_correlation_id()` - Get current correlation ID
- `set_correlation_id(id)` - Set correlation ID
- `clear_correlation_id()` - Clear correlation ID

### Context Managers

- `CorrelationIdContext(id)` - Correlation ID scope
- `LogContext(**kwargs)` - Add context to logs

### Requirements

- Requirements: 7.6, 9.5, 12.5
- Related: Task 1.2 - Structured Logging Implementation
