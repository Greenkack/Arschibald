# CRM System Enhancement - Requirements Document

## Introduction

Dieses Dokument definiert die Anforderungen für die umfassende Erweiterung und Optimierung des bestehenden CRM-Systems in der Solar-Angebotsapp. Das Ziel ist es, aus den vorhandenen CRM-Funktionen ein vollständig integriertes, professionelles Customer Relationship Management System zu entwickeln, das nahtlos mit allen anderen Bereichen der Anwendung (Bedarfsanalyse, Berechnungen, PDF-Erstellung) verknüpft ist.

### Aktuelle Situation (Analyse)

**Vorhandene CRM-Dateien:**

- `crm.py` - Basis-Kundenverwaltung mit Kunden- und Projektdaten
- `crm_dashboard_ui.py` - Dashboard mit Übersichten und KPIs
- `crm_pipeline_ui.py` - Sales Pipeline mit Lead-Management
- `crm_calendar_ui.py` - Kalender und Terminverwaltung

**Vorhandene Funktionen:**

- Kundenverwaltung (CRUD)
- Projektverwaltung pro Kunde
- Kundenakte mit Dokumenten-Upload
- Dashboard mit Geschäftsübersicht
- Sales Pipeline (Lead → Qualified → Proposal → Negotiation → Won/Lost)
- Kalender mit Terminverwaltung
- Basis-Verknüpfung: "Kunde in CRM speichern" Button

**Vorhandene Datenbankstruktur:**

- `customers` Tabelle (Kundendaten)
- `projects` Tabelle (Projektdaten)
- `customer_documents` Tabelle (Kundenakte)
- `crm_leads` Tabelle (Pipeline-Leads)
- `crm_appointments` Tabelle (Termine)

**Identifizierte Schwachstellen:**

1. Keine automatische Synchronisation zwischen Bedarfsanalyse und CRM
2. Keine Verknüpfung zwischen Berechnungsergebnissen und Kundenprojekten
3. Keine automatische PDF-Archivierung in Kundenakte
4. Keine E-Mail-Integration
5. Keine Aufgabenverwaltung
6. Keine Notizen-/Kommunikationshistorie
7. Keine Angebotsverfolgung
8. Keine automatischen Erinnerungen
9. Keine Reporting-Funktionen
10. Keine Export-/Import-Funktionen

## Requirements

### Requirement 1: Automatische Datenübernahme aus Bedarfsanalyse

**User Story:** Als Vertriebsmitarbeiter möchte ich, dass Kundendaten aus der Bedarfsanalyse automatisch ins CRM übernommen werden, damit ich keine Daten doppelt eingeben muss.

#### Acceptance Criteria

1. WHEN ein Benutzer in der Bedarfsanalyse (Tab A) Kundendaten eingibt THEN sollen diese Daten automatisch für die CRM-Übernahme vorbereitet werden
2. WHEN der Benutzer auf "Kunde in CRM speichern" klickt THEN sollen ALLE Felder (Name, Adresse, Kontaktdaten, Projektdetails) übernommen werden
3. WHEN bereits ein Kunde mit gleicher E-Mail existiert THEN soll der Benutzer gefragt werden, ob er aktualisieren oder neu anlegen möchte
4. WHEN die Übernahme erfolgreich ist THEN soll eine Bestätigung mit Link zum Kundenprofil angezeigt werden
5. IF Pflichtfelder fehlen THEN soll eine klare Fehlermeldung erscheinen mit Hinweis auf fehlende Daten

### Requirement 2: Berechnungsergebnisse mit Kundenprojekten verknüpfen

**User Story:** Als Vertriebsmitarbeiter möchte ich, dass alle Berechnungsergebnisse automatisch dem Kundenprojekt zugeordnet werden, damit ich die Historie aller Angebotsvarianten nachvollziehen kann.

#### Acceptance Criteria

