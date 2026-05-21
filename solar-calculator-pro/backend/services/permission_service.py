"""
Permission Management Service

Business logic for granular permissions, roles, groups, and access control
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime
from fastapi import HTTPException, status
import logging

from backend.models.permission_models import (
    Permission, EnhancedRole, Group, UserRoleAssignment,
    AccessControlList, PermissionAuditLog
)
from backend.models.permission_schemas import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleWithInheritance,
    GroupCreate, GroupUpdate, GroupResponse,
    UserRoleAssignmentCreate, ACLCreate, ACLUpdate,
    PermissionCheckRequest, PermissionCheckResponse,
    BulkPermissionAssignment, BulkRoleAssignment, BulkGroupAssignment,
    PermissionStatistics, RoleStatistics, GroupStatistics, UserPermissionSummary
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for permission management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self._permission_cache: Dict[int, Set[str]] = {}  # user_id -> set of permission strings
    
    # Permission Management
    def create_permission(
        self,
        permission_data: PermissionCreate,
        created_by_id: Optional[int] = None
    ) -> Permission:
        """Create a new permission"""
        # Check if permission already exists
        existing = self.db.query(Permission).filter(
            Permission.name == permission_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission with this name already exists"
            )
        
        permission = Permission(
            name=permission_data.name,
            description=permission_data.description,
            resource=permission_data.resource,
            action=permission_data.action,
            conditions=permission_data.conditions
        )
        
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        
        # Log audit
        if created_by_id:
            self._log_audit(
                user_id=created_by_id,
                action="create_permission",
                resource_type="permission",
                resource_id=permission.id,
                allowed=True,
                details={"name": permission.name}
            )
        
        logger.info(f"Permission created: {permission.name} (ID: {permission.id})")
        return permission
    
    def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permissions(
        self,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Permission], int]:
        """Get list of permissions with filtering"""
        query = self.db.query(Permission)
        
        if resource:
            query = query.filter(Permission.resource == resource)
        if action:
            query = query.filter(Permission.action == action)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        
        total = query.count()
        permissions = query.order_by(Permission.name).offset(skip).limit(limit).all()
        
        return permissions, total
    
    def update_permission(
        self,
        permission_id: int,
        permission_data: PermissionUpdate,
        updated_by_id: Optional[int] = None
    ) -> Permission:
        """Update permission"""
        permission = self.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        if permission.is_system_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update system permission"
            )
        
        update_data = permission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        self.db.commit()
        self.db.refresh(permission)
        
        # Clear cache
        self._permission_cache.clear()
        
        if updated_by_id:
            self._log_audit(
                user_id=updated_by_id,
                action="update_permission",
                resource_type="permission",
                resource_id=permission.id,
                allowed=True,
                details=update_data
            )
        
        logger.info(f"Permission updated: {permission.name} (ID: {permission.id})")
        return permission
    
    def delete_permission(
        self,
        permission_id: int,
        deleted_by_id: Optional[int] = None
    ) -> bool:
        """Delete permission"""
        permission = self.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        if permission.is_system_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system permission"
            )
        
        permission_name = permission.name
        
        if deleted_by_id:
            self._log_audit(
                user_id=deleted_by_id,
                action="delete_permission",
                resource_type="permission",
                resource_id=permission.id,
                allowed=True,
                details={"name": permission_name}
            )
        
        self.db.delete(permission)
        self.db.commit()
        
        # Clear cache
        self._permission_cache.clear()
        
        logger.info(f"Permission deleted: {permission_name} (ID: {permission_id})")
        return True
    
    # Role Management with Inheritance
    def create_role(
        self,
        role_data: RoleCreate,
        created_by_id: Optional[int] = None
    ) -> EnhancedRole:
        """Create a new role"""
        existing = self.db.query(EnhancedRole).filter(
            EnhancedRole.name == role_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        # Validate parent role
        if role_data.parent_role_id:
            parent = self.get_role(role_data.parent_role_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent role not found"
                )
        
        role = EnhancedRole(
            name=role_data.name,
            description=role_data.description,
            parent_role_id=role_data.parent_role_id,
            priority=role_data.priority
        )
        
        self.db.add(role)
        self.db.flush()
        
        # Assign permissions
        if role_data.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        
        # Clear cache
        self._permission_cache.clear()
        
        if created_by_id:
            self._log_audit(
                user_id=created_by_id,
                action="create_role",
                resource_type="role",
                resource_id=role.id,
                allowed=True,
                details={"name": role.name}
            )
        
        logger.info(f"Role created: {role.name} (ID: {role.id})")
        return role
    
    def get_role(self, role_id: int) -> Optional[EnhancedRole]:
        """Get role by ID"""
        return self.db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
    
    def get_roles(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[EnhancedRole], int]:
        """Get list of roles"""
        query = self.db.query(EnhancedRole)
        
        if is_active is not None:
            query = query.filter(EnhancedRole.is_active == is_active)
        
        total = query.count()
        roles = query.order_by(desc(EnhancedRole.priority), EnhancedRole.name).offset(skip).limit(limit).all()
        
        return roles, total
    
    def get_role_with_inheritance(self, role_id: int) -> Optional[Dict[str, Any]]:
        """Get role with all inherited permissions"""
        role = self.get_role(role_id)
        if not role:
            return None
        
        all_permissions = self._get_inherited_permissions(role)
        
        return {
            "role": role,
            "direct_permissions": role.permissions,
            "inherited_permissions": [p for p in all_permissions if p not in role.permissions],
            "all_permissions": list(all_permissions)
        }
    
    def _get_inherited_permissions(self, role: EnhancedRole) -> Set[Permission]:
        """Recursively get all permissions including inherited ones"""
        permissions = set(role.permissions)
        
        if role.parent_role:
            parent_permissions = self._get_inherited_permissions(role.parent_role)
            permissions.update(parent_permissions)
        
        return permissions
    
    def update_role(
        self,
        role_id: int,
        role_data: RoleUpdate,
        updated_by_id: Optional[int] = None
    ) -> EnhancedRole:
        """Update role"""
        role = self.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update system role"
            )
        
        update_data = role_data.dict(exclude_unset=True)
        
        # Handle permission updates separately
        permission_ids = update_data.pop('permission_ids', None)
        
        for field, value in update_data.items():
            setattr(role, field, value)
        
        if permission_ids is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(permission_ids)
            ).all()
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        
        # Clear cache
        self._permission_cache.clear()
        
        if updated_by_id:
            self._log_audit(
                user_id=updated_by_id,
                action="update_role",
                resource_type="role",
                resource_id=role.id,
                allowed=True,
                details=update_data
            )
        
        logger.info(f"Role updated: {role.name} (ID: {role.id})")
        return role
    
    def delete_role(
        self,
        role_id: int,
        deleted_by_id: Optional[int] = None
    ) -> bool:
        """Delete role"""
        role = self.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system role"
            )
        
        role_name = role.name
        
        if deleted_by_id:
            self._log_audit(
                user_id=deleted_by_id,
                action="delete_role",
                resource_type="role",
                resource_id=role.id,
                allowed=True,
                details={"name": role_name}
            )
        
        self.db.delete(role)
        self.db.commit()
        
        # Clear cache
        self._permission_cache.clear()
        
        logger.info(f"Role deleted: {role_name} (ID: {role_id})")
        return True
