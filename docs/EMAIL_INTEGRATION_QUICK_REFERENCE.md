# E-Mail-Integration - Quick Reference

## Übersicht

Die E-Mail-Integration ermöglicht das Versenden von E-Mails direkt aus dem CRM-System mit Vorlagen, Platzhaltern und automatischer Historie.

**Status:** ✅ Vollständig implementiert (Task 9)

**Anforderungen:** Requirements 4.1, 4.2, 4.3, 4.4, 4.5

---

## Hauptfunktionen

### 1. SMTP-Konfiguration (Admin-Panel)
- SMTP-Server-Einstellungen
- Verbindungstest
- Verschlüsselte Speicherung

### 2. E-Mail-Vorlagen
- Vorlagen erstellen, bearbeiten, löschen
- Platzhalter-System
- Kategorisierung
- Versionierung

### 3. E-Mail-Versand
- Direkt aus Kundenprofil
- Mit oder ohne Vorlage
- Anhänge aus Kundenakte
- Automatische Historie

### 4. E-Mail-Historie
- Chronologische Anzeige
- Status-Tracking (gesendet/fehlgeschlagen)
- Fehlerprotokollierung

---

## Datenbankstruktur

### Tabelle: `email_templates`
```sql
CREATE TABLE email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT,
    placeholders TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabelle: `email_history`
```sql
CREATE TABLE email_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    template_id INTEGER,
    attachments TEXT,
    status TEXT DEFAULT 'sent',
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_by TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (template_id) REFERENCES email_templates(id)
)
```

---

## Verwendung

### SMTP-Konfiguration einrichten

1. Öffnen Sie das Admin-Panel (Tab F)
2. Navigieren Sie zu "E-Mail-Integration"
3. Tab "SMTP-Konfiguration" öffnen
4. Geben Sie Ihre SMTP-Daten ein:
   - Host (z.B. smtp.gmail.com)
   - Port (z.B. 587)
   - Benutzername
   - Passwort
   - Absender-E-Mail
   - Absender-Name
5. Klicken Sie auf "Verbindung testen"
6. Bei Erfolg: "Konfiguration speichern"

**Hinweis für Gmail:** Verwenden Sie ein [App-Passwort](https://support.google.com/accounts/answer/185833)

### E-Mail-Vorlage erstellen

1. Admin-Panel → E-Mail-Integration
2. Tab "E-Mail-Vorlagen"
3. Tab "Neue Vorlage"
4. Füllen Sie aus:
   - Vorlagenname (eindeutig)
   - Kategorie
   - Betreff (mit Platzhaltern)
   - E-Mail-Text (mit Platzhaltern)
5. Klicken Sie auf "Vorlage erstellen"

**Verfügbare Platzhalter:**
- `{{customer_name}}` - Vollständiger Name
- `{{first_name}}` - Vorname
- `{{last_name}}` - Nachname
- `{{company_name}}` - Firmenname
- `{{email}}` - E-Mail-Adresse
- `{{phone}}` - Telefonnummer
- `{{address}}` - Vollständige Adresse
- `{{city}}` - Stadt
- `{{zip_code}}` - Postleitzahl
- `{{project_value}}` - Projektwert
- `{{current_date}}` - Aktuelles Datum

### E-Mail an Kunden senden

1. Öffnen Sie ein Kundenprofil im CRM
2. Scrollen Sie zum Abschnitt "E-Mail-Kommunikation"
3. Wählen Sie eine der Optionen:
   - **Mit Vorlage:** Wählen Sie eine Vorlage aus
   - **Individuelle E-Mail:** Schreiben Sie eine neue E-Mail
4. Optional: Wählen Sie Anhänge aus der Kundenakte
5. Klicken Sie auf "E-Mail senden"

### E-Mail-Historie anzeigen

1. Öffnen Sie ein Kundenprofil im CRM
2. Navigieren Sie zu "E-Mail-Kommunikation"
3. Tab "E-Mail-Historie"
4. Sehen Sie alle gesendeten E-Mails mit:
   - Status (✅ gesendet / ❌ fehlgeschlagen)
   - Betreff
   - Datum
   - Vollständiger Text
   - Anhänge
   - Fehlermeldungen (falls vorhanden)

---

## API-Referenz

### Core Functions

#### `create_email_tables(conn: sqlite3.Connection)`
Erstellt die E-Mail-Tabellen in der Datenbank.

#### `create_email_template(conn, name, subject, body, category=None, placeholders=None)`
Erstellt eine neue E-Mail-Vorlage.

**Returns:** Template-ID oder None bei Fehler

#### `send_email(config, recipient_email, subject, body, html=False, attachments=None)`
Sendet eine E-Mail über SMTP.

**Parameters:**
- `config`: SMTP-Konfiguration (dict)
- `recipient_email`: Empfänger-E-Mail
- `subject`: E-Mail-Betreff
- `body`: E-Mail-Text
- `html`: HTML-Format (bool)
- `attachments`: Liste von (filename, bytes) Tupeln

**Returns:** (success: bool, message: str)

#### `send_email_with_template(conn, config, template_id, customer_data, attachments=None, sent_by=None)`
Sendet eine E-Mail mit Vorlage und ersetzt Platzhalter.

**Returns:** (success: bool, message: str)

#### `replace_placeholders(text, customer_data)`
Ersetzt Platzhalter im Text mit Kundendaten.

**Returns:** Text mit ersetzten Platzhaltern

#### `get_email_history_for_customer(conn, customer_id, limit=50)`
Holt die E-Mail-Historie für einen Kunden.

**Returns:** Liste von E-Mail-Dictionaries

---

## UI-Komponenten

### Admin-Panel Integration

```python
from crm.features.admin_email_settings_ui import render_email_admin_settings

