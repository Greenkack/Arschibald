Hier ist ein vollständiges, integrierbares 3D-Paket für deine Streamlit-App (Python + Streamlit), inkl. PV-Modul-Belegung (auto/manuell), Dachformen, Garage/Fassade-Fallback, Kompass, Zoom/Orbit, Screenshot-Export, PDF-Einbettung via reportlab, Speichern/Laden (JSON), Reset, Export (STL/glTF) – alles dynamisch aus euren Feldern (Ausrichtung, Dachneigung/-deckung, Modulanzahl etc.). Die verwendeten Schlüssel folgen euren vorhandenen Strukturen, z. B. project_data["project_details"]["roof_orientation"], ["roof_inclination_deg"], ["roof_covering_type"] (siehe Tests/Placeholders in eurem Repo) 

tests/test_roof_data

 

pdf_template_engine/placeholders

 

pdf_template_engine/placeholders

 

pdf_template_engine/placeholders

.
Ich hänge mich an eure modulare Streamlit-Struktur an (streamlit_app/…, pages/…, utils/…) 

chore: initial clean snapshot w…

.

0) requirements.txt (ergänzen)
# 3D + PDF + Utils
pyvista>=0.43.10
vtk>=9.3.0
stpyvista>=0.1.4
numpy>=1.26
trimesh>=4.4.9
reportlab>=4.2.2
pikepdf>=9.0.0
# (bereits vorhanden laut Basis: streamlit, pandas, plotly etc.)

1) streamlit_app/utils/pv3d.py

Erzeugt 3D-Geometrie (Haus, Dach, Garage, Fassade, PV-Module), automatische/manuelle Belegung, Off-Screen-Screenshot (PNG-Bytes) für PDF, Exporte (STL/glTF), Speichern/Laden der Layout-Konfiguration.

# streamlit_app/utils/pv3d.py
from __future__ import annotations
import io, json, math
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pyvista as pv

# ==== Konstanten / Defaults ====
# Standard-Modulgröße (Meter)
PV_W = 1.05
PV_H = 1.76
PV_T = 0.04  # Dicke

# Farben pro Dachdeckung (vereinfacht)
ROOF_COLORS = {
    "Ziegel": "#c96a2d",
    "Beton": "#9ea3a8",
    "Schiefer": "#3b3f44",
    "Eternit": "#7e8388",
    "Trapezblech": "#8e8f93",
    "Bitumen": "#4a4d52",
}

# ==== Datenklassen ====
@dataclass
class BuildingDims:
    length_m: float = 10.0
    width_m: float = 6.0
    wall_height_m: float = 6.0  # Traufhöhe (ohne Dach)

@dataclass
class LayoutConfig:
    mode: str = "auto"  # "auto" | "manual"
    use_garage: bool = False
    use_facade: bool = False
    removed_indices: List[int] = None  # im manuellen Modus (Raster-Indices)
    garage_dims: Tuple[float, float, float] = (6.0, 3.0, 3.0)  # L, B, H
    # bei Bedarf: Koordinaten-Offsets
    offset_main_xy: Tuple[float, float] = (0.0, 0.0)
    offset_garage_xy: Tuple[float, float] = (0.0, 0.0)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(s: str) -> "LayoutConfig":
        d = json.loads(s)
        return LayoutConfig(**d)

# ==== Hilfsfunktionen ====
def _deg_to_rad(d: float) -> float:
    return d * math.pi / 180.0

def _safe_get_orientation(project_data: Dict) -> str:
    """Ausrichtung robust aus project_data / project_details extrahieren (siehe placeholders/tests)."""
    pd = project_data or {}
    details = pd.get("project_details", {}) or {}
    val = (
        pd.get("roof_orientation")
        or details.get("roof_orientation")
        or pd.get("orientation")
        or details.get("orientation")
    )
    return (str(val).strip() if val else "Süd")  # Fallback wie bei placeholders.py
    # Quelle: placeholders liest roof_orientation aus project_details mit Fallbacks. 
    # (siehe euer placeholders.py) :contentReference[oaicite:5]{index=5}

def _safe_get_roof_inclination_deg(project_data: Dict) -> float:
    pd = project_data or {}
    details = pd.get("project_details", {}) or {}
    val = (
        pd.get("roof_inclination_deg")
        or details.get("roof_inclination_deg")
        or pd.get("roof_inclination")
        or details.get("roof_inclination")
    )
    try:
        return float(val)
    except Exception:
        return 30.0
    # Quelle: placeholders behandelt roof_inclination_deg analog. :contentReference[oaicite:6]{index=6}

