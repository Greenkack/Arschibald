# Requirements Document

## Introduction

Das PDF-Generierungssystem der Solar-App erstellt derzeit standardmäßig 7-seitige PDF-Angebote. Der Benutzer hat bereits alle notwendigen Template-Dateien (PDFs und YML-Koordinatendateien) vorbereitet, um eine neue Seite 1 einzufügen. Die bestehenden 7 Seiten müssen dabei um eine Position nach hinten verschoben werden (alte Seite 1 wird zu Seite 2, alte Seite 2 wird zu Seite 3, usw.).

Die Herausforderung besteht darin, alle Code-Referenzen, Hardcoded-Seitenzahlen, Schleifen und Logik im gesamten System zu identifizieren und präzise anzupassen, ohne dabei bestehende Funktionalität zu beeinträchtigen.

**Bereits vom Benutzer vorbereitet:**

- `coords/seite1.yml` bis `seite8.yml` (neue Seite 1 + verschobene Seiten 2-8)
- `coords_wp/wp_seite1.yml` bis `wp_seite8.yml` (Wärmepumpen-Variante)
- `pdf_templates_static/notext/nt_nt_01.pdf` bis `nt_nt_08.pdf` (neue Seite 1 + verschobene Seiten)
- `pdf_templates_static/notext/hp_nt_01.pdf` bis `hp_nt_08.pdf` (Wärmepumpen-Variante)

## Requirements

### Requirement 1: Code-Analyse und Identifikation

**User Story:** Als Entwickler möchte ich alle Code-Stellen identifizieren, die auf Seitenzahlen oder Seitenanzahl referenzieren, damit ich eine vollständige Übersicht über notwendige Änderungen habe.

#### Acceptance Criteria

1. WHEN die Code-Analyse durchgeführt wird THEN sollen alle Dateien identifiziert werden, die Hardcoded-Referenzen auf Seitenzahlen 1-7 enthalten
2. WHEN die Code-Analyse durchgeführt wird THEN sollen alle Schleifen identifiziert werden, die über `range(1, 8)` oder ähnliche Konstrukte iterieren
3. WHEN die Code-Analyse durchgeführt wird THEN sollen alle Funktionen identifiziert werden, die spezifische Seiten-Logik implementieren (z.B. `_draw_page3_waterfall_chart`)
4. WHEN die Code-Analyse durchgeführt wird THEN sollen alle Datei-Pfad-Konstruktionen identifiziert werden, die auf `seite1.yml` bis `seite7.yml` oder `nt_nt_01.pdf` bis `nt_nt_07.pdf` referenzieren
5. WHEN die Code-Analyse durchgeführt wird THEN soll eine strukturierte Liste aller betroffenen Dateien mit Zeilennummern erstellt werden

### Requirement 2: Seitenzahl-Erweiterung in Core-Dateien

**User Story:** Als System möchte ich die Seitenanzahl von 7 auf 8 erweitern, damit das PDF-System die neue Seite 1 korrekt verarbeitet.

#### Acceptance Criteria

1. WHEN `pdf_template_engine/dynamic_overlay.py` angepasst wird THEN soll die Hauptschleife von `range(1, 8)` auf `range(1, 9)` erweitert werden
2. WHEN `pdf_template_engine/merger.py` angepasst wird THEN soll die Merge-Funktion von 7 auf 8 Seiten erweitert werden
3. WHEN Koordinaten-Dateien geladen werden THEN sollen die Pfade `coords/seite1.yml` bis `coords/seite8.yml` korrekt aufgelöst werden
4. WHEN PDF-Templates geladen werden THEN sollen die Pfade `nt_nt_01.pdf` bis `nt_nt_08.pdf` korrekt aufgelöst werden
5. WHEN Wärmepumpen-Varianten verwendet werden THEN sollen die Pfade `hp_nt_01.pdf` bis `hp_nt_08.pdf` und `wp_seite1.yml` bis `wp_seite8.yml` korrekt aufgelöst werden

