"""Demo: Economic Analysis Integration

Demonstrates the integration between the enhanced pricing system and economic
analysis calculations for accurate payback period, ROI, and profitability analysis.
"""

from pricing.profitability_reporting import get_profitability_reporting_engine
from pricing.enhanced_pricing_engine import FinalPricingResult, PriceComponent
from pricing.economic_analysis_integration import get_economic_analysis_integration
import os
import sys
from datetime import datetime
from typing import Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_sample_components() -> list[PriceComponent]:
    """Create sample components for demonstration"""

    components = [
        PriceComponent(
            product_id=1,
            model_name="Premium PV Module 400W",
            category="pv_modules",
            brand="SolarTech",
            quantity=25,
            price_euro=185.0,
            calculate_per="Stück",
            capacity_w=400.0,
            efficiency_percent=21.8,
            warranty_years=25,
            technology="Monocrystalline",
            feature="Half-cell",
            design="Black Frame"
        ),
        PriceComponent(
            product_id=2,
            model_name="String Inverter 8kW",
            category="inverters",
            brand="PowerConvert",
            quantity=1,
            price_euro=1200.0,
            calculate_per="Stück",
            power_kw=8.0,
            efficiency_percent=97.8,
            warranty_years=12,
            technology="Transformerless",
            feature="WiFi Monitoring"
        ),
        PriceComponent(
            product_id=3,
            model_name="Lithium Battery 10kWh",
            category="batteries",
            brand="EnergyStore",
            quantity=1,
            price_euro=4500.0,
            calculate_per="Stück",
            capacity_w=10000.0,
            max_cycles=6000,
            warranty_years=15,
            technology="LiFePO4",
            feature="Smart BMS"
        ),
        PriceComponent(
            product_id=4,
            model_name="Mounting System",
            category="mounting",
            brand="RoofMount",
            quantity=1,
            price_euro=800.0,
            calculate_per="pauschal",
            technology="Aluminum Rails",
            feature="Adjustable Tilt"
        )
    ]

    return components


def create_sample_final_pricing_result(
        components: list[PriceComponent]) -> FinalPricingResult:
    """Create sample final pricing result"""

    base_price = sum(comp.price_euro * comp.quantity for comp in components)

    return FinalPricingResult(
        base_price=base_price,
        components=components,
        dynamic_keys={
            "PV_BASE_PRICE": f"{base_price:,.2f}€",
            "PV_COMPONENT_COUNT": str(len(components))
        },
        metadata={
            "calculation_time": 0.15,
            "system_type": "pv",
            "calculation_date": datetime.now().isoformat()
        },
        final_price_net=base_price * 0.95,  # 5% discount
        final_price_gross=base_price * 0.95 * 1.19,  # Add 19% VAT
        vat_amount=base_price * 0.95 * 0.19,
        total_discounts=base_price * 0.05,
        total_surcharges=0.0,
        vat_rate_percent=19.0,
        profit_margin=25.0
    )


def create_sample_system_performance() -> dict[str, Any]:
    """Create sample system performance data"""

    return {
        "annual_production_kwh": 12500.0,
        "self_consumption_kwh": 8500.0,
        "feed_in_kwh": 4000.0,
        "system_power_kwp": 10.0,
        "performance_ratio": 0.85,
        "specific_yield_kwh_per_kwp": 1250.0
    }


def create_sample_economic_parameters() -> dict[str, Any]:
    """Create sample economic parameters"""

    return {
        "electricity_price_kwh": 0.32,
        "feed_in_tariff_kwh": 0.082,
        "discount_rate": 0.04,
        "analysis_years": 25,
        "inflation_rate": 0.02,
        "electricity_price_increase": 0.03
    }


def create_sample_historical_data() -> dict[str, Any]:
    """Create sample historical data for trend analysis"""

    return {
        "pricing_history": {
            "Premium PV Module 400W": [190.0, 188.0, 185.0, 183.0, 185.0, 187.0],
            "String Inverter 8kW": [1300.0, 1250.0, 1200.0, 1180.0, 1200.0, 1220.0],
            "Lithium Battery 10kWh": [5000.0, 4800.0, 4600.0, 4500.0, 4450.0, 4500.0],
            "Mounting System": [850.0, 820.0, 800.0, 790.0, 800.0, 810.0]
        },
        "sales_history": {
            "Premium PV Module 400W": [150, 180, 220, 250, 280, 300],
            "String Inverter 8kW": [15, 18, 22, 25, 28, 30],
            "Lithium Battery 10kWh": [8, 12, 15, 18, 20, 22],
            "Mounting System": [20, 25, 30, 35, 38, 40]
        }
    }


