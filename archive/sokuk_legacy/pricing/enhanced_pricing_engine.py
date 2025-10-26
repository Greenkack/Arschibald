"""Enhanced Pricing Engine

Core pricing calculation engine with dynamic key generation that leverages
all existing product fields from the comprehensive product database.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:
    from product_db import get_product_by_id, get_product_by_model_name, list_products
except ImportError:
    # Fallback for testing without database
    def get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return None

    def get_product_by_model_name(model_name: str) -> dict[str, Any] | None:
        return None

    def list_products(category: str | None = None,
                      company_id: int | None = None) -> list[dict[str, Any]]:
        return []

from .dynamic_key_manager import DynamicKeyManager
from .pricing_audit import (
    audit_price_calculation,
    audit_pricing_error,
    get_calculation_logger,
)
from .pricing_cache import get_cache_manager
from .pricing_errors import (
    ProductNotFoundError,
    ValidationError,
    safe_pricing_operation,
)
from .pricing_validation import ValidationSeverity, get_pricing_validator
from .vat_manager import VATCalculation, get_vat_manager

logger = logging.getLogger(__name__)


@dataclass
class PriceComponent:
    """Represents a single pricing component with all product fields"""
    product_id: int
    model_name: str
    category: str
    brand: str | None = None
    quantity: int = 1

    # Core pricing fields
    price_euro: float = 0.0
    # "Stück", "Meter", "pauschal", "kWp", etc.
    calculate_per: str | None = None

    # Technical specifications
    capacity_w: float | None = None
    storage_power_kw: float | None = None
    power_kw: float | None = None
    max_cycles: int | None = None
    warranty_years: int | None = None

    # Enhanced product attributes
    technology: str | None = None
    feature: str | None = None
    design: str | None = None
    upgrade: str | None = None
    max_kwh_capacity: float | None = None
    outdoor_opt: bool | None = None
    self_supply_feature: bool | None = None
    shadow_fading: bool | None = None
    smart_home: bool | None = None

    # Physical dimensions
    length_m: float | None = None
    width_m: float | None = None
    weight_kg: float | None = None
    efficiency_percent: float | None = None

    # Additional information
    origin_country: str | None = None
    description: str | None = None
    pros: str | None = None
    cons: str | None = None
    rating: float | None = None

    # Calculated fields
    unit_price: float = field(init=False)
    total_price: float = field(init=False)
    dynamic_keys: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Calculate derived fields after initialization"""
        self.unit_price = self._calculate_unit_price()
        self.total_price = self._calculate_total_price()
        self.dynamic_keys = self._generate_component_keys()

    def _calculate_unit_price(self) -> float:
        """Calculate unit price based on calculate_per method using enhanced engine"""
        try:
            from .calculate_per_engine import CalculatePerEngine, CalculationContext

            # Create calculation context
            context = CalculationContext(
                capacity_w=self.capacity_w,
                power_kw=self.power_kw,
                efficiency_percent=self.efficiency_percent,
                length_m=self.length_m,
                width_m=self.width_m,
                technology=self.technology,
                feature=self.feature,
                design=self.design,
                upgrade=self.upgrade,
                category=self.category,
                brand=self.brand
            )

            # Use enhanced engine for calculation
            engine = CalculatePerEngine()
            result = engine.calculate_price(
                self.price_euro, 1, self.calculate_per or "Stück", context)

            return result.unit_price

        except ImportError:
            # Fallback to legacy calculation
            return self._legacy_calculate_unit_price()
        except Exception:
            # Fallback on any error
            return self._legacy_calculate_unit_price()

    def _calculate_total_price(self) -> float:
        """Calculate total price based on quantity and calculation method using enhanced engine"""
        try:
            from .calculate_per_engine import CalculatePerEngine, CalculationContext

            # Create calculation context
            context = CalculationContext(
                capacity_w=self.capacity_w,
                power_kw=self.power_kw,
                efficiency_percent=self.efficiency_percent,
                length_m=self.length_m,
                width_m=self.width_m,
                technology=self.technology,
                feature=self.feature,
                design=self.design,
                upgrade=self.upgrade,
                category=self.category,
                brand=self.brand
            )

            # Use enhanced engine for calculation
            engine = CalculatePerEngine()
            result = engine.calculate_price(
                self.price_euro,
                self.quantity,
                self.calculate_per or "Stück",
                context)

            # Store additional information from enhanced calculation
            if hasattr(self, '_enhanced_result'):
                self._enhanced_result = result

            return result.total_price

        except ImportError:
            # Fallback to legacy calculation
            return self._legacy_calculate_total_price()
        except Exception:
            # Fallback on any error
            return self._legacy_calculate_total_price()

    def _legacy_calculate_unit_price(self) -> float:
        """Legacy unit price calculation for fallback"""
        if not self.calculate_per or self.calculate_per.lower() in [
            "stück", "piece"] or self.calculate_per.lower() in [
            "meter", "m"] or self.calculate_per.lower() in [
                "pauschal", "lump_sum"]:
            return self.price_euro
        if self.calculate_per.lower() in ["kwp"]:
            if self.capacity_w:
                return self.price_euro * (self.capacity_w / 1000.0)
            return self.price_euro
        return self.price_euro

    def _legacy_calculate_total_price(self) -> float:
        """Legacy total price calculation for fallback"""
        if not self.calculate_per or self.calculate_per.lower() in [
                "stück",
                "piece"] or self.calculate_per.lower() in [
                "meter",
                "m"]:
            return self.unit_price * self.quantity
        if self.calculate_per.lower() in ["pauschal", "lump_sum"]:
            return self.unit_price
        if self.calculate_per.lower() in ["kwp"]:
            return self.unit_price * self.quantity
        return self.unit_price * self.quantity

    def _generate_component_keys(self) -> dict[str, Any]:
        """Generate dynamic keys for this component"""
        key_manager = DynamicKeyManager()

        # Create safe key name from model name
        safe_name = key_manager._create_safe_key_name(self.model_name)

        keys = {
            f"{safe_name}_UNIT_PRICE": self.unit_price,
            f"{safe_name}_QUANTITY": self.quantity,
            f"{safe_name}_TOTAL_PRICE": self.total_price,
            f"{safe_name}_CATEGORY": self.category,
            f"{safe_name}_BRAND": self.brand or "",
            f"{safe_name}_CALCULATE_PER": self.calculate_per or "Stück"
        }

        # Add technical specifications if available
        if self.capacity_w:
            keys[f"{safe_name}_CAPACITY_W"] = self.capacity_w
        if self.power_kw:
            keys[f"{safe_name}_POWER_KW"] = self.power_kw
        if self.efficiency_percent:
            keys[f"{safe_name}_EFFICIENCY_PCT"] = self.efficiency_percent
        if self.warranty_years:
            keys[f"{safe_name}_WARRANTY_YEARS"] = self.warranty_years

        # Add enhanced attributes if available
        if self.technology:
            keys[f"{safe_name}_TECHNOLOGY"] = self.technology
        if self.feature:
            keys[f"{safe_name}_FEATURE"] = self.feature
        if self.design:
            keys[f"{safe_name}_DESIGN"] = self.design

        return keys


