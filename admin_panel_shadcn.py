"""
admin_panel_shadcn.py

Migrated version of admin_panel.py using shadcn/ui components.
This module wraps the existing admin panel functionality with modern UI components.
"""

import streamlit as st
from typing import Any, Dict, List, Optional, Callable

# Import original admin panel functions
from admin_panel import (
    render_admin_panel as render_admin_panel_original,
    get_text_local,
    trace_admin,
    ADMIN_TAB_KEYS_DEFINITION_GLOBAL,
    ADMIN_TAB_ICONS,
    ADMIN_TAB_DESCRIPTIONS,
    ADMIN_TAB_LABELS_DE,
)

# Import shadcn/ui migration helpers
from utils.shadcn_migration_helpers import (
    inject_shadcn_styles,
    shadcn_card,
    shadcn_alert,
    shadcn_metric,
    shadcn_badge,
    shadcn_section,
    SHADCN_AVAILABLE,
)

# Import components directly
try:
    from components.card import card
    from components.alert import alert
    from components.badge import badge
    from components.metric_card import metric_card
    from components.accordion import accordion
    from theming import ThemeManager
    from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem
except ImportError:
    pass


@trace_admin
def render_admin_panel_with_shadcn(
    texts: dict[str, str] | tuple,
    get_db_connection_func: Callable[[], Any | None],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    **kwargs
):
    """
    Enhanced Admin Panel with shadcn/ui components.
    
    This is a wrapper around the original render_admin_panel that adds
    shadcn/ui styling and components while maintaining all functionality.
    
    Args:
        texts: Translation dictionary
        get_db_connection_func: Function to get database connection
        load_admin_setting_func: Function to load admin settings
        save_admin_setting_func: Function to save admin settings
        **kwargs: Additional arguments
    """
    # Inject shadcn/ui styles
    inject_shadcn_styles()
    
    # Initialize theme manager
    if 'theme_manager' not in st.session_state and SHADCN_AVAILABLE:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    # Call original function
    render_admin_panel_original(
        texts,
        get_db_connection_func,
        load_admin_setting_func,
        save_admin_setting_func,
        **kwargs
    )


