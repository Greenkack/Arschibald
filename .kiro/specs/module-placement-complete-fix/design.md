# Design Document - PV-Modul Platzierung Komplett-Fix

## Overview

Dieses Design beschreibt eine vollständige Überarbeitung der PV-Modul-Platzierungslogik. Das System besteht aus mehreren Komponenten die zusammenarbeiten um Module zu berechnen, zu platzieren, zu visualisieren und zu steuern.

## Architecture

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    solar_3d_view_module.py                  │
│                    (Haupt-UI-Komponente)                    │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│ pv3d_module_placement_ui   │  │  pv3d_placement_handler    │
│ (UI-Komponenten & Buttons) │  │  (Business Logic)          │
└────────────┬───────────────┘  └────────────┬───────────────┘
             │                                │
             │                                ▼
             │                   ┌────────────────────────────┐
             │                   │  pv3d_grid_calculator      │
             │                   │  (Grid-Berechnung)         │
             │                   └────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      pv3d_plotly.py                         │
│              (3D-Rendering & Visualisierung)                │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit Session State                   │
│         (placed_module_positions, placed_module_count)      │
└─────────────────────────────────────────────────────────────┘
```

### Datenfluss

1. **Benutzer-Interaktion** → UI-Komponente (Button-Klick)
2. **UI-Komponente** → Placement Handler (Trigger-Event)
3. **Placement Handler** → Grid Calculator (Positions-Anfrage)
4. **Grid Calculator** → Placement Handler (Berechnete Positionen)
5. **Placement Handler** → Session State (Speichern)
6. **Session State** → 3D-Rendering (Lesen & Visualisieren)
7. **3D-Rendering** → Plotly Figure (Mesh-Objekte)
8. **Plotly Figure** → Benutzer (Visuelle Darstellung)

## Components and Interfaces

### 1. UI-Komponente: `pv3d_module_placement_ui.py`

**Zweck**: Rendert das Modul-Belegungs-Panel mit allen Buttons und Statistiken.

**Funktionen**:

```python
def render_module_placement_panel(
    module_quantity: int,
    roof_area: float,
    current_placed: int = 0
) -> Dict[str, Any]:
    """
    Rendert das Modul-Belegungs-Panel.
    
    Args:
        module_quantity: Gewünschte Anzahl Module
        roof_area: Verfügbare Dachfläche in m²
        current_placed: Aktuell platzierte Module
    
    Returns:
        Dictionary mit Button-States:
        - auto_place_clicked: bool
        - manual_add_clicked: bool
        - remove_selected_clicked: bool
        - reset_all_clicked: bool
        - show_grid: bool
        - show_numbers: bool
    """
```

**UI-Elemente**:
- Statistik-Metriken (Gewünscht, Platziert, Abdeckung %)
- Fortschrittsbalken
- Button "Automatisch belegen" (Primary)
- Button "Modul hinzufügen"
- Button "Ausgewählte entfernen"
- Button "Alle zurücksetzen"
- Checkbox "Raster anzeigen"
- Checkbox "Modul-Nummern anzeigen"

### 2. Grid Calculator: `pv3d_grid_calculator.py`

**Zweck**: Berechnet optimale Modul-Positionen auf der Dachfläche.

**Konstanten**:
```python
PV_W = 1.05  # Modul-Breite in Metern
PV_H = 1.76  # Modul-Höhe in Metern
PV_T = 0.04  # Modul-Dicke in Metern
DEFAULT_SPACING = 0.05  # Abstand zwischen Modulen (5cm)
DEFAULT_MARGIN = 0.30   # Randabstand (30cm)
```

**Funktionen**:

```python
def calculate_module_grid(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    spacing: float = DEFAULT_SPACING,
    margin: float = DEFAULT_MARGIN,
    orientation: str = "portrait"
) -> List[Tuple[float, float]]:
    """
    Berechnet Grid-Positionen für Module.
    
    Args:
        roof_length: Länge des Dachs in Metern
        roof_width: Breite des Dachs in Metern
        module_quantity: Gewünschte Anzahl Module
        spacing: Abstand zwischen Modulen
        margin: Randabstand
        orientation: "portrait" oder "landscape"
    
    Returns:
        Liste von (x, y) Positionen relativ zum Dach-Zentrum
    
    Algorithm:
        1. Berechne verfügbare Fläche (Dach - Ränder)
        2. Berechne Module pro Reihe und Spalte
        3. Berechne maximale Anzahl Module
        4. Begrenze auf gewünschte Anzahl
        5. Generiere zentrierte Grid-Positionen
    """
