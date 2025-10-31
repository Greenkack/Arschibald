# Requirements Document: 3D PV-Visualisierung

## Introduction

Dieses Dokument definiert die Anforderungen für ein vollständig integriertes, dynamisches 3D-Visualisierungstool zur Photovoltaik-Planung in der Streamlit-App "Arschibald". Das Tool ermöglicht die realistische Darstellung von Gebäuden mit verschiedenen Dachformen und die interaktive Platzierung von PV-Modulen. Alle Eingaben aus der Bedarfsanalyse und dem Solarkalkulator werden dynamisch übernommen, um ein individuelles 3D-Modell zu generieren.

## Glossary

- **System**: Das 3D-Visualisierungstool für PV-Planung
- **Benutzer**: Der Anwender der Streamlit-App (Berater oder Endkunde)
- **PV-Modul**: Photovoltaik-Solarmodul mit Standardmaßen (1.05m × 1.76m × 0.04m)
- **Dachfläche**: Die für PV-Module nutzbare Oberfläche des Gebäudes
- **Belegungsmodus**: Automatische oder manuelle Platzierung von PV-Modulen
- **PyVista**: Python-Bibliothek für 3D-Visualisierung basierend auf VTK
- **stpyvista**: Streamlit-Komponente zur Integration von PyVista
- **Plotter**: PyVista-Objekt zur Verwaltung der 3D-Szene
- **Mesh**: 3D-Geometrie-Objekt (Gebäude, Dach, Module)
- **Session State**: Streamlit-Mechanismus zur Speicherung von Zustandsdaten
- **project_data**: Datenstruktur mit Projektinformationen aus der Bedarfsanalyse
- **analysis_results**: Datenstruktur mit Berechnungsergebnissen aus dem Solarkalkulator
- **Aufständerung**: Montagesystem für PV-Module auf Flachdächern
- **Off-Screen Rendering**: Bildgenerierung ohne sichtbares Fenster für PDF-Export
- **ReportLab**: Python-Bibliothek zur PDF-Generierung

## Requirements

### Requirement 1: Dynamische 3D-Gebäudemodellierung

**User Story:** Als Benutzer möchte ich, dass das System automatisch ein 3D-Modell meines Gebäudes basierend auf meinen Eingaben erstellt, damit ich eine realistische Darstellung erhalte.

#### Acceptance Criteria

1. WHEN der Benutzer die 3D-Visualisierung aktiviert, THE System SHALL ein 3D-Gebäudemodell basierend auf den Werten aus project_data["project_details"] generieren
2. THE System SHALL die Gebäudeart (Einfamilienhaus, Mehrfamilienhaus, Wohnblock) aus project_data auslesen und entsprechende Standardmaße anwenden
3. THE System SHALL die Gebäudedimensionen (Länge, Breite, Traufhöhe) aus Benutzereingaben oder Standardwerten ableiten
4. THE System SHALL editierbare Eingabefelder für Gebäudelänge (8.0-60.0m), Gebäudebreite (5.0-40.0m) und Traufhöhe (3.0-20.0m) bereitstellen
5. WHEN Gebäudedimensionen geändert werden, THE System SHALL das 3D-Modell neu generieren

### Requirement 2: Unterstützung verschiedener Dachformen

**User Story:** Als Benutzer möchte ich, dass das System meine gewählte Dachform korrekt darstellt, damit die Visualisierung meinem realen Gebäude entspricht.

#### Acceptance Criteria

1. THE System SHALL folgende Dachformen unterstützen: Flachdach, Satteldach, Walmdach, Krüppelwalmdach, Pultdach, Zeltdach, Sonstiges
2. WHEN der Benutzer eine Dachform aus project_data["project_details"]["roof_type"] auswählt, THE System SHALL die entsprechende 3D-Geometrie generieren
3. THE System SHALL die Dachneigung aus project_data["project_details"]["roof_inclination_deg"] auslesen und auf die Dachgeometrie anwenden
4. THE System SHALL für Flachdächer eine horizontale Dachfläche mit minimaler Dicke (0.12m) erstellen
5. THE System SHALL für Satteldächer zwei geneigte Dachflächen mit First entlang der Längsachse erstellen
6. THE System SHALL für Walmdächer vier geneigte Dachflächen mit zentralem Gipfel erstellen
7. THE System SHALL für Pultdächer eine einzelne geneigte Dachfläche erstellen
8. THE System SHALL für Zeltdächer pyramidenförmige Dachflächen zum zentralen Punkt erstellen

