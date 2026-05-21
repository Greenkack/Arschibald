# Requirements Document - PV-Modul Platzierung Komplett-Fix

## Introduction

Dieses Dokument definiert die Anforderungen für eine vollständige Überarbeitung der PV-Modul-Platzierungslogik in der 3D-Visualisierung. Das System muss Module korrekt auf Dachflächen platzieren, visualisieren und dem Benutzer intuitive Steuerungsmöglichkeiten bieten.

## Glossary

- **PV-Modul**: Photovoltaik-Modul, das auf Dachflächen platziert wird
- **3D-Szene**: Die Plotly-basierte 3D-Visualisierung des Gebäudes mit Dach und Modulen
- **Grid-Berechnung**: Algorithmus zur Berechnung optimaler Modul-Positionen
- **Automatische Belegung**: System-gesteuerte Platzierung von Modulen
- **Manuelle Belegung**: Benutzer-gesteuerte Platzierung von Modulen
- **Mesh**: 3D-Geometrie-Objekt in Plotly
- **Session State**: Streamlit Session State zur Speicherung von Zuständen
- **Dachtyp**: Art des Dachs (Flachdach, Satteldach, Pultdach, etc.)
- **Aufständerung**: Montagesystem für Module auf Flachdächern mit Neigungswinkel

## Requirements

### Requirement 1: Modul-Sichtbarkeit

**User Story:** Als Benutzer möchte ich platzierte PV-Module in der 3D-Ansicht sehen können, damit ich die Belegung visuell überprüfen kann.

#### Acceptance Criteria

1. WHEN THE System platziert ein Modul, THEN THE 3D-Szene SHALL das Modul als sichtbares 3D-Mesh darstellen
2. THE PV-Modul SHALL eine erkennbare Farbe (dunkelblau oder schwarz) haben
3. THE PV-Modul SHALL die korrekten Dimensionen (1.05m x 1.76m x 0.04m) haben
4. THE PV-Modul SHALL auf der Dachfläche positioniert sein
5. WHEN der Benutzer die 3D-Ansicht dreht, THEN THE PV-Module SHALL aus allen Winkeln sichtbar bleiben

### Requirement 2: Automatische Modul-Platzierung

**User Story:** Als Benutzer möchte ich Module automatisch auf dem Dach platzieren lassen, damit ich schnell eine optimale Belegung erhalte.

#### Acceptance Criteria

1. THE System SHALL einen Button "Automatisch belegen" in der Sidebar bereitstellen
2. WHEN der Benutzer auf "Automatisch belegen" klickt, THEN THE System SHALL Module automatisch auf der Dachfläche platzieren
3. THE System SHALL die maximale Anzahl Module innerhalb der verfügbaren Dachfläche platzieren
4. THE System SHALL Mindestabstände zwischen Modulen (5cm) einhalten
5. THE System SHALL Randabstände (30cm) zur Dachkante einhalten
6. WHEN die Platzierung abgeschlossen ist, THEN THE System SHALL die Anzahl platzierter Module anzeigen

### Requirement 3: Grid-Berechnung

**User Story:** Als System möchte ich optimale Modul-Positionen berechnen, damit Module effizient und ohne Überlappung platziert werden.

#### Acceptance Criteria

1. THE Grid-Berechnung SHALL (x, y) Koordinaten für jedes Modul berechnen
2. THE Grid-Berechnung SHALL die Dachfläche (Länge x Breite) berücksichtigen
3. THE Grid-Berechnung SHALL Modul-Dimensionen (1.05m x 1.76m) berücksichtigen
4. THE Grid-Berechnung SHALL Abstände zwischen Modulen berücksichtigen
5. THE Grid-Berechnung SHALL Randabstände berücksichtigen
6. WHEN die verfügbare Fläche kleiner ist als die gewünschte Modulanzahl, THEN THE Grid-Berechnung SHALL die maximal mögliche Anzahl zurückgeben

### Requirement 4: Manuelle Modul-Steuerung

**User Story:** Als Benutzer möchte ich Module manuell hinzufügen und entfernen können, damit ich die Belegung individuell anpassen kann.

#### Acceptance Criteria

1. THE System SHALL einen Button "Modul hinzufügen" bereitstellen
2. THE System SHALL einen Button "Ausgewählte entfernen" bereitstellen
3. THE System SHALL einen Button "Alle zurücksetzen" bereitstellen
4. WHEN der Benutzer auf "Alle zurücksetzen" klickt, THEN THE System SHALL alle platzierten Module entfernen
5. WHEN Module entfernt werden, THEN THE 3D-Szene SHALL aktualisiert werden

### Requirement 5: Echtzeit-Feedback

**User Story:** Als Benutzer möchte ich jederzeit sehen wie viele Module platziert sind, damit ich den Fortschritt überwachen kann.

#### Acceptance Criteria

