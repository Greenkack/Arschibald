# crm/utils/reminder_ui.py
"""
Reminder UI Module für CRM Dashboard
Dashboard-Widget für fällige Erinnerungen

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
from datetime import date, timedelta
from typing import Any

try:
    from crm.utils.notification_manager import (
        get_due_reminders,
        get_all_reminders,
        update_reminder_status,
        snooze_reminder,
        create_manual_reminder,
        format_reminder_for_display,
        get_reminder_statistics
    )
    NOTIFICATION_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Notification Manager nicht verfügbar: {e}")
    NOTIFICATION_MANAGER_AVAILABLE = False


def render_reminders_widget(texts: dict[str, str] = None):
    """
    Rendert das Erinnerungs-Widget für das Dashboard.
    Zeigt fällige Erinnerungen und ermöglicht Aktionen.
    
    Args:
        texts: Übersetzungstexte (optional)
    """
    if not NOTIFICATION_MANAGER_AVAILABLE:
        st.warning("Erinnerungssystem nicht verfügbar")
        return
    
    st.subheader("🔔 Fällige Erinnerungen")
    
    # Lade fällige Erinnerungen
    due_reminders = get_due_reminders()
    
    if not due_reminders:
        st.success("Keine fälligen Erinnerungen!")
        st.info("Alle Erinnerungen sind auf dem neuesten Stand.")
        return
    
    # Zeige Anzahl
    st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #EF4444 0%, #DC2626 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        ">
            <h2 style="margin: 0; font-size: 2em;">{len(due_reminders)}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Fällige Erinnerung(en)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Zeige jede Erinnerung
    for reminder in due_reminders:
        display_reminder = format_reminder_for_display(reminder)
        render_reminder_card(display_reminder)


def render_reminder_card(reminder: dict[str, Any]):
    """
    Rendert eine einzelne Erinnerungs-Karte mit Aktionen.
    
    Args:
        reminder: Erinnerungs-Dictionary (formatiert)
    """
    reminder_id = reminder['id']
    color = reminder['display_color']
    
    # Container für Erinnerung
    with st.container():
        col_info, col_actions = st.columns([3, 1])
        
        with col_info:
            # Erinnerungs-Info
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, {color} 0%, {color}dd 100%);
                    padding: 15px;
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 5px;">
                                {reminder['type_label']}
                            </div>
                            <div style="font-size: 1.1em; font-weight: bold; margin-bottom: 8px;">
                                {reminder.get('message', 'Keine Nachricht')}
                            </div>
                            <div style="font-size: 0.85em; opacity: 0.8;">
                                {reminder['due_date_label']}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            # Aktions-Buttons
            st.write("")  # Spacing
            
            if st.button("Erledigt", key=f"complete_{reminder_id}", use_container_width=True):
                if update_reminder_status(reminder_id, 'completed'):
                    st.success("Erinnerung als erledigt markiert!")
                    st.rerun()
                else:
                    st.error("Fehler beim Aktualisieren")
            
            if st.button("💤 Snooze (2 Tage)", key=f"snooze_{reminder_id}", use_container_width=True):
                if snooze_reminder(reminder_id, days=2):
                    st.success("Erinnerung um 2 Tage verschoben!")
                    st.rerun()
                else:
                    st.error("Fehler beim Verschieben")
            
            if st.button("Verwerfen", key=f"dismiss_{reminder_id}", use_container_width=True):
                if update_reminder_status(reminder_id, 'dismissed'):
                    st.success("Erinnerung verworfen!")
                    st.rerun()
                else:
                    st.error("Fehler beim Verwerfen")


def render_reminders_management_ui(texts: dict[str, str] = None):
    """
    Vollständige Erinnerungsverwaltungs-UI.
    Zeigt alle Erinnerungen und ermöglicht Verwaltung.
    
    Args:
        texts: Übersetzungstexte (optional)
    """
    if not NOTIFICATION_MANAGER_AVAILABLE:
        st.error("Erinnerungssystem nicht verfügbar")
        return
    
    st.header("🔔 Erinnerungsverwaltung")
    
    # Tabs für verschiedene Ansichten
    tabs = st.tabs([
        "📋 Fällige Erinnerungen",
        "Alle Erinnerungen",
        "➕ Neue Erinnerung",
        "Statistiken"
    ])
    
    with tabs[0]:
        render_due_reminders_tab()
    
    with tabs[1]:
        render_all_reminders_tab()
    
    with tabs[2]:
        render_create_reminder_tab()
    
    with tabs[3]:
        render_statistics_tab()


def render_due_reminders_tab():
    """Rendert Tab mit fälligen Erinnerungen."""
    st.subheader("📋 Fällige Erinnerungen")
    
    due_reminders = get_due_reminders()
    
    if not due_reminders:
        st.success("Keine fälligen Erinnerungen!")
        return
    
    st.info(f"Sie haben {len(due_reminders)} fällige Erinnerung(en)")
    
    for reminder in due_reminders:
        display_reminder = format_reminder_for_display(reminder)
        render_reminder_card(display_reminder)


def render_all_reminders_tab():
    """Rendert Tab mit allen Erinnerungen."""
    st.subheader("Alle Erinnerungen")
    
    # Filter
    col_status, col_type = st.columns(2)
    
    with col_status:
        status_filter = st.selectbox(
            "Status filtern",
            options=["Alle", "Ausstehend", "Verschoben", "Erledigt", "Verworfen"],
            key="reminder_status_filter"
        )
    
    with col_type:
        type_filter = st.selectbox(
            "Typ filtern",
            options=["Alle", "Lead Follow-up", "Angebots Follow-up", "Termin Follow-up", "Manuell"],
            key="reminder_type_filter"
        )
    
    # Mappe Filter zu DB-Werten
    status_map = {
        "Alle": None,
        "Ausstehend": "pending",
        "Verschoben": "snoozed",
        "Erledigt": "completed",
        "Verworfen": "dismissed"
    }
    
    type_map = {
        "Alle": None,
        "Lead Follow-up": "lead_created",
        "Angebots Follow-up": "offer_sent",
        "Termin Follow-up": "appointment_completed",
        "Manuell": "manual"
    }
    
    status_value = status_map[status_filter]
    
    # Lade Erinnerungen
    if status_value:
        reminders = get_all_reminders(status=status_value)
    else:
        reminders = get_all_reminders()
    
    # Filtere nach Typ (client-side)
    type_value = type_map[type_filter]
    if type_value:
        reminders = [r for r in reminders if r.get('reminder_type') == type_value]
    
    if not reminders:
        st.info("Keine Erinnerungen gefunden mit den gewählten Filtern.")
        return
    
    st.write(f"**{len(reminders)} Erinnerung(en) gefunden**")
    
    # Zeige Erinnerungen
    for reminder in reminders:
        display_reminder = format_reminder_for_display(reminder)
        
        with st.expander(f"{display_reminder['type_label']} - {display_reminder['due_date_label']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Nachricht:** {reminder.get('message', 'Keine Nachricht')}")
                st.write(f"**Status:** {display_reminder['status_label']}")
                st.write(f"**Fällig:** {display_reminder['due_date_label']}")
                st.write(f"**Verknüpft mit:** {reminder.get('related_type', 'Unbekannt')} #{reminder.get('related_id', 'N/A')}")
                
                if reminder.get('repeat_count', 0) > 0:
                    st.write(f"**Verschoben:** {reminder['repeat_count']}x")
            
            with col2:
                if reminder.get('status') not in ['completed', 'dismissed']:
                    if st.button("Erledigt", key=f"complete_all_{reminder['id']}"):
                        if update_reminder_status(reminder['id'], 'completed'):
                            st.success("Erledigt!")
                            st.rerun()
                    
                    if st.button("💤 Snooze", key=f"snooze_all_{reminder['id']}"):
                        if snooze_reminder(reminder['id']):
                            st.success("Verschoben!")
                            st.rerun()


def render_create_reminder_tab():
    """Rendert Tab zum Erstellen neuer Erinnerungen."""
    st.subheader("➕ Neue Erinnerung erstellen")
    
    with st.form("create_reminder_form"):
        st.write("**Erinnerungsdetails**")
        
        # Verknüpfung
        col1, col2 = st.columns(2)
        
        with col1:
            related_type = st.selectbox(
                "Verknüpft mit",
                options=["customer", "project", "lead", "appointment"],
                format_func=lambda x: {
                    "customer": "Kunde",
                    "project": "Projekt",
                    "lead": "Lead",
                    "appointment": "Termin"
                }[x]
            )
        
        with col2:
            related_id = st.number_input(
                "ID",
                min_value=1,
                value=1,
                step=1
            )
        
        # Nachricht
        message = st.text_area(
            "Nachricht",
            placeholder="Beschreiben Sie woran Sie erinnert werden möchten...",
            height=100
        )
        
        # Fälligkeitsdatum
        due_date = st.date_input(
            "Fälligkeitsdatum",
            value=date.today() + timedelta(days=1),
            min_value=date.today()
        )
        
        # Submit
        submitted = st.form_submit_button("🔔 Erinnerung erstellen", use_container_width=True)
        
        if submitted:
            if not message or not message.strip():
                st.error("Bitte geben Sie eine Nachricht ein!")
            else:
                reminder_id = create_manual_reminder(
                    related_id=related_id,
                    related_type=related_type,
                    due_date=due_date,
                    message=message.strip()
                )
                
                if reminder_id:
                    st.success(f"Erinnerung #{reminder_id} erfolgreich erstellt!")
                    st.balloons()
                else:
                    st.error("Fehler beim Erstellen der Erinnerung")


def render_statistics_tab():
    """Rendert Tab mit Statistiken."""
    st.subheader("Erinnerungs-Statistiken")
    
    stats = get_reminder_statistics()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #2563EB 0%, #1D4ED8 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                text-align: center;
                box-shadow: 0 3px 10px rgba(37, 99, 235, 0.3);
            ">
                <h3 style="margin: 0; font-size: 0.9em; opacity: 0.9;">Gesamt</h3>
                <h1 style="margin: 10px 0; font-size: 2.2em;">{stats.get('total', 0)}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #EF4444 0%, #DC2626 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                text-align: center;
                box-shadow: 0 3px 10px rgba(239, 68, 68, 0.3);
            ">
                <h3 style="margin: 0; font-size: 0.9em; opacity: 0.9;">Fällig</h3>
                <h1 style="margin: 10px 0; font-size: 2.2em;">{stats.get('due', 0)}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #F59E0B 0%, #D97706 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                text-align: center;
                box-shadow: 0 3px 10px rgba(245, 158, 11, 0.3);
            ">
                <h3 style="margin: 0; font-size: 0.9em; opacity: 0.9;">Heute</h3>
                <h1 style="margin: 10px 0; font-size: 2.2em;">{stats.get('due_today', 0)}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pending = stats.get('by_status', {}).get('pending', 0)
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #8B5CF6 0%, #7C3AED 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                text-align: center;
                box-shadow: 0 3px 10px rgba(139, 92, 246, 0.3);
            ">
                <h3 style="margin: 0; font-size: 0.9em; opacity: 0.9;">Ausstehend</h3>
                <h1 style="margin: 10px 0; font-size: 2.2em;">{pending}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Verteilung nach Status
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("**Verteilung nach Status**")
        by_status = stats.get('by_status', {})
        
        status_labels = {
            'pending': '⏳ Ausstehend',
            'completed': 'Erledigt',
            'snoozed': '💤 Verschoben',
            'dismissed': 'Verworfen'
        }
        
        for status, count in by_status.items():
            label = status_labels.get(status, status)
            st.write(f"{label}: **{count}**")
    
    with col_right:
        st.write("**Verteilung nach Typ**")
        by_type = stats.get('by_type', {})
        
        type_labels = {
            'lead_created': '👤 Lead Follow-up',
            'offer_sent': '📋 Angebots Follow-up',
            'appointment_completed': '📅 Termin Follow-up',
            'manual': '✏️ Manuell'
        }
        
        for reminder_type, count in by_type.items():
            label = type_labels.get(reminder_type, reminder_type)
            st.write(f"{label}: **{count}**")
    
    # Durchschnittliche Snooze-Anzahl
    st.write("")
    avg_snooze = stats.get('avg_snooze_count', 0)
    st.metric(
        label="Durchschnittliche Snooze-Anzahl",
        value=f"{avg_snooze}x",
        help="Wie oft Erinnerungen im Durchschnitt verschoben werden"
    )


# ============================================================================
# Export-Funktionen
# ============================================================================

def show_reminders_widget(texts: dict[str, str] = None):
    """Öffentliche Funktion zum Anzeigen des Erinnerungs-Widgets."""
    render_reminders_widget(texts)


def show_reminders_management(texts: dict[str, str] = None):
    """Öffentliche Funktion zum Anzeigen der vollständigen Erinnerungsverwaltung."""
    render_reminders_management_ui(texts)


if __name__ == "__main__":
    # Test-Modus
    import streamlit as st
    st.set_page_config(page_title="Reminder UI Test", layout="wide")
    
    show_reminders_management()
