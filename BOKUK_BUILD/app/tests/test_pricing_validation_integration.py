"""Integration Tests for Pricing Validation and Audit Systems

Tests the integration of validation, error handling, and audit systems
with the existing pricing engine.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pricing.enhanced_pricing_engine import PricingEngine
from pricing.pricing_errors import (
    ProductNotFoundError,
    ValidationError,
)
from pricing.pricing_validation import get_pricing_validator


class TestPricingValidationIntegration:
    """Test integration of validation with pricing engine"""

    def setup_method(self):
        """Setup test environment"""
        self.pricing_engine = PricingEngine("pv", enable_caching=False)
        self.validator = get_pricing_validator()

        # Setup temporary audit database
        self.temp_dir = tempfile.mkdtemp()
        self.audit_db_path = Path(self.temp_dir) / "test_audit.db"

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_successful_calculation_with_validation_and_audit(
            self, mock_get_product):
        """Test successful calculation with validation and audit logging"""
        # Mock product data
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test PV Module",
            "category": "PV-Module",
            "price_euro": 250.0,
            "calculate_per": "Stück",
            "capacity_w": 400,
            "efficiency_percent": 20.5,
            "warranty_years": 25
        }

        # Valid component data
        components = [
            {
                "product_id": 123,
                "quantity": 10
            }
        ]

        # Calculate base price (should succeed with validation)
        result = self.pricing_engine.calculate_base_price(components)

        assert result.base_price == 2500.0  # 250 * 10
        assert len(result.components) == 1
        assert result.components[0].model_name == "Test PV Module"
        assert result.components[0].total_price == 2500.0

    def test_validation_error_on_invalid_component_data(self):
        """Test validation error with invalid component data"""
        # Invalid component data (negative quantity)
        components = [
            {
                "product_id": 123,
                "quantity": -5  # Invalid negative quantity
            }
        ]

        # Should raise ValidationError due to invalid quantity
        with pytest.raises(ValidationError) as exc_info:
            self.pricing_engine.calculate_base_price(components)

        assert "validation failed" in str(exc_info.value).lower()
        assert "quantity" in str(exc_info.value).lower()

    def test_validation_error_on_missing_required_fields(self):
        """Test validation error with missing required fields"""
        # Missing required fields
        components = [
            {
                "product_id": 123
                # Missing quantity
            }
        ]

        # Should raise ValidationError due to missing quantity
        with pytest.raises(ValidationError) as exc_info:
            self.pricing_engine.calculate_base_price(components)

        assert "validation failed" in str(exc_info.value).lower()

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_product_not_found_error(self, mock_get_product):
        """Test ProductNotFoundError when product doesn't exist"""
        # Mock product not found
        mock_get_product.return_value = None

        components = [
            {
                "product_id": 999,  # Non-existent product
                "quantity": 5
            }
        ]

        # Should raise ProductNotFoundError
        with pytest.raises(ProductNotFoundError) as exc_info:
            self.pricing_engine.calculate_base_price(components)

        assert "999" in str(exc_info.value)

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_product_validation_warnings_logged(self, mock_get_product):
        """Test that product validation warnings are logged but don't stop calculation"""
        # Mock product with validation warnings (unusual efficiency)
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 250.0,
            "calculate_per": "unknown_method",  # Will generate warning
            "efficiency_percent": 150.0,  # Will generate warning (>100%)
            "warranty_years": 25
        }

        components = [
            {
                "product_id": 123,
                "quantity": 5
            }
        ]

        # Should succeed despite warnings
        with patch.object(self.pricing_engine.logger, 'warning') as mock_warning:
            result = self.pricing_engine.calculate_base_price(components)

            # Check that warnings were logged
            assert mock_warning.call_count >= 1
            warning_messages = [call[0][0]
                                for call in mock_warning.call_args_list]
            assert any("validation warning" in msg.lower()
                       for msg in warning_messages)

        # Calculation should still succeed
        assert result.base_price == 1250.0  # 250 * 5

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_final_pricing_validation(self, mock_get_product):
        """Test validation of final pricing calculation"""
        # Mock valid product
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 1000.0,
            "calculate_per": "Stück"
        }

        # Valid calculation data
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 1}
            ],
            "modifications": {
                "discount_percent": 10.0,
                "surcharge_fixed": 50.0
            },
            "vat_rate": 19.0
        }

        # Should succeed with valid data
        result = self.pricing_engine.generate_final_price(calculation_data)

        assert result.final_price_net > 0
        assert result.final_price_gross > result.final_price_net
        assert result.vat_amount > 0

    def test_final_pricing_validation_error_invalid_vat(self):
        """Test validation error with invalid VAT rate"""
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 1}
            ],
            "vat_rate": -5.0  # Invalid negative VAT rate
        }

        # Should raise ValidationError due to invalid VAT rate
        with pytest.raises(ValidationError) as exc_info:
            self.pricing_engine.generate_final_price(calculation_data)

        assert "validation failed" in str(exc_info.value).lower()

    def test_final_pricing_validation_error_missing_components(self):
        """Test validation error with missing components"""
        calculation_data = {
            # Missing components
            "modifications": {"discount_percent": 5.0}
        }

        # Should raise ValidationError due to missing components
        with pytest.raises(ValidationError) as exc_info:
            self.pricing_engine.generate_final_price(calculation_data)

        assert "validation failed" in str(exc_info.value).lower()
        assert "components" in str(exc_info.value).lower()


