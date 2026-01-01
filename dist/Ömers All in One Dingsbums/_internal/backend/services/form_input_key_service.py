"""
Form Input Dynamic Keys Service

This module provides comprehensive dynamic key management for all form inputs,
including text fields, number inputs, dropdowns, sliders, checkboxes, and more.

Requirements: 14.7
Task: 223
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

try:
    from backend.core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )
except ImportError:
    from core.dynamic_keys import (
        DynamicKeyMixin,
        KeyPrefix,
        DynamicKeyIndex,
        get_global_key_index
    )


class FormInputType(str, Enum):
    """Enumeration of form input types"""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SLIDER = "slider"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    FILE = "file"
    COLOR = "color"
    RANGE = "range"
    TOGGLE = "toggle"


class FormInputKeyManager:
    """
    Manager for generating and tracking dynamic keys for form inputs.

    This class provides methods to attach dynamic keys to all types of
    form inputs, create key mappings, and manage key-based data retrieval.
    """

    def __init__(self):
        """Initialize the form input key manager"""
        self.key_index = get_global_key_index()
        self.form_mappings: Dict[str, Dict[str, Any]] = {}
        self.input_registry: Dict[str, 'FormInput'] = {}

    def create_input_key(
        self,
        input_type: FormInputType,
        form_id: str,
        field_name: str,
        custom_suffix: Optional[str] = None
    ) -> str:
        """
        Create a dynamic key for a form input.

        Args:
            input_type: Type of the form input
            form_id: ID of the form containing the input
            field_name: Name of the input field
            custom_suffix: Optional custom suffix

        Returns:
            Generated dynamic key

        Example:
            >>> manager = FormInputKeyManager()
            >>> key = manager.create_input_key(
            ...     FormInputType.TEXT,
            ...     "solar_calc_form",
            ...     "roof_area"
            ... )
            >>> print(key)
            'FRM_20231116_143052_a1b2c3d4_solar_calc_form_roof_area'
        """
        # Create composite suffix
        suffix_parts = [form_id, field_name]
        if custom_suffix:
            suffix_parts.append(custom_suffix)
        suffix = "_".join(suffix_parts)

        # Generate key using mixin
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            prefix=KeyPrefix.DATA,
            include_timestamp=True,
            include_uuid=True,
            custom_suffix=suffix
        )

        # Store metadata
        metadata = {
            'input_type': input_type.value,
            'form_id': form_id,
            'field_name': field_name,
            'created_at': datetime.now().isoformat()
        }

        self.key_index.add(key, None, metadata)

        return key

    def register_form_input(
        self,
        form_id: str,
        field_name: str,
        input_type: FormInputType,
        label: str,
        default_value: Any = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'FormInput':
        """
        Register a form input with dynamic key.

        Args:
            form_id: ID of the form
            field_name: Name of the field
            input_type: Type of input
            label: Display label
            default_value: Default value for the input
            validation_rules: Validation rules
            metadata: Additional metadata

        Returns:
            FormInput object with dynamic key
        """
        # Create dynamic key
        key = self.create_input_key(input_type, form_id, field_name)

        # Create FormInput object
        form_input = FormInput(
            key=key,
            form_id=form_id,
            field_name=field_name,
            input_type=input_type,
            label=label,
            default_value=default_value,
            validation_rules=validation_rules or {},
            metadata=metadata or {}
        )

        # Register in registry
        self.input_registry[key] = form_input

        # Add to form mapping
        if form_id not in self.form_mappings:
            self.form_mappings[form_id] = {}
        self.form_mappings[form_id][field_name] = key

        return form_input

    def get_input_by_key(self, key: str) -> Optional['FormInput']:
        """
        Retrieve a form input by its dynamic key.

        Args:
            key: Dynamic key to lookup

        Returns:
            FormInput object or None if not found
        """
        return self.input_registry.get(key)

    def get_input_by_field(
        self,
        form_id: str,
        field_name: str
    ) -> Optional['FormInput']:
        """
        Retrieve a form input by form ID and field name.

        Args:
            form_id: ID of the form
            field_name: Name of the field

        Returns:
            FormInput object or None if not found
        """
        if form_id not in self.form_mappings:
            return None

        key = self.form_mappings[form_id].get(field_name)
        if not key:
            return None

        return self.input_registry.get(key)

    def get_form_inputs(self, form_id: str) -> List['FormInput']:
        """
        Get all inputs for a specific form.

        Args:
            form_id: ID of the form

        Returns:
            List of FormInput objects
        """
        if form_id not in self.form_mappings:
            return []

        keys = self.form_mappings[form_id].values()
        return [
            self.input_registry[key]
            for key in keys
            if key in self.input_registry
        ]

    def get_form_key_mapping(self, form_id: str) -> Dict[str, str]:
        """
        Get the key mapping for a form (field_name -> dynamic_key).

        Args:
            form_id: ID of the form

        Returns:
            Dictionary mapping field names to dynamic keys
        """
        return self.form_mappings.get(form_id, {}).copy()

    def update_input_value(
        self,
        key: str,
        value: Any,
        validate: bool = True
    ) -> bool:
        """
        Update the value of a form input.

        Args:
            key: Dynamic key of the input
            value: New value
            validate: Whether to validate the value

        Returns:
            True if update successful, False otherwise
        """
        form_input = self.get_input_by_key(key)
        if not form_input:
            return False

        if validate:
            is_valid, error = form_input.validate_value(value)
            if not is_valid:
                raise ValueError(f"Validation failed: {error}")

        form_input.set_value(value)
        return True

    def get_input_value(self, key: str) -> Any:
        """
        Get the current value of a form input.

        Args:
            key: Dynamic key of the input

        Returns:
            Current value or None if not found
        """
        form_input = self.get_input_by_key(key)
        return form_input.get_value() if form_input else None

    def get_form_data(
        self,
        form_id: str,
        include_keys: bool = False
    ) -> Dict[str, Any]:
        """
        Get all data from a form.

        Args:
            form_id: ID of the form
            include_keys: Whether to include dynamic keys in output

        Returns:
            Dictionary of form data
        """
        inputs = self.get_form_inputs(form_id)
        data = {}

        for input_obj in inputs:
            if include_keys:
                data[input_obj.field_name] = {
                    'value': input_obj.get_value(),
                    'key': input_obj.key,
                    'type': input_obj.input_type.value
                }
            else:
                data[input_obj.field_name] = input_obj.get_value()

        return data

    def set_form_data(
        self,
        form_id: str,
        data: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, str]:
        """
        Set data for multiple form inputs.

        Args:
            form_id: ID of the form
            data: Dictionary of field_name -> value
            validate: Whether to validate values

        Returns:
            Dictionary of field_name -> error_message for failed fields
        """
        errors = {}

        for field_name, value in data.items():
            form_input = self.get_input_by_field(form_id, field_name)
            if not form_input:
                errors[field_name] = "Field not found"
                continue

            if validate:
                is_valid, error = form_input.validate_value(value)
                if not is_valid:
                    errors[field_name] = error
                    continue

            form_input.set_value(value)

        return errors

    def validate_form(self, form_id: str) -> tuple[bool, Dict[str, str]]:
        """
        Validate all inputs in a form.

        Args:
            form_id: ID of the form

        Returns:
            Tuple of (is_valid, errors_dict)
        """
        inputs = self.get_form_inputs(form_id)
        errors = {}

        for input_obj in inputs:
            is_valid, error = input_obj.validate_value(input_obj.get_value())
            if not is_valid:
                errors[input_obj.field_name] = error

        return len(errors) == 0, errors

    def clear_form(self, form_id: str) -> None:
        """
        Clear all values in a form (reset to defaults).

        Args:
            form_id: ID of the form
        """
        inputs = self.get_form_inputs(form_id)
        for input_obj in inputs:
            input_obj.reset_to_default()

    def export_form_schema(self, form_id: str) -> Dict[str, Any]:
        """
        Export the schema of a form including all inputs and their keys.

        Args:
            form_id: ID of the form

        Returns:
            Dictionary containing form schema
        """
        inputs = self.get_form_inputs(form_id)

        return {
            'form_id': form_id,
            'inputs': [input_obj.to_dict() for input_obj in inputs],
            'key_mapping': self.get_form_key_mapping(form_id),
            'total_inputs': len(inputs)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered forms and inputs.

        Returns:
            Dictionary with statistics
        """
        total_inputs = len(self.input_registry)
        total_forms = len(self.form_mappings)

        inputs_by_type = {}
        for input_obj in self.input_registry.values():
            input_type = input_obj.input_type.value
            inputs_by_type[input_type] = inputs_by_type.get(input_type, 0) + 1

        inputs_by_form = {
            form_id: len(fields)
            for form_id, fields in self.form_mappings.items()
        }

        return {
            'total_inputs': total_inputs,
            'total_forms': total_forms,
            'inputs_by_type': inputs_by_type,
            'inputs_by_form': inputs_by_form
        }


