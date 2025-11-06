"""
3D PV-Visualisierung Optimierungs-Modul

Dieses Modul enthält Optimierungs-Funktionen für die 3D-Visualisierung:
- Layout-Optimierung basierend auf verschiedenen Zielen
- Konfigurations-Bewertung
- Generierung von Layout-Varianten
- Auswahl der besten Konfiguration
"""

import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

try:
    import numpy as np
except ImportError:
    np = None

from utils.pv3d import (
    BuildingDims,
    AdvancedLayoutConfig,
    PV_W,
    PV_H,
    _deg_to_rad
)
from utils.pv3d_performance import cached, monitor_performance


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class ConfigurationScore:
    """
    Bewertung einer Konfiguration mit detaillierten Metriken.
    
    Attributes:
        total_score: Gesamt-Score (0-100)
        module_count_score: Score für Modulanzahl (0-100)
        yield_score: Score für Ertragspotential (0-100)
        space_efficiency_score: Score für Flächennutzung (0-100)
        orientation_score: Score für Ausrichtung (0-100)
        tilt_score: Score für Neigung (0-100)
        collision_penalty: Abzug für Kollisionen (0-100)
        metrics: Zusätzliche Metriken als Dictionary
    """
    total_score: float
    module_count_score: float
    yield_score: float
    space_efficiency_score: float
    orientation_score: float
    tilt_score: float
    collision_penalty: float
    metrics: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# HAUPTFUNKTIONEN
# ============================================================================

@cached(ttl=180.0)  # Cache für 3 Minuten
@monitor_performance("layout_optimization")
def optimize_layout(
    dims: BuildingDims,
    goal: str,
    constraints: Dict[str, Any],
    roof_type: str = "Flachdach",
    latitude: float = 51.0
) -> List[AdvancedLayoutConfig]:
    """
    Optimiert das PV-Modul-Layout basierend auf dem Ziel und Constraints.
    
    Diese Hauptfunktion generiert verschiedene Layout-Varianten, bewertet sie
    und gibt die besten Konfigurationen zurück.
    
    Args:
        dims: Gebäudedimensionen
        goal: Optimierungsziel:
            - "max_modules": Maximale Modulanzahl
            - "max_yield": Maximaler Ertrag
            - "balanced": Ausgewogen zwischen Anzahl und Ertrag
        constraints: Dictionary mit Constraints:
            - "target_modules": Gewünschte Modulanzahl (optional)
            - "min_modules": Minimale Modulanzahl (optional)
            - "max_modules": Maximale Modulanzahl (optional)
            - "use_garage": Garage verwenden (bool, optional)
            - "use_facade": Fassade verwenden (bool, optional)
            - "min_tilt": Minimale Neigung in Grad (optional)
            - "max_tilt": Maximale Neigung in Grad (optional)
        roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
        latitude: Breitengrad für Ertragsberechnung
    
    Returns:
        Liste der Top 3 AdvancedLayoutConfig-Objekte, sortiert nach Score
    
    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> constraints = {"target_modules": 20, "use_garage": False}
        >>> configs = optimize_layout(dims, "max_yield", constraints)
        >>> len(configs)
        3
        >>> configs[0]  # Beste Konfiguration
        <AdvancedLayoutConfig object>
    """
    # Generiere Layout-Varianten
    variants = generate_layout_variants(
        dims=dims,
        roof_type=roof_type,
        constraints=constraints
    )
    
    # Bewerte alle Varianten
    scored_variants = []
    for variant in variants:
        score = evaluate_configuration(
            config=variant,
            dims=dims,
            goal=goal,
            constraints=constraints,
            latitude=latitude
        )
        scored_variants.append((variant, score))
    
    # Wähle beste Konfigurationen aus
    best_configs = select_best_configuration(
        scored_variants=scored_variants,
        goal=goal,
        top_n=3
    )
    
    return best_configs


