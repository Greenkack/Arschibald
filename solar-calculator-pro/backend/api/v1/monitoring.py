"""
Solar Monitoring Integration API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.dependencies import get_db
from ...services.monitoring_service import MonitoringService
from ...models.monitoring_schemas import (
    MonitoringSystemConfig, RealTimeProductionData,
    PerformanceAnalysisRequest, PerformanceAnalysisResponse,
    AlertCreate, AlertResponse, AlertRule,
    MaintenanceTaskCreate, MaintenanceTaskResponse, MaintenanceStatus,
    PerformanceReportRequest, PerformanceReportResponse,
    MonitoringDashboardData, SystemHealthCheck
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    """Get monitoring service instance"""
    return MonitoringService(db)


# Monitoring System Connection

@router.post("/connect", response_model=dict)
async def connect_monitoring_system(
    config: MonitoringSystemConfig,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Connect to monitoring system API"""
    try:
        result = await service.connect_monitoring_system(config)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect: {str(e)}"
        )


# Real-time Production Tracking

@router.get("/realtime/{site_id}", response_model=RealTimeProductionData)
async def get_realtime_production(
    site_id: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Get real-time production data"""
    try:
        data = await service.get_realtime_production(site_id)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get real-time data: {str(e)}"
        )



# Performance Analysis

@router.post("/analyze", response_model=PerformanceAnalysisResponse)
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Analyze system performance"""
    try:
        analysis = await service.analyze_performance(request)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance: {str(e)}"
        )


# Alert System

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Create new alert"""
    try:
        result = await service.create_alert(alert)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )


@router.get("/alerts/{site_id}", response_model=List[AlertResponse])
async def get_active_alerts(
    site_id: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Get active alerts for a site"""
    try:
        alerts = await service.get_active_alerts(site_id)
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    resolved_by: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Resolve an alert"""
    try:
        result = await service.resolve_alert(alert_id, resolved_by)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}"
        )


@router.post("/alerts/rules/{site_id}")
async def add_alert_rule(
    site_id: str,
    rule: AlertRule,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Add alert rule"""
    try:
        service.add_alert_rule(site_id, rule)
        return {"status": "success", "message": "Alert rule added"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add alert rule: {str(e)}"
        )



# Maintenance Scheduling

@router.post("/maintenance", response_model=MaintenanceTaskResponse)
async def create_maintenance_task(
    task: MaintenanceTaskCreate,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Create maintenance task"""
    try:
        result = await service.create_maintenance_task(task)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create maintenance task: {str(e)}"
        )


@router.put("/maintenance/{task_id}", response_model=MaintenanceTaskResponse)
async def update_maintenance_task(
    task_id: int,
    status: MaintenanceStatus,
    notes: str = None,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Update maintenance task"""
    try:
        result = await service.update_maintenance_task(task_id, status, notes)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update maintenance task: {str(e)}"
        )


@router.get("/maintenance/{site_id}/upcoming", response_model=List[MaintenanceTaskResponse])
async def get_upcoming_maintenance(
    site_id: str,
    days_ahead: int = 30,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Get upcoming maintenance tasks"""
    try:
        tasks = await service.get_upcoming_maintenance(site_id, days_ahead)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming maintenance: {str(e)}"
        )


@router.get("/maintenance/{site_id}/overdue", response_model=List[MaintenanceTaskResponse])
async def get_overdue_maintenance(
    site_id: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Get overdue maintenance tasks"""
    try:
        tasks = await service.get_overdue_maintenance(site_id)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overdue maintenance: {str(e)}"
        )


# Performance Reporting

@router.post("/reports", response_model=PerformanceReportResponse)
async def generate_performance_report(
    request: PerformanceReportRequest,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Generate performance report"""
    try:
        report = await service.generate_performance_report(request)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# Dashboard

@router.get("/dashboard/{site_id}", response_model=MonitoringDashboardData)
async def get_dashboard_data(
    site_id: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Get dashboard data"""
    try:
        data = await service.get_dashboard_data(site_id)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/health/{site_id}", response_model=SystemHealthCheck)
async def check_system_health(
    site_id: str,
    service: MonitoringService = Depends(get_monitoring_service)
):
    """Check system health"""
    try:
        health = await service.check_system_health(site_id)
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check system health: {str(e)}"
        )
