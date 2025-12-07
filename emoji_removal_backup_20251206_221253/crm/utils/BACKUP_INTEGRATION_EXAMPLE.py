"""
Datei: crm/utils/BACKUP_INTEGRATION_EXAMPLE.py
Zweck: Beispiel für die Integration des Backup-Systems in die Hauptanwendung
Autor: Kiro AI
Datum: 2025-01-14

Dieses Beispiel zeigt, wie das Backup-System in admin_panel.py und gui.py integriert wird.
"""

# ============================================================================
# BEISPIEL 1: Integration in admin_panel.py
# ============================================================================

"""
# In admin_panel.py

from crm.utils.backup_ui import render_admin_backup_tab

def render_admin_panel():
    st.title("⚙️ Admin-Panel")
    
    # Bestehende Tabs + neuer Backup-Tab
    tabs = st.tabs([
        "Produkte",
        "Preise",
        "PDF-Einstellungen",
        "👥 Benutzerverwaltung",
        "🗄️ Backup-Verwaltung"  # NEUER TAB
    ])
    
    with tabs[0]:
        # Produkte-UI
        render_product_admin_ui()
    
    with tabs[1]:
        # Preise-UI
        render_price_matrix_tab()
    
    with tabs[2]:
        # PDF-UI
        render_pdf_settings_ui()
    
    with tabs[3]:
        # Benutzer-UI
        render_user_management_tab()
    
    with tabs[4]:
        # BACKUP-UI (NEU)
        render_admin_backup_tab()
"""

# ============================================================================
# BEISPIEL 2: Scheduler beim Anwendungsstart aktivieren
# ============================================================================

"""
# In gui.py oder main.py (am Anfang der Datei)

import streamlit as st
from crm.utils.backup_scheduler import start_scheduler, get_scheduler_status

# Initialisiere Scheduler beim ersten Laden
if 'backup_scheduler_initialized' not in st.session_state:
    success, message = start_scheduler()
    if success:
        st.success(f"{message}", icon="🗄️")
    else:
        # APScheduler nicht installiert oder bereits gestartet
        if "bereits" not in message.lower():
            st.warning(f"{message}", icon="🗄️")
    
    st.session_state.backup_scheduler_initialized = True
"""

# ============================================================================
# BEISPIEL 3: Manuelles Backup vor kritischen Operationen
# ============================================================================

"""
# In database.py oder migrations.py

from crm.utils.backup_scheduler import create_backup

def perform_database_migration():
    # Erstelle Sicherheits-Backup vor Migration
    st.info("Erstelle Sicherheits-Backup vor Migration...")
    success, message = create_backup("manual")
    
    if not success:
        st.error(f"Backup fehlgeschlagen: {message}")
        st.error("Migration wird abgebrochen!")
        return False
    
    st.success(f"{message}")
    
    # Führe Migration durch
    try:
        # ... Migration Code ...
        st.success("Migration erfolgreich!")
        return True
    except Exception as e:
        st.error(f"Migration fehlgeschlagen: {e}")
        st.warning("Sie können das Backup wiederherstellen im Admin-Panel → Backup-Verwaltung")
        return False
"""

# ============================================================================
# BEISPIEL 4: Backup-Status im Dashboard anzeigen
# ============================================================================

"""
# In crm_dashboard_ui.py

from crm.utils.backup_scheduler import get_backup_statistics, get_scheduler_status

def render_crm_dashboard():
    st.title("CRM Dashboard")
    
    # Backup-Status Widget
    with st.expander("🗄️ Backup-Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        # Hole Statistiken
        stats = get_backup_statistics()
        scheduler_status = get_scheduler_status()
        
        with col1:
            st.metric(
                "Gesamt Backups",
                stats["total_backups"],
                delta=None
            )
        
        with col2:
            status_icon = "🟢" if scheduler_status["running"] else "🔴"
            st.metric(
                "Scheduler",
                f"{status_icon} {'Aktiv' if scheduler_status['running'] else 'Inaktiv'}"
            )
        
        with col3:
            st.metric(
                "Letztes Backup",
                stats["latest_backup"]
            )
        
        # Warnung wenn keine Backups
        if stats["total_backups"] == 0:
            st.warning("Keine Backups vorhanden! Erstellen Sie ein Backup im Admin-Panel.")
        
        # Link zum Admin-Panel
        st.info("Verwalten Sie Backups im Admin-Panel → Backup-Verwaltung")
"""

# ============================================================================
# BEISPIEL 5: Backup-Benachrichtigungen
# ============================================================================

