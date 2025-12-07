"""
shadcn_migration_helpers.py

Helper functions for migrating existing modules to shadcn/ui components.
Provides convenience wrappers and utilities for consistent migration.
"""

import streamlit as st
from typing import Any, Dict, Optional, Callable
import plotly.graph_objects as go

# Import shadcn/ui components
try:
    from components.card import Card, card
    from components.alert import Alert, alert
    from components.badge import Badge, badge
    from components.metric_card import MetricCard, metric_card
    from theming import ThemeManager
    from utils.shadcn_chart_theme import apply_chart_theme
    SHADCN_AVAILABLE = True
except ImportError:
    SHADCN_AVAILABLE = False
    print("Warning: shadcn/ui components not available for migration")


def get_theme_manager() -> Optional[Any]:
    """Get or initialize the theme manager from session state."""
    if not SHADCN_AVAILABLE:
        return None
    
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    return st.session_state.theme_manager


def shadcn_container(
    title: Optional[str] = None,
    content: Optional[str] = None,
    footer: Optional[str] = None,
    variant: str = "default",
    icon: Optional[str] = None,
    **kwargs
):
    """
    Replacement for st.container() using shadcn/ui Card component.
    
    Args:
        title: Card title
        content: Card content (markdown)
        footer: Card footer (markdown)
        variant: Card variant (default, outlined, elevated)
        icon: Optional icon for the card
        **kwargs: Additional arguments passed to Card
    
    Returns:
        Context manager for the card content
    """
    if not SHADCN_AVAILABLE:
        return st.container()
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        return st.container()
    
    card_component = Card(theme_manager)
    return card_component.render(
        title=title,
        content=content,
        footer=footer,
        variant=variant,
        icon=icon,
        **kwargs
    )


def shadcn_card(
    title: Optional[str] = None,
    content: Optional[str] = None,
    footer: Optional[str] = None,
    variant: str = "default",
    icon: Optional[str] = None,
    **kwargs
):
    """
    Convenience function for creating a shadcn/ui card.
    Falls back to st.container() if shadcn/ui is not available.
    """
    if not SHADCN_AVAILABLE:
        # Fallback to basic container
        with st.container():
            if title:
                st.subheader(title)
            if content:
                st.markdown(content)
            if footer:
                st.caption(footer)
        return
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        with st.container():
            if title:
                st.subheader(title)
            if content:
                st.markdown(content)
            if footer:
                st.caption(footer)
        return
    
    card(
        title=title,
        content=content,
        footer=footer,
        variant=variant,
        icon=icon,
        theme_manager=theme_manager,
        **kwargs
    )


def shadcn_alert(
    message: str,
    alert_type: str = "info",
    title: Optional[str] = None,
    icon: Optional[str] = None,
    dismissible: bool = False,
    **kwargs
):
    """
    Replacement for st.info/warning/error/success using shadcn/ui Alert component.
    
    Args:
        message: Alert message
        alert_type: Type of alert (info, success, warning, error)
        title: Optional alert title
        icon: Optional custom icon
        dismissible: Whether the alert can be dismissed
        **kwargs: Additional arguments
    """
    if not SHADCN_AVAILABLE:
        # Fallback to standard Streamlit alerts
        if alert_type == "info":
            st.info(message)
        elif alert_type == "success":
            st.success(message)
        elif alert_type == "warning":
            st.warning(message)
        elif alert_type == "error":
            st.error(message)
        return
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        if alert_type == "info":
            st.info(message)
        elif alert_type == "success":
            st.success(message)
        elif alert_type == "warning":
            st.warning(message)
        elif alert_type == "error":
            st.error(message)
        return
    
    alert(
        message=message,
        alert_type=alert_type,
        title=title,
        icon=icon,
        dismissible=dismissible,
        theme_manager=theme_manager,
        **kwargs
    )


def shadcn_metric(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    icon: Optional[str] = None,
    size: str = "medium",
    **kwargs
):
    """
    Replacement for st.metric() using shadcn/ui MetricCard component.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator
        delta_color: Color for delta (normal, inverse, off)
        icon: Optional icon
        size: Card size (small, medium, large)
        **kwargs: Additional arguments
    """
    if not SHADCN_AVAILABLE:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
        return
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
        return
    
    metric_card(
        label=label,
        value=value,
        trend=delta,
        icon=icon,
        size=size,
        theme_manager=theme_manager,
        **kwargs
    )


def shadcn_badge(
    text: str,
    variant: str = "default",
    size: str = "medium",
    icon: Optional[str] = None,
    **kwargs
):
    """
    Create a shadcn/ui badge.
    
    Args:
        text: Badge text
        variant: Badge variant (default, secondary, success, warning, error, info)
        size: Badge size (small, medium, large)
        icon: Optional icon
        **kwargs: Additional arguments
    """
    if not SHADCN_AVAILABLE:
        st.markdown(f"`{text}`")
        return
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        st.markdown(f"`{text}`")
        return
    
    badge(
        text=text,
        variant=variant,
        size=size,
        icon=icon,
        theme_manager=theme_manager,
        **kwargs
    )


def apply_shadcn_chart_theme(fig: go.Figure, theme_name: Optional[str] = None) -> go.Figure:
    """
    Apply shadcn/ui theme to a Plotly chart.
    
    Args:
        fig: Plotly figure
        theme_name: Optional theme name (uses current theme if not specified)
    
    Returns:
        Themed Plotly figure
    """
    if not SHADCN_AVAILABLE:
        return fig
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        return fig
    
    if theme_name:
        theme_manager.set_theme(theme_name)
    
    return apply_chart_theme(fig, theme_manager)


def shadcn_section(
    title: str,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    collapsible: bool = False,
    expanded: bool = True
):
    """
    Create a styled section with shadcn/ui design.
    
    Args:
        title: Section title
        icon: Optional icon
        description: Optional description
        collapsible: Whether the section is collapsible
        expanded: Whether the section is expanded by default (if collapsible)
    
    Returns:
        Context manager for the section content
    """
    if collapsible:
        with st.expander(f"{icon or ''} {title}", expanded=expanded):
            if description:
                st.caption(description)
            yield
    else:
        st.markdown(f"### {icon or ''} {title}")
        if description:
            st.caption(description)
        yield


def migrate_container_to_card(
    container_func: Callable,
    title: Optional[str] = None,
    variant: str = "default",
    icon: Optional[str] = None
):
    """
    Decorator to migrate a function that uses st.container() to use shadcn/ui Card.
    
    Usage:
        @migrate_container_to_card(title="My Section", icon="")
        def my_section():
            st.write("Content here")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if SHADCN_AVAILABLE:
                theme_manager = get_theme_manager()
                if theme_manager:
                    with shadcn_container(title=title, variant=variant, icon=icon):
                        return func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def inject_shadcn_styles():
    """
    Inject shadcn/ui CSS styles into the current page.
    Should be called once at the beginning of each page.
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = get_theme_manager()
    if not theme_manager:
        return
    
    # Only inject once per session
    if 'shadcn_css_injected' not in st.session_state:
        from theming import CSSGenerator
        css_gen = CSSGenerator(theme_manager.current_theme)
        css = css_gen.generate_full_css()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.session_state.shadcn_css_injected = True


# Convenience exports
__all__ = [
    'get_theme_manager',
    'shadcn_container',
    'shadcn_card',
    'shadcn_alert',
    'shadcn_metric',
    'shadcn_badge',
    'apply_shadcn_chart_theme',
    'shadcn_section',
    'migrate_container_to_card',
    'inject_shadcn_styles',
    'SHADCN_AVAILABLE',
]
