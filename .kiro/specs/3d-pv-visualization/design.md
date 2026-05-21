# Design Document: 3D PV-Visualisierung

## Overview

Das 3D-Visualisierungstool ist ein vollständig integriertes Modul für die Streamlit-App "Arschibald", das eine realistische, interaktive Darstellung von Gebäuden mit PV-Modulbelegung ermöglicht. Das System nutzt PyVista/VTK für 3D-Rendering und stpyvista für die Streamlit-Integration.

### Hauptziele

1. **Dynamische Modellgenerierung**: Automatische Erstellung von 3D-Gebäudemodellen basierend auf Benutzereingaben
2. **Interaktive PV-Planung**: Automatische und manuelle Platzierung von PV-Modulen
3. **Nahtlose Integration**: Vollständige Anbindung an bestehende App-Daten (project_data, analysis_results)
4. **PDF-Export**: Automatische Einbettung von 3D-Screenshots in PDF-Angebote
5. **Performance**: Flüssiges Rendering ohne Beeinträchtigung der restlichen App

### Technologie-Stack

- **3D-Rendering**: PyVista (>= 0.43.10) mit VTK (>= 9.3.0)
- **Streamlit-Integration**: stpyvista (>= 0.1.4)
- **Geometrie-Verarbeitung**: NumPy (>= 1.26), trimesh (>= 4.4.9)
- **PDF-Integration**: ReportLab (>= 4.2.2), pikepdf (>= 9.0.0)
- **Bildverarbeitung**: Pillow (für PNG-Konvertierung)

## Architecture

### Modulstruktur

```
streamlit_app/
├── utils/
│   ├── pv3d.py                    # Kern-3D-Engine
│   └── pdf_visual_inject.py       # PDF-Integration
└── pages/
    └── solar_3d_view.py           # UI-Seite

pdf_template_engine/
└── (Integration in bestehende PDF-Pipeline)
```

### Datenfluss

```
Benutzer-Eingabe (Bedarfsanalyse/Solarkalkulator)
    ↓
st.session_state.project_data
st.session_state.analysis_results
    ↓
pv3d.build_scene() → PyVista Plotter
    ↓
stpyvista() → Interaktiver 3D-Viewer (Browser)
    ↓
pv3d.render_image_bytes() → PNG-Bytes
    ↓
pdf_visual_inject.make_pv3d_image_flowable() → ReportLab Image
    ↓
PDF-Generator → Finales PDF-Angebot
```

## Components and Interfaces

### 1. Core 3D Engine (pv3d.py)

#### Datenklassen

```python
@dataclass
class BuildingDims:
    """Gebäudedimensionen"""
    length_m: float = 10.0
    width_m: float = 6.0
    wall_height_m: float = 6.0

@dataclass
class LayoutConfig:
    """PV-Layout-Konfiguration"""
    mode: str = "auto"  # "auto" | "manual"
    use_garage: bool = False
    use_facade: bool = False
    removed_indices: List[int] = None
    garage_dims: Tuple[float, float, float] = (6.0, 3.0, 3.0)
    offset_main_xy: Tuple[float, float] = (0.0, 0.0)
    offset_garage_xy: Tuple[float, float] = (0.0, 0.0)
```


#### Hauptfunktionen

**build_scene()**
- **Zweck**: Erstellt die komplette 3D-Szene mit Gebäude, Dach und PV-Modulen
- **Input**: project_data, BuildingDims, roof_type, LayoutConfig, module_quantity
- **Output**: (PyVista Plotter, Dict mit Panel-Listen)
- **Logik**:
  1. Erstellt PyVista Plotter mit weißem Hintergrund
  2. Generiert Bodenplatte (3x Gebäudegröße, 0.05m dick)
  3. Erstellt Gebäudewände als Quader
  4. Generiert Dach basierend auf roof_type
  5. Rotiert Szene basierend auf Ausrichtung
  6. Platziert Kompass-Pfeil
  7. Berechnet und platziert PV-Module
  8. Fügt optional Garage und Fassadenmodule hinzu

