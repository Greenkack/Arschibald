"""
Results Visualization API Endpoints

API endpoints for creating and managing result visualizations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ...models.results_schemas import (
    InteractiveDashboard,
    DashboardCreateRequest,
    ComparisonView,
    ComparisonCreateRequest,
    ScenarioAnalysis,
    ScenarioAnalysisRequest,
    SensitivityAnalysis,
    SensitivityAnalysisRequest,
    WhatIfAnalysis,
    WhatIfAnalysisRequest,
    ExportRequest,
    ExportResponse,
    ExportFormat
)
from ...services.results_visualization_service import ResultsVisualizationService

router = APIRouter(prefix="/results-visualization", tags=["results-visualization"])

# Service instance (in production, use dependency injection)
visualization_service = ResultsVisualizationService()


# Dashboard Endpoints

@router.post("/dashboards", response_model=InteractiveDashboard)
async def create_dashboard(request: DashboardCreateRequest):
    """
    Create interactive dashboard
    
    Creates a new interactive dashboard with specified widgets and layout.
    """
    try:
        dashboard = visualization_service.create_dashboard(
            name=request.name,
            calculation_id=request.calculation_id,
            widgets=request.widgets,
            description=request.description,
            layout=request.layout
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboards/{dashboard_id}", response_model=InteractiveDashboard)
async def get_dashboard(dashboard_id: str):
    """
    Get dashboard by ID
    
    Retrieves a specific dashboard by its ID.
    """
    dashboard = visualization_service.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=InteractiveDashboard)
async def update_dashboard(
    dashboard_id: str,
    widgets: List = None,
    layout: str = None
):
    """
    Update dashboard
    
    Updates dashboard widgets and/or layout.
    """
    try:
        dashboard = visualization_service.update_dashboard(
            dashboard_id=dashboard_id,
            widgets=widgets,
            layout=layout
        )
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """
    Delete dashboard
    
    Deletes a dashboard by its ID.
    """
    success = visualization_service.delete_dashboard(dashboard_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"message": "Dashboard deleted successfully"}


@router.post("/dashboards/default", response_model=InteractiveDashboard)
async def create_default_dashboard(
    calculation_id: int,
    calculation_data: dict
):
    """
    Create default dashboard
    
    Creates a dashboard with standard widgets for a calculation.
    """
    try:
        dashboard = visualization_service.create_default_dashboard(
            calculation_id=calculation_id,
            calculation_data=calculation_data
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Comparison Endpoints

@router.post("/comparisons", response_model=ComparisonView)
async def create_comparison(request: ComparisonCreateRequest):
    """
    Create comparison view
    
    Creates a new comparison view for multiple calculations.
    """
    try:
        # In production, fetch calculation data from database
        items = []
        # items = fetch_calculations(request.calculation_ids)
        
        comparison = visualization_service.create_comparison(
            name=request.name,
            items=items,
            metrics_to_compare=request.metrics_to_compare,
            description=request.description,
            chart_type=request.chart_type
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/comparisons/{comparison_id}", response_model=ComparisonView)
async def get_comparison(comparison_id: str):
    """
    Get comparison by ID
    
    Retrieves a specific comparison view by its ID.
    """
    comparison = visualization_service.get_comparison(comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comparison


@router.post("/comparisons/compare")
async def compare_calculations(
    calculation_ids: List[int],
    metrics: List[str]
):
    """
    Compare calculations
    
    Compares multiple calculations on specified metrics.
    """
    try:
        # In production, fetch calculation data from database
        calculation_data_list = []
        # calculation_data_list = fetch_calculations(calculation_ids)
        
        comparison_data = visualization_service.compare_calculations(
            calculation_data_list=calculation_data_list,
            metrics=metrics
        )
        return comparison_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Scenario Analysis Endpoints

@router.post("/scenarios", response_model=ScenarioAnalysis)
async def create_scenario_analysis(request: ScenarioAnalysisRequest):
    """
    Create scenario analysis
    
    Creates a new scenario analysis with multiple scenarios.
    """
    try:
        # In production, fetch base calculation data from database
        base_calculation_data = {}
        # base_calculation_data = fetch_calculation(request.base_calculation_id)
        
        analysis = visualization_service.create_scenario_analysis(
            name=request.name,
            base_calculation_id=request.base_calculation_id,
            parameters=request.parameters,
            base_calculation_data=base_calculation_data,
            num_scenarios=request.num_scenarios,
            description=request.description
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scenarios/{scenario_id}", response_model=ScenarioAnalysis)
async def get_scenario_analysis(scenario_id: str):
    """
    Get scenario analysis by ID
    
    Retrieves a specific scenario analysis by its ID.
    """
    analysis = visualization_service.scenarios.get(scenario_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Scenario analysis not found")
    return analysis


# Sensitivity Analysis Endpoints

@router.post("/sensitivity", response_model=SensitivityAnalysis)
async def create_sensitivity_analysis(request: SensitivityAnalysisRequest):
    """
    Create sensitivity analysis
    
    Creates a new sensitivity analysis showing parameter impacts.
    """
    try:
        # In production, fetch base calculation data from database
        base_calculation_data = {}
        # base_calculation_data = fetch_calculation(request.base_calculation_id)
        
        analysis = visualization_service.create_sensitivity_analysis(
            name=request.name,
            base_calculation_id=request.base_calculation_id,
            parameters=request.parameters,
            base_calculation_data=base_calculation_data,
            num_points=request.num_points,
            description=request.description
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sensitivity/{sensitivity_id}", response_model=SensitivityAnalysis)
async def get_sensitivity_analysis(sensitivity_id: str):
    """
    Get sensitivity analysis by ID
    
    Retrieves a specific sensitivity analysis by its ID.
    """
    analysis = visualization_service.sensitivities.get(sensitivity_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Sensitivity analysis not found")
    return analysis


# What-If Analysis Endpoints

@router.post("/what-if", response_model=WhatIfAnalysis)
async def create_what_if_analysis(request: WhatIfAnalysisRequest):
    """
    Create what-if analysis
    
    Creates a new what-if analysis showing impact of parameter changes.
    """
    try:
        # In production, fetch base calculation data from database
        base_calculation_data = {}
        # base_calculation_data = fetch_calculation(request.base_calculation_id)
        
        analysis = visualization_service.create_what_if_analysis(
            name=request.name,
            base_calculation_id=request.base_calculation_id,
            parameter_changes=request.parameter_changes,
            base_calculation_data=base_calculation_data,
            description=request.description
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/what-if/{what_if_id}", response_model=WhatIfAnalysis)
async def get_what_if_analysis(what_if_id: str):
    """
    Get what-if analysis by ID
    
    Retrieves a specific what-if analysis by its ID.
    """
    analysis = visualization_service.what_ifs.get(what_if_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="What-if analysis not found")
    return analysis


# Export Endpoints

@router.post("/export", response_model=dict)
async def export_visualization(request: ExportRequest):
    """
    Export visualization
    
    Exports a visualization to the specified format.
    """
    try:
        export_data = visualization_service.export_visualization(
            visualization_id=request.visualization_id,
            visualization_type=request.visualization_type.value,
            export_format=request.format
        )
        return export_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/formats")
async def get_export_formats():
    """
    Get available export formats
    
    Returns list of available export formats.
    """
    return {
        "formats": [format.value for format in ExportFormat]
    }
