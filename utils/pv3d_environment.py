"""
Interaktive Gebäude-Umgebung mit 3D-Objekten

Dieses Modul ermöglicht das Hinzufügen von Umgebungsobjekten (Bäume, Nachbargebäude,
Schornsteine, Antennen) zur 3D-Visualisierung und berechnet deren Verschattung.

Author: PV3D Team
Date: 2025-01-03
"""

from typing import Dict, List, Tuple, Any, Optional
import plotly.graph_objects as go
import numpy as np
import streamlit as st
from dataclasses import dataclass


@dataclass
class ShadowData:
    """Verschattungs-Daten eines Objekts."""
    corners: np.ndarray  # Schatten-Polygon-Ecken
    intensity: float  # Verschattungs-Intensität (0-1)
    source_object: str  # Name des verschattenden Objekts


class EnvironmentObject:
    """Basis-Klasse für Umgebungs-Objekte."""
    
    def __init__(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        width: float = 1.0,
        length: float = 1.0,
        height: float = 1.0,
        name: str = "Object"
    ):
        """
        Initialisiert Umgebungs-Objekt.
        
        Args:
            x: X-Position (Meter)
            y: Y-Position (Meter)
            z: Z-Position (Meter, Standard: 0 = Bodenniveau)
            width: Breite (Meter)
            length: Länge (Meter)
            height: Höhe (Meter)
            name: Name des Objekts
        """
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.length = length
        self.height = height
        self.name = name
    
    def to_mesh(self) -> go.Mesh3d:
        """
        Konvertiert Objekt zu Plotly Mesh.
        
        Returns:
            Plotly Mesh3d Objekt
        
        Raises:
            NotImplementedError: Muss in Subklasse implementiert werden
        """
        raise NotImplementedError("Subklasse muss to_mesh() implementieren")
    
    def calculate_shadow(
        self,
        sun_azimuth: float,
        sun_elevation: float
    ) -> ShadowData:
        """
        Berechnet Schatten des Objekts.
        
        Args:
            sun_azimuth: Sonnen-Azimuth in Grad (0° = Süd, 90° = West)
            sun_elevation: Sonnen-Elevation in Grad (0° = Horizont, 90° = Zenit)
        
        Returns:
            ShadowData mit Schatten-Polygon und Intensität
        """
        # Verhindere Division durch Null
        if sun_elevation <= 0:
            sun_elevation = 0.1
        
        # Berechne Schatten-Länge
        shadow_length = self.height / np.tan(np.radians(sun_elevation))
        
        # Berechne Schatten-Richtung
        shadow_direction = np.array([
            np.sin(np.radians(sun_azimuth)),
            np.cos(np.radians(sun_azimuth))
        ])
        
        # Schatten-Offset
        shadow_offset = shadow_direction * shadow_length
        
        # Objekt-Ecken (Grundfläche)
        corners = np.array([
            [self.x - self.width/2, self.y - self.length/2],
            [self.x + self.width/2, self.y - self.length/2],
            [self.x + self.width/2, self.y + self.length/2],
            [self.x - self.width/2, self.y + self.length/2]
        ])
        
        # Schatten-Ecken
        shadow_corners = corners + shadow_offset
        
        # Verschattungs-Intensität (höhere Sonne = schwächerer Schatten)
        intensity = 1.0 - (sun_elevation / 90.0) * 0.5
        
        return ShadowData(
            corners=shadow_corners,
            intensity=intensity,
            source_object=self.name
        )
    
    def _create_cylinder(
        self,
        x: float, y: float, z: float,
        radius: float,
        height: float,
        color: str,
        segments: int = 16
    ) -> go.Mesh3d:
        """
        Erstellt Zylinder-Mesh.
        
        Args:
            x, y, z: Position des Zylinder-Mittelpunkts (Basis)
            radius: Radius des Zylinders
            height: Höhe des Zylinders
            color: Farbe (Hex-Code)
            segments: Anzahl der Segmente (höher = runder)
        
        Returns:
            Plotly Mesh3d für Zylinder
        """
        # Erstelle Kreis-Punkte
        theta = np.linspace(0, 2*np.pi, segments, endpoint=False)
        
        # Basis-Kreis
        x_base = x + radius * np.cos(theta)
        y_base = y + radius * np.sin(theta)
        z_base = np.full(segments, z)
        
        # Top-Kreis
        x_top = x + radius * np.cos(theta)
        y_top = y + radius * np.sin(theta)
        z_top = np.full(segments, z + height)
        
        # Kombiniere Punkte
        vertices_x = np.concatenate([x_base, x_top, [x], [x]])
        vertices_y = np.concatenate([y_base, y_top, [y], [y]])
        vertices_z = np.concatenate([z_base, z_top, [z], [z + height]])
        
        # Erstelle Dreiecke (Faces)
        i_faces = []
        j_faces = []
        k_faces = []
        
        center_base_idx = 2 * segments
        center_top_idx = 2 * segments + 1
        
        # Mantel
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            
            # Dreieck 1
            i_faces.append(seg)
            j_faces.append(next_seg)
            k_faces.append(seg + segments)
            
            # Dreieck 2
            i_faces.append(next_seg)
            j_faces.append(next_seg + segments)
            k_faces.append(seg + segments)
        
        # Basis
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            i_faces.append(center_base_idx)
            j_faces.append(seg)
            k_faces.append(next_seg)
        
        # Top
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            i_faces.append(center_top_idx)
            j_faces.append(next_seg + segments)
            k_faces.append(seg + segments)
        
        return go.Mesh3d(
            x=vertices_x,
            y=vertices_y,
            z=vertices_z,
            i=i_faces,
            j=j_faces,
            k=k_faces,
            color=color,
            opacity=1.0,
            name=self.name,
            hovertemplate=f'<b>{self.name}</b><br>Position: ({x:.1f}, {y:.1f}, {z:.1f})<extra></extra>'
        )
    
    def _create_cone(
        self,
        x: float, y: float, z: float,
        radius: float,
        height: float,
        color: str,
        segments: int = 16
    ) -> go.Mesh3d:
        """
        Erstellt Kegel-Mesh.
        
        Args:
            x, y, z: Position der Kegel-Basis
            radius: Radius der Basis
            height: Höhe des Kegels
            color: Farbe (Hex-Code)
            segments: Anzahl der Segmente
        
        Returns:
            Plotly Mesh3d für Kegel
        """
        # Erstelle Kreis-Punkte für Basis
        theta = np.linspace(0, 2*np.pi, segments, endpoint=False)
        
        x_base = x + radius * np.cos(theta)
        y_base = y + radius * np.sin(theta)
        z_base = np.full(segments, z)
        
        # Spitze und Zentrum
        vertices_x = np.concatenate([x_base, [x], [x]])
        vertices_y = np.concatenate([y_base, [y], [y]])
        vertices_z = np.concatenate([z_base, [z + height], [z]])
        
        # Erstelle Dreiecke
        i_faces = []
        j_faces = []
        k_faces = []
        
        apex_idx = segments
        center_base_idx = segments + 1
        
        # Mantel
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            i_faces.append(apex_idx)
            j_faces.append(seg)
            k_faces.append(next_seg)
        
        # Basis
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            i_faces.append(center_base_idx)
            j_faces.append(next_seg)
            k_faces.append(seg)
        
        return go.Mesh3d(
            x=vertices_x,
            y=vertices_y,
            z=vertices_z,
            i=i_faces,
            j=j_faces,
            k=k_faces,
            color=color,
            opacity=1.0,
            name=self.name,
            hovertemplate=f'<b>{self.name}</b><br>Position: ({x:.1f}, {y:.1f}, {z:.1f})<extra></extra>'
        )


