"""
3D PV-Visualisierung Analyse-Modul

Dieses Modul enthält alle Analyse-Funktionen für die 3D-Visualisierung:
- Optimierungs-Assistent
- Verschattungs-Analyse
- Ertrags-Heatmap
- Sonnenverlauf-Berechnung
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

try:
    import numpy as np
except ImportError:
    np = None

from utils.pv3d import (
    BuildingDims,
    AdvancedLayoutConfig,
    ModuleTransform,
    ModuleGroup,
    PV_W,
    PV_H,
    _deg_to_rad
)
from utils.pv3d_performance import cached, monitor_performance


# ============================================================================
# SONNENVERLAUF-BERECHNUNG
# ============================================================================

@cached(ttl=300.0)  # Cache für 5 Minuten
@monitor_performance("sun_position_calculation")
def calculate_sun_position_for_time(
    latitude: float,
    day_of_year: int,
    hour: float
) -> Tuple[float, float]:
    """
    Berechnet die Sonnenposition (Azimuth und Elevation) für einen gegebenen
    Standort, Tag und Uhrzeit.
    
    Diese Funktion verwendet eine vereinfachte astronomische Berechnung
    basierend auf der Sonnendeklination und dem Stundenwinkel.
    
    Args:
        latitude: Breitengrad des Standorts in Grad (z.B. 51.0 für Deutschland)
                 Positiv für nördliche Breite, negativ für südliche Breite
        day_of_year: Tag im Jahr (1-365, wobei 1 = 1. Januar)
        hour: Stunde des Tages (0.0-24.0, z.B. 12.5 für 12:30 Uhr)
    
    Returns:
        Tuple mit (azimuth_deg, elevation_deg):
        - azimuth_deg: Azimuth-Winkel in Grad (0° = Norden, 90° = Osten,
                      180° = Süden, 270° = Westen)
        - elevation_deg: Elevations-Winkel in Grad (0° = Horizont,
                        90° = Zenit, negative Werte = unter Horizont)
    
    Example:
        >>> # Mittag am 21. Juni (Sommersonnenwende) in Deutschland
        >>> azimuth, elevation = calculate_sun_position_for_time(51.0, 172, 12.0)
        >>> print(f"Azimuth: {azimuth:.1f}°, Elevation: {elevation:.1f}°")
        Azimuth: 180.0°, Elevation: 62.0°
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    # Validiere Eingaben
    latitude = max(-90.0, min(90.0, latitude))
    day_of_year = max(1, min(365, day_of_year))
    hour = max(0.0, min(24.0, hour))
    
    # Berechne Sonnendeklination (Winkel zwischen Sonnenstrahlen und Äquatorebene)
    # Vereinfachte Formel nach Cooper (1969)
    declination_rad = _deg_to_rad(23.45) * math.sin(
        _deg_to_rad(360.0 * (284 + day_of_year) / 365.0)
    )
    
    # Berechne Stundenwinkel (0° um 12:00 Uhr Ortszeit, 15° pro Stunde)
    hour_angle_deg = 15.0 * (hour - 12.0)
    hour_angle_rad = _deg_to_rad(hour_angle_deg)
    
    # Berechne Sonnen-Elevation (Höhenwinkel)
    latitude_rad = _deg_to_rad(latitude)
    
    sin_elevation = (
        math.sin(latitude_rad) * math.sin(declination_rad) +
        math.cos(latitude_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
    )
    
    # Begrenze auf [-1, 1] um numerische Fehler zu vermeiden
    sin_elevation = max(-1.0, min(1.0, sin_elevation))
    
    elevation_rad = math.asin(sin_elevation)
    elevation_deg = math.degrees(elevation_rad)
    
    # Berechne Sonnen-Azimuth (Himmelsrichtung)
    cos_elevation = math.cos(elevation_rad)
    
    # Vermeide Division durch Null
    if abs(cos_elevation) < 0.001 or abs(math.cos(latitude_rad)) < 0.001:
        # Sonne im Zenit oder an den Polen
        azimuth_deg = 180.0  # Konvention: Süden
    else:
        cos_azimuth = (
            (math.sin(declination_rad) - math.sin(elevation_rad) * math.sin(latitude_rad)) /
            (cos_elevation * math.cos(latitude_rad))
        )
        
        # Begrenze auf [-1, 1]
        cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
        
        azimuth_rad = math.acos(cos_azimuth)
        azimuth_deg = math.degrees(azimuth_rad)
        
        # Korrigiere Azimuth basierend auf Stundenwinkel
        # Wenn Stundenwinkel positiv (Nachmittag), ist Azimuth > 180°
        if hour_angle_deg > 0:
            azimuth_deg = 360.0 - azimuth_deg
    
    return (azimuth_deg, elevation_deg)


# ============================================================================
# VERSCHATTUNGS-ANALYSE
# ============================================================================

@cached(ttl=60.0)  # Cache für 1 Minute
@monitor_performance("shading_analysis")
def calculate_shading_analysis(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    sun_azimuth: float,
    sun_elevation: float,
    building_dims: BuildingDims
) -> Dict[int, float]:
    """
    Berechnet den Verschattungsgrad für alle Module basierend auf Sonnenposition.
    
    Diese Funktion verwendet eine vereinfachte Verschattungsberechnung basierend
    auf der relativen Position der Module zueinander und der Sonnenrichtung.
    
    Args:
        module_positions: Liste von (x, y, z) Positionen für alle Module
        module_transforms: Dictionary mit ModuleTransform-Objekten (Key: Index)
        sun_azimuth: Sonnen-Azimuth in Grad (0° = Norden, 180° = Süden)
        sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        building_dims: Gebäudedimensionen für Kontext
    
    Returns:
        Dictionary mit Verschattungsgrad pro Modul (Key: Index, Value: Prozent 0-100)
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0), (4.0, 0.0, 6.0)]
        >>> transforms = {i: ModuleTransform(index=i) for i in range(3)}
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> shading = calculate_shading_analysis(positions, transforms, 180.0, 45.0, dims)
        >>> len(shading)
        3
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    shading_values = {}
    
    # Prüfe ob Sonne über dem Horizont ist
    if sun_elevation <= 0.0:
        # Sonne unter Horizont -> vollständige Verschattung (Nacht)
        return {i: 100.0 for i in range(len(module_positions))}
    
    # Konvertiere Sonnenposition zu Richtungsvektor
    azimuth_rad = _deg_to_rad(sun_azimuth)
    elevation_rad = _deg_to_rad(sun_elevation)
    
    sun_direction = np.array([
        math.sin(azimuth_rad) * math.cos(elevation_rad),  # X (Ost-West)
        math.cos(azimuth_rad) * math.cos(elevation_rad),  # Y (Nord-Süd)
        math.sin(elevation_rad)                            # Z (Höhe)
    ])
    
    # Berechne Verschattung für jedes Modul
    for i, pos_i in enumerate(module_positions):
        pos_i_array = np.array(pos_i)
        
        # Hole Transform für Modul i
        transform_i = module_transforms.get(i, ModuleTransform(index=i))
        
        # Berechne Modul-Normale (Richtung in die das Modul zeigt)
        azimuth_i_rad = _deg_to_rad(transform_i.azimuth_deg)
        tilt_i_rad = _deg_to_rad(transform_i.tilt_deg)
        
        # Modul-Normale in kartesischen Koordinaten
        module_normal = np.array([
            math.sin(azimuth_i_rad) * math.sin(tilt_i_rad),
            math.cos(azimuth_i_rad) * math.sin(tilt_i_rad),
            math.cos(tilt_i_rad)
        ])
        
        # Berechne Winkel zwischen Modul-Normale und Sonnenrichtung
        dot_product = np.dot(module_normal, sun_direction)
        
        # Wenn Modul von Sonne abgewandt ist, ist es verschattet
        if dot_product <= 0:
            shading_values[i] = 100.0
            continue
        
        # Prüfe Verschattung durch andere Module
        shading_factor = 0.0
        
        for j, pos_j in enumerate(module_positions):
            if i == j:
                continue
            
            pos_j_array = np.array(pos_j)
            
            # Vektor von Modul i zu Modul j
            vec_ij = pos_j_array - pos_i_array
            distance_ij = np.linalg.norm(vec_ij)
            
            if distance_ij < 0.1:  # Zu nah, ignorieren
                continue
            
            # Normalisiere Vektor
            if distance_ij != 0:
                vec_ij_norm = vec_ij / distance_ij
            else:
                vec_ij_norm = 0.0
            
            # Prüfe ob Modul j in Richtung der Sonne liegt
            # (d.h. ob der Vektor von i zu j ähnlich zur Sonnenrichtung ist)
            dot_sun = np.dot(vec_ij_norm, sun_direction)
            
            if dot_sun > 0.7:  # Modul j liegt in Sonnenrichtung
                # Berechne Verschattungsfaktor basierend auf Distanz und Winkel
                # Näher = mehr Verschattung
                distance_factor = max(0.0, 1.0 - distance_ij / 10.0)
                angle_factor = dot_sun
                
                shading_contribution = distance_factor * angle_factor * 30.0
                shading_factor += shading_contribution
        
        # Begrenze Verschattung auf 0-100%
        shading_values[i] = min(100.0, max(0.0, shading_factor))
    
    return shading_values


# ============================================================================
# ERWEITERTE VERSCHATTUNGS-ANALYSE (Task 5.1)
# ============================================================================

@cached(ttl=60.0)
@monitor_performance("shading_analysis_enhanced")
def calculate_shading_analysis_enhanced(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    sun_azimuth: float,
    sun_elevation: float,
    building_dims: BuildingDims,
    include_indirect: bool = True
) -> Dict[str, Any]:
    """
    Erweiterte Verschattungs-Analyse mit direkter/indirekter Unterscheidung.
    
    Diese Funktion unterscheidet zwischen:
    - Direkter Verschattung: Objekte blockieren direktes Sonnenlicht
    - Indirekter Verschattung: Reduzierte diffuse Strahlung durch Umgebung
    
    Args:
        module_positions: Liste von (x, y, z) Positionen für alle Module
        module_transforms: Dictionary mit ModuleTransform-Objekten
        sun_azimuth: Sonnen-Azimuth in Grad (0° = Norden, 180° = Süden)
        sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        building_dims: Gebäudedimensionen für Kontext
        include_indirect: Ob indirekte Verschattung berechnet werden soll
    
    Returns:
        Dictionary mit:
            "direct_shading": List[float] - Direkte Verschattung (0-1)
            "indirect_shading": List[float] - Indirekte Verschattung (0-1)
            "total_shading": List[float] - Kombinierte Verschattung (0-1)
            "shading_sources": List[str] - Verschattungsquellen
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> transforms = {i: ModuleTransform(index=i) for i in range(2)}
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> result = calculate_shading_analysis_enhanced(
        ...     positions, transforms, 180.0, 45.0, dims
        ... )
        >>> len(result["direct_shading"])
        2
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    results = {
        "direct_shading": [],
        "indirect_shading": [],
        "total_shading": [],
        "shading_sources": []
    }
    
    # Prüfe ob Sonne über dem Horizont ist
    if sun_elevation <= 0.0:
        # Sonne unter Horizont -> vollständige Verschattung (Nacht)
        n = len(module_positions)
        return {
            "direct_shading": [1.0] * n,
            "indirect_shading": [0.0] * n,
            "total_shading": [1.0] * n,
            "shading_sources": ["night"] * n
        }
    
    # Konvertiere Sonnenposition zu Richtungsvektor
    azimuth_rad = _deg_to_rad(sun_azimuth)
    elevation_rad = _deg_to_rad(sun_elevation)
    
    sun_direction = np.array([
        math.sin(azimuth_rad) * math.cos(elevation_rad),
        math.cos(azimuth_rad) * math.cos(elevation_rad),
        math.sin(elevation_rad)
    ])
    
    # Berechne Verschattung für jedes Modul
    for i, pos_i in enumerate(module_positions):
        pos_i_array = np.array(pos_i)
        
        # Hole Transform für Modul i
        transform_i = module_transforms.get(i, ModuleTransform(index=i))
        
        # Berechne Modul-Normale
        azimuth_i_rad = _deg_to_rad(transform_i.azimuth_deg)
        tilt_i_rad = _deg_to_rad(transform_i.tilt_deg)
        
        module_normal = np.array([
            math.sin(azimuth_i_rad) * math.sin(tilt_i_rad),
            math.cos(azimuth_i_rad) * math.sin(tilt_i_rad),
            math.cos(tilt_i_rad)
        ])
        
        # Berechne Winkel zwischen Modul-Normale und Sonnenrichtung
        dot_product = np.dot(module_normal, sun_direction)
        
        # Wenn Modul von Sonne abgewandt ist, ist es direkt verschattet
        if dot_product <= 0:
            results["direct_shading"].append(1.0)
            results["indirect_shading"].append(0.0)
            results["total_shading"].append(1.0)
            results["shading_sources"].append("self_orientation")
            continue
        
        # === DIREKTE VERSCHATTUNG ===
        direct_shading = 0.0
        shading_source = "none"
        
        for j, pos_j in enumerate(module_positions):
            if i == j:
                continue
            
            pos_j_array = np.array(pos_j)
            
            # Vektor von Modul i zu Modul j
            vec_ij = pos_j_array - pos_i_array
            distance_ij = np.linalg.norm(vec_ij)
            
            if distance_ij < 0.1:
                continue
            
            # Normalisiere Vektor
            vec_ij_norm = vec_ij / distance_ij
            
            # Prüfe ob Modul j in Richtung der Sonne liegt
            dot_sun = np.dot(vec_ij_norm, sun_direction)
            
            if dot_sun > 0.7:  # Modul j liegt in Sonnenrichtung
                # Berechne Verschattungsfaktor
                distance_factor = max(0.0, 1.0 - distance_ij / 10.0)
                angle_factor = dot_sun
                
                shading_contribution = distance_factor * angle_factor * 0.3
                direct_shading += shading_contribution
                
                if shading_contribution > 0.1:
                    shading_source = "module"
        
        # Begrenze direkte Verschattung auf 0-1
        direct_shading = min(1.0, max(0.0, direct_shading))
        
        # === INDIREKTE VERSCHATTUNG ===
        indirect_shading = 0.0
        
        if include_indirect:
            # Berechne indirekte Verschattung basierend auf Umgebung
            # Faktoren: Höhe, Position, umgebende Module
            
            # Höhenfaktor: Niedrigere Module haben mehr indirekte Verschattung
            z_pos = pos_i[2]
            max_z = max([p[2] for p in module_positions]) if module_positions else z_pos
            if max_z > 0:
                height_factor = 1.0 - (z_pos / max_z)
            else:
                height_factor = 0.0
            
            # Dichte-Faktor: Mehr umgebende Module = mehr indirekte Verschattung
            nearby_modules = 0
            for j, pos_j in enumerate(module_positions):
                if i == j:
                    continue
                distance = np.linalg.norm(np.array(pos_j) - pos_i_array)
                if distance < 3.0:  # Innerhalb 3m
                    nearby_modules += 1
            
            density_factor = min(1.0, nearby_modules / 10.0)
            
            # Kombiniere Faktoren
            indirect_shading = (height_factor * 0.5 + density_factor * 0.5) * 0.3
            
            # Indirekte Verschattung ist weniger stark als direkte
            indirect_shading = min(0.3, indirect_shading)
        
        # === KOMBINIERTE VERSCHATTUNG ===
        # Indirekte Verschattung hat weniger Einfluss (30%)
        total_shading = min(1.0, direct_shading + indirect_shading * 0.3)
        
        results["direct_shading"].append(direct_shading)
        results["indirect_shading"].append(indirect_shading)
        results["total_shading"].append(total_shading)
        results["shading_sources"].append(shading_source)
    
    return results


def _identify_shading_source(
    module_index: int,
    direct_shading: float
) -> str:
    """
    Identifiziert die Quelle der Verschattung.
    
    Args:
        module_index: Index des Moduls
        direct_shading: Direkte Verschattung (0-1)
    
    Returns:
        String mit Verschattungsquelle: "none", "module", "building", "environment"
    """
    if direct_shading < 0.1:
        return "none"
    elif direct_shading < 0.5:
        return "module"
    else:
        return "building"


# ============================================================================
# NACHBARGEBÄUDE-INTEGRATION (Task 5.2)
# ============================================================================

def add_neighboring_buildings(
    building_positions: List[Dict[str, Any]]
) -> None:
    """
    Fügt Nachbargebäude zur Verschattungs-Analyse hinzu.
    
    Diese Funktion speichert Nachbargebäude in Session State für spätere
    Verwendung in der Verschattungsberechnung.
    
    Args:
        building_positions: Liste von Gebäuden mit:
            - x, y: Position relativ zum Hauptgebäude (in Metern)
            - width, length, height: Dimensionen (in Metern)
            - roof_type: Dachform (optional)
    
    Example:
        >>> buildings = [
        ...     {"x": 15.0, "y": 0.0, "width": 10.0, "length": 8.0, "height": 8.0},
        ...     {"x": -15.0, "y": 5.0, "width": 12.0, "length": 10.0, "height": 10.0}
        ... ]
        >>> add_neighboring_buildings(buildings)
    """
    try:
        import streamlit as st
        
        if "neighboring_buildings" not in st.session_state:
            st.session_state["neighboring_buildings"] = []
        
        st.session_state["neighboring_buildings"].extend(building_positions)
    except ImportError:
        # Streamlit nicht verfügbar (z.B. in Tests)
        # Verwende globale Variable als Fallback
        global _neighboring_buildings_cache
        if "_neighboring_buildings_cache" not in globals():
            _neighboring_buildings_cache = []
        _neighboring_buildings_cache.extend(building_positions)


def get_neighboring_buildings() -> List[Dict[str, Any]]:
    """
    Holt gespeicherte Nachbargebäude aus Session State.
    
    Returns:
        Liste von Nachbargebäuden
    """
    try:
        import streamlit as st
        return st.session_state.get("neighboring_buildings", [])
    except ImportError:
        # Fallback für Tests
        return globals().get("_neighboring_buildings_cache", [])


def clear_neighboring_buildings() -> None:
    """Löscht alle gespeicherten Nachbargebäude."""
    try:
        import streamlit as st
        st.session_state["neighboring_buildings"] = []
    except ImportError:
        global _neighboring_buildings_cache
        _neighboring_buildings_cache = []


def calculate_building_shadow(
    building: Dict[str, Any],
    sun_azimuth: float,
    sun_elevation: float
) -> List[Tuple[float, float]]:
    """
    Berechnet den Schatten eines Nachbargebäudes.
    
    Args:
        building: Dictionary mit x, y, width, length, height
        sun_azimuth: Sonnen-Azimuth in Grad
        sun_elevation: Sonnen-Elevation in Grad
    
    Returns:
        Liste von (x, y) Punkten die das Schatten-Polygon definieren
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    if sun_elevation <= 0:
        return []  # Keine Schatten bei Nacht
    
    # Berechne Schattenlänge
    shadow_length = building["height"] / math.tan(_deg_to_rad(sun_elevation))
    
    # Berechne Schattenrichtung
    azimuth_rad = _deg_to_rad(sun_azimuth)
    shadow_direction = np.array([
        math.sin(azimuth_rad),
        math.cos(azimuth_rad)
    ])
    
    # Gebäude-Ecken
    x, y = building["x"], building["y"]
    w, l = building["width"], building["length"]
    
    corners = np.array([
        [x - w/2, y - l/2],
        [x + w/2, y - l/2],
        [x + w/2, y + l/2],
        [x - w/2, y + l/2]
    ])
    
    # Projiziere Schatten
    shadow_offset = shadow_direction * shadow_length
    shadow_corners = corners + shadow_offset
    
    # Konvertiere zu Liste von Tupeln
    return [(float(p[0]), float(p[1])) for p in shadow_corners]


# ============================================================================
# VERSCHATTUNGS-VERLAUF DIAGRAMM (Task 5.3)
# ============================================================================

def create_shading_timeline_chart(
    module_index: int,
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    building_dims: BuildingDims,
    date: str = "2024-06-21",
    latitude: float = 51.0
):
    """
    Erstellt Verschattungs-Verlauf über den Tag als Diagramm.
    
    Diese Funktion berechnet die Verschattung für ein spezifisches Modul
    über den Tagesverlauf und erstellt ein Plotly-Diagramm.
    
    Args:
        module_index: Index des zu analysierenden Moduls
        module_positions: Liste aller Modulpositionen
        module_transforms: Dictionary mit ModuleTransform-Objekten
        building_dims: Gebäudedimensionen
        date: Datum im Format "YYYY-MM-DD"
        latitude: Breitengrad des Standorts
    
    Returns:
        Plotly Figure mit Verschattung (%) über Zeit (Stunden)
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> transforms = {i: ModuleTransform(index=i) for i in range(2)}
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> fig = create_shading_timeline_chart(0, positions, transforms, dims)
        >>> fig.data[0].name
        'Verschattung'
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise RuntimeError("Plotly ist nicht installiert")
    
    # Parse Datum um Tag des Jahres zu berechnen
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_year = date_obj.timetuple().tm_yday
    except Exception:
        # Fallback: Sommersonnenwende (21. Juni = Tag 172)
        day_of_year = 172
    
    # Berechne Verschattung für jede Stunde
    hours = list(range(6, 21))  # 6:00 - 20:00 Uhr
    shading_values = []
    
    for hour in hours:
        # Berechne Sonnenposition
        sun_azimuth, sun_elevation = calculate_sun_position_for_time(
            latitude, day_of_year, float(hour)
        )
        
        # Berechne Verschattung
        shading_result = calculate_shading_analysis_enhanced(
            module_positions,
            module_transforms,
            sun_azimuth,
            sun_elevation,
            building_dims,
            include_indirect=True
        )
        
        # Hole Verschattung für dieses Modul
        if module_index < len(shading_result["total_shading"]):
            shading = shading_result["total_shading"][module_index] * 100
        else:
            shading = 0.0
        
        shading_values.append(shading)
    
    # Erstelle Plotly Figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=shading_values,
        mode='lines+markers',
        name='Verschattung',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8, color='#e74c3c'),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.2)',
        hovertemplate='<b>%{x}:00 Uhr</b><br>Verschattung: %{y:.1f}%<extra></extra>'
    ))
    
    # Layout
    fig.update_layout(
        title=f"Verschattungs-Verlauf Modul #{module_index} ({date})",
        xaxis_title="Uhrzeit",
        yaxis_title="Verschattung (%)",
        yaxis_range=[0, 100],
        xaxis=dict(
            tickmode='linear',
            tick0=6,
            dtick=2,
            ticksuffix=':00'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


# ============================================================================
# OPTIMIERUNGSVORSCHLÄGE (Task 5.4)
# ============================================================================

def identify_heavily_shaded_modules(
    shading_result: Dict[str, Any],
    threshold_percent: float = 60.0
) -> List[int]:
    """
    Identifiziert stark verschattete Module (>60% Verschattung).
    
    Args:
        shading_result: Ergebnis von calculate_shading_analysis_enhanced()
        threshold_percent: Schwellwert für "stark verschattet" (Standard: 60%)
    
    Returns:
        Liste von Modul-Indizes mit starker Verschattung
    
    Example:
        >>> result = {
        ...     "total_shading": [0.2, 0.7, 0.3, 0.8],
        ...     "shading_sources": ["none", "module", "none", "building"]
        ... }
        >>> identify_heavily_shaded_modules(result, 60.0)
        [1, 3]
    """
    heavily_shaded = []
    
    for i, shading in enumerate(shading_result["total_shading"]):
        if shading * 100 > threshold_percent:
            heavily_shaded.append(i)
    
    return heavily_shaded


def generate_optimization_suggestions(
    heavily_shaded_modules: List[int],
    module_positions: List[Tuple[float, float, float]],
    shading_result: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generiert Optimierungsvorschläge für stark verschattete Module.
    
    Args:
        heavily_shaded_modules: Liste von Modul-Indizes mit starker Verschattung
        module_positions: Liste aller Modulpositionen
        shading_result: Ergebnis von calculate_shading_analysis_enhanced()
    
    Returns:
        Liste von Vorschlägen mit:
            - module_index: Index des Moduls
            - shading_percent: Verschattungsgrad in Prozent
            - issue: Beschreibung des Problems
            - suggestion: Optimierungsvorschlag
            - priority: Priorität ("high", "medium", "low")
    
    Example:
        >>> modules = [1, 3]
        >>> positions = [(0, 0, 6), (2, 0, 6), (4, 0, 6), (6, 0, 6)]
        >>> result = {
        ...     "total_shading": [0.2, 0.7, 0.3, 0.8],
        ...     "shading_sources": ["none", "module", "none", "building"],
        ...     "direct_shading": [0.1, 0.7, 0.2, 0.8]
        ... }
        >>> suggestions = generate_optimization_suggestions(modules, positions, result)
        >>> len(suggestions)
        2
    """
    suggestions = []
    
    for idx in heavily_shaded_modules:
        if idx >= len(module_positions):
            continue
        
        x, y, z = module_positions[idx]
        shading_percent = shading_result["total_shading"][idx] * 100
        shading_source = shading_result["shading_sources"][idx]
        direct_shading = shading_result["direct_shading"][idx]
        
        # Bestimme Problem und Vorschlag basierend auf Verschattungsquelle
        if shading_source == "module":
            issue = f"Verschattung durch andere Module ({shading_percent:.1f}%)"
            suggestion = "Modul an weniger dicht belegte Position verschieben oder Abstand zu Nachbarmodulen vergrößern"
            priority = "high" if shading_percent > 80 else "medium"
        
        elif shading_source == "building":
            issue = f"Verschattung durch Gebäude ({shading_percent:.1f}%)"
            suggestion = "Modul an höhere Position verschieben oder auf andere Dachseite platzieren"
            priority = "high"
        
        elif shading_source == "self_orientation":
            issue = f"Modul ist von Sonne abgewandt ({shading_percent:.1f}%)"
            suggestion = "Modul-Ausrichtung anpassen (Richtung Süden drehen)"
            priority = "high"
        
        else:
            issue = f"Hohe Verschattung ({shading_percent:.1f}%)"
            suggestion = "Position und Ausrichtung des Moduls überprüfen"
            priority = "medium" if shading_percent > 80 else "low"
        
        suggestions.append({
            "module_index": idx,
            "shading_percent": shading_percent,
            "issue": issue,
            "suggestion": suggestion,
            "priority": priority,
            "current_position": (x, y, z)
        })
    
    # Sortiere nach Priorität (high > medium > low) und Verschattungsgrad
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(
        key=lambda s: (priority_order[s["priority"]], -s["shading_percent"])
    )
    
    return suggestions


# ============================================================================
# ERTRAGS-HEATMAP
# ============================================================================

@cached(ttl=120.0)  # Cache für 2 Minuten
@monitor_performance("yield_heatmap")
def calculate_yield_heatmap(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    latitude: float,
    building_dims: BuildingDims
) -> Dict[int, float]:
    """
    Berechnet das Ertragspotential für alle Module basierend auf Ausrichtung
    und Neigung.
    
    Diese Funktion berechnet einen relativen Ertragswert für jedes Modul
    basierend auf:
    - Azimuth (Süd = optimal)
    - Neigung (30-35° = optimal für Deutschland)
    - Position (höher = weniger Verschattung)
    
    Args:
        module_positions: Liste von (x, y, z) Positionen für alle Module
        module_transforms: Dictionary mit ModuleTransform-Objekten (Key: Index)
        latitude: Breitengrad des Standorts
        building_dims: Gebäudedimensionen für Kontext
    
    Returns:
        Dictionary mit relativem Ertragspotential pro Modul (Key: Index, Value: 0-100)
        100 = optimales Ertragspotential, 0 = kein Ertrag
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> transforms = {
        ...     0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=30.0),
        ...     1: ModuleTransform(index=1, azimuth_deg=90.0, tilt_deg=15.0)
        ... }
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> yield_map = calculate_yield_heatmap(positions, transforms, 51.0, dims)
        >>> yield_map[0] > yield_map[1]  # Süd-Ausrichtung besser als Ost
        True
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    yield_values = {}
    
    # Optimale Werte für Deutschland (Breitengrad ~51°)
    optimal_azimuth = 0.0  # Süd
    optimal_tilt = 35.0    # Optimal für Jahresertrag
    
    # Passe optimale Neigung an Breitengrad an
    # Faustregel: optimale Neigung ≈ Breitengrad - 15°
    optimal_tilt = max(25.0, min(45.0, abs(latitude) - 15.0))
    
    for i, pos in enumerate(module_positions):
        # Hole Transform für Modul
        transform = module_transforms.get(i, ModuleTransform(index=i))
        
        # Berechne Azimuth-Faktor (Süd = 1.0, Nord = 0.0)
        # Verwende Cosinus-Funktion für sanften Übergang
        azimuth_diff = abs(transform.azimuth_deg - optimal_azimuth)
        if azimuth_diff > 180:
            azimuth_diff = 360 - azimuth_diff
        
        azimuth_factor = math.cos(_deg_to_rad(azimuth_diff))
        azimuth_factor = max(0.0, azimuth_factor)  # Negative Werte auf 0
        
        # Berechne Neigungs-Faktor (optimal_tilt = 1.0)
        # Verwende Gauss-Kurve für sanften Abfall
        tilt_diff = abs(transform.tilt_deg - optimal_tilt)
        tilt_factor = math.exp(-(tilt_diff ** 2) / (2 * 20 ** 2))  # Sigma = 20°
        
        # Berechne Höhen-Faktor (höher = besser, weniger Verschattung)
        # Normalisiere auf Gebäudehöhe
        z_pos = pos[2]
        max_z = building_dims.wall_height_m + 5.0  # Geschätzte max. Höhe
        if max_z != 0:
            height_factor = min(1.0, z_pos / max_z)
        else:
            height_factor = 0.0
        height_factor = 0.7 + 0.3 * height_factor  # Min 70%, Max 100%
        
        # Kombiniere Faktoren
        # Azimuth: 50% Gewicht
        # Neigung: 30% Gewicht
        # Höhe: 20% Gewicht
        total_yield = (
            azimuth_factor * 0.5 +
            tilt_factor * 0.3 +
            height_factor * 0.2
        ) * 100.0
        
        yield_values[i] = min(100.0, max(0.0, total_yield))
    
    return yield_values


# ============================================================================
# ERWEITERTE ERTRAGS-HEATMAP (Task 6)
# ============================================================================

@dataclass
class ExtendedYieldMetrics:
    """Erweiterte Ertrags-Metriken für ein Modul."""
    module_index: int
    yearly_yield_kwh: float          # Jahresertrag in kWh
    monthly_avg_yield_kwh: float     # Monatlicher Durchschnittsertrag in kWh
    shading_loss_percent: float      # Verschattungsverlust in %
    roi_years: float                 # Return on Investment in Jahren
    co2_savings_kg: float            # CO₂-Einsparung in kg/Jahr
    relative_performance: float      # Relative Performance (0-100)
    position: Tuple[float, float, float]  # (x, y, z) Position


@cached(ttl=120.0)
@monitor_performance("extended_yield_calculation")
def calculate_extended_yield_metrics(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    building_dims: BuildingDims,
    latitude: float = 51.0,
    module_power_wp: float = 400.0,
    electricity_price_eur_kwh: float = 0.30,
    module_cost_eur: float = 200.0
) -> List[ExtendedYieldMetrics]:
    """
    Berechnet erweiterte Ertrags-Metriken für alle Module.
    
    Diese Funktion kombiniert:
    - Basis-Ertragspotential (Ausrichtung, Neigung)
    - Verschattungs-Analyse (durchschnittlich über Jahr)
    - Wirtschaftliche Kennzahlen (ROI, CO₂-Einsparung)
    
    Args:
        module_positions: Liste von (x, y, z) Positionen
        module_transforms: Dictionary mit ModuleTransform-Objekten
        building_dims: Gebäudedimensionen
        latitude: Breitengrad des Standorts
        module_power_wp: Nennleistung des Moduls in Wp (Standard: 400W)
        electricity_price_eur_kwh: Strompreis in EUR/kWh (Standard: 0.30)
        module_cost_eur: Modulkosten in EUR (Standard: 200)
    
    Returns:
        Liste von ExtendedYieldMetrics für jedes Modul
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> transforms = {i: ModuleTransform(index=i) for i in range(2)}
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> metrics = calculate_extended_yield_metrics(positions, transforms, dims)
        >>> len(metrics)
        2
        >>> metrics[0].yearly_yield_kwh > 0
        True
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")
    
    # Berechne Basis-Ertragspotential
    yield_heatmap = calculate_yield_heatmap(
        module_positions,
        module_transforms,
        latitude,
        building_dims
    )
    
    # Berechne durchschnittliche Verschattung über Jahr
    # Simuliere 4 repräsentative Tage (Sonnenwenden und Tagundnachtgleichen)
    representative_days = [
        80,   # 21. März (Frühlingstagundnachtgleiche)
        172,  # 21. Juni (Sommersonnenwende)
        266,  # 23. September (Herbsttagundnachtgleiche)
        355   # 21. Dezember (Wintersonnenwende)
    ]
    
    avg_shading_per_module = {}
    
    for i in range(len(module_positions)):
        total_shading = 0.0
        count = 0
        
        for day in representative_days:
            # Simuliere Mittag (12:00 Uhr)
            sun_azimuth, sun_elevation = calculate_sun_position_for_time(
                latitude, day, 12.0
            )
            
            if sun_elevation > 0:  # Nur wenn Sonne über Horizont
                shading_result = calculate_shading_analysis_enhanced(
                    module_positions,
                    module_transforms,
                    sun_azimuth,
                    sun_elevation,
                    building_dims,
                    include_indirect=True
                )
                
                if i < len(shading_result["total_shading"]):
                    total_shading += shading_result["total_shading"][i]
                    count += 1
        
        if count > 0:
            avg_shading_per_module[i] = total_shading / count
        else:
            avg_shading_per_module[i] = 0.0
    
    # Berechne erweiterte Metriken für jedes Modul
    metrics_list = []
    
    for i, pos in enumerate(module_positions):
        # Basis-Ertragspotential (0-100)
        base_yield_percent = yield_heatmap.get(i, 0.0)
        
        # Verschattungsverlust
        shading_loss = avg_shading_per_module.get(i, 0.0) * 100.0
        
        # Effektives Ertragspotential nach Verschattung
        effective_yield_percent = base_yield_percent * (1.0 - avg_shading_per_module.get(i, 0.0))
        
        # Jahresertrag in kWh
        # Annahme: 1000 kWh/kWp in Deutschland bei optimaler Ausrichtung
        yearly_yield_kwh = (module_power_wp / 1000.0) * 1000.0 * (effective_yield_percent / 100.0)
        
        # Monatlicher Durchschnittsertrag
        monthly_avg_yield_kwh = yearly_yield_kwh / 12.0
        
        # ROI (Return on Investment) in Jahren
        yearly_revenue_eur = yearly_yield_kwh * electricity_price_eur_kwh
        if yearly_revenue_eur > 0:
            roi_years = module_cost_eur / yearly_revenue_eur
        else:
            roi_years = 999.0  # Unendlich (kein Ertrag)
        
        # CO₂-Einsparung in kg/Jahr
        # Annahme: 0.485 kg CO₂/kWh (deutscher Strommix 2024)
        co2_savings_kg = yearly_yield_kwh * 0.485
        
        metrics_list.append(ExtendedYieldMetrics(
            module_index=i,
            yearly_yield_kwh=yearly_yield_kwh,
            monthly_avg_yield_kwh=monthly_avg_yield_kwh,
            shading_loss_percent=shading_loss,
            roi_years=roi_years,
            co2_savings_kg=co2_savings_kg,
            relative_performance=effective_yield_percent,
            position=pos
        ))
    
    return metrics_list


def create_pv_module_3d_with_heatmap(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, ModuleTransform],
    extended_metrics: List[ExtendedYieldMetrics],
    color_by: str = "yearly_yield"
):
    """
    Erstellt 3D-Visualisierung mit Heatmap basierend auf erweiterten Metriken.
    
    Diese Funktion färbt Module basierend auf der gewählten Metrik und
    zeigt alle Details im Hover-Text.
    
    Args:
        module_positions: Liste von (x, y, z) Positionen
        module_transforms: Dictionary mit ModuleTransform-Objekten
        extended_metrics: Liste von ExtendedYieldMetrics
        color_by: Metrik für Farbgebung:
            - "yearly_yield": Jahresertrag (kWh)
            - "roi": Return on Investment (Jahre)
            - "co2_savings": CO₂-Einsparung (kg)
            - "performance": Relative Performance (%)
    
    Returns:
        Plotly Figure mit 3D-Visualisierung und Heatmap
    
    Example:
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> transforms = {i: ModuleTransform(index=i) for i in range(2)}
        >>> metrics = [
        ...     ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, positions[0]),
        ...     ExtendedYieldMetrics(1, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, positions[1])
        ... ]
        >>> fig = create_pv_module_3d_with_heatmap(positions, transforms, metrics)
        >>> len(fig.data) > 0
        True
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise RuntimeError("Plotly ist nicht installiert")
    
    if not extended_metrics:
        raise ValueError("extended_metrics darf nicht leer sein")
    
    # Extrahiere Werte für Farbgebung
    if color_by == "yearly_yield":
        color_values = [m.yearly_yield_kwh for m in extended_metrics]
        colorbar_title = "Jahresertrag (kWh)"
        colorscale = "Viridis"
    elif color_by == "roi":
        color_values = [m.roi_years for m in extended_metrics]
        colorbar_title = "ROI (Jahre)"
        colorscale = "RdYlGn_r"  # Reversed: Rot = lange ROI, Grün = kurze ROI
    elif color_by == "co2_savings":
        color_values = [m.co2_savings_kg for m in extended_metrics]
        colorbar_title = "CO₂-Einsparung (kg/Jahr)"
        colorscale = "Greens"
    else:  # performance
        color_values = [m.relative_performance for m in extended_metrics]
        colorbar_title = "Performance (%)"
        colorscale = "RdYlGn"
    
    # Erstelle Hover-Texte mit allen Metriken
    hover_texts = []
    for m in extended_metrics:
        hover_text = (
            f"<b>Modul #{m.module_index}</b><br>"
            f"Position: ({m.position[0]:.1f}, {m.position[1]:.1f}, {m.position[2]:.1f})<br>"
            f"<br>"
            f"<b>Ertrag:</b><br>"
            f"Jahresertrag: {m.yearly_yield_kwh:.1f} kWh<br>"
            f"Ø Monat: {m.monthly_avg_yield_kwh:.1f} kWh<br>"
            f"Performance: {m.relative_performance:.1f}%<br>"
            f"<br>"
            f"<b>Verschattung:</b><br>"
            f"Verlust: {m.shading_loss_percent:.1f}%<br>"
            f"<br>"
            f"<b>Wirtschaftlichkeit:</b><br>"
            f"ROI: {m.roi_years:.1f} Jahre<br>"
            f"CO₂-Einsparung: {m.co2_savings_kg:.1f} kg/Jahr"
        )
        hover_texts.append(hover_text)
    
    # Erstelle 3D-Scatter Plot
    fig = go.Figure()
    
    # Extrahiere x, y, z Koordinaten
    x_coords = [m.position[0] for m in extended_metrics]
    y_coords = [m.position[1] for m in extended_metrics]
    z_coords = [m.position[2] for m in extended_metrics]
    
    fig.add_trace(go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers',
        marker=dict(
            size=10,
            color=color_values,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(title=colorbar_title),
            line=dict(color='white', width=1)
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        name='Module'
    ))
    
    # Layout
    fig.update_layout(
        title="PV-Module Heatmap",
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
            aspectmode='data'
        ),
        hovermode='closest',
        height=600
    )
    
    return fig


