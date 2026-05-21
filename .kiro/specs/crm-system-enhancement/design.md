# CRM System Enhancement - Design Document

## Overview

Dieses Design-Dokument beschreibt die technische Umsetzung der 25 CRM-Funktionen. Jede Funktion wird bewertet nach:

- **Priorität** (Hoch/Mittel/Niedrig)
- **Komplexität** (Einfach/Mittel/Komplex)
- **Implementierungsaufwand** (Stunden)
- **Nutzen** (Hoch/Mittel/Niedrig)
- **Abhängigkeiten**
- **Kompatibilität** mit bestehendem System
- **Stabilität** (Risikobewertung)

## Architektur

### Bestehende Struktur

```
crm.py                  # Basis-CRUD für Kunden/Projekte
crm_dashboard_ui.py     # Dashboard mit KPIs
crm_pipeline_ui.py      # Sales Pipeline
crm_calendar_ui.py      # Terminverwaltung
database.py             # Datenbankzugriff
```

### Neue Module (geplant)

```
crm/
├── core/
│   ├── customer_manager.py      # Erweiterte Kundenverwaltung
│   ├── project_manager.py       # Erweiterte Projektverwaltung
│   └── activity_tracker.py      # Aktivitätsverfolgung
├── integration/
│   ├── data_input_bridge.py     # Brücke zur Bedarfsanalyse
│   ├── calculation_bridge.py    # Brücke zu Berechnungen
│   └── pdf_bridge.py            # Brücke zur PDF-Generierung
├── features/
│   ├── email_manager.py         # E-Mail-Integration
│   ├── task_manager.py          # Aufgabenverwaltung
│   ├── note_manager.py          # Notizen & Historie
│   └── offer_tracker.py         # Angebotsverfolgung
└── utils/
    ├── dynamic_keys.py          # Dynamische Keys für alle Daten
    └── notification_manager.py  # Benachrichtigungssystem
```

## Detaillierte Funktionsbewertung

### Funktion 1: Automatische Datenübernahme aus Bedarfsanalyse

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟢 EINFACH  
**Aufwand:** 4-6 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Diese Funktion ermöglicht die nahtlose Übernahme aller Kundendaten aus der Bedarfsanalyse (Tab A) ins CRM-System. Aktuell existiert bereits ein "Kunde in CRM speichern" Button, aber die Übernahme ist nicht vollständig.

**Vorteile:**

- ✅ Keine doppelte Dateneingabe mehr
- ✅ Zeitersparnis von ca. 5-10 Minuten pro Kunde
- ✅ Reduzierung von Tippfehlern
- ✅ Konsistente Datenqualität

**Implementierung:**

- Erweitere `data_input.py` um vollständige Datenextraktion
- Erstelle `crm/integration/data_input_bridge.py`
- Implementiere Duplikatserkennung via E-Mail
- Füge Bestätigungsdialog mit Vorschau hinzu

**Abhängigkeiten:**

- `data_input.py` (vorhanden)
- `crm.py` (vorhanden)
- `database.py` (vorhanden)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil (nutzt vorhandene Funktionen)

---

### Funktion 2: Berechnungsergebnisse mit Kundenprojekten verknüpfen

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 8-12 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Alle Berechnungsergebnisse aus `calculations.py` und `analysis.py` werden automatisch mit dem Kundenprojekt verknüpft und mit dynamischen Keys gespeichert. Dies ermöglicht Versionierung und Vergleich verschiedener Angebotsvarianten.

**Vorteile:**

- ✅ Vollständige Historie aller Berechnungen
- ✅ Vergleich verschiedener Angebotsvarianten
- ✅ Nachvollziehbarkeit für Kunden
- ✅ Basis für Reporting und Analysen

**Implementierung:**

- Erstelle neue Tabelle `project_calculations` mit JSON-Feld für dynamische Keys
- Implementiere `crm/integration/calculation_bridge.py`
- Füge Versionierung hinzu (v1, v2, v3...)
- Erstelle Vergleichs-UI in `crm.py`

**Abhängigkeiten:**

- `calculations.py` (vorhanden)
- `analysis.py` (vorhanden)
- Neue DB-Tabelle erforderlich

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil (isolierte neue Funktionalität)

---

### Funktion 3: Automatische PDF-Archivierung in Kundenakte

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟢 EINFACH  
**Aufwand:** 3-5 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Jedes generierte PDF wird automatisch in der Kundenakte gespeichert. Die Infrastruktur existiert bereits (`customer_documents` Tabelle), muss nur mit PDF-Generierung verknüpft werden.

**Vorteile:**

- ✅ Zentrale Dokumentenverwaltung
- ✅ Keine manuellen Uploads mehr nötig
- ✅ Automatische Versionierung
- ✅ Audit-Trail für alle Dokumente

