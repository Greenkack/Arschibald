"""
Tests for Advanced 3D Visualization Service

Tests all features of the advanced visualization service.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.visualization_advanced_service import (
    VisualizationAdvancedService,
    RoofDetectionResult,
    CollisionResult,
    MountingSystemResult,
    PlacementConstraints
)


@pytest.fixture
def viz_service():
    """Create visualization service instance."""
    return VisualizationAdvancedService()


@pytest.fixture
def sample_building_dims():
    """Sample building dimensions."""
    return {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }


@pytest.fixture
def sample_roof_config():
    """Sample roof configuration."""
    return {
        "type": "flat",
        "angle": 0.0,
        "orientation": "south"
    }


@pytest.fixture
def sample_module_config():
    """Sample module configuration."""
    return {
        "count": 20,
        "module_power_w": 400,
        "module_weight_kg": 20.0,
        "module_efficiency": 0.20,
        "min_spacing": 0.02,
        "min_edge_distance": 0.5,
        "avoid_shading": True,
        "optimize_for": "max_modules"
    }


class TestVisualizationAdvancedService:
    """Test suite for VisualizationAdvancedService."""
    
    def test_service_initialization(self, viz_service):
        """Test service initializes correctly."""
        assert viz_service is not None
        assert hasattr(viz_service, 'pv_width')
        assert hasattr(viz_service, 'pv_height')
        assert hasattr(viz_service, 'pv_thickness')
    
    def test_is_available(self, viz_service):
        """Test availability check."""
        # Should return boolean
        available = viz_service.is_available()
        assert isinstance(available, bool)
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_generate_complete_3d_model(
        self,
        viz_service,
        sample_building_dims,
        sample_roof_config,
        sample_module_config
    ):
        """Test complete 3D model generation."""
        result = viz_service.generate_complete_3d_model(
            building_dims=sample_building_dims,
            roof_config=sample_roof_config,
            module_config=sample_module_config,
            placement_mode="auto"
        )
        
        # Check result structure
        assert "scene_data" in result
        assert "module_positions" in result
        assert "collision_result" in result
        assert "mounting_result" in result
        assert "statistics" in result
        assert "metadata" in result
        
        # Check statistics
        stats = result["statistics"]
        assert stats["total_modules"] > 0
        assert stats["total_power_kw"] > 0
        assert stats["roof_coverage_percent"] >= 0
        
        # Check collision result
        collision = result["collision_result"]
        assert "has_collisions" in collision
        assert "severity" in collision
        assert "recommendations" in collision
        
        # Check mounting result
        mounting = result["mounting_result"]
        assert "rail_count" in mounting
        assert "clamp_count" in mounting
        assert "total_weight_kg" in mounting
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_detect_roof_type(self, viz_service, sample_building_dims):
        """Test roof type detection."""
        result = viz_service.detect_roof_type(
            building_dims=sample_building_dims,
            roof_hints=None
        )
        
        assert isinstance(result, RoofDetectionResult)
        assert result.roof_type in ["flat", "gable", "hip", "shed"]
        assert 0.0 <= result.confidence <= 1.0
        assert result.angle_deg >= 0
        assert result.area_m2 > 0
        assert result.usable_area_m2 > 0
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_detect_collisions_no_collision(
        self,
        viz_service,
        sample_building_dims,
        sample_roof_config
    ):
        """Test collision detection with no collisions."""
        # Create well-spaced positions
        positions = [
            {"x": 1.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
            {"x": 3.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
            {"x": 5.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
        ]
        
        result = viz_service.detect_collisions_advanced(
            module_positions=positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert isinstance(result, CollisionResult)
        assert result.has_collisions == False
        assert result.collision_count == 0
        assert result.severity == "none"
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_detect_collisions_with_collision(
        self,
        viz_service,
        sample_building_dims,
        sample_roof_config
    ):
        """Test collision detection with collisions."""
        # Create overlapping positions
        positions = [
            {"x": 1.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
            {"x": 1.5, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},  # Overlap!
        ]
        
        result = viz_service.detect_collisions_advanced(
            module_positions=positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert isinstance(result, CollisionResult)
        assert result.has_collisions == True
        assert result.collision_count > 0
        assert result.severity in ["warning", "critical"]
        assert len(result.recommendations) > 0
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_calculate_automatic_placement(
        self,
        viz_service,
        sample_building_dims,
        sample_roof_config,
        sample_module_config
    ):
        """Test automatic module placement."""
        positions = viz_service.calculate_automatic_placement(
            building_dims=sample_building_dims,
            roof_config=sample_roof_config,
            module_config=sample_module_config
        )
        
        assert isinstance(positions, list)
        assert len(positions) > 0
        
        # Check position structure
        for pos in positions:
            assert "x" in pos
            assert "y" in pos
            assert "z" in pos
            assert "azimuth" in pos
            assert "tilt" in pos
            assert "power_w" in pos
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_validate_manual_placement(
        self,
        viz_service,
        sample_building_dims,
        sample_roof_config
    ):
        """Test manual placement validation."""
        positions = [
            {"x": 1.0, "y": 1.0},  # Missing z and tilt
            {"x": 3.0, "y": 1.0},
        ]
        
        validated = viz_service.validate_manual_placement(
            positions=positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config,
            constraints={}
        )
        
        assert isinstance(validated, list)
        assert len(validated) == len(positions)
        
        # Check that z and tilt were calculated
        for pos in validated:
            assert "z" in pos
            assert "tilt" in pos
    
    @pytest.mark.skipif(
        not VisualizationAdvancedService().is_available(),
        reason="3D visualization not available"
    )
    def test_calculate_mounting_system(
        self,
        viz_service,
        sample_roof_config,
        sample_module_config
    ):
        """Test mounting system calculation."""
        positions = [
            {"x": i * 1.1, "y": j * 1.8, "z": 6.0}
            for i in range(4) for j in range(3)
        ]
        
        result = viz_service.calculate_mounting_system(
            module_positions=positions,
            roof_config=sample_roof_config,
            module_config=sample_module_config
        )
        
        assert isinstance(result, MountingSystemResult)
        assert result.rail_count > 0
        assert result.clamp_count > 0
        assert result.total_weight_kg > 0
        assert result.cost_estimate > 0
        assert len(result.bom) > 0
        assert result.installation_time_hours > 0
    
    def test_check_module_overlap(self, viz_service):
        """Test module overlap detection."""
        pos1 = {"x": 1.0, "y": 1.0}
        pos2 = {"x": 1.5, "y": 1.0}  # Should overlap
        pos3 = {"x": 3.0, "y": 1.0}  # Should not overlap
        
        # Test overlap
        overlap1 = viz_service._check_module_overlap(pos1, pos2, 0.01)
        assert overlap1 == True
        
        # Test no overlap
        overlap2 = viz_service._check_module_overlap(pos1, pos3, 0.01)
        assert overlap2 == False
    
    def test_is_within_boundaries(self, viz_service):
        """Test boundary checking."""
        roof_length = 10.0
        roof_width = 6.0
        
        # Position within boundaries
        pos1 = {"x": 5.0, "y": 3.0}
        assert viz_service._is_within_boundaries(pos1, roof_length, roof_width) == True
        
        # Position outside boundaries
        pos2 = {"x": 11.0, "y": 3.0}
        assert viz_service._is_within_boundaries(pos2, roof_length, roof_width) == False
    
    def test_calculate_boundary_distance(self, viz_service):
        """Test boundary distance calculation."""
        roof_length = 10.0
        roof_width = 6.0
        
        # Position in center
        pos = {"x": 5.0, "y": 3.0}
        distance = viz_service._calculate_boundary_distance(pos, roof_length, roof_width)
        assert distance > 0
    
    def test_generate_collision_recommendations(self, viz_service):
        """Test collision recommendation generation."""
        collisions = [
            {"type": "module_overlap", "severity": "critical"},
            {"type": "boundary_violation", "severity": "critical"},
            {"type": "clearance_violation", "severity": "warning"}
        ]
        
        recommendations = viz_service._generate_collision_recommendations(collisions)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_calculate_comprehensive_statistics(self, viz_service):
        """Test statistics calculation."""
        positions = [
            {"x": i * 1.1, "y": j * 1.8, "z": 6.0, "power_w": 400}
            for i in range(4) for j in range(3)
        ]
        
        building_dims = {"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0}
        roof_config = {"type": "flat"}
        mounting_result = MountingSystemResult(
            rail_count=20,
            clamp_count=40,
            total_weight_kg=300.0,
            cost_estimate=800.0,
            bom=[],
            installation_time_hours=5.0
        )
        
        stats = viz_service._calculate_comprehensive_statistics(
            positions=positions,
            building_dims=building_dims,
            roof_config=roof_config,
            mounting_result=mounting_result
        )
        
        assert stats["total_modules"] == len(positions)
        assert stats["total_power_kw"] > 0
        assert stats["roof_coverage_percent"] > 0
        assert stats["total_weight_kg"] == 300.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
