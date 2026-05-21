"""
Tests for PricingAdvancedService

Requirements: 1.3, 4.5, 6.1
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.pricing_advanced_service import (
    PricingAdvancedService,
    PricingRuleType,
    DiscountType
)


@pytest.fixture
def service():
    """Create service instance for testing"""
    return PricingAdvancedService()


class TestHealthCheck:
    """Test health check functionality"""
    
    def test_health_check(self, service):
        """Test service health check"""
        result = service.health_check()
        
        assert result['service'] == 'PricingAdvancedService'
        assert result['status'] == 'healthy'
        assert 'timestamp' in result


class TestDynamicPricingRules:
    """Test dynamic pricing rules engine"""
    
    def test_create_pricing_rule(self, service):
        """Test creating a pricing rule"""
        result = service.create_pricing_rule(
            name="Test Rule",
            rule_type=PricingRuleType.VOLUME_DISCOUNT.value,
            conditions={'quantity': {'min': 10}},
            actions={'discount_percentage': 10},
            priority=1
        )
        
        assert result['success'] is True
        assert 'rule_id' in result
    
    def test_apply_pricing_rules_with_discount(self, service):
        """Test applying pricing rules with discount"""
        # Create rule
        service.create_pricing_rule(
            name="Volume Discount",
            rule_type=PricingRuleType.VOLUME_DISCOUNT.value,
            conditions={'quantity': {'min': 10}},
            actions={'discount_percentage': 10},
            priority=1
        )
        
        # Apply rules
        result = service.apply_pricing_rules(
            base_price=1000.0,
            context={'quantity': 15}
        )
        
        assert result['success'] is True
        assert result['base_price'] == 1000.0
        assert result['final_price'] == 900.0  # 10% discount
        assert len(result['applied_rules']) == 1
    
    def test_apply_pricing_rules_no_match(self, service):
        """Test applying rules when conditions don't match"""
        # Create rule
        service.create_pricing_rule(
            name="Volume Discount",
            rule_type=PricingRuleType.VOLUME_DISCOUNT.value,
            conditions={'quantity': {'min': 10}},
            actions={'discount_percentage': 10},
            priority=1
        )
        
        # Apply rules with quantity below threshold
        result = service.apply_pricing_rules(
            base_price=1000.0,
            context={'quantity': 5}
        )
        
        assert result['success'] is True
        assert result['final_price'] == 1000.0  # No discount
        assert len(result['applied_rules']) == 0


class TestVolumeDiscounts:
    """Test volume discount calculations"""
    
    def test_volume_discount_single_tier(self, service):
        """Test volume discount with single tier"""
        discount_tiers = [
            {'min_quantity': 10, 'discount_percentage': 10}
        ]
        
        result = service.calculate_volume_discount(
            quantity=15,
            unit_price=100.0,
            discount_tiers=discount_tiers
        )
        
        assert result['success'] is True
        assert result['base_total'] == 1500.0
        assert result['discount_percentage'] == 10.0
        assert result['discount_amount'] == 150.0
        assert result['final_total'] == 1350.0
    
    def test_volume_discount_multiple_tiers(self, service):
        """Test volume discount with multiple tiers"""
        discount_tiers = [
            {'min_quantity': 10, 'discount_percentage': 5},
            {'min_quantity': 50, 'discount_percentage': 10},
            {'min_quantity': 100, 'discount_percentage': 15}
        ]
        
        # Test tier 2
        result = service.calculate_volume_discount(
            quantity=75,
            unit_price=100.0,
            discount_tiers=discount_tiers
        )
        
        assert result['success'] is True
        assert result['discount_percentage'] == 10.0
        assert result['final_total'] == 6750.0  # 7500 - 10%
    
    def test_volume_discount_no_tier_match(self, service):
        """Test volume discount when no tier matches"""
        discount_tiers = [
            {'min_quantity': 10, 'discount_percentage': 10}
        ]
        
        result = service.calculate_volume_discount(
            quantity=5,
            unit_price=100.0,
            discount_tiers=discount_tiers
        )
        
        assert result['success'] is True
        assert result['discount_percentage'] == 0
        assert result['final_total'] == 500.0


class TestTimeBasedPricing:
    """Test time-based pricing"""
    
    def test_weekend_pricing(self, service):
        """Test weekend pricing multiplier"""
        pricing_schedule = {
            'weekday_multiplier': 1.0,
            'weekend_multiplier': 1.1
        }
        
        # Saturday
        saturday = datetime(2024, 1, 6, 10, 0)  # Saturday
        
        result = service.calculate_time_based_price(
            base_price=1000.0,
            pricing_schedule=pricing_schedule,
            target_date=saturday
        )
        
        assert result['success'] is True
        assert result['final_price'] == 1100.0
        assert any(adj['type'] == 'weekend' for adj in result['adjustments'])
    
    def test_peak_hours_pricing(self, service):
        """Test peak hours pricing"""
        pricing_schedule = {
            'peak_hours': {'start': 9, 'end': 17, 'multiplier': 1.2}
        }
        
        # During peak hours
        peak_time = datetime(2024, 1, 8, 12, 0)  # Monday noon
        
        result = service.calculate_time_based_price(
            base_price=1000.0,
            pricing_schedule=pricing_schedule,
            target_date=peak_time
        )
        
        assert result['success'] is True
        assert result['final_price'] == 1200.0
    
    def test_seasonal_pricing(self, service):
        """Test seasonal pricing"""
        pricing_schedule = {
            'seasonal': {
                'summer': {'months': [6, 7, 8], 'multiplier': 1.15}
            }
        }
        
        # Summer month
        summer_date = datetime(2024, 7, 15, 10, 0)
        
        result = service.calculate_time_based_price(
            base_price=1000.0,
            pricing_schedule=pricing_schedule,
            target_date=summer_date
        )
        
        assert result['success'] is True
        assert result['final_price'] == 1150.0


