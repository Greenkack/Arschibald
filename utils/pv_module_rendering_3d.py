"""
3D-Rendering für PV-Module mit dem Placement-System
===================================================

Integration des ModulePlacementManager mit Plotly 3D-Rendering.
Rendert Module mit allen Transformationen, Farben und Gruppierungen.
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Dict, Optional, Tuple

from utils.pv_module_placement_system import (
    PVModule,
    ModulePlacementManager,
    ModuleType,
    ModuleOrientation,
)


def render_pv_module_3d(module: PVModule, show_selection: bool = True) -> go.Mesh3d:
    """
    Rendert ein einzelnes PV-Modul als 3D-Mesh.
    
    Args:
        module: Das zu rendernde Modul
        show_selection: Ob Auswahl-Status visuell angezeigt werden soll
        
    Returns:
        Plotly Mesh3d-Objekt
    """
    # Hole Vertices des Moduls
    vertices = module.get_vertices_3d()
    
    # Farbe basierend auf Typ
    color = module.get_color()
    
    # Bei Auswahl: hellere Farbe
    if show_selection and module.is_selected:
        # Konvertiere Hex zu RGB und mache heller
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # 50% heller
        r = min(255, int(r * 1.5))
        g = min(255, int(g * 1.5))
        b = min(255, int(b * 1.5))
        
        color = f"#{r:02x}{g:02x}{b:02x}"
    
    # Erstelle Mesh (Quader mit 12 Dreiecken)
    # 8 Vertices -> 6 Seiten -> 12 Dreiecke
    i = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
    j = [1, 2, 6, 7, 5, 4, 6, 7, 3, 7, 5, 6]
    k = [2, 3, 5, 6, 1, 5, 7, 3, 7, 4, 6, 2]
    
    mesh = go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=0.95 if not module.is_locked else 0.7,
        name=f"Modul {module.id}" if module.name is None else module.name,
        showlegend=False,
        flatshading=False,
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            specular=0.4,
            roughness=0.5,
            fresnel=0.2
        ),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=1),
        customdata=[module.id],  # Für Interaktivität
        hovertemplate=(
            f"<b>{module.name or f'Modul {module.id}'}</b><br>" +
            f"Typ: {module.module_type.display_name}<br>" +
            f"Leistung: {module.dimensions.power_wp:.0f} Wp<br>" +
            f"Position: ({module.transform.x:.2f}, {module.transform.y:.2f}, {module.transform.z:.2f})<br>" +
            f"Neigung: {module.transform.rotation_x:.1f}°<br>" +
            f"<extra></extra>"
        )
    )
    
    return mesh


def render_module_edges_3d(module: PVModule, color: str = 'black', 
                           line_width: int = 2) -> go.Scatter3d:
    """
    Rendert die Kanten eines PV-Moduls als Linien.
    
    Args:
        module: Das Modul
        color: Linienfarbe
        line_width: Linienbreite
        
    Returns:
        Plotly Scatter3d-Objekt mit Linien
    """
    vertices = module.get_vertices_3d()
    
    # 12 Kanten eines Quaders
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Untere Fläche
        (4, 5), (5, 6), (6, 7), (7, 4),  # Obere Fläche
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertikale Kanten
    ]
    
    # Erstelle Linienpunkte (mit None als Trenner)
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([vertices[start, 0], vertices[end, 0], None])
        y_lines.extend([vertices[start, 1], vertices[end, 1], None])
        z_lines.extend([vertices[start, 2], vertices[end, 2], None])
    
    return go.Scatter3d(
        x=x_lines,
        y=y_lines,
        z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def render_all_modules(manager: ModulePlacementManager, 
                      show_edges: bool = True,
                      show_selection: bool = True) -> List[go.Mesh3d]:
    """
    Rendert alle Module aus dem Manager.
    
    Args:
        manager: ModulePlacementManager mit allen Modulen
        show_edges: Ob Kanten angezeigt werden sollen
        show_selection: Ob Auswahl-Status angezeigt werden soll
        
    Returns:
        Liste von Plotly-Objekten (Meshes + optional Edges)
    """
    traces = []
    
    print(f"render_all_modules: Rendere {len(manager.modules)} Module...")
    
    for module in manager.get_all_modules():
        # Modul-Mesh
        mesh = render_pv_module_3d(module, show_selection=show_selection)
        traces.append(mesh)
        
        print(f"  Modul {module.id} gerendert bei ({module.transform.x:.2f}, {module.transform.y:.2f}, {module.transform.z:.2f})")
        
        # Kanten
        if show_edges:
            edges = render_module_edges_3d(module)
            traces.append(edges)
    
    return traces


def render_module_group_indicator(manager: ModulePlacementManager, 
                                  group_id: int) -> Optional[go.Scatter3d]:
    """
    Rendert einen visuellen Indikator für eine Modul-Gruppe.
    
    Args:
        manager: ModulePlacementManager
        group_id: ID der Gruppe
        
    Returns:
        Plotly Scatter3d-Objekt oder None
    """
    if group_id not in manager.groups:
        return None
    
    group = manager.groups[group_id]
    
    # Sammle alle Positionen der Module in der Gruppe
    positions = []
    for mid in group.module_ids:
        if mid in manager.modules:
            m = manager.modules[mid]
            positions.append([m.transform.x, m.transform.y, m.transform.z])
    
    if not positions:
        return None
    
    positions = np.array(positions)
    
    # Berechne Zentrum und Bounding Box
    center = positions.mean(axis=0)
    min_pos = positions.min(axis=0)
    max_pos = positions.max(axis=0)
    
    # Erstelle Bounding Box Kanten
    corners = np.array([
        [min_pos[0], min_pos[1], min_pos[2]],
        [max_pos[0], min_pos[1], min_pos[2]],
        [max_pos[0], max_pos[1], min_pos[2]],
        [min_pos[0], max_pos[1], min_pos[2]],
        [min_pos[0], min_pos[1], max_pos[2]],
        [max_pos[0], min_pos[1], max_pos[2]],
        [max_pos[0], max_pos[1], max_pos[2]],
        [min_pos[0], max_pos[1], max_pos[2]],
    ])
    
    # Kanten der Bounding Box
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Unten
        (4, 5), (5, 6), (6, 7), (7, 4),  # Oben
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertikal
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([corners[start, 0], corners[end, 0], None])
        y_lines.extend([corners[start, 1], corners[end, 1], None])
        z_lines.extend([corners[start, 2], corners[end, 2], None])
    
    return go.Scatter3d(
        x=x_lines,
        y=y_lines,
        z=z_lines,
        mode='lines',
        line=dict(color=group.color_tag, width=3, dash='dash'),
        name=group.name,
        showlegend=True,
        hovertemplate=f"<b>{group.name}</b><br>Module: {len(group.module_ids)}<extra></extra>"
    )


def render_roof_surface_wireframe(surface_vertices: List[Tuple[float, float, float]], 
                                  color: str = 'rgba(100, 100, 255, 0.3)',
                                  name: str = "Dachfläche") -> go.Scatter3d:
    """
    Rendert eine Dachfläche als Wireframe.
    
    Args:
        surface_vertices: Liste von (x, y, z) Punkten
        color: Farbe der Linien
        name: Name für Legende
        
    Returns:
        Plotly Scatter3d-Objekt
    """
    if not surface_vertices:
        return None
    
    # Schließe das Polygon
    vertices = surface_vertices + [surface_vertices[0]]
    
    x = [v[0] for v in vertices]
    y = [v[1] for v in vertices]
    z = [v[2] for v in vertices]
    
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='lines',
        line=dict(color=color, width=3, dash='dot'),
        name=name,
        showlegend=True,
        hovertemplate=f"<b>{name}</b><extra></extra>"
    )


def create_grid_helper(center: Tuple[float, float, float],
                       size: float = 10.0,
                       spacing: float = 1.0,
                       color: str = 'rgba(200, 200, 200, 0.3)') -> List[go.Scatter3d]:
    """
    Erstellt ein Hilfs-Grid für die Platzierung.
    
    Args:
        center: Zentrum des Grids (x, y, z)
        size: Größe des Grids in m
        spacing: Abstand zwischen Grid-Linien
        color: Farbe der Grid-Linien
        
    Returns:
        Liste von Scatter3d-Objekten
    """
    traces = []
    half_size = size / 2
    cx, cy, cz = center
    
    # X-Linien (parallel zur X-Achse)
    for y in np.arange(-half_size, half_size + spacing, spacing):
        traces.append(go.Scatter3d(
            x=[cx - half_size, cx + half_size],
            y=[cy + y, cy + y],
            z=[cz, cz],
            mode='lines',
            line=dict(color=color, width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Y-Linien (parallel zur Y-Achse)
    for x in np.arange(-half_size, half_size + spacing, spacing):
        traces.append(go.Scatter3d(
            x=[cx + x, cx + x],
            y=[cy - half_size, cy + half_size],
            z=[cz, cz],
            mode='lines',
            line=dict(color=color, width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    return traces


def render_placement_statistics(manager: ModulePlacementManager,
                                position: Tuple[float, float, float]) -> go.Scatter3d:
    """
    Rendert Statistiken als 3D-Text.
    
    Args:
        manager: ModulePlacementManager
        position: Position für den Text
        
    Returns:
        Plotly Scatter3d mit Text-Annotation
    """
    stats = manager.get_statistics()
    
    text = (
        f"<b>PV-Anlage</b><br>" +
        f"Module: {stats['total_modules']}<br>" +
        f"Leistung: {stats['total_power_kwp']:.2f} kWp<br>" +
        f"Fläche: {stats['total_area_m2']:.1f} m²<br>" +
        f"Mono: {stats['monocrystalline_count']} | " +
        f"Poly: {stats['polycrystalline_count']}"
    )
    
    return go.Scatter3d(
        x=[position[0]],
        y=[position[1]],
        z=[position[2]],
        mode='text',
        text=[text],
        textposition='middle center',
        textfont=dict(size=10, color='black'),
        showlegend=False,
        hoverinfo='skip'
    )


def create_module_transform_gizmo(module: PVModule, 
                                  size: float = 0.5) -> List[go.Scatter3d]:
    """
    Erstellt ein Transform-Gizmo (Achsen) für ein Modul.
    
    Args:
        module: Das Modul
        size: Größe der Achsen
        
    Returns:
        Liste von Scatter3d-Objekten (X, Y, Z Achsen)
    """
    cx, cy, cz = module.transform.x, module.transform.y, module.transform.z
    
    gizmos = []
    
    # X-Achse (Rot)
    gizmos.append(go.Scatter3d(
        x=[cx, cx + size],
        y=[cy, cy],
        z=[cz, cz],
        mode='lines+markers',
        line=dict(color='red', width=6),
        marker=dict(size=6, color='red', symbol='arrow'),
        name='X-Achse',
        showlegend=False,
        hovertemplate='X-Achse<extra></extra>'
    ))
    
    # Y-Achse (Grün)
    gizmos.append(go.Scatter3d(
        x=[cx, cx],
        y=[cy, cy + size],
        z=[cz, cz],
        mode='lines+markers',
        line=dict(color='green', width=6),
        marker=dict(size=6, color='green', symbol='arrow'),
        name='Y-Achse',
        showlegend=False,
        hovertemplate='Y-Achse<extra></extra>'
    ))
    
    # Z-Achse (Blau)
    gizmos.append(go.Scatter3d(
        x=[cx, cx],
        y=[cy, cy],
        z=[cz, cz + size],
        mode='lines+markers',
        line=dict(color='blue', width=6),
        marker=dict(size=6, color='blue', symbol='arrow'),
        name='Z-Achse',
        showlegend=False,
        hovertemplate='Z-Achse<extra></extra>'
    ))
    
    return gizmos
