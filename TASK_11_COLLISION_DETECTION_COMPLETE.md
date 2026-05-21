# Task 11: Kollisionserkennung - ABGESCHLOSSEN ✓

## Übersicht

Die Kollisionserkennung für die PV-Modul-Platzierung wurde erfolgreich implementiert. Das System erkennt nun automatisch Überlappungen zwischen Modulen und Überschreitungen der Dachgrenzen.

## Implementierte Funktionen

### 1. `check_module_collision()` - Hauptfunktion

**Datei**: `utils/pv3d_placement_handler.py`

**Funktionalität**:
- Prüft ob ein neues Modul mit bestehenden Modulen überlappt
- Prüft ob ein Modul über die Dachkanten hinausragt
- Berücksichtigt Modul-Orientierung (Portrait/Landscape)
- Berücksichtigt Sicherheitsabstände (Margins)

**Parameter**:
```python
check_module_collision(
    new_position: tuple,           # (x, y, z) Position des neuen Moduls
    existing_positions: List[tuple], # Liste bestehender Modul-Positionen
    roof_length: float,            # Dachlänge in Metern
    roof_width: float,             # Dachbreite in Metern
    margin: float = 0.30,          # Randabstand (Standard: 30cm)
    orientation: str = "portrait"  # Modul-Orientierung
) -> Dict[str, Any]
```

**Rückgabewert**:
```python
{
    "collision": bool,           # True wenn Kollision erkannt
    "type": str,                 # "module", "boundary", oder "none"
    "message": str,              # Beschreibung der Kollision
    "colliding_index": int|None  # Index des kollidierenden Moduls
}
```

### 2. Kollisionstypen

#### A. Modul-zu-Modul Überlappung (Requirement 7.1)

**Algorithmus**:
- Berechnet Abstand zwischen Modul-Zentren (dx, dy)
- Vergleicht mit Modul-Dimensionen
- Kollision wenn: `dx < module_width AND dy < module_height`

**Beispiel-Meldung**:
```
⚠️ Modul überlappt mit bestehendem Modul #3 (Abstand: X=0.50m, Y=0.30m)
```

#### B. Dachrand-Überschreitung (Requirement 7.2)

**Prüfungen**:
- Linke Kante: `(x - module_width/2) < min_x`
- Rechte Kante: `(x + module_width/2) > max_x`
- Untere Kante: `(y - module_height/2) < min_y`
- Obere Kante: `(y + module_height/2) > max_y`

**Beispiel-Meldungen**:
```
⚠️ Modul überschreitet linke Dachkante (X: -5.03m < -4.70m)
⚠️ Modul überschreitet rechte Dachkante (X: 5.03m > 4.70m)
⚠️ Modul überschreitet untere Dachkante (Y: -4.38m < -3.70m)
⚠️ Modul überschreitet obere Dachkante (Y: 4.38m > 3.70m)
```

### 3. Integration in `handle_manual_add()`

**Erweiterte Funktionalität**:
- Ruft `check_module_collision()` vor dem Hinzufügen auf
- Verhindert Platzierung bei erkannter Kollision (Requirement 7.4)
- Zeigt Warnung an (Requirement 7.3)
- Fügt Modul nur hinzu wenn keine Kollision vorliegt

**Neue Parameter**:
```python
handle_manual_add(
    x: float,
    y: float,
    roof_type: str,
    roof_pitch: float = 0.0,
    roof_length: float = 10.0,     # NEU
    roof_width: float = 8.0,       # NEU
    orientation: str = "portrait"  # NEU
)
```

## Technische Details

### Modul-Dimensionen

**Portrait-Orientierung** (Standard):
- Breite: 1.05m
- Höhe: 1.76m
- Dicke: 0.04m

**Landscape-Orientierung**:
- Breite: 1.76m (gedreht)
- Höhe: 1.05m (gedreht)
- Dicke: 0.04m

### Bounding Box Berechnung

```python
# Modul-Zentrum bei (x, y)
half_width = module_width / 2
half_height = module_height / 2

# Bounding Box Grenzen
left_edge = x - half_width
right_edge = x + half_width
bottom_edge = y - half_height
top_edge = y + half_height
```

### Dach-Grenzen Berechnung

```python
# Mit Margin (Standard: 0.30m)
max_x = (roof_length / 2) - margin
min_x = -(roof_length / 2) + margin
max_y = (roof_width / 2) - margin
min_y = -(roof_width / 2) + margin
```

## Test-Ergebnisse

### Alle Tests bestanden ✓

```
======================================================================
TEST RESULTS: 10 passed, 0 failed
======================================================================
```

### Test-Abdeckung

