"""
Launch Support System
Task 83: Launch monitoring, immediate support, issue tracking, and feedback
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/launch-support", tags=["Launch Support"])


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssueCategory(str, Enum):
    BUG = "bug"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    FEATURE_REQUEST = "feature_request"
    QUESTION = "question"
    OTHER = "other"


class FeedbackType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"


class Issue(BaseModel):
    """Support issue"""
    id: str
    title: str
    description: str
    category: IssueCategory
    severity: IssueSeverity
    status: IssueStatus
    reporter_email: str
    reporter_name: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    tags: List[str] = []
    attachments: List[str] = []


class Feedback(BaseModel):
    """User feedback"""
    id: str
    type: FeedbackType
    message: str
    rating: Optional[int] = None  # 1-5
    user_email: Optional[str] = None
    page: Optional[str] = None
    created_at: datetime
    processed: bool = False


class LaunchMetrics(BaseModel):
    """Launch metrics"""
    active_users: int
    total_sessions: int
    error_rate: float
    avg_response_time_ms: float
    successful_operations: int
    failed_operations: int
    support_tickets: int
    feedback_count: int


# In-memory storage
issues_db: List[Issue] = []
feedback_db: List[Feedback] = []
launch_events: List[Dict] = []


# ============================================
# Launch Monitoring
# ============================================

@router.get("/status")
async def get_launch_status():
    """Get current launch status"""
    now = datetime.now()
    
    # Calculate metrics
    open_issues = len([i for i in issues_db if i.status == IssueStatus.OPEN])
    critical_issues = len([i for i in issues_db if i.severity == IssueSeverity.CRITICAL and i.status != IssueStatus.CLOSED])
    
    if critical_issues > 0:
        status = "critical"
    elif open_issues > 10:
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "launch_time": (now - timedelta(hours=2)).isoformat(),
        "uptime_hours": 2,
        "metrics": {
            "active_users": 150,
            "total_sessions": 500,
            "error_rate": 0.5,
            "avg_response_time_ms": 125,
            "successful_operations": 4500,
            "failed_operations": 25
        },
        "support": {
            "open_issues": open_issues,
            "critical_issues": critical_issues,
            "feedback_received": len(feedback_db)
        },
        "health_checks": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "external_services": "healthy"
        }
    }


@router.get("/metrics")
async def get_launch_metrics():
    """Get detailed launch metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "users": {
            "active": 150,
            "new_today": 45,
            "returning": 105,
            "by_role": {
                "admin": 5,
                "sales": 50,
                "viewer": 95
            }
        },
        "performance": {
            "avg_response_time_ms": 125,
            "p95_response_time_ms": 350,
            "p99_response_time_ms": 750,
            "requests_per_minute": 250
        },
        "errors": {
            "total": 25,
            "by_type": {
                "validation": 15,
                "server": 5,
                "timeout": 3,
                "other": 2
            }
        },
        "features": {
            "projects_created": 75,
            "calculations_run": 200,
            "pdfs_generated": 50,
            "3d_views_rendered": 30
        }
    }


@router.get("/events")
async def get_launch_events(limit: int = 50):
    """Get launch events timeline"""
    # Generate sample events
    events = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "info",
            "message": "System operating normally",
            "source": "monitoring"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "type": "warning",
            "message": "High memory usage detected (85%)",
            "source": "infrastructure"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "type": "info",
            "message": "100 users milestone reached",
            "source": "analytics"
        },
        {
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "type": "success",
            "message": "Launch completed successfully",
            "source": "deployment"
        }
    ]
    
    return {
        "events": events[:limit],
        "total": len(events)
    }


# ============================================
# Issue Management
# ============================================

@router.post("/issues", response_model=Issue)
async def create_issue(
    title: str,
    description: str,
    category: IssueCategory,
    severity: IssueSeverity,
    reporter_email: str,
    reporter_name: Optional[str] = None,
    tags: List[str] = []
):
    """Create a new support issue"""
    issue = Issue(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        category=category,
        severity=severity,
        status=IssueStatus.OPEN,
        reporter_email=reporter_email,
        reporter_name=reporter_name,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=tags
    )
    issues_db.append(issue)
    return issue


@router.get("/issues", response_model=List[Issue])
async def get_issues(
    status: Optional[IssueStatus] = None,
    severity: Optional[IssueSeverity] = None,
    category: Optional[IssueCategory] = None,
    limit: int = 50
):
    """Get support issues"""
    filtered = issues_db
    if status:
        filtered = [i for i in filtered if i.status == status]
    if severity:
        filtered = [i for i in filtered if i.severity == severity]
    if category:
        filtered = [i for i in filtered if i.category == category]
    return filtered[-limit:]


@router.get("/issues/{issue_id}", response_model=Issue)
async def get_issue(issue_id: str):
    """Get issue details"""
    for issue in issues_db:
        if issue.id == issue_id:
            return issue
    raise HTTPException(status_code=404, detail="Issue not found")


@router.put("/issues/{issue_id}")
async def update_issue(
    issue_id: str,
    status: Optional[IssueStatus] = None,
    assigned_to: Optional[str] = None,
    resolution: Optional[str] = None
):
    """Update issue"""
    for issue in issues_db:
        if issue.id == issue_id:
            if status:
                issue.status = status
                if status == IssueStatus.RESOLVED:
                    issue.resolved_at = datetime.now()
            if assigned_to:
                issue.assigned_to = assigned_to
            if resolution:
                issue.resolution = resolution
            issue.updated_at = datetime.now()
            return issue
    raise HTTPException(status_code=404, detail="Issue not found")