1. WHEN eine Berechnung durchgeführt wird THEN sollen die Ergebnisse mit dynamischen Keys gespeichert werden
2. WHEN ein Kunde im CRM ausgewählt ist THEN sollen alle zugehörigen Berechnungen angezeigt werden
3. WHEN mehrere Berechnungsvarianten existieren THEN sollen diese vergleichbar dargestellt werden
4. WHEN eine Berechnung als "Hauptangebot" markiert wird THEN soll diese hervorgehoben werden
5. IF Berechnungen älter als 90 Tage sind THEN sollen diese als "archiviert" gekennzeichnet werden

### Requirement 3: Automatische PDF-Archivierung in Kundenakte

**User Story:** Als Vertriebsmitarbeiter möchte ich, dass alle generierten PDFs automatisch in der Kundenakte gespeichert werden, damit ich jederzeit Zugriff auf alle Dokumente habe.

#### Acceptance Criteria

1. WHEN ein PDF generiert wird THEN soll es automatisch in der Kundenakte des zugeordneten Kunden gespeichert werden
2. WHEN ein PDF gespeichert wird THEN soll es mit Metadaten (Datum, Typ, Version) versehen werden
3. WHEN mehrere PDF-Versionen existieren THEN sollen diese chronologisch sortiert angezeigt werden
4. WHEN ein PDF heruntergeladen wird THEN soll dies in der Aktivitätshistorie protokolliert werden
5. IF kein Kunde zugeordnet ist THEN soll der Benutzer vor der PDF-Generierung zur Kundenzuordnung aufgefordert werden

### Requirement 4: E-Mail-Integration

**User Story:** Als Vertriebsmitarbeiter möchte ich E-Mails direkt aus dem CRM versenden können, damit ich alle Kommunikation zentral verwalten kann.

#### Acceptance Criteria

1. WHEN ich einen Kunden öffne THEN soll ich eine E-Mail-Funktion sehen
2. WHEN ich eine E-Mail versende THEN soll diese in der Kommunikationshistorie gespeichert werden
3. WHEN ich ein PDF anhängen möchte THEN sollen alle Dokumente aus der Kundenakte zur Auswahl stehen
4. WHEN ich E-Mail-Vorlagen verwende THEN sollen Platzhalter automatisch mit Kundendaten gefüllt werden
5. IF die E-Mail-Konfiguration fehlt THEN soll eine klare Anleitung zur Einrichtung angezeigt werden

### Requirement 5: Aufgabenverwaltung (Task Management)

**User Story:** Als Vertriebsmitarbeiter möchte ich Aufgaben zu Kunden und Projekten erstellen können, damit ich nichts vergesse und meine Arbeit strukturieren kann.

#### Acceptance Criteria

1. WHEN ich eine Aufgabe erstelle THEN soll ich diese einem Kunden, Projekt oder Lead zuordnen können
2. WHEN eine Aufgabe fällig wird THEN soll ich eine Benachrichtigung erhalten
3. WHEN ich Aufgaben filtere THEN soll ich nach Status, Priorität, Fälligkeit und Zuordnung filtern können
4. WHEN eine Aufgabe erledigt wird THEN soll dies in der Aktivitätshistorie protokolliert werden
5. IF überfällige Aufgaben existieren THEN sollen diese im Dashboard rot hervorgehoben werden

### Requirement 6: Notizen und Kommunikationshistorie

**User Story:** Als Vertriebsmitarbeiter möchte ich alle Notizen und Kommunikationen zu einem Kunden chronologisch sehen, damit ich den Kontext jeder Interaktion verstehe.

#### Acceptance Criteria

1. WHEN ich eine Notiz erstelle THEN soll diese mit Zeitstempel und Benutzer gespeichert werden
2. WHEN ich die Kommunikationshistorie öffne THEN sollen alle Aktivitäten (Notizen, E-Mails, Anrufe, Termine) chronologisch angezeigt werden
3. WHEN ich nach Aktivitäten suche THEN soll eine Volltextsuche verfügbar sein
4. WHEN ich eine Aktivität als wichtig markiere THEN soll diese hervorgehoben werden
5. IF eine Aktivität länger als 30 Tage zurückliegt THEN soll sie als "archiviert" gekennzeichnet werden

