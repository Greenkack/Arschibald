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
            vec_ij_norm = vec_ij / distance_ij
            
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
        height_factor = min(1.0, z_pos / max_z)
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
    base_modules = int((roof_area / module_area) * 0.7)
    
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
        module_score = base_modules / target_modules if target_modules > 0 else 1.0
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
