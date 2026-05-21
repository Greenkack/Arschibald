/**
 * useWebSocket Hook
 * 
 * Custom hook for WebSocket communication
 */

import { useEffect, useCallback, useRef } from 'react';
import { websocketService, WebSocketEventHandler } from '@services/websocket';

export const useWebSocket = (event: string, handler: WebSocketEventHandler) => {
  const handlerRef = useRef(handler);

  // Update handler ref when it changes
  useEffect(() => {
    handlerRef.current = handler;
  }, [handler]);

  // Subscribe to event
  useEffect(() => {
    const wrappedHandler: WebSocketEventHandler = (data) => {
      handlerRef.current(data);
    };

    websocketService.on(event, wrappedHandler);

    return () => {
      websocketService.off(event, wrappedHandler);
    };
  }, [event]);

  // Emit function
  const emit = useCallback(
    (data?: any) => {
      websocketService.emit(event, data);
    },
    [event]
  );

  return { emit };
};

/**
 * Hook to manage WebSocket connection
 */
export const useWebSocketConnection = () => {
  useEffect(() => {
    websocketService.connect();

    return () => {
      websocketService.disconnect();
    };
  }, []);

  return {
    isConnected: websocketService.isConnected(),
    connect: () => websocketService.connect(),
    disconnect: () => websocketService.disconnect(),
  };
};
