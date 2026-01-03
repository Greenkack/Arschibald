# State Manager Usage Examples

## Example 1: Basic Theme Persistence

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager

# Initialize managers
if 'managers_initialized' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage']
    )
    st.session_state.managers_initialized = True

theme_manager = st.session_state.theme_manager
state_manager = st.session_state.state_manager

# Get user ID (from login system or use default)
user_id = st.session_state.get('user_id', 'default_user')

# Load saved theme preference
if 'current_theme' not in st.session_state:
    saved_theme = state_manager.load_theme_preference(user_id)
    st.session_state.current_theme = saved_theme or 'shadcn-default'

# Apply current theme
theme_manager.set_theme(st.session_state.current_theme)

# Theme selector in sidebar
with st.sidebar:
    st.subheader("🎨 Theme Settings")
    
    available_themes = [
        'shadcn-default',
        'shadcn-dark',
        'shadcn-ocean',
        'shadcn-forest',
        'shadcn-sunset'
    ]
    
    selected_theme = st.selectbox(
        'Select Theme',
        available_themes,
        index=available_themes.index(st.session_state.current_theme)
    )
    
    # Save and apply new theme
    if selected_theme != st.session_state.current_theme:
        st.session_state.current_theme = selected_theme
        theme_manager.set_theme(selected_theme)
        
        # Save to all backends
        results = state_manager.save_theme_preference(user_id, selected_theme)
        
        # Show save status
        success_count = sum(results.values())
        if success_count == len(results):
            st.success(f"✅ Theme saved successfully")
        elif success_count > 0:
            st.warning(f"⚠️ Theme saved to {success_count}/{len(results)} backends")
        else:
            st.error("❌ Failed to save theme")
        
        st.rerun()

# Main content
st.title("My App")
st.write(f"Current theme: {st.session_state.current_theme}")
```

## Example 2: Multi-Device Sync with Database

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager

# Initialize with database backend for multi-device sync
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database'],
        db_path='theming/theme_preferences.db'
    )

state_manager = st.session_state.state_manager

# User authentication (example)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None

# Login form
if not st.session_state.authenticated:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit and username:
            # Simulate authentication
            st.session_state.authenticated = True
            st.session_state.user_id = username
            
            # Load user's theme preference from database
            saved_theme = state_manager.load_theme_preference(
                username,
                backends=['database', 'local_storage', 'session']
            )
            
            if saved_theme:
                st.session_state.current_theme = saved_theme
                st.success(f"✅ Welcome back! Your theme '{saved_theme}' has been restored.")
            else:
                st.session_state.current_theme = 'shadcn-default'
                st.info("👋 Welcome! Using default theme.")
            
            st.rerun()
else:
    # User is logged in
    user_id = st.session_state.user_id
    
    st.title(f"Welcome, {user_id}!")
    
    # Theme selector
    with st.sidebar:
        st.subheader("Theme Settings")
        
        themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean']
        current = st.session_state.get('current_theme', 'shadcn-default')
        
        new_theme = st.selectbox('Theme', themes, index=themes.index(current))
        
        if new_theme != current:
            st.session_state.current_theme = new_theme
            
            # Save to all backends (especially database for multi-device)
            results = state_manager.save_theme_preference(user_id, new_theme)
            
            if results.get('database'):
                st.success("✅ Theme saved across all devices")
            else:
                st.warning("⚠️ Theme saved locally only")
            
            st.rerun()
        
        # Show sync status
        if st.button("🔄 Sync Theme"):
            state_manager.sync_across_backends(user_id, 'database')
            st.success("✅ Theme synced across all backends")
    
    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.rerun()
```

## Example 3: State Recovery After Browser Refresh

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager

# Initialize managers
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()

if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )

theme_manager = st.session_state.theme_manager
state_manager = st.session_state.state_manager

# Get user ID
user_id = st.session_state.get('user_id', 'default_user')

