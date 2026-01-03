# Feedback Manager - Technische Referenz

## Übersicht

Das Feedback-System ermöglicht die Erstellung und Verwaltung von Kundenzufriedenheitsumfragen mit automatischem Versand und umfassenden Auswertungsfunktionen.

## Datenbank-Schema

### Tabelle: feedback_surveys

Speichert Umfrage-Definitionen.

```sql
CREATE TABLE feedback_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    questions_json TEXT NOT NULL,
    trigger_event TEXT,
    trigger_delay_days INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    email_subject TEXT,
    email_body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
)
```

### Tabelle: feedback_responses

Speichert Kunden-Antworten.

```sql
CREATE TABLE feedback_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    responses_json TEXT NOT NULL,
    overall_rating INTEGER,
    sentiment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (survey_id) REFERENCES feedback_surveys(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
)
```

### Tabelle: feedback_triggers

Verwaltet automatische Umfrage-Versendungen.

```sql
CREATE TABLE feedback_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    project_id INTEGER,
    trigger_event TEXT NOT NULL,
    scheduled_date DATE NOT NULL,
    status TEXT DEFAULT 'pending',
    sent_at TIMESTAMP,
    response_id INTEGER,
    reminder_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES feedback_surveys(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (response_id) REFERENCES feedback_responses(id)
)
```

## API-Funktionen

### Umfrage-Verwaltung

#### create_survey()

Erstellt eine neue Umfrage.

```python
survey_id = feedback_manager.create_survey(
    conn,
    name="Kundenzufriedenheit 2025",
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
    trigger_delay_days=7,
    email_subject="Ihre Meinung ist uns wichtig!",
    email_body="Hallo {{customer_name}}, ..."
)
```

**Parameter:**
- `name`: Name der Umfrage
- `questions`: Liste von Fragen (siehe Fragetypen)
- `trigger_event`: Auslösendes Ereignis (optional)
- `trigger_delay_days`: Verzögerung in Tagen
- `email_subject`: E-Mail Betreff
- `email_body`: E-Mail Text mit Platzhaltern

**Rückgabe:** ID der erstellten Umfrage

#### get_survey_by_id()

Lädt eine Umfrage anhand der ID.

```python
survey = feedback_manager.get_survey_by_id(conn, survey_id)
```

#### get_all_surveys()

Lädt alle Umfragen.

```python
surveys = feedback_manager.get_all_surveys(conn, active_only=True)
```

#### update_survey()

Aktualisiert eine Umfrage.

```python
success = feedback_manager.update_survey(
    conn,
    survey_id,
    name="Neuer Name",
    is_active=False
)
```

#### delete_survey()

Löscht eine Umfrage.

```python
success = feedback_manager.delete_survey(conn, survey_id)
```

### Antwort-Verwaltung

#### submit_response()

Speichert eine Umfrage-Antwort.

```python
response_id = feedback_manager.submit_response(
    conn,
    survey_id=1,
    customer_id=42,
    responses={
        'q1': 5,
        'q2': 'Alles super!'
    },
    overall_rating=5,
    project_id=10
)
```

**Sentiment-Berechnung:**
- Rating 4-5: `positive`
- Rating 3: `neutral`
- Rating 1-2: `negative`

#### get_responses_by_survey()

Lädt alle Antworten zu einer Umfrage.

```python
responses = feedback_manager.get_responses_by_survey(
    conn,
    survey_id,
    sentiment_filter='negative'  # optional
)
```

#### get_responses_by_customer()

Lädt alle Antworten eines Kunden.

```python
responses = feedback_manager.get_responses_by_customer(conn, customer_id)
```

### Trigger-Verwaltung

#### create_trigger()

Erstellt einen manuellen Trigger.

```python
trigger_id = feedback_manager.create_trigger(
    conn,
    survey_id=1,
    customer_id=42,
    trigger_event="manual",
    scheduled_date="2025-02-01",
    project_id=10
)
```

#### trigger_survey_on_event()

Löst automatisch Umfragen bei Ereignissen aus.

```python
trigger_ids = feedback_manager.trigger_survey_on_event(
    conn,
    event_type="project_completed",
    customer_id=42,
    project_id=10
)
```

**Unterstützte Events:**
- `project_completed`: Projekt abgeschlossen
- `installation_done`: Installation fertig
- `after_30_days`: 30 Tage nach Projekt
- `after_90_days`: 90 Tage nach Projekt

