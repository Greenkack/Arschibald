"""
Hinderniserkennung für PV-Modul-Platzierung

Dieses Modul implementiert automatische Erkennung und Vermeidung von
Hindernissen wie Schornsteinen, Fenstern, Gauben, Antennen, etc.

Requirements: 7.3
"""

from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import math


# ============================================================================
# ENUMS
# ============================================================================

class ObstacleType(Enum):
    """Typen von Hindernissen auf dem Dach."""
    CHIMNEY = "schornstein"
    WINDOW = "fenster"
    DORMER = "gaube"
    SKYLIGHT = "dachfenster"
    VENT = "lüftung"
    ANTENNA = "antenne"
    SOLAR_THERMAL = "solarthermie"
    CUSTOM = "benutzerdefiniert"


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class Obstacle:
    """
    Repräsentiert ein Hindernis auf dem Dach.

    Attributes:
        x: X-Position des Zentrums (Meter)
        y: Y-Position des Zentrums (Meter)
        z: Z-Position (Höhe über Dach, Meter)
        width: Breite in X-Richtung (Meter)
        height: Höhe in Y-Richtung (Meter)
        depth: Tiefe in Z-Richtung (Meter)
        obstacle_type: Typ des Hindernisses
        name: Optionaler Name
        safety_margin: Sicherheitsabstand in Metern
    """
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    obstacle_type: ObstacleType
    name: str = ""
    safety_margin: float = 0.30  # 30cm Standard-Sicherheitsabstand

    def get_bounding_box(self) -> Dict[str, float]:
        """
        Berechnet Bounding Box mit Sicherheitsabstand.

        Returns:
            Dict mit min_x, max_x, min_y, max_y, min_z, max_z
        """
        return {
            "min_x": self.x - (self.width / 2) - self.safety_margin,
            "max_x": self.x + (self.width / 2) + self.safety_margin,
            "min_y": self.y - (self.height / 2) - self.safety_margin,
            "max_y": self.y + (self.height / 2) + self.safety_margin,
            "min_z": self.z,
            "max_z": self.z + self.depth
        }

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "obstacle_type": self.obstacle_type.value,
            "name": self.name,
            "safety_margin": self.safety_margin
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Obstacle':
        """Erstellt Obstacle aus Dictionary."""
        obstacle_type = ObstacleType(data.get("obstacle_type", "custom"))
        return cls(
            x=data["x"],
            y=data["y"],
            z=data.get("z", 0.0),
            width=data["width"],
            height=data["height"],
            depth=data.get("depth", 1.0),
            obstacle_type=obstacle_type,
            name=data.get("name", ""),
            safety_margin=data.get("safety_margin", 0.30)
        )


@dataclass
class ObstacleDetectionResult:
    """
    Ergebnis der Hinderniserkennung.

    Attributes:
        has_collision: Ob Kollision vorliegt
        colliding_obstacles: Liste kollidierender Hindernisse
        safe_distance: Minimaler Abstand zum nächsten Hindernis
        suggestions: Vorschläge zur Vermeidung
    """
    has_collision: bool
    colliding_obstacles: List[Obstacle]
    safe_distance: float
    suggestions: List[str]


# ============================================================================
# VORDEFINIERTE HINDERNISSE
# ============================================================================

def create_standard_chimney(
    x: float,
    y: float,
    z: float = 0.0
) -> Obstacle:
    """
    Erstellt Standard-Schornstein.

    Args:
        x, y: Position auf dem Dach
        z: Höhe über Dach (default: 0.0)

    Returns:
        Obstacle-Objekt für Schornstein
    """
    return Obstacle(
        x=x,
        y=y,
        z=z,
        width=0.80,  # 80cm breit
        height=0.80,  # 80cm tief
        depth=2.0,  # 2m hoch
        obstacle_type=ObstacleType.CHIMNEY,
        name="Schornstein",
        safety_margin=0.50  # 50cm Sicherheitsabstand
    )