### Requirement 3: Seiten-spezifische Funktionen verschieben

**User Story:** Als System möchte ich seiten-spezifische Funktionen auf die neuen Seitenzahlen mappen, damit die Inhalte auf den korrekten Seiten erscheinen.

#### Acceptance Criteria

1. WHEN `_draw_page1_test_donuts` existiert THEN soll diese Funktion auf die neue Seite 2 verschoben werden (alte Seite 1)
2. WHEN `_draw_page3_waterfall_chart` existiert THEN soll diese Funktion auf die neue Seite 4 verschoben werden (alte Seite 3)
3. WHEN `_draw_page6_storage_donuts_fixed` existiert THEN soll diese Funktion auf die neue Seite 7 verschoben werden (alte Seite 6)
4. WHEN seiten-spezifische Logik in `add_page3_elements` oder ähnlichen Funktionen existiert THEN soll diese auf die neue Seitenzahl +1 verschoben werden
5. WHEN neue Seite 1 spezifische Logik benötigt wird THEN soll eine neue Funktion `_draw_page1_new_content` erstellt werden

### Requirement 4: Koordinaten-Mapping aktualisieren

**User Story:** Als System möchte ich sicherstellen, dass die YML-Koordinaten-Dateien korrekt den PDF-Seiten zugeordnet werden, damit Text an den richtigen Positionen erscheint.

#### Acceptance Criteria

1. WHEN Seite 1 verarbeitet wird THEN sollen die Koordinaten aus `coords/seite1.yml` (neue Seite) verwendet werden
2. WHEN Seite 2 verarbeitet wird THEN sollen die Koordinaten aus `coords/seite2.yml` (alte Seite 1) verwendet werden
3. WHEN Seite 3 verarbeitet wird THEN sollen die Koordinaten aus `coords/seite3.yml` (alte Seite 2) verwendet werden
4. WHEN Seite 8 verarbeitet wird THEN sollen die Koordinaten aus `coords/seite8.yml` (alte Seite 7) verwendet werden
5. IF Wärmepumpen-Modus aktiv ist THEN sollen die entsprechenden `coords_wp/wp_seiteX.yml` Dateien verwendet werden

### Requirement 5: PDF-Template-Mapping aktualisieren

**User Story:** Als System möchte ich sicherstellen, dass die PDF-Template-Dateien korrekt den Seiten zugeordnet werden, damit die Hintergrund-Templates korrekt sind.

#### Acceptance Criteria

1. WHEN Seite 1 verarbeitet wird THEN soll `nt_nt_01.pdf` (neue Seite) als Template verwendet werden
2. WHEN Seite 2 verarbeitet wird THEN soll `nt_nt_02.pdf` (alte Seite 1) als Template verwendet werden
3. WHEN Seite 3 verarbeitet wird THEN soll `nt_nt_03.pdf` (alte Seite 2) als Template verwendet werden
4. WHEN Seite 8 verarbeitet wird THEN soll `nt_nt_08.pdf` (alte Seite 7) als Template verwendet werden
5. IF Wärmepumpen-Modus aktiv ist THEN sollen die entsprechenden `hp_nt_XX.pdf` Dateien verwendet werden

### Requirement 6: Seitennummerierung und Footer aktualisieren

**User Story:** Als Benutzer möchte ich, dass die Seitennummerierung im PDF-Footer korrekt von 1-8 läuft, damit die Seitenzahlen stimmen.

#### Acceptance Criteria

1. WHEN ein PDF generiert wird THEN soll der Footer "Seite 1" bis "Seite 8" anzeigen
2. WHEN die Seitennummerierung berechnet wird THEN soll die maximale Seitenzahl 8 sein
3. WHEN Header/Footer-Logik existiert THEN soll diese für alle 8 Seiten korrekt funktionieren
4. IF spezielle Header/Footer-Regeln für bestimmte Seiten existieren THEN sollen diese auf die neuen Seitenzahlen angepasst werden
5. WHEN Seitenzahlen in Logs oder Debug-Ausgaben erscheinen THEN sollen diese korrekt 1-8 anzeigen

