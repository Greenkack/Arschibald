"""
Database Migration: Add Document Management Tables

Creates tables for document storage, versioning, templates, and sharing.
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from datetime import datetime
import enum


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


def upgrade(engine):
    """Create document management tables"""
    metadata = MetaData()

    # Documents table
    documents = Table(
        'documents',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(255), nullable=False, index=True),
        Column('description', Text, nullable=True),
        Column('type', Enum(DocumentType), nullable=False, index=True),
        Column('status', Enum(DocumentStatus), nullable=False, index=True),
        Column('file_name', String(255), nullable=False),
        Column('file_path', String(500), nullable=False),
        Column('file_size', Integer, nullable=False),
        Column('mime_type', String(100), nullable=False),
        Column('version', Integer, nullable=False, default=1),
        Column('is_latest_version', Boolean, nullable=False, default=True, index=True),
        Column('parent_document_id', Integer, ForeignKey('documents.id'), nullable=True),
        Column('tags', JSON, nullable=True),
        Column('metadata', JSON, nullable=True),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('updated_by', Integer, ForeignKey('users.id'), nullable=True),
        Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
        Column('updated_at', DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Document templates table
    document_templates = Table(
        'document_templates',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(255), nullable=False, index=True),
        Column('description', Text, nullable=True),
        Column('type', Enum(DocumentType), nullable=False),
        Column('template_path', String(500), nullable=False),
        Column('template_variables', JSON, nullable=True),
        Column('category', String(100), nullable=True, index=True),
        Column('tags', JSON, nullable=True),
        Column('is_active', Boolean, nullable=False, default=True, index=True),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
        Column('updated_at', DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Document shares table
    document_shares = Table(
        'document_shares',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('document_id', Integer, ForeignKey('documents.id'), nullable=False, index=True),
        Column('shared_with_user_id', Integer, ForeignKey('users.id'), nullable=True),
        Column('shared_with_email', String(255), nullable=True),
        Column('can_view', Boolean, nullable=False, default=True),
        Column('can_edit', Boolean, nullable=False, default=False),
        Column('can_delete', Boolean, nullable=False, default=False),
        Column('can_share', Boolean, nullable=False, default=False),
        Column('access_token', String(255), unique=True, nullable=True, index=True),
        Column('expires_at', DateTime, nullable=True),
        Column('shared_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('message', Text, nullable=True),
        Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
        Column('accessed_at', DateTime, nullable=True)
    )

    # Create all tables
    metadata.create_all(engine)
    print("✓ Created documents table")
    print("✓ Created document_templates table")
    print("✓ Created document_shares table")


def downgrade(engine):
    """Drop document management tables"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    tables_to_drop = ['document_shares', 'document_templates', 'documents']
    
    for table_name in tables_to_drop:
        if table_name in metadata.tables:
            metadata.tables[table_name].drop(engine)
            print(f"✓ Dropped {table_name} table")


if __name__ == "__main__":
    # Example usage
    from backend.core.database import engine
    
    print("Running document management migration...")
    upgrade(engine)
    print("Migration completed successfully!")
