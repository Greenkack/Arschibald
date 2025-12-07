"""
WebSocket Demo and Testing Script

This script demonstrates how to use the WebSocket functionality
for real-time updates and progress notifications.
"""

import asyncio
import socketio
import time
from typing import Dict, Any


class WebSocketClient:
    """Demo WebSocket client"""
    
    def __init__(self, url: str = 'http://localhost:8000', token: str = None):
        self.url = url
        self.token = token
        self.sio = socketio.AsyncClient()
        self.connected = False
        
        # Setup event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect():
            print(f" Connected to WebSocket server at {self.url}")
            self.connected = True
        
        @self.sio.event
        async def disconnect():
            print(" Disconnected from WebSocket server")
            self.connected = False
        
        @self.sio.event
        async def connected(data):
            print(f" Connection confirmed: {data}")
        
        @self.sio.event
        async def calculation_progress(data):
            print(f" Calculation Progress: {data['progress']:.1f}% - {data['message']}")
        
        @self.sio.event
        async def calculation_complete(data):
            print(f" Calculation Complete: {data['calculation_id']}")
            print(f"   Result: {data['result']}")
        
        @self.sio.event
        async def calculation_error(data):
            print(f" Calculation Error: {data['error']}")
        
        @self.sio.event
        async def notification(data):
            level_emoji = {
                'info': 'ℹ',
                'success': '',
                'warning': '',
                'error': ''
            }
            emoji = level_emoji.get(data['level'], 'ℹ')
            print(f"{emoji} Notification: {data['title']}")
            print(f"   {data['message']}")
        
        @self.sio.event
        async def status_update(data):
            print(f" Status Update: {data['status']}")
            print(f"   Data: {data['data']}")
        
        @self.sio.event
        async def data_update(data):
            print(f" Data Update: {data['entity_type']} {data['action']}")
            print(f"   ID: {data['entity_id']}")
        
        @self.sio.event
        async def pong(data):
            print(f" Pong received: {data['timestamp']}")
        
        @self.sio.event
        async def error(data):
            print(f" Error: {data['message']}")
    
    async def connect(self):
        """Connect to WebSocket server"""
        auth = {'token': self.token} if self.token else None
        await self.sio.connect(self.url, auth=auth, socketio_path='/socket.io')
        await asyncio.sleep(1)  # Wait for connection to establish
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        await self.sio.disconnect()
    
    async def ping(self):
        """Send ping to server"""
        await self.sio.emit('ping')
    
    async def subscribe(self, channels: list):
        """Subscribe to channels"""
        await self.sio.emit('subscribe', {'channels': channels})
    
    async def unsubscribe(self, channels: list):
        """Unsubscribe from channels"""
        await self.sio.emit('unsubscribe', {'channels': channels})
    
    async def wait_for_messages(self, duration: int = 10):
        """Wait for messages for specified duration"""
        print(f"⏳ Waiting for messages for {duration} seconds...")
        await asyncio.sleep(duration)


async def demo_basic_connection():
    """Demo: Basic WebSocket connection"""
    print("\n" + "="*60)
    print("Demo 1: Basic WebSocket Connection")
    print("="*60)
    
    client = WebSocketClient()
    
    try:
        await client.connect()
        await client.ping()
        await asyncio.sleep(2)
        await client.disconnect()
    except Exception as e:
        print(f"Error: {e}")


async def demo_authenticated_connection():
    """Demo: Authenticated WebSocket connection"""
    print("\n" + "="*60)
    print("Demo 2: Authenticated WebSocket Connection")
    print("="*60)
    
    # Note: Replace with actual JWT token from login
    token = "your_jwt_token_here"
    
    client = WebSocketClient(token=token)
    
    try:
        await client.connect()
        await client.ping()
        await asyncio.sleep(2)
        await client.disconnect()
    except Exception as e:
        print(f"Error: {e}")


async def demo_channel_subscription():
    """Demo: Channel subscription"""
    print("\n" + "="*60)
    print("Demo 3: Channel Subscription")
    print("="*60)
    
    client = WebSocketClient()
    
    try:
        await client.connect()
        
        # Subscribe to channels
        await client.subscribe(['calculations', 'notifications'])
        await asyncio.sleep(1)
        
        # Wait for messages
        await client.wait_for_messages(5)
        
        # Unsubscribe
        await client.unsubscribe(['calculations'])
        await asyncio.sleep(1)
        
        await client.disconnect()
    except Exception as e:
        print(f"Error: {e}")


async def simulate_calculation_progress():
    """Simulate calculation with progress updates"""
    print("\n" + "="*60)
    print("Demo 4: Simulated Calculation Progress")
    print("="*60)
    
    # This would normally be done by the backend service
    # Here we're just showing what the messages would look like
    
    calculation_id = "calc_12345"
    
    print(f"Starting calculation: {calculation_id}")
    
    for progress in range(0, 101, 20):
        print(f"Progress: {progress}%")
        await asyncio.sleep(0.5)
    
    print("Calculation complete!")


async def demo_multiple_clients():
    """Demo: Multiple clients connected simultaneously"""
    print("\n" + "="*60)
    print("Demo 5: Multiple Clients")
    print("="*60)
    
    clients = []
    
    try:
        # Create and connect multiple clients
        for i in range(3):
            client = WebSocketClient()
            await client.connect()
            clients.append(client)
            print(f"Client {i+1} connected")
            await asyncio.sleep(0.5)
        
        # All clients wait for messages
        await asyncio.sleep(3)
        
        # Disconnect all clients
        for i, client in enumerate(clients):
            await client.disconnect()
            print(f"Client {i+1} disconnected")
            await asyncio.sleep(0.5)
    
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("WebSocket Demo and Testing")
    print("="*60)
    print("\nMake sure the FastAPI backend is running on http://localhost:8000")
    print("Start it with: python backend/main.py")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Run demos
        await demo_basic_connection()
        await asyncio.sleep(1)
        
        # Uncomment to run other demos
        # await demo_authenticated_connection()
        # await asyncio.sleep(1)
        
        # await demo_channel_subscription()
        # await asyncio.sleep(1)
        
        # await simulate_calculation_progress()
        # await asyncio.sleep(1)
        
        # await demo_multiple_clients()
        
        print("\n" + "="*60)
        print("All demos completed!")
        print("="*60)
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError running demos: {e}")


if __name__ == "__main__":
    print("""
    
             WebSocket Demo - Solar Calculator Pro           
    
    """)
    
    asyncio.run(main())
