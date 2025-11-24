"""
Tests for Price Matrix Versioning System

This module contains comprehensive tests for:
- Version creation and management
- Version comparison
- Version rollback
- Approval workflow
- Version history tracking
- Version migration
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.price_matrix_version_service import PriceMatrixVersionService
from backend.models.price_matrix_version_schemas import (
    PriceMatrixVersionCreate,
    PriceMatrixVersionUpdate,
    PriceMatrixVersionApprove,
    PriceMatrixVersionReject,
    PriceMatrixVersionRollback,
    PriceMatrixVersionCompare,
    VersionStatus
)


@pytest.fixture
def service(db_session: Session):
    """Create a PriceMatrixVersionService instance"""
    return PriceMatrixVersionService(db_session)


@pytest.fixture
def sample_matrix_data():
    """Sample matrix data for testing"""
    return {
        "modules": {
            "5": {"10kWh": 15000, "15kWh": 18000, "20kWh": 21000},
            "10": {"10kWh": 25000, "15kWh": 28000, "20kWh": 31000},
            "15": {"10kWh": 35000, "15kWh": 38000, "20kWh": 41000}
        },
        "metadata": {
            "currency": "EUR",
            "last_updated": "2024-01-01"
        }
    }


@pytest.fixture
def sample_version(service, sample_matrix_data):
    """Create a sample version for testing"""
    data = PriceMatrixVersionCreate(
        matrix_id=1,
        version_name="Test Version 1.0",
        description="Initial test version",
        matrix_data=sample_matrix_data,
        metadata={"test": True}
    )
    return service.create_version(data, user_id=1)


class TestVersionCreation:
    """Tests for version creation"""

    def test_create_version(self, service, sample_matrix_data):
        """Test creating a new version"""
        data = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            description="Initial version",
            matrix_data=sample_matrix_data
        )
        
        version = service.create_version(data, user_id=1)
        
        assert version.id is not None
        assert version.version_number == 1
        assert version.version_name == "Version 1.0"
        assert version.status == VersionStatus.DRAFT
        assert version.is_active is False
        assert version.created_by == 1

    def test_create_multiple_versions(self, service, sample_matrix_data):
        """Test creating multiple versions increments version number"""
        # Create first version
        data1 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version1 = service.create_version(data1, user_id=1)
        
        # Create second version
        data2 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 2.0",
            matrix_data=sample_matrix_data
        )
        version2 = service.create_version(data2, user_id=1)
        
        assert version1.version_number == 1
        assert version2.version_number == 2


class TestVersionRetrieval:
    """Tests for version retrieval"""

    def test_get_version(self, service, sample_version):
        """Test retrieving a version by ID"""
        version = service.get_version(sample_version.id)
        
        assert version is not None
        assert version.id == sample_version.id
        assert version.version_name == sample_version.version_name

    def test_get_nonexistent_version(self, service):
        """Test retrieving a non-existent version"""
        version = service.get_version(99999)
        assert version is None

    def test_get_versions_by_matrix(self, service, sample_matrix_data):
        """Test retrieving all versions for a matrix"""
        # Create multiple versions
        for i in range(3):
            data = PriceMatrixVersionCreate(
                matrix_id=1,
                version_name=f"Version {i+1}.0",
                matrix_data=sample_matrix_data
            )
            service.create_version(data, user_id=1)
        
        versions, total_count = service.get_versions_by_matrix(matrix_id=1)
        
        assert total_count == 3
        assert len(versions) == 3

    def test_get_active_version(self, service, sample_version):
        """Test retrieving the active version"""
        # Approve and activate the version
        service.submit_for_approval(sample_version.id, user_id=1)
        service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(),
            user_id=2
        )
        service.activate_version(sample_version.id, user_id=1)
        
        active_version = service.get_active_version(matrix_id=1)
        
        assert active_version is not None
        assert active_version.id == sample_version.id
        assert active_version.is_active is True


class TestVersionUpdate:
    """Tests for version updates"""

    def test_update_draft_version(self, service, sample_version):
        """Test updating a draft version"""
        update_data = PriceMatrixVersionUpdate(
            version_name="Updated Version 1.0",
            description="Updated description"
        )
        
        updated_version = service.update_version(
            sample_version.id,
            update_data,
            user_id=1
        )
        
        assert updated_version.version_name == "Updated Version 1.0"
        assert updated_version.description == "Updated description"

    def test_cannot_update_approved_version(self, service, sample_version):
        """Test that approved versions cannot be updated"""
        # Approve the version
        service.submit_for_approval(sample_version.id, user_id=1)
        service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(),
            user_id=2
        )
        
        update_data = PriceMatrixVersionUpdate(
            version_name="Should Fail"
        )
        
        with pytest.raises(ValueError, match="Cannot update version"):
            service.update_version(sample_version.id, update_data, user_id=1)


class TestApprovalWorkflow:
    """Tests for approval workflow"""

    def test_submit_for_approval(self, service, sample_version):
        """Test submitting a version for approval"""
        version = service.submit_for_approval(sample_version.id, user_id=1)
        
        assert version.status == VersionStatus.PENDING

    def test_approve_version(self, service, sample_version):
        """Test approving a version"""
        service.submit_for_approval(sample_version.id, user_id=1)
        
        version = service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(approval_notes="Looks good"),
            user_id=2
        )
        
        assert version.status == VersionStatus.APPROVED
        assert version.approved_by == 2
        assert version.approved_at is not None

    def test_reject_version(self, service, sample_version):
        """Test rejecting a version"""
        service.submit_for_approval(sample_version.id, user_id=1)
        
        version = service.reject_version(
            sample_version.id,
            PriceMatrixVersionReject(rejection_reason="Needs more work"),
            user_id=2
        )
        
        assert version.status == VersionStatus.REJECTED

    def test_activate_approved_version(self, service, sample_version):
        """Test activating an approved version"""
        service.submit_for_approval(sample_version.id, user_id=1)
        service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(),
            user_id=2
        )
        
        version = service.activate_version(sample_version.id, user_id=1)
        
        assert version.status == VersionStatus.ACTIVE
        assert version.is_active is True

    def test_cannot_activate_unapproved_version(self, service, sample_version):
        """Test that unapproved versions cannot be activated"""
        with pytest.raises(ValueError, match="Can only activate approved versions"):
            service.activate_version(sample_version.id, user_id=1)


class TestVersionComparison:
    """Tests for version comparison"""

    def test_compare_versions(self, service, sample_matrix_data):
        """Test comparing two versions"""
        # Create first version
        data1 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version1 = service.create_version(data1, user_id=1)
        
        # Create second version with modified data
        modified_data = sample_matrix_data.copy()
        modified_data["modules"]["5"]["10kWh"] = 16000  # Changed price
        
        data2 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 2.0",
            matrix_data=modified_data
        )
        version2 = service.create_version(data2, user_id=1)
        
        # Compare versions
        comparison_data = PriceMatrixVersionCompare(
            version_a_id=version1.id,
            version_b_id=version2.id,
            include_details=True
        )
        
        comparison = service.compare_versions(comparison_data, user_id=1)
        
        assert comparison is not None
        assert comparison.version_a_id == version1.id
        assert comparison.version_b_id == version2.id
        assert "modified" in comparison.differences
        assert len(comparison.differences["modified"]) > 0

    def test_compare_versions_different_matrices(self, service, sample_matrix_data):
        """Test that versions from different matrices cannot be compared"""
        data1 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version1 = service.create_version(data1, user_id=1)
        
        data2 = PriceMatrixVersionCreate(
            matrix_id=2,  # Different matrix
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version2 = service.create_version(data2, user_id=1)
        
        comparison_data = PriceMatrixVersionCompare(
            version_a_id=version1.id,
            version_b_id=version2.id
        )
        
        with pytest.raises(ValueError, match="must belong to the same matrix"):
            service.compare_versions(comparison_data, user_id=1)


class TestVersionRollback:
    """Tests for version rollback"""

    def test_rollback_to_version(self, service, sample_matrix_data):
        """Test rolling back to a previous version"""
        # Create and activate first version
        data1 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version1 = service.create_version(data1, user_id=1)
        service.submit_for_approval(version1.id, user_id=1)
        service.approve_version(version1.id, PriceMatrixVersionApprove(), user_id=2)
        service.activate_version(version1.id, user_id=1)
        
        # Create and activate second version
        modified_data = sample_matrix_data.copy()
        modified_data["modules"]["5"]["10kWh"] = 16000
        
        data2 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 2.0",
            matrix_data=modified_data
        )
        version2 = service.create_version(data2, user_id=1)
        service.submit_for_approval(version2.id, user_id=1)
        service.approve_version(version2.id, PriceMatrixVersionApprove(), user_id=2)
        service.activate_version(version2.id, user_id=1)
        
        # Rollback to version 1
        rollback_data = PriceMatrixVersionRollback(
            rollback_reason="Testing rollback",
            create_backup=True
        )
        
        result = service.rollback_to_version(version1.id, rollback_data, user_id=1)
        
        assert result["success"] is True
        assert result["rolled_back_to_version"] == 1
        assert result["previous_version"] == 2
        assert result["backup_version_id"] is not None
        
        # Verify version 1 is now active
        active_version = service.get_active_version(matrix_id=1)
        assert active_version.id == version1.id


class TestVersionHistory:
    """Tests for version history"""

    def test_get_version_history(self, service, sample_matrix_data):
        """Test retrieving version history"""
        # Create multiple versions
        for i in range(5):
            data = PriceMatrixVersionCreate(
                matrix_id=1,
                version_name=f"Version {i+1}.0",
                matrix_data=sample_matrix_data
            )
            service.create_version(data, user_id=1)
        
        history = service.get_version_history(matrix_id=1, limit=10)
        
        assert history["total_count"] == 5
        assert len(history["versions"]) == 5

    def test_get_version_changes(self, service, sample_version):
        """Test retrieving version changes"""
        # Make some changes
        update_data = PriceMatrixVersionUpdate(
            version_name="Updated Version"
        )
        service.update_version(sample_version.id, update_data, user_id=1)
        
        changes, total_count = service.get_version_changes(sample_version.id)
        
        assert total_count >= 2  # Creation + update
        assert len(changes) >= 2


class TestVersionMigration:
    """Tests for version migration"""

    def test_migrate_version_data(self, service, sample_matrix_data):
        """Test migrating data between versions"""
        # Create source version
        data1 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 1.0",
            matrix_data=sample_matrix_data
        )
        version1 = service.create_version(data1, user_id=1)
        
        # Create target version
        data2 = PriceMatrixVersionCreate(
            matrix_id=1,
            version_name="Version 2.0",
            matrix_data={}
        )
        version2 = service.create_version(data2, user_id=1)
        
        # Define migration rules
        migration_rules = {
            "add_timestamp": {
                "type": "add_default",
                "key": "migrated_at",
                "default": datetime.utcnow().isoformat()
            }
        }
        
        result = service.migrate_version_data(
            from_version_id=version1.id,
            to_version_id=version2.id,
            migration_rules=migration_rules,
            user_id=1
        )
        
        assert result["success"] is True
        assert result["from_version"] == 1
        assert result["to_version"] == 2
        assert result["migrated_records"] > 0


class TestVersionDeletion:
    """Tests for version deletion"""

    def test_delete_draft_version(self, service, sample_version):
        """Test deleting a draft version"""
        success = service.delete_version(sample_version.id, user_id=1)
        
        assert success is True
        
        # Verify version is deleted
        version = service.get_version(sample_version.id)
        assert version is None

    def test_cannot_delete_approved_version(self, service, sample_version):
        """Test that approved versions cannot be deleted"""
        service.submit_for_approval(sample_version.id, user_id=1)
        service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(),
            user_id=2
        )
        
        with pytest.raises(ValueError, match="Cannot delete version"):
            service.delete_version(sample_version.id, user_id=1)

    def test_cannot_delete_active_version(self, service, sample_version):
        """Test that active versions cannot be deleted"""
        service.submit_for_approval(sample_version.id, user_id=1)
        service.approve_version(
            sample_version.id,
            PriceMatrixVersionApprove(),
            user_id=2
        )
        service.activate_version(sample_version.id, user_id=1)
        
        with pytest.raises(ValueError, match="Cannot delete active version"):
            service.delete_version(sample_version.id, user_id=1)
