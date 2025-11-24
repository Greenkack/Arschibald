"""
Permission and Role Management Schemas

Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PermissionActionEnum(str, Enum):
    """Permission action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"


class PermissionResourceEnum(str, Enum):
    """Permission resource types"""
    USER = "user"
    ROLE = "role"
    GROUP = "group"
    PERMISSION = "permission"
    PROJECT = "project"
    CALCULATION = "calculation"
    PDF = "pdf"
    PRODUCT = "product"
    PRICE_MATRIX = "price_matrix"
    CRM = "crm"
    CUSTOMER = "customer"
    OFFER = "offer"
    REPORT = "report"
    SETTINGS = "settings"
    AUDIT_LOG = "audit_log"
    SYSTEM = "system"


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=1)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    conditions: Optional[Dict[str, Any]] = None


class PermissionCreate(PermissionBase):
    """Schema for creating a permission"""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    resource: Optional[str] = Field(None, min_length=1, max_length=50)
    action: Optional[str] = Field(None, min_length=1, max_length=50)
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    is_system_permission: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=1)
    parent_role_id: Optional[int] = None
    priority: int = Field(default=0, ge=0, le=100)


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    parent_role_id: Optional[int] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    permission_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


class RoleWithInheritance(RoleResponse):
    """Schema for role with inherited permissions"""
    inherited_permissions: List[PermissionResponse] = []
    all_permissions: List[PermissionResponse] = []


# Group Schemas
class GroupBase(BaseModel):
    """Base group schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=1)
    parent_group_id: Optional[int] = None


class GroupCreate(GroupBase):
    """Schema for creating a group"""
    role_ids: List[int] = Field(default_factory=list)


class GroupUpdate(BaseModel):
    """Schema for updating a group"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    parent_group_id: Optional[int] = None
    role_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class GroupResponse(GroupBase):
    """Schema for group response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True


# User Role Assignment Schemas
class UserRoleAssignmentCreate(BaseModel):
    """Schema for assigning role to user"""
    user_id: int
    role_id: int
    expires_at: Optional[datetime] = None


class UserRoleAssignmentResponse(BaseModel):
    """Schema for user role assignment response"""
    id: int
    user_id: int
    role_id: int
    assigned_by_id: Optional[int]
    assigned_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


# Access Control List Schemas
class ACLCreate(BaseModel):
    """Schema for creating ACL entry"""
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    role_id: Optional[int] = None
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: Optional[int] = None
    permission_id: int
    allow: bool = True
    priority: int = Field(default=0, ge=0, le=100)
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    
    @validator('user_id', 'group_id', 'role_id')
    def validate_subject(cls, v, values):
        """Ensure at least one subject is specified"""
        if not any([values.get('user_id'), values.get('group_id'), values.get('role_id'), v]):
            raise ValueError("At least one of user_id, group_id, or role_id must be specified")
        return v


class ACLUpdate(BaseModel):
    """Schema for updating ACL entry"""
    allow: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class ACLResponse(BaseModel):
    """Schema for ACL response"""
    id: int
    user_id: Optional[int]
    group_id: Optional[int]
    role_id: Optional[int]
    resource_type: str
    resource_id: Optional[int]
    permission_id: int
    allow: bool
    priority: int
    conditions: Optional[Dict[str, Any]]
    created_by_id: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


# Permission Audit Log Schemas
class PermissionAuditLogResponse(BaseModel):
    """Schema for permission audit log response"""
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    permission_id: Optional[int]
    role_id: Optional[int]
    group_id: Optional[int]
    allowed: bool
    reason: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Permission Check Schemas
class PermissionCheckRequest(BaseModel):
    """Schema for checking permissions"""
    user_id: int
    resource: str
    action: str
    resource_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response"""
    allowed: bool
    reason: str
    matched_permissions: List[PermissionResponse] = []
    matched_roles: List[RoleResponse] = []


# Bulk Operations
class BulkPermissionAssignment(BaseModel):
    """Schema for bulk permission assignment"""
    role_id: int
    permission_ids: List[int]


class BulkRoleAssignment(BaseModel):
    """Schema for bulk role assignment"""
    user_ids: List[int]
    role_id: int
    expires_at: Optional[datetime] = None


class BulkGroupAssignment(BaseModel):
    """Schema for bulk group assignment"""
    user_ids: List[int]
    group_id: int


# Statistics and Reports
class PermissionStatistics(BaseModel):
    """Schema for permission statistics"""
    total_permissions: int
    active_permissions: int
    system_permissions: int
    custom_permissions: int
    permissions_by_resource: Dict[str, int]
    permissions_by_action: Dict[str, int]


class RoleStatistics(BaseModel):
    """Schema for role statistics"""
    total_roles: int
    active_roles: int
    system_roles: int
    custom_roles: int
    roles_with_inheritance: int
    average_permissions_per_role: float


class GroupStatistics(BaseModel):
    """Schema for group statistics"""
    total_groups: int
    active_groups: int
    groups_with_hierarchy: int
    average_users_per_group: float
    average_roles_per_group: float


class UserPermissionSummary(BaseModel):
    """Schema for user permission summary"""
    user_id: int
    direct_roles: List[RoleResponse]
    group_roles: List[RoleResponse]
    all_permissions: List[PermissionResponse]
    permission_count: int
