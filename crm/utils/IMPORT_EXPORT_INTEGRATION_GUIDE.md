# Import/Export Integration Guide

## Übersicht

Diese Anleitung beschreibt, wie das Import/Export-System in das Admin-Panel integriert wird.

**Voraussetzungen:**
- ✅ `crm/utils/import_export_manager.py` implementiert
- ✅ `crm/utils/import_export_ui.py` implementiert
- ✅ Tests erfolgreich durchgeführt
- ✅ Dokumentation vorhanden

---

## Schritt 1: Admin-Panel erweitern

### 1.1 Import hinzufügen

Öffnen Sie `admin_panel.py` und fügen Sie den Import hinzu:

```python
# Am Anfang der Datei
from crm.utils.import_export_ui import render_import_export_ui
```

### 1.2 Menü-Option hinzufügen

Fügen Sie "Import/Export" zum Menü hinzu:

```python
# Im Admin-Panel-Menü
menu_options = [
    "🏠 Dashboard",
    "⚙️ Einstellungen",
    "📊 Berichte",
    "📥📤 Import/Export",  # NEU
    "👥 Benutzerverwaltung",
    # ... weitere Optionen
]
```

### 1.3 Rendering hinzufügen

Fügen Sie das Rendering für die Import/Export-Seite hinzu:

```python
# Im Hauptbereich des Admin-Panels
if selected_menu == "📥📤 Import/Export":
    render_import_export_ui()
```

---

## Schritt 2: Vollständiges Beispiel

Hier ist ein vollständiges Beispiel für die Integration in `admin_panel.py`:

```python
# admin_panel.py

import streamlit as st
from database import get_db_connection

# Imports für verschiedene Admin-Funktionen
from crm.utils.import_export_ui import render_import_export_ui
# ... weitere Imports

def render_admin_panel():
    """Hauptfunktion für Admin-Panel."""
    
    st.title("⚙️ Admin-Panel")
    
    # Sidebar-Menü
    with st.sidebar:
        st.header("Navigation")
        
        menu_options = [
            "🏠 Dashboard",
            "⚙️ Einstellungen",
            "📊 Berichte",
            "📥📤 Import/Export",  # NEU
            "👥 Benutzerverwaltung",
            "🔒 Sicherheit",
            "💾 Backups",
        ]
        
        selected_menu = st.radio(
            "Menü",
            menu_options,
            label_visibility="collapsed"
        )
    
    # Hauptbereich
    if selected_menu == "🏠 Dashboard":
        render_dashboard()
    
    elif selected_menu == "⚙️ Einstellungen":
        render_settings()
    
    elif selected_menu == "📊 Berichte":
        render_reports()
    
    elif selected_menu == "📥📤 Import/Export":
        render_import_export_ui()  # NEU
    
    elif selected_menu == "👥 Benutzerverwaltung":
        render_user_management()
    
    elif selected_menu == "🔒 Sicherheit":
        render_security()
    
    elif selected_menu == "💾 Backups":
        render_backups()


if __name__ == "__main__":
    render_admin_panel()
```

---

## Schritt 3: Berechtigungen (Optional)

Falls Sie ein Berechtigungssystem haben, fügen Sie Berechtigungsprüfungen hinzu:

```python
# Beispiel mit Berechtigungsprüfung
if selected_menu == "📥📤 Import/Export":
    # Prüfe Berechtigung
    if has_permission(current_user, "import_export"):
        render_import_export_ui()
    else:
        st.error("❌ Keine Berechtigung für Import/Export")
```

---

## Schritt 4: Testen

### 4.1 Admin-Panel starten

```bash
streamlit run admin_panel.py
```

### 4.2 Test-Checkliste

- [ ] Menü-Option "Import/Export" ist sichtbar
- [ ] Export-Tab funktioniert
  - [ ] CSV-Export funktioniert
  - [ ] Excel-Export funktioniert
  - [ ] Statistiken werden angezeigt
  - [ ] Download-Buttons funktionieren
- [ ] Import-Tab funktioniert
  - [ ] CSV-Upload funktioniert
  - [ ] Excel-Upload funktioniert
  - [ ] Feld-Mapping funktioniert
  - [ ] Vorschau wird angezeigt
  - [ ] Import funktioniert
  - [ ] Statistiken werden angezeigt

