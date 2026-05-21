"""
gui_integration_example.py

Example of how to integrate the migrated shadcn/ui modules into gui.py.
This shows the recommended pattern for gradual rollout with a feature flag.
"""

import streamlit as st

# Import original modules
from solar_calculator import render_solar_calculator
from crm import render_crm
from admin_panel import render_admin_panel

# Import migrated shadcn/ui modules
from solar_calculator_shadcn import render_solar_calculator_with_shadcn
from crm_shadcn import render_crm_with_shadcn
from admin_panel_shadcn import render_admin_panel_with_shadcn

# Import migration helpers
from utils.shadcn_migration_helpers import inject_shadcn_styles


def initialize_shadcn_ui():
    """
    Initialize shadcn/ui system.
    Call this once at the beginning of your app.
    """
    # Initialize feature flag if not set
    if 'enable_shadcn_ui' not in st.session_state:
        st.session_state.enable_shadcn_ui = True  # Enable by default
    
    # Inject styles if enabled
    if st.session_state.enable_shadcn_ui:
        inject_shadcn_styles()


def render_page_with_shadcn_support(
    page_name: str,
    original_render_func,
    shadcn_render_func,
    *args,
    **kwargs
):
    """
    Render a page with shadcn/ui support and automatic fallback.
    
    Args:
        page_name: Name of the page (for logging)
        original_render_func: Original render function
        shadcn_render_func: shadcn/ui render function
        *args: Arguments to pass to render function
        **kwargs: Keyword arguments to pass to render function
    """
    use_shadcn = st.session_state.get('enable_shadcn_ui', True)
    
    if use_shadcn:
        try:
            # Try to render with shadcn/ui
            shadcn_render_func(*args, **kwargs)
        except Exception as e:
            # Fallback to original on error
            st.error(f"Error rendering {page_name} with shadcn/ui: {e}")
            st.warning("Falling back to original rendering...")
            original_render_func(*args, **kwargs)
    else:
        # Use original rendering
        original_render_func(*args, **kwargs)


# Example integration in gui.py main function
def main():
    """
    Main application function with shadcn/ui integration.
    """
    
    # Initialize shadcn/ui
    initialize_shadcn_ui()
    
    # Sidebar - Feature flag toggle (optional, for testing)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎨 UI Settings")
        
        enable_shadcn = st.checkbox(
            "Enable Modern UI (shadcn/ui)",
            value=st.session_state.get('enable_shadcn_ui', True),
            key="shadcn_ui_toggle",
            help="Toggle between modern shadcn/ui design and classic Streamlit design"
        )
        
        if enable_shadcn != st.session_state.enable_shadcn_ui:
            st.session_state.enable_shadcn_ui = enable_shadcn
            st.rerun()
    
    # Get current page from session state or navigation
    current_page = st.session_state.get('current_page', 'home')
    
    # Example: Dummy functions for demonstration
    def get_texts():
        return {}
    
    def get_db_connection():
        return None
    
    def load_admin_setting(key, default=None):
        return default
    
    def save_admin_setting(key, value):
        return True
    
    # Page routing with shadcn/ui support
    if current_page == 'solar_calculator':
        render_page_with_shadcn_support(
            'Solar Calculator',
            render_solar_calculator,
            render_solar_calculator_with_shadcn,
            get_texts(),
            module_name='solar_calculator'
        )
    
    elif current_page == 'crm':
        render_page_with_shadcn_support(
            'CRM',
            render_crm,
            render_crm_with_shadcn,
            get_texts(),
            get_db_connection,
            show_header=True
        )
    
    elif current_page == 'admin':
        render_page_with_shadcn_support(
            'Admin Panel',
            render_admin_panel,
            render_admin_panel_with_shadcn,
            get_texts(),
            get_db_connection,
            load_admin_setting,
            save_admin_setting
        )
    
    else:
        st.title("Welcome")
        st.write("Select a page from the sidebar")


# Alternative: Direct integration without feature flag
def main_direct():
    """
    Direct integration - always use shadcn/ui.
    """
    
    # Initialize shadcn/ui
    inject_shadcn_styles()
    
    # Get current page
    current_page = st.session_state.get('current_page', 'home')
    
    # Example: Dummy functions
    def get_texts():
        return {}
    
    def get_db_connection():
        return None
    
    def load_admin_setting(key, default=None):
        return default
    
    def save_admin_setting(key, value):
        return True
    
    # Page routing - always use shadcn/ui versions
    if current_page == 'solar_calculator':
        render_solar_calculator_with_shadcn(
            get_texts(),
            module_name='solar_calculator'
        )
    
    elif current_page == 'crm':
        render_crm_with_shadcn(
            get_texts(),
            get_db_connection,
            show_header=True
        )
    
    elif current_page == 'admin':
        render_admin_panel_with_shadcn(
            get_texts(),
            get_db_connection,
            load_admin_setting,
            save_admin_setting
        )
    
    else:
        st.title("Welcome")
        st.write("Select a page from the sidebar")


# Alternative: Gradual rollout with user preference
def main_with_user_preference():
    """
    Integration with user preference storage.
    """
    
    # Load user preference from database or session
    user_id = st.session_state.get('user_id')
    
    if user_id:
        # Load user preference from database
        # user_prefs = load_user_preferences(user_id)
        # enable_shadcn = user_prefs.get('enable_shadcn_ui', True)
        enable_shadcn = True  # Default for demo
    else:
        # Default for anonymous users
        enable_shadcn = True
    
    # Store in session state
    if 'enable_shadcn_ui' not in st.session_state:
        st.session_state.enable_shadcn_ui = enable_shadcn
    
    # Initialize shadcn/ui if enabled
    if st.session_state.enable_shadcn_ui:
        inject_shadcn_styles()
    
    # Sidebar - User preference toggle
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Preferences")
        
        new_preference = st.checkbox(
            "Modern UI Design",
            value=st.session_state.enable_shadcn_ui,
            key="ui_preference",
            help="Enable modern shadcn/ui design"
        )
        
        if new_preference != st.session_state.enable_shadcn_ui:
            st.session_state.enable_shadcn_ui = new_preference
            
            # Save user preference to database
            if user_id:
                # save_user_preference(user_id, 'enable_shadcn_ui', new_preference)
                pass
            
            st.rerun()
    
    # Rest of the app...
    # (Same as main() function)


# Alternative: A/B testing integration
def main_with_ab_testing():
    """
    Integration with A/B testing framework.
    """
    
    # Determine which variant to show
    user_id = st.session_state.get('user_id')
    
    if user_id:
        # Use A/B testing framework to determine variant
        # variant = ab_test_framework.get_variant(user_id, 'shadcn_ui_test')
        variant = 'B'  # 'A' = original, 'B' = shadcn/ui
    else:
        variant = 'B'  # Default to shadcn/ui for anonymous users
    
    # Set feature flag based on variant
    st.session_state.enable_shadcn_ui = (variant == 'B')
    
    # Initialize shadcn/ui if enabled
    if st.session_state.enable_shadcn_ui:
        inject_shadcn_styles()
    
    # Track variant exposure
    # ab_test_framework.track_exposure(user_id, 'shadcn_ui_test', variant)
    
    # Rest of the app...
    # (Same as main() function)


if __name__ == "__main__":
    # Choose your integration approach:
    
    # Option 1: With feature flag (recommended for gradual rollout)
    main()
    
    # Option 2: Direct integration (always use shadcn/ui)
    # main_direct()
    
    # Option 3: With user preference
    # main_with_user_preference()
    
    # Option 4: With A/B testing
    # main_with_ab_testing()
