/**
 * Services Index
 * 
 * Central export point for all services
 */

export { UniversalDataService, universalDataService } from './UniversalDataService';
export type { DataWithPDFBytes, DownloadOptions } from './UniversalDataService';

export { default as api, uploadFile, downloadFile, retryRequest } from './api';
export type { APIError } from './api';

export { authService } from './auth';
export type { LoginRequest, TokenResponse, User } from './auth';

export { websocketService } from './websocket';
export type { WebSocketEventHandler } from './websocket';
