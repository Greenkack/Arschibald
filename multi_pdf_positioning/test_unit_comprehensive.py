"""
Comprehensive Unit Test Suite for Multi-PDF Positioning System

This test suite provides comprehensive coverage of all core modules:
- YML Parser
- PDF Analyzer
- Position Calculator
- YML Generator

Goal: Achieve 80%+ code coverage
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List

# Import modules to test
from multi_pdf_positioning.yml_parser import (
    YMLParser, YMLElement, parse_yml
)
from multi_pdf_positioning.pdf_analyzer import (
    PDFAnalyzer, PDFAnalysis, DesignRegion, SafeZone, analyze_pdf
)
from multi_pdf_positioning.position_calculator import (
    PositionCalculator, POSITIONING_RULES, CollisionInfo, calculate_positions
)
from multi_pdf_positioning.yml_generator import (
    YMLGenerator, generate_yml, validate_yml_output
)


# ============================================================================
# YML PARSER TESTS
# ============================================================================

class TestYMLParser:
    """Comprehensive tests for YML Parser."""
    
    @pytest.fixture
    def sample_yml_content(self):
        """Create sample YML content for testing."""
        return """Text: ERSTELLT FÜR:
Position: (48.0, 70.0, 220.0, 87.0)
Schriftart: Helvetica-Bold
Schriftgröße: 20.0
Farbe: 30920
----------------------------------------
Text: kunde_vorname_und_nachname
Position: (90.0, 87.0, 220.0, 105.0)
Schriftart: Helvetica-Bold
Schriftgröße: 14.0
Farbe: 3487029
----------------------------------------
Text: PHOTOVOLTAIK
Position: (48.0, 120.0, 250.0, 140.0)
Schriftart: Helvetica-Bold
Schriftgröße: 24.0
Farbe: 30920
----------------------------------------
"""
    
    @pytest.fixture
    def temp_yml_file(self, sample_yml_content):
        """Create a temporary YML file."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.yml', delete=False, encoding='utf-8'
        )
        temp_file.write(sample_yml_content)
        temp_file.close()
        yield temp_file.name
        Path(temp_file.name).unlink()
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = YMLParser()
        assert parser.elements == []
        assert parser.raw_content == ""
        assert parser.file_path is None
    
    def test_parse_yml_basic(self, temp_yml_file):
        """Test basic YML parsing."""
        parser = YMLParser()
        elements = parser.parse_yml(temp_yml_file)
        
        assert len(elements) == 3
        assert all(isinstance(e, YMLElement) for e in elements)
    
    def test_parse_yml_file_not_found(self):
        """Test error handling for missing file."""
        parser = YMLParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_yml("nonexistent_file.yml")
    
    def test_element_attributes(self, temp_yml_file):
        """Test that all element attributes are parsed correctly."""
        parser = YMLParser()
        elements = parser.parse_yml(temp_yml_file)
        
        first_elem = elements[0]
        assert first_elem.text == "ERSTELLT FÜR:"
        assert first_elem.position == (48.0, 70.0, 220.0, 87.0)
        assert first_elem.font == "Helvetica-Bold"
        assert first_elem.font_size == 20.0
        assert first_elem.color == 30920
        assert first_elem.index == 0
    
    def test_element_ordering(self, temp_yml_file):
        """Test that elements maintain correct order."""
        parser = YMLParser()
        elements = parser.parse_yml(temp_yml_file)
        
        for i, elem in enumerate(elements):
            assert elem.index == i
    
    def test_get_element_by_text(self, temp_yml_file):
        """Test finding elements by text."""
        parser = YMLParser()
        parser.parse_yml(temp_yml_file)
        
        elem = parser.get_element_by_text("PHOTOVOLTAIK")
        assert elem is not None
        assert elem.text == "PHOTOVOLTAIK"
        
        not_found = parser.get_element_by_text("NONEXISTENT")
        assert not_found is None
    
    def test_get_elements_by_font(self, temp_yml_file):
        """Test finding elements by font."""
        parser = YMLParser()
        parser.parse_yml(temp_yml_file)
        
        bold_elements = parser.get_elements_by_font("Helvetica-Bold")
        assert len(bold_elements) == 3
    
    def test_get_non_empty_elements(self, temp_yml_file):
        """Test filtering non-empty elements."""
        parser = YMLParser()
        parser.parse_yml(temp_yml_file)
        
        non_empty = parser.get_non_empty_elements()
        assert len(non_empty) == 3
        assert all(elem.text.strip() for elem in non_empty)
    
    def test_validate_elements_success(self, temp_yml_file):
        """Test validation of valid elements."""
        parser = YMLParser()
        parser.parse_yml(temp_yml_file)
        
        is_valid, errors = parser.validate_elements()
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_elements_invalid_position(self):
        """Test validation catches invalid positions."""
        parser = YMLParser()
        parser.elements = [
            YMLElement(
                text="Test",
                position=(600.0, 70.0, 700.0, 87.0),  # x > 595
                font="Helvetica",
                font_size=12.0,
                color=0,
                index=0
            )
        ]
        
        is_valid, errors = parser.validate_elements()
        assert not is_valid
        assert len(errors) > 0
    
    def test_get_statistics(self, temp_yml_file):
        """Test statistics generation."""
        parser = YMLParser()
        parser.parse_yml(temp_yml_file)
        
        stats = parser.get_statistics()
        assert stats["total_elements"] == 3
        assert stats["non_empty_elements"] == 3
        assert stats["unique_fonts"] == 1
        assert stats["unique_colors"] == 2
    
    def test_convenience_function(self, temp_yml_file):
        """Test parse_yml convenience function."""
        elements = parse_yml(temp_yml_file)
        assert len(elements) == 3


