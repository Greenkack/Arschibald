# Dachtyp-spezifische Logik - Schnellreferenz

## Übersicht

Die dachtyp-spezifische Logik optimiert die Modul-Platzierung basierend auf dem Dachtyp. Jeder Dachtyp hat einzigartige Anforderungen für optimale Energieausbeute und Wartungsfreundlichkeit.

---

## Unterstützte Dachtypen

### 1. Flachdach

**Merkmale:**
- Module auf Aufständerung (30cm Höhe)
- 30° Neigung für optimale Sonneneinstrahlung
- Große Reihenabstände (3-4m) zur Verschattungs-Vermeidung

**Verwendung:**
```python
from utils.pv3d_roof_type_logic import calculate_flat_roof_positions

positions = calculate_flat_roof_positions(
    roof_length=10.0,      # Dachlänge in Metern
    roof_width=8.0,        # Dachbreite in Metern
    module_quantity=20,    # Gewünschte Modulanzahl
    tilt_angle=30.0,       # Neigungs-Winkel (Standard: 30°)
    margin=0.30            # Rand-Abstand (Standard: 0.30m)
)
```

**Besonderheiten:**
- Weniger Module als bei geneigten Dächern (wegen Reihenabstand)
- Alle Module auf gleicher Z-Höhe (0.30m)
- Optimiert für Mitteleuropa (Wintersonnenstand 15°)

---

### 2. Schrägdach (Pultdach)

**Merkmale:**
- Module parallel zur Dachfläche
- Keine Aufständerung (nur 0.15m Montage-Schienen)
- Z-Position variiert mit Dachneigung

**Verwendung:**
```python
from utils.pv3d_roof_type_logic import calculate_pitched_roof_positions

positions = calculate_pitched_roof_positions(
    roof_length=10.0,      # Dachlänge in Metern
    roof_width=8.0,        # Dachbreite in Metern
    roof_pitch=25.0,       # Dachneigung in Grad
    module_quantity=20,    # Gewünschte Modulanzahl
    base_z=0.15            # Basis Z-Position (Standard: 0.15m)
)
```

**Besonderheiten:**
- Module folgen Dachneigung
- Z steigt von vorne nach hinten
- Standard Grid-Spacing (0.05m)

---

### 3. Satteldach

**Merkmale:**
- Module auf beiden Dachseiten
- First-Bereich freigelassen (0.50m Abstand)
- Symmetrische Belegung (gleiche Anzahl pro Seite)

**Verwendung:**
```python
from utils.pv3d_roof_type_logic import calculate_gabled_roof_positions

result = calculate_gabled_roof_positions(
    roof_length=12.0,      # Dachlänge in Metern
    roof_width=10.0,       # Dachbreite in Metern (gesamt)
    roof_pitch=35.0,       # Dachneigung in Grad
    module_quantity=30,    # Gewünschte Modulanzahl (gesamt)
    ridge_clearance=0.50,  # First-Abstand (Standard: 0.50m)
    symmetric=True         # Symmetrische Belegung (Standard: True)
)

# Ergebnis:
# result["left_side"]   - Liste von (x, y, z) für linke Seite
# result["right_side"]  - Liste von (x, y, z) für rechte Seite
# result["total_count"] - Gesamtanzahl platzierter Module

# Kombiniere beide Seiten:
all_positions = result["left_side"] + result["right_side"]
```

**Besonderheiten:**
- Linke Seite: negative Y-Koordinaten
- Rechte Seite: positive Y-Koordinaten
- First-Bereich für Wartung freigelassen
- Z steigt von Traufe zum First (beide Seiten)

---

## Haupt-Einstiegspunkt

### `get_roof_type_placement()`

Automatisches Routing zur richtigen Dachtyp-Logik:

```python
from utils.pv3d_roof_type_logic import get_roof_type_placement

positions = get_roof_type_placement(
    roof_type="Flachdach",  # oder "Satteldach", "Pultdach", etc.
    roof_length=10.0,
    roof_width=8.0,
    roof_pitch=0.0,         # Nur für geneigte Dächer
    module_quantity=20
)
```

**Erkannte Dachtypen:**
- `"Flachdach"` → Flachdach-Logik
- `"Satteldach"` → Satteldach-Logik
- `"Pultdach"` → Schrägdach-Logik
- Andere → Schrägdach-Logik (Fallback)

---

## Reihenabstand-Berechnung (Flachdach)

### `calculate_flat_roof_row_spacing()`

Berechnet optimalen Reihenabstand zur Verschattungs-Vermeidung:

```python
from utils.pv3d_roof_type_logic import calculate_flat_roof_row_spacing

spacing = calculate_flat_roof_row_spacing(
    module_height=1.76,      # Modul-Höhe (Standard: 1.76m)
    tilt_angle=30.0,         # Neigungs-Winkel (Standard: 30°)
    sun_elevation=15.0       # Min. Sonnenstand (Standard: 15°)
)

print(f"Optimaler Reihenabstand: {spacing:.2f}m")
# Ausgabe: Optimaler Reihenabstand: 3.94m
```

**Formel:**
```
module_height_vertical = module_height * sin(tilt_angle)
shadow_length = module_height_vertical / tan(sun_elevation)
row_spacing = shadow_length * safety_factor (1.2)
```

---

## Parameter

### Modul-Dimensionen

```python
PV_W = 1.05  # Modul-Breite (m)
PV_H = 1.76  # Modul-Höhe (m)
PV_T = 0.04  # Modul-Dicke (m)
```

### Flachdach-Konstanten

