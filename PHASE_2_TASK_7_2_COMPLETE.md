# Phase 2 - Task 7.2: Magnet-Funktion (Snap-to-Grid) - COMPLETE ✅

## Übersicht

Task 7.2 implementiert eine Magnet-Funktion (Snap-to-Grid), die es ermöglicht, Module beim manuellen Verschieben automatisch am Raster auszurichten. Dies erleichtert die präzise Platzierung und sorgt für eine ordentliche Anordnung.

**Status**: ✅ COMPLETE (8/8 Tests bestanden)

## Implementierte Features

### 1. Snap-to-Grid Funktion

**Funktion**: `snap_to_grid(x, y, grid_spacing=0.5)`

Richtet eine Position am nächsten Raster-Punkt aus.

**Features**:
- Rundet X- und Y-Koordinaten auf nächstes Raster-Vielfaches
- Konfigurierbare Raster-Größe (0.1m - 1.0m)
- Funktioniert mit positiven und negativen Koordinaten
- Standard-Raster: 0.5m (50cm)

**Beispiele**:
```python
# 0.5m Raster
snap_to_grid(1.23, 2.67, grid_spacing=0.5)
# → (1.0, 2.5)

# 0.1m Raster (präzise)
snap_to_grid(1.23, 2.67, grid_spacing=0.1)
# → (1.2, 2.7)

# 1.0m Raster (grob)
snap_to_grid(1.23, 2.67, grid_spacing=1.0)
# → (1.0, 3.0)
```

### 2. Manuelle Verschiebung mit Snap

**Funktion**: `handle_manual_move_with_snap()`

Verschiebt ein Modul zu einer neuen Position mit optionaler Raster-Ausrichtung.

**Features**:
- Optional aktivierbare Snap-to-Grid Funktion
- Konfigurierbare Raster-Größe
- Automatische Z-Positions-Berechnung basierend auf Dachtyp
- Kollisionserkennung an neuer Position
- Session State Update bei erfolgreicher Verschiebung
- Detaillierte Rückmeldung über Erfolg/Fehler

**Parameter**:
- `module_index`: Index des zu verschiebenden Moduls
- `new_x`, `new_y`: Neue Position
- `roof_type`, `roof_pitch`, `roof_width`, `roof_length`: Dach-Parameter
- `enable_snap`: Snap-to-Grid aktivieren? (default: True)
- `grid_spacing`: Raster-Größe in Metern (default: 0.5m)
- `orientation`: Modul-Orientierung (default: "portrait")

**Rückgabe**:
```python
{
    "success": bool,           # Ob Verschiebung erfolgreich war
    "message": str,            # Status oder Fehlermeldung
    "old_position": tuple,     # Alte Position (x, y, z)
    "new_position": tuple      # Neue Position (x, y, z)
}
```

**Beispiel**:
```python
result = handle_manual_move_with_snap(
    module_index=0,
    new_x=1.23,
    new_y=2.67,
    roof_type="Flachdach",
    roof_pitch=0.0,
    roof_width=10.0,
    roof_length=10.0,
    enable_snap=True,
    grid_spacing=0.5
)

if result["success"]:
    print(f"Modul verschoben: {result['message']}")
    # Position wurde auf (1.0, 2.5, z) ausgerichtet
else:
    print(f"Fehler: {result['message']}")
```

## Implementierungs-Details

### Datei-Änderungen

**`utils/pv3d_placement_handler.py`**:
- Neue Funktion `snap_to_grid()` (Zeilen 975-1015)
- Neue Funktion `handle_manual_move_with_snap()` (Zeilen 1018-1150)
- Beide Funktionen vor `initialize_session_state()` eingefügt

### Algorithmus

**Snap-to-Grid**:
```python
x_snapped = round(x / grid_spacing) * grid_spacing
y_snapped = round(y / grid_spacing) * grid_spacing
```

**Verschiebungs-Workflow**:
1. Validiere Modul-Index
2. Speichere alte Position
3. Wende Snap-to-Grid an (wenn aktiviert)
4. Berechne neue Z-Position basierend auf Dachtyp
5. Prüfe Kollision mit anderen Modulen
6. Bei Kollision: Abbruch mit Fehlermeldung
7. Bei Erfolg: Update Session State und Rückmeldung

## Test-Ergebnisse

**Test-Datei**: `test_task7_2_standalone.py`

### Alle Tests bestanden ✅ (8/8)

1. ✅ **test_snap_to_grid_half_meter**: Snap auf 0.5m Raster
   - Testet 4 verschiedene Positionen
   - Verifiziert korrekte Rundung

2. ✅ **test_snap_to_grid_tenth_meter**: Snap auf 0.1m Raster
   - Testet präzise Ausrichtung
   - Verifiziert feinere Raster-Größe

3. ✅ **test_snap_to_grid_one_meter**: Snap auf 1.0m Raster
   - Testet grobe Ausrichtung
   - Verifiziert größere Raster-Größe

4. ✅ **test_snap_to_grid_zero_position**: Snap am Ursprung
   - Verifiziert dass (0, 0) korrekt behandelt wird

5. ✅ **test_snap_to_grid_negative_positions**: Snap mit negativen Koordinaten
   - Testet negative X- und Y-Werte
   - Verifiziert korrekte Rundung in alle Richtungen

6. ✅ **test_handle_manual_move_with_snap_enabled**: Modul-Verschiebung mit Snap
   - Testet kompletten Verschiebungs-Workflow
   - Verifiziert dass Position am Raster ausgerichtet wird
   - Verifiziert Session State Update

7. ✅ **test_handle_manual_move_with_snap_disabled**: Modul-Verschiebung ohne Snap
   - Testet Verschiebung ohne Raster-Ausrichtung
   - Verifiziert dass exakte Position verwendet wird