# State Recovery Logic
if 'theme_recovered' not in st.session_state:
    st.session_state.theme_recovered = False
    
    # Try to recover theme from persistent backends
    with st.spinner("🔄 Restoring your theme..."):
        recovered_theme = state_manager.recover_state(user_id)
        
        if recovered_theme:
            st.session_state.current_theme = recovered_theme
            st.session_state.theme_recovered = True
            
            # Show recovery notification
            st.success(f"✅ Theme restored: {recovered_theme}")
            
            # Apply recovered theme
            theme_manager.set_theme(recovered_theme)
        else:
            # No saved theme found, use default
            st.session_state.current_theme = 'shadcn-default'
            st.info("👋 Using default theme")
            theme_manager.set_theme('shadcn-default')

# Rest of the app
st.title("State Recovery Demo")
st.write(f"Current theme: {st.session_state.current_theme}")

# Theme selector
with st.sidebar:
    themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean']
    new_theme = st.selectbox(
        'Theme',
        themes,
        index=themes.index(st.session_state.current_theme)
    )
    
    if new_theme != st.session_state.current_theme:
        st.session_state.current_theme = new_theme
        theme_manager.set_theme(new_theme)
        state_manager.save_theme_preference(user_id, new_theme)
        st.rerun()

# Test recovery button
if st.button("🔄 Test Recovery (Refresh Page)"):
    st.info("💡 Refresh the page to test state recovery")
```

## Example 4: Tab Synchronization

```python
import streamlit as st
from theming.state_manager import ThemeStateManager

# Initialize with tab sync enabled
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage']
    )
    # Enable tab synchronization
    st.session_state.state_manager.enable_tab_sync()

state_manager = st.session_state.state_manager
user_id = 'demo_user'

# Load current theme
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = state_manager.load_theme_preference(user_id) or 'shadcn-default'

st.title("Tab Synchronization Demo")

st.info("""
📱 **Try this:**
1. Open this app in multiple browser tabs
2. Change the theme in one tab
3. Watch other tabs update automatically!
""")

# Theme selector
with st.sidebar:
    st.subheader("🎨 Theme")
    
    themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean', 'shadcn-forest']
    
    selected = st.radio(
        'Select Theme',
        themes,
        index=themes.index(st.session_state.current_theme)
    )
    
    if selected != st.session_state.current_theme:
        st.session_state.current_theme = selected
        
        # Save to local storage (triggers sync)
        state_manager.save_theme_preference(
            user_id,
            selected,
            backends=['local_storage']
        )
        
        st.success(f"✅ Theme changed to {selected}")
        st.info("🔄 Other tabs will update automatically")
        st.rerun()

