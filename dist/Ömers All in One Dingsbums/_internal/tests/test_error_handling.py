"""
Unit Tests for Error Handling System

Tests for:
- Exception hierarchy
- Error handler functionality
- Fallback mechanisms
- Automatic recovery
- Error reporting
"""

import pytest
import json
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import components to test
from theming.theme_errors import (
    ThemeError,
    ThemeLoadError,
    ThemeValidationError,
    ThemeNotFoundError,
    CSSGenerationError,
    CSSInjectionError,
    ComponentRenderError,
    TokenNotFoundError,
    ThemeFileError,
    ThemeCacheError,
    ThemeStateError
)
from theming.error_handler import ErrorHandler, get_error_handler, set_error_handler


class TestExceptionHierarchy:
    """Test custom exception classes"""
    
    def test_theme_error_base(self):
        """Test base ThemeError exception"""
        error = ThemeError("Test error", details={'key': 'value'})
        
        assert str(error) == "Test error (key=value)"
        assert error.message == "Test error"
        assert error.details == {'key': 'value'}
    
    def test_theme_load_error(self):
        """Test ThemeLoadError exception"""
        error = ThemeLoadError(
            theme_name="custom-theme",
            reason="File not found",
            details={'path': '/themes/custom.json'}
        )
        
        assert error.theme_name == "custom-theme"
        assert error.reason == "File not found"
        assert "custom-theme" in str(error)
        assert "File not found" in str(error)
    
    def test_theme_validation_error(self):
        """Test ThemeValidationError exception"""
        errors = ["Invalid color", "Missing font"]
        error = ThemeValidationError(
            theme_name="invalid-theme",
            errors=errors
        )
        
        assert error.theme_name == "invalid-theme"
        assert error.validation_errors == errors
        assert "2 error(s)" in str(error)
    
    def test_theme_not_found_error(self):
        """Test ThemeNotFoundError exception"""
        available = ["default", "dark", "ocean"]
        error = ThemeNotFoundError(
            theme_name="missing",
            available_themes=available
        )
        
        assert error.theme_name == "missing"
        assert error.available_themes == available
        assert "missing" in str(error)
    
    def test_css_generation_error(self):
        """Test CSSGenerationError exception"""
        error = CSSGenerationError(
            theme_name="broken-theme",
            reason="Invalid token",
            details={'token': 'colors.invalid'}
        )
        
        assert error.theme_name == "broken-theme"
        assert error.reason == "Invalid token"
        assert "broken-theme" in str(error)
    
    def test_component_render_error(self):
        """Test ComponentRenderError exception"""
        error = ComponentRenderError(
            component_name="Card",
            reason="Missing props",
            details={'required': ['title']}
        )
        
        assert error.component_name == "Card"
        assert error.reason == "Missing props"
        assert "Card" in str(error)


