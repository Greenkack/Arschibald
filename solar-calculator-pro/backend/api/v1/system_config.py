# System Configuration API Endpoints

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.services.system_config_service import SystemConfigService
from backend.models.system_config_schemas import (
    SystemConfigurationCreate,
    SystemConfigurationUpdate,
    SystemConfigurationResponse,
    ModuleConfigurationCreate,
    ModuleConfigurationUpdate,
    ModuleConfigurationResponse,
    ConfigurationTemplateCreate,
    ConfigurationTemplateUpdate,
    ConfigurationTemplateResponse,
    ConfigurationVersionResponse,
    ConfigurationExport,
    ConfigurationImport,
    ConfigurationSearchRequest,
    ConfigCategory
)

router = APIRouter(prefix="/system-config", tags=["System Configuration"])


# System Configuration Endpoints

@router.post("/system", response_model=SystemConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_system_configuration(
    config: SystemConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new system configuration"""
    service = SystemConfigService(db)
    return service.create_system_config(config, user_id=current_user.get('id'))


@router.get("/system", response_model=List[SystemConfigurationResponse])
async def get_system_configurations(
    category: Optional[ConfigCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all system configurations"""
    service = SystemConfigService(db)
    return service.get_system_configs(category=category, skip=skip, limit=limit)


@router.get("/system/{config_id}", response_model=SystemConfigurationResponse)
async def get_system_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get system configuration by ID"""
    service = SystemConfigService(db)
    config = service.get_system_config(config_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config


@router.get("/system/key/{key}", response_model=SystemConfigurationResponse)
async def get_system_configuration_by_key(
    key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get system configuration by key"""
    service = SystemConfigService(db)
    config = service.get_system_config_by_key(key)
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config


@router.put("/system/{config_id}", response_model=SystemConfigurationResponse)
async def update_system_configuration(
    config_id: int,
    config_update: SystemConfigurationUpdate,
    change_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update system configuration"""
    service = SystemConfigService(db)
    return service.update_system_config(
        config_id,
        config_update,
        user_id=current_user.get('id'),
        change_reason=change_reason
    )


@router.delete("/system/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete system configuration"""
    service = SystemConfigService(db)
    service.delete_system_config(config_id)


# Module Configuration Endpoints

@router.post("/module", response_model=ModuleConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_module_configuration(
    config: ModuleConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new module configuration"""
    service = SystemConfigService(db)
    return service.create_module_config(config)


@router.get("/module", response_model=List[ModuleConfigurationResponse])
async def get_module_configurations(
    module_name: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get module configurations"""
    service = SystemConfigService(db)
    return service.get_module_configs(
        module_name=module_name,
        is_enabled=is_enabled,
        skip=skip,
        limit=limit
    )


@router.get("/module/{config_id}", response_model=ModuleConfigurationResponse)
async def get_module_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get module configuration by ID"""
    service = SystemConfigService(db)
    config = service.get_module_config(config_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Module configuration not found")
    
    return config


@router.put("/module/{config_id}", response_model=ModuleConfigurationResponse)
async def update_module_configuration(
    config_id: int,
    config_update: ModuleConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update module configuration"""
    service = SystemConfigService(db)
    return service.update_module_config(config_id, config_update)


@router.delete("/module/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete module configuration"""
    service = SystemConfigService(db)
    service.delete_module_config(config_id)


# Template Endpoints

@router.post("/template", response_model=ConfigurationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_configuration_template(
    template: ConfigurationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create configuration template"""
    service = SystemConfigService(db)
    return service.create_template(template, user_id=current_user.get('id'))


@router.get("/template", response_model=List[ConfigurationTemplateResponse])
async def get_configuration_templates(
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get configuration templates"""
    service = SystemConfigService(db)
    return service.get_templates(is_active=is_active, skip=skip, limit=limit)


@router.get("/template/{template_id}", response_model=ConfigurationTemplateResponse)
async def get_configuration_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get configuration template by ID"""
    service = SystemConfigService(db)
    template = service.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/template/{template_id}/apply")
async def apply_configuration_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply configuration template"""
    service = SystemConfigService(db)
    return service.apply_template(template_id, user_id=current_user.get('id'))


# Import/Export Endpoints

@router.get("/export", response_model=ConfigurationExport)
async def export_configuration(
    include_sensitive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export all configuration"""
    service = SystemConfigService(db)
    return service.export_configuration(include_sensitive=include_sensitive)


@router.post("/import")
async def import_configuration(
    import_data: ConfigurationImport,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Import configuration"""
    service = SystemConfigService(db)
    return service.import_configuration(import_data, user_id=current_user.get('id'))


# Search Endpoint

@router.post("/search")
async def search_configurations(
    search_request: ConfigurationSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search configurations"""
    service = SystemConfigService(db)
    return service.search_configurations(search_request)


# Version Control Endpoints

@router.get("/system/{config_id}/versions", response_model=List[ConfigurationVersionResponse])
async def get_configuration_versions(
    config_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get configuration version history"""
    service = SystemConfigService(db)
    return service.get_config_versions(config_id, limit=limit)


@router.post("/system/{config_id}/rollback/{version_number}", response_model=SystemConfigurationResponse)
async def rollback_configuration(
    config_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Rollback configuration to specific version"""
    service = SystemConfigService(db)
    return service.rollback_to_version(
        config_id,
        version_number,
        user_id=current_user.get('id')
    )
