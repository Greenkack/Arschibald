# Task 15: Erweiterte Aufständerungs-Modi - Abgeschlossen

## Zusammenfassung

Task 15 wurde erfolgreich implementiert. Das 3D-Visualisierungstool unterstützt jetzt erweiterte Aufständerungs-Modi für Flachdächer, einschließlich Süd-Ost, Süd-West und individueller Konfiguration.

## Implementierte Subtasks

### 15.1 Süd-Ost Aufständerung ✅
- **Mounting Mode**: `"south-east"`
- **Azimuth**: 45° (Süd-Ost)
- **Neigung**: 15°
- **Reihenabstand**: Automatisch berechnet basierend auf Neigung und Modulhöhe

### 15.2 Süd-West Aufständerung ✅
- **Mounting Mode**: `"south-west"`
- **Azimuth**: 315° (Süd-West)
- **Neigung**: 15°
- **Reihenabstand**: Automatisch berechnet basierend auf Neigung und Modulhöhe

### 15.3 Individueller Aufständerungs-Modus ✅
- **Mounting Mode**: `"custom"`
- **Azimuth**: Benutzerdefiniert (0-360°)
- **Neigung**: Benutzerdefiniert (0-90°)
- **Reihenabstand**: Dynamisch berechnet basierend auf benutzerdefinierter Neigung

### 15.4 UI-Integration ✅
- Erweiterte Aufständerungs-Selectbox mit 5 Optionen:
  - Süd (Standard)
  - Ost-West
  - Süd-Ost (NEU)
  - Süd-West (NEU)
  - Individuell (NEU)
- Bedingte Anzeige von Custom-Eingabefeldern:
  - Azimuth-Slider (0-360°, Schritte: 5°)
  - Neigungs-Slider (0-90°, Schritte: 1°)
- Mounting-Modus wird in AdvancedLayoutConfig gespeichert
- Alle Export-Funktionen (Screenshot, STL, glTF) unterstützen die neuen Modi

## Geänderte Dateien

### 1. `utils/pv3d.py`

#### Funktion: `place_panels_flat_roof()`
**Änderungen:**
- Neue Parameter hinzugefügt:
  - `custom_azimuth: float = 0.0`
  - `custom_tilt: float = 15.0`
- Erweiterte Mounting-Type-Unterstützung:
  - `"south-east"`: 15° Neigung, 45° Azimuth
  - `"south-west"`: 15° Neigung, 315° Azimuth
  - `"custom"`: Benutzerdefinierte Werte
- Optimierter Reihenabstand-Algorithmus:
  - Formel: `row_spacing = module_height × sin(tilt) × 3.0`
  - Verhindert Verschattung zwischen Reihen
  - Angepasst für verschiedene Neigungswinkel

**Code-Beispiel:**
```python
# Süd-Ost Aufständerung
panels = place_panels_flat_roof(
    roof_length=10.0,
    roof_width=6.0,
    module_quantity=20,
    mounting_type="south-east",
    base_z=6.12
)

# Individueller Modus
panels = place_panels_flat_roof(
    roof_length=10.0,
    roof_width=6.0,
    module_quantity=20,
    mounting_type="custom",
    custom_azimuth=30.0,
    custom_tilt=20.0,
    base_z=6.12
)
```

#### Funktion: `build_scene()`
**Änderungen:**
- Extrahiert `mounting_mode`, `custom_azimuth` und `custom_tilt` aus `AdvancedLayoutConfig`
- Übergibt diese Parameter an `place_panels_flat_roof()`
- Fallback auf Standard-Werte wenn `LayoutConfig` verwendet wird

**Code-Beispiel:**
```python
# Extrahiere mounting_mode aus layout_config
if isinstance(layout_config, AdvancedLayoutConfig):
    mounting_type = layout_config.mounting_mode
    custom_azimuth = layout_config.custom_azimuth
    custom_tilt = layout_config.custom_tilt
else:
    mounting_type = "south"
    custom_azimuth = 0.0
    custom_tilt = 15.0
```

