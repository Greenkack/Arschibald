"""
Demo script for Solar Financial Analysis Service
Demonstrates all features of the financial analysis system
"""

import asyncio
from models.financial_schemas import (
    FinancialAnalysisRequest,
    FinancingOption,
    FinancingType,
    TaxIncentive,
    TaxIncentiveType
)
from services.financial_analysis_service import FinancialAnalysisService


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_basic_analysis():
    """Demonstrate basic financial analysis"""
    print_section("DEMO 1: Basic Financial Analysis")
    
    # Create service
    service = FinancialAnalysisService()
    
    # Create basic request
    request = FinancialAnalysisRequest(
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
    
    # Calculate analysis
    result = service.calculate_comprehensive_analysis(request)
    
    # Print results
    print(f"System Size: {result.system_size_kwp} kWp")
    print(f"Total Cost: €{result.total_system_cost:,.2f}")
    print(f"Analysis Period: {result.analysis_period_years} years")
    print()
    
    print("ROI ANALYSIS:")
    print(f"  Simple ROI: {result.roi_analysis.simple_roi_percent:.1f}%")
    print(f"  Simple Payback: {result.roi_analysis.simple_payback_years:.1f} years")
    print(f"  Discounted Payback: {result.roi_analysis.discounted_payback_years:.1f} years")
    print(f"  Total Lifetime Savings: €{result.roi_analysis.total_lifetime_savings:,.2f}")
    print(f"  Average Annual Return: €{result.roi_analysis.average_annual_return:,.2f} ({result.roi_analysis.average_annual_return_percent:.1f}%)")
    print()
    
    print("NPV ANALYSIS:")
    print(f"  Net Present Value: €{result.npv_analysis.npv:,.2f}")
    print(f"  NPV Positive: {result.npv_analysis.npv_positive}")
    print(f"  Present Value of Benefits: €{result.npv_analysis.present_value_benefits:,.2f}")
    print(f"  Present Value of Costs: €{result.npv_analysis.present_value_costs:,.2f}")
    print(f"  Benefit-Cost Ratio: {result.npv_analysis.benefit_cost_ratio:.2f}")
    print()
    
    print("IRR ANALYSIS:")
    print(f"  Internal Rate of Return: {result.irr_analysis.irr_percent:.2f}%")
    print(f"  IRR Exceeds Discount Rate: {result.irr_analysis.irr_exceeds_discount_rate}")
    print(f"  Modified IRR: {result.irr_analysis.modified_irr_percent:.2f}%")
    print()
    
    print("ENVIRONMENTAL IMPACT:")
    print(f"  Total Energy Produced: {result.total_energy_produced_kwh:,.0f} kWh")
    print(f"  CO2 Savings: {result.co2_savings_kg:,.0f} kg")
    print(f"  Trees Equivalent: {result.trees_equivalent:,} trees")
    print()
    
    print(f"INVESTMENT GRADE: {result.investment_grade}")
    print()
    
    print("KEY INSIGHTS:")
    for i, insight in enumerate(result.key_insights, 1):
        print(f"  {i}. {insight}")


def demo_financing_comparison():
    """Demonstrate financing options comparison"""
    print_section("DEMO 2: Financing Options Comparison")
    
    service = FinancialAnalysisService()
    
    # Create request with multiple financing options
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
        analysis_period_years=25,
        financing_options=[
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
                name="5-Year Loan (20% down)",
                down_payment=3399.80,
                down_payment_percent=20.0,
                loan_amount=13599.20,
                interest_rate=4.5,
                term_years=5
            ),
            FinancingOption(
                type=FinancingType.LOAN,
                name="10-Year Loan (20% down)",
                down_payment=3399.80,
                down_payment_percent=20.0,
                loan_amount=13599.20,
                interest_rate=5.0,
                term_years=10
            ),
            FinancingOption(
                type=FinancingType.LOAN,
                name="10-Year Loan (0% down)",
                down_payment=0.0,
                down_payment_percent=0.0,
                loan_amount=16999.00,
                interest_rate=6.0,
                term_years=10
            )
        ]
    )
    
    result = service.calculate_comprehensive_analysis(request)
    
    print("FINANCING OPTIONS COMPARISON:")
    print()
    
    for comp in result.financing_comparisons:
        print(f"Rank #{comp.rank}: {comp.option_name}")
        print(f"  Type: {comp.financing_type.value}")
        print(f"  Monthly Payment: €{comp.monthly_payment:,.2f}")
        print(f"  Total Interest: €{comp.total_interest:,.2f}")
        print(f"  Total Cost: €{comp.total_cost:,.2f}")
        print(f"  NPV: €{comp.npv:,.2f}")
        print(f"  IRR: {comp.irr_percent:.2f}%")
        print(f"  Payback: {comp.payback_years:.1f} years")
        print(f"  Lifetime Savings: €{comp.lifetime_savings:,.2f}")
        print()
    
    if result.recommended_financing:
        print(f"RECOMMENDED: {result.recommended_financing}")


