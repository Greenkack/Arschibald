"""
Tests for YML Generator Module

This test suite validates the YML generator functionality including:
- YML generation with new positions
- Format preservation (separators, whitespace, indentation)
- Validation of generated files
- Batch processing
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from multi_pdf_positioning.yml_generator import (
    YMLGenerator,
    generate_yml,
    validate_yml_output
)
from multi_pdf_positioning.yml_parser import YMLParser, YMLElement


class TestYMLGenerator:
    """Test suite for YML Generator."""
    
    @pytest.fixture
    def sample_elements(self):
        """Create sample YML elements for testing."""
        return [
            YMLElement(
                text="ERSTELLT FÜR:",
                position=(48.0, 70.0, 220.0, 87.0),
                font="Helvetica-Bold",
                font_size=20.0,
                color=30920,
                index=0,
                raw_block="Text: ERSTELLT FÜR:\nPosition: (48.0, 70.0, 220.0, 87.0)\nSchriftart: Helvetica-Bold\nSchriftgröße: 20.0\nFarbe: 30920"
            ),
            YMLElement(
                text="kunde_vorname_und_nachname",
                position=(90.0, 87.0, 220.0, 105.0),
                font="Helvetica-Bold",
                font_size=14.0,
                color=3487029,
                index=1,
                raw_block="Text: kunde_vorname_und_nachname\nPosition: (90.0, 87.0, 220.0, 105.0)\nSchriftart: Helvetica-Bold\nSchriftgröße: 14.0\nFarbe: 3487029"
            ),
            YMLElement(
                text="PHOTOVOLTAIK",
                position=(48.0, 120.0, 250.0, 140.0),
                font="Helvetica-Bold",
                font_size=24.0,
                color=30920,
                index=2,
                raw_block="Text: PHOTOVOLTAIK\nPosition: (48.0, 120.0, 250.0, 140.0)\nSchriftart: Helvetica-Bold\nSchriftgröße: 24.0\nFarbe: 30920"
            )
        ]
    
    @pytest.fixture
    def new_positions(self):
        """Create new positions for testing."""
        return [
            (50.0, 75.0, 225.0, 92.0),
            (95.0, 92.0, 225.0, 110.0),
            (50.0, 125.0, 255.0, 145.0)
        ]
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_format_position(self):
        """Test position formatting."""
        generator = YMLGenerator()
        
        # Test standard position
        result = generator.format_position(48.0, 70.0, 220.0, 87.0)
        assert result == "(48.0, 70.0, 220.0, 87.0)"
        
        # Test with integers
        result = generator.format_position(50, 75, 200, 100)
        assert result == "(50, 75, 200, 100)"
        
        # Test with floats
        result = generator.format_position(48.5, 70.3, 220.7, 87.9)
        assert result == "(48.5, 70.3, 220.7, 87.9)"
    
    def test_generate_yml_basic(self, sample_elements, new_positions, temp_dir):
        """Test basic YML generation."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_output.yml"
        
        # Generate YML
        content = generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Check that file was created
        assert output_path.exists()
        
        # Check content is not empty
        assert len(content) > 0
        
        # Check that content contains expected elements
        assert "ERSTELLT FÜR:" in content
        assert "kunde_vorname_und_nachname" in content
        assert "PHOTOVOLTAIK" in content
        
        # Check that new positions are in content
        assert "(50.0, 75.0, 225.0, 92.0)" in content
        assert "(95.0, 92.0, 225.0, 110.0)" in content
        assert "(50.0, 125.0, 255.0, 145.0)" in content
    
    def test_generate_yml_preserves_attributes(self, sample_elements, new_positions, temp_dir):
        """Test that non-position attributes are preserved."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_attributes.yml"
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Parse generated file
        parser = YMLParser()
        generated_elements = parser.parse_yml(str(output_path))
        
        # Check that all attributes except position are preserved
        for orig, gen in zip(sample_elements, generated_elements):
            assert orig.text == gen.text, f"Text mismatch: {orig.text} != {gen.text}"
            assert orig.font == gen.font, f"Font mismatch: {orig.font} != {gen.font}"
            assert orig.font_size == gen.font_size, f"Font size mismatch"
            assert orig.color == gen.color, f"Color mismatch"
    
    def test_generate_yml_updates_positions(self, sample_elements, new_positions, temp_dir):
        """Test that positions are correctly updated."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_positions.yml"
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Parse generated file
        parser = YMLParser()
        generated_elements = parser.parse_yml(str(output_path))
        
        # Check that positions match new positions
        for gen, new_pos in zip(generated_elements, new_positions):
            assert gen.position == new_pos, \
                f"Position mismatch: {gen.position} != {new_pos}"
    
    def test_generate_yml_with_separator(self, sample_elements, new_positions, temp_dir):
        """Test that separators are preserved."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_separator.yml"
        
        # Generate YML
        content = generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Check that separators are present
        separator_count = content.count("----------------------------------------")
        # Should have separator between each element and at the end
        assert separator_count >= len(sample_elements), \
            f"Expected at least {len(sample_elements)} separators, found {separator_count}"
    
    def test_generate_yml_mismatch_error(self, sample_elements, temp_dir):
        """Test error handling for mismatched element/position counts."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_error.yml"
        
        # Try to generate with mismatched counts
        wrong_positions = [(50.0, 75.0, 225.0, 92.0)]  # Only 1 position for 3 elements
        
        with pytest.raises(ValueError, match="Mismatch"):
            generator.generate_yml(
                sample_elements,
                wrong_positions,
                str(output_path)
            )
    
    def test_validate_yml_output_success(self, sample_elements, new_positions, temp_dir):
        """Test validation of correctly generated YML."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_validate_success.yml"
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Validate
        is_valid, errors = generator.validate_yml_output(str(output_path), sample_elements)
        
        assert is_valid, f"Validation failed: {errors}"
        assert len(errors) == 0
    
    def test_validate_yml_output_detects_text_change(self, sample_elements, new_positions, temp_dir):
        """Test that validation detects changed text."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_validate_text.yml"
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Manually modify the file to change text
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified_content = content.replace("ERSTELLT FÜR:", "MODIFIED TEXT:")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Validate should fail
        is_valid, errors = generator.validate_yml_output(str(output_path), sample_elements)
        
        assert not is_valid
        assert any("Text changed" in error for error in errors)
    
    def test_validate_yml_output_detects_font_change(self, sample_elements, new_positions, temp_dir):
        """Test that validation detects changed font."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_validate_font.yml"
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Manually modify the file to change font
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified_content = content.replace("Helvetica-Bold", "Arial")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Validate should fail
        is_valid, errors = generator.validate_yml_output(str(output_path), sample_elements)
        
        assert not is_valid
        assert any("Font changed" in error for error in errors)
    
    def test_validate_yml_output_allows_position_change(self, sample_elements, new_positions, temp_dir):
        """Test that validation allows position changes."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_validate_position.yml"
        
        # Generate YML with new positions
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Validate should pass even though positions changed
        is_valid, errors = generator.validate_yml_output(str(output_path), sample_elements)
        
        assert is_valid, f"Validation should pass with changed positions: {errors}"
    
    def test_validate_yml_output_detects_invalid_bounds(self, sample_elements, temp_dir):
        """Test that validation detects positions outside bounds."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_validate_bounds.yml"
        
        # Create positions outside valid bounds
        invalid_positions = [
            (600.0, 75.0, 700.0, 92.0),  # x2 > 595 (page width)
            (50.0, 850.0, 150.0, 900.0),  # y2 > 842 (page height)
            (-10.0, 75.0, 100.0, 92.0)   # x1 < 0
        ]
        
        # Generate YML
        generator.generate_yml(
            sample_elements,
            invalid_positions,
            str(output_path)
        )
        
        # Validate should fail
        is_valid, errors = generator.validate_yml_output(str(output_path), sample_elements)
        
        assert not is_valid
        assert any("Invalid" in error and "coordinates" in error for error in errors)
    
    def test_get_validation_report(self, sample_elements, new_positions, temp_dir):
        """Test validation report generation."""
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test_report.yml"
        
        # Generate and validate
        generator.generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        generator.validate_yml_output(str(output_path), sample_elements)
        
        # Get report
        report = generator.get_validation_report()
        
        assert "is_valid" in report
        assert "error_count" in report
        assert "errors" in report
        assert "original_element_count" in report
        assert report["original_element_count"] == len(sample_elements)
    
    def test_preserve_formatting_with_raw_block(self, sample_elements, new_positions):
        """Test formatting preservation using raw block."""
        generator = YMLGenerator()
        
        # Test with element that has raw_block
        element = sample_elements[0]
        new_pos = new_positions[0]
        
        formatted = generator.preserve_formatting(element, new_pos)
        
        # Should contain the new position
        assert "(50.0, 75.0, 225.0, 92.0)" in formatted
        
        # Should preserve other attributes
        assert "ERSTELLT FÜR:" in formatted
        assert "Helvetica-Bold" in formatted
        assert "20.0" in formatted
        assert "30920" in formatted
    
    def test_convenience_function_generate_yml(self, sample_elements, new_positions, temp_dir):
        """Test convenience function for YML generation."""
        output_path = Path(temp_dir) / "test_convenience.yml"
        
        # Use convenience function
        content = generate_yml(
            sample_elements,
            new_positions,
            str(output_path)
        )
        
        # Check that file was created
        assert output_path.exists()
        assert len(content) > 0
    
    def test_convenience_function_validate_yml(self, sample_elements, new_positions, temp_dir):
        """Test convenience function for validation."""
        output_path = Path(temp_dir) / "test_convenience_validate.yml"
        
        # Generate YML
        generate_yml(sample_elements, new_positions, str(output_path))
        
        # Use convenience function to validate
        is_valid, errors = validate_yml_output(str(output_path), sample_elements)
        
        assert is_valid
        assert len(errors) == 0


class TestYMLGeneratorIntegration:
    """Integration tests with real YML files."""
    
    @pytest.fixture
    def real_yml_file(self):
        """Get path to a real YML file if it exists."""
        yml_path = Path("coords_multi/seite1_f1.yml")
        if yml_path.exists():
            return str(yml_path)
        return None
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_generate_from_real_file(self, real_yml_file, temp_dir):
        """Test generation from a real YML file."""
        if real_yml_file is None:
            pytest.skip("Real YML file not available")
        
        # Parse real file
        parser = YMLParser()
        elements = parser.parse_yml(real_yml_file)
        
        # Create new positions (shift by 10 points)
        new_positions = []
        for elem in elements:
            x1, y1, x2, y2 = elem.position
            new_positions.append((x1 + 10, y1 + 10, x2 + 10, y2 + 10))
        
        # Generate new YML
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "real_file_output.yml"
        
        content = generator.generate_yml(
            elements,
            new_positions,
            str(output_path),
            real_yml_file
        )
        
        # Validate
        is_valid, errors = generator.validate_yml_output(str(output_path), elements)
        
        assert is_valid, f"Validation failed: {errors}"
        assert output_path.exists()
        assert len(content) > 0
    
    def test_format_preservation_with_real_file(self, real_yml_file, temp_dir):
        """Test that format is preserved with real file."""
        if real_yml_file is None:
            pytest.skip("Real YML file not available")
        
        # Parse real file
        parser = YMLParser()
        elements = parser.parse_yml(real_yml_file)
        
        # Use same positions (no change)
        original_positions = [elem.position for elem in elements]
        
        # Generate new YML
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "format_test_output.yml"
        
        generator.generate_yml(
            elements,
            original_positions,
            str(output_path),
            real_yml_file
        )
        
        # Read both files
        with open(real_yml_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            generated_content = f.read()
        
        # Check separator count matches
        original_sep_count = original_content.count("----------------------------------------")
        generated_sep_count = generated_content.count("----------------------------------------")
        assert original_sep_count == generated_sep_count
        
        # Check line count is similar (may differ slightly due to formatting)
        original_lines = len(original_content.split('\n'))
        generated_lines = len(generated_content.split('\n'))
        assert abs(original_lines - generated_lines) <= 2  # Allow small difference


def test_module_imports():
    """Test that all module imports work."""
    from multi_pdf_positioning.yml_generator import (
        YMLGenerator,
        generate_yml,
        validate_yml_output
    )
    
    assert YMLGenerator is not None
    assert generate_yml is not None
    assert validate_yml_output is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
