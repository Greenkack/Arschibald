"""
Solar Monitoring Integration Schemas
Pydantic models for monitoring system data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MonitoringSystemType(str, Enum):
    """Types of monitoring systems"""
    SOLAR_EDGE = "solaredge"
    FRONIUS = "fronius"
    SMA = "sma"
    ENPHASE = "enphase"
    HUAWEI = "huawei"
    GENERIC = "generic"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts"""
    LOW_PRODUCTION = "low_production"
    SYSTEM_OFFLINE = "system_offline"
    INVERTER_ERROR = "inverter_error"
    MODULE_FAILURE = "module_failure"
    GRID_DISCONNECTION = "grid_disconnection"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MAINTENANCE_DUE = "maintenance_due"
    WEATHER_IMPACT = "weather_impact"


class MaintenanceStatus(str, Enum):
    """Maintenance task status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


# Request/Response Models

class MonitoringSystemConfig(BaseModel):
    """Configuration for monitoring system connection"""
    system_type: MonitoringSystemType
    api_key: str
    api_secret: Optional[str] = None
    site_id: str
    base_url: Optional[str] = None
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    enabled: bool = True


class RealTimeProductionData(BaseModel):
    """Real-time production data"""
    timestamp: datetime
    current_power: float = Field(description="Current power in kW")
    daily_energy: float = Field(description="Daily energy in kWh")
    monthly_energy: float = Field(description="Monthly energy in kWh")
    yearly_energy: float = Field(description="Yearly energy in kWh")
    lifetime_energy: float = Field(description="Lifetime energy in kWh")
    system_status: str
    inverter_status: Dict[str, Any] = {}
    module_temperatures: List[float] = []
    grid_voltage: Optional[float] = None
    grid_frequency: Optional[float] = None


class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    performance_ratio: float = Field(description="Performance ratio (0-1)")
    capacity_factor: float = Field(description="Capacity factor (0-1)")
    specific_yield: float = Field(description="Specific yield in kWh/kWp")
    availability: float = Field(description="System availability (0-1)")
    degradation_rate: float = Field(description="Annual degradation rate (%)")
    expected_vs_actual: float = Field(description="Actual/Expected ratio")


class PerformanceAnalysisRequest(BaseModel):
    """Request for performance analysis"""
    site_id: str
    start_date: datetime
    end_date: datetime
    include_weather: bool = True
    include_comparison: bool = True
    granularity: str = Field(default="daily", description="hourly, daily, weekly, monthly")


class PerformanceAnalysisResponse(BaseModel):
    """Performance analysis results"""
    site_id: str
    period: Dict[str, datetime]
    metrics: PerformanceMetrics
    production_data: List[Dict[str, Any]]
    weather_correlation: Optional[Dict[str, Any]] = None
    comparison_data: Optional[Dict[str, Any]] = None
    insights: List[str] = []
    recommendations: List[str] = []


class AlertCreate(BaseModel):
    """Create new alert"""
    site_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    data: Dict[str, Any] = {}
    auto_resolve: bool = False


class AlertResponse(BaseModel):
    """Alert response"""
    id: int
    site_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    data: Dict[str, Any]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    is_resolved: bool = False
    auto_resolve: bool


class AlertRule(BaseModel):
    """Alert rule configuration"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str = Field(description="Condition expression")
    threshold: float
    duration: int = Field(description="Duration in minutes before triggering")
    enabled: bool = True
    notification_channels: List[str] = ["email"]


class MaintenanceTaskCreate(BaseModel):
    """Create maintenance task"""
    site_id: str
    title: str
    description: str
    task_type: str = Field(description="cleaning, inspection, repair, upgrade")
    scheduled_date: datetime
    estimated_duration: int = Field(description="Duration in minutes")
    assigned_to: Optional[str] = None
    priority: str = Field(default="normal", description="low, normal, high, urgent")
    recurring: bool = False
    recurrence_pattern: Optional[str] = None


class MaintenanceTaskResponse(BaseModel):
    """Maintenance task response"""
    id: int
    site_id: str
    title: str
    description: str
    task_type: str
    status: MaintenanceStatus
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    estimated_duration: int
    actual_duration: Optional[int] = None
    assigned_to: Optional[str] = None
    priority: str
    recurring: bool
    recurrence_pattern: Optional[str] = None
    notes: List[str] = []
    created_at: datetime
    updated_at: datetime


class PerformanceReportRequest(BaseModel):
    """Request for performance report"""
    site_id: str
    report_type: str = Field(description="daily, weekly, monthly, yearly, custom")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_charts: bool = True
    include_weather: bool = True
    include_financial: bool = True
    format: str = Field(default="pdf", description="pdf, excel, json")


class PerformanceReportResponse(BaseModel):
    """Performance report response"""
    report_id: str
    site_id: str
    report_type: str
    period: Dict[str, datetime]
    summary: Dict[str, Any]
    production_data: Dict[str, Any]
    performance_metrics: PerformanceMetrics
    alerts: List[AlertResponse]
    maintenance_history: List[MaintenanceTaskResponse]
    financial_summary: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    generated_at: datetime
    file_url: Optional[str] = None


class MonitoringDashboardData(BaseModel):
    """Dashboard data for monitoring overview"""
    site_id: str
    current_production: RealTimeProductionData
    today_summary: Dict[str, Any]
    week_summary: Dict[str, Any]
    month_summary: Dict[str, Any]
    active_alerts: List[AlertResponse]
    upcoming_maintenance: List[MaintenanceTaskResponse]
    performance_trend: List[Dict[str, Any]]
    system_health: Dict[str, Any]


class SystemHealthCheck(BaseModel):
    """System health check result"""
    site_id: str
    timestamp: datetime
    overall_status: str = Field(description="healthy, degraded, critical, offline")
    components: Dict[str, Dict[str, Any]]
    issues: List[str] = []
    recommendations: List[str] = []
    last_communication: datetime
    uptime_percentage: float


# Monitoring System Integration Models

class MonitoringAPICredentials(BaseModel):
    """API credentials for monitoring system"""
    system_type: MonitoringSystemType
    api_key: str
    api_secret: Optional[str] = None
    site_id: str
    additional_params: Dict[str, Any] = {}


class MonitoringDataSync(BaseModel):
    """Data synchronization status"""
    site_id: str
    last_sync: datetime
    next_sync: datetime
    sync_status: str
    records_synced: int
    errors: List[str] = []
