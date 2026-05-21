"""
Database Audit System Pydantic Schemas

This module defines the Pydantic schemas for audit system API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Enum for audit action types"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class QueryType(str, Enum):
    """Enum for data access query types"""
    SELECT = "SELECT"
    SEARCH = "SEARCH"
    EXPORT = "EXPORT"


class ActionCategory(str, Enum):
    """Enum for user action categories"""
    AUTH = "AUTH"
    CALCULATION = "CALCULATION"
    REPORT = "REPORT"
    ADMIN = "ADMIN"
    CRM = "CRM"
    PRODUCT = "PRODUCT"
    PDF = "PDF"
    SYSTEM = "SYSTEM"


class ActionStatus(str, Enum):
    """Enum for action status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"


class ComplianceType(str, Enum):
    """Enum for compliance types"""
    GDPR = "GDPR"
    DATA_RETENTION = "DATA_RETENTION"
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    ACCESS_CONTROL = "ACCESS_CONTROL"


class ComplianceStatus(str, Enum):
    """Enum for compliance status"""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING = "PENDING"


class ReportType(str, Enum):
    """Enum for report types"""
    AUDIT = "AUDIT"
    ACCESS = "ACCESS"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"
    USER_ACTIVITY = "USER_ACTIVITY"


class ReportFormat(str, Enum):
    """Enum for report formats"""
    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"


class ReportStatus(str, Enum):
    """Enum for report status"""
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Audit Log Schemas
class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: ActionType
    table_name: str
    record_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: Optional[str]
    action: str
    table_name: str
    record_id: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    changes: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    session_id: Optional[str]
    
    class Config:
        from_attributes = True


# Data Access Log Schemas
class DataAccessLogCreate(BaseModel):
    """Schema for creating a data access log entry"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    table_name: str
    record_id: Optional[str] = None
    query_type: QueryType
    query_params: Optional[Dict[str, Any]] = None
    result_count: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class DataAccessLogResponse(BaseModel):
    """Schema for data access log response"""
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: Optional[str]
    table_name: str
    record_id: Optional[str]
    query_type: str
    query_params: Optional[Dict[str, Any]]
    result_count: Optional[int]
    ip_address: Optional[str]
    session_id: Optional[str]
    
    class Config:
        from_attributes = True


# User Action Log Schemas
class UserActionLogCreate(BaseModel):
    """Schema for creating a user action log entry"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action_type: str
    action_category: ActionCategory
    action_details: Optional[Dict[str, Any]] = None
    status: ActionStatus
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class UserActionLogResponse(BaseModel):
    """Schema for user action log response"""
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: Optional[str]
    action_type: str
    action_category: str
    action_details: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    duration_ms: Optional[int]
    ip_address: Optional[str]
    session_id: Optional[str]
    
    class Config:
        from_attributes = True


# Compliance Log Schemas
class ComplianceLogCreate(BaseModel):
    """Schema for creating a compliance log entry"""
    compliance_type: ComplianceType
    event_type: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    affected_data: Optional[Dict[str, Any]] = None
    compliance_status: ComplianceStatus
    details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ComplianceLogResponse(BaseModel):
    """Schema for compliance log response"""
    id: int
    timestamp: datetime
    compliance_type: str
    event_type: str
    user_id: Optional[int]
    username: Optional[str]
    affected_data: Optional[Dict[str, Any]]
    compliance_status: str
    details: Optional[Dict[str, Any]]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


# Audit Report Schemas
class AuditReportCreate(BaseModel):
    """Schema for creating an audit report"""
    report_type: ReportType
    report_name: str
    date_from: datetime
    date_to: datetime
    filters: Optional[Dict[str, Any]] = None
    file_format: ReportFormat = ReportFormat.PDF


class AuditReportResponse(BaseModel):
    """Schema for audit report response"""
    id: int
    created_at: datetime
    created_by_id: int
    report_type: str
    report_name: str
    date_from: datetime
    date_to: datetime
    filters: Optional[Dict[str, Any]]
    summary: Optional[Dict[str, Any]]
    file_path: Optional[str]
    file_format: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


# Query Schemas
class AuditLogQuery(BaseModel):
    """Schema for querying audit logs"""
    user_id: Optional[int] = None
    action: Optional[ActionType] = None
    table_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class DataAccessLogQuery(BaseModel):
    """Schema for querying data access logs"""
    user_id: Optional[int] = None
    table_name: Optional[str] = None
    query_type: Optional[QueryType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class UserActionLogQuery(BaseModel):
    """Schema for querying user action logs"""
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    action_category: Optional[ActionCategory] = None
    status: Optional[ActionStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ComplianceLogQuery(BaseModel):
    """Schema for querying compliance logs"""
    compliance_type: Optional[ComplianceType] = None
    compliance_status: Optional[ComplianceStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# Statistics Schemas
class AuditStatistics(BaseModel):
    """Schema for audit statistics"""
    total_changes: int
    changes_by_action: Dict[str, int]
    changes_by_table: Dict[str, int]
    changes_by_user: Dict[str, int]
    most_active_users: List[Dict[str, Any]]
    most_modified_tables: List[Dict[str, Any]]


class AccessStatistics(BaseModel):
    """Schema for access statistics"""
    total_accesses: int
    accesses_by_type: Dict[str, int]
    accesses_by_table: Dict[str, int]
    accesses_by_user: Dict[str, int]
    most_accessed_tables: List[Dict[str, Any]]
    most_active_users: List[Dict[str, Any]]


class ComplianceStatistics(BaseModel):
    """Schema for compliance statistics"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_status: Dict[str, int]
    compliance_rate: float
    non_compliant_events: List[Dict[str, Any]]
