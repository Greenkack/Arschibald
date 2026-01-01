"""
WebSocket API Endpoints

Provides REST API endpoints for WebSocket management and testing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.core.websocket_manager import get_websocket_manager, MessageType
from backend.core.auth_dependencies import get_current_user
from backend.models.auth_schemas import UserResponse

router = APIRouter()


class BroadcastMessage(BaseModel):
    """Model for broadcast message"""
    event: str
    data: Dict[str, Any]
    channel: Optional[str] = None


class UserMessage(BaseModel):
    """Model for user-specific message"""
    user_id: str
    event: str
    data: Dict[str, Any]


class NotificationMessage(BaseModel):
    """Model for notification"""
    user_id: str
    title: str
    message: str
    level: str = 'info'
    action: Optional[Dict[str, Any]] = None


class CalculationProgress(BaseModel):
    """Model for calculation progress update"""
    user_id: str
    calculation_id: str
    progress: float
    message: str
    details: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_websocket_status(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get WebSocket server status
    
    Returns information about active connections and server health.
    """
    ws_manager = get_websocket_manager()
    
    return {
        "status": "running",
        "active_users": ws_manager.get_active_users(),
        "active_sessions": ws_manager.get_active_sessions(),
        "message_types": [mt.value for mt in MessageType]
    }


@router.get("/connections")
async def get_active_connections(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get list of active WebSocket connections
    
    Requires authentication. Admin users can see all connections,
    regular users can only see their own.
    """
    ws_manager = get_websocket_manager()
    
    if current_user.role == 'admin':
        # Admin can see all connections
        connections = []
        for user_id, sessions in ws_manager.active_connections.items():
            for session_id in sessions:
                session_data = ws_manager.session_data.get(session_id, {})
                connections.append({
                    'user_id': user_id,
                    'session_id': session_id,
                    'connected_at': session_data.get('connected_at'),
                    'authenticated': session_data.get('authenticated', False)
                })
        return {"connections": connections}
    else:
        # Regular users can only see their own connections
        user_sessions = ws_manager.get_user_sessions(current_user.username)
        connections = []
        for session_id in user_sessions:
            session_data = ws_manager.session_data.get(session_id, {})
            connections.append({
                'session_id': session_id,
                'connected_at': session_data.get('connected_at'),
                'authenticated': session_data.get('authenticated', False)
            })
        return {"connections": connections}


@router.post("/broadcast")
async def broadcast_message(
    message: BroadcastMessage,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Broadcast message to all connected clients or specific channel
    
    Requires admin role.
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can broadcast messages"
        )
    
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(
        event=message.event,
        data=message.data,
        channel=message.channel
    )
    
    return {
        "status": "success",
        "message": "Message broadcast successfully",
        "event": message.event,
        "channel": message.channel
    }


@router.post("/send")
async def send_user_message(
    message: UserMessage,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Send message to specific user
    
    Users can only send messages to themselves unless they are admin.
    """
    # Check permissions
    if current_user.role != 'admin' and message.user_id != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send messages to yourself"
        )
    
    ws_manager = get_websocket_manager()
    
    # Check if user is connected
    if not ws_manager.is_user_connected(message.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {message.user_id} is not connected"
        )
    
    await ws_manager.send_to_user(
        user_id=message.user_id,
        event=message.event,
        data=message.data
    )
    
    return {
        "status": "success",
        "message": "Message sent successfully",
        "user_id": message.user_id,
        "event": message.event
    }


@router.post("/notify")
async def send_notification(
    notification: NotificationMessage,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Send notification to user
    
    Users can only send notifications to themselves unless they are admin.
    """
    # Check permissions
    if current_user.role != 'admin' and notification.user_id != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send notifications to yourself"
        )
    
    ws_manager = get_websocket_manager()
    
    # Check if user is connected
    if not ws_manager.is_user_connected(notification.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {notification.user_id} is not connected"
        )
    
    await ws_manager.send_notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        level=notification.level,
        action=notification.action
    )
    
    return {
        "status": "success",
        "message": "Notification sent successfully",
        "user_id": notification.user_id
    }


@router.post("/calculation/progress")
async def send_calculation_progress(
    progress: CalculationProgress,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Send calculation progress update
    
    Used by backend services to notify users about calculation progress.
    """
    ws_manager = get_websocket_manager()
    
    await ws_manager.send_calculation_progress(
        user_id=progress.user_id,
        calculation_id=progress.calculation_id,
        progress=progress.progress,
        message=progress.message,
        details=progress.details
    )
    
    return {
        "status": "success",
        "message": "Progress update sent",
        "calculation_id": progress.calculation_id,
        "progress": progress.progress
    }


@router.get("/test")
async def test_websocket():
    """
    Test endpoint to verify WebSocket is working
    
    This endpoint doesn't require authentication and can be used
    to test basic WebSocket functionality.
    """
    ws_manager = get_websocket_manager()
    
    return {
        "status": "ok",
        "message": "WebSocket server is running",
        "active_users": ws_manager.get_active_users(),
        "active_sessions": ws_manager.get_active_sessions(),
        "endpoints": {
            "status": "/api/v1/websocket/status",
            "connections": "/api/v1/websocket/connections",
            "broadcast": "/api/v1/websocket/broadcast",
            "send": "/api/v1/websocket/send",
            "notify": "/api/v1/websocket/notify",
            "test": "/api/v1/websocket/test"
        }
    }
