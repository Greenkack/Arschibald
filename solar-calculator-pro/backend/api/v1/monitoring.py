"""
Monitoring API Endpoints

Provides endpoints for post-release monitoring, crash reporting, and analytics.
Requirement: 8.1 - Performance monitoring and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from backend.core.dependencies import get_db
from backend.services.monitoring_service import MonitoringService


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ==================== Request/Response Models ====================

class PerformanceMetricRequest(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    metadata: dict = Field(default_factory=dict, description="Additional context")


class CrashReportRequest(BaseModel):
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    stack_trace: str = Field(..., description="Full stack trace")
    user_id: Optional[int] = Field(None, description="User ID")
    app_version: Optional[str] = Field(None, description="Application version")
    metadata: dict = Field(default_factory=dict, description="Additional context")


class FeedbackRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    feedback_type: str = Field(..., description="Type of feedback")
    title: str = Field(..., description="Feedback title")
    description: str = Field(..., description="Detailed description")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    metadata: dict = Field(default_factory=dict, description="Additional context")


class UpdateAdoptionRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    from_version: str = Field(..., description="Previous version")
    to_version: str = Field(..., description="New version")
    update_method: str = Field(..., description="Update method")
    success: bool = Field(..., description="Update success")
    duration_seconds: Optional[float] = Field(None, description="Update duration")


# ==================== Performance Monitoring Endpoints ====================

@router.post("/performance/track")
async def track_performance_metric(
    request: PerformanceMetricRequest,
    db: Session = Depends(get_db)
):
    """
    Track a performance metric
    
    **Example metrics:**
    - api_response_time (ms)
    - memory_usage (MB)
    - cpu_usage (percent)
    - database_query_time (ms)
    """
    service = MonitoringService(db)
    
    metric = service.track_performance_metric(
        metric_name=request.metric_name,
        value=request.value,
        unit=request.unit,
        metadata=request.metadata
    )
    
    return {
        "success": True,
        "metric": metric
    }


@router.get("/performance/summary")
async def get_performance_summary(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """
    Get performance summary for a time period
    
    Returns system metrics, platform info, and performance statistics.
    """
    service = MonitoringService(db)
    
    summary = service.get_performance_summary(
        start_date=start_date,
        end_date=end_date
    )
    
    return summary


@router.get("/performance/trends/{metric_name}")
async def get_performance_trends(
    metric_name: str,
    days: int = Query(7, ge=1, le=90, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Get performance trends for a specific metric
    
    Returns daily averages and trend analysis.
    """
    service = MonitoringService(db)
    
    trends = service.get_performance_trends(
        metric_name=metric_name,
        days=days
    )
    
    return trends


# ==================== Crash Reporting Endpoints ====================

@router.post("/crashes/report")
async def report_crash(
    request: CrashReportRequest,
    db: Session = Depends(get_db)
):
    """
    Report an application crash
    
    Captures error details, stack trace, and context for debugging.
    """
    service = MonitoringService(db)
    
    crash_report = service.report_crash(
        error_type=request.error_type,
        error_message=request.error_message,
        stack_trace=request.stack_trace,
        user_id=request.user_id,
        app_version=request.app_version,
        metadata=request.metadata
    )
    
    return {
        "success": True,
        "crash_report": crash_report
    }


@router.get("/crashes/reports")
async def get_crash_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    days: int = Query(7, ge=1, le=90, description="Number of days"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get crash reports
    
    Filter by status: new, investigating, resolved
    """
    service = MonitoringService(db)
    
    reports = service.get_crash_reports(
        status=status,
        days=days,
        limit=limit
    )
    
    return {
        "total": len(reports),
        "reports": reports
    }


@router.get("/crashes/statistics")
async def get_crash_statistics(
    days: int = Query(7, ge=1, le=90, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Get crash statistics
    
    Returns crash counts, affected users, and crash-free rate.
    """
    service = MonitoringService(db)
    
    stats = service.get_crash_statistics(days=days)
    
    return stats


# ==================== User Feedback Endpoints ====================

@router.post("/feedback/submit")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback
    
    **Feedback types:**
    - bug: Report a bug
    - feature_request: Request a new feature
    - improvement: Suggest an improvement
    - praise: Positive feedback
    """
    service = MonitoringService(db)
    
    feedback = service.submit_feedback(
        user_id=request.user_id,
        feedback_type=request.feedback_type,
        title=request.title,
        description=request.description,
        rating=request.rating,
        metadata=request.metadata
    )
    
    return {
        "success": True,
        "feedback": feedback
    }


@router.get("/feedback/summary")
async def get_feedback_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Get feedback summary
    
    Returns feedback counts by type, average rating, and trending topics.
    """
    service = MonitoringService(db)
    
    summary = service.get_feedback_summary(days=days)
    
    return summary


# ==================== Update Adoption Endpoints ====================

@router.post("/updates/track")
async def track_update_adoption(
    request: UpdateAdoptionRequest,
    db: Session = Depends(get_db)
):
    """
    Track update adoption
    
    Records when users update to new versions.
    """
    service = MonitoringService(db)
    
    update_record = service.track_update_adoption(
        user_id=request.user_id,
        from_version=request.from_version,
        to_version=request.to_version,
        update_method=request.update_method,
        success=request.success,
        duration_seconds=request.duration_seconds
    )
    
    return {
        "success": True,
        "update_record": update_record
    }


@router.get("/updates/adoption/{version}")
async def get_update_adoption_stats(
    version: str,
    db: Session = Depends(get_db)
):
    """
    Get update adoption statistics for a version
    
    Returns adoption rate, update methods, and timeline.
    """
    service = MonitoringService(db)
    
    stats = service.get_update_adoption_stats(version=version)
    
    return stats


@router.get("/updates/distribution")
async def get_version_distribution(
    db: Session = Depends(get_db)
):
    """
    Get current version distribution across users
    
    Shows which versions users are running.
    """
    service = MonitoringService(db)
    
    distribution = service.get_version_distribution()
    
    return distribution


# ==================== Improvement Planning Endpoints ====================

@router.get("/improvements/opportunities")
async def analyze_improvement_opportunities(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Analyze data to identify improvement opportunities
    
    Returns prioritized list of improvements based on crashes, feedback, and performance.
    """
    service = MonitoringService(db)
    
    opportunities = service.analyze_improvement_opportunities(days=days)
    
    return opportunities


@router.post("/improvements/roadmap")
async def create_improvement_roadmap(
    opportunities: dict,
    db: Session = Depends(get_db)
):
    """
    Create improvement roadmap from opportunities
    
    Organizes improvements into quarterly plan.
    """
    service = MonitoringService(db)
    
    roadmap = service.create_improvement_roadmap(opportunities=opportunities)
    
    return roadmap


# ==================== Health Status Endpoint ====================

@router.get("/health")
async def get_health_status(
    db: Session = Depends(get_db)
):
    """
    Get overall application health status
    
    Returns: healthy, degraded, or critical
    """
    service = MonitoringService(db)
    
    health = service.get_health_status()
    
    return health
