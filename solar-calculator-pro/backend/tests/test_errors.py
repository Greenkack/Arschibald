"""
Tests for Error Handling Framework

Tests custom exceptions, error codes, message templates, logging, and error responses.
"""

import pytest
import json
from datetime import datetime
from core.errors import (
    ErrorCode,
    ErrorSeverity,
    ErrorCategory,
    AppError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    BusinessLogicError,
    FileError,
    ExternalServiceError,
    SolarCalculatorError,
    HeatPumpError,
    PriceMatrixError,
    PDFGenerationError,
    ErrorHandler,
    handle_errors,
    ErrorContext)


class TestErrorCodes:
    """Test error code definitions"""
    
    def test_error_codes_are_unique(self):
        """Test that all error codes are unique"""
        codes = [code.value for code in ErrorCode]
        assert len(codes) == len(set(codes)), "Duplicate error codes found"
    
    def test_error_code_format(self):
        """Test that error codes follow the correct format"""
        for code in ErrorCode:
            assert code.value.startswith("ERR_"), f"Error code {code.value} doesn't start with ERR_"
            assert code.value[4:].isdigit(), f"Error code {code.value} doesn't have numeric suffix"


class TestAppError:
    """Test base AppError class"""
    
    def test_create_basic_error(self):
        """Test creating a basic error"""
        error = AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Test error"
        )
        
        assert error.error_code == ErrorCode.GENERAL_UNKNOWN
        assert error.message == "Test error"
        assert isinstance(error.timestamp, datetime)
        assert error.status_code == 500
    
    def test_error_with_details(self):
        """Test error with details"""
        error = AppError(
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            details={"field": "email", "value": ""}
        )
        
        assert error.details["field"] == "email"
        assert "email" in error.user_message
    
    def test_error_message_formatting(self):
        """Test that error messages are formatted with details"""
        error = AppError(
            error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
            details={"field": "age", "min": 0, "max": 120}
        )
        
        assert "age" in error.user_message
        assert "0" in error.user_message
        assert "120" in error.user_message
    
    def test_error_to_dict(self):
        """Test converting error to dictionary"""
        error = AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Test error",
            details={"key": "value"}
        )
        
        error_dict = error.to_dict()
        
        assert "error" in error_dict
        assert error_dict["error"]["code"] == ErrorCode.GENERAL_UNKNOWN
        assert "message" in error_dict["error"]
        assert "details" in error_dict["error"]
        assert "timestamp" in error_dict["error"]
    
    def test_error_to_json(self):
        """Test converting error to JSON"""
        error = AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Test error"
        )
        
        error_json = error.to_json()
        parsed = json.loads(error_json)
        
        assert "error" in parsed
        assert parsed["error"]["code"] == ErrorCode.GENERAL_UNKNOWN
    
    def test_error_severity_assignment(self):
        """Test that severity is correctly assigned"""
        error = AppError(
            error_code=ErrorCode.GENERAL_INTERNAL_SERVER
        )
        
        assert error.severity == ErrorSeverity.CRITICAL
    
    def test_error_category_assignment(self):
        """Test that category is correctly assigned"""
        error = AppError(
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD
        )
        
        assert error.category == ErrorCategory.VALIDATION


class TestSpecificErrors:
    """Test specific error classes"""
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError(
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            details={"field": "email"}
        )
        
        assert error.status_code == 422
        assert isinstance(error, AppError)
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError()
        
        assert error.status_code == 401
        assert error.category == ErrorCategory.AUTHENTICATION
    
    def test_authorization_error(self):
        """Test AuthorizationError"""
        error = AuthorizationError()
        
        assert error.status_code == 403
        assert error.category == ErrorCategory.AUTHORIZATION
    
    def test_database_error(self):
        """Test DatabaseError"""
        error = DatabaseError(
            error_code=ErrorCode.DB_CONNECTION_FAILED
        )
        
        assert error.status_code == 500
        assert error.category == ErrorCategory.DATABASE
    
    def test_not_found_error(self):
        """Test NotFoundError"""
        error = NotFoundError(
            details={"resource": "User", "id": 123}
        )
        
        assert error.status_code == 404
    
    def test_business_logic_error(self):
        """Test BusinessLogicError"""
        error = BusinessLogicError(
            error_code=ErrorCode.BUSINESS_CALCULATION_FAILED
        )
        
        assert error.status_code == 400
        assert error.category == ErrorCategory.BUSINESS_LOGIC
    
    def test_file_error(self):
        """Test FileError"""
        error = FileError(
            error_code=ErrorCode.FILE_NOT_FOUND,
            details={"filename": "test.pdf"}
        )
        
        assert error.status_code == 400
        assert error.category == ErrorCategory.FILE_SYSTEM
    
    def test_external_service_error(self):
        """Test ExternalServiceError"""
        error = ExternalServiceError(
            error_code=ErrorCode.EXTERNAL_API_FAILED
        )
        
        assert error.status_code == 502


