# Session Recovery System

## Overview

The Session Recovery System provides complete session state restoration after browser refresh, ensuring zero data loss and seamless user experience. This system is a critical component of the robust Streamlit application architecture.

## Features

- **Complete Session Restoration**: Recover all session data after browser refresh
- **Form Data Recovery**: Restore form inputs with validation and error handling
- **Navigation State Preservation**: Maintain current page and navigation history
- **Cache Key Restoration**: Preserve cache keys for performance optimization
- **Automatic Retry Logic**: Retry recovery with exponential backoff on failures
- **Validation Support**: Validate recovered form data against schemas
- **Error Handling**: Graceful degradation with detailed error reporting

## Architecture

### Components

1. **SessionRecoveryManager**: Core recovery logic and orchestration
2. **Form Validation**: Schema-based validation of recovered form data
3. **Navigation Recovery**: Restore page state and navigation history
4. **Cache Recovery**: Restore cache keys and dependencies
5. **Error Handling**: Comprehensive error handling and reporting

### Recovery Flow

```
Browser Refresh
    ↓
Detect Session ID (query params or session_state)
    ↓
Recover from Database
    ↓
Validate Form Data (optional)
    ↓
Restore Navigation State
    ↓
Restore Cache Keys
    ↓
Update Session State
    ↓
Session Recovered
```

## Usage

### Basic Usage

```python
from core.session_recovery import recover_session_after_refresh, ensure_session_persistence

# At the top of your Streamlit app
ensure_session_persistence()

# Recover session after refresh
session = recover_session_after_refresh(validate_forms=True)

if session:
    print(f"Session recovered: {session.session_id}")
    print(f"Current page: {session.current_page}")
```

### Streamlit Integration

```python
import streamlit as st
from core.session_recovery import (
    recover_session_after_refresh,
    ensure_session_persistence,
    get_recovery_status
)

# Ensure session can be recovered
ensure_session_persistence()

# Recover session
session = recover_session_after_refresh(validate_forms=True)

# Check for validation errors
status = get_recovery_status()
if status['has_errors']:
    st.warning("Some form data could not be validated")
    for form_id, errors in status['validation_errors'].items():
        st.error(f"{form_id}: {errors}")

# Use recovered session
st.write(f"Welcome back! Session: {session.session_id}")
```

### Recovery with Specific Session ID

```python
from core.session_recovery import recover_session_after_refresh

# Recover specific session
session = recover_session_after_refresh(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    validate_forms=True
)
```

### Recovery without Validation

```python
from core.session_recovery import recover_session_after_refresh

# Skip validation for faster recovery
session = recover_session_after_refresh(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    validate_forms=False
)
```

## Form Validation

### Validation Schema

Form validation schemas define rules for validating recovered form data:

```python
validation_schema = {
    'name': {
        'required': True,
        'type': 'string',
        'minLength': 2,
        'maxLength': 100
    },
    'email': {
        'required': True,
        'type': 'string'
    },
    'age': {
        'type': 'number',
        'min': 18,
        'max': 120
    },
    'active': {
        'type': 'boolean'
    }
}
```

### Supported Validation Rules

- **required**: Field must have a value
- **type**: Data type validation (string, number, boolean)
- **min/max**: Numeric range validation
- **minLength/maxLength**: String length validation

### Handling Validation Errors

```python
from core.session_recovery import (
    recover_session_after_refresh,
    get_recovery_status,
    clear_recovery_errors
)

# Recover with validation
session = recover_session_after_refresh(validate_forms=True)

# Check for errors
status = get_recovery_status()
if status['has_errors']:
    for form_id, errors in status['validation_errors'].items():
        print(f"Form '{form_id}' has errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Clear errors after handling
    clear_recovery_errors()
```

## Navigation Recovery

### Navigation State

The recovery system preserves:

- Current page
- Page parameters
- Navigation history
- Page view counts

```python
session = recover_session_after_refresh()

print(f"Current page: {session.current_page}")
print(f"Page params: {session.page_params}")
print(f"History: {len(session.navigation_history)} entries")
```

### Navigation History

```python
# Access navigation history
for entry in session.navigation_history:
    print(f"{entry.page} - {entry.timestamp}")
    print(f"  Params: {entry.params}")
```

## Cache Recovery

### Cache Keys

The recovery system restores cache keys and dependencies:

```python
session = recover_session_after_refresh()

print(f"Cache keys: {len(session.cache_keys)}")
print(f"Dependencies: {len(session.cache_dependencies)}")

# Use recovered cache keys
for key in session.cache_keys:
    if key in session.cache_dependencies:
        deps = session.cache_dependencies[key]
        print(f"{key} depends on: {deps}")
```

## Error Handling

### Exception Types

- **SessionRecoveryError**: Base exception for recovery errors
- **FormValidationError**: Form validation failures
- **NavigationRecoveryError**: Navigation state recovery failures
- **CacheRecoveryError**: Cache key recovery failures

