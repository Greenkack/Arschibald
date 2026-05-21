"""
Results Visualization Service

Service for creating interactive dashboards, comparisons, and analyses.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from ..models.results_schemas import (
    InteractiveDashboard,
    DashboardWidget,
    ComparisonView,
    ComparisonItem,
    ScenarioAnalysis,
    ScenarioResult,
    ScenarioParameter,
    SensitivityAnalysis,
    SensitivityResult,
    SensitivityParameter,
    WhatIfAnalysis,
    WhatIfResult,
    WhatIfParameter,
    ResultMetric,
    ChartType,
    ExportFormat
)


class ResultsVisualizationService:
    """Service for results visualization and analysis"""
    
    def __init__(self):
        self.dashboards: Dict[str, InteractiveDashboard] = {}
        self.comparisons: Dict[str, ComparisonView] = {}
        self.scenarios: Dict[str, ScenarioAnalysis] = {}
        self.sensitivities: Dict[str, SensitivityAnalysis] = {}
        self.what_ifs: Dict[str, WhatIfAnalysis] = {}
    
    # Dashboard Methods
    
    def create_dashboard(
        self,
        name: str,
        calculation_id: int,
        widgets: List[DashboardWidget],
        description: Optional[str] = None,
        layout: str = "grid"
    ) -> InteractiveDashboard:
        """Create interactive dashboard"""
        dashboard_id = str(uuid.uuid4())
        
        dashboard = InteractiveDashboard(
            id=dashboard_id,
            name=name,
            description=description,
            calculation_id=calculation_id,
            widgets=widgets,
            layout=layout,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.dashboards[dashboard_id] = dashboard
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[InteractiveDashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)
    
    def update_dashboard(
        self,
        dashboard_id: str,
        widgets: Optional[List[DashboardWidget]] = None,
        layout: Optional[str] = None
    ) -> InteractiveDashboard:
        """Update dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        if widgets is not None:
            dashboard.widgets = widgets
        if layout is not None:
            dashboard.layout = layout
        
        dashboard.updated_at = datetime.now()
        return dashboard
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""
        if dashboard_id in self.dashboards:
            del self.dashboards[dashboard_id]
            return True
        return False
    
    def create_default_dashboard(
        self,
        calculation_id: int,
        calculation_data: Dict[str, Any]
    ) -> InteractiveDashboard:
        """Create default dashboard with standard widgets"""
        widgets = [
            DashboardWidget(
                id="system-size",
                type="metric",
                title="System Size",
                position={"x": 0, "y": 0, "width": 3, "height": 2},
                data={
                    "value": calculation_data.get("system_size", 0),
                    "unit": "kWp",
                    "trend": "up"
                }
            ),
            DashboardWidget(
                id="total-cost",
                type="metric",
                title="Total Cost",
                position={"x": 3, "y": 0, "width": 3, "height": 2},
                data={
                    "value": calculation_data.get("total_cost", 0),
                    "unit": "€",
                    "formatted": f"{calculation_data.get('total_cost', 0):,.2f} €"
                }
            ),
            DashboardWidget(
                id="payback-period",
                type="metric",
                title="Payback Period",
                position={"x": 6, "y": 0, "width": 3, "height": 2},
                data={
                    "value": calculation_data.get("payback_period", 0),
                    "unit": "years"
                }
            ),
            DashboardWidget(
                id="annual-savings",
                type="metric",
                title="Annual Savings",
                position={"x": 9, "y": 0, "width": 3, "height": 2},
                data={
                    "value": calculation_data.get("annual_savings", 0),
                    "unit": "€/year",
                    "formatted": f"{calculation_data.get('annual_savings', 0):,.2f} €"
                }
            ),
            DashboardWidget(
                id="production-chart",
                type="chart",
                title="Energy Production",
                position={"x": 0, "y": 2, "width": 6, "height": 4},
                data={
                    "chart_type": "line",
                    "data": calculation_data.get("monthly_production", [])
                }
            ),
            DashboardWidget(
                id="savings-chart",
                type="chart",
                title="Cumulative Savings",
                position={"x": 6, "y": 2, "width": 6, "height": 4},
                data={
                    "chart_type": "area",
                    "data": calculation_data.get("cumulative_savings", [])
                }
            ),
            DashboardWidget(
                id="breakdown-chart",
                type="chart",
                title="Cost Breakdown",
                position={"x": 0, "y": 6, "width": 6, "height": 4},
                data={
                    "chart_type": "pie",
                    "data": calculation_data.get("cost_breakdown", [])
                }
            ),
            DashboardWidget(
                id="roi-chart",
                type="chart",
                title="Return on Investment",
                position={"x": 6, "y": 6, "width": 6, "height": 4},
                data={
                    "chart_type": "bar",
                    "data": calculation_data.get("roi_data", [])
                }
            )
        ]
        
        return self.create_dashboard(
            name=f"Dashboard for Calculation {calculation_id}",
            calculation_id=calculation_id,
            widgets=widgets,
            description="Auto-generated dashboard"
        )
    
    # Comparison Methods
    
    def create_comparison(
        self,
        name: str,
        items: List[ComparisonItem],
        metrics_to_compare: List[str],
        description: Optional[str] = None,
        chart_type: ChartType = ChartType.BAR
    ) -> ComparisonView:
        """Create comparison view"""
        comparison_id = str(uuid.uuid4())
        
        comparison = ComparisonView(
            id=comparison_id,
            name=name,
            description=description,
            items=items,
            metrics_to_compare=metrics_to_compare,
            chart_type=chart_type,
            created_at=datetime.now()
        )
        
        self.comparisons[comparison_id] = comparison
        return comparison
    
    def get_comparison(self, comparison_id: str) -> Optional[ComparisonView]:
        """Get comparison by ID"""
        return self.comparisons.get(comparison_id)
    
    def compare_calculations(
        self,
        calculation_data_list: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple calculations"""
        comparison_data = {
            "metrics": metrics,
            "calculations": []
        }
        
        for calc_data in calculation_data_list:
            calc_comparison = {
                "id": calc_data.get("id"),
                "name": calc_data.get("name", f"Calculation {calc_data.get('id')}"),
                "values": {}
            }
            
            for metric in metrics:
                calc_comparison["values"][metric] = calc_data.get(metric, 0)
            
            comparison_data["calculations"].append(calc_comparison)
        
        return comparison_data
    
    # Scenario Analysis Methods
    
    def create_scenario_analysis(
        self,
        name: str,
        base_calculation_id: int,
        parameters: List[ScenarioParameter],
        base_calculation_data: Dict[str, Any],
        num_scenarios: int = 5,
        description: Optional[str] = None
    ) -> ScenarioAnalysis:
        """Create scenario analysis"""
        scenario_id = str(uuid.uuid4())
        
        # Generate scenarios
        scenarios = self._generate_scenarios(
            base_calculation_data,
            parameters,
            num_scenarios
        )
        
        analysis = ScenarioAnalysis(
            id=scenario_id,
            name=name,
            description=description,
            base_calculation_id=base_calculation_id,
            parameters=parameters,
            scenarios=scenarios,
            created_at=datetime.now()
        )
        
        self.scenarios[scenario_id] = analysis
        return analysis
    
    def _generate_scenarios(
        self,
        base_data: Dict[str, Any],
        parameters: List[ScenarioParameter],
        num_scenarios: int
    ) -> List[ScenarioResult]:
        """Generate scenarios based on parameters"""
        scenarios = []
        
        # Best case scenario
        best_params = {
            param.name: param.max_value for param in parameters
        }
        scenarios.append(self._calculate_scenario(
            "Best Case",
            base_data,
            best_params
        ))
        
        # Worst case scenario
        worst_params = {
            param.name: param.min_value for param in parameters
        }
        scenarios.append(self._calculate_scenario(
            "Worst Case",
            base_data,
            worst_params
        ))
        
        # Base case scenario
        base_params = {
            param.name: param.base_value for param in parameters
        }
        scenarios.append(self._calculate_scenario(
            "Base Case",
            base_data,
            base_params
        ))
        
        # Generate intermediate scenarios
        for i in range(num_scenarios - 3):
            scenario_params = {}
            for param in parameters:
                # Random value between min and max
                value = np.random.uniform(param.min_value, param.max_value)
                scenario_params[param.name] = value
            
            scenarios.append(self._calculate_scenario(
                f"Scenario {i + 1}",
                base_data,
                scenario_params
            ))
        
        return scenarios
    
    def _calculate_scenario(
        self,
        scenario_name: str,
        base_data: Dict[str, Any],
        parameters: Dict[str, float]
    ) -> ScenarioResult:
        """Calculate results for a scenario"""
        # Apply parameter changes to base calculation
        # This is a simplified version - in production, you'd recalculate everything
        
        base_cost = base_data.get("total_cost", 0)
        base_savings = base_data.get("annual_savings", 0)
        base_payback = base_data.get("payback_period", 0)
        
        # Apply parameter impacts (simplified)
        cost_factor = 1.0
        savings_factor = 1.0
        
        if "system_size" in parameters:
            size_change = parameters["system_size"] / base_data.get("system_size", 1)
            cost_factor *= size_change
            savings_factor *= size_change
        
        if "electricity_price" in parameters:
            price_change = parameters["electricity_price"] / base_data.get("electricity_price", 1)
            savings_factor *= price_change
        
        total_cost = base_cost * cost_factor
        total_savings = base_savings * savings_factor
        payback_period = total_cost / total_savings if total_savings > 0 else 0
        
        metrics = [
            ResultMetric(
                name="Total Cost",
                value=total_cost,
                unit="€",
                formatted_value=f"{total_cost:,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Annual Savings",
                value=total_savings,
                unit="€/year",
                formatted_value=f"{total_savings:,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Payback Period",
                value=payback_period,
                unit="years",
                formatted_value=f"{payback_period:.1f} years",
                category="financial"
            )
        ]
        
        return ScenarioResult(
            scenario_name=scenario_name,
            parameters=parameters,
            metrics=metrics,
            total_cost=total_cost,
            total_savings=total_savings,
            payback_period=payback_period
        )
    
    # Sensitivity Analysis Methods
    
    def create_sensitivity_analysis(
        self,
        name: str,
        base_calculation_id: int,
        parameters: List[SensitivityParameter],
        base_calculation_data: Dict[str, Any],
        num_points: int = 10,
        description: Optional[str] = None
    ) -> SensitivityAnalysis:
        """Create sensitivity analysis"""
        sensitivity_id = str(uuid.uuid4())
        
        # Calculate sensitivity for each parameter
        results = self._calculate_sensitivity(
            base_calculation_data,
            parameters,
            num_points
        )
        
        # Generate tornado chart data
        tornado_data = self._generate_tornado_chart(results)
        
        analysis = SensitivityAnalysis(
            id=sensitivity_id,
            name=name,
            description=description,
            base_calculation_id=base_calculation_id,
            parameters=parameters,
            results=results,
            tornado_chart_data=tornado_data,
            created_at=datetime.now()
        )
        
        self.sensitivities[sensitivity_id] = analysis
        return analysis
    
    def _calculate_sensitivity(
        self,
        base_data: Dict[str, Any],
        parameters: List[SensitivityParameter],
        num_points: int
    ) -> List[SensitivityResult]:
        """Calculate sensitivity for each parameter"""
        results = []
        
        base_roi = base_data.get("roi", 0)
        base_payback = base_data.get("payback_period", 0)
        base_savings = base_data.get("total_savings_25_years", 0)
        
        for param in parameters:
            # Vary parameter and measure impact
            variation = param.base_value * (param.variation_range / 100)
            
            # Test positive variation
            new_value = param.base_value + variation
            impact_roi = self._calculate_impact_on_roi(
                param.name,
                param.base_value,
                new_value,
                base_data
            )
            impact_payback = self._calculate_impact_on_payback(
                param.name,
                param.base_value,
                new_value,
                base_data
            )
            impact_savings = self._calculate_impact_on_savings(
                param.name,
                param.base_value,
                new_value,
                base_data
            )
            
            results.append(SensitivityResult(
                parameter_name=param.name,
                parameter_value=new_value,
                impact_on_roi=impact_roi,
                impact_on_payback=impact_payback,
                impact_on_savings=impact_savings
            ))
        
        return results
    
    def _calculate_impact_on_roi(
        self,
        param_name: str,
        base_value: float,
        new_value: float,
        base_data: Dict[str, Any]
    ) -> float:
        """Calculate impact on ROI"""
        # Simplified impact calculation
        change_percent = ((new_value - base_value) / base_value) * 100
        
        # Different parameters have different impacts
        impact_factors = {
            "system_size": 0.8,
            "electricity_price": 1.2,
            "installation_cost": -0.9,
            "maintenance_cost": -0.3,
            "feed_in_tariff": 0.5
        }
        
        factor = impact_factors.get(param_name, 0.5)
        return change_percent * factor
    
    def _calculate_impact_on_payback(
        self,
        param_name: str,
        base_value: float,
        new_value: float,
        base_data: Dict[str, Any]
    ) -> float:
        """Calculate impact on payback period"""
        change_percent = ((new_value - base_value) / base_value) * 100
        
        impact_factors = {
            "system_size": -0.3,
            "electricity_price": -0.8,
            "installation_cost": 0.9,
            "maintenance_cost": 0.2,
            "feed_in_tariff": -0.4
        }
        
        factor = impact_factors.get(param_name, 0.3)
        return change_percent * factor
    
    def _calculate_impact_on_savings(
        self,
        param_name: str,
        base_value: float,
        new_value: float,
        base_data: Dict[str, Any]
    ) -> float:
        """Calculate impact on total savings"""
        change_percent = ((new_value - base_value) / base_value) * 100
        
        impact_factors = {
            "system_size": 0.9,
            "electricity_price": 1.0,
            "installation_cost": -0.1,
            "maintenance_cost": -0.5,
            "feed_in_tariff": 0.6
        }
        
        factor = impact_factors.get(param_name, 0.5)
        return change_percent * factor
    
    def _generate_tornado_chart(
        self,
        results: List[SensitivityResult]
    ) -> Dict[str, Any]:
        """Generate tornado chart data"""
        # Sort by absolute impact on ROI
        sorted_results = sorted(
            results,
            key=lambda x: abs(x.impact_on_roi),
            reverse=True
        )
        
        tornado_data = {
            "parameters": [],
            "impacts": []
        }
        
        for result in sorted_results:
            tornado_data["parameters"].append(result.parameter_name)
            tornado_data["impacts"].append(result.impact_on_roi)
        
        return tornado_data
    
    # What-If Analysis Methods
    
    def create_what_if_analysis(
        self,
        name: str,
        base_calculation_id: int,
        parameter_changes: List[WhatIfParameter],
        base_calculation_data: Dict[str, Any],
        description: Optional[str] = None
    ) -> WhatIfAnalysis:
        """Create what-if analysis"""
        what_if_id = str(uuid.uuid4())
        
        # Calculate what-if result
        result = self._calculate_what_if(
            base_calculation_data,
            parameter_changes
        )
        
        analysis = WhatIfAnalysis(
            id=what_if_id,
            name=name,
            description=description,
            base_calculation_id=base_calculation_id,
            parameter_changes=parameter_changes,
            result=result,
            created_at=datetime.now()
        )
        
        self.what_ifs[what_if_id] = analysis
        return analysis
    
    def _calculate_what_if(
        self,
        base_data: Dict[str, Any],
        parameter_changes: List[WhatIfParameter]
    ) -> WhatIfResult:
        """Calculate what-if result"""
        # Extract original metrics
        original_metrics = [
            ResultMetric(
                name="Total Cost",
                value=base_data.get("total_cost", 0),
                unit="€",
                formatted_value=f"{base_data.get('total_cost', 0):,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Annual Savings",
                value=base_data.get("annual_savings", 0),
                unit="€/year",
                formatted_value=f"{base_data.get('annual_savings', 0):,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Payback Period",
                value=base_data.get("payback_period", 0),
                unit="years",
                formatted_value=f"{base_data.get('payback_period', 0):.1f} years",
                category="financial"
            )
        ]
        
        # Apply parameter changes
        modified_data = base_data.copy()
        for change in parameter_changes:
            modified_data[change.name] = change.new_value
        
        # Recalculate metrics (simplified)
        new_cost = modified_data.get("total_cost", 0)
        new_savings = modified_data.get("annual_savings", 0)
        new_payback = new_cost / new_savings if new_savings > 0 else 0
        
        new_metrics = [
            ResultMetric(
                name="Total Cost",
                value=new_cost,
                unit="€",
                formatted_value=f"{new_cost:,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Annual Savings",
                value=new_savings,
                unit="€/year",
                formatted_value=f"{new_savings:,.2f} €",
                category="financial"
            ),
            ResultMetric(
                name="Payback Period",
                value=new_payback,
                unit="years",
                formatted_value=f"{new_payback:.1f} years",
                category="financial"
            )
        ]
        
        # Calculate deltas
        delta_metrics = []
        for orig, new in zip(original_metrics, new_metrics):
            delta = new.value - orig.value
            delta_percent = (delta / orig.value * 100) if orig.value != 0 else 0
            
            delta_metrics.append(ResultMetric(
                name=f"Δ {orig.name}",
                value=delta,
                unit=orig.unit,
                formatted_value=f"{delta:+,.2f} {orig.unit} ({delta_percent:+.1f}%)",
                category="delta"
            ))
        
        return WhatIfResult(
            parameter_changes=parameter_changes,
            original_metrics=original_metrics,
            new_metrics=new_metrics,
            delta_metrics=delta_metrics
        )
    
    # Export Methods
    
    def export_visualization(
        self,
        visualization_id: str,
        visualization_type: str,
        export_format: ExportFormat
    ) -> Dict[str, Any]:
        """Export visualization to specified format"""
        # Get visualization data
        viz_data = None
        if visualization_type == "dashboard":
            viz_data = self.get_dashboard(visualization_id)
        elif visualization_type == "comparison":
            viz_data = self.get_comparison(visualization_id)
        elif visualization_type == "scenario":
            viz_data = self.scenarios.get(visualization_id)
        elif visualization_type == "sensitivity":
            viz_data = self.sensitivities.get(visualization_id)
        elif visualization_type == "what_if":
            viz_data = self.what_ifs.get(visualization_id)
        
        if not viz_data:
            raise ValueError(f"Visualization {visualization_id} not found")
        
        # Export based on format
        if export_format == ExportFormat.JSON:
            return self._export_to_json(viz_data)
        elif export_format == ExportFormat.CSV:
            return self._export_to_csv(viz_data)
        elif export_format == ExportFormat.PDF:
            return self._export_to_pdf(viz_data)
        elif export_format == ExportFormat.EXCEL:
            return self._export_to_excel(viz_data)
        elif export_format in [ExportFormat.PNG, ExportFormat.SVG]:
            return self._export_to_image(viz_data, export_format)
        
        raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_to_json(self, viz_data: Any) -> Dict[str, Any]:
        """Export to JSON"""
        return {
            "format": "json",
            "data": viz_data.dict() if hasattr(viz_data, "dict") else viz_data
        }
    
    def _export_to_csv(self, viz_data: Any) -> Dict[str, Any]:
        """Export to CSV"""
        # Simplified CSV export
        return {
            "format": "csv",
            "data": "CSV export not yet implemented"
        }
    
    def _export_to_pdf(self, viz_data: Any) -> Dict[str, Any]:
        """Export to PDF"""
        return {
            "format": "pdf",
            "data": "PDF export not yet implemented"
        }
    
    def _export_to_excel(self, viz_data: Any) -> Dict[str, Any]:
        """Export to Excel"""
        return {
            "format": "excel",
            "data": "Excel export not yet implemented"
        }
    
    def _export_to_image(self, viz_data: Any, format: ExportFormat) -> Dict[str, Any]:
        """Export to image"""
        return {
            "format": format.value,
            "data": f"{format.value.upper()} export not yet implemented"
        }
