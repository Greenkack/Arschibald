"""Tests for Form State Management with Undo/Redo"""

import time
import uuid
from datetime import datetime

import pytest

from .database import get_db_manager, init_database
from .form_manager import (
    FormAutoSave,
    FormManager,
    FormRepository,
    FormSnapshot,
    FormState,
    FormValidator,
    create_form,
    get_form_manager,
    init_form_tables,
    redo_form,
    reset_form,
    save_form_now,
    undo_form,
    update_form_field,
    validate_form,
)


@pytest.fixture
def db_manager():
    """Create test database manager"""
    # Use in-memory database for tests
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    db_mgr = get_db_manager()
    init_database(auto_migrate=False)
    init_form_tables()

    yield db_mgr

    # Cleanup
    db_mgr.drop_tables()


@pytest.fixture
def form_repository(db_manager):
    """Create form repository"""
    return FormRepository(db_manager)


@pytest.fixture
def form_validator():
    """Create form validator"""
    return FormValidator()


@pytest.fixture
def form_auto_save(form_repository):
    """Create auto-save system"""
    return FormAutoSave(form_repository, debounce_ms=100)


@pytest.fixture
def form_manager(form_repository, form_validator, form_auto_save):
    """Create form manager"""
    return FormManager(form_repository, form_validator, form_auto_save)


