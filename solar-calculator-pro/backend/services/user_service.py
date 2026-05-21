"""
User Management Service

Business logic for user management operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime
from fastapi import HTTPException, status

from backend.models.user_models import User, UserActivityLog, UserSettings, Role
from backend.models.user_schemas import (
    UserCreate, UserUpdate, UserPasswordChange, UserResponse,
    UserActivityLog as UserActivityLogSchema, UserSettings as UserSettingsSchema,
    UserSettingsUpdate, RoleCreate, RoleUpdate, UserRole, UserStatus
)
from backend.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate, created_by_id: Optional[int] = None) -> User:
        """Create a new user"""
        # Check if username already exists
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            status=user_data.status,
            phone=user_data.phone,
            department=user_data.department
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create default settings
        settings = UserSettings(user_id=user.id)
        self.db.add(settings)
        self.db.commit()
        
        # Log activity
        if created_by_id:
            self.log_activity(
                user_id=created_by_id,
                action="create_user",
                resource="user",
                resource_id=user.id,
                details={"username": user.username, "role": user.role.value}
            )
        
        logger.info(f"User created: {user.username} (ID: {user.id})")
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Get list of users with filtering"""
        query = self.db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
        
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        return users, total
    
    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        updated_by_id: Optional[int] = None
    ) -> User:
        """Update user"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log activity
        if updated_by_id:
            self.log_activity(
                user_id=updated_by_id,
                action="update_user",
                resource="user",
                resource_id=user.id,
                details=update_data
            )
        
        logger.info(f"User updated: {user.username} (ID: {user.id})")
        return user
    
    def delete_user(self, user_id: int, deleted_by_id: Optional[int] = None) -> bool:
        """Delete user"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting super admin
        if user.role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete super admin user"
            )
        
        username = user.username
        
        # Log activity before deletion
        if deleted_by_id:
            self.log_activity(
                user_id=deleted_by_id,
                action="delete_user",
                resource="user",
                resource_id=user.id,
                details={"username": username}
            )
        
        self.db.delete(user)
        self.db.commit()
        
        logger.info(f"User deleted: {username} (ID: {user_id})")
        return True
    
    def change_password(
        self,
        user_id: int,
        password_data: UserPasswordChange
    ) -> bool:
        """Change user password"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        self.db.commit()
        
        # Log activity
        self.log_activity(
            user_id=user_id,
            action="change_password",
            resource="user",
            resource_id=user_id
        )
        
        logger.info(f"Password changed for user: {user.username} (ID: {user_id})")
        return True
    
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = self.get_user(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def log_activity(
        self,
        user_id: int,
        action: str,
        resource: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivityLog:
        """Log user activity"""
        log = UserActivityLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_user_activity_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[UserActivityLog], int]:
        """Get user activity logs"""
        query = self.db.query(UserActivityLog)
        
        # Apply filters
        if user_id:
            query = query.filter(UserActivityLog.user_id == user_id)
        
        if action:
            query = query.filter(UserActivityLog.action == action)
        
        if resource:
            query = query.filter(UserActivityLog.resource == resource)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        logs = query.order_by(desc(UserActivityLog.timestamp)).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """Get user settings"""
        return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    def update_user_settings(
        self,
        user_id: int,
        settings_data: UserSettingsUpdate
    ) -> UserSettings:
        """Update user settings"""
        settings = self.get_user_settings(user_id)
        if not settings:
            # Create default settings if not exists
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
        
        # Update fields
        update_data = settings_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        self.db.commit()
        self.db.refresh(settings)
        
        # Log activity
        self.log_activity(
            user_id=user_id,
            action="update_settings",
            resource="user_settings",
            resource_id=settings.id,
            details=update_data
        )
        
        logger.info(f"Settings updated for user ID: {user_id}")
        return settings
    
    def create_role(self, role_data: RoleCreate, created_by_id: Optional[int] = None) -> Role:
        """Create a custom role"""
        # Check if role name already exists
        existing_role = self.db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        
        role = Role(
            name=role_data.name,
            description=role_data.description,
            permissions=[p.dict() for p in role_data.permissions],
            is_system_role=False
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        # Log activity
        if created_by_id:
            self.log_activity(
                user_id=created_by_id,
                action="create_role",
                resource="role",
                resource_id=role.id,
                details={"name": role.name}
            )
        
        logger.info(f"Role created: {role.name} (ID: {role.id})")
        return role
    
    def get_roles(self) -> List[Role]:
        """Get all roles"""
        return self.db.query(Role).order_by(Role.name).all()
    
    def update_role(
        self,
        role_id: int,
        role_data: RoleUpdate,
        updated_by_id: Optional[int] = None
    ) -> Role:
        """Update role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Prevent updating system roles
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update system role"
            )
        
        # Update fields
        update_data = role_data.dict(exclude_unset=True)
        if 'permissions' in update_data:
            update_data['permissions'] = [p.dict() for p in update_data['permissions']]
        
        for field, value in update_data.items():
            setattr(role, field, value)
        
        self.db.commit()
        self.db.refresh(role)
        
        # Log activity
        if updated_by_id:
            self.log_activity(
                user_id=updated_by_id,
                action="update_role",
                resource="role",
                resource_id=role.id,
                details=update_data
            )
        
        logger.info(f"Role updated: {role.name} (ID: {role.id})")
        return role
    
    def delete_role(self, role_id: int, deleted_by_id: Optional[int] = None) -> bool:
        """Delete role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Prevent deleting system roles
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system role"
            )
        
        role_name = role.name
        
        # Log activity before deletion
        if deleted_by_id:
            self.log_activity(
                user_id=deleted_by_id,
                action="delete_role",
                resource="role",
                resource_id=role.id,
                details={"name": role_name}
            )
        
        self.db.delete(role)
        self.db.commit()
        
        logger.info(f"Role deleted: {role_name} (ID: {role_id})")
        return True