### Requirement 7: Rückwärtskompatibilität und Fehlerbehandlung

**User Story:** Als System möchte ich robust mit fehlenden Dateien umgehen, damit das System nicht abstürzt, wenn alte 7-Seiten-Dateien noch existieren.

#### Acceptance Criteria

1. WHEN eine YML-Datei nicht existiert THEN soll eine aussagekräftige Fehlermeldung ausgegeben werden
2. WHEN ein PDF-Template nicht existiert THEN soll ein Fallback-Mechanismus greifen oder eine klare Fehlermeldung erscheinen
3. WHEN alte 7-Seiten-Konfigurationen noch im System sind THEN sollen diese erkannt und gemeldet werden
4. IF eine Seite keine Koordinaten hat THEN soll die Seite trotzdem generiert werden (ohne Text-Overlay)
5. WHEN Tests existieren, die auf 7 Seiten basieren THEN sollen diese identifiziert und aktualisiert werden

### Requirement 8: Validierung und Testing

**User Story:** Als Entwickler möchte ich sicherstellen, dass alle Änderungen korrekt funktionieren, damit keine Funktionalität verloren geht.

#### Acceptance Criteria

1. WHEN ein 8-seitiges PDF generiert wird THEN sollen alle 8 Seiten korrekt erstellt werden
2. WHEN Text-Overlays angewendet werden THEN sollen diese auf den korrekten Seiten mit korrekten Koordinaten erscheinen
3. WHEN seiten-spezifische Grafiken (Donuts, Wasserfall-Charts) gezeichnet werden THEN sollen diese auf den korrekten neuen Seiten erscheinen
4. WHEN das PDF geöffnet wird THEN sollen alle Seiten in der korrekten Reihenfolge sein (neue Seite 1 zuerst)
5. WHEN bestehende Tests ausgeführt werden THEN sollen diese entweder erfolgreich sein oder klar identifiziert werden als "benötigt Update"

### Requirement 9: Dokumentation der Änderungen

**User Story:** Als zukünftiger Entwickler möchte ich verstehen, welche Änderungen vorgenommen wurden, damit ich das System warten kann.

#### Acceptance Criteria

1. WHEN Code-Änderungen vorgenommen werden THEN sollen aussagekräftige Kommentare hinzugefügt werden
2. WHEN Funktionen umbenannt werden THEN soll die Umbenennung dokumentiert werden
3. WHEN neue Seiten-Logik hinzugefügt wird THEN soll diese klar kommentiert werden
4. IF komplexe Verschiebungen vorgenommen werden THEN soll ein Mapping-Kommentar hinzugefügt werden (z.B. "# OLD: page 3 -> NEW: page 4")
5. WHEN die Implementierung abgeschlossen ist THEN soll eine Zusammenfassung der Änderungen erstellt werden

### Requirement 10: Keine Funktionalitätsverluste

**User Story:** Als Benutzer möchte ich, dass alle bestehenden PDF-Features weiterhin funktionieren, damit keine Regression entsteht.

#### Acceptance Criteria

1. WHEN ein PDF generiert wird THEN sollen alle bisherigen Inhalte (Texte, Grafiken, Charts) weiterhin erscheinen
2. WHEN Firmenlogos eingefügt werden THEN sollen diese weiterhin auf den korrekten Seiten erscheinen
3. WHEN Wasserfall-Diagramme gezeichnet werden THEN sollen diese weiterhin korrekt berechnet und positioniert werden
4. WHEN Donut-Charts gezeichnet werden THEN sollen diese weiterhin korrekt berechnet und positioniert werden
5. WHEN dynamische Daten eingefügt werden THEN sollen diese weiterhin an den korrekten Positionen erscheinen