### Requirement 7: Angebotsverfolgung (Offer Tracking)

**User Story:** Als Vertriebsmitarbeiter möchte ich den Status aller Angebote verfolgen können, damit ich rechtzeitig nachfassen kann.

#### Acceptance Criteria

1. WHEN ein Angebot erstellt wird THEN soll es automatisch in der Angebotsverfolgung erscheinen
2. WHEN ein Angebot versendet wird THEN soll der Status auf "Versendet" gesetzt werden
3. WHEN ein Angebot 7 Tage alt ist THEN soll eine Nachfass-Erinnerung erstellt werden
4. WHEN ein Angebot angenommen wird THEN soll der Lead-Status auf "Won" gesetzt werden
5. IF ein Angebot abgelehnt wird THEN soll der Ablehnungsgrund erfasst werden können

### Requirement 8: Automatische Erinnerungen und Follow-ups

**User Story:** Als Vertriebsmitarbeiter möchte ich automatische Erinnerungen für Follow-ups erhalten, damit ich keine Opportunities verpasse.

#### Acceptance Criteria

1. WHEN ein Lead erstellt wird THEN soll automatisch ein Follow-up nach 3 Tagen geplant werden
2. WHEN ein Angebot versendet wird THEN soll automatisch ein Follow-up nach 7 Tagen geplant werden
3. WHEN ein Termin stattfindet THEN soll automatisch ein Follow-up nach 1 Tag geplant werden
4. WHEN eine Erinnerung fällig wird THEN soll eine Benachrichtigung im Dashboard erscheinen
5. IF eine Erinnerung ignoriert wird THEN soll sie nach 2 Tagen erneut erscheinen

### Requirement 9: Erweiterte Reporting-Funktionen

**User Story:** Als Geschäftsführer möchte ich detaillierte Reports über Verkaufsaktivitäten, Conversion-Raten und Umsätze sehen, damit ich fundierte Entscheidungen treffen kann.

#### Acceptance Criteria

1. WHEN ich den Report-Bereich öffne THEN sollen vordefinierte Reports verfügbar sein
2. WHEN ich einen Report erstelle THEN soll ich Zeiträume, Filter und Gruppierungen wählen können
3. WHEN ich einen Report exportiere THEN sollen Excel, PDF und CSV als Formate verfügbar sein
4. WHEN ich einen Report speichere THEN soll ich ihn als Vorlage wiederverwenden können
5. IF keine Daten für einen Report vorhanden sind THEN soll eine hilfreiche Meldung erscheinen

### Requirement 10: Kunden-Segmentierung und Tags

**User Story:** Als Vertriebsmitarbeiter möchte ich Kunden mit Tags kategorisieren können, damit ich zielgerichtete Aktionen durchführen kann.

#### Acceptance Criteria

1. WHEN ich einen Kunden bearbeite THEN soll ich Tags hinzufügen können
2. WHEN ich nach Tags filtere THEN sollen alle Kunden mit diesem Tag angezeigt werden
3. WHEN ich Tags verwalte THEN soll ich Tags erstellen, umbenennen und löschen können
4. WHEN ich Massen-Aktionen durchführe THEN soll ich Kunden nach Tags auswählen können
5. IF ein Tag nicht mehr verwendet wird THEN soll eine Warnung vor dem Löschen erscheinen

### Requirement 11: Aktivitäts-Dashboard mit Echtzeit-Updates

**User Story:** Als Vertriebsmitarbeiter möchte ich ein Dashboard mit Echtzeit-Updates meiner Aktivitäten sehen, damit ich immer auf dem neuesten Stand bin.

#### Acceptance Criteria

