"""
Company API Endpoints for Multi-PDF System

This module provides REST API endpoints for managing companies, documents, images,
and pricing rules in the multi-PDF generation system.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from backend.core.dependencies import get_db
from backend.services.company_service import CompanyService
from backend.models.company_schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanySelectionResponse,
    CompanyDocumentCreate, CompanyDocumentUpdate, CompanyDocumentResponse,
    CompanyImageCreate, CompanyImageUpdate, CompanyImageResponse,
    CompanyPricingRuleCreate, CompanyPricingRuleUpdate, CompanyPricingRuleResponse
)


router = APIRouter(prefix="/companies", tags=["companies"])


# ============================================================================
# Company Endpoints
# ============================================================================

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new company
    
    Creates a new company with all configuration including branding, pricing rules,
    and template settings.
    """
    service = CompanyService(db)
    company = service.create_company(company_data)
    
    # Add counts
    response = CompanyResponse.from_orm(company)
    response.document_count = len(company.documents)
    response.image_count = len(company.images)
    response.pricing_rule_count = len(company.pricing_rules)
    
    return response


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of companies
    
    Retrieve companies with optional filtering by active status and search term.
    """
    service = CompanyService(db)
    companies = service.get_companies(skip=skip, limit=limit, active_only=active_only, search=search)
    
    # Add counts for each company
    response_list = []
    for company in companies:
        response = CompanyResponse.from_orm(company)
        response.document_count = len(company.documents)
        response.image_count = len(company.images)
        response.pricing_rule_count = len(company.pricing_rules)
        response_list.append(response)
    
    return response_list


@router.get("/selection", response_model=CompanySelectionResponse)
async def get_company_selection(
    db: Session = Depends(get_db)
):
    """
    Get companies for selection UI
    
    Returns all active companies with metadata for the multi-PDF selection interface.
    """
    service = CompanyService(db)
    companies = service.get_companies(active_only=True)
    default_company = service.get_default_company()
    
    # Build response
    company_responses = []
    for company in companies:
        response = CompanyResponse.from_orm(company)
        response.document_count = len(company.documents)
        response.image_count = len(company.images)
        response.pricing_rule_count = len(company.pricing_rules)
        company_responses.append(response)
    
    return CompanySelectionResponse(
        companies=company_responses,
        total=len(companies),
        active_count=len([c for c in companies if c.is_active]),
        default_company_id=default_company.id if default_company else None
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific company by ID"""
    service = CompanyService(db)
    company = service.get_company(company_id)
    
    response = CompanyResponse.from_orm(company)
    response.document_count = len(company.documents)
    response.image_count = len(company.images)
    response.pricing_rule_count = len(company.pricing_rules)
    
    return response


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """Update a company"""
    service = CompanyService(db)
    company = service.update_company(company_id, company_data)
    
    response = CompanyResponse.from_orm(company)
    response.document_count = len(company.documents)
    response.image_count = len(company.images)
    response.pricing_rule_count = len(company.pricing_rules)
    
    return response


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Delete a company (soft delete)"""
    service = CompanyService(db)
    service.delete_company(company_id)
    return None


@router.get("/{company_id}/data")
async def get_company_data(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete company data
    
    Returns all data for a company including documents, images, pricing rules,
    branding configuration, and template settings.
    """
    service = CompanyService(db)
    return service.load_company_data(company_id)


# ============================================================================
# Company Logo Endpoints
# ============================================================================

@router.post("/{company_id}/logo")
async def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    position_x: Optional[float] = Query(None),
    position_y: Optional[float] = Query(None),
    width: Optional[float] = Query(None),
    height: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Upload company logo
    
    Upload a logo file for a company and optionally configure its position and size in PDFs.
    """
    service = CompanyService(db)
    company = service.get_company(company_id)
    
    # Create upload directory if it doesn't exist
    upload_dir = Path("uploads/company_logos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"company_{company_id}_logo{file_extension}"
    file_path = upload_dir / file_name
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update company with logo path
    updated_company = service.upload_company_logo(
        company_id=company_id,
        file_path=str(file_path),
        position_x=position_x,
        position_y=position_y,
        width=width,
        height=height
    )
    
    return {
        "success": True,
        "logo_path": str(file_path),
        "company_id": company_id,
        "company_name": updated_company.name
    }


@router.get("/{company_id}/logo/config")
async def get_logo_config(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get logo configuration for a company"""
    service = CompanyService(db)
    return service.get_company_logo_config(company_id)


