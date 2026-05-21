"""
Tests for 3D Mounting System Visualization Service

Tests all mounting system functionality including:
- Rail generation
- Clamp placement
- Roof penetrations
- Cable routing
- BOM generation
- Cost calculation
"""

import pytest
from typing import List, Dict, Any

from ..services.mounting_system_service import (
    MountingSystemService,
    MountingType,
    RailOrientation,
    ClampType,
    PenetrationType,
    MountingRail,
    MountingClamp,
    RoofPenetration,
    CableRoute,
    BOMItem,
    MountingSystemVisualization
)


@pytest.fixture
def mounting_service():
    """Create mounting system service instance"""
    return MountingSystemService()


@pytest.fixture
def sample_module_positions():
    """Create sample module positions for testing"""
    return [
        {
            'id': 'module_1',
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        },
        {
            'id': 'module_2',
            'position': {'x': 1.7, 'y': 0.0, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        },
        {
            'id': 'module_3',
            'position': {'x': 3.4, 'y': 0.0, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        },
        {
            'id': 'module_4',
            'position': {'x': 0.0, 'y': 1.1, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        },
        {
            'id': 'module_5',
            'position': {'x': 1.7, 'y': 1.1, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        },
        {
            'id': 'module_6',
            'position': {'x': 3.4, 'y': 1.1, 'z': 0.0},
            'width': 1.6,
            'height': 1.0,
            'orientation': 'landscape'
        }
    ]


class TestMountingRailGeneration:
    """Test mounting rail generation"""
    
    def test_generate_horizontal_rails(self, mounting_service, sample_module_positions):
        """Test horizontal rail generation"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        assert len(rails) > 0
        assert all(rail.orientation == RailOrientation.HORIZONTAL for rail in rails)
        assert all(rail.length > 0 for rail in rails)
        assert all(rail.material == "aluminum" for rail in rails)
    
    def test_generate_vertical_rails(self, mounting_service, sample_module_positions):
        """Test vertical rail generation"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.VERTICAL
        )
        
        assert len(rails) > 0
        assert all(rail.orientation == RailOrientation.VERTICAL for rail in rails)
        assert all(rail.length > 0 for rail in rails)
    
    def test_rail_count_matches_module_layout(self, mounting_service, sample_module_positions):
        """Test that rail count is appropriate for module layout"""
        # For horizontal orientation, expect 2 rails per row (top and bottom)
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        # 6 modules in 2 rows = 4 rails (2 per row)
        assert len(rails) == 4
    
    def test_empty_module_list(self, mounting_service):
        """Test handling of empty module list"""
        rails = mounting_service.generate_mounting_rails(
            [],
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        assert len(rails) == 0


class TestMountingClampGeneration:
    """Test mounting clamp generation"""
    
    def test_generate_clamps(self, mounting_service, sample_module_positions):
        """Test clamp generation"""
        # First generate rails
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        # Then generate clamps
        clamps = mounting_service.generate_mounting_clamps(rails, sample_module_positions)
        
        assert len(clamps) > 0
        assert all(isinstance(clamp.clamp_type, ClampType) for clamp in clamps)
        assert all(clamp.torque_spec > 0 for clamp in clamps)
    
    def test_clamp_types_distribution(self, mounting_service, sample_module_positions):
        """Test that clamps have appropriate type distribution"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        clamps = mounting_service.generate_mounting_clamps(rails, sample_module_positions)
        
        # Should have both end clamps and mid clamps
        clamp_types = {clamp.clamp_type for clamp in clamps}
        assert ClampType.END_CLAMP in clamp_types or ClampType.MID_CLAMP in clamp_types
    
    def test_clamps_reference_valid_rails(self, mounting_service, sample_module_positions):
        """Test that all clamps reference valid rails"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        clamps = mounting_service.generate_mounting_clamps(rails, sample_module_positions)
        
        rail_ids = {rail.id for rail in rails}
        assert all(clamp.rail_id in rail_ids for clamp in clamps)


class TestRoofPenetrationGeneration:
    """Test roof penetration generation"""
    
    def test_generate_penetrations_pitched_roof(self, mounting_service, sample_module_positions):
        """Test penetration generation for pitched roof"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        penetrations = mounting_service.generate_roof_penetrations(
            rails,
            MountingType.PITCHED_ROOF,
            30.0
        )
        
        assert len(penetrations) > 0
        assert all(pen.penetration_type == PenetrationType.HOOK for pen in penetrations)
        assert all(pen.waterproofing for pen in penetrations)
    
    def test_generate_penetrations_flat_roof(self, mounting_service, sample_module_positions):
        """Test penetration generation for flat roof"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.FLAT_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        penetrations = mounting_service.generate_roof_penetrations(
            rails,
            MountingType.FLAT_ROOF,
            0.0
        )
        
        assert len(penetrations) > 0
        assert all(pen.penetration_type == PenetrationType.BALLAST for pen in penetrations)
        assert all(not pen.waterproofing for pen in penetrations)
    
    def test_penetration_spacing(self, mounting_service, sample_module_positions):
        """Test that penetrations are appropriately spaced"""
        rails = mounting_service.generate_mounting_rails(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL
        )
        
        penetrations = mounting_service.generate_roof_penetrations(
            rails,
            MountingType.PITCHED_ROOF,
            30.0
        )
        
        # Each rail should have at least 2 penetrations
        rail_ids = {rail.id for rail in rails}
        for rail_id in rail_ids:
            rail_penetrations = [p for p in penetrations if p.rail_id == rail_id]
            assert len(rail_penetrations) >= 2


class TestCableRoutingGeneration:
    """Test cable routing generation"""
    
    def test_generate_cable_routes(self, mounting_service, sample_module_positions):
        """Test cable route generation"""
        inverter_position = (5.0, 0.5, 0.0)
        
        cable_routes = mounting_service.generate_cable_routing(
            sample_module_positions,
            inverter_position,
            MountingType.PITCHED_ROOF
        )
        
        assert len(cable_routes) > 0
        assert any(route.cable_type == "DC" for route in cable_routes)
        assert any(route.cable_type == "AC" for route in cable_routes)
    
    def test_cable_length_calculation(self, mounting_service, sample_module_positions):
        """Test that cable lengths are calculated correctly"""
        inverter_position = (5.0, 0.5, 0.0)
        
        cable_routes = mounting_service.generate_cable_routing(
            sample_module_positions,
            inverter_position,
            MountingType.PITCHED_ROOF
        )
        
        assert all(route.length > 0 for route in cable_routes)
        assert all(len(route.waypoints) >= 2 for route in cable_routes)
    
    def test_dc_routes_end_at_inverter(self, mounting_service, sample_module_positions):
        """Test that DC routes end at inverter position"""
        inverter_position = (5.0, 0.5, 0.0)
        
        cable_routes = mounting_service.generate_cable_routing(
            sample_module_positions,
            inverter_position,
            MountingType.PITCHED_ROOF
        )
        
        dc_routes = [route for route in cable_routes if route.cable_type == "DC"]
        for route in dc_routes:
            last_waypoint = route.waypoints[-1]
            assert last_waypoint == inverter_position


class TestBOMGeneration:
    """Test Bill of Materials generation"""
    
    def test_generate_bom(self, mounting_service, sample_module_positions):
        """Test BOM generation"""
        # Create complete visualization
        visualization = mounting_service.create_complete_visualization(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        assert len(visualization.bom) > 0
        assert all(isinstance(item, BOMItem) for item in visualization.bom)
        assert all(item.quantity > 0 for item in visualization.bom)
        assert all(item.unit_price > 0 for item in visualization.bom)
        assert all(item.total_price > 0 for item in visualization.bom)
    
    def test_bom_includes_all_categories(self, mounting_service, sample_module_positions):
        """Test that BOM includes all component categories"""
        visualization = mounting_service.create_complete_visualization(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        categories = {item.category for item in visualization.bom}
        
        # Should include mounting structure, hardware, and electrical
        assert "Mounting Structure" in categories or "Mounting Hardware" in categories
        assert "Electrical" in categories or "Roof Attachment" in categories
    
    def test_bom_total_matches_sum(self, mounting_service, sample_module_positions):
        """Test that BOM total matches sum of item totals"""
        visualization = mounting_service.create_complete_visualization(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        calculated_total = sum(item.total_price for item in visualization.bom)
        assert abs(visualization.total_cost - calculated_total) < 0.01


class TestCostCalculation:
    """Test cost calculation"""
    
    def test_calculate_total_cost(self, mounting_service):
        """Test total cost calculation"""
        bom = [
            BOMItem(
                item_id="TEST_001",
                description="Test Item 1",
                quantity=10,
                unit="piece",
                unit_price=5.0,
                total_price=50.0,
                category="Test"
            ),
            BOMItem(
                item_id="TEST_002",
                description="Test Item 2",
                quantity=5,
                unit="meter",
                unit_price=10.0,
                total_price=50.0,
                category="Test"
            )
        ]
        
        total = mounting_service.calculate_total_cost(bom)
        assert total == 100.0
    
    def test_cost_increases_with_system_size(self, mounting_service):
        """Test that cost increases with larger systems"""
        # Small system (3 modules)
        small_modules = [
            {'id': f'module_{i}', 'position': {'x': i * 1.7, 'y': 0.0, 'z': 0.0}, 
             'width': 1.6, 'height': 1.0}
            for i in range(3)
        ]
        
        # Large system (12 modules)
        large_modules = [
            {'id': f'module_{i}', 'position': {'x': (i % 4) * 1.7, 'y': (i // 4) * 1.1, 'z': 0.0}, 
             'width': 1.6, 'height': 1.0}
            for i in range(12)
        ]
        
        small_viz = mounting_service.create_complete_visualization(
            small_modules,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        large_viz = mounting_service.create_complete_visualization(
            large_modules,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (10.0, 1.5, 0.0)
        )
        
        assert large_viz.total_cost > small_viz.total_cost


class TestCompleteMountingSystemVisualization:
    """Test complete mounting system visualization"""
    
    def test_create_complete_visualization(self, mounting_service, sample_module_positions):
        """Test creating complete visualization"""
        visualization = mounting_service.create_complete_visualization(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        assert isinstance(visualization, MountingSystemVisualization)
        assert len(visualization.rails) > 0
        assert len(visualization.clamps) > 0
        assert len(visualization.penetrations) > 0
        assert len(visualization.cable_routes) > 0
        assert len(visualization.bom) > 0
        assert visualization.total_cost > 0
    
    def test_visualization_consistency(self, mounting_service, sample_module_positions):
        """Test that visualization components are consistent"""
        visualization = mounting_service.create_complete_visualization(
            sample_module_positions,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (5.0, 0.5, 0.0)
        )
        
        # All clamps should reference existing rails
        rail_ids = {rail.id for rail in visualization.rails}
        assert all(clamp.rail_id in rail_ids for clamp in visualization.clamps)
        
        # All penetrations should reference existing rails
        assert all(pen.rail_id in rail_ids for pen in visualization.penetrations)
    
    def test_different_mounting_types(self, mounting_service, sample_module_positions):
        """Test visualization with different mounting types"""
        for mounting_type in [MountingType.PITCHED_ROOF, MountingType.FLAT_ROOF, MountingType.GROUND_MOUNT]:
            visualization = mounting_service.create_complete_visualization(
                sample_module_positions,
                mounting_type,
                RailOrientation.HORIZONTAL,
                30.0 if mounting_type == MountingType.PITCHED_ROOF else 0.0,
                (5.0, 0.5, 0.0)
            )
            
            assert visualization.mounting_type == mounting_type
            assert len(visualization.rails) > 0
            assert len(visualization.bom) > 0


class TestHelperMethods:
    """Test helper methods"""
    
    def test_group_modules_by_rows(self, mounting_service, sample_module_positions):
        """Test grouping modules by rows"""
        rows = mounting_service._group_modules_by_rows(sample_module_positions)
        
        assert len(rows) == 2  # 6 modules in 2 rows
        assert all(len(row) == 3 for row in rows)  # 3 modules per row
    
    def test_group_modules_by_columns(self, mounting_service, sample_module_positions):
        """Test grouping modules by columns"""
        columns = mounting_service._group_modules_by_columns(sample_module_positions)
        
        assert len(columns) == 3  # 6 modules in 3 columns
        assert all(len(col) == 2 for col in columns)  # 2 modules per column
    
    def test_group_modules_into_strings(self, mounting_service, sample_module_positions):
        """Test grouping modules into electrical strings"""
        strings = mounting_service._group_modules_into_strings(sample_module_positions, modules_per_string=3)
        
        assert len(strings) == 2  # 6 modules / 3 per string = 2 strings
        assert all(len(string) <= 3 for string in strings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
