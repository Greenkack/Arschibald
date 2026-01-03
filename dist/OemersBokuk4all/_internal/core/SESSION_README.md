# Enhanced Session Management System

Complete session management with state persistence, recovery, and debounced database writes for maximally robust Streamlit applications.

## Overview

The Enhanced Session Management System provides:

- **UserSession**: Comprehensive session state with navigation history, form states, permissions
- **Session Persistence**: Debounced database writes to prevent excessive I/O
- **Session Recovery**: Complete state restoration after browser refresh
- **Form Management**: Form state tracking with dirty/clean status
- **Cache Tracking**: Cache key management with dependencies
- **Conflict Resolution**: Automatic conflict resolution for concurrent modifications
- **Metrics Tracking**: Page views, interaction counts, session duration

## Core Components

### UserSession

The main session dataclass that holds all user state:

```python
from core.session import UserSession

# Create new session
session = UserSession(user_id="user123")

# Add navigation
session.add_navigation("dashboard", {"view": "overview"})

# Manage forms
form_state = session.get_form_state("contact_form")
form_state.data = {"name": "John", "email": "john@example.com"}
session.mark_form_dirty("contact_form")

# Track permissions
session.permissions.add("read")
session.permissions.add("write")

# Check permissions
if session.has_permission("write"):
    # Allow write operation
    pass
```

### Session Persistence

Automatic debounced persistence to database:

```python
from core.session import persist_input, save_session

# Immediate session_state update, debounced DB write
persist_input("user_name", "John Doe")

# Manual save (immediate)
save_session(session, immediate=True)

# Manual save (debounced)
save_session(session, immediate=False)
```

### Session Recovery

Restore complete session state after browser refresh:

```python
from core.session import bootstrap_session, recover_session

# Bootstrap session (creates new or restores existing)
session = bootstrap_session(
    session_id="existing_session_id",  # Optional
    user_id="user123",                  # Optional
    restore_from_db=True                # Try to restore from DB
)

# Explicit recovery
recovered = recover_session("session_id_123")
if recovered:
    print(f"Session recovered: {recovered.session_id}")
```

## Key Features

### 1. Navigation History

Track user navigation with parameters:

```python
session = UserSession()

# Add navigation entries
session.add_navigation("home")
session.add_navigation("products", {"category": "electronics"})
session.add_navigation("cart", {"items": 3})

# Access history
for entry in session.navigation_history:
    print(f"{entry.page}: {entry.params} at {entry.timestamp}")

# Page view metrics
print(session.page_views)  # {'home': 1, 'products': 1, 'cart': 1}
```

### 2. Form State Management

Complete form state with validation and history:

```python
# Get or create form state
form_state = session.get_form_state("registration_form")

# Update form data
form_state.data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "********"
}

# Add validation errors
form_state.errors = {
    "email": ["Email already exists"]
}

# Mark as dirty (unsaved changes)
session.mark_form_dirty("registration_form")

# Check dirty status
if "registration_form" in session.dirty_forms:
    print("Form has unsaved changes")

# Mark as clean (saved)
session.mark_form_clean("registration_form")
print(f"Form saved at: {form_state.last_saved}")
```

### 3. Form Snapshots (Undo/Redo)

Create snapshots for undo/redo functionality:

```python
from core.session import FormSnapshot
import uuid
from datetime import datetime

# Create snapshot
snapshot = FormSnapshot(
    snapshot_id=str(uuid.uuid4()),
    form_id="editor_form",
    data=form_state.data.copy(),
    timestamp=datetime.now(),
    description="Before major edit"
)

# Add to form state
form_state.snapshots.append(snapshot)

# Restore from snapshot
if form_state.snapshots:
    snapshot = form_state.snapshots[-1]
    form_state.data = snapshot.data.copy()
```

### 4. Cache Key Tracking

Track cache keys with dependencies:

```python
# Add cache key with dependencies
session.add_cache_key("user_data", {"user_id"})
session.add_cache_key("user_posts", {"user_id", "posts"})

# Check tracked keys
print(session.cache_keys)  # {'user_data', 'user_posts'}

# Check dependencies
print(session.cache_dependencies["user_data"])  # {'user_id'}

# Remove cache key
session.remove_cache_key("user_data")
```

### 5. Permissions & Roles

Role-based access control:

```python
# Create session with roles and permissions
session = UserSession(
    user_id="user123",
    roles={"admin", "editor"},
    permissions={"read", "write", "delete"}
)

# Check permissions
if session.has_permission("delete"):
    # Allow delete operation
    pass

# Check roles
if session.has_role("admin"):
    # Show admin panel
    pass
```

### 6. Session Metrics

Track user activity and engagement:

