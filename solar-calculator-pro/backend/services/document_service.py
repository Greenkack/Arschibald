"""
Document Management Service

Provides comprehensive document management functionality including storage,
versioning, templates, generation, sharing, and search.
"""

import os
import shutil
import secrets
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.document_models import (
    Document, DocumentTemplate, DocumentShare,
    DocumentType, DocumentStatus
)
from backend.models.document_schemas import (
    DocumentCreate, DocumentUpdate, DocumentSearchRequest,
    DocumentTemplateCreate, DocumentTemplateUpdate,
    DocumentShareCreate, DocumentGenerateRequest
)


class DocumentService:
    """Service for document management operations"""

    def __init__(self, db: Session, storage_path: str = "storage/documents"):
        """
        Initialize document service
        
        Args:
            db: Database session
            storage_path: Base path for document storage
        """
        self.db = db
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    # Document CRUD Operations

    def create_document(
        self,
        document_data: DocumentCreate,
        file_content: BinaryIO,
        user_id: int
    ) -> Document:
        """
        Create a new document
        
        Args:
            document_data: Document creation data
            file_content: File content stream
            user_id: ID of user creating the document
            
        Returns:
            Created document
        """
        # Generate unique file path
        file_path = self._generate_file_path(document_data.file_name)
        
        # Save file to storage
        full_path = os.path.join(self.storage_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_content, f)
        
        # Create document record
        document = Document(
            name=document_data.name,
            description=document_data.description,
            type=document_data.type,
            status=DocumentStatus.DRAFT,
            file_name=document_data.file_name,
            file_path=file_path,
            file_size=document_data.file_size,
            mime_type=document_data.mime_type,
            tags=document_data.tags,
            metadata=document_data.metadata,
            created_by=user_id,
            version=1,
            is_latest_version=True
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(
            Document.id == document_id,
            Document.status != DocumentStatus.DELETED
        ).first()

    def update_document(
        self,
        document_id: int,
        document_data: DocumentUpdate,
        user_id: int
    ) -> Optional[Document]:
        """
        Update document metadata
        
        Args:
            document_id: Document ID
            document_data: Update data
            user_id: ID of user updating the document
            
        Returns:
            Updated document or None if not found
        """
        document = self.get_document(document_id)
        if not document:
            return None
        
        # Update fields
        update_data = document_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_by = user_id
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def delete_document(self, document_id: int, user_id: int) -> bool:
        """
        Soft delete a document
        
        Args:
            document_id: Document ID
            user_id: ID of user deleting the document
            
        Returns:
            True if deleted, False if not found
        """
        document = self.get_document(document_id)
        if not document:
            return False
        
        document.status = DocumentStatus.DELETED
        document.updated_by = user_id
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    # Document Versioning

    def create_version(
        self,
        document_id: int,
        file_content: BinaryIO,
        user_id: int
    ) -> Optional[Document]:
        """
        Create a new version of a document
        
        Args:
            document_id: Original document ID
            file_content: New file content
            user_id: ID of user creating the version
            
        Returns:
            New document version or None if original not found
        """
        original = self.get_document(document_id)
        if not original:
            return None
        
        # Mark current version as not latest
        original.is_latest_version = False
        
        # Generate new file path
        file_path = self._generate_file_path(original.file_name)
        
        # Save new file
        full_path = os.path.join(self.storage_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            file_size = 0
            for chunk in iter(lambda: file_content.read(8192), b''):
                f.write(chunk)
                file_size += len(chunk)
        
        # Create new version
        new_version = Document(
            name=original.name,
            description=original.description,
            type=original.type,
            status=original.status,
            file_name=original.file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=original.mime_type,
            tags=original.tags,
            metadata=original.metadata,
            created_by=user_id,
            version=original.version + 1,
            is_latest_version=True,
            parent_document_id=original.parent_document_id or original.id
        )
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version

    def get_versions(self, document_id: int) -> List[Document]:
        """Get all versions of a document"""
        document = self.get_document(document_id)
        if not document:
            return []
        
        parent_id = document.parent_document_id or document.id
        
        return self.db.query(Document).filter(
            or_(
                Document.id == parent_id,
                Document.parent_document_id == parent_id
            ),
            Document.status != DocumentStatus.DELETED
        ).order_by(Document.version.desc()).all()

    # Document Templates

    def create_template(
        self,
        template_data: DocumentTemplateCreate,
        user_id: int
    ) -> DocumentTemplate:
        """Create a new document template"""
        template = DocumentTemplate(
            name=template_data.name,
            description=template_data.description,
            type=template_data.type,
            template_path=template_data.template_path,
            template_variables=template_data.template_variables,
            category=template_data.category,
            tags=template_data.tags,
            created_by=user_id
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template

    def get_template(self, template_id: int) -> Optional[DocumentTemplate]:
        """Get template by ID"""
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.id == template_id,
            DocumentTemplate.is_active == True
        ).first()

    def list_templates(
        self,
        type: Optional[DocumentType] = None,
        category: Optional[str] = None
    ) -> List[DocumentTemplate]:
        """List available templates"""
        query = self.db.query(DocumentTemplate).filter(
            DocumentTemplate.is_active == True
        )
        
        if type:
            query = query.filter(DocumentTemplate.type == type)
        if category:
            query = query.filter(DocumentTemplate.category == category)
        
        return query.order_by(DocumentTemplate.name).all()

    def update_template(
        self,
        template_id: int,
        template_data: DocumentTemplateUpdate
    ) -> Optional[DocumentTemplate]:
        """Update template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(template)
        
        return template

    # Document Generation

    def generate_from_template(
        self,
        request: DocumentGenerateRequest,
        user_id: int
    ) -> Optional[Document]:
        """
        Generate a document from a template
        
        Args:
            request: Generation request with template ID and variables
            user_id: ID of user generating the document
            
        Returns:
            Generated document or None if template not found
        """
        template = self.get_template(request.template_id)
        if not template:
            return None
        
        # Load template content
        template_path = os.path.join(self.storage_path, template.template_path)
        if not os.path.exists(template_path):
            return None
        
        # Generate document from template
        # This is a simplified version - actual implementation would use
        # template engines like Jinja2 for text, python-docx for Word, etc.
        output_path = self._generate_file_path(request.output_name)
        full_output_path = os.path.join(self.storage_path, output_path)
        
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        shutil.copy2(template_path, full_output_path)
        
        # Create document record
        file_size = os.path.getsize(full_output_path)
        
        document = Document(
            name=request.output_name,
            description=f"Generated from template: {template.name}",
            type=template.type,
            status=DocumentStatus.ACTIVE,
            file_name=request.output_name,
            file_path=output_path,
            file_size=file_size,
            mime_type=self._get_mime_type(template.type),
            tags=request.tags,
            metadata={"template_id": template.id, "variables": request.variables},
            created_by=user_id,
            version=1,
            is_latest_version=True
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document

    # Document Sharing

    def share_document(
        self,
        share_data: DocumentShareCreate,
        user_id: int
    ) -> Optional[DocumentShare]:
        """
        Share a document with a user or email
        
        Args:
            share_data: Share configuration
            user_id: ID of user sharing the document
            
        Returns:
            Document share record or None if document not found
        """
        document = self.get_document(share_data.document_id)
        if not document:
            return None
        
        # Generate access token
        access_token = secrets.token_urlsafe(32)
        
        share = DocumentShare(
            document_id=share_data.document_id,
            shared_with_user_id=share_data.shared_with_user_id,
            shared_with_email=share_data.shared_with_email,
            can_view=share_data.can_view,
            can_edit=share_data.can_edit,
            can_delete=share_data.can_delete,
            can_share=share_data.can_share,
            access_token=access_token,
            expires_at=share_data.expires_at,
            shared_by=user_id,
            message=share_data.message
        )
        
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        
        return share

    def get_shared_documents(self, user_id: int) -> List[Document]:
        """Get documents shared with a user"""
        shares = self.db.query(DocumentShare).filter(
            DocumentShare.shared_with_user_id == user_id,
            or_(
                DocumentShare.expires_at == None,
                DocumentShare.expires_at > datetime.utcnow()
            )
        ).all()
        
        document_ids = [share.document_id for share in shares]
        
        return self.db.query(Document).filter(
            Document.id.in_(document_ids),
            Document.status != DocumentStatus.DELETED
        ).all()

    def revoke_share(self, share_id: int, user_id: int) -> bool:
        """Revoke a document share"""
        share = self.db.query(DocumentShare).filter(
            DocumentShare.id == share_id,
            DocumentShare.shared_by == user_id
        ).first()
        
        if not share:
            return False
        
        self.db.delete(share)
        self.db.commit()
        
        return True

    # Document Search

    def search_documents(
        self,
        search_request: DocumentSearchRequest,
        user_id: int
    ) -> tuple[List[Document], int]:
        """
        Search documents with filters
        
        Args:
            search_request: Search criteria
            user_id: ID of user performing search
            
        Returns:
            Tuple of (documents, total_count)
        """
        query = self.db.query(Document).filter(
            Document.status != DocumentStatus.DELETED,
            Document.created_by == user_id
        )
        
        # Apply filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.filter(
                or_(
                    Document.name.ilike(search_term),
                    Document.description.ilike(search_term)
                )
            )
        
        if search_request.type:
            query = query.filter(Document.type == search_request.type)
        
        if search_request.status:
            query = query.filter(Document.status == search_request.status)
        
        if search_request.tags:
            # Filter by tags (JSON array contains)
            for tag in search_request.tags:
                query = query.filter(Document.tags.contains([tag]))
        
        if search_request.created_after:
            query = query.filter(Document.created_at >= search_request.created_after)
        
        if search_request.created_before:
            query = query.filter(Document.created_at <= search_request.created_before)
        
        if search_request.created_by:
            query = query.filter(Document.created_by == search_request.created_by)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        documents = query.order_by(Document.created_at.desc()).offset(
            search_request.offset
        ).limit(search_request.limit).all()
        
        return documents, total

    # Helper Methods

    def _generate_file_path(self, filename: str) -> str:
        """Generate unique file path for storage"""
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        unique_id = secrets.token_hex(8)
        return f"{timestamp}/{unique_id}_{filename}"

    def _get_mime_type(self, doc_type: DocumentType) -> str:
        """Get MIME type for document type"""
        mime_types = {
            DocumentType.PDF: "application/pdf",
            DocumentType.WORD: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            DocumentType.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            DocumentType.IMAGE: "image/png",
            DocumentType.TEXT: "text/plain",
            DocumentType.OTHER: "application/octet-stream"
        }
        return mime_types.get(doc_type, "application/octet-stream")

    def get_file_path(self, document: Document) -> str:
        """Get full file system path for a document"""
        return os.path.join(self.storage_path, document.file_path)
