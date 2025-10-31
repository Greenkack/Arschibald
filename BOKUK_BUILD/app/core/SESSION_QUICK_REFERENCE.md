# Session Management Quick Reference

## Overview

The session management system provides comprehensive state persistence, navigation tracking, and form management for Streamlit applications with zero data loss guarantees.

## Key Features

- **Automatic Persistence**: All session data is automatically saved to database with debouncing
- **Browser Refresh Recovery**: Complete session state restoration after page refresh
- **Navigation History**: Track and navigate through page history
- **Form State Management**: Automatic form data persistence with undo/redo
- **Cache Tracking**: Monitor and invalidate cache keys
- **Permissions & Roles**: Built-in user permission management

## Quick Start

### 1. Bootstrap Session

Call this at the start of your Streamlit app:

```python
import streamlit as st
from core import bootstrap_session

# Initialize or recover session
session = bootstrap_session()

st.write(f"Session ID: {session.session_id}")
st.write(f"Current Page: {session.current_page}")
```

### 2. Persist User Input

Use `persist_input()` for automatic widget state persistence:

```python
from core import persist_input

def on_name_change():
    persist_input("name", st.session_state.name, form_id="user_form")

st.text_input("Name", key="name", on_change=on_name_change)
```

### 3. Save Complete Forms

Save entire form data at once:

```python
from core import save_form

if st.button("Save"):
    form_data = {
        "name": st.session_state.name,
        "email": st.session_state.email,
        "phone": st.session_state.phone,
    }
    save_form("contact_form", form_data)
    st.success("Form saved!")
```

### 4. Navigate Between Pages

```python
from core import get_session_manager

manager = get_session_manager()

if st.button("Go to Profile"):
    manager.navigate_to("profile", {"user_id": "123"})
    st.rerun()

if st.button("Go Back"):
    if manager.go_back():
        st.rerun()
```

## Core Classes

### UserSession

Main session class with all state:

```python
from core import UserSession

session = UserSession(user_id="user123")

# Navigation
session.navigate_to("profile", {"id": "123"})
session.go_back()

# Forms
session.update_form_data("form1", "field", "value")
session.mark_form_saved("form1")

# Snapshots
snapshot = session.create_form_snapshot("form1", "Before changes")
session.restore_form_snapshot(snapshot.snapshot_id)

# Permissions
session.add_role("admin")
session.add_permission("write")
assert session.has_permission("write")

# Cache
session.add_cache_key("user_data_123")
session.invalidate_cache_keys("user_data")
```

### FormState

Individual form state:

```python
form_state = session.get_form_state("contact_form")

# Access data
name = form_state.data.get("name")

# Check if dirty
if form_state.is_dirty:
    st.warning("Unsaved changes!")

# Check errors
if form_state.errors:
    for field, errors in form_state.errors.items():
        st.error(f"{field}: {', '.join(errors)}")
```

## Session Persistence

### Automatic Persistence

Sessions are automatically persisted with debouncing (default 2 seconds):

```python
from core import persist_input

# This triggers debounced persistence
persist_input("field", "value", form_id="form1")
```

### Immediate Persistence

Force immediate write to database:

```python
from core import save_form

# Immediate write (no debouncing)
save_form("important_form", data, immediate=True)
```

### Manual Persistence

```python
from core.session_persistence import persist_session

session = get_current_session()
persist_session(session, immediate=True)
```

## Session Recovery

### Automatic Recovery

Sessions are automatically recovered on bootstrap:

```python
# If session_id exists in cookie/URL, it's automatically recovered
session = bootstrap_session(session_id=request_session_id)
```

### Manual Recovery

```python
from core.session_persistence import recover_session

session = recover_session("session-id-here")
if session:
    st.write("Session recovered!")
else:
    st.write("Session not found or expired")
```

### Recover User Sessions

```python
from core.session_persistence import get_persistence_engine

engine = get_persistence_engine()
sessions = engine.recover_user_sessions("user123")

st.write(f"Found {len(sessions)} sessions for user")
```

## Navigation Management

### Navigate to Page

```python
manager = get_session_manager()

# Simple navigation
manager.navigate_to("settings")

# With parameters
manager.navigate_to("profile", {"user_id": "123", "tab": "edit"})
```

### Navigation History

```python
session = get_current_session()

# View history
for entry in session.navigation_history:
    st.write(f"{entry.page} at {entry.timestamp}")

# Go back
if manager.go_back():
    st.rerun()
```

## Form Management

### Update Form Data

