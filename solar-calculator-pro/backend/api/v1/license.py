# License Management API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db
from backend.core.auth_dependencies import get_current_user, require_admin
from backend.services.license_service import LicenseService
from backend.models.license_schemas import (
    LicenseCreate, LicenseUpdate, LicenseResponse,
    LicenseValidationRequest, LicenseValidationResponse,
    LicenseRenewalRequest, LicenseRenewalResponse,
    LicenseFeatureCreate, LicenseFeatureResponse,
    LicenseReportRequest, LicenseReportResponse,
    LicenseActivationRequest, LicenseActivationResponse
)

router = APIRouter(prefix="/licenses", tags=["licenses"])


@router.post("/", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
async def create_license(
    license_data: LicenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new license (Admin only)
    
    - **license_type**: Type of license (trial, basic, professional, enterprise, lifetime)
    - **user_email**: Email of the license holder
    - **organization_name**: Optional organization name
    - **expires_at**: Optional expiry date (auto-calculated if not provided)
    - **enabled_features**: Dictionary of feature flags
    - **max_users**: Maximum number of users
    - **max_projects**: Maximum number of projects
    - **max_calculations_per_month**: Maximum calculations per month
    """
    service = LicenseService(db)
    return service.create_license(license_data, created_by=current_user.get("username"))


@router.get("/{license_id}", response_model=LicenseResponse)
async def get_license(
    license_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Get license by ID (Admin only)"""
    service = LicenseService(db)
    license = service.get_license(license_id)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return license


@router.get("/key/{license_key}", response_model=LicenseResponse)
async def get_license_by_key(
    license_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get license by key (Authenticated users)"""
    service = LicenseService(db)
    license = service.get_license_by_key(license_key)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    # Users can only view their own licenses (unless admin)
    if not current_user.get("is_admin") and license.user_email != current_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this license"
        )
    
    return license


@router.put("/{license_id}", response_model=LicenseResponse)
async def update_license(
    license_id: int,
    license_data: LicenseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a license (Admin only)"""
    service = LicenseService(db)
    license = service.update_license(
        license_id,
        license_data,
        updated_by=current_user.get("username")
    )
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return license


@router.post("/activate", response_model=LicenseActivationResponse)
async def activate_license(
    activation_data: LicenseActivationRequest,
    db: Session = Depends(get_db)
):
    """
    Activate a license (Public endpoint)
    
    - **license_key**: The license key to activate
    - **hardware_id**: Unique hardware identifier
    - **machine_name**: Optional machine name
    """
    service = LicenseService(db)
    return service.activate_license(activation_data)


@router.post("/validate", response_model=LicenseValidationResponse)
async def validate_license(
    validation_data: LicenseValidationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Validate a license (Public endpoint)
    
    - **license_key**: The license key to validate
    - **hardware_id**: Optional hardware identifier for binding check
    - **machine_name**: Optional machine name
    - **features_to_check**: Optional list of features to check access for
    """
    service = LicenseService(db)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return service.validate_license(
        validation_data,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.post("/renew", response_model=LicenseRenewalResponse)
async def renew_license(
    renewal_data: LicenseRenewalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Renew a license (Authenticated users)
    
    - **license_key**: The license key to renew
    - **renewal_period_days**: Number of days to extend the license
    - **payment_reference**: Optional payment reference
    - **payment_amount**: Optional payment amount in cents
    - **payment_currency**: Payment currency (default: EUR)
    """
    service = LicenseService(db)
    renewal = service.renew_license(
        renewal_data,
        renewed_by=current_user.get("username")
    )
    
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return renewal


@router.post("/report", response_model=LicenseReportResponse)
async def get_license_report(
    report_request: LicenseReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Generate license report (Admin only)
    
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    - **license_types**: Optional list of license types to include
    - **statuses**: Optional list of statuses to include
    - **include_validations**: Include recent validation history
    - **include_renewals**: Include recent renewal history
    """
    service = LicenseService(db)
    return service.get_license_report(report_request)


# Feature management endpoints

@router.post("/features", response_model=LicenseFeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: LicenseFeatureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new licensable feature (Admin only)
    
    - **feature_key**: Unique feature identifier (lowercase, underscores)
    - **feature_name**: Human-readable feature name
    - **description**: Optional feature description
    - **available_in_***: Availability flags for each license type
    - **category**: Optional feature category
    """
    service = LicenseService(db)
    return service.create_feature(feature_data)


@router.get("/features", response_model=List[LicenseFeatureResponse])
async def get_all_features(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all licensable features (Authenticated users)"""
    service = LicenseService(db)
    return service.get_all_features()
