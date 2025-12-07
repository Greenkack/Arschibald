"""
3D PV-Visualisierung mit Plotly

Hochwertige 3D-Visualisierung für Photovoltaik-Anlagen auf Gebäuden.
Verwendet Plotly für interaktive, browserbasierte 3D-Grafiken.
"""

import math
import plotly.graph_objects as go
import numpy as np
import traceback
from typing import Dict, List, Tuple, Any, Optional

# Export list
__all__ = [
    'R',
    'build_plotly_scene',
    'calculate_grid_positions',
    'create_box_edges',
    'create_color_legend',
    'create_complete_box',
    'create_gabled_roof_complete',
    'create_gabled_roof_edges',
    'create_gabled_roof_with_dormer',
    'create_half_hipped_roof',
    'create_half_hipped_roof_edges',
    'create_hipped_roof',
    'create_hipped_roof_edges',
    'create_module_number_annotation',
    'create_pent_roof',
    'create_pent_roof_edges',
    'create_placement_grid',
    'create_pv_module_3d',
    'create_pv_module_edges',
    'create_pyramid_roof',
    'create_pyramid_roof_edges',
    'create_sun_marker',
]

# Import data classes from utils.pv3d
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
from utils.pv3d_performance import (
    cached,
    monitor_performance,
    calculate_module_positions_cached,
    should_render_module
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


def create_pv_module_3d(x, y, z, azimuth_deg=0, tilt_deg=15, color="#1a1a2e", selected=False, show_mounting=True, roof_type="Flachdach", invalid=False, module_number=None):
    """
    Erstellt ein detailliertes PV-Modul mit Dicke und korrekter Rotation.
    Gibt Tuple zurück: (mesh, vertices) für Kanten-Rendering.
    
    FIX 2024: Mounting Height wird jetzt basierend auf Dachform berechnet:
    - Geneigte Dächer (Satteldach, Walmdach, etc.): Sichtbare Aufständerung 0.1-0.3m
    - Flachdach mit Aufständerung: Höhere Aufständerung 0.3-0.8m
    - Module sinken NICHT mehr in die Dachfläche ein
    
    TASK 12: Visualisierungs-Verbesserungen:
    - Farb-Unterscheidung für normale Module (dunkelblau #1a1a2e)
    - Farb-Unterscheidung für ausgewählte Module (hellblau #4a90e2)
    - Farb-Unterscheidung für ungültige Positionen (rot #e74c3c)
    - Modul-Nummern Anzeige (optional)
    
    Args:
        x, y, z: Position des Moduls
        azimuth_deg: Azimuth-Winkel (0° = Süd)
        tilt_deg: Neigungs-Winkel (0° = horizontal)
        color: Farbe des Moduls (Standard: dunkelblau)
        selected: Ob Modul ausgewählt ist (hellblau Farbe)
        show_mounting: Ob Montage-Gestell visualisiert werden soll
        roof_type: Dachform ("Flachdach", "Satteldach", "Walmdach", etc.)
        invalid: Ob Modul an ungültiger Position ist (rot Farbe)
        module_number: Optionale Modul-Nummer für Anzeige
    
    Requirements:
        - 1.2: Module haben erkennbare Farbe
        - 8.5: Visualisierungs-Optionen (Nummern)
    """
    # Lokale Koordinaten (Modul zentriert im Ursprung)
    hw = PV_W / 2
    hh = PV_H / 2
    ht = PV_T / 2
    
    # CRITICAL FIX 2025-01-10:
    # Z-Position ist bereits korrekt berechnet (absolut)!
    # calculate_z_position() gibt relative Position zurück
    # build_plotly_scene addiert wall_height_m dazu
    # Wir dürfen NICHT nochmal mounting_height addieren!
    # 
    # Die Z-Position die hier ankommt ist bereits:
    # - Für Flachdach: wall_height_m + 0.30m (Aufständerung)
    # - Für geneigte Dächer: wall_height_m + 0.15m (auf Dachfläche)
    #
    # KEINE weitere Modifikation der Z-Position!
    
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
    
    # TASK 12: Farb-Unterscheidung für verschiedene Modul-Zustände
    # Requirement 1.2: Erkennbare Farben für verschiedene Zustände
    if invalid:
        # Ungültige Position: Rot
        module_color = "#e74c3c"
        module_name = "PV Module (Ungültig)"
    elif selected:
        # Ausgewähltes Modul: Hellblau
        module_color = "#4a90e2"
        module_name = "PV Module (Ausgewählt)"
    else:
        # Normales Modul: Dunkelblau (Standard)
        module_color = color
        module_name = "PV Module"
    
    # Füge Modul-Nummer zum Namen hinzu wenn vorhanden
    # Requirement 8.5: Modul-Nummern Anzeige (optional)
    if module_number is not None:
        module_name = f"{module_name} #{module_number}"
    
    mesh = go.Mesh3d(
        x=final_vertices[:, 0],
        y=final_vertices[:, 1],
        z=final_vertices[:, 2],
        i=i, j=j, k=k,
        color=module_color,
        opacity=0.9,
        name=module_name,
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
        name=' Sonne',
        showlegend=True,
        hovertemplate=f'Sonne<br>Azimuth: {azimuth_deg:.1f}°<br>Elevation: {elevation_deg:.1f}°<extra></extra>'
    )


# ============================================================================
# TASK 12: VISUALISIERUNGS-VERBESSERUNGEN
# ============================================================================

def create_module_number_annotation(x, y, z, module_number, offset_z=0.1):
    """
    Erstellt eine Text-Annotation für Modul-Nummern.
    
    TASK 12: Modul-Nummern Anzeige (optional)
    
    Args:
        x, y, z: Position des Moduls
        module_number: Nummer des Moduls
        offset_z: Vertikaler Offset über dem Modul (Standard: 0.1m)
    
    Returns:
        Plotly Scatter3d Objekt mit Text-Annotation
    
    Requirements:
        - 8.5: Modul-Nummern anzeigen (optional)
    """
    return go.Scatter3d(
        x=[x],
        y=[y],
        z=[z + offset_z],
        mode='text',
        text=[str(module_number)],
        textfont=dict(
            size=12,
            color='white',
            family='Arial Black'
        ),
        textposition='middle center',
        name=f'Modul #{module_number}',
        showlegend=False,
        hoverinfo='skip'
    )


def create_placement_grid(roof_length, roof_width, base_z, grid_spacing=1.0, color='rgba(128, 128, 128, 0.3)', line_width=1):
    """
    Erstellt ein Raster-Overlay zur Orientierung auf der Dachfläche.
    
    TASK 12: Raster-Overlay (optional)
    
    Args:
        roof_length: Länge des Dachs in Metern
        roof_width: Breite des Dachs in Metern
        base_z: Z-Position der Dachfläche
        grid_spacing: Abstand zwischen Rasterlinien in Metern
        color: Farbe der Rasterlinien (RGBA mit Transparenz)
        line_width: Breite der Rasterlinien
    
    Returns:
        Plotly Scatter3d Objekt mit Rasterlinien
    
    Requirements:
        - 8.5: Raster anzeigen (optional)
    """
    half_l = roof_length / 2
    half_w = roof_width / 2
    
    x_lines, y_lines, z_lines = [], [], []
    
    # Vertikale Linien (parallel zur Y-Achse)
    x_pos = -half_l
    while x_pos <= half_l:
        x_lines.extend([x_pos, x_pos, None])
        y_lines.extend([-half_w, half_w, None])
        z_lines.extend([base_z + 0.01, base_z + 0.01, None])
        x_pos += grid_spacing
    
    # Horizontale Linien (parallel zur X-Achse)
    y_pos = -half_w
    while y_pos <= half_w:
        x_lines.extend([-half_l, half_l, None])
        y_lines.extend([y_pos, y_pos, None])
        z_lines.extend([base_z + 0.01, base_z + 0.01, None])
        y_pos += grid_spacing
    
    return go.Scatter3d(
        x=x_lines,
        y=y_lines,
        z=z_lines,
        mode='lines',
        line=dict(color=color, width=line_width),
        name='Platzierungs-Raster',
        showlegend=False,
        hoverinfo='skip'
    )


def create_color_legend():
    """
    Erstellt eine Legende für die Modul-Farben.
    
    TASK 12: Farb-Unterscheidung Dokumentation
    
    Returns:
        Liste von Plotly Scatter3d Objekten für die Legende
    
    Requirements:
        - 1.2: Erkennbare Farben
    """
    # Erstelle unsichtbare Marker für die Legende
    legend_items = []
    
    # Normales Modul (Dunkelblau)
    legend_items.append(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='#1a1a2e'),
        name='Normal',
        showlegend=True,
        visible='legendonly'
    ))
    
    # Ausgewähltes Modul (Hellblau)
    legend_items.append(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='#4a90e2'),
        name='Ausgewählt',
        showlegend=True,
        visible='legendonly'
    ))
    
    # Ungültiges Modul (Rot)
    legend_items.append(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='#e74c3c'),
        name='Ungültig',
        showlegend=True,
        visible='legendonly'
    ))
    
    return legend_items


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
    Berechnet EXAKT 'count' Grid-Positionen für PV-Module (oder weniger wenn nicht genug Platz).
    
    FIX 2024: Komplett überarbeitete Berechnung für exakte Modulanzahl mit optimaler Zentrierung.
    
    Args:
        length: Dachlänge in Metern
        width: Dachbreite in Metern
        count: Gewünschte Anzahl Module
        spacing_x: Abstand zwischen Modulen in X-Richtung (m)
        spacing_y: Abstand zwischen Modulen in Y-Richtung (m)
    
    Returns:
        Liste von (x, y) Positionen für Module
    """
    import math
    
    positions = []
    margin = 0.5  # 50cm Randabstand
    
    # Verfügbare Fläche berechnen
    available_length = length - 2 * margin
    available_width = width - 2 * margin
    
    # Maximale Anzahl Module die passen (in jede Richtung)
    max_modules_x = max(1, int((available_length + spacing_x) / (PV_W + spacing_x)))
    max_modules_y = max(1, int((available_width + spacing_y) / (PV_H + spacing_y)))
    max_total = max_modules_x * max_modules_y
    
    # Logging: Zeige Berechnungsdetails
    print(f"\nGrid-Positionierung:")
    print(f"   Dachgröße: {length:.1f}m x {width:.1f}m")
    print(f"   Verfügbare Fläche: {available_length:.1f}m x {available_width:.1f}m")
    print(f"   Max. Module: {max_modules_x} x {max_modules_y} = {max_total}")
    print(f"   Gewünschte Module: {count}")
    
    # Warnung wenn nicht genug Platz
    if count > max_total:
        print(f"   WARNUNG: Nur {max_total} von {count} Modulen passen!")
        count = max_total
    
    # Berechne optimales Layout für 'count' Module
    # Ziel: Möglichst quadratisches Layout (ähnliche Anzahl Reihen/Spalten)
    best_layout = None
    min_waste = float('inf')
    
    # Probiere verschiedene Spalten-Anzahlen
    for cols in range(1, max_modules_x + 1):
        rows = math.ceil(count / cols)
        
        # Prüfe ob Layout passt
        if rows <= max_modules_y:
            # Berechne "Verschwendung" (leere Plätze im Grid)
            waste = (cols * rows) - count
            
            # Bevorzuge Layout mit weniger Verschwendung
            if waste < min_waste:
                min_waste = waste
                best_layout = (cols, rows)
    
    # Fallback wenn kein Layout gefunden
    if not best_layout:
        best_layout = (max_modules_x, math.ceil(count / max_modules_x))
    
    modules_x, modules_y = best_layout
    
    print(f"   Gewähltes Layout: {modules_x} x {modules_y}")
    
    # Berechne tatsächliche Grid-Größe
    total_width_x = modules_x * PV_W + (modules_x - 1) * spacing_x
    total_width_y = modules_y * PV_H + (modules_y - 1) * spacing_y
    
    # Zentriere Grid auf Dachfläche
    start_x = -total_width_x / 2
    start_y = -total_width_y / 2
    
    # Erstelle EXAKT 'count' Positionen
    for row in range(modules_y):
        for col in range(modules_x):
            if len(positions) >= count:
                break
            
            # Berechne Position
            x = start_x + col * (PV_W + spacing_x) + PV_W / 2
            y = start_y + row * (PV_H + spacing_y) + PV_H / 2
            positions.append((x, y))
        
        if len(positions) >= count:
            break
    
    print(f"   Platzierte Module: {len(positions)}")
    
    if len(positions) < count:
        print(f"   {count - len(positions)} Module konnten nicht platziert werden!")
    
    return positions


# ============================================================================
# HAUPTFUNKTION: VOLLSTÄNDIGE 3D-SZENE
# ============================================================================

@monitor_performance("build_3d_scene")
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
        default_tilt = 0.0  # FIX: Module liegen flach auf Dachfläche, keine Aufständerung
        
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
    # TASK 4: 3D-Rendering Integration
    # TASK 13: Performance-optimized batch rendering
    # Load module positions from session state and render them
    try:
        import streamlit as st
        
        # Requirement 10.1: Load positions from session state
        # Requirement 11.3: Try-Catch around rendering
        placed_positions = st.session_state.get("placed_module_positions", [])
        
        # Requirement 11.1: Validate positions data
        if not isinstance(placed_positions, list):
            print(
                f"Invalid placed_positions type: "
                f"{type(placed_positions).__name__}, expected list"
            )
            placed_positions = []
        
        if placed_positions:
            # TASK 13: Limit rendering for performance
            # Requirement 10.5: Begrenzung auf maximal 200 Module
            if len(placed_positions) > 200:
                print(f"Limiting rendering to 200 modules (total: {len(placed_positions)})")
                placed_positions = placed_positions[:200]
            
            # Requirement 10.2: Loop over all placed positions
            print(
                f"Rendering {len(placed_positions)} PV modules "
                "from session state..."
            )
            
            # TASK 13: Collect all meshes first, then add in batch
            # Requirement 10.5: Batch-Hinzufügen von Meshes zur Figure
            module_meshes = []
            edge_meshes = []
            
            successful_renders = 0
            failed_renders = 0
            
            for i, position in enumerate(placed_positions):
                try:
                    # Requirement 11.1: Validate position format
                    if not isinstance(position, (tuple, list)):
                        print(
                            f"Invalid position type at index {i}: "
                            f"{type(position).__name__}"
                        )
                        failed_renders += 1
                        continue
                    
                    # Requirement 10.3: Extract position coordinates
                    if len(position) == 3:
                        x, y, z_relative = position
                        
                        # Requirement 11.1: Validate coordinate values
                        if not all(isinstance(coord, (int, float))
                                   for coord in [x, y, z_relative]):
                            print(
                                f"Invalid coordinate types at index {i}: "
                                f"{position}"
                            )
                            failed_renders += 1
                            continue
                        
                        # Check for NaN or Inf values
                        import math
                        if any(math.isnan(coord) or math.isinf(coord)
                               for coord in [x, y, z_relative]):
                            print(
                                f"Invalid coordinate values (NaN/Inf) "
                                f"at index {i}: {position}"
                            )
                            failed_renders += 1
                            continue
                        
                        # FIX: Add building height to z-position
                        # z_relative is relative to roof surface,
                        # we need absolute position
                        z = dims.wall_height_m + z_relative
                    else:
                        print(
                            f"Invalid position format at index {i}: "
                            f"{position} (expected 3 coordinates)"
                        )
                        failed_renders += 1
                        continue
                    
                    # TASK 8: Calculate rotation based on roof type and pitch
                    # Requirement 6.1: Flat roof with 30° tilt
                    # Requirement 6.5: Pitched roofs use roof pitch angle
                    try:
                        if roof_type == "Flachdach":
                            tilt_deg = 30.0  # Aufständerung with 30° tilt
                        else:
                            # Requirement 6.2, 6.3, 6.5: Pitched roofs
                            # use roof inclination
                            tilt_deg = roof_inclination  # Use actual roof pitch
                        
                        azimuth_deg = 0.0  # South-facing (default)
                    except Exception as angle_error:
                        # Requirement 11.4: Meaningful error messages
                        print(
                            f"Error calculating angles for module {i}: "
                            f"{angle_error}, using defaults"
                        )
                        tilt_deg = 30.0
                        azimuth_deg = 0.0
                    
                    # Check if module is selected
                    is_selected = i in selected_modules
                    
                    # TASK 12: Get visualization options from session state
                    # Requirement 8.5: Module numbers and grid display
                    show_module_numbers = st.session_state.get(
                        "show_module_numbers", False
                    )
                    
                    # TASK 12: Determine if module is at invalid position
                    # (for future collision detection visualization)
                    is_invalid = False  # Placeholder for collision detection
                    
                    # Requirement 10.3, 11.3: Call create_pv_module_3d()
                    # with error handling
                    # TASK 12: Pass module_number and invalid flag
                    try:
                        module_mesh, module_vertices = create_pv_module_3d(
                            x=x,
                            y=y,
                            z=z,
                            azimuth_deg=azimuth_deg,
                            tilt_deg=tilt_deg,
                            color="#1a1a2e",  # Dark blue/black (normal)
                            selected=is_selected,  # Hellblau if selected
                            show_mounting=True,
                            roof_type=roof_type,
                            invalid=is_invalid,  # TASK 12: Red if invalid
                            module_number=(i + 1) if show_module_numbers else None
                        )
                    except Exception as mesh_error:
                        # Requirement 11.2, 11.4: Error handling
                        print(
                            f"Error creating mesh for module {i}: "
                            f"{mesh_error}"
                        )
                        failed_renders += 1
                        continue
                    
                    # TASK 13: Collect meshes for batch addition
                    # Requirement 10.5: Batch-Hinzufügen von Meshes zur Figure
                    try:
                        module_meshes.append(module_mesh)
                        
                        # Add module edges for better visibility
                        module_edges = create_pv_module_edges(
                            vertices=module_vertices,
                            color='black',
                            line_width=1
                        )
                        edge_meshes.append(module_edges)
                        
                        successful_renders += 1
                        
                    except Exception as add_error:
                        # Requirement 11.2, 11.4: Error handling
                        print(
                            f"Error adding module {i} to figure: "
                            f"{add_error}"
                        )
                        failed_renders += 1
                        continue
                    
                except Exception as module_error:
                    # Requirement 10.5, 11.2: Error handling for
                    # individual modules
                    print(
                        f"Unexpected error rendering module {i}: "
                        f"{module_error}"
                    )
                    failed_renders += 1
                    import traceback
                    traceback.print_exc()
                    continue
            
            # TASK 13: Add all meshes to figure in batch
            # Requirement 10.5: Batch-Hinzufügen von Meshes zur Figure
            # This is much faster than adding one at a time
            print(f"Adding {len(module_meshes)} module meshes to figure (batch)...")
            for mesh in module_meshes:
                fig.add_trace(mesh)
            
            print(f"Adding {len(edge_meshes)} edge meshes to figure (batch)...")
            for edges in edge_meshes:
                fig.add_trace(edges)
            
            # Requirement 11.4: Meaningful status messages
            if successful_renders > 0:
                print(
                    f"Successfully rendered {successful_renders} of "
                    f"{len(placed_positions)} modules"
                )
            if failed_renders > 0:
                print(
                    f"Failed to render {failed_renders} modules "
                    "(see warnings above)"
                )
            
        else:
            # No modules in session state - use fallback grid-based placement
            print("No modules in session state, using fallback grid placement...")
            
            # Fallback: Calculate grid positions
            positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
            
            for i, (x, y) in enumerate(positions[:module_quantity]):
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
                    selected=is_selected,
                    roof_type=roof_type
                )
                fig.add_trace(module)
                
                # Modul-Kanten hinzufügen
                module_edges = create_pv_module_edges(
                    vertices=module_vertices,
                    color='black',
                    line_width=1
                )
                fig.add_trace(module_edges)
            
            print(f"Fallback: {len(positions[:module_quantity])} modules rendered")
    
    except Exception as e:
        # Requirement 10.5, 11.2, 11.4: Error handling for rendering
        # with meaningful messages
        print(f"Kritischer Fehler beim Rendern der PV-Module: {e}")
        print(f"   Fehlertyp: {type(e).__name__}")
        print(f"   Fehlerdetails: {str(e)}")
        traceback.print_exc()
        
        # Last resort fallback: Simple grid-based modules
        try:
            print("Attempting last resort fallback rendering...")
            positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
            
            for i, (x, y) in enumerate(positions[:module_quantity]):
                if i >= module_quantity:
                    break
                
                # Standard values
                azimuth = 0.0  # South
                tilt = default_tilt
                z = module_base_z
                
                # Apply transformations if AdvancedLayoutConfig
                if isinstance(layout_config, AdvancedLayoutConfig):
                    if i in layout_config.module_transforms:
                        transform = layout_config.module_transforms[i]
                        azimuth = transform.azimuth_deg
                        tilt = transform.tilt_deg
                        x += transform.offset_x
                        y += transform.offset_y
                        z += transform.offset_z
                
                # Create module
                is_selected = i in selected_modules
                module, module_vertices = create_pv_module_3d(
                    x, y, z,
                    azimuth_deg=azimuth,
                    tilt_deg=tilt,
                    color="#1a1a2e",
                    selected=is_selected,
                    roof_type=roof_type
                )
                fig.add_trace(module)
                
                # Add module edges
                module_edges = create_pv_module_edges(
                    vertices=module_vertices,
                    color='black',
                    line_width=1
                )
                fig.add_trace(module_edges)
            
            print(f"Last resort fallback: {len(positions[:module_quantity])} modules rendered")
        
        except Exception as fallback_error:
            # Requirement 11.3: Fallback to previous state on error
            print(f"Complete failure rendering modules: {fallback_error}")
            print("No modules will be displayed")
    
    # ========== 4. TASK 12: VISUALISIERUNGS-VERBESSERUNGEN ==========
    try:
        # TASK 12: Module Number Annotations (optional)
        # Requirement 8.5: Show module numbers if enabled
        show_module_numbers = st.session_state.get("show_module_numbers", False)
        
        if show_module_numbers and placed_positions:
            print(f"Adding module number annotations for {len(placed_positions)} modules...")
            
            for i, position in enumerate(placed_positions):
                try:
                    if len(position) == 3:
                        x, y, z_relative = position
                        z = dims.wall_height_m + z_relative
                        
                        # Create number annotation above module
                        number_annotation = create_module_number_annotation(
                            x=x,
                            y=y,
                            z=z,
                            module_number=i + 1,
                            offset_z=0.3  # 30cm above module
                        )
                        fig.add_trace(number_annotation)
                except Exception as annotation_error:
                    print(f"Error adding annotation for module {i}: {annotation_error}")
                    continue
            
            print(f"Module number annotations added")
        
        # TASK 12: Placement Grid Overlay (optional)
        # Requirement 8.5: Show grid if enabled
        show_placement_grid = st.session_state.get("show_placement_grid", False)
        
        if show_placement_grid:
            print("Adding placement grid overlay...")
            
            try:
                # Create grid at roof level
                grid_overlay = create_placement_grid(
                    roof_length=dims.length_m,
                    roof_width=dims.width_m,
                    base_z=module_base_z - 0.05,  # Slightly below modules
                    grid_spacing=1.0,  # 1m grid
                    color='rgba(128, 128, 128, 0.3)',  # Semi-transparent gray
                    line_width=1
                )
                fig.add_trace(grid_overlay)
                
                print("Placement grid overlay added")
            except Exception as grid_error:
                print(f"Error adding placement grid: {grid_error}")
        
        # TASK 12: Color Legend (always add for reference)
        # Requirement 1.2: Document color meanings
        try:
            legend_items = create_color_legend()
            for legend_item in legend_items:
                fig.add_trace(legend_item)
            print("Color legend added")
        except Exception as legend_error:
            print(f"Error adding color legend: {legend_error}")
    
    except Exception as viz_error:
        print(f"Error adding visualization improvements: {viz_error}")
        # Continue without visualization improvements
    
    # ========== 5. SONNE (optional) ==========
    if isinstance(layout_config, AdvancedLayoutConfig) and layout_config.enable_shading_analysis:
        sun_azimuth = project_data.get("sun_azimuth", 180.0)
        sun_elevation = project_data.get("sun_elevation", 45.0)
        sun = create_sun_marker(sun_azimuth, sun_elevation)
        fig.add_trace(sun)
    
    # ========== 6. LAYOUT & KAMERA ==========
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
            text=f' 3D PV-Visualisierung ({module_quantity} Module)',
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
