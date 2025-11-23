"""
Tests for Standard PV PDF Service

Author: Kiro AI
Date: 2025-01-22
"""

import pytest
import os
from pathlib import Path
from io import BytesIO

from services.standard_pv_pdf_service import (
    YMLCoordinateParser,
    TemplateLoader,
    PlaceholderSystem,
    PositioningEngine,
    StandardPVPDFService
)


class TestYMLCoordinateParser:
    """Tests for YML coordinate parser"""
    
    def test_parse_yml_file_success(self, tmp_path):
        """Test successful parsing of YML file"""
        # Create a test YML file
        yml_content = """Text: ERSTELLT FÜR:
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
----------------------------------------"""
        
        yml_file = tmp_path / "test.yml"
        yml_file.write_text(yml_content, encoding='utf-8')
        
        # Parse the file
        elements = YMLCoordinateParser.parse_yml_file(str(yml_file))
        
        # Verify results
        assert len(elements) == 2
        assert elements[0]['text'] == 'ERSTELLT FÜR:'
        assert elements[0]['font'] == 'Helvetica-Bold'
        assert elements[0]['font_size'] == 20.0
        assert elements[0]['position']['x'] == 48.0
        assert elements[1]['text'] == 'kunde_vorname_und_nachname'
    
    def test_parse_yml_file_not_found(self):
        """Test parsing non-existent file"""
        elements = YMLCoordinateParser.parse_yml_file("nonexistent.yml")
        assert elements == []
    
    def test_color_int_to_hex(self):
        """Test color conversion"""
        # Test black
        assert YMLCoordinateParser.color_int_to_hex(0) == '#000000'
        
        # Test white
        assert YMLCoordinateParser.color_int_to_hex(16777215) == '#FFFFFF'
        
        # Test red
        assert YMLCoordinateParser.color_int_to_hex(16711680) == '#FF0000'
        
        # Test custom color
        hex_color = YMLCoordinateParser.color_int_to_hex(3487029)
        assert hex_color.startswith('#')
        assert len(hex_color) == 7


