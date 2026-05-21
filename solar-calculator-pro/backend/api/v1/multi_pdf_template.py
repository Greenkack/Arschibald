"""
Multi-PDF Template & Koordinaten System API Endpoints

This module provides REST API endpoints for the Multi-PDF template and coordinate system.

Requirements: 1.3, 6.1, 7.3
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from services.multi_pdf_template_service import MultiPDFTemplateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multi-pdf-template", tags=["Multi-PDF Template"])

# Initialize service
multi_pdf_service = MultiPDFTemplateService()


# Pydantic Models for API

class TemplateInfoResponse(BaseModel):
    """Response model for template information"""
    company_id: int
    page_number: int
    file_path: str
    exists: bool
    file_size: Optional[int] = None


class CoordinateInfoResponse(BaseModel):
    """Response model for coordinate information"""
    company_id: int
    page_number: int
    file_path: str
    exists: bool
    has_coordinates: bool


class ValidationResponse(BaseModel):
    """Response model for validation results"""
    is_valid: bool
    missing_files: List[str]
    message: str


class CompanySummaryResponse(BaseModel):
    """Response model for company summary"""
    company_id: int
    templates: Dict[str, Any]
    coordinates: Dict[str, Any]
    ready_for_generation: bool


class AllCompaniesSummaryResponse(BaseModel):
    """Response model for all companies summary"""
    total_companies: int
    companies_ready: int
    companies_with_issues: int
    company_ids: List[int]
    details: Dict[int, Dict[str, Any]]


class BatchLoadRequest(BaseModel):
    """Request model for batch loading"""
    company_ids: List[int] = Field(..., description="List of company IDs to load")
    pages: int = Field(8, ge=1, le=20, description="Number of pages per company")


# API Endpoints

@router.get("/companies", response_model=List[int])
async def discover_companies():
    """
    Discover all available companies by scanning template files.
    
    Returns:
        List of company IDs found in the template directory
    """
    try:
        companies = multi_pdf_service.discover_companies()
        return companies
    except Exception as e:
        logger.error(f"Error discovering companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/summary", response_model=AllCompaniesSummaryResponse)
async def get_all_companies_summary():
    """
    Get a summary of all discovered companies including validation status.
    
    Returns:
        Summary information for all companies
    """
    try:
        summary = multi_pdf_service.get_all_companies_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting companies summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}/summary", response_model=CompanySummaryResponse)
async def get_company_summary(company_id: int):
    """
    Get a summary of templates and coordinates for a specific company.
    
    Args:
        company_id: Company number
        
    Returns:
        Summary information for the company
    """
    try:
        summary = multi_pdf_service.get_company_summary(company_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting company {company_id} summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/templates",
    response_model=List[TemplateInfoResponse]
)
async def get_company_templates(
    company_id: int,
    pages: int = Query(8, ge=1, le=20, description="Number of pages")
):
    """
    Get information about all templates for a specific company.
    
    Args:
        company_id: Company number
        pages: Number of pages (default: 8)
        
    Returns:
        List of template information
    """
    try:
        templates = multi_pdf_service.get_all_templates_for_company(company_id, pages)
        return [
            TemplateInfoResponse(
                company_id=t.company_id,
                page_number=t.page_number,
                file_path=str(t.file_path),
                exists=t.exists,
                file_size=t.file_size
            )
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Error getting templates for company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/coordinates",
    response_model=List[CoordinateInfoResponse]
)
async def get_company_coordinates(
    company_id: int,
    pages: int = Query(8, ge=1, le=20, description="Number of pages")
):
    """
    Get information about all coordinate files for a specific company.
    
    Args:
        company_id: Company number
        pages: Number of pages (default: 8)
        
    Returns:
        List of coordinate information
    """
    try:
        coordinates = multi_pdf_service.get_all_coordinates_for_company(company_id, pages)
        return [
            CoordinateInfoResponse(
                company_id=c.company_id,
                page_number=c.page_number,
                file_path=str(c.file_path),
                exists=c.exists,
                has_coordinates=c.coordinates is not None
            )
            for c in coordinates
        ]
    except Exception as e:
        logger.error(f"Error getting coordinates for company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/templates/{page_number}",
    response_model=TemplateInfoResponse
)
async def get_template_info(company_id: int, page_number: int):
    """
    Get information about a specific template file.
    
    Args:
        company_id: Company number
        page_number: Page number (1-8)
        
    Returns:
        Template information
    """
    try:
        template_info = multi_pdf_service.get_template_info(company_id, page_number)
        return TemplateInfoResponse(
            company_id=template_info.company_id,
            page_number=template_info.page_number,
            file_path=str(template_info.file_path),
            exists=template_info.exists,
            file_size=template_info.file_size
        )
    except Exception as e:
        logger.error(
            f"Error getting template info for company {company_id}, "
            f"page {page_number}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/coordinates/{page_number}",
    response_model=Dict[str, Any]
)
async def get_coordinates(company_id: int, page_number: int):
    """
    Load and return coordinate data for a specific page.
    
    Args:
        company_id: Company number
        page_number: Page number (1-8)
        
    Returns:
        Coordinate data as dictionary
    """
    try:
        coordinates = multi_pdf_service.load_coordinates(company_id, page_number)
        if coordinates is None:
            raise HTTPException(
                status_code=404,
                detail=f"Coordinates not found for company {company_id}, page {page_number}"
            )
        return coordinates
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error loading coordinates for company {company_id}, "
            f"page {page_number}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/validate/templates",
    response_model=ValidationResponse
)
async def validate_company_templates(
    company_id: int,
    pages: int = Query(8, ge=1, le=20, description="Number of pages to validate")
):
    """
    Validate that all required templates exist for a company.
    
    Args:
        company_id: Company number
        pages: Number of pages to validate (default: 8)
        
    Returns:
        Validation result
    """
    try:
        is_valid, missing_files = multi_pdf_service.validate_company_templates(
            company_id, pages
        )
        
        message = (
            f"All {pages} templates are valid for company {company_id}"
            if is_valid
            else f"Missing {len(missing_files)} templates for company {company_id}"
        )
        
        return ValidationResponse(
            is_valid=is_valid,
            missing_files=missing_files,
            message=message
        )
    except Exception as e:
        logger.error(f"Error validating templates for company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/companies/{company_id}/validate/coordinates",
    response_model=ValidationResponse
)
async def validate_company_coordinates(
    company_id: int,
    pages: int = Query(8, ge=1, le=20, description="Number of pages to validate")
):
    """
    Validate that all required coordinate files exist for a company.
    
    Args:
        company_id: Company number
        pages: Number of pages to validate (default: 8)
        
    Returns:
        Validation result
    """
    try:
        is_valid, missing_files = multi_pdf_service.validate_company_coordinates(
            company_id, pages
        )
        
        message = (
            f"All {pages} coordinate files are valid for company {company_id}"
            if is_valid
            else f"Missing {len(missing_files)} coordinate files for company {company_id}"
        )
        
        return ValidationResponse(
            is_valid=is_valid,
            missing_files=missing_files,
            message=message
        )
    except Exception as e:
        logger.error(f"Error validating coordinates for company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/validate")
async def batch_validate_companies(request: BatchLoadRequest):
    """
    Validate templates and coordinates for multiple companies.
    
    Args:
        request: Batch load request with company IDs and page count
        
    Returns:
        Validation results for all companies
    """
    try:
        results = {}
        
        for company_id in request.company_ids:
            templates_valid, templates_missing = multi_pdf_service.validate_company_templates(
                company_id, request.pages
            )
            coords_valid, coords_missing = multi_pdf_service.validate_company_coordinates(
                company_id, request.pages
            )
            
            results[company_id] = {
                "templates": {
                    "valid": templates_valid,
                    "missing": templates_missing
                },
                "coordinates": {
                    "valid": coords_valid,
                    "missing": coords_missing
                },
                "ready": templates_valid and coords_valid
            }
        
        return {
            "total_companies": len(request.company_ids),
            "companies_ready": sum(1 for r in results.values() if r["ready"]),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in batch validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the Multi-PDF Template service.
    
    Returns:
        Service health status
    """
    try:
        # Check if directories exist
        template_dir_exists = multi_pdf_service.template_base_dir.exists()
        coord_dir_exists = multi_pdf_service.coordinate_base_dir.exists()
        
        # Discover companies
        companies = multi_pdf_service.discover_companies()
        
        return {
            "status": "healthy",
            "template_directory": str(multi_pdf_service.template_base_dir),
            "template_directory_exists": template_dir_exists,
            "coordinate_directory": str(multi_pdf_service.coordinate_base_dir),
            "coordinate_directory_exists": coord_dir_exists,
            "companies_discovered": len(companies),
            "company_ids": companies
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