class FormInput:
    """
    Represents a single form input with dynamic key.
    """

    def __init__(
        self,
        key: str,
        form_id: str,
        field_name: str,
        input_type: FormInputType,
        label: str,
        default_value: Any = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize form input"""
        self.key = key
        self.form_id = form_id
        self.field_name = field_name
        self.input_type = input_type
        self.label = label
        self.default_value = default_value
        self.current_value = default_value
        self.validation_rules = validation_rules or {}
        self.metadata = metadata or {}
        self.value_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def set_value(self, value: Any) -> None:
        """
        Set the current value of the input.

        Args:
            value: New value to set
        """
        # Store in history
        self.value_history.append({
            'value': self.current_value,
            'timestamp': datetime.now().isoformat()
        })

        self.current_value = value
        self.updated_at = datetime.now()

    def get_value(self) -> Any:
        """
        Get the current value of the input.

        Returns:
            Current value
        """
        return self.current_value

    def reset_to_default(self) -> None:
        """Reset the input to its default value"""
        self.set_value(self.default_value)

    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against the input's validation rules.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Required check
        if self.validation_rules.get('required', False):
            if value is None or value == '':
                return False, "This field is required"

        # Type-specific validation
        if self.input_type == FormInputType.NUMBER:
            return self._validate_number(value)
        elif self.input_type == FormInputType.EMAIL:
            return self._validate_email(value)
        elif self.input_type in [FormInputType.TEXT, FormInputType.TEXTAREA]:
            return self._validate_text(value)
        elif self.input_type == FormInputType.SELECT:
            return self._validate_select(value)

        return True, None

    def _validate_number(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate number input"""
        if value is None:
            return True, None

        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, "Must be a valid number"

        # Min/max checks
        if 'min' in self.validation_rules:
            if num_value < self.validation_rules['min']:
                return False, f"Must be at least {self.validation_rules['min']}"

        if 'max' in self.validation_rules:
            if num_value > self.validation_rules['max']:
                return False, f"Must be at most {self.validation_rules['max']}"

        return True, None

    def _validate_email(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate email input"""
        if value is None or value == '':
            return True, None

        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(value)):
            return False, "Must be a valid email address"

        return True, None

    def _validate_text(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate text input"""
        if value is None:
            return True, None

        text_value = str(value)

        # Length checks
        if 'minLength' in self.validation_rules:
            if len(text_value) < self.validation_rules['minLength']:
                min_len = self.validation_rules['minLength']
                return False, f"Must be at least {min_len} characters"

        if 'maxLength' in self.validation_rules:
            if len(text_value) > self.validation_rules['maxLength']:
                max_len = self.validation_rules['maxLength']
                return False, f"Must be at most {max_len} characters"

        # Pattern check
        if 'pattern' in self.validation_rules:
            import re
            if not re.match(self.validation_rules['pattern'], text_value):
                return False, "Invalid format"

        return True, None

    def _validate_select(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate select input"""
        if value is None:
            return True, None

        # Check if value is in allowed options
        if 'options' in self.validation_rules:
            allowed = self.validation_rules['options']
            if value not in allowed:
                return False, "Invalid selection"

        return True, None

    def get_value_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of value changes.

        Returns:
            List of value history entries
        """
        return self.value_history.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the form input to a dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'key': self.key,
            'form_id': self.form_id,
            'field_name': self.field_name,
            'input_type': self.input_type.value,
            'label': self.label,
            'current_value': self.current_value,
            'default_value': self.default_value,
            'validation_rules': self.validation_rules,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'value_history_count': len(self.value_history)
        }


# Global form input key manager instance
_global_form_input_manager = FormInputKeyManager()


def get_form_input_manager() -> FormInputKeyManager:
    """
    Get the global form input key manager instance.

    Returns:
        Global FormInputKeyManager instance
    """
    return _global_form_input_manager
