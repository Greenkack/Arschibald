# crm/features/contract_ui.py
"""
Streamlit UI für Vertrags- und Garantieverwaltung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
from datetime import datetime, timedelta
from database import get_db_connection
from crm.features import contract_manager


def render_contract_management_ui():
    """Hauptfunktion für die Vertrags- und Garantieverwaltung UI."""
    st.header("📋 Vertrags- und Garantieverwaltung")
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs([
        "Verträge",
        "🛡️ Garantien",
        "⏰ Erinnerungen",
        "Übersicht"
    ])
    
    with tab1:
        render_contracts_tab()
    
    with tab2:
        render_warranties_tab()
    
    with tab3:
        render_reminders_tab()
    
    with tab4:
        render_overview_tab()


def render_contracts_tab():
    """Rendert den Verträge-Tab."""
    st.subheader("Verträge")
    
    # Action Buttons
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        if st.button("➕ Neuer Vertrag", use_container_width=True):
            st.session_state['show_contract_form'] = True
    with col2:
        if st.button("🔄 Aktualisieren", use_container_width=True):
            st.rerun()
    
    # Neuer Vertrag Formular
    if st.session_state.get('show_contract_form', False):
        render_contract_form()
    
    # Filter
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["Alle", "active", "expired", "cancelled"],
            key="contract_status_filter"
        )
    
    with col2:
        conn = get_db_connection()
        if conn:
            contract_types = contract_manager.get_contract_types(conn)
            conn.close()
            type_filter = st.selectbox(
                "Vertragstyp",
                ["Alle"] + contract_types,
                key="contract_type_filter"
            )
        else:
            type_filter = "Alle"
    
    # Verträge laden und anzeigen
    conn = get_db_connection()
    if conn:
        status = None if status_filter == "Alle" else status_filter
        contract_type = None if type_filter == "Alle" else type_filter
        
        contracts = contract_manager.get_all_contracts(conn, status, contract_type)
        conn.close()
        
        if contracts:
            st.markdown(f"**{len(contracts)} Verträge gefunden**")
            
            for contract in contracts:
                render_contract_card(contract)
        else:
            st.info("Keine Verträge gefunden.")
    else:
        st.error("Datenbankverbindung fehlgeschlagen.")


def render_contract_form(contract_id: int | None = None):
    """Rendert das Formular zum Erstellen/Bearbeiten eines Vertrags."""
    
    # Lade bestehenden Vertrag wenn ID gegeben
    existing_contract = None
    if contract_id:
        conn = get_db_connection()
        if conn:
            existing_contract = contract_manager.get_contract_by_id(conn, contract_id)
            conn.close()
    
    with st.form("contract_form"):
        st.subheader("Vertrag erstellen" if not contract_id else "Vertrag bearbeiten")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Kunde auswählen (vereinfacht - in Praxis aus DB laden)
            customer_id = st.number_input(
                "Kunden-ID *",
                min_value=1,
                value=existing_contract['customer_id'] if existing_contract else 1
            )
            
            contract_type = st.selectbox(
                "Vertragstyp *",
                ["Wartungsvertrag", "Kaufvertrag", "Mietvertrag", "Servicevertrag", "Sonstiges"],
                index=0 if not existing_contract else 
                      ["Wartungsvertrag", "Kaufvertrag", "Mietvertrag", "Servicevertrag", "Sonstiges"].index(
                          existing_contract.get('contract_type', 'Wartungsvertrag')
                      ) if existing_contract.get('contract_type') in 
                      ["Wartungsvertrag", "Kaufvertrag", "Mietvertrag", "Servicevertrag", "Sonstiges"] else 4
            )
            
            title = st.text_input(
                "Titel *",
                value=existing_contract['title'] if existing_contract else ""
            )
            
            contract_number = st.text_input(
                "Vertragsnummer",
                value=existing_contract.get('contract_number', '') if existing_contract else ""
            )
        
        with col2:
            project_id = st.number_input(
                "Projekt-ID (optional)",
                min_value=0,
                value=existing_contract.get('project_id', 0) if existing_contract else 0
            )
            if project_id == 0:
                project_id = None
            
            status = st.selectbox(
                "Status",
                ["active", "expired", "cancelled"],
                index=0 if not existing_contract else 
                      ["active", "expired", "cancelled"].index(existing_contract.get('status', 'active'))
            )
            
            value = st.number_input(
                "Vertragswert (EUR)",
                min_value=0.0,
                value=float(existing_contract.get('value', 0.0)) if existing_contract and existing_contract.get('value') else 0.0
            )
            
            renewal_type = st.selectbox(
                "Verlängerungstyp",
                ["Keine", "Automatisch", "Auf Anfrage"],
                index=0
            )
        
        # Datumsfelder
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Startdatum *",
                value=datetime.strptime(existing_contract['start_date'], '%Y-%m-%d').date() 
                      if existing_contract and existing_contract.get('start_date') 
                      else datetime.now().date()
            )
        
        with col2:
            has_end_date = st.checkbox(
                "Enddatum festlegen",
                value=bool(existing_contract and existing_contract.get('end_date'))
            )
            if has_end_date:
                end_date = st.date_input(
                    "Enddatum",
                    value=datetime.strptime(existing_contract['end_date'], '%Y-%m-%d').date()
                          if existing_contract and existing_contract.get('end_date')
                          else (datetime.now() + timedelta(days=365)).date()
                )
            else:
                end_date = None
        
        description = st.text_area(
            "Beschreibung",
            value=existing_contract.get('description', '') if existing_contract else ""
        )
        
        notes = st.text_area(
            "Notizen",
            value=existing_contract.get('notes', '') if existing_contract else ""
        )
        
        # Submit Button
        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("💾 Speichern", use_container_width=True)
        with col2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state['show_contract_form'] = False
                st.rerun()
        
        if submitted:
            if not title or not customer_id:
                st.error("Bitte füllen Sie alle Pflichtfelder aus.")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        if contract_id:
                            # Update
                            success = contract_manager.update_contract(
                                conn, contract_id,
                                customer_id=customer_id,
                                project_id=project_id,
                                contract_type=contract_type,
                                contract_number=contract_number if contract_number else None,
                                title=title,
                                description=description if description else None,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                end_date=end_date.strftime('%Y-%m-%d') if end_date else None,
                                value=value if value > 0 else None,
                                status=status,
                                renewal_type=renewal_type if renewal_type != "Keine" else None,
                                notes=notes if notes else None,
                                updated_by="System"
                            )
                            if success:
                                st.success("Vertrag erfolgreich aktualisiert!")
                                st.session_state['show_contract_form'] = False
                                st.rerun()
                            else:
                                st.error("Fehler beim Aktualisieren des Vertrags.")
                        else:
                            # Create
                            new_id = contract_manager.create_contract(
                                conn,
                                customer_id=customer_id,
                                contract_type=contract_type,
                                title=title,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                end_date=end_date.strftime('%Y-%m-%d') if end_date else None,
                                project_id=project_id,
                                contract_number=contract_number if contract_number else None,
                                description=description if description else None,
                                value=value if value > 0 else None,
                                status=status,
                                renewal_type=renewal_type if renewal_type != "Keine" else None,
                                notes=notes if notes else None,
                                created_by="System"
                            )
                            if new_id:
                                st.success(f"Vertrag erfolgreich erstellt! (ID: {new_id})")
                                st.session_state['show_contract_form'] = False
                                st.rerun()
                            else:
                                st.error("Fehler beim Erstellen des Vertrags.")
                    finally:
                        conn.close()
                else:
                    st.error("Datenbankverbindung fehlgeschlagen.")



def render_contract_card(contract: dict):
    """Rendert eine Vertragskarte."""
    with st.expander(f"{contract['title']} - {contract['contract_type']}", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**Vertragsnummer:** {contract.get('contract_number', 'N/A')}")
            st.markdown(f"**Kunde:** ID {contract['customer_id']}")
            st.markdown(f"**Status:** {contract['status']}")
        
        with col2:
            st.markdown(f"**Start:** {contract['start_date']}")
            st.markdown(f"**Ende:** {contract.get('end_date', 'Unbefristet')}")
            if contract.get('value'):
                st.markdown(f"**Wert:** {contract['value']:.2f} {contract.get('currency', 'EUR')}")
        
        with col3:
            if st.button("✏️ Bearbeiten", key=f"edit_contract_{contract['id']}", use_container_width=True):
                st.session_state[f'edit_contract_{contract["id"]}'] = True
                st.rerun()
            
            if st.button("Löschen", key=f"delete_contract_{contract['id']}", use_container_width=True):
                conn = get_db_connection()
                if conn:
                    if contract_manager.delete_contract(conn, contract['id']):
                        st.success("Vertrag gelöscht!")
                        st.rerun()
                    conn.close()
        
        if contract.get('description'):
            st.markdown(f"**Beschreibung:** {contract['description']}")
        
        if contract.get('notes'):
            st.markdown(f"**Notizen:** {contract['notes']}")
        
        # Bearbeitungsformular anzeigen wenn aktiviert
        if st.session_state.get(f'edit_contract_{contract["id"]}', False):
            render_contract_form(contract['id'])
            st.session_state[f'edit_contract_{contract["id"]}'] = False


def render_warranties_tab():
    """Rendert den Garantien-Tab."""
    st.subheader("Garantien")
    
    # Action Buttons
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        if st.button("➕ Neue Garantie", use_container_width=True):
            st.session_state['show_warranty_form'] = True
    with col2:
        if st.button("🔄 Aktualisieren", key="refresh_warranties", use_container_width=True):
            st.rerun()
    
    # Neue Garantie Formular
    if st.session_state.get('show_warranty_form', False):
        render_warranty_form()
    
    # Filter
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["Alle", "active", "expired"],
            key="warranty_status_filter"
        )
    
    with col2:
        conn = get_db_connection()
        if conn:
            warranty_types = contract_manager.get_warranty_types(conn)
            conn.close()
            type_filter = st.selectbox(
                "Garantietyp",
                ["Alle"] + warranty_types,
                key="warranty_type_filter"
            )
        else:
            type_filter = "Alle"
    
    # Garantien laden und anzeigen
    conn = get_db_connection()
    if conn:
        status = None if status_filter == "Alle" else status_filter
        warranty_type = None if type_filter == "Alle" else type_filter
        
        warranties = contract_manager.get_all_warranties(conn, status, warranty_type)
        conn.close()
        
        if warranties:
            st.markdown(f"**{len(warranties)} Garantien gefunden**")
            
            for warranty in warranties:
                render_warranty_card(warranty)
        else:
            st.info("Keine Garantien gefunden.")
    else:
        st.error("Datenbankverbindung fehlgeschlagen.")



def render_warranty_form(warranty_id: int | None = None):
    """Rendert das Formular zum Erstellen/Bearbeiten einer Garantie."""
    
    # Lade bestehende Garantie wenn ID gegeben
    existing_warranty = None
    if warranty_id:
        conn = get_db_connection()
        if conn:
            existing_warranty = contract_manager.get_warranty_by_id(conn, warranty_id)
            conn.close()
    
    with st.form("warranty_form"):
        st.subheader("Garantie erstellen" if not warranty_id else "Garantie bearbeiten")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_id = st.number_input(
                "Kunden-ID *",
                min_value=1,
                value=existing_warranty['customer_id'] if existing_warranty else 1
            )
            
            project_id = st.number_input(
                "Projekt-ID *",
                min_value=1,
                value=existing_warranty['project_id'] if existing_warranty else 1
            )
            
            warranty_type = st.selectbox(
                "Garantietyp *",
                ["Produktgarantie", "Leistungsgarantie", "Herstellergarantie", "Erweiterte Garantie"],
                index=0 if not existing_warranty else
                      ["Produktgarantie", "Leistungsgarantie", "Herstellergarantie", "Erweiterte Garantie"].index(
                          existing_warranty.get('warranty_type', 'Produktgarantie')
                      ) if existing_warranty.get('warranty_type') in
                      ["Produktgarantie", "Leistungsgarantie", "Herstellergarantie", "Erweiterte Garantie"] else 0
            )
            
            title = st.text_input(
                "Titel *",
                value=existing_warranty['title'] if existing_warranty else ""
            )
        
        with col2:
            start_date = st.date_input(
                "Startdatum *",
                value=datetime.strptime(existing_warranty['start_date'], '%Y-%m-%d').date()
                      if existing_warranty and existing_warranty.get('start_date')
                      else datetime.now().date()
            )
            
            duration_months = st.number_input(
                "Laufzeit (Monate) *",
                min_value=1,
                max_value=600,
                value=existing_warranty['duration_months'] if existing_warranty else 24
            )
            
            status = st.selectbox(
                "Status",
                ["active", "expired"],
                index=0 if not existing_warranty else
                      ["active", "expired"].index(existing_warranty.get('status', 'active'))
            )
            
            provider = st.text_input(
                "Garantiegeber",
                value=existing_warranty.get('provider', '') if existing_warranty else ""
            )
        
        description = st.text_area(
            "Beschreibung",
            value=existing_warranty.get('description', '') if existing_warranty else ""
        )
        
        terms = st.text_area(
            "Garantiebedingungen",
            value=existing_warranty.get('terms', '') if existing_warranty else ""
        )
        
        coverage_details = st.text_area(
            "Abdeckungsdetails",
            value=existing_warranty.get('coverage_details', '') if existing_warranty else ""
        )
        
        notes = st.text_area(
            "Notizen",
            value=existing_warranty.get('notes', '') if existing_warranty else ""
        )
        
        # Submit Button
        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("💾 Speichern", use_container_width=True)
        with col2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state['show_warranty_form'] = False
                st.rerun()
        
        if submitted:
            if not title or not customer_id or not project_id:
                st.error("Bitte füllen Sie alle Pflichtfelder aus.")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        if warranty_id:
                            # Update
                            success = contract_manager.update_warranty(
                                conn, warranty_id,
                                customer_id=customer_id,
                                project_id=project_id,
                                warranty_type=warranty_type,
                                title=title,
                                description=description if description else None,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                duration_months=duration_months,
                                terms=terms if terms else None,
                                coverage_details=coverage_details if coverage_details else None,
                                provider=provider if provider else None,
                                status=status,
                                notes=notes if notes else None,
                                updated_by="System"
                            )
                            if success:
                                st.success("Garantie erfolgreich aktualisiert!")
                                st.session_state['show_warranty_form'] = False
                                st.rerun()
                            else:
                                st.error("Fehler beim Aktualisieren der Garantie.")
                        else:
                            # Create
                            new_id = contract_manager.create_warranty(
                                conn,
                                project_id=project_id,
                                customer_id=customer_id,
                                warranty_type=warranty_type,
                                title=title,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                duration_months=duration_months,
                                description=description if description else None,
                                terms=terms if terms else None,
                                coverage_details=coverage_details if coverage_details else None,
                                provider=provider if provider else None,
                                status=status,
                                notes=notes if notes else None,
                                created_by="System"
                            )
                            if new_id:
                                st.success(f"Garantie erfolgreich erstellt! (ID: {new_id})")
                                st.session_state['show_warranty_form'] = False
                                st.rerun()
                            else:
                                st.error("Fehler beim Erstellen der Garantie.")
                    finally:
                        conn.close()
                else:
                    st.error("Datenbankverbindung fehlgeschlagen.")



def render_warranty_card(warranty: dict):
    """Rendert eine Garantiekarte."""
    with st.expander(f"🛡️ {warranty['title']} - {warranty['warranty_type']}", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**Projekt:** ID {warranty['project_id']}")
            st.markdown(f"**Kunde:** ID {warranty['customer_id']}")
            st.markdown(f"**Status:** {warranty['status']}")
            if warranty.get('provider'):
                st.markdown(f"**Garantiegeber:** {warranty['provider']}")
        
        with col2:
            st.markdown(f"**Start:** {warranty['start_date']}")
            st.markdown(f"**Ende:** {warranty.get('end_date', 'N/A')}")
            st.markdown(f"**Laufzeit:** {warranty['duration_months']} Monate")
        
        with col3:
            if st.button("✏️ Bearbeiten", key=f"edit_warranty_{warranty['id']}", use_container_width=True):
                st.session_state[f'edit_warranty_{warranty["id"]}'] = True
                st.rerun()
            
            if st.button("Löschen", key=f"delete_warranty_{warranty['id']}", use_container_width=True):
                conn = get_db_connection()
                if conn:
                    if contract_manager.delete_warranty(conn, warranty['id']):
                        st.success("Garantie gelöscht!")
                        st.rerun()
                    conn.close()
        
        if warranty.get('description'):
            st.markdown(f"**Beschreibung:** {warranty['description']}")
        
        if warranty.get('terms'):
            with st.expander("Garantiebedingungen"):
                st.markdown(warranty['terms'])
        
        if warranty.get('coverage_details'):
            with st.expander("Abdeckungsdetails"):
                st.markdown(warranty['coverage_details'])
        
        if warranty.get('notes'):
            st.markdown(f"**Notizen:** {warranty['notes']}")
        
        # Bearbeitungsformular anzeigen wenn aktiviert
        if st.session_state.get(f'edit_warranty_{warranty["id"]}', False):
            render_warranty_form(warranty['id'])
            st.session_state[f'edit_warranty_{warranty["id"]}'] = False


def render_reminders_tab():
    """Rendert den Erinnerungen-Tab."""
    st.subheader("⏰ Ablauf-Erinnerungen")
    
    # Zeitraum auswählen
    days_ahead = st.slider(
        "Erinnerungen für die nächsten X Tage anzeigen",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    
    conn = get_db_connection()
    if conn:
        # Fällige Erinnerungen
        reminders = contract_manager.get_pending_reminders(conn, days_ahead)
        
        # Ablaufende Verträge
        expiring_contracts = contract_manager.get_expiring_contracts(conn, days_ahead)
        
        # Ablaufende Garantien
        expiring_warranties = contract_manager.get_expiring_warranties(conn, days_ahead)
        
        conn.close()
        
        # Anzeige
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### Ablaufende Verträge ({len(expiring_contracts)})")
            if expiring_contracts:
                for contract in expiring_contracts:
                    days_until = (datetime.strptime(contract['end_date'], '%Y-%m-%d') - datetime.now()).days
                    color = "🔴" if days_until <= 7 else "🟡" if days_until <= 14 else "🟢"
                    
                    with st.expander(f"{color} {contract['title']} - {days_until} Tage"):
                        st.markdown(f"**Vertragstyp:** {contract['contract_type']}")
                        st.markdown(f"**Enddatum:** {contract['end_date']}")
                        st.markdown(f"**Kunde:** ID {contract['customer_id']}")
                        
                        if st.button("Details anzeigen", key=f"contract_detail_{contract['id']}"):
                            st.session_state[f'show_contract_{contract["id"]}'] = True
            else:
                st.info("Keine ablaufenden Verträge in diesem Zeitraum.")
        
        with col2:
            st.markdown(f"### 🛡️ Ablaufende Garantien ({len(expiring_warranties)})")
            if expiring_warranties:
                for warranty in expiring_warranties:
                    days_until = (datetime.strptime(warranty['end_date'], '%Y-%m-%d') - datetime.now()).days
                    color = "🔴" if days_until <= 7 else "🟡" if days_until <= 14 else "🟢"
                    
                    with st.expander(f"{color} {warranty['title']} - {days_until} Tage"):
                        st.markdown(f"**Garantietyp:** {warranty['warranty_type']}")
                        st.markdown(f"**Enddatum:** {warranty['end_date']}")
                        st.markdown(f"**Projekt:** ID {warranty['project_id']}")
                        
                        if st.button("Details anzeigen", key=f"warranty_detail_{warranty['id']}"):
                            st.session_state[f'show_warranty_{warranty["id"]}'] = True
            else:
                st.info("Keine ablaufenden Garantien in diesem Zeitraum.")
    else:
        st.error("Datenbankverbindung fehlgeschlagen.")


def render_overview_tab():
    """Rendert den Übersichts-Tab."""
    st.subheader("Übersicht")
    
    conn = get_db_connection()
    if conn:
        # Statistiken laden
        contract_stats = contract_manager.get_contract_statistics(conn)
        warranty_stats = contract_manager.get_warranty_statistics(conn)
        conn.close()
        
        # Vertrags-Statistiken
        st.markdown("### Verträge")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt", contract_stats['total'])
        with col2:
            st.metric("Aktiv", contract_stats['by_status'].get('active', 0))
        with col3:
            st.metric("Ablaufend (30 Tage)", contract_stats['expiring_30_days'])
        with col4:
            st.metric("Abgelaufen", contract_stats['expired'])
        
        if contract_stats['total_value'] > 0:
            st.metric("Gesamtwert aktiver Verträge", f"{contract_stats['total_value']:,.2f} EUR")
        
        # Verträge nach Typ
        if contract_stats['by_type']:
            st.markdown("**Verträge nach Typ:**")
            for contract_type, count in contract_stats['by_type'].items():
                st.markdown(f"- {contract_type}: {count}")
        
        st.markdown("---")
        
        # Garantie-Statistiken
        st.markdown("### 🛡️ Garantien")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt", warranty_stats['total'])
        with col2:
            st.metric("Aktiv", warranty_stats['by_status'].get('active', 0))
        with col3:
            st.metric("Ablaufend (30 Tage)", warranty_stats['expiring_30_days'])
        with col4:
            st.metric("Abgelaufen", warranty_stats['expired'])
        
        # Garantien nach Typ
        if warranty_stats['by_type']:
            st.markdown("**Garantien nach Typ:**")
            for warranty_type, count in warranty_stats['by_type'].items():
                st.markdown(f"- {warranty_type}: {count}")
    else:
        st.error("Datenbankverbindung fehlgeschlagen.")


# Hilfsfunktion für Integration in CRM
def show_customer_contracts_warranties(customer_id: int):
    """Zeigt Verträge und Garantien eines Kunden an.
    
    Diese Funktion kann in der Kundendetailansicht verwendet werden.
    """
    st.markdown("### 📋 Verträge & Garantien")
    
    conn = get_db_connection()
    if conn:
        # Verträge laden
        contracts = contract_manager.get_contracts_by_customer(conn, customer_id)
        
        # Garantien laden
        warranties = contract_manager.get_warranties_by_customer(conn, customer_id)
        
        conn.close()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Verträge ({len(contracts)})**")
            if contracts:
                for contract in contracts:
                    status_icon = "" if contract['status'] == 'active' else ""
                    st.markdown(f"{status_icon} {contract['title']} ({contract['contract_type']})")
            else:
                st.info("Keine Verträge vorhanden.")
        
        with col2:
            st.markdown(f"**Garantien ({len(warranties)})**")
            if warranties:
                for warranty in warranties:
                    status_icon = "" if warranty['status'] == 'active' else ""
                    st.markdown(f"{status_icon} {warranty['title']} ({warranty['warranty_type']})")
            else:
                st.info("Keine Garantien vorhanden.")
    else:
        st.error("Datenbankverbindung fehlgeschlagen.")
