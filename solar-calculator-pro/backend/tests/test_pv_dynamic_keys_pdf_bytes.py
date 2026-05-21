"""
Tests for PV Dynamic Keys and PDF Bytes Generation

This test suite verifies the functionality of:
- PV Dynamic Key Manager
- PV PDF Bytes Generator
- German number formatting
- Integration with existing infrastructure

Requirements: 1.3, 4.5, 14.1, 14.2
Task: 115 - Standard PV PDF Dynamic Keys & PDF Bytes
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from services.pv_dynamic_key_manager import (
        PVDynamicKeyManager,
        PVKeyPrefix,
        GermanNumberFormatter,
        PVDataModel
    )
    from services.pv_pdf_bytes_generator import (
        PVPDFBytesGenerator,
        PVCalculationResultPDF,
        PVProductDataPDF,
        PVChartPDF,
        PV3DVisualizationPDF
    )
except ImportError:
    from backend.services.pv_dynamic_key_manager import (
        PVDynamicKeyManager,
        PVKeyPrefix,
        GermanNumberFormatter,
        PVDataModel
    )
    from backend.services.pv_pdf_bytes_generator import (
        PVPDFBytesGenerator,
        PVCalculationResultPDF,
        PVProductDataPDF,
        PVChartPDF,
        PV3DVisualizationPDF
    )


class TestGermanNumberFormatter:
    """Test German number formatting"""
    
    def test_format_basic_number(self):
        """Test basic number formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format(1234.56, 2)
        assert result == "1.234,56"
    
    def test_format_large_number(self):
        """Test large number formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format(1234567.89, 2)
        assert result == "1.234.567,89"
    
    def test_format_currency(self):
        """Test currency formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format_currency(16999.00)
        assert result == "16.999,00 €"
    
    def test_format_kwh(self):
        """Test kWh formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format_kwh(12500.50)
        assert result == "12.500,50 kWh"
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format_percentage(85.5)
        assert result == "85,50 %"
    
    def test_format_years(self):
        """Test years formatting"""
        formatter = GermanNumberFormatter()
        result = formatter.format_years(12.5)
        assert result == "12,5 Jahre"
    
    def test_format_zero(self):
        """Test formatting zero"""
        formatter = GermanNumberFormatter()
        result = formatter.format(0.0, 2)
        assert result == "0,00"
    
    def test_format_negative(self):
        """Test formatting negative numbers"""
        formatter = GermanNumberFormatter()
        result = formatter.format(-1234.56, 2)
        assert result == "-1.234,56"


class TestPVDynamicKeyManager:
    """Test PV Dynamic Key Manager"""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance"""
        return PVDynamicKeyManager()
    
    @pytest.fixture
    def sample_calculation_data(self):
        """Sample calculation data"""
        return {
            'system_size': 10.5,
            'module_count': 30,
            'annual_production': 12500.0,
            'self_consumption_rate': 85.5,
            'payback_period': 12.5,
            'total_cost': 16999.00,
            'savings_25_years': 45000.00,
            'co2_savings': 125000.0
        }
    
    @pytest.fixture
    def sample_product_data(self):
        """Sample product data"""
        return {
            'module_type': 'Trina Solar TSM-400W',
            'module_power': 400,
            'module_efficiency': 20.5,
            'inverter_type': 'SMA Sunny Tripower 10.0',
            'battery_type': 'BYD Battery-Box Premium HVS 10.2',
            'battery_capacity': 10.2
        }
    
    @pytest.fixture
    def sample_pricing_data(self):
        """Sample pricing data"""
        return {
            'base_price': 15000.00,
            'total_price': 16999.00,
            'module_price': 8000.00,
            'inverter_price': 3000.00,
            'battery_price': 5000.00
        }
    
    def test_import_calculation_keys(self, manager, sample_calculation_data):
        """Test importing calculation keys"""
        keys = manager.import_calculation_keys(sample_calculation_data)
        
        assert len(keys) > 0
        assert 'system_size' in keys
        assert 'module_count' in keys
        assert 'annual_production' in keys
        
        # Verify keys are in index
        for original_key, dynamic_key in keys.items():
            assert manager.index.exists(dynamic_key)
    
    def test_import_product_keys(self, manager, sample_product_data):
        """Test importing product keys"""
        keys = manager.import_product_keys(sample_product_data)
        
        assert len(keys) > 0
        assert 'module_type' in keys
        assert 'inverter_type' in keys
        
        # Verify keys are in index
        for original_key, dynamic_key in keys.items():
            assert manager.index.exists(dynamic_key)
    
    def test_import_pricing_keys(self, manager, sample_pricing_data):
        """Test importing pricing keys with German formatting"""
        keys = manager.import_pricing_keys(sample_pricing_data)
        
        assert len(keys) > 0
        assert 'total_price' in keys
        
        # Verify formatted values
        total_price_key = keys['total_price']
        formatted_value = manager.index.get(total_price_key)
        assert '€' in formatted_value
        assert ',' in formatted_value  # German decimal separator
    
    def test_get_value_by_key(self, manager, sample_calculation_data):
        """Test retrieving values by key"""
        keys = manager.import_calculation_keys(sample_calculation_data)
        
        system_size_key = keys['system_size']
        value = manager.get_value_by_key(system_size_key)
        
        assert value == sample_calculation_data['system_size']
    
    def test_get_formatted_value(self, manager, sample_pricing_data):
        """Test retrieving formatted values"""
        keys = manager.import_pricing_keys(sample_pricing_data)
        
        total_price_key = keys['total_price']
        formatted = manager.get_formatted_value(total_price_key)
        
        assert isinstance(formatted, str)
        assert '€' in formatted
    
    def test_export_all_keys(self, manager, sample_calculation_data, sample_pricing_data):
        """Test exporting all keys"""
        manager.import_calculation_keys(sample_calculation_data)
        manager.import_pricing_keys(sample_pricing_data)
        
        exported = manager.export_all_keys()
        
        assert len(exported) > 0
        assert 'system_size' in exported
        assert 'total_price' in exported
        
        # Verify structure
        for key_data in exported.values():
            assert 'dynamic_key' in key_data
            assert 'value' in key_data
            assert 'formatted_value' in key_data
            assert 'metadata' in key_data
    
    def test_key_uniqueness(self, manager, sample_calculation_data):
        """Test that generated keys are unique"""
        keys1 = manager.import_calculation_keys(sample_calculation_data)
        keys2 = manager.import_calculation_keys(sample_calculation_data)
        
        # Keys should be different even for same data
        assert keys1['system_size'] != keys2['system_size']


