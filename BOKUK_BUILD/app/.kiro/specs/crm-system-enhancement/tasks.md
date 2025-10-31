# CRM System Enhancement - Implementation Tasks

## Übersicht

Dieses Dokument enthält die Implementierungs-Tasks für das erweiterte CRM-System. Die Tasks sind nach Priorität und Abhängigkeiten sortiert.

**Hinweis:** Tasks mit "*" am Ende sind optional (z.B. Unit Tests) und können übersprungen werden.

---

## Phase 1: Kern-Funktionen (MVP + Essentials)

### 1. Projekt-Setup und Datenbankstruktur

- [ ] 1.1 Erstelle neue Datenbankstruktur für CRM-Erweiterungen
  - Erstelle Tabelle `project_calculations` für Berechnungsversionierung
  - Erstelle Tabelle `crm_tasks` für Aufgabenverwaltung
  - Erstelle Tabelle `crm_activities` für Notizen und Historie
  - Erstelle Tabelle `crm_reminders` für automatische Erinnerungen
  - Erweitere `projects` Tabelle um Angebots-Felder
  - Erstelle Migrations-Skript mit Backup-Funktion
  - _Requirements: 1.1, 2.1, 5.1, 6.1, 7.1, 8.1_

- [ ]* 1.2 Schreibe Unit Tests für Datenbankstruktur
  - Teste Tabellenerstellung
  - Teste Foreign Key Constraints
  - Teste Migrations-Rollback
  - _Requirements: 1.1, 2.1_

### 2. Funktion 1: Automatische Datenübernahme aus Bedarfsanalyse

- [ ] 2.1 Erstelle Data Input Bridge Modul
  - Erstelle `crm/integration/data_input_bridge.py`
  - Implementiere Funktion `extract_customer_data_from_session()`
  - Implementiere Funktion `extract_project_data_from_session()`
  - Implementiere Duplikatserkennung via E-Mail
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2.2 Erweitere Bedarfsanalyse-UI
  - Verbessere "Kunde in CRM speichern" Button
  - Füge Vorschau-Dialog mit allen zu übernehmenden Daten hinzu
  - Implementiere Duplikat-Warnung mit Optionen (Aktualisieren/Neu anlegen)
  - Füge Erfolgsbestätigung mit Link zum Kundenprofil hinzu
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 2.3 Implementiere Validierung und Fehlerbehandlung
  - Validiere Pflichtfelder vor Übernahme
  - Zeige klare Fehlermeldungen bei fehlenden Daten
  - Implementiere Rollback bei Fehlern
  - _Requirements: 1.5_

- [ ]* 2.4 Schreibe Tests für Datenübernahme
  - Teste vollständige Datenübernahme
  - Teste Duplikatserkennung
  - Teste Fehlerbehandlung
  - _Requirements: 1.1, 1.2, 1.3_

### 3. Funktion 3: Automatische PDF-Archivierung

- [ ] 3.1 Erstelle PDF Bridge Modul
  - Erstelle `crm/integration/pdf_bridge.py`
  - Implementiere Funktion `auto_save_pdf_to_customer_documents()`
  - Implementiere Metadaten-Extraktion (Typ, Version, Datum)
  - _Requirements: 3.1, 3.2_

- [ ] 3.2 Erweitere PDF-Generator
  - Integriere `pdf_bridge.auto_save_pdf_to_customer_documents()` in `pdf_generator.py`
  - Füge Kundenzuordnung vor PDF-Generierung hinzu (falls nicht vorhanden)
  - Implementiere automatische Versionsnummerierung
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3.3 Erweitere Kundenakte-UI
  - Zeige PDF-Typ und Version in Dokumentenliste
  - Implementiere chronologische Sortierung
  - Füge Download-Protokollierung hinzu
  - _Requirements: 3.3, 3.4_

- [ ]* 3.4 Schreibe Tests für PDF-Archivierung
  - Teste automatisches Speichern
  - Teste Metadaten-Extraktion
  - Teste Versionierung
  - _Requirements: 3.1, 3.2, 3.3_

