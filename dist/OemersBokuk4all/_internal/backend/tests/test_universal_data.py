"""
Tests for Universal Data Model

This module tests the UniversalDataModel class and its integration
of dynamic keys, PDF bytes, and German formatting.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from backend.core.universal_data import (
    UniversalDataModel,
    SimpleDataModel,
    create_universal_model,
    format_dict_german
)
from backend.core.dynamic_keys import KeyPrefix


class TestUniversalDataModel:
    """Test suite for UniversalDataModel"""

    def test_initialization(self):
        """Test model initialization"""
        model = SimpleDataModel(title="Test")
        assert model.title == "Test"
        assert model.get_locale() == 'de-DE'
        assert model._decimal_places == 2

    def test_set_locale(self):
        """Test setting locale"""
        model = SimpleDataModel(title="Test")
        model.set_locale('en-US')
        assert model.get_locale() == 'en-US'

    def test_set_decimal_places(self):
        """Test setting decimal places"""
        model = SimpleDataModel(title="Test")
        model.set_decimal_places(3)
        assert model._decimal_places == 3

    def test_dynamic_key_generation(self):
        """Test dynamic key generation"""
        model = SimpleDataModel(title="Test")
        key = model.generate_dynamic_key(KeyPrefix.DATA)

        assert key is not None
        assert key.startswith('DAT_')
        assert model.get_dynamic_key() == key

    def test_formatted_value_german_number(self):
        """Test German number formatting"""
        model = SimpleDataModel(title="Test", cost=1234.56)

        formatted = model.get_formatted_value('cost', locale='de-DE')
        assert formatted == '1.234,56'

    def test_formatted_value_german_currency(self):
        """Test German currency formatting"""
        model = SimpleDataModel(title="Test", price=15000.0)

        formatted = model.get_formatted_value(
            'price', locale='de-DE', format_type='currency'
        )
        assert formatted == '15.000,00 €'

    def test_formatted_value_german_percent(self):
        """Test German percent formatting"""
        model = SimpleDataModel(title="Test", efficiency=95.5)

        formatted = model.get_formatted_value(
            'efficiency', locale='de-DE', format_type='percent'
        )
        assert formatted == '95,50 %'

    def test_formatted_value_english_number(self):
        """Test English number formatting"""
        model = SimpleDataModel(title="Test", cost=1234.56)

        formatted = model.get_formatted_value('cost', locale='en-US')
        assert formatted == '1,234.56'

    def test_formatted_value_datetime(self):
        """Test datetime formatting"""
        dt = datetime(2023, 11, 16, 14, 30, 0)
        model = SimpleDataModel(title="Test", created=dt)

        formatted_de = model.get_formatted_value('created', locale='de-DE')
        assert formatted_de == '16.11.2023 14:30:00'

        formatted_en = model.get_formatted_value('created', locale='en-US')
        assert formatted_en == '2023-11-16 14:30:00'

    def test_formatted_value_boolean(self):
        """Test boolean formatting"""
        model = SimpleDataModel(title="Test", active=True, inactive=False)

        assert model.get_formatted_value('active', locale='de-DE') == 'Ja'
        assert model.get_formatted_value('inactive', locale='de-DE') == 'Nein'
        assert model.get_formatted_value('active', locale='en-US') == 'Yes'
        assert model.get_formatted_value('inactive', locale='en-US') == 'No'

    def test_get_all_formatted_values(self):
        """Test getting all formatted values"""
        model = SimpleDataModel(
            title="Test",
            cost=1234.56,
            size=10.5,
            name="Solar System"
        )

        formatted = model.get_all_formatted_values(locale='de-DE')

        assert 'cost' in formatted
        assert formatted['cost'] == '1.234,56'
        assert 'size' in formatted
        assert formatted['size'] == '10,50'

    def test_to_dict_basic(self):
        """Test basic dictionary conversion"""
        model = SimpleDataModel(
            title="Test",
            cost=1234.56,
            size=10.5
        )
        model.generate_dynamic_key(KeyPrefix.DATA)

        data = model.to_dict(include_keys=True, include_metadata=True)

        assert 'title' in data
        assert data['title'] == "Test"
        assert 'cost' in data
        assert data['cost'] == 1234.56
        assert '_dynamic_key' in data
        assert '_key_metadata' in data

    def test_to_dict_formatted(self):
        """Test formatted dictionary conversion"""
        model = SimpleDataModel(
            title="Test",
            cost=1234.56,
            size=10.5
        )

        data = model.to_dict(formatted=True, locale='de-DE')

        assert data['cost'] == '1.234,56'
        assert data['size'] == '10,50'

    def test_to_json_serializable(self):
        """Test JSON serialization"""
        dt = datetime(2023, 11, 16, 14, 30, 0)
        model = SimpleDataModel(
            title="Test",
            cost=Decimal('1234.56'),
            created=dt
        )

        data = model.to_json_serializable()

        assert isinstance(data['cost'], float)
        assert data['cost'] == 1234.56
        assert isinstance(data['created'], str)
        assert '2023-11-16' in data['created']

    def test_set_and_get_data(self):
        """Test setting and getting data"""
        model = SimpleDataModel(title="Test")

        model.set_data('custom_field', 'custom_value')
        assert model.get_data('custom_field') == 'custom_value'
        assert model.get_data('nonexistent', 'default') == 'default'

    def test_set_and_get_metadata(self):
        """Test setting and getting metadata"""
        model = SimpleDataModel(title="Test")

        model.set_metadata('version', '1.0')
        assert model.get_metadata('version') == '1.0'
        assert model.get_metadata('nonexistent', 'default') == 'default'

    def test_format_all_numbers_german(self):
        """Test formatting all numbers in German format"""
        model = SimpleDataModel(
            title="Test",
            cost=1234.56,
            size=10.5,
            count=42,
            name="Solar System"
        )

        formatted = model.format_all_numbers_german()

        assert 'cost' in formatted
        assert formatted['cost'] == '1.234,56'
        assert 'size' in formatted
        assert formatted['size'] == '10,50'
        assert 'count' in formatted
        assert formatted['count'] == '42,00'
        assert 'name' not in formatted  # Non-numeric values excluded

    def test_pdf_bytes_generation(self):
        """Test PDF bytes generation"""
        model = SimpleDataModel(
            title="Test Report",
            cost=1234.56,
            size=10.5
        )

        try:
            pdf_bytes = model.to_pdf_bytes()
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0
            assert pdf_bytes.startswith(b'%PDF')
        except ImportError:
            pytest.skip("reportlab not installed")

    def test_pdf_base64_generation(self):
        """Test PDF base64 generation"""
        model = SimpleDataModel(
            title="Test Report",
            cost=1234.56
        )

        try:
            pdf_base64 = model.to_pdf_base64()
            assert isinstance(pdf_base64, str)
            assert len(pdf_base64) > 0
        except ImportError:
            pytest.skip("reportlab not installed")

    def test_repr_and_str(self):
        """Test string representations"""
        model = SimpleDataModel(title="Test")
        model.generate_dynamic_key(KeyPrefix.DATA)

        repr_str = repr(model)
        assert 'SimpleDataModel' in repr_str
        assert 'DAT_' in repr_str

        str_str = str(model)
        assert str_str == repr_str


class TestCreateUniversalModel:
    """Test suite for create_universal_model utility"""

    def test_create_from_dict(self):
        """Test creating model from dictionary"""
        data = {
            'cost': 15000.0,
            'size': 10.5,
            'name': 'Solar System'
        }

        model = create_universal_model(
            data,
            title="Solar Calculation",
            key_prefix=KeyPrefix.SOLAR_CALCULATION
        )

        assert model.title == "Solar Calculation"
        assert model.get_data('cost') == 15000.0
        assert model.get_data('size') == 10.5
        assert model.get_data('name') == 'Solar System'
        assert model.get_dynamic_key().startswith('SOL_')

    def test_formatted_values_from_created_model(self):
        """Test formatted values from created model"""
        data = {'cost': 15000.0, 'size': 10.5}

        model = create_universal_model(data, title="Test")

        formatted_cost = model.get_formatted_value('cost', locale='de-DE')
        assert formatted_cost == '15.000,00'


class TestFormatDictGerman:
    """Test suite for format_dict_german utility"""

    def test_format_numeric_values(self):
        """Test formatting numeric values"""
        data = {
            'cost': 15000.0,
            'size': 10.5,
            'count': 42
        }

        formatted = format_dict_german(data)

        assert formatted['cost'] == '15.000,00'
        assert formatted['size'] == '10,50'
        assert formatted['count'] == '42,00'

    def test_format_mixed_values(self):
        """Test formatting mixed value types"""
        data = {
            'cost': 15000.0,
            'name': 'Solar System',
            'active': True
        }

        formatted = format_dict_german(data)

        assert formatted['cost'] == '15.000,00'
        assert formatted['name'] == 'Solar System'
        assert formatted['active'] == 'True'

    def test_format_decimal_values(self):
        """Test formatting Decimal values"""
        data = {
            'price': Decimal('1234.56'),
            'tax': Decimal('234.56')
        }

        formatted = format_dict_german(data)

        assert formatted['price'] == '1.234,56'
        assert formatted['tax'] == '234,56'


class TestIntegration:
    """Integration tests for UniversalDataModel"""

    def test_complete_workflow(self):
        """Test complete workflow with all features"""
        # Create model
        model = SimpleDataModel(
            title="Solar System Calculation",
            system_size=10.5,
            cost=15000.0,
            efficiency=95.5,
            annual_production=12000.0
        )

        # Generate dynamic key
        key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        assert key.startswith('SOL_')

        # Get formatted values
        formatted_cost = model.get_formatted_value(
            'cost', locale='de-DE', format_type='currency'
        )
        assert formatted_cost == '15.000,00 €'

        formatted_efficiency = model.get_formatted_value(
            'efficiency', locale='de-DE', format_type='percent'
        )
        assert formatted_efficiency == '95,50 %'

        # Get all formatted values
        all_formatted = model.get_all_formatted_values(locale='de-DE')
        assert 'system_size' in all_formatted
        assert all_formatted['system_size'] == '10,50'

        # Convert to dict
        data_dict = model.to_dict(formatted=True, locale='de-DE')
        assert data_dict['cost'] == '15.000,00'

        # Generate PDF
        try:
            pdf_bytes = model.to_pdf_bytes()
            assert len(pdf_bytes) > 0
        except ImportError:
            pytest.skip("reportlab not installed")

    def test_multiple_models_with_keys(self):
        """Test multiple models with unique keys"""
        models = []

        for i in range(5):
            model = SimpleDataModel(
                title=f"Model {i}",
                value=1000.0 * (i + 1)
            )
            model.generate_dynamic_key(KeyPrefix.DATA)
            models.append(model)

        # Verify all keys are unique
        keys = [m.get_dynamic_key() for m in models]
        assert len(keys) == len(set(keys))

        # Verify all keys start with correct prefix
        assert all(k.startswith('DAT_') for k in keys)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
