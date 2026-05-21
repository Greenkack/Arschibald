# Requirements Document

## Introduction

Das Employee Controlling System ist ein umfassendes Modul zur Verwaltung, Auswertung und Analyse von Mitarbeiterleistungen, das in die bestehende Streamlit Python App integriert wird. Das Modul wird im Hauptmenü/Sidemenu unter dem Bereich "Controlling" zugänglich sein. Ein separater "Controlling Einstellungen" Bereich wird im Admin-Panel bereitgestellt. Das System ermöglicht die Erfassung von Mitarbeiterdaten, die Definition von Positionen und Auswertungskriterien, sowie die Erstellung detaillierter Leistungsberichte mit verschiedenen Zeiträumen (täglich, wöchentlich, monatlich, quartalsweise, jährlich und seit Arbeitsbeginn). Alle Daten werden in Datenbanken gespeichert und können jederzeit exportiert, archiviert und abgerufen werden.

## Glossary

- **System**: Das Employee Controlling System
- **Streamlit-App**: Die bestehende Streamlit Python Anwendung
- **Hauptmenü/Sidemenu**: Navigationsbereich der Streamlit-App
- **Controlling-Bereich**: Menüpunkt im Hauptmenü/Sidemenu für Mitarbeiterauswertungen
- **Admin-Panel**: Administrationsbereich der Streamlit-App
- **Controlling-Einstellungen**: Separater Bereich im Admin-Panel für Controlling-Konfiguration
- **Admin**: Benutzer mit administrativen Rechten
- **Mitarbeiter**: Angestellte Person, die im System erfasst und ausgewertet wird
- **Position**: Rolle oder Funktion eines Mitarbeiters in der Firma
- **Auswertungskriterium**: Messbarer Leistungsindikator für eine bestimmte Position
- **Quote**: Prozentuale Auswertung basierend auf Auswertungskriterien
- **Bericht**: Zusammenfassung von Auswertungen für einen bestimmten Zeitraum
- **Controlling-UI**: Benutzeroberfläche für die Mitarbeiterauswertung im Controlling-Bereich
- **Zeitraum**: Definierter Zeitabschnitt für Auswertungen (täglich, wöchentlich, monatlich, quartalsweise, jährlich, seit Arbeitsbeginn)

## Requirements

### Requirement 1

**User Story:** Als Benutzer möchte ich auf das Controlling-Modul über das Hauptmenü/Sidemenu zugreifen, so dass ich die Controlling-Funktionen in der Streamlit-App nutzen kann.

#### Acceptance Criteria

1. WHEN die Streamlit-App geladen wird, THEN THE System SHALL einen Menüpunkt "Controlling" im Hauptmenü/Sidemenu anzeigen
2. WHEN ein Benutzer auf den Menüpunkt "Controlling" klickt, THEN THE System SHALL die Controlling-UI anzeigen
3. WHEN ein Admin auf das Admin-Panel zugreift, THEN THE System SHALL einen separaten Bereich "Controlling Einstellungen" anzeigen
4. WHEN ein Admin auf "Controlling Einstellungen" klickt, THEN THE System SHALL den Konfigurationsbereich für Positionen und Auswertungskriterien anzeigen
5. THE System SHALL das Streamlit shadcn/ui Design für alle Controlling-Komponenten verwenden

### Requirement 2

**User Story:** Als Admin möchte ich Mitarbeiter mit vollständigen Stammdaten anlegen, so dass ich alle relevanten Informationen für die Auswertung erfasse.

#### Acceptance Criteria

1. WHEN ein Admin einen neuen Mitarbeiter anlegt, THEN THE System SHALL die Felder Vorname, Nachname, Wohnort, Geburtsdatum, Position und Arbeitsbeginndatum erfassen
2. WHEN ein Geburtsdatum eingegeben wird, THEN THE System SHALL das aktuelle Alter automatisch berechnen und anzeigen
3. WHEN ein Arbeitsbeginndatum eingegeben wird, THEN THE System SHALL die Anzahl der gearbeiteten Tage bis zum aktuellen Datum automatisch berechnen und anzeigen
4. THE System SHALL eine unbegrenzte Anzahl von Mitarbeitern unterstützen
5. WHEN Mitarbeiterdaten gespeichert werden, THEN THE System SHALL diese in einer Datenbank persistent speichern

### Requirement 3

**User Story:** Als Admin möchte ich Mitarbeiterdaten bearbeiten und verwalten, so dass ich Änderungen nachvollziehen und aktualisieren kann.

