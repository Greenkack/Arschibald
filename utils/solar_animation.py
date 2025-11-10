"""
Solar-Animationen für 3D-Visualisierung
========================================

Dieses Modul enthält Funktionen zur Erstellung von Animationen
für die 3D-Visualisierung der PV-Anlage.
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import streamlit as st


def create_sun_path_animation(
    fig: go.Figure,
    building_center: Tuple[float, float, float],
    radius: float = 50.0,
    num_frames: int = 24
) -> go.Figure:
    """
    Erstellt eine Animation des Sonnenpfads über dem Gebäude.
    
    Args:
        fig: Plotly Figure
        building_center: Mittelpunkt des Gebäudes (x, y, z)
        radius: Radius der Sonnenbahn
        num_frames: Anzahl der Frames (24 = 1 Frame pro Stunde)
        
    Returns:
        Figure mit Animation
    """
    frames = []
    
    for i in range(num_frames):
        # Winkel für aktuelle Tageszeit (0-360°)
        angle = (i / num_frames) * 360
        angle_rad = np.radians(angle)
        
        # Sonnenposition berechnen
        sun_x = building_center[0] + radius * np.cos(angle_rad)
        sun_y = building_center[1] + radius * np.sin(angle_rad)
        # Höhe variiert mit sin (höchster Punkt bei 90°)
        sun_z = building_center[2] + radius * abs(np.sin(angle_rad))
        
        # Sonne als Scatter3d
        sun_trace = go.Scatter3d(
            x=[sun_x],
            y=[sun_y],
            z=[sun_z],
            mode='markers',
            marker=dict(
                size=15,
                color='yellow',
                symbol='circle',
                line=dict(color='orange', width=2)
            ),
            name=f'Sonne ({i}:00 Uhr)',
            showlegend=False
        )
        
        # Sonnenstrahlen
        rays = []
        for module_point in _get_module_center_points(fig):
            rays.append(go.Scatter3d(
                x=[sun_x, module_point[0]],
                y=[sun_y, module_point[1]],
                z=[sun_z, module_point[2]],
                mode='lines',
                line=dict(color='rgba(255, 255, 0, 0.2)', width=1),
                showlegend=False
            ))
        
        frame_data = [sun_trace] + rays
        frames.append(go.Frame(data=frame_data, name=str(i)))
    
    fig.frames = frames
    
    # Animation-Buttons hinzufügen
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': '▶ Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 500, 'redraw': True},
                        'fromcurrent': True,
                        'mode': 'immediate'
                    }]
                },
                {
                    'label': '⏸ Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }
            ]
        }],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'args': [[f.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate'
                    }],
                    'label': f'{i}:00',
                    'method': 'animate'
                }
                for i, f in enumerate(frames)
            ]
        }]
    )
    
    return fig


def create_360_rotation_animation(
    fig: go.Figure,
    building_center: Tuple[float, float, float],
    num_frames: int = 36,
    distance: float = 100.0
) -> go.Figure:
    """
    Erstellt eine 360°-Rotation-Animation um das Gebäude.
    
    Args:
        fig: Plotly Figure
        building_center: Mittelpunkt des Gebäudes
        num_frames: Anzahl der Frames (36 = 10° pro Frame)
        distance: Entfernung der Kamera vom Gebäude
        
    Returns:
        Figure mit Rotation-Animation
    """
    frames = []
    
    for i in range(num_frames):
        angle = (i / num_frames) * 360
        angle_rad = np.radians(angle)
        
        # Kamera-Position berechnen
        camera_x = building_center[0] + distance * np.cos(angle_rad)
        camera_y = building_center[1] + distance * np.sin(angle_rad)
        camera_z = building_center[2] + distance * 0.5
        
        # Camera-Einstellungen für diesen Frame
        camera = dict(
            eye=dict(
                x=(camera_x - building_center[0]) / distance,
                y=(camera_y - building_center[1]) / distance,
                z=(camera_z - building_center[2]) / distance
            ),
            center=dict(
                x=building_center[0] / distance,
                y=building_center[1] / distance,
                z=building_center[2] / distance
            ),
            up=dict(x=0, y=0, z=1)
        )
        
        frames.append(go.Frame(
            layout=dict(scene=dict(camera=camera)),
            name=str(i)
        ))
    
    fig.frames = frames
    
    # Animation-Controls
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'y': 1.0,
            'x': 1.15,
            'buttons': [
                {
                    'label': '🔄 360° Rotation',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                },
                {
                    'label': '⏹ Stop',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate'
                    }]
                }
            ]
        }]
    )
    
    return fig


def create_seasonal_shadow_animation(
    fig: go.Figure,
    building_dims: Any,
    num_seasons: int = 4
) -> go.Figure:
    """
    Erstellt eine Animation der Verschattung über verschiedene Jahreszeiten.
    
    Args:
        fig: Plotly Figure
        building_dims: BuildingDims-Objekt
        num_seasons: Anzahl der Jahreszeiten (default: 4)
        
    Returns:
        Figure mit Schatten-Animation
    """
    seasons = ['Winter', 'Frühling', 'Sommer', 'Herbst']
    sun_angles = [15, 35, 65, 35]  # Sonnenhöhen-Winkel für Jahreszeiten
    
    frames = []
    
    for i in range(num_seasons):
        season_name = seasons[i]
        sun_angle = sun_angles[i]
        
        # Schatten-Projektion berechnen
        shadow_offset_x = 20 * np.cos(np.radians(sun_angle))
        shadow_offset_y = 20 * np.sin(np.radians(sun_angle))
        
        # Schatten als halbtransparente Fläche
        # FIX: BuildingDims verwendet width_m und length_m, nicht width/depth
        shadow_trace = go.Mesh3d(
            x=[0, building_dims.width_m, building_dims.width_m, 0],
            y=[shadow_offset_y, shadow_offset_y, 
               building_dims.length_m + shadow_offset_y, 
               building_dims.length_m + shadow_offset_y],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='black',
            opacity=0.3,
            name=f'{season_name}-Schatten',
            showlegend=True
        )
        
        frames.append(go.Frame(
            data=[shadow_trace],
            name=season_name,
            layout=dict(
                title=dict(text=f'Verschattung im {season_name} (Sonnenwinkel: {sun_angle}°)')
            )
        ))
    
    fig.frames = frames
    
    # Jahreszeiten-Buttons
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'direction': 'left',
            'buttons': [
                {
                    'label': season,
                    'method': 'animate',
                    'args': [[season], {
                        'frame': {'duration': 500, 'redraw': True},
                        'mode': 'immediate'
                    }]
                }
                for season in seasons
            ],
            'x': 0.1,
            'y': 1.15
        }]
    )
    
    return fig


def create_energy_yield_timelapse(
    fig: go.Figure,
    modules_data: List[Dict],
    hours: int = 12
) -> go.Figure:
    """
    Erstellt eine Zeitraffer-Animation der Energieerträge über den Tag.
    
    Args:
        fig: Plotly Figure
        modules_data: Liste mit Modul-Daten inkl. Position und Ertrag
        hours: Anzahl Stunden für Simulation
        
    Returns:
        Figure mit Ertrags-Animation
    """
    frames = []
    
    for hour in range(hours):
        # Ertrags-Faktor basierend auf Tageszeit (Peak um Mittag)
        yield_factor = np.sin((hour / hours) * np.pi)
        
        # Module mit Farbe basierend auf aktuellem Ertrag
        module_traces = []
        
        for module in modules_data:
            current_yield = module.get('max_yield', 400) * yield_factor
            
            # Farbe von dunkel (wenig Ertrag) zu hell (viel Ertrag)
            color_intensity = int(255 * yield_factor)
            color = f'rgb(255, {color_intensity}, 0)'  # Orange-Gradient
            
            module_trace = go.Scatter3d(
                x=[module['x']],
                y=[module['y']],
                z=[module['z']],
                mode='markers',
                marker=dict(
                    size=10,
                    color=color,
                    opacity=0.8
                ),
                text=f'{current_yield:.0f} W',
                showlegend=False
            )
            module_traces.append(module_trace)
        
        frames.append(go.Frame(
            data=module_traces,
            name=f'{hour:02d}:00',
            layout=dict(
                title=dict(text=f'Energieertrag um {hour:02d}:00 Uhr')
            )
        ))
    
    fig.frames = frames
    
    # Zeitraffer-Controls
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {
                    'label': '⏩ Zeitraffer',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 200, 'redraw': True},
                        'fromcurrent': True
                    }]
                }
            ]
        }],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'args': [[f.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate'
                    }],
                    'label': f'{i:02d}:00',
                    'method': 'animate'
                }
                for i, f in enumerate(frames)
            ]
        }]
    )
    
    return fig


def _get_module_center_points(fig: go.Figure) -> List[Tuple[float, float, float]]:
    """
    Hilfsfunktion: Extrahiert Mittelpunkte aller Module aus der Figure.
    
    Args:
        fig: Plotly Figure mit Modulen
        
    Returns:
        Liste von (x, y, z) Tupeln
    """
    points = []
    
    for trace in fig.data:
        if hasattr(trace, 'x') and hasattr(trace, 'y') and hasattr(trace, 'z'):
            if len(trace.x) > 0:
                # Berechne Mittelpunkt
                center_x = np.mean(trace.x)
                center_y = np.mean(trace.y)
                center_z = np.mean(trace.z)
                points.append((center_x, center_y, center_z))
    
    return points


def render_animation_controls(animation_type: str = "sun_path") -> Dict[str, Any]:
    """
    Rendert Streamlit-UI-Controls für Animation-Einstellungen.
    
    Args:
        animation_type: Typ der Animation ('sun_path', 'rotation', 'shadow', 'yield')
        
    Returns:
        Dictionary mit Animations-Parametern
    """
    st.subheader("🎬 Animations-Einstellungen")
    
    params = {}
    
    if animation_type == "sun_path":
        params['num_frames'] = st.slider(
            "Anzahl Frames (Stunden)",
            min_value=12,
            max_value=48,
            value=24,
            step=6
        )
        params['radius'] = st.slider(
            "Sonnenbahn-Radius (m)",
            min_value=30.0,
            max_value=100.0,
            value=50.0,
            step=5.0
        )
    
    elif animation_type == "rotation":
        params['num_frames'] = st.slider(
            "Anzahl Frames",
            min_value=18,
            max_value=72,
            value=36,
            step=6
        )
        params['distance'] = st.slider(
            "Kamera-Distanz (m)",
            min_value=50.0,
            max_value=200.0,
            value=100.0,
            step=10.0
        )
    
    elif animation_type == "shadow":
        params['num_seasons'] = 4  # Fest: 4 Jahreszeiten
    
    elif animation_type == "yield":
        params['hours'] = st.slider(
            "Simulierte Stunden",
            min_value=6,
            max_value=24,
            value=12,
            step=1
        )
    
    return params
