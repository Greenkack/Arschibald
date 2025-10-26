# Implementation Plan

- [x] 1. Erstelle zentrale PriceMatrix Klasse mit INDEX/MATCH Logik

  - Implementiere neue `PriceMatrix` Klasse in separater Datei
  - Schreibe robuste `get_price()` Methode mit exakter INDEX/MATCH Semantik
  - Implementiere Speichermodell-Normalisierung (trim, case-insensitive)
  - Füge Validierung für Matrix-Struktur hinzu
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 2. Implementiere einheitliche Matrix-Loader mit Caching

  - Erstelle `MatrixLoader` Klasse mit Hash-basiertem Caching
  - Implementiere einheitliche CSV-Parser Funktion
  - Implementiere einheitliche Excel-Parser Funktion
  - Füge Struktur-Validierung hinzu (erste Spalte = "Anzahl Module", letzte = "Ohne Speicher")
  - _Requirements: 2.2, 3.3, 4.4_

- [x] 3. Implementiere StorageModelResolver für korrekte Speicher-Auflösung

  - Erstelle `StorageModelResolver` Klasse
  - Implementiere `resolve_storage_name()` Methode
  - Füge Fallback-Logik für "Ohne Speicher" hinzu
  - Teste Auflösung von Speicher-IDs zu Modellnamen
  - _Requirements: 1.2, 1.3, 4.5_

- [x] 4. Ersetze bestehende Preismatrix-Logik in calculations.py

  - Identifiziere und entferne die fehlerhafte Index-Korrektur (+5 Module)
  - Ersetze bestehende Matrix-Lookup Logik mit neuer PriceMatrix Klasse
  - Integriere StorageModelResolver für korrekte Speicher-Auflösung
  - Entferne Debug-Prints und temporäre Fixes
  - _Requirements: 3.1, 3.2, 1.1, 1.4_

- [ ] 5. Verbessere Admin Panel Matrix-Upload Validierung
  - Erweitere `render_price_matrix()` Funktion um Struktur-Validierung
  - Füge aussagekräftige Fehlermeldungen für Upload-Probleme hinzu
  - Implementiere Vorschau-Validierung vor dem Speichern
  - Teste Upload-Workflow für CSV und Excel Dateien
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 6. Implementiere robuste Fehlerbehandlung
  - Füge spezifische Fehlermeldungen für Matrix-Lookup Probleme hinzu
  - Implementiere Fallback-Strategien bei fehlenden Werten
  - Verbessere Error-Logging für Debugging
  - Teste Edge Cases (leere Matrix, ungültige Eingaben)
  - _Requirements: 4.4, 1.5, 3.4_

- [ ] 7. Erstelle umfassende Unit Tests
  - Schreibe Tests für PriceMatrix INDEX/MATCH Logik
  - Teste MatrixLoader mit verschiedenen CSV/Excel Formaten
  - Teste StorageModelResolver mit realen Produktdaten
  - Implementiere Tests für Fehlerbehandlung und Edge Cases
  - _Requirements: 3.1, 4.1, 4.2, 4.3_

- [x] 8. Integriere Zusatzkosten-Berechnung korrekt

  - Stelle sicher, dass Matrixpreis als Basis verwendet wird
  - Implementiere korrekte Formel: Matrixpreis + Zubehör - Rabatte
  - Teste Echtzeit-Aktualisierung bei Änderungen
  - Validiere Endpreis-Berechnung mit verschiedenen Szenarien
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9. Konsolidiere und entferne alte Matrix-Implementierungen

  - Suche nach allen Preismatrix-Referenzen im gesamten Codebase
  - Entferne oder konsolidiere widersprüchliche Implementierungen
  - Aktualisiere alle Aufrufe auf neue zentrale Implementierung
  - Bereinige veraltete Funktionen und Kommentare
  - _Requirements: 3.1, 3.2_

- [ ] 10. Führe End-to-End Tests mit realen Daten durch
  - Teste kompletten Workflow: Upload → Berechnung → Anzeige
  - Validiere Preise mit bekannten Matrix-Werten
  - Teste verschiedene Speicher-Kombinationen
  - Verifiziere korrekte Anzeige in Solar Calculator UI
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 11. Optimiere Performance und finalisiere Implementation
  - Überprüfe Cache-Performance bei wiederholten Berechnungen
  - Optimiere Matrix-Loading für große Dateien
  - Füge Performance-Monitoring hinzu
  - Dokumentiere neue API und Verwendung
  - _Requirements: 3.3, 4.1_