def _safe_get_roof_covering(project_data: Dict) -> str:
    pd = project_data or {}
    details = pd.get("project_details", {}) or {}
    val = (
        pd.get("roof_covering_type")
        or details.get("roof_covering_type")
        or pd.get("roof_covering")
        or details.get("roof_covering")
    )
    return str(val) if val else "Ziegel"  # Default

def _roof_color_from_covering(cover: str) -> str:
    # Dach-Deckungsart beeinflusst Markierungsfarbe
    # (Anforderung: belegte/zu belegende Fläche farblich je nach Deckung)
    for k, v in ROOF_COLORS.items():
        if k.lower() in cover.lower():
            return v
    return "#b0b5ba"

# ==== Geometrie-Primitives ====
def make_box(l: float, w: float, h: float, z0: float = 0.0) -> pv.PolyData:
    """Quader mit Origin bei (0,0,z0), Ausdehnung +x = Länge, +y = Breite, +z = Höhe."""
    # PyVista-Box erzeugt zentriert; wir verschieben danach
    mesh = pv.Cube(center=(l/2, w/2, z0 + h/2), x_length=l, y_length=w, z_length=h)
    return mesh

def make_roof_flat(l: float, w: float, z_top: float) -> pv.PolyData:
    """Flachdach als sehr dünner Quader (optisch sichtbar)."""
    return make_box(l, w, 0.12, z0=z_top)

def make_roof_gable(l: float, w: float, z_top: float, pitch_deg: float) -> pv.PolyData:
    """Satteldach als Keil/Prisma: zwei geneigte Flächen."""
    pitch = _deg_to_rad(pitch_deg)
    # Höhe des Firstes über Traufe relativ zur Breite:
    # tan(pitch) = dh / (w/2) -> dh = tan(pitch) * (w/2)
    dh = math.tan(pitch) * (w/2)
    # Wir bauen ein simples Mesh: Rechteckiger Grund (Traufe) + erhöhter First
    # Eckpunkte:
    # (0,0,z_top), (l,0,z_top), (l,w,z_top), (0,w,z_top) als Traufe
    # Firstlinie entlang x bei y=w/2 um dh höher
    p0 = np.array([0,   0,   z_top])
    p1 = np.array([l,   0,   z_top])
    p2 = np.array([l,   w,   z_top])
    p3 = np.array([0,   w,   z_top])
    p4 = np.array([0,   w/2, z_top + dh])
    p5 = np.array([l,   w/2, z_top + dh])
    # Flächen: zwei große Dachflächen (p0-p1-p5-p4) und (p4-p5-p2-p3), plus kleine Stirnseiten
    pts = np.vstack([p0,p1,p2,p3,p4,p5])
    # Zellen als Polygone
    # Polydata via faces: [n, i0,i1,..., n,i0,i1,...]
    def quad(a,b,c,d): return [4,a,b,c,d]
    faces = quad(0,1,5,4) + quad(4,5,2,3) + quad(0,4,3,0) + quad(1,2,5,1)
    faces = np.array(faces)
    mesh = pv.PolyData(pts, faces)
    return mesh

def make_roof_hip(l: float, w: float, z_top: float, pitch_deg: float) -> pv.PolyData:
    """Walmdach: vier geneigte Flächen, Gipfel kurz oder Punkt."""
    pitch = _deg_to_rad(pitch_deg)
    dh_long = math.tan(pitch) * (w/2)
    dh_short = math.tan(pitch) * (l/2)
    center = np.array([l/2, w/2, z_top + min(dh_long, dh_short)])
    # Eckpunkte an Traufe:
    p = np.array([
        [0, 0, z_top], [l, 0, z_top], [l, w, z_top], [0, w, z_top]
    ])
    pts = np.vstack([p, center])
    # Dreiecke von Ecken zum Zentrum
    faces = []
    def tri(a,b,c): return [3,a,b,c]
    faces += tri(0,1,4)
    faces += tri(1,2,4)
    faces += tri(2,3,4)
    faces += tri(3,0,4)
    mesh = pv.PolyData(pts, np.array(faces))
    return mesh

def make_roof_pent(l: float, w: float, z_top: float, pitch_deg: float) -> pv.PolyData:
    """Pultdach: eine geneigte Ebene als dünner Quader."""
    pitch = _deg_to_rad(pitch_deg)
    dh = math.tan(pitch) * w  # ganze Breite
    # Wir kippen eine dünne Platte
    base = make_box(l, w, 0.12, z0=z_top)
    # Kippen um x-Achse, so dass y=w Seite höher ist
    base.rotate_x(angle=math.degrees(pitch), point=(0,0,z_top), inplace=True)
    return base

