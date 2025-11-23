"""
3D Export Service

This service provides comprehensive 3D model export functionality in multiple formats:
- STL (Stereolithography) - for 3D printing
- OBJ (Wavefront) - universal 3D format
- GLTF/GLB (GL Transmission Format) - web-optimized 3D
- DXF (Drawing Exchange Format) - for CAD software
- PDF 3D - embedded 3D models in PDF
- PNG/JPG - high-quality image exports
"""

import sys
import io
import os
import tempfile
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# Add parent directory to path to import legacy modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import trimesh
    import numpy as np
    from PIL import Image
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    logging.warning("trimesh not available - some export formats will be limited")

try:
    import ezdxf
    DXF_AVAILABLE = True
except ImportError:
    DXF_AVAILABLE = False
    logging.warning("ezdxf not available - DXF export will not be available")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("reportlab not available - PDF 3D export will be limited")

try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig,
        export_stl as legacy_export_stl,
        export_gltf as legacy_export_gltf
    )
    from utils.pv3d_plotly import build_plotly_scene
    from utils.pv3d_export import (
        export_screenshot,
        export_multi_view,
        export_360_animation
    )
    PV3D_AVAILABLE = True
except ImportError as e:
    logging.warning(f"3D visualization modules not available: {e}")
    PV3D_AVAILABLE = False

logger = logging.getLogger(__name__)


