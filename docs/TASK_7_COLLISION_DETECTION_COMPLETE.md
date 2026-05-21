# Task 7: Kollisionserkennung - Abgeschlossen ✓

## Übersicht

Task 7 (Kollisionserkennung) wurde erfolgreich abgeschlossen. Das System verfügt nun über eine vollständige Kollisionserkennung, die sowohl Modul-zu-Modul-Überlappungen als auch Dachrand-Überschreitungen erkennt und verhindert.

## Implementierte Funktionen

### 7.1 Modul-Modul Kollision ✓

**Implementierung:**
- Funktion `check_module_collision()` in `utils/pv3d_placement_handler.py`
- Bounding-Box-basierte Kollisionserkennung
- Unterstützt beide Orientierungen (Portrait und Landscape)
- Erkennt Überlappungen zwischen Modulen

**Features:**
- Berechnet Modul-Dimensionen basierend auf Orientierung
- Verwendet Bounding-Box-Kollisionserkennung (AABB - Axis-Aligned Bounding Box)
- Prüft Abstand zwischen Modul-Zentren in X und Y Richtung
- Identifiziert das kollidierende Modul (Index)

**Algorithmus:**
```python
# Zwei Module überlappen wenn:
# - Abstand in X < Summe der halben Breiten
# - Abstand in Y < Summe der halben Höhen
if dx < module_width and dy < module_height:
    # Kollision erkannt!
```

**Test-Ergebnisse:**
- ✓ Erkennt Überlappungen korrekt
- ✓ Erlaubt gültige Platzierungen (keine False Positives)
- ✓ Funktioniert mit Portrait und Landscape Orientierung
- ✓ Identifiziert kollidierendes Modul

### 7.2 Modul-Dach Kollision ✓

**Implementierung:**
- Integriert in `check_module_collision()` Funktion
- Prüft alle vier Dachkanten (links, rechts, oben, unten)
- Berücksichtigt Modul-Dimensionen und Margin

**Features:**
- Berechnet Modul-Kanten basierend auf Zentrumsposition
- Vergleicht mit Dach-Grenzen (mit Margin)
- Zeigt präzise Fehlermeldungen mit Koordinaten
- Verhindert Platzierung außerhalb des Dachs

**Algorithmus:**
```python
# Berechne Modul-Kanten
module_left = x - module_width/2
module_right = x + module_width/2
module_bottom = y - module_height/2
module_top = y + module_height/2

# Berechne Dach-Grenzen
roof_left = -roof_length/2
roof_right = roof_length/2
roof_bottom = -roof_width/2
roof_top = roof_width/2

# Prüfe Überschreitungen
if module_left < roof_left: # Linke Kante überschritten
if module_right > roof_right: # Rechte Kante überschritten
if module_bottom < roof_bottom: # Untere Kante überschritten
if module_top > roof_top: # Obere Kante überschritten
```

**Test-Ergebnisse:**
- ✓ Erkennt Überschreitungen aller vier Kanten
- ✓ Zeigt präzise Fehlermeldungen mit Koordinaten
- ✓ Verhindert ungültige Platzierungen
- ✓ Berücksichtigt Modul-Dimensionen korrekt

### 7.3 Warnungen anzeigen ✓

**Implementierung:**
- Detaillierte Fehlermeldungen in deutscher Sprache
- Unterschiedliche Meldungen für verschiedene Kollisionstypen
- Zeigt relevante Informationen (Abstände, Koordinaten, Modul-Nummern)

**Meldungstypen:**

1. **Modul-Überlappung:**
   ```
   ⚠️ Modul überlappt mit bestehendem Modul #1 (Abstand: X=0.50m, Y=0.00m)
   ```

2. **Linke Dachkante:**
   ```
   ⚠️ Modul überschreitet linke Dachkante (Modul-Kante: -5.03m < Dachkante: -5.00m)
   ```

3. **Rechte Dachkante:**
   ```
   ⚠️ Modul überschreitet rechte Dachkante (Modul-Kante: 6.53m > Dachkante: 5.00m)
   ```

4. **Obere Dachkante:**
   ```
   ⚠️ Modul überschreitet obere Dachkante (Modul-Kante: 4.38m > Dachkante: 4.00m)
   ```

5. **Untere Dachkante:**
   ```
   ⚠️ Modul überschreitet untere Dachkante (Modul-Kante: -4.38m < Dachkante: -4.00m)
   ```

6. **Keine Kollision:**
   ```
   ✓ Keine Kollision erkannt
   ```

**Features:**
- Emoji-Icons für bessere Sichtbarkeit (⚠️, ✓)
- Präzise Koordinaten-Angaben
- Modul-Nummern bei Überlappungen
- Konsistente Formatierung

