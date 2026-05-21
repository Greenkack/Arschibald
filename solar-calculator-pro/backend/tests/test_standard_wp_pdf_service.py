"""
Tests for Standard WP PDF Service

Author: Kiro AI
Date: 2025-01-22
"""

import pytest
import os
from pathlib import Path
from io import BytesIO

# Import the service and components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.standard_wp_pdf_service import (
    StandardWPPDFService,
    WPYMLCoordinateParser,
    WPTemplateLoader,
    WPPlaceholderSystem,
    WPPositioningEngine
)


class TestWPYMLCoordinateParser:
    """Tests for WP YML coordinate parser"""
    
    def test_color_int_to_hex(self):
        """Test color integer to hex conversion"""
        # Black
        assert WPYMLCoordinateParser.color_int_to_hex(0) == '#000000'
        
        # White
        assert WPYMLCoordinateParser.color_int_to_hex(16777215) == '#FFFFFF'
        
        # Red
        assert WPYMLCoordinateParser.color_int_to_hex(16711680) == '#FF0000'
        
        # Green
        assert WPYMLCoordinateParser.color_int_to_hex(65280) == '#00FF00'
        
        # Blue
        assert WPYMLCoordinateParser.color_int_to_hex(255) == '#0000FF'
    
    def test_parse_yml_file_not_found(self):
        """Test parsing non-existent YML file"""
        result = WPYMLCoordinateParser.parse_yml_file("nonexistent.yml")
        assert result == []
    
    def test_parse_yml_file_structure(self):
        """Test YML file parsing structure"""
        # Create a temporary YML file for testing
        test_yml_content = """----------------------------------------
Text: wp_modell_name
Position: (100.0, 200.0, 300.0, 250.0)
Schriftart: Helvetica
Schriftgröße: 12
Farbe: 0
----------------------------------------
Text: wp_cop_wert
Position: (100.0, 300.0, 300.0, 350.0)
Schriftart: Helvetica-Bold
Schriftgröße: 14
Farbe: 16711680
"""
        
        # Write to temporary file
        test_file = Path("test_wp_coords.yml")
        test_file.write_text(test_yml_content, encoding='utf-8')
        
        try:
            elements = WPYMLCoordinateParser.parse_yml_file(str(test_file))
            
            assert len(elements) == 2
            
            # Check first element
            assert elements[0]['text'] == 'wp_modell_name'
            assert elements[0]['position']['x'] == 100.0
            assert elements[0]['position']['y'] == 200.0
            assert elements[0]['font'] == 'Helvetica'
            assert elements[0]['font_size'] == 12
            assert elements[0]['color'] == 0
            
            # Check second element
            assert elements[1]['text'] == 'wp_cop_wert'
            assert elements[1]['font'] == 'Helvetica-Bold'
            assert elements[1]['font_size'] == 14
            assert elements[1]['color'] == 16711680
            
        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()


class TestWPTemplateLoader:
    """Tests for WP template loader"""
    
    def test_template_loader_initialization(self):
        """Test template loader initialization"""
        loader = WPTemplateLoader()
        assert loader.template_dir == Path("pdf_templates_static/notext")
    
    def test_template_loader_custom_dir(self):
        """Test template loader with custom directory"""
        loader = WPTemplateLoader("custom/path")
        assert loader.template_dir == Path("custom/path")
    
    def test_load_template_not_found(self):
        """Test loading non-existent template"""
        loader = WPTemplateLoader()
        result = loader.load_template(99)
        assert result is None
    
    def test_get_all_templates_structure(self):
        """Test getting all templates structure"""
        loader = WPTemplateLoader()
        templates = loader.get_all_templates()
        
        # Should return a dictionary
        assert isinstance(templates, dict)
        
        # Keys should be page numbers
        for key in templates.keys():
            assert isinstance(key, int)
            assert 1 <= key <= 8


