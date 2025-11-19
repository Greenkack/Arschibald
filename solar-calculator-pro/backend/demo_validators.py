"""
Demo: Validation Framework Usage Examples

This file demonstrates practical usage of the validation framework
for various scenarios in the Solar Calculator Pro application.
"""

from datetime import date, datetime
from core.validators import (
    NumberValidator,
    StringValidator,
    DateTimeValidator,
    EmailValidator,
    URLValidator,
    DictValidator,
    ListValidator,
    CompositeValidator,
    validate_number,
    validate_string,
    validate_email
)


def demo_basic_validation():
    """Demo: Basic validation examples"""
    print("=" * 60)
    print("DEMO: Basic Validation")
    print("=" * 60)
    
    # Number validation
    print("\n1. Number Validation:")
    result = validate_number(25, field_name="age", min_value=18, max_value=100)
    print(f"   validate_number(25, min=18, max=100): {result.is_valid}")
    
    result = validate_number(15, field_name="age", min_value=18)
    print(f"   validate_number(15, min=18): {result.is_valid}")
    if not result.is_valid:
        print(f"   Error: {result.errors[0].message}")
    
    # String validation
    print("\n2. String Validation:")
    result = validate_string("hello", field_name="greeting", min_length=3)
    print(f"   validate_string('hello', min_length=3): {result.is_valid}")
    
    result = validate_string("hi", field_name="greeting", min_length=3)
    print(f"   validate_string('hi', min_length=3): {result.is_valid}")
    if not result.is_valid:
        print(f"   Error: {result.errors[0].message}")
    
    # Email validation
    print("\n3. Email Validation:")
    result = validate_email("user@example.com")
    print(f"   validate_email('user@example.com'): {result.is_valid}")
    
    result = validate_email("invalid-email")
    print(f"   validate_email('invalid-email'): {result.is_valid}")
    if not result.is_valid:
        print(f"   Error: {result.errors[0].message}")


def demo_german_format():
    """Demo: German number format validation"""
    print("\n" + "=" * 60)
    print("DEMO: German Number Format")
    print("=" * 60)
    
    validator = NumberValidator(
        field_name="price",
        german_format=True,
        min_value=0,
        decimal_places=2
    )
    
    test_cases = [
        "1.234,56",    # Valid: 1234.56
        "50,5",        # Valid: 50.5
        "1.000",       # Valid: 1000
        "123,456",     # Valid: 123.456
        "-50,00",      # Invalid: negative
        "abc",         # Invalid: not a number
    ]
    
    print("\nValidating German number formats:")
    for test_value in test_cases:
        result = validator.validate(test_value)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {test_value:15} -> {status}")
        if not result.is_valid:
            print(f"      Error: {result.errors[0].message}")


