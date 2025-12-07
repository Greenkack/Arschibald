"""
Error Handler for Theme System

Provides centralized error handling with fallback mechanisms,
logging, and automatic recovery.
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from pathlib import Path
import json

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .theme_errors import (
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


class ErrorHandler:
    """
    Centralized error handler for the theme system.
    
    Features:
    - Error logging with stack traces
    - Fallback mechanisms
    - Automatic error recovery
    - Error statistics and reporting
    - User notifications
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Optional logger instance. If None, creates default logger.
        """
        self.logger = logger or self._create_default_logger()
        self.error_count = 0
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default logger for error handler"""
        logger = logging.getLogger("shadcn_error_handler")
        logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "theme_errors.log")
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        notify_user: bool = True,
        severity: str = "error"
    ) -> None:
        """
        Handle an error with logging and optional user notification.
        
        Args:
            error: The exception to handle
            context: Additional context information
            notify_user: Whether to show notification to user
            severity: Error severity level (error, warning, info)
        """
        # Record error
        error_record = self._create_error_record(error, context)
        self._add_to_history(error_record)
        
        # Log error
        self._log_error(error, error_record, severity)
        
        # Notify user if requested and Streamlit is available
        if notify_user and STREAMLIT_AVAILABLE:
            self._notify_user(error, severity)
    
    def _create_error_record(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create error record for history"""
        return {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'stack_trace': traceback.format_exc(),
            'details': getattr(error, 'details', {})
        }
    
    def _add_to_history(self, error_record: Dict[str, Any]) -> None:
        """Add error to history with size limit"""
        self.error_count += 1
        self.error_history.append(error_record)
        
        # Keep only recent errors
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _log_error(
        self,
        error: Exception,
        error_record: Dict[str, Any],
        severity: str
    ) -> None:
        """Log error with appropriate severity"""
        log_message = f"{error_record['error_type']}: {error_record['error_message']}"
        
        if error_record['context']:
            log_message += f" | Context: {error_record['context']}"
        
        if severity == "error":
            self.logger.error(log_message, exc_info=True)
        elif severity == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _notify_user(self, error: Exception, severity: str) -> None:
        """Show user notification in Streamlit"""
        if isinstance(error, ThemeLoadError):
            st.warning(
                f"⚠️ Theme '{error.theme_name}' konnte nicht geladen werden. "
                f"Verwende Fallback-Theme."
            )
        elif isinstance(error, ThemeValidationError):
            st.error(
                f"❌ Theme '{error.theme_name}' ist ungültig. "
                f"Gefunden: {len(error.validation_errors)} Fehler."
            )
        elif isinstance(error, CSSInjectionError):
            st.error(
                "❌ CSS konnte nicht geladen werden. "
                "App läuft mit Standard-Styling."
            )
        elif isinstance(error, ComponentRenderError):
            st.warning(
                f"⚠️ Komponente '{error.component_name}' konnte nicht "
                f"gerendert werden. Verwende Fallback."
            )
        elif isinstance(error, ThemeNotFoundError):
            available = ", ".join(error.available_themes[:5])
            st.warning(
                f"⚠️ Theme '{error.theme_name}' nicht gefunden. "
                f"Verfügbar: {available}"
            )
        else:
            if severity == "error":
                st.error(f"❌ Fehler: {str(error)}")
            elif severity == "warning":
                st.warning(f"⚠️ Warnung: {str(error)}")
            else:
                st.info(f"ℹ️ {str(error)}")
    
    def handle_theme_load_error(
        self,
        theme_name: str,
        error: Exception,
        fallback_callback: Callable
    ) -> Any:
        """
        Handle theme loading error with fallback.
        
        Args:
            theme_name: Name of theme that failed to load
            error: The exception that occurred
            fallback_callback: Function to call for fallback theme
            
        Returns:
            Result from fallback_callback
        """
        load_error = ThemeLoadError(
            theme_name=theme_name,
            reason=str(error),
            details={'original_error': type(error).__name__}
        )
        
        self.handle_error(load_error, context={'theme_name': theme_name})
        
        # Attempt recovery
        return self._attempt_recovery(
            f"theme_load_{theme_name}",
            fallback_callback
        )
    
    def handle_css_generation_error(
        self,
        theme_name: str,
        error: Exception,
        fallback_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Handle CSS generation error with optional fallback.
        
        Args:
            theme_name: Name of theme
            error: The exception that occurred
            fallback_callback: Optional function to generate fallback CSS
            
        Returns:
            Fallback CSS if available, None otherwise
        """
        css_error = CSSGenerationError(
            theme_name=theme_name,
            reason=str(error),
            details={'original_error': type(error).__name__}
        )
        
        self.handle_error(css_error, context={'theme_name': theme_name})
        
        if fallback_callback:
            return self._attempt_recovery(
                f"css_generation_{theme_name}",
                fallback_callback
            )
        return None
    
    def handle_css_injection_error(self, error: Exception) -> None:
        """
        Handle CSS injection error.
        
        Args:
            error: The exception that occurred
        """
        injection_error = CSSInjectionError(
            reason=str(error),
            details={'original_error': type(error).__name__}
        )
        
        self.handle_error(injection_error, severity="error")
    
    def handle_component_error(
        self,
        component_name: str,
        error: Exception,
        fallback_callback: Optional[Callable] = None
    ) -> Any:
        """
        Handle component rendering error with optional fallback.
        
        Args:
            component_name: Name of component
            error: The exception that occurred
            fallback_callback: Optional function to render fallback
            
        Returns:
            Result from fallback_callback if provided
        """
        component_error = ComponentRenderError(
            component_name=component_name,
            reason=str(error),
            details={'original_error': type(error).__name__}
        )
        
        self.handle_error(
            component_error,
            context={'component_name': component_name}
        )
        
        if fallback_callback:
            return self._attempt_recovery(
                f"component_{component_name}",
                fallback_callback
            )
        return None
    
    def _attempt_recovery(
        self,
        operation_key: str,
        recovery_callback: Callable
    ) -> Any:
        """
        Attempt automatic recovery with retry limit.
        
        Args:
            operation_key: Unique key for this operation
            recovery_callback: Function to call for recovery
            
        Returns:
            Result from recovery_callback
        """
        # Track recovery attempts
        if operation_key not in self.recovery_attempts:
            self.recovery_attempts[operation_key] = 0
        
        self.recovery_attempts[operation_key] += 1
        
        # Check if max attempts exceeded
        if self.recovery_attempts[operation_key] > self.max_recovery_attempts:
            self.logger.error(
                f"Max recovery attempts ({self.max_recovery_attempts}) "
                f"exceeded for operation: {operation_key}"
            )
            if STREAMLIT_AVAILABLE:
                st.error(
                    f"❌ Automatische Wiederherstellung fehlgeschlagen. "
                    f"Bitte Seite neu laden."
                )
            return None
        
        try:
            self.logger.info(
                f"Attempting recovery for {operation_key} "
                f"(attempt {self.recovery_attempts[operation_key]})"
            )
            result = recovery_callback()
            
            # Reset counter on success
            self.recovery_attempts[operation_key] = 0
            
            return result
        except Exception as e:
            self.logger.error(
                f"Recovery attempt failed for {operation_key}: {e}"
            )
            return None
    
    def get_error_report(self) -> Dict[str, Any]:
        """
        Get comprehensive error report.
        
        Returns:
            Dictionary with error statistics and recent errors
        """
        # Count errors by type
        error_types = {}
        for record in self.error_history:
            error_type = record['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = self.error_history[-10:] if self.error_history else []
        
        return {
            'total_errors': self.error_count,
            'errors_in_history': len(self.error_history),
            'error_types': error_types,
            'recent_errors': recent_errors,
            'recovery_attempts': dict(self.recovery_attempts),
            'generated_at': datetime.now().isoformat()
        }
    
    def export_error_report(self, filepath: str) -> None:
        """
        Export error report to JSON file.
        
        Args:
            filepath: Path to save report
        """
        report = self.get_error_report()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Error report exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export error report: {e}")
    
    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        self.recovery_attempts.clear()
        self.logger.info("Error history cleared")
    
    def get_error_count_by_severity(self) -> Dict[str, int]:
        """Get error count grouped by severity"""
        # This is a simplified version - in production you'd track severity
        return {
            'critical': sum(1 for e in self.error_history 
                          if 'CSS' in e['error_type'] or 'Load' in e['error_type']),
            'warning': sum(1 for e in self.error_history 
                         if 'Component' in e['error_type']),
            'info': len(self.error_history) - sum(1 for e in self.error_history 
                      if 'CSS' in e['error_type'] or 'Load' in e['error_type'] 
                      or 'Component' in e['error_type'])
        }


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set global error handler instance"""
    global _global_error_handler
    _global_error_handler = handler
