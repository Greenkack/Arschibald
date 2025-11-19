# Migrating to the New API Service Layer

## Overview

This guide helps you migrate from direct Axios usage or other API patterns to the new enhanced API Service Layer.

## Why Migrate?

The new API Service Layer provides:
- ✅ Automatic token refresh
- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive error handling
- ✅ Request/response logging
- ✅ File upload/download utilities
- ✅ Batch operations
- ✅ Polling support
- ✅ Request cancellation
- ✅ Rate limiting

## Migration Steps

### Step 1: Update Imports

**Before:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});
```

**After:**
```typescript
import api from '@/services/api';
// That's it! The instance is already configured
```

### Step 2: Remove Manual Token Injection

**Before:**
```typescript
const token = localStorage.getItem('access_token');
const response = await axios.get('/endpoint', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

**After:**
```typescript
// Token is automatically injected
const response = await api.get('/endpoint');
```

### Step 3: Simplify Error Handling

**Before:**
```typescript
try {
  const response = await axios.get('/endpoint');
  return response.data;
} catch (error) {
  if (error.response?.status === 401) {
    // Manual token refresh logic
    const refreshToken = localStorage.getItem('refresh_token');
    const refreshResponse = await axios.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    localStorage.setItem('access_token', refreshResponse.data.access_token);
    // Retry original request
    return axios.get('/endpoint');
  }
  throw error;
}
```

**After:**
```typescript
try {
  const response = await api.get('/endpoint');
  return response.data;
} catch (error: APIError) {
  // Token refresh is automatic
  // Just handle the error
  console.error(error.message);
  throw error;
}
```

### Step 4: Remove Manual Retry Logic

**Before:**
```typescript
async function fetchWithRetry(url: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await axios.get(url);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

**After:**
```typescript
// Retry is automatic for retryable errors
const response = await api.get('/endpoint');

// Or use manual retry for custom scenarios
import { retryRequest } from '@/services/api';
const response = await retryRequest(() => api.get('/endpoint'));
```

### Step 5: Simplify File Uploads

**Before:**
```typescript
const formData = new FormData();
formData.append('file', file);

const response = await axios.post('/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  onUploadProgress: (progressEvent) => {
    const progress = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    setUploadProgress(progress);
  },
});
```

**After:**
```typescript
import { uploadFile } from '@/services/api';

const response = await uploadFile(
  '/upload',
  file,
  (progress) => setUploadProgress(progress)
);
```

### Step 6: Simplify File Downloads

**Before:**
```typescript
const response = await axios.get('/download', {
  responseType: 'blob',
});

const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', 'filename.pdf');
document.body.appendChild(link);
link.click();
link.remove();
window.URL.revokeObjectURL(url);
```

**After:**
```typescript
import { downloadFile } from '@/services/api';

await downloadFile('/download', 'filename.pdf');
```

### Step 7: Use Batch Operations

**Before:**
```typescript
const [result1, result2, result3] = await Promise.all([
  axios.get('/endpoint1'),
  axios.get('/endpoint2'),
  axios.get('/endpoint3'),
]);
```

**After:**
```typescript
import { batchRequest } from '@/services/api';

const results = await batchRequest([
  () => api.get('/endpoint1'),
  () => api.get('/endpoint2'),
  () => api.get('/endpoint3'),
]);
```

### Step 8: Implement Polling

**Before:**
```typescript
async function pollUntilComplete(jobId: string) {
  while (true) {
    const response = await axios.get(`/job/${jobId}`);
    if (response.data.status === 'completed') {
      return response.data;
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

**After:**
```typescript
import { pollEndpoint } from '@/services/api';

const result = await pollEndpoint(
  () => api.get(`/job/${jobId}`),
  (data) => data.status === 'completed',
  { interval: 2000 }
);
```

### Step 9: Add Request Cancellation

**Before:**
```typescript
const source = axios.CancelToken.source();

axios.get('/endpoint', {
  cancelToken: source.token,
});

// Cancel
source.cancel('Operation cancelled');
```

**After:**
```typescript
import { createCancelToken, isCancelError } from '@/services/api';

const cancelToken = createCancelToken();

try {
  await api.get('/endpoint', {
    cancelToken: cancelToken.token,
  });
} catch (error) {
  if (isCancelError(error)) {
    console.log('Request was cancelled');
  }
}

// Cancel
cancelToken.cancel('Operation cancelled');
```

### Step 10: Use Token Management

**Before:**
```typescript
// Check if authenticated
const token = localStorage.getItem('access_token');
const isAuth = !!token;

// Logout
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

**After:**
```typescript
import { isAuthenticated, clearTokens } from '@/services/api';

// Check if authenticated
const isAuth = isAuthenticated();

// Logout
clearTokens();
```

## Common Patterns

### Pattern 1: Fetch Data on Component Mount

**Before:**
```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/data', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
    } catch (error) {
      console.error(error);
    }
  };
  fetchData();
}, []);
```

**After:**
```typescript
import api from '@/services/api';

useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await api.get('/data');
      setData(response.data);
    } catch (error: APIError) {
      console.error(error.message);
    }
  };
  fetchData();
}, []);
```

### Pattern 2: Form Submission with Loading State

**Before:**
```typescript
const handleSubmit = async (formData: any) => {
  setLoading(true);
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post('/submit', formData, {
      headers: { Authorization: `Bearer ${token}` },
    });
    toast.success('Success!');
  } catch (error) {
    toast.error('Error occurred');
  } finally {
    setLoading(false);
  }
};
```

**After:**
```typescript
import api from '@/services/api';

const handleSubmit = async (formData: any) => {
  setLoading(true);
  try {
    const response = await api.post('/submit', formData);
    toast.success('Success!');
  } catch (error: APIError) {
    toast.error(error.message);
  } finally {
    setLoading(false);
  }
};
```

### Pattern 3: Search with Debounce

**Before:**
```typescript
const debouncedSearch = useCallback(
  debounce(async (query: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/search', {
        params: { q: query },
        headers: { Authorization: `Bearer ${token}` },
      });
      setResults(response.data);
    } catch (error) {
      console.error(error);
    }
  }, 300),
  []
);
```

**After:**
```typescript
import api from '@/services/api';

const debouncedSearch = useCallback(
  debounce(async (query: string) => {
    try {
      const response = await api.get('/search', {
        params: { q: query },
      });
      setResults(response.data);
    } catch (error: APIError) {
      console.error(error.message);
    }
  }, 300),
  []
);
```

### Pattern 4: Infinite Scroll / Pagination

**Before:**
```typescript
const loadMore = async () => {
  setLoading(true);
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get('/items', {
      params: { page: currentPage + 1 },
      headers: { Authorization: `Bearer ${token}` },
    });
    setItems([...items, ...response.data]);
    setCurrentPage(currentPage + 1);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};
```

**After:**
```typescript
import api from '@/services/api';

const loadMore = async () => {
  setLoading(true);
  try {
    const response = await api.get('/items', {
      params: { page: currentPage + 1 },
    });
    setItems([...items, ...response.data]);
    setCurrentPage(currentPage + 1);
  } catch (error: APIError) {
    console.error(error.message);
  } finally {
    setLoading(false);
  }
};
```

## Testing Migration

### Before (Manual Mocking)
```typescript
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

mockedAxios.get.mockResolvedValue({ data: mockData });
```

### After (Using API Service)
```typescript
import api from '@/services/api';
import MockAdapter from 'axios-mock-adapter';

const mock = new MockAdapter(api);
mock.onGet('/endpoint').reply(200, mockData);
```

## Checklist

Use this checklist to ensure complete migration:

- [ ] Replace all direct `axios` imports with `api` from `@/services/api`
- [ ] Remove manual token injection code
- [ ] Remove manual token refresh logic
- [ ] Remove manual retry logic
- [ ] Update file upload code to use `uploadFile`
- [ ] Update file download code to use `downloadFile`
- [ ] Replace `Promise.all` with `batchRequest` where appropriate
- [ ] Replace polling loops with `pollEndpoint`
- [ ] Update cancellation code to use `createCancelToken`
- [ ] Replace token management with utility functions
- [ ] Update error handling to use `APIError` type
- [ ] Update tests to use new API service
- [ ] Remove unused axios configuration code
- [ ] Test all migrated endpoints
- [ ] Verify token refresh works correctly
- [ ] Verify retry logic works for failed requests
- [ ] Check that logging appears in development mode

## Troubleshooting

### Issue: Token not being injected
**Solution**: Ensure token is stored in localStorage with key `access_token`

### Issue: Requests not retrying
**Solution**: Check that the error status code is in the retryable list (408, 429, 500, 502, 503, 504)

### Issue: Token refresh not working
**Solution**: Ensure refresh token is stored with key `refresh_token` and the refresh endpoint is correct

### Issue: CORS errors
**Solution**: Ensure backend CORS middleware is configured correctly

### Issue: Logging not appearing
**Solution**: Check that you're in development mode (`import.meta.env.DEV`)

## Getting Help

- Read the [Complete Guide](./API_SERVICE_GUIDE.md)
- Check the [Quick Reference](./API_SERVICE_QUICK_REFERENCE.md)
- Review the [Demo Component](./src/examples/ApiServiceDemo.tsx)
- Check the [Task Completion Report](../TASK_28_COMPLETE.md)

## Benefits After Migration

After migrating, you'll have:
- ✅ Less boilerplate code
- ✅ Automatic token management
- ✅ Automatic retry logic
- ✅ Better error handling
- ✅ Comprehensive logging
- ✅ Type safety with TypeScript
- ✅ Easier testing
- ✅ Better developer experience

Happy migrating! 🚀
