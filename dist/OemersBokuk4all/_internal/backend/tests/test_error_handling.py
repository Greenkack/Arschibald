"""
Tests for Error Handling and Validation System

Tests custom exceptions, validation, error handlers, and logging.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import BaseModel, Field

from backend.core.exceptions import (
    BaseAPIException,
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    AuthorizationError,
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    ValidationError,
    InvalidInputError,
    MissingRequiredFieldError,
    InvalidFormatError,
    BusinessLogicError,
    CalculationError,
    DatabaseError,
    DatabaseIntegrityError,
    ExternalServiceError,
    FileError,
    InvalidFileTypeError,
    FileSizeExceededError,
    RateLimitExceededError,
    PricingError,
    MatrixLookupError
)

from backend.core.validation import (
    ValidationRules,
    Validator,
    PaginationParams,
    SortParams,
    DateRangeParams,
    SearchParams
)

from backend.middleware.error_handler import (
    setup_error_handlers,
    create_error_response
)


# Test Custom Exceptions

class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_base_api_exception(self):
        """Test BaseAPIException"""
        exc = BaseAPIException(
            message="Test error",
            status_code=400,
            details={"key": "value"},
            error_code="TEST_ERROR"
        )
        
        assert exc.message == "Test error"
        assert exc.status_code == 400
        assert exc.details == {"key": "value"}
        assert exc.error_code == "TEST_ERROR"
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        exc = AuthenticationError()
        
        assert exc.status_code == 401
        assert exc.error_code == "AUTH_FAILED"
        assert "Authentication failed" in exc.message
    
    def test_invalid_credentials_error(self):
        """Test InvalidCredentialsError"""
        exc = InvalidCredentialsError()
        
        assert exc.status_code == 401
        assert exc.error_code == "INVALID_CREDENTIALS"
        assert "hint" in exc.details
    
    def test_token_expired_error(self):
        """Test TokenExpiredError"""
        exc = TokenExpiredError()
        
        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"
        assert "expired" in exc.message.lower()
    
    def test_authorization_error(self):
        """Test AuthorizationError"""
        exc = AuthorizationError(required_permission="admin")
        
        assert exc.status_code == 403
        assert exc.error_code == "INSUFFICIENT_PERMISSIONS"
        assert exc.details["required_permission"] == "admin"
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError"""
        exc = ResourceNotFoundError("Project", 123)
        
        assert exc.status_code == 404
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.details["resource_type"] == "Project"
        assert exc.details["resource_id"] == "123"
    
    def test_resource_already_exists_error(self):
        """Test ResourceAlreadyExistsError"""
        exc = ResourceAlreadyExistsError("User", "john@example.com")
        
        assert exc.status_code == 409
        assert exc.error_code == "RESOURCE_ALREADY_EXISTS"
        assert exc.details["identifier"] == "john@example.com"
    
    def test_validation_error(self):
        """Test ValidationError"""
        exc = ValidationError("Invalid value", field="email", value="invalid")
        
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "email"
    
    def test_invalid_input_error(self):
        """Test InvalidInputError"""
        exc = InvalidInputError("age", "Must be positive", value=-5)
        
        assert exc.status_code == 422
        assert exc.error_code == "INVALID_INPUT"
        assert "age" in exc.message
    
    def test_missing_required_field_error(self):
        """Test MissingRequiredFieldError"""
        exc = MissingRequiredFieldError("username")
        
        assert exc.status_code == 422
        assert exc.error_code == "MISSING_REQUIRED_FIELD"
        assert "username" in exc.message
    
    def test_calculation_error(self):
        """Test CalculationError"""
        exc = CalculationError("solar", "Invalid roof area")
        
        assert exc.status_code == 400
        assert exc.error_code == "CALCULATION_ERROR"
        assert exc.details["calculation_type"] == "solar"
    
    def test_database_integrity_error(self):
        """Test DatabaseIntegrityError"""
        exc = DatabaseIntegrityError("unique_email")
        
        assert exc.status_code == 500
        assert exc.error_code == "DATABASE_INTEGRITY_ERROR"
        assert exc.details["constraint"] == "unique_email"
    
    def test_external_service_error(self):
        """Test ExternalServiceError"""
        exc = ExternalServiceError("WeatherAPI", "Connection timeout")
        
        assert exc.status_code == 502
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.details["service_name"] == "WeatherAPI"
    
    def test_invalid_file_type_error(self):
        """Test InvalidFileTypeError"""
        exc = InvalidFileTypeError("document.txt", [".pdf", ".docx"])
        
        assert exc.status_code == 400
        assert exc.error_code == "INVALID_FILE_TYPE"
        assert exc.details["allowed_types"] == [".pdf", ".docx"]
    
    def test_file_size_exceeded_error(self):
        """Test FileSizeExceededError"""
        exc = FileSizeExceededError("large.pdf", 10_000_000, 5_000_000)
        
        assert exc.status_code == 400
        assert exc.error_code == "FILE_SIZE_EXCEEDED"
        assert exc.details["file_size"] == 10_000_000
        assert exc.details["max_size"] == 5_000_000
    
    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError"""
        exc = RateLimitExceededError(limit=100, window=60, retry_after=30)
        
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.details["limit"] == 100
        assert exc.details["retry_after"] == 30
    
    def test_matrix_lookup_error(self):
        """Test MatrixLookupError"""
        exc = MatrixLookupError(module_count=50, battery_model="Tesla Powerwall")
        
        assert exc.status_code == 400
        assert exc.error_code == "MATRIX_LOOKUP_ERROR"
        assert exc.details["module_count"] == 50
        assert exc.details["battery_model"] == "Tesla Powerwall"


# Test Validation Rules

class TestValidationRules:
    """Test validation rules"""
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert ValidationRules.validate_email("user@example.com") is True
        assert ValidationRules.validate_email("test.user+tag@domain.co.uk") is True
    
    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert ValidationRules.validate_email("invalid") is False
        assert ValidationRules.validate_email("@example.com") is False
        assert ValidationRules.validate_email("user@") is False
    
    def test_validate_phone_valid(self):
        """Test valid phone validation"""
        assert ValidationRules.validate_phone("+491234567890") is True
        assert ValidationRules.validate_phone("+12025551234") is True
    
    def test_validate_phone_invalid(self):
        """Test invalid phone validation"""
        assert ValidationRules.validate_phone("123") is False
        assert ValidationRules.validate_phone("invalid") is False
    
    def test_validate_postal_code_de_valid(self):
        """Test valid German postal code"""
        assert ValidationRules.validate_postal_code_de("12345") is True
        assert ValidationRules.validate_postal_code_de("80331") is True
    
    def test_validate_postal_code_de_invalid(self):
        """Test invalid German postal code"""
        assert ValidationRules.validate_postal_code_de("1234") is False
        assert ValidationRules.validate_postal_code_de("123456") is False
    
    def test_validate_password_strength_valid(self):
        """Test valid password strength"""
        assert ValidationRules.validate_password_strength("Password123") is True
        assert ValidationRules.validate_password_strength("MyP@ssw0rd") is True
    
    def test_validate_password_strength_invalid(self):
        """Test invalid password strength"""
        assert ValidationRules.validate_password_strength("password") is False  # No uppercase
        assert ValidationRules.validate_password_strength("PASSWORD123") is False  # No lowercase
        assert ValidationRules.validate_password_strength("Password") is False  # No digit
        assert ValidationRules.validate_password_strength("Pass1") is False  # Too short
    
    def test_validate_range(self):
        """Test range validation"""
        assert ValidationRules.validate_range(5, min_val=0, max_val=10) is True
        assert ValidationRules.validate_range(-1, min_val=0, max_val=10) is False
        assert ValidationRules.validate_range(11, min_val=0, max_val=10) is False
    
    def test_validate_length(self):
        """Test length validation"""
        assert ValidationRules.validate_length("hello", min_length=3, max_length=10) is True
        assert ValidationRules.validate_length("hi", min_length=3, max_length=10) is False
        assert ValidationRules.validate_length("verylongstring", min_length=3, max_length=10) is False
    
    def test_validate_enum(self):
        """Test enum validation"""
        assert ValidationRules.validate_enum("active", ["active", "inactive", "pending"]) is True
        assert ValidationRules.validate_enum("deleted", ["active", "inactive", "pending"]) is False


# Test Validator Class

class TestValidator:
    """Test Validator helper class"""
    
    def test_validate_required_success(self):
        """Test required field validation success"""
        Validator.validate_required("value", "field_name")  # Should not raise
    
    def test_validate_required_failure(self):
        """Test required field validation failure"""
        with pytest.raises(MissingRequiredFieldError):
            Validator.validate_required(None, "field_name")
        
        with pytest.raises(MissingRequiredFieldError):
            Validator.validate_required("", "field_name")
    
    def test_validate_email_success(self):
        """Test email validation success"""
        Validator.validate_email("user@example.com")  # Should not raise
    
    def test_validate_email_failure(self):
        """Test email validation failure"""
        with pytest.raises(InvalidFormatError):
            Validator.validate_email("invalid-email")
    
    def test_validate_password_success(self):
        """Test password validation success"""
        Validator.validate_password("Password123")  # Should not raise
    
    def test_validate_password_failure(self):
        """Test password validation failure"""
        with pytest.raises(InvalidInputError):
            Validator.validate_password("weak")
    
    def test_validate_range_success(self):
        """Test range validation success"""
        Validator.validate_range(5, "age", min_val=0, max_val=120)  # Should not raise
    
    def test_validate_range_failure(self):
        """Test range validation failure"""
        with pytest.raises(InvalidInputError):
            Validator.validate_range(-1, "age", min_val=0, max_val=120)
    
    def test_validate_length_success(self):
        """Test length validation success"""
        Validator.validate_length("hello", "username", min_length=3, max_length=20)  # Should not raise
    
    def test_validate_length_failure(self):
        """Test length validation failure"""
        with pytest.raises(InvalidInputError):
            Validator.validate_length("ab", "username", min_length=3, max_length=20)
    
    def test_validate_enum_success(self):
        """Test enum validation success"""
        Validator.validate_enum("active", "status", ["active", "inactive"])  # Should not raise
    
    def test_validate_enum_failure(self):
        """Test enum validation failure"""
        with pytest.raises(InvalidInputError):
            Validator.validate_enum("deleted", "status", ["active", "inactive"])
    
    def test_validate_positive_success(self):
        """Test positive validation success"""
        Validator.validate_positive(5, "quantity")  # Should not raise
    
    def test_validate_positive_failure(self):
        """Test positive validation failure"""
        with pytest.raises(InvalidInputError):
            Validator.validate_positive(0, "quantity")
        
        with pytest.raises(InvalidInputError):
            Validator.validate_positive(-5, "quantity")
    
    def test_validate_german_number_format_success(self):
        """Test German number format validation success"""
        result = Validator.validate_german_number_format("1.234,56", "price")
        assert result == 1234.56
    
    def test_validate_german_number_format_failure(self):
        """Test German number format validation failure"""
        with pytest.raises(InvalidFormatError):
            Validator.validate_german_number_format("invalid", "price")


# Test Pydantic Models

class TestPydanticModels:
    """Test Pydantic validation models"""
    
    def test_pagination_params_valid(self):
        """Test valid pagination parameters"""
        params = PaginationParams(page=2, page_size=50)
        assert params.page == 2
        assert params.page_size == 50
        assert params.offset == 50
        assert params.limit == 50
    
    def test_pagination_params_defaults(self):
        """Test pagination parameter defaults"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20
        assert params.offset == 0
    
    def test_pagination_params_invalid(self):
        """Test invalid pagination parameters"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PaginationParams(page=0)  # Must be >= 1
        
        with pytest.raises(Exception):
            PaginationParams(page_size=101)  # Must be <= 100
    
    def test_sort_params_valid(self):
        """Test valid sort parameters"""
        params = SortParams(sort_by="name", sort_order="desc")
        assert params.sort_by == "name"
        assert params.sort_order == "desc"
    
    def test_sort_params_invalid_order(self):
        """Test invalid sort order"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SortParams(sort_order="invalid")