class Tree(EnvironmentObject):
    """Baum-Objekt mit Stamm und Krone."""
    
    def __init__(
        self,
        x: float,
        y: float,
        height: float = 5.0,
        tree_type: str = "Laubbaum",
        **kwargs
    ):
        """
        Initialisiert Baum.
        
        Args:
            x: X-Position
            y: Y-Position
            height: Gesamthöhe des Baums (Meter)
            tree_type: Baumart ("Laubbaum", "Nadelbaum", "Palme")
        """
        super().__init__(x, y, 0, 1.0, 1.0, height, f"Baum ({tree_type})")
        self.tree_type = tree_type
        self.trunk_height = height * 0.4
        self.crown_radius = height * 0.3
        
        # Anpassungen je nach Baumart
        if tree_type == "Nadelbaum":
            self.crown_radius = height * 0.2  # Schmaler
        elif tree_type == "Palme":
            self.trunk_height = height * 0.7  # Höherer Stamm
            self.crown_radius = height * 0.25
    
    def to_mesh(self) -> List[go.Mesh3d]:
        """
        Erstellt Baum-Mesh (Stamm + Krone).
        
        Returns:
            Liste mit [Stamm-Mesh, Kronen-Mesh]
        """
        meshes = []
        
        # Stamm (Zylinder)
        trunk = self._create_cylinder(
            self.x, self.y, 0,
            radius=0.2,
            height=self.trunk_height,
            color='#8B4513'  # Braun
        )
        meshes.append(trunk)
        
        # Krone (Kegel oder Kugel-Approximation)
        if self.tree_type == "Nadelbaum":
            # Spitzer Kegel
            crown = self._create_cone(
                self.x, self.y, self.trunk_height,
                radius=self.crown_radius,
                height=self.height - self.trunk_height,
                color='#228B22'  # Dunkelgrün
            )
            meshes.append(crown)
        else:
            # Runder Kegel (Laubbaum/Palme)
            crown = self._create_cone(
                self.x, self.y, self.trunk_height,
                radius=self.crown_radius,
                height=self.height - self.trunk_height,
                color='#32CD32' if self.tree_type == "Palme" else '#228B22'
            )
            meshes.append(crown)
        
        return meshes


