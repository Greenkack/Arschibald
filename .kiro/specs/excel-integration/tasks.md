# Implementation Plan

## Task Overview

Dieser Implementierungsplan beschreibt die schrittweise Umsetzung der Excel-Integration in die PV-Anwendung. Jeder Task baut auf den vorherigen auf und endet mit einer funktionsfähigen Integration.

---

## Phase 1: Grundlagen und Infrastruktur

- [ ] 1. Datenmodelle und Basis-Klassen erstellen
  - Cell, ExcelMatrix Dataclasses implementieren
  - Basis-Struktur für ExcelManager erstellen
  - Hilfsfunktionen für Zellreferenzen (A1-Notation)
  - _Requirements: 1.1, 2.1, 2.2_

- [ ] 2. Formula Engine Grundgerüst
  - FormulaEngine Klasse mit Parser-Grundstruktur
  - Regex-basiertes Parsing für einfache Formeln
  - Integration der bestehenden `python_function_recipes.py`
  - Basis-Fehlerbehandlung (FormulaError Klassen)
  - _Requirements: 5.1, 5.2, 5.3, 10.1, 10.2_

- [ ] 3. Erweiterte Formel-Funktionen implementieren
  - Alle mathematischen Funktionen (SUM, AVERAGE, MIN, MAX, ROUND, etc.)
  - Logische Funktionen (IF, AND, OR, IFERROR)
  - Lookup-Funktionen (VLOOKUP, HLOOKUP, INDEX, MATCH)
  - Datums- und Textfunktionen
  - Verschachtelte Formeln unterstützen
  - _Requirements: 5.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 3.1 Unit Tests für Formel-Engine
  - Tests für alle Excel-Funktionen
  - Tests für verschachtelte Formeln
  - Tests für Fehlerbehandlung
  - Edge-Case Tests
  - _Requirements: 5.2, 6.6_

---

## Phase 2: Excel Manager und Zustandsverwaltung

- [ ] 4. ExcelManager Kern-Funktionalität
  - Matrix laden und initialisieren
  - get_cell_value und set_cell_value implementieren
  - Formel-Parsing und -Ausführung integrieren
  - Dependency Graph für Zell-Abhängigkeiten
  - Automatische Neuberechnung bei Änderungen
  - _Requirements: 5.5, 11.4_

- [ ] 5. CRUD-Operationen für Zeilen und Spalten
  - add_row mit Position-Parameter
  - add_column mit Position-Parameter
  - delete_row mit Formel-Anpassung
  - delete_column mit Formel-Anpassung
  - Formel-Referenzen automatisch aktualisieren
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6. Undo/Redo Funktionalität
  - Undo-Stack implementieren
  - Redo-Stack implementieren
  - State-Snapshots für Operationen
  - Integration in alle Änderungs-Operationen
  - _Requirements: 12.3_

- [ ] 6.1 Unit Tests für ExcelManager
  - Tests für CRUD-Operationen
  - Tests für Undo/Redo
  - Tests für Dependency Graph
  - Performance-Tests
  - _Requirements: 3.5, 11.2_

---

## Phase 3: UI-Komponenten

- [ ] 7. Admin Panel Integration
  - Neuen Tab "Preis Matrix" in ADMIN_TAB_KEYS_DEFINITION_GLOBAL hinzufügen
  - Tab-Rendering in admin_panel.py integrieren
  - Navigation und State-Management
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 8. Excel Grid UI Basis-Komponente
  - Neue Datei `excel_grid_ui.py` erstellen
  - Matrix-Auswahl Dropdown
  - Toolbar mit Basis-Buttons (Neu, Speichern, Laden)
  - Grid-Darstellung mit Streamlit Data Editor
  - Zeilen- und Spalten-Header (A, B, C... / 1, 2, 3...)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 9. Formelleiste und Zell-Bearbeitung
  - Formelleiste über dem Grid
  - Aktive Zelle anzeigen
  - Formel-Eingabe und -Anzeige
  - Zell-Bearbeitung mit Validierung
  - Fehleranzeige in Zellen
  - _Requirements: 2.3, 5.1, 10.1, 10.2, 10.3, 10.4, 10.5, 12.4_

- [ ] 10. Erweiterte Grid-Features
  - Zeilen/Spalten hinzufügen/löschen Buttons
  - Tastaturnavigation (Pfeiltasten, Tab, Enter)
  - Copy-Paste Funktionalität
  - Zell-Formatierung (Zahlen, Datum, Text)
  - Tooltips für Fehler und Hilfe
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 12.1, 12.2, 12.5_

---

## Phase 4: Persistenz und CRUD

- [ ] 11. Matrix-Verwaltung UI
  - Dialog für neue Matrix erstellen
  - Matrix-Liste anzeigen
  - Matrix laden
  - Matrix löschen
  - Matrix umbenennen
  - Matrix klonen
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 12. Speichern und Laden
  - Speichern-Funktion mit price_matrix_store Integration
  - Laden-Funktion mit Formel-Wiederherstellung
  - Auto-Save Funktionalität (optional)
  - Änderungs-Tracking
  - _Requirements: 4.2, 4.3_

