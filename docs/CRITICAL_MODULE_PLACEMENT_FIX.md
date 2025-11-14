# KRITISCHER FIX: Module werden korrekt auf dem Dach platziert

## Problem-Analyse

Es gibt **DREI** zusammenhängende Probleme:

### Problem 1: Module werden nicht initial angezeigt
- "Module automatisch belegen" Button funktioniert nicht sichtbar
- Module werden in Session State gespeichert, aber nicht gerendert

### Problem 2: Module erscheinen bei "Rotation starten" falsch
- Module sind auf dem Boden oder Decke statt auf dem Dach
- Z-Position wird mehrfach falsch berechnet

### Problem 3: Z-Positions-Berechnung ist inkonsistent
- `calculate_z_position()` gibt relative Position zurück (0.15m)
- `build_plotly_scene` addiert `wall_height_m` dazu
- `create_pv_module_3d` addiert NOCHMAL `mounting_height` dazu
- **Ergebnis**: Module sind viel zu hoch oder zu niedrig

## Root Cause

Die Z-Positions-Berechnung hat **drei Schichten**:

```python
# Schicht 1: calculate_z_position() 
z_relative = 0.15  # Relativ zur Traufhöhe

# Schicht 2: build_plotly_scene
z = dims.wall_height_m + z_relative  # z = 6.0 + 0.15 = 6.15m

# Schicht 3: create_pv_module_3d
z += mounting_height  # z = 6.15 + 0.3 = 6.45m (FALSCH!)
```

Das Problem: **Mounting Height wird doppelt addiert!**

## Lösung

Die Z-Position muss **NUR EINMAL** korrekt berechnet werden:

### Für geneigte Dächer (Satteldach, Pultdach, etc.):
```python
z_absolute = wall_height_m + 0.15  # 15cm über Traufhöhe
# KEINE zusätzliche mounting_height in create_pv_module_3d!
```

### Für Flachdächer:
```python
z_absolute = wall_height_m + 0.30  # 30cm Aufständerung
# KEINE zusätzliche mounting_height in create_pv_module_3d!
```

## Implementierung

### Fix 1: `create_pv_module_3d` - Entferne doppelte Mounting Height

Die Funktion sollte die Z-Position **NICHT** mehr modifizieren:

```python
def create_pv_module_3d(x, y, z, ...):
    # Z-Position ist bereits korrekt (absolut)
    # KEINE Modifikation mehr!
    
    # Alte Version (FALSCH):
    # z += mounting_height  # ❌ Doppelt addiert!
    
    # Neue Version (KORREKT):
    # z bleibt unverändert  # ✅ Bereits korrekt
```

### Fix 2: Logging verbessern

Füge Debug-Ausgaben hinzu um die Z-Positionen zu verfolgen:

```python
print(f"Module {i}:")
print(f"  Position aus Session State: ({x:.2f}, {y:.2f}, {z_relative:.2f})")
print(f"  Wall Height: {dims.wall_height_m:.2f}m")
print(f"  Absolute Z: {z:.2f}m")
print(f"  Roof Type: {roof_type}")
print(f"  Tilt: {tilt_deg:.1f}°")
```

## Erwartete Ergebnisse

### Satteldach (30° Neigung, 6m Wandhöhe):
- Z-Position in Session State: 0.15m (relativ)
- Absolute Z-Position: 6.15m
- Module erscheinen **AUF** dem Dach, nicht im Boden

### Flachdach (6m Wandhöhe):
- Z-Position in Session State: 0.30m (relativ)
- Absolute Z-Position: 6.30m
- Module erscheinen **AUF** der Aufständerung

## Nächste Schritte

1. ✅ `calculate_z_position()` korrigiert (gibt relative Position zurück)
2. ⏳ `create_pv_module_3d()` korrigieren (keine doppelte Mounting Height)
3. ⏳ Debug-Logging hinzufügen
4. ⏳ Testen mit verschiedenen Dachtypen