class NeighborBuilding(EnvironmentObject):
    """Nachbargebäude."""
    
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        length: float,
        height: float,
        building_type: str = "Wohnhaus",
        **kwargs
    ):
        """
        Initialisiert Nachbargebäude.
        
        Args:
            x: X-Position (Zentrum)
            y: Y-Position (Zentrum)
            width: Breite (Meter)
            length: Länge (Meter)
            height: Höhe (Meter)
            building_type: Gebäudetyp ("Wohnhaus", "Hochhaus", "Garage")
        """
        super().__init__(x, y, 0, width, length, height, f"Nachbargebäude ({building_type})")
        self.building_type = building_type
    
    def to_mesh(self) -> go.Mesh3d:
        """
        Erstellt Gebäude-Mesh (Box).
        
        Returns:
            Plotly Mesh3d für Gebäude
        """
        from utils.pv3d_plotly import create_complete_box
        
        # Farbe je nach Gebäudetyp
        colors = {
            "Wohnhaus": '#D3D3D3',  # Hellgrau
            "Hochhaus": '#A9A9A9',  # Dunkelgrau
            "Garage": '#C0C0C0'     # Silber
        }
        color = colors.get(self.building_type, '#D3D3D3')
        
        return create_complete_box(
            x_min=self.x - self.width/2,
            x_max=self.x + self.width/2,
            y_min=self.y - self.length/2,
            y_max=self.y + self.length/2,
            z_min=0,
            z_max=self.height,
            color=color,
            name=self.name
        )


class Chimney(EnvironmentObject):
    """Schornstein."""
    
    def __init__(
        self,
        x: float,
        y: float,
        height: float = 3.0,
        **kwargs
    ):
        """
        Initialisiert Schornstein.
        
        Args:
            x: X-Position
            y: Y-Position
            height: Höhe (Meter)
        """
        super().__init__(x, y, 0, 0.5, 0.5, height, "Schornstein")
    
    def to_mesh(self) -> go.Mesh3d:
        """
        Erstellt Schornstein-Mesh (Zylinder).
        
        Returns:
            Plotly Mesh3d für Schornstein
        """
        return self._create_cylinder(
            self.x, self.y, 0,
            radius=0.25,
            height=self.height,
            color='#8B0000'  # Dunkelrot (Ziegel)
        )