# Display current theme
st.markdown(f"""
### Current Theme
**{st.session_state.current_theme}**

Open this page in another tab and change the theme there.
This tab will automatically reload with the new theme!
""")
```

## Example 5: Backend Status Monitoring

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
import pandas as pd

# Initialize
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )

state_manager = st.session_state.state_manager

st.title("State Management Dashboard")

# Backend Status
st.subheader("📊 Backend Status")

status = state_manager.get_backend_status()

status_data = []
for backend_name, info in status.items():
    status_data.append({
        'Backend': backend_name,
        'Type': info['type'],
        'Status': '✅ Available' if info['available'] else '❌ Unavailable'
    })

df = pd.DataFrame(status_data)
st.dataframe(df, use_container_width=True)

# Test Operations
st.subheader("🧪 Test Operations")

col1, col2 = st.columns(2)

with col1:
    test_user = st.text_input("User ID", value="test_user")
    test_theme = st.selectbox("Theme", ['shadcn-default', 'shadcn-dark', 'shadcn-ocean'])

with col2:
    backends_to_test = st.multiselect(
        "Backends to Test",
        ['session', 'local_storage', 'database'],
        default=['session', 'local_storage']
    )

# Save Test
if st.button("💾 Test Save"):
    with st.spinner("Saving..."):
        results = state_manager.save_theme_preference(
            test_user,
            test_theme,
            backends=backends_to_test
        )
        
        st.write("**Results:**")
        for backend, success in results.items():
            if success:
                st.success(f"✅ {backend}: Saved successfully")
            else:
                st.error(f"❌ {backend}: Save failed")

# Load Test
if st.button("📂 Test Load"):
    with st.spinner("Loading..."):
        loaded_theme = state_manager.load_theme_preference(
            test_user,
            backends=backends_to_test
        )
        
        if loaded_theme:
            st.success(f"✅ Loaded theme: {loaded_theme}")
        else:
            st.warning("⚠️ No theme found")

# Recovery Test
if st.button("🔄 Test Recovery"):
    with st.spinner("Recovering..."):
        recovered_theme = state_manager.recover_state(test_user)
        
        if recovered_theme:
            st.success(f"✅ Recovered theme: {recovered_theme}")
        else:
            st.warning("⚠️ No theme to recover")

# Sync Test
if st.button("🔄 Test Sync"):
    if len(backends_to_test) < 2:
        st.warning("⚠️ Select at least 2 backends to test sync")
    else:
        with st.spinner("Syncing..."):
            source = backends_to_test[0]
            results = state_manager.sync_across_backends(test_user, source)
            
            st.write(f"**Synced from {source}:**")
            for backend, success in results.items():
                if success:
                    st.success(f"✅ {backend}: Synced")
                else:
                    st.error(f"❌ {backend}: Sync failed")

# Database Viewer (if database backend is active)
if 'database' in state_manager.backends:
    st.subheader("🗄️ Database Contents")
    
    db_backend = state_manager.backends['database']
    all_prefs = db_backend.get_all_preferences()
    
    if all_prefs:
        df_prefs = pd.DataFrame(all_prefs)
        st.dataframe(df_prefs, use_container_width=True)
    else:
        st.info("No preferences in database")
```

## Example 6: Error Handling and Fallbacks

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize with error handling
try:
    if 'state_manager' not in st.session_state:
        st.session_state.state_manager = ThemeStateManager(
            backends=['session', 'local_storage', 'database']
        )
        st.session_state.theme_manager = ThemeManager()
except Exception as e:
    logger.error(f"Failed to initialize managers: {e}")
    st.error(f"❌ Initialization error: {e}")
    st.stop()

state_manager = st.session_state.state_manager
theme_manager = st.session_state.theme_manager

# Get user ID
user_id = st.session_state.get('user_id', 'default_user')

# Load theme with error handling
def load_theme_safe(user_id: str) -> str:
    """Safely load theme with fallbacks"""
    try:
        # Try to load from state manager
        theme = state_manager.load_theme_preference(user_id)
        if theme:
            logger.info(f"Loaded theme: {theme}")
            return theme
    except Exception as e:
        logger.error(f"Failed to load theme: {e}")
        st.warning(f"⚠️ Could not load saved theme: {e}")
    
    # Fallback 1: Try recovery
    try:
        theme = state_manager.recover_state(user_id)
        if theme:
            logger.info(f"Recovered theme: {theme}")
            st.info(f"🔄 Theme recovered: {theme}")
            return theme
    except Exception as e:
        logger.error(f"Failed to recover theme: {e}")
    
    # Fallback 2: Use default
    logger.info("Using default theme")
    return 'shadcn-default'

# Save theme with error handling
def save_theme_safe(user_id: str, theme_name: str) -> bool:
    """Safely save theme with error handling"""
    try:
        results = state_manager.save_theme_preference(user_id, theme_name)
        
        # Check if at least one backend succeeded
        if any(results.values()):
            success_count = sum(results.values())
            total_count = len(results)
            
            if success_count == total_count:
                st.success(f"✅ Theme saved to all backends")
            else:
                st.warning(f"⚠️ Theme saved to {success_count}/{total_count} backends")
            
            return True
        else:
            st.error("❌ Failed to save theme to any backend")
            return False
            
    except Exception as e:
        logger.error(f"Failed to save theme: {e}")
        st.error(f"❌ Save error: {e}")
        
        # Fallback: Save to session state only
        try:
            st.session_state.current_theme = theme_name
            st.warning("⚠️ Theme saved to session only (not persistent)")
            return True
        except Exception as e2:
            logger.error(f"Fallback save failed: {e2}")
            return False

