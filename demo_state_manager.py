"""
Demo: State Management System

Demonstriert die Verwendung des State Management Systems für Theme-Präferenzen.
"""

import streamlit as st
from theming.state_manager import ThemeStateManager
from theming.theme_manager import ThemeManager
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="State Management Demo",
    page_
    layout="wide"
)

# Initialize managers
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()

if 'state_manager' not in st.session_state:
    st.session_state.state_manager = ThemeStateManager(
        backends=['session', 'local_storage', 'database']
    )
    # Enable tab synchronization
    st.session_state.state_manager.enable_tab_sync()

theme_manager = st.session_state.theme_manager
state_manager = st.session_state.state_manager

# Get user ID (simulated)
if 'user_id' not in st.session_state:
    st.session_state.user_id = 'demo_user'

user_id = st.session_state.user_id

# State Recovery
if 'theme_recovered' not in st.session_state:
    st.session_state.theme_recovered = False
    
    with st.spinner(" Restoring theme..."):
        recovered_theme = state_manager.recover_state(user_id)
        
        if recovered_theme:
            st.session_state.current_theme = recovered_theme
            st.session_state.theme_recovered = True
            st.success(f" Theme restored: {recovered_theme}")
        else:
            st.session_state.current_theme = 'shadcn-default'
            st.info(" Using default theme")

# Apply theme
theme_manager.set_theme(st.session_state.current_theme)

# Header
st.title(" State Management System Demo")
st.markdown("---")

# Sidebar - Theme Selector
with st.sidebar:
    st.header(" Theme Settings")
    
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
        index=available_themes.index(st.session_state.current_theme),
        key='theme_selector'
    )
    
    if selected_theme != st.session_state.current_theme:
        st.session_state.current_theme = selected_theme
        theme_manager.set_theme(selected_theme)
        
        # Save to all backends
        results = state_manager.save_theme_preference(user_id, selected_theme)
        
        # Show results
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            st.success(f" Saved to all {total_count} backends")
        elif success_count > 0:
            st.warning(f" Saved to {success_count}/{total_count} backends")
        else:
            st.error(" Failed to save")
        
        st.rerun()
    
    st.markdown("---")
    
    # User Settings
    st.subheader(" User Settings")
    new_user_id = st.text_input("User ID", value=user_id)
    
    if new_user_id != user_id:
        st.session_state.user_id = new_user_id
        # Load theme for new user
        loaded_theme = state_manager.load_theme_preference(new_user_id)
        if loaded_theme:
            st.session_state.current_theme = loaded_theme
            st.success(f" Loaded theme: {loaded_theme}")
        st.rerun()

# Main Content
tab1, tab2, tab3, tab4 = st.tabs([
    " Overview",
    " Test Operations",
    " Backend Status",
    " Performance"
])

