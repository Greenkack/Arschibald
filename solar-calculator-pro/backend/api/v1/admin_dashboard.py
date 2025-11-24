"""
Admin Dashboard API Endpoints
Provides endpoints for system monitoring, health checks, and usage statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ...core.dependencies import get_db
from ...services.admin_dashboard_service import AdminDashboardService

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard summary
    
    Returns:
        - System health metrics
        - Database health
        - Usage statistics
        - Performance metrics
        - Active alerts
        - User activity overview
    """
    try:
        service = AdminDashboardService(db)
        summary = service.get_dashboard_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/system")
async def get_system_health(
    db: Session = Depends(get_db)
):
    """
    Get system health metrics
    
    Returns:
        - CPU usage
        - Memory usage
        - Disk usage
        - Process information
        - System uptime
        - Health status and issues
    """
    try:
        service = AdminDashboardService(db)
        health = service.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/database")
async def get_database_health(
    db: Session = Depends(get_db)
):
    """
    Get database health and statistics
    
    Returns:
        - Connection status
        - Table statistics
        - Total records
        - Database health status
    """
    try:
        service = AdminDashboardService(db)
        health = service.get_database_health()
        return health
    except Exception as e:
        logger.error(f"Error getting database health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/usage")
async def get_usage_statistics(
    period: str = Query("today", regex="^(today|week|month|year)$"),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for specified period
    
    Args:
        period: Time period (today, week, month, year)
    
    Returns:
        - User statistics
        - Project statistics
        - Calculation statistics
        - PDF generation statistics
        - API usage statistics
    """
    try:
        service = AdminDashboardService(db)
        stats = service.get_usage_statistics(period)
        return stats
    except Exception as e:
        logger.error(f"Error getting usage statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/performance")
async def get_performance_metrics(
    db: Session = Depends(get_db)
):
    """
    Get system performance metrics
    
    Returns:
        - Response time metrics
        - Throughput metrics
        - Error rate metrics
        - Resource usage trends
        - Cache performance
    """
    try:
        service = AdminDashboardService(db)
        metrics = service.get_performance_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activity/users")
async def get_user_activity(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get user activity overview
    
    Args:
        limit: Maximum number of records to return
    
    Returns:
        - Recent logins
        - Active sessions
        - Recent user actions
        - Top users by activity
    """
    try:
        service = AdminDashboardService(db)
        activity = service.get_user_activity_overview(limit)
        return activity
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_system_alerts(
    severity: Optional[str] = Query(None, regex="^(info|warning|critical)$"),
    db: Session = Depends(get_db)
):
    """
    Get system alerts
    
    Args:
        severity: Filter by severity (info, warning, critical)
    
    Returns:
        List of system alerts with details
    """
    try:
        service = AdminDashboardService(db)
        alerts = service.get_system_alerts(severity)
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        logger.error(f"Error getting system alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Resolve a system alert
    
    Args:
        alert_id: ID of the alert to resolve
    
    Returns:
        Success status
    """
    try:
        service = AdminDashboardService(db)
        success = service.resolve_alert(alert_id)
        
        if success:
            return {"message": "Alert resolved successfully", "alert_id": alert_id}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/historical")
async def get_historical_metrics(
    metric_type: str = Query(..., regex="^(system_health|usage|performance)$"),
    period: str = Query("week", regex="^(today|week|month|year)$"),
    db: Session = Depends(get_db)
):
    """
    Get historical metrics data
    
    Args:
        metric_type: Type of metrics (system_health, usage, performance)
        period: Time period (today, week, month, year)
    
    Returns:
        Historical metrics data for the specified period
    """
    try:
        service = AdminDashboardService(db)
        metrics = service.get_historical_metrics(metric_type, period)
        return metrics
    except Exception as e:
        logger.error(f"Error getting historical metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint for monitoring
@router.get("/ping")
async def ping():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "admin-dashboard"}
