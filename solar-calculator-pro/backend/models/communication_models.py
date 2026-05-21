"""
Communication Database Models

Database models for customer communication system including emails, SMS,
templates, scheduling, tracking, and analytics.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class CommunicationType(enum.Enum):
    """Communication type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    MEETING = "meeting"
    NOTE = "note"


class CommunicationStatus(enum.Enum):
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


class TemplateType(enum.Enum):
    """Template type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    DOCUMENT = "document"


class Communication(Base):
    """Communication record model"""
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Communication details
    type = Column(SQLEnum(CommunicationType), nullable=False, index=True)
    status = Column(SQLEnum(CommunicationStatus), default=CommunicationStatus.DRAFT, index=True)
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    
    # Recipients
    to_addresses = Column(JSON)  # List of email addresses or phone numbers
    cc_addresses = Column(JSON)  # CC email addresses
    bcc_addresses = Column(JSON)  # BCC email addresses
    
    # Scheduling
    scheduled_at = Column(DateTime, index=True)
    sent_at = Column(DateTime, index=True)
    
    # Tracking
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)
    
    # Metadata
    template_id = Column(Integer, ForeignKey("communication_templates.id"))
    campaign_id = Column(Integer, ForeignKey("communication_campaigns.id"), index=True)
    attachments = Column(JSON)  # List of attachment file paths
    metadata = Column(JSON)  # Additional metadata
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="communications")
    user = relationship("User", back_populates="communications")
    template = relationship("CommunicationTemplate", back_populates="communications")
    campaign = relationship("CommunicationCampaign", back_populates="communications")
    analytics = relationship("CommunicationAnalytics", back_populates="communication", uselist=False)


class CommunicationTemplate(Base):
    """Communication template model"""
    __tablename__ = "communication_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Template details
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    type = Column(SQLEnum(TemplateType), nullable=False, index=True)
    
    # Content
    subject = Column(String(500))  # For email templates
    body = Column(Text, nullable=False)
    
    # Variables
    variables = Column(JSON)  # List of available variables
    
    # Settings
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)
    category = Column(String(100), index=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="communication_templates")
    communications = relationship("Communication", back_populates="template")


class CommunicationCampaign(Base):
    """Communication campaign model"""
    __tablename__ = "communication_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Campaign details
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    type = Column(SQLEnum(CommunicationType), nullable=False, index=True)
    
    # Status
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, active, completed, paused
    
    # Scheduling
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
    
    # Target audience
    target_criteria = Column(JSON)  # Criteria for selecting recipients
    recipient_count = Column(Integer, default=0)
    
    # Template
    template_id = Column(Integer, ForeignKey("communication_templates.id"))
    
    # Statistics
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    replied_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="communication_campaigns")
    template = relationship("CommunicationTemplate")
    communications = relationship("Communication", back_populates="campaign")


class CommunicationSchedule(Base):
    """Communication schedule model"""
    __tablename__ = "communication_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Schedule details
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    type = Column(SQLEnum(CommunicationType), nullable=False, index=True)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, default=1)
    recurrence_days = Column(JSON)  # Days of week/month
    
    # Schedule timing
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, index=True)
    time_of_day = Column(String(10))  # HH:MM format
    
    # Template and recipients
    template_id = Column(Integer, ForeignKey("communication_templates.id"))
    recipient_criteria = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="communication_schedules")
    template = relationship("CommunicationTemplate")


class CommunicationAnalytics(Base):
    """Communication analytics model"""
    __tablename__ = "communication_analytics"

    id = Column(Integer, primary_key=True, index=True)
    communication_id = Column(Integer, ForeignKey("communications.id"), nullable=False, unique=True, index=True)
    
    # Engagement metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    forward_count = Column(Integer, default=0)
    
    # Timing metrics
    time_to_open = Column(Integer)  # Seconds
    time_to_click = Column(Integer)  # Seconds
    time_to_reply = Column(Integer)  # Seconds
    
    # Device and location
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    operating_system = Column(String(100))
    location = Column(String(200))
    ip_address = Column(String(50))
    
    # Link tracking
    links_clicked = Column(JSON)  # List of clicked links with timestamps
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    communication = relationship("Communication", back_populates="analytics")


class EmailConfiguration(Base):
    """Email configuration model"""
    __tablename__ = "email_configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Configuration details
    name = Column(String(200), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # SMTP settings
    smtp_host = Column(String(200), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_username = Column(String(200), nullable=False)
    smtp_password = Column(String(500), nullable=False)  # Encrypted
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    
    # Sender information
    from_email = Column(String(200), nullable=False)
    from_name = Column(String(200))
    reply_to_email = Column(String(200))
    
    # Settings
    is_active = Column(Boolean, default=True, index=True)
    daily_limit = Column(Integer)
    hourly_limit = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="email_configurations")


class SMSConfiguration(Base):
    """SMS configuration model"""
    __tablename__ = "sms_configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Configuration details
    name = Column(String(200), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Provider settings
    provider = Column(String(100), nullable=False)  # twilio, nexmo, etc.
    api_key = Column(String(500), nullable=False)  # Encrypted
    api_secret = Column(String(500))  # Encrypted
    account_sid = Column(String(200))
    
    # Sender information
    from_number = Column(String(20), nullable=False)
    
    # Settings
    is_active = Column(Boolean, default=True, index=True)
    daily_limit = Column(Integer)
    hourly_limit = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sms_configurations")
