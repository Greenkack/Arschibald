"""
Tests for Form Input Dynamic Keys System

Requirements: 14.7
Task: 223
"""

import pytest
import os
from datetime import datetime

from backend.services.form_input_key_service import (
    FormInputKeyManager,
    FormInput,
    FormInputType,
    get_form_input_manager
)
from backend.services.form_key_persistence import (
    FormKeyPersistence,
    get_form_key_persistence
)


class TestFormInputKeyManager:
    """Tests for FormInputKeyManager"""

    def setup_method(self):
        """Setup test fixtures"""
        self.manager = FormInputKeyManager()

    def test_create_input_key(self):
        """Test creating a dynamic key for form input"""
        key = self.manager.create_input_key(
            FormInputType.TEXT,
            "test_form",
            "test_field"
        )

        assert key is not None
        assert isinstance(key, str)
        assert "test_form" in key
        assert "test_field" in key

    def test_register_form_input(self):
        """Test registering a form input"""
        form_input = self.manager.register_form_input(
            form_id="solar_calc",
            field_name="roof_area",
            input_type=FormInputType.NUMBER,
            label="Roof Area (m²)",
            default_value=50.0,
            validation_rules={'min': 10, 'max': 1000, 'required': True}
        )

        assert form_input is not None
        assert form_input.key is not None
        assert form_input.form_id == "solar_calc"
        assert form_input.field_name == "roof_area"
        assert form_input.input_type == FormInputType.NUMBER

    def test_get_input_by_key(self):
        """Test retrieving input by dynamic key"""
        form_input = self.manager.register_form_input(
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field"
        )

        retrieved = self.manager.get_input_by_key(form_input.key)
        assert retrieved is not None
        assert retrieved.key == form_input.key

    def test_get_input_by_field(self):
        """Test retrieving input by form ID and field name"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field"
        )

        retrieved = self.manager.get_input_by_field("test_form", "test_field")
        assert retrieved is not None
        assert retrieved.field_name == "test_field"

    def test_get_form_inputs(self):
        """Test getting all inputs for a form"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1"
        )
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field2",
            input_type=FormInputType.NUMBER,
            label="Field 2"
        )

        inputs = self.manager.get_form_inputs("test_form")
        assert len(inputs) == 2

    def test_get_form_key_mapping(self):
        """Test getting key mapping for a form"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1"
        )

        mapping = self.manager.get_form_key_mapping("test_form")
        assert "field1" in mapping
        assert isinstance(mapping["field1"], str)

    def test_update_input_value(self):
        """Test updating input value"""
        form_input = self.manager.register_form_input(
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.NUMBER,
            label="Test Field",
            validation_rules={'min': 0, 'max': 100}
        )

        success = self.manager.update_input_value(form_input.key, 50)
        assert success is True

        value = self.manager.get_input_value(form_input.key)
        assert value == 50

    def test_update_input_value_validation_fail(self):
        """Test updating input value with validation failure"""
        form_input = self.manager.register_form_input(
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.NUMBER,
            label="Test Field",
            validation_rules={'min': 0, 'max': 100}
        )

        with pytest.raises(ValueError):
            self.manager.update_input_value(form_input.key, 150, validate=True)

    def test_get_form_data(self):
        """Test getting all data from a form"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1",
            default_value="test"
        )
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field2",
            input_type=FormInputType.NUMBER,
            label="Field 2",
            default_value=42
        )

        data = self.manager.get_form_data("test_form")
        assert "field1" in data
        assert "field2" in data
        assert data["field1"] == "test"
        assert data["field2"] == 42

    def test_get_form_data_with_keys(self):
        """Test getting form data with keys included"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1",
            default_value="test"
        )

        data = self.manager.get_form_data("test_form", include_keys=True)
        assert "field1" in data
        assert "value" in data["field1"]
        assert "key" in data["field1"]
        assert "type" in data["field1"]

    def test_set_form_data(self):
        """Test setting data for multiple form inputs"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1"
        )
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field2",
            input_type=FormInputType.NUMBER,
            label="Field 2"
        )

        errors = self.manager.set_form_data(
            "test_form",
            {"field1": "new value", "field2": 100}
        )

        assert len(errors) == 0

        data = self.manager.get_form_data("test_form")
        assert data["field1"] == "new value"
        assert data["field2"] == 100

    def test_validate_form(self):
        """Test validating all inputs in a form"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="required_field",
            input_type=FormInputType.TEXT,
            label="Required Field",
            validation_rules={'required': True}
        )

        is_valid, errors = self.manager.validate_form("test_form")
        assert is_valid is False
        assert "required_field" in errors

    def test_clear_form(self):
        """Test clearing all values in a form"""
        form_input = self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1",
            default_value="default"
        )

        self.manager.update_input_value(form_input.key, "changed")
        self.manager.clear_form("test_form")

        value = self.manager.get_input_value(form_input.key)
        assert value == "default"

    def test_export_form_schema(self):
        """Test exporting form schema"""
        self.manager.register_form_input(
            form_id="test_form",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1"
        )

        schema = self.manager.export_form_schema("test_form")
        assert "form_id" in schema
        assert "inputs" in schema
        assert "key_mapping" in schema
        assert schema["form_id"] == "test_form"

    def test_get_statistics(self):
        """Test getting statistics"""
        self.manager.register_form_input(
            form_id="form1",
            field_name="field1",
            input_type=FormInputType.TEXT,
            label="Field 1"
        )
        self.manager.register_form_input(
            form_id="form2",
            field_name="field1",
            input_type=FormInputType.NUMBER,
            label="Field 1"
        )

        stats = self.manager.get_statistics()
        assert stats["total_inputs"] >= 2
        assert stats["total_forms"] >= 2


class TestFormInput:
    """Tests for FormInput class"""

    def test_form_input_creation(self):
        """Test creating a FormInput"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field",
            default_value="default"
        )

        assert form_input.key == "TEST_KEY_123"
        assert form_input.get_value() == "default"

    def test_set_and_get_value(self):
        """Test setting and getting value"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field"
        )

        form_input.set_value("new value")
        assert form_input.get_value() == "new value"

    def test_reset_to_default(self):
        """Test resetting to default value"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field",
            default_value="default"
        )

        form_input.set_value("changed")
        form_input.reset_to_default()
        assert form_input.get_value() == "default"

    def test_validate_required_field(self):
        """Test validation of required field"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field",
            validation_rules={'required': True}
        )

        is_valid, error = form_input.validate_value(None)
        assert is_valid is False
        assert error is not None

    def test_validate_number_min_max(self):
        """Test number validation with min/max"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.NUMBER,
            label="Test Field",
            validation_rules={'min': 0, 'max': 100}
        )

        is_valid, error = form_input.validate_value(50)
        assert is_valid is True

        is_valid, error = form_input.validate_value(150)
        assert is_valid is False

    def test_validate_email(self):
        """Test email validation"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="email",
            input_type=FormInputType.EMAIL,
            label="Email"
        )

        is_valid, error = form_input.validate_value("test@example.com")
        assert is_valid is True

        is_valid, error = form_input.validate_value("invalid-email")
        assert is_valid is False

    def test_value_history(self):
        """Test value history tracking"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field"
        )

        form_input.set_value("value1")
        form_input.set_value("value2")

        history = form_input.get_value_history()
        assert len(history) >= 2

    def test_to_dict(self):
        """Test converting to dictionary"""
        form_input = FormInput(
            key="TEST_KEY_123",
            form_id="test_form",
            field_name="test_field",
            input_type=FormInputType.TEXT,
            label="Test Field"
        )

        data = form_input.to_dict()
        assert data["key"] == "TEST_KEY_123"
        assert data["form_id"] == "test_form"
        assert data["field_name"] == "test_field"


