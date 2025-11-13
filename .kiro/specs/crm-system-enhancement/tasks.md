# CRM System Enhancement - Implementation Tasks

## Übersicht

Implementierungs-Tasks für das erweiterte CRM-System basierend auf 25 definierten Funktionen.

**Priorisierung:**
- Phase 1 (Kern-Funktionen): Tasks 1-8 - SOFORT umsetzen
- Phase 2 (Erweiterte Funktionen): Tasks 9-15 - Nach Phase 1
- Phase 3 (Optional): Tasks 16-21 - Nice-to-have

**Hinweis:** Tasks mit "*" am Ende sind optional und können übersprungen werden.

## Tasks

- [x] 1. Automatische Datenübernahme aus Bedarfsanalyse implementieren




  - Erstelle `crm/integration/data_input_bridge.py` Modul
  - Implementiere `extract_customer_data_from_session()` Funktion
  - Implementiere `extract_project_data_from_session()` Funktion
  - Implementiere `check_duplicate_customer(conn, email)` Funktion
  - Erweitere "Kunde in CRM speichern" Button in `gui.py`
  - Füge Vorschau-Dialog mit allen zu übernehmenden Daten hinzu
  - Implementiere Duplikat-Warnung mit Auswahloptionen
  - Füge Erfolgsbestätigung mit Link zum Kundenprofil hinzu
  - Implementiere Validierung für Pflichtfelder
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 Schreibe Unit Tests für Datenübernahme





  - Teste vollständige Datenextraktion
  - Teste Duplikatserkennung
  - Teste Fehlerbehandlung bei fehlenden Pflichtfeldern
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Berechnungsergebnisse mit Kundenprojekten verknüpfen





  - Erstelle neue Tabelle `project_calculations` in `database.py`
  - Implementiere `crm/integration/calculation_bridge.py` Modul
  - Implementiere `save_calculation_to_project()` Funktion mit JSON-Speicherung
  - Implementiere Versionierungs-Logik (v1, v2, v3...)
  - Implementiere `get_calculations_for_project()` Funktion
  - Implementiere `set_main_offer()` Funktion
  - Integriere in `calculations.py` nach erfolgreicher Berechnung
  - Integriere in `analysis.py` nach Analyse
  - Erstelle Berechnungs-Historie UI in `crm.py`
  - Implementiere Vergleichs-Ansicht für zwei Versionen
  - Füge "Als Hauptangebot markieren" Button hinzu
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.1 Schreibe Unit Tests für Berechnungsverknüpfung





  - Teste Speichern von Berechnungen
  - Teste Versionierung
  - Teste Vergleichs-Funktion
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. Automatische PDF-Archivierung in Kundenakte





  - Erstelle `crm/integration/pdf_bridge.py` Modul
  - Implementiere `auto_save_pdf_to_customer_documents()` Funktion
  - Nutze bestehende `add_customer_document()` aus `database.py`
  - Implementiere Metadaten-Extraktion (Typ, Version, Datum)
  - Implementiere automatische Versionsnummerierung
  - Integriere in `pdf_generator.py` nach PDF-Erstellung
  - Füge Kundenzuordnung-Dialog hinzu falls nicht vorhanden
  - Erweitere Kundenakte-UI um PDF-Typ und Version
  - Implementiere chronologische Sortierung
  - Füge Badges für PDF-Typ hinzu
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.1 Schreibe Tests für PDF-Archivierung





  - Teste automatisches Speichern
  - Teste Metadaten-Extraktion
  - Teste Versionierung
  - _Requirements: 3.1, 3.2_