class Export3DService:
    """
    Service for exporting 3D models in various formats.
    
    Supported formats:
    - STL: Stereolithography format for 3D printing
    - OBJ: Wavefront OBJ format (universal)
    - GLTF/GLB: GL Transmission Format (web-optimized)
    - DXF: AutoCAD Drawing Exchange Format
    - PDF 3D: PDF with embedded 3D model
    - PNG/JPG: High-quality image exports
    """
    
    def __init__(self):
        """Initialize the 3D export service."""
        self.supported_formats = self._get_supported_formats()
        logger.info(f"Export3DService initialized with formats: {list(self.supported_formats.keys())}")
    
    def _get_supported_formats(self) -> Dict[str, bool]:
        """Get dictionary of supported export formats."""
        return {
            "stl": PV3D_AVAILABLE,
            "obj": PV3D_AVAILABLE and TRIMESH_AVAILABLE,
            "gltf": PV3D_AVAILABLE and TRIMESH_AVAILABLE,
            "glb": PV3D_AVAILABLE and TRIMESH_AVAILABLE,
            "dxf": DXF_AVAILABLE,
            "pdf": PDF_AVAILABLE,
            "png": PV3D_AVAILABLE,
            "jpg": PV3D_AVAILABLE,
            "jpeg": PV3D_AVAILABLE
        }
    
    def is_format_supported(self, format: str) -> bool:
        """Check if a format is supported."""
        return self.supported_formats.get(format.lower(), False)
    
    # ========================================================================
    # STL Export
    # ========================================================================
    
    def export_stl(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model as STL (Stereolithography) format.
        
        STL is widely used for 3D printing and CAD applications.
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            options: Export options (binary=True/False, ascii=False)
            
        Returns:
            STL file as bytes
        """
        if not self.is_format_supported("stl"):
            raise RuntimeError("STL export not available")
        
        try:
            options = options or {}
            
            # Create building dimensions
            dims = BuildingDims(
                length_m=building_dims.get("length_m", 10.0),
                width_m=building_dims.get("width_m", 6.0),
                wall_height_m=building_dims.get("wall_height_m", 6.0)
            )
            
            # Create layout config
            layout_config = LayoutConfig(
                roof_type=roof_config.get("type", "flat"),
                roof_angle_deg=roof_config.get("angle", 15.0),
                orientation=roof_config.get("orientation", "south"),
                module_count=module_config.get("count", 20)
            )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Export using legacy function
                success = legacy_export_stl(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_config.get("type", "flat"),
                    module_quantity=module_config.get("count", 20),
                    layout_config=layout_config,
                    filepath=tmp_path
                )
                
                if not success:
                    raise RuntimeError("STL export failed")
                
                # Read file
                with open(tmp_path, 'rb') as f:
                    stl_bytes = f.read()
                
                return stl_bytes
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.error(f"Error exporting STL: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # OBJ Export
    # ========================================================================
    
    def export_obj(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model as OBJ (Wavefront) format.
        
        OBJ is a universal 3D format supported by most 3D software.
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            options: Export options (include_mtl=True/False)
            
        Returns:
            OBJ file as bytes
        """
        if not self.is_format_supported("obj"):
            raise RuntimeError("OBJ export not available")
        
        try:
            options = options or {}
            
            # First export as STL
            stl_bytes = self.export_stl(
                project_data=project_data,
                building_dims=building_dims,
                roof_config=roof_config,
                module_config=module_config
            )
            
            # Convert STL to OBJ using trimesh
            mesh = trimesh.load(io.BytesIO(stl_bytes), file_type='stl')
            
            # Export as OBJ
            obj_export = trimesh.exchange.obj.export_obj(mesh)
            
            return obj_export.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error exporting OBJ: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # GLTF/GLB Export
    # ========================================================================
    
    def export_gltf(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        binary: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model as GLTF or GLB format.
        
        GLTF is optimized for web and real-time applications.
        GLB is the binary version of GLTF.
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            binary: If True, export as GLB (binary), else GLTF (JSON)
            options: Export options
            
        Returns:
            GLTF/GLB file as bytes
        """
        if not self.is_format_supported("gltf"):
            raise RuntimeError("GLTF export not available")
        
        try:
            options = options or {}
            
            # Create building dimensions
            dims = BuildingDims(
                length_m=building_dims.get("length_m", 10.0),
                width_m=building_dims.get("width_m", 6.0),
                wall_height_m=building_dims.get("wall_height_m", 6.0)
            )
            
            # Create layout config
            layout_config = LayoutConfig(
                roof_type=roof_config.get("type", "flat"),
                roof_angle_deg=roof_config.get("angle", 15.0),
                orientation=roof_config.get("orientation", "south"),
                module_count=module_config.get("count", 20)
            )
            
            # Create temporary file
            ext = ".glb" if binary else ".gltf"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Export using legacy function
                success = legacy_export_gltf(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_config.get("type", "flat"),
                    module_quantity=module_config.get("count", 20),
                    layout_config=layout_config,
                    filepath=tmp_path
                )
                
                if not success:
                    raise RuntimeError("GLTF export failed")
                
                # Read file
                with open(tmp_path, 'rb') as f:
                    gltf_bytes = f.read()
                
                return gltf_bytes
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.error(f"Error exporting GLTF: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # DXF Export
    # ========================================================================
    
    def export_dxf(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model as DXF (Drawing Exchange Format) for CAD software.
        
        DXF is widely supported by AutoCAD and other CAD applications.
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            options: Export options (version='R2018', units='Meters')
            
        Returns:
            DXF file as bytes
        """
        if not self.is_format_supported("dxf"):
            raise RuntimeError("DXF export not available - ezdxf library required")
        
        try:
            options = options or {}
            version = options.get('version', 'R2018')
            units = options.get('units', 'Meters')
            
            # Create new DXF document
            doc = ezdxf.new(version)
            msp = doc.modelspace()
            
            # Set units
            doc.header['$INSUNITS'] = 6  # Meters
            
            # Get building dimensions
            length = building_dims.get("length_m", 10.0)
            width = building_dims.get("width_m", 6.0)
            height = building_dims.get("wall_height_m", 6.0)
            
            # Draw building base (rectangle)
            points = [
                (0, 0, 0),
                (length, 0, 0),
                (length, width, 0),
                (0, width, 0),
                (0, 0, 0)
            ]
            msp.add_polyline3d(points, dxfattribs={'layer': 'Building_Base'})
            
            # Draw walls
            wall_points = [
                [(0, 0, 0), (0, 0, height)],
                [(length, 0, 0), (length, 0, height)],
                [(length, width, 0), (length, width, height)],
                [(0, width, 0), (0, width, height)]
            ]
            for wall in wall_points:
                msp.add_line(wall[0], wall[1], dxfattribs={'layer': 'Walls'})
            
            # Draw roof outline
            roof_type = roof_config.get("type", "flat")
            roof_angle = roof_config.get("angle", 15.0)
            
            if roof_type.lower() == "flat":
                # Flat roof - simple rectangle at height
                roof_points = [
                    (0, 0, height),
                    (length, 0, height),
                    (length, width, height),
                    (0, width, height),
                    (0, 0, height)
                ]
                msp.add_polyline3d(roof_points, dxfattribs={'layer': 'Roof'})
            
            elif roof_type.lower() in ["satteldach", "gable"]:
                # Gable roof - ridge in the middle
                ridge_height = height + (width / 2) * np.tan(np.radians(roof_angle))
                ridge_points = [
                    (0, width / 2, ridge_height),
                    (length, width / 2, ridge_height)
                ]
                msp.add_line(ridge_points[0], ridge_points[1], dxfattribs={'layer': 'Roof_Ridge'})
                
                # Roof faces
                face1 = [
                    (0, 0, height),
                    (length, 0, height),
                    (length, width / 2, ridge_height),
                    (0, width / 2, ridge_height),
                    (0, 0, height)
                ]
                face2 = [
                    (0, width, height),
                    (length, width, height),
                    (length, width / 2, ridge_height),
                    (0, width / 2, ridge_height),
                    (0, width, height)
                ]
                msp.add_polyline3d(face1, dxfattribs={'layer': 'Roof_Face1'})
                msp.add_polyline3d(face2, dxfattribs={'layer': 'Roof_Face2'})
            
            # Add PV modules as rectangles
            module_count = module_config.get("count", 20)
            module_width = 1.05  # Standard module width
            module_height = 1.76  # Standard module height
            
            # Simple grid layout for DXF
            cols = int(np.sqrt(module_count * (length / width)))
            rows = int(np.ceil(module_count / cols))
            
            spacing_x = length / (cols + 1)
            spacing_y = width / (rows + 1)
            
            module_idx = 0
            for row in range(rows):
                for col in range(cols):
                    if module_idx >= module_count:
                        break
                    
                    # Calculate module position
                    x = spacing_x * (col + 1)
                    y = spacing_y * (row + 1)
                    z = height + 0.1  # Slightly above roof
                    
                    # Draw module rectangle
                    module_points = [
                        (x - module_width / 2, y - module_height / 2, z),
                        (x + module_width / 2, y - module_height / 2, z),
                        (x + module_width / 2, y + module_height / 2, z),
                        (x - module_width / 2, y + module_height / 2, z),
                        (x - module_width / 2, y - module_height / 2, z)
                    ]
                    msp.add_polyline3d(module_points, dxfattribs={'layer': 'PV_Modules'})
                    
                    module_idx += 1
            
            # Write to bytes
            output = io.BytesIO()
            doc.write(output)
            output.seek(0)
            
            return output.read()
            
        except Exception as e:
            logger.error(f"Error exporting DXF: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # PDF 3D Export
    # ========================================================================
    
    def export_pdf_3d(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model embedded in PDF.
        
        Creates a PDF with a 3D preview image and embedded 3D model data.
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            options: Export options (include_3d_data=True, image_quality='high')
            
        Returns:
            PDF file as bytes
        """
        if not self.is_format_supported("pdf"):
            raise RuntimeError("PDF export not available - reportlab library required")
        
        try:
            options = options or {}
            include_3d_data = options.get('include_3d_data', True)
            image_quality = options.get('image_quality', 'high')
            
            # Create PDF buffer
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Add title
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, height - 50, "3D PV System Model")
            
            # Add project info
            c.setFont("Helvetica", 12)
            y_pos = height - 100
            
            info_lines = [
                f"Building Dimensions: {building_dims.get('length_m', 0):.1f}m × {building_dims.get('width_m', 0):.1f}m",
                f"Wall Height: {building_dims.get('wall_height_m', 0):.1f}m",
                f"Roof Type: {roof_config.get('type', 'Unknown')}",
                f"Roof Angle: {roof_config.get('angle', 0):.1f}°",
                f"Module Count: {module_config.get('count', 0)}",
            ]
            
            for line in info_lines:
                c.drawString(50, y_pos, line)
                y_pos -= 20
            
            # Generate 3D preview image
            try:
                # Create building dimensions
                dims = BuildingDims(
                    length_m=building_dims.get("length_m", 10.0),
                    width_m=building_dims.get("width_m", 6.0),
                    wall_height_m=building_dims.get("wall_height_m", 6.0)
                )
                
                # Create layout config
                layout_config = LayoutConfig(
                    roof_type=roof_config.get("type", "flat"),
                    roof_angle_deg=roof_config.get("angle", 15.0),
                    orientation=roof_config.get("orientation", "south"),
                    module_count=module_config.get("count", 20)
                )
                
                # Generate scene
                fig = build_plotly_scene(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_config.get("type", "flat"),
                    module_quantity=module_config.get("count", 20),
                    layout_config=layout_config,
                    selected_modules=[]
                )
                
                # Export as PNG
                resolution = (1200, 900) if image_quality == 'high' else (800, 600)
                png_bytes = export_screenshot(
                    fig=fig,
                    format="png",
                    width=resolution[0],
                    height=resolution[1],
                    scale=2.0 if image_quality == 'high' else 1.0
                )
                
                # Add image to PDF
                img = Image.open(io.BytesIO(png_bytes))
                img_reader = ImageReader(img)
                
                # Calculate image size to fit on page
                img_width = width - 100
                img_height = (img.height / img.width) * img_width
                
                if img_height > (height - y_pos - 100):
                    img_height = height - y_pos - 100
                    img_width = (img.width / img.height) * img_height
                
                c.drawImage(img_reader, 50, y_pos - img_height - 20, 
                           width=img_width, height=img_height)
                
            except Exception as e:
                logger.warning(f"Could not generate 3D preview: {e}")
                c.drawString(50, y_pos - 40, "3D preview not available")
            
            # Add footer
            c.setFont("Helvetica", 10)
            c.drawString(50, 30, "Generated by Solar Calculator Pro")
            
            # If include_3d_data, add embedded 3D model info
            if include_3d_data:
                try:
                    # Export as GLB for embedding
                    glb_bytes = self.export_gltf(
                        project_data=project_data,
                        building_dims=building_dims,
                        roof_config=roof_config,
                        module_config=module_config,
                        binary=True
                    )
                    
                    # Add note about embedded 3D data
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(50, 50, f"3D model data embedded ({len(glb_bytes)} bytes)")
                    
                except Exception as e:
                    logger.warning(f"Could not embed 3D data: {e}")
            
            # Finalize PDF
            c.save()
            buffer.seek(0)
            
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error exporting PDF 3D: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Image Export (PNG/JPG)
    # ========================================================================
    
    def export_image(
        self,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        format: str = "png",
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model as high-quality image (PNG or JPG).
        
        Args:
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            format: Image format ("png" or "jpg"/"jpeg")
            options: Export options (width, height, scale, quality)
            
        Returns:
            Image file as bytes
        """
        if not self.is_format_supported(format):
            raise RuntimeError(f"{format.upper()} export not available")
        
        try:
            options = options or {}
            width = options.get('width', 1920)
            height = options.get('height', 1080)
            scale = options.get('scale', 2.0)
            quality = options.get('quality', 95)  # For JPEG
            
            # Create building dimensions
            dims = BuildingDims(
                length_m=building_dims.get("length_m", 10.0),
                width_m=building_dims.get("width_m", 6.0),
                wall_height_m=building_dims.get("wall_height_m", 6.0)
            )
            
            # Create layout config
            layout_config = LayoutConfig(
                roof_type=roof_config.get("type", "flat"),
                roof_angle_deg=roof_config.get("angle", 15.0),
                orientation=roof_config.get("orientation", "south"),
                module_count=module_config.get("count", 20)
            )
            
            # Generate scene
            fig = build_plotly_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_config.get("type", "flat"),
                module_quantity=module_config.get("count", 20),
                layout_config=layout_config,
                selected_modules=[]
            )
            
            # Export as image
            img_format = "jpeg" if format.lower() in ["jpg", "jpeg"] else "png"
            img_bytes = export_screenshot(
                fig=fig,
                format=img_format,
                width=width,
                height=height,
                scale=scale
            )
            
            # For JPEG, apply quality setting
            if img_format == "jpeg" and quality < 100:
                img = Image.open(io.BytesIO(img_bytes))
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                return output.read()
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error exporting image: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Universal Export Method
    # ========================================================================
    
    def export(
        self,
        format: str,
        project_data: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Universal export method that routes to the appropriate format handler.
        
        Args:
            format: Export format (stl, obj, gltf, glb, dxf, pdf, png, jpg)
            project_data: Project data dictionary
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            options: Format-specific export options
            
        Returns:
            Exported file as bytes
            
        Raises:
            ValueError: If format is not supported
            RuntimeError: If export fails
        """
        format_lower = format.lower()
        
        if not self.is_format_supported(format_lower):
            raise ValueError(
                f"Format '{format}' is not supported. "
                f"Supported formats: {[k for k, v in self.supported_formats.items() if v]}"
            )
        
        # Route to appropriate export method
        if format_lower == "stl":
            return self.export_stl(project_data, building_dims, roof_config, module_config, options)
        elif format_lower == "obj":
            return self.export_obj(project_data, building_dims, roof_config, module_config, options)
        elif format_lower == "gltf":
            return self.export_gltf(project_data, building_dims, roof_config, module_config, False, options)
        elif format_lower == "glb":
            return self.export_gltf(project_data, building_dims, roof_config, module_config, True, options)
        elif format_lower == "dxf":
            return self.export_dxf(project_data, building_dims, roof_config, module_config, options)
        elif format_lower == "pdf":
            return self.export_pdf_3d(project_data, building_dims, roof_config, module_config, options)
        elif format_lower in ["png", "jpg", "jpeg"]:
            return self.export_image(project_data, building_dims, roof_config, module_config, format_lower, options)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_format_info(self, format: str) -> Dict[str, Any]:
        """
        Get information about a specific export format.
        
        Args:
            format: Format name
            
        Returns:
            Dictionary with format information
        """
        format_info = {
            "stl": {
                "name": "STL (Stereolithography)",
                "description": "Standard format for 3D printing",
                "mime_type": "model/stl",
                "extension": ".stl",
                "use_cases": ["3D printing", "CAD import", "Manufacturing"],
                "binary": True
            },
            "obj": {
                "name": "OBJ (Wavefront)",
                "description": "Universal 3D format",
                "mime_type": "model/obj",
                "extension": ".obj",
                "use_cases": ["3D modeling", "Animation", "Rendering"],
                "binary": False
            },
            "gltf": {
                "name": "glTF (GL Transmission Format)",
                "description": "Web-optimized 3D format (JSON)",
                "mime_type": "model/gltf+json",
                "extension": ".gltf",
                "use_cases": ["Web 3D", "AR/VR", "Real-time rendering"],
                "binary": False
            },
            "glb": {
                "name": "GLB (Binary glTF)",
                "description": "Web-optimized 3D format (Binary)",
                "mime_type": "model/gltf-binary",
                "extension": ".glb",
                "use_cases": ["Web 3D", "AR/VR", "Real-time rendering"],
                "binary": True
            },
            "dxf": {
                "name": "DXF (Drawing Exchange Format)",
                "description": "AutoCAD exchange format",
                "mime_type": "application/dxf",
                "extension": ".dxf",
                "use_cases": ["CAD software", "Architecture", "Engineering"],
                "binary": False
            },
            "pdf": {
                "name": "PDF 3D",
                "description": "PDF with embedded 3D model",
                "mime_type": "application/pdf",
                "extension": ".pdf",
                "use_cases": ["Documentation", "Presentations", "Reports"],
                "binary": True
            },
            "png": {
                "name": "PNG Image",
                "description": "High-quality raster image",
                "mime_type": "image/png",
                "extension": ".png",
                "use_cases": ["Documentation", "Presentations", "Web"],
                "binary": True
            },
            "jpg": {
                "name": "JPEG Image",
                "description": "Compressed raster image",
                "mime_type": "image/jpeg",
                "extension": ".jpg",
                "use_cases": ["Documentation", "Presentations", "Web"],
                "binary": True
            }
        }
        
        format_lower = format.lower()
        if format_lower == "jpeg":
            format_lower = "jpg"
        
        info = format_info.get(format_lower, {})
        info["supported"] = self.is_format_supported(format_lower)
        
        return info