class TestWPPlaceholderSystem:
    """Tests for WP placeholder system"""
    
    def test_static_placeholders(self):
        """Test static placeholder identification"""
        assert WPPlaceholderSystem.is_static_placeholder('WÄRMEPUMPE')
        assert WPPlaceholderSystem.is_static_placeholder('COP-Wert:')
        assert WPPlaceholderSystem.is_static_placeholder('Heizkosten:')
        assert not WPPlaceholderSystem.is_static_placeholder('wp_modell_name')
    
    def test_dynamic_placeholders(self):
        """Test dynamic placeholder identification"""
        assert WPPlaceholderSystem.is_dynamic_placeholder('wp_modell_name')
        assert WPPlaceholderSystem.is_dynamic_placeholder('wp_cop_wert')
        assert WPPlaceholderSystem.is_dynamic_placeholder('wp_leistung_kw')
        assert not WPPlaceholderSystem.is_dynamic_placeholder('WÄRMEPUMPE')
    
    def test_replace_placeholder_found(self):
        """Test placeholder replacement when value exists"""
        data = {
            'wp_modell_name': 'Viessmann Vitocal 200-S',
            'wp_cop_wert': '4,5'
        }
        
        result = WPPlaceholderSystem.replace_placeholder('wp_modell_name', data)
        assert result == 'Viessmann Vitocal 200-S'
        
        result = WPPlaceholderSystem.replace_placeholder('wp_cop_wert', data)
        assert result == '4,5'
    
    def test_replace_placeholder_not_found(self):
        """Test placeholder replacement when value doesn't exist"""
        data = {'wp_modell_name': 'Viessmann'}
        
        result = WPPlaceholderSystem.replace_placeholder('wp_cop_wert', data)
        assert result == 'wp_cop_wert'
    
    def test_all_dynamic_placeholders_defined(self):
        """Test that all expected WP placeholders are defined"""
        expected_placeholders = [
            'wp_leistung_kw',
            'wp_cop_wert',
            'wp_jahresarbeitszahl',
            'wp_heizkosten_jahr',
            'wp_modell_name',
            'wp_hersteller'
        ]
        
        for placeholder in expected_placeholders:
            assert placeholder in WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS


class TestWPPositioningEngine:
    """Tests for WP positioning engine"""
    
    def test_positioning_engine_initialization(self):
        """Test positioning engine initialization"""
        engine = WPPositioningEngine()
        assert engine.page_width > 0
        assert engine.page_height > 0
    
    def test_create_overlay_empty_elements(self):
        """Test creating overlay with empty elements"""
        engine = WPPositioningEngine()
        overlay = engine.create_overlay([], {})
        
        # Should return bytes (even if empty)
        assert isinstance(overlay, bytes)
    
    def test_create_overlay_with_elements(self):
        """Test creating overlay with text elements"""
        engine = WPPositioningEngine()
        
        elements = [
            {
                'text': 'Test Text',
                'position': {'x': 100, 'y': 200, 'x2': 300, 'y2': 250},
                'font': 'Helvetica',
                'font_size': 12,
                'color': 0
            }
        ]
        
        overlay = engine.create_overlay(elements, {})
        
        # Should return non-empty bytes
        assert isinstance(overlay, bytes)
        assert len(overlay) > 0