- [x] 4. Aufgabenverwaltung (Task Management) implementieren





  - Erstelle neue Tabelle `crm_tasks` in `database.py`
  - Erstelle `crm/features/task_manager.py` Modul
  - Implementiere CRUD-Funktionen für Tasks
  - Implementiere Zuordnung zu Kunden, Projekten, Leads
  - Implementiere Status-Workflow (offen, in Arbeit, erledigt)
  - Implementiere Prioritäten (niedrig, mittel, hoch)
  - Erstelle Task-UI in Dashboard
  - Implementiere Filterung nach Status, Priorität, Fälligkeit
  - Füge Benachrichtigungen für fällige Tasks hinzu
  - Zeige überfällige Tasks rot hervorgehoben
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.1 Schreibe Tests für Task Management





  - Teste Task-Erstellung
  - Teste Status-Workflow
  - Teste Benachrichtigungen
  - _Requirements: 5.1, 5.2_

- [x] 5. Notizen und Kommunikationshistorie implementieren





  - Erstelle neue Tabelle `crm_activities` in `database.py`
  - Erstelle `crm/features/note_manager.py` Modul
  - Implementiere CRUD-Funktionen für Notizen
  - Implementiere Aktivitätstypen (Notiz, E-Mail, Anruf, Termin)
  - Erstelle Timeline-UI mit chronologischer Anzeige
  - Implementiere Volltextsuche (SQLite FTS5)
  - Füge "Als wichtig markieren" Funktion hinzu
  - Implementiere Filterung nach Aktivitätstyp und Datum
  - Zeige Archivierungs-Status für alte Aktivitäten
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_


- [x] 5.1 Schreibe Tests für Kommunikationshistorie



  - Teste Notiz-Erstellung
  - Teste Timeline-Anzeige
  - Teste Volltextsuche
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 6. Angebotsverfolgung (Offer Tracking) implementieren
  - Erweitere `projects` Tabelle um Angebots-Felder
  - Erstelle `crm/features/offer_tracker.py` Modul
  - Implementiere Status-Workflow (Entwurf, Versendet, Angenommen, Abgelehnt)
  - Implementiere automatische Status-Aktualisierung bei PDF-Versand
  - Erstelle Angebots-Übersicht UI
  - Implementiere Nachfass-Erinnerungen (7 Tage nach Versand)
  - Füge Ablehnungsgrund-Erfassung hinzu
  - Verknüpfe mit Lead-Status-Aktualisierung
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [ ] 6.1 Schreibe Tests für Angebotsverfolgung

  - Teste Status-Workflow
  - Teste automatische Erinnerungen
  - Teste Lead-Status-Verknüpfung
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 7. Automatische Erinnerungen und Follow-ups implementieren
  - Erstelle neue Tabelle `crm_reminders` in `database.py`
  - Erstelle `crm/utils/notification_manager.py` Modul
  - Implementiere Regel-Engine für automatische Erinnerungen
  - Implementiere Regel: Lead erstellt → Follow-up nach 3 Tagen
  - Implementiere Regel: Angebot versendet → Follow-up nach 7 Tagen
  - Implementiere Regel: Termin → Follow-up nach 1 Tag
  - Erstelle Dashboard-Widget für fällige Erinnerungen
  - Implementiere Snooze-Funktion (2 Tage)
  - Füge manuelle Erinnerungs-Erstellung hinzu
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


- [ ] 7.1 Schreibe Tests für Erinnerungssystem

  - Teste Regel-Engine
  - Teste automatische Erinnerungs-Erstellung
  - Teste Snooze-Funktion
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 8. Automatische Datensicherung implementieren
  - Erstelle `crm/utils/backup_scheduler.py` Modul
  - Nutze bestehende `backup_database()` Funktion
  - Implementiere APScheduler für automatische Backups
  - Implementiere tägliche Backups (2:00 Uhr)
  - Implementiere wöchentliche Backups (Sonntag 3:00 Uhr)
  - Implementiere monatliche Backups (1. des Monats)
  - Implementiere Backup-Rotation (7 täglich, 4 wöchentlich, 12 monatlich)
  - Erstelle Backup-Verwaltung UI im Admin-Panel
  - Implementiere manuelle Backup-Erstellung
  - Implementiere Wiederherstellungs-Funktion mit Bestätigung
  - _Requirements: 18.1, 18.2, 18.3, 18.4_


