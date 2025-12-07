#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM E-Mail-Integration - UI Components
Provides UI for email template management, SMTP configuration, and email sending

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import streamlit as st
from typing import Any, Callable
import sqlite3

try:
    from crm.features.email_manager import (
        create_email_tables,
        ensure_email_tables,
        create_email_template,
        get_email_template,
        get_email_template_by_name,
        list_email_templates,
        update_email_template,
        delete_email_template,
        replace_placeholders,
        extract_placeholders,
        send_email,
        send_email_with_template,
        save_email_to_history,
        get_email_history_for_customer,
        test_smtp_connection,
        get_smtp_config,
        save_smtp_config,
        create_default_templates
    )
except ImportError:
    from email_manager import (
        create_email_tables,
        ensure_email_tables,
        create_email_template,
        get_email_template,
        get_email_template_by_name,
        list_email_templates,
        update_email_template,
        delete_email_template,
        replace_placeholders,
        extract_placeholders,
        send_email,
        send_email_with_template,
        save_email_to_history,
        get_email_history_for_customer,
        test_smtp_connection,
        get_smtp_config,
        save_smtp_config,
        create_default_templates
    )


# ============================================================================
# SMTP Configuration UI (for Admin Panel)
# ============================================================================

def render_smtp_configuration_ui(
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool]
):
    """Render SMTP configuration UI in admin panel"""
    
    st.subheader(" E-Mail-Konfiguration (SMTP)")
    
    st.info("""
    **E-Mail-Integration einrichten**
    
    Konfigurieren Sie hier Ihren SMTP-Server, um E-Mails direkt aus dem CRM zu versenden.
    Die Konfiguration wird verschlüsselt gespeichert.
    
    **Unterstützte Anbieter:**
    - Gmail (smtp.gmail.com:587)
    - Outlook/Office365 (smtp.office365.com:587)
    - Eigener SMTP-Server
    """)
    
    # Load current config
    current_config = get_smtp_config(load_admin_setting_func)
    
    # Configuration form
    with st.form("smtp_config_form"):
        st.markdown("### SMTP-Server-Einstellungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_host = st.text_input(
                "SMTP-Host",
                value=current_config.get('smtp_host', ''),
                placeholder="smtp.gmail.com",
                help="SMTP-Server-Adresse"
            )
            
            smtp_port = st.number_input(
                "SMTP-Port",
                min_value=1,
                max_value=65535,
                value=current_config.get('smtp_port', 587),
                help="Standard: 587 (TLS) oder 465 (SSL)"
            )
            
            smtp_use_tls = st.checkbox(
                "TLS verwenden",
                value=current_config.get('smtp_use_tls', True),
                help="Empfohlen für Port 587"
            )
        
        with col2:
            smtp_username = st.text_input(
                "Benutzername",
                value=current_config.get('smtp_username', ''),
                placeholder="ihre-email@example.com",
                help="Meist Ihre E-Mail-Adresse"
            )
            
            smtp_password = st.text_input(
                "Passwort",
                value=current_config.get('smtp_password', ''),
                type="password",
                help="SMTP-Passwort oder App-Passwort"
            )
        
        st.markdown("### Absender-Einstellungen")
        
        col3, col4 = st.columns(2)
        
        with col3:
            smtp_from_email = st.text_input(
                "Absender E-Mail",
                value=current_config.get('smtp_from_email', ''),
                placeholder="noreply@example.com",
                help="E-Mail-Adresse des Absenders"
            )
        
        with col4:
            smtp_from_name = st.text_input(
                "Absender Name",
                value=current_config.get('smtp_from_name', ''),
                placeholder="Ihr Firmenname",
                help="Anzeigename des Absenders"
            )
        
        # Submit buttons
        col_save, col_test = st.columns(2)
        
        with col_save:
            submit_save = st.form_submit_button(" Konfiguration speichern", use_container_width=True)
        
        with col_test:
            submit_test = st.form_submit_button(" Verbindung testen", use_container_width=True)
    
    # Handle form submission
    if submit_save or submit_test:
        new_config = {
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'smtp_username': smtp_username,
            'smtp_password': smtp_password,
            'smtp_use_tls': smtp_use_tls,
            'smtp_from_email': smtp_from_email,
            'smtp_from_name': smtp_from_name
        }
        
        if submit_test:
            # Test connection
            with st.spinner("Teste SMTP-Verbindung..."):
                success, message = test_smtp_connection(new_config)
                
                if success:
                    st.success(f" {message}")
                else:
                    st.error(f" {message}")
        
        if submit_save:
            # Save configuration
            if save_smtp_config(save_admin_setting_func, new_config):
                st.success(" SMTP-Konfiguration erfolgreich gespeichert!")
                st.rerun()
            else:
                st.error(" Fehler beim Speichern der Konfiguration")
    
    # Quick setup guides
    with st.expander(" Schnellanleitungen für gängige Anbieter"):
        st.markdown("""
        ### Gmail
        - **Host:** smtp.gmail.com
        - **Port:** 587
        - **TLS:** Aktiviert
        - **Hinweis:** Verwenden Sie ein [App-Passwort](https://support.google.com/accounts/answer/185833)
        
        ### Outlook/Office365
        - **Host:** smtp.office365.com
        - **Port:** 587
        - **TLS:** Aktiviert
        
        ### Eigener Server
        - Kontaktieren Sie Ihren IT-Administrator für die korrekten Einstellungen
        """)