# Initialize theme
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = load_theme_safe(user_id)

# Apply theme
try:
    theme_manager.set_theme(st.session_state.current_theme)
except Exception as e:
    logger.error(f"Failed to apply theme: {e}")
    st.error(f"❌ Could not apply theme: {e}")

# UI
st.title("Error Handling Demo")

with st.sidebar:
    st.subheader("🎨 Theme Settings")
    
    themes = ['shadcn-default', 'shadcn-dark', 'shadcn-ocean']
    
    selected = st.selectbox(
        'Theme',
        themes,
        index=themes.index(st.session_state.current_theme)
    )
    
    if selected != st.session_state.current_theme:
        if save_theme_safe(user_id, selected):
            st.session_state.current_theme = selected
            try:
                theme_manager.set_theme(selected)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Could not apply theme: {e}")

# Show current state
st.write(f"**Current Theme:** {st.session_state.current_theme}")

# Backend status
with st.expander("🔍 Backend Status"):
    try:
        status = state_manager.get_backend_status()
        for backend, info in status.items():
            st.write(f"**{backend}:** {info['type']}")
    except Exception as e:
        st.error(f"Could not get backend status: {e}")
```

## Example 7: Performance Monitoring

```python
import streamlit as st
from theming.state_manager import ThemeStateManager
import time
from datetime import datetime

# Initialize
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )
    st.session_state.performance_metrics = []

state_manager = st.session_state.state_manager

def measure_operation(operation_name, func, *args, **kwargs):
    """Measure operation performance"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = (time.perf_counter() - start) * 1000  # ms
    
    st.session_state.performance_metrics.append({
        'operation': operation_name,
        'duration_ms': duration,
        'timestamp': datetime.now()
    })
    
    return result, duration

st.title("Performance Monitoring")

# Test operations
user_id = 'perf_test_user'
theme = 'shadcn-dark'

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Test Save"):
        _, duration = measure_operation(
            'save',
            state_manager.save_theme_preference,
            user_id, theme
        )
        st.metric("Save Time", f"{duration:.2f}ms")

with col2:
    if st.button("Test Load"):
        _, duration = measure_operation(
            'load',
            state_manager.load_theme_preference,
            user_id
        )
        st.metric("Load Time", f"{duration:.2f}ms")

with col3:
    if st.button("Test Recovery"):
        _, duration = measure_operation(
            'recovery',
            state_manager.recover_state,
            user_id
        )
        st.metric("Recovery Time", f"{duration:.2f}ms")

# Performance metrics
if st.session_state.performance_metrics:
    st.subheader("📊 Performance Metrics")
    
    import pandas as pd
    df = pd.DataFrame(st.session_state.performance_metrics)
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_duration = df['duration_ms'].mean()
        st.metric("Average", f"{avg_duration:.2f}ms")
    
    with col2:
        min_duration = df['duration_ms'].min()
        st.metric("Minimum", f"{min_duration:.2f}ms")
    
    with col3:
        max_duration = df['duration_ms'].max()
        st.metric("Maximum", f"{max_duration:.2f}ms")
    
    # Detailed metrics
    st.dataframe(df, use_container_width=True)
    
    # Clear metrics
    if st.button("Clear Metrics"):
        st.session_state.performance_metrics = []
        st.rerun()
```

## See Also

- [State Manager Reference](STATE_MANAGER_REFERENCE.md)
- [Quick Reference](../docs/STATE_MANAGEMENT_QUICK_REFERENCE.md)
- [Theme Manager](THEME_MANAGER_REFERENCE.md)