class Antenna(EnvironmentObject):
    """Antenne."""
    
    def __init__(
        self,
        x: float,
        y: float,
        height: float = 2.0,
        **kwargs
    ):
        """
        Initialisiert Antenne.
        
        Args:
            x: X-Position
            y: Y-Position
            height: Höhe (Meter)
        """
        super().__init__(x, y, 0, 0.2, 0.2, height, "Antenne")
    
    def to_mesh(self) -> go.Mesh3d:
        """
        Erstellt Antennen-Mesh (dünner Zylinder).
        
        Returns:
            Plotly Mesh3d für Antenne
        """
        return self._create_cylinder(
            self.x, self.y, 0,
            radius=0.1,
            height=self.height,
            color='#C0C0C0'  # Silber (Metall)
        )


def render_environment_editor() -> Dict[str, Any]:
    """
    Rendert UI für Umgebungs-Editor.
    
    Ermöglicht das Hinzufügen von Umgebungsobjekten zur Szene.
    
    Returns:
        Dictionary mit:
            - add_object: str or None - Typ des hinzuzufügenden Objekts
            - object_params: Dict - Parameter für neues Objekt
    
    Example:
        >>> result = render_environment_editor()
        >>> if result["add_object"]:
        ...     obj_type = result["add_object"]
        ...     params = result["object_params"]
        ...     # Erstelle Objekt basierend auf Typ
    """
    st.sidebar.subheader("🌳 Umgebung")
    
    object_type = st.sidebar.selectbox(
        "Objekt hinzufügen",
        ["Keins", "Baum", "Nachbargebäude", "Schornstein", "Antenne"],
        key="environment_object_type"
    )
    
    if object_type != "Keins":
        st.sidebar.write(f"**{object_type} platzieren:**")
        
        # Gemeinsame Parameter
        x = st.sidebar.slider(
            "X-Position (m)",
            -20.0, 20.0, 0.0, 0.5,
            key="env_obj_x"
        )
        y = st.sidebar.slider(
            "Y-Position (m)",
            -20.0, 20.0, 0.0, 0.5,
            key="env_obj_y"
        )
        
        # Typ-spezifische Parameter
        if object_type == "Baum":
            height = st.sidebar.slider(
                "Höhe (m)",
                2.0, 15.0, 5.0, 0.5,
                key="tree_height"
            )
            tree_type = st.sidebar.selectbox(
                "Baumart",
                ["Laubbaum", "Nadelbaum", "Palme"],
                key="tree_type"
            )
            params = {
                "x": x,
                "y": y,
                "height": height,
                "tree_type": tree_type
            }
        
        elif object_type == "Nachbargebäude":
            width = st.sidebar.slider(
                "Breite (m)",
                5.0, 20.0, 10.0, 1.0,
                key="building_width"
            )
            length = st.sidebar.slider(
                "Länge (m)",
                5.0, 20.0, 10.0, 1.0,
                key="building_length"
            )
            height = st.sidebar.slider(
                "Höhe (m)",
                3.0, 30.0, 10.0, 1.0,
                key="building_height"
            )
            building_type = st.sidebar.selectbox(
                "Gebäudetyp",
                ["Wohnhaus", "Hochhaus", "Garage"],
                key="building_type"
            )
            params = {
                "x": x,
                "y": y,
                "width": width,
                "length": length,
                "height": height,
                "building_type": building_type
            }
        
        elif object_type == "Schornstein":
            height = st.sidebar.slider(
                "Höhe (m)",
                1.0, 5.0, 3.0, 0.5,
                key="chimney_height"
            )
            params = {
                "x": x,
                "y": y,
                "height": height
            }
        
        elif object_type == "Antenne":
            height = st.sidebar.slider(
                "Höhe (m)",
                1.0, 5.0, 2.0, 0.5,
                key="antenna_height"
            )
            params = {
                "x": x,
                "y": y,
                "height": height
            }
        
        else:
            params = {"x": x, "y": y}
        
        # Hinzufügen-Button
        if st.sidebar.button(f"➕ {object_type} hinzufügen", key="add_env_object"):
            return {
                "add_object": object_type,
                "object_params": params
            }
    
    return {"add_object": None, "object_params": {}}


