# System Configuration Pydantic Schemas

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


class ConfigCategory(str, Enum):
    """Configuration categories"""
    GENERAL = "general"
    SECURITY = "security"
    DATABASE = "database"
    EMAIL = "email"
    BACKUP = "backup"
    LOGGING = "logging"
    PERFORMANCE = "performance"
    UI = "ui"
    API = "api"


class ValidationType(str, Enum):
    """Validation types"""
    REGEX = "regex"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"


# System Configuration Schemas

class SystemConfigurationBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    value: str
    value_type: ValueType
    category: ConfigCategory
    description: Optional[str] = None
    is_sensitive: bool = False
    is_readonly: bool = False


class SystemConfigurationCreate(SystemConfigurationBase):
    pass


class SystemConfigurationUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None


class SystemConfigurationResponse(SystemConfigurationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# Module Configuration Schemas

class ModuleConfigurationBase(BaseModel):
    module_name: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=1, max_length=255)
    value: str
    value_type: ValueType
    description: Optional[str] = None
    is_enabled: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None


class ModuleConfigurationCreate(ModuleConfigurationBase):
    pass


class ModuleConfigurationUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None


class ModuleConfigurationResponse(ModuleConfigurationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Configuration Version Schemas

class ConfigurationVersionResponse(BaseModel):
    id: int
    configuration_id: int
    version_number: int
    old_value: Optional[str] = None
    new_value: str
    change_reason: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: datetime
    
    class Config:
        from_attributes = True


# Configuration Template Schemas

class ConfigurationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_data: Dict[str, Any]
    is_active: bool = True


class ConfigurationTemplateCreate(ConfigurationTemplateBase):
    pass


class ConfigurationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConfigurationTemplateResponse(ConfigurationTemplateBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# Configuration Validation Schemas

class ConfigurationValidationBase(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=255)
    validation_type: ValidationType
    validation_rule: str
    error_message: Optional[str] = None
    is_active: bool = True


class ConfigurationValidationCreate(ConfigurationValidationBase):
    pass


class ConfigurationValidationUpdate(BaseModel):
    validation_rule: Optional[str] = None
    error_message: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigurationValidationResponse(ConfigurationValidationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bulk Operations

class ConfigurationExport(BaseModel):
    """Export configuration data"""
    system_configs: List[SystemConfigurationResponse]
    module_configs: List[ModuleConfigurationResponse]
    templates: List[ConfigurationTemplateResponse]
    export_date: datetime
    version: str = "1.0"


class ConfigurationImport(BaseModel):
    """Import configuration data"""
    system_configs: Optional[List[SystemConfigurationCreate]] = None
    module_configs: Optional[List[ModuleConfigurationCreate]] = None
    templates: Optional[List[ConfigurationTemplateCreate]] = None
    overwrite_existing: bool = False


# Search and Filter

class ConfigurationSearchRequest(BaseModel):
    """Search configuration"""
    query: Optional[str] = None
    category: Optional[ConfigCategory] = None
    module_name: Optional[str] = None
    is_sensitive: Optional[bool] = None
    is_readonly: Optional[bool] = None
    is_enabled: Optional[bool] = None


class ConfigurationBulkUpdate(BaseModel):
    """Bulk update configurations"""
    updates: List[Dict[str, Any]]
    change_reason: Optional[str] = None
