"""
Validation Framework for Solar Calculator Pro Backend

This module provides a comprehensive validation system with support for:
- Base validator classes
- Number validation (including German format)
- String validation
- Date/time validation
- Custom validation rules
- Validation error handling

Requirements: 4.4, 11.3
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Callable, Union
from datetime import datetime, date, time
from decimal import Decimal, InvalidOperation
import re
from enum import Enum


class ValidationError(Exception):
    """Base exception for validation errors"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        code: Optional[str] = None
    ):
        self.message = message
        self.field = field
        self.value = value
        self.code = code or "VALIDATION_ERROR"
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        return {
            "message": self.message,
            "field": self.field,
            "value": self.value,
            "code": self.code
        }


class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[ValidationError]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: ValidationError):
        """Add an error to the result"""
        self.is_valid = False
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format"""
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors]
        }


class BaseValidator(ABC):
    """Abstract base class for all validators"""
    
    def __init__(self, field_name: Optional[str] = None, required: bool = False):
        self.field_name = field_name
        self.required = required
        self.custom_validators: List[Callable] = []
    
    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validate the given value"""
        pass
    
    def add_custom_validator(self, validator: Callable[[Any], bool], error_message: str):
        """Add a custom validation function"""
        self.custom_validators.append((validator, error_message))
        return self
    
    def _check_required(self, value: Any) -> Optional[ValidationError]:
        """Check if required field is present"""
        if self.required and (value is None or value == ""):
            return ValidationError(
                message=f"Field '{self.field_name}' is required",
                field=self.field_name,
                value=value,
                code="REQUIRED_FIELD"
            )
        return None
    
    def _run_custom_validators(self, value: Any) -> List[ValidationError]:
        """Run all custom validators"""
        errors = []
        for validator_func, error_message in self.custom_validators:
            try:
                if not validator_func(value):
                    errors.append(ValidationError(
                        message=error_message,
                        field=self.field_name,
                        value=value,
                        code="CUSTOM_VALIDATION_FAILED"
                    ))
            except Exception as e:
                errors.append(ValidationError(
                    message=f"Custom validator error: {str(e)}",
                    field=self.field_name,
                    value=value,
                    code="CUSTOM_VALIDATOR_ERROR"
                ))
        return errors