class TestCustomerSpecificPricing:
    """Test customer-specific pricing"""
    
    def test_customer_price_with_custom_rule(self, service):
        """Test customer-specific pricing with custom rule"""
        # Create customer-specific rule
        service.create_pricing_rule(
            name="VIP Customer Discount",
            rule_type=PricingRuleType.CUSTOMER_SPECIFIC.value,
            conditions={'customer_id': 'CUST001'},
            actions={'discount_percentage': 15},
            priority=10
        )
        
        result = service.get_customer_price(
            customer_id='CUST001',
            product_id='PROD001',
            base_price=1000.0,
            quantity=1
        )
        
        assert result['success'] is True
        assert result['has_custom_pricing'] is True
        assert result['final_price'] == 850.0  # 15% discount
    
    def test_customer_price_no_custom_rule(self, service):
        """Test customer pricing without custom rule"""
        result = service.get_customer_price(
            customer_id='CUST999',
            product_id='PROD001',
            base_price=1000.0,
            quantity=1
        )
        
        assert result['success'] is True
        assert result['has_custom_pricing'] is False
        assert result['final_price'] == 1000.0


class TestBundlePricing:
    """Test bundle pricing logic"""
    
    def test_bundle_with_discount(self, service):
        """Test bundle pricing with discount"""
        items = [
            {'product_id': 'solar_panel', 'quantity': 20, 'unit_price': 250},
            {'product_id': 'inverter', 'quantity': 1, 'unit_price': 1500},
            {'product_id': 'battery', 'quantity': 1, 'unit_price': 5000}
        ]
        
        bundle_rules = {
            'discount_percentage': 10
        }
        
        result = service.calculate_bundle_price(items, bundle_rules)
        
        assert result['success'] is True
        assert result['individual_total'] == 11500.0  # 5000 + 1500 + 5000
        assert result['bundle_discount_percentage'] == 10.0
        assert result['bundle_total'] == 10350.0  # 10% off
        assert result['savings'] == 1150.0
    
    def test_bundle_without_discount(self, service):
        """Test bundle pricing without discount"""
        items = [
            {'product_id': 'solar_panel', 'quantity': 10, 'unit_price': 250}
        ]
        
        result = service.calculate_bundle_price(items, None)
        
        assert result['success'] is True
        assert result['individual_total'] == 2500.0
        assert result['bundle_total'] == 2500.0
        assert result['savings'] == 0


class TestPromotionalPricing:
    """Test promotional pricing"""
    
    def test_create_promotion(self, service):
        """Test creating a promotion"""
        result = service.create_promotion(
            name="Summer Sale",
            promotion_type="percentage",
            discount_value=20.0,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=30)
        )
        
        assert result['success'] is True
        assert 'promotion_id' in result


class TestCurrencyConversion:
    """Test currency conversion"""
    
    def test_set_exchange_rate(self, service):
        """Test setting exchange rate"""
        result = service.set_exchange_rate(
            from_currency='EUR',
            to_currency='USD',
            rate=1.10
        )
        
        assert result['success'] is True
        assert result['rate'] == 1.10
    
    def test_convert_currency(self, service):
        """Test currency conversion"""
        # Set rate first
        service.set_exchange_rate('EUR', 'USD', 1.10)
        
        result = service.convert_currency(
            amount=1000.0,
            from_currency='EUR',
            to_currency='USD'
        )
        
        assert result['success'] is True
        assert result['converted_amount'] == 1100.0
    
    def test_convert_same_currency(self, service):
        """Test converting same currency"""
        result = service.convert_currency(
            amount=1000.0,
            from_currency='EUR',
            to_currency='EUR'
        )
        
        assert result['success'] is True
        assert result['converted_amount'] == 1000.0
    
    def test_multi_currency_price(self, service):
        """Test multi-currency pricing"""
        # Set rates
        service.set_exchange_rate('EUR', 'USD', 1.10)
        service.set_exchange_rate('EUR', 'GBP', 0.85)
        
        result = service.get_multi_currency_price(
            base_price=1000.0,
            base_currency='EUR',
            target_currencies=['USD', 'GBP']
        )
        
        assert result['success'] is True
        assert 'EUR' in result['prices']
        assert 'USD' in result['prices']
        assert 'GBP' in result['prices']
        assert result['prices']['EUR'] == 1000.0
        assert result['prices']['USD'] == 1100.0
        assert result['prices']['GBP'] == 850.0


class TestPriceHistory:
    """Test price history tracking"""
    
    def test_record_price_change(self, service):
        """Test recording price change"""
        result = service.record_price_change(
            product_id='PROD001',
            old_price=1000.0,
            new_price=1100.0,
            reason='Market adjustment',
            changed_by='admin'
        )
        
        assert result['success'] is True
        assert 'history_id' in result
    
    def test_get_price_history(self, service):
        """Test getting price history"""
        # Record some changes
        service.record_price_change('PROD001', 1000.0, 1100.0, 'Increase')
        service.record_price_change('PROD001', 1100.0, 1050.0, 'Decrease')
        
        result = service.get_price_history(product_id='PROD001')
        
        assert result['success'] is True
        assert result['count'] >= 2
        assert len(result['history']) >= 2
    
    def test_get_price_trend(self, service):
        """Test price trend analysis"""
        # Record changes
        service.record_price_change('PROD001', 1000.0, 1100.0, 'Increase')
        service.record_price_change('PROD001', 1100.0, 1200.0, 'Increase')
        
        result = service.get_price_trend(product_id='PROD001', days=30)
        
        assert result['success'] is True
        assert result['trend'] == 'increasing'
        assert result['changes_count'] >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
