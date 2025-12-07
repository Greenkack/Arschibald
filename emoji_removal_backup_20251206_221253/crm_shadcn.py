"""
crm_shadcn.py

Migrated version of crm.py using shadcn/ui components.
This module wraps the existing CRM functionality with modern UI components.
"""

import streamlit as st
import sqlite3
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

# Import original CRM functions
from crm import (
    render_crm as render_crm_original,
    save_customer,
    load_customer,
    load_all_customers,
    delete_customer,
    create_tables_crm,
    get_text_crm,
    trace_crm,
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
    from theming import ThemeManager
except ImportError:
    pass


@trace_crm
def render_crm_with_shadcn(
    texts: dict[str, str],
    get_db_connection_func: Callable[[], sqlite3.Connection | None],
    *,
    show_header: bool = True,
    **kwargs
):
    """
    Enhanced CRM with shadcn/ui components.
    
    This is a wrapper around the original render_crm that adds
    shadcn/ui styling and components while maintaining all functionality.
    
    Args:
        texts: Translation dictionary
        get_db_connection_func: Function to get database connection
        show_header: Whether to show the header
        **kwargs: Additional arguments
    """
    # Inject shadcn/ui styles
    inject_shadcn_styles()
    
    # Initialize theme manager
    if 'theme_manager' not in st.session_state and SHADCN_AVAILABLE:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    # Call original function
    render_crm_original(texts, get_db_connection_func, show_header=show_header, **kwargs)


def render_customer_list_with_cards(
    customers: List[Dict[str, Any]],
    texts: dict[str, str],
    conn: sqlite3.Connection
):
    """
    Render customer list using shadcn/ui Card components.
    
    Args:
        customers: List of customer dictionaries
        texts: Translation dictionary
        conn: Database connection
    """
    if not SHADCN_AVAILABLE or not customers:
        # Fallback to original rendering
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    # Display customer count metric
    metric_card(
        label="Gesamt Kunden",
        value=str(len(customers)),
        icon="👥",
        size="medium",
        theme_manager=theme_manager
    )
    
    st.markdown("---")
    
    # Display customers in modern card grid (4 columns)
    cols_per_row = 4
    for i in range(0, len(customers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(customers):
                customer = customers[i + j]
                with cols[j]:
                    render_customer_card(customer, texts, conn, theme_manager)


def render_customer_card(
    customer: Dict[str, Any],
    texts: dict[str, str],
    conn: sqlite3.Connection,
    theme_manager: Any
):
    """
    Render a single customer as a shadcn/ui card.
    
    Args:
        customer: Customer dictionary
        texts: Translation dictionary
        conn: Database connection
        theme_manager: Theme manager instance
    """
    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
    customer_city = customer.get('city', 'N/A')
    customer_email = customer.get('email', 'N/A')
    customer_phone = customer.get('phone', 'N/A')
    
    # Create card content
    card_content = f"""
    **📍 Stadt:** {customer_city}  
    **📧 E-Mail:** {customer_email[:30]}{'...' if len(customer_email) > 30 else ''}  
    **📞 Telefon:** {customer_phone}
    """
    
    with card(
        title=f"👤 {customer_name}",
        content=card_content,
        variant="outlined",
        theme_manager=theme_manager
    ):
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👁️", key=f"view_customer_{customer['id']}", help="Ansehen", use_container_width=True):
                st.session_state['selected_customer_id'] = customer['id']
                st.session_state['crm_view_mode'] = 'view_customer'
                st.rerun()
        
        with col2:
            if st.button("✏️", key=f"edit_customer_{customer['id']}", help="Bearbeiten", use_container_width=True):
                st.session_state['selected_customer_id'] = customer['id']
                st.session_state['crm_view_mode'] = 'edit_customer'
                st.rerun()
        
        with col3:
            if st.button("❌", key=f"del_customer_{customer['id']}", help="Löschen", use_container_width=True):
                confirm_key = f"confirm_delete_customer_{customer['id']}"
                if st.session_state.get(confirm_key, False):
                    if delete_customer(conn, customer['id']):
                        alert(
                            message="Kunde erfolgreich gelöscht.",
                            alert_type="success",
                            theme_manager=theme_manager
                        )
                        del st.session_state[confirm_key]
                        st.rerun()
                    else:
                        alert(
                            message="Löschen fehlgeschlagen.",
                            alert_type="error",
                            theme_manager=theme_manager
                        )
                else:
                    st.session_state[confirm_key] = True
                    alert(
                        message="Nochmal klicken zum Bestätigen!",
                        alert_type="warning",
                        theme_manager=theme_manager
                    )


def render_customer_form_with_shadcn(
    customer_data: Dict[str, Any],
    texts: dict[str, str],
    is_edit: bool = False
):
    """
    Render customer form using shadcn/ui components.
    
    Args:
        customer_data: Customer data dictionary
        texts: Translation dictionary
        is_edit: Whether this is an edit form
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    form_title = "Kunden bearbeiten" if is_edit else "Neuen Kunden anlegen"
    
    with card(
        title=f"📝 {form_title}",
        variant="elevated",
        theme_manager=theme_manager
    ):
        with st.form("customer_form_shadcn", clear_on_submit=False):
            # Personal Information Section
            st.markdown("### 👤 Persönliche Daten")
            
            col1, col2 = st.columns(2)
            with col1:
                salutation = st.selectbox(
                    "Anrede",
                    options=['Herr', 'Frau', 'Familie', 'Divers', ''],
                    index=['Herr', 'Frau', 'Familie', 'Divers', ''].index(
                        customer_data.get('salutation', '')
                    )
                )
            
            with col2:
                title = st.text_input(
                    "Titel",
                    value=customer_data.get('title', '')
                )
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input(
                    "Vorname *",
                    value=customer_data.get('first_name', '')
                )
            
            with col2:
                last_name = st.text_input(
                    "Nachname *",
                    value=customer_data.get('last_name', '')
                )
            
            company_name = st.text_input(
                "Firmenname (optional)",
                value=customer_data.get('company_name', '')
            )
            
            st.markdown("---")
            st.markdown("### 📍 Adresse")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                address = st.text_input(
                    "Straße",
                    value=customer_data.get('address', '')
                )
            
            with col2:
                house_number = st.text_input(
                    "Nr.",
                    value=customer_data.get('house_number', '')
                )
            
            col1, col2 = st.columns([1, 2])
            with col1:
                zip_code = st.text_input(
                    "PLZ",
                    value=customer_data.get('zip_code', '')
                )
            
            with col2:
                city = st.text_input(
                    "Ort",
                    value=customer_data.get('city', '')
                )
            
            st.markdown("---")
            st.markdown("### 📞 Kontakt")
            
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input(
                    "E-Mail",
                    value=customer_data.get('email', '')
                )
            
            with col2:
                phone = st.text_input(
                    "Telefon",
                    value=customer_data.get('phone', '')
                )
            
            # Submit button
            submitted = st.form_submit_button(
                "💾 Speichern",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                # Return form data
                return {
                    'salutation': salutation,
                    'title': title,
                    'first_name': first_name,
                    'last_name': last_name,
                    'company_name': company_name,
                    'address': address,
                    'house_number': house_number,
                    'zip_code': zip_code,
                    'city': city,
                    'email': email,
                    'phone': phone,
                }
    
    return None


def render_crm_dashboard_with_metrics(
    conn: sqlite3.Connection,
    texts: dict[str, str]
):
    """
    Render CRM dashboard with shadcn/ui metrics.
    
    Args:
        conn: Database connection
        texts: Translation dictionary
    """
    if not SHADCN_AVAILABLE:
        return
    
    theme_manager = st.session_state.get('theme_manager')
    if not theme_manager:
        return
    
    # Get statistics
    customers = load_all_customers(conn)
    total_customers = len(customers)
    
    # Display metrics in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            label="Gesamt Kunden",
            value=str(total_customers),
            icon="👥",
            size="medium",
            theme_manager=theme_manager
        )
    
    with col2:
        # Count customers with email
        customers_with_email = sum(1 for c in customers if c.get('email'))
        metric_card(
            label="Mit E-Mail",
            value=str(customers_with_email),
            icon="📧",
            size="medium",
            theme_manager=theme_manager
        )
    
    with col3:
        # Count customers with phone
        customers_with_phone = sum(1 for c in customers if c.get('phone'))
        metric_card(
            label="Mit Telefon",
            value=str(customers_with_phone),
            icon="📞",
            size="medium",
            theme_manager=theme_manager
        )
    
    with col4:
        # Count unique cities
        unique_cities = len(set(c.get('city', '') for c in customers if c.get('city')))
        metric_card(
            label="Städte",
            value=str(unique_cities),
            icon="📍",
            size="medium",
            theme_manager=theme_manager
        )


# Export the main render function
__all__ = [
    'render_crm_with_shadcn',
    'render_customer_list_with_cards',
    'render_customer_card',
    'render_customer_form_with_shadcn',
    'render_crm_dashboard_with_metrics',
]
