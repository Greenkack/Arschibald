"""
Module Features API Endpoints

API endpoints for managing module-level feature toggles
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from backend.core.dependencies import get_db
from backend.services.module_feature_service import ModuleFeatureService
from backend.core.auth_dependencies import get_current_user
from backend.models.user_schemas import UserResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/module-features", tags=["module-features"])


class ModuleToggleRequest(BaseModel):
    """Request to toggle a module"""
    module_key: str
    enabled: bool


class SubFeatureToggleRequest(BaseModel):
    """Request to toggle a sub-feature"""
    sub_feature_key: str
    enabled: bool


class ModuleStatusResponse(BaseModel):
    """Response with module status"""
    modules: Dict[str, Dict]


class InitializeResponse(BaseModel):
    """Response from initialization"""
    results: Dict[str, str]
    total: int
    created: int
    existing: int
    errors: int


@router.post("/initialize", response_model=InitializeResponse)
async def initialize_module_features(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Initialize all module-level feature flags
    
    This endpoint creates all predefined module and sub-feature flags.
    Only needs to be called once during setup.
    
    **Requires**: Admin privileges
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        service = ModuleFeatureService(db)
        results = service.initialize_module_features(created_by=current_user.id)
        
        # Count results
        created = sum(1 for v in results.values() if v == "created")
        existing = sum(1 for v in results.values() if v == "already_exists")
        errors = sum(1 for v in results.values() if v.startswith("error"))
        
        return InitializeResponse(
            results=results,
            total=len(results),
            created=created,
            existing=existing,
            errors=errors
        )
    except Exception as e:
        logger.error(f"Failed to initialize module features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ModuleStatusResponse)
async def get_module_status(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get status of all modules and their sub-features
    
    Returns the enabled/disabled status of all modules and their sub-features.
    If user_id is provided, checks status for that specific user.
    """
    try:
        service = ModuleFeatureService(db)
        
        # Use provided user_id or current user's id
        check_user_id = user_id if user_id is not None else current_user.id
        
        status = service.get_module_status(check_user_id)
        
        return ModuleStatusResponse(modules=status)
    except Exception as e:
        logger.error(f"Failed to get module status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle-module")
async def toggle_module(
    request: ModuleToggleRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Enable or disable a module
    
    **Requires**: Admin privileges
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        service = ModuleFeatureService(db)
        
        if request.enabled:
            service.enable_module(request.module_key)
        else:
            service.disable_module(request.module_key)
        
        return {
            "success": True,
            "module_key": request.module_key,
            "enabled": request.enabled
        }
    except Exception as e:
        logger.error(f"Failed to toggle module: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle-sub-feature")
async def toggle_sub_feature(
    request: SubFeatureToggleRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Enable or disable a sub-feature
    
    **Requires**: Admin privileges
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        service = ModuleFeatureService(db)
        
        if request.enabled:
            service.enable_sub_feature(request.sub_feature_key)
        else:
            service.disable_sub_feature(request.sub_feature_key)
        
        return {
            "success": True,
            "sub_feature_key": request.sub_feature_key,
            "enabled": request.enabled
        }
    except Exception as e:
        logger.error(f"Failed to toggle sub-feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-module/{module_key}")
async def check_module(
    module_key: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Check if a specific module is enabled
    """
    try:
        service = ModuleFeatureService(db)
        
        # Use provided user_id or current user's id
        check_user_id = user_id if user_id is not None else current_user.id
        
        enabled = service.is_module_enabled(module_key, check_user_id)
        
        return {
            "module_key": module_key,
            "enabled": enabled
        }
    except Exception as e:
        logger.error(f"Failed to check module: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-sub-feature/{module_key}/{sub_feature_key}")
async def check_sub_feature(
    module_key: str,
    sub_feature_key: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Check if a specific sub-feature is enabled
    
    This checks both the parent module and the sub-feature.
    """
    try:
        service = ModuleFeatureService(db)
        
        # Use provided user_id or current user's id
        check_user_id = user_id if user_id is not None else current_user.id
        
        enabled = service.is_sub_feature_enabled(module_key, sub_feature_key, check_user_id)
        
        return {
            "module_key": module_key,
            "sub_feature_key": sub_feature_key,
            "enabled": enabled
        }
    except Exception as e:
        logger.error(f"Failed to check sub-feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))
