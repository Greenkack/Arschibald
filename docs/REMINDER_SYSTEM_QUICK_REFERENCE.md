# Erinnerungssystem - Quick Reference

## Übersicht

Das Erinnerungssystem ermöglicht automatische Follow-ups und manuelle Erinnerungen für Leads, Angebote, Termine und Kunden.

## Automatische Erinnerungs-Regeln

### 1. Lead Follow-up
- **Trigger:** Neuer Lead erstellt
- **Follow-up:** Nach 3 Tagen
- **Verwendung:**
```python
from crm.utils.notification_manager import create_reminder_for_lead

reminder_id = create_reminder_for_lead(
    lead_id=123,
    lead_name="Max Mustermann"
)
```

### 2. Angebots Follow-up
- **Trigger:** Angebot versendet
- **Follow-up:** Nach 7 Tagen
- **Verwendung:**
```python
from crm.utils.notification_manager import create_reminder_for_offer

reminder_id = create_reminder_for_offer(
    project_id=456,
    project_name="PV-Anlage 15kWp"
)
```

### 3. Termin Follow-up
- **Trigger:** Termin abgeschlossen
- **Follow-up:** Nach 1 Tag
- **Verwendung:**
```python
from crm.utils.notification_manager import create_reminder_for_appointment

reminder_id = create_reminder_for_appointment(
    appointment_id=789,
    appointment_title="Vor-Ort Besichtigung"
)
```

## Manuelle Erinnerungen

```python
from crm.utils.notification_manager import create_manual_reminder
from datetime import date, timedelta

reminder_id = create_manual_reminder(
    related_id=123,
    related_type='customer',  # 'customer', 'project', 'lead', 'appointment'
    due_date=date.today() + timedelta(days=5),
    message="Kunde wegen Finanzierung kontaktieren"
)
```

## Erinnerungen verwalten

### Erinnerung laden
```python
from crm.utils.notification_manager import get_reminder

reminder = get_reminder(reminder_id=1)
print(reminder['message'])
print(reminder['due_date'])
print(reminder['status'])
```

### Status aktualisieren
```python
from crm.utils.notification_manager import update_reminder_status

# Als erledigt markieren
update_reminder_status(reminder_id=1, new_status='completed')

# Verwerfen
update_reminder_status(reminder_id=1, new_status='dismissed')
```

### Snooze-Funktion (Verschieben)
```python
from crm.utils.notification_manager import snooze_reminder

# Um 2 Tage verschieben (Standard)
snooze_reminder(reminder_id=1)

# Um X Tage verschieben
snooze_reminder(reminder_id=1, days=5)
```

### Erinnerung löschen
```python
from crm.utils.notification_manager import delete_reminder

delete_reminder(reminder_id=1)
```

## Erinnerungen abfragen

### Alle fälligen Erinnerungen
```python
from crm.utils.notification_manager import get_due_reminders

due_reminders = get_due_reminders()
for reminder in due_reminders:
    print(f"{reminder['message']} - Fällig: {reminder['due_date']}")
```

### Alle Erinnerungen mit Filter
```python
from crm.utils.notification_manager import get_all_reminders

# Nur ausstehende Erinnerungen
pending = get_all_reminders(status='pending')

# Nur Lead-Erinnerungen
lead_reminders = get_all_reminders(related_type='lead')

# Erinnerungen für bestimmtes Objekt
customer_reminders = get_all_reminders(
    related_type='customer',
    related_id=123
)
```

### Erinnerungen nach Typ
```python
from crm.utils.notification_manager import get_reminders_by_type

# Alle Lead Follow-ups
lead_followups = get_reminders_by_type('lead_created')

# Alle Angebots Follow-ups
offer_followups = get_reminders_by_type('offer_sent')
```

## Statistiken

```python
from crm.utils.notification_manager import get_reminder_statistics

stats = get_reminder_statistics()

print(f"Gesamt: {stats['total']}")
print(f"Fällig: {stats['due']}")
print(f"Heute fällig: {stats['due_today']}")
print(f"Nach Status: {stats['by_status']}")
print(f"Nach Typ: {stats['by_type']}")
print(f"Durchschnittliche Snooze-Anzahl: {stats['avg_snooze_count']}")
```

## UI-Integration

### Dashboard-Widget anzeigen
```python
from crm.utils.reminder_ui import render_reminders_widget

# Im Dashboard
render_reminders_widget(texts=translation_texts)
```

### Vollständige Verwaltungs-UI
```python
from crm.utils.reminder_ui import render_reminders_management_ui

# Separate Seite für Erinnerungsverwaltung
render_reminders_management_ui(texts=translation_texts)
```

## Status-Werte

- `pending` - Ausstehend (Standard)
- `completed` - Erledigt
- `snoozed` - Verschoben
- `dismissed` - Verworfen

## Erinnerungs-Typen

- `lead_created` - Lead Follow-up (3 Tage)
- `offer_sent` - Angebots Follow-up (7 Tage)
- `appointment_completed` - Termin Follow-up (1 Tag)
- `manual` - Manuelle Erinnerung

## Verknüpfungs-Typen

