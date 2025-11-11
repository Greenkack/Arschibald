# Modul-Belegung Komplett-Fix - Task Liste

## Übersicht

Vollständige Überarbeitung der Modul-Platzierungs-Logik für die 3D-Visualisierung.

**Hauptprobleme:**
- Module werden nicht auf Dachflächen platziert
- Module sind nicht sichtbar
- Automatische Belegung funktioniert nicht
- Manuelle Belegung funktioniert nicht
- Fehlende Buttons für Funktionen

## Tasks

- [x] 1. Diagnose und Analyse





  - Identifiziere alle Probleme in der Modul-Platzierungs-Logik
  - Prüfe `utils/pv3d_plotly.py` auf Fehler
  - Prüfe `utils/pv3d.py` auf Fehler
  - Analysiere Modul-Sichtbarkeit
  - _Requirements: Alle_

- [x] 2. Modul-Rendering reparieren




  - [x] 2.1 Modul-Geometrie korrigieren


    - Stelle sicher dass Module als 3D-Meshes erstellt werden
    - Korrigiere Modul-Dimensionen (PV_W, PV_H, PV_T)
    - Füge sichtbare Farben hinzu
    - _Requirements: Module müssen sichtbar sein_
  

  - [x] 2.2 Modul-Positionierung korrigieren

    - Berechne korrekte X, Y, Z Koordinaten
    - Berücksichtige Dachtyp (Flach vs. Schrägdach)
    - Berücksichtige Aufständerung
    - _Requirements: Module auf Dachfläche_
  

  - [x] 2.3 Modul-Rotation korrigieren

    - Implementiere korrekte Rotation für Schrägdächer
    - Implementiere Aufständerungs-Winkel für Flachdächer
    - Teste alle Dachtypen
    - _Requirements: Module folgen Dachneigung_

- [ ] 3. Automatische Belegung reparieren
  - [ ] 3.1 Grid-Berechnung korrigieren
    - Implementiere `calculate_grid_positions()` neu
    - Berücksichtige Dachfläche
    - Berücksichtige Abstände zwischen Modulen
    - Vermeide Überlappungen
    - _Requirements: Automatische Platzierung funktioniert_
  
  - [ ] 3.2 Platzierungs-Algorithmus optimieren
    - Maximiere Modulanzahl auf verfügbarer Fläche
    - Berücksichtige Verschattung
    - Berücksichtige Randabstände
    - _Requirements: Optimale Belegung_
  
  - [ ] 3.3 Button "Automatisch belegen" hinzufügen
    - Erstelle Button in Sidebar
    - Implementiere Click-Handler
    - Zeige Fortschritt an
    - Zeige Ergebnis (Anzahl platzierter Module)
    - _Requirements: Benutzerfreundlichkeit_

- [ ] 4. Manuelle Belegung reparieren
  - [ ] 4.1 Modul-Auswahl implementieren
    - Click auf Modul wählt es aus
    - Mehrfachauswahl mit Ctrl
    - Visuelle Hervorhebung ausgewählter Module
    - _Requirements: Interaktive Auswahl_
  
  - [ ] 4.2 Modul-Manipulation implementieren
    - Button "Modul hinzufügen"
    - Button "Modul entfernen"
    - Button "Modul verschieben"
    - Button "Modul drehen"
    - _Requirements: Manuelle Kontrolle_
  
  - [ ] 4.3 Drag & Drop implementieren
    - Ziehe Modul an neue Position
    - Zeige Vorschau während Drag
    - Snap-to-Grid Funktion
    - _Requirements: Intuitive Bedienung_

- [ ] 5. UI-Verbesserungen
  - [ ] 5.1 Modul-Belegungs-Panel erstellen
    - Neuer Expander "🔲 Modul-Belegung"
    - Zeige Statistiken (platziert/gesamt)
    - Zeige Belegungsgrad in %
    - _Requirements: Übersichtlichkeit_
  
  - [ ] 5.2 Buttons hinzufügen
    - "🎯 Automatisch belegen" Button
    - "➕ Modul hinzufügen" Button
    - "➖ Ausgewählte entfernen" Button
    - "🔄 Alle zurücksetzen" Button
    - "↻ Rückgängig" Button
    - _Requirements: Alle Funktionen zugänglich_
  
  - [ ] 5.3 Echtzeit-Feedback
    - Zeige Anzahl platzierter Module
    - Zeige verfügbare Fläche
    - Zeige Warnungen bei Problemen
    - _Requirements: Transparenz_