1. WHEN das Dashboard geladen wird THEN sollen aktuelle KPIs angezeigt werden
2. WHEN eine neue Aktivität stattfindet THEN soll das Dashboard automatisch aktualisiert werden
3. WHEN ich KPIs anpasse THEN sollen meine Einstellungen gespeichert werden
4. WHEN ich Zeiträume ändere THEN sollen alle Widgets entsprechend aktualisiert werden
5. IF keine Aktivitäten vorhanden sind THEN sollen Onboarding-Tipps angezeigt werden

### Requirement 12: Kunden-Import/Export

**User Story:** Als Administrator möchte ich Kundendaten importieren und exportieren können, damit ich Daten aus anderen Systemen übernehmen oder sichern kann.

#### Acceptance Criteria

1. WHEN ich Kunden importiere THEN sollen CSV, Excel und vCard-Formate unterstützt werden
2. WHEN ich Kunden exportiere THEN sollen alle Felder inklusive Notizen exportiert werden
3. WHEN Duplikate beim Import erkannt werden THEN soll ich wählen können: Überspringen, Aktualisieren oder Duplizieren
4. WHEN der Import fehlschlägt THEN soll ein detaillierter Fehlerbericht angezeigt werden
5. IF Pflichtfelder beim Import fehlen THEN sollen Standardwerte verwendet oder Zeilen übersprungen werden

### Requirement 13: Anruf-Protokollierung

**User Story:** Als Vertriebsmitarbeiter möchte ich Telefonanrufe protokollieren können, damit ich die Kommunikationshistorie vollständig habe.

#### Acceptance Criteria

1. WHEN ich einen Anruf protokolliere THEN soll ich Datum, Dauer, Richtung und Notizen erfassen können
2. WHEN ich einen Anruf starte THEN soll automatisch ein Timer gestartet werden
3. WHEN ein Anruf beendet wird THEN soll ich direkt Notizen hinzufügen können
4. WHEN ich Anrufe filtere THEN soll ich nach eingehend/ausgehend und Datum filtern können
5. IF ein Kunde mehrere Telefonnummern hat THEN sollen alle zur Auswahl stehen

### Requirement 14: Dokument-Vorlagen-Management

**User Story:** Als Administrator möchte ich Dokument-Vorlagen verwalten können, damit alle Mitarbeiter einheitliche Dokumente verwenden.

#### Acceptance Criteria

1. WHEN ich eine Vorlage erstelle THEN soll ich Platzhalter für Kundendaten definieren können
2. WHEN ich eine Vorlage verwende THEN sollen alle Platzhalter automatisch ersetzt werden
3. WHEN ich Vorlagen verwalte THEN soll ich diese kategorisieren und versionieren können
4. WHEN eine Vorlage gelöscht wird THEN sollen bereits generierte Dokumente erhalten bleiben
5. IF eine Vorlage fehlerhaft ist THEN soll eine Validierung vor dem Speichern erfolgen

### Requirement 15: Kunden-Portal (optional)

**User Story:** Als Kunde möchte ich ein Portal haben, wo ich meine Angebote einsehen und Dokumente herunterladen kann, damit ich jederzeit Zugriff auf meine Unterlagen habe.

#### Acceptance Criteria

1. WHEN ein Kunde Zugang erhält THEN soll er per E-Mail eingeladen werden
2. WHEN ein Kunde sich anmeldet THEN soll er nur seine eigenen Daten sehen
3. WHEN neue Dokumente verfügbar sind THEN soll der Kunde benachrichtigt werden
4. WHEN ein Kunde Fragen hat THEN soll er Nachrichten an den Vertrieb senden können
5. IF ein Kunde sein Passwort vergisst THEN soll ein sicherer Reset-Prozess verfügbar sein

### Requirement 16: Geo-Mapping und Routenplanung

**User Story:** Als Außendienstmitarbeiter möchte ich Kunden auf einer Karte sehen und Routen planen können, damit ich meine Besuche effizient organisieren kann.

