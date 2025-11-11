"""
Tests for Position Calculator Module

This module tests the position calculation, collision detection,
and boundary validation functionality.
"""

import pytest
from multi_pdf_positioning.position_calculator import (
    PositionCalculator,
    POSITIONING_RULES,
    CollisionInfo,
    calculate_positions
)
from multi_pdf_positioning.yml_parser import YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, SafeZone


class TestPositioningRules:
    """Test positioning rules configuration."""
    
    def test_rules_exist(self):
        """Test that all required rules are defined."""
        assert "min_margin" in POSITIONING_RULES
        assert "min_spacing" in POSITIONING_RULES
        assert "page_width" in POSITIONING_RULES
        assert "page_height" in POSITIONING_RULES
        assert "importance_weights" in POSITIONING_RULES
        assert "default_importance" in POSITIONING_RULES
    
    def test_rules_values(self):
        """Test that rule values are reasonable."""
        assert POSITIONING_RULES["min_margin"] > 0
        assert POSITIONING_RULES["min_spacing"] > 0
        assert POSITIONING_RULES["page_width"] == 595  # A4 width
        assert POSITIONING_RULES["page_height"] == 842  # A4 height
        assert 0 <= POSITIONING_RULES["default_importance"] <= 1


class TestPositionCalculator:
    """Test PositionCalculator class."""
    
    def test_init(self):
        """Test calculator initialization."""
        calc = PositionCalculator()
        assert calc.rules == POSITIONING_RULES
        assert calc.collisions == []
    
    def test_init_custom_rules(self):
        """Test calculator with custom rules."""
        custom_rules = {"min_margin": 20}
        calc = PositionCalculator(rules=custom_rules)
        assert calc.rules == custom_rules


class TestEnsureBounds:
    """Test ensure_bounds function."""
    
    def test_valid_position(self):
        """Test that valid positions are unchanged."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result == pos
    
    def test_x1_out_of_bounds(self):
        """Test correction of x1 below minimum."""
        calc = PositionCalculator()
        pos = (-10.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result[0] >= POSITIONING_RULES["min_margin"]
    
    def test_y1_out_of_bounds(self):
        """Test correction of y1 below minimum."""
        calc = PositionCalculator()
        pos = (50.0, -10.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result[1] >= POSITIONING_RULES["min_margin"]
    
    def test_x2_out_of_bounds(self):
        """Test correction of x2 above maximum."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 700.0, 100.0)
        result = calc.ensure_bounds(pos)
        max_x = POSITIONING_RULES["page_width"] - POSITIONING_RULES["min_margin"]
        assert result[2] <= max_x
    
    def test_y2_out_of_bounds(self):
        """Test correction of y2 above maximum."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 200.0, 900.0)
        result = calc.ensure_bounds(pos)
        max_y = POSITIONING_RULES["page_height"] - POSITIONING_RULES["min_margin"]
        assert result[3] <= max_y
    
    def test_all_bounds_out(self):
        """Test correction when all bounds are out."""
        calc = PositionCalculator()
        pos = (-10.0, -10.0, 700.0, 900.0)
        result = calc.ensure_bounds(pos)
        
        min_margin = POSITIONING_RULES["min_margin"]
        max_x = POSITIONING_RULES["page_width"] - min_margin
        max_y = POSITIONING_RULES["page_height"] - min_margin
        
        assert result[0] >= min_margin
        assert result[1] >= min_margin
        assert result[2] <= max_x
        assert result[3] <= max_y
    
    def test_maintains_positive_dimensions(self):
        """Test that adjusted positions have positive dimensions."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        
        assert result[2] > result[0]  # width > 0
        assert result[3] > result[1]  # height > 0


