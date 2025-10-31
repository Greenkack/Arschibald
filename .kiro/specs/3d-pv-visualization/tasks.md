# Implementation Plan: 3D PV-Visualisierung

## Übersicht

Dieser Plan beschreibt die schrittweise Implementierung des 3D-Visualisierungstools für PV-Planung. Jeder Task baut auf den vorherigen auf und endet mit vollständig integriertem, funktionsfähigem Code.

## Tasks

- [x] 1. Projekt-Setup und Dependencies





  - Installiere alle erforderlichen Python-Pakete (pyvista, vtk, stpyvista, numpy, trimesh, reportlab, pikepdf, Pillow)
  - Erstelle die Verzeichnisstruktur (streamlit_app/utils/, streamlit_app/pages/)
  - Füge Dependencies zu requirements.txt hinzu
  - Verifiziere Installation durch Import-Tests
  - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [x] 2. Core 3D Engine - Datenstrukturen und Hilfsfunktionen





  - [x] 2.1 Erstelle streamlit_app/utils/pv3d.py mit Basis-Imports und Konstanten


    - Definiere PV-Modul-Konstanten (PV_W=1.05, PV_H=1.76, PV_T=0.04)
    - Definiere ROOF_COLORS Dictionary mit allen Dachdeckungsfarben
    - Implementiere _deg_to_rad() Konvertierungsfunktion
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  
  - [x] 2.2 Implementiere Datenklassen (BuildingDims, LayoutConfig)


    - Erstelle BuildingDims mit length_m, width_m, wall_height_m
    - Erstelle LayoutConfig mit mode, use_garage, use_facade, removed_indices, garage_dims, offsets
    - Implementiere LayoutConfig.to_json() und from_json() Methoden
    - _Requirements: 11.3, 11.6_
  
  - [x] 2.3 Implementiere robuste Datenextraktions-Funktionen


    - Schreibe _safe_get_orientation() mit Fallbacks für verschiedene Key-Strukturen
    - Schreibe _safe_get_roof_inclination_deg() mit Float-Konvertierung und Fallback
    - Schreibe _safe_get_roof_covering() mit String-Fallback
    - Schreibe _roof_color_from_covering() für Farb-Mapping
    - _Requirements: 4.1, 2.3, 3.1, 19.4, 19.5, 19.6, 19.7_

- [x] 3. Geometrie-Primitives und Dachformen



  - [x] 3.1 Implementiere Basis-Geometrie-Funktionen


    - Schreibe make_box() für Quader-Erstellung mit Origin-Kontrolle
    - Teste make_box() mit verschiedenen Dimensionen
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 3.2 Implementiere alle Dachform-Funktionen


    - Schreibe make_roof_flat() für Flachdächer (0.12m Dicke)
    - Schreibe make_roof_gable() für Satteldächer mit Firstberechnung
    - Schreibe make_roof_hip() für Walmdächer mit vier Flächen
    - Schreibe make_roof_pent() für Pultdächer mit Rotation
    - Schreibe make_roof_pyramid() für Zeltdächer mit zentralem Gipfel
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [x] 3.3 Implementiere PV-Modul-Geometrie


    - Schreibe make_panel() mit Position, Yaw und Tilt-Parametern
    - Implementiere Rotation um Z-Achse (yaw) und Y-Achse (tilt)
    - Teste Modul-Erstellung mit verschiedenen Winkeln
    - _Requirements: 5.3, 5.4, 7.3, 7.4, 7.5_


