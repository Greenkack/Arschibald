"""
Tests for Financial Analysis Service
"""

import pytest
from decimal import Decimal

from ..models.financial_schemas import (
    FinancialAnalysisRequest,
    FinancingOption,
    FinancingType,
    TaxIncentive,
    TaxIncentiveType
)
from ..services.financial_analysis_service import FinancialAnalysisService


@pytest.fixture
def service():
    """Create financial analysis service instance"""
    return FinancialAnalysisService()


@pytest.fixture
def basic_request():
    """Create basic financial analysis request"""
    return FinancialAnalysisRequest(
        system_size_kwp=10.5,
        total_system_cost=16999.00,
        annual_production_kwh=12000,
        current_electricity_price=0.35,
        electricity_price_increase=3.0,
        feed_in_tariff=0.08,
        annual_consumption_kwh=4000,
        self_consumption_rate=35.0,
        system_degradation=0.5,
        maintenance_cost_annual=200.0,
        insurance_cost_annual=150.0,
        discount_rate=4.0,
        analysis_period_years=25
    )


@pytest.fixture
def request_with_financing():
    """Create request with financing options"""
    request = FinancialAnalysisRequest(
        system_size_kwp=10.5,
        total_system_cost=16999.00,
        annual_production_kwh=12000,
        current_electricity_price=0.35,
        electricity_price_increase=3.0,
        feed_in_tariff=0.08,
        annual_consumption_kwh=4000,
        self_consumption_rate=35.0,
        discount_rate=4.0,
        analysis_period_years=25
    )
    
    # Add financing options
    request.financing_options = [
        FinancingOption(
            type=FinancingType.CASH,
            name="Cash Purchase",
            down_payment=16999.00,
            down_payment_percent=100.0,
            loan_amount=0.0,
            interest_rate=0.0,
            term_years=0
        ),
        FinancingOption(
            type=FinancingType.LOAN,
            name="10-Year Loan",
            down_payment=3399.80,
            down_payment_percent=20.0,
            loan_amount=13599.20,
            interest_rate=5.0,
            term_years=10
        )
    ]
    
    return request


def test_comprehensive_analysis_basic(service, basic_request):
    """Test comprehensive analysis with basic parameters"""
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Check that all required fields are present
    assert result.system_size_kwp == 10.5
    assert result.total_system_cost == 16999.00
    assert result.analysis_period_years == 25
    
    # Check ROI analysis
    assert result.roi_analysis is not None
    assert result.roi_analysis.simple_roi_percent > 0
    assert result.roi_analysis.simple_payback_years > 0
    assert result.roi_analysis.total_lifetime_savings > 0
    
    # Check NPV analysis
    assert result.npv_analysis is not None
    assert result.npv_analysis.npv != 0
    assert result.npv_analysis.benefit_cost_ratio > 0
    
    # Check IRR analysis
    assert result.irr_analysis is not None
    assert result.irr_analysis.irr_percent != 0
    
    # Check cash flows
    assert len(result.yearly_cash_flows) == 25
    assert all(cf.year == i for i, cf in enumerate(result.yearly_cash_flows, 1))
    
    # Check environmental impact
    assert result.co2_savings_kg > 0
    assert result.trees_equivalent > 0
    
    # Check investment grade
    assert result.investment_grade in ["Excellent", "Good", "Fair", "Poor"]
    
    # Check key insights
    assert len(result.key_insights) > 0


def test_roi_calculation(service, basic_request):
    """Test ROI calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    roi = service._calculate_roi(basic_request, cash_flows)
    
    assert roi.simple_roi_percent > 0
    assert roi.simple_payback_years > 0
    assert roi.simple_payback_years < basic_request.analysis_period_years
    assert roi.total_lifetime_savings > 0
    assert roi.average_annual_return > 0
    assert roi.average_annual_return_percent > 0


def test_npv_calculation(service, basic_request):
    """Test NPV calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    npv = service._calculate_npv(basic_request, cash_flows)
    
    assert npv.npv != 0
    assert npv.present_value_benefits > 0
    assert npv.present_value_costs > 0
    assert npv.benefit_cost_ratio > 0
    
    # NPV should be positive for a good investment
    if npv.npv > 0:
        assert npv.npv_positive is True
        assert npv.benefit_cost_ratio > 1.0