**Implementierung:**

- Erweitere `pdf_generator.py` um Auto-Save-Funktion
- Nutze vorhandene `add_customer_document()` Funktion
- Füge Metadaten hinzu (PDF-Typ, Version, Datum)
- Implementiere `crm/integration/pdf_bridge.py`

**Abhängigkeiten:**

- `pdf_generator.py` (vorhanden)
- `database.py::add_customer_document()` (vorhanden)
- `customer_documents` Tabelle (vorhanden)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil (nutzt vorhandene Infrastruktur)

---

### Funktion 4: E-Mail-Integration

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🔴 KOMPLEX  
**Aufwand:** 20-30 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Vollständige E-Mail-Integration mit SMTP/IMAP, Vorlagen-System und Kommunikationshistorie.

**Vorteile:**

- ✅ Zentrale Kommunikationsverwaltung
- ✅ Automatische Dokumentation
- ✅ E-Mail-Vorlagen mit Platzhaltern
- ✅ Anhänge aus Kundenakte

**Implementierung:**

- Erstelle `crm/features/email_manager.py`
- Implementiere SMTP-Konfiguration in Admin-Panel
- Erstelle Vorlagen-System mit Platzhaltern
- Füge E-Mail-Historie zur Kommunikations-Timeline hinzu
- Neue Tabellen: `email_templates`, `email_history`

**Abhängigkeiten:**

- Python `smtplib` (Standard-Bibliothek)
- Neue DB-Tabellen erforderlich
- Admin-Panel für Konfiguration

**Kompatibilität:** ✅ Kompatibel (neue isolierte Funktion)  
**Stabilität:** ⚠️ Mittel (externe SMTP-Abhängigkeit)

**Schwierigkeitsgrad:** Mittel-Hoch (SMTP-Konfiguration kann komplex sein)

---

### Funktion 5: Aufgabenverwaltung (Task Management)

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 12-16 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Vollständiges Task-Management-System mit Zuordnung zu Kunden, Projekten und Leads.

**Vorteile:**

- ✅ Strukturierte Arbeitsorganisation
- ✅ Keine vergessenen Follow-ups
- ✅ Priorisierung von Aufgaben
- ✅ Team-Koordination

**Implementierung:**

- Erstelle `crm/features/task_manager.py`
- Neue Tabelle `crm_tasks` mit Feldern:
  - id, title, description, status, priority
  - due_date, assigned_to, customer_id, project_id, lead_id
  - created_at, completed_at
- Implementiere Task-UI in Dashboard
- Füge Benachrichtigungen für fällige Tasks hinzu

**Abhängigkeiten:**

- Neue DB-Tabelle erforderlich
- Benachrichtigungssystem (siehe Funktion 8)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil (isolierte neue Funktionalität)

**Schwierigkeitsgrad:** Mittel (Standard CRUD + Benachrichtigungen)

---

### Funktion 6: Notizen und Kommunikationshistorie

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 10-14 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Zentrale Timeline für alle Aktivitäten (Notizen, E-Mails, Anrufe, Termine) mit Volltextsuche.

**Vorteile:**

- ✅ Vollständiger Kontext jeder Kundeninteraktion
- ✅ Schnelle Informationsfindung
- ✅ Team-Transparenz
- ✅ Audit-Trail

**Implementierung:**

- Erstelle `crm/features/note_manager.py`
- Neue Tabelle `crm_activities` mit Feldern:
  - id, customer_id, activity_type, title, content
  - created_by, created_at, is_important
- Implementiere Timeline-UI mit Filterung
- Füge Volltextsuche hinzu (SQLite FTS5)

**Abhängigkeiten:**

- Neue DB-Tabelle erforderlich
- SQLite FTS5 für Volltextsuche

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil

**Schwierigkeitsgrad:** Mittel (Timeline-UI + Suche)

---

### Funktion 7: Angebotsverfolgung (Offer Tracking)

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 8-12 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Systematische Verfolgung aller Angebote mit Status-Tracking und automatischen Follow-up-Erinnerungen.

**Vorteile:**

- ✅ Kein Angebot geht verloren
- ✅ Automatische Nachfass-Erinnerungen
- ✅ Conversion-Rate-Tracking
- ✅ Ablehnungsgründe-Analyse

**Implementierung:**

- Erstelle `crm/features/offer_tracker.py`
- Erweitere `projects` Tabelle um Felder:
  - offer_status, offer_sent_date, offer_version
  - offer_value, offer_accepted_date, rejection_reason
- Implementiere Status-Workflow
- Füge automatische Erinnerungen hinzu (7 Tage nach Versand)

**Abhängigkeiten:**

- Bestehende `projects` Tabelle
- Benachrichtigungssystem (Funktion 8)
- PDF-Archivierung (Funktion 3)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Status-Workflow + Automatisierung)

