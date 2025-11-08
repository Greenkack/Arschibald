# CRM System Enhancement - Implementation Tasks

## Übersicht

Dieses Dokument enthält die Implementierungs-Tasks für das erweiterte CRM-System. Die Tasks sind nach Priorität und Abhängigkeiten sortiert.

**Aktueller Stand:**
- ✅ Basis-CRM existiert: `crm.py`, `crm_dashboard_ui.py`, `crm_pipeline_ui.py`, `crm_calendar_ui.py`
- ✅ Kundenverwaltung (CRUD) vorhanden
- ✅ Projektverwaltung vorhanden
- ✅ Kundenakte mit Dokumenten-Upload vorhanden (`customer_documents` Tabelle)
- ✅ Dashboard mit KPIs vorhanden
- ✅ Sales Pipeline vorhanden (`crm_leads` Tabelle)
- ✅ Kalender mit Terminverwaltung vorhanden (`crm_appointments` Tabelle)
- ✅ "Kunde in CRM speichern" Button existiert in `gui.py` und `drawer_actions.py`
- ❌ Keine automatische Datenübernahme aus Bedarfsanalyse
- ❌ Keine Berechnungsversionierung
- ❌ Keine automatische PDF-Archivierung
- ❌ Keine Aufgabenverwaltung
- ❌ Keine Notizen/Kommunikationshistorie
- ❌ Keine Angebotsverfolgung
- ❌ Keine automatischen Erinnerungen

**Hinweis:** Tasks mit "*" am Ende sind optional (z.B. Unit Tests) und können übersprungen werden.

---

## Phase 1: Kern-Funktionen (MVP + Essentials)

### 1. Projekt-Setup und Datenbankstruktur

- [ ] 1.1 Erstelle neue Datenbankstruktur für CRM-Erweiterungen
  - Erstelle Tabelle `project_calculations` für Berechnungsversionierung
  - Erstelle Tabelle `crm_tasks` für Aufgabenverwaltung
  - Erstelle Tabelle `crm_activities` für Notizen und Historie
  - Erstelle Tabelle `crm_reminders` für automatische Erinnerungen
  - Erweitere `projects` Tabelle um Angebots-Felder (offer_status, offer_sent_date, offer_version, offer_value, offer_accepted_date, rejection_reason)
  - Erstelle Migrations-Skript in `database.py` mit Backup-Funktion
  - Füge Indizes für Performance hinzu
  - _Requirements: 1.1, 2.1, 5.1, 6.1, 7.1, 8.1_

- [ ]* 1.2 Schreibe Unit Tests für Datenbankstruktur
  - Teste Tabellenerstellung
  - Teste Foreign Key Constraints
  - Teste Migrations-Rollback
  - _Requirements: 1.1, 2.1_

### 2. Funktion 1: Automatische Datenübernahme aus Bedarfsanalyse

- [ ] 2.1 Erstelle Data Input Bridge Modul
  - Erstelle Verzeichnis `crm/integration/` falls nicht vorhanden
  - Erstelle `crm/integration/__init__.py`
  - Erstelle `crm/integration/data_input_bridge.py`
  - Implementiere Funktion `extract_customer_data_from_session()` - extrahiert alle Kundendaten aus st.session_state
  - Implementiere Funktion `extract_project_data_from_session()` - extrahiert Projektdetails (Dachfläche, Ausrichtung, etc.)
  - Implementiere Funktion `check_duplicate_customer(email)` - prüft ob Kunde mit E-Mail bereits existiert
  - Nutze bestehende `save_customer()` und `save_project()` Funktionen aus `crm.py`
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2.2 Erweitere bestehenden "Kunde in CRM speichern" Button
  - Aktualisiere `_handle_context_menu_save_to_crm()` in `gui.py`
  - Nutze neue `data_input_bridge` Funktionen für vollständige Datenextraktion
  - Füge Vorschau-Dialog mit allen zu übernehmenden Daten hinzu (st.expander)
  - Implementiere Duplikat-Warnung mit Radio-Buttons (Aktualisieren/Neu anlegen/Abbrechen)
  - Füge Erfolgsbestätigung mit st.success und Link zum Kundenprofil hinzu
  - Aktualisiere auch `drawer_actions.py` für Konsistenz
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 2.3 Implementiere Validierung und Fehlerbehandlung
  - Validiere Pflichtfelder (first_name, last_name, email) vor Übernahme
  - Zeige klare Fehlermeldungen mit st.error bei fehlenden Daten
  - Implementiere try-except mit Rollback bei Datenbankfehlern
  - Protokolliere Fehler in Logdatei
  - _Requirements: 1.5_

- [ ]* 2.4 Schreibe Tests für Datenübernahme
  - Teste vollständige Datenübernahme
  - Teste Duplikatserkennung
  - Teste Fehlerbehandlung
  - _Requirements: 1.1, 1.2, 1.3_

### 3. Funktion 3: Automatische PDF-Archivierung

