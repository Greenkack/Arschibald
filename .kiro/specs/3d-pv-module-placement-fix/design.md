# Design Document - 3D PV-Visualisierung: Fixes, Optimierungen & Neue Features

## 1. Introduction

### 1.1 Purpose
Dieses Design-Dokument beschreibt die technische Lösung für kritische Bugfixes, Performance-Optimierungen und neue Features der 3D-PV-Visualisierung. Der Fokus liegt auf der korrekten Modulplatzierung auf geneigten Dächern und der Implementierung innovativer Features.

### 1.2 Scope
- **TEIL A**: Kritische Bugfixes (Modulplatzierung auf geneigten Dächern)
- **TEIL B**: Optimierungen bestehender Features (Sonnenverlauf, Verschattung, Heatmap, manuelle Platzierung)
- **TEIL C**: 7 neue Features (Modulfarben, KI-Optimierung, Wetter, Video-Export, Vergleich, Umgebung, Kollaboration)

### 1.3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    solar_3d_view_module.py                  │
│                   (Main Orchestration)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌──────────────┐
│ pv3d_plotly.py │ │ pv3d_      │ │ pv3d_        │
│ (Rendering)    │ │ placement_ │ │ analysis.py  │
│                │ │ handler.py │ │ (Analysis)   │
└────────────────┘ └────────────┘ └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌──────────────┐
│ solar_         │ │ pv3d_      │ │ pv3d_        │
│ animation.py   │ │ export.py  │ │ optimization │
│ (Animations)   │ │ (Export)   │ │ .py (AI)     │
└────────────────┘ └────────────┘ └──────────────┘
```

## 2. TEIL A: KRITISCHE BUGFIXES

### 2.1 Problem Analysis

**Aktuelles Problem:**
- Module werden auf geneigten Dächern (Satteldach, Walmdach, Pultdach) wie auf Flachdächern behandelt
- Z-Position wird konstant berechnet (0.30m Aufständerung)
- Module erscheinen auf dem flachen Basis-Bereich statt auf den geneigten Dachflächen

**Root Cause:**
In `utils/pv3d_placement_handler.py` Zeile 690-800:
- `calculate_z_position()` gibt nur eine konstante Basis-Z-Position zurück
- Die Y-Position des Moduls wird nicht berücksichtigt
- Für geneigte Dächer muss Z basierend auf Y berechnet werden

### 2.2 Solution: Korrekte Z-Position Berechnung

#### 2.2.1 Mathematische Grundlage

Für geneigte Dächer gilt:
```
z = base_z + (y_offset * tan(roof_pitch))
```

Wobei:
- `base_z` = Traufhöhe (0.15m über Dachbasis)
- `y_offset` = Abstand von der Traufe (untere Dachkante)
- `roof_pitch` = Dachneigung in Grad

#### 2.2.2 Implementation Strategy

**Datei:** `utils/pv3d_placement_handler.py`

**Änderung 1:** Erweitere `calculate_z_position()` Signatur
```python
def calculate_z_position(
    roof_type: str, 
    roof_pitch: float = 0.0, 
    roof_width: float = 10.0,
    y_position: float = 0.0  # NEU: Y-Position des Moduls
) -> float:
```

**Änderung 2:** Implementiere dachtyp-spezifische Logik

```python
# Flachdach: Konstante Höhe mit Aufständerung
if "flach" in roof_type_normalized:
    return 0.30  # 30cm Aufständerung

# Satteldach: Z steigt vom Rand zur Mitte
elif roof_type_normalized in ["satteldach", "satteldach mit gaube"]:
    base_z = 0.15  # 15cm über Dachbasis
    if roof_pitch > 0:
        # Abstand von Traufe (y = -roof_width/2)
        dist_from_eave = y_position + roof_width / 2
        z_offset = dist_from_eave * math.tan(math.radians(roof_pitch))
        return base_z + z_offset
    return base_z

# Pultdach: Z steigt linear von vorne nach hinten
elif roof_type_normalized == "pultdach":
    base_z = 0.15
    if roof_pitch > 0:
        dist_from_front = y_position + roof_width / 2
        z_offset = dist_from_front * math.tan(math.radians(roof_pitch))
        return base_z + z_offset
    return base_z

# Walmdach/Krüppelwalmdach: Ähnlich wie Satteldach
elif roof_type_normalized in ["walmdach", "krüppelwalmdach"]:
    base_z = 0.15
    if roof_pitch > 0:
        dist_from_eave = y_position + roof_width / 2
        z_offset = dist_from_eave * math.tan(math.radians(roof_pitch))
        return base_z + z_offset
    return base_z

# Zeltdach: Z steigt vom Rand zur Mitte (pyramidenförmig)
elif roof_type_normalized == "zeltdach":
    base_z = 0.15
    if roof_pitch > 0:
        # Minimaler Abstand von allen 4 Kanten
        dist_from_edge = min(
            y_position + roof_width / 2,
            roof_width / 2 - y_position
        )
        z_offset = dist_from_edge * math.tan(math.radians(roof_pitch))
        return base_z + z_offset
    return base_z

# Fallback: Konstante Höhe
else:
    return 0.15
```

**Änderung 3:** Update `handle_auto_placement()` Aufruf
```python
# In handle_auto_placement() - Zeile ~450
for x, y in grid_positions_2d:
    # Berechne Z für jedes Modul individuell
    z = calculate_z_position(roof_type, roof_pitch, roof_width, y)
    positions_3d.append((float(x), float(y), float(z)))
```

### 2.3 Testing Strategy

**Test Cases:**
1. **Flachdach**: Alle Module auf gleicher Höhe (0.30m)
2. **Satteldach 30°**: Module steigen von Traufe zum First
3. **Pultdach 15°**: Module steigen linear von vorne nach hinten
4. **Walmdach 25°**: Module folgen Dachneigung
5. **Zeltdach 20°**: Module steigen pyramidenförmig zur Mitte

**Validation:**
- Visuelle Inspektion in 3D-Ansicht
- Module liegen auf Dachflächen (nicht darunter/darüber)
- Keine Kollisionen mit Dachgeometrie

## 3. TEIL B: OPTIMIERUNGEN BESTEHENDER FEATURES

### 3.1 Sonnenverlauf-Animation (Requirement 2)

**Bestehende Implementierung:**
- `utils/solar_animation.py` - `create_sun_path_animation()`
- `utils/pv3d_wow_features.py` - `render_sun_path_animation()`

**Optimierungen:**

#### 3.1.1 Performance-Verbesserung
**Datei:** `utils/solar_animation.py`

```python
def create_sun_path_animation(
    fig: go.Figure,
    building_center: Tuple[float, float, float],
    latitude: float = 48.0,
    longitude: float = 11.0,
    date: str = "2024-06-21",
    fps: int = 24,  # NEU: Konfigurierbare FPS
    time_compression: float = 1.0  # NEU: Zeitraffer-Faktor
) -> go.Figure:
    """
    Erstellt Sonnenverlauf-Animation mit verbesserter Performance.
    
    Optimierungen:
    - Reduzierte Frame-Anzahl bei gleichbleibender Qualität
    - Adaptive Frame-Rate basierend auf Geräteleistung
    - Caching von Sonnenpositions-Berechnungen
    """
    # Frame-Anzahl basierend auf FPS und Zeitraffer
    hours = 24
    frames_per_hour = fps / time_compression
    total_frames = int(hours * frames_per_hour)
    
    # Cache für Sonnenpositions-Berechnungen
    sun_positions = _calculate_sun_positions_cached(
        latitude, longitude, date, total_frames
    )
    
    # Erstelle Frames mit optimierter Rendering-Pipeline
    frames = []
    for i, (azimuth, elevation) in enumerate(sun_positions):
        frame = _create_sun_frame_optimized(
            fig, building_center, azimuth, elevation, i
        )
        frames.append(frame)
    
    # Füge Animation mit konfigurierbarer Geschwindigkeit hinzu
    fig.frames = frames
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate', 
                 'args': [None, {'frame': {'duration': 1000/fps}}]},
                {'label': 'Pause', 'method': 'animate',
                 'args': [[None], {'mode': 'immediate'}]}
            ]
        }]
    )
    
    return fig
```


#### 3.1.2 Echtzeit-Schatten-Update
**Datei:** `utils/solar_animation.py`

```python
def update_shadows_realtime(
    fig: go.Figure,
    sun_azimuth: float,
    sun_elevation: float,
    module_positions: List[Tuple[float, float, float]],
    building_dims: Any
) -> go.Figure:
    """
    Aktualisiert Schatten in Echtzeit basierend auf Sonnenposition.
    
    Verwendet Ray-Tracing für realistische Schatten-Projektion.
    """
    # Berechne Schatten-Vektoren
    shadow_direction = _calculate_shadow_vector(sun_azimuth, sun_elevation)
    
    # Projiziere Schatten auf Dachfläche
    shadow_polygons = []
    for x, y, z in module_positions:
        shadow_poly = _project_module_shadow(
            x, y, z, shadow_direction, building_dims
        )
        shadow_polygons.append(shadow_poly)
    
    # Füge Schatten als semi-transparente Meshes hinzu
    for poly in shadow_polygons:
        fig.add_trace(go.Mesh3d(
            x=poly[:, 0], y=poly[:, 1], z=poly[:, 2],
            color='rgba(0, 0, 0, 0.3)',
            name='Schatten',
            showlegend=False
        ))
    
    return fig