class TestFormState:
    """Test FormState class"""

    def test_create_form_state(self):
        """Test creating form state"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session"
        )

        assert form_state.form_id == "test_form"
        assert form_state.session_id == "test_session"
        assert form_state.data == {}
        assert form_state.is_dirty == False
        assert form_state.version == 1

    def test_update_data(self):
        """Test updating form data"""
        form_state = FormState(form_id="test_form", session_id="test_session")

        form_state.update_data("field1", "value1")

        assert form_state.data["field1"] == "value1"
        assert form_state.is_dirty
        assert len(form_state.snapshots) == 1  # Auto-snapshot created

    def test_update_multiple(self):
        """Test updating multiple fields"""
        form_state = FormState(form_id="test_form", session_id="test_session")

        updates = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        form_state.update_multiple(updates)

        assert form_state.data == updates
        assert form_state.is_dirty

    def test_create_snapshot(self):
        """Test creating snapshots"""
        form_state = FormState(form_id="test_form", session_id="test_session")
        form_state.data = {"field1": "value1"}

        snapshot = form_state.create_snapshot(
            description="Test snapshot",
            snapshot_type="manual"
        )

        assert snapshot.form_id == "test_form"
        assert snapshot.data == {"field1": "value1"}
        assert snapshot.description == "Test snapshot"
        assert snapshot.snapshot_type == "manual"
        assert len(form_state.snapshots) == 1

    def test_undo_redo(self):
        """Test undo/redo functionality"""
        form_state = FormState(form_id="test_form", session_id="test_session")

        # Create initial snapshot
        form_state.data = {"field1": "value1"}
        form_state.create_snapshot("Initial")

        # Make changes
        form_state.data = {"field1": "value2"}
        form_state.create_snapshot("Second")

        form_state.data = {"field1": "value3"}
        form_state.create_snapshot("Third")

        # Test undo
        assert form_state.can_undo()
        assert form_state.undo()
        assert form_state.data == {"field1": "value2"}

        assert form_state.undo()
        assert form_state.data == {"field1": "value1"}

        # Test redo
        assert form_state.can_redo()
        assert form_state.redo()
        assert form_state.data == {"field1": "value2"}

        assert form_state.redo()
        assert form_state.data == {"field1": "value3"}

    def test_snapshot_history_limit(self):
        """Test snapshot history limit"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session",
            max_snapshots=5
        )

        # Create more snapshots than limit
        for i in range(10):
            form_state.data = {"field": f"value{i}"}
            form_state.create_snapshot(f"Snapshot {i}")

        # Should only keep last 5
        assert len(form_state.snapshots) <= 5

    def test_restore_snapshot(self):
        """Test restoring specific snapshot"""
        form_state = FormState(form_id="test_form", session_id="test_session")

        # Create snapshots
        form_state.data = {"field1": "value1"}
        snapshot1 = form_state.create_snapshot("First")

        form_state.data = {"field1": "value2"}
        snapshot2 = form_state.create_snapshot("Second")

        form_state.data = {"field1": "value3"}
        form_state.create_snapshot("Third")

        # Restore second snapshot
        assert form_state.restore_snapshot(snapshot2.snapshot_id)
        assert form_state.data == {"field1": "value2"}

    def test_dependencies(self):
        """Test form dependencies"""
        form_state = FormState(form_id="test_form", session_id="test_session")

        form_state.add_dependency("parent_form")
        form_state.add_dependent("child_form")

        assert "parent_form" in form_state.depends_on
        assert "child_form" in form_state.dependents

        form_state.remove_dependency("parent_form")
        assert "parent_form" not in form_state.depends_on

    def test_serialization(self):
        """Test form state serialization"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session",
            user_id="test_user"
        )
        form_state.data = {"field1": "value1"}
        form_state.create_snapshot("Test")

        # Serialize
        data_dict = form_state.to_dict()

        # Deserialize
        restored = FormState.from_dict(data_dict)

        assert restored.form_id == form_state.form_id
        assert restored.data == form_state.data
        assert len(restored.snapshots) == len(form_state.snapshots)


class TestFormRepository:
    """Test FormRepository class"""

    def test_save_and_load_form(self, form_repository):
        """Test saving and loading form"""
        form_id = "test_form"
        session_id = "test_session"
        data = {"field1": "value1", "field2": "value2"}

        # Save form
        form_repository.save_form(
            form_id=form_id,
            data=data,
            session_id=session_id
        )

        # Load form
        loaded = form_repository.load_form(form_id, session_id)

        assert loaded is not None
        assert loaded['data'] == data
        assert loaded['version'] == 1

    def test_update_form(self, form_repository):
        """Test updating existing form"""
        form_id = "test_form"
        session_id = "test_session"

        # Save initial
        form_repository.save_form(
            form_id=form_id,
            data={"field1": "value1"},
            session_id=session_id
        )

        # Update
        form_repository.save_form(
            form_id=form_id,
            data={"field1": "value2"},
            session_id=session_id
        )

        # Load and verify
        loaded = form_repository.load_form(form_id, session_id)
        assert loaded['data'] == {"field1": "value2"}
        assert loaded['version'] == 2

    def test_delete_form(self, form_repository):
        """Test deleting form"""
        form_id = "test_form"
        session_id = "test_session"

        # Save form
        form_repository.save_form(
            form_id=form_id,
            data={"field1": "value1"},
            session_id=session_id
        )

        # Delete form
        assert form_repository.delete_form(form_id, session_id, soft=True)

        # Should not be loadable
        loaded = form_repository.load_form(form_id, session_id)
        assert loaded is None

    def test_save_and_load_snapshots(self, form_repository):
        """Test saving and loading snapshots"""
        form_id = "test_form"
        session_id = "test_session"

        # Create and save first snapshot
        snapshot1_id = str(uuid.uuid4())
        snapshot1 = FormSnapshot(
            snapshot_id=snapshot1_id,
            form_id=form_id,
            data={"field1": "value1"},
            timestamp=datetime.now(),
            session_id=session_id
        )
        form_repository.save_snapshot(snapshot1)

        # Create and save second snapshot
        snapshot2_id = str(uuid.uuid4())
        snapshot2 = FormSnapshot(
            snapshot_id=snapshot2_id,
            form_id=form_id,
            data={"field1": "value2"},
            timestamp=datetime.now(),
            session_id=session_id
        )
        form_repository.save_snapshot(snapshot2)

        # Load snapshots
        loaded = form_repository.load_snapshots(form_id, session_id)

        # Verify we got 2 snapshots
        assert len(loaded) == 2

        # Verify both snapshot IDs are present
        loaded_ids = [s.snapshot_id for s in loaded]
        assert snapshot1_id in loaded_ids
        assert snapshot2_id in loaded_ids

    def test_cleanup_old_snapshots(self, form_repository):
        """Test cleaning up old snapshots"""
        form_id = "test_form"
        session_id = "test_session"

        # Create many snapshots
        for i in range(10):
            snapshot = FormSnapshot(
                snapshot_id=str(uuid.uuid4()),
                form_id=form_id,
                data={"field": f"value{i}"},
                timestamp=datetime.now(),
                session_id=session_id
            )
            form_repository.save_snapshot(snapshot)

        # Cleanup, keep only 5
        deleted = form_repository.cleanup_old_snapshots(form_id, keep_count=5)

        assert deleted == 5

        # Verify only 5 remain
        remaining = form_repository.load_snapshots(form_id, session_id)
        assert len(remaining) == 5


class TestFormValidator:
    """Test FormValidator class"""

    def test_register_and_validate_field(self, form_validator):
        """Test field validation"""
        form_id = "test_form"

        # Register validator
        def validate_email(value):
            if "@" not in value:
                return False, "Invalid email"
            return True, None

        form_validator.register_validator(form_id, "email", validate_email)

        # Test valid value
        result = form_validator.validate_field(
            form_id, "email", "test@example.com")
        assert result.is_valid

        # Test invalid value
        result = form_validator.validate_field(form_id, "email", "invalid")
        assert not result.is_valid
        assert "Invalid email" in result.errors.get("email", [])

    def test_validate_form(self, form_validator):
        """Test form validation"""
        form_id = "test_form"

        # Register validators
        def validate_required(value):
            if not value:
                return False, "Field is required"
            return True, None

        form_validator.register_validator(form_id, "name", validate_required)
        form_validator.register_validator(form_id, "email", validate_required)

        # Test valid form
        result = form_validator.validate_form(
            form_id,
            {"name": "John", "email": "john@example.com"}
        )
        assert result.is_valid

        # Test invalid form
        result = form_validator.validate_form(
            form_id,
            {"name": "", "email": "john@example.com"}
        )
        assert not result.is_valid
        assert "name" in result.errors

    def test_form_level_validator(self, form_validator):
        """Test form-level validation"""
        form_id = "test_form"

        # Register form-level validator
        def validate_passwords_match(data):
            if data.get("password") != data.get("confirm_password"):
                return False, {"confirm_password": ["Passwords do not match"]}
            return True, {}

        form_validator.register_form_validator(
            form_id, validate_passwords_match)

        # Test matching passwords
        result = form_validator.validate_form(
            form_id,
            {"password": "secret", "confirm_password": "secret"}
        )
        assert result.is_valid

        # Test non-matching passwords
        result = form_validator.validate_form(
            form_id,
            {"password": "secret", "confirm_password": "different"}
        )
        assert not result.is_valid
        assert "confirm_password" in result.errors


class TestFormAutoSave:
    """Test FormAutoSave class"""

    def test_schedule_save(self, form_auto_save):
        """Test scheduling auto-save"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session"
        )
        form_state.data = {"field1": "value1"}

        # Schedule save
        save_called = []

        def callback(success, error):
            save_called.append((success, error))

        form_auto_save.schedule_save(form_state, callback)

        # Wait for debounce
        time.sleep(0.2)

        # Verify save was called
        assert len(save_called) == 1
        assert save_called[0][0]  # Success

    def test_debouncing(self, form_auto_save):
        """Test save debouncing"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session"
        )

        save_count = []

        def callback(success, error):
            save_count.append(1)

        # Schedule multiple saves quickly
        for i in range(5):
            form_state.data = {"field": f"value{i}"}
            form_auto_save.schedule_save(form_state, callback)
            time.sleep(0.05)

        # Wait for debounce
        time.sleep(0.2)

        # Should only save once
        assert len(save_count) == 1

    def test_flush(self, form_auto_save):
        """Test immediate flush"""
        form_state = FormState(
            form_id="test_form",
            session_id="test_session"
        )
        form_state.data = {"field1": "value1"}

        save_called = []

        def callback(success, error):
            save_called.append((success, error))

        # Schedule save
        form_auto_save.schedule_save(form_state, callback)

        # Flush immediately
        form_auto_save.flush("test_form")

        # Should be saved immediately
        assert len(save_called) == 1

    def test_recover_form(self, form_auto_save, form_repository):
        """Test form recovery"""
        form_id = "test_form"
        session_id = "test_session"

        # Save form data
        form_repository.save_form(
            form_id=form_id,
            data={"field1": "value1"},
            session_id=session_id
        )

        # Recover form
        recovered = form_auto_save.recover_form(form_id, session_id)

        assert recovered is not None
        assert recovered.form_id == form_id
        assert recovered.data == {"field1": "value1"}


class TestFormManager:
    """Test FormManager class"""

    def test_get_form(self, form_manager):
        """Test getting form"""
        form_state = form_manager.get_form(
            form_id="test_form",
            session_id="test_session"
        )

        assert form_state.form_id == "test_form"
        assert form_state.session_id == "test_session"

    def test_update_field(self, form_manager):
        """Test updating field"""
        form_id = "test_form"
        session_id = "test_session"

        result = form_manager.update_field(
            form_id=form_id,
            session_id=session_id,
            field="name",
            value="John Doe"
        )

        assert result.is_valid

        form_state = form_manager.get_form(form_id, session_id)
        assert form_state.data["name"] == "John Doe"

    def test_undo_redo_integration(self, form_manager):
        """Test undo/redo through manager"""
        form_id = "test_form"
        session_id = "test_session"

        # Make changes
        form_manager.update_field(form_id, session_id, "field1", "value1")
        form_manager.update_field(form_id, session_id, "field1", "value2")
        form_manager.update_field(form_id, session_id, "field1", "value3")

        # Undo
        assert form_manager.can_undo(form_id, session_id)
        assert form_manager.undo(form_id, session_id)

        form_state = form_manager.get_form(form_id, session_id)
        assert form_state.data["field1"] == "value2"

        # Redo
        assert form_manager.can_redo(form_id, session_id)
        assert form_manager.redo(form_id, session_id)

        form_state = form_manager.get_form(form_id, session_id)
        assert form_state.data["field1"] == "value3"

    def test_save_and_load(self, form_manager):
        """Test saving and loading form"""
        form_id = "test_form"
        session_id = "test_session"

        # Update form
        form_manager.update_field(form_id, session_id, "field1", "value1")

        # Save
        assert form_manager.save(form_id, session_id, immediate=True)

        # Create new manager to simulate restart
        new_manager = FormManager(
            form_manager.repository,
            form_manager.validator,
            form_manager.auto_save
        )

        # Load form
        form_state = new_manager.get_form(form_id, session_id)
        assert form_state.data["field1"] == "value1"

    def test_validation_integration(self, form_manager):
        """Test validation through manager"""
        form_id = "test_form"
        session_id = "test_session"

        # Register validator
        def validate_positive(value):
            if value <= 0:
                return False, "Must be positive"
            return True, None

        form_manager.validator.register_validator(
            form_id, "amount", validate_positive)

        # Test invalid value
        result = form_manager.update_field(
            form_id, session_id, "amount", -10
        )
        assert not result.is_valid

        # Test valid value
        result = form_manager.update_field(
            form_id, session_id, "amount", 100
        )
        assert result.is_valid

    def test_reset_form(self, form_manager):
        """Test resetting form"""
        form_id = "test_form"
        session_id = "test_session"

        # Add data
        form_manager.update_field(form_id, session_id, "field1", "value1")
        form_manager.update_field(form_id, session_id, "field2", "value2")

        # Reset
        form_manager.reset(form_id, session_id)

        form_state = form_manager.get_form(form_id, session_id)
        assert form_state.data == {}


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_create_form(self, db_manager):
        """Test create_form function"""
        form_state = create_form(
            form_id="test_form",
            session_id="test_session",
            initial_data={"field1": "value1"}
        )

        assert form_state.form_id == "test_form"
        assert form_state.data["field1"] == "value1"

    def test_update_form_field(self, db_manager):
        """Test update_form_field function"""
        create_form("test_form", "test_session")

        result = update_form_field(
            "test_form",
            "test_session",
            "name",
            "John"
        )

        assert result.is_valid

    def test_save_form_now(self, db_manager):
        """Test save_form_now function"""
        create_form("test_form", "test_session", {"field1": "value1"})

        assert save_form_now("test_form", "test_session")

    def test_undo_redo_functions(self, db_manager):
        """Test undo/redo functions"""
        create_form("test_form", "test_session")

        update_form_field("test_form", "test_session", "field1", "value1")
        update_form_field("test_form", "test_session", "field1", "value2")

        assert undo_form("test_form", "test_session")
        assert redo_form("test_form", "test_session")

    def test_validate_form_function(self, db_manager):
        """Test validate_form function"""
        create_form("test_form", "test_session", {"field1": "value1"})

        result = validate_form("test_form", "test_session")
        assert result.is_valid

    def test_reset_form_function(self, db_manager):
        """Test reset_form function"""
        create_form("test_form", "test_session", {"field1": "value1"})

        reset_form("test_form", "test_session")

        manager = get_form_manager()
        form_state = manager.get_form("test_form", "test_session")
        assert form_state.data == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