#### Acceptance Criteria

1. WHEN ein Admin einen Mitarbeiter auswählt, THEN THE System SHALL alle gespeicherten Daten des Mitarbeiters anzeigen
2. WHEN ein Admin Mitarbeiterdaten ändert, THEN THE System SHALL die Änderungen in der Datenbank aktualisieren
3. WHEN ein Admin einen Mitarbeiter löscht, THEN THE System SHALL alle zugehörigen Daten archivieren und aus der aktiven Liste entfernen
4. THE System SHALL eine Suchfunktion für Mitarbeiter bereitstellen
5. THE System SHALL eine Filterfunktion nach Position, Name oder anderen Kriterien bereitstellen

### Requirement 4

**User Story:** Als Admin möchte ich Positionen definieren und verwalten, so dass ich verschiedene Rollen in der Firma abbilden kann.

#### Acceptance Criteria

1. WHEN ein Admin eine neue Position erstellt, THEN THE System SHALL einen eindeutigen Positionsnamen erfassen
2. WHEN ein Admin eine Position bearbeitet, THEN THE System SHALL die Änderungen in der Datenbank speichern
3. WHEN ein Admin eine Position löscht, THEN THE System SHALL prüfen ob Mitarbeiter dieser Position zugeordnet sind und eine Warnung anzeigen
4. THE System SHALL eine unbegrenzte Anzahl von Positionen unterstützen
5. WHEN eine Position gelöscht wird und Mitarbeiter zugeordnet sind, THEN THE System SHALL die Löschung verhindern oder eine Neuzuordnung verlangen

### Requirement 5

**User Story:** Als Admin möchte ich Auswertungskriterien definieren und verwalten, so dass ich verschiedene Leistungsindikatoren erfassen kann.

#### Acceptance Criteria

1. WHEN ein Admin ein neues Auswertungskriterium erstellt, THEN THE System SHALL einen eindeutigen Namen und eine Beschreibung erfassen
2. THE System SHALL die folgenden Standard-Auswertungskriterien bereitstellen: Kunden terminiert, QC bestanden, storniert/kein Interesse, nicht erreicht/neu terminieren, technisch nicht machbar, angefahrene Termine, nicht angefahrene Termine, Verkauf, Folgetermin gemacht, zu teuer gewesen, Angebot erhalten, getätigte Anrufe gesamt, angefahrene Termine gesamt, sonstiges
3. WHEN ein Admin ein Auswertungskriterium bearbeitet, THEN THE System SHALL die Änderungen in der Datenbank speichern
4. WHEN ein Admin ein Auswertungskriterium löscht, THEN THE System SHALL prüfen ob es Positionen zugeordnet ist und eine Warnung anzeigen
5. THE System SHALL die Möglichkeit bieten, weitere benutzerdefinierte Auswertungskriterien hinzuzufügen

### Requirement 6

**User Story:** Als Admin möchte ich Auswertungskriterien bestimmten Positionen zuordnen, so dass jede Position die relevanten Leistungsindikatoren hat.

#### Acceptance Criteria

1. WHEN ein Admin eine Position auswählt, THEN THE System SHALL alle verfügbaren Auswertungskriterien anzeigen
2. WHEN ein Admin Auswertungskriterien einer Position zuordnet, THEN THE System SHALL die Zuordnung in der Datenbank speichern
3. WHEN ein Admin Auswertungskriterien von einer Position entfernt, THEN THE System SHALL die Zuordnung in der Datenbank löschen
4. THE System SHALL mehrere Auswertungskriterien pro Position unterstützen
5. WHEN ein Mitarbeiter einer Position zugeordnet ist, THEN THE System SHALL automatisch die zugeordneten Auswertungskriterien für diesen Mitarbeiter aktivieren

### Requirement 7

**User Story:** Als Admin möchte ich auf einen passwortgeschützten Controlling-Einstellungsbereich zugreifen, so dass nur autorisierte Personen Konfigurationen vornehmen können.

#### Acceptance Criteria

1. WHEN ein Benutzer auf den Controlling-Einstellungsbereich zugreift, THEN THE System SHALL eine Passwortabfrage anzeigen
2. WHEN ein Admin das korrekte Passwort eingibt, THEN THE System SHALL Zugriff auf die Controlling-Einstellungen gewähren
3. WHEN ein Benutzer ein falsches Passwort eingibt, THEN THE System SHALL den Zugriff verweigern und eine Fehlermeldung anzeigen
4. THE System SHALL nur Benutzern mit Admin-Rechten Zugriff auf die Controlling-Einstellungen gewähren
5. WHEN ein Admin die Controlling-Einstellungen verlässt, THEN THE System SHALL die Sitzung beenden

