"""
Security Headers Middleware

Implements security headers to protect against common web vulnerabilities.
"""

from fastapi import Request, Response
from typing import Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SecurityHeaders:
    """
    Security headers implementation
    
    Adds security headers to all responses to protect against common attacks.
    """
    
    def __init__(
        self,
        enable_hsts: bool = True,
        enable_csp: bool = True,
        enable_x_frame_options: bool = True,
        enable_x_content_type_options: bool = True,
        enable_x_xss_protection: bool = True,
        enable_referrer_policy: bool = True,
        enable_permissions_policy: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        csp_directives: Optional[Dict[str, str]] = None,
        frame_options: str = "DENY",
        referrer_policy: str = "strict-origin-when-cross-origin"):
        """
        Initialize security headers
        
        Args:
            enable_hsts: Enable HTTP Strict Transport Security
            enable_csp: Enable Content Security Policy
            enable_x_frame_options: Enable X-Frame-Options
            enable_x_content_type_options: Enable X-Content-Type-Options
            enable_x_xss_protection: Enable X-XSS-Protection
            enable_referrer_policy: Enable Referrer-Policy
            enable_permissions_policy: Enable Permissions-Policy
            hsts_max_age: HSTS max-age in seconds
            hsts_include_subdomains: Include subdomains in HSTS
            hsts_preload: Enable HSTS preload
            csp_directives: Custom CSP directives
            frame_options: X-Frame-Options value (DENY, SAMEORIGIN)
            referrer_policy: Referrer-Policy value
        """
        self.enable_hsts = enable_hsts
        self.enable_csp = enable_csp
        self.enable_x_frame_options = enable_x_frame_options
        self.enable_x_content_type_options = enable_x_content_type_options
        self.enable_x_xss_protection = enable_x_xss_protection
        self.enable_referrer_policy = enable_referrer_policy
        self.enable_permissions_policy = enable_permissions_policy
        
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        
        self.frame_options = frame_options
        self.referrer_policy = referrer_policy
        
        # Default CSP directives
        self.csp_directives = csp_directives or {
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data: https:",
            "font-src": "'self' data:",
            "connect-src": "'self'",
            "frame-ancestors": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
        }
    
    def get_hsts_header(self) -> str:
        """
        Get HSTS header value
        
        Returns:
            HSTS header value
        """
        value = f"max-age={self.hsts_max_age}"
        
        if self.hsts_include_subdomains:
            value += "; includeSubDomains"
        
        if self.hsts_preload:
            value += "; preload"
        
        return value
    
    def get_csp_header(self) -> str:
        """
        Get CSP header value
        
        Returns:
            CSP header value
        """
        directives = []
        for directive, value in self.csp_directives.items():
            directives.append(f"{directive} {value}")
        
        return "; ".join(directives)
    
    def get_permissions_policy_header(self) -> str:
        """
        Get Permissions-Policy header value
        
        Returns:
            Permissions-Policy header value
        """
        # Restrict dangerous features
        policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        
        return ", ".join(policies)
    
    def add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response
        
        Args:
            response: FastAPI response object
            
        Returns:
            Response with security headers
        """
        # HTTP Strict Transport Security (HSTS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = self.get_hsts_header()
        
        # Content Security Policy (CSP)
        if self.enable_csp:
            response.headers["Content-Security-Policy"] = self.get_csp_header()
        
        # X-Frame-Options
        if self.enable_x_frame_options:
            response.headers["X-Frame-Options"] = self.frame_options
        
        # X-Content-Type-Options
        if self.enable_x_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        if self.enable_x_xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        if self.enable_referrer_policy:
            response.headers["Referrer-Policy"] = self.referrer_policy
        
        # Permissions-Policy
        if self.enable_permissions_policy:
            response.headers["Permissions-Policy"] = self.get_permissions_policy_header()
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["X-Download-Options"] = "noopen"
        
        return response
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Security headers middleware
        
        Args:
            request: FastAPI request object
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers
        """
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response = self.add_security_headers(response)
        
        return response


def get_security_headers(
    enable_hsts: bool = True,
    enable_csp: bool = True,
    csp_directives: Optional[Dict[str, str]] = None) -> SecurityHeaders:
    """
    Factory function to create security headers instance
    
    Args:
        enable_hsts: Enable HSTS
        enable_csp: Enable CSP
        csp_directives: Custom CSP directives
        
    Returns:
        SecurityHeaders instance
    """
    return SecurityHeaders(
        enable_hsts=enable_hsts,
        enable_csp=enable_csp,
        csp_directives=csp_directives)


class SecurityHeadersConfig:
    """Configuration for security headers"""
    
    # HSTS Configuration
    HSTS_ENABLED = True
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = False
    
    # CSP Configuration
    CSP_ENABLED = True
    CSP_DIRECTIVES = {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data: https:",
        "font-src": "'self' data:",
        "connect-src": "'self' ws: wss:",
        "frame-ancestors": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'",
    }
    
    # X-Frame-Options
    X_FRAME_OPTIONS_ENABLED = True
    X_FRAME_OPTIONS_VALUE = "DENY"
    
    # X-Content-Type-Options
    X_CONTENT_TYPE_OPTIONS_ENABLED = True
    
    # X-XSS-Protection
    X_XSS_PROTECTION_ENABLED = True
    
    # Referrer-Policy
    REFERRER_POLICY_ENABLED = True
    REFERRER_POLICY_VALUE = "strict-origin-when-cross-origin"
    
    # Permissions-Policy
    PERMISSIONS_POLICY_ENABLED = True


def setup_security_headers(app, config: Optional[SecurityHeadersConfig] = None):
    """
    Setup security headers for the FastAPI application
    
    Args:
        app: FastAPI application instance
        config: Security headers configuration
    """
    if config is None:
        config = SecurityHeadersConfig()
    
    security_headers = SecurityHeaders(
        enable_hsts=config.HSTS_ENABLED,
        enable_csp=config.CSP_ENABLED,
        enable_x_frame_options=config.X_FRAME_OPTIONS_ENABLED,
        enable_x_content_type_options=config.X_CONTENT_TYPE_OPTIONS_ENABLED,
        enable_x_xss_protection=config.X_XSS_PROTECTION_ENABLED,
        enable_referrer_policy=config.REFERRER_POLICY_ENABLED,
        enable_permissions_policy=config.PERMISSIONS_POLICY_ENABLED,
        hsts_max_age=config.HSTS_MAX_AGE,
        hsts_include_subdomains=config.HSTS_INCLUDE_SUBDOMAINS,
        hsts_preload=config.HSTS_PRELOAD,
        csp_directives=config.CSP_DIRECTIVES,
        frame_options=config.X_FRAME_OPTIONS_VALUE,
        referrer_policy=config.REFERRER_POLICY_VALUE)
    
    app.middleware("http")(security_headers)
    
    logger.info("Security headers configured successfully")