#### Acceptance Criteria

1. WHEN ich die Karten-Ansicht öffne THEN sollen alle Kunden mit Adressen als Marker angezeigt werden
2. WHEN ich einen Marker anklicke THEN sollen Kundendetails angezeigt werden
3. WHEN ich mehrere Kunden auswähle THEN soll eine optimierte Route berechnet werden
4. WHEN ich eine Route speichere THEN soll sie als Termin-Serie im Kalender erscheinen
5. IF eine Adresse nicht gefunden wird THEN soll eine manuelle Positionierung möglich sein

### Requirement 17: Verkaufschancen-Bewertung (Lead Scoring)

**User Story:** Als Vertriebsleiter möchte ich Leads automatisch bewerten lassen, damit mein Team sich auf die vielversprechendsten Opportunities konzentriert.

#### Acceptance Criteria

1. WHEN ein Lead erstellt wird THEN soll automatisch ein Score berechnet werden
2. WHEN Lead-Daten aktualisiert werden THEN soll der Score neu berechnet werden
3. WHEN ich Scoring-Regeln definiere THEN soll ich Gewichtungen für verschiedene Faktoren festlegen können
4. WHEN Leads sortiert werden THEN soll der Score als Sortierkriterium verfügbar sein
5. IF ein Lead einen hohen Score erreicht THEN soll eine Benachrichtigung an den Vertrieb gesendet werden

### Requirement 18: Automatische Datensicherung

**User Story:** Als Administrator möchte ich, dass CRM-Daten automatisch gesichert werden, damit keine Daten verloren gehen.

#### Acceptance Criteria

1. WHEN die Anwendung läuft THEN sollen täglich automatische Backups erstellt werden
2. WHEN ein Backup erstellt wird THEN soll es mit Zeitstempel versehen werden
3. WHEN ich Backups verwalte THEN soll ich alte Backups löschen können
4. WHEN ich ein Backup wiederherstelle THEN soll eine Bestätigung erforderlich sein
5. IF ein Backup fehlschlägt THEN soll eine E-Mail-Benachrichtigung versendet werden

### Requirement 19: Multi-User-Unterstützung mit Berechtigungen

**User Story:** Als Administrator möchte ich verschiedene Benutzerrollen mit unterschiedlichen Berechtigungen definieren können, damit sensible Daten geschützt sind.

#### Acceptance Criteria

1. WHEN ich einen Benutzer anlege THEN soll ich eine Rolle zuweisen können
2. WHEN ein Benutzer sich anmeldet THEN sollen nur erlaubte Funktionen sichtbar sein
3. WHEN ich Rollen verwalte THEN soll ich Berechtigungen granular festlegen können
4. WHEN ein Benutzer unerlaubte Aktionen versucht THEN soll eine Fehlermeldung erscheinen
5. IF ein Benutzer deaktiviert wird THEN sollen seine Daten erhalten bleiben

### Requirement 20: Integrierte Wissensdatenbank

**User Story:** Als Vertriebsmitarbeiter möchte ich Zugriff auf eine Wissensdatenbank mit FAQs und Best Practices haben, damit ich Kunden besser beraten kann.

#### Acceptance Criteria

1. WHEN ich die Wissensdatenbank öffne THEN sollen Artikel nach Kategorien sortiert sein
2. WHEN ich nach Artikeln suche THEN soll eine Volltextsuche verfügbar sein
3. WHEN ich einen Artikel teile THEN soll ich ihn per E-Mail an Kunden senden können
4. WHEN ich Artikel bewerte THEN sollen die hilfreichsten Artikel oben angezeigt werden
5. IF ein Artikel veraltet ist THEN soll eine Warnung angezeigt werden

### Requirement 21: Verkaufsziele und Forecasting

**User Story:** Als Vertriebsleiter möchte ich Verkaufsziele definieren und Forecasts erstellen können, damit ich die Zielerreichung überwachen kann.

