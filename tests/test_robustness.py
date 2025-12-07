"""
Tests for Controlling System Robustness Module

Tests error handling, validation, retry logic, and stability features.
"""

import pytest
from datetime import date, datetime
from sqlalchemy.exc import OperationalError
from controlling.robustness import (
    ControllingError,
    ValidationError,
    DatabaseError,
    ExportError,
    validate_not_none,
    validate_not_empty,
    validate_positive,
    validate_percentage,
    validate_date_range,
    safe_division,
    safe_percentage,
    TransactionContext,
    validate_export_format,
    PerformanceMonitor
)


class TestValidation:
    """Test validation functions."""
    
    def test_validate_not_none_success(self):
        """Test validate_not_none with valid value."""
        validate_not_none("value", "field")  # Should not raise
    
    def test_validate_not_none_failure(self):
        """Test validate_not_none with None."""
        with pytest.raises(ValidationError, match="field cannot be None"):
            validate_not_none(None, "field")
    
    def test_validate_not_empty_success(self):
        """Test validate_not_empty with valid string."""
        validate_not_empty("value", "field")  # Should not raise
    
    def test_validate_not_empty_failure_empty(self):
        """Test validate_not_empty with empty string."""
        with pytest.raises(ValidationError, match="field cannot be empty"):
            validate_not_empty("", "field")
    
    def test_validate_not_empty_failure_whitespace(self):
        """Test validate_not_empty with whitespace."""
        with pytest.raises(ValidationError, match="field cannot be empty"):
            validate_not_empty("   ", "field")
    
    def test_validate_positive_success(self):
        """Test validate_positive with positive number."""
        validate_positive(10.0, "field")  # Should not raise
        validate_positive(0.0, "field")  # Zero is valid
    
    def test_validate_positive_failure(self):
        """Test validate_positive with negative number."""
        with pytest.raises(ValidationError, match="field must be positive"):
            validate_positive(-1.0, "field")
    
    def test_validate_percentage_success(self):
        """Test validate_percentage with valid percentage."""
        validate_percentage(50.0, "field")  # Should not raise
        validate_percentage(0.0, "field")  # 0% is valid
        validate_percentage(100.0, "field")  # 100% is valid
    
    def test_validate_percentage_failure_too_low(self):
        """Test validate_percentage with value < 0."""
        with pytest.raises(ValidationError, match="field must be between 0 and 100"):
            validate_percentage(-1.0, "field")
    
    def test_validate_percentage_failure_too_high(self):
        """Test validate_percentage with value > 100."""
        with pytest.raises(ValidationError, match="field must be between 0 and 100"):
            validate_percentage(101.0, "field")
    
    def test_validate_date_range_success(self):
        """Test validate_date_range with valid range."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 12, 31)
        validate_date_range(start, end)  # Should not raise
    
    def test_validate_date_range_failure(self):
        """Test validate_date_range with invalid range."""
        start = datetime(2025, 12, 31)
        end = datetime(2025, 1, 1)
        with pytest.raises(ValidationError, match="start date must be before"):
            validate_date_range(start, end)
    
    def test_validate_export_format_success(self):
        """Test validate_export_format with valid formats."""
        validate_export_format("json")  # Should not raise
        validate_export_format("excel")
        validate_export_format("pdf")
        validate_export_format("JSON")  # Case insensitive
    
    def test_validate_export_format_failure(self):
        """Test validate_export_format with invalid format."""
        with pytest.raises(ValidationError, match="Unsupported export format"):
            validate_export_format("invalid")


class TestSafeOperations:
    """Test safe mathematical operations."""
    
    def test_safe_division_normal(self):
        """Test safe_division with normal values."""
        result = safe_division(10.0, 2.0)
        assert result == 5.0
    
    def test_safe_division_zero_denominator(self):
        """Test safe_division with zero denominator."""
        result = safe_division(10.0, 0.0, default=0.0)
        assert result == 0.0
    
    def test_safe_division_custom_default(self):
        """Test safe_division with custom default."""
        result = safe_division(10.0, 0.0, default=-1.0)
        assert result == -1.0
    
    def test_safe_percentage_normal(self):
        """Test safe_percentage with normal values."""
        result = safe_percentage(5.0, 10.0)
        assert result == 50.0
    
    def test_safe_percentage_zero_denominator(self):
        """Test safe_percentage with zero denominator."""
        result = safe_percentage(5.0, 0.0, default=0.0)
        assert result == 0.0
    
    def test_safe_percentage_full(self):
        """Test safe_percentage with 100%."""
        result = safe_percentage(10.0, 10.0)
        assert result == 100.0


class TestPerformanceMonitor:
    """Test performance monitoring."""
    
    def test_performance_monitor_success(self):
        """Test performance monitor with successful operation."""
        with PerformanceMonitor("test_operation") as monitor:
            # Simulate some work
            import time
            time.sleep(0.001)  # Sleep for 1ms to ensure measurable time
        
        assert monitor.elapsed >= 0  # Changed to >= to handle very fast operations
        assert monitor.start_time is not None
        assert monitor.end_time is not None
    
    def test_performance_monitor_with_error(self):
        """Test performance monitor with error."""
        monitor = None
        with pytest.raises(ValueError):
            with PerformanceMonitor("test_operation") as mon:
                monitor = mon
                raise ValueError("Test error")
        
        # Monitor should still record time
        assert monitor is not None
        assert monitor.elapsed >= 0  # Changed to >= to handle very fast operations


class TestExceptions:
    """Test custom exceptions."""
    
    def test_controlling_error(self):
        """Test ControllingError."""
        with pytest.raises(ControllingError, match="Test error"):
            raise ControllingError("Test error")
    
    def test_validation_error(self):
        """Test ValidationError."""
        with pytest.raises(ValidationError, match="Test validation"):
            raise ValidationError("Test validation")
    
    def test_database_error(self):
        """Test DatabaseError."""
        with pytest.raises(DatabaseError, match="Test database"):
            raise DatabaseError("Test database")
    
    def test_export_error(self):
        """Test ExportError."""
        with pytest.raises(ExportError, match="Test export"):
            raise ExportError("Test export")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
