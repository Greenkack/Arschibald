"""Tests for PDF Pricing Templates

Tests the specialized PDF templates for PV systems, heat pump systems,
and combined offers with dynamic pricing placeholders.
"""


import pytest

# Import the module under test
try:
    from pdf_pricing_templates import (
        CombinedPricingTemplate,
        HeatPumpPricingTemplate,
        PricingTemplateConfig,
        PricingTemplateManager,
        PVPricingTemplate,
        create_combined_pricing_template,
        create_heatpump_pricing_template,
        create_pv_pricing_template,
        get_template_manager,
    )
except ImportError:
    # Skip tests if modules not available
    pytest.skip("PDF pricing templates modules not available", allow_module_level=True)


class TestPricingTemplateConfig:
    """Test cases for PricingTemplateConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = PricingTemplateConfig(system_type='pv')

        assert config.system_type == 'pv'
        assert config.include_components is True
        assert config.include_modifications is True
        assert config.include_vat_breakdown is True
        assert config.include_summary is True
        assert config.currency_symbol == "€"
        assert config.decimal_places == 2
        assert config.use_german_formatting is True

    def test_custom_config(self):
        """Test custom configuration values"""
        config = PricingTemplateConfig(
            system_type='heatpump',
            include_components=False,
            include_modifications=False,
            currency_symbol="USD",
            decimal_places=3,
            use_german_formatting=False
        )

        assert config.system_type == 'heatpump'
        assert config.include_components is False
        assert config.include_modifications is False
        assert config.currency_symbol == "USD"
        assert config.decimal_places == 3
        assert config.use_german_formatting is False


class TestPVPricingTemplate:
    """Test cases for PVPricingTemplate"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = PricingTemplateConfig(system_type='pv')
        self.template = PVPricingTemplate(self.config)

    def test_initialization(self):
        """Test PV template initialization"""
        assert self.template.config == self.config
        assert isinstance(self.template.placeholders, dict)
        assert len(self.template.placeholders) > 0

    def test_pv_placeholders_generation(self):
        """Test PV-specific placeholder generation"""
        placeholders = self.template.placeholders

        # Check for essential PV component placeholders
        assert "PV_MODULES_QUANTITY" in placeholders
        assert "PV_MODULES_UNIT_PRICE" in placeholders
        assert "PV_MODULES_TOTAL_PRICE" in placeholders
        assert "PV_INVERTER_QUANTITY" in placeholders
        assert "PV_INVERTER_UNIT_PRICE" in placeholders
        assert "PV_STORAGE_QUANTITY" in placeholders

        # Check for installation placeholders
        assert "PV_INSTALLATION_DC_PRICE" in placeholders
        assert "PV_INSTALLATION_AC_PRICE" in placeholders
        assert "PV_COMMISSIONING_PRICE" in placeholders

        # Check for total placeholders
        assert "PV_NET_TOTAL" in placeholders
        assert "PV_VAT_AMOUNT" in placeholders
        assert "PV_GROSS_TOTAL" in placeholders

        # Check for system specification placeholders
        assert "PV_SYSTEM_POWER_KWP" in placeholders
        assert "PV_ANNUAL_PRODUCTION_KWH" in placeholders

    def test_pv_modifications_placeholders(self):
        """Test PV modification placeholders when enabled"""
        config_with_mods = PricingTemplateConfig(
            system_type='pv',
            include_modifications=True
        )
        template_with_mods = PVPricingTemplate(config_with_mods)

        placeholders = template_with_mods.placeholders

        # Check for discount placeholders
        assert "PV_EARLY_PAYMENT_DISCOUNT" in placeholders
        assert "PV_VOLUME_DISCOUNT" in placeholders
        assert "PV_TOTAL_DISCOUNTS" in placeholders

        # Check for surcharge placeholders
        assert "PV_RUSH_ORDER_SURCHARGE" in placeholders
        assert "PV_TOTAL_SURCHARGES" in placeholders

    def test_pv_modifications_disabled(self):
        """Test PV template without modifications"""
        config_no_mods = PricingTemplateConfig(
            system_type='pv',
            include_modifications=False
        )
        template_no_mods = PVPricingTemplate(config_no_mods)

        placeholders = template_no_mods.placeholders

        # Should not have modification placeholders
        assert "PV_EARLY_PAYMENT_DISCOUNT" not in placeholders
        assert "PV_VOLUME_DISCOUNT" not in placeholders
        assert "PV_TOTAL_DISCOUNTS" not in placeholders

    def test_pv_template_structure(self):
        """Test PV template structure"""
        structure = self.template.get_template_structure()

        assert structure["title"] == "Photovoltaik-Anlage - Preisaufstellung"
        assert "sections" in structure

        sections = structure["sections"]
        section_names = [s["name"] for s in sections]

        assert "components" in section_names
        assert "installation" in section_names
        assert "totals" in section_names

        # Check components section
        components_section = next(s for s in sections if s["name"] == "components")
        assert components_section["title"] == "Komponenten"
        assert "items" in components_section

        # Check that items have required keys
        for item in components_section["items"]:
            assert "description" in item
            if "quantity_key" in item:
                assert "unit_price_key" in item
                assert "total_price_key" in item


