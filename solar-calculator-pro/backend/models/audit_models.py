"""
Database Audit System Models

This module defines the database models for the audit system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class AuditLog(Base):
    """
    Main audit log table for tracking all database changes.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, READ
    table_name = Column(String(255), nullable=False, index=True)
    record_id = Column(String(255), nullable=True, index=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_timestamp_action', 'timestamp', 'action'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_table_record', 'table_name', 'record_id'),
    )


class DataAccessLog(Base):
    """
    Log table for tracking data access (read operations).
    """
    __tablename__ = "data_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    table_name = Column(String(255), nullable=False, index=True)
    record_id = Column(String(255), nullable=True)
    query_type = Column(String(50), nullable=False)  # SELECT, SEARCH, EXPORT
    query_params = Column(JSON, nullable=True)
    result_count = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="data_access_logs", foreign_keys=[user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_access_timestamp_user', 'timestamp', 'user_id'),
        Index('idx_access_table_timestamp', 'table_name', 'timestamp'),
    )


class UserActionLog(Base):
    """
    Log table for tracking user actions and activities.
    """
    __tablename__ = "user_action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    action_type = Column(String(100), nullable=False, index=True)  # LOGIN, LOGOUT, CALCULATION, PDF_GENERATION, etc.
    action_category = Column(String(50), nullable=False, index=True)  # AUTH, CALCULATION, REPORT, ADMIN, etc.
    action_details = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILURE, ERROR
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="user_action_logs", foreign_keys=[user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_action_timestamp_user', 'timestamp', 'user_id'),
        Index('idx_action_type_timestamp', 'action_type', 'timestamp'),
        Index('idx_action_category_status', 'action_category', 'status'),
    )


class ComplianceLog(Base):
    """
    Log table for compliance and regulatory tracking.
    """
    __tablename__ = "compliance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    compliance_type = Column(String(100), nullable=False, index=True)  # GDPR, DATA_RETENTION, SECURITY, etc.
    event_type = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    affected_data = Column(JSON, nullable=True)
    compliance_status = Column(String(50), nullable=False)  # COMPLIANT, NON_COMPLIANT, PENDING
    details = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="compliance_logs", foreign_keys=[user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_compliance_type_timestamp', 'compliance_type', 'timestamp'),
        Index('idx_compliance_status', 'compliance_status'),
    )


class AuditReport(Base):
    """
    Table for storing generated audit reports.
    """
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(100), nullable=False, index=True)  # AUDIT, ACCESS, COMPLIANCE, SECURITY
    report_name = Column(String(255), nullable=False)
    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)
    filters = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(20), nullable=True)  # PDF, EXCEL, CSV, JSON
    status = Column(String(50), nullable=False)  # GENERATING, COMPLETED, FAILED
    
    # Relationships
    created_by = relationship("User", back_populates="audit_reports", foreign_keys=[created_by_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_report_type_created', 'report_type', 'created_at'),
        Index('idx_report_status', 'status'),
    )
