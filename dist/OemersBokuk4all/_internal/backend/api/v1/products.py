"""
Product Management API Endpoints

RESTful API endpoints for product management operations.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
import logging

from backend.services.product_service import get_product_service, ProductService
from backend.models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductSearchRequest,
    ProductSearchResponse,
    ProductImageUploadRequest,
    ProductImageUploadResponse,
    ProductExportRequest,
    ProductExportResponse,
    ProductImportRequest,
    ProductImportResponse,
    CategoryListResponse,
    ProductDeleteResponse
)

# Create router
router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)


# Dependency to get product service
def get_service() -> ProductService:
    """Get the product service instance"""
    return get_product_service()


# ==================== CRUD Endpoints ====================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_service)
):
    """
    Create a new product.
    
    - **category**: Product category (required)
    - **model_name**: Unique model name (required)
    - **brand**: Product brand/manufacturer
    - **price_euro**: Price in euros
    - Additional fields for technical specifications
    """
    try:
        created_product = service.create_product(product.dict(exclude_unset=True))
        return ProductResponse(**created_product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Get a product by ID.
    
    - **product_id**: Product ID
    """
    try:
        product = service.get_product(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        return ProductResponse(**product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/by-model/{model_name}", response_model=ProductResponse)
async def get_product_by_model_name(
    model_name: str,
    service: ProductService = Depends(get_service)
):
    """
    Get a product by model name.
    
    - **model_name**: Product model name
    """
    try:
        product = service.get_product_by_model_name(model_name)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with model name '{model_name}' not found"
            )
        
        return ProductResponse(**product)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting product by model name '{model_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    service: ProductService = Depends(get_service)
):
    """
    Update an existing product.
    
    - **product_id**: Product ID
    - All fields are optional, only provided fields will be updated
    """
    try:
        # Filter out None values
        update_data = product.dict(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        updated_product = service.update_product(product_id, update_data)
        return ProductResponse(**updated_product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Delete a product.
    
    - **product_id**: Product ID
    """
    try:
        success = service.delete_product(product_id)
        
        return ProductDeleteResponse(
            product_id=product_id,
            success=success,
            message=f"Product {product_id} deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== List and Search Endpoints ====================

@router.get("/", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    search: Optional[str] = Query(None, description="Search term"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Number of results to skip"),
    service: ProductService = Depends(get_service)
):
    """
    List products with optional filtering and pagination.
    
    - **category**: Filter by product category
    - **company_id**: Filter by company ID
    - **search**: Search in model name, brand, or description
    - **limit**: Maximum number of results
    - **offset**: Number of results to skip (for pagination)
    """
    try:
        products = service.list_products(
            category=category,
            company_id=company_id,
            search_term=search,
            limit=limit,
            offset=offset
        )
        
        return ProductListResponse(
            products=[ProductResponse(**p) for p in products],
            total=len(products),
            category=category,
            company_id=company_id
        )
    except Exception as e:
        logger.error(f"Unexpected error listing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/search", response_model=ProductSearchResponse)
async def search_products(
    search_request: ProductSearchRequest,
    service: ProductService = Depends(get_service)
):
    """
    Advanced product search with multiple filters.
    
    - **query**: Search query
    - **category**: Filter by category
    - **company_id**: Filter by company ID
    - **brand**: Filter by brand
    - **price_min**: Minimum price
    - **price_max**: Maximum price
    - **limit**: Maximum number of results
    """
    try:
        filters = {
            "category": search_request.category,
            "company_id": search_request.company_id,
            "brand": search_request.brand,
            "price_min": search_request.price_min,
            "price_max": search_request.price_max
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        products = service.search_products(
            query=search_request.query,
            filters=filters,
            limit=search_request.limit
        )
        
        return ProductSearchResponse(
            products=[ProductResponse(**p) for p in products],
            total=len(products),
            query=search_request.query
        )
    except Exception as e:
        logger.error(f"Unexpected error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/categories/list", response_model=CategoryListResponse)
async def get_categories(
    service: ProductService = Depends(get_service)
):
    """
    Get all product categories.
    """
    try:
        categories = service.get_categories()
        
        return CategoryListResponse(
            categories=categories,
            total=len(categories)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Image Management Endpoints ====================

@router.post("/{product_id}/image", response_model=ProductImageUploadResponse)
async def upload_product_image(
    product_id: int,
    image_request: ProductImageUploadRequest,
    service: ProductService = Depends(get_service)
):
    """
    Upload an image for a product.
    
    - **product_id**: Product ID
    - **image_data**: Image data (base64 encoded)
    - **image_format**: Image format (base64 or file_path)
    """
    try:
        updated_product = service.upload_product_image(
            product_id=product_id,
            image_data=image_request.image_data,
            image_format=image_request.image_format
        )
        
        return ProductImageUploadResponse(
            product_id=product_id,
            success=True,
            message="Image uploaded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error uploading image for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/{product_id}/image", response_model=ProductImageUploadResponse)
async def delete_product_image(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Delete the image from a product.
    
    - **product_id**: Product ID
    """
    try:
        updated_product = service.delete_product_image(product_id)
        
        return ProductImageUploadResponse(
            product_id=product_id,
            success=True,
            message="Image deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting image for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Import/Export Endpoints ====================

@router.post("/export", response_model=ProductExportResponse)
async def export_products(
    export_request: ProductExportRequest,
    service: ProductService = Depends(get_service)
):
    """
    Export products to various formats.
    
    - **category**: Filter by category
    - **company_id**: Filter by company ID
    - **format**: Export format (json, csv, excel)
    """
    try:
        export_data = service.export_products(
            category=export_request.category,
            company_id=export_request.company_id,
            format=export_request.format
        )
        
        return ProductExportResponse(**export_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error exporting products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/import", response_model=ProductImportResponse)
async def import_products(
    import_request: ProductImportRequest,
    service: ProductService = Depends(get_service)
):
    """
    Import products from various formats.
    
    - **format**: Import format (json, csv, excel)
    - **update_existing**: Whether to update existing products
    - **products**: Product data (for JSON format)
    - **csv_data**: CSV data (for CSV format)
    """
    try:
        import_data = import_request.dict(exclude_unset=True)
        
        results = service.import_products(
            import_data=import_data,
            format=import_request.format,
            update_existing=import_request.update_existing
        )
        
        return ProductImportResponse(**results)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error importing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
        )


@router.post("/import", response_model=ProductImportResponse)
async def import_products(
    import_request: ProductImportRequest,
    service: ProductService = Depends(get_service)
):
    """
    Import products from various formats.
    
    - **data**: Import data
    - **format**: Import format (json, csv, excel)
    - **update_existing**: Whether to update existing products
    """
    try:
        import_result = service.import_products(
            data=import_request.data,
            format=import_request.format,
            update_existing=import_request.update_existing
        )
        
        return ProductImportResponse(**import_result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error importing products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ==================== Attribute Management Endpoints ====================

@router.get("/attributes", response_model=dict)
async def list_attributes(
    service: ProductService = Depends(get_service)
):
    """
    Get all product attributes.
    
    Returns list of all defined product attributes with their configurations.
    """
    try:
        attributes = service.get_all_attributes()
        return {"attributes": attributes}
    except Exception as e:
        logger.error(f"Error fetching attributes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attributes"
        )


@router.post("/attributes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_attribute(
    attribute_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Create a new product attribute.
    
    - **name**: Attribute name (lowercase with underscores)
    - **label**: Display label
    - **type**: Attribute type (text, number, boolean, select, multiselect, date)
    - **required**: Whether the attribute is required
    - **options**: Options for select/multiselect types
    - **group_id**: Optional attribute group ID
    """
    try:
        attribute = service.create_attribute(attribute_data)
        return {"attribute": attribute}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attribute"
        )


@router.put("/attributes/{attribute_id}", response_model=dict)
async def update_attribute(
    attribute_id: int,
    attribute_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Update an existing product attribute.
    """
    try:
        attribute = service.update_attribute(attribute_id, attribute_data)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with ID {attribute_id} not found"
            )
        return {"attribute": attribute}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attribute"
        )


@router.delete("/attributes/{attribute_id}", response_model=dict)
async def delete_attribute(
    attribute_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Delete a product attribute.
    """
    try:
        success = service.delete_attribute(attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute with ID {attribute_id} not found"
            )
        return {"message": "Attribute deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attribute"
        )


# ==================== Attribute Group Endpoints ====================

@router.get("/attribute-groups", response_model=dict)
async def list_attribute_groups(
    service: ProductService = Depends(get_service)
):
    """
    Get all attribute groups.
    """
    try:
        groups = service.get_all_attribute_groups()
        return {"groups": groups}
    except Exception as e:
        logger.error(f"Error fetching attribute groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attribute groups"
        )


@router.post("/attribute-groups", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_attribute_group(
    group_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Create a new attribute group.
    
    - **name**: Group name (lowercase with underscores)
    - **label**: Display label
    - **description**: Optional description
    - **order**: Display order
    - **is_collapsible**: Whether the group can be collapsed
    - **is_expanded_by_default**: Whether the group is expanded by default
    """
    try:
        group = service.create_attribute_group(group_data)
        return {"group": group}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating attribute group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attribute group"
        )


@router.put("/attribute-groups/{group_id}", response_model=dict)
async def update_attribute_group(
    group_id: int,
    group_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Update an existing attribute group.
    """
    try:
        group = service.update_attribute_group(group_id, group_data)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute group with ID {group_id} not found"
            )
        return {"group": group}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attribute group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attribute group"
        )


@router.delete("/attribute-groups/{group_id}", response_model=dict)
async def delete_attribute_group(
    group_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Delete an attribute group.
    """
    try:
        success = service.delete_attribute_group(group_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute group with ID {group_id} not found"
            )
        return {"message": "Attribute group deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attribute group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attribute group"
        )


# ==================== Attribute Template Endpoints ====================

@router.get("/attribute-templates", response_model=dict)
async def list_attribute_templates(
    service: ProductService = Depends(get_service)
):
    """
    Get all attribute templates.
    """
    try:
        templates = service.get_all_attribute_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error fetching attribute templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attribute templates"
        )


@router.post("/attribute-templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_attribute_template(
    template_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Create a new attribute template.
    
    - **name**: Template name
    - **description**: Optional description
    - **category**: Product category this template applies to
    - **attributes**: List of attribute IDs to include
    """
    try:
        template = service.create_attribute_template(template_data)
        return {"template": template}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating attribute template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attribute template"
        )


@router.put("/attribute-templates/{template_id}", response_model=dict)
async def update_attribute_template(
    template_id: int,
    template_data: dict,
    service: ProductService = Depends(get_service)
):
    """
    Update an existing attribute template.
    """
    try:
        template = service.update_attribute_template(template_id, template_data)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute template with ID {template_id} not found"
            )
        return {"template": template}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attribute template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attribute template"
        )


@router.delete("/attribute-templates/{template_id}", response_model=dict)
async def delete_attribute_template(
    template_id: int,
    service: ProductService = Depends(get_service)
):
    """
    Delete an attribute template.
    """
    try:
        success = service.delete_attribute_template(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attribute template with ID {template_id} not found"
            )
        return {"message": "Attribute template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attribute template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attribute template"
        )
