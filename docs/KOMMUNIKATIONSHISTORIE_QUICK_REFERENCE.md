# Kommunikationshistorie - Quick Reference

## Schnellstart

### Aktivität erstellen

```python
from crm.features.note_manager import add_note, add_email_activity, add_call_activity

# Notiz hinzufügen
note_id = add_note(
    customer_id=1,
    title="Wichtige Besprechung",
    content="Details...",
    created_by="Max Mustermann",
    is_important=True
)

# E-Mail-Aktivität
email_id = add_email_activity(
    customer_id=1,
    subject="Angebot",
    body="Sehr geehrter..."
)

# Anruf protokollieren
call_id = add_call_activity(
    customer_id=1,
    title="Rückruf",
    notes="Kunde hat Fragen..."
)
```

### Timeline anzeigen

```python
from crm.features.note_ui import render_activity_timeline

# In Streamlit
render_activity_timeline(customer_id=1, show_filters=True)
```

### Suchen

```python
from crm.features.note_manager import search_activities

# Suche
results = search_activities(
    "Finanzierung",
    customer_id=1,
    activity_type="call"
)
```

## Aktivitätstypen

- `note` - Notiz
- `email` - E-Mail
- `call` - Anruf
- `appointment` - Termin
- `meeting` - Besprechung
- `task` - Aufgabe
- `other` - Sonstiges

## UI-Komponenten

```python
from crm.features.note_ui import (
    render_activity_timeline,      # Vollständige Timeline
    render_add_activity_form,       # Formular zum Hinzufügen
    render_quick_add_buttons,       # Schnellzugriff-Buttons
    render_activity_summary         # Kompakte Zusammenfassung
)
```

## Wichtige Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| `create_activity()` | Neue Aktivität erstellen |
| `get_activity()` | Einzelne Aktivität abrufen |
| `get_customer_activities()` | Alle Aktivitäten eines Kunden |
| `update_activity()` | Aktivität aktualisieren |
| `delete_activity()` | Aktivität löschen |
| `toggle_important()` | Wichtig-Status umschalten |
| `search_activities()` | Volltextsuche |
| `auto_archive_old_activities()` | Alte Aktivitäten archivieren |
| `get_activity_statistics()` | Statistiken abrufen |

## Features

✅ CRUD-Operationen  
✅ Timeline-Ansicht  
✅ Volltextsuche  
✅ Wichtig-Markierung  
✅ Auto-Archivierung  
✅ Filterung nach Typ  
✅ Statistiken  
✅ UI-Komponenten  

## Tests ausführen

```bash
python -m pytest crm/features/test_note_manager.py -v
```

33 Tests - Alle bestanden ✅

## Dokumentation

Vollständige Dokumentation: `crm/features/NOTE_MANAGER_REFERENCE.md`
