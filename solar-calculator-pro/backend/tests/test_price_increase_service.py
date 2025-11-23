"""
Tests for Price Increase Service

Tests the critical price increase logic for multi-PDF generation.
"""

import pytest
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.price_increase_service import (
    PriceIncreaseService,
    IncreaseStrategy,
    get_price_increase_service
)


@pytest.fixture
def service():
    """Create a fresh service instance for each test"""
    service = PriceIncreaseService()
    service.initialize()
    service.reset_price_state()
    return service


class TestServiceInitialization:
    """Test service initialization"""
    
    def test_service_initializes_successfully(self, service):
        """Test that service initializes without errors"""
        assert service.is_initialized
        assert service.health_check().status.value == "healthy"
    
    def test_singleton_returns_same_instance(self):
        """Test that get_price_increase_service returns singleton"""
        service1 = get_price_increase_service()
        service2 = get_price_increase_service()
        assert service1 is service2


class TestConfiguration:
    """Test configuration management"""
    
    def test_default_configuration(self, service):
        """Test default configuration values"""
        config = service.get_configuration()
        assert config["default_increase_rate"] == 0.07  # 7%
        assert config["strategy"] == "cumulative"
        assert config["min_increase_rate"] == 0.01
        assert config["max_increase_rate"] == 0.50
    
    def test_set_increase_rate(self, service):
        """Test setting increase rate"""
        service.set_increase_rate(0.10)  # 10%
        config = service.get_configuration()
        assert config["default_increase_rate"] == 0.10
    
    def test_set_increase_rate_validates_minimum(self, service):
        """Test that increase rate validates minimum"""
        with pytest.raises(ValueError):
            service.set_increase_rate(0.005)  # Below minimum
    
    def test_set_increase_rate_validates_maximum(self, service):
        """Test that increase rate validates maximum"""
        with pytest.raises(ValueError):
            service.set_increase_rate(0.60)  # Above maximum
    
    def test_set_strategy(self, service):
        """Test setting strategy"""
        service.set_strategy("fixed")
        config = service.get_configuration()
        assert config["strategy"] == "fixed"
    
    def test_set_invalid_strategy_raises_error(self, service):
        """Test that invalid strategy raises error"""
        with pytest.raises(ValueError):
            service.set_strategy("invalid_strategy")
    
    def test_set_custom_rates(self, service):
        """Test setting custom rates"""
        rates = [0.05, 0.10, 0.15]
        service.set_custom_rates(rates)
        config = service.get_configuration()
        assert config["custom_rates"] == rates


class TestPriceStateManagement:
    """Test price state management"""
    
    def test_set_base_price(self, service):
        """Test setting base price"""
        service.set_base_price(16999.00)
        assert service.get_current_price() == 16999.00
    
    def test_reset_price_state(self, service):
        """Test resetting price state"""
        service.set_base_price(16999.00)
        service.calculate_next_price()
        service.reset_price_state()
        assert service.get_current_price() is None
        assert len(service.get_price_history()) == 0
    
    def test_price_history_includes_base(self, service):
        """Test that price history includes base price"""
        service.set_base_price(16999.00)
        history = service.get_price_history()
        assert len(history) == 1
        assert history[0]["is_base"] is True
        assert history[0]["price"] == 16999.00


