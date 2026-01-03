"""
3D Visualization Service

This service wraps the existing pv3d.py and utils/pv3d_*.py modules
to provide 3D visualization functionality through the FastAPI backend.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import logging

# Add parent directory to path to import legacy modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig,
        AdvancedLayoutConfig,
        ModuleTransform,
        ModuleGroup,
        PV_W,
        PV_H,
        PV_T,
        ROOF_COLORS
    )
    from utils.pv3d_plotly import (
        build_plotly_scene,
        create_pv_module_3d,
        export_scene_to_formats
    )
    from utils.pv3d_placement_handler import (
        handle_auto_placement,
        handle_manual_placement,
        calculate_z_position,
        calculate_tilt_angle
    )
    from utils.pv3d_grid_calculator import (
        calculate_module_grid,
        optimize_module_placement
    )
    from utils.pv3d_analysis import (
        detect_collisions,
        calculate_shading_analysis,
        calculate_roof_coverage
    )
    from utils.pv3d_export import (
        export_to_stl,
        export_to_obj,
        export_to_gltf,
        export_multi_view,
        create_360_animation
    )
    PV3D_AVAILABLE = True
except ImportError as e:
    logging.warning(f"3D visualization modules not available: {e}")
    PV3D_AVAILABLE = False
    BuildingDims = None
    LayoutConfig = None
    AdvancedLayoutConfig = None
    ModuleTransform = None
    ModuleGroup = None

logger = logging.getLogger(__name__)


class VisualizationService:
    """
    Service for 3D visualization of PV systems.
    
    This service wraps the existing pv3d.py and related modules to provide:
    - 3D model generation
    - Module placement calculation
    - Collision detection
    - Export to various 3D formats
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        if not PV3D_AVAILABLE:
            logger.warning("3D visualization modules not available")
        self.pv_width = PV_W if PV3D_AVAILABLE else 1.05
        self.pv_height = PV_H if PV3D_AVAILABLE else 1.76
        self.pv_thickness = PV_T if PV3D_AVAILABLE else 0.04
    
    def is_available(self) -> bool:
        """Check if 3D visualization is available."""
        return PV3D_AVAILABLE
    
    # ========================================================================
    # 3D Model Generation
    # ========================================================================
    
    def generate_3d_model(
        self,
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        placement_mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Generate a complete 3D model of the PV system.
        
        Args:
            building_dims: Building dimensions (length_m, width_m, wall_height_m)
            roof_config: Roof configuration (type, angle, orientation, etc.)
            module_config: Module configuration (count, type, dimensions)
            placement_mode: "auto" or "manual" placement
            
        Returns:
            Dictionary containing:
                - scene_data: Plotly scene data
                - module_positions: List of module positions
                - statistics: Placement statistics
                - warnings: Any warnings or issues
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
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
            scene_data = build_plotly_scene(
                dims=dims,
                layout_config=layout_config,
                advanced_config=None
            )
            
            # Calculate module positions
            if placement_mode == "auto":
                positions = self.calculate_auto_placement(
                    building_dims=building_dims,
                    roof_config=roof_config,
                    module_config=module_config
                )
            else:
                positions = module_config.get("manual_positions", [])
            
            # Calculate statistics
            statistics = self._calculate_placement_statistics(
                positions=positions,
                building_dims=building_dims,
                roof_config=roof_config
            )
            
            return {
                "scene_data": scene_data,
                "module_positions": positions,
                "statistics": statistics,
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error generating 3D model: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Module Placement
    # ========================================================================
    
    def calculate_auto_placement(
        self,
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate automatic module placement.
        
        Args:
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            
        Returns:
            List of module positions with coordinates and orientations
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            # Calculate grid
            grid = calculate_module_grid(
                roof_length=building_dims.get("length_m", 10.0),
                roof_width=building_dims.get("width_m", 6.0),
                module_width=self.pv_width,
                module_height=self.pv_height,
                spacing=module_config.get("spacing", 0.02),
                margin=module_config.get("margin", 0.5)
            )
            
            # Optimize placement
            optimized = optimize_module_placement(
                grid=grid,
                roof_type=roof_config.get("type", "flat"),
                constraints=module_config.get("constraints", {})
            )
            
            # Convert to position list
            positions = []
            for idx, pos in enumerate(optimized):
                positions.append({
                    "index": idx,
                    "x": pos["x"],
                    "y": pos["y"],
                    "z": calculate_z_position(
                        x=pos["x"],
                        y=pos["y"],
                        roof_type=roof_config.get("type", "flat"),
                        roof_angle=roof_config.get("angle", 15.0),
                        wall_height=building_dims.get("wall_height_m", 6.0)
                    ),
                    "azimuth": pos.get("azimuth", 0.0),
                    "tilt": calculate_tilt_angle(
                        roof_type=roof_config.get("type", "flat"),
                        roof_angle=roof_config.get("angle", 15.0)
                    )
                })
            
            return positions
            
        except Exception as e:
            logger.error(f"Error calculating auto placement: {e}", exc_info=True)
            raise
    
    def calculate_manual_placement(
        self,
        positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Validate and process manual module placement.
        
        Args:
            positions: List of manually specified positions
            building_dims: Building dimensions
            roof_config: Roof configuration
            
        Returns:
            Validated and processed positions
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            validated_positions = []
            
            for pos in positions:
                # Calculate Z position if not provided
                if "z" not in pos:
                    pos["z"] = calculate_z_position(
                        x=pos["x"],
                        y=pos["y"],
                        roof_type=roof_config.get("type", "flat"),
                        roof_angle=roof_config.get("angle", 15.0),
                        wall_height=building_dims.get("wall_height_m", 6.0)
                    )
                
                # Calculate tilt if not provided
                if "tilt" not in pos:
                    pos["tilt"] = calculate_tilt_angle(
                        roof_type=roof_config.get("type", "flat"),
                        roof_angle=roof_config.get("angle", 15.0)
                    )
                
                validated_positions.append(pos)
            
            return validated_positions
            
        except Exception as e:
            logger.error(f"Error processing manual placement: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Collision Detection
    # ========================================================================
    
    def detect_collisions(
        self,
        module_positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect collisions between modules and with building boundaries.
        
        Args:
            module_positions: List of module positions
            building_dims: Building dimensions
            roof_config: Roof configuration
            
        Returns:
            Dictionary containing:
                - has_collisions: Boolean
                - collisions: List of collision details
                - warnings: List of warnings
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            collisions = detect_collisions(
                positions=module_positions,
                module_width=self.pv_width,
                module_height=self.pv_height,
                building_dims=building_dims,
                roof_config=roof_config
            )
            
            return {
                "has_collisions": len(collisions) > 0,
                "collisions": collisions,
                "warnings": self._generate_collision_warnings(collisions)
            }
            
        except Exception as e:
            logger.error(f"Error detecting collisions: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Export Functions
    # ========================================================================
    
    def export_3d_model(
        self,
        scene_data: Dict[str, Any],
        format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export 3D model to specified format.
        
        Args:
            scene_data: Plotly scene data
            format: Export format ("stl", "obj", "gltf", "glb")
            options: Export options
            
        Returns:
            Binary data of exported model
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            options = options or {}
            
            if format.lower() == "stl":
                return export_to_stl(scene_data, **options)
            elif format.lower() == "obj":
                return export_to_obj(scene_data, **options)
            elif format.lower() in ["gltf", "glb"]:
                return export_to_gltf(scene_data, binary=(format.lower() == "glb"), **options)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting 3D model: {e}", exc_info=True)
            raise
    
    def export_multi_view(
        self,
        scene_data: Dict[str, Any],
        views: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bytes]:
        """
        Export multiple views of the 3D model.
        
        Args:
            scene_data: Plotly scene data
            views: List of view names ("front", "side", "top", "perspective")
            options: Export options
            
        Returns:
            Dictionary mapping view names to image data
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            options = options or {}
            return export_multi_view(scene_data, views=views, **options)
            
        except Exception as e:
            logger.error(f"Error exporting multi-view: {e}", exc_info=True)
            raise
    
    def create_360_animation(
        self,
        scene_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Create 360-degree rotation animation.
        
        Args:
            scene_data: Plotly scene data
            options: Animation options (frames, duration, etc.)
            
        Returns:
            Binary data of animation (GIF or MP4)
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            options = options or {}
            return create_360_animation(scene_data, **options)
            
        except Exception as e:
            logger.error(f"Error creating 360 animation: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_placement_statistics(
        self,
        positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate statistics about module placement."""
        if not positions:
            return {
                "total_modules": 0,
                "total_area_m2": 0.0,
                "roof_coverage_percent": 0.0,
                "average_spacing_m": 0.0
            }
        
        total_modules = len(positions)
        module_area = self.pv_width * self.pv_height
        total_area = total_modules * module_area
        
        # Calculate roof area
        roof_area = building_dims.get("length_m", 10.0) * building_dims.get("width_m", 6.0)
        coverage_percent = (total_area / roof_area) * 100 if roof_area > 0 else 0.0
        
        # Calculate average spacing
        if total_modules > 1:
            spacings = []
            for i in range(len(positions) - 1):
                dx = positions[i+1]["x"] - positions[i]["x"]
                dy = positions[i+1]["y"] - positions[i]["y"]
                spacing = (dx**2 + dy**2)**0.5
                spacings.append(spacing)
            average_spacing = sum(spacings) / len(spacings)
        else:
            average_spacing = 0.0
        
        return {
            "total_modules": total_modules,
            "total_area_m2": round(total_area, 2),
            "roof_coverage_percent": round(coverage_percent, 2),
            "average_spacing_m": round(average_spacing, 3)
        }
    
    def _generate_collision_warnings(self, collisions: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable warnings from collision data."""
        warnings = []
        
        for collision in collisions:
            if collision["type"] == "module_overlap":
                warnings.append(
                    f"Module {collision['module1']} overlaps with module {collision['module2']}"
                )
            elif collision["type"] == "boundary_violation":
                warnings.append(
                    f"Module {collision['module']} exceeds roof boundary"
                )
            elif collision["type"] == "clearance_violation":
                warnings.append(
                    f"Module {collision['module']} violates minimum clearance requirements"
                )
        
        return warnings
