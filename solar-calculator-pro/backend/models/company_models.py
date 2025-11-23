"""
Company Database Models for Multi-PDF System

This module defines the database models for company management in the multi-PDF system.
Each company has individual data including logos, documents, images, prices, and contact information.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class Company(Base):
    """
    Company model for multi-PDF generation
    
    Each company represents a separate business entity that can generate
    customized PDF offers with their own branding, pricing, and content.
    """
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    
    # Contact Information
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(255))
    address_street = Column(String(255))
    address_city = Column(String(100))
    address_postal_code = Column(String(20))
    address_country = Column(String(100), default="Deutschland")
    
    # Tax and Legal
    tax_id = Column(String(50))
    vat_number = Column(String(50))
    registration_number = Column(String(100))
    
    # Branding
    logo_path = Column(String(500))  # Path to company logo
    logo_position_x = Column(Float, default=50.0)  # X position in PDF (mm)
    logo_position_y = Column(Float, default=20.0)  # Y position in PDF (mm)
    logo_width = Column(Float, default=50.0)  # Logo width (mm)
    logo_height = Column(Float, default=30.0)  # Logo height (mm)
    
    # Color Scheme (hex colors)
    primary_color = Column(String(7), default="#0066CC")
    secondary_color = Column(String(7), default="#FF6600")
    accent_color = Column(String(7), default="#00CC66")
    
    # Pricing Rules
    base_markup_percentage = Column(Float, default=0.0)  # Base markup for all products
    price_increase_percentage = Column(Float, default=7.0)  # Increase for multi-PDF offers
    
    # Template Configuration
    template_prefix = Column(String(50))  # e.g., "f1", "f2" for template files
    template_folder = Column(String(255))  # Custom template folder path
    
    # Status and Metadata
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    notes = Column(Text)
    
    # Additional Configuration (JSON)
    custom_config = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("CompanyDocument", back_populates="company", cascade="all, delete-orphan")
    images = relationship("CompanyImage", back_populates="company", cascade="all, delete-orphan")
    pricing_rules = relationship("CompanyPricingRule", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', active={self.is_active})>"


class CompanyDocument(Base):
    """
    Documents associated with a company (datasheets, certificates, etc.)
    """
    __tablename__ = "company_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Document Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    document_type = Column(String(50))  # 'datasheet', 'certificate', 'brochure', 'contract', etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    
    # PDF Integration
    include_in_pdf = Column(Boolean, default=False)
    pdf_page_number = Column(Integer)  # Which page to include on
    pdf_position_x = Column(Float)
    pdf_position_y = Column(Float)
    
    # Metadata
    tags = Column(JSON, default=[])
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    
    def __repr__(self):
        return f"<CompanyDocument(id={self.id}, title='{self.title}', type='{self.document_type}')>"


class CompanyImage(Base):
    """
    Images associated with a company (product photos, facility images, etc.)
    """
    __tablename__ = "company_images"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Image Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_type = Column(String(50))  # 'product', 'facility', 'team', 'logo', etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    
    # Image Properties
    width = Column(Integer)  # Original width in pixels
    height = Column(Integer)  # Original height in pixels
    
    # PDF Integration
    include_in_pdf = Column(Boolean, default=False)
    pdf_page_number = Column(Integer)
    pdf_position_x = Column(Float)
    pdf_position_y = Column(Float)
    pdf_width = Column(Float)  # Width in PDF (mm)
    pdf_height = Column(Float)  # Height in PDF (mm)
    
    # Metadata
    tags = Column(JSON, default=[])
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="images")
    
    def __repr__(self):
        return f"<CompanyImage(id={self.id}, title='{self.title}', type='{self.image_type}')>"


class CompanyPricingRule(Base):
    """
    Custom pricing rules for specific products or categories per company
    """
    __tablename__ = "company_pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Rule Configuration
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False)  # 'product', 'category', 'brand', 'global'
    
    # Target (what this rule applies to)
    target_id = Column(Integer)  # Product ID, Category ID, etc.
    target_name = Column(String(255))  # Product name, Category name, Brand name
    
    # Pricing Adjustments
    markup_percentage = Column(Float, default=0.0)
    markup_fixed = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    discount_fixed = Column(Float, default=0.0)
    
    # Conditions
    min_quantity = Column(Integer)
    max_quantity = Column(Integer)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    
    # Priority and Status
    priority = Column(Integer, default=0)  # Higher priority rules apply first
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="pricing_rules")
    
    def __repr__(self):
        return f"<CompanyPricingRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"
