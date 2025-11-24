"""
Result History Database Models

Defines database models for storing calculation results history.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class ResultHistory(Base):
    """Calculation result history"""
    __tablename__ = "result_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    
    # Result metadata
    result_type = Column(String(50), nullable=False, index=True)  # solar, heatpump, combined
    result_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Result data
    input_data = Column(JSON, nullable=False)  # Input parameters
    output_data = Column(JSON, nullable=False)  # Calculation results
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("result_history.id"), nullable=True)
    
    # Status
    is_favorite = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="result_history")
    project = relationship("Project", back_populates="result_history")
    children = relationship("ResultHistory", backref="parent", remote_side=[id])
    tags = relationship("ResultTag", back_populates="result", cascade="all, delete-orphan")
    shares = relationship("ResultShare", back_populates="result", cascade="all, delete-orphan")


class ResultTag(Base):
    """Tags for organizing results"""
    __tablename__ = "result_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("result_history.id"), nullable=False, index=True)
    tag_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    result = relationship("ResultHistory", back_populates="tags")


class ResultShare(Base):
    """Shared results with other users"""
    __tablename__ = "result_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("result_history.id"), nullable=False, index=True)
    shared_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Share settings
    share_token = Column(String(255), unique=True, nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Relationships
    result = relationship("ResultHistory", back_populates="shares")
    shared_by = relationship("User", foreign_keys=[shared_by_user_id])
    shared_with = relationship("User", foreign_keys=[shared_with_user_id])


class ResultComparison(Base):
    """Saved result comparisons"""
    __tablename__ = "result_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Comparison metadata
    comparison_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Results being compared
    result_ids = Column(JSON, nullable=False)  # List of result IDs
    
    # Comparison settings
    comparison_type = Column(String(50), nullable=False)  # side-by-side, overlay, difference
    metrics_to_compare = Column(JSON, nullable=True)  # Specific metrics to highlight
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