def demo_economic_analysis():
    """Demonstrate economic analysis integration"""

    print("=" * 80)
    print("ECONOMIC ANALYSIS INTEGRATION DEMO")
    print("=" * 80)

    # Create sample data
    components = create_sample_components()
    final_pricing_result = create_sample_final_pricing_result(components)
    system_performance = create_sample_system_performance()
    economic_parameters = create_sample_economic_parameters()

    print("\n📊 System Configuration:")
    print(f"   • Components: {len(components)}")
    print(f"   • System Power: {system_performance['system_power_kwp']} kWp")
    print(
        f"   • Annual Production: {
            system_performance['annual_production_kwh']:,.0f} kWh")
    print(
        f"   • Final Price (Net): {
            final_pricing_result.final_price_net:,.2f}€")
    print(
        f"   • Final Price (Gross): {
            final_pricing_result.final_price_gross:,.2f}€")

    # Initialize economic analysis integration
    economic_integration = get_economic_analysis_integration("pv")

    print("\n🔄 Calculating Economic Analysis...")

    # Perform economic analysis
    economic_result = economic_integration.calculate_economic_analysis(
        final_pricing_result,
        system_performance,
        economic_parameters
    )

    print("\n💰 Economic Analysis Results:")
    print(
        f"   • Total Investment (Net): {
            economic_result.total_investment_net:,.2f}€")
    print(f"   • Annual Savings: {economic_result.annual_savings:,.2f}€")
    print(
        f"   • Annual Feed-in Revenue: {economic_result.annual_feed_in_revenue:,.2f}€")
    print(
        f"   • Total Annual Benefit: {
            economic_result.total_annual_benefit:,.2f}€")
    print(
        f"   • Payback Period: {
            economic_result.payback_period_years:.1f} years")
    print(f"   • ROI: {economic_result.roi_percent:.1f}%")
    print(f"   • NPV: {economic_result.npv_eur:,.2f}€")
    print(f"   • IRR: {economic_result.irr_percent:.1f}%")

    print("\n🌱 Environmental Impact:")
    print(
        f"   • Annual CO2 Savings: {
            economic_result.annual_co2_savings_kg:,.0f} kg")
    print(
        f"   • CO2 Payback Time: {
            economic_result.co2_payback_years:.1f} years")
    print(
        f"   • Lifetime CO2 Savings: {
            economic_result.lifetime_co2_savings_tons:.1f} tons")

    print("\n🔑 Dynamic Keys Generated:")
    for key, value in list(economic_result.dynamic_keys.items())[:5]:
        print(f"   • {key}: {value}")
    print(f"   ... and {len(economic_result.dynamic_keys) - 5} more keys")

    return economic_result


def demo_profitability_reporting():
    """Demonstrate profitability reporting"""

    print("\n" + "=" * 80)
    print("PROFITABILITY REPORTING DEMO")
    print("=" * 80)

    # Create multiple pricing results for comprehensive analysis
    components1 = create_sample_components()
    components2 = create_sample_components()
    components2[0].quantity = 20  # Different quantity for variation
    components2[2].price_euro = 4200.0  # Different price for variation

    final_pricing_results = [
        create_sample_final_pricing_result(components1),
        create_sample_final_pricing_result(components2)
    ]

    historical_data = create_sample_historical_data()

    print(
        f"\n📈 Analyzing {
            len(final_pricing_results)} pricing configurations...")

    # Initialize profitability reporting engine
    reporting_engine = get_profitability_reporting_engine("pv")

    # Generate comprehensive report
    profitability_report = reporting_engine.generate_comprehensive_report(
        final_pricing_results,
        historical_data,
        "Q1_2024"
    )

    print("\n💼 Executive Summary:")
    print(f"   • Total Revenue: {profitability_report.total_revenue:,.2f}€")
    print(f"   • Total Costs: {profitability_report.total_costs:,.2f}€")
    print(f"   • Gross Profit: {profitability_report.gross_profit:,.2f}€")
    print(
        f"   • Gross Margin: {
            profitability_report.gross_margin_percent:.1f}%")

    print("\n🔧 Component Analysis:")
    print(
        f"   • Components Analyzed: {len(profitability_report.component_analyses)}")
    print(
        f"   • Top Profit Components: {len(profitability_report.top_profit_components)}")
    print(
        f"   • Low Margin Components: {len(profitability_report.low_margin_components)}")

    if profitability_report.top_profit_components:
        top_component = profitability_report.top_profit_components[0]
        print(
            f"   • Best Performer: {
                top_component.component_name} ({
                top_component.average_margin_percent:.1f}% margin)")

    print("\n📊 Pricing Trends:")
    for trend in profitability_report.pricing_trends[:3]:
        print(
            f"   • {
                trend.component_name}: {
                trend.trend_direction} ({
                trend.price_change_percent:+.1f}%)")

    print("\n🎯 Optimization Opportunities:")
    print(
        f"   • Total Optimization Potential: {
            profitability_report.total_optimization_potential:,.2f}€")
    print(f"   • Quick Wins: {len(profitability_report.quick_wins)}")
    print(
        f"   • Strategic Initiatives: {len(profitability_report.strategic_initiatives)}")

    print("\n💡 Top Optimization Suggestions:")
    for i, suggestion in enumerate(
            profitability_report.optimization_suggestions[:3], 1):
        print(f"   {i}. {suggestion.title}")
        print(f"      • Type: {suggestion.type}")
        print(
            f"      • Potential Savings: {
                suggestion.potential_savings:,.2f}€")
        print(f"      • Implementation: {suggestion.implementation_effort}")
        print(f"      • Priority Score: {suggestion.priority_score:.1f}")

    print("\n📈 Performance Metrics:")
    for metric, value in list(
            profitability_report.performance_metrics.items())[:4]:
        if "percent" in metric or "ratio" in metric:
            print(f"   • {metric.replace('_', ' ').title()}: {value:.1f}%")
        else:
            print(f"   • {metric.replace('_', ' ').title()}: {value:.2f}")

    print("\n🏪 Market Insights:")
    market_insights = profitability_report.market_insights
    if "competitive_analysis" in market_insights:
        comp_analysis = market_insights["competitive_analysis"]
        print(
            f"   • Premium Components: {
                comp_analysis.get(
                    'premium_components',
                    0)}")
        print(
            f"   • Competitive Components: {
                comp_analysis.get(
                    'competitive_components',
                    0)}")
        print(
            f"   • Low Cost Components: {
                comp_analysis.get(
                    'low_cost_components',
                    0)}")

    if "risk_assessment" in market_insights:
        risk_assessment = market_insights["risk_assessment"]
        print(
            f"   • Overall Risk Level: {
                risk_assessment.get(
                    'overall_risk_level',
                    'unknown')}")
        print(
            f"   • Volatile Components: {
                risk_assessment.get(
                    'volatile_components',
                    0)}")

    print("\n🔑 Report Dynamic Keys:")
    for key, value in list(profitability_report.dynamic_keys.items())[:5]:
        print(f"   • {key}: {value}")
    print(f"   ... and {len(profitability_report.dynamic_keys) - 5} more keys")

    return profitability_report


