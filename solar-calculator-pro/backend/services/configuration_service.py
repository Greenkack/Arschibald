"""
Configuration Service

This module provides comprehensive configuration management services including:
- CRUD operations for configurations
- Configuration caching with Redis/in-memory fallback
- Configuration validation against schemas
- Configuration migration between versions
- Configuration export/import (JSON, YAML, CSV)
- Configuration rollback to previous versions
"""

import json
import yaml
import csv
import io
import hashlib
import gzip
import bz2
import lzma
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status
import logging

from backend.models.configuration_models import (
    Configuration,
    ConfigurationVersion,
    ConfigurationAuditLog,
    ConfigurationBackup,
    ConfigurationValidationRule,
    ConfigurationTemplate
)
from backend.models.configuration_schemas import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigurationSearch,
    ConfigurationExport,
    ConfigurationImport,
    ConfigurationBackupCreate,
    ConfigurationRestoreRequest,
    ValidationResult,
    AuditAction,
    ChangeType,
    BackupType
)

logger = logging.getLogger(__name__)


class ConfigurationCache:
    """
    In-memory cache for configuration values.
    Falls back to Redis if available.
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._ttl_seconds = 300  # 5 minutes default TTL
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            # Check if expired
            if key in self._cache_timestamps:
                age = (datetime.now() - self._cache_timestamps[key]).total_seconds()
                if age > self._ttl_seconds:
                    # Expired, remove from cache
                    del self._cache[key]
                    del self._cache_timestamps[key]
                    return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
        if ttl:
            self._ttl_seconds = ttl
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._cache_timestamps:
            del self._cache_timestamps[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def clear_namespace(self, namespace: str):
        """Clear all cache entries for a namespace"""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{namespace}:")]
        for key in keys_to_delete:
            self.delete(key)


class ConfigurationService:
    """
    Configuration Service providing comprehensive configuration management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = ConfigurationCache()
        self.logger = logging.getLogger(__name__)
    
    # ==================== CRUD Operations ====================
    
    def create_configuration(
        self,
        config_data: ConfigurationCreate,
        user: Optional[str] = None
    ) -> Configuration:
        """
        Create a new configuration.
        
        Args:
            config_data: Configuration creation data
            user: Username for audit trail
            
        Returns:
            Created configuration
            
        Raises:
            HTTPException: If validation fails or key already exists
        """
        # Check if key already exists in namespace
        existing = self.db.query(Configuration).filter(
            and_(
                Configuration.key == config_data.key,
                Configuration.namespace == config_data.namespace,
                Configuration.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Configuration key '{config_data.key}' already exists in namespace '{config_data.namespace}'"
            )
        
        # Validate parent exists if specified
        if config_data.parent_id:
            parent = self.db.query(Configuration).filter(
                Configuration.id == config_data.parent_id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent configuration with ID {config_data.parent_id} not found"
                )
        
        # Validate value against schema if provided
        if config_data.validation_schema:
            validation_result = self._validate_value(
                config_data.value,
                config_data.validation_schema
            )
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation failed: {validation_result.errors}"
                )
        
        # Create configuration
        config = Configuration(
            **config_data.model_dump(),
            created_by=user,
            updated_by=user
        )
        
        self.db.add(config)
        self.db.flush()
        
        # Create initial version
        self._create_version(
            config.id,
            config.value,
            config.value_type,
            ChangeType.CREATED,
            "Initial creation",
            None,
            user
        )
        
        # Log audit
        self._log_audit(
            config.id,
            AuditAction.CREATE,
            user,
            None,
            config.value,
            {"key": config.key, "namespace": config.namespace}
        )
        
        self.db.commit()
        self.db.refresh(config)
        
        # Invalidate cache
        self._invalidate_cache(config.namespace, config.key)
        
        self.logger.info(f"Created configuration: {config.key} in namespace {config.namespace}")
        
        return config
    
    def get_configuration(
        self,
        config_id: int,
        use_cache: bool = True
    ) -> Optional[Configuration]:
        """
        Get configuration by ID.
        
        Args:
            config_id: Configuration ID
            use_cache: Whether to use cache
            
        Returns:
            Configuration or None if not found
        """
        # Try cache first
        if use_cache:
            cache_key = f"config:id:{config_id}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        config = self.db.query(Configuration).filter(
            Configuration.id == config_id
        ).first()
        
        if config and use_cache:
            cache_key = f"config:id:{config_id}"
            self.cache.set(cache_key, config)
        
        return config
    
    def get_configuration_by_key(
        self,
        key: str,
        namespace: str = "global",
        use_cache: bool = True
    ) -> Optional[Configuration]:
        """
        Get configuration by key and namespace.
        
        Args:
            key: Configuration key
            namespace: Configuration namespace
            use_cache: Whether to use cache
            
        Returns:
            Configuration or None if not found
        """
        # Try cache first
        if use_cache:
            cache_key = f"config:{namespace}:{key}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        config = self.db.query(Configuration).filter(
            and_(
                Configuration.key == key,
                Configuration.namespace == namespace,
                Configuration.is_active == True
            )
        ).first()
        
        if config and use_cache:
            cache_key = f"config:{namespace}:{key}"
            self.cache.set(cache_key, config)
        
        return config
    
    def get_configuration_value(
        self,
        key: str,
        namespace: str = "global",
        default: Any = None,
        use_cache: bool = True
    ) -> Any:
        """
        Get configuration value with type conversion.
        
        Args:
            key: Configuration key
            namespace: Configuration namespace
            default: Default value if not found
            use_cache: Whether to use cache
            
        Returns:
            Configuration value or default
        """
        config = self.get_configuration_by_key(key, namespace, use_cache)
        
        if not config:
            return default
        
        # Convert value based on type
        return self._convert_value(config.value, config.value_type)
    
    def update_configuration(
        self,
        config_id: int,
        update_data: ConfigurationUpdate,
        user: Optional[str] = None
    ) -> Configuration:
        """
        Update configuration.
        
        Args:
            config_id: Configuration ID
            update_data: Update data
            user: Username for audit trail
            
        Returns:
            Updated configuration
            
        Raises:
            HTTPException: If not found or validation fails
        """
        config = self.get_configuration(config_id, use_cache=False)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID {config_id} not found"
            )
        
        # Check if system configuration
        if config.is_system and update_data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate system configuration"
            )
        
        # Store old value for version tracking
        old_value = config.value
        
        # Validate new value if provided
        if update_data.value is not None:
            validation_schema = update_data.validation_schema or config.validation_schema
            if validation_schema:
                validation_result = self._validate_value(
                    update_data.value,
                    validation_schema
                )
                if not validation_result.is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Validation failed: {validation_result.errors}"
                    )
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(config, field, value)
        
        config.updated_by = user
        config.version += 1
        
        # Create version if value changed
        if update_data.value is not None and update_data.value != old_value:
            self._create_version(
                config.id,
                config.value,
                config.value_type,
                ChangeType.UPDATED,
                "Configuration updated",
                old_value,
                user
            )
        
        # Log audit
        self._log_audit(
            config.id,
            AuditAction.UPDATE,
            user,
            old_value,
            config.value,
            {"updated_fields": list(update_dict.keys())}
        )
        
        self.db.commit()
        self.db.refresh(config)
        
        # Invalidate cache
        self._invalidate_cache(config.namespace, config.key)
        
        self.logger.info(f"Updated configuration: {config.key} (version {config.version})")
        
        return config
    
    def delete_configuration(
        self,
        config_id: int,
        user: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """
        Delete configuration (soft delete by default).
        
        Args:
            config_id: Configuration ID
            user: Username for audit trail
            force: Force delete system configurations
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If not found or cannot delete
        """
        config = self.get_configuration(config_id, use_cache=False)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID {config_id} not found"
            )
        
        # Check if system configuration
        if config.is_system and not force:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system configuration without force flag"
            )
        
        # Soft delete
        old_value = config.value
        config.is_active = False
        config.updated_by = user
        
        # Create version
        self._create_version(
            config.id,
            config.value,
            config.value_type,
            ChangeType.DELETED,
            "Configuration deleted",
            old_value,
            user
        )
        
        # Log audit
        self._log_audit(
            config.id,
            AuditAction.DELETE,
            user,
            old_value,
            None,
            {"force": force}
        )
        
        self.db.commit()
        
        # Invalidate cache
        self._invalidate_cache(config.namespace, config.key)
        
        self.logger.info(f"Deleted configuration: {config.key}")
        
        return True
    
    def search_configurations(
        self,
        search_params: ConfigurationSearch
    ) -> Tuple[List[Configuration], int]:
        """
        Search configurations with filters.
        
        Args:
            search_params: Search parameters
            
        Returns:
            Tuple of (configurations, total_count)
        """
        query = self.db.query(Configuration)
        
        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Configuration.key.ilike(search_term),
                    Configuration.value.ilike(search_term),
                    Configuration.description.ilike(search_term)
                )
            )
        
        if search_params.namespace:
            query = query.filter(Configuration.namespace == search_params.namespace)
        
        if search_params.category:
            query = query.filter(Configuration.category == search_params.category)
        
        if search_params.is_active is not None:
            query = query.filter(Configuration.is_active == search_params.is_active)
        
        if search_params.is_system is not None:
            query = query.filter(Configuration.is_system == search_params.is_system)
        
        if search_params.parent_id is not None:
            query = query.filter(Configuration.parent_id == search_params.parent_id)
        
        if search_params.created_after:
            query = query.filter(Configuration.created_at >= search_params.created_after)
        
        if search_params.created_before:
            query = query.filter(Configuration.created_at <= search_params.created_before)
        
        if search_params.updated_after:
            query = query.filter(Configuration.updated_at >= search_params.updated_after)
        
        if search_params.updated_before:
            query = query.filter(Configuration.updated_at <= search_params.updated_before)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if search_params.sort_by == "key":
            sort_column = Configuration.key
        elif search_params.sort_by == "created_at":
            sort_column = Configuration.created_at
        elif search_params.sort_by == "updated_at":
            sort_column = Configuration.updated_at
        else:
            sort_column = Configuration.key
        
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        query = query.offset(search_params.offset).limit(search_params.limit)
        
        configurations = query.all()
        
        return configurations, total_count
    
    # ==================== Validation ====================
    
    def _validate_value(
        self,
        value: Any,
        validation_schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate value against JSON schema.
        
        Args:
            value: Value to validate
            validation_schema: JSON schema
            
        Returns:
            Validation result
        """
        try:
            import jsonschema
            
            # Convert value to appropriate type
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    pass
            
            jsonschema.validate(instance=value, schema=validation_schema)
            
            return ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
            
        except jsonschema.ValidationError as e:
            return ValidationResult(
                is_valid=False,
                errors=[{"message": str(e.message), "path": list(e.path)}],
                warnings=[],
                info=[]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[{"message": f"Validation error: {str(e)}"}],
                warnings=[],
                info=[]
            )
    
    # ==================== Versioning and Rollback ====================
    
    def get_configuration_versions(
        self,
        config_id: int,
        limit: int = 50
    ) -> List[ConfigurationVersion]:
        """
        Get version history for configuration.
        
        Args:
            config_id: Configuration ID
            limit: Maximum number of versions to return
            
        Returns:
            List of versions
        """
        versions = self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config_id
        ).order_by(desc(ConfigurationVersion.version_number)).limit(limit).all()
        
        return versions
    
    def rollback_configuration(
        self,
        config_id: int,
        version_number: int,
        user: Optional[str] = None
    ) -> Configuration:
        """
        Rollback configuration to a previous version.
        
        Args:
            config_id: Configuration ID
            version_number: Version number to rollback to
            user: Username for audit trail
            
        Returns:
            Updated configuration
            
        Raises:
            HTTPException: If not found or invalid version
        """
        config = self.get_configuration(config_id, use_cache=False)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID {config_id} not found"
            )
        
        # Get target version
        target_version = self.db.query(ConfigurationVersion).filter(
            and_(
                ConfigurationVersion.configuration_id == config_id,
                ConfigurationVersion.version_number == version_number
            )
        ).first()
        
        if not target_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found for configuration {config_id}"
            )
        
        # Store current value
        old_value = config.value
        
        # Rollback to target version
        config.value = target_version.value
        config.value_type = target_version.value_type
        config.updated_by = user
        config.version += 1
        
        # Create new version for rollback
        self._create_version(
            config.id,
            config.value,
            config.value_type,
            ChangeType.RESTORED,
            f"Rolled back to version {version_number}",
            old_value,
            user
        )
        
        # Log audit
        self._log_audit(
            config.id,
            AuditAction.UPDATE,
            user,
            old_value,
            config.value,
            {"action": "rollback", "target_version": version_number}
        )
        
        self.db.commit()
        self.db.refresh(config)
        
        # Invalidate cache
        self._invalidate_cache(config.namespace, config.key)
        
        self.logger.info(f"Rolled back configuration {config.key} to version {version_number}")
        
        return config
    
    def _create_version(
        self,
        config_id: int,
        value: str,
        value_type: str,
        change_type: ChangeType,
        description: str,
        previous_value: Optional[str],
        user: Optional[str]
    ):
        """Create configuration version"""
        # Get current version number
        latest_version = self.db.query(func.max(ConfigurationVersion.version_number)).filter(
            ConfigurationVersion.configuration_id == config_id
        ).scalar() or 0
        
        version = ConfigurationVersion(
            configuration_id=config_id,
            version_number=latest_version + 1,
            value=value,
            value_type=value_type,
            change_type=change_type,
            change_description=description,
            previous_value=previous_value,
            created_by=user
        )
        
        self.db.add(version)
    
    # ==================== Backup and Restore ====================
    
    def create_backup(
        self,
        backup_data: ConfigurationBackupCreate,
        user: Optional[str] = None
    ) -> ConfigurationBackup:
        """
        Create configuration backup.
        
        Args:
            backup_data: Backup creation data
            user: Username for audit trail
            
        Returns:
            Created backup
        """
        # Query configurations to backup
        query = self.db.query(Configuration).filter(Configuration.is_active == True)
        
        # Apply filters
        if backup_data.namespace_filter:
            query = query.filter(Configuration.namespace.in_(backup_data.namespace_filter))
        
        if backup_data.category_filter:
            query = query.filter(Configuration.category.in_(backup_data.category_filter))
        
        configurations = query.all()
        
        # Serialize configurations
        config_data = {
            "timestamp": datetime.now().isoformat(),
            "configurations": [
                {
                    "key": c.key,
                    "value": c.value,
                    "value_type": c.value_type,
                    "description": c.description,
                    "category": c.category,
                    "namespace": c.namespace,
                    "parent_id": c.parent_id,
                    "validation_schema": c.validation_schema,
                    "is_required": c.is_required,
                    "default_value": c.default_value
                }
                for c in configurations
            ]
        }
        
        # Compress if requested
        data_json = json.dumps(config_data, indent=2)
        data_bytes = data_json.encode('utf-8')
        
        if backup_data.is_compressed:
            data_bytes = gzip.compress(data_bytes)
            compression_algorithm = "gzip"
        else:
            compression_algorithm = None
        
        # Calculate checksum
        checksum = hashlib.sha256(data_bytes).hexdigest()
        
        # Calculate expiration
        expires_at = None
        if backup_data.retention_days:
            expires_at = datetime.now() + timedelta(days=backup_data.retention_days)
        
        # Create backup record
        backup = ConfigurationBackup(
            backup_name=backup_data.backup_name,
            backup_type=backup_data.backup_type,
            description=backup_data.description,
            configuration_data=config_data,
            configuration_count=len(configurations),
            is_compressed=backup_data.is_compressed,
            is_encrypted=backup_data.is_encrypted,
            compression_algorithm=compression_algorithm,
            file_size_bytes=len(data_bytes),
            checksum=checksum,
            status="completed",
            retention_days=backup_data.retention_days,
            expires_at=expires_at,
            created_by=user
        )
        
        self.db.add(backup)
        self.db.commit()
        self.db.refresh(backup)
        
        self.logger.info(f"Created backup: {backup.backup_name} with {len(configurations)} configurations")
        
        return backup
    
    def restore_backup(
        self,
        restore_request: ConfigurationRestoreRequest,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore configuration from backup.
        
        Args:
            restore_request: Restore request data
            user: Username for audit trail
            
        Returns:
            Restore result with statistics
            
        Raises:
            HTTPException: If backup not found
        """
        backup = self.db.query(ConfigurationBackup).filter(
            ConfigurationBackup.id == restore_request.backup_id
        ).first()
        
        if not backup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backup with ID {restore_request.backup_id} not found"
            )
        
        # Extract configurations from backup
        backup_configs = backup.configuration_data.get("configurations", [])
        
        # Apply filters
        if restore_request.namespace_filter:
            backup_configs = [
                c for c in backup_configs
                if c["namespace"] in restore_request.namespace_filter
            ]
        
        if restore_request.category_filter:
            backup_configs = [
                c for c in backup_configs
                if c["category"] in restore_request.category_filter
            ]
        
        # Statistics
        stats = {
            "total": len(backup_configs),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Dry run mode
        if restore_request.dry_run:
            for config_data in backup_configs:
                existing = self.get_configuration_by_key(
                    config_data["key"],
                    config_data["namespace"],
                    use_cache=False
                )
                if existing:
                    stats["updated"] += 1
                else:
                    stats["created"] += 1
            
            return stats
        
        # Actual restore
        for config_data in backup_configs:
            try:
                existing = self.get_configuration_by_key(
                    config_data["key"],
                    config_data["namespace"],
                    use_cache=False
                )
                
                if existing:
                    # Update mode
                    if restore_request.restore_mode == "merge":
                        # Only update if backup value is different
                        if existing.value != config_data["value"]:
                            update_data = ConfigurationUpdate(
                                value=config_data["value"],
                                description=config_data.get("description")
                            )
                            self.update_configuration(existing.id, update_data, user)
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    elif restore_request.restore_mode == "replace":
                        # Always update
                        update_data = ConfigurationUpdate(
                            value=config_data["value"],
                            description=config_data.get("description")
                        )
                        self.update_configuration(existing.id, update_data, user)
                        stats["updated"] += 1
                    else:  # skip
                        stats["skipped"] += 1
                else:
                    # Create new
                    create_data = ConfigurationCreate(**config_data)
                    self.create_configuration(create_data, user)
                    stats["created"] += 1
                    
            except Exception as e:
                stats["errors"].append({
                    "key": config_data["key"],
                    "error": str(e)
                })
        
        # Update backup restore tracking
        backup.restored_at = datetime.now()
        backup.restored_by = user
        backup.restore_count += 1
        self.db.commit()
        
        # Clear cache
        self.cache.clear()
        
        self.logger.info(f"Restored backup: {backup.backup_name} - {stats}")
        
        return stats
    
    # ==================== Export/Import ====================
    
    def export_configurations(
        self,
        export_params: ConfigurationExport,
        user: Optional[str] = None
    ) -> str:
        """
        Export configurations to JSON, YAML, or CSV.
        
        Args:
            export_params: Export parameters
            user: Username for audit trail
            
        Returns:
            Exported data as string
        """
        # Query configurations
        query = self.db.query(Configuration).filter(Configuration.is_active == True)
        
        # Apply filters
        if export_params.namespace_filter:
            query = query.filter(Configuration.namespace.in_(export_params.namespace_filter))
        
        if export_params.category_filter:
            query = query.filter(Configuration.category.in_(export_params.category_filter))
        
        configurations = query.all()
        
        # Prepare data
        export_data = []
        for config in configurations:
            config_dict = {
                "key": config.key,
                "value": config.value,
                "value_type": config.value_type,
                "description": config.description,
                "category": config.category,
                "namespace": config.namespace,
                "version": config.version,
                "is_required": config.is_required,
                "default_value": config.default_value
            }
            
            # Include versions if requested
            if export_params.include_versions:
                versions = self.get_configuration_versions(config.id)
                config_dict["versions"] = [
                    {
                        "version_number": v.version_number,
                        "value": v.value,
                        "change_type": v.change_type,
                        "created_at": v.created_at.isoformat()
                    }
                    for v in versions
                ]
            
            export_data.append(config_dict)
        
        # Format output
        if export_params.format == "json":
            output = json.dumps(export_data, indent=2)
        elif export_params.format == "yaml":
            output = yaml.dump(export_data, default_flow_style=False)
        elif export_params.format == "csv":
            output_io = io.StringIO()
            if export_data:
                fieldnames = list(export_data[0].keys())
                writer = csv.DictWriter(output_io, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)
            output = output_io.getvalue()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {export_params.format}"
            )
        
        # Log audit
        self._log_audit(
            None,
            AuditAction.EXPORT,
            user,
            None,
            None,
            {
                "format": export_params.format,
                "count": len(configurations),
                "namespaces": export_params.namespace_filter,
                "categories": export_params.category_filter
            }
        )
        
        self.logger.info(f"Exported {len(configurations)} configurations in {export_params.format} format")
        
        return output
    
    def import_configurations(
        self,
        import_params: ConfigurationImport,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import configurations from JSON, YAML, or CSV.
        
        Args:
            import_params: Import parameters
            user: Username for audit trail
            
        Returns:
            Import result with statistics
        """
        # Parse data
        try:
            if import_params.format == "json":
                import_data = json.loads(import_params.data)
            elif import_params.format == "yaml":
                import_data = yaml.safe_load(import_params.data)
            elif import_params.format == "csv":
                reader = csv.DictReader(io.StringIO(import_params.data))
                import_data = list(reader)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported import format: {import_params.format}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse import data: {str(e)}"
            )
        
        # Ensure import_data is a list
        if not isinstance(import_data, list):
            import_data = [import_data]
        
        # Statistics
        stats = {
            "total": len(import_data),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
        
        # Validate before import if requested
        if import_params.validate_before_import:
            for config_data in import_data:
                if not all(k in config_data for k in ["key", "namespace"]):
                    stats["errors"].append({
                        "data": config_data,
                        "error": "Missing required fields: key, namespace"
                    })
        
        # Dry run mode
        if import_params.dry_run:
            for config_data in import_data:
                if "key" not in config_data or "namespace" not in config_data:
                    stats["errors"].append({
                        "data": config_data,
                        "error": "Missing required fields"
                    })
                    continue
                
                existing = self.get_configuration_by_key(
                    config_data["key"],
                    config_data["namespace"],
                    use_cache=False
                )
                if existing:
                    stats["updated"] += 1
                else:
                    stats["created"] += 1
            
            return stats
        
        # Actual import
        for config_data in import_data:
            try:
                if "key" not in config_data or "namespace" not in config_data:
                    stats["errors"].append({
                        "data": config_data,
                        "error": "Missing required fields"
                    })
                    continue
                
                existing = self.get_configuration_by_key(
                    config_data["key"],
                    config_data["namespace"],
                    use_cache=False
                )
                
                if existing:
                    # Update mode
                    if import_params.merge_mode == "merge":
                        # Only update if value is different
                        if existing.value != config_data.get("value"):
                            update_data = ConfigurationUpdate(
                                value=config_data.get("value"),
                                description=config_data.get("description")
                            )
                            self.update_configuration(existing.id, update_data, user)
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    elif import_params.merge_mode == "replace":
                        # Always update
                        update_data = ConfigurationUpdate(
                            value=config_data.get("value"),
                            description=config_data.get("description")
                        )
                        self.update_configuration(existing.id, update_data, user)
                        stats["updated"] += 1
                    else:  # skip
                        stats["skipped"] += 1
                else:
                    # Create new
                    create_data = ConfigurationCreate(
                        key=config_data["key"],
                        value=config_data.get("value"),
                        value_type=config_data.get("value_type", "string"),
                        description=config_data.get("description"),
                        category=config_data.get("category", "user"),
                        namespace=config_data["namespace"]
                    )
                    self.create_configuration(create_data, user)
                    stats["created"] += 1
                    
            except Exception as e:
                stats["errors"].append({
                    "key": config_data.get("key"),
                    "error": str(e)
                })
        
        # Log audit
        self._log_audit(
            None,
            AuditAction.IMPORT,
            user,
            None,
            None,
            {
                "format": import_params.format,
                "merge_mode": import_params.merge_mode,
                "stats": stats
            }
        )
        
        # Clear cache
        self.cache.clear()
        
        self.logger.info(f"Imported configurations - {stats}")
        
        return stats
    
    # ==================== Migration ====================
    
    def migrate_configuration(
        self,
        from_namespace: str,
        to_namespace: str,
        key_mapping: Optional[Dict[str, str]] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate configurations from one namespace to another.
        
        Args:
            from_namespace: Source namespace
            to_namespace: Target namespace
            key_mapping: Optional key renaming map
            user: Username for audit trail
            
        Returns:
            Migration result with statistics
        """
        # Get source configurations
        source_configs = self.db.query(Configuration).filter(
            and_(
                Configuration.namespace == from_namespace,
                Configuration.is_active == True
            )
        ).all()
        
        stats = {
            "total": len(source_configs),
            "migrated": 0,
            "skipped": 0,
            "errors": []
        }
        
        for config in source_configs:
            try:
                # Determine new key
                new_key = config.key
                if key_mapping and config.key in key_mapping:
                    new_key = key_mapping[config.key]
                
                # Check if already exists in target namespace
                existing = self.get_configuration_by_key(
                    new_key,
                    to_namespace,
                    use_cache=False
                )
                
                if existing:
                    stats["skipped"] += 1
                    continue
                
                # Create in new namespace
                create_data = ConfigurationCreate(
                    key=new_key,
                    value=config.value,
                    value_type=config.value_type,
                    description=config.description,
                    category=config.category,
                    namespace=to_namespace,
                    validation_schema=config.validation_schema,
                    is_required=config.is_required,
                    default_value=config.default_value
                )
                
                self.create_configuration(create_data, user)
                stats["migrated"] += 1
                
            except Exception as e:
                stats["errors"].append({
                    "key": config.key,
                    "error": str(e)
                })
        
        self.logger.info(f"Migrated {stats['migrated']} configurations from {from_namespace} to {to_namespace}")
        
        return stats
    
    # ==================== Helper Methods ====================
    
    def _convert_value(self, value: str, value_type: str) -> Any:
        """Convert string value to appropriate type"""
        if value is None:
            return None
        
        try:
            if value_type == "number":
                return float(value)
            elif value_type == "boolean":
                return value.lower() in ("true", "1", "yes", "on")
            elif value_type == "json":
                return json.loads(value)
            elif value_type == "array":
                return json.loads(value) if isinstance(value, str) else value
            else:  # string
                return value
        except:
            return value
    
    def _invalidate_cache(self, namespace: str, key: str):
        """Invalidate cache for configuration"""
        self.cache.delete(f"config:{namespace}:{key}")
        self.cache.clear_namespace(namespace)
    
    def _log_audit(
        self,
        config_id: Optional[int],
        action: AuditAction,
        user: Optional[str],
        old_value: Optional[str],
        new_value: Optional[str],
        details: Optional[Dict[str, Any]] = None
    ):
        """Log audit entry"""
        audit_log = ConfigurationAuditLog(
            configuration_id=config_id,
            action=action,
            action_details=details,
            username=user,
            old_value=old_value,
            new_value=new_value,
            status="success"
        )
        
        self.db.add(audit_log)
