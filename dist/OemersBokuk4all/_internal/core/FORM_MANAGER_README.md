# Form State Management with Undo/Redo

Comprehensive form state management system with undo/redo functionality, validation, auto-save, and conflict resolution.

## Features

- **Enhanced FormState**: Complete form state with snapshot management and validation
- **Undo/Redo System**: Full undo/redo functionality with configurable history depth
- **Validation Engine**: Real-time validation with debounced execution and custom validators
- **Auto-Save**: Debounced auto-save with conflict resolution
- **Form Dependencies**: Track dependencies between related forms
- **Transactional Persistence**: All saves are transactional with rollback capability
- **Snapshot Management**: Create, restore, and manage form snapshots
- **Conflict Resolution**: Multiple strategies for handling concurrent edits

## Quick Start

### Basic Usage

```python
from core.form_manager import create_form, update_form_field, save_form_now

# Create a new form
form_state = create_form(
    form_id="user_profile",
    session_id="session_123",
    user_id="user_456",
    initial_data={"name": "", "email": ""}
)

# Update form fields
update_form_field("user_profile", "session_123", "name", "John Doe")
update_form_field("user_profile", "session_123", "email", "john@example.com")

# Save immediately
save_form_now("user_profile", "session_123")
```

### Undo/Redo

```python
from core.form_manager import undo_form, redo_form, get_form_manager

manager = get_form_manager()

# Make changes
update_form_field("user_profile", "session_123", "name", "John Doe")
update_form_field("user_profile", "session_123", "name", "Jane Smith")
update_form_field("user_profile", "session_123", "name", "Bob Johnson")

# Undo changes
if manager.can_undo("user_profile", "session_123"):
    undo_form("user_profile", "session_123")  # Back to "Jane Smith"
    undo_form("user_profile", "session_123")  # Back to "John Doe"

# Redo changes
if manager.can_redo("user_profile", "session_123"):
    redo_form("user_profile", "session_123")  # Forward to "Jane Smith"
```

### Validation

```python
from core.form_manager import get_form_validator, validate_form

validator = get_form_validator()

# Register field validator
def validate_email(value):
    if "@" not in value:
        return False, "Invalid email address"
    return True, None

validator.register_validator("user_profile", "email", validate_email)

# Register form-level validator
def validate_passwords_match(data):
    if data.get("password") != data.get("confirm_password"):
        return False, {"confirm_password": ["Passwords do not match"]}
    return True, {}

validator.register_form_validator("user_profile", validate_passwords_match)

# Validate form
result = validate_form("user_profile", "session_123")
if not result.is_valid:
    print("Validation errors:", result.errors)
```

### Auto-Save

```python
from core.form_manager import FormManager

manager = FormManager()

# Auto-save is enabled by default
form_state = manager.get_form(
    form_id="user_profile",
    session_id="session_123",
    auto_save_enabled=True
)

# Changes are automatically saved after debounce period
manager.update_field("user_profile", "session_123", "name", "John Doe")
# ... auto-save will trigger after 500ms

# Check save status
status = manager.get_save_status("user_profile")
print(f"Save status: {status['status']}")  # pending, saving, saved, or error
```

### Snapshots

```python
from core.form_manager import get_form_manager

manager = get_form_manager()

# Create manual snapshot
snapshot = manager.create_snapshot(
    form_id="user_profile",
    session_id="session_123",
    description="Before major changes",
    snapshot_type="checkpoint"
)

# Get snapshot history
history = manager.get_snapshot_history("user_profile", "session_123")
for snap in history:
    print(f"{snap.timestamp}: {snap.description}")

# Restore specific snapshot
manager.restore_snapshot("user_profile", "session_123", snapshot.snapshot_id)
```

## Advanced Usage

### Form Manager API

```python
from core.form_manager import FormManager

manager = FormManager()

# Get or create form
form_state = manager.get_form(
    form_id="complex_form",
    session_id="session_123",
    user_id="user_456",
    auto_save_enabled=True,
    max_snapshots=100
)

# Update single field
result = manager.update_field(
    form_id="complex_form",
    session_id="session_123",
    field="amount",
    value=1000,
    create_snapshot=True,
    validate=True
)

# Update multiple fields
result = manager.update_multiple(
    form_id="complex_form",
    session_id="session_123",
    updates={
        "field1": "value1",
        "field2": "value2",
        "field3": "value3"
    },
    create_snapshot=True,
    validate=True
)

# Save with options
manager.save(
    form_id="complex_form",
    session_id="session_123",
    immediate=True  # Skip debounce
)

# Reset form
manager.reset(
    form_id="complex_form",
    session_id="session_123",
    create_snapshot=True  # Create snapshot before reset
)

# Check form state
is_dirty = manager.is_dirty("complex_form", "session_123")
is_valid = manager.is_valid("complex_form", "session_123")
```

