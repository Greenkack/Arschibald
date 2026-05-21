# State Management Quick Reference

## Import Stores

```typescript
import { useAuthStore, useUIStore, useProjectStore } from '@/store';
```

## Auth Store

### Get State
```typescript
const { user, isAuthenticated, isLoading, error } = useAuthStore();
```

### Actions
```typescript
const { setUser, setLoading, setError, logout } = useAuthStore();

// Login
setUser({ id: 1, username: 'john', email: 'john@example.com' });

// Logout
logout();

// Set loading
setLoading(true);

// Set error
setError('Login failed');
```

### Selective Access
```typescript
// Only subscribe to what you need
const user = useAuthStore(state => state.user);
const isAuthenticated = useAuthStore(state => state.isAuthenticated);
```

---

## UI Store

### Get State
```typescript
const { 
  sidebarCollapsed, 
  sidebarVisible,
  theme, 
  globalLoading,
  loadingMessage,
  notifications 
} = useUIStore();
```

### Actions
```typescript
const { 
  toggleSidebar,
  setSidebarCollapsed,
  setSidebarVisible,
  setTheme,
  setGlobalLoading,
  addNotification,
  removeNotification,
  clearNotifications
} = useUIStore();

// Sidebar
toggleSidebar();
setSidebarCollapsed(true);
setSidebarVisible(false);

// Theme
setTheme('dark'); // 'light' | 'dark' | 'auto'

// Loading
setGlobalLoading(true, 'Saving...');
setGlobalLoading(false);

// Notifications (auto-remove after 5s)
addNotification({
  type: 'success', // 'success' | 'error' | 'warning' | 'info'
  title: 'Success',
  message: 'Operation completed!'
});

removeNotification('notification-id');
clearNotifications();
```

---

## Project Store

### Get State
```typescript
const { 
  projects, 
  currentProject, 
  isLoading, 
  error 
} = useProjectStore();
```

### Actions
```typescript
const { 
  setProjects,
  setCurrentProject,
  addProject,
  updateProject,
  deleteProject,
  setLoading,
  setError,
  clearError
} = useProjectStore();

// Set projects list
setProjects([project1, project2]);

// Set current project
setCurrentProject(project);

// Add project
addProject({
  id: 1,
  name: 'Solar Project',
  customerName: 'John Doe',
  projectType: 'solar',
  status: 'draft',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  data: {}
});

// Update project
updateProject(1, { name: 'Updated Name', status: 'active' });

// Delete project
deleteProject(1);

// Loading and errors
setLoading(true);
setError('Failed to load projects');
clearError();
```

---

## Common Patterns

### Loading State Pattern
```typescript
const handleSave = async () => {
  const { setLoading, setError } = useUIStore.getState();
  
  setLoading(true);
  setError(null);
  
  try {
    await saveData();
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

### Notification Pattern
```typescript
const { addNotification } = useUIStore();

try {
  await saveData();
  addNotification({
    type: 'success',
    title: 'Success',
    message: 'Data saved successfully!'
  });
} catch (error) {
  addNotification({
    type: 'error',
    title: 'Error',
    message: error.message
  });
}
```

### Optimistic Update Pattern
```typescript
const handleUpdate = async (id, updates) => {
  const { updateProject, projects } = useProjectStore.getState();
  const original = projects.find(p => p.id === id);
  
  // Optimistic update
  updateProject(id, updates);
  
  try {
    await api.put(`/projects/${id}`, updates);
  } catch (error) {
    // Rollback
    if (original) updateProject(id, original);
    throw error;
  }
};
```

### Selector Pattern
```typescript
// Computed value
const activeProjects = useProjectStore(
  state => state.projects.filter(p => p.status === 'active')
);

// Derived value
const projectCount = useProjectStore(
  state => state.projects.length
);
```

---

## Persistence

### Auth Store
- **Persisted**: `user`, `isAuthenticated`
- **Storage Key**: `auth-storage`

### UI Store
- **Persisted**: `sidebarCollapsed`, `theme`
- **Storage Key**: `ui-storage`

### Project Store
- **Not Persisted** (loaded from API)

---

## TypeScript Types

```typescript
// Auth
interface User {
  id: number;
  username: string;
  email: string;
  role?: string;
}

// Project
interface Project {
  id: number;
  name: string;
  customerName: string;
  customerEmail?: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
  data: Record<string, any>;
}

// Notification
interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;
}
```

---

## Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/store';

// Reset store before test
beforeEach(() => {
  useAuthStore.setState({ user: null, isAuthenticated: false });
});

// Test action
it('should set user', () => {
  const { result } = renderHook(() => useAuthStore());
  
  act(() => {
    result.current.setUser({ id: 1, username: 'test' });
  });

  expect(result.current.isAuthenticated).toBe(true);
});
```

---

## Performance Tips

1. **Selective Subscription**: Only subscribe to needed state
   ```typescript
   const user = useAuthStore(state => state.user); // ✅
   const store = useAuthStore(); // ❌ subscribes to everything
   ```

2. **Memoize Selectors**: For expensive computations
   ```typescript
   const sortedProjects = useMemo(() => 
     [...projects].sort((a, b) => a.name.localeCompare(b.name)),
     [projects]
   );
   ```

3. **Split Large Stores**: Keep stores focused and small

4. **Avoid Large Objects**: Store only what you need

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| State not persisting | Check `partialize` config and localStorage |
| State not updating | Use actions, not direct mutation |
| Too many re-renders | Use selective subscription with selectors |
| Stale data | Ensure you're not caching API responses too long |

---

## Resources

- 📚 [Full Guide](./STATE_MANAGEMENT_GUIDE.md)
- 🔗 [Zustand Docs](https://github.com/pmndrs/zustand)
- 📝 [Task 5 Complete](./TASK_5_COMPLETE.md)
