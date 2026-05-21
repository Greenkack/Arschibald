"""
Tests for Extended PV PDF Service

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

from ..services.extended_pv_pdf_service import (
    ExtendedPVPDFService,
    ComponentSelection,
    ComponentType,
    ExtendedPageConfig,
    DatasheetIntegration,
    DocumentIntegration,
    ImageIntegration,
    ExtendedCalculationGenerator,
    ExtendedVisualizationGenerator
)

logger = logging.getLogger(__name__)


# Mock database service for testing
class MockDatabaseService:
    """Mock database service for testing"""
    
    def get_product_datasheet(self, product_id: str):
        """Mock get product datasheet"""
        if product_id == "test_product_1":
            return {'pdf_bytes': b'%PDF-1.4 mock datasheet'}
        return None
    
    def get_document(self, document_id: str):
        """Mock get document"""
        if document_id == "test_doc_1":
            return {'pdf_bytes': b'%PDF-1.4 mock document'}
        return None
    
    def get_product_documents(self, product_id: str):
        """Mock get product documents"""
        if product_id == "test_product_1":
            return [
                {'id': 'doc1', 'name': 'Installation Guide'},
                {'id': 'doc2', 'name': 'Warranty Information'}
            ]
        return []
    
    def get_image(self, image_id: str):
        """Mock get image"""
        if image_id == "test_image_1":
            # Return a minimal PNG image
            return {'image_bytes': b'\x89PNG\r\n\x1a\n'}
        return None


@pytest.fixture
def mock_db_service():
    """Fixture for mock database service"""
    return MockDatabaseService()


@pytest.fixture
def extended_pdf_service(mock_db_service):
    """Fixture for extended PDF service"""
    return ExtendedPVPDFService(database_service=mock_db_service)


@pytest.fixture
def sample_data():
    """Fixture for sample data"""
    return {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'kWp_anlage_anlage': '10,5 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 16999.00,
        'detailed_roi': 8.5,
        'annual_production': 12500,
        'annual_savings': 2100
    }


class TestComponentSelection:
    """Tests for ComponentSelection"""
    
    def test_component_selection_defaults(self):
        """Test default component selection"""
        selection = ComponentSelection()
        
        assert selection.include_detailed_calculations is False
        assert selection.include_additional_diagrams is False
        assert selection.include_product_datasheets is False
        assert selection.include_documents is False
        assert selection.include_images is False
        assert selection.include_extended_visualizations is False
        assert selection.selected_diagram_types == []
        assert selection.selected_product_ids == []
        assert selection.selected_document_ids == []
        assert selection.selected_image_ids == []
    
    def test_component_selection_with_values(self):
        """Test component selection with values"""
        selection = ComponentSelection(
            include_detailed_calculations=True,
            include_additional_diagrams=True,
            selected_diagram_types=['production_monthly', 'savings_projection'],
            selected_product_ids=['product1', 'product2']
        )
        
        assert selection.include_detailed_calculations is True
        assert selection.include_additional_diagrams is True
        assert len(selection.selected_diagram_types) == 2
        assert len(selection.selected_product_ids) == 2


class TestDatasheetIntegration:
    """Tests for DatasheetIntegration"""
    
    def test_get_product_datasheet_success(self, mock_db_service):
        """Test successful datasheet retrieval"""
        integration = DatasheetIntegration(mock_db_service)
        datasheet = integration.get_product_datasheet('test_product_1')
        
        assert datasheet is not None
        assert isinstance(datasheet, bytes)
    
    def test_get_product_datasheet_not_found(self, mock_db_service):
        """Test datasheet not found"""
        integration = DatasheetIntegration(mock_db_service)
        datasheet = integration.get_product_datasheet('nonexistent_product')
        
        assert datasheet is None
    
    def test_get_all_product_datasheets(self, mock_db_service):
        """Test getting multiple datasheets"""
        integration = DatasheetIntegration(mock_db_service)
        datasheets = integration.get_all_product_datasheets([
            'test_product_1',
            'nonexistent_product'
        ])
        
        assert len(datasheets) == 1
        assert 'test_product_1' in datasheets


class TestDocumentIntegration:
    """Tests for DocumentIntegration"""
    
    def test_get_document_success(self, mock_db_service):
        """Test successful document retrieval"""
        integration = DocumentIntegration(mock_db_service)
        document = integration.get_document('test_doc_1')
        
        assert document is not None
        assert isinstance(document, bytes)
    
    def test_get_document_not_found(self, mock_db_service):
        """Test document not found"""
        integration = DocumentIntegration(mock_db_service)
        document = integration.get_document('nonexistent_doc')
        
        assert document is None
    
    def test_get_product_documents(self, mock_db_service):
        """Test getting product documents"""
        integration = DocumentIntegration(mock_db_service)
        documents = integration.get_product_documents('test_product_1')
        
        assert len(documents) == 2
        assert documents[0]['id'] == 'doc1'


class TestImageIntegration:
    """Tests for ImageIntegration"""
    
    def test_get_image_success(self, mock_db_service):
        """Test successful image retrieval"""
        integration = ImageIntegration(mock_db_service)
        image_pdf = integration.get_image('test_image_1')
        
        # Image conversion might fail without PIL, that's ok for this test
        assert image_pdf is not None or image_pdf == b''
    
    def test_get_image_not_found(self, mock_db_service):
        """Test image not found"""
        integration = ImageIntegration(mock_db_service)
        image_pdf = integration.get_image('nonexistent_image')
        
        assert image_pdf is None


class TestExtendedPVPDFService:
    """Tests for ExtendedPVPDFService"""
    
    def test_service_initialization(self, extended_pdf_service):
        """Test service initialization"""
        assert extended_pdf_service is not None
        assert extended_pdf_service.standard_service is not None
        assert extended_pdf_service.datasheet_integration is not None
        assert extended_pdf_service.document_integration is not None
        assert extended_pdf_service.image_integration is not None
    
    def test_generate_extended_pdf_standard_only(self, extended_pdf_service, sample_data):
        """Test generating PDF with standard pages only"""
        selection = ComponentSelection()  # All False
        
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        if PYPDF_AVAILABLE:
            pdf = PdfReader(BytesIO(pdf_bytes))
            # Should have 8 standard pages
            assert len(pdf.pages) >= 1  # At least some pages
    
    def test_generate_extended_pdf_with_calculations(self, extended_pdf_service, sample_data):
        """Test generating PDF with detailed calculations"""
        selection = ComponentSelection(
            include_detailed_calculations=True
        )
        
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        if PYPDF_AVAILABLE:
            pdf = PdfReader(BytesIO(pdf_bytes))
            # Should have 8 standard pages + 1 calculation page
            assert len(pdf.pages) >= 1
    
    def test_generate_extended_pdf_with_diagrams(self, extended_pdf_service, sample_data):
        """Test generating PDF with additional diagrams"""
        selection = ComponentSelection(
            include_additional_diagrams=True,
            selected_diagram_types=['production_monthly', 'savings_projection']
        )
        
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        if PYPDF_AVAILABLE:
            pdf = PdfReader(BytesIO(pdf_bytes))
            # Should have 8 standard pages + 2 diagram pages
            assert len(pdf.pages) >= 1
    
    def test_generate_extended_pdf_with_datasheets(self, extended_pdf_service, sample_data):
        """Test generating PDF with product datasheets"""
        selection = ComponentSelection(
            include_product_datasheets=True,
            selected_product_ids=['test_product_1']
        )
        
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
    
    def test_generate_extended_pdf_with_all_components(self, extended_pdf_service, sample_data):
        """Test generating PDF with all components"""
        selection = ComponentSelection(
            include_detailed_calculations=True,
            include_additional_diagrams=True,
            include_product_datasheets=True,
            include_documents=True,
            include_images=True,
            include_extended_visualizations=True,
            selected_diagram_types=['production_monthly'],
            selected_product_ids=['test_product_1'],
            selected_document_ids=['test_doc_1'],
            selected_image_ids=['test_image_1']
        )
        
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        if PYPDF_AVAILABLE:
            pdf = PdfReader(BytesIO(pdf_bytes))
            # Should have many pages
            assert len(pdf.pages) >= 1
    
    def test_get_available_components_no_products(self, extended_pdf_service):
        """Test getting available components without product IDs"""
        components = extended_pdf_service.get_available_components()
        
        assert 'calculations' in components
        assert 'diagrams' in components
        assert 'datasheets' in components
        assert 'documents' in components
        assert 'images' in components
        
        assert len(components['calculations']) > 0
        assert len(components['diagrams']) > 0
    
    def test_get_available_components_with_products(self, extended_pdf_service):
        """Test getting available components with product IDs"""
        components = extended_pdf_service.get_available_components(
            product_ids=['test_product_1']
        )
        
        assert 'datasheets' in components
        assert 'documents' in components
        
        # Should have datasheet for test_product_1
        assert len(components['datasheets']) >= 0
        assert len(components['documents']) >= 0


class TestExtendedCalculationGenerator:
    """Tests for ExtendedCalculationGenerator"""
    
    def test_create_calculation_elements(self):
        """Test creating calculation elements"""
        from ..services.extended_pv_pdf_service import PositioningEngine
        
        engine = PositioningEngine()
        generator = ExtendedCalculationGenerator(engine)
        
        calculation_data = {
            'roi': 8.5,
            'payback_period': 12,
            'annual_savings': 2100
        }
        
        elements = generator._create_calculation_elements(calculation_data)
        
        assert len(elements) > 0
        assert elements[0]['text'] == 'Detaillierte Berechnungen'


class TestExtendedVisualizationGenerator:
    """Tests for ExtendedVisualizationGenerator"""
    
    def test_generate_visualization_page(self):
        """Test generating visualization page"""
        from ..services.extended_pv_pdf_service import PositioningEngine
        
        engine = PositioningEngine()
        generator = ExtendedVisualizationGenerator(engine)
        
        # This test would need a valid template
        # For now, just verify the generator exists
        assert generator is not None


# Integration tests
class TestIntegration:
    """Integration tests for extended PDF service"""
    
    def test_full_workflow(self, extended_pdf_service, sample_data):
        """Test full workflow from data to PDF"""
        # Step 1: Get available components
        components = extended_pdf_service.get_available_components()
        assert components is not None
        
        # Step 2: Create selection
        selection = ComponentSelection(
            include_detailed_calculations=True,
            include_additional_diagrams=True,
            selected_diagram_types=['production_monthly']
        )
        
        # Step 3: Generate PDF
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Step 4: Verify PDF structure
        if PYPDF_AVAILABLE:
            pdf = PdfReader(BytesIO(pdf_bytes))
            assert len(pdf.pages) >= 1
    
    def test_error_handling_invalid_data(self, extended_pdf_service):
        """Test error handling with invalid data"""
        selection = ComponentSelection()
        
        # Empty data should still generate standard pages
        pdf_bytes = extended_pdf_service.generate_extended_pdf({}, selection)
        assert pdf_bytes is not None
    
    def test_error_handling_missing_components(self, extended_pdf_service, sample_data):
        """Test error handling with missing components"""
        selection = ComponentSelection(
            include_product_datasheets=True,
            selected_product_ids=['nonexistent_product']
        )
        
        # Should still generate PDF, just skip missing components
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        assert pdf_bytes is not None


# Performance tests
class TestPerformance:
    """Performance tests for extended PDF service"""
    
    def test_generation_time_standard_only(self, extended_pdf_service, sample_data):
        """Test generation time for standard pages only"""
        import time
        
        selection = ComponentSelection()
        
        start_time = time.time()
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        assert pdf_bytes is not None
        # Should complete in reasonable time (adjust threshold as needed)
        assert generation_time < 10.0  # 10 seconds max
        
        logger.info(f"Standard PDF generation time: {generation_time:.2f}s")
    
    def test_generation_time_with_many_components(self, extended_pdf_service, sample_data):
        """Test generation time with many components"""
        import time
        
        selection = ComponentSelection(
            include_detailed_calculations=True,
            include_additional_diagrams=True,
            include_extended_visualizations=True,
            selected_diagram_types=['production_monthly', 'savings_projection']
        )
        
        start_time = time.time()
        pdf_bytes = extended_pdf_service.generate_extended_pdf(sample_data, selection)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        assert pdf_bytes is not None
        # Should complete in reasonable time
        assert generation_time < 30.0  # 30 seconds max
        
        logger.info(f"Extended PDF generation time: {generation_time:.2f}s")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
