"""
User Management Schemas

Pydantic models for user management API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class PermissionCategory(str, Enum):
    """Permission categories"""
    USERS = "users"
    PROJECTS = "projects"
    PRODUCTS = "products"
    PRICING = "pricing"
    PDF = "pdf"
    CRM = "crm"
    REPORTS = "reports"
    SETTINGS = "settings"


class Permission(BaseModel):
    """Permission model"""
    category: PermissionCategory
    action: str  # create, read, update, delete, execute
    granted: bool = True


class RolePermissions(BaseModel):
    """Role with permissions"""
    role: UserRole
    permissions: List[Permission]
    description: str


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    phone: Optional[str] = None
    department: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with _ or - allowed)')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Schema for changing user password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    phone: Optional[str]
    department: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserActivityLog(BaseModel):
    """Schema for user activity log"""
    id: int
    user_id: int
    username: str
    action: str
    resource: str
    resource_id: Optional[int]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    
    class Config:
        orm_mode = True


class UserActivityLogResponse(BaseModel):
    """Schema for user activity log response"""
    logs: List[UserActivityLog]
    total: int
    page: int
    page_size: int


class UserSettings(BaseModel):
    """Schema for user settings"""
    theme: str = "light"
    language: str = "de"
    notifications_enabled: bool = True
    email_notifications: bool = True
    timezone: str = "Europe/Berlin"
    date_format: str = "DD.MM.YYYY"
    number_format: str = "de-DE"
    
    class Config:
        orm_mode = True


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings"""
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    number_format: Optional[str] = None


class RoleCreate(BaseModel):
    """Schema for creating a custom role"""
    name: str = Field(..., min_length=3, max_length=50)
    description: str
    permissions: List[Permission]


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    permissions: Optional[List[Permission]] = None


class RoleResponse(BaseModel):
    """Schema for role response"""
    id: int
    name: str
    description: str
    permissions: List[Permission]
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
