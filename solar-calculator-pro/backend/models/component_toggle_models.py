"""
Component Toggle Database Models

Database models for component-level feature toggles.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from backend.core.database import Base
import enum


class ComponentToggleCategory(str, enum.Enum):
    """Categories of component toggles"""
    CHART = "chart"
    FORM_FIELD = "form_field"
    CALCULATION_OPTION = "calculation_option"
    EXPORT_FORMAT = "export_format"
    UI_THEME = "ui_theme"
    LANGUAGE = "language"


class ComponentToggleType(str, enum.Enum):
    """Types of toggles"""
    VISIBILITY = "visibility"  # Show/hide component
    FEATURE = "feature"  # Enable/disable feature
    PERMISSION = "permission"  # Access control


class ComponentToggle(Base):
    """Component toggle model"""
    __tablename__ = "component_toggles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Toggle identification
    category = Column(SQLEnum(ComponentToggleCategory), nullable=False, index=True)
    component_key = Column(String(255), nullable=False, index=True)
    component_name = Column(String(255), nullable=False)
    
    # Toggle state
    enabled = Column(Boolean, default=True, nullable=False)
    toggle_type = Column(SQLEnum(ComponentToggleType), default=ComponentToggleType.FEATURE)
    
    # User association (None = global toggle)
    user_id = Column(Integer, nullable=True, index=True)
    
    # Additional metadata
    metadata = Column(JSON, default={})
    description = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ComponentToggle {self.category}:{self.component_key} enabled={self.enabled}>"
