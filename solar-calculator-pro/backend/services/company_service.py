"""
Company Service for Multi-PDF System

This service handles all company-related operations including CRUD operations,
data loading, and integration with the multi-PDF generation system.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from datetime import datetime
import os
import shutil

from backend.models.company_models import Company, CompanyDocument, CompanyImage, CompanyPricingRule
from backend.models.company_schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    CompanyDocumentCreate, CompanyDocumentUpdate,
    CompanyImageCreate, CompanyImageUpdate,
    CompanyPricingRuleCreate, CompanyPricingRuleUpdate
)


class CompanyService:
    """Service for managing companies in the multi-PDF system"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Company CRUD Operations
    # ========================================================================
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """
        Create a new company
        
        Args:
            company_data: Company creation data
            
        Returns:
            Created company instance
            
        Raises:
            HTTPException: If company name already exists
        """
        # Check if company name already exists
        existing = self.db.query(Company).filter(Company.name == company_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with name '{company_data.name}' already exists"
            )
        
        # If this is set as default, unset other defaults
        if company_data.is_default:
            self.db.query(Company).update({"is_default": False})
        
        # Create company
        company = Company(**company_data.dict())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def get_company(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found"
            )
        return company
    
    def get_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        search: Optional[str] = None
    ) -> List[Company]:
        """
        Get list of companies with optional filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Only return active companies
            search: Search term for name or display_name
            
        Returns:
            List of companies
        """
        query = self.db.query(Company)
        
        if active_only:
            query = query.filter(Company.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.display_name.ilike(search_term)
                )
            )
        
        query = query.order_by(Company.sort_order, Company.name)
        return query.offset(skip).limit(limit).all()
    
    def update_company(self, company_id: int, company_data: CompanyUpdate) -> Company:
        """
        Update company data
        
        Args:
            company_id: ID of company to update
            company_data: Updated company data
            
        Returns:
            Updated company instance
        """
        company = self.get_company(company_id)
        
        # Check if name is being changed and if it conflicts
        if company_data.name and company_data.name != company.name:
            existing = self.db.query(Company).filter(
                and_(
                    Company.name == company_data.name,
                    Company.id != company_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Company with name '{company_data.name}' already exists"
                )
        
        # If setting as default, unset other defaults
        if company_data.is_default:
            self.db.query(Company).filter(Company.id != company_id).update({"is_default": False})
        
        # Update fields
        update_data = company_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def delete_company(self, company_id: int) -> bool:
        """
        Delete a company (soft delete by setting is_active=False)
        
        Args:
            company_id: ID of company to delete
            
        Returns:
            True if successful
        """
        company = self.get_company(company_id)
        
        # Soft delete
        company.is_active = False
        company.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_default_company(self) -> Optional[Company]:
        """Get the default company"""
        return self.db.query(Company).filter(
            and_(
                Company.is_default == True,
                Company.is_active == True
            )
        ).first()
    
    # ========================================================================
    # Company Data Loading
    # ========================================================================
    
    def load_company_data(self, company_id: int) -> Dict[str, Any]:
        """
        Load all data for a company including documents, images, and pricing rules
        
        Args:
            company_id: ID of company to load
            
        Returns:
            Dictionary with complete company data
        """
        company = self.get_company(company_id)
        
        # Load related data
        documents = self.get_company_documents(company_id, active_only=True)
        images = self.get_company_images(company_id, active_only=True)
        pricing_rules = self.get_company_pricing_rules(company_id, active_only=True)
        
        return {
            "company": company,
            "documents": documents,
            "images": images,
            "pricing_rules": pricing_rules,
            "branding": {
                "logo_path": company.logo_path,
                "logo_position": {
                    "x": company.logo_position_x,
                    "y": company.logo_position_y,
                    "width": company.logo_width,
                    "height": company.logo_height
                },
                "colors": {
                    "primary": company.primary_color,
                    "secondary": company.secondary_color,
                    "accent": company.accent_color
                }
            },
            "pricing": {
                "base_markup": company.base_markup_percentage,
                "price_increase": company.price_increase_percentage
            },
            "template": {
                "prefix": company.template_prefix,
                "folder": company.template_folder
            }
        }
    
    def load_multiple_companies_data(self, company_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Load data for multiple companies
        
        Args:
            company_ids: List of company IDs
            
        Returns:
            List of company data dictionaries
        """
        return [self.load_company_data(company_id) for company_id in company_ids]
    
    # ========================================================================
    # Company Document Operations
    # ========================================================================
    
    def create_company_document(self, document_data: CompanyDocumentCreate) -> CompanyDocument:
        """Create a new company document"""
        # Verify company exists
        self.get_company(document_data.company_id)
        
        document = CompanyDocument(**document_data.dict())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def get_company_documents(
        self,
        company_id: int,
        active_only: bool = False,
        document_type: Optional[str] = None
    ) -> List[CompanyDocument]:
        """Get all documents for a company"""
        query = self.db.query(CompanyDocument).filter(CompanyDocument.company_id == company_id)
        
        if active_only:
            query = query.filter(CompanyDocument.is_active == True)
        
        if document_type:
            query = query.filter(CompanyDocument.document_type == document_type)
        
        return query.order_by(CompanyDocument.sort_order, CompanyDocument.title).all()
    
    def update_company_document(
        self,
        document_id: int,
        document_data: CompanyDocumentUpdate
    ) -> CompanyDocument:
        """Update a company document"""
        document = self.db.query(CompanyDocument).filter(CompanyDocument.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        update_data = document_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def delete_company_document(self, document_id: int) -> bool:
        """Delete a company document"""
        document = self.db.query(CompanyDocument).filter(CompanyDocument.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Delete file if it exists
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                # Log error but don't fail
                print(f"Error deleting file {document.file_path}: {e}")
        
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    # ========================================================================
    # Company Image Operations
    # ========================================================================
    
    def create_company_image(self, image_data: CompanyImageCreate) -> CompanyImage:
        """Create a new company image"""
        # Verify company exists
        self.get_company(image_data.company_id)
        
        image = CompanyImage(**image_data.dict())
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        
        return image
    
    def get_company_images(
        self,
        company_id: int,
        active_only: bool = False,
        image_type: Optional[str] = None
    ) -> List[CompanyImage]:
        """Get all images for a company"""
        query = self.db.query(CompanyImage).filter(CompanyImage.company_id == company_id)
        
        if active_only:
            query = query.filter(CompanyImage.is_active == True)
        
        if image_type:
            query = query.filter(CompanyImage.image_type == image_type)
        
        return query.order_by(CompanyImage.sort_order, CompanyImage.title).all()
    
    def update_company_image(self, image_id: int, image_data: CompanyImageUpdate) -> CompanyImage:
        """Update a company image"""
        image = self.db.query(CompanyImage).filter(CompanyImage.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found"
            )
        
        update_data = image_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(image, field, value)
        
        image.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(image)
        
        return image
    
    def delete_company_image(self, image_id: int) -> bool:
        """Delete a company image"""
        image = self.db.query(CompanyImage).filter(CompanyImage.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found"
            )
        
        # Delete file if it exists
        if image.file_path and os.path.exists(image.file_path):
            try:
                os.remove(image.file_path)
            except Exception as e:
                # Log error but don't fail
                print(f"Error deleting file {image.file_path}: {e}")
        
        self.db.delete(image)
        self.db.commit()
        
        return True
    
    # ========================================================================
    # Company Pricing Rule Operations
    # ========================================================================
    
    def create_pricing_rule(self, rule_data: CompanyPricingRuleCreate) -> CompanyPricingRule:
        """Create a new pricing rule"""
        # Verify company exists
        self.get_company(rule_data.company_id)
        
        rule = CompanyPricingRule(**rule_data.dict())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def get_company_pricing_rules(
        self,
        company_id: int,
        active_only: bool = False,
        rule_type: Optional[str] = None
    ) -> List[CompanyPricingRule]:
        """Get all pricing rules for a company"""
        query = self.db.query(CompanyPricingRule).filter(
            CompanyPricingRule.company_id == company_id
        )
        
        if active_only:
            query = query.filter(CompanyPricingRule.is_active == True)
        
        if rule_type:
            query = query.filter(CompanyPricingRule.rule_type == rule_type)
        
        return query.order_by(CompanyPricingRule.priority.desc(), CompanyPricingRule.rule_name).all()
    
    def update_pricing_rule(
        self,
        rule_id: int,
        rule_data: CompanyPricingRuleUpdate
    ) -> CompanyPricingRule:
        """Update a pricing rule"""
        rule = self.db.query(CompanyPricingRule).filter(CompanyPricingRule.id == rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricing rule with ID {rule_id} not found"
            )
        
        update_data = rule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        rule.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def delete_pricing_rule(self, rule_id: int) -> bool:
        """Delete a pricing rule"""
        rule = self.db.query(CompanyPricingRule).filter(CompanyPricingRule.id == rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricing rule with ID {rule_id} not found"
            )
        
        self.db.delete(rule)
        self.db.commit()
        
        return True
    
    # ========================================================================
    # Logo Management
    # ========================================================================
    
    def upload_company_logo(
        self,
        company_id: int,
        file_path: str,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> Company:
        """
        Upload and configure company logo
        
        Args:
            company_id: ID of company
            file_path: Path to logo file
            position_x: X position in PDF (mm)
            position_y: Y position in PDF (mm)
            width: Logo width (mm)
            height: Logo height (mm)
            
        Returns:
            Updated company instance
        """
        company = self.get_company(company_id)
        
        # Update logo configuration
        company.logo_path = file_path
        if position_x is not None:
            company.logo_position_x = position_x
        if position_y is not None:
            company.logo_position_y = position_y
        if width is not None:
            company.logo_width = width
        if height is not None:
            company.logo_height = height
        
        company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(company)
        
        return company
    
    def get_company_logo_config(self, company_id: int) -> Dict[str, Any]:
        """Get logo configuration for a company"""
        company = self.get_company(company_id)
        
        return {
            "logo_path": company.logo_path,
            "position": {
                "x": company.logo_position_x,
                "y": company.logo_position_y
            },
            "size": {
                "width": company.logo_width,
                "height": company.logo_height
            }
        }
    
    # ========================================================================
    # Template Management
    # ========================================================================
    
    def get_company_template_config(self, company_id: int) -> Dict[str, Any]:
        """Get template configuration for a company"""
        company = self.get_company(company_id)
        
        return {
            "prefix": company.template_prefix,
            "folder": company.template_folder,
            "template_files": self._get_template_files(company)
        }
    
    def _get_template_files(self, company: Company) -> List[str]:
        """Get list of template files for a company"""
        if not company.template_folder or not os.path.exists(company.template_folder):
            return []
        
        template_files = []
        for file in os.listdir(company.template_folder):
            if file.endswith('.pdf') and company.template_prefix in file:
                template_files.append(os.path.join(company.template_folder, file))
        
        return sorted(template_files)
