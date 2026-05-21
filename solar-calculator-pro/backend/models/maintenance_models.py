"""
Database models for system maintenance
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from backend.core.database import Base


class MaintenanceLog(Base):
    """Log of maintenance operations"""
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(100), nullable=False, index=True)
    operation_name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, in_progress
    details = Column(JSON)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    performed_by = Column(String(100), nullable=True)


class SystemDiagnostic(Base):
    """System diagnostic results"""
    __tablename__ = "system_diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # healthy, warning, critical
    metrics = Column(JSON)
    issues = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())


class CacheEntry(Base):
    """Cache management entries"""
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(500), unique=True, nullable=False, index=True)
    cache_type = Column(String(100), nullable=False, index=True)
    size_bytes = Column(Integer, nullable=False)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_valid = Column(Boolean, default=True)


class TempFile(Base):
    """Temporary file tracking"""
    __tablename__ = "temp_files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    should_delete = Column(Boolean, default=False)
    delete_after = Column(DateTime(timezone=True), nullable=True)
