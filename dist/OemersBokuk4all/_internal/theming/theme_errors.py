"""
Theme Error Exception Hierarchy

Defines all custom exceptions for the theme system.
"""

from typing import Optional, Dict, Any


class ThemeError(Exception):
    """Base exception for all theme-related errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ThemeLoadError(ThemeError):
    """Raised when a theme cannot be loaded"""
    
    def __init__(self, theme_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"Failed to load theme '{theme_name}': {reason}"
        super().__init__(message, details)
        self.theme_name = theme_name
        self.reason = reason


class ThemeValidationError(ThemeError):
    """Raised when theme validation fails"""
    
    def __init__(self, theme_name: str, errors: list, details: Optional[Dict[str, Any]] = None):
        message = f"Theme '{theme_name}' validation failed with {len(errors)} error(s)"
        super().__init__(message, details)
        self.theme_name = theme_name
        self.validation_errors = errors


class ThemeNotFoundError(ThemeError):
    """Raised when a requested theme does not exist"""
    
    def __init__(self, theme_name: str, available_themes: list):
        message = f"Theme '{theme_name}' not found"
        details = {"available_themes": available_themes}
        super().__init__(message, details)
        self.theme_name = theme_name
        self.available_themes = available_themes


class CSSGenerationError(ThemeError):
    """Raised when CSS generation fails"""
    
    def __init__(self, theme_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"CSS generation failed for theme '{theme_name}': {reason}"
        super().__init__(message, details)
        self.theme_name = theme_name
        self.reason = reason


class CSSInjectionError(ThemeError):
    """Raised when CSS injection into Streamlit fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"CSS injection failed: {reason}"
        super().__init__(message, details)
        self.reason = reason


class ComponentRenderError(ThemeError):
    """Raised when a component fails to render"""
    
    def __init__(self, component_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"Component '{component_name}' failed to render: {reason}"
        super().__init__(message, details)
        self.component_name = component_name
        self.reason = reason


class TokenNotFoundError(ThemeError):
    """Raised when a design token is not found"""
    
    def __init__(self, token_path: str, theme_name: str):
        message = f"Token '{token_path}' not found in theme '{theme_name}'"
        super().__init__(message)
        self.token_path = token_path
        self.theme_name = theme_name


class ThemeFileError(ThemeError):
    """Raised when there's an error with theme file operations"""
    
    def __init__(self, filepath: str, operation: str, reason: str):
        message = f"Theme file operation '{operation}' failed for '{filepath}': {reason}"
        super().__init__(message)
        self.filepath = filepath
        self.operation = operation
        self.reason = reason


class ThemeCacheError(ThemeError):
    """Raised when there's an error with theme caching"""
    
    def __init__(self, operation: str, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"Cache operation '{operation}' failed: {reason}"
        super().__init__(message, details)
        self.operation = operation
        self.reason = reason


class ThemeStateError(ThemeError):
    """Raised when there's an error with theme state management"""
    
    def __init__(self, operation: str, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"State operation '{operation}' failed: {reason}"
        super().__init__(message, details)
        self.operation = operation
        self.reason = reason