# ============================================================================
# Email Template Management UI (for Admin Panel)
# ============================================================================

def render_email_template_management_ui(conn: sqlite3.Connection):
    """Render email template management UI in admin panel"""
    
    st.subheader(" E-Mail-Vorlagen verwalten")
    
    # Ensure tables exist
    ensure_email_tables(conn)
    
    # Tabs for different actions
    tab_list, tab_create, tab_edit = st.tabs([
        " Vorlagen anzeigen",
        " Neue Vorlage",
        " Vorlage bearbeiten"
    ])
    
    # Tab 1: List templates
    with tab_list:
        st.markdown("### Vorhandene E-Mail-Vorlagen")
        
        # Filter options
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            filter_category = st.selectbox(
                "Nach Kategorie filtern",
                ["Alle", "Angebot", "Nachfass", "Bestätigung", "Sonstiges"],
                key="template_filter_category"
            )
        
        with col_filter2:
            show_inactive = st.checkbox("Inaktive Vorlagen anzeigen", key="show_inactive_templates")
        
        # Get templates
        category = None if filter_category == "Alle" else filter_category
        templates = list_email_templates(conn, category=category, active_only=not show_inactive)
        
        if not templates:
            st.info("Keine Vorlagen gefunden. Erstellen Sie eine neue Vorlage im Tab 'Neue Vorlage'.")
        else:
            for template in templates:
                with st.expander(f" {template['name']} ({template['category'] or 'Keine Kategorie'})"):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**Betreff:** {template['subject']}")
                        st.markdown(f"**Kategorie:** {template['category'] or 'Keine'}")
                        st.markdown(f"**Status:** {' Aktiv' if template['is_active'] else ' Inaktiv'}")
                        st.markdown(f"**Erstellt:** {template['created_at']}")
                        
                        if template['placeholders']:
                            placeholders = template['placeholders']
                            if isinstance(placeholders, str):
                                import json
                                try:
                                    placeholders = json.loads(placeholders)
                                except:
                                    placeholders = []
                            st.markdown(f"**Platzhalter:** {', '.join(placeholders)}")
                        
                        with st.container():
                            st.markdown("**Vorschau:**")
                            st.text_area(
                                "Body",
                                value=template['body'][:200] + "..." if len(template['body']) > 200 else template['body'],
                                height=100,
                                disabled=True,
                                key=f"preview_{template['id']}"
                            )
                    
                    with col_actions:
                        if st.button(" Löschen", key=f"delete_{template['id']}", use_container_width=True):
                            if delete_email_template(conn, template['id']):
                                st.success("Vorlage gelöscht!")
                                st.rerun()
                            else:
                                st.error("Fehler beim Löschen")
    
    # Tab 2: Create new template
    with tab_create:
        st.markdown("### Neue E-Mail-Vorlage erstellen")
        
        with st.form("create_template_form"):
            template_name = st.text_input(
                "Vorlagenname *",
                placeholder="z.B. Angebot Nachfass",
                help="Eindeutiger Name für die Vorlage"
            )
            
            template_category = st.selectbox(
                "Kategorie",
                ["Angebot", "Nachfass", "Bestätigung", "Sonstiges"]
            )
            
            template_subject = st.text_input(
                "E-Mail-Betreff *",
                placeholder="z.B. Ihr Angebot für {{customer_name}}",
                help="Verwenden Sie {{platzhalter}} für dynamische Inhalte"
            )
            
            template_body = st.text_area(
                "E-Mail-Text *",
                height=300,
                placeholder="""Sehr geehrte/r {{customer_name}},

vielen Dank für Ihr Interesse an unseren Solaranlagen.

Anbei finden Sie Ihr persönliches Angebot.

Mit freundlichen Grüßen
{{company_name}}""",
                help="Verwenden Sie {{platzhalter}} für dynamische Inhalte"
            )
            
            st.markdown("**Verfügbare Platzhalter:**")
            st.code("""
{{customer_name}}    - Vollständiger Name
{{first_name}}       - Vorname
{{last_name}}        - Nachname
{{company_name}}     - Firmenname
{{email}}            - E-Mail-Adresse
{{phone}}            - Telefonnummer
{{address}}          - Vollständige Adresse
{{city}}             - Stadt
{{zip_code}}         - Postleitzahl
{{project_value}}    - Projektwert
{{current_date}}     - Aktuelles Datum
            """)
            
            submit_create = st.form_submit_button(" Vorlage erstellen", use_container_width=True)
        
        if submit_create:
            if not template_name or not template_subject or not template_body:
                st.error("Bitte füllen Sie alle Pflichtfelder aus!")
            else:
                # Extract placeholders
                placeholders = extract_placeholders(template_subject + " " + template_body)
                
                template_id = create_email_template(
                    conn,
                    name=template_name,
                    subject=template_subject,
                    body=template_body,
                    category=template_category,
                    placeholders=placeholders
                )
                
                if template_id:
                    st.success(f" Vorlage '{template_name}' erfolgreich erstellt!")
                    st.rerun()
                else:
                    st.error(" Fehler beim Erstellen der Vorlage. Möglicherweise existiert bereits eine Vorlage mit diesem Namen.")
    
    # Tab 3: Edit template
    with tab_edit:
        st.markdown("### Vorlage bearbeiten")
        
        templates = list_email_templates(conn, active_only=True)
        
        if not templates:
            st.info("Keine aktiven Vorlagen zum Bearbeiten vorhanden.")
        else:
            template_names = [t['name'] for t in templates]
            selected_template_name = st.selectbox(
                "Vorlage auswählen",
                template_names,
                key="edit_template_select"
            )
            
            if selected_template_name:
                template = get_email_template_by_name(conn, selected_template_name)
                
                if template:
                    with st.form("edit_template_form"):
                        edit_subject = st.text_input(
                            "E-Mail-Betreff",
                            value=template['subject']
                        )
                        
                        edit_body = st.text_area(
                            "E-Mail-Text",
                            value=template['body'],
                            height=300
                        )
                        
                        edit_category = st.selectbox(
                            "Kategorie",
                            ["Angebot", "Nachfass", "Bestätigung", "Sonstiges"],
                            index=["Angebot", "Nachfass", "Bestätigung", "Sonstiges"].index(template['category']) if template['category'] in ["Angebot", "Nachfass", "Bestätigung", "Sonstiges"] else 3
                        )
                        
                        submit_edit = st.form_submit_button(" Änderungen speichern", use_container_width=True)
                    
                    if submit_edit:
                        # Extract new placeholders
                        placeholders = extract_placeholders(edit_subject + " " + edit_body)
                        
                        if update_email_template(
                            conn,
                            template['id'],
                            subject=edit_subject,
                            body=edit_body,
                            category=edit_category,
                            placeholders=placeholders
                        ):
                            st.success(" Vorlage erfolgreich aktualisiert!")
                            st.rerun()
                        else:
                            st.error(" Fehler beim Aktualisieren der Vorlage")