- [x] 4. PV-Modul-Platzierungs-Algorithmen





  - [x] 4.1 Implementiere Raster-Positionierungs-Funktion


    - Schreibe grid_positions() für gleichmäßige Modul-Verteilung
    - Berechne Spalten und Reihen basierend auf verfügbarer Fläche
    - Berücksichtige Randabstände (0.25m) und Modul-Zwischenräume
    - _Requirements: 5.5, 5.6, 5.7_
  
  - [x] 4.2 Implementiere automatische Belegungslogik


    - Berechne maximale Modul-Kapazität basierend auf Dachfläche
    - Platziere Module in Reihen und Spalten
    - Implementiere Logik für geneigte Dächer (parallel zur Dachfläche)
    - _Requirements: 5.1, 5.2, 5.8_
  

  - [x] 4.3 Implementiere manuelle Belegungslogik

    - Filtere Module basierend auf removed_indices
    - Validiere Indizes gegen verfügbare Positionen
    - _Requirements: 6.2, 6.3, 6.4_
  
  - [x] 4.4 Implementiere Flachdach-Aufständerung


    - Implementiere Süd-Aufständerung (15° Neigung, 0° Yaw)
    - Implementiere Ost-West-Aufständerung (10° Neigung, alternierender Yaw)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 5. Hauptfunktion build_scene()


  - [x] 5.1 Implementiere Szenen-Initialisierung


    - Erstelle PyVista Plotter mit off_screen=False und weißem Hintergrund
    - Generiere und füge Bodenplatte hinzu (3x Gebäudegröße, Farbe #f3f3f5)
    - Erstelle und füge Gebäudewände hinzu (Farbe #e7e7ea)
    - _Requirements: 10.6, 10.7, 1.1, 1.2, 1.3_
  

  - [x] 5.2 Implementiere Dach-Generierung und Rotation

    - Wähle Dachform basierend auf roof_type Parameter
    - Generiere Dach mit korrekter Neigung und Farbe
    - Implementiere Gebäude-Rotation basierend auf Ausrichtung (0°, -90°, 90°, 180°)
    - Füge Dach zum Plotter hinzu
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 4.5, 4.6, 4.7, 4.8_
  


  - [x] 5.3 Implementiere Kompass-Platzierung
    - Erstelle roten Pfeil-Mesh für Kompass
    - Platziere Kompass an Position (Länge*1.6, Breite*1.6, 0.1m)
    - Richte Pfeil nach Norden (Richtung 0, -1, 0)
    - _Requirements: 4.3, 4.4_
  


  - [x] 5.4 Implementiere PV-Modul-Platzierung auf Hauptdach
    - Berechne Raster-Positionen für Hauptdach
    - Filtere Positionen im manuellen Modus
    - Erstelle und platziere Module mit korrekter Neigung
    - Rotiere Module mit Gebäude
    - Füge Module zum Plotter hinzu (schwarze Farbe)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.2, 6.3, 6.4_


  
  - [x] 5.5 Implementiere Garage-Hinzufügung
    - Prüfe use_garage Flag und fehlende Module
    - Erstelle Garagengebäude mit garage_dims
    - Platziere Garage neben Hauptgebäude mit Offset
    - Erstelle Garagendach (Flachdach)
    - Platziere verbleibende Module auf Garagendach
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 5.6 Implementiere Fassaden-Belegung
    - Prüfe use_facade Flag und verbleibende fehlende Module
    - Identifiziere Südfassade basierend auf Ausrichtung
    - Berechne Raster-Positionen für Fassade (vertikal)
    - Platziere Module mit 90° Neigung an Fassade
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [x] 5.7 Finalisiere build_scene() Return

    - Gebe Plotter und Dictionary mit Panel-Listen zurück
    - Strukturiere Return als (plotter, {"main": [...], "garage": [...], "facade": [...]})
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 6. Export-Funktionen




  - [x] 6.1 Implementiere Off-Screen Screenshot-Funktion

    - Schreibe render_image_bytes() mit Off-Screen Plotter
    - Setze Auflösung auf 1600×1000 Pixel
    - Verwende isometrische Kameraperspektive
    - Konvertiere Screenshot zu PNG-Bytes mit Pillow
    - Implementiere Fehlerbehandlung (return b"" bei Fehler)
    - _Requirements: 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_
  


  - [x] 6.2 Implementiere STL-Export
    - Schreibe export_stl() Funktion
    - Merge alle Meshes (Panels, Dach) zu einem kombinierten Mesh
    - Speichere als STL-Datei
    - _Requirements: 14.1, 14.2, 14.3, 14.7_

  
  - [x] 6.3 Implementiere glTF-Export


    - Schreibe export_gltf() Funktion mit trimesh
    - Konvertiere PyVista Meshes zu trimesh Meshes
    - Erstelle trimesh Scene und exportiere als glTF/glb
    - _Requirements: 14.4, 14.5, 14.6, 14.7_

- [x] 7. PDF-Integration Modul




  - [x] 7.1 Erstelle streamlit_app/utils/pdf_visual_inject.py


    - Importiere ReportLab und pv3d Module
    - Implementiere make_pv3d_image_flowable() Funktion
    - Rufe render_image_bytes() auf und konvertiere zu BytesIO
    - Erstelle ReportLab Image mit width_cm und Seitenverhältnis 16:10
    - Implementiere Fehlerbehandlung (return None bei Fehler)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.6_
  
  - [x] 7.2 Implementiere get_pv3d_png_bytes_for_pdf()

    - Wrapper-Funktion für direkten PNG-Bytes Zugriff
    - Rufe render_image_bytes() mit Standardparametern auf
    - _Requirements: 15.1, 15.5_
  
  - [x] 7.3 Integriere in bestehenden PDF-Generator


    - Identifiziere Einfügepunkt in pdf_generator.py oder Template-Engine
    - Füge Import von pdf_visual_inject hinzu
    - Erstelle BuildingDims und LayoutConfig aus project_data
    - Rufe make_pv3d_image_flowable() auf und füge zu Story hinzu
    - Füge Bildunterschrift hinzu
    - Teste PDF-Generierung mit 3D-Bild
    - _Requirements: 15.7_

- [x] 8. Streamlit UI-Seite






  - [x] 8.1 Erstelle streamlit_app/pages/solar_3d_view.py Grundstruktur

    - Setze Page Config (Titel, Layout wide)
    - Lade project_data und analysis_results aus Session State
    - Extrahiere relevante Felder (roof_type, orientation, module_quantity, etc.)
    - Implementiere robuste Fallbacks für fehlende Daten
    - _Requirements: 19.1, 19.2, 19.3, 19.7, 20.1_
  


  - [x] 8.2 Implementiere Sidebar-Einstellungen
    - Erstelle Eingabefelder für Gebäudedimensionen (Länge 8-60m, Breite 5-40m, Höhe 3-20m)
    - Erstelle Dachform-Selectbox mit allen unterstützten Typen
    - Erstelle Belegungsmodus Radio-Buttons (Automatisch/Manuell)
    - Erstelle Flachdach-Aufständerungs-Selectbox (Süd/Ost-West)
    - Erstelle Checkboxen für Garage und Fassade
    - Erstelle Text-Area für manuelle Indizes-Eingabe
    - Parse Indizes-String zu Integer-Liste
    - _Requirements: 1.4, 1.5, 2.1, 6.1, 6.2, 7.1, 8.1, 9.1, 20.2, 20.3_

  
  - [x] 8.3 Implementiere Aktions-Buttons in Sidebar

    - Erstelle "Visualisierung aktualisieren" Button (Primary)
    - Erstelle "Reset (Auto-Belegung)" Button
    - Erstelle "Layout speichern" Button
    - Erstelle "Layout laden" Button
    - _Requirements: 11.1, 11.4, 12.1, 20.3_
  

  - [x] 8.4 Implementiere Session State Management

    - Initialisiere pv3d_layout_json mit Default LayoutConfig
    - Initialisiere pv3d_last_rendered Flag
    - Initialisiere _pv3d_plotter Slot
    - Implementiere Speichern-Logik (to_json → Session State)
    - Implementiere Laden-Logik (from_json ← Session State)
    - Implementiere Reset-Logik (Default LayoutConfig)
    - _Requirements: 11.2, 11.5, 11.7, 12.2, 12.3, 12.4, 12.5, 12.6_
  

  - [x] 8.5 Implementiere 3D-Rendering-Logik

    - Prüfe Render-Trigger (Button-Klick oder erste Anzeige)
    - Erstelle BuildingDims aus Eingabefeldern
    - Erstelle LayoutConfig aus Sidebar-Werten
    - Rufe build_scene() auf mit allen Parametern
    - Speichere Plotter in Session State
    - Implementiere Try-Catch mit Fehlerbehandlung
    - _Requirements: 17.1, 17.2, 17.3, 17.7, 18.2_
  

  - [x] 8.6 Implementiere Hauptbereich mit 2-Spalten-Layout

    - Erstelle Spalten mit Verhältnis 3:2 (60%:40%)
    - Linke Spalte: Zeige 3D-Viewer mit stpyvista()
    - Rechte Spalte: Zeige Status-Metriken
    - Implementiere Fehler-Fallback wenn Plotter fehlt
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 20.4, 20.5_
  

  - [x] 8.7 Implementiere Status-Anzeige

    - Berechne geschätzte Dachkapazität
    - Berechne platzierte Module (min von Kapazität und Modulanzahl)
    - Berechne fehlende Module
    - Zeige Metriken mit st.metric()
    - Zeige Warnung wenn Module fehlen (mit Hinweis auf Garage/Fassade)
    - Zeige Erfolg wenn alle Module passen
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 20.6_
  

  - [x] 8.8 Implementiere Export-Buttons

    - Erstelle "Screenshot (PNG) erzeugen" Button
    - Bei Klick: Rufe render_image_bytes() auf
    - Zeige Download-Button für PNG
    - Erstelle "STL exportieren" Button mit Download
    - Erstelle "glTF (.glb) exportieren" Button mit Download
    - Implementiere Fehlerbehandlung für alle Exports
    - _Requirements: 13.1, 13.6, 13.7, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_
  

  - [x] 8.9 Implementiere Hilfe-Sektion

    - Erstelle Expander "Datenquelle (App-Bindung)"
    - Erkläre Herkunft von Ausrichtung, Dachneigung, Dachdeckung
    - Erkläre Herkunft von Modulanzahl
    - _Requirements: 20.7_

- [x] 9. Integration und Testing





  - [x] 9.1 Integriere 3D-Seite in App-Navigation


    - Füge Link/Button im Solarkalkulator hinzu
    - Teste Navigation zur 3D-Seite
    - Verifiziere Datenübergabe (project_data, analysis_results)
    - _Requirements: 19.1, 19.2_
  


  - [ ] 9.2 Teste alle Dachformen
    - Teste Flachdach mit Süd- und Ost-West-Aufständerung
    - Teste Satteldach mit verschiedenen Neigungen
    - Teste Walmdach, Pultdach, Zeltdach
    - Verifiziere korrekte Geometrie und Farben


    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [ ] 9.3 Teste automatische und manuelle Belegung
    - Teste automatische Belegung mit verschiedenen Modulanzahlen
    - Teste manuelle Modul-Entfernung mit verschiedenen Indizes


    - Teste Garage-Hinzufügung bei Platzmangel
    - Teste Fassaden-Belegung
    - _Requirements: 5.1, 5.2, 6.1, 6.2, 6.3, 6.4, 8.1, 8.2, 9.1, 9.2_
  
  - [x] 9.4 Teste Export-Funktionen


    - Teste Screenshot-Export mit verschiedenen Szenen
    - Teste STL-Export und öffne in 3D-Viewer
    - Teste glTF-Export und öffne in 3D-Viewer
    - Verifiziere Dateigrößen und Qualität


    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_
  
  - [ ] 9.5 Teste PDF-Integration
    - Generiere PDF mit 3D-Visualisierung
    - Verifiziere Bildqualität und Positionierung


    - Teste Fehlerfall (Rendering fehlgeschlagen)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_
  
  - [ ] 9.6 Teste Fehlerbehandlung
    - Teste mit fehlenden project_data
    - Teste mit ungültigen Dimensionen
    - Teste mit extremen Werten (sehr groß/klein)
    - Verifiziere Fehlermeldungen und Fallbacks
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_
  
  - [ ] 9.7 Teste Performance
    - Messe Szenen-Erstellungszeit (< 1 Sekunde)
    - Messe Screenshot-Zeit (< 2 Sekunden)
    - Teste mit 10, 50, 100 Modulen
    - Verifiziere flüssiges Rendering im Browser
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7_

- [ ] 10. Dokumentation und Finalisierung
  - [ ]* 10.1 Erstelle Benutzer-Dokumentation
    - Schreibe Anleitung für 3D-Visualisierung
    - Erkläre alle Bedienelemente
    - Füge Screenshots hinzu
    - Dokumentiere Export-Optionen
  
  - [ ]* 10.2 Erstelle Entwickler-Dokumentation
    - Dokumentiere API von pv3d.py
    - Dokumentiere Datenstrukturen
    - Füge Code-Beispiele hinzu
    - Dokumentiere Erweiterungsmöglichkeiten
  
  - [ ] 10.3 Code-Review und Cleanup
    - Überprüfe Code-Qualität und Konsistenz
    - Entferne Debug-Code und Kommentare
    - Optimiere Imports
    - Formatiere Code (PEP 8)
  
  - [ ] 10.4 Finale Integration und Deployment
    - Merge in Hauptbranch
    - Aktualisiere requirements.txt
    - Teste auf verschiedenen Systemen (Windows, Linux, macOS)
    - Erstelle Release Notes

## Hinweise

- Jeder Task sollte mit funktionsfähigem, getesteten Code abgeschlossen werden
- Bei Problemen: Fehlerbehandlung implementieren und mit Fallbacks fortfahren
- Regelmäßig committen nach jedem abgeschlossenen Task
- Bei Performance-Problemen: Profiling durchführen und optimieren
- Die Implementierung folgt dem Code aus utils/3d_visuals.md als Referenz