**Dachgeometrie-Funktionen**
- `make_roof_flat()`: Flachdach als dünner Quader (0.12m)
- `make_roof_gable()`: Satteldach mit zwei geneigten Flächen
- `make_roof_hip()`: Walmdach mit vier geneigten Flächen
- `make_roof_pent()`: Pultdach als gekippte Platte
- `make_roof_pyramid()`: Zeltdach mit zentralem Gipfel

**PV-Modul-Funktionen**
- `make_panel()`: Erstellt einzelnes PV-Modul (1.05×1.76×0.04m)
- `grid_positions()`: Berechnet Rasterposit ionen für Module
- Unterstützt Rotation (yaw, tilt) für Aufständerung

**Export-Funktionen**
- `render_image_bytes()`: Off-Screen Screenshot als PNG-Bytes
- `export_stl()`: 3D-Modell als STL-Datei
- `export_gltf()`: 3D-Modell als glTF/glb-Datei

#### Hilfsfunktionen

**Datenextraktion (robust mit Fallbacks)**
- `_safe_get_orientation()`: Liest Ausrichtung aus project_data
- `_safe_get_roof_inclination_deg()`: Liest Dachneigung
- `_safe_get_roof_covering()`: Liest Dachdeckung
- `_roof_color_from_covering()`: Mappt Deckung zu Farbe

**Geometrie-Primitives**
- `make_box()`: Erstellt Quader mit Origin-Kontrolle
- `_deg_to_rad()`: Grad zu Radiant Konvertierung

### 2. UI-Seite (solar_3d_view.py)

#### Seitenstruktur

```
Streamlit Page: "3D PV-Visualisierung"
├── Sidebar (Einstellungen)
│   ├── Gebäudedimensionen (Länge, Breite, Höhe)
│   ├── Dachform-Auswahl
│   ├── Belegungsmodus (Auto/Manuell)
│   ├── Flachdach-Aufständerung
│   ├── Platzmangel-Fallback (Garage, Fassade)
│   ├── Manuelle Indizes-Eingabe
│   └── Aktionen (Aktualisieren, Reset, Speichern, Laden)
├── Hauptbereich (2 Spalten)
│   ├── Linke Spalte (60%): 3D-Viewer
│   └── Rechte Spalte (40%): Status & Export
│       ├── Metriken (Gewählt, Platziert, Fehlend)
│       ├── Warnungen/Erfolg
│       └── Export-Buttons (Screenshot, STL, glTF)
└── Expandable: Datenquellen-Info
```

#### Session State Management

```python
# Initialisierung
if "pv3d_layout_json" not in st.session_state:
    st.session_state["pv3d_layout_json"] = LayoutConfig().to_json()

if "pv3d_last_rendered" not in st.session_state:
    st.session_state["pv3d_last_rendered"] = False

if "_pv3d_plotter" not in st.session_state:
    st.session_state["_pv3d_plotter"] = None
```

#### Interaktionslogik

1. **Initialisierung**: Liest project_data und analysis_results
2. **Eingabe-Verarbeitung**: Sammelt Dimensionen, Dachform, Modus
3. **Rendering-Trigger**: Button-Klick oder erste Anzeige
4. **Szenen-Erstellung**: Ruft build_scene() auf
5. **Viewer-Anzeige**: Nutzt stpyvista() für interaktive Darstellung
6. **Status-Update**: Berechnet und zeigt Kapazität/Fehlende Module
7. **Export-Handling**: Generiert Downloads bei Button-Klick

### 3. PDF-Integration (pdf_visual_inject.py)

#### Funktionen

**make_pv3d_image_flowable()**
- **Zweck**: Erstellt ReportLab Image-Objekt für PDF
- **Input**: project_data, BuildingDims, roof_type, module_quantity, LayoutConfig, width_cm
- **Output**: ReportLab Image Flowable oder None
- **Prozess**:
  1. Ruft render_image_bytes() auf
  2. Konvertiert PNG-Bytes zu BytesIO
  3. Erstellt Image mit Breite width_cm und Höhe (width_cm * 0.62)
  4. Gibt Image-Flowable zurück