1. THE System SHALL die Anzahl gewünschter Module anzeigen
2. THE System SHALL die Anzahl platzierter Module anzeigen
3. THE System SHALL den Belegungsgrad in Prozent anzeigen
4. THE System SHALL einen Fortschrittsbalken anzeigen
5. WHEN Module platziert oder entfernt werden, THEN THE System SHALL die Anzeigen sofort aktualisieren

### Requirement 6: Dachtyp-spezifische Platzierung

**User Story:** Als System möchte ich Module entsprechend dem Dachtyp korrekt platzieren, damit die Visualisierung realistisch ist.

#### Acceptance Criteria

1. WHEN der Dachtyp "Flachdach" ist, THEN THE System SHALL Module mit Aufständerung (30° Neigung) platzieren
2. WHEN der Dachtyp "Satteldach" ist, THEN THE System SHALL Module parallel zur Dachfläche platzieren
3. WHEN der Dachtyp "Pultdach" ist, THEN THE System SHALL Module parallel zur Dachfläche platzieren
4. THE System SHALL die Z-Position (Höhe) basierend auf dem Dachtyp berechnen
5. THE System SHALL die Rotation basierend auf dem Dachtyp berechnen

### Requirement 7: Kollisionsvermeidung

**User Story:** Als System möchte ich Überlappungen zwischen Modulen verhindern, damit die Platzierung physikalisch korrekt ist.

#### Acceptance Criteria

1. THE System SHALL prüfen ob ein Modul mit einem anderen Modul überlappt
2. THE System SHALL prüfen ob ein Modul über die Dachkante hinausragt
3. WHEN eine Kollision erkannt wird, THEN THE System SHALL das Modul nicht platzieren
4. WHEN eine Kollision erkannt wird, THEN THE System SHALL eine Warnung anzeigen

### Requirement 8: UI-Integration

**User Story:** Als Benutzer möchte ich alle Modul-Belegungs-Funktionen in einem übersichtlichen Panel finden, damit die Bedienung einfach ist.

#### Acceptance Criteria

1. THE System SHALL ein Expander-Panel "🔲 Modul-Belegung" in der Sidebar bereitstellen
2. THE Panel SHALL Statistiken (Gewünscht, Platziert, Abdeckung) anzeigen
3. THE Panel SHALL einen Fortschrittsbalken anzeigen
4. THE Panel SHALL alle Steuerungs-Buttons enthalten
5. THE Panel SHALL Optionen (Raster anzeigen, Nummern anzeigen) bereitstellen

### Requirement 9: Session State Management

**User Story:** Als System möchte ich Modul-Positionen im Session State speichern, damit sie zwischen Interaktionen erhalten bleiben.

#### Acceptance Criteria

1. THE System SHALL platzierte Modul-Positionen in `st.session_state["placed_module_positions"]` speichern
2. THE System SHALL die Anzahl platzierter Module in `st.session_state["placed_module_count"]` speichern
3. WHEN die Seite neu geladen wird, THEN THE System SHALL gespeicherte Positionen wiederherstellen
4. WHEN Module zurückgesetzt werden, THEN THE System SHALL den Session State leeren

### Requirement 10: 3D-Rendering Integration

**User Story:** Als System möchte ich platzierte Module korrekt in die 3D-Szene integrieren, damit sie zusammen mit dem Gebäude dargestellt werden.

#### Acceptance Criteria

1. THE System SHALL für jede gespeicherte Position ein 3D-Mesh erstellen
2. THE System SHALL jedes Mesh zur Plotly Figure hinzufügen
3. THE System SHALL Module mit korrekten Transformationen (Position, Rotation) rendern
4. WHEN keine Module platziert sind, THEN THE System SHALL nur das Gebäude rendern
5. THE System SHALL die Rendering-Performance für bis zu 100 Module gewährleisten

### Requirement 11: Fehlerbehandlung

**User Story:** Als System möchte ich Fehler bei der Modul-Platzierung abfangen, damit die Anwendung stabil bleibt.

#### Acceptance Criteria

1. WHEN ein Fehler bei der Grid-Berechnung auftritt, THEN THE System SHALL eine Fehlermeldung anzeigen
2. WHEN ein Fehler beim Rendering auftritt, THEN THE System SHALL eine Fehlermeldung anzeigen
3. THE System SHALL bei Fehlern nicht abstürzen
4. THE System SHALL aussagekräftige Fehlermeldungen bereitstellen
5. THE System SHALL bei Fehlern den vorherigen Zustand beibehalten

### Requirement 12: Keine Regression

**User Story:** Als Entwickler möchte ich sicherstellen dass bestehende Funktionen nicht beeinträchtigt werden, damit die Anwendung stabil bleibt.

#### Acceptance Criteria

1. THE System SHALL alle bestehenden Export-Funktionen unverändert lassen
2. THE System SHALL alle bestehenden WOW-Features unverändert lassen
3. THE System SHALL alle bestehenden 3D-Visualisierungs-Features unverändert lassen
4. THE System SHALL die Performance der Anwendung nicht verschlechtern
5. WHEN neue Funktionen hinzugefügt werden, THEN THE System SHALL bestehende Funktionen nicht überschreiben
