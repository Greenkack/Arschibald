"""
Encryption Pydantic Schemas

Request/Response models for encryption API endpoints.

Requirements: 11.3
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Encryption Settings Schemas

class EncryptionSettingBase(BaseModel):
    """Base schema for encryption settings."""
    setting_key: str = Field(..., description="Unique setting key")
    setting_value: str = Field(..., description="Setting value")
    description: Optional[str] = Field(None, description="Setting description")
    is_active: bool = Field(True, description="Whether setting is active")


class EncryptionSettingCreate(EncryptionSettingBase):
    """Schema for creating encryption settings."""
    pass


class EncryptionSettingUpdate(BaseModel):
    """Schema for updating encryption settings."""
    setting_value: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EncryptionSettingResponse(EncryptionSettingBase):
    """Schema for encryption setting response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Encrypted Field Schemas

class EncryptedFieldBase(BaseModel):
    """Base schema for encrypted fields."""
    table_name: str = Field(..., description="Database table name")
    field_name: str = Field(..., description="Field name")
    encryption_algorithm: str = Field("Fernet", description="Encryption algorithm")
    key_name: str = Field(..., description="Encryption key name")
    is_active: bool = Field(True, description="Whether encryption is active")


class EncryptedFieldCreate(EncryptedFieldBase):
    """Schema for registering encrypted fields."""
    pass


class EncryptedFieldUpdate(BaseModel):
    """Schema for updating encrypted field configuration."""
    encryption_algorithm: Optional[str] = None
    key_name: Optional[str] = None
    is_active: Optional[bool] = None


class EncryptedFieldResponse(EncryptedFieldBase):
    """Schema for encrypted field response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Encryption Key Schemas

class EncryptionKeyBase(BaseModel):
    """Base schema for encryption keys."""
    key_name: str = Field(..., description="Unique key name")
    key_type: str = Field("symmetric", description="Key type (symmetric/asymmetric)")
    algorithm: str = Field("Fernet", description="Encryption algorithm")
    purpose: Optional[str] = Field(None, description="Key purpose (database/file/communication)")
    rotation_schedule: Optional[str] = Field(None, description="Rotation schedule")


class EncryptionKeyCreate(EncryptionKeyBase):
    """Schema for creating encryption key metadata."""
    pass


class EncryptionKeyUpdate(BaseModel):
    """Schema for updating encryption key metadata."""
    purpose: Optional[str] = None
    rotation_schedule: Optional[str] = None
    is_active: Optional[bool] = None


class EncryptionKeyResponse(EncryptionKeyBase):
    """Schema for encryption key response."""
    id: int
    is_active: bool
    created_at: datetime
    last_rotated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Encryption Audit Log Schemas

class EncryptionAuditLogBase(BaseModel):
    """Base schema for encryption audit logs."""
    operation: str = Field(..., description="Operation type")
    data_type: str = Field(..., description="Data type (database/file/communication)")
    user_id: Optional[str] = Field(None, description="User ID")
    success: bool = Field(True, description="Whether operation succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class EncryptionAuditLogCreate(EncryptionAuditLogBase):
    """Schema for creating audit log entries."""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class EncryptionAuditLogResponse(EncryptionAuditLogBase):
    """Schema for audit log response."""
    id: int
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    class Config:
        from_attributes = True


class EncryptionAuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    operation: Optional[str] = None
    data_type: Optional[str] = None
    user_id: Optional[str] = None
    success: Optional[bool] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# Encryption Policy Schemas

class EncryptionPolicyBase(BaseModel):
    """Base schema for encryption policies."""
    policy_name: str = Field(..., description="Unique policy name")
    description: Optional[str] = Field(None, description="Policy description")
    data_classification: str = Field(..., description="Data classification level")
    encryption_required: bool = Field(True, description="Whether encryption is required")
    encryption_algorithm: str = Field("Fernet", description="Encryption algorithm")
    key_rotation_days: int = Field(90, ge=1, description="Key rotation interval in days")
    applies_to_tables: Optional[List[str]] = Field(None, description="List of table names")
    applies_to_fields: Optional[List[str]] = Field(None, description="List of field patterns")
    is_active: bool = Field(True, description="Whether policy is active")


class EncryptionPolicyCreate(EncryptionPolicyBase):
    """Schema for creating encryption policies."""
    pass


class EncryptionPolicyUpdate(BaseModel):
    """Schema for updating encryption policies."""
    description: Optional[str] = None
    data_classification: Optional[str] = None
    encryption_required: Optional[bool] = None
    encryption_algorithm: Optional[str] = None
    key_rotation_days: Optional[int] = None
    applies_to_tables: Optional[List[str]] = None
    applies_to_fields: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EncryptionPolicyResponse(EncryptionPolicyBase):
    """Schema for encryption policy response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Encryption Operation Schemas

