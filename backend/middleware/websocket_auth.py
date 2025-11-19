"""
WebSocket Authentication Middleware

Handles authentication for WebSocket connections using JWT tokens.
"""

import logging
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from backend.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketAuthMiddleware:
    """
    Middleware for authenticating WebSocket connections
    """
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and extract user information
        
        Args:
            token: JWT token string
            
        Returns:
            User information dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                logger.warning("Token missing 'sub' claim")
                return None
            
            return {
                'user_id': user_id,
                'username': payload.get('username'),
                'email': payload.get('email'),
                'role': payload.get('role', 'user')
            }
        
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            return None
    
    @staticmethod
    def extract_token_from_auth(auth: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract token from Socket.IO auth data
        
        Args:
            auth: Authentication data from Socket.IO connection
            
        Returns:
            Token string if present, None otherwise
        """
        if not auth:
            return None
        
        # Try different token formats
        token = auth.get('token')
        if token:
            return token
        
        # Try Authorization header format
        authorization = auth.get('Authorization') or auth.get('authorization')
        if authorization:
            # Handle "Bearer <token>" format
            if authorization.startswith('Bearer '):
                return authorization[7:]
            return authorization
        
        return None
    
    @staticmethod
    async def authenticate_connection(auth: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Authenticate a WebSocket connection
        
        Args:
            auth: Authentication data from Socket.IO connection
            
        Returns:
            User information if authenticated, None otherwise
        """
        # Extract token
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        
        if not token:
            logger.info("No token provided for WebSocket connection")
            return None
        
        # Verify token
        user_info = WebSocketAuthMiddleware.verify_token(token)
        
        if user_info:
            logger.info(f"WebSocket connection authenticated for user: {user_info['user_id']}")
        else:
            logger.warning("WebSocket authentication failed")
        
        return user_info
    
    @staticmethod
    def require_authentication(func):
        """
        Decorator to require authentication for Socket.IO event handlers
        
        Usage:
            @sio.event
            @WebSocketAuthMiddleware.require_authentication
            async def my_event(sid, data):
                # This will only execute if user is authenticated
                pass
        """
        async def wrapper(sid, *args, **kwargs):
            # Get WebSocket manager
            from backend.core.websocket_manager import get_websocket_manager
            ws_manager = get_websocket_manager()
            
            # Check if session is authenticated
            session_data = ws_manager.session_data.get(sid, {})
            if not session_data.get('authenticated'):
                logger.warning(f"Unauthenticated access attempt on {func.__name__} from session {sid}")
                await ws_manager.send_to_session(sid, 'error', {
                    'message': 'Authentication required',
                    'event': func.__name__
                })
                return
            
            # Call original function
            return await func(sid, *args, **kwargs)
        
        return wrapper
    
    @staticmethod
    def require_role(required_role: str):
        """
        Decorator to require specific role for Socket.IO event handlers
        
        Args:
            required_role: Required user role (e.g., 'admin', 'user')
            
        Usage:
            @sio.event
            @WebSocketAuthMiddleware.require_role('admin')
            async def admin_event(sid, data):
                # This will only execute if user has admin role
                pass
        """
        def decorator(func):
            async def wrapper(sid, *args, **kwargs):
                # Get WebSocket manager
                from backend.core.websocket_manager import get_websocket_manager
                ws_manager = get_websocket_manager()
                
                # Check if session is authenticated
                session_data = ws_manager.session_data.get(sid, {})
                if not session_data.get('authenticated'):
                    logger.warning(f"Unauthenticated access attempt on {func.__name__} from session {sid}")
                    await ws_manager.send_to_session(sid, 'error', {
                        'message': 'Authentication required',
                        'event': func.__name__
                    })
                    return
                
                # Check role
                user_role = session_data.get('role', 'user')
                if user_role != required_role and user_role != 'admin':
                    logger.warning(f"Insufficient permissions for {func.__name__} from session {sid} (role: {user_role})")
                    await ws_manager.send_to_session(sid, 'error', {
                        'message': f'Insufficient permissions. Required role: {required_role}',
                        'event': func.__name__
                    })
                    return
                
                # Call original function
                return await func(sid, *args, **kwargs)
            
            return wrapper
        return decorator
