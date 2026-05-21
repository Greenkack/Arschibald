# Fix: Module werden unter dem Dach gerendert

## Problem

Module auf Flachdächern werden teilweise **unter** dem Dach gerendert, anstatt darauf zu liegen.

### Diagnose-Ergebnisse

```
Dach-Parameter:
  - Wandhöhe: 6.0m
  - Basis-Z (Dachoberkante): 6.12m

Modul-Analyse:
  Modul 0:
    - Zentrum: (-3.62, -1.56, 6.17)m
    - Z-Bereich: 6.015m bis 6.325m
    - Über Dach: -0.105m  ← NEGATIV! Modul ist UNTER dem Dach!
```

## Ursache

Das Problem liegt in der `place_panels_flat_roof` Funktion (Zeile 2305 in `utils/pv3d.py`):

```python
z = base_z + 0.05  # 5cm über Dach
```

**ABER**: `make_panel` erstellt Module mit `origin_at_bottom=False`, was bedeutet, dass die Z-Position das **Zentrum** des Moduls ist, nicht die Unterseite!

Wenn ein Modul:
- Dicke: 0.04m (PV_T)
- Neigung: 30° (tilt_deg)
- Position Z: base_z + 0.05

Nach der Rotation um 30° wird das Modul gekippt, und die Unterseite rutscht unter die angegebene Z-Position!

### Berechnung

Für ein geneigtes Modul (30°):
- Modul-Höhe (PV_H): 1.76m
- Nach Rotation: Vertikale Projektion = 1.76m * sin(30°) = 0.88m
- Halbe Höhe: 0.44m

Die Unterseite des Moduls ist also:
- Z_center - (Höhe/2) * cos(tilt) - (Dicke/2) * sin(tilt)
- 6.17 - 0.88 * cos(30°) - 0.02 * sin(30°)
- 6.17 - 0.76 - 0.01
- ≈ 5.40m (viel zu niedrig!)

## Lösung

Die Z-Position muss so berechnet werden, dass die **Unterseite** des Moduls auf dem Dach liegt, nicht das Zentrum.

### Formel für korrekte Z-Position

Für ein geneigtes Modul:
```python
# Berechne die Höhe, die das Modul nach Rotation einnimmt
module_height_projected = (PV_H / 2) * math.sin(_deg_to_rad(tilt_deg))
module_thickness_projected = (PV_T / 2) * math.cos(_deg_to_rad(tilt_deg))

# Z-Position so dass Unterseite auf base_z liegt
z = base_z + module_height_projected + module_thickness_projected + 0.05
```

### Alternative: Einfachere Lösung

Für Flachdächer mit Aufständerung (15-30° Neigung):
```python
# Für 15° Neigung: ~0.25m Erhöhung
# Für 30° Neigung: ~0.50m Erhöhung
elevation = (PV_H / 2) * math.sin(_deg_to_rad(tilt_deg))
z = base_z + elevation + 0.10  # 10cm zusätzlicher Abstand
```

## Implementation

Die Änderung muss in `utils/pv3d.py` in der Funktion `place_panels_flat_roof` vorgenommen werden:

```python
# ALT (Zeile 2305):
z = base_z + 0.05  # 5cm über Dach

# NEU:
# Berechne Erhöhung basierend auf Modul-Neigung
# Die Unterseite des geneigten Moduls muss auf dem Dach liegen
import math
elevation = (PV_H / 2) * math.sin(_deg_to_rad(tilt))
z = base_z + elevation + 0.10  # Unterseite + 10cm Abstand
```

## Erwartetes Ergebnis

Nach dem Fix sollten Module korrekt **über** dem Dach liegen:

```
Modul-Analyse:
  Modul 0:
    - Z-Bereich: 6.35m bis 6.65m
    - Über Dach: +0.23m  ← POSITIV! Modul ist ÜBER dem Dach!
```

## Zusätzliche Überprüfungen

Das gleiche Problem könnte auch in anderen Funktionen auftreten:
1. `place_panels_auto` - für geneigte Dächer
2. `place_panels_manual` - für manuelle Platzierung

Diese sollten ebenfalls überprüft werden!