- [ ] 6. Dachtyp-spezifische Logik
  - [ ] 6.1 Flachdach-Belegung
    - Aufständerung berücksichtigen
    - Reihenabstände berechnen
    - Verschattung zwischen Reihen vermeiden
    - _Requirements: Flachdach-Optimierung_
  
  - [ ] 6.2 Schrägdach-Belegung
    - Module parallel zur Dachfläche
    - Keine Aufständerung
    - Dachneigung berücksichtigen
    - _Requirements: Schrägdach-Optimierung_
  
  - [ ] 6.3 Satteldach-Belegung
    - Beide Dachseiten belegen
    - First-Bereich freilassen
    - Symmetrische Belegung
    - _Requirements: Satteldach-Optimierung_

- [ ] 7. Kollisionserkennung
  - [ ] 7.1 Modul-Modul Kollision
    - Erkenne Überlappungen
    - Verhindere Platzierung bei Kollision
    - Zeige Warnung
    - _Requirements: Keine Überlappungen_
  
  - [ ] 7.2 Modul-Dach Kollision
    - Erkenne wenn Modul über Dachrand hinausragt
    - Verhindere ungültige Platzierung
    - Zeige Warnung
    - _Requirements: Module bleiben auf Dach_

- [ ] 8. Visualisierungs-Verbesserungen
  - [ ] 8.1 Modul-Farben
    - Normale Module: Dunkelblau
    - Ausgewählte Module: Hellblau/Gelb
    - Ungültige Position: Rot
    - _Requirements: Visuelle Klarheit_
  
  - [ ] 8.2 Modul-Details
    - Zeige Modul-Nummer
    - Zeige Leistung (W)
    - Zeige Ausrichtung (Azimut)
    - _Requirements: Informationsgehalt_
  
  - [ ] 8.3 Gitter-Overlay
    - Zeige Platzierungs-Raster
    - Hilfslinien für Ausrichtung
    - Toggle Ein/Aus
    - _Requirements: Platzierungs-Hilfe_

- [ ] 9. Performance-Optimierung
  - [ ] 9.1 Lazy Loading
    - Lade nur sichtbare Module
    - Reduziere Mesh-Komplexität
    - _Requirements: Schnelle Darstellung_
  
  - [ ] 9.2 Caching
    - Cache berechnete Positionen
    - Cache Mesh-Geometrie
    - _Requirements: Flüssige Interaktion_

- [ ] 10. Testing und Validierung
  - [ ] 10.1 Unit Tests
    - Teste Grid-Berechnung
    - Teste Kollisionserkennung
    - Teste Positionierung
    - _Requirements: Zuverlässigkeit_
  
  - [ ] 10.2 Integrationstests
    - Teste alle Dachtypen
    - Teste automatische Belegung
    - Teste manuelle Belegung
    - _Requirements: Vollständige Funktionalität_
  
  - [ ] 10.3 UI-Tests
    - Teste alle Buttons
    - Teste Interaktionen
    - Teste Feedback
    - _Requirements: Benutzerfreundlichkeit_

## Prioritäten

**Kritisch (Sofort):**
1. Task 2: Modul-Rendering reparieren
2. Task 3: Automatische Belegung reparieren
3. Task 5.2: Buttons hinzufügen

**Hoch (Bald):**
4. Task 4: Manuelle Belegung reparieren
5. Task 6: Dachtyp-spezifische Logik
6. Task 7: Kollisionserkennung

**Mittel (Später):**
7. Task 8: Visualisierungs-Verbesserungen
8. Task 9: Performance-Optimierung

**Niedrig (Optional):**
9. Task 10: Testing und Validierung

## Erfolgskriterien

✅ Module sind auf Dachflächen sichtbar
✅ Automatische Belegung funktioniert mit einem Button-Klick
✅ Manuelle Belegung funktioniert mit Buttons
✅ Alle Dachtypen werden korrekt unterstützt
✅ Keine Überlappungen oder Kollisionen
✅ Benutzerfreundliche UI mit klaren Buttons
✅ Echtzeit-Feedback über Belegungsstatus
✅ Keine negativen Auswirkungen auf bestehende Funktionen