# Test Error Response Creation

class TestErrorResponse:
    """Test error response creation"""
    
    def test_create_error_response_basic(self):
        """Test basic error response"""
        response = create_error_response(
            status_code=400,
            message="Bad request",
            error_code="BAD_REQUEST"
        )
        
        assert response["error"]["code"] == "BAD_REQUEST"
        assert response["error"]["message"] == "Bad request"
        assert "timestamp" in response["error"]
    
    def test_create_error_response_with_details(self):
        """Test error response with details"""
        response = create_error_response(
            status_code=422,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"field": "email", "issue": "invalid format"}
        )
        
        assert response["error"]["details"]["field"] == "email"
        assert response["error"]["details"]["issue"] == "invalid format"
    
    def test_create_error_response_with_hint(self):
        """Test error response includes helpful hints"""
        response = create_error_response(
            status_code=401,
            message="Unauthorized",
            error_code="UNAUTHORIZED"
        )
        
        assert "hint" in response["error"]
        assert "authentication" in response["error"]["hint"].lower()


# Integration Tests with FastAPI

def create_test_app():
    """Create a test FastAPI app with error handlers"""
    app = FastAPI()
    setup_error_handlers(app)
    
    @app.get("/test/success")
    async def test_success():
        return {"message": "success"}
    
    @app.get("/test/not-found")
    async def test_not_found():
        raise ResourceNotFoundError("Project", 123)
    
    @app.get("/test/validation")
    async def test_validation():
        raise InvalidInputError("email", "Invalid format", "not-an-email")
    
    @app.get("/test/auth")
    async def test_auth():
        raise InvalidCredentialsError()
    
    @app.get("/test/server-error")
    async def test_server_error():
        raise Exception("Unexpected error")
    
    return app


