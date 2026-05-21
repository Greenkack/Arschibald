# API Service Layer - Quick Reference

## Import

```typescript
import api, { apiService } from '@/services/api';
```

## Basic Requests

```typescript
// GET
const response = await api.get('/endpoint');

// POST
const response = await api.post('/endpoint', data);

// PUT
const response = await api.put('/endpoint/1', data);

// PATCH
const response = await api.patch('/endpoint/1', data);

// DELETE
const response = await api.delete('/endpoint/1');
```

## File Operations

```typescript
import { uploadFile, downloadFile } from '@/services/api';

// Upload
await uploadFile('/upload', file, (progress) => console.log(progress));

// Download
await downloadFile('/download', 'filename.pdf');
```

## Retry Logic

```typescript
import { retryRequest, requestWithRetry } from '@/services/api';

// Simple retry
await retryRequest(() => api.get('/endpoint'), 3, 1000);

// Custom retry
await requestWithRetry(
  () => api.get('/endpoint'),
  { maxRetries: 5, retryDelay: 2000 }
);
```

## Batch & Sequential

```typescript
import { batchRequest, sequentialRequest } from '@/services/api';

// Parallel
const results = await batchRequest([
  () => api.get('/endpoint1'),
  () => api.get('/endpoint2'),
]);

// Sequential
const results = await sequentialRequest([
  () => api.post('/step1', data1),
  () => api.post('/step2', data2),
]);
```

## Polling

```typescript
import { pollEndpoint } from '@/services/api';

const result = await pollEndpoint(
  () => api.get('/job/123'),
  (data) => data.status === 'completed',
  { interval: 2000, maxAttempts: 30 }
);
```

## Cancellation

```typescript
import { createCancelToken, isCancelError } from '@/services/api';

const cancelToken = createCancelToken();

try {
  await api.get('/endpoint', { cancelToken: cancelToken.token });
} catch (error) {
  if (isCancelError(error)) {
    console.log('Cancelled');
  }
}

cancelToken.cancel();
```

## Token Management

```typescript
import { 
  isAuthenticated, 
  getAccessToken, 
  setAccessToken, 
  clearTokens 
} from '@/services/api';

if (isAuthenticated()) {
  const token = getAccessToken();
}

setAccessToken('new-token');
clearTokens();
```

## Error Handling

```typescript
try {
  const response = await api.get('/endpoint');
} catch (error: APIError) {
  console.error(error.message);  // User-friendly message
  console.error(error.status);   // HTTP status code
  console.error(error.details);  // Additional details
}
```

## Features

- ✅ Automatic token refresh on 401
- ✅ Automatic retry with exponential backoff
- ✅ Request/response logging with timing
- ✅ File upload with progress tracking
- ✅ File download
- ✅ Batch requests (parallel)
- ✅ Sequential requests
- ✅ Polling with timeout
- ✅ Request cancellation
- ✅ Rate limiting queue
- ✅ Comprehensive error handling

## Automatic Features

### Token Refresh
- Automatically refreshes expired tokens
- Retries original request with new token
- Redirects to login if refresh fails

### Retry Logic
- Retries on: 408, 429, 500, 502, 503, 504
- Up to 3 attempts
- Exponential backoff: 1s, 2s, 4s

### Logging (Dev Mode)
- Request: method, URL, headers, data, params
- Response: status, data, headers, duration
- Errors: status, message, details, duration

## Configuration

```env
# .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Common Patterns

### With Toast Notifications

```typescript
import { toast } from 'react-toastify';

try {
  await api.post('/endpoint', data);
  toast.success('Success!');
} catch (error: APIError) {
  toast.error(error.message);
}
```

### With Loading State

```typescript
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  setLoading(true);
  try {
    const response = await api.get('/endpoint');
    setData(response.data);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};
```

### With Cancellation on Unmount

```typescript
useEffect(() => {
  const cancelToken = createCancelToken();
  
  const fetchData = async () => {
    try {
      const response = await api.get('/endpoint', {
        cancelToken: cancelToken.token,
      });
      setData(response.data);
    } catch (error) {
      if (!isCancelError(error)) {
        console.error(error);
      }
    }
  };
  
  fetchData();
  
  return () => {
    cancelToken.cancel();
  };
}, []);
```

## Requirements Met

- ✅ 4.1: RESTful API communication
- ✅ 4.3: Comprehensive error handling
- ✅ Request/response logging
- ✅ Automatic token refresh
- ✅ Retry logic for failed requests
- ✅ API error handling
