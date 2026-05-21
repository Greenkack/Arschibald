"""
3D Collision Detection Service

This service provides comprehensive collision detection for 3D PV module placement:
- Module-to-module collision detection
- Module-to-obstacle collision detection
- Boundary detection and validation
- Overhang detection
- Clearance validation
- Collision resolution suggestions
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """3D Bounding box representation."""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    
    @property
    def center(self) -> Tuple[float, float, float]:
        """Get center point of bounding box."""
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )
    
    @property
    def dimensions(self) -> Tuple[float, float, float]:
        """Get dimensions (width, depth, height)."""
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z
        )
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box intersects with another."""
        return (
            self.min_x <= other.max_x and self.max_x >= other.min_x and
            self.min_y <= other.max_y and self.max_y >= other.min_y and
            self.min_z <= other.max_z and self.max_z >= other.min_z
        )
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """Check if a point is inside this bounding box."""
        return (
            self.min_x <= x <= self.max_x and
            self.min_y <= y <= self.max_y and
            self.min_z <= z <= self.max_z
        )


@dataclass
class CollisionInfo:
    """Information about a detected collision."""
    collision_type: str  # "module_overlap", "obstacle_collision", "boundary_violation", "overhang", "clearance_violation"
    severity: str  # "critical", "warning", "info"
    module_id: int
    other_id: Optional[int] = None  # For module-to-module or module-to-obstacle
    overlap_volume: float = 0.0
    overlap_percentage: float = 0.0
    distance: float = 0.0
    description: str = ""
    suggestion: str = ""
    position: Optional[Tuple[float, float, float]] = None


@dataclass
class Obstacle:
    """Representation of an obstacle in the scene."""
    id: int
    name: str
    bbox: BoundingBox
    obstacle_type: str  # "chimney", "skylight", "vent", "antenna", "tree", "building", "custom"


