"""
Error Report Dashboard

Provides a Streamlit UI for viewing error reports and statistics.
"""

from typing import Optional
from datetime import datetime, timedelta
import json

try:
    import streamlit as st
    import plotly.graph_objects as go
    import plotly.express as px
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .error_handler import ErrorHandler, get_error_handler


def render_error_dashboard(error_handler: Optional[ErrorHandler] = None):
    """
    Render error dashboard in Streamlit.
    
    Args:
        error_handler: ErrorHandler instance. If None, uses global handler.
    """
    if not STREAMLIT_AVAILABLE:
        print("Streamlit not available. Cannot render dashboard.")
        return
    
    handler = error_handler or get_error_handler()
    
    st.title("🔍 Theme System Error Dashboard")
    st.markdown("---")
    
    # Get error report
    report = handler.get_error_report()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Errors",
            value=report['total_errors'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="In History",
            value=report['errors_in_history'],
            delta=None
        )
    
    with col3:
        error_types_count = len(report['error_types'])
        st.metric(
            label="Error Types",
            value=error_types_count,
            delta=None
        )
    
    with col4:
        recovery_count = sum(report['recovery_attempts'].values())
        st.metric(
            label="Recovery Attempts",
            value=recovery_count,
            delta=None
        )
    
    st.markdown("---")
    
    # Error types breakdown
    if report['error_types']:
        st.subheader("📊 Error Types Breakdown")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(report['error_types'].keys()),
                values=list(report['error_types'].values()),
                hole=0.3
            )])
            fig.update_layout(
                title="Error Distribution",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Table
            st.markdown("**Error Counts:**")
            for error_type, count in sorted(
                report['error_types'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                st.markdown(f"- **{error_type}**: {count}")
    
    st.markdown("---")
    
    # Recent errors
    if report['recent_errors']:
        st.subheader("🕐 Recent Errors")
        
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            filter_type = st.multiselect(
                "Filter by error type",
                options=list(report['error_types'].keys()),
                default=[]
            )
        with col2:
            show_stack_trace = st.checkbox("Show stack traces", value=False)
        
        # Display errors
        for i, error in enumerate(reversed(report['recent_errors'])):
            # Apply filter
            if filter_type and error['error_type'] not in filter_type:
                continue
            
            with st.expander(
                f"❌ {error['error_type']}: {error['error_message'][:80]}...",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Type:** `{error['error_type']}`")
                    st.markdown(f"**Time:** {error['timestamp']}")
                
                with col2:
                    if error['context']:
                        st.markdown("**Context:**")
                        st.json(error['context'])
                
                st.markdown(f"**Message:** {error['error_message']}")
                
                if error['details']:
                    st.markdown("**Details:**")
                    st.json(error['details'])
                
                if show_stack_trace and error['stack_trace']:
                    st.markdown("**Stack Trace:**")
                    st.code(error['stack_trace'], language='python')
    else:
        st.info("✅ No errors recorded yet!")
    
    st.markdown("---")
    
    # Recovery attempts
    if report['recovery_attempts']:
        st.subheader("🔄 Recovery Attempts")
        
        recovery_data = [
            {'Operation': op, 'Attempts': count}
            for op, count in report['recovery_attempts'].items()
        ]
        
        st.dataframe(
            recovery_data,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Actions
    st.subheader("⚙️ Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Error History", type="secondary"):
            handler.clear_history()
            st.success("Error history cleared!")
            st.rerun()
    
    with col2:
        if st.button("💾 Export Report", type="secondary"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/error_report_{timestamp}.json"
            handler.export_error_report(filepath)
            st.success(f"Report exported to {filepath}")
    
    with col3:
        if st.button("🔄 Refresh", type="primary"):
            st.rerun()
    
    # Report metadata
    st.markdown("---")
    st.caption(f"Report generated at: {report['generated_at']}")


def render_error_summary_widget(error_handler: Optional[ErrorHandler] = None):
    """
    Render compact error summary widget.
    
    Args:
        error_handler: ErrorHandler instance. If None, uses global handler.
    """
    if not STREAMLIT_AVAILABLE:
        return
    
    handler = error_handler or get_error_handler()
    report = handler.get_error_report()
    
    if report['total_errors'] == 0:
        st.success("✅ No errors")
        return
    
    # Show warning if there are errors
    severity_counts = handler.get_error_count_by_severity()
    
    if severity_counts['critical'] > 0:
        st.error(
            f"❌ {severity_counts['critical']} critical error(s) | "
            f"⚠️ {severity_counts['warning']} warning(s)"
        )
    elif severity_counts['warning'] > 0:
        st.warning(f"⚠️ {severity_counts['warning']} warning(s)")
    else:
        st.info(f"ℹ️ {report['total_errors']} info message(s)")
    
    # Show link to full dashboard
    if st.button("View Error Dashboard", key="view_error_dashboard"):
        st.session_state['show_error_dashboard'] = True


def render_inline_error_notification(
    error_type: str,
    message: str,
    details: Optional[dict] = None,
    severity: str = "error"
):
    """
    Render inline error notification.
    
    Args:
        error_type: Type of error
        message: Error message
        details: Optional error details
        severity: Severity level (error, warning, info)
    """
    if not STREAMLIT_AVAILABLE:
        return
    
    # Choose icon and color based on severity
    if severity == "error":
        icon = "❌"
        st.error(f"{icon} **{error_type}**: {message}")
    elif severity == "warning":
        icon = "⚠️"
        st.warning(f"{icon} **{error_type}**: {message}")
    else:
        icon = "ℹ️"
        st.info(f"{icon} **{error_type}**: {message}")
    
    # Show details in expander if provided
    if details:
        with st.expander("Show details"):
            st.json(details)


def render_error_toast(
    message: str,
    severity: str = "error",
    duration: int = 5000
):
    """
    Render error as toast notification.
    
    Args:
        message: Error message
        severity: Severity level (error, warning, info, success)
        duration: Duration in milliseconds
    """
    if not STREAMLIT_AVAILABLE:
        return
    
    # Map severity to icon
    icons = {
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✅'
    }
    
    icon = icons.get(severity, 'ℹ️')
    
    st.toast(f"{icon} {message}", icon=icon)


# Example usage function
def demo_error_dashboard():
    """Demo function showing error dashboard usage"""
    if not STREAMLIT_AVAILABLE:
        print("Streamlit not available")
        return
    
    st.set_page_config(page_title="Error Dashboard Demo", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Select page",
            ["Dashboard", "Simulate Errors", "Widget Demo"]
        )
    
    if page == "Dashboard":
        render_error_dashboard()
    
    elif page == "Simulate Errors":
        st.title("Simulate Errors")
        st.markdown("Generate test errors to populate the dashboard")
        
        handler = get_error_handler()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Simulate Theme Load Error"):
                from .theme_errors import ThemeLoadError
                error = ThemeLoadError("test-theme", "File not found")
                handler.handle_error(error)
                st.success("Error simulated!")
        
        with col2:
            if st.button("Simulate CSS Error"):
                from .theme_errors import CSSGenerationError
                error = CSSGenerationError("test-theme", "Invalid token")
                handler.handle_error(error)
                st.success("Error simulated!")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("Simulate Component Error"):
                from .theme_errors import ComponentRenderError
                error = ComponentRenderError("Card", "Missing props")
                handler.handle_error(error)
                st.success("Error simulated!")
        
        with col4:
            if st.button("Simulate Validation Error"):
                from .theme_errors import ThemeValidationError
                error = ThemeValidationError(
                    "test-theme",
                    ["Invalid color", "Missing font"]
                )
                handler.handle_error(error)
                st.success("Error simulated!")
    
    elif page == "Widget Demo":
        st.title("Error Widget Demo")
        
        st.subheader("Summary Widget")
        render_error_summary_widget()
        
        st.markdown("---")
        
        st.subheader("Inline Notifications")
        
        render_inline_error_notification(
            "ThemeLoadError",
            "Failed to load theme 'custom-theme'",
            details={'reason': 'File not found', 'path': '/themes/custom-theme.json'},
            severity="error"
        )
        
        render_inline_error_notification(
            "ComponentWarning",
            "Component rendered with default props",
            severity="warning"
        )
        
        render_inline_error_notification(
            "Info",
            "Theme switched successfully",
            severity="info"
        )
        
        st.markdown("---")
        
        st.subheader("Toast Notifications")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Error Toast"):
                render_error_toast("An error occurred!", "error")
        
        with col2:
            if st.button("Warning Toast"):
                render_error_toast("This is a warning", "warning")
        
        with col3:
            if st.button("Info Toast"):
                render_error_toast("Information message", "info")
        
        with col4:
            if st.button("Success Toast"):
                render_error_toast("Operation successful!", "success")


if __name__ == "__main__":
    demo_error_dashboard()
