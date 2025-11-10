# Implementation Plan: Multi-PDF Positioning Optimization

## Task Overview

Dieser Implementierungsplan beschreibt die schrittweise Umsetzung des Multi-PDF Positioning Systems. Jeder Task baut auf den vorherigen auf und endet mit einer funktionierenden, getesteten Komponente.

- [-] 1. Projekt-Setup und Datenstruktur-Analyse


- [ ] 1.1 Projekt-Struktur erstellen und Dependencies installieren
  - Erstelle Hauptverzeichnis-Struktur für das Projekt
  - Installiere erforderliche Python-Pakete (PyPDF2, PyYAML, Pillow)
  - Erstelle Konfigurationsdatei mit Pfaden und Einstellungen
  - _Requirements: 8.1_

- [ ] 1.2 YML-Dateien analysieren und Datenstruktur verstehen
  - Lese alle 48 YML-Dateien aus `coords_multi` ein
  - Analysiere die Struktur und identifiziere alle verwendeten Attribute
  - Erstelle eine Liste aller Text-Elemente (statisch und dynamisch)
  - Dokumentiere die YML-Formatierung und Trennzeichen
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 1.3 PDF-Vorlagen inventarisieren
  - Liste alle 48 PDF-Dateien aus dem Verzeichnis auf
  - Validiere, dass für jede PDF eine entsprechende YML-Datei existiert
  - Erstelle Mapping zwischen PDF-Dateien und YML-Dateien
  - _Requirements: 1.1_

- [ ] 2. YML Parser implementieren
- [ ] 2.1 YML-Parsing-Modul erstellen
  - Implementiere `parse_yml(yml_path)` Funktion
  - Extrahiere alle Text-Elemente mit Attributen (Text, Position, Schriftart, Schriftgröße, Farbe)
  - Speichere Original-Reihenfolge der Elemente (index)
  - Erstelle YMLElement Dataclass
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2.2 YML-Struktur-Erhaltung implementieren
  - Implementiere Funktion zum Bewahren der Original-Formatierung
  - Speichere Trennzeichen und Leerzeichen
  - Teste mit mehreren YML-Dateien
  - _Requirements: 2.4, 2.5_

- [ ] 3. PDF Analyzer implementieren
- [ ] 3.1 PDF-Metadaten-Extraktion
  - Implementiere `analyze_pdf(pdf_path)` Funktion
  - Extrahiere Seitengröße (Breite, Höhe)
  - Erstelle PDFAnalysis Dataclass
  - Teste mit mehreren PDF-Dateien
  - _Requirements: 1.1, 1.2_

- [ ] 3.2 PDF-Design-Analyse (vereinfacht)
  - Implementiere Funktion zur Erkennung von Farbbereichen
  - Identifiziere Header-, Content- und Footer-Bereiche basierend auf Y-Koordinaten
  - Definiere Safe Zones (sichere Bereiche für Text)
  - _Requirements: 1.2, 1.3_

- [ ] 3.3 Batch-Analyse aller PDFs
  - Implementiere Funktion zur Analyse aller 48 PDFs
  - Speichere Analyse-Ergebnisse in strukturiertem Format (JSON)
  - Erstelle Zusammenfassung der Design-Charakteristiken pro Firma
  - _Requirements: 1.3, 1.4, 1.5_

- [ ] 4. Position Calculator - Basis-Implementierung
- [ ] 4.1 Positionierungs-Regeln definieren
  - Definiere POSITIONING_RULES Dictionary mit Mindestabständen
  - Implementiere `ensure_bounds(position)` Funktion
  - Implementiere `check_collisions(positions)` Funktion
  - _Requirements: 3.3, 3.4, 6.1, 6.2_

