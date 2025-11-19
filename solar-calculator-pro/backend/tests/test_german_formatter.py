"""
Unit tests for German Number Formatter

Tests all functionality of the GermanNumberFormatter class including:
- Number formatting (number -> German format)
- Number parsing (German format -> number)
- Currency formatting
- Percentage formatting
- Validation
- Edge cases and error handling
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.german_formatter import (
    GermanNumberFormatter,
    format_german,
    parse_german,
    format_currency_german,
    format_percent_german,
    validate_german
)


class TestGermanNumberFormatter:
    """Test suite for GermanNumberFormatter class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.formatter = GermanNumberFormatter()
    
    # ===== format() method tests =====
    
    def test_format_simple_integer(self):
        """Test formatting simple integers"""
        assert self.formatter.format(1234) == "1.234,00"
        assert self.formatter.format(100) == "100,00"
        assert self.formatter.format(0) == "0,00"
    
    def test_format_simple_float(self):
        """Test formatting simple floats"""
        assert self.formatter.format(1234.56) == "1.234,56"
        assert self.formatter.format(0.5) == "0,50"
        assert self.formatter.format(0.05) == "0,05"
    
    def test_format_large_numbers(self):
        """Test formatting large numbers with multiple thousand separators"""
        assert self.formatter.format(1234567) == "1.234.567,00"
        assert self.formatter.format(1234567.89) == "1.234.567,89"
        assert self.formatter.format(1000000) == "1.000.000,00"
    
    def test_format_negative_numbers(self):
        """Test formatting negative numbers"""
        assert self.formatter.format(-1234.56) == "-1.234,56"
        assert self.formatter.format(-0.5) == "-0,50"
        assert self.formatter.format(-1234567.89) == "-1.234.567,89"
    
    def test_format_decimal_input(self):
        """Test formatting with Decimal input"""
        assert self.formatter.format(Decimal("1234.56")) == "1.234,56"
        assert self.formatter.format(Decimal("0.5")) == "0,50"
    
    def test_format_string_input(self):
        """Test formatting with string input"""
        assert self.formatter.format("1234.56") == "1.234,56"
        assert self.formatter.format("1234") == "1.234,00"
    
    def test_format_custom_decimal_places(self):
        """Test formatting with custom decimal places"""
        assert self.formatter.format(1234.5678, decimal_places=3) == "1.234,568"
        assert self.formatter.format(1234.5678, decimal_places=0) == "1.235"
        assert self.formatter.format(1234.5678, decimal_places=4) == "1.234,5678"
    
    def test_format_rounding(self):
        """Test proper rounding behavior"""
        assert self.formatter.format(1234.566) == "1.234,57"  # Round up
        assert self.formatter.format(1234.564) == "1.234,56"  # Round down
        assert self.formatter.format(1234.565) == "1.234,56"  # Banker's rounding (round to even)
    
    def test_format_very_small_numbers(self):
        """Test formatting very small numbers"""
        assert self.formatter.format(0.01) == "0,01"
        assert self.formatter.format(0.001) == "0,00"
        assert self.formatter.format(0.0001) == "0,00"
    
    def test_format_invalid_input(self):
        """Test formatting with invalid input"""
        with pytest.raises(ValueError):
            self.formatter.format("invalid")
        with pytest.raises(ValueError):
            self.formatter.format("12.34.56")
    
    # ===== parse() method tests =====
    
    def test_parse_simple_german_number(self):
        """Test parsing simple German-formatted numbers"""
        assert self.formatter.parse("1.234,56") == Decimal("1234.56")
        assert self.formatter.parse("100,00") == Decimal("100.00")
        assert self.formatter.parse("0,50") == Decimal("0.50")
    
    def test_parse_large_german_number(self):
        """Test parsing large German-formatted numbers"""
        assert self.formatter.parse("1.234.567,89") == Decimal("1234567.89")
        assert self.formatter.parse("1.000.000,00") == Decimal("1000000.00")
    
    def test_parse_negative_german_number(self):
        """Test parsing negative German-formatted numbers"""
        assert self.formatter.parse("-1.234,56") == Decimal("-1234.56")
        assert self.formatter.parse("-0,50") == Decimal("-0.50")
    
    def test_parse_without_thousand_separator(self):
        """Test parsing numbers without thousand separators"""
        assert self.formatter.parse("123,45") == Decimal("123.45")
        assert self.formatter.parse("12,34") == Decimal("12.34")
    
    def test_parse_integer_only(self):
        """Test parsing integer-only German numbers"""
        assert self.formatter.parse("1.234") == Decimal("1234")
        assert self.formatter.parse("100") == Decimal("100")
    
    def test_parse_with_whitespace(self):
        """Test parsing with leading/trailing whitespace"""
        assert self.formatter.parse("  1.234,56  ") == Decimal("1234.56")
        assert self.formatter.parse(" 100,00 ") == Decimal("100.00")
    
    def test_parse_invalid_format(self):
        """Test parsing invalid formats"""
        with pytest.raises(ValueError):
            self.formatter.parse("1,234.56")  # English format
        with pytest.raises(ValueError):
            self.formatter.parse("1.23.456,78")  # Invalid separator placement
        with pytest.raises(ValueError):
            self.formatter.parse("invalid")
        with pytest.raises(ValueError):
            self.formatter.parse("")
    
    def test_parse_non_string_input(self):
        """Test parsing with non-string input"""
        with pytest.raises(ValueError):
            self.formatter.parse(1234)
        with pytest.raises(ValueError):
            self.formatter.parse(None)
    
    # ===== format_currency() method tests =====
    
    def test_format_currency_default(self):
        """Test currency formatting with default settings"""
        assert self.formatter.format_currency(1234.56) == "1.234,56 €"
        assert self.formatter.format_currency(0.5) == "0,50 €"
    
    def test_format_currency_custom_symbol(self):
        """Test currency formatting with custom symbol"""
        assert self.formatter.format_currency(1234.56, "$") == "1.234,56 $"
        assert self.formatter.format_currency(1234.56, "USD") == "1.234,56 USD"
    
    def test_format_currency_prefix(self):
        """Test currency formatting with prefix position"""
        assert self.formatter.format_currency(1234.56, "$", "prefix") == "$ 1.234,56"
        assert self.formatter.format_currency(1234.56, "€", "prefix") == "€ 1.234,56"
    
    def test_format_currency_negative(self):
        """Test currency formatting with negative amounts"""
        assert self.formatter.format_currency(-1234.56) == "-1.234,56 €"
        assert self.formatter.format_currency(-1234.56, "$", "prefix") == "$ -1.234,56"
    
    # ===== format_percent() method tests =====
    
    def test_format_percent_default(self):
        """Test percentage formatting with default settings"""
        assert self.formatter.format_percent(0.15) == "15,00 %"
        assert self.formatter.format_percent(0.5) == "50,00 %"
        assert self.formatter.format_percent(1.0) == "100,00 %"
    
    def test_format_percent_no_multiply(self):
        """Test percentage formatting without multiplication"""
        assert self.formatter.format_percent(15, multiply_by_100=False) == "15,00 %"
        assert self.formatter.format_percent(50, multiply_by_100=False) == "50,00 %"
    
    def test_format_percent_decimal_input(self):
        """Test percentage formatting with Decimal input"""
        assert self.formatter.format_percent(Decimal("0.15")) == "15,00 %"
        assert self.formatter.format_percent(Decimal("0.125")) == "12,50 %"
    
    def test_format_percent_negative(self):
        """Test percentage formatting with negative values"""
        assert self.formatter.format_percent(-0.15) == "-15,00 %"
        assert self.formatter.format_percent(-15, multiply_by_100=False) == "-15,00 %"
    
    def test_format_percent_small_values(self):
        """Test percentage formatting with small values"""
        assert self.formatter.format_percent(0.001) == "0,10 %"
        assert self.formatter.format_percent(0.0001) == "0,01 %"
    
    # ===== validate() method tests =====
    
    def test_validate_valid_formats(self):
        """Test validation of valid German number formats"""
        assert self.formatter.validate("1.234,56") is True
        assert self.formatter.validate("1.234.567,89") is True
        assert self.formatter.validate("123,45") is True
        assert self.formatter.validate("1.234") is True
        assert self.formatter.validate("123") is True
        assert self.formatter.validate("0,50") is True
        assert self.formatter.validate("-1.234,56") is True
    
    def test_validate_invalid_formats(self):
        """Test validation of invalid formats"""
        assert self.formatter.validate("1,234.56") is False  # English format
        assert self.formatter.validate("1.23.456,78") is False  # Invalid separators
        assert self.formatter.validate("invalid") is False
        assert self.formatter.validate("") is False
        assert self.formatter.validate("12..34") is False
        assert self.formatter.validate("12,,34") is False
    
    def test_validate_non_string(self):
        """Test validation with non-string input"""
        assert self.formatter.validate(1234) is False
        assert self.formatter.validate(None) is False
        assert self.formatter.validate([]) is False
    
    # ===== Helper method tests =====
    
    def test_to_float(self):
        """Test conversion to float"""
        assert self.formatter.to_float("1.234,56") == 1234.56
        assert self.formatter.to_float("0,50") == 0.5
        assert self.formatter.to_float("-1.234,56") == -1234.56
    
    def test_to_int(self):
        """Test conversion to integer"""
        assert self.formatter.to_int("1.234,56") == 1235  # Rounded
        assert self.formatter.to_int("1.234,44") == 1234  # Rounded
        assert self.formatter.to_int("100,00") == 100
    
    # ===== Bidirectional conversion tests =====
    
    def test_bidirectional_conversion(self):
        """Test that format and parse are inverse operations"""
        test_numbers = [1234.56, 0.5, 1234567.89, -1234.56, 0.01]
        
        for number in test_numbers:
            formatted = self.formatter.format(number)
            parsed = self.formatter.parse(formatted)
            assert float(parsed) == pytest.approx(number, rel=1e-9)
    
    def test_round_trip_with_string(self):
        """Test round-trip conversion with string input"""
        original = "1.234,56"
        parsed = self.formatter.parse(original)
        formatted = self.formatter.format(parsed)
        assert formatted == original