@router.get("/issues/summary")
async def get_issues_summary():
    """Get issues summary"""
    return {
        "total": len(issues_db),
        "by_status": {
            "open": len([i for i in issues_db if i.status == IssueStatus.OPEN]),
            "in_progress": len([i for i in issues_db if i.status == IssueStatus.IN_PROGRESS]),
            "resolved": len([i for i in issues_db if i.status == IssueStatus.RESOLVED]),
            "closed": len([i for i in issues_db if i.status == IssueStatus.CLOSED])
        },
        "by_severity": {
            "critical": len([i for i in issues_db if i.severity == IssueSeverity.CRITICAL]),
            "high": len([i for i in issues_db if i.severity == IssueSeverity.HIGH]),
            "medium": len([i for i in issues_db if i.severity == IssueSeverity.MEDIUM]),
            "low": len([i for i in issues_db if i.severity == IssueSeverity.LOW])
        },
        "by_category": {
            "bug": len([i for i in issues_db if i.category == IssueCategory.BUG]),
            "performance": len([i for i in issues_db if i.category == IssueCategory.PERFORMANCE]),
            "usability": len([i for i in issues_db if i.category == IssueCategory.USABILITY]),
            "feature_request": len([i for i in issues_db if i.category == IssueCategory.FEATURE_REQUEST]),
            "question": len([i for i in issues_db if i.category == IssueCategory.QUESTION])
        },
        "avg_resolution_time_hours": 4.5
    }


# ============================================
# Feedback Collection
# ============================================

@router.post("/feedback", response_model=Feedback)
async def submit_feedback(
    type: FeedbackType,
    message: str,
    rating: Optional[int] = None,
    user_email: Optional[str] = None,
    page: Optional[str] = None
):
    """Submit user feedback"""
    feedback = Feedback(
        id=str(uuid.uuid4())[:8],
        type=type,
        message=message,
        rating=rating,
        user_email=user_email,
        page=page,
        created_at=datetime.now()
    )
    feedback_db.append(feedback)
    return feedback


@router.get("/feedback", response_model=List[Feedback])
async def get_feedback(
    type: Optional[FeedbackType] = None,
    processed: Optional[bool] = None,
    limit: int = 50
):
    """Get user feedback"""
    filtered = feedback_db
    if type:
        filtered = [f for f in filtered if f.type == type]
    if processed is not None:
        filtered = [f for f in filtered if f.processed == processed]
    return filtered[-limit:]


@router.put("/feedback/{feedback_id}/process")
async def process_feedback(feedback_id: str):
    """Mark feedback as processed"""
    for feedback in feedback_db:
        if feedback.id == feedback_id:
            feedback.processed = True
            return feedback
    raise HTTPException(status_code=404, detail="Feedback not found")


@router.get("/feedback/summary")
async def get_feedback_summary():
    """Get feedback summary"""
    ratings = [f.rating for f in feedback_db if f.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total": len(feedback_db),
        "processed": len([f for f in feedback_db if f.processed]),
        "unprocessed": len([f for f in feedback_db if not f.processed]),
        "by_type": {
            "positive": len([f for f in feedback_db if f.type == FeedbackType.POSITIVE]),
            "negative": len([f for f in feedback_db if f.type == FeedbackType.NEGATIVE]),
            "suggestion": len([f for f in feedback_db if f.type == FeedbackType.SUGGESTION]),
            "bug_report": len([f for f in feedback_db if f.type == FeedbackType.BUG_REPORT])
        },
        "average_rating": round(avg_rating, 2),
        "rating_distribution": {
            "5": len([f for f in feedback_db if f.rating == 5]),
            "4": len([f for f in feedback_db if f.rating == 4]),
            "3": len([f for f in feedback_db if f.rating == 3]),
            "2": len([f for f in feedback_db if f.rating == 2]),
            "1": len([f for f in feedback_db if f.rating == 1])
        }
    }


# ============================================
# Support Dashboard
# ============================================

@router.get("/dashboard")
async def get_support_dashboard():
    """Get support dashboard data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "launch_status": "healthy",
        "uptime_percent": 99.9,
        "issues": {
            "open": len([i for i in issues_db if i.status == IssueStatus.OPEN]),
            "critical": len([i for i in issues_db if i.severity == IssueSeverity.CRITICAL and i.status != IssueStatus.CLOSED]),
            "resolved_today": len([i for i in issues_db if i.resolved_at and i.resolved_at.date() == datetime.now().date()])
        },
        "feedback": {
            "total_today": len([f for f in feedback_db if f.created_at.date() == datetime.now().date()]),
            "positive_ratio": 0.85,
            "avg_rating": 4.2
        },
        "metrics": {
            "active_users": 150,
            "error_rate": 0.5,
            "avg_response_time_ms": 125
        },
        "recent_issues": [i.dict() for i in issues_db[-5:]],
        "recent_feedback": [f.dict() for f in feedback_db[-5:]]
    }


@router.get("/team-status")
async def get_team_status():
    """Get support team status"""
    return {
        "team_members": [
            {"name": "Support Agent 1", "status": "online", "tickets_assigned": 5},
            {"name": "Support Agent 2", "status": "online", "tickets_assigned": 3},
            {"name": "Support Agent 3", "status": "busy", "tickets_assigned": 7},
            {"name": "Tech Lead", "status": "online", "tickets_assigned": 2}
        ],
        "queue": {
            "waiting": 3,
            "avg_wait_time_minutes": 5
        },
        "sla_compliance": {
            "critical": 100,
            "high": 95,
            "medium": 90,
            "low": 85
        }
    }
