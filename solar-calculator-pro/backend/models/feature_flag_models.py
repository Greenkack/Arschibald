"""
Feature Flag Database Models

This module defines the SQLAlchemy models for the feature flag system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base


# Association table for feature flag to user relationship
feature_flag_users = Table(
    'feature_flag_users',
    Base.metadata,
    Column('feature_flag_id', Integer, ForeignKey('feature_flags.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


# Association table for feature flag to role relationship
feature_flag_roles = Table(
    'feature_flag_roles',
    Base.metadata,
    Column('feature_flag_id', Integer, ForeignKey('feature_flags.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class FeatureFlag(Base):
    """
    Feature Flag Model
    
    Represents a feature flag that can be toggled on/off for different users or roles.
    """
    __tablename__ = 'feature_flags'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=False, nullable=False)
    
    # Feature flag type: 'global', 'user', 'role', 'percentage'
    flag_type = Column(String(50), default='global', nullable=False)
    
    # For percentage rollout (0-100)
    rollout_percentage = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    users = relationship('User', secondary=feature_flag_users, back_populates='feature_flags')
    roles = relationship('Role', secondary=feature_flag_roles, back_populates='feature_flags')
    
    def __repr__(self):
        return f"<FeatureFlag(key='{self.key}', enabled={self.enabled})>"


class Role(Base):
    """
    Role Model
    
    Represents a user role for role-based feature access.
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    feature_flags = relationship('FeatureFlag', secondary=feature_flag_roles, back_populates='roles')
    
    def __repr__(self):
        return f"<Role(name='{self.name}')>"
