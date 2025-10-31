"""
3D PV-Visualisierung Core Engine

Dieses Modul stellt die Kern-Funktionalität für die 3D-Visualisierung
von Photovoltaik-Anlagen auf Gebäuden bereit.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
import json

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
    """
    Gebäudedimensionen für 3D-Modellierung.

    Attributes:
        length_m: Gebäudelänge in Metern
        width_m: Gebäudebreite in Metern
        wall_height_m: Traufhöhe (Wandhöhe) in Metern
    """
    length_m: float = 10.0
    width_m: float = 6.0
    wall_height_m: float = 6.0


@dataclass
class LayoutConfig:
    """
    Konfiguration für PV-Modul-Layout.

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
    spacing: float = 0.25
) -> List['pv.PolyData']:
    """
    Platziert PV-Module auf Flachdach mit Aufständerung.

    Implementiert zwei Aufständerungstypen:
    - "south": Süd-Aufständerung (15° Neigung, 0° Yaw)
    - "east-west": Ost-West-Aufständerung (10° Neigung, alternierender Yaw)

    Args:
        roof_length: Dachlänge in X-Richtung (Meter)
        roof_width: Dachbreite in Y-Richtung (Meter)
        module_quantity: Gewünschte Anzahl der Module
        mounting_type: Aufständerungstyp ("south" oder "east-west")
        removed_indices: Liste der zu entfernenden Modul-Indizes (optional)
        base_z: Basis-Z-Höhe für Modul-Platzierung
        margin: Randabstand (Meter)
        spacing: Abstand zwischen Modulen (Meter)

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
    else:
        # Süd (Standard): 15° Neigung, 0° Yaw
        tilt = 15.0
        use_alternating_yaw = False

    # Berechne Rasterposit ionen
    # Bei Ost-West: Verwende größeren Reihenabstand
    if use_alternating_yaw:
        # Für Ost-West: Berechne Positionen mit erhöhtem Reihenabstand
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
    else:
        # Süd: Normale Rasterposit ionen
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
                yaw = -90.0  # Osten
            else:
                yaw = 90.0   # Westen
        else:
            # Süd: 0° Yaw (nach Süden)
            yaw = 0.0

        # Z-Position: Auf Flachdach + kleine Erhöhung für Aufständerung
        z = base_z + 0.05  # 5cm über Dach

        # Erstelle Modul
        panel = make_panel(
            position=(x, y, z),
            yaw_deg=yaw,
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
    off_screen: bool = False
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
        ...     layout_config=layout
        ... )
    """
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

    # Platziere Module basierend auf Belegungsmodus
    if layout_config.mode == "manual":
        # Manuelle Belegung mit removed_indices
        if roof_type_normalized == "Flachdach":
            # Flachdach: Verwende Aufständerung
            # Bestimme Aufständerungstyp (Standard: Süd)
            mounting_type = "south"  # Kann später erweitert werden
            panels_main = place_panels_flat_roof(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                mounting_type=mounting_type,
                removed_indices=layout_config.removed_indices,
                base_z=base_z
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
            # Flachdach: Verwende Aufständerung
            mounting_type = "south"  # Kann später erweitert werden
            panels_main = place_panels_flat_roof(
                roof_length=length,
                roof_width=width,
                module_quantity=module_quantity,
                mounting_type=mounting_type,
                base_z=base_z
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

    # Füge Module zum Plotter hinzu (schwarze Farbe)
    for panel in panels_main:
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
        for panel in panels_garage:
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
        for panel in panels_facade:
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