class NumberValidator(BaseValidator):
    """Validator for numeric values with German format support"""
    
    def __init__(
        self,
        field_name: Optional[str] = None,
        required: bool = False,
        min_value: Optional[Union[int, float, Decimal]] = None,
        max_value: Optional[Union[int, float, Decimal]] = None,
        allow_negative: bool = True,
        allow_decimal: bool = True,
        decimal_places: Optional[int] = None,
        german_format: bool = False
    ):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value
        self.allow_negative = allow_negative
        self.allow_decimal = allow_decimal
        self.decimal_places = decimal_places
        self.german_format = german_format
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate numeric value"""
        result = ValidationResult()
        
        # Check required
        required_error = self._check_required(value)
        if required_error:
            result.add_error(required_error)
            return result
        
        # Skip validation if value is None and not required
        if value is None:
            return result
        
        # Convert to number
        try:
            numeric_value = self._parse_number(value)
        except (ValueError, InvalidOperation) as e:
            result.add_error(ValidationError(
                message=f"Invalid number format: {str(e)}",
                field=self.field_name,
                value=value,
                code="INVALID_NUMBER_FORMAT"
            ))
            return result
        
        # Check negative
        if not self.allow_negative and numeric_value < 0:
            result.add_error(ValidationError(
                message=f"Negative values not allowed for field '{self.field_name}'",
                field=self.field_name,
                value=value,
                code="NEGATIVE_NOT_ALLOWED"
            ))
        
        # Check decimal
        if not self.allow_decimal and isinstance(numeric_value, (float, Decimal)):
            if numeric_value != int(numeric_value):
                result.add_error(ValidationError(
                    message=f"Decimal values not allowed for field '{self.field_name}'",
                    field=self.field_name,
                    value=value,
                    code="DECIMAL_NOT_ALLOWED"
                ))
        
        # Check decimal places
        if self.decimal_places is not None and isinstance(numeric_value, (float, Decimal)):
            decimal_str = str(numeric_value).split('.')
            if len(decimal_str) > 1 and len(decimal_str[1]) > self.decimal_places:
                result.add_error(ValidationError(
                    message=f"Maximum {self.decimal_places} decimal places allowed",
                    field=self.field_name,
                    value=value,
                    code="TOO_MANY_DECIMAL_PLACES"
                ))
        
        # Check min value
        if self.min_value is not None and numeric_value < self.min_value:
            result.add_error(ValidationError(
                message=f"Value must be at least {self.min_value}",
                field=self.field_name,
                value=value,
                code="VALUE_TOO_SMALL"
            ))
        
        # Check max value
        if self.max_value is not None and numeric_value > self.max_value:
            result.add_error(ValidationError(
                message=f"Value must be at most {self.max_value}",
                field=self.field_name,
                value=value,
                code="VALUE_TOO_LARGE"
            ))
        
        # Run custom validators
        for error in self._run_custom_validators(numeric_value):
            result.add_error(error)
        
        return result
    
    def _parse_number(self, value: Any) -> Union[int, float, Decimal]:
        """Parse number from various formats"""
        if isinstance(value, (int, float, Decimal)):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            
            # Handle German format (1.234,56 -> 1234.56)
            if self.german_format:
                # Remove thousand separators (.)
                value = value.replace('.', '')
                # Replace decimal comma with dot
                value = value.replace(',', '.')
            
            # Try to parse as Decimal for precision
            try:
                return Decimal(value)
            except InvalidOperation:
                # Fall back to float
                return float(value)
        
        raise ValueError(f"Cannot convert {type(value).__name__} to number")


class StringValidator(BaseValidator):
    """Validator for string values"""
    
    def __init__(
        self,
        field_name: Optional[str] = None,
        required: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        trim: bool = True,
        lowercase: bool = False,
        uppercase: bool = False
    ):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_values = allowed_values
        self.trim = trim
        self.lowercase = lowercase
        self.uppercase = uppercase
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate string value"""
        result = ValidationResult()
        
        # Check required
        required_error = self._check_required(value)
        if required_error:
            result.add_error(required_error)
            return result
        
        # Skip validation if value is None and not required
        if value is None:
            return result
        
        # Convert to string
        if not isinstance(value, str):
            value = str(value)
        
        # Apply transformations
        if self.trim:
            value = value.strip()
        if self.lowercase:
            value = value.lower()
        if self.uppercase:
            value = value.upper()
        
        # Check min length
        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(ValidationError(
                message=f"Minimum length is {self.min_length} characters",
                field=self.field_name,
                value=value,
                code="STRING_TOO_SHORT"
            ))
        
        # Check max length
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(ValidationError(
                message=f"Maximum length is {self.max_length} characters",
                field=self.field_name,
                value=value,
                code="STRING_TOO_LONG"
            ))
        
        # Check pattern
        if self.pattern and not self.pattern.match(value):
            result.add_error(ValidationError(
                message=f"Value does not match required pattern",
                field=self.field_name,
                value=value,
                code="PATTERN_MISMATCH"
            ))
        
        # Check allowed values
        if self.allowed_values and value not in self.allowed_values:
            result.add_error(ValidationError(
                message=f"Value must be one of: {', '.join(self.allowed_values)}",
                field=self.field_name,
                value=value,
                code="INVALID_VALUE"
            ))
        
        # Run custom validators
        for error in self._run_custom_validators(value):
            result.add_error(error)
        
        return result