**get_pv3d_png_bytes_for_pdf()**
- **Zweck**: Direkte PNG-Bytes für flexible PDF-Integration
- **Output**: PNG-Bytes (1600×1000 px, isometrische Ansicht)

#### Integration in bestehenden PDF-Generator

```python
# In pdf_generator.py oder Template-Engine
from streamlit_app.utils.pdf_visual_inject import make_pv3d_image_flowable
from streamlit_app.utils.pv3d import BuildingDims, LayoutConfig

# Während Story-Aufbau
dims = BuildingDims(length_m=10, width_m=6, wall_height_m=6)
layout = LayoutConfig(mode="auto")
roof_type = project_data.get("project_details", {}).get("roof_type", "Flachdach")
module_qty = analysis_results.get("module_quantity", 0)

flow = make_pv3d_image_flowable(
    project_data, dims, roof_type, module_qty, layout, width_cm=17.0
)
if flow:
    Story.append(flow)
    Story.append(Paragraph(
        "Abb.: 3D-Visualisierung der geplanten PV-Belegung",
        styles["Normal"]
    ))
```

## Data Models

### project_data Struktur (Eingabe)

```python
{
    "project_details": {
        "roof_type": str,              # "Flachdach", "Satteldach", etc.
        "roof_orientation": str,        # "Süd", "Ost", "West", "Nord"
        "roof_inclination_deg": float,  # 0-90
        "roof_covering_type": str,      # "Ziegel", "Beton", etc.
        "free_roof_area_m2": float,     # Optional
        # ... weitere Felder
    },
    "module_quantity": int,  # Fallback wenn nicht in analysis_results
    # ... weitere Felder
}
```

### analysis_results Struktur (Eingabe)

```python
{
    "module_quantity": int,  # Primäre Quelle für Modulanzahl
    "system_kwp": float,
    "annual_pv_production_kwh": float,
    # ... weitere Berechnungsergebnisse
}
```

### LayoutConfig (Intern)

```python
{
    "mode": "auto" | "manual",
    "use_garage": bool,
    "use_facade": bool,
    "removed_indices": [int, ...],  # 0-basierte Indizes
    "garage_dims": (float, float, float),  # (L, B, H)
    "offset_main_xy": (float, float),
    "offset_garage_xy": (float, float)
}
```

### Scene Output (build_scene Return)

```python
(
    plotter: pv.Plotter,  # PyVista Plotter-Objekt
    panels: {
        "main": [pv.PolyData, ...],     # Module auf Hauptdach
        "garage": [pv.PolyData, ...],   # Module auf Garage
        "facade": [pv.PolyData, ...]    # Module an Fassade
    }
)
```

## Error Handling

### Fehlerklassen und Behandlung

1. **Daten-Fehler**
   - Fehlende/ungültige project_data: Fallback auf Standardwerte
   - Fehlende module_quantity: Warnung + 0 Module
   - Ungültige Dimensionen: Clipping auf gültige Bereiche

2. **Rendering-Fehler**
   - PyVista-Fehler: Try-Catch mit Fehlermeldung
   - Off-Screen Rendering fehlgeschlagen: Leere Bytes zurückgeben
   - WebGL nicht verfügbar: Browser-Warnung

3. **Export-Fehler**
   - Screenshot fehlgeschlagen: Fehlermeldung, kein Download
   - STL/glTF Export fehlgeschlagen: Fehlermeldung
   - PDF-Integration fehlgeschlagen: PDF ohne Bild fortsetzen

### Fehlerbehandlungs-Pattern

```python
try:
    plotter, panels = build_scene(...)
    stpyvista(plotter, key="pv3d_viewer")
except Exception as e:
    st.error(f"3D-Visualisierung konnte nicht geladen werden: {e}")
    st.info("Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut.")
finally:
    if plotter:
        try:
            plotter.close()
        except:
            pass
```

## Testing Strategy

### Unit Tests

1. **Geometrie-Funktionen**
   - Test make_box() mit verschiedenen Dimensionen
   - Test Dachformen (flat, gable, hip, pent, pyramid)
   - Test make_panel() mit Rotation

