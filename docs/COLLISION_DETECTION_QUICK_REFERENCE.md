# Kollisionserkennung - Quick Reference

## Übersicht

Die Kollisionserkennung verhindert, dass PV-Module sich überlappen oder über den Dachrand hinausragen.

## Hauptfunktion

```python
from utils.pv3d_placement_handler import check_module_collision

result = check_module_collision(
    new_position=(x, y, z),           # Neue Modul-Position
    existing_positions=[...],          # Liste existierender Positionen
    roof_length=10.0,                  # Dachlänge in Metern
    roof_width=8.0,                    # Dachbreite in Metern
    margin=0.30,                       # Rand-Abstand (optional)
    orientation="portrait"             # "portrait" oder "landscape"
)
```

## Rückgabewert

```python
{
    "collision": bool,           # True wenn Kollision erkannt
    "type": str,                 # "module", "boundary" oder "none"
    "message": str,              # Beschreibung der Kollision
    "colliding_index": int|None  # Index des kollidierende Moduls (nur bei type="module")
}
```

## Beispiele

### Beispiel 1: Keine Kollision
```python
result = check_module_collision(
    new_position=(0.0, 0.0, 0.3),
    existing_positions=[(3.0, 0.0, 0.3)],  # 3m entfernt
    roof_length=10.0,
    roof_width=8.0
)

# result = {
#     "collision": False,
#     "type": "none",
#     "message": "✓ Keine Kollision erkannt",
#     "colliding_index": None
# }
```

### Beispiel 2: Modul-Überlappung
```python
result = check_module_collision(
    new_position=(0.0, 0.0, 0.3),
    existing_positions=[(0.5, 0.0, 0.3)],  # Nur 0.5m entfernt
    roof_length=10.0,
    roof_width=8.0
)

# result = {
#     "collision": True,
#     "type": "module",
#     "message": "⚠️ Modul überlappt mit bestehendem Modul #1 (Abstand: X=0.50m, Y=0.00m)",
#     "colliding_index": 0
# }
```

### Beispiel 3: Dachrand-Überschreitung
```python
result = check_module_collision(
    new_position=(6.0, 0.0, 0.3),  # Zu weit rechts
    existing_positions=[],
    roof_length=10.0,
    roof_width=8.0
)

# result = {
#     "collision": True,
#     "type": "boundary",
#     "message": "⚠️ Modul überschreitet rechte Dachkante (Modul-Kante: 6.53m > Dachkante: 5.00m)",
#     "colliding_index": None
# }
```

## Integration in Platzierungs-Funktionen

### Manuelle Platzierung
```python
from utils.pv3d_placement_handler import handle_manual_add

result = handle_manual_add(
    x=2.0,
    y=1.0,
    roof_type="Flachdach",
    roof_pitch=0.0,
    roof_length=10.0,
    roof_width=8.0,
    orientation="portrait"
)

if result["success"]:
    print(f"✓ {result['message']}")
else:
    print(f"✗ {result['message']}")
```

### Modul verschieben
```python
from utils.pv3d_placement_handler import handle_move_selected

result = handle_move_selected(
    selected_indices=[0, 1],
    offset_x=1.0,
    offset_y=0.5,
    roof_length=10.0,
    roof_width=8.0,
    roof_type="Flachdach",
    roof_pitch=0.0
)

if result["success"]:
    print(f"✓ {result['count']} Module verschoben")
else:
    print(f"✗ {result['message']}")
```

## Modul-Dimensionen

### Portrait (Standard)
- Breite: 1.05m
- Höhe: 1.76m

### Landscape
- Breite: 1.76m
- Höhe: 1.05m

## Koordinatensystem

```
        Y
        ^
        |
  (-5, 4) -------- (5, 4)
        |          |
        |  (0,0)   |
        |    •     |
        |          |
  (-5,-4) -------- (5,-4)
        |
        +----------> X

Beispiel: 10m x 8m Dach
X: -5m bis +5m
Y: -4m bis +4m
```