- [ ] 3.1 Erstelle PDF Bridge Modul
  - Erstelle `crm/integration/pdf_bridge.py`
  - Implementiere Funktion `auto_save_pdf_to_customer_documents(customer_id, project_id, pdf_bytes, pdf_type, version)`
  - Nutze bestehende `add_customer_document()` Funktion aus `database.py`
  - Implementiere Metadaten-Extraktion (Typ: 'offer_pdf', 'calculation_pdf', 'contract_pdf', Version, Datum)
  - Implementiere automatische Versionsnummerierung basierend auf existierenden PDFs
  - _Requirements: 3.1, 3.2_

- [ ] 3.2 Erweitere PDF-Generator
  - Integriere `pdf_bridge.auto_save_pdf_to_customer_documents()` in `pdf_generator.py`
  - Finde alle PDF-Generierungs-Funktionen (z.B. `generate_offer_pdf()`)
  - Füge Kundenzuordnung vor PDF-Generierung hinzu falls nicht vorhanden (Dialog mit Kundenauswahl)
  - Rufe `auto_save_pdf_to_customer_documents()` nach erfolgreicher PDF-Erstellung auf
  - Zeige Bestätigung "PDF wurde in Kundenakte gespeichert"
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3.3 Erweitere Kundenakte-UI in crm.py
  - Aktualisiere Dokumentenliste-Anzeige um PDF-Typ und Version zu zeigen
  - Implementiere chronologische Sortierung (neueste zuerst)
  - Füge Badges für PDF-Typ hinzu (🔵 Angebot, 🟢 Berechnung, 🟡 Vertrag)
  - Füge Download-Protokollierung in `crm_activities` Tabelle hinzu
  - Zeige Anzahl der Versionen pro PDF-Typ
  - _Requirements: 3.3, 3.4_

- [ ]* 3.4 Schreibe Tests für PDF-Archivierung
  - Teste automatisches Speichern
  - Teste Metadaten-Extraktion
  - Teste Versionierung
  - _Requirements: 3.1, 3.2, 3.3_

### 4. Funktion 2: Berechnungsergebnisse verknüpfen

- [ ] 4.1 Erstelle Calculation Bridge Modul
  - Erstelle `crm/integration/calculation_bridge.py`
  - Implementiere Funktion `save_calculation_to_project(project_id, calculation_data, dynamic_keys, is_main_offer=False)`
  - Implementiere Versionierungs-Logik: Zähle existierende Versionen und inkrementiere
  - Implementiere dynamische Keys Extraktion aus st.session_state (alle Berechnungsergebnisse)
  - Speichere in `project_calculations` Tabelle als JSON
  - Nutze `json.dumps()` für Serialisierung
  - _Requirements: 2.1, 2.2_

- [ ] 4.2 Erweitere Berechnungs-Module
  - Integriere `calculation_bridge` in `calculations.py` nach erfolgreicher Berechnung
  - Integriere `calculation_bridge` in `analysis.py` nach Analyse
  - Füge automatisches Speichern nach Berechnung hinzu (optional mit Checkbox "In CRM speichern")
  - Zeige Bestätigung "Berechnung wurde als Version X gespeichert"
  - Verknüpfe mit aktuellem Projekt aus Session State
  - _Requirements: 2.1, 2.2_

- [ ] 4.3 Erstelle Berechnungs-Historie UI
  - Erstelle neue Sektion "📊 Berechnungshistorie" in `crm.py` unter Projektdetails
  - Zeige alle Versionen chronologisch in Tabelle (Version, Datum, Hauptwerte, Status)
  - Implementiere Vergleichs-Ansicht für zwei Versionen (Side-by-Side mit Differenzen)
  - Füge "⭐ Als Hauptangebot markieren" Button hinzu (setzt is_main_offer=1)
  - Zeige Hauptangebot mit Badge hervorgehoben
  - Füge "👁️ Details anzeigen" Button für jede Version hinzu
  - _Requirements: 2.2, 2.3, 2.4_

- [ ] 4.4 Implementiere Archivierungs-Logik
  - Füge `archived` Boolean-Feld zur `project_calculations` Tabelle hinzu
  - Implementiere Funktion `archive_old_calculations()` die Berechnungen älter als 90 Tage markiert
  - Füge Filter-Toggle "Archivierte anzeigen" in UI hinzu
  - Zeige archivierte Berechnungen ausgegraut
  - _Requirements: 2.5_

- [ ]* 4.5 Schreibe Tests für Berechnungsverknüpfung
  - Teste Speichern von Berechnungen
  - Teste Versionierung
  - Teste Vergleichs-Funktion
  - _Requirements: 2.1, 2.2, 2.3_

### 5. Funktion 18: Automatische Datensicherung

