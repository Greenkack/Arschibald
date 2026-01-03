"""
Universal Data Model

This module provides a comprehensive base class that combines dynamic key
generation, PDF byte generation, and German number formatting capabilities.
It serves as the foundation for all data models in the application.

Requirements: 14.4, 14.5, 14.10
"""

from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from decimal import Decimal
from abc import ABC

from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix
from backend.core.pdf_bytes import PDFByteMixin, PDFMetadata
from backend.core.german_formatter import GermanNumberFormatter


class UniversalDataModel(DynamicKeyMixin, PDFByteMixin, ABC):
    """
    Universal base class for all data models.

    This class combines:
    - Dynamic key generation (DynamicKeyMixin)
    - PDF byte generation (PDFByteMixin)
    - German number formatting
    - Locale-aware data retrieval
    - Data serialization

    All data models should inherit from this class to gain these capabilities.

    Example:
        >>> class SolarCalculation(UniversalDataModel):
        ...     def __init__(self, system_size: float, cost: float):
        ...         super().__init__()
        ...         self.system_size = system_size
        ...         self.cost = cost
        ...
        ...     def _get_default_title(self) -> str:
        ...         return "Solar Calculation Report"
        ...
        ...     def _render_to_pdf(self, story, doc):
        ...         # Render PDF content
        ...         pass
        ...
        >>> calc = SolarCalculation(10.5, 15000.0)
        >>> calc.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        >>> formatted_cost = calc.get_formatted_value('cost', locale='de-DE')
        >>> pdf_bytes = calc.to_pdf_bytes()
    """

    def __init__(self):
        """Initialize the universal data model"""
        DynamicKeyMixin.__init__(self)
        PDFByteMixin.__init__(self)

        # German formatter instance
        self._german_formatter = GermanNumberFormatter()

        # Data storage
        self._data: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}

        # Locale settings
        self._locale = 'de-DE'
        self._decimal_places = 2

    def set_locale(self, locale: str):
        """
        Set the locale for formatting.

        Args:
            locale: Locale string (e.g., 'de-DE', 'en-US')
        """
        self._locale = locale

    def get_locale(self) -> str:
        """
        Get the current locale.

        Returns:
            Current locale string
        """
        return self._locale

    def set_decimal_places(self, places: int):
        """
        Set the number of decimal places for formatting.

        Args:
            places: Number of decimal places
        """
        self._decimal_places = places
        self._german_formatter = GermanNumberFormatter(decimal_places=places)

    def get_formatted_value(
        self,
        key: str,
        locale: Optional[str] = None,
        format_type: Optional[str] = None
    ) -> str:
        """
        Get a formatted value based on locale.

        Args:
            key: Key of the value to retrieve
            locale: Locale to use (defaults to instance locale)
            format_type: Optional format type ('currency', 'percent', 'number')

        Returns:
            Formatted string value

        Examples:
            >>> model.get_formatted_value('cost', locale='de-DE')
            '15.000,00'
            >>> model.get_formatted_value('cost', format_type='currency')
            '15.000,00 €'
            >>> model.get_formatted_value('efficiency', format_type='percent')
            '95,50 %'
        """
        locale = locale or self._locale
        value = self._get_value(key)

        if value is None:
            return ""

        # Handle boolean values BEFORE numeric (bool is subclass of int)
        if isinstance(value, bool):
            return self._format_boolean_value(value, locale)

        # Handle numeric values
        if isinstance(value, (int, float, Decimal)):
            return self._format_numeric_value(
                value, locale, format_type
            )

        # Handle datetime values
        if isinstance(value, datetime):
            return self._format_datetime_value(value, locale)

        # Default: convert to string
        return str(value)

    def _get_value(self, key: str) -> Any:
        """
        Get a value by key from the model.

        Args:
            key: Key to retrieve

        Returns:
            Value associated with key
        """
        # Try to get from _data dict first
        if key in self._data:
            return self._data[key]

        # Try to get as attribute
        if hasattr(self, key):
            return getattr(self, key)

        return None

    def _format_numeric_value(
        self,
        value: Union[int, float, Decimal],
        locale: str,
        format_type: Optional[str]
    ) -> str:
        """
        Format a numeric value based on locale and type.

        Args:
            value: Numeric value to format
            locale: Locale string
            format_type: Format type ('currency', 'percent', 'number')

        Returns:
            Formatted string
        """
        if locale == 'de-DE':
            if format_type == 'currency':
                return self._german_formatter.format_currency(value)
            elif format_type == 'percent':
                return self._german_formatter.format_percent(
                    value, multiply_by_100=False
                )
            else:
                return self._german_formatter.format(value)
        else:
            # Default English format
            if format_type == 'currency':
                return f"${value:,.2f}"
            elif format_type == 'percent':
                return f"{value:.2f}%"
            else:
                return f"{value:,.2f}"

    def _format_datetime_value(
        self,
        value: datetime,
        locale: str
    ) -> str:
        """
        Format a datetime value based on locale.

        Args:
            value: Datetime value
            locale: Locale string

        Returns:
            Formatted datetime string
        """
        if locale == 'de-DE':
            return value.strftime("%d.%m.%Y %H:%M:%S")
        else:
            return value.strftime("%Y-%m-%d %H:%M:%S")

    def _format_boolean_value(
        self,
        value: bool,
        locale: str
    ) -> str:
        """
        Format a boolean value based on locale.

        Args:
            value: Boolean value
            locale: Locale string

        Returns:
            Formatted boolean string
        """
        if locale == 'de-DE':
            return "Ja" if value else "Nein"
        else:
            return "Yes" if value else "No"

    def get_all_formatted_values(
        self,
        locale: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get all values formatted according to locale.

        Args:
            locale: Locale to use (defaults to instance locale)

        Returns:
            Dictionary of formatted values
        """
        locale = locale or self._locale
        formatted = {}

        # Get all attributes
        for key in dir(self):
            if key.startswith('_'):
                continue
            if callable(getattr(self, key)):
                continue

            try:
                formatted[key] = self.get_formatted_value(key, locale)
            except Exception:
                # Skip attributes that can't be formatted
                continue

        # Add data dict values
        for key, value in self._data.items():
            if key not in formatted:
                formatted[key] = self.get_formatted_value(key, locale)

        return formatted

    def to_dict(
        self,
        include_keys: bool = True,
        include_metadata: bool = True,
        formatted: bool = False,
        locale: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Args:
            include_keys: Include dynamic key information
            include_metadata: Include metadata
            formatted: Return formatted values (German format for numbers)
            locale: Locale for formatting (if formatted=True)

        Returns:
            Dictionary representation of the model
        """
        result = {}

        # Get base attributes
        for key in dir(self):
            if key.startswith('_'):
                continue
            if callable(getattr(self, key)):
                continue

            try:
                value = getattr(self, key)
                if formatted:
                    result[key] = self.get_formatted_value(
                        key, locale or self._locale
                    )
                else:
                    result[key] = value
            except Exception:
                continue

        # Add data dict
        for key, value in self._data.items():
            if key not in result:
                if formatted:
                    result[key] = self.get_formatted_value(
                        key, locale or self._locale
                    )
                else:
                    result[key] = value

        # Add dynamic key information
        if include_keys:
            result['_dynamic_key'] = self.get_dynamic_key()
            result['_key_metadata'] = self.get_key_metadata()

        # Add metadata
        if include_metadata:
            result['_metadata'] = self._metadata

        return result

    def to_json_serializable(self) -> Dict[str, Any]:
        """
        Convert model to JSON-serializable dictionary.

        Returns:
            JSON-serializable dictionary
        """
        data = self.to_dict(formatted=False)

        # Convert non-serializable types
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, bytes):
                data[key] = value.decode('utf-8', errors='ignore')

        return data

    def set_data(self, key: str, value: Any):
        """
        Set a data value.

        Args:
            key: Data key
            value: Data value
        """
        self._data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get a data value.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        return self._data.get(key, default)

    def set_metadata(self, key: str, value: Any):
        """
        Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self._metadata.get(key, default)

    def format_all_numbers_german(self) -> Dict[str, str]:
        """
        Get all numeric values formatted in German format.

        Returns:
            Dictionary with German-formatted numbers
        """
        result = {}

        for key in dir(self):
            if key.startswith('_'):
                continue
            if callable(getattr(self, key)):
                continue

            try:
                value = getattr(self, key)
                if isinstance(value, (int, float, Decimal)):
                    result[key] = self._german_formatter.format(value)
            except Exception:
                continue

        # Add data dict numeric values
        for key, value in self._data.items():
            if isinstance(value, (int, float, Decimal)):
                result[key] = self._german_formatter.format(value)

        return result

    def __repr__(self) -> str:
        """String representation of the model"""
        key = self.get_dynamic_key() or "no-key"
        return f"<{self.__class__.__name__} key={key}>"

    def __str__(self) -> str:
        """String representation of the model"""
        return self.__repr__()


class SimpleDataModel(UniversalDataModel):
    """
    Simple implementation of UniversalDataModel for testing and basic use.

    Example:
        >>> model = SimpleDataModel(
        ...     title="Test Data",
        ...     value=1234.56,
        ...     description="Test description"
        ... )
        >>> model.generate_dynamic_key(KeyPrefix.DATA)
        >>> formatted = model.get_formatted_value('value', locale='de-DE')
        >>> print(formatted)  # "1.234,56"
    """

    def __init__(self, title: str = "Data", **kwargs):
        """
        Initialize simple data model.

        Args:
            title: Title for the model
            **kwargs: Additional data to store
        """
        super().__init__()
        self.title = title

        # Store all kwargs in data dict
        for key, value in kwargs.items():
            self._data[key] = value

    def _get_default_title(self) -> str:
        """Get default PDF title"""
        return self.title

    def _render_to_pdf(self, story: List, doc):
        """Render simple data to PDF"""
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, Spacer, Table

            styles = getSampleStyleSheet()

            # Add title
            story.append(Paragraph(self.title, styles['Heading1']))
            story.append(Spacer(1, 12))

            # Add data as table
            table_data = [['Key', 'Value']]
            for key, value in self._data.items():
                formatted_value = self.get_formatted_value(
                    key, locale='de-DE'
                )
                table_data.append([str(key), formatted_value])

            if len(table_data) > 1:
                table = self._pdf_engine.create_table(table_data)
                story.append(table)

        except ImportError:
            # reportlab not available
            pass


# Utility functions

def create_universal_model(
    data: Dict[str, Any],
    title: str = "Data Model",
    key_prefix: KeyPrefix = KeyPrefix.DATA
) -> SimpleDataModel:
    """
    Create a universal data model from a dictionary.

    Args:
        data: Dictionary of data
        title: Title for the model
        key_prefix: Key prefix to use

    Returns:
        SimpleDataModel instance

    Example:
        >>> data = {'cost': 15000.0, 'size': 10.5}
        >>> model = create_universal_model(
        ...     data, title="Solar System", key_prefix=KeyPrefix.SOLAR_CALCULATION
        ... )
        >>> model.generate_dynamic_key(key_prefix)
        >>> formatted = model.get_formatted_value('cost', locale='de-DE')
    """
    model = SimpleDataModel(title=title, **data)
    model.generate_dynamic_key(key_prefix)
    return model


def format_dict_german(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format all numeric values in a dictionary to German format.

    Args:
        data: Dictionary with numeric values

    Returns:
        Dictionary with German-formatted values

    Example:
        >>> data = {'cost': 15000.0, 'size': 10.5, 'name': 'Solar System'}
        >>> formatted = format_dict_german(data)
        >>> print(formatted['cost'])  # "15.000,00"
    """
    formatter = GermanNumberFormatter()
    result = {}

    for key, value in data.items():
        # Skip booleans (they are subclass of int)
        if isinstance(value, bool):
            result[key] = str(value)
        elif isinstance(value, (int, float, Decimal)):
            result[key] = formatter.format(value)
        else:
            result[key] = str(value)

    return result
