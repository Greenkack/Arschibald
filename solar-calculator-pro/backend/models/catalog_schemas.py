"""
Product Catalog Pydantic Schemas

This module defines the Pydantic schemas for request/response validation
in the product catalog management system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AttributeType(str, Enum):
    """Attribute data types"""
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"


class RelationshipType(str, Enum):
    """Product relationship types"""
    RELATED = "related"
    CROSS_SELL = "cross_sell"
    UPSELL = "upsell"
    ACCESSORY = "accessory"


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CategoryResponse(CategoryBase):
    id: int
    level: int
    path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    children_count: Optional[int] = 0
    products_count: Optional[int] = 0

    class Config:
        from_attributes = True


class CategoryTree(CategoryResponse):
    children: List['CategoryTree'] = []

    class Config:
        from_attributes = True


# Attribute Schemas
class AttributeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: AttributeType
    unit: Optional[str] = None
    is_required: bool = False
    is_filterable: bool = True
    is_searchable: bool = True
    is_visible: bool = True
    sort_order: int = 0
    validation_rules: Optional[Dict[str, Any]] = None


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[AttributeType] = None
    unit: Optional[str] = None
    is_required: Optional[bool] = None
    is_filterable: Optional[bool] = None
    is_searchable: Optional[bool] = None
    is_visible: Optional[bool] = None
    sort_order: Optional[int] = None
    validation_rules: Optional[Dict[str, Any]] = None


class AttributeValueBase(BaseModel):
    value: str = Field(..., min_length=1, max_length=255)
    label: str = Field(..., min_length=1, max_length=255)
    sort_order: int = 0
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class AttributeValueCreate(AttributeValueBase):
    attribute_id: int


class AttributeValueResponse(AttributeValueBase):
    id: int
    attribute_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttributeResponse(AttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    values: List[AttributeValueResponse] = []

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    manufacturer: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=255)
    base_price: float = Field(..., ge=0)
    currency: str = Field(default="EUR", max_length=3)
    is_active: bool = True
    is_featured: bool = False
    stock_quantity: int = Field(default=0, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    tag_ids: Optional[List[int]] = []
    attribute_value_ids: Optional[List[int]] = []


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    manufacturer: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=255)
    base_price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tag_ids: Optional[List[int]] = None
    attribute_value_ids: Optional[List[int]] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    tags: List['TagResponse'] = []
    variants_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Product Variant Schemas
class ProductVariantBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    price_adjustment: float = 0.0
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True
    variant_attributes: Optional[Dict[str, str]] = None
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductVariantCreate(ProductVariantBase):
    parent_product_id: int


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    price_adjustment: Optional[float] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    variant_attributes: Optional[Dict[str, str]] = None
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductVariantResponse(ProductVariantBase):
    id: int
    parent_product_id: int
    created_at: datetime
    updated_at: datetime
    final_price: Optional[float] = None

    class Config:
        from_attributes = True


# Product Bundle Schemas
class BundleProductItem(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class ProductBundleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    bundle_price: float = Field(..., ge=0)
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    is_active: bool = True
    is_featured: bool = False
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductBundleCreate(ProductBundleBase):
    product_items: List[BundleProductItem]


class ProductBundleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    bundle_price: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    product_items: Optional[List[BundleProductItem]] = None


class ProductBundleResponse(ProductBundleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    products: List[ProductResponse] = []
    total_savings: Optional[float] = None

    class Config:
        from_attributes = True


# Product Relationship Schemas
class ProductRelationshipBase(BaseModel):
    related_product_id: int
    relationship_type: RelationshipType
    sort_order: int = 0


class ProductRelationshipCreate(ProductRelationshipBase):
    product_id: int


class ProductRelationshipResponse(ProductRelationshipBase):
    id: int
    product_id: int
    created_at: datetime
    related_product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_active: bool = True


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None


class TagResponse(TagBase):
    id: int
    created_at: datetime
    products_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Search and Filter Schemas
class ProductSearchRequest(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    manufacturer: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[int]] = None
    attributes: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = None
    sort_by: Optional[str] = "name"
    sort_order: Optional[str] = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Update forward references
CategoryTree.model_rebuild()
