# Custom Hooks Guide

This guide provides comprehensive documentation for all custom React hooks in the Solar Calculator Pro application.

## Table of Contents

1. [useAuth](#useauth)
2. [useApi](#useapi)
3. [useWebSocket](#usewebsocket)
4. [useForm](#useform)
5. [useDebounce](#usedebounce)

---

## useAuth

**Purpose:** Manages authentication state and operations.

### Import

```typescript
import { useAuth } from '@hooks';
```

### API

```typescript
const {
  user,              // Current user object or null
  isAuthenticated,   // Boolean indicating if user is logged in
  isLoading,         // Boolean indicating if auth operation is in progress
  error,             // Error message if auth operation failed
  login,             // Function to log in user
  logout,            // Function to log out user
  refreshUser,       // Function to refresh user data
} = useAuth();
```

### Usage Example

```typescript
import React, { useState } from 'react';
import { useAuth } from '@hooks';

const LoginPage: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await login({ username, password });
    if (success) {
      // Redirect to dashboard
      window.location.href = '/dashboard';
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
};
```

### Features

- ✅ Automatic token management
- ✅ User state persistence
- ✅ Error handling with notifications
- ✅ Loading states
- ✅ Integration with auth store

---

## useApi

**Purpose:** Handles API calls with automatic loading and error state management.

### Import

```typescript
import { useApi } from '@hooks';
```

### API

```typescript
const {
  data,       // Response data from API call
  isLoading,  // Boolean indicating if request is in progress
  error,      // Error object if request failed
  execute,    // Function to execute the API call
  reset,      // Function to reset state
} = useApi(apiFunction, options);
```

### Parameters

- `apiFunction`: Async function that makes the API call
- `options`: Configuration object
  - `showNotification?: boolean` - Show toast notifications (default: false)
  - `successMessage?: string` - Success notification message

### Usage Example

```typescript
import React, { useState } from 'react';
import { useApi } from '@hooks';
import { projectService } from '@services';

const ProjectDetails: React.FC = () => {
  const [projectId, setProjectId] = useState('1');

  const {
    data: project,
    isLoading,
    error,
    execute,
  } = useApi(projectService.getProject, {
    showNotification: true,
    successMessage: 'Project loaded successfully!',
  });

  const loadProject = () => {
    execute(projectId);
  };

  return (
    <div>
      <input
        value={projectId}
        onChange={(e) => setProjectId(e.target.value)}
      />
      <button onClick={loadProject} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Load Project'}
      </button>

      {error && <div className="error">{error.message}</div>}
      
      {project && (
        <div>
          <h2>{project.name}</h2>
          <p>Status: {project.status}</p>
        </div>
      )}
    </div>
  );
};
```

### Features

- ✅ Automatic loading state management
- ✅ Error handling with detailed error objects
- ✅ Optional toast notifications
- ✅ Reset functionality
- ✅ TypeScript generic support for type safety

---

## useWebSocket

**Purpose:** Manages WebSocket connections and real-time communication.

### Import

```typescript
import { useWebSocket, useWebSocketConnection } from '@hooks';
```

### API

#### useWebSocket

```typescript
const { emit } = useWebSocket(event, handler);
```

- `event`: WebSocket event name to listen to
- `handler`: Callback function to handle incoming data
- `emit`: Function to send data to the server

#### useWebSocketConnection

```typescript
const {
  isConnected,  // Boolean indicating connection status
  connect,      // Function to connect to WebSocket
  disconnect,   // Function to disconnect from WebSocket
} = useWebSocketConnection();
```

### Usage Example

```typescript
import React, { useState } from 'react';
import { useWebSocket, useWebSocketConnection } from '@hooks';

const CalculationMonitor: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const { isConnected } = useWebSocketConnection();

  // Listen for calculation progress
  useWebSocket('calculation:progress', (data) => {
    setProgress(data.percentage);
  });

  // Listen for calculation results
  const { emit: requestCalculation } = useWebSocket(
    'calculation:result',
    (data) => {
      setResults(data);
    }
  );

  const startCalculation = () => {
    requestCalculation({
      roofArea: 50,
      moduleType: 'standard',
    });
  };

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      <button onClick={startCalculation} disabled={!isConnected}>
        Start Calculation
      </button>
      {progress > 0 && <div>Progress: {progress}%</div>}
      {results && <pre>{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
};
```

### Features

- ✅ Automatic connection management
- ✅ Event-based communication
- ✅ Multiple event listeners
- ✅ Bidirectional communication
- ✅ Connection status tracking

---

## useForm

**Purpose:** Enhanced form management with validation, auto-save, and error handling.

### Import

```typescript
import { useForm } from '@hooks';
import { z } from 'zod';
```

### API

```typescript
const {
  register,       // Register form fields
  handleSubmit,   // Submit handler
  formState,      // Form state (errors, isDirty, etc.)
  isAutoSaving,   // Boolean indicating if auto-save is in progress
  lastSaved,      // Date of last auto-save
  manualSave,     // Function to trigger manual save
  ...rest,        // All other react-hook-form methods
} = useForm<FormData>(options);
```

### Options

```typescript
interface UseFormOptions {
  schema?: ZodSchema;              // Zod validation schema
  autoSave?: boolean;              // Enable auto-save (default: false)
  autoSaveInterval?: number;       // Auto-save delay in ms (default: 5000)
  onAutoSave?: (data) => Promise<void>;  // Auto-save callback
  onSubmitSuccess?: (data) => void;      // Success callback
  onSubmitError?: (error) => void;       // Error callback
  showSuccessToast?: boolean;      // Show success notification (default: true)
  showErrorToast?: boolean;        // Show error notification (default: true)
  successMessage?: string;         // Custom success message
  errorMessage?: string;           // Custom error message
  defaultValues?: Partial<FormData>;  // Default form values
}
```

### Usage Example

```typescript
import React from 'react';
import { useForm } from '@hooks';
import { z } from 'zod';

// Define validation schema
const solarFormSchema = z.object({
  roofArea: z.number().min(10, 'Roof area must be at least 10 m²'),
  roofType: z.enum(['flat', 'gable', 'hip']),
  annualConsumption: z.number().min(1000),
  location: z.string().min(2),
});

type SolarFormData = z.infer<typeof solarFormSchema>;

const SolarCalculatorForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    isAutoSaving,
    lastSaved,
  } = useForm<SolarFormData>({
    schema: solarFormSchema,
    defaultValues: {
      roofArea: 50,
      roofType: 'flat',
      annualConsumption: 4000,
      location: 'Berlin',
    },
    autoSave: true,
    autoSaveInterval: 3000,
    onAutoSave: async (data) => {
      await api.post('/api/v1/solar/save-draft', data);
    },
    onSubmitSuccess: (data) => {
      console.log('Form submitted:', data);
    },
  });

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Roof Area (m²):</label>
        <input
          type="number"
          {...register('roofArea', { valueAsNumber: true })}
        />
        {errors.roofArea && (
          <span className="error">{errors.roofArea.message}</span>
        )}
      </div>

      <div>
        <label>Roof Type:</label>
        <select {...register('roofType')}>
          <option value="flat">Flat</option>
          <option value="gable">Gable</option>
          <option value="hip">Hip</option>
        </select>
        {errors.roofType && (
          <span className="error">{errors.roofType.message}</span>
        )}
      </div>

      <button type="submit">Calculate</button>

      {isAutoSaving && <span>Auto-saving...</span>}
      {isDirty && <span>Unsaved changes</span>}
      {lastSaved && <span>Last saved: {lastSaved.toLocaleTimeString()}</span>}
    </form>
  );
};
```

### Features

- ✅ Zod schema validation
- ✅ Auto-save with configurable interval
- ✅ Manual save trigger
- ✅ Toast notifications
- ✅ Form state tracking (dirty, errors, etc.)
- ✅ TypeScript type safety
- ✅ Integration with react-hook-form

---

## useDebounce

**Purpose:** Debounces values to reduce unnecessary operations (e.g., API calls during typing).

### Import

```typescript
import { useDebounce } from '@hooks';
```

### API

```typescript
const debouncedValue = useDebounce(value, delay);
```

- `value`: The value to debounce
- `delay`: Delay in milliseconds (default: 500)

### Usage Example

```typescript
import React, { useState, useEffect } from 'react';
import { useDebounce } from '@hooks';
import { productService } from '@services';

const ProductSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounce search term
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Perform search when debounced value changes
  useEffect(() => {
    if (debouncedSearchTerm) {
      setIsSearching(true);
      productService
        .search(debouncedSearchTerm)
        .then((data) => {
          setResults(data);
          setIsSearching(false);
        })
        .catch((error) => {
          console.error('Search error:', error);
          setIsSearching(false);
        });
    } else {
      setResults([]);
    }
  }, [debouncedSearchTerm]);

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search products..."
      />

      {isSearching && <div>Searching...</div>}

      <ul>
        {results.map((product) => (
          <li key={product.id}>{product.name}</li>
        ))}
      </ul>
    </div>
  );
};
```

### Features

- ✅ Reduces API calls during typing
- ✅ Configurable delay
- ✅ Automatic cleanup
- ✅ TypeScript generic support

---

## Best Practices

### 1. useAuth

- Always check `isAuthenticated` before rendering protected content
- Handle loading states to prevent UI flicker
- Use `refreshUser` after profile updates

### 2. useApi

- Use TypeScript generics for type-safe responses
- Enable notifications for user-facing operations
- Reset state when component unmounts if needed

### 3. useWebSocket

- Always check `isConnected` before emitting events
- Use `useWebSocketConnection` at the app root level
- Clean up listeners by using the hook in components that unmount

### 4. useForm

- Define Zod schemas for all forms
- Use auto-save for long forms to prevent data loss
- Provide meaningful error messages in schemas

### 5. useDebounce

- Use 300-500ms delay for search inputs
- Use 1000ms+ delay for expensive operations
- Combine with `useEffect` for side effects

---

## Testing

### Example Test for useDebounce

```typescript
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '@hooks';

describe('useDebounce', () => {
  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    // Change value
    rerender({ value: 'updated', delay: 500 });

    // Value should not change immediately
    expect(result.current).toBe('initial');

    // Wait for debounce delay
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 600));
    });

    // Value should now be updated
    expect(result.current).toBe('updated');
  });
});
```

---

## Troubleshooting

### useAuth not persisting login

- Check if `authStore` is properly configured
- Verify token is being stored in localStorage
- Ensure API endpoints are returning correct data

### useApi not showing notifications

- Verify `showNotification: true` is set in options
- Check if toast container is rendered in app root
- Ensure `useUIStore` is properly initialized

### useWebSocket not connecting

- Check if backend WebSocket server is running
- Verify WebSocket URL in configuration
- Check browser console for connection errors

### useForm auto-save not working

- Ensure `autoSave: true` is set
- Verify `onAutoSave` callback is provided
- Check if form is marked as dirty (`isDirty`)

### useDebounce not debouncing

- Verify delay value is reasonable (> 0)
- Check if value is actually changing
- Ensure component is not re-rendering excessively

---

## Additional Resources

- [React Hook Form Documentation](https://react-hook-form.com/)
- [Zod Documentation](https://zod.dev/)
- [Socket.IO Client Documentation](https://socket.io/docs/v4/client-api/)
- [React Hooks Documentation](https://react.dev/reference/react)

---

## Support

For questions or issues with custom hooks, please:

1. Check this documentation
2. Review the demo examples in `src/examples/CustomHooksDemo.tsx`
3. Check the implementation in `src/hooks/`
4. Contact the development team