- `customer` - Kunde
- `project` - Projekt
- `lead` - Lead
- `appointment` - Termin

## Display-Formatierung

```python
from crm.utils.notification_manager import format_reminder_for_display

reminder = get_reminder(1)
display_reminder = format_reminder_for_display(reminder)

print(display_reminder['status_label'])      # "⏳ Ausstehend"
print(display_reminder['type_label'])        # "👤 Lead Follow-up"
print(display_reminder['due_date_label'])    # "⏰ Heute"
print(display_reminder['display_color'])     # "#F59E0B"
print(display_reminder['is_overdue'])        # True/False
```

## Hilfsfunktionen

### Prüfen ob überfällig
```python
from crm.utils.notification_manager import is_reminder_overdue

reminder = get_reminder(1)
if is_reminder_overdue(reminder):
    print("Diese Erinnerung ist überfällig!")
```

### Display-Farbe ermitteln
```python
from crm.utils.notification_manager import get_reminder_display_color

reminder = get_reminder(1)
color = get_reminder_display_color(reminder)
# Farben: #22C55E (Grün), #EF4444 (Rot), #F59E0B (Orange), #2563EB (Blau), #64748B (Grau)
```

## Best Practices

### 1. Automatische Erinnerungen bei Ereignissen erstellen
```python
# Bei Lead-Erstellung
def create_lead(lead_data):
    lead_id = save_lead_to_database(lead_data)
    
    # Automatisches Follow-up erstellen
    create_reminder_for_lead(
        lead_id=lead_id,
        lead_name=lead_data['name']
    )
    
    return lead_id
```

### 2. Erinnerungen im Dashboard anzeigen
```python
# Im Dashboard-Overview
def render_dashboard():
    # ... andere Widgets ...
    
    # Erinnerungs-Widget
    render_reminders_widget(texts)
```

### 3. Regelmäßige Benachrichtigungen prüfen
```python
# In einem Hintergrund-Job oder beim Dashboard-Load
def check_reminders():
    due_reminders = get_due_reminders()
    
    if due_reminders:
        # Zeige Benachrichtigung
        st.warning(f"Sie haben {len(due_reminders)} fällige Erinnerung(en)!")
```

### 4. Erinnerungen mit Workflow verknüpfen
```python
# Bei Angebots-Versand
def send_offer(project_id):
    # Sende Angebot
    send_pdf_to_customer(project_id)
    
    # Erstelle automatisches Follow-up
    create_reminder_for_offer(
        project_id=project_id,
        project_name=get_project_name(project_id)
    )
    
    # Update Angebotsstatus
    update_offer_status(project_id, 'sent')
```

## Fehlerbehandlung

```python
from crm.utils.notification_manager import create_reminder

try:
    reminder_id = create_reminder(
        reminder_type='manual',
        related_id=123,
        related_type='customer',
        due_date=date.today(),
        message='Test'
    )
    
    if reminder_id:
        print(f"Erinnerung #{reminder_id} erstellt")
    else:
        print("Fehler beim Erstellen der Erinnerung")
        
except Exception as e:
    print(f"Fehler: {e}")
```

## Datenbank-Schema

### Tabelle: crm_reminders

```sql
CREATE TABLE crm_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_type TEXT NOT NULL,           -- 'lead_created', 'offer_sent', etc.
    related_id INTEGER,                    -- ID des verknüpften Objekts
    related_type TEXT,                     -- 'customer', 'project', 'lead', 'appointment'
    due_date TIMESTAMP NOT NULL,           -- Fälligkeitsdatum
    status TEXT DEFAULT 'pending',         -- 'pending', 'completed', 'snoozed', 'dismissed'
    message TEXT,                          -- Nachricht der Erinnerung
    repeat_count INTEGER DEFAULT 0,        -- Wie oft wurde gesnoozed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indizes

- `idx_crm_reminders_due_date` - Schnelle Abfrage fälliger Erinnerungen
- `idx_crm_reminders_status` - Filterung nach Status

## Testing

```bash
# Tests ausführen
python crm/utils/test_notification_manager.py
```

## Troubleshooting

### Problem: Erinnerungen werden nicht angezeigt
**Lösung:** Prüfen Sie ob die Tabelle `crm_reminders` existiert:
```python
from database import get_db_connection, create_crm_enhancement_tables

conn = get_db_connection()
create_crm_enhancement_tables(conn)
conn.close()
```

### Problem: Snooze funktioniert nicht
**Lösung:** Prüfen Sie ob die Erinnerung den Status 'pending' oder 'snoozed' hat. Erledigte oder verworfene Erinnerungen können nicht gesnoozed werden.

### Problem: Automatische Erinnerungen werden nicht erstellt
**Lösung:** Stellen Sie sicher, dass die Regel-Engine korrekt konfiguriert ist und `auto_calculate_date=True` gesetzt ist.

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Logs in der Konsole
2. Führen Sie die Tests aus: `python crm/utils/test_notification_manager.py`
3. Überprüfen Sie die Datenbank-Struktur
4. Kontaktieren Sie den Support

---

**Version:** 1.0  
**Datum:** 2025-01-14  
**Autor:** Kiro AI
