"""
Feature Flag API Endpoints

This module provides REST API endpoints for managing feature flags.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.core.dependencies import get_db, get_current_user
from backend.services.feature_flag_service import FeatureFlagService
from backend.models.feature_flag_schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    FeatureFlagCheck,
    FeatureFlagCheckResponse,
    FeatureFlagBulkCheck,
    FeatureFlagBulkCheckResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse
)
from backend.models.user_models import User
from backend.core.errors import APIError

router = APIRouter(prefix="/feature-flags", tags=["Feature Flags"])


def get_feature_flag_service(db: Session = Depends(get_db)) -> FeatureFlagService:
    """Dependency to get feature flag service"""
    return FeatureFlagService(db)


@router.post("/", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
def create_feature_flag(
    flag_data: FeatureFlagCreate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new feature flag
    
    Requires authentication. Only admins can create feature flags.
    """
    try:
        flag = service.create_feature_flag(flag_data, created_by=current_user.id)
        
        # Get user and role IDs for response
        user_ids = [user.id for user in flag.users]
        role_ids = [role.id for role in flag.roles]
        
        response = FeatureFlagResponse.from_orm(flag)
        response.user_ids = user_ids
        response.role_ids = role_ids
        
        return response
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[FeatureFlagResponse])
def list_feature_flags(
    skip: int = 0,
    limit: int = 100,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    List all feature flags
    
    Requires authentication.
    """
    try:
        flags = service.list_feature_flags(skip=skip, limit=limit)
        
        responses = []
        for flag in flags:
            user_ids = [user.id for user in flag.users]
            role_ids = [role.id for role in flag.roles]
            
            response = FeatureFlagResponse.from_orm(flag)
            response.user_ids = user_ids
            response.role_ids = role_ids
            responses.append(response)
        
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flag_id}", response_model=FeatureFlagResponse)
def get_feature_flag(
    flag_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific feature flag by ID
    
    Requires authentication.
    """
    try:
        flag = service.get_feature_flag(flag_id)
        if not flag:
            raise HTTPException(status_code=404, detail=f"Feature flag with ID {flag_id} not found")
        
        user_ids = [user.id for user in flag.users]
        role_ids = [role.id for role in flag.roles]
        
        response = FeatureFlagResponse.from_orm(flag)
        response.user_ids = user_ids
        response.role_ids = role_ids
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{flag_id}", response_model=FeatureFlagResponse)
def update_feature_flag(
    flag_id: int,
    flag_data: FeatureFlagUpdate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update a feature flag
    
    Requires authentication. Only admins can update feature flags.
    """
    try:
        flag = service.update_feature_flag(flag_id, flag_data)
        
        user_ids = [user.id for user in flag.users]
        role_ids = [role.id for role in flag.roles]
        
        response = FeatureFlagResponse.from_orm(flag)
        response.user_ids = user_ids
        response.role_ids = role_ids
        
        return response
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature_flag(
    flag_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a feature flag
    
    Requires authentication. Only admins can delete feature flags.
    """
    try:
        service.delete_feature_flag(flag_id)
        return None
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check", response_model=FeatureFlagCheckResponse)
def check_feature_flag(
    check_data: FeatureFlagCheck,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Check if a feature flag is enabled
    
    Can be called with or without authentication.
    If user_id is not provided, uses current authenticated user.
    """
    try:
        user_id = check_data.user_id or (current_user.id if current_user else None)
        return service.is_feature_enabled(check_data.key, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-bulk", response_model=FeatureFlagBulkCheckResponse)
def check_multiple_feature_flags(
    check_data: FeatureFlagBulkCheck,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Check multiple feature flags at once
    
    Can be called with or without authentication.
    If user_id is not provided, uses current authenticated user.
    """
    try:
        user_id = check_data.user_id or (current_user.id if current_user else None)
        flags = service.check_multiple_features(check_data.keys, user_id)
        return FeatureFlagBulkCheckResponse(flags=flags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Role management endpoints

@router.post("/roles/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new role
    
    Requires authentication. Only admins can create roles.
    """
    try:
        role = service.create_role(role_data)
        return RoleResponse.from_orm(role)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles/", response_model=List[RoleResponse])
def list_roles(
    skip: int = 0,
    limit: int = 100,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    List all roles
    
    Requires authentication.
    """
    try:
        roles = service.list_roles(skip=skip, limit=limit)
        return [RoleResponse.from_orm(role) for role in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific role by ID
    
    Requires authentication.
    """
    try:
        role = service.get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
        return RoleResponse.from_orm(role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update a role
    
    Requires authentication. Only admins can update roles.
    """
    try:
        role = service.update_role(role_id, role_data)
        return RoleResponse.from_orm(role)
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a role
    
    Requires authentication. Only admins can delete roles.
    """
    try:
        service.delete_role(role_id)
        return None
    except APIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