#### Acceptance Criteria

1. WHEN ich Ziele definiere THEN soll ich diese pro Mitarbeiter, Team oder Gesamt festlegen können
2. WHEN ich Forecasts erstelle THEN sollen Pipeline-Daten automatisch berücksichtigt werden
3. WHEN ich Ziele überwache THEN soll der Fortschritt visuell dargestellt werden
4. WHEN Ziele erreicht werden THEN soll eine Erfolgsmeldung angezeigt werden
5. IF Ziele gefährdet sind THEN soll eine Warnung im Dashboard erscheinen

### Requirement 22: Kunden-Feedback und Zufriedenheitsumfragen

**User Story:** Als Geschäftsführer möchte ich Kundenfeedback systematisch erfassen können, damit ich die Servicequalität verbessern kann.

#### Acceptance Criteria

1. WHEN ein Projekt abgeschlossen wird THEN soll automatisch eine Feedback-Anfrage versendet werden
2. WHEN ein Kunde Feedback gibt THEN soll dies im CRM gespeichert werden
3. WHEN ich Feedback auswerte THEN sollen Durchschnittswerte und Trends angezeigt werden
4. WHEN negatives Feedback eingeht THEN soll eine Benachrichtigung an den Vertrieb gesendet werden
5. IF ein Kunde nicht antwortet THEN soll nach 7 Tagen eine Erinnerung versendet werden

### Requirement 23: Vertrags- und Garantieverwaltung

**User Story:** Als Vertriebsmitarbeiter möchte ich Verträge und Garantien verwalten können, damit ich Kunden bei Fragen schnell helfen kann.

#### Acceptance Criteria

1. WHEN ein Vertrag erstellt wird THEN sollen alle relevanten Daten erfasst werden
2. WHEN ein Vertrag ausläuft THEN soll eine Erinnerung 30 Tage vorher erscheinen
3. WHEN ich Garantien verwalte THEN soll ich Garantiezeiträume und -bedingungen hinterlegen können
4. WHEN ein Kunde eine Garantieanfrage stellt THEN sollen alle relevanten Dokumente sofort verfügbar sein
5. IF ein Vertrag verlängert wird THEN soll die Historie erhalten bleiben

### Requirement 24: Social Media Integration

**User Story:** Als Marketing-Manager möchte ich Social Media Aktivitäten mit CRM-Daten verknüpfen können, damit ich die Wirksamkeit von Kampagnen messen kann.

#### Acceptance Criteria

1. WHEN ein Lead aus Social Media kommt THEN soll die Quelle automatisch erfasst werden
2. WHEN ich Kampagnen auswerte THEN sollen Conversion-Raten nach Quelle angezeigt werden
3. WHEN ich Social Media Profile verknüpfe THEN sollen diese im Kundenprofil sichtbar sein
4. WHEN ich Posts teile THEN soll ich Kunden direkt aus dem CRM taggen können
5. IF eine Kampagne erfolgreich ist THEN sollen ähnliche Kunden vorgeschlagen werden

### Requirement 25: Mobile App (Progressive Web App)

**User Story:** Als Außendienstmitarbeiter möchte ich das CRM auch mobil nutzen können, damit ich unterwegs auf alle Daten zugreifen kann.

#### Acceptance Criteria

1. WHEN ich die App auf dem Smartphone öffne THEN soll sie responsiv und touch-optimiert sein
2. WHEN ich offline bin THEN sollen zumindest Lesezugriffe auf gecachte Daten möglich sein
3. WHEN ich wieder online bin THEN sollen Änderungen automatisch synchronisiert werden
4. WHEN ich Fotos mache THEN soll ich diese direkt zur Kundenakte hinzufügen können
5. IF die Verbindung instabil ist THEN soll eine Offline-Warnung angezeigt werden

## Prioritäten und Komplexität

Die 25 Funktionen werden im Design-Dokument nach Priorität, Komplexität und Abhängigkeiten bewertet.
