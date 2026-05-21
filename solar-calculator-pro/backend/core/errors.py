"""
Error Handling Framework

Comprehensive error handling system with custom exceptions, error codes,
message templates, logging, and user-friendly responses.

Requirements: 4.3, 4.4, 11.3
"""

from enum import Enum
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging
import traceback
import json


# Configure logger
logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """
    Standardized error codes for the application.
    Format: CATEGORY_SPECIFIC_ERROR
    """
    # General Errors (1000-1999)
    GENERAL_UNKNOWN = "ERR_1000"
    GENERAL_INTERNAL_SERVER = "ERR_1001"
    GENERAL_NOT_IMPLEMENTED = "ERR_1002"
    GENERAL_SERVICE_UNAVAILABLE = "ERR_1003"
    GENERAL_TIMEOUT = "ERR_1004"
    
    # Validation Errors (2000-2999)
    VALIDATION_REQUIRED_FIELD = "ERR_2000"
    VALIDATION_INVALID_FORMAT = "ERR_2001"
    VALIDATION_OUT_OF_RANGE = "ERR_2002"
    VALIDATION_INVALID_TYPE = "ERR_2003"
    VALIDATION_CONSTRAINT_VIOLATION = "ERR_2004"
    VALIDATION_DUPLICATE_VALUE = "ERR_2005"
    VALIDATION_INVALID_LENGTH = "ERR_2006"
    
    # Authentication Errors (3000-3999)
    AUTH_INVALID_CREDENTIALS = "ERR_3000"
    AUTH_TOKEN_EXPIRED = "ERR_3001"
    AUTH_TOKEN_INVALID = "ERR_3002"
    AUTH_UNAUTHORIZED = "ERR_3003"
    AUTH_FORBIDDEN = "ERR_3004"
    AUTH_SESSION_EXPIRED = "ERR_3005"
    AUTH_ACCOUNT_LOCKED = "ERR_3006"
    AUTH_ACCOUNT_DISABLED = "ERR_3007"
    
    # Database Errors (4000-4999)
    DB_CONNECTION_FAILED = "ERR_4000"
    DB_QUERY_FAILED = "ERR_4001"
    DB_RECORD_NOT_FOUND = "ERR_4002"
    DB_DUPLICATE_RECORD = "ERR_4003"
    DB_CONSTRAINT_VIOLATION = "ERR_4004"
    DB_TRANSACTION_FAILED = "ERR_4005"
    DB_MIGRATION_FAILED = "ERR_4006"
    
    # Business Logic Errors (5000-5999)
    BUSINESS_INVALID_OPERATION = "ERR_5000"
    BUSINESS_CALCULATION_FAILED = "ERR_5001"
    BUSINESS_INSUFFICIENT_DATA = "ERR_5002"
    BUSINESS_INVALID_STATE = "ERR_5003"
    BUSINESS_QUOTA_EXCEEDED = "ERR_5004"
    BUSINESS_DEPENDENCY_FAILED = "ERR_5005"
    
    # File/Resource Errors (6000-6999)
    FILE_NOT_FOUND = "ERR_6000"
    FILE_UPLOAD_FAILED = "ERR_6001"
    FILE_INVALID_FORMAT = "ERR_6002"
    FILE_SIZE_EXCEEDED = "ERR_6003"
    FILE_PERMISSION_DENIED = "ERR_6004"
    RESOURCE_NOT_AVAILABLE = "ERR_6005"
    
    # External Service Errors (7000-7999)
    EXTERNAL_API_FAILED = "ERR_7000"
    EXTERNAL_API_TIMEOUT = "ERR_7001"
    EXTERNAL_API_RATE_LIMIT = "ERR_7002"
    EXTERNAL_SERVICE_UNAVAILABLE = "ERR_7003"
    
    # Solar Calculator Errors (8000-8999)
    SOLAR_INVALID_ROOF_AREA = "ERR_8000"
    SOLAR_INVALID_MODULE_TYPE = "ERR_8001"
    SOLAR_CALCULATION_FAILED = "ERR_8002"
    SOLAR_INSUFFICIENT_SPACE = "ERR_8003"
    SOLAR_INVALID_ORIENTATION = "ERR_8004"
    
    # Heat Pump Errors (9000-9999)
    HEATPUMP_INVALID_BUILDING_DATA = "ERR_9000"
    HEATPUMP_CALCULATION_FAILED = "ERR_9001"
    HEATPUMP_INVALID_MODEL = "ERR_9002"
    HEATPUMP_INSUFFICIENT_CAPACITY = "ERR_9003"
    
    # Price Matrix Errors (10000-10999)
    PRICE_MATRIX_NOT_FOUND = "ERR_10000"
    PRICE_MATRIX_INVALID_FORMAT = "ERR_10001"
    PRICE_MATRIX_CALCULATION_FAILED = "ERR_10002"
    PRICE_MATRIX_PRODUCT_NOT_FOUND = "ERR_10003"
    PRICE_MATRIX_FORMULA_ERROR = "ERR_10004"
    
    # PDF Generation Errors (11000-11999)
    PDF_GENERATION_FAILED = "ERR_11000"
    PDF_TEMPLATE_NOT_FOUND = "ERR_11001"
    PDF_INVALID_DATA = "ERR_11002"
    PDF_RENDERING_FAILED = "ERR_11003"


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    SYSTEM = "system"