```

**Algorithmus-Details**:

```
Verfügbare Länge = Dach-Länge - 2 * Rand
Verfügbare Breite = Dach-Breite - 2 * Rand

Module pro Reihe = floor(Verfügbare Länge / (Modul-Breite + Abstand))
Module pro Spalte = floor(Verfügbare Breite / (Modul-Höhe + Abstand))

Max Module = Module pro Reihe * Module pro Spalte
Tatsächliche Module = min(Gewünschte Module, Max Module)

Start X = -Dach-Länge/2 + Rand + Modul-Breite/2
Start Y = -Dach-Breite/2 + Rand + Modul-Höhe/2

Für jede Reihe r:
    Für jede Spalte c:
        X = Start X + c * (Modul-Breite + Abstand)
        Y = Start Y + r * (Modul-Höhe + Abstand)
        Position hinzufügen (X, Y)
```

### 3. Placement Handler: `pv3d_placement_handler.py`

**Zweck**: Verarbeitet Platzierungs-Aktionen und verwaltet Session State.

**Funktionen**:

```python
def handle_auto_placement(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    roof_type: str,
    roof_pitch: float = 0.0
) -> Dict[str, Any]:
    """
    Führt automatische Modul-Platzierung durch.
    
    Args:
        roof_length: Länge des Dachs
        roof_width: Breite des Dachs
        module_quantity: Gewünschte Anzahl
        roof_type: "Flachdach", "Satteldach", etc.
        roof_pitch: Dachneigung in Grad
    
    Returns:
        {
            "success": bool,
            "positions": List[Tuple[float, float, float]],
            "count": int,
            "message": str
        }
    
    Process:
        1. Rufe Grid Calculator auf
        2. Konvertiere 2D zu 3D Positionen
        3. Berechne Z-Position basierend auf Dachtyp
        4. Speichere in Session State
        5. Gebe Ergebnis zurück
    """

def handle_reset_placement() -> Dict[str, Any]:
    """
    Setzt alle platzierten Module zurück.
    
    Returns:
        {
            "success": bool,
            "message": str
        }
    """

def handle_manual_add(
    x: float,
    y: float,
    roof_type: str
) -> Dict[str, Any]:
    """
    Fügt ein Modul an spezifischer Position hinzu.
    
    Args:
        x: X-Koordinate
        y: Y-Koordinate
        roof_type: Dachtyp
    
    Returns:
        {
            "success": bool,
            "message": str
        }
    """

def handle_remove_selected(
    selected_indices: List[int]
) -> Dict[str, Any]:
    """
    Entfernt ausgewählte Module.
    
    Args:
        selected_indices: Indizes der zu entfernenden Module
    
    Returns:
        {
            "success": bool,
            "count": int,
            "message": str
        }
    """
```

**Z-Position Berechnung**:

```python
def calculate_z_position(roof_type: str, roof_pitch: float) -> float:
    """
    Berechnet Z-Position basierend auf Dachtyp.
    
    Flachdach: 0.3m (Aufständerung)
    Satteldach: 0.05m (direkt auf Dach)
    Pultdach: 0.05m (direkt auf Dach)
    """
    if roof_type == "Flachdach":
        return 0.3  # Aufständerung
    else:
        return 0.05  # Direkt auf Dach
