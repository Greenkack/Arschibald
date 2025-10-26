"""Pricing Validation System

Comprehensive input validation for all pricing calculations, error handling
for invalid component configurations, and validation for margin and modification settings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(Enum):
    """Categories of validation checks"""
    COMPONENT = "component"
    PRICING = "pricing"
    MARGIN = "margin"
    MODIFICATION = "modification"
    CALCULATION = "calculation"
    BUSINESS_RULE = "business_rule"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: ValidationSeverity
    category: ValidationCategory
    code: str
    message: str
    field: str | None = None
    value: Any | None = None
    suggestion: str | None = None
    context: dict[str, Any] | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert validation issue to dictionary"""
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "value": self.value,
            "suggestion": self.suggestion,
            "context": self.context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class ValidationResult:
    """Result of validation checks"""
    is_valid: bool
    issues: list[ValidationIssue] | None = None
    warnings: list[ValidationIssue] | None = None
    errors: list[ValidationIssue] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Categorize issues by severity"""
        if self.issues is None:
            self.issues = []
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}

        self.errors = [
            issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
        self.warnings = [
            issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
        self.is_valid = len(self.errors) == 0

    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue"""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)

    def get_summary(self) -> dict[str, Any]:
        """Get validation summary"""
        return {
            "is_valid": self.is_valid,
            "total_issues": len(self.issues),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "categories": {
                category.value: len([i for i in self.issues if i.category == category])
                for category in ValidationCategory
            }
        }