## Margin

Standard-Margin: **0.30m** (30cm)

Der Margin wird von allen Dachkanten abgezogen:
- Effektive Dachfläche = (Länge - 2×Margin) × (Breite - 2×Margin)
- Beispiel 10m × 8m Dach: Effektiv 9.4m × 7.4m

## Kollisions-Typen

### 1. Modul-zu-Modul ("module")
- Zwei Module überlappen sich
- Abstand zwischen Zentren < Summe der halben Dimensionen
- Zeigt Modul-Nummer und Abstände

### 2. Dachrand-Überschreitung ("boundary")
- Modul-Kante überschreitet Dach-Grenze
- Prüft alle vier Kanten (links, rechts, oben, unten)
- Zeigt Richtung und Koordinaten

### 3. Keine Kollision ("none")
- Modul kann platziert werden
- Ausreichend Abstand zu anderen Modulen
- Innerhalb der Dach-Grenzen

## Fehlerbehandlung

```python
try:
    result = check_module_collision(...)
    
    if result["collision"]:
        # Kollision behandeln
        if result["type"] == "module":
            print(f"Überlappung mit Modul #{result['colliding_index'] + 1}")
        elif result["type"] == "boundary":
            print("Modul außerhalb des Dachs")
    else:
        # Platzierung erlaubt
        print("Modul kann platziert werden")
        
except Exception as e:
    print(f"Fehler bei Kollisionsprüfung: {e}")
```

## Performance

- **Einzelne Prüfung:** O(1)
- **N existierende Module:** O(N)
- **Early Exit:** Stoppt bei erster Kollision

## Best Practices

### ✅ DO
- Immer vor Platzierung prüfen
- Fehlermeldungen an Benutzer zeigen
- Beide Orientierungen unterstützen
- Margin berücksichtigen

### ❌ DON'T
- Nicht ohne Kollisionsprüfung platzieren
- Nicht Z-Koordinate für Kollision verwenden (nur X, Y)
- Nicht Margin vergessen
- Nicht Modul-Dimensionen ignorieren

## Debugging

### Kollision wird nicht erkannt
```python
# Prüfe Modul-Dimensionen
print(f"Modul-Breite: {PV_W}m, Höhe: {PV_H}m")

# Prüfe Abstände
dx = abs(x1 - x2)
dy = abs(y1 - y2)
print(f"Abstand: dx={dx:.2f}m, dy={dy:.2f}m")

# Prüfe Schwellwerte
print(f"Kollision wenn: dx < {PV_W}m UND dy < {PV_H}m")
```

### Falsche Kollision erkannt
```python
# Prüfe Dach-Grenzen
roof_left = -roof_length / 2
roof_right = roof_length / 2
roof_bottom = -roof_width / 2
roof_top = roof_width / 2

print(f"Dach-Grenzen: X=[{roof_left}, {roof_right}], Y=[{roof_bottom}, {roof_top}]")

# Prüfe Modul-Kanten
module_left = x - PV_W / 2
module_right = x + PV_W / 2
module_bottom = y - PV_H / 2
module_top = y + PV_H / 2

print(f"Modul-Kanten: X=[{module_left}, {module_right}], Y=[{module_bottom}, {module_top}]")
```

## Tests

### Unit Tests ausführen
```bash
python test_collision_detection_task11.py
```

### Integration Tests ausführen
```bash
python test_collision_detection_integration.py
```

## Weitere Informationen

- **Vollständige Dokumentation:** `TASK_7_COLLISION_DETECTION_COMPLETE.md`
- **Verifikation:** `TASK_7_VERIFICATION_SUMMARY.md`
- **Source Code:** `utils/pv3d_placement_handler.py`
- **Tests:** `test_collision_detection_task11.py`, `test_collision_detection_integration.py`