---

### Funktion 8: Automatische Erinnerungen und Follow-ups

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 10-15 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Intelligentes Erinnerungssystem mit konfigurierbaren Regeln für verschiedene Ereignisse.

**Vorteile:**

- ✅ Keine verpassten Opportunities
- ✅ Systematisches Follow-up
- ✅ Erhöhte Conversion-Rate
- ✅ Professioneller Eindruck

**Implementierung:**

- Erstelle `crm/utils/notification_manager.py`
- Neue Tabelle `crm_reminders` mit Feldern:
  - id, reminder_type, related_id, due_date
  - status, message, created_at
- Implementiere Regel-Engine:
  - Lead erstellt → Follow-up nach 3 Tagen
  - Angebot versendet → Follow-up nach 7 Tagen
  - Termin → Follow-up nach 1 Tag
- Füge Dashboard-Widget für Erinnerungen hinzu

**Abhängigkeiten:**

- Neue DB-Tabelle erforderlich
- Hintergrund-Task-System (optional: APScheduler)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Regel-Engine + Scheduling)

---

### Funktion 9: Erweiterte Reporting-Funktionen

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🔴 KOMPLEX  
**Aufwand:** 25-35 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Umfassendes Reporting-System mit vordefinierten und benutzerdefinierten Reports, Export-Funktionen.

**Vorteile:**

- ✅ Datengetriebene Entscheidungen
- ✅ Performance-Tracking
- ✅ Trend-Analysen
- ✅ Export für externe Analysen

**Implementierung:**

- Erstelle `crm/features/reporting_engine.py`
- Implementiere vordefinierte Reports:
  - Verkaufsübersicht (täglich/wöchentlich/monatlich)
  - Conversion-Funnel
  - Lead-Quellen-Analyse
  - Mitarbeiter-Performance
- Füge Report-Builder hinzu (Filter, Gruppierung, Aggregation)
- Implementiere Export (Excel, PDF, CSV)
- Neue Tabelle `saved_reports` für Vorlagen

**Abhängigkeiten:**

- Pandas für Datenverarbeitung
- Plotly für Visualisierungen
- openpyxl für Excel-Export

**Kompatibilität:** ✅ Kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Hoch (komplexe Datenverarbeitung)

---

### Funktion 10: Kunden-Segmentierung und Tags

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟢 EINFACH  
**Aufwand:** 6-8 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Flexibles Tag-System zur Kategorisierung von Kunden für zielgerichtete Aktionen.

**Vorteile:**

- ✅ Flexible Kategorisierung
- ✅ Zielgruppen-Marketing
- ✅ Schnelle Filterung
- ✅ Massen-Aktionen

**Implementierung:**

- Neue Tabellen:
  - `crm_tags` (id, name, color, category)
  - `customer_tags` (customer_id, tag_id)
- Erweitere Kunden-UI um Tag-Management
- Implementiere Tag-Filter in Kundenliste
- Füge Massen-Tagging hinzu

**Abhängigkeiten:**

- Neue DB-Tabellen erforderlich

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil

**Schwierigkeitsgrad:** Einfach (Standard Many-to-Many Beziehung)

---

### Funktion 11: Aktivitäts-Dashboard mit Echtzeit-Updates

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 12-18 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Erweiterung des bestehenden Dashboards mit konfigurierbaren Widgets und Auto-Refresh.

**Vorteile:**

- ✅ Immer aktuelle Informationen
- ✅ Personalisierbare Ansicht
- ✅ Schneller Überblick
- ✅ Motivierende KPIs

**Implementierung:**

- Erweitere `crm_dashboard_ui.py`
- Implementiere Widget-System:
  - Offene Aufgaben
  - Anstehende Termine
  - Pipeline-Übersicht
  - Umsatz-Tracking
- Füge Auto-Refresh hinzu (Streamlit `st.rerun()`)
- Implementiere Widget-Konfiguration (Position, Größe, Sichtbarkeit)

**Abhängigkeiten:**

- Bestehende Dashboard-Infrastruktur
- Alle anderen CRM-Module für Daten

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Widget-System + State-Management)

---

### Funktion 12: Kunden-Import/Export

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 10-14 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Umfassende Import/Export-Funktionalität für Kundendaten mit Duplikatserkennung.

**Vorteile:**

- ✅ Migration aus anderen Systemen
- ✅ Datensicherung
- ✅ Bulk-Operations
- ✅ Datenanalyse in Excel

**Implementierung:**

- Erstelle `crm/utils/import_export_manager.py`
- Implementiere Import-Formate:
  - CSV (mit Mapping-UI)
  - Excel (mit Sheet-Auswahl)
  - vCard (für Kontakte)