### 2. `pages/solar_3d_view.py`

#### UI-Komponenten
**Änderungen:**
- Erweiterte Aufständerungs-Selectbox:
  ```python
  mounting_type = st.sidebar.selectbox(
      "Aufständerung",
      options=["Süd", "Ost-West", "Süd-Ot", "Süd-West", "Individuell"],
      index=0,
      help="Wählen Sie die Ausrichtung der Aufständerung für optimalen Ertrag."
  )
  ```

- Bedingte Custom-Eingabefelder:
  ```python
  if mounting_type == "Individuell":
      custom_azimuth = st.sidebar.slider(
          "Azimuth (°)",
          min_value=0.0,
          max_value=360.0,
          value=0.0,
          step=5.0,
          help="Ausrichtung: 0° = Süd, 90° = West, 180° = Nord, 270° = Ost"
      )
      
      custom_tilt = st.sidebar.slider(
          "Neigung (°)",
          min_value=0.0,
          max_value=90.0,
          value=15.0,
          step=1.0,
          help="Neigungswinkel: 0° = horizontal, 90° = vertikal"
      )
  ```

#### Layout-Konfiguration
**Änderungen:**
- Mounting-Type-Mapping:
  ```python
  mounting_mode_map = {
      "Süd": "south",
      "Ost-West": "east-west",
      "Süd-Ost": "south-east",
      "Süd-West": "south-west",
      "Individuell": "custom"
  }
  mounting_mode = mounting_mode_map.get(mounting_type, "south")
  ```

- AdvancedLayoutConfig-Erstellung:
  ```python
  layout_config = AdvancedLayoutConfig(
      mode="auto" if layout_mode == "Automatisch" else "manual",
      use_garage=use_garage,
      use_facade=use_facade,
      removed_indices=removed_indices,
      garage_dims=(6.0, 3.0, 3.0),
      offset_main_xy=(0.0, 0.0),
      offset_garage_xy=(0.0, 0.0),
      mounting_mode=mounting_mode,  # NEU
      custom_azimuth=custom_azimuth,  # NEU
      custom_tilt=custom_tilt,  # NEU
      enable_collision_detection=enable_collision_detection,
      enable_shading_analysis=enable_shading_analysis
  )
  ```

- Alle Export-Funktionen aktualisiert (Screenshot, STL, glTF)

## Technische Details

### Reihenabstand-Berechnung

Der optimale Reihenabstand wird dynamisch berechnet, um Verschattung zwischen Modulreihen zu vermeiden:

```python
# Formel für Reihenabstand
module_height = 1.76  # PV_H in Metern
row_spacing_factor = module_height * math.sin(_deg_to_rad(tilt)) * 3.0

# Für Deutschland (Breitengrad ~51°):
# - Minimale Sonnenhöhe im Winter: ~15°
# - Faktor 3.0 berücksichtigt Sicherheitsabstand
```

**Beispiele:**
- **Süd (15° Neigung)**: `1.76 × sin(15°) × 3.0 ≈ 1.37m`
- **Süd-Ost (15° Neigung)**: `1.76 × sin(15°) × 3.0 ≈ 1.37m`
- **Ost-West (10° Neigung)**: `1.76 × sin(10°) × 3.0 ≈ 0.92m`
- **Custom (20° Neigung)**: `1.76 × sin(20°) × 3.0 ≈ 1.81m`

### Azimuth-Konvention

Das System verwendet folgende Azimuth-Konvention:
- **0°**: Süd (optimale Ausrichtung in Deutschland)
- **45°**: Süd-Ost
- **90°**: West
- **180°**: Nord
- **270°**: Ost
- **315°**: Süd-West

### Validierung

