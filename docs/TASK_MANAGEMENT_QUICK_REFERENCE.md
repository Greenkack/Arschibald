# Task Management - Quick Reference

## Übersicht

Das Task Management System ermöglicht die vollständige Verwaltung von Aufgaben im CRM mit Status-Workflow, Prioritäten, Fälligkeitsdaten und Benachrichtigungen.

## Features

### ✅ Implementierte Funktionen

1. **CRUD-Operationen**
   - Aufgaben erstellen, lesen, aktualisieren, löschen
   - Vollständige Datenbankintegration

2. **Status-Workflow**
   - `open` - Offen
   - `in_progress` - In Arbeit
   - `completed` - Erledigt

3. **Prioritäten**
   - `low` - Niedrig (🔵)
   - `medium` - Mittel (🟡)
   - `high` - Hoch (🔴)

4. **Zuordnungen**
   - Kunde (customer_id)
   - Projekt (project_id)
   - Lead (lead_id)
   - Zugewiesener Benutzer (assigned_to)

5. **Fälligkeitsverwaltung**
   - Fälligkeitsdatum setzen
   - Überfällige Tasks erkennen
   - Benachrichtigungen für fällige Tasks

6. **Filterung**
   - Nach Status
   - Nach Priorität
   - Nach Fälligkeit
   - Nach Zuordnung

7. **Dashboard-Integration**
   - KPI-Cards mit Statistiken
   - Übersichts-Dashboard
   - Benachrichtigungs-Center

## Verwendung

### Python API

```python
from crm.features.task_manager import (
    create_task,
    get_task,
    update_task,
    delete_task,
    get_all_tasks,
    get_overdue_tasks,
    mark_task_completed
)

# Task erstellen
task_id = create_task(
    title="Kunde anrufen",
    description="Angebot besprechen",
    priority="high",
    due_date=date.today() + timedelta(days=3),
    customer_id=123
)

# Task laden
task = get_task(task_id)

# Task aktualisieren
update_task(task_id, status="in_progress")

# Task als erledigt markieren
mark_task_completed(task_id)

# Alle überfälligen Tasks
overdue = get_overdue_tasks()

# Tasks filtern
tasks = get_all_tasks(
    status="open",
    priority="high",
    customer_id=123
)
```

### UI-Integration

```python
from crm.features.task_ui import render_task_management_ui

# Vollständige Task-UI rendern
render_task_management_ui(texts=texts)

# Mit Filterung nach Kunde
render_task_management_ui(
    texts=texts,
    customer_id=123
)
```

### In CRM Dashboard

Das Task Management ist automatisch im CRM Dashboard integriert:
- Tab "📋 Aufgaben" im Dashboard
- Zugriff über `crm_dashboard_ui.py`

## Datenbankschema

```sql
CREATE TABLE crm_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'medium',
    due_date DATE,
    customer_id INTEGER,
    project_id INTEGER,
    lead_id INTEGER,
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_id) REFERENCES crm_leads(id) ON DELETE CASCADE
)
```

## Funktions-Referenz

### CRUD-Funktionen

#### `create_task()`
Erstellt eine neue Aufgabe.

**Parameter:**
- `title` (str, erforderlich): Titel der Aufgabe
- `description` (str): Beschreibung
- `status` (str): 'open', 'in_progress', 'completed'
- `priority` (str): 'low', 'medium', 'high'
- `due_date` (date): Fälligkeitsdatum
- `customer_id` (int): Kundenzuordnung
- `project_id` (int): Projektzuordnung
- `lead_id` (int): Lead-Zuordnung
- `assigned_to` (str): Zugewiesener Benutzer

**Returns:** Task-ID oder None

#### `get_task(task_id)`
Lädt eine einzelne Aufgabe.

**Returns:** Task-Dictionary oder None

#### `update_task(task_id, **kwargs)`
Aktualisiert eine Aufgabe. Nur übergebene Parameter werden geändert.

**Returns:** True bei Erfolg, False bei Fehler

#### `delete_task(task_id)`
Löscht eine Aufgabe.

**Returns:** True bei Erfolg, False bei Fehler

### Abfrage-Funktionen

#### `get_all_tasks(**filters)`
Lädt alle Tasks mit optionaler Filterung.

**Filter-Parameter:**
- `status`: Filter nach Status
- `priority`: Filter nach Priorität
- `customer_id`: Filter nach Kunde
- `project_id`: Filter nach Projekt
- `lead_id`: Filter nach Lead
- `assigned_to`: Filter nach Zugewiesenem
- `overdue_only`: Nur überfällige Tasks
- `due_soon_days`: Tasks die in X Tagen fällig sind

**Returns:** Liste von Task-Dictionaries

#### `get_overdue_tasks()`
Lädt alle überfälligen Tasks.

#### `get_tasks_due_soon(days=7)`
Lädt alle Tasks die in den nächsten X Tagen fällig sind.

#### `get_tasks_by_customer(customer_id)`
Lädt alle Tasks für einen Kunden.

#### `get_tasks_by_project(project_id)`
Lädt alle Tasks für ein Projekt.

### Status-Workflow

#### `mark_task_in_progress(task_id)`
Setzt Status auf 'in_progress'.

#### `mark_task_completed(task_id)`
Setzt Status auf 'completed' und setzt completed_at Timestamp.

#### `reopen_task(task_id)`
Setzt Status zurück auf 'open' und löscht completed_at.

### Statistiken

#### `get_task_statistics()`
Liefert umfassende Statistiken über alle Tasks.

**Returns:**
```python
{
    'total': 42,
    'by_status': {'open': 15, 'in_progress': 8, 'completed': 19},
    'by_priority': {'high': 5, 'medium': 12, 'low': 6},
    'overdue': 3,
    'due_today': 2,
    'due_this_week': 7
}
```

