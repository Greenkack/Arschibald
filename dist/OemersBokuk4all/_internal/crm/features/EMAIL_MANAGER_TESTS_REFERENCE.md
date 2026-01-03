# E-Mail-Manager Tests - Referenz

## Übersicht

Dieses Dokument beschreibt die Unit Tests für das E-Mail-Integration-System.

**Datei:** `crm/features/test_email_manager.py`  
**Anforderungen:** 4.1, 4.2, 4.3  
**Status:** ✅ Alle 19 Tests bestanden

## Test-Kategorien

### 1. Vorlagen-System (Requirement 4.2)

#### Test: create_email_template
- **Zweck:** Erstellen einer E-Mail-Vorlage
- **Prüft:** Template-ID, Name, Betreff, Kategorie, Platzhalter
- **Status:** ✅ Bestanden

#### Test: create_duplicate_template
- **Zweck:** Duplikat-Vorlage sollte abgelehnt werden
- **Prüft:** Eindeutigkeit des Vorlagennamens
- **Status:** ✅ Bestanden

#### Test: get_template_by_name
- **Zweck:** Vorlage nach Name abrufen
- **Prüft:** Abruf aktiver Vorlagen nach Name
- **Status:** ✅ Bestanden

#### Test: list_email_templates
- **Zweck:** Alle Vorlagen auflisten
- **Prüft:** Filterung nach Kategorie, aktive Vorlagen
- **Status:** ✅ Bestanden

#### Test: update_email_template
- **Zweck:** Vorlage aktualisieren
- **Prüft:** Änderung von Betreff und Body
- **Status:** ✅ Bestanden

#### Test: delete_email_template
- **Zweck:** Vorlage löschen (soft delete)
- **Prüft:** Soft-Delete-Mechanismus, is_active Flag
- **Status:** ✅ Bestanden

### 2. Platzhalter-Ersetzung (Requirement 4.2)

#### Test: replace_placeholders_basic
- **Zweck:** Grundlegende Platzhalter-Ersetzung
- **Prüft:** {{customer_name}}, {{email}}
- **Status:** ✅ Bestanden

#### Test: replace_placeholders_all_types
- **Zweck:** Alle Platzhalter-Typen
- **Prüft:** Alle 11 unterstützten Platzhalter
  - {{customer_name}}, {{first_name}}, {{last_name}}
  - {{company_name}}, {{email}}, {{phone}}
  - {{address}}, {{city}}, {{zip_code}}
  - {{project_value}}, {{current_date}}
- **Status:** ✅ Bestanden

#### Test: replace_placeholders_missing_data
- **Zweck:** Platzhalter-Ersetzung mit fehlenden Daten
- **Prüft:** Behandlung fehlender Kundendaten (leere Strings)
- **Status:** ✅ Bestanden

#### Test: extract_placeholders
- **Zweck:** Platzhalter aus Text extrahieren
- **Prüft:** Regex-basierte Extraktion aller {{placeholder}}
- **Status:** ✅ Bestanden

### 3. E-Mail-Versand (Mock) (Requirement 4.1)

#### Test: send_email_mock
- **Zweck:** E-Mail-Versand mit Mock
- **Prüft:** SMTP-Verbindung, Login, Versand, Quit
- **Mocks:** smtplib.SMTP
- **Status:** ✅ Bestanden

#### Test: send_email_with_attachments_mock
- **Zweck:** E-Mail mit Anhängen versenden
- **Prüft:** Anhang-Handling (PDF, Bilder)
- **Mocks:** smtplib.SMTP
- **Status:** ✅ Bestanden

#### Test: send_email_authentication_error_mock
- **Zweck:** Authentifizierungsfehler behandeln
- **Prüft:** SMTPAuthenticationError, Fehlermeldung
- **Mocks:** smtplib.SMTP mit side_effect
- **Status:** ✅ Bestanden

#### Test: send_email_incomplete_config
- **Zweck:** Unvollständige Konfiguration erkennen
- **Prüft:** Validierung von SMTP-Konfiguration
- **Status:** ✅ Bestanden

#### Test: test_smtp_connection_mock
- **Zweck:** SMTP-Verbindungstest
- **Prüft:** Verbindung, TLS, Login, Quit
- **Mocks:** smtplib.SMTP
- **Status:** ✅ Bestanden

### 4. E-Mail mit Vorlage (Requirement 4.3)