### 7.4 Platzierung verhindern ✓

**Implementierung:**
- Integration in `handle_manual_add()` Funktion
- Integration in `handle_move_selected()` Funktion
- Verhindert ungültige Operationen vor Ausführung

**Workflow:**

1. **Manuelle Platzierung:**
   ```python
   # Prüfe Kollision vor Platzierung
   collision_result = check_module_collision(...)
   
   if collision_result["collision"]:
       return {"success": False, "message": collision_result["message"]}
   
   # Nur bei keiner Kollision: Modul hinzufügen
   existing_positions.append(new_position)
   ```

2. **Modul verschieben:**
   ```python
   # Prüfe Kollision für neue Position
   collision_result = check_module_collision(...)
   
   if collision_result["collision"]:
       return {"success": False, "message": "Verschieben nicht möglich"}
   
   # Nur bei keiner Kollision: Position aktualisieren
   positions[index] = new_position
   ```

**Features:**
- Verhindert ungültige Platzierungen komplett
- Erhält vorherigen Zustand bei Kollision
- Zeigt Fehlermeldung an Benutzer
- Keine Änderung am Session State bei Kollision

## Integration

### Betroffene Dateien

1. **utils/pv3d_placement_handler.py**
   - `check_module_collision()` - Hauptfunktion für Kollisionserkennung
   - `handle_manual_add()` - Verwendet Kollisionserkennung
   - `handle_move_selected()` - Verwendet Kollisionserkennung

2. **utils/pv3d_module_placement_ui.py**
   - Zeigt Warnungen in der UI an
   - Buttons für manuelle Platzierung und Verschiebung

3. **utils/pv3d_grid_calculator.py**
   - Stellt Modul-Dimensionen bereit (PV_W, PV_H)
   - Stellt Standard-Margin bereit (DEFAULT_MARGIN)

### Verwendung

```python
from utils.pv3d_placement_handler import check_module_collision

# Prüfe Kollision
result = check_module_collision(
    new_position=(x, y, z),
    existing_positions=[(x1, y1, z1), (x2, y2, z2), ...],
    roof_length=10.0,
    roof_width=8.0,
    margin=0.30,
    orientation="portrait"
)

# Auswerten
if result["collision"]:
    print(f"Kollision erkannt: {result['message']}")
    print(f"Typ: {result['type']}")  # "module" oder "boundary"
    if result["type"] == "module":
        print(f"Kollidiert mit Modul #{result['colliding_index'] + 1}")
else:
    print("Keine Kollision - Platzierung erlaubt")
```

## Tests

### Test-Dateien

1. **test_collision_detection_task11.py**
   - 10 umfassende Unit-Tests
   - Testet alle Kollisionstypen
   - Testet beide Orientierungen
   - Testet Edge-Cases

2. **test_collision_detection_integration.py**
   - 6 Integrationstests
   - Testet Workflow mit Session State
   - Testet manuelle Platzierung
   - Testet Verschiebung
   - Testet Warnmeldungen

### Test-Ergebnisse

**Unit Tests (test_collision_detection_task11.py):**
```
✓ Test 1: No Collision (Well-Separated Modules)
✓ Test 2: Module-to-Module Overlap
✓ Test 3: Exact Overlap (Same Position)
✓ Test 4: Boundary Violation (Left Edge)
✓ Test 5: Boundary Violation (Right Edge)
✓ Test 6: Boundary Violation (Top Edge)
✓ Test 7: Boundary Violation (Bottom Edge)
✓ Test 8: Multiple Existing Modules
✓ Test 9: Landscape Orientation
✓ Test 10: Edge Case - Just Touching

TEST RESULTS: 10 passed, 0 failed
```

**Integration Tests (test_collision_detection_integration.py):**
```
✓ 7.1 - Module Overlap Prevention
✓ 7.1 - Valid Placement Allowed
✓ 7.2 - Boundary Violation Prevention
✓ 7.1 + 7.2 - Move Collision Detection
✓ 7.3 - Warning Messages
✓ 7.1 - Orientation Support

TEST RESULTS: 6 passed, 0 failed
```

### Tests ausführen

```bash
# Unit Tests
python test_collision_detection_task11.py

# Integration Tests
python test_collision_detection_integration.py
```

## Technische Details

### Koordinatensystem

- **Ursprung:** Zentrum des Dachs (0, 0)
- **X-Achse:** Länge des Dachs (-length/2 bis +length/2)
- **Y-Achse:** Breite des Dachs (-width/2 bis +width/2)
- **Z-Achse:** Höhe über Wandhöhe

### Modul-Dimensionen

- **Portrait (Standard):**
  - Breite: 1.05m (PV_W)
  - Höhe: 1.76m (PV_H)
  - Dicke: 0.04m (PV_T)

