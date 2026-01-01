# Notizen und Kommunikationshistorie - Referenzdokumentation

## Übersicht

Das Notizen- und Kommunikationshistorie-System ermöglicht die zentrale Verwaltung aller Kundeninteraktionen in einer chronologischen Timeline mit Volltextsuche und Filterung.

## Module

### 1. note_manager.py

Kern-Modul mit allen CRUD-Funktionen und Business-Logik.

#### Aktivitätstypen

```python
ACTIVITY_TYPES = {
    "note": "Notiz",
    "email": "E-Mail",
    "call": "Anruf",
    "appointment": "Termin",
    "meeting": "Besprechung",
    "task": "Aufgabe",
    "other": "Sonstiges"
}
```

#### Hauptfunktionen

**Erstellen:**
```python
# Allgemeine Aktivität
activity_id = create_activity(
    customer_id=1,
    activity_type="note",
    title="Wichtige Besprechung",
    content="Details der Besprechung...",
    created_by="Max Mustermann",
    is_important=True
)

# Helper-Funktionen
note_id = add_note(customer_id, title, content, created_by, is_important)
email_id = add_email_activity(customer_id, subject, body, created_by)
call_id = add_call_activity(customer_id, title, notes, created_by)
appointment_id = add_appointment_activity(customer_id, title, details, created_by)
```

**Abrufen:**
```python
# Einzelne Aktivität
activity = get_activity(activity_id)

# Alle Aktivitäten eines Kunden
activities = get_customer_activities(
    customer_id=1,
    activity_type="note",  # Optional: Filter nach Typ
    include_archived=False,  # Archivierte einschließen?
    limit=100  # Maximale Anzahl
)

# Statistiken
stats = get_activity_statistics(customer_id)
# Returns: {
#     "total": 42,
#     "by_type": {"note": 20, "email": 15, "call": 7},
#     "important": 5,
#     "last_activity": "2024-01-15 14:30:00"
# }
```

**Aktualisieren:**
```python
# Einzelne Felder
success = update_activity(
    activity_id,
    title="Neuer Titel",
    content="Neuer Inhalt",
    is_important=True,
    archived=False
)

# Wichtig-Status umschalten
success = toggle_important(activity_id)
```

**Löschen:**
```python
success = delete_activity(activity_id)
```

**Suchen:**
```python
# Volltextsuche
results = search_activities(
    search_term="Angebot",
    customer_id=1,  # Optional
    activity_type="email",  # Optional
    limit=50
)
```

**Auto-Archivierung:**
```python
# Archiviert Aktivitäten älter als X Tage (außer wichtige)
count = auto_archive_old_activities(days_threshold=30)
```

### 2. note_ui.py

Streamlit UI-Komponenten für die Darstellung und Verwaltung.

#### UI-Funktionen

**Timeline-Ansicht:**
```python
# Vollständige Timeline mit Filtern
render_activity_timeline(customer_id, show_filters=True)
```

**Neue Aktivität hinzufügen:**
```python
# Vollständiges Formular
render_add_activity_form(customer_id)

# Schnellzugriff-Buttons
render_quick_add_buttons(customer_id)
```

**Kompakte Zusammenfassung:**
```python
# Zeigt letzte 3 Aktivitäten
render_activity_summary(customer_id)
```

## Datenbankstruktur

### Tabelle: crm_activities

```sql
CREATE TABLE crm_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_important BOOLEAN DEFAULT 0,
    archived BOOLEAN DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
)
```

## Features

### ✅ Implementiert

1. **CRUD-Operationen**
   - Erstellen, Lesen, Aktualisieren, Löschen von Aktivitäten
   - Alle Aktivitätstypen unterstützt

2. **Timeline-Ansicht**
   - Chronologische Darstellung (neueste zuerst)
   - Filterung nach Typ und Datum
   - Archivierte ein-/ausblenden

3. **Volltextsuche**
   - Suche in Titel und Inhalt
   - Case-insensitive
   - Kombinierbar mit Filtern

4. **Wichtig-Markierung**
   - Aktivitäten als wichtig markieren
   - Wichtige werden nicht auto-archiviert
   - Visuelle Hervorhebung in UI

5. **Auto-Archivierung**
   - Automatisches Archivieren alter Aktivitäten
   - Konfigurierbare Schwelle (Standard: 30 Tage)
   - Wichtige Aktivitäten werden ausgenommen

6. **Statistiken**
   - Gesamtanzahl Aktivitäten
   - Aufschlüsselung nach Typ
   - Anzahl wichtiger Aktivitäten
   - Letzte Aktivität

7. **UI-Komponenten**
   - Timeline mit Karten-Layout
   - Inline-Bearbeitung
   - Schnellzugriff-Buttons
   - Kompakte Zusammenfassung

## Verwendungsbeispiele

### In CRM-Kundenprofil integrieren