with tab1:
    st.header("Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current User", user_id)
    
    with col2:
        st.metric("Current Theme", st.session_state.current_theme)
    
    with col3:
        st.metric("Active Backends", len(state_manager.backends))
    
    st.markdown("---")
    
    # Features
    st.subheader(" Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **State Management:**
        -  Multi-backend support
        -  Automatic fallbacks
        -  State recovery
        -  Tab synchronization
        """)
    
    with col2:
        st.markdown("""
        **Backends:**
        - 🟢 Session State (fast)
        - 🟡 Local Storage (persistent)
        -  Database (multi-device)
        """)
    
    st.markdown("---")
    
    # Instructions
    st.subheader(" How to Use")
    
    st.markdown("""
    1. **Select a theme** from the sidebar
    2. **Refresh the page** to test state recovery
    3. **Open in multiple tabs** to test synchronization
    4. **Change user ID** to test multi-user support
    5. **Check the Test Operations tab** for detailed testing
    """)
    
    # Info boxes
    st.info("""
     **Tip:** Open this page in multiple browser tabs and change the theme in one tab.
    Watch as other tabs automatically update!
    """)
    
    st.success("""
     **State Recovery:** Your theme preference is automatically saved and restored
    when you refresh the page or return later.
    """)

with tab2:
    st.header(" Test Operations")
    
    # Test configuration
    col1, col2 = st.columns(2)
    
    with col1:
        test_user = st.text_input("Test User ID", value="test_user")
        test_theme = st.selectbox(
            "Test Theme",
            available_themes,
            index=0
        )
    
    with col2:
        test_backends = st.multiselect(
            "Backends to Test",
            ['session', 'local_storage', 'database'],
            default=['session', 'local_storage']
        )
    
    st.markdown("---")
    
    # Test buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(" Test Save", use_container_width=True):
            with st.spinner("Saving..."):
                import time
                start = time.perf_counter()
                
                results = state_manager.save_theme_preference(
                    test_user,
                    test_theme,
                    backends=test_backends
                )
                
                duration = (time.perf_counter() - start) * 1000
                
                st.write("**Results:**")
                for backend, success in results.items():
                    if success:
                        st.success(f" {backend}")
                    else:
                        st.error(f" {backend}")
                
                st.info(f"⏱ Duration: {duration:.2f}ms")
    
    with col2:
        if st.button(" Test Load", use_container_width=True):
            with st.spinner("Loading..."):
                import time
                start = time.perf_counter()
                
                loaded = state_manager.load_theme_preference(
                    test_user,
                    backends=test_backends
                )
                
                duration = (time.perf_counter() - start) * 1000
                
                if loaded:
                    st.success(f" Loaded: {loaded}")
                else:
                    st.warning(" No theme found")
                
                st.info(f"⏱ Duration: {duration:.2f}ms")
    
    with col3:
        if st.button(" Test Recovery", use_container_width=True):
            with st.spinner("Recovering..."):
                import time
                start = time.perf_counter()
                
                recovered = state_manager.recover_state(test_user)
                
                duration = (time.perf_counter() - start) * 1000
                
                if recovered:
                    st.success(f" Recovered: {recovered}")
                else:
                    st.warning(" No theme to recover")
                
                st.info(f"⏱ Duration: {duration:.2f}ms")
    
    with col4:
        if st.button(" Test Delete", use_container_width=True):
            with st.spinner("Deleting..."):
                results = state_manager.delete_theme_preference(
                    test_user,
                    backends=test_backends
                )
                
                st.write("**Results:**")
                for backend, success in results.items():
                    if success:
                        st.success(f" {backend}")
                    else:
                        st.error(f" {backend}")
    
    st.markdown("---")
    
    # Sync test
    st.subheader(" Backend Synchronization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sync_source = st.selectbox(
            "Source Backend",
            test_backends if test_backends else ['session']
        )
    
    with col2:
        if st.button(" Sync Across Backends", use_container_width=True):
            if len(test_backends) < 2:
                st.warning(" Select at least 2 backends")
            else:
                with st.spinner("Syncing..."):
                    results = state_manager.sync_across_backends(
                        test_user,
                        sync_source
                    )
                    
                    st.write(f"**Synced from {sync_source}:**")
                    for backend, success in results.items():
                        if success:
                            st.success(f" {backend}")
                        else:
                            st.error(f" {backend}")

with tab3:
    st.header(" Backend Status")
    
    # Backend status
    status = state_manager.get_backend_status()
    
    status_data = []
    for backend_name, info in status.items():
        status_data.append({
            'Backend': backend_name,
            'Type': info['type'],
            'Status': ' Available' if info['available'] else ' Unavailable'
        })
    
    df_status = pd.DataFrame(status_data)
    st.dataframe(df_status, use_container_width=True)
    
    st.markdown("---")
    
    # Backend details
    for backend_name, backend in state_manager.backends.items():
        with st.expander(f" {backend_name.upper()} Backend"):
            st.write(f"**Type:** {type(backend).__name__}")
            
            # Test existence
            exists = backend.exists(user_id)
            st.write(f"**Has preference for {user_id}:** {' Yes' if exists else ' No'}")
            
            # Load current value
            if exists:
                value = backend.load(user_id)
                st.write(f"**Current value:** {value}")
    
    st.markdown("---")
    
    # Database contents (if available)
    if 'database' in state_manager.backends:
        st.subheader(" Database Contents")
        
        db_backend = state_manager.backends['database']
        all_prefs = db_backend.get_all_preferences()
        
        if all_prefs:
            df_prefs = pd.DataFrame(all_prefs)
            st.dataframe(df_prefs, use_container_width=True)
            
            # Export option
            if st.button(" Export to CSV"):
                csv = df_prefs.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "theme_preferences.csv",
                    "text/csv"
                )
        else:
            st.info("No preferences in database")

with tab4:
    st.header(" Performance Metrics")
    
    # Initialize metrics storage
    if 'perf_metrics' not in st.session_state:
        st.session_state.perf_metrics = []
    
    # Run performance test
    if st.button(" Run Performance Test"):
        import time
        
        test_user = "perf_test_user"
        test_theme = "shadcn-dark"
        
        metrics = []
        
        with st.spinner("Running tests..."):
            # Test save
            for backend in ['session', 'local_storage', 'database']:
                start = time.perf_counter()
                state_manager.save_theme_preference(
                    test_user,
                    test_theme,
                    backends=[backend]
                )
                duration = (time.perf_counter() - start) * 1000
                
                metrics.append({
                    'operation': 'save',
                    'backend': backend,
                    'duration_ms': duration,
                    'timestamp': datetime.now()
                })
            
            # Test load
            for backend in ['session', 'local_storage', 'database']:
                start = time.perf_counter()
                state_manager.load_theme_preference(
                    test_user,
                    backends=[backend]
                )
                duration = (time.perf_counter() - start) * 1000
                
                metrics.append({
                    'operation': 'load',
                    'backend': backend,
                    'duration_ms': duration,
                    'timestamp': datetime.now()
                })
            
            # Test recovery
            start = time.perf_counter()
            state_manager.recover_state(test_user)
            duration = (time.perf_counter() - start) * 1000
            
            metrics.append({
                'operation': 'recovery',
                'backend': 'all',
                'duration_ms': duration,
                'timestamp': datetime.now()
            })
        
        st.session_state.perf_metrics.extend(metrics)
        st.success(" Performance test completed")
    
    # Display metrics
    if st.session_state.perf_metrics:
        df_metrics = pd.DataFrame(st.session_state.perf_metrics)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg = df_metrics['duration_ms'].mean()
            st.metric("Average", f"{avg:.2f}ms")
        
        with col2:
            min_val = df_metrics['duration_ms'].min()
            st.metric("Minimum", f"{min_val:.2f}ms")
        
        with col3:
            max_val = df_metrics['duration_ms'].max()
            st.metric("Maximum", f"{max_val:.2f}ms")
        
        st.markdown("---")
        
        # Detailed metrics
        st.subheader("Detailed Metrics")
        st.dataframe(df_metrics, use_container_width=True)
        
        # Clear button
        if st.button(" Clear Metrics"):
            st.session_state.perf_metrics = []
            st.rerun()
    else:
        st.info("No performance metrics yet. Run a test to see results.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>State Management System Demo | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
