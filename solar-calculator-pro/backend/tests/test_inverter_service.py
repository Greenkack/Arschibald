"""
Tests for Inverter Service

Comprehensive test suite for solar inverter management functionality.

Requirements: 1.3, 6.1
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.inverter_service import InverterService, InverterSpecs


@pytest.fixture
def inverter_service():
    """Create inverter service instance for testing"""
    return InverterService()


@pytest.fixture
def sample_inverter_data():
    """Sample inverter data for testing"""
    return {
        'id': 1,
        'model_name': 'Test Inverter 10kW',
        'brand': 'TestBrand',
        'manufacturer': 'TestBrand',
        'power_kw': 10.0,
        'efficiency_percent': 97.5,
        'max_dc_voltage': 1000.0,
        'mppt_count': 2,
        'max_dc_current': 30.0,
        'price_euro': 2500.0,
        'additional_cost_netto': 100.0,
        'warranty_years': 10,
        'weight_kg': 25.0,
        'description': 'Test inverter for unit testing',
        'technology': 'String Inverter',
        'smart_home': True,
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-01T00:00:00'
    }


@pytest.fixture
def sample_inverters_list():
    """Sample list of inverters for testing"""
    return [
        {
            'id': 1,
            'model_name': 'Small Inverter 5kW',
            'brand': 'BrandA',
            'power_kw': 5.0,
            'efficiency_percent': 96.0,
            'max_dc_voltage': 1000.0,
            'mppt_count': 2,
            'max_dc_current': 25.0,
            'price_euro': 1500.0,
            'additional_cost_netto': 50.0,
            'warranty_years': 10,
            'weight_kg': 15.0,
            'description': 'Small inverter',
            'technology': 'String',
            'smart_home': False
        },
        {
            'id': 2,
            'model_name': 'Medium Inverter 10kW',
            'brand': 'BrandB',
            'power_kw': 10.0,
            'efficiency_percent': 97.5,
            'max_dc_voltage': 1000.0,
            'mppt_count': 2,
            'max_dc_current': 30.0,
            'price_euro': 2500.0,
            'additional_cost_netto': 100.0,
            'warranty_years': 12,
            'weight_kg': 25.0,
            'description': 'Medium inverter',
            'technology': 'String',
            'smart_home': True
        },
        {
            'id': 3,
            'model_name': 'Large Inverter 15kW',
            'brand': 'BrandC',
            'power_kw': 15.0,
            'efficiency_percent': 98.0,
            'max_dc_voltage': 1000.0,
            'mppt_count': 3,
            'max_dc_current': 35.0,
            'price_euro': 3500.0,
            'additional_cost_netto': 150.0,
            'warranty_years': 15,
            'weight_kg': 35.0,
            'description': 'Large inverter',
            'technology': 'Hybrid',
            'smart_home': True
        }
    ]


class TestInverterDataExtraction:
    """Test inverter data extraction"""
    
    def test_extract_inverter_data_basic(self, inverter_service, sample_inverter_data):
        """Test basic inverter data extraction"""
        result = inverter_service.extract_inverter_data(sample_inverter_data)
        
        assert result['id'] == 1
        assert result['model_name'] == 'Test Inverter 10kW'
        assert result['manufacturer'] == 'TestBrand'
        assert result['power_kw'] == 10.0
        assert result['efficiency_percent'] == 97.5
    
    def test_extract_inverter_data_features(self, inverter_service, sample_inverter_data):
        """Test feature extraction"""
        result = inverter_service.extract_inverter_data(sample_inverter_data)
        
        assert 'features' in result
        assert 'Smart Home Integration' in result['features']
    
    def test_extract_inverter_data_missing_fields(self, inverter_service):
        """Test extraction with missing fields"""
        minimal_data = {
            'id': 1,
            'model_name': 'Minimal Inverter'
        }
        
        result = inverter_service.extract_inverter_data(minimal_data)
        
        assert result['id'] == 1
        assert result['model_name'] == 'Minimal Inverter'
        assert result['power_kw'] == 0.0  # Default value
        assert result['efficiency_percent'] == 97.0  # Default value


class TestInverterSelection:
    """Test inverter selection algorithm"""
    
    def test_select_inverter_optimal_match(self, inverter_service, sample_inverters_list):
        """Test selection with optimal match"""
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.select_inverter(pv_power_kwp=10.0)
            
            assert result['selected_inverter']['power_kw'] == 10.0
            assert result['sizing_ratio'] == 1.0
            assert result['selection_score'] > 0
    
    def test_select_inverter_with_preferences(self, inverter_service, sample_inverters_list):
        """Test selection with manufacturer preference"""
        preferences = {'manufacturer': 'BrandA'}
        
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.select_inverter(
                pv_power_kwp=5.0,
                preferences=preferences
            )
            
            assert result['selected_inverter']['manufacturer'] == 'BrandA'
    
    def test_select_inverter_oversizing(self, inverter_service, sample_inverters_list):
        """Test selection with oversizing"""
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.select_inverter(pv_power_kwp=12.0)
            
            # Should select 15kW inverter for 12kWp system
            assert result['selected_inverter']['power_kw'] >= 12.0
            assert result['sizing_ratio'] <= 1.0
    
    def test_select_inverter_no_available(self, inverter_service):
        """Test selection with no available inverters"""
        with patch.object(inverter_service, '_get_available_inverters', return_value=[]):
            with pytest.raises(ValueError, match="No inverters available"):
                inverter_service.select_inverter(pv_power_kwp=10.0)
    
    def test_select_inverter_alternatives(self, inverter_service, sample_inverters_list):
        """Test that alternatives are provided"""
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.select_inverter(pv_power_kwp=10.0)
            
            assert 'alternatives' in result
            assert len(result['alternatives']) > 0


class TestInverterSizing:
    """Test inverter sizing calculations"""
    
    def test_calculate_sizing_basic(self, inverter_service):
        """Test basic sizing calculation"""
        string_config = {
            'modules_per_string': 10,
            'number_of_strings': 2
        }
        
        result = inverter_service.calculate_inverter_sizing(
            pv_power_kwp=10.0,
            module_voltage=40.0,
            module_current=10.0,
            string_configuration=string_config
        )
        
        assert 'required_power_kw' in result
        assert 'recommended_power_range' in result
        assert 'dc_specifications' in result
        assert 'mppt_configuration' in result
    
    def test_calculate_sizing_voltage(self, inverter_service):
        """Test voltage calculations"""
        string_config = {
            'modules_per_string': 10,
            'number_of_strings': 2
        }
        
        result = inverter_service.calculate_inverter_sizing(
            pv_power_kwp=10.0,
            module_voltage=40.0,
            module_current=10.0,
            string_configuration=string_config
        )
        
        # String voltage = module_voltage * modules_per_string
        assert result['dc_specifications']['string_voltage'] == 400.0
        # Required max voltage with 20% safety margin
        assert result['dc_specifications']['required_max_voltage'] == 480.0
    
    def test_calculate_sizing_current(self, inverter_service):
        """Test current calculations"""
        string_config = {
            'modules_per_string': 10,
            'number_of_strings': 3
        }
        
        result = inverter_service.calculate_inverter_sizing(
            pv_power_kwp=15.0,
            module_voltage=40.0,
            module_current=10.0,
            string_configuration=string_config
        )
        
        # Total current = module_current * number_of_strings
        assert result['dc_specifications']['total_current'] == 30.0
        # Required max current with 10% safety margin
        assert result['dc_specifications']['required_max_current'] == 33.0
    
    def test_calculate_sizing_mppt(self, inverter_service):
        """Test MPPT configuration"""
        string_config = {
            'modules_per_string': 10,
            'number_of_strings': 4
        }
        
        result = inverter_service.calculate_inverter_sizing(
            pv_power_kwp=20.0,
            module_voltage=40.0,
            module_current=10.0,
            string_configuration=string_config
        )
        
        assert result['mppt_configuration']['recommended_mppt_count'] == 2
        assert result['mppt_configuration']['strings_per_mppt'] == 2


class TestCompatibilityCheck:
    """Test inverter compatibility checking"""
    
    def test_compatibility_check_compatible(self, inverter_service, sample_inverter_data):
        """Test compatibility check with compatible system"""
        pv_system = {
            'pv_power_kwp': 10.0,
            'string_voltage': 400.0,
            'total_current': 20.0,
            'number_of_strings': 2
        }
        
        result = inverter_service.check_inverter_compatibility(
            inverter=sample_inverter_data,
            pv_system=pv_system
        )
        
        assert result['is_compatible'] is True
        assert result['compatibility_score'] > 0
        assert len(result['checks']) > 0
    
    def test_compatibility_check_voltage_too_high(self, inverter_service, sample_inverter_data):
        """Test compatibility check with voltage too high"""
        pv_system = {
            'pv_power_kwp': 10.0,
            'string_voltage': 1100.0,  # Exceeds max_dc_voltage
            'total_current': 20.0,
            'number_of_strings': 2
        }
        
        result = inverter_service.check_inverter_compatibility(
            inverter=sample_inverter_data,
            pv_system=pv_system
        )
        
        assert result['is_compatible'] is False
        assert any('Spannungskompatibilität' in check['check'] for check in result['checks'])
    
    def test_compatibility_check_current_too_high(self, inverter_service, sample_inverter_data):
        """Test compatibility check with current too high"""
        pv_system = {
            'pv_power_kwp': 10.0,
            'string_voltage': 400.0,
            'total_current': 80.0,  # Exceeds max_dc_current per MPPT
            'number_of_strings': 2
        }
        
        result = inverter_service.check_inverter_compatibility(
            inverter=sample_inverter_data,
            pv_system=pv_system
        )
        
        assert result['is_compatible'] is False
        assert any('Stromkompatibilität' in check['check'] for check in result['checks'])
    
    def test_compatibility_check_oversized(self, inverter_service, sample_inverter_data):
        """Test compatibility check with oversized inverter"""
        pv_system = {
            'pv_power_kwp': 5.0,  # Much smaller than inverter
            'string_voltage': 400.0,
            'total_current': 15.0,
            'number_of_strings': 2
        }
        
        result = inverter_service.check_inverter_compatibility(
            inverter=sample_inverter_data,
            pv_system=pv_system
        )
        
        assert len(result['warnings']) > 0
        assert 'überdimensioniert' in result['warnings'][0].lower()


class TestMultiInverterConfiguration:
    """Test multi-inverter configuration"""
    
    def test_single_inverter_small_system(self, inverter_service, sample_inverters_list):
        """Test that small systems get single inverter"""
        system_layout = {
            'roof_sections': [
                {'section_id': '1', 'orientation': 180, 'tilt': 30, 'area_sqm': 50, 'power_kwp': 10.0}
            ]
        }
        
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.create_multi_inverter_configuration(
                pv_power_kwp=10.0,
                system_layout=system_layout
            )
            
            assert result['configuration_type'] == 'single'
            assert result['inverter_count'] == 1
    
    def test_multi_inverter_large_system(self, inverter_service, sample_inverters_list):
        """Test that large systems get multiple inverters"""
        system_layout = {
            'roof_sections': [
                {'section_id': '1', 'orientation': 180, 'tilt': 30, 'area_sqm': 200, 'power_kwp': 40.0}
            ]
        }
        
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.create_multi_inverter_configuration(
                pv_power_kwp=40.0,
                system_layout=system_layout
            )
            
            assert result['configuration_type'] == 'multi'
            assert result['inverter_count'] > 1
    
    def test_multi_inverter_multiple_orientations(self, inverter_service, sample_inverters_list):
        """Test multi-inverter for multiple roof orientations"""
        system_layout = {
            'roof_sections': [
                {'section_id': '1', 'orientation': 180, 'tilt': 30, 'area_sqm': 50, 'power_kwp': 10.0},
                {'section_id': '2', 'orientation': 90, 'tilt': 30, 'area_sqm': 50, 'power_kwp': 10.0}
            ]
        }
        
        with patch.object(inverter_service, '_get_available_inverters', return_value=sample_inverters_list):
            result = inverter_service.create_multi_inverter_configuration(
                pv_power_kwp=20.0,
                system_layout=system_layout
            )
            
            assert result['configuration_type'] == 'multi'
            assert result['inverter_count'] == 2  # One per roof section
            assert 'power_distribution' in result


class TestMonitoringIntegration:
    """Test monitoring integration"""
    
    def test_monitoring_supported(self, inverter_service, sample_inverter_data):
        """Test monitoring integration for supported inverter"""
        monitoring_config = {
            'protocol': 'Modbus TCP',
            'update_interval': 60,
            'retention_days': 365
        }
        
        result = inverter_service.integrate_monitoring(
            inverter=sample_inverter_data,
            monitoring_config=monitoring_config
        )
        
        assert result['monitoring_supported'] is True
        assert 'data_points' in result
        assert 'alerts' in result
        assert 'api_endpoints' in result
    
    def test_monitoring_not_supported(self, inverter_service):
        """Test monitoring integration for unsupported inverter"""
        inverter_data = {
            'id': 1,
            'model_name': 'Basic Inverter',
            'brand': 'BasicBrand',
            'power_kw': 5.0,
            'technology': 'Basic',
            'smart_home': False
        }
        
        monitoring_config = {
            'protocol': 'Modbus TCP',
            'update_interval': 60
        }
        
        result = inverter_service.integrate_monitoring(
            inverter=inverter_data,
            monitoring_config=monitoring_config
        )
        
        assert result['monitoring_supported'] is False
        assert 'alternative' in result
    
    def test_monitoring_data_points(self, inverter_service, sample_inverter_data):
        """Test that monitoring includes all required data points"""
        monitoring_config = {'protocol': 'Modbus TCP'}
        
        result = inverter_service.integrate_monitoring(
            inverter=sample_inverter_data,
            monitoring_config=monitoring_config
        )
        
        required_data_points = [
            'AC Power Output (kW)',
            'DC Power Input (kW)',
            'Efficiency (%)',
            'Daily Energy (kWh)',
            'Total Energy (kWh)'
        ]
        
        for data_point in required_data_points:
            assert data_point in result['data_points']


class TestInverterScoring:
    """Test inverter scoring algorithm"""
    
    def test_score_optimal_power(self, inverter_service):
        """Test scoring with optimal power match"""
        inverter = {
            'power_kw': 10.0,
            'efficiency_percent': 97.0,
            'price_euro': 2500.0
        }
        
        score = inverter_service._score_inverter(
            inverter=inverter,
            optimal_power_kw=10.0,
            min_power_kw=8.0,
            max_power_kw=12.0,
            preferences={}
        )
        
        assert score > 50  # Should get good score for optimal match
    
    def test_score_high_efficiency(self, inverter_service):
        """Test that high efficiency increases score"""
        inverter_high_eff = {
            'power_kw': 10.0,
            'efficiency_percent': 98.0,
            'price_euro': 2500.0
        }
        
        inverter_low_eff = {
            'power_kw': 10.0,
            'efficiency_percent': 95.0,
            'price_euro': 2500.0
        }
        
        score_high = inverter_service._score_inverter(
            inverter=inverter_high_eff,
            optimal_power_kw=10.0,
            min_power_kw=8.0,
            max_power_kw=12.0,
            preferences={}
        )
        
        score_low = inverter_service._score_inverter(
            inverter=inverter_low_eff,
            optimal_power_kw=10.0,
            min_power_kw=8.0,
            max_power_kw=12.0,
            preferences={}
        )
        
        assert score_high > score_low
    
    def test_score_manufacturer_preference(self, inverter_service):
        """Test that manufacturer preference increases score"""
        inverter = {
            'brand': 'PreferredBrand',
            'power_kw': 10.0,
            'efficiency_percent': 97.0,
            'price_euro': 2500.0
        }
        
        score_with_pref = inverter_service._score_inverter(
            inverter=inverter,
            optimal_power_kw=10.0,
            min_power_kw=8.0,
            max_power_kw=12.0,
            preferences={'manufacturer': 'PreferredBrand'}
        )
        
        score_without_pref = inverter_service._score_inverter(
            inverter=inverter,
            optimal_power_kw=10.0,
            min_power_kw=8.0,
            max_power_kw=12.0,
            preferences={}
        )
        
        assert score_with_pref > score_without_pref


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