```

#### 3.1.3 Zeitraffer-Funktion
**UI-Komponente:** `utils/pv3d_ui_components.py`

```python
def render_animation_controls() -> Dict[str, Any]:
    """Rendert erweiterte Animation-Controls."""
    st.sidebar.subheader("⏱️ Zeitraffer-Einstellungen")
    
    time_compression = st.sidebar.slider(
        "Zeitraffer-Faktor",
        min_value=1.0,
        max_value=100.0,
        value=10.0,
        step=1.0,
        help="1 Stunde = X Sekunden"
    )
    
    fps = st.sidebar.slider(
        "Frames pro Sekunde",
        min_value=12,
        max_value=60,
        value=24,
        step=6,
        help="Höhere FPS = flüssigere Animation"
    )
    
    return {
        "time_compression": time_compression,
        "fps": fps
    }
```

### 3.2 Verschattungs-Analyse (Requirement 3)

**Bestehende Implementierung:**
- `utils/pv3d_analysis.py` - `calculate_shading_analysis()`

**Optimierungen:**

#### 3.2.1 Direkte vs. Indirekte Verschattung
**Datei:** `utils/pv3d_analysis.py`

```python
def calculate_shading_analysis_enhanced(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    sun_azimuth: float,
    sun_elevation: float,
    include_indirect: bool = True  # NEU
) -> Dict[str, Any]:
    """
    Erweiterte Verschattungs-Analyse mit direkter/indirekter Unterscheidung.
    
    Returns:
        {
            "direct_shading": List[float],  # 0-1 für jedes Modul
            "indirect_shading": List[float],  # 0-1 für jedes Modul
            "total_shading": List[float],  # Kombiniert
            "shading_sources": List[str]  # "module", "building", "environment"
        }
    """
    results = {
        "direct_shading": [],
        "indirect_shading": [],
        "total_shading": [],
        "shading_sources": []
    }
    
    for i, (x, y, z) in enumerate(module_positions):
        # Direkte Verschattung: Objekte blockieren Sonnenlicht
        direct = _calculate_direct_shading(
            x, y, z, sun_azimuth, sun_elevation,
            module_positions, module_transforms
        )
        
        # Indirekte Verschattung: Reduzierte diffuse Strahlung
        indirect = 0.0
        if include_indirect:
            indirect = _calculate_indirect_shading(
                x, y, z, module_positions, module_transforms
            )
        
        total = min(1.0, direct + indirect * 0.3)  # Indirekt hat weniger Einfluss
        
        results["direct_shading"].append(direct)
        results["indirect_shading"].append(indirect)
        results["total_shading"].append(total)
        results["shading_sources"].append(_identify_shading_source(i, direct))
    
    return results
```

#### 3.2.2 Verschattung durch Nachbargebäude
**Neue Funktion:** `utils/pv3d_analysis.py`

```python
def add_neighboring_buildings(
    building_positions: List[Dict[str, Any]]
) -> None:
    """
    Fügt Nachbargebäude zur Verschattungs-Analyse hinzu.
    
    Args:
        building_positions: Liste von Gebäuden mit:
            - x, y: Position relativ zum Hauptgebäude
            - width, length, height: Dimensionen
            - roof_type: Dachform
    """
    if "neighboring_buildings" not in st.session_state:
        st.session_state["neighboring_buildings"] = []
    
    st.session_state["neighboring_buildings"].extend(building_positions)
```

#### 3.2.3 Verschattungs-Verlauf Diagramm
**Datei:** `utils/pv3d_analysis.py`

```python
def create_shading_timeline_chart(
    module_index: int,
    date: str = "2024-06-21",
    latitude: float = 48.0
) -> go.Figure:
    """
    Erstellt Verschattungs-Verlauf über den Tag als Diagramm.
    
    Returns:
        Plotly Figure mit Verschattung (%) über Zeit (Stunden)
    """
    hours = list(range(6, 21))  # 6:00 - 20:00
    shading_values = []
    
    for hour in hours:
        # Berechne Sonnenposition für diese Stunde
        sun_pos = _calculate_sun_position(latitude, date, hour)
        
        # Berechne Verschattung für dieses Modul
        shading = _calculate_module_shading(
            module_index, sun_pos["azimuth"], sun_pos["elevation"]
        )
        shading_values.append(shading * 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=shading_values,
        mode='lines+markers',
        name='Verschattung',
        line=dict(color='#e74c3c', width=3),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.2)'
    ))
    
    fig.update_layout(
        title=f"Verschattungs-Verlauf Modul #{module_index}",
        xaxis_title="Uhrzeit",
        yaxis_title="Verschattung (%)",
        yaxis_range=[0, 100]
    )
    
    return fig
```

### 3.3 Ertrags-Heatmap (Requirement 4)

**Bestehende Implementierung:**
- `utils/pv3d_analysis.py` - `calculate_yield_heatmap()`
- `utils/pv3d_wow_features.py` - `render_yield_heatmap_overlay()`

**Optimierungen:**

#### 3.3.1 Erweiterte Metriken
**Datei:** `utils/pv3d_analysis.py`

```python
def calculate_yield_heatmap_enhanced(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    module_power_w: float = 400.0,
    electricity_price_eur_kwh: float = 0.30,
    co2_factor_kg_kwh: float = 0.485
) -> Dict[str, Any]:
    """
    Erweiterte Ertrags-Heatmap mit mehreren Metriken.
    
    Returns:
        {
            "annual_yield_kwh": List[float],  # Jahresertrag pro Modul
            "monthly_avg_kwh": List[float],  # Monatlicher Durchschnitt
            "shading_loss_percent": List[float],  # Verschattungsverlust
            "roi_years": List[float],  # Return on Investment
            "co2_savings_kg": List[float],  # CO₂-Einsparung
            "revenue_eur": List[float]  # Jährliche Einnahmen
        }
    """
    results = {
        "annual_yield_kwh": [],
        "monthly_avg_kwh": [],
        "shading_loss_percent": [],
        "roi_years": [],
        "co2_savings_kg": [],
        "revenue_eur": []
    }
    
    for i, (x, y, z) in enumerate(module_positions):
        # Berechne Basis-Ertrag (ohne Verschattung)
        base_yield = _calculate_base_yield(
            x, y, z, module_transforms.get(i), module_power_w
        )
        
        # Berechne Verschattungsverlust
        shading_loss = _calculate_annual_shading_loss(i)
        
        # Tatsächlicher Ertrag
        actual_yield = base_yield * (1 - shading_loss)
        
        # Berechne Metriken
        monthly_avg = actual_yield / 12
        revenue = actual_yield * electricity_price_eur_kwh
        co2_savings = actual_yield * co2_factor_kg_kwh
        
        # ROI (vereinfacht: Modulkosten / Jahresertrag)
        module_cost = 200.0  # EUR (Durchschnitt)
        roi = module_cost / revenue if revenue > 0 else 999
        
        results["annual_yield_kwh"].append(actual_yield)
        results["monthly_avg_kwh"].append(monthly_avg)
        results["shading_loss_percent"].append(shading_loss * 100)
        results["roi_years"].append(roi)
        results["co2_savings_kg"].append(co2_savings)
        results["revenue_eur"].append(revenue)
    
    return results
```


#### 3.3.2 Hover-Details mit allen Metriken
**Datei:** `utils/pv3d_plotly.py`

```python
def create_pv_module_3d_with_heatmap(
    x, y, z,
    heatmap_data: Dict[str, Any],
    module_index: int,
    **kwargs
) -> Tuple[go.Mesh3d, np.ndarray]:
    """
    Erstellt PV-Modul mit Heatmap-Daten im Hover-Text.
    """
    # Hole Metriken für dieses Modul
    annual_yield = heatmap_data["annual_yield_kwh"][module_index]
    monthly_avg = heatmap_data["monthly_avg_kwh"][module_index]
    shading_loss = heatmap_data["shading_loss_percent"][module_index]
    roi = heatmap_data["roi_years"][module_index]
    co2_savings = heatmap_data["co2_savings_kg"][module_index]
    revenue = heatmap_data["revenue_eur"][module_index]
    
    # Erstelle erweiterten Hover-Text
    hover_template = (
        f"<b>Modul #{module_index}</b><br>"
        f"<br><b>Ertrag:</b><br>"
        f"Jahresertrag: {annual_yield:.0f} kWh<br>"
        f"Monatlich: {monthly_avg:.0f} kWh<br>"
        f"<br><b>Verluste:</b><br>"
        f"Verschattung: {shading_loss:.1f}%<br>"
        f"<br><b>Wirtschaftlichkeit:</b><br>"
        f"ROI: {roi:.1f} Jahre<br>"
        f"Einnahmen: {revenue:.2f} €/Jahr<br>"
        f"<br><b>Umwelt:</b><br>"
        f"CO₂-Einsparung: {co2_savings:.0f} kg/Jahr<br>"
        f"<br><b>Position:</b><br>"
        f"({x:.2f}, {y:.2f}, {z:.2f}) m"
        "<extra></extra>"
    )
    
    # Farbe basierend auf Ertrag (Heatmap)
    # Grün = hoher Ertrag, Gelb = mittel, Rot = niedrig
    color = _yield_to_color(annual_yield, heatmap_data["annual_yield_kwh"])
    
    # Erstelle Modul mit Heatmap-Farbe
    mesh, vertices = create_pv_module_3d(
        x, y, z,
        color=color,
        hovertemplate=hover_template,
        **kwargs
    )
    
    return mesh, vertices