def identify_weak_modules(
    extended_metrics: List[ExtendedYieldMetrics],
    threshold_percent: float = 50.0
) -> List[int]:
    """
    Identifiziert schwache Module mit <50% Performance.
    
    Args:
        extended_metrics: Liste von ExtendedYieldMetrics
        threshold_percent: Schwellwert für "schwach" (Standard: 50%)
    
    Returns:
        Liste von Modul-Indizes mit schwacher Performance
    
    Example:
        >>> metrics = [
        ...     ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ...     ExtendedYieldMetrics(1, 200.0, 16.7, 50.0, 30.0, 97.0, 45.0, (2, 0, 6)),
        ...     ExtendedYieldMetrics(2, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (4, 0, 6))
        ... ]
        >>> identify_weak_modules(metrics, 50.0)
        [1]
    """
    weak_modules = []
    
    for metric in extended_metrics:
        if metric.relative_performance < threshold_percent:
            weak_modules.append(metric.module_index)
    
    return weak_modules


def suggest_module_optimization(
    weak_modules: List[int],
    extended_metrics: List[ExtendedYieldMetrics]
) -> List[Dict[str, Any]]:
    """
    Generiert Optimierungsvorschläge für schwache Module.
    
    Args:
        weak_modules: Liste von Modul-Indizes mit schwacher Performance
        extended_metrics: Liste von ExtendedYieldMetrics
    
    Returns:
        Liste von Vorschlägen mit:
            - module_index: Index des Moduls
            - performance: Aktuelle Performance (%)
            - yearly_loss_kwh: Jährlicher Ertragsverlust (kWh)
            - issue: Beschreibung des Problems
            - suggestion: Optimierungsvorschlag
            - priority: Priorität ("high", "medium", "low")
    
    Example:
        >>> metrics = [
        ...     ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6)),
        ...     ExtendedYieldMetrics(1, 200.0, 16.7, 50.0, 30.0, 97.0, 45.0, (2, 0, 6))
        ... ]
        >>> suggestions = suggest_module_optimization([1], metrics)
        >>> len(suggestions)
        1
        >>> suggestions[0]["priority"]
        'high'
    """
    suggestions = []
    
    # Finde beste Performance als Referenz
    if extended_metrics:
        best_performance = max(m.relative_performance for m in extended_metrics)
        best_yield = max(m.yearly_yield_kwh for m in extended_metrics)
    else:
        best_performance = 100.0
        best_yield = 400.0
    
    for idx in weak_modules:
        # Finde Metrik für dieses Modul
        metric = next((m for m in extended_metrics if m.module_index == idx), None)
        
        if metric is None:
            continue
        
        # Berechne Ertragsverlust im Vergleich zum besten Modul
        yearly_loss_kwh = best_yield - metric.yearly_yield_kwh
        
        # Bestimme Hauptproblem
        if metric.shading_loss_percent > 40.0:
            issue = f"Hohe Verschattung ({metric.shading_loss_percent:.1f}%)"
            suggestion = (
                "Modul an weniger verschattete Position verschieben oder "
                "Verschattungsquellen (Nachbargebäude, andere Module) entfernen"
            )
            priority = "high"
        
        elif metric.relative_performance < 30.0:
            issue = f"Sehr niedrige Performance ({metric.relative_performance:.1f}%)"
            suggestion = (
                "Modul-Ausrichtung optimieren (Richtung Süden) und "
                "Neigung anpassen (30-35° für Deutschland)"
            )
            priority = "high"
        
        elif metric.roi_years > 25.0:
            issue = f"Lange Amortisationszeit ({metric.roi_years:.1f} Jahre)"
            suggestion = (
                "Modul entfernen oder an bessere Position verschieben, "
                "da wirtschaftlich nicht rentabel"
            )
            priority = "medium"
        
        else:
            issue = f"Unterdurchschnittliche Performance ({metric.relative_performance:.1f}%)"
            suggestion = (
                "Position und Ausrichtung überprüfen, "
                "ggf. mit besser performenden Modulen vergleichen"
            )
            priority = "low"
        
        suggestions.append({
            "module_index": idx,
            "performance": metric.relative_performance,
            "yearly_loss_kwh": yearly_loss_kwh,
            "issue": issue,
            "suggestion": suggestion,
            "priority": priority,
            "current_position": metric.position,
            "roi_years": metric.roi_years,
            "shading_loss": metric.shading_loss_percent
        })
    
    # Sortiere nach Priorität und Ertragsverlust
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(
        key=lambda s: (priority_order[s["priority"]], -s["yearly_loss_kwh"])
    )
    
    return suggestions