class TestDomainSpecificErrors:
    """Test domain-specific error classes"""
    
    def test_solar_calculator_error(self):
        """Test SolarCalculatorError"""
        error = SolarCalculatorError(
            error_code=ErrorCode.SOLAR_INVALID_ROOF_AREA,
            details={"min": 10, "max": 1000}
        )
        
        assert isinstance(error, BusinessLogicError)
        assert "10" in error.user_message
        assert "1000" in error.user_message
    
    def test_heat_pump_error(self):
        """Test HeatPumpError"""
        error = HeatPumpError(
            error_code=ErrorCode.HEATPUMP_CALCULATION_FAILED
        )
        
        assert isinstance(error, BusinessLogicError)
    
    def test_price_matrix_error(self):
        """Test PriceMatrixError"""
        error = PriceMatrixError(
            error_code=ErrorCode.PRICE_MATRIX_NOT_FOUND
        )
        
        assert isinstance(error, BusinessLogicError)
        assert "Preismatrix" in error.user_message
    
    def test_pdf_generation_error(self):
        """Test PDFGenerationError"""
        error = PDFGenerationError(
            error_code=ErrorCode.PDF_GENERATION_FAILED
        )
        
        assert isinstance(error, BusinessLogicError)
        assert "PDF" in error.user_message


class TestErrorHandler:
    """Test ErrorHandler utility class"""
    
    def test_handle_app_error(self):
        """Test handling AppError (should return as-is)"""
        original_error = AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Test error"
        )
        
        handled_error = ErrorHandler.handle_exception(original_error)
        
        assert handled_error is original_error
    
    def test_handle_value_error(self):
        """Test handling ValueError"""
        exc = ValueError("Invalid value")
        
        handled_error = ErrorHandler.handle_exception(exc)
        
        assert isinstance(handled_error, AppError)
        assert handled_error.error_code == ErrorCode.VALIDATION_INVALID_TYPE
        assert handled_error.status_code == 422
    
    def test_handle_key_error(self):
        """Test handling KeyError"""
        exc = KeyError("missing_key")
        
        handled_error = ErrorHandler.handle_exception(exc)
        
        assert isinstance(handled_error, AppError)
        assert handled_error.error_code == ErrorCode.DB_RECORD_NOT_FOUND
        assert handled_error.status_code == 404
    
    def test_handle_file_not_found_error(self):
        """Test handling FileNotFoundError"""
        exc = FileNotFoundError("file.txt")
        
        handled_error = ErrorHandler.handle_exception(exc)
        
        assert isinstance(handled_error, AppError)
        assert handled_error.error_code == ErrorCode.FILE_NOT_FOUND
        assert handled_error.status_code == 404
    
    def test_handle_unknown_exception(self):
        """Test handling unknown exception"""
        exc = RuntimeError("Unknown error")
        
        handled_error = ErrorHandler.handle_exception(exc)
        
        assert isinstance(handled_error, AppError)
        assert handled_error.error_code == ErrorCode.GENERAL_UNKNOWN
        assert handled_error.status_code == 500
    
    def test_create_validation_error(self):
        """Test creating validation error with helper"""
        error = ErrorHandler.create_validation_error(
            field="email",
            value="invalid-email",
            constraint="Must be valid email format"
        )
        
        assert isinstance(error, ValidationError)
        assert error.details["field"] == "email"
        assert error.details["value"] == "invalid-email"
        assert error.details["constraint"] == "Must be valid email format"
    
    def test_create_not_found_error(self):
        """Test creating not found error with helper"""
        error = ErrorHandler.create_not_found_error(
            resource_type="Project",
            resource_id=123
        )
        
        assert isinstance(error, NotFoundError)
        assert error.details["resource_type"] == "Project"
        assert error.details["resource_id"] == "123"