class TestErrorHandler:
    """Test ErrorHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create fresh error handler for each test"""
        return ErrorHandler()
    
    def test_initialization(self, handler):
        """Test error handler initialization"""
        assert handler.error_count == 0
        assert len(handler.error_history) == 0
        assert handler.max_history_size == 100
        assert handler.max_recovery_attempts == 3
        assert handler.logger is not None
    
    def test_handle_error_basic(self, handler):
        """Test basic error handling"""
        error = ValueError("Test error")
        
        handler.handle_error(
            error=error,
            context={'test': 'value'},
            notify_user=False
        )
        
        assert handler.error_count == 1
        assert len(handler.error_history) == 1
        
        record = handler.error_history[0]
        assert record['error_type'] == 'ValueError'
        assert record['error_message'] == 'Test error'
        assert record['context'] == {'test': 'value'}
    
    def test_handle_error_with_details(self, handler):
        """Test error handling with ThemeError details"""
        error = ThemeLoadError(
            theme_name="test",
            reason="Test reason",
            details={'extra': 'info'}
        )
        
        handler.handle_error(error, notify_user=False)
        
        record = handler.error_history[0]
        assert record['details'] == {'extra': 'info'}
    
    def test_error_history_limit(self, handler):
        """Test error history size limit"""
        handler.max_history_size = 5
        
        # Add more errors than limit
        for i in range(10):
            handler.handle_error(
                ValueError(f"Error {i}"),
                notify_user=False
            )
        
        assert handler.error_count == 10
        assert len(handler.error_history) == 5
        
        # Check that oldest errors were removed
        messages = [r['error_message'] for r in handler.error_history]
        assert "Error 5" in messages
        assert "Error 0" not in messages
    
    def test_handle_theme_load_error(self, handler):
        """Test theme load error handling with fallback"""
        fallback_called = False
        
        def fallback():
            nonlocal fallback_called
            fallback_called = True
            return "fallback_theme"
        
        error = ThemeLoadError("custom", "Not found")
        result = handler.handle_theme_load_error(
            theme_name="custom",
            error=error,
            fallback_callback=fallback
        )
        
        assert fallback_called
        assert result == "fallback_theme"
        assert handler.error_count == 1
    
    def test_handle_css_generation_error(self, handler):
        """Test CSS generation error handling"""
        def fallback():
            return "/* fallback css */"
        
        error = CSSGenerationError("theme", "Invalid")
        result = handler.handle_css_generation_error(
            theme_name="theme",
            error=error,
            fallback_callback=fallback
        )
        
        assert result == "/* fallback css */"
        assert handler.error_count == 1
    
    def test_handle_component_error(self, handler):
        """Test component error handling"""
        fallback_called = False
        
        def fallback():
            nonlocal fallback_called
            fallback_called = True
            return "fallback_component"
        
        error = ComponentRenderError("Card", "Missing props")
        result = handler.handle_component_error(
            component_name="Card",
            error=error,
            fallback_callback=fallback
        )
        
        assert fallback_called
        assert result == "fallback_component"
    
    def test_automatic_recovery(self, handler):
        """Test automatic recovery mechanism"""
        call_count = 0
        
        def recovery_func():
            nonlocal call_count
            call_count += 1
            return "recovered"
        
        result = handler._attempt_recovery("test_op", recovery_func)
        
        assert result == "recovered"
        assert call_count == 1
        # Counter is reset to 0 on successful recovery
        assert handler.recovery_attempts["test_op"] == 0
    
    def test_recovery_retry_limit(self, handler):
        """Test recovery retry limit"""
        handler.max_recovery_attempts = 2
        call_count = 0
        
        def failing_recovery():
            nonlocal call_count
            call_count += 1
            raise ValueError("Still failing")
        
        # First attempt
        result1 = handler._attempt_recovery("test_op", failing_recovery)
        assert result1 is None
        assert call_count == 1
        
        # Second attempt
        result2 = handler._attempt_recovery("test_op", failing_recovery)
        assert result2 is None
        assert call_count == 2
        
        # Third attempt (should be blocked)
        result3 = handler._attempt_recovery("test_op", failing_recovery)
        assert result3 is None
        assert call_count == 2  # Should not increment
    
    def test_recovery_success_resets_counter(self, handler):
        """Test that successful recovery resets attempt counter"""
        def recovery_func():
            return "success"
        
        handler._attempt_recovery("test_op", recovery_func)
        assert handler.recovery_attempts["test_op"] == 0
    
    def test_get_error_report(self, handler):
        """Test error report generation"""
        # Add some errors
        handler.handle_error(ThemeLoadError("t1", "r1"), notify_user=False)
        handler.handle_error(ThemeLoadError("t2", "r2"), notify_user=False)
        handler.handle_error(CSSGenerationError("t3", "r3"), notify_user=False)
        
        report = handler.get_error_report()
        
        assert report['total_errors'] == 3
        assert report['errors_in_history'] == 3
        assert 'ThemeLoadError' in report['error_types']
        assert 'CSSGenerationError' in report['error_types']
        assert report['error_types']['ThemeLoadError'] == 2
        assert report['error_types']['CSSGenerationError'] == 1
        assert len(report['recent_errors']) == 3
    
    def test_export_error_report(self, handler, tmp_path):
        """Test error report export"""
        handler.handle_error(ValueError("Test"), notify_user=False)
        
        filepath = tmp_path / "test_report.json"
        handler.export_error_report(str(filepath))
        
        assert filepath.exists()
        
        with open(filepath) as f:
            data = json.load(f)
        
        assert data['total_errors'] == 1
        assert 'error_types' in data
        assert 'recent_errors' in data
    
    def test_clear_history(self, handler):
        """Test clearing error history"""
        handler.handle_error(ValueError("Test"), notify_user=False)
        handler._attempt_recovery("test", lambda: "ok")
        
        assert handler.error_count > 0
        assert len(handler.error_history) > 0
        assert len(handler.recovery_attempts) > 0
        
        handler.clear_history()
        
        # Count should remain but history should be cleared
        assert handler.error_count > 0
        assert len(handler.error_history) == 0
        assert len(handler.recovery_attempts) == 0
    
    def test_get_error_count_by_severity(self, handler):
        """Test error count by severity"""
        handler.handle_error(ThemeLoadError("t", "r"), notify_user=False)
        handler.handle_error(CSSGenerationError("t", "r"), notify_user=False)
        handler.handle_error(ComponentRenderError("c", "r"), notify_user=False)
        
        counts = handler.get_error_count_by_severity()
        
        assert 'critical' in counts
        assert 'warning' in counts
        assert 'info' in counts
        assert counts['critical'] >= 2  # Load and CSS errors
        assert counts['warning'] >= 1   # Component error


