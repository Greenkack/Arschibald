# Requirements Document - 3D PV-Visualisierung: Fixes, Optimierungen & Neue Features

## Introduction

Die 3D-Dachvisualisierung hat kritische Bugs bei der Modulplatzierung auf geneigten Dächern und benötigt Performance-Optimierungen. Zusätzlich sollen bestehende Features verbessert und neue innovative Features hinzugefügt werden, um die Visualisierung auf das nächste Level zu heben.

## Glossary

- **PV-Modul**: Photovoltaik-Modul (Solarpanel)
- **Aufständerung**: Montagegestell für Module auf Flachdächern (erhöht Module um ~30cm)
- **Dachfläche**: Die geneigte Oberfläche eines Schrägdachs
- **Satteldach**: Dach mit zwei geneigten Flächen, die sich am First treffen
- **Flachdach**: Horizontales oder nahezu horizontales Dach
- **Drag & Drop**: Ziehen und Ablegen von Objekten mit der Maus
- **Azimuth**: Horizontaler Winkel (0° = Süd, 90° = West, 180° = Nord, 270° = Ost)
- **Tilt**: Neigungs-Winkel des Moduls (0° = horizontal, 90° = vertikal)

## Requirements

## TEIL A: KRITISCHE BUGFIXES

### Requirement 1: FIX - Korrekte Modulplatzierung auf geneigten Dächern

**User Story:** Als Benutzer möchte ich, dass PV-Module korrekt auf geneigten Dächern (Satteldach, Walmdach, Pultdach) platziert werden, damit die 3D-Visualisierung realistisch ist.

**Problem:** Module werden aktuell wie auf Flachdächern aufgeständert, auch wenn ein Satteldach gewählt wird. Sie erscheinen auf dem Flachdach-Bereich statt auf den geneigten Dachflächen.

#### Acceptance Criteria

1. WHEN ein Satteldach ausgewählt ist, THE System SHALL Module direkt auf die geneigten Dachflächen platzieren (nicht auf das Flachdach darunter)

2. WHEN ein Walmdach ausgewählt ist, THE System SHALL Module parallel zur jeweiligen Dachfläche ausrichten

3. WHEN ein Pultdach ausgewählt ist, THE System SHALL Module mit der Dachneigung ausrichten

4. WHEN ein Flachdach ausgewählt ist, THE System SHALL Module mit Aufständerung (30cm Höhe, 30° Neigung) platzieren

5. WHEN Module auf einem geneigten Dach platziert werden, THE System SHALL die Z-Position basierend auf der Dachgeometrie und Y-Position berechnen

6. WHEN Module platziert werden, THE System SHALL die korrekte Neigung entsprechend dem Dachtyp anwenden

## TEIL B: OPTIMIERUNGEN BESTEHENDER FEATURES

### Requirement 2: OPTIMIERUNG - Sonnenverlauf-Animation

**User Story:** Als Benutzer möchte ich eine flüssigere und realistischere Sonnenverlauf-Animation sehen.

**Bestehend:** Sonnenverlauf-Animation existiert bereits in `utils/solar_animation.py` und `utils/pv3d_wow_features.py`

#### Acceptance Criteria

1. WHEN die Animation läuft, THE System SHALL mindestens 24 Frames pro Sekunde erreichen

2. WHEN die Sonne sich bewegt, THE System SHALL Schatten in Echtzeit aktualisieren

3. THE System SHALL eine Zeitraffer-Funktion bieten (1 Stunde = 1 Sekunde)

4. THE System SHALL die Sonnenposition für jeden Monat des Jahres korrekt berechnen

5. WHEN der Benutzer die Animation pausiert, THE System SHALL die aktuelle Sonnenposition beibehalten

### Requirement 3: OPTIMIERUNG - Verschattungs-Analyse

**User Story:** Als Benutzer möchte ich eine detailliertere und genauere Verschattungs-Analyse sehen.

**Bestehend:** Verschattungs-Analyse existiert bereits in `utils/pv3d_analysis.py`

#### Acceptance Criteria