class CollisionDetectionService:
    """
    Service for detecting and resolving collisions in 3D PV module placement.
    
    This service provides:
    - Module-to-module collision detection
    - Module-to-obstacle collision detection
    - Boundary detection
    - Overhang detection
    - Clearance validation
    - Collision resolution suggestions
    """
    
    def __init__(
        self,
        module_width: float = 1.05,
        module_height: float = 1.76,
        module_thickness: float = 0.04,
        min_clearance: float = 0.02,
        max_overhang: float = 0.1
    ):
        """
        Initialize collision detection service.
        
        Args:
            module_width: Width of PV module in meters
            module_height: Height of PV module in meters
            module_thickness: Thickness of PV module in meters
            min_clearance: Minimum clearance between modules in meters
            max_overhang: Maximum allowed overhang beyond roof edge in meters
        """
        self.module_width = module_width
        self.module_height = module_height
        self.module_thickness = module_thickness
        self.min_clearance = min_clearance
        self.max_overhang = max_overhang
    
    # ========================================================================
    # Module-to-Module Collision Detection
    # ========================================================================
    
    def detect_module_collisions(
        self,
        module_positions: List[Dict[str, Any]]
    ) -> List[CollisionInfo]:
        """
        Detect collisions between modules.
        
        Args:
            module_positions: List of module positions with x, y, z, azimuth, tilt
            
        Returns:
            List of collision information objects
        """
        collisions = []
        
        # Create bounding boxes for all modules
        bounding_boxes = []
        for i, module in enumerate(module_positions):
            bbox = self._create_module_bounding_box(module)
            bounding_boxes.append((i, bbox))
        
        # Check all pairs for collisions
        for i in range(len(bounding_boxes)):
            for j in range(i + 1, len(bounding_boxes)):
                idx1, bbox1 = bounding_boxes[i]
                idx2, bbox2 = bounding_boxes[j]
                
                if bbox1.intersects(bbox2):
                    # Calculate overlap details
                    overlap_volume = self._calculate_overlap_volume(bbox1, bbox2)
                    module_volume = (
                        self.module_width * self.module_height * self.module_thickness
                    )
                    overlap_percentage = (overlap_volume / module_volume) * 100
                    
                    # Calculate distance between centers
                    center1 = bbox1.center
                    center2 = bbox2.center
                    distance = math.sqrt(
                        (center2[0] - center1[0])**2 +
                        (center2[1] - center1[1])**2 +
                        (center2[2] - center1[2])**2
                    )
                    
                    collision = CollisionInfo(
                        collision_type="module_overlap",
                        severity="critical" if overlap_percentage > 10 else "warning",
                        module_id=idx1,
                        other_id=idx2,
                        overlap_volume=overlap_volume,
                        overlap_percentage=overlap_percentage,
                        distance=distance,
                        description=f"Module {idx1} overlaps with module {idx2} by {overlap_percentage:.1f}%",
                        suggestion=self._suggest_module_collision_resolution(
                            module_positions[idx1],
                            module_positions[idx2],
                            distance
                        ),
                        position=center1
                    )
                    collisions.append(collision)
        
        return collisions
    
    # ========================================================================
    # Module-to-Obstacle Collision Detection
    # ========================================================================
    
    def detect_obstacle_collisions(
        self,
        module_positions: List[Dict[str, Any]],
        obstacles: List[Obstacle]
    ) -> List[CollisionInfo]:
        """
        Detect collisions between modules and obstacles.
        
        Args:
            module_positions: List of module positions
            obstacles: List of obstacles in the scene
            
        Returns:
            List of collision information objects
        """
        collisions = []
        
        for i, module in enumerate(module_positions):
            module_bbox = self._create_module_bounding_box(module)
            
            for obstacle in obstacles:
                if module_bbox.intersects(obstacle.bbox):
                    overlap_volume = self._calculate_overlap_volume(
                        module_bbox,
                        obstacle.bbox
                    )
                    module_volume = (
                        self.module_width * self.module_height * self.module_thickness
                    )
                    overlap_percentage = (overlap_volume / module_volume) * 100
                    
                    collision = CollisionInfo(
                        collision_type="obstacle_collision",
                        severity="critical",
                        module_id=i,
                        other_id=obstacle.id,
                        overlap_volume=overlap_volume,
                        overlap_percentage=overlap_percentage,
                        description=f"Module {i} collides with {obstacle.name} ({obstacle.obstacle_type})",
                        suggestion=f"Move module {i} at least {self.min_clearance + 0.1:.2f}m away from {obstacle.name}",
                        position=module_bbox.center
                    )
                    collisions.append(collision)
        
        return collisions
    
    # ========================================================================
    # Boundary Detection
    # ========================================================================
    
    def detect_boundary_violations(
        self,
        module_positions: List[Dict[str, Any]],
        roof_boundaries: Dict[str, float]
    ) -> List[CollisionInfo]:
        """
        Detect modules that exceed roof boundaries.
        
        Args:
            module_positions: List of module positions
            roof_boundaries: Dictionary with min_x, max_x, min_y, max_y, min_z, max_z
            
        Returns:
            List of collision information objects
        """
        collisions = []
        
        boundary_bbox = BoundingBox(
            min_x=roof_boundaries.get("min_x", -100),
            min_y=roof_boundaries.get("min_y", -100),
            min_z=roof_boundaries.get("min_z", 0),
            max_x=roof_boundaries.get("max_x", 100),
            max_y=roof_boundaries.get("max_y", 100),
            max_z=roof_boundaries.get("max_z", 100)
        )
        
        for i, module in enumerate(module_positions):
            module_bbox = self._create_module_bounding_box(module)
            
            # Check each boundary
            violations = []
            if module_bbox.min_x < boundary_bbox.min_x:
                violations.append(("left", boundary_bbox.min_x - module_bbox.min_x))
            if module_bbox.max_x > boundary_bbox.max_x:
                violations.append(("right", module_bbox.max_x - boundary_bbox.max_x))
            if module_bbox.min_y < boundary_bbox.min_y:
                violations.append(("front", boundary_bbox.min_y - module_bbox.min_y))
            if module_bbox.max_y > boundary_bbox.max_y:
                violations.append(("back", module_bbox.max_y - boundary_bbox.max_y))
            if module_bbox.min_z < boundary_bbox.min_z:
                violations.append(("bottom", boundary_bbox.min_z - module_bbox.min_z))
            if module_bbox.max_z > boundary_bbox.max_z:
                violations.append(("top", module_bbox.max_z - boundary_bbox.max_z))
            
            for direction, distance in violations:
                collision = CollisionInfo(
                    collision_type="boundary_violation",
                    severity="critical",
                    module_id=i,
                    distance=abs(distance),
                    description=f"Module {i} exceeds {direction} boundary by {abs(distance):.2f}m",
                    suggestion=self._suggest_boundary_resolution(module, direction, distance),
                    position=module_bbox.center
                )
                collisions.append(collision)
        
        return collisions
    
    # ========================================================================
    # Overhang Detection
    # ========================================================================
    
    def detect_overhangs(
        self,
        module_positions: List[Dict[str, Any]],
        roof_edges: List[Dict[str, Any]]
    ) -> List[CollisionInfo]:
        """
        Detect modules with excessive overhang beyond roof edges.
        
        Args:
            module_positions: List of module positions
            roof_edges: List of roof edge definitions with position and normal
            
        Returns:
            List of collision information objects
        """
        collisions = []
        
        for i, module in enumerate(module_positions):
            module_bbox = self._create_module_bounding_box(module)
            
            for edge in roof_edges:
                overhang_distance = self._calculate_overhang_distance(
                    module_bbox,
                    edge
                )
                
                if overhang_distance > self.max_overhang:
                    collision = CollisionInfo(
                        collision_type="overhang",
                        severity="warning" if overhang_distance < self.max_overhang * 1.5 else "critical",
                        module_id=i,
                        distance=overhang_distance,
                        description=f"Module {i} overhangs roof edge by {overhang_distance:.2f}m (max: {self.max_overhang:.2f}m)",
                        suggestion=f"Move module {i} inward by at least {overhang_distance - self.max_overhang:.2f}m",
                        position=module_bbox.center
                    )
                    collisions.append(collision)
        
        return collisions
    
    # ========================================================================
    # Clearance Validation
    # ========================================================================
    
    def validate_clearances(
        self,
        module_positions: List[Dict[str, Any]]
    ) -> List[CollisionInfo]:
        """
        Validate minimum clearance between modules.
        
        Args:
            module_positions: List of module positions
            
        Returns:
            List of collision information objects
        """
        collisions = []
        
        for i in range(len(module_positions)):
            for j in range(i + 1, len(module_positions)):
                module1 = module_positions[i]
                module2 = module_positions[j]
                
                bbox1 = self._create_module_bounding_box(module1)
                bbox2 = self._create_module_bounding_box(module2)
                
                # Calculate minimum distance between bounding boxes
                distance = self._calculate_bbox_distance(bbox1, bbox2)
                
                if distance < self.min_clearance:
                    collision = CollisionInfo(
                        collision_type="clearance_violation",
                        severity="warning",
                        module_id=i,
                        other_id=j,
                        distance=distance,
                        description=f"Clearance between module {i} and {j} is {distance:.3f}m (min: {self.min_clearance:.3f}m)",
                        suggestion=f"Increase spacing by {self.min_clearance - distance:.3f}m",
                        position=bbox1.center
                    )
                    collisions.append(collision)
        
        return collisions
    
    # ========================================================================
    # Comprehensive Collision Detection
    # ========================================================================
    
    def detect_all_collisions(
        self,
        module_positions: List[Dict[str, Any]],
        roof_boundaries: Dict[str, float],
        obstacles: Optional[List[Obstacle]] = None,
        roof_edges: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive collision detection.
        
        Args:
            module_positions: List of module positions
            roof_boundaries: Roof boundary definitions
            obstacles: Optional list of obstacles
            roof_edges: Optional list of roof edges
            
        Returns:
            Dictionary containing:
                - has_collisions: Boolean
                - total_collisions: Total number of collisions
                - collisions_by_type: Dictionary of collisions grouped by type
                - critical_count: Number of critical collisions
                - warning_count: Number of warnings
                - all_collisions: List of all collision objects
        """
        all_collisions = []
        
        # Module-to-module collisions
        module_collisions = self.detect_module_collisions(module_positions)
        all_collisions.extend(module_collisions)
        
        # Boundary violations
        boundary_violations = self.detect_boundary_violations(
            module_positions,
            roof_boundaries
        )
        all_collisions.extend(boundary_violations)
        
        # Clearance violations
        clearance_violations = self.validate_clearances(module_positions)
        all_collisions.extend(clearance_violations)
        
        # Obstacle collisions (if obstacles provided)
        if obstacles:
            obstacle_collisions = self.detect_obstacle_collisions(
                module_positions,
                obstacles
            )
            all_collisions.extend(obstacle_collisions)
        
        # Overhang detection (if roof edges provided)
        if roof_edges:
            overhangs = self.detect_overhangs(module_positions, roof_edges)
            all_collisions.extend(overhangs)
        
        # Group collisions by type
        collisions_by_type = {}
        for collision in all_collisions:
            if collision.collision_type not in collisions_by_type:
                collisions_by_type[collision.collision_type] = []
            collisions_by_type[collision.collision_type].append(collision)
        
        # Count by severity
        critical_count = sum(1 for c in all_collisions if c.severity == "critical")
        warning_count = sum(1 for c in all_collisions if c.severity == "warning")
        
        return {
            "has_collisions": len(all_collisions) > 0,
            "total_collisions": len(all_collisions),
            "collisions_by_type": {
                k: [self._collision_to_dict(c) for c in v]
                for k, v in collisions_by_type.items()
            },
            "critical_count": critical_count,
            "warning_count": warning_count,
            "all_collisions": [self._collision_to_dict(c) for c in all_collisions]
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _create_module_bounding_box(self, module: Dict[str, Any]) -> BoundingBox:
        """Create bounding box for a module based on its position and orientation."""
        x = module.get("x", 0.0)
        y = module.get("y", 0.0)
        z = module.get("z", 0.0)
        azimuth = module.get("azimuth", 0.0)
        tilt = module.get("tilt", 0.0)
        
        # For simplicity, create axis-aligned bounding box
        # In production, this should account for rotation
        half_width = self.module_width / 2
        half_height = self.module_height / 2
        half_thickness = self.module_thickness / 2
        
        # Account for tilt (simplified)
        tilt_rad = math.radians(tilt)
        z_offset = half_height * math.sin(tilt_rad)
        y_offset = half_height * math.cos(tilt_rad)
        
        return BoundingBox(
            min_x=x - half_width,
            min_y=y - y_offset,
            min_z=z - half_thickness,
            max_x=x + half_width,
            max_y=y + y_offset,
            max_z=z + z_offset + half_thickness
        )
    
    def _calculate_overlap_volume(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox
    ) -> float:
        """Calculate the volume of overlap between two bounding boxes."""
        if not bbox1.intersects(bbox2):
            return 0.0
        
        overlap_x = min(bbox1.max_x, bbox2.max_x) - max(bbox1.min_x, bbox2.min_x)
        overlap_y = min(bbox1.max_y, bbox2.max_y) - max(bbox1.min_y, bbox2.min_y)
        overlap_z = min(bbox1.max_z, bbox2.max_z) - max(bbox1.min_z, bbox2.min_z)
        
        return max(0.0, overlap_x * overlap_y * overlap_z)
    
    def _calculate_bbox_distance(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox
    ) -> float:
        """Calculate minimum distance between two bounding boxes."""
        if bbox1.intersects(bbox2):
            return 0.0
        
        # Calculate distance in each dimension
        dx = max(0, max(bbox1.min_x - bbox2.max_x, bbox2.min_x - bbox1.max_x))
        dy = max(0, max(bbox1.min_y - bbox2.max_y, bbox2.min_y - bbox1.max_y))
        dz = max(0, max(bbox1.min_z - bbox2.max_z, bbox2.min_z - bbox1.max_z))
        
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def _calculate_overhang_distance(
        self,
        module_bbox: BoundingBox,
        roof_edge: Dict[str, Any]
    ) -> float:
        """Calculate overhang distance from roof edge."""
        # Simplified calculation - assumes edge is a plane
        edge_position = roof_edge.get("position", [0, 0, 0])
        edge_normal = roof_edge.get("normal", [0, 1, 0])
        
        # Calculate distance from module center to edge plane
        center = module_bbox.center
        distance = abs(
            (center[0] - edge_position[0]) * edge_normal[0] +
            (center[1] - edge_position[1]) * edge_normal[1] +
            (center[2] - edge_position[2]) * edge_normal[2]
        )
        
        # Subtract half module dimension in edge direction
        module_extent = self.module_height / 2
        overhang = max(0, distance - module_extent)
        
        return overhang
    
    def _suggest_module_collision_resolution(
        self,
        module1: Dict[str, Any],
        module2: Dict[str, Any],
        distance: float
    ) -> str:
        """Generate suggestion for resolving module-to-module collision."""
        # Calculate direction vector
        dx = module2["x"] - module1["x"]
        dy = module2["y"] - module1["y"]
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            direction = "horizontally" if dx > 0 else "horizontally (opposite)"
            move_distance = self.module_width + self.min_clearance
        else:
            direction = "vertically" if dy > 0 else "vertically (opposite)"
            move_distance = self.module_height + self.min_clearance
        
        return f"Move one module {direction} by at least {move_distance:.2f}m"
    
    def _suggest_boundary_resolution(
        self,
        module: Dict[str, Any],
        direction: str,
        distance: float
    ) -> str:
        """Generate suggestion for resolving boundary violation."""
        move_map = {
            "left": ("right", "x", abs(distance) + self.min_clearance),
            "right": ("left", "x", abs(distance) + self.min_clearance),
            "front": ("back", "y", abs(distance) + self.min_clearance),
            "back": ("forward", "y", abs(distance) + self.min_clearance),
            "bottom": ("up", "z", abs(distance) + self.min_clearance),
            "top": ("down", "z", abs(distance) + self.min_clearance)
        }
        
        move_direction, axis, move_distance = move_map.get(
            direction,
            ("inward", "xy", abs(distance) + self.min_clearance)
        )
        
        return f"Move module {move_direction} by {move_distance:.2f}m"
    
    def _collision_to_dict(self, collision: CollisionInfo) -> Dict[str, Any]:
        """Convert CollisionInfo to dictionary."""
        return {
            "collision_type": collision.collision_type,
            "severity": collision.severity,
            "module_id": collision.module_id,
            "other_id": collision.other_id,
            "overlap_volume": collision.overlap_volume,
            "overlap_percentage": collision.overlap_percentage,
            "distance": collision.distance,
            "description": collision.description,
            "suggestion": collision.suggestion,
            "position": collision.position
        }
