"""
PV3D Export Module

Dieses Modul enthält alle Export-Funktionen für die 3D-Visualisierung:
- Screenshot-Export (PNG, JPEG)
- Multi-View Screenshots (ZIP)
- 360° Animationen (GIF)
- 3D-Modell Export (STL, GLTF, OBJ)
"""

import io
import math
import os
import tempfile
import zipfile
from typing import Dict, Any, List, Tuple, Optional, Callable
from PIL import Image
import plotly.graph_objects as go

# Import der Datenklassen
try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig
    )
    from utils.pv3d_plotly import build_plotly_scene
    PV3D_AVAILABLE = True
except ImportError as e:
    PV3D_AVAILABLE = False
    print(f"WARNUNG: PV3D nicht verfügbar: {e}")


# ============================================================================
# SCREENSHOT EXPORT
# ============================================================================

def export_screenshot(
    fig: go.Figure,
    format: str = "png",
    width: int = 1600,
    height: int = 1000,
    scale: float = 2.0
) -> bytes:
    """
    Exportiert einen Screenshot der Plotly 3D-Szene.
    
    Args:
        fig: Plotly Figure Objekt
        format: Ausgabeformat ("png" oder "jpeg")
        width: Breite in Pixeln
        height: Höhe in Pixeln
        scale: Skalierungsfaktor für höhere Auflösung (1.0 = normal, 2.0 = doppelt)
    
    Returns:
        Bild als Bytes
    
    Example:
        >>> fig = build_plotly_scene(...)
        >>> png_bytes = export_screenshot(fig, format="png", width=1920, height=1080)
        >>> with open("screenshot.png", "wb") as f:
        ...     f.write(png_bytes)
    """
    try:
        # Setze Größe
        fig.update_layout(width=width, height=height)
        
        # Konvertiere zu Bild-Bytes
        img_bytes = fig.to_image(format=format, scale=scale)
        
        return img_bytes
    except Exception as e:
        print(f"Fehler beim Screenshot-Export: {e}")
        import traceback
        traceback.print_exc()
        return b""


def export_screenshot_from_scene(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: Optional[Any] = None,
    format: str = "png",
    width: int = 1600,
    height: int = 1000,
    scale: float = 2.0,
    selected_modules: Optional[List[int]] = None
) -> bytes:
    """
    Erstellt einen Screenshot direkt aus Szenen-Parametern.
    
    Args:
        project_data: Projektdaten-Dictionary
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp ("Flachdach", "Satteldach", etc.)
        module_quantity: Anzahl der PV-Module
        layout_config: Layout-Konfiguration (optional)
        format: Ausgabeformat ("png" oder "jpeg")
        width: Breite in Pixeln
        height: Höhe in Pixeln
        scale: Skalierungsfaktor
        selected_modules: Liste ausgewählter Modul-Indizes (optional)
    
    Returns:
        Bild als Bytes
    """
    try:
        if not PV3D_AVAILABLE:
            raise RuntimeError("PV3D ist nicht verfügbar")
        
        # Erstelle Plotly Figure
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            selected_modules=selected_modules or []
        )
        
        # Exportiere Screenshot
        return export_screenshot(fig, format=format, width=width, height=height, scale=scale)
        
    except Exception as e:
        print(f"Fehler beim Screenshot-Export: {e}")
        import traceback
        traceback.print_exc()
        return b""


# ============================================================================
# MULTI-VIEW EXPORT
# ============================================================================

