"""
3D PV-Visualisierung mit Plotly

Hochwertige 3D-Visualisierung für Photovoltaik-Anlagen auf Gebäuden.
Verwendet Plotly für interaktive, browserbasierte 3D-Grafiken.
"""

import math
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

# Import der Datenklassen aus der Original-Datei
from utils.pv3d import (
    BuildingDims, 
    LayoutConfig, 
    AdvancedLayoutConfig,
    ModuleTransform,
    ModuleGroup,
    PV_W, 
    PV_H, 
    PV_T,
    ROOF_COLORS,
    _deg_to_rad
)


# ============================================================================
# VOLLSTÄNDIGE 3D MESH GENERATOREN
# ============================================================================

def create_complete_box(x_min, x_max, y_min, y_max, z_min, z_max, color="#d4d4d4", name="Box"):
    """Erstellt eine vollständige Box mit allen 6 Seiten."""
    # 8 Ecken der Box
    vertices = np.array([
        [x_min, y_min, z_min],  # 0
        [x_max, y_min, z_min],  # 1
        [x_max, y_max, z_min],  # 2
        [x_min, y_max, z_min],  # 3
        [x_min, y_min, z_max],  # 4
        [x_max, y_min, z_max],  # 5
        [x_max, y_max, z_max],  # 6
        [x_min, y_max, z_max],  # 7
    ])
    
    # Alle 12 Dreiecke (6 Seiten * 2 Dreiecke)
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 5, 5, 1, 1, 6, 6, 2, 2, 7, 7, 3, 3]
    j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 4, 1, 6, 4, 5, 0, 7, 5, 6, 1, 4, 6, 7, 2]
    k = [3, 2, 5, 6, 6, 7, 7, 4, 7, 6, 5, 4, 4, 5, 0, 4, 5, 6, 1, 2, 6, 7, 2, 3]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=0.85,
        name=name,
        showlegend=False,
        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.3, roughness=0.5),
        lightposition=dict(x=100, y=100, z=100)
    )