```

### 4. 3D-Rendering Integration: `pv3d_plotly.py`

**Zweck**: Rendert platzierte Module in der 3D-Szene.

**Modifikationen in `build_plotly_scene()`**:

```python
def build_plotly_scene(...):
    """Erweitert um Modul-Rendering."""
    
    # ... Bestehender Code für Gebäude und Dach ...
    
    # NEU: Module aus Session State laden und rendern
    placed_positions = st.session_state.get("placed_module_positions", [])
    
    if placed_positions:
        print(f"✓ Rendering {len(placed_positions)} PV modules...")
        
        for i, (x, y, z) in enumerate(placed_positions):
            # Berechne Rotation basierend auf Dachtyp
            tilt_deg = 30 if roof_type == "Flachdach" else roof_pitch
            
            # Erstelle Modul-Mesh
            module_mesh, module_vertices = create_pv_module_3d(
                x=x,
                y=y,
                z=z,
                azimuth_deg=0,
                tilt_deg=tilt_deg,
                color="#1a1a2e",  # Dunkelblau/Schwarz
                selected=False,
                show_mounting=True,
                roof_type=roof_type
            )
            
            # Füge zur Szene hinzu
            fig.add_trace(module_mesh)
    
    return fig
```

**Modul-Mesh Erstellung**:

```python
def create_pv_module_3d(
    x: float,
    y: float,
    z: float,
    azimuth_deg: float,
    tilt_deg: float,
    color: str = "#1a1a2e",
    selected: bool = False,
    show_mounting: bool = True,
    roof_type: str = "Flachdach"
) -> Tuple[go.Mesh3d, np.ndarray]:
    """
    Erstellt 3D-Mesh für ein PV-Modul.
    
    Returns:
        (mesh, vertices) - Plotly Mesh3d Objekt und Vertex-Array
    """
    # Modul-Dimensionen
    w, h, t = PV_W, PV_H, PV_T
    
    # Basis-Vertices (Quader)
    vertices = np.array([
        [-w/2, -h/2, 0],    # 0: unten-links-vorne
        [w/2, -h/2, 0],     # 1: unten-rechts-vorne
        [w/2, h/2, 0],      # 2: oben-rechts-vorne
        [-w/2, h/2, 0],     # 3: oben-links-vorne
        [-w/2, -h/2, t],    # 4: unten-links-hinten
        [w/2, -h/2, t],     # 5: unten-rechts-hinten
        [w/2, h/2, t],      # 6: oben-rechts-hinten
        [-w/2, h/2, t]      # 7: oben-links-hinten
    ])
    
    # Rotation um Y-Achse (Neigung)
    if tilt_deg != 0:
        angle_rad = np.radians(tilt_deg)
        rotation_matrix = np.array([
            [np.cos(angle_rad), 0, np.sin(angle_rad)],
            [0, 1, 0],
            [-np.sin(angle_rad), 0, np.cos(angle_rad)]
        ])
        vertices = vertices @ rotation_matrix.T
    
    # Rotation um Z-Achse (Azimut)
    if azimuth_deg != 0:
        angle_rad = np.radians(azimuth_deg)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad), 0],
            [np.sin(angle_rad), np.cos(angle_rad), 0],
            [0, 0, 1]
        ])
        vertices = vertices @ rotation_matrix.T
    
    # Translation zur finalen Position
    vertices += np.array([x, y, z])
    
    # Faces (Dreiecke)
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 6, 4]
    k = [4, 4, 5, 6, 6, 7, 7, 4, 6, 6, 7, 7]
    
    # Farbe (heller wenn ausgewählt)
    final_color = "#4a90e2" if selected else color
    
    mesh = go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=final_color,
        opacity=0.9,
        name=f"PV Module",
        hoverinfo="name"
    )
    
    return mesh, vertices
