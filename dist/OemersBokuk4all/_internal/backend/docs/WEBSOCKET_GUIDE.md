# WebSocket Support Guide

## Overview

The Solar Calculator Pro backend provides comprehensive WebSocket support for real-time communication between the server and clients. This enables features like:

- Real-time calculation progress updates
- Live notifications
- Data synchronization
- Status updates
- Bidirectional communication

## Architecture

### Components

1. **WebSocket Manager** (`backend/core/websocket_manager.py`)
   - Manages all WebSocket connections
   - Handles message broadcasting
   - Tracks active sessions
   - Provides high-level messaging APIs

2. **WebSocket Authentication** (`backend/middleware/websocket_auth.py`)
   - JWT-based authentication for WebSocket connections
   - Role-based access control
   - Session management

3. **WebSocket API** (`backend/api/v1/websocket.py`)
   - REST endpoints for WebSocket management
   - Testing and monitoring endpoints
   - Message sending APIs

## Connection

### Client Connection

```typescript
// Frontend example using Socket.IO client
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  path: '/socket.io',
  auth: {
    token: 'your_jwt_token_here'
  }
});

socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket server');
});
```

### Authentication

WebSocket connections can be authenticated using JWT tokens:

```typescript
// Pass token in auth object
const socket = io('http://localhost:8000', {
  path: '/socket.io',
  auth: {
    token: localStorage.getItem('access_token')
  }
});
```

## Message Types

### 1. Calculation Progress

Sent during long-running calculations to update progress:

```typescript
socket.on('calculation_progress', (data) => {
  console.log(`Progress: ${data.progress}%`);
  console.log(`Message: ${data.message}`);
  // Update UI progress bar
  updateProgressBar(data.progress);
});
```

**Data Structure:**
```json
{
  "calculation_id": "calc_12345",
  "progress": 45.5,
  "message": "Calculating solar production...",
  "details": {
    "step": "module_placement",
    "total_steps": 10,
    "current_step": 5
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Calculation Complete

Sent when a calculation finishes successfully:

```typescript
socket.on('calculation_complete', (data) => {
  console.log('Calculation complete!');
  console.log('Result:', data.result);
  // Display results
  displayResults(data.result);
});
```

**Data Structure:**
```json
{
  "calculation_id": "calc_12345",
  "result": {
    "system_size": 10.5,
    "module_count": 30,
    "annual_production": 12000,
    "payback_period": 8.5
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### 3. Calculation Error

Sent when a calculation fails:

```typescript
socket.on('calculation_error', (data) => {
  console.error('Calculation error:', data.error);
  // Show error message
  showError(data.error);
});
```

**Data Structure:**
```json
{
  "calculation_id": "calc_12345",
  "error": "Invalid roof area",
  "details": {
    "field": "roof_area",
    "value": -10,
    "constraint": "must be positive"
  },
  "timestamp": "2024-01-15T10:32:00Z"
}
```

### 4. Notifications

General notifications to users:

```typescript
socket.on('notification', (data) => {
  const { title, message, level } = data;
  // Show toast notification
  showToast(title, message, level);
});
```

**Data Structure:**
```json
{
  "title": "New Feature Available",
  "message": "Heat pump calculator is now available!",
  "level": "info",
  "action": {
    "label": "Try it now",
    "url": "/heatpump"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Notification Levels:**
- `info` - Informational messages
- `success` - Success messages
- `warning` - Warning messages
- `error` - Error messages

### 5. Status Updates

System or feature status updates:

```typescript
socket.on('status_update', (data) => {
  console.log('Status:', data.status);
  // Update status indicator
  updateStatus(data.status, data.data);
});
```

### 6. Data Updates

Real-time data synchronization:

```typescript
socket.on('data_update', (data) => {
  const { entity_type, entity_id, action, data: entityData } = data;
  
  if (action === 'created') {
    // Add new item to list
    addItem(entityData);
  } else if (action === 'updated') {
    // Update existing item
    updateItem(entity_id, entityData);
  } else if (action === 'deleted') {
    // Remove item from list
    removeItem(entity_id);
  }
});
```

## Channel Subscription

Subscribe to specific channels to receive targeted messages:

```typescript
// Subscribe to channels
socket.emit('subscribe', {
  channels: ['calculations', 'notifications', 'projects']
});

// Unsubscribe from channels
socket.emit('unsubscribe', {
  channels: ['calculations']
});

// Listen for subscription confirmation
socket.on('subscribed', (data) => {
  console.log('Subscribed to:', data.channels);
});
```

## Backend Usage

### Sending Messages from Services

```python
from backend.core.websocket_manager import get_websocket_manager

# Get WebSocket manager
ws_manager = get_websocket_manager()

# Send calculation progress
await ws_manager.send_calculation_progress(
    user_id="user123",
    calculation_id="calc_12345",
    progress=50.0,
    message="Halfway through calculation",
    details={"step": "optimization"}
)

# Send notification
await ws_manager.send_notification(
    user_id="user123",
    title="Calculation Complete",
    message="Your solar calculation is ready",
    level="success"
)

# Send data update
await ws_manager.send_data_update(
    user_id="user123",
    entity_type="project",
    entity_id="proj_456",
    action="updated",
    data={"name": "Updated Project", "status": "active"}
)
```

### Example: Solar Calculation with Progress

```python
from backend.services.solar_service import SolarService
from backend.core.websocket_manager import get_websocket_manager

async def calculate_solar_with_progress(request, user_id: str):
    ws_manager = get_websocket_manager()
    calculation_id = generate_calculation_id()
    
    try:
        # Step 1: Validate input
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id=calculation_id,
            progress=10.0,
            message="Validating input parameters"
        )
        
        # Step 2: Calculate system size
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id=calculation_id,
            progress=30.0,
            message="Calculating system size"
        )
        
        # Step 3: Module placement
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id=calculation_id,
            progress=60.0,
            message="Optimizing module placement"
        )
        
        # Step 4: Financial analysis
        await ws_manager.send_calculation_progress(
            user_id=user_id,
            calculation_id=calculation_id,
            progress=90.0,
            message="Calculating financial metrics"
        )
        
        # Complete
        result = perform_calculation(request)
        
        await ws_manager.send_calculation_complete(
            user_id=user_id,
            calculation_id=calculation_id,
            result=result
        )
        
        return result
    
    except Exception as e:
        await ws_manager.send_calculation_error(
            user_id=user_id,
            calculation_id=calculation_id,
            error=str(e)
        )
        raise
