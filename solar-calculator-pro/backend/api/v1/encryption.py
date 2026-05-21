"""
Encryption API Endpoints

Provides REST API endpoints for encryption management and operations.

Requirements: 11.3
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ...services.encryption_service import get_encryption_service, EncryptionService
from ...core.auth_dependencies import get_current_user


router = APIRouter(prefix="/encryption", tags=["encryption"])


# Request/Response Models

class EncryptFieldRequest(BaseModel):
    """Request model for encrypting a field."""
    value: str
    field_name: str


class EncryptFieldResponse(BaseModel):
    """Response model for encrypted field."""
    encrypted_value: str
    field_name: str


class DecryptFieldRequest(BaseModel):
    """Request model for decrypting a field."""
    encrypted_value: str
    field_name: str


class DecryptFieldResponse(BaseModel):
    """Response model for decrypted field."""
    decrypted_value: str
    field_name: str


class EncryptRowRequest(BaseModel):
    """Request model for encrypting a row."""
    row_data: Dict[str, Any]
    encrypted_fields: List[str]


class EncryptRowResponse(BaseModel):
    """Response model for encrypted row."""
    encrypted_row: Dict[str, Any]


class EncryptPayloadRequest(BaseModel):
    """Request model for encrypting a payload."""
    payload: Dict[str, Any]


class EncryptPayloadResponse(BaseModel):
    """Response model for encrypted payload."""
    encrypted_payload: Dict[str, str]


class KeyGenerationRequest(BaseModel):
    """Request model for key generation."""
    key_name: str


class KeyGenerationResponse(BaseModel):
    """Response model for key generation."""
    key_name: str
    success: bool
    message: str


class KeyRotationRequest(BaseModel):
    """Request model for key rotation."""
    key_name: str


class KeyRotationResponse(BaseModel):
    """Response model for key rotation."""
    key_name: str
    success: bool
    message: str


class KeyListResponse(BaseModel):
    """Response model for key list."""
    keys: List[str]


class AuditLogRequest(BaseModel):
    """Request model for audit log retrieval."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    operation: Optional[str] = None
    user_id: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Response model for audit log."""
    entries: List[Dict[str, Any]]
    total_count: int


class EncryptionStatusResponse(BaseModel):
    """Response model for encryption status."""
    encryption_enabled: bool
    master_key_exists: bool
    stored_keys: List[str]
    audit_statistics: Dict[str, Any]


class EncryptionValidationResponse(BaseModel):
    """Response model for encryption validation."""
    database_encryption: bool
    file_encryption: bool
    communication_encryption: bool
    key_management: bool
    all_valid: bool


# Database Encryption Endpoints

@router.post("/database/encrypt-field", response_model=EncryptFieldResponse)
async def encrypt_database_field(
    request: EncryptFieldRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Encrypt a database field value.
    
    Requires authentication.
    """
    try:
        encrypted_value = encryption_service.encrypt_database_field(
            value=request.value,
            field_name=request.field_name,
            user_id=current_user.get('id')
        )
        return EncryptFieldResponse(
            encrypted_value=encrypted_value,
            field_name=request.field_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}"
        )


@router.post("/database/decrypt-field", response_model=DecryptFieldResponse)
async def decrypt_database_field(
    request: DecryptFieldRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Decrypt a database field value.
    
    Requires authentication.
    """
    try:
        decrypted_value = encryption_service.decrypt_database_field(
            encrypted_value=request.encrypted_value,
            field_name=request.field_name,
            user_id=current_user.get('id')
        )
        return DecryptFieldResponse(
            decrypted_value=decrypted_value,
            field_name=request.field_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption failed: {str(e)}"
        )


@router.post("/database/encrypt-row", response_model=EncryptRowResponse)
async def encrypt_database_row(
    request: EncryptRowRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Encrypt specified fields in a database row.
    
    Requires authentication.
    """
    try:
        encrypted_row = encryption_service.encrypt_database_row(
            row_data=request.row_data,
            encrypted_fields=request.encrypted_fields,
            user_id=current_user.get('id')
        )
        return EncryptRowResponse(encrypted_row=encrypted_row)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Row encryption failed: {str(e)}"
        )


@router.post("/database/decrypt-row", response_model=EncryptRowResponse)
async def decrypt_database_row(
    request: EncryptRowRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Decrypt specified fields in a database row.
    
    Requires authentication.
    """
    try:
        decrypted_row = encryption_service.decrypt_database_row(
            row_data=request.row_data,
            encrypted_fields=request.encrypted_fields,
            user_id=current_user.get('id')
        )
        return EncryptRowResponse(encrypted_row=decrypted_row)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Row decryption failed: {str(e)}"
        )


# File Encryption Endpoints

@router.post("/file/encrypt")
async def encrypt_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Encrypt an uploaded file.
    
    Requires authentication.
    Returns the encrypted file for download.
    """
    try:
        # Read file data
        file_data = await file.read()
        
        # Encrypt file data
        encrypted_data = encryption_service.encrypt_file_data(
            file_data=file_data,
            user_id=current_user.get('id')
        )
        
        # Return encrypted file
        from fastapi.responses import Response
        return Response(
            content=encrypted_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}.encrypted"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File encryption failed: {str(e)}"
        )


