# Implementation Plan: 3D PV-Visualisierung - Kritische Bugfixes

## Übersicht

Dieser Plan beschreibt die schrittweise Behebung von vier kritischen Bugs im 3D-Visualisierungssystem. Jeder Task ist fokussiert und baut auf den vorherigen auf.

## Tasks

- [x] 1. Fix Grid-Positionierung für exakte Modulanzahl


  - Korrigiere calculate_grid_positions() in utils/pv3d_plotly.py
  - Implementiere korrekte Berechnung: max_modules_x und max_modules_y
  - Implementiere optimales Layout-Algorithmus für gewünschte Anzahl
  - Implementiere Zentrierung des Grids auf Dachfläche
  - Füge Logging hinzu: gewünschte vs. platzierte Anzahl
  - Füge Warnung hinzu wenn nicht genug Platz
  - Teste mit verschiedenen Dachgrößen und Modulanzahlen
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_



- [x] 2. Fix Modul-Aufständerung auf geneigten Dächern





  - Korrigiere create_pv_module_3d() in utils/pv3d_plotly.py
  - Füge roof_type Parameter hinzu
  - Implementiere Mounting Height Berechnung basierend auf Dachform und Neigung
  - Setze Mounting Height für Satteldach: min(0.3m, neigung/90 * 0.5m)
  - Setze Mounting Height für Walmdach: min(0.3m, neigung/90 * 0.5m)
  - Setze Mounting Height für Pultdach: min(0.3m, neigung/90 * 0.5m)
  - Setze Mounting Height für Zeltdach: min(0.3m, neigung/90 * 0.5m)
  - Setze Mounting Height für Krüppelwalmdach: min(0.3m, neigung/90 * 0.5m)
  - Erhöhe Z-Position um Mounting Height
  - Füge Logging hinzu: Dachform, Neigung, Mounting Height, Z-Position

  - Teste mit allen Dachformen


  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_
-

- [x] 3. Implementiere Optimierungs-Assistent





  - [x] 3.1 Implementiere optimize_layout() Funktion in utils/pv3d.py



    - Erstelle Funktion mit Parametern: building_dims, target_modules, roof_type, optimization_goal
    - Generiere Strategie 1: Süd-Aufständerung (mounting_mode="south")
    - Generiere Strategie 2: Ost-West-Aufständerung (mounting_mode="east-west")
    - Generiere Strategie 3: Süd-Ost-Aufständerung (mounting_mode="south-east")
    - Generiere Strategie 4: Gemischt mit Garage und Fassade
    - Bewerte jede Strategie mit evaluate_config()

    - Sortiere Konfigurationen nach Score (höchster zuerst)
    - Gebe Top 3 Konfigurationen zurück
    - Füge Logging hinzu: Anzahl Konfigurationen, Scores
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.7_
  

  - [x] 3.2 Implementiere evaluate_config() Funktion in utils/pv3d.py

    - Erstelle Funktion mit Parametern: config, building_dims, target_modules, goal
    - Berechne geschätzte Modulanzahl basierend auf Dachfläche und Effizienz
    - Implementiere Bewertung für goal="max_modules": Modulanzahl maximieren


    - Implementiere Bewertung für goal="max_yield": Ertrag maximieren (Süd bevorzugt)
    - Implementiere Bewertung für goal="balanced": Ausgewogen
    - Berechne Score von 0-100
    - Gebe Score zurück
    - _Requirements: 3.4, 3.5, 3.6_
  
  - [x] 3.3 Integriere Optimierung in UI (solar_3d_view_module.py)


    - Importiere optimize_layout aus utils.pv3d

    - Rufe optimize_layout() auf wenn Button geklickt


    - Speichere Ergebnisse in st.session_state["optimization_results"] als JSON
    - Zeige Top 3 Konfigurationen mit Details: Aufständerung, Garage, Fassade, Score
    - Implementiere "Übernehmen" Button für jede Konfiguration
    - Aktualisiere UI-Werte bei Übernahme: layout_mode, use_garage, use_facade, mounting_mode
    - Zeige Erfolgsmeldung nach Übernahme
    - Füge Fehlerbehandlung hinzu mit aussagekräftigen Meldungen
    - _Requirements: 3.7, 3.8, 3.9, 3.10_

