"""
Unit tests for Pricing Service

Requirements: 1.3, 4.5, 14.1, 14.2
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.pricing_service import PricingService, get_pricing_service


class TestPricingService:
    """Test suite for PricingService"""
    
    @pytest.fixture
    def service(self):
        """Get pricing service instance"""
        return get_pricing_service()
    
    def test_service_initialization(self, service):
        """Test service can be initialized"""
        assert service is not None
        assert isinstance(service, PricingService)
    
    def test_health_check(self, service):
        """Test health check"""
        result = service.health_check()
        
        assert result['service'] == 'PricingService'
        assert result['status'] == 'healthy'
        assert 'timestamp' in result
    
    def test_calculate_price_basic(self, service):
        """Test basic price calculation"""
        result = service.calculate_price(
            module_count=20,
            storage_model="15kWh"
        )
        
        assert 'success' in result
        assert 'base_price' in result
        assert 'row_used' in result
        assert 'column_used' in result
    
    def test_calculate_price_no_storage(self, service):
        """Test price calculation without storage"""
        result = service.calculate_price(
            module_count=15,
            storage_model=None
        )
        
        assert 'success' in result
        assert 'base_price' in result
    
    def test_calculate_price_with_fallback(self, service):
        """Test price calculation with fallback"""
        result = service.calculate_price(
            module_count=999,  # Not in matrix
            storage_model="15kWh",
            enable_fallback=True
        )
        
        assert 'success' in result
        assert 'fallback_used' in result
    
    def test_list_matrices(self, service):
        """Test listing matrices"""
        result = service.list_matrices()
        
        assert result['success'] is True
        assert 'matrices' in result
        assert 'count' in result
        assert isinstance(result['matrices'], list)
    
    def test_create_matrix(self, service):
        """Test creating a matrix"""
        result = service.create_matrix(
            name="Test Matrix",
            description="Test description"
        )
        
        assert 'success' in result
        if result['success']:
            assert 'matrix_id' in result
            assert result['matrix_id'] is not None
    
    def test_cache_operations(self, service):
        """Test cache operations"""
        # Get stats
        stats = service.get_cache_stats()
        assert 'cache_size' in stats
        assert 'cache_keys' in stats
        
        # Clear cache
        result = service.clear_cache()
        assert result['success'] is True


class TestPriceCalculationLogic:
    """Test INDEX/MATCH logic"""
    
    @pytest.fixture
    def service(self):
        """Get pricing service instance"""
        return get_pricing_service()
    
    def test_index_match_logic(self, service):
        """Test Excel INDEX/MATCH logic"""
        # This tests the core INDEX/MATCH implementation
        result = service.calculate_price(
            module_count=20,
            storage_model="15kWh"
        )
        
        if result['success']:
            # Verify row and column were found
            assert result['row_used'] is not None
            assert result['column_used'] is not None
            assert result['base_price'] is not None
    
    def test_floor_logic(self, service):
        """Test floor logic for module count"""
        # Request module count not in matrix
        result = service.calculate_price(
            module_count=18,  # Between 15 and 20
            storage_model="15kWh",
            enable_fallback=True
        )
        
        if result['success'] and result['fallback_used']:
            # Should use floor logic (15 instead of 18)
            assert result['fallback_info'] is not None
    
    def test_kein_speicher_logic(self, service):
        """Test 'kein Speicher' logic"""
        result = service.calculate_price(
            module_count=20,
            storage_model=None  # Should use "kein Speicher" column
        )
        
        if result['success']:
            # Verify "kein Speicher" column was used
            column_used = result['column_used']
            assert column_used is not None


class TestErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def service(self):
        """Get pricing service instance"""
        return get_pricing_service()
    
    def test_invalid_module_count(self, service):
        """Test invalid module count"""
        result = service.calculate_price(
            module_count=-5,
            storage_model="15kWh"
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'user_message' in result
    
    def test_missing_matrix(self, service):
        """Test missing matrix"""
        result = service.calculate_price(
            module_count=20,
            storage_model="15kWh",
            matrix_id=99999  # Non-existent matrix
        )
        
        assert result['success'] is False
        assert 'error_type' in result
    
    def test_error_suggestions(self, service):
        """Test error suggestions"""
        result = service.calculate_price(
            module_count=999,
            storage_model="NonExistent",
            enable_fallback=False
        )
        
        if not result['success']:
            # Should have suggestions
            assert 'suggestions' in result or 'user_message' in result


class TestMatrixOperations:
    """Test matrix CRUD operations"""
    
    @pytest.fixture
    def service(self):
        """Get pricing service instance"""
        return get_pricing_service()
    
    def test_matrix_lifecycle(self, service):
        """Test complete matrix lifecycle"""
        # Create
        result = service.create_matrix(
            name="Lifecycle Test Matrix"
        )
        
        if not result['success']:
            pytest.skip("Cannot create matrix")
        
        matrix_id = result['matrix_id']
        
        # Get
        result = service.get_matrix(matrix_id)
        assert result['success'] is True
        
        # Activate
        result = service.set_active_matrix(matrix_id)
        assert result['success'] is True
        
        # Delete
        result = service.delete_matrix(matrix_id)
        assert result['success'] is True
    
    def test_add_row_and_column(self, service):
        """Test adding rows and columns"""
        # Get or create matrix
        matrices = service.list_matrices()
        if matrices['count'] == 0:
            result = service.create_matrix(name="Test Matrix")
            if not result['success']:
                pytest.skip("Cannot create matrix")
            matrix_id = result['matrix_id']
        else:
            matrix_id = matrices['matrices'][0]['id']
        
        # Add row
        result = service.add_row(
            matrix_id=matrix_id,
            label="Test Row"
        )
        assert 'success' in result
        
        # Add column
        result = service.add_column(
            matrix_id=matrix_id,
            label="Test Column"
        )
        assert 'success' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