render_email_admin_settings(
    get_db_connection_func,
    load_admin_setting_func,
    save_admin_setting_func
)
```

### CRM-Integration

```python
from crm.features.email_crm_integration import render_customer_email_section

render_customer_email_section(
    conn,
    customer_data,
    load_admin_setting_func,
    texts
)
```

---

## Fehlerbehandlung

### Häufige Fehler

**1. "SMTP-Konfiguration unvollständig"**
- Lösung: Alle SMTP-Felder im Admin-Panel ausfüllen

**2. "Authentifizierung fehlgeschlagen"**
- Lösung: Benutzername/Passwort prüfen
- Bei Gmail: App-Passwort verwenden

**3. "Verbindung zum SMTP-Server fehlgeschlagen"**
- Lösung: Host und Port prüfen
- Firewall-Einstellungen überprüfen

**4. "Keine E-Mail-Adresse für diesen Kunden"**
- Lösung: E-Mail-Adresse im Kundenprofil hinterlegen

### Logging

Alle E-Mail-Aktivitäten werden in der `email_history` Tabelle protokolliert:
- Erfolgreiche Sendungen: `status = 'sent'`
- Fehlgeschlagene Sendungen: `status = 'failed'` mit `error_message`

---

## Tests

### Unit Tests ausführen

```bash
python crm/features/test_email_manager.py
```

**Getestete Funktionalität:**
- ✅ E-Mail-Vorlagen-System (CRUD)
- ✅ Platzhalter-Ersetzung (alle Typen)
- ✅ E-Mail-Versand mit Mock
- ✅ E-Mail-Versand mit Vorlagen
- ✅ E-Mail-Historie und Tracking
- ✅ Fehlerbehandlung und Validierung

---

## Best Practices

### 1. SMTP-Sicherheit
- Verwenden Sie App-Passwörter statt Haupt-Passwörter
- Aktivieren Sie TLS (Port 587)
- Speichern Sie Passwörter niemals im Code

### 2. E-Mail-Vorlagen
- Verwenden Sie aussagekräftige Namen
- Kategorisieren Sie Vorlagen
- Testen Sie Vorlagen vor dem Produktiveinsatz
- Verwenden Sie Platzhalter für Personalisierung

### 3. Anhänge
- Begrenzen Sie Anhang-Größe (max. 10 MB empfohlen)
- Verwenden Sie nur Dokumente aus der Kundenakte
- Prüfen Sie Dateitypen

### 4. E-Mail-Historie
- Überprüfen Sie regelmäßig fehlgeschlagene Sendungen
- Archivieren Sie alte E-Mails (> 1 Jahr)
- Nutzen Sie die Historie für Nachverfolgung

---

## Integration mit anderen Modulen

### Kommunikationshistorie (Task 5)
E-Mails werden automatisch in der `crm_activities` Tabelle protokolliert.

### Angebotsverfolgung (Task 6)
E-Mail-Versand kann Angebotsstatus aktualisieren.

### Automatische Erinnerungen (Task 7)
E-Mail-Vorlagen können für automatische Follow-ups verwendet werden.

---

## Erweiterungsmöglichkeiten

### Geplante Features (Optional)

1. **E-Mail-Tracking**
   - Öffnungsrate
   - Klick-Tracking
   - Bounce-Handling

2. **Massen-E-Mails**
   - An mehrere Kunden gleichzeitig
   - Mit Tag-Filter
   - Zeitgesteuert

3. **E-Mail-Automatisierung**
   - Trigger-basiert
   - Workflow-Integration
   - A/B-Testing

4. **Erweiterte Vorlagen**
   - HTML-Editor
   - Bild-Einbettung
   - Responsive Design

---

## Support

Bei Problemen oder Fragen:
1. Prüfen Sie die E-Mail-Historie auf Fehlermeldungen
2. Testen Sie die SMTP-Verbindung im Admin-Panel
3. Überprüfen Sie die Logs in der Konsole
4. Kontaktieren Sie den Support mit:
   - Fehlermeldung
   - SMTP-Provider
   - Zeitpunkt des Fehlers

---

**Version:** 1.0  
**Datum:** 2025-01-14  
**Status:** ✅ Produktionsbereit
