"""Combined Pricing Engine

Pricing engine for combined PV + heat pump systems that handles
separate calculations for each system type and applies combined
system discounts and surcharges.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
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

from financial_calculations import calculate_discount_amount

from .enhanced_heatpump_pricing import EnhancedHeatPumpPricingEngine
from .enhanced_pricing_engine import PricingEngine, PricingResult
from .pv_pricing_engine import PVPricingEngine

logger = logging.getLogger(__name__)


@dataclass
class CombinedPricingResult:
    """Result of combined PV + heat pump pricing calculation"""
    pv_result: PricingResult | None = None
    heatpump_result: PricingResult | None = None
    combined_base_price: float = 0.0
    combined_final_price: float = 0.0
    system_synergy_discount: float = 0.0
    combined_dynamic_keys: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    calculation_timestamp: datetime = field(default_factory=datetime.now)


class CombinedPricingEngine(PricingEngine):
    """Combined pricing engine for PV + heat pump systems"""

    def __init__(self):
        """Initialize combined pricing engine"""
        super().__init__(system_type="combined")
        self.pv_engine = PVPricingEngine()
        self.heatpump_engine = EnhancedHeatPumpPricingEngine()
        self.logger = logging.getLogger(f"{__name__}.CombinedPricingEngine")

    def calculate_combined_system_price(
            self, system_config: dict[str, Any]) -> CombinedPricingResult:
        """Calculate complete combined system pricing

        Args:
            system_config: Combined system configuration with PV and heat pump components

        Returns:
            CombinedPricingResult with complete pricing breakdown
        """
        try:
            # Extract system configurations
            pv_config = system_config.get("pv_system", {})
            heatpump_config = system_config.get("heatpump_system", {})
            combined_specs = system_config.get("combined_specs", {})

            # Calculate individual system prices
            pv_result = None
            heatpump_result = None

            if pv_config.get("components"):
                pv_result = self.pv_engine.calculate_pv_system_price(pv_config)
                self.logger.info(
                    f"PV system calculated: {
                        pv_result.base_price} EUR")

            if heatpump_config.get("components"):
                heatpump_result = self.heatpump_engine.calculate_heatpump_system_price(
                    heatpump_config)
                self.logger.info(
                    f"Heat pump system calculated: {
                        heatpump_result.base_price} EUR")

            # Calculate combined pricing
            combined_result = self._calculate_combined_pricing(
                pv_result, heatpump_result, combined_specs
            )

            return combined_result

        except Exception as e:
            self.logger.error(f"Error calculating combined system price: {e}")
            raise

    def _calculate_combined_pricing(self,
                                    pv_result: PricingResult | None,
                                    heatpump_result: PricingResult | None,
                                    combined_specs: dict[str,
                                                         Any]) -> CombinedPricingResult:
        """Calculate combined pricing with synergies and discounts"""

        # Calculate base combined price
        combined_base_price = 0.0
        if pv_result:
            combined_base_price += pv_result.base_price
        if heatpump_result:
            combined_base_price += heatpump_result.base_price

        # Apply system synergy discount
        synergy_discount = self._calculate_system_synergy_discount(
            pv_result, heatpump_result, combined_specs
        )

        # Calculate final combined price
        combined_final_price = combined_base_price - synergy_discount

        # Apply combined system modifications
        combined_modifications = combined_specs.get("modifications", {})
        if combined_modifications:
            modification_result = self._apply_combined_modifications(
                combined_final_price, combined_modifications
            )
            combined_final_price = modification_result["final_price"]

        # Generate combined dynamic keys
        combined_keys = self._generate_combined_dynamic_keys(
            pv_result, heatpump_result, combined_base_price,
            combined_final_price, synergy_discount
        )

        # Create metadata
        metadata = {
            "system_type": "combined",
            "has_pv": pv_result is not None,
            "has_heatpump": heatpump_result is not None,
            "pv_capacity_kwp": self._extract_pv_capacity(pv_result),
            "heatpump_capacity_kw": self._extract_heatpump_capacity(heatpump_result),
            "synergy_discount_applied": synergy_discount > 0,
            "calculation_method": "combined_system"}

        return CombinedPricingResult(
            pv_result=pv_result,
            heatpump_result=heatpump_result,
            combined_base_price=combined_base_price,
            combined_final_price=combined_final_price,
            system_synergy_discount=synergy_discount,
            combined_dynamic_keys=combined_keys,
            metadata=metadata
        )

    def _calculate_system_synergy_discount(self,
                                           pv_result: PricingResult | None,
                                           heatpump_result: PricingResult | None,
                                           combined_specs: dict[str,
                                                                Any]) -> float:
        """Calculate discount for combined system synergies"""
        if not (pv_result and heatpump_result):
            return 0.0

        # Base synergy discount percentage
        base_synergy_discount_pct = combined_specs.get(
            "synergy_discount_percent", 5.0)

        # Additional discounts based on system integration
        integration_bonus = 0.0

        # Smart home integration bonus
        if self._has_smart_home_integration(pv_result, heatpump_result):
            integration_bonus += 2.0
            self.logger.info("Smart home integration bonus applied: +2%")

        # Energy management system bonus
        if combined_specs.get("energy_management_system", False):
            integration_bonus += 3.0
            self.logger.info("Energy management system bonus applied: +3%")

        # Storage system synergy bonus
        if self._has_storage_synergy(pv_result, heatpump_result):
            integration_bonus += 2.5
            self.logger.info("Storage system synergy bonus applied: +2.5%")

        # Calculate total discount
        total_discount_pct = base_synergy_discount_pct + integration_bonus

        # Cap maximum discount
        max_discount_pct = combined_specs.get(
            "max_synergy_discount_percent", 15.0)
        total_discount_pct = min(total_discount_pct, max_discount_pct)

        # Apply discount to combined base price
        combined_base = (pv_result.base_price if pv_result else 0.0) + \
            (heatpump_result.base_price if heatpump_result else 0.0)

        discount_amount = calculate_discount_amount(
            combined_base,
            total_discount_pct,
        )

        self.logger.info(
            f"System synergy discount: {total_discount_pct}% = {discount_amount} EUR")

        return discount_amount

    def _has_smart_home_integration(self, pv_result: PricingResult,
                                    heatpump_result: PricingResult) -> bool:
        """Check if both systems have smart home integration"""
        pv_smart = any(
            comp.smart_home for comp in pv_result.components
            if hasattr(comp, 'smart_home') and comp.smart_home
        )

        hp_smart = any(
            comp.smart_home for comp in heatpump_result.components
            if hasattr(comp, 'smart_home') and comp.smart_home
        )

        return pv_smart and hp_smart

    def _has_storage_synergy(self, pv_result: PricingResult,
                             heatpump_result: PricingResult) -> bool:
        """Check if systems have complementary storage capabilities"""
        # Check for PV battery storage
        pv_has_storage = any(
            comp.category == "storage" for comp in pv_result.components
        )

        # Check for heat pump thermal storage
        hp_has_storage = any(
            comp.category == "storage" for comp in heatpump_result.components
        )

        return pv_has_storage or hp_has_storage

    def _apply_combined_modifications(
            self, base_price: float, modifications: dict[str, Any]) -> dict[str, Any]:
        """Apply combined system-specific modifications"""
        # Use the base pricing engine modification logic
        return self.apply_modifications(base_price, modifications)

    def _generate_combined_dynamic_keys(self,
                                        pv_result: PricingResult | None,
                                        heatpump_result: PricingResult | None,
                                        combined_base_price: float,
                                        combined_final_price: float,
                                        synergy_discount: float) -> dict[str,
                                                                         Any]:
        """Generate dynamic keys for combined system"""
        combined_keys = {}

        # Add individual system keys with prefixes
        if pv_result:
            for key, value in pv_result.dynamic_keys.items():
                combined_keys[f"PV_{key}"] = value

        if heatpump_result:
            for key, value in heatpump_result.dynamic_keys.items():
                combined_keys[f"HP_{key}"] = value

        # Add combined system keys
        combined_system_keys = {
            "COMBINED_BASE_PRICE": combined_base_price,
            "COMBINED_FINAL_PRICE": combined_final_price,
            "COMBINED_SYNERGY_DISCOUNT": synergy_discount,
            "COMBINED_SYNERGY_DISCOUNT_PCT": (
                synergy_discount /
                combined_base_price *
                100.0) if combined_base_price > 0 else 0.0,
            "COMBINED_SYSTEM_COUNT": sum(
                [
                    1 for result in [
                        pv_result,
                        heatpump_result] if result is not None])}

        # Add system-specific totals
        if pv_result:
            combined_system_keys["COMBINED_PV_TOTAL"] = pv_result.base_price
            combined_system_keys["COMBINED_PV_COMPONENT_COUNT"] = len(
                pv_result.components)

        if heatpump_result:
            combined_system_keys["COMBINED_HP_TOTAL"] = heatpump_result.base_price
            combined_system_keys["COMBINED_HP_COMPONENT_COUNT"] = len(
                heatpump_result.components)

        # Calculate system ratios
        if pv_result and heatpump_result:
            total_price = pv_result.base_price + heatpump_result.base_price
            if total_price > 0:
                combined_system_keys["COMBINED_PV_RATIO_PCT"] = (
                    pv_result.base_price / total_price) * 100.0
                combined_system_keys["COMBINED_HP_RATIO_PCT"] = (
                    heatpump_result.base_price / total_price) * 100.0

        # Energy system calculations
        pv_capacity = self._extract_pv_capacity(pv_result)
        hp_capacity = self._extract_heatpump_capacity(heatpump_result)

        if pv_capacity and hp_capacity:
            combined_system_keys["COMBINED_PV_CAPACITY_KWP"] = pv_capacity
            combined_system_keys["COMBINED_HP_CAPACITY_KW"] = hp_capacity
            combined_system_keys["COMBINED_CAPACITY_RATIO"] = pv_capacity / hp_capacity

            # Estimated energy balance
            # kWh per year (rough estimate)
            annual_pv_yield = pv_capacity * 1000
            annual_hp_consumption = hp_capacity * 2000 / 4.0  # Assuming COP 4.0
            combined_system_keys["COMBINED_ESTIMATED_PV_YIELD_KWH"] = annual_pv_yield
            combined_system_keys["COMBINED_ESTIMATED_HP_CONSUMPTION_KWH"] = annual_hp_consumption
            combined_system_keys["COMBINED_ENERGY_BALANCE_KWH"] = annual_pv_yield - \
                annual_hp_consumption

        combined_keys.update(combined_system_keys)

        return combined_keys

    def _extract_pv_capacity(
            self,
            pv_result: PricingResult | None) -> float | None:
        """Extract total PV capacity from PV result"""
        if not pv_result:
            return None

        return pv_result.dynamic_keys.get("PV_TOTAL_CAPACITY_KWP", 0.0)

    def _extract_heatpump_capacity(
            self, heatpump_result: PricingResult | None) -> float | None:
        """Extract total heat pump capacity from heat pump result"""
        if not heatpump_result:
            return None

        return heatpump_result.dynamic_keys.get(
            "HP_TOTAL_HEATING_CAPACITY_KW", 0.0)

    def calculate_combined_financing(self,
                                     combined_result: CombinedPricingResult,
                                     financing_config: dict[str,
                                                            Any]) -> dict[str,
                                                                          Any]:
        """Calculate financing for combined system"""
        try:
            # Extract financing parameters
            loan_amount = combined_result.combined_final_price
            down_payment = financing_config.get("down_payment", 0.0)
            interest_rate = financing_config.get("interest_rate_percent", 3.5)
            loan_term_years = financing_config.get("loan_term_years", 15)

            # Apply down payment
            financed_amount = loan_amount - down_payment

            if financed_amount <= 0:
                return {
                    "financed_amount": 0.0,
                    "monthly_payment": 0.0,
                    "total_interest": 0.0,
                    "total_payments": down_payment,
                    "financing_required": False
                }

            # Calculate monthly payment using annuity formula
            monthly_rate = interest_rate / 100.0 / 12.0
            num_payments = loan_term_years * 12

            if monthly_rate == 0:
                monthly_payment = financed_amount / num_payments
            else:
                monthly_payment = financed_amount * (
                    monthly_rate * (1 + monthly_rate) ** num_payments
                ) / ((1 + monthly_rate) ** num_payments - 1)

            total_payments = monthly_payment * num_payments + down_payment
            total_interest = total_payments - loan_amount

            # Generate financing keys
            financing_keys = self.key_manager.generate_keys({
                "FINANCING_LOAN_AMOUNT": loan_amount,
                "FINANCING_DOWN_PAYMENT": down_payment,
                "FINANCING_FINANCED_AMOUNT": financed_amount,
                "FINANCING_INTEREST_RATE_PCT": interest_rate,
                "FINANCING_LOAN_TERM_YEARS": loan_term_years,
                "FINANCING_MONTHLY_PAYMENT": monthly_payment,
                "FINANCING_TOTAL_INTEREST": total_interest,
                "FINANCING_TOTAL_PAYMENTS": total_payments
            }, prefix="COMBINED_")

            return {
                "loan_amount": loan_amount,
                "down_payment": down_payment,
                "financed_amount": financed_amount,
                "interest_rate_percent": interest_rate,
                "loan_term_years": loan_term_years,
                "monthly_payment": round(monthly_payment, 2),
                "total_interest": round(total_interest, 2),
                "total_payments": round(total_payments, 2),
                "financing_required": True,
                "dynamic_keys": financing_keys
            }

        except Exception as e:
            self.logger.error(f"Error calculating combined financing: {e}")
            return {
                "error": str(e),
                "financing_required": False
            }

    def calculate_combined_subsidies(self,
                                     combined_result: CombinedPricingResult,
                                     subsidy_config: dict[str,
                                                          Any]) -> dict[str,
                                                                        Any]:
        """Calculate available subsidies for combined system"""
        try:
            total_subsidies = 0.0
            subsidy_details = {}
            subsidy_keys = {}

            # PV subsidies (if applicable)
            if combined_result.pv_result and subsidy_config.get(
                    "pv_subsidies"):
                pv_subsidy_amount = self._calculate_pv_subsidies(
                    combined_result.pv_result, subsidy_config["pv_subsidies"]
                )
                total_subsidies += pv_subsidy_amount
                subsidy_details["pv_subsidies"] = pv_subsidy_amount
                subsidy_keys["COMBINED_PV_SUBSIDY_AMOUNT"] = pv_subsidy_amount

            # Heat pump subsidies (BEG)
            if combined_result.heatpump_result and subsidy_config.get(
                    "beg_subsidies"):
                beg_subsidy_result = self.heatpump_engine.calculate_beg_subsidy_integration(
                    combined_result.heatpump_result, subsidy_config["beg_subsidies"])
                if beg_subsidy_result["integration_successful"]:
                    beg_amount = beg_subsidy_result["beg_calculation"].get(
                        "subsidy_amount_net", 0.0)
                    total_subsidies += beg_amount
                    subsidy_details["beg_subsidies"] = beg_amount
                    subsidy_keys["COMBINED_BEG_SUBSIDY_AMOUNT"] = beg_amount

            # Combined system bonus subsidies
            if subsidy_config.get("combined_system_bonus"):
                bonus_amount = self._calculate_combined_system_bonus(
                    combined_result, subsidy_config["combined_system_bonus"]
                )
                total_subsidies += bonus_amount
                subsidy_details["combined_bonus"] = bonus_amount
                subsidy_keys["COMBINED_SYSTEM_BONUS_AMOUNT"] = bonus_amount

            # Calculate final price after subsidies
            final_price_after_subsidies = combined_result.combined_final_price - total_subsidies

            # Add summary keys
            subsidy_keys.update(
                {
                    "COMBINED_TOTAL_SUBSIDIES": total_subsidies,
                    "COMBINED_SUBSIDY_PERCENTAGE": (
                        total_subsidies /
                        combined_result.combined_final_price *
                        100.0) if combined_result.combined_final_price > 0 else 0.0,
                    "COMBINED_FINAL_PRICE_AFTER_SUBSIDIES": final_price_after_subsidies})

            return {
                "total_subsidies": total_subsidies,
                "subsidy_details": subsidy_details,
                "final_price_after_subsidies": final_price_after_subsidies,
                "subsidy_percentage": (
                    total_subsidies /
                    combined_result.combined_final_price *
                    100.0) if combined_result.combined_final_price > 0 else 0.0,
                "dynamic_keys": subsidy_keys}

        except Exception as e:
            self.logger.error(f"Error calculating combined subsidies: {e}")
            return {
                "error": str(e),
                "total_subsidies": 0.0
            }

    def _calculate_pv_subsidies(self, pv_result: PricingResult,
                                pv_subsidy_config: dict[str, Any]) -> float:
        """Calculate PV-specific subsidies"""
        # This would integrate with regional PV subsidy programs
        # For now, implement a simple percentage-based subsidy
        subsidy_rate = pv_subsidy_config.get("subsidy_rate_percent", 0.0)
        max_subsidy = pv_subsidy_config.get("max_subsidy_amount", float('inf'))

        subsidy_amount = calculate_discount_amount(
            pv_result.base_price,
            subsidy_rate,
        )
        return min(subsidy_amount, max_subsidy)

    def _calculate_combined_system_bonus(self,
                                         combined_result: CombinedPricingResult,
                                         bonus_config: dict[str,
                                                            Any]) -> float:
        """Calculate bonus subsidies for combined systems"""
        # Bonus for installing both PV and heat pump
        if combined_result.pv_result and combined_result.heatpump_result:
            bonus_rate = bonus_config.get("bonus_rate_percent", 2.0)
            max_bonus = bonus_config.get("max_bonus_amount", 2000.0)

            bonus_amount = calculate_discount_amount(
                combined_result.combined_base_price,
                bonus_rate,
            )
            return min(bonus_amount, max_bonus)

        return 0.0

    def validate_combined_system_configuration(
            self, system_config: dict[str, Any]) -> dict[str, Any]:
        """Validate combined system configuration"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }

        pv_config = system_config.get("pv_system", {})
        heatpump_config = system_config.get("heatpump_system", {})

        # Check that at least one system is configured
        if not pv_config.get(
                "components") and not heatpump_config.get("components"):
            validation_results["errors"].append(
                "At least one system (PV or heat pump) must be configured")
            validation_results["is_valid"] = False

        # Validate individual systems
        if pv_config.get("components"):
            try:
                self.pv_engine._validate_pv_configuration(
                    pv_config["components"],
                    pv_config.get("system_specs", {})
                )
            except Exception as e:
                validation_results["warnings"].append(
                    f"PV system validation warning: {e}")

        if heatpump_config.get("components"):
            try:
                self.heatpump_engine._validate_heatpump_configuration(
                    heatpump_config["components"],
                    heatpump_config.get("system_specs", {})
                )
            except Exception as e:
                validation_results["warnings"].append(
                    f"Heat pump system validation warning: {e}")

        # Check system compatibility
        compatibility_check = self._check_system_compatibility(
            pv_config, heatpump_config)
        validation_results["recommendations"].extend(compatibility_check)

        return validation_results

    def _check_system_compatibility(self, pv_config: dict[str, Any],
                                    heatpump_config: dict[str, Any]) -> list[str]:
        """Check compatibility between PV and heat pump systems"""
        recommendations = []

        # Check capacity matching
        pv_capacity = pv_config.get(
            "system_specs", {}).get(
            "total_capacity_kwp", 0.0)
        hp_demand = heatpump_config.get(
            "system_specs", {}).get(
            "heating_demand_kw", 0.0)

        if pv_capacity > 0 and hp_demand > 0:
            # Rough estimate: 1 kWp PV can support ~0.25 kW heat pump
            # (considering COP and utilization)
            optimal_ratio = pv_capacity / hp_demand

            if optimal_ratio < 0.5:
                recommendations.append(
                    f"Consider increasing PV capacity. Current ratio: {
                        optimal_ratio:.2f}, " "recommended: >0.5 for better energy balance")
            elif optimal_ratio > 3.0:
                recommendations.append(
                    f"PV system may be oversized for heat pump. Current ratio: {
                        optimal_ratio:.2f}, " "consider adding battery storage or reducing PV capacity")

        # Check for smart home integration opportunities
        if (pv_config.get("components") and heatpump_config.get("components")) or (
                pv_config.get("system_specs") and heatpump_config.get("system_specs")):
            recommendations.append(
                "Consider adding smart home integration for optimal energy management between PV and heat pump systems"
            )

        return recommendations


# Convenience functions for external use
def create_combined_pricing_engine() -> CombinedPricingEngine:
    """Create a new combined pricing engine instance"""
    return CombinedPricingEngine()


def calculate_combined_system_pricing(
        system_config: dict[str, Any]) -> CombinedPricingResult:
    """Calculate combined system pricing using the combined pricing engine

    Args:
        system_config: Combined system configuration

    Returns:
        CombinedPricingResult with complete combined system pricing
    """
    engine = create_combined_pricing_engine()
    return engine.calculate_combined_system_price(system_config)


__all__ = [
    "CombinedPricingResult",
    "CombinedPricingEngine",
    "create_combined_pricing_engine",
    "calculate_combined_system_pricing"
]