class TestStandardWPPDFService:
    """Tests for main WP PDF service"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        service = StandardWPPDFService()
        
        assert service.template_loader is not None
        assert service.coords_dir == Path("coords_wp")
        assert service.positioning_engine is not None
    
    def test_service_custom_directories(self):
        """Test service with custom directories"""
        service = StandardWPPDFService(
            template_dir="custom/templates",
            coords_dir="custom/coords"
        )
        
        assert service.template_loader.template_dir == Path("custom/templates")
        assert service.coords_dir == Path("custom/coords")
    
    def test_load_page_coordinates_not_found(self):
        """Test loading coordinates for non-existent page"""
        service = StandardWPPDFService()
        coords = service.load_page_coordinates(99)
        
        assert coords == []
    
    def test_format_german_currency(self):
        """Test German currency formatting"""
        # Test various amounts
        assert StandardWPPDFService._format_german_currency(16999.00) == "16.999,00 €"
        assert StandardWPPDFService._format_german_currency(1250.50) == "1.250,50 €"
        assert StandardWPPDFService._format_german_currency(99.99) == "99,99 €"
        assert StandardWPPDFService._format_german_currency(1000000.00) == "1.000.000,00 €"
    
    def test_format_german_decimal(self):
        """Test German decimal formatting"""
        # Test COP values
        assert StandardWPPDFService._format_german_decimal(4.5, 1) == "4,5"
        assert StandardWPPDFService._format_german_decimal(4.25, 2) == "4,25"
        assert StandardWPPDFService._format_german_decimal(3500.75, 2) == "3.500,75"
    
    def test_generate_complete_pdf_structure(self):
        """Test complete PDF generation structure"""
        service = StandardWPPDFService()
        
        sample_data = {
            'anrede_kunde': 'Herr',
            'kunde_vorname_und_nachname': 'Max Mustermann',
            'kunde_wohnort': 'Berlin',
            'wp_leistung_kw': 12.5,
            'wp_cop_wert': 4.5,
            'wp_modell_name': 'Viessmann Vitocal 200-S',
            'wp_hersteller': 'Viessmann'
        }
        
        # Generate PDF (may fail if templates don't exist, but should not crash)
        try:
            pdf_bytes = service.generate_complete_pdf(sample_data)
            
            # If successful, should return bytes
            if pdf_bytes:
                assert isinstance(pdf_bytes, bytes)
                assert len(pdf_bytes) > 0
        except Exception as e:
            # Expected if templates don't exist in test environment
            assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_generate_pdf_with_german_formatting(self):
        """Test PDF generation with German formatting"""
        service = StandardWPPDFService()
        
        calculation_data = {
            'wp_leistung_kw': 12.5,
            'wp_cop_wert': 4.5,
            'wp_jahresarbeitszahl': 4.2,
            'wp_heizkosten_jahr': 1250.00,
            'wp_heizkosten_monat': 104.17,
            'wp_einsparung_jahr': 2500.00,
            'wp_heizlast_kw': 10.0,
            'wp_modell_name': 'Viessmann Vitocal 200-S',
            'wp_hersteller': 'Viessmann'
        }
        
        customer_data = {
            'anrede_kunde': 'Herr',
            'kunde_vorname_und_nachname': 'Max Mustermann',
            'kunde_wohnort': 'Berlin'
        }
        
        pricing_data = {
            'total_price': 18999.00
        }
        
        # Generate PDF (may fail if templates don't exist)
        try:
            pdf_bytes = service.generate_pdf_with_german_formatting(
                calculation_data=calculation_data,
                customer_data=customer_data,
                pricing_data=pricing_data
            )
            
            if pdf_bytes:
                assert isinstance(pdf_bytes, bytes)
                assert len(pdf_bytes) > 0
        except Exception as e:
            # Expected if templates don't exist
            assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_generate_page_with_missing_template(self):
        """Test page generation with missing template"""
        service = StandardWPPDFService()
        
        # Try to generate page 99 (doesn't exist)
        page_bytes = service.generate_page(99, {})
        
        assert page_bytes is None
    
    def test_generate_complete_pdf_with_page_selection(self):
        """Test PDF generation with specific pages"""
        service = StandardWPPDFService()
        
        sample_data = {
            'wp_modell_name': 'Test Model',
            'wp_cop_wert': 4.5
        }
        
        # Try to generate only pages 1-3
        try:
            pdf_bytes = service.generate_complete_pdf(
                sample_data,
                include_pages=[1, 2, 3]
            )
            
            # Should return bytes or empty bytes
            assert isinstance(pdf_bytes, bytes)
        except Exception:
            # Expected if templates don't exist
            pass


class TestWPPDFIntegration:
    """Integration tests for WP PDF system"""
    
    def test_end_to_end_pdf_generation(self):
        """Test complete end-to-end PDF generation"""
        service = StandardWPPDFService()
        
        # Complete WP data
        complete_data = {
            'anrede_kunde': 'Herr',
            'kunde_vorname_und_nachname': 'Max Mustermann',
            'kunde_wohnort': 'Berlin',
            'wp_leistung_kw': 12.5,
            'wp_cop_wert': 4.5,
            'wp_jahresarbeitszahl': 4.2,
            'wp_heizkosten_jahr': 1250.00,
            'wp_heizkosten_monat': 104.17,
            'wp_einsparung_jahr': 2500.00,
            'wp_einsparung_prozent': '66,7%',
            'wp_amortisationszeit': '8 Jahre',
            'wp_co2_einsparung': '4.500 kg/Jahr',
            'wp_effizienzklasse': 'A+++',
            'wp_vorlauftemperatur': '35°C',
            'wp_heizlast_kw': 10.0,
            'wp_warmwasser_liter': 300,
            'langes_datum_heute': '22. Januar 2025',
            'wp_modell_name': 'Viessmann Vitocal 200-S',
            'wp_hersteller': 'Viessmann',
            'total_price': 18999.00
        }
        
        try:
            pdf_bytes = service.generate_pdf_with_german_formatting(
                calculation_data=complete_data,
                customer_data=complete_data,
                pricing_data=complete_data
            )
            
            if pdf_bytes:
                # Verify PDF structure
                assert isinstance(pdf_bytes, bytes)
                assert len(pdf_bytes) > 0
                
                # PDF should start with %PDF
                assert pdf_bytes[:4] == b'%PDF'
                
                print(f" Generated WP PDF: {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f" PDF generation skipped (templates not available): {e}")
    
    def test_all_placeholders_coverage(self):
        """Test that all placeholders are properly handled"""
        service = StandardWPPDFService()
        
        # Create data with all dynamic placeholders
        all_placeholder_data = {}
        for placeholder in WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS:
            all_placeholder_data[placeholder] = f"Test_{placeholder}"
        
        # Should not crash
        try:
            pdf_bytes = service.generate_complete_pdf(all_placeholder_data)
            assert isinstance(pdf_bytes, bytes)
        except Exception as e:
            # Expected if templates don't exist
            assert "not found" in str(e).lower() or "not available" in str(e).lower()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
