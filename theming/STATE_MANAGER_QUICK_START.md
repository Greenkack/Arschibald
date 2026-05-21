# State Manager Quick Start

## Installation

No installation required - the State Manager is part of the theming module.

## 5-Minute Setup

### Step 1: Import

```python
from theming.state_manager import ThemeStateManager
```

### Step 2: Initialize

```python
import streamlit as st

# Initialize once
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )
```

### Step 3: Save Theme

```python
state_manager = st.session_state.state_manager
user_id = 'user123'

# Save theme preference
state_manager.save_theme_preference(user_id, 'shadcn-dark')
```

### Step 4: Load Theme

```python
# Load saved theme
theme = state_manager.load_theme_preference(user_id)

# Use with fallback
theme = state_manager.load_theme_preference(user_id) or 'shadcn-default'
```

### Step 5: State Recovery

```python
# Recover theme after browser refresh
if 'current_theme' not in st.session_state:
    recovered = state_manager.recover_state(user_id)
    st.session_state.current_theme = recovered or 'shadcn-default'
```

## Complete Example

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager

# Initialize (once)
if 'managers_initialized' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.state_manager = ThemeStateManager()
    st.session_state.managers_initialized = True

theme_manager = st.session_state.theme_manager
state_manager = st.session_state.state_manager

# Get user ID
user_id = st.session_state.get('user_id', 'default_user')

# Load or recover theme
if 'current_theme' not in st.session_state:
    theme = state_manager.recover_state(user_id)
    st.session_state.current_theme = theme or 'shadcn-default'

# Apply theme
theme_manager.set_theme(st.session_state.current_theme)

# Theme selector
with st.sidebar:
    themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean']
    selected = st.selectbox('Theme', themes)
    
    if selected != st.session_state.current_theme:
        st.session_state.current_theme = selected
        theme_manager.set_theme(selected)
        state_manager.save_theme_preference(user_id, selected)
        st.rerun()

# Your app content
st.title("My App")
st.write(f"Current theme: {st.session_state.current_theme}")
```

## Backend Options

### Session State (Default)
- ✅ Fastest
- ❌ Lost on refresh
- Use for: Active session

```python
ThemeStateManager(backends=['session'])
```

### Local Storage
- ✅ Persistent
- ✅ Tab sync
- Use for: Single device

```python
ThemeStateManager(backends=['session', 'local_storage'])
```

### Database
- ✅ Multi-device
- ✅ Centralized
- Use for: Multi-device sync

```python
ThemeStateManager(
    backends=['session', 'local_storage', 'database'],
    db_path='theming/theme_preferences.db'
)
```

## Common Patterns

### Save with Error Handling

```python
results = state_manager.save_theme_preference(user_id, theme)

if all(results.values()):
    st.success("✅ Saved to all backends")
elif any(results.values()):
    st.warning("⚠️ Saved to some backends")
else:
    st.error("❌ Failed to save")
```

### Load with Priority

```python
# Try database first, then local storage, then session
theme = state_manager.load_theme_preference(
    user_id,
    backends=['database', 'local_storage', 'session']
)
```

### Tab Synchronization

```python
# Enable tab sync
state_manager.enable_tab_sync()

# Theme changes in one tab will update all tabs
```

### Multi-User Support

```python
# Each user has their own theme
user1_theme = state_manager.load_theme_preference('user1')
user2_theme = state_manager.load_theme_preference('user2')
```

## Testing

Run the demo:

```bash
streamlit run demo_state_manager.py
```

Run tests:

```bash
pytest tests/test_state_manager.py -v
```

## Next Steps

1. ✅ Read [Full Reference](STATE_MANAGER_REFERENCE.md)
2. ✅ Check [Usage Examples](STATE_MANAGER_USAGE_EXAMPLE.md)
3. ✅ Review [Quick Reference](../docs/STATE_MANAGEMENT_QUICK_REFERENCE.md)
4. ✅ Integrate with your app

## Troubleshooting

### Theme not persistent?
```python
# Use local storage or database
ThemeStateManager(backends=['session', 'local_storage'])
```

### Tab sync not working?
```python
# Enable tab sync
state_manager.enable_tab_sync()
```

### Database errors?
```python
import os
db_path = 'theming/theme_preferences.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
```

## Support

- 📖 [Full Documentation](STATE_MANAGER_REFERENCE.md)
- 💡 [Usage Examples](STATE_MANAGER_USAGE_EXAMPLE.md)
- 🚀 [Quick Reference](../docs/STATE_MANAGEMENT_QUICK_REFERENCE.md)
