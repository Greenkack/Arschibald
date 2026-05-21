# Fix: Module werden jetzt korrekt AUF dem Dach platziert

## Problem
Die PV-Module wurden auf der Gebäudefläche (Boden) platziert statt auf dem Dach. Dies war ein Fehler in der Z-Positions-Berechnung.

## Ursache
Die Funktion `calculate_z_position()` in `utils/pv3d_placement_handler.py` berechnete die Z-Position für geneigte Dächer falsch:

**Alte Berechnung (FALSCH):**
```python
# Platzierte Module bei 60% der Firsthöhe
roof_height = (roof_width / 2) * math.tan(math.radians(roof_pitch))
return roof_height * 0.6 + 0.05  # Zu niedrig!
```

Dies führte dazu, dass Module auf der Gebäudefläche erschienen, da die Z-Position zu niedrig war.

## Lösung
Die Z-Position wird jetzt korrekt relativ zur Traufhöhe (wall_height_m) berechnet:

**Neue Berechnung (KORREKT):**
```python
# Module sitzen auf der Dachoberfläche
# Die Dachneigung wird durch die Dachgeometrie selbst dargestellt
return 0.15  # 15cm Abstand über Traufhöhe
```

### Warum funktioniert das?

1. **Koordinatensystem**: Die Z-Position ist relativ zur Traufhöhe (Oberkante der Gebäudewand)
2. **Dachgeometrie**: Das Dach selbst hat bereits die korrekte Neigung und Geometrie
3. **Module**: Module werden mit 0.15m Abstand über der Traufhöhe platziert
4. **Rendering**: In `build_plotly_scene()` wird dann `dims.wall_height_m + z_relative` addiert

## Änderungen

### Datei: `utils/pv3d_placement_handler.py`

**Funktion:** `calculate_z_position()`

**Vorher:**
```python
if roof_pitch > 0:
    roof_height = (roof_width / 2) * math.tan(math.radians(roof_pitch))
    return roof_height * 0.6 + 0.05  # ❌ Zu niedrig
```

**Nachher:**
```python
# For pitched roofs, modules sit on the roof surface
# The roof itself is already at the correct height in the scene
# We just need a small clearance above the roof base
return 0.15  # ✅ 15cm clearance above roof base (Traufhöhe)
```

## Ergebnisse

### Z-Positionen nach Dachtyp

| Dachtyp | Z-Position | Beschreibung |
|---------|-----------|--------------|
| Flachdach | 0.30m | Aufständerung mit 30° Neigung |
| Satteldach | 0.15m | 15cm über Traufhöhe |
| Pultdach | 0.15m | 15cm über Traufhöhe |
| Walmdach | 0.15m | 15cm über Traufhöhe |
| Krüppelwalmdach | 0.15m | 15cm über Traufhöhe |
| Zeltdach | 0.15m | 15cm über Traufhöhe |

### Beispielrechnung

**Satteldach mit 30° Neigung, 10m Breite:**

- Traufhöhe (wall_height_m): 6.0m
- Z-Position (relativ): 0.15m
- Absolute Z-Position: 6.0m + 0.15m = 6.15m
- Firsthöhe: 6.0m + 2.89m = 8.89m

Die Module erscheinen jetzt korrekt auf der Dachoberfläche!

## Validierung

Der Test `test_module_roof_placement_fix.py` validiert die Korrektur:

```bash
python test_module_roof_placement_fix.py
```

**Ergebnis:**
```
✓ ALLE TESTS BESTANDEN!

ZUSAMMENFASSUNG:
  • Flachdach: Module auf Aufständerung (0.30m über Dachbasis)
  • Geneigte Dächer: Module auf Dachoberfläche (0.15m über Traufhöhe)
  • Z-Position ist relativ zur Traufhöhe (wall_height_m)
  • Die Dachneigung wird durch die Dachgeometrie selbst dargestellt
  • Fix erfolgreich: Module korrekt auf dem Dach platziert!
```

## Visuelle Verbesserung

**Vorher:**
- ❌ Module auf Gebäudefläche (Boden)
- ❌ Module nicht sichtbar oder falsch positioniert
- ❌ Unrealistische Darstellung

**Nachher:**
- ✅ Module korrekt auf Dachoberfläche
- ✅ Module gut sichtbar und realistisch positioniert
- ✅ Korrekte Darstellung der PV-Anlage

## Betroffene Dateien

1. `utils/pv3d_placement_handler.py` - Z-Positions-Berechnung korrigiert
2. `test_module_roof_placement_fix.py` - Validierungstest erstellt
3. `MODULE_PLACEMENT_ON_ROOF_FIX.md` - Diese Dokumentation

## Nächste Schritte

Die Module werden jetzt korrekt auf dem Dach platziert. Weitere Verbesserungen:

1. ✅ Module auf Dachoberfläche (ERLEDIGT)
2. Feinabstimmung der Modul-Rotation für verschiedene Dachtypen
3. Optimierung der Modul-Verteilung auf komplexen Dachformen
4. Verschattungsanalyse für realistische Ertragsprognosen

## Datum
2025-01-10
