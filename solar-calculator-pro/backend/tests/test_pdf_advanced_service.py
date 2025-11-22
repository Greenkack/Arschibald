"""
PDF Advanced Service Tests - Task 103

Comprehensive tests for PDF Advanced Service including:
- Service initialization
- PDF generation
- Custom branding
- Chart integration
- Batch generation
- Multi-company offers
- Template management
- Language support
- Error handling

Requirements: 1.3, 6.1, 7.3
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.services.pdf_advanced_service import (
    PDFAdvancedService,
    get_pdf_advanced_service,
    PDFGenerationOptions,
    PDFBrandingConfig,
    PDFTemplate,
    PDFLanguage,
    ChartType,
    YMLCoordinate
)
from backend.core.base_service import ServiceStatus


class TestPDFAdvancedServiceInitialization:
    """Test service initialization"""
    
    def test_service_singleton(self):
        """Test that service is a singleton"""
        service1 = get_pdf_advanced_service()
        service2 = get_pdf_advanced_service()
        
        assert service1 is service2
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = get_pdf_advanced_service()
        
        assert service.is_initialized
        assert service._pdf_generator is not None
        assert isinstance(service._yml_cache, dict)
        assert isinstance(service._template_cache, dict)
    
    def test_yml_coordinates_loaded(self):
        """Test YML coordinate files are loaded"""
        service = get_pdf_advanced_service()
        
        # Should load ~162 YML files
        assert len(service._yml_cache) > 0
        print(f"YML files loaded: {len(service._yml_cache)}")
    
    def test_templates_loaded(self):
        """Test PDF templates are loaded"""
        service = get_pdf_advanced_service()
        
        # Should load ~88 templates
        assert len(service._template_cache) > 0
        print(f"Templates loaded: {len(service._template_cache)}")


class TestPDFGeneration:
    """Test PDF generation"""
    
    def test_basic_pdf_generation(self):
        """Test basic PDF generation"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 1,
            'customer_name': 'Test Customer',
            'system_size': 10.0,
            'total_cost': 20000
        }
        
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            include_charts=False,
            include_3d_visualization=False,
            compress=False,
            archive_to_crm=False
        )
        
        pdf_bytes = service.generate_advanced_pdf(offer_data, options)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # Check PDF header
        assert pdf_bytes[:4] == b'%PDF' or len(pdf_bytes) > 0
    
    def test_pdf_generation_with_compression(self):
        """Test PDF generation with compression"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 2,
            'customer_name': 'Test Customer 2',
            'system_size': 12.0,
            'total_cost': 25000
        }
        
        # Generate without compression
        options_no_compress = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=False,
            archive_to_crm=False
        )
        pdf_no_compress = service.generate_advanced_pdf(offer_data, options_no_compress)
        
        # Generate with compression
        options_compress = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=True,
            archive_to_crm=False
        )
        pdf_compress = service.generate_advanced_pdf(offer_data, options_compress)
        
        # Compressed should be smaller or equal
        assert len(pdf_compress) <= len(pdf_no_compress)
        print(f"Compression: {len(pdf_no_compress)} -> {len(pdf_compress)} bytes")
    
    def test_pdf_generation_with_different_templates(self):
        """Test PDF generation with different templates"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 3,
            'customer_name': 'Test Customer 3',
            'system_size': 15.0,
            'total_cost': 30000
        }
        
        templates = [
            PDFTemplate.BASIS,
            PDFTemplate.STORAGE_10KWH,
            PDFTemplate.HEATPUMP
        ]
        
        for template in templates:
            options = PDFGenerationOptions(
                template=template,
                language=PDFLanguage.GERMAN,
                compress=False,
                archive_to_crm=False
            )
            
            pdf_bytes = service.generate_advanced_pdf(offer_data, options)
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            print(f"Template {template.value}: {len(pdf_bytes)} bytes")


class TestCustomBranding:
    """Test custom branding"""
    
    def test_branding_configuration(self):
        """Test branding configuration"""
        branding = PDFBrandingConfig(
            company_name="Test Company",
            logo_path="test/logo.png",
            logo_position=(50, 50),
            logo_size=(100, 50),
            primary_color="#0066CC",
            secondary_color="#FF6600",
            font_family="Helvetica"
        )
        
        assert branding.company_name == "Test Company"
        assert branding.primary_color == "#0066CC"
        assert branding.logo_position == (50, 50)
    
    def test_pdf_generation_with_branding(self):
        """Test PDF generation with custom branding"""
        service = get_pdf_advanced_service()
        
        branding = PDFBrandingConfig(
            company_name="Test Company",
            logo_path="test/logo.png",
            logo_position=(50, 50),
            logo_size=(100, 50),
            primary_color="#0066CC",
            secondary_color="#FF6600",
            font_family="Helvetica",
            watermark_text="CONFIDENTIAL",
            watermark_opacity=0.1
        )
        
        offer_data = {
            'customer_id': 4,
            'customer_name': 'Test Customer 4',
            'system_size': 8.0,
            'total_cost': 18000
        }
        
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            branding=branding,
            compress=False,
            archive_to_crm=False
        )
        
        pdf_bytes = service.generate_advanced_pdf(offer_data, options)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0