```python
session = get_current_session()

# Update individual field
session.update_form_data("contact_form", "name", "John")

# Check if dirty
if "contact_form" in session.dirty_forms:
    st.warning("Unsaved changes!")
```

### Form Snapshots (Undo/Redo)

```python
session = get_current_session()

# Create snapshot
snapshot = session.create_form_snapshot("form1", "Before major changes")

# Make changes
session.update_form_data("form1", "field", "new_value")

# Undo by restoring snapshot
session.restore_form_snapshot(snapshot.snapshot_id)
```

### Form Validation

```python
form_state = session.get_form_state("contact_form")

# Add errors
form_state.errors["email"] = ["Invalid email format"]
form_state.warnings["phone"] = ["Phone number not verified"]

# Display errors
if form_state.errors:
    for field, errors in form_state.errors.items():
        for error in errors:
            st.error(f"{field}: {error}")
```

## Cache Management

### Track Cache Keys

```python
session = get_current_session()

# Add cache key
session.add_cache_key("user_data_123")

# Add with dependencies
session.add_cache_key("profile_123", dependencies={"user_data_123"})
```

### Invalidate Cache

```python
manager = get_session_manager()

# Invalidate by pattern
manager.invalidate_cache("user_data")

# Invalidate all
manager.invalidate_cache()
```

## Permissions & Roles

### Manage Roles

```python
session = get_current_session()

# Add roles
session.add_role("user")
session.add_role("admin")

# Check roles
if session.has_role("admin"):
    st.write("Admin panel")

# Remove role
session.remove_role("admin")
```

### Manage Permissions

```python
session = get_current_session()

# Add permissions
session.add_permission("read")
session.add_permission("write")
session.add_permission("delete")

# Check permissions
if session.has_permission("delete"):
    if st.button("Delete"):
        delete_item()

# Remove permission
session.remove_permission("delete")
```

## Session Metrics

```python
session = get_current_session()

# View metrics
st.write(f"Page views: {session.metrics.page_views}")
st.write(f"Interactions: {session.metrics.interaction_count}")
st.write(f"Session duration: {session.metrics.session_duration}")
st.write(f"Last activity: {session.metrics.last_activity}")
```

## Session Cleanup

### Manual Cleanup

```python
manager = get_session_manager()
manager.cleanup_session()
```

### Automatic Cleanup

```python
from core.session_persistence import get_persistence_engine

engine = get_persistence_engine()

# Cleanup expired sessions
count = engine.cleanup_expired_sessions()
st.write(f"Cleaned up {count} expired sessions")

# Cleanup inactive sessions (7 days)
count = engine.cleanup_inactive_sessions(inactive_days=7)
st.write(f"Cleaned up {count} inactive sessions")
```

## Configuration

### Session Timeout

Configure in environment or config:

```bash
SESSION_TIMEOUT=86400  # 24 hours in seconds
```

### Debounce Delay

```python
from core.session_persistence import SessionPersistenceEngine

engine = SessionPersistenceEngine(
    debounce_delay=2.0,  # 2 seconds
    session_timeout=86400  # 24 hours
)
```

## Best Practices

1. **Always bootstrap session at app start**
   ```python
   session = bootstrap_session()
   ```

2. **Use persist_input for widgets**
   ```python
   def on_change():
       persist_input("field", st.session_state.field, form_id="form1")
   ```

3. **Save forms explicitly**
   ```python
   if st.button("Save"):
       save_form("form1", form_data)
   ```

4. **Create snapshots before major changes**
   ```python
   session.create_form_snapshot("form1", "Before bulk edit")
   ```

5. **Check permissions before actions**
   ```python
   if session.has_permission("delete"):
       # Allow delete
   ```

6. **Cleanup sessions periodically**
   ```python
   # Run as scheduled job
   engine.cleanup_expired_sessions()
   ```

## Troubleshooting

### Session Not Persisting

Check database connection:
```python
from core.database import get_db_manager

db = get_db_manager()
if db.health_check():
    st.success("Database OK")
else:
    st.error("Database connection failed")
```

### Session Not Recovering

Check session expiration:
```python
from core.session_persistence import recover_session

session = recover_session(session_id)
if session is None:
    st.warning("Session expired or not found")
```

### Debouncing Issues

Flush immediately for testing:
```python
from core.session_persistence import get_persistence_engine

engine = get_persistence_engine()
engine.flush_all()  # Force immediate write
```

## Examples

See `demo_session_system.py` for complete examples.