### Requirement 8

**User Story:** Als Benutzer möchte ich Leistungsdaten für Mitarbeiter manuell erfassen, so dass ich tägliche Tätigkeiten dokumentieren kann.

#### Acceptance Criteria

1. WHEN ein Benutzer einen Mitarbeiter auswählt, THEN THE System SHALL alle zugeordneten Auswertungskriterien anzeigen
2. WHEN ein Benutzer Werte für Auswertungskriterien eingibt, THEN THE System SHALL numerische Eingaben validieren
3. WHEN ein Benutzer Leistungsdaten speichert, THEN THE System SHALL die Daten mit Zeitstempel in der Datenbank speichern
4. THE System SHALL die Eingabe von Leistungsdaten für verschiedene Zeiträume ermöglichen
5. WHEN Leistungsdaten gespeichert werden, THEN THE System SHALL diese dem entsprechenden Mitarbeiter und Datum zuordnen

### Requirement 9

**User Story:** Als Benutzer möchte ich Auswertungen für verschiedene Zeiträume erstellen, so dass ich Leistungstrends analysieren kann.

#### Acceptance Criteria

1. WHEN ein Benutzer eine Auswertung startet, THEN THE System SHALL die Auswahl zwischen täglich, wöchentlich, monatlich, quartalsweise, jährlich und seit Arbeitsbeginn ermöglichen
2. WHEN ein Zeitraum ausgewählt wird, THEN THE System SHALL alle relevanten Leistungsdaten für diesen Zeitraum aus der Datenbank abrufen
3. WHEN Leistungsdaten abgerufen werden, THEN THE System SHALL die Daten nach Auswertungskriterien gruppieren
4. THE System SHALL Auswertungen für einzelne Mitarbeiter oder Gruppen von Mitarbeitern ermöglichen
5. WHEN eine Auswertung erstellt wird, THEN THE System SHALL die Berechnungen basierend auf den zugeordneten Auswertungskriterien durchführen

### Requirement 10

**User Story:** Als Benutzer möchte ich prozentuale Quoten berechnen lassen, so dass ich Leistungsindikatoren vergleichen kann.

#### Acceptance Criteria

1. WHEN eine Auswertung erstellt wird, THEN THE System SHALL Abschlussquote, Terminvereinbarungsquote, Termine-Anfahrquote, nicht interessierte Kunden Quote, technisch nicht machbar Quote, Quote der nicht erreichten Kunden, Quote für Folgetermine-Vereinbarungen, Quote für Angebote, Quote für zu teuer und Quote für QC bestanden berechnen
2. WHEN Quoten berechnet werden, THEN THE System SHALL die Prozentsätze basierend auf den Gesamtwerten der relevanten Auswertungskriterien berechnen
3. WHEN alle Quoten berechnet werden, THEN THE System SHALL sicherstellen dass die Summe der Quoten 100 Prozent ergibt
4. THE System SHALL Quoten mit zwei Dezimalstellen anzeigen
5. WHEN keine Daten für eine Quote vorhanden sind, THEN THE System SHALL 0 Prozent anzeigen

### Requirement 11

**User Story:** Als Benutzer möchte ich beschreibende Verhältnisse zu Quoten sehen, so dass ich die Bedeutung der Zahlen besser verstehe.

#### Acceptance Criteria

1. WHEN eine Quote berechnet wird, THEN THE System SHALL ein beschreibendes Verhältnis berechnen (z.B. "jeder 4. angefahrene Termin ist ein Verkauf")
2. WHEN ein Verhältnis berechnet wird, THEN THE System SHALL die Formel "1 zu X" verwenden, wobei X aus der Quote abgeleitet wird
3. WHEN ein Verhältnis angezeigt wird, THEN THE System SHALL eine verständliche Beschreibung in deutscher Sprache ausgeben
4. THE System SHALL Verhältnisse für alle berechneten Quoten bereitstellen
5. WHEN eine Quote 0 Prozent ist, THEN THE System SHALL "keine Daten" als Verhältnis anzeigen

### Requirement 12

**User Story:** Als Benutzer möchte ich Auswertungen als visuelle Diagramme sehen, so dass ich Daten schnell erfassen kann.