- [ ] 8.1 Schreibe Tests für Backup-System

  - Teste Backup-Erstellung
  - Teste Rotation
  - Teste Wiederherstellung
  - _Requirements: 18.1, 18.2, 18.3_

- [ ] 9. E-Mail-Integration implementieren
  - Erstelle `crm/features/email_manager.py` Modul
  - Implementiere SMTP-Konfiguration im Admin-Panel
  - Erstelle neue Tabellen `email_templates` und `email_history`
  - Implementiere E-Mail-Versand-Funktion mit SMTP
  - Erstelle Vorlagen-System mit Platzhaltern
  - Implementiere Platzhalter-Ersetzung ({{customer_name}}, etc.)
  - Füge E-Mail-Funktion zu Kundenprofil hinzu
  - Implementiere Anhang-Auswahl aus Kundenakte
  - Speichere versendete E-Mails in Kommunikationshistorie
  - Erstelle E-Mail-Vorlagen-Verwaltung
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_


- [ ] 9.1 Schreibe Tests für E-Mail-Integration

  - Teste E-Mail-Versand (Mock)
  - Teste Platzhalter-Ersetzung
  - Teste Vorlagen-System
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 10. Erweiterte Reporting-Funktionen implementieren
  - Erstelle `crm/features/reporting_engine.py` Modul
  - Implementiere vordefinierte Reports (Verkaufsübersicht, Conversion-Funnel, Lead-Quellen)
  - Erstelle Report-Builder mit Filtern und Gruppierungen
  - Implementiere Zeitraum-Auswahl (täglich, wöchentlich, monatlich)
  - Füge Visualisierungen mit Plotly hinzu
  - Implementiere Export-Funktionen (Excel, PDF, CSV)
  - Erstelle neue Tabelle `saved_reports` für Vorlagen
  - Implementiere Report-Vorlagen-Speicherung
  - Erstelle Reports-UI im Dashboard
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [ ] 10.1 Schreibe Tests für Reporting

  - Teste Report-Generierung
  - Teste Export-Funktionen
  - Teste Vorlagen-Speicherung
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 11. Kunden-Segmentierung und Tags implementieren
  - Erstelle neue Tabellen `crm_tags` und `customer_tags`
  - Erstelle Tag-Verwaltung im Admin-Panel
  - Implementiere Tag-CRUD-Funktionen
  - Füge Tag-Auswahl zu Kunden-Bearbeitung hinzu
  - Implementiere Tag-Filter in Kundenliste
  - Füge Farb-Coding für Tags hinzu
  - Implementiere Massen-Tagging-Funktion
  - Zeige Tag-Statistiken im Dashboard
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 11.1 Schreibe Tests für Tag-System

  - Teste Tag-Erstellung
  - Teste Tag-Zuordnung
  - Teste Filterung
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 12. Aktivitäts-Dashboard mit Echtzeit-Updates erweitern
  - Erweitere `crm_dashboard_ui.py`
  - Implementiere Widget-System für Dashboard
  - Erstelle Widget: Offene Aufgaben
  - Erstelle Widget: Anstehende Termine
  - Erstelle Widget: Pipeline-Übersicht
  - Erstelle Widget: Umsatz-Tracking
  - Implementiere Auto-Refresh-Funktion
  - Füge Widget-Konfiguration hinzu (Position, Sichtbarkeit)
  - Speichere Benutzer-Einstellungen
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 12.1 Schreibe Tests für Dashboard-Widgets

  - Teste Widget-Rendering
  - Teste Auto-Refresh
  - Teste Konfiguration
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 13. Kunden-Import/Export implementieren
  - Erstelle `crm/utils/import_export_manager.py` Modul
  - Implementiere CSV-Import mit Mapping-UI
  - Implementiere Excel-Import mit Sheet-Auswahl
  - Implementiere Duplikatserkennung beim Import
  - Füge Import-Vorschau hinzu
  - Implementiere Export aller Kundenfelder
  - Füge Export-Format-Auswahl hinzu (CSV, Excel)
  - Erstelle Import/Export-UI im Admin-Panel
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13.1 Schreibe Tests für Import/Export

  - Teste CSV-Import
  - Teste Excel-Import
  - Teste Duplikatserkennung
  - Teste Export
  - _Requirements: 12.1, 12.2, 12.3_

