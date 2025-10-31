"""Unit tests for ProfitMarginManager

Tests margin calculations across all calculate_per scenarios and priority resolution.
"""

from pricing.profit_margin_manager import (
    MarginBreakdown,
    MarginConfig,
    ProfitMarginManager,
)
import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMarginConfig(unittest.TestCase):
    """Test MarginConfig data class"""

    def test_valid_percentage_margin(self):
        """Test creating valid percentage margin"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='product'
        )
        self.assertEqual(config.margin_type, 'percentage')
        self.assertEqual(config.margin_value, 25.0)
        self.assertEqual(config.applies_to, 'product')

    def test_valid_fixed_margin(self):
        """Test creating valid fixed margin"""
        config = MarginConfig(
            margin_type='fixed',
            margin_value=100.0,
            applies_to='category'
        )
        self.assertEqual(config.margin_type, 'fixed')
        self.assertEqual(config.margin_value, 100.0)
        self.assertEqual(config.applies_to, 'category')

    def test_invalid_margin_type(self):
        """Test invalid margin type raises error"""
        with self.assertRaises(ValueError):
            MarginConfig(
                margin_type='invalid',
                margin_value=25.0,
                applies_to='product'
            )

    def test_invalid_applies_to(self):
        """Test invalid applies_to raises error"""
        with self.assertRaises(ValueError):
            MarginConfig(
                margin_type='percentage',
                margin_value=25.0,
                applies_to='invalid'
            )

    def test_negative_fixed_margin(self):
        """Test negative fixed margin raises error"""
        with self.assertRaises(ValueError):
            MarginConfig(
                margin_type='fixed',
                margin_value=-50.0,
                applies_to='product'
            )


class TestMarginBreakdown(unittest.TestCase):
    """Test MarginBreakdown calculations"""

    def test_per_piece_calculation(self):
        """Test per piece calculation"""
        breakdown = MarginBreakdown(
            purchase_price=100.0,
            margin_amount=25.0,
            selling_price=125.0,
            margin_percentage=25.0,
            source='product',
            calculate_per_method='Stück',
            quantity=5.0
        )

        self.assertEqual(breakdown.total_purchase_cost, 500.0)  # 100 * 5
        self.assertEqual(breakdown.total_selling_price, 625.0)  # 125 * 5
        self.assertEqual(breakdown.total_margin_amount, 125.0)  # 625 - 500

    def test_per_meter_calculation(self):
        """Test per meter calculation"""
        breakdown = MarginBreakdown(
            purchase_price=50.0,
            margin_amount=15.0,
            selling_price=65.0,
            margin_percentage=30.0,
            source='category',
            calculate_per_method='Meter',
            quantity=10.0
        )

        self.assertEqual(breakdown.total_purchase_cost, 500.0)  # 50 * 10
        self.assertEqual(breakdown.total_selling_price, 650.0)  # 65 * 10
        self.assertEqual(breakdown.total_margin_amount, 150.0)  # 650 - 500

    def test_lump_sum_calculation(self):
        """Test lump sum calculation"""
        breakdown = MarginBreakdown(
            purchase_price=1000.0,
            margin_amount=300.0,
            selling_price=1300.0,
            margin_percentage=30.0,
            source='global',
            calculate_per_method='pauschal',
            quantity=3.0  # Should be ignored for lump sum
        )

        self.assertEqual(
            breakdown.total_purchase_cost,
            1000.0)  # Ignore quantity
        self.assertEqual(
            breakdown.total_selling_price,
            1300.0)  # Ignore quantity
        self.assertEqual(breakdown.total_margin_amount, 300.0)   # 1300 - 1000

    def test_per_kwp_calculation(self):
        """Test per kWp calculation"""
        breakdown = MarginBreakdown(
            purchase_price=200.0,
            margin_amount=50.0,
            selling_price=250.0,
            margin_percentage=25.0,
            source='product',
            calculate_per_method='kWp',
            quantity=8.5  # 8.5 kWp system
        )

        self.assertEqual(breakdown.total_purchase_cost, 1700.0)  # 200 * 8.5
        self.assertEqual(breakdown.total_selling_price, 2125.0)  # 250 * 8.5
        self.assertEqual(breakdown.total_margin_amount, 425.0)   # 2125 - 1700


class TestProfitMarginManager(unittest.TestCase):
    """Test ProfitMarginManager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ProfitMarginManager()

        # Mock database functions
        self.mock_get_product = Mock()
        self.mock_update_pricing = Mock()
        self.mock_list_products = Mock()
        self.mock_load_admin_setting = Mock()
        self.mock_save_admin_setting = Mock()

        # Patch database functions
        self.patcher_get_product = patch(
            'pricing.profit_margin_manager.get_product_by_id',
            self.mock_get_product)
        self.patcher_update_pricing = patch(
            'pricing.profit_margin_manager.update_product_pricing_fields',
            self.mock_update_pricing)
        self.patcher_list_products = patch(
            'pricing.profit_margin_manager.list_products',
            self.mock_list_products)
        self.patcher_load_admin_setting = patch(
            'pricing.profit_margin_manager.load_admin_setting',
            self.mock_load_admin_setting)
        self.patcher_save_admin_setting = patch(
            'pricing.profit_margin_manager.save_admin_setting',
            self.mock_save_admin_setting)

        self.patcher_get_product.start()
        self.patcher_update_pricing.start()
        self.patcher_list_products.start()
        self.patcher_load_admin_setting.start()
        self.patcher_save_admin_setting.start()

        # Set up default mock returns
        self.mock_load_admin_setting.return_value = {}
        self.mock_save_admin_setting.return_value = True
        self.mock_list_products.return_value = []

    def tearDown(self):
        """Clean up patches"""
        self.patcher_get_product.stop()
        self.patcher_update_pricing.stop()
        self.patcher_list_products.stop()
        self.patcher_load_admin_setting.stop()
        self.patcher_save_admin_setting.stop()

    def test_set_product_margin_success(self):
        """Test successful product margin setting"""
        # Mock product exists
        self.mock_get_product.return_value = {
            'id': 1, 'model_name': 'Test Module'}
        self.mock_update_pricing.return_value = True

        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='product'
        )

        result = self.manager.set_product_margin(1, config)

        self.assertTrue(result)
        self.mock_get_product.assert_called_once_with(1)
        self.mock_update_pricing.assert_called_once()

    def test_set_product_margin_product_not_found(self):
        """Test product margin setting when product doesn't exist"""
        # Mock product not found
        self.mock_get_product.return_value = None

        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='product'
        )

        result = self.manager.set_product_margin(999, config)

        self.assertFalse(result)
        self.mock_update_pricing.assert_not_called()

    def test_set_global_margin(self):
        """Test setting global margin"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='global'
        )

        result = self.manager.set_global_margin(config)

        self.assertTrue(result)
        self.assertIn('default', self.manager._global_margins)

    def test_set_category_margin(self):
        """Test setting category-specific margin"""
        config = MarginConfig(
            margin_type='fixed',
            margin_value=150.0,
            applies_to='category'
        )

        result = self.manager.set_global_margin(config, category='Modul')

        self.assertTrue(result)
        self.assertIn('Modul', self.manager._category_margins)

    def test_calculate_selling_price_percentage_margin(self):
        """Test selling price calculation with percentage margin"""
        # Set up global margin
        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        selling_price = self.manager.calculate_selling_price(
            purchase_price=100.0,
            calculate_per='Stück'
        )

        self.assertEqual(selling_price, 125.0)  # 100 + (100 * 0.25)

    def test_calculate_selling_price_fixed_margin(self):
        """Test selling price calculation with fixed margin"""
        # Set up global margin
        config = MarginConfig(
            margin_type='fixed',
            margin_value=50.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        selling_price = self.manager.calculate_selling_price(
            purchase_price=200.0,
            calculate_per='Meter'
        )

        self.assertEqual(selling_price, 250.0)  # 200 + 50

    def test_margin_priority_resolution(self):
        """Test margin priority resolution (product > category > global)"""
        # Set up different margin levels
        global_config = MarginConfig(
            margin_type='percentage',
            margin_value=20.0,
            applies_to='global'
        )
        self.manager.set_global_margin(global_config)

        category_config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='category'
        )
        self.manager.set_global_margin(category_config, category='Modul')

        # Mock product with specific margin
        self.mock_get_product.return_value = {
            'id': 1,
            'model_name': 'Test Module',
            'category': 'Modul',
            'margin_type': 'percentage',
            'margin_value': 40.0,
            'margin_priority': 100
        }

        breakdown = self.manager.get_margin_breakdown(
            purchase_price=100.0,
            product_id=1,
            category='Modul'
        )

        # Should use product-specific margin (40%)
        self.assertEqual(breakdown.margin_percentage, 40.0)
        self.assertEqual(breakdown.selling_price, 140.0)
        self.assertEqual(breakdown.source, 'product')

    def test_calculate_per_stück_scenario(self):
        """Test calculate_per 'Stück' scenario"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        result = self.manager.calculate_total_price_with_margin(
            purchase_price=180.0,
            quantity=20,
            calculate_per='Stück'
        )

        self.assertEqual(result['unit_purchase_price'], 180.0)
        self.assertEqual(result['unit_selling_price'], 225.0)  # 180 * 1.25
        self.assertEqual(result['total_purchase_price'], 3600.0)  # 180 * 20
        self.assertEqual(result['total_selling_price'], 4500.0)  # 225 * 20
        self.assertEqual(result['total_margin_amount'], 900.0)  # 4500 - 3600

    def test_calculate_per_meter_scenario(self):
        """Test calculate_per 'Meter' scenario"""
        config = MarginConfig(
            margin_type='fixed',
            margin_value=5.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        result = self.manager.calculate_total_price_with_margin(
            purchase_price=12.0,
            quantity=50.0,  # 50 meters of cable
            calculate_per='Meter'
        )

        self.assertEqual(result['unit_purchase_price'], 12.0)
        self.assertEqual(result['unit_selling_price'], 17.0)  # 12 + 5
        self.assertEqual(result['total_purchase_price'], 600.0)  # 12 * 50
        self.assertEqual(result['total_selling_price'], 850.0)  # 17 * 50
        self.assertEqual(result['total_margin_amount'], 250.0)  # 850 - 600

    def test_calculate_per_pauschal_scenario(self):
        """Test calculate_per 'pauschal' (lump sum) scenario"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        result = self.manager.calculate_total_price_with_margin(
            purchase_price=2000.0,
            quantity=3,  # Should be ignored for lump sum
            calculate_per='pauschal'
        )

        self.assertEqual(result['unit_purchase_price'], 2000.0)
        self.assertEqual(result['unit_selling_price'], 2600.0)  # 2000 * 1.30
        self.assertEqual(
            result['total_purchase_price'],
            2000.0)  # Ignore quantity
        self.assertEqual(
            result['total_selling_price'],
            2600.0)  # Ignore quantity
        self.assertEqual(result['total_margin_amount'], 600.0)  # 2600 - 2000

    def test_calculate_per_kwp_scenario(self):
        """Test calculate_per 'kWp' scenario"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=20.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

        result = self.manager.calculate_total_price_with_margin(
            purchase_price=300.0,  # 300€ per kWp
            quantity=8.5,  # 8.5 kWp system
            calculate_per='kWp'
        )

        self.assertEqual(result['unit_purchase_price'], 300.0)
        self.assertEqual(result['unit_selling_price'], 360.0)  # 300 * 1.20
        self.assertEqual(result['total_purchase_price'], 2550.0)  # 300 * 8.5
        self.assertEqual(result['total_selling_price'], 3060.0)  # 360 * 8.5
        self.assertEqual(result['total_margin_amount'], 510.0)  # 3060 - 2550

    def test_no_margin_configured(self):
        """Test behavior when no margin is configured"""
        # Clear default margins
        self.manager._global_margins.clear()

        breakdown = self.manager.get_margin_breakdown(
            purchase_price=100.0
        )

        self.assertEqual(breakdown.purchase_price, 100.0)
        self.assertEqual(breakdown.selling_price, 100.0)
        self.assertEqual(breakdown.margin_amount, 0.0)
        self.assertEqual(breakdown.margin_percentage, 0.0)
        self.assertEqual(breakdown.source, 'none')

    def test_validate_margin_config_valid(self):
        """Test margin config validation with valid config"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='product'
        )

        result = self.manager.validate_margin_config(config)
        self.assertTrue(result)

    def test_validate_margin_config_negative_percentage(self):
        """Test margin config validation with negative percentage"""
        config = MarginConfig(
            margin_type='percentage',
            margin_value=-10.0,
            applies_to='product'
        )

        result = self.manager.validate_margin_config(config)
        self.assertFalse(result)

    def test_get_all_margins(self):
        """Test getting all configured margins"""
        # Set up some margins
        global_config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='global'
        )
        self.manager.set_global_margin(global_config)

        category_config = MarginConfig(
            margin_type='fixed',
            margin_value=100.0,
            applies_to='category'
        )
        self.manager.set_global_margin(category_config, category='Inverter')

        all_margins = self.manager.get_all_margins()

        self.assertIn('global_margins', all_margins)
        self.assertIn('category_margins', all_margins)
        self.assertIn('default', all_margins['global_margins'])
        self.assertIn('Inverter', all_margins['category_margins'])

    def test_set_category_margin(self):
        """Test setting category-specific margin"""
        # Mock products in category
        self.mock_list_products.return_value = [
            {'id': 1, 'category': 'Modul', 'model_name': 'Test Module 1'},
            {'id': 2, 'category': 'Modul', 'model_name': 'Test Module 2'}
        ]

        config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='category'
        )

        result = self.manager.set_category_margin('Modul', config)

        self.assertTrue(result)
        self.assertIn('Modul', self.manager._category_margins)
        self.assertEqual(
            self.manager._category_margins['Modul'].margin_value, 30.0)

    def test_remove_category_margin(self):
        """Test removing category margin"""
        # Set up a category margin first
        config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='category'
        )
        self.manager.set_category_margin('Modul', config)

        # Remove it
        result = self.manager.remove_category_margin('Modul')

        self.assertTrue(result)
        self.assertNotIn('Modul', self.manager._category_margins)

    def test_get_available_categories(self):
        """Test getting available product categories"""
        # Mock products with different categories
        self.mock_list_products.return_value = [
            {'id': 1, 'category': 'Modul'},
            {'id': 2, 'category': 'Inverter'},
            {'id': 3, 'category': 'Modul'},  # Duplicate category
            {'id': 4, 'category': 'Speicher'}
        ]

        categories = self.manager.get_available_categories()

        expected_categories = ['Inverter', 'Modul',
                               'Speicher']  # Sorted, no duplicates
        self.assertEqual(categories, expected_categories)

    def test_apply_margin_to_category_products(self):
        """Test applying margin to all products in a category"""
        # Mock products in category
        self.mock_list_products.return_value = [
            {'id': 1, 'category': 'Modul', 'model_name': 'Test Module 1'},
            {'id': 2, 'category': 'Modul', 'model_name': 'Test Module 2'}
        ]

        # Mock successful product updates
        self.mock_get_product.return_value = {
            'id': 1, 'model_name': 'Test Module'}
        self.mock_update_pricing.return_value = True

        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='product'
        )

        result = self.manager.apply_margin_to_category_products(
            'Modul', config)

        self.assertTrue(result['success'])
        self.assertEqual(result['updated_count'], 2)
        self.assertEqual(result['failed_count'], 0)
        self.assertEqual(len(result['products']), 2)

    def test_get_margin_priority_info(self):
        """Test margin priority information"""
        # Set up different margin levels
        global_config = MarginConfig(
            margin_type='percentage',
            margin_value=20.0,
            applies_to='global'
        )
        self.manager.set_global_margin(global_config)

        category_config = MarginConfig(
            margin_type='percentage',
            margin_value=30.0,
            applies_to='category'
        )
        self.manager.set_category_margin('Modul', category_config)

        # Mock product with specific margin
        self.mock_get_product.return_value = {
            'id': 1,
            'model_name': 'Test Module',
            'category': 'Modul',
            'margin_type': 'percentage',
            'margin_value': 40.0,
            'margin_priority': 100
        }

        priority_info = self.manager.get_margin_priority_info(
            product_id=1,
            category='Modul'
        )

        # Should have all margin levels
        self.assertIsNotNone(priority_info['product_margin'])
        self.assertIsNotNone(priority_info['category_margin'])
        self.assertIsNotNone(priority_info['global_default_margin'])

        # Should select product margin (highest priority)
        self.assertEqual(
            priority_info['selected_margin']['margin_value'], 40.0)
        self.assertEqual(priority_info['selected_margin']['source'], 'product')
        self.assertIn('Product-specific', priority_info['selection_reason'])

    def test_admin_settings_persistence(self):
        """Test that margins are persisted to admin settings"""
        # Test global margin persistence
        global_config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='global'
        )

        result = self.manager.set_global_margin(global_config)

        self.assertTrue(result)
        # Should have called save_admin_setting for global margins
        self.mock_save_admin_setting.assert_called()

        # Test category margin persistence
        category_config = MarginConfig(
            margin_type='fixed',
            margin_value=100.0,
            applies_to='category'
        )

        result = self.manager.set_category_margin('Modul', category_config)

        self.assertTrue(result)
        # Should have called save_admin_setting for category margins
        self.assertEqual(
            self.mock_save_admin_setting.call_count,
            2)  # Global + Category

    def test_load_margins_from_admin_settings(self):
        """Test loading margins from admin settings"""
        # Mock admin settings data
        global_margins_data = {
            'default': {
                'margin_type': 'percentage',
                'margin_value': 25.0,
                'priority': 0,
                'calculate_per_method': None,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
        }

        category_margins_data = {
            'Modul': {
                'margin_type': 'percentage',
                'margin_value': 30.0,
                'priority': 50,
                'calculate_per_method': None,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
        }

        def mock_load_setting(key, default=None):
            if key == 'profit_margins_global':
                return global_margins_data
            if key == 'profit_margins_category':
                return category_margins_data
            return default

        self.mock_load_admin_setting.side_effect = mock_load_setting

        # Create new manager to trigger loading
        new_manager = ProfitMarginManager()

        # Should have loaded the margins
        self.assertIn('default', new_manager._global_margins)
        self.assertIn('Modul', new_manager._category_margins)
        self.assertEqual(
            new_manager._global_margins['default'].margin_value, 25.0)
        self.assertEqual(
            new_manager._category_margins['Modul'].margin_value, 30.0)


class TestCalculatePerIntegration(unittest.TestCase):
    """Integration tests for calculate_per with different product types"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ProfitMarginManager()

        # Set up a standard margin
        config = MarginConfig(
            margin_type='percentage',
            margin_value=25.0,
            applies_to='global'
        )
        self.manager.set_global_margin(config)

    def test_pv_module_per_piece(self):
        """Test PV module pricing per piece"""
        result = self.manager.calculate_total_price_with_margin(
            purchase_price=180.0,
            quantity=24,  # 24 modules
            calculate_per='Stück',
            category='Modul'
        )

        expected_unit_selling = 180.0 * 1.25  # 225.0
        expected_total_selling = expected_unit_selling * 24  # 5400.0

        self.assertEqual(result['unit_selling_price'], expected_unit_selling)
        self.assertEqual(result['total_selling_price'], expected_total_selling)
        self.assertEqual(result['calculate_per'], 'Stück')

    def test_cable_per_meter(self):
        """Test cable pricing per meter"""
        result = self.manager.calculate_total_price_with_margin(
            purchase_price=8.50,
            quantity=75.0,  # 75 meters
            calculate_per='Meter',
            category='Kabel'
        )

        expected_unit_selling = 8.50 * 1.25  # 10.625
        expected_total_selling = expected_unit_selling * 75.0  # 796.875

        self.assertEqual(result['unit_selling_price'], expected_unit_selling)
        self.assertEqual(result['total_selling_price'], expected_total_selling)
        self.assertEqual(result['calculate_per'], 'Meter')

    def test_installation_lump_sum(self):
        """Test installation service lump sum pricing"""
        result = self.manager.calculate_total_price_with_margin(
            purchase_price=3500.0,
            quantity=1,  # Quantity ignored for lump sum
            calculate_per='pauschal',
            category='Installation'
        )

        # The manager has a method-specific margin for 'pauschal' (30%)
        expected_selling = 3500.0 * 1.30  # 4550.0

        self.assertEqual(result['unit_selling_price'], expected_selling)
        self.assertEqual(
            result['total_selling_price'],
            expected_selling)  # Same as unit for lump sum
        self.assertEqual(result['calculate_per'], 'pauschal')

    def test_system_per_kwp(self):
        """Test system component pricing per kWp"""
        result = self.manager.calculate_total_price_with_margin(
            purchase_price=250.0,  # 250€ per kWp
            quantity=9.6,  # 9.6 kWp system
            calculate_per='kWp',
            category='System'
        )

        expected_unit_selling = 250.0 * 1.25  # 312.5
        expected_total_selling = expected_unit_selling * 9.6  # 3000.0

        self.assertEqual(result['unit_selling_price'], expected_unit_selling)
        self.assertEqual(result['total_selling_price'], expected_total_selling)
        self.assertEqual(result['calculate_per'], 'kWp')


if __name__ == '__main__':
    unittest.main()
