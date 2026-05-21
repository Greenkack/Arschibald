"""
Configuration Pydantic Schemas

This module defines the Pydantic schemas for configuration API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ValueType(str, Enum):
    """Configuration value types"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"


class ConfigCategory(str, Enum):
    """Configuration categories"""
    SYSTEM = "system"
    USER = "user"
    MODULE = "module"
    FEATURE = "feature"


class ChangeType(str, Enum):
    """Configuration change types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESTORED = "restored"


class AuditAction(str, Enum):
    """Audit log actions"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    RESTORE = "restore"


class BackupType(str, Enum):
    """Backup types"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"


class ValidationSeverity(str, Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Configuration Schemas

class ConfigurationBase(BaseModel):
    """Base configuration schema"""
    key: str = Field(..., min_length=1, max_length=255, description="Configuration key")
    value: Optional[str] = Field(None, description="Configuration value")
    value_type: ValueType = Field(ValueType.STRING, description="Value data type")
    description: Optional[str] = Field(None, description="Configuration description")
    category: ConfigCategory = Field(..., description="Configuration category")
    namespace: str = Field("global", min_length=1, max_length=100, description="Configuration namespace")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate key format"""
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError('Key must contain only alphanumeric characters, underscores, dots, and hyphens')
        return v


class ConfigurationCreate(ConfigurationBase):
    """Schema for creating configuration"""
    parent_id: Optional[int] = Field(None, description="Parent configuration ID for inheritance")
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for validation")
    is_required: bool = Field(False, description="Whether configuration is required")
    default_value: Optional[str] = Field(None, description="Default value")
    is_encrypted: bool = Field(False, description="Whether value should be encrypted")
    is_sensitive: bool = Field(False, description="Whether to hide in UI")


class ConfigurationUpdate(BaseModel):
    """Schema for updating configuration"""
    value: Optional[str] = None
    description: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigurationResponse(ConfigurationBase):
    """Schema for configuration response"""
    id: int
    parent_id: Optional[int]
    version: int
    is_active: bool
    validation_schema: Optional[Dict[str, Any]]
    is_required: bool
    default_value: Optional[str]
    is_system: bool
    is_encrypted: bool
    is_sensitive: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True


class ConfigurationWithChildren(ConfigurationResponse):
    """Schema for configuration with children"""
    children: List[ConfigurationResponse] = []


# Version Schemas

class ConfigurationVersionBase(BaseModel):
    """Base version schema"""
    version_number: int
    value: Optional[str]
    value_type: ValueType
    change_type: ChangeType
    change_description: Optional[str]
    previous_value: Optional[str]


class ConfigurationVersionResponse(ConfigurationVersionBase):
    """Schema for version response"""
    id: int
    configuration_id: int
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# Audit Log Schemas

class ConfigurationAuditLogBase(BaseModel):
    """Base audit log schema"""
    action: AuditAction
    action_details: Optional[Dict[str, Any]]
    old_value: Optional[str]
    new_value: Optional[str]


class ConfigurationAuditLogResponse(ConfigurationAuditLogBase):
    """Schema for audit log response"""
    id: int
    configuration_id: Optional[int]
    user_id: Optional[int]
    username: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    error_message: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Backup Schemas

class ConfigurationBackupCreate(BaseModel):
    """Schema for creating backup"""
    backup_name: str = Field(..., min_length=1, max_length=255)
    backup_type: BackupType = Field(BackupType.MANUAL)
    description: Optional[str] = None
    is_compressed: bool = Field(True)
    is_encrypted: bool = Field(False)
    retention_days: Optional[int] = Field(None, ge=1, le=3650)
    namespace_filter: Optional[List[str]] = Field(None, description="Filter by namespaces")
    category_filter: Optional[List[str]] = Field(None, description="Filter by categories")


class ConfigurationBackupResponse(BaseModel):
    """Schema for backup response"""
    id: int
    backup_name: str
    backup_type: BackupType
    description: Optional[str]
    configuration_count: int
    is_compressed: bool
    is_encrypted: bool
    compression_algorithm: Optional[str]
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    checksum: Optional[str]
    status: str
    error_message: Optional[str]
    retention_days: Optional[int]
    expires_at: Optional[datetime]
    created_at: datetime
    created_by: Optional[str]
    restored_at: Optional[datetime]
    restored_by: Optional[str]
    restore_count: int
    
    class Config:
        from_attributes = True


