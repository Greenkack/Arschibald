"""
3D PV-Visualisierung mit Plotly

Hochwertige 3D-Visualisierung für Photovoltaik-Anlagen auf Gebäuden.
Verwendet Plotly für interaktive, browserbasierte 3D-Grafiken.
"""

import math
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

# Import der Datenklassen aus der Original-Datei
from utils.pv3d import (
    BuildingDims, 
    LayoutConfig, 
    AdvancedLayoutConfig,
    ModuleTransform,
    ModuleGroup,
    PV_W, 
    PV_H, 
    PV_T,
    ROOF_COLORS,
    _deg_to_rad
)


# ============================================================================
# VOLLSTÄNDIGE 3D MESH GENERATOREN
# ============================================================================

def create_complete_box(x_min, x_max, y_min, y_max, z_min, z_max, color="#d4d4d4", name="Box"):
    """Erstellt eine vollständige Box mit allen 6 Seiten - hochqualitativ."""
    # 8 Ecken der Box
    vertices = np.array([
        [x_min, y_min, z_min],  # 0: vorne links unten
        [x_max, y_min, z_min],  # 1: vorne rechts unten
        [x_max, y_max, z_min],  # 2: hinten rechts unten
        [x_min, y_max, z_min],  # 3: hinten links unten
        [x_min, y_min, z_max],  # 4: vorne links oben
        [x_max, y_min, z_max],  # 5: vorne rechts oben
        [x_max, y_max, z_max],  # 6: hinten rechts oben
        [x_min, y_max, z_max],  # 7: hinten links oben
    ])
    
    # Alle 12 Dreiecke für 6 vollständige Seiten (2 Dreiecke pro Seite)
    # Unten (z_min): 0,1,2 und 0,2,3
    # Oben (z_max): 4,6,5 und 4,7,6
    # Vorne (y_min): 0,5,1 und 0,4,5
    # Hinten (y_max): 2,6,7 und 2,7,3
    # Links (x_min): 0,3,7 und 0,7,4
    # Rechts (x_max): 1,5,6 und 1,6,2
    i = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
    j = [1, 2, 6, 7, 5, 4, 6, 7, 3, 7, 5, 6]
    k = [2, 3, 5, 6, 1, 5, 7, 3, 7, 4, 6, 2]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.5, roughness=0.3, fresnel=0.2),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_gabled_roof_complete(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein VOLLSTÄNDIG GESCHLOSSENES Satteldach - wirklich KEINE Löcher mehr!"""
    half_l = length / 2
    half_w = width / 2
    
    # 6 Punkte für Satteldach
    vertices = np.array([
        [-half_l, -half_w, base_z],        # 0: Ecke vorne links
        [half_l, -half_w, base_z],         # 1: Ecke vorne rechts
        [half_l, half_w, base_z],          # 2: Ecke hinten rechts
        [-half_l, half_w, base_z],         # 3: Ecke hinten links
        [-half_l, 0, base_z + height],     # 4: First links oben
        [half_l, 0, base_z + height],      # 5: First rechts oben
    ])
    
    # ALLE Flächen als Dreiecke - komplett geschlossen:
    # Linke Dachfläche: (0,4,5) und (0,5,1)
    # Rechte Dachfläche: (3,2,5) und (3,5,4)
    # Giebel LINKS vollständig: (0,3,4)
    # Giebel RECHTS vollständig: (1,5,2)
    i = [0, 0, 3, 3, 0, 1]
    j = [4, 5, 2, 5, 3, 5]
    k = [5, 1, 5, 4, 4, 2]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.6, roughness=0.2, fresnel=0.3),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_hipped_roof(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein VOLLSTÄNDIG GESCHLOSSENES Walmdach - keine Löcher!"""
    half_l = length / 2
    half_w = width / 2
    
    # Walmdach mit First-Linie
    first_length = length * 0.4
    vertices = np.array([
        [-half_l, -half_w, base_z],              # 0: Ecke vorne links
        [half_l, -half_w, base_z],               # 1: Ecke vorne rechts
        [half_l, half_w, base_z],                # 2: Ecke hinten rechts
        [-half_l, half_w, base_z],               # 3: Ecke hinten links
        [-first_length/2, 0, base_z + height],   # 4: First Anfang
        [first_length/2, 0, base_z + height],    # 5: First Ende
    ])
    
    # KOMPLETT GESCHLOSSEN - alle Flächen:
    # Walm links: 0-3-4
    # Walm rechts: 1-2-5
    # Dachfläche vorne: 0-4-5 und 0-5-1
    # Dachfläche hinten: 3-5-4 und 3-2-5
    i = [0, 1, 0, 0, 3, 3]
    j = [3, 2, 4, 5, 5, 2]
    k = [4, 5, 5, 1, 4, 5]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.6, roughness=0.2, fresnel=0.3),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_half_hipped_roof(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein VOLLSTÄNDIG GESCHLOSSENES Krüppelwalmdach - Satteldach mit abgeschrägten Giebeln!"""
    half_l = length / 2
    half_w = width / 2
    
    # Krüppelwalm: First ist kürzer, Giebel sind teilweise abgewalmt
    first_offset = length * 0.15  # First ist 30% kürzer (15% pro Seite)
    hip_height = height * 0.6     # Walm-Punkte bei 60% der Firsthöhe
    
    vertices = np.array([
        [-half_l, -half_w, base_z],                    # 0: Ecke vorne links
        [half_l, -half_w, base_z],                     # 1: Ecke vorne rechts
        [half_l, half_w, base_z],                      # 2: Ecke hinten rechts
        [-half_l, half_w, base_z],                     # 3: Ecke hinten links
        [-half_l + first_offset, 0, base_z + height],  # 4: First Anfang links
        [half_l - first_offset, 0, base_z + height],   # 5: First Ende rechts
        [-half_l, 0, base_z + hip_height],             # 6: Walm-Punkt links
        [half_l, 0, base_z + hip_height],              # 7: Walm-Punkt rechts
    ])
    
    # ALLE Flächen komplett geschlossen:
    # Hauptdachflächen vorne/hinten: (0,4,5), (0,5,1) und (3,2,5), (3,5,4)
    # Walme links: (0,6,4), (3,4,6)
    # Walme rechts: (1,5,7), (2,7,5)
    # Untere Giebel-Dreiecke: (0,3,6) und (1,7,2)
    i = [0, 0, 3, 3, 0, 3, 1, 2, 0, 1]
    j = [4, 5, 2, 5, 6, 4, 5, 7, 3, 7]
    k = [5, 1, 5, 4, 4, 6, 7, 5, 6, 2]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.6, roughness=0.2, fresnel=0.3),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_pent_roof(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein VOLLSTÄNDIG GESCHLOSSENES Pultdach - wirklich keine Löcher!"""
    half_l = length / 2
    half_w = width / 2
    
    vertices = np.array([
        [-half_l, -half_w, base_z],              # 0: vorne links niedrig
        [half_l, -half_w, base_z],               # 1: vorne rechts niedrig
        [half_l, half_w, base_z],                # 2: hinten rechts niedrig
        [-half_l, half_w, base_z],               # 3: hinten links niedrig
        [-half_l, -half_w, base_z + height],     # 4: vorne links hoch
        [half_l, -half_w, base_z + height],      # 5: vorne rechts hoch
    ])
    
    # ALLE Flächen komplett geschlossen:
    # Hauptdachfläche schräg: (4,5,2) und (4,2,3)
    # Stirnwand links: (0,4,3)
    # Stirnwand rechts: (1,2,5)
    # Vorderseite hoch: (4,5,1) und (4,1,0)
    i = [4, 4, 0, 1, 4, 4]
    j = [5, 2, 4, 2, 5, 1]
    k = [2, 3, 3, 5, 1, 0]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.6, roughness=0.2, fresnel=0.3),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_pyramid_roof(length, width, height, base_z, color="#c96a2d", name="Roof"):
    """Erstellt ein Zeltdach - pyramidenförmiges Dach."""
    half_l = length / 2
    half_w = width / 2
    
    # Zeltdach: Alle Seiten laufen zu einem Punkt zusammen
    vertices = np.array([
        [-half_l, -half_w, base_z],        # 0: vorne links
        [half_l, -half_w, base_z],         # 1: vorne rechts
        [half_l, half_w, base_z],          # 2: hinten rechts
        [-half_l, half_w, base_z],         # 3: hinten links
        [0, 0, base_z + height],           # 4: Spitze
    ])
    
    # 4 Dreiecke für alle Seiten
    i = [0, 1, 2, 3]
    j = [1, 2, 3, 0]
    k = [4, 4, 4, 4]
    
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color=color,
        opacity=1.0,
        name=name,
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.6, roughness=0.2, fresnel=0.3),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=2)
    )


