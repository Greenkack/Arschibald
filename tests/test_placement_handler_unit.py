"""
Unit Tests for PV Module Placement Handler

This test suite covers:
- Z-position calculation for different roof types
- Tilt angle calculation
- Collision detection
- Error handling

Requirements: 2.2, 2.6, 4.4, 6.1-6.5, 7.1-7.4, 9.1-9.2, 11.1-11.5
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pv3d_placement_handler import (
    calculate_z_position,
    calculate_tilt_angle,
    check_module_collision,
    handle_reset_placement,
    initialize_session_state,
    get_placement_statistics,
    PV_W,
    PV_H,
    DEFAULT_MARGIN
)


class TestZPositionCalculation:
    """Test suite for calculate_z_position() function."""

    def test_z_position_flat_roof(self):
        """Test Z-position calculation for flat roof (Flachdach)."""
        # Requirement 6.1: Flat roof with elevated mounting (30° tilt)
        # Act
        z_pos = calculate_z_position("Flachdach", 0.0, 10.0)

        # Assert
        assert z_pos == 0.3  # 30cm elevation for mounting frame

    def test_z_position_gable_roof(self):
        """Test Z-position calculation for gable roof (Satteldach)."""
        # Requirement 6.2: Gable roof parallel to surface
        # Act
        z_pos = calculate_z_position("Satteldach", 35.0, 10.0)

        # Assert
        assert z_pos == 0.15  # 15cm clearance above roof base

    def test_z_position_shed_roof(self):
        """Test Z-position calculation for shed roof (Pultdach)."""
        # Requirement 6.3: Shed roof parallel to surface
        # Act
        z_pos = calculate_z_position("Pultdach", 25.0, 10.0)

        # Assert
        assert z_pos == 0.15  # 15cm clearance above roof base

    def test_z_position_hip_roof(self):
        """Test Z-position calculation for hip roof (Walmdach)."""
        # Act
        z_pos = calculate_z_position("Walmdach", 40.0, 10.0)

        # Assert
        assert z_pos == 0.15  # 15cm clearance above roof base

    def test_z_position_case_insensitive(self):
        """Test that roof type matching is case-insensitive."""
        # Act
        z_pos_lower = calculate_z_position("flachdach", 0.0, 10.0)
        z_pos_upper = calculate_z_position("FLACHDACH", 0.0, 10.0)
        z_pos_mixed = calculate_z_position("FlachDach", 0.0, 10.0)

        # Assert
        assert z_pos_lower == z_pos_upper == z_pos_mixed == 0.3

    def test_z_position_with_whitespace(self):
        """Test that roof type handles whitespace."""
        # Act
        z_pos = calculate_z_position("  Flachdach  ", 0.0, 10.0)

        # Assert
        assert z_pos == 0.3


class TestTiltAngleCalculation:
    """Test suite for calculate_tilt_angle() function."""

    def test_tilt_angle_flat_roof(self):
        """Test tilt angle for flat roof."""
        # Requirement 6.1: Flat roof with 30° tilt
        # Act
        tilt = calculate_tilt_angle("Flachdach", 0.0)

        # Assert
        assert tilt == 30.0

    def test_tilt_angle_gable_roof(self):
        """Test tilt angle for gable roof."""
        # Requirement 6.5: Pitched roofs use roof pitch angle
        # Act
        tilt = calculate_tilt_angle("Satteldach", 35.0)

        # Assert
        assert tilt == 35.0

    def test_tilt_angle_shed_roof(self):
        """Test tilt angle for shed roof."""
        # Requirement 6.5: Pitched roofs use roof pitch angle
        # Act
        tilt = calculate_tilt_angle("Pultdach", 25.0)

        # Assert
        assert tilt == 25.0

    def test_tilt_angle_zero_pitch(self):
        """Test tilt angle with zero pitch on pitched roof."""
        # Act
        tilt = calculate_tilt_angle("Satteldach", 0.0)

        # Assert
        assert tilt == 0.0

    def test_tilt_angle_case_insensitive(self):
        """Test that tilt angle calculation is case-insensitive."""
        # Act
        tilt_lower = calculate_tilt_angle("flachdach", 0.0)
        tilt_upper = calculate_tilt_angle("FLACHDACH", 0.0)

        # Assert
        assert tilt_lower == tilt_upper == 30.0


class TestCollisionDetection:
    """Test suite for check_module_collision() function."""

    def test_no_collision_empty_roof(self):
        """Test collision detection with no existing modules."""
        # Requirement 7.1, 7.2: Check for collisions
        # Arrange
        new_position = (0.0, 0.0, 0.3)
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is False
        assert result["type"] == "none"

    def test_collision_with_existing_module(self):
        """Test collision detection with overlapping module."""
        # Requirement 7.1: Check for module-to-module overlap
        # Arrange
        new_position = (0.0, 0.0, 0.3)
        existing_positions = [(0.0, 0.0, 0.3)]  # Same position
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "module"
        assert result["colliding_index"] == 0

    def test_collision_boundary_left(self):
        """Test collision detection at left boundary."""
        # Requirement 7.2: Check for roof edge violation
        # Arrange
        new_position = (-10.0, 0.0, 0.3)  # Far left
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "boundary"

    def test_collision_boundary_right(self):
        """Test collision detection at right boundary."""
        # Requirement 7.2: Check for roof edge violation
        # Arrange
        new_position = (10.0, 0.0, 0.3)  # Far right
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "boundary"

    def test_collision_boundary_top(self):
        """Test collision detection at top boundary."""
        # Requirement 7.2: Check for roof edge violation
        # Arrange
        new_position = (0.0, 10.0, 0.3)  # Far top
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "boundary"

    def test_collision_boundary_bottom(self):
        """Test collision detection at bottom boundary."""
        # Requirement 7.2: Check for roof edge violation
        # Arrange
        new_position = (0.0, -10.0, 0.3)  # Far bottom
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "boundary"

    def test_no_collision_adjacent_modules(self):
        """Test that adjacent modules with proper spacing don't collide."""
        # Arrange
        spacing = 0.05
        new_position = (PV_W + spacing, 0.0, 0.3)
        existing_positions = [(0.0, 0.0, 0.3)]
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is False

    def test_collision_with_multiple_modules(self):
        """Test collision detection with multiple existing modules."""
        # Arrange
        new_position = (2.0, 2.0, 0.3)
        existing_positions = [
            (0.0, 0.0, 0.3),
            (2.0, 2.0, 0.3),  # Collides with this one
            (4.0, 4.0, 0.3)
        ]
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width
        )

        # Assert
        assert result["collision"] is True
        assert result["type"] == "module"
        assert result["colliding_index"] == 1

    def test_collision_landscape_orientation(self):
        """Test collision detection with landscape orientation."""
        # Arrange
        new_position = (0.0, 0.0, 0.3)
        existing_positions = []
        roof_length = 10.0
        roof_width = 8.0

        # Act
        result = check_module_collision(
            new_position, existing_positions,
            roof_length, roof_width,
            orientation="landscape"
        )

        # Assert
        assert result["collision"] is False


