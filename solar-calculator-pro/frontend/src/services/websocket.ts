/**
 * WebSocket Service
 * 
 * Handles real-time communication with the backend using Socket.IO.
 */

import { io, Socket } from 'socket.io-client';

export type WebSocketEventHandler = (data: any) => void;

/**
 * WebSocket service class
 */
class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.socket?.connected) {
      console.log('[WebSocket] Already connected');
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const token = localStorage.getItem('access_token');

    this.socket = io(wsUrl, {
      auth: {
        token,
      },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    this.setupEventListeners();
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('[WebSocket] Disconnected');
    }
  }

  /**
   * Setup default event listeners
   */
  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
    });

    this.socket.on('error', (error) => {
      console.error('[WebSocket] Error:', error);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('[WebSocket] Reconnected after', attemptNumber, 'attempts');
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('[WebSocket] Reconnection error:', error);
    });
  }

  /**
   * Subscribe to an event
   */
  on(event: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }

    this.eventHandlers.get(event)!.add(handler);

    if (this.socket) {
      this.socket.on(event, handler);
    }
  }

  /**
   * Unsubscribe from an event
   */
  off(event: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.eventHandlers.delete(event);
      }
    }

    if (this.socket) {
      this.socket.off(event, handler);
    }
  }

  /**
   * Emit an event
   */
  emit(event: string, data?: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('[WebSocket] Cannot emit event, not connected');
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const websocketService = new WebSocketService();
