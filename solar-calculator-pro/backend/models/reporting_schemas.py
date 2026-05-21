# Reporting and Analytics Schemas

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Report types"""
    SALES = "sales"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    CUSTOMER = "customer"
    PRODUCT = "product"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ScheduleFrequency(str, Enum):
    """Report schedule frequencies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AggregationType(str, Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"


class ChartType(str, Enum):
    """Chart types for visualizations"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    DONUT = "donut"


# Report Builder Schemas

class ReportField(BaseModel):
    """Field configuration for report"""
    name: str
    label: str
    data_type: str  # string, number, date, boolean
    aggregation: Optional[AggregationType] = None
    format: Optional[str] = None  # e.g., "currency", "percentage"


class ReportFilter(BaseModel):
    """Filter configuration for report"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, between, like
    value: Any


class ReportSort(BaseModel):
    """Sort configuration for report"""
    field: str
    direction: str = "asc"  # asc or desc


class ReportVisualization(BaseModel):
    """Visualization configuration"""
    chart_type: ChartType
    x_axis: str
    y_axis: str
    title: str
    color_scheme: Optional[str] = "default"


class ReportDefinition(BaseModel):
    """Complete report definition"""
    name: str
    description: Optional[str] = None
    report_type: ReportType
    data_source: str  # table or view name
    fields: List[ReportField]
    filters: List[ReportFilter] = []
    sorts: List[ReportSort] = []
    visualizations: List[ReportVisualization] = []
    group_by: List[str] = []
    limit: Optional[int] = None


class ReportCreate(BaseModel):
    """Create report request"""
    definition: ReportDefinition
    owner_id: int
    is_public: bool = False
    tags: List[str] = []


class ReportUpdate(BaseModel):
    """Update report request"""
    definition: Optional[ReportDefinition] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class ReportExecute(BaseModel):
    """Execute report request"""
    report_id: int
    parameters: Dict[str, Any] = {}
    format: ReportFormat = ReportFormat.JSON


class ReportResponse(BaseModel):
    """Report execution response"""
    id: int
    name: str
    report_type: ReportType
    executed_at: datetime
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    visualizations: List[Dict[str, Any]] = []


# Scheduled Reports Schemas

class ScheduleCreate(BaseModel):
    """Create schedule request"""
    report_id: int
    frequency: ScheduleFrequency
    time_of_day: str  # HH:MM format
    recipients: List[str]  # email addresses
    format: ReportFormat = ReportFormat.PDF
    enabled: bool = True


class ScheduleUpdate(BaseModel):
    """Update schedule request"""
    frequency: Optional[ScheduleFrequency] = None
    time_of_day: Optional[str] = None
    recipients: Optional[List[str]] = None
    format: Optional[ReportFormat] = None
    enabled: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """Schedule response"""
    id: int
    report_id: int
    report_name: str
    frequency: ScheduleFrequency
    time_of_day: str
    recipients: List[str]
    format: ReportFormat
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: datetime
    created_at: datetime


# Dashboard Widgets Schemas

class WidgetType(str, Enum):
    """Widget types"""
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    GAUGE = "gauge"
    MAP = "map"
    TEXT = "text"


class WidgetSize(str, Enum):
    """Widget sizes"""
    SMALL = "small"  # 1x1
    MEDIUM = "medium"  # 2x1
    LARGE = "large"  # 2x2
    XLARGE = "xlarge"  # 3x2


class WidgetConfig(BaseModel):
    """Widget configuration"""
    widget_type: WidgetType
    title: str
    data_source: str
    query: Dict[str, Any]
    visualization: Optional[Dict[str, Any]] = None
    refresh_interval: int = 300  # seconds
    size: WidgetSize = WidgetSize.MEDIUM


class WidgetCreate(BaseModel):
    """Create widget request"""
    dashboard_id: int
    config: WidgetConfig
    position_x: int = 0
    position_y: int = 0


class WidgetUpdate(BaseModel):
    """Update widget request"""
    config: Optional[WidgetConfig] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None


class WidgetResponse(BaseModel):
    """Widget response"""
    id: int
    dashboard_id: int
    config: WidgetConfig
    position_x: int
    position_y: int
    data: Dict[str, Any]
    last_updated: datetime


class DashboardCreate(BaseModel):
    """Create dashboard request"""
    name: str
    description: Optional[str] = None
    is_public: bool = False
    layout: str = "grid"  # grid or freeform


class DashboardResponse(BaseModel):
    """Dashboard response"""
    id: int
    name: str
    description: Optional[str] = None
    is_public: bool
    layout: str
    widgets: List[WidgetResponse]
    created_at: datetime
    updated_at: datetime


# KPI Tracking Schemas

class KPIMetric(str, Enum):
    """KPI metric types"""
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    CUSTOMER_ACQUISITION_COST = "customer_acquisition_cost"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    AVERAGE_ORDER_VALUE = "average_order_value"
    CHURN_RATE = "churn_rate"
    GROWTH_RATE = "growth_rate"


class KPITarget(BaseModel):
    """KPI target configuration"""
    metric: KPIMetric
    target_value: float
    period: str  # daily, weekly, monthly, quarterly, yearly
    comparison_operator: str = "gte"  # gte, lte, eq


class KPICreate(BaseModel):
    """Create KPI request"""
    name: str
    metric: KPIMetric
    target: KPITarget
    data_source: str
    calculation: Dict[str, Any]


class KPIResponse(BaseModel):
    """KPI response"""
    id: int
    name: str
    metric: KPIMetric
    current_value: float
    target_value: float
    achievement_percentage: float
    trend: str  # up, down, stable
    period: str
    last_updated: datetime


# Predictive Analytics Schemas

class PredictionModel(str, Enum):
    """Prediction model types"""
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"


class PredictionRequest(BaseModel):
    """Prediction request"""
    model_type: PredictionModel
    data_source: str
    target_field: str
    feature_fields: List[str]
    prediction_period: int  # days into future
    confidence_level: float = 0.95


class PredictionResponse(BaseModel):
    """Prediction response"""
    model_type: PredictionModel
    predictions: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    accuracy_metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    generated_at: datetime


# Data Export Schemas

class ExportFormat(str, Enum):
    """Export formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Data export request"""
    data_source: str
    filters: List[ReportFilter] = []
    fields: List[str] = []
    format: ExportFormat = ExportFormat.CSV
    include_headers: bool = True
    german_formatting: bool = True  # Use German number formatting


class ExportResponse(BaseModel):
    """Export response"""
    file_name: str
    file_size: int
    download_url: str
    expires_at: datetime
    format: ExportFormat