```

#### 3.3.3 Schwache Module automatisch markieren
**Datei:** `utils/pv3d_analysis.py`

```python
def identify_weak_modules(
    heatmap_data: Dict[str, Any],
    threshold_percent: float = 50.0
) -> List[int]:
    """
    Identifiziert Module mit <50% Ertrag.
    
    Returns:
        Liste von Modul-Indizes mit schwachem Ertrag
    """
    annual_yields = heatmap_data["annual_yield_kwh"]
    max_yield = max(annual_yields) if annual_yields else 1.0
    
    weak_modules = []
    for i, yield_val in enumerate(annual_yields):
        relative_yield = (yield_val / max_yield) * 100
        if relative_yield < threshold_percent:
            weak_modules.append(i)
    
    return weak_modules


def suggest_module_optimization(
    weak_modules: List[int],
    module_positions: List[Tuple[float, float, float]]
) -> List[Dict[str, Any]]:
    """
    Schlägt Optimierungen für schwache Module vor.
    
    Returns:
        Liste von Vorschlägen mit:
            - module_index: Index des Moduls
            - issue: Beschreibung des Problems
            - suggestion: Optimierungsvorschlag
    """
    suggestions = []
    
    for idx in weak_modules:
        x, y, z = module_positions[idx]
        
        # Analysiere Ursache
        shading = _calculate_module_shading(idx)
        orientation = _get_module_orientation(idx)
        
        issue = ""
        suggestion = ""
        
        if shading > 0.6:
            issue = "Starke Verschattung (>60%)"
            suggestion = "Modul an weniger verschattete Position verschieben"
        elif orientation["azimuth"] > 45:
            issue = "Suboptimale Ausrichtung"
            suggestion = "Modul Richtung Süden ausrichten"
        else:
            issue = "Niedriger Ertrag"
            suggestion = "Position und Ausrichtung überprüfen"
        
        suggestions.append({
            "module_index": idx,
            "issue": issue,
            "suggestion": suggestion,
            "current_position": (x, y, z)
        })
    
    return suggestions
```

### 3.4 Manuelle Modulplatzierung (Requirement 5)

**Bestehende Implementierung:**
- `utils/pv3d_placement_handler.py` - Basis-Funktionen

**Verbesserungen:**

#### 3.4.1 Modul-Hervorhebung
**Datei:** `utils/pv3d_plotly.py`

```python
def create_pv_module_3d_with_highlight(
    x, y, z,
    selected: bool = False,
    hover: bool = False,
    **kwargs
) -> Tuple[go.Mesh3d, np.ndarray]:
    """
    Erstellt PV-Modul mit optionaler Hervorhebung.
    
    Args:
        selected: Modul ist ausgewählt (leuchtender Rahmen)
        hover: Maus schwebt über Modul (leichtes Glühen)
    """
    # Basis-Modul erstellen
    mesh, vertices = create_pv_module_3d(x, y, z, **kwargs)
    
    # Leuchtender Rahmen für ausgewählte Module
    if selected:
        # Erstelle Kanten-Linien mit Glow-Effekt
        edges = create_module_edges_with_glow(
            vertices,
            color='#4a90e2',  # Hellblau
            width=4,
            glow_intensity=0.8
        )
        return [mesh, edges], vertices
    
    # Leichtes Glühen bei Hover
    elif hover:
        mesh.opacity = 0.95
        mesh.lighting = dict(
            ambient=0.8,  # Erhöhtes Umgebungslicht
            diffuse=0.9,
            specular=0.7,
            roughness=0.1
        )
    
    return mesh, vertices


def create_module_edges_with_glow(
    vertices: np.ndarray,
    color: str = '#4a90e2',
    width: int = 4,
    glow_intensity: float = 0.8
) -> go.Scatter3d:
    """
    Erstellt leuchtende Kanten für Modul-Hervorhebung.
    """
    # Extrahiere Kanten-Punkte
    edges_x, edges_y, edges_z = _extract_box_edges(vertices)
    
    return go.Scatter3d(
        x=edges_x,
        y=edges_y,
        z=edges_z,
        mode='lines',
        line=dict(
            color=color,
            width=width
        ),
        opacity=glow_intensity,
        name='Auswahl',
        showlegend=False,
        hoverinfo='skip'
    )
```

#### 3.4.2 Magnet-Funktion (Snap-to-Grid)
**Datei:** `utils/pv3d_placement_handler.py`

```python
def snap_to_grid(
    x: float,
    y: float,
    grid_spacing: float = 0.5
) -> Tuple[float, float]:
    """
    Richtet Position am Raster aus (Magnet-Funktion).
    
    Args:
        x, y: Ursprüngliche Position
        grid_spacing: Raster-Abstand in Metern
    
    Returns:
        (x_snapped, y_snapped): An Raster ausgerichtete Position
    """
    x_snapped = round(x / grid_spacing) * grid_spacing
    y_snapped = round(y / grid_spacing) * grid_spacing
    
    return x_snapped, y_snapped


def handle_manual_move_with_snap(
    module_index: int,
    new_x: float,
    new_y: float,
    enable_snap: bool = True,
    grid_spacing: float = 0.5,
    **kwargs
) -> Dict[str, Any]:
    """
    Verschiebt Modul mit optionaler Raster-Ausrichtung.
    """
    # Snap-to-Grid wenn aktiviert
    if enable_snap:
        new_x, new_y = snap_to_grid(new_x, new_y, grid_spacing)
    
    # Verwende bestehende Move-Funktion
    return handle_move_selected(
        selected_indices=[module_index],
        offset_x=new_x,
        offset_y=new_y,
        **kwargs
    )
```

#### 3.4.3 Kopieren & Einfügen
**Datei:** `utils/pv3d_placement_handler.py`

```python
def copy_module_group(
    module_indices: List[int]
) -> Dict[str, Any]:
    """
    Kopiert ausgewählte Module in Zwischenablage.
    
    Returns:
        {
            "success": bool,
            "clipboard_data": Dict mit Modul-Daten
        }
    """
    if not module_indices:
        return {"success": False, "message": "Keine Module ausgewählt"}
    
    positions = st.session_state.get("placed_module_positions", [])
    
    # Kopiere Modul-Daten
    clipboard = []
    for idx in module_indices:
        if idx < len(positions):
            x, y, z = positions[idx]
            clipboard.append({
                "x": x, "y": y, "z": z,
                "index": idx
            })
    
    # Speichere in Session State
    st.session_state["module_clipboard"] = clipboard
    
    return {
        "success": True,
        "message": f"{len(clipboard)} Module kopiert",
        "clipboard_data": clipboard
    }


def paste_module_group(
    offset_x: float = 1.0,
    offset_y: float = 1.0,
    **kwargs
) -> Dict[str, Any]:
    """
    Fügt kopierte Module mit Offset ein.
    """
    clipboard = st.session_state.get("module_clipboard", [])
    
    if not clipboard:
        return {"success": False, "message": "Zwischenablage leer"}
    
    positions = st.session_state.get("placed_module_positions", [])
    new_positions = []
    
    for module_data in clipboard:
        new_x = module_data["x"] + offset_x
        new_y = module_data["y"] + offset_y
        
        # Berechne neue Z-Position
        new_z = calculate_z_position(
            kwargs.get("roof_type", "Flachdach"),
            kwargs.get("roof_pitch", 0.0),
            kwargs.get("roof_width", 10.0),
            new_y
        )
        
        # Prüfe Kollision
        collision = check_module_collision(
            (new_x, new_y, new_z),
            positions + new_positions,
            kwargs.get("roof_length", 10.0),
            kwargs.get("roof_width", 8.0)
        )
        
        if not collision["collision"]:
            new_positions.append((new_x, new_y, new_z))
    
    # Füge neue Module hinzu
    positions.extend(new_positions)
    st.session_state["placed_module_positions"] = positions
    st.session_state["placed_module_count"] = len(positions)
    
    return {
        "success": True,
        "message": f"{len(new_positions)} Module eingefügt"
    }
