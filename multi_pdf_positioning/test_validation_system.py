"""
Tests for Validation System Module

This test suite validates all functionality of the validation system including:
- Position validation (bounds, margins, dimensions)
- Collision detection
- Collision resolution
- Validation reporting
"""

import pytest
from multi_pdf_positioning.validation_system import (
    ValidationSystem,
    ValidationReport,
    ValidationLevel,
    ValidationMessage,
    CollisionInfo,
    validate_positions,
    detect_collisions,
    generate_validation_report
)
from multi_pdf_positioning.yml_parser import YMLElement


class TestPositionValidation:
    """Test position validation functionality."""
    
    def test_valid_positions(self):
        """Test that valid positions pass validation."""
        validator = ValidationSystem()
        
        positions = [
            (50, 50, 200, 100),
            (250, 150, 400, 250),
            (100, 400, 300, 500),
        ]
        
        report = validator.validate_positions(positions)
        
        assert report.total_elements == 3
        # Should have no errors (might have warnings for margins)
        assert len(report.get_errors()) == 0
    
    def test_position_out_of_bounds(self):
        """Test detection of positions outside PDF bounds."""
        validator = ValidationSystem()
        
        positions = [
            (-10, 50, 200, 100),     # x1 negative
            (50, -10, 200, 100),     # y1 negative
            (400, 50, 700, 100),     # x2 exceeds page width
            (50, 800, 200, 900),     # y2 exceeds page height
        ]
        
        report = validator.validate_positions(positions)
        
        # Should have 4 errors (one for each out-of-bounds position)
        errors = report.get_errors()
        assert len(errors) >= 4
        assert not report.is_valid
    
    def test_margin_validation(self):
        """Test minimum margin validation."""
        validator = ValidationSystem(min_margin=10)
        
        positions = [
            (5, 50, 200, 100),       # x1 too close to left edge
            (50, 5, 200, 100),       # y1 too close to bottom edge
            (400, 50, 590, 100),     # x2 too close to right edge
            (50, 750, 200, 838),     # y2 too close to top edge
        ]
        
        report = validator.validate_positions(positions)
        
        # Should have warnings for margin violations
        warnings = report.get_warnings()
        assert len(warnings) >= 4
    
    def test_invalid_dimensions(self):
        """Test detection of invalid dimensions."""
        validator = ValidationSystem()
        
        positions = [
            (200, 50, 100, 100),     # x2 <= x1 (invalid width)
            (50, 200, 200, 100),     # y2 <= y1 (invalid height)
            (100, 100, 100, 100),    # Zero width and height
        ]
        
        report = validator.validate_positions(positions)
        
        # Should have errors for invalid dimensions
        errors = report.get_errors()
        assert len(errors) >= 3
        assert not report.is_valid
    
    def test_small_element_warning(self):
        """Test warning for very small elements."""
        validator = ValidationSystem()
        
        positions = [
            (50, 50, 52, 100),       # Width = 2 (very small)
            (100, 100, 200, 102),    # Height = 2 (very small)
        ]
        
        report = validator.validate_positions(positions)
        
        # Should have warnings for small dimensions
        warnings = report.get_warnings()
        assert len(warnings) >= 2
    
    def test_validation_with_elements(self):
        """Test validation with YMLElement context."""
        validator = ValidationSystem()
        
        elements = [
            YMLElement(
                text="Test Element 1",
                position=(50, 50, 200, 100),
                font="Helvetica",
                font_size=12,
                color=0,
                index=0
            ),
            YMLElement(
                text="Test Element 2",
                position=(-10, 50, 200, 100),  # Invalid
                font="Helvetica",
                font_size=12,
                color=0,
                index=1
            ),
        ]
        
        positions = [elem.position for elem in elements]
        report = validator.validate_positions(positions, elements)
        
        # Check that element text is included in error messages
        errors = report.get_errors()
        assert len(errors) > 0
        assert any("Test Element 2" in str(err.message) for err in errors)