```python
# Metrics are automatically tracked
session.add_navigation("home")
session.add_navigation("products")
session.add_navigation("home")

# View metrics
print(f"Total interactions: {session.interaction_count}")
print(f"Page views: {session.page_views}")
print(f"Session duration: {session.session_duration}")
print(f"Last activity: {session.last_activity}")
```

## Database Persistence

### Session Repository

The `SessionRepository` handles all database operations:

```python
from core.session_repository import SessionRepository, init_session_tables

# Initialize database tables
init_session_tables()

# Create repository
repo = SessionRepository()

# Save session
repo.save_session(session)

# Get session
session_data = repo.get_session("session_id_123")
if session_data:
    session = UserSession.from_dict(session_data)

# Get session by user
session_data = repo.get_session_by_user("user123")

# Delete session
repo.delete_session("session_id_123")

# Cleanup expired sessions
count = repo.cleanup_expired_sessions(max_age_hours=24)
print(f"Cleaned up {count} expired sessions")

# Get active session count
active_count = repo.get_active_session_count(active_threshold_minutes=30)
print(f"{active_count} active sessions")
```

### Conflict Resolution

Handle concurrent session modifications:

```python
# Last write wins strategy
resolved = repo.resolve_conflict(
    session_id="session_123",
    local_session=local_session,
    strategy='last_write_wins'
)

# Merge strategy
resolved = repo.resolve_conflict(
    session_id="session_123",
    local_session=local_session,
    strategy='merge'
)
```

## Debounced Persistence

The system uses debouncing to prevent excessive database writes:

```python
from core.session import SessionPersistence

# Create persistence engine (500ms debounce)
persistence = SessionPersistence(debounce_ms=500)

# Schedule save (will be debounced)
def save_fn(sess):
    repo.save_session(sess)

persistence.schedule_save(session.session_id, session, save_fn)

# Multiple rapid saves will be coalesced
for i in range(10):
    persistence.schedule_save(session.session_id, session, save_fn)
    # Only one actual save will occur after 500ms

# Force immediate flush
persistence.flush(session.session_id)
```

## Streamlit Integration

### Basic Usage

```python
import streamlit as st
from core.session import bootstrap_session, persist_input

# Bootstrap session (automatically uses st.session_state)
session = bootstrap_session()

# Persist input immediately to session_state and DB
name = st.text_input("Name", key="user_name")
persist_input("user_name", name)

# Access session
st.write(f"Session ID: {session.session_id}")
st.write(f"Interactions: {session.interaction_count}")
```

### Navigation Tracking

```python
import streamlit as st
from core.session import get_current_session

# Get current session
session = get_current_session()

# Track page navigation
if st.button("Go to Dashboard"):
    session.add_navigation("dashboard", {"view": "overview"})
    st.rerun()

# Show navigation history
st.write("Navigation History:")
for entry in session.navigation_history[-5:]:
    st.write(f"- {entry.page} ({entry.timestamp})")
```

### Form State Management

```python
import streamlit as st
from core.session import get_current_session, save_session

session = get_current_session()

# Get form state
form_state = session.get_form_state("contact_form")

# Form inputs
name = st.text_input("Name", value=form_state.data.get("name", ""))
email = st.text_input("Email", value=form_state.data.get("email", ""))

# Update form data
if name or email:
    form_state.data["name"] = name
    form_state.data["email"] = email
    session.mark_form_dirty("contact_form")

# Save button
if st.button("Save"):
    # Validate and save
    if not email:
        form_state.errors["email"] = ["Email is required"]
    else:
        session.mark_form_clean("contact_form")
        save_session(session, immediate=True)
        st.success("Form saved!")

# Show errors
if form_state.errors:
    for field, errors in form_state.errors.items():
        for error in errors:
            st.error(f"{field}: {error}")
```

## Session Lifecycle

### Complete Workflow

```python
from core.session import (
    bootstrap_session,
    persist_input,
    save_session,
    recover_session,
    cleanup_expired_sessions
)
from core.session_repository import init_session_tables

# 1. Initialize database
init_session_tables()

# 2. Bootstrap session (first visit or recovery)
session = bootstrap_session(user_id="user123", restore_from_db=True)

# 3. User interacts with application
session.add_navigation("dashboard")
persist_input("current_view", "overview")

# 4. User fills form
form_state = session.get_form_state("settings_form")
form_state.data = {"theme": "dark", "language": "en"}
session.mark_form_dirty("settings_form")

# 5. Auto-save (debounced)
save_session(session, immediate=False)

# 6. Browser refresh - session automatically recovered
# (bootstrap_session handles this)

# 7. Periodic cleanup (run as scheduled job)
cleanup_expired_sessions(max_age_hours=24)
```

## Serialization

Sessions can be serialized to dict or JSON:

```python
# To dictionary
session_dict = session.to_dict()

# From dictionary
restored_session = UserSession.from_dict(session_dict)

# To JSON
session_json = session.to_json()

# From JSON
restored_session = UserSession.from_json(session_json)
```