---

## Schritt 5: Benutzer-Dokumentation

### 5.1 Hilfe-Text hinzufügen

Fügen Sie einen Hilfe-Button im Admin-Panel hinzu:

```python
# Im Import/Export-Bereich
with st.expander("❓ Hilfe", expanded=False):
    st.markdown("""
    ### Import/Export-Hilfe
    
    **Export:**
    1. Wählen Sie Format (CSV oder Excel)
    2. Wählen Sie Felder aus
    3. Optional: Wählen Sie Kunden aus
    4. Klicken Sie auf "Export starten"
    5. Laden Sie die Datei herunter
    
    **Import:**
    1. Laden Sie CSV oder Excel-Datei hoch
    2. Prüfen Sie Feld-Zuordnung
    3. Prüfen Sie Vorschau
    4. Wählen Sie Duplikat-Strategie
    5. Klicken Sie auf "Import starten"
    
    Weitere Informationen: [Dokumentation](docs/IMPORT_EXPORT_QUICK_REFERENCE.md)
    """)
```

### 5.2 Link zur Dokumentation

Fügen Sie einen Link zur vollständigen Dokumentation hinzu:

```python
st.info("📖 [Vollständige Dokumentation](docs/IMPORT_EXPORT_QUICK_REFERENCE.md)")
```

---

## Schritt 6: Logging (Optional)

Fügen Sie Logging für Import/Export-Aktivitäten hinzu:

```python
import logging

# Logger konfigurieren
logger = logging.getLogger(__name__)

# Im Import/Export-Code
def render_import_export_ui():
    logger.info("Import/Export-Seite aufgerufen")
    
    # ... Code ...
    
    if st.button("Export starten"):
        logger.info(f"Export gestartet: Format={format}, Felder={fields}")
        # ... Export-Code ...
        logger.info(f"Export abgeschlossen: {len(csv_data)} Bytes")
```

---

## Schritt 7: Fehlerbehandlung

Fügen Sie globale Fehlerbehandlung hinzu:

```python
def render_import_export_ui():
    try:
        # ... Import/Export-Code ...
        pass
    except Exception as e:
        st.error(f"❌ Fehler im Import/Export-System: {str(e)}")
        logger.error(f"Import/Export-Fehler: {str(e)}", exc_info=True)
        
        # Optional: Fehler-Details für Admins
        if st.session_state.get('is_admin'):
            with st.expander("🔍 Fehlerdetails (nur für Admins)"):
                st.code(traceback.format_exc())
```

---

## Schritt 8: Performance-Optimierung

### 8.1 Caching

Nutzen Sie Streamlit-Caching für häufige Abfragen:

```python
@st.cache_data(ttl=300)  # Cache für 5 Minuten
def get_cached_export_statistics(db_path):
    conn = get_db_connection()
    stats = get_export_statistics(conn)
    conn.close()
    return stats
```

### 8.2 Fortschrittsanzeige

Fügen Sie Fortschrittsanzeigen für lange Operationen hinzu:

```python
if st.button("Import starten"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Import durchführen
    for i, row in enumerate(rows):
        # ... Import-Code ...
        progress = (i + 1) / len(rows)
        progress_bar.progress(progress)
        status_text.text(f"Importiere Zeile {i+1} von {len(rows)}")
    
    progress_bar.empty()
    status_text.empty()
    st.success("✅ Import abgeschlossen!")
```

---

## Schritt 9: Sicherheit

### 9.1 Datei-Upload-Limits

Konfigurieren Sie Upload-Limits in `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200  # MB
```

### 9.2 Validierung

Validieren Sie hochgeladene Dateien:

```python
def validate_upload(uploaded_file):
    """Validiert hochgeladene Datei."""
    
    # Dateigröße prüfen
    if uploaded_file.size > 200 * 1024 * 1024:  # 200 MB
        return False, "Datei zu groß (max. 200 MB)"
    
    # Dateiformat prüfen
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return False, f"Ungültiges Format (erlaubt: {', '.join(allowed_extensions)})"
    
    return True, "OK"

# Verwendung
if uploaded_file:
    valid, message = validate_upload(uploaded_file)
    if not valid:
        st.error(f"❌ {message}")
        return
```