class PricingValidator:
    """Comprehensive pricing validation system"""

    def __init__(self):
        """Initialize pricing validator"""
        self.logger = logging.getLogger(f"{__name__}.PricingValidator")

        # Validation rules configuration
        self.rules = {
            "min_price": 0.0,
            "max_price": 1000000.0,  # 1 million euro max
            "min_quantity": 0.0,
            "max_quantity": 10000.0,
            # Allow negative margins (loss leaders)
            "min_margin_percentage": -100.0,
            "max_margin_percentage": 1000.0,  # 1000% max margin
            "min_discount_percentage": 0.0,
            "max_discount_percentage": 100.0,
            "min_surcharge_percentage": 0.0,
            "max_surcharge_percentage": 500.0,  # 500% max surcharge
            "valid_calculate_per_methods": [
                "stück", "piece", "unit",
                "meter", "m",
                "pauschal", "lump_sum", "flat",
                "kwp", "kw_peak"
            ],
            "valid_margin_types": ["percentage", "fixed"],
            "valid_modification_types": ["percentage", "fixed", "tiered"],
            "required_product_fields": ["id", "model_name", "category", "price_euro"],
            "valid_categories": [
                "PV-Module", "Wechselrichter", "Batteriespeicher", "Montagesystem",
                "Kabel", "Zubehör", "Wärmepumpe", "Installation", "Service"
            ]
        }

    def validate_component_data(
            self, component_data: dict[str, Any]) -> ValidationResult:
        """Validate component data for pricing calculations

        Args:
            component_data: Component data to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Check required fields
            self._validate_required_fields(
                component_data,
                ["product_id", "quantity"],
                result,
                ValidationCategory.COMPONENT
            )

            # Validate product_id
            if "product_id" in component_data:
                product_id = component_data["product_id"]
                if not isinstance(product_id, int) or product_id <= 0:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.COMPONENT,
                            code="INVALID_PRODUCT_ID",
                            message=f"Product ID must be a positive integer, got: {product_id}",
                            field="product_id",
                            value=product_id,
                            suggestion="Provide a valid product ID from the database"))

            # Validate quantity
            if "quantity" in component_data:
                quantity = component_data["quantity"]
                if not isinstance(quantity, (int, float)
                                  ) or quantity < self.rules["min_quantity"]:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.COMPONENT,
                            code="INVALID_QUANTITY",
                            message=f"Quantity must be a positive number, got: {quantity}",
                            field="quantity",
                            value=quantity,
                            suggestion=f"Provide quantity >= {
                                self.rules['min_quantity']}"))
                elif quantity > self.rules["max_quantity"]:
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.COMPONENT,
                        code="HIGH_QUANTITY",
                        message=f"Unusually high quantity: {quantity}",
                        field="quantity",
                        value=quantity,
                        suggestion="Verify quantity is correct"
                    ))

            # Validate optional fields if present
            if "price_override" in component_data:
                self._validate_price_value(
                    component_data["price_override"],
                    "price_override",
                    result
                )

            return result

        except Exception as e:
            self.logger.error(f"Error validating component data: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.COMPONENT,
                code="VALIDATION_ERROR",
                message=f"Validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def validate_product_data(
            self, product_data: dict[str, Any]) -> ValidationResult:
        """Validate product data from database

        Args:
            product_data: Product data to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Check required fields
            self._validate_required_fields(
                product_data,
                self.rules["required_product_fields"],
                result,
                ValidationCategory.COMPONENT
            )

            # Validate price_euro
            if "price_euro" in product_data:
                self._validate_price_value(
                    product_data["price_euro"],
                    "price_euro",
                    result
                )

            # Validate calculate_per method
            if "calculate_per" in product_data:
                calculate_per = product_data["calculate_per"]
                if calculate_per and calculate_per.lower(
                ) not in self.rules["valid_calculate_per_methods"]:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.COMPONENT,
                            code="UNKNOWN_CALCULATE_PER",
                            message=f"Unknown calculate_per method: {calculate_per}",
                            field="calculate_per",
                            value=calculate_per,
                            suggestion=f"Valid methods: {
                                ', '.join(
                                    self.rules['valid_calculate_per_methods'])}"))

            # Validate category
            if "category" in product_data:
                category = product_data["category"]
                if category not in self.rules["valid_categories"]:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.COMPONENT,
                            code="UNKNOWN_CATEGORY",
                            message=f"Unknown product category: {category}",
                            field="category",
                            value=category,
                            suggestion=f"Valid categories: {
                                ', '.join(
                                    self.rules['valid_categories'])}"))

            # Validate technical specifications
            self._validate_technical_specs(product_data, result)

            return result

        except Exception as e:
            self.logger.error(f"Error validating product data: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.COMPONENT,
                code="VALIDATION_ERROR",
                message=f"Product validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def validate_margin_configuration(
            self, margin_config: dict[str, Any]) -> ValidationResult:
        """Validate margin configuration

        Args:
            margin_config: Margin configuration to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Check required fields
            self._validate_required_fields(
                margin_config,
                ["margin_type", "margin_value"],
                result,
                ValidationCategory.MARGIN
            )

            # Validate margin_type
            if "margin_type" in margin_config:
                margin_type = margin_config["margin_type"]
                if margin_type not in self.rules["valid_margin_types"]:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MARGIN,
                            code="INVALID_MARGIN_TYPE",
                            message=f"Invalid margin type: {margin_type}",
                            field="margin_type",
                            value=margin_type,
                            suggestion=f"Valid types: {
                                ', '.join(
                                    self.rules['valid_margin_types'])}"))

            # Validate margin_value
            if "margin_value" in margin_config:
                margin_value = margin_config["margin_value"]
                margin_type = margin_config.get("margin_type", "percentage")

                if not isinstance(margin_value, (int, float)):
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MARGIN,
                            code="INVALID_MARGIN_VALUE_TYPE",
                            message=f"Margin value must be numeric, got: {
                                type(margin_value).__name__}",
                            field="margin_value",
                            value=margin_value))
                else:
                    if margin_type == "percentage":
                        if margin_value < self.rules["min_margin_percentage"]:
                            result.add_issue(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    category=ValidationCategory.MARGIN,
                                    code="LOW_MARGIN_PERCENTAGE",
                                    message=f"Very low margin percentage: {margin_value}%",
                                    field="margin_value",
                                    value=margin_value,
                                    suggestion="Verify this is intentional (loss leader?)"))
                        elif margin_value > self.rules["max_margin_percentage"]:
                            result.add_issue(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    category=ValidationCategory.MARGIN,
                                    code="HIGH_MARGIN_PERCENTAGE",
                                    message=f"Very high margin percentage: {margin_value}%",
                                    field="margin_value",
                                    value=margin_value,
                                    suggestion="Verify this is correct"))
                    elif margin_type == "fixed":
                        if margin_value < 0:
                            result.add_issue(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    category=ValidationCategory.MARGIN,
                                    code="NEGATIVE_FIXED_MARGIN",
                                    message=f"Negative fixed margin: {margin_value}€",
                                    field="margin_value",
                                    value=margin_value,
                                    suggestion="Verify this is intentional"))

            # Validate priority if present
            if "priority" in margin_config:
                priority = margin_config["priority"]
                if not isinstance(priority, int) or priority < 0:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MARGIN,
                            code="INVALID_PRIORITY",
                            message=f"Priority must be a non-negative integer, got: {priority}",
                            field="priority",
                            value=priority))

            return result

        except Exception as e:
            self.logger.error(f"Error validating margin configuration: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.MARGIN,
                code="VALIDATION_ERROR",
                message=f"Margin validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def validate_modification_configuration(
            self, modification_config: dict[str, Any]) -> ValidationResult:
        """Validate discount/surcharge modification configuration

        Args:
            modification_config: Modification configuration to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Determine modification type (discount or surcharge)
            mod_type = None
            if "discount_type" in modification_config:
                mod_type = "discount"
                type_field = "discount_type"
                value_field = "discount_value"
            elif "surcharge_type" in modification_config:
                mod_type = "surcharge"
                type_field = "surcharge_type"
                value_field = "surcharge_value"
            else:
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.MODIFICATION,
                        code="UNKNOWN_MODIFICATION_TYPE",
                        message="Configuration must specify either discount_type or surcharge_type",
                        suggestion="Add discount_type or surcharge_type field"))
                return result

            # Validate modification type
            if type_field in modification_config:
                config_type = modification_config[type_field]
                if config_type not in self.rules["valid_modification_types"]:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MODIFICATION,
                            code="INVALID_MODIFICATION_TYPE",
                            message=f"Invalid {mod_type} type: {config_type}",
                            field=type_field,
                            value=config_type,
                            suggestion=f"Valid types: {
                                ', '.join(
                                    self.rules['valid_modification_types'])}"))

            # Validate modification value
            if value_field in modification_config:
                mod_value = modification_config[value_field]
                config_type = modification_config.get(type_field, "percentage")

                if not isinstance(mod_value, (int, float)):
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MODIFICATION,
                            code="INVALID_MODIFICATION_VALUE_TYPE",
                            message=f"{
                                mod_type.title()} value must be numeric, got: {
                                type(mod_value).__name__}",
                            field=value_field,
                            value=mod_value))
                else:
                    if config_type == "percentage":
                        if mod_type == "discount":
                            if mod_value < self.rules["min_discount_percentage"] or mod_value > self.rules["max_discount_percentage"]:
                                result.add_issue(
                                    ValidationIssue(
                                        severity=ValidationSeverity.ERROR,
                                        category=ValidationCategory.MODIFICATION,
                                        code="INVALID_DISCOUNT_PERCENTAGE",
                                        message=f"Discount percentage must be between {
                                            self.rules['min_discount_percentage']}% and {
                                            self.rules['max_discount_percentage']}%, got: {mod_value}%",
                                        field=value_field,
                                        value=mod_value))
                        elif mod_type == "surcharge":
                            if mod_value < self.rules["min_surcharge_percentage"]:
                                result.add_issue(
                                    ValidationIssue(
                                        severity=ValidationSeverity.ERROR,
                                        category=ValidationCategory.MODIFICATION,
                                        code="NEGATIVE_SURCHARGE_PERCENTAGE",
                                        message=f"Surcharge percentage cannot be negative, got: {mod_value}%",
                                        field=value_field,
                                        value=mod_value))
                            elif mod_value > self.rules["max_surcharge_percentage"]:
                                result.add_issue(
                                    ValidationIssue(
                                        severity=ValidationSeverity.WARNING,
                                        category=ValidationCategory.MODIFICATION,
                                        code="HIGH_SURCHARGE_PERCENTAGE",
                                        message=f"Very high surcharge percentage: {mod_value}%",
                                        field=value_field,
                                        value=mod_value,
                                        suggestion="Verify this is correct"))
                    elif config_type == "fixed":
                        if mod_value < 0:
                            result.add_issue(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    category=ValidationCategory.MODIFICATION,
                                    code="NEGATIVE_FIXED_MODIFICATION",
                                    message=f"Negative fixed {mod_type}: {mod_value}€",
                                    field=value_field,
                                    value=mod_value,
                                    suggestion="Verify this is intentional"))

            # Validate conditions if present
            if "conditions" in modification_config:
                conditions = modification_config["conditions"]
                if not isinstance(conditions, dict):
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.MODIFICATION,
                        code="INVALID_CONDITIONS_TYPE",
                        message="Conditions must be a dictionary",
                        field="conditions",
                        value=type(conditions).__name__
                    ))

            # Validate minimum_amount if present
            if "minimum_amount" in modification_config:
                min_amount = modification_config["minimum_amount"]
                if not isinstance(min_amount, (int, float)) or min_amount < 0:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.MODIFICATION,
                            code="INVALID_MINIMUM_AMOUNT",
                            message=f"Minimum amount must be non-negative number, got: {min_amount}",
                            field="minimum_amount",
                            value=min_amount))

            return result

        except Exception as e:
            self.logger.error(
                f"Error validating modification configuration: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.MODIFICATION,
                code="VALIDATION_ERROR",
                message=f"Modification validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def validate_pricing_calculation_data(
            self, calculation_data: dict[str, Any]) -> ValidationResult:
        """Validate complete pricing calculation data

        Args:
            calculation_data: Complete calculation data to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Validate components
            if "components" not in calculation_data:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.CALCULATION,
                    code="MISSING_COMPONENTS",
                    message="Calculation data must include components",
                    suggestion="Add 'components' field with list of components"
                ))
            else:
                components = calculation_data["components"]
                if not isinstance(components, list):
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.CALCULATION,
                        code="INVALID_COMPONENTS_TYPE",
                        message="Components must be a list",
                        field="components",
                        value=type(components).__name__
                    ))
                else:
                    # Validate each component
                    for i, component in enumerate(components):
                        comp_result = self.validate_component_data(component)
                        for issue in comp_result.issues:
                            issue.context["component_index"] = i
                            result.add_issue(issue)

            # Validate modifications if present
            if "modifications" in calculation_data:
                modifications = calculation_data["modifications"]
                if not isinstance(modifications, dict):
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.CALCULATION,
                        code="INVALID_MODIFICATIONS_TYPE",
                        message="Modifications must be a dictionary",
                        field="modifications",
                        value=type(modifications).__name__
                    ))
                else:
                    # Validate modification values
                    for mod_key, mod_value in modifications.items():
                        if mod_key.endswith("_percent") and isinstance(
                                mod_value, (int, float)):
                            if mod_key == "discount_percent":
                                # Discount percentages have stricter validation
                                if mod_value < 0 or mod_value > 100:
                                    result.add_issue(
                                        ValidationIssue(
                                            severity=ValidationSeverity.ERROR,
                                            category=ValidationCategory.CALCULATION,
                                            code="INVALID_DISCOUNT_PERCENTAGE",
                                            message=f"Invalid discount percentage: {mod_value}% (must be 0-100%)",
                                            field=mod_key,
                                            value=mod_value,
                                            suggestion="Discount percentage must be between 0% and 100%"))
                            elif mod_value < 0 or mod_value > 100:
                                result.add_issue(
                                    ValidationIssue(
                                        severity=ValidationSeverity.WARNING,
                                        category=ValidationCategory.CALCULATION,
                                        code="UNUSUAL_PERCENTAGE",
                                        message=f"Unusual percentage value for {mod_key}: {mod_value}%",
                                        field=mod_key,
                                        value=mod_value))
                        elif mod_key.endswith("_fixed") and isinstance(mod_value, (int, float)):
                            if mod_value < 0:
                                result.add_issue(
                                    ValidationIssue(
                                        severity=ValidationSeverity.WARNING,
                                        category=ValidationCategory.CALCULATION,
                                        code="NEGATIVE_FIXED_VALUE",
                                        message=f"Negative fixed value for {mod_key}: {mod_value}€",
                                        field=mod_key,
                                        value=mod_value))

            # Validate VAT rate if present
            if "vat_rate" in calculation_data:
                vat_rate = calculation_data["vat_rate"]
                if not isinstance(vat_rate, (int, float)):
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.CALCULATION,
                        code="INVALID_VAT_RATE_TYPE",
                        message="VAT rate must be numeric",
                        field="vat_rate",
                        value=type(vat_rate).__name__
                    ))
                elif vat_rate < 0:  # Negative VAT is an error
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.CALCULATION,
                        code="NEGATIVE_VAT_RATE",
                        message=f"VAT rate cannot be negative: {vat_rate}%",
                        field="vat_rate",
                        value=vat_rate,
                        suggestion="VAT rate must be 0 or positive"
                    ))
                elif vat_rate > 50:  # Very high VAT is a warning
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.CALCULATION,
                        code="UNUSUAL_VAT_RATE",
                        message=f"Unusual VAT rate: {vat_rate}%",
                        field="vat_rate",
                        value=vat_rate,
                        suggestion="Verify VAT rate is correct"
                    ))

            # Business rule validations
            self._validate_business_rules(calculation_data, result)

            return result

        except Exception as e:
            self.logger.error(
                f"Error validating pricing calculation data: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.CALCULATION,
                code="VALIDATION_ERROR",
                message=f"Calculation validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def validate_final_pricing_result(
            self, pricing_result: dict[str, Any]) -> ValidationResult:
        """Validate final pricing calculation result

        Args:
            pricing_result: Final pricing result to validate

        Returns:
            ValidationResult with validation issues
        """
        result = ValidationResult(is_valid=True)

        try:
            # Check for required result fields
            required_fields = [
                "final_price_net",
                "final_price_gross",
                "base_price"]
            self._validate_required_fields(
                pricing_result,
                required_fields,
                result,
                ValidationCategory.CALCULATION
            )

            # Validate price consistency
            if all(
                field in pricing_result for field in [
                    "final_price_net",
                    "final_price_gross",
                    "vat_amount"]):
                net = pricing_result["final_price_net"]
                gross = pricing_result["final_price_gross"]
                vat = pricing_result.get("vat_amount", 0)

                expected_gross = net + vat
                if abs(
                        gross -
                        expected_gross) > 0.01:  # Allow for rounding differences
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.CALCULATION,
                            code="PRICE_CONSISTENCY_ERROR",
                            message=f"Price consistency error: net ({net}) + VAT ({vat}) ≠ gross ({gross})",
                            context={
                                "net_price": net,
                                "vat_amount": vat,
                                "gross_price": gross,
                                "expected_gross": expected_gross}))

            # Validate price ranges
            for price_field in [
                "base_price",
                "final_price_net",
                    "final_price_gross"]:
                if price_field in pricing_result:
                    price = pricing_result[price_field]
                    if not isinstance(price, (int, float)):
                        result.add_issue(
                            ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category=ValidationCategory.CALCULATION,
                                code="INVALID_PRICE_TYPE",
                                message=f"{price_field} must be numeric, got: {
                                    type(price).__name__}",
                                field=price_field,
                                value=price))
                    elif price < 0:
                        result.add_issue(
                            ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                category=ValidationCategory.CALCULATION,
                                code="NEGATIVE_PRICE",
                                message=f"Negative price not allowed: {price_field} = {price}",
                                field=price_field,
                                value=price))
                    elif price > self.rules["max_price"]:
                        result.add_issue(
                            ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                category=ValidationCategory.CALCULATION,
                                code="HIGH_PRICE",
                                message=f"Unusually high price: {price_field} = {price}€",
                                field=price_field,
                                value=price,
                                suggestion="Verify calculation is correct"))

            # Validate discount/surcharge totals
            if "total_discounts" in pricing_result and "total_surcharges" in pricing_result:
                discounts = pricing_result["total_discounts"]
                surcharges = pricing_result["total_surcharges"]

                if discounts < 0:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.CALCULATION,
                            code="NEGATIVE_TOTAL_DISCOUNTS",
                            message=f"Total discounts cannot be negative: {discounts}",
                            field="total_discounts",
                            value=discounts))

                if surcharges < 0:
                    result.add_issue(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.CALCULATION,
                            code="NEGATIVE_TOTAL_SURCHARGES",
                            message=f"Total surcharges cannot be negative: {surcharges}",
                            field="total_surcharges",
                            value=surcharges))

            return result

        except Exception as e:
            self.logger.error(f"Error validating final pricing result: {e}")
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.CALCULATION,
                code="VALIDATION_ERROR",
                message=f"Result validation error: {str(e)}",
                context={"exception": str(e)}
            ))
            return result

    def _validate_required_fields(self,
                                  data: dict[str,
                                             Any],
                                  required_fields: list[str],
                                  result: ValidationResult,
                                  category: ValidationCategory):
        """Validate required fields are present"""
        for field in required_fields:
            if field not in data:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=category,
                    code="MISSING_REQUIRED_FIELD",
                    message=f"Required field missing: {field}",
                    field=field,
                    suggestion=f"Add required field: {field}"
                ))
            elif data[field] is None:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=category,
                    code="NULL_REQUIRED_FIELD",
                    message=f"Required field cannot be null: {field}",
                    field=field,
                    value=None
                ))

    def _validate_price_value(
            self,
            price: Any,
            field_name: str,
            result: ValidationResult):
        """Validate a price value"""
        if not isinstance(price, (int, float)):
            result.add_issue(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.PRICING,
                    code="INVALID_PRICE_TYPE",
                    message=f"{field_name} must be numeric, got: {
                        type(price).__name__}",
                    field=field_name,
                    value=price))
        elif price < self.rules["min_price"]:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.PRICING,
                code="NEGATIVE_PRICE",
                message=f"{field_name} cannot be negative: {price}",
                field=field_name,
                value=price
            ))
        elif price > self.rules["max_price"]:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PRICING,
                code="HIGH_PRICE",
                message=f"Unusually high price for {field_name}: {price}€",
                field=field_name,
                value=price,
                suggestion="Verify price is correct"
            ))

    def _validate_technical_specs(
            self, product_data: dict[str, Any], result: ValidationResult):
        """Validate technical specifications"""
        # Validate capacity_w
        if "capacity_w" in product_data and product_data["capacity_w"] is not None:
            capacity = product_data["capacity_w"]
            if not isinstance(capacity, (int, float)) or capacity <= 0:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPONENT,
                    code="INVALID_CAPACITY",
                    message=f"Invalid capacity_w: {capacity}",
                    field="capacity_w",
                    value=capacity
                ))

        # Validate efficiency_percent
        if "efficiency_percent" in product_data and product_data["efficiency_percent"] is not None:
            efficiency = product_data["efficiency_percent"]
            if not isinstance(efficiency, (int, float)
                              ) or efficiency <= 0 or efficiency > 100:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPONENT,
                    code="INVALID_EFFICIENCY",
                    message=f"Invalid efficiency_percent: {efficiency}%",
                    field="efficiency_percent",
                    value=efficiency,
                    suggestion="Efficiency should be between 0% and 100%"
                ))

        # Validate warranty_years
        if "warranty_years" in product_data and product_data["warranty_years"] is not None:
            warranty = product_data["warranty_years"]
            if not isinstance(warranty, (int, float)
                              ) or warranty < 0 or warranty > 50:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.COMPONENT,
                    code="UNUSUAL_WARRANTY",
                    message=f"Unusual warranty period: {warranty} years",
                    field="warranty_years",
                    value=warranty,
                    suggestion="Verify warranty period is correct"
                ))

    def _validate_business_rules(
            self, calculation_data: dict[str, Any], result: ValidationResult):
        """Validate business rules"""
        # Rule: PV systems should have at least modules and inverter
        components = calculation_data.get("components", [])
        if components:
            categories = [
                comp.get(
                    "category",
                    "") for comp in components if isinstance(
                    comp,
                    dict)]

            # Check for PV system completeness
            has_modules = any("modul" in cat.lower() for cat in categories)
            has_inverter = any("wechselrichter" in cat.lower(
            ) or "inverter" in cat.lower() for cat in categories)

            if has_modules and not has_inverter:
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BUSINESS_RULE,
                        code="INCOMPLETE_PV_SYSTEM",
                        message="PV system has modules but no inverter",
                        suggestion="Consider adding an inverter to complete the system"))
            elif has_inverter and not has_modules:
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BUSINESS_RULE,
                        code="INCOMPLETE_PV_SYSTEM",
                        message="PV system has inverter but no modules",
                        suggestion="Consider adding PV modules to complete the system"))

        # Rule: Check for reasonable system sizes
        total_capacity = 0
        for comp in components:
            if isinstance(comp, dict) and "capacity_w" in comp:
                capacity = comp.get("capacity_w", 0)
                quantity = comp.get("quantity", 1)
                if isinstance(
                        capacity, (int, float)) and isinstance(
                        quantity, (int, float)):
                    total_capacity += capacity * quantity

        if total_capacity > 0:
            if total_capacity < 1000:  # Less than 1kW
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.BUSINESS_RULE,
                    code="SMALL_SYSTEM_SIZE",
                    message=f"Small system capacity: {total_capacity}W",
                    suggestion="Verify system size is correct"
                ))
            elif total_capacity > 100000:  # More than 100kW
                result.add_issue(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BUSINESS_RULE,
                        code="LARGE_SYSTEM_SIZE",
                        message=f"Large system capacity: {total_capacity}W",
                        suggestion="Verify system size is correct for residential/commercial use"))

    def get_validation_rules(self) -> dict[str, Any]:
        """Get current validation rules configuration

        Returns:
            Dictionary with validation rules
        """
        return self.rules.copy()

    def update_validation_rules(self, new_rules: dict[str, Any]) -> bool:
        """Update validation rules configuration

        Args:
            new_rules: New rules to update

        Returns:
            True if successful, False otherwise
        """
        try:
            self.rules.update(new_rules)
            self.logger.info(
                f"Updated validation rules: {
                    list(
                        new_rules.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating validation rules: {e}")
            return False


# Global validator instance
_validator_instance = None


def get_pricing_validator() -> PricingValidator:
    """Get global pricing validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = PricingValidator()
    return _validator_instance