def export_multi_view(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: Optional[Any] = None,
    output_dir: str = ".",
    base_filename: str = "view",
    resolution: Tuple[int, int] = (1200, 750),
    views: Optional[List[str]] = None,
    return_zip_bytes: bool = False
) -> Dict[str, bytes]:
    """
    Erstellt Multi-View Screenshots aus verschiedenen Kamera-Perspektiven.
    
    Args:
        project_data: Projektdaten-Dictionary
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp
        module_quantity: Anzahl der PV-Module
        layout_config: Layout-Konfiguration (optional)
        output_dir: Ausgabe-Verzeichnis für ZIP-Datei
        base_filename: Basis-Dateiname für Screenshots
        resolution: Auflösung als (width, height) Tuple
        views: Liste der zu rendernden Ansichten (optional, default: alle)
        return_zip_bytes: Wenn True, gibt ZIP-Bytes zurück statt Datei zu schreiben
    
    Returns:
        Dictionary mit view_name -> png_bytes
    
    Example:
        >>> views_dict = export_multi_view(
        ...     project_data={},
        ...     dims=BuildingDims(10, 6, 3),
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     views=["isometric", "top"]
        ... )
    """
    try:
        if not PV3D_AVAILABLE:
            raise RuntimeError("PV3D ist nicht verfügbar")
        
        width, height = resolution
        view_images = {}
        
        print("Multi-View Export: Erstelle Basis-Szene...")
        
        # Basis-Szene EINMAL erstellen
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            selected_modules=[]
        )
        
        # Setze Größe einmal für alle Views
        fig.update_layout(width=width, height=height)
        
        # Definiere Kamera-Ansichten
        all_camera_configs = {
            "isometric": {
                "eye": {"x": 0.7, "y": -0.7, "z": 0.5},
                "name": "Isometrisch"
            },
            "top": {
                "eye": {"x": 0, "y": 0, "z": 2.5},
                "name": "Draufsicht"
            },
            "south": {
                "eye": {"x": 0, "y": -2.0, "z": 0.3},
                "name": "Südansicht"
            },
            "east": {
                "eye": {"x": 2.0, "y": 0, "z": 0.3},
                "name": "Ostansicht"
            },
            "west": {
                "eye": {"x": -2.0, "y": 0, "z": 0.3},
                "name": "Westansicht"
            },
            "north": {
                "eye": {"x": 0, "y": 2.0, "z": 0.3},
                "name": "Nordansicht"
            }
        }
        
        # Filtere Ansichten wenn spezifiziert
        if views:
            camera_configs = {k: v for k, v in all_camera_configs.items() if k in views}
        else:
            # Default: isometric, top, south, east
            camera_configs = {
                k: v for k, v in all_camera_configs.items() 
                if k in ["isometric", "top", "south", "east"]
            }
        
        print(f"Basis-Szene erstellt, rendere {len(camera_configs)} Ansichten...")
        
        # Rendere jede Ansicht
        for view_name, camera_config in camera_configs.items():
            try:
                print(f"  Rendere {camera_config['name']} ({view_name})...")
                
                # Ändere NUR die Kamera
                fig.update_layout(scene_camera={"eye": camera_config["eye"]})
                
                # Konvertiere zu PNG
                png_bytes = fig.to_image(format="png", scale=1.0)
                view_images[view_name] = png_bytes
                
                print(f"  ✓ {view_name} fertig ({len(png_bytes)} bytes)")
                
            except Exception as e:
                print(f"Fehler beim Rendern von {view_name}: {e}")
        
        # Erstelle ZIP-Datei
        if view_images:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for view_name, png_bytes in view_images.items():
                    filename = f"{base_filename}_{view_name}.png"
                    zipf.writestr(filename, png_bytes)
            
            if return_zip_bytes:
                # Gib ZIP-Bytes zurück (NUR die Bytes, kein Dictionary!)
                zip_buffer.seek(0)
                return zip_buffer.read()
            else:
                # Schreibe ZIP-Datei
                zip_path = os.path.join(output_dir, f"{base_filename}_multi_view.zip")
                with open(zip_path, 'wb') as f:
                    f.write(zip_buffer.getvalue())
                print(f"Multi-View ZIP erstellt: {zip_path} ({len(view_images)} Ansichten)")
                
                # Gib Dictionary mit View-Images zurück
                return view_images
        
        # Wenn keine Images erstellt wurden, gib leeres Dictionary zurück
        return {}
        
    except Exception as e:
        print(f"Fehler bei Multi-View Export: {e}")
        import traceback
        traceback.print_exc()
        return {}


# ============================================================================
# 360° ANIMATION EXPORT
# ============================================================================

