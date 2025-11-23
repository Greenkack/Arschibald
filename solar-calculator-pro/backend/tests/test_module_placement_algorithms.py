"""
Tests for Module Placement Algorithms

Task 135: 3D Module Placement Algorithms
Requirements: 1.3, 6.1
"""

import pytest
import math
from backend.services.module_placement_algorithms import (
    ModulePlacementAlgorithms,
    PlacementConfig,
    RoofSurface,
    ModuleOrientation,
    PlacementStrategy,
    PlacementConstraint,
    ModuleDimensions
)


class TestModuleDimensions:
    """Test module dimensions"""
    
    def test_portrait_dimensions(self):
        dims = ModuleDimensions()
        w, h = dims.get_dimensions(ModuleOrientation.PORTRAIT)
        assert w == 1.05
        assert h == 1.76
    
    def test_landscape_dimensions(self):
        dims = ModuleDimensions()
        w, h = dims.get_dimensions(ModuleOrientation.LANDSCAPE)
        assert w == 1.76
        assert h == 1.05


class TestOptimalPlacement:
    """Test optimal placement algorithm"""
    
    def test_basic_placement(self):
        """Test basic optimal placement on flat roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(
            roof=roof,
            module_quantity=30,
            orientation=ModuleOrientation.AUTO
        )
        
        result = algorithms.calculate_optimal_placement(config)
        
        assert result.count > 0
        assert result.count <= 30
        assert 0 <= result.coverage <= 100
        assert 0 <= result.efficiency <= 1.0
        assert result.strategy_used == PlacementStrategy.OPTIMAL
        assert len(result.positions) == result.count
        assert len(result.orientations) == result.count
    
    def test_small_roof(self):
        """Test placement on small roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=3.0, width=3.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=10)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Small roof should place fewer modules
        assert result.count < 10
        assert result.efficiency < 1.0
    
    def test_large_roof(self):
        """Test placement on large roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=20.0, width=15.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=50)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Large roof should place all modules
        assert result.count == 50
        assert result.efficiency == 1.0
        assert result.coverage > 0


class TestConstraintBasedPlacement:
    """Test constraint-based placement"""
    
    def test_single_obstacle(self):
        """Test placement with single obstacle"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        obstacle = PlacementConstraint(
            x=0.0, y=0.0, width=2.0, height=2.0, type="obstacle"
        )
        
        config = PlacementConfig(
            roof=roof,
            module_quantity=30,
            constraints=[obstacle]
        )
        
        result = algorithms.calculate_constraint_based_placement(config)
        
        # Should place fewer modules due to obstacle
        assert result.count > 0
        assert result.strategy_used == PlacementStrategy.CONSTRAINT_BASED
        
        # Verify no modules in obstacle area
        for pos in result.positions:
            x, y, z = pos
            # Check if position is outside obstacle
            assert not (-1.0 <= x <= 1.0 and -1.0 <= y <= 1.0)
    
    def test_multiple_constraints(self):
        """Test placement with multiple constraints"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=12.0, width=10.0, type="flat")
        constraints = [
            PlacementConstraint(x=2.0, y=2.0, width=1.5, height=1.5, type="obstacle"),
            PlacementConstraint(x=-2.0, y=-2.0, width=1.5, height=1.5, type="shading")
        ]
        
        config = PlacementConfig(
            roof=roof,
            module_quantity=40,
            constraints=constraints
        )
        
        result = algorithms.calculate_constraint_based_placement(config)
        
        assert result.count > 0
        assert result.count < 40  # Some modules blocked by constraints


class TestSpacingCalculation:
    """Test spacing calculation"""
    
    def test_portrait_spacing(self):
        """Test spacing calculation for portrait orientation"""
        algorithms = ModulePlacementAlgorithms()
        
        spacing_x, spacing_y = algorithms.calculate_spacing(
            module_count=30,
            roof_length=10.0,
            roof_width=8.0,
            orientation=ModuleOrientation.PORTRAIT,
            margin=0.30
        )
        
        assert spacing_x >= 0.05  # Minimum spacing
        assert spacing_y >= 0.05
        assert spacing_x < 1.0  # Reasonable spacing
        assert spacing_y < 1.0
    
    def test_landscape_spacing(self):
        """Test spacing calculation for landscape orientation"""
        algorithms = ModulePlacementAlgorithms()
        
        spacing_x, spacing_y = algorithms.calculate_spacing(
            module_count=30,
            roof_length=10.0,
            roof_width=8.0,
            orientation=ModuleOrientation.LANDSCAPE,
            margin=0.30
        )
        
        assert spacing_x >= 0.05
        assert spacing_y >= 0.05


class TestOrientationOptimization:
    """Test orientation optimization"""
    
    def test_wide_roof(self):
        """Test orientation for wide roof"""
        algorithms = ModulePlacementAlgorithms()
        
        # Wide roof (length > width)
        roof = RoofSurface(length=15.0, width=8.0, type="flat")
        
        orientation = algorithms.optimize_orientation(
            roof=roof,
            module_quantity=30,
            margin=0.30
        )
        
        # Should prefer orientation that fits more modules
        assert orientation in [ModuleOrientation.PORTRAIT, ModuleOrientation.LANDSCAPE]
    
    def test_square_roof(self):
        """Test orientation for square roof"""
        algorithms = ModulePlacementAlgorithms()
        
        # Square roof
        roof = RoofSurface(length=10.0, width=10.0, type="flat")
        
        orientation = algorithms.optimize_orientation(
            roof=roof,
            module_quantity=30,
            margin=0.30
        )
        
        # For square roof, should default to portrait
        assert orientation == ModuleOrientation.PORTRAIT


class TestRowColumnLayout:
    """Test row/column layout generation"""
    
    def test_specific_layout(self):
        """Test generation of specific row/column layout"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=30)
        
        result = algorithms.generate_row_column_layout(config, rows=5, cols=6)
        
        assert result.count == 30  # 5 rows × 6 cols
        assert result.strategy_used == PlacementStrategy.GRID
        assert len(result.positions) == 30
    
    def test_partial_layout(self):
        """Test layout with fewer modules than grid capacity"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=20)
        
        result = algorithms.generate_row_column_layout(config, rows=5, cols=6)
        
        assert result.count == 20  # Only 20 modules requested
        # Efficiency is 1.0 because all requested modules were placed
        assert result.efficiency == pytest.approx(1.0, abs=0.01)


class TestStaggeredPattern:
    """Test staggered pattern generation"""
    
    def test_staggered_placement(self):
        """Test staggered pattern placement"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=30)
        
        result = algorithms.generate_staggered_pattern(config)
        
        assert result.count > 0
        assert result.strategy_used == PlacementStrategy.STAGGERED
        
        # Verify positions are staggered (alternating rows have offset)
        # This is a simplified check
        assert len(result.positions) > 0