```


#### 3.4.4 Tastatur-Shortcuts
**Datei:** `utils/pv3d_ui_components.py`

```python
def inject_keyboard_shortcuts() -> None:
    """
    Injiziert JavaScript für Tastatur-Shortcuts.
    
    Shortcuts:
    - Pfeiltasten: Verschieben (0.5m)
    - Shift + Pfeiltasten: Verschieben (0.1m)
    - R: Rotieren um 90°
    - Delete: Löschen
    - Ctrl+C: Kopieren
    - Ctrl+V: Einfügen
    """
    keyboard_js = """
    <script>
    document.addEventListener('keydown', function(e) {
        const selected = window.parent.streamlit.getSessionState('selected_module_indices');
        if (!selected || selected.length === 0) return;
        
        let offset_x = 0, offset_y = 0;
        const step = e.shiftKey ? 0.1 : 0.5;
        
        switch(e.key) {
            case 'ArrowLeft':
                offset_x = -step;
                e.preventDefault();
                break;
            case 'ArrowRight':
                offset_x = step;
                e.preventDefault();
                break;
            case 'ArrowUp':
                offset_y = step;
                e.preventDefault();
                break;
            case 'ArrowDown':
                offset_y = -step;
                e.preventDefault();
                break;
            case 'r':
            case 'R':
                window.parent.streamlit.setSessionState('rotate_selected_trigger', true);
                e.preventDefault();
                break;
            case 'Delete':
                window.parent.streamlit.setSessionState('delete_selected_trigger', true);
                e.preventDefault();
                break;
            case 'c':
                if (e.ctrlKey) {
                    window.parent.streamlit.setSessionState('copy_selected_trigger', true);
                    e.preventDefault();
                }
                break;
            case 'v':
                if (e.ctrlKey) {
                    window.parent.streamlit.setSessionState('paste_trigger', true);
                    e.preventDefault();
                }
                break;
        }
        
        if (offset_x !== 0 || offset_y !== 0) {
            window.parent.streamlit.setSessionState('move_offset_x', offset_x);
            window.parent.streamlit.setSessionState('move_offset_y', offset_y);
            window.parent.streamlit.setSessionState('move_selected_trigger', true);
        }
    });
    </script>
    """
    
    st.components.v1.html(keyboard_js, height=0)
```

## 4. TEIL C: NEUE FEATURES

### 4.1 Feature 6: Modulfarben & Materialien (Requirement 6)

#### 4.1.1 Farb-System
**Datei:** `utils/pv3d_module_colors.py` (NEU)

```python
"""
PV-Modul Farben und Materialien System
"""

from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class ModuleMaterial:
    """Definiert Material-Eigenschaften eines PV-Moduls."""
    name: str
    color: str  # Hex-Code
    ambient: float  # Umgebungslicht (0-1)
    diffuse: float  # Diffuses Licht (0-1)
    specular: float  # Spiegelung (0-1)
    roughness: float  # Rauheit (0-1)
    metalness: float  # Metallischer Effekt (0-1)
    opacity: float  # Transparenz (0-1)


# Vordefinierte Materialien
MATERIALS = {
    "schwarz_matt": ModuleMaterial(
        name="Schwarz (Matt)",
        color="#1a1a1a",
        ambient=0.5,
        diffuse=0.8,
        specular=0.2,
        roughness=0.8,
        metalness=0.0,
        opacity=1.0
    ),
    "dunkelblau_matt": ModuleMaterial(
        name="Dunkelblau (Matt)",
        color="#1a1a2e",
        ambient=0.5,
        diffuse=0.8,
        specular=0.2,
        roughness=0.8,
        metalness=0.0,
        opacity=1.0
    ),
    "dunkelrot_matt": ModuleMaterial(
        name="Dunkelrot (Matt)",
        color="#8b0000",
        ambient=0.5,
        diffuse=0.8,
        specular=0.2,
        roughness=0.8,
        metalness=0.0,
        opacity=1.0
    ),
    "anthrazit_matt": ModuleMaterial(
        name="Anthrazit (Matt)",
        color="#2f4f4f",
        ambient=0.5,
        diffuse=0.8,
        specular=0.2,
        roughness=0.8,
        metalness=0.0,
        opacity=1.0
    ),
    "silber_glaenzend": ModuleMaterial(
        name="Silber (Glänzend)",
        color="#c0c0c0",
        ambient=0.6,
        diffuse=0.7,
        specular=0.9,
        roughness=0.1,
        metalness=0.8,
        opacity=1.0
    ),
    "schwarz_glaenzend": ModuleMaterial(
        name="Schwarz (Glänzend)",
        color="#1a1a1a",
        ambient=0.5,
        diffuse=0.7,
        specular=0.9,
        roughness=0.1,
        metalness=0.5,
        opacity=1.0
    ),
    "glas_glas": ModuleMaterial(
        name="Glas-Glas (Transparent)",
        color="#e0f7fa",
        ambient=0.8,
        diffuse=0.5,
        specular=0.95,
        roughness=0.05,
        metalness=0.0,
        opacity=0.7
    )
}


def apply_material_to_module(
    mesh: 'go.Mesh3d',
    material: ModuleMaterial
) -> 'go.Mesh3d':
    """
    Wendet Material-Eigenschaften auf Modul-Mesh an.
    """
    mesh.color = material.color
    mesh.opacity = material.opacity
    mesh.lighting = dict(
        ambient=material.ambient,
        diffuse=material.diffuse,
        specular=material.specular,
        roughness=material.roughness,
        fresnel=material.metalness * 0.5
    )
    
    return mesh


def render_material_selector() -> str:
    """
    Rendert UI für Material-Auswahl.
    
    Returns:
        Material-Key (z.B. "schwarz_matt")
    """
    import streamlit as st
    
    st.sidebar.subheader("🎨 Modul-Farbe & Material")
    
    # Gruppiere nach Oberfläche
    matt_materials = [k for k, v in MATERIALS.items() if "matt" in k.lower()]
    glaenzend_materials = [k for k, v in MATERIALS.items() if "glaenzend" in k.lower()]
    special_materials = [k for k, v in MATERIALS.items() if k not in matt_materials + glaenzend_materials]
    
    material_category = st.sidebar.radio(
        "Oberfläche",
        ["Matt", "Glänzend", "Spezial"],
        index=0
    )
    
    if material_category == "Matt":
        options = matt_materials
    elif material_category == "Glänzend":
        options = glaenzend_materials
    else:
        options = special_materials
    
    # Zeige Vorschau-Farben
    cols = st.sidebar.columns(len(options))
    selected_material = None
    
    for i, material_key in enumerate(options):
        material = MATERIALS[material_key]
        with cols[i]:
            if st.button(
                "●",
                key=f"material_{material_key}",
                help=material.name
            ):
                selected_material = material_key
            # Zeige Farbe als HTML
            st.markdown(
                f'<div style="background-color: {material.color}; '
                f'width: 100%; height: 20px; border-radius: 5px;"></div>',
                unsafe_allow_html=True
            )
    
    # Speichere Auswahl in Session State
    if selected_material:
        st.session_state["selected_module_material"] = selected_material
    
    return st.session_state.get("selected_module_material", "schwarz_matt")
```

#### 4.1.2 Integration in Modul-Rendering
**Datei:** `utils/pv3d_plotly.py`

```python
def create_pv_module_3d_with_material(
    x, y, z,
    material_key: str = "schwarz_matt",
    **kwargs
) -> Tuple[go.Mesh3d, np.ndarray]:
    """
    Erstellt PV-Modul mit ausgewähltem Material.
    """
    from utils.pv3d_module_colors import MATERIALS, apply_material_to_module
    
    # Erstelle Basis-Modul
    mesh, vertices = create_pv_module_3d(x, y, z, **kwargs)
    
    # Wende Material an
    material = MATERIALS.get(material_key, MATERIALS["schwarz_matt"])
    mesh = apply_material_to_module(mesh, material)
    
    return mesh, vertices
```

### 4.2 Feature 7: KI-Optimierung (Requirement 7)

#### 4.2.1 KI-Algorithmus
**Datei:** `utils/pv3d_ai_optimization.py` (NEU)

```python
"""
KI-basierte Modul-Anordnungs-Optimierung
"""

from typing import List, Dict, Tuple, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class LayoutScore:
    """Bewertung eines Layouts."""
    total_yield_kwh: float  # Gesamtertrag
    module_count: int  # Anzahl Module
    aesthetic_score: float  # Ästhetik (0-100)
    cost_eur: float  # Kosten
    roi_years: float  # Return on Investment
    
    def get_weighted_score(self, weights: Dict[str, float]) -> float:
        """Berechnet gewichtete Gesamtbewertung."""
        return (
            weights.get("yield", 0.4) * (self.total_yield_kwh / 1000) +
            weights.get("count", 0.2) * self.module_count +
            weights.get("aesthetic", 0.2) * self.aesthetic_score +
            weights.get("roi", 0.2) * (10 / max(self.roi_years, 0.1))
        )