def demo_tax_incentives():
    """Demonstrate analysis with tax incentives"""
    print_section("DEMO 3: Analysis with Tax Incentives")
    
    service = FinancialAnalysisService()
    
    # Create request with tax incentives
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
        analysis_period_years=25,
        income_tax_rate=30.0,
        tax_incentives=[
            TaxIncentive(
                type=TaxIncentiveType.GRANT,
                name="KfW Förderung 270",
                amount=1699.90,  # 10% of system cost
                year_received=1,
                description="KfW loan program for renewable energy"
            ),
            TaxIncentive(
                type=TaxIncentiveType.GRANT,
                name="BAFA Förderung",
                amount=2549.85,  # 15% of system cost
                year_received=1,
                description="Federal Office for Economic Affairs grant"
            ),
            TaxIncentive(
                type=TaxIncentiveType.DEPRECIATION,
                name="Degressive AfA",
                amount=3399.80,  # 20% of system cost
                year_received=1,
                description="Accelerated depreciation for tax purposes"
            )
        ]
    )
    
    result = service.calculate_comprehensive_analysis(request)
    
    print("TAX INCENTIVES:")
    for incentive in request.tax_incentives:
        print(f"  {incentive.name}: €{incentive.amount:,.2f} (Year {incentive.year_received})")
    print()
    
    total_incentives = sum(inc.amount for inc in request.tax_incentives)
    print(f"Total Tax Benefits: €{total_incentives:,.2f}")
    print()
    
    print("IMPACT ON FINANCIAL METRICS:")
    print(f"  NPV: €{result.npv_analysis.npv:,.2f}")
    print(f"  IRR: {result.irr_analysis.irr_percent:.2f}%")
    print(f"  Payback Period: {result.roi_analysis.simple_payback_years:.1f} years")
    print(f"  Investment Grade: {result.investment_grade}")


def demo_sensitivity_analysis():
    """Demonstrate sensitivity analysis"""
    print_section("DEMO 4: Sensitivity Analysis")
    
    service = FinancialAnalysisService()
    
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
    
    result = service.calculate_comprehensive_analysis(request)
    
    print("SENSITIVITY ANALYSIS:")
    print()
    print(f"{'Parameter':<25} {'Base Value':<15} {'Low Value':<15} {'High Value':<15} {'Sensitivity':<15}")
    print("-" * 85)
    
    for analysis in result.sensitivity_analyses:
        print(f"{analysis.parameter:<25} {analysis.base_value:<15.2f} {analysis.low_value:<15.2f} {analysis.high_value:<15.2f} {analysis.sensitivity_percent:<15.2f}%")
    
    print()
    print("NPV IMPACT:")
    print(f"{'Parameter':<25} {'NPV @ Low':<20} {'NPV @ Base':<20} {'NPV @ High':<20}")
    print("-" * 85)
    
    for analysis in result.sensitivity_analyses:
        print(f"{analysis.parameter:<25} €{analysis.npv_at_low:<19,.2f} €{analysis.npv_at_base:<19,.2f} €{analysis.npv_at_high:<19,.2f}")


def demo_cash_flow_projection():
    """Demonstrate cash flow projections"""
    print_section("DEMO 5: 25-Year Cash Flow Projection")
    
    service = FinancialAnalysisService()
    
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
    
    result = service.calculate_comprehensive_analysis(request)
    
    print("YEARLY CASH FLOW PROJECTION:")
    print()
    print(f"{'Year':<6} {'Production':<12} {'Savings':<12} {'Feed-in':<12} {'Costs':<12} {'Net CF':<12} {'Cumulative':<12}")
    print("-" * 78)
    
    # Show every 5 years
    for cf in result.yearly_cash_flows:
        if cf.year == 1 or cf.year % 5 == 0 or cf.year == 25:
            print(f"{cf.year:<6} {cf.energy_production_kwh:<12,.0f} €{cf.electricity_savings:<11,.2f} €{cf.feed_in_revenue:<11,.2f} €{cf.total_costs:<11,.2f} €{cf.net_cash_flow:<11,.2f} €{cf.cumulative_cash_flow:<11,.2f}")
    
    print()
    print(f"Total Energy Produced: {result.total_energy_produced_kwh:,.0f} kWh")
    print(f"Total Energy Savings: €{result.total_energy_savings_eur:,.2f}")
    print(f"Total Feed-in Revenue: €{result.total_feed_in_revenue_eur:,.2f}")
    print(f"Total Costs: €{result.total_maintenance_costs_eur + result.total_insurance_costs_eur:,.2f}")
    print(f"Net Lifetime Benefit: €{result.net_lifetime_benefit_eur:,.2f}")