```

## REST API Endpoints

### Get WebSocket Status

```http
GET /api/v1/websocket/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "running",
  "active_users": 5,
  "active_sessions": 8,
  "message_types": [
    "calculation_progress",
    "calculation_complete",
    "calculation_error",
    "notification",
    "status_update",
    "data_update",
    "heartbeat"
  ]
}
```

### Get Active Connections

```http
GET /api/v1/websocket/connections
Authorization: Bearer <token>
```

**Response (Admin):**
```json
{
  "connections": [
    {
      "user_id": "user123",
      "session_id": "abc123",
      "connected_at": "2024-01-15T10:00:00Z",
      "authenticated": true
    }
  ]
}
```

### Broadcast Message (Admin Only)

```http
POST /api/v1/websocket/broadcast
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "event": "system_announcement",
  "data": {
    "message": "System maintenance in 1 hour"
  },
  "channel": "notifications"
}
```

### Send User Message

```http
POST /api/v1/websocket/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user123",
  "event": "custom_event",
  "data": {
    "key": "value"
  }
}
```

### Send Notification

```http
POST /api/v1/websocket/notify
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user123",
  "title": "Important Update",
  "message": "Your calculation is ready",
  "level": "info"
}
```

## Connection Management

### Heartbeat/Ping

Keep connection alive with periodic pings:

```typescript
// Send ping every 30 seconds
setInterval(() => {
  socket.emit('ping');
}, 30000);

// Listen for pong
socket.on('pong', (data) => {
  console.log('Connection alive:', data.timestamp);
});
```

### Reconnection

Handle reconnection automatically:

```typescript
socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
  
  if (reason === 'io server disconnect') {
    // Server disconnected, manually reconnect
    socket.connect();
  }
  // Otherwise, Socket.IO will automatically reconnect
});

socket.on('reconnect', (attemptNumber) => {
  console.log('Reconnected after', attemptNumber, 'attempts');
});
```

## Security

### Authentication

All WebSocket connections should be authenticated:

```typescript
// Include JWT token in connection
const socket = io('http://localhost:8000', {
  auth: {
    token: getAccessToken()
  }
});

// Handle authentication errors
socket.on('error', (error) => {
  if (error.message === 'Authentication required') {
    // Redirect to login
    redirectToLogin();
  }
});
```

### Authorization

Some events require specific roles:

```python
from backend.middleware.websocket_auth import WebSocketAuthMiddleware

@sio.event
@WebSocketAuthMiddleware.require_role('admin')
async def admin_event(sid, data):
    # Only admin users can trigger this event
    pass
```

## Testing

### Manual Testing

Use the demo script:

```bash
python backend/demo_websocket.py
```

### Integration Testing

```python
import pytest
from socketio import AsyncClient

@pytest.mark.asyncio
async def test_websocket_connection():
    client = AsyncClient()
    
    # Connect
    await client.connect('http://localhost:8000', socketio_path='/socket.io')
    
    # Test ping
    await client.emit('ping')
    
    # Wait for pong
    response = await client.receive()
    assert response[0] == 'pong'
    
    # Disconnect
    await client.disconnect()
```

## Best Practices

1. **Always authenticate connections** - Use JWT tokens for security
2. **Handle reconnection** - Implement automatic reconnection logic
3. **Use channels** - Subscribe only to relevant channels
4. **Implement heartbeat** - Keep connections alive with periodic pings
5. **Handle errors gracefully** - Show user-friendly error messages
6. **Clean up on unmount** - Disconnect when component unmounts
7. **Throttle updates** - Don't send too many updates too quickly
8. **Use message types** - Follow the defined message type conventions

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to WebSocket server

**Solutions:**
- Verify backend is running on correct port
- Check CORS settings
- Verify Socket.IO path is '/socket.io'
- Check firewall settings

### Authentication Issues

**Problem:** Connection rejected with authentication error

**Solutions:**
- Verify JWT token is valid and not expired
- Check token format in auth object
- Ensure user has necessary permissions

### Message Not Received

**Problem:** Client not receiving messages

**Solutions:**
- Verify client is subscribed to correct channel
- Check user_id matches authenticated user
- Verify WebSocket connection is active
- Check browser console for errors

## Performance Considerations

1. **Connection Pooling** - Reuse connections when possible
2. **Message Batching** - Batch multiple updates into single message
3. **Compression** - Enable WebSocket compression for large messages
4. **Selective Broadcasting** - Use channels to target specific users
5. **Rate Limiting** - Implement rate limiting for message sending

## Future Enhancements

- [ ] Message persistence for offline clients
- [ ] Message acknowledgment system
- [ ] Binary message support for large data
- [ ] WebSocket clustering for horizontal scaling
- [ ] Advanced analytics and monitoring
- [ ] Custom event handlers via plugins