- Implementiere Export mit allen Feldern
- Füge Duplikatserkennung hinzu (E-Mail, Name+PLZ)
- Erstelle Vorschau vor Import

**Abhängigkeiten:**

- Pandas für CSV/Excel
- vobject für vCard (optional)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Datenvalidierung + Duplikate)

---

### Funktion 13: Anruf-Protokollierung

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🟢 EINFACH  
**Aufwand:** 4-6 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Einfaches System zur Protokollierung von Telefonanrufen mit Timer und Notizen.

**Vorteile:**

- ✅ Vollständige Kommunikationshistorie
- ✅ Zeiterfassung
- ✅ Nachvollziehbarkeit
- ✅ Statistiken über Anrufaktivitäten

**Implementierung:**

- Erweitere `crm_activities` Tabelle um Anruf-Typ
- Füge Anruf-Dialog hinzu mit:
  - Telefonnummer-Auswahl
  - Timer (Start/Stop)
  - Richtung (eingehend/ausgehend)
  - Notizen-Feld
- Integriere in Kommunikations-Timeline

**Abhängigkeiten:**

- Kommunikationshistorie (Funktion 6)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil

**Schwierigkeitsgrad:** Einfach (Formular + Timer)

---

### Funktion 14: Dokument-Vorlagen-Management

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 12-16 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Verwaltungssystem für Dokument-Vorlagen mit Platzhalter-System.

**Vorteile:**

- ✅ Einheitliche Dokumente
- ✅ Zeitersparnis
- ✅ Professionelles Erscheinungsbild
- ✅ Versionskontrolle

**Implementierung:**

- Neue Tabelle `document_templates`:
  - id, name, category, content, placeholders
  - version, is_active, created_at
- Implementiere Platzhalter-System:
  - {{customer_name}}, {{project_value}}, etc.
- Erstelle Template-Editor mit Vorschau
- Füge Template-Kategorien hinzu (Angebot, Vertrag, Brief)

**Abhängigkeiten:**

- Jinja2 für Template-Rendering (optional)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Template-Engine + Editor)

---

### Funktion 15: Kunden-Portal (optional)

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🔴 SEHR KOMPLEX  
**Aufwand:** 40-60 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Separates Web-Portal für Kunden mit Login, Dokumentenzugriff und Messaging.

**Vorteile:**

- ✅ Kunden-Self-Service
- ✅ Reduzierte Support-Anfragen
- ✅ Moderne Customer Experience
- ✅ Dokumenten-Transparenz

**Implementierung:**

- Erstelle separate Flask/FastAPI-Anwendung
- Implementiere Authentifizierung (JWT)
- Neue Tabellen:
  - `customer_portal_users`
  - `customer_portal_sessions`
  - `customer_messages`
- Implementiere Features:
  - Login/Logout
  - Dokumenten-Download
  - Messaging
  - Profil-Verwaltung

**Abhängigkeiten:**

- Flask oder FastAPI
- JWT für Authentication
- Separate Deployment-Infrastruktur

**Kompatibilität:** ⚠️ Erfordert separate Anwendung  
**Stabilität:** ⚠️ Mittel (externe Abhängigkeiten)

**Schwierigkeitsgrad:** Sehr Hoch (separate Anwendung + Security)

**Empfehlung:** Erst in Phase 2, nach Kern-CRM-Funktionen

---

### Funktion 16: Geo-Mapping und Routenplanung

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🔴 KOMPLEX  
**Aufwand:** 20-30 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Kartenansicht aller Kunden mit Routenplanung für Außendienst.

**Vorteile:**

- ✅ Effiziente Besuchsplanung
- ✅ Visualisierung der Kundenverteilung
- ✅ Optimierte Routen
- ✅ Zeitersparnis im Außendienst

**Implementierung:**

- Integriere Folium oder Plotly Maps
- Implementiere Geocoding für Adressen (Google Maps API oder Nominatim)
- Füge Kunden-Marker mit Popup-Infos hinzu
- Implementiere Routenplanung (Google Directions API oder OSRM)
- Erstelle Routen-Export für Kalender

**Abhängigkeiten:**

- Folium oder Plotly für Karten
- Geocoding-API (Google oder OpenStreetMap)
- Routing-API (optional)

**Kompatibilität:** ✅ Kompatibel  
**Stabilität:** ⚠️ Mittel (externe API-Abhängigkeiten)

**Schwierigkeitsgrad:** Hoch (API-Integration + Routing-Algorithmen)

**Empfehlung:** Optional, erst nach Kern-Funktionen

---

### Funktion 17: Verkaufschancen-Bewertung (Lead Scoring)

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 12-18 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Automatisches Scoring-System für Leads basierend auf konfigurierbaren Regeln.

**Vorteile:**

