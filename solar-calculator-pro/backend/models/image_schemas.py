# backend/models/image_schemas.py
"""
Pydantic schemas for product image management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ImageVariantSchema(BaseModel):
    """Schema for image variant"""
    variant_name: str
    width: int
    height: int
    file_path: str
    file_size: int
    quality: int = 85
    format: str = "webp"
    cdn_url: Optional[str] = None


class ImageUploadRequest(BaseModel):
    """Schema for image upload request"""
    product_id: int
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None
    is_primary: bool = False
    generate_variants: bool = True
    cdn_enabled: bool = False
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return v


class ImageOptimizationRequest(BaseModel):
    """Schema for image optimization request"""
    image_id: int
    quality: int = Field(default=85, ge=1, le=100)
    max_width: Optional[int] = Field(default=None, ge=100, le=4000)
    max_height: Optional[int] = Field(default=None, ge=100, le=4000)
    format: str = Field(default="webp", regex="^(webp|jpg|png)$")
    generate_variants: bool = True


class ImageVariantConfig(BaseModel):
    """Configuration for image variants"""
    thumbnail: Dict[str, int] = {"width": 150, "height": 150}
    small: Dict[str, int] = {"width": 300, "height": 300}
    medium: Dict[str, int] = {"width": 600, "height": 600}
    large: Dict[str, int] = {"width": 1200, "height": 1200}
    quality: int = 85
    format: str = "webp"


class ImageResponse(BaseModel):
    """Schema for image response"""
    id: int
    product_id: int
    original_filename: str
    original_path: str
    original_size: int
    original_width: int
    original_height: int
    mime_type: str
    file_hash: str
    alt_text: Optional[str]
    caption: Optional[str]
    variants: Dict[str, str]
    cdn_url: Optional[str]
    cdn_enabled: bool
    is_primary: bool
    display_order: int
    is_active: bool
    tags: List[str]
    category: Optional[str]
    uploaded_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ImageGalleryRequest(BaseModel):
    """Schema for creating image gallery"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    layout: str = Field(default="grid", regex="^(grid|masonry|carousel)$")
    columns: int = Field(default=4, ge=1, le=12)
    product_category: Optional[str] = None
    tags: List[str] = []


class ImageGalleryResponse(BaseModel):
    """Schema for image gallery response"""
    id: int
    name: str
    description: Optional[str]
    layout: str
    columns: int
    product_category: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ImageSearchRequest(BaseModel):
    """Schema for image search request"""
    query: str = Field(..., min_length=1)
    product_category: Optional[str] = None
    tags: List[str] = []
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    is_primary_only: bool = False
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class ImageSearchResponse(BaseModel):
    """Schema for image search response"""
    total: int
    images: List[ImageResponse]
    query: str
    filters: Dict[str, Any]


class ImageBulkUploadRequest(BaseModel):
    """Schema for bulk image upload"""
    product_id: int
    images: List[Dict[str, Any]]  # List of image data
    default_tags: List[str] = []
    default_category: Optional[str] = None
    generate_variants: bool = True
    cdn_enabled: bool = False


class ImageBulkOperationResponse(BaseModel):
    """Schema for bulk operation response"""
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, str]]
    results: List[ImageResponse]


class CDNConfigRequest(BaseModel):
    """Schema for CDN configuration"""
    provider: str = Field(..., regex="^(cloudflare|aws|azure|custom)$")
    base_url: str
    api_key: Optional[str] = None
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    custom_domain: Optional[str] = None


class ImageUpdateRequest(BaseModel):
    """Schema for updating image metadata"""
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_primary: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
