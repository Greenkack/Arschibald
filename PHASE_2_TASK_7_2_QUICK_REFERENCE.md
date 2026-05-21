# Task 7.2: Snap-to-Grid - Quick Reference

## Status
✅ **COMPLETE** - 8/8 Tests bestanden

## Neue Funktionen

### 1. `snap_to_grid(x, y, grid_spacing=0.5)`
Richtet Position am Raster aus.

**Parameter**:
- `x`, `y`: Position in Metern
- `grid_spacing`: Raster-Größe (0.1m - 1.0m, default: 0.5m)

**Rückgabe**: `(x_snapped, y_snapped)`

**Beispiel**:
```python
from utils.pv3d_placement_handler import snap_to_grid

# 0.5m Raster
x, y = snap_to_grid(1.23, 2.67, grid_spacing=0.5)
# → (1.0, 2.5)

# 0.1m Raster (präzise)
x, y = snap_to_grid(1.23, 2.67, grid_spacing=0.1)
# → (1.2, 2.7)
```

### 2. `handle_manual_move_with_snap()`
Verschiebt Modul mit optionalem Snap.

**Wichtige Parameter**:
- `module_index`: Index des Moduls
- `new_x`, `new_y`: Neue Position
- `enable_snap`: Snap aktivieren? (default: True)
- `grid_spacing`: Raster-Größe (default: 0.5m)
- Dach-Parameter: `roof_type`, `roof_pitch`, `roof_width`, `roof_length`

**Rückgabe**:
```python
{
    "success": bool,
    "message": str,
    "old_position": tuple,
    "new_position": tuple
}
```

**Beispiel**:
```python
from utils.pv3d_placement_handler import handle_manual_move_with_snap

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
    print(f"✓ {result['message']}")
else:
    print(f"✗ {result['message']}")
```

## UI Integration

```python
import streamlit as st

# Controls
enable_snap = st.checkbox("Snap-to-Grid", value=True)
grid_spacing = st.slider("Raster (m)", 0.1, 1.0, 0.5, 0.1)

# Verschieben
if st.button("Verschieben"):
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

## Tests

**Datei**: `test_task7_2_standalone.py`

**Ausführen**:
```bash
python test_task7_2_standalone.py
```

**Ergebnis**: ✅ 8/8 Tests bestanden

## Features

- ✅ Snap auf 0.5m Raster (Standard)
- ✅ Snap auf 0.1m Raster (präzise)
- ✅ Snap auf 1.0m Raster (grob)
- ✅ Funktioniert mit negativen Koordinaten
- ✅ Optional aktivierbar/deaktivierbar
- ✅ Kollisionserkennung
- ✅ Automatische Z-Positions-Berechnung
- ✅ Session State Update

## Raster-Größen

| Größe | Verwendung | Präzision |
|-------|-----------|-----------|
| 0.1m  | Sehr präzise | Hoch |
| 0.5m  | Standard | Mittel |
| 1.0m  | Grob | Niedrig |

## Datei-Änderungen

- ✅ `utils/pv3d_placement_handler.py`: 2 neue Funktionen
- ✅ `test_task7_2_standalone.py`: 8 Tests
- ✅ `PHASE_2_TASK_7_2_COMPLETE.md`: Dokumentation
- ✅ `PHASE_2_TASK_7_2_QUICK_REFERENCE.md`: Diese Datei

## Requirements Erfüllt

- ✅ **5.2**: Magnet-Funktion für Raster-Ausrichtung
- ✅ **7.1-7.4**: Kollisionserkennung
- ✅ **9.1-9.2**: Session State Management

## Nächste Schritte

- [ ] Task 7.3: Kopieren & Einfügen
- [ ] Task 7.4: Vorschau bei Verschieben
- [ ] Task 7.5: Tastatur-Shortcuts
