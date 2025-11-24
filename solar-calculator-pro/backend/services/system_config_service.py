# System Configuration Service

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from backend.models.system_config_models import (
    SystemConfiguration,
    ModuleConfiguration,
    ConfigurationVersion,
    ConfigurationTemplate,
    ConfigurationValidation
)
from backend.models.system_config_schemas import (
    SystemConfigurationCreate,
    SystemConfigurationUpdate,
    ModuleConfigurationCreate,
    ModuleConfigurationUpdate,
    ConfigurationTemplateCreate,
    ConfigurationTemplateUpdate,
    ConfigurationValidationCreate,
    ConfigurationSearchRequest,
    ConfigurationExport,
    ConfigurationImport,
    ValueType,
    ValidationType
)
from backend.core.exceptions import APIError


class SystemConfigService:
    """Service for managing system configuration"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # System Configuration Methods
    
    def create_system_config(
        self,
        config: SystemConfigurationCreate,
        user_id: Optional[int] = None
    ) -> SystemConfiguration:
        """Create new system configuration"""
        # Check if key already exists
        existing = self.db.query(SystemConfiguration).filter(
            SystemConfiguration.key == config.key
        ).first()
        
        if existing:
            raise APIError(400, f"Configuration key '{config.key}' already exists")
        
        # Validate value
        self._validate_value(config.value, config.value_type)
        
        db_config = SystemConfiguration(
            **config.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def get_system_config(self, config_id: int) -> Optional[SystemConfiguration]:
        """Get system configuration by ID"""
        return self.db.query(SystemConfiguration).filter(
            SystemConfiguration.id == config_id
        ).first()
    
    def get_system_config_by_key(self, key: str) -> Optional[SystemConfiguration]:
        """Get system configuration by key"""
        return self.db.query(SystemConfiguration).filter(
            SystemConfiguration.key == key
        ).first()
    
    def get_system_configs(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SystemConfiguration]:
        """Get all system configurations"""
        query = self.db.query(SystemConfiguration)
        
        if category:
            query = query.filter(SystemConfiguration.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def update_system_config(
        self,
        config_id: int,
        config_update: SystemConfigurationUpdate,
        user_id: Optional[int] = None,
        change_reason: Optional[str] = None
    ) -> SystemConfiguration:
        """Update system configuration"""
        db_config = self.get_system_config(config_id)
        
        if not db_config:
            raise APIError(404, "Configuration not found")
        
        if db_config.is_readonly:
            raise APIError(403, "Configuration is read-only")
        
        # Store old value for versioning
        old_value = db_config.value
        
        # Update fields
        update_data = config_update.dict(exclude_unset=True)
        
        if 'value' in update_data:
            self._validate_value(update_data['value'], db_config.value_type)
        
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        db_config.updated_by = user_id
        db_config.updated_at = datetime.utcnow()
        
        # Create version record
        if 'value' in update_data and old_value != update_data['value']:
            self._create_version(
                config_id=config_id,
                old_value=old_value,
                new_value=update_data['value'],
                changed_by=user_id,
                change_reason=change_reason
            )
        
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def delete_system_config(self, config_id: int) -> bool:
        """Delete system configuration"""
        db_config = self.get_system_config(config_id)
        
        if not db_config:
            raise APIError(404, "Configuration not found")
        
        if db_config.is_readonly:
            raise APIError(403, "Configuration is read-only and cannot be deleted")
        
        self.db.delete(db_config)
        self.db.commit()
        
        return True
    
    # Module Configuration Methods
    
    def create_module_config(
        self,
        config: ModuleConfigurationCreate
    ) -> ModuleConfiguration:
        """Create new module configuration"""
        # Check if key already exists for this module
        existing = self.db.query(ModuleConfiguration).filter(
            and_(
                ModuleConfiguration.module_name == config.module_name,
                ModuleConfiguration.key == config.key
            )
        ).first()
        
        if existing:
            raise APIError(
                400,
                f"Configuration key '{config.key}' already exists for module '{config.module_name}'"
            )
        
        # Validate value
        self._validate_value(config.value, config.value_type)
        
        # Validate against rules if provided
        if config.validation_rules:
            self._validate_against_rules(config.value, config.validation_rules)
        
        db_config = ModuleConfiguration(**config.dict())
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def get_module_config(self, config_id: int) -> Optional[ModuleConfiguration]:
        """Get module configuration by ID"""
        return self.db.query(ModuleConfiguration).filter(
            ModuleConfiguration.id == config_id
        ).first()
    
    def get_module_configs(
        self,
        module_name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModuleConfiguration]:
        """Get module configurations"""
        query = self.db.query(ModuleConfiguration)
        
        if module_name:
            query = query.filter(ModuleConfiguration.module_name == module_name)
        
        if is_enabled is not None:
            query = query.filter(ModuleConfiguration.is_enabled == is_enabled)
        
        return query.offset(skip).limit(limit).all()
    
    def update_module_config(
        self,
        config_id: int,
        config_update: ModuleConfigurationUpdate
    ) -> ModuleConfiguration:
        """Update module configuration"""
        db_config = self.get_module_config(config_id)
        
        if not db_config:
            raise APIError(404, "Module configuration not found")
        
        update_data = config_update.dict(exclude_unset=True)
        
        if 'value' in update_data:
            self._validate_value(update_data['value'], db_config.value_type)
            
            # Validate against rules
            rules = update_data.get('validation_rules', db_config.validation_rules)
            if rules:
                self._validate_against_rules(update_data['value'], rules)
        
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        db_config.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_config)
        
        return db_config
    
    def delete_module_config(self, config_id: int) -> bool:
        """Delete module configuration"""
        db_config = self.get_module_config(config_id)
        
        if not db_config:
            raise APIError(404, "Module configuration not found")
        
        self.db.delete(db_config)
        self.db.commit()
        
        return True
    
    # Configuration Template Methods
    
    def create_template(
        self,
        template: ConfigurationTemplateCreate,
        user_id: Optional[int] = None
    ) -> ConfigurationTemplate:
        """Create configuration template"""
        # Check if template name already exists
        existing = self.db.query(ConfigurationTemplate).filter(
            ConfigurationTemplate.name == template.name
        ).first()
        
        if existing:
            raise APIError(400, f"Template '{template.name}' already exists")
        
        db_template = ConfigurationTemplate(
            **template.dict(),
            created_by=user_id
        )
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def get_template(self, template_id: int) -> Optional[ConfigurationTemplate]:
        """Get configuration template by ID"""
        return self.db.query(ConfigurationTemplate).filter(
            ConfigurationTemplate.id == template_id
        ).first()
    
    def get_templates(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConfigurationTemplate]:
        """Get configuration templates"""
        query = self.db.query(ConfigurationTemplate)
        
        if is_active is not None:
            query = query.filter(ConfigurationTemplate.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def apply_template(
        self,
        template_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Apply configuration template"""
        template = self.get_template(template_id)
        
        if not template:
            raise APIError(404, "Template not found")
        
        if not template.is_active:
            raise APIError(400, "Template is not active")
        
        results = {
            'applied': [],
            'failed': [],
            'skipped': []
        }
        
        template_data = template.template_data
        
        # Apply system configurations
        for config_data in template_data.get('system_configs', []):
            try:
                existing = self.get_system_config_by_key(config_data['key'])
                if existing:
                    # Update existing
                    self.update_system_config(
                        existing.id,
                        SystemConfigurationUpdate(value=config_data['value']),
                        user_id=user_id,
                        change_reason=f"Applied template: {template.name}"
                    )
                    results['applied'].append(config_data['key'])
                else:
                    # Create new
                    self.create_system_config(
                        SystemConfigurationCreate(**config_data),
                        user_id=user_id
                    )
                    results['applied'].append(config_data['key'])
            except Exception as e:
                results['failed'].append({
                    'key': config_data['key'],
                    'error': str(e)
                })
        
        # Apply module configurations
        for config_data in template_data.get('module_configs', []):
            try:
                existing = self.db.query(ModuleConfiguration).filter(
                    and_(
                        ModuleConfiguration.module_name == config_data['module_name'],
                        ModuleConfiguration.key == config_data['key']
                    )
                ).first()
                
                if existing:
                    self.update_module_config(
                        existing.id,
                        ModuleConfigurationUpdate(value=config_data['value'])
                    )
                    results['applied'].append(f"{config_data['module_name']}.{config_data['key']}")
                else:
                    self.create_module_config(ModuleConfigurationCreate(**config_data))
                    results['applied'].append(f"{config_data['module_name']}.{config_data['key']}")
            except Exception as e:
                results['failed'].append({
                    'key': f"{config_data['module_name']}.{config_data['key']}",
                    'error': str(e)
                })
        
        return results
    
    # Import/Export Methods
    
    def export_configuration(
        self,
        include_sensitive: bool = False
    ) -> ConfigurationExport:
        """Export all configuration"""
        system_configs = self.get_system_configs(limit=10000)
        module_configs = self.get_module_configs(limit=10000)
        templates = self.get_templates(limit=1000)
        
        # Filter sensitive data if needed
        if not include_sensitive:
            system_configs = [
                config for config in system_configs
                if not config.is_sensitive
            ]
        
        return ConfigurationExport(
            system_configs=system_configs,
            module_configs=module_configs,
            templates=templates,
            export_date=datetime.utcnow()
        )
    
    def import_configuration(
        self,
        import_data: ConfigurationImport,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Import configuration"""
        results = {
            'imported': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        # Import system configurations
        if import_data.system_configs:
            for config_data in import_data.system_configs:
                try:
                    existing = self.get_system_config_by_key(config_data.key)
                    
                    if existing:
                        if import_data.overwrite_existing:
                            self.update_system_config(
                                existing.id,
                                SystemConfigurationUpdate(value=config_data.value),
                                user_id=user_id
                            )
                            results['updated'] += 1
                        else:
                            results['errors'].append(f"Key '{config_data.key}' already exists")
                    else:
                        self.create_system_config(config_data, user_id=user_id)
                        results['imported'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to import '{config_data.key}': {str(e)}")
        
        # Import module configurations
        if import_data.module_configs:
            for config_data in import_data.module_configs:
                try:
                    existing = self.db.query(ModuleConfiguration).filter(
                        and_(
                            ModuleConfiguration.module_name == config_data.module_name,
                            ModuleConfiguration.key == config_data.key
                        )
                    ).first()
                    
                    if existing:
                        if import_data.overwrite_existing:
                            self.update_module_config(
                                existing.id,
                                ModuleConfigurationUpdate(value=config_data.value)
                            )
                            results['updated'] += 1
                        else:
                            results['errors'].append(
                                f"Key '{config_data.module_name}.{config_data.key}' already exists"
                            )
                    else:
                        self.create_module_config(config_data)
                        results['imported'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(
                        f"Failed to import '{config_data.module_name}.{config_data.key}': {str(e)}"
                    )
        
        # Import templates
        if import_data.templates:
            for template_data in import_data.templates:
                try:
                    existing = self.db.query(ConfigurationTemplate).filter(
                        ConfigurationTemplate.name == template_data.name
                    ).first()
                    
                    if existing:
                        if import_data.overwrite_existing:
                            for field, value in template_data.dict(exclude_unset=True).items():
                                setattr(existing, field, value)
                            existing.updated_at = datetime.utcnow()
                            self.db.commit()
                            results['updated'] += 1
                        else:
                            results['errors'].append(f"Template '{template_data.name}' already exists")
                    else:
                        self.create_template(template_data, user_id=user_id)
                        results['imported'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to import template '{template_data.name}': {str(e)}")
        
        return results
    
    # Search and Filter
    
    def search_configurations(
        self,
        search_request: ConfigurationSearchRequest
    ) -> Dict[str, List]:
        """Search configurations"""
        results = {
            'system_configs': [],
            'module_configs': []
        }
        
        # Search system configurations
        sys_query = self.db.query(SystemConfiguration)
        
        if search_request.query:
            sys_query = sys_query.filter(
                or_(
                    SystemConfiguration.key.contains(search_request.query),
                    SystemConfiguration.description.contains(search_request.query)
                )
            )
        
        if search_request.category:
            sys_query = sys_query.filter(SystemConfiguration.category == search_request.category)
        
        if search_request.is_sensitive is not None:
            sys_query = sys_query.filter(SystemConfiguration.is_sensitive == search_request.is_sensitive)
        
        if search_request.is_readonly is not None:
            sys_query = sys_query.filter(SystemConfiguration.is_readonly == search_request.is_readonly)
        
        results['system_configs'] = sys_query.all()
        
        # Search module configurations
        mod_query = self.db.query(ModuleConfiguration)
        
        if search_request.query:
            mod_query = mod_query.filter(
                or_(
                    ModuleConfiguration.key.contains(search_request.query),
                    ModuleConfiguration.description.contains(search_request.query)
                )
            )
        
        if search_request.module_name:
            mod_query = mod_query.filter(ModuleConfiguration.module_name == search_request.module_name)
        
        if search_request.is_enabled is not None:
            mod_query = mod_query.filter(ModuleConfiguration.is_enabled == search_request.is_enabled)
        
        results['module_configs'] = mod_query.all()
        
        return results
    
    # Version Control
    
    def get_config_versions(
        self,
        config_id: int,
        limit: int = 50
    ) -> List[ConfigurationVersion]:
        """Get configuration version history"""
        return self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config_id
        ).order_by(ConfigurationVersion.version_number.desc()).limit(limit).all()
    
    def rollback_to_version(
        self,
        config_id: int,
        version_number: int,
        user_id: Optional[int] = None
    ) -> SystemConfiguration:
        """Rollback configuration to specific version"""
        version = self.db.query(ConfigurationVersion).filter(
            and_(
                ConfigurationVersion.configuration_id == config_id,
                ConfigurationVersion.version_number == version_number
            )
        ).first()
        
        if not version:
            raise APIError(404, "Version not found")
        
        return self.update_system_config(
            config_id,
            SystemConfigurationUpdate(value=version.old_value or version.new_value),
            user_id=user_id,
            change_reason=f"Rollback to version {version_number}"
        )
    
    # Private Helper Methods
    
    def _validate_value(self, value: str, value_type: ValueType):
        """Validate configuration value based on type"""
        try:
            if value_type == ValueType.NUMBER:
                float(value)
            elif value_type == ValueType.BOOLEAN:
                if value.lower() not in ['true', 'false', '1', '0']:
                    raise ValueError("Invalid boolean value")
            elif value_type == ValueType.JSON:
                json.loads(value)
        except (ValueError, json.JSONDecodeError) as e:
            raise APIError(400, f"Invalid value for type {value_type}: {str(e)}")
    
    def _validate_against_rules(self, value: str, rules: Dict[str, Any]):
        """Validate value against validation rules"""
        if 'regex' in rules:
            if not re.match(rules['regex'], value):
                raise APIError(400, f"Value does not match pattern: {rules['regex']}")
        
        if 'min' in rules or 'max' in rules:
            try:
                num_value = float(value)
                if 'min' in rules and num_value < rules['min']:
                    raise APIError(400, f"Value must be at least {rules['min']}")
                if 'max' in rules and num_value > rules['max']:
                    raise APIError(400, f"Value must be at most {rules['max']}")
            except ValueError:
                raise APIError(400, "Value must be a number for min/max validation")
        
        if 'enum' in rules:
            if value not in rules['enum']:
                raise APIError(400, f"Value must be one of: {', '.join(rules['enum'])}")
    
    def _create_version(
        self,
        config_id: int,
        old_value: str,
        new_value: str,
        changed_by: Optional[int] = None,
        change_reason: Optional[str] = None
    ):
        """Create configuration version record"""
        # Get latest version number
        latest = self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config_id
        ).order_by(ConfigurationVersion.version_number.desc()).first()
        
        version_number = (latest.version_number + 1) if latest else 1
        
        version = ConfigurationVersion(
            configuration_id=config_id,
            version_number=version_number,
            old_value=old_value,
            new_value=new_value,
            change_reason=change_reason,
            changed_by=changed_by
        )
        
        self.db.add(version)