def create_gabled_roof_with_dormer(length, width, height, base_z, 
                                   dormer_width=2.0, dormer_height=0.5, dormer_depth=1.0,
                                   dormer_position=0.0, color="#c96a2d", name="Roof"):
    """
    Erstellt ein VOLLSTÄNDIG GESCHLOSSENES Satteldach mit DREIECK-GAUBE!
    
    Gaube = Dreieckiger Giebel (wie vom Satteldach) wird FLACH auf Dachfläche gelegt.
    Die Ecken wo das Dreieck durchs Dach stößt werden abgeschnitten.
    Das ist eine klassische Giebelgaube / Spitzgaube.
    """
    half_l = length / 2
    half_w = width / 2
    
    # === HAUPTDACH: KOMPLETT GESCHLOSSEN ===
    main_roof = create_gabled_roof_complete(
        length=length,
        width=width,
        height=height,
        base_z=base_z,
        color=color,
        name=name
    )
    
    # === DREIECK-GAUBE ===
    dormer_x = dormer_position  # Position entlang Hauptfirst
    dormer_half_w = dormer_width / 2
    
    # Position auf vorderer Dachfläche (näher am First = weiter oben)
    dormer_y_on_roof = -width / 6  # War 1/3, jetzt 1/6 = näher am First!
    # Z auf Dachschräge: z = base_z + height * (1 - abs(y) / (width/2))
    dormer_z_base = base_z + height * (1 - abs(dormer_y_on_roof) / (width/2))
    
    # Gaube ragt nach vorne raus (aus dem Dach)
    dormer_front_y = dormer_y_on_roof - dormer_depth
    dormer_front_z = base_z + height * (1 - abs(dormer_front_y) / (width/2))
    
    # Dreiecksspitze (Giebelspitze) - jetzt flacher!
    dormer_peak_z = dormer_z_base + dormer_height
    
    # === GAUBE VERTICES (Dreieck auf Dachfläche) ===
    dormer_vertices = np.array([
        # BODEN: Rechteck auf Hauptdach (wo Gaube aufsitzt)
        [dormer_x - dormer_half_w, dormer_y_on_roof, dormer_z_base],      # 0: hinten links
        [dormer_x + dormer_half_w, dormer_y_on_roof, dormer_z_base],      # 1: hinten rechts
        [dormer_x + dormer_half_w, dormer_front_y, dormer_front_z],       # 2: vorne rechts
        [dormer_x - dormer_half_w, dormer_front_y, dormer_front_z],       # 3: vorne links
        
        # DREIECKSSPITZE (in der Mitte oben)
        [dormer_x, dormer_y_on_roof, dormer_peak_z],                       # 4: Spitze hinten
        [dormer_x, dormer_front_y, dormer_peak_z],                         # 5: Spitze vorne
    ])
    
    # === GAUBE DREIECKE ===
    i_dormer = []
    j_dormer = []
    k_dormer = []
    
    # BODEN (Rechteck auf Dachfläche) - 2 Dreiecke
    i_dormer.extend([0, 2])
    j_dormer.extend([1, 3])
    k_dormer.extend([2, 0])
    
    # VORDERE GIEBEL-DREIECK (das charakteristische Dreieck!)
    i_dormer.extend([3])
    j_dormer.extend([2])
    k_dormer.extend([5])
    
    # HINTERE GIEBEL-DREIECK
    i_dormer.extend([0])
    j_dormer.extend([4])
    k_dormer.extend([1])
    
    # LINKE DACHFLÄCHE (von unten links zur Spitze)
    i_dormer.extend([0, 3])
    j_dormer.extend([3, 5])
    k_dormer.extend([4, 4])
    
    # RECHTE DACHFLÄCHE (von unten rechts zur Spitze)
    i_dormer.extend([1, 2])
    j_dormer.extend([4, 5])
    k_dormer.extend([2, 5])
    
    # === GAUBE MESH ===
    dormer_mesh = go.Mesh3d(
        x=dormer_vertices[:, 0],
        y=dormer_vertices[:, 1],
        z=dormer_vertices[:, 2],
        i=i_dormer, j=j_dormer, k=k_dormer,
        color=color,  # Gleiche Farbe wie Hauptdach
        opacity=1.0,
        name="Dreieck-Gaube",
        showlegend=False,
        flatshading=False,
        lighting=dict(ambient=0.7, diffuse=0.9, specular=0.5, roughness=0.3, fresnel=0.2),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=1)
    )
    
    # === FENSTER IM VORDEREN GIEBEL ===
    # Fenster als Dreieck im Giebel (oben schmaler)
    window_margin_side = 0.4
    window_margin_bottom = 0.3
    window_height_factor = 0.6  # Fenster geht 60% hoch
    
    window_vertices = np.array([
        # Unten links
        [dormer_x - dormer_half_w + window_margin_side, dormer_front_y - 0.01, 
         dormer_front_z + window_margin_bottom],
        # Unten rechts
        [dormer_x + dormer_half_w - window_margin_side, dormer_front_y - 0.01, 
         dormer_front_z + window_margin_bottom],
        # Oben (Spitze, etwas unter der Giebelspitze)
        [dormer_x, dormer_front_y - 0.01, 
         dormer_front_z + window_margin_bottom + dormer_height * window_height_factor],
    ])
    
    window_mesh = go.Mesh3d(
        x=window_vertices[:, 0],
        y=window_vertices[:, 1],
        z=window_vertices[:, 2],
        i=[0],
        j=[1],
        k=[2],
        color="#2E4057",  # Dunkelblau (Fenster)
        opacity=1.0,
        name="Fenster",
        showlegend=False,
        flatshading=True,
        lighting=dict(ambient=0.8, diffuse=0.5, specular=0.9, roughness=0.1, fresnel=0.5),
        lightposition=dict(x=1000, y=1000, z=2000),
        contour=dict(show=True, color='black', width=1)
    )
    
    # Rückgabe: Hauptdach + Gaube + Fenster
    return [main_roof, dormer_mesh, window_mesh]


