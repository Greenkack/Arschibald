"""
Price Matrix Version Service

This service handles all price matrix versioning operations including:
- Version creation and management
- Version comparison
- Version rollback
- Approval workflow
- Version history tracking
- Version migration
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json
import copy

from backend.models.price_matrix_version_models import (
    PriceMatrixVersion,
    PriceMatrixVersionChange,
    PriceMatrixVersionComparison
)
from backend.models.price_matrix_version_schemas import (
    PriceMatrixVersionCreate,
    PriceMatrixVersionUpdate,
    PriceMatrixVersionApprove,
    PriceMatrixVersionReject,
    PriceMatrixVersionRollback,
    PriceMatrixVersionCompare,
    VersionStatus,
    ChangeType
)


class PriceMatrixVersionService:
    """Service for managing price matrix versions"""

    def __init__(self, db: Session):
        self.db = db

    # Version CRUD Operations

    def create_version(
        self,
        data: PriceMatrixVersionCreate,
        user_id: int
    ) -> PriceMatrixVersion:
        """Create a new price matrix version"""
        # Get the next version number
        last_version = self.db.query(PriceMatrixVersion).filter(
            PriceMatrixVersion.matrix_id == data.matrix_id
        ).order_by(desc(PriceMatrixVersion.version_number)).first()
        
        next_version_number = (last_version.version_number + 1) if last_version else 1

        # Create new version
        version = PriceMatrixVersion(
            matrix_id=data.matrix_id,
            version_number=next_version_number,
            version_name=data.version_name,
            description=data.description,
            matrix_data=data.matrix_data,
            metadata=data.metadata or {},
            status=VersionStatus.DRAFT,
            created_by=user_id
        )
        
        self.db.add(version)
        self.db.flush()

        # Log the creation
        self._log_change(
            version_id=version.id,
            change_type=ChangeType.CREATED,
            change_description=f"Version {next_version_number} created",
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(version)
        return version

    def get_version(self, version_id: int) -> Optional[PriceMatrixVersion]:
        """Get a specific version by ID"""
        return self.db.query(PriceMatrixVersion).filter(
            PriceMatrixVersion.id == version_id
        ).first()

    def get_versions_by_matrix(
        self,
        matrix_id: int,
        status: Optional[VersionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[PriceMatrixVersion], int]:
        """Get all versions for a specific matrix"""
        query = self.db.query(PriceMatrixVersion).filter(
            PriceMatrixVersion.matrix_id == matrix_id
        )

        if status:
            query = query.filter(PriceMatrixVersion.status == status)

        total_count = query.count()
        versions = query.order_by(
            desc(PriceMatrixVersion.version_number)
        ).limit(limit).offset(offset).all()

        return versions, total_count

    def get_active_version(self, matrix_id: int) -> Optional[PriceMatrixVersion]:
        """Get the currently active version for a matrix"""
        return self.db.query(PriceMatrixVersion).filter(
            and_(
                PriceMatrixVersion.matrix_id == matrix_id,
                PriceMatrixVersion.is_active == True
            )
        ).first()

    def update_version(
        self,
        version_id: int,
        data: PriceMatrixVersionUpdate,
        user_id: int
    ) -> PriceMatrixVersion:
        """Update a version (only if in draft status)"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != VersionStatus.DRAFT:
            raise ValueError(f"Cannot update version in {version.status} status")

        # Track changes
        changes = []
        
        if data.version_name and data.version_name != version.version_name:
            changes.append(("version_name", version.version_name, data.version_name))
            version.version_name = data.version_name

        if data.description is not None and data.description != version.description:
            changes.append(("description", version.description, data.description))
            version.description = data.description

        if data.matrix_data:
            changes.append(("matrix_data", "updated", "updated"))
            version.matrix_data = data.matrix_data

        if data.metadata:
            version.metadata = {**(version.metadata or {}), **data.metadata}

        if data.status and data.status != version.status:
            changes.append(("status", version.status, data.status))
            version.status = data.status

        version.updated_at = datetime.utcnow()

        # Log all changes
        for field_name, old_value, new_value in changes:
            self._log_change(
                version_id=version.id,
                change_type=ChangeType.UPDATED,
                field_name=field_name,
                old_value=str(old_value),
                new_value=str(new_value),
                user_id=user_id
            )

        self.db.commit()
        self.db.refresh(version)
        return version

    def delete_version(self, version_id: int, user_id: int) -> bool:
        """Delete a version (only if in draft status)"""
        version = self.get_version(version_id)
        if not version:
            return False

        if version.status != VersionStatus.DRAFT:
            raise ValueError(f"Cannot delete version in {version.status} status")

        if version.is_active:
            raise ValueError("Cannot delete active version")

        self.db.delete(version)
        self.db.commit()
        return True

    # Approval Workflow

    def submit_for_approval(self, version_id: int, user_id: int) -> PriceMatrixVersion:
        """Submit a version for approval"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != VersionStatus.DRAFT:
            raise ValueError(f"Can only submit draft versions for approval")

        version.status = VersionStatus.PENDING
        version.updated_at = datetime.utcnow()

        self._log_change(
            version_id=version.id,
            change_type=ChangeType.UPDATED,
            change_description="Submitted for approval",
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(version)
        return version

    def approve_version(
        self,
        version_id: int,
        data: PriceMatrixVersionApprove,
        user_id: int
    ) -> PriceMatrixVersion:
        """Approve a version"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != VersionStatus.PENDING:
            raise ValueError(f"Can only approve pending versions")

        version.status = VersionStatus.APPROVED
        version.approved_by = user_id
        version.approved_at = datetime.utcnow()
        version.updated_at = datetime.utcnow()

        self._log_change(
            version_id=version.id,
            change_type=ChangeType.APPROVED,
            change_description=data.approval_notes or "Version approved",
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(version)
        return version

    def reject_version(
        self,
        version_id: int,
        data: PriceMatrixVersionReject,
        user_id: int
    ) -> PriceMatrixVersion:
        """Reject a version"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != VersionStatus.PENDING:
            raise ValueError(f"Can only reject pending versions")

        version.status = VersionStatus.REJECTED
        version.updated_at = datetime.utcnow()

        self._log_change(
            version_id=version.id,
            change_type=ChangeType.REJECTED,
            change_description=data.rejection_reason,
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(version)
        return version

    def activate_version(self, version_id: int, user_id: int) -> PriceMatrixVersion:
        """Activate a version (make it the current active version)"""
        version = self.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != VersionStatus.APPROVED:
            raise ValueError(f"Can only activate approved versions")

        # Deactivate current active version
        current_active = self.get_active_version(version.matrix_id)
        if current_active:
            current_active.is_active = False
            current_active.status = VersionStatus.ARCHIVED
            self._log_change(
                version_id=current_active.id,
                change_type=ChangeType.ARCHIVED,
                change_description="Deactivated due to new version activation",
                user_id=user_id
            )

        # Activate new version
        version.is_active = True
        version.status = VersionStatus.ACTIVE
        version.updated_at = datetime.utcnow()

        self._log_change(
            version_id=version.id,
            change_type=ChangeType.ACTIVATED,
            change_description="Version activated",
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(version)
        return version

    # Version Comparison

    def compare_versions(
        self,
        data: PriceMatrixVersionCompare,
        user_id: int
    ) -> PriceMatrixVersionComparison:
        """Compare two versions and return differences"""
        version_a = self.get_version(data.version_a_id)
        version_b = self.get_version(data.version_b_id)

        if not version_a or not version_b:
            raise ValueError("One or both versions not found")

        if version_a.matrix_id != version_b.matrix_id:
            raise ValueError("Versions must belong to the same matrix")

        # Perform comparison
        differences = self._calculate_differences(
            version_a.matrix_data,
            version_b.matrix_data,
            include_details=data.include_details
        )

        summary = self._generate_comparison_summary(differences)

        # Save comparison result
        comparison = PriceMatrixVersionComparison(
            version_a_id=data.version_a_id,
            version_b_id=data.version_b_id,
            differences=differences,
            summary=summary,
            compared_by=user_id
        )

        self.db.add(comparison)
        self.db.commit()
        self.db.refresh(comparison)
        return comparison

    def _calculate_differences(
        self,
        data_a: Dict[str, Any],
        data_b: Dict[str, Any],
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Calculate differences between two matrix data sets"""
        differences = {
            "added": [],
            "removed": [],
            "modified": [],
            "unchanged_count": 0
        }

        # Find all keys
        keys_a = set(self._flatten_dict(data_a).keys())
        keys_b = set(self._flatten_dict(data_b).keys())

        # Added keys
        added_keys = keys_b - keys_a
        for key in added_keys:
            differences["added"].append({
                "key": key,
                "new_value": self._get_nested_value(data_b, key)
            })

        # Removed keys
        removed_keys = keys_a - keys_b
        for key in removed_keys:
            differences["removed"].append({
                "key": key,
                "old_value": self._get_nested_value(data_a, key)
            })

        # Modified keys
        common_keys = keys_a & keys_b
        for key in common_keys:
            value_a = self._get_nested_value(data_a, key)
            value_b = self._get_nested_value(data_b, key)
            
            if value_a != value_b:
                differences["modified"].append({
                    "key": key,
                    "old_value": value_a,
                    "new_value": value_b
                })
            else:
                differences["unchanged_count"] += 1

        return differences

    def _generate_comparison_summary(self, differences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for comparison"""
        return {
            "total_added": len(differences["added"]),
            "total_removed": len(differences["removed"]),
            "total_modified": len(differences["modified"]),
            "total_unchanged": differences["unchanged_count"],
            "total_changes": len(differences["added"]) + len(differences["removed"]) + len(differences["modified"])
        }

    # Version Rollback

    def rollback_to_version(
        self,
        version_id: int,
        data: PriceMatrixVersionRollback,
        user_id: int
    ) -> Dict[str, Any]:
        """Rollback to a specific version"""
        target_version = self.get_version(version_id)
        if not target_version:
            raise ValueError(f"Version {version_id} not found")

        current_active = self.get_active_version(target_version.matrix_id)
        if not current_active:
            raise ValueError("No active version to rollback from")

        start_time = datetime.utcnow()

        # Create backup of current version if requested
        backup_version_id = None
        if data.create_backup:
            backup = self.create_version(
                PriceMatrixVersionCreate(
                    matrix_id=target_version.matrix_id,
                    version_name=f"Backup before rollback to v{target_version.version_number}",
                    description=f"Automatic backup created before rollback. {data.rollback_reason or ''}",
                    matrix_data=current_active.matrix_data,
                    metadata=current_active.metadata
                ),
                user_id=user_id
            )
            backup_version_id = backup.id

        # Deactivate current version
        current_active.is_active = False
        current_active.status = VersionStatus.ARCHIVED

        # Activate target version
        target_version.is_active = True
        target_version.status = VersionStatus.ACTIVE
        target_version.updated_at = datetime.utcnow()

        # Log rollback
        self._log_change(
            version_id=target_version.id,
            change_type=ChangeType.ROLLED_BACK,
            change_description=f"Rolled back from v{current_active.version_number}. {data.rollback_reason or ''}",
            user_id=user_id
        )

        self.db.commit()

        end_time = datetime.utcnow()
        rollback_time = (end_time - start_time).total_seconds()

        return {
            "success": True,
            "rolled_back_to_version": target_version.version_number,
            "previous_version": current_active.version_number,
            "backup_version_id": backup_version_id,
            "rollback_time": rollback_time
        }

    # Version History

    def get_version_history(
        self,
        matrix_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get complete version history for a matrix"""
        versions, total_count = self.get_versions_by_matrix(
            matrix_id=matrix_id,
            limit=limit,
            offset=offset
        )

        active_version = self.get_active_version(matrix_id)

        return {
            "versions": versions,
            "total_count": total_count,
            "active_version": active_version
        }

    def get_version_changes(
        self,
        version_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[PriceMatrixVersionChange], int]:
        """Get all changes for a specific version"""
        query = self.db.query(PriceMatrixVersionChange).filter(
            PriceMatrixVersionChange.version_id == version_id
        )

        total_count = query.count()
        changes = query.order_by(
            desc(PriceMatrixVersionChange.changed_at)
        ).limit(limit).offset(offset).all()

        return changes, total_count

    # Version Migration

    def migrate_version_data(
        self,
        from_version_id: int,
        to_version_id: int,
        migration_rules: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """Migrate data from one version to another using migration rules"""
        from_version = self.get_version(from_version_id)
        to_version = self.get_version(to_version_id)

        if not from_version or not to_version:
            raise ValueError("One or both versions not found")

        start_time = datetime.utcnow()
        migrated_records = 0
        errors = []
        warnings = []

        try:
            # Apply migration rules
            migrated_data = copy.deepcopy(from_version.matrix_data)
            
            for rule_name, rule_config in migration_rules.items():
                try:
                    migrated_data = self._apply_migration_rule(
                        migrated_data,
                        rule_name,
                        rule_config
                    )
                    migrated_records += 1
                except Exception as e:
                    errors.append(f"Rule '{rule_name}' failed: {str(e)}")

            # Update target version with migrated data
            to_version.matrix_data = migrated_data
            to_version.updated_at = datetime.utcnow()

            self._log_change(
                version_id=to_version.id,
                change_type=ChangeType.UPDATED,
                change_description=f"Data migrated from v{from_version.version_number}",
                user_id=user_id
            )

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            errors.append(f"Migration failed: {str(e)}")

        end_time = datetime.utcnow()
        migration_time = (end_time - start_time).total_seconds()

        return {
            "success": len(errors) == 0,
            "from_version": from_version.version_number,
            "to_version": to_version.version_number,
            "migrated_records": migrated_records,
            "errors": errors,
            "warnings": warnings,
            "migration_time": migration_time
        }

    def _apply_migration_rule(
        self,
        data: Dict[str, Any],
        rule_name: str,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a single migration rule to data"""
        rule_type = rule_config.get("type")
        
        if rule_type == "rename_key":
            old_key = rule_config["old_key"]
            new_key = rule_config["new_key"]
            if old_key in data:
                data[new_key] = data.pop(old_key)
        
        elif rule_type == "transform_value":
            key = rule_config["key"]
            transform_fn = rule_config["transform"]
            if key in data:
                data[key] = transform_fn(data[key])
        
        elif rule_type == "add_default":
            key = rule_config["key"]
            default_value = rule_config["default"]
            if key not in data:
                data[key] = default_value
        
        elif rule_type == "remove_key":
            key = rule_config["key"]
            data.pop(key, None)
        
        return data

    # Helper Methods

    def _log_change(
        self,
        version_id: int,
        change_type: ChangeType,
        user_id: int,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        change_description: Optional[str] = None
    ):
        """Log a change to a version"""
        change = PriceMatrixVersionChange(
            version_id=version_id,
            change_type=change_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            change_description=change_description,
            changed_by=user_id
        )
        self.db.add(change)

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _get_nested_value(self, d: Dict[str, Any], key: str, sep: str = '.') -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split(sep)
        value = d
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value