### 9.3 SQL-Injection-Schutz

Das System verwendet bereits Prepared Statements, aber prüfen Sie zusätzlich:

```python
# Bereits implementiert in import_export_manager.py
cursor.execute(
    "INSERT INTO customers (first_name, last_name) VALUES (?, ?)",
    (first_name, last_name)  # Sichere Parameter-Bindung
)
```

---

## Schritt 10: Monitoring

### 10.1 Aktivitäts-Tracking

Tracken Sie Import/Export-Aktivitäten:

```python
def log_import_activity(user_id, stats):
    """Loggt Import-Aktivität."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO activity_log (
            user_id, activity_type, details, timestamp
        ) VALUES (?, ?, ?, ?)
    """, (
        user_id,
        'import',
        json.dumps(stats),
        datetime.now()
    ))
    
    conn.commit()
    conn.close()
```

### 10.2 Fehler-Tracking

Tracken Sie Fehler:

```python
def log_import_error(user_id, error_message):
    """Loggt Import-Fehler."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO error_log (
            user_id, error_type, error_message, timestamp
        ) VALUES (?, ?, ?, ?)
    """, (
        user_id,
        'import_error',
        error_message,
        datetime.now()
    ))
    
    conn.commit()
    conn.close()
```

---

## Troubleshooting

### Problem: Import/Export-Menü wird nicht angezeigt

**Lösung:**
1. Prüfen Sie, ob Import korrekt ist
2. Prüfen Sie, ob Menü-Option hinzugefügt wurde
3. Prüfen Sie Berechtigungen

### Problem: Upload funktioniert nicht

**Lösung:**
1. Prüfen Sie Upload-Limits in `.streamlit/config.toml`
2. Prüfen Sie Dateigröße
3. Prüfen Sie Dateiformat

### Problem: Import schlägt fehl

**Lösung:**
1. Prüfen Sie Datenbankverbindung
2. Prüfen Sie Feld-Mapping
3. Prüfen Sie Validierung
4. Prüfen Sie Logs

### Problem: Performance-Probleme

**Lösung:**
1. Nutzen Sie Batch-Import
2. Aktivieren Sie Caching
3. Reduzieren Sie Datenmenge
4. Optimieren Sie Datenbank-Indizes

---

## Best Practices

1. **Testen Sie gründlich** vor Produktiv-Einsatz
2. **Erstellen Sie Backups** vor großen Imports
3. **Dokumentieren Sie** Änderungen
4. **Schulen Sie Benutzer** im Umgang mit Import/Export
5. **Überwachen Sie** Aktivitäten und Fehler
6. **Optimieren Sie** Performance bei Bedarf
7. **Validieren Sie** Daten vor Import
8. **Prüfen Sie** Duplikate
9. **Nutzen Sie** Vorschau-Funktion
10. **Sichern Sie** sensible Daten

---

## Checkliste für Produktiv-Einsatz

- [ ] Integration in Admin-Panel abgeschlossen
- [ ] Tests erfolgreich durchgeführt
- [ ] Berechtigungen konfiguriert
- [ ] Logging aktiviert
- [ ] Fehlerbehandlung implementiert
- [ ] Performance optimiert
- [ ] Sicherheit geprüft
- [ ] Monitoring eingerichtet
- [ ] Dokumentation erstellt
- [ ] Benutzer geschult
- [ ] Backup-Strategie definiert
- [ ] Rollback-Plan vorhanden

---

## Weitere Ressourcen

- **Modul-Dokumentation:** `crm/utils/IMPORT_EXPORT_REFERENCE.md`
- **Quick Reference:** `docs/IMPORT_EXPORT_QUICK_REFERENCE.md`
- **Task Summary:** `TASK_13_IMPORT_EXPORT_COMPLETE.md`
- **Tests:** `crm/utils/test_import_export_manager.py`

---

## Support

Bei Fragen oder Problemen:

1. Prüfen Sie die Dokumentation
2. Prüfen Sie die Logs
3. Führen Sie Tests aus
4. Kontaktieren Sie den Support

---

**Version:** 1.0  
**Datum:** 2025-01-14  
**Autor:** Kiro AI Assistant
