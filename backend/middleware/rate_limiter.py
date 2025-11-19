"""
Rate Limiting Middleware

Implements rate limiting using SlowAPI to prevent abuse and ensure fair usage.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour", "50/minute"],
    storage_uri="memory://",  # Use in-memory storage (can be changed to Redis)
    strategy="fixed-window",
    headers_enabled=True,
)


def get_limiter():
    """Get the limiter instance"""
    return limiter


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configured successfully")


# Custom rate limit decorators for different endpoint types
def rate_limit_auth(func):
    """Rate limit for authentication endpoints (stricter)"""
    return limiter.limit("5/minute")(func)


def rate_limit_calculation(func):
    """Rate limit for calculation endpoints (moderate)"""
    return limiter.limit("30/minute")(func)


def rate_limit_data(func):
    """Rate limit for data retrieval endpoints (lenient)"""
    return limiter.limit("100/minute")(func)


def rate_limit_upload(func):
    """Rate limit for file upload endpoints (strict)"""
    return limiter.limit("10/minute")(func)


# Custom key functions for more sophisticated rate limiting
def get_user_id(request: Request) -> str:
    """
    Get user ID from request for authenticated rate limiting
    Falls back to IP address if user is not authenticated
    """
    try:
        # Try to get user from token
        user = getattr(request.state, 'user', None)
        if user:
            return f"user:{user.id}"
    except:
        pass
    
    # Fallback to IP address
    return get_remote_address(request)


def get_api_key(request: Request) -> str:
    """
    Get API key from request headers for API key-based rate limiting
    Falls back to IP address if no API key is present
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key}"
    
    return get_remote_address(request)


# Create user-based limiter
user_limiter = Limiter(
    key_func=get_user_id,
    default_limits=["500/hour", "100/minute"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
)


# Create API key-based limiter
api_key_limiter = Limiter(
    key_func=get_api_key,
    default_limits=["1000/hour", "200/minute"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
)


class RateLimitConfig:
    """Configuration for rate limiting"""
    
    # Global limits
    GLOBAL_RATE_LIMIT = "200/hour"
    GLOBAL_BURST_LIMIT = "50/minute"
    
    # Endpoint-specific limits
    AUTH_LIMIT = "5/minute"
    CALCULATION_LIMIT = "30/minute"
    DATA_LIMIT = "100/minute"
    UPLOAD_LIMIT = "10/minute"
    EXPORT_LIMIT = "20/minute"
    
    # User-based limits (authenticated users get higher limits)
    USER_RATE_LIMIT = "500/hour"
    USER_BURST_LIMIT = "100/minute"
    
    # API key limits (for integrations)
    API_KEY_RATE_LIMIT = "1000/hour"
    API_KEY_BURST_LIMIT = "200/minute"
    
    # Storage configuration
    STORAGE_URI = "memory://"  # Change to "redis://localhost:6379" for production
    
    # Strategy
    STRATEGY = "fixed-window"  # Options: "fixed-window", "moving-window"
    
    # Headers
    HEADERS_ENABLED = True


def get_rate_limit_info(request: Request) -> dict:
    """
    Get rate limit information for the current request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with rate limit information
    """
    return {
        "limit": request.headers.get("X-RateLimit-Limit"),
        "remaining": request.headers.get("X-RateLimit-Remaining"),
        "reset": request.headers.get("X-RateLimit-Reset"),
    }


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to add rate limit information to all responses
    
    Args:
        request: FastAPI request object
        call_next: Next middleware in chain
        
    Returns:
        Response with rate limit headers
    """
    response = await call_next(request)
    
    # Add rate limit info to response headers
    rate_limit_info = get_rate_limit_info(request)
    if rate_limit_info["limit"]:
        response.headers["X-RateLimit-Limit"] = rate_limit_info["limit"]
        response.headers["X-RateLimit-Remaining"] = rate_limit_info["remaining"]
        response.headers["X-RateLimit-Reset"] = rate_limit_info["reset"]
    
    return response