class TestTemplateLoader:
    """Tests for template loader"""
    
    def test_load_template_success(self, tmp_path):
        """Test successful template loading"""
        # Create a mock template directory
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        # Create a mock PDF file
        template_file = template_dir / "nt_nt_01.pdf"
        template_file.write_bytes(b'%PDF-1.4\nMock PDF content')
        
        # Load template
        loader = TemplateLoader(str(template_dir))
        template_bytes = loader.load_template(1)
        
        assert template_bytes is not None
        assert b'PDF' in template_bytes
    
    def test_load_template_not_found(self, tmp_path):
        """Test loading non-existent template"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        loader = TemplateLoader(str(template_dir))
        template_bytes = loader.load_template(1)
        
        assert template_bytes is None
    
    def test_get_all_templates(self, tmp_path):
        """Test loading all templates"""
        # Create mock templates
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        for i in range(1, 9):
            template_file = template_dir / f"nt_nt_{i:02d}.pdf"
            template_file.write_bytes(b'%PDF-1.4\nMock PDF content')
        
        # Load all templates
        loader = TemplateLoader(str(template_dir))
        templates = loader.get_all_templates()
        
        assert len(templates) == 8
        assert all(i in templates for i in range(1, 9))


class TestPlaceholderSystem:
    """Tests for placeholder system"""
    
    def test_is_dynamic_placeholder(self):
        """Test dynamic placeholder detection"""
        assert PlaceholderSystem.is_dynamic_placeholder('anrede_kunde')
        assert PlaceholderSystem.is_dynamic_placeholder('kunde_vorname_und_nachname')
        assert not PlaceholderSystem.is_dynamic_placeholder('ERSTELLT FÜR:')
        assert not PlaceholderSystem.is_dynamic_placeholder('random_text')
    
    def test_is_static_placeholder(self):
        """Test static placeholder detection"""
        assert PlaceholderSystem.is_static_placeholder('ERSTELLT FÜR:')
        assert PlaceholderSystem.is_static_placeholder('PHOTOVOLTAIK')
        assert not PlaceholderSystem.is_static_placeholder('anrede_kunde')
    
    def test_replace_placeholder(self):
        """Test placeholder replacement"""
        data = {
            'anrede_kunde': 'Herr',
            'kunde_vorname_und_nachname': 'Max Mustermann'
        }
        
        # Test successful replacement
        result = PlaceholderSystem.replace_placeholder('anrede_kunde', data)
        assert result == 'Herr'
        
        # Test missing placeholder
        result = PlaceholderSystem.replace_placeholder('missing_key', data)
        assert result == 'missing_key'


class TestPositioningEngine:
    """Tests for positioning engine"""
    
    def test_create_overlay(self):
        """Test overlay creation"""
        engine = PositioningEngine()
        
        elements = [
            {
                'text': 'Test Text',
                'position': {'x': 100, 'y': 100, 'x2': 200, 'y2': 120},
                'font': 'Helvetica',
                'font_size': 12,
                'color': 0
            }
        ]
        
        data = {}
        
        overlay_bytes = engine.create_overlay(elements, data)
        
        # Verify overlay was created
        assert overlay_bytes is not None
        assert len(overlay_bytes) > 0
        assert b'PDF' in overlay_bytes
    
    def test_create_overlay_with_dynamic_placeholder(self):
        """Test overlay creation with dynamic placeholder"""
        engine = PositioningEngine()
        
        elements = [
            {
                'text': 'anrede_kunde',
                'position': {'x': 100, 'y': 100, 'x2': 200, 'y2': 120},
                'font': 'Helvetica',
                'font_size': 12,
                'color': 0
            }
        ]
        
        data = {'anrede_kunde': 'Herr'}
        
        overlay_bytes = engine.create_overlay(elements, data)
        
        assert overlay_bytes is not None
        assert len(overlay_bytes) > 0


class TestStandardPVPDFService:
    """Tests for main PDF service"""
    
    def test_format_german_currency(self):
        """Test German currency formatting"""
        # Test standard amount
        result = StandardPVPDFService._format_german_currency(16999.00)
        assert result == "16.999,00 €"
        
        # Test amount with cents
        result = StandardPVPDFService._format_german_currency(1234.56)
        assert result == "1.234,56 €"
        
        # Test small amount
        result = StandardPVPDFService._format_german_currency(99.99)
        assert result == "99,99 €"
        
        # Test large amount
        result = StandardPVPDFService._format_german_currency(123456.78)
        assert result == "123.456,78 €"
    
    def test_service_initialization(self, tmp_path):
        """Test service initialization"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        coords_dir = tmp_path / "coords"
        coords_dir.mkdir()
        
        service = StandardPVPDFService(
            template_dir=str(template_dir),
            coords_dir=str(coords_dir)
        )
        
        assert service.template_loader is not None
        assert service.positioning_engine is not None
        assert service.coords_dir == coords_dir
    
    def test_load_page_coordinates(self, tmp_path):
        """Test loading page coordinates"""
        coords_dir = tmp_path / "coords"
        coords_dir.mkdir()
        
        # Create a test coordinate file
        yml_content = """Text: Test
Position: (100.0, 100.0, 200.0, 120.0)
Schriftart: Helvetica
Schriftgröße: 12.0
Farbe: 0
----------------------------------------"""
        
        yml_file = coords_dir / "seite1.yml"
        yml_file.write_text(yml_content, encoding='utf-8')
        
        service = StandardPVPDFService(coords_dir=str(coords_dir))
        elements = service.load_page_coordinates(1)
        
        assert len(elements) == 1
        assert elements[0]['text'] == 'Test'
    
    def test_generate_page_without_template(self, tmp_path):
        """Test page generation when template is missing"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        coords_dir = tmp_path / "coords"
        coords_dir.mkdir()
        
        service = StandardPVPDFService(
            template_dir=str(template_dir),
            coords_dir=str(coords_dir)
        )
        
        data = {'test_key': 'test_value'}
        page_bytes = service.generate_page(1, data)
        
        assert page_bytes is None


# Integration tests
class TestStandardPVPDFServiceIntegration:
    """Integration tests for PDF service"""
    
    @pytest.mark.skipif(
        not os.path.exists("pdf_templates_static/notext/nt_nt_01.pdf"),
        reason="Template files not available"
    )
    def test_generate_complete_pdf_with_real_templates(self):
        """Test PDF generation with real templates (if available)"""
        service = StandardPVPDFService()
        
        data = {
            'anrede_kunde': 'Herr',
            'kunde_vorname_und_nachname': 'Max Mustermann',
            'kunde_wohnort': 'Berlin',
            'kWp_anlage_anlage': '10,5 kWp',
            'langes_datum_heute': '22. Januar 2025',
            'total_price': 16999.00
        }
        
        pdf_bytes = service.generate_complete_pdf(data, include_pages=[1])
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert b'PDF' in pdf_bytes
    
    @pytest.mark.skipif(
        not os.path.exists("coords/seite1.yml"),
        reason="Coordinate files not available"
    )
    def test_load_real_coordinates(self):
        """Test loading real coordinate files (if available)"""
        service = StandardPVPDFService()
        
        elements = service.load_page_coordinates(1)
        
        assert len(elements) > 0
        assert all('text' in elem for elem in elements)
        assert all('position' in elem for elem in elements)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
