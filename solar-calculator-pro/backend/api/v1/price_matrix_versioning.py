"""
Price Matrix Versioning API Endpoints

This module provides REST API endpoints for price matrix versioning operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.services.price_matrix_version_service import PriceMatrixVersionService
from backend.models.price_matrix_version_schemas import (
    PriceMatrixVersionCreate,
    PriceMatrixVersionUpdate,
    PriceMatrixVersionApprove,
    PriceMatrixVersionReject,
    PriceMatrixVersionRollback,
    PriceMatrixVersionCompare,
    PriceMatrixVersionResponse,
    PriceMatrixVersionListResponse,
    PriceMatrixVersionComparisonResponse,
    PriceMatrixVersionHistoryResponse,
    PriceMatrixVersionMigrationResult,
    PriceMatrixVersionRollbackResult,
    PriceMatrixVersionChangeResponse,
    VersionStatus
)

router = APIRouter(prefix="/price-matrix/versioning", tags=["Price Matrix Versioning"])


# Version CRUD Endpoints

@router.post("/versions", response_model=PriceMatrixVersionResponse, status_code=status.HTTP_201_CREATED)
def create_version(
    data: PriceMatrixVersionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new price matrix version
    
    - **matrix_id**: ID of the price matrix
    - **version_name**: Name for this version
    - **description**: Optional description
    - **matrix_data**: Complete matrix data snapshot
    - **metadata**: Optional metadata
    """
    service = PriceMatrixVersionService(db)
    try:
        version = service.create_version(data, current_user["id"])
        return version
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/versions/{version_id}", response_model=PriceMatrixVersionResponse)
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific version by ID"""
    service = PriceMatrixVersionService(db)
    version = service.get_version(version_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found"
        )
    
    return version


@router.get("/matrices/{matrix_id}/versions", response_model=List[PriceMatrixVersionListResponse])
def get_matrix_versions(
    matrix_id: int,
    status: Optional[VersionStatus] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all versions for a specific matrix"""
    service = PriceMatrixVersionService(db)
    versions, total_count = service.get_versions_by_matrix(
        matrix_id=matrix_id,
        status=status,
        limit=limit,
        offset=offset
    )
    return versions


@router.get("/matrices/{matrix_id}/versions/active", response_model=PriceMatrixVersionResponse)
def get_active_version(
    matrix_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the currently active version for a matrix"""
    service = PriceMatrixVersionService(db)
    version = service.get_active_version(matrix_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active version found for matrix {matrix_id}"
        )
    
    return version


@router.put("/versions/{version_id}", response_model=PriceMatrixVersionResponse)
def update_version(
    version_id: int,
    data: PriceMatrixVersionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a version (only if in draft status)"""
    service = PriceMatrixVersionService(db)
    try:
        version = service.update_version(version_id, data, current_user["id"])
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a version (only if in draft status)"""
    service = PriceMatrixVersionService(db)
    try:
        success = service.delete_version(version_id, current_user["id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_id} not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Approval Workflow Endpoints

@router.post("/versions/{version_id}/submit", response_model=PriceMatrixVersionResponse)
def submit_for_approval(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit a version for approval"""
    service = PriceMatrixVersionService(db)
    try:
        version = service.submit_for_approval(version_id, current_user["id"])
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/versions/{version_id}/approve", response_model=PriceMatrixVersionResponse)
def approve_version(
    version_id: int,
    data: PriceMatrixVersionApprove,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a version"""
    service = PriceMatrixVersionService(db)
    try:
        version = service.approve_version(version_id, data, current_user["id"])
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/versions/{version_id}/reject", response_model=PriceMatrixVersionResponse)
def reject_version(
    version_id: int,
    data: PriceMatrixVersionReject,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reject a version"""
    service = PriceMatrixVersionService(db)
    try:
        version = service.reject_version(version_id, data, current_user["id"])
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/versions/{version_id}/activate", response_model=PriceMatrixVersionResponse)
def activate_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Activate a version (make it the current active version)"""
    service = PriceMatrixVersionService(db)
    try:
        version = service.activate_version(version_id, current_user["id"])
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Version Comparison Endpoints

@router.post("/versions/compare", response_model=PriceMatrixVersionComparisonResponse)
def compare_versions(
    data: PriceMatrixVersionCompare,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Compare two versions and return differences
    
    - **version_a_id**: First version to compare
    - **version_b_id**: Second version to compare
    - **include_details**: Include detailed differences (default: true)
    """
    service = PriceMatrixVersionService(db)
    try:
        comparison = service.compare_versions(data, current_user["id"])
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Version Rollback Endpoints

@router.post("/versions/{version_id}/rollback", response_model=PriceMatrixVersionRollbackResult)
def rollback_to_version(
    version_id: int,
    data: PriceMatrixVersionRollback,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Rollback to a specific version
    
    - **rollback_reason**: Optional reason for rollback
    - **create_backup**: Create backup of current version before rollback (default: true)
    """
    service = PriceMatrixVersionService(db)
    try:
        result = service.rollback_to_version(version_id, data, current_user["id"])
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Version History Endpoints

@router.get("/matrices/{matrix_id}/history", response_model=PriceMatrixVersionHistoryResponse)
def get_version_history(
    matrix_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get complete version history for a matrix"""
    service = PriceMatrixVersionService(db)
    history = service.get_version_history(
        matrix_id=matrix_id,
        limit=limit,
        offset=offset
    )
    return history


@router.get("/versions/{version_id}/changes", response_model=List[PriceMatrixVersionChangeResponse])
def get_version_changes(
    version_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all changes for a specific version"""
    service = PriceMatrixVersionService(db)
    changes, total_count = service.get_version_changes(
        version_id=version_id,
        limit=limit,
        offset=offset
    )
    return changes


# Version Migration Endpoints

@router.post("/versions/migrate", response_model=PriceMatrixVersionMigrationResult)
def migrate_version_data(
    from_version_id: int = Query(..., description="Source version ID"),
    to_version_id: int = Query(..., description="Target version ID"),
    migration_rules: dict = Query(..., description="Migration rules configuration"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Migrate data from one version to another using migration rules
    
    Migration rules format:
    ```json
    {
        "rule_name": {
            "type": "rename_key|transform_value|add_default|remove_key",
            "old_key": "old_key_name",
            "new_key": "new_key_name",
            "transform": "function_name",
            "default": "default_value"
        }
    }
    ```
    """
    service = PriceMatrixVersionService(db)
    try:
        result = service.migrate_version_data(
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            migration_rules=migration_rules,
            user_id=current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
