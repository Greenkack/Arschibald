# API Service Layer - Complete Guide

## Overview

The API Service Layer provides a robust, feature-rich interface for communicating with the FastAPI backend. It includes automatic token refresh, retry logic, request/response logging, error handling, and various utility functions.

## Features

### 1. Automatic Token Refresh

The service automatically handles token expiration and refreshes tokens without user intervention.

```typescript
// Tokens are automatically refreshed when a 401 response is received
// No manual intervention required
const response = await api.get('/protected-endpoint');
```

**How it works:**
- When a 401 Unauthorized response is received, the interceptor attempts to refresh the token
- If refresh is successful, the original request is retried with the new token
- If refresh fails, the user is redirected to the login page
- Multiple simultaneous requests wait for a single token refresh to complete

### 2. Automatic Retry Logic

Failed requests are automatically retried with exponential backoff for retryable errors.

```typescript
// Automatic retry for 408, 429, 500, 502, 503, 504 status codes
// Up to 3 retries with exponential backoff (1s, 2s, 4s)
const response = await api.get('/api/endpoint');
```

**Retryable Status Codes:**
- 408: Request Timeout
- 429: Too Many Requests
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable
- 504: Gateway Timeout

### 3. Request/Response Logging

Comprehensive logging in development mode with timing information.

```typescript
// Logs include:
// - Request method, URL, headers, data, params
// - Response status, data, headers
// - Request duration in milliseconds
```

**Example Console Output:**
```
[API Request] GET /api/v1/projects
  Headers: { Authorization: "Bearer ...", ... }
  Data: undefined
  Params: { page: 1, limit: 10 }

[API Response] GET /api/v1/projects (245ms)
  Status: 200
  Data: { projects: [...], total: 50 }
  Headers: { content-type: "application/json", ... }
```

### 4. Error Handling

Consistent error handling with structured error objects.

```typescript
try {
  const response = await api.get('/api/endpoint');
} catch (error: APIError) {
  console.error(error.message);    // User-friendly message
  console.error(error.status);     // HTTP status code
  console.error(error.details);    // Additional error details
  console.error(error.path);       // API endpoint path
}
```

## API Methods

### Basic HTTP Methods

```typescript
import api from '@/services/api';

// GET request
const response = await api.get('/endpoint', { params: { id: 1 } });

// POST request
const response = await api.post('/endpoint', { data: 'value' });

// PUT request
const response = await api.put('/endpoint/1', { data: 'updated' });

// PATCH request
const response = await api.patch('/endpoint/1', { field: 'value' });

// DELETE request
const response = await api.delete('/endpoint/1');
```

### File Upload

```typescript
import { uploadFile } from '@/services/api';

const file = document.querySelector('input[type="file"]').files[0];

const response = await uploadFile(
  '/api/v1/upload',
  file,
  (progress) => {
    console.log(`Upload progress: ${progress}%`);
  }
);
```

### File Download

```typescript
import { downloadFile } from '@/services/api';

await downloadFile('/api/v1/download/report', 'report.pdf');
```

### Manual Retry

```typescript
import { retryRequest } from '@/services/api';

const data = await retryRequest(
  () => api.get('/unstable-endpoint'),
  3,    // max retries
  1000  // initial delay in ms
);
```

### Custom Retry Configuration

```typescript
import { requestWithRetry, configureRetry } from '@/services/api';

const data = await requestWithRetry(
  () => api.get('/endpoint'),
  configureRetry({
    maxRetries: 5,
    retryDelay: 2000,
    retryableStatuses: [500, 502, 503],
  })
);
```

### Batch Requests (Parallel)

```typescript
import { batchRequest } from '@/services/api';

const results = await batchRequest([
  () => api.get('/endpoint1'),
  () => api.get('/endpoint2'),
  () => api.get('/endpoint3'),
]);

console.log(results); // [data1, data2, data3]
```

### Sequential Requests

```typescript
import { sequentialRequest } from '@/services/api';

const results = await sequentialRequest([
  () => api.post('/step1', { data: 'value1' }),
  () => api.post('/step2', { data: 'value2' }),
  () => api.post('/step3', { data: 'value3' }),
]);
```

### Polling

```typescript
import { pollEndpoint } from '@/services/api';

const result = await pollEndpoint(
  () => api.get('/job/status/123'),
  (data) => data.status === 'completed',
  {
    interval: 2000,      // Poll every 2 seconds
    maxAttempts: 30,     // Maximum 30 attempts
    timeout: 60000,      // Timeout after 60 seconds
  }
);
```

### Request Cancellation

```typescript
import { createCancelToken, isCancelError } from '@/services/api';

const cancelToken = createCancelToken();

try {
  const response = await api.get('/long-request', {
    cancelToken: cancelToken.token,
  });
} catch (error) {
  if (isCancelError(error)) {
    console.log('Request was cancelled');
  }
}

// Cancel the request
cancelToken.cancel('User cancelled the request');
```

### Rate-Limited Requests

```typescript
import { requestQueue } from '@/services/api';

// Add requests to queue (max 10 requests per second)
const result1 = await requestQueue.add(() => api.get('/endpoint1'));
const result2 = await requestQueue.add(() => api.get('/endpoint2'));
const result3 = await requestQueue.add(() => api.get('/endpoint3'));
```

## Token Management

### Check Authentication Status

```typescript
import { isAuthenticated } from '@/services/api';

if (isAuthenticated()) {
  console.log('User is authenticated');
}
```

### Get Current Token

```typescript
import { getAccessToken } from '@/services/api';

const token = getAccessToken();
```

### Set Tokens