class TestCumulativeStrategy:
    """Test cumulative increase strategy"""
    
    def test_cumulative_first_offer(self, service):
        """Test first offer with cumulative strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)  # 7%
        
        result = service.calculate_next_price()
        
        # 16999 * 1.07 = 18188.93
        assert result["offer_index"] == 1
        assert abs(result["price"] - 18188.93) < 0.01
        assert result["increase_rate"] == 0.07
    
    def test_cumulative_second_offer(self, service):
        """Test second offer with cumulative strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)  # 7%
        
        service.calculate_next_price()  # First offer
        result = service.calculate_next_price()  # Second offer
        
        # 18188.93 * 1.07 = 19462.16
        assert result["offer_index"] == 2
        assert abs(result["price"] - 19462.16) < 0.01
    
    def test_cumulative_third_offer(self, service):
        """Test third offer with cumulative strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)  # 7%
        
        service.calculate_next_price()  # First offer
        service.calculate_next_price()  # Second offer
        result = service.calculate_next_price()  # Third offer
        
        # 19462.16 * 1.07 = 20824.51
        assert result["offer_index"] == 3
        assert abs(result["price"] - 20824.51) < 0.01


class TestFixedStrategy:
    """Test fixed increase strategy"""
    
    def test_fixed_first_offer(self, service):
        """Test first offer with fixed strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("fixed")
        service.set_increase_rate(0.07)  # 7%
        
        result = service.calculate_next_price()
        
        # 16999 * (1 + 0.07 * 1) = 18188.93
        assert result["offer_index"] == 1
        assert abs(result["price"] - 18188.93) < 0.01
    
    def test_fixed_second_offer(self, service):
        """Test second offer with fixed strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("fixed")
        service.set_increase_rate(0.07)  # 7%
        
        service.calculate_next_price()  # First offer
        result = service.calculate_next_price()  # Second offer
        
        # 16999 * (1 + 0.07 * 2) = 19378.86
        assert result["offer_index"] == 2
        assert abs(result["price"] - 19378.86) < 0.01
    
    def test_fixed_third_offer(self, service):
        """Test third offer with fixed strategy"""
        service.set_base_price(16999.00)
        service.set_strategy("fixed")
        service.set_increase_rate(0.07)  # 7%
        
        service.calculate_next_price()  # First offer
        service.calculate_next_price()  # Second offer
        result = service.calculate_next_price()  # Third offer
        
        # 16999 * (1 + 0.07 * 3) = 20568.79
        assert result["offer_index"] == 3
        assert abs(result["price"] - 20568.79) < 0.01


class TestCustomStrategy:
    """Test custom increase strategy"""
    
    def test_custom_rates(self, service):
        """Test custom rates for each offer"""
        service.set_base_price(16999.00)
        service.set_strategy("custom")
        service.set_custom_rates([0.05, 0.10, 0.15])  # 5%, 10%, 15%
        
        # First offer: 16999 * 1.05 = 17848.95
        result1 = service.calculate_next_price()
        assert abs(result1["price"] - 17848.95) < 0.01
        
        # Second offer: 16999 * 1.10 = 18698.90
        result2 = service.calculate_next_price()
        assert abs(result2["price"] - 18698.90) < 0.01
        
        # Third offer: 16999 * 1.15 = 19548.85
        result3 = service.calculate_next_price()
        assert abs(result3["price"] - 19548.85) < 0.01


class TestPriceCalculation:
    """Test price calculation methods"""
    
    def test_calculate_price_for_specific_offer(self, service):
        """Test calculating price for specific offer index"""
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)
        
        # Calculate for offer 3 directly
        result = service.calculate_price_for_offer(3)
        
        # 16999 * (1.07)^3 = 20824.51
        assert result["offer_index"] == 3
        assert abs(result["price"] - 20824.51) < 0.01
    
    def test_calculate_all_prices(self, service):
        """Test calculating all prices at once"""
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)
        
        prices = service.calculate_all_prices(3)
        
        assert len(prices) == 4  # Base + 3 offers
        assert prices[0]["offer_index"] == 0  # Base
        assert prices[0]["price"] == 16999.00
        assert prices[1]["offer_index"] == 1
        assert abs(prices[1]["price"] - 18188.93) < 0.01
        assert prices[2]["offer_index"] == 2
        assert abs(prices[2]["price"] - 19462.16) < 0.01
        assert prices[3]["offer_index"] == 3
        assert abs(prices[3]["price"] - 20824.51) < 0.01
    
    def test_calculate_without_base_price_raises_error(self, service):
        """Test that calculating without base price raises error"""
        with pytest.raises(RuntimeError):
            service.calculate_next_price()


class TestGermanFormatting:
    """Test German number formatting"""
    
    def test_price_formatted_in_german(self, service):
        """Test that prices are formatted in German"""
        service.set_base_price(16999.00)
        result = service.calculate_next_price()
        
        # Should be formatted as "18.188,93 €"
        assert "€" in result["price_formatted"]
        assert "," in result["price_formatted"]  # Decimal separator
        assert "." in result["price_formatted"]  # Thousand separator
    
    def test_increase_amount_formatted(self, service):
        """Test that increase amount is formatted"""
        service.set_base_price(16999.00)
        result = service.calculate_next_price()
        
        assert "€" in result["increase_amount_formatted"]
        assert result["increase_amount"] > 0


class TestPriceComparison:
    """Test price comparison functionality"""
    
    def test_price_comparison_report(self, service):
        """Test generating price comparison report"""
        service.set_base_price(16999.00)
        service.set_increase_rate(0.07)
        
        service.calculate_next_price()
        service.calculate_next_price()
        service.calculate_next_price()
        
        comparison = service.generate_price_comparison()
        
        assert comparison["total_offers"] == 3
        assert comparison["base_price"] == 16999.00
        assert comparison["current_price"] > comparison["base_price"]
        assert comparison["total_increase"] > 0
        assert "%" in comparison["total_increase_percentage"]
        assert "%" in comparison["average_increase_percentage"]
    
    def test_empty_comparison(self, service):
        """Test comparison with no prices"""
        comparison = service.generate_price_comparison()
        
        assert comparison["total_offers"] == 0
        assert comparison["base_price"] is None
        assert comparison["current_price"] is None


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_small_base_price(self, service):
        """Test with very small base price"""
        service.set_base_price(1.00)
        result = service.calculate_next_price()
        
        assert result["price"] > 1.00
        assert result["price"] < 2.00  # Should be 1.07
    
    def test_very_large_base_price(self, service):
        """Test with very large base price"""
        service.set_base_price(999999.99)
        result = service.calculate_next_price()
        
        assert result["price"] > 999999.99
        assert result["increase_amount"] > 0
    
    def test_zero_increase_rate(self, service):
        """Test with minimum increase rate"""
        service.set_base_price(16999.00)
        service.set_increase_rate(0.01)  # 1%
        
        result = service.calculate_next_price()
        
        # 16999 * 1.01 = 17168.99
        assert abs(result["price"] - 17168.99) < 0.01
    
    def test_maximum_increase_rate(self, service):
        """Test with maximum increase rate"""
        service.set_base_price(16999.00)
        service.set_increase_rate(0.50)  # 50%
        
        result = service.calculate_next_price()
        
        # 16999 * 1.50 = 25498.50
        assert abs(result["price"] - 25498.50) < 0.01
    
    def test_many_offers(self, service):
        """Test generating many offers"""
        service.set_base_price(16999.00)
        service.set_increase_rate(0.07)
        
        prices = service.calculate_all_prices(10)
        
        assert len(prices) == 11  # Base + 10 offers
        assert prices[-1]["price"] > prices[0]["price"]
        
        # Each price should be higher than previous
        for i in range(1, len(prices)):
            assert prices[i]["price"] > prices[i-1]["price"]


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    def test_multi_pdf_scenario(self, service):
        """Test typical multi-PDF generation scenario"""
        # Setup: 8 companies, 7% increase
        service.set_base_price(16999.00)
        service.set_strategy("cumulative")
        service.set_increase_rate(0.07)
        
        # Generate prices for 8 offers
        prices = service.calculate_all_prices(8)
        
        assert len(prices) == 9  # Base + 8 offers
        
        # Verify each offer is more expensive
        for i in range(1, len(prices)):
            assert prices[i]["price"] > prices[i-1]["price"]
            assert prices[i]["increase_rate"] == 0.07
        
        # Verify final price is significantly higher
        final_price = prices[-1]["price"]
        base_price = prices[0]["price"]
        assert final_price > base_price * 1.5  # At least 50% more
    
    def test_custom_rates_per_company(self, service):
        """Test custom rates for different companies"""
        service.set_base_price(16999.00)
        service.set_strategy("custom")
        
        # Different rates for each company
        service.set_custom_rates([0.05, 0.07, 0.10, 0.12, 0.15])
        
        prices = service.calculate_all_prices(5)
        
        # Verify rates are applied correctly
        assert abs(prices[1]["price"] - 16999.00 * 1.05) < 0.01
        assert abs(prices[2]["price"] - 16999.00 * 1.07) < 0.01
        assert abs(prices[3]["price"] - 16999.00 * 1.10) < 0.01
        assert abs(prices[4]["price"] - 16999.00 * 1.12) < 0.01
        assert abs(prices[5]["price"] - 16999.00 * 1.15) < 0.01
    
    def test_price_tracking_across_offers(self, service):
        """Test price tracking across multiple offers"""
        service.set_base_price(16999.00)
        service.set_increase_rate(0.07)
        
        # Generate offers one by one
        offer1 = service.calculate_next_price()
        offer2 = service.calculate_next_price()
        offer3 = service.calculate_next_price()
        
        # Get history
        history = service.get_price_history()
        
        assert len(history) == 4  # Base + 3 offers
        assert history[1]["price"] == offer1["price"]
        assert history[2]["price"] == offer2["price"]
        assert history[3]["price"] == offer3["price"]
        
        # Get comparison
        comparison = service.generate_price_comparison()
        
        assert comparison["total_offers"] == 3
        assert comparison["current_price"] == offer3["price"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