class TestPricingAuditIntegration:
    """Test integration of audit system with pricing engine"""

    def setup_method(self):
        """Setup test environment"""
        # Setup temporary audit database
        self.temp_dir = tempfile.mkdtemp()
        self.audit_db_path = Path(self.temp_dir) / "test_audit.db"

        # Create pricing engine with audit integration
        self.pricing_engine = PricingEngine("pv", enable_caching=False)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    @patch('pricing.pricing_audit.get_calculation_logger')
    def test_successful_calculation_audit_logging(
            self, mock_get_calc_logger, mock_get_product):
        """Test that successful calculations are audited"""
        # Mock calculation logger
        mock_calc_logger = Mock()
        mock_get_calc_logger.return_value = mock_calc_logger

        # Mock product data
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 500.0,
            "calculate_per": "Stück"
        }

        components = [{"product_id": 123, "quantity": 2}]

        # Calculate base price
        result = self.pricing_engine.calculate_base_price(components)

        # Verify audit logging was called
        mock_calc_logger.log_calculation_complete.assert_called_once()

        # Check the logged data
        call_args = mock_calc_logger.log_calculation_complete.call_args
        logged_result = call_args[0][0]
        duration_ms = call_args[0][1]

        assert logged_result["base_price"] == 1000.0  # 500 * 2
        assert logged_result["component_count"] == 1
        assert isinstance(duration_ms, float)
        assert duration_ms >= 0

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    @patch('pricing.pricing_audit.audit_price_calculation')
    def test_final_pricing_audit_logging(
            self, mock_audit_calc, mock_get_product):
        """Test that final pricing calculations are audited"""
        # Mock product data
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 1000.0,
            "calculate_per": "Stück"
        }

        calculation_data = {
            "components": [{"product_id": 123, "quantity": 1}],
            "modifications": {"discount_percent": 5.0},
            "vat_rate": 19.0
        }

        # Generate final price
        result = self.pricing_engine.generate_final_price(calculation_data)

        # Verify audit function was called
        mock_audit_calc.assert_called_once()

        # Check the audit call arguments
        call_args = mock_audit_calc.call_args
        logged_calc_data = call_args[1]["calculation_data"]
        logged_result = call_args[1]["result"]
        duration_ms = call_args[1]["duration_ms"]

        assert logged_calc_data == calculation_data
        assert "final_price_net" in logged_result
        assert isinstance(duration_ms, float)
        assert duration_ms >= 0

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    @patch('pricing.pricing_audit.audit_pricing_error')
    def test_calculation_error_audit_logging(
            self, mock_audit_error, mock_get_product):
        """Test that calculation errors are audited"""
        # Mock product not found to trigger error
        mock_get_product.return_value = None

        components = [{"product_id": 999, "quantity": 1}]

        # Should raise ProductNotFoundError and audit it
        with pytest.raises(ProductNotFoundError):
            self.pricing_engine.calculate_base_price(components)

        # Verify error audit was called
        mock_audit_error.assert_called_once()

        # Check the audit call arguments
        call_args = mock_audit_error.call_args
        logged_error = call_args[0][0]
        logged_context = call_args[0][1]

        assert isinstance(logged_error, ProductNotFoundError)
        assert "components" in logged_context

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    @patch('pricing.pricing_audit.audit_pricing_error')
    def test_validation_error_audit_logging(
            self, mock_audit_error, mock_get_product):
        """Test that validation errors are audited"""
        # Mock valid product but use invalid calculation data
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "Test Module",
            "category": "PV-Module",
            "price_euro": 1000.0
        }

        # Invalid calculation data (missing components)
        calculation_data = {
            "modifications": {"discount_percent": 5.0}
            # Missing components
        }

        # Should raise ValidationError and audit it
        with pytest.raises(ValidationError):
            self.pricing_engine.generate_final_price(calculation_data)

        # Verify error audit was called
        mock_audit_error.assert_called_once()

        # Check the audit call arguments
        call_args = mock_audit_error.call_args
        logged_error = call_args[0][0]
        logged_context = call_args[0][1]

        assert isinstance(logged_error, ValidationError)
        assert logged_context == calculation_data