- **Landscape:**
  - Breite: 1.76m (PV_H)
  - Höhe: 1.05m (PV_W)
  - Dicke: 0.04m (PV_T)

### Margin

- **Standard-Margin:** 0.30m (30cm)
- Abstand von allen Dachkanten
- Wird bei Grenz-Prüfung berücksichtigt

### Kollisions-Algorithmus

**Bounding Box Collision Detection (AABB):**

1. Berechne Modul-Zentren: `(x1, y1)` und `(x2, y2)`
2. Berechne Abstände: `dx = |x1 - x2|`, `dy = |y1 - y2|`
3. Berechne Modul-Dimensionen basierend auf Orientierung
4. Prüfe Überlappung:
   - Überlappung in X wenn: `dx < module_width`
   - Überlappung in Y wenn: `dy < module_height`
   - Kollision wenn: Überlappung in X UND Y

**Vorteile:**
- Sehr schnell (O(1) pro Vergleich)
- Einfach zu implementieren
- Präzise für rechteckige Module
- Funktioniert mit beiden Orientierungen

## Performance

### Komplexität

- **Einzelne Kollisionsprüfung:** O(1)
- **Prüfung gegen N Module:** O(N)
- **Automatische Platzierung:** O(N²) im worst case

### Optimierungen

1. **Early Exit:** Stoppt bei erster Kollision
2. **Bounding Box:** Schnelle AABB-Prüfung
3. **Keine komplexen Geometrie-Berechnungen**

### Limits

- Maximal 200 Module (MAX_MODULES) für Performance
- Bei mehr Modulen: Automatische Begrenzung

## Bekannte Einschränkungen

1. **2D-Kollisionserkennung:**
   - Prüft nur X-Y-Ebene
   - Z-Koordinate wird nicht für Kollision verwendet
   - Ausreichend für flache Dächer und parallele Module

2. **Rechteckige Bounding Boxes:**
   - Keine Rotation der Bounding Box
   - Module werden als achsen-ausgerichtete Rechtecke behandelt
   - Bei gedrehten Modulen: Konservative Kollisionserkennung

3. **Keine Verschattungs-Analyse:**
   - Erkennt nur physische Überlappungen
   - Keine Berücksichtigung von Schatten
   - Für Verschattung: Separate Analyse erforderlich

## Zukünftige Erweiterungen

### Mögliche Verbesserungen

1. **3D-Kollisionserkennung:**
   - Berücksichtigung von Z-Koordinaten
   - Wichtig für aufgeständerte Module
   - Erkennung von Höhen-Konflikten

2. **Rotierte Bounding Boxes (OBB):**
   - Präzisere Kollisionserkennung für gedrehte Module
   - Oriented Bounding Box statt AABB
   - Komplexer aber genauer

3. **Verschattungs-Analyse:**
   - Berechnung von Schatten-Würfen
   - Berücksichtigung von Sonnenstand
   - Optimierung der Modul-Anordnung

4. **Spatial Hashing:**
   - Beschleunigung bei vielen Modulen (>200)
   - Grid-basierte Kollisionserkennung
   - O(1) statt O(N) für Nachbarschafts-Suche

5. **Kollisions-Vorschau:**
   - Echtzeit-Feedback während Drag
   - Visuelle Hervorhebung von Kollisionen
   - Snap-to-Grid mit Kollisions-Vermeidung

## Zusammenfassung

Task 7 (Kollisionserkennung) ist vollständig implementiert und getestet:

✅ **7.1 Modul-Modul Kollision**
- Erkennt Überlappungen zwischen Modulen
- Funktioniert mit beiden Orientierungen
- Identifiziert kollidierendes Modul

✅ **7.2 Modul-Dach Kollision**
- Erkennt Überschreitungen aller vier Dachkanten
- Berücksichtigt Modul-Dimensionen und Margin
- Zeigt präzise Koordinaten

✅ **7.3 Warnungen anzeigen**
- Detaillierte Fehlermeldungen
- Unterschiedliche Meldungen für verschiedene Typen
- Benutzerfreundliche Formatierung

✅ **7.4 Platzierung verhindern**
- Verhindert ungültige Platzierungen komplett
- Integration in manuelle Platzierung
- Integration in Verschiebung

### Test-Abdeckung

- **16 Tests insgesamt** (10 Unit + 6 Integration)
- **100% Pass-Rate**
- Alle Requirements abgedeckt

### Qualität

- ✓ Vollständige Dokumentation
- ✓ Umfassende Tests
- ✓ Benutzerfreundliche Fehlermeldungen
- ✓ Performance-optimiert
- ✓ Wartbar und erweiterbar

**Status: ABGESCHLOSSEN ✓**