```

### 5. Integration in `solar_3d_view_module.py`

**Platzierung im Code**:

Nach `render_export_options()` und vor der 3D-Szenen-Erstellung:

```python
# ... Bestehender Code ...

# Export-Optionen
render_export_options(...)

# NEU: Modul-Belegungs-Panel
try:
    from utils.pv3d_module_placement_ui import render_module_placement_panel
    from utils.pv3d_placement_handler import (
        handle_auto_placement,
        handle_reset_placement,
        handle_manual_add,
        handle_remove_selected
    )
    
    # Berechne Dachfläche
    roof_area = dims.length_m * dims.width_m
    current_placed = st.session_state.get("placed_module_count", 0)
    
    # Rendere Panel
    placement_actions = render_module_placement_panel(
        module_quantity=module_quantity,
        roof_area=roof_area,
        current_placed=current_placed
    )
    
    # Handle Auto-Placement Trigger
    if st.session_state.get("trigger_auto_placement", False):
        st.session_state["trigger_auto_placement"] = False
        
        result = handle_auto_placement(
            roof_length=dims.length_m,
            roof_width=dims.width_m,
            module_quantity=module_quantity,
            roof_type=roof_type,
            roof_pitch=roof_pitch
        )
        
        if result["success"]:
            st.success(result["message"])
            st.rerun()
        else:
            st.error(result["message"])
    
    # Handle Reset
    if placement_actions.get("reset_all_clicked"):
        result = handle_reset_placement()
        st.info(result["message"])
        st.rerun()
    
    # Handle Manual Add (wenn implementiert)
    if placement_actions.get("manual_add_clicked"):
        st.info("ℹ️ Klicken Sie auf die Dachfläche um ein Modul hinzuzufügen")
    
    # Handle Remove Selected (wenn implementiert)
    if placement_actions.get("remove_selected_clicked"):
        result = handle_remove_selected([])
        st.info(result["message"])

except ImportError as e:
    st.sidebar.warning(f"⚠️ Modul-Belegungs-Panel nicht verfügbar: {e}")

# ... 3D-Szenen-Erstellung ...
fig = build_plotly_scene(...)
```

## Data Models

### Session State Schema

```python
# Modul-Positionen
st.session_state["placed_module_positions"]: List[Tuple[float, float, float]]
# Beispiel: [(0.0, 0.0, 0.3), (1.1, 0.0, 0.3), ...]

# Anzahl platzierter Module
st.session_state["placed_module_count"]: int
# Beispiel: 24

# Trigger für automatische Platzierung
st.session_state["trigger_auto_placement"]: bool
# Beispiel: True

# Ausgewählte Module (für manuelle Bearbeitung)
st.session_state["selected_module_indices"]: List[int]
# Beispiel: [0, 5, 12]

# Optionen
st.session_state["show_placement_grid"]: bool
st.session_state["show_module_numbers"]: bool
```

### Modul-Position Datenstruktur

```python
ModulePosition = Tuple[float, float, float]
# (x, y, z) in Metern relativ zum Dach-Zentrum
# x: -length/2 bis +length/2
# y: -width/2 bis +width/2
# z: Höhe über Dach (0.05 für Schrägdach, 0.3 für Flachdach)
```

## Error Handling

### Fehlertypen und Behandlung

1. **Grid-Berechnung Fehler**:
   - Ursache: Ungültige Dach-Dimensionen (0 oder negativ)
   - Behandlung: Fehlermeldung anzeigen, leere Liste zurückgeben
   - User-Feedback: "❌ Fehler: Ungültige Dach-Dimensionen"

2. **Rendering Fehler**:
   - Ursache: Ungültige Modul-Positionen, Plotly-Fehler
   - Behandlung: Try-Catch um Mesh-Erstellung, Fehler loggen
   - User-Feedback: "⚠️ Einige Module konnten nicht dargestellt werden"

3. **Session State Fehler**:
   - Ursache: Fehlende oder korrupte Daten
   - Behandlung: Initialisiere mit Standardwerten
   - User-Feedback: Keine (Silent Recovery)

4. **Import Fehler**:
   - Ursache: Fehlende Module
   - Behandlung: Try-Catch um Imports, Fallback auf Basis-Funktionalität
   - User-Feedback: "⚠️ Modul-Belegungs-Panel nicht verfügbar"

### Error Recovery

```python
def safe_grid_calculation(roof_length, roof_width, module_quantity):
    """Sichere Grid-Berechnung mit Fehlerbehandlung."""
    try:
        # Validierung
        if roof_length <= 0 or roof_width <= 0:
            raise ValueError("Dach-Dimensionen müssen positiv sein")
        
        if module_quantity <= 0:
            return []
        
        # Berechnung
        positions = calculate_module_grid(
            roof_length, roof_width, module_quantity
        )
        
        return positions
    
    except Exception as e:
        print(f"❌ Grid-Berechnung Fehler: {e}")
        return []
