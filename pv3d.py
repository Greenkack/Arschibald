"""
3D PV-Visualisierung Core Engine

Dieses Modul stellt die Kern-Funktionalität für die 3D-Visualisierung
von Photovoltaik-Anlagen auf Gebäuden bereit.
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Callable
import json

# Monitoring Infrastructure
try:
    from app_tracing import app_tracer
    from app_evaluation import track_success, track_error, evaluate_performance
    MONITORING_AVAILABLE = True
    
    def trace_pv3d(func):
        """Decorator for PV 3D operations tracing."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = f"pv3d.{func.__name__}"
            try:
                with app_tracer.create_span(operation_name, {"function": func.__name__}):
                    result = func(*args, **kwargs)
                    track_success(operation_name)
                    evaluate_performance(operation_name, time.time() - start_time)
                    return result
            except Exception as e:
                track_error(operation_name, e)
                raise
        return wrapper
except ImportError:
    MONITORING_AVAILABLE = False
    def trace_pv3d(func):
        return func
__all__ = [
    'AdvancedLayoutConfig',
    'BuildingDims',
    'LayoutConfig',
    'ModuleGroup',
    'ModuleTransform',
    'PV_H',
    'PV_T',
    'PV_W',
    'ROOF_COLORS',
    'add_module',
    'apply_module_transform',
    'build_scene',
    'calculate_shading_for_module',
    'calculate_sun_position',
    'detect_collisions',
    'evaluate_config',
    'export_360_animation',
    'export_gltf',
    'export_layout_json',
    'export_module_details_csv',
    'export_multi_view_screenshots',
    'export_stl',
    'from_dict',
    'from_json',
    'generate_east_west_config',
    'generate_mixed_config',
    'generate_south_config',
    'generate_south_east_config',
    'get_module_bounding_box',
    'get_module_count',
    'grid_positions',
    'has_module',
    'import_layout_json',
    'interpolate_color',
    'make_box',
    'make_panel',
    'make_roof_flat',
    'make_roof_gable',
    'make_roof_hip',
    'make_roof_pent',
    'make_roof_pyramid',
    'optimize_layout',
    'place_panels_auto',
    'place_panels_flat_roof',
    'place_panels_manual',
    'remove_module',
    'render_image_bytes',
    'to_dict',
    'to_json',
    'visualize_shading',
]


try:
    import pyvista as pv
    import numpy as np
except ImportError:
    pv = None
    np = None


# ============================================================================
# KONSTANTEN
# ============================================================================

# PV-Modul Standardmaße (in Metern)
PV_W = 1.05  # Breite
PV_H = 1.76  # Höhe
PV_T = 0.04  # Dicke

# Dachdeckungsfarben (Hex-Farben)
ROOF_COLORS = {
    "Ziegel": "#c96a2d",           # orange-rötlich
    "Beton": "#9ea3a8",            # grau
    "Schiefer": "#3b3f44",         # dunkelgrau
    "Eternit": "#7e8388",          # mittelgrau
    "Trapezblech": "#8e8f93",      # hellgrau
    "Bitumen": "#4a4d52",          # dunkelgrau
    "default": "#b0b5ba"           # Standard-grau
}


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def _deg_to_rad(degrees: float) -> float:
    """
    Konvertiert Grad zu Radiant.

    Args:
        degrees: Winkel in Grad

    Returns:
        Winkel in Radiant
    """
    return degrees * math.pi / 180.0


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class BuildingDims:
    """Gebäudedimensionen für 3D-Modellierung.

    Attributes:
        length_m: Gebäudelänge in Metern
        width_m: Gebäudebreite in Metern
        wall_height_m: Traufhöhe (Wandhöhe) in Metern
    """
    length_m: float = 10.0
    width_m: float = 6.0
    wall_height_m: float = 6.0