# Error message templates
ERROR_MESSAGES: Dict[ErrorCode, Dict[str, Any]] = {
    # General Errors
    ErrorCode.GENERAL_UNKNOWN: {
        "message": "An unexpected error occurred",
        "user_message": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
        "severity": ErrorSeverity.HIGH,
        "category": ErrorCategory.SYSTEM,
    },
    ErrorCode.GENERAL_INTERNAL_SERVER: {
        "message": "Internal server error",
        "user_message": "Ein interner Serverfehler ist aufgetreten. Unser Team wurde benachrichtigt.",
        "severity": ErrorSeverity.CRITICAL,
        "category": ErrorCategory.SYSTEM,
    },
    ErrorCode.GENERAL_SERVICE_UNAVAILABLE: {
        "message": "Service temporarily unavailable",
        "user_message": "Der Dienst ist vorübergehend nicht verfügbar. Bitte versuchen Sie es später erneut.",
        "severity": ErrorSeverity.HIGH,
        "category": ErrorCategory.SYSTEM,
    },
    ErrorCode.GENERAL_TIMEOUT: {
        "message": "Request timeout",
        "user_message": "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es erneut.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.NETWORK,
    },
    
    # Validation Errors
    ErrorCode.VALIDATION_REQUIRED_FIELD: {
        "message": "Required field missing",
        "user_message": "Pflichtfeld fehlt: {field}",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    ErrorCode.VALIDATION_INVALID_FORMAT: {
        "message": "Invalid format",
        "user_message": "Ungültiges Format für {field}. Erwartetes Format: {expected_format}",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    ErrorCode.VALIDATION_OUT_OF_RANGE: {
        "message": "Value out of range",
        "user_message": "{field} muss zwischen {min} und {max} liegen",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    ErrorCode.VALIDATION_INVALID_TYPE: {
        "message": "Invalid data type",
        "user_message": "{field} hat einen ungültigen Datentyp. Erwartet: {expected_type}",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    ErrorCode.VALIDATION_DUPLICATE_VALUE: {
        "message": "Duplicate value",
        "user_message": "{field} existiert bereits. Bitte wählen Sie einen anderen Wert.",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    
    # Authentication Errors
    ErrorCode.AUTH_INVALID_CREDENTIALS: {
        "message": "Invalid credentials",
        "user_message": "Ungültige Anmeldedaten. Bitte überprüfen Sie Benutzername und Passwort.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.AUTHENTICATION,
    },
    ErrorCode.AUTH_TOKEN_EXPIRED: {
        "message": "Token expired",
        "user_message": "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.AUTHENTICATION,
    },
    ErrorCode.AUTH_UNAUTHORIZED: {
        "message": "Unauthorized access",
        "user_message": "Sie sind nicht berechtigt, auf diese Ressource zuzugreifen.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.AUTHORIZATION,
    },
    ErrorCode.AUTH_FORBIDDEN: {
        "message": "Forbidden",
        "user_message": "Sie haben keine Berechtigung für diese Aktion.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.AUTHORIZATION,
    },
    
    # Database Errors
    ErrorCode.DB_CONNECTION_FAILED: {
        "message": "Database connection failed",
        "user_message": "Datenbankverbindung fehlgeschlagen. Bitte versuchen Sie es später erneut.",
        "severity": ErrorSeverity.CRITICAL,
        "category": ErrorCategory.DATABASE,
    },
    ErrorCode.DB_RECORD_NOT_FOUND: {
        "message": "Record not found",
        "user_message": "Der angeforderte Datensatz wurde nicht gefunden.",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.DATABASE,
    },
    ErrorCode.DB_DUPLICATE_RECORD: {
        "message": "Duplicate record",
        "user_message": "Ein Datensatz mit diesen Daten existiert bereits.",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.DATABASE,
    },
    
    # Business Logic Errors
    ErrorCode.BUSINESS_CALCULATION_FAILED: {
        "message": "Calculation failed",
        "user_message": "Die Berechnung konnte nicht durchgeführt werden. Bitte überprüfen Sie Ihre Eingaben.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    ErrorCode.BUSINESS_INSUFFICIENT_DATA: {
        "message": "Insufficient data",
        "user_message": "Nicht genügend Daten für diese Operation vorhanden.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    
    # File Errors
    ErrorCode.FILE_NOT_FOUND: {
        "message": "File not found",
        "user_message": "Die Datei wurde nicht gefunden.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.FILE_SYSTEM,
    },
    ErrorCode.FILE_INVALID_FORMAT: {
        "message": "Invalid file format",
        "user_message": "Ungültiges Dateiformat. Erlaubte Formate: {allowed_formats}",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.FILE_SYSTEM,
    },
    ErrorCode.FILE_SIZE_EXCEEDED: {
        "message": "File size exceeded",
        "user_message": "Die Datei ist zu groß. Maximale Größe: {max_size}",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.FILE_SYSTEM,
    },
    
    # Solar Calculator Errors
    ErrorCode.SOLAR_INVALID_ROOF_AREA: {
        "message": "Invalid roof area",
        "user_message": "Ungültige Dachfläche. Bitte geben Sie einen Wert zwischen {min} und {max} m² ein.",
        "severity": ErrorSeverity.LOW,
        "category": ErrorCategory.VALIDATION,
    },
    ErrorCode.SOLAR_CALCULATION_FAILED: {
        "message": "Solar calculation failed",
        "user_message": "Die Solaranlage-Berechnung ist fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    
    # Price Matrix Errors
    ErrorCode.PRICE_MATRIX_NOT_FOUND: {
        "message": "Price matrix not found",
        "user_message": "Preismatrix nicht gefunden. Bitte laden Sie eine Preismatrix hoch.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    ErrorCode.PRICE_MATRIX_CALCULATION_FAILED: {
        "message": "Price calculation failed",
        "user_message": "Die Preisberechnung ist fehlgeschlagen. Bitte überprüfen Sie die Preismatrix.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    
    # PDF Errors
    ErrorCode.PDF_GENERATION_FAILED: {
        "message": "PDF generation failed",
        "user_message": "Die PDF-Generierung ist fehlgeschlagen. Bitte versuchen Sie es erneut.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.BUSINESS_LOGIC,
    },
    ErrorCode.PDF_TEMPLATE_NOT_FOUND: {
        "message": "PDF template not found",
        "user_message": "PDF-Vorlage nicht gefunden.",
        "severity": ErrorSeverity.MEDIUM,
        "category": ErrorCategory.FILE_SYSTEM,
    },
}


class AppError(Exception):
    """
    Base application error class with comprehensive error handling.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        context: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.timestamp = datetime.utcnow()
        self.details = details or {}
        self.status_code = status_code
        self.context = context or {}
        
        # Get error template
        template = ERROR_MESSAGES.get(error_code, {})
        
        # Set message (developer-facing)
        self.message = message or template.get("message", "An error occurred")
        
        # Set user message (user-facing, German)
        self.user_message = user_message or template.get("user_message", self.message)
        
        # Format user message with details
        if self.details:
            try:
                self.user_message = self.user_message.format(**self.details)
            except KeyError:
                pass  # Keep original message if formatting fails
        
        # Set severity and category
        self.severity = severity or template.get("severity", ErrorSeverity.MEDIUM)
        self.category = category or template.get("category", ErrorCategory.SYSTEM)
        
        # Log the error
        self._log_error()
        
        super().__init__(self.message)
    
    def _log_error(self):
        """Log the error with appropriate level based on severity"""
        log_data = {
            "error_code": self.error_code,
            "error_message": self.message,  # Renamed to avoid conflict with LogRecord.message
            "user_message": self.user_message,
            "severity": self.severity,
            "category": self.category,
            "details": self.details,
            "context": self.context,
            "error_timestamp": self.timestamp.isoformat(),  # Renamed to avoid conflict
        }
        
        log_message = f"[{self.error_code}] {self.message}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=log_data, exc_info=True)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=log_data, exc_info=True)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=log_data)
        else:
            logger.info(log_message, extra=log_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.user_message,  # User-friendly message
                "details": self.details,
                "severity": self.severity,
                "category": self.category,
                "timestamp": self.timestamp.isoformat(),
            }
        }
    
    def to_json(self) -> str:
        """Convert error to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# Specific Exception Classes

class ValidationError(AppError):
    """Validation error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.VALIDATION_INVALID_FORMAT,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=422,
            **kwargs
        )


class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=401,
            **kwargs
        )


class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.AUTH_FORBIDDEN,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=403,
            **kwargs
        )



class DatabaseError(AppError):
    """Database error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.DB_QUERY_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=500,
            **kwargs
        )


class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.DB_RECORD_NOT_FOUND,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=404,
            **kwargs
        )


class BusinessLogicError(AppError):
    """Business logic error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.BUSINESS_INVALID_OPERATION,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=400,
            **kwargs
        )


class FileError(AppError):
    """File operation error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.FILE_NOT_FOUND,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=400,
            **kwargs
        )



class ExternalServiceError(AppError):
    """External service error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.EXTERNAL_API_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            status_code=502,
            **kwargs
        )


# Domain-Specific Errors

class SolarCalculatorError(BusinessLogicError):
    """Solar calculator specific error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.SOLAR_CALCULATION_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            **kwargs
        )


class HeatPumpError(BusinessLogicError):
    """Heat pump specific error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.HEATPUMP_CALCULATION_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            **kwargs
        )


class PriceMatrixError(BusinessLogicError):
    """Price matrix specific error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.PRICE_MATRIX_CALCULATION_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            **kwargs
        )



class PDFGenerationError(BusinessLogicError):
    """PDF generation specific error"""
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.PDF_GENERATION_FAILED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            **kwargs
        )


# Error Handler Utilities

class ErrorHandler:
    """
    Utility class for error handling operations
    """
    
    @staticmethod
    def handle_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> AppError:
        """
        Convert any exception to AppError
        
        Args:
            exc: The exception to handle
            context: Additional context information
            
        Returns:
            AppError instance
        """
        if isinstance(exc, AppError):
            return exc
        
        # Map common exceptions to AppError
        error_mapping = {
            ValueError: (ErrorCode.VALIDATION_INVALID_TYPE, 422),
            KeyError: (ErrorCode.DB_RECORD_NOT_FOUND, 404),
            FileNotFoundError: (ErrorCode.FILE_NOT_FOUND, 404),
            PermissionError: (ErrorCode.AUTH_FORBIDDEN, 403),
            TimeoutError: (ErrorCode.GENERAL_TIMEOUT, 408),
        }
        
        error_code, status_code = error_mapping.get(
            type(exc),
            (ErrorCode.GENERAL_UNKNOWN, 500)
        )
        
        return AppError(
            error_code=error_code,
            message=str(exc),
            status_code=status_code,
            context=context or {},
            details={"original_error": type(exc).__name__}
        )
    
    @staticmethod
    def create_validation_error(
        field: str,
        value: Any,
        constraint: str,
        **kwargs
    ) -> ValidationError:
        """
        Create a validation error with formatted details
        
        Args:
            field: Field name that failed validation
            value: The invalid value
            constraint: Description of the constraint that was violated
            **kwargs: Additional details
            
        Returns:
            ValidationError instance
        """
        details = {
            "field": field,
            "value": str(value),
            "constraint": constraint,
            **kwargs
        }
        
        return ValidationError(
            error_code=ErrorCode.VALIDATION_CONSTRAINT_VIOLATION,
            details=details
        )
    
    @staticmethod
    def create_not_found_error(
        resource_type: str,
        resource_id: Any
    ) -> NotFoundError:
        """
        Create a not found error
        
        Args:
            resource_type: Type of resource (e.g., "Project", "User")
            resource_id: ID of the resource
            
        Returns:
            NotFoundError instance
        """
        return NotFoundError(
            error_code=ErrorCode.DB_RECORD_NOT_FOUND,
            details={
                "resource_type": resource_type,
                "resource_id": str(resource_id)
            }
        )
    
    @staticmethod
    def log_error_with_context(
        error: AppError,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """
        Log error with additional context
        
        Args:
            error: The error to log
            request_id: Request ID for tracing
            user_id: User ID if available
            additional_context: Additional context information
        """
        context = {
            "request_id": request_id,
            "user_id": user_id,
            **(additional_context or {})
        }
        
        logger.error(
            f"Error occurred: {error.error_code} - {error.message}",
            extra={
                **error.to_dict(),
                "context": context
            },
            exc_info=True
        )



# Decorator for error handling

def handle_errors(
    default_error_code: ErrorCode = ErrorCode.GENERAL_UNKNOWN,
    log_errors: bool = True
):
    """
    Decorator to handle errors in functions
    
    Args:
        default_error_code: Default error code if exception is not AppError
        log_errors: Whether to log errors
        
    Example:
        @handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
        def calculate_solar_system(data):
            # Function implementation
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AppError:
                raise  # Re-raise AppError as-is
            except Exception as e:
                error = ErrorHandler.handle_exception(e)
                error.error_code = default_error_code
                
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                
                raise error
        
        return wrapper
    return decorator


# Context manager for error handling

class ErrorContext:
    """
    Context manager for error handling with automatic logging
    
    Example:
        with ErrorContext("solar_calculation", user_id="123"):
            result = calculate_solar_system(data)
    """
    
    def __init__(
        self,
        operation: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **context
    ):
        self.operation = operation
        self.user_id = user_id
        self.request_id = request_id
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        logger.info(f"Starting operation: {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(
                f"Operation completed: {self.operation} (duration: {duration:.2f}s)",
                extra=self.context
            )
            return True
        
        if isinstance(exc_val, AppError):
            ErrorHandler.log_error_with_context(
                exc_val,
                request_id=self.request_id,
                user_id=self.user_id,
                additional_context={
                    "operation": self.operation,
                    "duration": duration,
                    **self.context
                }
            )
        else:
            logger.error(
                f"Operation failed: {self.operation} (duration: {duration:.2f}s)",
                extra={
                    "error_type": type(exc_val).__name__,
                    "error_message": str(exc_val),
                    **self.context
                },
                exc_info=True
            )
        
        return False  # Re-raise the exception
