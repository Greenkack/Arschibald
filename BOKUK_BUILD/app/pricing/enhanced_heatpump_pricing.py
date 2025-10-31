"""Enhanced Heat Pump Pricing Engine

Enhanced pricing engine for heat pump systems that integrates with the new
pricing system architecture while maintaining compatibility with existing
heatpump_pricing.py functionality.
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

# Import enhanced pricing system components
from .dynamic_key_manager import DynamicKeyManager
from .enhanced_pricing_engine import PriceComponent, PricingEngine, PricingResult
from .vat_manager import VATCategory

# Import existing heat pump pricing functionality
try:
    from heatpump_pricing import (
        LABOR_RATE_EUR_PER_HOUR_DEFAULT,
        BegConfig,
        ComponentCost,
        calculate_annuity_loan,
        calculate_beg_subsidy,
    )
except ImportError:
    # Fallback definitions if heatpump_pricing is not available
    @dataclass
    class ComponentCost:
        name: str
        category: str
        material_net: float
        labor_hours: float = 0.0
        labor_rate: float = 75.0
        description: str = ""

        @property
        def labor_cost_net(self) -> float:
            return self.labor_hours * self.labor_rate

        @property
        def total_net(self) -> float:
            return self.material_net + self.labor_cost_net

    @dataclass
    class BegConfig:
        base_pct: float = 30.0
        refrigerant_bonus_pct: float = 5.0
        heating_replacement_bonus_pct: float = 20.0
        low_income_bonus_pct: float = 20.0
        max_total_pct: float = 70.0
        eligible_cost_cap_eur: float = 30000.0

    def calculate_beg_subsidy(total_cost_net: float,
                              use_natural_refrigerant: bool,
                              replace_old_heating: bool,
                              low_income: bool,
                              cfg: BegConfig | None = None) -> dict[str,
                                                                    Any]:
        return {"subsidy_amount_net": 0.0, "applied_pct": 0.0}

    def calculate_annuity_loan(principal: float,
                               annual_interest_rate_pct: float,
                               years: int) -> dict[str,
                                                   Any]:
        return {"monthly_rate": 0.0, "total_interest": 0.0}

    LABOR_RATE_EUR_PER_HOUR_DEFAULT = 75.0


logger = logging.getLogger(__name__)

# Heat pump specific component categories
HEATPUMP_CATEGORIES = {
    "heatpump": [
        "waermepumpe",
        "wärmepumpe",
        "heatpump",
        "heat-pump",
        "vitocal"],
    "storage": [
        "speicher",
        "pufferspeicher",
        "warmwasserspeicher",
        "boiler"],
    "installation": [
        "dienstleistung",
        "service",
        "installation",
        "montage",
        "planung"],
    "accessories": [
        "zubehoer",
        "zubehör",
        "accessory",
        "kleinteile",
        "rohre",
        "ventile"],
    "controls": [
        "regelung",
        "steuerung",
        "thermostat",
        "control",
        "sensor"],
    "piping": [
        "rohrleitungen",
        "rohre",
        "pipes",
        "fittings",
        "anschluss"]}


@dataclass
class HeatPumpPriceComponent(PriceComponent):
    """Extended PriceComponent for heat pump-specific calculations"""

    # Heat pump specific fields
    heating_capacity_kw: float | None = None
    cop_rating: float | None = None  # Coefficient of Performance
    refrigerant_type: str | None = None
    installation_complexity: str | None = None  # "simple", "medium", "complex"
    labor_hours_required: float | None = None
    beg_eligible: bool | None = None

    def __post_init__(self):
        """Enhanced post-init for heat pump-specific calculations"""
        super().__post_init__()
        self._calculate_heatpump_specific_pricing()

    def _calculate_heatpump_specific_pricing(self):
        """Apply heat pump-specific pricing logic"""
        # Apply labor costs if specified
        if self.labor_hours_required:
            labor_cost = self.labor_hours_required * LABOR_RATE_EUR_PER_HOUR_DEFAULT
            self.total_price += labor_cost

        # Apply installation complexity adjustment
        if self.installation_complexity == "complex":
            complexity_multiplier = 1.3
        elif self.installation_complexity == "medium":
            complexity_multiplier = 1.15
        else:
            complexity_multiplier = 1.0

        self.total_price *= complexity_multiplier

        # Update dynamic keys with heat pump-specific information
        self._add_heatpump_keys()

    def _add_heatpump_keys(self):
        """Add heat pump-specific dynamic keys"""
        key_manager = DynamicKeyManager()
        safe_name = key_manager._create_safe_key_name(self.model_name)

        hp_keys = {}

        if self.heating_capacity_kw:
            hp_keys[f"{safe_name}_HEATING_CAPACITY_KW"] = self.heating_capacity_kw

        if self.cop_rating:
            hp_keys[f"{safe_name}_COP_RATING"] = self.cop_rating

        if self.refrigerant_type:
            hp_keys[f"{safe_name}_REFRIGERANT"] = self.refrigerant_type

        if self.installation_complexity:
            hp_keys[f"{safe_name}_COMPLEXITY"] = self.installation_complexity

        if self.labor_hours_required:
            hp_keys[f"{safe_name}_LABOR_HOURS"] = self.labor_hours_required
            hp_keys[f"{safe_name}_LABOR_COST"] = self.labor_hours_required * \
                LABOR_RATE_EUR_PER_HOUR_DEFAULT

        if self.beg_eligible is not None:
            hp_keys[f"{safe_name}_BEG_ELIGIBLE"] = self.beg_eligible

        # Add efficiency-based classification
        if self.cop_rating:
            if self.cop_rating >= 4.5:
                efficiency_class = "A+++"
            elif self.cop_rating >= 4.0:
                efficiency_class = "A++"
            elif self.cop_rating >= 3.5:
                efficiency_class = "A+"
            else:
                efficiency_class = "A"
            hp_keys[f"{safe_name}_EFFICIENCY_CLASS"] = efficiency_class

        self.dynamic_keys.update(hp_keys)


class EnhancedHeatPumpPricingEngine(PricingEngine):
    """Enhanced heat pump pricing engine with comprehensive product integration"""

    def __init__(self, country_code: str = "DE"):
        """Initialize enhanced heat pump pricing engine"""
        super().__init__(system_type="heatpump", country_code=country_code)
        self.logger = logging.getLogger(
            f"{__name__}.EnhancedHeatPumpPricingEngine")
        self.labor_rate = LABOR_RATE_EUR_PER_HOUR_DEFAULT

        # Set up heat pump-specific VAT mappings
        self._setup_heatpump_vat_mappings()

    def calculate_heatpump_system_price(
            self, system_config: dict[str, Any]) -> PricingResult:
        """Calculate complete heat pump system pricing

        Args:
            system_config: Heat pump system configuration with components and specifications

        Returns:
            PricingResult with heat pump system pricing
        """
        try:
            components = system_config.get("components", [])
            system_specs = system_config.get("system_specs", {})

            # Calculate base price with heat pump-specific logic
            base_result = self._calculate_heatpump_base_price(
                components, system_specs)

            # Add heat pump-specific validations
            self._validate_heatpump_configuration(components, system_specs)

            # Generate heat pump-specific system keys
            hp_system_keys = self._generate_heatpump_system_keys(
                base_result, system_specs)
            base_result.dynamic_keys.update(hp_system_keys)

            return base_result

        except Exception as e:
            self.logger.error(f"Error calculating heat pump system price: {e}")
            raise

    def _setup_heatpump_vat_mappings(self):
        """Set up heat pump-specific VAT category mappings"""
        try:
            # Map heat pump component categories to VAT categories
            hp_vat_mappings = {
                # Hardware components - standard VAT
                "Heat Pump": VATCategory.STANDARD,
                "Buffer Tank": VATCategory.STANDARD,
                "Expansion Tank": VATCategory.STANDARD,
                "Circulation Pump": VATCategory.STANDARD,
                "Controls": VATCategory.STANDARD,
                "Piping": VATCategory.STANDARD,
                "Electrical": VATCategory.STANDARD,
                "Insulation": VATCategory.STANDARD,

                # Services - standard VAT
                "Installation Service": VATCategory.STANDARD,
                "Planning Service": VATCategory.STANDARD,
                "Commissioning": VATCategory.STANDARD,
                "Maintenance": VATCategory.STANDARD,

                # Accessories - standard VAT
                "Accessories": VATCategory.STANDARD,
                "Tools": VATCategory.STANDARD,

                # Special categories
                "BEG Subsidy": VATCategory.EXEMPT,  # Subsidies are typically VAT exempt
                "Financing": VATCategory.EXEMPT     # Financial services are typically VAT exempt
            }

            for category, vat_category in hp_vat_mappings.items():
                self.vat_manager.set_category_vat_mapping(
                    category, vat_category)

            self.logger.info(
                f"Set up {
                    len(hp_vat_mappings)} heat pump VAT category mappings")

        except Exception as e:
            self.logger.error(f"Error setting up heat pump VAT mappings: {e}")

    def calculate_heatpump_system_vat(self,
                                      components: list[PriceComponent],
                                      beg_subsidy: float = 0.0,
                                      additional_costs: float = 0.0) -> dict[str,
                                                                             Any]:
        """Calculate VAT for heat pump system with BEG subsidy handling

        Args:
            components: List of heat pump price components
            beg_subsidy: BEG subsidy amount (typically VAT exempt)
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
                    "category": "Accessories"
                })

            # BEG subsidy is handled separately as it's typically VAT exempt
            # and reduces the net amount rather than being a separate line item

            # Calculate mixed VAT for components and additional costs
            vat_calculation = self.vat_manager.calculate_mixed_vat(vat_items)

            # Handle BEG subsidy (typically reduces net amount, no VAT impact)
            net_after_subsidy = max(
                0.0, vat_calculation.net_amount - beg_subsidy)
            vat_after_subsidy = vat_calculation.vat_amount  # VAT calculated on full amount
            gross_after_subsidy = net_after_subsidy + vat_after_subsidy

            return {
                "vat_calculation": vat_calculation,
                "component_breakdown": vat_calculation.breakdown.get(
                    "category_breakdowns",
                    {}),
                "total_net_before_subsidy": vat_calculation.net_amount,
                "beg_subsidy": beg_subsidy,
                "total_net_after_subsidy": net_after_subsidy,
                "total_vat": vat_after_subsidy,
                "total_gross_after_subsidy": gross_after_subsidy,
                "effective_vat_rate": vat_calculation.vat_rate_percent,
                "dynamic_keys": {
                    **vat_calculation.dynamic_keys,
                    "HP_BEG_SUBSIDY": beg_subsidy,
                    "HP_NET_AFTER_SUBSIDY": net_after_subsidy,
                    "HP_GROSS_AFTER_SUBSIDY": gross_after_subsidy}}

        except Exception as e:
            self.logger.error(f"Error calculating heat pump system VAT: {e}")
            # Fallback to simple VAT calculation
            total_net = sum(
                comp.total_price for comp in components) + additional_costs
            fallback_vat = self.vat_manager.calculate_vat(
                total_net, "Heat Pump")
            net_after_subsidy = max(0.0, total_net - beg_subsidy)
            return {
                "vat_calculation": fallback_vat,
                "component_breakdown": {},
                "total_net_before_subsidy": total_net,
                "beg_subsidy": beg_subsidy,
                "total_net_after_subsidy": net_after_subsidy,
                "total_vat": fallback_vat.vat_amount,
                "total_gross_after_subsidy": net_after_subsidy +
                fallback_vat.vat_amount,
                "effective_vat_rate": fallback_vat.vat_rate_percent,
                "dynamic_keys": fallback_vat.dynamic_keys}

    def _calculate_heatpump_base_price(self, components: list[dict[str, Any]],
                                       system_specs: dict[str, Any]) -> PricingResult:
        """Calculate base price with heat pump-specific logic"""
        hp_components = []
        total_base_price = 0.0
        all_dynamic_keys = {}

        # Extract system-level specifications
        heating_demand_kw = system_specs.get("heating_demand_kw", 0.0)
        building_type = system_specs.get("building_type", "residential")

        for comp_data in components:
            # Get product information
            product = self._get_product_info(comp_data)
            if not product:
                self.logger.warning(
                    f"Heat pump product not found: {comp_data}")
                continue

            # Determine component category
            category = self._classify_heatpump_component(product)

            # Create heat pump-specific price component
            hp_comp = self._create_heatpump_price_component(
                product, comp_data, system_specs, category
            )
            hp_components.append(hp_comp)

            # Calculate price using heat pump-specific logic
            component_price = self._calculate_heatpump_component_price(
                hp_comp, system_specs
            )
            total_base_price += component_price

            # Merge dynamic keys
            all_dynamic_keys.update(hp_comp.dynamic_keys)

        # Generate system-level keys
        system_keys = self._generate_heatpump_system_keys_base(
            total_base_price, hp_components, system_specs
        )
        all_dynamic_keys.update(system_keys)

        return PricingResult(
            base_price=total_base_price,
            components=hp_components,
            dynamic_keys=all_dynamic_keys,
            metadata={
                "system_type": "heatpump",
                "component_count": len(hp_components),
                "heating_demand_kw": heating_demand_kw,
                "building_type": building_type,
                "calculation_method": "heatpump_specific"
            }
        )

    def _classify_heatpump_component(self, product: dict[str, Any]) -> str:
        """Classify heat pump component based on product data"""
        category = product.get("category", "").lower()
        model_name = product.get("model_name", "").lower()

        # First check category (more reliable than model name)
        for hp_cat, keywords in HEATPUMP_CATEGORIES.items():
            if any(keyword in category for keyword in keywords):
                return hp_cat

        # Then check model name if category didn't match
        for hp_cat, keywords in HEATPUMP_CATEGORIES.items():
            if any(keyword in model_name for keyword in keywords):
                return hp_cat

        # Default classification based on product attributes
        if product.get("power_kw") and (
                "wärme" in model_name or "heat" in model_name):
            return "heatpump"
        if product.get(
                "labor_hours") or "installation" in model_name or "service" in model_name:
            return "installation"
        if "speicher" in category or "boiler" in category or "storage" in category:
            return "storage"
        return "accessories"

    def _create_heatpump_price_component(self,
                                         product: dict[str,
                                                       Any],
                                         comp_data: dict[str,
                                                         Any],
                                         system_specs: dict[str,
                                                            Any],
                                         category: str) -> HeatPumpPriceComponent:
        """Create heat pump-specific price component"""
        # Determine installation complexity
        installation_complexity = self._determine_installation_complexity(
            product, system_specs
        )

        # Extract heat pump-specific attributes
        heating_capacity_kw = product.get("power_kw")
        cop_rating = self._extract_cop_rating(product)
        refrigerant_type = self._extract_refrigerant_type(product)
        labor_hours = product.get("labor_hours", 0.0)
        beg_eligible = self._determine_beg_eligibility(product)

        return HeatPumpPriceComponent(
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

            # Heat pump-specific fields
            heating_capacity_kw=heating_capacity_kw,
            cop_rating=cop_rating,
            refrigerant_type=refrigerant_type,
            installation_complexity=installation_complexity,
            labor_hours_required=labor_hours,
            beg_eligible=beg_eligible
        )

    def _determine_installation_complexity(
            self, product: dict[str, Any], system_specs: dict[str, Any]) -> str:
        """Determine installation complexity based on product and system specs"""
        building_type = system_specs.get("building_type", "residential")
        existing_heating = system_specs.get("existing_heating_system", "none")

        # Complex installations
        if building_type == "commercial" or existing_heating == "oil":
            return "complex"

        # Medium complexity
        if existing_heating in [
                "gas", "electric"] or system_specs.get(
                "requires_electrical_upgrade", False):
            return "medium"

        # Simple installations
        return "simple"

    def _extract_cop_rating(self, product: dict[str, Any]) -> float | None:
        """Extract COP rating from product data"""
        # Check if COP is directly specified
        if "cop" in product:
            return float(product["cop"])

        # Try to extract from description or model name
        description = (
            product.get(
                "description",
                "") +
            " " +
            product.get(
                "model_name",
                "")).lower()

        # Look for COP patterns in text
        import re
        cop_match = re.search(r'cop[:\s]*(\d+\.?\d*)', description)
        if cop_match:
            return float(cop_match.group(1))

        # Default based on technology if available
        technology = product.get("technology", "").lower()
        if "inverter" in technology:
            return 4.2  # Typical for inverter heat pumps
        if "luft" in technology or "air" in technology:
            return 3.8  # Typical for air source

        return None

    def _extract_refrigerant_type(self, product: dict[str, Any]) -> str | None:
        """Extract refrigerant type from product data"""
        # Check direct field
        if "refrigerant" in product:
            return product["refrigerant"]

        # Extract from description
        description = (
            product.get(
                "description",
                "") +
            " " +
            product.get(
                "model_name",
                "")).lower()

        # Common refrigerant types
        refrigerants = ["r32", "r410a", "r290", "r744", "co2"]
        for ref in refrigerants:
            if ref in description:
                return ref.upper()

        return None

    def _determine_beg_eligibility(self, product: dict[str, Any]) -> bool:
        """Determine BEG subsidy eligibility"""
        # Heat pumps are generally BEG eligible
        category = product.get("category", "").lower()
        if any(
                keyword in category for keyword in HEATPUMP_CATEGORIES["heatpump"]):
            return True

        # Check for efficiency requirements
        cop_rating = self._extract_cop_rating(product)
        if cop_rating and cop_rating >= 3.5:
            return True

        return False

    def _calculate_heatpump_component_price(self, component: HeatPumpPriceComponent,
                                            system_specs: dict[str, Any]) -> float:
        """Calculate component price using heat pump-specific logic"""
        base_price = component.price_euro
        quantity = component.quantity
        calculate_per = component.calculate_per or "Stück"

        # Use enhanced calculation method
        product_specs = {
            "power_kw": component.power_kw,
            "heating_capacity_kw": component.heating_capacity_kw,
            "labor_hours": component.labor_hours_required
        }

        total_price = calculate_price_by_method(
            base_price, quantity, calculate_per, product_specs
        )

        # Apply COP-based adjustments
        total_price = self._apply_cop_adjustments(component, total_price)

        # Apply refrigerant-based adjustments
        total_price = self._apply_refrigerant_adjustments(
            component, total_price)

        return total_price

    def _apply_cop_adjustments(self, component: HeatPumpPriceComponent,
                               base_price: float) -> float:
        """Apply COP-based pricing adjustments"""
        if not component.cop_rating:
            return base_price

        # High-efficiency premium
        if component.cop_rating >= 4.5:
            return base_price * 1.1  # 10% premium for very high efficiency
        if component.cop_rating >= 4.0:
            return base_price * 1.05  # 5% premium for high efficiency

        return base_price

    def _apply_refrigerant_adjustments(self, component: HeatPumpPriceComponent,
                                       base_price: float) -> float:
        """Apply refrigerant-based pricing adjustments"""
        if not component.refrigerant_type:
            return base_price

        refrigerant = component.refrigerant_type.lower()

        # Natural refrigerant premium (eligible for BEG bonus)
        if refrigerant in ["r290", "r744", "co2"]:
            return base_price * 1.08  # 8% premium for natural refrigerants
        if refrigerant == "r32":
            return base_price * 1.02  # 2% premium for R32 (lower GWP)

        return base_price

    def _generate_heatpump_system_keys_base(self,
                                            total_price: float,
                                            components: list[HeatPumpPriceComponent],
                                            system_specs: dict[str,
                                                               Any]) -> dict[str,
                                                                             Any]:
        """Generate heat pump system-level dynamic keys"""
        system_keys = {
            "HP_BASE_PRICE_NET": total_price,
            "HP_COMPONENT_COUNT": len(components),
            "HP_SYSTEM_TYPE": "heatpump"
        }

        # Calculate category totals
        category_totals = {}
        total_heating_capacity = 0.0
        total_labor_hours = 0.0
        beg_eligible_components = 0

        for comp in components:
            cat = comp.category
            if cat not in category_totals:
                category_totals[cat] = 0.0
            category_totals[cat] += comp.total_price

            # Track system specifications
            if comp.heating_capacity_kw:
                total_heating_capacity += comp.heating_capacity_kw

            if comp.labor_hours_required:
                total_labor_hours += comp.labor_hours_required * \
                    (comp.quantity or 1)

            if comp.beg_eligible:
                beg_eligible_components += 1

        # Add category totals
        for category, total in category_totals.items():
            safe_cat = self.key_manager._create_safe_key_name(category)
            system_keys[f"HP_{safe_cat.upper()}_TOTAL"] = total

        # Add system specifications
        system_keys.update({
            "HP_TOTAL_HEATING_CAPACITY_KW": total_heating_capacity,
            "HP_TOTAL_LABOR_HOURS": total_labor_hours,
            "HP_TOTAL_LABOR_COST": total_labor_hours * self.labor_rate,
            "HP_BEG_ELIGIBLE_COMPONENTS": beg_eligible_components,
            "HP_BUILDING_TYPE": system_specs.get("building_type", "residential"),
            "HP_HEATING_DEMAND_KW": system_specs.get("heating_demand_kw", 0.0)
        })

        return system_keys

    def _generate_heatpump_system_keys(self,
                                       base_result: PricingResult,
                                       system_specs: dict[str,
                                                          Any]) -> dict[str,
                                                                        Any]:
        """Generate additional heat pump system keys"""
        hp_keys = {}

        # Performance calculations
        total_heating_capacity = system_specs.get("heating_demand_kw", 0.0)
        if total_heating_capacity > 0:
            # Price per kW heating capacity
            price_per_kw = base_result.base_price / total_heating_capacity
            hp_keys["HP_PRICE_PER_KW_HEATING"] = round(price_per_kw, 2)

            # Estimated annual energy consumption (rough calculation)
            annual_hours = 2000  # Typical heating hours per year
            avg_cop = self._calculate_average_cop(base_result.components)
            if avg_cop:
                annual_consumption_kwh = (
                    total_heating_capacity * annual_hours) / avg_cop
                hp_keys["HP_ESTIMATED_ANNUAL_CONSUMPTION_KWH"] = round(
                    annual_consumption_kwh, 0)

        # System efficiency indicators
        avg_cop = self._calculate_average_cop(base_result.components)
        if avg_cop:
            hp_keys["HP_AVERAGE_COP"] = round(avg_cop, 2)

        # BEG eligibility assessment
        beg_eligible_ratio = self._calculate_beg_eligibility_ratio(
            base_result.components)
        hp_keys["HP_BEG_ELIGIBILITY_RATIO"] = round(beg_eligible_ratio, 2)

        return hp_keys

    def _calculate_average_cop(
            self,
            components: list[HeatPumpPriceComponent]) -> float | None:
        """Calculate weighted average COP of heat pump components"""
        total_capacity = 0.0
        weighted_cop = 0.0

        for comp in components:
            if (comp.category == "heatpump" and
                comp.cop_rating and
                    comp.heating_capacity_kw):

                capacity = comp.heating_capacity_kw * (comp.quantity or 1)
                total_capacity += capacity
                weighted_cop += comp.cop_rating * capacity

        if total_capacity > 0:
            return weighted_cop / total_capacity

        return None

    def _calculate_beg_eligibility_ratio(
            self, components: list[HeatPumpPriceComponent]) -> float:
        """Calculate ratio of BEG-eligible components"""
        if not components:
            return 0.0

        eligible_count = sum(1 for comp in components if comp.beg_eligible)
        return eligible_count / len(components)

    def _validate_heatpump_configuration(
            self, components: list[dict[str, Any]], system_specs: dict[str, Any]):
        """Validate heat pump system configuration"""
        # Check for required components
        has_heatpump = any(
            self._classify_heatpump_component(self._get_product_info(comp) or {}) == "heatpump"
            for comp in components
        )

        if not has_heatpump:
            self.logger.warning(
                "Heat pump system configuration missing main heat pump unit")

        # Validate capacity matching
        self._validate_heating_capacity_matching(components, system_specs)

    def _get_product_info(
            self, comp_data: dict[str, Any]) -> dict[str, Any] | None:
        """Get product information from database"""
        if "product_id" in comp_data:
            return get_product_by_id(comp_data["product_id"])
        if "model_name" in comp_data:
            return get_product_by_model_name(comp_data["model_name"])
        return None

    def _validate_heating_capacity_matching(
            self, components: list[dict[str, Any]], system_specs: dict[str, Any]):
        """Validate that heat pump capacity matches heating demand"""
        heating_demand = system_specs.get("heating_demand_kw", 0.0)
        if heating_demand <= 0:
            return

        total_capacity = 0.0
        for comp_data in components:
            product = self._get_product_info(comp_data)
            if not product:
                continue

            category = self._classify_heatpump_component(product)
            if category == "heatpump" and product.get("power_kw"):
                quantity = comp_data.get("quantity", 1)
                total_capacity += product["power_kw"] * quantity

        if total_capacity > 0:
            ratio = total_capacity / heating_demand
            if ratio < 0.8 or ratio > 1.5:
                self.logger.warning(
                    f"Heat pump capacity mismatch: demand {heating_demand}kW, "
                    f"capacity {total_capacity}kW (ratio: {ratio:.2f})"
                )

    def calculate_beg_subsidy_integration(self, pricing_result: PricingResult,
                                          beg_config: dict[str, Any]) -> dict[str, Any]:
        """Calculate BEG subsidy with integration to pricing system"""
        try:
            # Extract BEG configuration
            use_natural_refrigerant = beg_config.get(
                "natural_refrigerant", False)
            replace_old_heating = beg_config.get("replace_old_heating", False)
            low_income = beg_config.get("low_income", False)

            # Use existing BEG calculation
            beg_result = calculate_beg_subsidy(
                pricing_result.base_price,
                use_natural_refrigerant,
                replace_old_heating,
                low_income
            )

            # Generate BEG-specific dynamic keys with HP prefix
            hp_beg_keys = {
                "HP_BEG_SUBSIDY_PERCENT": beg_result.get(
                    "applied_pct",
                    0.0),
                "HP_BEG_SUBSIDY_AMOUNT": beg_result.get(
                    "subsidy_amount_net",
                    0.0),
                "HP_BEG_ELIGIBLE_COSTS": beg_result.get(
                    "eligible_costs_net",
                    0.0),
                "HP_BEG_FINAL_COST": beg_result.get(
                    "effective_total_after_subsidy_net",
                    0.0),
                "HP_BEG_NATURAL_REFRIGERANT": use_natural_refrigerant,
                "HP_BEG_REPLACE_OLD_HEATING": replace_old_heating,
                "HP_BEG_LOW_INCOME": low_income}

            return {
                "beg_calculation": beg_result,
                "dynamic_keys": hp_beg_keys,
                "integration_successful": True
            }

        except Exception as e:
            self.logger.error(
                f"Error calculating BEG subsidy integration: {e}")
            return {
                "beg_calculation": {},
                "dynamic_keys": {},
                "integration_successful": False,
                "error": str(e)
            }


# Convenience functions for external use
def create_enhanced_heatpump_pricing_engine() -> EnhancedHeatPumpPricingEngine:
    """Create a new enhanced heat pump pricing engine instance"""
    return EnhancedHeatPumpPricingEngine()


def calculate_heatpump_system_pricing(
        system_config: dict[str, Any]) -> PricingResult:
    """Calculate heat pump system pricing using the enhanced pricing engine

    Args:
        system_config: Heat pump system configuration

    Returns:
        PricingResult with complete heat pump system pricing
    """
    engine = create_enhanced_heatpump_pricing_engine()
    return engine.calculate_heatpump_system_price(system_config)


__all__ = [
    "HeatPumpPriceComponent",
    "EnhancedHeatPumpPricingEngine",
    "create_enhanced_heatpump_pricing_engine",
    "calculate_heatpump_system_pricing",
    "HEATPUMP_CATEGORIES"
]