### 4. Funktion 2: Berechnungsergebnisse verknüpfen

- [ ] 4.1 Erstelle Calculation Bridge Modul
  - Erstelle `crm/integration/calculation_bridge.py`
  - Implementiere Funktion `save_calculation_to_project()`
  - Implementiere Versionierungs-Logik
  - Implementiere dynamische Keys Extraktion
  - _Requirements: 2.1, 2.2_

- [ ] 4.2 Erweitere Berechnungs-Module
  - Integriere `calculation_bridge` in `calculations.py`
  - Integriere `calculation_bridge` in `analysis.py`
  - Füge automatisches Speichern nach Berechnung hinzu
  - _Requirements: 2.1, 2.2_

- [ ] 4.3 Erstelle Berechnungs-Historie UI
  - Erstelle neue Sektion in `crm.py` für Berechnungshistorie
  - Zeige alle Versionen chronologisch
  - Implementiere Vergleichs-Ansicht für zwei Versionen
  - Füge "Als Hauptangebot markieren" Funktion hinzu
  - _Requirements: 2.2, 2.3, 2.4_

- [ ] 4.4 Implementiere Archivierungs-Logik
  - Markiere Berechnungen älter als 90 Tage als "archiviert"
  - Füge Filter für aktive/archivierte Berechnungen hinzu
  - _Requirements: 2.5_

- [ ]* 4.5 Schreibe Tests für Berechnungsverknüpfung
  - Teste Speichern von Berechnungen
  - Teste Versionierung
  - Teste Vergleichs-Funktion
  - _Requirements: 2.1, 2.2, 2.3_

### 5. Funktion 18: Automatische Datensicherung

- [ ] 5.1 Implementiere Backup-Scheduler
  - Installiere APScheduler
  - Erstelle `crm/utils/backup_scheduler.py`
  - Implementiere tägliche Backups (2:00 Uhr)
  - Implementiere wöchentliche Backups (Sonntag)
  - Implementiere monatliche Backups (1. des Monats)
  - _Requirements: 18.1, 18.2_

- [ ] 5.2 Implementiere Backup-Rotation
  - Behalte letzte 7 tägliche Backups
  - Behalte letzte 4 wöchentliche Backups
  - Behalte letzte 12 monatliche Backups
  - Lösche ältere Backups automatisch
  - _Requirements: 18.2_

- [ ] 5.3 Erweitere Admin-Panel
  - Füge Backup-Verwaltungs-Sektion hinzu
  - Zeige Liste aller Backups mit Größe und Datum
  - Implementiere manuelle Backup-Erstellung
  - Implementiere Wiederherstellungs-Funktion mit Bestätigung
  - _Requirements: 18.3, 18.4_

- [ ] 5.4 Implementiere E-Mail-Benachrichtigungen
  - Sende E-Mail bei Backup-Fehlern
  - Sende wöchentliche Backup-Status-E-Mail
  - _Requirements: 18.5_

- [ ]* 5.5 Schreibe Tests für Backup-System
  - Teste Backup-Erstellung
  - Teste Rotation
  - Teste Wiederherstellung
  - _Requirements: 18.1, 18.2, 18.3_

### 6. Funktion 7: Angebotsverfolgung

- [ ] 6.1 Erweitere Projekt-Datenmodell
  - Füge Angebots-Status-Felder zur `projects` Tabelle hinzu
  - Implementiere Status-Workflow (Draft → Sent → Accepted/Rejected)
  - _Requirements: 7.1, 7.2_

- [ ] 6.2 Erstelle Offer Tracker Modul
  - Erstelle `crm/features/offer_tracker.py`
  - Implementiere Funktion `update_offer_status()`
  - Implementiere Funktion `get_offers_by_status()`
  - Implementiere Funktion `get_offers_needing_followup()`
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 6.3 Erstelle Angebotsverfolgung UI
  - Erstelle neue Sektion in CRM-Dashboard
  - Zeige alle Angebote mit Status
  - Implementiere Status-Änderungs-Buttons
  - Füge Ablehnungsgrund-Erfassung hinzu
  - _Requirements: 7.2, 7.4, 7.5_