2. **Datenextraktion**
   - Test _safe_get_* Funktionen mit vollständigen Daten
   - Test mit fehlenden Keys (Fallbacks)
   - Test mit ungültigen Werten

3. **Layout-Konfiguration**
   - Test LayoutConfig.to_json() / from_json()
   - Test mit verschiedenen Parameterkombinationen

### Integration Tests

1. **Szenen-Erstellung**
   - Test build_scene() mit verschiedenen Dachtypen
   - Test automatische Modul-Platzierung
   - Test manuelle Modul-Entfernung
   - Test Garage-Hinzufügung
   - Test Fassaden-Belegung

2. **PDF-Integration**
   - Test render_image_bytes() Ausgabe
   - Test make_pv3d_image_flowable() mit ReportLab
   - Test PDF-Generierung mit 3D-Bild

3. **UI-Integration**
   - Test Streamlit-Seite lädt ohne Fehler
   - Test Button-Interaktionen
   - Test Session State Persistenz

### Performance Tests

1. **Rendering-Geschwindigkeit**
   - Szenen-Erstellung < 1 Sekunde
   - Off-Screen Screenshot < 2 Sekunden
   - UI-Update < 500ms

2. **Speicher-Nutzung**
   - Plotter-Objekte werden korrekt freigegeben
   - Keine Memory Leaks bei wiederholtem Rendering

3. **Skalierbarkeit**
   - Test mit 10, 50, 100 Modulen
   - Test mit komplexen Dachformen

### Manuelle Tests

1. **Browser-Kompatibilität**
   - Chrome, Firefox, Edge, Safari
   - WebGL-Unterstützung prüfen

2. **Benutzer-Workflows**
   - Kompletter Durchlauf: Eingabe → 3D → Export → PDF
   - Verschiedene Dachformen durchspielen
   - Manueller Modus mit Modul-Entfernung

3. **Fehlerszenarien**
   - Ungültige Eingaben
   - Extreme Werte (sehr große/kleine Gebäude)
   - Netzwerk-Unterbrechungen

## Performance Considerations

### Optimierungen

1. **Mesh-Zusammenführung**
   - Module zu kombinierten Meshes zusammenfassen
   - Reduziert Draw-Calls von N auf 1-3

2. **Lazy Loading**
   - 3D-Szene nur bei Bedarf erstellen
   - Plotter im Session State cachen

3. **Off-Screen Rendering**
   - Separate Plotter-Instanz für Screenshots
   - Keine Blockierung der UI

4. **Geometrie-Vereinfachung**
   - Einfache Primitives (Quader, Dreiecke)
   - Keine hochauflösenden Texturen

### Ressourcen-Management

1. **Plotter Lifecycle**
   ```python
   try:
       plotter = pv.Plotter(off_screen=True)
       # ... Rendering
   finally:
       plotter.close()  # Wichtig!
   ```

2. **Session State Cleanup**
   - Alte Plotter-Objekte entfernen
   - Layout-Konfiguration kompakt halten

3. **Memory Limits**
   - Max. 100 Module gleichzeitig
   - Screenshot-Auflösung begrenzt (1600×1000)

## Security Considerations

1. **Input Validation**
   - Dimensionen auf gültige Bereiche begrenzen
   - Modul-Indizes validieren
   - JSON-Parsing mit Fehlerbehandlung

2. **File Operations**
   - Export-Dateien in temporäre Verzeichnisse
   - Keine Pfad-Traversal-Angriffe

3. **Resource Limits**
   - Maximale Polygon-Anzahl begrenzen
   - Timeout für Rendering-Operationen

## Deployment Considerations

### Dependencies

```txt
# requirements.txt Ergänzungen
pyvista>=0.43.10
vtk>=9.3.0
stpyvista>=0.1.4
numpy>=1.26
trimesh>=4.4.9
reportlab>=4.2.2
pikepdf>=9.0.0
Pillow>=10.0.0
```

### System Requirements

- **Python**: 3.10+
- **Browser**: Moderner Browser mit WebGL-Unterstützung
- **RAM**: Min. 4GB (8GB empfohlen)
- **GPU**: Optional, aber empfohlen für flüssiges Rendering

