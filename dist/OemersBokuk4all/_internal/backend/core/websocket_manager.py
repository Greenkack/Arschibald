"""
WebSocket Manager for Real-Time Communication

This module provides WebSocket support for real-time updates,
progress notifications, and bidirectional communication between
the backend and frontend.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import socketio

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    CALCULATION_PROGRESS = "calculation_progress"
    CALCULATION_COMPLETE = "calculation_complete"
    CALCULATION_ERROR = "calculation_error"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    DATA_UPDATE = "data_update"
    HEARTBEAT = "heartbeat"


class WebSocketManager:
    """
    Manages WebSocket connections and message broadcasting
    """
    
    def __init__(self):
        # Create Socket.IO server
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=True,
            engineio_logger=True
        )
        
        # Track active connections
        self.active_connections: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.session_data: Dict[str, Dict[str, Any]] = {}  # session_id -> user data
        
        # Setup event handlers
        self._setup_handlers()
        
        logger.info("WebSocket Manager initialized")
    
    def _setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            logger.info(f"Client connected: {sid}")
            
            # Extract user info from auth
            user_id = auth.get('user_id') if auth else 'anonymous'
            
            # Store session data
            self.session_data[sid] = {
                'user_id': user_id,
                'connected_at': datetime.now().isoformat(),
                'authenticated': bool(auth)
            }
            
            # Track connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(sid)
            
            # Send welcome message
            await self.sio.emit('connected', {
                'message': 'Connected to Solar Calculator Pro',
                'session_id': sid,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
            
            logger.info(f"User {user_id} connected with session {sid}")
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {sid}")
            
            # Get user info
            session_info = self.session_data.get(sid, {})
            user_id = session_info.get('user_id', 'anonymous')
            
            # Remove from tracking
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(sid)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Clean up session data
            if sid in self.session_data:
                del self.session_data[sid]
            
            logger.info(f"User {user_id} disconnected session {sid}")
        
        @self.sio.event
        async def ping(sid):
            """Handle ping for connection health check"""
            await self.sio.emit('pong', {'timestamp': datetime.now().isoformat()}, room=sid)
        
        @self.sio.event
        async def subscribe(sid, data):
            """Subscribe to specific channels"""
            channels = data.get('channels', [])
            for channel in channels:
                await self.sio.enter_room(sid, channel)
                logger.info(f"Session {sid} subscribed to channel: {channel}")
            
            await self.sio.emit('subscribed', {
                'channels': channels,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
        
        @self.sio.event
        async def unsubscribe(sid, data):
            """Unsubscribe from specific channels"""
            channels = data.get('channels', [])
            for channel in channels:
                await self.sio.leave_room(sid, channel)
                logger.info(f"Session {sid} unsubscribed from channel: {channel}")
            
            await self.sio.emit('unsubscribed', {
                'channels': channels,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
    
    async def send_to_user(
        self,
        user_id: str,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Send message to all sessions of a specific user
        
        Args:
            user_id: User identifier
            event: Event name
            data: Message data
        """
        if user_id not in self.active_connections:
            logger.warning(f"User {user_id} has no active connections")
            return
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Send to all user sessions
        for sid in self.active_connections[user_id]:
            await self.sio.emit(event, data, room=sid)
        
        logger.debug(f"Sent {event} to user {user_id} ({len(self.active_connections[user_id])} sessions)")
    
    async def send_to_session(
        self,
        session_id: str,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Send message to a specific session
        
        Args:
            session_id: Session identifier
            event: Event name
            data: Message data
        """
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        await self.sio.emit(event, data, room=session_id)
        logger.debug(f"Sent {event} to session {session_id}")
    
    async def broadcast(
        self,
        event: str,
        data: Dict[str, Any],
        channel: Optional[str] = None
    ):
        """
        Broadcast message to all connected clients or specific channel
        
        Args:
            event: Event name
            data: Message data
            channel: Optional channel name to broadcast to
        """
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        if channel:
            await self.sio.emit(event, data, room=channel)
            logger.debug(f"Broadcast {event} to channel {channel}")
        else:
            await self.sio.emit(event, data)
            logger.debug(f"Broadcast {event} to all clients")
    
    async def send_calculation_progress(
        self,
        user_id: str,
        calculation_id: str,
        progress: float,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send calculation progress update
        
        Args:
            user_id: User identifier
            calculation_id: Calculation identifier
            progress: Progress percentage (0-100)
            message: Progress message
            details: Optional additional details
        """
        await self.send_to_user(user_id, MessageType.CALCULATION_PROGRESS, {
            'calculation_id': calculation_id,
            'progress': progress,
            'message': message,
            'details': details or {}
        })
    
    async def send_calculation_complete(
        self,
        user_id: str,
        calculation_id: str,
        result: Dict[str, Any]
    ):
        """
        Send calculation completion notification
        
        Args:
            user_id: User identifier
            calculation_id: Calculation identifier
            result: Calculation result
        """
        await self.send_to_user(user_id, MessageType.CALCULATION_COMPLETE, {
            'calculation_id': calculation_id,
            'result': result
        })
    
    async def send_calculation_error(
        self,
        user_id: str,
        calculation_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send calculation error notification
        
        Args:
            user_id: User identifier
            calculation_id: Calculation identifier
            error: Error message
            details: Optional error details
        """
        await self.send_to_user(user_id, MessageType.CALCULATION_ERROR, {
            'calculation_id': calculation_id,
            'error': error,
            'details': details or {}
        })
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        level: str = 'info',
        action: Optional[Dict[str, Any]] = None
    ):
        """
        Send notification to user
        
        Args:
            user_id: User identifier
            title: Notification title
            message: Notification message
            level: Notification level (info, success, warning, error)
            action: Optional action data
        """
        await self.send_to_user(user_id, MessageType.NOTIFICATION, {
            'title': title,
            'message': message,
            'level': level,
            'action': action
        })
    
    async def send_status_update(
        self,
        user_id: str,
        status: str,
        data: Dict[str, Any]
    ):
        """
        Send status update to user
        
        Args:
            user_id: User identifier
            status: Status type
            data: Status data
        """
        await self.send_to_user(user_id, MessageType.STATUS_UPDATE, {
            'status': status,
            'data': data
        })
    
    async def send_data_update(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        data: Dict[str, Any]
    ):
        """
        Send data update notification
        
        Args:
            user_id: User identifier
            entity_type: Type of entity (project, customer, etc.)
            entity_id: Entity identifier
            action: Action performed (created, updated, deleted)
            data: Entity data
        """
        await self.send_to_user(user_id, MessageType.DATA_UPDATE, {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'data': data
        })
    
    def get_active_users(self) -> int:
        """Get count of active users"""
        return len(self.active_connections)
    
    def get_active_sessions(self) -> int:
        """Get count of active sessions"""
        return sum(len(sessions) for sessions in self.active_connections.values())
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_user_sessions(self, user_id: str) -> Set[str]:
        """Get all session IDs for a user"""
        return self.active_connections.get(user_id, set())


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    return websocket_manager