- [ ] 4.2 Basis-Positionierungs-Algorithmus
  - Implementiere `calculate_positions()` Hauptfunktion
  - Implementiere einfache Grid-basierte Positionierung als Fallback
  - Teste mit einer Beispiel-YML-Datei
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 5. Positionierungs-Strategien implementieren
- [ ] 5.1 Strategie 1: Header-Focused (Firma 1)
  - Implementiere `apply_header_focused_strategy()` Funktion
  - Positioniere Hauptüberschrift oben links
  - Positioniere wichtige Werte (kWp) rechts unten
  - Positioniere Kundeninfo zentriert unter Überschrift
  - Teste mit Seite 1-8 von Firma 1
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.2 Strategie 2: Center-Prominent (Firma 2)
  - Implementiere `apply_center_prominent_strategy()` Funktion
  - Positioniere Hauptüberschrift zentriert
  - Positioniere wichtige Werte rechts oben
  - Positioniere Kundeninfo links oben
  - Teste mit Seite 1-8 von Firma 2
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.3 Strategie 3: Asymmetric-Modern (Firma 3)
  - Implementiere `apply_asymmetric_modern_strategy()` Funktion
  - Positioniere Hauptüberschrift rechts oben
  - Positioniere wichtige Werte links unten
  - Positioniere Kundeninfo rechts Mitte
  - Teste mit Seite 1-8 von Firma 3
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.4 Strategie 4: Grid-Based (Firma 4)
  - Implementiere `apply_grid_based_strategy()` Funktion
  - Verteile Elemente in 3x3 Grid
  - Positioniere wichtige Werte im Zentrum
  - Symmetrische Anordnung
  - Teste mit Seite 1-8 von Firma 4
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.5 Strategie 5: Diagonal-Flow (Firma 5)
  - Implementiere `apply_diagonal_flow_strategy()` Funktion
  - Positioniere Elemente diagonal von links oben nach rechts unten
  - Wichtige Werte folgen diagonaler Linie
  - Teste mit Seite 1-8 von Firma 5
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.6 Strategie 6: Sidebar-Layout (Firma 6)
  - Implementiere `apply_sidebar_layout_strategy()` Funktion
  - Positioniere Hauptinfo in linker Spalte
  - Positioniere wichtige Werte in rechter Spalte
  - Klare vertikale Trennung
  - Teste mit Seite 1-8 von Firma 6
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5.7 Strategie-Auswahl-Logik
  - Implementiere `select_strategy(firma, seite)` Funktion
  - Mappe Firma-Nummern zu Strategien
  - Ermögliche Strategie-Variationen pro Seite
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 6. YML Generator implementieren
- [ ] 6.1 YML-Generierungs-Modul erstellen
  - Implementiere `generate_yml(elements, new_positions, output_path)` Funktion
  - Implementiere `format_position(x1, y1, x2, y2)` für korrekte Formatierung
  - Stelle sicher, dass alle Attribute außer Position unverändert bleiben
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 6.2 Format-Erhaltung implementieren
  - Implementiere `preserve_formatting()` Funktion
  - Behalte Original-Trennzeichen (----------------------------------------) bei
  - Behalte Leerzeilen und Einrückungen bei
  - Teste mit mehreren YML-Dateien
  - _Requirements: 5.2, 5.4_

- [ ] 6.3 YML-Validierung
  - Implementiere `validate_yml_output(yml_path)` Funktion
  - Prüfe, dass alle Original-Elemente vorhanden sind
  - Prüfe, dass nur Positionen geändert wurden
  - Prüfe, dass YML-Format gültig ist
  - _Requirements: 5.5, 6.4_

- [ ] 7. Backup Manager implementieren
- [ ] 7.1 Backup-Funktionalität erstellen
  - Implementiere `create_backup(yml_files)` Funktion
  - Erstelle Backup-Verzeichnis mit Zeitstempel
  - Kopiere alle Original-YML-Dateien
  - _Requirements: 8.1, 8.2_

- [ ] 7.2 Wiederherstellungs-Funktionalität
  - Implementiere `restore_backup(backup_id)` Funktion
  - Implementiere `list_backups()` Funktion
  - Implementiere `validate_backup(backup_path)` Funktion
  - _Requirements: 8.3, 8.4, 8.5_