### Installation

```bash
# Installation der Dependencies
pip install -r requirements.txt

# Für Linux: OpenGL-Bibliotheken
sudo apt-get install libgl1-mesa-glx libglu1-mesa

# Für macOS: Keine zusätzlichen Schritte
# Für Windows: Keine zusätzlichen Schritte
```

### Configuration

Keine spezielle Konfiguration erforderlich. Das Modul nutzt die bestehende Streamlit-Konfiguration.

## Advanced Features (Phase 2)

### 1. Individuelle Modul-Kontrolle

#### Erweiterte Datenstrukturen

```python
@dataclass
class ModuleTransform:
    """Transformation für einzelnes Modul"""
    index: int
    azimuth_deg: float = 0.0      # 0=Süd, 90=West, 180=Nord, 270=Ost
    tilt_deg: float = 15.0         # 0=horizontal, 90=vertikal
    offset_x: float = 0.0          # Verschiebung in X (m)
    offset_y: float = 0.0          # Verschiebung in Y (m)
    offset_z: float = 0.0          # Verschiebung in Z (m)
    group_id: Optional[str] = None # Gruppen-Zugehörigkeit

@dataclass
class ModuleGroup:
    """Gruppe von Modulen mit gemeinsamen Eigenschaften"""
    name: str
    module_indices: List[int]
    azimuth_deg: float = 0.0
    tilt_deg: float = 15.0
    color: str = "#000000"         # Optionale Gruppen-Farbe

@dataclass
class AdvancedLayoutConfig(LayoutConfig):
    """Erweiterte Layout-Konfiguration"""
    module_transforms: Dict[int, ModuleTransform] = None
    module_groups: Dict[str, ModuleGroup] = None
    mounting_mode: str = "south"   # "south", "east-west", "south-east", "south-west", "custom"
    custom_azimuth: float = 0.0
    custom_tilt: float = 15.0
    enable_collision_detection: bool = True
    enable_shading_analysis: bool = False
```

#### Erweiterte Funktionen

**apply_module_transform()**
- **Zweck**: Wendet individuelle Transformation auf Modul an
- **Input**: ModuleTransform, Basis-Position
- **Output**: Transformiertes PyVista Mesh
- **Logik**:
  1. Erstellt Modul an Basis-Position
  2. Rotiert um Y-Achse (Neigung)
  3. Rotiert um Z-Achse (Azimuth)
  4. Verschiebt um Offset (X, Y, Z)
  5. Prüft Kollisionen wenn aktiviert

**detect_collisions()**
- **Zweck**: Erkennt Überschneidungen zwischen Modulen
- **Input**: Liste von Modul-Meshes
- **Output**: Liste von Kollisions-Paaren
- **Algorithmus**: Bounding-Box Intersection Test

**calculate_shading()**
- **Zweck**: Berechnet Verschattung für gegebene Sonnenposition
- **Input**: Modul-Liste, Sonnen-Azimuth, Sonnen-Elevation
- **Output**: Verschattungsgrad pro Modul (0-100%)
- **Methode**: Ray-Casting von Modulzentrum zur Sonne

### 2. Interaktive Modul-Auswahl

#### UI-Komponenten

**ModuleSelector**
- Klick-basierte Auswahl im 3D-Viewer
- Hervorhebung durch Farb-Änderung (z.B. gelb)
- Mehrfachauswahl mit Strg+Klick
- Eigenschaften-Panel für ausgewählte Module

**TransformControls**
- Visuelle Rotations-Handles (Ringe)
- Verschiebe-Pfeile (X, Y, Z)
- Snap-to-Grid Funktion
- Echtzeit-Vorschau

#### Implementierung