#### Test: send_email_with_template_mock
- **Zweck:** E-Mail mit Vorlage versenden
- **Prüft:** 
  - Template-Abruf
  - Platzhalter-Ersetzung in Betreff und Body
  - E-Mail-Versand
  - Historie-Speicherung
- **Mocks:** smtplib.SMTP
- **Status:** ✅ Bestanden

#### Test: send_email_with_template_failed_mock
- **Zweck:** Fehlgeschlagener Versand mit Vorlage
- **Prüft:**
  - Fehlerbehandlung
  - Historie-Speicherung mit Status 'failed'
  - Fehlermeldung in Historie
- **Mocks:** smtplib.SMTP mit SMTPException
- **Status:** ✅ Bestanden

### 5. E-Mail-Historie

#### Test: save_email_to_history
- **Zweck:** E-Mail in Historie speichern
- **Prüft:** Speicherung aller Felder, E-Mail-ID
- **Status:** ✅ Bestanden

#### Test: get_email_history_multiple
- **Zweck:** Mehrere E-Mails in Historie
- **Prüft:** Anzahl, Vollständigkeit
- **Status:** ✅ Bestanden

## Test-Ausführung

```bash
# Alle Tests ausführen
python crm/features/test_email_manager.py

# Erwartete Ausgabe
======================================================================
E-Mail-Integration - Unit Tests
======================================================================
✅ Bestanden: 19/19
❌ Fehlgeschlagen: 0/19

🎉 Alle Tests erfolgreich!
```

## Getestete Funktionalität

✅ **E-Mail-Vorlagen-System (CRUD)** (Requirement 4.2)
- Erstellen, Abrufen, Auflisten, Aktualisieren, Löschen

✅ **Platzhalter-Ersetzung (alle Typen)** (Requirement 4.2)
- 11 verschiedene Platzhalter
- Fehlerbehandlung bei fehlenden Daten

✅ **E-Mail-Versand mit Mock** (Requirement 4.1)
- SMTP-Verbindung und Authentifizierung
- Anhänge
- Fehlerbehandlung

✅ **E-Mail-Versand mit Vorlagen** (Requirement 4.3)
- Template-basierter Versand
- Automatische Platzhalter-Ersetzung
- Historie-Integration

✅ **E-Mail-Historie und Tracking**
- Speicherung aller versendeten E-Mails
- Status-Tracking (sent/failed)
- Fehlermeldungen

✅ **Fehlerbehandlung und Validierung**
- Unvollständige Konfiguration
- Authentifizierungsfehler
- SMTP-Fehler

## Technische Details

### Test-Setup
- **Datenbank:** In-Memory SQLite (`:memory:`)
- **Mocking:** `unittest.mock.patch` für SMTP
- **Encoding:** UTF-8 mit Windows-Kompatibilität

### Test-Struktur
```python
def setup_test_db() -> sqlite3.Connection:
    """Erstellt In-Memory-Testdatenbank"""
    
def cleanup_test_db(conn: sqlite3.Connection):
    """Schließt Testdatenbank"""
    
def create_test_customer(conn: sqlite3.Connection) -> int:
    """Erstellt Test-Kunden"""
```

### Mock-Beispiel
```python
with patch('email_manager.smtplib.SMTP') as mock_smtp:
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    # Test-Code
    success, message = send_email(config, ...)
    
    # Assertions
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()
```

## Anforderungs-Abdeckung

| Requirement | Beschreibung | Tests | Status |
|-------------|--------------|-------|--------|
| 4.1 | E-Mail-Versand | 5 Tests | ✅ |
| 4.2 | Vorlagen & Platzhalter | 10 Tests | ✅ |
| 4.3 | Vorlage-Versand | 2 Tests | ✅ |
| - | Historie | 2 Tests | ✅ |

**Gesamt:** 19 Tests, 100% bestanden

## Nächste Schritte

1. ✅ Tests für E-Mail-Integration implementiert
2. ⏭️ Integration in CI/CD-Pipeline (optional)
3. ⏭️ Performance-Tests für große E-Mail-Mengen (optional)
4. ⏭️ Integration-Tests mit echtem SMTP-Server (optional)

## Wartung

- **Letzte Aktualisierung:** 2025-01-14
- **Version:** 1.0
- **Autor:** Kiro AI
- **Kontakt:** Bei Fragen zu den Tests siehe `test_email_manager.py`