- [ ] 8. Validierungs-System implementieren
- [ ] 8.1 Position-Validierung
  - Implementiere `validate_positions(positions)` Funktion
  - Prüfe, dass alle Positionen innerhalb PDF-Grenzen liegen (0-595, 0-842)
  - Prüfe Mindestabstand zum Rand (10 Punkte)
  - Prüfe Mindestabstand zwischen Elementen (5 Punkte)
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 8.2 Kollisions-Erkennung
  - Implementiere `detect_collisions(positions)` Funktion
  - Identifiziere überlappende Text-Elemente
  - Implementiere automatische Kollisions-Auflösung
  - _Requirements: 6.2, 3.4_

- [ ] 8.3 Validierungs-Report
  - Implementiere `generate_validation_report()` Funktion
  - Dokumentiere alle Validierungs-Prüfungen
  - Liste Warnungen und Fehler auf
  - Erstelle Zusammenfassung pro Firma und Seite
  - _Requirements: 6.4, 6.5_

- [ ] 9. Haupt-Orchestrierung implementieren
- [ ] 9.1 Main-Workflow erstellen
  - Implementiere `main()` Funktion mit vollständigem Workflow
  - Integriere alle Komponenten (Parser, Analyzer, Calculator, Generator)
  - Implementiere Fortschritts-Anzeige
  - Implementiere Fehlerbehandlung
  - _Requirements: Alle_

- [ ] 9.2 Batch-Processing
  - Implementiere Verarbeitung aller 48 Kombinationen
  - Implementiere parallele Verarbeitung (optional)
  - Implementiere Logging für jeden Schritt
  - _Requirements: Alle_

- [ ] 9.3 Command-Line Interface
  - Implementiere CLI mit argparse
  - Optionen: --analyze, --generate, --validate, --backup, --restore
  - Implementiere Hilfe-Text und Beispiele
  - _Requirements: Alle_

- [ ] 10. Visualisierung und Dokumentation
- [ ] 10.1 Visualisierungs-Tool erstellen
  - Implementiere Funktion zur Visualisierung von Positionen
  - Erstelle Overlay-Bilder mit alten und neuen Positionen
  - Generiere Vergleichs-Ansichten
  - _Requirements: 7.1, 7.2_

- [ ] 10.2 Statistiken generieren
  - Implementiere `generate_statistics()` Funktion
  - Berechne durchschnittliche Positions-Änderungen
  - Dokumentiere Strategie-Verteilung
  - Erstelle Zusammenfassung der Optimierungen
  - _Requirements: 7.3, 7.4_

- [ ] 10.3 Benutzer-Dokumentation
  - Erstelle README mit Installations-Anleitung
  - Dokumentiere alle CLI-Optionen
  - Erstelle Beispiele für typische Anwendungsfälle
  - Dokumentiere Positionierungs-Strategien
  - _Requirements: 7.5_

- [ ] 11. Testing und Qualitätssicherung
- [ ] 11.1 Unit Tests schreiben
  - Schreibe Tests für YML Parser
  - Schreibe Tests für PDF Analyzer
  - Schreibe Tests für Position Calculator
  - Schreibe Tests für YML Generator
  - Erreiche mindestens 80% Code-Coverage

- [ ] 11.2 Integration Tests
  - Teste End-to-End Workflow für eine Firma-Seiten-Kombination
  - Teste Batch-Processing für alle 48 Kombinationen
  - Teste Backup und Wiederherstellung
  - Teste Fehlerbehandlung

- [ ] 11.3 Validierungs-Tests
  - Validiere alle generierten YML-Dateien
  - Prüfe, dass keine Positionen außerhalb der Grenzen liegen
  - Prüfe, dass keine Überlappungen existieren
  - Vergleiche generierte YML mit Original (nur Positionen geändert)

- [ ] 12. Finale Integration und Deployment
- [ ] 12.1 Performance-Optimierung
  - Messe Laufzeit für alle 48 Kombinationen
  - Optimiere langsame Komponenten
  - Implementiere Caching wo sinnvoll

- [ ] 12.2 Finale Validierung
  - Führe vollständigen Test-Durchlauf durch
  - Validiere alle 48 generierten YML-Dateien
  - Erstelle finalen Validierungs-Report

- [ ] 12.3 Deployment-Vorbereitung
  - Erstelle requirements.txt
  - Erstelle Setup-Skript
  - Dokumentiere System-Anforderungen
  - Erstelle Deployment-Anleitung