"""
# In crm/utils/backup_notifications.py (optional)

import streamlit as st
from datetime import datetime, timedelta
from crm.utils.backup_scheduler import get_backup_statistics

def check_backup_health():
    '''Prüft Backup-Gesundheit und zeigt Warnungen an.'''
    
    stats = get_backup_statistics()
    
    # Warnung: Keine Backups
    if stats["total_backups"] == 0:
        st.warning(
            "**Keine Backups vorhanden!**\\n\\n"
            "Erstellen Sie ein Backup im Admin-Panel → Backup-Verwaltung",
            icon="🗄️"
        )
        return
    
    # Warnung: Letztes Backup zu alt
    latest_backup_str = stats["latest_backup"]
    if latest_backup_str != "Keine Backups":
        try:
            latest_backup = datetime.strptime(latest_backup_str, "%Y-%m-%d %H:%M:%S")
            days_old = (datetime.now() - latest_backup).days
            
            if days_old > 7:
                st.warning(
                    f"**Letztes Backup ist {days_old} Tage alt!**\\n\\n"
                    "Erstellen Sie ein neues Backup oder aktivieren Sie den Scheduler.",
                    icon="🗄️"
                )
        except:
            pass
    
    # Info: Backup-Größe wird groß
    if stats["total_size_mb"] > 1000:  # > 1 GB
        st.info(
            f"**Backup-Verzeichnis wird groß:** {stats['total_size_mb']} MB\\n\\n"
            "Erwägen Sie, alte Backups zu löschen.",
            icon="🗄️"
        )

# In gui.py oder crm_dashboard_ui.py aufrufen:
# check_backup_health()
"""

# ============================================================================
# BEISPIEL 6: Backup vor Datenbank-Operationen
# ============================================================================

"""
# In database.py

from crm.utils.backup_scheduler import create_backup
import functools

def with_backup(func):
    '''Decorator: Erstellt automatisch Backup vor Datenbank-Operation.'''
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Erstelle Backup
        success, message = create_backup("manual")
        if not success:
            print(f"Backup fehlgeschlagen: {message}")
            # Optional: Operation trotzdem durchführen oder abbrechen
        
        # Führe Original-Funktion aus
        return func(*args, **kwargs)
    
    return wrapper

# Verwendung:
@with_backup
def delete_all_customers():
    '''Löscht alle Kunden (mit automatischem Backup).'''
    # ... Lösch-Code ...
    pass

@with_backup
def reset_database():
    '''Setzt Datenbank zurück (mit automatischem Backup).'''
    # ... Reset-Code ...
    pass
"""

# ============================================================================
# BEISPIEL 7: Backup-Download-Button
# ============================================================================

"""
# In admin_panel.py oder backup_ui.py

import streamlit as st
from crm.utils.backup_scheduler import list_backups

def render_backup_download_section():
    '''Zeigt Download-Buttons für Backups.'''
    
    st.subheader("📥 Backups herunterladen")
    
    backups = list_backups()
    
    if not backups:
        st.info("Keine Backups zum Herunterladen verfügbar.")
        return
    
    for backup in backups[:5]:  # Zeige nur die 5 neuesten
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{backup['filename']}**")
            st.caption(f"{backup['created_str']} - {backup['size_mb']} MB")
        
        with col2:
            # Download-Button
            with open(backup['path'], 'rb') as f:
                st.download_button(
                    label="📥 Download",
                    data=f,
                    file_name=backup['filename'],
                    mime="application/x-sqlite3",
                    key=f"download_{backup['filename']}"
                )
        
        with col3:
            # Info-Button
            if st.button("", key=f"info_{backup['filename']}"):
                st.info(
                    f"**Typ:** {backup['type']}\\n"
                    f"**Größe:** {backup['size_mb']} MB\\n"
                    f"**Pfad:** `{backup['path']}`"
                )
"""

# ============================================================================
# BEISPIEL 8: Backup-Upload (Wiederherstellung von externer Datei)
# ============================================================================

"""
# In admin_panel.py oder backup_ui.py

import streamlit as st
from crm.utils.backup_scheduler import restore_backup
import tempfile
import os

def render_backup_upload_section():
    '''Ermöglicht Upload und Wiederherstellung von Backup-Dateien.'''
    
    st.subheader("📤 Backup hochladen und wiederherstellen")
    
    uploaded_file = st.file_uploader(
        "Wählen Sie eine Backup-Datei (.db)",
        type=['db'],
        help="Laden Sie eine Backup-Datei hoch, um sie wiederherzustellen"
    )
    
    if uploaded_file is not None:
        st.info(f"Datei: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")
        
        if st.button("🔄 Backup wiederherstellen", type="primary"):
            # Warnung anzeigen
            st.warning(
                "**ACHTUNG:** Die aktuelle Datenbank wird überschrieben!\\n\\n"
                "Ein Sicherheits-Backup wird automatisch erstellt."
            )
            
            # Bestätigung
            if st.checkbox("Ich verstehe und möchte fortfahren"):
                # Speichere Upload temporär
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Stelle Backup wieder her
                    with st.spinner("Stelle Backup wieder her..."):
                        success, message = restore_backup(tmp_path)
                    
                    if success:
                        st.success(f"{message}")
                        st.info("Bitte starten Sie die Anwendung neu.")
                    else:
                        st.error(f"{message}")
                finally:
                    # Lösche temporäre Datei
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
"""

