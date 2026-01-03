"""
Tests for 3D Visualization Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.visualization_service import VisualizationService


@pytest.fixture
def visualization_service():
    """Create a visualization service instance."""
    return VisualizationService()


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
        "type": "gable",
        "angle": 30.0,
        "orientation": "south",
        "covering": "Ziegel"
    }


@pytest.fixture
def sample_module_config():
    """Sample module configuration."""
    return {
        "count": 20,
        "type": "standard",
        "spacing": 0.02,
        "margin": 0.5
    }


class TestVisualizationService:
    """Test suite for VisualizationService."""
    
    def test_service_initialization(self, visualization_service):
        """Test service initializes correctly."""
        assert visualization_service is not None
        assert hasattr(visualization_service, 'pv_width')
        assert hasattr(visualization_service, 'pv_height')
        assert hasattr(visualization_service, 'pv_thickness')
    
    def test_is_available(self, visualization_service):
        """Test availability check."""
        available = visualization_service.is_available()
        assert isinstance(available, bool)

    
    def test_calculate_placement_statistics_empty(self, visualization_service, sample_building_dims, sample_roof_config):
        """Test statistics calculation with no modules."""
        stats = visualization_service._calculate_placement_statistics(
            positions=[],
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert stats["total_modules"] == 0
        assert stats["total_area_m2"] == 0.0
        assert stats["roof_coverage_percent"] == 0.0
        assert stats["average_spacing_m"] == 0.0
    
    def test_calculate_placement_statistics_single_module(self, visualization_service, sample_building_dims, sample_roof_config):
        """Test statistics calculation with single module."""
        positions = [
            {"index": 0, "x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
        
        stats = visualization_service._calculate_placement_statistics(
            positions=positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert stats["total_modules"] == 1
        assert stats["total_area_m2"] > 0
        assert stats["roof_coverage_percent"] > 0
        assert stats["average_spacing_m"] == 0.0  # Only one module
    
    def test_calculate_placement_statistics_multiple_modules(self, visualization_service, sample_building_dims, sample_roof_config):
        """Test statistics calculation with multiple modules."""
        positions = [
            {"index": 0, "x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"index": 1, "x": 1.1, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
            {"index": 2, "x": 2.2, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        ]
        
        stats = visualization_service._calculate_placement_statistics(
            positions=positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert stats["total_modules"] == 3
        assert stats["total_area_m2"] > 0
        assert stats["roof_coverage_percent"] > 0
        assert stats["average_spacing_m"] > 0
    
    def test_generate_collision_warnings_empty(self, visualization_service):
        """Test warning generation with no collisions."""
        warnings = visualization_service._generate_collision_warnings([])
        assert warnings == []
    
    def test_generate_collision_warnings_module_overlap(self, visualization_service):
        """Test warning generation for module overlap."""
        collisions = [
            {"type": "module_overlap", "module1": 0, "module2": 1}
        ]
        
        warnings = visualization_service._generate_collision_warnings(collisions)
        assert len(warnings) == 1
        assert "Module 0 overlaps with module 1" in warnings[0]
    
    def test_generate_collision_warnings_boundary_violation(self, visualization_service):
        """Test warning generation for boundary violation."""
        collisions = [
            {"type": "boundary_violation", "module": 5}
        ]
        
        warnings = visualization_service._generate_collision_warnings(collisions)
        assert len(warnings) == 1
        assert "Module 5 exceeds roof boundary" in warnings[0]
    
    def test_generate_collision_warnings_clearance_violation(self, visualization_service):
        """Test warning generation for clearance violation."""
        collisions = [
            {"type": "clearance_violation", "module": 3}
        ]
        
        warnings = visualization_service._generate_collision_warnings(collisions)
        assert len(warnings) == 1
        assert "Module 3 violates minimum clearance" in warnings[0]
    
    def test_generate_collision_warnings_multiple(self, visualization_service):
        """Test warning generation for multiple collisions."""
        collisions = [
            {"type": "module_overlap", "module1": 0, "module2": 1},
            {"type": "boundary_violation", "module": 5},
            {"type": "clearance_violation", "module": 3}
        ]
        
        warnings = visualization_service._generate_collision_warnings(collisions)
        assert len(warnings) == 3


@pytest.mark.skipif(
    not VisualizationService().is_available(),
    reason="3D visualization modules not available"
)
class TestVisualizationServiceIntegration:
    """Integration tests for VisualizationService (requires pv3d modules)."""
    
    def test_generate_3d_model(self, visualization_service, sample_building_dims, sample_roof_config, sample_module_config):
        """Test 3D model generation."""
        result = visualization_service.generate_3d_model(
            building_dims=sample_building_dims,
            roof_config=sample_roof_config,
            module_config=sample_module_config,
            placement_mode="auto"
        )
        
        assert "scene_data" in result
        assert "module_positions" in result
        assert "statistics" in result
        assert "warnings" in result
        assert isinstance(result["module_positions"], list)
        assert isinstance(result["statistics"], dict)
    
    def test_calculate_auto_placement(self, visualization_service, sample_building_dims, sample_roof_config, sample_module_config):
        """Test automatic placement calculation."""
        positions = visualization_service.calculate_auto_placement(
            building_dims=sample_building_dims,
            roof_config=sample_roof_config,
            module_config=sample_module_config
        )
        
        assert isinstance(positions, list)
        assert len(positions) > 0
        
        # Check position structure
        for pos in positions:
            assert "index" in pos
            assert "x" in pos
            assert "y" in pos
            assert "z" in pos
            assert "azimuth" in pos
            assert "tilt" in pos
    
    def test_calculate_manual_placement(self, visualization_service, sample_building_dims, sample_roof_config):
        """Test manual placement validation."""
        manual_positions = [
            {"index": 0, "x": 1.0, "y": 1.0, "azimuth": 0.0},
            {"index": 1, "x": 2.5, "y": 1.0, "azimuth": 0.0}
        ]
        
        validated = visualization_service.calculate_manual_placement(
            positions=manual_positions,
            building_dims=sample_building_dims,
            roof_config=sample_roof_config
        )
        
        assert isinstance(validated, list)
        assert len(validated) == 2
        
        # Check that Z and tilt were calculated
        for pos in validated:
            assert "z" in pos
            assert "tilt" in pos
            assert pos["z"] is not None
            assert pos["tilt"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