### Custom Validators

```python
from core.form_manager import get_form_validator

validator = get_form_validator()

# Required field validator
def validate_required(value):
    if not value or (isinstance(value, str) and not value.strip()):
        return False, "This field is required"
    return True, None

# Numeric range validator
def validate_range(min_val, max_val):
    def validator(value):
        if not isinstance(value, (int, float)):
            return False, "Must be a number"
        if value < min_val or value > max_val:
            return False, f"Must be between {min_val} and {max_val}"
        return True, None
    return validator

# String length validator
def validate_length(min_len, max_len):
    def validator(value):
        if not isinstance(value, str):
            return False, "Must be a string"
        if len(value) < min_len:
            return False, f"Must be at least {min_len} characters"
        if len(value) > max_len:
            return False, f"Must be at most {max_len} characters"
        return True, None
    return validator

# Register validators
validator.register_validator("my_form", "name", validate_required)
validator.register_validator("my_form", "name", validate_length(2, 50))
validator.register_validator("my_form", "age", validate_range(0, 120))
```

### Debounced Validation

```python
from core.form_manager import get_form_validator

validator = get_form_validator()

def on_validation_complete(result):
    if result.is_valid:
        print("Form is valid!")
    else:
        print("Validation errors:", result.errors)

# Validate with debouncing (useful for real-time validation)
validator.validate_debounced(
    form_id="my_form",
    data={"name": "John", "email": "john@example.com"},
    callback=on_validation_complete,
    debounce_ms=300
)
```

### Conflict Resolution

```python
from core.form_manager import get_auto_save

auto_save = get_auto_save()

# Resolve conflicts with different strategies
resolved_data, was_conflict = auto_save.resolve_conflict(
    form_id="my_form",
    session_id="session_123",
    local_data={"field1": "local_value"},
    local_updated_at=datetime.now(),
    strategy="last_write_wins"  # or "prefer_local", "prefer_remote", "merge"
)

if was_conflict:
    print("Conflict detected and resolved")
    print("Resolved data:", resolved_data)
```

### Form Recovery

```python
from core.form_manager import get_auto_save

auto_save = get_auto_save()

# Recover form after unexpected termination
recovered_form = auto_save.recover_form(
    form_id="my_form",
    session_id="session_123"
)

if recovered_form:
    print("Form recovered successfully")
    print("Data:", recovered_form.data)
    print("Snapshots:", len(recovered_form.snapshots))
else:
    print("No form data to recover")
```

### Form Dependencies

```python
from core.form_manager import get_form_manager

manager = get_form_manager()

# Get forms
parent_form = manager.get_form("parent_form", "session_123")
child_form = manager.get_form("child_form", "session_123")

# Set up dependencies
child_form.add_dependency("parent_form")
parent_form.add_dependent("child_form")

# When parent changes, you can update children
def on_parent_change(parent_data):
    for dependent_id in parent_form.dependents:
        # Update dependent forms
        manager.update_field(
            dependent_id,
            "session_123",
            "parent_value",
            parent_data.get("key_field")
        )
```

## Streamlit Integration