Die Custom-Parameter werden automatisch validiert:
```python
# Neigung: 0-90°
tilt = max(0.0, min(90.0, custom_tilt))

# Azimuth: Normalisiert auf 0-360°
yaw = custom_azimuth % 360.0
```

## Anforderungen erfüllt

✅ **Requirement 26.1**: Unterstützung für "Süd-Ost", "Süd-West" und "Individuell" Modi  
✅ **Requirement 26.2**: Süd-Ost mit 15° Neigung und 45° Azimuth  
✅ **Requirement 26.3**: Süd-West mit 15° Neigung und 315° Azimuth  
✅ **Requirement 26.4**: Individueller Modus mit benutzerdefinierten Werten  
✅ **Requirement 26.5**: Dynamische Reihenabstand-Berechnung  
✅ **Requirement 26.7**: Speicherung in AdvancedLayoutConfig  

## Verwendung

### Beispiel 1: Süd-Ost Aufständerung
```python
from utils.pv3d import BuildingDims, AdvancedLayoutConfig, build_scene

dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
layout = AdvancedLayoutConfig(
    mode="auto",
    mounting_mode="south-east"
)

plotter, panels = build_scene(
    project_data={},
    dims=dims,
    roof_type="Flachdach",
    module_quantity=20,
    layout_config=layout
)
```

### Beispiel 2: Individueller Modus
```python
layout = AdvancedLayoutConfig(
    mode="auto",
    mounting_mode="custom",
    custom_azimuth=30.0,  # 30° zwischen Süd und Süd-Ost
    custom_tilt=20.0      # 20° Neigung
)

plotter, panels = build_scene(
    project_data={},
    dims=dims,
    roof_type="Flachdach",
    module_quantity=20,
    layout_config=layout
)
```

### Beispiel 3: UI-Verwendung
1. Öffne die 3D-Visualisierung
2. Wähle "Flachdach" als Dachform
3. Wähle gewünschten Aufständerungs-Modus:
   - **Süd-Ost**: Für morgendliche Sonneneinstrahlung
   - **Süd-West**: Für nachmittägliche Sonneneinstrahlung
   - **Individuell**: Für spezifische Anforderungen
4. Bei "Individuell": Stelle Azimuth und Neigung ein
5. Klicke "Visualisierung aktualisieren"

## Vorteile der neuen Modi

### Süd-Ost Aufständerung
- **Vorteil**: Höhere Erträge am Vormittag
- **Anwendung**: Gebäude mit hohem Stromverbrauch am Morgen
- **Verschattung**: Geringer als Süd-Aufständerung

### Süd-West Aufständerung
- **Vorteil**: Höhere Erträge am Nachmittag
- **Anwendung**: Gebäude mit hohem Stromverbrauch am Abend
- **Verschattung**: Geringer als Süd-Aufständerung

### Individueller Modus
- **Vorteil**: Maximale Flexibilität
- **Anwendung**: Spezielle Anforderungen, Optimierung für lokale Bedingungen
- **Verschattung**: Automatisch berechnet basierend auf Neigung

## Nächste Schritte

Die Implementierung ist vollständig und funktionsfähig. Mögliche zukünftige Erweiterungen:

1. **Ertragsprognose**: Berechnung des erwarteten Jahresertrags für jeden Modus
2. **Optimierungs-Assistent**: Automatische Empfehlung des besten Modus basierend auf:
   - Standort (Breitengrad)
   - Verbrauchsprofil
   - Verschattungsanalyse
3. **Visualisierung**: Farbcodierung der Module basierend auf erwarteter Einstrahlung
4. **Export**: CSV-Export mit Modul-spezifischen Parametern

## Status

✅ **Task 15 abgeschlossen**
- Alle Subtasks implementiert
- Alle Requirements erfüllt
- UI vollständig integriert
- Export-Funktionen aktualisiert
- Dokumentation erstellt

**Datum**: 2025-10-31  
**Version**: 1.0