def evaluate_configuration(
    config: AdvancedLayoutConfig,
    dims: BuildingDims,
    goal: str,
    constraints: Dict[str, Any],
    latitude: float = 51.0
) -> ConfigurationScore:
    """
    Bewertet eine Konfiguration basierend auf verschiedenen Kriterien.
    
    Diese Funktion berechnet einen Gesamt-Score für eine Konfiguration
    basierend auf:
    - Modulanzahl
    - Ertragspotential (Ausrichtung, Neigung)
    - Flächennutzung
    - Kollisionen
    
    Args:
        config: Zu bewertende Konfiguration
        dims: Gebäudedimensionen
        goal: Optimierungsziel ("max_modules", "max_yield", "balanced")
        constraints: Dictionary mit Constraints
        latitude: Breitengrad für Ertragsberechnung
    
    Returns:
        ConfigurationScore-Objekt mit detaillierter Bewertung
    
    Example:
        >>> config = AdvancedLayoutConfig(mounting_mode="south")
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> score = evaluate_configuration(config, dims, "max_yield", {})
        >>> score.total_score
        85.5
    """
    # ========================================================================
    # 1. MODULANZAHL-SCORE
    # ========================================================================
    estimated_modules = _estimate_module_count(config, dims)
    target_modules = constraints.get("target_modules", estimated_modules)
    
    if target_modules > 0:
        module_count_score = min(100.0, (estimated_modules / target_modules) * 100.0)
    else:
        module_count_score = 100.0
    
    # ========================================================================
    # 2. ERTRAGS-SCORE (Ausrichtung + Neigung)
    # ========================================================================
    orientation_score = _calculate_orientation_score(config, latitude)
    tilt_score = _calculate_tilt_score(config, latitude)
    
    # Kombiniere Ausrichtung und Neigung für Gesamt-Ertragsscore
    yield_score = (orientation_score * 0.6 + tilt_score * 0.4)
    
    # ========================================================================
    # 3. FLÄCHENNUTZUNGS-SCORE
    # ========================================================================
    space_efficiency_score = _calculate_space_efficiency(config, dims, estimated_modules)
    
    # ========================================================================
    # 4. KOLLISIONS-PENALTY
    # ========================================================================
    collision_penalty = 0.0
    if config.enable_collision_detection:
        # Schätze Kollisionen basierend auf Konfiguration
        collision_penalty = _estimate_collision_penalty(config, dims)
    
    # ========================================================================
    # 5. GESAMT-SCORE BERECHNEN
    # ========================================================================
    # Gewichte basierend auf Optimierungsziel
    if goal == "max_modules":
        weights = {
            "module_count": 0.6,
            "yield": 0.2,
            "space_efficiency": 0.2
        }
    elif goal == "max_yield":
        weights = {
            "module_count": 0.2,
            "yield": 0.6,
            "space_efficiency": 0.2
        }
    else:  # balanced
        weights = {
            "module_count": 0.35,
            "yield": 0.35,
            "space_efficiency": 0.3
        }
    
    # Berechne gewichteten Gesamt-Score
    total_score = (
        module_count_score * weights["module_count"] +
        yield_score * weights["yield"] +
        space_efficiency_score * weights["space_efficiency"]
    )
    
    # Ziehe Kollisions-Penalty ab
    total_score = max(0.0, total_score - collision_penalty)
    
    # ========================================================================
    # 6. ERSTELLE METRIKEN
    # ========================================================================
    metrics = {
        "estimated_modules": estimated_modules,
        "target_modules": target_modules,
        "mounting_mode": config.mounting_mode,
        "azimuth_deg": config.custom_azimuth,
        "tilt_deg": config.custom_tilt,
        "uses_garage": config.use_garage,
        "uses_facade": config.use_facade,
        "roof_area_m2": dims.length_m * dims.width_m,
        "module_area_m2": PV_W * PV_H,
        "coverage_ratio": (estimated_modules * PV_W * PV_H) / (dims.length_m * dims.width_m)
    }
    
    return ConfigurationScore(
        total_score=total_score,
        module_count_score=module_count_score,
        yield_score=yield_score,
        space_efficiency_score=space_efficiency_score,
        orientation_score=orientation_score,
        tilt_score=tilt_score,
        collision_penalty=collision_penalty,
        metrics=metrics
    )