- [ ] 6.4 Integriere mit PDF-Generierung
  - Setze Status auf "Sent" bei PDF-Versand
  - Speichere Versanddatum
  - _Requirements: 7.2_

- [ ] 6.5 Implementiere automatische Follow-up-Erinnerungen
  - Erstelle Erinnerung 7 Tage nach Versand
  - Integriere mit Erinnerungs-System (Funktion 8)
  - _Requirements: 7.3_

- [ ]* 6.6 Schreibe Tests für Angebotsverfolgung
  - Teste Status-Workflow
  - Teste Follow-up-Erstellung
  - Teste Ablehnungsgrund-Erfassung
  - _Requirements: 7.1, 7.2, 7.3_

### 7. Funktion 6: Notizen und Kommunikationshistorie

- [ ] 7.1 Erstelle Note Manager Modul
  - Erstelle `crm/features/note_manager.py`
  - Implementiere CRUD-Funktionen für Aktivitäten
  - Implementiere Funktion `get_customer_timeline()`
  - Implementiere Volltextsuche mit SQLite FTS5
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 7.2 Erstelle Timeline UI
  - Erstelle Timeline-Komponente in `crm.py`
  - Zeige alle Aktivitäten chronologisch
  - Implementiere Aktivitäts-Typen (Notiz, E-Mail, Anruf, Termin)
  - Füge Icons für jeden Typ hinzu
  - _Requirements: 6.2_

- [ ] 7.3 Implementiere Notiz-Erstellung
  - Füge "Neue Notiz" Button hinzu
  - Implementiere Notiz-Editor mit Rich Text
  - Füge "Als wichtig markieren" Option hinzu
  - Speichere Benutzer und Zeitstempel automatisch
  - _Requirements: 6.1, 6.4_

- [ ] 7.4 Implementiere Suche und Filter
  - Füge Suchfeld für Volltextsuche hinzu
  - Implementiere Filter nach Aktivitätstyp
  - Implementiere Filter nach Datum
  - Implementiere Filter "Nur wichtige"
  - _Requirements: 6.3_

- [ ] 7.5 Implementiere Archivierung
  - Markiere Aktivitäten älter als 30 Tage als "archiviert"
  - Füge Toggle für Anzeige archivierter Aktivitäten hinzu
  - _Requirements: 6.5_

- [ ]* 7.6 Schreibe Tests für Notizen-System
  - Teste CRUD-Operationen
  - Teste Timeline-Generierung
  - Teste Volltextsuche
  - _Requirements: 6.1, 6.2, 6.3_

### 8. Funktion 5: Aufgabenverwaltung

- [ ] 8.1 Erstelle Task Manager Modul
  - Erstelle `crm/features/task_manager.py`
  - Implementiere CRUD-Funktionen für Tasks
  - Implementiere Funktion `get_tasks_by_status()`
  - Implementiere Funktion `get_overdue_tasks()`
  - Implementiere Funktion `get_tasks_due_today()`
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 8.2 Erstelle Task UI
  - Erstelle Task-Verwaltungs-Sektion im Dashboard
  - Implementiere Task-Erstellungs-Dialog
  - Zeige Tasks gruppiert nach Status (Offen, In Arbeit, Erledigt)
  - Implementiere Drag & Drop für Status-Änderung (optional)
  - _Requirements: 5.1, 5.3_

- [ ] 8.3 Implementiere Task-Zuordnung
  - Füge Zuordnung zu Kunde, Projekt oder Lead hinzu
  - Zeige zugeordnete Tasks in jeweiligen Profilen
  - _Requirements: 5.1_