def demo_integration_workflow():
    """Demonstrate complete integration workflow"""

    print("\n" + "=" * 80)
    print("COMPLETE INTEGRATION WORKFLOW DEMO")
    print("=" * 80)

    print("\n🔄 Step 1: Enhanced Pricing Calculation")
    components = create_sample_components()
    final_pricing_result = create_sample_final_pricing_result(components)
    print(
        f"   ✅ Final pricing calculated: {
            final_pricing_result.final_price_net:,.2f}€")

    print("\n🔄 Step 2: Economic Analysis Integration")
    system_performance = create_sample_system_performance()
    economic_parameters = create_sample_economic_parameters()

    economic_integration = get_economic_analysis_integration("pv")
    economic_result = economic_integration.calculate_economic_analysis(
        final_pricing_result,
        system_performance,
        economic_parameters
    )
    print(
        f"   ✅ Economic analysis completed: {
            economic_result.payback_period_years:.1f} year payback")

    print("\n🔄 Step 3: Profitability Analysis")
    historical_data = create_sample_historical_data()

    reporting_engine = get_profitability_reporting_engine("pv")
    profitability_report = reporting_engine.generate_comprehensive_report(
        [final_pricing_result],
        historical_data
    )
    print(
        f"   ✅ Profitability report generated: {
            profitability_report.gross_margin_percent:.1f}% margin")

    print("\n🔄 Step 4: PDF Integration Ready")
    all_keys = {}
    all_keys.update(final_pricing_result.dynamic_keys)
    all_keys.update(economic_result.dynamic_keys)
    all_keys.update(profitability_report.dynamic_keys)
    print(f"   ✅ {len(all_keys)} dynamic keys ready for PDF generation")

    print("\n📋 Integration Summary:")
    print("   • Enhanced Pricing: ✅ Complete")
    print("   • Economic Analysis: ✅ Complete")
    print("   • Profitability Reporting: ✅ Complete")
    print("   • PDF Key Generation: ✅ Complete")
    print("   • Total Processing Time: < 1 second")

    return {
        "final_pricing_result": final_pricing_result,
        "economic_result": economic_result,
        "profitability_report": profitability_report,
        "all_keys": all_keys
    }


def main():
    """Main demonstration function"""

    print("🚀 Starting Economic Analysis Integration Demo")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run individual demos
        economic_result = demo_economic_analysis()
        profitability_report = demo_profitability_reporting()

        # Run complete workflow demo
        workflow_results = demo_integration_workflow()

        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\n🎯 Key Achievements:")
        print("   • Economic analysis integrated with enhanced pricing")
        print("   • Profitability reporting with trend analysis")
        print("   • Comprehensive optimization suggestions")
        print("   • Dynamic PDF key generation")
        print("   • Real-time calculation performance")

        print("\n📊 Demo Statistics:")
        print(
            f"   • Components Analyzed: {len(workflow_results['final_pricing_result'].components)}")
        print("   • Economic Metrics Calculated: 8")
        print(
            f"   • Profitability Insights Generated: {
                len(
                    profitability_report.optimization_suggestions)}")
        print(
            f"   • Dynamic Keys Created: {len(workflow_results['all_keys'])}")

        return True

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
