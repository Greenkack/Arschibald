# WebSocket Quick Reference

## Client Connection

```typescript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  path: '/socket.io',
  auth: { token: 'your_jwt_token' }
});
```

## Event Listeners

```typescript
// Connection events
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));
socket.on('connected', (data) => console.log('Welcome:', data));

// Calculation events
socket.on('calculation_progress', (data) => {
  console.log(`${data.progress}%: ${data.message}`);
});

socket.on('calculation_complete', (data) => {
  console.log('Result:', data.result);
});

socket.on('calculation_error', (data) => {
  console.error('Error:', data.error);
});

// Notifications
socket.on('notification', (data) => {
  showToast(data.title, data.message, data.level);
});

// Data updates
socket.on('data_update', (data) => {
  handleDataUpdate(data.entity_type, data.action, data.data);
});

// Status updates
socket.on('status_update', (data) => {
  updateStatus(data.status, data.data);
});
```

## Emitting Events

```typescript
// Ping/Pong
socket.emit('ping');
socket.on('pong', (data) => console.log('Pong:', data.timestamp));

// Subscribe to channels
socket.emit('subscribe', { channels: ['calculations', 'notifications'] });
socket.on('subscribed', (data) => console.log('Subscribed:', data.channels));

// Unsubscribe from channels
socket.emit('unsubscribe', { channels: ['calculations'] });
socket.on('unsubscribed', (data) => console.log('Unsubscribed:', data.channels));
```

## Backend Usage

```python
from backend.core.websocket_manager import get_websocket_manager

ws_manager = get_websocket_manager()

# Send calculation progress
await ws_manager.send_calculation_progress(
    user_id="user123",
    calculation_id="calc_123",
    progress=50.0,
    message="Processing..."
)

# Send notification
await ws_manager.send_notification(
    user_id="user123",
    title="Update",
    message="Task completed",
    level="success"
)

# Send data update
await ws_manager.send_data_update(
    user_id="user123",
    entity_type="project",
    entity_id="proj_456",
    action="updated",
    data={"status": "active"}
)

# Broadcast to all
await ws_manager.broadcast(
    event="announcement",
    data={"message": "System update"}
)

# Send to specific user
await ws_manager.send_to_user(
    user_id="user123",
    event="custom_event",
    data={"key": "value"}
)
```

## REST API Endpoints

```bash
# Get status
GET /api/v1/websocket/status

# Get connections
GET /api/v1/websocket/connections

# Broadcast (admin only)
POST /api/v1/websocket/broadcast
{
  "event": "announcement",
  "data": {"message": "Hello"},
  "channel": "notifications"
}

# Send to user
POST /api/v1/websocket/send
{
  "user_id": "user123",
  "event": "custom",
  "data": {"key": "value"}
}

# Send notification
POST /api/v1/websocket/notify
{
  "user_id": "user123",
  "title": "Title",
  "message": "Message",
  "level": "info"
}
```

## Message Types

| Type | Description | Use Case |
|------|-------------|----------|
| `calculation_progress` | Progress updates | Long calculations |
| `calculation_complete` | Completion notification | Calculation finished |
| `calculation_error` | Error notification | Calculation failed |
| `notification` | General notifications | User alerts |
| `status_update` | Status changes | System status |
| `data_update` | Data synchronization | Real-time updates |
| `heartbeat` | Connection health | Keep-alive |

## Notification Levels

- `info` - Informational (blue)
- `success` - Success (green)
- `warning` - Warning (yellow)
- `error` - Error (red)

## Connection Management

```typescript
// Reconnection handling
socket.on('disconnect', (reason) => {
  if (reason === 'io server disconnect') {
    socket.connect();
  }
});

socket.on('reconnect', (attemptNumber) => {
  console.log('Reconnected');
});

// Heartbeat
setInterval(() => socket.emit('ping'), 30000);
```

## React Hook Example

```typescript
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

export const useWebSocket = (token: string) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      path: '/socket.io',
      auth: { token }
    });

    newSocket.on('connect', () => setConnected(true));
    newSocket.on('disconnect', () => setConnected(false));

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [token]);

  return { socket, connected };
};

// Usage
const { socket, connected } = useWebSocket(accessToken);

useEffect(() => {
  if (!socket) return;

  socket.on('notification', (data) => {
    showToast(data.title, data.message);
  });

  return () => {
    socket.off('notification');
  };
}, [socket]);
```

## Testing

```bash
# Run demo
python backend/demo_websocket.py

# Manual test with curl
curl http://localhost:8000/api/v1/websocket/test
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Cannot connect | Check backend is running, verify URL and path |
| Auth failed | Verify JWT token is valid and not expired |
| No messages | Check subscription to correct channels |
| Connection drops | Implement heartbeat and reconnection logic |

## Security Checklist

- ✅ Use JWT authentication
- ✅ Validate tokens on connection
- ✅ Implement role-based access
- ✅ Use HTTPS in production
- ✅ Rate limit message sending
- ✅ Sanitize message data
- ✅ Log security events

## Performance Tips

1. **Batch updates** - Combine multiple updates
2. **Use channels** - Target specific users
3. **Throttle messages** - Limit update frequency
4. **Compress data** - Enable compression
5. **Connection pooling** - Reuse connections
6. **Monitor metrics** - Track active connections

## URLs

- **WebSocket**: `ws://localhost:8000/socket.io`
- **API Docs**: `http://localhost:8000/api/docs`
- **Status**: `http://localhost:8000/api/v1/websocket/status`
- **Test**: `http://localhost:8000/api/v1/websocket/test`
