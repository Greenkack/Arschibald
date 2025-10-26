"""Tests for Profitability Reporting Module

Tests the comprehensive profitability analysis and reporting functionality
including profit margin analysis, pricing trends, and optimization suggestions.
"""

from datetime import datetime

import numpy as np
import pytest

from pricing.enhanced_pricing_engine import FinalPricingResult, PriceComponent
from pricing.pricing_errors import CalculationError

# Import the module under test
from pricing.profitability_reporting import (
    ComponentCostAnalysis,
    ComprehensiveProfitabilityReport,
    OptimizationSuggestion,
    PricingTrendAnalysis,
    ProfitabilityReportingEngine,
    get_profitability_reporting_engine,
)


class TestProfitabilityReportingEngine:
    """Test cases for ProfitabilityReportingEngine class"""

    @pytest.fixture
    def reporting_engine(self):
        """Create ProfitabilityReportingEngine instance for testing"""
        return ProfitabilityReportingEngine(system_type="pv")

    @pytest.fixture
    def sample_price_components(self):
        """Create sample price components for testing"""
        return [
            PriceComponent(
                product_id=1,
                model_name="PV Module A",
                category="pv_modules",
                brand="BrandA",
                quantity=20,
                price_euro=180.0,
                calculate_per="Stück",
                capacity_w=400.0,
                efficiency_percent=21.5,
                warranty_years=25
            ),
            PriceComponent(
                product_id=2,
                model_name="Inverter B",
                category="inverters",
                brand="BrandB",
                quantity=1,
                price_euro=800.0,
                calculate_per="Stück",
                power_kw=5.0,
                efficiency_percent=97.5,
                warranty_years=10
            ),
            PriceComponent(
                product_id=3,
                model_name="Battery C",
                category="batteries",
                brand="BrandC",
                quantity=2,
                price_euro=2500.0,
                calculate_per="Stück",
                capacity_w=5000.0,
                max_cycles=6000,
                warranty_years=15
            )
        ]

    @pytest.fixture
    def sample_final_pricing_results(self, sample_price_components):
        """Create sample final pricing results for testing"""
        return [
            FinalPricingResult(
                base_price=15000.0,
                components=sample_price_components,
                dynamic_keys={"PV_BASE_PRICE": "15000.00€"},
                metadata={"calculation_time": 0.1},
                final_price_net=14250.0,
                final_price_gross=16977.50,
                vat_amount=2727.50,
                total_discounts=750.0,
                total_surcharges=0.0
            ),
            FinalPricingResult(
                base_price=12000.0,
                # Only modules and inverter
                components=sample_price_components[:2],
                dynamic_keys={"PV_BASE_PRICE": "12000.00€"},
                metadata={"calculation_time": 0.08},
                final_price_net=11400.0,
                final_price_gross=13566.0,
                vat_amount=2166.0,
                total_discounts=600.0,
                total_surcharges=0.0
            )
        ]

    @pytest.fixture
    def sample_historical_data(self):
        """Create sample historical data for testing"""
        return {
            "pricing_history": {
                "PV Module A": [175.0, 178.0, 180.0, 182.0, 185.0],
                "Inverter B": [820.0, 810.0, 800.0, 795.0, 790.0],
                "Battery C": [2600.0, 2550.0, 2500.0, 2480.0, 2450.0]
            },
            "sales_history": {
                "PV Module A": [100, 120, 150, 180, 200],
                "Inverter B": [10, 12, 15, 18, 20],
                "Battery C": [5, 8, 10, 12, 15]
            }
        }

    def test_initialization(self):
        """Test ProfitabilityReportingEngine initialization"""
        engine = ProfitabilityReportingEngine(system_type="pv")

        assert engine.system_type == "pv"
        assert engine.key_manager is not None
        assert engine.validator is not None
        assert engine.logger is not None
        assert engine.economic_integration is not None

    def test_generate_comprehensive_report_success(
        self,
        reporting_engine,
        sample_final_pricing_results,
        sample_historical_data
    ):
        """Test successful comprehensive report generation"""

        report = reporting_engine.generate_comprehensive_report(
            sample_final_pricing_results,
            sample_historical_data,
            "Q1_2024"
        )

        # Verify report structure
        assert isinstance(report, ComprehensiveProfitabilityReport)
        assert report.system_type == "pv"
        assert report.analysis_period == "Q1_2024"

        # Verify financial metrics
        assert report.total_revenue > 0
        assert report.total_costs > 0
        assert report.gross_profit != 0
        assert report.gross_margin_percent != 0

        # Verify component analysis
        assert len(report.component_analyses) > 0
        assert len(report.top_profit_components) > 0

        # Verify trend analysis
        assert len(report.pricing_trends) > 0

        # Verify optimization suggestions
        assert len(report.optimization_suggestions) > 0
        assert report.total_optimization_potential > 0

        # Verify categorized suggestions
        assert isinstance(report.quick_wins, list)
        assert isinstance(report.strategic_initiatives, list)

        # Verify performance metrics
        assert len(report.performance_metrics) > 0
        assert "gross_margin_percent" in report.performance_metrics

        # Verify market insights
        assert len(report.market_insights) > 0
        assert "market_position_distribution" in report.market_insights

        # Verify dynamic keys
        assert len(report.dynamic_keys) > 0
        assert "PV_PROFITABILITY_REPORT_TOTAL_REVENUE" in report.dynamic_keys

    def test_generate_comprehensive_report_empty_results(
            self, reporting_engine):
        """Test comprehensive report with empty results (should raise error)"""

        with pytest.raises(CalculationError, match="final_pricing_results cannot be empty"):
            reporting_engine.generate_comprehensive_report([])

    def test_generate_comprehensive_report_invalid_results(
            self, reporting_engine):
        """Test comprehensive report with invalid results"""

        invalid_results = ["not_a_pricing_result", "another_invalid_item"]

        with pytest.raises(CalculationError, match="must be a FinalPricingResult"):
            reporting_engine.generate_comprehensive_report(invalid_results)

    def test_aggregate_pricing_data(
            self,
            reporting_engine,
            sample_final_pricing_results):
        """Test pricing data aggregation"""

        aggregated = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)

        assert isinstance(aggregated, dict)
        assert "components" in aggregated
        assert "total_revenue" in aggregated
        assert "total_base_cost" in aggregated
        assert "result_count" in aggregated

        # Verify aggregation correctness
        assert aggregated["result_count"] == 2
        assert aggregated["total_revenue"] == 14250.0 + \
            11400.0  # Sum of final prices
        assert aggregated["total_base_cost"] == 15000.0 + \
            12000.0  # Sum of base prices

        # Verify component aggregation
        assert len(aggregated["components"]) > 0

        # Check specific component aggregation
        pv_module_key = "pv_modules_PV Module A"
        if pv_module_key in aggregated["components"]:
            comp_data = aggregated["components"][pv_module_key]
            # 20 + 20 from both results
            assert comp_data["total_quantity"] == 40
            assert comp_data["occurrences"] == 2

    def test_analyze_component_costs(
            self,
            reporting_engine,
            sample_final_pricing_results):
        """Test component cost analysis"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        analyses = reporting_engine._analyze_component_costs(aggregated_data)

        assert isinstance(analyses, list)
        assert len(analyses) > 0

        # Verify analysis structure
        for analysis in analyses:
            assert isinstance(analysis, ComponentCostAnalysis)
            assert analysis.component_name is not None
            assert analysis.category is not None
            assert analysis.total_quantity > 0
            assert analysis.total_purchase_cost >= 0
            assert analysis.total_selling_price > 0
            assert analysis.market_position in [
                "low_cost", "competitive", "premium"]
            assert analysis.optimization_potential >= 0

    def test_analyze_pricing_trends_with_data(
        self,
        reporting_engine,
        sample_final_pricing_results,
        sample_historical_data
    ):
        """Test pricing trend analysis with historical data"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        component_analyses = reporting_engine._analyze_component_costs(
            aggregated_data)

        trends = reporting_engine._analyze_pricing_trends(
            component_analyses, sample_historical_data)

        assert isinstance(trends, list)
        assert len(trends) > 0

        # Verify trend structure
        for trend in trends:
            assert isinstance(trend, PricingTrendAnalysis)
            assert trend.component_name is not None
            assert trend.trend_direction in [
                "increasing",
                "decreasing",
                "stable",
                "volatile",
                "insufficient_data"]
            assert 0.0 <= trend.trend_strength <= 1.0
            assert 0.0 <= trend.confidence_level <= 1.0
            assert trend.forecast_next_period >= 0

    def test_analyze_pricing_trends_without_data(
            self, reporting_engine, sample_final_pricing_results):
        """Test pricing trend analysis without historical data"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        component_analyses = reporting_engine._analyze_component_costs(
            aggregated_data)

        trends = reporting_engine._analyze_pricing_trends(
            component_analyses, None)

        assert isinstance(trends, list)
        assert len(trends) > 0

        # All trends should be "stable" without historical data
        for trend in trends:
            assert trend.trend_direction == "stable"
            assert trend.trend_strength == 0.5
            assert trend.confidence_level == 0.6

    def test_generate_advanced_optimization_suggestions(
        self,
        reporting_engine,
        sample_final_pricing_results,
        sample_historical_data
    ):
        """Test advanced optimization suggestion generation"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        component_analyses = reporting_engine._analyze_component_costs(
            aggregated_data)
        pricing_trends = reporting_engine._analyze_pricing_trends(
            component_analyses, sample_historical_data)

        suggestions = reporting_engine._generate_advanced_optimization_suggestions(
            component_analyses, pricing_trends)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Verify suggestion structure
        for suggestion in suggestions:
            assert isinstance(suggestion, OptimizationSuggestion)
            assert suggestion.suggestion_id is not None
            assert suggestion.type is not None
            assert suggestion.title is not None
            assert suggestion.description is not None
            assert len(suggestion.affected_components) > 0
            assert suggestion.current_cost >= 0
            assert suggestion.potential_savings >= 0
            assert suggestion.implementation_effort in [
                "low", "medium", "high"]
            assert suggestion.risk_level in ["low", "medium", "high"]
            assert suggestion.expected_timeframe in [
                "immediate", "short_term", "long_term"]
            assert suggestion.priority_score >= 0
            assert suggestion.roi_estimate >= 0

        # Verify suggestions are sorted by priority
        priorities = [s.priority_score for s in suggestions]
        assert priorities == sorted(priorities, reverse=True)

    def test_calculate_performance_metrics(
            self, reporting_engine, sample_final_pricing_results):
        """Test performance metrics calculation"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        component_analyses = reporting_engine._analyze_component_costs(
            aggregated_data)

        metrics = reporting_engine._calculate_performance_metrics(
            aggregated_data, component_analyses)

        assert isinstance(metrics, dict)
        assert len(metrics) > 0

        # Verify required metrics
        required_metrics = [
            "gross_margin_percent",
            "average_component_margin",
            "margin_variance",
            "cost_per_revenue_ratio",
            "high_margin_component_ratio",
            "optimization_potential_ratio"
        ]

        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
            assert metrics[metric] >= 0  # All metrics should be non-negative

    def test_generate_market_insights(
            self,
            reporting_engine,
            sample_final_pricing_results,
            sample_historical_data):
        """Test market insights generation"""

        aggregated_data = reporting_engine._aggregate_pricing_data(
            sample_final_pricing_results)
        component_analyses = reporting_engine._analyze_component_costs(
            aggregated_data)
        pricing_trends = reporting_engine._analyze_pricing_trends(
            component_analyses, sample_historical_data)

        insights = reporting_engine._generate_market_insights(
            component_analyses, pricing_trends)

        assert isinstance(insights, dict)
        assert len(insights) > 0

        # Verify required insight categories
        required_categories = [
            "market_position_distribution",
            "trend_summary",
            "competitive_analysis",
            "risk_assessment"
        ]

        for category in required_categories:
            assert category in insights
            assert isinstance(insights[category], dict)

        # Verify competitive analysis structure
        competitive_analysis = insights["competitive_analysis"]
        assert "premium_components" in competitive_analysis
        assert "competitive_components" in competitive_analysis
        assert "low_cost_components" in competitive_analysis

        # Verify risk assessment structure
        risk_assessment = insights["risk_assessment"]
        assert "volatile_components" in risk_assessment
        assert "high_risk_components" in risk_assessment
        assert "overall_risk_level" in risk_assessment
        assert risk_assessment["overall_risk_level"] in [
            "low", "medium", "high"]

    def test_calculate_trend_direction(self, reporting_engine):
        """Test trend direction calculation"""

        # Test increasing trend
        increasing_prices = np.array([100.0, 105.0, 110.0, 115.0, 120.0])
        direction, strength = reporting_engine._calculate_trend_direction(
            increasing_prices)
        assert direction == "increasing"
        assert strength > 0.8  # Should be strong trend

        # Test decreasing trend
        decreasing_prices = np.array([120.0, 115.0, 110.0, 105.0, 100.0])
        direction, strength = reporting_engine._calculate_trend_direction(
            decreasing_prices)
        assert direction == "decreasing"
        assert strength > 0.8  # Should be strong trend

        # Test stable trend
        stable_prices = np.array([100.0, 101.0, 99.0, 100.5, 99.5])
        direction, strength = reporting_engine._calculate_trend_direction(
            stable_prices)
        assert direction == "stable"

        # Test insufficient data
        single_price = np.array([100.0])
        direction, strength = reporting_engine._calculate_trend_direction(
            single_price)
        assert direction == "insufficient_data"
        assert strength == 0.0

    def test_forecast_next_period(self, reporting_engine):
        """Test next period forecasting"""

        # Test with increasing trend
        increasing_prices = np.array([100.0, 105.0, 110.0, 115.0, 120.0])
        forecast = reporting_engine._forecast_next_period(increasing_prices)
        assert forecast > 120.0  # Should forecast higher price

        # Test with decreasing trend
        decreasing_prices = np.array([120.0, 115.0, 110.0, 105.0, 100.0])
        forecast = reporting_engine._forecast_next_period(decreasing_prices)
        assert forecast < 100.0  # Should forecast lower price

        # Test with single data point
        single_price = np.array([100.0])
        forecast = reporting_engine._forecast_next_period(single_price)
        assert forecast == 100.0  # Should return same price

        # Test with empty array
        empty_prices = np.array([])
        forecast = reporting_engine._forecast_next_period(empty_prices)
        assert forecast == 0.0  # Should return 0

    def test_calculate_priority_score(self, reporting_engine):
        """Test priority score calculation"""

        # Create sample analysis
        high_priority_analysis = ComponentCostAnalysis(
            component_name="High Priority Component",
            category="test",
            total_quantity=10,
            total_purchase_cost=5000.0,
            total_selling_price=6000.0,
            average_margin_percent=10.0,  # Low margin
            cost_per_unit=500.0,
            selling_price_per_unit=600.0,
            profit_per_unit=100.0,
            market_position="low_cost",
            optimization_potential=1000.0  # High potential
        )

        # Create sample trend
        positive_trend = PricingTrendAnalysis(
            component_name="High Priority Component",
            trend_direction="increasing",
            trend_strength=0.8,
            price_change_percent=10.0,
            volatility_index=0.2,
            forecast_next_period=650.0,
            confidence_level=0.9
        )

        score = reporting_engine._calculate_priority_score(
            high_priority_analysis, positive_trend)

        assert isinstance(score, float)
        assert score > 0  # Should have positive score

        # Test with no trend
        score_no_trend = reporting_engine._calculate_priority_score(
            high_priority_analysis, None)
        assert isinstance(score_no_trend, float)
        assert score_no_trend >= 0

    def test_get_industry_benchmarks(self, reporting_engine):
        """Test industry benchmarks retrieval"""

        benchmarks = reporting_engine._get_industry_benchmarks()

        assert isinstance(benchmarks, dict)
        assert len(benchmarks) > 0

        # Verify required benchmarks
        required_benchmarks = [
            "target_gross_margin_percent",
            "excellent_gross_margin_percent",
            "minimum_component_margin_percent",
            "target_component_margin_percent",
            "acceptable_volatility_index",
            "high_volatility_threshold"
        ]

        for benchmark in required_benchmarks:
            assert benchmark in benchmarks
            assert isinstance(benchmarks[benchmark], (int, float))
            assert benchmarks[benchmark] > 0

    def test_generate_report_keys(self, reporting_engine):
        """Test report dynamic key generation"""

        report_data = {
            "total_revenue": 25000.0,
            "gross_margin_percent": 22.5,
            "optimization_potential": 1500.0,
            "component_count": 5
        }

        keys = reporting_engine._generate_report_keys(report_data)

        assert isinstance(keys, dict)
        assert len(keys) > 0

        # Check key formatting
        assert "PV_PROFITABILITY_REPORT_TOTAL_REVENUE" in keys
        assert "PV_PROFITABILITY_REPORT_GROSS_MARGIN_PERCENT" in keys

        # Check value formatting
        assert "€" in keys["PV_PROFITABILITY_REPORT_TOTAL_REVENUE"]
        assert "%" in keys["PV_PROFITABILITY_REPORT_GROSS_MARGIN_PERCENT"]


class TestFactoryFunction:
    """Test cases for factory function"""

    def test_get_profitability_reporting_engine_default(self):
        """Test factory function with default parameters"""
        engine = get_profitability_reporting_engine()

        assert isinstance(engine, ProfitabilityReportingEngine)
        assert engine.system_type == "pv"

    def test_get_profitability_reporting_engine_custom_type(self):
        """Test factory function with custom system type"""
        engine = get_profitability_reporting_engine("heatpump")

        assert isinstance(engine, ProfitabilityReportingEngine)
        assert engine.system_type == "heatpump"


class TestDataClasses:
    """Test cases for data classes"""

    def test_component_cost_analysis_creation(self):
        """Test ComponentCostAnalysis creation"""
        analysis = ComponentCostAnalysis(
            component_name="Test Component",
            category="test_category",
            total_quantity=10,
            total_purchase_cost=1000.0,
            total_selling_price=1200.0,
            average_margin_percent=16.7,
            cost_per_unit=100.0,
            selling_price_per_unit=120.0,
            profit_per_unit=20.0,
            market_position="competitive",
            optimization_potential=50.0
        )

        assert analysis.component_name == "Test Component"
        assert analysis.total_quantity == 10
        assert analysis.average_margin_percent == 16.7
        assert analysis.market_position == "competitive"

    def test_pricing_trend_analysis_creation(self):
        """Test PricingTrendAnalysis creation"""
        trend = PricingTrendAnalysis(
            component_name="Test Component",
            trend_direction="increasing",
            trend_strength=0.8,
            price_change_percent=5.5,
            volatility_index=0.3,
            forecast_next_period=125.0,
            confidence_level=0.85
        )

        assert trend.component_name == "Test Component"
        assert trend.trend_direction == "increasing"
        assert trend.trend_strength == 0.8
        assert trend.confidence_level == 0.85

    def test_optimization_suggestion_creation(self):
        """Test OptimizationSuggestion creation"""
        suggestion = OptimizationSuggestion(
            suggestion_id="TEST_001",
            type="margin_improvement",
            title="Test Suggestion",
            description="This is a test suggestion",
            affected_components=["Component A", "Component B"],
            current_cost=1000.0,
            potential_savings=100.0,
            margin_improvement_percent=2.5,
            implementation_effort="medium",
            risk_level="low",
            expected_timeframe="short_term",
            priority_score=7.5,
            roi_estimate=3.2
        )

        assert suggestion.suggestion_id == "TEST_001"
        assert suggestion.type == "margin_improvement"
        assert len(suggestion.affected_components) == 2
        assert suggestion.priority_score == 7.5

    def test_comprehensive_profitability_report_creation(self):
        """Test ComprehensiveProfitabilityReport creation"""
        report = ComprehensiveProfitabilityReport(
            total_revenue=25000.0,
            total_costs=18000.0,
            gross_profit=7000.0,
            gross_margin_percent=28.0,
            component_analyses=[],
            top_profit_components=[],
            low_margin_components=[],
            pricing_trends=[],
            market_insights={},
            optimization_suggestions=[],
            total_optimization_potential=1500.0,
            quick_wins=[],
            strategic_initiatives=[],
            performance_metrics={},
            benchmarks={}
        )

        assert report.total_revenue == 25000.0
        assert report.gross_margin_percent == 28.0
        assert report.system_type == "pv"  # Default value
        assert isinstance(report.report_timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__])
