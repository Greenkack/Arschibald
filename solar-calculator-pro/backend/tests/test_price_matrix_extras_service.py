"""
Tests for Price Matrix Extras Service

Comprehensive tests for extras, services, bundles, and pricing rules.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from ..services.price_matrix_extras_service import (
    PriceMatrixExtrasService,
    PricingRuleType,
    CalculationBasis
)


@pytest.fixture
def mock_db():
    """Create a mock database connection"""
    db = Mock()
    cursor = Mock()
    db.cursor.return_value = cursor
    return db, cursor


@pytest.fixture
def service(mock_db):
    """Create service instance with mock database"""
    db, _ = mock_db
    return PriceMatrixExtrasService(db)


@pytest.fixture
def sample_project_details():
    """Sample project details for testing"""
    return {
        'anlage_kwp': 10.0,
        'pv_kwp': 10.0,
        'roof_area_m2': 70.0,
        'module_quantity': 25,
        'module_power_w': 400,
        'selected_module_name': 'TSM-400W',
        'selected_inverter_name': 'Fronius Symo 10.0',
        'selected_storage_name': 'BYD Battery-Box Premium HVS 10.2'
    }


class TestSpecialProductsCalculation:
    """Tests for special products calculation"""
    
    def test_calculate_special_products_empty_list(self, service, sample_project_details):
        """Test with no special products"""
        result = service.calculate_special_products(sample_project_details, [])
        
        assert result['total'] == Decimal('0.00')
        assert result['count'] == 0
        assert len(result['items']) == 0
        assert result['formatted_total'] == '0,00 €'
    
    def test_calculate_special_products_with_items(self, service, sample_project_details, mock_db):
        """Test with special products"""
        _, cursor = mock_db
        
        # Mock database responses
        cursor.fetchone.side_effect = [
            (1,),  # First product is special
            (0,),  # Second product is not special
            (1,)   # Third product is special
        ]
        
        products = [
            {'id': 1, 'name': 'Special Module', 'price': 500.0, 'quantity': 2},
            {'id': 2, 'name': 'Normal Module', 'price': 300.0, 'quantity': 1},
            {'id': 3, 'name': 'Special Optimizer', 'price': 150.0, 'quantity': 5}
        ]
        
        result = service.calculate_special_products(sample_project_details, products)
        
        assert result['count'] == 2  # Only special products counted
        assert result['total'] == Decimal('1750.00')  # 500*2 + 150*5
        assert len(result['items']) == 2
    
    def test_calculate_special_products_by_name(self, service, sample_project_details, mock_db):
        """Test special product identification by name"""
        _, cursor = mock_db
        
        # Mock database response for name lookup
        cursor.fetchone.return_value = (1,)
        
        products = [
            {'model_name': 'Special-Module-X', 'price': 600.0, 'quantity': 1}
        ]
        
        result = service.calculate_special_products(sample_project_details, products)
        
        assert result['count'] == 1
        assert result['total'] == Decimal('600.00')


class TestServicesCalculation:
    """Tests for services calculation"""
    
    def test_calculate_services_standard_only(self, service, sample_project_details, mock_db):
        """Test calculation with only standard services"""
        _, cursor = mock_db
        
        # Mock database response
        cursor.fetchall.return_value = [
            (1, 'Installation', 'Standard installation', 'Installation', 100.0, 'kWp', 1, 1),
            (2, 'Commissioning', 'System commissioning', 'Service', 200.0, 'Pauschal', 1, 2)
        ]
        
        result = service.calculate_services(sample_project_details, [], include_standard=True)
        
        assert len(result['standard_services']) == 2
        assert len(result['optional_services']) == 0
        assert result['total_standard'] == Decimal('1200.00')  # 100*10 + 200*1
        assert result['total_optional'] == Decimal('0.00')
        assert result['total_services'] == Decimal('1200.00')
    
    def test_calculate_services_with_optional(self, service, sample_project_details, mock_db):
        """Test calculation with optional services"""
        _, cursor = mock_db
        
        # Mock database response
        cursor.fetchall.return_value = [
            (1, 'Installation', 'Standard installation', 'Installation', 100.0, 'kWp', 1, 1),
            (2, 'Monitoring', 'System monitoring', 'Service', 50.0, 'Pauschal', 0, 3),
            (3, 'Maintenance', 'Annual maintenance', 'Service', 150.0, 'Pauschal', 0, 4)
        ]
        
        result = service.calculate_services(
            sample_project_details,
            [2, 3],  # Select optional services
            include_standard=True
        )
        
        assert len(result['standard_services']) == 1
        assert len(result['optional_services']) == 2
        assert result['total_standard'] == Decimal('1000.00')  # 100*10
        assert result['total_optional'] == Decimal('200.00')  # 50 + 150
        assert result['total_services'] == Decimal('1200.00')
    
    def test_calculate_quantity_per_kwp(self, service, sample_project_details):
        """Test quantity calculation per kWp"""
        quantity = service._calculate_quantity('kWp', sample_project_details)
        assert quantity == 10.0
    
    def test_calculate_quantity_per_sqm(self, service, sample_project_details):
        """Test quantity calculation per m²"""
        quantity = service._calculate_quantity('m²', sample_project_details)
        assert quantity == 70.0
    
    def test_calculate_quantity_per_hour(self, service, sample_project_details):
        """Test quantity calculation per hour"""
        quantity = service._calculate_quantity('Stunde', sample_project_details)
        assert quantity == 20.0  # max(8, 10*2)
    
    def test_calculate_quantity_flat_rate(self, service, sample_project_details):
        """Test quantity calculation for flat rate"""
        quantity = service._calculate_quantity('Pauschal', sample_project_details)
        assert quantity == 1.0


class TestBundlePricing:
    """Tests for bundle pricing"""
    
    def test_bundle_pricing_no_rules(self, service):
        """Test bundle pricing with no rules"""
        items = [
            {'total_price': 1000.0},
            {'total_price': 500.0}
        ]
        
        result = service.calculate_bundle_pricing(items, [])
        
        assert result['original_total'] == Decimal('1500.00')
        assert result['discount_amount'] == Decimal('0.00')
        assert result['final_total'] == Decimal('1500.00')
    
    def test_bundle_pricing_percentage_discount(self, service):
        """Test bundle pricing with percentage discount"""
        items = [
            {'id': 1, 'total_price': 1000.0, 'category': 'Module'},
            {'id': 2, 'total_price': 500.0, 'category': 'Inverter'}
        ]
        
        rules = [
            {
                'name': '10% Bundle Discount',
                'type': 'percentage',
                'value': 10.0,
                'min_items': 2,
                'min_total': 0,
                'required_items': [],
                'required_categories': []
            }
        ]
        
        result = service.calculate_bundle_pricing(items, rules)
        
        assert result['original_total'] == Decimal('1500.00')
        assert result['discount_amount'] == Decimal('150.00')
        assert result['final_total'] == Decimal('1350.00')
        assert result['discount_percentage'] == Decimal('10.00')
    
    def test_bundle_pricing_fixed_discount(self, service):
        """Test bundle pricing with fixed discount"""
        items = [
            {'id': 1, 'total_price': 1000.0},
            {'id': 2, 'total_price': 500.0}
        ]
        
        rules = [
            {
                'name': '200€ Bundle Discount',
                'type': 'fixed',
                'value': 200.0,
                'min_items': 2,
                'min_total': 0,
                'required_items': [],
                'required_categories': []
            }
        ]
        
        result = service.calculate_bundle_pricing(items, rules)
        
        assert result['discount_amount'] == Decimal('200.00')
        assert result['final_total'] == Decimal('1300.00')
    
    def test_bundle_rule_min_items_not_met(self, service):
        """Test bundle rule not applied when min items not met"""
        items = [
            {'id': 1, 'total_price': 1000.0}
        ]
        
        rules = [
            {
                'name': 'Bundle Discount',
                'type': 'percentage',
                'value': 10.0,
                'min_items': 2,
                'min_total': 0,
                'required_items': [],
                'required_categories': []
            }
        ]
        
        result = service.calculate_bundle_pricing(items, rules)
        
        assert result['discount_amount'] == Decimal('0.00')
        assert len(result['applied_rules']) == 0


class TestConditionalPricing:
    """Tests for conditional pricing"""
    
    def test_conditional_pricing_no_rules(self, service):
        """Test conditional pricing with no rules"""
        result = service.apply_conditional_pricing(
            Decimal('1000.00'),
            {'system_size': 10.0},
            []
        )
        
        assert result['base_price'] == Decimal('1000.00')
        assert result['total_adjustment'] == Decimal('0.00')
        assert result['final_price'] == Decimal('1000.00')
    
    def test_conditional_pricing_percentage_adjustment(self, service):
        """Test conditional pricing with percentage adjustment"""
        rules = [
            {
                'name': 'Large System Discount',
                'condition': {
                    'type': 'size_based',
                    'field': 'system_size',
                    'operator': 'greater_than',
                    'value': 5.0
                },
                'adjustment_type': 'percentage',
                'adjustment_value': -5.0  # 5% discount
            }
        ]
        
        result = service.apply_conditional_pricing(
            Decimal('1000.00'),
            {'system_size': 10.0},
            rules
        )
        
        assert result['total_adjustment'] == Decimal('-50.00')
        assert result['final_price'] == Decimal('950.00')
    
    def test_conditional_pricing_fixed_adjustment(self, service):
        """Test conditional pricing with fixed adjustment"""
        rules = [
            {
                'name': 'Premium Customer Discount',
                'condition': {
                    'type': 'customer_type',
                    'field': 'customer_type',
                    'operator': 'equals',
                    'value': 'premium'
                },
                'adjustment_type': 'fixed',
                'adjustment_value': -100.0
            }
        ]
        
        result = service.apply_conditional_pricing(
            Decimal('1000.00'),
            {'customer_type': 'premium'},
            rules
        )
        
        assert result['total_adjustment'] == Decimal('-100.00')
        assert result['final_price'] == Decimal('900.00')
    
    def test_conditional_pricing_condition_not_met(self, service):
        """Test conditional pricing when condition is not met"""
        rules = [
            {
                'name': 'Large System Discount',
                'condition': {
                    'type': 'size_based',
                    'field': 'system_size',
                    'operator': 'greater_than',
                    'value': 15.0
                },
                'adjustment_type': 'percentage',
                'adjustment_value': -5.0
            }
        ]
        
        result = service.apply_conditional_pricing(
            Decimal('1000.00'),
            {'system_size': 10.0},
            rules
        )
        
        assert result['total_adjustment'] == Decimal('0.00')
        assert result['final_price'] == Decimal('1000.00')


class TestCustomPricingRules:
    """Tests for custom pricing rules"""
    
    def test_custom_discount_fixed(self, service):
        """Test custom fixed discount"""
        pricing_data = {'total': 1000.0}
        rules = [
            {
                'name': 'Special Discount',
                'type': 'discount',
                'value': 100.0,
                'value_type': 'fixed',
                'enabled': True
            }
        ]
        
        result = service.apply_custom_pricing_rules(pricing_data, rules)
        
        assert result['total'] == Decimal('900.00')
        assert result['discount_applied'] == Decimal('100.00')
    
    def test_custom_discount_percentage(self, service):
        """Test custom percentage discount"""
        pricing_data = {'total': 1000.0}
        rules = [
            {
                'name': 'Percentage Discount',
                'type': 'discount',
                'value': 10.0,
                'value_type': 'percentage',
                'enabled': True
            }
        ]
        
        result = service.apply_custom_pricing_rules(pricing_data, rules)
        
        assert result['total'] == Decimal('900.00')
        assert result['discount_applied'] == Decimal('100.00')
    
    def test_custom_surcharge_fixed(self, service):
        """Test custom fixed surcharge"""
        pricing_data = {'total': 1000.0}
        rules = [
            {
                'name': 'Express Surcharge',
                'type': 'surcharge',
                'value': 50.0,
                'value_type': 'fixed',
                'enabled': True
            }
        ]
        
        result = service.apply_custom_pricing_rules(pricing_data, rules)
        
        assert result['total'] == Decimal('1050.00')
        assert result['surcharge_applied'] == Decimal('50.00')
    
    def test_custom_rule_disabled(self, service):
        """Test that disabled rules are not applied"""
        pricing_data = {'total': 1000.0}
        rules = [
            {
                'name': 'Disabled Discount',
                'type': 'discount',
                'value': 100.0,
                'value_type': 'fixed',
                'enabled': False
            }
        ]
        
        result = service.apply_custom_pricing_rules(pricing_data, rules)
        
        assert result['total'] == 1000.0
        assert 'discount_applied' not in result


class TestCurrencyFormatting:
    """Tests for German currency formatting"""
    
    def test_format_small_amount(self, service):
        """Test formatting small amounts"""
        formatted = service._format_currency(Decimal('99.99'))
        assert formatted == '99,99 €'
    
    def test_format_thousands(self, service):
        """Test formatting with thousands separator"""
        formatted = service._format_currency(Decimal('1234.56'))
        assert formatted == '1.234,56 €'
    
    def test_format_millions(self, service):
        """Test formatting large amounts"""
        formatted = service._format_currency(Decimal('1234567.89'))
        assert formatted == '1.234.567,89 €'
    
    def test_format_zero(self, service):
        """Test formatting zero"""
        formatted = service._format_currency(Decimal('0.00'))
        assert formatted == '0,00 €'
    
    def test_format_negative(self, service):
        """Test formatting negative amounts"""
        formatted = service._format_currency(Decimal('-500.00'))
        assert formatted == '-500,00 €'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
