# crm/features/call_ui.py
"""
Streamlit UI für Anruf-Protokollierung im CRM-System.

Bietet einen Dialog mit Timer, Telefonnummer-Auswahl und Notizen-Feld.
"""

import streamlit as st
from datetime import datetime, timedelta
import time
from typing import Optional, Dict, Any

try:
    from crm.features.call_manager import (
        create_call, get_call, get_customer_calls, update_call, delete_call,
        get_call_statistics, format_duration, parse_duration, CALL_DIRECTIONS,
        ensure_call_fields
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from crm.features.call_manager import (
        create_call, get_call, get_customer_calls, update_call, delete_call,
        get_call_statistics, format_duration, parse_duration, CALL_DIRECTIONS,
        ensure_call_fields
    )


def render_call_dialog(customer_id: int, customer_name: str, phone_numbers: list = None):
    """
    Rendert einen Dialog zum Protokollieren eines Anrufs mit Timer.
    
    Args:
        customer_id: ID des Kunden
        customer_name: Name des Kunden
        phone_numbers: Liste von Telefonnummern des Kunden
    """
    # Stelle sicher, dass die Felder existieren
    ensure_call_fields()
    
    st.subheader(f"📞 Anruf protokollieren - {customer_name}")
    
    # Initialisiere Session State für Timer
    if "call_timer_running" not in st.session_state:
        st.session_state.call_timer_running = False
    if "call_timer_start" not in st.session_state:
        st.session_state.call_timer_start = None
    if "call_timer_elapsed" not in st.session_state:
        st.session_state.call_timer_elapsed = 0
    
    # Anruf-Richtung
    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox(
            "Richtung",
            options=list(CALL_DIRECTIONS.keys()),
            format_func=lambda x: CALL_DIRECTIONS[x],
            key="call_direction"
        )
    
    # Telefonnummer-Auswahl
    with col2:
        if phone_numbers and len(phone_numbers) > 0:
            phone_number = st.selectbox(
                "Telefonnummer",
                options=phone_numbers,
                key="call_phone_number"
            )
        else:
            phone_number = st.text_input(
                "Telefonnummer",
                placeholder="+43 123 456789",
                key="call_phone_number"
            )
    
    # Timer-Bereich
    st.markdown("---")
    st.markdown("**⏱️ Anrufdauer**")
    
    timer_col1, timer_col2, timer_col3 = st.columns([2, 1, 1])
    
    with timer_col1:
        # Zeige aktuelle Zeit
        if st.session_state.call_timer_running:
            elapsed = int(time.time() - st.session_state.call_timer_start) + st.session_state.call_timer_elapsed
            st.markdown(f"### {format_duration(elapsed)}")
        else:
            st.markdown(f"### {format_duration(st.session_state.call_timer_elapsed)}")
    
    with timer_col2:
        if not st.session_state.call_timer_running:
            if st.button("▶️ Start", key="call_timer_start_btn", use_container_width=True):
                st.session_state.call_timer_running = True
                st.session_state.call_timer_start = time.time()
                st.rerun()
        else:
            if st.button("⏸️ Stopp", key="call_timer_stop_btn", use_container_width=True):
                st.session_state.call_timer_running = False
                st.session_state.call_timer_elapsed += int(time.time() - st.session_state.call_timer_start)
                st.session_state.call_timer_start = None
                st.rerun()
    
    with timer_col3:
        if st.button("🔄 Reset", key="call_timer_reset_btn", use_container_width=True):
            st.session_state.call_timer_running = False
            st.session_state.call_timer_start = None
            st.session_state.call_timer_elapsed = 0
            st.rerun()
    
    # Manuelle Eingabe der Dauer
    manual_duration = st.text_input(
        "Oder Dauer manuell eingeben (MM:SS oder HH:MM:SS)",
        placeholder="5:30",
        key="call_manual_duration"
    )
    
    # Notizen
    st.markdown("---")
    notes = st.text_area(
        "Notizen zum Anruf",
        placeholder="Was wurde besprochen? Nächste Schritte?",
        height=150,
        key="call_notes"
    )
    
    # Speichern-Button
    st.markdown("---")
    col_save, col_cancel = st.columns([1, 1])
    
    with col_save:
        if st.button("💾 Anruf speichern", type="primary", use_container_width=True):
            # Bestimme Dauer
            if manual_duration:
                duration = parse_duration(manual_duration)
            else:
                duration = st.session_state.call_timer_elapsed
            
            # Validierung
            if not phone_number:
                st.error("Bitte geben Sie eine Telefonnummer ein.")
                return
            
            # Speichere Anruf
            call_id = create_call(
                customer_id=customer_id,
                phone_number=phone_number,
                direction=direction,
                duration_seconds=duration,
                notes=notes,
                created_by=st.session_state.get("current_user", "System")
            )
            
            if call_id:
                st.success(f"[OK] Anruf erfolgreich protokolliert! (Dauer: {format_duration(duration)})")
                # Reset Timer
                st.session_state.call_timer_running = False
                st.session_state.call_timer_start = None
                st.session_state.call_timer_elapsed = 0
                time.sleep(1)
                st.rerun()
            else:
                st.error("[ERROR] Fehler beim Speichern des Anrufs.")
    
    with col_cancel:
        if st.button("[ERROR] Abbrechen", use_container_width=True):
            # Reset Timer
            st.session_state.call_timer_running = False
            st.session_state.call_timer_start = None
            st.session_state.call_timer_elapsed = 0
            st.rerun()
    
    # Auto-Refresh wenn Timer läuft
    if st.session_state.call_timer_running:
        time.sleep(1)
        st.rerun()


def render_call_list(customer_id: int, limit: int = 20):
    """
    Rendert eine Liste aller Anrufe eines Kunden.
    
    Args:
        customer_id: ID des Kunden
        limit: Maximale Anzahl anzuzeigender Anrufe
    """
    st.subheader("📞 Anruf-Historie")
    
    # Filter
    col1, col2 = st.columns([2, 1])
    with col1:
        direction_filter = st.selectbox(
            "Filter nach Richtung",
            options=["Alle", "incoming", "outgoing"],
            format_func=lambda x: "Alle Anrufe" if x == "Alle" else CALL_DIRECTIONS.get(x, x),
            key="call_list_direction_filter"
        )
    
    with col2:
        include_archived = st.checkbox("Archivierte anzeigen", key="call_list_include_archived")
    
    # Hole Anrufe
    direction = None if direction_filter == "Alle" else direction_filter
    calls = get_customer_calls(
        customer_id=customer_id,
        direction=direction,
        include_archived=include_archived,
        limit=limit
    )
    
    if not calls:
        st.info("Noch keine Anrufe protokolliert.")
        return
    
    # Zeige Anrufe
    for call in calls:
        with st.expander(
            f"{call['call_direction_display']} - {call['call_phone_number']} - {call['call_duration_formatted']} - {call['created_at']}"
        ):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Richtung:** {call['call_direction_display']}")
                st.markdown(f"**Telefonnummer:** {call['call_phone_number']}")
            
            with col2:
                st.markdown(f"**Dauer:** {call['call_duration_formatted']}")
                st.markdown(f"**Datum:** {call['created_at']}")
            
            with col3:
                st.markdown(f"**Erstellt von:** {call['created_by']}")
                if call['is_important']:
                    st.markdown("⭐ **Wichtig**")
            
            if call['call_notes']:
                st.markdown("**Notizen:**")
                st.markdown(call['call_notes'])
            
            # Aktionen
            action_col1, action_col2 = st.columns([1, 1])
            with action_col1:
                if st.button("[DELETE] Löschen", key=f"delete_call_{call['id']}"):
                    if delete_call(call['id']):
                        st.success("Anruf gelöscht!")
                        st.rerun()
                    else:
                        st.error("Fehler beim Löschen.")


def render_call_statistics(customer_id: int):
    """
    Rendert Statistiken über Anrufe eines Kunden.
    
    Args:
        customer_id: ID des Kunden
    """
    stats = get_call_statistics(customer_id)
    
    if not stats or stats.get("total", 0) == 0:
        st.info("Noch keine Anruf-Statistiken verfügbar.")
        return
    
    st.subheader("[CHART] Anruf-Statistiken")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gesamt", stats["total"])
    
    with col2:
        st.metric("Eingehend", stats["incoming"])
    
    with col3:
        st.metric("Ausgehend", stats["outgoing"])
    
    with col4:
        st.metric("Gesamtdauer", stats["total_duration_formatted"])
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric("Ø Dauer", stats["average_duration_formatted"])
    
    with col6:
        if stats.get("last_call"):
            last_call = stats["last_call"]
            st.markdown(f"**Letzter Anruf:**")
            st.markdown(f"{last_call['date']}")
            st.markdown(f"{CALL_DIRECTIONS.get(last_call['direction'], last_call['direction'])} - {last_call['phone_number']}")


def render_call_quick_action(customer_id: int, customer_name: str, phone_numbers: list = None):
    """
    Rendert einen Quick-Action-Button zum schnellen Protokollieren eines Anrufs.
    
    Args:
        customer_id: ID des Kunden
        customer_name: Name des Kunden
        phone_numbers: Liste von Telefonnummern des Kunden
    """
    if st.button("📞 Anruf protokollieren", key=f"quick_call_{customer_id}"):
        st.session_state.show_call_dialog = True
        st.session_state.call_dialog_customer_id = customer_id
        st.session_state.call_dialog_customer_name = customer_name
        st.session_state.call_dialog_phone_numbers = phone_numbers
        st.rerun()
    
    # Zeige Dialog wenn aktiviert
    if st.session_state.get("show_call_dialog") and st.session_state.get("call_dialog_customer_id") == customer_id:
        with st.container():
            render_call_dialog(
                customer_id=customer_id,
                customer_name=customer_name,
                phone_numbers=phone_numbers
            )
            if st.button("Schließen", key=f"close_call_dialog_{customer_id}"):
                st.session_state.show_call_dialog = False
                st.rerun()


# Beispiel-Integration in bestehende CRM-UI
def integrate_call_logging_to_customer_profile(customer_id: int, customer_data: Dict[str, Any]):
    """
    Integriert Anruf-Protokollierung in ein Kundenprofil.
    
    Args:
        customer_id: ID des Kunden
        customer_data: Dictionary mit Kundendaten
    """
    st.markdown("---")
    st.markdown("### 📞 Anrufe")
    
    # Sammle Telefonnummern
    phone_numbers = []
    if customer_data.get("phone"):
        phone_numbers.append(customer_data["phone"])
    if customer_data.get("mobile"):
        phone_numbers.append(customer_data["mobile"])
    
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3 = st.tabs(["Neuer Anruf", "Anruf-Historie", "Statistiken"])
    
    with tab1:
        render_call_dialog(
            customer_id=customer_id,
            customer_name=customer_data.get("name", "Unbekannt"),
            phone_numbers=phone_numbers if phone_numbers else None
        )
    
    with tab2:
        render_call_list(customer_id=customer_id)
    
    with tab3:
        render_call_statistics(customer_id=customer_id)