```python
import streamlit as st
from crm.features.note_ui import (
    render_activity_timeline,
    render_add_activity_form,
    render_quick_add_buttons
)

# In der Kundendetail-Ansicht
customer_id = st.session_state.get("selected_customer_id")

if customer_id:
    # Tab für Kommunikationshistorie
    tab1, tab2 = st.tabs(["Timeline", "Neue Aktivität"])
    
    with tab1:
        render_quick_add_buttons(customer_id)
        st.divider()
        render_activity_timeline(customer_id)
    
    with tab2:
        render_add_activity_form(customer_id)
```

### Automatische Aktivitäten erstellen

```python
from crm.features.note_manager import add_email_activity, add_call_activity

# Nach E-Mail-Versand
email_id = add_email_activity(
    customer_id=customer_id,
    subject="Angebot PV-Anlage",
    body="Sehr geehrter Herr Müller, anbei unser Angebot...",
    created_by="System"
)

# Nach Telefonat
call_id = add_call_activity(
    customer_id=customer_id,
    title="Rückruf wegen Angebot",
    notes="Kunde hat Fragen zur Finanzierung. Termin vereinbart für nächste Woche.",
    created_by="Max Mustermann"
)
```

### Suche implementieren

```python
from crm.features.note_manager import search_activities

# Globale Suche über alle Kunden
results = search_activities("Finanzierung")

# Suche nur für einen Kunden
results = search_activities(
    "Finanzierung",
    customer_id=customer_id,
    activity_type="call"
)

# Ergebnisse anzeigen
for activity in results:
    st.write(f"{activity['activity_type_display']}: {activity['title']}")
    st.caption(activity['created_at'])
```

### Regelmäßige Wartung

```python
from crm.features.note_manager import auto_archive_old_activities

# In einem Scheduler (z.B. täglich)
archived_count = auto_archive_old_activities(days_threshold=30)
print(f"{archived_count} Aktivitäten archiviert")
```

## Tests

Umfassende Test-Suite mit 33 Tests:

```bash
# Alle Tests ausführen
python -m pytest crm/features/test_note_manager.py -v

# Spezifische Test-Klasse
python -m pytest crm/features/test_note_manager.py::TestActivityCreation -v

# Mit Coverage
python -m pytest crm/features/test_note_manager.py --cov=crm.features.note_manager
```

### Test-Kategorien

1. **TestActivityCreation** (8 Tests)
   - Erstellen mit allen Typen
   - Validierung
   - Helper-Funktionen

2. **TestActivityRetrieval** (7 Tests)
   - Einzelne Aktivität abrufen
   - Listen mit Filtern
   - Limit und Sortierung

3. **TestActivityUpdate** (7 Tests)
   - Einzelne Felder
   - Mehrere Felder
   - Toggle-Funktionen

4. **TestActivityDeletion** (2 Tests)
   - Erfolgreiches Löschen
   - Fehlerbehandlung

5. **TestActivitySearch** (5 Tests)
   - Suche in Titel und Inhalt
   - Case-insensitive
   - Mit Filtern

6. **TestActivityArchiving** (2 Tests)
   - Auto-Archivierung
   - Wichtige ausgenommen

7. **TestActivityStatistics** (2 Tests)
   - Statistiken abrufen
   - Leere Statistiken

## Performance-Hinweise

1. **Indizes empfohlen:**
   ```sql
   CREATE INDEX idx_activities_customer ON crm_activities(customer_id);
   CREATE INDEX idx_activities_type ON crm_activities(activity_type);
   CREATE INDEX idx_activities_created ON crm_activities(created_at);
   ```

2. **Volltextsuche optimieren:**
   - Für große Datenmengen SQLite FTS5 verwenden
   - Aktuell: Einfache LIKE-Suche (ausreichend für < 10.000 Aktivitäten)

3. **Pagination:**
   - Limit-Parameter verwenden
   - Standard: 100 Aktivitäten pro Abfrage

## Zukünftige Erweiterungen

### Geplant (Optional)

1. **SQLite FTS5 Volltextsuche**
   - Schnellere Suche bei großen Datenmengen
   - Erweiterte Suchoperatoren

2. **Anhänge**
   - Dateien an Aktivitäten anhängen
   - Bilder, PDFs, etc.

3. **Erwähnungen**
   - @-Mentions für Teammitglieder
   - Benachrichtigungen

4. **Aktivitäts-Templates**
   - Vordefinierte Vorlagen
   - Schnelleres Erstellen

5. **Export**
   - Timeline als PDF exportieren
   - CSV-Export für Analysen

## Anforderungen erfüllt

✅ **Requirement 6.1:** Notizen mit Zeitstempel und Benutzer  
✅ **Requirement 6.2:** Chronologische Timeline aller Aktivitäten  
✅ **Requirement 6.3:** Volltextsuche  
✅ **Requirement 6.4:** Wichtig-Markierung  
✅ **Requirement 6.5:** Archivierung alter Aktivitäten  

## Support

Bei Fragen oder Problemen:
- Siehe Tests für Verwendungsbeispiele
- Prüfe Konsolenausgabe für Fehlermeldungen
- Stelle sicher, dass `crm_activities` Tabelle existiert