def create_pv_module_3d(x, y, z, azimuth_deg=0, tilt_deg=15, color="#1a1a2e", selected=False, show_mounting=True):
    """
    Erstellt ein detailliertes PV-Modul mit Dicke und korrekter Rotation.
    Gibt Tuple zurück: (mesh, vertices) für Kanten-Rendering.
    
    FIX: Aufständerung wird jetzt deutlicher dargestellt durch:
    - Erhöhte Z-Position bei Neigung > 5°
    - Optionale Montage-Gestelle (show_mounting=True)
    """
    # Lokale Koordinaten (Modul zentriert im Ursprung)
    hw = PV_W / 2
    hh = PV_H / 2
    ht = PV_T / 2
    
    # FIX: Bei Aufständerung (tilt > 5°) erhöhe Z-Position um Gestell-Höhe
    if tilt_deg > 5.0 and show_mounting:
        # Gestell-Höhe abhängig von Neigung (min 0.3m, max 0.8m)
        mounting_height = 0.3 + (tilt_deg / 90.0) * 0.5
        z += mounting_height
    
    # 8 Ecken des Moduls (wie ein flacher Quader)
    local_vertices = np.array([
        [-hw, -hh, -ht],  # 0: links vorne unten
        [hw, -hh, -ht],   # 1: rechts vorne unten
        [hw, hh, -ht],    # 2: rechts hinten unten
        [-hw, hh, -ht],   # 3: links hinten unten
        [-hw, -hh, ht],   # 4: links vorne oben
        [hw, -hh, ht],    # 5: rechts vorne oben
        [hw, hh, ht],     # 6: rechts hinten oben
        [-hw, hh, ht],    # 7: links hinten oben
    ])
    
    # Rotation um Y-Achse (Tilt/Neigung)
    tilt_rad = np.deg2rad(tilt_deg)
    Ry = np.array([
        [np.cos(tilt_rad), 0, np.sin(tilt_rad)],
        [0, 1, 0],
        [-np.sin(tilt_rad), 0, np.cos(tilt_rad)]
    ])
    
    # Rotation um Z-Achse (Azimuth)
    az_rad = np.deg2rad(azimuth_deg)
    Rz = np.array([
        [np.cos(az_rad), -np.sin(az_rad), 0],
        [np.sin(az_rad), np.cos(az_rad), 0],
        [0, 0, 1]
    ])
    
    # Kombinierte Rotation: erst Tilt, dann Azimuth
    R = Rz @ Ry
    
    # Rotiere alle Vertices
    rotated = (R @ local_vertices.T).T
    
    # Verschiebe zur finalen Position
    final_vertices = rotated + np.array([x, y, z])
    
    # Alle 12 Dreiecke für vollständigen Quader
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 5, 5, 1, 1, 6, 6, 2, 2, 7, 7, 3, 3]
    j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 4, 1, 6, 4, 5, 0, 7, 5, 6, 1, 4, 6, 7, 2]
    k = [3, 2, 5, 6, 6, 7, 7, 4, 7, 6, 5, 4, 4, 5, 0, 4, 5, 6, 1, 2, 6, 7, 2, 3]
    
    module_color = "#ff6b35" if selected else color
    
    mesh = go.Mesh3d(
        x=final_vertices[:, 0],
        y=final_vertices[:, 1],
        z=final_vertices[:, 2],
        i=i, j=j, k=k,
        color=module_color,
        opacity=0.95,
        name="PV Module",
        showlegend=False,
        lighting=dict(ambient=0.5, diffuse=0.9, specular=0.5, roughness=0.2),
        lightposition=dict(x=100, y=100, z=100),
        contour=dict(show=True, color='black', width=1)
    )
    
    return mesh, final_vertices


