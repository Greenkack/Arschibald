"""
Authentication API Endpoints

REST API endpoints for user authentication, registration, and session management.

Requirements: 1.7, 11.1, 11.2
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.core.auth_dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user
)
from backend.models.database_models import User
from backend.models.auth_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse,
    SessionInfo
)
from backend.services.auth_service import AuthService


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **username**: Unique username (3-100 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, must include uppercase, lowercase, and digit)
    - **full_name**: Optional full name
    - **role**: Optional role (default: "user")
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and receive access and refresh tokens.
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token and refresh token.
    """
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token.
    """
    auth_service = AuthService(db)
    return auth_service.refresh_access_token(refresh_data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    Note: In a stateless JWT system, logout is handled client-side by
    discarding the tokens. This endpoint is provided for consistency
    and can be extended to implement token blacklisting if needed.
    """
    return MessageResponse(
        message="Logged out successfully",
        detail="Please discard your access and refresh tokens"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    - **email**: New email address (optional)
    - **full_name**: New full name (optional)
    
    Note: Regular users cannot change their own role or active status.
    """
    # Prevent users from changing their own role or active status
    if update_data.role is not None or update_data.is_active is not None:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change role or active status"
            )
    
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(current_user, update_data)
    return updated_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    """
    auth_service = AuthService(db)
    result = auth_service.change_password(current_user, password_data)
    return MessageResponse(**result)


@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset token.
    
    - **email**: User's email address
    
    Sends password reset token to email (in production).
    For development, returns token in response.
    """
    auth_service = AuthService(db)
    result = auth_service.request_password_reset(reset_data)
    return MessageResponse(**result)


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.
    
    - **token**: Password reset token
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    """
    auth_service = AuthService(db)
    result = auth_service.reset_password(reset_data)
    return MessageResponse(**result)


@router.get("/session", response_model=SessionInfo)
async def get_session_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current session information.
    
    Returns information about the current authenticated session.
    """
    return SessionInfo(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        login_time=current_user.last_login or current_user.created_at,
        last_activity=current_user.last_login or current_user.created_at
    )


# Admin endpoints

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    
    Requires admin role.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only).
    
    Requires admin role.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user by ID (admin only).
    
    Allows admins to update any user's information including role and active status.
    
    Requires admin role.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = auth_service.update_user(user, update_data)
    return updated_user


@router.post("/users/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account (admin only).
    
    Requires admin role.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    result = auth_service.deactivate_user(user)
    return MessageResponse(**result)


@router.post("/users/{user_id}/activate", response_model=MessageResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate user account (admin only).
    
    Requires admin role.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = auth_service.activate_user(user)
    return MessageResponse(**result)
