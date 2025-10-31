"""Tests for Pricing Validation System

Comprehensive tests for input validation, error handling for invalid component
configurations, and validation for margin and modification settings.
"""


import pytest

from pricing.pricing_errors import (
    ComponentError,
    ProductNotFoundError,
    ValidationError,
    get_error_handler,
    handle_pricing_error,
    safe_pricing_operation,
)
from pricing.pricing_validation import (
    PricingValidator,
    ValidationCategory,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    get_pricing_validator,
)


class TestPricingValidator:
    """Test pricing validation system"""

    def setup_method(self):
        """Setup test environment"""
        self.validator = PricingValidator()

    def test_validate_component_data_valid(self):
        """Test validation of valid component data"""
        component_data = {
            "product_id": 123,
            "quantity": 5
        }

        result = self.validator.validate_component_data(component_data)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_component_data_missing_required_fields(self):
        """Test validation with missing required fields"""
        component_data = {
            "product_id": 123
            # Missing quantity
        }

        result = self.validator.validate_component_data(component_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "MISSING_REQUIRED_FIELD"
        assert result.errors[0].field == "quantity"

    def test_validate_component_data_invalid_product_id(self):
        """Test validation with invalid product ID"""
        component_data = {
            "product_id": -1,  # Invalid negative ID
            "quantity": 5
        }

        result = self.validator.validate_component_data(component_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_PRODUCT_ID"

    def test_validate_component_data_invalid_quantity(self):
        """Test validation with invalid quantity"""
        component_data = {
            "product_id": 123,
            "quantity": -5  # Invalid negative quantity
        }

        result = self.validator.validate_component_data(component_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_QUANTITY"

    def test_validate_component_data_high_quantity_warning(self):
        """Test validation with unusually high quantity"""
        component_data = {
            "product_id": 123,
            "quantity": 15000  # Very high quantity
        }

        result = self.validator.validate_component_data(component_data)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "HIGH_QUANTITY"

    def test_validate_product_data_valid(self):
        """Test validation of valid product data"""
        product_data = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 250.0,
            "calculate_per": "Stück",
            "capacity_w": 400,
            "efficiency_percent": 20.5,
            "warranty_years": 25
        }

        result = self.validator.validate_product_data(product_data)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_product_data_missing_required_fields(self):
        """Test validation with missing required product fields"""
        product_data = {
            "id": 123,
            "model_name": "Test Module"
            # Missing category and price_euro
        }

        result = self.validator.validate_product_data(product_data)

        assert not result.is_valid
        assert len(result.errors) == 2  # Missing category and price_euro

    def test_validate_product_data_invalid_price(self):
        """Test validation with invalid price"""
        product_data = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": -100.0  # Invalid negative price
        }

        result = self.validator.validate_product_data(product_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "NEGATIVE_PRICE"

    def test_validate_product_data_unknown_calculate_per(self):
        """Test validation with unknown calculate_per method"""
        product_data = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 250.0,
            "calculate_per": "unknown_method"
        }

        result = self.validator.validate_product_data(product_data)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "UNKNOWN_CALCULATE_PER"

    def test_validate_product_data_invalid_efficiency(self):
        """Test validation with invalid efficiency"""
        product_data = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 250.0,
            "efficiency_percent": 150.0  # Invalid >100% efficiency
        }

        result = self.validator.validate_product_data(product_data)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "INVALID_EFFICIENCY"

    def test_validate_margin_configuration_valid(self):
        """Test validation of valid margin configuration"""
        margin_config = {
            "margin_type": "percentage",
            "margin_value": 25.0,
            "priority": 10
        }

        result = self.validator.validate_margin_configuration(margin_config)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_margin_configuration_invalid_type(self):
        """Test validation with invalid margin type"""
        margin_config = {
            "margin_type": "invalid_type",
            "margin_value": 25.0
        }

        result = self.validator.validate_margin_configuration(margin_config)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_MARGIN_TYPE"

    def test_validate_margin_configuration_high_percentage(self):
        """Test validation with very high margin percentage"""
        margin_config = {
            "margin_type": "percentage",
            "margin_value": 2000.0  # Very high margin
        }

        result = self.validator.validate_margin_configuration(margin_config)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "HIGH_MARGIN_PERCENTAGE"

    def test_validate_margin_configuration_negative_fixed(self):
        """Test validation with negative fixed margin"""
        margin_config = {
            "margin_type": "fixed",
            "margin_value": -50.0  # Negative fixed margin
        }

        result = self.validator.validate_margin_configuration(margin_config)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "NEGATIVE_FIXED_MARGIN"

    def test_validate_modification_configuration_valid_discount(self):
        """Test validation of valid discount configuration"""
        discount_config = {
            "discount_type": "percentage",
            "discount_value": 10.0,
            "minimum_amount": 1000.0,
            "conditions": {"customer_type": "premium"}
        }

        result = self.validator.validate_modification_configuration(
            discount_config)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_modification_configuration_valid_surcharge(self):
        """Test validation of valid surcharge configuration"""
        surcharge_config = {
            "surcharge_type": "fixed",
            "surcharge_value": 100.0,
            "minimum_amount": 0.0
        }

        result = self.validator.validate_modification_configuration(
            surcharge_config)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_modification_configuration_missing_type(self):
        """Test validation with missing modification type"""
        config = {
            "value": 10.0
            # Missing discount_type or surcharge_type
        }

        result = self.validator.validate_modification_configuration(config)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "UNKNOWN_MODIFICATION_TYPE"

    def test_validate_modification_configuration_invalid_discount_percentage(
            self):
        """Test validation with invalid discount percentage"""
        discount_config = {
            "discount_type": "percentage",
            "discount_value": 150.0  # Invalid >100% discount
        }

        result = self.validator.validate_modification_configuration(
            discount_config)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_DISCOUNT_PERCENTAGE"

    def test_validate_pricing_calculation_data_valid(self):
        """Test validation of valid pricing calculation data"""
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 10},
                {"product_id": 456, "quantity": 1}
            ],
            "modifications": {
                "discount_percent": 5.0,
                "surcharge_fixed": 50.0
            },
            "vat_rate": 19.0
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_pricing_calculation_data_missing_components(self):
        """Test validation with missing components"""
        calculation_data = {
            "modifications": {"discount_percent": 5.0}
            # Missing components
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "MISSING_COMPONENTS"

    def test_validate_pricing_calculation_data_invalid_components_type(self):
        """Test validation with invalid components type"""
        calculation_data = {
            "components": "not_a_list"  # Should be a list
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_COMPONENTS_TYPE"

    def test_validate_pricing_calculation_data_unusual_vat_rate(self):
        """Test validation with unusual VAT rate"""
        calculation_data = {
            "components": [{"product_id": 123, "quantity": 1}],
            "vat_rate": 75.0  # Unusually high VAT rate
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "UNUSUAL_VAT_RATE"

    def test_validate_final_pricing_result_valid(self):
        """Test validation of valid final pricing result"""
        pricing_result = {
            "base_price": 1000.0,
            "final_price_net": 950.0,
            "final_price_gross": 1130.5,
            "vat_amount": 180.5,
            "total_discounts": 50.0,
            "total_surcharges": 0.0
        }

        result = self.validator.validate_final_pricing_result(pricing_result)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_final_pricing_result_price_consistency_error(self):
        """Test validation with price consistency error"""
        pricing_result = {
            "base_price": 1000.0,
            "final_price_net": 950.0,
            "final_price_gross": 1000.0,  # Inconsistent with net + VAT
            "vat_amount": 180.5
        }

        result = self.validator.validate_final_pricing_result(pricing_result)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "PRICE_CONSISTENCY_ERROR"

    def test_validate_final_pricing_result_negative_price(self):
        """Test validation with negative price"""
        pricing_result = {
            "base_price": 1000.0,
            "final_price_net": -100.0,  # Invalid negative price
            "final_price_gross": -81.0,
            "vat_amount": 19.0
        }

        result = self.validator.validate_final_pricing_result(pricing_result)

        assert not result.is_valid
        assert len(result.errors) >= 1
        assert any(error.code == "NEGATIVE_PRICE" for error in result.errors)

    def test_business_rules_validation_incomplete_pv_system(self):
        """Test business rule validation for incomplete PV system"""
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 10, "category": "PV-Module"}
                # Missing inverter
            ]
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) >= 1
        assert any(
            warning.code == "INCOMPLETE_PV_SYSTEM" for warning in result.warnings)

    def test_get_validation_rules(self):
        """Test getting validation rules"""
        rules = self.validator.get_validation_rules()

        assert isinstance(rules, dict)
        assert "min_price" in rules
        assert "max_price" in rules
        assert "valid_calculate_per_methods" in rules

    def test_update_validation_rules(self):
        """Test updating validation rules"""
        new_rules = {"min_price": 1.0, "max_price": 500000.0}

        success = self.validator.update_validation_rules(new_rules)

        assert success
        rules = self.validator.get_validation_rules()
        assert rules["min_price"] == 1.0
        assert rules["max_price"] == 500000.0

    def test_global_validator_instance(self):
        """Test global validator instance"""
        validator1 = get_pricing_validator()
        validator2 = get_pricing_validator()

        assert validator1 is validator2  # Should be the same instance


