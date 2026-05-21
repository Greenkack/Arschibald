# crm/features/template_ui.py
"""
UI-Komponenten für Dokument-Vorlagen-Management

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
from datetime import datetime
from typing import Any
from database import get_db_connection
from crm.features.template_manager import (
    create_template,
    get_template_by_id,
    get_all_templates,
    update_template,
    delete_template,
    get_template_versions,
    restore_template_version,
    preview_template,
    get_template_categories,
    get_template_statistics,
    duplicate_template,
    extract_placeholders,
    validate_placeholders
)


# ============================================================================
# AVAILABLE PLACEHOLDERS
# ============================================================================

# Standard-Platzhalter die im System verfügbar sind
AVAILABLE_PLACEHOLDERS = {
    # Kundendaten
    'customer_name': 'Kundenname',
    'customer_email': 'Kunden-E-Mail',
    'customer_phone': 'Kunden-Telefon',
    'customer_address': 'Kundenadresse',
    'customer_city': 'Kundenstadt',
    'customer_zip': 'Kunden-PLZ',
    
    # Projektdaten
    'project_name': 'Projektname',
    'project_value': 'Projektwert',
    'project_status': 'Projektstatus',
    'project_start_date': 'Projektstart',
    'project_end_date': 'Projektende',
    
    # Berechnungsdaten
    'system_size_kwp': 'Anlagengröße (kWp)',
    'annual_production_kwh': 'Jahresertrag (kWh)',
    'investment_total_eur': 'Gesamtinvestition (€)',
    'payback_period_years': 'Amortisationszeit (Jahre)',
    'module_manufacturer': 'Modulhersteller',
    'module_model': 'Modulmodell',
    'inverter_manufacturer': 'Wechselrichterhersteller',
    'inverter_model': 'Wechselrichtermodell',
    
    # Firmendaten
    'company_name': 'Firmenname',
    'company_address': 'Firmenadresse',
    'company_phone': 'Firmentelefon',
    'company_email': 'Firmen-E-Mail',
    'company_website': 'Firmen-Website',
    
    # Datum/Zeit
    'current_date': 'Aktuelles Datum',
    'current_year': 'Aktuelles Jahr',
    
    # Benutzer
    'user_name': 'Benutzername',
    'user_email': 'Benutzer-E-Mail'
}


# ============================================================================
# TEMPLATE LIST VIEW
# ============================================================================

def render_template_list() -> None:
    """Rendert die Template-Übersicht."""
    st.subheader("Dokument-Vorlagen")
    
    conn = get_db_connection()
    if not conn:
        st.error("Datenbankverbindung fehlgeschlagen")
        return
    
    try:
        # Filter
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            categories = ['Alle'] + get_template_categories(conn)
            selected_category = st.selectbox(
                "Kategorie",
                categories,
                key="template_category_filter"
            )
        
        with col2:
            show_inactive = st.checkbox("Inaktive anzeigen", key="show_inactive_templates")
        
        with col3:
            if st.button(" Neue Vorlage", key="new_template_btn", use_container_width=True):
                st.session_state['template_action'] = 'create'
                st.rerun()
        
        # Lade Templates
        category_filter = None if selected_category == 'Alle' else selected_category
        templates = get_all_templates(conn, category=category_filter, active_only=not show_inactive)
        
        if not templates:
            st.info("Keine Vorlagen gefunden. Erstellen Sie Ihre erste Vorlage!")
            return
        
        # Statistiken
        stats = get_template_statistics(conn)
        col1, col2, col3 = st.columns(3)
        col1.metric("Gesamt", stats['total'])
        col2.metric("Aktiv", stats['active'])
        col3.metric("Inaktiv", stats['inactive'])
        
        st.divider()
        
        # Template-Liste
        for template in templates:
            with st.expander(
                f"{'' if template['is_active'] else ''} {template['name']} ({template['category']})",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if template.get('description'):
                        st.write(template['description'])
                    
                    st.caption(f"Version: {template['version']} | "
                             f"Erstellt: {template['created_at'][:10]} | "
                             f"Platzhalter: {len(template.get('placeholders', []))}")
                    
                    # Platzhalter anzeigen
                    if template.get('placeholders'):
                        with st.expander("Platzhalter", expanded=False):
                            for ph in template['placeholders']:
                                desc = AVAILABLE_PLACEHOLDERS.get(ph, 'Unbekannt')
                                st.code(f"{{{{{ph}}}}} - {desc}")
                
                with col2:
                    if st.button(" Bearbeiten", key=f"edit_template_{template['id']}", use_container_width=True):
                        st.session_state['template_action'] = 'edit'
                        st.session_state['template_id'] = template['id']
                        st.rerun()
                    
                    if st.button(" Vorschau", key=f"preview_template_{template['id']}", use_container_width=True):
                        st.session_state['template_action'] = 'preview'
                        st.session_state['template_id'] = template['id']
                        st.rerun()
                    
                    if st.button(" Duplizieren", key=f"duplicate_template_{template['id']}", use_container_width=True):
                        st.session_state['template_action'] = 'duplicate'
                        st.session_state['template_id'] = template['id']
                        st.rerun()
                    
                    if st.button("Löschen", key=f"delete_template_{template['id']}", use_container_width=True):
                        if st.session_state.get(f'confirm_delete_{template["id"]}'):
                            if delete_template(conn, template['id']):
                                st.success("Vorlage gelöscht!")
                                st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{template["id"]}'] = True
                            st.warning("Nochmal klicken zum Bestätigen")
    
    finally:
        conn.close()


# ============================================================================
# TEMPLATE EDITOR
# ============================================================================

def render_template_editor(template_id: int | None = None) -> None:
    """Rendert den Template-Editor.
    
    Args:
        template_id: ID des zu bearbeitenden Templates (None für neu)
    """
    conn = get_db_connection()
    if not conn:
        st.error("Datenbankverbindung fehlgeschlagen")
        return
    
    try:
        is_edit = template_id is not None
        template = get_template_by_id(conn, template_id) if is_edit else None
        
        st.subheader(" Vorlage bearbeiten" if is_edit else " Neue Vorlage erstellen")
        
        # Zurück-Button
        if st.button("← Zurück zur Übersicht"):
            st.session_state.pop('template_action', None)
            st.session_state.pop('template_id', None)
            st.rerun()
        
        st.divider()
        
        # Formular
        with st.form("template_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Vorlagen-Name *",
                    value=template['name'] if template else "",
                    placeholder="z.B. Standard-Angebot"
                )
            
            with col2:
                categories = ['Angebot', 'Vertrag', 'Brief', 'Rechnung', 'Sonstiges']
                category = st.selectbox(
                    "Kategorie *",
                    categories,
                    index=categories.index(template['category']) if template and template['category'] in categories else 0
                )
            
            description = st.text_area(
                "Beschreibung",
                value=template.get('description', '') if template else "",
                placeholder="Kurze Beschreibung der Vorlage"
            )
            
            # Platzhalter-Hilfe
            with st.expander(" Verfügbare Platzhalter", expanded=False):
                st.write("Verwenden Sie diese Platzhalter in Ihrer Vorlage:")
                cols = st.columns(2)
                for i, (key, desc) in enumerate(AVAILABLE_PLACEHOLDERS.items()):
                    with cols[i % 2]:
                        st.code(f"{{{{{key}}}}}")
                        st.caption(desc)
            
            content = st.text_area(
                "Vorlagen-Inhalt *",
                value=template['content'] if template else "",
                height=400,
                placeholder="Geben Sie hier den Vorlagen-Inhalt ein. Verwenden Sie {{platzhalter}} für dynamische Werte.",
                help="Verwenden Sie {{platzhalter_name}} für dynamische Werte"
            )
            
            # Platzhalter-Validierung
            if content:
                used_placeholders = extract_placeholders(content)
                validation = validate_placeholders(content, list(AVAILABLE_PLACEHOLDERS.keys()))
                
                if validation['invalid']:
                    st.warning(f"Unbekannte Platzhalter: {', '.join(validation['invalid'])}")
                
                if validation['valid']:
                    st.success(f"Verwendete Platzhalter: {', '.join(validation['valid'])}")
            
            if is_edit:
                change_note = st.text_input(
                    "Änderungsnotiz",
                    placeholder="Was wurde geändert?"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                is_active = st.checkbox(
                    "Vorlage aktiv",
                    value=template['is_active'] if template else True
                )
            
            submitted = st.form_submit_button(
                " Speichern",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if not name or not category or not content:
                    st.error("Bitte füllen Sie alle Pflichtfelder aus!")
                else:
                    user = st.session_state.get('current_user', 'System')
                    
                    if is_edit:
                        success = update_template(
                            conn,
                            template_id,
                            name=name,
                            category=category,
                            content=content,
                            description=description,
                            is_active=is_active,
                            updated_by=user,
                            change_note=change_note if 'change_note' in locals() else None
                        )
                        if success:
                            st.success("Vorlage aktualisiert!")
                            st.session_state.pop('template_action', None)
                            st.session_state.pop('template_id', None)
                            st.rerun()
                        else:
                            st.error("Fehler beim Aktualisieren der Vorlage")
                    else:
                        new_id = create_template(
                            conn,
                            name=name,
                            category=category,
                            content=content,
                            description=description,
                            created_by=user
                        )
                        if new_id:
                            st.success("Vorlage erstellt!")
                            st.session_state.pop('template_action', None)
                            st.rerun()
                        else:
                            st.error("Fehler beim Erstellen der Vorlage")
        
        # Versionshistorie (nur bei Bearbeitung)
        if is_edit and template:
            st.divider()
            st.subheader(" Versionshistorie")
            
            versions = get_template_versions(conn, template_id)
            if versions:
                for version in versions:
                    with st.expander(
                        f"Version {version['version']} - {version['created_at'][:16]}",
                        expanded=version['version'] == template['version']
                    ):
                        st.caption(f"Erstellt von: {version.get('created_by', 'Unbekannt')}")
                        if version.get('change_note'):
                            st.info(version['change_note'])
                        
                        st.code(version['content'][:200] + "..." if len(version['content']) > 200 else version['content'])
                        
                        if version['version'] != template['version']:
                            if st.button(
                                " Diese Version wiederherstellen",
                                key=f"restore_version_{version['version']}"
                            ):
                                if restore_template_version(conn, template_id, version['version'], user):
                                    st.success("Version wiederhergestellt!")
                                    st.rerun()
    
    finally:
        conn.close()


# ============================================================================
# TEMPLATE PREVIEW
# ============================================================================

def render_template_preview(template_id: int) -> None:
    """Rendert die Template-Vorschau.
    
    Args:
        template_id: Template-ID
    """
    conn = get_db_connection()
    if not conn:
        st.error("Datenbankverbindung fehlgeschlagen")
        return
    
    try:
        template = get_template_by_id(conn, template_id)
        if not template:
            st.error("Vorlage nicht gefunden")
            return
        
        st.subheader(f" Vorschau: {template['name']}")
        
        # Zurück-Button
        if st.button("← Zurück zur Übersicht"):
            st.session_state.pop('template_action', None)
            st.session_state.pop('template_id', None)
            st.rerun()
        
        st.divider()
        
        # Beispieldaten eingeben
        st.write("**Beispieldaten für Vorschau:**")
        
        sample_data = {}
        if template.get('placeholders'):
            cols = st.columns(2)
            for i, placeholder in enumerate(template['placeholders']):
                with cols[i % 2]:
                    desc = AVAILABLE_PLACEHOLDERS.get(placeholder, placeholder)
                    sample_data[placeholder] = st.text_input(
                        desc,
                        value=f"[{placeholder}]",
                        key=f"preview_{placeholder}"
                    )
        
        st.divider()
        
        # Vorschau rendern
        st.write("**Vorschau:**")
        preview_content = preview_template(conn, template_id, sample_data)
        
        if preview_content:
            st.text_area(
                "Gerenderter Inhalt",
                value=preview_content,
                height=400,
                disabled=True
            )
        else:
            st.error("Fehler beim Rendern der Vorschau")
    
    finally:
        conn.close()


# ============================================================================
# TEMPLATE DUPLICATE
# ============================================================================

def render_template_duplicate(template_id: int) -> None:
    """Rendert das Duplikat-Formular.
    
    Args:
        template_id: ID des zu duplizierenden Templates
    """
    conn = get_db_connection()
    if not conn:
        st.error("Datenbankverbindung fehlgeschlagen")
        return
    
    try:
        template = get_template_by_id(conn, template_id)
        if not template:
            st.error("Vorlage nicht gefunden")
            return
        
        st.subheader(f" Vorlage duplizieren: {template['name']}")
        
        # Zurück-Button
        if st.button("← Zurück zur Übersicht"):
            st.session_state.pop('template_action', None)
            st.session_state.pop('template_id', None)
            st.rerun()
        
        st.divider()
        
        with st.form("duplicate_form"):
            new_name = st.text_input(
                "Name für neue Vorlage *",
                value=f"{template['name']} (Kopie)",
                placeholder="Neuer Name"
            )
            
            submitted = st.form_submit_button(" Duplizieren", use_container_width=True, type="primary")
            
            if submitted:
                if not new_name:
                    st.error("Bitte geben Sie einen Namen ein!")
                else:
                    user = st.session_state.get('current_user', 'System')
                    new_id = duplicate_template(conn, template_id, new_name, user)
                    
                    if new_id:
                        st.success(f"Vorlage dupliziert! (ID: {new_id})")
                        st.session_state.pop('template_action', None)
                        st.session_state.pop('template_id', None)
                        st.rerun()
                    else:
                        st.error("Fehler beim Duplizieren der Vorlage")
    
    finally:
        conn.close()


# ============================================================================
# MAIN TEMPLATE UI
# ============================================================================

def render_template_management() -> None:
    """Hauptfunktion für Template-Management UI."""
    
    # Routing basierend auf Action
    action = st.session_state.get('template_action')
    template_id = st.session_state.get('template_id')
    
    if action == 'create':
        render_template_editor()
    elif action == 'edit' and template_id:
        render_template_editor(template_id)
    elif action == 'preview' and template_id:
        render_template_preview(template_id)
    elif action == 'duplicate' and template_id:
        render_template_duplicate(template_id)
    else:
        render_template_list()