def test_irr_calculation(service, basic_request):
    """Test IRR calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    irr = service._calculate_irr(basic_request, cash_flows)
    
    assert irr.irr_percent != 0
    assert irr.modified_irr_percent is not None
    
    # IRR should be reasonable (between -50% and 50%)
    assert -50 <= irr.irr_percent <= 50


def test_cash_flow_calculation(service, basic_request):
    """Test yearly cash flow calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    
    assert len(cash_flows) == basic_request.analysis_period_years
    
    # Check first year
    first_year = cash_flows[0]
    assert first_year.year == 1
    assert first_year.energy_production_kwh > 0
    assert first_year.self_consumed_kwh > 0
    assert first_year.exported_kwh > 0
    assert first_year.electricity_savings > 0
    assert first_year.feed_in_revenue > 0
    assert first_year.total_revenue > 0
    assert first_year.maintenance_cost > 0
    assert first_year.net_cash_flow != 0
    
    # Check that cumulative cash flow increases over time (for good investment)
    if cash_flows[-1].cumulative_cash_flow > 0:
        assert cash_flows[-1].cumulative_cash_flow > cash_flows[0].cumulative_cash_flow
    
    # Check degradation effect
    assert cash_flows[-1].energy_production_kwh < cash_flows[0].energy_production_kwh


def test_financing_comparison(service, request_with_financing):
    """Test financing options comparison"""
    cash_flows = service._calculate_yearly_cash_flows(request_with_financing)
    comparisons = service._compare_financing_options(request_with_financing, cash_flows)
    
    assert len(comparisons) == 2
    
    # Check that comparisons are ranked
    ranks = [c.rank for c in comparisons]
    assert sorted(ranks) == [1, 2]
    
    # Check cash option
    cash_option = next(c for c in comparisons if c.financing_type == FinancingType.CASH)
    assert cash_option.total_interest == 0
    assert cash_option.monthly_payment == 0
    
    # Check loan option
    loan_option = next(c for c in comparisons if c.financing_type == FinancingType.LOAN)
    assert loan_option.total_interest > 0
    assert loan_option.monthly_payment > 0
    assert loan_option.total_cost > request_with_financing.total_system_cost


def test_sensitivity_analysis(service, basic_request):
    """Test sensitivity analysis"""
    analyses = service._perform_sensitivity_analysis(basic_request)
    
    assert len(analyses) > 0
    
    for analysis in analyses:
        assert analysis.parameter in ["electricity_price", "system_cost", "self_consumption_rate", "discount_rate"]
        assert analysis.base_value > 0
        assert analysis.low_value < analysis.high_value
        assert analysis.npv_at_base != 0
        assert analysis.sensitivity_percent != 0


def test_monthly_payment_calculation(service):
    """Test monthly loan payment calculation"""
    # Test with 5% interest, 10 years, 10000 EUR
    payment = service._calculate_monthly_payment(10000, 5.0, 10)
    
    assert payment > 0
    assert payment < 200  # Should be around 106 EUR/month
    
    # Test with 0% interest
    payment_zero = service._calculate_monthly_payment(10000, 0.0, 10)
    assert abs(payment_zero - (10000 / 120)) < 0.01  # Should be exactly 10000/120


def test_payback_period_simple(service, basic_request):
    """Test simple payback period calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    payback = service._calculate_payback_period(cash_flows, discounted=False)
    
    assert payback > 0
    assert payback <= basic_request.analysis_period_years


def test_payback_period_discounted(service, basic_request):
    """Test discounted payback period calculation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    payback = service._calculate_payback_period(
        cash_flows, 
        discounted=True, 
        discount_rate=basic_request.discount_rate
    )
    
    assert payback > 0
    assert payback <= basic_request.analysis_period_years
    
    # Discounted payback should be longer than simple payback
    simple_payback = service._calculate_payback_period(cash_flows, discounted=False)
    assert payback >= simple_payback


def test_investment_grade_excellent(service):
    """Test investment grade determination for excellent investment"""
    npv = type('NPV', (), {'npv': 25000, 'npv_positive': True})()
    irr = type('IRR', (), {'irr_percent': 16.0})()
    roi = type('ROI', (), {'simple_payback_years': 7.0})()
    
    grade = service._determine_investment_grade(npv, irr, roi)
    assert grade == "Excellent"


