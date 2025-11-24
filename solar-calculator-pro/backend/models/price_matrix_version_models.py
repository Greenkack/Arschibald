"""
Price Matrix Version Database Models

This module defines the database models for price matrix versioning system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class PriceMatrixVersion(Base):
    """Price Matrix Version Model"""
    __tablename__ = "price_matrix_versions"

    id = Column(Integer, primary_key=True, index=True)
    matrix_id = Column(Integer, ForeignKey("price_matrices.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Version data
    matrix_data = Column(JSON, nullable=False)  # Complete matrix data snapshot
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Status
    status = Column(String(50), default="draft")  # draft, pending, approved, rejected, active, archived
    is_active = Column(Boolean, default=False)
    
    # Approval workflow
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matrix = relationship("PriceMatrix", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    changes = relationship("PriceMatrixVersionChange", back_populates="version", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PriceMatrixVersion(id={self.id}, version={self.version_number}, status={self.status})>"


class PriceMatrixVersionChange(Base):
    """Price Matrix Version Change Log"""
    __tablename__ = "price_matrix_version_changes"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("price_matrix_versions.id"), nullable=False)
    
    # Change details
    change_type = Column(String(50), nullable=False)  # created, updated, approved, rejected, activated, archived
    field_name = Column(String(255), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_description = Column(Text, nullable=True)
    
    # User and timestamp
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    version = relationship("PriceMatrixVersion", back_populates="changes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<PriceMatrixVersionChange(id={self.id}, type={self.change_type})>"


class PriceMatrixVersionComparison(Base):
    """Price Matrix Version Comparison Results"""
    __tablename__ = "price_matrix_version_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    version_a_id = Column(Integer, ForeignKey("price_matrix_versions.id"), nullable=False)
    version_b_id = Column(Integer, ForeignKey("price_matrix_versions.id"), nullable=False)
    
    # Comparison results
    differences = Column(JSON, nullable=False)  # Detailed differences
    summary = Column(JSON, nullable=True)  # Summary statistics
    
    # Metadata
    compared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    compared_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    version_a = relationship("PriceMatrixVersion", foreign_keys=[version_a_id])
    version_b = relationship("PriceMatrixVersion", foreign_keys=[version_b_id])
    user = relationship("User")
    
    def __repr__(self):
        return f"<PriceMatrixVersionComparison(id={self.id}, v{self.version_a_id} vs v{self.version_b_id})>"
