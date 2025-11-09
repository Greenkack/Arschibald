# Implementation Plan - PV-Modul Platzierung Komplett-Fix

## Übersicht

Diese Task-Liste beschreibt die schrittweise Implementierung der vollständigen Modul-Platzierungs-Funktionalität. Jeder Task baut auf den vorherigen auf und kann einzeln getestet werden.

## Tasks

- [x] 1. Grid Calculator implementieren





  - Erstelle `utils/pv3d_grid_calculator.py` mit Modul-Dimensionen und Grid-Berechnung
  - Implementiere `calculate_module_grid()` Funktion mit Abständen und Rändern
  - Implementiere Validierung für Eingabeparameter
  - Implementiere Optimierung für maximale Modulanzahl
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 2. Placement Handler implementieren





  - Erstelle `utils/pv3d_placement_handler.py` mit Handler-Funktionen
  - Implementiere `handle_auto_placement()` für automatische Platzierung
  - Implementiere `handle_reset_placement()` für Zurücksetzen
  - Implementiere `calculate_z_position()` für dachtyp-spezifische Z-Koordinate
  - Implementiere Session State Management für Positionen
  - Implementiere Fehlerbehandlung mit aussagekräftigen Meldungen
  - _Requirements: 2.2, 2.6, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5, 9.1, 9.2, 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 3. UI-Komponente implementieren





  - Erstelle `utils/pv3d_module_placement_ui.py` mit Panel-Rendering
  - Implementiere `render_module_placement_panel()` mit Expander
  - Implementiere Statistik-Anzeige (Gewünscht, Platziert, Abdeckung)
  - Implementiere Fortschrittsbalken
  - Implementiere Button "Automatisch belegen" (Primary)
  - Implementiere Button "Alle zurücksetzen"
  - Implementiere Checkboxen für Optionen (Raster, Nummern)
  - _Requirements: 2.1, 5.1, 5.2, 5.3, 5.4, 5.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 4. 3D-Rendering Integration implementieren





  - Modifiziere `utils/pv3d_plotly.py` in `build_plotly_scene()` Funktion
  - Implementiere Laden von Positionen aus Session State
  - Implementiere Loop über alle platzierten Positionen
  - Implementiere Aufruf von `create_pv_module_3d()` für jedes Modul
  - Implementiere Hinzufügen von Meshes zur Plotly Figure
  - Implementiere Fehlerbehandlung beim Rendering
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 5. Modul-Mesh Erstellung verbessern





  - Überprüfe `create_pv_module_3d()` in `utils/pv3d_plotly.py`
  - Stelle sicher dass Modul-Dimensionen korrekt sind (1.05m x 1.76m x 0.04m)
  - Stelle sicher dass Farbe sichtbar ist (dunkelblau #1a1a2e)
  - Stelle sicher dass Rotation korrekt angewendet wird (Neigung und Azimut)
  - Stelle sicher dass Translation korrekt angewendet wird (x, y, z)
  - Implementiere Opacity von 0.9 für bessere Sichtbarkeit
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 6. Integration in solar_3d_view_module.py





  - Importiere neue Module (pv3d_module_placement_ui, pv3d_placement_handler)
  - Füge Modul-Belegungs-Panel nach Export-Optionen ein
  - Implementiere Berechnung von Dachfläche und aktuell platzierten Modulen
  - Implementiere Aufruf von `render_module_placement_panel()`
  - Implementiere Handler für Auto-Placement Trigger
  - Implementiere Handler für Reset Button
  - Implementiere Try-Catch für Import-Fehler
  - Implementiere st.rerun() nach erfolgreicher Platzierung
  - _Requirements: 2.1, 2.2, 2.6, 4.3, 4.5, 8.1, 8.2, 8.3, 8.4, 8.5, 11.1, 11.2, 11.3, 11.4_

- [x] 7. Session State Initialisierung





  - Initialisiere `placed_module_positions` als leere Liste
  - Initialisiere `placed_module_count` als 0
  - Initialisiere `trigger_auto_placement` als False
  - Stelle sicher dass Initialisierung vor Panel-Rendering erfolgt
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 8. Dachtyp-spezifische Logik implementieren





  - Implementiere Z-Position Berechnung für Flachdach (0.3m Aufständerung)
  - Implementiere Z-Position Berechnung für Satteldach (0.05m direkt auf Dach)
  - Implementiere Z-Position Berechnung für Pultdach (0.05m direkt auf Dach)
  - Implementiere Neigungswinkel für Flachdach (30°)
  - Implementiere Neigungswinkel für Schrägdächer (Dachneigung)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. Fehlerbehandlung und Validierung





  - Implementiere Validierung für Dach-Dimensionen (> 0)
  - Implementiere Validierung für Modulanzahl (> 0)
  - Implementiere Try-Catch um Grid-Berechnung
  - Implementiere Try-Catch um Rendering
  - Implementiere aussagekräftige Fehlermeldungen
  - Implementiere Fallback auf vorherigen Zustand bei Fehler
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 10. Manuelle Steuerungs-Buttons hinzufügen
  - Implementiere Button "Modul hinzufügen" in UI-Komponente
  - Implementiere Button "Ausgewählte entfernen" in UI-Komponente
  - Implementiere `handle_manual_add()` in Placement Handler
  - Implementiere `handle_remove_selected()` in Placement Handler
  - Implementiere Session State für ausgewählte Module
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [ ] 11. Kollisionserkennung implementieren
  - Implementiere `check_module_collision()` Funktion
  - Implementiere Prüfung auf Modul-Modul Überlappung
  - Implementiere Prüfung auf Dach-Rand Überschreitung
  - Implementiere Warnung bei erkannter Kollision
  - Implementiere Verhinderung von Platzierung bei Kollision
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Visualisierungs-Verbesserungen
  - Implementiere Farb-Unterscheidung für normale Module (dunkelblau)
  - Implementiere Farb-Unterscheidung für ausgewählte Module (hellblau)
  - Implementiere Farb-Unterscheidung für ungültige Positionen (rot)
  - Implementiere Modul-Nummern Anzeige (optional)
  - Implementiere Raster-Overlay (optional)
  - _Requirements: 1.2, 8.5_

- [ ] 13. Performance-Optimierung
  - Implementiere Batch-Hinzufügen von Meshes zur Figure
  - Implementiere Caching von berechneten Positionen
  - Implementiere Begrenzung auf maximal 200 Module
  - Implementiere numpy Arrays statt Python Listen
  - Teste Performance mit 50, 100, 200 Modulen
  - _Requirements: 10.5_

- [ ]* 14. Unit Tests schreiben
  - Schreibe Tests für `calculate_module_grid()` mit verschiedenen Parametern
  - Schreibe Tests für `handle_auto_placement()` mit verschiedenen Dachtypen
  - Schreibe Tests für `handle_reset_placement()`
  - Schreibe Tests für Z-Position Berechnung
  - Schreibe Tests für Fehlerbehandlung
  - _Requirements: Alle_

- [ ]* 15. Integrationstests schreiben
  - Schreibe End-to-End Test für automatische Platzierung
  - Schreibe Test für verschiedene Dachtypen (Flach, Satteldach, Pultdach)
  - Schreibe Test für verschiedene Modulanzahlen (1, 10, 50, 100)
  - Schreibe Test für UI-Integration (Panel, Buttons, Statistiken)
  - Schreibe Test für Session State Persistenz
  - _Requirements: Alle_

- [ ] 16. Regression Testing
  - Teste alle bestehenden Export-Funktionen (STL, GLB, Screenshot)
  - Teste alle bestehenden WOW-Features
  - Teste alle bestehenden 3D-Visualisierungs-Features
  - Stelle sicher dass keine Performance-Verschlechterung auftritt
  - Stelle sicher dass keine Breaking Changes existieren
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 17. Dokumentation erstellen
  - Erstelle Benutzer-Dokumentation für Modul-Belegung
  - Erstelle Code-Dokumentation (Docstrings)
  - Erstelle Beispiele für verschiedene Anwendungsfälle
  - Erstelle Troubleshooting-Guide
  - Aktualisiere README mit neuen Features
  - _Requirements: Alle_

## Prioritäten

### Phase 1: Kern-Funktionalität (Kritisch)
- Task 1: Grid Calculator
- Task 2: Placement Handler
- Task 3: UI-Komponente
- Task 4: 3D-Rendering Integration
- Task 5: Modul-Mesh Erstellung
- Task 6: Integration in solar_3d_view_module.py
- Task 7: Session State Initialisierung

**Ziel**: Module sind sichtbar und automatische Belegung funktioniert

### Phase 2: Dachtyp-Unterstützung (Hoch)
- Task 8: Dachtyp-spezifische Logik
- Task 9: Fehlerbehandlung und Validierung

**Ziel**: Alle Dachtypen werden korrekt unterstützt

### Phase 3: Erweiterte Funktionen (Mittel)
- Task 10: Manuelle Steuerungs-Buttons
- Task 11: Kollisionserkennung
- Task 12: Visualisierungs-Verbesserungen

**Ziel**: Vollständige Benutzer-Kontrolle und visuelle Verbesserungen

### Phase 4: Qualitätssicherung (Niedrig)
- Task 13: Performance-Optimierung
- Task 14: Unit Tests (Optional)
- Task 15: Integrationstests (Optional)
- Task 16: Regression Testing
- Task 17: Dokumentation

**Ziel**: Stabile, performante und gut dokumentierte Lösung

## Erfolgskriterien

Nach Abschluss aller Tasks (Phase 1-3):

✅ **Sichtbarkeit**:
- Module sind in 3D-Ansicht sichtbar
- Module haben korrekte Dimensionen und Farbe
- Module sind aus allen Winkeln sichtbar

✅ **Automatische Belegung**:
- Button "Automatisch belegen" ist vorhanden
- Klick auf Button platziert Module
- Statistiken zeigen korrekte Anzahl
- Fortschrittsbalken zeigt korrekten Wert

✅ **Manuelle Steuerung**:
- Button "Alle zurücksetzen" funktioniert
- Buttons für manuelle Belegung sind vorhanden
- Module können hinzugefügt und entfernt werden

✅ **Dachtyp-Unterstützung**:
- Flachdach: Module mit Aufständerung (30°)
- Satteldach: Module parallel zur Dachfläche
- Pultdach: Module parallel zur Dachfläche

✅ **Fehlerbehandlung**:
- Ungültige Eingaben werden abgefangen
- Aussagekräftige Fehlermeldungen werden angezeigt
- Anwendung stürzt nicht ab

✅ **Keine Regression**:
- Alle bestehenden Funktionen funktionieren weiter
- Keine Performance-Verschlechterung
- Keine Breaking Changes

## Test-Anleitung

### Manueller Test nach Phase 1

```bash
1. Starte Anwendung: streamlit run gui.py
2. Navigiere zu: 3D-Visualisierung
3. Sidebar → Scrolle nach unten
4. ✅ Prüfe: "🔲 Modul-Belegung" Panel ist sichtbar
5. ✅ Prüfe: Statistiken zeigen "Gewünscht", "Platziert", "Abdeckung"
6. ✅ Prüfe: Fortschrittsbalken ist sichtbar
7. ✅ Prüfe: Button "Automatisch belegen" ist sichtbar
8. Klicke: "Automatisch belegen"
9. ✅ Prüfe: Module erscheinen in 3D-Ansicht
10. ✅ Prüfe: Statistiken aktualisieren sich
11. ✅ Prüfe: Fortschrittsbalken zeigt Fortschritt
12. Klicke: "Alle zurücksetzen"
13. ✅ Prüfe: Module verschwinden
14. ✅ Prüfe: Statistiken zeigen 0
```

### Test verschiedener Dachtypen

```bash
1. Wähle Dachtyp: "Flachdach"
2. Klicke: "Automatisch belegen"
3. ✅ Prüfe: Module haben Aufständerung (schräg)
4. Wähle Dachtyp: "Satteldach"
5. Klicke: "Automatisch belegen"
6. ✅ Prüfe: Module liegen parallel zur Dachfläche
7. Wähle Dachtyp: "Pultdach"
8. Klicke: "Automatisch belegen"
9. ✅ Prüfe: Module liegen parallel zur Dachfläche
```

### Test verschiedener Modulanzahlen

```bash
1. Setze Modulanzahl: 10
2. Klicke: "Automatisch belegen"
3. ✅ Prüfe: 10 Module sind platziert
4. Klicke: "Alle zurücksetzen"
5. Setze Modulanzahl: 50
6. Klicke: "Automatisch belegen"
7. ✅ Prüfe: 50 Module sind platziert (oder weniger wenn Platz nicht reicht)
8. ✅ Prüfe: Performance ist akzeptabel (< 2 Sekunden)
```

### Regression Test

```bash
1. Teste Export-Funktionen:
   - ✅ STL Export funktioniert
   - ✅ GLB Export funktioniert
   - ✅ Screenshot funktioniert
2. Teste WOW-Features:
   - ✅ 360° Animation funktioniert
   - ✅ Multi-View funktioniert
3. Teste 3D-Navigation:
   - ✅ Zoom funktioniert
   - ✅ Rotation funktioniert
   - ✅ Pan funktioniert
```

## Dateien-Übersicht

### Neue Dateien

```
utils/pv3d_grid_calculator.py          # Task 1
utils/pv3d_placement_handler.py        # Task 2
utils/pv3d_module_placement_ui.py      # Task 3
tests/test_module_placement.py         # Task 14
tests/test_module_integration.py       # Task 15
docs/MODULE_PLACEMENT_USER_GUIDE.md    # Task 17
```

### Modifizierte Dateien

```
utils/pv3d_plotly.py                   # Task 4, 5
solar_3d_view_module.py                # Task 6, 7
```

### Keine Änderungen

```
utils/pv3d_export_buttons.py           # Bleibt unverändert
utils/pv3d_wow_features.py             # Bleibt unverändert
utils/pv3d_ui_components.py            # Bleibt unverändert
... (alle anderen bestehenden Dateien)
```

## Implementierungs-Reihenfolge

1. **Task 1** → Grid Calculator (Basis für alles)
2. **Task 2** → Placement Handler (Business Logic)
3. **Task 3** → UI-Komponente (Benutzer-Interface)
4. **Task 7** → Session State (Vorbereitung)
5. **Task 6** → Integration in solar_3d_view_module.py (Verbindung)
6. **Task 5** → Modul-Mesh Erstellung (Sichtbarkeit)
7. **Task 4** → 3D-Rendering Integration (Visualisierung)
8. **Task 9** → Fehlerbehandlung (Stabilität)
9. **Task 8** → Dachtyp-Logik (Korrektheit)
10. **Task 16** → Regression Testing (Qualität)
11. **Task 10-13** → Erweiterte Features (Optional)
12. **Task 14-15** → Tests (Optional)
13. **Task 17** → Dokumentation (Abschluss)

## Geschätzte Aufwände

- **Phase 1** (Task 1-7): 2-3 Stunden
- **Phase 2** (Task 8-9): 1 Stunde
- **Phase 3** (Task 10-12): 2-3 Stunden
- **Phase 4** (Task 13-17): 2-4 Stunden

**Gesamt**: 7-11 Stunden für vollständige Implementierung

**Minimum Viable Product (MVP)**: Phase 1 (2-3 Stunden)
