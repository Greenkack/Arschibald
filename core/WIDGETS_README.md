# Controlled Widget System with Auto-Persistence

This module provides a comprehensive controlled widget system for Streamlit applications with automatic state management, persistence, and validation.

## Overview

The controlled widget system implements the following key features:

1. **Unified State Management**: All widgets use consistent state management with stable keys
2. **Auto-Persistence**: Immediate session_state updates with debounced database writes
3. **Real-Time Validation**: Configurable validation rules with field-level error messages
4. **Change Detection**: Track widget changes and dirty states
5. **Conflict Resolution**: Handle concurrent user scenarios with configurable strategies
6. **State Recovery**: Restore widget states after browser refresh

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Widget                          │
│                    (s_text, s_number, etc.)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─> Immediate: st.session_state update
                     │
                     ├─> Validation: Real-time validation
                     │
                     └─> Persistence: Debounced DB write
                              │
                              ├─> Batch Queue (10 widgets or 1s)
                              │
                              └─> Database (widget_states table)
```

## Components

### 1. Controlled Widgets (`core/widgets.py`)

Provides wrapped Streamlit widgets with unified behavior:

- `s_text()` - Text input
- `s_number()` - Number input
- `s_select()` - Selectbox
- `s_checkbox()` - Checkbox
- `s_date()` - Date input
- `s_file()` - File uploader
- `s_multiselect()` - Multiselect
- `s_slider()` - Slider
- `s_textarea()` - Text area
- `s_radio()` - Radio buttons

### 2. Widget Persistence (`core/widget_persistence.py`)

Handles debounced persistence to database:

- **Debouncing**: 500ms default delay before DB write
- **Batching**: Groups up to 10 widget updates or 1s timeout
- **Conflict Resolution**: Last-write-wins or merge strategies
- **Recovery**: Restore states from database

### 3. Widget Validation (`core/widget_validation.py`)

Provides real-time validation:

- **Built-in Rules**: Required, min/max length, min/max value, range, pattern, email, URL, phone, date range
- **Custom Rules**: Define custom validation functions
- **Error Display**: Automatic error and warning messages
- **Validation State**: Track validation status per widget

## Usage Examples

### Basic Text Input

```python
from core import s_text

# Simple text input with auto-persistence
name = s_text(
    label="Your Name",
    placeholder="Enter your name",
    help="This will be saved automatically"
)
```

### Text Input with Validation

```python
from core import s_text, required_text

# Text input with validation
email = s_text(
    label="Email Address",
    placeholder="user@example.com",
    validator=required_text(min_length=5, max_length=100)
)
```

### Number Input with Range Validation

```python
from core import s_number, required_number

# Number input with range validation
age = s_number(
    label="Age",
    min_value=0,
    max_value=150,
    validator=required_number(min_value=18, max_value=100)
)
```

### Select with Custom Validation

```python
from core import s_select, Validator, CustomRule

# Custom validation function
def validate_country(value):
    return value in ["USA", "Canada", "UK"]

# Select with custom validation
country = s_select(
    options=["USA", "Canada", "UK", "Other"],
    label="Country",
    validator=Validator([
        CustomRule(validate_country, "Please select a valid country")
    ])
)
```

### Multiselect with Max Selections

```python
from core import s_multiselect, Validator, CustomRule

# Validator for max selections
def max_3_selections(value):
    return len(value) <= 3

