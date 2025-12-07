#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Panel - E-Mail Settings UI
Provides SMTP configuration and email template management for admin panel

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
from typing import Any, Callable
import sqlite3


def render_email_admin_settings(
    get_db_connection_func: Callable[[], sqlite3.Connection],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool]
):
    """
    Render email administration settings in admin panel
    
    Args:
        get_db_connection_func: Function to get database connection
        load_admin_setting_func: Function to load admin settings
        save_admin_setting_func: Function to save admin settings
    """
    
    try:
        from crm.features.email_ui import (
            render_smtp_configuration_ui,
            render_email_template_management_ui
        )
    except ImportError:
        st.error("E-Mail-Module konnten nicht geladen werden. Bitte prüfen Sie die Installation.")
        return
    
    st.header(" E-Mail-Integration")
    
    st.markdown("""
    Verwalten Sie hier die E-Mail-Integration für Ihr CRM-System.
    
    **Funktionen:**
    - SMTP-Server-Konfiguration
    - E-Mail-Vorlagen erstellen und verwalten
    - E-Mails direkt aus Kundenprofilen versenden
    - Automatische E-Mail-Historie
    """)
    
    # Create tabs for different sections
    tab_smtp, tab_templates = st.tabs([
        " SMTP-Konfiguration",
        " E-Mail-Vorlagen"
    ])
    
    # Tab 1: SMTP Configuration
    with tab_smtp:
        render_smtp_configuration_ui(
            load_admin_setting_func,
            save_admin_setting_func
        )
    
    # Tab 2: Email Templates
    with tab_templates:
        conn = get_db_connection_func()
        if conn:
            try:
                render_email_template_management_ui(conn)
            finally:
                conn.close()
        else:
            st.error("Keine Datenbankverbindung verfügbar")
