"""
Lead Management Database Models
Implements lead tracking, scoring, and lifecycle management
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class LeadStatus(str, enum.Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    NURTURING = "nurturing"


class LeadSource(str, enum.Enum):
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


class LeadPriority(str, enum.Enum):
    """Lead priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Lead(Base):
    """Lead model for CRM system"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50))
    company = Column(String(255))
    job_title = Column(String(100))
    
    # Address
    street = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Germany")
    
    # Lead Details
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, index=True)
    source = Column(SQLEnum(LeadSource), nullable=False, index=True)
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.MEDIUM)
    
    # Scoring
    score = Column(Integer, default=0, index=True)
    score_breakdown = Column(Text)  # JSON string with scoring details
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", back_populates="assigned_leads")
    assigned_at = Column(DateTime, nullable=True)
    
    # Interest
    interested_in = Column(Text)  # JSON array of products/services
    estimated_value = Column(Float, default=0.0)
    estimated_close_date = Column(DateTime, nullable=True)
    
    # Tracking
    first_contact_date = Column(DateTime, nullable=True)
    last_contact_date = Column(DateTime, nullable=True)
    next_follow_up_date = Column(DateTime, nullable=True)
    contact_count = Column(Integer, default=0)
    
    # Conversion
    converted = Column(Boolean, default=False, index=True)
    converted_at = Column(DateTime, nullable=True)
    converted_to_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    nurturing_campaigns = relationship("LeadNurturingCampaign", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead {self.first_name} {self.last_name} ({self.email})>"


class LeadActivity(Base):
    """Lead activity tracking"""
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False)  # call, email, meeting, note, etc.
    subject = Column(String(255))
    description = Column(Text)
    outcome = Column(String(100))
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")
    
    def __repr__(self):
        return f"<LeadActivity {self.activity_type} for Lead {self.lead_id}>"


class LeadScoringRule(Base):
    """Lead scoring rules configuration"""
    __tablename__ = "lead_scoring_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # demographic, behavioral, engagement
    
    # Scoring
    field = Column(String(100), nullable=False)  # Field to evaluate
    operator = Column(String(20), nullable=False)  # equals, contains, greater_than, etc.
    value = Column(String(255))  # Value to compare
    points = Column(Integer, nullable=False)  # Points to add/subtract
    
    # Status
    active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeadScoringRule {self.name}>"


class LeadAssignmentRule(Base):
    """Lead assignment rules configuration"""
    __tablename__ = "lead_assignment_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Conditions
    conditions = Column(Text, nullable=False)  # JSON string with conditions
    
    # Assignment
    assign_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assign_to_team_id = Column(Integer, nullable=True)  # Future: team assignment
    assignment_method = Column(String(50), default="direct")  # direct, round_robin, load_balanced
    
    # Status
    active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeadAssignmentRule {self.name}>"


class LeadNurturingCampaign(Base):
    """Lead nurturing campaign tracking"""
    __tablename__ = "lead_nurturing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    
    # Campaign Details
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(String(50))  # email_sequence, drip_campaign, etc.
    
    # Status
    status = Column(String(50), default="active")  # active, paused, completed, cancelled
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer)
    
    # Tracking
    started_at = Column(DateTime, default=datetime.utcnow)
    last_action_at = Column(DateTime, nullable=True)
    next_action_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Engagement
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="nurturing_campaigns")
    
    def __repr__(self):
        return f"<LeadNurturingCampaign {self.campaign_name} for Lead {self.lead_id}>"


class LeadSourceAnalytics(Base):
    """Lead source analytics and tracking"""
    __tablename__ = "lead_source_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Source Details
    source = Column(SQLEnum(LeadSource), nullable=False, index=True)
    source_detail = Column(String(255))  # Specific campaign, ad, etc.
    
    # Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metrics
    leads_generated = Column(Integer, default=0)
    leads_qualified = Column(Integer, default=0)
    leads_converted = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    average_conversion_time_days = Column(Float, default=0.0)
    
    # Cost (optional)
    cost = Column(Float, default=0.0)
    cost_per_lead = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeadSourceAnalytics {self.source} ({self.period_start} - {self.period_end})>"
