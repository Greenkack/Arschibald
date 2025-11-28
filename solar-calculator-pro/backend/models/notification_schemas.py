"""
Notification Pydantic Schemas

This module defines the Pydantic schemas for notification API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CALCULATION_COMPLETE = "calculation_complete"
    PDF_GENERATED = "pdf_generated"
    PROJECT_UPDATED = "project_updated"
    SYSTEM_ALERT = "system_alert"
    USER_MENTION = "user_mention"
    TASK_ASSIGNED = "task_assigned"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    DESKTOP = "desktop"
    EMAIL = "email"
    SMS = "sms"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Notification Action Schemas
class NotificationActionBase(BaseModel):
    """Base notification action schema"""
    action_type: str = Field(..., description="Type of action (approve, reject, view, etc.)")
    label: str = Field(..., max_length=100, description="Action button label")
    url: Optional[str] = Field(None, max_length=500, description="Action URL")


class NotificationActionCreate(NotificationActionBase):
    """Schema for creating a notification action"""
    pass


class NotificationActionResponse(NotificationActionBase):
    """Schema for notification action response"""
    id: int
    notification_id: int
    is_executed: bool
    executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationBase(BaseModel):
    """Base notification schema"""
    type: NotificationType = Field(default=NotificationType.INFO)
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    title: str = Field(..., max_length=255, description="Notification title")
    message: str = Field(..., description="Notification message")
    category: Optional[str] = Field(None, max_length=100, description="Notification category")
    action_url: Optional[str] = Field(None, max_length=500, description="Primary action URL")
    action_label: Optional[str] = Field(None, max_length=100, description="Primary action label")
    icon: Optional[str] = Field(None, max_length=100, description="Notification icon")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    user_id: int = Field(..., description="Target user ID")
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.IN_APP], description="Delivery channels")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    actions: Optional[List[NotificationActionCreate]] = Field(None, description="Interactive actions")


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: int
    user_id: int
    channels: str
    is_read: bool
    is_archived: bool
    read_at: Optional[datetime]
    sent_in_app: bool
    sent_desktop: bool
    sent_email: bool
    sent_sms: bool
    created_at: datetime
    expires_at: Optional[datetime]
    actions: List[NotificationActionResponse] = []

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


# Notification Preference Schemas
class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema"""
    enable_in_app: bool = True
    enable_desktop: bool = True
    enable_email: bool = True
    enable_sms: bool = False
    enabled_types: Optional[List[NotificationType]] = None
    enable_quiet_hours: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    digest_mode: bool = False
    digest_frequency: Optional[str] = Field(None, pattern=r"^(daily|weekly)$")


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences"""
    user_id: int


class NotificationPreferenceUpdate(NotificationPreferenceBase):
    """Schema for updating notification preferences"""
    pass


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Notification Template Schemas
class NotificationTemplateBase(BaseModel):
    """Base notification template schema"""
    template_key: str = Field(..., max_length=100, description="Unique template key")
    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = None
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    title_template: str = Field(..., max_length=255, description="Title template with placeholders")
    message_template: str = Field(..., description="Message template with placeholders")
    default_channels: List[NotificationChannel] = Field(default=[NotificationChannel.IN_APP])
    icon: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating a notification template"""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating a notification template"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    title_template: Optional[str] = Field(None, max_length=255)
    message_template: Optional[str] = None
    default_channels: Optional[List[NotificationChannel]] = None
    icon: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema for notification template response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Bulk Operations
class BulkNotificationCreate(BaseModel):
    """Schema for creating notifications in bulk"""
    user_ids: List[int] = Field(..., description="List of target user IDs")
    notification: NotificationBase
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.IN_APP])


class BulkMarkReadRequest(BaseModel):
    """Schema for marking multiple notifications as read"""
    notification_ids: List[int] = Field(..., description="List of notification IDs to mark as read")


# Statistics
class NotificationStatistics(BaseModel):
    """Schema for notification statistics"""
    total_notifications: int
    unread_count: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    by_channel: Dict[str, int]
    recent_count: int  # Last 24 hours