#### Acceptance Criteria

1. WHEN eine Auswertung erstellt wird, THEN THE System SHALL Balkendiagramme, Säulendiagramme und Donut-Charts generieren
2. WHEN Diagramme erstellt werden, THEN THE System SHALL das Streamlit shadcn/ui Design verwenden
3. WHEN Diagramme angezeigt werden, THEN THE System SHALL alle relevanten Auswertungskriterien und Quoten visualisieren
4. THE System SHALL ein Dashboard mit allen Diagrammen in einer Übersicht bereitstellen
5. WHEN Diagramme generiert werden, THEN THE System SHALL interaktive Elemente für detaillierte Ansichten ermöglichen

### Requirement 13

**User Story:** Als Benutzer möchte ich Auswertungen speichern und archivieren, so dass ich historische Daten jederzeit abrufen kann.

#### Acceptance Criteria

1. WHEN eine Auswertung erstellt wird, THEN THE System SHALL einen Speichern-Button bereitstellen
2. WHEN ein Benutzer eine Auswertung speichert, THEN THE System SHALL die Auswertung mit Zeitstempel und Mitarbeiterbezug in der Datenbank speichern
3. WHEN eine Auswertung gespeichert wird, THEN THE System SHALL alle Diagramme, Quoten und Rohdaten archivieren
4. THE System SHALL eine unbegrenzte Anzahl gespeicherter Auswertungen unterstützen
5. WHEN ein Benutzer gespeicherte Auswertungen abruft, THEN THE System SHALL eine Liste aller archivierten Auswertungen anzeigen

### Requirement 14

**User Story:** Als Benutzer möchte ich Auswertungen in verschiedenen Formaten exportieren, so dass ich Daten außerhalb des Systems verwenden kann.

#### Acceptance Criteria

1. WHEN ein Benutzer eine Auswertung exportiert, THEN THE System SHALL die Formate PDF, Excel und JSON unterstützen
2. WHEN ein PDF-Export erstellt wird, THEN THE System SHALL alle Diagramme, Tabellen und Beschreibungen einbinden
3. WHEN ein Excel-Export erstellt wird, THEN THE System SHALL alle Rohdaten und berechneten Quoten in strukturierten Tabellen bereitstellen
4. WHEN ein JSON-Export erstellt wird, THEN THE System SHALL alle Daten in einem strukturierten JSON-Format bereitstellen
5. WHEN ein Export abgeschlossen ist, THEN THE System SHALL die Datei zum Download bereitstellen

### Requirement 15

**User Story:** Als Benutzer möchte ich gespeicherte Auswertungen importieren und erneut anzeigen, so dass ich historische Analysen überprüfen kann.

#### Acceptance Criteria

1. WHEN ein Benutzer eine gespeicherte Auswertung auswählt, THEN THE System SHALL alle Daten aus der Datenbank abrufen
2. WHEN eine Auswertung importiert wird, THEN THE System SHALL alle Diagramme und Tabellen in der ursprünglichen Form wiederherstellen
3. WHEN eine importierte Auswertung angezeigt wird, THEN THE System SHALL den Zeitraum und das Erstellungsdatum anzeigen
4. THE System SHALL die Möglichkeit bieten, importierte Auswertungen erneut zu exportieren
5. WHEN eine Auswertung importiert wird, THEN THE System SHALL die Daten schreibgeschützt anzeigen

### Requirement 16

**User Story:** Als Benutzer möchte ich Mitarbeiter in der Controlling-UI filtern, so dass ich gezielt Auswertungen für bestimmte Gruppen erstellen kann.

#### Acceptance Criteria

1. WHEN ein Benutzer die Controlling-UI öffnet, THEN THE System SHALL alle Mitarbeiter mit ihren Positionen anzeigen
2. WHEN ein Benutzer einen Filter anwendet, THEN THE System SHALL die Mitarbeiterliste nach Position, Name, Wohnort oder Arbeitsbeginndatum filtern
3. WHEN ein Filter aktiv ist, THEN THE System SHALL nur die gefilterten Mitarbeiter in Auswertungen einbeziehen
4. THE System SHALL mehrere Filter gleichzeitig unterstützen
5. WHEN ein Benutzer Filter zurücksetzt, THEN THE System SHALL alle Mitarbeiter wieder anzeigen

### Requirement 17

