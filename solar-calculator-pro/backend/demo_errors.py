"""
Error Handling Framework Demo

Demonstrates usage of the error handling framework.
"""

from core.errors import (
    AppError,
    ErrorCode,
    ValidationError,
    AuthenticationError,
    DatabaseError,
    NotFoundError,
    SolarCalculatorError,
    PriceMatrixError,
    PDFGenerationError,
    ErrorHandler,
    handle_errors,
    ErrorContext,
)


def demo_basic_error():
    """Demo: Basic error creation"""
    print("\n=== Demo: Basic Error ===")
    
    try:
        raise AppError(
            error_code=ErrorCode.GENERAL_UNKNOWN,
            message="Something went wrong",
            details={"operation": "demo"}
        )
    except AppError as e:
        print(f"Error Code: {e.error_code}")
        print(f"Message: {e.message}")
        print(f"User Message: {e.user_message}")
        print(f"Status Code: {e.status_code}")
        print(f"Severity: {e.severity}")
        print(f"Category: {e.category}")
        print(f"\nJSON Response:\n{e.to_json()}")


def demo_validation_error():
    """Demo: Validation error with details"""
    print("\n=== Demo: Validation Error ===")
    
    try:
        raise ValidationError(
            error_code=ErrorCode.VALIDATION_OUT_OF_RANGE,
            details={"field": "roof_area", "min": 10, "max": 1000}
        )
    except ValidationError as e:
        print(f"Error Code: {e.error_code}")
        print(f"User Message (German): {e.user_message}")
        print(f"Details: {e.details}")


def demo_solar_calculator_error():
    """Demo: Solar calculator specific error"""
    print("\n=== Demo: Solar Calculator Error ===")
    
    try:
        raise SolarCalculatorError(
            error_code=ErrorCode.SOLAR_INVALID_ROOF_AREA,
            details={"min": 10, "max": 1000}
        )
    except SolarCalculatorError as e:
        print(f"Error Code: {e.error_code}")
        print(f"User Message: {e.user_message}")
        print(f"Status Code: {e.status_code}")


def demo_error_handler():
    """Demo: ErrorHandler utility"""
    print("\n=== Demo: Error Handler ===")
    
    # Handle ValueError
    try:
        raise ValueError("Invalid input")
    except Exception as e:
        app_error = ErrorHandler.handle_exception(e)
        print(f"Converted to: {app_error.error_code}")
        print(f"Status Code: {app_error.status_code}")
    
    # Create validation error
    error = ErrorHandler.create_validation_error(
        field="email",
        value="invalid-email",
        constraint="Must be valid email format"
    )
    print(f"\nValidation Error: {error.user_message}")
    
    # Create not found error
    error = ErrorHandler.create_not_found_error(
        resource_type="Project",
        resource_id=123
    )
    print(f"Not Found Error: {error.user_message}")


@handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
def demo_function_with_decorator():
    """Demo: Function with error handling decorator"""
    print("\n=== Demo: Error Decorator ===")
    
    # This will be caught and converted to AppError
    raise ValueError("Calculation failed")


def demo_error_context():
    """Demo: Error context manager"""
    print("\n=== Demo: Error Context ===")
    
    try:
        with ErrorContext("solar_calculation", user_id="user-123", request_id="req-456"):
            print("Starting calculation...")
            # Simulate calculation
            result = 42
            print(f"Calculation completed: {result}")
    except Exception as e:
        print(f"Error occurred: {e}")


def demo_domain_errors():
    """Demo: Domain-specific errors"""
    print("\n=== Demo: Domain-Specific Errors ===")
    
    # Solar Calculator Error
    try:
        raise SolarCalculatorError(
            error_code=ErrorCode.SOLAR_CALCULATION_FAILED,
            details={"roof_area": 50, "reason": "Insufficient space"}
        )
    except SolarCalculatorError as e:
        print(f"Solar Error: {e.user_message}")
    
    # Price Matrix Error
    try:
        raise PriceMatrixError(
            error_code=ErrorCode.PRICE_MATRIX_NOT_FOUND
        )
    except PriceMatrixError as e:
        print(f"Price Matrix Error: {e.user_message}")
    
    # PDF Generation Error
    try:
        raise PDFGenerationError(
            error_code=ErrorCode.PDF_GENERATION_FAILED
        )
    except PDFGenerationError as e:
        print(f"PDF Error: {e.user_message}")


def demo_error_response():
    """Demo: Error response format"""
    print("\n=== Demo: Error Response Format ===")
    
    error = ValidationError(
        error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        details={"field": "email", "value": ""}
    )
    
    # Get dictionary format (for API response)
    response_dict = error.to_dict()
    print("Dictionary format:")
    print(response_dict)
    
    # Get JSON format
    response_json = error.to_json()
    print("\nJSON format:")
    print(response_json)


def demo_all_error_types():
    """Demo: All error types"""
    print("\n=== Demo: All Error Types ===")
    
    errors = [
        ("Validation", ValidationError(error_code=ErrorCode.VALIDATION_REQUIRED_FIELD)),
        ("Authentication", AuthenticationError(error_code=ErrorCode.AUTH_INVALID_CREDENTIALS)),
        ("Database", DatabaseError(error_code=ErrorCode.DB_CONNECTION_FAILED)),
        ("Not Found", NotFoundError(error_code=ErrorCode.DB_RECORD_NOT_FOUND)),
        ("Solar", SolarCalculatorError(error_code=ErrorCode.SOLAR_CALCULATION_FAILED)),
        ("Price Matrix", PriceMatrixError(error_code=ErrorCode.PRICE_MATRIX_NOT_FOUND)),
        ("PDF", PDFGenerationError(error_code=ErrorCode.PDF_GENERATION_FAILED)),
    ]
    
    for name, error in errors:
        print(f"\n{name} Error:")
        print(f"  Code: {error.error_code}")
        print(f"  Status: {error.status_code}")
        print(f"  Severity: {error.severity}")
        print(f"  Category: {error.category}")
        print(f"  Message: {error.user_message}")


if __name__ == "__main__":
    print("=" * 60)
    print("ERROR HANDLING FRAMEWORK DEMO")
    print("=" * 60)
    
    # Run all demos
    demo_basic_error()
    demo_validation_error()
    demo_solar_calculator_error()
    demo_error_handler()
    
    try:
        demo_function_with_decorator()
    except AppError as e:
        print(f"Caught decorated error: {e.error_code}")
    
    demo_error_context()
    demo_domain_errors()
    demo_error_response()
    demo_all_error_types()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
