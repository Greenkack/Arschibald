"""Pricing Error Handling

Comprehensive error handling classes and exceptions for the pricing system.
Provides structured error handling with detailed context and recovery suggestions.
"""

from __future__ import annotations

import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class PricingError(Exception):
    """Base class for pricing-related errors"""

    def __init__(self,
                 message: str,
                 error_code: str = None,
                 context: dict[str,
                               Any] = None,
                 suggestion: str = None,
                 original_exception: Exception = None):
        """Initialize pricing error

        Args:
            message: Error message
            error_code: Unique error code for categorization
            context: Additional context information
            suggestion: Suggested resolution
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.suggestion = suggestion
        self.original_exception = original_exception
        self.timestamp = datetime.now()

        # Log the error
        logger.error(f"PricingError [{self.error_code}]: {message}", extra={
                     "context": self.context, "suggestion": self.suggestion})

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "suggestion": self.suggestion,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": str(
                self.original_exception) if self.original_exception else None}


class ValidationError(PricingError):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: str = None, value: Any = None,
                 validation_issues: list[dict[str, Any]] = None, **kwargs):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = value
        if validation_issues:
            context["validation_issues"] = validation_issues

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            suggestion=kwargs.get("suggestion", "Check input data and fix validation issues"),
            **{k: v for k, v in kwargs.items() if k not in ["context", "suggestion"]}
        )


class ComponentError(PricingError):
    """Raised when component data is invalid or missing"""

    def __init__(
            self,
            message: str,
            component_id: int = None,
            product_id: int = None,
            **kwargs):
        context = kwargs.get("context", {})
        if component_id is not None:
            context["component_id"] = component_id
        if product_id is not None:
            context["product_id"] = product_id

        super().__init__(
            message=message,
            error_code="COMPONENT_ERROR",
            context=context,
            suggestion=kwargs.get("suggestion", "Verify component configuration and product data"),
            **{k: v for k, v in kwargs.items() if k not in ["context", "suggestion"]}
        )


class ProductNotFoundError(ComponentError):
    """Raised when a product is not found in the database"""

    def __init__(self, product_identifier: int | str, **kwargs):
        message = f"Product not found: {product_identifier}"
        context = kwargs.get("context", {})
        context["product_identifier"] = product_identifier

        # Remove conflicting kwargs
        filtered_kwargs = {
            k: v for k,
            v in kwargs.items() if k not in [
                "context",
                "suggestion",
                "error_code"]}

        super().__init__(
            message=message,
            context=context,
            suggestion="Verify product ID exists in database or check product name spelling",
            **filtered_kwargs)

        # Override error code after initialization
        self.error_code = "PRODUCT_NOT_FOUND"


class MarginCalculationError(PricingError):
    """Raised when margin calculation fails"""

    def __init__(self, message: str, margin_config: dict[str, Any] = None,
                 purchase_price: float = None, **kwargs):
        context = kwargs.get("context", {})
        if margin_config:
            context["margin_config"] = margin_config
        if purchase_price is not None:
            context["purchase_price"] = purchase_price

        super().__init__(message=message,
                         error_code="MARGIN_CALCULATION_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Check margin configuration and purchase price values"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


class PriceMatrixError(PricingError):
    """Raised when price matrix lookup fails"""

    def __init__(self, message: str, lookup_key: str = None, **kwargs):
        context = kwargs.get("context", {})
        if lookup_key:
            context["lookup_key"] = lookup_key

        super().__init__(message=message,
                         error_code="PRICE_MATRIX_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Verify price matrix configuration and lookup parameters"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


class ModificationError(PricingError):
    """Raised when discount/surcharge modification fails"""

    def __init__(self, message: str, modification_type: str = None,
                 modification_config: dict[str, Any] = None, **kwargs):
        context = kwargs.get("context", {})
        if modification_type:
            context["modification_type"] = modification_type
        if modification_config:
            context["modification_config"] = modification_config

        super().__init__(message=message,
                         error_code="MODIFICATION_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Check modification configuration and application conditions"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


class CalculationError(PricingError):
    """Raised when pricing calculation fails"""

    def __init__(self, message: str, calculation_step: str = None,
                 calculation_data: dict[str, Any] = None, **kwargs):
        context = kwargs.get("context", {})
        if calculation_step:
            context["calculation_step"] = calculation_step
        if calculation_data:
            # Only include safe data to avoid circular references
            safe_data = {k: v for k, v in calculation_data.items()
                         if isinstance(v, (str, int, float, bool, type(None)))}
            context["calculation_data"] = safe_data

        super().__init__(message=message,
                         error_code="CALCULATION_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Check calculation inputs and verify all required data is present"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


class DynamicKeyError(PricingError):
    """Raised when dynamic key generation fails"""

    def __init__(
            self,
            message: str,
            key_name: str = None,
            key_value: Any = None,
            **kwargs):
        context = kwargs.get("context", {})
        if key_name:
            context["key_name"] = key_name
        if key_value is not None:
            context["key_value"] = key_value

        super().__init__(
            message=message,
            error_code="DYNAMIC_KEY_ERROR",
            context=context,
            suggestion=kwargs.get("suggestion", "Check key naming conventions and value types"),
            **{k: v for k, v in kwargs.items() if k not in ["context", "suggestion"]}
        )


class DatabaseError(PricingError):
    """Raised when database operations fail"""

    def __init__(
            self,
            message: str,
            operation: str = None,
            table: str = None,
            **kwargs):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        if table:
            context["table"] = table

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            context=context,
            suggestion=kwargs.get("suggestion", "Check database connection and data integrity"),
            **{k: v for k, v in kwargs.items() if k not in ["context", "suggestion"]}
        )


class CacheError(PricingError):
    """Raised when cache operations fail"""

    def __init__(
            self,
            message: str,
            cache_key: str = None,
            operation: str = None,
            **kwargs):
        context = kwargs.get("context", {})
        if cache_key:
            context["cache_key"] = cache_key
        if operation:
            context["operation"] = operation

        super().__init__(message=message,
                         error_code="CACHE_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Cache error is non-critical, operation will continue without caching"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


class BusinessRuleError(PricingError):
    """Raised when business rules are violated"""

    def __init__(self, message: str, rule_name: str = None,
                 rule_context: dict[str, Any] = None, **kwargs):
        context = kwargs.get("context", {})
        if rule_name:
            context["rule_name"] = rule_name
        if rule_context:
            context["rule_context"] = rule_context

        super().__init__(message=message,
                         error_code="BUSINESS_RULE_ERROR",
                         context=context,
                         suggestion=kwargs.get("suggestion",
                                               "Review business rules and adjust configuration or inputs"),
                         **{k: v for k,
                             v in kwargs.items() if k not in ["context",
                                                              "suggestion"]})


@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    component: str
    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    additional_data: dict[str, Any] | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PricingErrorHandler:
    """Centralized error handling for pricing operations"""

    def __init__(self):
        """Initialize error handler"""
        self.logger = logging.getLogger(f"{__name__}.PricingErrorHandler")
        self.error_history: list[dict[str, Any]] = []
        self.max_history_size = 1000

    def handle_error(self, error: Exception, context: ErrorContext = None,
                     reraise: bool = True) -> dict[str, Any] | None:
        """Handle and log pricing errors

        Args:
            error: Exception to handle
            context: Error context information
            reraise: Whether to reraise the exception

        Returns:
            Error information dictionary if not reraising
        """
        try:
            # Create error info
            error_info = self._create_error_info(error, context)

            # Log error
            self._log_error(error_info)

            # Store in history
            self._store_error_history(error_info)

            # Handle specific error types
            if isinstance(error, ValidationError):
                self._handle_validation_error(error, context)
            elif isinstance(error, ComponentError):
                self._handle_component_error(error, context)
            elif isinstance(error, DatabaseError):
                self._handle_database_error(error, context)
            elif isinstance(error, CacheError):
                self._handle_cache_error(error, context)
            else:
                self._handle_generic_error(error, context)

            if reraise:
                raise error
            return error_info

        except Exception as handler_error:
            self.logger.error(f"Error in error handler: {handler_error}")
            if reraise:
                raise error
            return {
                "error": "Error handler failed",
                "original_error": str(error)}

    def _create_error_info(self, error: Exception,
                           context: ErrorContext = None) -> dict[str, Any]:
        """Create comprehensive error information"""
        error_info = {
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }

        # Add PricingError specific information
        if isinstance(error, PricingError):
            error_info.update(error.to_dict())

        # Add context information
        if context:
            error_info["context"] = {
                "operation": context.operation,
                "component": context.component,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "request_id": context.request_id,
                "additional_data": context.additional_data,
                "context_timestamp": context.timestamp.isoformat()
            }

        return error_info

    def _log_error(self, error_info: dict[str, Any]):
        """Log error with appropriate level"""
        error_type = error_info.get("error_type", "Unknown")
        message = error_info.get("message", "No message")

        # Determine log level based on error type
        if error_type in ["ValidationError", "ComponentError"]:
            self.logger.warning(
                f"{error_type}: {message}", extra={
                    "error_info": error_info})
        elif error_type in ["CacheError"]:
            self.logger.info(
                f"{error_type}: {message}", extra={
                    "error_info": error_info})
        else:
            self.logger.error(
                f"{error_type}: {message}", extra={
                    "error_info": error_info})

    def _store_error_history(self, error_info: dict[str, Any]):
        """Store error in history for analysis"""
        self.error_history.append(error_info)

        # Trim history if too large
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]

    def _handle_validation_error(
            self,
            error: ValidationError,
            context: ErrorContext = None):
        """Handle validation errors with specific recovery strategies"""
        self.logger.info(f"Handling validation error: {error.message}")

        # Could implement automatic data correction here
        # For now, just log the validation issues
        if "validation_issues" in error.context:
            issues = error.context["validation_issues"]
            self.logger.info(f"Validation issues count: {len(issues)}")

    def _handle_component_error(
            self,
            error: ComponentError,
            context: ErrorContext = None):
        """Handle component errors with fallback strategies"""
        self.logger.info(f"Handling component error: {error.message}")

        # Could implement component fallback strategies here
        if isinstance(error, ProductNotFoundError):
            self.logger.info(
                "Product not found - could suggest similar products")

    def _handle_database_error(
            self,
            error: DatabaseError,
            context: ErrorContext = None):
        """Handle database errors with retry strategies"""
        self.logger.warning(f"Handling database error: {error.message}")

        # Could implement retry logic or fallback to cached data
        operation = error.context.get("operation", "unknown")
        self.logger.info(f"Database operation failed: {operation}")

    def _handle_cache_error(
            self,
            error: CacheError,
            context: ErrorContext = None):
        """Handle cache errors (non-critical)"""
        self.logger.debug(f"Cache error (non-critical): {error.message}")

        # Cache errors are typically non-critical
        # Operation should continue without caching

    def _handle_generic_error(
            self,
            error: Exception,
            context: ErrorContext = None):
        """Handle generic errors"""
        self.logger.error(f"Handling generic error: {error}")

        # Generic error handling
        if context:
            self.logger.error(
                f"Error in {
                    context.operation} ({
                    context.component})")

    def get_error_statistics(self) -> dict[str, Any]:
        """Get error statistics for monitoring"""
        if not self.error_history:
            return {"total_errors": 0}

        # Count errors by type
        error_counts = {}
        recent_errors = []
        now = datetime.now()

        for error_info in self.error_history:
            error_type = error_info.get("error_type", "Unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

            # Check if error is recent (last hour)
            try:
                error_time = datetime.fromisoformat(error_info["timestamp"])
                if (now - error_time).total_seconds() < 3600:  # 1 hour
                    recent_errors.append(error_info)
            except (KeyError, ValueError):
                pass

        return {
            "total_errors": len(
                self.error_history),
            "error_counts_by_type": error_counts,
            "recent_errors_count": len(recent_errors),
            "most_common_error": max(
                error_counts.items(),
                key=lambda x: x[1])[0] if error_counts else None}

    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.logger.info("Error history cleared")

    def get_recent_errors(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent errors within specified hours

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent error information
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = []

        for error_info in self.error_history:
            try:
                error_time = datetime.fromisoformat(error_info["timestamp"])
                if error_time >= cutoff_time:
                    recent_errors.append(error_info)
            except (KeyError, ValueError):
                continue

        return recent_errors


# Global error handler instance
_error_handler_instance = None


def get_error_handler() -> PricingErrorHandler:
    """Get global error handler instance"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = PricingErrorHandler()
    return _error_handler_instance


def handle_pricing_error(error: Exception, operation: str = "unknown",
                         component: str = "pricing", **context_data) -> None:
    """Convenience function to handle pricing errors

    Args:
        error: Exception to handle
        operation: Operation that caused the error
        component: Component where error occurred
        **context_data: Additional context data
    """
    context = ErrorContext(
        operation=operation,
        component=component,
        additional_data=context_data
    )

    error_handler = get_error_handler()
    error_handler.handle_error(error, context, reraise=True)


def safe_pricing_operation(
        operation_name: str,
        component_name: str = "pricing"):
    """Decorator for safe pricing operations with error handling

    Args:
        operation_name: Name of the operation
        component_name: Name of the component
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=operation_name,
                    component=component_name,
                    additional_data={
                        "args_count": len(args),
                        "kwargs_keys": list(
                            kwargs.keys())})

                error_handler = get_error_handler()
                error_handler.handle_error(e, context, reraise=True)

        return wrapper
    return decorator