def create_standard_dormer(
    x: float,
    y: float,
    z: float = 0.0,
    width: float = 1.5
) -> Obstacle:
    """
    Erstellt Standard-Gaube.

    Args:
        x, y: Position auf dem Dach
        z: Höhe über Dach
        width: Breite der Gaube

    Returns:
        Obstacle-Objekt für Gaube
    """
    return Obstacle(
        x=x,
        y=y,
        z=z,
        width=width,
        height=1.0,  # 1m tief
        depth=1.5,  # 1.5m hoch
        obstacle_type=ObstacleType.DORMER,
        name="Gaube",
        safety_margin=0.30
    )


def create_standard_skylight(
    x: float,
    y: float,
    z: float = 0.0
) -> Obstacle:
    """
    Erstellt Standard-Dachfenster.

    Args:
        x, y: Position auf dem Dach
        z: Höhe über Dach

    Returns:
        Obstacle-Objekt für Dachfenster
    """
    return Obstacle(
        x=x,
        y=y,
        z=z,
        width=1.0,  # 1m breit
        height=1.2,  # 1.2m hoch
        depth=0.15,  # 15cm erhöht
        obstacle_type=ObstacleType.SKYLIGHT,
        name="Dachfenster",
        safety_margin=0.20
    )


def create_standard_vent(
    x: float,
    y: float,
    z: float = 0.0
) -> Obstacle:
    """
    Erstellt Standard-Lüftung.

    Args:
        x, y: Position auf dem Dach
        z: Höhe über Dach

    Returns:
        Obstacle-Objekt für Lüftung
    """
    return Obstacle(
        x=x,
        y=y,
        z=z,
        width=0.30,  # 30cm breit
        height=0.30,  # 30cm tief
        depth=0.50,  # 50cm hoch
        obstacle_type=ObstacleType.VENT,
        name="Lüftung",
        safety_margin=0.20
    )


# ============================================================================
# HINDERNISERKENNUNG
# ============================================================================