class TestConvenienceFunctions:
    """Test suite for convenience functions"""
    
    def test_format_german(self):
        """Test format_german convenience function"""
        assert format_german(1234.56) == "1.234,56"
        assert format_german(1234.56, decimal_places=3) == "1.234,560"
    
    def test_parse_german(self):
        """Test parse_german convenience function"""
        assert parse_german("1.234,56") == Decimal("1234.56")
        assert parse_german("0,50") == Decimal("0.50")
    
    def test_format_currency_german(self):
        """Test format_currency_german convenience function"""
        assert format_currency_german(1234.56) == "1.234,56 €"
        assert format_currency_german(1234.56, "$") == "1.234,56 $"
    
    def test_format_percent_german(self):
        """Test format_percent_german convenience function"""
        assert format_percent_german(0.15) == "15,00 %"
        assert format_percent_german(15, multiply_by_100=False) == "15,00 %"
    
    def test_validate_german(self):
        """Test validate_german convenience function"""
        assert validate_german("1.234,56") is True
        assert validate_german("1,234.56") is False


class TestEdgeCases:
    """Test suite for edge cases and special scenarios"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.formatter = GermanNumberFormatter()
    
    def test_zero_values(self):
        """Test handling of zero values"""
        assert self.formatter.format(0) == "0,00"
        assert self.formatter.format(0.0) == "0,00"
        assert self.formatter.parse("0,00") == Decimal("0")
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        large_num = 999999999999.99
        formatted = self.formatter.format(large_num)
        parsed = self.formatter.parse(formatted)
        assert float(parsed) == pytest.approx(large_num, rel=1e-9)
    
    def test_precision_preservation(self):
        """Test that precision is preserved through conversions"""
        test_value = Decimal("1234.56")
        formatted = self.formatter.format(test_value)
        parsed = self.formatter.parse(formatted)
        assert parsed == test_value
    
    def test_custom_decimal_places_formatter(self):
        """Test formatter with custom default decimal places"""
        formatter_3dp = GermanNumberFormatter(decimal_places=3)
        assert formatter_3dp.format(1234.5) == "1.234,500"
        
        formatter_0dp = GermanNumberFormatter(decimal_places=0)
        assert formatter_0dp.format(1234.5) == "1.234"  # Banker's rounding (round to even)
    
    def test_german_format_string_input(self):
        """Test formatting when input is already in German format"""
        assert self.formatter.format("1.234,56") == "1.234,56"
        assert self.formatter.format("0,50") == "0,50"


class TestRequirementCompliance:
    """Test suite to verify compliance with requirements 14.1, 14.2, 14.6"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.formatter = GermanNumberFormatter()
    
    def test_requirement_14_1_german_locale(self):
        """
        Requirement 14.1: Format all numbers with German locale (de-DE)
        using dot (.) as thousand separator and comma (,) as decimal separator
        """
        # Test thousand separator (dot)
        assert "." in self.formatter.format(1234.56)
        assert self.formatter.format(1234.56).count(".") == 1
        
        # Test decimal separator (comma)
        assert "," in self.formatter.format(1234.56)
        assert self.formatter.format(1234.56).split(",")[0] == "1.234"
        assert self.formatter.format(1234.56).split(",")[1] == "56"
    
    def test_requirement_14_2_two_decimal_places(self):
        """
        Requirement 14.2: Display exactly 2 decimal places for all decimal numbers
        """
        # Test various inputs all result in 2 decimal places
        assert self.formatter.format(1234) == "1.234,00"
        assert self.formatter.format(1234.5) == "1.234,50"
        assert self.formatter.format(1234.56) == "1.234,56"
        assert self.formatter.format(1234.567) == "1.234,57"  # Rounded
        
        # Verify decimal places count
        for number in [0, 1, 10, 100, 1000, 1234.5, 1234.56]:
            formatted = self.formatter.format(number)
            decimal_part = formatted.split(",")[1]
            assert len(decimal_part) == 2, f"Expected 2 decimal places, got {len(decimal_part)}"
    
    def test_requirement_14_6_bidirectional_conversion(self):
        """
        Requirement 14.6: Provide bidirectional conversion between
        German format (display) and standard format (calculation)
        """
        # Test format (standard -> German)
        standard_numbers = [1234.56, 0.5, 1234567.89, -1234.56]
        for num in standard_numbers:
            german = self.formatter.format(num)
            assert isinstance(german, str)
            assert "," in german  # Has German decimal separator
        
        # Test parse (German -> standard)
        german_numbers = ["1.234,56", "0,50", "1.234.567,89", "-1.234,56"]
        for german in german_numbers:
            standard = self.formatter.parse(german)
            assert isinstance(standard, Decimal)
        
        # Test round-trip conversion
        for num in standard_numbers:
            german = self.formatter.format(num)
            back_to_standard = float(self.formatter.parse(german))
            assert back_to_standard == pytest.approx(num, rel=1e-9)
    
    def test_requirement_14_6_validation(self):
        """
        Requirement 14.6: Build validation for German number format
        """
        # Valid German formats
        valid_formats = [
            "1.234,56",
            "1.234.567,89",
            "123,45",
            "1.234",
            "123",
            "0,50",
            "-1.234,56"
        ]
        for fmt in valid_formats:
            assert self.formatter.validate(fmt) is True, f"Should validate: {fmt}"
        
        # Invalid formats
        invalid_formats = [
            "1,234.56",  # English format
            "1.23.456,78",  # Invalid separator placement
            "invalid",
            "",
            "12..34",
            "12,,34"
        ]
        for fmt in invalid_formats:
            assert self.formatter.validate(fmt) is False, f"Should not validate: {fmt}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
