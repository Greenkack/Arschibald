"""PDF Pricing Templates

Provides specialized PDF templates with dynamic pricing placeholders for
PV systems, heat pump systems, and combined offers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PricingTemplateConfig:
    """Configuration for pricing template generation"""
    system_type: str  # 'pv', 'heatpump', 'combined'
    include_components: bool = True
    include_modifications: bool = True
    include_vat_breakdown: bool = True
    include_summary: bool = True
    currency_symbol: str = "€"
    decimal_places: int = 2
    use_german_formatting: bool = True


class PVPricingTemplate:
    """Template for PV system pricing sections"""

    def __init__(self, config: PricingTemplateConfig):
        self.config = config
        self.placeholders = self._generate_pv_placeholders()

    def _generate_pv_placeholders(self) -> dict[str, str]:
        """Generate PV-specific pricing placeholders"""
        placeholders = {
            # PV System Components
            "PV_MODULES_QUANTITY": "{{PV_MODULES_QUANTITY}}",
            "PV_MODULES_UNIT_PRICE": "{{PV_MODULES_UNIT_PRICE}}",
            "PV_MODULES_TOTAL_PRICE": "{{PV_MODULES_TOTAL_PRICE}}",
            "PV_MODULES_DESCRIPTION": "{{PV_MODULES_DESCRIPTION}}",

            "PV_INVERTER_QUANTITY": "{{PV_INVERTER_QUANTITY}}",
            "PV_INVERTER_UNIT_PRICE": "{{PV_INVERTER_UNIT_PRICE}}",
            "PV_INVERTER_TOTAL_PRICE": "{{PV_INVERTER_TOTAL_PRICE}}",
            "PV_INVERTER_DESCRIPTION": "{{PV_INVERTER_DESCRIPTION}}",

            "PV_STORAGE_QUANTITY": "{{PV_STORAGE_QUANTITY}}",
            "PV_STORAGE_UNIT_PRICE": "{{PV_STORAGE_UNIT_PRICE}}",
            "PV_STORAGE_TOTAL_PRICE": "{{PV_STORAGE_TOTAL_PRICE}}",
            "PV_STORAGE_DESCRIPTION": "{{PV_STORAGE_DESCRIPTION}}",

            # Installation and Services
            "PV_INSTALLATION_DC_PRICE": "{{PV_INSTALLATION_DC_PRICE}}",
            "PV_INSTALLATION_AC_PRICE": "{{PV_INSTALLATION_AC_PRICE}}",
            "PV_COMMISSIONING_PRICE": "{{PV_COMMISSIONING_PRICE}}",
            "PV_GRID_CONNECTION_PRICE": "{{PV_GRID_CONNECTION_PRICE}}",

            # Accessories and Optional Components
            "PV_MONITORING_SYSTEM_PRICE": "{{PV_MONITORING_SYSTEM_PRICE}}",
            "PV_SURGE_PROTECTION_PRICE": "{{PV_SURGE_PROTECTION_PRICE}}",
            "PV_CABLE_MANAGEMENT_PRICE": "{{PV_CABLE_MANAGEMENT_PRICE}}",

            # PV System Totals
            "PV_COMPONENTS_SUBTOTAL": "{{PV_COMPONENTS_SUBTOTAL}}",
            "PV_INSTALLATION_SUBTOTAL": "{{PV_INSTALLATION_SUBTOTAL}}",
            "PV_ACCESSORIES_SUBTOTAL": "{{PV_ACCESSORIES_SUBTOTAL}}",
            "PV_NET_TOTAL": "{{PV_NET_TOTAL}}",
            "PV_VAT_AMOUNT": "{{PV_VAT_AMOUNT}}",
            "PV_GROSS_TOTAL": "{{PV_GROSS_TOTAL}}",

            # PV System Specifications
            "PV_SYSTEM_POWER_KWP": "{{PV_SYSTEM_POWER_KWP}}",
            "PV_ANNUAL_PRODUCTION_KWH": "{{PV_ANNUAL_PRODUCTION_KWH}}",
            "PV_SELF_CONSUMPTION_RATE": "{{PV_SELF_CONSUMPTION_RATE}}",
            "PV_FEED_IN_RATE": "{{PV_FEED_IN_RATE}}",
        }

        # Add modifications if enabled
        if self.config.include_modifications:
            placeholders.update({
                "PV_EARLY_PAYMENT_DISCOUNT": "{{PV_EARLY_PAYMENT_DISCOUNT}}",
                "PV_VOLUME_DISCOUNT": "{{PV_VOLUME_DISCOUNT}}",
                "PV_SEASONAL_DISCOUNT": "{{PV_SEASONAL_DISCOUNT}}",
                "PV_RUSH_ORDER_SURCHARGE": "{{PV_RUSH_ORDER_SURCHARGE}}",
                "PV_WEEKEND_SURCHARGE": "{{PV_WEEKEND_SURCHARGE}}",
                "PV_TOTAL_DISCOUNTS": "{{PV_TOTAL_DISCOUNTS}}",
                "PV_TOTAL_SURCHARGES": "{{PV_TOTAL_SURCHARGES}}",
            })

        return placeholders

    def get_template_structure(self) -> dict[str, Any]:
        """Get PV pricing template structure"""
        return {
            "title": "Photovoltaik-Anlage - Preisaufstellung",
            "sections": [
                {
                    "name": "components",
                    "title": "Komponenten",
                    "items": [
                        {
                            "description": "PV-Module",
                            "quantity_key": "PV_MODULES_QUANTITY",
                            "unit_price_key": "PV_MODULES_UNIT_PRICE",
                            "total_price_key": "PV_MODULES_TOTAL_PRICE"
                        },
                        {
                            "description": "Wechselrichter",
                            "quantity_key": "PV_INVERTER_QUANTITY",
                            "unit_price_key": "PV_INVERTER_UNIT_PRICE",
                            "total_price_key": "PV_INVERTER_TOTAL_PRICE"
                        },
                        {
                            "description": "Batteriespeicher",
                            "quantity_key": "PV_STORAGE_QUANTITY",
                            "unit_price_key": "PV_STORAGE_UNIT_PRICE",
                            "total_price_key": "PV_STORAGE_TOTAL_PRICE"
                        }
                    ]
                },
                {
                    "name": "installation",
                    "title": "Installation und Inbetriebnahme",
                    "items": [
                        {
                            "description": "DC-Installation",
                            "price_key": "PV_INSTALLATION_DC_PRICE"
                        },
                        {
                            "description": "AC-Installation",
                            "price_key": "PV_INSTALLATION_AC_PRICE"
                        },
                        {
                            "description": "Inbetriebnahme",
                            "price_key": "PV_COMMISSIONING_PRICE"
                        }
                    ]
                },
                {
                    "name": "totals",
                    "title": "Gesamtsumme",
                    "items": [
                        {
                            "description": "Nettosumme",
                            "price_key": "PV_NET_TOTAL"
                        },
                        {
                            "description": "Mehrwertsteuer (19%)",
                            "price_key": "PV_VAT_AMOUNT"
                        },
                        {
                            "description": "Bruttosumme",
                            "price_key": "PV_GROSS_TOTAL",
                            "is_total": True
                        }
                    ]
                }
            ]
        }


class HeatPumpPricingTemplate:
    """Template for heat pump system pricing sections"""

    def __init__(self, config: PricingTemplateConfig):
        self.config = config
        self.placeholders = self._generate_heatpump_placeholders()

    def _generate_heatpump_placeholders(self) -> dict[str, str]:
        """Generate heat pump-specific pricing placeholders"""
        placeholders = {
            # Heat Pump Components
            "HP_UNIT_QUANTITY": "{{HP_UNIT_QUANTITY}}",
            "HP_UNIT_UNIT_PRICE": "{{HP_UNIT_UNIT_PRICE}}",
            "HP_UNIT_TOTAL_PRICE": "{{HP_UNIT_TOTAL_PRICE}}",
            "HP_UNIT_DESCRIPTION": "{{HP_UNIT_DESCRIPTION}}",

            "HP_BUFFER_TANK_QUANTITY": "{{HP_BUFFER_TANK_QUANTITY}}",
            "HP_BUFFER_TANK_UNIT_PRICE": "{{HP_BUFFER_TANK_UNIT_PRICE}}",
            "HP_BUFFER_TANK_TOTAL_PRICE": "{{HP_BUFFER_TANK_TOTAL_PRICE}}",

            "HP_HOT_WATER_TANK_QUANTITY": "{{HP_HOT_WATER_TANK_QUANTITY}}",
            "HP_HOT_WATER_TANK_UNIT_PRICE": "{{HP_HOT_WATER_TANK_UNIT_PRICE}}",
            "HP_HOT_WATER_TANK_TOTAL_PRICE": "{{HP_HOT_WATER_TANK_TOTAL_PRICE}}",

            # Installation and Services
            "HP_INSTALLATION_PRICE": "{{HP_INSTALLATION_PRICE}}",
            "HP_HYDRAULIC_INSTALLATION_PRICE": "{{HP_HYDRAULIC_INSTALLATION_PRICE}}",
            "HP_ELECTRICAL_INSTALLATION_PRICE": "{{HP_ELECTRICAL_INSTALLATION_PRICE}}",
            "HP_COMMISSIONING_PRICE": "{{HP_COMMISSIONING_PRICE}}",

            # Heat Pump Accessories
            "HP_CONTROL_SYSTEM_PRICE": "{{HP_CONTROL_SYSTEM_PRICE}}",
            "HP_SMART_GRID_INTERFACE_PRICE": "{{HP_SMART_GRID_INTERFACE_PRICE}}",
            "HP_BACKUP_HEATER_PRICE": "{{HP_BACKUP_HEATER_PRICE}}",

            # Heat Pump Totals
            "HP_COMPONENTS_SUBTOTAL": "{{HP_COMPONENTS_SUBTOTAL}}",
            "HP_INSTALLATION_SUBTOTAL": "{{HP_INSTALLATION_SUBTOTAL}}",
            "HP_ACCESSORIES_SUBTOTAL": "{{HP_ACCESSORIES_SUBTOTAL}}",
            "HP_NET_TOTAL": "{{HP_NET_TOTAL}}",
            "HP_VAT_AMOUNT": "{{HP_VAT_AMOUNT}}",
            "HP_GROSS_TOTAL": "{{HP_GROSS_TOTAL}}",

            # Heat Pump Specifications
            "HP_HEATING_POWER_KW": "{{HP_HEATING_POWER_KW}}",
            "HP_COP_VALUE": "{{HP_COP_VALUE}}",
            "HP_SCOP_VALUE": "{{HP_SCOP_VALUE}}",
            "HP_ANNUAL_CONSUMPTION_KWH": "{{HP_ANNUAL_CONSUMPTION_KWH}}",

            # BEG Subsidy Information
            "HP_BEG_SUBSIDY_RATE": "{{HP_BEG_SUBSIDY_RATE}}",
            "HP_BEG_SUBSIDY_AMOUNT": "{{HP_BEG_SUBSIDY_AMOUNT}}",
            "HP_NET_INVESTMENT_AFTER_SUBSIDY": "{{HP_NET_INVESTMENT_AFTER_SUBSIDY}}",
        }

        # Add modifications if enabled
        if self.config.include_modifications:
            placeholders.update({
                "HP_BEG_BONUS_DISCOUNT": "{{HP_BEG_BONUS_DISCOUNT}}",
                "HP_EFFICIENCY_BONUS": "{{HP_EFFICIENCY_BONUS}}",
                "HP_EARLY_PAYMENT_DISCOUNT": "{{HP_EARLY_PAYMENT_DISCOUNT}}",
                "HP_COMPLEXITY_SURCHARGE": "{{HP_COMPLEXITY_SURCHARGE}}",
                "HP_TOTAL_DISCOUNTS": "{{HP_TOTAL_DISCOUNTS}}",
                "HP_TOTAL_SURCHARGES": "{{HP_TOTAL_SURCHARGES}}",
            })

        return placeholders

    def get_template_structure(self) -> dict[str, Any]:
        """Get heat pump pricing template structure"""
        return {
            "title": "Wärmepumpe - Preisaufstellung",
            "sections": [
                {
                    "name": "components",
                    "title": "Komponenten",
                    "items": [
                        {
                            "description": "Wärmepumpe",
                            "quantity_key": "HP_UNIT_QUANTITY",
                            "unit_price_key": "HP_UNIT_UNIT_PRICE",
                            "total_price_key": "HP_UNIT_TOTAL_PRICE"
                        },
                        {
                            "description": "Pufferspeicher",
                            "quantity_key": "HP_BUFFER_TANK_QUANTITY",
                            "unit_price_key": "HP_BUFFER_TANK_UNIT_PRICE",
                            "total_price_key": "HP_BUFFER_TANK_TOTAL_PRICE"
                        },
                        {
                            "description": "Warmwasserspeicher",
                            "quantity_key": "HP_HOT_WATER_TANK_QUANTITY",
                            "unit_price_key": "HP_HOT_WATER_TANK_UNIT_PRICE",
                            "total_price_key": "HP_HOT_WATER_TANK_TOTAL_PRICE"
                        }
                    ]
                },
                {
                    "name": "installation",
                    "title": "Installation und Inbetriebnahme",
                    "items": [
                        {
                            "description": "Hydraulische Installation",
                            "price_key": "HP_HYDRAULIC_INSTALLATION_PRICE"
                        },
                        {
                            "description": "Elektrische Installation",
                            "price_key": "HP_ELECTRICAL_INSTALLATION_PRICE"
                        },
                        {
                            "description": "Inbetriebnahme",
                            "price_key": "HP_COMMISSIONING_PRICE"
                        }
                    ]
                },
                {
                    "name": "subsidies",
                    "title": "BEG-Förderung",
                    "items": [
                        {
                            "description": "Fördersatz",
                            "value_key": "HP_BEG_SUBSIDY_RATE"
                        },
                        {
                            "description": "Förderbetrag",
                            "price_key": "HP_BEG_SUBSIDY_AMOUNT"
                        }
                    ]
                },
                {
                    "name": "totals",
                    "title": "Gesamtsumme",
                    "items": [
                        {
                            "description": "Nettosumme",
                            "price_key": "HP_NET_TOTAL"
                        },
                        {
                            "description": "Mehrwertsteuer (19%)",
                            "price_key": "HP_VAT_AMOUNT"
                        },
                        {
                            "description": "Bruttosumme",
                            "price_key": "HP_GROSS_TOTAL"
                        },
                        {
                            "description": "Abzgl. BEG-Förderung",
                            "price_key": "HP_BEG_SUBSIDY_AMOUNT",
                            "is_deduction": True
                        },
                        {
                            "description": "Eigenanteil",
                            "price_key": "HP_NET_INVESTMENT_AFTER_SUBSIDY",
                            "is_total": True
                        }
                    ]
                }
            ]
        }


class CombinedPricingTemplate:
    """Template for combined PV + heat pump system pricing"""

    def __init__(self, config: PricingTemplateConfig):
        self.config = config
        self.pv_template = PVPricingTemplate(config)
        self.hp_template = HeatPumpPricingTemplate(config)
        self.placeholders = self._generate_combined_placeholders()

    def _generate_combined_placeholders(self) -> dict[str, str]:
        """Generate combined system pricing placeholders"""
        placeholders = {}

        # Include all PV placeholders
        placeholders.update(self.pv_template.placeholders)

        # Include all heat pump placeholders
        placeholders.update(self.hp_template.placeholders)

        # Add combined system placeholders
        combined_placeholders = {
            # Combined System Totals
            "COMBINED_PV_SUBTOTAL": "{{COMBINED_PV_SUBTOTAL}}",
            "COMBINED_HP_SUBTOTAL": "{{COMBINED_HP_SUBTOTAL}}",
            "COMBINED_NET_TOTAL": "{{COMBINED_NET_TOTAL}}",
            "COMBINED_VAT_AMOUNT": "{{COMBINED_VAT_AMOUNT}}",
            "COMBINED_GROSS_TOTAL": "{{COMBINED_GROSS_TOTAL}}",

            # Combined System Discounts
            "COMBINED_SYSTEM_DISCOUNT": "{{COMBINED_SYSTEM_DISCOUNT}}",
            "COMBINED_PACKAGE_DISCOUNT": "{{COMBINED_PACKAGE_DISCOUNT}}",
            "COMBINED_TOTAL_DISCOUNTS": "{{COMBINED_TOTAL_DISCOUNTS}}",

            # Combined System Specifications
            "COMBINED_TOTAL_POWER_KW": "{{COMBINED_TOTAL_POWER_KW}}",
            "COMBINED_ANNUAL_SAVINGS": "{{COMBINED_ANNUAL_SAVINGS}}",
            "COMBINED_PAYBACK_PERIOD": "{{COMBINED_PAYBACK_PERIOD}}",
            "COMBINED_ROI_PERCENT": "{{COMBINED_ROI_PERCENT}}",

            # Synergy Benefits
            "SYNERGY_SMART_GRID_BENEFIT": "{{SYNERGY_SMART_GRID_BENEFIT}}",
            "SYNERGY_SELF_CONSUMPTION_BENEFIT": "{{SYNERGY_SELF_CONSUMPTION_BENEFIT}}",
            "SYNERGY_TOTAL_BENEFIT": "{{SYNERGY_TOTAL_BENEFIT}}",
        }

        placeholders.update(combined_placeholders)
        return placeholders

    def get_template_structure(self) -> dict[str, Any]:
        """Get combined system pricing template structure"""
        return {"title": "Photovoltaik + Wärmepumpe - Gesamtpaket",
                "sections": [{"name": "pv_system",
                              "title": "Photovoltaik-Anlage",
                              "subsections": self.pv_template.get_template_structure()["sections"]},
                             {"name": "hp_system",
                              "title": "Wärmepumpen-System",
                              "subsections": self.hp_template.get_template_structure()["sections"]},
                             {"name": "synergies",
                              "title": "Synergieeffekte",
                              "items": [{"description": "Smart Grid Integration",
                                         "benefit_key": "SYNERGY_SMART_GRID_BENEFIT"},
                                        {"description": "Erhöhter Eigenverbrauch",
                                         "benefit_key": "SYNERGY_SELF_CONSUMPTION_BENEFIT"},
                                        {"description": "Gesamtnutzen Synergien",
                                         "benefit_key": "SYNERGY_TOTAL_BENEFIT"}]},
                             {"name": "combined_totals",
                              "title": "Gesamtinvestition",
                              "items": [{"description": "Photovoltaik-Anlage",
                                         "price_key": "COMBINED_PV_SUBTOTAL"},
                                        {"description": "Wärmepumpen-System",
                                         "price_key": "COMBINED_HP_SUBTOTAL"},
                                        {"description": "Paketrabatt",
                                         "price_key": "COMBINED_PACKAGE_DISCOUNT",
                                         "is_discount": True},
                                        {"description": "Nettosumme",
                                         "price_key": "COMBINED_NET_TOTAL"},
                                        {"description": "Mehrwertsteuer (19%)",
                                         "price_key": "COMBINED_VAT_AMOUNT"},
                                        {"description": "Gesamtinvestition",
                                         "price_key": "COMBINED_GROSS_TOTAL",
                                         "is_total": True}]}]}


class PricingTemplateManager:
    """Manager for pricing template generation and rendering"""

    def __init__(self):
        self.templates = {}

    def create_template(self, system_type: str, config: PricingTemplateConfig |
                        None = None) -> PVPricingTemplate | HeatPumpPricingTemplate | CombinedPricingTemplate:
        """Create pricing template for specified system type

        Args:
            system_type: Type of system ('pv', 'heatpump', 'combined')
            config: Optional template configuration

        Returns:
            Appropriate pricing template instance
        """
        if config is None:
            config = PricingTemplateConfig(system_type=system_type)

        if system_type == 'pv':
            template = PVPricingTemplate(config)
        elif system_type == 'heatpump':
            template = HeatPumpPricingTemplate(config)
        elif system_type == 'combined':
            template = CombinedPricingTemplate(config)
        else:
            raise ValueError(f"Unknown system type: {system_type}")

        self.templates[system_type] = template
        return template

    def get_template(
            self,
            system_type: str) -> PVPricingTemplate | HeatPumpPricingTemplate | CombinedPricingTemplate | None:
        """Get existing template for system type"""
        return self.templates.get(system_type)

    def render_template(self, system_type: str,
                        pricing_data: dict[str, Any]) -> dict[str, str]:
        """Render template with actual pricing data

        Args:
            system_type: Type of system
            pricing_data: Actual pricing values

        Returns:
            Dictionary with rendered placeholders
        """
        template = self.get_template(system_type)
        if not template:
            template = self.create_template(system_type)

        rendered = {}

        # Replace placeholders with actual values
        for placeholder_key, placeholder_value in template.placeholders.items():
            # Extract the key name from placeholder (remove {{ and }})
            key_name = placeholder_value.replace('{{', '').replace('}}', '')

            # Look for matching data in pricing_data
            actual_value = self._find_pricing_value(key_name, pricing_data)

            if actual_value is not None:
                rendered[placeholder_key] = self._format_value(
                    actual_value, template.config)
            else:
                rendered[placeholder_key] = ""  # Empty if no data found

        return rendered

    def _find_pricing_value(self, key_name: str,
                            pricing_data: dict[str, Any]) -> Any:
        """Find pricing value in nested data structure"""
        # Direct key match
        if key_name in pricing_data:
            return pricing_data[key_name]

        # Search in nested dictionaries
        for category_data in pricing_data.values():
            if isinstance(category_data, dict):
                if key_name in category_data:
                    return category_data[key_name]

                # Try partial key matches
                for data_key, data_value in category_data.items():
                    if key_name.upper() in data_key.upper() or data_key.upper() in key_name.upper():
                        return data_value

        return None

    def _format_value(self, value: Any, config: PricingTemplateConfig) -> str:
        """Format value according to template configuration"""
        try:
            if isinstance(value, bool):
                return "Ja" if value else "Nein"
            if isinstance(value, (int, float)):
                if config.use_german_formatting:
                    # German formatting: dot as thousands separator, comma as
                    # decimal
                    formatted = f"{value:,.{config.decimal_places}f}"
                    formatted = formatted.replace(
                        ',',
                        'X').replace(
                        '.',
                        ',').replace(
                        'X',
                        '.')
                    return f"{formatted} {config.currency_symbol}"
                return f"{
                    value:.{
                        config.decimal_places}f} {
                    config.currency_symbol}"
            if isinstance(value, str):
                return value
            return str(value)
        except (ValueError, TypeError):
            return str(value) if value is not None else ""

    def get_all_placeholders(self, system_type: str) -> dict[str, str]:
        """Get all placeholders for a system type"""
        template = self.get_template(system_type)
        if not template:
            template = self.create_template(system_type)

        return template.placeholders

    def export_template_documentation(
            self, system_type: str) -> dict[str, Any]:
        """Export template documentation for system type"""
        template = self.get_template(system_type)
        if not template:
            template = self.create_template(system_type)

        return {
            "system_type": system_type,
            "placeholders": template.placeholders,
            "structure": template.get_template_structure(),
            "config": {
                "currency_symbol": template.config.currency_symbol,
                "decimal_places": template.config.decimal_places,
                "use_german_formatting": template.config.use_german_formatting,
                "include_components": template.config.include_components,
                "include_modifications": template.config.include_modifications,
                "include_vat_breakdown": template.config.include_vat_breakdown
            }
        }


# Convenience functions for template creation
def create_pv_pricing_template(
        config: PricingTemplateConfig | None = None) -> PVPricingTemplate:
    """Create PV pricing template"""
    if config is None:
        config = PricingTemplateConfig(system_type='pv')
    return PVPricingTemplate(config)


def create_heatpump_pricing_template(
        config: PricingTemplateConfig | None = None) -> HeatPumpPricingTemplate:
    """Create heat pump pricing template"""
    if config is None:
        config = PricingTemplateConfig(system_type='heatpump')
    return HeatPumpPricingTemplate(config)


def create_combined_pricing_template(
        config: PricingTemplateConfig | None = None) -> CombinedPricingTemplate:
    """Create combined system pricing template"""
    if config is None:
        config = PricingTemplateConfig(system_type='combined')
    return CombinedPricingTemplate(config)


def get_template_manager() -> PricingTemplateManager:
    """Get global template manager instance"""
    if not hasattr(get_template_manager, '_instance'):
        get_template_manager._instance = PricingTemplateManager()
    return get_template_manager._instance
