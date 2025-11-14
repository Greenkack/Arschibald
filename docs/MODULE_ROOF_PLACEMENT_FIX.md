# Modul-Dach-Platzierung Fix - BEHOBEN ✅

## Problem

Module wurden an der GEBÄUDEWAND platziert, nicht AUF DEM DACH!

![Problem](Screenshot zeigt Module an der Seite des Gebäudes)
- Module an der Gebäudewand (vertikal)
- Nicht auf der Dachfläche
- Falsche Z-Position

## Ursache

Die `calculate_z_position()` Funktion gab für Satteldächer nur **0.05m** zurück.

Das war die Höhe relativ zur **Gebäudehöhe** (wall_height), nicht zur **Dachhöhe** (ridge height).

Für ein Satteldach mit:
- Gebäudehöhe: 3.0m
- Dachneigung: 35°
- Dachbreite: 10.0m

Wurde berechnet:
```
Z-Position = 0.05m (relativ zur Gebäudehöhe)
Absolute Position = 3.0m + 0.05m = 3.05m
```

Aber die **Firsthöhe** (ridge height) ist:
```
Firsthöhe = (10.0m / 2) * tan(35°) = 3.50m
Absolute Firsthöhe = 3.0m + 3.50m = 6.50m
```

Die Module wurden also bei 3.05m platziert, während das Dach bis 6.50m geht!

## Lösung

**Berechne Z-Position basierend auf Dachhöhe**:

```python
def calculate_z_position(roof_type: str, roof_pitch: float = 0.0, roof_width: float = 10.0) -> float:
    import math
    
    roof_type_normalized = roof_type.strip().lower()

    # Flachdach: Aufständerung
    if "flach" in roof_type_normalized:
        return 0.3  # 30cm elevation
    
    # Schrägdach: Berechne Firsthöhe
    else:
        if roof_pitch > 0:
            # Berechne Dachhöhe am First
            roof_height = (roof_width / 2) * math.tan(math.radians(roof_pitch))
            # Platziere Module bei ~60% der Firsthöhe (Mitte der Dachschräge)
            return roof_height * 0.6 + 0.05
        else:
            return 0.05
```

## Neue Berechnung

Für Satteldach mit 35° Neigung und 10m Breite:

```
Firsthöhe = (10.0m / 2) * tan(35°) = 3.50m
Z-Position = 3.50m * 0.6 + 0.05m = 2.15m (relativ zur Gebäudehöhe)
Absolute Position = 3.0m + 2.15m = 5.15m
```

Die Module werden jetzt bei **5.15m** platziert, was auf der **Dachschräge** ist!

## Vorteile

1. ✅ **Korrekte Platzierung**: Module auf dem Dach, nicht an der Wand
2. ✅ **Dachneigung berücksichtigt**: Höhere Dächer = höhere Module
3. ✅ **Realistische Darstellung**: Module folgen der Dachgeometrie
4. ✅ **Flexible Berechnung**: Funktioniert für verschiedene Dachneigungen

## Geänderte Dateien

- `utils/pv3d_placement_handler.py`:
  - Zeile 440-478: `calculate_z_position()` mit `roof_width` Parameter
  - Zeile 323: Aufruf mit `roof_width`
  - Zeile 561: Aufruf mit `roof_width`
  - Zeile 758-780: Test-Aufrufe aktualisiert

## Erwartetes Verhalten (Nach Fix)

### Flachdach:
- Z-Position: 0.3m (Aufständerung)
- Module auf Flachdach mit Rahmen

### Satteldach (35°, 10m breit):
- Firsthöhe: 3.50m
- Z-Position: 2.15m (60% der Firsthöhe)
- Module auf Dachschräge

### Pultdach (25°, 10m breit):
- Firsthöhe: 2.33m
- Z-Position: 1.45m (60% der Firsthöhe)
- Module auf Dachschräge

## Warum 60% der Firsthöhe?

Module werden bei 60% der Firsthöhe platziert, weil:
1. Das ist ungefähr die **Mitte der Dachschräge**
2. Nicht zu nah am Rand (0%)
3. Nicht zu nah am First (100%)
4. Gute Balance für Visualisierung

## Zusammenfassung

Das Problem wurde behoben durch:
1. ✅ Berechnung der Firsthöhe basierend auf Dachneigung
2. ✅ Platzierung der Module bei 60% der Firsthöhe
3. ✅ Übergabe von `roof_width` an `calculate_z_position()`
4. ✅ Aktualisierung aller Funktionsaufrufe

Die Module werden jetzt korrekt AUF DEM DACH platziert, nicht mehr an der Gebäudewand!