class AILayoutOptimizer:
    """KI-Optimierer für Modul-Layouts."""
    
    def __init__(
        self,
        roof_length: float,
        roof_width: float,
        roof_type: str,
        roof_pitch: float
    ):
        self.roof_length = roof_length
        self.roof_width = roof_width
        self.roof_type = roof_type
        self.roof_pitch = roof_pitch
    
    def optimize_for_max_yield(self) -> List[Tuple[float, float, float]]:
        """
        Optimiert für maximalen Ertrag.
        
        Strategie:
        - Platziere Module an Positionen mit bester Sonneneinstrahlung
        - Vermeide verschattete Bereiche
        - Optimale Ausrichtung (Süd, 30-35°)
        """
        positions = []
        
        # Berechne Sonneneinstrahlungs-Heatmap
        irradiance_map = self._calculate_irradiance_map()
        
        # Sortiere Positionen nach Einstrahlung (höchste zuerst)
        sorted_positions = self._sort_by_irradiance(irradiance_map)
        
        # Platziere Module an besten Positionen
        for x, y in sorted_positions:
            z = self._calculate_z(y)
            
            # Prüfe Kollision
            if not self._has_collision(x, y, z, positions):
                positions.append((x, y, z))
        
        return positions
    
    def optimize_for_max_count(self) -> List[Tuple[float, float, float]]:
        """
        Optimiert für maximale Anzahl Module.
        
        Strategie:
        - Dichte Packung mit minimalem Abstand
        - Nutze gesamte verfügbare Fläche
        - Akzeptiere auch suboptimale Positionen
        """
        positions = []
        
        # Verwende minimalen Abstand
        min_spacing = 0.05  # 5cm
        
        # Grid mit dichter Packung
        grid_positions = self._calculate_dense_grid(min_spacing)
        
        for x, y in grid_positions:
            z = self._calculate_z(y)
            
            if not self._has_collision(x, y, z, positions):
                positions.append((x, y, z))
        
        return positions
    
    def optimize_for_aesthetics(self) -> List[Tuple[float, float, float]]:
        """
        Optimiert für beste Ästhetik.
        
        Strategie:
        - Symmetrische Anordnung
        - Gleichmäßige Abstände
        - Zentrierte Platzierung
        - Vermeidung von "Lücken"
        """
        positions = []
        
        # Berechne symmetrisches Grid
        symmetric_grid = self._calculate_symmetric_grid()
        
        for x, y in symmetric_grid:
            z = self._calculate_z(y)
            positions.append((x, y, z))
        
        return positions
    
    def _calculate_irradiance_map(self) -> np.ndarray:
        """Berechnet Sonneneinstrahlungs-Karte."""
        # Vereinfachte Simulation
        # In Realität: Berücksichtigung von Verschattung, Ausrichtung, etc.
        resolution = 50
        x_range = np.linspace(-self.roof_length/2, self.roof_length/2, resolution)
        y_range = np.linspace(-self.roof_width/2, self.roof_width/2, resolution)
        
        irradiance = np.zeros((resolution, resolution))
        
        for i, y in enumerate(y_range):
            for j, x in enumerate(x_range):
                # Höhere Einstrahlung in der Mitte, niedriger an Rändern
                dist_from_center = np.sqrt(x**2 + y**2)
                max_dist = np.sqrt((self.roof_length/2)**2 + (self.roof_width/2)**2)
                irradiance[i, j] = 1.0 - (dist_from_center / max_dist) * 0.3
        
        return irradiance
    
    def _calculate_z(self, y: float) -> float:
        """Berechnet Z-Position für gegebenes Y."""
        from utils.pv3d_placement_handler import calculate_z_position
        return calculate_z_position(
            self.roof_type, self.roof_pitch, self.roof_width, y
        )
    
    def _has_collision(
        self,
        x: float, y: float, z: float,
        existing: List[Tuple[float, float, float]]
    ) -> bool:
        """Prüft auf Kollision."""
        from utils.pv3d_placement_handler import check_module_collision
        result = check_module_collision(
            (x, y, z), existing,
            self.roof_length, self.roof_width
        )
        return result["collision"]
```


### 4.3 Feature 8: Wetter-Simulation (Requirement 8)

#### 4.3.1 Wetter-System
**Datei:** `utils/pv3d_weather.py` (NEU)

```python
"""
Realistische Wetter-Simulation für 3D-Visualisierung
"""

from typing import Dict, Any
from dataclasses import dataclass
import plotly.graph_objects as go

@dataclass
class WeatherCondition:
    """Definiert Wetterbedingungen."""
    name: str
    sky_color: str  # Himmel-Farbe
    ambient_light: float  # Umgebungslicht (0-1)
    sun_intensity: float  # Sonnenintensität (0-1)
    diffuse_factor: float  # Diffuse Strahlung (0-1)
    yield_factor: float  # Ertragsfaktor (0-1)
    particles: bool  # Partikel-Effekte (Regen/Schnee)


WEATHER_CONDITIONS = {
    "sonnig": WeatherCondition(
        name="Sonnig",
        sky_color="#87CEEB",
        ambient_light=0.8,
        sun_intensity=1.0,
        diffuse_factor=0.2,
        yield_factor=1.0,
        particles=False
    ),
    "bewoelkt": WeatherCondition(
        name="Bewölkt",
        sky_color="#B0C4DE",
        ambient_light=0.6,
        sun_intensity=0.4,
        diffuse_factor=0.8,
        yield_factor=0.6,
        particles=False
    ),
    "regen": WeatherCondition(
        name="Regen",
        sky_color="#778899",
        ambient_light=0.4,
        sun_intensity=0.2,
        diffuse_factor=0.9,
        yield_factor=0.3,
        particles=True
    ),
    "schnee": WeatherCondition(
        name="Schnee",
        sky_color="#F0F8FF",
        ambient_light=0.7,
        sun_intensity=0.3,
        diffuse_factor=0.85,
        yield_factor=0.1,  # Schneebedeckung reduziert Ertrag stark
        particles=True
    ),
    "nebel": WeatherCondition(
        name="Nebel",
        sky_color="#DCDCDC",
        ambient_light=0.5,
        sun_intensity=0.1,
        diffuse_factor=0.95,
        yield_factor=0.2,
        particles=False
    )
}


def apply_weather_to_scene(
    fig: go.Figure,
    weather_key: str = "sonnig"
) -> go.Figure:
    """
    Wendet Wetterbedingungen auf 3D-Szene an.
    """
    weather = WEATHER_CONDITIONS.get(weather_key, WEATHER_CONDITIONS["sonnig"])
    
    # Update Hintergrundfarbe (Himmel)
    fig.update_layout(
        scene=dict(
            bgcolor=weather.sky_color
        )
    )
    
    # Update Beleuchtung aller Meshes
    for trace in fig.data:
        if hasattr(trace, 'lighting'):
            trace.lighting = dict(
                ambient=weather.ambient_light,
                diffuse=weather.diffuse_factor,
                specular=0.5,
                roughness=0.3
            )
    
    # Füge Partikel-Effekte hinzu
    if weather.particles:
        if weather_key == "regen":
            fig = add_rain_particles(fig)
        elif weather_key == "schnee":
            fig = add_snow_particles(fig)
    
    return fig


def add_rain_particles(fig: go.Figure) -> go.Figure:
    """Fügt Regen-Partikel hinzu."""
    import numpy as np
    
    # Generiere Regentropfen
    n_drops = 200
    x = np.random.uniform(-15, 15, n_drops)
    y = np.random.uniform(-15, 15, n_drops)
    z = np.random.uniform(0, 20, n_drops)
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=2,
            color='rgba(100, 150, 200, 0.5)',
            symbol='diamond'
        ),
        name='Regen',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig


def add_snow_particles(fig: go.Figure) -> go.Figure:
    """Fügt Schnee-Partikel hinzu."""
    import numpy as np
    
    # Generiere Schneeflocken
    n_flakes = 150
    x = np.random.uniform(-15, 15, n_flakes)
    y = np.random.uniform(-15, 15, n_flakes)
    z = np.random.uniform(0, 20, n_flakes)
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=3,
            color='rgba(255, 255, 255, 0.8)',
            symbol='circle'
        ),
        name='Schnee',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    return fig


def calculate_weather_yield_impact(
    base_yield_kwh: float,
    weather_key: str
) -> Dict[str, float]:
    """
    Berechnet Ertragsverlust durch Wetter.
    
    Returns:
        {
            "base_yield": float,
            "weather_factor": float,
            "actual_yield": float,
            "loss_kwh": float,
            "loss_percent": float
        }
    """
    weather = WEATHER_CONDITIONS.get(weather_key, WEATHER_CONDITIONS["sonnig"])
    
    actual_yield = base_yield_kwh * weather.yield_factor
    loss_kwh = base_yield_kwh - actual_yield
    loss_percent = (1 - weather.yield_factor) * 100
    
    return {
        "base_yield": base_yield_kwh,
        "weather_factor": weather.yield_factor,
        "actual_yield": actual_yield,
        "loss_kwh": loss_kwh,
        "loss_percent": loss_percent
    }