class TestResetPlacement:
    """Test suite for handle_reset_placement() function."""

    @patch('streamlit.session_state', {})
    def test_reset_placement_empty(self):
        """Test reset with no modules placed."""
        # Requirement 4.4: Reset button functionality
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_reset_placement()

        # Assert
        assert result["success"] is True
        assert st.session_state["placed_module_count"] == 0
        assert len(st.session_state["placed_module_positions"]) == 0

    @patch('streamlit.session_state', {})
    def test_reset_placement_with_modules(self):
        """Test reset with modules placed."""
        # Requirement 4.4: Reset button functionality
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = [
            (0.0, 0.0, 0.3),
            (1.1, 0.0, 0.3),
            (2.2, 0.0, 0.3)
        ]
        st.session_state["placed_module_count"] = 3

        # Act
        result = handle_reset_placement()

        # Assert
        assert result["success"] is True
        assert st.session_state["placed_module_count"] == 0
        assert len(st.session_state["placed_module_positions"]) == 0


class TestSessionStateManagement:
    """Test suite for session state management functions."""

    @patch('streamlit.session_state', {})
    def test_initialize_session_state(self):
        """Test session state initialization."""
        # Requirement 9.1-9.4: Session state initialization
        import streamlit as st

        # Act
        initialize_session_state()

        # Assert
        assert "placed_module_positions" in st.session_state
        assert "placed_module_count" in st.session_state
        assert "trigger_auto_placement" in st.session_state
        assert "selected_module_indices" in st.session_state
        assert "show_placement_grid" in st.session_state
        assert "show_module_numbers" in st.session_state

        assert st.session_state["placed_module_positions"] == []
        assert st.session_state["placed_module_count"] == 0
        assert st.session_state["trigger_auto_placement"] is False

    @patch('streamlit.session_state', {})
    def test_get_placement_statistics_empty(self):
        """Test getting statistics with no modules."""
        import streamlit as st

        # Arrange
        st.session_state["placed_module_count"] = 0
        st.session_state["placed_module_positions"] = []

        # Act
        stats = get_placement_statistics()

        # Assert
        assert stats["placed_count"] == 0
        assert stats["positions"] == []
        assert stats["has_modules"] is False

    @patch('streamlit.session_state', {})
    def test_get_placement_statistics_with_modules(self):
        """Test getting statistics with modules placed."""
        import streamlit as st

        # Arrange
        positions = [(0.0, 0.0, 0.3), (1.1, 0.0, 0.3)]
        st.session_state["placed_module_count"] = 2
        st.session_state["placed_module_positions"] = positions

        # Act
        stats = get_placement_statistics()

        # Assert
        assert stats["placed_count"] == 2
        assert stats["positions"] == positions
        assert stats["has_modules"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
