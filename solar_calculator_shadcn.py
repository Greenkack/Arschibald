"""
solar_calculator_shadcn.py

Migrated version of solar_calculator.py using shadcn/ui components.
This module wraps the existing solar_calculator functionality with modern UI components.
"""

import streamlit as st
from typing import Any, Dict, Optional
import plotly.graph_objects as go

# Import original solar calculator functions
from solar_calculator import (
    render_solar_calculator as render_solar_calculator_original,
    _ensure_project_data_dicts,
    _get_text,
    _is_session_alive,
    trace_solar,
)

# Import shadcn/ui migration helpers
from utils.shadcn_migration_helpers import (
    inject_shadcn_styles,
    shadcn_card,
    shadcn_alert,
    shadcn_metric,
    shadcn_badge,
    apply_shadcn_chart_theme,
    shadcn_section,
    SHADCN_AVAILABLE,
)

# Import components directly
try:
    from components.card import card
    from components.alert import alert
    from components.metric_card import metric_card
    from theming import ThemeManager
    from utils.shadcn_chart_theme import apply_chart_theme
except ImportError:
    pass


@trace_solar
def render_solar_calculator_with_shadcn(
    texts: dict[str, str],
    module_name: str | None = None
) -> None:
    """
    Enhanced Solar Calculator with shadcn/ui components.
    
    This is a wrapper around the original render_solar_calculator that adds
    shadcn/ui styling and components while maintaining all functionality.
    
    Args:
        texts: Translation dictionary
        module_name: Optional module name for navigation
    """
    # Inject shadcn/ui styles
    inject_shadcn_styles()
    
    # Initialize theme manager
    if 'theme_manager' not in st.session_state and SHADCN_AVAILABLE:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    # Call original function with shadcn/ui enhancements
    render_solar_calculator_original(texts, module_name)


def render_solar_calculator_section_with_card(
    title: str,
    icon: str,
    content_func: callable,
    variant: str = "default",
    collapsible: bool = False,
    expanded: bool = True
):
    """
    Render a solar calculator section using shadcn/ui Card component.
    
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
    
    if collapsible:
        with st.expander(f"{icon} {title}", expanded=expanded):
            content_func()
    else:
        theme_manager = st.session_state.get('theme_manager')
        if theme_manager:
            with card(title=f"{icon} {title}", variant=variant, theme_manager=theme_manager):
                content_func()
        else:
            st.subheader(f"{icon} {title}")
            content_func()


def display_pricing_with_shadcn(details: dict[str, Any], texts: dict[str, str]) -> None:
    """
    Display pricing information using shadcn/ui components.
    
    Replaces the standard pricing display with modern cards and metrics.
    
    Args:
        details: Project details dictionary
        texts: Translation dictionary
    """
    if not SHADCN_AVAILABLE or not _is_session_alive():
        # Fallback to original display
        from solar_calculator import _display_matrix_pricing
        _display_matrix_pricing(details, texts)
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        from solar_calculator import _display_matrix_pricing
        _display_matrix_pricing(details, texts)
        return
    
    # Import pricing functions
    try:
        from solar_calculator import get_total_price_with_matrix_mode, _format_german_currency
    except ImportError:
        st.error("Pricing functions not available")
        return
    
    # Get pricing data
    pricing_result = get_total_price_with_matrix_mode(details)
    
    if not pricing_result['success']:
        # Display error with shadcn/ui alert
        alert(
            message=pricing_result['error'],
            alert_type="error",
            title="Preismatrix-Fehler",
            theme_manager=theme_manager
        )
        
        # Provide guidance
        matrix_info = pricing_result.get('matrix_info', {})
        error_type = matrix_info.get('error_type')
        
        if error_type == 'no_matrix':
            alert(
                message="Aktivieren Sie eine Preismatrix in den Admin-Einstellungen.",
                alert_type="info",
                title="Lösung",
                icon="",
                theme_manager=theme_manager
            )
        return
    
    # Display pricing with cards
    with card(
        title=" Preisübersicht (Preismatrix-Modus)",
        variant="elevated",
        theme_manager=theme_manager
    ):
        base_price = pricing_result['base_price']
        extras_price = pricing_result['extras_price']
        net_total = pricing_result['net_total']
        vat_amount = pricing_result['vat_amount']
        gross_total = pricing_result['gross_total']
        
        # Display metrics in a grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            metric_card(
                label="Basispreis",
                value=_format_german_currency(base_price),
                icon="",
                size="medium",
                theme_manager=theme_manager
            )
        
        with col2:
            metric_card(
                label="Extras",
                value=_format_german_currency(extras_price),
                icon="",
                size="medium",
                theme_manager=theme_manager
            )
        
        with col3:
            metric_card(
                label="Netto-Gesamt",
                value=_format_german_currency(net_total),
                icon="",
                size="medium",
                theme_manager=theme_manager
            )
        
        st.markdown("---")
        
        # Display final price prominently
        metric_card(
            label=" Brutto-Gesamtpreis",
            value=_format_german_currency(gross_total),
            icon="",
            size="large",
            theme_manager=theme_manager
        )
        
        # Display VAT info
        st.caption(f"inkl. MwSt. (19%): {_format_german_currency(vat_amount)}")
    
    # Store pricing data
    details['pricing_mode'] = 'matrix'
    details['net_total'] = net_total
    details['vat_amount'] = vat_amount
    details['gross_total'] = gross_total


def apply_chart_theme_to_all_figures(figures: list[go.Figure]) -> list[go.Figure]:
    """
    Apply shadcn/ui theme to all Plotly figures.
    
    Args:
        figures: List of Plotly figures
    
    Returns:
        List of themed figures
    """
    if not SHADCN_AVAILABLE:
        return figures
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return figures
    
    themed_figures = []
    for fig in figures:
        themed_fig = apply_chart_theme(fig, theme_manager)
        themed_figures.append(themed_fig)
    
    return themed_figures


# Export the main render function
__all__ = [
    'render_solar_calculator_with_shadcn',
    'render_solar_calculator_section_with_card',
    'display_pricing_with_shadcn',
    'apply_chart_theme_to_all_figures',
]