class TestCustomPattern:
    """Test custom pattern generation"""
    
    def test_custom_pattern_function(self):
        """Test custom pattern with user-defined function"""
        algorithms = ModulePlacementAlgorithms()
        
        def simple_pattern(config):
            # Simple 3-module pattern
            return [
                (0.0, 0.0, 0.30),
                (2.0, 0.0, 0.30),
                (4.0, 0.0, 0.30)
            ]
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=3)
        
        result = algorithms.generate_custom_pattern(config, simple_pattern)
        
        assert result.count == 3
        assert result.strategy_used == PlacementStrategy.CUSTOM
        assert len(result.positions) == 3
    
    def test_custom_pattern_error_handling(self):
        """Test error handling in custom pattern"""
        algorithms = ModulePlacementAlgorithms()
        
        def broken_pattern(config):
            raise ValueError("Test error")
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=10)
        
        result = algorithms.generate_custom_pattern(config, broken_pattern)
        
        assert result.count == 0
        assert "Error" in result.message


class TestZPositionCalculation:
    """Test Z-position calculation for different roof types"""
    
    def test_flat_roof_z_position(self):
        """Test Z-position for flat roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat", pitch=0.0)
        config = PlacementConfig(roof=roof, module_quantity=1)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Flat roof should have constant Z = 0.30m
        for pos in result.positions:
            x, y, z = pos
            assert z == pytest.approx(0.30, abs=0.01)
    
    def test_pitched_roof_z_position(self):
        """Test Z-position for pitched roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="gable", pitch=35.0)
        config = PlacementConfig(roof=roof, module_quantity=10)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Pitched roof should have varying Z positions
        z_positions = [pos[2] for pos in result.positions]
        assert len(set(z_positions)) > 1  # Multiple different Z values


class TestCoverageCalculation:
    """Test coverage calculation"""
    
    def test_full_coverage(self):
        """Test coverage calculation for full roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=100)  # More than fits
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Coverage should be reasonable (not over 100%)
        assert 0 <= result.coverage <= 100
    
    def test_partial_coverage(self):
        """Test coverage calculation for partial roof"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=10.0, width=8.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=10)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Partial coverage should be less than full
        assert result.coverage < 50  # 10 modules won't cover much


class TestEfficiencyCalculation:
    """Test efficiency calculation"""
    
    def test_full_efficiency(self):
        """Test efficiency when all modules placed"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=20.0, width=15.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=30)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Large roof should place all modules
        assert result.efficiency == pytest.approx(1.0, abs=0.01)
    
    def test_partial_efficiency(self):
        """Test efficiency when not all modules fit"""
        algorithms = ModulePlacementAlgorithms()
        
        roof = RoofSurface(length=5.0, width=4.0, type="flat")
        config = PlacementConfig(roof=roof, module_quantity=50)
        
        result = algorithms.calculate_optimal_placement(config)
        
        # Small roof can't fit all modules
        assert result.efficiency < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
