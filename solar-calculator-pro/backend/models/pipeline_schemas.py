"""
Sales Pipeline Pydantic Schemas
Request/Response models for pipeline API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PipelineStageTypeEnum(str, Enum):
    """Pipeline stage types"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityStatusEnum(str, Enum):
    """Opportunity status"""
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


# Pipeline Stage Schemas
class PipelineStageBase(BaseModel):
    name: str = Field(..., max_length=100)
    stage_type: PipelineStageTypeEnum
    order_index: int = Field(..., ge=0)
    probability: float = Field(default=0.0, ge=0.0, le=100.0)
    color: str = Field(default="#3B82F6", max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    auto_actions: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    time_limit_days: Optional[int] = Field(None, ge=0)


class PipelineStageCreate(PipelineStageBase):
    pass


class PipelineStageUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    order_index: Optional[int] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0.0, le=100.0)
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    auto_actions: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    time_limit_days: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class PipelineStageResponse(PipelineStageBase):
    id: int
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime
    opportunity_count: Optional[int] = 0
    total_value: Optional[float] = 0.0

    class Config:
        from_attributes = True


# Opportunity Schemas
class OpportunityBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    customer_id: Optional[int] = None
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=50)
    stage_id: int
    estimated_value: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    probability: Optional[float] = Field(None, ge=0.0, le=100.0)
    expected_close_date: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=100)
    campaign_id: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class OpportunityCreate(OpportunityBase):
    owner_id: int
    team_id: Optional[int] = None


class OpportunityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=50)
    stage_id: Optional[int] = None
    estimated_value: Optional[float] = Field(None, gt=0)
    probability: Optional[float] = Field(None, ge=0.0, le=100.0)
    expected_close_date: Optional[datetime] = None
    owner_id: Optional[int] = None
    team_id: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class OpportunityStageChange(BaseModel):
    stage_id: int
    reason: Optional[str] = None


class OpportunityWin(BaseModel):
    actual_value: float = Field(..., gt=0)
    actual_close_date: Optional[datetime] = None
    win_reason: Optional[str] = None


class OpportunityLoss(BaseModel):
    loss_reason: str
    competitor: Optional[str] = Field(None, max_length=100)
    actual_close_date: Optional[datetime] = None


class OpportunityResponse(OpportunityBase):
    id: int
    status: OpportunityStatusEnum
    actual_value: Optional[float] = None
    weighted_value: Optional[float] = None
    actual_close_date: Optional[datetime] = None
    stage_entered_at: datetime
    owner_id: int
    team_id: Optional[int] = None
    win_reason: Optional[str] = None
    loss_reason: Optional[str] = None
    competitor: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    stage_name: Optional[str] = None
    owner_name: Optional[str] = None
    days_in_stage: Optional[int] = None

    class Config:
        from_attributes = True


# Activity Schemas
class OpportunityActivityBase(BaseModel):
    activity_type: str = Field(..., max_length=50)
    subject: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class OpportunityActivityCreate(OpportunityActivityBase):
    opportunity_id: int


class OpportunityActivityResponse(OpportunityActivityBase):
    id: int
    opportunity_id: int
    completed_at: Optional[datetime] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class OpportunityProductBase(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(..., gt=0)
    discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    description: Optional[str] = None


class OpportunityProductCreate(OpportunityProductBase):
    opportunity_id: int

    @validator('total_price', always=True)
    def calculate_total(cls, v, values):
        quantity = values.get('quantity', 1)
        unit_price = values.get('unit_price', 0)
        discount = values.get('discount_percent', 0)
        return quantity * unit_price * (1 - discount / 100)


class OpportunityProductResponse(OpportunityProductBase):
    id: int
    opportunity_id: int
    total_price: float
    created_at: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


# Analytics Schemas
class PipelineAnalytics(BaseModel):
    """Pipeline analytics summary"""
    total_opportunities: int
    total_value: float
    weighted_value: float
    average_deal_size: float
    win_rate: float
    average_sales_cycle_days: float
    
    by_stage: List[Dict[str, Any]]
    by_owner: List[Dict[str, Any]]
    by_source: List[Dict[str, Any]]
    
    trend_data: Dict[str, List[float]]


class WinLossAnalysis(BaseModel):
    """Win/Loss analysis"""
    total_won: int
    total_lost: int
    win_rate: float
    total_won_value: float
    total_lost_value: float
    average_won_deal_size: float
    average_lost_deal_size: float
    
    win_reasons: List[Dict[str, Any]]
    loss_reasons: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    
    by_stage: List[Dict[str, Any]]
    by_source: List[Dict[str, Any]]


class PipelineForecastData(BaseModel):
    """Pipeline forecast"""
    period_start: datetime
    period_end: datetime
    total_opportunities: int
    total_value: float
    weighted_value: float
    expected_wins: int
    expected_revenue: float
    confidence_level: float
    
    by_stage: List[Dict[str, Any]]
    by_owner: List[Dict[str, Any]]
    by_month: List[Dict[str, Any]]


# Automation Schemas
class PipelineAutomationBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    trigger_type: str = Field(..., max_length=50)
    trigger_config: Dict[str, Any]
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: List[Dict[str, Any]]


class PipelineAutomationCreate(PipelineAutomationBase):
    pass


class PipelineAutomationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class PipelineAutomationResponse(PipelineAutomationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        from_attributes = True


# List Response Schemas
class OpportunityListResponse(BaseModel):
    opportunities: List[OpportunityResponse]
    total: int
    page: int
    page_size: int


class PipelineStageListResponse(BaseModel):
    stages: List[PipelineStageResponse]
    total: int