def create_comparison_view(
    config_a_metrics: List[ExtendedYieldMetrics],
    config_b_metrics: List[ExtendedYieldMetrics],
    config_a_name: str = "Konfiguration A",
    config_b_name: str = "Konfiguration B"
):
    """
    Erstellt Vergleichsansicht für zwei verschiedene Modulkonfigurationen.
    
    Args:
        config_a_metrics: Metriken für Konfiguration A
        config_b_metrics: Metriken für Konfiguration B
        config_a_name: Name für Konfiguration A
        config_b_name: Name für Konfiguration B
    
    Returns:
        Dictionary mit:
            - "summary": Zusammenfassung der Unterschiede
            - "table": Vergleichstabelle als DataFrame (wenn pandas verfügbar)
            - "chart": Plotly Figure mit Vergleichs-Diagramm
    
    Example:
        >>> metrics_a = [ExtendedYieldMetrics(0, 400.0, 33.3, 10.0, 15.0, 194.0, 90.0, (0, 0, 6))]
        >>> metrics_b = [ExtendedYieldMetrics(0, 350.0, 29.2, 20.0, 17.0, 170.0, 80.0, (0, 0, 6))]
        >>> result = create_comparison_view(metrics_a, metrics_b)
        >>> "summary" in result
        True
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise RuntimeError("Plotly ist nicht installiert")
    
    # Berechne Gesamt-Metriken für beide Konfigurationen
    def calc_totals(metrics):
        return {
            "module_count": len(metrics),
            "total_yearly_yield": sum(m.yearly_yield_kwh for m in metrics),
            "avg_performance": sum(m.relative_performance for m in metrics) / len(metrics) if metrics else 0,
            "total_co2_savings": sum(m.co2_savings_kg for m in metrics),
            "avg_roi": sum(m.roi_years for m in metrics) / len(metrics) if metrics else 0,
            "avg_shading_loss": sum(m.shading_loss_percent for m in metrics) / len(metrics) if metrics else 0
        }
    
    totals_a = calc_totals(config_a_metrics)
    totals_b = calc_totals(config_b_metrics)
    
    # Erstelle Zusammenfassung
    summary = {
        "config_a": {
            "name": config_a_name,
            **totals_a
        },
        "config_b": {
            "name": config_b_name,
            **totals_b
        },
        "differences": {
            "module_count_diff": totals_b["module_count"] - totals_a["module_count"],
            "yearly_yield_diff": totals_b["total_yearly_yield"] - totals_a["total_yearly_yield"],
            "performance_diff": totals_b["avg_performance"] - totals_a["avg_performance"],
            "co2_diff": totals_b["total_co2_savings"] - totals_a["total_co2_savings"],
            "roi_diff": totals_b["avg_roi"] - totals_a["avg_roi"]
        }
    }
    
    # Erstelle Vergleichs-Diagramm
    fig = go.Figure()
    
    categories = [
        "Modulanzahl",
        "Jahresertrag (kWh)",
        "Ø Performance (%)",
        "CO₂-Einsparung (kg)",
        "Ø ROI (Jahre)"
    ]
    
    values_a = [
        totals_a["module_count"],
        totals_a["total_yearly_yield"],
        totals_a["avg_performance"],
        totals_a["total_co2_savings"],
        totals_a["avg_roi"]
    ]
    
    values_b = [
        totals_b["module_count"],
        totals_b["total_yearly_yield"],
        totals_b["avg_performance"],
        totals_b["total_co2_savings"],
        totals_b["avg_roi"]
    ]
    
    fig.add_trace(go.Bar(
        name=config_a_name,
        x=categories,
        y=values_a,
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        name=config_b_name,
        x=categories,
        y=values_b,
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title="Konfigurationsvergleich",
        barmode='group',
        yaxis_title="Wert",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    result = {
        "summary": summary,
        "chart": fig
    }
    
    # Erstelle Tabelle wenn pandas verfügbar
    try:
        import pandas as pd
        
        table_data = {
            "Metrik": [
                "Modulanzahl",
                "Jahresertrag (kWh)",
                "Ø Performance (%)",
                "CO₂-Einsparung (kg/Jahr)",
                "Ø ROI (Jahre)",
                "Ø Verschattungsverlust (%)"
            ],
            config_a_name: [
                totals_a["module_count"],
                f"{totals_a['total_yearly_yield']:.1f}",
                f"{totals_a['avg_performance']:.1f}",
                f"{totals_a['total_co2_savings']:.1f}",
                f"{totals_a['avg_roi']:.1f}",
                f"{totals_a['avg_shading_loss']:.1f}"
            ],
            config_b_name: [
                totals_b["module_count"],
                f"{totals_b['total_yearly_yield']:.1f}",
                f"{totals_b['avg_performance']:.1f}",
                f"{totals_b['total_co2_savings']:.1f}",
                f"{totals_b['avg_roi']:.1f}",
                f"{totals_b['avg_shading_loss']:.1f}"
            ],
            "Differenz": [
                f"{summary['differences']['module_count_diff']:+d}",
                f"{summary['differences']['yearly_yield_diff']:+.1f}",
                f"{summary['differences']['performance_diff']:+.1f}",
                f"{summary['differences']['co2_diff']:+.1f}",
                f"{summary['differences']['roi_diff']:+.1f}",
                f"{totals_b['avg_shading_loss'] - totals_a['avg_shading_loss']:+.1f}"
            ]
        }
        
        result["table"] = pd.DataFrame(table_data)
    except ImportError:
        # Pandas nicht verfügbar
        pass
    
    return result


# ============================================================================
# OPTIMIERUNGS-ASSISTENT
# ============================================================================

@dataclass
class OptimizationResult:
    """Ergebnis einer Optimierung."""
    config: AdvancedLayoutConfig
    score: float
    strategy_name: str
    metrics: Dict[str, Any]


def run_optimization_assistant(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str,
    optimization_goal: str,
    latitude: float = 51.0
) -> List[OptimizationResult]:
    """
    Führt den Optimierungs-Assistenten aus und generiert verschiedene
    Layout-Konfigurationen basierend auf dem Optimierungsziel.
    
    Diese Hauptfunktion generiert 4-5 verschiedene Strategien, bewertet sie
    und gibt die Top 3 zurück.
    
    Generierte Strategien:
    1. Süd-Aufständerung (optimal für Jahresertrag)
    2. Ost-West-Aufständerung (gleichmäßiger Tagesertrag)
    3. Süd-Ost-Aufständerung (optimal für Morgenertrag)
    4. Gemischte Konfiguration mit Garage und Fassade (maximale Kapazität)
    
    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
        optimization_goal: Optimierungsziel:
            - "max_modules": Maximale Modulanzahl
            - "max_yield": Maximaler Ertrag
            - "balanced": Ausgewogen zwischen Anzahl und Ertrag
        latitude: Breitengrad für Ertragsberechnung
    
    Returns:
        Liste der Top 3 OptimizationResult-Objekte, sortiert nach Score
    
    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> results = run_optimization_assistant(dims, 20, "Flachdach", "max_yield")
        >>> len(results)
        3
        >>> results[0].score >= results[1].score
        True
    """
    configurations = []
    
    # ========================================================================
    # STRATEGIE 1: SÜD-AUFSTÄNDERUNG
    # ========================================================================
    config_south = _generate_south_config(building_dims, target_modules, roof_type)
    score_south, metrics_south = _evaluate_config(
        config_south, building_dims, target_modules, roof_type, optimization_goal, latitude
    )
    configurations.append(OptimizationResult(
        config=config_south,
        score=score_south,
        strategy_name="Süd-Aufständerung",
        metrics=metrics_south
    ))
    
    # ========================================================================
    # STRATEGIE 2: OST-WEST-AUFSTÄNDERUNG
    # ========================================================================
    config_east_west = _generate_east_west_config(building_dims, target_modules, roof_type)
    score_east_west, metrics_east_west = _evaluate_config(
        config_east_west, building_dims, target_modules, roof_type, optimization_goal, latitude
    )
    configurations.append(OptimizationResult(
        config=config_east_west,
        score=score_east_west,
        strategy_name="Ost-West-Aufständerung",
        metrics=metrics_east_west
    ))
    
    # ========================================================================
    # STRATEGIE 3: SÜD-OST-AUFSTÄNDERUNG
    # ========================================================================
    config_south_east = _generate_south_east_config(building_dims, target_modules, roof_type)
    score_south_east, metrics_south_east = _evaluate_config(
        config_south_east, building_dims, target_modules, roof_type, optimization_goal, latitude
    )
    configurations.append(OptimizationResult(
        config=config_south_east,
        score=score_south_east,
        strategy_name="Süd-Ost-Aufständerung",
        metrics=metrics_south_east
    ))
    
    # ========================================================================
    # STRATEGIE 4: GEMISCHTE KONFIGURATION
    # ========================================================================
    config_mixed = _generate_mixed_config(building_dims, target_modules, roof_type)
    score_mixed, metrics_mixed = _evaluate_config(
        config_mixed, building_dims, target_modules, roof_type, optimization_goal, latitude
    )
    configurations.append(OptimizationResult(
        config=config_mixed,
        score=score_mixed,
        strategy_name="Gemischt (Garage + Fassade)",
        metrics=metrics_mixed
    ))
    
    # Sortiere nach Score (höchster zuerst)
    configurations.sort(key=lambda x: x.score, reverse=True)
    
    # Gebe Top 3 zurück
    return configurations[:3]


# ============================================================================
# HILFSFUNKTIONEN FÜR OPTIMIERUNG
# ============================================================================

def _generate_south_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str
) -> AdvancedLayoutConfig:
    """Generiert Süd-Aufständerungs-Konfiguration."""
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        mounting_mode="south",
        custom_azimuth=0.0,  # Süd
        custom_tilt=30.0,
        enable_collision_detection=True
    )
    return config


def _generate_east_west_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str
) -> AdvancedLayoutConfig:
    """Generiert Ost-West-Aufständerungs-Konfiguration."""
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        mounting_mode="east-west",
        custom_azimuth=90.0,  # Ost
        custom_tilt=15.0,
        enable_collision_detection=True
    )
    return config


def _generate_south_east_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str
) -> AdvancedLayoutConfig:
    """Generiert Süd-Ost-Aufständerungs-Konfiguration."""
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        mounting_mode="south-east",
        custom_azimuth=45.0,  # Süd-Ost
        custom_tilt=25.0,
        enable_collision_detection=True
    )
    return config


def _generate_mixed_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str
) -> AdvancedLayoutConfig:
    """Generiert gemischte Konfiguration mit Garage und Fassade."""
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=True,
        use_facade=True,
        mounting_mode="south",
        custom_azimuth=0.0,
        custom_tilt=30.0,
        enable_collision_detection=True
    )
    return config


def _evaluate_config(
    config: AdvancedLayoutConfig,
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str,
    optimization_goal: str,
    latitude: float
) -> Tuple[float, Dict[str, Any]]:
    """
    Bewertet eine Konfiguration basierend auf dem Optimierungsziel.
    
    Returns:
        Tuple mit (score, metrics_dict)
    """
    # Schätze Modulanzahl basierend auf Konfiguration
    roof_area = building_dims.length_m * building_dims.width_m
    module_area = PV_W * PV_H
    
    # Basis-Modulanzahl (70% der Dachfläche)
    if module_area != 0:
        base_modules = int((roof_area / module_area) * 0.7)
    else:
        base_modules = 0.0
    
    # Anpassungen basierend auf Konfiguration
    if config.use_garage:
        base_modules += int(base_modules * 0.3)  # +30% durch Garage
    
    if config.use_facade:
        base_modules += int(base_modules * 0.2)  # +20% durch Fassade
    
    # Berechne Ertragsfaktor basierend auf Ausrichtung
    if config.mounting_mode == "south" or config.custom_azimuth == 0.0:
        yield_factor = 1.0  # Optimal
    elif config.mounting_mode == "east-west":
        yield_factor = 0.85  # Gut für Eigenverbrauch
    elif config.mounting_mode == "south-east":
        yield_factor = 0.95  # Sehr gut
    else:
        # Berechne basierend auf custom_azimuth
        azimuth_diff = abs(config.custom_azimuth)
        if azimuth_diff > 180:
            azimuth_diff = 360 - azimuth_diff
        yield_factor = max(0.5, math.cos(_deg_to_rad(azimuth_diff)))
    
    # Berechne Neigungs-Faktor
    optimal_tilt = 35.0
    tilt_diff = abs(config.custom_tilt - optimal_tilt)
    tilt_factor = math.exp(-(tilt_diff ** 2) / (2 * 20 ** 2))
    
    # Kombiniere Faktoren
    total_yield_factor = yield_factor * tilt_factor
    
    # Berechne Score basierend auf Optimierungsziel
    if optimization_goal == "max_modules":
        # Maximiere Modulanzahl
        score = base_modules * 1.0
    elif optimization_goal == "max_yield":
        # Maximiere Ertrag (Anzahl × Ertragsfaktor)
        score = base_modules * total_yield_factor * 100.0
    else:  # balanced
        # Balance zwischen Anzahl und Ertrag
        if target_modules != 0:
            module_score = base_modules / target_modules if target_modules > 0 else 1.0
        else:
            module_score = 0.0
        yield_score = total_yield_factor
        score = (module_score * 0.5 + yield_score * 0.5) * 100.0
    
    # Erstelle Metriken
    metrics = {
        "estimated_modules": base_modules,
        "yield_factor": total_yield_factor,
        "azimuth_factor": yield_factor,
        "tilt_factor": tilt_factor,
        "uses_garage": config.use_garage,
        "uses_facade": config.use_facade,
        "mounting_mode": config.mounting_mode
    }
    
    return score, metrics