def export_360_animation(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: Optional[Any] = None,
    filepath: str = "animation_360.gif",
    frames: int = 36,
    resolution: Tuple[int, int] = (600, 450),
    duration_ms: int = 100,
    camera_distance: float = 2.5,
    camera_height: float = 0.4,
    return_bytes: bool = False,
    progress_callback: Optional[Callable] = None
) -> bytes:
    """
    Erstellt eine 360° Animation als GIF.
    
    Args:
        project_data: Projektdaten-Dictionary
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp
        module_quantity: Anzahl der PV-Module
        layout_config: Layout-Konfiguration (optional)
        filepath: Pfad zur Ausgabe-GIF-Datei
        frames: Anzahl der Frames (mehr = flüssiger, aber größer)
        resolution: Auflösung als (width, height) Tuple
        duration_ms: Dauer pro Frame in Millisekunden
        camera_distance: Abstand der Kamera vom Zentrum
        camera_height: Höhe der Kamera
        return_bytes: Wenn True, gibt GIF-Bytes zurück statt Datei zu schreiben
    
    Returns:
        GIF als Bytes (wenn return_bytes=True), sonst leere Bytes
    
    Example:
        >>> gif_bytes = export_360_animation(
        ...     project_data={},
        ...     dims=BuildingDims(10, 6, 3),
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     frames=36,
        ...     return_bytes=True
        ... )
    """
    try:
        if not PV3D_AVAILABLE:
            raise RuntimeError("PV3D ist nicht verfügbar")
        
        width, height = resolution
        images = []
        
        print("360° Animation: Erstelle Basis-Szene...")
        
        # Erstelle Basis-Szene EINMAL
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            selected_modules=[]
        )
        
        # Setze Größe einmal
        fig.update_layout(width=width, height=height)
        
        print(f"Basis-Szene erstellt, rendere {frames} Frames...")
        
        # Rendere jeden Frame
        for i in range(frames):
            try:
                # Berechne Rotationswinkel
                angle_deg = (360.0 / frames) * i
                angle_rad = math.radians(angle_deg)
                
                # Berechne Kamera-Position (Rotation um Z-Achse)
                camera_x = camera_distance * math.cos(angle_rad)
                camera_y = camera_distance * math.sin(angle_rad)
                camera_z = camera_height
                
                # Ändere NUR die Kamera
                fig.update_layout(
                    scene_camera=dict(
                        eye=dict(x=camera_x, y=camera_y, z=camera_z),
                        center=dict(x=0, y=0, z=0),
                        up=dict(x=0, y=0, z=1)
                    )
                )
                
                # Konvertiere zu PNG
                png_bytes = fig.to_image(format="png", scale=1.0)
                img = Image.open(io.BytesIO(png_bytes))
                images.append(img)
                
                # Fortschritt (jedes 6. Frame)
                if (i + 1) % 6 == 0:
                    progress = ((i + 1) / frames) * 100
                    print(f"  Fortschritt: {progress:.0f}% ({i + 1}/{frames} Frames)")
                
            except Exception as e:
                print(f"Fehler beim Rendern von Frame {i}: {e}")
        
        # Erstelle GIF
        if images:
            # Speichere als GIF
            images[0].save(
                filepath,
                save_all=True,
                append_images=images[1:],
                duration=duration_ms,
                loop=0,
                optimize=False  # Schneller, aber größere Datei
            )
            
            print(f"360° Animation erstellt: {filepath} ({len(images)} Frames)")
            
            # Lese GIF-Bytes wenn gewünscht
            if return_bytes:
                with open(filepath, 'rb') as f:
                    return f.read()
            else:
                return b""
        else:
            print("Keine Frames für GIF erstellt")
            return b""
            
    except Exception as e:
        print(f"Fehler bei 360° Animation: {e}")
        import traceback
        traceback.print_exc()
        return b""


# ============================================================================
# 3D MODEL EXPORT
# ============================================================================