- [ ] 5.1 Implementiere Backup-Scheduler
  - Prüfe ob APScheduler bereits in requirements.txt ist (✅ bereits vorhanden in setup.py)
  - Erstelle Verzeichnis `crm/utils/` falls nicht vorhanden
  - Erstelle `crm/utils/__init__.py`
  - Erstelle `crm/utils/backup_scheduler.py`
  - Nutze bestehende `backup_database()` Funktion aus `database.py`
  - Implementiere BackgroundScheduler mit täglichen Backups (2:00 Uhr)
  - Implementiere wöchentliche Backups (Sonntag 3:00 Uhr)
  - Implementiere monatliche Backups (1. des Monats 4:00 Uhr)
  - Starte Scheduler beim App-Start in `gui.py`
  - _Requirements: 18.1, 18.2_

- [ ] 5.2 Implementiere Backup-Rotation
  - Implementiere Funktion `cleanup_old_backups()` in `backup_scheduler.py`
  - Behalte letzte 7 tägliche Backups (Präfix: `daily_`)
  - Behalte letzte 4 wöchentliche Backups (Präfix: `weekly_`)
  - Behalte letzte 12 monatliche Backups (Präfix: `monthly_`)
  - Lösche ältere Backups automatisch nach jedem Backup
  - Protokolliere gelöschte Backups in Logdatei
  - _Requirements: 18.2_

- [ ] 5.3 Erweitere Admin-Panel
  - Füge neuen Tab "💾 Backup-Verwaltung" zu `admin_panel.py` hinzu
  - Zeige Liste aller Backups mit Größe, Datum und Typ (täglich/wöchentlich/monatlich)
  - Implementiere "🔄 Manuelles Backup erstellen" Button
  - Implementiere "📥 Wiederherstellen" Button mit Bestätigungs-Dialog
  - Zeige Warnung: "Aktuelle Daten werden überschrieben!"
  - Implementiere "🗑️ Backup löschen" Funktion
  - Zeige Backup-Status (letztes Backup, nächstes geplantes Backup)
  - _Requirements: 18.3, 18.4_

- [ ] 5.4 Implementiere E-Mail-Benachrichtigungen (Optional - benötigt E-Mail-System)
  - Sende E-Mail bei Backup-Fehlern
  - Sende wöchentliche Backup-Status-E-Mail
  - _Requirements: 18.5_
  - _Hinweis: Abhängig von Funktion 4 (E-Mail-Integration)_

- [ ]* 5.5 Schreibe Tests für Backup-System
  - Teste Backup-Erstellung
  - Teste Rotation
  - Teste Wiederherstellung
  - _Requirements: 18.1, 18.2, 18.3_

### 6. Funktion 7: Angebotsverfolgung

- [ ] 6.1 Erweitere Projekt-Datenmodell (bereits in Task 1.1 enthalten)
  - Felder werden in Task 1.1 zur `projects` Tabelle hinzugefügt
  - Implementiere Status-Workflow: 'draft' → 'sent' → 'accepted'/'rejected'
  - _Requirements: 7.1, 7.2_

- [ ] 6.2 Erstelle Offer Tracker Modul
  - Erstelle Verzeichnis `crm/features/` falls nicht vorhanden
  - Erstelle `crm/features/__init__.py`
  - Erstelle `crm/features/offer_tracker.py`
  - Implementiere Funktion `update_offer_status(project_id, new_status, rejection_reason=None)`
  - Implementiere Funktion `get_offers_by_status(status)` - gibt alle Projekte mit diesem Status zurück
  - Implementiere Funktion `get_offers_needing_followup()` - gibt Angebote zurück die >7 Tage alt sind und Status 'sent' haben
  - Implementiere Funktion `set_offer_sent(project_id, offer_value)` - setzt Status auf 'sent' und Datum
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 6.3 Erstelle Angebotsverfolgung UI
  - Erstelle neue Sektion "📋 Angebotsverfolgung" in `crm_dashboard_ui.py`
  - Zeige alle Angebote gruppiert nach Status (Draft, Versendet, Angenommen, Abgelehnt)
  - Implementiere Status-Änderungs-Dropdown für jedes Angebot
  - Füge Ablehnungsgrund-Erfassung hinzu (Text-Input bei Status 'rejected')
  - Zeige Angebotswert und Versanddatum
  - Markiere Angebote die Follow-up benötigen (>7 Tage) mit 🔔 Icon
  - Implementiere Filter nach Status und Zeitraum
  - _Requirements: 7.2, 7.4, 7.5_

- [ ] 6.4 Integriere mit PDF-Generierung
  - Aktualisiere `pdf_generator.py` nach erfolgreicher PDF-Erstellung
  - Rufe `offer_tracker.set_offer_sent()` auf wenn PDF generiert wird
  - Setze Status auf "sent" und speichere Versanddatum
  - Extrahiere Angebotswert aus Berechnungsdaten
  - Zeige Bestätigung "Angebotsstatus aktualisiert"
  - _Requirements: 7.2_

- [ ] 6.5 Implementiere automatische Follow-up-Erinnerungen
  - Erstelle Erinnerung 7 Tage nach Versand in `crm_reminders` Tabelle
  - Integriere mit Erinnerungs-System (wird in Task 9 implementiert)
  - Trigger: Wenn offer_status auf 'sent' gesetzt wird
  - _Requirements: 7.3_