```python
import streamlit as st
from core.form_manager import get_form_manager

manager = get_form_manager()

# Get session ID from Streamlit
session_id = st.session_state.get('session_id', 'default')

# Create form
form_state = manager.get_form("user_form", session_id)

# Form UI
st.title("User Profile")

name = st.text_input("Name", value=form_state.data.get("name", ""))
if name != form_state.data.get("name"):
    manager.update_field("user_form", session_id, "name", name)

email = st.text_input("Email", value=form_state.data.get("email", ""))
if email != form_state.data.get("email"):
    manager.update_field("user_form", session_id, "email", email)

# Display validation errors
if form_state.errors:
    for field, errors in form_state.errors.items():
        for error in errors:
            st.error(f"{field}: {error}")

# Undo/Redo buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Undo", disabled=not manager.can_undo("user_form", session_id)):
        manager.undo("user_form", session_id)
        st.rerun()

with col2:
    if st.button("Redo", disabled=not manager.can_redo("user_form", session_id)):
        manager.redo("user_form", session_id)
        st.rerun()

with col3:
    if st.button("Reset"):
        manager.reset("user_form", session_id)
        st.rerun()

# Save button
if st.button("Save", type="primary"):
    if manager.save("user_form", session_id, immediate=True):
        st.success("Form saved successfully!")
    else:
        st.error("Failed to save form")

# Display save status
status = manager.get_save_status("user_form")
if status:
    if status['status'] == 'saving':
        st.info("Saving...")
    elif status['status'] == 'saved':
        st.success(f"Last saved: {status['saved_at']}")
    elif status['status'] == 'error':
        st.error(f"Save error: {status['error']}")
```

## Database Schema

The form management system uses three database tables:

### form_data
- `id`: Primary key
- `form_id`: Form identifier
- `user_id`: User identifier (optional)
- `session_id`: Session identifier
- `data`: Form data (JSON)
- `metadata`: Additional metadata (JSON)
- `version`: Version number
- `is_dirty`: Has unsaved changes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `deleted_at`: Soft delete timestamp

### form_snapshots
- `id`: Primary key
- `snapshot_id`: Unique snapshot identifier
- `form_id`: Form identifier
- `user_id`: User identifier (optional)
- `session_id`: Session identifier
- `data`: Snapshot data (JSON)
- `description`: Snapshot description
- `snapshot_type`: Type (manual, auto, checkpoint)
- `created_at`: Creation timestamp

### form_validation
- `id`: Primary key
- `form_id`: Form identifier
- `session_id`: Session identifier
- `errors`: Validation errors (JSON)
- `warnings`: Validation warnings (JSON)
- `is_valid`: Validation status
- `validated_at`: Validation timestamp

## Configuration

```python
from core.form_manager import FormManager, FormAutoSave

# Configure auto-save debounce
auto_save = FormAutoSave(debounce_ms=1000)  # 1 second

# Configure form with custom settings
form_state = manager.get_form(
    form_id="my_form",
    session_id="session_123",
    auto_save_enabled=True,
    max_snapshots=100  # Keep up to 100 snapshots
)

# Configure snapshot retention
form_state.max_snapshots = 50
form_state.cleanup_old_snapshots(keep_count=50)
```

## Best Practices

1. **Use Descriptive Form IDs**: Use meaningful form IDs that describe the form's purpose
2. **Enable Auto-Save**: Enable auto-save for better user experience
3. **Create Checkpoints**: Create manual snapshots before major operations
4. **Validate Early**: Validate fields as users type for immediate feedback
5. **Handle Errors**: Always check validation results and display errors to users
6. **Clean Up Snapshots**: Periodically clean up old snapshots to save space
7. **Use Dependencies**: Track form dependencies for related forms
8. **Test Recovery**: Test form recovery to ensure data isn't lost

## Performance Considerations

- **Debouncing**: Auto-save and validation are debounced to prevent excessive operations
- **Snapshot Limits**: Configure appropriate snapshot limits based on your needs
- **Batch Updates**: Use `update_multiple()` for updating many fields at once
- **Lazy Loading**: Forms are loaded on-demand, not all at once
- **Database Indexes**: Form tables have indexes on frequently queried columns

## Troubleshooting

### Forms Not Saving
- Check database connection
- Verify session_id is consistent
- Check auto-save status with `get_save_status()`
- Try immediate save with `save(immediate=True)`

### Undo/Redo Not Working
- Ensure snapshots are being created (`create_snapshot=True`)
- Check snapshot history with `get_snapshot_history()`
- Verify max_snapshots limit isn't too low

### Validation Not Running
- Ensure validators are registered before validation
- Check validation result for errors
- Use debounced validation for real-time feedback

### Performance Issues
- Reduce max_snapshots limit
- Increase debounce delays
- Clean up old snapshots regularly
- Use batch updates for multiple fields

## API Reference

See the module docstrings for complete API documentation:

```python
from core import form_manager
help(form_manager.FormManager)
help(form_manager.FormState)
help(form_manager.FormValidator)
help(form_manager.FormAutoSave)
```
