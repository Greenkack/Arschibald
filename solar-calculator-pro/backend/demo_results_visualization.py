"""
Results Visualization Demo

Demonstrates the results visualization features.
"""

from services.results_visualization_service import ResultsVisualizationService
from models.results_schemas import (
    DashboardWidget,
    ScenarioParameter,
    SensitivityParameter,
    WhatIfParameter,
    ChartType,
    ExportFormat
)


def demo_interactive_dashboard():
    """Demo interactive dashboard creation"""
    print("\n=== Interactive Dashboard Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Sample calculation data
    calculation_data = {
        "id": 123,
        "system_size": 10.5,
        "total_cost": 16999.00,
        "annual_savings": 1850.00,
        "payback_period": 9.2,
        "roi": 15.5,
        "co2_savings": 8500,
        "monthly_production": [800, 950, 1200, 1400, 1500, 1600, 1550, 1450, 1250, 1000, 850, 750],
        "cumulative_savings": [1850, 3700, 5550, 7400, 9250, 11100, 12950, 14800, 16650, 18500],
        "cost_breakdown": [
            {"label": "Modules", "value": 8000},
            {"label": "Inverter", "value": 3000},
            {"label": "Installation", "value": 4000},
            {"label": "Other", "value": 1999}
        ],
        "roi_data": [
            {"year": "Year 1", "value": 1850},
            {"year": "Year 5", "value": 9250},
            {"year": "Year 10", "value": 18500},
            {"year": "Year 15", "value": 27750},
            {"year": "Year 20", "value": 37000}
        ]
    }
    
    # Create default dashboard
    dashboard = service.create_default_dashboard(
        calculation_id=123,
        calculation_data=calculation_data
    )
    
    print(f"Dashboard created: {dashboard.name}")
    print(f"Dashboard ID: {dashboard.id}")
    print(f"Number of widgets: {len(dashboard.widgets)}")
    print(f"Layout: {dashboard.layout}")
    
    # List widgets
    print("\nWidgets:")
    for widget in dashboard.widgets:
        print(f"  - {widget.title} ({widget.type})")
        print(f"    Position: x={widget.position['x']}, y={widget.position['y']}, "
              f"w={widget.position['width']}, h={widget.position['height']}")


def demo_comparison_view():
    """Demo comparison view"""
    print("\n=== Comparison View Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Sample calculation data for comparison
    calculations = [
        {
            "id": 123,
            "name": "System A (10 kWp)",
            "total_cost": 16999.00,
            "annual_savings": 1850.00,
            "payback_period": 9.2,
            "system_size": 10.0
        },
        {
            "id": 124,
            "name": "System B (12 kWp)",
            "total_cost": 19999.00,
            "annual_savings": 2200.00,
            "payback_period": 9.1,
            "system_size": 12.0
        },
        {
            "id": 125,
            "name": "System C (15 kWp)",
            "total_cost": 24999.00,
            "annual_savings": 2750.00,
            "payback_period": 9.1,
            "system_size": 15.0
        }
    ]
    
    # Compare calculations
    comparison_data = service.compare_calculations(
        calculation_data_list=calculations,
        metrics=["total_cost", "annual_savings", "payback_period", "system_size"]
    )
    
    print("Comparison Data:")
    print(f"Metrics: {', '.join(comparison_data['metrics'])}")
    print(f"\nCalculations:")
    for calc in comparison_data['calculations']:
        print(f"\n  {calc['name']}:")
        for metric, value in calc['values'].items():
            print(f"    {metric}: {value}")


def demo_scenario_analysis():
    """Demo scenario analysis"""
    print("\n=== Scenario Analysis Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Base calculation data
    base_data = {
        "id": 123,
        "system_size": 10.0,
        "electricity_price": 0.30,
        "total_cost": 16999.00,
        "annual_savings": 1850.00,
        "payback_period": 9.2
    }
    
    # Define parameters for scenario analysis
    parameters = [
        ScenarioParameter(
            name="system_size",
            base_value=10.0,
            min_value=8.0,
            max_value=12.0,
            step=0.5,
            unit="kWp"
        ),
        ScenarioParameter(
            name="electricity_price",
            base_value=0.30,
            min_value=0.25,
            max_value=0.35,
            step=0.01,
            unit="€/kWh"
        )
    ]
    
    # Create scenario analysis
    analysis = service.create_scenario_analysis(
        name="System Size & Price Scenarios",
        base_calculation_id=123,
        parameters=parameters,
        base_calculation_data=base_data,
        num_scenarios=5
    )
    
    print(f"Scenario Analysis: {analysis.name}")
    print(f"Analysis ID: {analysis.id}")
    print(f"Number of scenarios: {len(analysis.scenarios)}")
    
    print("\nScenarios:")
    for scenario in analysis.scenarios:
        print(f"\n  {scenario.scenario_name}:")
        print(f"    Parameters: {scenario.parameters}")
        print(f"    Total Cost: {scenario.total_cost:,.2f} €")
        print(f"    Annual Savings: {scenario.total_savings:,.2f} €")
        print(f"    Payback Period: {scenario.payback_period:.1f} years")


def demo_sensitivity_analysis():
    """Demo sensitivity analysis"""
    print("\n=== Sensitivity Analysis Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Base calculation data
    base_data = {
        "id": 123,
        "system_size": 10.0,
        "electricity_price": 0.30,
        "installation_cost": 16999.00,
        "roi": 15.5,
        "payback_period": 9.2,
        "total_savings_25_years": 46250.00
    }
    
    # Define parameters for sensitivity analysis
    parameters = [
        SensitivityParameter(
            name="system_size",
            base_value=10.0,
            variation_range=20.0,  # ±20%
            unit="kWp"
        ),
        SensitivityParameter(
            name="electricity_price",
            base_value=0.30,
            variation_range=15.0,  # ±15%
            unit="€/kWh"
        ),
        SensitivityParameter(
            name="installation_cost",
            base_value=16999.00,
            variation_range=10.0,  # ±10%
            unit="€"
        )
    ]
    
    # Create sensitivity analysis
    analysis = service.create_sensitivity_analysis(
        name="Parameter Sensitivity Analysis",
        base_calculation_id=123,
        parameters=parameters,
        base_calculation_data=base_data,
        num_points=10
    )
    
    print(f"Sensitivity Analysis: {analysis.name}")
    print(f"Analysis ID: {analysis.id}")
    print(f"Number of parameters: {len(analysis.parameters)}")
    
    print("\nSensitivity Results:")
    for result in analysis.results:
        print(f"\n  {result.parameter_name}:")
        print(f"    Parameter Value: {result.parameter_value:.2f}")
        print(f"    Impact on ROI: {result.impact_on_roi:+.2f}%")
        print(f"    Impact on Payback: {result.impact_on_payback:+.2f}%")
        print(f"    Impact on Savings: {result.impact_on_savings:+.2f}%")
    
    print("\nTornado Chart Data:")
    print(f"  Parameters: {analysis.tornado_chart_data['parameters']}")
    print(f"  Impacts: {analysis.tornado_chart_data['impacts']}")


def demo_what_if_analysis():
    """Demo what-if analysis"""
    print("\n=== What-If Analysis Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Base calculation data
    base_data = {
        "id": 123,
        "system_size": 10.0,
        "total_cost": 16999.00,
        "annual_savings": 1850.00,
        "payback_period": 9.2
    }
    
    # Define parameter changes
    parameter_changes = [
        WhatIfParameter(
            name="system_size",
            current_value=10.0,
            new_value=12.0,
            unit="kWp"
        )
    ]
    
    # Create what-if analysis
    analysis = service.create_what_if_analysis(
        name="What If: Larger System",
        base_calculation_id=123,
        parameter_changes=parameter_changes,
        base_calculation_data=base_data
    )
    
    print(f"What-If Analysis: {analysis.name}")
    print(f"Analysis ID: {analysis.id}")
    
    print("\nParameter Changes:")
    for change in analysis.parameter_changes:
        print(f"  {change.name}: {change.current_value} → {change.new_value} {change.unit}")
    
    print("\nOriginal Metrics:")
    for metric in analysis.result.original_metrics:
        print(f"  {metric.name}: {metric.formatted_value}")
    
    print("\nNew Metrics:")
    for metric in analysis.result.new_metrics:
        print(f"  {metric.name}: {metric.formatted_value}")
    
    print("\nDelta Metrics:")
    for metric in analysis.result.delta_metrics:
        print(f"  {metric.name}: {metric.formatted_value}")


def demo_export():
    """Demo export functionality"""
    print("\n=== Export Demo ===\n")
    
    service = ResultsVisualizationService()
    
    # Create a dashboard first
    calculation_data = {
        "id": 123,
        "system_size": 10.5,
        "total_cost": 16999.00,
        "annual_savings": 1850.00,
        "payback_period": 9.2
    }
    
    dashboard = service.create_default_dashboard(
        calculation_id=123,
        calculation_data=calculation_data
    )
    
    # Export to different formats
    formats = [ExportFormat.JSON, ExportFormat.CSV, ExportFormat.PDF]
    
    for format in formats:
        print(f"\nExporting to {format.value}...")
        try:
            export_data = service.export_visualization(
                visualization_id=dashboard.id,
                visualization_type="dashboard",
                export_format=format
            )
            print(f"  Format: {export_data['format']}")
            print(f"  Status: Success")
        except Exception as e:
            print(f"  Status: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Results Visualization Demo")
    print("=" * 60)
    
    demo_interactive_dashboard()
    demo_comparison_view()
    demo_scenario_analysis()
    demo_sensitivity_analysis()
    demo_what_if_analysis()
    demo_export()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