**User Story:** Als System möchte ich performante Berechnungen durchführen, so dass auch große Datenmengen schnell ausgewertet werden können.

#### Acceptance Criteria

1. WHEN eine Auswertung mit mehr als 100 Mitarbeitern erstellt wird, THEN THE System SHALL die Berechnung innerhalb von 5 Sekunden abschließen
2. WHEN Quoten berechnet werden, THEN THE System SHALL optimierte Algorithmen verwenden
3. WHEN Diagramme generiert werden, THEN THE System SHALL Caching-Mechanismen für wiederholte Anfragen nutzen
4. THE System SHALL Datenbankabfragen optimieren um Ladezeiten zu minimieren
5. WHEN große Datenmengen verarbeitet werden, THEN THE System SHALL Fortschrittsindikatoren anzeigen

### Requirement 18

**User Story:** Als Benutzer möchte ich rückwirkend auf alle Auswertungen und Berichte zugreifen, so dass ich historische Leistungsdaten analysieren kann.

#### Acceptance Criteria

1. WHEN ein Benutzer das Archiv öffnet, THEN THE System SHALL alle gespeicherten Auswertungen chronologisch sortiert anzeigen
2. WHEN ein Benutzer eine historische Auswertung auswählt, THEN THE System SHALL die Auswertung mit allen ursprünglichen Daten anzeigen
3. THE System SHALL eine Suchfunktion für historische Auswertungen bereitstellen
4. THE System SHALL Filter für historische Auswertungen nach Mitarbeiter, Zeitraum oder Erstellungsdatum bereitstellen
5. WHEN historische Auswertungen abgerufen werden, THEN THE System SHALL die Daten aus der Archiv-Datenbank laden

### Requirement 19

**User Story:** Als Admin möchte ich Berechnungsmethoden für Auswertungskriterien definieren, so dass verschiedene Positionen unterschiedlich ausgewertet werden.

#### Acceptance Criteria

1. WHEN ein Admin ein Auswertungskriterium erstellt, THEN THE System SHALL die Auswahl einer Berechnungsmethode ermöglichen
2. THE System SHALL verschiedene Berechnungsmethoden unterstützen (Summe, Durchschnitt, Prozentsatz, Verhältnis)
3. WHEN eine Berechnungsmethode ausgewählt wird, THEN THE System SHALL diese mit dem Auswertungskriterium in der Datenbank speichern
4. WHEN eine Auswertung erstellt wird, THEN THE System SHALL die definierten Berechnungsmethoden anwenden
5. WHEN eine Berechnungsmethode geändert wird, THEN THE System SHALL zukünftige Auswertungen mit der neuen Methode berechnen

### Requirement 20

**User Story:** Als Benutzer möchte ich Vergleichsauswertungen zwischen Mitarbeitern erstellen, so dass ich Leistungsunterschiede erkennen kann.

#### Acceptance Criteria

1. WHEN ein Benutzer mehrere Mitarbeiter auswählt, THEN THE System SHALL eine Vergleichsauswertung ermöglichen
2. WHEN eine Vergleichsauswertung erstellt wird, THEN THE System SHALL alle Quoten und Kennzahlen nebeneinander anzeigen
3. WHEN Vergleichsdiagramme erstellt werden, THEN THE System SHALL verschiedene Farben für jeden Mitarbeiter verwenden
4. THE System SHALL Vergleichsauswertungen für bis zu 10 Mitarbeiter gleichzeitig unterstützen
5. WHEN eine Vergleichsauswertung gespeichert wird, THEN THE System SHALL alle verglichenen Mitarbeiter in der Archivierung vermerken

### Requirement 21

**User Story:** Als Benutzer möchte ich Benachrichtigungen für wichtige Ereignisse erhalten, so dass ich zeitnah auf Änderungen reagieren kann.

#### Acceptance Criteria

1. WHEN ein Mitarbeiter eine bestimmte Quote überschreitet, THEN THE System SHALL eine Benachrichtigung anzeigen
2. WHEN ein Mitarbeiter eine bestimmte Quote unterschreitet, THEN THE System SHALL eine Warnung anzeigen
3. WHEN eine Auswertung abgeschlossen ist, THEN THE System SHALL eine Erfolgsmeldung anzeigen
4. THE System SHALL Schwellenwerte für Benachrichtigungen in den Admin-Einstellungen konfigurierbar machen
5. WHEN Benachrichtigungen angezeigt werden, THEN THE System SHALL diese in einem nicht-störenden Format präsentieren