```python
# In solar_3d_view.py
if "selected_modules" not in st.session_state:
    st.session_state["selected_modules"] = []

# Auswahl-Logik
selected_idx = st.number_input("Modul auswählen (Index)", 0, max_modules-1)
if st.button("Auswählen"):
    st.session_state["selected_modules"].append(selected_idx)

# Transformations-Controls für ausgewählte Module
if st.session_state["selected_modules"]:
    st.subheader("Ausgewählte Module bearbeiten")
    azimuth = st.slider("Azimuth (°)", 0, 360, 0)
    tilt = st.slider("Neigung (°)", 0, 90, 15)
    offset_x = st.number_input("X-Offset (m)", -5.0, 5.0, 0.0, 0.1)
    offset_y = st.number_input("Y-Offset (m)", -5.0, 5.0, 0.0, 0.1)
    offset_z = st.number_input("Z-Offset (m)", -2.0, 2.0, 0.0, 0.1)
```

### 3. Verschattungs-Analyse

#### Sonnenpositions-Berechnung

```python
def calculate_sun_position(latitude: float, day_of_year: int, hour: float) -> Tuple[float, float]:
    """
    Berechnet Sonnenposition (Azimuth, Elevation)
    
    Args:
        latitude: Breitengrad (z.B. 51.0 für Deutschland)
        day_of_year: Tag im Jahr (1-365)
        hour: Stunde (0-24)
    
    Returns:
        (azimuth_deg, elevation_deg)
    """
    # Vereinfachte Berechnung (für Präzision: pvlib verwenden)
    declination = 23.45 * np.sin(np.radians(360/365 * (day_of_year - 81)))
    hour_angle = 15 * (hour - 12)
    
    elevation = np.arcsin(
        np.sin(np.radians(latitude)) * np.sin(np.radians(declination)) +
        np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle))
    )
    
    azimuth = np.arctan2(
        np.sin(np.radians(hour_angle)),
        np.cos(np.radians(hour_angle)) * np.sin(np.radians(latitude)) - 
        np.tan(np.radians(declination)) * np.cos(np.radians(latitude))
    )
    
    return np.degrees(azimuth), np.degrees(elevation)
```

#### Verschattungs-Visualisierung

```python
def visualize_shading(plotter, modules, sun_azimuth, sun_elevation):
    """
    Färbt Module basierend auf Verschattungsgrad
    
    Args:
        plotter: PyVista Plotter
        modules: Liste von Modul-Meshes
        sun_azimuth: Sonnen-Azimuth (°)
        sun_elevation: Sonnen-Elevation (°)
    """
    for i, module in enumerate(modules):
        shading_pct = calculate_shading_for_module(module, modules, sun_azimuth, sun_elevation)
        
        # Farbskala: Grün (0%) -> Gelb (50%) -> Rot (100%)
        if shading_pct < 50:
            color = interpolate_color("#00ff00", "#ffff00", shading_pct / 50)
        else:
            color = interpolate_color("#ffff00", "#ff0000", (shading_pct - 50) / 50)
        
        plotter.add_mesh(module, color=color, opacity=0.9)
```

### 4. Optimierungs-Assistent

#### Optimierungs-Algorithmus

```python
def optimize_layout(
    building_dims: BuildingDims,
    roof_type: str,
    target_modules: int,
    optimization_goal: str = "max_modules"  # "max_modules" | "max_yield" | "balanced"
) -> List[AdvancedLayoutConfig]:
    """
    Findet optimale Layout-Konfigurationen
    
    Returns:
        Top 3 Konfigurationen sortiert nach Score
    """
    configurations = []
    
    # Strategie 1: Süd-Aufständerung
    config1 = generate_south_config(building_dims, target_modules)
    score1 = evaluate_config(config1, optimization_goal)
    configurations.append((config1, score1))
    
    # Strategie 2: Ost-West-Aufständerung
    config2 = generate_east_west_config(building_dims, target_modules)
    score2 = evaluate_config(config2, optimization_goal)
    configurations.append((config2, score2))
    
    # Strategie 3: Süd-Ost
    config3 = generate_south_east_config(building_dims, target_modules)
    score3 = evaluate_config(config3, optimization_goal)
    configurations.append((config3, score3))
    
    # Strategie 4: Gemischt (Süd + Ost-West)
    config4 = generate_mixed_config(building_dims, target_modules)
    score4 = evaluate_config(config4, optimization_goal)
    configurations.append((config4, score4))
    
    # Sortiere nach Score
    configurations.sort(key=lambda x: x[1], reverse=True)
    
    return [c[0] for c in configurations[:3]]

def evaluate_config(config: AdvancedLayoutConfig, goal: str) -> float:
    """
    Bewertet Konfiguration basierend auf Ziel
    
    Returns:
        Score (0-100)
    """
    score = 0.0
    
    if goal == "max_modules":
        # Maximiere Modulanzahl
        score += config.placed_modules * 10
        score -= config.shading_total * 0.5
    
    elif goal == "max_yield":
        # Maximiere Ertrag (berücksichtigt Verschattung stark)
        score += config.placed_modules * 5
        score -= config.shading_total * 2
        score += config.optimal_orientation_bonus * 3
    
    elif goal == "balanced":
        # Ausgewogen
        score += config.placed_modules * 7
        score -= config.shading_total * 1
        score += config.optimal_orientation_bonus * 1.5
    
    return min(score, 100.0)
```