```

### 4.4 Feature 10: Video-Export (Requirement 9)

#### 4.4.1 Video-Export-System
**Datei:** `utils/pv3d_video_export.py` (NEU)

```python
"""
Video-Export für 3D-Visualisierung
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
import numpy as np

def export_timelapse_video(
    fig: go.Figure,
    mode: str = "day",  # "day", "year", "custom"
    duration_seconds: int = 30,
    resolution: str = "1080p",  # "720p", "1080p", "4K"
    format: str = "mp4",  # "mp4", "gif", "webm"
    show_overlays: bool = True,
    output_path: str = "timelapse.mp4"
) -> Dict[str, Any]:
    """
    Exportiert Zeitraffer-Video der 3D-Visualisierung.
    
    Args:
        fig: Plotly Figure
        mode: Zeitraffer-Modus
        duration_seconds: Video-Länge in Sekunden
        resolution: Video-Auflösung
        format: Video-Format
        show_overlays: Text-Overlays anzeigen
        output_path: Ausgabe-Pfad
    
    Returns:
        {
            "success": bool,
            "output_path": str,
            "file_size_mb": float,
            "duration_seconds": float,
            "frame_count": int
        }
    """
    try:
        # Bestimme Auflösung
        width, height = _get_resolution(resolution)
        
        # Berechne Frame-Anzahl (24 FPS)
        fps = 24
        frame_count = duration_seconds * fps
        
        # Generiere Frames basierend auf Modus
        if mode == "day":
            frames = _generate_day_timelapse_frames(
                fig, frame_count, show_overlays
            )
        elif mode == "year":
            frames = _generate_year_timelapse_frames(
                fig, frame_count, show_overlays
            )
        else:  # custom
            frames = _generate_custom_frames(fig, frame_count)
        
        # Exportiere Video
        success = _export_frames_to_video(
            frames, output_path, fps, width, height, format
        )
        
        if success:
            import os
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size_mb": file_size,
                "duration_seconds": duration_seconds,
                "frame_count": frame_count
            }
        else:
            return {
                "success": False,
                "error": "Video-Export fehlgeschlagen"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _generate_day_timelapse_frames(
    fig: go.Figure,
    frame_count: int,
    show_overlays: bool
) -> List[np.ndarray]:
    """Generiert Frames für Tagesverlauf (24h in 30s)."""
    frames = []
    
    for i in range(frame_count):
        # Berechne Tageszeit (0-24 Stunden)
        hour = (i / frame_count) * 24
        
        # Update Sonnenposition
        fig_copy = _update_sun_position(fig, hour)
        
        # Füge Text-Overlay hinzu
        if show_overlays:
            fig_copy = _add_time_overlay(fig_copy, hour)
        
        # Rendere Frame
        frame = _render_figure_to_image(fig_copy)
        frames.append(frame)
    
    return frames


def _add_time_overlay(
    fig: go.Figure,
    hour: float
) -> go.Figure:
    """Fügt Zeit-Overlay zum Frame hinzu."""
    # Formatiere Zeit
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    time_str = f"{hour_int:02d}:{minute:02d}"
    
    # Füge Annotation hinzu
    fig.add_annotation(
        text=f"<b>{time_str} Uhr</b>",
        xref="paper", yref="paper",
        x=0.05, y=0.95,
        showarrow=False,
        font=dict(size=24, color="white"),
        bgcolor="rgba(0, 0, 0, 0.5)",
        borderpad=10
    )
    
    return fig
```

### 4.5 Feature 11: Vergleichs-Modus (Requirement 10)

#### 4.5.1 Side-by-Side Vergleich
**Datei:** `utils/pv3d_comparison.py` (NEU)

```python
"""
Vergleichs-Modus für verschiedene Konfigurationen
"""

from typing import Dict, Any, List, Tuple
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_comparison_view(
    config_a: Dict[str, Any],
    config_b: Dict[str, Any],
    sync_camera: bool = True
) -> go.Figure:
    """
    Erstellt Side-by-Side Vergleichsansicht.
    
    Args:
        config_a: Konfiguration A (links)
        config_b: Konfiguration B (rechts)
        sync_camera: Kamera-Bewegungen synchronisieren
    
    Returns:
        Plotly Figure mit 2 Subplots
    """
    # Erstelle 1x2 Subplot-Grid
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'scene'}]],
        subplot_titles=(
            f"Konfiguration A: {config_a['name']}",
            f"Konfiguration B: {config_b['name']}"
        ),
        horizontal_spacing=0.05
    )
    
    # Rendere Konfiguration A (links)
    traces_a = _build_scene_traces(config_a)
    for trace in traces_a:
        fig.add_trace(trace, row=1, col=1)
    
    # Rendere Konfiguration B (rechts)
    traces_b = _build_scene_traces(config_b)
    for trace in traces_b:
        fig.add_trace(trace, row=1, col=2)
    
    # Synchronisiere Kamera wenn aktiviert
    if sync_camera:
        camera = dict(
            eye=dict(x=1.5, y=1.5, z=1.2),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1)
        )
        fig.update_layout(
            scene=camera,
            scene2=camera
        )
    
    # Layout-Anpassungen
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Konfigurations-Vergleich"
    )
    
    return fig


def highlight_differences(
    fig: go.Figure,
    config_a: Dict[str, Any],
    config_b: Dict[str, Any]
) -> go.Figure:
    """
    Hebt Unterschiede zwischen Konfigurationen hervor.
    """
    # Finde unterschiedliche Module
    positions_a = set(config_a.get("module_positions", []))
    positions_b = set(config_b.get("module_positions", []))
    
    only_in_a = positions_a - positions_b
    only_in_b = positions_b - positions_a
    
    # Markiere Module die nur in A sind (rot)
    for x, y, z in only_in_a:
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers',
            marker=dict(size=10, color='red', symbol='x'),
            name='Nur in A',
            showlegend=False
        ), row=1, col=1)
    
    # Markiere Module die nur in B sind (grün)
    for x, y, z in only_in_b:
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers',
            marker=dict(size=10, color='green', symbol='circle'),
            name='Nur in B',
            showlegend=False
        ), row=1, col=2)
    
    return fig


def create_comparison_table(
    config_a: Dict[str, Any],
    config_b: Dict[str, Any]
) -> None:
    """
    Erstellt Vergleichstabelle mit Kennzahlen.
    """
    import pandas as pd
    
    # Sammle Kennzahlen
    metrics = {
        "Metrik": [
            "Modulanzahl",
            "Gesamtertrag (kWh/Jahr)",
            "Kosten (€)",
            "ROI (Jahre)",
            "CO₂-Einsparung (kg/Jahr)"
        ],
        config_a["name"]: [
            config_a.get("module_count", 0),
            config_a.get("total_yield_kwh", 0),
            config_a.get("total_cost_eur", 0),
            config_a.get("roi_years", 0),
            config_a.get("co2_savings_kg", 0)
        ],
        config_b["name"]: [
            config_b.get("module_count", 0),
            config_b.get("total_yield_kwh", 0),
            config_b.get("total_cost_eur", 0),
            config_b.get("roi_years", 0),
            config_b.get("co2_savings_kg", 0)
        ]
    }
    
    # Berechne Differenzen
    differences = []
    for i in range(len(metrics["Metrik"])):
        val_a = metrics[config_a["name"]][i]
        val_b = metrics[config_b["name"]][i]
        diff = val_b - val_a
        diff_percent = (diff / val_a * 100) if val_a != 0 else 0
        differences.append(f"{diff:+.1f} ({diff_percent:+.1f}%)")
    
    metrics["Differenz"] = differences
    
    # Zeige Tabelle
    df = pd.DataFrame(metrics)
    st.dataframe(df, use_container_width=True)
```

### 4.6 Feature 12: Gebäude-Umgebung (Requirement 11)

#### 4.6.1 3D-Objekt-Bibliothek
**Datei:** `utils/pv3d_environment.py` (NEU)

```python
"""
Interaktive Gebäude-Umgebung mit 3D-Objekten
"""

from typing import Dict, List, Tuple
import plotly.graph_objects as go
import numpy as np

class EnvironmentObject:
    """Basis-Klasse für Umgebungs-Objekte."""
    
    def __init__(
        self,
        x: float, y: float, z: float,
        width: float, length: float, height: float,
        name: str = "Object"
    ):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.length = length
        self.height = height
        self.name = name
    
    def to_mesh(self) -> go.Mesh3d:
        """Konvertiert Objekt zu Plotly Mesh."""
        raise NotImplementedError


class Tree(EnvironmentObject):
    """Baum-Objekt."""
    
    def __init__(self, x: float, y: float, height: float = 5.0, **kwargs):
        super().__init__(x, y, 0, 1.0, 1.0, height, "Baum")
        self.trunk_height = height * 0.4
        self.crown_radius = height * 0.3
    
    def to_mesh(self) -> List[go.Mesh3d]:
        """Erstellt Baum-Mesh (Stamm + Krone)."""
        meshes = []
        
        # Stamm (Zylinder)
        trunk = self._create_cylinder(
            self.x, self.y, 0,
            radius=0.2,
            height=self.trunk_height,
            color='#8B4513'  # Braun
        )
        meshes.append(trunk)
        
        # Krone (Kegel)
        crown = self._create_cone(
            self.x, self.y, self.trunk_height,
            radius=self.crown_radius,
            height=self.height - self.trunk_height,
            color='#228B22'  # Grün
        )
        meshes.append(crown)
        
        return meshes


class NeighborBuilding(EnvironmentObject):
    """Nachbargebäude."""
    
    def __init__(
        self,
        x: float, y: float,
        width: float, length: float, height: float,
        **kwargs
    ):
        super().__init__(x, y, 0, width, length, height, "Nachbargebäude")
    
    def to_mesh(self) -> go.Mesh3d:
        """Erstellt Gebäude-Mesh (Box)."""
        from utils.pv3d_plotly import create_complete_box
        
        return create_complete_box(
            x_min=self.x - self.width/2,
            x_max=self.x + self.width/2,
            y_min=self.y - self.length/2,
            y_max=self.y + self.length/2,
            z_min=0,
            z_max=self.height,
            color='#D3D3D3',  # Hellgrau
            name=self.name
        )
    
    def calculate_shadow(
        self,
        sun_azimuth: float,
        sun_elevation: float
    ) -> np.ndarray:
        """Berechnet Schatten des Gebäudes."""
        # Vereinfachte Schatten-Projektion
        shadow_length = self.height / np.tan(np.radians(sun_elevation))
        shadow_direction = np.array([
            np.sin(np.radians(sun_azimuth)),
            np.cos(np.radians(sun_azimuth))
        ])
        
        # Schatten-Polygon
        shadow_offset = shadow_direction * shadow_length
        
        corners = np.array([
            [self.x - self.width/2, self.y - self.length/2],
            [self.x + self.width/2, self.y - self.length/2],
            [self.x + self.width/2, self.y + self.length/2],
            [self.x - self.width/2, self.y + self.length/2]
        ])
        
        shadow_corners = corners + shadow_offset
        
        return shadow_corners


def render_environment_editor() -> Dict[str, Any]:
    """
    Rendert UI für Umgebungs-Editor.
    
    Returns:
        {
            "add_object": str or None,  # Typ des hinzuzufügenden Objekts
            "object_params": Dict  # Parameter für neues Objekt
        }
    """
    import streamlit as st
    
    st.sidebar.subheader("🌳 Umgebung")
    
    object_type = st.sidebar.selectbox(
        "Objekt hinzufügen",
        ["Keins", "Baum", "Nachbargebäude", "Schornstein", "Antenne"]
    )
    
    if object_type != "Keins":
        st.sidebar.write(f"**{object_type} platzieren:**")
        
        x = st.sidebar.slider("X-Position", -20.0, 20.0, 0.0, 0.5)
        y = st.sidebar.slider("Y-Position", -20.0, 20.0, 0.0, 0.5)
        
        if object_type == "Baum":
            height = st.sidebar.slider("Höhe (m)", 2.0, 15.0, 5.0, 0.5)
            params = {"x": x, "y": y, "height": height}
        
        elif object_type == "Nachbargebäude":
            width = st.sidebar.slider("Breite (m)", 5.0, 20.0, 10.0, 1.0)
            length = st.sidebar.slider("Länge (m)", 5.0, 20.0, 10.0, 1.0)
            height = st.sidebar.slider("Höhe (m)", 3.0, 30.0, 10.0, 1.0)
            params = {
                "x": x, "y": y,
                "width": width, "length": length, "height": height
            }
        
        else:
            params = {"x": x, "y": y}
        
        if st.sidebar.button(f"{object_type} hinzufügen"):
            return {
                "add_object": object_type,
                "object_params": params
            }
    
    return {"add_object": None, "object_params": {}}
```


### 4.7 Feature 13: Echtzeit-Kollaboration (Requirement 12)

#### 4.7.1 Kollaborations-System
**Datei:** `utils/pv3d_collaboration.py` (NEU)

```python
"""
Echtzeit-Kollaboration für 3D-Visualisierung
"""

from typing import Dict, List, Any, Optional
import streamlit as st
import json
import time
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class CollaborationSession:
    """Kollaborations-Session."""
    session_id: str
    created_at: float
    owner_name: str
    participants: List[str]
    share_link: str
    is_active: bool


@dataclass
class CollaborationEvent:
    """Kollaborations-Event (Änderung)."""
    event_id: str
    session_id: str
    user_name: str
    timestamp: float
    event_type: str  # "module_add", "module_move", "module_delete", etc.
    data: Dict[str, Any]


class CollaborationManager:
    """Verwaltet Echtzeit-Kollaboration."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.events: List[CollaborationEvent] = []
        self.cursors: Dict[str, Dict[str, float]] = {}  # user -> {x, y, z}
    
    def create_session(
        self,
        owner_name: str,
        project_data: Dict[str, Any]
    ) -> CollaborationSession:
        """
        Erstellt neue Kollaborations-Session.
        
        Returns:
            CollaborationSession mit Share-Link
        """
        # Generiere eindeutige Session-ID
        session_id = self._generate_session_id()
        
        # Generiere Share-Link
        share_link = f"https://app.example.com/collab/{session_id}"
        
        # Erstelle Session
        session = CollaborationSession(
            session_id=session_id,
            created_at=time.time(),
            owner_name=owner_name,
            participants=[owner_name],
            share_link=share_link,
            is_active=True
        )
        
        self.sessions[session_id] = session
        
        # Speichere Projekt-Daten
        self._save_session_data(session_id, project_data)
        
        return session
    
    def join_session(
        self,
        session_id: str,
        user_name: str
    ) -> Optional[CollaborationSession]:
        """
        Tritt bestehender Session bei.
        """
        session = self.sessions.get(session_id)
        
        if not session or not session.is_active:
            return None
        
        # Füge Teilnehmer hinzu
        if user_name not in session.participants:
            session.participants.append(user_name)
        
        return session
    
    def broadcast_event(
        self,
        session_id: str,
        user_name: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Sendet Event an alle Teilnehmer.
        """
        event = CollaborationEvent(
            event_id=self._generate_event_id(),
            session_id=session_id,
            user_name=user_name,
            timestamp=time.time(),
            event_type=event_type,
            data=data
        )
        
        self.events.append(event)
        
        # In Realität: WebSocket-Broadcast an alle Clients
        # Hier: Speichere in Session State für Polling
        self._store_event_for_polling(event)
    
    def update_cursor_position(
        self,
        session_id: str,
        user_name: str,
        x: float, y: float, z: float
    ) -> None:
        """
        Aktualisiert Cursor-Position eines Benutzers.
        """
        cursor_key = f"{session_id}:{user_name}"
        self.cursors[cursor_key] = {"x": x, "y": y, "z": z}
    
    def get_cursor_positions(
        self,
        session_id: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Holt Cursor-Positionen aller Teilnehmer.
        """
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        cursors = {}
        for user in session.participants:
            cursor_key = f"{session_id}:{user}"
            if cursor_key in self.cursors:
                cursors[user] = self.cursors[cursor_key]
        
        return cursors
    
    def _generate_session_id(self) -> str:
        """Generiert eindeutige Session-ID."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _generate_event_id(self) -> str:
        """Generiert eindeutige Event-ID."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]


def render_collaboration_ui() -> Dict[str, Any]:
    """
    Rendert UI für Kollaboration.
    
    Returns:
        {
            "action": str,  # "create", "join", "leave", None
            "session_id": str or None,
            "user_name": str
        }
    """
    st.sidebar.subheader("👥 Kollaboration")
    
    # Hole oder erstelle Benutzer-Namen
    if "collab_user_name" not in st.session_state:
        st.session_state["collab_user_name"] = f"Benutzer_{int(time.time()) % 1000}"
    
    user_name = st.sidebar.text_input(
        "Ihr Name",
        value=st.session_state["collab_user_name"]
    )
    st.session_state["collab_user_name"] = user_name
    
    # Prüfe ob bereits in Session
    current_session = st.session_state.get("collab_session_id")
    
    if current_session:
        # Bereits in Session
        st.sidebar.success(f"✓ Verbunden: Session {current_session[:8]}")
        
        # Zeige Teilnehmer
        manager = _get_collaboration_manager()
        session = manager.sessions.get(current_session)
        
        if session:
            st.sidebar.write("**Teilnehmer:**")
            for participant in session.participants:
                icon = "👑" if participant == session.owner_name else "👤"
                st.sidebar.write(f"{icon} {participant}")
        
        # Leave-Button
        if st.sidebar.button("Session verlassen"):
            return {
                "action": "leave",
                "session_id": current_session,
                "user_name": user_name
            }
    
    else:
        # Nicht in Session
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("Neue Session"):
                return {
                    "action": "create",
                    "session_id": None,
                    "user_name": user_name
                }
        
        with col2:
            session_id = st.text_input("Session-ID", max_chars=12)
            if st.button("Beitreten") and session_id:
                return {
                    "action": "join",
                    "session_id": session_id,
                    "user_name": user_name
                }
    
    return {"action": None, "session_id": None, "user_name": user_name}


def render_cursor_indicators(
    fig: go.Figure,
    session_id: str,
    current_user: str
) -> go.Figure:
    """
    Rendert Cursor-Indikatoren für andere Teilnehmer.
    """
    manager = _get_collaboration_manager()
    cursors = manager.get_cursor_positions(session_id)
    
    # Farben für verschiedene Benutzer
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for i, (user, pos) in enumerate(cursors.items()):
        if user == current_user:
            continue  # Eigenen Cursor nicht anzeigen
        
        color = colors[i % len(colors)]
        
        # Cursor als Marker
        fig.add_trace(go.Scatter3d(
            x=[pos["x"]],
            y=[pos["y"]],
            z=[pos["z"]],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color,
                symbol='diamond',
                line=dict(color='white', width=2)
            ),
            text=[user],
            textposition='top center',
            textfont=dict(size=12, color=color),
            name=f"Cursor: {user}",
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return fig


def _get_collaboration_manager() -> CollaborationManager:
    """Holt oder erstellt CollaborationManager."""
    if "collab_manager" not in st.session_state:
        st.session_state["collab_manager"] = CollaborationManager()
    return st.session_state["collab_manager"]
```

## 5. Implementation Plan

### 5.1 Phase 1: Kritische Bugfixes (Woche 1)
**Priorität: CRITICAL**

1. **Tag 1-2**: Fix `calculate_z_position()` für geneigte Dächer
   - Erweitere Funktion um `y_position` Parameter
   - Implementiere dachtyp-spezifische Z-Berechnung
   - Update `handle_auto_placement()` Aufrufe

2. **Tag 3-4**: Testing & Validation
   - Teste alle Dachtypen (Flach, Satteldach, Pultdach, Walmdach, Zeltdach)
   - Visuelle Inspektion der Modulplatzierung
   - Kollisions-Tests

3. **Tag 5**: Bug-Fixes & Dokumentation
   - Behebe gefundene Probleme
   - Dokumentiere Änderungen

### 5.2 Phase 2: Optimierungen (Woche 2-3)
**Priorität: HIGH**

1. **Woche 2**: Sonnenverlauf & Verschattung
   - Performance-Optimierung der Animation
   - Echtzeit-Schatten-Update
   - Direkte/indirekte Verschattung
   - Nachbargebäude-Integration

2. **Woche 3**: Ertrags-Heatmap & Manuelle Platzierung
   - Erweiterte Metriken (ROI, CO₂, etc.)
   - Hover-Details mit allen Metriken
   - Modul-Hervorhebung
   - Magnet-Funktion
   - Kopieren & Einfügen
   - Tastatur-Shortcuts

### 5.3 Phase 3: Neue Features (Woche 4-8)
**Priorität: MEDIUM**

1. **Woche 4**: Modulfarben & KI-Optimierung
   - Farb-System implementieren
   - Material-Eigenschaften
   - KI-Algorithmen (Max Ertrag, Max Anzahl, Ästhetik)

2. **Woche 5**: Wetter-Simulation
   - Wetter-Bedingungen (Sonnig, Bewölkt, Regen, Schnee, Nebel)
   - Partikel-Effekte
   - Ertragsverlust-Berechnung

3. **Woche 6**: Video-Export
   - Zeitraffer-Modi (Tag, Jahr, Custom)
   - Video-Formate (MP4, GIF, WebM)
   - Text-Overlays

4. **Woche 7**: Vergleichs-Modus & Umgebung
   - Side-by-Side Ansicht
   - Unterschieds-Hervorhebung
   - Vergleichstabelle
   - 3D-Objekt-Bibliothek (Bäume, Gebäude)

5. **Woche 8**: Echtzeit-Kollaboration
   - Session-Management
   - Event-Broadcasting
   - Cursor-Indikatoren
   - Chat-Integration

### 5.4 Phase 4: Testing & Polish (Woche 9)
**Priorität: HIGH**

1. **Integration Testing**: Alle Features zusammen testen
2. **Performance Testing**: Optimierung für große Anlagen
3. **User Testing**: Feedback von Benutzern einholen
4. **Bug Fixes**: Behebung gefundener Probleme
5. **Dokumentation**: Vollständige Benutzer-Dokumentation

## 6. Technical Considerations

### 6.1 Performance
- **Caching**: Verwende `@cached` Decorator für teure Berechnungen
- **Lazy Loading**: Lade Features nur bei Bedarf
- **Frame-Rate**: Adaptive FPS basierend auf Geräteleistung
- **Module Limit**: Maximal 200 Module für flüssige Performance

### 6.2 Compatibility
- **Browser**: Chrome, Firefox, Safari, Edge
- **Plotly Version**: >= 5.0.0
- **Streamlit Version**: >= 1.28.0
- **Python Version**: >= 3.10.0

### 6.3 Security
- **Session Isolation**: Jede Kollaborations-Session ist isoliert
- **Input Validation**: Alle Benutzereingaben validieren
- **Rate Limiting**: Begrenze API-Aufrufe für Kollaboration

### 6.4 Scalability
- **Modular Architecture**: Jedes Feature in separatem Modul
- **Plugin System**: Neue Features als Plugins hinzufügbar
- **Database**: Optional: Persistierung in Datenbank für Kollaboration

## 7. Testing Strategy

### 7.1 Unit Tests
```python
# tests/test_pv3d_placement.py
def test_calculate_z_position_flat_roof():
    """Test Z-Position für Flachdach."""
    z = calculate_z_position("Flachdach", 0.0, 10.0, 0.0)
    assert z == 0.30  # 30cm Aufständerung

def test_calculate_z_position_gabled_roof():
    """Test Z-Position für Satteldach."""
    # Am Rand (y = -5.0)
    z_edge = calculate_z_position("Satteldach", 30.0, 10.0, -5.0)
    assert z_edge == 0.15  # Basis-Z
    
    # In der Mitte (y = 0.0)
    z_middle = calculate_z_position("Satteldach", 30.0, 10.0, 0.0)
    assert z_middle > z_edge  # Höher als am Rand
```

### 7.2 Integration Tests
```python
# tests/test_pv3d_integration.py
def test_full_workflow():
    """Test kompletter Workflow."""
    # 1. Erstelle Gebäude
    dims = BuildingDims(10.0, 8.0, 3.0)
    
    # 2. Platziere Module automatisch
    result = handle_auto_placement(
        roof_length=10.0,
        roof_width=8.0,
        module_quantity=20,
        roof_type="Satteldach",
        roof_pitch=30.0
    )
    assert result["success"]
    assert result["count"] > 0
    
    # 3. Berechne Verschattung
    shading = calculate_shading_analysis_enhanced(
        result["positions"],
        {},
        180.0,  # Süd
        45.0    # 45° Elevation
    )
    assert len(shading["direct_shading"]) == result["count"]
    
    # 4. Erstelle Heatmap
    heatmap = calculate_yield_heatmap_enhanced(
        result["positions"],
        {}
    )
    assert len(heatmap["annual_yield_kwh"]) == result["count"]
```

### 7.3 Visual Regression Tests
- Screenshot-Vergleiche für verschiedene Dachtypen
- Automatische Erkennung von Rendering-Fehlern
- Vergleich vor/nach Änderungen

## 8. Documentation

### 8.1 User Documentation
- **Schnellstart-Guide**: Erste Schritte mit 3D-Visualisierung
- **Feature-Guides**: Detaillierte Anleitungen für jedes Feature
- **Video-Tutorials**: Screencasts für komplexe Workflows
- **FAQ**: Häufig gestellte Fragen

### 8.2 Developer Documentation
- **API-Referenz**: Alle Funktionen und Parameter
- **Architecture-Diagramme**: System-Übersicht
- **Code-Beispiele**: Best Practices
- **Contribution-Guide**: Wie man beiträgt

## 9. Success Metrics

### 9.1 Functional Metrics
- ✅ Module werden korrekt auf allen Dachtypen platziert
- ✅ Keine Kollisionen oder Überlappungen
- ✅ Alle 7 neuen Features funktionieren
- ✅ Performance: <2s für 100 Module

### 9.2 User Experience Metrics
- ✅ Intuitive Bedienung (User Testing)
- ✅ Flüssige Animationen (>24 FPS)
- ✅ Responsive UI (<100ms Reaktionszeit)
- ✅ Positive Benutzer-Feedback

### 9.3 Code Quality Metrics
- ✅ Test Coverage >80%
- ✅ Keine kritischen Bugs
- ✅ Code-Review bestanden
- ✅ Dokumentation vollständig

## 10. Risks & Mitigation

### 10.1 Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance-Probleme bei vielen Modulen | HIGH | MEDIUM | Caching, Lazy Loading, Module Limit |
| Browser-Kompatibilität | MEDIUM | LOW | Cross-Browser Testing |
| Kollaborations-Latenz | MEDIUM | MEDIUM | WebSocket-Optimierung, Polling-Fallback |

### 10.2 Schedule Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Verzögerung bei KI-Features | MEDIUM | MEDIUM | Vereinfachte Algorithmen, MVP-Ansatz |
| Testing dauert länger | LOW | HIGH | Automatisierte Tests, Continuous Integration |

## 11. Conclusion

Dieses Design-Dokument beschreibt eine umfassende Lösung für die 3D-PV-Visualisierung mit:
- **Kritischen Bugfixes** für korrekte Modulplatzierung
- **Performance-Optimierungen** für bestehende Features
- **7 innovativen neuen Features** für "Next-Level" Visualisierung

Die modulare Architektur ermöglicht schrittweise Implementierung und einfache Erweiterbarkeit. Mit dem vorgeschlagenen 9-Wochen-Plan können alle Features systematisch umgesetzt werden.
