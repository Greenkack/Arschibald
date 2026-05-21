# backend/api/v1/images.py
"""
API endpoints for product image management
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db
from backend.services.image_service import ImageService
from backend.models.image_schemas import (
    ImageUploadRequest, ImageOptimizationRequest, ImageResponse,
    ImageSearchRequest, ImageSearchResponse, ImageUpdateRequest,
    ImageBulkUploadRequest, ImageBulkOperationResponse
)

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    product_id: int = Query(...),
    alt_text: Optional[str] = Query(None),
    caption: Optional[str] = Query(None),
    tags: List[str] = Query([]),
    category: Optional[str] = Query(None),
    is_primary: bool = Query(False),
    generate_variants: bool = Query(True),
    cdn_enabled: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Upload a product image
    
    - **file**: Image file to upload
    - **product_id**: ID of the product
    - **alt_text**: Alternative text for accessibility
    - **caption**: Image caption
    - **tags**: List of tags for categorization
    - **category**: Image category
    - **is_primary**: Set as primary product image
    - **generate_variants**: Generate thumbnail variants
    - **cdn_enabled**: Upload to CDN
    """
    service = ImageService(db)
    
    request = ImageUploadRequest(
        product_id=product_id,
        alt_text=alt_text,
        caption=caption,
        tags=tags,
        category=category,
        is_primary=is_primary,
        generate_variants=generate_variants,
        cdn_enabled=cdn_enabled
    )
    
    return await service.upload_image(file, request)


@router.post("/optimize", response_model=ImageResponse)
async def optimize_image(
    request: ImageOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize an existing image
    
    - **image_id**: ID of the image to optimize
    - **quality**: JPEG/WebP quality (1-100)
    - **max_width**: Maximum width in pixels
    - **max_height**: Maximum height in pixels
    - **format**: Output format (webp, jpg, png)
    - **generate_variants**: Regenerate variants
    """
    service = ImageService(db)
    return await service.optimize_image(request)


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get image by ID"""
    service = ImageService(db)
    image = service.get_image(image_id)
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image


@router.get("/product/{product_id}", response_model=List[ImageResponse])
def get_product_images(
    product_id: int,
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all images for a product"""
    service = ImageService(db)
    return service.get_product_images(product_id, include_inactive)


@router.post("/search", response_model=ImageSearchResponse)
def search_images(
    request: ImageSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search images with filters
    
    - **query**: Search text
    - **product_category**: Filter by category
    - **tags**: Filter by tags
    - **min_width/max_width**: Filter by width
    - **min_height/max_height**: Filter by height
    - **is_primary_only**: Only primary images
    - **limit**: Results per page
    - **offset**: Pagination offset
    """
    service = ImageService(db)
    return service.search_images(request)


@router.patch("/{image_id}", response_model=ImageResponse)
def update_image(
    image_id: int,
    request: ImageUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update image metadata
    
    - **alt_text**: Update alternative text
    - **caption**: Update caption
    - **tags**: Update tags
    - **category**: Update category
    - **is_primary**: Set as primary
    - **display_order**: Update display order
    - **is_active**: Activate/deactivate
    """
    service = ImageService(db)
    updates = request.dict(exclude_unset=True)
    return service.update_image(image_id, updates)


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Delete image and all variants"""
    service = ImageService(db)
    success = service.delete_image(image_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message": "Image deleted successfully"}


@router.post("/bulk-upload", response_model=ImageBulkOperationResponse)
async def bulk_upload_images(
    files: List[UploadFile] = File(...),
    product_id: int = Query(...),
    default_tags: List[str] = Query([]),
    default_category: Optional[str] = Query(None),
    generate_variants: bool = Query(True),
    cdn_enabled: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Upload multiple images at once
    
    - **files**: List of image files
    - **product_id**: ID of the product
    - **default_tags**: Tags to apply to all images
    - **default_category**: Category for all images
    - **generate_variants**: Generate variants for all
    - **cdn_enabled**: Upload all to CDN
    """
    service = ImageService(db)
    
    results = []
    errors = []
    successful = 0
    
    for file in files:
        try:
            request = ImageUploadRequest(
                product_id=product_id,
                tags=default_tags,
                category=default_category,
                generate_variants=generate_variants,
                cdn_enabled=cdn_enabled
            )
            
            result = await service.upload_image(file, request)
            results.append(result)
            successful += 1
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return ImageBulkOperationResponse(
        total=len(files),
        successful=successful,
        failed=len(errors),
        errors=errors,
        results=results
    )


@router.post("/{image_id}/set-primary")
def set_primary_image(
    image_id: int,
    product_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Set image as primary for product"""
    service = ImageService(db)
    
    # Unset all other primary images for this product
    from backend.models.image_models import ProductImage
    db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.is_primary == True
    ).update({"is_primary": False})
    
    # Set this image as primary
    service.update_image(image_id, {"is_primary": True})
    
    return {"message": "Primary image updated"}


@router.get("/{image_id}/variants")
def get_image_variants(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get all variants of an image"""
    from backend.models.image_models import ImageVariant
    
    variants = db.query(ImageVariant).filter(
        ImageVariant.image_id == image_id
    ).all()
    
    return {
        "image_id": image_id,
        "variants": [
            {
                "name": v.variant_name,
                "width": v.width,
                "height": v.height,
                "size": v.file_size,
                "format": v.format,
                "url": v.cdn_url or v.file_path
            }
            for v in variants
        ]
    }


@router.post("/{image_id}/regenerate-variants")
async def regenerate_variants(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Regenerate all variants for an image"""
    service = ImageService(db)
    
    from backend.models.image_models import ProductImage
    from PIL import Image
    
    image_record = db.query(ProductImage).filter(
        ProductImage.id == image_id
    ).first()
    
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Load original image
    original_image = Image.open(image_record.original_path)
    
    # Regenerate variants
    await service._generate_variants(image_record, original_image)
    
    return {"message": "Variants regenerated successfully"}