def test_investment_grade_poor(service):
    """Test investment grade determination for poor investment"""
    npv = type('NPV', (), {'npv': -5000, 'npv_positive': False})()
    irr = type('IRR', (), {'irr_percent': 2.0})()
    roi = type('ROI', (), {'simple_payback_years': 20.0})()
    
    grade = service._determine_investment_grade(npv, irr, roi)
    assert grade == "Poor"


def test_key_insights_generation(service, basic_request):
    """Test key insights generation"""
    cash_flows = service._calculate_yearly_cash_flows(basic_request)
    roi = service._calculate_roi(basic_request, cash_flows)
    npv = service._calculate_npv(basic_request, cash_flows)
    irr = service._calculate_irr(basic_request, cash_flows)
    
    insights = service._generate_key_insights(basic_request, roi, npv, irr, [])
    
    assert len(insights) > 0
    assert all(isinstance(insight, str) for insight in insights)
    assert any("NPV" in insight for insight in insights)
    assert any("IRR" in insight for insight in insights)


def test_with_tax_incentives(service, basic_request):
    """Test analysis with tax incentives"""
    # Add tax incentives
    basic_request.tax_incentives = [
        TaxIncentive(
            type=TaxIncentiveType.GRANT,
            name="KfW Förderung",
            amount=2000.0,
            year_received=1
        ),
        TaxIncentive(
            type=TaxIncentiveType.DEPRECIATION,
            name="Degressive AfA",
            amount=1500.0,
            year_received=1
        )
    ]
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Tax benefits should improve NPV
    assert result.npv_analysis.npv > 0
    
    # Check that tax benefits are included in cash flows
    first_year = result.yearly_cash_flows[0]
    assert first_year.tax_benefit == 3500.0


def test_high_self_consumption(service, basic_request):
    """Test with high self-consumption rate"""
    basic_request.self_consumption_rate = 70.0
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Higher self-consumption should lead to better financial results
    assert result.roi_analysis.simple_payback_years < 15
    assert result.npv_analysis.npv > 0


def test_low_electricity_price(service, basic_request):
    """Test with low electricity price"""
    basic_request.current_electricity_price = 0.20
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Lower electricity price should lead to longer payback
    assert result.roi_analysis.simple_payback_years > 8


def test_high_system_cost(service, basic_request):
    """Test with high system cost"""
    basic_request.total_system_cost = 25000.00
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Higher cost should lead to longer payback
    assert result.roi_analysis.simple_payback_years > 10


def test_environmental_impact(service, basic_request):
    """Test environmental impact calculations"""
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Check CO2 savings
    expected_co2 = result.total_energy_produced_kwh * service.CO2_PER_KWH_KG
    assert abs(result.co2_savings_kg - expected_co2) < 1.0
    
    # Check trees equivalent
    expected_trees = int(result.co2_savings_kg / service.CO2_PER_TREE_KG)
    assert result.trees_equivalent == expected_trees


def test_edge_case_zero_consumption(service, basic_request):
    """Test edge case with zero self-consumption"""
    basic_request.self_consumption_rate = 0.0
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Should still calculate, but with lower returns
    assert result.roi_analysis.simple_payback_years > 0
    assert all(cf.self_consumed_kwh == 0 for cf in result.yearly_cash_flows)


def test_edge_case_100_percent_consumption(service, basic_request):
    """Test edge case with 100% self-consumption"""
    basic_request.self_consumption_rate = 100.0
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    # Should calculate with no feed-in revenue
    assert all(cf.exported_kwh == 0 for cf in result.yearly_cash_flows)
    assert all(cf.feed_in_revenue == 0 for cf in result.yearly_cash_flows)


def test_long_analysis_period(service, basic_request):
    """Test with long analysis period"""
    basic_request.analysis_period_years = 30
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    assert len(result.yearly_cash_flows) == 30
    assert result.analysis_period_years == 30


def test_short_analysis_period(service, basic_request):
    """Test with short analysis period"""
    basic_request.analysis_period_years = 10
    
    result = service.calculate_comprehensive_analysis(basic_request)
    
    assert len(result.yearly_cash_flows) == 10
    assert result.analysis_period_years == 10
