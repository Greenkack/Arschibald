"""
Demo: Theme System Error Handling

Demonstrates the complete error handling system including:
- Exception hierarchy
- Error handler with fallback mechanisms
- Error dashboard
- User notifications
- Automatic recovery
"""

import streamlit as st
from datetime import datetime
import time

# Import error handling components
from theming.theme_errors import (
    ThemeError,
    ThemeLoadError,
    ThemeValidationError,
    ThemeNotFoundError,
    CSSGenerationError,
    CSSInjectionError,
    ComponentRenderError,
    TokenNotFoundError
)
from theming.error_handler import ErrorHandler, get_error_handler
from theming.error_dashboard import (
    render_error_dashboard,
    render_error_summary_widget,
    render_inline_error_notification,
    render_error_toast
)


def demo_exception_hierarchy():
    """Demonstrate exception hierarchy"""
    st.header("1⃣ Exception Hierarchy")
    
    st.markdown("""
    The error handling system provides a comprehensive exception hierarchy
    for all theme-related errors.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Exceptions")
        st.code("""
ThemeError (base)
 ThemeLoadError
 ThemeValidationError
 ThemeNotFoundError
 CSSGenerationError
 CSSInjectionError
 ComponentRenderError
 TokenNotFoundError
 ThemeFileError
 ThemeCacheError
 ThemeStateError
        """, language="text")
    
    with col2:
        st.subheader("Try It")
        
        exception_type = st.selectbox(
            "Select exception to raise",
            [
                "ThemeLoadError",
                "ThemeValidationError",
                "ThemeNotFoundError",
                "CSSGenerationError",
                "ComponentRenderError"
            ]
        )
        
        if st.button("Raise Exception", key="raise_exception"):
            handler = get_error_handler()
            
            if exception_type == "ThemeLoadError":
                error = ThemeLoadError(
                    theme_name="custom-theme",
                    reason="File not found",
                    details={'path': '/themes/custom-theme.json'}
                )
            elif exception_type == "ThemeValidationError":
                error = ThemeValidationError(
                    theme_name="invalid-theme",
                    errors=["Invalid color format", "Missing font-family"],
                    details={'schema_version': '1.0'}
                )
            elif exception_type == "ThemeNotFoundError":
                error = ThemeNotFoundError(
                    theme_name="missing-theme",
                    available_themes=["default", "dark", "ocean"]
                )
            elif exception_type == "CSSGenerationError":
                error = CSSGenerationError(
                    theme_name="broken-theme",
                    reason="Invalid token reference",
                    details={'token': 'colors.invalid'}
                )
            else:  # ComponentRenderError
                error = ComponentRenderError(
                    component_name="Card",
                    reason="Missing required prop: title",
                    details={'props': {'content': 'test'}}
                )
            
            handler.handle_error(error, notify_user=True)
            st.success(f" {exception_type} raised and handled!")


def demo_error_handler():
    """Demonstrate error handler functionality"""
    st.header("2⃣ Error Handler")
    
    st.markdown("""
    The ErrorHandler provides centralized error handling with:
    - Automatic logging
    - User notifications
    - Fallback mechanisms
    - Recovery attempts
    """)
    
    handler = get_error_handler()
    
    tab1, tab2, tab3 = st.tabs([
        "Basic Handling",
        "Fallback Mechanisms",
        "Error Reports"
    ])
    
    with tab1:
        st.subheader("Basic Error Handling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.code("""
handler = get_error_handler()

try:
    # Your code
    raise ValueError("Test error")
except Exception as e:
    handler.handle_error(
        error=e,
        context={'operation': 'test'},
        notify_user=True,
        severity='error'
    )
            """, language="python")
        
        with col2:
            severity = st.selectbox(
                "Select severity",
                ["error", "warning", "info"]
            )
            
            if st.button("Simulate Error", key="basic_error"):
                error = ValueError("This is a test error")
                handler.handle_error(
                    error=error,
                    context={
                        'operation': 'demo',
                        'timestamp': datetime.now().isoformat()
                    },
                    notify_user=True,
                    severity=severity
                )
    
    with tab2:
        st.subheader("Fallback Mechanisms")
        
        st.markdown("""
        The error handler supports automatic fallback for critical operations:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.code("""
def load_fallback_theme():
    return default_theme

try:
    theme = load_theme("custom")
except Exception as e:
    theme = handler.handle_theme_load_error(
        theme_name="custom",
        error=e,
        fallback_callback=load_fallback_theme
    )
            """, language="python")
        
        with col2:
            if st.button("Test Theme Load Fallback", key="theme_fallback"):
                def load_fallback():
                    return {"name": "fallback-theme", "type": "default"}
                
                error = ThemeLoadError("custom-theme", "File not found")
                result = handler.handle_theme_load_error(
                    theme_name="custom-theme",
                    error=error,
                    fallback_callback=load_fallback
                )
                
                st.success(" Fallback executed!")
                st.json(result)
            
            if st.button("Test Component Fallback", key="component_fallback"):
                def render_fallback():
                    st.info(" Fallback component rendered")
                    return "fallback"
                
                error = ComponentRenderError("Card", "Missing props")
                result = handler.handle_component_error(
                    component_name="Card",
                    error=error,
                    fallback_callback=render_fallback
                )
                
                st.success(" Component fallback executed!")
    
    with tab3:
        st.subheader("Error Reports")
        
        report = handler.get_error_report()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Errors", report['total_errors'])
        
        with col2:
            st.metric("In History", report['errors_in_history'])
        
        with col3:
            st.metric("Error Types", len(report['error_types']))
        
        if report['error_types']:
            st.markdown("**Error Types:**")
            st.json(report['error_types'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Report", key="export_report"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"logs/error_report_{timestamp}.json"
                handler.export_error_report(filepath)
                st.success(f" Report exported to {filepath}")
        
        with col2:
            if st.button("Clear History", key="clear_history"):
                handler.clear_history()
                st.success(" Error history cleared!")
                st.rerun()


def demo_automatic_recovery():
    """Demonstrate automatic recovery"""
    st.header("3⃣ Automatic Recovery")
    
    st.markdown("""
    The error handler automatically attempts recovery with retry limits.
    """)
    
    handler = get_error_handler()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        
        st.code(f"""
Max Recovery Attempts: {handler.max_recovery_attempts}
Current Attempts: {len(handler.recovery_attempts)}
        """, language="text")
        
        if handler.recovery_attempts:
            st.markdown("**Active Recovery Operations:**")
            for op, count in handler.recovery_attempts.items():
                st.markdown(f"- `{op}`: {count} attempt(s)")
    
    with col2:
        st.subheader("Test Recovery")
        
        if st.button("Simulate Recovery", key="test_recovery"):
            attempt_count = [0]
            
            def recovery_function():
                attempt_count[0] += 1
                if attempt_count[0] < 2:
                    raise ValueError("Still failing")
                return "Success!"
            
            with st.spinner("Attempting recovery..."):
                try:
                    result = handler._attempt_recovery(
                        "demo_recovery",
                        recovery_function
                    )
                    st.success(f" Recovered after {attempt_count[0]} attempt(s)!")
                    st.info(f"Result: {result}")
                except Exception as e:
                    st.error(f" Recovery failed: {e}")


def demo_user_notifications():
    """Demonstrate user notifications"""
    st.header("4⃣ User Notifications")
    
    st.markdown("""
    Multiple notification styles for different use cases.
    """)
    
    tab1, tab2, tab3 = st.tabs([
        "Inline Notifications",
        "Toast Notifications",
        "Summary Widget"
    ])
    
    with tab1:
        st.subheader("Inline Error Notifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Show Error", key="inline_error"):
                render_inline_error_notification(
                    error_type="ThemeLoadError",
                    message="Failed to load theme 'custom-theme'",
                    details={
                        'reason': 'File not found',
                        'path': '/themes/custom-theme.json'
                    },
                    severity="error"
                )
            
            if st.button("Show Warning", key="inline_warning"):
                render_inline_error_notification(
                    error_type="ComponentWarning",
                    message="Component rendered with default props",
                    details={'component': 'Card', 'missing_props': ['title']},
                    severity="warning"
                )
        
        with col2:
            if st.button("Show Info", key="inline_info"):
                render_inline_error_notification(
                    error_type="ThemeSwitch",
                    message="Theme switched successfully",
                    details={'from': 'dark', 'to': 'light'},
                    severity="info"
                )
    
    with tab2:
        st.subheader("Toast Notifications")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Error Toast", key="toast_error"):
                render_error_toast("An error occurred!", "error")
        
        with col2:
            if st.button("Warning Toast", key="toast_warning"):
                render_error_toast("This is a warning", "warning")
        
        with col3:
            if st.button("Info Toast", key="toast_info"):
                render_error_toast("Information message", "info")
        
        with col4:
            if st.button("Success Toast", key="toast_success"):
                render_error_toast("Operation successful!", "success")
    
    with tab3:
        st.subheader("Error Summary Widget")
        
        st.markdown("Compact widget for sidebar or dashboard:")
        
        render_error_summary_widget()


def demo_error_dashboard():
    """Demonstrate error dashboard"""
    st.header("5⃣ Error Dashboard")
    
    st.markdown("""
    Comprehensive error monitoring and reporting dashboard.
    """)
    
    if st.button("Open Full Dashboard", key="open_dashboard"):
        st.session_state['show_full_dashboard'] = True
    
    if st.session_state.get('show_full_dashboard', False):
        st.markdown("---")
        render_error_dashboard()
        
        if st.button("Close Dashboard", key="close_dashboard"):
            st.session_state['show_full_dashboard'] = False
            st.rerun()


def demo_integration_examples():
    """Show integration examples"""
    st.header("6⃣ Integration Examples")
    
    st.markdown("""
    Examples of integrating error handling into your components.
    """)
    
    tab1, tab2, tab3 = st.tabs([
        "Theme Manager",
        "Component",
        "CSS Generator"
    ])
    
    with tab1:
        st.subheader("Theme Manager Integration")
        
        st.code("""
from theming.error_handler import get_error_handler

class ThemeManager:
    def __init__(self):
        self.error_handler = get_error_handler()
    
    def load_theme(self, theme_name: str):
        try:
            theme = self._load_theme_file(theme_name)
            return theme
        except Exception as e:
            return self.error_handler.handle_theme_load_error(
                theme_name=theme_name,
                error=e,
                fallback_callback=self._get_fallback_theme
            )
    
    def _get_fallback_theme(self):
        return self.themes.get('shadcn-default')
        """, language="python")
    
    with tab2:
        st.subheader("Component Integration")
        
        st.code("""
from components.shadcn_base import ShadcnComponent
from theming.error_handler import get_error_handler

class Card(ShadcnComponent):
    def render(self, **kwargs):
        handler = get_error_handler()
        
        try:
            self._render_card(**kwargs)
        except Exception as e:
            handler.handle_component_error(
                component_name="Card",
                error=e,
                fallback_callback=lambda: st.container()
            )
        """, language="python")
    
    with tab3:
        st.subheader("CSS Generator Integration")
        
        st.code("""
from theming.css_generator import CSSGenerator
from theming.error_handler import get_error_handler

class CSSGenerator:
    def generate_full_css(self):
        handler = get_error_handler()
        
        try:
            css = self._generate_css()
            return css
        except Exception as e:
            return handler.handle_css_generation_error(
                theme_name=self.theme.name,
                error=e,
                fallback_callback=self._generate_minimal_css
            )
    
    def _generate_minimal_css(self):
        return "/* Minimal fallback CSS */"
        """, language="python")


def main():
    """Main demo application"""
    st.set_page_config(
        page_title="Error Handling Demo",
        page_icon="",
        layout="wide"
    )
    
    st.title(" Theme System Error Handling Demo")
    
    st.markdown("""
    This demo showcases the comprehensive error handling system for the shadcn/ui theme system.
    
    **Features:**
    - Custom exception hierarchy
    - Centralized error handler
    - Automatic fallback mechanisms
    - Error recovery with retry limits
    - User notifications (inline, toast, dashboard)
    - Error reporting and analytics
    """)
    
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        page = st.radio(
            "Select Demo",
            [
                "Exception Hierarchy",
                "Error Handler",
                "Automatic Recovery",
                "User Notifications",
                "Error Dashboard",
                "Integration Examples"
            ]
        )
        
        st.markdown("---")
        
        st.subheader("Quick Actions")
        
        if st.button("Generate Test Errors", key="generate_errors"):
            handler = get_error_handler()
            
            # Generate various test errors
            errors = [
                ThemeLoadError("test-1", "Test error 1"),
                CSSGenerationError("test-2", "Test error 2"),
                ComponentRenderError("TestComponent", "Test error 3"),
                ThemeValidationError("test-4", ["Error 1", "Error 2"])
            ]
            
            for error in errors:
                handler.handle_error(error, notify_user=False)
            
            st.success(f" Generated {len(errors)} test errors")
        
        st.markdown("---")
        
        # Show error summary
        st.subheader("Error Summary")
        render_error_summary_widget()
    
    # Main content
    if page == "Exception Hierarchy":
        demo_exception_hierarchy()
    elif page == "Error Handler":
        demo_error_handler()
    elif page == "Automatic Recovery":
        demo_automatic_recovery()
    elif page == "User Notifications":
        demo_user_notifications()
    elif page == "Error Dashboard":
        demo_error_dashboard()
    elif page == "Integration Examples":
        demo_integration_examples()
    
    # Footer
    st.markdown("---")
    st.caption(
        "Error Handling System Demo | "
        f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
