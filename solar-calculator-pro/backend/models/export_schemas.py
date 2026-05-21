"""
Pydantic schemas for results export functionality.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime


class ExportRequest(BaseModel):
    """Base export request schema"""
    result_id: int = Field(..., description="ID of the result to export")
    format: Literal['pdf', 'excel', 'csv', 'json', 'xml'] = Field(..., description="Export format")
    options: Dict[str, Any] = Field(default_factory=dict, description="Format-specific options")


class PDFExportOptions(BaseModel):
    """PDF export options"""
    include_charts: bool = Field(default=True, description="Include charts in PDF")
    include_tables: bool = Field(default=True, description="Include data tables")
    include_summary: bool = Field(default=True, description="Include executive summary")
    page_size: Literal['A4', 'Letter', 'Legal'] = Field(default='A4')
    orientation: Literal['portrait', 'landscape'] = Field(default='portrait')
    template: Optional[str] = Field(default=None, description="PDF template name")


class ExcelExportOptions(BaseModel):
    """Excel export options"""
    include_charts: bool = Field(default=True, description="Include charts as images")
    include_formulas: bool = Field(default=False, description="Include Excel formulas")
    sheet_names: Optional[List[str]] = Field(default=None, description="Custom sheet names")
    freeze_panes: bool = Field(default=True, description="Freeze header rows")
    auto_filter: bool = Field(default=True, description="Enable auto-filter")


class CSVExportOptions(BaseModel):
    """CSV export options"""
    delimiter: str = Field(default=',', description="CSV delimiter")
    encoding: str = Field(default='utf-8', description="File encoding")
    include_headers: bool = Field(default=True, description="Include column headers")
    decimal_separator: str = Field(default=',', description="Decimal separator (German: )")
    thousands_separator: str = Field(default='.', description="Thousands separator (German: .)")


class JSONExportOptions(BaseModel):
    """JSON export options"""
    pretty_print: bool = Field(default=True, description="Format JSON with indentation")
    include_metadata: bool = Field(default=True, description="Include export metadata")
    date_format: str = Field(default='iso', description="Date format (iso, unix, custom)")


class XMLExportOptions(BaseModel):
    """XML export options"""
    root_element: str = Field(default='result', description="Root XML element name")
    include_schema: bool = Field(default=False, description="Include XML schema")
    pretty_print: bool = Field(default=True, description="Format XML with indentation")


class ExportResponse(BaseModel):
    """Export response schema"""
    export_id: str = Field(..., description="Unique export ID")
    format: str = Field(..., description="Export format")
    file_name: str = Field(..., description="Generated file name")
    file_size: int = Field(..., description="File size in bytes")
    download_url: str = Field(..., description="Download URL")
    expires_at: datetime = Field(..., description="URL expiration time")
    created_at: datetime = Field(default_factory=datetime.now)


class BatchExportRequest(BaseModel):
    """Batch export request for multiple results"""
    result_ids: List[int] = Field(..., description="List of result IDs to export")
    format: Literal['pdf', 'excel', 'csv', 'json', 'xml'] = Field(..., description="Export format")
    options: Dict[str, Any] = Field(default_factory=dict, description="Format-specific options")
    combine_files: bool = Field(default=False, description="Combine into single file")


class ExportHistory(BaseModel):
    """Export history record"""
    id: int
    result_id: int
    format: str
    file_name: str
    file_size: int
    user_id: Optional[int]
    created_at: datetime
    downloaded_at: Optional[datetime]
    download_count: int = 0


class APIExportConfig(BaseModel):
    """API export configuration"""
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL for async exports")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    format: Literal['json', 'xml'] = Field(default='json', description="API response format")
    include_raw_data: bool = Field(default=False, description="Include raw calculation data")