1. WHEN Verschattung berechnet wird, THE System SHALL zwischen direkter und indirekter Verschattung unterscheiden

2. THE System SHALL Verschattung durch benachbarte Gebäude simulieren können

3. THE System SHALL einen Verschattungs-Verlauf über den Tag als Diagramm anzeigen

4. WHEN ein Modul stark verschattet ist (>60%), THE System SHALL Optimierungsvorschläge machen

5. THE System SHALL die Verschattung für jede Jahreszeit separat berechnen können

### Requirement 4: OPTIMIERUNG - Ertrags-Heatmap

**User Story:** Als Benutzer möchte ich eine präzisere Ertrags-Heatmap mit mehr Metriken sehen.

**Bestehend:** Ertrags-Heatmap existiert bereits in `utils/pv3d_analysis.py`

#### Acceptance Criteria

1. THE System SHALL folgende Metriken in der Heatmap anzeigen können:
   - Jahresertrag (kWh)
   - Monatlicher Durchschnittsertrag
   - Verschattungsverlust (%)
   - ROI (Return on Investment)
   - CO₂-Einsparung pro Modul

2. WHEN der Benutzer über ein Modul hovert, THE System SHALL detaillierte Ertragsdaten anzeigen

3. THE System SHALL eine Vergleichsansicht zwischen verschiedenen Modulpositionen ermöglichen

4. THE System SHALL schwache Module (<50% Ertrag) automatisch markieren

### Requirement 5: VERBESSERUNG - Manuelle Modulplatzierung

**User Story:** Als Benutzer möchte ich Module einfacher und intuitiver manuell platzieren können.

**Bestehend:** Basis-Funktionen existieren in `utils/pv3d_placement_handler.py`

#### Acceptance Criteria

1. WHEN der Benutzer ein Modul auswählt, THE System SHALL das Modul mit einem leuchtenden Rahmen hervorheben

2. THE System SHALL eine "Magnet-Funktion" bieten, die Module automatisch am Raster ausrichtet

3. THE System SHALL eine "Kopieren & Einfügen" Funktion für Modulgruppen bieten

4. WHEN der Benutzer Module verschiebt, THE System SHALL eine Vorschau der neuen Position zeigen

5. THE System SHALL Tastatur-Shortcuts unterstützen:
   - Pfeiltasten: Verschieben (0.5m)
   - Shift + Pfeiltasten: Verschieben (0.1m)
   - R: Rotieren um 90°
   - Delete: Löschen
   - Ctrl+C/V: Kopieren/Einfügen

## TEIL C: NEUE FEATURES (10 Vorschläge zur Auswahl)

### Requirement 6: NEU - Modulfarben & Materialien

**User Story:** Als Benutzer möchte ich verschiedene Modulfarben und Materialien wählen können, um realistische Visualisierungen zu erstellen.

#### Acceptance Criteria

1. THE System SHALL folgende Modulfarben unterstützen:
   - Schwarz (Standard) #1a1a1a
   - Dunkelblau #1a1a2e
   - Dunkelrot #8b0000
   - Anthrazit #2f4f4f
   - Silber #c0c0c0

2. THE System SHALL verschiedene Oberflächen-Materialien simulieren:
   - Matt (Standard)
   - Glänzend (mit Reflexionen)
   - Glas-Glas (transparent)

3. WHEN die Farbe geändert wird, THE System SHALL alle Module sofort aktualisieren

4. THE System SHALL die Farbe pro Modul individuell einstellbar machen

### Requirement 7: NEU - Intelligente Modul-Anordnung mit KI

**User Story:** Als Benutzer möchte ich, dass eine KI die optimale Modulanordnung vorschlägt.

#### Acceptance Criteria

1. WHEN der Benutzer "KI-Optimierung" aktiviert, THE System SHALL 3 verschiedene Layouts vorschlagen:
   - Maximum Ertrag
   - Maximum Anzahl
   - Beste Ästhetik

2. THE System SHALL für jedes Layout eine Bewertung anzeigen (Ertrag, Kosten, Ästhetik)

3. THE System SHALL Hindernisse (Schornstein, Fenster, Gauben) automatisch erkennen und umgehen

