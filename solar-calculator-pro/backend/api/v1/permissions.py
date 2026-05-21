"""
Permission Management API Endpoints

API routes for granular permissions, roles, groups, and access control
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.models.user_models import User
from backend.services.permission_service import PermissionService
from backend.models.permission_schemas import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleWithInheritance,
    GroupCreate, GroupUpdate, GroupResponse,
    UserRoleAssignmentCreate, UserRoleAssignmentResponse,
    ACLCreate, ACLUpdate, ACLResponse,
    PermissionCheckRequest, PermissionCheckResponse,
    BulkPermissionAssignment, BulkRoleAssignment, BulkGroupAssignment,
    PermissionStatistics, RoleStatistics, GroupStatistics, UserPermissionSummary,
    PermissionAuditLogResponse
)

router = APIRouter(prefix="/permissions", tags=["permissions"])


# Permission Endpoints
@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new permission"""
    service = PermissionService(db)
    return service.create_permission(permission_data, current_user.id)


@router.get("/", response_model=List[PermissionResponse])
def get_permissions(
    resource: Optional[str] = None,
    action: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of permissions"""
    service = PermissionService(db)
    permissions, total = service.get_permissions(resource, action, is_active, skip, limit)
    return permissions


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permission by ID"""
    service = PermissionService(db)
    permission = service.get_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update permission"""
    service = PermissionService(db)
    return service.update_permission(permission_id, permission_data, current_user.id)


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete permission"""
    service = PermissionService(db)
    service.delete_permission(permission_id, current_user.id)


# Role Endpoints
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role"""
    service = PermissionService(db)
    return service.create_role(role_data, current_user.id)


@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of roles"""
    service = PermissionService(db)
    roles, total = service.get_roles(is_active, skip, limit)
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role by ID"""
    service = PermissionService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get("/roles/{role_id}/inheritance", response_model=RoleWithInheritance)
def get_role_with_inheritance(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role with inherited permissions"""
    service = PermissionService(db)
    role_data = service.get_role_with_inheritance(role_id)
    if not role_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role_data


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update role"""
    service = PermissionService(db)
    return service.update_role(role_id, role_data, current_user.id)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete role"""
    service = PermissionService(db)
    service.delete_role(role_id, current_user.id)
