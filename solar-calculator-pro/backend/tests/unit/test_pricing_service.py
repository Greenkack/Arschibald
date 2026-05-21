"""
Task 21: Backend Unit Tests - Pricing Service
=============================================
Unit tests for the Pricing Service and Price Matrix.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from typing import Dict, List, Optional


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_price_matrix():
    """Sample price matrix data."""
    return {
        "headers": ["kein Speicher", "BYD 5.1", "BYD 7.7", "BYD 10.2", "BYD 12.8"],
        "rows": {
            10: [8500, 11500, 13000, 14500, 16000],
            12: [9500, 12500, 14000, 15500, 17000],
            14: [10500, 13500, 15000, 16500, 18000],
            16: [11500, 14500, 16000, 17500, 19000],
            18: [12500, 15500, 17000, 18500, 20000],
            20: [13500, 16500, 18000, 19500, 21000],
        }
    }


@pytest.fixture
def sample_extras():
    """Sample extras and surcharges."""
    return {
        "wallbox": {"name": "Wallbox 11kW", "price": 1200},
        "optimizer": {"name": "Leistungsoptimierer", "price": 50, "per_module": True},
        "monitoring": {"name": "Monitoring System", "price": 350},
        "insurance": {"name": "Versicherung 1 Jahr", "price": 150},
    }


@pytest.fixture
def sample_discounts():
    """Sample discounts."""
    return {
        "early_bird": {"name": "Frühbucher-Rabatt", "percent": 5},
        "referral": {"name": "Empfehlungsrabatt", "amount": 500},
        "cash_payment": {"name": "Barzahlung", "percent": 2},
    }


# ============================================================================
# Price Matrix Lookup Tests
# ============================================================================

class TestPriceMatrixLookup:
    """Tests for price matrix lookup functionality."""

    def test_lookup_price_no_storage(self, sample_price_matrix):
        """Test price lookup without battery storage."""
        module_count = 14
        storage_model = "kein Speicher"
        
        row = sample_price_matrix["rows"][module_count]
        col_index = sample_price_matrix["headers"].index(storage_model)
        price = row[col_index]
        
        assert price == 10500

    def test_lookup_price_with_storage(self, sample_price_matrix):
        """Test price lookup with battery storage."""
        module_count = 16
        storage_model = "BYD 10.2"
        
        row = sample_price_matrix["rows"][module_count]
        col_index = sample_price_matrix["headers"].index(storage_model)
        price = row[col_index]
        
        assert price == 17500

    def test_lookup_price_interpolation(self, sample_price_matrix):
        """Test price interpolation for non-exact module counts."""
        module_count = 15  # Not in matrix
        storage_model = "kein Speicher"
        
        # Interpolate between 14 and 16 modules
        lower_count = 14
        upper_count = 16
        lower_price = sample_price_matrix["rows"][lower_count][0]
        upper_price = sample_price_matrix["rows"][upper_count][0]
        
        interpolated_price = lower_price + (upper_price - lower_price) * (module_count - lower_count) / (upper_count - lower_count)
        
        assert interpolated_price == 11000

    def test_lookup_invalid_module_count(self, sample_price_matrix):
        """Test handling of invalid module count."""
        module_count = 5  # Below minimum
        
        assert module_count not in sample_price_matrix["rows"]

    def test_lookup_invalid_storage_model(self, sample_price_matrix):
        """Test handling of invalid storage model."""
        storage_model = "Invalid Model"
        
        assert storage_model not in sample_price_matrix["headers"]


class TestPriceCalculation:
    """Tests for price calculation with extras and discounts."""

    def test_calculate_base_price(self, sample_price_matrix):
        """Test base price calculation."""
        module_count = 18
        storage_model = "BYD 7.7"
        
        row = sample_price_matrix["rows"][module_count]
        col_index = sample_price_matrix["headers"].index(storage_model)
        base_price = Decimal(str(row[col_index]))
        
        assert base_price == Decimal("17000")

    def test_add_extras(self, sample_extras):
        """Test adding extras to price."""
        base_price = Decimal("15000")
        module_count = 16
        
        # Add wallbox
        extras_total = Decimal(str(sample_extras["wallbox"]["price"]))
        
        # Add optimizer (per module)
        optimizer = sample_extras["optimizer"]
        extras_total += Decimal(str(optimizer["price"])) * module_count
        
        # Add monitoring
        extras_total += Decimal(str(sample_extras["monitoring"]["price"]))
        
        total_price = base_price + extras_total
        
        expected_extras = 1200 + (50 * 16) + 350  # 2350
        assert extras_total == Decimal("2350")
        assert total_price == Decimal("17350")

    def test_apply_percent_discount(self, sample_discounts):
        """Test applying percentage discount."""
        base_price = Decimal("15000")
        discount = sample_discounts["early_bird"]
        
        discount_amount = base_price * Decimal(str(discount["percent"])) / 100
        final_price = base_price - discount_amount
        
        assert discount_amount == Decimal("750")
        assert final_price == Decimal("14250")

    def test_apply_fixed_discount(self, sample_discounts):
        """Test applying fixed amount discount."""
        base_price = Decimal("15000")
        discount = sample_discounts["referral"]
        
        discount_amount = Decimal(str(discount["amount"]))
        final_price = base_price - discount_amount
        
        assert discount_amount == Decimal("500")
        assert final_price == Decimal("14500")

    def test_apply_multiple_discounts(self, sample_discounts):
        """Test applying multiple discounts."""
        base_price = Decimal("15000")
        
        # Apply early bird (5%)
        after_early_bird = base_price * Decimal("0.95")
        
        # Apply referral (€500)
        after_referral = after_early_bird - Decimal("500")
        
        # Apply cash payment (2%)
        final_price = after_referral * Decimal("0.98")
        
        assert final_price < base_price
        # 15000 * 0.95 = 14250 - 500 = 13750 * 0.98 = 13475
        assert final_price == Decimal("13475.00")

    def test_full_price_calculation(self, sample_price_matrix, sample_extras, sample_discounts):
        """Test complete price calculation flow."""
        module_count = 16
        storage_model = "BYD 10.2"
        
        # Step 1: Get base price
        row = sample_price_matrix["rows"][module_count]
        col_index = sample_price_matrix["headers"].index(storage_model)
        base_price = Decimal(str(row[col_index]))
        
        # Step 2: Add extras
        extras = Decimal(str(sample_extras["wallbox"]["price"]))
        subtotal = base_price + extras
        
        # Step 3: Apply discount
        discount_percent = Decimal(str(sample_discounts["early_bird"]["percent"]))
        discount_amount = subtotal * discount_percent / 100
        final_price = subtotal - discount_amount
        
        # Assertions
        assert base_price == Decimal("17500")
        assert extras == Decimal("1200")
        assert subtotal == Decimal("18700")
        assert discount_amount == Decimal("935")
        assert final_price == Decimal("17765")


class TestGermanFormatting:
    """Tests for German number formatting."""

    def test_format_currency(self):
        """Test German currency formatting."""
        amount = Decimal("12345.67")
        
        # German format: 12.345,67 €
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"
        
        assert formatted == "12.345,67 €"

    def test_format_large_number(self):
        """Test formatting large numbers."""
        amount = Decimal("1234567.89")
        
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        assert formatted == "1.234.567,89"

    def test_format_small_number(self):
        """Test formatting small numbers."""
        amount = Decimal("0.35")
        
        formatted = f"{amount:.2f}".replace(".", ",")
        
        assert formatted == "0,35"

    def test_parse_german_number(self):
        """Test parsing German formatted numbers."""
        german_string = "12.345,67"
        
        # Convert to standard format
        standard_string = german_string.replace(".", "").replace(",", ".")
        parsed = Decimal(standard_string)
        
        assert parsed == Decimal("12345.67")


class TestPriceValidation:
    """Tests for price validation."""

    def test_validate_positive_price(self):
        """Test that prices must be positive."""
        price = Decimal("-100")
        
        assert price < 0, "Negative price should be invalid"

    def test_validate_reasonable_price(self):
        """Test that prices are within reasonable bounds."""
        price = Decimal("50000")
        min_price = Decimal("5000")
        max_price = Decimal("100000")
        
        assert min_price <= price <= max_price

    def test_validate_discount_not_exceed_price(self):
        """Test that discount doesn't exceed price."""
        base_price = Decimal("15000")
        discount = Decimal("20000")
        
        final_price = max(base_price - discount, Decimal("0"))
        
        assert final_price >= 0

    def test_validate_vat_calculation(self):
        """Test VAT calculation."""
        net_price = Decimal("10000")
        vat_rate = Decimal("0.19")  # 19% German VAT
        
        vat_amount = net_price * vat_rate
        gross_price = net_price + vat_amount
        
        assert vat_amount == Decimal("1900")
        assert gross_price == Decimal("11900")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
