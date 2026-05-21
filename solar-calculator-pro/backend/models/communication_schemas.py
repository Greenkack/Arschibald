"""
Communication Pydantic Schemas

Request and response schemas for customer communication system.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CommunicationType(str, Enum):
    """Communication type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    MEETING = "meeting"
    NOTE = "note"


class CommunicationStatus(str, Enum):
    """Communication status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class TemplateType(str, Enum):
    """Template type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    DOCUMENT = "document"


# Communication Schemas

class CommunicationBase(BaseModel):
    """Base communication schema"""
    customer_id: int
    type: CommunicationType
    subject: Optional[str] = None
    body: str
    to_addresses: List[str]
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None
    template_id: Optional[int] = None
    campaign_id: Optional[int] = None
    attachments: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CommunicationCreate(CommunicationBase):
    """Schema for creating communication"""
    pass


class CommunicationUpdate(BaseModel):
    """Schema for updating communication"""
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[CommunicationStatus] = None
    scheduled_at: Optional[datetime] = None
    to_addresses: Optional[List[str]] = None
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CommunicationResponse(CommunicationBase):
    """Schema for communication response"""
    id: int
    user_id: int
    status: CommunicationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Template Schemas

class TemplateBase(BaseModel):
    """Base template schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: TemplateType
    subject: Optional[str] = Field(None, max_length=500)
    body: str
    variables: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_default: bool = False


class TemplateCreate(TemplateBase):
    """Schema for creating template"""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating template"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = None
    variables: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response"""
    id: int
    user_id: int
    usage_count: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Campaign Schemas

class CampaignBase(BaseModel):
    """Base campaign schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: CommunicationType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_criteria: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None


class CampaignCreate(CampaignBase):
    """Schema for creating campaign"""
    pass


class CampaignUpdate(BaseModel):
    """Schema for updating campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_criteria: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: int
    user_id: int
    status: str
    recipient_count: int
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    replied_count: int
    bounced_count: int
    failed_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    """Schema for campaign statistics"""
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_replied: int
    total_bounced: int
    total_failed: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    reply_rate: float
    bounce_rate: float


# Schedule Schemas

class ScheduleBase(BaseModel):
    """Base schedule schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: CommunicationType
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_interval: int = 1
    recurrence_days: Optional[List[int]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    time_of_day: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    template_id: Optional[int] = None
    recipient_criteria: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ScheduleCreate(ScheduleBase):
    """Schema for creating schedule"""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating schedule"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    recurrence_interval: Optional[int] = None
    recurrence_days: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    time_of_day: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    template_id: Optional[int] = None
    recipient_criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    """Schema for schedule response"""
    id: int
    user_id: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas

class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    id: int
    communication_id: int
    open_count: int
    click_count: int
    reply_count: int
    forward_count: int
    time_to_open: Optional[int] = None
    time_to_click: Optional[int] = None
    time_to_reply: Optional[int] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    location: Optional[str] = None
    links_clicked: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Configuration Schemas

class EmailConfigBase(BaseModel):
    """Base email configuration schema"""
    name: str = Field(..., min_length=1, max_length=200)
    smtp_host: str = Field(..., min_length=1, max_length=200)
    smtp_port: int = Field(..., ge=1, le=65535)
    smtp_username: str = Field(..., min_length=1, max_length=200)
    smtp_password: str = Field(..., min_length=1, max_length=500)
    use_tls: bool = True
    use_ssl: bool = False
    from_email: EmailStr
    from_name: Optional[str] = Field(None, max_length=200)
    reply_to_email: Optional[EmailStr] = None
    is_default: bool = False
    is_active: bool = True
    daily_limit: Optional[int] = Field(None, ge=0)
    hourly_limit: Optional[int] = Field(None, ge=0)


class EmailConfigCreate(EmailConfigBase):
    """Schema for creating email configuration"""
    pass


class EmailConfigUpdate(BaseModel):
    """Schema for updating email configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    smtp_host: Optional[str] = Field(None, min_length=1, max_length=200)
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_username: Optional[str] = Field(None, min_length=1, max_length=200)
    smtp_password: Optional[str] = Field(None, min_length=1, max_length=500)
    use_tls: Optional[bool] = None
    use_ssl: Optional[bool] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = Field(None, max_length=200)
    reply_to_email: Optional[EmailStr] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    daily_limit: Optional[int] = Field(None, ge=0)
    hourly_limit: Optional[int] = Field(None, ge=0)


class EmailConfigResponse(BaseModel):
    """Schema for email configuration response"""
    id: int
    user_id: int
    name: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    use_tls: bool
    use_ssl: bool
    from_email: str
    from_name: Optional[str] = None
    reply_to_email: Optional[str] = None
    is_default: bool
    is_active: bool
    daily_limit: Optional[int] = None
    hourly_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SMSConfigBase(BaseModel):
    """Base SMS configuration schema"""
    name: str = Field(..., min_length=1, max_length=200)
    provider: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1, max_length=500)
    api_secret: Optional[str] = Field(None, max_length=500)
    account_sid: Optional[str] = Field(None, max_length=200)
    from_number: str = Field(..., min_length=1, max_length=20)
    is_default: bool = False
    is_active: bool = True
    daily_limit: Optional[int] = Field(None, ge=0)
    hourly_limit: Optional[int] = Field(None, ge=0)


class SMSConfigCreate(SMSConfigBase):
    """Schema for creating SMS configuration"""
    pass


class SMSConfigUpdate(BaseModel):
    """Schema for updating SMS configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    provider: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=1, max_length=500)
    api_secret: Optional[str] = Field(None, max_length=500)
    account_sid: Optional[str] = Field(None, max_length=200)
    from_number: Optional[str] = Field(None, min_length=1, max_length=20)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    daily_limit: Optional[int] = Field(None, ge=0)
    hourly_limit: Optional[int] = Field(None, ge=0)


class SMSConfigResponse(BaseModel):
    """Schema for SMS configuration response"""
    id: int
    user_id: int
    name: str
    provider: str
    from_number: str
    is_default: bool
    is_active: bool
    daily_limit: Optional[int] = None
    hourly_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Bulk Operations

class BulkCommunicationCreate(BaseModel):
    """Schema for bulk communication creation"""
    customer_ids: List[int]
    type: CommunicationType
    subject: Optional[str] = None
    body: str
    template_id: Optional[int] = None
    campaign_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    attachments: Optional[List[str]] = None


class BulkCommunicationResponse(BaseModel):
    """Schema for bulk communication response"""
    total: int
    successful: int
    failed: int
    communication_ids: List[int]
    errors: Optional[List[Dict[str, Any]]] = None


# Analytics Summary

class CommunicationAnalyticsSummary(BaseModel):
    """Schema for communication analytics summary"""
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_replied: int
    total_bounced: int
    total_failed: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    reply_rate: float
    bounce_rate: float
    avg_time_to_open: Optional[float] = None
    avg_time_to_click: Optional[float] = None
    avg_time_to_reply: Optional[float] = None
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_date: List[Dict[str, Any]]
