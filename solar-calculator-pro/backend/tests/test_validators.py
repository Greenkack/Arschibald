"""
Tests for the Validation Framework

Tests all validator types and validation scenarios.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.validators import (
    ValidationError,
    ValidationResult,
    NumberValidator,
    StringValidator,
    DateTimeValidator,
    EmailValidator,
    URLValidator,
    CompositeValidator,
    DictValidator,
    ListValidator,
    validate_number,
    validate_string,
    validate_date,
    validate_email,
    validate_url
)


class TestValidationError:
    """Test ValidationError class"""
    
    def test_validation_error_creation(self):
        """Test creating a validation error"""
        error = ValidationError(
            message="Test error",
            field="test_field",
            value="test_value",
            code="TEST_ERROR"
        )
        
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.value == "test_value"
        assert error.code == "TEST_ERROR"
    
    def test_validation_error_to_dict(self):
        """Test converting error to dictionary"""
        error = ValidationError(
            message="Test error",
            field="test_field",
            value="test_value"
        )
        
        error_dict = error.to_dict()
        assert error_dict["message"] == "Test error"
        assert error_dict["field"] == "test_field"
        assert error_dict["value"] == "test_value"
        assert "code" in error_dict


class TestValidationResult:
    """Test ValidationResult class"""
    
    def test_valid_result(self):
        """Test creating a valid result"""
        result = ValidationResult()
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_adding_error(self):
        """Test adding an error to result"""
        result = ValidationResult()
        error = ValidationError("Test error")
        result.add_error(error)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == error


class TestNumberValidator:
    """Test NumberValidator class"""
    
    def test_valid_integer(self):
        """Test validating a valid integer"""
        validator = NumberValidator(field_name="age")
        result = validator.validate(25)
        assert result.is_valid is True
    
    def test_valid_float(self):
        """Test validating a valid float"""
        validator = NumberValidator(field_name="price")
        result = validator.validate(19.99)
        assert result.is_valid is True
    
    def test_valid_decimal(self):
        """Test validating a valid Decimal"""
        validator = NumberValidator(field_name="amount")
        result = validator.validate(Decimal("123.45"))
        assert result.is_valid is True
    
    def test_string_number(self):
        """Test validating a string number"""
        validator = NumberValidator(field_name="count")
        result = validator.validate("42")
        assert result.is_valid is True
    
    def test_german_format(self):
        """Test validating German number format"""
        validator = NumberValidator(field_name="price", german_format=True)
        result = validator.validate("1.234,56")
        assert result.is_valid is True
    
    def test_required_field(self):
        """Test required field validation"""
        validator = NumberValidator(field_name="age", required=True)
        result = validator.validate(None)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "REQUIRED_FIELD"
    
    def test_min_value(self):
        """Test minimum value validation"""
        validator = NumberValidator(field_name="age", min_value=18)
        result = validator.validate(15)
        assert result.is_valid is False
        assert result.errors[0].code == "VALUE_TOO_SMALL"
    
    def test_max_value(self):
        """Test maximum value validation"""
        validator = NumberValidator(field_name="percentage", max_value=100)
        result = validator.validate(150)
        assert result.is_valid is False
        assert result.errors[0].code == "VALUE_TOO_LARGE"
    
    def test_negative_not_allowed(self):
        """Test negative value validation"""
        validator = NumberValidator(field_name="count", allow_negative=False)
        result = validator.validate(-5)
        assert result.is_valid is False
        assert result.errors[0].code == "NEGATIVE_NOT_ALLOWED"
    
    def test_decimal_not_allowed(self):
        """Test decimal not allowed validation"""
        validator = NumberValidator(field_name="count", allow_decimal=False)
        result = validator.validate(5.5)
        assert result.is_valid is False
        assert result.errors[0].code == "DECIMAL_NOT_ALLOWED"
    
    def test_decimal_places(self):
        """Test decimal places validation"""
        validator = NumberValidator(field_name="price", decimal_places=2)
        result = validator.validate(19.999)
        assert result.is_valid is False
        assert result.errors[0].code == "TOO_MANY_DECIMAL_PLACES"
    
    def test_invalid_format(self):
        """Test invalid number format"""
        validator = NumberValidator(field_name="value")
        result = validator.validate("not a number")
        assert result.is_valid is False
        assert result.errors[0].code == "INVALID_NUMBER_FORMAT"
    
    def test_custom_validator(self):
        """Test custom validator"""
        validator = NumberValidator(field_name="even_number")
        validator.add_custom_validator(
            lambda x: x % 2 == 0,
            "Number must be even"
        )
        
        result = validator.validate(5)
        assert result.is_valid is False
        assert result.errors[0].code == "CUSTOM_VALIDATION_FAILED"


class TestStringValidator:
    """Test StringValidator class"""
    
    def test_valid_string(self):
        """Test validating a valid string"""
        validator = StringValidator(field_name="name")
        result = validator.validate("John Doe")
        assert result.is_valid is True
    
    def test_required_field(self):
        """Test required field validation"""
        validator = StringValidator(field_name="name", required=True)
        result = validator.validate("")
        assert result.is_valid is False
        assert result.errors[0].code == "REQUIRED_FIELD"
    
    def test_min_length(self):
        """Test minimum length validation"""
        validator = StringValidator(field_name="password", min_length=8)
        result = validator.validate("short")
        assert result.is_valid is False
        assert result.errors[0].code == "STRING_TOO_SHORT"
    
    def test_max_length(self):
        """Test maximum length validation"""
        validator = StringValidator(field_name="username", max_length=20)
        result = validator.validate("a" * 25)
        assert result.is_valid is False
        assert result.errors[0].code == "STRING_TOO_LONG"
    
    def test_pattern(self):
        """Test pattern validation"""
        validator = StringValidator(field_name="code", pattern=r'^[A-Z]{3}\d{3}$')
        result = validator.validate("ABC123")
        assert result.is_valid is True
        
        result = validator.validate("abc123")
        assert result.is_valid is False
        assert result.errors[0].code == "PATTERN_MISMATCH"
    
    def test_allowed_values(self):
        """Test allowed values validation"""
        validator = StringValidator(
            field_name="status",
            allowed_values=["active", "inactive", "pending"]
        )
        result = validator.validate("active")
        assert result.is_valid is True
        
        result = validator.validate("unknown")
        assert result.is_valid is False
        assert result.errors[0].code == "INVALID_VALUE"
    
    def test_trim(self):
        """Test string trimming"""
        validator = StringValidator(field_name="name", trim=True, max_length=5)
        result = validator.validate("  test  ")
        assert result.is_valid is True
    
    def test_lowercase(self):
        """Test lowercase transformation"""
        validator = StringValidator(field_name="email", lowercase=True)
        result = validator.validate("TEST@EXAMPLE.COM")
        assert result.is_valid is True
    
    def test_uppercase(self):
        """Test uppercase transformation"""
        validator = StringValidator(field_name="code", uppercase=True)
        result = validator.validate("abc123")
        assert result.is_valid is True


class TestDateTimeValidator:
    """Test DateTimeValidator class"""
    
    def test_valid_date(self):
        """Test validating a valid date"""
        validator = DateTimeValidator(field_name="birth_date")
        result = validator.validate(date(1990, 1, 1))
        assert result.is_valid is True
    
    def test_valid_datetime(self):
        """Test validating a valid datetime"""
        validator = DateTimeValidator(field_name="created_at")
        result = validator.validate(datetime(2023, 1, 1, 12, 0, 0))
        assert result.is_valid is True
    
    def test_string_date(self):
        """Test validating a string date"""
        validator = DateTimeValidator(field_name="date", date_format="%Y-%m-%d")
        result = validator.validate("2023-01-01")
        assert result.is_valid is True
    
    def test_invalid_format(self):
        """Test invalid date format"""
        validator = DateTimeValidator(field_name="date", date_format="%Y-%m-%d")
        result = validator.validate("01/01/2023")
        assert result.is_valid is False
        assert result.errors[0].code == "INVALID_DATE_FORMAT"
    
    def test_future_not_allowed(self):
        """Test future date not allowed"""
        validator = DateTimeValidator(field_name="birth_date", allow_future=False)
        future_date = date.today() + timedelta(days=1)
        result = validator.validate(future_date)
        assert result.is_valid is False
        assert result.errors[0].code == "FUTURE_DATE_NOT_ALLOWED"
    
    def test_past_not_allowed(self):
        """Test past date not allowed"""
        validator = DateTimeValidator(field_name="appointment", allow_past=False)
        past_date = date.today() - timedelta(days=1)
        result = validator.validate(past_date)
        assert result.is_valid is False
        assert result.errors[0].code == "PAST_DATE_NOT_ALLOWED"
    
    def test_min_date(self):
        """Test minimum date validation"""
        min_date = date(2020, 1, 1)
        validator = DateTimeValidator(field_name="date", min_date=min_date)
        result = validator.validate(date(2019, 12, 31))
        assert result.is_valid is False
        assert result.errors[0].code == "DATE_TOO_EARLY"
    
    def test_max_date(self):
        """Test maximum date validation"""
        max_date = date(2025, 12, 31)
        validator = DateTimeValidator(field_name="date", max_date=max_date)
        result = validator.validate(date(2026, 1, 1))
        assert result.is_valid is False
        assert result.errors[0].code == "DATE_TOO_LATE"


class TestEmailValidator:
    """Test EmailValidator class"""
    
    def test_valid_email(self):
        """Test validating a valid email"""
        validator = EmailValidator(field_name="email")
        result = validator.validate("user@example.com")
        assert result.is_valid is True
    
    def test_invalid_email(self):
        """Test validating an invalid email"""
        validator = EmailValidator(field_name="email")
        
        # Missing @
        result = validator.validate("userexample.com")
        assert result.is_valid is False
        
        # Missing domain
        result = validator.validate("user@")
        assert result.is_valid is False
        
        # Double dots
        result = validator.validate("user..name@example.com")
        assert result.is_valid is False
    
    def test_email_lowercase(self):
        """Test email is converted to lowercase"""
        validator = EmailValidator(field_name="email")
        result = validator.validate("USER@EXAMPLE.COM")
        assert result.is_valid is True


class TestURLValidator:
    """Test URLValidator class"""
    
    def test_valid_url(self):
        """Test validating a valid URL"""
        validator = URLValidator(field_name="website")
        result = validator.validate("https://example.com")
        assert result.is_valid is True
        
        result = validator.validate("http://example.com/path?query=value")
        assert result.is_valid is True
    
    def test_invalid_url(self):
        """Test validating an invalid URL"""
        validator = URLValidator(field_name="website")
        result = validator.validate("not a url")
        assert result.is_valid is False
    
    def test_https_required(self):
        """Test HTTPS requirement"""
        validator = URLValidator(field_name="website", require_https=True)
        result = validator.validate("http://example.com")
        assert result.is_valid is False
        assert result.errors[0].code == "HTTPS_REQUIRED"
        
        result = validator.validate("https://example.com")
        assert result.is_valid is True


class TestCompositeValidator:
    """Test CompositeValidator class"""
    
    def test_all_validators_pass(self):
        """Test when all validators pass"""
        validators = [
            NumberValidator(field_name="age", min_value=18),
            NumberValidator(field_name="age", max_value=100)
        ]
        composite = CompositeValidator(validators)
        result = composite.validate(25)
        assert result.is_valid is True
    
    def test_one_validator_fails(self):
        """Test when one validator fails"""
        validators = [
            NumberValidator(field_name="age", min_value=18),
            NumberValidator(field_name="age", max_value=100)
        ]
        composite = CompositeValidator(validators)
        result = composite.validate(15)
        assert result.is_valid is False
        assert len(result.errors) == 1
    
    def test_stop_on_first_error(self):
        """Test stop on first error"""
        validators = [
            NumberValidator(field_name="age", min_value=18),
            NumberValidator(field_name="age", max_value=100)
        ]
        composite = CompositeValidator(validators, stop_on_first_error=True)
        result = composite.validate(150)  # Fails both validators
        assert result.is_valid is False
        assert len(result.errors) == 1  # Only first error


class TestDictValidator:
    """Test DictValidator class"""
    
    def test_valid_dict(self):
        """Test validating a valid dictionary"""
        schema = {
            "name": StringValidator(field_name="name", required=True),
            "age": NumberValidator(field_name="age", min_value=0),
            "email": EmailValidator(field_name="email")
        }
        validator = DictValidator(schema)
        
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        result = validator.validate(data)
        assert result.is_valid is True
    
    def test_invalid_dict(self):
        """Test validating an invalid dictionary"""
        schema = {
            "name": StringValidator(field_name="name", required=True),
            "age": NumberValidator(field_name="age", min_value=0)
        }
        validator = DictValidator(schema)
        
        data = {
            "name": "",
            "age": -5
        }
        result = validator.validate(data)
        assert result.is_valid is False
        assert len(result.errors) == 2
    
    def test_not_a_dict(self):
        """Test validating a non-dictionary value"""
        schema = {"name": StringValidator(field_name="name")}
        validator = DictValidator(schema)
        
        result = validator.validate("not a dict")
        assert result.is_valid is False
        assert result.errors[0].code == "INVALID_TYPE"


class TestListValidator:
    """Test ListValidator class"""
    
    def test_valid_list(self):
        """Test validating a valid list"""
        item_validator = NumberValidator(field_name="item", min_value=0)
        validator = ListValidator(item_validator, field_name="numbers")
        
        result = validator.validate([1, 2, 3, 4, 5])
        assert result.is_valid is True
    
    def test_invalid_items(self):
        """Test validating a list with invalid items"""
        item_validator = NumberValidator(field_name="item", min_value=0)
        validator = ListValidator(item_validator, field_name="numbers")
        
        result = validator.validate([1, -2, 3, -4, 5])
        assert result.is_valid is False
        assert len(result.errors) == 2  # Two negative numbers
    
    def test_min_items(self):
        """Test minimum items validation"""
        item_validator = StringValidator(field_name="item")
        validator = ListValidator(
            item_validator,
            field_name="tags",
            min_items=3
        )
        
        result = validator.validate(["tag1", "tag2"])
        assert result.is_valid is False
        assert result.errors[0].code == "TOO_FEW_ITEMS"
    
    def test_max_items(self):
        """Test maximum items validation"""
        item_validator = StringValidator(field_name="item")
        validator = ListValidator(
            item_validator,
            field_name="tags",
            max_items=3
        )
        
        result = validator.validate(["tag1", "tag2", "tag3", "tag4"])
        assert result.is_valid is False
        assert result.errors[0].code == "TOO_MANY_ITEMS"
    
    def test_unique_items(self):
        """Test unique items validation"""
        item_validator = StringValidator(field_name="item")
        validator = ListValidator(
            item_validator,
            field_name="tags",
            unique=True
        )
        
        result = validator.validate(["tag1", "tag2", "tag1"])
        assert result.is_valid is False
        assert result.errors[0].code == "DUPLICATE_ITEMS"
    
    def test_not_a_list(self):
        """Test validating a non-list value"""
        item_validator = StringValidator(field_name="item")
        validator = ListValidator(item_validator, field_name="tags")
        
        result = validator.validate("not a list")
        assert result.is_valid is False
        assert result.errors[0].code == "INVALID_TYPE"


class TestConvenienceFunctions:
    """Test convenience validation functions"""
    
    def test_validate_number(self):
        """Test validate_number convenience function"""
        result = validate_number(42, field_name="age", min_value=18)
        assert result.is_valid is True
        
        result = validate_number(15, field_name="age", min_value=18)
        assert result.is_valid is False
    
    def test_validate_string(self):
        """Test validate_string convenience function"""
        result = validate_string("hello", field_name="greeting", min_length=3)
        assert result.is_valid is True
        
        result = validate_string("hi", field_name="greeting", min_length=3)
        assert result.is_valid is False
    
    def test_validate_date(self):
        """Test validate_date convenience function"""
        result = validate_date(date.today(), field_name="date")
        assert result.is_valid is True
    
    def test_validate_email(self):
        """Test validate_email convenience function"""
        result = validate_email("user@example.com")
        assert result.is_valid is True
        
        result = validate_email("invalid-email")
        assert result.is_valid is False
    
    def test_validate_url(self):
        """Test validate_url convenience function"""
        result = validate_url("https://example.com")
        assert result.is_valid is True
        
        result = validate_url("not a url")
        assert result.is_valid is False