def demo_scenario_comparison():
    """Demonstrate scenario comparison"""
    print_section("DEMO 6: Scenario Comparison")
    
    service = FinancialAnalysisService()
    
    # Scenario 1: Small system
    scenario1 = FinancialAnalysisRequest(
        system_size_kwp=7.5,
        total_system_cost=12999.00,
        annual_production_kwh=8500,
        current_electricity_price=0.35,
        electricity_price_increase=3.0,
        feed_in_tariff=0.08,
        annual_consumption_kwh=4000,
        self_consumption_rate=45.0,
        discount_rate=4.0,
        analysis_period_years=25
    )
    
    # Scenario 2: Medium system (base)
    scenario2 = FinancialAnalysisRequest(
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
    
    # Scenario 3: Large system
    scenario3 = FinancialAnalysisRequest(
        system_size_kwp=15.0,
        total_system_cost=22999.00,
        annual_production_kwh=17000,
        current_electricity_price=0.35,
        electricity_price_increase=3.0,
        feed_in_tariff=0.08,
        annual_consumption_kwh=4000,
        self_consumption_rate=25.0,
        discount_rate=4.0,
        analysis_period_years=25
    )
    
    scenarios = [
        ("Small System (7.5 kWp)", scenario1),
        ("Medium System (10.5 kWp)", scenario2),
        ("Large System (15.0 kWp)", scenario3)
    ]
    
    results = []
    for name, scenario in scenarios:
        result = service.calculate_comprehensive_analysis(scenario)
        results.append((name, result))
    
    print("SCENARIO COMPARISON:")
    print()
    print(f"{'Metric':<30} {'Small':<20} {'Medium':<20} {'Large':<20}")
    print("-" * 90)
    
    print(f"{'System Size (kWp)':<30} {results[0][1].system_size_kwp:<20.1f} {results[1][1].system_size_kwp:<20.1f} {results[2][1].system_size_kwp:<20.1f}")
    print(f"{'Total Cost (EUR)':<30} €{results[0][1].total_system_cost:<19,.2f} €{results[1][1].total_system_cost:<19,.2f} €{results[2][1].total_system_cost:<19,.2f}")
    print(f"{'NPV (EUR)':<30} €{results[0][1].npv_analysis.npv:<19,.2f} €{results[1][1].npv_analysis.npv:<19,.2f} €{results[2][1].npv_analysis.npv:<19,.2f}")
    print(f"{'IRR (%)':<30} {results[0][1].irr_analysis.irr_percent:<20.2f} {results[1][1].irr_analysis.irr_percent:<20.2f} {results[2][1].irr_analysis.irr_percent:<20.2f}")
    print(f"{'Payback (years)':<30} {results[0][1].roi_analysis.simple_payback_years:<20.1f} {results[1][1].roi_analysis.simple_payback_years:<20.1f} {results[2][1].roi_analysis.simple_payback_years:<20.1f}")
    print(f"{'Lifetime Savings (EUR)':<30} €{results[0][1].roi_analysis.total_lifetime_savings:<19,.2f} €{results[1][1].roi_analysis.total_lifetime_savings:<19,.2f} €{results[2][1].roi_analysis.total_lifetime_savings:<19,.2f}")
    print(f"{'Investment Grade':<30} {results[0][1].investment_grade:<20} {results[1][1].investment_grade:<20} {results[2][1].investment_grade:<20}")
    
    # Determine best scenario
    best_npv = max(results, key=lambda x: x[1].npv_analysis.npv)
    print()
    print(f"BEST SCENARIO (by NPV): {best_npv[0]}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  SOLAR FINANCIAL ANALYSIS SERVICE - COMPREHENSIVE DEMO")
    print("=" * 80)
    
    demo_basic_analysis()
    demo_financing_comparison()
    demo_tax_incentives()
    demo_sensitivity_analysis()
    demo_cash_flow_projection()
    demo_scenario_comparison()
    
    print("\n" + "=" * 80)
    print("  DEMO COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