class DateTimeValidator(BaseValidator):
    """Validator for date and time values"""
    
    def __init__(
        self,
        field_name: Optional[str] = None,
        required: bool = False,
        min_date: Optional[Union[datetime, date]] = None,
        max_date: Optional[Union[datetime, date]] = None,
        date_format: str = "%Y-%m-%d",
        allow_future: bool = True,
        allow_past: bool = True
    ):
        super().__init__(field_name, required)
        self.min_date = min_date
        self.max_date = max_date
        self.date_format = date_format
        self.allow_future = allow_future
        self.allow_past = allow_past
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate date/time value"""
        result = ValidationResult()
        
        # Check required
        required_error = self._check_required(value)
        if required_error:
            result.add_error(required_error)
            return result
        
        # Skip validation if value is None and not required
        if value is None:
            return result
        
        # Parse date
        try:
            date_value = self._parse_date(value)
        except ValueError as e:
            result.add_error(ValidationError(
                message=f"Invalid date format: {str(e)}",
                field=self.field_name,
                value=value,
                code="INVALID_DATE_FORMAT"
            ))
            return result
        
        # Check future/past
        today = datetime.now().date() if isinstance(date_value, date) else datetime.now()
        
        if not self.allow_future and date_value > today:
            result.add_error(ValidationError(
                message="Future dates are not allowed",
                field=self.field_name,
                value=value,
                code="FUTURE_DATE_NOT_ALLOWED"
            ))
        
        if not self.allow_past and date_value < today:
            result.add_error(ValidationError(
                message="Past dates are not allowed",
                field=self.field_name,
                value=value,
                code="PAST_DATE_NOT_ALLOWED"
            ))
        
        # Check min date
        if self.min_date and date_value < self.min_date:
            result.add_error(ValidationError(
                message=f"Date must be on or after {self.min_date}",
                field=self.field_name,
                value=value,
                code="DATE_TOO_EARLY"
            ))
        
        # Check max date
        if self.max_date and date_value > self.max_date:
            result.add_error(ValidationError(
                message=f"Date must be on or before {self.max_date}",
                field=self.field_name,
                value=value,
                code="DATE_TOO_LATE"
            ))
        
        # Run custom validators
        for error in self._run_custom_validators(date_value):
            result.add_error(error)
        
        return result
    
    def _parse_date(self, value: Any) -> Union[datetime, date]:
        """Parse date from various formats"""
        if isinstance(value, (datetime, date)):
            return value
        
        if isinstance(value, str):
            return datetime.strptime(value, self.date_format)
        
        raise ValueError(f"Cannot convert {type(value).__name__} to date")


class EmailValidator(StringValidator):
    """Validator for email addresses"""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __init__(self, field_name: Optional[str] = None, required: bool = False):
        super().__init__(
            field_name=field_name,
            required=required,
            pattern=self.EMAIL_PATTERN,
            trim=True,
            lowercase=True
        )
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate email address"""
        result = super().validate(value)
        
        # Additional email-specific validation
        if result.is_valid and value:
            # Check for common typos
            if '..' in value or value.startswith('.') or value.endswith('.'):
                result.add_error(ValidationError(
                    message="Invalid email format",
                    field=self.field_name,
                    value=value,
                    code="INVALID_EMAIL"
                ))
        
        return result


class URLValidator(StringValidator):
    """Validator for URLs"""
    
    URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'
    
    def __init__(
        self,
        field_name: Optional[str] = None,
        required: bool = False,
        require_https: bool = False
    ):
        super().__init__(
            field_name=field_name,
            required=required,
            pattern=self.URL_PATTERN,
            trim=True
        )
        self.require_https = require_https
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate URL"""
        result = super().validate(value)
        
        # Check HTTPS requirement
        if result.is_valid and value and self.require_https:
            if not value.startswith('https://'):
                result.add_error(ValidationError(
                    message="URL must use HTTPS protocol",
                    field=self.field_name,
                    value=value,
                    code="HTTPS_REQUIRED"
                ))
        
        return result


class CompositeValidator(BaseValidator):
    """Validator that combines multiple validators"""
    
    def __init__(
        self,
        validators: List[BaseValidator],
        field_name: Optional[str] = None,
        stop_on_first_error: bool = False
    ):
        super().__init__(field_name)
        self.validators = validators
        self.stop_on_first_error = stop_on_first_error
    
    def validate(self, value: Any) -> ValidationResult:
        """Run all validators"""
        result = ValidationResult()
        
        for validator in self.validators:
            validator_result = validator.validate(value)
            
            if not validator_result.is_valid:
                for error in validator_result.errors:
                    result.add_error(error)
                
                if self.stop_on_first_error:
                    break
        
        return result


class DictValidator:
    """Validator for dictionary/object structures"""
    
    def __init__(self, schema: Dict[str, BaseValidator]):
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate dictionary against schema"""
        result = ValidationResult()
        
        if not isinstance(data, dict):
            result.add_error(ValidationError(
                message="Value must be a dictionary",
                value=data,
                code="INVALID_TYPE"
            ))
            return result
        
        # Validate each field
        for field_name, validator in self.schema.items():
            value = data.get(field_name)
            field_result = validator.validate(value)
            
            if not field_result.is_valid:
                for error in field_result.errors:
                    result.add_error(error)
        
        return result


