"""PV-Specific Pricing Engine

Specialized pricing engine for photovoltaic systems with full product integration.
Extends the base PricingEngine with PV-specific logic for modules, inverters,
storage systems, and accessories.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

try:
    from product_db import (
        calculate_price_by_method,
        calculate_selling_price,
        get_product_by_id,
        get_product_by_model_name,
        list_products,
    )
except ImportError:
    # Fallback for testing without database
    def get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return None

    def get_product_by_model_name(model_name: str) -> dict[str, Any] | None:
        return None

    def list_products(category: str | None = None,
                      company_id: int | None = None) -> list[dict[str, Any]]:
        return []

    def calculate_price_by_method(base_price: float,
                                  quantity: float,
                                  calculate_per: str,
                                  product_specs: dict[str,
                                                      Any] | None = None) -> float:
        return base_price * quantity

    def calculate_selling_price(
            product_id: int | float) -> dict[str, Any] | None:
        return None

from .dynamic_key_manager import DynamicKeyManager
from .enhanced_pricing_engine import PriceComponent, PricingEngine, PricingResult
from .vat_manager import VATCategory

logger = logging.getLogger(__name__)

# PV-specific component categories
PV_CATEGORIES = {
    "modules": [
        "pv-modul",
        "pv-module",
        "solarmodul",
        "solar-modul",
        "photovoltaik-modul"],
    "inverters": [
        "wechselrichter",
        "inverter",
        "string-wechselrichter",
        "mikro-wechselrichter"],
    "storage": [
        "speicher",
        "batteriespeicher",
        "stromspeicher",
        "battery",
        "akku"],
    "mounting": [
        "montagesystem",
        "mounting",
        "befestigung",
        "dachbefestigung",
        "unterkonstruktion"],
    "cables": [
        "kabel",
        "cable",
        "dc-kabel",
        "ac-kabel",
        "solarkabel"],
    "accessories": [
        "zubehoer",
        "zubehör",
        "accessory",
        "kleinteile",
        "sicherung"],
    "services": [
        "dienstleistung",
        "service",
        "installation",
        "montage",
        "planung"]}


@dataclass
class PVPriceComponent(PriceComponent):
    """Extended PriceComponent for PV-specific calculations"""

    # PV-specific fields
    system_capacity_kwp: float | None = None
    module_count: int | None = None
    string_configuration: str | None = None
    installation_complexity: str | None = None  # "simple", "medium", "complex"

    def __post_init__(self):
        """Enhanced post-init for PV-specific calculations"""
        super().__post_init__()
        self._calculate_pv_specific_pricing()

    def _calculate_pv_specific_pricing(self):
        """Apply PV-specific pricing logic"""
        # Adjust pricing based on installation complexity
        if self.installation_complexity == "complex":
            complexity_multiplier = 1.2
        elif self.installation_complexity == "medium":
            complexity_multiplier = 1.1
        else:
            complexity_multiplier = 1.0

        # Apply complexity adjustment
        self.total_price *= complexity_multiplier

        # Update dynamic keys with PV-specific information
        self._add_pv_keys()

    def _add_pv_keys(self):
        """Add PV-specific dynamic keys"""
        key_manager = DynamicKeyManager()
        safe_name = key_manager._create_safe_key_name(self.model_name)

        pv_keys = {}

        if self.system_capacity_kwp:
            pv_keys[f"{safe_name}_SYSTEM_KWP"] = self.system_capacity_kwp

        if self.module_count:
            pv_keys[f"{safe_name}_MODULE_COUNT"] = self.module_count

        if self.string_configuration:
            pv_keys[f"{safe_name}_STRING_CONFIG"] = self.string_configuration

        if self.installation_complexity:
            pv_keys[f"{safe_name}_COMPLEXITY"] = self.installation_complexity

        # Add efficiency-based pricing information
        if self.efficiency_percent:
            efficiency_tier = "high" if self.efficiency_percent >= 20 else "standard"
            pv_keys[f"{safe_name}_EFFICIENCY_TIER"] = efficiency_tier

        # Add technology-based pricing
        if self.technology:
            pv_keys[f"{safe_name}_TECH_TYPE"] = self.technology

        self.dynamic_keys.update(pv_keys)


class PVPricingEngine(PricingEngine):
    """PV-specific pricing engine with comprehensive product integration"""

    def __init__(self, country_code: str = "DE"):
        """Initialize PV pricing engine"""
        super().__init__(system_type="pv", country_code=country_code)
        self.logger = logging.getLogger(f"{__name__}.PVPricingEngine")

        # Set up PV-specific VAT mappings
        self._setup_pv_vat_mappings()

    def calculate_pv_system_price(
            self, system_config: dict[str, Any]) -> PricingResult:
        """Calculate complete PV system pricing

        Args:
            system_config: PV system configuration with components and specifications

        Returns:
            PricingResult with PV system pricing
        """
        try:
            components = system_config.get("components", [])
            system_specs = system_config.get("system_specs", {})

            # Calculate base price with PV-specific logic
            base_result = self._calculate_pv_base_price(
                components, system_specs)

            # Add PV-specific validations
            self._validate_pv_configuration(components, system_specs)

            # Generate PV-specific system keys
            pv_system_keys = self._generate_pv_system_keys(
                base_result, system_specs)
            base_result.dynamic_keys.update(pv_system_keys)

            return base_result

        except Exception as e:
            self.logger.error(f"Error calculating PV system price: {e}")
            raise

    def _setup_pv_vat_mappings(self):
        """Set up PV-specific VAT category mappings"""
        try:
            # Map PV component categories to VAT categories
            pv_vat_mappings = {
                # Hardware components - standard VAT
                "PV Module": VATCategory.STANDARD,
                "Inverter": VATCategory.STANDARD,
                "Battery Storage": VATCategory.STANDARD,
                "Mounting System": VATCategory.STANDARD,
                "Cables": VATCategory.STANDARD,
                "Safety Equipment": VATCategory.STANDARD,
                "Monitoring": VATCategory.STANDARD,

                # Services - standard VAT (could be different in some
                # countries)
                "Installation Service": VATCategory.STANDARD,
                "Planning Service": VATCategory.STANDARD,
                "Maintenance": VATCategory.STANDARD,

                # Accessories - standard VAT
                "Accessories": VATCategory.STANDARD,
                "Tools": VATCategory.STANDARD
            }

            for category, vat_category in pv_vat_mappings.items():
                self.vat_manager.set_category_vat_mapping(
                    category, vat_category)

            self.logger.info(
                f"Set up {
                    len(pv_vat_mappings)} PV VAT category mappings")

        except Exception as e:
            self.logger.error(f"Error setting up PV VAT mappings: {e}")

    def calculate_pv_system_vat(self,
                                components: list[PriceComponent],
                                additional_costs: float = 0.0) -> dict[str,
                                                                       Any]:
        """Calculate VAT for PV system with component-level breakdown

        Args:
            components: List of PV price components
            additional_costs: Additional costs (accessories, services)

        Returns:
            Dictionary with VAT calculation details
        """
        try:
            # Prepare items for mixed VAT calculation
            vat_items = []

            # Add component costs
            for comp in components:
                vat_items.append({
                    "net_amount": comp.total_price,
                    "category": comp.category
                })

            # Add additional costs if any
            if additional_costs > 0:
                vat_items.append({
                    "net_amount": additional_costs,
                    "category": "Accessories"  # Default category for additional costs
                })

            # Calculate mixed VAT
            vat_calculation = self.vat_manager.calculate_mixed_vat(vat_items)

            return {
                "vat_calculation": vat_calculation,
                "component_breakdown": vat_calculation.breakdown.get(
                    "category_breakdowns",
                    {}),
                "total_net": vat_calculation.net_amount,
                "total_vat": vat_calculation.vat_amount,
                "total_gross": vat_calculation.gross_amount,
                "effective_vat_rate": vat_calculation.vat_rate_percent,
                "dynamic_keys": vat_calculation.dynamic_keys}

        except Exception as e:
            self.logger.error(f"Error calculating PV system VAT: {e}")
            # Fallback to simple VAT calculation
            total_net = sum(
                comp.total_price for comp in components) + additional_costs
            fallback_vat = self.vat_manager.calculate_vat(
                total_net, "PV Module")
            return {
                "vat_calculation": fallback_vat,
                "component_breakdown": {},
                "total_net": fallback_vat.net_amount,
                "total_vat": fallback_vat.vat_amount,
                "total_gross": fallback_vat.gross_amount,
                "effective_vat_rate": fallback_vat.vat_rate_percent,
                "dynamic_keys": fallback_vat.dynamic_keys
            }

    def _calculate_pv_base_price(self,
                                 components: list[dict[str,
                                                       Any]],
                                 system_specs: dict[str,
                                                    Any]) -> PricingResult:
        """Calculate base price with PV-specific logic"""
        pv_components = []
        total_base_price = 0.0
        all_dynamic_keys = {}

        # Extract system-level specifications
        total_capacity_kwp = system_specs.get("total_capacity_kwp", 0.0)
        installation_type = system_specs.get(
            "installation_type", "roof_mounted")

        for comp_data in components:
            # Get product information
            product = self._get_product_info(comp_data)
            if not product:
                self.logger.warning(f"PV product not found: {comp_data}")
                continue

            # Determine component category
            category = self._classify_pv_component(product)

            # Create PV-specific price component
            pv_comp = self._create_pv_price_component(
                product, comp_data, system_specs, category
            )
            pv_components.append(pv_comp)

            # Calculate price using PV-specific logic
            component_price = self._calculate_pv_component_price(
                pv_comp, system_specs
            )
            total_base_price += component_price

            # Merge dynamic keys
            all_dynamic_keys.update(pv_comp.dynamic_keys)

        # Generate system-level keys
        system_keys = self._generate_pv_system_keys_base(
            total_base_price, pv_components, system_specs
        )
        all_dynamic_keys.update(system_keys)

        return PricingResult(
            base_price=total_base_price,
            components=pv_components,
            dynamic_keys=all_dynamic_keys,
            metadata={
                "system_type": "pv",
                "component_count": len(pv_components),
                "total_capacity_kwp": total_capacity_kwp,
                "installation_type": installation_type,
                "calculation_method": "pv_specific"
            }
        )

    def _classify_pv_component(self, product: dict[str, Any]) -> str:
        """Classify PV component based on product data"""
        category = product.get("category", "").lower()
        model_name = product.get("model_name", "").lower()

        # Check each PV category
        for pv_cat, keywords in PV_CATEGORIES.items():
            if any(keyword in category for keyword in keywords):
                return pv_cat
            if any(keyword in model_name for keyword in keywords):
                return pv_cat

        # Default classification based on capacity and power
        if product.get("capacity_w"):
            return "modules"
        if product.get("power_kw"):
            return "inverters"
        if product.get("max_kwh_capacity"):
            return "storage"
        return "accessories"

    def _create_pv_price_component(self, product: dict[str, Any],
                                   comp_data: dict[str, Any],
                                   system_specs: dict[str, Any],
                                   category: str) -> PVPriceComponent:
        """Create PV-specific price component"""
        # Calculate system capacity for this component
        system_capacity_kwp = None
        if category == "modules" and product.get("capacity_w"):
            quantity = comp_data.get("quantity", 1)
            system_capacity_kwp = (product["capacity_w"] * quantity) / 1000.0

        # Determine installation complexity
        installation_complexity = self._determine_installation_complexity(
            product, system_specs
        )

        return PVPriceComponent(
            product_id=product.get("id", 0),
            model_name=product.get("model_name", ""),
            category=category,
            brand=product.get("brand"),
            quantity=comp_data.get("quantity", 1),

            # Core pricing
            price_euro=float(product.get("price_euro", 0.0)),
            calculate_per=product.get("calculate_per"),

            # Technical specs
            capacity_w=product.get("capacity_w"),
            storage_power_kw=product.get("storage_power_kw"),
            power_kw=product.get("power_kw"),
            max_cycles=product.get("max_cycles"),
            warranty_years=product.get("warranty_years"),

            # Enhanced attributes
            technology=product.get("technology"),
            feature=product.get("feature"),
            design=product.get("design"),
            upgrade=product.get("upgrade"),
            max_kwh_capacity=product.get("max_kwh_capacity"),
            outdoor_opt=product.get("outdoor_opt"),
            self_supply_feature=product.get("self_supply_feature"),
            shadow_fading=product.get("shadow_fading"),
            smart_home=product.get("smart_home"),

            # Physical dimensions
            length_m=product.get("length_m"),
            width_m=product.get("width_m"),
            weight_kg=product.get("weight_kg"),
            efficiency_percent=product.get("efficiency_percent"),

            # Additional info
            origin_country=product.get("origin_country"),
            description=product.get("description"),
            pros=product.get("pros"),
            cons=product.get("cons"),
            rating=product.get("rating"),

            # PV-specific fields
            system_capacity_kwp=system_capacity_kwp,
            module_count=comp_data.get(
                "quantity") if category == "modules" else None,
            string_configuration=comp_data.get("string_configuration"),
            installation_complexity=installation_complexity
        )

    def _determine_installation_complexity(
            self, product: dict[str, Any], system_specs: dict[str, Any]) -> str:
        """Determine installation complexity based on product and system specs"""
        installation_type = system_specs.get(
            "installation_type", "roof_mounted")
        roof_type = system_specs.get("roof_type", "standard")

        # Complex installations
        if installation_type in ["ground_mounted", "facade", "carport"]:
            return "complex"

        # Medium complexity
        if roof_type in [
                "flat",
                "metal",
                "tile"] and system_specs.get(
                "obstacles",
                False):
            return "medium"

        # Simple installations
        return "simple"

    def _calculate_pv_component_price(self, component: PVPriceComponent,
                                      system_specs: dict[str, Any]) -> float:
        """Calculate component price using PV-specific logic"""
        base_price = component.price_euro
        quantity = component.quantity
        calculate_per = component.calculate_per or "Stück"

        # Use enhanced calculation method
        if calculate_per.lower() == "kwp" and component.system_capacity_kwp:
            # For kWp-based pricing, use system capacity
            total_price = base_price * component.system_capacity_kwp
        else:
            # Use standard calculation method
            product_specs = {
                "capacity_w": component.capacity_w,
                "power_kw": component.power_kw,
                "max_kwh_capacity": component.max_kwh_capacity
            }
            total_price = calculate_price_by_method(
                base_price, quantity, calculate_per, product_specs
            )

        # Apply technology-based adjustments
        total_price = self._apply_technology_adjustments(
            component, total_price)

        # Apply efficiency-based adjustments
        total_price = self._apply_efficiency_adjustments(
            component, total_price)

        return total_price

    def _apply_technology_adjustments(self, component: PVPriceComponent,
                                      base_price: float) -> float:
        """Apply technology-based pricing adjustments"""
        if not component.technology:
            return base_price

        technology = component.technology.lower()

        # Premium technology adjustments
        if "topcon" in technology or "hjt" in technology:
            return base_price * 1.05  # 5% premium for advanced technology
        if "perc" in technology:
            return base_price * 1.02  # 2% premium for PERC technology

        return base_price

    def _apply_efficiency_adjustments(self, component: PVPriceComponent,
                                      base_price: float) -> float:
        """Apply efficiency-based pricing adjustments"""
        if not component.efficiency_percent:
            return base_price

        # High-efficiency premium
        if component.efficiency_percent >= 22:
            return base_price * 1.08  # 8% premium for >22% efficiency
        if component.efficiency_percent >= 20:
            return base_price * 1.04  # 4% premium for >20% efficiency

        return base_price

    def _generate_pv_system_keys_base(self,
                                      total_price: float,
                                      components: list[PVPriceComponent],
                                      system_specs: dict[str,
                                                         Any]) -> dict[str,
                                                                       Any]:
        """Generate PV system-level dynamic keys"""
        system_keys = self.key_manager.generate_keys({
            "PV_BASE_PRICE_NET": total_price,
            "PV_COMPONENT_COUNT": len(components),
            "PV_SYSTEM_TYPE": "photovoltaic"
        }, prefix="PV_")

        # Calculate category totals
        category_totals = {}
        module_count = 0
        total_capacity_w = 0

        for comp in components:
            cat = comp.category
            if cat not in category_totals:
                category_totals[cat] = 0.0
            category_totals[cat] += comp.total_price

            # Track modules and capacity
            if cat == "modules":
                module_count += comp.quantity or 0
                if comp.capacity_w:
                    total_capacity_w += (comp.capacity_w *
                                         (comp.quantity or 0))

        # Add category totals
        for category, total in category_totals.items():
            safe_cat = self.key_manager._create_safe_key_name(category)
            system_keys[f"PV_{safe_cat.upper()}_TOTAL"] = total

        # Add system specifications
        system_keys.update({
            "PV_MODULE_COUNT": module_count,
            "PV_TOTAL_CAPACITY_W": total_capacity_w,
            "PV_TOTAL_CAPACITY_KWP": round(total_capacity_w / 1000.0, 2),
            "PV_INSTALLATION_TYPE": system_specs.get("installation_type", "roof_mounted"),
            "PV_ROOF_TYPE": system_specs.get("roof_type", "standard")
        })

        return system_keys

    def _generate_pv_system_keys(self,
                                 base_result: PricingResult,
                                 system_specs: dict[str,
                                                    Any]) -> dict[str,
                                                                  Any]:
        """Generate additional PV system keys"""
        pv_keys = {}

        # Performance calculations
        total_capacity_kwp = system_specs.get("total_capacity_kwp", 0.0)
        if total_capacity_kwp > 0:
            # Estimated annual yield (rough calculation)
            annual_yield_kwh = total_capacity_kwp * 1000  # 1000 kWh per kWp
            pv_keys["PV_ESTIMATED_ANNUAL_YIELD_KWH"] = annual_yield_kwh

            # Price per kWp
            price_per_kwp = base_result.base_price / total_capacity_kwp
            pv_keys["PV_PRICE_PER_KWP"] = round(price_per_kwp, 2)

        # System quality indicators
        avg_efficiency = self._calculate_average_efficiency(
            base_result.components)
        if avg_efficiency:
            pv_keys["PV_AVERAGE_EFFICIENCY_PCT"] = round(avg_efficiency, 2)

        # Warranty information
        min_warranty = self._calculate_minimum_warranty(base_result.components)
        if min_warranty:
            pv_keys["PV_MINIMUM_WARRANTY_YEARS"] = min_warranty

        return pv_keys

    def _calculate_average_efficiency(
            self, components: list[PriceComponent]) -> float | None:
        """Calculate weighted average efficiency of PV modules"""
        total_capacity = 0.0
        weighted_efficiency = 0.0

        for comp in components:
            if (comp.category == "modules" and
                comp.efficiency_percent and
                    comp.capacity_w):

                capacity = comp.capacity_w * (comp.quantity or 1)
                total_capacity += capacity
                weighted_efficiency += comp.efficiency_percent * capacity

        if total_capacity > 0:
            return weighted_efficiency / total_capacity

        return None

    def _calculate_minimum_warranty(
            self, components: list[PriceComponent]) -> int | None:
        """Calculate minimum warranty across all components"""
        warranties = [
            comp.warranty_years for comp in components
            if comp.warranty_years and comp.warranty_years > 0
        ]

        return min(warranties) if warranties else None

    def _validate_pv_configuration(self, components: list[dict[str, Any]],
                                   system_specs: dict[str, Any]):
        """Validate PV system configuration"""
        # Check for required components
        has_modules = any(
            self._classify_pv_component(self._get_product_info(comp) or {}) == "modules"
            for comp in components
        )

        has_inverter = any(
            self._classify_pv_component(self._get_product_info(comp) or {}) == "inverters"
            for comp in components
        )

        if not has_modules:
            self.logger.warning("PV system configuration missing modules")

        if not has_inverter:
            self.logger.warning("PV system configuration missing inverter")

        # Validate capacity matching
        self._validate_capacity_matching(components)

    def _validate_capacity_matching(self, components: list[dict[str, Any]]):
        """Validate that inverter capacity matches module capacity"""
        total_module_capacity = 0.0
        total_inverter_capacity = 0.0

        for comp_data in components:
            product = self._get_product_info(comp_data)
            if not product:
                continue

            category = self._classify_pv_component(product)
            quantity = comp_data.get("quantity", 1)

            if category == "modules" and product.get("capacity_w"):
                total_module_capacity += product["capacity_w"] * quantity
            elif category == "inverters" and product.get("power_kw"):
                # Convert to W
                total_inverter_capacity += product["power_kw"] * \
                    quantity * 1000

        if total_module_capacity > 0 and total_inverter_capacity > 0:
            ratio = total_module_capacity / total_inverter_capacity
            if ratio > 1.3 or ratio < 0.8:
                self.logger.warning(
                    f"PV capacity mismatch: modules {total_module_capacity}W, "
                    f"inverters {total_inverter_capacity}W (ratio: {ratio:.2f})"
                )

    def calculate_pv_accessories_price(self, accessories: list[dict[str, Any]],
                                       base_system_price: float) -> dict[str, Any]:
        """Calculate pricing for PV accessories and optional components"""
        try:
            accessory_components = []
            total_accessory_price = 0.0
            accessory_keys = {}

            for acc_data in accessories:
                product = self._get_product_info(acc_data)
                if not product:
                    continue

                # Create accessory component
                acc_comp = self._create_pv_price_component(
                    product, acc_data, {}, "accessories"
                )
                accessory_components.append(acc_comp)

                # Calculate accessory price
                acc_price = self._calculate_pv_component_price(acc_comp, {})
                total_accessory_price += acc_price

                # Add accessory keys
                accessory_keys.update(acc_comp.dynamic_keys)

            # Generate accessory summary keys
            summary_keys = self.key_manager.generate_keys(
                {
                    "ACCESSORIES_COUNT": len(accessory_components),
                    "ACCESSORIES_TOTAL_PRICE": total_accessory_price,
                    "ACCESSORIES_PERCENTAGE": (
                        total_accessory_price /
                        base_system_price *
                        100.0) if base_system_price > 0 else 0.0},
                prefix="PV_")

            accessory_keys.update(summary_keys)

            return {
                "components": accessory_components,
                "total_price": total_accessory_price,
                "dynamic_keys": accessory_keys,
                "metadata": {
                    "accessory_count": len(accessory_components),
                    "base_system_price": base_system_price
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating PV accessories price: {e}")
            raise


# Convenience functions for external use
def create_pv_pricing_engine() -> PVPricingEngine:
    """Create a new PV pricing engine instance"""
    return PVPricingEngine()


def calculate_pv_system_pricing(
        system_config: dict[str, Any]) -> PricingResult:
    """Calculate PV system pricing using the PV pricing engine

    Args:
        system_config: PV system configuration

    Returns:
        PricingResult with complete PV system pricing
    """
    engine = create_pv_pricing_engine()
    return engine.calculate_pv_system_price(system_config)


__all__ = [
    "PVPriceComponent",
    "PVPricingEngine",
    "create_pv_pricing_engine",
    "calculate_pv_system_pricing",
    "PV_CATEGORIES"
]