- [ ] 8.4 Implementiere Prioritäten und Fälligkeiten
  - Füge Prioritäts-Auswahl hinzu (Niedrig, Mittel, Hoch, Dringend)
  - Implementiere Fälligkeitsdatum-Auswahl
  - Zeige überfällige Tasks rot hervorgehoben
  - _Requirements: 5.2, 5.3, 5.5_

- [ ] 8.5 Integriere mit Benachrichtigungssystem
  - Erstelle Benachrichtigung bei fälliger Task
  - Zeige Anzahl offener Tasks im Dashboard
  - _Requirements: 5.2_

- [ ] 8.6 Implementiere Aktivitäts-Protokollierung
  - Protokolliere Task-Erstellung in Timeline
  - Protokolliere Task-Abschluss in Timeline
  - _Requirements: 5.4_

- [ ]* 8.7 Schreibe Tests für Task-Management
  - Teste CRUD-Operationen
  - Teste Fälligkeits-Logik
  - Teste Zuordnungs-Funktionen
  - _Requirements: 5.1, 5.2, 5.3_

### 9. Funktion 8: Automatische Erinnerungen und Follow-ups

- [ ] 9.1 Erstelle Notification Manager Modul
  - Erstelle `crm/utils/notification_manager.py`
  - Implementiere CRUD-Funktionen für Erinnerungen
  - Implementiere Funktion `create_reminder()`
  - Implementiere Funktion `get_due_reminders()`
  - Implementiere Funktion `mark_reminder_as_completed()`
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 9.2 Implementiere Regel-Engine
  - Erstelle Regel: Lead erstellt → Follow-up nach 3 Tagen
  - Erstelle Regel: Angebot versendet → Follow-up nach 7 Tagen
  - Erstelle Regel: Termin → Follow-up nach 1 Tag
  - Implementiere konfigurierbare Regeln im Admin-Panel
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9.3 Implementiere Erinnerungs-Scheduler
  - Integriere mit APScheduler
  - Prüfe stündlich auf fällige Erinnerungen
  - Erstelle automatisch Erinnerungen basierend auf Regeln
  - _Requirements: 8.1, 8.4_

- [ ] 9.4 Erstelle Erinnerungs-UI
  - Füge Erinnerungs-Widget zum Dashboard hinzu
  - Zeige fällige Erinnerungen prominent
  - Implementiere "Erledigt" und "Später erinnern" Buttons
  - _Requirements: 8.4_

- [ ] 9.5 Implementiere Wiederholungs-Logik
  - Erstelle Erinnerung erneut nach 2 Tagen wenn ignoriert
  - Begrenze auf maximal 3 Wiederholungen
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

Die Tasks sind so angeordnet, dass Abhängigkeiten berücksichtigt werden. Folge der Reihenfolge für optimale Ergebnisse.

### Optionale Tasks

Tasks mit "*" am Ende sind optional (hauptsächlich Unit Tests). Diese können übersprungen werden, wenn Zeitdruck besteht.

### Dynamische Keys

Alle Berechnungsergebnisse und Daten sollten mit dynamischen Keys gespeichert werden für maximale Flexibilität.

### Testing

Auch wenn Unit Tests optional sind, sollte jede Funktion manuell getestet werden vor dem Merge.

### Dokumentation

Dokumentiere jeden neuen Modul und jede neue Funktion inline mit Docstrings.

---

## Geschätzter Gesamtaufwand

- **Phase 1 (MVP + Essentials):** 60-90 Stunden
- **Phase 2 (Erweiterte Funktionen):** 80-120 Stunden
- **Phase 3 (Optionale Funktionen):** 100-150 Stunden
- **Integration & Testing:** 20-30 Stunden

**Gesamt:** 260-390 Stunden (je nach gewählten Funktionen)

---

## Nächste Schritte

1. Wähle welche Phase(n) du implementieren möchtest
2. Beginne mit Task 1.1 (Datenbankstruktur)
3. Arbeite dich sequenziell durch die Tasks
4. Teste jede Funktion nach Fertigstellung
5. Dokumentiere Änderungen

**Bereit zum Start? Sag mir, mit welchem Task ich beginnen soll!**
