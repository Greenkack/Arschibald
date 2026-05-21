"""
Notification Database Models

This module defines the database models for the notification system.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class NotificationType(str, enum.Enum):
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


class NotificationChannel(str, enum.Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    DESKTOP = "desktop"
    EMAIL = "email"
    SMS = "sms"


class NotificationPriority(str, enum.Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    type = Column(Enum(NotificationType), nullable=False, default=NotificationType.INFO)
    priority = Column(Enum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Notification metadata
    category = Column(String(100), nullable=True, index=True)
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)
    icon = Column(String(100), nullable=True)
    
    # Delivery channels
    channels = Column(String(255), nullable=False, default="in_app")  # Comma-separated
    
    # Status tracking
    is_read = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Delivery tracking
    sent_in_app = Column(Boolean, default=False)
    sent_desktop = Column(Boolean, default=False)
    sent_email = Column(Boolean, default=False)
    sent_sms = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    actions = relationship("NotificationAction", back_populates="notification", cascade="all, delete-orphan")


class NotificationAction(Base):
    """Notification action model for interactive notifications"""
    __tablename__ = "notification_actions"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # approve, reject, view, dismiss, etc.
    label = Column(String(100), nullable=False)
    url = Column(String(500), nullable=True)
    
    # Action status
    is_executed = Column(Boolean, default=False)
    executed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    notification = relationship("Notification", back_populates="actions")


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Channel preferences
    enable_in_app = Column(Boolean, default=True)
    enable_desktop = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)
    
    # Type preferences (JSON-like string)
    enabled_types = Column(Text, nullable=True)  # JSON array of enabled types
    
    # Quiet hours
    enable_quiet_hours = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)  # HH:MM format
    
    # Frequency settings
    digest_mode = Column(Boolean, default=False)
    digest_frequency = Column(String(20), nullable=True)  # daily, weekly
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class NotificationTemplate(Base):
    """Notification templates for consistent messaging"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    template_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    
    # Template settings
    default_channels = Column(String(255), nullable=False, default="in_app")
    icon = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