class TestHeatPumpPricingTemplate:
    """Test cases for HeatPumpPricingTemplate"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = PricingTemplateConfig(system_type='heatpump')
        self.template = HeatPumpPricingTemplate(self.config)

    def test_initialization(self):
        """Test heat pump template initialization"""
        assert self.template.config == self.config
        assert isinstance(self.template.placeholders, dict)
        assert len(self.template.placeholders) > 0

    def test_heatpump_placeholders_generation(self):
        """Test heat pump-specific placeholder generation"""
        placeholders = self.template.placeholders

        # Check for essential heat pump component placeholders
        assert "HP_UNIT_QUANTITY" in placeholders
        assert "HP_UNIT_UNIT_PRICE" in placeholders
        assert "HP_UNIT_TOTAL_PRICE" in placeholders
        assert "HP_BUFFER_TANK_QUANTITY" in placeholders
        assert "HP_HOT_WATER_TANK_QUANTITY" in placeholders

        # Check for installation placeholders
        assert "HP_INSTALLATION_PRICE" in placeholders
        assert "HP_HYDRAULIC_INSTALLATION_PRICE" in placeholders
        assert "HP_ELECTRICAL_INSTALLATION_PRICE" in placeholders

        # Check for heat pump specifications
        assert "HP_HEATING_POWER_KW" in placeholders
        assert "HP_COP_VALUE" in placeholders
        assert "HP_SCOP_VALUE" in placeholders

        # Check for BEG subsidy placeholders
        assert "HP_BEG_SUBSIDY_RATE" in placeholders
        assert "HP_BEG_SUBSIDY_AMOUNT" in placeholders
        assert "HP_NET_INVESTMENT_AFTER_SUBSIDY" in placeholders

    def test_heatpump_template_structure(self):
        """Test heat pump template structure"""
        structure = self.template.get_template_structure()

        assert structure["title"] == "Wärmepumpe - Preisaufstellung"
        assert "sections" in structure

        sections = structure["sections"]
        section_names = [s["name"] for s in sections]

        assert "components" in section_names
        assert "installation" in section_names
        assert "subsidies" in section_names
        assert "totals" in section_names

        # Check subsidies section (unique to heat pump)
        subsidies_section = next(s for s in sections if s["name"] == "subsidies")
        assert subsidies_section["title"] == "BEG-Förderung"
        assert "items" in subsidies_section


class TestCombinedPricingTemplate:
    """Test cases for CombinedPricingTemplate"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = PricingTemplateConfig(system_type='combined')
        self.template = CombinedPricingTemplate(self.config)

    def test_initialization(self):
        """Test combined template initialization"""
        assert self.template.config == self.config
        assert isinstance(self.template.pv_template, PVPricingTemplate)
        assert isinstance(self.template.hp_template, HeatPumpPricingTemplate)
        assert isinstance(self.template.placeholders, dict)

    def test_combined_placeholders_include_all(self):
        """Test that combined template includes all PV and HP placeholders"""
        placeholders = self.template.placeholders

        # Should include PV placeholders
        assert "PV_MODULES_QUANTITY" in placeholders
        assert "PV_NET_TOTAL" in placeholders

        # Should include HP placeholders
        assert "HP_UNIT_QUANTITY" in placeholders
        assert "HP_NET_TOTAL" in placeholders

        # Should include combined-specific placeholders
        assert "COMBINED_NET_TOTAL" in placeholders
        assert "COMBINED_GROSS_TOTAL" in placeholders
        assert "COMBINED_SYSTEM_DISCOUNT" in placeholders
        assert "SYNERGY_TOTAL_BENEFIT" in placeholders

    def test_combined_template_structure(self):
        """Test combined template structure"""
        structure = self.template.get_template_structure()

        assert structure["title"] == "Photovoltaik + Wärmepumpe - Gesamtpaket"
        assert "sections" in structure

        sections = structure["sections"]
        section_names = [s["name"] for s in sections]

        assert "pv_system" in section_names
        assert "hp_system" in section_names
        assert "synergies" in section_names
        assert "combined_totals" in section_names

        # Check synergies section (unique to combined)
        synergies_section = next(s for s in sections if s["name"] == "synergies")
        assert synergies_section["title"] == "Synergieeffekte"
        assert "items" in synergies_section