skills = s_multiselect(
    options=["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
    label="Select up to 3 skills",
    validator=Validator([
        CustomRule(max_3_selections, "Please select at most 3 skills")
    ])
)
```

### Date Input with Range

```python
from core import s_date, required_date
from datetime import date, timedelta

# Date input with range validation
today = date.today()
start_date = s_date(
    label="Start Date",
    min_value=today,
    max_value=today + timedelta(days=365),
    validator=required_date(min_date=today, max_date=today + timedelta(days=365))
)
```

### File Upload with Validation

```python
from core import s_file, Validator, CustomRule

# Validator for file size
def validate_file_size(file):
    if file is None:
        return True
    return file.size <= 5 * 1024 * 1024  # 5MB

uploaded_file = s_file(
    label="Upload Document",
    type=["pdf", "docx"],
    validator=Validator([
        CustomRule(validate_file_size, "File must be less than 5MB")
    ])
)
```

## Advanced Features

### Widget State Management

```python
from core import get_widget_state, get_all_widget_states, get_dirty_widgets

# Get state for specific widget
state = get_widget_state("my_widget_key")
print(f"Value: {state.value}")
print(f"Is dirty: {state.is_dirty}")
print(f"Is valid: {state.is_valid}")
print(f"Errors: {state.errors}")

# Get all widget states
all_states = get_all_widget_states()

# Get dirty (unsaved) widgets
dirty_widgets = get_dirty_widgets()
print(f"Unsaved widgets: {dirty_widgets}")
```

### Manual Persistence Control

```python
from core import flush_widget_states, save_widget_state

# Flush all pending saves immediately
flush_widget_states()

# Flush specific session
flush_widget_states(session_id="abc123")

# Flush specific widget
flush_widget_states(session_id="abc123", widget_key="my_widget")

# Manually save widget state
save_widget_state(
    session_id="abc123",
    widget_key="my_widget",
    widget_value="some value",
    widget_type="text",
    is_valid=True
)
```

### State Recovery

```python
from core import recover_widget_states, get_current_session

# Recover all widget states for current session
session = get_current_session()
recovered = recover_widget_states(session.session_id)

for widget_key, state_data in recovered.items():
    print(f"{widget_key}: {state_data['value']}")
    print(f"  Valid: {state_data['is_valid']}")
    print(f"  Errors: {state_data['errors']}")
```

### Custom Validators

```python
from core import Validator, ValidationRule

# Create custom validation rule
class PasswordStrengthRule(ValidationRule):
    def __init__(self):
        super().__init__(error_message="Password must contain uppercase, lowercase, and numbers")
    
    def validate(self, value):
        if value is None or value == "":
            return True, None, None
        
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        
        if has_upper and has_lower and has_digit:
            return True, None, None
        else:
            return False, self.error_message, None

# Use custom rule
from core import s_text, RequiredRule

password = s_text(
    label="Password",
    type="password",
    validator=Validator([
        RequiredRule(),
        PasswordStrengthRule()
    ])
)
```

### Validation Engine

```python
from core import get_validation_engine, Validator, required_text

# Get global validation engine
engine = get_validation_engine()

# Register validators for multiple widgets
engine.register_validator("username", required_text(min_length=3, max_length=20))
engine.register_validator("email", required_email())
engine.register_validator("age", required_number(min_value=18, max_value=100))

# Validate all at once
values = {
    "username": "john",
    "email": "john@example.com",
    "age": 25
}

results = engine.validate_all(values)
for key, (is_valid, errors, warnings) in results.items():
    print(f"{key}: valid={is_valid}, errors={errors}")

# Check if all valid
if engine.is_all_valid(values):
    print("All fields are valid!")
```

## Configuration

### Debounce Settings

```python
from core import get_persistence_engine

# Get persistence engine
engine = get_persistence_engine()

# Default settings:
# - debounce_ms: 500 (wait 500ms before saving)
# - batch_size: 10 (save when 10 widgets changed)
# - batch_timeout_ms: 1000 (save after 1s even if batch not full)
```

### Cleanup Old States

```python
from core import cleanup_old_widget_states

# Clean up widget states older than 24 hours
count = cleanup_old_widget_states(max_age_hours=24)
print(f"Cleaned up {count} old widget states")
```

## Database Schema

The widget persistence system uses the following table:

```sql
CREATE TABLE widget_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) NOT NULL,
    widget_key VARCHAR(255) NOT NULL,
    widget_value TEXT,
    widget_type VARCHAR(50),
    is_valid INTEGER DEFAULT 1,
    errors TEXT,  -- JSON array
    warnings TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    INDEX idx_session_id (session_id),
    INDEX idx_widget_key (widget_key)
);
```

## Best Practices

1. **Use Stable Keys**: Always provide explicit keys for widgets that need to persist across sessions
2. **Validate Early**: Add validation rules to catch errors before they reach the database
3. **Batch Updates**: Let the system batch updates automatically for better performance
4. **Clean Up**: Regularly clean up old widget states to prevent database bloat
5. **Handle Conflicts**: Use appropriate conflict resolution strategy for your use case
6. **Test Recovery**: Test widget state recovery after browser refresh
7. **Monitor Performance**: Track widget persistence performance in production

## Performance Considerations

- **Debouncing**: Reduces database writes by waiting for user to finish typing
- **Batching**: Groups multiple widget updates into single database transaction
- **Indexing**: Session ID and widget key are indexed for fast lookups
- **Cleanup**: Regular cleanup prevents table from growing indefinitely

## Error Handling

The system handles errors gracefully:

- **Validation Errors**: Displayed inline with the widget
- **Persistence Errors**: Logged but don't block UI
- **Recovery Errors**: Fall back to default values
- **Conflict Errors**: Use configured resolution strategy

## Integration with Session Management

The widget system integrates seamlessly with the session management system:

```python
from core import get_current_session, persist_input

# Widget changes automatically update session
session = get_current_session()

# Access widget values from session
value = session.form_states.get("my_form", {}).get("my_widget")

# Manual persistence also available
persist_input("my_widget", "new value")
```

## Testing

See `core/test_widgets.py` for comprehensive test examples.

## Troubleshooting

### Widgets Not Persisting

1. Check database connection
2. Verify session ID is valid
3. Check logs for persistence errors
4. Ensure `init_widget_persistence_tables()` was called

### Validation Not Working

1. Verify validator is properly configured
2. Check validation function returns correct tuple format
3. Ensure validator is passed to widget
4. Check logs for validation errors

### State Not Recovering

1. Verify session ID matches
2. Check database for widget states
3. Ensure recovery is called after session bootstrap
4. Check for serialization errors in logs

## See Also

- [Session Management](SESSION_README.md)
- [Navigation System](NAVIGATION_README.md)
- [Configuration](CONFIG_README.md)