class ObstacleDetector:
    """
    Erkennt und verwaltet Hindernisse auf dem Dach.
    """

    def __init__(
        self,
        module_width: float = 1.05,
        module_height: float = 1.76
    ):
        """
        Initialisiert Hinderniserkennung.

        Args:
            module_width: Breite eines PV-Moduls (Meter)
            module_height: Höhe eines PV-Moduls (Meter)
        """
        self.module_width = module_width
        self.module_height = module_height
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """
        Fügt Hindernis hinzu.

        Args:
            obstacle: Hinzuzufügendes Hindernis
        """
        self.obstacles.append(obstacle)

    def remove_obstacle(self, index: int) -> bool:
        """
        Entfernt Hindernis.

        Args:
            index: Index des zu entfernenden Hindernisses

        Returns:
            True wenn erfolgreich, False sonst
        """
        if 0 <= index < len(self.obstacles):
            self.obstacles.pop(index)
            return True
        return False

    def clear_obstacles(self) -> None:
        """Entfernt alle Hindernisse."""
        self.obstacles.clear()

    def check_module_collision(
        self,
        x: float,
        y: float,
        z: float,
        rotation: float = 0.0
    ) -> ObstacleDetectionResult:
        """
        Prüft ob Modul mit Hindernissen kollidiert.

        Args:
            x, y, z: Position des Moduls
            rotation: Rotation in Grad (0, 90, 180, 270)

        Returns:
            ObstacleDetectionResult mit Kollisionsinformationen
        """
        # Berechne Modul-Bounding-Box
        if rotation in [90, 270]:
            # Rotiert: Breite und Höhe vertauscht
            mod_width = self.module_height
            mod_height = self.module_width
        else:
            mod_width = self.module_width
            mod_height = self.module_height

        module_bbox = {
            "min_x": x - mod_width / 2,
            "max_x": x + mod_width / 2,
            "min_y": y - mod_height / 2,
            "max_y": y + mod_height / 2,
            "min_z": z,
            "max_z": z + 0.05  # 5cm Moduldicke
        }

        colliding_obstacles = []
        min_distance = float('inf')

        for obstacle in self.obstacles:
            obs_bbox = obstacle.get_bounding_box()

            # Prüfe 3D-Überlappung
            if self._boxes_overlap(module_bbox, obs_bbox):
                colliding_obstacles.append(obstacle)

            # Berechne minimalen Abstand
            distance = self._calculate_distance_2d(
                x, y,
                obstacle.x, obstacle.y
            )
            min_distance = min(min_distance, distance)

        # Generiere Vorschläge
        suggestions = self._generate_avoidance_suggestions(
            x, y, colliding_obstacles
        )

        return ObstacleDetectionResult(
            has_collision=len(colliding_obstacles) > 0,
            colliding_obstacles=colliding_obstacles,
            safe_distance=min_distance,
            suggestions=suggestions
        )

    def find_safe_positions(
        self,
        candidate_positions: List[Tuple[float, float, float]],
        rotation: float = 0.0
    ) -> List[Tuple[float, float, float]]:
        """
        Filtert sichere Positionen ohne Kollisionen.

        Args:
            candidate_positions: Liste von (x, y, z) Positionen
            rotation: Rotation der Module

        Returns:
            Liste sicherer Positionen
        """
        safe_positions = []

        for x, y, z in candidate_positions:
            result = self.check_module_collision(x, y, z, rotation)
            if not result.has_collision:
                safe_positions.append((x, y, z))

        return safe_positions

    def get_obstacle_map(
        self,
        roof_length: float,
        roof_width: float,
        resolution: int = 50
    ) -> List[List[bool]]:
        """
        Erstellt 2D-Karte mit Hindernissen.

        Args:
            roof_length: Dachlänge (X-Achse)
            roof_width: Dachbreite (Y-Achse)
            resolution: Auflösung der Karte

        Returns:
            2D-Liste mit True für Hindernisse, False für frei
        """
        obstacle_map = [
            [False for _ in range(resolution)]
            for _ in range(resolution)
        ]

        x_step = roof_length / resolution
        y_step = roof_width / resolution

        for i in range(resolution):
            for j in range(resolution):
                x = -roof_length/2 + i * x_step
                y = -roof_width/2 + j * y_step

                # Prüfe ob Position in Hindernis liegt
                for obstacle in self.obstacles:
                    bbox = obstacle.get_bounding_box()
                    if (bbox["min_x"] <= x <= bbox["max_x"] and
                            bbox["min_y"] <= y <= bbox["max_y"]):
                        obstacle_map[i][j] = True
                        break

        return obstacle_map

    def get_obstacles_by_type(
        self,
        obstacle_type: ObstacleType
    ) -> List[Obstacle]:
        """
        Gibt alle Hindernisse eines bestimmten Typs zurück.

        Args:
            obstacle_type: Typ der Hindernisse

        Returns:
            Liste von Hindernissen
        """
        return [
            obs for obs in self.obstacles
            if obs.obstacle_type == obstacle_type
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über Hindernisse zurück.

        Returns:
            Dict mit Statistiken
        """
        type_counts = {}
        for obs_type in ObstacleType:
            count = len(self.get_obstacles_by_type(obs_type))
            if count > 0:
                type_counts[obs_type.value] = count

        total_area = sum(
            obs.width * obs.height for obs in self.obstacles
        )

        return {
            "total_count": len(self.obstacles),
            "by_type": type_counts,
            "total_area_m2": total_area,
            "average_safety_margin": (
                sum(obs.safety_margin for obs in self.obstacles) /
                len(self.obstacles)
                if self.obstacles else 0.0
            )
        }

    # ========================================================================
    # HILFSFUNKTIONEN
    # ========================================================================

    def _boxes_overlap(
        self,
        box1: Dict[str, float],
        box2: Dict[str, float]
    ) -> bool:
        """
        Prüft ob zwei 3D-Bounding-Boxes überlappen.

        Args:
            box1, box2: Dicts mit min_x, max_x, min_y, max_y, min_z, max_z

        Returns:
            True wenn Überlappung, False sonst
        """
        # Prüfe X-Achse
        if box1["max_x"] < box2["min_x"] or box1["min_x"] > box2["max_x"]:
            return False

        # Prüfe Y-Achse
        if box1["max_y"] < box2["min_y"] or box1["min_y"] > box2["max_y"]:
            return False

        # Prüfe Z-Achse
        if box1["max_z"] < box2["min_z"] or box1["min_z"] > box2["max_z"]:
            return False

        return True

    def _calculate_distance_2d(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> float:
        """
        Berechnet 2D-Distanz zwischen zwei Punkten.

        Args:
            x1, y1: Punkt 1
            x2, y2: Punkt 2

        Returns:
            Distanz in Metern
        """
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _generate_avoidance_suggestions(
        self,
        x: float,
        y: float,
        colliding_obstacles: List[Obstacle]
    ) -> List[str]:
        """
        Generiert Vorschläge zur Vermeidung von Hindernissen.

        Args:
            x, y: Aktuelle Position
            colliding_obstacles: Liste kollidierender Hindernisse

        Returns:
            Liste von Vorschlägen
        """
        if not colliding_obstacles:
            return ["Position ist sicher"]

        suggestions = []

        for obstacle in colliding_obstacles:
            # Berechne Richtung zum Hindernis
            dx = obstacle.x - x
            dy = obstacle.y - y

            # Empfehle Bewegung weg vom Hindernis
            if abs(dx) > abs(dy):
                direction = "links" if dx > 0 else "rechts"
                distance = abs(dx) + obstacle.width/2 + self.module_width/2
            else:
                direction = "unten" if dy > 0 else "oben"
                distance = abs(dy) + obstacle.height/2 + self.module_height/2

            suggestions.append(
                f"Modul {distance:.2f}m nach {direction} verschieben "
                f"(Kollision mit {obstacle.name or obstacle.obstacle_type.value})"
            )

        return suggestions


# ============================================================================
# AUTOMATISCHE HINDERNISERKENNUNG
# ============================================================================

def detect_obstacles_from_roof_geometry(
    roof_type: str,
    roof_length: float,
    roof_width: float,
    **kwargs
) -> List[Obstacle]:
    """
    Erkennt typische Hindernisse basierend auf Dachgeometrie.

    Diese Funktion schätzt wahrscheinliche Hindernisse basierend auf
    Dachtyp und Größe. In einer realen Anwendung würde dies durch
    Bildverarbeitung oder manuelle Eingabe ersetzt.

    Args:
        roof_type: Typ des Dachs
        roof_length: Dachlänge
        roof_width: Dachbreite
        **kwargs: Zusätzliche Parameter

    Returns:
        Liste geschätzter Hindernisse
    """
    obstacles = []
    roof_type_lower = roof_type.lower()

    # Schornstein bei Schrägdächern wahrscheinlich
    if "satteldach" in roof_type_lower or "walmdach" in roof_type_lower:
        # Platziere Schornstein nahe First (Mitte Y-Achse)
        obstacles.append(create_standard_chimney(
            x=0.0,
            y=roof_width * 0.3,  # 30% vom Rand
            z=0.0
        ))

    # Gauben bei größeren Dächern
    if roof_length > 8.0 and "satteldach" in roof_type_lower:
        # Zwei Gauben symmetrisch
        obstacles.append(create_standard_dormer(
            x=-roof_length * 0.25,
            y=roof_width * 0.2,
            z=0.0
        ))
        obstacles.append(create_standard_dormer(
            x=roof_length * 0.25,
            y=roof_width * 0.2,
            z=0.0
        ))

    return obstacles
