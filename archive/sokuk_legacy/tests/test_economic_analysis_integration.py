"""Tests for Economic Analysis Integration

Tests the integration between enhanced pricing system and economic calculations
for accurate payback period, ROI, and profitability analysis.
"""

from datetime import datetime

import pytest

# Import the module under test
from pricing.economic_analysis_integration import (
    EconomicAnalysisIntegration,
    EconomicAnalysisResult,
    ProfitabilityReport,
    get_economic_analysis_integration,
)
from pricing.enhanced_pricing_engine import (
    FinalPricingResult,
    PriceComponent,
)
from pricing.pricing_errors import CalculationError


class TestEconomicAnalysisIntegration:
    """Test cases for EconomicAnalysisIntegration class"""

    @pytest.fixture
    def integration(self):
        """Create EconomicAnalysisIntegration instance for testing"""
        return EconomicAnalysisIntegration(system_type="pv")

    @pytest.fixture
    def sample_price_component(self):
        """Create sample price component for testing"""
        return PriceComponent(
            product_id=1,
            model_name="Test PV Module",
            category="pv_modules",
            brand="TestBrand",
            quantity=20,
            price_euro=180.0,
            calculate_per="Stück",
            capacity_w=400.0,
            efficiency_percent=21.5,
            warranty_years=25
        )

    @pytest.fixture
    def sample_final_pricing_result(self, sample_price_component):
        """Create sample final pricing result for testing"""
        return FinalPricingResult(
            base_price=15000.0,
            components=[sample_price_component],
            dynamic_keys={"PV_BASE_PRICE": "15000.00€"},
            metadata={"calculation_time": 0.1},
            final_price_net=14250.0,
            final_price_gross=16977.50,
            vat_amount=2727.50,
            total_discounts=750.0,
            total_surcharges=0.0
        )

    @pytest.fixture
    def sample_system_performance(self):
        """Create sample system performance data"""
        return {
            "annual_production_kwh": 12000.0,
            "self_consumption_kwh": 8000.0,
            "feed_in_kwh": 4000.0,
            "system_power_kwp": 8.0
        }

    @pytest.fixture
    def sample_economic_parameters(self):
        """Create sample economic parameters"""
        return {
            "electricity_price_kwh": 0.32,
            "feed_in_tariff_kwh": 0.082,
            "discount_rate": 0.04,
            "analysis_years": 25
        }

    def test_initialization(self):
        """Test EconomicAnalysisIntegration initialization"""
        integration = EconomicAnalysisIntegration(system_type="pv")

        assert integration.system_type == "pv"
        assert integration.key_manager is not None
        assert integration.validator is not None
        assert integration.logger is not None

    def test_calculate_economic_analysis_success(
        self,
        integration,
        sample_final_pricing_result,
        sample_system_performance,
        sample_economic_parameters
    ):
        """Test successful economic analysis calculation"""

        result = integration.calculate_economic_analysis(
            sample_final_pricing_result,
            sample_system_performance,
            sample_economic_parameters
        )

        # Verify result type and basic structure
        assert isinstance(result, EconomicAnalysisResult)
        assert result.total_investment_net == 14250.0
        assert result.total_investment_gross == 16977.50
        assert result.system_type == "pv"

        # Verify economic calculations
        assert result.annual_savings > 0  # Should have savings from self-consumption
        assert result.annual_feed_in_revenue > 0  # Should have feed-in revenue
        assert result.total_annual_benefit > 0
        assert result.payback_period_years > 0
        assert result.roi_percent != 0

        # Verify environmental calculations
        assert result.annual_co2_savings_kg > 0
        assert result.co2_payback_years > 0
        assert result.lifetime_co2_savings_tons > 0

        # Verify dynamic keys are generated
        assert len(result.dynamic_keys) > 0
        assert "PV_ECONOMIC_TOTAL_INVESTMENT_NET" in result.dynamic_keys

        # Verify pricing breakdown
        assert "base_price" in result.final_pricing_breakdown
        assert "final_net" in result.final_pricing_breakdown

    def test_calculate_economic_analysis_with_zero_investment(
        self,
        integration,
        sample_system_performance,
        sample_economic_parameters
    ):
        """Test economic analysis with zero investment (should raise error)"""

        # Create pricing result with zero investment
        zero_pricing_result = FinalPricingResult(
            base_price=0.0,
            components=[],
            dynamic_keys={},
            metadata={},
            final_price_net=0.0,
            final_price_gross=0.0,
            vat_amount=0.0,
            total_discounts=0.0,
            total_surcharges=0.0
        )

        with pytest.raises(CalculationError, match="Final price net must be positive"):
            integration.calculate_economic_analysis(
                zero_pricing_result,
                sample_system_performance,
                sample_economic_parameters
            )

    def test_calculate_economic_analysis_missing_performance_data(
        self,
        integration,
        sample_final_pricing_result,
        sample_economic_parameters
    ):
        """Test economic analysis with missing system performance data"""

        incomplete_performance = {
            "annual_production_kwh": 12000.0
            # Missing self_consumption_kwh and feed_in_kwh
        }

        with pytest.raises(CalculationError, match="Missing required system performance field"):
            integration.calculate_economic_analysis(
                sample_final_pricing_result,
                incomplete_performance,
                sample_economic_parameters
            )

    def test_calculate_economic_analysis_missing_economic_parameters(
        self,
        integration,
        sample_final_pricing_result,
        sample_system_performance
    ):
        """Test economic analysis with missing economic parameters"""

        incomplete_parameters = {
            "electricity_price_kwh": 0.32
            # Missing feed_in_tariff_kwh
        }

        with pytest.raises(CalculationError, match="Missing required economic parameter"):
            integration.calculate_economic_analysis(
                sample_final_pricing_result,
                sample_system_performance,
                incomplete_parameters
            )

    def test_create_profitability_report_success(
        self,
        integration,
        sample_final_pricing_result
    ):
        """Test successful profitability report creation"""

        # Add purchase price data to component for testing
        component = sample_final_pricing_result.components[0]
        component.purchase_price = 150.0  # Add purchase price attribute

        historical_data = {
            "Test PV Module": [150.0, 155.0, 160.0, 158.0, 162.0]
        }

        report = integration.create_profitability_report(
            sample_final_pricing_result,
            historical_data
        )

        # Verify report structure
        assert isinstance(report, ProfitabilityReport)
        assert report.total_purchase_cost > 0
        assert report.total_selling_price > 0
        assert report.gross_profit != 0
        assert report.gross_margin_percent != 0

        # Verify component analysis
        assert len(report.component_margins) > 0
        component_margin = report.component_margins[0]
        assert "component_name" in component_margin
        assert "margin_percent" in component_margin
        assert "total_purchase_cost" in component_margin

        # Verify optimization suggestions
        assert isinstance(report.optimization_suggestions, list)
        assert report.potential_savings >= 0
        assert report.margin_improvement_potential >= 0

        # Verify dynamic keys
        assert len(report.dynamic_keys) > 0
        assert "PV_PROFITABILITY_GROSS_MARGIN_PERCENT" in report.dynamic_keys

    def test_create_profitability_report_no_components(self, integration):
        """Test profitability report with no components"""

        empty_pricing_result = FinalPricingResult(
            base_price=1000.0,
            components=[],
            dynamic_keys={},
            metadata={},
            final_price_net=1000.0,
            final_price_gross=1190.0,
            vat_amount=190.0,
            total_discounts=0.0,
            total_surcharges=0.0
        )

        report = integration.create_profitability_report(empty_pricing_result)

        assert isinstance(report, ProfitabilityReport)
        assert len(report.component_margins) == 0
        assert report.highest_margin_component == {}
        assert report.lowest_margin_component == {}

    def test_analyze_pricing_trends(self, integration):
        """Test pricing trend analysis"""

        pricing_trends = {
            "increasing_component": [100.0, 105.0, 110.0, 115.0, 120.0],
            "decreasing_component": [200.0, 190.0, 180.0, 170.0, 160.0],
            "stable_component": [150.0, 151.0, 149.0, 152.0, 150.0],
            "insufficient_data": [100.0]
        }

        trend_analysis = integration._analyze_pricing_trends(pricing_trends)

        assert trend_analysis["increasing_component"] == "increasing"
        assert trend_analysis["decreasing_component"] == "decreasing"
        assert trend_analysis["stable_component"] == "stable"
        assert trend_analysis["insufficient_data"] == "insufficient_data"

    def test_generate_optimization_suggestions(self, integration):
        """Test optimization suggestion generation"""

        component_margins = [
            {
                "component_name": "Low Margin Component",
                "margin_percent": 8.0,
                "quantity": 5,
                "total_selling_price": 1000.0,
                "total_purchase_cost": 920.0
            },
            {
                "component_name": "High Volume Component",
                "margin_percent": 18.0,
                "quantity": 25,
                "total_selling_price": 2500.0,
                "total_purchase_cost": 2050.0
            },
            {
                "component_name": "Expensive Component",
                "margin_percent": 15.0,
                "quantity": 2,
                "total_selling_price": 3000.0,
                "total_purchase_cost": 2550.0
            }
        ]

        suggestions = integration._generate_optimization_suggestions(
            component_margins, 15.0)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Check for different types of suggestions
        suggestion_types = [s["type"] for s in suggestions]
        assert "margin_improvement" in suggestion_types  # For low margin component
        assert "bulk_purchasing" in suggestion_types  # For high volume component
        assert "supplier_optimization" in suggestion_types  # For expensive component

        # Verify suggestion structure
        for suggestion in suggestions:
            assert "type" in suggestion
            assert "description" in suggestion
            assert "priority" in suggestion
            assert "potential_savings" in suggestion

    def test_generate_economic_keys(self, integration):
        """Test economic dynamic key generation"""

        economic_data = {
            "total_investment_net": 15000.0,
            "annual_savings": 2400.0,
            "payback_period_years": 6.25,
            "roi_percent": 12.5,
            "annual_co2_savings_kg": 5688.0
        }

        keys = integration._generate_economic_keys(economic_data)

        assert isinstance(keys, dict)
        assert len(keys) > 0

        # Check key formatting
        assert "PV_ECONOMIC_TOTAL_INVESTMENT_NET" in keys
        assert "PV_ECONOMIC_ANNUAL_SAVINGS" in keys
        assert "PV_ECONOMIC_PAYBACK_PERIOD_YEARS" in keys
        assert "PV_ECONOMIC_ROI_PERCENT" in keys
        assert "PV_ECONOMIC_ANNUAL_CO2_SAVINGS_KG" in keys

        # Check value formatting
        assert "€" in keys["PV_ECONOMIC_TOTAL_INVESTMENT_NET"]
        assert "%" in keys["PV_ECONOMIC_ROI_PERCENT"]
        assert "Jahre" in keys["PV_ECONOMIC_PAYBACK_PERIOD_YEARS"]
        assert "kg" in keys["PV_ECONOMIC_ANNUAL_CO2_SAVINGS_KG"]

    def test_generate_profitability_keys(self, integration):
        """Test profitability dynamic key generation"""

        profitability_data = {
            "total_purchase_cost": 12000.0,
            "total_selling_price": 15000.0,
            "gross_profit": 3000.0,
            "gross_margin_percent": 20.0,
            "potential_savings": 500.0,
            "component_count": 5
        }

        keys = integration._generate_profitability_keys(profitability_data)

        assert isinstance(keys, dict)
        assert len(keys) > 0

        # Check key formatting
        assert "PV_PROFITABILITY_TOTAL_PURCHASE_COST" in keys
        assert "PV_PROFITABILITY_GROSS_MARGIN_PERCENT" in keys
        assert "PV_PROFITABILITY_POTENTIAL_SAVINGS" in keys

        # Check value formatting
        assert "€" in keys["PV_PROFITABILITY_TOTAL_PURCHASE_COST"]
        assert "%" in keys["PV_PROFITABILITY_GROSS_MARGIN_PERCENT"]