# ============================================================================
# Email Sending UI (for Customer Profile)
# ============================================================================

def render_send_email_ui(
    conn: sqlite3.Connection,
    customer_data: dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    get_customer_documents_func: Callable[[int], list[dict[str, Any]]] = None
):
    """Render email sending UI in customer profile"""
    
    st.subheader(f" E-Mail an {customer_data.get('first_name', '')} {customer_data.get('last_name', '')} senden")
    
    # Ensure tables exist
    ensure_email_tables(conn)
    
    # Get SMTP config
    smtp_config = get_smtp_config(load_admin_setting_func)
    
    # Check if SMTP is configured
    if not smtp_config.get('smtp_host') or not smtp_config.get('smtp_username'):
        st.warning("""
         **E-Mail-Versand nicht konfiguriert**
        
        Bitte konfigurieren Sie zuerst die SMTP-Einstellungen im Admin-Panel unter "E-Mail-Konfiguration".
        """)
        return
    
    # Tabs for template or custom email
    tab_template, tab_custom = st.tabs([" Mit Vorlage", " Individuelle E-Mail"])
    
    # Tab 1: Send with template
    with tab_template:
        templates = list_email_templates(conn, active_only=True)
        
        if not templates:
            st.info("Keine E-Mail-Vorlagen verfügbar. Erstellen Sie Vorlagen im Admin-Panel.")
        else:
            template_names = ["-- Vorlage auswählen --"] + [t['name'] for t in templates]
            selected_template_name = st.selectbox(
                "E-Mail-Vorlage",
                template_names,
                key="send_template_select"
            )
            
            if selected_template_name and selected_template_name != "-- Vorlage auswählen --":
                template = get_email_template_by_name(conn, selected_template_name)
                
                if template:
                    # Show preview with replaced placeholders
                    preview_subject = replace_placeholders(template['subject'], customer_data)
                    preview_body = replace_placeholders(template['body'], customer_data)
                    
                    st.markdown("### Vorschau")
                    st.text_input("Betreff", value=preview_subject, disabled=True)
                    st.text_area("Nachricht", value=preview_body, height=200, disabled=True)
                    
                    # Attachments selection
                    attachments = []
                    if get_customer_documents_func:
                        documents = get_customer_documents_func(customer_data['id'])
                        if documents:
                            st.markdown("### Anhänge auswählen")
                            selected_docs = st.multiselect(
                                "Dokumente aus Kundenakte",
                                options=[doc['filename'] for doc in documents],
                                key="template_attachments"
                            )
                            
                            if selected_docs:
                                for doc in documents:
                                    if doc['filename'] in selected_docs:
                                        attachments.append((doc['filename'], doc['file_data']))
                    
                    # Send button
                    if st.button(" E-Mail senden", key="send_template_button", use_container_width=True):
                        with st.spinner("Sende E-Mail..."):
                            success, message = send_email_with_template(
                                conn,
                                smtp_config,
                                template['id'],
                                customer_data,
                                attachments=attachments if attachments else None,
                                sent_by="CRM User"
                            )
                            
                            if success:
                                st.success(f" {message}")
                            else:
                                st.error(f" {message}")
    
    # Tab 2: Send custom email
    with tab_custom:
        with st.form("send_custom_email_form"):
            custom_subject = st.text_input(
                "Betreff *",
                placeholder="E-Mail-Betreff eingeben"
            )
            
            custom_body = st.text_area(
                "Nachricht *",
                height=300,
                placeholder="E-Mail-Text eingeben..."
            )
            
            custom_html = st.checkbox("Als HTML senden", value=False)
            
            # Attachments
            attachments = []
            if get_customer_documents_func:
                documents = get_customer_documents_func(customer_data['id'])
                if documents:
                    selected_docs = st.multiselect(
                        "Anhänge aus Kundenakte",
                        options=[doc['filename'] for doc in documents],
                        key="custom_attachments"
                    )
                    
                    if selected_docs:
                        for doc in documents:
                            if doc['filename'] in selected_docs:
                                attachments.append((doc['filename'], doc['file_data']))
            
            submit_custom = st.form_submit_button(" E-Mail senden", use_container_width=True)
        
        if submit_custom:
            if not custom_subject or not custom_body:
                st.error("Bitte füllen Sie Betreff und Nachricht aus!")
            else:
                with st.spinner("Sende E-Mail..."):
                    success, message = send_email(
                        smtp_config,
                        recipient_email=customer_data.get('email', ''),
                        subject=custom_subject,
                        body=custom_body,
                        html=custom_html,
                        attachments=attachments if attachments else None
                    )
                    
                    if success:
                        # Save to history
                        save_email_to_history(
                            conn,
                            customer_id=customer_data['id'],
                            recipient_email=customer_data.get('email', ''),
                            subject=custom_subject,
                            body=custom_body,
                            status='sent',
                            sent_by="CRM User"
                        )
                        st.success(f" {message}")
                    else:
                        # Save failed attempt to history
                        save_email_to_history(
                            conn,
                            customer_id=customer_data['id'],
                            recipient_email=customer_data.get('email', ''),
                            subject=custom_subject,
                            body=custom_body,
                            status='failed',
                            error_message=message,
                            sent_by="CRM User"
                        )
                        st.error(f" {message}")