- [ ] 14. Dokument-Vorlagen-Management implementieren
  - Erstelle neue Tabelle `document_templates`
  - Erstelle `crm/features/template_manager.py` Modul
  - Implementiere Template-CRUD-Funktionen
  - Erstelle Template-Editor mit Platzhalter-System
  - Implementiere Platzhalter-Ersetzung
  - Füge Template-Kategorien hinzu (Angebot, Vertrag, Brief)
  - Implementiere Template-Versionierung
  - Erstelle Template-Vorschau-Funktion
  - Füge Template-Verwaltung im Admin-Panel hinzu
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 14.1 Schreibe Tests für Template-System

  - Teste Template-Erstellung
  - Teste Platzhalter-Ersetzung
  - Teste Versionierung
  - _Requirements: 14.1, 14.2, 14.3_

- [ ] 15. Lead Scoring implementieren
  - Erweitere `crm_leads` Tabelle um `score` Feld
  - Erstelle Scoring-Engine mit konfigurierbaren Regeln
  - Implementiere Scoring-Faktoren (Projektgröße, Lead-Quelle, Reaktionszeit, Engagement)
  - Füge Regel-Konfiguration im Admin-Panel hinzu
  - Implementiere automatische Score-Berechnung bei Lead-Änderungen
  - Füge Score-Visualisierung in Pipeline hinzu
  - Implementiere Benachrichtigungen bei hohem Score
  - Füge Score-basierte Sortierung hinzu
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_


- [ ] 15.1 Schreibe Tests für Lead Scoring

  - Teste Score-Berechnung
  - Teste Regel-Engine
  - Teste Benachrichtigungen
  - _Requirements: 17.1, 17.2, 17.3_

- [ ] 16. Anruf-Protokollierung implementieren
  - Erweitere `crm_activities` Tabelle um Anruf-Felder
  - Erstelle Anruf-Dialog mit Timer
  - Implementiere Telefonnummer-Auswahl
  - Füge Richtung (eingehend/ausgehend) hinzu
  - Implementiere Notizen-Feld für Anrufe
  - Integriere in Kommunikations-Timeline
  - Füge Anruf-Statistiken hinzu
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_


- [ ] 16.1 Schreibe Tests für Anruf-Protokollierung

  - Teste Anruf-Erstellung
  - Teste Timer-Funktion
  - Teste Timeline-Integration
  - _Requirements: 13.1, 13.2_

- [ ] 17. Wissensdatenbank implementieren
  - Erstelle neue Tabellen `kb_articles`, `kb_categories`, `kb_ratings`
  - Erstelle `crm/features/knowledge_base.py` Modul
  - Implementiere Artikel-CRUD-Funktionen
  - Erstelle Artikel-Editor mit Markdown-Unterstützung
  - Implementiere Kategorien-Hierarchie
  - Füge Volltextsuche hinzu (SQLite FTS5)
  - Implementiere Bewertungssystem
  - Erstelle E-Mail-Share-Funktion
  - Erstelle Wissensdatenbank-UI
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_


- [ ] 17.1 Schreibe Tests für Wissensdatenbank

  - Teste Artikel-Erstellung
  - Teste Suche
  - Teste Bewertungssystem
  - _Requirements: 20.1, 20.2, 20.3_

