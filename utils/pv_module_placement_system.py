"""
PV-Modul Platzierungs-System
============================

Vollständiges System für automatische und manuelle Platzierung von PV-Modulen
auf verschiedenen Dachtypen mit umfassenden Bearbeitungsfunktionen.

Features:
- Automatische Vollbelegung mit Maximalanzahl
- Manuelle Einzelplatzierung
- Modul-Typen: Monokristallin (schwarz) und Polykristallin (blau)
- Transformationen: Drehen, Neigen, Rotieren, Verschieben, Spiegeln
- Gruppenverwaltung
- Speichern/Laden von Layouts
"""

from __future__ import annotations
import json
import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum


# ============================================================================
# MODUL-TYPEN UND KONSTANTEN
# ============================================================================

class ModuleType(Enum):
    """PV-Modul Typen"""
    MONOCRYSTALLINE = "mono"  # Schwarz
    POLYCRYSTALLINE = "poly"  # Blau
    
    @property
    def color(self) -> str:
        """Farbe des Modul-Typs"""
        return {
            ModuleType.MONOCRYSTALLINE: "#1a1a1a",  # Dunkel-Schwarz
            ModuleType.POLYCRYSTALLINE: "#1e3a8a",  # Dunkel-Blau
        }[self]
    
    @property
    def display_name(self) -> str:
        """Anzeigename des Modul-Typs"""
        return {
            ModuleType.MONOCRYSTALLINE: "Monokristallin (Schwarz)",
            ModuleType.POLYCRYSTALLINE: "Polykristallin (Blau)",
        }[self]


class ModuleOrientation(Enum):
    """Modul-Ausrichtung"""
    LANDSCAPE = "landscape"  # Querformat (Breite > Höhe)
    PORTRAIT = "portrait"    # Hochformat (Höhe > Breite)


# Standard-Modulgrößen (in Metern)
DEFAULT_MODULE_WIDTH = 1.722   # Standard Breite
DEFAULT_MODULE_HEIGHT = 1.134  # Standard Höhe
DEFAULT_MODULE_THICKNESS = 0.035  # Standard Dicke


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class ModuleDimensions:
    """Modul-Abmessungen"""
    width: float = DEFAULT_MODULE_WIDTH
    height: float = DEFAULT_MODULE_HEIGHT
    thickness: float = DEFAULT_MODULE_THICKNESS
    power_wp: float = 400.0  # Nennleistung in Wp
    
    def get_area(self) -> float:
        """Berechnet die Modulfläche in m²"""
        return self.width * self.height
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModuleDimensions':
        return cls(**data)


@dataclass
class ModuleTransform3D:
    """3D-Transformation eines einzelnen Moduls"""
    # Position (Zentrum des Moduls)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # Rotation (in Grad)
    rotation_x: float = 0.0  # Neigung (tilt)
    rotation_y: float = 0.0  # Seitliche Neigung
    rotation_z: float = 0.0  # Drehung um Z-Achse (azimuth)
    
    # Skalierung (normalerweise 1.0)
    scale_x: float = 1.0
    scale_y: float = 1.0
    scale_z: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModuleTransform3D':
        return cls(**data)
    
    def copy(self) -> 'ModuleTransform3D':
        """Erstellt eine Kopie der Transformation"""
        return ModuleTransform3D(**asdict(self))