class TestErrorHandlerIntegration:
    """Test error handler integration with FastAPI"""
    
    def setup_method(self):
        """Setup test client"""
        self.app = create_test_app()
        self.client = TestClient(self.app)
    
    def test_success_response(self):
        """Test successful response"""
        response = self.client.get("/test/success")
        assert response.status_code == 200
        assert response.json()["message"] == "success"
    
    def test_not_found_error(self):
        """Test 404 error handling"""
        response = self.client.get("/test/not-found")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "Project" in data["error"]["message"]
        assert "hint" in data["error"]
    
    def test_validation_error(self):
        """Test validation error handling"""
        response = self.client.get("/test/validation")
        assert response.status_code == 422
        
        data = response.json()
        assert data["error"]["code"] == "INVALID_INPUT"
        assert "email" in data["error"]["message"]
    
    def test_auth_error(self):
        """Test authentication error handling"""
        response = self.client.get("/test/auth")
        assert response.status_code == 401
        
        data = response.json()
        assert data["error"]["code"] == "INVALID_CREDENTIALS"
        assert "hint" in data["error"]
    
    def test_server_error(self):
        """Test server error handling"""
        # Use raise_server_exceptions=False to let error handlers work
        with TestClient(self.app, raise_server_exceptions=False) as client:
            response = client.get("/test/server-error")
            assert response.status_code == 500
            
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
            assert "hint" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