# ============================================================================
# PDF ANALYZER TESTS
# ============================================================================

class TestPDFAnalyzer:
    """Comprehensive tests for PDF Analyzer."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = PDFAnalyzer()
        assert analyzer.analysis_results == []
        assert analyzer.pdf_dir is None
    
    def test_analyzer_with_directory(self):
        """Test analyzer initialization with directory."""
        analyzer = PDFAnalyzer(pdf_dir="test_dir")
        assert analyzer.pdf_dir == Path("test_dir")
    
    def test_extract_color_palette(self):
        """Test color palette extraction."""
        analyzer = PDFAnalyzer()
        
        # Test different firmen have different palettes
        palette1 = analyzer._extract_color_palette("dummy.pdf", 1, 1)
        palette2 = analyzer._extract_color_palette("dummy.pdf", 2, 1)
        
        assert palette1 != palette2
        assert len(palette1) > 0
        assert all(color.startswith("#") for color in palette1)
    
    def test_design_regions_structure(self):
        """Test design region structure."""
        analyzer = PDFAnalyzer()
        page_size = {"width": 595, "height": 842}
        color_palette = ["#007BFF", "#FFFFFF", "#F8F9FA", "#000000"]
        
        regions = analyzer._analyze_design_regions(
            page_size, 1, 1, color_palette
        )
        
        assert len(regions) > 0
        assert all(isinstance(r, DesignRegion) for r in regions)
        
        # Check region types
        region_types = [r.type for r in regions]
        assert "header" in region_types or "content" in region_types
    
    def test_safe_zones_creation(self):
        """Test safe zone creation."""
        analyzer = PDFAnalyzer()
        page_size = {"width": 595, "height": 842}
        
        # Create mock design regions
        regions = [
            DesignRegion(
                type="content",
                bounds={"x1": 0, "y1": 100, "x2": 595, "y2": 742},
                dominant_color="#FFFFFF",
                suggested_text_color="#000000"
            )
        ]
        
        safe_zones = analyzer._define_safe_zones(page_size, regions)
        
        assert len(safe_zones) > 0
        assert all(isinstance(z, SafeZone) for z in safe_zones)
        
        # Check safe zones have positive dimensions
        for zone in safe_zones:
            assert zone.x2 > zone.x1
            assert zone.y2 > zone.y1
    
    def test_get_analysis_by_firma(self):
        """Test filtering analyses by firma."""
        analyzer = PDFAnalyzer()
        
        # Add mock analyses
        analyzer.analysis_results = [
            PDFAnalysis(
                firma=1, seite=1, page_size={"width": 595, "height": 842},
                design_regions=[], visual_elements=[], safe_zones=[],
                color_palette=[]
            ),
            PDFAnalysis(
                firma=2, seite=1, page_size={"width": 595, "height": 842},
                design_regions=[], visual_elements=[], safe_zones=[],
                color_palette=[]
            ),
            PDFAnalysis(
                firma=1, seite=2, page_size={"width": 595, "height": 842},
                design_regions=[], visual_elements=[], safe_zones=[],
                color_palette=[]
            )
        ]
        
        firma1_results = analyzer.get_analysis_by_firma(1)
        assert len(firma1_results) == 2
        assert all(a.firma == 1 for a in firma1_results)
    
    def test_get_analysis_by_seite(self):
        """Test filtering analyses by seite."""
        analyzer = PDFAnalyzer()
        
        # Add mock analyses
        analyzer.analysis_results = [
            PDFAnalysis(
                firma=1, seite=1, page_size={"width": 595, "height": 842},
                design_regions=[], visual_elements=[], safe_zones=[],
                color_palette=[]
            ),
            PDFAnalysis(
                firma=2, seite=1, page_size={"width": 595, "height": 842},
                design_regions=[], visual_elements=[], safe_zones=[],
                color_palette=[]
            )
        ]
        
        seite1_results = analyzer.get_analysis_by_seite(1)
        assert len(seite1_results) == 2
        assert all(a.seite == 1 for a in seite1_results)


# ============================================================================
# POSITION CALCULATOR TESTS
# ============================================================================

class TestPositionCalculator:
    """Comprehensive tests for Position Calculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initialization."""
        calc = PositionCalculator()
        assert calc.rules == POSITIONING_RULES
        assert calc.collisions == []
    
    def test_custom_rules(self):
        """Test calculator with custom rules."""
        custom_rules = {"min_margin": 20, "min_spacing": 10}
        calc = PositionCalculator(rules=custom_rules)
        assert calc.rules == custom_rules
    
    def test_ensure_bounds_valid(self):
        """Test ensure_bounds with valid position."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result == pos
    
    def test_ensure_bounds_x1_negative(self):
        """Test ensure_bounds corrects negative x1."""
        calc = PositionCalculator()
        pos = (-10.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result[0] >= POSITIONING_RULES["min_margin"]
    
    def test_ensure_bounds_x2_exceeds(self):
        """Test ensure_bounds corrects x2 exceeding page width."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 700.0, 100.0)
        result = calc.ensure_bounds(pos)
        max_x = POSITIONING_RULES["page_width"] - POSITIONING_RULES["min_margin"]
        assert result[2] <= max_x
    
    def test_ensure_bounds_maintains_dimensions(self):
        """Test that ensure_bounds maintains positive dimensions."""
        calc = PositionCalculator()
        pos = (50.0, 50.0, 200.0, 100.0)
        result = calc.ensure_bounds(pos)
        assert result[2] > result[0]
        assert result[3] > result[1]
    
    def test_check_collisions_none(self):
        """Test collision detection with no collisions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (200.0, 200.0, 300.0, 250.0)
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) == 0
    
    def test_check_collisions_detected(self):
        """Test collision detection finds overlaps."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0)  # Overlaps
        ]
        collisions = calc.check_collisions(positions)
        assert len(collisions) == 1
        assert isinstance(collisions[0], CollisionInfo)
    
    def test_rectangles_overlap_true(self):
        """Test rectangle overlap detection."""
        calc = PositionCalculator()
        rect1 = (50.0, 50.0, 150.0, 100.0)
        rect2 = (100.0, 75.0, 200.0, 125.0)
        assert calc._rectangles_overlap(rect1, rect2)
    
    def test_rectangles_overlap_false(self):
        """Test rectangle non-overlap detection."""
        calc = PositionCalculator()
        rect1 = (50.0, 50.0, 150.0, 100.0)
        rect2 = (200.0, 200.0, 300.0, 250.0)
        assert not calc._rectangles_overlap(rect1, rect2)
    
    def test_calculate_overlap_area(self):
        """Test overlap area calculation."""
        calc = PositionCalculator()
        rect1 = (50.0, 50.0, 150.0, 100.0)
        rect2 = (100.0, 75.0, 200.0, 125.0)
        area = calc._calculate_overlap_area(rect1, rect2)
        assert area > 0
    
    def test_calculate_overlap_area_no_overlap(self):
        """Test overlap area is zero for non-overlapping rectangles."""
        calc = PositionCalculator()
        rect1 = (50.0, 50.0, 150.0, 100.0)
        rect2 = (200.0, 200.0, 300.0, 250.0)
        area = calc._calculate_overlap_area(rect1, rect2)
        assert area == 0.0
    
    def test_get_element_importance_known(self):
        """Test importance for known elements."""
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
    
    def test_get_element_importance_unknown(self):
        """Test importance for unknown elements."""
        calc = PositionCalculator()
        elem = YMLElement(
            text="Unknown Element",
            position=(50.0, 50.0, 150.0, 100.0),
            font="Helvetica",
            font_size=12.0,
            color=0,
            index=0
        )
        importance = calc.get_element_importance(elem)
        assert importance == POSITIONING_RULES["default_importance"]
    
    def test_validate_positions_valid(self):
        """Test validation of valid positions."""
        calc = PositionCalculator()
        positions = [
            (50.0, 50.0, 150.0, 100.0),
            (200.0, 200.0, 300.0, 250.0)
        ]
        is_valid, errors = calc.validate_positions(positions)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_positions_invalid_bounds(self):
        """Test validation catches invalid bounds."""
        calc = PositionCalculator()
        positions = [
            (5.0, 50.0, 150.0, 100.0)  # x1 < min_margin
        ]
        is_valid, errors = calc.validate_positions(positions)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_positions_invalid_dimensions(self):
        """Test validation catches invalid dimensions."""
        calc = PositionCalculator()
        positions = [
            (150.0, 50.0, 100.0, 100.0)  # x2 < x1
        ]
        is_valid, errors = calc.validate_positions(positions)
        assert not is_valid
        assert len(errors) > 0
    
    def test_grid_based_positioning(self):
        """Test grid-based positioning fallback."""
        calc = PositionCalculator()
        
        elements = [
            YMLElement(
                text=f"Element {i}",
                position=(50.0, 50.0, 150.0, 100.0),
                font="Helvetica",
                font_size=12.0,
                color=0,
                index=i
            )
            for i in range(5)
        ]
        
        analysis = PDFAnalysis(
            firma=1, seite=1,
            page_size={"width": 595, "height": 842},
            design_regions=[], visual_elements=[], safe_zones=[],
            color_palette=[]
        )
        
        positions = calc._grid_based_positioning(elements, analysis)
        
        assert len(positions) == len(elements)
        assert all(isinstance(p, tuple) for p in positions)
        assert all(len(p) == 4 for p in positions)


# ============================================================================
# YML GENERATOR TESTS
# ============================================================================

class TestYMLGenerator:
    """Comprehensive tests for YML Generator."""
    
    @pytest.fixture
    def sample_elements(self):
        """Create sample elements for testing."""
        return [
            YMLElement(
                text="ERSTELLT FÜR:",
                position=(48.0, 70.0, 220.0, 87.0),
                font="Helvetica-Bold",
                font_size=20.0,
                color=30920,
                index=0
            ),
            YMLElement(
                text="PHOTOVOLTAIK",
                position=(48.0, 120.0, 250.0, 140.0),
                font="Helvetica-Bold",
                font_size=24.0,
                color=30920,
                index=1
            )
        ]
    
    @pytest.fixture
    def new_positions(self):
        """Create new positions for testing."""
        return [
            (50.0, 75.0, 225.0, 92.0),
            (50.0, 125.0, 255.0, 145.0)
        ]
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        gen = YMLGenerator()
        assert gen.format_preserver is None
        assert gen.original_elements == []
        assert gen.validation_errors == []
    
    def test_format_position(self):
        """Test position formatting."""
        gen = YMLGenerator()
        result = gen.format_position(48.0, 70.0, 220.0, 87.0)
        assert result == "(48.0, 70.0, 220.0, 87.0)"
    
    def test_generate_yml_basic(self, sample_elements, new_positions, temp_dir):
        """Test basic YML generation."""
        gen = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        
        content = gen.generate_yml(
            sample_elements, new_positions, str(output_path)
        )
        
        assert output_path.exists()
        assert len(content) > 0
        assert "ERSTELLT FÜR:" in content
        assert "PHOTOVOLTAIK" in content
    
    def test_generate_yml_mismatch_error(self, sample_elements, temp_dir):
        """Test error on element/position count mismatch."""
        gen = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        wrong_positions = [(50.0, 75.0, 225.0, 92.0)]  # Only 1 position
        
        with pytest.raises(ValueError, match="Mismatch"):
            gen.generate_yml(sample_elements, wrong_positions, str(output_path))
    
    def test_validate_yml_output_success(
        self, sample_elements, new_positions, temp_dir
    ):
        """Test validation of correctly generated YML."""
        gen = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        
        gen.generate_yml(sample_elements, new_positions, str(output_path))
        is_valid, errors = gen.validate_yml_output(
            str(output_path), sample_elements
        )
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_yml_output_invalid_bounds(
        self, sample_elements, temp_dir
    ):
        """Test validation detects invalid bounds."""
        gen = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        
        invalid_positions = [
            (600.0, 75.0, 700.0, 92.0),  # x2 > 595
            (50.0, 850.0, 150.0, 900.0)  # y2 > 842
        ]
        
        gen.generate_yml(sample_elements, invalid_positions, str(output_path))
        is_valid, errors = gen.validate_yml_output(
            str(output_path), sample_elements
        )
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_get_validation_report(
        self, sample_elements, new_positions, temp_dir
    ):
        """Test validation report generation."""
        gen = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        
        gen.generate_yml(sample_elements, new_positions, str(output_path))
        gen.validate_yml_output(str(output_path), sample_elements)
        
        report = gen.get_validation_report()
        
        assert "is_valid" in report
        assert "error_count" in report
        assert "errors" in report
        assert "original_element_count" in report
    
    def test_convenience_function_generate(
        self, sample_elements, new_positions, temp_dir
    ):
        """Test generate_yml convenience function."""
        output_path = Path(temp_dir) / "test.yml"
        
        content = generate_yml(
            sample_elements, new_positions, str(output_path)
        )
        
        assert output_path.exists()
        assert len(content) > 0
    
    def test_convenience_function_validate(
        self, sample_elements, new_positions, temp_dir
    ):
        """Test validate_yml_output convenience function."""
        output_path = Path(temp_dir) / "test.yml"
        
        generate_yml(sample_elements, new_positions, str(output_path))
        is_valid, errors = validate_yml_output(
            str(output_path), sample_elements
        )
        
        assert is_valid
        assert len(errors) == 0


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short", "--cov=multi_pdf_positioning",
                 "--cov-report=term-missing", "--cov-report=html"])
