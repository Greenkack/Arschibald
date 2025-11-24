# backend/models/preference_models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class UserPreference(Base):
    """User preference model for storing user-specific settings"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # e.g., 'ui', 'calculation', 'pdf'
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)  # JSON string
    data_type = Column(String(50), nullable=False)  # 'string', 'number', 'boolean', 'object', 'array'
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, category={self.category}, key={self.key})>"


class PreferenceTemplate(Base):
    """Template for default preferences"""
    __tablename__ = "preference_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    preferences = Column(Text, nullable=False)  # JSON string of all preferences
    is_system = Column(Boolean, default=False)  # System templates cannot be deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PreferenceTemplate(name={self.name}, category={self.category})>"


class PreferenceSync(Base):
    """Track preference synchronization across devices"""
    __tablename__ = "preference_syncs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(String(200), nullable=False, index=True)
    device_name = Column(String(200))
    last_sync_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String(50), default='success')  # 'success', 'failed', 'pending'
    sync_data = Column(Text)  # JSON string of synced preferences
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preference_syncs")

    def __repr__(self):
        return f"<PreferenceSync(user_id={self.user_id}, device_id={self.device_id})>"
