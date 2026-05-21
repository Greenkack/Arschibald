# backend/models/image_models.py
"""
Database models for product image management
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class ProductImage(Base):
    """Product image model with variants and metadata"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Original image
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    original_size = Column(Integer, nullable=False)  # bytes
    original_width = Column(Integer, nullable=False)
    original_height = Column(Integer, nullable=False)
    
    # Image metadata
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    alt_text = Column(String(500))
    caption = Column(Text)
    
    # Image variants (thumbnails, optimized versions)
    variants = Column(JSON, default={})  # {size: path}
    
    # CDN integration
    cdn_url = Column(String(500))
    cdn_enabled = Column(Boolean, default=False)
    
    # Image properties
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Tags and categories
    tags = Column(JSON, default=[])
    category = Column(String(100))
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="images")


class ImageVariant(Base):
    """Image variant model for different sizes"""
    __tablename__ = "image_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("product_images.id"), nullable=False, index=True)
    
    # Variant details
    variant_name = Column(String(50), nullable=False)  # thumbnail, small, medium, large
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Optimization
    quality = Column(Integer, default=85)
    format = Column(String(10), default="webp")  # webp, jpg, png
    
    # CDN
    cdn_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("ProductImage", backref="variant_records")


class ImageGallery(Base):
    """Image gallery for organizing product images"""
    __tablename__ = "image_galleries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Gallery settings
    layout = Column(String(50), default="grid")  # grid, masonry, carousel
    columns = Column(Integer, default=4)
    
    # Filters
    product_category = Column(String(100))
    tags = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ImageSearchIndex(Base):
    """Search index for images"""
    __tablename__ = "image_search_index"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("product_images.id"), nullable=False, index=True)
    
    # Search fields
    search_text = Column(Text, nullable=False)  # Combined searchable text
    keywords = Column(JSON, default=[])
    
    # Timestamps
    indexed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("ProductImage", backref="search_index")