## Configuration

Session behavior can be configured:

```python
# Create session with custom settings
session = UserSession(
    max_history_size=50,  # Limit navigation history
    theme="dark",          # User preference
    language="en",         # User language
    timezone="UTC"         # User timezone
)

# Configure form state
form_state = session.get_form_state("my_form")
form_state.auto_save = True           # Enable auto-save
form_state.save_debounce_ms = 1000    # 1 second debounce
form_state.max_snapshots = 20         # Limit undo history
```

## Best Practices

### 1. Always Bootstrap Sessions

```python
# Good: Use bootstrap_session
session = bootstrap_session(user_id="user123")

# Avoid: Creating sessions manually
# session = UserSession()  # Won't restore from DB
```

### 2. Use persist_input for Widgets

```python
# Good: Immediate session_state + debounced DB
name = st.text_input("Name", key="user_name")
persist_input("user_name", name)

# Avoid: Manual session_state management
# st.session_state["user_name"] = name  # No DB persistence
```

### 3. Mark Forms Dirty/Clean

```python
# Good: Track form state
if form_data_changed:
    session.mark_form_dirty("my_form")

if form_saved:
    session.mark_form_clean("my_form")

# Show indicator
if "my_form" in session.dirty_forms:
    st.warning("Unsaved changes")
```

### 4. Cleanup Expired Sessions

```python
# Run as scheduled job (e.g., daily)
from core.session import cleanup_expired_sessions

count = cleanup_expired_sessions(max_age_hours=24)
logger.info(f"Cleaned up {count} expired sessions")
```

### 5. Handle Conflicts

```python
# Use conflict resolution when needed
from core.session_repository import SessionRepository

repo = SessionRepository()
resolved = repo.resolve_conflict(
    session_id=session.session_id,
    local_session=local_session,
    strategy='last_write_wins'  # or 'merge'
)
```

## Testing

Run the test suite:

```bash
# Test session management
pytest core/test_session.py -v

# Test session repository
pytest core/test_session_repository.py -v

# Run all tests
pytest core/test_session*.py -v
```

## Examples

See `core/example_session_usage.py` for comprehensive examples:

```bash
python -m core.example_session_usage
```

## API Reference

### UserSession

- `add_navigation(page, params)` - Add navigation entry
- `get_form_state(form_id)` - Get or create form state
- `mark_form_dirty(form_id)` - Mark form as having unsaved changes
- `mark_form_clean(form_id)` - Mark form as saved
- `add_cache_key(key, dependencies)` - Track cache key
- `remove_cache_key(key)` - Remove cache key
- `has_permission(permission)` - Check permission
- `has_role(role)` - Check role
- `to_dict()` - Serialize to dictionary
- `from_dict(data)` - Deserialize from dictionary
- `to_json()` - Serialize to JSON
- `from_json(json_str)` - Deserialize from JSON

### Functions

- `bootstrap_session(session_id, user_id, restore_from_db)` - Initialize or restore session
- `get_current_session()` - Get current session
- `persist_input(key, val)` - Persist input with debouncing
- `save_session(session, immediate)` - Save session to database
- `recover_session(session_id)` - Recover session from database
- `cleanup_expired_sessions(max_age_hours)` - Cleanup old sessions

### SessionRepository

- `save_session(session)` - Save or update session
- `get_session(session_id)` - Get session by ID
- `get_session_by_user(user_id)` - Get user's most recent session
- `delete_session(session_id)` - Delete session
- `cleanup_expired_sessions(max_age_hours)` - Cleanup expired sessions
- `get_active_session_count(active_threshold_minutes)` - Count active sessions
- `get_all_sessions(limit, offset, user_id)` - Get all sessions with pagination
- `update_last_activity(session_id)` - Update activity timestamp
- `resolve_conflict(session_id, local_session, strategy)` - Resolve conflicts

## Requirements Met

This implementation satisfies the following requirements:

- **1.2**: Widget state management with stable keys
- **1.3**: Immediate session_state updates with debounced DB writes
- **1.5**: Form state with undo/redo functionality
- **2.1**: Automatic session persistence
- **2.6**: Session recovery after browser refresh
- **6.3**: Permission-based access control
- **6.4**: Role management
- **13.1**: Core classes (UserSession, FormState, etc.)

## Next Steps

After implementing session management, the next tasks are:

1. **Container-Based Navigation** (Task 3) - Router with page swapping
2. **Controlled Widget System** (Task 4) - Widget wrappers with auto-persistence
3. **Form State Management** (Task 5) - Enhanced form handling with undo/redo

## Support

For issues or questions, refer to:
- Design document: `.kiro/specs/streamlit-robustness-enhancement/design.md`
- Requirements: `.kiro/specs/streamlit-robustness-enhancement/requirements.md`
- Test files: `core/test_session*.py`
