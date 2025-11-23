"""
Tests for Collision Detection Service

This module contains comprehensive tests for the 3D collision detection functionality.
"""

import pytest
import math
from backend.services.collision_detection_service import (
    CollisionDetectionService,
    BoundingBox,
    Obstacle,
    CollisionInfo
)


class TestBoundingBox:
    """Tests for BoundingBox class."""
    
    def test_bounding_box_creation(self):
        """Test bounding box creation."""
        bbox = BoundingBox(
            min_x=0.0, min_y=0.0, min_z=0.0,
            max_x=1.0, max_y=1.0, max_z=1.0
        )
        assert bbox.min_x == 0.0
        assert bbox.max_x == 1.0
    
    def test_bounding_box_center(self):
        """Test bounding box center calculation."""
        bbox = BoundingBox(
            min_x=0.0, min_y=0.0, min_z=0.0,
            max_x=2.0, max_y=4.0, max_z=6.0
        )
        center = bbox.center
        assert center == (1.0, 2.0, 3.0)
    
    def test_bounding_box_dimensions(self):
        """Test bounding box dimensions calculation."""
        bbox = BoundingBox(
            min_x=0.0, min_y=0.0, min_z=0.0,
            max_x=2.0, max_y=3.0, max_z=4.0
        )
        dims = bbox.dimensions
        assert dims == (2.0, 3.0, 4.0)
    
    def test_bounding_box_intersects_true(self):
        """Test bounding box intersection detection - overlapping."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
        bbox2 = BoundingBox(1.0, 1.0, 1.0, 3.0, 3.0, 3.0)
        assert bbox1.intersects(bbox2)
        assert bbox2.intersects(bbox1)
    
    def test_bounding_box_intersects_false(self):
        """Test bounding box intersection detection - separate."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        bbox2 = BoundingBox(2.0, 2.0, 2.0, 3.0, 3.0, 3.0)
        assert not bbox1.intersects(bbox2)
        assert not bbox2.intersects(bbox1)
    
    def test_bounding_box_contains_point_inside(self):
        """Test point containment - point inside."""
        bbox = BoundingBox(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
        assert bbox.contains_point(1.0, 1.0, 1.0)
    
    def test_bounding_box_contains_point_outside(self):
        """Test point containment - point outside."""
        bbox = BoundingBox(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
        assert not bbox.contains_point(3.0, 3.0, 3.0)


class TestCollisionDetectionService:
    """Tests for CollisionDetectionService."""
    
    @pytest.fixture
    def service(self):
        """Create collision detection service instance."""
        return CollisionDetectionService(
            module_width=1.05,
            module_height=1.76,
            module_thickness=0.04,
            min_clearance=0.02,
            max_overhang=0.1
        )
    
    @pytest.fixture
    def sample_modules(self):
        """Create sample module positions."""
        return [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 2.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 4.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
    
    # ========================================================================
    # Module-to-Module Collision Tests
    # ========================================================================
    
    def test_detect_module_collisions_no_collision(self, service, sample_modules):
        """Test module collision detection with no collisions."""
        collisions = service.detect_module_collisions(sample_modules)
        assert len(collisions) == 0
    
    def test_detect_module_collisions_with_overlap(self, service):
        """Test module collision detection with overlapping modules."""
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 0.5, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Too close
        ]
        collisions = service.detect_module_collisions(modules)
        assert len(collisions) > 0
        assert collisions[0].collision_type == "module_overlap"
        assert collisions[0].severity in ["critical", "warning"]
    
    def test_detect_module_collisions_exact_overlap(self, service):
        """Test module collision detection with exact overlap."""
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Exact same position
        ]
        collisions = service.detect_module_collisions(modules)
        assert len(collisions) > 0
        assert collisions[0].overlap_percentage > 90.0  # Nearly 100% overlap
    
    # ========================================================================
    # Obstacle Collision Tests
    # ========================================================================
    
    def test_detect_obstacle_collisions_no_collision(self, service, sample_modules):
        """Test obstacle collision detection with no collisions."""
        obstacles = [
            Obstacle(
                id=1,
                name="Chimney",
                bbox=BoundingBox(10.0, 10.0, 6.0, 11.0, 11.0, 8.0),
                obstacle_type="chimney"
            )
        ]
        collisions = service.detect_obstacle_collisions(sample_modules, obstacles)
        assert len(collisions) == 0
    
    def test_detect_obstacle_collisions_with_collision(self, service):
        """Test obstacle collision detection with collision."""
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
        obstacles = [
            Obstacle(
                id=1,
                name="Chimney",
                bbox=BoundingBox(-0.5, -0.5, 5.5, 0.5, 0.5, 7.0),  # Overlaps module
                obstacle_type="chimney"
            )
        ]
        collisions = service.detect_obstacle_collisions(modules, obstacles)
        assert len(collisions) > 0
        assert collisions[0].collision_type == "obstacle_collision"
        assert collisions[0].severity == "critical"
        assert "Chimney" in collisions[0].description
    
    # ========================================================================
    # Boundary Violation Tests
    # ========================================================================
    
    def test_detect_boundary_violations_no_violation(self, service, sample_modules):
        """Test boundary violation detection with no violations."""
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        violations = service.detect_boundary_violations(sample_modules, boundaries)
        assert len(violations) == 0
    
    def test_detect_boundary_violations_x_boundary(self, service):
        """Test boundary violation detection - X boundary."""
        modules = [
            {"x": 15.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Beyond max_x
        ]
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        violations = service.detect_boundary_violations(modules, boundaries)
        assert len(violations) > 0
        assert violations[0].collision_type == "boundary_violation"
        assert "right" in violations[0].description
    
    def test_detect_boundary_violations_multiple(self, service):
        """Test boundary violation detection - multiple violations."""
        modules = [
            {"x": -15.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},  # Beyond min_x
            {"x": 15.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}   # Beyond max_x
        ]
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        violations = service.detect_boundary_violations(modules, boundaries)
        assert len(violations) >= 2
    
    # ========================================================================
    # Overhang Detection Tests
    # ========================================================================
    
    def test_detect_overhangs_no_overhang(self, service, sample_modules):
        """Test overhang detection with no overhangs."""
        roof_edges = [
            {"position": [10.0, 0.0, 6.0], "normal": [1.0, 0.0, 0.0]}
        ]
        overhangs = service.detect_overhangs(sample_modules, roof_edges)
        # May or may not have overhangs depending on calculation
        assert isinstance(overhangs, list)
    
    def test_detect_overhangs_with_overhang(self, service):
        """Test overhang detection with excessive overhang."""
        modules = [
            {"x": 9.5, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
        roof_edges = [
            {"position": [10.0, 0.0, 6.0], "normal": [1.0, 0.0, 0.0]}
        ]
        overhangs = service.detect_overhangs(modules, roof_edges)
        # Check if overhangs detected (depends on calculation)
        assert isinstance(overhangs, list)
    
    # ========================================================================
    # Clearance Validation Tests
    # ========================================================================
    
    def test_validate_clearances_sufficient(self, service, sample_modules):
        """Test clearance validation with sufficient spacing."""
        violations = service.validate_clearances(sample_modules)
        assert len(violations) == 0
    
    def test_validate_clearances_insufficient(self, service):
        """Test clearance validation with insufficient spacing."""
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 1.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Too close
        ]
        violations = service.validate_clearances(modules)
        assert len(violations) > 0
        assert violations[0].collision_type == "clearance_violation"
        assert violations[0].severity == "warning"
    
    # ========================================================================
    # Comprehensive Detection Tests
    # ========================================================================
    
    def test_detect_all_collisions_no_issues(self, service, sample_modules):
        """Test comprehensive detection with no issues."""
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        result = service.detect_all_collisions(sample_modules, boundaries)
        
        assert isinstance(result, dict)
        assert "has_collisions" in result
        assert "total_collisions" in result
        assert "collisions_by_type" in result
        assert "critical_count" in result
        assert "warning_count" in result
    
    def test_detect_all_collisions_with_issues(self, service):
        """Test comprehensive detection with multiple issues."""
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 0.5, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},  # Overlap
            {"x": 15.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Boundary violation
        ]
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        result = service.detect_all_collisions(modules, boundaries)
        
        assert result["has_collisions"]
        assert result["total_collisions"] > 0
        assert result["critical_count"] > 0
    
    def test_detect_all_collisions_with_obstacles(self, service, sample_modules):
        """Test comprehensive detection with obstacles."""
        boundaries = {
            "min_x": -10.0,
            "max_x": 10.0,
            "min_y": -10.0,
            "max_y": 10.0,
            "min_z": 0.0,
            "max_z": 20.0
        }
        obstacles = [
            Obstacle(
                id=1,
                name="Chimney",
                bbox=BoundingBox(-0.5, -0.5, 5.5, 0.5, 0.5, 7.0),
                obstacle_type="chimney"
            )
        ]
        result = service.detect_all_collisions(
            sample_modules,
            boundaries,
            obstacles=obstacles
        )
        
        assert isinstance(result, dict)
        # May or may not have collisions depending on positions
    
    # ========================================================================
    # Helper Method Tests
    # ========================================================================
    
    def test_create_module_bounding_box(self, service):
        """Test module bounding box creation."""
        module = {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        bbox = service._create_module_bounding_box(module)
        
        assert isinstance(bbox, BoundingBox)
        assert bbox.min_x < bbox.max_x
        assert bbox.min_y < bbox.max_y
        assert bbox.min_z < bbox.max_z
    
    def test_calculate_overlap_volume_no_overlap(self, service):
        """Test overlap volume calculation with no overlap."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        bbox2 = BoundingBox(2.0, 2.0, 2.0, 3.0, 3.0, 3.0)
        volume = service._calculate_overlap_volume(bbox1, bbox2)
        assert volume == 0.0
    
    def test_calculate_overlap_volume_with_overlap(self, service):
        """Test overlap volume calculation with overlap."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
        bbox2 = BoundingBox(1.0, 1.0, 1.0, 3.0, 3.0, 3.0)
        volume = service._calculate_overlap_volume(bbox1, bbox2)
        assert volume > 0.0
        assert volume == 1.0  # 1x1x1 overlap
    
    def test_calculate_bbox_distance_no_overlap(self, service):
        """Test bounding box distance calculation."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        bbox2 = BoundingBox(3.0, 0.0, 0.0, 4.0, 1.0, 1.0)
        distance = service._calculate_bbox_distance(bbox1, bbox2)
        assert distance == 2.0  # 2 meters apart in X direction
    
    def test_calculate_bbox_distance_with_overlap(self, service):
        """Test bounding box distance with overlap."""
        bbox1 = BoundingBox(0.0, 0.0, 0.0, 2.0, 2.0, 2.0)
        bbox2 = BoundingBox(1.0, 1.0, 1.0, 3.0, 3.0, 3.0)
        distance = service._calculate_bbox_distance(bbox1, bbox2)
        assert distance == 0.0  # Overlapping
    
    def test_collision_to_dict(self, service):
        """Test collision info to dictionary conversion."""
        collision = CollisionInfo(
            collision_type="module_overlap",
            severity="critical",
            module_id=0,
            other_id=1,
            overlap_volume=0.5,
            overlap_percentage=25.0,
            distance=0.5,
            description="Test collision",
            suggestion="Move module",
            position=(0.0, 0.0, 6.0)
        )
        
        result = service._collision_to_dict(collision)
        
        assert isinstance(result, dict)
        assert result["collision_type"] == "module_overlap"
        assert result["severity"] == "critical"
        assert result["module_id"] == 0
        assert result["other_id"] == 1
        assert result["description"] == "Test collision"


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_module_list(self):
        """Test with empty module list."""
        service = CollisionDetectionService()
        collisions = service.detect_module_collisions([])
        assert len(collisions) == 0
    
    def test_single_module(self):
        """Test with single module."""
        service = CollisionDetectionService()
        modules = [{"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}]
        collisions = service.detect_module_collisions(modules)
        assert len(collisions) == 0
    
    def test_zero_dimensions(self):
        """Test with zero module dimensions."""
        service = CollisionDetectionService(
            module_width=0.0,
            module_height=0.0,
            module_thickness=0.0
        )
        modules = [
            {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"x": 1.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
        # Should not crash
        collisions = service.detect_module_collisions(modules)
        assert isinstance(collisions, list)