@dataclass
class PricingResult:
    """Result of pricing calculation with dynamic keys"""
    base_price: float
    components: list[PriceComponent]
    dynamic_keys: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    calculation_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FinalPricingResult(PricingResult):
    """Final pricing result with all modifications applied"""
    final_price_net: float = 0.0
    final_price_gross: float = 0.0
    total_discounts: float = 0.0
    total_surcharges: float = 0.0
    vat_amount: float = 0.0
    vat_rate_percent: float = 0.0
    vat_calculation: VATCalculation | None = None
    profit_margin: float = 0.0


class PricingEngine:
    """Core pricing calculation engine with dynamic key generation and intelligent caching"""

    def __init__(
            self,
            system_type: str = "pv",
            enable_caching: bool = True,
            country_code: str = "DE"):
        """Initialize pricing engine for specific system type

        Args:
            system_type: Type of system ("pv", "heatpump", "combined")
            enable_caching: Whether to enable intelligent caching
            country_code: Country code for VAT calculations (default: DE)
        """
        self.system_type = system_type.lower()
        self.key_manager = DynamicKeyManager()
        self.logger = logging.getLogger(f"{__name__}.{system_type}")
        self.enable_caching = enable_caching
        self.country_code = country_code.upper()

        # Initialize cache manager if caching is enabled
        if self.enable_caching:
            self.cache_manager = get_cache_manager()
        else:
            self.cache_manager = None

        # Initialize VAT manager
        self.vat_manager = get_vat_manager(country_code)

        # Validate system type
        if self.system_type not in ["pv", "heatpump", "combined"]:
            raise ValueError(
                f"Invalid system_type: {system_type}. Must be 'pv', 'heatpump', or 'combined'")

    @safe_pricing_operation("calculate_base_price", "pricing_engine")
    def calculate_base_price(
            self, components: list[dict[str, Any]]) -> PricingResult:
        """Calculate base price from component list with intelligent caching

        Args:
            components: List of component dictionaries with product info and quantities

        Returns:
            PricingResult with base pricing calculation
        """
        start_time = datetime.now()

        try:
            # Validate input components
            validator = get_pricing_validator()
            for i, component in enumerate(components):
                validation_result = validator.validate_component_data(
                    component)
                if not validation_result.is_valid:
                    error_messages = [
                        issue.message for issue in validation_result.errors]
                    raise ValidationError(
                        f"Component {i} validation failed: {
                            '; '.join(error_messages)}", context={
                            "component_index": i, "validation_issues": [
                                issue.to_dict() for issue in validation_result.issues]})
            # Check cache if enabled
            if self.cache_manager:
                cache_key = self.cache_manager.generate_system_key(
                    components, self.system_type)
                cached_result = self.cache_manager.get_system_pricing(
                    cache_key)
                if cached_result:
                    self.logger.debug(
                        f"Cache hit for base price calculation: {cache_key}")
                    return cached_result

            price_components = []
            total_base_price = 0.0
            all_dynamic_keys = {}
            component_cache_keys = []

            for comp_data in components:
                # Check component-level cache
                component_key = None
                if self.cache_manager:
                    product_id = comp_data.get('product_id', 0)
                    quantity = comp_data.get('quantity', 1)
                    component_key = self.cache_manager.generate_component_key(
                        product_id, quantity)
                    cached_component = self.cache_manager.get_component_pricing(
                        component_key)

                    if cached_component:
                        price_components.append(cached_component)
                        total_base_price += cached_component.total_price
                        all_dynamic_keys.update(cached_component.dynamic_keys)
                        component_cache_keys.append(component_key)
                        continue

                # Get product information
                product = self._get_product_info(comp_data)
                if not product:
                    product_id = comp_data.get(
                        'product_id', comp_data.get(
                            'model_name', 'unknown'))
                    raise ProductNotFoundError(
                        product_identifier=product_id,
                        context={"component_data": comp_data}
                    )

                # Validate product data
                validator = get_pricing_validator()
                product_validation = validator.validate_product_data(product)
                if not product_validation.is_valid:
                    # Log validation warnings but continue
                    for warning in product_validation.warnings:
                        self.logger.warning(
                            f"Product validation warning: {
                                warning.message}")

                    # Raise error only for critical validation failures
                    if any(
                            error.severity == ValidationSeverity.ERROR for error in product_validation.errors):
                        error_messages = [
                            error.message for error in product_validation.errors]
                        raise ValidationError(
                            f"Product validation failed: {
                                '; '.join(error_messages)}", context={
                                "product_id": product.get('id'), "validation_issues": [
                                    issue.to_dict() for issue in product_validation.issues]})

                # Create price component with all product fields
                price_comp = self._create_price_component(product, comp_data)
                price_components.append(price_comp)

                # Cache component if caching enabled
                if self.cache_manager and component_key:
                    self.cache_manager.cache_component_pricing(
                        component_key, price_comp)
                    component_cache_keys.append(component_key)

                # Add to total
                total_base_price += price_comp.total_price

                # Merge dynamic keys
                all_dynamic_keys.update(price_comp.dynamic_keys)

            # Generate system-level keys
            system_keys = self._generate_system_keys(
                total_base_price, price_components)
            all_dynamic_keys.update(system_keys)

            result = PricingResult(
                base_price=total_base_price,
                components=price_components,
                dynamic_keys=all_dynamic_keys,
                metadata={
                    "system_type": self.system_type,
                    "component_count": len(price_components),
                    "calculation_method": "base_price",
                    "cached": False
                }
            )

            # Cache system-level result
            if self.cache_manager:
                cache_key = self.cache_manager.generate_system_key(
                    components, self.system_type)
                self.cache_manager.cache_system_pricing(
                    cache_key, result, component_cache_keys)

            # Log successful calculation
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            calc_logger = get_calculation_logger()
            calc_logger.log_calculation_complete(
                {"base_price": total_base_price, "component_count": len(price_components)},
                duration_ms
            )

            return result

        except Exception as e:
            # Log calculation error
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            calc_logger = get_calculation_logger()
            calc_logger.log_calculation_error(e, {"components": components})

            self.logger.error(f"Error calculating base price: {e}")
            raise

    def apply_modifications(self, base_price: float,
                            modifications: dict[str, Any]) -> dict[str, Any]:
        """Apply discounts, surcharges, and other modifications

        Args:
            base_price: Base price before modifications
            modifications: Dictionary with discount/surcharge configuration

        Returns:
            Dictionary with modification results and dynamic keys
        """
        try:
            # Extract modification parameters
            discount_pct = modifications.get("discount_percent", 0.0)
            discount_fixed = modifications.get("discount_fixed", 0.0)
            surcharge_pct = modifications.get("surcharge_percent", 0.0)
            surcharge_fixed = modifications.get("surcharge_fixed", 0.0)
            accessories_cost = modifications.get("accessories_cost", 0.0)

            # Apply pricing formula: (Matrix Price + Accessories) × (1 -
            # Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed
            # Surcharges
            price_with_accessories = base_price + accessories_cost

            # Apply percentage-based modifications
            discount_amount_pct = price_with_accessories * \
                (discount_pct / 100.0)
            price_after_discount_pct = price_with_accessories - discount_amount_pct

            surcharge_amount_pct = price_after_discount_pct * \
                (surcharge_pct / 100.0)
            price_after_surcharge_pct = price_after_discount_pct + surcharge_amount_pct

            # Apply fixed modifications
            final_price = price_after_surcharge_pct - discount_fixed + surcharge_fixed

            # Ensure price doesn't go negative
            final_price = max(0.0, final_price)

            # Calculate totals
            total_discounts = discount_amount_pct + discount_fixed
            total_surcharges = surcharge_amount_pct + surcharge_fixed

            # Generate modification keys
            mod_keys = self.key_manager.generate_keys({
                "DISCOUNT_PERCENT": discount_pct,
                "DISCOUNT_PERCENT_AMOUNT": discount_amount_pct,
                "DISCOUNT_FIXED": discount_fixed,
                "SURCHARGE_PERCENT": surcharge_pct,
                "SURCHARGE_PERCENT_AMOUNT": surcharge_amount_pct,
                "SURCHARGE_FIXED": surcharge_fixed,
                "ACCESSORIES_COST": accessories_cost,
                "TOTAL_DISCOUNTS": total_discounts,
                "TOTAL_SURCHARGES": total_surcharges,
                "PRICE_AFTER_MODIFICATIONS": final_price
            }, prefix=f"{self.system_type.upper()}")

            return {
                "original_price": base_price,
                "accessories_cost": accessories_cost,
                "price_with_accessories": price_with_accessories,
                "discount_percent": discount_pct,
                "discount_percent_amount": discount_amount_pct,
                "discount_fixed": discount_fixed,
                "surcharge_percent": surcharge_pct,
                "surcharge_percent_amount": surcharge_amount_pct,
                "surcharge_fixed": surcharge_fixed,
                "total_discounts": total_discounts,
                "total_surcharges": total_surcharges,
                "final_price": final_price,
                "dynamic_keys": mod_keys
            }

        except Exception as e:
            self.logger.error(f"Error applying modifications: {e}")
            raise

    @safe_pricing_operation("generate_final_price", "pricing_engine")
    def generate_final_price(self,
                             calculation_data: dict[str,
                                                    Any]) -> FinalPricingResult:
        """Generate final pricing result with all calculations and intelligent caching

        Args:
            calculation_data: Complete calculation data including components and modifications

        Returns:
            FinalPricingResult with complete pricing information
        """
        start_time = datetime.now()

        try:
            # Validate complete calculation data
            validator = get_pricing_validator()
            validation_result = validator.validate_pricing_calculation_data(
                calculation_data)
            if not validation_result.is_valid:
                error_messages = [
                    issue.message for issue in validation_result.errors]
                raise ValidationError(
                    f"Calculation data validation failed: {
                        '; '.join(error_messages)}", context={
                        "validation_issues": [
                            issue.to_dict() for issue in validation_result.issues]})

            # Log validation warnings
            for warning in validation_result.warnings:
                self.logger.warning(
                    f"Calculation validation warning: {
                        warning.message}")
            # Check cache for final pricing if enabled
            if self.cache_manager:
                final_cache_key = self.cache_manager.generate_final_key(
                    calculation_data)
                cached_final = self.cache_manager.get_final_pricing(
                    final_cache_key)
                if cached_final:
                    self.logger.debug(
                        f"Cache hit for final price calculation: {final_cache_key}")
                    # Update metadata to indicate cache hit
                    cached_final.metadata["cached"] = True
                    return cached_final

            # Calculate base price
            components = calculation_data.get("components", [])
            base_result = self.calculate_base_price(components)

            # Apply modifications
            modifications = calculation_data.get("modifications", {})
            mod_result = self.apply_modifications(
                base_result.base_price, modifications)

            # Calculate VAT using VAT manager
            final_price_net = mod_result["final_price"]

            # Get VAT configuration from calculation data
            vat_config = calculation_data.get("vat_config", {})
            vat_rate_override = vat_config.get("vat_rate_override")
            use_mixed_vat = vat_config.get("use_mixed_vat", True)

            # Calculate VAT based on configuration
            if vat_rate_override is not None:
                # Use override rate for entire amount
                vat_calculation = self.vat_manager.calculate_vat(
                    net_amount=final_price_net,
                    vat_rate_override=vat_rate_override
                )
                primary_category = "Override"
            elif use_mixed_vat and len(base_result.components) > 0:
                # Use mixed VAT calculation based on component categories
                # First calculate VAT for base components
                component_vat = self.calculate_mixed_vat_for_components(
                    base_result.components)

                # Then calculate VAT for any additional costs (accessories,
                # modifications)
                additional_net = final_price_net - base_result.base_price
                if additional_net > 0:
                    # Apply standard VAT to additional costs
                    additional_vat = self.vat_manager.calculate_vat(
                        additional_net)

                    # Combine VAT calculations
                    total_net = component_vat.net_amount + additional_vat.net_amount
                    total_vat = component_vat.vat_amount + additional_vat.vat_amount
                    total_gross = total_net + total_vat
                    effective_rate = (
                        total_vat / total_net * 100.0) if total_net > 0 else 0.0

                    # Create combined VAT calculation
                    vat_calculation = VATCalculation(
                        net_amount=total_net,
                        vat_rate_percent=effective_rate,
                        vat_amount=total_vat,
                        gross_amount=total_gross,
                        vat_category=component_vat.vat_category,
                        breakdown={
                            "component_vat": component_vat.breakdown,
                            "additional_vat": additional_vat.breakdown,
                            "calculation_type": "mixed_with_additional"},
                        dynamic_keys={
                            **component_vat.dynamic_keys,
                            **additional_vat.dynamic_keys})
                else:
                    vat_calculation = component_vat

                primary_category = "Mixed Categories"
            else:
                # Use single category VAT calculation
                component_categories = [
                    comp.category for comp in base_result.components if comp.category]
                if component_categories:
                    primary_category = component_categories[0]
                else:
                    primary_category = "PV Module" if self.system_type == "pv" else "Heat Pump"

                vat_calculation = self.vat_manager.calculate_vat(
                    net_amount=final_price_net,
                    product_category=primary_category
                )

            vat_amount = vat_calculation.vat_amount
            final_price_gross = vat_calculation.gross_amount
            vat_rate = vat_calculation.vat_rate_percent

            # Generate final keys
            final_keys = base_result.dynamic_keys.copy()
            final_keys.update(mod_result["dynamic_keys"])

            # Add VAT-related dynamic keys
            final_keys.update(vat_calculation.dynamic_keys)

            # Add final pricing keys
            final_pricing_keys = self.key_manager.generate_keys({
                "FINAL_PRICE_NET": final_price_net,
                "VAT_RATE": vat_rate,
                "VAT_AMOUNT": vat_amount,
                "FINAL_PRICE_GROSS": final_price_gross,
                "VAT_CATEGORY": vat_calculation.vat_category.value
            }, prefix=f"{self.system_type.upper()}")

            final_keys.update(final_pricing_keys)

            # Validate final pricing result
            final_result_data = {
                "base_price": base_result.base_price,
                "final_price_net": final_price_net,
                "final_price_gross": final_price_gross,
                "vat_amount": vat_amount,
                "total_discounts": mod_result["total_discounts"],
                "total_surcharges": mod_result["total_surcharges"]
            }

            final_validation = validator.validate_final_pricing_result(
                final_result_data)
            if not final_validation.is_valid:
                error_messages = [
                    issue.message for issue in final_validation.errors]
                raise ValidationError(
                    f"Final pricing result validation failed: {
                        '; '.join(error_messages)}", context={
                        "final_result": final_result_data, "validation_issues": [
                            issue.to_dict() for issue in final_validation.issues]})

            result = FinalPricingResult(
                base_price=base_result.base_price,
                components=base_result.components,
                dynamic_keys=final_keys,
                metadata={
                    **base_result.metadata,
                    "has_modifications": bool(modifications),
                    "vat_rate": vat_rate,
                    "vat_category": vat_calculation.vat_category.value,
                    "primary_category": primary_category,
                    "calculation_complete": True,
                    "cached": False
                },
                final_price_net=final_price_net,
                final_price_gross=final_price_gross,
                total_discounts=mod_result["total_discounts"],
                total_surcharges=mod_result["total_surcharges"],
                vat_amount=vat_amount,
                vat_rate_percent=vat_rate,
                vat_calculation=vat_calculation,
                profit_margin=0.0  # Will be calculated by profit margin manager
            )

            # Cache final result
            if self.cache_manager:
                final_cache_key = self.cache_manager.generate_final_key(
                    calculation_data)
                # Get system cache key as dependency
                system_cache_key = self.cache_manager.generate_system_key(
                    components, self.system_type)
                self.cache_manager.cache_final_pricing(
                    final_cache_key, result, system_cache_key)

            # Log successful final calculation
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            audit_price_calculation(
                calculation_data=calculation_data,
                result=final_result_data,
                duration_ms=duration_ms
            )

            return result

        except Exception as e:
            # Log calculation error
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            audit_pricing_error(e, calculation_data)

            self.logger.error(f"Error generating final price: {e}")
            raise

    def _get_product_info(
            self, comp_data: dict[str, Any]) -> dict[str, Any] | None:
        """Get product information from database"""
        if "product_id" in comp_data:
            return get_product_by_id(comp_data["product_id"])
        if "model_name" in comp_data:
            return get_product_by_model_name(comp_data["model_name"])
        return None

    def _create_price_component(
            self, product: dict[str, Any], comp_data: dict[str, Any]) -> PriceComponent:
        """Create PriceComponent from product data"""
        return PriceComponent(
            product_id=product.get("id", 0),
            model_name=product.get("model_name", ""),
            category=product.get("category", ""),
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
            rating=product.get("rating")
        )

    def _generate_system_keys(
            self, total_price: float, components: list[PriceComponent]) -> dict[str, Any]:
        """Generate system-level dynamic keys"""
        system_keys = self.key_manager.generate_keys({
            "BASE_PRICE_NET": total_price,
            "COMPONENT_COUNT": len(components),
            "SYSTEM_TYPE": self.system_type.upper()
        }, prefix=f"{self.system_type.upper()}")

        # Add category summaries
        category_totals = {}
        for comp in components:
            cat = comp.category
            if cat not in category_totals:
                category_totals[cat] = 0.0
            category_totals[cat] += comp.total_price

        for category, total in category_totals.items():
            safe_cat = self.key_manager._create_safe_key_name(category)
            system_keys[f"{self.system_type.upper()}_{safe_cat}_TOTAL"] = total

        return system_keys

    def calculate_mixed_vat_for_components(
            self, components: list[PriceComponent]) -> VATCalculation:
        """Calculate VAT for components with potentially different categories

        Args:
            components: List of price components

        Returns:
            VATCalculation with mixed category handling
        """
        try:
            # Group components by category for VAT calculation
            vat_items = []
            for comp in components:
                vat_items.append({
                    "net_amount": comp.total_price,
                    "category": comp.category
                })

            if not vat_items:
                # Return zero VAT calculation for empty components
                return self.vat_manager.calculate_vat(0.0)

            # Use mixed VAT calculation if multiple categories, otherwise
            # single calculation
            categories = set(item["category"] for item in vat_items)
            if len(categories) > 1:
                return self.vat_manager.calculate_mixed_vat(vat_items)
            # Single category - sum amounts and calculate once
            total_net = sum(item["net_amount"] for item in vat_items)
            category = next(iter(categories))
            return self.vat_manager.calculate_vat(total_net, category)

        except Exception as e:
            self.logger.error(
                f"Error calculating mixed VAT for components: {e}")
            # Fallback to standard VAT calculation
            total_net = sum(comp.total_price for comp in components)
            return self.vat_manager.calculate_vat(total_net)

    def validate_pricing_data(self, data: dict[str, Any]) -> bool:
        """Validate pricing calculation input data

        Args:
            data: Pricing calculation data to validate

        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required fields
            if "components" not in data:
                self.logger.error("Missing 'components' in pricing data")
                return False

            components = data["components"]
            if not isinstance(components, list):
                self.logger.error("'components' must be a list")
                return False

            if not components:
                self.logger.warning("Empty components list")
                return True  # Empty is valid, just results in zero price

            # Validate each component
            for i, comp in enumerate(components):
                if not isinstance(comp, dict):
                    self.logger.error(f"Component {i} must be a dictionary")
                    return False

                # Must have either product_id or model_name
                if "product_id" not in comp and "model_name" not in comp:
                    self.logger.error(
                        f"Component {i} must have 'product_id' or 'model_name'")
                    return False

                # Quantity must be positive
                quantity = comp.get("quantity", 1)
                if not isinstance(quantity, (int, float)) or quantity <= 0:
                    self.logger.error(
                        f"Component {i} quantity must be positive number")
                    return False

            # Validate modifications if present
            if "modifications" in data:
                modifications = data["modifications"]
                if not isinstance(modifications, dict):
                    self.logger.error("'modifications' must be a dictionary")
                    return False

                # Validate numeric fields
                numeric_fields = [
                    "discount_percent", "discount_fixed",
                    "surcharge_percent", "surcharge_fixed",
                    "accessories_cost"
                ]

                for field in numeric_fields:
                    if field in modifications:
                        value = modifications[field]
                        if not isinstance(value, (int, float)):
                            self.logger.error(
                                f"Modification '{field}' must be numeric")
                            return False

                        # Percentages should be reasonable
                        if field.endswith("_percent") and (
                                value < 0 or value > 100):
                            self.logger.warning(
                                f"Modification '{field}' outside normal range: {value}%")

            return True

        except Exception as e:
            self.logger.error(f"Error validating pricing data: {e}")
            return False

    def invalidate_cache(self, product_id: int | None = None,
                         system_type: str | None = None) -> int:
        """Invalidate pricing cache entries

        Args:
            product_id: Specific product ID to invalidate (all if None)
            system_type: Specific system type to invalidate (current if None)

        Returns:
            Number of cache entries invalidated
        """
        if not self.cache_manager:
            return 0

        invalidated_count = 0

        try:
            if product_id:
                # Invalidate specific product cache
                invalidated_count += self.cache_manager.invalidate_product_cache(
                    product_id)
                self.logger.info(
                    f"Invalidated cache for product_id: {product_id}")

            if system_type:
                # Invalidate specific system type cache
                invalidated_count += self.cache_manager.invalidate_system_cache(
                    system_type)
                self.logger.info(
                    f"Invalidated cache for system_type: {system_type}")
            elif not product_id:
                # Invalidate current system type cache if no specific targets
                invalidated_count += self.cache_manager.invalidate_system_cache(
                    self.system_type)
                self.logger.info(
                    f"Invalidated cache for current system_type: {
                        self.system_type}")

            return invalidated_count

        except Exception as e:
            self.logger.error(f"Error invalidating cache: {e}")
            return 0

    def clear_all_cache(self) -> int:
        """Clear all pricing cache entries

        Returns:
            Number of cache entries cleared
        """
        if not self.cache_manager:
            return 0

        try:
            cleared_count = self.cache_manager.cache.clear()
            self.logger.info(
                f"Cleared all pricing cache entries: {cleared_count}")
            return cleared_count

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return 0

    def get_cache_stats(self) -> dict[str, Any]:
        """Get current cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_manager:
            return {"caching_enabled": False}

        try:
            stats = self.cache_manager.cache.get_stats()
            return {
                "caching_enabled": True,
                "cache_stats": stats,
                "system_type": self.system_type
            }

        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"caching_enabled": True, "error": str(e)}
