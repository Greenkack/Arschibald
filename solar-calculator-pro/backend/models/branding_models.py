# backend/models/branding_models.py

"""
Database models for PDF Branding & Multi-Logo System
Supports company-specific branding with logos, colors, fonts, and templates
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class CompanyBranding(Base):
    """Company branding configuration for PDF generation"""
    __tablename__ = "company_branding"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Logo configuration
    logo_path = Column(String(500))  # Path to logo file
    logo_base64 = Column(Text)  # Base64 encoded logo
    logo_width = Column(Float, default=100.0)  # Logo width in points
    logo_height = Column(Float, default=50.0)  # Logo height in points
    logo_position_x = Column(Float, default=50.0)  # X position from YML
    logo_position_y = Column(Float, default=750.0)  # Y position from YML
    logo_page = Column(String(50), default="all")  # "all", "first", "header", "footer"
    
    # Color scheme
    primary_color = Column(String(7), default="#0066CC")  # Hex color
    secondary_color = Column(String(7), default="#003366")
    accent_color = Column(String(7), default="#FF6600")
    text_color = Column(String(7), default="#333333")
    background_color = Column(String(7), default="#FFFFFF")
    header_color = Column(String(7), default="#0066CC")
    footer_color = Column(String(7), default="#666666")
    
    # Typography
    font_family = Column(String(100), default="Helvetica")
    font_size_base = Column(Integer, default=10)
    font_size_heading = Column(Integer, default=16)
    font_size_subheading = Column(Integer, default=12)
    font_weight = Column(String(20), default="normal")  # "normal", "bold"
    
    # Header configuration
    header_enabled = Column(Boolean, default=True)
    header_text = Column(String(500))
    header_height = Column(Float, default=80.0)
    header_background_color = Column(String(7))
    header_text_color = Column(String(7))
    header_logo_enabled = Column(Boolean, default=True)
    
    # Footer configuration
    footer_enabled = Column(Boolean, default=True)
    footer_text = Column(String(500))
    footer_height = Column(Float, default=60.0)
    footer_background_color = Column(String(7))
    footer_text_color = Column(String(7))
    footer_logo_enabled = Column(Boolean, default=False)
    footer_page_numbers = Column(Boolean, default=True)
    
    # Watermark configuration
    watermark_enabled = Column(Boolean, default=False)
    watermark_text = Column(String(200))
    watermark_opacity = Column(Float, default=0.1)  # 0.0 to 1.0
    watermark_rotation = Column(Float, default=45.0)  # Degrees
    watermark_font_size = Column(Integer, default=60)
    watermark_color = Column(String(7), default="#CCCCCC")
    
    # Template configuration
    template_path = Column(String(500))  # Path to custom template
    template_type = Column(String(50), default="standard")  # "standard", "extended", "custom"
    
    # YML coordinates override
    yml_coordinates = Column(JSON)  # Custom YML coordinates for this company
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="branding")
    logo_positions = relationship("LogoPosition", back_populates="branding", cascade="all, delete-orphan")


class LogoPosition(Base):
    """Logo positioning for different pages and contexts"""
    __tablename__ = "logo_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    branding_id = Column(Integer, ForeignKey("company_branding.id"), nullable=False, index=True)
    
    # Position context
    page_number = Column(Integer)  # Specific page number, null for all pages
    context = Column(String(50), default="header")  # "header", "footer", "body", "watermark"
    
    # Position from YML coordinates
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float)
    height = Column(Float)
    
    # Styling
    opacity = Column(Float, default=1.0)
    rotation = Column(Float, default=0.0)
    scale = Column(Float, default=1.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    branding = relationship("CompanyBranding", back_populates="logo_positions")


class BrandingTemplate(Base):
    """Predefined branding templates"""
    __tablename__ = "branding_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    
    # Template configuration (JSON)
    config = Column(JSON, nullable=False)
    
    # Preview
    preview_image = Column(Text)  # Base64 encoded preview
    
    # Metadata
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BrandingAsset(Base):
    """Branding assets (logos, images, fonts)"""
    __tablename__ = "branding_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Asset information
    asset_type = Column(String(50), nullable=False)  # "logo", "image", "font", "icon"
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(500))
    file_base64 = Column(Text)
    file_size = Column(Integer)  # Bytes
    mime_type = Column(String(100))
    
    # Dimensions (for images)
    width = Column(Integer)
    height = Column(Integer)
    
    # Metadata
    is_primary = Column(Boolean, default=False)  # Primary logo/asset
    tags = Column(JSON)  # Array of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