class TestFormKeyPersistence:
    """Tests for FormKeyPersistence"""

    def setup_method(self):
        """Setup test fixtures"""
        self.test_db = "test_form_keys.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.persistence = FormKeyPersistence(self.test_db)

    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_save_and_load_form_input(self):
        """Test saving and loading a form input"""
        form_input_dict = {
            'key': 'TEST_KEY_123',
            'form_id': 'test_form',
            'field_name': 'test_field',
            'input_type': 'text',
            'label': 'Test Field',
            'current_value': 'test value',
            'default_value': 'default',
            'validation_rules': {'required': True},
            'metadata': {'custom': 'data'},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        success = self.persistence.save_form_input(form_input_dict)
        assert success is True

        loaded = self.persistence.load_form_input('TEST_KEY_123')
        assert loaded is not None
        assert loaded['key'] == 'TEST_KEY_123'
        assert loaded['form_id'] == 'test_form'

    def test_load_form_inputs(self):
        """Test loading all inputs for a form"""
        for i in range(3):
            form_input_dict = {
                'key': f'TEST_KEY_{i}',
                'form_id': 'test_form',
                'field_name': f'field_{i}',
                'input_type': 'text',
                'label': f'Field {i}',
                'current_value': None,
                'default_value': None,
                'validation_rules': {},
                'metadata': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.persistence.save_form_input(form_input_dict)

        inputs = self.persistence.load_form_inputs('test_form')
        assert len(inputs) == 3

    def test_save_and_load_form_submission(self):
        """Test saving and loading form submissions"""
        submission_id = self.persistence.save_form_submission(
            form_id='test_form',
            data={'field1': 'value1', 'field2': 'value2'},
            user_id='user123'
        )

        assert submission_id is not None

        submissions = self.persistence.load_form_submissions('test_form')
        assert len(submissions) >= 1
        assert submissions[0]['form_id'] == 'test_form'

    def test_save_and_load_value_history(self):
        """Test saving and loading value history"""
        success = self.persistence.save_value_history(
            input_key='TEST_KEY_123',
            value='test value'
        )
        assert success is True

        history = self.persistence.load_value_history('TEST_KEY_123')
        assert len(history) >= 1

    def test_delete_form_input(self):
        """Test deleting a form input"""
        form_input_dict = {
            'key': 'TEST_KEY_DELETE',
            'form_id': 'test_form',
            'field_name': 'test_field',
            'input_type': 'text',
            'label': 'Test Field',
            'current_value': None,
            'default_value': None,
            'validation_rules': {},
            'metadata': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self.persistence.save_form_input(form_input_dict)
        success = self.persistence.delete_form_input('TEST_KEY_DELETE')
        assert success is True

        loaded = self.persistence.load_form_input('TEST_KEY_DELETE')
        assert loaded is None

    def test_delete_form(self):
        """Test deleting an entire form"""
        form_input_dict = {
            'key': 'TEST_KEY_123',
            'form_id': 'test_form_delete',
            'field_name': 'test_field',
            'input_type': 'text',
            'label': 'Test Field',
            'current_value': None,
            'default_value': None,
            'validation_rules': {},
            'metadata': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self.persistence.save_form_input(form_input_dict)
        success = self.persistence.delete_form('test_form_delete')
        assert success is True

        inputs = self.persistence.load_form_inputs('test_form_delete')
        assert len(inputs) == 0

    def test_get_statistics(self):
        """Test getting persistence statistics"""
        form_input_dict = {
            'key': 'TEST_KEY_STATS',
            'form_id': 'test_form',
            'field_name': 'test_field',
            'input_type': 'text',
            'label': 'Test Field',
            'current_value': None,
            'default_value': None,
            'validation_rules': {},
            'metadata': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self.persistence.save_form_input(form_input_dict)

        stats = self.persistence.get_statistics()
        assert 'total_inputs' in stats
        assert 'total_forms' in stats
        assert stats['total_inputs'] >= 1
