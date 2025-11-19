"""
PDF Generation Schemas

Pydantic models for PDF generation requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class PDFTemplate(str, Enum):
    """Available PDF templates"""
    MAIN = "main"
    SIMPLE = "simple"
    EXTENDED = "extended"


class PDFGenerationRequest(BaseModel):
    """Request model for PDF generation"""
    
    offer_data: Dict[str, Any] = Field(
        ...,
        description="Offer/project data for PDF generation"
    )
    template: PDFTemplate = Field(
        default=PDFTemplate.MAIN,
        description="Template to use for PDF generation"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached PDF if available"
    )
    store_pdf: bool = Field(
        default=False,
        description="Whether to store the generated PDF"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Filename for stored PDF (if store_pdf is True)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata to store with PDF"
    )
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename if provided"""
        if v is not None:
            # Remove any path separators
            v = v.replace('/', '_').replace('\\', '_')
            # Ensure .pdf extension
            if not v.endswith('.pdf'):
                v += '.pdf'
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "offer_data": {
                    "customer_name": "Max Mustermann",
                    "project_name": "Solar Installation",
                    "system_size": 10.5,
                    "module_count": 30,
                    "total_cost": 25000.00
                },
                "template": "main",
                "use_cache": True,
                "store_pdf": True,
                "filename": "offer_mustermann_2024.pdf",
                "metadata": {
                    "customer_id": 123,
                    "project_id": 456
                }
            }
        }


class PDFPreviewRequest(BaseModel):
    """Request model for PDF preview generation"""
    
    offer_data: Dict[str, Any] = Field(
        ...,
        description="Offer/project data for PDF preview"
    )
    template: PDFTemplate = Field(
        default=PDFTemplate.MAIN,
        description="Template to use for PDF preview"
    )
    page_limit: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of pages to include in preview"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "offer_data": {
                    "customer_name": "Max Mustermann",
                    "project_name": "Solar Installation"
                },
                "template": "main",
                "page_limit": 3
            }
        }


class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation"""
    
    pdf_base64: str = Field(
        ...,
        description="Base64-encoded PDF content"
    )
    size_bytes: int = Field(
        ...,
        description="Size of PDF in bytes"
    )
    template: str = Field(
        ...,
        description="Template used for generation"
    )
    cached: bool = Field(
        ...,
        description="Whether PDF was retrieved from cache"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when PDF was generated"
    )
    stored_path: Optional[str] = Field(
        default=None,
        description="File path if PDF was stored"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "pdf_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0NvdW50IDEvS2lkc1szIDAgUl0+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDYxMiA3OTJdL1BhcmVudCAyIDAgUi9SZXNvdXJjZXM8PC9Gb250PDwvRjEgNCAwIFI+Pj4+L0NvbnRlbnRzIDUgMCBSPj4KZW5kb2JqCjQgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCjUgMCBvYmoKPDwvTGVuZ3RoIDQ0Pj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoxMCA3MDAgVGQKKEhlbGxvIFdvcmxkKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY0IDAwMDAwIG4gCjAwMDAwMDAxMjEgMDAwMDAgbiAKMDAwMDAwMDIyNyAwMDAwMCBuIAowMDAwMDAwMjk1IDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA2L1Jvb3QgMSAwIFI+PgpzdGFydHhyZWYKMzg5CiUlRU9GCg==",
                "size_bytes": 1024,
                "template": "main",
                "cached": False,
                "generated_at": "2024-01-15T10:30:00",
                "stored_path": "/path/to/stored/pdf.pdf"
            }
        }


class PDFStorageInfo(BaseModel):
    """Information about a stored PDF"""
    
    filename: str = Field(..., description="PDF filename")
    size_bytes: int = Field(..., description="File size in bytes")
    created_at: str = Field(..., description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "20240115_103000_offer_mustermann.pdf",
                "size_bytes": 524288,
                "created_at": "2024-01-15T10:30:00",
                "metadata": {
                    "customer_id": 123,
                    "project_id": 456,
                    "customer_name": "Max Mustermann"
                }
            }
        }


class PDFListResponse(BaseModel):
    """Response model for listing stored PDFs"""
    
    pdfs: List[PDFStorageInfo] = Field(
        ...,
        description="List of stored PDFs"
    )
    total_count: int = Field(
        ...,
        description="Total number of stored PDFs"
    )
    total_size_bytes: int = Field(
        ...,
        description="Total size of all PDFs in bytes"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "pdfs": [
                    {
                        "filename": "20240115_103000_offer_mustermann.pdf",
                        "size_bytes": 524288,
                        "created_at": "2024-01-15T10:30:00"
                    }
                ],
                "total_count": 1,
                "total_size_bytes": 524288
            }
        }


class PDFTemplateInfo(BaseModel):
    """Information about a PDF template"""
    
    name: str = Field(..., description="Template identifier")
    display_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "main",
                "display_name": "Main Template",
                "description": "Full-featured PDF with all sections and visualizations"
            }
        }


class PDFTemplatesResponse(BaseModel):
    """Response model for available templates"""
    
    templates: List[PDFTemplateInfo] = Field(
        ...,
        description="List of available templates"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "templates": [
                    {
                        "name": "main",
                        "display_name": "Main Template",
                        "description": "Full-featured PDF with all sections"
                    },
                    {
                        "name": "simple",
                        "display_name": "Simple Template",
                        "description": "Simplified PDF with essential information"
                    }
                ]
            }
        }


class PDFCacheStats(BaseModel):
    """Cache statistics"""
    
    cached_items: int = Field(..., description="Number of cached PDFs")
    total_size_bytes: int = Field(..., description="Total cache size in bytes")
    total_size_mb: float = Field(..., description="Total cache size in MB")
    cache_ttl_seconds: int = Field(..., description="Cache TTL in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "cached_items": 5,
                "total_size_bytes": 2621440,
                "total_size_mb": 2.5,
                "cache_ttl_seconds": 600
            }
        }


class PDFDeleteResponse(BaseModel):
    """Response model for PDF deletion"""
    
    success: bool = Field(..., description="Whether deletion was successful")
    filename: str = Field(..., description="Filename that was deleted")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "filename": "offer_mustermann.pdf",
                "message": "PDF deleted successfully"
            }
        }