@dataclass
class PVModule:
    """Einzelnes PV-Modul mit allen Eigenschaften"""
    id: int
    module_type: ModuleType
    dimensions: ModuleDimensions
    transform: ModuleTransform3D
    orientation: ModuleOrientation = ModuleOrientation.LANDSCAPE
    
    # Status
    is_selected: bool = False
    is_locked: bool = False
    group_id: Optional[int] = None
    
    # Metadaten
    name: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary (für JSON)"""
        return {
            "id": self.id,
            "module_type": self.module_type.value,
            "dimensions": self.dimensions.to_dict(),
            "transform": self.transform.to_dict(),
            "orientation": self.orientation.value,
            "is_selected": self.is_selected,
            "is_locked": self.is_locked,
            "group_id": self.group_id,
            "name": self.name,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PVModule':
        """Erstellt Modul aus Dictionary"""
        return cls(
            id=data["id"],
            module_type=ModuleType(data["module_type"]),
            dimensions=ModuleDimensions.from_dict(data["dimensions"]),
            transform=ModuleTransform3D.from_dict(data["transform"]),
            orientation=ModuleOrientation(data["orientation"]),
            is_selected=data.get("is_selected", False),
            is_locked=data.get("is_locked", False),
            group_id=data.get("group_id"),
            name=data.get("name"),
            notes=data.get("notes", ""),
        )
    
    def get_color(self) -> str:
        """Gibt die Farbe des Moduls zurück"""
        return self.module_type.color
    
    def get_actual_dimensions(self) -> Tuple[float, float, float]:
        """
        Gibt die tatsächlichen Dimensionen basierend auf Orientierung zurück.
        
        Returns:
            (width, height, thickness) in aktueller Orientierung
        """
        if self.orientation == ModuleOrientation.LANDSCAPE:
            return (self.dimensions.width, self.dimensions.height, self.dimensions.thickness)
        else:
            return (self.dimensions.height, self.dimensions.width, self.dimensions.thickness)
    
    def get_vertices_3d(self) -> np.ndarray:
        """
        Berechnet die 8 Vertices des Moduls im 3D-Raum unter
        Berücksichtigung aller Transformationen.
        
        Returns:
            Array (8, 3) mit den 8 Eckpunkten des Quaders
        """
        w, h, t = self.get_actual_dimensions()
        
        # Basis-Vertices im lokalen Koordinatensystem (Zentrum bei 0,0,0)
        half_w, half_h, half_t = w/2, h/2, t/2
        local_vertices = np.array([
            [-half_w, -half_h, -half_t],  # 0: vorne links unten
            [+half_w, -half_h, -half_t],  # 1: vorne rechts unten
            [+half_w, +half_h, -half_t],  # 2: hinten rechts unten
            [-half_w, +half_h, -half_t],  # 3: hinten links unten
            [-half_w, -half_h, +half_t],  # 4: vorne links oben
            [+half_w, -half_h, +half_t],  # 5: vorne rechts oben
            [+half_w, +half_h, +half_t],  # 6: hinten rechts oben
            [-half_w, +half_h, +half_t],  # 7: hinten links oben
        ])
        
        # Rotationen anwenden (in Reihenfolge: X -> Y -> Z)
        vertices = local_vertices.copy()
        
        # Rotation um X-Achse (Neigung)
        if self.transform.rotation_x != 0:
            angle = np.deg2rad(self.transform.rotation_x)
            rot_x = np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)]
            ])
            vertices = vertices @ rot_x.T
        
        # Rotation um Y-Achse
        if self.transform.rotation_y != 0:
            angle = np.deg2rad(self.transform.rotation_y)
            rot_y = np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)]
            ])
            vertices = vertices @ rot_y.T
        
        # Rotation um Z-Achse (Drehung)
        if self.transform.rotation_z != 0:
            angle = np.deg2rad(self.transform.rotation_z)
            rot_z = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            vertices = vertices @ rot_z.T
        
        # Skalierung anwenden
        scale = np.array([self.transform.scale_x, self.transform.scale_y, self.transform.scale_z])
        vertices = vertices * scale
        
        # Translation anwenden
        translation = np.array([self.transform.x, self.transform.y, self.transform.z])
        vertices = vertices + translation
        
        return vertices


@dataclass
class ModuleGroup:
    """Gruppe von Modulen für gemeinsame Transformationen"""
    id: int
    name: str
    module_ids: List[int] = field(default_factory=list)
    color_tag: str = "#ff6b6b"  # Farbe für Gruppenmarkierung
    is_locked: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModuleGroup':
        return cls(**data)


@dataclass
class RoofSurface:
    """Dachfläche für Modul-Platzierung"""
    id: int
    name: str
    roof_type: str  # "Flachdach", "Satteldach", etc.
    
    # Geometrie (vereinfacht als Polygon)
    vertices_3d: List[Tuple[float, float, float]]  # Liste von (x, y, z) Punkten
    
    # Neigung und Ausrichtung
    tilt_deg: float = 0.0
    azimuth_deg: float = 0.0  # 0=Süd, 90=West, -90=Ost, 180=Nord
    
    # Verfügbare Fläche
    usable_area_m2: float = 0.0
    
    # Platzierte Module auf dieser Fläche
    module_ids: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "roof_type": self.roof_type,
            "vertices_3d": self.vertices_3d,
            "tilt_deg": self.tilt_deg,
            "azimuth_deg": self.azimuth_deg,
            "usable_area_m2": self.usable_area_m2,
            "module_ids": self.module_ids,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoofSurface':
        return cls(**data)


# ============================================================================
# MODUL-PLATZIERUNGS-MANAGER
# ============================================================================

class ModulePlacementManager:
    """
    Zentrale Verwaltung aller PV-Module und deren Platzierung.
    
    Features:
    - Automatische Vollbelegung
    - Manuelle Platzierung
    - Transformationen (Drehen, Verschieben, etc.)
    - Gruppenverwaltung
    - Speichern/Laden
    """
    
    def __init__(self):
        self.modules: Dict[int, PVModule] = {}
        self.groups: Dict[int, ModuleGroup] = {}
        self.roof_surfaces: Dict[int, RoofSurface] = {}
        
        self.next_module_id = 1
        self.next_group_id = 1
        self.next_surface_id = 1
        
        # Standardeinstellungen
        self.default_module_type = ModuleType.MONOCRYSTALLINE
        self.default_dimensions = ModuleDimensions()
        self.default_orientation = ModuleOrientation.LANDSCAPE
    
    # ========================================================================
    # DACHFLÄCHEN-VERWALTUNG
    # ========================================================================
    
    def add_roof_surface(self, name: str, roof_type: str, vertices_3d: List[Tuple[float, float, float]],
                        tilt_deg: float = 0.0, azimuth_deg: float = 0.0) -> RoofSurface:
        """Fügt eine neue Dachfläche hinzu"""
        surface = RoofSurface(
            id=self.next_surface_id,
            name=name,
            roof_type=roof_type,
            vertices_3d=vertices_3d,
            tilt_deg=tilt_deg,
            azimuth_deg=azimuth_deg,
            usable_area_m2=self._calculate_surface_area(vertices_3d)
        )
        self.roof_surfaces[surface.id] = surface
        self.next_surface_id += 1
        return surface
    
    def _calculate_surface_area(self, vertices: List[Tuple[float, float, float]]) -> float:
        """Berechnet die Fläche eines Polygons (vereinfacht für planare Flächen)"""
        if len(vertices) < 3:
            return 0.0
        
        # Projektion auf XY-Ebene und Shoelace-Formel
        area = 0.0
        n = len(vertices)
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        return abs(area) / 2.0
    
    # ========================================================================
    # MODUL-VERWALTUNG
    # ========================================================================
    
    def add_module(self, x: float, y: float, z: float, 
                   module_type: Optional[ModuleType] = None,
                   dimensions: Optional[ModuleDimensions] = None,
                   orientation: Optional[ModuleOrientation] = None,
                   roof_surface_id: Optional[int] = None) -> PVModule:
        """
        Fügt ein neues Modul hinzu.
        
        Args:
            x, y, z: Position des Modul-Zentrums
            module_type: Typ des Moduls (mono/poly)
            dimensions: Abmessungen des Moduls
            orientation: Ausrichtung (landscape/portrait)
            roof_surface_id: ID der Dachfläche
            
        Returns:
            Das erstellte PVModule
        """
        if module_type is None:
            module_type = self.default_module_type
        if dimensions is None:
            dimensions = ModuleDimensions()
        if orientation is None:
            orientation = self.default_orientation
        
        transform = ModuleTransform3D(x=x, y=y, z=z)
        
        module = PVModule(
            id=self.next_module_id,
            module_type=module_type,
            dimensions=dimensions,
            transform=transform,
            orientation=orientation
        )
        
        self.modules[module.id] = module
        self.next_module_id += 1
        
        # Zu Dachfläche hinzufügen
        if roof_surface_id and roof_surface_id in self.roof_surfaces:
            self.roof_surfaces[roof_surface_id].module_ids.append(module.id)
        
        return module
    
    def remove_module(self, module_id: int) -> bool:
        """Entfernt ein Modul"""
        if module_id not in self.modules:
            return False
        
        module = self.modules[module_id]
        
        # Aus Gruppe entfernen
        if module.group_id and module.group_id in self.groups:
            group = self.groups[module.group_id]
            if module_id in group.module_ids:
                group.module_ids.remove(module_id)
        
        # Aus Dachflächen entfernen
        for surface in self.roof_surfaces.values():
            if module_id in surface.module_ids:
                surface.module_ids.remove(module_id)
        
        # Modul löschen
        del self.modules[module_id]
        return True
    
    def get_module(self, module_id: int) -> Optional[PVModule]:
        """Holt ein Modul anhand der ID"""
        return self.modules.get(module_id)
    
    def get_all_modules(self) -> List[PVModule]:
        """Gibt alle Module zurück"""
        return list(self.modules.values())
    
    def get_selected_modules(self) -> List[PVModule]:
        """Gibt alle ausgewählten Module zurück"""
        return [m for m in self.modules.values() if m.is_selected]
    
    def select_module(self, module_id: int, add_to_selection: bool = False):
        """Wählt ein Modul aus"""
        if not add_to_selection:
            # Deselektiere alle anderen
            for m in self.modules.values():
                m.is_selected = False
        
        if module_id in self.modules:
            self.modules[module_id].is_selected = True
    
    def deselect_all(self):
        """Deselektiert alle Module"""
        for m in self.modules.values():
            m.is_selected = False
    
    # ========================================================================
    # TRANSFORMATIONEN
    # ========================================================================
    
    def translate_module(self, module_id: int, dx: float, dy: float, dz: float):
        """Verschiebt ein Modul"""
        if module_id in self.modules:
            m = self.modules[module_id]
            if not m.is_locked:
                m.transform.x += dx
                m.transform.y += dy
                m.transform.z += dz
    
    def translate_selected(self, dx: float, dy: float, dz: float):
        """Verschiebt alle ausgewählten Module"""
        for m in self.get_selected_modules():
            if not m.is_locked:
                m.transform.x += dx
                m.transform.y += dy
                m.transform.z += dz
    
    def rotate_module(self, module_id: int, axis: str, angle_deg: float):
        """
        Rotiert ein Modul.
        
        Args:
            module_id: ID des Moduls
            axis: 'x', 'y', oder 'z'
            angle_deg: Winkel in Grad
        """
        if module_id in self.modules:
            m = self.modules[module_id]
            if not m.is_locked:
                if axis == 'x':
                    m.transform.rotation_x += angle_deg
                elif axis == 'y':
                    m.transform.rotation_y += angle_deg
                elif axis == 'z':
                    m.transform.rotation_z += angle_deg
    
    def rotate_selected(self, axis: str, angle_deg: float):
        """Rotiert alle ausgewählten Module"""
        for m in self.get_selected_modules():
            if not m.is_locked:
                if axis == 'x':
                    m.transform.rotation_x += angle_deg
                elif axis == 'y':
                    m.transform.rotation_y += angle_deg
                elif axis == 'z':
                    m.transform.rotation_z += angle_deg
    
    def set_orientation(self, module_id: int, orientation: ModuleOrientation):
        """Ändert die Orientierung eines Moduls"""
        if module_id in self.modules:
            self.modules[module_id].orientation = orientation
    
    def toggle_orientation(self, module_id: int):
        """Wechselt zwischen Landscape und Portrait"""
        if module_id in self.modules:
            m = self.modules[module_id]
            m.orientation = (ModuleOrientation.PORTRAIT 
                           if m.orientation == ModuleOrientation.LANDSCAPE 
                           else ModuleOrientation.LANDSCAPE)
    
    def change_module_type(self, module_id: int, module_type: ModuleType):
        """Ändert den Typ (Farbe) eines Moduls"""
        if module_id in self.modules:
            self.modules[module_id].module_type = module_type
    
    # ========================================================================
    # GRUPPENVERWALTUNG
    # ========================================================================
    
    def create_group(self, name: str, module_ids: List[int]) -> ModuleGroup:
        """Erstellt eine neue Gruppe"""
        group = ModuleGroup(
            id=self.next_group_id,
            name=name,
            module_ids=module_ids.copy()
        )
        self.groups[group.id] = group
        self.next_group_id += 1
        
        # Module der Gruppe zuweisen
        for mid in module_ids:
            if mid in self.modules:
                self.modules[mid].group_id = group.id
        
        return group
    
    def create_group_from_selected(self, name: str) -> Optional[ModuleGroup]:
        """Erstellt eine Gruppe aus ausgewählten Modulen"""
        selected = self.get_selected_modules()
        if not selected:
            return None
        
        module_ids = [m.id for m in selected]
        return self.create_group(name, module_ids)
    
    def add_to_group(self, group_id: int, module_id: int):
        """Fügt ein Modul zu einer Gruppe hinzu"""
        if group_id in self.groups and module_id in self.modules:
            group = self.groups[group_id]
            if module_id not in group.module_ids:
                group.module_ids.append(module_id)
                self.modules[module_id].group_id = group_id
    
    def remove_from_group(self, module_id: int):
        """Entfernt ein Modul aus seiner Gruppe"""
        if module_id in self.modules:
            m = self.modules[module_id]
            if m.group_id and m.group_id in self.groups:
                group = self.groups[m.group_id]
                if module_id in group.module_ids:
                    group.module_ids.remove(module_id)
                m.group_id = None
    
    def select_group(self, group_id: int):
        """Wählt alle Module einer Gruppe aus"""
        if group_id in self.groups:
            self.deselect_all()
            for mid in self.groups[group_id].module_ids:
                if mid in self.modules:
                    self.modules[mid].is_selected = True
    
    # ========================================================================
    # AUTOMATISCHE PLATZIERUNG
    # ========================================================================
    
    def auto_place_modules_on_surface(self, 
                                     surface_id: int,
                                     max_count: int,
                                     module_type: ModuleType,
                                     dimensions: ModuleDimensions,
                                     orientation: ModuleOrientation,
                                     spacing: float = 0.02,
                                     margin: float = 0.1,
                                     mounting_type: str = "south") -> int:
        """
        Platziert automatisch Module auf einer Dachfläche.
        
        Args:
            surface_id: ID der Dachfläche
            max_count: Maximale Anzahl der Module
            module_type: Typ der Module
            dimensions: Abmessungen der Module
            orientation: Ausrichtung
            spacing: Abstand zwischen Modulen (in m)
            margin: Rand um die Dachfläche (in m)
            mounting_type: "south" (Süd-Aufständerung) oder "east_west" (Ost-West-Dreieck)
            
        Returns:
            Anzahl der platzierten Module
        """
        print(f"🔍 auto_place_modules_on_surface aufgerufen:")
        print(f"  - surface_id: {surface_id}")
        print(f"  - max_count: {max_count}")
        print(f"  - mounting_type: {mounting_type}")
        print(f"  - roof_surfaces: {list(self.roof_surfaces.keys())}")
        
        if surface_id not in self.roof_surfaces:
            print(f"❌ Surface {surface_id} nicht in roof_surfaces gefunden!")
            return 0
        
        surface = self.roof_surfaces[surface_id]
        print(f"✓ Surface gefunden: {surface.name}, Typ: {surface.roof_type}")
        
        # Berechne verfügbare Fläche und Grid
        # TODO: Implementierung für verschiedene Dachformen
        # Hier vereinfachte Implementierung für rechteckige Flächen
        
        placed_count = 0
        
        # Für Flachdach: Einfaches Grid-Layout
        if surface.roof_type == "Flachdach":
            print(f"  -> Verwende _auto_place_flat_roof")
            placed_count = self._auto_place_flat_roof(
                surface, max_count, module_type, dimensions, 
                orientation, spacing, margin, mounting_type
            )
        elif surface.roof_type == "Satteldach":
            print(f"  -> Verwende _auto_place_gabled_roof")
            placed_count = self._auto_place_gabled_roof(
                surface, max_count, module_type, dimensions,
                orientation, spacing, margin
            )
        else:
            print(f"  -> Dachtyp '{surface.roof_type}' nicht unterstützt - verwende Flachdach")
            placed_count = self._auto_place_flat_roof(
                surface, max_count, module_type, dimensions, 
                orientation, spacing, margin, mounting_type
            )
        
        print(f"✓ auto_place_modules_on_surface beendet: {placed_count} Module platziert")
        return placed_count
    
    def _auto_place_flat_roof(self, surface: RoofSurface, max_count: int,
                             module_type: ModuleType, dimensions: ModuleDimensions,
                             orientation: ModuleOrientation, spacing: float, 
                             margin: float, mounting_type: str = "south") -> int:
        """
        Automatische Platzierung auf Flachdach
        
        Args:
            mounting_type: "south" (klassisch 15° Süd) oder "east_west" (Dreieck Ost-West)
        """
        print(f"🔍 _auto_place_flat_roof gestartet (mounting_type={mounting_type})")
        
        # Vereinfachte Implementierung - Annahme: rechteckige Fläche
        vertices = surface.vertices_3d
        print(f"  - Vertices: {len(vertices)} Punkte")
        
        if len(vertices) < 4:
            print(f"❌ Zu wenige Vertices: {len(vertices)}")
            return 0
        
        # Berechne Bounding Box
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        z = sum(zs) / len(zs)  # Durchschnittliche Z-Position
        
        print(f"  - Bounding Box: X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}], Z={z:.2f}")
        
        # Verfügbare Fläche mit Rand
        available_width = (x_max - x_min) - 2 * margin
        available_height = (y_max - y_min) - 2 * margin
        
        print(f"  - Verfügbare Fläche: {available_width:.2f} x {available_height:.2f}m")
        
        # Modulabmessungen (abhängig von Orientierung)
        if orientation == ModuleOrientation.LANDSCAPE:
            mod_w, mod_h = dimensions.width, dimensions.height
        else:
            mod_w, mod_h = dimensions.height, dimensions.width
        
        print(f"  - Modul-Größe: {mod_w:.2f} x {mod_h:.2f}m")
        
        # Berechne Grid
        cols = int(available_width / (mod_w + spacing))
        rows = int(available_height / (mod_h + spacing))
        
        print(f"  - Grid: {cols} Spalten x {rows} Zeilen = {cols * rows} Plätze")
        
        total_possible = cols * rows
        actual_count = min(total_possible, max_count)
        
        print(f"  - Platziere {actual_count} von {max_count} gewünschten Modulen")
        
        # Platziere Module
        placed = 0
        start_x = x_min + margin + mod_w / 2
        start_y = y_min + margin + mod_h / 2
        
        for row in range(rows):
            for col in range(cols):
                if placed >= actual_count:
                    break
                
                x = start_x + col * (mod_w + spacing)
                y = start_y + row * (mod_h + spacing)
                
                # Z-Position: Deutlich ÜBER dem Dach für Sichtbarkeit
                module_z = z + 0.3  # 30cm über Dach statt 10cm
                
                print(f"    - Platziere Modul {placed + 1} bei ({x:.2f}, {y:.2f}, {module_z:.2f})")
                
                # Modul hinzufügen
                module = self.add_module(
                    x=x, y=y, z=module_z,
                    module_type=module_type,
                    dimensions=dimensions,
                    orientation=orientation,
                    roof_surface_id=surface.id
                )
                
                # Aufständerung für Flachdach
                if surface.roof_type == "Flachdach":
                    if mounting_type == "south":
                        # Klassische Süd-Aufständerung: 15° nach Süden geneigt
                        module.transform.rotation_x = 15.0
                        module.transform.rotation_z = 0.0  # Azimut Süd
                    elif mounting_type == "east_west":
                        # Ost-West-Aufständerung: Abwechselnd Ost/West (Dreieck)
                        # Gerade Spalten = Ost (Azimut -90°), ungerade = West (Azimut +90°)
                        module.transform.rotation_x = 15.0  # Neigung gleich
                        if col % 2 == 0:
                            module.transform.rotation_z = -90.0  # Ost
                            print(f"      -> Ost-Modul (Azimut -90°)")
                        else:
                            module.transform.rotation_z = 90.0  # West
                            print(f"      -> West-Modul (Azimut +90°)")
                
                placed += 1
            
            if placed >= actual_count:
                break
        
        return placed
    
    def _auto_place_gabled_roof(self, surface: RoofSurface, max_count: int,
                               module_type: ModuleType, dimensions: ModuleDimensions,
                               orientation: ModuleOrientation, spacing: float,
                               margin: float) -> int:
        """Automatische Platzierung auf Satteldach"""
        # TODO: Implementierung für Satteldach
        # Berücksichtige Dachneigung und zwei Dachflächen
        return 0
    
    # ========================================================================
    # SPEICHERN/LADEN
    # ========================================================================
    
    def to_dict(self) -> Dict:
        """Exportiert den gesamten Zustand als Dictionary"""
        return {
            "modules": {mid: m.to_dict() for mid, m in self.modules.items()},
            "groups": {gid: g.to_dict() for gid, g in self.groups.items()},
            "roof_surfaces": {sid: s.to_dict() for sid, s in self.roof_surfaces.items()},
            "next_module_id": self.next_module_id,
            "next_group_id": self.next_group_id,
            "next_surface_id": self.next_surface_id,
        }
    
    def to_json(self) -> str:
        """Exportiert als JSON-String"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModulePlacementManager':
        """Lädt aus Dictionary"""
        manager = cls()
        
        # Lade Dachflächen
        for sid_str, sdata in data.get("roof_surfaces", {}).items():
            surface = RoofSurface.from_dict(sdata)
            manager.roof_surfaces[surface.id] = surface
        
        # Lade Module
        for mid_str, mdata in data.get("modules", {}).items():
            module = PVModule.from_dict(mdata)
            manager.modules[module.id] = module
        
        # Lade Gruppen
        for gid_str, gdata in data.get("groups", {}).items():
            group = ModuleGroup.from_dict(gdata)
            manager.groups[group.id] = group
        
        # Aktualisiere Zähler
        manager.next_module_id = data.get("next_module_id", 1)
        manager.next_group_id = data.get("next_group_id", 1)
        manager.next_surface_id = data.get("next_surface_id", 1)
        
        return manager
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ModulePlacementManager':
        """Lädt aus JSON-String"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    # ========================================================================
    # STATISTIKEN
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken über die Platzierung zurück"""
        modules = self.get_all_modules()
        
        mono_count = sum(1 for m in modules if m.module_type == ModuleType.MONOCRYSTALLINE)
        poly_count = sum(1 for m in modules if m.module_type == ModuleType.POLYCRYSTALLINE)
        
        total_power = sum(m.dimensions.power_wp for m in modules)
        total_area = sum(m.dimensions.get_area() for m in modules)
        
        return {
            "total_modules": len(modules),
            "monocrystalline_count": mono_count,
            "polycrystalline_count": poly_count,
            "total_power_wp": total_power,
            "total_power_kwp": total_power / 1000.0,
            "total_area_m2": total_area,
            "groups_count": len(self.groups),
            "roof_surfaces_count": len(self.roof_surfaces),
        }
