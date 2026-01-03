"""
CRM Schemas

Pydantic models for CRM API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# ==================== Customer Schemas ====================

class CustomerBase(BaseModel):
    """Base customer model"""
    first_name: str = Field(..., description="Customer first name")
    last_name: str = Field(..., description="Customer last name")
    company_name: Optional[str] = Field(None, description="Company name")
    email: Optional[str] = Field(None, description="Email address")
    phone_mobile: Optional[str] = Field(None, description="Mobile phone")
    phone_landline: Optional[str] = Field(None, description="Landline phone")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field("Deutschland", description="Country")
    notes: Optional[str] = Field(None, description="Additional notes")


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer (all fields optional)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_landline: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    id: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Schema for customer list response"""
    customers: List[CustomerResponse]
    total: int
    limit: int
    offset: int


# ==================== Offer Tracking Schemas ====================

class OfferStatusUpdate(BaseModel):
    """Schema for updating offer status"""
    new_status: str = Field(..., description="New status (draft, sent, accepted, rejected)")
    offer_sent_date: Optional[str] = None
    offer_accepted_date: Optional[str] = None
    offer_rejected_date: Optional[str] = None
    rejection_reason: Optional[str] = None
    rejection_notes: Optional[str] = None
    offer_value: Optional[float] = Field(None, ge=0)
    offer_version: Optional[int] = Field(None, ge=1)
    
    @validator('new_status')
    def validate_status(cls, v):
        valid_statuses = ['draft', 'sent', 'accepted', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class OfferStatusResponse(BaseModel):
    """Schema for offer status response"""
    id: int
    project_name: str
    offer_status: str
    offer_sent_date: Optional[str] = None
    offer_accepted_date: Optional[str] = None
    offer_rejected_date: Optional[str] = None
    offer_version: int
    offer_value: Optional[float] = None
    rejection_reason: Optional[str] = None
    rejection_notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    follow_up_completed: int
    customer_id: Optional[int] = None


class OfferListResponse(BaseModel):
    """Schema for offer list response"""
    offers: List[OfferStatusResponse]
    total: int


class OfferStatisticsResponse(BaseModel):
    """Schema for offer statistics response"""
    total_offers: int
    draft: int
    sent: int
    accepted: int
    rejected: int
    avg_offer_value: float
    conversion_rate: float
    pending_follow_ups: int


# ==================== Task Management Schemas ====================

class TaskBase(BaseModel):
    """Base task model"""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field("", description="Task description")
    status: Optional[str] = Field("open", description="Task status (open, in_progress, completed)")
    priority: Optional[str] = Field("medium", description="Task priority (low, medium, high)")
    due_date: Optional[date] = Field(None, description="Due date")
    customer_id: Optional[int] = Field(None, description="Associated customer ID")
    project_id: Optional[int] = Field(None, description="Associated project ID")
    lead_id: Optional[int] = Field(None, description="Associated lead ID")
    assigned_to: Optional[str] = Field("", description="Assigned user")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['open', 'in_progress', 'completed']:
            raise ValueError("Status must be one of: open, in_progress, completed")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be one of: low, medium, high")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    customer_id: Optional[int] = None
    project_id: Optional[int] = None
    lead_id: Optional[int] = None
    assigned_to: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['open', 'in_progress', 'completed']:
            raise ValueError("Status must be one of: open, in_progress, completed")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be one of: low, medium, high")
        return v


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response"""
    tasks: List[TaskResponse]
    total: int


class TaskStatisticsResponse(BaseModel):
    """Schema for task statistics response"""
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    overdue: int
    due_today: int
    due_this_week: int


# ==================== Activity/Note Schemas ====================

class ActivityBase(BaseModel):
    """Base activity model"""
    customer_id: int = Field(..., description="Customer ID")
    activity_type: str = Field(..., description="Activity type (note, email, call, appointment, meeting, task, other)")
    title: str = Field(..., description="Activity title")
    content: Optional[str] = Field("", description="Activity content")
    created_by: Optional[str] = Field("System", description="Creator name")
    is_important: Optional[bool] = Field(False, description="Important flag")
    
    @validator('activity_type')
    def validate_activity_type(cls, v):
        valid_types = ['note', 'email', 'call', 'appointment', 'meeting', 'task', 'other']
        if v not in valid_types:
            raise ValueError(f"Activity type must be one of: {', '.join(valid_types)}")
        return v


class ActivityCreate(ActivityBase):
    """Schema for creating a new activity"""
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an activity (all fields optional)"""
    title: Optional[str] = None
    content: Optional[str] = None
    is_important: Optional[bool] = None
    archived: Optional[bool] = None


class ActivityResponse(ActivityBase):
    """Schema for activity response"""
    id: int
    activity_type_display: str
    created_at: str
    archived: bool
    
    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for activity list response"""
    activities: List[ActivityResponse]
    total: int


class ActivityStatisticsResponse(BaseModel):
    """Schema for activity statistics response"""
    total: int
    by_type: Dict[str, int]
    important: int
    last_activity: Optional[str] = None


# ==================== Search and Filter Schemas ====================

class CustomerSearchRequest(BaseModel):
    """Schema for customer search request"""
    search: Optional[str] = Field(None, description="Search term")
    limit: int = Field(100, ge=1, le=1000, description="Results limit")
    offset: int = Field(0, ge=0, description="Results offset")


class TaskFilterRequest(BaseModel):
    """Schema for task filter request"""
    status: Optional[str] = None
    priority: Optional[str] = None
    customer_id: Optional[int] = None
    project_id: Optional[int] = None
    lead_id: Optional[int] = None
    assigned_to: Optional[str] = None
    overdue_only: bool = False
    due_soon_days: Optional[int] = None


class ActivityFilterRequest(BaseModel):
    """Schema for activity filter request"""
    customer_id: int
    activity_type: Optional[str] = None
    include_archived: bool = False
    limit: int = Field(100, ge=1, le=1000)


class ActivitySearchRequest(BaseModel):
    """Schema for activity search request"""
    search_term: str = Field(..., min_length=1)
    customer_id: Optional[int] = None
    activity_type: Optional[str] = None
    limit: int = Field(50, ge=1, le=500)


# ==================== Generic Response Schemas ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class DeleteResponse(BaseModel):
    """Generic delete response"""
    success: bool
    message: str
    deleted_id: int
