"""
Datei: crm/utils/backup_ui.py
Zweck: Streamlit UI für Backup-Verwaltung im Admin-Panel
Autor: Kiro AI
Datum: 2025-01-14

Funktionen:
- Backup-Verwaltungs-UI
- Manuelle Backup-Erstellung
- Backup-Liste mit Wiederherstellungs-Funktion
- Scheduler-Steuerung
- Backup-Statistiken
"""

import streamlit as st
from datetime import datetime
from typing import Optional

try:
    from crm.utils.backup_scheduler import (
        create_backup,
        list_backups,
        restore_backup,
        delete_backup,
        start_scheduler,
        stop_scheduler,
        get_scheduler_status,
        get_backup_statistics,
        APSCHEDULER_AVAILABLE
    )
    BACKUP_MODULE_AVAILABLE = True
except ImportError:
    BACKUP_MODULE_AVAILABLE = False


def render_backup_management_ui() -> None:
    """Rendert die Backup-Verwaltungs-UI im Admin-Panel."""
    
    if not BACKUP_MODULE_AVAILABLE:
        st.error("Backup-Modul nicht verfügbar. Bitte prüfen Sie die Installation.")
        return
    
    st.title(" Backup-Verwaltung")
    st.markdown("---")
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs([
        "Übersicht",
        " Backups verwalten",
        " Automatische Backups",
        "Statistiken"
    ])
    
    # Tab 1: Übersicht
    with tab1:
        render_backup_overview()
    
    # Tab 2: Backup-Verwaltung
    with tab2:
        render_backup_management()
    
    # Tab 3: Scheduler-Steuerung
    with tab3:
        render_scheduler_control()
    
    # Tab 4: Statistiken
    with tab4:
        render_backup_statistics()