class ConfigurationRestoreRequest(BaseModel):
    """Schema for restore request"""
    backup_id: int
    restore_mode: str = Field("merge", description="merge, replace, or selective")
    namespace_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    dry_run: bool = Field(False, description="Preview changes without applying")


# Validation Rule Schemas

class ConfigurationValidationRuleBase(BaseModel):
    """Base validation rule schema"""
    rule_name: str = Field(..., min_length=1, max_length=255)
    rule_type: str = Field(..., description="schema, regex, range, enum, custom")
    description: Optional[str]
    rule_definition: Dict[str, Any]
    error_message: Optional[str]
    applies_to_namespace: Optional[str]
    applies_to_category: Optional[str]
    applies_to_key_pattern: Optional[str]
    severity: ValidationSeverity = Field(ValidationSeverity.ERROR)


class ConfigurationValidationRuleCreate(ConfigurationValidationRuleBase):
    """Schema for creating validation rule"""
    pass


class ConfigurationValidationRuleUpdate(BaseModel):
    """Schema for updating validation rule"""
    description: Optional[str] = None
    rule_definition: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    is_active: Optional[bool] = None
    severity: Optional[ValidationSeverity] = None


class ConfigurationValidationRuleResponse(ConfigurationValidationRuleBase):
    """Schema for validation rule response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ValidationResult(BaseModel):
    """Schema for validation result"""
    is_valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    info: List[Dict[str, Any]] = []


# Template Schemas

class ConfigurationTemplateBase(BaseModel):
    """Base template schema"""
    template_name: str = Field(..., min_length=1, max_length=255)
    template_type: str = Field(..., description="system, module, feature, custom")
    description: Optional[str]
    configuration_data: Dict[str, Any]
    category: Optional[str]
    tags: Optional[List[str]]


class ConfigurationTemplateCreate(ConfigurationTemplateBase):
    """Schema for creating template"""
    pass


class ConfigurationTemplateUpdate(BaseModel):
    """Schema for updating template"""
    description: Optional[str] = None
    configuration_data: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ConfigurationTemplateResponse(ConfigurationTemplateBase):
    """Schema for template response"""
    id: int
    usage_count: int
    last_used_at: Optional[datetime]
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ConfigurationTemplateApply(BaseModel):
    """Schema for applying template"""
    template_id: int
    namespace: str = Field("global")
    overrides: Optional[Dict[str, Any]] = Field(None, description="Override template values")
    merge_mode: str = Field("replace", description="replace or merge")


# Bulk Operations

class ConfigurationBulkCreate(BaseModel):
    """Schema for bulk create"""
    configurations: List[ConfigurationCreate]
    stop_on_error: bool = Field(True)


class ConfigurationBulkUpdate(BaseModel):
    """Schema for bulk update"""
    updates: List[Dict[str, Any]]  # List of {id, ...update_fields}
    stop_on_error: bool = Field(True)


class ConfigurationBulkDelete(BaseModel):
    """Schema for bulk delete"""
    ids: List[int]
    force: bool = Field(False, description="Force delete system configurations")


# Export/Import Schemas

class ConfigurationExport(BaseModel):
    """Schema for export request"""
    namespace_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    include_versions: bool = Field(False)
    include_audit_logs: bool = Field(False)
    format: str = Field("json", description="json, yaml, or csv")


class ConfigurationImport(BaseModel):
    """Schema for import request"""
    data: str = Field(..., description="Configuration data to import")
    format: str = Field("json", description="json, yaml, or csv")
    merge_mode: str = Field("merge", description="merge, replace, or skip")
    validate_before_import: bool = Field(True)
    dry_run: bool = Field(False)


# Search and Filter Schemas

class ConfigurationSearch(BaseModel):
    """Schema for configuration search"""
    query: Optional[str] = Field(None, description="Search in key, value, description")
    namespace: Optional[str] = None
    category: Optional[ConfigCategory] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None
    parent_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    sort_by: str = Field("key", description="key, created_at, updated_at")
    sort_order: str = Field("asc", description="asc or desc")


# Statistics Schemas

class ConfigurationStatistics(BaseModel):
    """Schema for configuration statistics"""
    total_configurations: int
    active_configurations: int
    inactive_configurations: int
    by_namespace: Dict[str, int]
    by_category: Dict[str, int]
    by_value_type: Dict[str, int]
    system_configurations: int
    user_configurations: int
    total_versions: int
    total_backups: int
    last_backup_at: Optional[datetime]
    last_modified_at: Optional[datetime]