- [x] 4. Fix PDF-Screenshot-Integration




  - [x] 4.1 Korrigiere Screenshot-Speicherung in solar_3d_view_module.py





    - Finde "3D-Screenshot erstellen" Button Handler
    - Rufe render_plotly_image_bytes() auf
    - Speichere PNG-Bytes in st.session_state["pdf_3d_screenshot"]
    - Zeige Download-Button für PNG
    - Zeige Erfolgsmeldung: "Screenshot erstellt und für PDF vorbereitet"
    - Zeige Info-Meldung über automatische PDF-Integration
    - Füge Fehlerbehandlung hinzu
    - Füge Logging hinzu: Screenshot-Größe, Erfolg/Fehler
    - _Requirements: 4.1, 4.2, 4.3_

  
  - [x] 4.2 Korrigiere PDF-Integration in pdf_generator.py




    - Finde _add_3d_visualization_section() oder ähnliche Funktion
    - Lese PNG-Bytes aus st.session_state["pdf_3d_screenshot"]
    - Prüfe ob Screenshot vorhanden ist
    - Wenn vorhanden: Konvertiere zu BytesIO
    - Erstelle ReportLab Image mit Breite 17cm, Höhe 10.625cm (16:10)
    - Füge Image zu Story hinzu
    - Füge Bildunterschrift hinzu: "Abb.: 3D-Visualisierung der geplanten PV-Anlage"
    - Wenn nicht vorhanden: Füge Platzhalter-Text hinzu
    - Füge Fehlerbehandlung hinzu: Bei Fehler Platzhalter-Text


    - Füge Logging hinzu: Screenshot vorhanden, Einfüge-Erfolg/Fehler
    - _Requirements: 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

- [x] 5. Verbessere Logging und Fehlerbehandlung





  - Füge detailliertes Logging zu calculate_grid_positions() hinzu
  - Füge detailliertes Logging zu create_pv_module_3d() hinzu
  - Füge detailliertes Logging zu optimize_layout() hinzu
  - Füge detailliertes Logging zu PDF-Integration hinzu
  - Implementiere try-except Blöcke für alle kritischen Funktionen
  - Zeige aussagekräftige Fehlermeldungen in UI
  - Logge Fehler mit Traceback in Konsole
  - Implementiere Fallback-Werte bei fehlenden Daten
  - Stelle sicher dass App bei Fehlern nicht blockiert
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

- [x] 6. Verbessere Benutzer-Feedback








  - Zeige Erfolgsmeldung nach erfolgreicher Modul-Platzierung
  - Zeige Warnung wenn nicht alle Module passen mit Details
  - Zeige Metriken: Platzierte Module vs. Gewünschte Module
  - Zeige Fortschrittsbalken während Optimierung läuft
  - Zeige Erfolgsmeldung nach erfolgreicher Optimierung
  - Zeige Erfolgsmeldung nach Screenshot-Erstellung
  - Zeige Info-Meldung über PDF-Integration
  - Füge Tooltips für alle wichtigen Eingabefelder hinzu
  - Implementiere visuelle Indikatoren für ausgewählte Module
  - Teste Echtzeit-Updates der 3D-Visualisierung
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10_

