# crm/features/task_ui.py
"""
Task Management UI für CRM Dashboard
Streamlit-basierte Benutzeroberfläche für Aufgabenverwaltung

Author: Kiro AI
Version: 1.0
Date: 2025-01-13
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import Optional

try:
    from crm.features.task_manager import (
        create_task,
        get_task,
        update_task,
        delete_task,
        get_all_tasks,
        get_overdue_tasks,
        get_tasks_due_soon,
        get_task_statistics,
        get_tasks_needing_notification,
        mark_task_in_progress,
        mark_task_completed,
        reopen_task,
        format_task_for_display
    )
except ImportError as e:
    st.error(f"Task Manager Module konnte nicht geladen werden: {e}")
    # Dummy-Funktionen für Fallback
    def create_task(*args, **kwargs): return None
    def get_task(*args, **kwargs): return None
    def update_task(*args, **kwargs): return False
    def delete_task(*args, **kwargs): return False
    def get_all_tasks(*args, **kwargs): return []
    def get_overdue_tasks(*args, **kwargs): return []
    def get_tasks_due_soon(*args, **kwargs): return []
    def get_task_statistics(*args, **kwargs): return {}
    def get_tasks_needing_notification(*args, **kwargs): return []
    def mark_task_in_progress(*args, **kwargs): return False
    def mark_task_completed(*args, **kwargs): return False
    def reopen_task(*args, **kwargs): return False
    def format_task_for_display(task): return task


# ============================================================================
# Haupt-UI-Funktion
# ============================================================================

def render_task_management_ui(
    texts: dict = None,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None
):
    """
    Hauptfunktion für Task Management UI.
    
    Args:
        texts: Übersetzungs-Dictionary
        customer_id: Optionale Filterung nach Kunde
        project_id: Optionale Filterung nach Projekt
        lead_id: Optionale Filterung nach Lead
    """
    if texts is None:
        texts = {}
    
    st.header(" Aufgabenverwaltung")
    
    # Tabs für verschiedene Ansichten
    tabs = st.tabs([
        "Übersicht",
        "Alle Aufgaben",
        " Neue Aufgabe",
        "Benachrichtigungen"
    ])
    
    with tabs[0]:
        render_task_overview()
    
    with tabs[1]:
        render_task_list(customer_id=customer_id, project_id=project_id, lead_id=lead_id)
    
    with tabs[2]:
        render_create_task_form(customer_id=customer_id, project_id=project_id, lead_id=lead_id)
    
    with tabs[3]:
        render_task_notifications()


# ============================================================================
# Übersichts-Sektion
# ============================================================================

def render_task_overview():
    """Zeigt Task-Statistiken und KPIs."""
    st.subheader("Aufgaben-Übersicht")
    
    # Lade Statistiken
    stats = get_task_statistics()
    
    # KPI-Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = stats.get('total', 0)
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #2563EB 0%, #1d4ed8 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
                text-align: center;
            ">
                <h3 style="margin: 0; font-size: 1em; opacity: 0.9;">Gesamt</h3>
                <h1 style="margin: 10px 0; font-size: 2.5em;">{total}</h1>
                <p style="margin: 0; opacity: 0.8;">Aufgaben</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        open_tasks = stats.get('by_status', {}).get('open', 0)
        in_progress = stats.get('by_status', {}).get('in_progress', 0)
        active = open_tasks + in_progress
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #F59E0B 0%, #d97706 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
                text-align: center;
            ">
                <h3 style="margin: 0; font-size: 1em; opacity: 0.9;">Aktiv</h3>
                <h1 style="margin: 10px 0; font-size: 2.5em;">{active}</h1>
                <p style="margin: 0; opacity: 0.8;">Offen/In Arbeit</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        overdue = stats.get('overdue', 0)
        color = "#EF4444" if overdue > 0 else "#22C55E"
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, {color} 0%, {color}dd 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
                text-align: center;
            ">
                <h3 style="margin: 0; font-size: 1em; opacity: 0.9;">Überfällig</h3>
                <h1 style="margin: 10px 0; font-size: 2.5em;">{overdue}</h1>
                <p style="margin: 0; opacity: 0.8;">Dringend</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed = stats.get('by_status', {}).get('completed', 0)
        st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, #22C55E 0%, #16a34a 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
                text-align: center;
            ">
                <h3 style="margin: 0; font-size: 1em; opacity: 0.9;">Erledigt</h3>
                <h1 style="margin: 10px 0; font-size: 2.5em;">{completed}</h1>
                <p style="margin: 0; opacity: 0.8;">Abgeschlossen</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Prioritäten-Übersicht
    st.subheader("Nach Priorität (Aktive Aufgaben)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high = stats.get('by_priority', {}).get('high', 0)
        st.metric(" Hoch", high)
    
    with col2:
        medium = stats.get('by_priority', {}).get('medium', 0)
        st.metric("🟡 Mittel", medium)
    
    with col3:
        low = stats.get('by_priority', {}).get('low', 0)
        st.metric(" Niedrig", low)
    
    st.markdown("---")
    
    # Fälligkeits-Übersicht
    st.subheader(" Fälligkeiten")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        due_today = stats.get('due_today', 0)
        st.metric("⏰ Heute fällig", due_today)
    
    with col2:
        due_week = stats.get('due_this_week', 0)
        st.metric(" Diese Woche", due_week)
    
    with col3:
        st.metric("Überfällig", overdue)


# ============================================================================
# Task-Listen-Sektion
# ============================================================================

def render_task_list(
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None
):
    """Zeigt gefilterte Task-Liste."""
    st.subheader("Aufgabenliste")
    
    # Filter-Optionen
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        status_filter = st.selectbox(
            "Status",
            options=["Alle", "Offen", "In Arbeit", "Erledigt"],
            key="task_status_filter"
        )
    
    with col_filter2:
        priority_filter = st.selectbox(
            "Priorität",
            options=["Alle", "Hoch", "Mittel", "Niedrig"],
            key="task_priority_filter"
        )
    
    with col_filter3:
        due_filter = st.selectbox(
            "Fälligkeit",
            options=["Alle", "Überfällig", "Heute", "Diese Woche", "Nächste 30 Tage"],
            key="task_due_filter"
        )
    
    with col_filter4:
        sort_by = st.selectbox(
            "Sortierung",
            options=["Fälligkeit", "Priorität", "Erstellt", "Status"],
            key="task_sort_by"
        )
    
    # Lade Tasks mit Filtern
    status_map = {"Offen": "open", "In Arbeit": "in_progress", "Erledigt": "completed"}
    priority_map = {"Hoch": "high", "Mittel": "medium", "Niedrig": "low"}
    
    filter_status = status_map.get(status_filter) if status_filter != "Alle" else None
    filter_priority = priority_map.get(priority_filter) if priority_filter != "Alle" else None
    
    # Lade Tasks
    if due_filter == "Überfällig":
        tasks = get_overdue_tasks()
    elif due_filter == "Diese Woche":
        tasks = get_tasks_due_soon(days=7)
    elif due_filter == "Nächste 30 Tage":
        tasks = get_tasks_due_soon(days=30)
    else:
        tasks = get_all_tasks(
            status=filter_status,
            priority=filter_priority,
            customer_id=customer_id,
            project_id=project_id,
            lead_id=lead_id
        )
    
    # Zusätzliche Filter für "Heute"
    if due_filter == "Heute":
        today_str = date.today().isoformat()
        tasks = [t for t in tasks if t.get('due_date') == today_str]
    
    st.markdown(f"**{len(tasks)}** Aufgaben gefunden")
    st.markdown("---")
    
    if not tasks:
        st.info("Keine Aufgaben gefunden mit den aktuellen Filterkriterien.")
        return
    
    # Zeige Tasks als Cards
    for task in tasks:
        render_task_card(task)


def render_task_card(task: dict):
    """Rendert eine einzelne Task-Card."""
    display_task = format_task_for_display(task)
    
    # Bestimme Hintergrundfarbe
    bg_color = display_task['display_color']
    if display_task.get('is_overdue'):
        border_color = "#EF4444"
        border_width = "3px"
    else:
        border_color = bg_color
        border_width = "1px"
    
    # Card-Container
    with st.container():
        st.markdown(f"""
            <div style="
                border: {border_width} solid {border_color};
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #f8f9fa;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 8px 0; color: #1f2937;">
                            {display_task.get('title', 'Ohne Titel')}
                        </h4>
                        <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 0.9em;">
                            {display_task.get('description', '')[:100]}{'...' if len(display_task.get('description', '')) > 100 else ''}
                        </p>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <span style="background: {bg_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                {display_task.get('status_label', '')}
                            </span>
                            <span style="background: #64748b; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                {display_task.get('priority_label', '')}
                            </span>
                            <span style="background: #475569; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">
                                {display_task.get('due_date_label', '')}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Aktions-Buttons
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
        
        task_id = task['id']
        
        with col1:
            if task.get('status') != 'in_progress':
                if st.button(" In Arbeit", key=f"progress_{task_id}", use_container_width=True):
                    if mark_task_in_progress(task_id):
                        st.success("Status aktualisiert!")
                        st.rerun()
        
        with col2:
            if task.get('status') != 'completed':
                if st.button("Erledigt", key=f"complete_{task_id}", use_container_width=True):
                    if mark_task_completed(task_id):
                        st.success("Aufgabe erledigt!")
                        st.rerun()
        
        with col3:
            if task.get('status') == 'completed':
                if st.button(" Wieder öffnen", key=f"reopen_{task_id}", use_container_width=True):
                    if reopen_task(task_id):
                        st.success("Aufgabe wieder geöffnet!")
                        st.rerun()
        
        with col4:
            if st.button(" Bearbeiten", key=f"edit_{task_id}", use_container_width=True):
                st.session_state[f'edit_task_{task_id}'] = True
                st.rerun()
        
        with col5:
            if st.button("Löschen", key=f"delete_{task_id}", use_container_width=True):
                if st.session_state.get(f'confirm_delete_{task_id}', False):
                    if delete_task(task_id):
                        st.success("Aufgabe gelöscht!")
                        del st.session_state[f'confirm_delete_{task_id}']
                        st.rerun()
                else:
                    st.warning("Nochmal klicken zum Bestätigen!")
                    st.session_state[f'confirm_delete_{task_id}'] = True
        
        # Bearbeitungs-Formular (wenn aktiviert)
        if st.session_state.get(f'edit_task_{task_id}', False):
            render_edit_task_form(task)


