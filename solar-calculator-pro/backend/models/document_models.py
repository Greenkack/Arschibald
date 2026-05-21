"""
Document Management Database Models

Provides SQLAlchemy models for document storage, versioning, and management.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(DocumentType), nullable=False, index=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, index=True)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    is_latest_version = Column(Boolean, default=True, index=True)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Ownership and access
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("Document", backref="parent_document", remote_side=[id])
    shares = relationship("DocumentShare", back_populates="document", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class DocumentTemplate(Base):
    """Document template model"""
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(DocumentType), nullable=False)
    
    # Template content
    template_path = Column(String(500), nullable=False)
    template_variables = Column(JSON, default=list)  # List of variable names
    
    # Metadata
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, index=True)
    
    # Ownership
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


class DocumentShare(Base):
    """Document sharing model"""
    __tablename__ = "document_shares"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_email = Column(String(255), nullable=True)
    
    # Permissions
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # Access control
    access_token = Column(String(255), unique=True, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accessed_at = Column(DateTime, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="shares")
    shared_by_user = relationship("User", foreign_keys=[shared_by])
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id])
