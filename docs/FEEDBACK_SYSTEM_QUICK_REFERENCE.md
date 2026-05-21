# Feedback-System - Quick Reference

## Schnellstart

### 1. Tabellen erstellen

```python
from crm.features import feedback_manager

feedback_manager.create_feedback_tables(conn)
```

### 2. Umfrage erstellen

```python
survey_id = feedback_manager.create_survey(
    conn,
    name="Kundenzufriedenheit",
    questions=[
        {
            'id': 'q1',
            'type': 'rating',
            'text': 'Wie zufrieden sind Sie?',
            'required': True
        },
        {
            'id': 'q2',
            'type': 'text',
            'text': 'Was können wir verbessern?',
            'required': False
        }
    ],
    trigger_event="project_completed",
    trigger_delay_days=7
)
```

### 3. Automatischen Trigger auslösen

```python
# Bei Projektabschluss
trigger_ids = feedback_manager.trigger_survey_on_event(
    conn,
    event_type="project_completed",
    customer_id=42,
    project_id=10
)
```

### 4. Antwort speichern

```python
response_id = feedback_manager.submit_response(
    conn,
    survey_id=1,
    customer_id=42,
    responses={'q1': 5, 'q2': 'Alles super!'},
    overall_rating=5
)
```

### 5. Statistiken abrufen

```python
stats = feedback_manager.get_survey_statistics(conn, survey_id)
print(f"Antworten: {stats['total_responses']}")
print(f"Ø Rating: {stats['avg_rating']:.1f}")
print(f"Response Rate: {stats['response_rate']:.1f}%")
```

## Häufige Aufgaben

### Umfrage mit E-Mail-Vorlage

```python
survey_id = feedback_manager.create_survey(
    conn,
    name="Projekt-Feedback",
    questions=[...],
    email_subject="Ihre Meinung zu {{project_name}}",
    email_body="Hallo {{customer_name}},\n\nwie war Ihr Projekt?"
)
```

### Negatives Feedback überwachen

```python
alerts = feedback_manager.get_negative_feedback_alerts(conn, days=7)
for alert in alerts:
    print(f"⚠️ {alert['first_name']} {alert['last_name']}: {alert['overall_rating']}⭐")
```

### Trend-Analyse

```python
trends = feedback_manager.get_trend_analysis(conn, survey_id, days=30)
for trend in trends:
    print(f"{trend['date']}: {trend['avg_rating']:.1f}⭐ ({trend['responses']} Antworten)")
```

### Ausstehende Trigger verarbeiten

```python
pending = feedback_manager.get_pending_triggers(conn)
for trigger in pending:
    # E-Mail senden
    send_email(trigger['email'], trigger['email_subject'], ...)
    
    # Als versendet markieren
    feedback_manager.mark_trigger_sent(conn, trigger['id'])
```

## Fragetypen

| Typ | Beschreibung | Beispiel |
|-----|--------------|----------|
| `rating` | Sterne-Bewertung (1-5) | "Wie zufrieden sind Sie?" |
| `text` | Freitext | "Was können wir verbessern?" |
| `multiple_choice` | Auswahl | "Würden Sie uns empfehlen?" |
| `yes_no` | Ja/Nein | "War alles pünktlich?" |

## Trigger-Events

| Event | Beschreibung | Typische Verzögerung |
|-------|--------------|---------------------|
| `project_completed` | Projekt abgeschlossen | 7 Tage |
| `installation_done` | Installation fertig | 1 Tag |
| `after_30_days` | 30 Tage nach Projekt | 30 Tage |
| `after_90_days` | 90 Tage nach Projekt | 90 Tage |
| `manual` | Manuell ausgelöst | 0 Tage |

## E-Mail-Platzhalter

- `{{customer_name}}` - Vollständiger Name
- `{{first_name}}` - Vorname
- `{{last_name}}` - Nachname
- `{{project_name}}` - Projektname
- `{{company}}` - Firmenname
- `{{email}}` - E-Mail-Adresse

## Sentiment-Berechnung

| Rating | Sentiment |
|--------|-----------|
| 4-5 ⭐ | `positive` |
| 3 ⭐ | `neutral` |
| 1-2 ⭐ | `negative` |

## UI Integration

```python
import streamlit as st
from crm.features import feedback_ui

# In Ihrer Streamlit-App
feedback_ui.render_feedback_management(conn)
```

## Best Practices

✅ **DO:**
- Umfragen kurz halten (max. 5-7 Fragen)
- Personalisierung nutzen (Platzhalter)
- Negatives Feedback schnell bearbeiten (24h)
- Erinnerungen nach 7 Tagen senden
- Response Rate tracken

❌ **DON'T:**
- Zu viele Pflichtfelder
- Zu lange Umfragen (>5 Min)
- Zu häufig befragen (max. 1x/Quartal)
- Negatives Feedback ignorieren
- Ohne Follow-up lassen

## Troubleshooting

### Keine Trigger werden erstellt

```python
# Prüfen ob Umfrage aktiv ist
survey = feedback_manager.get_survey_by_id(conn, survey_id)
if not survey['is_active']:
    feedback_manager.update_survey(conn, survey_id, is_active=True)
```

### Niedrige Response Rate

1. E-Mail-Betreff optimieren
2. Umfrage kürzen
3. Incentive anbieten
4. Erinnerungen aktivieren
5. Timing anpassen

### Statistiken zeigen 0

```python
# Prüfen ob Antworten vorhanden
responses = feedback_manager.get_responses_by_survey(conn, survey_id)
print(f"Anzahl Antworten: {len(responses)}")
```

## Weitere Ressourcen

- **Technische Referenz**: `crm/features/FEEDBACK_MANAGER_REFERENCE.md`
- **Tests**: `crm/features/test_feedback_manager.py`
- **UI-Komponenten**: `crm/features/feedback_ui.py`

## Support

Bei Fragen oder Problemen:
1. Logs prüfen (Fehler werden automatisch geloggt)
2. Tests ausführen: `pytest crm/features/test_feedback_manager.py`
3. Dokumentation konsultieren