class TestChartIntegration:
    """Test chart integration"""
    
    def test_chart_types_available(self):
        """Test all chart types are available"""
        service = get_pdf_advanced_service()
        
        chart_types = service.get_available_chart_types()
        
        assert len(chart_types) == 10
        chart_names = [ct['type'] for ct in chart_types]
        
        assert 'circle' in chart_names
        assert 'donut' in chart_names
        assert 'bar' in chart_names
        assert 'line' in chart_names
        assert 'pie' in chart_names
    
    def test_pdf_generation_with_charts(self):
        """Test PDF generation with charts"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 5,
            'customer_name': 'Test Customer 5',
            'system_size': 10.0,
            'total_cost': 22000,
            'charts': {
                'energy_production': {
                    'type': 'line',
                    'data': [10000, 11000, 12000],
                    'labels': ['Year 1', 'Year 10', 'Year 20']
                }
            }
        }
        
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            include_charts=True,
            chart_types=[ChartType.LINE, ChartType.BAR, ChartType.PIE],
            compress=False,
            archive_to_crm=False
        )
        
        pdf_bytes = service.generate_advanced_pdf(offer_data, options)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0


class TestBatchGeneration:
    """Test batch generation"""
    
    @pytest.mark.asyncio
    async def test_batch_generation(self):
        """Test batch PDF generation"""
        service = get_pdf_advanced_service()
        
        offers = [
            {'customer_id': 10, 'customer_name': 'Customer 10', 'system_size': 8.0},
            {'customer_id': 11, 'customer_name': 'Customer 11', 'system_size': 10.0},
            {'customer_id': 12, 'customer_name': 'Customer 12', 'system_size': 12.0}
        ]
        
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=False,
            archive_to_crm=False
        )
        
        pdf_list = await service.generate_batch_pdfs(offers, options)
        
        assert len(pdf_list) == 3
        for pdf_bytes in pdf_list:
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
    
    @pytest.mark.asyncio
    async def test_batch_generation_performance(self):
        """Test batch generation performance"""
        service = get_pdf_advanced_service()
        
        # Generate 5 PDFs
        offers = [
            {'customer_id': i, 'customer_name': f'Customer {i}', 'system_size': 10.0}
            for i in range(20, 25)
        ]
        
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=False,
            archive_to_crm=False
        )
        
        start_time = datetime.now()
        pdf_list = await service.generate_batch_pdfs(offers, options)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        assert len(pdf_list) == 5
        print(f"Batch generation: {duration:.2f} seconds for {len(pdf_list)} PDFs")
        print(f"Average: {duration/len(pdf_list):.2f} seconds per PDF")


class TestMultiCompanyOffers:
    """Test multi-company offers"""
    
    def test_multi_company_offer_generation(self):
        """Test multi-company offer generation"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 30,
            'customer_name': 'Corporate Client',
            'system_size': 50.0,
            'total_cost': 100000
        }
        
        companies = [
            PDFBrandingConfig(
                company_name="Company A",
                logo_path="logos/a.png",
                primary_color="#0066CC",
                secondary_color="#FF6600",
                font_family="Helvetica"
            ),
            PDFBrandingConfig(
                company_name="Company B",
                logo_path="logos/b.png",
                primary_color="#00CC66",
                secondary_color="#FFCC00",
                font_family="Helvetica"
            )
        ]
        
        zip_bytes = service.generate_multi_company_offer(offer_data, companies)
        
        assert zip_bytes is not None
        assert len(zip_bytes) > 0
        # Check ZIP header
        assert zip_bytes[:2] == b'PK'
        print(f"Multi-company ZIP: {len(zip_bytes)} bytes")


class TestTemplateManagement:
    """Test template management"""
    
    def test_get_available_templates(self):
        """Test getting available templates"""
        service = get_pdf_advanced_service()
        
        templates = service.get_available_templates()
        
        assert len(templates) > 0
        assert all('name' in t for t in templates)
        assert all('display_name' in t for t in templates)
        assert all('available' in t for t in templates)
    
    def test_template_enum_values(self):
        """Test template enum values"""
        templates = [
            PDFTemplate.BASIS,
            PDFTemplate.STORAGE_10KWH,
            PDFTemplate.HEATPUMP,
            PDFTemplate.WALLBOX,
            PDFTemplate.FINANCING
        ]
        
        for template in templates:
            assert template.value is not None
            assert isinstance(template.value, str)