class TestGlobalErrorHandler:
    """Test global error handler functions"""
    
    def test_get_error_handler(self):
        """Test getting global error handler"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        # Should return same instance
        assert handler1 is handler2
    
    def test_set_error_handler(self):
        """Test setting global error handler"""
        custom_handler = ErrorHandler()
        set_error_handler(custom_handler)
        
        retrieved = get_error_handler()
        assert retrieved is custom_handler


class TestErrorLogging:
    """Test error logging functionality"""
    
    def test_logger_creation(self):
        """Test default logger creation"""
        handler = ErrorHandler()
        
        assert handler.logger is not None
        assert handler.logger.name == "shadcn_error_handler"
    
    def test_custom_logger(self):
        """Test using custom logger"""
        custom_logger = logging.getLogger("custom_test_logger")
        handler = ErrorHandler(logger=custom_logger)
        
        assert handler.logger is custom_logger
        assert handler.logger.name == "custom_test_logger"
    
    @patch('logging.Logger.error')
    def test_error_logging(self, mock_log):
        """Test that errors are logged"""
        handler = ErrorHandler()
        error = ValueError("Test error")
        
        handler.handle_error(error, notify_user=False, severity='error')
        
        # Verify logger was called
        assert mock_log.called


class TestErrorContextAndDetails:
    """Test error context and details handling"""
    
    def test_context_in_error_record(self):
        """Test that context is stored in error record"""
        handler = ErrorHandler()
        context = {
            'operation': 'theme_load',
            'user_id': 'user123',
            'timestamp': datetime.now().isoformat()
        }
        
        handler.handle_error(
            ValueError("Test"),
            context=context,
            notify_user=False
        )
        
        record = handler.error_history[0]
        assert record['context'] == context
    
    def test_details_from_theme_error(self):
        """Test that ThemeError details are captured"""
        handler = ErrorHandler()
        details = {'path': '/test/path', 'size': 1024}
        error = ThemeLoadError("theme", "reason", details=details)
        
        handler.handle_error(error, notify_user=False)
        
        record = handler.error_history[0]
        assert record['details'] == details
    
    def test_stack_trace_captured(self):
        """Test that stack trace is captured"""
        handler = ErrorHandler()
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            handler.handle_error(e, notify_user=False)
        
        record = handler.error_history[0]
        assert 'stack_trace' in record
        assert len(record['stack_trace']) > 0
        assert 'ValueError' in record['stack_trace']


def test_error_handler_integration():
    """Integration test for complete error handling flow"""
    handler = ErrorHandler()
    
    # Simulate a complete error handling scenario
    def load_theme_with_fallback(theme_name):
        try:
            # Simulate theme loading failure
            raise FileNotFoundError(f"Theme {theme_name} not found")
        except Exception as e:
            return handler.handle_theme_load_error(
                theme_name=theme_name,
                error=ThemeLoadError(theme_name, str(e)),
                fallback_callback=lambda: {"name": "default", "type": "fallback"}
            )
    
    # Load theme with error
    result = load_theme_with_fallback("custom-theme")
    
    # Verify fallback was used
    assert result == {"name": "default", "type": "fallback"}
    
    # Verify error was recorded
    assert handler.error_count == 1
    assert len(handler.error_history) == 1
    
    # Verify error report
    report = handler.get_error_report()
    assert report['total_errors'] == 1
    assert 'ThemeLoadError' in report['error_types']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
