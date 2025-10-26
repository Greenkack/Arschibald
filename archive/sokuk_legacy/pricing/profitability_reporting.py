"""Profitability Reporting Module

Provides comprehensive profitability analysis and reporting functionality
for the enhanced pricing system, including profit margin analysis, pricing
trends, and optimization suggestions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

try:
    from product_db import get_all_products, get_product_by_id
except ImportError:
    # Fallback for testing
    def get_all_products() -> list[dict[str, Any]]:
        return []

    def get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return None

from .dynamic_key_manager import DynamicKeyManager
from .economic_analysis_integration import get_economic_analysis_integration
from .enhanced_pricing_engine import FinalPricingResult
from .pricing_audit import get_calculation_logger
from .pricing_errors import CalculationError, ValidationError, safe_pricing_operation
from .pricing_validation import get_pricing_validator

logger = logging.getLogger(__name__)


@dataclass
class ComponentCostAnalysis:
    """Analysis of component costs and profitability"""
    component_name: str
    category: str
    total_quantity: int
    total_purchase_cost: float
    total_selling_price: float
    average_margin_percent: float
    cost_per_unit: float
    selling_price_per_unit: float
    profit_per_unit: float
    market_position: str  # "low_cost", "premium", "competitive"
    optimization_potential: float


@dataclass
class PricingTrendAnalysis:
    """Analysis of pricing trends over time"""
    component_name: str
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float  # 0.0 to 1.0
    price_change_percent: float
    volatility_index: float
    forecast_next_period: float
    confidence_level: float


@dataclass
class OptimizationSuggestion:
    """Detailed optimization suggestion with impact analysis"""
    suggestion_id: str
    # "margin_improvement", "bulk_purchasing", "supplier_optimization", etc.
    type: str
    title: str
    description: str
    affected_components: list[str]
    current_cost: float
    potential_savings: float
    margin_improvement_percent: float
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    expected_timeframe: str  # "immediate", "short_term", "long_term"
    priority_score: float
    roi_estimate: float


@dataclass
class ComprehensiveProfitabilityReport:
    """Comprehensive profitability analysis report"""

    # Executive Summary
    total_revenue: float
    total_costs: float
    gross_profit: float
    gross_margin_percent: float

    # Component Analysis
    component_analyses: list[ComponentCostAnalysis]
    top_profit_components: list[ComponentCostAnalysis]
    low_margin_components: list[ComponentCostAnalysis]

    # Trend Analysis
    pricing_trends: list[PricingTrendAnalysis]
    market_insights: dict[str, Any]

    # Optimization Opportunities
    optimization_suggestions: list[OptimizationSuggestion]
    total_optimization_potential: float
    quick_wins: list[OptimizationSuggestion]
    strategic_initiatives: list[OptimizationSuggestion]

    # Performance Metrics
    performance_metrics: dict[str, float]
    benchmarks: dict[str, float]

    # Dynamic keys for reporting
    dynamic_keys: dict[str, Any] = field(default_factory=dict)

    # Metadata
    report_timestamp: datetime = field(default_factory=datetime.now)
    analysis_period: str = "current"
    system_type: str = "pv"


class ProfitabilityReportingEngine:
    """Advanced profitability reporting and analysis engine"""

    def __init__(self, system_type: str = "pv"):
        """Initialize profitability reporting engine

        Args:
            system_type: Type of system ("pv", "heatpump", "combined")
        """
        self.system_type = system_type
        self.key_manager = DynamicKeyManager()
        self.validator = get_pricing_validator()
        self.logger = get_calculation_logger()
        self.economic_integration = get_economic_analysis_integration(
            system_type)

        logger.info(
            f"Initialized ProfitabilityReportingEngine for {system_type}")

    @safe_pricing_operation("generate_comprehensive_report",
                            "profitability_reporting")
    def generate_comprehensive_report(
        self,
        final_pricing_results: list[FinalPricingResult],
        historical_data: dict[str, Any] | None = None,
        analysis_period: str = "current"
    ) -> ComprehensiveProfitabilityReport:
        """Generate comprehensive profitability analysis report

        Args:
            final_pricing_results: List of final pricing results to analyze
            historical_data: Optional historical pricing and sales data
            analysis_period: Analysis period identifier

        Returns:
            Comprehensive profitability report
        """
        try:
            # Validate inputs
            self._validate_report_inputs(
                final_pricing_results, historical_data)

            # Aggregate data from all pricing results
            aggregated_data = self._aggregate_pricing_data(
                final_pricing_results)

            # Perform component cost analysis
            component_analyses = self._analyze_component_costs(aggregated_data)

            # Analyze pricing trends
            pricing_trends = self._analyze_pricing_trends(
                component_analyses, historical_data
            )

            # Generate optimization suggestions
            optimization_suggestions = self._generate_advanced_optimization_suggestions(
                component_analyses, pricing_trends)

            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                aggregated_data, component_analyses
            )

            # Generate market insights
            market_insights = self._generate_market_insights(
                component_analyses, pricing_trends
            )

            # Calculate totals and summaries
            total_revenue = sum(
                result.final_price_net for result in final_pricing_results)
            total_costs = self._calculate_total_costs(component_analyses)
            gross_profit = total_revenue - total_costs
            gross_margin_percent = (
                gross_profit /
                total_revenue *
                100) if total_revenue > 0 else 0.0

            # Categorize optimization suggestions
            quick_wins = [
                s for s in optimization_suggestions if s.expected_timeframe == "immediate"]
            strategic_initiatives = [
                s for s in optimization_suggestions if s.expected_timeframe == "long_term"]

            # Calculate optimization potential
            total_optimization_potential = sum(
                s.potential_savings for s in optimization_suggestions)

            # Identify top performers and problem areas
            top_profit_components = sorted(
                component_analyses,
                key=lambda x: x.profit_per_unit * x.total_quantity,
                reverse=True
            )[:5]

            low_margin_components = [
                c for c in component_analyses
                if c.average_margin_percent < 15.0
            ]

            # Generate dynamic keys for reporting
            report_keys = self._generate_report_keys({
                "total_revenue": total_revenue,
                "total_costs": total_costs,
                "gross_profit": gross_profit,
                "gross_margin_percent": gross_margin_percent,
                "optimization_potential": total_optimization_potential,
                "component_count": len(component_analyses),
                "suggestion_count": len(optimization_suggestions)
            })

            # Create comprehensive report
            report = ComprehensiveProfitabilityReport(
                total_revenue=total_revenue,
                total_costs=total_costs,
                gross_profit=gross_profit,
                gross_margin_percent=gross_margin_percent,
                component_analyses=component_analyses,
                top_profit_components=top_profit_components,
                low_margin_components=low_margin_components,
                pricing_trends=pricing_trends,
                market_insights=market_insights,
                optimization_suggestions=optimization_suggestions,
                total_optimization_potential=total_optimization_potential,
                quick_wins=quick_wins,
                strategic_initiatives=strategic_initiatives,
                performance_metrics=performance_metrics,
                benchmarks=self._get_industry_benchmarks(),
                dynamic_keys=report_keys,
                analysis_period=analysis_period,
                system_type=self.system_type
            )

            logger.info(
                f"Comprehensive profitability report generated for {
                    self.system_type}")
            return report

        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {str(e)}")
            raise CalculationError(
                f"Comprehensive report generation failed: {
                    str(e)}")

    def _validate_report_inputs(
        self,
        final_pricing_results: list[FinalPricingResult],
        historical_data: dict[str, Any] | None
    ) -> None:
        """Validate inputs for report generation"""

        if not isinstance(final_pricing_results, list):
            raise ValidationError("final_pricing_results must be a list")

        if len(final_pricing_results) == 0:
            raise ValidationError("final_pricing_results cannot be empty")

        for i, result in enumerate(final_pricing_results):
            if not isinstance(result, FinalPricingResult):
                raise ValidationError(
                    f"Item {i} in final_pricing_results must be a FinalPricingResult")

            if result.final_price_net <= 0:
                raise ValidationError(
                    f"Final price net must be positive for result {i}")

    def _aggregate_pricing_data(
        self,
        final_pricing_results: list[FinalPricingResult]
    ) -> dict[str, Any]:
        """Aggregate data from multiple pricing results"""

        aggregated = {
            "components": {},
            "total_revenue": 0.0,
            "total_base_cost": 0.0,
            "result_count": len(final_pricing_results)
        }

        for result in final_pricing_results:
            aggregated["total_revenue"] += result.final_price_net
            aggregated["total_base_cost"] += result.base_price

            # Aggregate component data
            for component in result.components:
                comp_key = f"{component.category}_{component.model_name}"

                if comp_key not in aggregated["components"]:
                    aggregated["components"][comp_key] = {
                        "component": component,
                        "total_quantity": 0,
                        "total_price": 0.0,
                        "occurrences": 0
                    }

                comp_data = aggregated["components"][comp_key]
                comp_data["total_quantity"] += component.quantity
                comp_data["total_price"] += component.total_price
                comp_data["occurrences"] += 1

        return aggregated

    def _analyze_component_costs(
        self,
        aggregated_data: dict[str, Any]
    ) -> list[ComponentCostAnalysis]:
        """Analyze component costs and profitability"""

        analyses = []

        for comp_key, comp_data in aggregated_data["components"].items():
            component = comp_data["component"]
            total_quantity = comp_data["total_quantity"]
            total_selling_price = comp_data["total_price"]

            # Estimate purchase cost (fallback if not available)
            purchase_cost_per_unit = getattr(
                component, 'purchase_price', component.price_euro * 0.7)
            total_purchase_cost = purchase_cost_per_unit * total_quantity

            # Calculate metrics
            selling_price_per_unit = total_selling_price / \
                total_quantity if total_quantity > 0 else 0.0
            profit_per_unit = selling_price_per_unit - purchase_cost_per_unit
            average_margin_percent = (
                profit_per_unit /
                selling_price_per_unit *
                100) if selling_price_per_unit > 0 else 0.0

            # Determine market position
            market_position = self._determine_market_position(
                selling_price_per_unit, average_margin_percent, component.category)

            # Calculate optimization potential
            optimization_potential = self._calculate_optimization_potential(
                total_purchase_cost, average_margin_percent, component.category
            )

            analysis = ComponentCostAnalysis(
                component_name=component.model_name,
                category=component.category,
                total_quantity=total_quantity,
                total_purchase_cost=total_purchase_cost,
                total_selling_price=total_selling_price,
                average_margin_percent=average_margin_percent,
                cost_per_unit=purchase_cost_per_unit,
                selling_price_per_unit=selling_price_per_unit,
                profit_per_unit=profit_per_unit,
                market_position=market_position,
                optimization_potential=optimization_potential
            )

            analyses.append(analysis)

        return analyses

    def _analyze_pricing_trends(
        self,
        component_analyses: list[ComponentCostAnalysis],
        historical_data: dict[str, Any] | None
    ) -> list[PricingTrendAnalysis]:
        """Analyze pricing trends for components"""

        trends = []

        if not historical_data or "pricing_history" not in historical_data:
            # Generate placeholder trends if no historical data
            for analysis in component_analyses:
                trend = PricingTrendAnalysis(
                    component_name=analysis.component_name,
                    trend_direction="stable",
                    trend_strength=0.5,
                    price_change_percent=0.0,
                    volatility_index=0.3,
                    forecast_next_period=analysis.selling_price_per_unit,
                    confidence_level=0.6
                )
                trends.append(trend)
            return trends

        pricing_history = historical_data["pricing_history"]

        for analysis in component_analyses:
            component_history = pricing_history.get(
                analysis.component_name, [])

            if len(component_history) < 2:
                # Insufficient data for trend analysis
                trend = PricingTrendAnalysis(
                    component_name=analysis.component_name,
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    price_change_percent=0.0,
                    volatility_index=0.0,
                    forecast_next_period=analysis.selling_price_per_unit,
                    confidence_level=0.1
                )
                trends.append(trend)
                continue

            # Calculate trend metrics
            prices = np.array(component_history)
            trend_direction, trend_strength = self._calculate_trend_direction(
                prices)
            price_change_percent = (
                (prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0.0
            volatility_index = np.std(
                prices) / np.mean(prices) if np.mean(prices) > 0 else 0.0

            # Simple forecast (linear trend)
            forecast_next_period = self._forecast_next_period(prices)
            confidence_level = self._calculate_forecast_confidence(
                prices, volatility_index)

            trend = PricingTrendAnalysis(
                component_name=analysis.component_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                price_change_percent=price_change_percent,
                volatility_index=volatility_index,
                forecast_next_period=forecast_next_period,
                confidence_level=confidence_level
            )

            trends.append(trend)

        return trends

    def _generate_advanced_optimization_suggestions(
        self,
        component_analyses: list[ComponentCostAnalysis],
        pricing_trends: list[PricingTrendAnalysis]
    ) -> list[OptimizationSuggestion]:
        """Generate advanced optimization suggestions"""

        suggestions = []
        suggestion_id = 1

        # Create trend lookup for easy access
        trend_lookup = {
            trend.component_name: trend for trend in pricing_trends}

        for analysis in component_analyses:
            trend = trend_lookup.get(analysis.component_name)

            # Low margin improvement suggestions
            if analysis.average_margin_percent < 15.0:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"MARGIN_{suggestion_id}",
                    type="margin_improvement",
                    title=f"Improve margin for {analysis.component_name}",
                    description=f"Current margin of {
                        analysis.average_margin_percent:.1f}% is below target. Consider price increase or cost reduction.",
                    affected_components=[analysis.component_name],
                    current_cost=analysis.total_purchase_cost,
                    potential_savings=analysis.total_selling_price * 0.05,  # 5% improvement
                    margin_improvement_percent=5.0,
                    implementation_effort="medium",
                    risk_level="low",
                    expected_timeframe="short_term",
                    priority_score=self._calculate_priority_score(
                        analysis, trend),
                    roi_estimate=2.5
                )
                suggestions.append(suggestion)
                suggestion_id += 1

            # Bulk purchasing suggestions for high-volume components
            if analysis.total_quantity > 20:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"BULK_{suggestion_id}",
                    type="bulk_purchasing",
                    title=f"Negotiate bulk pricing for {
                        analysis.component_name}",
                    description=f"High volume ({
                        analysis.total_quantity} units) presents bulk purchasing opportunity.",
                    affected_components=[analysis.component_name],
                    current_cost=analysis.total_purchase_cost,
                    potential_savings=analysis.total_purchase_cost * 0.08,  # 8% bulk discount
                    margin_improvement_percent=3.0,
                    implementation_effort="low",
                    risk_level="low",
                    expected_timeframe="immediate",
                    priority_score=self._calculate_priority_score(
                        analysis, trend),
                    roi_estimate=4.0
                )
                suggestions.append(suggestion)
                suggestion_id += 1

            # Supplier optimization for expensive components
            if analysis.total_purchase_cost > 2000.0:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"SUPPLIER_{suggestion_id}",
                    type="supplier_optimization",
                    title=f"Evaluate alternative suppliers for {
                        analysis.component_name}",
                    description=f"High cost component (€{
                        analysis.total_purchase_cost:,.2f}) warrants supplier evaluation.",
                    affected_components=[analysis.component_name],
                    current_cost=analysis.total_purchase_cost,
                    potential_savings=analysis.total_purchase_cost *
                    0.12,  # 12% alternative supplier savings
                    margin_improvement_percent=4.0,
                    implementation_effort="high",
                    risk_level="medium",
                    expected_timeframe="long_term",
                    priority_score=self._calculate_priority_score(
                        analysis, trend),
                    roi_estimate=3.2
                )
                suggestions.append(suggestion)
                suggestion_id += 1

            # Trend-based suggestions
            if trend and trend.trend_direction == "increasing" and trend.trend_strength > 0.7:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"TREND_{suggestion_id}",
                    type="price_adjustment",
                    title=f"Adjust pricing for {
                        analysis.component_name} based on market trends",
                    description=f"Strong upward trend ({
                        trend.price_change_percent:.1f}%) suggests pricing adjustment opportunity.",
                    affected_components=[analysis.component_name],
                    current_cost=analysis.total_selling_price,
                    potential_savings=analysis.total_selling_price * 0.03,  # 3% price increase
                    margin_improvement_percent=2.5,
                    implementation_effort="low",
                    risk_level="medium",
                    expected_timeframe="immediate",
                    priority_score=self._calculate_priority_score(
                        analysis, trend),
                    roi_estimate=5.0
                )
                suggestions.append(suggestion)
                suggestion_id += 1

        # Sort by priority score
        suggestions.sort(key=lambda x: x.priority_score, reverse=True)

        return suggestions[:10]  # Return top 10 suggestions

    def _calculate_performance_metrics(
        self,
        aggregated_data: dict[str, Any],
        component_analyses: list[ComponentCostAnalysis]
    ) -> dict[str, float]:
        """Calculate key performance metrics"""

        total_revenue = aggregated_data["total_revenue"]
        total_costs = sum(
            analysis.total_purchase_cost for analysis in component_analyses)

        metrics = {
            "gross_margin_percent": (
                (total_revenue -
                 total_costs) /
                total_revenue *
                100) if total_revenue > 0 else 0.0,
            "average_component_margin": np.mean(
                [
                    a.average_margin_percent for a in component_analyses]) if component_analyses else 0.0,
            "margin_variance": np.var(
                [
                    a.average_margin_percent for a in component_analyses]) if component_analyses else 0.0,
            "cost_per_revenue_ratio": (
                total_costs /
                total_revenue) if total_revenue > 0 else 0.0,
            "high_margin_component_ratio": len(
                [
                    a for a in component_analyses if a.average_margin_percent > 20.0]) /
            len(component_analyses) if component_analyses else 0.0,
            "optimization_potential_ratio": sum(
                a.optimization_potential for a in component_analyses) /
            total_costs if total_costs > 0 else 0.0}

        return metrics

    def _generate_market_insights(
        self,
        component_analyses: list[ComponentCostAnalysis],
        pricing_trends: list[PricingTrendAnalysis]
    ) -> dict[str, Any]:
        """Generate market insights from analysis"""

        insights = {
            "market_position_distribution": {},
            "trend_summary": {},
            "competitive_analysis": {},
            "risk_assessment": {}
        }

        # Market position distribution
        position_counts = {}
        for analysis in component_analyses:
            position = analysis.market_position
            position_counts[position] = position_counts.get(position, 0) + 1

        insights["market_position_distribution"] = position_counts

        # Trend summary
        trend_counts = {}
        for trend in pricing_trends:
            direction = trend.trend_direction
            trend_counts[direction] = trend_counts.get(direction, 0) + 1

        insights["trend_summary"] = trend_counts

        # Competitive analysis
        insights["competitive_analysis"] = {
            "premium_components": len([a for a in component_analyses if a.market_position == "premium"]),
            "competitive_components": len([a for a in component_analyses if a.market_position == "competitive"]),
            "low_cost_components": len([a for a in component_analyses if a.market_position == "low_cost"])
        }

        # Risk assessment
        volatile_trends = [
            t for t in pricing_trends if t.volatility_index > 0.5]
        insights["risk_assessment"] = {
            "volatile_components": len(volatile_trends),
            "high_risk_components": [
                t.component_name for t in volatile_trends],
            "overall_risk_level": "high" if len(volatile_trends) > len(pricing_trends) *
            0.3 else "medium" if len(volatile_trends) > 0 else "low"}

        return insights

    def _calculate_total_costs(
            self,
            component_analyses: list[ComponentCostAnalysis]) -> float:
        """Calculate total costs from component analyses"""
        return sum(
            analysis.total_purchase_cost for analysis in component_analyses)

    def _determine_market_position(
        self,
        selling_price: float,
        margin_percent: float,
        category: str
    ) -> str:
        """Determine market position based on price and margin"""

        # Simple heuristic - could be enhanced with market data
        if margin_percent > 25.0:
            return "premium"
        if margin_percent > 15.0:
            return "competitive"
        return "low_cost"

    def _calculate_optimization_potential(
        self,
        total_cost: float,
        margin_percent: float,
        category: str
    ) -> float:
        """Calculate optimization potential for a component"""

        # Base potential on margin gap and cost magnitude
        target_margin = 20.0  # Target margin percentage
        margin_gap = max(0, target_margin - margin_percent)

        # Higher cost components have higher absolute potential
        cost_factor = min(1.0, total_cost / 5000.0)  # Normalize to €5000

        return total_cost * (margin_gap / 100.0) * cost_factor

    def _calculate_trend_direction(
            self, prices: np.ndarray) -> tuple[str, float]:
        """Calculate trend direction and strength"""

        if len(prices) < 2:
            return "insufficient_data", 0.0

        # Linear regression to determine trend
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)

        # Calculate trend strength (R-squared)
        y_pred = slope * x + intercept
        ss_res = np.sum((prices - y_pred) ** 2)
        ss_tot = np.sum((prices - np.mean(prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Calculate relative slope (slope as percentage of mean price)
        mean_price = np.mean(prices)
        relative_slope = abs(slope) / mean_price if mean_price > 0 else 0.0

        # Determine direction - use relative slope threshold
        if relative_slope < 0.02:  # Less than 2% change per period
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return direction, abs(r_squared)

    def _forecast_next_period(self, prices: np.ndarray) -> float:
        """Simple linear forecast for next period"""

        if len(prices) < 2:
            return prices[-1] if len(prices) > 0 else 0.0

        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)

        # Forecast next period
        next_x = len(prices)
        forecast = slope * next_x + intercept

        return max(0.0, forecast)  # Ensure non-negative

    def _calculate_forecast_confidence(
            self,
            prices: np.ndarray,
            volatility: float) -> float:
        """Calculate confidence level for forecast"""

        # Base confidence on data length and volatility
        # More data = higher confidence
        data_confidence = min(1.0, len(prices) / 12.0)
        # Lower volatility = higher confidence
        volatility_confidence = max(0.1, 1.0 - volatility)

        return (data_confidence + volatility_confidence) / 2.0

    def _calculate_priority_score(
        self,
        analysis: ComponentCostAnalysis,
        trend: PricingTrendAnalysis | None
    ) -> float:
        """Calculate priority score for optimization suggestions"""

        # Base score on potential savings and margin improvement
        savings_score = min(
            10.0,
            analysis.optimization_potential /
            1000.0)  # Normalize to €1000
        # Lower margin = higher score
        margin_score = max(0.0, 20.0 - analysis.average_margin_percent) / 2.0

        # Trend factor
        trend_score = 0.0
        if trend:
            if trend.trend_direction == "increasing":
                trend_score = trend.trend_strength * 2.0
            elif trend.trend_direction == "decreasing":
                trend_score = trend.trend_strength * -1.0

        return savings_score + margin_score + trend_score

    def _get_industry_benchmarks(self) -> dict[str, float]:
        """Get industry benchmarks for comparison"""

        # These would typically come from market research or industry data
        benchmarks = {
            "target_gross_margin_percent": 25.0,
            "excellent_gross_margin_percent": 35.0,
            "minimum_component_margin_percent": 15.0,
            "target_component_margin_percent": 20.0,
            "acceptable_volatility_index": 0.3,
            "high_volatility_threshold": 0.5
        }

        return benchmarks

    def _generate_report_keys(
            self, report_data: dict[str, Any]) -> dict[str, Any]:
        """Generate dynamic keys for profitability report"""

        # Format values for PDF display
        formatted_data = {}

        for key, value in report_data.items():
            if isinstance(value, float):
                if "percent" in key.lower() or "margin" in key.lower():
                    formatted_data[key.upper()] = f"{value:.1f}%"
                elif "revenue" in key.lower() or "cost" in key.lower() or "profit" in key.lower() or "potential" in key.lower():
                    formatted_data[key.upper()] = f"{value:,.2f}€"
                else:
                    formatted_data[key.upper()] = f"{value:.2f}"
            else:
                formatted_data[key.upper()] = str(value)

        # Generate keys with system type prefix
        return self.key_manager.generate_keys(
            formatted_data,
            prefix=f"{self.system_type.upper()}_PROFITABILITY_REPORT"
        )


def get_profitability_reporting_engine(
        system_type: str = "pv") -> ProfitabilityReportingEngine:
    """Factory function to get profitability reporting engine instance

    Args:
        system_type: Type of system ("pv", "heatpump", "combined")

    Returns:
        ProfitabilityReportingEngine instance
    """
    return ProfitabilityReportingEngine(system_type=system_type)


# Export main classes and functions
__all__ = [
    "ComponentCostAnalysis",
    "PricingTrendAnalysis",
    "OptimizationSuggestion",
    "ComprehensiveProfitabilityReport",
    "ProfitabilityReportingEngine",
    "get_profitability_reporting_engine"
]
