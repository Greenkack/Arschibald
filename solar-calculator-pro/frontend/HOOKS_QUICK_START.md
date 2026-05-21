# Custom Hooks Quick Start

Get started with custom hooks in 5 minutes!

## Installation

Hooks are already installed and ready to use. No additional setup required.

## Import

```typescript
import { useAuth, useApi, useWebSocket, useForm, useDebounce } from '@hooks';
```

## 1. Authentication (useAuth)

```typescript
import { useAuth } from '@hooks';

function LoginPage() {
  const { login, isLoading } = useAuth();
  
  const handleLogin = async () => {
    await login({ username: 'user', password: 'pass' });
  };
  
  return (
    <button onClick={handleLogin} disabled={isLoading}>
      {isLoading ? 'Logging in...' : 'Login'}
    </button>
  );
}
```

## 2. API Calls (useApi)

```typescript
import { useApi } from '@hooks';

function ProjectList() {
  const { data, isLoading, execute } = useApi(fetchProjects);
  
  useEffect(() => {
    execute();
  }, []);
  
  if (isLoading) return <div>Loading...</div>;
  return <div>{data?.map(p => <div key={p.id}>{p.name}</div>)}</div>;
}
```

## 3. Real-time Updates (useWebSocket)

```typescript
import { useWebSocket } from '@hooks';

function LiveProgress() {
  const [progress, setProgress] = useState(0);
  
  useWebSocket('calculation:progress', (data) => {
    setProgress(data.percentage);
  });
  
  return <div>Progress: {progress}%</div>;
}
```

## 4. Forms (useForm)

```typescript
import { useForm } from '@hooks';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

function ContactForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    schema,
    onSubmitSuccess: (data) => console.log(data),
  });
  
  return (
    <form onSubmit={handleSubmit}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}
      <button type="submit">Submit</button>
    </form>
  );
}
```

## 5. Search (useDebounce)

```typescript
import { useDebounce } from '@hooks';

function SearchBar() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  
  useEffect(() => {
    if (debouncedQuery) {
      searchAPI(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

## Demo

Run the interactive demo:

```bash
# The demo is available at:
# frontend/src/examples/CustomHooksDemo.tsx
```

## Documentation

- **Full Guide:** `frontend/CUSTOM_HOOKS_GUIDE.md`
- **Quick Reference:** `frontend/CUSTOM_HOOKS_QUICK_REFERENCE.md`

## Common Patterns

### Protected Route
```typescript
const { isAuthenticated, isLoading } = useAuth();

if (isLoading) return <Spinner />;
if (!isAuthenticated) return <Navigate to="/login" />;
return <>{children}</>;
```

### Form with Auto-save
```typescript
const { register, handleSubmit, isAutoSaving } = useForm({
  autoSave: true,
  onAutoSave: async (data) => await saveDraft(data),
});
```

### Search with Debounce
```typescript
const [query, setQuery] = useState('');
const debouncedQuery = useDebounce(query, 500);

useEffect(() => {
  if (debouncedQuery) searchAPI(debouncedQuery);
}, [debouncedQuery]);
```

## Tips

1. **useAuth:** Use at app root level
2. **useApi:** Always handle loading and error states
3. **useWebSocket:** Check connection before emitting
4. **useForm:** Define Zod schemas for validation
5. **useDebounce:** Use 300-500ms for search, 1000ms+ for expensive ops

## Need Help?

- Check the comprehensive guide: `CUSTOM_HOOKS_GUIDE.md`
- Review the demo: `src/examples/CustomHooksDemo.tsx`
- See quick reference: `CUSTOM_HOOKS_QUICK_REFERENCE.md`

---

**Ready to use!** All hooks are production-ready and fully documented.
