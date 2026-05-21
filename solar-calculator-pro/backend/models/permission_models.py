"""
Permission and Role Management Models

Enhanced models for granular permissions, role inheritance, and user groups
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.core.database import Base


# Association tables for many-to-many relationships
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('enhanced_roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)

group_roles = Table(
    'group_roles',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('enhanced_roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)


class PermissionAction(str, enum.Enum):
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


class PermissionResource(str, enum.Enum):
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


class Permission(Base):
    """Granular permission model"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    
    # Conditions for dynamic permission evaluation
    conditions = Column(JSON, nullable=True)  # e.g., {"owner_only": true, "department": "sales"}
    
    # Metadata
    is_system_permission = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    roles = relationship("EnhancedRole", secondary=role_permissions, back_populates="permissions")
    audit_logs = relationship("PermissionAuditLog", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class EnhancedRole(Base):
    """Enhanced role model with inheritance"""
    __tablename__ = "enhanced_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Role hierarchy
    parent_role_id = Column(Integer, ForeignKey('enhanced_roles.id', ondelete='SET NULL'), nullable=True)
    
    # Metadata
    is_system_role = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority = more permissions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    parent_role = relationship("EnhancedRole", remote_side=[id], backref="child_roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    groups = relationship("Group", secondary=group_roles, back_populates="roles")
    users = relationship("UserRoleAssignment", back_populates="role", cascade="all, delete-orphan")
    audit_logs = relationship("PermissionAuditLog", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EnhancedRole(id={self.id}, name='{self.name}', parent_id={self.parent_role_id})>"


class Group(Base):
    """User group model"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Group hierarchy
    parent_group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    parent_group = relationship("Group", remote_side=[id], backref="child_groups")
    users = relationship("User", secondary=user_groups, back_populates="groups")
    roles = relationship("EnhancedRole", secondary=group_roles, back_populates="groups")
    audit_logs = relationship("PermissionAuditLog", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', parent_id={self.parent_group_id})>"


class UserRoleAssignment(Base):
    """User role assignment with metadata"""
    __tablename__ = "user_role_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('enhanced_roles.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Assignment metadata
    assigned_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="role_assignments")
    role = relationship("EnhancedRole", back_populates="users")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    
    def __repr__(self):
        return f"<UserRoleAssignment(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"


class AccessControlList(Base):
    """Access Control List for fine-grained resource access"""
    __tablename__ = "access_control_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Subject (who)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True, index=True)
    role_id = Column(Integer, ForeignKey('enhanced_roles.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Resource (what)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Permission (how)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    
    # Access control
    allow = Column(Boolean, default=True, nullable=False)  # True = allow, False = deny
    priority = Column(Integer, default=0, nullable=False)  # Higher priority wins
    
    # Conditions
    conditions = Column(JSON, nullable=True)
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    group = relationship("Group", foreign_keys=[group_id])
    role = relationship("EnhancedRole", foreign_keys=[role_id])
    permission = relationship("Permission")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<AccessControlList(id={self.id}, resource='{self.resource_type}:{self.resource_id}', allow={self.allow})>"


class PermissionAuditLog(Base):
    """Audit log for permission changes and access attempts"""
    __tablename__ = "permission_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # What
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Permission context
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='SET NULL'), nullable=True)
    role_id = Column(Integer, ForeignKey('enhanced_roles.id', ondelete='SET NULL'), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    
    # Result
    allowed = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    permission = relationship("Permission", back_populates="audit_logs")
    role = relationship("EnhancedRole", back_populates="audit_logs")
    group = relationship("Group", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<PermissionAuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', allowed={self.allowed})>"


# Update User model to include groups relationship
from backend.models.user_models import User
User.groups = relationship("Group", secondary=user_groups, back_populates="users")