def render_backup_overview() -> None:
    """Rendert die Backup-Übersicht."""
    
    st.subheader("Backup-Übersicht")
    
    # Hole Statistiken
    stats = get_backup_statistics()
    scheduler_status = get_scheduler_status()
    
    # Metriken in Spalten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gesamt Backups", stats["total_backups"])
    
    with col2:
        st.metric("Gesamtgröße", f"{stats['total_size_mb']} MB")
    
    with col3:
        status_icon = "🟢" if scheduler_status["running"] else ""
        st.metric("Scheduler", f"{status_icon} {'Aktiv' if scheduler_status['running'] else 'Inaktiv'}")
    
    with col4:
        st.metric("Letztes Backup", stats["latest_backup"])
    
    st.markdown("---")
    
    # Backup-Typen Übersicht
    st.subheader("Backup-Typen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("** Tägliche Backups**")
        daily_stats = stats["by_type"]["daily"]
        st.write(f"Anzahl: {daily_stats['count']} (max. 7)")
        st.write(f"Größe: {daily_stats['size_mb']} MB")
        st.write(f"Letztes: {daily_stats['latest']}")
        
        st.markdown("** Wöchentliche Backups**")
        weekly_stats = stats["by_type"]["weekly"]
        st.write(f"Anzahl: {weekly_stats['count']} (max. 4)")
        st.write(f"Größe: {weekly_stats['size_mb']} MB")
        st.write(f"Letztes: {weekly_stats['latest']}")
    
    with col2:
        st.markdown("**Monatliche Backups**")
        monthly_stats = stats["by_type"]["monthly"]
        st.write(f"Anzahl: {monthly_stats['count']} (max. 12)")
        st.write(f"Größe: {monthly_stats['size_mb']} MB")
        st.write(f"Letztes: {monthly_stats['latest']}")
        
        st.markdown("**Manuelle Backups**")
        manual_stats = stats["by_type"]["manual"]
        st.write(f"Anzahl: {manual_stats['count']} (max. 10)")
        st.write(f"Größe: {manual_stats['size_mb']} MB")
        st.write(f"Letztes: {manual_stats['latest']}")
    
    # Schnellaktionen
    st.markdown("---")
    st.subheader("Schnellaktionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(" Manuelles Backup erstellen", use_container_width=True):
            with st.spinner("Erstelle Backup..."):
                success, message = create_backup("manual")
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        if scheduler_status["running"]:
            if st.button("⏸ Scheduler stoppen", use_container_width=True):
                success, message = stop_scheduler()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            if st.button(" Scheduler starten", use_container_width=True):
                success, message = start_scheduler()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col3:
        if st.button(" Ansicht aktualisieren", use_container_width=True):
            st.rerun()


def render_backup_management() -> None:
    """Rendert die Backup-Verwaltung mit Liste und Aktionen."""
    
    st.subheader(" Backup-Verwaltung")
    
    # Manuelle Backup-Erstellung
    st.markdown("### Neues Backup erstellen")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("Erstellen Sie ein manuelles Backup der Datenbank. Dieses wird im 'manual' Ordner gespeichert.")
    
    with col2:
        if st.button(" Backup erstellen", use_container_width=True, type="primary"):
            with st.spinner("Erstelle Backup..."):
                success, message = create_backup("manual")
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    
    # Filter für Backup-Typ
    st.markdown("### Vorhandene Backups")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        backup_type_filter = st.selectbox(
            "Backup-Typ filtern",
            ["Alle", "Täglich", "Wöchentlich", "Monatlich", "Manuell"],
            key="backup_type_filter"
        )
    
    # Mappe Filter zu internem Typ
    type_mapping = {
        "Alle": None,
        "Täglich": "daily",
        "Wöchentlich": "weekly",
        "Monatlich": "monthly",
        "Manuell": "manual"
    }
    
    filter_type = type_mapping[backup_type_filter]
    
    # Hole Backups
    backups = list_backups(filter_type)
    
    if not backups:
        st.info("Keine Backups gefunden.")
        return
    
    st.write(f"**{len(backups)} Backup(s) gefunden**")
    
    # Backup-Liste
    for backup in backups:
        with st.expander(f"{backup['filename']} ({backup['size_mb']} MB)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Typ:** {backup['type'].capitalize()}")
                st.write(f"**Erstellt:** {backup['created_str']}")
                st.write(f"**Größe:** {backup['size_mb']} MB")
                st.write(f"**Pfad:** `{backup['path']}`")
            
            with col2:
                # Wiederherstellungs-Button mit Bestätigung
                restore_key = f"restore_{backup['filename']}"
                delete_key = f"delete_{backup['filename']}"
                
                if st.button(" Wiederherstellen", key=restore_key, use_container_width=True):
                    st.session_state[f"confirm_restore_{backup['filename']}"] = True
                
                # Bestätigungs-Dialog
                if st.session_state.get(f"confirm_restore_{backup['filename']}", False):
                    st.warning("**ACHTUNG:** Die aktuelle Datenbank wird überschrieben!")
                    
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("Ja", key=f"yes_{restore_key}", use_container_width=True):
                            with st.spinner("Stelle Backup wieder her..."):
                                success, message = restore_backup(backup['path'])
                                if success:
                                    st.success(message)
                                    st.session_state[f"confirm_restore_{backup['filename']}"] = False
                                    st.rerun()
                                else:
                                    st.error(message)
                    
                    with col_no:
                        if st.button("Nein", key=f"no_{restore_key}", use_container_width=True):
                            st.session_state[f"confirm_restore_{backup['filename']}"] = False
                            st.rerun()
                
                # Lösch-Button
                if st.button("Löschen", key=delete_key, use_container_width=True):
                    st.session_state[f"confirm_delete_{backup['filename']}"] = True
                
                # Lösch-Bestätigung
                if st.session_state.get(f"confirm_delete_{backup['filename']}", False):
                    st.warning("Backup wirklich löschen?")
                    
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("Ja", key=f"yes_{delete_key}", use_container_width=True):
                            success, message = delete_backup(backup['path'])
                            if success:
                                st.success(message)
                                st.session_state[f"confirm_delete_{backup['filename']}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col_no:
                        if st.button("Nein", key=f"no_{delete_key}", use_container_width=True):
                            st.session_state[f"confirm_delete_{backup['filename']}"] = False
                            st.rerun()


def render_scheduler_control() -> None:
    """Rendert die Scheduler-Steuerung."""
    
    st.subheader(" Automatische Backups")
    
    # Prüfe APScheduler-Verfügbarkeit
    if not APSCHEDULER_AVAILABLE:
        st.error("APScheduler ist nicht installiert.")
        st.info("Installieren Sie APScheduler mit: `pip install apscheduler`")
        return
    
    # Hole Scheduler-Status
    status = get_scheduler_status()
    
    # Status-Anzeige
    if status["running"]:
        st.success("Automatische Backups sind **AKTIV**")
    else:
        st.warning("Automatische Backups sind **INAKTIV**")
    
    st.markdown("---")
    
    # Scheduler-Steuerung
    col1, col2 = st.columns(2)
    
    with col1:
        if status["running"]:
            if st.button("⏸ Scheduler stoppen", use_container_width=True, type="secondary"):
                success, message = stop_scheduler()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            if st.button(" Scheduler starten", use_container_width=True, type="primary"):
                success, message = start_scheduler()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        if st.button(" Status aktualisieren", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Geplante Jobs
    if status["running"] and "jobs" in status:
        st.subheader(" Geplante Backup-Jobs")
        
        for job in status["jobs"]:
            with st.container():
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**{job['name']}**")
                    st.write(f"ID: `{job['id']}`")
                
                with col2:
                    st.write(f"**Nächste Ausführung:**")
                    st.write(f"{job['next_run']}")
                
                st.markdown("---")
    
    # Backup-Zeitplan Informationen
    st.subheader(" Backup-Zeitplan")
    
    st.markdown("""
    **Automatische Backups werden zu folgenden Zeiten erstellt:**
    
    -  **Täglich:** Jeden Tag um 2:00 Uhr (max. 7 Backups)
    -  **Wöchentlich:** Jeden Sonntag um 3:00 Uhr (max. 4 Backups)
    - **Monatlich:** Am 1. jeden Monats um 4:00 Uhr (max. 12 Backups)
    
    **Backup-Rotation:**
    - Alte Backups werden automatisch gelöscht, wenn die maximale Anzahl erreicht ist
    - Die neuesten Backups werden immer behalten
    """)
    
    st.info("**Tipp:** Starten Sie den Scheduler beim Anwendungsstart, um automatische Backups zu aktivieren.")


def render_backup_statistics() -> None:
    """Rendert Backup-Statistiken und Analysen."""
    
    st.subheader("Backup-Statistiken")
    
    # Hole Statistiken
    stats = get_backup_statistics()
    backups = list_backups()
    
    # Gesamtstatistiken
    st.markdown("### Gesamtübersicht")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Gesamt Backups", stats["total_backups"])
    
    with col2:
        st.metric("Gesamtgröße", f"{stats['total_size_mb']} MB")
    
    with col3:
        avg_size = round(stats['total_size_mb'] / stats['total_backups'], 2) if stats['total_backups'] > 0 else 0
        st.metric("Durchschn. Größe", f"{avg_size} MB")
    
    st.markdown("---")
    
    # Statistiken nach Typ
    st.markdown("### Statistiken nach Backup-Typ")
    
    for btype, type_name in [("daily", "Täglich"), ("weekly", "Wöchentlich"), 
                              ("monthly", "Monatlich"), ("manual", "Manuell")]:
        type_stats = stats["by_type"][btype]
        
        with st.expander(f"{type_name}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Anzahl", type_stats["count"])
            
            with col2:
                st.metric("Größe", f"{type_stats['size_mb']} MB")
            
            with col3:
                st.write("**Letztes Backup:**")
                st.write(type_stats["latest"])
    
    st.markdown("---")
    
    # Neueste Backups
    st.markdown("###  Neueste Backups")
    
    recent_backups = backups[:5]  # Zeige die 5 neuesten
    
    if recent_backups:
        for backup in recent_backups:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{backup['filename']}**")
            
            with col2:
                st.write(backup['type'].capitalize())
            
            with col3:
                st.write(f"{backup['size_mb']} MB")
            
            with col4:
                st.write(backup['created_str'])
    else:
        st.info("Keine Backups vorhanden.")


# Hauptfunktion für Integration in Admin-Panel
def render_admin_backup_tab() -> None:
    """
    Hauptfunktion zum Rendern des Backup-Tabs im Admin-Panel.
    Diese Funktion kann direkt in admin_panel.py importiert werden.
    """
    render_backup_management_ui()
