"""Widget Validation Engine

This module provides real-time validation with configurable rules, field-level error
messages, and validation state persistence across page navigation.

Key Features:
- Real-time validation with configurable rules
- Field-level error and warning messages
- Validation state persistence
- Validation recovery after form restoration
- Built-in validators for common use cases
"""

import re
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class ValidationRule:
    """Base validation rule"""

    def __init__(self, error_message: str = None, warning_message: str = None):
        self.error_message = error_message
        self.warning_message = warning_message

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        """
        Validate value

        Returns:
            Tuple of (is_valid, error_message, warning_message)
        """
        raise NotImplementedError


class RequiredRule(ValidationRule):
    """Value is required"""

    def __init__(self, error_message: str = "This field is required"):
        super().__init__(error_message=error_message)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None or value == "" or (
                isinstance(value, (list, dict)) and len(value) == 0):
            return False, self.error_message, None
        return True, None, None


class MinLengthRule(ValidationRule):
    """Minimum string length"""

    def __init__(self, min_length: int, error_message: str = None):
        self.min_length = min_length
        error_msg = error_message or f"Must be at least {min_length} characters"
        super().__init__(error_message=error_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        if len(str(value)) < self.min_length:
            return False, self.error_message, None
        return True, None, None


class MaxLengthRule(ValidationRule):
    """Maximum string length"""

    def __init__(
            self,
            max_length: int,
            error_message: str = None,
            warning_threshold: float = 0.9):
        self.max_length = max_length
        self.warning_threshold = warning_threshold
        error_msg = error_message or f"Must be at most {max_length} characters"
        warning_msg = f"Approaching character limit ({max_length})"
        super().__init__(error_message=error_msg, warning_message=warning_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        length = len(str(value))

        if length > self.max_length:
            return False, self.error_message, None

        if length >= self.max_length * self.warning_threshold:
            return True, None, self.warning_message

        return True, None, None


class MinValueRule(ValidationRule):
    """Minimum numeric value"""

    def __init__(self, min_value: int | float, error_message: str = None):
        self.min_value = min_value
        error_msg = error_message or f"Must be at least {min_value}"
        super().__init__(error_message=error_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        try:
            if float(value) < self.min_value:
                return False, self.error_message, None
        except (ValueError, TypeError):
            return False, "Must be a valid number", None

        return True, None, None


class MaxValueRule(ValidationRule):
    """Maximum numeric value"""

    def __init__(self, max_value: int | float, error_message: str = None):
        self.max_value = max_value
        error_msg = error_message or f"Must be at most {max_value}"
        super().__init__(error_message=error_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        try:
            if float(value) > self.max_value:
                return False, self.error_message, None
        except (ValueError, TypeError):
            return False, "Must be a valid number", None

        return True, None, None


class RangeRule(ValidationRule):
    """Value within range"""

    def __init__(
        self,
        min_value: int | float,
        max_value: int | float,
        error_message: str = None
    ):
        self.min_value = min_value
        self.max_value = max_value
        error_msg = error_message or f"Must be between {min_value} and {max_value}"
        super().__init__(error_message=error_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        try:
            num_value = float(value)
            if num_value < self.min_value or num_value > self.max_value:
                return False, self.error_message, None
        except (ValueError, TypeError):
            return False, "Must be a valid number", None

        return True, None, None


class PatternRule(ValidationRule):
    """Regex pattern matching"""

    def __init__(self, pattern: str, error_message: str = "Invalid format"):
        self.pattern = re.compile(pattern)
        super().__init__(error_message=error_message)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None or value == "":
            return True, None, None

        if not self.pattern.match(str(value)):
            return False, self.error_message, None

        return True, None, None


class EmailRule(PatternRule):
    """Email validation"""

    def __init__(self, error_message: str = "Invalid email address"):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern=pattern, error_message=error_message)


class URLRule(PatternRule):
    """URL validation"""

    def __init__(self, error_message: str = "Invalid URL"):
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        super().__init__(pattern=pattern, error_message=error_message)


class PhoneRule(PatternRule):
    """Phone number validation"""

    def __init__(self, error_message: str = "Invalid phone number"):
        # Simple pattern, adjust based on requirements
        pattern = r'^\+?[\d\s\-\(\)]+$'
        super().__init__(pattern=pattern, error_message=error_message)


class DateRangeRule(ValidationRule):
    """Date within range"""

    def __init__(
        self,
        min_date: date | None = None,
        max_date: date | None = None,
        error_message: str = None
    ):
        self.min_date = min_date
        self.max_date = max_date

        if error_message:
            error_msg = error_message
        elif min_date and max_date:
            error_msg = f"Date must be between {min_date} and {max_date}"
        elif min_date:
            error_msg = f"Date must be after {min_date}"
        elif max_date:
            error_msg = f"Date must be before {max_date}"
        else:
            error_msg = "Invalid date"

        super().__init__(error_message=error_msg)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        if value is None:
            return True, None, None

        try:
            if isinstance(value, str):
                value = datetime.fromisoformat(value).date()
            elif isinstance(value, datetime):
                value = value.date()

            if self.min_date and value < self.min_date:
                return False, self.error_message, None

            if self.max_date and value > self.max_date:
                return False, self.error_message, None
        except (ValueError, TypeError):
            return False, "Invalid date format", None

        return True, None, None


class CustomRule(ValidationRule):
    """Custom validation function"""

    def __init__(
        self,
        validator_fn: Callable[[Any], bool],
        error_message: str = "Validation failed"
    ):
        self.validator_fn = validator_fn
        super().__init__(error_message=error_message)

    def validate(self, value: Any) -> tuple[bool, str | None, str | None]:
        try:
            if self.validator_fn(value):
                return True, None, None
            return False, self.error_message, None
        except Exception as e:
            logger.error("Custom validation failed", error=str(e))
            return False, f"Validation error: {str(e)}", None


class Validator:
    """Validator with multiple rules"""

    def __init__(self, rules: list[ValidationRule] = None):
        self.rules = rules or []

    def add_rule(self, rule: ValidationRule) -> 'Validator':
        """Add validation rule"""
        self.rules.append(rule)
        return self

    def validate(self, value: Any) -> tuple[bool, list[str], list[str]]:
        """
        Validate value against all rules

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        is_valid = True

        for rule in self.rules:
            valid, error, warning = rule.validate(value)

            if not valid:
                is_valid = False
                if error:
                    errors.append(error)

            if warning:
                warnings.append(warning)

        return is_valid, errors, warnings

    def __call__(self, value: Any) -> tuple[bool, list[str], list[str]]:
        """Allow validator to be called as function"""
        return self.validate(value)


class ValidationEngine:
    """Central validation engine for managing validators"""

    def __init__(self):
        self._validators: dict[str, Validator] = {}

    def register_validator(self, key: str, validator: Validator) -> None:
        """Register validator for widget key"""
        self._validators[key] = validator

    def unregister_validator(self, key: str) -> None:
        """Unregister validator"""
        self._validators.pop(key, None)

    def get_validator(self, key: str) -> Validator | None:
        """Get validator for widget key"""
        return self._validators.get(key)

    def validate(self,
                 key: str,
                 value: Any) -> tuple[bool,
                                      list[str],
                                      list[str]]:
        """Validate value for widget key"""
        validator = self.get_validator(key)

        if validator:
            return validator.validate(value)

        # No validator registered, consider valid
        return True, [], []

    def validate_all(self,
                     values: dict[str,
                                  Any]) -> dict[str,
                                                tuple[bool,
                                                      list[str],
                                                      list[str]]]:
        """Validate multiple values"""
        results = {}

        for key, value in values.items():
            results[key] = self.validate(key, value)

        return results

    def is_all_valid(self, values: dict[str, Any]) -> bool:
        """Check if all values are valid"""
        results = self.validate_all(values)
        return all(is_valid for is_valid, _, _ in results.values())


# Global validation engine
_validation_engine = ValidationEngine()


def get_validation_engine() -> ValidationEngine:
    """Get global validation engine"""
    return _validation_engine


# Convenience functions

def register_validator(key: str, validator: Validator) -> None:
    """Register validator for widget key"""
    engine = get_validation_engine()
    engine.register_validator(key, validator)


def validate_widget(key: str, value: Any) -> tuple[bool, list[str], list[str]]:
    """Validate widget value"""
    engine = get_validation_engine()
    return engine.validate(key, value)


# Common validator builders

def required_text(min_length: int = None, max_length: int = None) -> Validator:
    """Create validator for required text"""
    validator = Validator([RequiredRule()])

    if min_length:
        validator.add_rule(MinLengthRule(min_length))

    if max_length:
        validator.add_rule(MaxLengthRule(max_length))

    return validator


def required_number(min_value: int | float = None,
                    max_value: int | float = None) -> Validator:
    """Create validator for required number"""
    validator = Validator([RequiredRule()])

    if min_value is not None and max_value is not None:
        validator.add_rule(RangeRule(min_value, max_value))
    elif min_value is not None:
        validator.add_rule(MinValueRule(min_value))
    elif max_value is not None:
        validator.add_rule(MaxValueRule(max_value))

    return validator


def required_email() -> Validator:
    """Create validator for required email"""
    return Validator([RequiredRule(), EmailRule()])


def required_url() -> Validator:
    """Create validator for required URL"""
    return Validator([RequiredRule(), URLRule()])


def required_phone() -> Validator:
    """Create validator for required phone"""
    return Validator([RequiredRule(), PhoneRule()])


def required_date(min_date: date = None, max_date: date = None) -> Validator:
    """Create validator for required date"""
    validator = Validator([RequiredRule()])

    if min_date or max_date:
        validator.add_rule(DateRangeRule(min_date, max_date))

    return validator


def optional_text(min_length: int = None, max_length: int = None) -> Validator:
    """Create validator for optional text"""
    validator = Validator()

    if min_length:
        validator.add_rule(MinLengthRule(min_length))

    if max_length:
        validator.add_rule(MaxLengthRule(max_length))

    return validator


def optional_number(min_value: int | float = None,
                    max_value: int | float = None) -> Validator:
    """Create validator for optional number"""
    validator = Validator()

    if min_value is not None and max_value is not None:
        validator.add_rule(RangeRule(min_value, max_value))
    elif min_value is not None:
        validator.add_rule(MinValueRule(min_value))
    elif max_value is not None:
        validator.add_rule(MaxValueRule(max_value))

    return validator