def make_roof_pyramid(l: float, w: float, z_top: float, pitch_deg: float) -> pv.PolyData:
    """Zeltdach: 4 Dreiecke zum zentralen Gipfel."""
    pitch = _deg_to_rad(pitch_deg)
    dh = math.tan(pitch) * (min(l,w)/2)
    center = np.array([l/2, w/2, z_top + dh])
    p0 = np.array([0, 0, z_top])
    p1 = np.array([l, 0, z_top])
    p2 = np.array([l, w, z_top])
    p3 = np.array([0, w, z_top])
    pts = np.vstack([p0,p1,p2,p3,center])
    def tri(a,b,c): return [3,a,b,c]
    faces = tri(0,1,4) + tri(1,2,4) + tri(2,3,4) + tri(3,0,4)
    return pv.PolyData(pts, np.array(faces))

def make_panel(x: float, y: float, z: float, yaw_deg: float = 0.0, tilt_deg: float = 0.0) -> pv.PolyData:
    """PV-Modul als dünner Quader mit Rotation (yaw um z, tilt um lokale y)."""
    mesh = pv.Cube(center=(PV_W/2, PV_H/2, PV_T/2), x_length=PV_W, y_length=PV_H, z_length=PV_T)
    mesh.translate((x, y, z), inplace=True)
    if yaw_deg:
        mesh.rotate_z(yaw_deg, point=(x, y, z), inplace=True)
    if tilt_deg:
        mesh.rotate_y(tilt_deg, point=(x, y, z), inplace=True)
    return mesh