#### get_pending_triggers()

Lädt ausstehende Trigger.

```python
pending = feedback_manager.get_pending_triggers(conn, date="2025-01-15")
```

#### mark_trigger_sent()

Markiert Trigger als versendet.

```python
success = feedback_manager.mark_trigger_sent(conn, trigger_id)
```

#### send_reminder()

Sendet Erinnerung für Trigger.

```python
success = feedback_manager.send_reminder(conn, trigger_id)
```

### Analytics & Reporting

#### get_survey_statistics()

Berechnet Statistiken für eine Umfrage.

```python
stats = feedback_manager.get_survey_statistics(conn, survey_id)
```

**Rückgabe:**
```python
{
    'total_responses': 42,
    'avg_rating': 4.5,
    'positive_count': 35,
    'neutral_count': 5,
    'negative_count': 2,
    'response_rate': 84.0,
    'total_sent': 50
}
```

#### get_trend_analysis()

Analysiert Trends über Zeitraum.

```python
trends = feedback_manager.get_trend_analysis(conn, survey_id, days=30)
```

**Rückgabe:**
```python
[
    {
        'date': '2025-01-15',
        'responses': 5,
        'avg_rating': 4.2,
        'positive': 4,
        'negative': 1
    },
    ...
]
```

#### get_negative_feedback_alerts()

Lädt negatives Feedback für Alerts.

```python
alerts = feedback_manager.get_negative_feedback_alerts(conn, days=7)
```

#### get_question_statistics()

Berechnet Statistiken für einzelne Frage.

```python
stats = feedback_manager.get_question_statistics(conn, survey_id, 'q1')
```

**Rückgabe:**
```python
{
    'total_answers': 42,
    'answers': [5, 4, 5, 3, ...],
    'avg': 4.3,
    'min': 1,
    'max': 5,
    'frequency': {'Option A': 20, 'Option B': 15, ...}  # für Multiple Choice
}
```

## Fragetypen

### Rating

Bewertung mit Sternen (1-5).

```python
{
    'id': 'q1',
    'type': 'rating',
    'text': 'Wie zufrieden sind Sie?',
    'required': True
}
```

### Text

Freitext-Antwort.

```python
{
    'id': 'q2',
    'type': 'text',
    'text': 'Was können wir verbessern?',
    'required': False
}
```

### Multiple Choice

Auswahl aus Optionen.

```python
{
    'id': 'q3',
    'type': 'multiple_choice',
    'text': 'Würden Sie uns weiterempfehlen?',
    'options': ['Ja', 'Vielleicht', 'Nein'],
    'required': True
}
```

### Yes/No

Ja/Nein-Frage.

```python
{
    'id': 'q4',
    'type': 'yes_no',
    'text': 'War die Installation pünktlich?',
    'required': True
}
```

## E-Mail-Platzhalter

Verfügbare Platzhalter für E-Mail-Vorlagen:

- `{{customer_name}}`: Kundenname
- `{{first_name}}`: Vorname
- `{{last_name}}`: Nachname
- `{{project_name}}`: Projektname
- `{{company}}`: Firmenname
- `{{email}}`: E-Mail-Adresse

**Beispiel:**
```
Hallo {{first_name}} {{last_name}},

vielen Dank für Ihr Vertrauen in unser Projekt "{{project_name}}".
Wir würden uns über Ihr Feedback freuen!

Mit freundlichen Grüßen
Ihr Team
```

## Workflow-Beispiele

### Automatische Umfrage nach Projektabschluss

```python
# 1. Umfrage mit Trigger erstellen
survey_id = feedback_manager.create_survey(
    conn,
    name="Projekt-Feedback",
    questions=[...],
    trigger_event="project_completed",
    trigger_delay_days=7  # 7 Tage nach Abschluss
)

# 2. Bei Projektabschluss Trigger auslösen
trigger_ids = feedback_manager.trigger_survey_on_event(
    conn,
    event_type="project_completed",
    customer_id=customer_id,
    project_id=project_id
)

# 3. Täglich ausstehende Trigger verarbeiten
pending = feedback_manager.get_pending_triggers(conn)
for trigger in pending:
    # E-Mail versenden (über email_manager)
    send_email(trigger['email'], trigger['email_subject'], ...)
    
    # Als versendet markieren
    feedback_manager.mark_trigger_sent(conn, trigger['id'])

# 4. Nach 7 Tagen Erinnerung senden
for trigger in pending_reminders:
    send_reminder_email(...)
    feedback_manager.send_reminder(conn, trigger['id'])
```