class ListValidator(BaseValidator):
    """Validator for list/array values"""
    
    def __init__(
        self,
        item_validator: BaseValidator,
        field_name: Optional[str] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique: bool = False
    ):
        super().__init__(field_name, required)
        self.item_validator = item_validator
        self.min_items = min_items
        self.max_items = max_items
        self.unique = unique
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate list value"""
        result = ValidationResult()
        
        # Check required
        required_error = self._check_required(value)
        if required_error:
            result.add_error(required_error)
            return result
        
        # Skip validation if value is None and not required
        if value is None:
            return result
        
        # Check if value is a list
        if not isinstance(value, (list, tuple)):
            result.add_error(ValidationError(
                message="Value must be a list",
                field=self.field_name,
                value=value,
                code="INVALID_TYPE"
            ))
            return result
        
        # Check min items
        if self.min_items is not None and len(value) < self.min_items:
            result.add_error(ValidationError(
                message=f"List must contain at least {self.min_items} items",
                field=self.field_name,
                value=value,
                code="TOO_FEW_ITEMS"
            ))
        
        # Check max items
        if self.max_items is not None and len(value) > self.max_items:
            result.add_error(ValidationError(
                message=f"List must contain at most {self.max_items} items",
                field=self.field_name,
                value=value,
                code="TOO_MANY_ITEMS"
            ))
        
        # Check uniqueness
        if self.unique and len(value) != len(set(value)):
            result.add_error(ValidationError(
                message="List items must be unique",
                field=self.field_name,
                value=value,
                code="DUPLICATE_ITEMS"
            ))
        
        # Validate each item
        for i, item in enumerate(value):
            item_result = self.item_validator.validate(item)
            if not item_result.is_valid:
                for error in item_result.errors:
                    error.field = f"{self.field_name}[{i}]"
                    result.add_error(error)
        
        return result


# Convenience functions for common validations

def validate_number(
    value: Any,
    field_name: str = "value",
    **kwargs
) -> ValidationResult:
    """Convenience function for number validation"""
    validator = NumberValidator(field_name=field_name, **kwargs)
    return validator.validate(value)


def validate_string(
    value: Any,
    field_name: str = "value",
    **kwargs
) -> ValidationResult:
    """Convenience function for string validation"""
    validator = StringValidator(field_name=field_name, **kwargs)
    return validator.validate(value)


def validate_date(
    value: Any,
    field_name: str = "value",
    **kwargs
) -> ValidationResult:
    """Convenience function for date validation"""
    validator = DateTimeValidator(field_name=field_name, **kwargs)
    return validator.validate(value)


def validate_email(
    value: Any,
    field_name: str = "email",
    **kwargs
) -> ValidationResult:
    """Convenience function for email validation"""
    validator = EmailValidator(field_name=field_name, **kwargs)
    return validator.validate(value)


def validate_url(
    value: Any,
    field_name: str = "url",
    **kwargs
) -> ValidationResult:
    """Convenience function for URL validation"""
    validator = URLValidator(field_name=field_name, **kwargs)
    return validator.validate(value)
