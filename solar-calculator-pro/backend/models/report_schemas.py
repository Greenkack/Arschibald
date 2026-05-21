# backend/models/report_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration"""
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    ENVIRONMENTAL = "environmental"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Report output format"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    EXCEL = "excel"
    CSV = "csv"


class ReportSection(BaseModel):
    """Individual report section"""
    title: str
    content: Dict[str, Any]
    order: int = 0
    visible: bool = True
    charts: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []


class ReportTemplate(BaseModel):
    """Report template configuration"""
    id: Optional[int] = None
    name: str
    report_type: ReportType
    sections: List[ReportSection]
    header: Optional[Dict[str, Any]] = None
    footer: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReportGenerationRequest(BaseModel):
    """Request to generate a report"""
    project_id: int
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    template_id: Optional[int] = None
    custom_sections: Optional[List[ReportSection]] = None
    include_charts: bool = True
    include_tables: bool = True
    include_raw_data: bool = False
    language: str = "de"
    branding: Optional[Dict[str, Any]] = None


class DetailedReportData(BaseModel):
    """Data for detailed result report"""
    project_info: Dict[str, Any]
    system_configuration: Dict[str, Any]
    calculation_results: Dict[str, Any]
    energy_analysis: Dict[str, Any]
    financial_analysis: Dict[str, Any]
    environmental_impact: Dict[str, Any]
    technical_specifications: Dict[str, Any]
    recommendations: List[str]
    charts: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]


class ExecutiveSummaryData(BaseModel):
    """Data for executive summary report"""
    project_name: str
    customer_name: str
    system_size: float
    total_cost: float
    annual_savings: float
    payback_period: float
    roi_percentage: float
    co2_reduction: float
    key_highlights: List[str]
    recommendation: str
    charts: List[Dict[str, Any]]


class TechnicalReportData(BaseModel):
    """Data for technical report"""
    system_design: Dict[str, Any]
    component_specifications: List[Dict[str, Any]]
    installation_requirements: Dict[str, Any]
    electrical_design: Dict[str, Any]
    mounting_system: Dict[str, Any]
    performance_calculations: Dict[str, Any]
    compliance_standards: List[str]
    technical_drawings: List[Dict[str, Any]]


class FinancialReportData(BaseModel):
    """Data for financial report"""
    investment_summary: Dict[str, Any]
    cost_breakdown: Dict[str, Any]
    revenue_projections: Dict[str, Any]
    cash_flow_analysis: Dict[str, Any]
    roi_analysis: Dict[str, Any]
    financing_options: List[Dict[str, Any]]
    tax_benefits: Dict[str, Any]
    sensitivity_analysis: Dict[str, Any]
    charts: List[Dict[str, Any]]


class EnvironmentalReportData(BaseModel):
    """Data for environmental report"""
    co2_emissions_avoided: float
    equivalent_trees_planted: int
    equivalent_cars_removed: int
    renewable_energy_percentage: float
    lifecycle_analysis: Dict[str, Any]
    environmental_certifications: List[str]
    sustainability_metrics: Dict[str, Any]
    charts: List[Dict[str, Any]]


class ReportMetadata(BaseModel):
    """Report metadata"""
    report_id: str
    project_id: int
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    generated_by: str
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    version: str = "1.0"


class ReportResponse(BaseModel):
    """Response after report generation"""
    success: bool
    report_id: str
    metadata: ReportMetadata
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    file_path: Optional[str] = None
    message: Optional[str] = None


class ReportListItem(BaseModel):
    """Report list item for history"""
    report_id: str
    project_id: int
    project_name: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    file_size: int
    download_url: str


class ReportHistoryResponse(BaseModel):
    """Response for report history"""
    reports: List[ReportListItem]
    total: int
    page: int
    page_size: int