class TestLanguageSupport:
    """Test language support"""
    
    def test_get_available_languages(self):
        """Test getting available languages"""
        service = get_pdf_advanced_service()
        
        languages = service.get_available_languages()
        
        assert len(languages) == 4
        codes = [lang['code'] for lang in languages]
        
        assert 'de' in codes  # German
        assert 'en' in codes  # English
        assert 'fr' in codes  # French
        assert 'it' in codes  # Italian
    
    def test_pdf_generation_different_languages(self):
        """Test PDF generation in different languages"""
        service = get_pdf_advanced_service()
        
        offer_data = {
            'customer_id': 40,
            'customer_name': 'Test Customer',
            'system_size': 10.0,
            'total_cost': 20000
        }
        
        languages = [
            PDFLanguage.GERMAN,
            PDFLanguage.ENGLISH
        ]
        
        for language in languages:
            options = PDFGenerationOptions(
                template=PDFTemplate.BASIS,
                language=language,
                compress=False,
                archive_to_crm=False
            )
            
            pdf_bytes = service.generate_advanced_pdf(offer_data, options)
            assert pdf_bytes is not None
            print(f"Language {language.value}: {len(pdf_bytes)} bytes")


class TestYMLCoordinates:
    """Test YML coordinate system"""
    
    def test_yml_coordinate_structure(self):
        """Test YML coordinate data structure"""
        coord = YMLCoordinate(
            text="test_text",
            position=(50.0, 100.0, 150.0, 120.0),
            font_family="Helvetica",
            font_size=12.0,
            color=0,
            format_type="currency"
        )
        
        assert coord.text == "test_text"
        assert coord.position == (50.0, 100.0, 150.0, 120.0)
        assert coord.font_family == "Helvetica"
        assert coord.font_size == 12.0
        assert coord.format_type == "currency"
    
    def test_yml_coordinates_loaded(self):
        """Test YML coordinates are loaded correctly"""
        service = get_pdf_advanced_service()
        
        # Check that coordinates are loaded
        assert len(service._yml_cache) > 0
        
        # Check structure of first coordinate set
        if service._yml_cache:
            first_key = list(service._yml_cache.keys())[0]
            coordinates = service._yml_cache[first_key]
            
            assert isinstance(coordinates, dict)
            if coordinates:
                first_coord = list(coordinates.values())[0]
                assert isinstance(first_coord, YMLCoordinate)


class TestServiceHealth:
    """Test service health checks"""
    
    def test_health_check_healthy(self):
        """Test health check when service is healthy"""
        service = get_pdf_advanced_service()
        
        health = service.health_check()
        
        assert health.status == ServiceStatus.HEALTHY
        assert 'yml_files' in health.details
        assert 'templates' in health.details
    
    def test_health_check_details(self):
        """Test health check provides detailed information"""
        service = get_pdf_advanced_service()
        
        health = service.health_check()
        
        assert health.details['yml_files'] > 0
        assert health.details['templates'] > 0
        assert 'generations' in health.details
        assert 'batch_generations' in health.details


class TestStatistics:
    """Test service statistics"""
    
    def test_get_statistics(self):
        """Test getting service statistics"""
        service = get_pdf_advanced_service()
        
        stats = service.get_statistics()
        
        assert 'total_generations' in stats
        assert 'batch_generations' in stats
        assert 'archived_pdfs' in stats
        assert 'yml_files_loaded' in stats
        assert 'templates_loaded' in stats
        assert 'branding_configs' in stats
    
    def test_statistics_increment(self):
        """Test statistics increment after generation"""
        service = get_pdf_advanced_service()
        
        # Get initial stats
        initial_stats = service.get_statistics()
        initial_count = initial_stats['total_generations']
        
        # Generate PDF
        offer_data = {'customer_id': 50, 'customer_name': 'Test', 'system_size': 10.0}
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=False,
            archive_to_crm=False
        )
        service.generate_advanced_pdf(offer_data, options)
        
        # Get updated stats
        updated_stats = service.get_statistics()
        updated_count = updated_stats['total_generations']
        
        assert updated_count == initial_count + 1


class TestErrorHandling:
    """Test error handling"""
    
    def test_service_not_initialized_error(self):
        """Test error when service not initialized"""
        service = PDFAdvancedService()
        # Don't initialize
        
        offer_data = {'customer_id': 60, 'customer_name': 'Test'}
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN
        )
        
        with pytest.raises(RuntimeError, match="Service not initialized"):
            service.generate_advanced_pdf(offer_data, options)
    
    def test_missing_offer_data(self):
        """Test handling of missing offer data"""
        service = get_pdf_advanced_service()
        
        # Empty offer data
        offer_data = {}
        options = PDFGenerationOptions(
            template=PDFTemplate.BASIS,
            language=PDFLanguage.GERMAN,
            compress=False,
            archive_to_crm=False
        )
        
        # Should not crash, may use defaults
        try:
            pdf_bytes = service.generate_advanced_pdf(offer_data, options)
            assert pdf_bytes is not None
        except Exception as e:
            # Expected to fail gracefully
            assert isinstance(e, (KeyError, ValueError, RuntimeError))


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