4. WHEN der Benutzer ein Layout auswählt, THE System SHALL es mit Animation anwenden

### Requirement 8: NEU - Realistische Wetter-Simulation

**User Story:** Als Benutzer möchte ich sehen, wie die Anlage bei verschiedenen Wetterbedingungen aussieht und performt.

#### Acceptance Criteria

1. THE System SHALL folgende Wetterbedingungen simulieren:
   - Sonnig (Standard)
   - Bewölkt (diffuses Licht)
   - Regen (Wassertropfen auf Modulen)
   - Schnee (Schneebedeckung)
   - Nebel (reduzierte Sichtweite)

2. WHEN Wetter geändert wird, THE System SHALL die Beleuchtung und Schatten anpassen

3. THE System SHALL den Ertragsverlust bei schlechtem Wetter berechnen und anzeigen

4. THE System SHALL eine Jahres-Simulation mit realistischem Wetterverlauf bieten

### Requirement 9: NEU - Zeitraffer-Video-Export

**User Story:** Als Benutzer möchte ich ein Zeitraffer-Video der Sonnenbewegung und Verschattung exportieren können.

#### Acceptance Criteria

1. THE System SHALL Videos in folgenden Formaten exportieren: MP4, GIF, WebM

2. THE System SHALL folgende Zeitraffer-Modi anbieten:
   - Tagesverlauf (24 Stunden in 30 Sekunden)
   - Jahresverlauf (12 Monate in 60 Sekunden)
   - Benutzerdefiniert

3. THE System SHALL Auflösungen von 720p, 1080p und 4K unterstützen

4. WHEN das Video exportiert wird, THE System SHALL einen Fortschrittsbalken anzeigen

5. THE System SHALL Text-Overlays mit Datum, Uhrzeit und Ertragsdaten hinzufügen können

### Requirement 10: NEU - Vergleichs-Modus (Side-by-Side)

**User Story:** Als Benutzer möchte ich zwei verschiedene Konfigurationen nebeneinander vergleichen können.

#### Acceptance Criteria

1. THE System SHALL zwei 3D-Ansichten nebeneinander anzeigen können

2. WHEN der Benutzer in einer Ansicht navigiert, THE System SHALL die andere Ansicht synchronisieren

3. THE System SHALL Unterschiede zwischen den Konfigurationen farblich hervorheben

4. THE System SHALL eine Vergleichstabelle mit Kennzahlen anzeigen:
   - Modulanzahl
   - Gesamtertrag
   - Kosten
   - ROI
   - CO₂-Einsparung

### Requirement 11: NEU - Interaktive Gebäude-Umgebung

**User Story:** Als Benutzer möchte ich die Umgebung des Gebäudes (Bäume, Nachbargebäude) hinzufügen können.

#### Acceptance Criteria

1. THE System SHALL eine Bibliothek mit 3D-Objekten bereitstellen:
   - Bäume (verschiedene Arten und Größen)
   - Nachbargebäude (verschiedene Höhen)
   - Schornsteine
   - Antennen
   - Solaranlagen auf Nachbardächern

2. WHEN Objekte hinzugefügt werden, THE System SHALL deren Verschattung auf die Module berechnen

3. THE System SHALL Objekte per Drag & Drop platzierbar machen

4. THE System SHALL die Höhe und Größe von Objekten anpassbar machen

### Requirement 12: NEU - Echtzeit-Kollaboration

**User Story:** Als Benutzer möchte ich die 3D-Visualisierung mit Kollegen in Echtzeit teilen und gemeinsam bearbeiten.

#### Acceptance Criteria

1. THE System SHALL einen Share-Link generieren, der zur Live-Session führt

2. WHEN mehrere Benutzer verbunden sind, THE System SHALL deren Cursor-Positionen anzeigen

3. THE System SHALL Änderungen in Echtzeit an alle Teilnehmer übertragen

4. THE System SHALL einen Chat für Kommentare und Diskussionen bieten

5. THE System SHALL Änderungen mit Benutzer-Namen und Zeitstempel protokollieren