class TestCollisionDetection:
    """Test collision detection functionality."""
    
    def test_no_collisions(self):
        """Test positions with no collisions."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (200, 50, 300, 100),
            (50, 150, 150, 200),
        ]
        
        collisions = validator.detect_collisions(positions)
        
        assert len(collisions) == 0
    
    def test_overlapping_elements(self):
        """Test detection of overlapping elements."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),     # Overlaps with first
        ]
        
        collisions = validator.detect_collisions(positions)
        
        assert len(collisions) == 1
        assert collisions[0].element1_index == 0
        assert collisions[0].element2_index == 1
        assert collisions[0].overlap_area > 0
    
    def test_elements_too_close(self):
        """Test detection of elements closer than min_spacing."""
        validator = ValidationSystem(min_spacing=10)
        
        positions = [
            (50, 50, 150, 100),
            (155, 50, 250, 100),     # Only 5 pts apart (< min_spacing)
        ]
        
        collisions = validator.detect_collisions(positions)
        
        # Should detect collision due to min_spacing
        assert len(collisions) == 1
    
    def test_multiple_collisions(self):
        """Test detection of multiple collisions."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),     # Overlaps with first
            (125, 90, 225, 140),     # Overlaps with second
            (300, 300, 400, 400),    # No overlap
        ]
        
        collisions = validator.detect_collisions(positions)
        
        # Should detect at least 2 collisions
        assert len(collisions) >= 2
    
    def test_collision_info_details(self):
        """Test that collision info contains correct details."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),
        ]
        
        collisions = validator.detect_collisions(positions)
        
        assert len(collisions) == 1
        collision = collisions[0]
        
        assert collision.element1_index == 0
        assert collision.element2_index == 1
        assert collision.element1_position == positions[0]
        assert collision.element2_position == positions[1]
        assert collision.overlap_area > 0
        assert len(collision.overlap_rect) == 4


class TestCollisionResolution:
    """Test automatic collision resolution."""
    
    def test_resolve_simple_collision(self):
        """Test resolution of a simple collision."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),     # Overlaps with first
        ]
        
        collisions = validator.detect_collisions(positions)
        assert len(collisions) == 1
        
        # Resolve collisions
        adjusted = validator.resolve_collisions(positions, collisions)
        
        # Check that positions were adjusted
        assert adjusted != positions
        
        # Verify collision is resolved
        new_collisions = validator.detect_collisions(adjusted)
        assert len(new_collisions) < len(collisions)
    
    def test_resolve_maintains_bounds(self):
        """Test that collision resolution maintains page bounds."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),
        ]
        
        collisions = validator.detect_collisions(positions)
        adjusted = validator.resolve_collisions(positions, collisions)
        
        # Verify all positions are within bounds
        for pos in adjusted:
            x1, y1, x2, y2 = pos
            assert x1 >= validator.min_margin
            assert y1 >= validator.min_margin
            assert x2 <= validator.page_width - validator.min_margin
            assert y2 <= validator.page_height - validator.min_margin
    
    def test_resolve_multiple_iterations(self):
        """Test collision resolution with multiple iterations."""
        validator = ValidationSystem(min_spacing=5)
        
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),
            (125, 90, 225, 140),
        ]
        
        collisions = validator.detect_collisions(positions)
        initial_collision_count = len(collisions)
        
        # Resolve with multiple iterations
        adjusted = validator.resolve_collisions(
            positions, collisions, max_iterations=10
        )
        
        # Verify collisions are reduced
        new_collisions = validator.detect_collisions(adjusted)
        assert len(new_collisions) <= initial_collision_count