- [ ]* 6.6 Schreibe Tests für Angebotsverfolgung
  - Teste Status-Workflow
  - Teste Follow-up-Erstellung
  - Teste Ablehnungsgrund-Erfassung
  - _Requirements: 7.1, 7.2, 7.3_

### 7. Funktion 6: Notizen und Kommunikationshistorie

- [ ] 7.1 Erstelle Note Manager Modul
  - Erstelle `crm/features/note_manager.py`
  - Implementiere CRUD-Funktionen für Aktivitäten:
    - `add_activity(customer_id, activity_type, title, content, created_by, is_important=False)`
    - `get_activities(customer_id, activity_type=None, is_important=None)`
    - `update_activity(activity_id, title, content, is_important)`
    - `delete_activity(activity_id)`
  - Implementiere Funktion `get_customer_timeline(customer_id)` - gibt alle Aktivitäten chronologisch zurück
  - Implementiere Volltextsuche mit SQLite FTS5 (CREATE VIRTUAL TABLE für content-Suche)
  - Implementiere Funktion `search_activities(customer_id, search_term)`
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 7.2 Erstelle Timeline UI
  - Erstelle neue Sektion "📝 Kommunikationshistorie" in `crm.py` unter Kundendetails
  - Zeige alle Aktivitäten chronologisch (neueste zuerst)
  - Implementiere Aktivitäts-Typen mit Icons:
    - 📝 Notiz
    - 📧 E-Mail (für später)
    - 📞 Anruf
    - 📅 Termin
    - 📄 Dokument hochgeladen
    - 💰 Angebot versendet
  - Zeige Zeitstempel, Ersteller, Titel und Content
  - Markiere wichtige Aktivitäten mit ⭐
  - _Requirements: 6.2_

- [ ] 7.3 Implementiere Notiz-Erstellung
  - Füge "➕ Neue Notiz" Button in Timeline-Sektion hinzu
  - Implementiere Notiz-Editor mit st.text_area (Rich Text optional später)
  - Füge Titel-Feld hinzu
  - Füge Checkbox "⭐ Als wichtig markieren" hinzu
  - Speichere Benutzer automatisch (aus Session State oder "System")
  - Speichere Zeitstempel automatisch (CURRENT_TIMESTAMP)
  - Zeige Erfolgsbestätigung nach Speichern
  - _Requirements: 6.1, 6.4_

- [ ] 7.4 Implementiere Suche und Filter
  - Füge Suchfeld für Volltextsuche hinzu (st.text_input)
  - Implementiere Filter nach Aktivitätstyp (st.multiselect)
  - Implementiere Datumsfilter (st.date_input für Von/Bis)
  - Implementiere Toggle "Nur wichtige anzeigen" (st.checkbox)
  - Aktualisiere Timeline basierend auf Filtern
  - _Requirements: 6.3_

- [ ] 7.5 Implementiere Archivierung
  - Füge `archived` Boolean-Feld zur `crm_activities` Tabelle hinzu
  - Implementiere Funktion `archive_old_activities()` - markiert Aktivitäten älter als 30 Tage
  - Füge Toggle "Archivierte anzeigen" in UI hinzu
  - Zeige archivierte Aktivitäten ausgegraut
  - Implementiere "Archivieren" Button für einzelne Aktivitäten
  - _Requirements: 6.5_

- [ ]* 7.6 Schreibe Tests für Notizen-System
  - Teste CRUD-Operationen
  - Teste Timeline-Generierung
  - Teste Volltextsuche
  - _Requirements: 6.1, 6.2, 6.3_

### 8. Funktion 5: Aufgabenverwaltung

- [ ] 8.1 Erstelle Task Manager Modul
  - Erstelle `crm/features/task_manager.py`
  - Implementiere CRUD-Funktionen für Tasks:
    - `create_task(title, description, status, priority, due_date, customer_id, project_id, lead_id, assigned_to)`
    - `get_tasks(customer_id=None, project_id=None, lead_id=None, status=None)`
    - `update_task(task_id, **kwargs)`
    - `complete_task(task_id)` - setzt status='completed' und completed_at
    - `delete_task(task_id)`
  - Implementiere Funktion `get_tasks_by_status(status)` - gibt alle Tasks mit diesem Status zurück
  - Implementiere Funktion `get_overdue_tasks()` - gibt Tasks mit due_date < heute und status != 'completed' zurück
  - Implementiere Funktion `get_tasks_due_today()` - gibt Tasks mit due_date = heute zurück
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 8.2 Erstelle Task UI
  - Erstelle neue Sektion "✅ Aufgabenverwaltung" in `crm_dashboard_ui.py`
  - Implementiere Task-Erstellungs-Dialog mit st.form
  - Zeige Tasks gruppiert nach Status in Tabs:
    - 📋 Offen (status='open')
    - 🔄 In Arbeit (status='in_progress')
    - ✅ Erledigt (status='completed')
  - Zeige Task-Details: Titel, Beschreibung, Priorität, Fälligkeit, Zuordnung
  - Implementiere Status-Änderungs-Buttons für jede Task
  - Optional: Drag & Drop für Status-Änderung (später)
  - _Requirements: 5.1, 5.3_

