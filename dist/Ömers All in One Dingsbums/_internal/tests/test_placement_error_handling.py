"""
Unit Tests for Error Handling in PV Module Placement

This test suite covers:
- Error handling for invalid inputs
- Error handling for grid calculation failures
- Error handling for rendering failures
- Fallback to previous state on errors

Requirements: 11.1-11.5 (Error handling and validation)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pv3d_grid_calculator import (
    calculate_module_grid,
    _validate_inputs
)
from utils.pv3d_placement_handler import (
    handle_auto_placement,
    calculate_z_position,
    calculate_tilt_angle
)


class TestInputValidation:
    """Test suite for input validation and error handling."""

    def test_validate_negative_roof_length(self):
        """Test validation rejects negative roof length."""
        # Requirement 11.1: Validate roof dimensions (> 0)
        # Act
        result = _validate_inputs(-10.0, 8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False
        assert "length" in result["message"].lower()

    def test_validate_negative_roof_width(self):
        """Test validation rejects negative roof width."""
        # Requirement 11.1: Validate roof dimensions (> 0)
        # Act
        result = _validate_inputs(10.0, -8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False
        assert "width" in result["message"].lower()

    def test_validate_zero_roof_length(self):
        """Test validation rejects zero roof length."""
        # Requirement 11.1: Validate roof dimensions (> 0)
        # Act
        result = _validate_inputs(0.0, 8.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False

    def test_validate_zero_roof_width(self):
        """Test validation rejects zero roof width."""
        # Requirement 11.1: Validate roof dimensions (> 0)
        # Act
        result = _validate_inputs(10.0, 0.0, 20, 0.05, 0.30)

        # Assert
        assert result["valid"] is False

    def test_validate_negative_spacing(self):
        """Test validation rejects negative spacing."""
        # Act
        result = _validate_inputs(10.0, 8.0, 20, -0.05, 0.30)

        # Assert
        assert result["valid"] is False
        assert "spacing" in result["message"].lower()

    def test_validate_negative_margin(self):
        """Test validation rejects negative margin."""
        # Act
        result = _validate_inputs(10.0, 8.0, 20, 0.05, -0.30)

        # Assert
        assert result["valid"] is False
        assert "margin" in result["message"].lower()

    def test_validate_excessive_margins(self):
        """Test validation rejects margins that exceed roof dimensions."""
        # Act
        result = _validate_inputs(10.0, 8.0, 20, 0.05, 6.0)

        # Assert
        assert result["valid"] is False
        assert "margin" in result["message"].lower()


class TestGridCalculationErrors:
    """Test suite for grid calculation error handling."""

    def test_grid_with_invalid_dimensions_returns_empty(self):
        """Test that invalid dimensions return empty list."""
        # Requirement 11.1, 11.2: Error handling for invalid inputs
        # Act
        positions = calculate_module_grid(-10.0, 8.0, 20)

        # Assert
        assert positions == []

    def test_grid_with_too_small_roof_returns_empty(self):
        """Test that roof too small for even one module returns empty."""
        # Requirement 11.2: Error handling
        # Act
        positions = calculate_module_grid(0.5, 0.5, 10)

        # Assert
        assert positions == []

    def test_grid_with_excessive_margins_returns_empty(self):
        """Test that excessive margins return empty list."""
        # Act
        positions = calculate_module_grid(10.0, 8.0, 20, margin=10.0)

        # Assert
        assert positions == []


class TestAutoPlacementErrors:
    """Test suite for auto placement error handling."""

    @patch('streamlit.session_state', {})
    def test_auto_placement_negative_roof_length(self):
        """Test auto placement with negative roof length."""
        # Requirement 11.1: Validate roof dimensions
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=-10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        assert "fehler" in result["message"].lower()
        assert "länge" in result["message"].lower()

    @patch('streamlit.session_state', {})
    def test_auto_placement_negative_roof_width(self):
        """Test auto placement with negative roof width."""
        # Requirement 11.1: Validate roof dimensions
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=-8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        assert "fehler" in result["message"].lower()
        assert "breite" in result["message"].lower()

    @patch('streamlit.session_state', {})
    def test_auto_placement_zero_modules(self):
        """Test auto placement with zero modules."""
        # Requirement 11.1: Validate module quantity
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=0,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        assert "fehler" in result["message"].lower()

    @patch('streamlit.session_state', {})
    def test_auto_placement_negative_modules(self):
        """Test auto placement with negative module count."""
        # Requirement 11.1: Validate module quantity
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=-5,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        assert "fehler" in result["message"].lower()

    @patch('streamlit.session_state', {})
    def test_auto_placement_unrealistic_dimensions(self):
        """Test auto placement with unrealistic roof dimensions."""
        # Requirement 11.1: Validate reasonable values
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=2000.0,  # 2km roof!
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        assert "fehler" in result["message"].lower()

    @patch('streamlit.session_state', {})
    def test_auto_placement_excessive_modules(self):
        """Test auto placement with excessive module count."""
        # Requirement 11.1: Validate reasonable values
        # Note: The function limits to MAX_MODULES (200) and succeeds
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=2000,  # Way too many
            roof_type="Flachdach"
        )

        # Assert
        # Should succeed but limit to MAX_MODULES
        assert result["success"] is True
        assert result["count"] <= 200  # MAX_MODULES limit

    @patch('streamlit.session_state', {})
    def test_auto_placement_fallback_on_error(self):
        """Test that auto placement falls back to previous state on error."""
        # Requirement 11.5: Fallback to previous state on error
        import streamlit as st

        # Arrange
        previous_positions = [(0.0, 0.0, 0.3), (1.1, 0.0, 0.3)]
        st.session_state["placed_module_positions"] = previous_positions.copy()
        st.session_state["placed_module_count"] = 2

        # Act - trigger error with invalid dimensions
        result = handle_auto_placement(
            roof_length=-10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        # Previous state should be preserved
        assert st.session_state["placed_module_count"] == 2
        assert st.session_state["placed_module_positions"] == previous_positions


class TestZPositionErrors:
    """Test suite for Z-position calculation error handling."""

    def test_z_position_with_empty_roof_type(self):
        """Test Z-position calculation with empty roof type."""
        # Should not crash, should return default value
        # Act
        z_pos = calculate_z_position("", 0.0, 10.0)

        # Assert
        assert isinstance(z_pos, float)
        assert z_pos > 0

    def test_z_position_with_unknown_roof_type(self):
        """Test Z-position calculation with unknown roof type."""
        # Should not crash, should return default value
        # Act
        z_pos = calculate_z_position("UnknownRoofType", 0.0, 10.0)

        # Assert
        assert isinstance(z_pos, float)
        assert z_pos > 0

    def test_z_position_with_negative_pitch(self):
        """Test Z-position calculation with negative pitch."""
        # Should not crash
        # Act
        z_pos = calculate_z_position("Satteldach", -10.0, 10.0)

        # Assert
        assert isinstance(z_pos, float)
        assert z_pos > 0


class TestTiltAngleErrors:
    """Test suite for tilt angle calculation error handling."""

    def test_tilt_angle_with_empty_roof_type(self):
        """Test tilt angle calculation with empty roof type."""
        # Should not crash, should return default value
        # Act
        tilt = calculate_tilt_angle("", 0.0)

        # Assert
        assert isinstance(tilt, float)
        assert tilt >= 0

    def test_tilt_angle_with_unknown_roof_type(self):
        """Test tilt angle calculation with unknown roof type."""
        # Should not crash, should return default value
        # Act
        tilt = calculate_tilt_angle("UnknownRoofType", 35.0)

        # Assert
        assert isinstance(tilt, float)
        assert tilt >= 0

    def test_tilt_angle_with_negative_pitch(self):
        """Test tilt angle calculation with negative pitch."""
        # Should handle gracefully
        # Act
        tilt = calculate_tilt_angle("Satteldach", -10.0)

        # Assert
        assert isinstance(tilt, float)


class TestMeaningfulErrorMessages:
    """Test suite for meaningful error messages."""

    @patch('streamlit.session_state', {})
    def test_error_message_includes_actual_values(self):
        """Test that error messages include actual values."""
        # Requirement 11.4: Meaningful error messages
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=-5.5,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        # Message should include the actual invalid value
        assert "-5.5" in result["message"] or "5.5" in result["message"]

    @patch('streamlit.session_state', {})
    def test_error_message_is_in_german(self):
        """Test that error messages are in German."""
        # Requirement 11.4: Meaningful error messages
        import streamlit as st

        # Arrange
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0

        # Act
        result = handle_auto_placement(
            roof_length=-10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach"
        )

        # Assert
        assert result["success"] is False
        # Should contain German words
        assert any(word in result["message"].lower() for word in ["fehler", "ungültig", "größer"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