```python
FLAT_ROOF_TILT_ANGLE = 30.0      # Optimale Neigung (°)
FLAT_ROOF_ELEVATION = 0.30       # Aufständerung (m)
MIN_SUN_ELEVATION = 15.0         # Min. Sonnenstand (°)
SHADING_SAFETY_FACTOR = 1.2      # Sicherheitsfaktor
```

### Satteldach-Konstanten

```python
ridge_clearance = 0.50  # First-Abstand (m)
base_z = 0.15           # Basis Z-Position (m)
```

---

## Beispiele

### Beispiel 1: Flachdach

```python
from utils.pv3d_roof_type_logic import get_roof_type_placement

# 10m x 8m Flachdach, 20 Module gewünscht
positions = get_roof_type_placement(
    roof_type="Flachdach",
    roof_length=10.0,
    roof_width=8.0,
    roof_pitch=0.0,
    module_quantity=20
)

print(f"Platziert: {len(positions)} Module")
# Ausgabe: Platziert: 8 Module
# (Weniger wegen großem Reihenabstand)

# Erste Position
x, y, z = positions[0]
print(f"Erstes Modul: X={x:.2f}m, Y={y:.2f}m, Z={z:.2f}m")
# Ausgabe: Erstes Modul: X=-3.85m, Y=0.00m, Z=0.30m
```

### Beispiel 2: Pultdach

```python
# 10m x 8m Pultdach, 25° Neigung, 20 Module
positions = get_roof_type_placement(
    roof_type="Pultdach",
    roof_length=10.0,
    roof_width=8.0,
    roof_pitch=25.0,
    module_quantity=20
)

print(f"Platziert: {len(positions)} Module")
# Ausgabe: Platziert: 20 Module

# Z-Bereich
z_values = [pos[2] for pos in positions]
print(f"Z-Bereich: {min(z_values):.2f}m bis {max(z_values):.2f}m")
# Ausgabe: Z-Bereich: 0.75m bis 2.44m
```

### Beispiel 3: Satteldach

```python
from utils.pv3d_roof_type_logic import calculate_gabled_roof_positions

# 12m x 10m Satteldach, 35° Neigung, 30 Module
result = calculate_gabled_roof_positions(
    roof_length=12.0,
    roof_width=10.0,
    roof_pitch=35.0,
    module_quantity=30,
    symmetric=True
)

print(f"Total: {result['total_count']} Module")
print(f"Links: {len(result['left_side'])} Module")
print(f"Rechts: {len(result['right_side'])} Module")
# Ausgabe:
# Total: 30 Module
# Links: 15 Module
# Rechts: 15 Module

# Kombiniere beide Seiten
all_positions = result["left_side"] + result["right_side"]
```

---

## Integration in Placement Handler

Die dachtyp-spezifische Logik ist automatisch in `handle_auto_placement()` integriert:

```python
from utils.pv3d_placement_handler import handle_auto_placement

result = handle_auto_placement(
    roof_length=10.0,
    roof_width=8.0,
    module_quantity=20,
    roof_type="Flachdach",  # Automatisch richtige Logik
    roof_pitch=0.0
)

if result["success"]:
    print(result["message"])
    positions = result["positions"]
else:
    print(f"Fehler: {result['message']}")
```

---

## Tipps

### 1. Flachdach-Optimierung

**Problem:** Zu wenige Module passen auf Flachdach

**Lösung:**
- Vergrößere Dachfläche
- Reduziere Rand-Abstand (margin)
- Akzeptiere weniger Module (Verschattung wichtiger als Anzahl)

### 2. Satteldach-Asymmetrie

**Problem:** Ungleiche Belegung gewünscht (z.B. Süd-Seite bevorzugen)

**Lösung:**
```python
result = calculate_gabled_roof_positions(
    ...,
    symmetric=False  # Asymmetrische Belegung
)
# Füllt zuerst linke Seite, dann rechte Seite
```

### 3. Eigene Dachtypen

**Problem:** Neuer Dachtyp nicht unterstützt

**Lösung:**
```python
# Erstelle eigene Funktion nach gleichem Muster
def calculate_custom_roof_positions(...):
    # Eigene Logik
    return positions

# Oder verwende Fallback (Schrägdach-Logik)
positions = calculate_pitched_roof_positions(...)
```

---

## Fehlerbehandlung

### Häufige Fehler

**1. Keine Module platziert**
```python
positions = get_roof_type_placement(...)
if not positions:
    print("Fehler: Dachfläche zu klein oder Ränder zu groß")
```

**2. Weniger Module als gewünscht**
```python
if len(positions) < module_quantity:
    print(f"Nur {len(positions)} von {module_quantity} Modulen passen")
```

**3. Ungültige Parameter**
```python
try:
    positions = get_roof_type_placement(...)
except ValueError as e:
    print(f"Ungültige Parameter: {e}")
```

---

## Performance

**Berechnungszeit:**
- Flachdach: < 1ms (typisch 8-12 Module)
- Schrägdach: < 2ms (typisch 15-25 Module)
- Satteldach: < 3ms (typisch 20-40 Module)

**Speicher:**
- Minimal (nur Positions-Listen)
- Keine großen Datenstrukturen
- Effiziente Numpy-Arrays

---

## Weitere Informationen

**Vollständige Dokumentation:**
- `TASK_6_ROOF_TYPE_LOGIC_COMPLETE.md` - Detaillierte Implementierungs-Dokumentation

**Tests:**
- `test_task6_roof_type_logic.py` - Umfassende Tests für alle Dachtypen

**Quellcode:**
- `utils/pv3d_roof_type_logic.py` - Hauptmodul (1000+ Zeilen)
- `utils/pv3d_placement_handler.py` - Integration

---

**Letzte Aktualisierung:** 2025-01-13