- ✅ Priorisierung der besten Opportunities
- ✅ Effizientere Ressourcennutzung
- ✅ Höhere Conversion-Rate
- ✅ Datengetriebene Entscheidungen

**Implementierung:**

- Erweitere `crm_leads` Tabelle um `score` Feld
- Erstelle Scoring-Engine mit Regeln:
  - Projektgröße (Punkte nach Wert)
  - Lead-Quelle (Empfehlung = höher)
  - Reaktionszeit (schnell = höher)
  - Engagement (Anzahl Interaktionen)
- Implementiere Regel-Konfiguration im Admin-Panel
- Füge Score-Visualisierung in Pipeline hinzu
- Implementiere automatische Benachrichtigungen bei hohem Score

**Abhängigkeiten:**

- Bestehende Pipeline-Infrastruktur
- Admin-Panel für Konfiguration

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Scoring-Algorithmus + Konfiguration)

---

### Funktion 18: Automatische Datensicherung

**Priorität:** 🔴 HOCH  
**Komplexität:** 🟢 EINFACH  
**Aufwand:** 4-6 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Automatisches Backup-System für alle CRM-Daten mit Wiederherstellungsfunktion.

**Vorteile:**

- ✅ Datensicherheit
- ✅ Disaster Recovery
- ✅ Compliance-Anforderungen
- ✅ Seelenfrieden

**Implementierung:**

- Erweitere bestehende `backup_database()` Funktion
- Implementiere Scheduler (APScheduler):
  - Tägliche Backups um 2:00 Uhr
  - Wöchentliche Backups (Sonntag)
  - Monatliche Backups (1. des Monats)
- Füge Backup-Rotation hinzu (behalte letzte 7 täglich, 4 wöchentlich, 12 monatlich)
- Implementiere Wiederherstellungs-UI im Admin-Panel
- Füge E-Mail-Benachrichtigung bei Fehlern hinzu

**Abhängigkeiten:**

- APScheduler für Scheduling
- Bestehende `database.py::backup_database()`

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Sehr stabil

**Schwierigkeitsgrad:** Einfach (nutzt vorhandene Funktionen)

---

### Funktion 19: Multi-User-Unterstützung mit Berechtigungen

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🔴 KOMPLEX  
**Aufwand:** 30-40 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
Vollständiges Benutzer- und Rechteverwaltungssystem mit Rollen und Berechtigungen.

**Vorteile:**

- ✅ Datensicherheit
- ✅ Compliance (DSGVO)
- ✅ Team-Kollaboration
- ✅ Audit-Trail

**Implementierung:**

- Neue Tabellen:
  - `users` (id, username, email, password_hash, role_id)
  - `roles` (id, name, permissions_json)
  - `user_sessions` (id, user_id, token, expires_at)
- Implementiere Authentifizierung:
  - Login/Logout
  - Passwort-Hashing (bcrypt)
  - Session-Management
- Implementiere Autorisierung:
  - Rollen: Admin, Manager, Vertrieb, Viewer
  - Berechtigungen: create, read, update, delete (pro Modul)
- Füge Benutzer-Verwaltung im Admin-Panel hinzu
- Implementiere Audit-Log für alle Aktionen

**Abhängigkeiten:**

- bcrypt für Passwort-Hashing
- JWT oder Session-basierte Auth
- Streamlit Authenticator (optional)

**Kompatibilität:** ⚠️ Erfordert Umstrukturierung  
**Stabilität:** ⚠️ Mittel (Security-kritisch)

**Schwierigkeitsgrad:** Sehr Hoch (Security + Rechtesystem)

**Empfehlung:** Erst in Phase 2, nach Kern-Funktionen

---

### Funktion 20: Integrierte Wissensdatenbank

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 15-20 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Interne Wissensdatenbank mit FAQs, Best Practices und Produktinformationen.

**Vorteile:**

- ✅ Schnellere Kundenberatung
- ✅ Konsistente Informationen
- ✅ Onboarding neuer Mitarbeiter
- ✅ Self-Service für Team

**Implementierung:**

- Neue Tabellen:
  - `kb_articles` (id, title, content, category_id, tags)
  - `kb_categories` (id, name, parent_id)
  - `kb_ratings` (article_id, user_id, rating)
- Implementiere Artikel-Editor (Markdown)
- Füge Volltextsuche hinzu (SQLite FTS5)
- Implementiere Kategorien-Hierarchie
- Füge Bewertungssystem hinzu
- Erstelle E-Mail-Share-Funktion

**Abhängigkeiten:**

- Markdown-Renderer (streamlit-markdown)
- SQLite FTS5 für Suche

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Content-Management + Suche)

**Empfehlung:** Optional, Nice-to-have

---