### Requirement 3: Dachdeckung und Farbdarstellung

**User Story:** Als Benutzer möchte ich, dass das System meine gewählte Dachdeckung farblich korrekt darstellt, damit ich das Material visuell erkenne.

#### Acceptance Criteria

1. THE System SHALL die Dachdeckung aus project_data["project_details"]["roof_covering_type"] auslesen
2. THE System SHALL für Ziegel-Dachdeckung die Farbe #c96a2d (orange-rötlich) verwenden
3. THE System SHALL für Beton-Dachdeckung die Farbe #9ea3a8 (grau) verwenden
4. THE System SHALL für Schiefer-Dachdeckung die Farbe #3b3f44 (dunkelgrau) verwenden
5. THE System SHALL für Eternit-Dachdeckung die Farbe #7e8388 (mittelgrau) verwenden
6. THE System SHALL für Trapezblech-Dachdeckung die Farbe #8e8f93 (hellgrau) verwenden
7. THE System SHALL für Bitumen-Dachdeckung die Farbe #4a4d52 (dunkelgrau) verwenden
8. WHEN keine passende Dachdeckung gefunden wird, THE System SHALL die Standardfarbe #b0b5ba verwenden

### Requirement 4: Gebäudeausrichtung und Kompass

**User Story:** Als Benutzer möchte ich die Ausrichtung meines Gebäudes sehen, damit ich die Himmelsrichtung der Dachflächen verstehe.

#### Acceptance Criteria

1. THE System SHALL die Gebäudeausrichtung aus project_data["project_details"]["roof_orientation"] auslesen
2. THE System SHALL das gesamte Gebäudemodell entsprechend der Ausrichtung (Süd, Ost, West, Nord) rotieren
3. THE System SHALL einen roten Kompass-Pfeil im 3D-Modell platzieren, der nach Norden zeigt
4. THE System SHALL den Kompass-Pfeil an Position (Länge*1.6, Breite*1.6, 0.1m) mit Richtung (0, -1, 0) und Skalierung 1.5 darstellen
5. WHEN die Ausrichtung "Süd" ist, THE System SHALL das Gebäude um 0° drehen
6. WHEN die Ausrichtung "Ost" ist, THE System SHALL das Gebäude um -90° drehen
7. WHEN die Ausrichtung "West" ist, THE System SHALL das Gebäude um 90° drehen
8. WHEN die Ausrichtung "Nord" ist, THE System SHALL das Gebäude um 180° drehen

### Requirement 5: Automatische PV-Modul-Belegung

**User Story:** Als Benutzer möchte ich, dass das System automatisch PV-Module auf meinem Dach platziert, damit ich schnell eine Belegung sehe.

#### Acceptance Criteria

