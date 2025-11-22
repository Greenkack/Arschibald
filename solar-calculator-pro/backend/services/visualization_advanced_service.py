"""
3D Visualization Advanced Service

This service provides advanced 3D visualization capabilities including:
- Complete 3D model generation with realistic rendering
- Collision detection algorithms
- Automatic and manual module placement with constraints
- Roof type detection logic
- Mounting system calculations
- Multi-view export (front, side, top, 360°)
- Animation generation for presentations

Requirements: 1.3, 6.1
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import logging
import numpy as np
from dataclasses import dataclass, asdict

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
    from utils.pv3d_roof_type_logic import (
        detect_roof_type,
        calculate_roof_parameters
    )
    from utils.pv3d_mounting_logic import (
        calculate_mounting_system,
        generate_mounting_bom
    )
    PV3D_AVAILABLE = True
except ImportError as e:
    logging.warning(f"3D visualization modules not available: {e}")
    PV3D_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RoofDetectionResult:
    """Result of roof type detection."""
    roof_type: str
    confidence: float
    angle_deg: float
    orientation: str
    area_m2: float
    usable_area_m2: float
    parameters: Dict[str, Any]


@dataclass
class CollisionResult:
    """Result of collision detection."""
    has_collisions: bool
    collision_count: int
    collisions: List[Dict[str, Any]]
    severity: str  # "none", "warning", "critical"
    recommendations: List[str]


@dataclass
class MountingSystemResult:
    """Result of mounting system calculation."""
    rail_count: int
    clamp_count: int
    total_weight_kg: float
    cost_estimate: float
    bom: List[Dict[str, Any]]
    installation_time_hours: float


@dataclass
class PlacementConstraints:
    """Constraints for module placement."""
    min_spacing_m: float = 0.02
    min_edge_distance_m: float = 0.5
    max_tilt_deg: float = 60.0
    min_tilt_deg: float = 0.0
    avoid_shading: bool = True
    optimize_for: str = "max_modules"  # "max_modules", "max_power", "aesthetics"
    custom_zones: List[Dict[str, Any]] = None


class VisualizationAdvancedService:
    """
    Advanced 3D Visualization Service.
    
    Provides comprehensive 3D visualization capabilities for PV systems including:
    - Complete 3D model generation
    - Collision detection algorithms
    - Automatic module placement with optimization
    - Manual placement with constraint validation
    - Roof type detection
    - Mounting system calculations
    - Multi-view export
    - Animation generation
    """
    
    def __init__(self):
        """Initialize the advanced visualization service."""
        if not PV3D_AVAILABLE:
            logger.warning("3D visualization modules not available")
        self.pv_width = PV_W if PV3D_AVAILABLE else 1.05
        self.pv_height = PV_H if PV3D_AVAILABLE else 1.76
        self.pv_thickness = PV_T if PV3D_AVAILABLE else 0.04
    
    def is_available(self) -> bool:
        """Check if 3D visualization is available."""
        return PV3D_AVAILABLE

    
    # ========================================================================
    # Complete 3D Model Generation
    # ========================================================================
    
    def generate_complete_3d_model(
        self,
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any],
        placement_mode: str = "auto",
        rendering_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete 3D model with all features.
        
        Args:
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration
            placement_mode: "auto" or "manual"
            rendering_options: Rendering options (materials, lighting, etc.)
            
        Returns:
            Complete 3D model with scene data, positions, statistics, and metadata
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            # Detect roof type if not specified
            if "type" not in roof_config or roof_config["type"] == "auto":
                roof_detection = self.detect_roof_type(building_dims, roof_config)
                roof_config.update({
                    "type": roof_detection.roof_type,
                    "angle": roof_detection.angle_deg,
                    "orientation": roof_detection.orientation
                })
            
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
            
            # Create advanced config with rendering options
            rendering_options = rendering_options or {}
            advanced_config = AdvancedLayoutConfig(
                show_mounting=rendering_options.get("show_mounting", True),
                show_labels=rendering_options.get("show_labels", False),
                color_scheme=rendering_options.get("color_scheme", "default"),
                lighting=rendering_options.get("lighting", "realistic")
            )
            
            # Calculate module positions
            if placement_mode == "auto":
                positions = self.calculate_automatic_placement(
                    building_dims=building_dims,
                    roof_config=roof_config,
                    module_config=module_config
                )
            else:
                positions = self.validate_manual_placement(
                    positions=module_config.get("manual_positions", []),
                    building_dims=building_dims,
                    roof_config=roof_config,
                    constraints=module_config.get("constraints", {})
                )
            
            # Detect collisions
            collision_result = self.detect_collisions_advanced(
                module_positions=positions,
                building_dims=building_dims,
                roof_config=roof_config
            )
            
            # Calculate mounting system
            mounting_result = self.calculate_mounting_system(
                module_positions=positions,
                roof_config=roof_config,
                module_config=module_config
            )
            
            # Generate scene
            scene_data = build_plotly_scene(
                dims=dims,
                layout_config=layout_config,
                advanced_config=advanced_config
            )
            
            # Calculate comprehensive statistics
            statistics = self._calculate_comprehensive_statistics(
                positions=positions,
                building_dims=building_dims,
                roof_config=roof_config,
                mounting_result=mounting_result
            )
            
            return {
                "scene_data": scene_data,
                "module_positions": positions,
                "collision_result": asdict(collision_result),
                "mounting_result": asdict(mounting_result),
                "statistics": statistics,
                "metadata": {
                    "placement_mode": placement_mode,
                    "roof_type": roof_config.get("type"),
                    "total_modules": len(positions),
                    "generation_timestamp": self._get_timestamp()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating complete 3D model: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Collision Detection Algorithms
    # ========================================================================
    
    def detect_collisions_advanced(
        self,
        module_positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        tolerance: float = 0.01
    ) -> CollisionResult:
        """
        Advanced collision detection with detailed analysis.
        
        Args:
            module_positions: List of module positions
            building_dims: Building dimensions
            roof_config: Roof configuration
            tolerance: Collision tolerance in meters
            
        Returns:
            CollisionResult with detailed collision information
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            collisions = []
            
            # Module-to-module collision detection
            for i, pos1 in enumerate(module_positions):
                for j, pos2 in enumerate(module_positions[i+1:], start=i+1):
                    if self._check_module_overlap(pos1, pos2, tolerance):
                        collisions.append({
                            "type": "module_overlap",
                            "module1": i,
                            "module2": j,
                            "severity": "critical",
                            "overlap_area_m2": self._calculate_overlap_area(pos1, pos2)
                        })
            
            # Boundary collision detection
            roof_length = building_dims.get("length_m", 10.0)
            roof_width = building_dims.get("width_m", 6.0)
            
            for i, pos in enumerate(module_positions):
                if not self._is_within_boundaries(pos, roof_length, roof_width):
                    collisions.append({
                        "type": "boundary_violation",
                        "module": i,
                        "severity": "critical",
                        "distance_from_edge_m": self._calculate_boundary_distance(
                            pos, roof_length, roof_width
                        )
                    })
            
            # Clearance violation detection
            min_clearance = 0.5  # meters
            for i, pos in enumerate(module_positions):
                clearance = self._calculate_edge_clearance(pos, roof_length, roof_width)
                if clearance < min_clearance:
                    collisions.append({
                        "type": "clearance_violation",
                        "module": i,
                        "severity": "warning",
                        "clearance_m": clearance,
                        "required_clearance_m": min_clearance
                    })
            
            # Determine overall severity
            critical_count = sum(1 for c in collisions if c["severity"] == "critical")
            if critical_count > 0:
                severity = "critical"
            elif len(collisions) > 0:
                severity = "warning"
            else:
                severity = "none"
            
            # Generate recommendations
            recommendations = self._generate_collision_recommendations(collisions)
            
            return CollisionResult(
                has_collisions=len(collisions) > 0,
                collision_count=len(collisions),
                collisions=collisions,
                severity=severity,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error detecting collisions: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Automatic Module Placement
    # ========================================================================
    
    def calculate_automatic_placement(
        self,
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate automatic module placement with optimization.
        
        Args:
            building_dims: Building dimensions
            roof_config: Roof configuration
            module_config: Module configuration with constraints
            
        Returns:
            Optimized list of module positions
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            # Extract constraints
            constraints = PlacementConstraints(
                min_spacing_m=module_config.get("min_spacing", 0.02),
                min_edge_distance_m=module_config.get("min_edge_distance", 0.5),
                avoid_shading=module_config.get("avoid_shading", True),
                optimize_for=module_config.get("optimize_for", "max_modules")
            )
            
            # Calculate initial grid
            grid = calculate_module_grid(
                roof_length=building_dims.get("length_m", 10.0),
                roof_width=building_dims.get("width_m", 6.0),
                module_width=self.pv_width,
                module_height=self.pv_height,
                spacing=constraints.min_spacing_m,
                margin=constraints.min_edge_distance_m
            )
            
            # Optimize placement based on constraints
            optimized = optimize_module_placement(
                grid=grid,
                roof_type=roof_config.get("type", "flat"),
                constraints=asdict(constraints)
            )
            
            # Convert to position list with full 3D coordinates
            positions = []
            for idx, pos in enumerate(optimized):
                z_pos = calculate_z_position(
                    x=pos["x"],
                    y=pos["y"],
                    roof_type=roof_config.get("type", "flat"),
                    roof_angle=roof_config.get("angle", 15.0),
                    wall_height=building_dims.get("wall_height_m", 6.0)
                )
                
                tilt = calculate_tilt_angle(
                    roof_type=roof_config.get("type", "flat"),
                    roof_angle=roof_config.get("angle", 15.0)
                )
                
                positions.append({
                    "index": idx,
                    "x": pos["x"],
                    "y": pos["y"],
                    "z": z_pos,
                    "azimuth": pos.get("azimuth", 0.0),
                    "tilt": tilt,
                    "power_w": module_config.get("module_power_w", 400),
                    "efficiency": module_config.get("module_efficiency", 0.20)
                })
            
            return positions
            
        except Exception as e:
            logger.error(f"Error calculating automatic placement: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Manual Placement with Constraints
    # ========================================================================
    
    def validate_manual_placement(
        self,
        positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Validate and process manual module placement with constraints.
        
        Args:
            positions: Manually specified positions
            building_dims: Building dimensions
            roof_config: Roof configuration
            constraints: Placement constraints
            
        Returns:
            Validated positions with warnings
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            validated_positions = []
            warnings = []
            
            for idx, pos in enumerate(positions):
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
                
                # Validate against constraints
                validation_result = self._validate_position_constraints(
                    pos, building_dims, roof_config, constraints
                )
                
                if validation_result["valid"]:
                    validated_positions.append(pos)
                else:
                    warnings.extend(validation_result["warnings"])
            
            if warnings:
                logger.warning(f"Manual placement validation warnings: {warnings}")
            
            return validated_positions
            
        except Exception as e:
            logger.error(f"Error validating manual placement: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Roof Type Detection
    # ========================================================================
    
    def detect_roof_type(
        self,
        building_dims: Dict[str, float],
        roof_hints: Optional[Dict[str, Any]] = None
    ) -> RoofDetectionResult:
        """
        Detect roof type from building dimensions and hints.
        
        Args:
            building_dims: Building dimensions
            roof_hints: Optional hints (images, measurements, etc.)
            
        Returns:
            RoofDetectionResult with detected type and parameters
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            roof_hints = roof_hints or {}
            
            # Use detection logic from pv3d_roof_type_logic
            detection = detect_roof_type(
                length_m=building_dims.get("length_m", 10.0),
                width_m=building_dims.get("width_m", 6.0),
                wall_height_m=building_dims.get("wall_height_m", 6.0),
                hints=roof_hints
            )
            
            # Calculate roof parameters
            params = calculate_roof_parameters(
                roof_type=detection["type"],
                building_dims=building_dims
            )
            
            return RoofDetectionResult(
                roof_type=detection["type"],
                confidence=detection.get("confidence", 0.8),
                angle_deg=params.get("angle_deg", 15.0),
                orientation=params.get("orientation", "south"),
                area_m2=params.get("total_area_m2", 0.0),
                usable_area_m2=params.get("usable_area_m2", 0.0),
                parameters=params
            )
            
        except Exception as e:
            logger.error(f"Error detecting roof type: {e}", exc_info=True)
            # Return default flat roof
            return RoofDetectionResult(
                roof_type="flat",
                confidence=0.5,
                angle_deg=0.0,
                orientation="south",
                area_m2=building_dims.get("length_m", 10.0) * building_dims.get("width_m", 6.0),
                usable_area_m2=building_dims.get("length_m", 10.0) * building_dims.get("width_m", 6.0) * 0.8,
                parameters={}
            )
    
    # ========================================================================
    # Mounting System Calculations
    # ========================================================================
    
    def calculate_mounting_system(
        self,
        module_positions: List[Dict[str, Any]],
        roof_config: Dict[str, Any],
        module_config: Dict[str, Any]
    ) -> MountingSystemResult:
        """
        Calculate mounting system requirements.
        
        Args:
            module_positions: List of module positions
            roof_config: Roof configuration
            module_config: Module configuration
            
        Returns:
            MountingSystemResult with BOM and cost estimate
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            # Calculate mounting system using pv3d_mounting_logic
            mounting_calc = calculate_mounting_system(
                module_count=len(module_positions),
                roof_type=roof_config.get("type", "flat"),
                roof_angle=roof_config.get("angle", 15.0),
                module_dimensions={
                    "width": self.pv_width,
                    "height": self.pv_height,
                    "weight_kg": module_config.get("module_weight_kg", 20.0)
                }
            )
            
            # Generate BOM
            bom = generate_mounting_bom(mounting_calc)
            
            # Calculate total weight
            total_weight = (
                len(module_positions) * module_config.get("module_weight_kg", 20.0) +
                mounting_calc.get("rail_weight_kg", 0.0) +
                mounting_calc.get("clamp_weight_kg", 0.0)
            )
            
            # Estimate installation time (15 minutes per module + setup)
            installation_time = 2.0 + (len(module_positions) * 0.25)
            
            return MountingSystemResult(
                rail_count=mounting_calc.get("rail_count", 0),
                clamp_count=mounting_calc.get("clamp_count", 0),
                total_weight_kg=round(total_weight, 2),
                cost_estimate=mounting_calc.get("cost_estimate", 0.0),
                bom=bom,
                installation_time_hours=round(installation_time, 1)
            )
            
        except Exception as e:
            logger.error(f"Error calculating mounting system: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Multi-View Export
    # ========================================================================
    
    def export_multi_view(
        self,
        scene_data: Dict[str, Any],
        views: Optional[List[str]] = None,
        format: str = "png",
        resolution: Tuple[int, int] = (1920, 1080)
    ) -> Dict[str, bytes]:
        """
        Export multiple views of the 3D model.
        
        Args:
            scene_data: Plotly scene data
            views: List of view names (default: ["front", "side", "top", "perspective"])
            format: Image format ("png", "jpg", "svg")
            resolution: Image resolution (width, height)
            
        Returns:
            Dictionary mapping view names to image data
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            views = views or ["front", "side", "top", "perspective"]
            
            result = export_multi_view(
                scene_data=scene_data,
                views=views,
                format=format,
                width=resolution[0],
                height=resolution[1]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting multi-view: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Animation Generation
    # ========================================================================
    
    def create_360_animation(
        self,
        scene_data: Dict[str, Any],
        frames: int = 60,
        duration_seconds: float = 6.0,
        format: str = "gif"
    ) -> bytes:
        """
        Create 360-degree rotation animation.
        
        Args:
            scene_data: Plotly scene data
            frames: Number of frames
            duration_seconds: Animation duration
            format: Output format ("gif", "mp4")
            
        Returns:
            Binary animation data
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            animation_data = create_360_animation(
                scene_data=scene_data,
                frames=frames,
                duration=duration_seconds,
                format=format
            )
            
            return animation_data
            
        except Exception as e:
            logger.error(f"Error creating 360 animation: {e}", exc_info=True)
            raise
    
    def create_presentation_animation(
        self,
        scene_data: Dict[str, Any],
        animation_type: str = "assembly",
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Create presentation-quality animation.
        
        Args:
            scene_data: Plotly scene data
            animation_type: Type of animation ("assembly", "flythrough", "exploded")
            options: Animation options
            
        Returns:
            Binary animation data
        """
        if not PV3D_AVAILABLE:
            raise RuntimeError("3D visualization not available")
        
        try:
            options = options or {}
            
            if animation_type == "assembly":
                # Show modules being placed one by one
                return self._create_assembly_animation(scene_data, options)
            elif animation_type == "flythrough":
                # Camera flies around the model
                return self._create_flythrough_animation(scene_data, options)
            elif animation_type == "exploded":
                # Show exploded view of components
                return self._create_exploded_animation(scene_data, options)
            else:
                raise ValueError(f"Unknown animation type: {animation_type}")
                
        except Exception as e:
            logger.error(f"Error creating presentation animation: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _check_module_overlap(
        self,
        pos1: Dict[str, Any],
        pos2: Dict[str, Any],
        tolerance: float
    ) -> bool:
        """Check if two modules overlap."""
        dx = abs(pos1["x"] - pos2["x"])
        dy = abs(pos1["y"] - pos2["y"])
        
        min_distance_x = self.pv_width - tolerance
        min_distance_y = self.pv_height - tolerance
        
        return dx < min_distance_x and dy < min_distance_y
    
    def _calculate_overlap_area(
        self,
        pos1: Dict[str, Any],
        pos2: Dict[str, Any]
    ) -> float:
        """Calculate overlap area between two modules."""
        dx = abs(pos1["x"] - pos2["x"])
        dy = abs(pos1["y"] - pos2["y"])
        
        overlap_x = max(0, self.pv_width - dx)
        overlap_y = max(0, self.pv_height - dy)
        
        return overlap_x * overlap_y
    
    def _is_within_boundaries(
        self,
        pos: Dict[str, Any],
        roof_length: float,
        roof_width: float
    ) -> bool:
        """Check if module is within roof boundaries."""
        half_width = self.pv_width / 2
        half_height = self.pv_height / 2
        
        return (
            pos["x"] - half_width >= 0 and
            pos["x"] + half_width <= roof_length and
            pos["y"] - half_height >= 0 and
            pos["y"] + half_height <= roof_width
        )
    
    def _calculate_boundary_distance(
        self,
        pos: Dict[str, Any],
        roof_length: float,
        roof_width: float
    ) -> float:
        """Calculate distance from module to nearest boundary."""
        half_width = self.pv_width / 2
        half_height = self.pv_height / 2
        
        distances = [
            pos["x"] - half_width,  # Distance to left edge
            roof_length - (pos["x"] + half_width),  # Distance to right edge
            pos["y"] - half_height,  # Distance to front edge
            roof_width - (pos["y"] + half_height)  # Distance to back edge
        ]
        
        return min(distances)
    
    def _calculate_edge_clearance(
        self,
        pos: Dict[str, Any],
        roof_length: float,
        roof_width: float
    ) -> float:
        """Calculate clearance from module to roof edge."""
        return self._calculate_boundary_distance(pos, roof_length, roof_width)
    
    def _validate_position_constraints(
        self,
        pos: Dict[str, Any],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a position against constraints."""
        warnings = []
        
        # Check boundaries
        roof_length = building_dims.get("length_m", 10.0)
        roof_width = building_dims.get("width_m", 6.0)
        
        if not self._is_within_boundaries(pos, roof_length, roof_width):
            warnings.append(f"Module at ({pos['x']:.2f}, {pos['y']:.2f}) exceeds roof boundaries")
        
        # Check clearance
        min_clearance = constraints.get("min_edge_distance_m", 0.5)
        clearance = self._calculate_edge_clearance(pos, roof_length, roof_width)
        if clearance < min_clearance:
            warnings.append(
                f"Module at ({pos['x']:.2f}, {pos['y']:.2f}) has insufficient clearance: "
                f"{clearance:.2f}m < {min_clearance:.2f}m"
            )
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings
        }
    
    def _generate_collision_recommendations(
        self,
        collisions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on collision data."""
        recommendations = []
        
        module_overlaps = [c for c in collisions if c["type"] == "module_overlap"]
        boundary_violations = [c for c in collisions if c["type"] == "boundary_violation"]
        clearance_violations = [c for c in collisions if c["type"] == "clearance_violation"]
        
        if module_overlaps:
            recommendations.append(
                f"Increase spacing between modules to avoid {len(module_overlaps)} overlaps"
            )
        
        if boundary_violations:
            recommendations.append(
                f"Move {len(boundary_violations)} modules away from roof edges"
            )
        
        if clearance_violations:
            recommendations.append(
                f"Increase edge clearance for {len(clearance_violations)} modules"
            )
        
        if not collisions:
            recommendations.append("Module placement is optimal with no collisions")
        
        return recommendations
    
    def _calculate_comprehensive_statistics(
        self,
        positions: List[Dict[str, Any]],
        building_dims: Dict[str, float],
        roof_config: Dict[str, Any],
        mounting_result: MountingSystemResult
    ) -> Dict[str, Any]:
        """Calculate comprehensive statistics."""
        if not positions:
            return {
                "total_modules": 0,
                "total_area_m2": 0.0,
                "total_power_kw": 0.0,
                "roof_coverage_percent": 0.0,
                "average_spacing_m": 0.0,
                "total_weight_kg": 0.0,
                "installation_time_hours": 0.0
            }
        
        total_modules = len(positions)
        module_area = self.pv_width * self.pv_height
        total_area = total_modules * module_area
        
        # Calculate total power
        total_power_w = sum(pos.get("power_w", 400) for pos in positions)
        total_power_kw = total_power_w / 1000.0
        
        # Calculate roof coverage
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
            "total_power_kw": round(total_power_kw, 2),
            "roof_coverage_percent": round(coverage_percent, 2),
            "average_spacing_m": round(average_spacing, 3),
            "total_weight_kg": mounting_result.total_weight_kg,
            "installation_time_hours": mounting_result.installation_time_hours
        }
    
    def _create_assembly_animation(
        self,
        scene_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> bytes:
        """Create assembly animation showing modules being placed."""
        # Implementation would create frames showing progressive module placement
        frames = options.get("frames", 60)
        duration = options.get("duration", 10.0)
        
        # For now, return 360 animation as placeholder
        return create_360_animation(
            scene_data=scene_data,
            frames=frames,
            duration=duration,
            format="gif"
        )
    
    def _create_flythrough_animation(
        self,
        scene_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> bytes:
        """Create flythrough animation with camera movement."""
        # Implementation would create camera path animation
        frames = options.get("frames", 120)
        duration = options.get("duration", 12.0)
        
        # For now, return 360 animation as placeholder
        return create_360_animation(
            scene_data=scene_data,
            frames=frames,
            duration=duration,
            format="gif"
        )
    
    def _create_exploded_animation(
        self,
        scene_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> bytes:
        """Create exploded view animation."""
        # Implementation would create exploded view showing components
        frames = options.get("frames", 90)
        duration = options.get("duration", 9.0)
        
        # For now, return 360 animation as placeholder
        return create_360_animation(
            scene_data=scene_data,
            frames=frames,
            duration=duration,
            format="gif"
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