def create_gabled_roof_complete(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein vollständiges Satteldach mit beiden Dachflächen und Giebeln."""
    # 6 Punkte für Satteldach
    half_l = length / 2
    half_w = width / 2
    
    vertices = np.array([
        [-half_l, -half_w, base_z],  # 0: links vorne unten
        [half_l, -half_w, base_z],   # 1: rechts vorne unten
        [half_l, half_w, base_z],    # 2: rechts hinten unten
        [-half_l, half_w, base_z],   # 3: links hinten unten
        [-half_l, 0, base_z + height],  # 4: links oben (First)
        [half_l, 0, base_z + height],   # 5: rechts oben (First)
    ])
    
    # Dreiecke für alle Flächen
    i = [0, 0, 3, 3, 0, 2]
    j = [1, 5, 4, 5, 4, 5]
    k = [5, 4, 5, 2, 1, 3]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=0.9,
        name=name,
        showlegend=False,
        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4, roughness=0.3),
        lightposition=dict(x=100, y=100, z=100)
    )


def create_pv_module_3d(x, y, z, azimuth_deg=0, tilt_deg=15, color="#1a1a2e", selected=False):
    """
    Erstellt ein detailliertes PV-Modul mit Dicke und korrekter Rotation.
    """
    # Lokale Koordinaten (Modul zentriert im Ursprung)
    hw = PV_W / 2
    hh = PV_H / 2
    ht = PV_T / 2
    
    # 8 Ecken des Moduls (wie ein flacher Quader)
    local_vertices = np.array([
        [-hw, -hh, -ht],  # 0: links vorne unten
        [hw, -hh, -ht],   # 1: rechts vorne unten
        [hw, hh, -ht],    # 2: rechts hinten unten
        [-hw, hh, -ht],   # 3: links hinten unten
        [-hw, -hh, ht],   # 4: links vorne oben
        [hw, -hh, ht],    # 5: rechts vorne oben
        [hw, hh, ht],     # 6: rechts hinten oben
        [-hw, hh, ht],    # 7: links hinten oben
    ])
    
    # Rotation um Y-Achse (Tilt/Neigung)
    tilt_rad = np.deg2rad(tilt_deg)
    Ry = np.array([
        [np.cos(tilt_rad), 0, np.sin(tilt_rad)],
        [0, 1, 0],
        [-np.sin(tilt_rad), 0, np.cos(tilt_rad)]
    ])
    
    # Rotation um Z-Achse (Azimuth)
    az_rad = np.deg2rad(azimuth_deg)
    Rz = np.array([
        [np.cos(az_rad), -np.sin(az_rad), 0],
        [np.sin(az_rad), np.cos(az_rad), 0],
        [0, 0, 1]
    ])
    
    # Kombinierte Rotation: erst Tilt, dann Azimuth
    R = Rz @ Ry
    
    # Rotiere alle Vertices
    rotated = (R @ local_vertices.T).T
    
    # Verschiebe zur finalen Position
    final_vertices = rotated + np.array([x, y, z])
    
    # Alle 12 Dreiecke für vollständigen Quader
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 5, 5, 1, 1, 6, 6, 2, 2, 7, 7, 3, 3]
    j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 4, 1, 6, 4, 5, 0, 7, 5, 6, 1, 4, 6, 7, 2]
    k = [3, 2, 5, 6, 6, 7, 7, 4, 7, 6, 5, 4, 4, 5, 0, 4, 5, 6, 1, 2, 6, 7, 2, 3]
    
    module_color = "#ff6b35" if selected else color
    
    return go.Mesh3d(
        x=final_vertices[:, 0],
        y=final_vertices[:, 1],
        z=final_vertices[:, 2],
        i=i, j=j, k=k,
        color=module_color,
        opacity=0.95,
        name="PV Module",
        showlegend=False,
        lighting=dict(ambient=0.5, diffuse=0.9, specular=0.5, roughness=0.2),
        lightposition=dict(x=100, y=100, z=100)
    )


def create_sun_marker(azimuth_deg, elevation_deg, distance=20.0):
    """Erstellt eine Sonne als leuchtenden Marker."""
    # Konvertiere Azimuth/Elevation zu kartesischen Koordinaten
    az_rad = np.deg2rad(azimuth_deg)
    el_rad = np.deg2rad(elevation_deg)
    
    x = distance * np.cos(el_rad) * np.sin(az_rad)
    y = distance * np.cos(el_rad) * np.cos(az_rad)
    z = distance * np.sin(el_rad)
    
    return go.Scatter3d(
        x=[x], y=[y], z=[z],
        mode='markers',
        marker=dict(
            size=20,
            color='gold',
            symbol='circle',
            line=dict(color='orange', width=3)
        ),
        name='☀️ Sonne',
        showlegend=True,
        hovertemplate=f'Sonne<br>Azimuth: {azimuth_deg:.1f}°<br>Elevation: {elevation_deg:.1f}°<extra></extra>'
    )


def calculate_grid_positions(length, width, count, spacing_x=0.15, spacing_y=0.15):
    """Berechnet Grid-Positionen für PV-Module mit Spacing."""
    positions = []
    
    # Berechne wie viele Module in X und Y passen
    modules_x = int(length / (PV_W + spacing_x))
    modules_y = int(width / (PV_H + spacing_y))
    
    # Zentriere das Grid
    total_width_x = modules_x * (PV_W + spacing_x) - spacing_x
    total_width_y = modules_y * (PV_H + spacing_y) - spacing_y
    
    start_x = -total_width_x / 2
    start_y = -total_width_y / 2
    
    # Erstelle Grid
    for row in range(modules_y):
        for col in range(modules_x):
            if len(positions) >= count:
                break
            
            x = start_x + col * (PV_W + spacing_x) + PV_W / 2
            y = start_y + row * (PV_H + spacing_y) + PV_H / 2
            positions.append((x, y))
        
        if len(positions) >= count:
            break
    
    return positions


# ============================================================================
# HAUPTFUNKTION: VOLLSTÄNDIGE 3D-SZENE
# ============================================================================

def build_plotly_scene(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: Any = None,
    selected_modules: List[int] = None
) -> go.Figure:
    """
    Erstellt eine vollständige, hochwertige 3D-Szene mit Plotly.
    
    Args:
        project_data: Projekt-Daten Dictionary
        dims: Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Anzahl der Module
        layout_config: Layout-Konfiguration
        selected_modules: Liste ausgewählter Module
        
    Returns:
        Plotly Figure mit vollständiger 3D-Szene
    """
    if selected_modules is None:
        selected_modules = []
    
    fig = go.Figure()
    
    # ========== 1. GEBÄUDE (vollständig) ==========
    building = create_complete_box(
        x_min=-dims.length_m/2,
        x_max=dims.length_m/2,
        y_min=-dims.width_m/2,
        y_max=dims.width_m/2,
        z_min=0,
        z_max=dims.wall_height_m,
        color="#e8e8e8",
        name="Gebäude"
    )
    fig.add_trace(building)
    
    # ========== 2. DACH (vollständig) ==========
    roof_color = ROOF_COLORS.get(
        project_data.get("roof_covering", "default"),
        ROOF_COLORS["default"]
    )
    
    roof_z = dims.wall_height_m
    default_tilt = 15.0
    
    if roof_type == "Flachdach":
        # Flachdach als dünne Box
        roof = create_complete_box(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.1,
            color=roof_color,
            name="Dach"
        )
        fig.add_trace(roof)
        module_base_z = roof_z + 0.15
        default_tilt = 15.0
        
    elif roof_type == "Satteldach":
        roof_inclination = project_data.get("roof_inclination_deg", 35.0)
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        
        roof = create_gabled_roof_complete(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach"
        )
        fig.add_trace(roof)
        module_base_z = roof_z + 0.1
        default_tilt = roof_inclination
    
    else:
        # Fallback: Flachdach
        roof = create_complete_box(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.1,
            color=roof_color,
            name="Dach"
        )
        fig.add_trace(roof)
        module_base_z = roof_z + 0.15
        default_tilt = 15.0
    
    # ========== 3. PV-MODULE ==========
    positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
    
    for i, (x, y) in enumerate(positions):
        if i >= module_quantity:
            break
        
        # Standard-Werte
        azimuth = 0.0  # Süd
        tilt = default_tilt
        z = module_base_z
        
        # Transformationen anwenden wenn AdvancedLayoutConfig
        if isinstance(layout_config, AdvancedLayoutConfig):
            if i in layout_config.module_transforms:
                transform = layout_config.module_transforms[i]
                azimuth = transform.azimuth_deg
                tilt = transform.tilt_deg
                x += transform.offset_x
                y += transform.offset_y
                z += transform.offset_z
        
        # Modul erstellen
        is_selected = i in selected_modules
        module = create_pv_module_3d(
            x, y, z,
            azimuth_deg=azimuth,
            tilt_deg=tilt,
            color="#1a1a2e",
            selected=is_selected
        )
        fig.add_trace(module)
    
    # ========== 4. SONNE (optional) ==========
    if isinstance(layout_config, AdvancedLayoutConfig) and layout_config.enable_shading_analysis:
        sun_azimuth = project_data.get("sun_azimuth", 180.0)
        sun_elevation = project_data.get("sun_elevation", 45.0)
        sun = create_sun_marker(sun_azimuth, sun_elevation)
        fig.add_trace(sun)
    
    # ========== 5. LAYOUT & KAMERA ==========
    max_dim = max(dims.length_m, dims.width_m, dims.wall_height_m)
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='Länge (m)',
                showgrid=True,
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='#f5f5f5'
            ),
            yaxis=dict(
                title='Breite (m)',
                showgrid=True,
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='#f5f5f5'
            ),
            zaxis=dict(
                title='Höhe (m)',
                showgrid=True,
                gridcolor='lightgray',
                showbackground=True,
                backgroundcolor='#f5f5f5'
            ),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.8, y=-1.8, z=1.3),
                center=dict(x=0, y=0, z=0.3),
                up=dict(x=0, y=0, z=1)
            ),
            bgcolor='#e8f4f8'
        ),
        title=dict(
            text=f'🏠 3D PV-Visualisierung ({module_quantity} Module)',
            font=dict(size=18, color='#333')
        ),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#ccc',
            borderwidth=1
        ),
        height=750,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='white',
        hovermode='closest'
    )
    
    return fig
