# Requirements Document

## Introduction

Dieses Dokument beschreibt die Anforderungen für die Integration einer vollständigen Excel-ähnlichen Funktionalität in die Streamlit-basierte PV-Anwendung. Das System soll es Benutzern ermöglichen, Preismatrizen und andere tabellarische Daten in einem Excel-ähnlichen Interface zu erstellen, zu bearbeiten und zu verwalten, mit vollständiger Unterstützung für Excel-Formeln und -Funktionen.

## Glossary

- **Excel-Grid**: Die tabellarische Benutzeroberfläche, die Excel-Tabellen nachahmt
- **Preismatrix**: Eine Tabelle zur Verwaltung von Produktpreisen und Berechnungen
- **Formel-Engine**: Das Backend-System zur Verarbeitung und Berechnung von Excel-Formeln
- **CRUD**: Create, Read, Update, Delete - Grundlegende Datenbankoperationen
- **Admin Panel**: Das Verwaltungsinterface der Anwendung (admin_panel.py)
- **Streamlit**: Das Python-Framework für die Web-Anwendung
- **CSV/XLS/XLSX**: Dateiformate für Tabellendaten (Comma-Separated Values, Excel-Formate)

## Requirements

### Requirement 1: Neues Untermenü "Preis Matrix"

**User Story:** Als Administrator möchte ich ein dediziertes Untermenü "Preis Matrix" im Admin Panel haben, damit ich schnell auf die Excel-Funktionalität zugreifen kann.

#### Acceptance Criteria

1. WHEN der Administrator das Admin Panel öffnet, SHALL das System ein neues Menü-Tab "Preis Matrix" anzeigen
2. WHEN der Administrator auf "Preis Matrix" klickt, SHALL das System die Excel-Grid-Oberfläche laden
3. THE System SHALL das neue Menü in der bestehenden Admin-Panel-Struktur integrieren
4. THE System SHALL die Navigation zwischen verschiedenen Admin-Bereichen ohne Datenverlust ermöglichen

### Requirement 2: Excel-ähnliche Grid-Oberfläche

**User Story:** Als Benutzer möchte ich eine Excel-ähnliche Tabelle sehen und bedienen können, damit ich vertraut mit der Oberfläche arbeiten kann.

#### Acceptance Criteria

1. THE System SHALL eine tabellarische Oberfläche mit Zeilen und Spalten anzeigen
2. THE System SHALL Spaltenüberschriften (A, B, C, ...) und Zeilennummern (1, 2, 3, ...) anzeigen
3. WHEN der Benutzer auf eine Zelle klickt, SHALL das System die Zelle zur Bearbeitung aktivieren
4. THE System SHALL die Größe der Tabelle dynamisch anpassen können
5. THE System SHALL mindestens 100 Zeilen und 26 Spalten (A-Z) initial unterstützen

### Requirement 3: Dynamische Tabellengröße

**User Story:** Als Benutzer möchte ich die Tabellengröße nach Bedarf erweitern können, damit ich mit unterschiedlich großen Datensätzen arbeiten kann.

#### Acceptance Criteria

1. THE System SHALL eine Funktion zum Hinzufügen von Zeilen bereitstellen
2. THE System SHALL eine Funktion zum Hinzufügen von Spalten bereitstellen
3. THE System SHALL eine Funktion zum Löschen von Zeilen bereitstellen
4. THE System SHALL eine Funktion zum Löschen von Spalten bereitstellen
5. WHEN der Benutzer Zeilen oder Spalten hinzufügt, SHALL das System die Formeln entsprechend anpassen

### Requirement 4: CRUD-Operationen für Tabellen

**User Story:** Als Benutzer möchte ich Tabellen erstellen, speichern, laden und löschen können, damit ich mehrere Preismatrizen verwalten kann.

#### Acceptance Criteria

1. THE System SHALL eine Funktion zum Erstellen neuer Tabellen bereitstellen
2. THE System SHALL eine Funktion zum Speichern von Tabellen in der Datenbank bereitstellen
3. THE System SHALL eine Funktion zum Laden gespeicherter Tabellen bereitstellen
4. THE System SHALL eine Funktion zum Löschen von Tabellen bereitstellen
5. THE System SHALL eine Liste aller gespeicherten Tabellen anzeigen
6. WHEN der Benutzer eine Tabelle speichert, SHALL das System einen eindeutigen Namen vergeben oder abfragen

### Requirement 5: Excel-Formel-Unterstützung

**User Story:** Als Benutzer möchte ich Excel-Formeln in Zellen eingeben können, damit ich automatische Berechnungen durchführen kann.

#### Acceptance Criteria

1. WHEN der Benutzer eine Formel mit "=" beginnt, SHALL das System die Formel als Berechnung interpretieren
2. THE System SHALL mindestens folgende Excel-Funktionen unterstützen: SUM, AVERAGE, MIN, MAX, IF, VLOOKUP, HLOOKUP, COUNT, ROUND, SUMIF, SUMIFS
3. THE System SHALL Zellreferenzen im A1-Format (z.B. A1, B2) unterstützen
4. THE System SHALL Bereichsreferenzen (z.B. A1:B10) unterstützen
5. THE System SHALL Formeln automatisch neu berechnen, wenn sich referenzierte Zellen ändern
6. WHEN eine Formel einen Fehler enthält, SHALL das System eine Fehlermeldung in der Zelle anzeigen