### 5. Erweiterte Export-Funktionen

#### CSV-Export

```python
def export_module_details_csv(modules: List[ModuleTransform], filename: str):
    """
    Exportiert Modul-Details als CSV
    
    CSV-Format:
    Index,X,Y,Z,Azimuth,Tilt,Group,Shading%
    """
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'X', 'Y', 'Z', 'Azimuth', 'Tilt', 'Group', 'Shading%'])
        
        for module in modules:
            writer.writerow([
                module.index,
                f"{module.offset_x:.2f}",
                f"{module.offset_y:.2f}",
                f"{module.offset_z:.2f}",
                f"{module.azimuth_deg:.1f}",
                f"{module.tilt_deg:.1f}",
                module.group_id or "",
                f"{module.shading_pct:.1f}"
            ])
```

#### Multi-View Screenshot

```python
def export_multi_view_screenshots(
    project_data, building_dims, roof_type, module_qty, layout_config
) -> Dict[str, bytes]:
    """
    Erstellt Screenshots aus verschiedenen Perspektiven
    
    Returns:
        Dict mit View-Namen und PNG-Bytes
    """
    views = {}
    
    # Isometrisch (Standard)
    views["isometric"] = render_image_bytes(
        project_data, building_dims, roof_type, module_qty, layout_config,
        camera_position="isometric"
    )
    
    # Von oben
    views["top"] = render_image_bytes(
        project_data, building_dims, roof_type, module_qty, layout_config,
        camera_position=(0, 0, 50)
    )
    
    # Von Süden
    views["south"] = render_image_bytes(
        project_data, building_dims, roof_type, module_qty, layout_config,
        camera_position=(0, -30, 10)
    )
    
    # Von Osten
    views["east"] = render_image_bytes(
        project_data, building_dims, roof_type, module_qty, layout_config,
        camera_position=(30, 0, 10)
    )
    
    return views
```

#### 360° Animation

```python
def export_360_animation(
    project_data, building_dims, roof_type, module_qty, layout_config,
    frames: int = 36, output_format: str = "gif"
) -> bytes:
    """
    Erstellt 360° Rotations-Animation
    
    Args:
        frames: Anzahl Frames (36 = 10° pro Frame)
        output_format: "gif" oder "mp4"
    
    Returns:
        Animation als Bytes
    """
    from PIL import Image
    import io
    
    images = []
    
    for i in range(frames):
        angle = (360 / frames) * i
        
        # Render Frame
        img_bytes = render_image_bytes(
            project_data, building_dims, roof_type, module_qty, layout_config,
            camera_rotation_z=angle
        )
        
        images.append(Image.open(io.BytesIO(img_bytes)))
    
    # Erstelle GIF
    output = io.BytesIO()
    images[0].save(
        output,
        format='GIF',
        save_all=True,
        append_images=images[1:],
        duration=100,  # 100ms pro Frame
        loop=0
    )
    
    return output.getvalue()
```

### 6. UI-Erweiterungen

#### Erweiterte Sidebar-Struktur

