"""
Import/Export Pydantic Schemas

Request and response models for import/export API endpoints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ImportFormatEnum(str, Enum):
    """Import format options"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"


class ExportFormatEnum(str, Enum):
    """Export format options"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ValidationRuleSchema(BaseModel):
    """Validation rule schema"""
    field: str = Field(..., description="Field name to validate")
    rule_type: str = Field(..., description="Type of validation rule")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")
    error_message: str = Field(..., description="Error message if validation fails")


class DataMappingSchema(BaseModel):
    """Data mapping schema"""
    source_field: str = Field(..., description="Source field name")
    target_field: str = Field(..., description="Target field name")
    transformation: Optional[str] = Field(None, description="Transformation function name")
    default_value: Optional[Any] = Field(None, description="Default value if source is missing")


class ImportConfigSchema(BaseModel):
    """Import configuration schema"""
    format: ImportFormatEnum = Field(..., description="Import format")
    mappings: List[DataMappingSchema] = Field(..., description="Field mappings")
    validation_rules: List[ValidationRuleSchema] = Field(default_factory=list, description="Validation rules")
    skip_errors: bool = Field(False, description="Skip records with errors")
    batch_size: int = Field(100, description="Batch processing size")


class ExportConfigSchema(BaseModel):
    """Export configuration schema"""
    format: ExportFormatEnum = Field(..., description="Export format")
    fields: List[str] = Field(..., description="Fields to export")
    include_headers: bool = Field(True, description="Include headers in export")
    custom_headers: Optional[Dict[str, str]] = Field(None, description="Custom header names")


class ImportRequest(BaseModel):
    """Import data request"""
    file_content: str = Field(..., description="Base64 encoded file content")
    config: ImportConfigSchema = Field(..., description="Import configuration")


class ImportResultSchema(BaseModel):
    """Import operation result"""
    success: bool = Field(..., description="Whether import was successful")
    total_records: int = Field(..., description="Total number of records")
    imported_records: int = Field(..., description="Number of successfully imported records")
    failed_records: int = Field(..., description="Number of failed records")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")


class ExportRequest(BaseModel):
    """Export data request"""
    data_source: str = Field(..., description="Data source identifier (e.g., 'projects', 'customers')")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply")
    config: ExportConfigSchema = Field(..., description="Export configuration")


class ExportResponse(BaseModel):
    """Export data response"""
    file_content: str = Field(..., description="Base64 encoded file content")
    filename: str = Field(..., description="Suggested filename")
    content_type: str = Field(..., description="MIME type")


class TemplateRequest(BaseModel):
    """Import template request"""
    fields: List[str] = Field(..., description="Fields to include in template")
    format: ExportFormatEnum = Field(ExportFormatEnum.CSV, description="Template format")


class ValidationRequest(BaseModel):
    """File validation request"""
    file_content: str = Field(..., description="Base64 encoded file content")
    config: ImportConfigSchema = Field(..., description="Import configuration")


class ValidationResponse(BaseModel):
    """File validation response"""
    valid: bool = Field(..., description="Whether file is valid")
    record_count: Optional[int] = Field(None, description="Number of records found")
    fields: Optional[List[str]] = Field(None, description="Fields found in file")
    error: Optional[str] = Field(None, description="Error message if invalid")


class BatchImportRequest(BaseModel):
    """Batch import request"""
    files: List[Dict[str, str]] = Field(..., description="List of files with name and content")
    config: ImportConfigSchema = Field(..., description="Import configuration")


class BatchImportResult(BaseModel):
    """Batch import result"""
    total_files: int = Field(..., description="Total number of files")
    successful_files: int = Field(..., description="Number of successfully processed files")
    failed_files: int = Field(..., description="Number of failed files")
    results: List[ImportResultSchema] = Field(..., description="Individual file results")


class DataSourceInfo(BaseModel):
    """Data source information"""
    name: str = Field(..., description="Data source name")
    description: str = Field(..., description="Data source description")
    available_fields: List[str] = Field(..., description="Available fields for export")
    record_count: int = Field(..., description="Total number of records")


class TransformationInfo(BaseModel):
    """Transformation function information"""
    name: str = Field(..., description="Transformation name")
    description: str = Field(..., description="Transformation description")
    example: str = Field(..., description="Usage example")


class ValidatorInfo(BaseModel):
    """Validator function information"""
    name: str = Field(..., description="Validator name")
    description: str = Field(..., description="Validator description")
    parameters: List[str] = Field(default_factory=list, description="Required parameters")
