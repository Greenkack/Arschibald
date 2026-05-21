"""
Request Validation Utilities

Provides comprehensive validation functions for request data.
"""

from typing import Any, List, Optional, Union
from pydantic import BaseModel, validator, Field
from datetime import datetime
import re
from backend.core.exceptions import (
    ValidationError,
    InvalidInputError,
    MissingRequiredFieldError,
    InvalidFormatError
)


class ValidationRules:
    """Common validation rules"""
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Phone number pattern (international format - at least 7 digits)
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{6,14}$')
    
    # German postal code pattern
    POSTAL_CODE_DE_PATTERN = re.compile(r'^\d{5}$')
    
    # Password strength pattern (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        return bool(ValidationRules.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        return bool(ValidationRules.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_postal_code_de(postal_code: str) -> bool:
        """Validate German postal code"""
        return bool(ValidationRules.POSTAL_CODE_DE_PATTERN.match(postal_code))
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password strength"""
        return bool(ValidationRules.PASSWORD_PATTERN.match(password))
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None, 
                      max_val: Optional[Union[int, float]] = None) -> bool:
        """Validate numeric value is within range"""
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
    
    @staticmethod
    def validate_length(value: str, min_length: Optional[int] = None, 
                       max_length: Optional[int] = None) -> bool:
        """Validate string length"""
        length = len(value)
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
    
    @staticmethod
    def validate_enum(value: Any, allowed_values: List[Any]) -> bool:
        """Validate value is in allowed list"""
        return value in allowed_values
    
    @staticmethod
    def validate_date_range(date: datetime, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> bool:
        """Validate date is within range"""
        if start_date and date < start_date:
            return False
        if end_date and date > end_date:
            return False
        return True


class Validator:
    """Validation helper class"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str):
        """Validate required field"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise MissingRequiredFieldError(field_name)
    
    @staticmethod
    def validate_email(email: str, field_name: str = "email"):
        """Validate email and raise exception if invalid"""
        if not ValidationRules.validate_email(email):
            raise InvalidFormatError(
                field=field_name,
                expected_format="valid email address (e.g., user@example.com)",
                value=email
            )
    
    @staticmethod
    def validate_phone(phone: str, field_name: str = "phone"):
        """Validate phone number and raise exception if invalid"""
        if not ValidationRules.validate_phone(phone):
            raise InvalidFormatError(
                field=field_name,
                expected_format="international phone format (e.g., +491234567890)",
                value=phone
            )
    
    @staticmethod
    def validate_password(password: str, field_name: str = "password"):
        """Validate password strength and raise exception if weak"""
        if not ValidationRules.validate_password_strength(password):
            raise InvalidInputError(
                field=field_name,
                message="Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 digit",
                value="***"  # Don't expose password
            )
    
    @staticmethod
    def validate_range(value: Union[int, float], field_name: str, 
                      min_val: Optional[Union[int, float]] = None,
                      max_val: Optional[Union[int, float]] = None):
        """Validate numeric range and raise exception if out of bounds"""
        if not ValidationRules.validate_range(value, min_val, max_val):
            range_str = ""
            if min_val is not None and max_val is not None:
                range_str = f"between {min_val} and {max_val}"
            elif min_val is not None:
                range_str = f"at least {min_val}"
            elif max_val is not None:
                range_str = f"at most {max_val}"
            
            raise InvalidInputError(
                field=field_name,
                message=f"Value must be {range_str}",
                value=value
            )
    
    @staticmethod
    def validate_length(value: str, field_name: str,
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None):
        """Validate string length and raise exception if invalid"""
        if not ValidationRules.validate_length(value, min_length, max_length):
            length_str = ""
            if min_length is not None and max_length is not None:
                length_str = f"between {min_length} and {max_length} characters"
            elif min_length is not None:
                length_str = f"at least {min_length} characters"
            elif max_length is not None:
                length_str = f"at most {max_length} characters"
            
            raise InvalidInputError(
                field=field_name,
                message=f"Length must be {length_str}",
                value=f"{len(value)} characters"
            )
    
    @staticmethod
    def validate_enum(value: Any, field_name: str, allowed_values: List[Any]):
        """Validate enum value and raise exception if not in allowed list"""
        if not ValidationRules.validate_enum(value, allowed_values):
            raise InvalidInputError(
                field=field_name,
                message=f"Value must be one of: {', '.join(map(str, allowed_values))}",
                value=value
            )
    
    @staticmethod
    def validate_positive(value: Union[int, float], field_name: str):
        """Validate value is positive"""
        if value <= 0:
            raise InvalidInputError(
                field=field_name,
                message="Value must be positive (greater than 0)",
                value=value
            )
    
    @staticmethod
    def validate_non_negative(value: Union[int, float], field_name: str):
        """Validate value is non-negative"""
        if value < 0:
            raise InvalidInputError(
                field=field_name,
                message="Value must be non-negative (0 or greater)",
                value=value
            )
    
    @staticmethod
    def validate_german_number_format(value: str, field_name: str) -> float:
        """
        Validate and parse German number format (1.234,56)
        Returns the parsed float value
        """
        try:
            # Remove thousand separators (.)
            without_thousands = value.replace('.', '')
            # Replace decimal comma with dot
            standard_format = without_thousands.replace(',', '.')
            return float(standard_format)
        except (ValueError, AttributeError):
            raise InvalidFormatError(
                field=field_name,
                expected_format="German number format (e.g., 1.234,56)",
                value=value
            )
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str], field_name: str = "file"):
        """Validate file extension"""
        if not any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
            raise InvalidInputError(
                field=field_name,
                message=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
                value=filename
            )
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_bytes: int, field_name: str = "file"):
        """Validate file size"""
        if size_bytes > max_size_bytes:
            max_mb = max_size_bytes / (1024 * 1024)
            actual_mb = size_bytes / (1024 * 1024)
            raise InvalidInputError(
                field=field_name,
                message=f"File size ({actual_mb:.2f} MB) exceeds maximum allowed size ({max_mb:.2f} MB)",
                value=f"{actual_mb:.2f} MB"
            )


# Pydantic Base Models with Common Validators

class ValidatedBaseModel(BaseModel):
    """Base model with common validation"""
    
    class Config:
        # Allow validation on assignment
        validate_assignment = True
        # Use enum values
        use_enum_values = True
        # Extra fields not allowed
        extra = 'forbid'


class PaginationParams(ValidatedBaseModel):
    """Pagination parameters with validation"""
    
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class SortParams(ValidatedBaseModel):
    """Sorting parameters with validation"""
    
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order: asc or desc")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower() if v else 'asc'


class DateRangeParams(ValidatedBaseModel):
    """Date range parameters with validation"""
    
    start_date: Optional[datetime] = Field(default=None, description="Start date")
    end_date: Optional[datetime] = Field(default=None, description="End date")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError("end_date must be after start_date")
        return v


class SearchParams(ValidatedBaseModel):
    """Search parameters with validation"""
    
    query: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Search query")
    fields: Optional[List[str]] = Field(default=None, description="Fields to search in")
    
    @validator('query')
    def validate_query(cls, v):
        if v:
            # Remove excessive whitespace
            v = ' '.join(v.split())
        return v