### Funktion 21: Verkaufsziele und Forecasting

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🔴 KOMPLEX  
**Aufwand:** 20-30 Stunden  
**Nutzen:** 🔴 HOCH  

**Beschreibung:**
System zur Definition von Verkaufszielen und automatischer Forecast-Berechnung.

**Vorteile:**

- ✅ Zielverfolgung
- ✅ Prognosen für Planung
- ✅ Motivation des Teams
- ✅ Frühwarnsystem

**Implementierung:**

- Neue Tabellen:
  - `sales_targets` (id, user_id, period, target_value, target_type)
  - `sales_forecasts` (id, period, forecast_value, confidence)
- Implementiere Ziel-Definition:
  - Pro Mitarbeiter, Team, Gesamt
  - Monatlich, Quartalsweise, Jährlich
- Implementiere Forecast-Algorithmus:
  - Basierend auf Pipeline-Daten
  - Gewichtet nach Wahrscheinlichkeit
  - Historische Conversion-Raten
- Erstelle Visualisierungen:
  - Ziel vs. Ist
  - Forecast-Trend
  - Zielerreichungs-Wahrscheinlichkeit

**Abhängigkeiten:**

- Pipeline-Daten
- Historische Verkaufsdaten
- Plotly für Visualisierungen

**Kompatibilität:** ✅ Kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Hoch (Forecast-Algorithmen + Visualisierung)

---

### Funktion 22: Kunden-Feedback und Zufriedenheitsumfragen

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 12-18 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
System zur Erfassung und Auswertung von Kundenfeedback mit automatischen Umfragen.

**Vorteile:**

- ✅ Kundenzufriedenheit messen
- ✅ Verbesserungspotenziale erkennen
- ✅ Testimonials sammeln
- ✅ Frühwarnung bei Problemen

**Implementierung:**

- Neue Tabellen:
  - `feedback_surveys` (id, name, questions_json, trigger_event)
  - `feedback_responses` (id, survey_id, customer_id, responses_json, rating)
- Implementiere Umfrage-Builder:
  - Verschiedene Fragetypen (Rating, Text, Multiple Choice)
  - Trigger-Konfiguration (Projekt abgeschlossen, 30 Tage nach Installation)
- Implementiere automatischen Versand (E-Mail)
- Erstelle Auswertungs-Dashboard:
  - Durchschnittliche Bewertungen
  - Trend-Analysen
  - Negativ-Feedback-Alerts

**Abhängigkeiten:**

- E-Mail-System (Funktion 4)
- Benachrichtigungssystem (Funktion 8)

**Kompatibilität:** ✅ Kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Umfrage-System + Auswertung)

---

### Funktion 23: Vertrags- und Garantieverwaltung

**Priorität:** 🟡 MITTEL  
**Komplexität:** 🟡 MITTEL  
**Aufwand:** 10-15 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Verwaltung von Verträgen und Garantien mit automatischen Ablauf-Erinnerungen.

**Vorteile:**

- ✅ Zentrale Vertragsverwaltung
- ✅ Keine verpassten Verlängerungen
- ✅ Schneller Zugriff bei Anfragen
- ✅ Garantie-Tracking

**Implementierung:**

- Neue Tabellen:
  - `contracts` (id, customer_id, contract_type, start_date, end_date, value, document_id)
  - `warranties` (id, project_id, warranty_type, start_date, duration_months, terms)
- Implementiere Vertrags-CRUD
- Füge Ablauf-Erinnerungen hinzu (30 Tage vorher)
- Verknüpfe mit Dokumenten-System
- Erstelle Übersichts-Dashboard

**Abhängigkeiten:**

- Dokumenten-System (vorhanden)
- Benachrichtigungssystem (Funktion 8)

**Kompatibilität:** ✅ Vollständig kompatibel  
**Stabilität:** ✅ Stabil

**Schwierigkeitsgrad:** Mittel (Standard CRUD + Erinnerungen)

---

### Funktion 24: Social Media Integration

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🔴 SEHR KOMPLEX  
**Aufwand:** 30-50 Stunden  
**Nutzen:** 🟢 NIEDRIG  

**Beschreibung:**
Integration mit Social Media Plattformen zur Verfolgung von Lead-Quellen und Kampagnen.

**Vorteile:**

- ✅ Lead-Quellen-Tracking
- ✅ Kampagnen-ROI-Messung
- ✅ Social Selling
- ✅ Erweiterte Kundenprofile

**Implementierung:**

- Integriere Social Media APIs:
  - Facebook/Instagram (Meta Business API)
  - LinkedIn (LinkedIn API)
  - Twitter/X (Twitter API)
- Neue Tabellen:
  - `social_profiles` (customer_id, platform, profile_url)
  - `social_campaigns` (id, platform, campaign_id, metrics_json)