def generate_layout_variants(
    dims: BuildingDims,
    roof_type: str,
    constraints: Dict[str, Any]
) -> List[AdvancedLayoutConfig]:
    """
    Generiert verschiedene Layout-Varianten basierend auf Dachtyp und Constraints.
    
    Diese Funktion erstellt 6-8 verschiedene Konfigurationen mit unterschiedlichen
    Aufständerungs-Modi, Ausrichtungen und Zusatzflächen.
    
    Args:
        dims: Gebäudedimensionen
        roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
        constraints: Dictionary mit Constraints
    
    Returns:
        Liste von AdvancedLayoutConfig-Objekten (6-8 Varianten)
    
    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> variants = generate_layout_variants(dims, "Flachdach", {})
        >>> len(variants) >= 6
        True
    """
    variants = []
    
    # Extrahiere Constraints
    use_garage_constraint = constraints.get("use_garage", None)
    use_facade_constraint = constraints.get("use_facade", None)
    min_tilt = constraints.get("min_tilt", 0.0)
    max_tilt = constraints.get("max_tilt", 90.0)
    
    # ========================================================================
    # VARIANTE 1: SÜD-AUFSTÄNDERUNG (OPTIMAL)
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="south",
        custom_azimuth=0.0,  # Süd
        custom_tilt=max(min_tilt, min(30.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 2: OST-WEST-AUFSTÄNDERUNG
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="east-west",
        custom_azimuth=90.0,  # Ost
        custom_tilt=max(min_tilt, min(15.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 3: SÜD-OST-AUFSTÄNDERUNG
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="south-east",
        custom_azimuth=45.0,  # Süd-Ost
        custom_tilt=max(min_tilt, min(25.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 4: SÜD-WEST-AUFSTÄNDERUNG
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="south-west",
        custom_azimuth=315.0,  # Süd-West
        custom_tilt=max(min_tilt, min(25.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 5: FLACHE AUFSTÄNDERUNG (10°)
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="custom",
        custom_azimuth=0.0,  # Süd
        custom_tilt=max(min_tilt, min(10.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 6: STEILE AUFSTÄNDERUNG (35°)
    # ========================================================================
    variants.append(AdvancedLayoutConfig(
        mode="auto",
        use_garage=False if use_garage_constraint is None else use_garage_constraint,
        use_facade=False if use_facade_constraint is None else use_facade_constraint,
        mounting_mode="custom",
        custom_azimuth=0.0,  # Süd
        custom_tilt=max(min_tilt, min(35.0, max_tilt)),
        enable_collision_detection=True,
        enable_shading_analysis=False
    ))
    
    # ========================================================================
    # VARIANTE 7: MIT GARAGE (falls nicht durch Constraint verboten)
    # ========================================================================
    if use_garage_constraint is None or use_garage_constraint:
        variants.append(AdvancedLayoutConfig(
            mode="auto",
            use_garage=True,
            use_facade=False if use_facade_constraint is None else use_facade_constraint,
            mounting_mode="south",
            custom_azimuth=0.0,
            custom_tilt=max(min_tilt, min(30.0, max_tilt)),
            enable_collision_detection=True,
            enable_shading_analysis=False
        ))
    
    # ========================================================================
    # VARIANTE 8: MIT GARAGE UND FASSADE (maximale Kapazität)
    # ========================================================================
    if (use_garage_constraint is None or use_garage_constraint) and \
       (use_facade_constraint is None or use_facade_constraint):
        variants.append(AdvancedLayoutConfig(
            mode="auto",
            use_garage=True,
            use_facade=True,
            mounting_mode="south",
            custom_azimuth=0.0,
            custom_tilt=max(min_tilt, min(30.0, max_tilt)),
            enable_collision_detection=True,
            enable_shading_analysis=False
        ))
    
    return variants


def select_best_configuration(
    scored_variants: List[Tuple[AdvancedLayoutConfig, ConfigurationScore]],
    goal: str,
    top_n: int = 3
) -> List[AdvancedLayoutConfig]:
    """
    Wählt die besten Konfigurationen aus einer Liste von bewerteten Varianten.
    
    Diese Funktion sortiert die Varianten nach Score und gibt die Top N zurück.
    
    Args:
        scored_variants: Liste von Tupeln (config, score)
        goal: Optimierungsziel (für Logging/Debugging)
        top_n: Anzahl der zurückzugebenden Konfigurationen
    
    Returns:
        Liste der Top N AdvancedLayoutConfig-Objekte
    
    Example:
        >>> config1 = AdvancedLayoutConfig(mounting_mode="south")
        >>> score1 = ConfigurationScore(total_score=85.0, ...)
        >>> config2 = AdvancedLayoutConfig(mounting_mode="east-west")
        >>> score2 = ConfigurationScore(total_score=75.0, ...)
        >>> scored = [(config1, score1), (config2, score2)]
        >>> best = select_best_configuration(scored, "max_yield", top_n=1)
        >>> len(best)
        1
        >>> best[0].mounting_mode
        'south'
    """
    # Sortiere nach total_score (höchster zuerst)
    sorted_variants = sorted(
        scored_variants,
        key=lambda x: x[1].total_score,
        reverse=True
    )
    
    # Gebe Top N Konfigurationen zurück
    best_configs = [config for config, score in sorted_variants[:top_n]]
    
    return best_configs


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def _estimate_module_count(
    config: AdvancedLayoutConfig,
    dims: BuildingDims
) -> int:
    """
    Schätzt die Anzahl der Module für eine Konfiguration.
    
    Args:
        config: Konfiguration
        dims: Gebäudedimensionen
    
    Returns:
        Geschätzte Modulanzahl
    """
    # Berechne Dachfläche
    roof_area = dims.length_m * dims.width_m
    module_area = PV_W * PV_H
    
    # Anpassung basierend auf Neigung
    # Flachere Neigung = mehr Abstand nötig = weniger Module
    # Steilere Neigung = weniger Abstand = mehr Module
    tilt = config.custom_tilt
    if tilt < 15.0:
        coverage_factor = 0.6  # Flach: mehr Abstand für Verschattung
    elif tilt < 25.0:
        coverage_factor = 0.7  # Mittel: Standard
    else:
        coverage_factor = 0.75  # Steil: weniger Abstand nötig
    
    # Basis-Modulanzahl
    base_modules = int((roof_area / module_area) * coverage_factor)
    
    # Anpassungen basierend auf Zusatzflächen
    if config.use_garage:
        # Garage fügt ca. 30% mehr Module hinzu
        base_modules = int(base_modules * 1.3)
    
    if config.use_facade:
        # Fassade fügt ca. 20% mehr Module hinzu
        base_modules = int(base_modules * 1.2)
    
    return base_modules


def _calculate_orientation_score(
    config: AdvancedLayoutConfig,
    latitude: float
) -> float:
    """
    Berechnet den Ausrichtungs-Score (0-100) basierend auf Azimuth.
    
    Süd (0°) = 100, Nord (180°) = 0
    
    Args:
        config: Konfiguration
        latitude: Breitengrad
    
    Returns:
        Score 0-100
    """
    # Optimale Ausrichtung ist Süd (0°)
    optimal_azimuth = 0.0
    
    # Berechne Differenz zum Optimum
    azimuth_diff = abs(config.custom_azimuth - optimal_azimuth)
    if azimuth_diff > 180:
        azimuth_diff = 360 - azimuth_diff
    
    # Verwende Cosinus-Funktion für sanften Übergang
    # cos(0°) = 1.0 (Süd, optimal)
    # cos(90°) = 0.0 (Ost/West, akzeptabel)
    # cos(180°) = -1.0 (Nord, schlecht)
    orientation_factor = math.cos(_deg_to_rad(azimuth_diff))
    
    # Konvertiere zu 0-100 Score
    # -1.0 -> 0, 0.0 -> 50, 1.0 -> 100
    score = (orientation_factor + 1.0) * 50.0
    
    return max(0.0, min(100.0, score))


def _calculate_tilt_score(
    config: AdvancedLayoutConfig,
    latitude: float
) -> float:
    """
    Berechnet den Neigungs-Score (0-100) basierend auf Tilt.
    
    Optimal ist ca. Breitengrad - 15° (für Deutschland ca. 35°)
    
    Args:
        config: Konfiguration
        latitude: Breitengrad
    
    Returns:
        Score 0-100
    """
    # Optimale Neigung basierend auf Breitengrad
    # Faustregel: optimal_tilt ≈ latitude - 15°
    optimal_tilt = max(25.0, min(45.0, abs(latitude) - 15.0))
    
    # Berechne Differenz zum Optimum
    tilt_diff = abs(config.custom_tilt - optimal_tilt)
    
    # Verwende Gauss-Kurve für sanften Abfall
    # Sigma = 20° (großzügiger Toleranzbereich)
    tilt_factor = math.exp(-(tilt_diff ** 2) / (2 * 20 ** 2))
    
    # Konvertiere zu 0-100 Score
    score = tilt_factor * 100.0
    
    return max(0.0, min(100.0, score))


def _calculate_space_efficiency(
    config: AdvancedLayoutConfig,
    dims: BuildingDims,
    estimated_modules: int
) -> float:
    """
    Berechnet den Flächennutzungs-Score (0-100).
    
    Höhere Werte bedeuten bessere Nutzung der verfügbaren Fläche.
    
    Args:
        config: Konfiguration
        dims: Gebäudedimensionen
        estimated_modules: Geschätzte Modulanzahl
    
    Returns:
        Score 0-100
    """
    # Berechne verfügbare Fläche
    roof_area = dims.length_m * dims.width_m
    
    # Berechne genutzte Fläche
    module_area = PV_W * PV_H
    used_area = estimated_modules * module_area
    
    # Berechne Nutzungsgrad
    if roof_area > 0:
        efficiency = (used_area / roof_area) * 100.0
    else:
        efficiency = 0.0
    
    # Begrenze auf 0-100
    # Werte über 100% sind möglich wenn Garage/Fassade genutzt werden
    # Das ist positiv, also belohnen wir es
    score = min(100.0, efficiency)
    
    # Bonus für Zusatzflächen
    if config.use_garage:
        score = min(100.0, score * 1.1)  # +10% Bonus
    
    if config.use_facade:
        score = min(100.0, score * 1.05)  # +5% Bonus
    
    return max(0.0, score)


def _estimate_collision_penalty(
    config: AdvancedLayoutConfig,
    dims: BuildingDims
) -> float:
    """
    Schätzt die Kollisions-Penalty (0-100) basierend auf Konfiguration.
    
    Höhere Werte bedeuten mehr Kollisionen (schlechter).
    
    Args:
        config: Konfiguration
        dims: Gebäudedimensionen
    
    Returns:
        Penalty 0-100
    """
    penalty = 0.0
    
    # Flache Neigung + Ost-West = höheres Kollisionsrisiko
    if config.mounting_mode == "east-west" and config.custom_tilt < 15.0:
        penalty += 10.0
    
    # Sehr steile Neigung = höheres Kollisionsrisiko
    if config.custom_tilt > 40.0:
        penalty += 15.0
    
    # Kleine Dachfläche + viele Zusatzflächen = höheres Kollisionsrisiko
    roof_area = dims.length_m * dims.width_m
    if roof_area < 50.0 and (config.use_garage or config.use_facade):
        penalty += 5.0
    
    return min(100.0, penalty)