- [ ] 8.3 Implementiere Task-Zuordnung
  - Füge Zuordnungs-Felder zum Task-Formular hinzu:
    - st.selectbox für Kunde (aus customers Tabelle)
    - st.selectbox für Projekt (aus projects Tabelle, gefiltert nach Kunde)
    - st.selectbox für Lead (aus crm_leads Tabelle)
  - Zeige zugeordnete Tasks in jeweiligen Profilen:
    - In Kundendetails-Seite
    - In Projektdetails-Seite
    - In Lead-Details in Pipeline
  - Implementiere Filter "Meine Tasks" vs "Alle Tasks"
  - _Requirements: 5.1_

- [ ] 8.4 Implementiere Prioritäten und Fälligkeiten
  - Füge Prioritäts-Auswahl hinzu: st.selectbox(['Niedrig', 'Mittel', 'Hoch', 'Dringend'])
  - Implementiere Fälligkeitsdatum-Auswahl mit st.date_input
  - Zeige überfällige Tasks rot hervorgehoben (🔴)
  - Zeige heute fällige Tasks orange hervorgehoben (🟠)
  - Zeige Priorität mit Badges (🔵 Niedrig, 🟡 Mittel, 🟠 Hoch, 🔴 Dringend)
  - Sortiere Tasks nach Priorität und Fälligkeit
  - _Requirements: 5.2, 5.3, 5.5_

- [ ] 8.5 Integriere mit Benachrichtigungssystem
  - Erstelle Benachrichtigung in `crm_reminders` Tabelle bei fälliger Task
  - Zeige Anzahl offener Tasks im Dashboard (Badge)
  - Zeige Anzahl überfälliger Tasks prominent (Warnung)
  - Implementiere Dashboard-Widget "Meine Aufgaben heute"
  - _Requirements: 5.2_

- [ ] 8.6 Implementiere Aktivitäts-Protokollierung
  - Protokolliere Task-Erstellung in `crm_activities` Timeline (activity_type='task_created')
  - Protokolliere Task-Abschluss in Timeline (activity_type='task_completed')
  - Nutze `note_manager.add_activity()` aus Task 7.1
  - Zeige Tasks in Kommunikationshistorie
  - _Requirements: 5.4_

- [ ]* 8.7 Schreibe Tests für Task-Management
  - Teste CRUD-Operationen
  - Teste Fälligkeits-Logik
  - Teste Zuordnungs-Funktionen
  - _Requirements: 5.1, 5.2, 5.3_

### 9. Funktion 8: Automatische Erinnerungen und Follow-ups

- [ ] 9.1 Erstelle Notification Manager Modul
  - Erstelle `crm/utils/notification_manager.py`
  - Implementiere CRUD-Funktionen für Erinnerungen:
    - `create_reminder(reminder_type, related_id, related_type, due_date, message)`
    - `get_reminders(status=None, due_before=None)`
    - `get_due_reminders()` - gibt Erinnerungen mit due_date <= jetzt und status='pending' zurück
    - `mark_reminder_as_completed(reminder_id)`
    - `snooze_reminder(reminder_id, days=2)` - verschiebt due_date um X Tage
    - `delete_reminder(reminder_id)`
  - Implementiere Funktion `get_customer_reminders(customer_id)` für Kundenansicht
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 9.2 Implementiere Regel-Engine
  - Erstelle `crm/utils/reminder_rules.py`
  - Implementiere Regel-Funktionen:
    - `create_lead_followup_reminder(lead_id)` - Follow-up nach 3 Tagen
    - `create_offer_followup_reminder(project_id)` - Follow-up nach 7 Tagen
    - `create_appointment_followup_reminder(appointment_id)` - Follow-up nach 1 Tag
  - Integriere Regel-Aufrufe in entsprechende Module:
    - In `crm_pipeline_ui.py` bei Lead-Erstellung
    - In `offer_tracker.py` bei Angebot-Versand (Task 6.4)
    - In `crm_calendar_ui.py` nach Termin
  - Implementiere konfigurierbare Regeln im Admin-Panel (Tage anpassbar)
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9.3 Implementiere Erinnerungs-Scheduler
  - Erweitere `backup_scheduler.py` um Erinnerungs-Check
  - Integriere mit APScheduler (bereits vorhanden aus Task 5.1)
  - Prüfe stündlich auf fällige Erinnerungen mit `get_due_reminders()`
  - Erstelle automatisch Erinnerungen basierend auf Regeln
  - Protokolliere Erinnerungs-Erstellung in Logdatei
  - Optional: Zeige Benachrichtigung in Streamlit (st.toast)
  - _Requirements: 8.1, 8.4_

