# backend/services/image_service.py
"""
Service for product image management with optimization and CDN integration
"""

import os
import hashlib
import io
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from PIL import Image
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import aiofiles

from backend.models.image_models import ProductImage, ImageVariant, ImageGallery, ImageSearchIndex
from backend.models.image_schemas import (
    ImageUploadRequest, ImageOptimizationRequest, ImageVariantConfig,
    ImageResponse, ImageSearchRequest, ImageBulkUploadRequest
)


class ImageService:
    """Service for managing product images"""
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path("uploads/products")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Default variant configuration
        self.variant_config = ImageVariantConfig()
        
        # Supported formats
        self.supported_formats = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def upload_image(
        self,
        file: UploadFile,
        request: ImageUploadRequest
    ) -> ImageResponse:
        """Upload and process product image"""
        
        # Validate file
        self._validate_file(file)
        
        # Read file content
        content = await file.read()
        file_hash = self._calculate_hash(content)
        
        # Check for duplicates
        existing = self.db.query(ProductImage).filter(
            ProductImage.file_hash == file_hash,
            ProductImage.product_id == request.product_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Image already exists")
        
        # Open image
        image = Image.open(io.BytesIO(content))
        original_width, original_height = image.size
        
        # Generate filename
        filename = self._generate_filename(file.filename, file_hash)
        file_path = self.upload_dir / filename
        
        # Save original
        await self._save_file(content, file_path)
        
        # Create database record
        db_image = ProductImage(
            product_id=request.product_id,
            original_filename=file.filename,
            original_path=str(file_path),
            original_size=len(content),
            original_width=original_width,
            original_height=original_height,
            mime_type=file.content_type,
            file_hash=file_hash,
            alt_text=request.alt_text,
            caption=request.caption,
            tags=request.tags,
            category=request.category,
            is_primary=request.is_primary,
            cdn_enabled=request.cdn_enabled
        )
        
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        
        # Generate variants
        if request.generate_variants:
            await self._generate_variants(db_image, image)
        
        # Update search index
        self._update_search_index(db_image)
        
        # Upload to CDN if enabled
        if request.cdn_enabled:
            await self._upload_to_cdn(db_image)
        
        return ImageResponse.from_orm(db_image)
    
    async def optimize_image(
        self,
        request: ImageOptimizationRequest
    ) -> ImageResponse:
        """Optimize existing image"""
        
        image_record = self.db.query(ProductImage).filter(
            ProductImage.id == request.image_id
        ).first()
        
        if not image_record:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Load original image
        image = Image.open(image_record.original_path)
        
        # Resize if needed
        if request.max_width or request.max_height:
            image = self._resize_image(
                image,
                request.max_width,
                request.max_height
            )
        
        # Convert format
        if request.format != image.format.lower():
            image = self._convert_format(image, request.format)
        
        # Save optimized version
        optimized_path = self._get_optimized_path(
            image_record.original_path,
            request.format
        )
        
        image.save(
            optimized_path,
            quality=request.quality,
            optimize=True
        )
        
        # Update database
        image_record.original_path = str(optimized_path)
        image_record.original_size = os.path.getsize(optimized_path)
        image_record.original_width, image_record.original_height = image.size
        
        self.db.commit()
        self.db.refresh(image_record)
        
        # Regenerate variants
        if request.generate_variants:
            await self._generate_variants(image_record, image)
        
        return ImageResponse.from_orm(image_record)
    
    async def _generate_variants(
        self,
        image_record: ProductImage,
        original_image: Image.Image
    ):
        """Generate image variants (thumbnails, etc.)"""
        
        variants = {}
        
        for variant_name, dimensions in [
            ("thumbnail", self.variant_config.thumbnail),
            ("small", self.variant_config.small),
            ("medium", self.variant_config.medium),
            ("large", self.variant_config.large)
        ]:
            # Skip if original is smaller
            if (original_image.width <= dimensions["width"] and
                original_image.height <= dimensions["height"]):
                continue
            
            # Resize
            variant_image = self._resize_image(
                original_image.copy(),
                dimensions["width"],
                dimensions["height"]
            )
            
            # Generate path
            variant_path = self._get_variant_path(
                image_record.original_path,
                variant_name
            )
            
            # Save variant
            variant_image.save(
                variant_path,
                quality=self.variant_config.quality,
                optimize=True,
                format=self.variant_config.format.upper()
            )
            
            # Create variant record
            variant_record = ImageVariant(
                image_id=image_record.id,
                variant_name=variant_name,
                width=variant_image.width,
                height=variant_image.height,
                file_path=str(variant_path),
                file_size=os.path.getsize(variant_path),
                quality=self.variant_config.quality,
                format=self.variant_config.format
            )
            
            self.db.add(variant_record)
            variants[variant_name] = str(variant_path)
        
        # Update image record with variants
        image_record.variants = variants
        self.db.commit()
    
    def get_image(self, image_id: int) -> Optional[ImageResponse]:
        """Get image by ID"""
        
        image = self.db.query(ProductImage).filter(
            ProductImage.id == image_id
        ).first()
        
        if not image:
            return None
        
        return ImageResponse.from_orm(image)
    
    def get_product_images(
        self,
        product_id: int,
        include_inactive: bool = False
    ) -> List[ImageResponse]:
        """Get all images for a product"""
        
        query = self.db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        )
        
        if not include_inactive:
            query = query.filter(ProductImage.is_active == True)
        
        query = query.order_by(ProductImage.display_order, ProductImage.id)
        
        images = query.all()
        return [ImageResponse.from_orm(img) for img in images]
    
    def search_images(
        self,
        request: ImageSearchRequest
    ) -> Dict[str, Any]:
        """Search images with filters"""
        
        query = self.db.query(ProductImage).join(ImageSearchIndex)
        
        # Text search
        if request.query:
            query = query.filter(
                ImageSearchIndex.search_text.ilike(f"%{request.query}%")
            )
        
        # Category filter
        if request.product_category:
            query = query.filter(
                ProductImage.category == request.product_category
            )
        
        # Tags filter
        if request.tags:
            for tag in request.tags:
                query = query.filter(
                    ProductImage.tags.contains([tag])
                )
        
        # Dimension filters
        if request.min_width:
            query = query.filter(ProductImage.original_width >= request.min_width)
        if request.max_width:
            query = query.filter(ProductImage.original_width <= request.max_width)
        if request.min_height:
            query = query.filter(ProductImage.original_height >= request.min_height)
        if request.max_height:
            query = query.filter(ProductImage.original_height <= request.max_height)
        
        # Primary only filter
        if request.is_primary_only:
            query = query.filter(ProductImage.is_primary == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        images = query.offset(request.offset).limit(request.limit).all()
        
        return {
            "total": total,
            "images": [ImageResponse.from_orm(img) for img in images],
            "query": request.query,
            "filters": {
                "category": request.product_category,
                "tags": request.tags,
                "dimensions": {
                    "min_width": request.min_width,
                    "max_width": request.max_width,
                    "min_height": request.min_height,
                    "max_height": request.max_height
                }
            }
        }
    
    def update_image(
        self,
        image_id: int,
        updates: Dict[str, Any]
    ) -> ImageResponse:
        """Update image metadata"""
        
        image = self.db.query(ProductImage).filter(
            ProductImage.id == image_id
        ).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Update fields
        for key, value in updates.items():
            if hasattr(image, key) and value is not None:
                setattr(image, key, value)
        
        self.db.commit()
        self.db.refresh(image)
        
        # Update search index
        self._update_search_index(image)
        
        return ImageResponse.from_orm(image)
    
    def delete_image(self, image_id: int) -> bool:
        """Delete image and all variants"""
        
        image = self.db.query(ProductImage).filter(
            ProductImage.id == image_id
        ).first()
        
        if not image:
            return False
        
        # Delete files
        try:
            if os.path.exists(image.original_path):
                os.remove(image.original_path)
            
            # Delete variants
            for variant_path in image.variants.values():
                if os.path.exists(variant_path):
                    os.remove(variant_path)
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        # Delete from database
        self.db.delete(image)
        self.db.commit()
        
        return True
    
    def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        
        # Check file extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in self.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Allowed: {', '.join(self.supported_formats)}"
            )
        
        # Check content type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def _generate_filename(self, original: str, file_hash: str) -> str:
        """Generate unique filename"""
        ext = original.split('.')[-1].lower()
        return f"{file_hash[:16]}.{ext}"
    
    async def _save_file(self, content: bytes, path: Path):
        """Save file asynchronously"""
        async with aiofiles.open(path, 'wb') as f:
            await f.write(content)
    
    def _resize_image(
        self,
        image: Image.Image,
        max_width: Optional[int],
        max_height: Optional[int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        
        if not max_width and not max_height:
            return image
        
        width, height = image.size
        
        if max_width and max_height:
            # Fit within both dimensions
            ratio = min(max_width / width, max_height / height)
        elif max_width:
            ratio = max_width / width
        else:
            ratio = max_height / height
        
        if ratio < 1:
            new_size = (int(width * ratio), int(height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def _convert_format(self, image: Image.Image, format: str) -> Image.Image:
        """Convert image format"""
        
        if format == 'jpg' and image.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB for JPEG
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            return background
        
        return image
    
    def _get_optimized_path(self, original_path: str, format: str) -> Path:
        """Get path for optimized image"""
        path = Path(original_path)
        return path.parent / f"{path.stem}_optimized.{format}"
    
    def _get_variant_path(self, original_path: str, variant_name: str) -> Path:
        """Get path for image variant"""
        path = Path(original_path)
        return path.parent / f"{path.stem}_{variant_name}.{self.variant_config.format}"
    
    def _update_search_index(self, image: ProductImage):
        """Update search index for image"""
        
        # Build search text
        search_parts = [
            image.original_filename,
            image.alt_text or "",
            image.caption or "",
            image.category or "",
            " ".join(image.tags)
        ]
        search_text = " ".join(filter(None, search_parts))
        
        # Update or create index
        index = self.db.query(ImageSearchIndex).filter(
            ImageSearchIndex.image_id == image.id
        ).first()
        
        if index:
            index.search_text = search_text
            index.keywords = image.tags
        else:
            index = ImageSearchIndex(
                image_id=image.id,
                search_text=search_text,
                keywords=image.tags
            )
            self.db.add(index)
        
        self.db.commit()
    
    async def _upload_to_cdn(self, image: ProductImage):
        """Upload image to CDN (placeholder for actual implementation)"""
        # TODO: Implement actual CDN upload based on provider
        # This would integrate with Cloudflare, AWS S3, Azure Blob, etc.
        pass
