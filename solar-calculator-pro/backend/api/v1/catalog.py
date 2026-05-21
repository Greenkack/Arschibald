"""
Product Catalog API Endpoints

This module provides REST API endpoints for managing the product catalog.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.core.dependencies import get_db
from backend.services.catalog_service import CatalogService
from backend.models.catalog_schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTree,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductSearchRequest, PaginatedResponse,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductBundleCreate, ProductBundleUpdate, ProductBundleResponse,
    ProductRelationshipCreate, ProductRelationshipResponse, RelationshipType,
    TagCreate, TagUpdate, TagResponse
)

router = APIRouter(prefix="/catalog", tags=["Product Catalog"])


# ==================== Category Endpoints ====================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if slug already exists
    existing = CatalogService.get_category_by_slug(db, category_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with slug '{category_data.slug}' already exists"
        )
    
    return CatalogService.create_category(db, category_data)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category by ID"""
    category = CatalogService.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    return category


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get categories with optional filtering"""
    return CatalogService.get_categories(db, parent_id, is_active)


@router.get("/categories/tree/all", response_model=List[CategoryTree])
def get_category_tree(db: Session = Depends(get_db)):
    """Get hierarchical category tree"""
    return CatalogService.get_category_tree(db)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update category"""
    category = CatalogService.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete category"""
    success = CatalogService.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )


# ==================== Attribute Endpoints ====================

@router.post("/attributes", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
def create_attribute(
    attribute_data: AttributeCreate,
    db: Session = Depends(get_db)
):
    """Create a new attribute"""
    return CatalogService.create_attribute(db, attribute_data)


@router.get("/attributes/{attribute_id}", response_model=AttributeResponse)
def get_attribute(
    attribute_id: int,
    db: Session = Depends(get_db)
):
    """Get attribute by ID"""
    attribute = CatalogService.get_attribute(db, attribute_id)
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attribute with ID {attribute_id} not found"
        )
    return attribute


@router.get("/attributes", response_model=List[AttributeResponse])
def get_attributes(db: Session = Depends(get_db)):
    """Get all attributes"""
    return CatalogService.get_attributes(db)


@router.put("/attributes/{attribute_id}", response_model=AttributeResponse)
def update_attribute(
    attribute_id: int,
    attribute_data: AttributeUpdate,
    db: Session = Depends(get_db)
):
    """Update attribute"""
    attribute = CatalogService.update_attribute(db, attribute_id, attribute_data)
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attribute with ID {attribute_id} not found"
        )
    return attribute


@router.delete("/attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute(
    attribute_id: int,
    db: Session = Depends(get_db)
):
    """Delete attribute"""
    success = CatalogService.delete_attribute(db, attribute_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attribute with ID {attribute_id} not found"
        )


# ==================== Product Endpoints ====================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    # Check if SKU already exists
    existing = CatalogService.get_product_by_sku(db, product_data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )
    
    return CatalogService.create_product(db, product_data)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product by ID"""
    product = CatalogService.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


@router.post("/products/search", response_model=PaginatedResponse)
def search_products(
    search_params: ProductSearchRequest,
    db: Session = Depends(get_db)
):
    """Search products with filters and pagination"""
    products, total = CatalogService.search_products(db, search_params)
    
    total_pages = (total + search_params.page_size - 1) // search_params.page_size
    
    return PaginatedResponse(
        items=products,
        total=total,
        page=search_params.page,
        page_size=search_params.page_size,
        total_pages=total_pages
    )


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update product"""
    product = CatalogService.update_product(db, product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete product"""
    success = CatalogService.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )


# ==================== Product Variant Endpoints ====================

@router.post("/products/{product_id}/variants", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    product_id: int,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db)
):
    """Create a new product variant"""
    # Verify parent product exists
    product = CatalogService.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    variant_data.parent_product_id = product_id
    return CatalogService.create_variant(db, variant_data)


@router.get("/products/{product_id}/variants", response_model=List[ProductVariantResponse])
def get_product_variants(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all variants for a product"""
    return CatalogService.get_product_variants(db, product_id)


@router.get("/variants/{variant_id}", response_model=ProductVariantResponse)
def get_variant(
    variant_id: int,
    db: Session = Depends(get_db)
):
    """Get variant by ID"""
    variant = CatalogService.get_variant(db, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID {variant_id} not found"
        )
    return variant


@router.put("/variants/{variant_id}", response_model=ProductVariantResponse)
def update_variant(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db)
):
    """Update variant"""
    variant = CatalogService.update_variant(db, variant_id, variant_data)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID {variant_id} not found"
        )
    return variant


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db)
):
    """Delete variant"""
    success = CatalogService.delete_variant(db, variant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with ID {variant_id} not found"
        )


# ==================== Product Bundle Endpoints ====================

@router.post("/bundles", response_model=ProductBundleResponse, status_code=status.HTTP_201_CREATED)
def create_bundle(
    bundle_data: ProductBundleCreate,
    db: Session = Depends(get_db)
):
    """Create a new product bundle"""
    return CatalogService.create_bundle(db, bundle_data)


@router.get("/bundles/{bundle_id}", response_model=ProductBundleResponse)
def get_bundle(
    bundle_id: int,
    db: Session = Depends(get_db)
):
    """Get bundle by ID"""
    bundle = CatalogService.get_bundle(db, bundle_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle with ID {bundle_id} not found"
        )
    return bundle


@router.get("/bundles", response_model=List[ProductBundleResponse])
def get_bundles(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all bundles"""
    return CatalogService.get_bundles(db, is_active)


@router.put("/bundles/{bundle_id}", response_model=ProductBundleResponse)
def update_bundle(
    bundle_id: int,
    bundle_data: ProductBundleUpdate,
    db: Session = Depends(get_db)
):
    """Update bundle"""
    bundle = CatalogService.update_bundle(db, bundle_id, bundle_data)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle with ID {bundle_id} not found"
        )
    return bundle


@router.delete("/bundles/{bundle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bundle(
    bundle_id: int,
    db: Session = Depends(get_db)
):
    """Delete bundle"""
    success = CatalogService.delete_bundle(db, bundle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle with ID {bundle_id} not found"
        )


# ==================== Product Relationship Endpoints ====================

@router.post("/products/{product_id}/relationships", response_model=ProductRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(
    product_id: int,
    relationship_data: ProductRelationshipCreate,
    db: Session = Depends(get_db)
):
    """Create a product relationship"""
    # Verify product exists
    product = CatalogService.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    relationship_data.product_id = product_id
    return CatalogService.create_relationship(db, relationship_data)


@router.get("/products/{product_id}/related", response_model=List[ProductResponse])
def get_related_products(
    product_id: int,
    relationship_type: Optional[RelationshipType] = Query(None),
    db: Session = Depends(get_db)
):
    """Get related products"""
    return CatalogService.get_related_products(db, product_id, relationship_type)


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    relationship_id: int,
    db: Session = Depends(get_db)
):
    """Delete relationship"""
    success = CatalogService.delete_relationship(db, relationship_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found"
        )


# ==================== Tag Endpoints ====================

@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    """Create a new tag"""
    return CatalogService.create_tag(db, tag_data)


@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Get tag by ID"""
    tag = CatalogService.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag


@router.get("/tags", response_model=List[TagResponse])
def get_tags(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all tags"""
    return CatalogService.get_tags(db, is_active)


@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db)
):
    """Update tag"""
    tag = CatalogService.update_tag(db, tag_id, tag_data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Delete tag"""
    success = CatalogService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
