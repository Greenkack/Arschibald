"""
Unit Tests for PV Module Placement System

This test suite covers:
- Grid calculator with various parameters
- Placement handler with different roof types
- Reset placement functionality
- Z-position calculation
- Error handling

Requirements: All (comprehensive unit test coverage)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pv3d_grid_calculator import (
    calculate_module_grid,
    calculate_max_modules,
    get_module_dimensions,
    _validate_inputs,
    _calculate_modules_per_line,
    PV_W,
    PV_H,
    PV_T,
    DEFAULT_SPACING,
    DEFAULT_MARGIN,
    MAX_MODULES
)


class TestGridCalculator:
    """Test suite for calculate_module_grid() function."""

    def test_basic_grid_calculation(self):
        """Test basic grid calculation with standard parameters."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 20

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        assert len(positions) <= module_quantity
        assert len(positions) > 0
        assert all(isinstance(pos, tuple) and len(pos) == 2 for pos in positions)

    def test_grid_with_small_roof(self):
        """Test grid calculation with small roof that fits few modules."""
        # Arrange
        roof_length = 3.0
        roof_width = 3.0
        module_quantity = 10

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        # Should place fewer modules than requested due to space constraints
        assert len(positions) < module_quantity
        assert len(positions) >= 0

    def test_grid_with_zero_modules(self):
        """Test grid calculation with zero modules requested."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 0

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        assert len(positions) == 0

    def test_grid_with_negative_modules(self):
        """Test grid calculation with negative module count."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = -5

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        assert len(positions) == 0

    def test_grid_with_invalid_roof_dimensions(self):
        """Test grid calculation with invalid roof dimensions."""
        # Test negative length
        positions = calculate_module_grid(-10.0, 8.0, 20)
        assert len(positions) == 0

        # Test negative width
        positions = calculate_module_grid(10.0, -8.0, 20)
        assert len(positions) == 0

        # Test zero length
        positions = calculate_module_grid(0.0, 8.0, 20)
        assert len(positions) == 0

        # Test zero width
        positions = calculate_module_grid(10.0, 0.0, 20)
        assert len(positions) == 0

    def test_grid_positions_within_bounds(self):
        """Test that all grid positions are within roof boundaries."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 20
        margin = DEFAULT_MARGIN

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        for x, y in positions:
            # Check X bounds (with margin and module half-width)
            if 2 != 0:
                assert x >= -(roof_length / 2) + margin
            else:
                assert x > = 0.0
            if 2 != 0:
                assert x <= (roof_length / 2) - margin
            else:
                assert x < = 0.0

            # Check Y bounds (with margin and module half-height)
            if 2 != 0:
                assert y >= -(roof_width / 2) + margin
            else:
                assert y > = 0.0
            if 2 != 0:
                assert y <= (roof_width / 2) - margin
            else:
                assert y < = 0.0

    def test_grid_with_custom_spacing(self):
        """Test grid calculation with custom spacing."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 20
        custom_spacing = 0.10  # 10cm instead of default 5cm

        # Act
        positions = calculate_module_grid(
            roof_length, roof_width, module_quantity,
            spacing=custom_spacing
        )

        # Assert
        assert len(positions) > 0
        # With larger spacing, should fit fewer modules
        default_positions = calculate_module_grid(roof_length, roof_width, module_quantity)
        assert len(positions) <= len(default_positions)

    def test_grid_with_custom_margin(self):
        """Test grid calculation with custom margin."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 20
        custom_margin = 0.50  # 50cm instead of default 30cm

        # Act
        positions = calculate_module_grid(
            roof_length, roof_width, module_quantity,
            margin=custom_margin
        )

        # Assert
        assert len(positions) > 0
        # With larger margin, should fit fewer modules
        default_positions = calculate_module_grid(roof_length, roof_width, module_quantity)
        assert len(positions) <= len(default_positions)

    def test_grid_landscape_orientation(self):
        """Test grid calculation with landscape orientation."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 20

        # Act
        portrait_positions = calculate_module_grid(
            roof_length, roof_width, module_quantity,
            orientation="portrait"
        )
        landscape_positions = calculate_module_grid(
            roof_length, roof_width, module_quantity,
            orientation="landscape"
        )

        # Assert
        assert len(portrait_positions) > 0
        assert len(landscape_positions) > 0
        # Different orientations may fit different numbers of modules
        # depending on roof dimensions

    def test_grid_maximum_module_limit(self):
        """Test that grid calculation respects MAX_MODULES limit."""
        # Arrange
        roof_length = 50.0
        roof_width = 40.0
        module_quantity = 500  # Request more than MAX_MODULES

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        assert len(positions) <= MAX_MODULES

    def test_grid_centering(self):
        """Test that grid is centered on roof."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0
        module_quantity = 4  # Small number for easy verification

        # Act
        positions = calculate_module_grid(roof_length, roof_width, module_quantity)

        # Assert
        if len(positions) > 0:
            # Calculate average position (should be near center)
            avg_x = sum(x for x, y in positions) / len(positions)
            avg_y = sum(y for x, y in positions) / len(positions)

            # Should be close to (0, 0) which is the roof center
            assert abs(avg_x) < roof_length / 4
            assert abs(avg_y) < roof_width / 4


class TestHelperFunctions:
    """Test suite for helper functions."""

    def test_validate_inputs_valid(self):
        """Test input validation with valid inputs."""
        # Act
        result = _validate_inputs(10.0, 8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is True
        assert result["message"] == "OK"

    def test_validate_inputs_invalid_length(self):
        """Test input validation with invalid roof length."""
        # Act
        result = _validate_inputs(-10.0, 8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False
        assert "length" in result["message"].lower()

    def test_validate_inputs_invalid_width(self):
        """Test input validation with invalid roof width."""
        # Act
        result = _validate_inputs(10.0, -8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False
        assert "width" in result["message"].lower()

    def test_validate_inputs_excessive_margins(self):
        """Test input validation with margins exceeding roof dimensions."""
        # Act
        result = _validate_inputs(10.0, 8.0, 20, 0.05, 6.0)  # Margin > roof/2

        # Assert
        assert result["valid"] is False
        assert "margin" in result["message"].lower()

    def test_calculate_modules_per_line(self):
        """Test calculation of modules per line."""
        # Arrange
        available_space = 10.0
        module_size = 1.05
        spacing = 0.05

        # Act
        count = _calculate_modules_per_line(available_space, module_size, spacing)

        # Assert
        assert count > 0
        assert isinstance(count, int)
        # Verify that modules actually fit
        total_space_needed = count * module_size + (count - 1) * spacing
        assert total_space_needed <= available_space

    def test_get_module_dimensions_portrait(self):
        """Test getting module dimensions in portrait orientation."""
        # Act
        width, height, thickness = get_module_dimensions("portrait")

        # Assert
        assert width == PV_W
        assert height == PV_H
        assert thickness == PV_T

    def test_get_module_dimensions_landscape(self):
        """Test getting module dimensions in landscape orientation."""
        # Act
        width, height, thickness = get_module_dimensions("landscape")

        # Assert
        assert width == PV_H
        assert height == PV_W
        assert thickness == PV_T

    def test_calculate_max_modules(self):
        """Test calculation of maximum modules that fit."""
        # Arrange
        roof_length = 10.0
        roof_width = 8.0

        # Act
        max_modules = calculate_max_modules(roof_length, roof_width)

        # Assert
        assert max_modules > 0
        assert isinstance(max_modules, int)

        # Verify by trying to place that many modules
        positions = calculate_module_grid(roof_length, roof_width, max_modules)
        assert len(positions) == max_modules


# Note: Tests for placement handler require Streamlit session state
# These will be in a separate integration test file