### Error Handling Example

```python
from core.session_recovery import (
    recover_session_after_refresh,
    SessionRecoveryError
)

try:
    session = recover_session_after_refresh(validate_forms=True)
except SessionRecoveryError as e:
    print(f"Recovery failed: {e}")
    # Fall back to new session
    from core.session import bootstrap_session
    session = bootstrap_session()
```

## Advanced Usage

### Custom Recovery Manager

```python
from core.session_recovery import SessionRecoveryManager

# Create custom manager
manager = SessionRecoveryManager()
manager.max_recovery_attempts = 5

# Perform recovery
session = manager.recover_complete_session(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    validate_forms=True
)

# Get detailed status
status = manager.get_recovery_status()
print(f"Attempts: {status['recovery_attempts']}")
```

### Recovery Status

```python
from core.session_recovery import get_recovery_status

status = get_recovery_status()

print(f"Recovery attempts: {status['recovery_attempts']}")
print(f"Max attempts: {status['max_attempts']}")
print(f"Has errors: {status['has_errors']}")
print(f"Validation errors: {status['validation_errors']}")
```

## Best Practices

### 1. Always Ensure Persistence

Call `ensure_session_persistence()` at the top of every page:

```python
from core.session_recovery import ensure_session_persistence

ensure_session_persistence()
```

### 2. Validate Forms in Production

Enable form validation in production to catch data integrity issues:

```python
session = recover_session_after_refresh(validate_forms=True)
```

### 3. Handle Validation Errors

Always check for and handle validation errors:

```python
status = get_recovery_status()
if status['has_errors']:
    # Handle errors appropriately
    pass
```

### 4. Log Recovery Events

Log recovery events for monitoring and debugging:

```python
import logging

logger = logging.getLogger(__name__)

session = recover_session_after_refresh()
if session:
    logger.info(f"Session recovered: {session.session_id}")
```

### 5. Graceful Degradation

Always have a fallback for recovery failures:

```python
try:
    session = recover_session_after_refresh()
except SessionRecoveryError:
    session = bootstrap_session()
```

## Performance Considerations

### Recovery Time

- Database query: ~10-50ms
- Form validation: ~5-20ms per form
- Navigation restoration: ~1-5ms
- Cache restoration: ~1-5ms
- **Total**: ~20-100ms typical

### Optimization Tips

1. **Skip validation** when not needed for faster recovery
2. **Limit navigation history** size to reduce data transfer
3. **Use database indexes** on session_id for faster queries
4. **Cache session data** in memory for repeated access

## Testing

### Unit Tests

```bash
pytest core/test_session_recovery.py -v
```

### Integration Tests

```bash
pytest core/test_session_recovery.py::TestSessionRecoveryIntegration -v
```

### Test Coverage

Run tests with coverage:

```bash
pytest core/test_session_recovery.py --cov=core.session_recovery --cov-report=html
```

## Troubleshooting

### Session Not Found

**Problem**: Session not found in database after refresh

**Solution**:
- Check that `ensure_session_persistence()` is called
- Verify session is being saved to database
- Check database connectivity

### Validation Errors

**Problem**: Form validation fails during recovery

**Solution**:
- Review validation schema
- Check form data integrity
- Consider skipping validation temporarily

### Recovery Timeout

**Problem**: Recovery takes too long

**Solution**:
- Check database performance
- Reduce navigation history size
- Skip validation if not critical

### Cache Keys Not Restored

**Problem**: Cache keys not available after recovery

**Solution**:
- Verify cache keys are being tracked
- Check session persistence
- Review cache key naming

## API Reference

### Functions

#### `recover_session_after_refresh(session_id=None, user_id=None, validate_forms=True)`

Recover session after browser refresh.

**Parameters**:
- `session_id` (str, optional): Session ID to recover
- `user_id` (str, optional): User ID for recovery
- `validate_forms` (bool): Whether to validate form data

**Returns**: `UserSession` or `None`

#### `ensure_session_persistence()`

Ensure session ID is persisted for recovery.

#### `get_recovery_status()`

Get current recovery status.

**Returns**: Dictionary with recovery status

#### `clear_recovery_errors()`

Clear recovery validation errors.

### Classes

#### `SessionRecoveryManager`

Main recovery manager class.

**Methods**:
- `recover_complete_session()`: Recover complete session
- `get_recovery_status()`: Get recovery status
- `clear_validation_errors()`: Clear validation errors

## Requirements

This module satisfies the following requirements:

- **Requirement 1.3**: Session state restoration after browser refresh
- **Requirement 2.6**: Session recovery mechanism for browser refresh scenarios
- **Requirement 4.2**: Cache key restoration for performance optimization

## Related Documentation

- [Session Management](./SESSION_README.md)
- [Configuration System](./CONFIG_README.md)
- [Database Management](./database.py)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review example usage files
3. Run tests to verify functionality
4. Check logs for detailed error messages