@router.post("/file/decrypt")
async def decrypt_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Decrypt an uploaded encrypted file.
    
    Requires authentication.
    Returns the decrypted file for download.
    """
    try:
        # Read encrypted file data
        encrypted_data = await file.read()
        
        # Decrypt file data
        decrypted_data = encryption_service.decrypt_file_data(
            encrypted_data=encrypted_data,
            user_id=current_user.get('id')
        )
        
        # Return decrypted file
        from fastapi.responses import Response
        filename = file.filename
        if filename.endswith('.encrypted'):
            filename = filename[:-10]
            
        return Response(
            content=decrypted_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File decryption failed: {str(e)}"
        )


# Communication Encryption Endpoints

@router.post("/communication/encrypt-payload", response_model=EncryptPayloadResponse)
async def encrypt_api_payload(
    request: EncryptPayloadRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Encrypt an API payload.
    
    Requires authentication.
    """
    try:
        encrypted_payload = encryption_service.encrypt_api_payload(
            payload=request.payload,
            user_id=current_user.get('id')
        )
        return EncryptPayloadResponse(encrypted_payload=encrypted_payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payload encryption failed: {str(e)}"
        )


@router.post("/communication/decrypt-payload")
async def decrypt_api_payload(
    request: EncryptPayloadRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Decrypt an API payload.
    
    Requires authentication.
    """
    try:
        decrypted_payload = encryption_service.decrypt_api_payload(
            encrypted_payload=request.payload,
            user_id=current_user.get('id')
        )
        return {"payload": decrypted_payload}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payload decryption failed: {str(e)}"
        )


# Key Management Endpoints

@router.post("/keys/generate", response_model=KeyGenerationResponse)
async def generate_encryption_key(
    request: KeyGenerationRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Generate a new encryption key.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        encryption_service.generate_key(
            key_name=request.key_name,
            user_id=current_user.get('id')
        )
        return KeyGenerationResponse(
            key_name=request.key_name,
            success=True,
            message=f"Key '{request.key_name}' generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key generation failed: {str(e)}"
        )


@router.post("/keys/rotate", response_model=KeyRotationResponse)
async def rotate_encryption_key(
    request: KeyRotationRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Rotate an encryption key.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        encryption_service.rotate_key(
            key_name=request.key_name,
            user_id=current_user.get('id')
        )
        return KeyRotationResponse(
            key_name=request.key_name,
            success=True,
            message=f"Key '{request.key_name}' rotated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key rotation failed: {str(e)}"
        )


@router.get("/keys/list", response_model=KeyListResponse)
async def list_encryption_keys(
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    List all stored encryption keys.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        keys = encryption_service.list_keys()
        return KeyListResponse(keys=keys)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list keys: {str(e)}"
        )


@router.delete("/keys/{key_name}")
async def delete_encryption_key(
    key_name: str,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Delete an encryption key.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        encryption_service.delete_key(
            key_name=key_name,
            user_id=current_user.get('id')
        )
        return {"message": f"Key '{key_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key deletion failed: {str(e)}"
        )


# Audit Endpoints

@router.post("/audit/log", response_model=AuditLogResponse)
async def get_encryption_audit_log(
    request: AuditLogRequest,
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Retrieve encryption audit log.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        entries = encryption_service.get_audit_log(
            start_date=request.start_date,
            end_date=request.end_date,
            operation=request.operation,
            user_id=request.user_id
        )
        return AuditLogResponse(
            entries=entries,
            total_count=len(entries)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit log: {str(e)}"
        )


@router.get("/audit/statistics")
async def get_encryption_statistics(
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Get encryption operation statistics.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        statistics = encryption_service.get_audit_statistics()
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


# Status and Validation Endpoints

@router.get("/status", response_model=EncryptionStatusResponse)
async def get_encryption_status(
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Get current encryption system status.
    
    Requires authentication.
    """
    try:
        status_info = encryption_service.get_encryption_status()
        return EncryptionStatusResponse(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )


@router.get("/validate", response_model=EncryptionValidationResponse)
async def validate_encryption_system(
    current_user: dict = Depends(get_current_user),
    encryption_service: EncryptionService = Depends(get_encryption_service)
):
    """
    Validate encryption system functionality.
    
    Requires authentication and admin role.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        validation_results = encryption_service.validate_encryption()
        all_valid = all(validation_results.values())
        return EncryptionValidationResponse(
            **validation_results,
            all_valid=all_valid
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
