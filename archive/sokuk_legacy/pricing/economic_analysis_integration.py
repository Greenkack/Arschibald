"""Economic Analysis Integration

Connects the enhanced pricing system with economic calculations for accurate
payback period, ROI, and profitability analysis using final pricing data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

try:
    from pv_calculations_core import (
        DISCOUNT_RATE,
        LIFESPAN_YEARS,
        calculate_annual_cost_savings,
        calculate_co2_payback_time,
        calculate_co2_savings,
        calculate_feed_in_tariff_revenue,
        calculate_irr,
        calculate_net_present_value,
        calculate_payback_period,
        calculate_total_roi,
    )
except ImportError:
    # Fallback constants and functions for testing
    LIFESPAN_YEARS = 25
    DISCOUNT_RATE = 0.04

    def calculate_payback_period(
            investment: float,
            annual_savings: float) -> float:
        return investment / \
            annual_savings if annual_savings > 0 else float('inf')

    def calculate_annual_cost_savings(
            self_consumed_kwh: float,
            electricity_price: float) -> float:
        return self_consumed_kwh * electricity_price

    def calculate_feed_in_tariff_revenue(
            feed_in_kwh: float,
            feed_in_rate: float) -> float:
        return feed_in_kwh * feed_in_rate

    def calculate_net_present_value(
            investment: float,
            annual_savings: float,
            years: int = 25,
            discount_rate: float = 0.04) -> float:
        return sum(annual_savings / (1 + discount_rate) **
                   year for year in range(1, years + 1)) - investment

    def calculate_irr(
            investment: float,
            annual_savings: float,
            years: int = 25) -> float:
        # Simplified IRR calculation
        return (annual_savings * years / investment - 1) * \
            100 / years if investment > 0 else 0.0

    def calculate_total_roi(
            investment: float,
            annual_savings: float,
            years: int = 25) -> float:
        return ((annual_savings * years - investment) /
                investment) * 100 if investment > 0 else 0.0

    def calculate_co2_savings(annual_production: float) -> float:
        return annual_production * 0.474  # kg CO2 per kWh

    def calculate_co2_payback_time(
            system_kwp: float,
            annual_production: float) -> float:
        manufacturing_co2 = system_kwp * 2500  # kg CO2 for manufacturing
        annual_co2_savings = calculate_co2_savings(annual_production)
        return manufacturing_co2 / \
            annual_co2_savings if annual_co2_savings > 0 else float('inf')

from .dynamic_key_manager import DynamicKeyManager
from .enhanced_pricing_engine import FinalPricingResult
from .pricing_audit import audit_price_calculation, get_calculation_logger
from .pricing_errors import CalculationError, ValidationError, safe_pricing_operation
from .pricing_validation import get_pricing_validator

logger = logging.getLogger(__name__)


@dataclass
class EconomicAnalysisResult:
    """Complete economic analysis result with enhanced pricing integration"""

    # Investment data from enhanced pricing
    total_investment_net: float
    total_investment_gross: float
    final_pricing_breakdown: dict[str, float]

    # System performance data
    annual_production_kwh: float
    self_consumption_kwh: float
    feed_in_kwh: float

    # Economic parameters
    electricity_price_kwh: float
    feed_in_tariff_kwh: float

    # Calculated economic metrics
    annual_savings: float
    annual_feed_in_revenue: float
    total_annual_benefit: float
    payback_period_years: float
    roi_percent: float
    npv_eur: float
    irr_percent: float

    # Environmental metrics
    annual_co2_savings_kg: float
    co2_payback_years: float
    lifetime_co2_savings_tons: float

    # Dynamic keys for PDF integration
    dynamic_keys: dict[str, Any] = field(default_factory=dict)

    # Metadata
    calculation_timestamp: datetime = field(default_factory=datetime.now)
    system_type: str = "pv"  # "pv", "heatpump", "combined"
    analysis_parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfitabilityReport:
    """Comprehensive profitability analysis report"""

    # Profit margin analysis
    total_purchase_cost: float
    total_selling_price: float
    gross_profit: float
    gross_margin_percent: float

    # Component-level profitability
    component_margins: list[dict[str, Any]]
    highest_margin_component: dict[str, Any]
    lowest_margin_component: dict[str, Any]

    # Pricing trend analysis
    pricing_trends: dict[str, list[float]]
    trend_analysis: dict[str, str]

    # Optimization suggestions
    optimization_suggestions: list[dict[str, Any]]
    potential_savings: float
    margin_improvement_potential: float

    # Dynamic keys for reporting
    dynamic_keys: dict[str, Any] = field(default_factory=dict)

    # Metadata
    report_timestamp: datetime = field(default_factory=datetime.now)
    analysis_period: str = "current"


class EconomicAnalysisIntegration:
    """Integrates enhanced pricing system with economic analysis calculations"""

    def __init__(self, system_type: str = "pv"):
        """Initialize economic analysis integration

        Args:
            system_type: Type of system ("pv", "heatpump", "combined")
        """
        self.system_type = system_type
        self.key_manager = DynamicKeyManager()
        self.validator = get_pricing_validator()
        self.logger = get_calculation_logger()

        logger.info(
            f"Initialized EconomicAnalysisIntegration for {system_type}")

    @safe_pricing_operation("calculate_economic_analysis",
                            "economic_integration")
    def calculate_economic_analysis(
        self,
        final_pricing_result: FinalPricingResult,
        system_performance: dict[str, Any],
        economic_parameters: dict[str, Any]
    ) -> EconomicAnalysisResult:
        """Calculate complete economic analysis using final pricing data

        Args:
            final_pricing_result: Final pricing result from enhanced pricing engine
            system_performance: System performance data (production, consumption, etc.)
            economic_parameters: Economic parameters (electricity price, feed-in tariff, etc.)

        Returns:
            Complete economic analysis result
        """
        try:
            # Validate inputs
            self._validate_economic_inputs(
                final_pricing_result,
                system_performance,
                economic_parameters)

            # Extract investment amounts from final pricing
            total_investment_net = final_pricing_result.final_price_net
            total_investment_gross = final_pricing_result.final_price_gross

            # Extract system performance data
            annual_production_kwh = system_performance.get(
                "annual_production_kwh", 0.0)
            self_consumption_kwh = system_performance.get(
                "self_consumption_kwh", 0.0)
            feed_in_kwh = system_performance.get("feed_in_kwh", 0.0)

            # Extract economic parameters
            electricity_price_kwh = economic_parameters.get(
                "electricity_price_kwh", 0.30)
            feed_in_tariff_kwh = economic_parameters.get(
                "feed_in_tariff_kwh", 0.08)

            # Calculate annual savings and revenue
            annual_savings = calculate_annual_cost_savings(
                self_consumption_kwh, electricity_price_kwh)
            annual_feed_in_revenue = calculate_feed_in_tariff_revenue(
                feed_in_kwh, feed_in_tariff_kwh)
            total_annual_benefit = annual_savings + annual_feed_in_revenue

            # Calculate economic metrics using final investment amount
            payback_period_years = calculate_payback_period(
                total_investment_net, total_annual_benefit)
            roi_percent = calculate_total_roi(
                total_investment_net, total_annual_benefit)
            npv_eur = calculate_net_present_value(
                total_investment_net, total_annual_benefit)
            irr_percent = calculate_irr(
                total_investment_net, total_annual_benefit)

            # Calculate environmental metrics
            annual_co2_savings_kg = calculate_co2_savings(
                annual_production_kwh)
            system_kwp = system_performance.get("system_power_kwp", 10.0)
            co2_payback_years = calculate_co2_payback_time(
                system_kwp, annual_production_kwh)
            lifetime_co2_savings_tons = (
                annual_co2_savings_kg * LIFESPAN_YEARS) / 1000

            # Generate dynamic keys for PDF integration
            economic_keys = self._generate_economic_keys({
                "total_investment_net": total_investment_net,
                "total_investment_gross": total_investment_gross,
                "annual_savings": annual_savings,
                "annual_feed_in_revenue": annual_feed_in_revenue,
                "total_annual_benefit": total_annual_benefit,
                "payback_period_years": payback_period_years,
                "roi_percent": roi_percent,
                "npv_eur": npv_eur,
                "irr_percent": irr_percent,
                "annual_co2_savings_kg": annual_co2_savings_kg,
                "co2_payback_years": co2_payback_years,
                "lifetime_co2_savings_tons": lifetime_co2_savings_tons
            })

            # Create final pricing breakdown
            final_pricing_breakdown = {
                "base_price": final_pricing_result.base_price,
                "total_discounts": final_pricing_result.total_discounts,
                "total_surcharges": final_pricing_result.total_surcharges,
                "vat_amount": final_pricing_result.vat_amount,
                "final_net": total_investment_net,
                "final_gross": total_investment_gross
            }

            # Create result
            result = EconomicAnalysisResult(
                total_investment_net=total_investment_net,
                total_investment_gross=total_investment_gross,
                final_pricing_breakdown=final_pricing_breakdown,
                annual_production_kwh=annual_production_kwh,
                self_consumption_kwh=self_consumption_kwh,
                feed_in_kwh=feed_in_kwh,
                electricity_price_kwh=electricity_price_kwh,
                feed_in_tariff_kwh=feed_in_tariff_kwh,
                annual_savings=annual_savings,
                annual_feed_in_revenue=annual_feed_in_revenue,
                total_annual_benefit=total_annual_benefit,
                payback_period_years=payback_period_years,
                roi_percent=roi_percent,
                npv_eur=npv_eur,
                irr_percent=irr_percent,
                annual_co2_savings_kg=annual_co2_savings_kg,
                co2_payback_years=co2_payback_years,
                lifetime_co2_savings_tons=lifetime_co2_savings_tons,
                dynamic_keys=economic_keys,
                system_type=self.system_type,
                analysis_parameters=economic_parameters.copy()
            )

            # Audit the calculation
            audit_price_calculation(
                calculation_data={
                    "operation": "calculate_economic_analysis",
                    "final_price_net": total_investment_net,
                    "annual_production": annual_production_kwh,
                    "electricity_price": electricity_price_kwh,
                    "system_type": self.system_type
                },
                result={
                    "payback_period": payback_period_years,
                    "roi_percent": roi_percent,
                    "npv_eur": npv_eur,
                    "total_annual_benefit": total_annual_benefit
                },
                duration_ms=100.0  # Placeholder duration
            )

            logger.info(
                f"Economic analysis calculated successfully for {
                    self.system_type}")
            return result

        except Exception as e:
            logger.error(f"Economic analysis calculation failed: {str(e)}")
            raise CalculationError(
                f"Economic analysis calculation failed: {
                    str(e)}")

    def _validate_economic_inputs(
        self,
        final_pricing_result: FinalPricingResult,
        system_performance: dict[str, Any],
        economic_parameters: dict[str, Any]
    ) -> None:
        """Validate inputs for economic analysis"""

        # Validate final pricing result
        if not isinstance(final_pricing_result, FinalPricingResult):
            raise ValidationError(
                "final_pricing_result must be a FinalPricingResult instance")

        if final_pricing_result.final_price_net <= 0:
            raise ValidationError("Final price net must be positive")

        # Validate system performance
        required_performance_fields = [
            "annual_production_kwh",
            "self_consumption_kwh",
            "feed_in_kwh"]
        for field in required_performance_fields:
            if field not in system_performance:
                raise ValidationError(
                    f"Missing required system performance field: {field}")

            value = system_performance[field]
            if not isinstance(value, (int, float)) or value < 0:
                raise ValidationError(
                    f"System performance field {field} must be a non-negative number")

        # Validate economic parameters
        required_economic_fields = [
            "electricity_price_kwh",
            "feed_in_tariff_kwh"]
        for field in required_economic_fields:
            if field not in economic_parameters:
                raise ValidationError(
                    f"Missing required economic parameter: {field}")

            value = economic_parameters[field]
            if not isinstance(value, (int, float)) or value < 0:
                raise ValidationError(
                    f"Economic parameter {field} must be a non-negative number")

    def _generate_economic_keys(
            self, economic_data: dict[str, Any]) -> dict[str, Any]:
        """Generate dynamic keys for economic analysis data"""

        # Format values for PDF display
        formatted_data = {}

        for key, value in economic_data.items():
            if isinstance(value, float):
                if "percent" in key.lower() or "roi" in key.lower():
                    formatted_data[key.upper()] = f"{value:.1f}%"
                elif "kg" in key.lower():
                    formatted_data[key.upper()] = f"{value:,.0f} kg"
                elif "tons" in key.lower():
                    formatted_data[key.upper()] = f"{value:.1f} t"
                elif "kwh" in key.lower():
                    formatted_data[key.upper()] = f"{value:,.0f} kWh"
                elif "years" in key.lower() or "period" in key.lower():
                    formatted_data[key.upper()] = f"{value:.1f} Jahre"
                elif "eur" in key.lower() or "investment" in key.lower() or "savings" in key.lower():
                    formatted_data[key.upper()] = f"{value:,.2f}€"
                else:
                    formatted_data[key.upper()] = f"{value:.2f}"
            else:
                formatted_data[key.upper()] = str(value)

        # Generate keys with system type prefix
        return self.key_manager.generate_keys(
            formatted_data,
            prefix=f"{self.system_type.upper()}_ECONOMIC"
        )

    @safe_pricing_operation("create_profitability_report",
                            "economic_integration")
    def create_profitability_report(
        self,
        final_pricing_result: FinalPricingResult,
        historical_pricing_data: dict[str, list[float]] | None = None
    ) -> ProfitabilityReport:
        """Create comprehensive profitability analysis report

        Args:
            final_pricing_result: Final pricing result with component details
            historical_pricing_data: Optional historical pricing data for trend analysis

        Returns:
            Comprehensive profitability report
        """
        try:
            # Calculate total costs and margins
            total_purchase_cost = 0.0
            total_selling_price = final_pricing_result.base_price
            component_margins = []

            # Analyze component-level profitability
            for component in final_pricing_result.components:
                # Get purchase price from component data
                purchase_price = getattr(
                    component,
                    'purchase_price',
                    component.price_euro *
                    0.7)  # Fallback estimate
                selling_price = component.total_price
                margin_amount = selling_price - \
                    (purchase_price * component.quantity)
                margin_percent = (
                    margin_amount /
                    selling_price *
                    100) if selling_price > 0 else 0.0

                total_purchase_cost += purchase_price * component.quantity

                component_margin = {
                    "component_name": component.model_name,
                    "category": component.category,
                    "quantity": component.quantity,
                    "purchase_price_unit": purchase_price,
                    "selling_price_unit": component.unit_price,
                    "total_purchase_cost": purchase_price * component.quantity,
                    "total_selling_price": selling_price,
                    "margin_amount": margin_amount,
                    "margin_percent": margin_percent
                }
                component_margins.append(component_margin)

            # Calculate overall profitability
            gross_profit = total_selling_price - total_purchase_cost
            gross_margin_percent = (
                gross_profit /
                total_selling_price *
                100) if total_selling_price > 0 else 0.0

            # Find highest and lowest margin components
            highest_margin_component = max(
                component_margins,
                key=lambda x: x["margin_percent"]) if component_margins else {}
            lowest_margin_component = min(
                component_margins,
                key=lambda x: x["margin_percent"]) if component_margins else {}

            # Analyze pricing trends if historical data provided
            pricing_trends = historical_pricing_data or {}
            trend_analysis = self._analyze_pricing_trends(pricing_trends)

            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                component_margins, gross_margin_percent
            )

            # Calculate potential savings and improvements
            potential_savings = sum(
                suggestion.get("potential_savings", 0.0)
                for suggestion in optimization_suggestions
            )

            margin_improvement_potential = sum(
                suggestion.get("margin_improvement", 0.0)
                for suggestion in optimization_suggestions
            )

            # Generate dynamic keys for reporting
            profitability_keys = self._generate_profitability_keys({
                "total_purchase_cost": total_purchase_cost,
                "total_selling_price": total_selling_price,
                "gross_profit": gross_profit,
                "gross_margin_percent": gross_margin_percent,
                "potential_savings": potential_savings,
                "margin_improvement_potential": margin_improvement_potential,
                "component_count": len(component_margins)
            })

            # Create profitability report
            report = ProfitabilityReport(
                total_purchase_cost=total_purchase_cost,
                total_selling_price=total_selling_price,
                gross_profit=gross_profit,
                gross_margin_percent=gross_margin_percent,
                component_margins=component_margins,
                highest_margin_component=highest_margin_component,
                lowest_margin_component=lowest_margin_component,
                pricing_trends=pricing_trends,
                trend_analysis=trend_analysis,
                optimization_suggestions=optimization_suggestions,
                potential_savings=potential_savings,
                margin_improvement_potential=margin_improvement_potential,
                dynamic_keys=profitability_keys
            )

            logger.info(
                f"Profitability report created successfully for {
                    self.system_type}")
            return report

        except Exception as e:
            logger.error(f"Profitability report creation failed: {str(e)}")
            raise CalculationError(
                f"Profitability report creation failed: {
                    str(e)}")

    def _analyze_pricing_trends(
            self, pricing_trends: dict[str, list[float]]) -> dict[str, str]:
        """Analyze pricing trends from historical data"""

        trend_analysis = {}

        for component, prices in pricing_trends.items():
            if len(prices) < 2:
                trend_analysis[component] = "insufficient_data"
                continue

            # Calculate trend direction
            recent_avg = np.mean(
                prices[-3:]) if len(prices) >= 3 else prices[-1]
            older_avg = np.mean(prices[:3]) if len(prices) >= 3 else prices[0]

            change_percent = ((recent_avg - older_avg) /
                              older_avg * 100) if older_avg > 0 else 0.0

            if change_percent > 5:
                trend_analysis[component] = "increasing"
            elif change_percent < -5:
                trend_analysis[component] = "decreasing"
            else:
                trend_analysis[component] = "stable"

        return trend_analysis

    def _generate_optimization_suggestions(
        self,
        component_margins: list[dict[str, Any]],
        current_margin: float
    ) -> list[dict[str, Any]]:
        """Generate optimization suggestions based on margin analysis"""

        suggestions = []

        # Suggest improvements for low-margin components
        low_margin_components = [
            comp for comp in component_margins
            if comp["margin_percent"] < 15.0  # Less than 15% margin
        ]

        for comp in low_margin_components:
            suggestion = {
                "type": "margin_improvement",
                "component": comp["component_name"],
                "current_margin": comp["margin_percent"],
                "suggested_margin": 20.0,
                # 5% improvement
                "potential_savings": comp["total_selling_price"] * 0.05,
                "margin_improvement": 5.0,
                "description": f"Increase margin for {comp['component_name']} from {comp['margin_percent']:.1f}% to 20%",
                "priority": "high" if comp["margin_percent"] < 10.0 else "medium"
            }
            suggestions.append(suggestion)

        # Suggest bulk purchasing for high-volume components
        high_volume_components = [
            comp for comp in component_margins
            if comp["quantity"] > 10
        ]

        for comp in high_volume_components:
            suggestion = {
                "type": "bulk_purchasing",
                "component": comp["component_name"],
                "current_quantity": comp["quantity"],
                # 8% bulk discount
                "potential_savings": comp["total_purchase_cost"] * 0.08,
                "margin_improvement": 3.0,
                "description": f"Negotiate bulk pricing for {comp['component_name']} (quantity: {comp['quantity']})",
                "priority": "medium"
            }
            suggestions.append(suggestion)

        # Suggest alternative suppliers for expensive components
        expensive_components = [
            comp for comp in component_margins
            if comp["total_purchase_cost"] > 1000.0
        ]

        for comp in expensive_components:
            suggestion = {
                "type": "supplier_optimization",
                "component": comp["component_name"],
                "current_cost": comp["total_purchase_cost"],
                # 12% alternative supplier savings
                "potential_savings": comp["total_purchase_cost"] * 0.12,
                "margin_improvement": 4.0,
                "description": f"Evaluate alternative suppliers for {comp['component_name']}",
                "priority": "high" if comp["total_purchase_cost"] > 2000.0 else "medium"
            }
            suggestions.append(suggestion)

        # Sort suggestions by potential impact
        suggestions.sort(
            key=lambda x: x.get(
                "potential_savings",
                0.0),
            reverse=True)

        return suggestions[:5]  # Return top 5 suggestions

    def _generate_profitability_keys(
            self, profitability_data: dict[str, Any]) -> dict[str, Any]:
        """Generate dynamic keys for profitability report data"""

        # Format values for PDF display
        formatted_data = {}

        for key, value in profitability_data.items():
            if isinstance(value, float):
                if "percent" in key.lower() or "margin" in key.lower():
                    formatted_data[key.upper()] = f"{value:.1f}%"
                elif "cost" in key.lower() or "price" in key.lower() or "profit" in key.lower() or "savings" in key.lower():
                    formatted_data[key.upper()] = f"{value:,.2f}€"
                else:
                    formatted_data[key.upper()] = f"{value:.2f}"
            else:
                formatted_data[key.upper()] = str(value)

        # Generate keys with system type prefix
        return self.key_manager.generate_keys(
            formatted_data,
            prefix=f"{self.system_type.upper()}_PROFITABILITY"
        )


def get_economic_analysis_integration(
        system_type: str = "pv") -> EconomicAnalysisIntegration:
    """Factory function to get economic analysis integration instance

    Args:
        system_type: Type of system ("pv", "heatpump", "combined")

    Returns:
        EconomicAnalysisIntegration instance
    """
    return EconomicAnalysisIntegration(system_type=system_type)


# Export main classes and functions
__all__ = [
    "EconomicAnalysisResult",
    "ProfitabilityReport",
    "EconomicAnalysisIntegration",
    "get_economic_analysis_integration"
]