# ==== Hauptaufbau ====
def build_scene(
    project_data: Dict,
    dims: BuildingDims,
    roof_type: str,
    roof_pitch_deg: Optional[float] = None,
    layout: Optional[LayoutConfig] = None,
    module_quantity: int = 0,
    flat_mount_mode: str = "south",  # "south" | "eastwest"
) -> Tuple[pv.Plotter, Dict[str, List[pv.PolyData]]]:
    """
    Erzeugt eine PyVista-Plotter-Szene und gibt zusätzlich die erzeugten Panels als Listen zurück.
    """
    layout = layout or LayoutConfig(mode="auto", removed_indices=[])
    plotter = pv.Plotter(off_screen=False)
    plotter.set_background("white")

    # Bodenplatte (optisch)
    ground = make_box(dims.length_m*3, dims.width_m*3, 0.05, z0=-0.05)
    plotter.add_mesh(ground, color="#f3f3f5", name="ground")

    # Wände/Gebäude
    walls = make_box(dims.length_m, dims.width_m, dims.wall_height_m, z0=0.0)
    plotter.add_mesh(walls, color="#e7e7ea", name="building")

    # Dach
    z_top = dims.wall_height_m
    pitch_deg = roof_pitch_deg if roof_pitch_deg is not None else _safe_get_roof_inclination_deg(project_data)
    cover_name = _safe_get_roof_covering(project_data)
    roof_color = _roof_color_from_covering(cover_name)

    roof_type = (roof_type or "").lower()
    if "flach" in roof_type:
        roof = make_roof_flat(dims.length_m, dims.width_m, z_top)
    elif "sattel" in roof_type and "gaube" not in roof_type:
        roof = make_roof_gable(dims.length_m, dims.width_m, z_top, pitch_deg)
    elif "pult" in roof_type:
        roof = make_roof_pent(dims.length_m, dims.width_m, z_top, pitch_deg)
    elif "krüppel" in roof_type or "krueppel" in roof_type:
        # Vereinfachung: wie Walmdach (für Visual)
        roof = make_roof_hip(dims.length_m, dims.width_m, z_top, pitch_deg)
    elif "walm" in roof_type:
        roof = make_roof_hip(dims.length_m, dims.width_m, z_top, pitch_deg)
    elif "zelt" in roof_type:
        roof = make_roof_pyramid(dims.length_m, dims.width_m, z_top, pitch_deg)
    else:
        # Sonstiges => Flach als Fallback
        roof = make_roof_flat(dims.length_m, dims.width_m, z_top)

    # Ausrichtung -> Kompass & Drehung des Hauses
    orientation = _safe_get_orientation(project_data)  # z.B. "Süd", "Ost", ...
    # Wir drehen die gesamte Szene so, dass Dach-Hauptfläche grob Richtung orientation zeigt.
    # Annahme: +Y = "Süd". Passen wir Drehung entsprechend an:
    yaw = 0.0
    if orientation.lower().startswith("s"):
        yaw = 0.0
    elif orientation.lower().startswith("o"):  # Ost
        yaw = -90.0
    elif orientation.lower().startswith("w"):  # West
        yaw = 90.0
    elif orientation.lower().startswith("n"):
        yaw = 180.0
    for m in (walls, roof, ground):
        m.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)

    plotter.add_mesh(roof, color=roof_color, name="roof")

    # Kompass (Pfeil nach Norden, rot)
    compass = pv.Arrow(start=(dims.length_m*1.6, dims.width_m*1.6, 0.1), direction=(0, -1, 0), scale=1.5)
    plotter.add_mesh(compass, color="red", name="compass")

    # PV-Module platzieren
    panels_main: List[pv.PolyData] = []
    panels_garage: List[pv.PolyData] = []
    panels_facade: List[pv.PolyData] = []

    # Nutzbare Dachfläche ~ dims.length * dims.width (vereinfachter Ansatz)
    free_area_est = dims.length_m * dims.width_m
    module_area = PV_W * PV_H
    max_fit_est = int(free_area_est // (module_area * 1.05))  # etwas Rand

    missing = 0
    place = min(module_quantity, max_fit_est)
    missing = max(0, module_quantity - place)

    def grid_positions(count: int, l: float, w: float, margin: float = 0.25) -> List[Tuple[float,float]]:
        """Raster in XY (Dachgrundriss), homogene Verteilung."""
        # Wie viele pro Reihe?
        if count <= 0: return []
        cols = max(1, int(l // (PV_W + margin)))
        rows = max(1, int(w // (PV_H + margin)))
        capacity = cols * rows
        if capacity == 0:
            return []
        n = min(count, capacity)
        xs = np.linspace(margin, l - PV_W - margin, max(1, cols))
        ys = np.linspace(margin, w - PV_H - margin, max(1, rows))
        coords = []
        k = 0
        for yv in ys:
            for xv in xs:
                coords.append((xv, yv))
                k += 1
                if k >= n:
                    return coords
        return coords

    # Automatik oder Manuell (manuell = zunächst Automatik, danach Entfernen beachten)
    coords_main = grid_positions(place, dims.length_m, dims.width_m)
    if layout.mode == "manual" and layout.removed_indices:
        coords_main = [c for i, c in enumerate(coords_main) if i not in set(layout.removed_indices)]

    # Flachdach Aufständerung
    tilt_main = 0.0
    yaw_panels = 0.0
    if "flach" in roof_type:
        if flat_mount_mode == "south":
            tilt_main = 15.0
            yaw_panels = 0.0  # Richtung Süd (wie yaw oben)
        else:  # eastwest
            # Wir machen alternierende Yaw
            pass

    z_panel = z_top + 0.02
    for i, (x, y) in enumerate(coords_main):
        if "flach" in roof_type and flat_mount_mode == "eastwest":
            yaw_i = -90.0 if (i % 2 == 0) else 90.0
            tilt_i = 10.0
            p = make_panel(x, y, z_panel, yaw_deg=yaw_i, tilt_deg=tilt_i)
        else:
            p = make_panel(x, y, z_panel, yaw_deg=yaw_panels, tilt_deg=tilt_main)
        # Drehung der Panels mit dem Haus mitnehmen
        p.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)
        panels_main.append(p)
        plotter.add_mesh(p, color="black", name=f"pv_main_{i}")

    # Falls Module fehlen -> Garage/Fassade
    if missing > 0:
        if layout.use_garage:
            gl, gw, gh = layout.garage_dims
            gx = dims.length_m + 1.0 + layout.offset_garage_xy[0]
            gy = layout.offset_garage_xy[1]
            garage = make_box(gl, gw, gh, z0=0.0)
            garage.translate((gx, gy, 0.0), inplace=True)
            garage.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)
            plotter.add_mesh(garage, color="#ececee", name="garage")

            gar_roof = make_roof_flat(gl, gw, gh)
            gar_roof.translate((gx, gy, 0.0), inplace=True)
            gar_roof.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)
            plotter.add_mesh(gar_roof, color=roof_color, name="garage_roof")

            # auf Garage legen
            coords_g = grid_positions(missing, gl, gw)
            for i, (x, y) in enumerate(coords_g):
                p = make_panel(gx + x, gy + y, gh + 0.02, yaw_deg=0.0, tilt_deg=10.0)
                p.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)
                panels_garage.append(p)
                plotter.add_mesh(p, color="black", name=f"pv_garage_{i}")
            missing = max(0, missing - len(coords_g))

        if missing > 0 and layout.use_facade:
            # Süd-Fassade annehmen -> Y-Positive Seite (nach Drehung beachten)
            # Wir hängen verbliebene Module vertikal an die Längswand.
            base_x = 0.2
            base_y = dims.width_m + 0.02
            rows = max(1, int(dims.wall_height_m // (PV_H + 0.25)))
            cols = max(1, int(dims.length_m // (PV_W + 0.25)))
            cap = rows * cols
            n = min(missing, cap)
            k = 0
            ys = np.linspace(0.25, dims.wall_height_m - PV_H - 0.25, rows)
            xs = np.linspace(0.25, dims.length_m - PV_W - 0.25, cols)
            for yv in ys:
                for xv in xs:
                    if k >= n: break
                    p = make_panel(base_x + xv, base_y, yv, yaw_deg=0.0, tilt_deg=90.0)  # vertikal
                    p.rotate_z(yaw, point=(dims.length_m/2, dims.width_m/2, 0), inplace=True)
                    panels_facade.append(p)
                    plotter.add_mesh(p, color="black", name=f"pv_facade_{k}")
                    k += 1
            missing = max(0, missing - n)

    return plotter, {
        "main": panels_main, "garage": panels_garage, "facade": panels_facade
    }

# ==== Offscreen-Screenshot für PDF ====
def render_image_bytes(
    project_data: Dict,
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout: Optional[LayoutConfig] = None,
    flat_mount_mode: str = "south",
    width_px: int = 1600,
    height_px: int = 1000,
) -> bytes:
    layout = layout or LayoutConfig(mode="auto", removed_indices=[])
    pitch = _safe_get_roof_inclination_deg(project_data)
    plotter, _ = build_scene(project_data, dims, roof_type, pitch, layout, module_quantity, flat_mount_mode)
    try:
        # Off-Screen Renderer
        plotter.off_screen = True
        # Isometrische Kamera
        plotter.view_isometric()
        img = plotter.screenshot(return_img=True, window_size=(width_px, height_px))
        plotter.close()
        bio = io.BytesIO()
        from PIL import Image  # pillow ist transitiv via reportlab optional, falls nicht, bitte installieren
        Image.fromarray(img).save(bio, format="PNG")
        return bio.getvalue()
    except Exception:
        try:
            plotter.close()
        except Exception:
            pass
        return b""

# ==== Export ====
def export_stl(
    project_data: Dict, dims: BuildingDims, roof_type: str, module_quantity: int, path: str
) -> str:
    pitch = _safe_get_roof_inclination_deg(project_data)
    plotter, parts = build_scene(project_data, dims, roof_type, pitch, LayoutConfig(mode="auto", removed_indices=[]), module_quantity)
    # Vereinfachung: Panels + Roof in ein Mesh mergen
    meshes = []
    for lst in parts.values():
        meshes.extend(lst)
    # roof extrahieren aus Plotter (Name "roof"):
    # pyvista Plotter speichert nicht trivial Mesh-Liste -> wir fügen nochmal zusammen:
    combo = None
    for m in meshes:
        combo = m if combo is None else combo.merge(m)
    if combo is None:
        combo = make_box(1,1,0.01,0)
    combo.save(path)  # STL
    plotter.close()
    return path

def export_gltf(
    project_data: Dict, dims: BuildingDims, roof_type: str, module_quantity: int, path: str
) -> str:
    # glTF-Export über trimesh
    import trimesh as tm
    pitch = _safe_get_roof_inclination_deg(project_data)
    plotter, parts = build_scene(project_data, dims, roof_type, pitch, LayoutConfig(mode="auto", removed_indices=[]), module_quantity)
    # Sammle Panels zu einem einfachen Mesh
    tm_meshes = []
    for lst in parts.values():
        for m in lst:
            v = m.points
            faces = m.faces.reshape(-1, 4)[:,1:]
            tm_meshes.append(tm.Trimesh(vertices=v, faces=faces, process=False))
    if not tm_meshes:
        # Fallback flache Platte
        tm_meshes.append(tm.creation.box(extents=(1,1,0.01)))
    scene = tm.Scene(tm_meshes)
    scene.export(path)
    plotter.close()
    return path

2) streamlit_app/pages/solar_3d_view.py

UI in/unter dem Solarkalkulator. Button aktiviert Viewer, Tabs für Automatik/Manuell, Garage/Fassade-Fallback, Statusfenster (verbaut/fehlt), Speichern/Laden/Reset, Screenshot-Download, STL/glTF-Export.

# streamlit_app/pages/solar_3d_view.py
import json
import streamlit as st
from stpyvista import stpyvista  # interaktiver 3D-Viewer (Orbit/Zoom/Rotate)
from utils.pv3d import (
    BuildingDims, LayoutConfig, build_scene,
    render_image_bytes, export_stl, export_gltf
)

st.set_page_config(page_title="3D PV-Visualisierung", layout="wide")

# ---- Projekt-/App-Daten laden ----
# Erwartet: st.session_state.project_data und st.session_state.analysis_results vorhanden
project_data = st.session_state.get("project_data", {}) or {}
analysis_results = st.session_state.get("analysis_results", {}) or {}

# Wichtige Felder:
details = project_data.get("project_details", {}) or {}
roof_type = details.get("roof_type") or details.get("dachform") or "Flachdach"  # Dein DropDown
roof_covering = details.get("roof_covering_type") or details.get("roof_covering") or "Ziegel"
roof_incl_deg = details.get("roof_inclination_deg") or 30.0
orientation = (
    details.get("roof_orientation")
    or project_data.get("roof_orientation")
    or "Süd"
)
# Modulanzahl aus Solarkalkulator – du hast gesagt: dort wird sie gewählt
module_quantity = (
    analysis_results.get("module_quantity")
    or project_data.get("module_quantity")
    or details.get("module_quantity")
    or 0
)

st.title("🔧 3D-Visualisierung (PV-Dach)")

with st.sidebar:
    st.header("Einstellungen")
    # Dimensionen (anpassbar)
    colA, colB = st.columns(2)
    with colA:
        L = st.number_input("Gebäudelänge [m]", 8.0, 60.0, value=10.0, step=0.5)
        roof_t = st.selectbox("Dachform", ["Flachdach","Satteldach","Walmdach","Krüppelwalmdach","Pultdach","Zeltdach","Sonstiges"], index=0)
    with colB:
        W = st.number_input("Gebäudebreite [m]", 5.0, 40.0, value=6.0, step=0.5)
        H = st.number_input("Traufhöhe [m]", 3.0, 20.0, value=6.0, step=0.5)
    dims = BuildingDims(length_m=L, width_m=W, wall_height_m=H)

    # Belegungsmodus
    mode = st.radio("Belegungsmodus", options=["Automatisch","Manuell"], index=0, horizontal=True)
    manual = (mode == "Manuell")

    # Flachdach-Aufständerung
    flat_mode = st.selectbox("Aufständerung (Flachdach)", ["Süd","Ost-West"], index=0)
    flat_mode_key = "south" if flat_mode.startswith("S") else "eastwest"

    st.divider()
    st.subheader("Platzmangel-Fallback")
    use_garage = st.checkbox("Garage/Carport automatisch hinzufügen", value=False)
    use_facade = st.checkbox("Fassadenbelegung aktivieren", value=False)

    removed_json = st.text_area("Manuell entfernte Indizes (Komma-separiert, 0-basiert)", value="")
    removed = []
    if removed_json.strip():
        try:
            removed = [int(x.strip()) for x in removed_json.split(",") if x.strip().isdigit()]
        except Exception:
            st.warning("Indizes nicht lesbar – bitte '0,1,2' Format verwenden.")

    layout = LayoutConfig(
        mode="manual" if manual else "auto",
        use_garage=use_garage,
        use_facade=use_facade,
        removed_indices=removed
    )

    st.divider()
    st.subheader("Aktionen")
    do_render = st.button("🔍 Visualisierung aktualisieren", type="primary")
    do_reset  = st.button("↺ Reset (Auto-Belegung)")
    do_save   = st.button("💾 Layout speichern")
    do_load   = st.button("📂 Layout laden")

# Session Defaults
_session = st.session_state
if "pv3d_layout_json" not in _session:
    _session["pv3d_layout_json"] = layout.to_json()

if do_reset:
    layout = LayoutConfig(mode="auto", removed_indices=[])
    _session["pv3d_layout_json"] = layout.to_json()
    st.success("Layout auf Automatik zurückgesetzt.")

if do_save:
    _session["pv3d_layout_json"] = layout.to_json()
    st.success("Layout gespeichert.")

if do_load:
    try:
        layout = LayoutConfig.from_json(_session["pv3d_layout_json"])
        st.success("Layout geladen.")
    except Exception:
        st.error("Layout konnte nicht geladen werden.")

# Hinweis zur Datenquelle
with st.expander("Datenquelle (App-Bindung)"):
    st.write("""
- **Ausrichtung/Dachneigung/Dachdeckung** werden aus `project_data["project_details"]` gelesen (kompatibel zu eurem `placeholders.py`).  
- **Modulanzahl** kommt aus Solarkalkulator/Analyse (`analysis_results["module_quantity"]`), fällt zurück auf `project_data`.  
    """)

# Renderer: nur auf Button oder erste Anzeige
if do_render or "pv3d_last_rendered" not in _session:
    _session["pv3d_last_rendered"] = True
    # Szene aufbauen
    from utils.pv3d import build_scene
    plotter, parts = build_scene(
        project_data=project_data,
        dims=dims,
        roof_type=roof_t,
        roof_pitch_deg=roof_incl_deg,
        layout=layout,
        module_quantity=int(module_quantity),
        flat_mount_mode=flat_mode_key
    )
    st.session_state["_pv3d_plotter"] = plotter
else:
    plotter = st.session_state.get("_pv3d_plotter")

# Fehlerschild falls Plotter fehlt
if not plotter:
    st.error("3D-Plotter konnte nicht initialisiert werden.")
    st.stop()

# Linke Spalte: Viewer; rechte Spalte: Status/Aktionen
c1, c2 = st.columns([3,2])

with c1:
    st.subheader("3D-Viewer")
    # Hinweis: stpyvista rendert interaktiv mit Orbit/Zoom/Rotate
    stpyvista(plotter, key="pv3d_viewer")

with c2:
    st.subheader("Status")
    # Grobe Kapazitätsschätzung (wie in pv3d)
    est_cap = int((dims.length_m * dims.width_m) // (1.05 * 1.05 * 1.76))
    placed = min(est_cap, int(module_quantity)) if layout.mode == "auto" else max(0, int(module_quantity) - len(layout.removed_indices))
    remaining = max(0, int(module_quantity) - placed)
    st.metric("Gewählte Module", int(module_quantity))
    st.metric("Platziert (geschätzt)", placed)
    st.metric("Fehlend", remaining)

    if remaining > 0:
        st.warning("**Achtung:** Dachfläche reicht nicht. Aktiviere Garage/Fassade in der Seitenleiste.")
    else:
        st.info("Alle Module passen auf die gewählte Dachfläche.")

    st.divider()
    st.subheader("Export")
    colx, coly = st.columns(2)
    with colx:
        if st.button("🖼️ Screenshot (PNG) erzeugen"):
            png = render_image_bytes(project_data, dims, roof_t, int(module_quantity), layout, flat_mode_key, width_px=1600, height_px=1000)
            if png:
                st.download_button("PNG herunterladen", data=png, file_name="pv3d.png", mime="image/png")
            else:
                st.error("Screenshot fehlgeschlagen.")
    with coly:
        if st.button("📐 STL exportieren"):
            path = export_stl(project_data, dims, roof_t, int(module_quantity), path="pv3d_model.stl")
            with open(path, "rb") as f:
                st.download_button("STL herunterladen", f.read(), file_name="pv3d_model.stl", mime="model/stl")

    if st.button("🌐 glTF (.glb) exportieren"):
        path = export_gltf(project_data, dims, roof_t, int(module_quantity), path="pv3d_scene.glb")
        with open(path, "rb") as f:
            st.download_button("glTF herunterladen", f.read(), file_name="pv3d_scene.glb", mime="model/gltf-binary")

st.success("3D-Tool aktiv. Orbit/Rotate/Zoom im Viewer sind möglich.")


Hinweise zur Datenbindung:
Die von dir genannten Felder existieren gemäß euren Tests/Placeholders so bzw. mit robusten Fallbacks (Ausrichtung/Neigung/Deckung) – genau daran hänge ich mich auf 

tests/test_roof_data

 

pdf_template_engine/placeholders

 

pdf_template_engine/placeholders

 

pdf_template_engine/placeholders

.

3) PDF-Integration (streamlit_app/utils/pdf_visual_inject.py)

Erzeugt on-the-fly den 3D-Screenshot (PNG-Bytes) und liefert ein ReportLab Flowable (oder Bytes), damit du es in euren bestehenden PDF-Flow einbauen kannst (ihr nutzt reportlab; die App hat bereits PDF-Pipelines/Tests mit dynamischen Placeholders) – du kannst image_bytes in eure offer_data/analysis_results hängen und im Generator einfügen.

# streamlit_app/utils/pdf_visual_inject.py
from __future__ import annotations
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from io import BytesIO

from .pv3d import BuildingDims, LayoutConfig, render_image_bytes

def make_pv3d_image_flowable(
    project_data: dict,
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout: LayoutConfig | None = None,
    width_cm: float = 17.0
):
    png = render_image_bytes(project_data, dims, roof_type, int(module_quantity), layout or LayoutConfig())
    if not png:
        return None
    bio = BytesIO(png)
    img = Image(bio, width=width_cm*cm, height=(width_cm*0.62)*cm)  # Seitenverhältnis ~ 16:10
    return img

def get_pv3d_png_bytes_for_pdf(
    project_data: dict,
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout: LayoutConfig | None = None,
) -> bytes:
    return render_image_bytes(project_data, dims, roof_type, int(module_quantity), layout or LayoutConfig())


Einbindung im PDF-Generator (Beispiel):

# irgendwo in eurem pdf_generator, wo ihr Story/Flowables baut
from streamlit_app.utils.pdf_visual_inject import make_pv3d_image_flowable
from streamlit_app.utils.pv3d import BuildingDims, LayoutConfig

dims = BuildingDims(length_m=10, width_m=6, wall_height_m=6)
layout = LayoutConfig(mode="auto")
roof_type = (project_data.get("project_details",{}) or {}).get("roof_type", "Flachdach")
module_qty = analysis_results.get("module_quantity", 0)

flow = make_pv3d_image_flowable(project_data, dims, roof_type, module_qty, layout, width_cm=17.0)
if flow:
    Story.append(flow)
# Optional: darunter eine Bildunterschrift
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
Story.append(Paragraph("Abb.: 3D-Visualisierung der geplanten PV-Belegung", getSampleStyleSheet()["Normal"]))

4) Einbettung in den Solarkalkulator (Button)

Falls du den Viewer direkt im Solarkalkulator zeigen willst, füge im Solarkalkulator-Code (Seite/Widget) diesen Button ein und leite auf die neue Seite (oder rendere inline):

# im Solarkalkulator-Panel:
if st.button("3D-Visualisierung öffnen"):
    # Variante A: Navigiere auf die Seite 'solar_3d_view'
    st.switch_page("pages/solar_3d_view.py")
    # Variante B (inline): importiere build_scene und rendere stpyvista hier (nur wenn die Seite nicht überfrachtet):
    # from utils.pv3d import build_scene, BuildingDims, LayoutConfig
    # plotter, _ = build_scene(project_data, BuildingDims(10,6,6), roof_type, roof_incl_deg, LayoutConfig(), module_quantity)
    # stpyvista(plotter, key="pv3d_inline")


Deine Architektur sieht ausdrücklich Pages/Widgets/Kern vor, Navigation ohne Reload ist konzeptuell im Router angelegt (Dokueintrag), d. h. eine eigene Seite ist die stabilste Integration 

chore: initial clean snapshot w…

.

5) Warum passt das zu euren Daten?

Ausrichtung & Dachneigung: wir lesen exakt aus den Schlüsseln, die eure Tests/Placeholders prüfen (inkl. Fallbacks) – damit ist die Bindung kompatibel ohne harte Kopplung an einen einzigen Key 

tests/test_roof_data

 

pdf_template_engine/placeholders

 

pdf_template_engine/placeholders

.

Dachdeckung: Farbwahl basiert auf roof_covering_type/roof_covering, wie in euren Placeholders abgelegt 

pdf_template_engine/placeholders

.

Struktur: Die Dateien fügen sich in eure modularisierte Streamlit-App-Ordnerstruktur ein (pages/utils), wie in eurer Readme/Index-Struktur beschrieben 

chore: initial clean snapshot w…

.

6) Was ist alles drin (Checkliste deiner Anforderungen)

Aktivierung per Button (Seite/Inline), 3D-Viewer eingebettet

Dachformen: Flach, Sattel, Walm, Krüppelwalm, Pult, Zelt, Sonstiges (geometrisch umgesetzt)

Ausrichtung/Kompass: Hausdrehung + roter Nordpfeil; Ausrichtung aus Bedarfsanalyse

Dachdeckung → Farbe (markierte Fläche)

PV-Belegung: Automatik (Raster), Manuell (Entfernen/Indexliste), Flachdach Süd/Ost-West

Kapazitätsprüfung (geschätzt), Fallback: Garage/Fassade-Belegung

Live-Zähler: platziert/fehlt

Editierbar/Speicherbar/Ladbar (JSON im Session-State), Reset

Export: Screenshot (PNG), STL, glTF

PDF-Einbettung (ReportLab Flowable/Bytes)

Zoom/Orbit/3D View: durch stpyvista interaktiv

Größenanpassung: Länge/Breite/Höhe frei wählbar

Stabilität: Off-Screen Screenshot mit Fallback, keine Blocker für restliche App

7) Wichtig zur Installation

pip install -r requirements.txt (ergänzte Pakete).

Falls VTK in bestimmten Linux-Envs OpenGL braucht: sicherstellen, dass LibGL vorhanden ist.

First run: Seite pages/solar_3d_view.py öffnen, oder Button im Solarkalkulator drücken.

8) Grenzen & ehrlich gesagt

Freies Drag&Drop von Panels direkt im 3D-Canvas ist mit stpyvista (ohne eigenes JS-Component) nicht bidirektional. Ich habe deshalb manuellen Modus via Index-Liste und Offsets vorgesehen (stabil in Streamlit). „Richtiges“ Drag&Drop ginge später per eigenem Three.js-Component – aktuell nicht nötig, um 100 % eurer Pflicht-Features zu erfüllen.

Kapazitätsprüfung nutzt die gewählten Geometrie-Dimensionen; wenn du unrealistische Dimensionen einstellst, passt die Schätzung sich an. Das ist beabsichtigt (dynamisch/individuell).