- [ ] 9.4 Erstelle Erinnerungs-UI
  - Füge Erinnerungs-Widget "🔔 Erinnerungen" zum Dashboard hinzu (`crm_dashboard_ui.py`)
  - Zeige fällige Erinnerungen prominent (rot hervorgehoben)
  - Zeige kommende Erinnerungen (nächste 7 Tage)
  - Implementiere "✅ Erledigt" Button - ruft `mark_reminder_as_completed()` auf
  - Implementiere "⏰ Später erinnern" Button - ruft `snooze_reminder()` auf
  - Zeige Anzahl fälliger Erinnerungen als Badge
  - Gruppiere Erinnerungen nach Typ (Lead, Angebot, Termin, Task)
  - _Requirements: 8.4_

- [ ] 9.5 Implementiere Wiederholungs-Logik
  - Füge `repeat_count` Feld zur `crm_reminders` Tabelle hinzu
  - Implementiere Funktion `auto_snooze_ignored_reminders()` in Scheduler
  - Erstelle Erinnerung erneut nach 2 Tagen wenn status='pending' und due_date < jetzt - 1 Tag
  - Inkrementiere repeat_count bei jeder Wiederholung
  - Begrenze auf maximal 3 Wiederholungen (dann status='expired')
  - Zeige Wiederholungs-Anzahl in UI
  - _Requirements: 8.5_

- [ ]* 9.6 Schreibe Tests für Erinnerungs-System
  - Teste Regel-Engine
  - Teste Erinnerungs-Erstellung
  - Teste Wiederholungs-Logik
  - _Requirements: 8.1, 8.2, 8.3_

---

## Phase 2: Erweiterte Funktionen (Optional)

### 10. Funktion 10: Kunden-Segmentierung und Tags

- [ ] 10.1 Erstelle Tag-Datenmodell
  - Erstelle Tabelle `crm_tags`
  - Erstelle Tabelle `customer_tags` (Many-to-Many)
  - _Requirements: 10.1_

- [ ] 10.2 Implementiere Tag-Management
  - Erstelle Tag-Verwaltung im Admin-Panel
  - Implementiere CRUD-Funktionen für Tags
  - Füge Farb-Auswahl für Tags hinzu
  - _Requirements: 10.1, 10.3_

- [ ] 10.3 Erweitere Kunden-UI
  - Füge Tag-Auswahl zu Kunden-Formular hinzu
  - Zeige Tags in Kundenliste
  - Implementiere Tag-Filter
  - _Requirements: 10.1, 10.2_

- [ ] 10.4 Implementiere Massen-Tagging
  - Füge Mehrfachauswahl in Kundenliste hinzu
  - Implementiere "Tags hinzufügen" Massen-Aktion
  - _Requirements: 10.4_

- [ ]* 10.5 Schreibe Tests für Tag-System
  - Teste Tag-CRUD
  - Teste Tag-Zuordnung
  - Teste Filter-Funktionen
  - _Requirements: 10.1, 10.2, 10.3_

### 11. Funktion 12: Kunden-Import/Export

- [ ] 11.1 Erstelle Import/Export Manager Modul
  - Erstelle `crm/utils/import_export_manager.py`
  - Implementiere CSV-Import mit Pandas
  - Implementiere Excel-Import mit Pandas
  - Implementiere vCard-Import (optional)
  - _Requirements: 12.1, 12.2_

- [ ] 11.2 Implementiere Duplikatserkennung
  - Erkenne Duplikate via E-Mail
  - Erkenne Duplikate via Name + PLZ
  - Implementiere Auswahl-Dialog (Überspringen/Aktualisieren/Duplizieren)
  - _Requirements: 12.3_

- [ ] 11.3 Erstelle Import-UI
  - Füge Import-Sektion zum Admin-Panel hinzu
  - Implementiere Datei-Upload
  - Zeige Vorschau der zu importierenden Daten
  - Implementiere Feld-Mapping-UI
  - Zeige Import-Fortschritt
  - _Requirements: 12.1, 12.3, 12.4_

- [ ] 11.4 Implementiere Export-Funktionen
  - Exportiere alle Kunden als CSV
  - Exportiere alle Kunden als Excel
  - Inkludiere alle Felder und Notizen
  - _Requirements: 12.2_

- [ ] 11.5 Implementiere Fehlerbehandlung
  - Validiere Daten vor Import
  - Zeige detaillierten Fehlerbericht
  - Implementiere Rollback bei kritischen Fehlern
  - _Requirements: 12.4, 12.5_

- [ ]* 11.6 Schreibe Tests für Import/Export
  - Teste CSV-Import
  - Teste Excel-Import
  - Teste Duplikatserkennung
  - Teste Export
  - _Requirements: 12.1, 12.2, 12.3_

### 12. Funktion 17: Lead Scoring

- [ ] 12.1 Erweitere Lead-Datenmodell
  - Füge `score` Feld zur `crm_leads` Tabelle hinzu
  - Füge `score_factors` JSON-Feld hinzu
  - _Requirements: 17.1, 17.2_