def create_sun_marker(azimuth_deg, elevation_deg, distance=20.0):
    """Erstellt eine Sonne als leuchtenden Marker."""
    # Konvertiere Azimuth/Elevation zu kartesischen Koordinaten
    az_rad = np.deg2rad(azimuth_deg)
    el_rad = np.deg2rad(elevation_deg)
    
    x = distance * np.cos(el_rad) * np.sin(az_rad)
    y = distance * np.cos(el_rad) * np.cos(az_rad)
    z = distance * np.sin(el_rad)
    
    return go.Scatter3d(
        x=[x], y=[y], z=[z],
        mode='markers',
        marker=dict(
            size=20,
            color='gold',
            symbol='circle',
            line=dict(color='orange', width=3)
        ),
        name='☀️ Sonne',
        showlegend=True,
        hovertemplate=f'Sonne<br>Azimuth: {azimuth_deg:.1f}°<br>Elevation: {elevation_deg:.1f}°<extra></extra>'
    )


# ============================================================================
# KANTEN-LINIEN FÜR 3D-MESHES
# ============================================================================

def create_box_edges(x_min, x_max, y_min, y_max, z_min, z_max, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für eine Box."""
    # 8 Ecken der Box
    corners = np.array([
        [x_min, y_min, z_min],  # 0
        [x_max, y_min, z_min],  # 1
        [x_max, y_max, z_min],  # 2
        [x_min, y_max, z_min],  # 3
        [x_min, y_min, z_max],  # 4
        [x_max, y_min, z_max],  # 5
        [x_max, y_max, z_max],  # 6
        [x_min, y_max, z_max],  # 7
    ])
    
    # 12 Kanten einer Box (jede Kante einmal)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Untere Fläche
        (4, 5), (5, 6), (6, 7), (7, 4),  # Obere Fläche
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertikale Kanten
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([corners[start][0], corners[end][0], None])
        y_lines.extend([corners[start][1], corners[end][1], None])
        z_lines.extend([corners[start][2], corners[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_gabled_roof_edges(length, width, height, base_z, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für ein Satteldach."""
    half_l = length / 2
    half_w = width / 2
    
    # 6 Punkte des Satteldachs
    points = np.array([
        [-half_l, -half_w, base_z],        # 0
        [half_l, -half_w, base_z],         # 1
        [half_l, half_w, base_z],          # 2
        [-half_l, half_w, base_z],         # 3
        [-half_l, 0, base_z + height],     # 4
        [half_l, 0, base_z + height],      # 5
    ])
    
    # Kanten: Grundfläche + First + Dachkanten
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Basis-Rechteck
        (4, 5),                           # First
        (0, 4), (1, 5), (2, 5), (3, 4)   # Dachkanten zu First
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([points[start][0], points[end][0], None])
        y_lines.extend([points[start][1], points[end][1], None])
        z_lines.extend([points[start][2], points[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_hipped_roof_edges(length, width, height, base_z, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für ein Walmdach."""
    half_l = length / 2
    half_w = width / 2
    first_length = length * 0.4
    
    points = np.array([
        [-half_l, -half_w, base_z],              # 0
        [half_l, -half_w, base_z],               # 1
        [half_l, half_w, base_z],                # 2
        [-half_l, half_w, base_z],               # 3
        [-first_length/2, 0, base_z + height],   # 4
        [first_length/2, 0, base_z + height],    # 5
    ])
    
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Basis
        (4, 5),                           # First
        (0, 4), (1, 5), (2, 5), (3, 4)   # Dachkanten
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([points[start][0], points[end][0], None])
        y_lines.extend([points[start][1], points[end][1], None])
        z_lines.extend([points[start][2], points[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_half_hipped_roof_edges(length, width, height, base_z, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für ein Krüppelwalmdach."""
    half_l = length / 2
    half_w = width / 2
    first_offset = length * 0.15
    hip_height = height * 0.6
    
    points = np.array([
        [-half_l, -half_w, base_z],                    # 0
        [half_l, -half_w, base_z],                     # 1
        [half_l, half_w, base_z],                      # 2
        [-half_l, half_w, base_z],                     # 3
        [-half_l + first_offset, 0, base_z + height],  # 4
        [half_l - first_offset, 0, base_z + height],   # 5
        [-half_l, 0, base_z + hip_height],             # 6
        [half_l, 0, base_z + hip_height],              # 7
    ])
    
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Basis
        (4, 5),                           # First
        (0, 6), (3, 6), (6, 4),          # Linker Walm
        (1, 7), (2, 7), (7, 5),          # Rechter Walm
        (0, 4), (3, 4), (1, 5), (2, 5)   # Hauptdachkanten
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([points[start][0], points[end][0], None])
        y_lines.extend([points[start][1], points[end][1], None])
        z_lines.extend([points[start][2], points[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_pent_roof_edges(length, width, height, base_z, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für ein Pultdach."""
    half_l = length / 2
    half_w = width / 2
    
    points = np.array([
        [-half_l, -half_w, base_z],              # 0
        [half_l, -half_w, base_z],               # 1
        [half_l, half_w, base_z],                # 2
        [-half_l, half_w, base_z],               # 3
        [-half_l, -half_w, base_z + height],     # 4
        [half_l, -half_w, base_z + height],      # 5
    ])
    
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Basis
        (4, 5),                           # Obere vordere Kante
        (0, 4), (1, 5),                  # Vertikale vordere Kanten
        (4, 3), (5, 2)                   # Schräge Dachkanten
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([points[start][0], points[end][0], None])
        y_lines.extend([points[start][1], points[end][1], None])
        z_lines.extend([points[start][2], points[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_pyramid_roof_edges(length, width, height, base_z, color='black', line_width=2):
    """Erstellt schwarze Kanten-Linien für ein Zeltdach."""
    half_l = length / 2
    half_w = width / 2
    
    points = np.array([
        [-half_l, -half_w, base_z],        # 0
        [half_l, -half_w, base_z],         # 1
        [half_l, half_w, base_z],          # 2
        [-half_l, half_w, base_z],         # 3
        [0, 0, base_z + height],           # 4: Spitze
    ])
    
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Basis
        (0, 4), (1, 4), (2, 4), (3, 4)   # Kanten zur Spitze
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([points[start][0], points[end][0], None])
        y_lines.extend([points[start][1], points[end][1], None])
        z_lines.extend([points[start][2], points[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def create_pv_module_edges(vertices, color='black', line_width=1):
    """Erstellt schwarze Kanten-Linien für ein PV-Modul (Quader mit 8 Vertices)."""
    # 12 Kanten eines Quaders
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Untere Fläche
        (4, 5), (5, 6), (6, 7), (7, 4),  # Obere Fläche
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertikale Kanten
    ]
    
    x_lines, y_lines, z_lines = [], [], []
    for start, end in edges:
        x_lines.extend([vertices[start][0], vertices[end][0], None])
        y_lines.extend([vertices[start][1], vertices[end][1], None])
        z_lines.extend([vertices[start][2], vertices[end][2], None])
    
    return go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        showlegend=False,
        hoverinfo='skip'
    )


def calculate_grid_positions(length, width, count, spacing_x=0.25, spacing_y=0.25):
    """
    Berechnet Grid-Positionen für PV-Module mit Spacing.
    
    FIX: Verbesserte Berechnung mit korrektem Spacing und Zentrierung.
    """
    positions = []
    
    # FIX: Berechne wie viele Module in X und Y passen (mit Spacing)
    # Formel: (Länge - 2*Rand) / (Modul + Spacing)
    margin = 0.5  # 50cm Randabstand
    available_length = length - 2 * margin
    available_width = width - 2 * margin
    
    modules_x = max(1, int(available_length / (PV_W + spacing_x)))
    modules_y = max(1, int(available_width / (PV_H + spacing_y)))
    
    # FIX: Berechne tatsächliche Größe des Grids
    total_width_x = modules_x * PV_W + (modules_x - 1) * spacing_x
    total_width_y = modules_y * PV_H + (modules_y - 1) * spacing_y
    
    # FIX: Zentriere das Grid korrekt
    start_x = -total_width_x / 2
    start_y = -total_width_y / 2
    
    # Erstelle Grid
    for row in range(modules_y):
        for col in range(modules_x):
            if len(positions) >= count:
                break
            
            # FIX: Korrekte Positionsberechnung
            x = start_x + col * (PV_W + spacing_x) + PV_W / 2
            y = start_y + row * (PV_H + spacing_y) + PV_H / 2
            positions.append((x, y))
        
        if len(positions) >= count:
            break
    
    # FIX: Wenn nicht genug Platz, fülle mit Warnmeldung
    if len(positions) < count:
        print(f"⚠️ WARNUNG: Nur {len(positions)} von {count} Modulen passen auf das Dach!")
        print(f"   Dachgröße: {length}m x {width}m")
        print(f"   Modulraster: {modules_x} x {modules_y} = {modules_x * modules_y} Module")
    
    return positions


# ============================================================================
# HAUPTFUNKTION: VOLLSTÄNDIGE 3D-SZENE
# ============================================================================

def build_plotly_scene(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: Any = None,
    selected_modules: List[int] = None
) -> go.Figure:
    """
    Erstellt eine vollständige, hochwertige 3D-Szene mit Plotly.
    
    Args:
        project_data: Projekt-Daten Dictionary
        dims: Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Anzahl der Module
        layout_config: Layout-Konfiguration
        selected_modules: Liste ausgewählter Module
        
    Returns:
        Plotly Figure mit vollständiger 3D-Szene
    """
    if selected_modules is None:
        selected_modules = []
    
    fig = go.Figure()
    
    # ========== 1. GEBÄUDE (vollständig) ==========
    building = create_complete_box(
        x_min=-dims.length_m/2,
        x_max=dims.length_m/2,
        y_min=-dims.width_m/2,
        y_max=dims.width_m/2,
        z_min=0,
        z_max=dims.wall_height_m,
        color="#7a7a7a",  # Helleres Grau für bessere Sichtbarkeit
        name="Gebäude"
    )
    fig.add_trace(building)
    
    # GEBÄUDE-KANTEN hinzufügen
    building_edges = create_box_edges(
        x_min=-dims.length_m/2,
        x_max=dims.length_m/2,
        y_min=-dims.width_m/2,
        y_max=dims.width_m/2,
        z_min=0,
        z_max=dims.wall_height_m,
        color='black',
        line_width=2
    )
    fig.add_trace(building_edges)
    
    # ========== 2. DACH (vollständig) ==========
    # Hole Dachfarbe aus project_data
    roof_covering = project_data.get("roof_covering", "Ziegel")
    roof_color = ROOF_COLORS.get(roof_covering, ROOF_COLORS.get("default", "#8B4513"))
    
    roof_z = dims.wall_height_m
    default_tilt = 15.0
    roof_inclination = project_data.get("roof_inclination_deg", 35.0)
    
    # Erstelle das entsprechende Dach basierend auf dem Dachtyp
    if roof_type == "Flachdach":
        # Flachdach als dünne Box
        roof = create_complete_box(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.2,
            color=roof_color,
            name="Dach (Flachdach)"
        )
        fig.add_trace(roof)
        # Flachdach-Kanten
        roof_edges = create_box_edges(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.2,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.25
        default_tilt = 15.0
        
    elif roof_type == "Satteldach":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        roof = create_gabled_roof_complete(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach (Satteldach)"
        )
        fig.add_trace(roof)
        # Satteldach-Kanten
        roof_edges = create_gabled_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    elif roof_type == "Satteldach mit Gaube":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        # Erstelle Satteldach mit Gaube (gibt Liste von Meshes zurück)
        roof_meshes = create_gabled_roof_with_dormer(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            dormer_width=2.0,
            dormer_height=1.5,
            dormer_depth=1.5,
            dormer_position=0.0,
            color=roof_color,
            name="Dach (Satteldach mit Gaube)"
        )
        # Füge alle Meshes hinzu
        for mesh in roof_meshes:
            fig.add_trace(mesh)
        # Satteldach-Kanten (Basis)
        roof_edges = create_gabled_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    elif roof_type == "Walmdach":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        roof = create_hipped_roof(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach (Walmdach)"
        )
        fig.add_trace(roof)
        # Walmdach-Kanten
        roof_edges = create_hipped_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    elif roof_type == "Krüppelwalmdach":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        roof = create_half_hipped_roof(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach (Krüppelwalmdach)"
        )
        fig.add_trace(roof)
        # Krüppelwalmdach-Kanten
        roof_edges = create_half_hipped_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    elif roof_type == "Pultdach":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        roof = create_pent_roof(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach (Pultdach)"
        )
        fig.add_trace(roof)
        # Pultdach-Kanten
        roof_edges = create_pent_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    elif roof_type == "Zeltdach":
        roof_height = (dims.width_m / 2) * np.tan(np.deg2rad(roof_inclination))
        roof = create_pyramid_roof(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color=roof_color,
            name="Dach (Zeltdach)"
        )
        fig.add_trace(roof)
        # Zeltdach-Kanten
        roof_edges = create_pyramid_roof_edges(
            length=dims.length_m,
            width=dims.width_m,
            height=roof_height,
            base_z=roof_z,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.15
        default_tilt = roof_inclination
        
    else:
        # Fallback: Sonstiges als Flachdach
        roof = create_complete_box(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.2,
            color=roof_color,
            name="Dach (Sonstiges)"
        )
        fig.add_trace(roof)
        # Fallback-Dach-Kanten
        roof_edges = create_box_edges(
            x_min=-dims.length_m/2,
            x_max=dims.length_m/2,
            y_min=-dims.width_m/2,
            y_max=dims.width_m/2,
            z_min=roof_z,
            z_max=roof_z + 0.2,
            color='black',
            line_width=2
        )
        fig.add_trace(roof_edges)
        module_base_z = roof_z + 0.25
        default_tilt = 15.0
    
    # ========== 3. PV-MODULE ==========
    # NEUE LOGIK: Prüfe ob ModulePlacementManager Module hat
    try:
        import streamlit as st
        if hasattr(st, 'session_state') and 'pv_placement_manager' in st.session_state:
            manager = st.session_state.pv_placement_manager
            
            # Rendere Module aus ModulePlacementManager
            if len(manager.modules) > 0:
                from utils.pv_module_rendering_3d import render_all_modules
                
                module_traces = render_all_modules(
                    manager=manager,
                    show_edges=True,
                    show_selection=True
                )
                
                for trace in module_traces:
                    fig.add_trace(trace)
                
                print(f"✓ {len(manager.modules)} Module aus PlacementManager gerendert!")
            else:
                # Fallback: Alte Grid-basierte Module wenn keine im Manager
                positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
                
                for i, (x, y) in enumerate(positions):
                    if i >= module_quantity:
                        break
                    
                    # Standard-Werte
                    azimuth = 0.0  # Süd
                    tilt = default_tilt
                    z = module_base_z
                    
                    # Transformationen anwenden wenn AdvancedLayoutConfig
                    if isinstance(layout_config, AdvancedLayoutConfig):
                        if i in layout_config.module_transforms:
                            transform = layout_config.module_transforms[i]
                            azimuth = transform.azimuth_deg
                            tilt = transform.tilt_deg
                            x += transform.offset_x
                            y += transform.offset_y
                            z += transform.offset_z
                    
                    # Modul erstellen
                    is_selected = i in selected_modules
                    module, module_vertices = create_pv_module_3d(
                        x, y, z,
                        azimuth_deg=azimuth,
                        tilt_deg=tilt,
                        color="#1a1a2e",
                        selected=is_selected
                    )
                    fig.add_trace(module)
                    
                    # Modul-Kanten hinzufügen
                    module_edges = create_pv_module_edges(
                        vertices=module_vertices,
                        color='black',
                        line_width=1
                    )
                    fig.add_trace(module_edges)
        else:
            # Kein Streamlit Session State - Fallback zu Grid
            positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
            
            for i, (x, y) in enumerate(positions):
                if i >= module_quantity:
                    break
                
                # Standard-Werte
                azimuth = 0.0  # Süd
                tilt = default_tilt
                z = module_base_z
                
                # Transformationen anwenden wenn AdvancedLayoutConfig
                if isinstance(layout_config, AdvancedLayoutConfig):
                    if i in layout_config.module_transforms:
                        transform = layout_config.module_transforms[i]
                        azimuth = transform.azimuth_deg
                        tilt = transform.tilt_deg
                        x += transform.offset_x
                        y += transform.offset_y
                        z += transform.offset_z
                
                # Modul erstellen
                is_selected = i in selected_modules
                module, module_vertices = create_pv_module_3d(
                    x, y, z,
                    azimuth_deg=azimuth,
                    tilt_deg=tilt,
                    color="#1a1a2e",
                    selected=is_selected
                )
                fig.add_trace(module)
                
                # Modul-Kanten hinzufügen
                module_edges = create_pv_module_edges(
                    vertices=module_vertices,
                    color='black',
                    line_width=1
                )
                fig.add_trace(module_edges)
    except Exception as e:
        # Fallback bei Fehler - zeige keine Module
        print(f"Fehler beim Rendern von Modulen: {e}")
    
    # ========== 4. SONNE (optional) ==========
    if isinstance(layout_config, AdvancedLayoutConfig) and layout_config.enable_shading_analysis:
        sun_azimuth = project_data.get("sun_azimuth", 180.0)
        sun_elevation = project_data.get("sun_elevation", 45.0)
        sun = create_sun_marker(sun_azimuth, sun_elevation)
        fig.add_trace(sun)
    
    # ========== 5. LAYOUT & KAMERA ==========
    max_dim = max(dims.length_m, dims.width_m, dims.wall_height_m)
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='Länge (m)',
                showgrid=True,
                gridcolor='#1a2332',
                gridwidth=1,
                showbackground=True,
                backgroundcolor='#0B0F14'
            ),
            yaxis=dict(
                title='Breite (m)',
                showgrid=True,
                gridcolor='#1a2332',
                gridwidth=1,
                showbackground=True,
                backgroundcolor='#0B0F14'
            ),
            zaxis=dict(
                title='Höhe (m)',
                showgrid=True,
                gridcolor='#1a2332',
                gridwidth=1,
                showbackground=True,
                backgroundcolor='#0B0F14'
            ),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=-1.8, z=1.5),
                center=dict(x=0, y=0, z=0.2),
                up=dict(x=0, y=0, z=1)
            ),
            bgcolor='#0B0F14'
        ),
        title=dict(
            text=f'🏠 3D PV-Visualisierung ({module_quantity} Module)',
            font=dict(size=20, color='#FFFFFF', family='Arial, sans-serif')
        ),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(17, 23, 32, 0.95)',
            bordercolor='#00E5FF',
            borderwidth=1,
            font=dict(size=12, color='#FFFFFF')
        ),
        height=800,
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor='#0B0F14',
        plot_bgcolor='#0B0F14',
        hovermode='closest'
    )
    
    return fig