- [ ] 18. Verkaufsziele und Forecasting implementieren
  - Erstelle neue Tabellen `sales_targets` und `sales_forecasts`
  - Erstelle `crm/features/forecasting_engine.py` Modul
  - Implementiere Ziel-Definition (pro Mitarbeiter, Team, Gesamt)
  - Implementiere Zeiträume (monatlich, quartalsweise, jährlich)
  - Implementiere Forecast-Algorithmus basierend auf Pipeline
  - Füge Wahrscheinlichkeits-Gewichtung hinzu
  - Erstelle Visualisierungen (Ziel vs. Ist, Forecast-Trend)
  - Implementiere Zielerreichungs-Tracking
  - Füge Warnungen bei gefährdeten Zielen hinzu
  - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_

- [ ] 18.1 Schreibe Tests für Forecasting

  - Teste Ziel-Definition
  - Teste Forecast-Berechnung
  - Teste Visualisierungen
  - _Requirements: 21.1, 21.2, 21.3_

- [ ] 19. Kunden-Feedback und Zufriedenheitsumfragen implementieren
  - Erstelle neue Tabellen `feedback_surveys` und `feedback_responses`
  - Erstelle `crm/features/feedback_manager.py` Modul
  - Implementiere Umfrage-Builder mit verschiedenen Fragetypen
  - Implementiere Trigger-Konfiguration (Projekt abgeschlossen, etc.)
  - Implementiere automatischen E-Mail-Versand
  - Erstelle Auswertungs-Dashboard
  - Implementiere Trend-Analysen
  - Füge Negativ-Feedback-Alerts hinzu
  - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_

- [ ] 19.1 Schreibe Tests für Feedback-System

  - Teste Umfrage-Erstellung
  - Teste automatischen Versand
  - Teste Auswertung
  - _Requirements: 22.1, 22.2, 22.3_

- [ ] 20. Vertrags- und Garantieverwaltung implementieren
  - Erstelle neue Tabellen `contracts` und `warranties`
  - Erstelle `crm/features/contract_manager.py` Modul
  - Implementiere Vertrags-CRUD-Funktionen
  - Implementiere Garantie-CRUD-Funktionen
  - Füge Ablauf-Erinnerungen hinzu (30 Tage vorher)
  - Verknüpfe mit Dokumenten-System
  - Erstelle Vertrags-Übersicht UI
  - Füge Garantie-Tracking zu Projekten hinzu
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_


- [ ] 20.1 Schreibe Tests für Vertragsverwaltung

  - Teste Vertrags-Erstellung
  - Teste Ablauf-Erinnerungen
  - Teste Garantie-Tracking
  - _Requirements: 23.1, 23.2, 23.3_

- [ ] 21. Geo-Mapping und Routenplanung implementieren
  - Integriere Folium oder Plotly Maps
  - Implementiere Geocoding für Kundenadressen
  - Erstelle Karten-Ansicht mit Kunden-Markern
  - Füge Popup-Infos zu Markern hinzu
  - Implementiere Routenplanung-Algorithmus
  - Erstelle Routen-Optimierung für mehrere Kunden
  - Füge Routen-Export für Kalender hinzu
  - Erstelle Geo-Mapping-UI
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [ ] 21.1 Schreibe Tests für Geo-Mapping

  - Teste Geocoding
  - Teste Marker-Erstellung
  - Teste Routenplanung
  - _Requirements: 16.1, 16.2, 16.3_

## Zusammenfassung

**Phase 1 (Kern-Funktionen):** Tasks 1-8 (ca. 60-90 Stunden)
**Phase 2 (Erweiterte Funktionen):** Tasks 9-15 (ca. 80-120 Stunden)
**Phase 3 (Optional):** Tasks 16-21 (ca. 100-150 Stunden)

**Empfohlene Reihenfolge:**
1. Tasks 1, 3, 8 (Basis-Integration & Backups)
2. Tasks 2, 6 (Daten-Verknüpfung)
3. Tasks 4, 5 (Aktivitäts-Management)
4. Task 7 (Automatisierung)
5. Phase 2 nach Bedarf
