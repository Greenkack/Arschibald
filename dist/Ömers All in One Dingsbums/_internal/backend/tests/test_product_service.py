"""
Tests for Product Management Service

Unit tests for the ProductService class.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.product_service import ProductService


@pytest.fixture
def mock_product_db():
    """Mock product_db module"""
    mock_module = Mock()
    mock_module.DB_AVAILABLE = True
    mock_module.add_product = Mock()
    mock_module.get_product_by_id = Mock()
    mock_module.get_product_by_model_name = Mock()
    mock_module.update_product = Mock()
    mock_module.delete_product = Mock()
    mock_module.list_products = Mock()
    mock_module.list_product_categories = Mock()
    mock_module.update_product_image = Mock()
    return mock_module


@pytest.fixture
def product_service(mock_product_db):
    """Create ProductService instance with mocked product_db"""
    with patch('product_db', mock_product_db):
        service = ProductService()
        service._product_db_module = mock_product_db
        service._set_initialized(True)
        return service


@pytest.fixture
def sample_product():
    """Sample product data"""
    return {
        'id': 1,
        'category': 'Modul',
        'model_name': 'TestModule 400W',
        'brand': 'TestBrand',
        'price_euro': 200.0,
        'capacity_w': 400.0,
        'warranty_years': 25,
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-01T00:00:00'
    }


class TestProductServiceInitialization:
    """Test service initialization"""
    
    def test_service_creation(self):
        """Test that service can be created"""
        service = ProductService()
        assert service is not None
        assert service.service_name == "product_management"
    
    def test_service_initialization(self, mock_product_db):
        """Test service initialization"""
        with patch('product_db', mock_product_db):
            service = ProductService()
            service.initialize()
            assert service.is_initialized
            assert service._product_db_module is not None


class TestProductServiceHealthCheck:
    """Test health check functionality"""
    
    def test_health_check_healthy(self, product_service, mock_product_db):
        """Test health check when service is healthy"""
        mock_product_db.list_products.return_value = [{'id': 1}, {'id': 2}]
        
        result = product_service.health_check()
        
        assert result.status.value == "healthy"
        assert result.details['product_count'] == 2
    
    def test_health_check_not_initialized(self):
        """Test health check when service is not initialized"""
        service = ProductService()
        result = service.health_check()
        
        assert result.status.value == "unhealthy"
        assert "not initialized" in result.message.lower()
    
    def test_health_check_db_unavailable(self, product_service, mock_product_db):
        """Test health check when database is unavailable"""
        mock_product_db.DB_AVAILABLE = False
        
        result = product_service.health_check()
        
        assert result.status.value == "degraded"
        assert "database not available" in result.message.lower()


class TestProductServiceCRUD:
    """Test CRUD operations"""
    
    def test_create_product_success(self, product_service, mock_product_db, sample_product):
        """Test successful product creation"""
        mock_product_db.add_product.return_value = 1
        mock_product_db.get_product_by_id.return_value = sample_product
        
        product_data = {
            'category': 'Modul',
            'model_name': 'TestModule 400W',
            'brand': 'TestBrand',
            'price_euro': 200.0
        }
        
        result = product_service.create_product(product_data)
        
        assert result['id'] == 1
        assert result['model_name'] == 'TestModule 400W'
        mock_product_db.add_product.assert_called_once()
    
    def test_create_product_missing_category(self, product_service):
        """Test product creation with missing category"""
        product_data = {'model_name': 'TestModule 400W'}
        
        with pytest.raises(ValueError, match="category is required"):
            product_service.create_product(product_data)
    
    def test_create_product_missing_model_name(self, product_service):
        """Test product creation with missing model_name"""
        product_data = {'category': 'Modul'}
        
        with pytest.raises(ValueError, match="model_name is required"):
            product_service.create_product(product_data)
    
    def test_get_product_success(self, product_service, mock_product_db, sample_product):
        """Test successful product retrieval"""
        mock_product_db.get_product_by_id.return_value = sample_product
        
        result = product_service.get_product(1)
        
        assert result['id'] == 1
        assert result['model_name'] == 'TestModule 400W'
        mock_product_db.get_product_by_id.assert_called_once_with(1)
    
    def test_get_product_not_found(self, product_service, mock_product_db):
        """Test product retrieval when product not found"""
        mock_product_db.get_product_by_id.return_value = None
        
        result = product_service.get_product(999)
        
        assert result is None
    
    def test_get_product_by_model_name_success(self, product_service, mock_product_db, sample_product):
        """Test successful product retrieval by model name"""
        mock_product_db.get_product_by_model_name.return_value = sample_product
        
        result = product_service.get_product_by_model_name('TestModule 400W')
        
        assert result['id'] == 1
        assert result['model_name'] == 'TestModule 400W'
    
    def test_get_product_by_model_name_empty(self, product_service):
        """Test product retrieval with empty model name"""
        with pytest.raises(ValueError, match="cannot be empty"):
            product_service.get_product_by_model_name('')
    
    def test_update_product_success(self, product_service, mock_product_db, sample_product):
        """Test successful product update"""
        updated_product = sample_product.copy()
        updated_product['price_euro'] = 220.0
        
        mock_product_db.get_product_by_id.side_effect = [sample_product, updated_product]
        mock_product_db.update_product.return_value = True
        
        update_data = {'price_euro': 220.0}
        result = product_service.update_product(1, update_data)
        
        assert result['price_euro'] == 220.0
        mock_product_db.update_product.assert_called_once()
    
    def test_update_product_not_found(self, product_service, mock_product_db):
        """Test product update when product not found"""
        mock_product_db.get_product_by_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            product_service.update_product(999, {'price_euro': 220.0})
    
    def test_delete_product_success(self, product_service, mock_product_db, sample_product):
        """Test successful product deletion"""
        mock_product_db.get_product_by_id.return_value = sample_product
        mock_product_db.delete_product.return_value = True
        
        result = product_service.delete_product(1)
        
        assert result is True
        mock_product_db.delete_product.assert_called_once_with(1)
    
    def test_delete_product_not_found(self, product_service, mock_product_db):
        """Test product deletion when product not found"""
        mock_product_db.get_product_by_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            product_service.delete_product(999)


class TestProductServiceSearch:
    """Test search and filtering functionality"""
    
    def test_list_products_no_filters(self, product_service, mock_product_db):
        """Test listing all products"""
        products = [
            {'id': 1, 'model_name': 'Product 1', 'category': 'Modul'},
            {'id': 2, 'model_name': 'Product 2', 'category': 'Wechselrichter'}
        ]
        mock_product_db.list_products.return_value = products
        
        result = product_service.list_products()
        
        assert len(result) == 2
        mock_product_db.list_products.assert_called_once()
    
    def test_list_products_with_category_filter(self, product_service, mock_product_db):
        """Test listing products with category filter"""
        products = [{'id': 1, 'model_name': 'Product 1', 'category': 'Modul'}]
        mock_product_db.list_products.return_value = products
        
        result = product_service.list_products(category='Modul')
        
        assert len(result) == 1
        assert result[0]['category'] == 'Modul'
    
    def test_list_products_with_search(self, product_service, mock_product_db):
        """Test listing products with search term"""
        products = [
            {'id': 1, 'model_name': 'TestModule 400W', 'brand': 'TestBrand', 'description': ''},
            {'id': 2, 'model_name': 'OtherModule 500W', 'brand': 'OtherBrand', 'description': ''}
        ]
        mock_product_db.list_products.return_value = products
        
        result = product_service.list_products(search_term='TestModule')
        
        assert len(result) == 1
        assert result[0]['model_name'] == 'TestModule 400W'
    
    def test_list_products_with_pagination(self, product_service, mock_product_db):
        """Test listing products with pagination"""
        products = [
            {'id': i, 'model_name': f'Product {i}', 'category': 'Modul'}
            for i in range(1, 11)
        ]
        mock_product_db.list_products.return_value = products
        
        result = product_service.list_products(limit=5, offset=3)
        
        assert len(result) == 5
        assert result[0]['id'] == 4  # After skipping 3
    
    def test_search_products_with_filters(self, product_service, mock_product_db):
        """Test advanced product search"""
        products = [
            {'id': 1, 'model_name': 'Product 1', 'brand': 'BrandA', 'price_euro': 100.0, 'category': 'Modul'},
            {'id': 2, 'model_name': 'Product 2', 'brand': 'BrandB', 'price_euro': 200.0, 'category': 'Modul'},
            {'id': 3, 'model_name': 'Product 3', 'brand': 'BrandA', 'price_euro': 300.0, 'category': 'Modul'}
        ]
        mock_product_db.list_products.return_value = products
        
        filters = {'brand': 'BrandA', 'price_min': 150.0}
        result = product_service.search_products('Product', filters=filters)
        
        assert len(result) == 1
        assert result[0]['id'] == 3
    
    def test_get_categories(self, product_service, mock_product_db):
        """Test getting product categories"""
        categories = ['Modul', 'Wechselrichter', 'Batteriespeicher']
        mock_product_db.list_product_categories.return_value = categories
        
        result = product_service.get_categories()
        
        assert len(result) == 3
        assert 'Modul' in result


class TestProductServiceImageManagement:
    """Test image management functionality"""
    
    def test_upload_product_image_base64(self, product_service, mock_product_db, sample_product):
        """Test uploading product image with base64 data"""
        updated_product = sample_product.copy()
        updated_product['image_base64'] = 'base64encodeddata'
        
        mock_product_db.get_product_by_id.side_effect = [sample_product, updated_product]
        mock_product_db.update_product_image.return_value = True
        
        result = product_service.upload_product_image(1, 'base64encodeddata', 'base64')
        
        assert result['image_base64'] == 'base64encodeddata'
        mock_product_db.update_product_image.assert_called_once()
    
    def test_upload_product_image_product_not_found(self, product_service, mock_product_db):
        """Test uploading image when product not found"""
        mock_product_db.get_product_by_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            product_service.upload_product_image(999, 'base64data', 'base64')
    
    def test_delete_product_image(self, product_service, mock_product_db, sample_product):
        """Test deleting product image"""
        updated_product = sample_product.copy()
        updated_product['image_base64'] = None
        
        mock_product_db.get_product_by_id.side_effect = [sample_product, updated_product]
        mock_product_db.update_product_image.return_value = True
        
        result = product_service.delete_product_image(1)
        
        assert result['image_base64'] is None
        mock_product_db.update_product_image.assert_called_once_with(1, None)


class TestProductServiceImportExport:
    """Test import/export functionality"""
    
    def test_export_products_json(self, product_service, mock_product_db):
        """Test exporting products to JSON"""
        products = [
            {'id': 1, 'model_name': 'Product 1'},
            {'id': 2, 'model_name': 'Product 2'}
        ]
        mock_product_db.list_products.return_value = products
        
        result = product_service.export_products(format='json')
        
        assert result['format'] == 'json'
        assert result['product_count'] == 2
        assert len(result['products']) == 2
    
    def test_export_products_csv(self, product_service, mock_product_db):
        """Test exporting products to CSV"""
        products = [
            {'id': 1, 'model_name': 'Product 1', 'price_euro': 100.0},
            {'id': 2, 'model_name': 'Product 2', 'price_euro': 200.0}
        ]
        mock_product_db.list_products.return_value = products
        
        result = product_service.export_products(format='csv')
        
        assert result['format'] == 'csv'
        assert 'csv_data' in result
        assert 'Product 1' in result['csv_data']
    
    def test_import_products_json(self, product_service, mock_product_db):
        """Test importing products from JSON"""
        import_data = {
            'products': [
                {'category': 'Modul', 'model_name': 'New Product 1', 'price_euro': 100.0},
                {'category': 'Modul', 'model_name': 'New Product 2', 'price_euro': 200.0}
            ]
        }
        
        mock_product_db.get_product_by_model_name.return_value = None
        mock_product_db.add_product.side_effect = [1, 2]
        
        result = product_service.import_products(import_data, format='json')
        
        assert result['total'] == 2
        assert result['created'] == 2
        assert result['failed'] == 0
    
    def test_import_products_update_existing(self, product_service, mock_product_db, sample_product):
        """Test importing products with update_existing=True"""
        import_data = {
            'products': [
                {'category': 'Modul', 'model_name': 'TestModule 400W', 'price_euro': 250.0}
            ]
        }
        
        mock_product_db.get_product_by_model_name.return_value = sample_product
        mock_product_db.update_product.return_value = True
        
        result = product_service.import_products(import_data, format='json', update_existing=True)
        
        assert result['total'] == 1
        assert result['updated'] == 1
        assert result['created'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
