"""
German Number Formatter Core

This module provides comprehensive German number formatting functionality
for the application, supporting bidirectional conversion between German
format (1.234,56) and standard format (1234.56).

Requirements: 14.1, 14.2, 14.6
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Union, Optional


class GermanNumberFormatter:
    """
    Core formatter for German number formatting.
    
    German format uses:
    - Dot (.) as thousand separator
    - Comma (,) as decimal separator
    - Exactly 2 decimal places for currency and percentages
    
    Examples:
        1234.56 -> "1.234,56"
        1234567.89 -> "1.234.567,89"
        0.5 -> "0,50"
    """
    
    # Constants
    THOUSAND_SEPARATOR = "."
    DECIMAL_SEPARATOR = ","
    DEFAULT_DECIMAL_PLACES = 2
    
    # Regex patterns for validation
    GERMAN_NUMBER_PATTERN = re.compile(
        r'^-?\d{1,3}(?:\.\d{3})*(?:,\d+)?$|^-?\d+(?:,\d+)?$'
    )
    
    def __init__(self, decimal_places: int = DEFAULT_DECIMAL_PLACES):
        """
        Initialize the German number formatter.
        
        Args:
            decimal_places: Number of decimal places to display (default: 2)
        """
        self.decimal_places = decimal_places
    
    def format(
        self, 
        number: Union[int, float, Decimal, str], 
        decimal_places: Optional[int] = None
    ) -> str:
        """
        Format a number to German format.
        
        Args:
            number: The number to format (int, float, Decimal, or string)
            decimal_places: Override default decimal places (optional)
            
        Returns:
            Formatted string in German format (e.g., "1.234,56")
            
        Raises:
            ValueError: If the input cannot be converted to a number
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.format(1234.56)
            '1.234,56'
            >>> formatter.format(1234567.89)
            '1.234.567,89'
            >>> formatter.format(0.5)
            '0,50'
        """
        if decimal_places is None:
            decimal_places = self.decimal_places
        
        try:
            # Convert to Decimal for precise handling
            if isinstance(number, str):
                # If it's already in German format, parse it first
                if self.DECIMAL_SEPARATOR in number:
                    number = self.parse(number)
                else:
                    number = Decimal(number)
            else:
                number = Decimal(str(number))
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Cannot convert '{number}' to a number: {e}")
        
        # Handle negative numbers
        is_negative = number < 0
        number = abs(number)
        
        # Round to specified decimal places
        quantizer = Decimal('0.1') ** decimal_places
        number = number.quantize(quantizer)
        
        # Split into integer and decimal parts
        number_str = str(number)
        if '.' in number_str:
            integer_part, decimal_part = number_str.split('.')
        else:
            integer_part = number_str
            decimal_part = '0' * decimal_places
        
        # Pad decimal part to required length
        decimal_part = decimal_part.ljust(decimal_places, '0')[:decimal_places]
        
        # Add thousand separators to integer part
        integer_part = self._add_thousand_separators(integer_part)
        
        # Combine parts
        if decimal_places > 0:
            result = f"{integer_part}{self.DECIMAL_SEPARATOR}{decimal_part}"
        else:
            result = integer_part
        
        # Add negative sign if needed
        if is_negative:
            result = f"-{result}"
        
        return result
    
    def parse(self, german_number: str) -> Decimal:
        """
        Parse a German-formatted number string to a Decimal.
        
        Args:
            german_number: German-formatted number string (e.g., "1.234,56")
            
        Returns:
            Decimal representation of the number
            
        Raises:
            ValueError: If the input is not a valid German number format
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.parse("1.234,56")
            Decimal('1234.56')
            >>> formatter.parse("1.234.567,89")
            Decimal('1234567.89')
            >>> formatter.parse("0,50")
            Decimal('0.50')
        """
        if not isinstance(german_number, str):
            raise ValueError(f"Input must be a string, got {type(german_number)}")
        
        # Remove whitespace
        german_number = german_number.strip()
        
        # Validate format
        if not self.validate(german_number):
            raise ValueError(
                f"Invalid German number format: '{german_number}'. "
                f"Expected format: 1.234,56"
            )
        
        # Handle negative numbers
        is_negative = german_number.startswith('-')
        if is_negative:
            german_number = german_number[1:]
        
        # Remove thousand separators
        standard_number = german_number.replace(self.THOUSAND_SEPARATOR, '')
        
        # Replace decimal separator with standard dot
        standard_number = standard_number.replace(self.DECIMAL_SEPARATOR, '.')
        
        try:
            result = Decimal(standard_number)
            if is_negative:
                result = -result
            return result
        except InvalidOperation as e:
            raise ValueError(f"Cannot parse '{german_number}': {e}")
    
    def format_currency(
        self, 
        amount: Union[int, float, Decimal, str],
        currency_symbol: str = "€",
        symbol_position: str = "suffix"
    ) -> str:
        """
        Format a number as currency in German format.
        
        Args:
            amount: The amount to format
            currency_symbol: Currency symbol (default: "€")
            symbol_position: "prefix" or "suffix" (default: "suffix")
            
        Returns:
            Formatted currency string (e.g., "1.234,56 €")
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.format_currency(1234.56)
            '1.234,56 €'
            >>> formatter.format_currency(1234.56, "$", "prefix")
            '$ 1.234,56'
        """
        formatted_number = self.format(amount, decimal_places=2)
        
        if symbol_position == "prefix":
            return f"{currency_symbol} {formatted_number}"
        else:
            return f"{formatted_number} {currency_symbol}"
    
    def format_percent(
        self, 
        value: Union[int, float, Decimal, str],
        multiply_by_100: bool = True
    ) -> str:
        """
        Format a number as percentage in German format.
        
        Args:
            value: The value to format (0.15 for 15% if multiply_by_100=True)
            multiply_by_100: Whether to multiply by 100 (default: True)
            
        Returns:
            Formatted percentage string (e.g., "15,00 %")
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.format_percent(0.15)
            '15,00 %'
            >>> formatter.format_percent(15, multiply_by_100=False)
            '15,00 %'
        """
        try:
            if isinstance(value, str):
                value = self.parse(value) if self.DECIMAL_SEPARATOR in value else Decimal(value)
            else:
                value = Decimal(str(value))
            
            if multiply_by_100:
                value = value * 100
            
            formatted_number = self.format(value, decimal_places=2)
            return f"{formatted_number} %"
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Cannot format '{value}' as percentage: {e}")
    
    def validate(self, german_number: str) -> bool:
        """
        Validate if a string is in valid German number format.
        
        Args:
            german_number: String to validate
            
        Returns:
            True if valid German number format, False otherwise
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.validate("1.234,56")
            True
            >>> formatter.validate("1,234.56")
            False
            >>> formatter.validate("1.234.567,89")
            True
        """
        if not isinstance(german_number, str):
            return False
        
        german_number = german_number.strip()
        
        # Empty string is not valid
        if not german_number:
            return False
        
        # Check against pattern
        return bool(self.GERMAN_NUMBER_PATTERN.match(german_number))
    
    def _add_thousand_separators(self, integer_str: str) -> str:
        """
        Add thousand separators to an integer string.
        
        Args:
            integer_str: Integer part as string
            
        Returns:
            String with thousand separators
            
        Examples:
            "1234567" -> "1.234.567"
        """
        # Reverse the string to process from right to left
        reversed_str = integer_str[::-1]
        
        # Add separator every 3 digits
        parts = []
        for i in range(0, len(reversed_str), 3):
            parts.append(reversed_str[i:i+3])
        
        # Join with separator and reverse back
        result = self.THOUSAND_SEPARATOR.join(parts)
        return result[::-1]
    
    def to_float(self, german_number: str) -> float:
        """
        Convert German-formatted number to float.
        
        Args:
            german_number: German-formatted number string
            
        Returns:
            Float representation
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.to_float("1.234,56")
            1234.56
        """
        return float(self.parse(german_number))
    
    def to_int(self, german_number: str) -> int:
        """
        Convert German-formatted number to integer.
        
        Args:
            german_number: German-formatted number string
            
        Returns:
            Integer representation (rounded)
            
        Examples:
            >>> formatter = GermanNumberFormatter()
            >>> formatter.to_int("1.234,56")
            1235
        """
        return int(round(self.parse(german_number)))


# Singleton instance for convenience
default_formatter = GermanNumberFormatter()


# Convenience functions
def format_german(
    number: Union[int, float, Decimal, str],
    decimal_places: int = 2
) -> str:
    """
    Convenience function to format a number in German format.
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places (default: 2)
        
    Returns:
        German-formatted string
    """
    return default_formatter.format(number, decimal_places)


def parse_german(german_number: str) -> Decimal:
    """
    Convenience function to parse a German-formatted number.
    
    Args:
        german_number: German-formatted number string
        
    Returns:
        Decimal representation
    """
    return default_formatter.parse(german_number)


def format_currency_german(
    amount: Union[int, float, Decimal, str],
    currency_symbol: str = "€"
) -> str:
    """
    Convenience function to format currency in German format.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol (default: "€")
        
    Returns:
        German-formatted currency string
    """
    return default_formatter.format_currency(amount, currency_symbol)


def format_percent_german(
    value: Union[int, float, Decimal, str],
    multiply_by_100: bool = True
) -> str:
    """
    Convenience function to format percentage in German format.
    
    Args:
        value: Value to format
        multiply_by_100: Whether to multiply by 100 (default: True)
        
    Returns:
        German-formatted percentage string
    """
    return default_formatter.format_percent(value, multiply_by_100)


def validate_german(german_number: str) -> bool:
    """
    Convenience function to validate German number format.
    
    Args:
        german_number: String to validate
        
    Returns:
        True if valid, False otherwise
    """
    return default_formatter.validate(german_number)
