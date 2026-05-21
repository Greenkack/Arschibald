"""
User Management API Endpoints

REST API endpoints for user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.services.user_service import UserService
from backend.models.user_schemas import (
    UserCreate, UserUpdate, UserPasswordChange, UserResponse, UserListResponse,
    UserActivityLog, UserActivityLogResponse, UserSettings, UserSettingsUpdate,
    RoleCreate, RoleUpdate, RoleResponse, UserRole, UserStatus
)
from backend.models.user_models import User

router = APIRouter(prefix="/users", tags=["users"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user
    
    Requires admin role
    """
    service = UserService(db)
    
    # Log activity with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    user = service.create_user(user_data, created_by_id=current_user.id)
    
    # Log the creation
    service.log_activity(
        user_id=current_user.id,
        action="create_user",
        resource="user",
        resource_id=user.id,
        details={"username": user.username, "role": user.role.value},
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return user


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get list of users with filtering and pagination
    
    Requires admin role
    """
    service = UserService(db)
    users, total = service.get_users(
        skip=skip,
        limit=limit,
        role=role,
        status=status,
        search=search
    )
    
    return UserListResponse(
        users=users,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user by ID
    
    Requires admin role
    """
    service = UserService(db)
    user = service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update user
    
    Requires admin role
    """
    service = UserService(db)
    
    # Log activity with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    user = service.update_user(user_id, user_data, updated_by_id=current_user.id)
    
    # Log the update
    service.log_activity(
        user_id=current_user.id,
        action="update_user",
        resource="user",
        resource_id=user.id,
        details=user_data.dict(exclude_unset=True),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user
    
    Requires admin role
    """
    service = UserService(db)
    
    # Log activity with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service.delete_user(user_id, deleted_by_id=current_user.id)
    
    # Log the deletion
    service.log_activity(
        user_id=current_user.id,
        action="delete_user",
        resource="user",
        resource_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return None


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserPasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's password"""
    service = UserService(db)
    
    # Log activity with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service.change_password(current_user.id, password_data)
    
    # Log the password change
    service.log_activity(
        user_id=current_user.id,
        action="change_password",
        resource="user",
        resource_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {"message": "Password changed successfully"}


@router.get("/activity/logs", response_model=UserActivityLogResponse)
async def get_activity_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user activity logs
    
    Requires admin role
    """
    service = UserService(db)
    logs, total = service.get_user_activity_logs(
        user_id=user_id,
        action=action,
        resource=resource,
        skip=skip,
        limit=limit
    )
    
    # Convert to schema with username
    log_responses = []
    for log in logs:
        user = service.get_user(log.user_id)
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else "Unknown",
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "timestamp": log.timestamp
        }
        log_responses.append(UserActivityLog(**log_dict))
    
    return UserActivityLogResponse(
        logs=log_responses,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's settings"""
    service = UserService(db)
    settings = service.get_user_settings(current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User settings not found"
        )
    
    return settings


@router.put("/me/settings", response_model=UserSettings)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's settings"""
    service = UserService(db)
    settings = service.update_user_settings(current_user.id, settings_data)
    return settings


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a custom role
    
    Requires admin role
    """
    service = UserService(db)
    role = service.create_role(role_data, created_by_id=current_user.id)
    return role


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all roles
    
    Requires admin role
    """
    service = UserService(db)
    roles = service.get_roles()
    return roles


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update role
    
    Requires admin role
    """
    service = UserService(db)
    role = service.update_role(role_id, role_data, updated_by_id=current_user.id)
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete role
    
    Requires admin role
    """
    service = UserService(db)
    service.delete_role(role_id, deleted_by_id=current_user.id)
    return None
