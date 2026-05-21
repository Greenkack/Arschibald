"""
User Feedback Integration System
Task 86: Collect feedback, prioritize improvements, implement enhancements
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/user-feedback", tags=["User Feedback Integration"])


class FeedbackCategory(str, Enum):
    USABILITY = "usability"
    PERFORMANCE = "performance"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    DESIGN = "design"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class FeedbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackStatus(str, Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DECLINED = "declined"


class UserFeedback(BaseModel):
    """User feedback entry"""
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    category: FeedbackCategory
    title: str
    description: str
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    status: FeedbackStatus = FeedbackStatus.NEW
    rating: Optional[int] = None  # 1-5
    page_url: Optional[str] = None
    browser: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    votes: int = 0
    tags: List[str] = []
    attachments: List[str] = []


class Improvement(BaseModel):
    """Improvement/enhancement item"""
    id: str
    title: str
    description: str
    category: FeedbackCategory
    priority: FeedbackPriority
    status: str
    related_feedback_ids: List[str] = []
    estimated_effort: str  # hours, days, weeks
    assigned_to: Optional[str] = None
    target_release: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# In-memory storage
feedback_db: List[UserFeedback] = []
improvements_db: List[Improvement] = []
feedback_votes: Dict[str, List[str]] = {}  # feedback_id -> list of user_ids


# ============================================
# Feedback Collection
# ============================================

@router.post("/submit", response_model=UserFeedback)
async def submit_feedback(
    category: FeedbackCategory,
    title: str,
    description: str,
    user_email: Optional[str] = None,
    rating: Optional[int] = None,
    page_url: Optional[str] = None,
    tags: List[str] = []
):
    """Submit user feedback"""
    feedback = UserFeedback(
        id=str(uuid.uuid4())[:8],
        user_email=user_email,
        category=category,
        title=title,
        description=description,
        rating=rating,
        page_url=page_url,
        tags=tags,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    feedback_db.append(feedback)
    return feedback


@router.get("/list", response_model=List[UserFeedback])
async def list_feedback(
    category: Optional[FeedbackCategory] = None,
    status: Optional[FeedbackStatus] = None,
    priority: Optional[FeedbackPriority] = None,
    limit: int = 50
):
    """List feedback entries"""
    filtered = feedback_db
    if category:
        filtered = [f for f in filtered if f.category == category]
    if status:
        filtered = [f for f in filtered if f.status == status]
    if priority:
        filtered = [f for f in filtered if f.priority == priority]
    return sorted(filtered, key=lambda x: x.votes, reverse=True)[:limit]


@router.get("/{feedback_id}", response_model=UserFeedback)
async def get_feedback(feedback_id: str):
    """Get feedback details"""
    for feedback in feedback_db:
        if feedback.id == feedback_id:
            return feedback
    raise HTTPException(status_code=404, detail="Feedback not found")


@router.post("/{feedback_id}/vote")
async def vote_feedback(feedback_id: str, user_id: str):
    """Vote for feedback"""
    for feedback in feedback_db:
        if feedback.id == feedback_id:
            if feedback_id not in feedback_votes:
                feedback_votes[feedback_id] = []
            if user_id not in feedback_votes[feedback_id]:
                feedback_votes[feedback_id].append(user_id)
                feedback.votes += 1
            return {"votes": feedback.votes}
    raise HTTPException(status_code=404, detail="Feedback not found")


@router.put("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    status: FeedbackStatus,
    priority: Optional[FeedbackPriority] = None
):
    """Update feedback status"""
    for feedback in feedback_db:
        if feedback.id == feedback_id:
            feedback.status = status
            if priority:
                feedback.priority = priority
            feedback.updated_at = datetime.now()
            return feedback
    raise HTTPException(status_code=404, detail="Feedback not found")


# ============================================
# Feedback Analytics
# ============================================

@router.get("/analytics/summary")
async def get_feedback_summary():
    """Get feedback analytics summary"""
    total = len(feedback_db)
    
    return {
        "total_feedback": total,
        "by_category": {
            cat.value: len([f for f in feedback_db if f.category == cat])
            for cat in FeedbackCategory
        },
        "by_status": {
            status.value: len([f for f in feedback_db if f.status == status])
            for status in FeedbackStatus
        },
        "by_priority": {
            priority.value: len([f for f in feedback_db if f.priority == priority])
            for priority in FeedbackPriority
        },
        "average_rating": sum(f.rating for f in feedback_db if f.rating) / len([f for f in feedback_db if f.rating]) if any(f.rating for f in feedback_db) else 0,
        "top_voted": [
            {"id": f.id, "title": f.title, "votes": f.votes}
            for f in sorted(feedback_db, key=lambda x: x.votes, reverse=True)[:5]
        ]
    }


@router.get("/analytics/trends")
async def get_feedback_trends():
    """Get feedback trends over time"""
    now = datetime.now()
    
    return {
        "daily": {
            "today": len([f for f in feedback_db if f.created_at.date() == now.date()]),
            "yesterday": len([f for f in feedback_db if f.created_at.date() == (now - timedelta(days=1)).date()]),
            "last_7_days": len([f for f in feedback_db if f.created_at >= now - timedelta(days=7)])
        },
        "satisfaction_trend": [
            {"date": (now - timedelta(days=i)).strftime("%Y-%m-%d"), "rating": 4.2 - (i * 0.05)}
            for i in range(7)
        ],
        "category_trend": {
            "feature_request": "increasing",
            "bug_report": "decreasing",
            "usability": "stable"
        }
    }


# ============================================
# Improvements Management
# ============================================

@router.post("/improvements", response_model=Improvement)
async def create_improvement(
    title: str,
    description: str,
    category: FeedbackCategory,
    priority: FeedbackPriority,
    estimated_effort: str,
    related_feedback_ids: List[str] = [],
    target_release: Optional[str] = None
):
    """Create improvement from feedback"""
    improvement = Improvement(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        category=category,
        priority=priority,
        status="planned",
        related_feedback_ids=related_feedback_ids,
        estimated_effort=estimated_effort,
        target_release=target_release,
        created_at=datetime.now()
    )
    improvements_db.append(improvement)
    
    # Update related feedback status
    for fid in related_feedback_ids:
        for feedback in feedback_db:
            if feedback.id == fid:
                feedback.status = FeedbackStatus.PLANNED
    
    return improvement


@router.get("/improvements", response_model=List[Improvement])
async def list_improvements(
    status: Optional[str] = None,
    priority: Optional[FeedbackPriority] = None
):
    """List improvements"""
    filtered = improvements_db
    if status:
        filtered = [i for i in filtered if i.status == status]
    if priority:
        filtered = [i for i in filtered if i.priority == priority]
    return filtered


@router.put("/improvements/{improvement_id}")
async def update_improvement(
    improvement_id: str,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    target_release: Optional[str] = None
):
    """Update improvement"""
    for improvement in improvements_db:
        if improvement.id == improvement_id:
            if status:
                improvement.status = status
                if status == "completed":
                    improvement.completed_at = datetime.now()
                    # Update related feedback
                    for fid in improvement.related_feedback_ids:
                        for feedback in feedback_db:
                            if feedback.id == fid:
                                feedback.status = FeedbackStatus.IMPLEMENTED
            if assigned_to:
                improvement.assigned_to = assigned_to
            if target_release:
                improvement.target_release = target_release
            return improvement
    raise HTTPException(status_code=404, detail="Improvement not found")


# ============================================
# Prioritization
# ============================================

@router.get("/prioritization/matrix")
async def get_prioritization_matrix():
    """Get prioritization matrix (impact vs effort)"""
    return {
        "high_impact_low_effort": [
            f.dict() for f in feedback_db
            if f.priority in [FeedbackPriority.HIGH, FeedbackPriority.CRITICAL] and f.votes > 5
        ][:5],
        "high_impact_high_effort": [
            f.dict() for f in feedback_db
            if f.priority == FeedbackPriority.CRITICAL
        ][:5],
        "low_impact_low_effort": [
            f.dict() for f in feedback_db
            if f.priority == FeedbackPriority.LOW
        ][:5],
        "recommendations": [
            "Focus on high-impact, low-effort items first",
            "Schedule high-impact, high-effort items for next sprint",
            "Consider batching low-impact items"
        ]
    }


@router.get("/roadmap")
async def get_feedback_roadmap():
    """Get improvement roadmap"""
    return {
        "current_sprint": [
            i.dict() for i in improvements_db if i.status == "in_progress"
        ],
        "next_sprint": [
            i.dict() for i in improvements_db if i.status == "planned"
        ][:5],
        "backlog": [
            i.dict() for i in improvements_db if i.status == "backlog"
        ],
        "completed_this_month": [
            i.dict() for i in improvements_db
            if i.completed_at and i.completed_at >= datetime.now() - timedelta(days=30)
        ]
    }