# ============================================================================
# Email History UI (for Customer Profile)
# ============================================================================

def render_email_history_ui(conn: sqlite3.Connection, customer_id: int):
    """Render email history for a customer"""
    
    st.subheader(" E-Mail-Historie")
    
    # Ensure tables exist
    ensure_email_tables(conn)
    
    # Get email history
    history = get_email_history_for_customer(conn, customer_id)
    
    if not history:
        st.info("Noch keine E-Mails an diesen Kunden versendet.")
    else:
        for email in history:
            status_icon = "" if email['status'] == 'sent' else ""
            
            with st.expander(f"{status_icon} {email['subject']} - {email['sent_at']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**An:** {email['recipient_email']}")
                    st.markdown(f"**Betreff:** {email['subject']}")
                    st.markdown(f"**Status:** {email['status']}")
                    st.markdown(f"**Gesendet am:** {email['sent_at']}")
                    
                    if email.get('sent_by'):
                        st.markdown(f"**Gesendet von:** {email['sent_by']}")
                    
                    if email.get('error_message'):
                        st.error(f"**Fehler:** {email['error_message']}")
                    
                    st.markdown("**Nachricht:**")
                    st.text_area(
                        "Body",
                        value=email['body'],
                        height=150,
                        disabled=True,
                        key=f"history_{email['id']}"
                    )
                
                with col2:
                    if email.get('attachments'):
                        st.markdown("**Anhänge:**")
                        import json
                        try:
                            attachments = json.loads(email['attachments'])
                            for att in attachments:
                                st.text(f" {att}")
                        except:
                            st.text(" Anhänge vorhanden")


# ============================================================================
# Initialize Default Templates
# ============================================================================

def initialize_default_email_templates(conn: sqlite3.Connection):
    """Initialize default email templates if none exist"""
    ensure_email_tables(conn)
    
    templates = list_email_templates(conn, active_only=True)
    
    if not templates:
        create_default_templates(conn)