# ============================================================================
# VOLLSTÄNDIGES INTEGRATIONS-BEISPIEL
# ============================================================================

"""
# admin_panel.py - Vollständige Integration

import streamlit as st
from crm.utils.backup_ui import render_admin_backup_tab
from crm.utils.backup_scheduler import start_scheduler, get_scheduler_status

def render_admin_panel():
    '''Rendert das Admin-Panel mit Backup-Integration.'''
    
    st.title("⚙️ Admin-Panel")
    
    # Scheduler-Status in Sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🗄️ Backup-Status")
        
        status = get_scheduler_status()
        if status["running"]:
            st.success("Scheduler aktiv")
        else:
            st.warning("Scheduler inaktiv")
            if st.button("▶️ Scheduler starten"):
                success, message = start_scheduler()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Tabs
    tabs = st.tabs([
        "Produkte",
        "Preise",
        "PDF-Einstellungen",
        "👥 Benutzer",
        "🗄️ Backup"
    ])
    
    with tabs[0]:
        render_product_admin_ui()
    
    with tabs[1]:
        render_price_matrix_tab()
    
    with tabs[2]:
        render_pdf_settings_ui()
    
    with tabs[3]:
        render_user_management_tab()
    
    with tabs[4]:
        # BACKUP-VERWALTUNG
        render_admin_backup_tab()

if __name__ == "__main__":
    render_admin_panel()
"""

# ============================================================================
# HINWEISE
# ============================================================================

"""
WICHTIGE HINWEISE:

1. APScheduler installieren:
   pip install apscheduler

2. Scheduler beim Start aktivieren:
   - In gui.py oder main.py
   - Nur einmal beim Anwendungsstart
   - Läuft dann im Hintergrund

3. Backup-Verzeichnis:
   - Wird automatisch erstellt
   - Standardpfad: ./backups/
   - Kann in backup_scheduler.py angepasst werden

4. Scheduler-Jobs:
   - Täglich: 2:00 Uhr
   - Wöchentlich: Sonntag 3:00 Uhr
   - Monatlich: 1. des Monats 4:00 Uhr

5. Backup-Rotation:
   - Automatisch bei jedem neuen Backup
   - Älteste Backups werden zuerst gelöscht
   - Limits: 7 täglich, 4 wöchentlich, 12 monatlich

6. Sicherheits-Backup:
   - Wird automatisch vor Wiederherstellung erstellt
   - Gespeichert als "before_restore_*.db"
   - Ermöglicht Rollback bei Problemen

7. Fehlerbehandlung:
   - Alle Funktionen geben (success, message) zurück
   - Keine Exceptions nach außen
   - Detaillierte Fehlermeldungen

8. Performance:
   - Backup-Erstellung: < 1 Sekunde (für kleine DBs)
   - Rotation: < 1 Sekunde
   - Wiederherstellung: < 2 Sekunden
   - Scheduler: Minimal CPU-Last

9. Speicherplatz:
   - Durchschnittliche Backup-Größe: 1-10 MB
   - Maximum bei voller Rotation: ~230 MB
   - (7 täglich + 4 wöchentlich + 12 monatlich + 10 manuell = 33 Backups)

10. Monitoring:
    - Scheduler-Status: get_scheduler_status()
    - Backup-Statistiken: get_backup_statistics()
    - Backup-Liste: list_backups()
"""

print("=" * 70)
print("BACKUP-SYSTEM INTEGRATION - BEISPIELE")
print("=" * 70)
print()
print("Dieses Modul enthält Beispiele für die Integration des Backup-Systems.")
print()
print("Siehe Kommentare im Code für detaillierte Beispiele:")
print("  1. Integration in admin_panel.py")
print("  2. Scheduler beim Anwendungsstart")
print("  3. Manuelles Backup vor kritischen Operationen")
print("  4. Backup-Status im Dashboard")
print("  5. Backup-Benachrichtigungen")
print("  6. Backup vor Datenbank-Operationen")
print("  7. Backup-Download-Button")
print("  8. Backup-Upload und Wiederherstellung")
print()
print("Für vollständige Dokumentation siehe:")
print("  docs/BACKUP_SYSTEM_QUICK_REFERENCE.md")
print("=" * 70)