```

## Testing Strategy

### Unit Tests

1. **Grid Calculator Tests**:
   - Test: Korrekte Anzahl Positionen
   - Test: Positionen innerhalb Dach-Grenzen
   - Test: Mindestabstände eingehalten
   - Test: Randabstände eingehalten
   - Test: Handling von zu großer Modulanzahl

2. **Placement Handler Tests**:
   - Test: Auto-Placement speichert in Session State
   - Test: Reset löscht Session State
   - Test: Z-Position korrekt für verschiedene Dachtypen
   - Test: Fehlerbehandlung bei ungültigen Eingaben

3. **Rendering Tests**:
   - Test: Mesh-Erstellung für einzelnes Modul
   - Test: Korrekte Rotation und Translation
   - Test: Mesh hat korrekte Anzahl Vertices
   - Test: Mesh hat korrekte Farbe

### Integration Tests

1. **End-to-End Platzierung**:
   - Test: Button-Klick → Grid-Berechnung → Session State → Rendering
   - Test: Verschiedene Dachtypen (Flach, Satteldach, Pultdach)
   - Test: Verschiedene Modulanzahlen (1, 10, 50, 100)

2. **UI-Integration**:
   - Test: Panel wird korrekt gerendert
   - Test: Statistiken aktualisieren sich
   - Test: Buttons sind klickbar
   - Test: Fortschrittsbalken zeigt korrekten Wert

### Performance Tests

1. **Rendering Performance**:
   - Test: 50 Module in < 2 Sekunden
   - Test: 100 Module in < 5 Sekunden
   - Test: Keine Memory Leaks bei wiederholter Platzierung

2. **Grid-Berechnung Performance**:
   - Test: Berechnung für 100 Module in < 100ms
   - Test: Berechnung für 1000 Module in < 500ms

## Performance Considerations

### Optimierungen

1. **Lazy Rendering**:
   - Rendere nur Module im sichtbaren Bereich
   - Verwende Level-of-Detail für weit entfernte Module

2. **Caching**:
   - Cache berechnete Grid-Positionen
   - Cache Mesh-Geometrie für identische Module

3. **Batch Operations**:
   - Füge alle Module in einem Batch zur Szene hinzu
   - Verwende Plotly's Batch-Update Funktionen

### Memory Management

- Begrenze maximale Modulanzahl auf 200
- Verwende numpy Arrays statt Python Listen
- Lösche alte Positionen aus Session State bei Reset

## Backward Compatibility

### Keine Breaking Changes

- Alle neuen Funktionen sind optional
- Bestehende Funktionen bleiben unverändert
- Neue Module haben keine Abhängigkeiten zu bestehendem Code
- Import-Fehler werden abgefangen (Try-Catch)

### Migration Path

Keine Migration notwendig, da:
- Neue Funktionalität ist additiv
- Session State Keys sind neu (keine Konflikte)
- Bestehende 3D-Rendering-Logik wird erweitert, nicht ersetzt
