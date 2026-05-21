"""
Database Audit System API Endpoints

This module provides REST API endpoints for the audit system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.dependencies import get_db, get_current_user
from backend.services.audit_service import AuditService
from backend.models.audit_schemas import (
    AuditLogCreate, AuditLogResponse, AuditLogQuery,
    DataAccessLogCreate, DataAccessLogResponse, DataAccessLogQuery,
    UserActionLogCreate, UserActionLogResponse, UserActionLogQuery,
    ComplianceLogCreate, ComplianceLogResponse, ComplianceLogQuery,
    AuditReportCreate, AuditReportResponse,
    AuditStatistics, AccessStatistics, ComplianceStatistics,
    ActionType, QueryType, ActionCategory, ActionStatus,
    ComplianceType, ComplianceStatus, ReportType
)
from backend.models.user_schemas import UserResponse


router = APIRouter(prefix="/audit", tags=["audit"])


# ==================== Audit Logs ====================

@router.post("/logs", response_model=AuditLogResponse)
def create_audit_log(
    log_data: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new audit log entry.
    
    This endpoint is typically called internally by the system to log changes.
    """
    service = AuditService(db)
    log = service.log_change(log_data)
    return log


@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[ActionType] = Query(None),
    table_name: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve audit logs with optional filtering.
    
    Requires authentication. Admins can see all logs, users can see their own.
    """
    service = AuditService(db)
    
    # Non-admin users can only see their own logs
    if not current_user.is_admin and user_id != current_user.id:
        user_id = current_user.id
    
    query = AuditLogQuery(
        user_id=user_id,
        action=action,
        table_name=table_name,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    logs = service.get_audit_logs(query)
    return logs


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific audit log by ID"""
    service = AuditService(db)
    log = service.get_audit_log_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    # Non-admin users can only see their own logs
    if not current_user.is_admin and log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return log


@router.get("/logs/record/{table_name}/{record_id}", response_model=List[AuditLogResponse])
def get_record_history(
    table_name: str,
    record_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get complete change history for a specific record"""
    service = AuditService(db)
    logs = service.get_record_history(table_name, record_id)
    return logs


# ==================== Data Access Logs ====================

@router.post("/access", response_model=DataAccessLogResponse)
def create_data_access_log(
    log_data: DataAccessLogCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new data access log entry.
    
    This endpoint is typically called internally by the system to log data access.
    """
    service = AuditService(db)
    log = service.log_data_access(log_data)
    return log


@router.get("/access", response_model=List[DataAccessLogResponse])
def get_data_access_logs(
    user_id: Optional[int] = Query(None),
    table_name: Optional[str] = Query(None),
    query_type: Optional[QueryType] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve data access logs with optional filtering.
    
    Requires authentication. Admins can see all logs, users can see their own.
    """
    service = AuditService(db)
    
    # Non-admin users can only see their own logs
    if not current_user.is_admin and user_id != current_user.id:
        user_id = current_user.id
    
    query = DataAccessLogQuery(
        user_id=user_id,
        table_name=table_name,
        query_type=query_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    logs = service.get_data_access_logs(query)
    return logs


# ==================== User Action Logs ====================

@router.post("/actions", response_model=UserActionLogResponse)
def create_user_action_log(
    log_data: UserActionLogCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new user action log entry.
    
    This endpoint is typically called internally by the system to log user actions.
    """
    service = AuditService(db)
    log = service.log_user_action(log_data)
    return log


@router.get("/actions", response_model=List[UserActionLogResponse])
def get_user_action_logs(
    user_id: Optional[int] = Query(None),
    action_type: Optional[str] = Query(None),
    action_category: Optional[ActionCategory] = Query(None),
    status: Optional[ActionStatus] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve user action logs with optional filtering.
    
    Requires authentication. Admins can see all logs, users can see their own.
    """
    service = AuditService(db)
    
    # Non-admin users can only see their own logs
    if not current_user.is_admin and user_id != current_user.id:
        user_id = current_user.id
    
    query = UserActionLogQuery(
        user_id=user_id,
        action_type=action_type,
        action_category=action_category,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    logs = service.get_user_action_logs(query)
    return logs


# ==================== Compliance Logs ====================

@router.post("/compliance", response_model=ComplianceLogResponse)
def create_compliance_log(
    log_data: ComplianceLogCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new compliance log entry.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    log = service.log_compliance_event(log_data)
    return log


@router.get("/compliance", response_model=List[ComplianceLogResponse])
def get_compliance_logs(
    compliance_type: Optional[ComplianceType] = Query(None),
    compliance_status: Optional[ComplianceStatus] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve compliance logs with optional filtering.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    
    query = ComplianceLogQuery(
        compliance_type=compliance_type,
        compliance_status=compliance_status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    logs = service.get_compliance_logs(query)
    return logs


# ==================== Audit Reports ====================

@router.post("/reports", response_model=AuditReportResponse)
def create_audit_report(
    report_data: AuditReportCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new audit report.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    report = service.create_audit_report(report_data, current_user.id)
    return report


@router.get("/reports", response_model=List[AuditReportResponse])
def get_audit_reports(
    report_type: Optional[ReportType] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve audit reports.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    reports = service.get_audit_reports(
        user_id=current_user.id if not current_user.is_admin else None,
        report_type=report_type,
        limit=limit
    )
    return reports


# ==================== Statistics ====================

@router.get("/statistics/audit", response_model=AuditStatistics)
def get_audit_statistics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get audit statistics.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    stats = service.get_audit_statistics(date_from, date_to)
    return stats


@router.get("/statistics/access", response_model=AccessStatistics)
def get_access_statistics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get data access statistics.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    stats = service.get_access_statistics(date_from, date_to)
    return stats


@router.get("/statistics/compliance", response_model=ComplianceStatistics)
def get_compliance_statistics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get compliance statistics.
    
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    stats = service.get_compliance_statistics(date_from, date_to)
    return stats