class TestValidationResult:
    """Test ValidationResult class"""

    def test_validation_result_creation(self):
        """Test ValidationResult creation and categorization"""
        result = ValidationResult(is_valid=True)

        # Add an error
        error = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            category=ValidationCategory.COMPONENT,
            code="TEST_ERROR",
            message="Test error message"
        )
        result.add_issue(error)

        # Add a warning
        warning = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            category=ValidationCategory.PRICING,
            code="TEST_WARNING",
            message="Test warning message"
        )
        result.add_issue(warning)

        assert not result.is_valid  # Should be invalid due to error
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.issues) == 2

    def test_validation_result_summary(self):
        """Test ValidationResult summary"""
        result = ValidationResult(is_valid=True)

        result.add_issue(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            category=ValidationCategory.COMPONENT,
            code="TEST_ERROR",
            message="Test error"
        ))

        result.add_issue(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            category=ValidationCategory.PRICING,
            code="TEST_WARNING",
            message="Test warning"
        ))

        summary = result.get_summary()

        assert summary["is_valid"] == False
        assert summary["total_issues"] == 2
        assert summary["error_count"] == 1
        assert summary["warning_count"] == 1
        assert summary["categories"]["component"] == 1
        assert summary["categories"]["pricing"] == 1


class TestPricingErrors:
    """Test pricing error classes"""

    def test_pricing_error_creation(self):
        """Test PricingError creation"""
        from pricing.pricing_errors import PricingError

        error = PricingError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"test_key": "test_value"},
            suggestion="Test suggestion"
        )

        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.context["test_key"] == "test_value"
        assert error.suggestion == "Test suggestion"

    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError(
            message="Validation failed",
            field="test_field",
            value="invalid_value",
            validation_issues=[{"code": "INVALID", "message": "Invalid value"}]
        )

        assert error.error_code == "VALIDATION_ERROR"
        assert error.context["field"] == "test_field"
        assert error.context["value"] == "invalid_value"
        assert len(error.context["validation_issues"]) == 1

    def test_component_error_creation(self):
        """Test ComponentError creation"""
        error = ComponentError(
            message="Component error",
            component_id=123,
            product_id=456
        )

        assert error.error_code == "COMPONENT_ERROR"
        assert error.context["component_id"] == 123
        assert error.context["product_id"] == 456

    def test_product_not_found_error_creation(self):
        """Test ProductNotFoundError creation"""
        error = ProductNotFoundError(product_identifier=123)

        assert error.error_code == "PRODUCT_NOT_FOUND"
        assert error.context["product_identifier"] == 123
        assert "Product not found: 123" in str(error)

    def test_error_to_dict(self):
        """Test error serialization to dictionary"""
        from pricing.pricing_errors import PricingError

        error = PricingError(
            message="Test error",
            error_code="TEST_ERROR",
            context={"key": "value"}
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "PricingError"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"]["key"] == "value"
        assert "timestamp" in error_dict


class TestPricingErrorHandler:
    """Test pricing error handler"""

    def setup_method(self):
        """Setup test environment"""
        self.error_handler = get_error_handler()
        self.error_handler.clear_error_history()

    def test_handle_validation_error(self):
        """Test handling validation error"""
        from pricing.pricing_errors import ErrorContext

        error = ValidationError("Test validation error", field="test_field")
        context = ErrorContext(
            operation="test_operation",
            component="test_component")

        # Test without reraising
        error_info = self.error_handler.handle_error(
            error, context, reraise=False)

        assert error_info is not None
        assert error_info["error_type"] == "ValidationError"
        assert error_info["message"] == "Test validation error"

    def test_handle_component_error(self):
        """Test handling component error"""
        from pricing.pricing_errors import ErrorContext

        error = ComponentError("Test component error", product_id=123)
        context = ErrorContext(
            operation="test_operation",
            component="test_component")

        error_info = self.error_handler.handle_error(
            error, context, reraise=False)

        assert error_info is not None
        assert error_info["error_type"] == "ComponentError"

    def test_error_statistics(self):
        """Test error statistics"""
        from pricing.pricing_errors import ComponentError, ErrorContext, ValidationError

        # Generate some test errors
        context = ErrorContext(operation="test", component="test")

        self.error_handler.handle_error(
            ValidationError("Test 1"), context, reraise=False
        )
        self.error_handler.handle_error(
            ValidationError("Test 2"), context, reraise=False
        )
        self.error_handler.handle_error(
            ComponentError("Test 3"), context, reraise=False
        )

        stats = self.error_handler.get_error_statistics()

        assert stats["total_errors"] == 3
        assert stats["error_counts_by_type"]["ValidationError"] == 2
        assert stats["error_counts_by_type"]["ComponentError"] == 1
        assert stats["most_common_error"] == "ValidationError"

    def test_recent_errors(self):
        """Test getting recent errors"""
        from pricing.pricing_errors import ErrorContext, ValidationError

        context = ErrorContext(operation="test", component="test")

        self.error_handler.handle_error(
            ValidationError("Recent error"), context, reraise=False
        )

        recent_errors = self.error_handler.get_recent_errors(hours=1)

        assert len(recent_errors) == 1
        assert recent_errors[0]["message"] == "Recent error"

    def test_handle_pricing_error_function(self):
        """Test handle_pricing_error convenience function"""
        from pricing.pricing_errors import ValidationError

        error = ValidationError("Test error")

        with pytest.raises(ValidationError):
            handle_pricing_error(
                error,
                operation="test_operation",
                component="test_component",
                extra_data="test_value"
            )

    def test_safe_pricing_operation_decorator(self):
        """Test safe_pricing_operation decorator"""

        @safe_pricing_operation("test_operation", "test_component")
        def test_function():
            raise ValidationError("Test error in decorated function")

        with pytest.raises(ValidationError):
            test_function()

    def test_safe_pricing_operation_decorator_success(self):
        """Test safe_pricing_operation decorator with successful operation"""

        @safe_pricing_operation("test_operation", "test_component")
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"


class TestValidationIntegration:
    """Integration tests for validation system"""

    def setup_method(self):
        """Setup test environment"""
        self.validator = PricingValidator()

    def test_complete_pricing_validation_workflow(self):
        """Test complete validation workflow"""
        # Test data representing a complete pricing calculation
        calculation_data = {
            "components": [
                {
                    "product_id": 123,
                    "quantity": 20,
                    "category": "PV-Module"
                },
                {
                    "product_id": 456,
                    "quantity": 1,
                    "category": "Wechselrichter"
                }
            ],
            "modifications": {
                "discount_percent": 5.0,
                "surcharge_fixed": 100.0,
                "accessories_cost": 200.0
            },
            "vat_rate": 19.0
        }

        # Validate calculation data
        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert result.is_valid
        assert len(result.errors) == 0

        # Simulate final pricing result
        final_result = {
            "base_price": 5000.0,
            "final_price_net": 4950.0,  # After 5% discount + 100€ surcharge
            "final_price_gross": 5890.5,  # With 19% VAT
            "vat_amount": 940.5,
            "total_discounts": 250.0,
            "total_surcharges": 100.0
        }

        # Validate final result
        final_validation = self.validator.validate_final_pricing_result(
            final_result)

        assert final_validation.is_valid
        assert len(final_validation.errors) == 0

    def test_validation_with_multiple_issues(self):
        """Test validation with multiple issues of different severities"""
        calculation_data = {
            "components": [
                {
                    "product_id": -1,  # Invalid product ID (error)
                    "quantity": 15000,  # High quantity (warning)
                    "category": "Unknown"  # Unknown category (warning)
                }
            ],
            "modifications": {
                "discount_percent": 150.0,  # Invalid discount (error)
                "surcharge_fixed": -50.0  # Negative surcharge (warning)
            },
            "vat_rate": 75.0  # Unusual VAT rate (warning)
        }

        result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        assert not result.is_valid  # Should be invalid due to errors
        # At least product ID and discount errors
        assert len(result.errors) >= 2
        # At least quantity, category, and VAT warnings
        assert len(result.warnings) >= 3

        # Check that we have the expected error types
        error_codes = [error.code for error in result.errors]
        assert "INVALID_PRODUCT_ID" in error_codes

        warning_codes = [warning.code for warning in result.warnings]
        assert "HIGH_QUANTITY" in warning_codes
        assert "UNUSUAL_VAT_RATE" in warning_codes


if __name__ == "__main__":
    pytest.main([__file__])