- [x] 7. Testing und Validierung







  - [x] 7.1 Teste Grid-Positionierung


    - Teste mit 10m x 6m Dach, 20 Module: Erwarte 20 Module
    - Teste mit 20m x 12m Dach, 50 Module: Erwarte 50 Module
    - Teste mit 10m x 6m Dach, 100 Module: Erwarte Warnung und max. mögliche Anzahl
    - Teste Zentrierung: Prüfe dass Grid zentriert ist
    - Validiere Logging-Ausgaben
    - _Requirements: 1.1, 1.2, 1.9, 1.10_
  

  - [x] 7.2 Teste Modul-Aufständerung


    - Teste Satteldach mit 30° Neigung: Erwarte Mounting Height > 0.1m
    - Teste Walmdach mit 35° Neigung: Erwarte Mounting Height > 0.1m
    - Teste Pultdach mit 25° Neigung: Erwarte Mounting Height > 0.1m
    - Teste Zeltdach mit 40° Neigung: Erwarte Mounting Height > 0.1m
    - Teste Krüppelwalmdach mit 30° Neigung: Erwarte Mounting Height > 0.1m
    - Teste Flachdach mit 0° Neigung: Erwarte Mounting Height = 0m
    - Validiere dass Module NICHT in Dachfläche einsinken
    - Validiere Logging-Ausgaben
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9_
  


  - [x] 7.3 Teste Optimierungs-Assistent






    - Teste "Optimierung starten" Button: Erwarte 3 Konfigurationen
    - Teste goal="max_modules": Erwarte höchsten Score für Konfiguration mit Garage+Fassade
    - Teste goal="max_yield": Erwarte höchsten Score für Süd-Aufständerung
    - Teste goal="balanced": Erwarte ausgewogene Scores
    - Teste "Übernehmen" Button: Erwarte UI-Update
    - Validiere dass Konfiguration korrekt angewendet wird
    - Validiere Logging-Ausgaben
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8, 3.9, 3.10_
  


  - [x] 7.4 Teste PDF-Screenshot-Integration









    - Teste "3D-Screenshot erstellen" Button: Erwarte PNG-Bytes in Session State
    - Teste PDF-Generierung mit Screenshot: Erwarte Bild auf Seite 6
    - Teste PDF-Generierung ohne Screenshot: Erwarte Platzhalter-Text
    - Validiere Bildgröße im PDF: 17cm Breite
    - Validiere Seitenverhältnis: 16:10
    - Validiere Bildunterschrift
    - Validiere Logging-Ausgaben
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_


  
  - [ ] 7.5 Teste Fehlerbehandlung

    - Teste mit fehlenden project_data: Erwarte Fallback-Werte
    - Teste mit ungültigen Dimensionen: Erwarte Fehlerbehandlung
    - Teste mit extremen Werten: Erwarte Clipping/Validierung
    - Teste Optimierung mit fehlenden Funktionen: Erwarte aussagekräftige Fehlermeldung
    - Teste PDF-Integration mit Rendering-Fehler: Erwarte Platzhalter
    - Validiere dass App nicht abstürzt
    - Validiere Fehler-Logging
    - _Requirements: 5.1, 5.2, 5.3, 5.8, 5.9, 5.10_

- [ ] 8. Dokumentation

  - [ ] 8.1 Erstelle Bugfix-Dokumentation

    - Dokumentiere alle behobenen Bugs mit Vorher/Nachher
    - Dokumentiere neue Funktionen: optimize_layout(), evaluate_config()
    - Dokumentiere geänderte Funktionen: calculate_grid_positions(), create_pv_module_3d()
    - Füge Code-Beispiele hinzu
    - Dokumentiere Logging-Ausgaben
  
  - [ ] 8.2 Aktualisiere Benutzer-Dokumentation

    - Dokumentiere Optimierungs-Assistent Workflow
    - Dokumentiere PDF-Screenshot Workflow
    - Füge Screenshots der UI hinzu
    - Dokumentiere Fehlermeldungen und deren Bedeutung

## Hinweise

- Jeder Task sollte mit funktionsfähigem, getesteten Code abgeschlossen werden
- Fokus auf die 4 kritischen Bugs: Grid-Positionierung, Aufständerung, Optimierung, PDF-Integration
- Ausführliches Logging für bessere Nachvollziehbarkeit
- Robuste Fehlerbehandlung um App-Stabilität zu gewährleisten
- Testing ist optional aber empfohlen für Qualitätssicherung
