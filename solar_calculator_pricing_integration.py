"""
Solar Calculator Pricing Integration

Integrates the solar calculator component selection with the enhanced pricing system.
Provides real-time pricing calculations with calculate_per support and dynamic key generation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Dummy st for compatibility

    class DummySt:
        @staticmethod
        def info(msg): print(f"INFO: {msg}")
        @staticmethod
        def warning(msg): print(f"WARNING: {msg}")
        @staticmethod
        def error(msg): print(f"ERROR: {msg}")
        @staticmethod
        def success(msg): print(f"SUCCESS: {msg}")

        class session_state:
            def __init__(self):
                self._state = {}

            def get(self, key, default=None):
                return self._state.get(key, default)

            def __setitem__(self, key, value):
                self._state[key] = value

            def __getitem__(self, key):
                return self._state[key]

            def __contains__(self, key):
                return key in self._state
        session_state = session_state()
    st = DummySt()

# Import pricing system components
try:
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
    from pricing.enhanced_pricing_engine import PriceComponent, PricingEngine
    PRICING_SYSTEM_AVAILABLE = True
except ImportError as e:
    PRICING_SYSTEM_AVAILABLE = False
    print(f"Warning: Enhanced pricing system not available: {e}")

# Import product database
try:
    from product_db import (
        calculate_price_by_method,
        calculate_selling_price,
        get_product_by_id,
        get_product_by_model_name,
    )
    PRODUCT_DB_AVAILABLE = True
except ImportError as e:
    PRODUCT_DB_AVAILABLE = False
    print(f"Warning: Product database not available: {e}")

logger = logging.getLogger(__name__)


class SolarCalculatorPricingIntegration:
    """Handles pricing integration for the solar calculator"""

    def __init__(self):
        self.pricing_engine = None
        self.key_manager = None
        self.current_pricing_data = {}
        self.pricing_cache = {}
        self.last_calculation_time = None

        if PRICING_SYSTEM_AVAILABLE:
            self.pricing_engine = PricingEngine("pv")
            self.key_manager = DynamicKeyManager()

        self.logger = logging.getLogger(
            f"{__name__}.SolarCalculatorPricingIntegration")

    def calculate_component_pricing(
            self, project_details: dict[str, Any]) -> dict[str, Any]:
        """Calculate pricing for all selected components

        Args:
            project_details: Project details from solar calculator

        Returns:
            Dictionary with pricing results and dynamic keys
        """
        try:
            if not PRICING_SYSTEM_AVAILABLE or not PRODUCT_DB_AVAILABLE:
                self.logger.warning(
                    "Pricing system or product database not available")
                return {
                    "components": [],
                    "base_price": 0.0,
                    "dynamic_keys": {},
                    "error": "Pricing system not available"
                }

            components = []
            total_base_price = 0.0
            all_dynamic_keys = {}

            # Process PV modules
            if self._has_valid_module_selection(project_details):
                module_pricing = self._calculate_module_pricing(
                    project_details)
                if module_pricing:
                    components.append(module_pricing)
                    total_base_price += module_pricing.get("total_price", 0.0)
                    all_dynamic_keys.update(
                        module_pricing.get(
                            "dynamic_keys", {}))

            # Process inverters
            if self._has_valid_inverter_selection(project_details):
                inverter_pricing = self._calculate_inverter_pricing(
                    project_details)
                if inverter_pricing:
                    components.append(inverter_pricing)
                    total_base_price += inverter_pricing.get(
                        "total_price", 0.0)
                    all_dynamic_keys.update(
                        inverter_pricing.get(
                            "dynamic_keys", {}))

            # Process battery storage
            if self._has_valid_storage_selection(project_details):
                storage_pricing = self._calculate_storage_pricing(
                    project_details)
                if storage_pricing:
                    components.append(storage_pricing)
                    total_base_price += storage_pricing.get("total_price", 0.0)
                    all_dynamic_keys.update(
                        storage_pricing.get(
                            "dynamic_keys", {}))

            # Process additional components
            additional_components = self._calculate_additional_components_pricing(
                project_details)
            for comp in additional_components:
                components.append(comp)
                total_base_price += comp.get("total_price", 0.0)
                all_dynamic_keys.update(comp.get("dynamic_keys", {}))

            # Generate system-level keys
            system_keys = self._generate_system_level_keys(
                total_base_price, components)
            all_dynamic_keys.update(system_keys)

            # Cache the results
            self.current_pricing_data = {
                "components": components,
                "base_price": total_base_price,
                "dynamic_keys": all_dynamic_keys,
                "calculation_timestamp": datetime.now().isoformat(),
                "project_details_hash": self._hash_project_details(project_details)}

            self.last_calculation_time = datetime.now()

            return self.current_pricing_data

        except Exception as e:
            self.logger.error(f"Error calculating component pricing: {e}")
            return {
                "components": [],
                "base_price": 0.0,
                "dynamic_keys": {},
                "error": str(e)
            }

    def _has_valid_module_selection(
            self, project_details: dict[str, Any]) -> bool:
        """Check if valid module selection exists"""
        return (
            project_details.get("selected_module_name") and
            project_details.get("module_quantity", 0) > 0
        )

    def _has_valid_inverter_selection(
            self, project_details: dict[str, Any]) -> bool:
        """Check if valid inverter selection exists"""
        return (
            project_details.get("selected_inverter_name") and
            project_details.get("selected_inverter_quantity", 0) > 0
        )

    def _has_valid_storage_selection(
            self, project_details: dict[str, Any]) -> bool:
        """Check if valid storage selection exists"""
        return (
            project_details.get("include_storage", False) and
            project_details.get("selected_storage_name") and
            project_details.get("selected_storage_storage_power_kw", 0) > 0
        )

    def _calculate_module_pricing(
            self, project_details: dict[str, Any]) -> dict[str, Any] | None:
        """Calculate pricing for PV modules with calculate_per support"""
        try:
            model_name = project_details.get("selected_module_name")
            quantity = int(project_details.get("module_quantity", 0))

            if not model_name or quantity <= 0:
                return None

            # Get product information
            product = get_product_by_model_name(model_name)
            if not product:
                self.logger.warning(f"Product not found: {model_name}")
                return None

            # Calculate pricing based on calculate_per method
            # Always use price_euro from product database, not any matrix price
            base_price = float(product.get("price_euro", 0.0))
            calculate_per = product.get("calculate_per", "Stück")

            # Ensure we use the correct base price from product database
            if base_price <= 0:
                self.logger.warning(
                    f"Invalid base price for {model_name}: {base_price}")
                return None

            # FIXED: Direct calculation to ensure correct pricing
            # For modules: quantity × unit_price (simple multiplication)
            unit_selling_price = base_price
            total_selling_price = quantity * base_price

            self.logger.info(
                f"Module calculation: {quantity} × {base_price}€ = {total_selling_price}€")

            # Get margin info for reference (but use direct calculation above)
            margin_info = calculate_selling_price(product["id"])

            # Generate dynamic keys
            if self.key_manager:
                component_keys = self.key_manager.generate_keys({
                    "PV_MODULE_MODEL": model_name,
                    "PV_MODULE_QUANTITY": quantity,
                    "PV_MODULE_UNIT_PRICE": unit_selling_price,
                    "PV_MODULE_TOTAL_PRICE": total_selling_price,
                    "PV_MODULE_CALCULATE_PER": calculate_per,
                    "PV_MODULE_CAPACITY_W": product.get("capacity_w", 0),
                    "PV_MODULE_BRAND": product.get("brand", ""),
                    "PV_MODULE_EFFICIENCY": product.get("efficiency_percent", 0),
                    "PV_MODULE_WARRANTY": product.get("warranty_years", 0),
                    "PV_MODULE_TECHNOLOGY": product.get("technology", ""),
                    "PV_MODULE_FEATURE": product.get("feature", ""),
                    "PV_MODULE_DESIGN": product.get("design", "")
                }, prefix="", category=KeyCategory.COMPONENTS)
            else:
                component_keys = {}

            return {
                "component_type": "pv_module",
                "model_name": model_name,
                "quantity": quantity,
                "unit_price": unit_selling_price,
                "total_price": total_selling_price,
                "calculate_per": calculate_per,
                "product_specs": product,
                "margin_info": margin_info,
                "dynamic_keys": component_keys
            }

        except Exception as e:
            self.logger.error(f"Error calculating module pricing: {e}")
            return None

    def _calculate_inverter_pricing(
            self, project_details: dict[str, Any]) -> dict[str, Any] | None:
        """Calculate pricing for inverters with calculate_per support"""
        try:
            model_name = project_details.get("selected_inverter_name")
            quantity = int(
                project_details.get(
                    "selected_inverter_quantity", 1))

            if not model_name:
                return None

            # Get product information
            product = get_product_by_model_name(model_name)
            if not product:
                self.logger.warning(
                    f"Inverter product not found: {model_name}")
                return None

            # Calculate pricing
            base_price = float(product.get("price_euro", 0.0))
            calculate_per = product.get("calculate_per", "Stück")

            total_price = calculate_price_by_method(
                base_price=base_price,
                quantity=quantity,
                calculate_per=calculate_per,
                product_specs=product
            )

            # Calculate selling price with margins
            margin_info = calculate_selling_price(product["id"])
            if margin_info and margin_info.get("selling_price_net", 0) > 0:
                unit_selling_price = margin_info["selling_price_net"]
                total_selling_price = calculate_price_by_method(
                    base_price=unit_selling_price,
                    quantity=quantity,
                    calculate_per=calculate_per,
                    product_specs=product
                )
            else:
                unit_selling_price = base_price
                total_selling_price = total_price

            # Generate dynamic keys
            if self.key_manager:
                component_keys = self.key_manager.generate_keys({
                    "INVERTER_MODEL": model_name,
                    "INVERTER_QUANTITY": quantity,
                    "INVERTER_UNIT_PRICE": unit_selling_price,
                    "INVERTER_TOTAL_PRICE": total_selling_price,
                    "INVERTER_CALCULATE_PER": calculate_per,
                    "INVERTER_POWER_KW": product.get("power_kw", 0),
                    "INVERTER_BRAND": product.get("brand", ""),
                    "INVERTER_WARRANTY": product.get("warranty_years", 0),
                    "INVERTER_TECHNOLOGY": product.get("technology", ""),
                    "INVERTER_FEATURE": product.get("feature", "")
                }, prefix="", category=KeyCategory.COMPONENTS)
            else:
                component_keys = {}

            return {
                "component_type": "inverter",
                "model_name": model_name,
                "quantity": quantity,
                "unit_price": unit_selling_price,
                "total_price": total_selling_price,
                "calculate_per": calculate_per,
                "product_specs": product,
                "margin_info": margin_info,
                "dynamic_keys": component_keys
            }

        except Exception as e:
            self.logger.error(f"Error calculating inverter pricing: {e}")
            return None

    def _calculate_storage_pricing(
            self, project_details: dict[str, Any]) -> dict[str, Any] | None:
        """Calculate pricing for battery storage with calculate_per support"""
        try:
            model_name = project_details.get("selected_storage_name")
            desired_capacity = float(
                project_details.get(
                    "selected_storage_storage_power_kw", 0))

            if not model_name or desired_capacity <= 0:
                return None

            # Get product information
            product = get_product_by_model_name(model_name)
            if not product:
                self.logger.warning(f"Storage product not found: {model_name}")
                return None

            # Calculate quantity based on desired capacity vs. unit capacity
            unit_capacity = float(product.get("storage_power_kw", 1.0))
            if unit_capacity > 0:
                quantity = max(1, round(desired_capacity / unit_capacity))
            else:
                quantity = 1

            # Calculate pricing
            base_price = float(product.get("price_euro", 0.0))
            calculate_per = product.get("calculate_per", "Stück")

            total_price = calculate_price_by_method(
                base_price=base_price,
                quantity=quantity,
                calculate_per=calculate_per,
                product_specs=product
            )

            # Calculate selling price with margins
            margin_info = calculate_selling_price(product["id"])
            if margin_info and margin_info.get("selling_price_net", 0) > 0:
                unit_selling_price = margin_info["selling_price_net"]
                total_selling_price = calculate_price_by_method(
                    base_price=unit_selling_price,
                    quantity=quantity,
                    calculate_per=calculate_per,
                    product_specs=product
                )
            else:
                unit_selling_price = base_price
                total_selling_price = total_price

            # Generate dynamic keys
            if self.key_manager:
                component_keys = self.key_manager.generate_keys({
                    "STORAGE_MODEL": model_name,
                    "STORAGE_QUANTITY": quantity,
                    "STORAGE_UNIT_PRICE": unit_selling_price,
                    "STORAGE_TOTAL_PRICE": total_selling_price,
                    "STORAGE_CALCULATE_PER": calculate_per,
                    "STORAGE_CAPACITY_KWH": desired_capacity,
                    "STORAGE_UNIT_CAPACITY_KWH": unit_capacity,
                    "STORAGE_BRAND": product.get("brand", ""),
                    "STORAGE_WARRANTY": product.get("warranty_years", 0),
                    "STORAGE_MAX_CYCLES": product.get("max_cycles", 0),
                    "STORAGE_TECHNOLOGY": product.get("technology", ""),
                    "STORAGE_FEATURE": product.get("feature", "")
                }, prefix="", category=KeyCategory.COMPONENTS)
            else:
                component_keys = {}

            return {
                "component_type": "storage",
                "model_name": model_name,
                "quantity": quantity,
                "unit_price": unit_selling_price,
                "total_price": total_selling_price,
                "calculate_per": calculate_per,
                "desired_capacity": desired_capacity,
                "unit_capacity": unit_capacity,
                "product_specs": product,
                "margin_info": margin_info,
                "dynamic_keys": component_keys
            }

        except Exception as e:
            self.logger.error(f"Error calculating storage pricing: {e}")
            return None

    def _calculate_additional_components_pricing(
            self, project_details: dict[str, Any]) -> list[dict[str, Any]]:
        """Calculate pricing for additional components with enhanced categorization and quantity support"""
        additional_components = []

        if not project_details.get("include_additional_components", False):
            return additional_components

        # Define additional component types with their keys and categories
        component_configs = [
            {
                "type": "wallbox",
                "name_key": "selected_wallbox_name",
                "quantity_key": "selected_wallbox_quantity",
                "category": "Ladeinfrastruktur",
                "display_name": "Wallbox"
            },
            {
                "type": "ems",
                "name_key": "selected_ems_name",
                "quantity_key": None,  # EMS typically quantity 1
                "category": "Energiemanagement",
                "display_name": "Energiemanagementsystem"
            },
            {
                "type": "optimizer",
                "name_key": "selected_optimizer_name",
                "quantity_key": "selected_optimizer_quantity",
                "category": "Energiemanagement",
                "display_name": "Leistungsoptimierer"
            },
            {
                "type": "carport",
                "name_key": "selected_carport_name",
                "quantity_key": None,  # Carport typically quantity 1
                "category": "Bauliche Erweiterungen",
                "display_name": "Solar Carport"
            },
            {
                "type": "notstrom",
                "name_key": "selected_notstrom_name",
                "quantity_key": None,  # Emergency power typically quantity 1
                "category": "Zusätzliche Systeme",
                "display_name": "Notstromversorgung"
            },
            {
                "type": "tierabwehr",
                "name_key": "selected_tierabwehr_name",
                "quantity_key": None,  # Animal protection typically quantity 1
                "category": "Schutz & Sicherheit",
                "display_name": "Tierabwehrschutz"
            }
        ]

        for config in component_configs:
            model_name = project_details.get(config["name_key"])
            if model_name:
                quantity = 1
                if config["quantity_key"]:
                    quantity = max(
                        1, int(
                            project_details.get(
                                config["quantity_key"], 1)))

                comp_pricing = self._calculate_single_additional_component(
                    config["type"],
                    model_name,
                    quantity,
                    config["category"],
                    config["display_name"]
                )
                if comp_pricing:
                    additional_components.append(comp_pricing)

        # Handle custom "Sonstiges" component
        custom_description = project_details.get(
            "additional_other_custom", "").strip()
        custom_price = float(
            project_details.get(
                "additional_other_price", 0.0))

        if custom_description and custom_price > 0:
            custom_component = self._create_custom_component_pricing(
                custom_description,
                custom_price
            )
            if custom_component:
                additional_components.append(custom_component)

        return additional_components

    def _calculate_single_additional_component(self,
                                               comp_type: str,
                                               model_name: str,
                                               quantity: int = 1,
                                               category: str = "",
                                               display_name: str = "") -> dict[str,
                                                                               Any] | None:
        """Calculate pricing for a single additional component with quantity and categorization support"""
        try:
            # Get product information
            product = get_product_by_model_name(model_name)
            if not product:
                self.logger.warning(
                    f"Additional component product not found: {model_name}")
                return None

            # Validate quantity
            quantity = max(1, int(quantity))

            # Calculate pricing
            base_price = float(product.get("price_euro", 0.0))
            calculate_per = product.get("calculate_per", "Stück")

            total_price = calculate_price_by_method(
                base_price=base_price,
                quantity=quantity,
                calculate_per=calculate_per,
                product_specs=product
            )

            # Calculate selling price with margins
            margin_info = calculate_selling_price(product["id"])
            if margin_info and margin_info.get("selling_price_net", 0) > 0:
                unit_selling_price = margin_info["selling_price_net"]
                total_selling_price = calculate_price_by_method(
                    base_price=unit_selling_price,
                    quantity=quantity,
                    calculate_per=calculate_per,
                    product_specs=product
                )
            else:
                unit_selling_price = base_price
                total_selling_price = total_price

            # Generate dynamic keys with enhanced categorization
            if self.key_manager:
                safe_comp_type = comp_type.upper()
                component_keys = self.key_manager.generate_keys({
                    f"{safe_comp_type}_MODEL": model_name,
                    f"{safe_comp_type}_QUANTITY": quantity,
                    f"{safe_comp_type}_UNIT_PRICE": unit_selling_price,
                    f"{safe_comp_type}_TOTAL_PRICE": total_selling_price,
                    f"{safe_comp_type}_CALCULATE_PER": calculate_per,
                    f"{safe_comp_type}_BRAND": product.get("brand", ""),
                    f"{safe_comp_type}_WARRANTY": product.get("warranty_years", 0),
                    f"{safe_comp_type}_CATEGORY": category,
                    f"{safe_comp_type}_DISPLAY_NAME": display_name or comp_type.title(),
                    f"{safe_comp_type}_TECHNOLOGY": product.get("technology", ""),
                    f"{safe_comp_type}_FEATURE": product.get("feature", ""),
                    f"{safe_comp_type}_EFFICIENCY": product.get("efficiency_percent", 0)
                }, prefix="", category=KeyCategory.COMPONENTS)
            else:
                component_keys = {}

            return {
                "component_type": comp_type,
                "model_name": model_name,
                "quantity": quantity,
                "unit_price": unit_selling_price,
                "total_price": total_selling_price,
                "calculate_per": calculate_per,
                "category": category,
                "display_name": display_name or comp_type.title(),
                "product_specs": product,
                "margin_info": margin_info,
                "dynamic_keys": component_keys,
                "is_optional": True,
                "pricing_rules": self._get_accessory_pricing_rules(
                    comp_type,
                    product)}

        except Exception as e:
            self.logger.error(f"Error calculating {comp_type} pricing: {e}")
            return None

    def _create_custom_component_pricing(
            self, description: str, price: float) -> dict[str, Any] | None:
        """Create pricing entry for custom 'Sonstiges' component"""
        try:
            if not description.strip() or price <= 0:
                return None

            # Generate dynamic keys for custom component
            if self.key_manager:
                component_keys = self.key_manager.generate_keys({
                    "CUSTOM_DESCRIPTION": description,
                    "CUSTOM_PRICE": price,
                    "CUSTOM_QUANTITY": 1,
                    "CUSTOM_CALCULATE_PER": "pauschal",
                    "CUSTOM_CATEGORY": "Sonstige Komponenten"
                }, prefix="", category=KeyCategory.COMPONENTS)
            else:
                component_keys = {}

            return {
                "component_type": "custom",
                "model_name": description,
                "quantity": 1,
                "unit_price": price,
                "total_price": price,
                "calculate_per": "pauschal",
                "category": "Sonstige Komponenten",
                "display_name": "Sonstige Komponente",
                "product_specs": {
                    "id": "custom",
                    "model_name": description,
                    "price_euro": price,
                    "calculate_per": "pauschal",
                    "category": "Sonstiges"
                },
                "margin_info": None,
                "dynamic_keys": component_keys,
                "is_optional": True,
                "is_custom": True,
                "pricing_rules": {"type": "fixed", "value": price}
            }

        except Exception as e:
            self.logger.error(f"Error creating custom component pricing: {e}")
            return None

    def _get_accessory_pricing_rules(
            self, comp_type: str, product: dict[str, Any]) -> dict[str, Any]:
        """Get pricing rules specific to accessory type"""
        rules = {
            "type": "standard",
            "supports_quantity": comp_type in [
                "wallbox",
                "optimizer"],
            "max_quantity": 20 if comp_type in [
                "wallbox",
                "optimizer"] else 1,
            "bulk_discount": None,
            "installation_required": comp_type in [
                "wallbox",
                "carport",
                "notstrom"],
            "vat_rate": "standard"}

        # Add component-specific rules
        if comp_type == "wallbox":
            rules.update({
                "bulk_discount": {"threshold": 3, "discount_percent": 5},
                "installation_labor_hours": 4,
                "requires_electrical_permit": True
            })
        elif comp_type == "carport":
            rules.update({
                "installation_labor_hours": 16,
                "requires_building_permit": True,
                "foundation_required": True
            })
        elif comp_type == "optimizer":
            rules.update({
                "bulk_discount": {"threshold": 10, "discount_percent": 3},
                "installation_labor_hours": 0.5  # per unit
            })

        return rules

    def _generate_system_level_keys(
            self, total_price: float, components: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate system-level dynamic keys"""
        if not self.key_manager:
            return {}

        # Calculate system totals by component type
        component_totals = {}
        for comp in components:
            comp_type = comp.get("component_type", "unknown")
            if comp_type not in component_totals:
                component_totals[comp_type] = 0.0
            component_totals[comp_type] += comp.get("total_price", 0.0)

        # Generate system keys
        system_data = {
            "PV_SYSTEM_BASE_PRICE": total_price,
            "PV_SYSTEM_COMPONENT_COUNT": len(components),
            "PV_SYSTEM_CALCULATION_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        # Add component type totals
        for comp_type, total in component_totals.items():
            safe_type = comp_type.upper().replace("_", "")
            system_data[f"PV_SYSTEM_{safe_type}_TOTAL"] = total

        return self.key_manager.generate_keys(
            system_data,
            prefix="",
            category=KeyCategory.TOTALS
        )

    def _hash_project_details(self, project_details: dict[str, Any]) -> str:
        """Create a hash of project details for caching"""
        import hashlib
        import json

        # Extract relevant fields for pricing including new accessory fields
        relevant_fields = [
            "selected_module_name",
            "module_quantity",
            "selected_inverter_name",
            "selected_inverter_quantity",
            "include_storage",
            "selected_storage_name",
            "selected_storage_storage_power_kw",
            "include_additional_components",
            "selected_wallbox_name",
            "selected_wallbox_quantity",
            "selected_ems_name",
            "selected_optimizer_name",
            "selected_optimizer_quantity",
            "selected_carport_name",
            "selected_notstrom_name",
            "selected_tierabwehr_name",
            "additional_other_custom",
            "additional_other_price"]

        relevant_data = {k: project_details.get(k) for k in relevant_fields}
        data_str = json.dumps(relevant_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get_pricing_display_data(
            self, project_details: dict[str, Any]) -> dict[str, Any]:
        """Get formatted pricing data for display in the UI with enhanced categorization"""
        pricing_data = self.calculate_component_pricing(project_details)

        if pricing_data.get("error"):
            return {
                "error": pricing_data["error"],
                "display_components": [],
                "display_components_by_category": {},
                "total_price": 0.0,
                "formatted_total": "0,00 €"
            }

        display_components = []
        display_components_by_category = {}

        for comp in pricing_data.get("components", []):
            component_display = {
                "name": comp.get("model_name", "Unknown"),
                "type": comp.get("display_name", comp.get("component_type", "unknown").replace("_", " ").title()),
                "category": comp.get("category", "Hauptkomponenten"),
                "quantity": comp.get("quantity", 0),
                "unit_price": comp.get("unit_price", 0.0),
                "total_price": comp.get("total_price", 0.0),
                "calculate_per": comp.get("calculate_per", "Stück"),
                "formatted_unit_price": self._format_currency(comp.get("unit_price", 0.0)),
                "formatted_total_price": self._format_currency(comp.get("total_price", 0.0)),
                "is_optional": comp.get("is_optional", False),
                "is_custom": comp.get("is_custom", False),
                "pricing_rules": comp.get("pricing_rules", {}),
                "brand": comp.get("product_specs", {}).get("brand", ""),
                "technology": comp.get("product_specs", {}).get("technology", ""),
                "warranty": comp.get("product_specs", {}).get("warranty_years", 0)
            }

            display_components.append(component_display)

            # Group by category for organized display
            category = component_display["category"]
            if category not in display_components_by_category:
                display_components_by_category[category] = {
                    "components": [],
                    "category_total": 0.0,
                    "formatted_category_total": "0,00 €"
                }

            display_components_by_category[category]["components"].append(
                component_display)
            display_components_by_category[category]["category_total"] += component_display["total_price"]
            display_components_by_category[category]["formatted_category_total"] = self._format_currency(
                display_components_by_category[category]["category_total"])

        total_price = pricing_data.get("base_price", 0.0)

        # Calculate totals by component type
        main_components_total = sum(
            comp["total_price"] for comp in display_components
            if not comp.get("is_optional", False)
        )
        optional_components_total = sum(
            comp["total_price"] for comp in display_components
            if comp.get("is_optional", False)
        )

        return {
            "display_components": display_components,
            "display_components_by_category": display_components_by_category,
            "total_price": total_price,
            "main_components_total": main_components_total,
            "optional_components_total": optional_components_total,
            "formatted_total": self._format_currency(total_price),
            "formatted_main_total": self._format_currency(main_components_total),
            "formatted_optional_total": self._format_currency(optional_components_total),
            "dynamic_keys": pricing_data.get("dynamic_keys", {}),
            "calculation_timestamp": pricing_data.get("calculation_timestamp"),
            "component_count": len(display_components),
            "optional_component_count": len([c for c in display_components if c.get("is_optional", False)])
        }

    def _format_currency(self, amount: float) -> str:
        """Format currency amount for German locale"""
        return f"{
            amount:,.2f} €".replace(
            ",",
            "X").replace(
            ".",
            ",").replace(
                "X",
            ".")

    def update_session_state_pricing(
            self, project_details: dict[str, Any]) -> None:
        """Update Streamlit session state with current pricing data"""
        if not STREAMLIT_AVAILABLE:
            return

        try:
            pricing_data = self.calculate_component_pricing(project_details)

            # Store pricing data in session state
            if 'pricing_data' not in st.session_state:
                st.session_state.pricing_data = {}

            st.session_state.pricing_data.update({
                'pv_system_pricing': pricing_data,
                'last_update': datetime.now().isoformat()
            })

            # Store dynamic keys for PDF generation
            if 'dynamic_keys' not in st.session_state:
                st.session_state.dynamic_keys = {}

            st.session_state.dynamic_keys.update(
                pricing_data.get("dynamic_keys", {}))

        except Exception as e:
            self.logger.error(f"Error updating session state pricing: {e}")

    def get_cached_pricing(self,
                           project_details: dict[str,
                                                 Any]) -> dict[str,
                                                               Any] | None:
        """Get cached pricing data if available and valid"""
        if not self.current_pricing_data:
            return None

        current_hash = self._hash_project_details(project_details)
        cached_hash = self.current_pricing_data.get("project_details_hash")

        if current_hash == cached_hash:
            return self.current_pricing_data

        return None

    def clear_pricing_cache(self) -> None:
        """Clear the pricing cache"""
        self.current_pricing_data = {}
        self.pricing_cache = {}
        self.last_calculation_time = None

    def validate_pricing_configuration(self) -> dict[str, Any]:
        """Validate that the pricing system is properly configured"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        if not PRICING_SYSTEM_AVAILABLE:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                "Enhanced pricing system not available")

        if not PRODUCT_DB_AVAILABLE:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                "Product database not available")

        if not self.pricing_engine:
            validation_result["warnings"].append(
                "Pricing engine not initialized")

        if not self.key_manager:
            validation_result["warnings"].append(
                "Dynamic key manager not initialized")

        return validation_result


# Global instance for easy access
solar_pricing_integration = SolarCalculatorPricingIntegration()


def integrate_pricing_with_solar_calculator(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Main function to integrate pricing with solar calculator

    Args:
        project_details: Project details from solar calculator

    Returns:
        Dictionary with pricing results and dynamic keys
    """
    return solar_pricing_integration.calculate_component_pricing(
        project_details)


def get_pricing_display_for_ui(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Get pricing data formatted for UI display

    Args:
        project_details: Project details from solar calculator

    Returns:
        Dictionary with formatted pricing data for display
    """
    return solar_pricing_integration.get_pricing_display_data(project_details)


def update_pricing_in_session_state(project_details: dict[str, Any]) -> None:
    """Update Streamlit session state with current pricing

    Args:
        project_details: Project details from solar calculator
    """
    solar_pricing_integration.update_session_state_pricing(project_details)
