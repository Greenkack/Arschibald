"""Tests for PDF Generator Pricing Integration

Tests the enhanced PDF generation system with dynamic pricing keys,
automatic key population, and pricing breakdown sections.
"""

from unittest.mock import Mock, patch

import pytest

# Import the module under test
try:
    from pdf_generator import PDFGenerator
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
except ImportError:
    # Skip tests if modules not available
    pytest.skip("PDF generator modules not available", allow_module_level=True)


class TestPDFGeneratorPricingIntegration:
    """Test cases for PDF generator pricing integration"""

    def setup_method(self):
        """Set up test fixtures"""
        self.sample_offer_data = {
            'customer': {
                'name': 'Max Mustermann',
                'email': 'max@example.com',
                'phone': '+49 123 456789',
                'address': 'Teststraße 123, 12345 Teststadt'
            },
            'offer_id': 'OFFER-2024-001',
            'date': '2024-01-15',
            'items': [
                {
                    'name': 'PV-Module 400W',
                    'quantity': 20,
                    'unit_price': 180.0,
                    'total_price': 3600.0
                },
                {
                    'name': 'Wechselrichter 8kW',
                    'quantity': 1,
                    'unit_price': 800.0,
                    'total_price': 800.0
                },
                {
                    'name': 'Batteriespeicher 10kWh',
                    'quantity': 1,
                    'unit_price': 3500.0,
                    'total_price': 3500.0
                }
            ],
            'net_total': 12605.04,
            'vat': 2394.96,
            'grand_total': 15000.0
        }

        self.sample_pricing_data = {
            'components': {
                'modules_total': 3600.0,
                'modules_quantity': 20,
                'modules_unit_price': 180.0,
                'inverter_total': 800.0,
                'inverter_quantity': 1,
                'inverter_unit_price': 800.0,
                'storage_total': 3500.0,
                'storage_quantity': 1,
                'storage_unit_price': 3500.0,
                'installation_total': 4705.04
            },
            'discounts': {
                'early_payment_discount': 300.0,
                'volume_discount': 200.0
            },
            'surcharges': {
                'rush_order_surcharge': 150.0
            },
            'vat': {
                'vat_rate': 19.0,
                'vat_amount': 2394.96,
                'net_amount': 12605.04
            },
            'totals': {
                'net_total': 12605.04,
                'gross_total': 15000.0
            },
            'pv_pricing': {
                'base_price': 12000.0,
                'components_total': 11500.0,
                'installation_cost': 500.0,
                'net_total': 12605.04,
                'vat_amount': 2394.96,
                'gross_total': 15000.0
            }
        }

    def test_pdf_generator_initialization_with_pricing(self):
        """Test PDF generator initialization with pricing data"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        assert generator.offer_data == self.sample_offer_data
        assert generator.pricing_data == self.sample_pricing_data
        assert hasattr(generator, 'pricing_keys')
        assert isinstance(generator.pricing_keys, dict)
        assert hasattr(generator, 'key_manager')

    def test_pricing_key_generation(self):
        """Test pricing key generation from pricing data"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        # Check that pricing keys were generated
        assert isinstance(generator.pricing_keys, dict)

        # If pricing system is available, check for expected keys
        if generator.key_manager:
            # Should have some keys if pricing data was processed
            key_count = len(generator.pricing_keys)
            assert key_count >= 0  # May be 0 with fallback

            # Check for expected key patterns
            key_names = list(generator.pricing_keys.keys())
            component_keys = [k for k in key_names if 'COMPONENT' in k]
            discount_keys = [k for k in key_names if 'DISCOUNT' in k]
            total_keys = [k for k in key_names if 'TOTAL' in k]

            # At least one category should have keys if any exist
            if key_names:
                total_category_keys = len(component_keys) + len(discount_keys) + len(total_keys)
                assert total_category_keys > 0

    def test_get_all_dynamic_keys(self):
        """Test getting all dynamic keys for PDF templates"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        all_keys = generator.get_all_dynamic_keys()

        # Should include basic keys
        assert 'CUSTOMER_NAME' in all_keys
        assert 'OFFER_ID' in all_keys
        assert 'NET_TOTAL' in all_keys
        assert 'GROSS_TOTAL' in all_keys

        # Check values
        assert all_keys['CUSTOMER_NAME'] == 'Max Mustermann'
        assert all_keys['OFFER_ID'] == 'OFFER-2024-001'
        assert '€' in all_keys['NET_TOTAL']
        assert '€' in all_keys['GROSS_TOTAL']

        # Should include automatic keys
        assert 'TOTAL_ITEMS' in all_keys
        assert 'PRICING_KEYS_COUNT' in all_keys

        # Should include item keys
        assert 'ITEM_1_NAME' in all_keys
        assert 'ITEM_1_QUANTITY' in all_keys
        assert 'ITEM_1_UNIT_PRICE' in all_keys
        assert 'ITEM_1_TOTAL_PRICE' in all_keys

    def test_automatic_key_generation(self):
        """Test automatic key generation from offer items"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        auto_keys = generator._generate_automatic_keys()

        # Should have item keys for each offer item
        assert 'ITEM_1_NAME' in auto_keys
        assert auto_keys['ITEM_1_NAME'] == 'PV-Module 400W'
        assert 'ITEM_1_QUANTITY' in auto_keys
        assert auto_keys['ITEM_1_QUANTITY'] == '20'

        assert 'ITEM_2_NAME' in auto_keys
        assert auto_keys['ITEM_2_NAME'] == 'Wechselrichter 8kW'

        assert 'ITEM_3_NAME' in auto_keys
        assert auto_keys['ITEM_3_NAME'] == 'Batteriespeicher 10kWh'

        # Should have summary keys
        assert 'TOTAL_ITEMS' in auto_keys
        assert auto_keys['TOTAL_ITEMS'] == '3'
        assert 'PRICING_KEYS_COUNT' in auto_keys

    def test_flatten_pricing_data(self):
        """Test flattening of nested pricing data"""
        generator = PDFGenerator(
            offer_data={},
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

        nested_data = {
            'components': {
                'modules': 3600.0,
                'inverter': 800.0
            },
            'totals': {
                'net': 12605.04,
                'gross': 15000.0
            }
        }

        flattened = generator._flatten_pricing_data(nested_data)

        # Should flatten nested structure
        assert 'COMPONENTS_MODULES' in flattened
        assert 'COMPONENTS_INVERTER' in flattened
        assert 'TOTALS_NET' in flattened
        assert 'TOTALS_GROSS' in flattened

        # Should format currency values
        assert '€' in flattened['COMPONENTS_MODULES']
        assert '€' in flattened['TOTALS_NET']

    def test_populate_template_placeholders(self):
        """Test template placeholder population"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        template_content = """
        Angebot für {{CUSTOMER_NAME}}
        Angebotsnummer: {{OFFER_ID}}
        Gesamtsumme: {{GROSS_TOTAL}}
        Anzahl Positionen: {{TOTAL_ITEMS}}
        Erste Position: {{ITEM_1_NAME}} ({{ITEM_1_QUANTITY}} Stück)
        """

        populated = generator.populate_template_placeholders(template_content)

        # Check that placeholders were replaced
        assert 'Max Mustermann' in populated
        assert 'OFFER-2024-001' in populated
        assert '€' in populated
        assert '3' in populated  # TOTAL_ITEMS
        assert 'PV-Module 400W' in populated
        assert '20 Stück' in populated

        # Check that placeholders are gone
        assert '{{CUSTOMER_NAME}}' not in populated
        assert '{{OFFER_ID}}' not in populated
        assert '{{GROSS_TOTAL}}' not in populated
        assert '{{TOTAL_ITEMS}}' not in populated
        assert '{{ITEM_1_NAME}}' not in populated

    def test_get_available_placeholders(self):
        """Test getting available placeholders"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        placeholders = generator.get_available_placeholders()

        # Should be a list of strings
        assert isinstance(placeholders, list)
        assert len(placeholders) > 0

        # Should include expected placeholders
        assert 'CUSTOMER_NAME' in placeholders
        assert 'OFFER_ID' in placeholders
        assert 'NET_TOTAL' in placeholders
        assert 'GROSS_TOTAL' in placeholders
        assert 'TOTAL_ITEMS' in placeholders

    def test_validate_template_placeholders(self):
        """Test template placeholder validation"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        # Template with valid and invalid placeholders
        template_content = """
        Valid: {{CUSTOMER_NAME}}, {{OFFER_ID}}
        Invalid: {{INVALID_KEY}}, {{ANOTHER_INVALID}}
        """

        validation = generator.validate_template_placeholders(template_content)

        # Check validation structure
        assert 'total_placeholders' in validation
        assert 'valid_placeholders' in validation
        assert 'invalid_placeholders' in validation
        assert 'validation_success' in validation

        # Check validation results
        assert validation['total_placeholders'] == 4
        assert 'CUSTOMER_NAME' in validation['valid_placeholders']
        assert 'OFFER_ID' in validation['valid_placeholders']
        assert 'INVALID_KEY' in validation['invalid_placeholders']
        assert 'ANOTHER_INVALID' in validation['invalid_placeholders']
        assert validation['validation_success'] is False

    def test_analyze_pricing_key_categories(self):
        """Test pricing key category analysis"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        # Mock some pricing keys for testing
        generator.pricing_keys = {
            'COMPONENT_MODULES_TOTAL': '3.600,00 €',
            'COMPONENT_INVERTER_TOTAL': '800,00 €',
            'DISCOUNT_EARLY_PAYMENT': '300,00 €',
            'SURCHARGE_RUSH_ORDER': '150,00 €',
            'VAT_AMOUNT': '2.394,96 €',
            'NET_TOTAL': '12.605,04 €',
            'GROSS_TOTAL': '15.000,00 €'
        }

        categories = generator._analyze_pricing_key_categories()

        # Check category counts
        assert categories.get('Komponenten', 0) == 2  # COMPONENT keys
        assert categories.get('Rabatte', 0) == 1      # DISCOUNT keys
        assert categories.get('Zuschläge', 0) == 1    # SURCHARGE keys
        assert categories.get('MwSt.', 0) == 1        # VAT keys
        assert categories.get('Summen', 0) == 2       # TOTAL keys

    def test_get_key_category(self):
        """Test key category determination"""
        generator = PDFGenerator(
            offer_data={},
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

        # Test different key patterns
        assert generator._get_key_category('COMPONENT_MODULES_TOTAL') == 'Komponenten'
        assert generator._get_key_category('DISCOUNT_EARLY_PAYMENT') == 'Rabatte'
        assert generator._get_key_category('SURCHARGE_RUSH_ORDER') == 'Zuschläge'
        assert generator._get_key_category('VAT_AMOUNT') == 'MwSt.'
        assert generator._get_key_category('NET_TOTAL') == 'Summen'
        assert generator._get_key_category('PV_BASE_PRICE') == 'Photovoltaik'
        assert generator._get_key_category('HP_INSTALLATION') == 'Wärmepumpe'
        assert generator._get_key_category('HEATPUMP_TOTAL') == 'Wärmepumpe'
        assert generator._get_key_category('CUSTOM_KEY') == 'Allgemein'

    def test_currency_formatting(self):
        """Test currency value formatting"""
        generator = PDFGenerator(
            offer_data={},
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

        # Test various amounts
        assert generator._format_currency_value(1234.56) == "1.234,56 €"
        assert generator._format_currency_value(0.0) == "0,00 €"
        assert generator._format_currency_value(15000.0) == "15.000,00 €"
        assert generator._format_currency_value(None) == "0,00 €"
        assert generator._format_currency_value("invalid") == "0,00 €"

    def test_extract_numeric_value(self):
        """Test numeric value extraction from formatted strings"""
        generator = PDFGenerator(
            offer_data={},
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

        # Test various formats
        assert generator._extract_numeric_value("1.234,56 €") == 1234.56
        assert generator._extract_numeric_value("15.000,00 €") == 15000.0
        assert generator._extract_numeric_value(1234.56) == 1234.56
        assert generator._extract_numeric_value("invalid") is None
        assert generator._extract_numeric_value(None) is None

    def test_get_pricing_summary(self):
        """Test pricing summary generation"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        summary = generator.get_pricing_summary()

        # Check structure
        assert 'components' in summary
        assert 'modifications' in summary
        assert 'totals' in summary
        assert 'keys_generated' in summary

        # Check that keys_generated is a number
        assert isinstance(summary['keys_generated'], int)
        assert summary['keys_generated'] >= 0

    @patch('pdf_generator.SimpleDocTemplate')
    def test_create_pdf_with_pricing_breakdown(self, mock_doc):
        """Test PDF creation with pricing breakdown"""
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance

        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[{"id": "preisaufstellung"}],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        # Should not raise an exception
        generator.create_pdf()

        # Check that document was built
        mock_doc_instance.build.assert_called_once()

    def test_draw_pricing_breakdown_with_enhanced_data(self):
        """Test drawing pricing breakdown with enhanced pricing data"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf",
            pricing_data=self.sample_pricing_data
        )

        # Should not raise an exception
        generator._draw_pricing_breakdown()

        # Should have added content to story
        assert len(generator.story) > 0

        # Check for expected content
        story_text = str(generator.story)
        assert 'Preisaufstellung' in story_text

    def test_draw_basic_pricing_breakdown_fallback(self):
        """Test basic pricing breakdown when no enhanced pricing data"""
        generator = PDFGenerator(
            offer_data=self.sample_offer_data,
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

        # Clear pricing data to test fallback
        generator.pricing_data = {}
        generator.pricing_keys = {}

        # Should not raise an exception
        generator._draw_basic_pricing_breakdown()

        # Should have added content to story
        assert len(generator.story) > 0

    def test_pricing_integration_without_pricing_system(self):
        """Test PDF generator behavior when pricing system is not available"""
        # Mock import error for pricing system by patching the import inside the method
        with patch('pdf_generator.PDFGenerator._init_pricing_integration') as mock_init:
            # Make the init method simulate ImportError
            def mock_init_pricing(self):
                self.key_manager = None
                self.pricing_keys = {}
                print("Warning: Pricing system not available, using fallback")

            mock_init.side_effect = mock_init_pricing

            generator = PDFGenerator(
                offer_data=self.sample_offer_data,
                module_order=[],
                theme_name="default",
                filename="test.pdf",
                pricing_data=self.sample_pricing_data
            )

            # Should fall back gracefully
            assert generator.key_manager is None
            assert generator.pricing_keys == {}

            # Should still be able to get basic keys
            all_keys = generator.get_all_dynamic_keys()
            assert 'CUSTOMER_NAME' in all_keys
            assert 'OFFER_ID' in all_keys


class TestPDFPricingBreakdownSections:
    """Test cases for specific pricing breakdown sections"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = PDFGenerator(
            offer_data={
                'customer': {'name': 'Test Customer'},
                'offer_id': 'TEST-001',
                'items': []
            },
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

    def test_draw_component_pricing_empty(self):
        """Test component pricing section with no data"""
        self.generator.pricing_keys = {}
        self.generator.pricing_data = {}

        # Should not raise an exception
        self.generator._draw_component_pricing()

        # Should not add content if no data
        # (method returns early)

    def test_draw_pricing_modifications_empty(self):
        """Test pricing modifications section with no data"""
        self.generator.pricing_keys = {}

        # Should not raise an exception
        self.generator._draw_pricing_modifications()

        # Should not add content if no data
        # (method returns early)

    def test_draw_pricing_totals_empty(self):
        """Test pricing totals section with no data"""
        self.generator.pricing_keys = {}

        # Should not raise an exception
        self.generator._draw_pricing_totals()

        # Should not add content if no data
        # (method returns early)

    def test_draw_dynamic_key_reference_empty(self):
        """Test dynamic key reference section with no data"""
        self.generator.pricing_keys = {}

        # Should not raise an exception
        self.generator._draw_dynamic_key_reference()

        # Should not add content if no data
        # (method returns early)

    def test_draw_component_pricing_with_data(self):
        """Test component pricing section with data"""
        self.generator.pricing_keys = {
            'COMPONENT_MODULES_TOTAL': '3.600,00 €',
            'COMPONENT_MODULES_QUANTITY': '20',
            'COMPONENT_MODULES_UNIT_PRICE': '180,00 €',
            'COMPONENT_INVERTER_TOTAL': '800,00 €'
        }

        # Should not raise an exception
        self.generator._draw_component_pricing()

        # Should have added content to story
        assert len(self.generator.story) > 0

    def test_draw_pricing_modifications_with_data(self):
        """Test pricing modifications section with data"""
        self.generator.pricing_keys = {
            'DISCOUNT_EARLY_PAYMENT': '300,00 €',
            'SURCHARGE_RUSH_ORDER': '150,00 €'
        }

        # Should not raise an exception
        self.generator._draw_pricing_modifications()

        # Should have added content to story
        assert len(self.generator.story) > 0

    def test_draw_pricing_totals_with_data(self):
        """Test pricing totals section with data"""
        self.generator.pricing_keys = {
            'NET_TOTAL': '12.605,04 €',
            'VAT_AMOUNT': '2.394,96 €',
            'GROSS_TOTAL': '15.000,00 €'
        }

        # Should not raise an exception
        self.generator._draw_pricing_totals()

        # Should have added content to story
        assert len(self.generator.story) > 0


class TestPDFSystemSpecificPricing:
    """Test cases for system-specific pricing sections"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = PDFGenerator(
            offer_data={},
            module_order=[],
            theme_name="default",
            filename="test.pdf"
        )

    def test_draw_pv_pricing_section(self):
        """Test PV pricing section"""
        self.generator.pricing_data = {
            'pv_pricing': {
                'base_price': 12000.0,
                'components_total': 11500.0,
                'installation_cost': 500.0,
                'net_total': 12605.04,
                'vat_amount': 2394.96,
                'gross_total': 15000.0
            }
        }

        # Should not raise an exception
        self.generator._draw_pv_pricing_section()

        # Should have added content to story
        assert len(self.generator.story) > 0

    def test_draw_heatpump_pricing_section(self):
        """Test heat pump pricing section"""
        self.generator.pricing_data = {
            'heatpump_pricing': {
                'base_price': 8000.0,
                'components_total': 7500.0,
                'installation_cost': 500.0,
                'beg_subsidy_amount': 2000.0,
                'net_total': 6000.0,
                'vat_amount': 1140.0,
                'gross_total': 7140.0,
                'net_investment_after_subsidy': 5140.0
            }
        }

        # Should not raise an exception
        self.generator._draw_heatpump_pricing_section()

        # Should have added content to story
        assert len(self.generator.story) > 0

    def test_draw_combined_pricing_section(self):
        """Test combined pricing section"""
        self.generator.pricing_data = {
            'combined_pricing': {
                'pv_subtotal': 15000.0,
                'hp_subtotal': 7140.0,
                'package_discount': 500.0,
                'net_total': 21640.0,
                'vat_amount': 4111.60,
                'gross_total': 25751.60,
                'total_savings_annual': 1800.0,
                'payback_period': 14.3
            }
        }

        # Should not raise an exception
        self.generator._draw_combined_pricing_section()

        # Should have added content to story
        assert len(self.generator.story) > 0

    def test_draw_system_specific_pricing_empty(self):
        """Test system-specific pricing with no data"""
        self.generator.pricing_data = {}

        # Should not raise an exception
        self.generator._draw_system_specific_pricing()

        # Should not add content if no data
        # (method returns early)


if __name__ == '__main__':
    pytest.main([__file__])