class EncryptDataRequest(BaseModel):
    """Schema for data encryption request."""
    data: str = Field(..., description="Data to encrypt")
    data_type: str = Field("text", description="Data type (text/json/binary)")
    key_name: Optional[str] = Field(None, description="Specific key to use")


class EncryptDataResponse(BaseModel):
    """Schema for data encryption response."""
    encrypted_data: str = Field(..., description="Encrypted data (base64 encoded)")
    encryption_algorithm: str = Field(..., description="Algorithm used")
    key_name: str = Field(..., description="Key used")


class DecryptDataRequest(BaseModel):
    """Schema for data decryption request."""
    encrypted_data: str = Field(..., description="Encrypted data (base64 encoded)")
    key_name: Optional[str] = Field(None, description="Specific key to use")


class DecryptDataResponse(BaseModel):
    """Schema for data decryption response."""
    decrypted_data: str = Field(..., description="Decrypted data")
    data_type: str = Field(..., description="Data type")


# Encryption Status Schemas

class EncryptionStatusResponse(BaseModel):
    """Schema for encryption system status."""
    encryption_enabled: bool = Field(..., description="Whether encryption is enabled")
    master_key_exists: bool = Field(..., description="Whether master key exists")
    total_keys: int = Field(..., description="Total number of keys")
    active_keys: int = Field(..., description="Number of active keys")
    encrypted_tables: int = Field(..., description="Number of tables with encrypted fields")
    encrypted_fields: int = Field(..., description="Total number of encrypted fields")
    active_policies: int = Field(..., description="Number of active policies")
    last_key_rotation: Optional[datetime] = Field(None, description="Last key rotation timestamp")


class EncryptionStatisticsResponse(BaseModel):
    """Schema for encryption statistics."""
    total_operations: int = Field(..., description="Total encryption operations")
    successful_operations: int = Field(..., description="Successful operations")
    failed_operations: int = Field(..., description="Failed operations")
    operations_by_type: Dict[str, int] = Field(..., description="Operations grouped by type")
    operations_by_data_type: Dict[str, int] = Field(..., description="Operations grouped by data type")
    operations_by_user: Dict[str, int] = Field(..., description="Operations grouped by user")
    average_operation_time: Optional[float] = Field(None, description="Average operation time in ms")


class EncryptionValidationResponse(BaseModel):
    """Schema for encryption validation results."""
    database_encryption: bool = Field(..., description="Database encryption working")
    file_encryption: bool = Field(..., description="File encryption working")
    communication_encryption: bool = Field(..., description="Communication encryption working")
    key_management: bool = Field(..., description="Key management working")
    all_valid: bool = Field(..., description="All components valid")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)


# Key Rotation Schemas

class KeyRotationRequest(BaseModel):
    """Schema for key rotation request."""
    key_name: str = Field(..., description="Key to rotate")
    force: bool = Field(False, description="Force rotation even if not scheduled")


class KeyRotationResponse(BaseModel):
    """Schema for key rotation response."""
    key_name: str = Field(..., description="Rotated key name")
    old_key_archived: bool = Field(..., description="Whether old key was archived")
    new_key_active: bool = Field(..., description="Whether new key is active")
    rotation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    affected_records: int = Field(..., description="Number of records re-encrypted")


# Bulk Encryption Schemas

class BulkEncryptionRequest(BaseModel):
    """Schema for bulk encryption request."""
    table_name: str = Field(..., description="Table to encrypt")
    fields: List[str] = Field(..., description="Fields to encrypt")
    key_name: Optional[str] = Field(None, description="Key to use")
    batch_size: int = Field(1000, ge=1, le=10000, description="Batch size")


class BulkEncryptionResponse(BaseModel):
    """Schema for bulk encryption response."""
    table_name: str = Field(..., description="Encrypted table")
    fields: List[str] = Field(..., description="Encrypted fields")
    total_records: int = Field(..., description="Total records processed")
    successful_records: int = Field(..., description="Successfully encrypted records")
    failed_records: int = Field(..., description="Failed records")
    duration_seconds: float = Field(..., description="Operation duration")
    errors: Optional[List[str]] = Field(None, description="Error messages")