class TestCheckCollisions:
    """Test collision detection."""
    
    def test_no_collisions(self):
        """Test positions with no collisions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (200.0, 200.0, 300.0, 250.0),
            (400.0, 400.0, 500.0, 450.0),
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) == 0
    
    def test_two_collisions(self):
        """Test detection of overlapping positions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0),  # Overlaps with first
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) == 1
        assert collisions[0].element1_index == 0
        assert collisions[0].element2_index == 1
        assert collisions[0].overlap_area > 0
    
    def test_multiple_collisions(self):
        """Test detection of multiple collisions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0),  # Overlaps with first
            (125.0, 90.0, 225.0, 140.0),  # Overlaps with second
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) >= 1  # At least one collision
    
    def test_adjacent_no_collision(self):
        """Test that adjacent positions don't collide."""
        calc = PositionCalculator()
        spacing = POSITIONING_RULES["min_spacing"]
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (150.0 + spacing + 1, 50.0, 250.0, 100.0),  # Just beyond spacing
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) == 0
    
    def test_collision_info(self):
        """Test collision info contains correct data."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0),
        ]
        collisions = calc.check_collisions(positions)
        
        assert len(collisions) == 1
        collision = collisions[0]
        assert isinstance(collision, CollisionInfo)
        assert collision.element1_index == 0
        assert collision.element2_index == 1
        assert collision.overlap_area > 0


class TestCalculatePositions:
    """Test position calculation."""
    
    def create_test_elements(self, count: int = 5) -> list:
        """Create test YML elements."""
        elements = []
        for i in range(count):
            elem = YMLElement(
                text=f"Test Element {i}",
                position=(50.0 + i * 10, 50.0, 150.0 + i * 10, 100.0),
                font="Helvetica",
                font_size=12.0,
                color=0,
                index=i
            )
            elements.append(elem)
        return elements
    
    def create_test_analysis(self) -> PDFAnalysis:
        """Create test PDF analysis."""
        return PDFAnalysis(
            firma=1,
            seite=1,
            page_size={"width": 595, "height": 842},
            design_regions=[],
            visual_elements=[],
            safe_zones=[
                SafeZone(x1=50, y1=50, x2=545, y2=792)
            ],
            color_palette=["#007BFF", "#FFFFFF"]
        )
    
    def test_calculate_positions_basic(self):
        """Test basic position calculation."""
        calc = PositionCalculator()
        elements = self.create_test_elements(3)
        analysis = self.create_test_analysis()
        
        positions = calc.calculate_positions(elements, analysis)
        
        assert len(positions) == len(elements)
        assert all(isinstance(pos, tuple) for pos in positions)
        assert all(len(pos) == 4 for pos in positions)
    
    def test_calculate_positions_grid(self):
        """Test grid-based positioning."""
        calc = PositionCalculator()
        elements = self.create_test_elements(9)
        analysis = self.create_test_analysis()
        
        positions = calc.calculate_positions(elements, analysis, strategy="grid")
        
        assert len(positions) == len(elements)
        
        # All positions should be within bounds
        for pos in positions:
            x1, y1, x2, y2 = pos
            assert x1 >= POSITIONING_RULES["min_margin"]
            assert y1 >= POSITIONING_RULES["min_margin"]
            assert x2 <= POSITIONING_RULES["page_width"] - POSITIONING_RULES["min_margin"]
            assert y2 <= POSITIONING_RULES["page_height"] - POSITIONING_RULES["min_margin"]
    
    def test_calculate_positions_empty(self):
        """Test with empty element list."""
        calc = PositionCalculator()
        analysis = self.create_test_analysis()
        
        positions = calc.calculate_positions([], analysis)
        
        assert positions == []
    
    def test_calculate_positions_single(self):
        """Test with single element."""
        calc = PositionCalculator()
        elements = self.create_test_elements(1)
        analysis = self.create_test_analysis()
        
        positions = calc.calculate_positions(elements, analysis)
        
        assert len(positions) == 1


class TestGetElementImportance:
    """Test element importance calculation."""
    
    def test_known_important_element(self):
        """Test importance of known important elements."""
        calc = PositionCalculator()
        elem = YMLElement(
            text="ANGEBOT",
            position=(50.0, 50.0, 150.0, 100.0),
            font="Helvetica-Bold",
            font_size=20.0,
            color=0,
            index=0
        )
        
        importance = calc.get_element_importance(elem)
        assert importance == POSITIONING_RULES["importance_weights"]["ANGEBOT"]
    
    def test_unknown_element(self):
        """Test importance of unknown elements."""
        calc = PositionCalculator()
        elem = YMLElement(
            text="Unknown Text",
            position=(50.0, 50.0, 150.0, 100.0),
            font="Helvetica",
            font_size=12.0,
            color=0,
            index=0
        )
        
        importance = calc.get_element_importance(elem)
        assert importance == POSITIONING_RULES["default_importance"]
    
    def test_partial_match(self):
        """Test importance with partial text match."""
        calc = PositionCalculator()
        elem = YMLElement(
            text="kunde_vorname_und_nachname",
            position=(50.0, 50.0, 150.0, 100.0),
            font="Helvetica",
            font_size=12.0,
            color=0,
            index=0
        )
        
        importance = calc.get_element_importance(elem)
        expected = POSITIONING_RULES["importance_weights"]["kunde_vorname_und_nachname"]
        assert importance == expected


class TestValidatePositions:
    """Test position validation."""
    
    def test_valid_positions(self):
        """Test validation of valid positions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (200.0, 200.0, 300.0, 250.0),
        ]
        
        is_valid, errors = calc.validate_positions(positions)
        assert is_valid
        assert len(errors) == 0
    
    def test_invalid_x1(self):
        """Test validation catches invalid x1."""
        calc = PositionCalculator()
        positions = [
            (5.0, 50.0, 150.0, 100.0),  # x1 < min_margin
        ]
        
        is_valid, errors = calc.validate_positions(positions)
        assert not is_valid
        assert len(errors) > 0
    
    def test_invalid_dimensions(self):
        """Test validation catches invalid dimensions."""
        calc = PositionCalculator()
        positions = [
            (150.0, 50.0, 100.0, 100.0),  # x2 < x1
        ]
        
        is_valid, errors = calc.validate_positions(positions)
        assert not is_valid
        assert len(errors) > 0
    
    def test_collision_detected(self):
        """Test validation detects collisions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0),  # Overlaps
        ]
        
        is_valid, errors = calc.validate_positions(positions)
        assert not is_valid
        assert any("collision" in err.lower() for err in errors)


class TestConvenienceFunction:
    """Test convenience function."""
    
    def test_calculate_positions_function(self):
        """Test the convenience function."""
        elements = [
            YMLElement(
                text="Test",
                position=(50.0, 50.0, 150.0, 100.0),
                font="Helvetica",
                font_size=12.0,
                color=0,
                index=0
            )
        ]
        
        analysis = PDFAnalysis(
            firma=1,
            seite=1,
            page_size={"width": 595, "height": 842},
            design_regions=[],
            visual_elements=[],
            safe_zones=[],
            color_palette=[]
        )
        
        positions = calculate_positions(elements, analysis)
        
        assert len(positions) == 1
        assert isinstance(positions[0], tuple)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