- [ ] 12.1 Integration Tests für Persistenz
  - Test: Matrix erstellen → Speichern → Laden
  - Test: Formeln bleiben erhalten
  - Test: Große Matrizen (1000+ Zeilen)
  - _Requirements: 11.1_

---

## Phase 5: Import/Export

- [ ] 13. CSV Import
  - Datei-Upload Widget
  - CSV-Parser mit Encoding-Erkennung
  - Delimiter-Erkennung (;, ,, \t)
  - Matrix aus CSV erstellen
  - Fehlerbehandlung bei ungültigen Dateien
  - _Requirements: 8.1, 8.4, 8.6_

- [ ] 14. Excel Import (XLS/XLSX)
  - Excel-Datei-Upload
  - openpyxl Integration
  - Formel-Erkennung und -Übernahme
  - Sheet-Auswahl (bei mehreren Sheets)
  - Fehlerbehandlung
  - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 15. Export-Funktionalität
  - Export als CSV
  - Export als Excel (XLSX) mit Formeln
  - Download-Dialog
  - Dateiname-Generierung
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 15.1 Import/Export Tests
  - Test: CSV Import → Export → Re-Import
  - Test: Excel Import mit Formeln
  - Test: Große Dateien (10 MB)
  - Test: Verschiedene Encodings
  - _Requirements: 8.6, 11.5_

---

## Phase 6: Performance-Optimierung

- [ ] 16. Caching implementieren
  - Formel-Cache in FormulaEngine
  - Cache-Invalidierung bei Änderungen
  - Dependency-Cache für schnelle Neuberechnung
  - _Requirements: 11.2, 11.4_

- [ ] 17. Lazy Loading für große Datensätze
  - Virtuelles Scrolling im Grid
  - Nur sichtbare Zellen laden
  - Batch-Loading bei Scroll
  - _Requirements: 11.1, 11.3_

- [ ] 18. Batch-Operationen
  - Batch-Update für mehrere Zellen
  - Transaktionale DB-Operationen
  - Performance-Optimierung für große Updates
  - _Requirements: 11.2_

- [ ] 18.1 Performance Tests
  - Test: 1000 Zeilen × 50 Spalten
  - Test: 100 Formeln mit Abhängigkeiten
  - Test: Neuberechnung unter 2 Sekunden
  - _Requirements: 11.1, 11.2_

---

## Phase 7: Produktpreis-Integration

- [ ] 19. Produktpreis-Berechnung aus Matrix
  - calculate_product_price_from_matrix Funktion
  - Integration mit lookup_price aus price_matrix_store
  - Unterstützung für Pauschal- und Additiv-Modus
  - Zubehör-Preise einbeziehen (optional)
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 20. UI für Produktpreis-Konfiguration
  - Radio-Button: Einzelpreis vs. Matrix-Preis
  - Matrix-Auswahl für Produkte
  - Vorschau der berechneten Preise
  - Integration in Produktverwaltung
  - _Requirements: 7.4, 7.5_

- [ ] 20.1 Integration Tests für Produktpreise
  - Test: Preis aus Matrix berechnen
  - Test: Pauschal-Modus
  - Test: Additiv-Modus mit Zubehör
  - Test: Matrix-Änderung aktualisiert Preise
  - _Requirements: 7.3_

---

## Phase 8: Finalisierung und Dokumentation

- [ ] 21. Fehlerbehandlung und Validierung
  - Alle Fehlertypen implementieren (#ERROR!, #REF!, #DIV/0!, etc.)
  - Tooltip-Hilfe für Fehler
  - Input-Validierung für alle Felder
  - Zirkelbezug-Erkennung
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 22. Benutzerfreundlichkeit
  - Tastatur-Shortcuts dokumentieren
  - Hilfe-Tooltips für alle Funktionen
  - Beispiel-Matrizen erstellen
  - Onboarding-Tutorial (optional)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 23. End-to-End Tests
  - Vollständiger Workflow-Test
  - Test aller Features in Kombination
  - Regressions-Tests
  - _Requirements: Alle_

- [ ] 24. Dokumentation
  - Benutzer-Dokumentation erstellen
  - Entwickler-Dokumentation
  - API-Dokumentation
  - Beispiele und Tutorials
  - _Requirements: Alle_

---

## Hinweise zur Implementierung

### Reihenfolge
Die Tasks sollten in der angegebenen Reihenfolge ausgeführt werden, da spätere Tasks auf früheren aufbauen.

### Testing
Alle Test-Tasks sind erforderlich und sollten vollständig durchgeführt werden, um hohe Code-Qualität sicherzustellen.

### Integration
Jeder Task sollte mit einer funktionsfähigen Integration enden, die getestet werden kann.
