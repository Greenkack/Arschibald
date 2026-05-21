# State Management Quick Reference

## Quick Start

```python
from theming.state_manager import ThemeStateManager

# 1. Initialisierung
state_manager = ThemeStateManager(
    backends=['session', 'local_storage', 'database']
)

# 2. Theme speichern
state_manager.save_theme_preference('user123', 'shadcn-dark')

# 3. Theme laden
theme = state_manager.load_theme_preference('user123')

# 4. State Recovery
recovered = state_manager.recover_state('user123')
```

## Common Tasks

### Save Theme

```python
# Einfach
state_manager.save_theme_preference('user123', 'shadcn-dark')

# Mit spezifischen Backends
state_manager.save_theme_preference(
    'user123', 
    'shadcn-dark',
    backends=['session', 'local_storage']
)

# Prüfe Erfolg
results = state_manager.save_theme_preference('user123', 'shadcn-dark')
if all(results.values()):
    print("✅ Saved to all backends")
```

### Load Theme

```python
# Standard
theme = state_manager.load_theme_preference('user123')

# Mit Fallback
theme = state_manager.load_theme_preference('user123') or 'shadcn-default'

# Mit custom Backend-Reihenfolge
theme = state_manager.load_theme_preference(
    'user123',
    backends=['database', 'local_storage', 'session']
)
```

### State Recovery

```python
# Bei Browser-Refresh
if 'current_theme' not in st.session_state:
    recovered = state_manager.recover_state('user123')
    st.session_state.current_theme = recovered or 'shadcn-default'
```

### Tab Synchronization

```python
# Aktiviere Tab-Sync
state_manager.enable_tab_sync()

# Theme-Änderungen werden automatisch in anderen Tabs angezeigt
```

## Backend Comparison

| Feature | Session | LocalStorage | Database |
|---------|---------|--------------|----------|
| Speed | 🟢 Fastest | 🟡 Fast | 🔴 Slow |
| Persistent | ❌ No | ✅ Yes | ✅ Yes |
| Multi-Tab | ❌ No | ✅ Yes | ✅ Yes |
| Multi-Device | ❌ No | ❌ No | ✅ Yes |
| Setup | 🟢 None | 🟢 None | 🟡 DB File |

## Backend Selection Guide

### Use Session State when:
- ✅ Need maximum performance
- ✅ Theme only for current session
- ✅ No persistence required

### Use Local Storage when:
- ✅ Need persistence across refreshes
- ✅ Want tab synchronization
- ✅ Single-device usage

### Use Database when:
- ✅ Need multi-device sync
- ✅ Want centralized storage
- ✅ Need user history/analytics

## Integration Patterns

### With Theme Manager

```python
from theming.theme_manager import ThemeManager
from theming.state_manager import ThemeStateManager

theme_manager = ThemeManager()
state_manager = ThemeStateManager()

# Load saved theme
saved_theme = state_manager.load_theme_preference('user123')
if saved_theme:
    theme_manager.set_theme(saved_theme)

# On theme change
def on_theme_change(new_theme):
    theme_manager.set_theme(new_theme)
    state_manager.save_theme_preference('user123', new_theme)
```

### With Streamlit

```python
import streamlit as st

# Initialize once
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager()

# Get user ID
user_id = st.session_state.get('user_id', 'default')

# Load theme
current_theme = st.session_state.state_manager.load_theme_preference(user_id)

# Theme selector
new_theme = st.selectbox('Theme', ['shadcn-default', 'shadcn-dark'])

# Save on change
if new_theme != current_theme:
    st.session_state.state_manager.save_theme_preference(user_id, new_theme)
    st.rerun()
```

## Error Handling

```python
try:
    results = state_manager.save_theme_preference('user123', 'shadcn-dark')
    
    if not any(results.values()):
        st.error("Failed to save to any backend")
    elif all(results.values()):
        st.success("Saved to all backends")
    else:
        st.warning("Saved to some backends")
        
except Exception as e:
    st.error(f"Error: {e}")
    # Fallback
    st.session_state.current_theme = 'shadcn-dark'
```

## Troubleshooting

### Theme not persistent
```python
# ❌ Wrong - only session
state_manager = ThemeStateManager(backends=['session'])

# ✅ Correct - with persistence
state_manager = ThemeStateManager(backends=['session', 'local_storage'])
```

### Tab sync not working
```python
# Enable tab sync
state_manager.enable_tab_sync()

# Ensure local storage backend is active
assert 'local_storage' in state_manager.backend_names
```

### Database errors
```python
import os

# Ensure directory exists
db_path = 'theming/theme_preferences.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Use absolute path
db_path = os.path.abspath(db_path)
state_manager = ThemeStateManager(backends=['database'], db_path=db_path)
```

## Performance Tips

1. **Cache in Session State**
   ```python
   # Fast access
   theme = st.session_state.get('current_theme')
   ```

2. **Lazy Database Writes**
   ```python
   # Only save to DB on important events
   if user_logged_in:
       state_manager.save_theme_preference(user_id, theme, backends=['database'])
   ```

3. **Use Appropriate Backend**
   ```python
   # For active session: session state
   # For persistence: local storage
   # For multi-device: database
   ```

## Best Practices

✅ **DO:**
- Use multiple backends for redundancy
- Implement fallbacks
- Enable logging for debugging
- Test state recovery
- Validate user IDs

❌ **DON'T:**
- Rely on single backend
- Ignore save failures
- Skip error handling
- Store sensitive data
- Use without fallback theme

## Code Snippets

### Complete Setup

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.state_manager import ThemeStateManager

# Initialize (once)
if 'theme_system' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )
    st.session_state.state_manager.enable_tab_sync()

# Get managers
theme_manager = st.session_state.theme_manager
state_manager = st.session_state.state_manager

# Get user
user_id = st.session_state.get('user_id', 'default_user')

# Load or recover theme
if 'current_theme' not in st.session_state:
    theme = state_manager.recover_state(user_id)
    st.session_state.current_theme = theme or 'shadcn-default'

# Apply theme
theme_manager.set_theme(st.session_state.current_theme)

# Theme selector
with st.sidebar:
    themes = theme_manager.get_available_themes()
    selected = st.selectbox(
        'Theme',
        themes,
        index=themes.index(st.session_state.current_theme)
    )
    
    if selected != st.session_state.current_theme:
        st.session_state.current_theme = selected
        theme_manager.set_theme(selected)
        state_manager.save_theme_preference(user_id, selected)
        st.rerun()
```

### Minimal Setup

```python
from theming.state_manager import ThemeStateManager

# Simple setup
state_manager = ThemeStateManager()

# Save
state_manager.save_theme_preference('user123', 'shadcn-dark')

# Load
theme = state_manager.load_theme_preference('user123') or 'shadcn-default'
```

## API Cheatsheet

```python
# Initialize
manager = ThemeStateManager(backends=['session', 'local_storage', 'database'])

# Save
manager.save_theme_preference(user_id, theme_name, backends=None)

# Load
manager.load_theme_preference(user_id, backends=None)

# Delete
manager.delete_theme_preference(user_id, backends=None)

# Sync
manager.sync_across_backends(user_id, source_backend)

# Recovery
manager.recover_state(user_id)

# Status
manager.get_backend_status()

# Tab Sync
manager.enable_tab_sync()
```

## See Also

- [Full Reference](../theming/STATE_MANAGER_REFERENCE.md)
- [Theme Manager](../theming/THEME_MANAGER_REFERENCE.md)
- [Usage Examples](../theming/STATE_MANAGER_USAGE_EXAMPLE.md)