1. ✓ **Keine Kollision** - Gut getrennte Module
2. ✓ **Modul-Überlappung** - Module zu nah beieinander
3. ✓ **Exakte Überlappung** - Module an gleicher Position
4. ✓ **Linke Grenze** - Modul überschreitet linke Dachkante
5. ✓ **Rechte Grenze** - Modul überschreitet rechte Dachkante
6. ✓ **Obere Grenze** - Modul überschreitet obere Dachkante
7. ✓ **Untere Grenze** - Modul überschreitet untere Dachkante
8. ✓ **Multiple Module** - Kollisionsprüfung mit mehreren Modulen
9. ✓ **Landscape-Orientierung** - Korrekte Dimensionen bei Drehung
10. ✓ **Edge Case** - Module die sich gerade nicht berühren

## Requirements-Erfüllung

### ✓ Requirement 7.1: Modul-Modul Überlappung
- Implementiert in `check_module_collision()`
- Prüft Abstand zwischen allen Modul-Paaren
- Verwendet Bounding Box Kollisionserkennung

### ✓ Requirement 7.2: Dach-Rand Überschreitung
- Implementiert in `check_module_collision()`
- Prüft alle vier Dachkanten
- Berücksichtigt Sicherheitsabstände (Margins)

### ✓ Requirement 7.3: Warnung bei Kollision
- Aussagekräftige Fehlermeldungen
- Unterscheidung zwischen Kollisionstypen
- Angabe der betroffenen Position/Modul-Nummer

### ✓ Requirement 7.4: Verhinderung bei Kollision
- Integration in `handle_manual_add()`
- Modul wird nicht hinzugefügt bei Kollision
- Session State bleibt unverändert

## Verwendung

### Beispiel 1: Manuelle Platzierung mit Kollisionsprüfung

```python
import streamlit as st
from utils.pv3d_placement_handler import handle_manual_add

# Modul manuell hinzufügen
result = handle_manual_add(
    x=2.0,
    y=1.5,
    roof_type="Flachdach",
    roof_pitch=0.0,
    roof_length=10.0,
    roof_width=8.0,
    orientation="portrait"
)

if result["success"]:
    st.success(result["message"])
else:
    st.error(result["message"])  # Zeigt Kollisionswarnung
```

### Beispiel 2: Direkte Kollisionsprüfung

```python
from utils.pv3d_placement_handler import check_module_collision

# Neue Position prüfen
new_pos = (2.0, 1.5, 0.3)
existing = [(0.0, 0.0, 0.3), (4.0, 0.0, 0.3)]

result = check_module_collision(
    new_position=new_pos,
    existing_positions=existing,
    roof_length=10.0,
    roof_width=8.0
)

if result["collision"]:
    print(f"Kollision erkannt: {result['message']}")
    print(f"Typ: {result['type']}")
else:
    print("Keine Kollision - Position ist gültig")
```

## Dateien

### Geänderte Dateien

1. **`utils/pv3d_placement_handler.py`**
   - Neue Funktion: `check_module_collision()`
   - Erweiterte Funktion: `handle_manual_add()`
   - Aktualisierte Imports: `PV_W`, `PV_H`
   - Aktualisierte Docstrings

### Neue Dateien

1. **`test_collision_detection_task11.py`**
   - Umfassende Test-Suite
   - 10 Test-Fälle
   - Alle Requirements abgedeckt

2. **`TASK_11_COLLISION_DETECTION_COMPLETE.md`**
   - Diese Dokumentation
   - Verwendungsbeispiele
   - Technische Details

## Performance

### Komplexität

- **Zeit-Komplexität**: O(n) - Linear mit Anzahl bestehender Module
- **Speicher-Komplexität**: O(1) - Konstanter Speicherbedarf

### Optimierung

Die Kollisionsprüfung ist für bis zu 200 Module optimiert:
- Schnelle Bounding Box Berechnung
- Früher Abbruch bei erster Kollision
- Keine komplexen geometrischen Berechnungen

## Nächste Schritte

Die Kollisionserkennung ist vollständig implementiert und getestet. Sie kann nun in folgenden Bereichen verwendet werden:

1. **Automatische Platzierung** (Task 2)
   - Optional: Kollisionsprüfung in `handle_auto_placement()` integrieren
   - Verhindert ungültige Grid-Positionen

2. **UI-Integration** (Task 3)
   - Visuelle Feedback bei Kollisionen
   - Rote Markierung für ungültige Positionen

3. **3D-Visualisierung** (Task 12)
   - Farbcodierung: Rot für Kollisionen
   - Transparenz für ungültige Positionen

## Zusammenfassung

✅ **Task 11 vollständig abgeschlossen**

- Alle Sub-Tasks implementiert
- Alle Requirements erfüllt (7.1, 7.2, 7.3, 7.4)
- Umfassende Tests (10/10 bestanden)
- Dokumentation erstellt
- Keine Breaking Changes
- Performance optimiert

Die Kollisionserkennung ist produktionsreif und kann sofort verwendet werden.