```
Sidebar
├── Basis-Einstellungen (Collapsible)
│   ├── Gebäudedimensionen
│   ├── Dachform
│   └── Ausrichtung
├── Modul-Belegung (Collapsible)
│   ├── Belegungsmodus
│   ├── Aufständerung
│   └── Platzmangel-Fallbacks
├── Erweiterte Kontrolle (Collapsible) ← NEU
│   ├── Modul-Auswahl
│   ├── Azimuth-Steuerung
│   ├── Neigungs-Steuerung
│   ├── Positions-Offsets
│   └── Gruppen-Verwaltung
├── Analyse (Collapsible) ← NEU
│   ├── Verschattungs-Analyse
│   ├── Sonnenstand-Simulation
│   └── Optimierungs-Assistent
└── Export (Collapsible)
    ├── Screenshot
    ├── 3D-Modelle
    ├── Detailbericht ← NEU
    └── Animation ← NEU
```

#### Implementierung Erweiterte Kontrolle

```python
with st.sidebar.expander("🎛️ Erweiterte Kontrolle", expanded=False):
    st.subheader("Modul-Auswahl")
    
    # Auswahl-Modus
    selection_mode = st.radio(
        "Auswahl-Modus",
        ["Einzeln", "Gruppe", "Bereich"]
    )
    
    if selection_mode == "Einzeln":
        selected_idx = st.number_input("Modul-Index", 0, max_modules-1, 0)
        if st.button("Auswählen"):
            st.session_state.selected_modules = [selected_idx]
    
    elif selection_mode == "Gruppe":
        group_name = st.selectbox("Gruppe", list(module_groups.keys()))
        if st.button("Gruppe auswählen"):
            st.session_state.selected_modules = module_groups[group_name].module_indices
    
    elif selection_mode == "Bereich":
        start_idx = st.number_input("Von Index", 0, max_modules-1, 0)
        end_idx = st.number_input("Bis Index", 0, max_modules-1, 10)
        if st.button("Bereich auswählen"):
            st.session_state.selected_modules = list(range(start_idx, end_idx+1))
    
    # Transformations-Controls
    if st.session_state.selected_modules:
        st.subheader(f"{len(st.session_state.selected_modules)} Module ausgewählt")
        
        col1, col2 = st.columns(2)
        with col1:
            azimuth = st.slider("Azimuth (°)", 0, 360, 0, 5)
        with col2:
            tilt = st.slider("Neigung (°)", 0, 90, 15, 5)
        
        col3, col4, col5 = st.columns(3)
        with col3:
            offset_x = st.number_input("X-Offset (m)", -5.0, 5.0, 0.0, 0.1)
        with col4:
            offset_y = st.number_input("Y-Offset (m)", -5.0, 5.0, 0.0, 0.1)
        with col5:
            offset_z = st.number_input("Z-Offset (m)", -2.0, 2.0, 0.0, 0.1)
        
        if st.button("Transformation anwenden", type="primary"):
            apply_transform_to_selected(azimuth, tilt, offset_x, offset_y, offset_z)
            st.success("Transformation angewendet!")
```

## Future Enhancements (Phase 3)

### Weitere Optimierungen

1. **Performance**
   - GPU-Beschleunigung für Verschattungs-Berechnung
   - Level-of-Detail (LOD) System für große Anlagen
   - Streaming für Echtzeit-Updates

2. **Qualität**
   - Realistische Materialien und Texturen
   - Dynamische Schatten und Beleuchtung
   - Photorealistische Rendering-Option

3. **Integration**
   - API für externe Tools
   - Import von CAD-Modellen
   - Export zu PV-Simulations-Software (PVsyst, PVsol)
   - VR/AR-Export für immersive Präsentationen

## Conclusion

Das 3D-Visualisierungstool bietet eine vollständige, robuste Lösung für die interaktive PV-Planung in der Streamlit-App. Durch die modulare Architektur, klare Schnittstellen und umfassende Fehlerbehandlung ist das System wartbar, erweiterbar und performant. Die nahtlose Integration in die bestehende App-Struktur gewährleistet, dass keine negativen Auswirkungen auf andere Komponenten entstehen.