class TestErrorHandlingIntegration:
    """Test integration of error handling with pricing operations"""

    def setup_method(self):
        """Setup test environment"""
        self.pricing_engine = PricingEngine("pv", enable_caching=False)

    def test_safe_pricing_operation_decorator(self):
        """Test that safe_pricing_operation decorator works correctly"""
        # The decorator should be applied to pricing engine methods
        # and should handle errors appropriately

        # Test with invalid data that should trigger validation error
        components = [{"product_id": -1, "quantity": -5}]  # Invalid data

        with pytest.raises(ValidationError):
            self.pricing_engine.calculate_base_price(components)

        # The error should be properly handled by the decorator
        # (no additional verification needed as the decorator re-raises)

    def test_error_context_preservation(self):
        """Test that error context is preserved through the system"""
        # Test with missing product to trigger ProductNotFoundError
        components = [{"product_id": 999, "quantity": 5}]

        with pytest.raises(ProductNotFoundError) as exc_info:
            self.pricing_engine.calculate_base_price(components)

        # Verify error context is preserved
        error = exc_info.value
        assert hasattr(error, 'context')
        assert 'product_identifier' in error.context
        assert error.context['product_identifier'] == 999

    def test_validation_error_details(self):
        """Test that validation errors contain detailed information"""
        # Test with invalid component data
        components = [{"product_id": "invalid", "quantity": "invalid"}]

        with pytest.raises(ValidationError) as exc_info:
            self.pricing_engine.calculate_base_price(components)

        # Verify validation error contains details
        error = exc_info.value
        assert hasattr(error, 'context')
        assert 'validation_issues' in error.context
        assert len(error.context['validation_issues']) > 0


class TestBusinessRuleValidation:
    """Test business rule validation integration"""

    def setup_method(self):
        """Setup test environment"""
        self.pricing_engine = PricingEngine("pv", enable_caching=False)
        self.validator = get_pricing_validator()

    @patch('pricing.enhanced_pricing_engine.get_product_by_id')
    def test_incomplete_pv_system_warning(self, mock_get_product):
        """Test business rule validation for incomplete PV systems"""
        # Mock PV module product
        mock_get_product.return_value = {
            "id": 123,
            "model_name": "PV Module",
            "category": "PV-Module",
            "price_euro": 300.0,
            "calculate_per": "Stück"
        }

        # Calculation data with only modules (missing inverter)
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 10, "category": "PV-Module"}
            ]
        }

        # Validate calculation data
        validation_result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        # Should be valid but have warnings about incomplete system
        assert validation_result.is_valid
        assert len(validation_result.warnings) > 0

        # Check for incomplete system warning
        warning_codes = [w.code for w in validation_result.warnings]
        assert "INCOMPLETE_PV_SYSTEM" in warning_codes

    def test_system_size_validation(self):
        """Test system size business rule validation"""
        # Test very small system
        calculation_data = {
            "components": [
                # Very small 100W system
                {"product_id": 123, "quantity": 1, "capacity_w": 100}
            ]
        }

        validation_result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        # Should have warning about small system size
        assert validation_result.is_valid
        warning_codes = [w.code for w in validation_result.warnings]
        assert "SMALL_SYSTEM_SIZE" in warning_codes

        # Test very large system
        calculation_data = {
            "components": [
                # Very large 500kW system
                {"product_id": 123, "quantity": 1000, "capacity_w": 500}
            ]
        }

        validation_result = self.validator.validate_pricing_calculation_data(
            calculation_data)

        # Should have warning about large system size
        assert validation_result.is_valid
        warning_codes = [w.code for w in validation_result.warnings]
        assert "LARGE_SYSTEM_SIZE" in warning_codes


if __name__ == "__main__":
    pytest.main([__file__])
