"""
Document Management Pydantic Schemas

Provides request/response schemas for document management API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentBase(BaseModel):
    """Base document schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: DocumentType
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    file_name: str
    file_path: str
    file_size: int
    mime_type: str


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    status: DocumentStatus
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    version: int
    is_latest_version: bool
    parent_document_id: Optional[int]
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentVersionResponse(BaseModel):
    """Schema for document version information"""
    id: int
    version: int
    created_at: datetime
    created_by: int
    file_size: int
    is_latest_version: bool

    class Config:
        from_attributes = True


class DocumentTemplateBase(BaseModel):
    """Base document template schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: DocumentType
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    template_variables: List[str] = Field(default_factory=list)


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema for creating a document template"""
    template_path: str


class DocumentTemplateUpdate(BaseModel):
    """Schema for updating a document template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class DocumentTemplateResponse(DocumentTemplateBase):
    """Schema for document template response"""
    id: int
    template_path: str
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentShareBase(BaseModel):
    """Base document share schema"""
    shared_with_user_id: Optional[int] = None
    shared_with_email: Optional[str] = None
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_share: bool = False
    expires_at: Optional[datetime] = None
    message: Optional[str] = None

    @validator('shared_with_user_id', 'shared_with_email')
    def validate_share_target(cls, v, values):
        """Ensure at least one share target is provided"""
        if not v and not values.get('shared_with_email'):
            raise ValueError('Either shared_with_user_id or shared_with_email must be provided')
        return v


class DocumentShareCreate(DocumentShareBase):
    """Schema for creating a document share"""
    document_id: int


class DocumentShareResponse(DocumentShareBase):
    """Schema for document share response"""
    id: int
    document_id: int
    access_token: Optional[str]
    shared_by: int
    created_at: datetime
    accessed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentGenerateRequest(BaseModel):
    """Schema for document generation from template"""
    template_id: int
    output_name: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class DocumentSearchRequest(BaseModel):
    """Schema for document search"""
    query: Optional[str] = None
    type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    created_by: Optional[int] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int
