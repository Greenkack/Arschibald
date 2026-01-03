"""
Unit Tests for WebSocket Functionality

Tests the WebSocket manager, authentication, and message handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from backend.core.websocket_manager import WebSocketManager, MessageType
from backend.middleware.websocket_auth import WebSocketAuthMiddleware


class TestWebSocketManager:
    """Test WebSocket Manager functionality"""
    
    @pytest.fixture
    def ws_manager(self):
        """Create WebSocket manager instance"""
        return WebSocketManager()
    
    def test_initialization(self, ws_manager):
        """Test WebSocket manager initialization"""
        assert ws_manager.sio is not None
        assert isinstance(ws_manager.active_connections, dict)
        assert isinstance(ws_manager.session_data, dict)
        assert len(ws_manager.active_connections) == 0
        assert len(ws_manager.session_data) == 0
    
    def test_message_types(self):
        """Test message type enum"""
        assert MessageType.CALCULATION_PROGRESS == "calculation_progress"
        assert MessageType.CALCULATION_COMPLETE == "calculation_complete"
        assert MessageType.CALCULATION_ERROR == "calculation_error"
        assert MessageType.NOTIFICATION == "notification"
        assert MessageType.STATUS_UPDATE == "status_update"
        assert MessageType.DATA_UPDATE == "data_update"
        assert MessageType.HEARTBEAT == "heartbeat"
    
    @pytest.mark.asyncio
    async def test_send_to_user(self, ws_manager):
        """Test sending message to specific user"""
        # Setup mock session
        user_id = "test_user"
        session_id = "test_session"
        ws_manager.active_connections[user_id] = {session_id}
        ws_manager.session_data[session_id] = {
            'user_id': user_id,
            'authenticated': True
        }
        
        # Mock emit
        ws_manager.sio.emit = AsyncMock()
        
        # Send message
        await ws_manager.send_to_user(
            user_id=user_id,
            event="test_event",
            data={"message": "test"}
        )
        
        # Verify emit was called
        ws_manager.sio.emit.assert_called_once()
        call_args = ws_manager.sio.emit.call_args
        assert call_args[0][0] == "test_event"
        assert "message" in call_args[0][1]
        assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_send_to_session(self, ws_manager):
        """Test sending message to specific session"""
        session_id = "test_session"
        
        # Mock emit
        ws_manager.sio.emit = AsyncMock()
        
        # Send message
        await ws_manager.send_to_session(
            session_id=session_id,
            event="test_event",
            data={"message": "test"}
        )
        
        # Verify emit was called
        ws_manager.sio.emit.assert_called_once()
        call_args = ws_manager.sio.emit.call_args
        assert call_args[0][0] == "test_event"
        assert call_args[1]['room'] == session_id
    
    @pytest.mark.asyncio
    async def test_broadcast(self, ws_manager):
        """Test broadcasting message"""
        # Mock emit
        ws_manager.sio.emit = AsyncMock()
        
        # Broadcast without channel
        await ws_manager.broadcast(
            event="test_event",
            data={"message": "test"}
        )
        
        # Verify emit was called
        ws_manager.sio.emit.assert_called_once()
        
        # Reset mock
        ws_manager.sio.emit.reset_mock()
        
        # Broadcast with channel
        await ws_manager.broadcast(
            event="test_event",
            data={"message": "test"},
            channel="test_channel"
        )
        
        # Verify emit was called with channel
        ws_manager.sio.emit.assert_called_once()
        call_args = ws_manager.sio.emit.call_args
        assert call_args[1]['room'] == "test_channel"
    
    @pytest.mark.asyncio
    async def test_send_calculation_progress(self, ws_manager):
        """Test sending calculation progress"""
        user_id = "test_user"
        session_id = "test_session"
        ws_manager.active_connections[user_id] = {session_id}
        
        # Mock emit
        ws_manager.sio.emit = AsyncMock()
        
        # Send progress
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id="calc_123",
            progress=50.0,
            message="Processing..."
        )
        
        # Verify emit was called
        ws_manager.sio.emit.assert_called_once()
        call_args = ws_manager.sio.emit.call_args
        assert call_args[0][0] == MessageType.CALCULATION_PROGRESS
        data = call_args[0][1]
        assert data['calculation_id'] == "calc_123"
        assert data['progress'] == 50.0
        assert data['message'] == "Processing..."
    
    @pytest.mark.asyncio
    async def test_send_notification(self, ws_manager):
        """Test sending notification"""
        user_id = "test_user"
        session_id = "test_session"
        ws_manager.active_connections[user_id] = {session_id}
        
        # Mock emit
        ws_manager.sio.emit = AsyncMock()
        
        # Send notification
        await ws_manager.send_notification(
            user_id=user_id,
            title="Test",
            message="Test message",
            level="info"
        )
        
        # Verify emit was called
        ws_manager.sio.emit.assert_called_once()
        call_args = ws_manager.sio.emit.call_args
        assert call_args[0][0] == MessageType.NOTIFICATION
        data = call_args[0][1]
        assert data['title'] == "Test"
        assert data['message'] == "Test message"
        assert data['level'] == "info"
    
    def test_get_active_users(self, ws_manager):
        """Test getting active user count"""
        assert ws_manager.get_active_users() == 0
        
        # Add users
        ws_manager.active_connections["user1"] = {"session1"}
        ws_manager.active_connections["user2"] = {"session2", "session3"}
        
        assert ws_manager.get_active_users() == 2
    
    def test_get_active_sessions(self, ws_manager):
        """Test getting active session count"""
        assert ws_manager.get_active_sessions() == 0
        
        # Add sessions
        ws_manager.active_connections["user1"] = {"session1"}
        ws_manager.active_connections["user2"] = {"session2", "session3"}
        
        assert ws_manager.get_active_sessions() == 3
    
    def test_is_user_connected(self, ws_manager):
        """Test checking if user is connected"""
        user_id = "test_user"
        
        assert not ws_manager.is_user_connected(user_id)
        
        # Add connection
        ws_manager.active_connections[user_id] = {"session1"}
        
        assert ws_manager.is_user_connected(user_id)
    
    def test_get_user_sessions(self, ws_manager):
        """Test getting user sessions"""
        user_id = "test_user"
        
        assert len(ws_manager.get_user_sessions(user_id)) == 0
        
        # Add sessions
        sessions = {"session1", "session2"}
        ws_manager.active_connections[user_id] = sessions
        
        assert ws_manager.get_user_sessions(user_id) == sessions


class TestWebSocketAuth:
    """Test WebSocket authentication"""
    
    def test_verify_token_valid(self):
        """Test verifying valid JWT token"""
        # This would require a valid JWT token
        # For now, we test the structure
        with patch('backend.middleware.websocket_auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                'sub': 'user123',
                'username': 'testuser',
                'email': 'test@example.com',
                'role': 'user'
            }
            
            result = WebSocketAuthMiddleware.verify_token("valid_token")
            
            assert result is not None
            assert result['user_id'] == 'user123'
            assert result['username'] == 'testuser'
            assert result['role'] == 'user'
    
    def test_verify_token_invalid(self):
        """Test verifying invalid JWT token"""
        with patch('backend.middleware.websocket_auth.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            result = WebSocketAuthMiddleware.verify_token("invalid_token")
            
            assert result is None
    
    def test_extract_token_from_auth(self):
        """Test extracting token from auth data"""
        # Test with token field
        auth = {'token': 'test_token'}
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        assert token == 'test_token'
        
        # Test with Authorization header
        auth = {'Authorization': 'Bearer test_token'}
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        assert token == 'test_token'
        
        # Test with no token
        auth = {}
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        assert token is None
        
        # Test with None
        token = WebSocketAuthMiddleware.extract_token_from_auth(None)
        assert token is None
    
    @pytest.mark.asyncio
    async def test_authenticate_connection(self):
        """Test authenticating WebSocket connection"""
        with patch.object(WebSocketAuthMiddleware, 'extract_token_from_auth') as mock_extract:
            with patch.object(WebSocketAuthMiddleware, 'verify_token') as mock_verify:
                mock_extract.return_value = 'test_token'
                mock_verify.return_value = {
                    'user_id': 'user123',
                    'username': 'testuser'
                }
                
                result = await WebSocketAuthMiddleware.authenticate_connection(
                    {'token': 'test_token'}
                )
                
                assert result is not None
                assert result['user_id'] == 'user123'


@pytest.mark.asyncio
async def test_websocket_integration():
    """Integration test for WebSocket functionality"""
    ws_manager = WebSocketManager()
    
    # Simulate connection
    user_id = "test_user"
    session_id = "test_session"
    ws_manager.active_connections[user_id] = {session_id}
    ws_manager.session_data[session_id] = {
        'user_id': user_id,
        'authenticated': True
    }
    
    # Mock emit
    ws_manager.sio.emit = AsyncMock()
    
    # Test full workflow
    calculation_id = "calc_123"
    
    # Send progress updates
    for progress in [0, 25, 50, 75, 100]:
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id=calculation_id,
            progress=float(progress),
            message=f"Progress: {progress}%"
        )
    
    # Send completion
    await ws_manager.send_calculation_complete(
        user_id=user_id,
        calculation_id=calculation_id,
        result={"system_size": 10.5}
    )
    
    # Verify all messages were sent
    assert ws_manager.sio.emit.call_count == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