# ============================================================================
# Company Document Endpoints
# ============================================================================

@router.post("/{company_id}/documents", response_model=CompanyDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_company_document(
    company_id: int,
    document_data: CompanyDocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document for a company"""
    # Ensure company_id matches
    document_data.company_id = company_id
    
    service = CompanyService(db)
    document = service.create_company_document(document_data)
    return CompanyDocumentResponse.from_orm(document)


@router.get("/{company_id}/documents", response_model=List[CompanyDocumentResponse])
async def get_company_documents(
    company_id: int,
    active_only: bool = Query(False),
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all documents for a company"""
    service = CompanyService(db)
    documents = service.get_company_documents(company_id, active_only=active_only, document_type=document_type)
    return [CompanyDocumentResponse.from_orm(doc) for doc in documents]


@router.put("/documents/{document_id}", response_model=CompanyDocumentResponse)
async def update_company_document(
    document_id: int,
    document_data: CompanyDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a company document"""
    service = CompanyService(db)
    document = service.update_company_document(document_id, document_data)
    return CompanyDocumentResponse.from_orm(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a company document"""
    service = CompanyService(db)
    service.delete_company_document(document_id)
    return None


# ============================================================================
# Company Image Endpoints
# ============================================================================

@router.post("/{company_id}/images", response_model=CompanyImageResponse, status_code=status.HTTP_201_CREATED)
async def create_company_image(
    company_id: int,
    image_data: CompanyImageCreate,
    db: Session = Depends(get_db)
):
    """Create a new image for a company"""
    # Ensure company_id matches
    image_data.company_id = company_id
    
    service = CompanyService(db)
    image = service.create_company_image(image_data)
    return CompanyImageResponse.from_orm(image)


@router.get("/{company_id}/images", response_model=List[CompanyImageResponse])
async def get_company_images(
    company_id: int,
    active_only: bool = Query(False),
    image_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all images for a company"""
    service = CompanyService(db)
    images = service.get_company_images(company_id, active_only=active_only, image_type=image_type)
    return [CompanyImageResponse.from_orm(img) for img in images]


@router.put("/images/{image_id}", response_model=CompanyImageResponse)
async def update_company_image(
    image_id: int,
    image_data: CompanyImageUpdate,
    db: Session = Depends(get_db)
):
    """Update a company image"""
    service = CompanyService(db)
    image = service.update_company_image(image_id, image_data)
    return CompanyImageResponse.from_orm(image)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Delete a company image"""
    service = CompanyService(db)
    service.delete_company_image(image_id)
    return None


# ============================================================================
# Company Pricing Rule Endpoints
# ============================================================================

@router.post("/{company_id}/pricing-rules", response_model=CompanyPricingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_pricing_rule(
    company_id: int,
    rule_data: CompanyPricingRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new pricing rule for a company"""
    # Ensure company_id matches
    rule_data.company_id = company_id
    
    service = CompanyService(db)
    rule = service.create_pricing_rule(rule_data)
    return CompanyPricingRuleResponse.from_orm(rule)


@router.get("/{company_id}/pricing-rules", response_model=List[CompanyPricingRuleResponse])
async def get_pricing_rules(
    company_id: int,
    active_only: bool = Query(False),
    rule_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all pricing rules for a company"""
    service = CompanyService(db)
    rules = service.get_company_pricing_rules(company_id, active_only=active_only, rule_type=rule_type)
    return [CompanyPricingRuleResponse.from_orm(rule) for rule in rules]


@router.put("/pricing-rules/{rule_id}", response_model=CompanyPricingRuleResponse)
async def update_pricing_rule(
    rule_id: int,
    rule_data: CompanyPricingRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a pricing rule"""
    service = CompanyService(db)
    rule = service.update_pricing_rule(rule_id, rule_data)
    return CompanyPricingRuleResponse.from_orm(rule)


@router.delete("/pricing-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pricing_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a pricing rule"""
    service = CompanyService(db)
    service.delete_pricing_rule(rule_id)
    return None


# ============================================================================
# Template Configuration Endpoints
# ============================================================================

@router.get("/{company_id}/template-config")
async def get_template_config(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get template configuration for a company"""
    service = CompanyService(db)
    return service.get_company_template_config(company_id)
