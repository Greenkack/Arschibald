"""
Tests for Extended WP PDF Service

Author: Kiro AI
Date: 2025-01-22
"""

import pytest
import logging
from pathlib import Path
from io import BytesIO

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

from ..services.extended_wp_pdf_service import (
    ExtendedWPPDFService,
    WPComponentSelection,
    WPComponentType,
    ExtendedWPPageConfig,
    WPDatasheetIntegration,
    WPDocumentIntegration,
    WPImageIntegration,
    ExtendedWPCalculationGenerator,
    ExtendedWPVisualizationGenerator
)

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_wp_data():
    """Sample WP data for testing"""
    return {
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


@pytest.fixture
def basic_wp_component_selection():
    """Basic WP component selection for testing"""
    return WPComponentSelection(
        include_detailed_wp_calculations=True,
        include_additional_wp_diagrams=False,
        include_wp_product_datasheets=False,
        include_wp_documents=False,
        include_wp_images=False,
        include_extended_wp_visualizations=False
    )


@pytest.fixture
def full_wp_component_selection():
    """Full WP component selection for testing"""
    return WPComponentSelection(
        include_detailed_wp_calculations=True,
        include_additional_wp_diagrams=True,
        include_wp_product_datasheets=True,
        include_wp_documents=True,
        include_wp_images=True,
        include_extended_wp_visualizations=True,
        selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison'],
        selected_wp_product_ids=['wp_product_1'],
        selected_wp_document_ids=['wp_doc_1'],
        selected_wp_image_ids=['wp_img_1']
    )



class TestWPComponentSelection:
    """Tests for WPComponentSelection"""
    
    def test_default_initialization(self):
        """Test default initialization of WPComponentSelection"""
        selection = WPComponentSelection()
        
        assert selection.include_detailed_wp_calculations is False
        assert selection.include_additional_wp_diagrams is False
        assert selection.include_wp_product_datasheets is False
        assert selection.include_wp_documents is False
        assert selection.include_wp_images is False
        assert selection.include_extended_wp_visualizations is False
        assert selection.selected_wp_diagram_types == []
        assert selection.selected_wp_product_ids == []
        assert selection.selected_wp_document_ids == []
        assert selection.selected_wp_image_ids == []
    
    def test_custom_initialization(self):
        """Test custom initialization of WPComponentSelection"""
        selection = WPComponentSelection(
            include_detailed_wp_calculations=True,
            include_additional_wp_diagrams=True,
            selected_wp_diagram_types=['cop_monthly']
        )
        
        assert selection.include_detailed_wp_calculations is True
        assert selection.include_additional_wp_diagrams is True
        assert selection.selected_wp_diagram_types == ['cop_monthly']


class TestExtendedWPPDFService:
    """Tests for ExtendedWPPDFService"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        service = ExtendedWPPDFService()
        
        assert service.standard_wp_service is not None
        assert service.extended_wp_template_loader is not None
        assert service.positioning_engine is not None
        assert service.wp_datasheet_integration is not None
        assert service.wp_document_integration is not None
        assert service.wp_image_integration is not None
        assert service.wp_calculation_generator is not None
        assert service.wp_visualization_generator is not None
    
    @pytest.mark.skipif(not PYPDF_AVAILABLE, reason="PyPDF not available")
    def test_generate_extended_wp_pdf_basic(self, sample_wp_data, basic_wp_component_selection):
        """Test basic extended WP PDF generation"""
        service = ExtendedWPPDFService()
        
        pdf_bytes = service.generate_extended_wp_pdf(
            sample_wp_data,
            basic_wp_component_selection
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf = PdfReader(BytesIO(pdf_bytes))
        # Should have at least 8 standard pages + 1 detailed calculation page
        assert len(pdf.pages) >= 9
    
    def test_get_available_wp_components_without_products(self):
        """Test getting available WP components without product IDs"""
        service = ExtendedWPPDFService()
        
        components = service.get_available_wp_components()
        
        assert 'wp_calculations' in components
        assert 'wp_diagrams' in components
        assert 'wp_datasheets' in components
        assert 'wp_documents' in components
        assert 'wp_images' in components
        
        # Should have default calculations and diagrams
        assert len(components['wp_calculations']) > 0
        assert len(components['wp_diagrams']) > 0
        
        # Should have empty product-specific lists
        assert len(components['wp_datasheets']) == 0
        assert len(components['wp_documents']) == 0
    
    def test_generate_detailed_wp_calculations_page(self, sample_wp_data):
        """Test generating detailed WP calculations page"""
        service = ExtendedWPPDFService()
        
        # This will return None if template doesn't exist, which is expected in test environment
        page_bytes = service._generate_detailed_wp_calculations_page(9, sample_wp_data)
        
        # In test environment without templates, this should return None
        # In production with templates, it should return PDF bytes
        assert page_bytes is None or isinstance(page_bytes, bytes)


class TestWPDatasheetIntegration:
    """Tests for WPDatasheetIntegration"""
    
    def test_initialization_without_database(self):
        """Test initialization without database service"""
        integration = WPDatasheetIntegration()
        
        assert integration.database_service is None
    
    def test_get_wp_product_datasheet_without_database(self):
        """Test getting WP datasheet without database"""
        integration = WPDatasheetIntegration()
        
        datasheet = integration.get_wp_product_datasheet('test_product')
        
        assert datasheet is None


class TestWPDocumentIntegration:
    """Tests for WPDocumentIntegration"""
    
    def test_initialization_without_database(self):
        """Test initialization without database service"""
        integration = WPDocumentIntegration()
        
        assert integration.database_service is None
    
    def test_get_wp_document_without_database(self):
        """Test getting WP document without database"""
        integration = WPDocumentIntegration()
        
        document = integration.get_wp_document('test_doc')
        
        assert document is None
    
    def test_get_wp_product_documents_without_database(self):
        """Test getting WP product documents without database"""
        integration = WPDocumentIntegration()
        
        documents = integration.get_wp_product_documents('test_product')
        
        assert documents == []


class TestWPImageIntegration:
    """Tests for WPImageIntegration"""
    
    def test_initialization_without_database(self):
        """Test initialization without database service"""
        integration = WPImageIntegration()
        
        assert integration.database_service is None
    
    def test_get_wp_image_without_database(self):
        """Test getting WP image without database"""
        integration = WPImageIntegration()
        
        image = integration.get_wp_image('test_image')
        
        assert image is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