class TestFactoryFunction:
    """Test cases for factory function"""

    def test_get_economic_analysis_integration_default(self):
        """Test factory function with default parameters"""
        integration = get_economic_analysis_integration()

        assert isinstance(integration, EconomicAnalysisIntegration)
        assert integration.system_type == "pv"

    def test_get_economic_analysis_integration_custom_type(self):
        """Test factory function with custom system type"""
        integration = get_economic_analysis_integration("heatpump")

        assert isinstance(integration, EconomicAnalysisIntegration)
        assert integration.system_type == "heatpump"


class TestDataClasses:
    """Test cases for data classes"""

    def test_economic_analysis_result_creation(self):
        """Test EconomicAnalysisResult creation"""
        result = EconomicAnalysisResult(
            total_investment_net=15000.0,
            total_investment_gross=17850.0,
            final_pricing_breakdown={"base_price": 15000.0},
            annual_production_kwh=12000.0,
            self_consumption_kwh=8000.0,
            feed_in_kwh=4000.0,
            electricity_price_kwh=0.32,
            feed_in_tariff_kwh=0.082,
            annual_savings=2560.0,
            annual_feed_in_revenue=328.0,
            total_annual_benefit=2888.0,
            payback_period_years=5.2,
            roi_percent=15.8,
            npv_eur=8500.0,
            irr_percent=18.2,
            annual_co2_savings_kg=5688.0,
            co2_payback_years=2.1,
            lifetime_co2_savings_tons=142.2
        )

        assert result.total_investment_net == 15000.0
        assert result.payback_period_years == 5.2
        assert result.system_type == "pv"  # Default value
        assert isinstance(result.calculation_timestamp, datetime)

    def test_profitability_report_creation(self):
        """Test ProfitabilityReport creation"""
        report = ProfitabilityReport(
            total_purchase_cost=12000.0,
            total_selling_price=15000.0,
            gross_profit=3000.0,
            gross_margin_percent=20.0,
            component_margins=[],
            highest_margin_component={},
            lowest_margin_component={},
            pricing_trends={},
            trend_analysis={},
            optimization_suggestions=[],
            potential_savings=500.0,
            margin_improvement_potential=2.5
        )

        assert report.gross_profit == 3000.0
        assert report.gross_margin_percent == 20.0
        assert report.analysis_period == "current"  # Default value
        assert isinstance(report.report_timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__])