class TestPricingTemplateManager:
    """Test cases for PricingTemplateManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = PricingTemplateManager()

    def test_create_pv_template(self):
        """Test creating PV template"""
        template = self.manager.create_template('pv')

        assert isinstance(template, PVPricingTemplate)
        assert template.config.system_type == 'pv'
        assert 'pv' in self.manager.templates

    def test_create_heatpump_template(self):
        """Test creating heat pump template"""
        template = self.manager.create_template('heatpump')

        assert isinstance(template, HeatPumpPricingTemplate)
        assert template.config.system_type == 'heatpump'
        assert 'heatpump' in self.manager.templates

    def test_create_combined_template(self):
        """Test creating combined template"""
        template = self.manager.create_template('combined')

        assert isinstance(template, CombinedPricingTemplate)
        assert template.config.system_type == 'combined'
        assert 'combined' in self.manager.templates

    def test_create_template_with_custom_config(self):
        """Test creating template with custom configuration"""
        config = PricingTemplateConfig(
            system_type='pv',
            include_modifications=False,
            currency_symbol='USD'
        )

        template = self.manager.create_template('pv', config)

        assert template.config.currency_symbol == 'USD'
        assert template.config.include_modifications is False

    def test_create_template_invalid_type(self):
        """Test creating template with invalid system type"""
        with pytest.raises(ValueError, match="Unknown system type"):
            self.manager.create_template('invalid_type')

    def test_get_template(self):
        """Test getting existing template"""
        # Create template first
        created_template = self.manager.create_template('pv')

        # Get template
        retrieved_template = self.manager.get_template('pv')

        assert retrieved_template is created_template

    def test_get_nonexistent_template(self):
        """Test getting non-existent template"""
        template = self.manager.get_template('nonexistent')
        assert template is None

    def test_render_template(self):
        """Test rendering template with pricing data"""
        pricing_data = {
            'pv_pricing': {
                'PV_MODULES_QUANTITY': 20,
                'PV_MODULES_UNIT_PRICE': 180.0,
                'PV_NET_TOTAL': 15000.0
            }
        }

        rendered = self.manager.render_template('pv', pricing_data)

        assert isinstance(rendered, dict)
        assert len(rendered) > 0

        # Check that some values were rendered
        rendered_values = [v for v in rendered.values() if v != ""]
        assert len(rendered_values) > 0

    def test_find_pricing_value(self):
        """Test finding pricing values in nested data"""
        pricing_data = {
            'components': {
                'PV_MODULES_TOTAL': 3600.0,
                'PV_INVERTER_TOTAL': 800.0
            },
            'totals': {
                'NET_TOTAL': 15000.0
            }
        }

        # Test direct key match
        value1 = self.manager._find_pricing_value('NET_TOTAL', pricing_data)
        assert value1 == 15000.0

        # Test nested key match
        value2 = self.manager._find_pricing_value('PV_MODULES_TOTAL', pricing_data)
        assert value2 == 3600.0

        # Test non-existent key
        value3 = self.manager._find_pricing_value('NONEXISTENT_KEY', pricing_data)
        assert value3 is None

    def test_format_value_german(self):
        """Test German value formatting"""
        config = PricingTemplateConfig(
            system_type='pv',
            use_german_formatting=True,
            decimal_places=2
        )

        # Test number formatting
        formatted = self.manager._format_value(1234.56, config)
        assert formatted == "1.234,56 €"

        # Test large number
        formatted_large = self.manager._format_value(15000.0, config)
        assert formatted_large == "15.000,00 €"

        # Test boolean
        formatted_bool = self.manager._format_value(True, config)
        assert formatted_bool == "Ja"

        # Test string
        formatted_str = self.manager._format_value("Test", config)
        assert formatted_str == "Test"

    def test_format_value_english(self):
        """Test English value formatting"""
        config = PricingTemplateConfig(
            system_type='pv',
            use_german_formatting=False,
            decimal_places=2,
            currency_symbol='$'
        )

        formatted = self.manager._format_value(1234.56, config)
        assert formatted == "1234.56 $"

    def test_get_all_placeholders(self):
        """Test getting all placeholders for a system type"""
        placeholders = self.manager.get_all_placeholders('pv')

        assert isinstance(placeholders, dict)
        assert len(placeholders) > 0
        assert "PV_MODULES_QUANTITY" in placeholders

    def test_export_template_documentation(self):
        """Test exporting template documentation"""
        doc = self.manager.export_template_documentation('pv')

        assert doc["system_type"] == 'pv'
        assert "placeholders" in doc
        assert "structure" in doc
        assert "config" in doc

        config = doc["config"]
        assert "currency_symbol" in config
        assert "decimal_places" in config
        assert "use_german_formatting" in config


class TestConvenienceFunctions:
    """Test cases for convenience functions"""

    def test_create_pv_pricing_template(self):
        """Test PV template creation function"""
        template = create_pv_pricing_template()

        assert isinstance(template, PVPricingTemplate)
        assert template.config.system_type == 'pv'

    def test_create_heatpump_pricing_template(self):
        """Test heat pump template creation function"""
        template = create_heatpump_pricing_template()

        assert isinstance(template, HeatPumpPricingTemplate)
        assert template.config.system_type == 'heatpump'

    def test_create_combined_pricing_template(self):
        """Test combined template creation function"""
        template = create_combined_pricing_template()

        assert isinstance(template, CombinedPricingTemplate)
        assert template.config.system_type == 'combined'

    def test_get_template_manager(self):
        """Test global template manager function"""
        manager1 = get_template_manager()
        manager2 = get_template_manager()

        # Should return same instance (singleton pattern)
        assert manager1 is manager2
        assert isinstance(manager1, PricingTemplateManager)


class TestTemplateIntegration:
    """Integration tests for template system"""

    def test_full_pv_template_workflow(self):
        """Test complete PV template workflow"""
        # Create manager and template
        manager = PricingTemplateManager()
        template = manager.create_template('pv')

        # Sample pricing data
        pricing_data = {
            'components': {
                'PV_MODULES_QUANTITY': 20,
                'PV_MODULES_UNIT_PRICE': 180.0,
                'PV_MODULES_TOTAL_PRICE': 3600.0,
                'PV_INVERTER_QUANTITY': 1,
                'PV_INVERTER_UNIT_PRICE': 800.0,
                'PV_INVERTER_TOTAL_PRICE': 800.0
            },
            'totals': {
                'PV_NET_TOTAL': 12605.04,
                'PV_VAT_AMOUNT': 2394.96,
                'PV_GROSS_TOTAL': 15000.0
            }
        }

        # Render template
        rendered = manager.render_template('pv', pricing_data)

        # Check that key values were rendered
        assert rendered['PV_MODULES_QUANTITY'] != ""
        assert rendered['PV_NET_TOTAL'] != ""

        # Check formatting
        assert '€' in rendered['PV_NET_TOTAL'] or rendered['PV_NET_TOTAL'] == ""

    def test_combined_template_includes_all_systems(self):
        """Test that combined template includes both PV and HP data"""
        manager = PricingTemplateManager()

        pricing_data = {
            'pv_components': {
                'PV_NET_TOTAL': 10000.0
            },
            'hp_components': {
                'HP_NET_TOTAL': 8000.0
            },
            'combined': {
                'COMBINED_NET_TOTAL': 18000.0,
                'COMBINED_PACKAGE_DISCOUNT': 500.0
            }
        }

        rendered = manager.render_template('combined', pricing_data)

        # Should have both PV and HP placeholders
        pv_keys = [k for k in rendered.keys() if k.startswith('PV_')]
        hp_keys = [k for k in rendered.keys() if k.startswith('HP_')]
        combined_keys = [k for k in rendered.keys() if k.startswith('COMBINED_')]

        assert len(pv_keys) > 0
        assert len(hp_keys) > 0
        assert len(combined_keys) > 0


if __name__ == '__main__':
    pytest.main([__file__])