- Implementiere Lead-Tracking mit UTM-Parametern
- Erstelle Kampagnen-Dashboard
- Füge Social-Profile zu Kundenprofil hinzu

**Abhängigkeiten:**

- API-Keys für alle Plattformen
- OAuth-Implementierung
- Externe API-Limits

**Kompatibilität:** ⚠️ Externe Abhängigkeiten  
**Stabilität:** ⚠️ Niedrig (API-Änderungen, Rate-Limits)

**Schwierigkeitsgrad:** Sehr Hoch (Multiple APIs + OAuth)

**Empfehlung:** NICHT empfohlen - zu komplex, geringer Nutzen für Solar-Business

---

### Funktion 25: Mobile App (Progressive Web App)

**Priorität:** 🟢 NIEDRIG  
**Komplexität:** 🔴 SEHR KOMPLEX  
**Aufwand:** 60-100 Stunden  
**Nutzen:** 🟡 MITTEL  

**Beschreibung:**
Progressive Web App für mobilen Zugriff auf CRM-Funktionen mit Offline-Unterstützung.

**Vorteile:**

- ✅ Mobiler Zugriff
- ✅ Offline-Funktionalität
- ✅ Foto-Upload vor Ort
- ✅ Moderne User Experience

**Implementierung:**

- Erstelle separate PWA mit React oder Vue.js
- Implementiere Service Worker für Offline-Funktionalität
- Implementiere API-Backend (REST oder GraphQL)
- Implementiere Synchronisations-Mechanismus
- Füge Kamera-Integration hinzu
- Implementiere Touch-optimierte UI
- Erstelle App-Manifest für Installation

**Abhängigkeiten:**

- Separate Frontend-Technologie (React/Vue)
- API-Backend (FastAPI/Flask)
- Service Worker
- IndexedDB für Offline-Daten

**Kompatibilität:** ⚠️ Erfordert separate Anwendung  
**Stabilität:** ⚠️ Mittel (Offline-Sync komplex)

**Schwierigkeitsgrad:** Sehr Hoch (Separate App + Offline-Sync)

**Empfehlung:** Erst in Phase 3, nach vollständigem Desktop-CRM

---

## Zusammenfassung und Empfehlungen

### Prioritäts-Matrix

#### Phase 1: Kern-Funktionen (SOFORT umsetzen)

**Geschätzter Gesamtaufwand: 60-90 Stunden**

1. ✅ **Funktion 1**: Automatische Datenübernahme (4-6h) - KRITISCH
2. ✅ **Funktion 2**: Berechnungsergebnisse verknüpfen (8-12h) - KRITISCH
3. ✅ **Funktion 3**: PDF-Archivierung (3-5h) - KRITISCH
4. ✅ **Funktion 5**: Aufgabenverwaltung (12-16h) - SEHR WICHTIG
5. ✅ **Funktion 6**: Notizen & Historie (10-14h) - SEHR WICHTIG
6. ✅ **Funktion 7**: Angebotsverfolgung (8-12h) - SEHR WICHTIG
7. ✅ **Funktion 8**: Automatische Erinnerungen (10-15h) - SEHR WICHTIG
8. ✅ **Funktion 18**: Automatische Backups (4-6h) - KRITISCH

**Nutzen:** Diese Funktionen bilden das Fundament eines professionellen CRM-Systems und lösen die dringendsten Probleme.

#### Phase 2: Erweiterte Funktionen (Nach Phase 1)

**Geschätzter Gesamtaufwand: 80-120 Stunden**

9. ✅ **Funktion 4**: E-Mail-Integration (20-30h)
10. ✅ **Funktion 9**: Erweiterte Reports (25-35h)
11. ✅ **Funktion 10**: Kunden-Segmentierung (6-8h)
12. ✅ **Funktion 11**: Aktivitäts-Dashboard (12-18h)
13. ✅ **Funktion 12**: Import/Export (10-14h)
14. ✅ **Funktion 14**: Dokument-Vorlagen (12-16h)
15. ✅ **Funktion 17**: Lead Scoring (12-18h)

**Nutzen:** Diese Funktionen erhöhen die Effizienz und bieten erweiterte Analyse-Möglichkeiten.

#### Phase 3: Nice-to-Have (Optional)

**Geschätzter Gesamtaufwand: 100-150 Stunden**

16. ⚠️ **Funktion 13**: Anruf-Protokollierung (4-6h)
17. ⚠️ **Funktion 20**: Wissensdatenbank (15-20h)
18. ⚠️ **Funktion 21**: Verkaufsziele & Forecasting (20-30h)
19. ⚠️ **Funktion 22**: Kunden-Feedback (12-18h)
20. ⚠️ **Funktion 23**: Vertrags-Verwaltung (10-15h)
21. ⚠️ **Funktion 16**: Geo-Mapping (20-30h)