### Negativ-Feedback Monitoring

```python
# Täglich negatives Feedback prüfen
alerts = feedback_manager.get_negative_feedback_alerts(conn, days=1)

for alert in alerts:
    # Benachrichtigung an Vertrieb
    notify_sales_team(
        customer=alert['first_name'] + ' ' + alert['last_name'],
        rating=alert['overall_rating'],
        feedback=alert['responses']
    )
    
    # Automatische Aufgabe erstellen
    task_manager.create_task(
        conn,
        title=f"Negatives Feedback: {alert['first_name']} {alert['last_name']}",
        customer_id=alert['customer_id'],
        priority='high'
    )
```

## Best Practices

### Umfrage-Design

1. **Kurz halten**: Max. 5-7 Fragen
2. **Klare Fragen**: Eindeutig formuliert
3. **Mix aus Typen**: Rating + Text für Details
4. **Pflichtfelder sparsam**: Nur wichtigste Fragen

### Timing

1. **Projekt-Feedback**: 7 Tage nach Abschluss
2. **Installation-Feedback**: 1 Tag nach Installation
3. **Langzeit-Feedback**: 90 Tage nach Installation
4. **Erinnerungen**: Nach 7 Tagen

### Response Rate erhöhen

1. **Personalisierung**: Platzhalter nutzen
2. **Kurze Umfragen**: Unter 2 Minuten
3. **Incentives**: Rabatt/Gutschein anbieten
4. **Mobile-optimiert**: Responsive Design
5. **Erinnerungen**: Nach 7 Tagen

### Negativ-Feedback

1. **Schnell reagieren**: Innerhalb 24h
2. **Persönlich kontaktieren**: Telefon statt E-Mail
3. **Lösung anbieten**: Konkrete Maßnahmen
4. **Follow-up**: Nach Lösung erneut nachfragen

## Performance-Tipps

1. **Indizes nutzen**: Bereits implementiert
2. **Batch-Processing**: Trigger in Batches verarbeiten
3. **Archivierung**: Alte Antworten (>1 Jahr) archivieren
4. **Caching**: Statistiken cachen

## Fehlerbehandlung

Alle Funktionen geben `None` oder `False` bei Fehlern zurück und loggen Details:

```python
survey_id = feedback_manager.create_survey(...)
if survey_id is None:
    print("Fehler beim Erstellen der Umfrage!")
    # Fehlerdetails wurden bereits geloggt
```

## Integration mit anderen Modulen

### Mit E-Mail-Manager

```python
from crm.features import email_manager, feedback_manager

# Trigger verarbeiten und E-Mails senden
pending = feedback_manager.get_pending_triggers(conn)
for trigger in pending:
    email_manager.send_email(
        conn,
        to_email=trigger['email'],
        subject=trigger['email_subject'],
        body=trigger['email_body'],
        customer_id=trigger['customer_id']
    )
    feedback_manager.mark_trigger_sent(conn, trigger['id'])
```

### Mit Task-Manager

```python
from crm.features import task_manager, feedback_manager

# Aufgabe bei negativem Feedback
alerts = feedback_manager.get_negative_feedback_alerts(conn)
for alert in alerts:
    task_manager.create_task(
        conn,
        title=f"Negatives Feedback bearbeiten",
        description=f"Kunde: {alert['first_name']} {alert['last_name']}\n"
                   f"Rating: {alert['overall_rating']}\n"
                   f"Feedback: {alert['responses']}",
        customer_id=alert['customer_id'],
        priority='high',
        due_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    )
```

### Mit Notification-Manager

```python
from crm.utils import notification_manager
from crm.features import feedback_manager

# Erinnerung für ausstehende Umfragen
notification_manager.create_reminder(
    conn,
    reminder_type='feedback_pending',
    related_id=trigger_id,
    due_date=scheduled_date,
    message=f"Umfrage an {customer_name} versenden"
)
```

## Version History

- **1.0** (2025-01-14): Initial Release
  - Umfrage-Verwaltung
  - Automatische Trigger
  - Analytics & Reporting
  - Negativ-Feedback Alerts