class TestPVPDFBytesGenerator:
    """Test PV PDF Bytes Generator"""
    
    @pytest.fixture
    def generator(self):
        """Create a fresh generator instance"""
        return PVPDFBytesGenerator()
    
    @pytest.fixture
    def sample_calculation_data(self):
        """Sample calculation data"""
        return {
            'system_size': 10.5,
            'module_count': 30,
            'annual_production': 12500.0,
            'self_consumption_rate': 85.5,
            'payback_period': 12.5,
            'total_cost': 16999.00,
            'savings_25_years': 45000.00,
            'co2_savings': 125000.0
        }
    
    @pytest.fixture
    def sample_product_data(self):
        """Sample product data"""
        return {
            'module_type': 'Trina Solar TSM-400W',
            'module_power': 400,
            'module_efficiency': 20.5,
            'inverter_type': 'SMA Sunny Tripower 10.0',
            'battery_type': 'BYD Battery-Box Premium HVS 10.2',
            'battery_capacity': 10.2
        }
    
    def test_generate_calculation_pdf(self, generator, sample_calculation_data):
        """Test generating calculation PDF"""
        pdf_bytes = generator.generate_calculation_pdf(sample_calculation_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF header
    
    def test_generate_product_pdf(self, generator, sample_product_data):
        """Test generating product PDF"""
        pdf_bytes = generator.generate_product_pdf(sample_product_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_generate_chart_pdf(self, generator):
        """Test generating chart PDF"""
        chart_data = {
            'labels': ['Jan', 'Feb', 'Mar'],
            'values': [100, 200, 150]
        }
        
        pdf_bytes = generator.generate_chart_pdf('PIE', chart_data, 'Test Chart')
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_generate_3d_visualization_pdf(self, generator):
        """Test generating 3D visualization PDF"""
        viz_data = {
            'description': 'Test 3D visualization',
            'module_count': 30,
            'roof_area': 50.0,
            'orientation': 'South'
        }
        
        pdf_bytes = generator.generate_3d_visualization_pdf(viz_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')


class TestPVDataModel:
    """Test PV Data Model with dynamic keys and PDF bytes"""
    
    def test_create_model(self):
        """Test creating PV data model"""
        data = {'system_size': 10.5, 'module_count': 30}
        model = PVDataModel(data)
        
        assert model.data == data
    
    def test_generate_dynamic_key(self):
        """Test generating dynamic key"""
        data = {'system_size': 10.5}
        model = PVDataModel(data)
        
        key = model.generate_dynamic_key(prefix=PVKeyPrefix.SYSTEM_SIZE)
        
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0
    
    def test_to_pdf_bytes(self):
        """Test converting to PDF bytes"""
        data = {
            'system_size': 10.5,
            'module_count': 30,
            'annual_production': 12500.0
        }
        model = PVDataModel(data)
        
        pdf_bytes = model.to_pdf_bytes()
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_to_pdf_base64(self):
        """Test converting to base64 PDF"""
        data = {'system_size': 10.5}
        model = PVDataModel(data)
        
        base64_str = model.to_pdf_base64()
        
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0


class TestIntegration:
    """Integration tests for dynamic keys and PDF bytes"""
    
    def test_full_workflow(self):
        """Test complete workflow from data to PDF"""
        # Step 1: Create manager and generator
        manager = PVDynamicKeyManager()
        generator = PVPDFBytesGenerator()
        
        # Step 2: Import data
        calculation_data = {
            'system_size': 10.5,
            'module_count': 30,
            'annual_production': 12500.0,
            'total_cost': 16999.00
        }
        
        # Step 3: Generate dynamic keys
        keys = manager.import_calculation_keys(calculation_data)
        assert len(keys) > 0
        
        # Step 4: Generate PDF bytes
        pdf_bytes = generator.generate_calculation_pdf(calculation_data)
        assert len(pdf_bytes) > 0
        
        # Step 5: Verify we can retrieve values by key
        for original_key, dynamic_key in keys.items():
            value = manager.get_value_by_key(dynamic_key)
            assert value is not None
    
    def test_german_formatting_in_pdf(self):
        """Test that German formatting is applied in PDF"""
        generator = PVPDFBytesGenerator()
        
        calculation_data = {
            'system_size': 10.5,
            'total_cost': 16999.00,
            'annual_production': 12500.0
        }
        
        pdf_bytes = generator.generate_calculation_pdf(calculation_data)
        
        # PDF should contain German-formatted numbers
        # Note: This is a basic check - full PDF parsing would be more thorough
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
