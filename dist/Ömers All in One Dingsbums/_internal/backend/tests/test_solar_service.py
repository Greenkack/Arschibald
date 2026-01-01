"""
Tests for Solar Calculator Service

This module contains unit tests for the Solar Calculator Service.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from backend.services.solar_service import SolarCalculatorService, get_solar_service
from backend.models.solar_schemas import SolarCalculationRequest, RoofOrientation
from backend.core.base_service import ServiceStatus


class TestSolarCalculatorService:
    """Test suite for Solar Calculator Service"""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test"""
        service = SolarCalculatorService()
        service.initialize()
        return service
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample calculation request"""
        return SolarCalculationRequest(
            customer_name="Test Customer",
            latitude=48.1351,
            longitude=11.5820,
            roof_area_m2=50.0,
            roof_orientation=RoofOrientation.SOUTH,
            roof_inclination_deg=30.0,
            module_quantity=20,
            module_capacity_w=350.0,
            annual_consumption_kwh_yr=4000.0,
            electricity_price_kwh=0.30,
            include_storage=False
        )
    
    def test_service_initialization(self, service):
        """Test that service initializes correctly"""
        assert service.is_initialized
        assert service.service_name == "solar_calculator"
        assert service.legacy_module is not None
    
    def test_health_check_healthy(self, service):
        """Test health check returns healthy status"""
        health = service.health_check()
        assert health.is_healthy()
        assert health.status == ServiceStatus.HEALTHY
    
    def test_health_check_uninitialized(self):
        """Test health check on uninitialized service"""
        service = SolarCalculatorService()
        health = service.health_check()
        assert not health.is_healthy()
        assert health.status == ServiceStatus.UNHEALTHY
    
    def test_calculate_solar_system_basic(self, service, sample_request):
        """Test basic solar system calculation"""
        result = service.calculate_solar_system(sample_request)
        
        # Check that result is returned
        assert result is not None
        
        # Check system sizing
        assert result.system_sizing.system_size_kwp > 0
        assert result.system_sizing.module_count == 20
        
        # Check energy production
        assert result.energy_production.annual_production_kwh > 0
        
        # Check economic analysis
        assert result.economic_analysis.total_investment_cost_net >= 0
        assert result.economic_analysis.payback_period_years >= 0
        
        # Check environmental impact
        assert result.environmental_impact.annual_co2_savings_kg >= 0
    
    def test_calculate_with_storage(self, service, sample_request):
        """Test calculation with battery storage"""
        sample_request.include_storage = True
        sample_request.selected_storage_capacity_kwh = 10.0
        
        result = service.calculate_solar_system(sample_request)
        
        # Check that storage analysis is included
        assert result.storage_analysis is not None
        assert result.storage_analysis.storage_capacity_kwh == 10.0
    
    def test_cache_functionality(self, service, sample_request):
        """Test that caching works correctly"""
        # First calculation
        result1 = service.calculate_solar_system(sample_request)
        
        # Second calculation with same parameters should be cached
        result2 = service.calculate_solar_system(sample_request)
        
        # Results should be identical
        assert result1.system_sizing.system_size_kwp == result2.system_sizing.system_size_kwp
        assert result1.energy_production.annual_production_kwh == result2.energy_production.annual_production_kwh
        
        # Check cache stats
        stats = service.get_cache_stats()
        assert stats["total_entries"] >= 1
    
    def test_cache_key_generation(self, service, sample_request):
        """Test that cache keys are generated correctly"""
        key1 = service._generate_cache_key(sample_request)
        key2 = service._generate_cache_key(sample_request)
        
        # Same request should generate same key
        assert key1 == key2
        
        # Different request should generate different key
        sample_request.module_quantity = 25
        key3 = service._generate_cache_key(sample_request)
        assert key1 != key3
    
    def test_clear_cache(self, service, sample_request):
        """Test cache clearing"""
        # Add something to cache
        service.calculate_solar_system(sample_request)
        
        # Clear cache
        count = service.clear_cache()
        assert count >= 1
        
        # Cache should be empty
        stats = service.get_cache_stats()
        assert stats["total_entries"] == 0
    
    def test_invalid_coordinates(self, service, sample_request):
        """Test handling of invalid coordinates"""
        sample_request.latitude = 0.0
        sample_request.longitude = 0.0
        
        # Should still calculate (using manual calculation)
        result = service.calculate_solar_system(sample_request)
        assert result is not None
        assert result.energy_production.pvgis_source == "Manuelle Berechnung" or not result.energy_production.pvgis_data_used
    
    def test_zero_module_quantity(self, service, sample_request):
        """Test calculation with zero modules"""
        sample_request.module_quantity = 0
        
        result = service.calculate_solar_system(sample_request)
        
        # Should return zero production
        assert result.system_sizing.system_size_kwp == 0.0
        assert result.energy_production.annual_production_kwh == 0.0
    
    def test_get_solar_service_singleton(self):
        """Test that get_solar_service returns singleton"""
        service1 = get_solar_service()
        service2 = get_solar_service()
        
        # Should be the same instance
        assert service1 is service2
        assert service1.is_initialized


class TestSolarCalculationRequest:
    """Test suite for SolarCalculationRequest model"""
    
    def test_valid_request(self):
        """Test creating a valid request"""
        request = SolarCalculationRequest(
            latitude=48.1351,
            longitude=11.5820,
            roof_orientation=RoofOrientation.SOUTH,
            roof_inclination_deg=30.0,
            module_quantity=20,
            annual_consumption_kwh_yr=4000.0
        )
        
        assert request.latitude == 48.1351
        assert request.roof_orientation == RoofOrientation.SOUTH
    
    def test_default_values(self):
        """Test default values are applied"""
        request = SolarCalculationRequest()
        
        assert request.roof_orientation == RoofOrientation.SOUTH
        assert request.roof_inclination_deg == 30.0
        assert request.electricity_price_kwh == 0.30
        assert request.include_storage is False
    
    def test_invalid_latitude(self):
        """Test validation of latitude"""
        with pytest.raises(ValueError):
            SolarCalculationRequest(latitude=100.0)  # Out of range
    
    def test_invalid_longitude(self):
        """Test validation of longitude"""
        with pytest.raises(ValueError):
            SolarCalculationRequest(longitude=200.0)  # Out of range
    
    def test_negative_consumption(self):
        """Test validation of consumption"""
        with pytest.raises(ValueError):
            SolarCalculationRequest(annual_consumption_kwh_yr=-1000.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