@dataclass
class ModuleTransform:
    """Transformation für einzelnes PV-Modul.

    Diese Klasse speichert individuelle Transformationsparameter für ein
    einzelnes PV-Modul, einschließlich Rotation (Azimuth und Neigung) und
    Position (X, Y, Z Offsets).

    Attributes:
        index: Modul-Index (0-basiert)
        azimuth_deg: Azimuth-Winkel in Grad (0° = Süd, 90° = West, 
                     180° = Nord, 270° = Ost)
        tilt_deg: Neigungs-Winkel in Grad (0° = horizontal, 90° = vertikal)
        offset_x: X-Offset in Metern (relativ zur Rasterposition)
        offset_y: Y-Offset in Metern (relativ zur Rasterposition)
        offset_z: Z-Offset in Metern (relativ zur Rasterposition)
        group_id: Optionale Gruppen-ID für Gruppenzugehörigkeit
    """
    index: int
    azimuth_deg: float = 0.0
    tilt_deg: float = 15.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    offset_z: float = 0.0
    group_id: str = None

    def __post_init__(self):
        """
        Validiert Wertebereiche nach Initialisierung.

        Raises:
            ValueError: Wenn Werte außerhalb der gültigen Bereiche liegen
        """
        # Validiere Azimuth (0-360°)
        if not (0.0 <= self.azimuth_deg <= 360.0):
            raise ValueError(
                f"Azimuth muss zwischen 0° und 360° liegen, "
                f"erhalten: {self.azimuth_deg}°"
            )

        # Validiere Tilt (0-90°)
        if not (0.0 <= self.tilt_deg <= 90.0):
            raise ValueError(
                f"Neigung muss zwischen 0° und 90° liegen, "
                f"erhalten: {self.tilt_deg}°"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Transformation zu einem Dictionary.

        Returns:
            Dictionary mit allen Transformationsparametern
        """
        return {
            "index": self.index,
            "azimuth_deg": self.azimuth_deg,
            "tilt_deg": self.tilt_deg,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "offset_z": self.offset_z,
            "group_id": self.group_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleTransform':
        """
        Erstellt eine ModuleTransform-Instanz aus einem Dictionary.

        Args:
            data: Dictionary mit Transformationsparametern

        Returns:
            ModuleTransform-Instanz

        Raises:
            ValueError: Wenn erforderliche Felder fehlen oder ungültig sind
        """
        try:
            return cls(
                index=int(data["index"]),
                azimuth_deg=float(data.get("azimuth_deg", 0.0)),
                tilt_deg=float(data.get("tilt_deg", 15.0)),
                offset_x=float(data.get("offset_x", 0.0)),
                offset_y=float(data.get("offset_y", 0.0)),
                offset_z=float(data.get("offset_z", 0.0)),
                group_id=data.get("group_id")
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Ungültiges ModuleTransform Dictionary: {e}")


@dataclass
class ModuleGroup:
    """Gruppe von PV-Modulen mit gemeinsamen Eigenschaften.

    Diese Klasse ermöglicht die Verwaltung von Modulgruppen, die gemeinsame
    Transformationsparameter (Azimuth, Neigung) und visuelle Eigenschaften
    (Farbe) teilen.

    Attributes:
        name: Name der Gruppe (z.B. "Süddach", "Ostdach")
        module_indices: Liste der Modul-Indizes in dieser Gruppe
        azimuth_deg: Gemeinsamer Azimuth-Winkel für alle Module in der Gruppe
        tilt_deg: Gemeinsame Neigung für alle Module in der Gruppe
        color: Farbe für die Gruppe (Hex-String, z.B. "#000000")
    """
    name: str
    module_indices: List[int] = field(default_factory=list)
    azimuth_deg: float = 0.0
    tilt_deg: float = 15.0
    color: str = "#000000"

    def add_module(self, index: int) -> None:
        """
        Fügt ein Modul zur Gruppe hinzu.

        Args:
            index: Modul-Index (0-basiert)

        Raises:
            ValueError: Wenn Modul bereits in der Gruppe ist
        """
        if index in self.module_indices:
            raise ValueError(
                f"Modul {index} ist bereits in Gruppe '{self.name}'"
            )
        self.module_indices.append(index)

    def remove_module(self, index: int) -> None:
        """
        Entfernt ein Modul aus der Gruppe.

        Args:
            index: Modul-Index (0-basiert)

        Raises:
            ValueError: Wenn Modul nicht in der Gruppe ist
        """
        if index not in self.module_indices:
            raise ValueError(
                f"Modul {index} ist nicht in Gruppe '{self.name}'"
            )
        self.module_indices.remove(index)

    def has_module(self, index: int) -> bool:
        """
        Prüft ob ein Modul in der Gruppe ist.

        Args:
            index: Modul-Index (0-basiert)

        Returns:
            True wenn Modul in der Gruppe ist, sonst False
        """
        return index in self.module_indices

    def get_module_count(self) -> int:
        """
        Gibt die Anzahl der Module in der Gruppe zurück.

        Returns:
            Anzahl der Module
        """
        return len(self.module_indices)

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Gruppe zu einem Dictionary.

        Returns:
            Dictionary mit allen Gruppenparametern
        """
        return {
            "name": self.name,
            "module_indices": self.module_indices.copy(),
            "azimuth_deg": self.azimuth_deg,
            "tilt_deg": self.tilt_deg,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleGroup':
        """
        Erstellt eine ModuleGroup-Instanz aus einem Dictionary.

        Args:
            data: Dictionary mit Gruppenparametern

        Returns:
            ModuleGroup-Instanz

        Raises:
            ValueError: Wenn erforderliche Felder fehlen oder ungültig sind
        """
        try:
            return cls(
                name=str(data["name"]),
                module_indices=list(data.get("module_indices", [])),
                azimuth_deg=float(data.get("azimuth_deg", 0.0)),
                tilt_deg=float(data.get("tilt_deg", 15.0)),
                color=str(data.get("color", "#000000"))
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Ungültiges ModuleGroup Dictionary: {e}")


@dataclass
class LayoutConfig:
    """Konfiguration für PV-Modul-Layout.

    Attributes:
        mode: Belegungsmodus ("auto" oder "manual")
        use_garage: Garage/Carport automatisch hinzufügen
        use_facade: Fassadenbelegung aktivieren
        removed_indices: Liste der entfernten Modul-Indizes (0-basiert)
        garage_dims: Garage-Dimensionen (Länge, Breite, Höhe) in Metern
        offset_main_xy: Offset für Hauptgebäude (x, y) in Metern
        offset_garage_xy: Offset für Garage (x, y) in Metern
    """
    mode: str = "auto"
    use_garage: bool = False
    use_facade: bool = False
    removed_indices: List[int] = field(default_factory=list)
    garage_dims: Tuple[float, float, float] = (6.0, 3.0, 3.0)
    offset_main_xy: Tuple[float, float] = (0.0, 0.0)
    offset_garage_xy: Tuple[float, float] = (0.0, 0.0)

    def to_json(self) -> str:
        """
        Serialisiert die Konfiguration zu JSON.

        Returns:
            JSON-String der Konfiguration
        """
        data = {
            "mode": self.mode,
            "use_garage": self.use_garage,
            "use_facade": self.use_facade,
            "removed_indices": self.removed_indices,
            "garage_dims": list(self.garage_dims),
            "offset_main_xy": list(self.offset_main_xy),
            "offset_garage_xy": list(self.offset_garage_xy)
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'LayoutConfig':
        """
        Deserialisiert die Konfiguration aus JSON.

        Args:
            json_str: JSON-String der Konfiguration

        Returns:
            LayoutConfig-Instanz

        Raises:
            ValueError: Wenn JSON ungültig ist
        """
        try:
            data = json.loads(json_str)
            return cls(
                mode=data.get("mode", "auto"),
                use_garage=data.get("use_garage", False),
                use_facade=data.get("use_facade", False),
                removed_indices=data.get("removed_indices", []),
                garage_dims=tuple(
                    data.get("garage_dims", [6.0, 3.0, 3.0])
                ),
                offset_main_xy=tuple(
                    data.get("offset_main_xy", [0.0, 0.0])
                ),
                offset_garage_xy=tuple(
                    data.get("offset_garage_xy", [0.0, 0.0])
                )
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Ungültiger JSON-String: {e}")


@dataclass
class AdvancedLayoutConfig(LayoutConfig):
    """Erweiterte Konfiguration für PV-Modul-Layout mit individuellen
    Modul-Transformationen und Gruppen-Verwaltung.

    Diese Klasse erweitert LayoutConfig um erweiterte Funktionen für
    individuelle Modul-Kontrolle, Gruppen-Verwaltung und zusätzliche
    Aufständerungs-Modi.

    Attributes:
        module_transforms: Dictionary mit ModuleTransform-Objekten
                          (Key: Modul-Index, Value: ModuleTransform)
        module_groups: Dictionary mit ModuleGroup-Objekten
                      (Key: Gruppen-Name, Value: ModuleGroup)
        mounting_mode: Aufständerungs-Modus für Flachdächer
                      ("south", "east-west", "south-east", "south-west", "custom")
        custom_azimuth: Benutzerdefinierter Azimuth für "custom" Modus
        custom_tilt: Benutzerdefinierte Neigung für "custom" Modus
        enable_collision_detection: Aktiviert Kollisionserkennung zwischen Modulen
        enable_shading_analysis: Aktiviert Verschattungs-Analyse
    """
    module_transforms: Dict[int, 'ModuleTransform'] = field(default_factory=dict)
    module_groups: Dict[str, 'ModuleGroup'] = field(default_factory=dict)
    mounting_mode: str = "south"
    custom_azimuth: float = 0.0
    custom_tilt: float = 15.0
    enable_collision_detection: bool = True
    enable_shading_analysis: bool = False

    def to_json(self) -> str:
        """
        Serialisiert die erweiterte Konfiguration zu JSON.

        Returns:
            JSON-String der Konfiguration
        """
        # Basis-Daten von LayoutConfig
        data = {
            "mode": self.mode,
            "use_garage": self.use_garage,
            "use_facade": self.use_facade,
            "removed_indices": self.removed_indices,
            "garage_dims": list(self.garage_dims),
            "offset_main_xy": list(self.offset_main_xy),
            "offset_garage_xy": list(self.offset_garage_xy),
            # Erweiterte Daten
            "module_transforms": {
                str(idx): transform.to_dict()
                for idx, transform in self.module_transforms.items()
            },
            "module_groups": {
                name: group.to_dict()
                for name, group in self.module_groups.items()
            },
            "mounting_mode": self.mounting_mode,
            "custom_azimuth": self.custom_azimuth,
            "custom_tilt": self.custom_tilt,
            "enable_collision_detection": self.enable_collision_detection,
            "enable_shading_analysis": self.enable_shading_analysis
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'AdvancedLayoutConfig':
        """
        Deserialisiert die erweiterte Konfiguration aus JSON.

        Args:
            json_str: JSON-String der Konfiguration

        Returns:
            AdvancedLayoutConfig-Instanz

        Raises:
            ValueError: Wenn JSON ungültig ist
        """
        try:
            data = json.loads(json_str)
            
            # Konvertiere module_transforms Dictionary
            module_transforms = {}
            if "module_transforms" in data:
                for idx_str, transform_data in data["module_transforms"].items():
                    idx = int(idx_str)
                    module_transforms[idx] = ModuleTransform.from_dict(transform_data)
            
            # Konvertiere module_groups Dictionary
            module_groups = {}
            if "module_groups" in data:
                for name, group_data in data["module_groups"].items():
                    module_groups[name] = ModuleGroup.from_dict(group_data)
            
            return cls(
                # Basis-Felder von LayoutConfig
                mode=data.get("mode", "auto"),
                use_garage=data.get("use_garage", False),
                use_facade=data.get("use_facade", False),
                removed_indices=data.get("removed_indices", []),
                garage_dims=tuple(data.get("garage_dims", [6.0, 3.0, 3.0])),
                offset_main_xy=tuple(data.get("offset_main_xy", [0.0, 0.0])),
                offset_garage_xy=tuple(data.get("offset_garage_xy", [0.0, 0.0])),
                # Erweiterte Felder
                module_transforms=module_transforms,
                module_groups=module_groups,
                mounting_mode=data.get("mounting_mode", "south"),
                custom_azimuth=float(data.get("custom_azimuth", 0.0)),
                custom_tilt=float(data.get("custom_tilt", 15.0)),
                enable_collision_detection=data.get("enable_collision_detection", True),
                enable_shading_analysis=data.get("enable_shading_analysis", False)
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Ungültiger JSON-String: {e}")


# ============================================================================
# DATENEXTRAKTIONS-FUNKTIONEN
# ============================================================================

def _safe_get_orientation(project_data: Dict[str, Any]) -> str:
    """
    Extrahiert die Gebäudeausrichtung aus project_data mit Fallbacks.

    Versucht verschiedene Key-Strukturen:
    - project_data["project_details"]["roof_orientation"]
    - project_data["roof_orientation"]
    - project_data["orientation"]

    Args:
        project_data: Projektdaten-Dictionary

    Returns:
        Ausrichtung als String ("Süd", "Ost", "West", "Nord")
        Fallback: "Süd"
    """
    if not project_data:
        return "Süd"

    # Versuche verschiedene Pfade
    try:
        # Pfad 1: project_details.roof_orientation
        if "project_details" in project_data:
            orientation = project_data["project_details"].get(
                "roof_orientation"
            )
            if orientation:
                return str(orientation)

        # Pfad 2: roof_orientation
        orientation = project_data.get("roof_orientation")
        if orientation:
            return str(orientation)

        # Pfad 3: orientation
        orientation = project_data.get("orientation")
        if orientation:
            return str(orientation)
    except (KeyError, TypeError, AttributeError):
        pass

    # Fallback
    return "Süd"


def _safe_get_roof_inclination_deg(project_data: Dict[str, Any]) -> float:
    """
    Extrahiert die Dachneigung aus project_data mit Fallbacks.

    Versucht verschiedene Key-Strukturen und konvertiert zu Float.

    Args:
        project_data: Projektdaten-Dictionary

    Returns:
        Dachneigung in Grad (0-90)
        Fallback: 35.0
    """
    if not project_data:
        return 35.0

    # Versuche verschiedene Pfade
    try:
        # Pfad 1: project_details.roof_inclination_deg
        if "project_details" in project_data:
            inclination = project_data["project_details"].get(
                "roof_inclination_deg"
            )
            if inclination is not None:
                value = float(inclination)
                # Validiere Bereich
                return max(0.0, min(90.0, value))

        # Pfad 2: roof_inclination_deg
        inclination = project_data.get("roof_inclination_deg")
        if inclination is not None:
            value = float(inclination)
            return max(0.0, min(90.0, value))

        # Pfad 3: roof_inclination
        inclination = project_data.get("roof_inclination")
        if inclination is not None:
            value = float(inclination)
            return max(0.0, min(90.0, value))

        # Pfad 4: inclination
        inclination = project_data.get("inclination")
        if inclination is not None:
            value = float(inclination)
            return max(0.0, min(90.0, value))
    except (KeyError, TypeError, ValueError, AttributeError):
        pass

    # Fallback
    return 35.0


def _safe_get_roof_covering(project_data: Dict[str, Any]) -> str:
    """
    Extrahiert die Dachdeckung aus project_data mit Fallbacks.

    Args:
        project_data: Projektdaten-Dictionary

    Returns:
        Dachdeckung als String
        Fallback: "default"
    """
    if not project_data:
        return "default"

    # Versuche verschiedene Pfade
    try:
        # Pfad 1: project_details.roof_covering_type
        if "project_details" in project_data:
            covering = project_data["project_details"].get(
                "roof_covering_type"
            )
            if covering:
                return str(covering)

        # Pfad 2: roof_covering_type
        covering = project_data.get("roof_covering_type")
        if covering:
            return str(covering)

        # Pfad 3: roof_covering
        covering = project_data.get("roof_covering")
        if covering:
            return str(covering)

        # Pfad 4: covering
        covering = project_data.get("covering")
        if covering:
            return str(covering)
    except (KeyError, TypeError, AttributeError):
        pass

    # Fallback
    return "default"


def _roof_color_from_covering(covering: str) -> str:
    """
    Mappt Dachdeckungstyp zu Hex-Farbe.

    Args:
        covering: Dachdeckungstyp

    Returns:
        Hex-Farbe als String
    """
    # Normalisiere Input (case-insensitive)
    covering_normalized = covering.strip() if covering else ""

    # Suche exakte Übereinstimmung
    if covering_normalized in ROOF_COLORS:
        return ROOF_COLORS[covering_normalized]

    # Suche case-insensitive
    for key, color in ROOF_COLORS.items():
        if key.lower() == covering_normalized.lower():
            return color

    # Fallback auf default
    return ROOF_COLORS["default"]


# ============================================================================
# GEOMETRIE-PRIMITIVES
# ============================================================================

def make_box(
    length: float,
    width: float,
    height: float,
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    origin_at_bottom: bool = True
) -> 'pv.PolyData':
    """
    Erstellt einen Quader (Box) mit konfigurierbarem Ursprung.

    Args:
        length: Länge in X-Richtung (Meter)
        width: Breite in Y-Richtung (Meter)
        height: Höhe in Z-Richtung (Meter)
        center: Zentrum des Quaders (x, y, z)
        origin_at_bottom: Wenn True, liegt der Ursprung am Boden (z=0),
                         sonst in der Mitte

    Returns:
        PyVista PolyData Mesh des Quaders

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist
    """
    if pv is None:
        raise RuntimeError("PyVista ist nicht installiert")

    # Erstelle Box mit PyVista
    box = pv.Box(bounds=[
        -length / 2, length / 2,  # x min, max
        -width / 2, width / 2,    # y min, max
        -height / 2, height / 2   # z min, max
    ])

    # Verschiebe Box zum gewünschten Zentrum
    cx, cy, cz = center

    if origin_at_bottom:
        # Verschiebe so dass Boden bei z=cz liegt
        box.translate([cx, cy, cz + height / 2], inplace=True)
    else:
        # Verschiebe zum Zentrum
        box.translate([cx, cy, cz], inplace=True)

    return box


# ============================================================================
# DACHFORM-FUNKTIONEN
# ============================================================================

def make_roof_flat(
    length: float,
    width: float,
    base_height: float
) -> 'pv.PolyData':
    """
    Erstellt ein Flachdach als dünnen Quader.

    Args:
        length: Dachlänge in X-Richtung (Meter)
        width: Dachbreite in Y-Richtung (Meter)
        base_height: Höhe der Dachunterkante (Traufhöhe)

    Returns:
        PyVista PolyData Mesh des Flachdachs
    """
    if pv is None:
        raise RuntimeError("PyVista ist nicht installiert")

    # Flachdach mit 0.12m Dicke
    roof_thickness = 0.12
    return make_box(
        length=length,
        width=width,
        height=roof_thickness,
        center=(0.0, 0.0, base_height),
        origin_at_bottom=True
    )


def make_roof_gable(
    length: float,
    width: float,
    base_height: float,
    inclination_deg: float
) -> 'pv.PolyData':
    """
    Erstellt ein Satteldach mit zwei geneigten Flächen.

    Args:
        length: Dachlänge in X-Richtung (Meter)
        width: Dachbreite in Y-Richtung (Meter)
        base_height: Höhe der Dachunterkante (Traufhöhe)
        inclination_deg: Dachneigung in Grad

    Returns:
        PyVista PolyData Mesh des Satteldachs
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Berechne Firsthöhe
    inclination_rad = _deg_to_rad(inclination_deg)
    ridge_height = (width / 2) * math.tan(inclination_rad)

    # Definiere Eckpunkte des Satteldachs
    # 6 Punkte: 4 an der Traufe, 2 am First
    points = np.array([
        # Traufe vorne links
        [-length / 2, -width / 2, base_height],
        # Traufe vorne rechts
        [length / 2, -width / 2, base_height],
        # Traufe hinten rechts
        [length / 2, width / 2, base_height],
        # Traufe hinten links
        [-length / 2, width / 2, base_height],
        # First vorne
        [-length / 2, 0.0, base_height + ridge_height],
        # First hinten
        [length / 2, 0.0, base_height + ridge_height]
    ])

    # Definiere Flächen (Dreiecke)
    # Vordere Dachfläche (2 Dreiecke)
    # Hintere Dachfläche (2 Dreiecke)
    faces = np.array([
        # Vordere Dachfläche (links)
        [3, 0, 4, 3],  # Dreieck: Punkt 0, 4, 3
        [3, 4, 1, 0],  # Dreieck: Punkt 4, 1, 0
        # Hintere Dachfläche (rechts)
        [3, 1, 5, 2],  # Dreieck: Punkt 1, 5, 2
        [3, 5, 3, 2],  # Dreieck: Punkt 5, 3, 2
        # Giebel vorne
        [3, 0, 1, 4],
        # Giebel hinten
        [3, 2, 3, 5]
    ])

    # Erstelle PolyData
    roof = pv.PolyData(points, faces)
    return roof


def make_roof_hip(
    length: float,
    width: float,
    base_height: float,
    inclination_deg: float
) -> 'pv.PolyData':
    """
    Erstellt ein Walmdach mit vier geneigten Flächen.

    Args:
        length: Dachlänge in X-Richtung (Meter)
        width: Dachbreite in Y-Richtung (Meter)
        base_height: Höhe der Dachunterkante (Traufhöhe)
        inclination_deg: Dachneigung in Grad

    Returns:
        PyVista PolyData Mesh des Walmdachs
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Berechne Firsthöhe
    inclination_rad = _deg_to_rad(inclination_deg)
    ridge_height = (width / 2) * math.tan(inclination_rad)

    # Berechne First-Länge (verkürzt durch Walm)
    # Walm-Anteil: width/2 / tan(inclination)
    if inclination_deg > 0:
        walm_length = (width / 2) / math.tan(inclination_rad)
    else:
        walm_length = 0
    ridge_length = max(0, length - 2 * walm_length)

    # Definiere Eckpunkte
    points = np.array([
        # Traufe: 4 Ecken
        [-length / 2, -width / 2, base_height],  # 0: vorne links
        [length / 2, -width / 2, base_height],   # 1: vorne rechts
        [length / 2, width / 2, base_height],    # 2: hinten rechts
        [-length / 2, width / 2, base_height],   # 3: hinten links
        # First: 2 Punkte (oder 1 wenn ridge_length = 0)
        # 4: First links
        [-ridge_length / 2, 0.0, base_height + ridge_height],
        # 5: First rechts
        [ridge_length / 2, 0.0, base_height + ridge_height]
    ])

    # Definiere Flächen
    if ridge_length > 0.01:
        # Walmdach mit First
        faces = np.array([
            # Vordere Dachfläche
            [3, 0, 4, 3],
            [3, 4, 1, 0],
            # Hintere Dachfläche
            [3, 1, 5, 2],
            [3, 5, 3, 2],
            # Linker Walm
            [3, 3, 4, 0],
            # Rechter Walm
            [3, 1, 5, 2],
            # Hauptflächen
            [3, 0, 1, 4],
            [3, 4, 5, 1],
            [3, 5, 2, 3],
            [3, 3, 4, 5]
        ])
    else:
        # Zeltdach (kein First, nur ein Gipfelpunkt)
        peak = np.array([[0.0, 0.0, base_height + ridge_height]])
        points = np.vstack([points[:4], peak])
        faces = np.array([
            [3, 0, 1, 4],  # Vorne
            [3, 1, 2, 4],  # Rechts
            [3, 2, 3, 4],  # Hinten
            [3, 3, 0, 4]   # Links
        ])

    roof = pv.PolyData(points, faces)
    return roof


def make_roof_pent(
    length: float,
    width: float,
    base_height: float,
    inclination_deg: float
) -> 'pv.PolyData':
    """
    Erstellt ein Pultdach (eine geneigte Fläche).

    Args:
        length: Dachlänge in X-Richtung (Meter)
        width: Dachbreite in Y-Richtung (Meter)
        base_height: Höhe der Dachunterkante (Traufhöhe)
        inclination_deg: Dachneigung in Grad

    Returns:
        PyVista PolyData Mesh des Pultdachs
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Berechne Höhenunterschied
    inclination_rad = _deg_to_rad(inclination_deg)
    height_diff = width * math.tan(inclination_rad)

    # Definiere Eckpunkte (Pultdach steigt in Y-Richtung)
    points = np.array([
        # Untere Kante (vorne)
        [-length / 2, -width / 2, base_height],  # 0: vorne links
        [length / 2, -width / 2, base_height],   # 1: vorne rechts
        # Obere Kante (hinten)
        # 2: hinten rechts
        [length / 2, width / 2, base_height + height_diff],
        # 3: hinten links
        [-length / 2, width / 2, base_height + height_diff]
    ])

    # Definiere Flächen (2 Dreiecke für die Dachfläche)
    faces = np.array([
        [3, 0, 1, 2],  # Dreieck 1
        [3, 0, 2, 3]   # Dreieck 2
    ])

    roof = pv.PolyData(points, faces)
    return roof


def make_roof_pyramid(
    length: float,
    width: float,
    base_height: float,
    inclination_deg: float
) -> 'pv.PolyData':
    """
    Erstellt ein Zeltdach (pyramidenförmig mit zentralem Gipfel).

    Args:
        length: Dachlänge in X-Richtung (Meter)
        width: Dachbreite in Y-Richtung (Meter)
        base_height: Höhe der Dachunterkante (Traufhöhe)
        inclination_deg: Dachneigung in Grad

    Returns:
        PyVista PolyData Mesh des Zeltdachs
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Berechne Gipfelhöhe (basierend auf kürzerer Seite)
    inclination_rad = _deg_to_rad(inclination_deg)
    min_side = min(length, width)
    peak_height = (min_side / 2) * math.tan(inclination_rad)

    # Definiere Eckpunkte
    points = np.array([
        # Traufe: 4 Ecken
        [-length / 2, -width / 2, base_height],  # 0: vorne links
        [length / 2, -width / 2, base_height],   # 1: vorne rechts
        [length / 2, width / 2, base_height],    # 2: hinten rechts
        [-length / 2, width / 2, base_height],   # 3: hinten links
        # Gipfel (zentral)
        [0.0, 0.0, base_height + peak_height]    # 4: Gipfel
    ])

    # Definiere Flächen (4 Dreiecke)
    faces = np.array([
        [3, 0, 1, 4],  # Vordere Fläche
        [3, 1, 2, 4],  # Rechte Fläche
        [3, 2, 3, 4],  # Hintere Fläche
        [3, 3, 0, 4]   # Linke Fläche
    ])

    roof = pv.PolyData(points, faces)
    return roof


# ============================================================================
# PV-MODUL-GEOMETRIE
# ============================================================================

def make_panel(
    position: Tuple[float, float, float],
    yaw_deg: float = 0.0,
    tilt_deg: float = 0.0
) -> 'pv.PolyData':
    """
    Erstellt ein PV-Modul mit Position und Rotation.

    Das Modul wird zunächst horizontal erstellt und dann:
    1. Um die Y-Achse gekippt (tilt - Neigung)
    2. Um die Z-Achse gedreht (yaw - Ausrichtung)
    3. Zur finalen Position verschoben

    Args:
        position: Position (x, y, z) des Modul-Zentrums
        yaw_deg: Rotation um Z-Achse in Grad (0° = Süden, 90° = Westen)
        tilt_deg: Neigung um Y-Achse in Grad (0° = horizontal, 90° = vertikal)

    Returns:
        PyVista PolyData Mesh des PV-Moduls

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Erstelle Modul als Box (horizontal, zentriert bei Origin)
    panel = make_box(
        length=PV_W,   # Breite (X)
        width=PV_H,    # Höhe (Y)
        height=PV_T,   # Dicke (Z)
        center=(0.0, 0.0, 0.0),
        origin_at_bottom=False  # Zentriert
    )

    # Rotation 1: Tilt (Neigung um Y-Achse)
    # Positive Neigung kippt die Vorderkante nach oben
    if abs(tilt_deg) > 0.01:
        tilt_rad = _deg_to_rad(tilt_deg)
        # Rotationsmatrix um Y-Achse
        cos_t = math.cos(tilt_rad)
        sin_t = math.sin(tilt_rad)
        rotation_matrix_tilt = np.array([
            [cos_t, 0, sin_t],
            [0, 1, 0],
            [-sin_t, 0, cos_t]
        ])
        # Rotiere Punkte
        points = panel.points
        panel.points = points @ rotation_matrix_tilt.T

    # Rotation 2: Yaw (Drehung um Z-Achse)
    # 0° = Süden (negative Y-Richtung)
    # 90° = Westen (negative X-Richtung)
    # -90° = Osten (positive X-Richtung)
    # 180° = Norden (positive Y-Richtung)
    if abs(yaw_deg) > 0.01:
        yaw_rad = _deg_to_rad(yaw_deg)
        # Rotationsmatrix um Z-Achse
        cos_y = math.cos(yaw_rad)
        sin_y = math.sin(yaw_rad)
        rotation_matrix_yaw = np.array([
            [cos_y, -sin_y, 0],
            [sin_y, cos_y, 0],
            [0, 0, 1]
        ])
        # Rotiere Punkte
        points = panel.points
        panel.points = points @ rotation_matrix_yaw.T

    # Translation zur finalen Position
    px, py, pz = position
    panel.translate([px, py, pz], inplace=True)

    return panel


def apply_module_transform(
    base_position: Tuple[float, float, float],
    transform: 'ModuleTransform'
) -> 'pv.PolyData':
    """
    Wendet eine individuelle Transformation auf ein PV-Modul an.

    Diese Funktion erstellt ein PV-Modul an einer Basis-Position und wendet
    dann die in ModuleTransform definierten Transformationen an:
    1. Rotation um Y-Achse (Neigung/Tilt)
    2. Rotation um Z-Achse (Azimuth)
    3. Positions-Offset (X, Y, Z)

    Args:
        base_position: Basis-Position (x, y, z) aus dem Raster
        transform: ModuleTransform-Objekt mit Transformationsparametern

    Returns:
        PyVista PolyData Mesh des transformierten PV-Moduls

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist

    Example:
        >>> base_pos = (5.0, 3.0, 6.0)
        >>> transform = ModuleTransform(
        ...     index=0,
        ...     azimuth_deg=90.0,
        ...     tilt_deg=25.0,
        ...     offset_x=0.5,
        ...     offset_y=-0.3,
        ...     offset_z=0.1
        ... )
        >>> panel = apply_module_transform(base_pos, transform)
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Berechne finale Position: Basis-Position + Offsets
    bx, by, bz = base_position
    final_x = bx + transform.offset_x
    final_y = by + transform.offset_y
    final_z = bz + transform.offset_z
    final_position = (final_x, final_y, final_z)

    # Erstelle Modul mit Rotation und finaler Position
    # make_panel() wendet bereits Tilt und Yaw an
    panel = make_panel(
        position=final_position,
        yaw_deg=transform.azimuth_deg,
        tilt_deg=transform.tilt_deg
    )

    return panel


def get_module_bounding_box(
    module_mesh: 'pv.PolyData'
) -> Tuple[float, float, float, float, float, float]:
    """
    Berechnet die Bounding-Box eines transformierten PV-Moduls.

    Diese Funktion berechnet die achsenausgerichtete Bounding-Box (AABB)
    eines PV-Moduls unter Berücksichtigung aller Rotationen und Offsets.
    Die Bounding-Box wird durch die minimalen und maximalen Koordinaten
    in X, Y und Z definiert.

    Args:
        module_mesh: PyVista PolyData Mesh des PV-Moduls

    Returns:
        Tuple mit (min_x, min_y, min_z, max_x, max_y, max_z)

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist
        ValueError: Wenn das Mesh keine Punkte enthält

    Example:
        >>> panel = make_panel(position=(5.0, 3.0, 6.0), yaw_deg=45.0, tilt_deg=25.0)
        >>> bbox = get_module_bounding_box(panel)
        >>> min_x, min_y, min_z, max_x, max_y, max_z = bbox
        >>> print(f"Bounding Box: X=[{min_x:.2f}, {max_x:.2f}], "
        ...       f"Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Prüfe ob Mesh Punkte enthält
    if module_mesh is None or module_mesh.points is None or len(module_mesh.points) == 0:
        raise ValueError("Modul-Mesh enthält keine Punkte")

    # Extrahiere alle Punkte des Meshes
    points = module_mesh.points

    # Berechne minimale und maximale Koordinaten
    min_x = float(np.min(points[:, 0]))
    min_y = float(np.min(points[:, 1]))
    min_z = float(np.min(points[:, 2]))
    max_x = float(np.max(points[:, 0]))
    max_y = float(np.max(points[:, 1]))
    max_z = float(np.max(points[:, 2]))

    return (min_x, min_y, min_z, max_x, max_y, max_z)


def detect_collisions(
    module_meshes: List['pv.PolyData'],
    use_spatial_hashing: bool = True,
    grid_cell_size: float = 2.0
) -> List[Tuple[int, int]]:
    """
    Erkennt Kollisionen zwischen PV-Modulen mittels Bounding-Box Intersection-Test.

    Diese Funktion berechnet die Bounding-Boxes aller Module und prüft auf
    Überschneidungen. Für bessere Performance bei vielen Modulen wird
    Spatial-Hashing verwendet, um nur nahe Module zu vergleichen.

    Args:
        module_meshes: Liste von PyVista PolyData Meshes (PV-Module)
        use_spatial_hashing: Wenn True, verwende Spatial-Hashing für Performance
        grid_cell_size: Größe der Grid-Zellen für Spatial-Hashing (Meter)

    Returns:
        Liste von Kollisions-Paaren als Tupel (index1, index2).
        Leere Liste wenn keine Kollisionen erkannt wurden.
        index1 < index2 für jedes Paar.

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist

    Example:
        >>> panels = [
        ...     make_panel(position=(0.0, 0.0, 0.0)),
        ...     make_panel(position=(0.5, 0.0, 0.0)),  # Überlappung
        ...     make_panel(position=(5.0, 0.0, 0.0))   # Keine Überlappung
        ... ]
        >>> collisions = detect_collisions(panels)
        >>> print(f"Gefundene Kollisionen: {collisions}")
        Gefundene Kollisionen: [(0, 1)]
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Prüfe ob Module vorhanden sind
    if not module_meshes or len(module_meshes) < 2:
        return []

    # Berechne Bounding-Boxes für alle Module
    bounding_boxes = []
    for i, mesh in enumerate(module_meshes):
        try:
            bbox = get_module_bounding_box(mesh)
            bounding_boxes.append((i, bbox))
        except (ValueError, AttributeError):
            # Überspringe ungültige Meshes
            continue

    # Prüfe ob genug gültige Bounding-Boxes vorhanden sind
    if len(bounding_boxes) < 2:
        return []

    collisions = []

    if use_spatial_hashing and len(bounding_boxes) > 10:
        # ====================================================================
        # SPATIAL-HASHING OPTIMIERUNG
        # ====================================================================
        # Erstelle Spatial-Hash-Grid für effiziente Nachbarschaftssuche
        # Dies reduziert die Komplexität von O(n²) auf O(n) im Durchschnitt

        # Erstelle Hash-Grid: Dictionary mit Grid-Zellen-Keys
        # Key: (grid_x, grid_y, grid_z), Value: Liste von Modul-Indizes
        spatial_grid = {}

        # Füge jedes Modul zu allen Grid-Zellen hinzu, die es überlappt
        for idx, bbox in bounding_boxes:
            min_x, min_y, min_z, max_x, max_y, max_z = bbox

            # Berechne Grid-Zellen-Bereiche
            if grid_cell_size != 0:
                grid_min_x = int(math.floor(min_x / grid_cell_size))
            else:
                grid_min_x = 0.0
            if grid_cell_size != 0:
                grid_max_x = int(math.floor(max_x / grid_cell_size))
            else:
                grid_max_x = 0.0
            if grid_cell_size != 0:
                grid_min_y = int(math.floor(min_y / grid_cell_size))
            else:
                grid_min_y = 0.0
            if grid_cell_size != 0:
                grid_max_y = int(math.floor(max_y / grid_cell_size))
            else:
                grid_max_y = 0.0
            if grid_cell_size != 0:
                grid_min_z = int(math.floor(min_z / grid_cell_size))
            else:
                grid_min_z = 0.0
            if grid_cell_size != 0:
                grid_max_z = int(math.floor(max_z / grid_cell_size))
            else:
                grid_max_z = 0.0

            # Füge Modul zu allen überlappenden Grid-Zellen hinzu
            for gx in range(grid_min_x, grid_max_x + 1):
                for gy in range(grid_min_y, grid_max_y + 1):
                    for gz in range(grid_min_z, grid_max_z + 1):
                        cell_key = (gx, gy, gz)
                        if cell_key not in spatial_grid:
                            spatial_grid[cell_key] = []
                        spatial_grid[cell_key].append(idx)

        # Prüfe Kollisionen nur zwischen Modulen in gleichen Grid-Zellen
        checked_pairs = set()

        for cell_modules in spatial_grid.values():
            # Prüfe alle Paare in dieser Zelle
            for i in range(len(cell_modules)):
                for j in range(i + 1, len(cell_modules)):
                    idx1 = cell_modules[i]
                    idx2 = cell_modules[j]

                    # Stelle sicher dass idx1 < idx2
                    if idx1 > idx2:
                        idx1, idx2 = idx2, idx1

                    # Überspringe bereits geprüfte Paare
                    pair_key = (idx1, idx2)
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)

                    # Hole Bounding-Boxes
                    bbox1 = None
                    bbox2 = None
                    for idx, bbox in bounding_boxes:
                        if idx == idx1:
                            bbox1 = bbox
                        if idx == idx2:
                            bbox2 = bbox

                    if bbox1 is None or bbox2 is None:
                        continue

                    # Prüfe Intersection
                    if _bounding_boxes_intersect(bbox1, bbox2):
                        collisions.append((idx1, idx2))

    else:
        # ====================================================================
        # BRUTE-FORCE ANSATZ (für wenige Module)
        # ====================================================================
        # Prüfe alle Paare von Modulen
        for i in range(len(bounding_boxes)):
            for j in range(i + 1, len(bounding_boxes)):
                idx1, bbox1 = bounding_boxes[i]
                idx2, bbox2 = bounding_boxes[j]

                # Prüfe Intersection
                if _bounding_boxes_intersect(bbox1, bbox2):
                    collisions.append((idx1, idx2))

    return collisions


def _bounding_boxes_intersect(
    bbox1: Tuple[float, float, float, float, float, float],
    bbox2: Tuple[float, float, float, float, float, float]
) -> bool:
    """
    Prüft ob zwei Bounding-Boxes sich überschneiden.

    Verwendet den Separating Axis Theorem (SAT) für achsenausgerichtete
    Bounding-Boxes (AABB). Zwei AABBs überschneiden sich, wenn sie sich
    auf allen drei Achsen überschneiden.

    Args:
        bbox1: Erste Bounding-Box (min_x, min_y, min_z, max_x, max_y, max_z)
        bbox2: Zweite Bounding-Box (min_x, min_y, min_z, max_x, max_y, max_z)

    Returns:
        True wenn Bounding-Boxes sich überschneiden, sonst False

    Example:
        >>> bbox1 = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        >>> bbox2 = (0.5, 0.5, 0.5, 1.5, 1.5, 1.5)
        >>> _bounding_boxes_intersect(bbox1, bbox2)
        True
        >>> bbox3 = (2.0, 2.0, 2.0, 3.0, 3.0, 3.0)
        >>> _bounding_boxes_intersect(bbox1, bbox3)
        False
    """
    min_x1, min_y1, min_z1, max_x1, max_y1, max_z1 = bbox1
    min_x2, min_y2, min_z2, max_x2, max_y2, max_z2 = bbox2

    # Prüfe Überschneidung auf X-Achse
    if max_x1 < min_x2 or max_x2 < min_x1:
        return False

    # Prüfe Überschneidung auf Y-Achse
    if max_y1 < min_y2 or max_y2 < min_y1:
        return False

    # Prüfe Überschneidung auf Z-Achse
    if max_z1 < min_z2 or max_z2 < min_z1:
        return False

    # Überschneidung auf allen Achsen -> Kollision
    return True


# ============================================================================
# VERSCHATTUNGS-ANALYSE
# ============================================================================

def calculate_sun_position(
    latitude: float,
    day_of_year: int,
    hour: float
) -> Tuple[float, float]:
    """
    Berechnet die Sonnenposition (Azimuth und Elevation) für einen gegebenen
    Standort, Tag und Uhrzeit.

    Diese Funktion verwendet eine vereinfachte astronomische Berechnung
    basierend auf der Sonnendeklination und dem Stundenwinkel. Für höhere
    Präzision sollte eine spezialisierte Bibliothek wie pvlib verwendet werden.

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
        >>> azimuth, elevation = calculate_sun_position(51.0, 172, 12.0)
        >>> print(f"Azimuth: {azimuth:.1f}°, Elevation: {elevation:.1f}°")
        Azimuth: 180.0°, Elevation: 62.0°
        
        >>> # Morgens am 21. Dezember (Wintersonnenwende)
        >>> azimuth, elevation = calculate_sun_position(51.0, 355, 9.0)
        >>> print(f"Azimuth: {azimuth:.1f}°, Elevation: {elevation:.1f}°")
        Azimuth: 135.0°, Elevation: 12.0°
    """
    if np is None:
        raise RuntimeError("NumPy ist nicht installiert")

    # Validiere Eingaben
    latitude = max(-90.0, min(90.0, latitude))
    day_of_year = max(1, min(365, day_of_year))
    hour = max(0.0, min(24.0, hour))

    # ========================================================================
    # SCHRITT 1: BERECHNE SONNENDEKLINATION
    # ========================================================================
    # Die Sonnendeklination ist der Winkel zwischen den Sonnenstrahlen und
    # der Äquatorebene. Sie variiert zwischen -23.45° (Wintersonnenwende)
    # und +23.45° (Sommersonnenwende).
    
    # Vereinfachte Formel nach Cooper (1969):
    # δ = 23.45° × sin(360° × (284 + N) / 365)
    # wobei N = Tag im Jahr
    
    declination_rad = _deg_to_rad(23.45) * math.sin(
        _deg_to_rad(360.0 * (284 + day_of_year) / 365.0)
    )
    declination_deg = math.degrees(declination_rad)

    # ========================================================================
    # SCHRITT 2: BERECHNE STUNDENWINKEL
    # ========================================================================
    # Der Stundenwinkel ist der Winkel zwischen dem Meridian des Beobachters
    # und dem Meridian der Sonne. Er beträgt 0° um 12:00 Uhr Ortszeit.
    # Pro Stunde ändert sich der Stundenwinkel um 15°.
    
    # Stundenwinkel in Grad: 15° × (Stunde - 12)
    hour_angle_deg = 15.0 * (hour - 12.0)
    hour_angle_rad = _deg_to_rad(hour_angle_deg)

    # ========================================================================
    # SCHRITT 3: BERECHNE SONNEN-ELEVATION (HÖHENWINKEL)
    # ========================================================================
    # Die Elevation ist der Winkel zwischen der Sonne und dem Horizont.
    # Formel: sin(elevation) = sin(latitude) × sin(declination) +
    #                          cos(latitude) × cos(declination) × cos(hour_angle)
    
    latitude_rad = _deg_to_rad(latitude)
    
    sin_elevation = (
        math.sin(latitude_rad) * math.sin(declination_rad) +
        math.cos(latitude_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
    )
    
    # Begrenze auf [-1, 1] um numerische Fehler zu vermeiden
    sin_elevation = max(-1.0, min(1.0, sin_elevation))
    
    elevation_rad = math.asin(sin_elevation)
    elevation_deg = math.degrees(elevation_rad)

    # ========================================================================
    # SCHRITT 4: BERECHNE SONNEN-AZIMUTH (HIMMELSRICHTUNG)
    # ========================================================================
    # Der Azimuth ist der Winkel zwischen Norden und der Projektion der
    # Sonnenstrahlen auf die Horizontalebene (im Uhrzeigersinn).
    # Formel: cos(azimuth) = (sin(declination) - sin(elevation) × sin(latitude)) /
    #                        (cos(elevation) × cos(latitude))
    
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


def calculate_shading_for_module(
    module_mesh: 'pv.PolyData',
    all_modules: List['pv.PolyData'],
    sun_azimuth: float,
    sun_elevation: float,
    module_index: int = -1
) -> float:
    """
    Berechnet den Verschattungsgrad für ein einzelnes PV-Modul mittels
    Ray-Casting zur Sonne.

    Diese Funktion erstellt einen Ray vom Zentrum des Moduls in Richtung
    der Sonne und prüft, ob dieser Ray andere Module schneidet. Der
    Verschattungsgrad wird basierend auf der Anzahl und Größe der
    Verschattungen berechnet.

    Args:
        module_mesh: PyVista PolyData Mesh des zu prüfenden Moduls
        all_modules: Liste aller PyVista PolyData Meshes (PV-Module)
        sun_azimuth: Sonnen-Azimuth in Grad (0° = Norden, 180° = Süden)
        sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        module_index: Index des zu prüfenden Moduls in all_modules
                     (wird übersprungen bei Intersection-Test)

    Returns:
        Verschattungsgrad in Prozent (0.0 = keine Verschattung,
        100.0 = vollständige Verschattung)

    Example:
        >>> panel1 = make_panel(position=(0.0, 0.0, 0.0))
        >>> panel2 = make_panel(position=(2.0, 0.0, 1.0))  # Höher, könnte verschatten
        >>> all_panels = [panel1, panel2]
        >>> # Sonne im Süden, 45° Elevation
        >>> shading = calculate_shading_for_module(panel1, all_panels, 180.0, 45.0, 0)
        >>> print(f"Verschattung: {shading:.1f}%")
        Verschattung: 0.0%
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Prüfe ob Sonne über dem Horizont ist
    if sun_elevation <= 0.0:
        # Sonne unter Horizont -> vollständige Verschattung (Nacht)
        return 100.0

    # ========================================================================
    # SCHRITT 1: BERECHNE MODUL-ZENTRUM
    # ========================================================================
    # Berechne das Zentrum des Moduls als Ausgangspunkt für den Ray
    
    if module_mesh is None or module_mesh.points is None or len(module_mesh.points) == 0:
        return 0.0  # Ungültiges Mesh -> keine Verschattung
    
    # Zentrum = Durchschnitt aller Punkte
    module_center = np.mean(module_mesh.points, axis=0)
    
    # ========================================================================
    # SCHRITT 2: BERECHNE RAY-RICHTUNG ZUR SONNE
    # ========================================================================
    # Konvertiere Azimuth und Elevation zu kartesischen Koordinaten
    # Azimuth: 0° = Norden (+Y), 90° = Osten (+X), 180° = Süden (-Y), 270° = Westen (-X)
    # Elevation: 0° = Horizont, 90° = Zenit (+Z)
    
    azimuth_rad = _deg_to_rad(sun_azimuth)
    elevation_rad = _deg_to_rad(sun_elevation)
    
    # Berechne Richtungsvektor zur Sonne
    # X-Komponente: sin(azimuth) × cos(elevation)
    # Y-Komponente: cos(azimuth) × cos(elevation)  [Norden ist +Y]
    # Z-Komponente: sin(elevation)
    
    ray_direction = np.array([
        math.sin(azimuth_rad) * math.cos(elevation_rad),  # X (Ost-West)
        math.cos(azimuth_rad) * math.cos(elevation_rad),  # Y (Nord-Süd)
        math.sin(elevation_rad)                            # Z (Höhe)
    ])
    
    # Normalisiere Richtungsvektor
    if np != 0:
        ray_direction = ray_direction / np.linalg.norm(ray_direction)
    else:
        ray_direction = 0.0
    
    # ========================================================================
    # SCHRITT 3: PRÜFE INTERSECTION MIT ANDEREN MODULEN
    # ========================================================================
    # Erstelle einen Ray vom Modul-Zentrum zur Sonne und prüfe, ob dieser
    # andere Module schneidet
    
    # Ray-Länge: Ausreichend lang um alle Module zu erreichen (z.B. 100m)
    ray_length = 100.0
    ray_end = module_center + ray_direction * ray_length
    
    # Zähle Intersections mit anderen Modulen
    num_intersections = 0
    total_intersection_distance = 0.0
    
    for i, other_module in enumerate(all_modules):
        # Überspringe das Modul selbst
        if i == module_index:
            continue
        
        # Überspringe ungültige Meshes
        if other_module is None or other_module.points is None or len(other_module.points) == 0:
            continue
        
        # Prüfe ob Ray das andere Modul schneidet
        # Verwende Bounding-Box Test als schnelle Vorprüfung
        try:
            other_bbox = get_module_bounding_box(other_module)
            min_x, min_y, min_z, max_x, max_y, max_z = other_bbox
            
            # Prüfe ob Ray die Bounding-Box schneidet
            # Vereinfachter Test: Prüfe ob Modul-Zentrum zwischen Ray-Start und Ray-End liegt
            # und ob es in der Nähe der Ray-Linie ist
            
            other_center = np.mean(other_module.points, axis=0)
            
            # Berechne Abstand des anderen Moduls vom Ray
            # Verwende Punkt-zu-Linie Abstand
            ray_start = module_center
            
            # Vektor vom Ray-Start zum anderen Modul-Zentrum
            to_other = other_center - ray_start
            
            # Projektion auf Ray-Richtung
            projection_length = np.dot(to_other, ray_direction)
            
            # Prüfe ob Projektion in Ray-Richtung liegt (positiv)
            if projection_length > 0.1:  # Mindestens 10cm entfernt
                # Berechne nächsten Punkt auf Ray
                closest_point_on_ray = ray_start + ray_direction * projection_length
                
                # Berechne Abstand vom anderen Modul zum Ray
                distance_to_ray = np.linalg.norm(other_center - closest_point_on_ray)
                
                # Wenn Abstand kleiner als Modul-Diagonale, zähle als Intersection
                # Modul-Diagonale ≈ sqrt(PV_W² + PV_H²) ≈ 2.0m
                if distance_to_ray < 2.0:
                    num_intersections += 1
                    total_intersection_distance += projection_length
        
        except (ValueError, AttributeError):
            # Überspringe ungültige Meshes
            continue
    
    # ========================================================================
    # SCHRITT 4: BERECHNE VERSCHATTUNGSGRAD
    # ========================================================================
    # Verschattungsgrad basiert auf Anzahl der Intersections
    # Vereinfachte Berechnung: Jede Intersection = 50% Verschattung
    # Maximum: 100%
    
    if num_intersections == 0:
        return 0.0
    elif num_intersections == 1:
        return 50.0
    else:
        return 100.0


def interpolate_color(
    color1: str,
    color2: str,
    factor: float
) -> str:
    """
    Interpoliert zwischen zwei Hex-Farben.

    Args:
        color1: Erste Farbe als Hex-String (z.B. "#00ff00")
        color2: Zweite Farbe als Hex-String (z.B. "#ff0000")
        factor: Interpolationsfaktor (0.0 = color1, 1.0 = color2)

    Returns:
        Interpolierte Farbe als Hex-String

    Example:
        >>> interpolate_color("#00ff00", "#ff0000", 0.5)
        '#7f7f00'
    """
    # Entferne '#' falls vorhanden
    c1 = color1.lstrip('#')
    c2 = color2.lstrip('#')
    
    # Konvertiere zu RGB
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    
    # Begrenze factor auf [0, 1]
    factor = max(0.0, min(1.0, factor))
    
    # Interpoliere
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    # Konvertiere zurück zu Hex
    return f"#{r:02x}{g:02x}{b:02x}"


def visualize_shading(
    plotter: 'pv.Plotter',
    module_meshes: List['pv.PolyData'],
    sun_azimuth: float,
    sun_elevation: float,
    show_legend: bool = True
) -> Dict[int, float]:
    """
    Visualisiert Verschattung durch Einfärben der Module basierend auf
    Verschattungsgrad.

    Diese Funktion berechnet den Verschattungsgrad für jedes Modul und
    färbt es entsprechend ein:
    - Grün (0%): Keine Verschattung
    - Gelb (50%): Teilweise Verschattung
    - Rot (100%): Vollständige Verschattung

    Args:
        plotter: PyVista Plotter-Objekt für die Visualisierung
        module_meshes: Liste von PyVista PolyData Meshes (PV-Module)
        sun_azimuth: Sonnen-Azimuth in Grad (0° = Norden, 180° = Süden)
        sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        show_legend: Wenn True, füge Farbskala-Legende hinzu

    Returns:
        Dictionary mit Modul-Index als Key und Verschattungsgrad (0-100) als Value

    Example:
        >>> plotter = pv.Plotter()
        >>> panels = [
        ...     make_panel(position=(0.0, 0.0, 0.0)),
        ...     make_panel(position=(2.0, 0.0, 1.0))
        ... ]
        >>> shading_values = visualize_shading(plotter, panels, 180.0, 45.0)
        >>> print(f"Modul 0: {shading_values[0]:.1f}% verschattet")
        Modul 0: 0.0% verschattet
    """
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # Prüfe ob Module vorhanden sind
    if not module_meshes or len(module_meshes) == 0:
        return {}

    # Dictionary für Verschattungswerte
    shading_values = {}

    # ========================================================================
    # SCHRITT 1: BERECHNE VERSCHATTUNG FÜR ALLE MODULE
    # ========================================================================
    
    for i, module in enumerate(module_meshes):
        # Berechne Verschattungsgrad
        shading_pct = calculate_shading_for_module(
            module_mesh=module,
            all_modules=module_meshes,
            sun_azimuth=sun_azimuth,
            sun_elevation=sun_elevation,
            module_index=i
        )
        
        shading_values[i] = shading_pct

    # ========================================================================
    # SCHRITT 2: FÄRBE MODULE BASIEREND AUF VERSCHATTUNGSGRAD
    # ========================================================================
    # Farbskala: Grün (0%) → Gelb (50%) → Rot (100%)
    
    for i, module in enumerate(module_meshes):
        shading_pct = shading_values[i]
        
        # Berechne Farbe basierend auf Verschattungsgrad
        if shading_pct < 50.0:
            # Grün → Gelb
            factor = shading_pct / 50.0
            color = interpolate_color("#00ff00", "#ffff00", factor)
        else:
            # Gelb → Rot
            factor = (shading_pct - 50.0) / 50.0
            color = interpolate_color("#ffff00", "#ff0000", factor)
        
        # Füge Modul mit Farbe zum Plotter hinzu
        plotter.add_mesh(module, color=color, opacity=0.9, show_edges=False)

    # ========================================================================
    # SCHRITT 3: FÜGE LEGENDE HINZU (OPTIONAL)
    # ========================================================================
    
    if show_legend:
        # Erstelle Farbskala-Legende
        # PyVista unterstützt scalar bars für kontinuierliche Werte
        # Hier verwenden wir eine vereinfachte Text-Legende
        
        # Berechne Statistiken
        if shading_values:
            min_shading = min(shading_values.values())
            max_shading = max(shading_values.values())
            avg_shading = sum(shading_values.values()) / len(shading_values)
            
            # Füge Text-Annotation hinzu
            legend_text = (
                f"Verschattungs-Analyse\n"
                f"Sonnenstand: Az={sun_azimuth:.0f}°, El={sun_elevation:.0f}°\n"
                f"Min: {min_shading:.1f}%\n"
                f"Max: {max_shading:.1f}%\n"
                f"Durchschnitt: {avg_shading:.1f}%\n"
                f"\n"
                f"Farbskala:\n"
                f"Grün = 0% (keine Verschattung)\n"
                f"Gelb = 50% (teilweise)\n"
                f"Rot = 100% (vollständig)"
            )
            
            # Füge Text zum Plotter hinzu (oben links)
            plotter.add_text(
                legend_text,
                position='upper_left',
                font_size=10,
                color='black'
            )

    return shading_values


# ============================================================================
# PV-MODUL-PLATZIERUNGS-ALGORITHMEN
# ============================================================================

def grid_positions(
    area_length: float,
    area_width: float,
    margin: float = 0.25,
    spacing: float = 0.25,
    panel_width: float = PV_W,
    panel_height: float = PV_H
) -> List[Tuple[float, float]]:
    """
    Berechnet Rasterposit ionen für gleichmäßige PV-Modul-Verteilung.

    Die Funktion berechnet ein Raster von Positionen für PV-Module auf einer
    rechteckigen Fläche unter Berücksichtigung von Randabständen und
    Modul-Zwischenräumen.

    Args:
        area_length: Länge der verfügbaren Fläche in X-Richtung (Meter)
        area_width: Breite der verfügbaren Fläche in Y-Richtung (Meter)
        margin: Randabstand zu allen Seiten (Meter), Standard: 0.25m
        spacing: Abstand zwischen Modulen (Meter), Standard: 0.25m
        panel_width: Breite eines Moduls in X-Richtung (Meter)
        panel_height: Höhe eines Moduls in Y-Richtung (Meter)

    Returns:
        Liste von (x, y) Positionen relativ zum Flächenzentrum.
        Leere Liste wenn keine Module passen.

    Example:
        >>> positions = grid_positions(10.0, 6.0)
        >>> len(positions)  # Anzahl der möglichen Modulpositionen
        24
    """
    # Berechne nutzbare Fläche (abzüglich Randabstände)
    usable_length = area_length - 2 * margin
    usable_width = area_width - 2 * margin

    # Prüfe ob überhaupt ein Modul passt
    if usable_length < panel_width or usable_width < panel_height:
        return []

    # Berechne Anzahl der Spalten (X-Richtung)
    # Formel: (usable_length - panel_width) / (panel_width + spacing) + 1
    num_cols = int(
        (usable_length - panel_width) / (panel_width + spacing) + 1
    )
    num_cols = max(0, num_cols)

    # Berechne Anzahl der Reihen (Y-Richtung)
    # Formel: (usable_width - panel_height) / (panel_height + spacing) + 1
    num_rows = int(
        (usable_width - panel_height) / (panel_height + spacing) + 1
    )
    num_rows = max(0, num_rows)

    # Wenn keine Module passen
    if num_cols == 0 or num_rows == 0:
        return []

    # Berechne tatsächlich belegte Fläche
    total_cols_width = num_cols * panel_width + (num_cols - 1) * spacing
    total_rows_width = num_rows * panel_height + (num_rows - 1) * spacing

    # Berechne Start-Offsets (zentriert in nutzbarer Fläche)
    start_x = -total_cols_width / 2
    start_y = -total_rows_width / 2

    # Generiere Rasterposit ionen
    positions = []
    for row in range(num_rows):
        for col in range(num_cols):
            # Berechne Position des Modul-Zentrums
            x = start_x + col * (panel_width + spacing) + panel_width / 2
            y = start_y + row * (panel_height + spacing) + panel_height / 2
            positions.append((x, y))

    return positions


def place_panels_auto(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    roof_type: str = "Flachdach",
    inclination_deg: float = 0.0,
    base_z: float = 0.0,
    margin: float = 0.25,
    spacing: float = 0.25
) -> List['pv.PolyData']:
    """
    Platziert PV-Module automatisch auf einer Dachfläche.

    Berechnet die maximale Modul-Kapazität basierend auf der Dachfläche
    und platziert Module in Reihen und Spalten. Bei geneigten Dächern
    werden Module parallel zur Dachfläche platziert.

    Args:
        roof_length: Dachlänge in X-Richtung (Meter)
        roof_width: Dachbreite in Y-Richtung (Meter)
        module_quantity: Gewünschte Anzahl der Module
        roof_type: Dachtyp (für spezielle Behandlung)
        inclination_deg: Dachneigung in Grad (0-90)
        base_z: Basis-Z-Höhe für Modul-Platzierung
        margin: Randabstand (Meter)
        spacing: Abstand zwischen Modulen (Meter)

    Returns:
        Liste von PyVista PolyData Meshes (PV-Module)

    Example:
        >>> panels = place_panels_auto(10.0, 6.0, 20)
        >>> len(panels)
        20
    """
    if pv is None:
        raise RuntimeError("PyVista ist nicht installiert")

    # Berechne Rasterposit ionen
    positions_2d = grid_positions(
        area_length=roof_length,
        area_width=roof_width,
        margin=margin,
        spacing=spacing
    )

    # Berechne maximale Kapazität
    max_capacity = len(positions_2d)

    # Begrenze auf verfügbare Positionen
    num_to_place = min(module_quantity, max_capacity)

    # Erstelle Module
    panels = []

    # Bestimme Tilt basierend auf Dachtyp
    if roof_type == "Flachdach":
        # Flachdach: Module liegen flach (werden später aufgeständert)
        tilt = 0.0
    else:
        # Geneigte Dächer: Module parallel zur Dachfläche
        tilt = inclination_deg

    # Berechne Z-Offset für geneigte Dächer
    # Bei geneigten Dächern müssen Module auf der Dachfläche liegen
    if roof_type == "Satteldach" or roof_type == "Walmdach":
        # Für Satteldach: Module auf einer Seite (negative Y-Seite)
        # Z-Höhe variiert mit Y-Position
        pass  # Wird pro Modul berechnet
    elif roof_type == "Pultdach":
        # Pultdach: Lineare Z-Variation
        pass  # Wird pro Modul berechnet
    else:
        # Flachdach, Zeltdach, etc.: Konstante Z-Höhe
        pass

    # Platziere Module
    for i in range(num_to_place):
        x, y = positions_2d[i]

        # Berechne Z-Position basierend auf Dachtyp
        if roof_type == "Satteldach" or roof_type == "Walmdach":
            # Satteldach: Z steigt vom Rand zur Mitte
            # Vereinfachung: Module auf vorderer Dachfläche (y < 0)
            if inclination_deg > 0:
                inclination_rad = _deg_to_rad(inclination_deg)
                # Abstand von Traufe (y = -roof_width/2)
                dist_from_eave = y + roof_width / 2
                z_offset = dist_from_eave * math.tan(inclination_rad)
                z = base_z + z_offset
            else:
                z = base_z
        elif roof_type == "Pultdach":
            # Pultdach: Z steigt linear von vorne nach hinten
            if inclination_deg > 0:
                inclination_rad = _deg_to_rad(inclination_deg)
                # Abstand von vorderer Kante (y = -roof_width/2)
                dist_from_front = y + roof_width / 2
                z_offset = dist_from_front * math.tan(inclination_rad)
                z = base_z + z_offset
            else:
                z = base_z
        else:
            # Flachdach, Zeltdach, etc.
            z = base_z

        # Erstelle Modul
        panel = make_panel(
            position=(x, y, z),
            yaw_deg=0.0,
            tilt_deg=tilt
        )
        panels.append(panel)

    return panels


def place_panels_manual(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    removed_indices: List[int],
    roof_type: str = "Flachdach",
    inclination_deg: float = 0.0,
    base_z: float = 0.0,
    margin: float = 0.25,
    spacing: float = 0.25
) -> List['pv.PolyData']:
    """
    Platziert PV-Module manuell mit Filterung basierend auf removed_indices.

    Erstellt zunächst alle möglichen Modulpositionen und entfernt dann
    die Module an den angegebenen Indizes. Indizes werden gegen verfügbare
    Positionen validiert.

    Args:
        roof_length: Dachlänge in X-Richtung (Meter)
        roof_width: Dachbreite in Y-Richtung (Meter)
        module_quantity: Gewünschte Anzahl der Module
        removed_indices: Liste der zu entfernenden Modul-Indizes (0-basiert)
        roof_type: Dachtyp (für spezielle Behandlung)
        inclination_deg: Dachneigung in Grad (0-90)
        base_z: Basis-Z-Höhe für Modul-Platzierung
        margin: Randabstand (Meter)
        spacing: Abstand zwischen Modulen (Meter)

    Returns:
        Liste von PyVista PolyData Meshes (PV-Module)
        Module an removed_indices werden ausgelassen

    Example:
        >>> panels = place_panels_manual(
        ...     10.0, 6.0, 20, removed_indices=[0, 1, 5]
        ... )
        >>> len(panels)
        17
    """
    if pv is None:
        raise RuntimeError("PyVista ist nicht installiert")

    # Berechne Rasterposit ionen
    positions_2d = grid_positions(
        area_length=roof_length,
        area_width=roof_width,
        margin=margin,
        spacing=spacing
    )

    # Berechne maximale Kapazität
    max_capacity = len(positions_2d)

    # Begrenze auf verfügbare Positionen
    num_to_place = min(module_quantity, max_capacity)

    # Validiere und normalisiere removed_indices
    valid_removed = set()
    if removed_indices:
        for idx in removed_indices:
            # Prüfe ob Index im gültigen Bereich liegt
            if 0 <= idx < num_to_place:
                valid_removed.add(idx)
            # Ignoriere ungültige Indizes stillschweigend

    # Erstelle Module
    panels = []

    # Bestimme Tilt basierend auf Dachtyp
    if roof_type == "Flachdach":
        tilt = 0.0
    else:
        tilt = inclination_deg

    # Platziere Module (außer entfernte)
    for i in range(num_to_place):
        # Überspringe entfernte Module
        if i in valid_removed:
            continue

        x, y = positions_2d[i]

        # Berechne Z-Position basierend auf Dachtyp
        if roof_type == "Satteldach" or roof_type == "Walmdach":
            if inclination_deg > 0:
                inclination_rad = _deg_to_rad(inclination_deg)
                dist_from_eave = y + roof_width / 2
                z_offset = dist_from_eave * math.tan(inclination_rad)
                z = base_z + z_offset
            else:
                z = base_z
        elif roof_type == "Pultdach":
            if inclination_deg > 0:
                inclination_rad = _deg_to_rad(inclination_deg)
                dist_from_front = y + roof_width / 2
                z_offset = dist_from_front * math.tan(inclination_rad)
                z = base_z + z_offset
            else:
                z = base_z
        else:
            z = base_z

        # Erstelle Modul
        panel = make_panel(
            position=(x, y, z),
            yaw_deg=0.0,
            tilt_deg=tilt
        )
        panels.append(panel)

    return panels


def place_panels_flat_roof(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    mounting_type: str = "south",
    removed_indices: List[int] = None,
    base_z: float = 0.0,
    margin: float = 0.25,
    spacing: float = 0.25,
    custom_azimuth: float = 0.0,
    custom_tilt: float = 15.0
) -> List['pv.PolyData']:
    """
    Platziert PV-Module auf Flachdach mit Aufständerung.

    Implementiert verschiedene Aufständerungstypen:
    - "south": Süd-Aufständerung (15° Neigung, 0° Yaw)
    - "east-west": Ost-West-Aufständerung (10° Neigung, alternierender Yaw)
    - "south-east": Süd-Ost-Aufständerung (15° Neigung, 45° Yaw)
    - "south-west": Süd-West-Aufständerung (15° Neigung, 315° Yaw)
    - "custom": Individueller Modus (verwendet custom_azimuth und custom_tilt)

    Args:
        roof_length: Dachlänge in X-Richtung (Meter)
        roof_width: Dachbreite in Y-Richtung (Meter)
        module_quantity: Gewünschte Anzahl der Module
        mounting_type: Aufständerungstyp ("south", "east-west", "south-east", "south-west", "custom")
        removed_indices: Liste der zu entfernenden Modul-Indizes (optional)
        base_z: Basis-Z-Höhe für Modul-Platzierung
        margin: Randabstand (Meter)
        spacing: Abstand zwischen Modulen (Meter)
        custom_azimuth: Benutzerdefinierter Azimuth für "custom" Modus (0-360°)
        custom_tilt: Benutzerdefinierte Neigung für "custom" Modus (0-90°)

    Returns:
        Liste von PyVista PolyData Meshes (PV-Module)

    Example:
        >>> # Süd-Aufständerung
        >>> panels = place_panels_flat_roof(
        ...     10.0, 6.0, 20, mounting_type="south"
        ... )
        >>> # Ost-West-Aufständerung
        >>> panels = place_panels_flat_roof(
        ...     10.0, 6.0, 20, mounting_type="east-west"
        ... )
        >>> # Süd-Ost-Aufständerung
        >>> panels = place_panels_flat_roof(
        ...     10.0, 6.0, 20, mounting_type="south-east"
        ... )
        >>> # Individueller Modus
        >>> panels = place_panels_flat_roof(
        ...     10.0, 6.0, 20, mounting_type="custom",
        ...     custom_azimuth=30.0, custom_tilt=20.0
        ... )
    """
    if pv is None:
        raise RuntimeError("PyVista ist nicht installiert")

    # Normalisiere mounting_type
    mounting_type = mounting_type.lower()

    # Bestimme Aufständerungs-Parameter
    if mounting_type == "east-west":
        # Ost-West: 10° Neigung, alternierender Yaw
        tilt = 10.0
        use_alternating_yaw = True
        yaw = 0.0  # Wird pro Modul gesetzt
    elif mounting_type == "south-east":
        # Süd-Ost: 15° Neigung, 45° Yaw (Süd-Ost)
        tilt = 15.0
        use_alternating_yaw = False
        yaw = 45.0
    elif mounting_type == "south-west":
        # Süd-West: 15° Neigung, 315° Yaw (Süd-West)
        tilt = 15.0
        use_alternating_yaw = False
        yaw = 315.0
    elif mounting_type == "custom":
        # Individuell: Benutzerdefinierte Werte
        # Validiere und verwende custom_azimuth und custom_tilt
        tilt = max(0.0, min(90.0, custom_tilt))
        use_alternating_yaw = False
        yaw = custom_azimuth % 360.0  # Normalisiere auf 0-360°
    else:
        # Süd (Standard): 15° Neigung, 0° Yaw
        tilt = 15.0
        use_alternating_yaw = False
        yaw = 0.0

    # Berechne Rasterposit ionen
    # Berechne optimalen Reihenabstand basierend auf Aufständerungstyp
    # Der Reihenabstand muss Verschattung zwischen Reihen vermeiden
    
    # Formel für Reihenabstand: d = h / tan(sun_elevation_min)
    # wobei h = Modulhöhe * sin(tilt)
    # Für Deutschland (Breitengrad ~51°): Minimale Sonnenhöhe im Winter ~15°
    # Vereinfachte Berechnung: d ≈ Modulhöhe * sin(tilt) * 3.0
    
    if use_alternating_yaw:
        # Für Ost-West: Berechne Positionen mit erhöhtem Reihenabstand
        # Reihenabstand für 10° Neigung
        module_height = 1.76  # PV_H
        row_spacing_factor = module_height * math.sin(_deg_to_rad(tilt)) * 3.0
        
        positions_2d = grid_positions(
            area_length=roof_length,
            area_width=roof_width,
            margin=margin,
            spacing=spacing
        )
        # Filtere Positionen: Nur jede zweite Reihe für Ost-West
        # (um Verschattung zu vermeiden)
        if positions_2d:
            # Sortiere nach Y
            positions_sorted = sorted(positions_2d, key=lambda p: p[1])
            # Extrahiere eindeutige Y-Werte
            y_values = sorted(set(p[1] for p in positions_sorted))
            # Wähle jede zweite Reihe
            selected_y = set(y_values[::2])
            # Filtere Positionen
            positions_2d = [
                p for p in positions_2d if p[1] in selected_y
            ]
    elif mounting_type in ["south-east", "south-west"]:
        # Für Süd-Ost und Süd-West: Berechne optimalen Reihenabstand
        # Reihenabstand für 15° Neigung
        module_height = 1.76  # PV_H
        row_spacing_factor = module_height * math.sin(_deg_to_rad(tilt)) * 3.0
        
        # Verwende größeren Spacing für Reihen
        adjusted_spacing = max(spacing, row_spacing_factor)
        
        positions_2d = grid_positions(
            area_length=roof_length,
            area_width=roof_width,
            margin=margin,
            spacing=adjusted_spacing
        )
    else:
        # Süd oder Custom: Normale Rasterposit ionen mit optimiertem Reihenabstand
        module_height = 1.76  # PV_H
        row_spacing_factor = module_height * math.sin(_deg_to_rad(tilt)) * 3.0
        
        # Verwende größeren Spacing für Reihen
        adjusted_spacing = max(spacing, row_spacing_factor)
        
        positions_2d = grid_positions(
            area_length=roof_length,
            area_width=roof_width,
            margin=margin,
            spacing=adjusted_spacing
        )

    # Berechne maximale Kapazität
    max_capacity = len(positions_2d)

    # Begrenze auf verfügbare Positionen
    num_to_place = min(module_quantity, max_capacity)

    # Validiere removed_indices
    valid_removed = set()
    if removed_indices:
        for idx in removed_indices:
            if 0 <= idx < num_to_place:
                valid_removed.add(idx)

    # Erstelle Module
    panels = []

    for i in range(num_to_place):
        # Überspringe entfernte Module
        if i in valid_removed:
            continue

        x, y = positions_2d[i]

        # Bestimme Yaw basierend auf Aufständerungstyp
        if use_alternating_yaw:
            # Ost-West: Alternierender Yaw
            # Gerade Indizes: -90° (Osten)
            # Ungerade Indizes: 90° (Westen)
            if i % 2 == 0:
                module_yaw = -90.0  # Osten
            else:
                module_yaw = 90.0   # Westen
        else:
            # Alle anderen Modi: Verwende den festgelegten Yaw
            # (south: 0°, south-east: 45°, south-west: 315°, custom: wird separat gesetzt)
            module_yaw = yaw

        # Z-Position: Berechne so dass Unterseite des Moduls auf dem Dach liegt
        # Bei geneigten Modulen muss die Erhöhung die Rotation berücksichtigen
        # Die Unterseite des geneigten Moduls soll auf base_z liegen
        
        # Berechne vertikale Projektion der Modulhöhe nach Rotation
        # Modul wird um Y-Achse gekippt, daher ändert sich die Z-Höhe
        elevation = (PV_H / 2) * math.sin(_deg_to_rad(tilt))
        
        # Z-Position: Dachoberkante + Elevation + kleiner Abstand
        z = base_z + elevation + 0.10  # Unterseite + 10cm Abstand

        # Erstelle Modul
        panel = make_panel(
            position=(x, y, z),
            yaw_deg=module_yaw,
            tilt_deg=tilt
        )
        panels.append(panel)

    return panels


# ============================================================================
# HAUPTFUNKTION: SZENEN-ERSTELLUNG
# ============================================================================

def build_scene(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    off_screen: bool = False,
    selected_modules: List[int] = None
) -> Tuple['pv.Plotter', Dict[str, List['pv.PolyData']]]:
    """
    Erstellt die komplette 3D-Szene mit Gebäude, Dach und PV-Modulen.

    Diese Hauptfunktion orchestriert die gesamte Szenen-Erstellung:
    1. Initialisiert PyVista Plotter
    2. Erstellt Bodenplatte und Gebäudewände
    3. Generiert Dach basierend auf roof_type
    4. Rotiert Szene basierend auf Ausrichtung
    5. Platziert Kompass-Pfeil
    6. Berechnet und platziert PV-Module auf Hauptdach
    7. Fügt optional Garage und Fassadenmodule hinzu

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        off_screen: Wenn True, Off-Screen Rendering (für Screenshots)
        selected_modules: Liste der ausgewählten Modul-Indizes (für Hervorhebung)

    Returns:
        Tuple aus:
        - PyVista Plotter-Objekt mit der kompletten Szene
        - Dictionary mit Panel-Listen:
          {"main": [...], "garage": [...], "facade": [...]}

    Raises:
        RuntimeError: Wenn PyVista nicht verfügbar ist

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> plotter, panels = build_scene(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout,
        ...     selected_modules=[0, 1, 2]
        ... )
    """
    # Initialisiere selected_modules wenn None
    if selected_modules is None:
        selected_modules = []
    if pv is None or np is None:
        raise RuntimeError("PyVista oder NumPy ist nicht installiert")

    # ========================================================================
    # TASK 5.1: SZENEN-INITIALISIERUNG
    # ========================================================================

    # Erstelle PyVista Plotter mit weißem Hintergrund
    plotter = pv.Plotter(off_screen=off_screen)
    plotter.set_background("white")

    # Extrahiere Gebäudedimensionen
    length = dims.length_m
    width = dims.width_m
    wall_height = dims.wall_height_m

    # Generiere Bodenplatte (3x Gebäudegröße, Farbe #f3f3f5)
    ground_length = length * 3
    ground_width = width * 3
    ground_thickness = 0.05  # 5cm dick

    ground = make_box(
        length=ground_length,
        width=ground_width,
        height=ground_thickness,
        center=(0.0, 0.0, 0.0),
        origin_at_bottom=True
    )
    plotter.add_mesh(ground, color="#f3f3f5", show_edges=False)

    # Erstelle Gebäudewände (Farbe #e7e7ea)
    walls = make_box(
        length=length,
        width=width,
        height=wall_height,
        center=(0.0, 0.0, 0.0),
        origin_at_bottom=True
    )
    plotter.add_mesh(walls, color="#e7e7ea", show_edges=False)

    # ========================================================================
    # TASK 5.2: DACH-GENERIERUNG UND ROTATION
    # ========================================================================

    # Extrahiere Dachparameter aus project_data
    inclination_deg = _safe_get_roof_inclination_deg(project_data)
    covering = _safe_get_roof_covering(project_data)
    roof_color = _roof_color_from_covering(covering)
    orientation = _safe_get_orientation(project_data)

    # Wähle Dachform basierend auf roof_type
    roof_type_normalized = roof_type.strip() if roof_type else "Flachdach"

    if roof_type_normalized == "Flachdach":
        roof = make_roof_flat(length, width, wall_height)
    elif roof_type_normalized == "Satteldach":
        roof = make_roof_gable(length, width, wall_height, inclination_deg)
    elif roof_type_normalized == "Walmdach" or roof_type_normalized == "Krüppelwalmdach":
        roof = make_roof_hip(length, width, wall_height, inclination_deg)
    elif roof_type_normalized == "Pultdach":
        roof = make_roof_pent(length, width, wall_height, inclination_deg)
    elif roof_type_normalized == "Zeltdach":
        roof = make_roof_pyramid(length, width, wall_height, inclination_deg)
    else:
        # Fallback: Flachdach
        roof = make_roof_flat(length, width, wall_height)

    # Implementiere Gebäude-Rotation basierend auf Ausrichtung
    # 0° = Süd, -90° = Ost, 90° = West, 180° = Nord
    rotation_angle = 0.0
    if orientation == "Süd":
        rotation_angle = 0.0
    elif orientation == "Ost":
        rotation_angle = -90.0
    elif orientation == "West":
        rotation_angle = 90.0
    elif orientation == "Nord":
        rotation_angle = 180.0

    # Rotiere Dach um Z-Achse
    if abs(rotation_angle) > 0.01:
        rotation_rad = _deg_to_rad(rotation_angle)
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)
        rotation_matrix = np.array([
            [cos_r, -sin_r, 0],
            [sin_r, cos_r, 0],
            [0, 0, 1]
        ])
        roof.points = roof.points @ rotation_matrix.T

    # Füge Dach zum Plotter hinzu
    plotter.add_mesh(roof, color=roof_color, show_edges=False)

    # ========================================================================
    # TASK 5.3: KOMPASS-PLATZIERUNG
    # ========================================================================

    # Erstelle roten Pfeil-Mesh für Kompass
    # Platziere Kompass an Position (Länge*1.6, Breite*1.6, 0.1m)
    compass_x = length * 1.6
    compass_y = width * 1.6
    compass_z = 0.1

    # Erstelle Pfeil mit PyVista Arrow
    # Richtung nach Norden (0, -1, 0)
    arrow_start = np.array([compass_x, compass_y, compass_z])
    arrow_direction = np.array([0.0, -1.0, 0.0])
    arrow_scale = 1.5

    compass_arrow = pv.Arrow(
        start=arrow_start,
        direction=arrow_direction,
        scale=arrow_scale
    )
    plotter.add_mesh(compass_arrow, color="red", show_edges=False)

    # ========================================================================
    # TASK 5.4: PV-MODUL-PLATZIERUNG AUF HAUPTDACH
    # ========================================================================

    # Initialisiere Panel-Listen
    panels_main = []
    panels_garage = []
    panels_facade = []

    # Berechne Basis-Z-Höhe für Module (auf Dach)
    if roof_type_normalized == "Flachdach":
        base_z = wall_height + 0.12  # Flachdach-Dicke
    else:
        base_z = wall_height

    # Extrahiere mounting_mode und custom-Parameter aus layout_config
    # Wenn AdvancedLayoutConfig verwendet wird, nutze die erweiterten Parameter
    if isinstance(layout_config, AdvancedLayoutConfig):
        mounting_type = layout_config.mounting_mode
        custom_azimuth = layout_config.custom_azimuth
        custom_tilt = layout_config.custom_tilt
    else:
        # Fallback für LayoutConfig: Standard Süd-Aufständerung
        mounting_type = "south"
        custom_azimuth = 0.0
        custom_tilt = 15.0
    
    # Platziere Module basierend auf Belegungsmodus
    if layout_config.mode == "manual":
        # Manuelle Belegung mit removed_indices
        if roof_type_normalized == "Flachdach":
            # Flachdach: Verwende Aufständerung mit konfigurierbarem Modus
            panels_main = place_panels_flat_roof(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                mounting_type=mounting_type,
                removed_indices=layout_config.removed_indices,
                base_z=base_z,
                custom_azimuth=custom_azimuth,
                custom_tilt=custom_tilt
            )
        else:
            # Geneigte Dächer: Manuelle Platzierung
            panels_main = place_panels_manual(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                removed_indices=layout_config.removed_indices,
                roof_type=roof_type_normalized,
                inclination_deg=inclination_deg,
                base_z=base_z
            )
    else:
        # Automatische Belegung
        if roof_type_normalized == "Flachdach":
            # Flachdach: Verwende Aufständerung mit konfigurierbarem Modus
            panels_main = place_panels_flat_roof(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                mounting_type=mounting_type,
                base_z=base_z,
                custom_azimuth=custom_azimuth,
                custom_tilt=custom_tilt
            )
        else:
            # Geneigte Dächer: Automatische Platzierung
            panels_main = place_panels_auto(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                roof_type=roof_type_normalized,
                inclination_deg=inclination_deg,
                base_z=base_z
            )

    # Rotiere Module mit Gebäude
    if abs(rotation_angle) > 0.01:
        rotation_rad = _deg_to_rad(rotation_angle)
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)
        rotation_matrix = np.array([
            [cos_r, -sin_r, 0],
            [sin_r, cos_r, 0],
            [0, 0, 1]
        ])
        for panel in panels_main:
            panel.points = panel.points @ rotation_matrix.T

    # Füge Module zum Plotter hinzu (schwarze Farbe, ausgewählte in orange)
    for idx, panel in enumerate(panels_main):
        # Prüfe ob Modul ausgewählt ist
        if idx in selected_modules:
            # Hervorhebung: Orange/Gelb für ausgewählte Module
            plotter.add_mesh(panel, color="#FFA500", show_edges=True, edge_color="yellow", line_width=2)
        else:
            # Standard: Schwarz
            plotter.add_mesh(panel, color="black", show_edges=False)

    # ========================================================================
    # TASK 5.5: GARAGE-HINZUFÜGUNG
    # ========================================================================

    # Berechne fehlende Module
    placed_count = len(panels_main)
    missing_count = module_quantity - placed_count

    # Prüfe use_garage Flag und fehlende Module
    if layout_config.use_garage and missing_count > 0:
        # Extrahiere Garage-Dimensionen
        garage_length, garage_width, garage_height = layout_config.garage_dims

        # Erstelle Garagengebäude
        garage_x = length / 2 + garage_length / 2 + 1.0  # 1m Abstand
        garage_y = 0.0
        garage_walls = make_box(
            length=garage_length,
            width=garage_width,
            height=garage_height,
            center=(garage_x, garage_y, 0.0),
            origin_at_bottom=True
        )
        plotter.add_mesh(garage_walls, color="#ececee", show_edges=False)

        # Erstelle Garagendach (Flachdach)
        garage_roof = make_roof_flat(
            garage_length,
            garage_width,
            garage_height
        )
        # Verschiebe Garagendach zur Position
        garage_roof.translate([garage_x, garage_y, 0.0], inplace=True)
        plotter.add_mesh(garage_roof, color=roof_color, show_edges=False)

        # Platziere verbleibende Module auf Garagendach
        garage_base_z = garage_height + 0.12  # Flachdach-Dicke
        panels_garage = place_panels_flat_roof(
            roof_length=garage_length,
            roof_width=garage_width,
            module_quantity=missing_count,
            mounting_type="south",
            base_z=garage_base_z
        )

        # Verschiebe Garage-Module zur Garage-Position
        for panel in panels_garage:
            panel.translate([garage_x, garage_y, 0.0], inplace=True)

        # Rotiere Garage-Module mit Gebäude
        if abs(rotation_angle) > 0.01:
            rotation_rad = _deg_to_rad(rotation_angle)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)
            rotation_matrix = np.array([
                [cos_r, -sin_r, 0],
                [sin_r, cos_r, 0],
                [0, 0, 1]
            ])
            # Rotiere Garage-Wände und Dach
            garage_walls.points = garage_walls.points @ rotation_matrix.T
            garage_roof.points = garage_roof.points @ rotation_matrix.T
            # Rotiere Garage-Module
            for panel in panels_garage:
                panel.points = panel.points @ rotation_matrix.T

        # Füge Garage-Module zum Plotter hinzu
        for idx, panel in enumerate(panels_garage):
            # Berechne globalen Index (nach Hauptdach-Modulen)
            global_idx = len(panels_main) + idx
            
            # Prüfe ob Modul ausgewählt ist
            if global_idx in selected_modules:
                # Hervorhebung: Orange/Gelb für ausgewählte Module
                plotter.add_mesh(panel, color="#FFA500", show_edges=True, edge_color="yellow", line_width=2)
            else:
                # Standard: Schwarz
                plotter.add_mesh(panel, color="black", show_edges=False)

        # Aktualisiere fehlende Module
        placed_count += len(panels_garage)
        missing_count = module_quantity - placed_count

    # ========================================================================
    # TASK 5.6: FASSADEN-BELEGUNG
    # ========================================================================

    # Prüfe use_facade Flag und verbleibende fehlende Module
    if layout_config.use_facade and missing_count > 0:
        # Identifiziere Südfassade basierend auf Ausrichtung
        # Südfassade ist immer die Seite, die nach Süden zeigt
        # Nach Rotation: Südfassade ist bei y = -width/2 (vor Rotation)

        # Berechne Fassaden-Dimensionen
        facade_length = length
        facade_height = wall_height

        # Berechne Raster-Positionen für Fassade (vertikal)
        # Module werden vertikal (90° Neigung) platziert
        facade_positions = grid_positions(
            area_length=facade_length,
            area_width=facade_height,
            margin=0.25,
            spacing=0.25,
            panel_width=PV_W,
            panel_height=PV_H
        )

        # Begrenze auf fehlende Module
        num_facade_panels = min(missing_count, len(facade_positions))

        # Platziere Module an Fassade
        facade_y = -width / 2 - 0.05  # 5cm vor der Wand
        for i in range(num_facade_panels):
            x, z = facade_positions[i]
            # Z ist hier die Höhe an der Wand

            # Erstelle Modul mit 90° Neigung (vertikal)
            panel = make_panel(
                position=(x, facade_y, z),
                yaw_deg=0.0,
                tilt_deg=90.0
            )
            panels_facade.append(panel)

        # Rotiere Fassaden-Module mit Gebäude
        if abs(rotation_angle) > 0.01:
            rotation_rad = _deg_to_rad(rotation_angle)
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)
            rotation_matrix = np.array([
                [cos_r, -sin_r, 0],
                [sin_r, cos_r, 0],
                [0, 0, 1]
            ])
            for panel in panels_facade:
                panel.points = panel.points @ rotation_matrix.T

        # Füge Fassaden-Module zum Plotter hinzu
        for idx, panel in enumerate(panels_facade):
            # Berechne globalen Index (nach Hauptdach- und Garage-Modulen)
            global_idx = len(panels_main) + len(panels_garage) + idx
            
            # Prüfe ob Modul ausgewählt ist
            if global_idx in selected_modules:
                # Hervorhebung: Orange/Gelb für ausgewählte Module
                plotter.add_mesh(panel, color="#FFA500", show_edges=True, edge_color="yellow", line_width=2)
            else:
                # Standard: Schwarz
                plotter.add_mesh(panel, color="black", show_edges=False)

    # ========================================================================
    # TASK 5.7: FINALISIERE build_scene() RETURN
    # ========================================================================

    # Gebe Plotter und Dictionary mit Panel-Listen zurück
    panels_dict = {
        "main": panels_main,
        "garage": panels_garage,
        "facade": panels_facade
    }

    return plotter, panels_dict


# ============================================================================
# EXPORT-FUNKTIONEN
# ============================================================================

@trace_pv3d
def render_image_bytes(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    width: int = 1600,
    height: int = 1000
) -> bytes:
    """
    Erstellt einen Off-Screen Screenshot der 3D-Szene als PNG-Bytes.

    Diese Funktion rendert die 3D-Szene ohne sichtbares Fenster und
    konvertiert das Ergebnis zu PNG-Bytes für PDF-Einbettung oder Download.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        width: Screenshot-Breite in Pixeln (Standard: 1600)
        height: Screenshot-Höhe in Pixeln (Standard: 1000)

    Returns:
        PNG-Bytes des Screenshots. Leere Bytes (b"") bei Fehler.

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> png_bytes = render_image_bytes(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout
        ... )
        >>> len(png_bytes) > 0
        True
    """
    try:
        # Importiere Pillow für PNG-Konvertierung
        from PIL import Image
        import io

        # Erstelle Szene mit Off-Screen Rendering
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            off_screen=True
        )

        # Setze Auflösung
        plotter.window_size = [width, height]

        # Verwende isometrische Kameraperspektive
        # Positioniere Kamera für gute Übersicht
        plotter.camera_position = 'iso'
        
        # Zoom anpassen für bessere Ansicht
        plotter.camera.zoom(1.2)

        # Erstelle Screenshot
        screenshot = plotter.screenshot(return_img=True)

        # Schließe Plotter
        plotter.close()

        # Konvertiere NumPy Array zu PIL Image
        if screenshot is not None:
            img = Image.fromarray(screenshot)
            
            # Konvertiere zu PNG-Bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
        else:
            return b""

    except Exception as e:
        # Fehlerbehandlung: Gebe leere Bytes zurück
        print(f"Fehler beim Rendering: {e}")
        return b""


def export_stl(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    filepath: str
) -> bool:
    """
    Exportiert das 3D-Modell als STL-Datei.

    Merged alle Meshes (Gebäude, Dach, PV-Module) zu einem kombinierten
    Mesh und speichert es als STL-Datei.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        filepath: Pfad zur Ausgabe-STL-Datei

    Returns:
        True bei Erfolg, False bei Fehler

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> success = export_stl(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout,
        ...     filepath="output.stl"
        ... )
    """
    try:
        if pv is None:
            raise RuntimeError("PyVista ist nicht installiert")

        # Erstelle Szene mit Off-Screen Rendering
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            off_screen=True
        )

        # Sammle alle Meshes aus dem Plotter
        meshes_to_merge = []
        
        # Extrahiere alle Meshes aus dem Plotter
        # PyVista Plotter speichert Actors in einem Dictionary
        for actor in plotter.renderer.actors.values():
            if hasattr(actor, 'mapper') and actor.mapper is not None:
                mapper_input = actor.mapper.GetInput()
                if mapper_input is not None:
                    # Konvertiere VTK zu PyVista PolyData
                    mesh = pv.wrap(mapper_input)
                    meshes_to_merge.append(mesh)

        # Schließe Plotter
        plotter.close()

        # Merge alle Meshes zu einem kombinierten Mesh
        if meshes_to_merge:
            combined_mesh = meshes_to_merge[0].copy()
            for mesh in meshes_to_merge[1:]:
                combined_mesh = combined_mesh.merge(mesh)

            # Speichere als STL
            combined_mesh.save(filepath, binary=True)
            return True
        else:
            print("Keine Meshes zum Exportieren gefunden")
            return False

    except Exception as e:
        print(f"Fehler beim STL-Export: {e}")
        import traceback
        traceback.print_exc()
        return False


def export_gltf(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    filepath: str
) -> bool:
    """
    Exportiert das 3D-Modell als glTF/glb-Datei.

    Konvertiert PyVista Meshes zu trimesh Meshes und erstellt eine
    trimesh Scene für den glTF-Export.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        filepath: Pfad zur Ausgabe-glTF/glb-Datei

    Returns:
        True bei Erfolg, False bei Fehler

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> success = export_gltf(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout,
        ...     filepath="output.glb"
        ... )
    """
    try:
        import trimesh
        
        if pv is None:
            raise RuntimeError("PyVista ist nicht installiert")

        # Erstelle Szene mit Off-Screen Rendering
        plotter, panels = build_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            off_screen=True
        )

        # Sammle alle Meshes aus dem Plotter
        trimesh_meshes = []
        
        # Extrahiere alle Meshes aus dem Plotter und konvertiere zu trimesh
        for actor in plotter.renderer.actors.values():
            if hasattr(actor, 'mapper') and actor.mapper is not None:
                mapper_input = actor.mapper.GetInput()
                if mapper_input is not None:
                    # Konvertiere VTK zu PyVista PolyData
                    pv_mesh = pv.wrap(mapper_input)
                    
                    # Konvertiere PyVista Mesh zu trimesh Mesh
                    # Extrahiere Vertices und Faces
                    vertices = pv_mesh.points
                    
                    # PyVista faces sind im Format [n, v1, v2, ..., vn, n, ...]
                    # Konvertiere zu trimesh Format (nur Vertex-Indizes)
                    faces = []
                    i = 0
                    pv_faces = pv_mesh.faces
                    while i < len(pv_faces):
                        n_points = pv_faces[i]
                        if n_points == 3:  # Dreieck
                            face = [pv_faces[i+1], pv_faces[i+2], pv_faces[i+3]]
                            faces.append(face)
                        elif n_points == 4:  # Viereck - in 2 Dreiecke aufteilen
                            # Dreieck 1
                            face1 = [pv_faces[i+1], pv_faces[i+2], pv_faces[i+3]]
                            faces.append(face1)
                            # Dreieck 2
                            face2 = [pv_faces[i+1], pv_faces[i+3], pv_faces[i+4]]
                            faces.append(face2)
                        i += n_points + 1
                    
                    if len(faces) > 0:
                        # Erstelle trimesh Mesh
                        tm_mesh = trimesh.Trimesh(
                            vertices=vertices,
                            faces=faces
                        )
                        trimesh_meshes.append(tm_mesh)

        # Schließe Plotter
        plotter.close()

        # Erstelle trimesh Scene und exportiere als glTF
        if trimesh_meshes:
            scene = trimesh.Scene(trimesh_meshes)
            
            # Exportiere als glTF/glb
            # Wenn Dateiname auf .glb endet, exportiere als binäres glTF
            scene.export(filepath)
            return True
        else:
            print("Keine Meshes zum Exportieren gefunden")
            return False

    except Exception as e:
        print(f"Fehler beim glTF-Export: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# OPTIMIERUNGS-ASSISTENT
# ============================================================================

def generate_south_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str = "Flachdach"
) -> AdvancedLayoutConfig:
    """
    Generiert eine Konfiguration mit Süd-Aufständerung.

    Diese Funktion erstellt eine optimierte Konfiguration für maximale
    Energieausbeute durch Süd-Ausrichtung aller Module.

    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (Standard: "Flachdach")

    Returns:
        AdvancedLayoutConfig mit Süd-Aufständerung

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> config = generate_south_config(dims, 20)
        >>> config.mounting_mode
        'south'
    """
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        removed_indices=[],
        mounting_mode="south",
        custom_azimuth=0.0,
        custom_tilt=15.0,
        enable_collision_detection=True,
        enable_shading_analysis=False
    )
    
    return config


def generate_east_west_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str = "Flachdach"
) -> AdvancedLayoutConfig:
    """
    Generiert eine Konfiguration mit Ost-West-Aufständerung.

    Diese Funktion erstellt eine Konfiguration für gleichmäßige
    Energieverteilung über den Tag durch alternierende Ost-West-Ausrichtung.

    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (Standard: "Flachdach")

    Returns:
        AdvancedLayoutConfig mit Ost-West-Aufständerung

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> config = generate_east_west_config(dims, 20)
        >>> config.mounting_mode
        'east-west'
    """
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        removed_indices=[],
        mounting_mode="east-west",
        custom_azimuth=0.0,
        custom_tilt=10.0,
        enable_collision_detection=True,
        enable_shading_analysis=False
    )
    
    return config


def generate_south_east_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str = "Flachdach"
) -> AdvancedLayoutConfig:
    """
    Generiert eine Konfiguration mit Süd-Ost-Aufständerung.

    Diese Funktion erstellt eine Konfiguration für optimale
    Energieausbeute in den Morgenstunden durch Süd-Ost-Ausrichtung.

    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (Standard: "Flachdach")

    Returns:
        AdvancedLayoutConfig mit Süd-Ost-Aufständerung

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> config = generate_south_east_config(dims, 20)
        >>> config.mounting_mode
        'south-east'
    """
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=False,
        use_facade=False,
        removed_indices=[],
        mounting_mode="south-east",
        custom_azimuth=45.0,
        custom_tilt=15.0,
        enable_collision_detection=True,
        enable_shading_analysis=False
    )
    
    return config


def generate_mixed_config(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str = "Flachdach"
) -> AdvancedLayoutConfig:
    """
    Generiert eine gemischte Konfiguration mit Garage und Fassade.

    Diese Funktion erstellt eine Konfiguration, die Garage und Fassade
    nutzt, um die maximale Anzahl von Modulen unterzubringen.

    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (Standard: "Flachdach")

    Returns:
        AdvancedLayoutConfig mit gemischter Konfiguration

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> config = generate_mixed_config(dims, 50)
        >>> config.use_garage
        True
        >>> config.use_facade
        True
    """
    config = AdvancedLayoutConfig(
        mode="auto",
        use_garage=True,
        use_facade=True,
        removed_indices=[],
        mounting_mode="south",
        custom_azimuth=0.0,
        custom_tilt=15.0,
        enable_collision_detection=True,
        enable_shading_analysis=False
    )
    
    return config


def evaluate_config(
    config: AdvancedLayoutConfig,
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str,
    optimization_goal: str = "max_modules"
) -> float:
    """
    Bewertet eine Konfiguration basierend auf verschiedenen Kriterien.

    Diese Funktion berechnet einen Score (0-100) für eine gegebene
    Konfiguration basierend auf dem Optimierungsziel. Höhere Scores
    bedeuten bessere Konfigurationen.

    Bewertungskriterien:
    - Modulanzahl: Wie viele Module können platziert werden
    - Verschattung: Wie stark sind Module verschattet (geschätzt)
    - Ausrichtung: Wie optimal ist die Ausrichtung zur Sonne

    Args:
        config: Zu bewertende AdvancedLayoutConfig
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp
        optimization_goal: Optimierungsziel ("max_modules", "max_yield", "balanced")

    Returns:
        Score zwischen 0.0 und 100.0 (höher ist besser)

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> config = generate_south_config(dims, 20)
        >>> score = evaluate_config(config, dims, 20, "Flachdach", "max_yield")
        >>> 0.0 <= score <= 100.0
        True
    """
    score = 0.0
    
    # ========================================================================
    # KRITERIUM 1: MODULANZAHL
    # ========================================================================
    # Schätze wie viele Module mit dieser Konfiguration platziert werden können
    
    # Berechne verfügbare Fläche auf Hauptdach
    roof_area = building_dims.length_m * building_dims.width_m
    
    # Schätze Modul-Kapazität basierend auf Aufständerungstyp
    # Verschiedene Aufständerungstypen benötigen unterschiedlich viel Platz
    module_area = PV_W * PV_H  # ~1.85 m²
    
    if config.mounting_mode == "east-west":
        # Ost-West benötigt mehr Platz wegen Reihenabstand
        # Reduziere Kapazität um ~40%
        capacity_factor = 0.6
    elif config.mounting_mode in ["south-east", "south-west"]:
        # Süd-Ost/West benötigt etwas mehr Platz
        # Reduziere Kapazität um ~20%
        capacity_factor = 0.8
    else:
        # Süd oder Custom: Standard-Kapazität
        # Reduziere Kapazität um ~10% für Randabstände
        capacity_factor = 0.9
    
    # Berechne geschätzte Kapazität
    if module_area != 0:
        estimated_capacity = int((roof_area / module_area) * capacity_factor)
    else:
        estimated_capacity = 0.0
    
    # Füge Garage-Kapazität hinzu wenn aktiviert
    if config.use_garage:
        garage_length, garage_width, _ = config.garage_dims
        garage_area = garage_length * garage_width
        if module_area != 0:
            garage_capacity = int((garage_area / module_area) * 0.9)
        else:
            garage_capacity = 0.0
        estimated_capacity += garage_capacity
    
    # Füge Fassaden-Kapazität hinzu wenn aktiviert
    if config.use_facade:
        facade_area = building_dims.length_m * building_dims.wall_height_m
        if module_area != 0:
            facade_capacity = int((facade_area / module_area) * 0.7)  # Weniger effizient
        else:
            facade_capacity = 0.0
        estimated_capacity += facade_capacity
    
    # Berechne Modulanzahl-Score
    # 100% wenn alle gewünschten Module passen, linear abfallend
    if estimated_capacity >= target_modules:
        module_count_score = 100.0
    else:
        if target_modules != 0:
            module_count_score = (estimated_capacity / target_modules) * 100.0
        else:
            module_count_score = 0.0
    
    # ========================================================================
    # KRITERIUM 2: VERSCHATTUNG (GESCHÄTZT)
    # ========================================================================
    # Schätze Verschattungsgrad basierend auf Aufständerungstyp
    
    if config.mounting_mode == "south":
        # Süd-Aufständerung: Minimale Verschattung bei optimaler Auslegung
        shading_penalty = 5.0  # 5% Verschattung
    elif config.mounting_mode == "east-west":
        # Ost-West: Etwas mehr Verschattung durch alternierende Ausrichtung
        shading_penalty = 10.0  # 10% Verschattung
    elif config.mounting_mode in ["south-east", "south-west"]:
        # Süd-Ost/West: Moderate Verschattung
        shading_penalty = 7.0  # 7% Verschattung
    else:
        # Custom: Unbekannt, nehme mittleren Wert an
        shading_penalty = 10.0
    
    # Fassaden-Module haben höhere Verschattung
    if config.use_facade:
        shading_penalty += 5.0
    
    # Berechne Verschattungs-Score (100 - Penalty)
    shading_score = max(0.0, 100.0 - shading_penalty)
    
    # ========================================================================
    # KRITERIUM 3: AUSRICHTUNG (OPTIMAL FÜR ERTRAG)
    # ========================================================================
    # Bewerte wie optimal die Ausrichtung für Energieertrag ist
    # Süd-Ausrichtung ist optimal für Deutschland (Breitengrad ~51°)
    
    if config.mounting_mode == "south":
        # Süd: Optimal für Jahresertrag
        orientation_score = 100.0
    elif config.mounting_mode == "south-east":
        # Süd-Ost: Gut für Morgenertrag, leicht suboptimal für Jahresertrag
        orientation_score = 90.0
    elif config.mounting_mode == "south-west":
        # Süd-West: Gut für Nachmittagsertrag, leicht suboptimal für Jahresertrag
        orientation_score = 90.0
    elif config.mounting_mode == "east-west":
        # Ost-West: Gleichmäßiger Tagesertrag, aber geringerer Jahresertrag
        orientation_score = 85.0
    else:
        # Custom: Bewerte basierend auf Azimuth
        # Optimal bei 0° (Süd), abfallend zu 90° (West) und 270° (Ost)
        azimuth = config.custom_azimuth % 360.0
        
        # Berechne Abweichung von Süd (0° oder 360°)
        if azimuth <= 180.0:
            deviation = azimuth
        else:
            deviation = 360.0 - azimuth
        
        # Score: 100% bei 0°, linear abfallend zu 50% bei 90°
        orientation_score = max(50.0, 100.0 - (deviation / 90.0) * 50.0)
    
    # ========================================================================
    # GESAMTSCORE BASIEREND AUF OPTIMIERUNGSZIEL
    # ========================================================================
    
    if optimization_goal == "max_modules":
        # Maximiere Modulanzahl
        # Gewichtung: 70% Modulanzahl, 20% Verschattung, 10% Ausrichtung
        score = (
            module_count_score * 0.7 +
            shading_score * 0.2 +
            orientation_score * 0.1
        )
    
    elif optimization_goal == "max_yield":
        # Maximiere Ertrag (Energieausbeute)
        # Gewichtung: 30% Modulanzahl, 30% Verschattung, 40% Ausrichtung
        score = (
            module_count_score * 0.3 +
            shading_score * 0.3 +
            orientation_score * 0.4
        )
    
    elif optimization_goal == "balanced":
        # Ausgewogen zwischen Anzahl und Ertrag
        # Gewichtung: 50% Modulanzahl, 25% Verschattung, 25% Ausrichtung
        score = (
            module_count_score * 0.5 +
            shading_score * 0.25 +
            orientation_score * 0.25
        )
    
    else:
        # Unbekanntes Ziel: Verwende balanced
        score = (
            module_count_score * 0.5 +
            shading_score * 0.25 +
            orientation_score * 0.25
        )
    
    # Begrenze Score auf [0, 100]
    score = max(0.0, min(100.0, score))
    
    return score


def optimize_layout(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str = "Flachdach",
    optimization_goal: str = "max_modules"
) -> List[Tuple[AdvancedLayoutConfig, float]]:
    """
    Findet optimale Layout-Konfigurationen durch Generierung und Bewertung
    verschiedener Strategien.

    Diese Hauptfunktion des Optimierungs-Assistenten generiert 4-5
    verschiedene Konfigurationen, bewertet sie basierend auf dem
    Optimierungsziel und gibt die Top 3 zurück.

    Generierte Strategien:
    1. Süd-Aufständerung (optimal für Jahresertrag)
    2. Ost-West-Aufständerung (gleichmäßiger Tagesertrag)
    3. Süd-Ost-Aufständerung (optimal für Morgenertrag)
    4. Gemischte Konfiguration mit Garage und Fassade (maximale Kapazität)

    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Anzahl der Module
        roof_type: Dachtyp (Standard: "Flachdach")
        optimization_goal: Optimierungsziel ("max_modules", "max_yield", "balanced")

    Returns:
        Liste der Top 3 Konfigurationen als Tupel (config, score),
        sortiert nach Score (höchster zuerst)

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> top_configs = optimize_layout(dims, 20, "Flachdach", "max_yield")
        >>> len(top_configs)
        3
        >>> config1, score1 = top_configs[0]
        >>> score1 >= top_configs[1][1]  # Erste hat höchsten Score
        True
    """
    configurations = []
    
    # ========================================================================
    # STRATEGIE 1: SÜD-AUFSTÄNDERUNG
    # ========================================================================
    # Optimal für maximalen Jahresertrag in Deutschland
    
    config_south = generate_south_config(building_dims, target_modules, roof_type)
    score_south = evaluate_config(
        config_south,
        building_dims,
        target_modules,
        roof_type,
        optimization_goal
    )
    configurations.append((config_south, score_south, "Süd-Aufständerung"))
    
    # ========================================================================
    # STRATEGIE 2: OST-WEST-AUFSTÄNDERUNG
    # ========================================================================
    # Gleichmäßiger Tagesertrag, gut für Eigenverbrauch
    
    config_east_west = generate_east_west_config(building_dims, target_modules, roof_type)
    score_east_west = evaluate_config(
        config_east_west,
        building_dims,
        target_modules,
        roof_type,
        optimization_goal
    )
    configurations.append((config_east_west, score_east_west, "Ost-West-Aufständerung"))
    
    # ========================================================================
    # STRATEGIE 3: SÜD-OST-AUFSTÄNDERUNG
    # ========================================================================
    # Optimal für Morgenertrag
    
    config_south_east = generate_south_east_config(building_dims, target_modules, roof_type)
    score_south_east = evaluate_config(
        config_south_east,
        building_dims,
        target_modules,
        roof_type,
        optimization_goal
    )
    configurations.append((config_south_east, score_south_east, "Süd-Ost-Aufständerung"))
    
    # ========================================================================
    # STRATEGIE 4: GEMISCHTE KONFIGURATION
    # ========================================================================
    # Maximale Kapazität durch Nutzung von Garage und Fassade
    
    config_mixed = generate_mixed_config(building_dims, target_modules, roof_type)
    score_mixed = evaluate_config(
        config_mixed,
        building_dims,
        target_modules,
        roof_type,
        optimization_goal
    )
    configurations.append((config_mixed, score_mixed, "Gemischt (Garage + Fassade)"))
    
    # ========================================================================
    # SORTIERE UND GEBE TOP 3 ZURÜCK
    # ========================================================================
    # Sortiere nach Score (höchster zuerst)
    configurations.sort(key=lambda x: x[1], reverse=True)
    
    # Gebe Top 3 zurück (ohne Namen)
    top_3 = [(config, score) for config, score, _ in configurations[:3]]
    
    return top_3


# ============================================================================
# ERWEITERTE EXPORT-FUNKTIONEN (TASK 18)
# ============================================================================

def export_module_details_csv(
    module_transforms: Dict[int, 'ModuleTransform'],
    module_positions: List[Tuple[float, float, float]],
    shading_values: Dict[int, float] = None,
    filepath: str = None
) -> str:
    """
    Exportiert Modul-Details als CSV-Datei.

    Erstellt eine CSV-Datei mit detaillierten Informationen zu jedem PV-Modul:
    Index, Position (X, Y, Z), Azimuth, Neigung, Gruppe und Verschattungsgrad.

    Args:
        module_transforms: Dictionary mit ModuleTransform-Objekten (Key: Index)
        module_positions: Liste von (x, y, z) Positionen für alle Module
        shading_values: Optional - Dictionary mit Verschattungswerten (Key: Index, Value: Prozent)
        filepath: Optional - Pfad zur Ausgabe-CSV-Datei. Wenn None, wird CSV-String zurückgegeben.

    Returns:
        CSV-String mit Modul-Details

    Example:
        >>> transforms = {
        ...     0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=15.0),
        ...     1: ModuleTransform(index=1, azimuth_deg=90.0, tilt_deg=20.0)
        ... }
        >>> positions = [(0.0, 0.0, 6.0), (2.0, 0.0, 6.0)]
        >>> csv_data = export_module_details_csv(transforms, positions)
    """
    import csv
    import io

    # Erstelle CSV in Memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Schreibe Header
    writer.writerow(['Index', 'X', 'Y', 'Z', 'Azimuth', 'Tilt', 'Group', 'Shading%'])

    # Schreibe Daten für jedes Modul
    for i, position in enumerate(module_positions):
        x, y, z = position

        # Hole Transform-Daten wenn vorhanden
        if i in module_transforms:
            transform = module_transforms[i]
            azimuth = transform.azimuth_deg
            tilt = transform.tilt_deg
            group = transform.group_id if transform.group_id else ""
        else:
            # Fallback: Standard-Werte
            azimuth = 0.0
            tilt = 15.0
            group = ""

        # Hole Verschattungswert wenn vorhanden
        if shading_values and i in shading_values:
            shading = shading_values[i]
        else:
            shading = 0.0

        # Schreibe Zeile
        writer.writerow([
            i,
            f"{x:.2f}",
            f"{y:.2f}",
            f"{z:.2f}",
            f"{azimuth:.1f}",
            f"{tilt:.1f}",
            group,
            f"{shading:.1f}"
        ])

    # Hole CSV-String
    csv_string = output.getvalue()
    output.close()

    # Speichere in Datei wenn filepath angegeben
    if filepath:
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_string)
        except Exception as e:
            print(f"Fehler beim Speichern der CSV-Datei: {e}")

    return csv_string


def export_layout_json(
    layout_config: 'AdvancedLayoutConfig',
    filepath: str = None
) -> str:
    """
    Exportiert die komplette Layout-Konfiguration als JSON.

    Serialisiert die AdvancedLayoutConfig zu JSON für Export und späteren Import.

    Args:
        layout_config: AdvancedLayoutConfig-Objekt mit kompletter Konfiguration
        filepath: Optional - Pfad zur Ausgabe-JSON-Datei. Wenn None, wird JSON-String zurückgegeben.

    Returns:
        JSON-String der Konfiguration

    Example:
        >>> config = AdvancedLayoutConfig(mode="manual", mounting_mode="south-east")
        >>> json_data = export_layout_json(config, "layout.json")
    """
    # Konvertiere zu JSON
    json_string = layout_config.to_json()

    # Speichere in Datei wenn filepath angegeben
    if filepath:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_string)
        except Exception as e:
            print(f"Fehler beim Speichern der JSON-Datei: {e}")

    return json_string


def import_layout_json(
    json_string: str = None,
    filepath: str = None
) -> 'AdvancedLayoutConfig':
    """
    Importiert eine Layout-Konfiguration aus JSON.

    Lädt eine AdvancedLayoutConfig aus einem JSON-String oder einer JSON-Datei.
    Validiert die importierten Daten.

    Args:
        json_string: Optional - JSON-String der Konfiguration
        filepath: Optional - Pfad zur JSON-Datei

    Returns:
        AdvancedLayoutConfig-Objekt

    Raises:
        ValueError: Wenn JSON ungültig ist oder weder json_string noch filepath angegeben
        FileNotFoundError: Wenn filepath nicht existiert

    Example:
        >>> config = import_layout_json(filepath="layout.json")
        >>> print(f"Modus: {config.mode}, Mounting: {config.mounting_mode}")
    """
    # Prüfe ob json_string oder filepath angegeben
    if json_string is None and filepath is None:
        raise ValueError("Entweder json_string oder filepath muss angegeben werden")

    # Lade JSON aus Datei wenn filepath angegeben
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json_string = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON-Datei nicht gefunden: {filepath}")
        except Exception as e:
            raise ValueError(f"Fehler beim Laden der JSON-Datei: {e}")

    # Validiere und parse JSON
    try:
        config = AdvancedLayoutConfig.from_json(json_string)
        return config
    except ValueError as e:
        raise ValueError(f"Ungültige JSON-Konfiguration: {e}")


def export_multi_view_screenshots(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    output_dir: str = ".",
    base_filename: str = "view",
    resolution: Tuple[int, int] = (1600, 1000)
) -> Dict[str, bytes]:
    """
    Erstellt Screenshots aus 4 verschiedenen Perspektiven.

    Rendert die 3D-Szene aus 4 Kameraperspektiven:
    - Isometrisch (Standard-Ansicht)
    - Top (von oben)
    - Süd (von Süden)
    - Ost (von Osten)

    Erstellt eine ZIP-Datei mit allen Screenshots.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        output_dir: Ausgabe-Verzeichnis für ZIP-Datei
        base_filename: Basis-Dateiname für Screenshots
        resolution: Auflösung (Breite, Höhe) in Pixeln

    Returns:
        Dictionary mit View-Namen als Keys und PNG-Bytes als Values
        {"isometric": bytes, "top": bytes, "south": bytes, "east": bytes}

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> views = export_multi_view_screenshots(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout
        ... )
        >>> print(f"Erstellt {len(views)} Screenshots")
    """
    try:
        from PIL import Image
        import io
        import zipfile
        import os

        if pv is None or np is None:
            raise RuntimeError("PyVista oder NumPy ist nicht installiert")

        views = {}
        width, height = resolution

        # Berechne Kamera-Positionen basierend auf Gebäudedimensionen
        length = dims.length_m
        width_dim = dims.width_m
        wall_height = dims.wall_height_m

        # Zentrum der Szene
        center = (0.0, 0.0, wall_height / 2)

        # Kamera-Distanz (abhängig von Gebäudegröße)
        max_dim = max(length, width_dim, wall_height)
        camera_distance = max_dim * 3.0

        # ====================================================================
        # VIEW 1: ISOMETRISCH (Standard-Ansicht)
        # ====================================================================
        try:
            from PIL import Image
            import io
            
            # Erstelle Szene (build_scene erstellt eigenen Plotter)
            plotter, panels = build_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                off_screen=True
            )

            # Setze Fenstergröße
            plotter.window_size = [width, height]

            # Setze isometrische Kamera
            # Position: Schräg von vorne-rechts-oben
            camera_pos = (
                center[0] + camera_distance * 0.7,
                center[1] - camera_distance * 0.7,
                center[2] + camera_distance * 0.5
            )
            plotter.camera_position = [camera_pos, center, (0, 0, 1)]

            # Rendere Screenshot als NumPy Array
            screenshot = plotter.screenshot(return_img=True)
            plotter.close()

            # Konvertiere zu PNG-Bytes
            if screenshot is not None:
                img = Image.fromarray(screenshot)
                img_bytes_io = io.BytesIO()
                img.save(img_bytes_io, format='PNG')
                views["isometric"] = img_bytes_io.getvalue()
            else:
                views["isometric"] = b""

        except Exception as e:
            print(f"Fehler beim Rendern der isometrischen Ansicht: {e}")
            import traceback
            traceback.print_exc()
            views["isometric"] = b""

        # ====================================================================
        # VIEW 2: TOP (von oben)
        # ====================================================================
        try:
            from PIL import Image
            import io
            
            # Erstelle Szene (build_scene erstellt eigenen Plotter)
            plotter, panels = build_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                off_screen=True
            )

            # Setze Fenstergröße
            plotter.window_size = [width, height]

            # Setze Top-Kamera (direkt von oben)
            camera_pos = (center[0], center[1], center[2] + camera_distance)
            plotter.camera_position = [camera_pos, center, (0, 1, 0)]

            # Rendere Screenshot als NumPy Array
            screenshot = plotter.screenshot(return_img=True)
            plotter.close()

            # Konvertiere zu PNG-Bytes
            if screenshot is not None:
                img = Image.fromarray(screenshot)
                img_bytes_io = io.BytesIO()
                img.save(img_bytes_io, format='PNG')
                views["top"] = img_bytes_io.getvalue()
            else:
                views["top"] = b""

        except Exception as e:
            print(f"Fehler beim Rendern der Top-Ansicht: {e}")
            import traceback
            traceback.print_exc()
            views["top"] = b""

        # ====================================================================
        # VIEW 3: SÜD (von Süden)
        # ====================================================================
        try:
            from PIL import Image
            import io
            
            # Erstelle Szene (build_scene erstellt eigenen Plotter)
            plotter, panels = build_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                off_screen=True
            )

            # Setze Fenstergröße
            plotter.window_size = [width, height]

            # Setze Süd-Kamera (von Süden = negative Y-Richtung)
            camera_pos = (center[0], center[1] - camera_distance, center[2] + camera_distance * 0.3)
            plotter.camera_position = [camera_pos, center, (0, 0, 1)]

            # Rendere Screenshot als NumPy Array
            screenshot = plotter.screenshot(return_img=True)
            plotter.close()

            # Konvertiere zu PNG-Bytes
            if screenshot is not None:
                img = Image.fromarray(screenshot)
                img_bytes_io = io.BytesIO()
                img.save(img_bytes_io, format='PNG')
                views["south"] = img_bytes_io.getvalue()
            else:
                views["south"] = b""

        except Exception as e:
            print(f"Fehler beim Rendern der Süd-Ansicht: {e}")
            import traceback
            traceback.print_exc()
            views["south"] = b""

        # ====================================================================
        # VIEW 4: OST (von Osten)
        # ====================================================================
        try:
            from PIL import Image
            import io
            
            # Erstelle Szene (build_scene erstellt eigenen Plotter)
            plotter, panels = build_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                off_screen=True
            )

            # Setze Fenstergröße
            plotter.window_size = [width, height]

            # Setze Ost-Kamera (von Osten = positive X-Richtung)
            camera_pos = (center[0] + camera_distance, center[1], center[2] + camera_distance * 0.3)
            plotter.camera_position = [camera_pos, center, (0, 0, 1)]

            # Rendere Screenshot als NumPy Array
            screenshot = plotter.screenshot(return_img=True)
            plotter.close()

            # Konvertiere zu PNG-Bytes
            if screenshot is not None:
                img = Image.fromarray(screenshot)
                img_bytes_io = io.BytesIO()
                img.save(img_bytes_io, format='PNG')
                views["east"] = img_bytes_io.getvalue()
            else:
                views["east"] = b""

        except Exception as e:
            print(f"Fehler beim Rendern der Ost-Ansicht: {e}")
            import traceback
            traceback.print_exc()
            views["east"] = b""

        # ====================================================================
        # ERSTELLE ZIP-DATEI MIT ALLEN SCREENSHOTS
        # ====================================================================
        try:
            zip_filename = os.path.join(output_dir, f"{base_filename}_multi_view.zip")

            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for view_name, img_bytes in views.items():
                    if img_bytes:
                        # Füge Bild zur ZIP hinzu
                        zipf.writestr(f"{base_filename}_{view_name}.png", img_bytes)

            print(f"Multi-View Screenshots gespeichert in: {zip_filename}")

        except Exception as e:
            print(f"Fehler beim Erstellen der ZIP-Datei: {e}")

        return views

    except Exception as e:
        print(f"Fehler beim Export der Multi-View Screenshots: {e}")
        import traceback
        traceback.print_exc()
        return {}


def export_360_animation(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    filepath: str = "animation_360.gif",
    frames: int = 36,
    resolution: Tuple[int, int] = (800, 600),
    duration_ms: int = 100,
    progress_callback: Optional[Callable] = None
) -> bytes:
    """
    Erstellt eine 360° Rotations-Animation als GIF.

    Rendert die 3D-Szene aus verschiedenen Winkeln (360° Rotation um Z-Achse)
    und erstellt ein animiertes GIF.

    Args:
        project_data: Projektdaten-Dictionary mit Gebäudeinformationen
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Gewünschte Anzahl der PV-Module
        layout_config: LayoutConfig mit Belegungskonfiguration
        filepath: Pfad zur Ausgabe-GIF-Datei
        frames: Anzahl der Frames (36 = 10° pro Frame)
        resolution: Auflösung (Breite, Höhe) in Pixeln
        duration_ms: Dauer pro Frame in Millisekunden

    Returns:
        GIF-Bytes

    Example:
        >>> dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        >>> layout = LayoutConfig(mode="auto")
        >>> gif_bytes = export_360_animation(
        ...     project_data={},
        ...     dims=dims,
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=layout,
        ...     filepath="rotation.gif"
        ... )
    """
    try:
        from PIL import Image
        import io

        if pv is None or np is None:
            raise RuntimeError("PyVista oder NumPy ist nicht installiert")

        width, height = resolution
        images = []

        # Berechne Kamera-Parameter
        length = dims.length_m
        width_dim = dims.width_m
        wall_height = dims.wall_height_m

        # Zentrum der Szene
        center = (0.0, 0.0, wall_height / 2)

        # Kamera-Distanz
        max_dim = max(length, width_dim, wall_height)
        camera_distance = max_dim * 2.5

        # Kamera-Höhe (leicht erhöht für bessere Ansicht)
        camera_height_offset = camera_distance * 0.4

        print(f"Erstelle 360° Animation mit {frames} Frames...")

        # Rendere Frames
        for i in range(frames):
            try:
                # Berechne Rotationswinkel (0° bis 360°)
                if frames != 0:
                    angle_deg = (360.0 / frames) * i
                else:
                    angle_deg = 0.0
                angle_rad = _deg_to_rad(angle_deg)

                # Berechne Kamera-Position (kreist um Zentrum)
                camera_x = center[0] + camera_distance * math.cos(angle_rad)
                camera_y = center[1] + camera_distance * math.sin(angle_rad)
                camera_z = center[2] + camera_height_offset

                camera_pos = (camera_x, camera_y, camera_z)

                # Erstelle Szene (build_scene erstellt eigenen Plotter)
                plotter, panels = build_scene(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_type,
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    off_screen=True
                )

                # Setze Kamera-Position für diesen Frame
                plotter.camera_position = [camera_pos, center, (0, 0, 1)]

                # Rendere Frame als Screenshot
                img_array = plotter.screenshot(return_img=True, window_size=[width, height])
                plotter.close()

                # Konvertiere NumPy Array zu PIL Image
                if img_array is not None:
                    img = Image.fromarray(img_array)
                    images.append(img)

                # Fortschrittsanzeige
                if (i + 1) % 6 == 0:
                    progress = ((i + 1) / frames) * 100
                    print(f"  Fortschritt: {progress:.0f}% ({i + 1}/{frames} Frames)")

            except Exception as e:
                print(f"Fehler beim Rendern von Frame {i}: {e}")
                continue

        # Erstelle GIF
        if images:
            print(f"Speichere GIF mit {len(images)} Frames...")

            # Speichere als GIF
            output = io.BytesIO()
            images[0].save(
                output,
                format='GIF',
                save_all=True,
                append_images=images[1:],
                duration=duration_ms,
                loop=0,  # Endlos-Schleife
                optimize=False  # Schneller, aber größere Datei
            )

            gif_bytes = output.getvalue()
            output.close()

            # Speichere in Datei
            try:
                with open(filepath, 'wb') as f:
                    f.write(gif_bytes)
                print(f"360° Animation gespeichert: {filepath}")
            except Exception as e:
                print(f"Fehler beim Speichern der GIF-Datei: {e}")

            return gif_bytes
        else:
            print("Keine Frames zum Erstellen der Animation")
            return b""

    except Exception as e:
        print(f"Fehler beim Export der 360° Animation: {e}")
        import traceback
        traceback.print_exc()
        return b""


# ============================================================================
# OPTIMIERUNGS-ASSISTENT
# ============================================================================

def optimize_layout(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str,
    optimization_goal: str = "balanced"
) -> List[Tuple[AdvancedLayoutConfig, float]]:
    """
    Generiert und bewertet verschiedene PV-Layout-Konfigurationen.
    
    FIX 2024: Neu implementiert für funktionierenden Optimierungs-Assistenten.
    ENHANCED 2024: Detailliertes Logging und robuste Fehlerbehandlung.
    
    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Modulanzahl
        roof_type: Dachform
        optimization_goal: "max_modules", "max_yield", oder "balanced"
    
    Returns:
        Liste von (Konfiguration, Score) Tupeln, sortiert nach Score (höchster zuerst)
    """
    import traceback
    
    try:
        # Validiere Eingabeparameter
        if not isinstance(building_dims, BuildingDims):
            print(f"[ERROR] FEHLER: Ungültige BuildingDims: {type(building_dims)}")
            return []
        
        if target_modules <= 0:
            print(f"[ERROR] FEHLER: Ungültige Modulanzahl: {target_modules}")
            return []
        
        if optimization_goal not in ["max_modules", "max_yield", "balanced"]:
            print(f"[WARNING]  WARNUNG: Unbekanntes Optimierungsziel '{optimization_goal}', verwende 'balanced'")
            optimization_goal = "balanced"
        
        # DETAILLIERTES LOGGING: Zeige Optimierungsparameter
        print(f"\n[LAUNCH] Optimierung gestartet:")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   Eingabeparameter:")
        print(f"     • Optimierungsziel: {optimization_goal}")
        print(f"     • Gewünschte Module: {target_modules}")
        print(f"     • Dachform: {roof_type}")
        print(f"     • Gebäudedimensionen:")
        print(f"       - Länge: {building_dims.length_m:.1f}m")
        print(f"       - Breite: {building_dims.width_m:.1f}m")
        print(f"       - Wandhöhe: {building_dims.wall_height_m:.1f}m")
        print(f"       - Dachfläche: {building_dims.length_m * building_dims.width_m:.1f}m²")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
        configurations = []
        
        print(f"   Generiere Konfigurationen:")
        
        # Strategie 1: Süd-Aufständerung (optimal für Ertrag)
        try:
            config1 = AdvancedLayoutConfig(
                mode="auto",
                mounting_mode="south",
                custom_azimuth=0.0,
                custom_tilt=15.0,
                use_garage=False,
                use_facade=False
            )
            score1 = evaluate_config(config1, building_dims, target_modules, optimization_goal)
            configurations.append((config1, score1))
            print(f"     [OK] 1. Süd-Aufständerung: Score {score1:.1f}")
        except Exception as e:
            print(f"     [ERROR] 1. Süd-Aufständerung fehlgeschlagen: {e}")
        
        # Strategie 2: Ost-West-Aufständerung (mehr Module, weniger Ertrag pro Modul)
        try:
            config2 = AdvancedLayoutConfig(
                mode="auto",
                mounting_mode="east-west",
                custom_azimuth=0.0,
                custom_tilt=10.0,
                use_garage=False,
                use_facade=False
            )
            score2 = evaluate_config(config2, building_dims, target_modules, optimization_goal)
            configurations.append((config2, score2))
            print(f"     [OK] 2. Ost-West-Aufständerung: Score {score2:.1f}")
        except Exception as e:
            print(f"     [ERROR] 2. Ost-West-Aufständerung fehlgeschlagen: {e}")
        
        # Strategie 3: Süd-Ost (Kompromiss)
        try:
            config3 = AdvancedLayoutConfig(
                mode="auto",
                mounting_mode="south-east",
                custom_azimuth=45.0,
                custom_tilt=15.0,
                use_garage=False,
                use_facade=False
            )
            score3 = evaluate_config(config3, building_dims, target_modules, optimization_goal)
            configurations.append((config3, score3))
            print(f"     [OK] 3. Süd-Ost-Aufständerung: Score {score3:.1f}")
        except Exception as e:
            print(f"     [ERROR] 3. Süd-Ost-Aufständerung fehlgeschlagen: {e}")
        
        # Strategie 4: Gemischt (mit Garage und Fassade für maximale Modulanzahl)
        try:
            config4 = AdvancedLayoutConfig(
                mode="auto",
                use_garage=True,
                use_facade=True,
                mounting_mode="south",
                custom_azimuth=0.0,
                custom_tilt=15.0
            )
            score4 = evaluate_config(config4, building_dims, target_modules, optimization_goal)
            configurations.append((config4, score4))
            print(f"     [OK] 4. Gemischt (Garage + Fassade): Score {score4:.1f}")
        except Exception as e:
            print(f"     [ERROR] 4. Gemischt fehlgeschlagen: {e}")
        
        # Prüfe ob Konfigurationen generiert wurden
        if not configurations:
            print(f"   [ERROR] FEHLER: Keine Konfigurationen konnten generiert werden!")
            return []
        
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Sortiere nach Score (höchster zuerst)
        configurations.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   [OK] Optimierung abgeschlossen!")
        print(f"   Top 3 Konfigurationen:")
        for i, (config, score) in enumerate(configurations[:3], 1):
            mode_name = config.mounting_mode
            extras = []
            if config.use_garage:
                extras.append("Garage")
            if config.use_facade:
                extras.append("Fassade")
            if extras:
                mode_name += " + " + " + ".join(extras)
            print(f"     {i}. {mode_name}: Score {score:.1f}")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Gebe Top 3 zurück
        return configurations[:3]
        
    except Exception as e:
        # FEHLERBEHANDLUNG: Logge Fehler mit Traceback
        print(f"\n[ERROR] KRITISCHER FEHLER in optimize_layout():")
        print(f"   Fehler: {str(e)}")
        print(f"   Parameter: target_modules={target_modules}, goal={optimization_goal}")
        print(f"   Traceback:")
        traceback.print_exc()
        print(f"   Fallback: Rückgabe leere Liste\n")
        return []


def evaluate_config(
    config: AdvancedLayoutConfig,
    building_dims: BuildingDims,
    target_modules: int,
    goal: str
) -> float:
    """
    Bewertet eine Konfiguration basierend auf Optimierungsziel.
    
    FIX 2024: Neu implementiert für funktionierenden Optimierungs-Assistenten.
    ENHANCED 2024: Robuste Fehlerbehandlung.
    
    Args:
        config: Layout-Konfiguration
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Modulanzahl
        goal: "max_modules", "max_yield", oder "balanced"
    
    Returns:
        Score von 0-100
    """
    import traceback
    
    try:
        # Validiere Eingabeparameter
        if not isinstance(config, AdvancedLayoutConfig):
            print(f"[ERROR] FEHLER in evaluate_config: Ungültige Konfiguration")
            return 0.0
        
        if target_modules <= 0:
            print(f"[ERROR] FEHLER in evaluate_config: Ungültige Modulanzahl: {target_modules}")
            return 0.0
        
        score = 0.0
        
        # Berechne geschätzte Modulanzahl für diese Konfiguration
        roof_area = building_dims.length_m * building_dims.width_m
        module_area = 1.05 * 1.76  # PV_W * PV_H
        
        # Effizienzfaktor basierend auf Mounting Mode
        efficiency_factors = {
            "south": 0.75,
            "east-west": 0.65,  # Weniger Platz wegen Reihenabstand
            "south-east": 0.70,
            "south-west": 0.70,
            "custom": 0.70
        }
        efficiency = efficiency_factors.get(config.mounting_mode, 0.70)
        
        # Zusätzliche Kapazität durch Garage/Fassade
        if config.use_garage:
            efficiency += 0.15
        if config.use_facade:
            efficiency += 0.10
        
        if module_area != 0:
            estimated_modules = int((roof_area / module_area) * efficiency)
        else:
            estimated_modules = 0.0
        
        # Bewertung basierend auf Ziel
        if goal == "max_modules":
            # Maximiere Modulanzahl
            # Je näher an target_modules, desto besser
            if estimated_modules >= target_modules:
                score = 100.0
            else:
                if target_modules != 0:
                    score = (estimated_modules / target_modules) * 100
                else:
                    score = 0.0
            
        elif goal == "max_yield":
            # Maximiere Ertrag (Süd-Ausrichtung bevorzugt)
            # 70% Modulanzahl, 30% Ausrichtung
            if target_modules != 0:
                module_score = min(100, (estimated_modules / target_modules) * 70)
            else:
                module_score = 0.0
            
            # Ausrichtungs-Bonus
            orientation_bonus = 0
            if config.mounting_mode == "south":
                orientation_bonus = 30
            elif config.mounting_mode in ["south-east", "south-west"]:
                orientation_bonus = 20
            elif config.mounting_mode == "east-west":
                orientation_bonus = 15
            else:
                orientation_bonus = 10
            
            score = module_score + orientation_bonus
            
        elif goal == "balanced":
            # Ausgewogen: 60% Modulanzahl, 25% Ausrichtung, 15% Einfachheit
            if target_modules != 0:
                module_score = min(100, (estimated_modules / target_modules) * 60)
            else:
                module_score = 0.0
            
            # Ausrichtungs-Bonus
            orientation_bonus = 0
            if config.mounting_mode == "south":
                orientation_bonus = 25
            elif config.mounting_mode in ["south-east", "south-west"]:
                orientation_bonus = 20
            elif config.mounting_mode == "east-west":
                orientation_bonus = 15
            else:
                orientation_bonus = 10
            
            # Bonus für einfache Konfiguration (ohne Garage/Fassade)
            simplicity_bonus = 0
            if not config.use_garage and not config.use_facade:
                simplicity_bonus = 15
            elif not config.use_garage or not config.use_facade:
                simplicity_bonus = 7
            
            score = module_score + orientation_bonus + simplicity_bonus
        
        # Stelle sicher dass Score im Bereich 0-100 liegt
        final_score = min(100.0, max(0.0, score))
        
        # Logging für Debugging
        if final_score < 0 or final_score > 100:
            print(f"[WARNING]  WARNUNG: Score außerhalb des Bereichs vor Clipping: {score}")
        
        return final_score
        
    except Exception as e:
        # FEHLERBEHANDLUNG: Logge Fehler und gebe 0 zurück
        print(f"[ERROR] FEHLER in evaluate_config():")
        print(f"   Fehler: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        return 0.0