1. THE System SHALL die Modulanzahl aus analysis_results["module_quantity"] oder project_data["module_quantity"] auslesen
2. WHEN der Belegungsmodus "Automatisch" ist, THE System SHALL PV-Module in einem gleichmäßigen Raster auf der Dachfläche platzieren
3. THE System SHALL PV-Module mit Standardmaßen (Breite: 1.05m, Höhe: 1.76m, Dicke: 0.04m) erstellen
4. THE System SHALL PV-Module in schwarzer Farbe (#000000) darstellen
5. THE System SHALL die nutzbare Dachfläche unter Berücksichtigung von Randabständen (0.25m) berechnen
6. THE System SHALL Module in Reihen und Spalten anordnen mit Abstand von 0.25m zwischen Modulen
7. WHEN die Dachfläche nicht ausreicht, THE System SHALL eine Warnung anzeigen
8. THE System SHALL bei geneigten Dächern Module parallel zur Dachfläche platzieren

### Requirement 6: Manuelle PV-Modul-Belegung

**User Story:** Als Benutzer möchte ich einzelne Module manuell entfernen oder hinzufügen können, damit ich die Belegung an spezifische Anforderungen anpassen kann.

#### Acceptance Criteria

1. THE System SHALL einen Umschalter zwischen "Automatisch" und "Manuell" Belegungsmodus bereitstellen
2. WHEN der Belegungsmodus "Manuell" ist, THE System SHALL ein Eingabefeld für zu entfernende Modul-Indizes bereitstellen
3. THE System SHALL Modul-Indizes im Format "0,1,2" (komma-separiert, 0-basiert) akzeptieren
4. WHEN Modul-Indizes eingegeben werden, THE System SHALL die entsprechenden Module aus der Visualisierung entfernen
5. THE System SHALL die Anzahl platzierter Module in Echtzeit anzeigen
6. THE System SHALL die Anzahl fehlender Module berechnen und anzeigen
7. WHEN ungültige Indizes eingegeben werden, THE System SHALL eine Warnung anzeigen

### Requirement 7: Flachdach-Aufständerung

**User Story:** Als Benutzer möchte ich zwischen Süd- und Ost-West-Aufständerung für Flachdächer wählen können, damit ich verschiedene Montagesysteme visualisieren kann.

#### Acceptance Criteria

1. WHEN die Dachform "Flachdach" ist, THE System SHALL ein Auswahlfeld für Aufständerungstyp bereitstellen
2. THE System SHALL die Optionen "Süd" und "Ost-West" für Aufständerung anbieten
3. WHEN "Süd" Aufständerung gewählt ist, THE System SHALL alle Module mit 15° Neigung nach Süden ausrichten
4. WHEN "Ost-West" Aufständerung gewählt ist, THE System SHALL Module alternierend mit 10° Neigung nach Osten und Westen ausrichten
5. THE System SHALL bei Ost-West-Aufständerung Module paarweise anordnen
6. THE System SHALL den Reihenabstand entsprechend der Aufständerungsart anpassen

### Requirement 8: Garage als zusätzliche Fläche

**User Story:** Als Benutzer möchte ich eine Garage hinzufügen können, wenn das Hauptdach nicht ausreicht, damit ich alle gewünschten Module unterbringen kann.

#### Acceptance Criteria

1. THE System SHALL eine Checkbox "Garage/Carport automatisch hinzufügen" bereitstellen
2. WHEN die Checkbox aktiviert ist UND Module nicht auf dem Hauptdach passen, THE System SHALL ein Garagengebäude zum 3D-Modell hinzufügen
3. THE System SHALL die Garage mit Standardmaßen (Länge: 6.0m, Breite: 3.0m, Höhe: 3.0m) erstellen
4. THE System SHALL die Garage an Position (Gebäudelänge + 1.0m, 0.0m, 0.0m) platzieren
5. THE System SHALL ein Flachdach auf der Garage erstellen
6. THE System SHALL verbleibende Module auf dem Garagendach platzieren
7. THE System SHALL die Garage in Farbe #ececee (hellgrau) darstellen
8. THE System SHALL die Anzahl der auf der Garage platzierten Module anzeigen

### Requirement 9: Fassadenbelegung

**User Story:** Als Benutzer möchte ich Module an der Fassade anbringen können, wenn Dach und Garage nicht ausreichen, damit ich alle Module unterbringen kann.

#### Acceptance Criteria

1. THE System SHALL eine Checkbox "Fassadenbelegung aktivieren" bereitstellen
2. WHEN die Checkbox aktiviert ist UND Module nicht auf Dach und Garage passen, THE System SHALL Module an der Südfassade platzieren
3. THE System SHALL Module vertikal (90° Neigung) an der Fassade ausrichten
4. THE System SHALL Module in Reihen und Spalten an der Fassade anordnen
5. THE System SHALL die Anzahl der Fassadenmodule basierend auf verfügbarer Wandfläche berechnen
6. THE System SHALL Fassadenmodule mit Abstand von 0.25m zwischen Modulen platzieren
7. THE System SHALL die Anzahl der an der Fassade platzierten Module anzeigen

### Requirement 10: Interaktive 3D-Navigation

**User Story:** Als Benutzer möchte ich das 3D-Modell frei drehen, zoomen und verschieben können, damit ich alle Details aus verschiedenen Perspektiven betrachten kann.

#### Acceptance Criteria

1. THE System SHALL einen interaktiven 3D-Viewer mit stpyvista bereitstellen
2. THE System SHALL Orbit-Steuerung (Rotation mit linker Maustaste) ermöglichen
3. THE System SHALL Zoom-Steuerung (Mausrad) ermöglichen
4. THE System SHALL Pan-Steuerung (Verschieben mit rechter Maustaste) ermöglichen
5. THE System SHALL eine isometrische Standardperspektive beim Laden einstellen
6. THE System SHALL einen weißen Hintergrund für den 3D-Viewer verwenden
7. THE System SHALL eine Bodenplatte (Länge*3, Breite*3, Dicke: 0.05m) in Farbe #f3f3f5 darstellen

### Requirement 11: Layout-Speicherung und -Wiederherstellung

**User Story:** Als Benutzer möchte ich mein 3D-Layout speichern und später wieder laden können, damit ich meine Arbeit nicht verliere.

#### Acceptance Criteria

1. THE System SHALL einen "Layout speichern" Button bereitstellen
2. WHEN der "Layout speichern" Button geklickt wird, THE System SHALL die aktuelle Konfiguration in st.session_state["pv3d_layout_json"] speichern
3. THE System SHALL folgende Parameter speichern: Belegungsmodus, Garage-Status, Fassaden-Status, entfernte Modul-Indizes, Garage-Dimensionen
4. THE System SHALL einen "Layout laden" Button bereitstellen
5. WHEN der "Layout laden" Button geklickt wird, THE System SHALL die Konfiguration aus st.session_state["pv3d_layout_json"] wiederherstellen
6. THE System SHALL die Konfiguration im JSON-Format speichern
7. WHEN das Laden fehlschlägt, THE System SHALL eine Fehlermeldung anzeigen

### Requirement 12: Reset-Funktionalität

**User Story:** Als Benutzer möchte ich alle manuellen Änderungen zurücksetzen können, damit ich schnell zur automatischen Belegung zurückkehren kann.

#### Acceptance Criteria

1. THE System SHALL einen "Reset (Auto-Belegung)" Button bereitstellen
2. WHEN der "Reset" Button geklickt wird, THE System SHALL den Belegungsmodus auf "auto" setzen
3. WHEN der "Reset" Button geklickt wird, THE System SHALL alle entfernten Modul-Indizes löschen
4. WHEN der "Reset" Button geklickt wird, THE System SHALL Garage und Fassade deaktivieren
5. WHEN der "Reset" Button geklickt wird, THE System SHALL das 3D-Modell mit Standardeinstellungen neu generieren
6. WHEN der "Reset" Button geklickt wird, THE System SHALL eine Erfolgsmeldung anzeigen

### Requirement 13: Screenshot-Export

**User Story:** Als Benutzer möchte ich einen Screenshot der 3D-Visualisierung erstellen können, damit ich das Bild speichern oder teilen kann.

#### Acceptance Criteria

1. THE System SHALL einen "Screenshot (PNG) erzeugen" Button bereitstellen
2. WHEN der Screenshot-Button geklickt wird, THE System SHALL ein Off-Screen Rendering mit PyVista durchführen
3. THE System SHALL das Screenshot in Auflösung 1600x1000 Pixel erstellen
4. THE System SHALL eine isometrische Kameraperspektive für den Screenshot verwenden
5. THE System SHALL das Screenshot im PNG-Format generieren
6. THE System SHALL einen Download-Button für das PNG-Bild bereitstellen
7. WHEN das Rendering fehlschlägt, THE System SHALL eine Fehlermeldung anzeigen

### Requirement 14: 3D-Modell-Export

**User Story:** Als Benutzer möchte ich das 3D-Modell als Datei exportieren können, damit ich es in anderer Software verwenden kann.

#### Acceptance Criteria

1. THE System SHALL einen "STL exportieren" Button bereitstellen
2. WHEN der STL-Export-Button geklickt wird, THE System SHALL das 3D-Modell im STL-Format exportieren
3. THE System SHALL einen Download-Button für die STL-Datei bereitstellen
4. THE System SHALL einen "glTF (.glb) exportieren" Button bereitstellen
5. WHEN der glTF-Export-Button geklickt wird, THE System SHALL das 3D-Modell im glTF-Format exportieren
6. THE System SHALL einen Download-Button für die glTF-Datei bereitstellen
7. THE System SHALL alle Meshes (Gebäude, Dach, Module) im Export zusammenführen

### Requirement 15: PDF-Integration

**User Story:** Als Benutzer möchte ich, dass die 3D-Visualisierung automatisch in mein PDF-Angebot eingefügt wird, damit der Kunde eine visuelle Darstellung erhält.

#### Acceptance Criteria

1. THE System SHALL eine Funktion render_image_bytes() bereitstellen, die PNG-Bytes für PDF-Einbettung generiert
2. THE System SHALL eine Funktion make_pv3d_image_flowable() bereitstellen, die ein ReportLab Image-Objekt erstellt
3. THE System SHALL das 3D-Bild mit Standardbreite 17cm im PDF einfügen
4. THE System SHALL das Seitenverhältnis 16:10 für das PDF-Bild verwenden
5. THE System SHALL Off-Screen Rendering für PDF-Bilder verwenden
6. WHEN das Rendering fehlschlägt, THE System SHALL None zurückgeben ohne das PDF zu blockieren
7. THE System SHALL die PDF-Integration über pdf_visual_inject.py Modul bereitstellen

### Requirement 16: Status-Anzeige

**User Story:** Als Benutzer möchte ich sehen, wie viele Module platziert wurden und wie viele noch fehlen, damit ich den Fortschritt verfolgen kann.

#### Acceptance Criteria

1. THE System SHALL die Anzahl gewählter Module anzeigen
2. THE System SHALL die Anzahl platzierter Module berechnen und anzeigen
3. THE System SHALL die Anzahl fehlender Module berechnen und anzeigen
4. THE System SHALL die geschätzte Dachkapazität basierend auf Gebäudedimensionen berechnen
5. WHEN Module fehlen, THE System SHALL eine Warnung mit Hinweis auf Garage/Fassade anzeigen
6. WHEN alle Module platziert sind, THE System SHALL eine Erfolgsmeldung anzeigen
7. THE System SHALL die Status-Anzeige in Echtzeit aktualisieren

### Requirement 17: Fehlerbehandlung und Stabilität

**User Story:** Als Benutzer möchte ich, dass das System robust läuft und Fehler abfängt, damit die App nicht abstürzt.

#### Acceptance Criteria

1. THE System SHALL alle 3D-Rendering-Operationen in try-except Blöcken kapseln
2. WHEN ein Rendering-Fehler auftritt, THE System SHALL eine benutzerfreundliche Fehlermeldung anzeigen
3. WHEN ungültige Eingabewerte erkannt werden, THE System SHALL Standardwerte verwenden
4. THE System SHALL PyVista Plotter nach Verwendung mit close() freigeben
5. THE System SHALL Memory Leaks durch korrektes Ressourcen-Management vermeiden
6. WHEN project_data fehlt oder ungültig ist, THE System SHALL Fallback-Werte verwenden
7. THE System SHALL die restliche App-Funktionalität bei 3D-Fehlern nicht beeinträchtigen

### Requirement 18: Performance-Optimierung

**User Story:** Als Benutzer möchte ich, dass die 3D-Visualisierung flüssig läuft, damit ich ohne Verzögerungen arbeiten kann.

#### Acceptance Criteria

1. THE System SHALL die Anzahl der Polygone durch Mesh-Zusammenführung minimieren
2. THE System SHALL Geometrie-Berechnungen in unter 1 Sekunde durchführen
3. THE System SHALL WebGL-Rendering im Browser nutzen
4. THE System SHALL unnötige Neuberechnungen durch Caching vermeiden
5. THE System SHALL die 3D-Szene nur bei Benutzerinteraktion aktualisieren
6. THE System SHALL maximal 100 separate Mesh-Objekte gleichzeitig darstellen
7. THE System SHALL einfache Beleuchtung ohne aufwändige Shader verwenden

### Requirement 19: Datenintegration

**User Story:** Als Benutzer möchte ich, dass das System alle relevanten Daten aus der App übernimmt, damit ich keine Werte doppelt eingeben muss.

#### Acceptance Criteria

1. THE System SHALL Daten aus st.session_state["project_data"] auslesen
2. THE System SHALL Daten aus st.session_state["analysis_results"] auslesen
3. THE System SHALL robuste Fallbacks für fehlende Datenschlüssel implementieren
4. THE System SHALL die Funktion _safe_get_orientation() für Ausrichtung verwenden
5. THE System SHALL die Funktion _safe_get_roof_inclination_deg() für Dachneigung verwenden
6. THE System SHALL die Funktion _safe_get_roof_covering() für Dachdeckung verwenden
7. THE System SHALL mit verschiedenen Datenstruktur-Varianten kompatibel sein

### Requirement 20: Benutzeroberfläche und Bedienbarkeit

**User Story:** Als Benutzer möchte ich eine intuitive Benutzeroberfläche, damit ich das Tool einfach bedienen kann.

#### Acceptance Criteria

1. THE System SHALL alle Einstellungen in der Streamlit-Sidebar gruppieren
2. THE System SHALL beschriftete Eingabefelder mit sinnvollen Standardwerten bereitstellen
3. THE System SHALL Buttons mit klaren, deutschen Beschriftungen versehen
4. THE System SHALL den 3D-Viewer in der Hauptspalte mit 60% Breite anzeigen
5. THE System SHALL Status und Aktionen in der Nebenspalte mit 40% Breite anzeigen
6. THE System SHALL Erfolgsmeldungen in grün und Warnungen in orange/rot anzeigen
7. THE System SHALL eine Hilfe-Sektion mit Datenquellen-Erklärung bereitstellen
