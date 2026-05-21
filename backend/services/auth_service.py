"""
Authentication Service

Business logic for user authentication, registration, and session management.

Requirements: 1.7, 11.1, 11.2
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from backend.models.database_models import User
from backend.models.auth_schemas import (
    UserCreate,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm
)
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    generate_password_reset_token,
    verify_password_reset_token
)
from backend.core.config import settings
from backend.core.dynamic_keys import KeyPrefix


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_user = self.db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        existing_email = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role or "user",
            is_active=True
        )
        
        # Generate dynamic key if method exists
        try:
            user.generate_and_store_key(KeyPrefix.USER)
        except AttributeError:
            # Dynamic key generation is optional
            pass
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, login_data: LoginRequest) -> TokenResponse:
        """
        Authenticate user and generate tokens.
        
        Args:
            login_data: Login credentials
            
        Returns:
            Token response with access and refresh tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by username
        user = self.db.query(User).filter(
            User.username == login_data.username
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"})
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"})
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        username = payload.get("sub")
        
        # Get user
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def change_password(self, user: User, password_data: PasswordChangeRequest) -> Dict[str, str]:
        """
        Change user password.
        
        Args:
            user: Current user
            password_data: Password change data
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = hash_password(password_data.new_password)
        self.db.commit()
        
        return {"message": "Password changed successfully"}
    
    def request_password_reset(self, reset_data: PasswordResetRequest) -> Dict[str, str]:
        """
        Request password reset token.
        
        Args:
            reset_data: Password reset request data
            
        Returns:
            Reset token (in production, this should be sent via email)
        """
        # Get user by email
        user = self.db.query(User).filter(User.email == reset_data.email).first()
        
        # Always return success to prevent email enumeration
        if not user:
            return {
                "message": "If the email exists, a password reset link has been sent",
                "token": ""
            }
        
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        
        # In production, send this token via email
        # For now, return it in the response (development only)
        return {
            "message": "Password reset token generated",
            "token": reset_token  # Remove this in production
        }
    
    def reset_password(self, reset_data: PasswordResetConfirm) -> Dict[str, str]:
        """
        Reset password using reset token.
        
        Args:
            reset_data: Password reset confirmation data
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Verify reset token
        email = verify_password_reset_token(reset_data.token)
        
        # Get user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.hashed_password = hash_password(reset_data.new_password)
        self.db.commit()
        
        return {"message": "Password reset successfully"}
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user: User, update_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            user: User to update
            update_data: Update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email is being changed and already exists
        if update_data.email and update_data.email != user.email:
            existing_email = self.db.query(User).filter(
                User.email == update_data.email
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = update_data.email
        
        # Update other fields
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.role is not None:
            user.role = update_data.role
        if update_data.is_active is not None:
            user.is_active = update_data.is_active
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user: User) -> Dict[str, str]:
        """
        Deactivate user account.
        
        Args:
            user: User to deactivate
            
        Returns:
            Success message
        """
        user.is_active = False
        self.db.commit()
        
        return {"message": "User account deactivated"}
    
    def activate_user(self, user: User) -> Dict[str, str]:
        """
        Activate user account.
        
        Args:
            user: User to activate
            
        Returns:
            Success message
        """
        user.is_active = True
        self.db.commit()
        
        return {"message": "User account activated"}