# ============================================================================
# Formular-Sektionen
# ============================================================================

def render_create_task_form(
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None
):
    """Formular zum Erstellen einer neuen Aufgabe."""
    st.subheader(" Neue Aufgabe erstellen")
    
    with st.form("create_task_form", clear_on_submit=True):
        title = st.text_input("Titel *", placeholder="z.B. Kunde anrufen")
        
        description = st.text_area(
            "Beschreibung",
            placeholder="Detaillierte Beschreibung der Aufgabe...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox(
                "Priorität",
                options=["Niedrig", "Mittel", "Hoch"],
                index=1
            )
        
        with col2:
            due_date = st.date_input(
                "Fälligkeitsdatum",
                value=date.today() + timedelta(days=7),
                min_value=date.today()
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            assigned_to = st.text_input("Zugewiesen an", placeholder="Name des Bearbeiters")
        
        with col4:
            status = st.selectbox(
                "Status",
                options=["Offen", "In Arbeit"],
                index=0
            )
        
        # Zuordnungen (wenn nicht vorgegeben)
        if customer_id is None:
            customer_id_input = st.number_input(
                "Kunden-ID (optional)",
                min_value=0,
                value=0,
                step=1
            )
            customer_id = customer_id_input if customer_id_input > 0 else None
        
        if project_id is None:
            project_id_input = st.number_input(
                "Projekt-ID (optional)",
                min_value=0,
                value=0,
                step=1
            )
            project_id = project_id_input if project_id_input > 0 else None
        
        if lead_id is None:
            lead_id_input = st.number_input(
                "Lead-ID (optional)",
                min_value=0,
                value=0,
                step=1
            )
            lead_id = lead_id_input if lead_id_input > 0 else None
        
        submitted = st.form_submit_button("Aufgabe erstellen", use_container_width=True)
        
        if submitted:
            if not title or not title.strip():
                st.error("Titel ist erforderlich!")
            else:
                # Mapping
                priority_map = {"Niedrig": "low", "Mittel": "medium", "Hoch": "high"}
                status_map = {"Offen": "open", "In Arbeit": "in_progress"}
                
                task_id = create_task(
                    title=title,
                    description=description,
                    status=status_map[status],
                    priority=priority_map[priority],
                    due_date=due_date,
                    customer_id=customer_id,
                    project_id=project_id,
                    lead_id=lead_id,
                    assigned_to=assigned_to
                )
                
                if task_id:
                    st.success(f"Aufgabe #{task_id} erfolgreich erstellt!")
                    st.balloons()
                else:
                    st.error("Fehler beim Erstellen der Aufgabe.")


def render_edit_task_form(task: dict):
    """Formular zum Bearbeiten einer Aufgabe."""
    task_id = task['id']
    
    st.markdown("---")
    st.subheader(f" Aufgabe #{task_id} bearbeiten")
    
    with st.form(f"edit_task_form_{task_id}"):
        title = st.text_input("Titel", value=task.get('title', ''))
        
        description = st.text_area(
            "Beschreibung",
            value=task.get('description', ''),
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            priority_map = {"low": 0, "medium": 1, "high": 2}
            priority_index = priority_map.get(task.get('priority', 'medium'), 1)
            priority = st.selectbox(
                "Priorität",
                options=["Niedrig", "Mittel", "Hoch"],
                index=priority_index
            )
        
        with col2:
            due_date_str = task.get('due_date')
            if due_date_str:
                try:
                    due_date_val = datetime.fromisoformat(due_date_str).date()
                except:
                    due_date_val = date.today()
            else:
                due_date_val = date.today()
            
            due_date = st.date_input(
                "Fälligkeitsdatum",
                value=due_date_val
            )
        
        assigned_to = st.text_input(
            "Zugewiesen an",
            value=task.get('assigned_to', '')
        )
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            save_button = st.form_submit_button(" Speichern", use_container_width=True)
        
        with col_cancel:
            cancel_button = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if save_button:
            priority_map_reverse = {"Niedrig": "low", "Mittel": "medium", "Hoch": "high"}
            
            success = update_task(
                task_id=task_id,
                title=title,
                description=description,
                priority=priority_map_reverse[priority],
                due_date=due_date,
                assigned_to=assigned_to
            )
            
            if success:
                st.success("Aufgabe aktualisiert!")
                del st.session_state[f'edit_task_{task_id}']
                st.rerun()
            else:
                st.error("Fehler beim Aktualisieren.")
        
        if cancel_button:
            del st.session_state[f'edit_task_{task_id}']
            st.rerun()


# ============================================================================
# Benachrichtigungs-Sektion
# ============================================================================

def render_task_notifications():
    """Zeigt Benachrichtigungen für fällige und überfällige Tasks."""
    st.subheader("Benachrichtigungen")
    
    notifications = get_tasks_needing_notification()
    
    if not notifications:
        st.success(" Keine dringenden Benachrichtigungen!")
        st.info("Alle Aufgaben sind im Plan.")
        return
    
    # Gruppiere nach Benachrichtigungstyp
    overdue = [n for n in notifications if n.get('notification_type') == 'overdue']
    due_today = [n for n in notifications if n.get('notification_type') == 'due_today']
    due_tomorrow = [n for n in notifications if n.get('notification_type') == 'due_tomorrow']
    
    # Überfällige Tasks (Rot)
    if overdue:
        st.markdown("###  Überfällige Aufgaben")
        for task in overdue:
            display_task = format_task_for_display(task)
            st.error(f"**{display_task['title']}** - {display_task['due_date_label']}")
    
    # Heute fällige Tasks (Orange)
    if due_today:
        st.markdown("### ⏰ Heute fällig")
        for task in due_today:
            display_task = format_task_for_display(task)
            st.warning(f"**{display_task['title']}** - {display_task['priority_label']}")
    
    # Morgen fällige Tasks (Info)
    if due_tomorrow:
        st.markdown("###  Morgen fällig")
        for task in due_tomorrow:
            display_task = format_task_for_display(task)
            st.info(f"**{display_task['title']}** - {display_task['priority_label']}")


# ============================================================================
# Export-Funktion
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Task Management Test", layout="wide")
    render_task_management_ui()
