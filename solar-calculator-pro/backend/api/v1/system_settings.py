"""
System Settings API Endpoints

REST API endpoints for system settings management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from ...models.system_settings_schemas import (
    GeneralSettingsUpdate, GeneralSettingsResponse,
    EmailSettingsUpdate, EmailSettingsResponse, EmailTestRequest, EmailTestResponse,
    BackupSettingsUpdate, BackupSettingsResponse, BackupNowRequest, BackupInfo, BackupListResponse,
    LoggingSettingsUpdate, LoggingSettingsResponse, LogFilesResponse,
    SystemInfoResponse, SystemHealthResponse, SystemStatsResponse,
    AllSettingsResponse
)
from ...services.system_settings_service import SystemSettingsService

router = APIRouter(prefix="/system-settings", tags=["System Settings"])


def get_settings_service() -> SystemSettingsService:
    """Dependency to get settings service"""
    return SystemSettingsService()


# General Settings Endpoints
@router.get("/general", response_model=GeneralSettingsResponse)
async def get_general_settings(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get general system settings
    
    Returns application-wide general settings including language, currency, timezone, etc.
    """
    return service.get_general_settings()


@router.put("/general", response_model=GeneralSettingsResponse)
async def update_general_settings(
    update: GeneralSettingsUpdate,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Update general system settings
    
    Update one or more general settings. Only provided fields will be updated.
    """
    return service.update_general_settings(update)


# Email Settings Endpoints
@router.get("/email", response_model=EmailSettingsResponse)
async def get_email_settings(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get email configuration settings
    
    Returns email settings without sensitive data (passwords, API keys).
    """
    return service.get_email_settings()


@router.put("/email", response_model=EmailSettingsResponse)
async def update_email_settings(
    update: EmailSettingsUpdate,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Update email configuration settings
    
    Update email provider settings including SMTP or API credentials.
    """
    return service.update_email_settings(update)


@router.post("/email/test", response_model=EmailTestResponse)
async def test_email_configuration(
    request: EmailTestRequest,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Test email configuration
    
    Send a test email to verify email settings are working correctly.
    """
    return service.test_email(request)


# Backup Settings Endpoints
@router.get("/backup", response_model=BackupSettingsResponse)
async def get_backup_settings(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get backup configuration settings
    
    Returns backup settings including frequency, retention, and last backup info.
    """
    return service.get_backup_settings()


@router.put("/backup", response_model=BackupSettingsResponse)
async def update_backup_settings(
    update: BackupSettingsUpdate,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Update backup configuration settings
    
    Update backup settings including frequency, retention policy, and backup location.
    """
    return service.update_backup_settings(update)


@router.post("/backup/create", response_model=BackupInfo)
async def create_backup_now(
    request: BackupNowRequest,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Create a backup immediately
    
    Trigger a manual backup with specified options.
    """
    try:
        return service.create_backup(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup failed: {str(e)}"
        )


@router.get("/backup/list", response_model=BackupListResponse)
async def list_backups(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    List all available backups
    
    Returns a list of all backups with their metadata.
    """
    return service.list_backups()


# Logging Settings Endpoints
@router.get("/logging", response_model=LoggingSettingsResponse)
async def get_logging_settings(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get logging configuration settings
    
    Returns logging settings including log level, file paths, and rotation settings.
    """
    return service.get_logging_settings()


@router.put("/logging", response_model=LoggingSettingsResponse)
async def update_logging_settings(
    update: LoggingSettingsUpdate,
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Update logging configuration settings
    
    Update logging settings including log level and file management.
    """
    return service.update_logging_settings(update)


@router.get("/logging/files", response_model=LogFilesResponse)
async def list_log_files(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    List all log files
    
    Returns a list of all log files with their metadata.
    """
    return service.list_log_files()


# System Information Endpoints
@router.get("/info", response_model=SystemInfoResponse)
async def get_system_information(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get system information
    
    Returns comprehensive system information including hardware, software, and performance metrics.
    """
    return service.get_system_info()


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get system health status
    
    Returns health check results for various system components.
    """
    return service.get_system_health()


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_statistics(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get system statistics
    
    Returns usage statistics including users, projects, calculations, and API calls.
    """
    return service.get_system_stats()


# Combined Settings Endpoint
@router.get("/all", response_model=AllSettingsResponse)
async def get_all_settings(
    service: SystemSettingsService = Depends(get_settings_service)
):
    """
    Get all settings and system information
    
    Returns all settings categories and system information in a single response.
    """
    return AllSettingsResponse(
        general=service.get_general_settings(),
        email=service.get_email_settings(),
        backup=service.get_backup_settings(),
        logging=service.get_logging_settings(),
        system_info=service.get_system_info()
    )
