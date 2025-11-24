"""
Sales Pipeline Database Models
Implements customizable pipeline stages, opportunities, and analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class PipelineStageType(str, enum.Enum):
    """Pipeline stage types"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityStatus(str, enum.Enum):
    """Opportunity status"""
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


class PipelineStage(Base):
    """Pipeline stage configuration"""
    __tablename__ = "pipeline_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stage_type = Column(SQLEnum(PipelineStageType), nullable=False)
    order_index = Column(Integer, nullable=False)
    probability = Column(Float, default=0.0)  # Win probability percentage
    color = Column(String(20), default="#3B82F6")
    icon = Column(String(50))
    description = Column(Text)
    
    # Automation settings
    auto_actions = Column(JSON)  # Automated actions when entering stage
    required_fields = Column(JSON)  # Required fields to move to this stage
    time_limit_days = Column(Integer)  # Expected time in stage
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System stages cannot be deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="stage")


class Opportunity(Base):
    """Sales opportunity"""
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Customer information
    customer_id = Column(Integer, ForeignKey("customers.id"))
    contact_name = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(50))
    
    # Pipeline information
    stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=False)
    status = Column(SQLEnum(OpportunityStatus), default=OpportunityStatus.ACTIVE)
    
    # Financial information
    estimated_value = Column(Float, nullable=False)
    actual_value = Column(Float)
    currency = Column(String(3), default="EUR")
    probability = Column(Float)  # Override stage probability if needed
    weighted_value = Column(Float)  # estimated_value * probability
    
    # Dates
    expected_close_date = Column(DateTime)
    actual_close_date = Column(DateTime)
    stage_entered_at = Column(DateTime, default=datetime.utcnow)
    
    # Assignment
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    
    # Source tracking
    source = Column(String(100))  # web, referral, cold_call, etc.
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Additional data
    custom_fields = Column(JSON)
    tags = Column(JSON)
    
    # Win/Loss analysis
    win_reason = Column(Text)
    loss_reason = Column(Text)
    competitor = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stage = relationship("PipelineStage", back_populates="opportunities")
    activities = relationship("OpportunityActivity", back_populates="opportunity", cascade="all, delete-orphan")
    stage_history = relationship("OpportunityStageHistory", back_populates="opportunity", cascade="all, delete-orphan")
    products = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunityActivity(Base):
    """Activity log for opportunities"""
    __tablename__ = "opportunity_activities"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    
    activity_type = Column(String(50), nullable=False)  # call, email, meeting, note, etc.
    subject = Column(String(200))
    description = Column(Text)
    
    # Scheduling
    scheduled_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Assignment
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="activities")


class OpportunityStageHistory(Base):
    """Track stage changes for opportunities"""
    __tablename__ = "opportunity_stage_history"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    
    from_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"))
    to_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=False)
    
    days_in_previous_stage = Column(Integer)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="stage_history")


class OpportunityProduct(Base):
    """Products associated with opportunities"""
    __tablename__ = "opportunity_products"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="products")


class PipelineForecast(Base):
    """Pipeline forecasting data"""
    __tablename__ = "pipeline_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    
    forecast_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Forecast metrics
    total_opportunities = Column(Integer)
    total_value = Column(Float)
    weighted_value = Column(Float)
    expected_wins = Column(Integer)
    expected_revenue = Column(Float)
    
    # By stage
    stage_breakdown = Column(JSON)
    
    # By owner
    owner_breakdown = Column(JSON)
    
    # Confidence
    confidence_level = Column(Float)  # 0-100
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PipelineAutomation(Base):
    """Automation rules for pipeline"""
    __tablename__ = "pipeline_automations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Trigger
    trigger_type = Column(String(50), nullable=False)  # stage_change, time_based, value_change
    trigger_config = Column(JSON)
    
    # Conditions
    conditions = Column(JSON)
    
    # Actions
    actions = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
