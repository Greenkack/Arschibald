"""
Middleware module initialization
"""

from backend.middleware.error_handler import APIError, setup_error_handlers

__all__ = ["APIError", "setup_error_handlers"]
