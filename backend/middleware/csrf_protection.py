"""
CSRF Protection Middleware

Implements Cross-Site Request Forgery (CSRF) protection for state-changing operations.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from typing import Callable, Optional
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CSRFProtection:
    """
    CSRF Protection implementation
    
    Generates and validates CSRF tokens for state-changing operations.
    """
    
    def __init__(
        self,
        secret_key: str,
        token_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token",
        token_lifetime: int = 3600,  # 1 hour in seconds
        safe_methods: tuple = ("GET", "HEAD", "OPTIONS", "TRACE"),
    ):
        """
        Initialize CSRF protection
        
        Args:
            secret_key: Secret key for signing tokens
            token_name: Name of the token field
            header_name: Name of the header containing the token
            cookie_name: Name of the cookie containing the token
            token_lifetime: Token lifetime in seconds
            safe_methods: HTTP methods that don't require CSRF protection
        """
        self.secret_key = secret_key.encode()
        self.token_name = token_name
        self.header_name = header_name
        self.cookie_name = cookie_name
        self.token_lifetime = token_lifetime
        self.safe_methods = safe_methods
    
    def generate_token(self) -> str:
        """
        Generate a new CSRF token
        
        Returns:
            CSRF token string
        """
        # Generate random token
        random_token = secrets.token_urlsafe(32)
        
        # Add timestamp
        timestamp = str(int(datetime.now().timestamp()))
        
        # Create token with timestamp
        token_data = f"{random_token}:{timestamp}"
        
        # Sign the token
        signature = hmac.new(
            self.secret_key,
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Return token with signature
        return f"{token_data}:{signature}"
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a CSRF token
        
        Args:
            token: CSRF token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Split token into parts
            parts = token.split(":")
            if len(parts) != 3:
                return False
            
            random_token, timestamp, signature = parts
            
            # Check if token has expired
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.now() - token_time > timedelta(seconds=self.token_lifetime):
                logger.warning("CSRF token has expired")
                return False
            
            # Verify signature
            token_data = f"{random_token}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key,
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("CSRF token signature is invalid")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return False
    
    def get_token_from_request(self, request: Request) -> Optional[str]:
        """
        Extract CSRF token from request
        
        Args:
            request: FastAPI request object
            
        Returns:
            CSRF token if found, None otherwise
        """
        # Try to get token from header
        token = request.headers.get(self.header_name)
        if token:
            return token
        
        # Try to get token from form data
        if hasattr(request, "form"):
            try:
                form = request.form()
                token = form.get(self.token_name)
                if token:
                    return token
            except:
                pass
        
        # Try to get token from JSON body
        if hasattr(request, "json"):
            try:
                body = request.json()
                token = body.get(self.token_name)
                if token:
                    return token
            except:
                pass
        
        return None
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        CSRF protection middleware
        
        Args:
            request: FastAPI request object
            call_next: Next middleware in chain
            
        Returns:
            Response object
            
        Raises:
            HTTPException: If CSRF validation fails
        """
        # Skip CSRF check for safe methods
        if request.method in self.safe_methods:
            response = await call_next(request)
            
            # Add CSRF token to response for safe methods
            csrf_token = self.generate_token()
            response.set_cookie(
                key=self.cookie_name,
                value=csrf_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=self.token_lifetime
            )
            response.headers[self.header_name] = csrf_token
            
            return response
        
        # For state-changing methods, validate CSRF token
        token = self.get_token_from_request(request)
        
        if not token:
            logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if not self.validate_token(token):
            logger.warning(f"Invalid CSRF token for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )
        
        # Token is valid, proceed with request
        response = await call_next(request)
        
        # Generate new token for next request
        new_token = self.generate_token()
        response.set_cookie(
            key=self.cookie_name,
            value=new_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.token_lifetime
        )
        response.headers[self.header_name] = new_token
        
        return response


def get_csrf_protection(secret_key: str) -> CSRFProtection:
    """
    Factory function to create CSRF protection instance
    
    Args:
        secret_key: Secret key for signing tokens
        
    Returns:
        CSRFProtection instance
    """
    return CSRFProtection(secret_key=secret_key)


# Decorator for endpoints that require CSRF protection
def require_csrf(func):
    """
    Decorator to require CSRF token for an endpoint
    
    Usage:
        @app.post("/api/v1/data")
        @require_csrf
        async def create_data(request: Request):
            ...
    """
    async def wrapper(request: Request, *args, **kwargs):
        csrf = request.app.state.csrf_protection
        token = csrf.get_token_from_request(request)
        
        if not token or not csrf.validate_token(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing CSRF token"
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


# Exempt specific endpoints from CSRF protection
def csrf_exempt(func):
    """
    Decorator to exempt an endpoint from CSRF protection
    
    Usage:
        @app.post("/api/v1/webhook")
        @csrf_exempt
        async def webhook(request: Request):
            ...
    """
    func._csrf_exempt = True
    return func