def demo_solar_calculator_input():
    """Demo: Solar calculator input validation"""
    print("\n" + "=" * 60)
    print("DEMO: Solar Calculator Input Validation")
    print("=" * 60)
    
    # Define validation schema
    solar_schema = {
        "roof_area": NumberValidator(
            field_name="roof_area",
            required=True,
            min_value=10,
            max_value=1000,
            german_format=True
        ),
        "roof_angle": NumberValidator(
            field_name="roof_angle",
            required=True,
            min_value=0,
            max_value=90,
            allow_decimal=True,
            decimal_places=1
        ),
        "orientation": StringValidator(
            field_name="orientation",
            required=True,
            allowed_values=["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
        ),
        "annual_consumption": NumberValidator(
            field_name="annual_consumption",
            required=True,
            min_value=0,
            german_format=True
        ),
        "location": StringValidator(
            field_name="location",
            required=True,
            min_length=2,
            max_length=100
        )
    }
    
    validator = DictValidator(solar_schema)
    
    # Test case 1: Valid input
    print("\nTest Case 1: Valid Input")
    valid_input = {
        "roof_area": "50,5",
        "roof_angle": 30.0,
        "orientation": "south",
        "annual_consumption": "4.500",
        "location": "Berlin"
    }
    result = validator.validate(valid_input)
    print(f"   Result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    
    # Test case 2: Invalid input
    print("\nTest Case 2: Invalid Input")
    invalid_input = {
        "roof_area": "5",  # Too small
        "roof_angle": 95,  # Too large
        "orientation": "invalid",  # Not in allowed values
        "annual_consumption": "-100",  # Negative
        "location": "B"  # Too short
    }
    result = validator.validate(invalid_input)
    print(f"   Result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    if not result.is_valid:
        print(f"   Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"      - {error.field}: {error.message}")


def demo_price_matrix_validation():
    """Demo: Price matrix validation"""
    print("\n" + "=" * 60)
    print("DEMO: Price Matrix Validation")
    print("=" * 60)
    
    # Price entry validation
    price_validator = NumberValidator(
        field_name="price",
        required=True,
        min_value=0,
        german_format=True,
        decimal_places=2
    )
    
    print("\nValidating price entries:")
    prices = ["1.234,56", "50,00", "-10,00", "999.999,99"]
    for price in prices:
        result = price_validator.validate(price)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {price:15} -> {status}")
        if not result.is_valid:
            print(f"      Error: {result.errors[0].message}")
    
    # Product code validation
    print("\nValidating product codes:")
    code_validator = StringValidator(
        field_name="product_code",
        required=True,
        pattern=r'^[A-Z]{2,3}-\d{4,6}$'
    )
    
    codes = ["PV-12345", "INV-1234", "BAT-123456", "invalid", "pv-12345"]
    for code in codes:
        result = code_validator.validate(code)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {code:15} -> {status}")


def demo_user_registration():
    """Demo: User registration validation"""
    print("\n" + "=" * 60)
    print("DEMO: User Registration Validation")
    print("=" * 60)
    
    registration_schema = {
        "username": StringValidator(
            field_name="username",
            required=True,
            min_length=3,
            max_length=20,
            pattern=r'^[a-zA-Z0-9_]+$'
        ),
        "email": EmailValidator(
            field_name="email",
            required=True
        ),
        "password": StringValidator(
            field_name="password",
            required=True,
            min_length=8
        ),
        "age": NumberValidator(
            field_name="age",
            required=True,
            min_value=18,
            max_value=120,
            allow_decimal=False
        ),
        "website": URLValidator(
            field_name="website",
            required=False
        )
    }
    
    validator = DictValidator(registration_schema)
    
    # Valid registration
    print("\nTest Case 1: Valid Registration")
    valid_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123",
        "age": 30,
        "website": "https://johndoe.com"
    }
    result = validator.validate(valid_data)
    print(f"   Result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    
    # Invalid registration
    print("\nTest Case 2: Invalid Registration")
    invalid_data = {
        "username": "jd",  # Too short
        "email": "invalid-email",  # Invalid format
        "password": "short",  # Too short
        "age": 15,  # Too young
        "website": "not-a-url"  # Invalid URL
    }
    result = validator.validate(invalid_data)
    print(f"   Result: {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    if not result.is_valid:
        print(f"   Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"      - {error.field}: {error.message}")


def demo_custom_validators():
    """Demo: Custom validation rules"""
    print("\n" + "=" * 60)
    print("DEMO: Custom Validation Rules")
    print("=" * 60)
    
    # Even number validator
    print("\n1. Even Number Validator:")
    even_validator = NumberValidator(field_name="even_number")
    even_validator.add_custom_validator(
        lambda x: x % 2 == 0,
        "Number must be even"
    )
    
    for num in [2, 4, 5, 8, 9]:
        result = even_validator.validate(num)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {num} -> {status}")
    
    # Multiple of 5 validator
    print("\n2. Multiple of 5 Validator:")
    multiple_validator = NumberValidator(field_name="multiple")
    multiple_validator.add_custom_validator(
        lambda x: x % 5 == 0,
        "Number must be a multiple of 5"
    )
    
    for num in [5, 10, 12, 15, 17]:
        result = multiple_validator.validate(num)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {num} -> {status}")
    
    # Password strength validator
    print("\n3. Password Strength Validator:")
    password_validator = StringValidator(field_name="password", min_length=8)
    password_validator.add_custom_validator(
        lambda x: any(c.isupper() for c in x),
        "Password must contain at least one uppercase letter"
    )
    password_validator.add_custom_validator(
        lambda x: any(c.isdigit() for c in x),
        "Password must contain at least one digit"
    )
    
    passwords = ["password", "Password", "Password1", "pass"]
    for pwd in passwords:
        result = password_validator.validate(pwd)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {pwd:15} -> {status}")
        if not result.is_valid:
            for error in result.errors:
                print(f"      Error: {error.message}")


def demo_list_validation():
    """Demo: List validation"""
    print("\n" + "=" * 60)
    print("DEMO: List Validation")
    print("=" * 60)
    
    # Score list validator
    item_validator = NumberValidator(field_name="score", min_value=0, max_value=100)
    list_validator = ListValidator(
        item_validator,
        field_name="scores",
        min_items=1,
        max_items=10,
        unique=True
    )
    
    print("\nValidating score lists:")
    
    # Valid list
    result = list_validator.validate([85, 90, 95])
    print(f"   [85, 90, 95] -> {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    
    # Invalid: duplicate values
    result = list_validator.validate([85, 90, 85])
    print(f"   [85, 90, 85] -> {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    if not result.is_valid:
        print(f"      Error: {result.errors[0].message}")
    
    # Invalid: value out of range
    result = list_validator.validate([85, 150, 95])
    print(f"   [85, 150, 95] -> {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    if not result.is_valid:
        print(f"      Error: {result.errors[0].message}")
    
    # Invalid: too many items
    result = list_validator.validate(list(range(15)))
    print(f"   [0..14] (15 items) -> {'✓ Valid' if result.is_valid else '✗ Invalid'}")
    if not result.is_valid:
        print(f"      Error: {result.errors[0].message}")


def demo_composite_validators():
    """Demo: Composite validators"""
    print("\n" + "=" * 60)
    print("DEMO: Composite Validators")
    print("=" * 60)
    
    # Age validator with multiple rules
    validators = [
        NumberValidator(field_name="age", min_value=18),
        NumberValidator(field_name="age", max_value=100),
        NumberValidator(field_name="age", allow_decimal=False)
    ]
    composite = CompositeValidator(validators)
    
    print("\nValidating ages (must be 18-100, integer):")
    ages = [25, 17, 105, 25.5]
    for age in ages:
        result = composite.validate(age)
        status = "✓ Valid" if result.is_valid else "✗ Invalid"
        print(f"   {age} -> {status}")
        if not result.is_valid:
            for error in result.errors:
                print(f"      Error: {error.message}")


def demo_error_handling():
    """Demo: Error handling and reporting"""
    print("\n" + "=" * 60)
    print("DEMO: Error Handling and Reporting")
    print("=" * 60)
    
    validator = NumberValidator(
        field_name="age",
        required=True,
        min_value=18,
        max_value=100
    )
    
    print("\nValidation Result Structure:")
    result = validator.validate(15)
    
    print(f"\n   is_valid: {result.is_valid}")
    print(f"   error_count: {len(result.errors)}")
    
    if not result.is_valid:
        print("\n   Errors:")
        for i, error in enumerate(result.errors, 1):
            print(f"      {i}. Field: {error.field}")
            print(f"         Message: {error.message}")
            print(f"         Code: {error.code}")
            print(f"         Value: {error.value}")
    
    print("\n   As Dictionary:")
    result_dict = result.to_dict()
    import json
    print(f"   {json.dumps(result_dict, indent=6)}")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "VALIDATION FRAMEWORK DEMO" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")
    
    demo_basic_validation()
    demo_german_format()
    demo_solar_calculator_input()
    demo_price_matrix_validation()
    demo_user_registration()
    demo_custom_validators()
    demo_list_validation()
    demo_composite_validators()
    demo_error_handling()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - docs/VALIDATION_FRAMEWORK.md")
    print("  - docs/VALIDATION_QUICK_REFERENCE.md")
    print("  - tests/test_validators.py")
    print()


if __name__ == "__main__":
    main()