def export_3d_model(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    filepath: str,
    format: str = "auto"
) -> bool:
    """
    Exportiert das 3D-Modell in verschiedenen Formaten.
    
    Args:
        project_data: Projektdaten-Dictionary
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp
        module_quantity: Anzahl der PV-Module
        layout_config: Layout-Konfiguration
        filepath: Pfad zur Ausgabe-Datei
        format: Ausgabeformat ("stl", "gltf", "glb", "obj", oder "auto" für Erkennung aus Dateiendung)
    
    Returns:
        True bei Erfolg, False bei Fehler
    
    Example:
        >>> success = export_3d_model(
        ...     project_data={},
        ...     dims=BuildingDims(10, 6, 3),
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=LayoutConfig(mode="auto"),
        ...     filepath="model.stl"
        ... )
    """
    try:
        # Import der Export-Funktionen aus pv3d
        from utils.pv3d import export_stl, export_gltf
        
        # Erkenne Format aus Dateiendung wenn "auto"
        if format == "auto":
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".stl":
                format = "stl"
            elif ext in [".gltf", ".glb"]:
                format = "gltf"
            elif ext == ".obj":
                format = "obj"
            else:
                raise ValueError(f"Unbekanntes Dateiformat: {ext}")
        
        # Exportiere basierend auf Format
        if format == "stl":
            return export_stl(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                filepath=filepath
            )
        
        elif format in ["gltf", "glb"]:
            return export_gltf(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                filepath=filepath
            )
        
        elif format == "obj":
            # OBJ Export über STL als Zwischenschritt
            # (PyVista unterstützt OBJ nicht direkt, aber trimesh kann STL zu OBJ konvertieren)
            print("OBJ Export wird über STL-Konvertierung durchgeführt...")
            
            # Erstelle temporäre STL-Datei
            with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
                tmp_stl_path = tmp.name
            
            try:
                # Exportiere als STL
                success = export_stl(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_type,
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    filepath=tmp_stl_path
                )
                
                if not success:
                    return False
                
                # Konvertiere STL zu OBJ mit trimesh
                import trimesh
                mesh = trimesh.load(tmp_stl_path)
                mesh.export(filepath)
                
                print(f"OBJ Export erfolgreich: {filepath}")
                return True
                
            finally:
                # Lösche temporäre STL-Datei
                if os.path.exists(tmp_stl_path):
                    os.remove(tmp_stl_path)
        
        else:
            raise ValueError(f"Nicht unterstütztes Format: {format}")
    
    except Exception as e:
        print(f"Fehler beim 3D-Modell Export: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def export_all_formats(
    project_data: Dict[str, Any],
    dims: BuildingDims,
    roof_type: str,
    module_quantity: int,
    layout_config: LayoutConfig,
    output_dir: str = ".",
    base_filename: str = "pv_model"
) -> Dict[str, bool]:
    """
    Exportiert das 3D-Modell in allen verfügbaren Formaten.
    
    Args:
        project_data: Projektdaten-Dictionary
        dims: BuildingDims mit Gebäudedimensionen
        roof_type: Dachtyp
        module_quantity: Anzahl der PV-Module
        layout_config: Layout-Konfiguration
        output_dir: Ausgabe-Verzeichnis
        base_filename: Basis-Dateiname (ohne Endung)
    
    Returns:
        Dictionary mit format -> success (bool)
    
    Example:
        >>> results = export_all_formats(
        ...     project_data={},
        ...     dims=BuildingDims(10, 6, 3),
        ...     roof_type="Satteldach",
        ...     module_quantity=20,
        ...     layout_config=LayoutConfig(mode="auto"),
        ...     output_dir="exports"
        ... )
        >>> print(f"STL: {results['stl']}, glTF: {results['gltf']}")
    """
    results = {}
    
    formats = ["stl", "glb", "obj"]
    
    for fmt in formats:
        filepath = os.path.join(output_dir, f"{base_filename}.{fmt}")
        print(f"\nExportiere {fmt.upper()}...")
        
        try:
            success = export_3d_model(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                filepath=filepath,
                format=fmt
            )
            results[fmt] = success
            
            if success:
                print(f"✓ {fmt.upper()} Export erfolgreich: {filepath}")
            else:
                print(f"✗ {fmt.upper()} Export fehlgeschlagen")
                
        except Exception as e:
            print(f"✗ {fmt.upper()} Export Fehler: {e}")
            results[fmt] = False
    
    return results
