# backend/services/branding_service.py

"""
Service for PDF Branding & Multi-Logo System
Handles company-specific branding, logo positioning, color schemes, fonts, and templates
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import base64
import io
import yaml
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

from backend.models.branding_models import (
    CompanyBranding,
    LogoPosition,
    BrandingTemplate,
    BrandingAsset
)
from backend.models.branding_schemas import (
    CompanyBrandingCreate,
    CompanyBrandingUpdate,
    LogoPositionCreate,
    BrandingTemplateCreate,
    BrandingAssetCreate
)
from backend.core.errors import NotFoundError, ValidationError


class BrandingService:
    """Service for managing PDF branding and multi-logo system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.yml_base_path = Path("coords")  # Base path for YML coordinates
    
    # ==================== Company Branding CRUD ====================
    
    def create_branding(self, branding_data: CompanyBrandingCreate) -> CompanyBranding:
        """Create new company branding configuration"""
        # Validate company exists
        from backend.models.company_models import Company
        company = self.db.query(Company).filter(Company.id == branding_data.company_id).first()
        if not company:
            raise NotFoundError(f"Company with id {branding_data.company_id} not found")
        
        # Check if branding already exists for this company
        existing = self.db.query(CompanyBranding).filter(
            CompanyBranding.company_id == branding_data.company_id
        ).first()
        if existing:
            raise ValidationError(f"Branding already exists for company {branding_data.company_id}")
        
        # Create branding
        branding = CompanyBranding(**branding_data.dict())
        self.db.add(branding)
        self.db.commit()
        self.db.refresh(branding)
        
        return branding
    
    def get_branding(self, branding_id: int) -> Optional[CompanyBranding]:
        """Get branding by ID"""
        return self.db.query(CompanyBranding).filter(CompanyBranding.id == branding_id).first()
    
    def get_branding_by_company(self, company_id: int) -> Optional[CompanyBranding]:
        """Get branding by company ID"""
        return self.db.query(CompanyBranding).filter(
            CompanyBranding.company_id == company_id
        ).first()
    
    def update_branding(self, branding_id: int, branding_data: CompanyBrandingUpdate) -> CompanyBranding:
        """Update company branding"""
        branding = self.get_branding(branding_id)
        if not branding:
            raise NotFoundError(f"Branding with id {branding_id} not found")
        
        # Update only provided fields
        update_data = branding_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(branding, key, value)
        
        self.db.commit()
        self.db.refresh(branding)
        
        return branding
    
    def delete_branding(self, branding_id: int) -> bool:
        """Delete company branding"""
        branding = self.get_branding(branding_id)
        if not branding:
            raise NotFoundError(f"Branding with id {branding_id} not found")
        
        self.db.delete(branding)
        self.db.commit()
        
        return True
    
    def list_brandings(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[CompanyBranding]:
        """List all company brandings"""
        query = self.db.query(CompanyBranding)
        
        if active_only:
            query = query.filter(CompanyBranding.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    # ==================== Logo Positioning ====================
    
    def add_logo_position(self, branding_id: int, position_data: LogoPositionCreate) -> LogoPosition:
        """Add logo position for branding"""
        branding = self.get_branding(branding_id)
        if not branding:
            raise NotFoundError(f"Branding with id {branding_id} not found")
        
        position = LogoPosition(branding_id=branding_id, **position_data.dict())
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    def get_logo_positions(self, branding_id: int, page_number: Optional[int] = None, 
                          context: Optional[str] = None) -> List[LogoPosition]:
        """Get logo positions for branding"""
        query = self.db.query(LogoPosition).filter(LogoPosition.branding_id == branding_id)
        
        if page_number is not None:
            query = query.filter(LogoPosition.page_number == page_number)
        
        if context:
            query = query.filter(LogoPosition.context == context)
        
        return query.all()
    
    def delete_logo_position(self, position_id: int) -> bool:
        """Delete logo position"""
        position = self.db.query(LogoPosition).filter(LogoPosition.id == position_id).first()
        if not position:
            raise NotFoundError(f"Logo position with id {position_id} not found")
        
        self.db.delete(position)
        self.db.commit()
        
        return True
    
    # ==================== Logo Processing ====================
    
    def upload_logo(self, company_id: int, logo_file: bytes, filename: str) -> BrandingAsset:
        """Upload and process company logo"""
        # Validate image
        try:
            image = Image.open(io.BytesIO(logo_file))
            width, height = image.size
        except Exception as e:
            raise ValidationError(f"Invalid image file: {str(e)}")
        
        # Convert to base64
        logo_base64 = base64.b64encode(logo_file).decode('utf-8')
        
        # Create asset
        asset_data = BrandingAssetCreate(
            company_id=company_id,
            asset_type="logo",
            name=filename,
            file_base64=logo_base64,
            file_size=len(logo_file),
            mime_type=f"image/{image.format.lower()}",
            width=width,
            height=height,
            is_primary=True
        )
        
        asset = BrandingAsset(**asset_data.dict())
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        
        # Update branding with logo
        branding = self.get_branding_by_company(company_id)
        if branding:
            branding.logo_base64 = logo_base64
            branding.logo_width = width
            branding.logo_height = height
            self.db.commit()
        
        return asset
    
    def get_logo_image(self, branding_id: int) -> Optional[ImageReader]:
        """Get logo as ImageReader for PDF generation"""
        branding = self.get_branding(branding_id)
        if not branding or not branding.logo_base64:
            return None
        
        try:
            logo_bytes = base64.b64decode(branding.logo_base64)
            return ImageReader(io.BytesIO(logo_bytes))
        except Exception:
            return None
    
    # ==================== YML Coordinates Integration ====================
    
    def load_yml_coordinates(self, branding_id: int, page_number: int) -> Dict[str, Any]:
        """Load YML coordinates for specific page"""
        branding = self.get_branding(branding_id)
        if not branding:
            raise NotFoundError(f"Branding with id {branding_id} not found")
        
        # Check for custom YML coordinates
        if branding.yml_coordinates and f"page_{page_number}" in branding.yml_coordinates:
            return branding.yml_coordinates[f"page_{page_number}"]
        
        # Load from YML file
        yml_file = self.yml_base_path / f"seite{page_number}.yml"
        if not yml_file.exists():
            return {}
        
        try:
            with open(yml_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValidationError(f"Error loading YML coordinates: {str(e)}")
    
    def apply_logo_positioning(self, pdf_canvas: canvas.Canvas, branding_id: int, 
                              page_number: int, context: str = "header") -> None:
        """Apply logo positioning to PDF canvas"""
        branding = self.get_branding(branding_id)
        if not branding:
            return
        
        # Get logo image
        logo_image = self.get_logo_image(branding_id)
        if not logo_image:
            return
        
        # Get logo positions for this page and context
        positions = self.get_logo_positions(branding_id, page_number, context)
        
        # If no specific positions, use default from branding
        if not positions:
            if context == "header" and branding.header_logo_enabled:
                positions = [type('obj', (object), {
                    'x': branding.logo_position_x,
                    'y': branding.logo_position_y,
                    'width': branding.logo_width,
                    'height': branding.logo_height,
                    'opacity': 1.0,
                    'rotation': 0.0,
                    'scale': 1.0
                })()]
            elif context == "footer" and branding.footer_logo_enabled:
                positions = [type('obj', (object), {
                    'x': branding.logo_position_x,
                    'y': 50.0,  # Footer position
                    'width': branding.logo_width,
                    'height': branding.logo_height,
                    'opacity': 1.0,
                    'rotation': 0.0,
                    'scale': 1.0
                })()]
        
        # Draw logo at each position
        for position in positions:
            pdf_canvas.saveState()
            
            # Apply transformations
            if position.rotation != 0:
                pdf_canvas.rotate(position.rotation)
            
            # Apply opacity
            pdf_canvas.setFillAlpha(position.opacity)
            
            # Calculate dimensions with scale
            width = (position.width or branding.logo_width) * position.scale
            height = (position.height or branding.logo_height) * position.scale
            
            # Draw logo
            pdf_canvas.drawImage(
                logo_image,
                position.x,
                position.y,
                width=width,
                height=height,
                preserveAspectRatio=True,
                mask='auto'
            )
            
            pdf_canvas.restoreState()
    
    # ==================== Color Scheme Application ====================
    
    def apply_color_scheme(self, pdf_canvas: canvas.Canvas, branding_id: int) -> None:
        """Apply color scheme to PDF canvas"""
        branding = self.get_branding(branding_id)
        if not branding:
            return
        
        # Set default colors
        pdf_canvas.setFillColor(HexColor(branding.text_color))
        pdf_canvas.setStrokeColor(HexColor(branding.primary_color))
    
    def get_color(self, branding_id: int, color_type: str) -> str:
        """Get specific color from branding"""
        branding = self.get_branding(branding_id)
        if not branding:
            return "#000000"
        
        color_map = {
            "primary": branding.primary_color,
            "secondary": branding.secondary_color,
            "accent": branding.accent_color,
            "text": branding.text_color,
            "background": branding.background_color,
            "header": branding.header_color,
            "footer": branding.footer_color
        }
        
        return color_map.get(color_type, "#000000")
    
    # ==================== Font Application ====================
    
    def apply_font_settings(self, pdf_canvas: canvas.Canvas, branding_id: int, 
                           font_type: str = "base") -> None:
        """Apply font settings to PDF canvas"""
        branding = self.get_branding(branding_id)
        if not branding:
            return
        
        font_size_map = {
            "base": branding.font_size_base,
            "heading": branding.font_size_heading,
            "subheading": branding.font_size_subheading
        }
        
        font_size = font_size_map.get(font_type, branding.font_size_base)
        font_name = f"{branding.font_family}-{branding.font_weight.capitalize()}" if branding.font_weight == "bold" else branding.font_family
        
        pdf_canvas.setFont(font_name, font_size)
    
    # ==================== Header/Footer Templates ====================
    
    def apply_header(self, pdf_canvas: canvas.Canvas, branding_id: int, page_number: int) -> None:
        """Apply header template to PDF"""
        branding = self.get_branding(branding_id)
        if not branding or not branding.header_enabled:
            return
        
        page_width, page_height = A4
        
        # Draw header background
        if branding.header_background_color:
            pdf_canvas.setFillColor(HexColor(branding.header_background_color))
            pdf_canvas.rect(0, page_height - branding.header_height, page_width, branding.header_height, fill=1, stroke=0)
        
        # Draw header text
        if branding.header_text:
            pdf_canvas.setFillColor(HexColor(branding.header_text_color or branding.text_color))
            self.apply_font_settings(pdf_canvas, branding_id, "subheading")
            pdf_canvas.drawString(50, page_height - branding.header_height + 30, branding.header_text)
        
        # Draw header logo
        if branding.header_logo_enabled:
            self.apply_logo_positioning(pdf_canvas, branding_id, page_number, "header")
    
    def apply_footer(self, pdf_canvas: canvas.Canvas, branding_id: int, page_number: int, total_pages: int) -> None:
        """Apply footer template to PDF"""
        branding = self.get_branding(branding_id)
        if not branding or not branding.footer_enabled:
            return
        
        page_width, _ = A4
        
        # Draw footer background
        if branding.footer_background_color:
            pdf_canvas.setFillColor(HexColor(branding.footer_background_color))
            pdf_canvas.rect(0, 0, page_width, branding.footer_height, fill=1, stroke=0)
        
        # Draw footer text
        if branding.footer_text:
            pdf_canvas.setFillColor(HexColor(branding.footer_text_color or branding.text_color))
            self.apply_font_settings(pdf_canvas, branding_id, "base")
            pdf_canvas.drawString(50, 30, branding.footer_text)
        
        # Draw page numbers
        if branding.footer_page_numbers:
            pdf_canvas.setFillColor(HexColor(branding.footer_text_color or branding.text_color))
            page_text = f"Seite {page_number} von {total_pages}"
            pdf_canvas.drawRightString(page_width - 50, 30, page_text)
        
        # Draw footer logo
        if branding.footer_logo_enabled:
            self.apply_logo_positioning(pdf_canvas, branding_id, page_number, "footer")
    
    # ==================== Watermark Support ====================
    
    def apply_watermark(self, pdf_canvas: canvas.Canvas, branding_id: int) -> None:
        """Apply watermark to PDF"""
        branding = self.get_branding(branding_id)
        if not branding or not branding.watermark_enabled or not branding.watermark_text:
            return
        
        page_width, page_height = A4
        
        pdf_canvas.saveState()
        
        # Set watermark properties
        pdf_canvas.setFillColor(HexColor(branding.watermark_color))
        pdf_canvas.setFillAlpha(branding.watermark_opacity)
        pdf_canvas.setFont(branding.font_family, branding.watermark_font_size)
        
        # Rotate and position watermark
        pdf_canvas.translate(page_width / 2, page_height / 2)
        pdf_canvas.rotate(branding.watermark_rotation)
        
        # Draw watermark text
        text_width = pdf_canvas.stringWidth(branding.watermark_text, branding.font_family, branding.watermark_font_size)
        pdf_canvas.drawString(-text_width / 2, 0, branding.watermark_text)
        
        pdf_canvas.restoreState()
    
    # ==================== Branding Templates ====================
    
    def create_template(self, template_data: BrandingTemplateCreate, user_id: Optional[int] = None) -> BrandingTemplate:
        """Create branding template"""
        template = BrandingTemplate(**template_data.dict(), created_by=user_id)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def get_template(self, template_id: int) -> Optional[BrandingTemplate]:
        """Get branding template"""
        return self.db.query(BrandingTemplate).filter(BrandingTemplate.id == template_id).first()
    
    def list_templates(self, public_only: bool = True) -> List[BrandingTemplate]:
        """List branding templates"""
        query = self.db.query(BrandingTemplate)
        
        if public_only:
            query = query.filter(BrandingTemplate.is_public == True)
        
        return query.all()
    
    def apply_template(self, branding_id: int, template_id: int) -> CompanyBranding:
        """Apply template to company branding"""
        branding = self.get_branding(branding_id)
        if not branding:
            raise NotFoundError(f"Branding with id {branding_id} not found")
        
        template = self.get_template(template_id)
        if not template:
            raise NotFoundError(f"Template with id {template_id} not found")
        
        # Apply template configuration
        for key, value in template.config.items():
            if hasattr(branding, key):
                setattr(branding, key, value)
        
        self.db.commit()
        self.db.refresh(branding)
        
        return branding