### Benachrichtigungen

#### `get_tasks_needing_notification()`
Liefert alle Tasks die eine Benachrichtigung benötigen (überfällig, heute, morgen).

**Returns:** Liste von Tasks mit zusätzlichen Feldern:
- `notification_type`: 'overdue', 'due_today', 'due_tomorrow'
- `notification_priority`: 'high', 'medium', 'low'

### Hilfsfunktionen

#### `is_task_overdue(task)`
Prüft ob ein Task überfällig ist.

#### `get_task_display_color(task)`
Liefert Hex-Farbcode für Task-Anzeige.

#### `format_task_for_display(task)`
Formatiert Task mit zusätzlichen Display-Informationen:
- `is_overdue`: Boolean
- `display_color`: Hex-Farbe
- `status_label`: Formatiertes Status-Label
- `priority_label`: Formatiertes Prioritäts-Label
- `due_date_label`: Formatiertes Fälligkeits-Label

## UI-Komponenten

### Dashboard-Tabs

1. **📊 Übersicht**
   - KPI-Cards (Gesamt, Aktiv, Überfällig, Erledigt)
   - Prioritäten-Übersicht
   - Fälligkeits-Übersicht

2. **📝 Alle Aufgaben**
   - Filterbare Task-Liste
   - Task-Cards mit Aktions-Buttons
   - Inline-Bearbeitung

3. **➕ Neue Aufgabe**
   - Formular zum Erstellen
   - Alle Felder verfügbar
   - Validierung

4. **⚠️ Benachrichtigungen**
   - Überfällige Tasks (Rot)
   - Heute fällige Tasks (Orange)
   - Morgen fällige Tasks (Info)

### Task-Card Aktionen

- 🔄 **In Arbeit**: Setzt Status auf 'in_progress'
- ✅ **Erledigt**: Setzt Status auf 'completed'
- 🔓 **Wieder öffnen**: Setzt Status zurück auf 'open'
- ✏️ **Bearbeiten**: Öffnet Bearbeitungs-Formular
- 🗑️ **Löschen**: Löscht Task (mit Bestätigung)

## Best Practices

### 1. Task-Erstellung

```python
# Immer einen aussagekräftigen Titel verwenden
task_id = create_task(
    title="Angebot für Projekt XY erstellen",
    description="Detaillierte Beschreibung mit allen relevanten Infos",
    priority="high",
    due_date=date.today() + timedelta(days=3),
    customer_id=customer_id,
    assigned_to="Max Mustermann"
)
```

### 2. Regelmäßige Überprüfung

```python
# Täglich überfällige Tasks prüfen
overdue = get_overdue_tasks()
if overdue:
    for task in overdue:
        print(f"ÜBERFÄLLIG: {task['title']}")
```

### 3. Filterung nutzen

```python
# Nur hochpriorisierte, offene Tasks für einen Kunden
urgent_tasks = get_all_tasks(
    customer_id=123,
    status="open",
    priority="high"
)
```

### 4. Status-Workflow einhalten

```python
# Korrekter Workflow
task_id = create_task(...)  # Status: 'open'
mark_task_in_progress(task_id)  # Status: 'in_progress'
mark_task_completed(task_id)  # Status: 'completed'

# Bei Bedarf wieder öffnen
reopen_task(task_id)  # Status: 'open'
```

## Fehlerbehebung

### Problem: Tasks werden nicht angezeigt

**Lösung:**
1. Prüfe ob Tabelle existiert: `crm_tasks`
2. Prüfe Datenbankverbindung
3. Prüfe Filter-Einstellungen

### Problem: Benachrichtigungen fehlen

**Lösung:**
1. Prüfe Fälligkeitsdaten
2. Prüfe Status (completed Tasks werden nicht benachrichtigt)
3. Prüfe `get_tasks_needing_notification()`

### Problem: Update schlägt fehl

**Lösung:**
1. Prüfe ob Task existiert
2. Prüfe Validierung (Status, Priorität)
3. Prüfe Datenbankverbindung

## Performance-Tipps

1. **Indizes nutzen**: Tabelle hat bereits Indizes auf wichtigen Spalten
2. **Filter verwenden**: Nicht alle Tasks laden, sondern filtern
3. **Statistiken cachen**: Bei häufigem Zugriff Statistiken zwischenspeichern

## Erweiterungsmöglichkeiten

### Geplante Features (Optional)

1. **Wiederkehrende Tasks**
   - Automatische Erstellung nach Zeitplan
   - Regel-Engine für Wiederholungen

2. **Task-Vorlagen**
   - Vordefinierte Task-Templates
   - Schnelle Erstellung häufiger Tasks

3. **Kommentare**
   - Diskussionen zu Tasks
   - Aktivitäts-Log

4. **Dateianhänge**
   - Dokumente an Tasks anhängen
   - Integration mit Kundenakte

5. **E-Mail-Benachrichtigungen**
   - Automatische E-Mails bei Fälligkeit
   - Eskalations-Workflow

## Support

Bei Fragen oder Problemen:
1. Prüfe diese Dokumentation
2. Prüfe Modul-Docstrings
3. Prüfe Datenbank-Schema
4. Teste mit Beispiel-Code

## Changelog

### Version 1.0 (2025-01-13)
- ✅ Initiale Implementierung
- ✅ CRUD-Operationen
- ✅ Status-Workflow
- ✅ Prioritäten
- ✅ Filterung
- ✅ Dashboard-Integration
- ✅ Benachrichtigungen
- ✅ UI-Komponenten

---

**Autor:** Kiro AI  
**Datum:** 2025-01-13  
**Version:** 1.0