**Nutzen:** Diese Funktionen bieten zusätzlichen Komfort, sind aber nicht kritisch.

#### NICHT EMPFOHLEN (zu komplex, geringer ROI)

22. ❌ **Funktion 15**: Kunden-Portal (40-60h) - Separate Anwendung
23. ❌ **Funktion 19**: Multi-User-System (30-40h) - Zu komplex für aktuellen Stand
24. ❌ **Funktion 24**: Social Media Integration (30-50h) - Geringer Nutzen
25. ❌ **Funktion 25**: Mobile App (60-100h) - Separate Anwendung

---

## Technische Architektur

### Datenbank-Schema (Erweiterungen)

```sql
-- Neue Tabellen für Phase 1

CREATE TABLE project_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    calculation_data JSON NOT NULL,
    dynamic_keys JSON NOT NULL,
    is_main_offer BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

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
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (lead_id) REFERENCES crm_leads(id)
);

CREATE TABLE crm_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_important BOOLEAN DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE crm_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_type TEXT NOT NULL,
    related_id INTEGER,
    related_type TEXT,
    due_date TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Erweiterungen bestehender Tabellen

ALTER TABLE projects ADD COLUMN offer_status TEXT DEFAULT 'draft';
ALTER TABLE projects ADD COLUMN offer_sent_date DATE;
ALTER TABLE projects ADD COLUMN offer_version INTEGER DEFAULT 1;
ALTER TABLE projects ADD COLUMN offer_value REAL;
ALTER TABLE projects ADD COLUMN offer_accepted_date DATE;
ALTER TABLE projects ADD COLUMN rejection_reason TEXT;
```

### Dynamische Keys Struktur

Alle Berechnungsergebnisse werden mit dynamischen Keys gespeichert:

```python
{
    "SYSTEM_SIZE_KWP": 15.0,
    "ANNUAL_PRODUCTION_KWH": 14250,
    "INVESTMENT_TOTAL_EUR": 25000,
    "PAYBACK_PERIOD_YEARS": 12.5,
    "MODULE_MANUFACTURER": "Trina Solar",
    "MODULE_MODEL": "Vertex S 500W",
    "INVERTER_MANUFACTURER": "Fronius",
    "INVERTER_MODEL": "Symo 15.0-3-M",
    # ... alle weiteren Berechnungswerte
}
```

Diese Keys können dann überall verwendet werden:

- In PDF-Vorlagen
- In E-Mail-Vorlagen
- In Reports
- In der UI

---

## Implementierungs-Reihenfolge (Empfehlung)

### Woche 1-2: Basis-Integration

1. Funktion 1: Datenübernahme (6h)
2. Funktion 3: PDF-Archivierung (5h)
3. Funktion 18: Backups (6h)

### Woche 3-4: Daten-Verknüpfung

4. Funktion 2: Berechnungen verknüpfen (12h)
5. Funktion 7: Angebotsverfolgung (12h)

### Woche 5-6: Aktivitäts-Management

6. Funktion 6: Notizen & Historie (14h)
7. Funktion 5: Aufgabenverwaltung (16h)

### Woche 7-8: Automatisierung

8. Funktion 8: Erinnerungen (15h)

**Gesamt Phase 1: 86 Stunden ≈ 2 Monate bei Teilzeit**

---

## Risiken und Mitigation

### Technische Risiken

1. **Datenbank-Migration**
   - Risiko: Datenverlust bei Schema-Änderungen
   - Mitigation: Automatische Backups vor jeder Migration

2. **Performance bei großen Datenmengen**
   - Risiko: Langsame Queries bei vielen Kunden
   - Mitigation: Indizes auf häufig genutzte Felder, Pagination

3. **Streamlit Session State**
   - Risiko: Datenverlust bei Rerun
   - Mitigation: Persistierung in DB, nicht nur in Session State

### Funktionale Risiken

1. **Komplexität für Benutzer**
   - Risiko: Überforderung durch zu viele Funktionen
   - Mitigation: Schrittweise Einführung, gute Dokumentation

2. **Datenqualität**
   - Risiko: Inkonsistente oder fehlerhafte Daten
   - Mitigation: Validierung, Pflichtfelder, Duplikatserkennung

---

## Erfolgs-Metriken

Nach Implementierung sollten folgende Verbesserungen messbar sein:

1. **Zeitersparnis**: 30-40% weniger Zeit für administrative Aufgaben
2. **Datenqualität**: 95%+ vollständige Kundenprofile
3. **Follow-up-Rate**: 80%+ aller Angebote werden nachgefasst
4. **Conversion-Rate**: 10-15% Steigerung durch besseres Lead-Management
5. **Kundenzufriedenheit**: Messbar durch Feedback-System