def add_environment_objects_to_scene(
    fig: go.Figure,
    objects: List[EnvironmentObject]
) -> go.Figure:
    """
    Fügt Umgebungsobjekte zur 3D-Szene hinzu.
    
    Args:
        fig: Plotly Figure
        objects: Liste von EnvironmentObject-Instanzen
    
    Returns:
        Aktualisierte Figure mit Umgebungsobjekten
    
    Example:
        >>> tree = Tree(x=5, y=5, height=8)
        >>> building = NeighborBuilding(x=-10, y=0, width=8, length=10, height=12)
        >>> fig = add_environment_objects_to_scene(fig, [tree, building])
    """
    for obj in objects:
        meshes = obj.to_mesh()
        
        # to_mesh() kann einzelnes Mesh oder Liste zurückgeben
        if isinstance(meshes, list):
            for mesh in meshes:
                fig.add_trace(mesh)
        else:
            fig.add_trace(meshes)
    
    return fig


def calculate_environment_shading(
    objects: List[EnvironmentObject],
    module_positions: List[Tuple[float, float, float]],
    sun_azimuth: float,
    sun_elevation: float
) -> Dict[int, float]:
    """
    Berechnet Verschattung durch Umgebungsobjekte auf Module.
    
    Args:
        objects: Liste von Umgebungsobjekten
        module_positions: Liste von Modulpositionen (x, y, z)
        sun_azimuth: Sonnen-Azimuth in Grad
        sun_elevation: Sonnen-Elevation in Grad
    
    Returns:
        Dictionary: {module_index: shading_factor}
        shading_factor: 0.0 (keine Verschattung) bis 1.0 (vollständig verschattet)
    
    Example:
        >>> shading = calculate_environment_shading(
        ...     objects=[tree, building],
        ...     module_positions=[(0, 0, 0.3), (2, 0, 0.3)],
        ...     sun_azimuth=180,
        ...     sun_elevation=45
        ... )
        >>> print(shading)  # {0: 0.0, 1: 0.7}
    """
    shading_factors = {}
    
    for i, (mod_x, mod_y, mod_z) in enumerate(module_positions):
        total_shading = 0.0
        
        for obj in objects:
            # Berechne Schatten des Objekts
            shadow_data = obj.calculate_shadow(sun_azimuth, sun_elevation)
            
            # Prüfe ob Modul im Schatten liegt
            if _point_in_polygon((mod_x, mod_y), shadow_data.corners):
                # Verschattung abhängig von Objekthöhe und Abstand
                distance = np.sqrt((obj.x - mod_x)**2 + (obj.y - mod_y)**2)
                height_factor = min(1.0, obj.height / 10.0)  # Normalisiert auf 10m
                distance_factor = max(0.0, 1.0 - distance / 20.0)  # Abnahme über 20m
                
                shading = shadow_data.intensity * height_factor * distance_factor
                total_shading = min(1.0, total_shading + shading)
        
        shading_factors[i] = total_shading
    
    return shading_factors


def _point_in_polygon(point: Tuple[float, float], polygon: np.ndarray) -> bool:
    """
    Prüft ob Punkt innerhalb eines Polygons liegt (Ray-Casting-Algorithmus).
    
    Args:
        point: (x, y) Punkt
        polygon: Nx2 Array mit Polygon-Ecken
    
    Returns:
        True wenn Punkt im Polygon liegt
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside
