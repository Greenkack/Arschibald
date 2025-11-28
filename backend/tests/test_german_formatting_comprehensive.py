"""
Comprehensive German Formatting and Universal Data Testing

Task 232: Test German formatting in all components, dynamic keys,
PDF byte generation, and bidirectional number conversion.

Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.9
"""

import pytest
from decimal import Decimal
import sys
import os
import time
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.german_formatter import (
    GermanNumberFormatter,
    format_german,
    parse_german,
    format_currency_german,
    format_percent_german,
    validate_german,
    default_formatter
)


class TestGermanNumberFormatterBasic:
    """Test basic German number formatting functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_format_simple_integer(self):
        """Test formatting simple integers."""
        assert self.formatter.format(1234) == "1.234,00"
        assert self.formatter.format(0) == "0,00"
        assert self.formatter.format(1) == "1,00"
        assert self.formatter.format(999) == "999,00"
    
    def test_format_large_numbers(self):
        """Test formatting large numbers with thousand separators."""
        assert self.formatter.format(1234567) == "1.234.567,00"
        assert self.formatter.format(1234567890) == "1.234.567.890,00"
        assert self.formatter.format(999999999999) == "999.999.999.999,00"
    
    def test_format_decimal_numbers(self):
        """Test formatting decimal numbers."""
        assert self.formatter.format(1234.56) == "1.234,56"
        assert self.formatter.format(0.5) == "0,50"
        assert self.formatter.format(0.05) == "0,05"
        assert self.formatter.format(1234567.89) == "1.234.567,89"
    
    def test_format_negative_numbers(self):
        """Test formatting negative numbers."""
        assert self.formatter.format(-1234.56) == "-1.234,56"
        assert self.formatter.format(-0.5) == "-0,50"
        assert self.formatter.format(-1234567) == "-1.234.567,00"
    
    def test_format_custom_decimal_places(self):
        """Test formatting with custom decimal places."""
        assert self.formatter.format(1234.5678, decimal_places=4) == "1.234,5678"
        assert self.formatter.format(1234.5, decimal_places=0) == "1.234"  # Rounds down
        assert self.formatter.format(1234.5, decimal_places=3) == "1.234,500"
    
    def test_format_string_input(self):
        """Test formatting string input."""
        assert self.formatter.format("1234.56") == "1.234,56"
        assert self.formatter.format("1234") == "1.234,00"
    
    def test_format_decimal_input(self):
        """Test formatting Decimal input."""
        assert self.formatter.format(Decimal("1234.56")) == "1.234,56"
        assert self.formatter.format(Decimal("0.005")) == "0,00"  # Rounds to 2 decimal places


class TestGermanNumberFormatterParsing:
    """Test German number parsing functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_parse_simple_numbers(self):
        """Test parsing simple German numbers."""
        assert self.formatter.parse("1.234,56") == Decimal("1234.56")
        assert self.formatter.parse("0,50") == Decimal("0.50")
        assert self.formatter.parse("999,00") == Decimal("999.00")
    
    def test_parse_large_numbers(self):
        """Test parsing large German numbers."""
        assert self.formatter.parse("1.234.567,89") == Decimal("1234567.89")
        assert self.formatter.parse("999.999.999,99") == Decimal("999999999.99")
    
    def test_parse_negative_numbers(self):
        """Test parsing negative German numbers."""
        assert self.formatter.parse("-1.234,56") == Decimal("-1234.56")
        assert self.formatter.parse("-999.999,99") == Decimal("-999999.99")
    
    def test_parse_integers(self):
        """Test parsing German integers."""
        assert self.formatter.parse("1.234") == Decimal("1234")
        assert self.formatter.parse("999") == Decimal("999")
    
    def test_parse_invalid_format(self):
        """Test parsing invalid formats raises ValueError."""
        with pytest.raises(ValueError):
            self.formatter.parse("1,234.56")  # US format
        with pytest.raises(ValueError):
            self.formatter.parse("abc")
        with pytest.raises(ValueError):
            self.formatter.parse("")


class TestBidirectionalConversion:
    """Test bidirectional conversion (display ↔ calculation)."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_roundtrip_conversion(self):
        """Test that format -> parse -> format gives same result."""
        test_values = [
            1234.56, 0.5, 1234567.89, -999.99, 0.01, 
            12345678.90, 0.00, 100.00, -0.01
        ]
        
        for value in test_values:
            formatted = self.formatter.format(value)
            parsed = self.formatter.parse(formatted)
            reformatted = self.formatter.format(parsed)
            assert formatted == reformatted, f"Roundtrip failed for {value}"
    
    def test_parse_format_roundtrip(self):
        """Test that parse -> format -> parse gives same result."""
        test_strings = [
            "1.234,56", "0,50", "1.234.567,89", "-999,99",
            "0,01", "12.345.678,90", "0,00", "100,00"
        ]
        
        for german_str in test_strings:
            parsed = self.formatter.parse(german_str)
            formatted = self.formatter.format(parsed)
            reparsed = self.formatter.parse(formatted)
            assert parsed == reparsed, f"Roundtrip failed for {german_str}"
    
    def test_calculation_accuracy(self):
        """Test that calculations remain accurate after conversion."""
        # Simulate a calculation workflow
        price1 = self.formatter.parse("1.234,56")
        price2 = self.formatter.parse("567,89")
        
        total = price1 + price2
        formatted_total = self.formatter.format(total)
        
        assert formatted_total == "1.802,45"
        
        # Verify we can parse it back
        parsed_total = self.formatter.parse(formatted_total)
        assert parsed_total == Decimal("1802.45")


class TestCurrencyFormatting:
    """Test currency formatting functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_format_euro(self):
        """Test Euro currency formatting."""
        assert self.formatter.format_currency(1234.56) == "1.234,56 €"
        assert self.formatter.format_currency(0) == "0,00 €"
        assert self.formatter.format_currency(-500.00) == "-500,00 €"
    
    def test_format_other_currencies(self):
        """Test other currency symbols."""
        assert self.formatter.format_currency(1234.56, "$", "prefix") == "$ 1.234,56"
        assert self.formatter.format_currency(1234.56, "CHF") == "1.234,56 CHF"
    
    def test_format_large_currency(self):
        """Test large currency amounts."""
        assert self.formatter.format_currency(1234567.89) == "1.234.567,89 €"


class TestPercentageFormatting:
    """Test percentage formatting functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_format_percent_from_decimal(self):
        """Test percentage formatting from decimal values."""
        assert self.formatter.format_percent(0.15) == "15,00 %"
        assert self.formatter.format_percent(0.5) == "50,00 %"
        assert self.formatter.format_percent(1.0) == "100,00 %"
    
    def test_format_percent_direct(self):
        """Test percentage formatting without multiplication."""
        assert self.formatter.format_percent(15, multiply_by_100=False) == "15,00 %"
        assert self.formatter.format_percent(50.5, multiply_by_100=False) == "50,50 %"
    
    def test_format_small_percentages(self):
        """Test small percentage values."""
        assert self.formatter.format_percent(0.001) == "0,10 %"
        assert self.formatter.format_percent(0.0001) == "0,01 %"


class TestEdgeCases:
    """Test edge cases for German formatting."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_very_large_numbers(self):
        """Test very large numbers."""
        large = 999999999999.99
        formatted = self.formatter.format(large)
        assert "999.999.999.999,99" == formatted
    
    def test_very_small_numbers(self):
        """Test very small numbers."""
        assert self.formatter.format(0.001, decimal_places=3) == "0,001"
        assert self.formatter.format(0.0001, decimal_places=4) == "0,0001"
    
    def test_zero_values(self):
        """Test zero values."""
        assert self.formatter.format(0) == "0,00"
        assert self.formatter.format(0.0) == "0,00"
        assert self.formatter.format(Decimal("0")) == "0,00"
    
    def test_negative_zero(self):
        """Test negative zero handling."""
        assert self.formatter.format(-0.0) == "0,00"
    
    def test_rounding(self):
        """Test rounding behavior."""
        assert self.formatter.format(1.234) == "1,23"
        assert self.formatter.format(1.235) == "1,24"  # Round half up
        assert self.formatter.format(1.2349) == "1,23"
        assert self.formatter.format(1.2351) == "1,24"


class TestValidation:
    """Test German number validation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_valid_formats(self):
        """Test valid German number formats."""
        valid_numbers = [
            "1.234,56", "0,50", "999", "1.234.567,89",
            "-1.234,56", "0,00", "123", "1.000"
        ]
        for num in valid_numbers:
            assert self.formatter.validate(num), f"{num} should be valid"
    
    def test_invalid_formats(self):
        """Test invalid German number formats."""
        invalid_numbers = [
            "1,234.56",  # US format
            "1234.56",   # Standard format
            "abc",       # Not a number
            "",          # Empty
            "1..234",    # Double separator
            "1,234,56",  # Wrong separators
        ]
        for num in invalid_numbers:
            assert not self.formatter.validate(num), f"{num} should be invalid"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_format_german(self):
        """Test format_german convenience function."""
        assert format_german(1234.56) == "1.234,56"
        assert format_german(1234.5678, decimal_places=4) == "1.234,5678"
    
    def test_parse_german(self):
        """Test parse_german convenience function."""
        assert parse_german("1.234,56") == Decimal("1234.56")
    
    def test_format_currency_german(self):
        """Test format_currency_german convenience function."""
        assert format_currency_german(1234.56) == "1.234,56 €"
    
    def test_format_percent_german(self):
        """Test format_percent_german convenience function."""
        assert format_percent_german(0.15) == "15,00 %"
    
    def test_validate_german(self):
        """Test validate_german convenience function."""
        assert validate_german("1.234,56") is True
        assert validate_german("invalid") is False


class TestPerformance:
    """Test performance with large datasets."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_format_10000_numbers(self):
        """Test formatting 10,000+ numbers."""
        numbers = [random.uniform(-1000000, 1000000) for _ in range(10000)]
        
        start_time = time.time()
        for num in numbers:
            self.formatter.format(num)
        elapsed = time.time() - start_time
        
        # Should complete in under 2 seconds
        assert elapsed < 2.0, f"Formatting 10,000 numbers took {elapsed:.2f}s"
        print(f"\nFormatted 10,000 numbers in {elapsed:.3f}s")
    
    def test_parse_10000_numbers(self):
        """Test parsing 10,000+ German numbers."""
        # Generate German-formatted numbers
        german_numbers = [
            self.formatter.format(random.uniform(-1000000, 1000000))
            for _ in range(10000)
        ]
        
        start_time = time.time()
        for num in german_numbers:
            self.formatter.parse(num)
        elapsed = time.time() - start_time
        
        # Should complete in under 2 seconds
        assert elapsed < 2.0, f"Parsing 10,000 numbers took {elapsed:.2f}s"
        print(f"\nParsed 10,000 numbers in {elapsed:.3f}s")
    
    def test_roundtrip_10000_numbers(self):
        """Test roundtrip conversion of 10,000+ numbers."""
        numbers = [random.uniform(-1000000, 1000000) for _ in range(10000)]
        
        start_time = time.time()
        for num in numbers:
            formatted = self.formatter.format(num)
            parsed = self.formatter.parse(formatted)
            # Verify accuracy
            assert abs(float(parsed) - round(num, 2)) < 0.01
        elapsed = time.time() - start_time
        
        # Should complete in under 4 seconds
        assert elapsed < 4.0, f"Roundtrip 10,000 numbers took {elapsed:.2f}s"
        print(f"\nRoundtrip 10,000 numbers in {elapsed:.3f}s")


class TestLocaleConsistency:
    """Test locale consistency across application."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.formatter = GermanNumberFormatter()
    
    def test_consistent_separators(self):
        """Test that separators are consistent."""
        # All formatted numbers should use German separators
        test_values = [1234.56, 1234567.89, 0.5, -999.99]
        
        for value in test_values:
            formatted = self.formatter.format(value)
            # Should contain comma as decimal separator
            assert "," in formatted or "." in formatted
            # Should NOT contain US-style decimal point at end
            assert not formatted.endswith(".")
    
    def test_currency_consistency(self):
        """Test currency formatting consistency."""
        amounts = [100, 1000, 10000, 100000]
        
        for amount in amounts:
            formatted = self.formatter.format_currency(amount)
            # Should always end with € symbol
            assert formatted.endswith(" €")
            # Should use German decimal separator
            assert "," in formatted
    
    def test_percentage_consistency(self):
        """Test percentage formatting consistency."""
        values = [0.1, 0.5, 1.0, 0.01]
        
        for value in values:
            formatted = self.formatter.format_percent(value)
            # Should always end with % symbol
            assert formatted.endswith(" %")
            # Should use German decimal separator
            assert "," in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
