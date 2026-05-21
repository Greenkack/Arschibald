# Anruf-Protokollierung - Quick Reference

## Übersicht

Die Anruf-Protokollierung ermöglicht das systematische Erfassen von Telefonanrufen mit Timer, Richtung (eingehend/ausgehend), Telefonnummer-Auswahl und Notizen. Alle Anrufe werden in der Kommunikations-Timeline integriert.

## Hauptfunktionen

### 1. Anruf erstellen

```python
from crm.features.call_manager import create_call

call_id = create_call(
    customer_id=123,
    phone_number="+43 123 456789",
    direction="outgoing",  # oder "incoming"
    duration_seconds=300,  # 5 Minuten
    notes="Angebot besprochen, Kunde interessiert",
    created_by="Max Mustermann"
)
```

### 2. Anrufe abrufen

```python
from crm.features.call_manager import get_customer_calls

# Alle Anrufe eines Kunden
calls = get_customer_calls(customer_id=123)

# Nur ausgehende Anrufe
outgoing_calls = get_customer_calls(customer_id=123, direction="outgoing")

# Mit archivierten Anrufen
all_calls = get_customer_calls(customer_id=123, include_archived=True)
```

### 3. Anruf-Statistiken

```python
from crm.features.call_manager import get_call_statistics

stats = get_call_statistics(customer_id=123)
print(f"Gesamt: {stats['total']}")
print(f"Eingehend: {stats['incoming']}")
print(f"Ausgehend: {stats['outgoing']}")
print(f"Gesamtdauer: {stats['total_duration_formatted']}")
print(f"Ø Dauer: {stats['average_duration_formatted']}")
```

### 4. Dauer formatieren

```python
from crm.features.call_manager import format_duration, parse_duration

# Sekunden zu lesbarem Format
formatted = format_duration(323)  # "5:23"
formatted = format_duration(3665)  # "1:01:05"

# String zu Sekunden
seconds = parse_duration("5:30")  # 330
seconds = parse_duration("1:30:00")  # 5400
```

## UI-Integration

### Anruf-Dialog mit Timer

```python
from crm.features.call_ui import render_call_dialog

# In Streamlit-App
render_call_dialog(
    customer_id=123,
    customer_name="Max Mustermann",
    phone_numbers=["+43 123 456789", "+43 987 654321"]
)
```

### Anruf-Historie anzeigen

```python
from crm.features.call_ui import render_call_list

render_call_list(customer_id=123, limit=20)
```

### Anruf-Statistiken anzeigen

```python
from crm.features.call_ui import render_call_statistics

render_call_statistics(customer_id=123)
```

### Vollständige Integration

```python
from crm.features.call_ui import integrate_call_logging_to_customer_profile

# Integriert alle Anruf-Funktionen in Kundenprofil
integrate_call_logging_to_customer_profile(
    customer_id=123,
    customer_data={
        "name": "Max Mustermann",
        "phone": "+43 123 456789",
        "mobile": "+43 987 654321"
    }
)
```

## Datenbankstruktur

Die Anruf-Protokollierung erweitert die `crm_activities` Tabelle um folgende Felder:

```sql
ALTER TABLE crm_activities ADD COLUMN call_direction TEXT;
ALTER TABLE crm_activities ADD COLUMN call_phone_number TEXT;
ALTER TABLE crm_activities ADD COLUMN call_duration_seconds INTEGER DEFAULT 0;
ALTER TABLE crm_activities ADD COLUMN call_notes TEXT;
```

Diese Felder werden automatisch beim ersten Aufruf hinzugefügt durch:

```python
from crm.features.call_manager import ensure_call_fields

ensure_call_fields()
```

## Anruf-Richtungen

```python
CALL_DIRECTIONS = {
    "incoming": "Eingehend",
    "outgoing": "Ausgehend"
}
```

## Timer-Funktionalität

Der Timer in der UI:
- **Start**: Startet die Zeitmessung
- **Stopp**: Stoppt die Zeitmessung und addiert zur Gesamtdauer
- **Reset**: Setzt den Timer auf 0:00 zurück
- **Auto-Refresh**: Aktualisiert die Anzeige jede Sekunde während der Timer läuft

Manuelle Eingabe:
- Format: `MM:SS` (z.B. "5:30" für 5 Minuten 30 Sekunden)
- Format: `HH:MM:SS` (z.B. "1:30:00" für 1 Stunde 30 Minuten)

## Integration in Kommunikations-Timeline

Alle Anrufe werden automatisch in der Kommunikations-Timeline angezeigt:

```python
from crm.features.note_manager import get_customer_activities

# Alle Aktivitäten inkl. Anrufe
activities = get_customer_activities(customer_id=123)

# Nur Anrufe
calls = get_customer_activities(customer_id=123, activity_type="call")
```

## Best Practices

1. **Telefonnummern**: Verwenden Sie einheitliche Formate (z.B. +43 123 456789)
2. **Notizen**: Erfassen Sie wichtige Gesprächsinhalte und nächste Schritte
3. **Richtung**: Markieren Sie eingehende Anrufe, um Kundeninteresse zu tracken
4. **Timer**: Nutzen Sie den Timer für genaue Zeiterfassung
5. **Statistiken**: Überprüfen Sie regelmäßig die Anruf-Statistiken für Insights

## Beispiel-Workflow

```python
# 1. Kunde ruft an (eingehend)
call_id = create_call(
    customer_id=123,
    phone_number="+43 123 456789",
    direction="incoming",
    duration_seconds=180,
    notes="Kunde fragt nach Angebot für 10 kWp Anlage",
    created_by="Empfang"
)

# 2. Rückruf (ausgehend)
call_id = create_call(
    customer_id=123,
    phone_number="+43 123 456789",
    direction="outgoing",
    duration_seconds=420,
    notes="Angebot besprochen, Termin für Vor-Ort-Besichtigung vereinbart",
    created_by="Vertrieb"
)

# 3. Statistiken prüfen
stats = get_call_statistics(customer_id=123)
print(f"Kontakte: {stats['total']}, Gesamtdauer: {stats['total_duration_formatted']}")
```

## Fehlerbehandlung

```python
# Ungültige Richtung
call_id = create_call(customer_id=123, phone_number="+43 123", direction="invalid")
# Gibt None zurück und loggt Fehler

# Fehlende Telefonnummer in UI
# UI zeigt Fehlermeldung: "Bitte geben Sie eine Telefonnummer ein."

# Datenbankfehler
# Funktionen geben None/False zurück und loggen Fehler
```

## Performance-Hinweise

- Anrufe werden mit Index auf `customer_id` und `activity_type` effizient abgerufen
- Limit-Parameter verwenden für große Datenmengen
- Archivierte Anrufe standardmäßig ausblenden für bessere Performance

## Siehe auch

- [Kommunikationshistorie](KOMMUNIKATIONSHISTORIE_QUICK_REFERENCE.md)
- [Task Management](TASK_MANAGEMENT_QUICK_REFERENCE.md)
- [CRM Übersicht](../README.md)
