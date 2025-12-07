#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM Email Integration Helper
Provides helper functions to integrate email functionality into CRM customer views

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
import sqlite3
from typing import Any, Callable


def render_customer_email_section(
    conn: sqlite3.Connection,
    customer_data: dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    texts: dict[str, str] = None
):
    """
    Render email section in customer profile
    
    Args:
        conn: Database connection
        customer_data: Customer data dictionary
        load_admin_setting_func: Function to load admin settings
        texts: Translations dictionary (optional)
    """
    
    # Check if customer has email
    if not customer_data.get('email'):
        st.info("📧 Keine E-Mail-Adresse für diesen Kunden hinterlegt.")
        return
    
    st.markdown("---")
    st.subheader("📧 E-Mail-Kommunikation")
    
    # Create tabs for sending and history
    tab_send, tab_history = st.tabs(["📤 E-Mail senden", "📋 E-Mail-Historie"])
    
    with tab_send:
        try:
            from crm.features.email_ui import render_send_email_ui
            from database import list_customer_documents
            
            # Get customer documents for attachments
            def get_customer_docs(customer_id):
                docs = list_customer_documents(customer_id)
                return docs if docs else []
            
            render_send_email_ui(
                conn,
                customer_data,
                load_admin_setting_func,
                get_customer_documents_func=get_customer_docs
            )
        except ImportError as e:
            st.error(f"E-Mail-Modul konnte nicht geladen werden: {e}")
    
    with tab_history:
        try:
            from crm.features.email_ui import render_email_history_ui
            
            render_email_history_ui(conn, customer_data['id'])
        except ImportError as e:
            st.error(f"E-Mail-Historie konnte nicht geladen werden: {e}")


def add_email_quick_action_button(
    customer_data: dict[str, Any],
    key_suffix: str = ""
) -> bool:
    """
    Add a quick action button to send email to customer
    
    Args:
        customer_data: Customer data dictionary
        key_suffix: Suffix for button key to avoid duplicates
    
    Returns:
        True if button was clicked
    """
    
    if not customer_data.get('email'):
        return False
    
    if st.button(
        f"📧 E-Mail an {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}",
        key=f"quick_email_{customer_data['id']}_{key_suffix}",
        use_container_width=True
    ):
        # Set session state to show email dialog
        st.session_state['show_email_dialog'] = True
        st.session_state['email_customer_id'] = customer_data['id']
        return True
    
    return False