def render_admin_navigation_with_shadcn(
    current_tab: str,
    on_tab_change: Callable[[str], None]
):
    """
    Render admin navigation using shadcn/ui sidebar components.
    
    Args:
        current_tab: Currently selected tab key
        on_tab_change: Callback function when tab changes
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    # Create sidebar navigation
    sidebar = ShadcnSidebar(theme_manager)
    
    # Group tabs by category
    management_tabs = [
        "admin_tab_company_management_new",
        "admin_tab_user_management",
        "admin_tab_product_management",
        "admin_tab_logo_management",
    ]
    
    database_tabs = [
        "admin_tab_product_database_crud",
        "admin_tab_pv_mounting",
        "admin_tab_services_management",
        "admin_tab_price_matrix",
    ]
    
    crm_tabs = [
        "admin_tab_tag_management",
        "admin_tab_template_management",
        "admin_tab_lead_scoring",
        "admin_tab_backup_management",
    ]
    
    settings_tabs = [
        "admin_tab_general_settings",
        "admin_tab_intro_settings",
        "admin_tab_tariff_management",
        "admin_tab_heatpump_settings",
        "admin_tab_pdf_design",
        "admin_tab_payment_terms",
        "admin_tab_visualization_settings",
    ]
    
    system_tabs = [
        "admin_tab_build_infos",
        "admin_tab_security_settings",
        "admin_tab_advanced",
    ]
    
    # Create menu groups
    menu_groups = []
    
    # Management group
    management_items = []
    for tab_key in management_tabs:
        if tab_key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL:
            management_items.append(MenuItem(
                key=tab_key,
                label=ADMIN_TAB_LABELS_DE.get(tab_key, tab_key),
                icon=ADMIN_TAB_ICONS.get(tab_key, ""),
                active=tab_key == current_tab,
                on_click=lambda k=tab_key: on_tab_change(k)
            ))
    
    if management_items:
        menu_groups.append(MenuGroup(
            title=" Verwaltung",
            items=management_items
        ))
    
    # Database group
    database_items = []
    for tab_key in database_tabs:
        if tab_key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL:
            database_items.append(MenuItem(
                key=tab_key,
                label=ADMIN_TAB_LABELS_DE.get(tab_key, tab_key),
                icon=ADMIN_TAB_ICONS.get(tab_key, ""),
                active=tab_key == current_tab,
                on_click=lambda k=tab_key: on_tab_change(k)
            ))
    
    if database_items:
        menu_groups.append(MenuGroup(
            title=" Datenbank",
            items=database_items
        ))
    
    # CRM group
    crm_items = []
    for tab_key in crm_tabs:
        if tab_key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL:
            crm_items.append(MenuItem(
                key=tab_key,
                label=ADMIN_TAB_LABELS_DE.get(tab_key, tab_key),
                icon=ADMIN_TAB_ICONS.get(tab_key, ""),
                active=tab_key == current_tab,
                on_click=lambda k=tab_key: on_tab_change(k)
            ))
    
    if crm_items:
        menu_groups.append(MenuGroup(
            title=" CRM",
            items=crm_items
        ))
    
    # Settings group
    settings_items = []
    for tab_key in settings_tabs:
        if tab_key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL:
            settings_items.append(MenuItem(
                key=tab_key,
                label=ADMIN_TAB_LABELS_DE.get(tab_key, tab_key),
                icon=ADMIN_TAB_ICONS.get(tab_key, ""),
                active=tab_key == current_tab,
                on_click=lambda k=tab_key: on_tab_change(k)
            ))
    
    if settings_items:
        menu_groups.append(MenuGroup(
            title=" Einstellungen",
            items=settings_items
        ))
    
    # System group
    system_items = []
    for tab_key in system_tabs:
        if tab_key in ADMIN_TAB_KEYS_DEFINITION_GLOBAL:
            system_items.append(MenuItem(
                key=tab_key,
                label=ADMIN_TAB_LABELS_DE.get(tab_key, tab_key),
                icon=ADMIN_TAB_ICONS.get(tab_key, ""),
                active=tab_key == current_tab,
                on_click=lambda k=tab_key: on_tab_change(k)
            ))
    
    if system_items:
        menu_groups.append(MenuGroup(
            title=" System",
            items=system_items
        ))
    
    # Render sidebar
    sidebar.render(menu_groups)


def render_admin_section_with_card(
    title: str,
    icon: str,
    content_func: callable,
    variant: str = "default",
    collapsible: bool = False,
    expanded: bool = True
):
    """
    Render an admin section using shadcn/ui Card component.
    
    Args:
        title: Section title
        icon: Section icon
        content_func: Function that renders the section content
        variant: Card variant (default, outlined, elevated)
        collapsible: Whether the section is collapsible
        expanded: Whether the section is expanded by default
    """
    if not SHADCN_AVAILABLE:
        # Fallback to standard container
        if collapsible:
            with st.expander(f"{icon} {title}", expanded=expanded):
                content_func()
        else:
            st.subheader(f"{icon} {title}")
            content_func()
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        if collapsible:
            with st.expander(f"{icon} {title}", expanded=expanded):
                content_func()
        else:
            st.subheader(f"{icon} {title}")
            content_func()
        return
    
    if collapsible:
        with st.expander(f"{icon} {title}", expanded=expanded):
            content_func()
    else:
        with card(title=f"{icon} {title}", variant=variant, theme_manager=theme_manager):
            content_func()


def render_admin_settings_form_with_shadcn(
    settings: Dict[str, Any],
    on_save: Callable[[Dict[str, Any]], bool],
    form_title: str = "Einstellungen",
    form_icon: str = ""
):
    """
    Render admin settings form using shadcn/ui components.
    
    Args:
        settings: Settings dictionary
        on_save: Callback function to save settings
        form_title: Form title
        form_icon: Form icon
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    with card(
        title=f"{form_icon} {form_title}",
        variant="elevated",
        theme_manager=theme_manager
    ):
        with st.form("admin_settings_form_shadcn"):
            # Render form fields based on settings
            updated_settings = {}
            
            for key, value in settings.items():
                if isinstance(value, bool):
                    updated_settings[key] = st.checkbox(
                        key.replace('_', ' ').title(),
                        value=value
                    )
                elif isinstance(value, (int, float)):
                    updated_settings[key] = st.number_input(
                        key.replace('_', ' ').title(),
                        value=value
                    )
                elif isinstance(value, str):
                    updated_settings[key] = st.text_input(
                        key.replace('_', ' ').title(),
                        value=value
                    )
                else:
                    updated_settings[key] = value
            
            # Submit button
            submitted = st.form_submit_button(
                " Einstellungen speichern",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if on_save(updated_settings):
                    alert(
                        message="Einstellungen erfolgreich gespeichert!",
                        alert_type="success",
                        theme_manager=theme_manager
                    )
                else:
                    alert(
                        message="Fehler beim Speichern der Einstellungen.",
                        alert_type="error",
                        theme_manager=theme_manager
                    )


def render_admin_dashboard_with_metrics(
    stats: Dict[str, Any]
):
    """
    Render admin dashboard with shadcn/ui metrics.
    
    Args:
        stats: Statistics dictionary
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    # Display metrics in a grid
    cols = st.columns(4)
    
    metric_configs = [
        ("total_products", "Produkte", ""),
        ("total_customers", "Kunden", ""),
        ("total_companies", "Firmen", ""),
        ("total_users", "Benutzer", ""),
    ]
    
    for i, (key, label, icon) in enumerate(metric_configs):
        with cols[i]:
            value = stats.get(key, 0)
            metric_card(
                label=label,
                value=str(value),
                icon=icon,
                size="medium",
                theme_manager=theme_manager
            )


# Export the main render function
__all__ = [
    'render_admin_panel_with_shadcn',
    'render_admin_navigation_with_shadcn',
    'render_admin_section_with_card',
    'render_admin_settings_form_with_shadcn',
    'render_admin_dashboard_with_metrics',
]
