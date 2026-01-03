"""
Custom Exception Classes

Provides a comprehensive set of custom exceptions for different error scenarios.
"""

from typing import Any, Dict, Optional
from fastapi import status


class BaseAPIException(Exception):
    """Base exception for all API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


# Authentication & Authorization Exceptions

class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            error_code="AUTH_FAILED"
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(
            message=message,
            details={"hint": "Please check your credentials and try again"}
        )
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired"""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            details={"hint": "Please login again to get a new token"}
        )
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid"""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(
            message=message,
            details={"hint": "Token format is invalid or corrupted"}
        )
        self.error_code = "INVALID_TOKEN"


class AuthorizationError(BaseAPIException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "Insufficient permissions", required_permission: Optional[str] = None):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
            details["hint"] = f"You need '{required_permission}' permission to perform this action"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
            error_code="INSUFFICIENT_PERMISSIONS"
        )


# Resource Exceptions

class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "resource_type": resource_type,
                "resource_id": str(resource_id),
                "hint": f"The requested {resource_type.lower()} does not exist"
            },
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceAlreadyExistsError(BaseAPIException):
    """Raised when trying to create a resource that already exists"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={
                "resource_type": resource_type,
                "identifier": identifier,
                "hint": f"A {resource_type.lower()} with this identifier already exists"
            },
            error_code="RESOURCE_ALREADY_EXISTS"
        )


class ResourceConflictError(BaseAPIException):
    """Raised when there's a conflict with resource state"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
            error_code="RESOURCE_CONFLICT"
        )


# Validation Exceptions

class ValidationError(BaseAPIException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {"message": message}
        if field:
            details["field"] = field
        if value is not None:
            details["provided_value"] = str(value)
        
        super().__init__(
            message=f"Validation error: {message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            error_code="VALIDATION_ERROR"
        )


class InvalidInputError(ValidationError):
    """Raised when input data is invalid"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(
            message=f"Invalid value for field '{field}': {message}",
            field=field,
            value=value
        )
        self.error_code = "INVALID_INPUT"


class MissingRequiredFieldError(ValidationError):
    """Raised when a required field is missing"""
    
    def __init__(self, field: str):
        super().__init__(
            message=f"Required field '{field}' is missing",
            field=field
        )
        self.error_code = "MISSING_REQUIRED_FIELD"


class InvalidFormatError(ValidationError):
    """Raised when data format is invalid"""
    
    def __init__(self, field: str, expected_format: str, value: Any = None):
        super().__init__(
            message=f"Invalid format for field '{field}'. Expected: {expected_format}",
            field=field,
            value=value
        )
        self.details["expected_format"] = expected_format
        self.error_code = "INVALID_FORMAT"


# Business Logic Exceptions

class BusinessLogicError(BaseAPIException):
    """Raised when business logic validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
            error_code="BUSINESS_LOGIC_ERROR"
        )


class CalculationError(BusinessLogicError):
    """Raised when a calculation fails"""
    
    def __init__(self, calculation_type: str, reason: str):
        super().__init__(
            message=f"Calculation failed: {reason}",
            details={
                "calculation_type": calculation_type,
                "reason": reason
            }
        )
        self.error_code = "CALCULATION_ERROR"


class InvalidStateError(BusinessLogicError):
    """Raised when an operation is attempted on an invalid state"""
    
    def __init__(self, current_state: str, required_state: str):
        super().__init__(
            message=f"Invalid state for this operation",
            details={
                "current_state": current_state,
                "required_state": required_state,
                "hint": f"Resource must be in '{required_state}' state"
            }
        )
        self.error_code = "INVALID_STATE"


# Database Exceptions

class DatabaseError(BaseAPIException):
    """Raised when a database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="DATABASE_ERROR"
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(
            message=message,
            details={"hint": "Please check database configuration and connectivity"}
        )
        self.error_code = "DATABASE_CONNECTION_ERROR"


class DatabaseIntegrityError(DatabaseError):
    """Raised when database integrity constraint is violated"""
    
    def __init__(self, constraint: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"Database integrity constraint violated: {constraint}",
            details={
                "constraint": constraint,
                "hint": "This operation violates database constraints"
            }
        )
        self.error_code = "DATABASE_INTEGRITY_ERROR"


# External Service Exceptions

class ExternalServiceError(BaseAPIException):
    """Raised when an external service call fails"""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External service error ({service_name}): {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details or {},
            error_code="EXTERNAL_SERVICE_ERROR"
        )
        self.details["service_name"] = service_name


class ServiceUnavailableError(BaseAPIException):
    """Raised when a service is temporarily unavailable"""
    
    def __init__(self, service_name: str, retry_after: Optional[int] = None):
        details = {"service_name": service_name}
        if retry_after:
            details["retry_after"] = retry_after
            details["hint"] = f"Service will be available in approximately {retry_after} seconds"
        
        super().__init__(
            message=f"Service temporarily unavailable: {service_name}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
            error_code="SERVICE_UNAVAILABLE"
        )


# File & Upload Exceptions

class FileError(BaseAPIException):
    """Raised when file operations fail"""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        details = {}
        if filename:
            details["filename"] = filename
        
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
            error_code="FILE_ERROR"
        )


class InvalidFileTypeError(FileError):
    """Raised when file type is not allowed"""
    
    def __init__(self, filename: str, allowed_types: list):
        super().__init__(
            message=f"Invalid file type for '{filename}'",
            filename=filename
        )
        self.details["allowed_types"] = allowed_types
        self.details["hint"] = f"Allowed file types: {', '.join(allowed_types)}"
        self.error_code = "INVALID_FILE_TYPE"


class FileSizeExceededError(FileError):
    """Raised when file size exceeds limit"""
    
    def __init__(self, filename: str, size: int, max_size: int):
        super().__init__(
            message=f"File size exceeds limit for '{filename}'",
            filename=filename
        )
        self.details["file_size"] = size
        self.details["max_size"] = max_size
        self.details["hint"] = f"Maximum allowed size: {max_size} bytes"
        self.error_code = "FILE_SIZE_EXCEEDED"


# Rate Limiting Exceptions

class RateLimitExceededError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: int, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "limit": limit,
                "window": window,
                "retry_after": retry_after,
                "hint": f"You can make {limit} requests per {window} seconds. Try again in {retry_after} seconds"
            },
            error_code="RATE_LIMIT_EXCEEDED"
        )


# Configuration Exceptions

class ConfigurationError(BaseAPIException):
    """Raised when there's a configuration error"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=f"Configuration error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="CONFIGURATION_ERROR"
        )


# Payment & Pricing Exceptions

class PricingError(BusinessLogicError):
    """Raised when pricing calculation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Pricing error: {message}",
            details=details
        )
        self.error_code = "PRICING_ERROR"


class MatrixLookupError(PricingError):
    """Raised when price matrix lookup fails"""
    
    def __init__(self, module_count: int, battery_model: str):
        super().__init__(
            message="Price not found in matrix",
            details={
                "module_count": module_count,
                "battery_model": battery_model,
                "hint": "The specified combination is not available in the price matrix"
            }
        )
        self.error_code = "MATRIX_LOOKUP_ERROR"