- [ ] 12.2 Erstelle Scoring-Engine
  - Erstelle `crm/features/lead_scoring.py`
  - Implementiere Scoring-Algorithmus
  - Implementiere Faktoren:
    - Projektgröße (0-30 Punkte)
    - Lead-Quelle (0-20 Punkte)
    - Reaktionszeit (0-20 Punkte)
    - Engagement (0-30 Punkte)
  - _Requirements: 17.1, 17.2_

- [ ] 12.3 Implementiere automatische Score-Berechnung
  - Berechne Score bei Lead-Erstellung
  - Berechne Score neu bei Datenänderung
  - _Requirements: 17.1, 17.2_

- [ ] 12.4 Erstelle Scoring-Konfiguration
  - Füge Scoring-Regeln zum Admin-Panel hinzu
  - Implementiere Gewichtungs-Einstellungen
  - Ermögliche Anpassung der Faktoren
  - _Requirements: 17.3_

- [ ] 12.5 Erweitere Pipeline-UI
  - Zeige Score bei jedem Lead
  - Implementiere Sortierung nach Score
  - Füge Score-Visualisierung hinzu (Fortschrittsbalken)
  - _Requirements: 17.4_

- [ ] 12.6 Implementiere High-Score-Benachrichtigungen
  - Sende Benachrichtigung bei Score > 80
  - Zeige High-Score-Leads im Dashboard
  - _Requirements: 17.5_

- [ ]* 12.7 Schreibe Tests für Lead Scoring
  - Teste Score-Berechnung
  - Teste automatische Neuberechnung
  - Teste Benachrichtigungen
  - _Requirements: 17.1, 17.2, 17.5_

---

## Phase 3: Optionale Funktionen (Nach Bedarf)

### 13. Funktion 4: E-Mail-Integration

- [ ] 13.1 Erstelle Email Manager Modul
  - Erstelle `crm/features/email_manager.py`
  - Implementiere SMTP-Konfiguration
  - Implementiere E-Mail-Versand-Funktion
  - Implementiere E-Mail-Historie-Speicherung
  - _Requirements: 4.1, 4.2_

- [ ] 13.2 Erstelle E-Mail-Vorlagen-System
  - Erstelle Tabelle `email_templates`
  - Implementiere Platzhalter-System
  - Implementiere Template-Editor
  - _Requirements: 4.3, 4.4_

- [ ] 13.3 Erweitere Kunden-UI
  - Füge "E-Mail senden" Button hinzu
  - Implementiere E-Mail-Composer
  - Füge Anhang-Auswahl aus Kundenakte hinzu
  - Zeige E-Mails in Timeline
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 13.4 Implementiere SMTP-Konfiguration
  - Füge SMTP-Einstellungen zum Admin-Panel hinzu
  - Implementiere Test-E-Mail-Funktion
  - Zeige Konfigurationsanleitung bei Fehlen
  - _Requirements: 4.5_

- [ ]* 13.5 Schreibe Tests für E-Mail-System
  - Teste E-Mail-Versand (Mock)
  - Teste Template-Rendering
  - Teste Historie-Speicherung
  - _Requirements: 4.1, 4.2, 4.3_

### 14. Funktion 9: Erweiterte Reporting

- [ ] 14.1 Erstelle Reporting Engine Modul
  - Erstelle `crm/features/reporting_engine.py`
  - Implementiere Datenabfrage-Funktionen
  - Implementiere Aggregations-Funktionen
  - _Requirements: 9.1, 9.2_

- [ ] 14.2 Implementiere vordefinierte Reports
  - Verkaufsübersicht (täglich/wöchentlich/monatlich)
  - Conversion-Funnel
  - Lead-Quellen-Analyse
  - Mitarbeiter-Performance
  - _Requirements: 9.1, 9.2_

- [ ] 14.3 Erstelle Report-Builder UI
  - Implementiere Filter-Auswahl
  - Implementiere Gruppierungs-Optionen
  - Implementiere Aggregations-Auswahl
  - Zeige Vorschau
  - _Requirements: 9.2_

- [ ] 14.4 Implementiere Export-Funktionen
  - Export als Excel (openpyxl)
  - Export als PDF (ReportLab)
  - Export als CSV
  - _Requirements: 9.3_

- [ ] 14.5 Implementiere Report-Vorlagen
  - Erstelle Tabelle `saved_reports`
  - Implementiere Speichern von Report-Konfigurationen
  - Implementiere Laden gespeicherter Reports
  - _Requirements: 9.4_

- [ ]* 14.6 Schreibe Tests für Reporting
  - Teste Datenabfragen
  - Teste Aggregationen
  - Teste Export-Funktionen
  - _Requirements: 9.1, 9.2, 9.3_

---

## Abschluss und Integration

### 15. Finale Integration und Testing

- [ ] 15.1 Integriere alle Module in Haupt-GUI
  - Aktualisiere `gui.py` mit neuen CRM-Funktionen
  - Füge neue Menüpunkte hinzu
  - Teste Navigation zwischen allen Bereichen
  - _Requirements: Alle_

