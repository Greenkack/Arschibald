"""
Feature Flag Middleware

This module provides middleware for checking feature flags on API requests.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional, List
from backend.services.feature_flag_service import FeatureFlagService
from backend.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check feature flags before processing requests
    
    This middleware can be configured to check specific feature flags
    for certain routes or endpoints.
    """
    
    def __init__(self, app, route_flags: Optional[dict] = None):
        """
        Initialize feature flag middleware
        
        Args:
            app: FastAPI application
            route_flags: Dictionary mapping route patterns to required feature flags
                        Example: {"/api/v1/solar/advanced": "solar.advanced_features"}
        """
        super().__init__(app)
        self.route_flags = route_flags or {}
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request and check feature flags
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from next handler
            
        Raises:
            HTTPException: If required feature is not enabled
        """
        # Check if this route requires a feature flag
        required_flag = self._get_required_flag(request.url.path)
        
        if required_flag:
            # Get user ID from request if available
            user_id = self._get_user_id_from_request(request)
            
            # Check if feature is enabled
            db = SessionLocal()
            try:
                service = FeatureFlagService(db)
                result = service.is_feature_enabled(required_flag, user_id)
                
                if not result.enabled:
                    logger.warning(
                        f"Feature flag '{required_flag}' not enabled for user {user_id}. "
                        f"Reason: {result.reason}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Feature '{required_flag}' is not available. {result.reason}"
                    )
            finally:
                db.close()
        
        # Continue with request
        response = await call_next(request)
        return response
    
    def _get_required_flag(self, path: str) -> Optional[str]:
        """
        Get required feature flag for a path
        
        Args:
            path: Request path
            
        Returns:
            Feature flag key if required, None otherwise
        """
        # Exact match
        if path in self.route_flags:
            return self.route_flags[path]
        
        # Prefix match
        for route_pattern, flag in self.route_flags.items():
            if path.startswith(route_pattern):
                return flag
        
        return None
    
    def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """
        Extract user ID from request
        
        Args:
            request: Incoming request
            
        Returns:
            User ID if available, None otherwise
        """
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, 'user'):
            return request.state.user.id
        
        # Try to get from headers (for testing)
        user_id_header = request.headers.get('X-User-ID')
        if user_id_header:
            try:
                return int(user_id_header)
            except ValueError:
                pass
        
        return None


def require_feature_flag(flag_key: str):
    """
    Decorator to require a feature flag for an endpoint
    
    Usage:
        @router.get("/advanced")
        @require_feature_flag("solar.advanced_features")
        async def advanced_endpoint():
            ...
    
    Args:
        flag_key: Feature flag key to check
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get('request')
            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Could not find request object for feature flag check"
                )
            
            # Get user ID
            user_id = None
            if hasattr(request.state, 'user'):
                user_id = request.state.user.id
            
            # Check feature flag
            db = SessionLocal()
            try:
                service = FeatureFlagService(db)
                result = service.is_feature_enabled(flag_key, user_id)
                
                if not result.enabled:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Feature '{flag_key}' is not available. {result.reason}"
                    )
            finally:
                db.close()
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class FeatureFlagCache:
    """
    Simple cache for feature flag checks to reduce database queries
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str, user_id: Optional[int] = None) -> Optional[bool]:
        """
        Get cached feature flag value
        
        Args:
            key: Feature flag key
            user_id: Optional user ID
            
        Returns:
            Cached value if available and not expired, None otherwise
        """
        cache_key = f"{key}:{user_id}"
        if cache_key in self.cache:
            value, timestamp = self.cache[cache_key]
            import time
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[cache_key]
        return None
    
    def set(self, key: str, value: bool, user_id: Optional[int] = None):
        """
        Set cached feature flag value
        
        Args:
            key: Feature flag key
            value: Feature flag value
            user_id: Optional user ID
        """
        import time
        cache_key = f"{key}:{user_id}"
        self.cache[cache_key] = (value, time.time())
    
    def clear(self):
        """Clear all cached values"""
        self.cache.clear()


# Global cache instance
feature_flag_cache = FeatureFlagCache()
