# Custom Hooks Quick Reference

Quick reference guide for all custom React hooks.

## useAuth

```typescript
import { useAuth } from '@hooks';

const { user, isAuthenticated, isLoading, error, login, logout, refreshUser } = useAuth();

// Login
await login({ username: 'user', password: 'pass' });

// Logout
await logout();

// Refresh user data
await refreshUser();
```

**Use Cases:**
- Login/logout functionality
- Protected routes
- User profile display
- Authentication state management

---

## useApi

```typescript
import { useApi } from '@hooks';

const { data, isLoading, error, execute, reset } = useApi(
  apiFunction,
  {
    showNotification: true,
    successMessage: 'Success!',
  }
);

// Execute API call
await execute(param1, param2);

// Reset state
reset();
```

**Use Cases:**
- Fetching data from API
- Submitting forms
- CRUD operations
- Loading states

---

## useWebSocket

```typescript
import { useWebSocket, useWebSocketConnection } from '@hooks';

// Connection management
const { isConnected, connect, disconnect } = useWebSocketConnection();

// Event handling
const { emit } = useWebSocket('event:name', (data) => {
  console.log('Received:', data);
});

// Send data
emit({ message: 'Hello' });
```

**Use Cases:**
- Real-time updates
- Progress notifications
- Live calculations
- Chat functionality

---

## useForm

```typescript
import { useForm } from '@hooks';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

const {
  register,
  handleSubmit,
  formState: { errors },
  isAutoSaving,
  lastSaved,
  manualSave,
} = useForm({
  schema,
  autoSave: true,
  autoSaveInterval: 3000,
  onAutoSave: async (data) => {
    await api.post('/save', data);
  },
  onSubmitSuccess: (data) => {
    console.log('Submitted:', data);
  },
});

// In JSX
<form onSubmit={handleSubmit}>
  <input {...register('name')} />
  {errors.name && <span>{errors.name.message}</span>}
  <button type="submit">Submit</button>
</form>
```

**Use Cases:**
- Form validation
- Auto-save drafts
- Complex forms
- Multi-step forms

---

## useDebounce

```typescript
import { useDebounce } from '@hooks';

const [searchTerm, setSearchTerm] = useState('');
const debouncedSearchTerm = useDebounce(searchTerm, 500);

useEffect(() => {
  if (debouncedSearchTerm) {
    // Perform search
    searchAPI(debouncedSearchTerm);
  }
}, [debouncedSearchTerm]);
```

**Use Cases:**
- Search inputs
- Auto-complete
- Reducing API calls
- Performance optimization

---

## Common Patterns

### Protected Route with useAuth

```typescript
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  
  return <>{children}</>;
};
```

### Data Fetching with useApi

```typescript
const DataList: React.FC = () => {
  const { data, isLoading, error, execute } = useApi(fetchData);

  useEffect(() => {
    execute();
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return null;

  return <List items={data} />;
};
```

### Real-time Updates with useWebSocket

```typescript
const LiveCalculation: React.FC = () => {
  const [progress, setProgress] = useState(0);
  
  useWebSocket('calculation:progress', (data) => {
    setProgress(data.percentage);
  });

  return <ProgressBar value={progress} />;
};
```

### Form with Auto-save

```typescript
const DraftForm: React.FC = () => {
  const { register, handleSubmit, isAutoSaving, lastSaved } = useForm({
    autoSave: true,
    onAutoSave: async (data) => {
      await saveDraft(data);
    },
  });

  return (
    <form onSubmit={handleSubmit}>
      <input {...register('title')} />
      {isAutoSaving && <span>Saving...</span>}
      {lastSaved && <span>Saved at {lastSaved.toLocaleTimeString()}</span>}
    </form>
  );
};
```

### Search with Debounce

```typescript
const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  const { data, isLoading, execute } = useApi(searchProducts);

  useEffect(() => {
    if (debouncedQuery) {
      execute(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {isLoading && <Spinner />}
      {data && <Results items={data} />}
    </>
  );
};
```

---

## Hook Combinations

### Auth + API

```typescript
const UserProfile: React.FC = () => {
  const { user } = useAuth();
  const { data, execute } = useApi(updateProfile);

  const handleUpdate = async (profileData) => {
    await execute(user.id, profileData);
  };

  return <ProfileForm onSubmit={handleUpdate} />;
};
```

### Form + API

```typescript
const CreateProject: React.FC = () => {
  const { execute } = useApi(createProject, {
    showNotification: true,
    successMessage: 'Project created!',
  });

  const { register, handleSubmit } = useForm({
    onSubmitSuccess: async (data) => {
      await execute(data);
    },
  });

  return (
    <form onSubmit={handleSubmit}>
      <input {...register('name')} />
      <button type="submit">Create</button>
    </form>
  );
};
```

### WebSocket + Debounce

```typescript
const LiveSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  const { emit } = useWebSocket('search:query', handleResults);

  useEffect(() => {
    if (debouncedQuery) {
      emit({ query: debouncedQuery });
    }
  }, [debouncedQuery]);

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
};
```

---

## Performance Tips

1. **useAuth**: Use at app root level, not in every component
2. **useApi**: Reset state when component unmounts to prevent memory leaks
3. **useWebSocket**: Use `useWebSocketConnection` once at app root
4. **useForm**: Use `defaultValues` to prevent unnecessary re-renders
5. **useDebounce**: Choose appropriate delay (300-500ms for search, 1000ms+ for expensive ops)

---

## TypeScript Tips

```typescript
// Type-safe API calls
interface Project {
  id: number;
  name: string;
}

const { data } = useApi<Project>(fetchProject);
// data is typed as Project | null

// Type-safe forms
type FormData = {
  name: string;
  email: string;
};

const { register } = useForm<FormData>({ ... });
// register is type-safe for FormData fields

// Type-safe debounce
const debouncedValue = useDebounce<string>(searchTerm, 500);
// debouncedValue is typed as string
```

---

## Error Handling

```typescript
// useAuth
const { error } = useAuth();
if (error) {
  // error is string
  console.error('Auth error:', error);
}

// useApi
const { error } = useApi(apiFunction);
if (error) {
  // error is APIError with message, details, path, status
  console.error('API error:', error.message);
}

// useForm
const { formState: { errors } } = useForm();
if (errors.fieldName) {
  // errors.fieldName.message contains validation error
  console.error('Validation error:', errors.fieldName.message);
}
```

---

## Common Gotchas

1. **useAuth**: Don't call `login` in render - use event handlers
2. **useApi**: Don't forget to call `execute()` - hook doesn't auto-fetch
3. **useWebSocket**: Ensure connection is established before emitting
4. **useForm**: Register fields before using them in JSX
5. **useDebounce**: Value updates after delay, not immediately

---

## Demo

See `src/examples/CustomHooksDemo.tsx` for complete working examples of all hooks.

---

## Documentation

See `CUSTOM_HOOKS_GUIDE.md` for detailed documentation with examples and best practices.
