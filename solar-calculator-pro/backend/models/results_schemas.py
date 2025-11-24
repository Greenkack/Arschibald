"""
Results Visualization Schemas

Pydantic models for results visualization, comparison, and analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class VisualizationType(str, Enum):
    """Types of visualizations"""
    DASHBOARD = "dashboard"
    COMPARISON = "comparison"
    SCENARIO = "scenario"
    SENSITIVITY = "sensitivity"
    WHAT_IF = "what_if"


class ChartType(str, Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    RADAR = "radar"
    WATERFALL = "waterfall"


class ResultMetric(BaseModel):
    """Individual result metric"""
    name: str
    value: float
    unit: str
    formatted_value: str
    category: str
    description: Optional[str] = None


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    id: str
    type: str  # metric, chart, table, text
    title: str
    position: Dict[str, int]  # x, y, width, height
    data: Dict[str, Any]
    config: Dict[str, Any] = {}


class InteractiveDashboard(BaseModel):
    """Interactive results dashboard"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    calculation_id: int
    widgets: List[DashboardWidget]
    layout: str = "grid"  # grid, flex, custom
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ComparisonItem(BaseModel):
    """Item for comparison"""
    id: int
    name: str
    type: str  # solar, heatpump, combined
    metrics: List[ResultMetric]
    created_at: datetime


class ComparisonView(BaseModel):
    """Comparison view configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    items: List[ComparisonItem]
    metrics_to_compare: List[str]
    chart_type: ChartType = ChartType.BAR
    created_at: Optional[datetime] = None


class ScenarioParameter(BaseModel):
    """Parameter for scenario analysis"""
    name: str
    base_value: float
    min_value: float
    max_value: float
    step: float
    unit: str


class ScenarioResult(BaseModel):
    """Result for a specific scenario"""
    scenario_name: str
    parameters: Dict[str, float]
    metrics: List[ResultMetric]
    total_cost: float
    total_savings: float
    payback_period: float


class ScenarioAnalysis(BaseModel):
    """Scenario analysis configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameters: List[ScenarioParameter]
    scenarios: List[ScenarioResult]
    created_at: Optional[datetime] = None


class SensitivityParameter(BaseModel):
    """Parameter for sensitivity analysis"""
    name: str
    base_value: float
    variation_range: float  # percentage
    unit: str


class SensitivityResult(BaseModel):
    """Result for sensitivity analysis"""
    parameter_name: str
    parameter_value: float
    impact_on_roi: float
    impact_on_payback: float
    impact_on_savings: float


class SensitivityAnalysis(BaseModel):
    """Sensitivity analysis configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameters: List[SensitivityParameter]
    results: List[SensitivityResult]
    tornado_chart_data: Dict[str, Any]
    created_at: Optional[datetime] = None


class WhatIfParameter(BaseModel):
    """Parameter for what-if analysis"""
    name: str
    current_value: float
    new_value: float
    unit: str


class WhatIfResult(BaseModel):
    """Result for what-if analysis"""
    parameter_changes: List[WhatIfParameter]
    original_metrics: List[ResultMetric]
    new_metrics: List[ResultMetric]
    delta_metrics: List[ResultMetric]


class WhatIfAnalysis(BaseModel):
    """What-if analysis configuration"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameter_changes: List[WhatIfParameter]
    result: WhatIfResult
    created_at: Optional[datetime] = None


class ExportFormat(str, Enum):
    """Export formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    PNG = "png"
    SVG = "svg"


class ExportRequest(BaseModel):
    """Request for exporting results"""
    visualization_id: str
    visualization_type: VisualizationType
    format: ExportFormat
    include_charts: bool = True
    include_data: bool = True
    include_metadata: bool = True


class ExportResponse(BaseModel):
    """Response for export request"""
    file_url: str
    file_name: str
    file_size: int
    format: ExportFormat
    created_at: datetime


class DashboardCreateRequest(BaseModel):
    """Request to create dashboard"""
    name: str
    description: Optional[str] = None
    calculation_id: int
    widgets: List[DashboardWidget]
    layout: str = "grid"


class ComparisonCreateRequest(BaseModel):
    """Request to create comparison"""
    name: str
    description: Optional[str] = None
    calculation_ids: List[int]
    metrics_to_compare: List[str]
    chart_type: ChartType = ChartType.BAR


class ScenarioAnalysisRequest(BaseModel):
    """Request to create scenario analysis"""
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameters: List[ScenarioParameter]
    num_scenarios: int = Field(default=5, ge=2, le=20)


class SensitivityAnalysisRequest(BaseModel):
    """Request to create sensitivity analysis"""
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameters: List[SensitivityParameter]
    num_points: int = Field(default=10, ge=5, le=50)


class WhatIfAnalysisRequest(BaseModel):
    """Request to create what-if analysis"""
    name: str
    description: Optional[str] = None
    base_calculation_id: int
    parameter_changes: List[WhatIfParameter]
