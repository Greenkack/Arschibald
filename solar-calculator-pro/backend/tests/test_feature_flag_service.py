"""
Tests for Feature Flag Service

This module contains comprehensive tests for the feature flag service.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.services.feature_flag_service import FeatureFlagService
from backend.models.feature_flag_models import FeatureFlag, Role
from backend.models.feature_flag_schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagType,
    RoleCreate
)
from backend.core.errors import APIError


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def service(db_session):
    """Create a feature flag service instance"""
    return FeatureFlagService(db_session)


@pytest.fixture
def sample_role(db_session):
    """Create a sample role for testing"""
    role = Role(name="admin", description="Administrator role")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


class TestFeatureFlagCreation:
    """Tests for creating feature flags"""
    
    def test_create_global_flag(self, service):
        """Test creating a global feature flag"""
        flag_data = FeatureFlagCreate(
            key="test.feature",
            name="Test Feature",
            description="A test feature",
            enabled=True,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        flag = service.create_feature_flag(flag_data)
        
        assert flag.key == "test.feature"
        assert flag.name == "Test Feature"
        assert flag.enabled is True
        assert flag.flag_type == "global"
    
    def test_create_user_based_flag(self, service):
        """Test creating a user-based feature flag"""
        flag_data = FeatureFlagCreate(
            key="test.user.feature",
            name="User Feature",
            enabled=True,
            flag_type=FeatureFlagType.USER,
            user_ids=[1, 2, 3]
        )
        
        flag = service.create_feature_flag(flag_data)
        
        assert flag.flag_type == "user"
        assert len(flag.users) == 0  # Users don't exist in test DB
    
    def test_create_role_based_flag(self, service, sample_role):
        """Test creating a role-based feature flag"""
        flag_data = FeatureFlagCreate(
            key="test.role.feature",
            name="Role Feature",
            enabled=True,
            flag_type=FeatureFlagType.ROLE,
            role_ids=[sample_role.id]
        )
        
        flag = service.create_feature_flag(flag_data)
        
        assert flag.flag_type == "role"
    
    def test_create_percentage_flag(self, service):
        """Test creating a percentage rollout flag"""
        flag_data = FeatureFlagCreate(
            key="test.percentage.feature",
            name="Percentage Feature",
            enabled=True,
            flag_type=FeatureFlagType.PERCENTAGE,
            rollout_percentage=50
        )
        
        flag = service.create_feature_flag(flag_data)
        
        assert flag.flag_type == "percentage"
        assert flag.rollout_percentage == 50
    
    def test_create_duplicate_key_fails(self, service):
        """Test that creating a flag with duplicate key fails"""
        flag_data = FeatureFlagCreate(
            key="duplicate.key",
            name="First Flag",
            enabled=True
        )
        
        service.create_feature_flag(flag_data)
        
        # Try to create another with same key
        with pytest.raises(APIError) as exc_info:
            service.create_feature_flag(flag_data)
        
        assert exc_info.value.status_code == 409
    
    def test_key_normalization(self, service):
        """Test that keys are normalized to lowercase"""
        flag_data = FeatureFlagCreate(
            key="TEST.UPPER.CASE",
            name="Test Flag",
            enabled=True
        )
        
        flag = service.create_feature_flag(flag_data)
        
        assert flag.key == "test.upper.case"


class TestFeatureFlagRetrieval:
    """Tests for retrieving feature flags"""
    
    def test_get_by_id(self, service):
        """Test getting a flag by ID"""
        flag_data = FeatureFlagCreate(
            key="test.get.id",
            name="Test Get ID",
            enabled=True
        )
        
        created_flag = service.create_feature_flag(flag_data)
        retrieved_flag = service.get_feature_flag(created_flag.id)
        
        assert retrieved_flag is not None
        assert retrieved_flag.id == created_flag.id
        assert retrieved_flag.key == created_flag.key
    
    def test_get_by_key(self, service):
        """Test getting a flag by key"""
        flag_data = FeatureFlagCreate(
            key="test.get.key",
            name="Test Get Key",
            enabled=True
        )
        
        created_flag = service.create_feature_flag(flag_data)
        retrieved_flag = service.get_feature_flag_by_key("test.get.key")
        
        assert retrieved_flag is not None
        assert retrieved_flag.key == created_flag.key
    
    def test_get_nonexistent_flag(self, service):
        """Test getting a non-existent flag returns None"""
        flag = service.get_feature_flag(99999)
        assert flag is None
    
    def test_list_flags(self, service):
        """Test listing all flags"""
        # Create multiple flags
        for i in range(5):
            flag_data = FeatureFlagCreate(
                key=f"test.list.{i}",
                name=f"Test List {i}",
                enabled=True
            )
            service.create_feature_flag(flag_data)
        
        flags = service.list_feature_flags()
        
        assert len(flags) == 5
    
    def test_list_flags_with_pagination(self, service):
        """Test listing flags with pagination"""
        # Create multiple flags
        for i in range(10):
            flag_data = FeatureFlagCreate(
                key=f"test.page.{i}",
                name=f"Test Page {i}",
                enabled=True
            )
            service.create_feature_flag(flag_data)
        
        # Get first page
        page1 = service.list_feature_flags(skip=0, limit=5)
        assert len(page1) == 5
        
        # Get second page
        page2 = service.list_feature_flags(skip=5, limit=5)
        assert len(page2) == 5
        
        # Ensure no overlap
        page1_keys = {f.key for f in page1}
        page2_keys = {f.key for f in page2}
        assert len(page1_keys & page2_keys) == 0


class TestFeatureFlagUpdate:
    """Tests for updating feature flags"""
    
    def test_update_enabled_status(self, service):
        """Test updating the enabled status"""
        flag_data = FeatureFlagCreate(
            key="test.update.enabled",
            name="Test Update",
            enabled=False
        )
        
        flag = service.create_feature_flag(flag_data)
        
        update_data = FeatureFlagUpdate(enabled=True)
        updated_flag = service.update_feature_flag(flag.id, update_data)
        
        assert updated_flag.enabled is True
    
    def test_update_name_and_description(self, service):
        """Test updating name and description"""
        flag_data = FeatureFlagCreate(
            key="test.update.info",
            name="Original Name",
            description="Original description",
            enabled=True
        )
        
        flag = service.create_feature_flag(flag_data)
        
        update_data = FeatureFlagUpdate(
            name="Updated Name",
            description="Updated description"
        )
        updated_flag = service.update_feature_flag(flag.id, update_data)
        
        assert updated_flag.name == "Updated Name"
        assert updated_flag.description == "Updated description"
    
    def test_update_rollout_percentage(self, service):
        """Test updating rollout percentage"""
        flag_data = FeatureFlagCreate(
            key="test.update.percentage",
            name="Test Percentage",
            enabled=True,
            flag_type=FeatureFlagType.PERCENTAGE,
            rollout_percentage=25
        )
        
        flag = service.create_feature_flag(flag_data)
        
        update_data = FeatureFlagUpdate(rollout_percentage=75)
        updated_flag = service.update_feature_flag(flag.id, update_data)
        
        assert updated_flag.rollout_percentage == 75
    
    def test_update_nonexistent_flag_fails(self, service):
        """Test updating a non-existent flag fails"""
        update_data = FeatureFlagUpdate(enabled=True)
        
        with pytest.raises(APIError) as exc_info:
            service.update_feature_flag(99999, update_data)
        
        assert exc_info.value.status_code == 404


class TestFeatureFlagDeletion:
    """Tests for deleting feature flags"""
    
    def test_delete_flag(self, service):
        """Test deleting a flag"""
        flag_data = FeatureFlagCreate(
            key="test.delete",
            name="Test Delete",
            enabled=True
        )
        
        flag = service.create_feature_flag(flag_data)
        result = service.delete_feature_flag(flag.id)
        
        assert result is True
        
        # Verify flag is deleted
        deleted_flag = service.get_feature_flag(flag.id)
        assert deleted_flag is None
    
    def test_delete_nonexistent_flag_fails(self, service):
        """Test deleting a non-existent flag fails"""
        with pytest.raises(APIError) as exc_info:
            service.delete_feature_flag(99999)
        
        assert exc_info.value.status_code == 404


class TestFeatureFlagChecking:
    """Tests for checking if features are enabled"""
    
    def test_global_flag_enabled(self, service):
        """Test checking a globally enabled flag"""
        flag_data = FeatureFlagCreate(
            key="test.check.global",
            name="Test Check Global",
            enabled=True,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        service.create_feature_flag(flag_data)
        
        result = service.is_feature_enabled("test.check.global")
        
        assert result.enabled is True
        assert "Global flag" in result.reason
    
    def test_global_flag_disabled(self, service):
        """Test checking a globally disabled flag"""
        flag_data = FeatureFlagCreate(
            key="test.check.disabled",
            name="Test Check Disabled",
            enabled=False,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        service.create_feature_flag(flag_data)
        
        result = service.is_feature_enabled("test.check.disabled")
        
        assert result.enabled is False
    
    def test_nonexistent_flag(self, service):
        """Test checking a non-existent flag"""
        result = service.is_feature_enabled("nonexistent.flag")
        
        assert result.enabled is False
        assert "not found" in result.reason.lower()
    
    def test_percentage_rollout_consistency(self, service):
        """Test that percentage rollout is consistent for same user"""
        flag_data = FeatureFlagCreate(
            key="test.check.percentage",
            name="Test Percentage",
            enabled=True,
            flag_type=FeatureFlagType.PERCENTAGE,
            rollout_percentage=50
        )
        
        service.create_feature_flag(flag_data)
        
        # Check multiple times for same user
        user_id = 12345
        result1 = service.is_feature_enabled("test.check.percentage", user_id)
        result2 = service.is_feature_enabled("test.check.percentage", user_id)
        result3 = service.is_feature_enabled("test.check.percentage", user_id)
        
        # Should be consistent
        assert result1.enabled == result2.enabled == result3.enabled
    
    def test_check_multiple_features(self, service):
        """Test checking multiple features at once"""
        # Create multiple flags
        for i in range(3):
            flag_data = FeatureFlagCreate(
                key=f"test.multi.{i}",
                name=f"Test Multi {i}",
                enabled=(i % 2 == 0),  # Alternate enabled/disabled
                flag_type=FeatureFlagType.GLOBAL
            )
            service.create_feature_flag(flag_data)
        
        keys = ["test.multi.0", "test.multi.1", "test.multi.2"]
        results = service.check_multiple_features(keys)
        
        assert len(results) == 3
        assert results["test.multi.0"] is True
        assert results["test.multi.1"] is False
        assert results["test.multi.2"] is True


class TestRoleManagement:
    """Tests for role management"""
    
    def test_create_role(self, service):
        """Test creating a role"""
        role_data = RoleCreate(
            name="test_role",
            description="Test role description"
        )
        
        role = service.create_role(role_data)
        
        assert role.name == "test_role"
        assert role.description == "Test role description"
    
    def test_create_duplicate_role_fails(self, service):
        """Test creating a role with duplicate name fails"""
        role_data = RoleCreate(name="duplicate_role")
        
        service.create_role(role_data)
        
        with pytest.raises(APIError) as exc_info:
            service.create_role(role_data)
        
        assert exc_info.value.status_code == 409
    
    def test_list_roles(self, service):
        """Test listing roles"""
        # Create multiple roles
        for i in range(3):
            role_data = RoleCreate(name=f"role_{i}")
            service.create_role(role_data)
        
        roles = service.list_roles()
        
        assert len(roles) == 3


class TestCaching:
    """Tests for feature flag caching"""
    
    def test_cache_is_cleared_on_update(self, service):
        """Test that cache is cleared when flag is updated"""
        flag_data = FeatureFlagCreate(
            key="test.cache.update",
            name="Test Cache",
            enabled=False,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        flag = service.create_feature_flag(flag_data)
        
        # Check flag (should be cached)
        result1 = service.is_feature_enabled("test.cache.update")
        assert result1.enabled is False
        
        # Update flag
        update_data = FeatureFlagUpdate(enabled=True)
        service.update_feature_flag(flag.id, update_data)
        
        # Check again (should reflect update)
        result2 = service.is_feature_enabled("test.cache.update")
        assert result2.enabled is True
    
    def test_cache_is_cleared_on_delete(self, service):
        """Test that cache is cleared when flag is deleted"""
        flag_data = FeatureFlagCreate(
            key="test.cache.delete",
            name="Test Cache Delete",
            enabled=True,
            flag_type=FeatureFlagType.GLOBAL
        )
        
        flag = service.create_feature_flag(flag_data)
        
        # Check flag (should be cached)
        result1 = service.is_feature_enabled("test.cache.delete")
        assert result1.enabled is True
        
        # Delete flag
        service.delete_feature_flag(flag.id)
        
        # Check again (should not be found)
        result2 = service.is_feature_enabled("test.cache.delete")
        assert result2.enabled is False
        assert "not found" in result2.reason.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
