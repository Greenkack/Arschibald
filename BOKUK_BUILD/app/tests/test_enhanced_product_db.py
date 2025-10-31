"""Tests for Enhanced Product Database

Tests für die erweiterte Produktdatenbank mit neuen Spalten,
dynamischen Keys und Reset-Funktionalität.
"""

import sqlite3
from unittest.mock import patch

import pytest


# Mock the database connection for testing
@pytest.fixture
def mock_db_connection():
    """Create a temporary in-memory database for testing"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


@pytest.fixture
def mock_product_db(mock_db_connection):
    """Mock product_db module with test database"""
    with patch('product_db.get_db_connection_safe_pd', return_value=mock_db_connection):
        import product_db
        # Initialize the test database
        product_db.create_product_table(mock_db_connection)
        yield product_db


class TestEnhancedProductDatabase:
    """Test enhanced product database functionality"""

    def test_create_product_table_with_new_columns(
            self, mock_product_db, mock_db_connection):
        """Test that product table is created with all new columns"""
        cursor = mock_db_connection.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        # Check that all new columns are present
        expected_new_columns = [
            'technology', 'feature', 'design', 'upgrade', 'max_kwh_capacity',
            'outdoor_opt', 'self_supply_feature', 'shadow_fading', 'smart_home'
        ]

        for column in expected_new_columns:
            assert column in columns, f"Column {column} not found in products table"

    def test_add_product_with_new_fields(self, mock_product_db):
        """Test adding product with new enhanced fields"""
        product_data = {
            'category': 'PV Module',
            'model_name': 'Test PV Module 400W',
            'brand': 'TestBrand',
            'price_euro': 180.0,
            'capacity_w': 400.0,
            'technology': 'Monokristallin',
            'feature': 'High Efficiency',
            'design': 'All-Black',
            'shadow_fading': 1,
            'length_m': 2.0,
            'width_m': 1.0,
            'efficiency_percent': 21.5
        }

        product_id = mock_product_db.add_product(product_data)
        assert product_id is not None

        # Verify product was added with all fields
        added_product = mock_product_db.get_product_by_id(product_id)
        assert added_product is not None
        assert added_product['technology'] == 'Monokristallin'
        assert added_product['feature'] == 'High Efficiency'
        assert added_product['design'] == 'All-Black'
        assert added_product['shadow_fading'] == 1

    def test_add_inverter_with_specific_fields(self, mock_product_db):
        """Test adding inverter with inverter-specific fields"""
        inverter_data = {
            'category': 'Wechselrichter',
            'model_name': 'Test Inverter 10kW',
            'brand': 'InverterBrand',
            'price_euro': 800.0,
            'power_kw': 10.0,
            'technology': 'MPPT',
            'feature': 'String Inverter',
            'outdoor_opt': 1,
            'self_supply_feature': 1,
            'smart_home': 1,
            'efficiency_percent': 97.5
        }

        product_id = mock_product_db.add_product(inverter_data)
        assert product_id is not None

        added_product = mock_product_db.get_product_by_id(product_id)
        assert added_product['outdoor_opt'] == 1
        assert added_product['self_supply_feature'] == 1
        assert added_product['smart_home'] == 1

    def test_add_battery_with_specific_fields(self, mock_product_db):
        """Test adding battery with battery-specific fields"""
        battery_data = {
            'category': 'Batteriespeicher',
            'model_name': 'Test Battery 10kWh',
            'brand': 'BatteryBrand',
            'price_euro': 3500.0,
            'storage_power_kw': 5.0,
            'max_kwh_capacity': 10.0,
            'max_cycles': 6000,
            'technology': 'Lithium-Ion',
            'feature': 'High Capacity',
            'upgrade': 'Modular'
        }

        product_id = mock_product_db.add_product(battery_data)
        assert product_id is not None

        added_product = mock_product_db.get_product_by_id(product_id)
        assert added_product['max_kwh_capacity'] == 10.0
        assert added_product['upgrade'] == 'Modular'


class TestDynamicKeyGeneration:
    """Test dynamic key generation for products"""

    def test_generate_pv_module_dynamic_keys(self, mock_product_db):
        """Test dynamic key generation for PV modules"""
        pv_product = {
            'id': 1,
            'category': 'PV Module',
            'model_name': 'Test PV 400W',
            'brand': 'TestBrand',
            'price_euro': 180.0,
            'capacity_w': 400.0,
            'technology': 'Monokristallin',
            'feature': 'High Efficiency',
            'design': 'All-Black',
            'shadow_fading': 1,
            'length_m': 2.0,
            'width_m': 1.0,
            'efficiency_percent': 21.5
        }

        dynamic_keys = mock_product_db.generate_product_dynamic_keys(
            pv_product, category_specific=True)

        # Check that PV-specific keys are generated
        assert 'TEST_PV_400W_ID' in dynamic_keys
        assert 'TEST_PV_400W_MODEL_NAME' in dynamic_keys
        assert 'TEST_PV_400W_CAPACITY_W' in dynamic_keys
        assert 'TEST_PV_400W_TECHNOLOGY' in dynamic_keys
        assert 'TEST_PV_400W_SHADOW_FADING' in dynamic_keys
        assert 'TEST_PV_400W_SHADOW_FADING_TEXT' in dynamic_keys

        # Check values
        assert dynamic_keys['TEST_PV_400W_CAPACITY_W'] == 400.0
        assert dynamic_keys['TEST_PV_400W_TECHNOLOGY'] == 'Monokristallin'
        assert dynamic_keys['TEST_PV_400W_SHADOW_FADING_TEXT'] == 'Ja'

    def test_generate_inverter_dynamic_keys(self, mock_product_db):
        """Test dynamic key generation for inverters"""
        inverter_product = {
            'id': 2,
            'category': 'Wechselrichter',
            'model_name': 'Test Inverter 10kW',
            'brand': 'InverterBrand',
            'price_euro': 800.0,
            'power_kw': 10.0,
            'technology': 'MPPT',
            'outdoor_opt': 1,
            'self_supply_feature': 1,
            'smart_home': 0,
            'efficiency_percent': 97.5
        }

        dynamic_keys = mock_product_db.generate_product_dynamic_keys(
            inverter_product, category_specific=True)

        # Check that inverter-specific keys are generated
        assert 'TEST_INVERTER_10KW_POWER_KW' in dynamic_keys
        assert 'TEST_INVERTER_10KW_OUTDOOR_OPT' in dynamic_keys
        assert 'TEST_INVERTER_10KW_OUTDOOR_OPT_TEXT' in dynamic_keys
        assert 'TEST_INVERTER_10KW_SELF_SUPPLY_FEATURE_TEXT' in dynamic_keys
        assert 'TEST_INVERTER_10KW_SMART_HOME_TEXT' in dynamic_keys

        # Check boolean text values
        assert dynamic_keys['TEST_INVERTER_10KW_OUTDOOR_OPT_TEXT'] == 'Ja'
        assert dynamic_keys['TEST_INVERTER_10KW_SELF_SUPPLY_FEATURE_TEXT'] == 'Ja'
        assert dynamic_keys['TEST_INVERTER_10KW_SMART_HOME_TEXT'] == 'Nein'

    def test_generate_battery_dynamic_keys(self, mock_product_db):
        """Test dynamic key generation for batteries"""
        battery_product = {
            'id': 3,
            'category': 'Batteriespeicher',
            'model_name': 'Test Battery 10kWh',
            'brand': 'BatteryBrand',
            'price_euro': 3500.0,
            'storage_power_kw': 5.0,
            'max_kwh_capacity': 10.0,
            'max_cycles': 6000,
            'technology': 'Lithium-Ion',
            'upgrade': 'Modular'
        }

        dynamic_keys = mock_product_db.generate_product_dynamic_keys(
            battery_product, category_specific=True)

        # Check that battery-specific keys are generated
        assert 'TEST_BATTERY_10KWH_STORAGE_POWER_KW' in dynamic_keys
        assert 'TEST_BATTERY_10KWH_MAX_KWH_CAPACITY' in dynamic_keys
        assert 'TEST_BATTERY_10KWH_MAX_CYCLES' in dynamic_keys
        assert 'TEST_BATTERY_10KWH_UPGRADE' in dynamic_keys

        # Check values
        assert dynamic_keys['TEST_BATTERY_10KWH_STORAGE_POWER_KW'] == 5.0
        assert dynamic_keys['TEST_BATTERY_10KWH_MAX_KWH_CAPACITY'] == 10.0
        assert dynamic_keys['TEST_BATTERY_10KWH_UPGRADE'] == 'Modular'

    def test_get_product_with_dynamic_keys(self, mock_product_db):
        """Test getting product with generated dynamic keys"""
        # Add a test product
        product_data = {
            'category': 'PV Module',
            'model_name': 'Test PV Module',
            'brand': 'TestBrand',
            'price_euro': 200.0,
            'capacity_w': 450.0,
            'technology': 'Monokristallin'
        }

        product_id = mock_product_db.add_product(product_data)

        # Get product with dynamic keys
        product_with_keys = mock_product_db.get_product_with_dynamic_keys(
            product_id)

        assert product_with_keys is not None
        assert 'dynamic_keys' in product_with_keys
        assert len(product_with_keys['dynamic_keys']) > 0
        assert 'TEST_PV_MODULE_ID' in product_with_keys['dynamic_keys']

    def test_get_products_with_dynamic_keys(self, mock_product_db):
        """Test getting all products with dynamic keys"""
        # Add multiple test products
        products_data = [
            {
                'category': 'PV Module',
                'model_name': 'PV Module 1',
                'brand': 'Brand1',
                'price_euro': 180.0,
                'capacity_w': 400.0
            },
            {
                'category': 'Wechselrichter',
                'model_name': 'Inverter 1',
                'brand': 'Brand2',
                'price_euro': 800.0,
                'power_kw': 10.0
            }
        ]

        for product_data in products_data:
            mock_product_db.add_product(product_data)

        # Get all products with dynamic keys
        products_with_keys = mock_product_db.get_products_with_dynamic_keys()

        assert len(products_with_keys) == 2
        for product in products_with_keys:
            assert 'dynamic_keys' in product
            assert len(product['dynamic_keys']) > 0


class TestDatabaseReset:
    """Test database reset functionality"""

    def test_clear_all_products(self, mock_product_db):
        """Test clearing all products from database"""
        # Add some test products
        test_products = [
            {
                'category': 'PV Module',
                'model_name': 'Test PV 1',
                'brand': 'Brand1',
                'price_euro': 180.0
            },
            {
                'category': 'Wechselrichter',
                'model_name': 'Test Inverter 1',
                'brand': 'Brand2',
                'price_euro': 800.0
            },
            {
                'category': 'Batteriespeicher',
                'model_name': 'Test Battery 1',
                'brand': 'Brand3',
                'price_euro': 3500.0
            }
        ]

        for product_data in test_products:
            mock_product_db.add_product(product_data)

        # Verify products were added
        products_before = mock_product_db.list_products()
        assert len(products_before) == 3

        # Clear all products
        result = mock_product_db.clear_all_products()
        assert result is True

        # Verify all products were deleted
        products_after = mock_product_db.list_products()
        assert len(products_after) == 0

    def test_clear_all_products_empty_database(self, mock_product_db):
        """Test clearing products from empty database"""
        # Ensure database is empty
        products_before = mock_product_db.list_products()
        assert len(products_before) == 0

        # Clear all products (should not fail)
        result = mock_product_db.clear_all_products()
        assert result is True

        # Verify database is still empty
        products_after = mock_product_db.list_products()
        assert len(products_after) == 0


class TestProductFieldValidation:
    """Test validation of new product fields"""

    def test_boolean_field_conversion(self, mock_product_db):
        """Test that boolean fields are properly converted to integers"""
        product_data = {
            'category': 'Wechselrichter',
            'model_name': 'Test Inverter Boolean',
            'brand': 'TestBrand',
            'price_euro': 800.0,
            'outdoor_opt': 1,
            'self_supply_feature': 0,
            'shadow_fading': 1,
            'smart_home': 0
        }

        product_id = mock_product_db.add_product(product_data)
        added_product = mock_product_db.get_product_by_id(product_id)

        # Check that boolean values are stored as integers
        assert added_product['outdoor_opt'] == 1
        assert added_product['self_supply_feature'] == 0
        assert added_product['shadow_fading'] == 1
        assert added_product['smart_home'] == 0

    def test_optional_fields_handling(self, mock_product_db):
        """Test that optional fields can be None or empty"""
        minimal_product = {
            'category': 'PV Module',
            'model_name': 'Minimal PV Module',
            'price_euro': 150.0
        }

        product_id = mock_product_db.add_product(minimal_product)
        added_product = mock_product_db.get_product_by_id(product_id)

        # Check that optional fields are handled properly
        assert added_product['technology'] is None or added_product['technology'] == ''
        assert added_product['feature'] is None or added_product['feature'] == ''
        assert added_product['design'] is None or added_product['design'] == ''
        assert added_product['upgrade'] is None or added_product['upgrade'] == ''


class TestCategorySpecificFields:
    """Test category-specific field handling"""

    def test_pv_module_specific_fields(self, mock_product_db):
        """Test PV module specific fields are properly handled"""
        pv_data = {
            'category': 'PV Module',
            'model_name': 'PV Test Module',
            'capacity_w': 400.0,
            'efficiency_percent': 21.5,
            'length_m': 2.0,
            'width_m': 1.0,
            'shadow_fading': 1
        }

        product_id = mock_product_db.add_product(pv_data)
        product = mock_product_db.get_product_by_id(product_id)

        assert product['capacity_w'] == 400.0
        assert product['efficiency_percent'] == 21.5
        assert product['length_m'] == 2.0
        assert product['width_m'] == 1.0
        assert product['shadow_fading'] == 1

    def test_inverter_specific_fields(self, mock_product_db):
        """Test inverter specific fields are properly handled"""
        inverter_data = {
            'category': 'Wechselrichter',
            'model_name': 'Inverter Test',
            'power_kw': 10.0,
            'outdoor_opt': 1,
            'self_supply_feature': 1,
            'smart_home': 0
        }

        product_id = mock_product_db.add_product(inverter_data)
        product = mock_product_db.get_product_by_id(product_id)

        assert product['power_kw'] == 10.0
        assert product['outdoor_opt'] == 1
        assert product['self_supply_feature'] == 1
        assert product['smart_home'] == 0

    def test_battery_specific_fields(self, mock_product_db):
        """Test battery specific fields are properly handled"""
        battery_data = {
            'category': 'Batteriespeicher',
            'model_name': 'Battery Test',
            'storage_power_kw': 5.0,
            'max_kwh_capacity': 10.0,
            'max_cycles': 6000,
            'upgrade': 'Modular'
        }

        product_id = mock_product_db.add_product(battery_data)
        product = mock_product_db.get_product_by_id(product_id)

        assert product['storage_power_kw'] == 5.0
        assert product['max_kwh_capacity'] == 10.0
        assert product['max_cycles'] == 6000
        assert product['upgrade'] == 'Modular'


if __name__ == "__main__":
    pytest.main([__file__])
