"""
Security Manager

Central security management for the FastAPI application.
Coordinates all security features including rate limiting, CSRF protection,
input sanitization, and security headers.
"""

from fastapi import FastAPI
from typing import Optional
import logging

from backend.middleware.rate_limiter import setup_rate_limiting, get_limiter
from backend.middleware.csrf_protection import get_csrf_protection
from backend.middleware.input_sanitizer import get_input_sanitizer
from backend.middleware.security_headers import setup_security_headers, SecurityHeadersConfig
from backend.core.config import settings

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Central security manager for the application
    
    Manages all security features and provides a unified interface.
    """
    
    def __init__(
        self,
        app: FastAPI,
        enable_rate_limiting: bool = True,
        enable_csrf_protection: bool = True,
        enable_input_sanitization: bool = True,
        enable_security_headers: bool = True,
        enable_sql_injection_prevention: bool = True,
    ):
        """
        Initialize security manager
        
        Args:
            app: FastAPI application instance
            enable_rate_limiting: Enable rate limiting
            enable_csrf_protection: Enable CSRF protection
            enable_input_sanitization: Enable input sanitization
            enable_security_headers: Enable security headers
            enable_sql_injection_prevention: Enable SQL injection prevention
        """
        self.app = app
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_csrf_protection = enable_csrf_protection
        self.enable_input_sanitization = enable_input_sanitization
        self.enable_security_headers = enable_security_headers
        self.enable_sql_injection_prevention = enable_sql_injection_prevention
        
        self.rate_limiter = None
        self.csrf_protection = None
        self.input_sanitizer = None
        
        logger.info("Security Manager initialized")
    
    def setup_rate_limiting(self):
        """Setup rate limiting"""
        if not self.enable_rate_limiting:
            logger.info("Rate limiting disabled")
            return
        
        try:
            setup_rate_limiting(self.app)
            self.rate_limiter = get_limiter()
            logger.info(" Rate limiting enabled")
        except Exception as e:
            logger.error(f"Failed to setup rate limiting: {e}")
            raise
    
    def setup_csrf_protection(self):
        """Setup CSRF protection"""
        if not self.enable_csrf_protection:
            logger.info("CSRF protection disabled")
            return
        
        try:
            self.csrf_protection = get_csrf_protection(settings.SECRET_KEY)
            self.app.middleware("http")(self.csrf_protection)
            self.app.state.csrf_protection = self.csrf_protection
            logger.info(" CSRF protection enabled")
        except Exception as e:
            logger.error(f"Failed to setup CSRF protection: {e}")
            raise
    
    def setup_input_sanitization(self):
        """Setup input sanitization"""
        if not self.enable_input_sanitization:
            logger.info("Input sanitization disabled")
            return
        
        try:
            self.input_sanitizer = get_input_sanitizer()
            self.app.middleware("http")(self.input_sanitizer)
            logger.info(" Input sanitization enabled")
        except Exception as e:
            logger.error(f"Failed to setup input sanitization: {e}")
            raise
    
    def setup_security_headers(self):
        """Setup security headers"""
        if not self.enable_security_headers:
            logger.info("Security headers disabled")
            return
        
        try:
            setup_security_headers(self.app)
            logger.info(" Security headers enabled")
        except Exception as e:
            logger.error(f"Failed to setup security headers: {e}")
            raise
    
    def setup_sql_injection_prevention(self):
        """Setup SQL injection prevention"""
        if not self.enable_sql_injection_prevention:
            logger.info("SQL injection prevention disabled")
            return
        
        # SQL injection prevention is handled by:
        # 1. SQLAlchemy ORM (parameterized queries)
        # 2. Input sanitization middleware
        # 3. Pydantic validation
        
        logger.info(" SQL injection prevention enabled (via ORM + sanitization)")
    
    def setup_all(self):
        """Setup all security features"""
        logger.info("=" * 60)
        logger.info("Setting up security features...")
        logger.info("=" * 60)
        
        # Order matters: setup in order of middleware execution
        self.setup_security_headers()
        self.setup_input_sanitization()
        self.setup_csrf_protection()
        self.setup_rate_limiting()
        self.setup_sql_injection_prevention()
        
        logger.info("=" * 60)
        logger.info("Security setup complete!")
        logger.info("=" * 60)
    
    def get_security_status(self) -> dict:
        """
        Get security status
        
        Returns:
            Dictionary with security feature status
        """
        return {
            "rate_limiting": {
                "enabled": self.enable_rate_limiting,
                "status": "active" if self.rate_limiter else "inactive"
            },
            "csrf_protection": {
                "enabled": self.enable_csrf_protection,
                "status": "active" if self.csrf_protection else "inactive"
            },
            "input_sanitization": {
                "enabled": self.enable_input_sanitization,
                "status": "active" if self.input_sanitizer else "inactive"
            },
            "security_headers": {
                "enabled": self.enable_security_headers,
                "status": "active"
            },
            "sql_injection_prevention": {
                "enabled": self.enable_sql_injection_prevention,
                "status": "active"
            }
        }


def setup_security(
    app: FastAPI,
    enable_rate_limiting: bool = True,
    enable_csrf_protection: bool = True,
    enable_input_sanitization: bool = True,
    enable_security_headers: bool = True,
    enable_sql_injection_prevention: bool = True,
) -> SecurityManager:
    """
    Setup security for the FastAPI application
    
    Args:
        app: FastAPI application instance
        enable_rate_limiting: Enable rate limiting
        enable_csrf_protection: Enable CSRF protection
        enable_input_sanitization: Enable input sanitization
        enable_security_headers: Enable security headers
        enable_sql_injection_prevention: Enable SQL injection prevention
        
    Returns:
        SecurityManager instance
    """
    security_manager = SecurityManager(
        app=app,
        enable_rate_limiting=enable_rate_limiting,
        enable_csrf_protection=enable_csrf_protection,
        enable_input_sanitization=enable_input_sanitization,
        enable_security_headers=enable_security_headers,
        enable_sql_injection_prevention=enable_sql_injection_prevention,
    )
    
    security_manager.setup_all()
    
    # Store security manager in app state
    app.state.security_manager = security_manager
    
    return security_manager


# Security configuration presets
class SecurityPresets:
    """Predefined security configuration presets"""
    
    @staticmethod
    def development():
        """Development preset (less strict)"""
        return {
            "enable_rate_limiting": False,
            "enable_csrf_protection": False,
            "enable_input_sanitization": True,
            "enable_security_headers": False,
            "enable_sql_injection_prevention": True,
        }
    
    @staticmethod
    def production():
        """Production preset (strict)"""
        return {
            "enable_rate_limiting": True,
            "enable_csrf_protection": True,
            "enable_input_sanitization": True,
            "enable_security_headers": True,
            "enable_sql_injection_prevention": True,
        }
    
    @staticmethod
    def testing():
        """Testing preset (minimal)"""
        return {
            "enable_rate_limiting": False,
            "enable_csrf_protection": False,
            "enable_input_sanitization": False,
            "enable_security_headers": False,
            "enable_sql_injection_prevention": True,
        }
