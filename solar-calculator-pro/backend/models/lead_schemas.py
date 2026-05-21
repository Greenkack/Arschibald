"""
Lead Management Pydantic Schemas
Request/Response models for lead management API
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LeadStatusEnum(str, Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    NURTURING = "nurturing"


class LeadSourceEnum(str, Enum):
    """Lead source enumeration"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    PHONE = "phone"
    EVENT = "event"
    PARTNER = "partner"
    ADVERTISEMENT = "advertisement"
    ORGANIC_SEARCH = "organic_search"
    PAID_SEARCH = "paid_search"
    OTHER = "other"


class LeadPriorityEnum(str, Enum):
    """Lead priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Lead Schemas

class LeadBase(BaseModel):
    """Base lead schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=100)
    
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Germany", max_length=100)
    
    source: LeadSourceEnum
    priority: LeadPriorityEnum = LeadPriorityEnum.MEDIUM
    
    interested_in: Optional[List[str]] = None
    estimated_value: float = Field(default=0.0, ge=0)
    estimated_close_date: Optional[datetime] = None
    
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead"""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=100)
    
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    status: Optional[LeadStatusEnum] = None
    source: Optional[LeadSourceEnum] = None
    priority: Optional[LeadPriorityEnum] = None
    
    interested_in: Optional[List[str]] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    estimated_close_date: Optional[datetime] = None
    
    next_follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response"""
    id: int
    status: LeadStatusEnum
    score: int
    assigned_to_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    
    first_contact_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None
    contact_count: int
    
    converted: bool
    converted_at: Optional[datetime] = None
    converted_to_customer_id: Optional[int] = None
    
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for paginated lead list"""
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Lead Activity Schemas

class LeadActivityBase(BaseModel):
    """Base lead activity schema"""
    activity_type: str = Field(..., max_length=50)
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class LeadActivityCreate(LeadActivityBase):
    """Schema for creating a lead activity"""
    lead_id: int


class LeadActivityUpdate(BaseModel):
    """Schema for updating a lead activity"""
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class LeadActivityResponse(LeadActivityBase):
    """Schema for lead activity response"""
    id: int
    lead_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    created_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Lead Scoring Schemas

class LeadScoringRuleBase(BaseModel):
    """Base lead scoring rule schema"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    field: str = Field(..., max_length=100)
    operator: str = Field(..., max_length=20)
    value: Optional[str] = Field(None, max_length=255)
    points: int
    active: bool = True
    priority: int = 0


class LeadScoringRuleCreate(LeadScoringRuleBase):
    """Schema for creating a lead scoring rule"""
    pass


class LeadScoringRuleUpdate(BaseModel):
    """Schema for updating a lead scoring rule"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    field: Optional[str] = Field(None, max_length=100)
    operator: Optional[str] = Field(None, max_length=20)
    value: Optional[str] = Field(None, max_length=255)
    points: Optional[int] = None
    active: Optional[bool] = None
    priority: Optional[int] = None


class LeadScoringRuleResponse(LeadScoringRuleBase):
    """Schema for lead scoring rule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadScoreBreakdown(BaseModel):
    """Schema for lead score breakdown"""
    total_score: int
    rules_applied: List[Dict[str, Any]]
    demographic_score: int
    behavioral_score: int
    engagement_score: int


# Lead Assignment Schemas

class LeadAssignmentRuleBase(BaseModel):
    """Base lead assignment rule schema"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    conditions: Dict[str, Any]
    assign_to_user_id: Optional[int] = None
    assign_to_team_id: Optional[int] = None
    assignment_method: str = Field(default="direct", max_length=50)
    active: bool = True
    priority: int = 0


class LeadAssignmentRuleCreate(LeadAssignmentRuleBase):
    """Schema for creating a lead assignment rule"""
    pass


class LeadAssignmentRuleUpdate(BaseModel):
    """Schema for updating a lead assignment rule"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    assign_to_user_id: Optional[int] = None
    assign_to_team_id: Optional[int] = None
    assignment_method: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None
    priority: Optional[int] = None


class LeadAssignmentRuleResponse(LeadAssignmentRuleBase):
    """Schema for lead assignment rule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadAssignRequest(BaseModel):
    """Schema for manual lead assignment"""
    lead_id: int
    assign_to_user_id: int


# Lead Nurturing Schemas

class LeadNurturingCampaignBase(BaseModel):
    """Base lead nurturing campaign schema"""
    campaign_name: str = Field(..., max_length=255)
    campaign_type: Optional[str] = Field(None, max_length=50)
    total_steps: Optional[int] = Field(None, ge=1)


class LeadNurturingCampaignCreate(LeadNurturingCampaignBase):
    """Schema for creating a lead nurturing campaign"""
    lead_id: int


class LeadNurturingCampaignUpdate(BaseModel):
    """Schema for updating a lead nurturing campaign"""
    status: Optional[str] = Field(None, max_length=50)
    current_step: Optional[int] = Field(None, ge=1)


class LeadNurturingCampaignResponse(LeadNurturingCampaignBase):
    """Schema for lead nurturing campaign response"""
    id: int
    lead_id: int
    status: str
    current_step: int
    started_at: datetime
    last_action_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Lead Analytics Schemas

class LeadSourceAnalyticsResponse(BaseModel):
    """Schema for lead source analytics"""
    source: LeadSourceEnum
    source_detail: Optional[str] = None
    period_start: datetime
    period_end: datetime
    leads_generated: int
    leads_qualified: int
    leads_converted: int
    total_value: float
    average_score: float
    average_conversion_time_days: float
    cost: float
    cost_per_lead: float
    roi: float
    
    class Config:
        from_attributes = True


class LeadConversionTrackingResponse(BaseModel):
    """Schema for lead conversion tracking"""
    lead_id: int
    lead_name: str
    source: LeadSourceEnum
    created_at: datetime
    first_contact_date: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    conversion_time_days: Optional[float] = None
    estimated_value: float
    actual_value: Optional[float] = None
    status: LeadStatusEnum


class LeadDashboardMetrics(BaseModel):
    """Schema for lead dashboard metrics"""
    total_leads: int
    new_leads: int
    qualified_leads: int
    converted_leads: int
    conversion_rate: float
    average_score: float
    average_conversion_time_days: float
    total_estimated_value: float
    leads_by_source: Dict[str, int]
    leads_by_status: Dict[str, int]
    leads_by_priority: Dict[str, int]