### Requirement 6: Erweiterte Excel-Funktionen

**User Story:** Als Benutzer möchte ich komplexe Excel-Funktionen nutzen können, damit ich anspruchsvolle Berechnungen durchführen kann.

#### Acceptance Criteria

1. THE System SHALL mathematische Funktionen unterstützen (ROUND, ROUNDUP, ROUNDDOWN, MOD)
2. THE System SHALL logische Funktionen unterstützen (IF, AND, OR, IFERROR)
3. THE System SHALL Lookup-Funktionen unterstützen (VLOOKUP, HLOOKUP, INDEX, MATCH)
4. THE System SHALL Datumsfunktionen unterstützen (DATE, TODAY, YEAR, MONTH, DAY)
5. THE System SHALL Textfunktionen unterstützen (TEXT)
6. THE System SHALL verschachtelte Formeln unterstützen

### Requirement 7: Integration mit Produktpreisen

**User Story:** Als Benutzer möchte ich Preismatrizen für Produkte erstellen können, damit ich Pauschalpreise anstelle von Einzelpreisen berechnen kann.

#### Acceptance Criteria

1. THE System SHALL eine Funktion zum Verknüpfen von Tabellenzellen mit Produkten bereitstellen
2. THE System SHALL berechnete Preise aus der Tabelle in das Produktsystem übernehmen können
3. WHEN ein Preis in der Matrix geändert wird, SHALL das System die Produktpreise aktualisieren
4. THE System SHALL eine Vorschau der berechneten Preise anzeigen
5. THE System SHALL die Möglichkeit bieten, zwischen Einzelpreisen und Matrix-Preisen zu wählen

### Requirement 8: Import-Funktionalität

**User Story:** Als Benutzer möchte ich externe Tabellen importieren können, damit ich bestehende Daten nutzen kann.

#### Acceptance Criteria

1. THE System SHALL den Import von CSV-Dateien unterstützen
2. THE System SHALL den Import von XLS-Dateien unterstützen
3. THE System SHALL den Import von XLSX-Dateien unterstützen
4. WHEN der Benutzer eine Datei importiert, SHALL das System die Daten in das Grid laden
5. THE System SHALL Formeln aus importierten Excel-Dateien erkennen und übernehmen
6. WHEN eine importierte Datei Fehler enthält, SHALL das System eine Fehlermeldung anzeigen

### Requirement 9: Export-Funktionalität

**User Story:** Als Benutzer möchte ich Tabellen exportieren können, damit ich sie extern speichern und weitergeben kann.

#### Acceptance Criteria

1. THE System SHALL den Export als CSV-Datei unterstützen
2. THE System SHALL den Export als XLS-Datei unterstützen
3. THE System SHALL den Export als XLSX-Datei unterstützen
4. WHEN der Benutzer eine Tabelle exportiert, SHALL das System alle Daten und Formeln einschließen
5. THE System SHALL einen Download-Dialog für die exportierte Datei anzeigen

### Requirement 10: Datenvalidierung und Fehlerbehandlung

**User Story:** Als Benutzer möchte ich klare Fehlermeldungen erhalten, damit ich Probleme schnell beheben kann.

#### Acceptance Criteria

1. WHEN eine Formel einen Syntaxfehler enthält, SHALL das System "#ERROR!" in der Zelle anzeigen
2. WHEN eine Formel auf eine nicht existierende Zelle verweist, SHALL das System "#REF!" anzeigen
3. WHEN eine Division durch Null auftritt, SHALL das System "#DIV/0!" anzeigen
4. WHEN eine Formel einen Zirkelbezug enthält, SHALL das System "#CIRCULAR!" anzeigen
5. THE System SHALL eine Tooltip-Hilfe für Fehlermeldungen bereitstellen

### Requirement 11: Performance und Skalierbarkeit

**User Story:** Als Benutzer möchte ich mit großen Tabellen arbeiten können, ohne dass die Anwendung langsam wird.

#### Acceptance Criteria

1. THE System SHALL Tabellen mit mindestens 1000 Zeilen und 50 Spalten unterstützen
2. WHEN der Benutzer eine Zelle ändert, SHALL das System die Neuberechnung in weniger als 2 Sekunden durchführen
3. THE System SHALL nur sichtbare Zellen rendern (virtuelles Scrolling)
4. THE System SHALL Formeln effizient cachen
5. THE System SHALL große Dateien (bis 10 MB) importieren können

### Requirement 12: Benutzerfreundlichkeit

**User Story:** Als Benutzer möchte ich eine intuitive Oberfläche haben, damit ich ohne Schulung arbeiten kann.

#### Acceptance Criteria

1. THE System SHALL Tastaturnavigation (Pfeiltasten, Tab, Enter) unterstützen
2. THE System SHALL Copy-Paste-Funktionalität unterstützen
3. THE System SHALL Undo/Redo-Funktionalität bereitstellen
4. THE System SHALL eine Formelleiste zur Anzeige und Bearbeitung von Formeln anzeigen
5. THE System SHALL Tooltips für Funktionen und Bedienelemente anzeigen