- [ ] 15.2 Erstelle Dokumentation
  - Schreibe Benutzer-Handbuch
  - Schreibe Entwickler-Dokumentation
  - Erstelle Video-Tutorials (optional)
  - _Requirements: Alle_

- [ ] 15.3 Führe End-to-End-Tests durch
  - Teste kompletten Workflow: Lead → Angebot → Abschluss
  - Teste Datenintegrität über alle Module
  - Teste Performance mit großen Datenmengen
  - _Requirements: Alle_

- [ ] 15.4 Optimiere Performance
  - Füge Datenbank-Indizes hinzu
  - Implementiere Caching wo sinnvoll
  - Optimiere langsame Queries
  - _Requirements: Alle_

- [ ] 15.5 Erstelle Migrations-Guide
  - Dokumentiere Upgrade-Prozess
  - Erstelle Backup-Anleitung
  - Dokumentiere Rollback-Prozess
  - _Requirements: Alle_

---

## Hinweise zur Implementierung

### Reihenfolge

Die Tasks sind so angeordnet, dass Abhängigkeiten berücksichtigt werden. Folge der Reihenfolge für optimale Ergebnisse:

1. **Task 1.1** - Datenbankstruktur (Fundament für alles)
2. **Tasks 2.x** - Datenübernahme (nutzt bestehende Funktionen)
3. **Tasks 3.x** - PDF-Archivierung (nutzt bestehende Infrastruktur)
4. **Tasks 4.x** - Berechnungsversionierung (benötigt DB aus 1.1)
5. **Tasks 5.x** - Backup-System (unabhängig, kann parallel)
6. **Tasks 6.x** - Angebotsverfolgung (benötigt DB aus 1.1)
7. **Tasks 7.x** - Notizen/Historie (benötigt DB aus 1.1)
8. **Tasks 8.x** - Aufgabenverwaltung (benötigt DB aus 1.1 und 7.x)
9. **Tasks 9.x** - Erinnerungen (benötigt 5.x, 6.x, 7.x, 8.x)

### Optionale Tasks

Tasks mit "*" am Ende sind optional (hauptsächlich Unit Tests). Diese können übersprungen werden, wenn Zeitdruck besteht.

### Dynamische Keys

Alle Berechnungsergebnisse und Daten sollten mit dynamischen Keys gespeichert werden für maximale Flexibilität. Beispiel:
```python
{
    "SYSTEM_SIZE_KWP": 15.0,
    "ANNUAL_PRODUCTION_KWH": 14250,
    "INVESTMENT_TOTAL_EUR": 25000,
    "PAYBACK_PERIOD_YEARS": 12.5,
    # ... alle weiteren Werte
}
```

### Bestehende Infrastruktur nutzen

- ✅ `add_customer_document()` für PDF-Speicherung vorhanden
- ✅ `save_customer()` und `save_project()` in `crm.py` vorhanden
- ✅ `backup_database()` in `database.py` vorhanden
- ✅ APScheduler bereits in `setup.py` definiert
- ✅ Basis-CRM-UI vorhanden, nur erweitern

### Testing

Auch wenn Unit Tests optional sind, sollte jede Funktion manuell getestet werden vor dem Merge.

### Dokumentation

Dokumentiere jeden neuen Modul und jede neue Funktion inline mit Docstrings im Google-Style:
```python
def function_name(param1: str, param2: int) -> bool:
    """Kurzbeschreibung der Funktion.
    
    Längere Beschreibung falls nötig.
    
    Args:
        param1: Beschreibung von param1
        param2: Beschreibung von param2
        
    Returns:
        Beschreibung des Rückgabewerts
        
    Raises:
        ValueError: Wenn param2 < 0
    """
```

---

## Geschätzter Gesamtaufwand (Phase 1 nur)

- **Task 1: Datenbankstruktur:** 4-6 Stunden
- **Task 2: Datenübernahme:** 6-8 Stunden
- **Task 3: PDF-Archivierung:** 4-6 Stunden
- **Task 4: Berechnungsversionierung:** 10-14 Stunden
- **Task 5: Backup-System:** 6-8 Stunden
- **Task 6: Angebotsverfolgung:** 10-14 Stunden
- **Task 7: Notizen/Historie:** 12-16 Stunden
- **Task 8: Aufgabenverwaltung:** 14-18 Stunden
- **Task 9: Erinnerungen:** 12-16 Stunden

**Gesamt Phase 1:** 78-106 Stunden ≈ 2-3 Monate bei Teilzeit (20h/Woche)

---

## Nächste Schritte

1. ✅ Spec-Dokumente sind vollständig (Requirements, Design, Tasks)
2. ⏭️ Beginne mit **Task 1.1** (Datenbankstruktur) - dies ist das Fundament
3. 📝 Teste jede Funktion nach Fertigstellung manuell
4. 📚 Dokumentiere Änderungen inline mit Docstrings
5. 🔄 Committe nach jedem abgeschlossenen Task

**Bereit zum Start? Öffne tasks.md und klicke auf "Start task" neben Task 1.1!**