8. ✅ **test_handle_manual_move_collision_detection**: Kollisionserkennung
   - Testet dass Kollisionen erkannt werden
   - Verifiziert dass Verschiebung bei Kollision verhindert wird

### Test-Ausgabe

```
============================================================
TASK 7.2: SNAP-TO-GRID TESTS
============================================================

Testing snap to 0.5m grid...
✓ Snap to 0.5m grid test passed
Testing snap to 0.1m grid...
✓ Snap to 0.1m grid test passed
Testing snap to 1.0m grid...
✓ Snap to 1.0m grid test passed
Testing snap at origin...
✓ Snap at origin test passed
Testing snap with negative coordinates...
✓ Snap with negative coordinates test passed
Testing module move with snap enabled...
✓ Module move with snap enabled test passed
Testing module move with snap disabled...
✓ Module move with snap disabled test passed
Testing collision detection during move...
✓ Collision detection test passed

============================================================
✓ ALL TESTS PASSED (8/8)
============================================================

Task 7.2 implementation is complete and working!
```

## Requirements Erfüllt

- ✅ **Requirement 5.2**: Magnet-Funktion für automatische Raster-Ausrichtung
  - Snap-to-Grid implementiert
  - Konfigurierbare Raster-Größe (0.1m - 1.0m)
  - Optional aktivierbar/deaktivierbar

- ✅ **Requirement 7.1-7.4**: Kollisionserkennung
  - Kollisionsprüfung bei Verschiebung
  - Verhindert ungültige Platzierungen

- ✅ **Requirement 9.1-9.2**: Session State Management
  - Aktualisiert `placed_module_positions`
  - Erhält Konsistenz des Session State

## Integration

### Verwendung in UI

```python
import streamlit as st
from utils.pv3d_placement_handler import handle_manual_move_with_snap

# UI-Controls
enable_snap = st.checkbox("Snap-to-Grid aktivieren", value=True)
grid_spacing = st.slider(
    "Raster-Größe (m)",
    min_value=0.1,
    max_value=1.0,
    value=0.5,
    step=0.1
)

# Modul verschieben
if st.button("Modul verschieben"):
    result = handle_manual_move_with_snap(
        module_index=selected_module,
        new_x=new_x,
        new_y=new_y,
        roof_type=st.session_state.roof_type,
        roof_pitch=st.session_state.roof_pitch,
        roof_width=st.session_state.roof_width,
        roof_length=st.session_state.roof_length,
        enable_snap=enable_snap,
        grid_spacing=grid_spacing
    )
    
    if result["success"]:
        st.success(result["message"])
    else:
        st.error(result["message"])
```

### Verwendung mit Drag & Drop (zukünftig)

```python
# Bei Drag-Ende
def on_drag_end(module_index, new_x, new_y):
    result = handle_manual_move_with_snap(
        module_index=module_index,
        new_x=new_x,
        new_y=new_y,
        roof_type=st.session_state.roof_type,
        roof_pitch=st.session_state.roof_pitch,
        roof_width=st.session_state.roof_width,
        roof_length=st.session_state.roof_length,
        enable_snap=st.session_state.get("snap_enabled", True),
        grid_spacing=st.session_state.get("grid_spacing", 0.5)
    )
    return result
```

## Vorteile

1. **Präzise Platzierung**: Module werden exakt am Raster ausgerichtet
2. **Ordentliche Anordnung**: Gleichmäßige Abstände zwischen Modulen
3. **Flexibilität**: Snap kann aktiviert/deaktiviert werden
4. **Konfigurierbar**: Raster-Größe anpassbar (0.1m - 1.0m)
5. **Sicher**: Kollisionserkennung verhindert ungültige Platzierungen
6. **Benutzerfreundlich**: Klare Rückmeldungen über Erfolg/Fehler

## Nächste Schritte

Task 7.2 ist vollständig implementiert und getestet. Die nächsten Sub-Tasks in Task 7 sind:

- [ ] **Task 7.3**: Kopieren & Einfügen von Modulen
- [ ] **Task 7.4**: Vorschau bei Verschieben
- [ ] **Task 7.5**: Tastatur-Shortcuts

## Technische Details

### Performance

- **Snap-to-Grid**: O(1) - Konstante Zeit
- **Verschiebung**: O(n) - Linear mit Anzahl Module (Kollisionsprüfung)
- **Memory**: Minimal - Keine zusätzlichen Datenstrukturen

### Edge Cases

Alle Edge Cases werden korrekt behandelt:
- ✅ Position am Ursprung (0, 0)
- ✅ Negative Koordinaten
- ✅ Sehr kleine Raster (0.1m)
- ✅ Sehr große Raster (1.0m)
- ✅ Kollisionen mit anderen Modulen
- ✅ Ungültige Modul-Indizes

### Fehlerbehandlung

Die Funktion `handle_manual_move_with_snap()` behandelt alle Fehler:
- Ungültige Modul-Indizes
- Kollisionen
- Exceptions während Verschiebung
- Gibt immer strukturierte Rückmeldung zurück

## Zusammenfassung

Task 7.2 (Magnet-Funktion) ist vollständig implementiert und getestet:

- ✅ 2 neue Funktionen implementiert
- ✅ 8/8 Tests bestanden
- ✅ Alle Requirements erfüllt
- ✅ Dokumentation vollständig
- ✅ Bereit für Integration in UI

Die Snap-to-Grid Funktionalität ermöglicht präzise und ordentliche Modulplatzierung und ist ein wichtiger Baustein für die verbesserte manuelle Modulplatzierung (Task 7).
