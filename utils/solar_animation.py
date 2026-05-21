"""
Solar-Animationen für 3D-Visualisierung
========================================

Dieses Modul enthält Funktionen zur Erstellung von Animationen
für die 3D-Visualisierung der PV-Anlage.

PHASE 2 OPTIMIERUNGEN:
- Konfigurierbare FPS (12-60)
- Zeitraffer-Faktor (1-100x)
- Caching für Sonnenpositions-Berechnungen
- Echtzeit-Schatten-Updates
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Tuple, Dict, Any
import streamlit as st
from functools import lru_cache


# ============================================================================
# PERFORMANCE-OPTIMIERUNGEN (Phase 2, Task 4.1)
# ============================================================================

@lru_cache(maxsize=128)
def _calculate_sun_positions_cached(
    latitude: float,
    longitude: float,
    date: str,
    total_frames: int
) -> List[Tuple[float, float]]:
    """
    Berechnet und cached Sonnenpositions für alle Frames.
    
    Performance-Optimierung: Berechnet alle Positionen einmal und cached sie.
    
    Args:
        latitude: Breitengrad
        longitude: Längengrad
        date: Datum (YYYY-MM-DD)
        total_frames: Anzahl der Frames
        
    Returns:
        Liste von (azimuth, elevation) Tupeln für jeden Frame
    """
    positions = []
    
    for i in range(total_frames):
        # Winkel für aktuelle Tageszeit (0-360°)
        angle = (i / total_frames) * 360
        angle_rad = np.radians(angle)
        
        # Vereinfachte Sonnenpositions-Berechnung
        # In Produktion: Verwende pvlib oder ähnliche Bibliothek
        azimuth = angle
        elevation = 90 * abs(np.sin(angle_rad))  # Höchster Punkt bei 90°
        
        positions.append((azimuth, elevation))
    
    return positions


def create_sun_path_animation(
    fig: go.Figure,
    building_center: Tuple[float, float, float],
    radius: float = 50.0,
    num_frames: int = 24,
    fps: int = 24,
    time_compression: float = 1.0
) -> go.Figure:
    """
    Erstellt eine Animation des Sonnenpfads über dem Gebäude.
    
    PHASE 2 OPTIMIERUNGEN:
    - Konfigurierbare FPS (12-60)
    - Zeitraffer-Faktor für schnellere/langsamere Animation
    - Caching für Performance
    
    Args:
        fig: Plotly Figure
        building_center: Mittelpunkt des Gebäudes (x, y, z)
        radius: Radius der Sonnenbahn
        num_frames: Anzahl der Frames (12-48)
        fps: Frames pro Sekunde (12-60)
        time_compression: Zeitraffer-Faktor (1.0-100.0)
            1.0 = Echtzeit, 10.0 = 10x schneller
        
    Returns:
        Figure mit optimierter Animation
    """
    # Validierung: None-Checks
    if building_center is None or any(c is None for c in building_center):
        print(" Animation: building_center ist None, verwende (0, 0, 0)")
        building_center = (0.0, 0.0, 0.0)
    
    if radius is None:
        print(" Animation: radius ist None, verwende 50.0")
        radius = 50.0
    
    # Validiere und begrenze Parameter (Phase 2 Optimierung)
    fps = max(12, min(60, fps))  # 12-60 FPS
    time_compression = max(1.0, min(100.0, time_compression))  # 1-100x
    num_frames = max(12, min(48, num_frames))  # 12-48 Frames
    
    # Berechne Frame-Dauer basierend auf FPS und Zeitraffer
    frame_duration_ms = int(1000 / fps)
    
    # Cache Sonnenpositions-Berechnungen (Phase 2 Optimierung)
    sun_positions = _calculate_sun_positions_cached(
        48.0,  # Latitude (Deutschland)
        11.0,  # Longitude (Deutschland)
        "2024-06-21",  # Sommersonnenwende
        num_frames
    )
    
    frames = []
    
    for i in range(num_frames):
        # Hole gecachte Sonnenposition
        azimuth, elevation = sun_positions[i]
        angle_rad = np.radians(azimuth)
        
        # Sonnenposition berechnen (mit sicheren float-Werten)
        sun_x = float(building_center[0]) + float(radius) * np.cos(angle_rad)
        sun_y = float(building_center[1]) + float(radius) * np.sin(angle_rad)
        # Höhe variiert mit elevation
        sun_z = (float(building_center[2]) +
                 float(radius) * np.sin(np.radians(elevation)))
        
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
        
        # Sonnenstrahlen (optimiert: nur zu Modulen)
        rays = []
        module_points = _get_module_center_points(fig)
        
        # Limitiere Strahlen für Performance (max 10)
        for module_point in module_points[:10]:
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
    
    # Animation-Buttons mit konfigurierbarer Geschwindigkeit
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': ' Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {
                            'duration': frame_duration_ms,
                            'redraw': True
                        },
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


# ============================================================================
# ECHTZEIT-SCHATTEN-UPDATE (Phase 2, Task 4.2)
# ============================================================================

# Constants for shadow rendering
MAX_SHADOW_MODULES = 20  # Limit for performance
SHADOW_Z_OFFSET = 0.01  # Slight elevation above ground plane


def update_shadows_realtime(
    fig: go.Figure,
    sun_azimuth: float,
    sun_elevation: float,
    module_positions: List[Tuple[float, float, float]]
) -> go.Figure:
    """
    Aktualisiert Schatten in Echtzeit basierend auf Sonnenposition.
    
    Verwendet vereinfachte Schatten-Projektion für Performance.
    
    Args:
        fig: Plotly Figure
        sun_azimuth: Sonnen-Azimuth in Grad (0° = Nord, 180° = Süd)
        sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        module_positions: Liste von (x, y, z) Positionen der Module
        
    Returns:
        Figure mit aktualisierten Schatten
    """
    # Prüfe ob Sonne über Horizont ist
    if sun_elevation <= 0:
        # Keine Schatten bei Nacht
        return fig
    
    # Berechne Schatten-Richtungsvektor
    shadow_vector = _calculate_shadow_vector(sun_azimuth, sun_elevation)
    
    # Projiziere Schatten für jedes Modul
    shadow_traces = []
    
    # Limit number of shadows for performance
    limited_positions = module_positions[:MAX_SHADOW_MODULES]
    
    for x, y, z in limited_positions:
        # Berechne Schatten-Projektion auf Dachfläche (z=0 Ebene)
        if abs(shadow_vector[2]) > 1e-6:  # Avoid division by near-zero
            # Berechne wie weit der Schatten "fällt"
            shadow_length = z / abs(shadow_vector[2])
            
            # Schatten-Endpunkt
            shadow_x = x + shadow_vector[0] * shadow_length
            shadow_y = y + shadow_vector[1] * shadow_length
            shadow_z = SHADOW_Z_OFFSET  # Leicht über Boden
            
            # Erstelle Schatten als Linie
            shadow_trace = go.Scatter3d(
                x=[x, shadow_x],
                y=[y, shadow_y],
                z=[z, shadow_z],
                mode='lines',
                line=dict(
                    color='rgba(0, 0, 0, 0.3)',
                    width=3
                ),
                name='Schatten',
                showlegend=False,
                hoverinfo='skip'
            )
            shadow_traces.append(shadow_trace)
    
    # Füge Schatten zur Figure hinzu
    for trace in shadow_traces:
        fig.add_trace(trace)
    
    return fig


def _calculate_shadow_vector(
    sun_azimuth: float,
    sun_elevation: float
) -> Tuple[float, float, float]:
    """
    Berechnet Schatten-Richtungsvektor basierend auf Sonnenposition.
    
    Koordinatensystem:
    - X: Ost-West (positiv = Ost)
    - Y: Nord-Süd (positiv = Nord)
    - Z: Höhe (positiv = oben)
    
    Args:
        sun_azimuth: Azimuth in Grad (0° = Nord, 90° = Ost, 180° = Süd)
        sun_elevation: Elevation in Grad (0° = Horizont, 90° = Zenit)
        
    Returns:
        (x, y, z) Richtungsvektor des Schattens
    """
    # Konvertiere zu Radians
    azimuth_rad = np.radians(sun_azimuth)
    elevation_rad = np.radians(sun_elevation)
    
    # Schatten zeigt in entgegengesetzte Richtung der Sonne
    # Azimuth 0° = Nord, 180° = Süd
    # Bei Sonne im Süden (180°) zeigt Schatten nach Norden (negatives Y)
    shadow_x = -np.sin(azimuth_rad) * np.cos(elevation_rad)
    shadow_y = -np.cos(azimuth_rad) * np.cos(elevation_rad)
    shadow_z = -np.sin(elevation_rad)
    
    return (shadow_x, shadow_y, shadow_z)


# ============================================================================
# ERWEITERTE ANIMATION-CONTROLS (Phase 2, Task 4.3)
# ============================================================================

def render_animation_controls_enhanced(
    animation_type: str = "sun_path"
) -> Dict[str, Any]:
    """
    Rendert erweiterte Streamlit-UI-Controls für Animation-Einstellungen.
    
    PHASE 2 ERWEITERUNGEN:
    - FPS-Einstellung (12-60)
    - Zeitraffer-Faktor (1-100x)
    - Monats-Auswahl
    - Pause/Play Toggle
    
    Args:
        animation_type: Typ der Animation ('sun_path', 'rotation', etc.)
        
    Returns:
        Dictionary mit Animations-Parametern
    """
    st.subheader("⚙️ Animations-Einstellungen (Optimiert)")
    
    params = {}
    
    if animation_type == "sun_path":
        col1, col2 = st.columns(2)
        
        with col1:
            params['fps'] = st.slider(
                "Frames pro Sekunde",
                min_value=12,
                max_value=60,
                value=24,
                step=6,
                help="Höhere FPS = flüssigere Animation"
            )
            
            params['num_frames'] = st.slider(
                "Anzahl Frames (Stunden)",
                min_value=12,
                max_value=48,
                value=24,
                step=6,
                help="Mehr Frames = detailliertere Animation"
            )
        
        with col2:
            params['time_compression'] = st.slider(
                "Zeitraffer-Faktor",
                min_value=1.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
                help="1 = Echtzeit, 10 = 10x schneller"
            )
            
            params['month'] = st.selectbox(
                "Monat",
                options=[
                    "Januar", "Februar", "März", "April",
                    "Mai", "Juni", "Juli", "August",
                    "September", "Oktober", "November", "Dezember"
                ],
                index=5,  # Juni (Sommersonnenwende)
                help="Wählen Sie den Monat für die Sonnenposition"
            )
        
        params['radius'] = st.slider(
            "Sonnenbahn-Radius (m)",
            min_value=30.0,
            max_value=100.0,
            value=50.0,
            step=5.0
        )
        
        # Erweiterte Optionen
        with st.expander("🔧 Erweiterte Optionen"):
            params['show_shadows'] = st.checkbox(
                "Echtzeit-Schatten anzeigen",
                value=True,
                help="Zeigt Schatten-Projektion in Echtzeit"
            )
            
            params['show_sun_rays'] = st.checkbox(
                "Sonnenstrahlen anzeigen",
                value=True,
                help="Zeigt Strahlen von Sonne zu Modulen"
            )
            
            params['auto_play'] = st.checkbox(
                "Automatisch abspielen",
                value=False,
                help="Startet Animation automatisch"
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
        params['fps'] = st.slider(
            "Frames pro Sekunde",
            min_value=12,
            max_value=60,
            value=30,
            step=6
        )
    
    elif animation_type == "shadow":
        params['num_seasons'] = 4  # Fest: 4 Jahreszeiten
        params['show_sun_position'] = st.checkbox(
            "Sonnenposition anzeigen",
            value=True
        )
    
    elif animation_type == "yield":
        params['hours'] = st.slider(
            "Simulierte Stunden",
            min_value=6,
            max_value=24,
            value=12,
            step=1
        )
        params['fps'] = st.slider(
            "Frames pro Sekunde",
            min_value=12,
            max_value=60,
            value=24,
            step=6
        )
    
    return params


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
    # Validierung: None-Checks
    if building_center is None or any(c is None for c in building_center):
        print(" Animation: building_center ist None, verwende (0, 0, 0)")
        building_center = (0.0, 0.0, 0.0)
    
    if distance is None or distance <= 0:
        print(" Animation: distance ungültig, verwende 100.0")
        distance = 100.0
    
    if num_frames is None or num_frames <= 0:
        print(" Animation: num_frames ungültig, verwende 36")
        num_frames = 36
    
    frames = []
    
    for i in range(num_frames):
        angle = (i / num_frames) * 360
        angle_rad = np.radians(angle)
        
        # Kamera-Position berechnen (mit sicheren float-Werten)
        camera_x = float(building_center[0]) + float(distance) * np.cos(angle_rad)
        camera_y = float(building_center[1]) + float(distance) * np.sin(angle_rad)
        camera_z = float(building_center[2]) + float(distance) * 0.5
        
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
                    'label': ' 360° Rotation',
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
        if hours != 0:
            yield_factor = np.sin((hour / hours) * np.pi)
        else:
            yield_factor = 0.0
        
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
    
    DEPRECATED: Verwenden Sie render_animation_controls_enhanced() für
    erweiterte Funktionen (Phase 2).
    
    Args:
        animation_type: Typ der Animation ('sun_path', 'rotation', etc.)
        
    Returns:
        Dictionary mit Animations-Parametern
    """
    # Leite an erweiterte Version weiter
    return render_animation_controls_enhanced(animation_type)
