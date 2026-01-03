# crm/features/note_ui.py
"""
UI-Komponenten für Notizen und Kommunikationshistorie.

Dieses Modul stellt Streamlit-UI-Komponenten für die Timeline-Ansicht,
Filterung und Verwaltung von Aktivitäten bereit.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from crm.features.note_manager import (
    create_activity,
    get_customer_activities,
    update_activity,
    delete_activity,
    toggle_important,
    search_activities,
    get_activity_statistics,
    ACTIVITY_TYPES,
    add_note,
    add_email_activity,
    add_call_activity,
    add_appointment_activity
)


def render_activity_timeline(customer_id: int, show_filters: bool = True):
    """
    Rendert die Timeline-Ansicht für Kundenaktivitäten.
    
    Args:
        customer_id: ID des Kunden
        show_filters: Ob Filter angezeigt werden sollen
    """
    st.subheader(" Kommunikationshistorie & Timeline")
    
    # Statistiken anzeigen
    stats = get_activity_statistics(customer_id)
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gesamt", stats.get("total", 0))
        with col2:
            st.metric("Wichtig", stats.get("important", 0))
        with col3:
            by_type = stats.get("by_type", {})
            st.metric("Notizen", by_type.get("note", 0))
        with col4:
            last = stats.get("last_activity")
            if last:
                try:
                    last_date = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                    days_ago = (datetime.now() - last_date).days
                    st.metric("Letzte Aktivität", f"vor {days_ago}d")
                except:
                    st.metric("Letzte Aktivität", "N/A")
            else:
                st.metric("Letzte Aktivität", "Keine")
    
    st.divider()
    
    # Filter
    selected_type = None
    search_term = None
    include_archived = False
    
    if show_filters:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            search_term = st.text_input(
                "Suche",
                placeholder="Suche in Titel und Inhalt...",
                key=f"activity_search_{customer_id}"
            )
        
        with col2:
            type_options = ["Alle"] + list(ACTIVITY_TYPES.values())
            selected_type_display = st.selectbox(
                "Typ filtern",
                type_options,
                key=f"activity_type_filter_{customer_id}"
            )
            
            # Konvertiere Display-Name zurück zu Key
            if selected_type_display != "Alle":
                for key, value in ACTIVITY_TYPES.items():
                    if value == selected_type_display:
                        selected_type = key
                        break
        
        with col3:
            include_archived = st.checkbox(
                "Archivierte",
                key=f"activity_archived_{customer_id}"
            )
    
    # Aktivitäten abrufen
    if search_term:
        activities = search_activities(
            search_term,
            customer_id=customer_id,
            activity_type=selected_type
        )
    else:
        activities = get_customer_activities(
            customer_id,
            activity_type=selected_type,
            include_archived=include_archived
        )
    
    # Timeline rendern
    if not activities:
        st.info("Noch keine Aktivitäten vorhanden.")
        return
    
    st.write(f"**{len(activities)} Aktivitäten gefunden**")
    
    for activity in activities:
        render_activity_card(activity, customer_id)


def render_activity_card(activity: Dict[str, Any], customer_id: int):
    """
    Rendert eine einzelne Aktivitätskarte.
    
    Args:
        activity: Aktivitätsdaten
        customer_id: ID des Kunden
    """
    activity_id = activity["id"]
    
    # Icon basierend auf Typ
    type_icons = {
        "note": "",
        "email": "",
        "call": "",
        "appointment": "",
        "meeting": "",
        "task": "",
        "other": ""
    }
    icon = type_icons.get(activity["activity_type"], "")
    
    # Container für Aktivität
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Titel mit Icon und wichtig-Marker
            title_text = f"{icon} **{activity['title']}**"
            if activity.get("is_important"):
                title_text = f" {title_text}"
            if activity.get("archived"):
                title_text = f" {title_text}"
            st.markdown(title_text)
        
        with col2:
            st.caption(activity["activity_type_display"])
        
        with col3:
            # Datum formatieren
            try:
                created_date = datetime.strptime(activity["created_at"], "%Y-%m-%d %H:%M:%S")
                date_str = created_date.strftime("%d.%m.%Y %H:%M")
                
                # Zeige "alt" Marker
                if activity.get("is_old"):
                    st.caption(f" {date_str}")
                else:
                    st.caption(date_str)
            except:
                st.caption(activity["created_at"])
        
        # Inhalt
        if activity.get("content"):
            with st.expander("Details anzeigen", expanded=False):
                st.write(activity["content"])
        
        # Metadaten
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.caption(f"Erstellt von: {activity.get('created_by', 'Unbekannt')}")
        
        with col2:
            # Wichtig-Button
            if st.button(
                "" if not activity.get("is_important") else "",
                key=f"toggle_important_{activity_id}",
                help="Als wichtig markieren/entfernen"
            ):
                if toggle_important(activity_id):
                    st.success("Status aktualisiert!")
                    st.rerun()
        
        with col3:
            # Bearbeiten-Button
            if st.button("", key=f"edit_activity_{activity_id}", help="Bearbeiten"):
                st.session_state[f"edit_activity_{activity_id}"] = True
                st.rerun()
        
        # Bearbeiten-Dialog
        if st.session_state.get(f"edit_activity_{activity_id}", False):
            render_edit_activity_dialog(activity, customer_id)
        
        st.divider()


def render_edit_activity_dialog(activity: Dict[str, Any], customer_id: int):
    """
    Rendert einen Dialog zum Bearbeiten einer Aktivität.
    
    Args:
        activity: Aktivitätsdaten
        customer_id: ID des Kunden
    """
    activity_id = activity["id"]
    
    with st.form(key=f"edit_form_{activity_id}"):
        st.subheader("Aktivität bearbeiten")
        
        new_title = st.text_input("Titel", value=activity["title"])
        new_content = st.text_area("Inhalt", value=activity.get("content", ""), height=150)
        new_important = st.checkbox("Als wichtig markieren", value=activity.get("is_important", False))
        new_archived = st.checkbox("Archivieren", value=activity.get("archived", False))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button(" Speichern", use_container_width=True):
                if update_activity(
                    activity_id,
                    title=new_title,
                    content=new_content,
                    is_important=new_important,
                    archived=new_archived
                ):
                    st.success("Aktivität aktualisiert!")
                    st.session_state[f"edit_activity_{activity_id}"] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Aktualisieren!")
        
        with col2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f"edit_activity_{activity_id}"] = False
                st.rerun()
        
        with col3:
            if st.form_submit_button("Löschen", use_container_width=True):
                if delete_activity(activity_id):
                    st.success("Aktivität gelöscht!")
                    st.session_state[f"edit_activity_{activity_id}"] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Löschen!")


def render_add_activity_form(customer_id: int):
    """
    Rendert ein Formular zum Hinzufügen einer neuen Aktivität.
    
    Args:
        customer_id: ID des Kunden
    """
    st.subheader(" Neue Aktivität hinzufügen")
    
    with st.form(key=f"add_activity_form_{customer_id}"):
        # Typ auswählen
        activity_type_display = st.selectbox(
            "Typ",
            list(ACTIVITY_TYPES.values()),
            key=f"new_activity_type_{customer_id}"
        )
        
        # Konvertiere Display-Name zu Key
        activity_type = None
        for key, value in ACTIVITY_TYPES.items():
            if value == activity_type_display:
                activity_type = key
                break
        
        # Titel und Inhalt
        title = st.text_input("Titel *", key=f"new_activity_title_{customer_id}")
        content = st.text_area("Inhalt/Notizen", height=150, key=f"new_activity_content_{customer_id}")
        
        # Optionen
        col1, col2 = st.columns(2)
        with col1:
            created_by = st.text_input("Erstellt von", value="System", key=f"new_activity_by_{customer_id}")
        with col2:
            is_important = st.checkbox("Als wichtig markieren", key=f"new_activity_important_{customer_id}")
        
        # Submit
        if st.form_submit_button(" Aktivität erstellen", use_container_width=True):
            if not title:
                st.error("Bitte geben Sie einen Titel ein!")
            else:
                activity_id = create_activity(
                    customer_id=customer_id,
                    activity_type=activity_type,
                    title=title,
                    content=content,
                    created_by=created_by,
                    is_important=is_important
                )
                
                if activity_id:
                    st.success(f"Aktivität erstellt! (ID: {activity_id})")
                    st.rerun()
                else:
                    st.error("Fehler beim Erstellen der Aktivität!")


def render_quick_add_buttons(customer_id: int):
    """
    Rendert Schnellzugriff-Buttons für häufige Aktivitätstypen.
    
    Args:
        customer_id: ID des Kunden
    """
    st.write("**Schnellzugriff:**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Notiz", key=f"quick_note_{customer_id}", use_container_width=True):
            st.session_state[f"quick_add_type_{customer_id}"] = "note"
    
    with col2:
        if st.button(" Anruf", key=f"quick_call_{customer_id}", use_container_width=True):
            st.session_state[f"quick_add_type_{customer_id}"] = "call"
    
    with col3:
        if st.button(" E-Mail", key=f"quick_email_{customer_id}", use_container_width=True):
            st.session_state[f"quick_add_type_{customer_id}"] = "email"
    
    with col4:
        if st.button(" Termin", key=f"quick_appointment_{customer_id}", use_container_width=True):
            st.session_state[f"quick_add_type_{customer_id}"] = "appointment"
    
    # Schnell-Formular anzeigen
    quick_type = st.session_state.get(f"quick_add_type_{customer_id}")
    if quick_type:
        render_quick_add_form(customer_id, quick_type)


def render_quick_add_form(customer_id: int, activity_type: str):
    """
    Rendert ein vereinfachtes Schnell-Formular.
    
    Args:
        customer_id: ID des Kunden
        activity_type: Typ der Aktivität
    """
    type_display = ACTIVITY_TYPES.get(activity_type, activity_type)
    
    with st.form(key=f"quick_form_{customer_id}_{activity_type}"):
        st.write(f"**{type_display} hinzufügen**")
        
        title = st.text_input("Titel *")
        content = st.text_area("Notizen", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button(" Speichern", use_container_width=True):
                if not title:
                    st.error("Bitte geben Sie einen Titel ein!")
                else:
                    activity_id = create_activity(
                        customer_id=customer_id,
                        activity_type=activity_type,
                        title=title,
                        content=content,
                        created_by="System",
                        is_important=False
                    )
                    
                    if activity_id:
                        st.success("Gespeichert!")
                        st.session_state[f"quick_add_type_{customer_id}"] = None
                        st.rerun()
                    else:
                        st.error("Fehler beim Speichern!")
        
        with col2:
            if st.form_submit_button("Abbrechen", use_container_width=True):
                st.session_state[f"quick_add_type_{customer_id}"] = None
                st.rerun()


def render_activity_summary(customer_id: int):
    """
    Rendert eine kompakte Zusammenfassung der Aktivitäten.
    
    Args:
        customer_id: ID des Kunden
    """
    stats = get_activity_statistics(customer_id)
    
    if not stats or stats.get("total", 0) == 0:
        st.info("Noch keine Aktivitäten")
        return
    
    # Letzte 3 Aktivitäten
    recent = get_customer_activities(customer_id, limit=3)
    
    st.write("**Letzte Aktivitäten:**")
    for activity in recent:
        icon = {
            "note": "",
            "email": "",
            "call": "",
            "appointment": ""
        }.get(activity["activity_type"], "")
        
        try:
            created_date = datetime.strptime(activity["created_at"], "%Y-%m-%d %H:%M:%S")
            date_str = created_date.strftime("%d.%m. %H:%M")
        except:
            date_str = "N/A"
        
        st.caption(f"{icon} {activity['title']} - {date_str}")