```typescript
import { setAccessToken, setRefreshToken } from '@/services/api';

setAccessToken('new-access-token');
setRefreshToken('new-refresh-token');
```

### Clear Tokens (Logout)

```typescript
import { clearTokens } from '@/services/api';

clearTokens();
```

## Using the API Service Object

```typescript
import { apiService } from '@/services/api';

// Access the Axios instance
const response = await apiService.instance.get('/endpoint');

// Use utility methods
apiService.clearTokens();
const isAuth = apiService.isAuthenticated();
const token = apiService.getAccessToken();

// Use request utilities
const data = await apiService.retry(() => api.get('/endpoint'));
const results = await apiService.batch([
  () => api.get('/endpoint1'),
  () => api.get('/endpoint2'),
]);

// File operations
await apiService.upload('/upload', file, (progress) => console.log(progress));
await apiService.download('/download', 'filename.pdf');

// Cancellation
const cancelToken = apiService.createCancelToken();
if (apiService.isCancelError(error)) {
  console.log('Cancelled');
}
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Timeout Configuration

```typescript
import api from '@/services/api';

// Change timeout for specific request
const response = await api.get('/endpoint', {
  timeout: 60000, // 60 seconds
});
```

### Custom Headers

```typescript
import api from '@/services/api';

const response = await api.post('/endpoint', data, {
  headers: {
    'X-Custom-Header': 'value',
  },
});
```

## Error Handling Best Practices

### Basic Error Handling

```typescript
try {
  const response = await api.get('/endpoint');
  // Handle success
} catch (error: APIError) {
  // Handle error
  console.error(error.message);
}
```

### Specific Error Handling

```typescript
try {
  const response = await api.get('/endpoint');
} catch (error: APIError) {
  if (error.status === 404) {
    console.error('Resource not found');
  } else if (error.status === 403) {
    console.error('Access forbidden');
  } else if (error.status === 500) {
    console.error('Server error');
  } else {
    console.error('Unknown error:', error.message);
  }
}
```

### With Toast Notifications

```typescript
import { toast } from 'react-toastify';

try {
  const response = await api.post('/endpoint', data);
  toast.success('Operation successful!');
} catch (error: APIError) {
  toast.error(error.message);
}
```

## Advanced Usage

### Custom Interceptors

```typescript
import api from '@/services/api';

// Add custom request interceptor
api.interceptors.request.use(
  (config) => {
    // Modify config before request is sent
    config.headers['X-Custom-Header'] = 'value';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add custom response interceptor
api.interceptors.response.use(
  (response) => {
    // Modify response data
    return response;
  },
  (error) => {
    // Handle error
    return Promise.reject(error);
  }
);
```

### Request Transformation

```typescript
import api from '@/services/api';

const response = await api.post('/endpoint', data, {
  transformRequest: [(data, headers) => {
    // Transform request data
    return JSON.stringify(data);
  }],
  transformResponse: [(data) => {
    // Transform response data
    return JSON.parse(data);
  }],
});
```

### Progress Tracking

```typescript
import api from '@/services/api';

const response = await api.post('/upload', formData, {
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    console.log(`Upload: ${percentCompleted}%`);
  },
  onDownloadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    console.log(`Download: ${percentCompleted}%`);
  },
});
```

## Testing

### Mocking API Calls

```typescript
import api from '@/services/api';
import MockAdapter from 'axios-mock-adapter';

const mock = new MockAdapter(api);

// Mock GET request
mock.onGet('/endpoint').reply(200, {
  data: 'mocked data',
});

// Mock POST request
mock.onPost('/endpoint').reply(201, {
  id: 1,
  message: 'Created',
});

// Mock error
mock.onGet('/error').reply(500, {
  error: {
    message: 'Internal server error',
  },
});
```

## Performance Tips

1. **Use batch requests** for multiple independent API calls
2. **Implement request cancellation** for long-running requests that may be abandoned
3. **Use polling sparingly** and with appropriate intervals
4. **Leverage the request queue** for rate-limited APIs
5. **Cache responses** when appropriate using a caching library
6. **Use pagination** for large datasets
7. **Implement debouncing** for search/filter requests

## Troubleshooting

### Token Refresh Issues

If token refresh is not working:
1. Ensure refresh token is stored in localStorage
2. Check that the refresh endpoint is correct
3. Verify the refresh token is not expired
4. Check browser console for error messages

### Retry Not Working

If automatic retry is not working:
1. Check that the error status code is in the retryable list
2. Verify the request is not marked with `_retry: true`
3. Check console logs for retry attempts
4. Ensure the backend is returning proper status codes

### CORS Issues

If you encounter CORS errors:
1. Ensure backend CORS middleware is configured correctly
2. Check that the API base URL is correct
3. Verify credentials are being sent if required
4. Check browser console for specific CORS error messages

## Requirements Validation

This implementation satisfies the following requirements:

- ✅ **4.1**: RESTful API communication with consistent error handling
- ✅ **4.3**: Comprehensive error handling with structured error responses
- ✅ **Request/Response Logging**: Detailed logging with timing information
- ✅ **Automatic Token Refresh**: Seamless token refresh on 401 errors
- ✅ **Retry Logic**: Automatic retry with exponential backoff
- ✅ **Error Handling**: Consistent error structure and handling
- ✅ **Additional Features**: File upload/download, batch requests, polling, cancellation, rate limiting

## Next Steps

After implementing the API Service Layer:
1. Create custom hooks (Task 29) that use this API service
2. Implement specific API endpoints for each feature
3. Add integration tests for API calls
4. Set up error monitoring and logging service
5. Implement request/response caching where appropriate