class TestErrorDecorator:
    """Test error handling decorator"""
    
    def test_decorator_with_successful_function(self):
        """Test decorator with function that succeeds"""
        @handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_decorator_with_app_error(self):
        """Test decorator with function that raises AppError"""
        @handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
        def function_with_app_error():
            raise AppError(
                error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
                message="Test error"
            )
        
        with pytest.raises(AppError) as exc_info:
            function_with_app_error()
        
        assert exc_info.value.error_code == ErrorCode.VALIDATION_REQUIRED_FIELD
    
    def test_decorator_with_generic_exception(self):
        """Test decorator with function that raises generic exception"""
        @handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
        def function_with_exception():
            raise ValueError("Invalid value")
        
        with pytest.raises(AppError) as exc_info:
            function_with_exception()
        
        assert exc_info.value.error_code == ErrorCode.SOLAR_CALCULATION_FAILED


class TestErrorContext:
    """Test ErrorContext context manager"""
    
    def test_context_manager_success(self):
        """Test context manager with successful operation"""
        with ErrorContext("test_operation", user_id="123") as ctx:
            result = "success"
        
        assert result == "success"
    
    def test_context_manager_with_app_error(self):
        """Test context manager with AppError"""
        with pytest.raises(AppError):
            with ErrorContext("test_operation"):
                raise AppError(
                    error_code=ErrorCode.GENERAL_UNKNOWN,
                    message="Test error"
                )
    
    def test_context_manager_with_generic_exception(self):
        """Test context manager with generic exception"""
        with pytest.raises(ValueError):
            with ErrorContext("test_operation"):
                raise ValueError("Test error")


class TestGermanErrorMessages:
    """Test German error messages"""
    
    def test_validation_error_german(self):
        """Test validation error has German message"""
        error = ValidationError(
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            details={"field": "E-Mail"}
        )
        
        assert "Pflichtfeld" in error.user_message or "fehlt" in error.user_message
    
    def test_authentication_error_german(self):
        """Test authentication error has German message"""
        error = AuthenticationError()
        
        assert "Anmeldedaten" in error.user_message or "Passwort" in error.user_message
    
    def test_database_error_german(self):
        """Test database error has German message"""
        error = DatabaseError(
            error_code=ErrorCode.DB_CONNECTION_FAILED
        )
        
        assert "Datenbank" in error.user_message
    
    def test_solar_error_german(self):
        """Test solar calculator error has German message"""
        error = SolarCalculatorError(
            error_code=ErrorCode.SOLAR_INVALID_ROOF_AREA,
            details={"min": 10, "max": 1000}
        )
        
        assert "Dachfläche" in error.user_message or "m²" in error.user_message
    
    def test_price_matrix_error_german(self):
        """Test price matrix error has German message"""
        error = PriceMatrixError(
            error_code=ErrorCode.PRICE_MATRIX_NOT_FOUND
        )
        
        assert "Preismatrix" in error.user_message


class TestErrorLogging:
    """Test error logging functionality"""
    
    def test_error_logs_on_creation(self, caplog):
        """Test that errors are logged when created"""
        import logging
        caplog.set_level(logging.INFO)
        
        error = AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Test error"
        )
        
        # Check that error was logged
        assert len(caplog.records) > 0
    
    def test_critical_error_logging_level(self, caplog):
        """Test that critical errors use critical log level"""
        import logging
        caplog.set_level(logging.CRITICAL)
        
        error = AppError(
            error_code=ErrorCode.GENERAL_INTERNAL_SERVER,
            message="Critical error"
        )
        
        # Check that critical level was used
        assert any(record.levelname == "CRITICAL" for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