class TestValidationReport:
    """Test validation report generation."""
    
    def test_report_structure(self):
        """Test that report has correct structure."""
        validator = ValidationSystem()
        
        positions = [(50, 50, 200, 100)]
        report = validator.validate_positions(positions)
        
        assert isinstance(report, ValidationReport)
        assert report.total_elements == 1
        assert isinstance(report.messages, list)
        assert isinstance(report.collisions, list)
        assert isinstance(report.is_valid, bool)
        assert isinstance(report.summary, dict)
        assert report.timestamp is not None
    
    def test_report_with_firma_seite(self):
        """Test report with firma and seite information."""
        validator = ValidationSystem()
        
        positions = [(50, 50, 200, 100)]
        report = validator.generate_validation_report(
            positions, firma=1, seite=2
        )
        
        assert report.firma == 1
        assert report.seite == 2
    
    def test_report_summary_calculation(self):
        """Test that report summary is calculated correctly."""
        validator = ValidationSystem()
        
        positions = [
            (50, 50, 200, 100),      # Valid
            (-10, 50, 200, 100),     # Error
            (5, 50, 200, 100),       # Warning
        ]
        
        report = validator.validate_positions(positions)
        report.calculate_summary()
        
        assert "total_messages" in report.summary
        assert "errors" in report.summary
        assert "warnings" in report.summary
        assert "collisions" in report.summary
        assert report.summary["elements_validated"] == 3
    
    def test_report_message_filtering(self):
        """Test filtering messages by level."""
        validator = ValidationSystem()
        
        positions = [
            (-10, 50, 200, 100),     # Error
            (5, 50, 200, 100),       # Warning
            (50, 50, 200, 100),      # Valid
        ]
        
        report = validator.validate_positions(positions)
        
        errors = report.get_errors()
        warnings = report.get_warnings()
        info = report.get_info()
        
        assert len(errors) > 0
        assert len(warnings) > 0
        assert all(msg.level == ValidationLevel.ERROR for msg in errors)
        assert all(msg.level == ValidationLevel.WARNING for msg in warnings)
        assert all(msg.level == ValidationLevel.INFO for msg in info)
    
    def test_report_formatting(self):
        """Test report formatting to string."""
        validator = ValidationSystem()
        
        positions = [
            (50, 50, 200, 100),
            (100, 75, 200, 125),     # Collision
        ]
        
        report = validator.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        formatted = validator.format_report(report)
        
        assert isinstance(formatted, str)
        assert "VALIDATION REPORT" in formatted
        assert "Firma: 1" in formatted
        assert "Seite: 1" in formatted
        assert "SUMMARY" in formatted
        
        if report.collisions:
            assert "COLLISIONS" in formatted


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_validate_positions_function(self):
        """Test validate_positions convenience function."""
        positions = [(50, 50, 200, 100)]
        
        report = validate_positions(positions)
        
        assert isinstance(report, ValidationReport)
        assert report.total_elements == 1
    
    def test_detect_collisions_function(self):
        """Test detect_collisions convenience function."""
        positions = [
            (50, 50, 150, 100),
            (100, 75, 200, 125),
        ]
        
        collisions = detect_collisions(positions)
        
        assert isinstance(collisions, list)
        assert len(collisions) > 0
    
    def test_generate_validation_report_function(self):
        """Test generate_validation_report convenience function."""
        positions = [(50, 50, 200, 100)]
        
        report = generate_validation_report(positions, firma=1, seite=1)
        
        assert isinstance(report, ValidationReport)
        assert report.firma == 1
        assert report.seite == 1


class TestIntegration:
    """Integration tests for complete validation workflow."""
    
    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        validator = ValidationSystem()
        
        # Create test positions with various issues
        positions = [
            (50, 50, 200, 100),      # Valid
            (-10, 50, 200, 100),     # Out of bounds
            (5, 50, 200, 100),       # Too close to edge
            (100, 75, 250, 125),     # Collision with first
        ]
        
        # Generate report
        report = validator.generate_validation_report(positions, firma=1, seite=1)
        
        # Verify report contents
        assert report.total_elements == 4
        assert len(report.get_errors()) > 0
        assert len(report.get_warnings()) > 0
        assert len(report.collisions) > 0
        assert not report.is_valid
        
        # Format report
        formatted = validator.format_report(report)
        assert len(formatted) > 0
        
        # Resolve collisions
        if report.collisions:
            adjusted = validator.resolve_collisions(
                positions, report.collisions
            )
            
            # Re-validate
            new_report = validator.validate_positions(adjusted)
            assert len(new_report.collisions) <= len(report.collisions)
    
    def test_validation_with_yml_elements(self):
        """Test validation with actual YML elements."""
        validator = ValidationSystem()
        
        elements = [
            YMLElement(
                text="ERSTELLT FÜR:",
                position=(48, 70, 220, 87),
                font="Helvetica-Bold",
                font_size=20,
                color=30920,
                index=0
            ),
            YMLElement(
                text="kunde_vorname_und_nachname",
                position=(48, 110, 220, 130),  # Non-overlapping position
                font="Helvetica-Bold",
                font_size=14,
                color=3487029,
                index=1
            ),
        ]
        
        positions = [elem.position for elem in elements]
        report = validator.generate_validation_report(
            positions, elements, firma=1, seite=1
        )
        
        # Should be valid (no collisions, within bounds)
        assert report.total_elements == 2
        assert len(report.get_errors()) == 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
