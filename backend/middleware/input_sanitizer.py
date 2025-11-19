"""
Input Sanitization Middleware

Implements input sanitization to prevent XSS, SQL injection, and other injection attacks.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from typing import Any, Dict, List, Union, Callable
import re
import html
import logging
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Input sanitization implementation
    
    Sanitizes user input to prevent various injection attacks.
    """
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*OR.*'.*=.*')",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<applet[^>]*>",
        r"<meta[^>]*>",
        r"<link[^>]*>",
        r"<style[^>]*>.*?</style>",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"%252e%252e",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"`.*`",
        r"\|\|",
        r"&&",
    ]
    
    def __init__(
        self,
        enable_html_escape: bool = True,
        enable_sql_check: bool = True,
        enable_xss_check: bool = True,
        enable_path_traversal_check: bool = True,
        enable_command_injection_check: bool = True,
        max_string_length: int = 10000,
        max_array_length: int = 1000,
        max_object_depth: int = 10,
    ):
        """
        Initialize input sanitizer
        
        Args:
            enable_html_escape: Enable HTML escaping
            enable_sql_check: Enable SQL injection detection
            enable_xss_check: Enable XSS detection
            enable_path_traversal_check: Enable path traversal detection
            enable_command_injection_check: Enable command injection detection
            max_string_length: Maximum allowed string length
            max_array_length: Maximum allowed array length
            max_object_depth: Maximum allowed object nesting depth
        """
        self.enable_html_escape = enable_html_escape
        self.enable_sql_check = enable_sql_check
        self.enable_xss_check = enable_xss_check
        self.enable_path_traversal_check = enable_path_traversal_check
        self.enable_command_injection_check = enable_command_injection_check
        self.max_string_length = max_string_length
        self.max_array_length = max_array_length
        self.max_object_depth = max_object_depth
        
        # Compile patterns for better performance
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.path_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]
        self.cmd_patterns = [re.compile(p) for p in self.COMMAND_INJECTION_PATTERNS]
    
    def check_sql_injection(self, value: str) -> bool:
        """
        Check if string contains SQL injection patterns
        
        Args:
            value: String to check
            
        Returns:
            True if SQL injection detected, False otherwise
        """
        if not self.enable_sql_check:
            return False
        
        for pattern in self.sql_patterns:
            if pattern.search(value):
                logger.warning(f"SQL injection pattern detected: {pattern.pattern}")
                return True
        
        return False
    
    def check_xss(self, value: str) -> bool:
        """
        Check if string contains XSS patterns
        
        Args:
            value: String to check
            
        Returns:
            True if XSS detected, False otherwise
        """
        if not self.enable_xss_check:
            return False
        
        for pattern in self.xss_patterns:
            if pattern.search(value):
                logger.warning(f"XSS pattern detected: {pattern.pattern}")
                return True
        
        return False
    
    def check_path_traversal(self, value: str) -> bool:
        """
        Check if string contains path traversal patterns
        
        Args:
            value: String to check
            
        Returns:
            True if path traversal detected, False otherwise
        """
        if not self.enable_path_traversal_check:
            return False
        
        # Decode URL encoding
        decoded = unquote(value)
        
        for pattern in self.path_patterns:
            if pattern.search(decoded):
                logger.warning(f"Path traversal pattern detected: {pattern.pattern}")
                return True
        
        return False
    
    def check_command_injection(self, value: str) -> bool:
        """
        Check if string contains command injection patterns
        
        Args:
            value: String to check
            
        Returns:
            True if command injection detected, False otherwise
        """
        if not self.enable_command_injection_check:
            return False
        
        for pattern in self.cmd_patterns:
            if pattern.search(value):
                logger.warning(f"Command injection pattern detected: {pattern.pattern}")
                return True
        
        return False
    
    def sanitize_string(self, value: str) -> str:
        """
        Sanitize a string value
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
            
        Raises:
            HTTPException: If dangerous patterns are detected
        """
        # Check length
        if len(value) > self.max_string_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"String length exceeds maximum of {self.max_string_length}"
            )
        
        # Check for dangerous patterns
        if self.check_sql_injection(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential SQL injection detected"
            )
        
        if self.check_xss(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential XSS attack detected"
            )
        
        if self.check_path_traversal(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential path traversal attack detected"
            )
        
        if self.check_command_injection(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential command injection detected"
            )
        
        # HTML escape if enabled
        if self.enable_html_escape:
            value = html.escape(value)
        
        return value
    
    def sanitize_value(self, value: Any, depth: int = 0) -> Any:
        """
        Recursively sanitize a value
        
        Args:
            value: Value to sanitize
            depth: Current recursion depth
            
        Returns:
            Sanitized value
            
        Raises:
            HTTPException: If dangerous patterns are detected or limits exceeded
        """
        # Check depth
        if depth > self.max_object_depth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Object nesting depth exceeds maximum of {self.max_object_depth}"
            )
        
        # Handle different types
        if isinstance(value, str):
            return self.sanitize_string(value)
        
        elif isinstance(value, dict):
            return {
                self.sanitize_string(k) if isinstance(k, str) else k: 
                self.sanitize_value(v, depth + 1)
                for k, v in value.items()
            }
        
        elif isinstance(value, list):
            if len(value) > self.max_array_length:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Array length exceeds maximum of {self.max_array_length}"
                )
            return [self.sanitize_value(item, depth + 1) for item in value]
        
        elif isinstance(value, tuple):
            return tuple(self.sanitize_value(item, depth + 1) for item in value)
        
        else:
            # Return other types as-is (int, float, bool, None, etc.)
            return value
    
    async def sanitize_request(self, request: Request) -> None:
        """
        Sanitize request data
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If dangerous patterns are detected
        """
        # Sanitize query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                self.sanitize_string(key)
                self.sanitize_string(value)
        
        # Sanitize path parameters
        if hasattr(request, "path_params") and request.path_params:
            for key, value in request.path_params.items():
                if isinstance(value, str):
                    self.sanitize_string(value)
        
        # Sanitize headers (only specific headers)
        sanitize_headers = ["User-Agent", "Referer", "X-Forwarded-For"]
        for header in sanitize_headers:
            value = request.headers.get(header)
            if value:
                self.sanitize_string(value)
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Input sanitization middleware
        
        Args:
            request: FastAPI request object
            call_next: Next middleware in chain
            
        Returns:
            Response object
        """
        try:
            # Sanitize request
            await self.sanitize_request(request)
            
            # Proceed with request
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in input sanitization: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing request"
            )


def get_input_sanitizer() -> InputSanitizer:
    """
    Factory function to create input sanitizer instance
    
    Returns:
        InputSanitizer instance
    """
    return InputSanitizer()


# Decorator for endpoints that require input sanitization
def sanitize_input(func):
    """
    Decorator to sanitize input for an endpoint
    
    Usage:
        @app.post("/api/v1/data")
        @sanitize_input
        async def create_data(data: dict):
            ...
    """
    async def wrapper(*args, **kwargs):
        sanitizer = InputSanitizer()
        
        # Sanitize all arguments
        sanitized_args = [sanitizer.sanitize_value(arg) for arg in args]
        sanitized_kwargs = {
            k: sanitizer.sanitize_value(v)
            for k, v in kwargs.items()
        }
        
        return await func(*sanitized_args, **sanitized_kwargs)
    
    return wrapper
